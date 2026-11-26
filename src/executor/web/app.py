"""自建 Web 审批应用（FastAPI + Jinja2 + SQLite）。

启动：
    python -m executor.web --host 127.0.0.1 --port 8080
公网验证：
    scripts/web.ps1 + scripts/tunnel.ps1（ngrok）
"""
from __future__ import annotations

import json
import hmac
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import Settings
from ..models import now_iso
from ..runtime import build
from ..services.directory_refresh import refresh_directory
from .admin_auth import admin_configured, verify_password
from .auth import AuthError, WebAuth
from .bitable import BitableLedger
from .contacts import collect_contact_users, write_status as write_contacts_status
from .finedb import FineDB
from .service import ACTION_LABELS, WebApprovalError, WebApprovalService

LOGGER = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_LABELS = {
    "pending": "审批中", "approved": "已通过", "rejected": "已驳回",
    "withdrawn": "已撤回", "granting": "授权中", "done": "已授权", "failed": "授权失败",
}
ROLE_LABELS = {"data_owner": "数据 Owner", "business_owner": "业务 Owner",
               "membership_owner": "角色/部门审批人",
               "manager": "直属上级", "owner": "数据 Owner",
               "security": "数据安全", "bi_admin": "BI 管理员", "admin": "管理员"}
RESOURCE_LABELS = {"folder": "文件夹", "table": "数据集", "field": "字段",
                   "row": "行权限", "dashboard": "仪表板",
                   "dashboard_view": "仪表板查看", "dashboard_export": "仪表板导出",
                   "dashboard_edit": "仪表板编辑", "publink": "公共链接",
                   "dashboard_entry": "仪表板目录权限",
                   "dash_share": "仪表板分享", "dashboard_data": "目录组件数据",
                   "subject": "主题协作", "role": "角色", "schedule": "定时调度",
                   "department": "部门", "platform_module": "管理系统模块"}
CATEGORY_LABELS = {"dashboard": "仪表板权限", "public_data": "公共数据权限",
                   "admin": "管理系统权限", "membership": "角色/部门申请"}


def _schedules(ctx) -> List[Dict[str, Any]]:
    """读取全部定时调度任务（接口按 hasNext 分页，默认一页 50 条）。"""
    try:
        items: List[Dict[str, Any]] = []
        page = 1
        for _ in range(20):
            resp = ctx.platform.list_schedules(page=page, per_page=50)
            data = (resp or {}).get("data")
            has_next = False
            if isinstance(data, dict):
                has_next = bool(data.get("hasNext"))
                data = (data.get("list") or data.get("items")
                        or data.get("schedules") or [])
            items.extend(item for item in (data or []) if isinstance(item, dict))
            if not has_next:
                break
            page += 1
        result = []
        seen = set()
        for item in items:
            sid = item.get("id") or item.get("taskId") or item.get("name") or ""
            name = item.get("name") or item.get("taskName") or str(sid)
            if not sid or str(sid) in seen:
                continue
            seen.add(str(sid))
            result.append({"id": str(sid), "name": str(name)})
        return result
    except Exception:  # noqa: BLE001
        LOGGER.warning("读取定时调度列表失败", exc_info=True)
        return []


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings.load()
    ctx = build(settings)
    finedb = FineDB(settings.fine_db_host, settings.fine_db_port, settings.fine_db_user,
                    settings.fine_db_password, settings.fine_db_name)
    data_api_env = {
        "user_token": getattr(settings, "finebi_user_token", ""),
        "username": getattr(settings, "finebi_api_username", ""),
        "password": getattr(settings, "finebi_api_password", ""),
    }
    bitable = None
    bitable_table_id = (getattr(settings, "bitable_request_table_id", "")
                        or getattr(settings, "bitable_ledger_table_id", ""))
    if getattr(settings, "bitable_write", False) and getattr(settings, "bitable_app_token", ""):
        bitable = BitableLedger(ctx.feishu, settings.bitable_app_token,
                                bitable_table_id, dry_run=settings.dry_run)
        try:
            schema = bitable.ensure_schema()
            if schema.get("created") or schema.get("renamed"):
                LOGGER.info("多维表格字段已补齐：%s", schema)
        except Exception:  # noqa: BLE001 - 表格不可用不影响审批主流程
            LOGGER.warning("多维表格字段初始化失败", exc_info=True)
    service = WebApprovalService(
        ctx.storage, ctx.permission, ctx.notifier, policy=settings.policy,
        public_base_url=getattr(settings, "public_base_url", ""),
        dry_run=settings.dry_run, platform=ctx.platform, offboard_service=ctx.offboard,
        finedb=finedb, bitable=bitable,
        finebi_base_url=settings.finebi_base_url, http_client=ctx.http,
        data_api_env=data_api_env)
    auth = WebAuth(settings, service, ctx.http)
    if auth.mode == "dev" and not settings.dry_run:
        base_host = urlparse(getattr(settings, "public_base_url", "") or "").hostname or ""
        if base_host not in ("127.0.0.1", "localhost", "::1"):
            raise RuntimeError(
                "拒绝启动：WEB_AUTH_MODE=dev 可无密码冒充任意用户；"
                "生产环境（dry_run=false）必须使用 feishu 登录")
    if auth.mode == "dev":
        # 本地联调不往真实飞书发消息，避免把 127.0.0.1 链接推给用户
        ctx.notifier.dry_run = True
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
    contacts_status_path = os.path.join(
        os.path.dirname(service.directory_status_path), "contacts_status.json")

    # ---------- 飞书通讯录（Owner 候选） ----------
    contacts_cache: Dict[str, Any] = {"at": 0.0, "items": []}

    def load_contacts(force: bool = False) -> List[Dict[str, Any]]:
        """兼容入口：手动同步/极少数兜底用；后台页面请求不再实时遍历通讯录。"""
        now = time.time()
        if not force and contacts_cache["items"] and now - contacts_cache["at"] < 600:
            return contacts_cache["items"]
        items, stats = collect_contact_users(ctx.feishu)
        if stats.get("dept_error"):
            LOGGER.warning("飞书通讯录部分失败：%s", stats["dept_error"])
        contacts_cache["at"] = now
        contacts_cache["items"] = items
        LOGGER.info("飞书通讯录加载完成：%d 人", len(items))
        return items

    def read_contacts_status() -> Dict[str, Any]:
        try:
            with open(contacts_status_path, encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def owner_candidates() -> List[Dict[str, Any]]:
        """Owner 候选只读本地已同步映射（定时任务 / 手动同步写入）。"""
        candidates: List[Dict[str, Any]] = []
        for u in service.list_users():
            open_id = str(u.get("feishu_open_id") or "")
            if not (open_id or u.get("feishu_user_id")):
                continue
            candidates.append({
                "ref": ("feishu:" + open_id) if open_id else ("local:" + u["id"]),
                "name": str(u.get("name") or ""),
                "mobile": "",
                "email": str(u.get("email") or ""),
                "local_user_id": str(u.get("id") or ""),
            })
        candidates.sort(key=lambda x: str(x.get("name") or "").lower())
        return candidates

    def resolve_owner_refs(refs: List[str]) -> List[str]:
        """把通讯录 ref / 本地 user id 解析成 web_users.id；飞书用户自动建档。"""
        refs = [str(r or "").strip() for r in refs or [] if str(r or "").strip()]
        contacts: List[Dict[str, Any]] = []
        by_open: Dict[str, Dict[str, Any]] = {}
        missing: List[str] = []
        for ref in refs:
            if not ref.startswith("feishu:"):
                continue
            open_id = ref.split(":", 1)[1]
            user = service.find_by_open_id(open_id)
            if user:
                by_open[open_id] = {
                    "open_id": open_id,
                    "name": user.get("name") or "",
                    "email": user.get("email") or "",
                    "user_id": user.get("feishu_user_id") or "",
                }
            else:
                missing.append(ref)
        if missing:
            try:
                contacts = load_contacts()
            except Exception as exc:  # noqa: BLE001
                raise WebApprovalError("飞书通讯录读取失败：%s" % exc)
            for item in contacts:
                by_open.setdefault(str((item or {}).get("open_id") or ""), item)
        ids: List[str] = []
        for ref in refs:
            if ref.startswith("feishu:"):
                open_id = ref.split(":", 1)[1]
                item = by_open.get(open_id) or {}
                user = (service.find_by_open_id(open_id)
                        or (service.find_by_feishu_user_id(str(item.get("user_id") or ""))
                            if item.get("user_id") else None))
                if not user:
                    uid = "fs_" + open_id
                    user_id = str(item.get("user_id") or "")
                    fb_user = ""
                    if user_id and finedb.enabled():
                        try:
                            fb_user = finedb.feishu_user_by_id(user_id) or ""
                        except Exception:  # noqa: BLE001
                            fb_user = ""
                    name = str(item.get("name") or "")
                    if not name:
                        name = "飞书用户 " + open_id[-6:]
                    # 审批人只需要飞书账号：没有 FineBI 账号时 fb_user 留空，不阻塞审批
                    service.storage.conn.execute(
                        "INSERT INTO web_users(id,name,email,feishu_open_id,feishu_user_id,"
                        "fb_user,roles,active,created_at) VALUES(?,?,?,?,?,?,?,?,?) "
                        "ON CONFLICT(id) DO UPDATE SET name=excluded.name,"
                        "feishu_open_id=excluded.feishu_open_id,feishu_user_id=excluded.feishu_user_id,"
                        "active=1",
                        (uid, name, str(item.get("email") or ""),
                         open_id, user_id, fb_user, '["owner"]', 1, now_iso()))
                    service.storage.conn.commit()
                    user = service.get_user(uid)
                if not user:
                    raise WebApprovalError("飞书通讯录里找不到该用户：%s" % open_id)
                uid = user["id"]
            else:
                uid = ref.split(":", 1)[1] if ref.startswith("local:") else ref
                if not service.get_user(uid):
                    raise WebApprovalError("用户不存在：%s" % uid)
            if uid not in ids:
                ids.append(uid)
        return ids

    app = FastAPI(title="FineBI 数据权限申请", version="0.2.0")
    app.state.ctx = ctx
    app.state.service = service

    @app.middleware("http")
    async def csrf_origin_guard(request: Request, call_next):
        """轻量 CSRF 加固：写请求若带 Origin/Referer，主机必须与当前站点一致。"""
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin") or request.headers.get("referer") or ""
            if origin and origin != "null":
                origin_host = urlparse(origin).hostname or ""
                base_host = urlparse(getattr(settings, "public_base_url", "") or "").hostname or ""
                host = (request.headers.get("host") or "").split(":")[0]
                forwarded = (request.headers.get("x-forwarded-host") or "").split(":")[0]
                allowed = {item for item in (host, forwarded, base_host) if item}
                if origin_host and origin_host not in allowed:
                    return JSONResponse({"detail": "CSRF origin rejected"}, status_code=403)
        return await call_next(request)

    def current_user(request: Request) -> Optional[Dict[str, Any]]:
        sid = request.cookies.get("sid")
        return service.get_session_user(sid) if sid else None

    def is_admin(user: Optional[Dict[str, Any]]) -> bool:
        return bool(user and "admin" in (user.get("roles") or []))

    def is_admin_session(user: Optional[Dict[str, Any]]) -> bool:
        """只有后台独立登录账号（id=admin:xxx）才算后台会话，飞书管理员不算。"""
        return bool(user and str(user.get("id") or "").startswith("admin:")
                    and "admin" in (user.get("roles") or []))

    def render(request: Request, name: str, **context) -> HTMLResponse:
        user = context.get("user") or current_user(request)
        context["user"] = user
        context["is_admin"] = is_admin(user)
        context["is_admin_session"] = is_admin_session(user)
        context.setdefault("status_labels", STATUS_LABELS)
        context.setdefault("role_labels", ROLE_LABELS)
        context.setdefault("resource_labels", RESOURCE_LABELS)
        context.setdefault("category_labels", CATEGORY_LABELS)
        context.setdefault("action_labels", ACTION_LABELS)
        return templates.TemplateResponse(request=request, name=name, context=context)

    def require_user(request: Request):
        user = current_user(request)
        if not user:
            return None, RedirectResponse("/login", status_code=303)
        return user, None

    def require_admin(request: Request):
        user = current_user(request)
        if not is_admin_session(user):
            return None, RedirectResponse("/admin/login", status_code=303)
        return user, None

    def can_view_request(user: Optional[Dict[str, Any]],
                         req: Optional[Dict[str, Any]]) -> bool:
        """申请详情/评论的可见范围：申请人、任一节点审批人、管理员。"""
        if not user or not req:
            return False
        if is_admin(user) or is_admin_session(user):
            return True
        if req.get("applicant_id") == user.get("id"):
            return True
        for step in req.get("steps") or []:
            if service.can_approve(user["id"], step):
                return True
        return False

    def can_configure_scope(user: Optional[Dict[str, Any]],
                            req: Optional[Dict[str, Any]]) -> bool:
        """行/列权限补充配置：仅公共数据集的 pending 申请，审批人/管理员可操作。"""
        if not user or not req:
            return False
        payload = req.get("payload") or {}
        if (req.get("status") != "pending"
                or req.get("category") != "public_data"
                or payload.get("resource_type") != "table"):
            return False
        if is_admin(user) or is_admin_session(user):
            return True
        return bool(req.get("current_step")
                    and service.can_approve(user["id"], req.get("current_step")))

    def component_scope_tables(req: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """仪表板连带数据集中，能在公共数据目录里找到的数据集才需要行/列权限。"""
        if not req:
            return []
        payload = req.get("payload") or {}
        result: List[Dict[str, Any]] = []
        for dep in payload.get("component_datasets") or []:
            if not isinstance(dep, dict):
                continue
            rid = str(dep.get("resource_id") or "")
            if rid and service._table_row(rid):
                result.append(dep)
        return result

    def can_configure_component_scope(user: Optional[Dict[str, Any]],
                                      req: Optional[Dict[str, Any]]) -> bool:
        """仪表板连带组件数据集的行/列权限：pending 且有公共数据组件。"""
        if not user or not req:
            return False
        payload = req.get("payload") or {}
        if (req.get("status") != "pending"
                or req.get("category") != "dashboard"
                or not component_scope_tables(req)):
            return False
        if is_admin(user) or is_admin_session(user):
            return True
        return bool(req.get("current_step")
                    and service.can_approve(user["id"], req.get("current_step")))

    def request_table_for_scope(req: Optional[Dict[str, Any]],
                                table_id: str = "") -> Optional[str]:
        """返回申请单里允许补充行/列权限的公共数据集 ID。"""
        if not req:
            return None
        payload = req.get("payload") or {}
        if req.get("category") == "public_data":
            return str(payload.get("resource_id") or "") or None
        if req.get("category") == "dashboard":
            wanted = str(table_id or "")
            deps = {str((d or {}).get("resource_id") or "")
                    for d in (payload.get("component_datasets") or [])
                    if isinstance(d, dict)}
            if wanted and wanted in deps and service._table_row(wanted):
                return wanted
            return None
        return None

    def set_session_cookie(resp: RedirectResponse, sid: str) -> None:
        resp.set_cookie("sid", sid, httponly=True, samesite="lax",
                        secure=getattr(settings, "public_base_url", "").startswith("https"))

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "mode": auth.mode, "dry_run": settings.dry_run,
                "public_base_url": getattr(settings, "public_base_url", "")}

    # ---------- 登录 ----------
    @app.get("/login")
    def login_page(request: Request):
        if auth.mode == "feishu":
            return RedirectResponse(auth.authorize_url(), status_code=303)
        return render(request, "login.html", users=service.list_users(),
                      error=request.query_params.get("error", ""))

    @app.post("/login")
    def login_submit(request: Request, user_id: str = Form(...)):
        try:
            sid = auth.login_dev(user_id)
        except AuthError as exc:
            return RedirectResponse("/login?error=%s" % str(exc), status_code=303)
        resp = RedirectResponse("/", status_code=303)
        resp.set_cookie("sid", sid, httponly=True, samesite="lax",
                        secure=getattr(settings, "public_base_url", "").startswith("https"))
        return resp

    @app.get("/auth/feishu")
    def feishu_login():
        return RedirectResponse(auth.authorize_url(), status_code=303)

    @app.get("/auth/feishu/callback")
    def feishu_callback(request: Request, code: str = "", state: str = ""):
        try:
            if auth.mode == "feishu" and not state:
                raise AuthError("缺少 state（请从登录入口重新发起）")
            user = auth.handle_callback(code, state)
            sid = service.create_session(user["id"])
        except AuthError as exc:
            return RedirectResponse("/login?error=%s" % str(exc), status_code=303)
        resp = RedirectResponse("/", status_code=303)
        resp.set_cookie("sid", sid, httponly=True, samesite="lax",
                        secure=getattr(settings, "public_base_url", "").startswith("https"))
        return resp

    @app.post("/logout")
    def logout():
        resp = RedirectResponse("/login", status_code=303)
        resp.delete_cookie("sid")
        return resp

    # ---------- 后台独立入口（用户名/密码，与飞书登录隔离） ----------
    @app.get("/admin/login")
    def admin_login_page(request: Request):
        user = current_user(request)
        if is_admin_session(user):
            return RedirectResponse("/admin", status_code=303)
        return render(request, "admin_login.html",
                      error=request.query_params.get("error", ""),
                      configured=admin_configured(settings.admin_username,
                                                  settings.admin_password_hash))

    @app.post("/admin/login")
    def admin_login_submit(request: Request, username: str = Form(""),
                           password: str = Form("")):
        if not admin_configured(settings.admin_username, settings.admin_password_hash):
            return render(request, "admin_login.html",
                          error="后台未配置管理员账号，请先在 .env 设置 ADMIN_USERNAME / ADMIN_PASSWORD_HASH",
                          configured=False)
        username_ok = hmac.compare_digest(str(username or "").strip(),
                                          str(settings.admin_username or ""))
        password_ok = verify_password(password, settings.admin_password_hash)
        if not (username_ok and password_ok):
            time.sleep(0.3)
            return render(request, "admin_login.html",
                          error="用户名或密码错误", configured=True)
        admin_user = service.ensure_admin_user(settings.admin_username)
        sid = service.create_session(admin_user["id"])
        resp = RedirectResponse("/admin", status_code=303)
        set_session_cookie(resp, sid)
        return resp

    @app.post("/admin/logout")
    def admin_logout():
        resp = RedirectResponse("/admin/login", status_code=303)
        resp.delete_cookie("sid")
        return resp

    @app.get("/admin")
    def admin_home(request: Request):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            map_page = int(request.query_params.get("map_page", "1"))
        except (TypeError, ValueError):
            map_page = 1
        map_q = request.query_params.get("map_q", "").strip()
        mapping = service.mapping_page(page=map_page, page_size=50, keyword=map_q)
        return render(request, "admin.html",
                      dashboard_tree=service.resource_tree("dashboard"),
                      public_tree=service.resource_tree("public_data"),
                      owner_display_dashboard=service.owner_display_map("dashboard"),
                      owner_display_public=service.owner_display_map("public_data"),
                      owner_ids_json=json.dumps(service.owner_ids_map(),
                                                ensure_ascii=False),
                      membership_owner=service.membership_owner(),
                      membership_owner_id=(service.membership_owner() or {}).get("id", ""),
                      default_approver=service.default_approver(),
                      default_approver_id=(service.default_approver() or {}).get("id", ""),
                      users=service.list_users(),
                      mappings=mapping["rows"],
                      mapping_total=mapping["total"],
                      mapping_page=mapping["page"],
                      mapping_pages=mapping["pages"],
                      map_q=map_q,
                      contacts_status=read_contacts_status(),
                      directory_status=service.directory_status(),
                      data_api_status=service.data_api_status(),
                      message=request.query_params.get("message", ""),
                      error=request.query_params.get("error", ""))

    # ---------- 首页（多 tab） ----------
    @app.get("/")
    def dashboard(request: Request):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        if is_admin_session(user):
            return RedirectResponse("/admin", status_code=303)
        return render(request, "workspace.html",
                      my_requests=service.my_requests(user["id"]),
                      approvals=service.my_approvals(user["id"]),
                      dashboard_tree=service.resource_tree("dashboard"),
                      public_tree=service.resource_tree("public_data"),
                      schedules=_schedules(ctx),
                      directory_status=service.directory_status(),
                      active_tab=request.query_params.get("tab", "dashboard"),
                      message=request.query_params.get("message", ""),
                      error=request.query_params.get("error", ""))

    @app.get("/requests/new")
    def new_request_page():
        return RedirectResponse("/", status_code=303)

    @app.post("/requests/new")
    def new_request_submit(request: Request,
                           category: str = Form("dashboard"),
                           resource_id: str = Form(""),
                           entry_id: str = Form(""),
                           resource_path: str = Form(""),
                           resource_name: str = Form(""),
                           resource_type: str = Form(""),
                           permissions: List[str] = Form(default=[]),
                           period_type: str = Form("temp"),
                           days: int = Form(90),
                           reason: str = Form(""),
                           row_enabled: bool = Form(False),
                           row_field: str = Form(""),
                           row_operator: str = Form("strIn"),
                           row_values: List[str] = Form(default=[]),
                           schedule_task: str = Form(""),
                           schedule_name: str = Form(""),
                           module: str = Form(""),
                           membership_type: str = Form(""),
                           targets: List[str] = Form(default=[])):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        payload: Dict[str, Any] = {"period_type": period_type, "days": days,
                                   "reason": reason}
        if category == "dashboard":
            payload.update({"resource_id": resource_id, "entry_id": entry_id,
                            "resource_type": resource_type,
                            "resource_path": resource_path,
                            "resource_name": resource_name,
                            "permissions": permissions})
            tab = "dashboard"
        elif category == "admin":
            payload.update({"schedule_task": schedule_task, "module": module,
                            "resource_name": resource_name or schedule_name or schedule_task,
                            "permissions": permissions or ["use"]})
            if module:
                tab = "admin_alert"
            elif {"manage", "empower"} & set(permissions or []):
                tab = "admin_task"
            else:
                tab = "admin_function"
        elif category == "membership":
            payload.update({"membership_type": membership_type,
                            "targets": targets})
            tab = "membership"
        else:
            payload.update({"resource_type": resource_type, "resource_id": resource_id,
                            "resource_path": resource_path,
                            "resource_name": resource_name, "permissions": permissions,
                            "row_enabled": row_enabled, "row_field": row_field,
                            "row_operator": row_operator,
                            "row_values": row_values})
            tab = "public_data"
        try:
            req = service.create_request(user["id"], payload, category)
            return RedirectResponse("/requests/%s" % req["id"], status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/?tab=%s&error=%s" % (tab, exc), status_code=303)

    # ---------- 行权限枚举 / 调度 / 通讯录 ----------
    @app.get("/api/permission-status")
    def api_permission_status(request: Request):
        user = current_user(request)
        if not user:
            return JSONResponse({"known": False}, status_code=401)
        params = request.query_params
        actions = [a for a in params.get("actions", "").split(",") if a]
        return JSONResponse(service.permission_status(
            user["id"], params.get("resource_type", ""),
            params.get("resource_id", ""), params.get("entry_id", ""),
            params.get("resource_path", ""), actions))

    @app.get("/api/permission-map")
    def api_permission_map(request: Request, category: str = "dashboard"):
        """资源下拉框批量已有权限：一次查询，节点上显示“已有：查看/使用…”。"""
        user = current_user(request)
        if not user:
            return JSONResponse({"items": {}, "known": False}, status_code=401)
        if category not in ("dashboard", "public_data"):
            return JSONResponse({"items": {}, "known": False}, status_code=400)
        return JSONResponse(service.permission_map(user["id"], category))

    @app.get("/api/membership-status")
    def api_membership_status(request: Request):
        user = current_user(request)
        if not user:
            return JSONResponse({"known": False}, status_code=401)
        return JSONResponse(service.user_membership(user["id"]))

    @app.get("/api/row-values")
    def api_row_values(request: Request, table: str = ""):
        user = current_user(request)
        if not user:
            return JSONResponse({"fields": []}, status_code=401)
        if not table:
            return JSONResponse({"fields": []})
        # 目录树里文件夹和数据集共用 resource_id，文件夹不能拿来读字段/枚举
        if not service._table_row(table):
            return JSONResponse({"fields": []})
        sample = (user or {}).get("fb_user") or ""
        return JSONResponse({"fields": service.row_values(table, sample)})

    @app.get("/api/field-values")
    def api_field_values(request: Request, table: str = "", field: str = "",
                         request_id: str = ""):
        """字段去重值（行权限搜索多选）；数据源不可用时返回空，前端退化为手工输入。"""
        user = current_user(request)
        if not user:
            return JSONResponse({"values": [], "source": ""}, status_code=401)
        if not table or not field:
            return JSONResponse({"values": [], "source": ""})
        if request_id:
            req = service.get_request(request_id)
            if not req:
                return JSONResponse({"values": [], "source": ""}, status_code=404)
            if not (can_configure_scope(user, req)
                    or can_configure_component_scope(user, req)):
                return JSONResponse({"values": [], "source": ""}, status_code=403)
            allowed_table = request_table_for_scope(req, table)
            if not allowed_table:
                return JSONResponse({"values": [], "source": ""}, status_code=403)
            table = allowed_table
        # 没有申请单上下文时，只允许目录中的公共数据集，避免拿任意 tableId 探测数据
        elif not service._table_row(table):
            return JSONResponse({"values": [], "source": ""}, status_code=404)
        result = service.field_values(table, field)
        return JSONResponse({"field_id": result.get("field_id", field),
                             "name": result.get("name", ""),
                             "values": result.get("values", []),
                             "source": result.get("source", ""),
                             "scanned_rows": result.get("scanned_rows", 0),
                             "total_rows": result.get("total_rows", 0),
                             "scanned_pages": result.get("scanned_pages", 0)})

    @app.get("/api/table-fields")
    def api_table_fields(request: Request):
        """数据集字段：审批人补充列权限，或申请人选择行权限字段。"""
        user = current_user(request)
        if not user:
            return JSONResponse({"fields": []}, status_code=401)
        request_id = request.query_params.get("request_id", "")
        if request_id:
            req = service.get_request(request_id)
            if not req:
                return JSONResponse({"fields": [], "error": "申请不存在"}, status_code=404)
            if not (can_configure_scope(user, req)
                    or can_configure_component_scope(user, req)):
                return JSONResponse({"fields": [], "error": "无权查看"}, status_code=403)
            table_id = request_table_for_scope(
                req, request.query_params.get("table_id", ""))
            if not table_id:
                return JSONResponse({"fields": [], "error": "请选择组件数据集"},
                                    status_code=400)
            return JSONResponse({"fields": service.table_fields(table_id)})
        table = request.query_params.get("table", "")
        if not table:
            return JSONResponse({"fields": []})
        if not service._table_row(table):
            return JSONResponse({"fields": [], "error": "不是公共数据集"},
                                status_code=404)
        return JSONResponse({"fields": service.table_fields(table)})

    @app.get("/api/row-permission-status")
    def api_row_permission_status(request: Request):
        """检测数据集是否配置了行权限，供审批人补充配置前参考。"""
        user = current_user(request)
        if not user:
            return JSONResponse({"known": False}, status_code=401)
        request_id = request.query_params.get("request_id", "")
        req = service.get_request(request_id)
        if not req:
            return JSONResponse({"known": False, "error": "申请不存在"}, status_code=404)
        if not (can_configure_scope(user, req)
                or can_configure_component_scope(user, req)):
            return JSONResponse({"known": False, "error": "无权查看"}, status_code=403)
        table_id = request_table_for_scope(
            req, request.query_params.get("table_id", ""))
        if not table_id:
            return JSONResponse({"known": False, "error": "请选择组件数据集"},
                                status_code=400)
        applicant = req.get("applicant") or {}
        return JSONResponse(service.row_permission_status(
            table_id, str(applicant.get("fb_user") or "")))

    @app.get("/api/contacts")
    def api_contacts(request: Request, q: str = ""):
        user = current_user(request)
        if not is_admin_session(user):
            return JSONResponse({"items": []}, status_code=403)
        try:
            items = owner_candidates()
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({"items": [], "error": str(exc)[:200]})
        keyword = q.strip().lower()
        if keyword:
            items = [it for it in items
                     if keyword in str(it.get("name") or "").lower()
                     or keyword in str(it.get("email") or "").lower()
                     or keyword in str(it.get("mobile") or "").lower()]
        # 通讯录候选要全量返回给前端做本地搜索；之前截断 200 会让后台像“只有 200 人”
        return JSONResponse({"items": items[:2000], "total": len(items)})

    @app.get("/api/membership-options")
    def api_membership_options(request: Request):
        """可申请加入的 FineBI 角色/部门（登录用户均可读取，缓存 10 分钟）。"""
        user = current_user(request)
        if not user:
            return JSONResponse({"roles": [], "departments": [], "errors": ["未登录"]},
                                status_code=401)
        try:
            return JSONResponse(service.membership_options())
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("读取角色/部门列表失败：%s", exc)
            return JSONResponse({"roles": [], "departments": [],
                                 "errors": [str(exc)[:200]]})

    @app.get("/api/entity-permissions")
    def api_entity_permissions(request: Request):
        """成员关系申请：角色/部门当前权限摘要（详情页异步加载）。"""
        user = current_user(request)
        if not user:
            return JSONResponse({"known": False}, status_code=401)
        request_id = request.query_params.get("request_id", "")
        req = service.get_request(request_id)
        if not req:
            return JSONResponse({"known": False, "error": "申请不存在"}, status_code=404)
        if not can_view_request(user, req):
            return JSONResponse({"known": False, "error": "无权查看"}, status_code=403)
        return JSONResponse(service.membership_permissions(request_id))

    # ---------- 详情与动作 ----------
    @app.get("/requests/{request_id}")
    def request_detail(request: Request, request_id: str):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        req = service.get_request(request_id)
        if not req:
            return HTMLResponse("申请不存在", status_code=404)
        if not can_view_request(user, req):
            return HTMLResponse("无权查看该申请单", status_code=403)
        current = req.get("current_step") or {}
        can_approve = (req["status"] == "pending" and service.can_approve(user["id"], current))
        can_withdraw = (req["status"] == "pending" and req["applicant_id"] == user["id"])
        payload = req.get("payload") or {}
        table_fields = []
        if (payload.get("resource_type") == "table"
                and req.get("category") == "public_data"):
            table_fields = service.table_fields(str(payload.get("resource_id") or ""))
        field_name_map = {str(f["field_id"]): str(f["name"]) for f in table_fields}
        selected_field_names = [field_name_map.get(str(fid), str(fid))
                                for fid in (payload.get("field_ids") or [])]
        row_rules = ((payload.get("data_scope") or {}).get("rules") or [])
        row_field_name = ""
        row_values_text = ""
        if row_rules:
            row_field_name = field_name_map.get(
                str(row_rules[0].get("fieldId") or ""),
                str(row_rules[0].get("fieldId") or ""))
            row_values_text = "、".join(
                str(v) for v in (row_rules[0].get("filterValue") or []))
        return render(request, "detail.html", req=req, can_approve=can_approve,
                      can_withdraw=can_withdraw,
                      can_configure_scope=can_configure_scope(user, req),
                      can_configure_component_scope=(
                          can_configure_component_scope(user, req)),
                      component_scope_tables=component_scope_tables(req),
                      component_other_tables=[
                          d for d in (payload.get("component_self_service") or [])
                          if isinstance(d, dict)
                      ],
                      table_fields=table_fields,
                      selected_field_names=selected_field_names,
                      row_field_name=row_field_name,
                      row_values_text=row_values_text,
                      message=request.query_params.get("message", ""),
                      error=request.query_params.get("error", ""))

    @app.post("/requests/{request_id}/approve")
    def approve(request: Request, request_id: str, comment: str = Form("")):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        try:
            service.approve(request_id, user["id"], comment)
            return RedirectResponse("/requests/%s" % request_id, status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/requests/%s?error=%s" % (request_id, exc), status_code=303)

    @app.post("/requests/{request_id}/reject")
    def reject(request: Request, request_id: str, comment: str = Form("")):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        try:
            service.reject(request_id, user["id"], comment)
            return RedirectResponse("/requests/%s" % request_id, status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/requests/%s?error=%s" % (request_id, exc), status_code=303)

    @app.post("/requests/{request_id}/withdraw")
    def withdraw(request: Request, request_id: str):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        try:
            service.withdraw(request_id, user["id"])
            return RedirectResponse("/requests/%s" % request_id, status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/requests/%s?error=%s" % (request_id, exc), status_code=303)

    @app.post("/requests/{request_id}/comment")
    def comment(request: Request, request_id: str, content: str = Form(...)):
        user, redirect = require_user(request)
        if redirect:
            return redirect
        req = service.get_request(request_id)
        if not req:
            return HTMLResponse("申请不存在", status_code=404)
        if not can_view_request(user, req):
            return HTMLResponse("无权评论该申请单", status_code=403)
        service.add_comment(request_id, user["id"], content)
        return RedirectResponse("/requests/%s" % request_id, status_code=303)

    @app.post("/requests/{request_id}/scope")
    def set_approver_scope(request: Request, request_id: str,
                           row_enabled: bool = Form(False),
                           row_field: str = Form(""),
                           row_operator: str = Form("strIn"),
                           row_values: List[str] = Form(default=[]),
                           field_ids: List[str] = Form(default=[]),
                           scope_table_id: str = Form("")):
        """审批人补充行/列权限；仅当前节点审批人，且申请单必须为 pending。"""
        user, redirect = require_user(request)
        if redirect:
            return redirect
        try:
            service.set_approver_scope(
                request_id, user["id"], row_enabled=row_enabled,
                row_field=row_field, row_operator=row_operator,
                row_values=row_values, field_ids=field_ids,
                scope_table_id=scope_table_id)
            return RedirectResponse(
                "/requests/%s?message=%s" % (
                    request_id, "行/列权限已保存，审批通过后与数据权限一起执行"),
                status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse(
                "/requests/%s?error=%s" % (request_id, exc), status_code=303)

    # ---------- 后台管理 ----------
    @app.post("/admin/owners")
    def admin_set_owners(request: Request, resource_type: str = Form(...),
                         resource_id: str = Form(...),
                         data_owner_ref: str = Form(""),
                         business_owner_ref: str = Form("")):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            data_ids = resolve_owner_refs([data_owner_ref]) if data_owner_ref else []
            business_ids = resolve_owner_refs([business_owner_ref]) if business_owner_ref else []
            saved = service.set_owner_pair(resource_type, resource_id,
                                           data_ids, business_ids)
            message = "Owner 已保存（数据 %d 人 / 业务 %d 人）" % (
                len(saved["data"]), len(saved["business"]))
            return RedirectResponse("/admin?message=%s" % message, status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/membership-owner")
    def admin_set_membership_owner(request: Request, owner_ref: str = Form("")):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            ids = resolve_owner_refs([owner_ref]) if owner_ref else []
            service.set_membership_owner(ids[0] if ids else "")
            owner = service.membership_owner()
            message = ("角色/部门审批人已保存：%s" % owner["name"]
                       if owner else "角色/部门审批人已清空（将回退默认审批人）")
            return RedirectResponse("/admin?message=%s" % message, status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/default-approver")
    def admin_set_default_approver(request: Request, owner_ref: str = Form("")):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            ids = resolve_owner_refs([owner_ref]) if owner_ref else []
            service.set_default_approver(ids[0] if ids else "")
            owner = service.default_approver()
            message = ("默认审批人已保存：%s" % owner["name"]
                       if owner else "默认审批人已清空（将回退 config.json / admin）")
            return RedirectResponse("/admin?message=%s" % message, status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/data-api")
    def admin_save_data_api(request: Request,
                            username: str = Form(""),
                            password: str = Form(""),
                            user_token: str = Form(""),
                            clear_password: bool = Form(False),
                            clear_token: bool = Form(False),
                            clear_all: bool = Form(False)):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            service.save_data_api_config(
                username=username, password=password, user_token=user_token,
                clear_password=clear_password, clear_token=clear_token,
                clear_all=clear_all)
            return RedirectResponse("/admin?message=数据接口配置已保存", status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/data-api/test")
    def admin_test_data_api(request: Request):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            result = service.test_data_api()
            if result.get("ok"):
                return RedirectResponse(
                    "/admin?message=%s" % result.get("message", "连接成功"),
                    status_code=303)
            return RedirectResponse(
                "/admin?error=%s" % result.get("message", "连接失败"),
                status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/sync-users")
    def admin_sync_users(request: Request):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        messages: List[str] = []
        try:
            if finedb.enabled():
                count = service.sync_finedb_mapping()
                if count:
                    messages.append("从 FineDB 导入 %d 条映射" % count)
            # 手动同步：全量拉取一次（根部门 + 递归部门），结果写入本地映射和快照状态
            items, stats = collect_contact_users(ctx.feishu)
            contacts_cache["at"] = time.time()
            contacts_cache["items"] = items
            count = service.sync_feishu_users(items) if items else 0
            write_contacts_status(
                contacts_status_path, ok=not stats.get("dept_error"),
                total=len(items), synced=count, stats=stats,
                error=str(stats.get("dept_error") or ""))
            if items:
                message = ("同步飞书用户 %d 个（根部门 %d，部门 %d，部门用户 %d）"
                           % (count, stats.get("root", 0), stats.get("departments", 0),
                              stats.get("department_users", 0)))
                if stats.get("dept_error"):
                    message += "；" + str(stats["dept_error"])
                messages.append(message)
        except Exception as exc:  # noqa: BLE001
            try:
                write_contacts_status(contacts_status_path, ok=False, error=str(exc))
            except Exception:  # noqa: BLE001
                LOGGER.warning("通讯录状态写入失败", exc_info=True)
            if not messages:
                return RedirectResponse("/admin?error=同步失败：%s" % exc,
                                        status_code=303)
            messages.append("部分失败：%s" % exc)
        if not messages:
            return RedirectResponse(
                "/admin?error=飞书通讯录无可见用户或 FineDB 无映射，请检查应用通讯录权限/可见范围",
                status_code=303)
        return RedirectResponse("/admin?message=%s" % "；".join(messages),
                                status_code=303)

    @app.post("/admin/users/mapping")
    def admin_update_mapping(request: Request, user_id: str = Form(...),
                             fb_user: str = Form("")):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            service.update_user_fb_user(user_id, fb_user)
            return RedirectResponse("/admin?message=FineBI 账号映射已更新",
                                    status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/offboard")
    def admin_offboard(request: Request, source_id: str = Form(...),
                       target_id: str = Form(...)):
        user, redirect = require_admin(request)
        if redirect:
            return redirect
        try:
            service.offboard(source_id, target_id)
            return RedirectResponse("/admin?message=离职交接完成", status_code=303)
        except WebApprovalError as exc:
            return RedirectResponse("/admin?error=%s" % exc, status_code=303)

    @app.post("/admin/refresh-directory")
    def admin_refresh_directory(request: Request):
        user, redirect = require_admin(request)
        if redirect:
            return redirect

        def _run() -> None:
            try:
                status = refresh_directory(
                    ctx, interval_hours=settings.directory_refresh_hours)
                LOGGER.info("目录/角色/部门刷新完成：ok=%s", status.get("ok"))
            except Exception:  # noqa: BLE001
                LOGGER.exception("目录/角色/部门刷新失败")

        threading.Thread(target=_run, daemon=True).start()
        return RedirectResponse(
            "/admin?message=目录刷新已开始，约 1 分钟后刷新页面查看状态",
            status_code=303)

    return app
