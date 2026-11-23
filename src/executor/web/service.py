"""自建 Web 审批：领域模型与状态机（不依赖 FastAPI，便于单测）。

页面分类：dashboard（仪表板）、public_data（公共数据）、admin（管理系统-定时调度）、
membership（加入已有角色/部门）。
流程：pending → approved/rejected/withdrawn → granting → done/failed。
"""
from __future__ import annotations

import base64
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet, InvalidToken

from ..models import PermissionRequest, ResourceType, new_id, now_iso
from ..finebi.data import FineBIDataClient
from ..services import lineage
from ..services.directory_refresh import (collect_departments, collect_roles,
                                          read_directory_status, read_json)
from ..storage import Storage

LOGGER = logging.getLogger(__name__)

ROLE_ORDER = ("manager", "owner", "security", "bi_admin")
# 审批链：数据 Owner → 业务 Owner（配置了谁就走谁；都没有时回退 default_approver/admin）
OWNER_CHAIN = (("data", "data_owner", "数据 Owner"),
               ("business", "business_owner", "业务 Owner"))
HIGH_ACTIONS = {"manage", "empower", "edit"}
MEDIUM_ACTIONS = {"row", "field", "export", "dash_share", "publink", "subject"}
LONG_TERM_DAYS = 3650
# 数据预警（预警中心）是平台管理模块，权限用 /v3/auth/user/platform 配置
WARNING_MODULE = "decision-management-warningcenter"

# 服务端权限动作白名单：前端不展示的 action 不等于不能提交，必须在服务端拒绝。
PUBLIC_DATA_ACTIONS = {"use", "manage", "component"}
DASHBOARD_ACTIONS = {"view", "export", "edit", "component"}
MODULE_ACTIONS = {"use", "empower"}
SCHEDULE_ACTIONS = {"use", "manage", "empower"}
# 管理模块白名单：默认只允许“数据预警”；客户需要时在 config.policy.web_approval
# 的 allowed_admin_modules 里追加。
ALLOWED_ADMIN_MODULES = {WARNING_MODULE}
MODULE_LABELS = {WARNING_MODULE: "数据预警（预警中心）"}

ACTION_LABELS = {"view": "查看", "export": "导出", "edit": "编辑", "use": "使用",
                 "manage": "管理", "empower": "授权", "component": "组件数据",
                 "metadata": "元数据"}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def mobile_digits(value: str) -> str:
    """手机号归一化：去空格/横线/括号，去 0086、+86 前缀。"""
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if digits.startswith("0086"):
        digits = digits[4:]
    if len(digits) == 13 and digits.startswith("86"):
        digits = digits[2:]
    return digits


def mobile_candidates(value: str) -> List[str]:
    """归一化手机号及其 86 前缀变体，兼容 FineBI 里存 11 位或 13 位的情况。"""
    digits = mobile_digits(value)
    if not digits:
        return []
    values = [digits]
    if len(digits) == 11:
        values.append("86" + digits)
    return values


class WebApprovalError(Exception):
    """Web 审批业务错误。"""


class WebApprovalService:
    def __init__(self, storage: Storage, permission_service=None, notifier=None,
                 policy: Optional[Dict[str, Any]] = None,
                 public_base_url: str = "", dry_run: bool = True,
                 platform=None, offboard_service=None, finedb=None,
                 bitable=None, data_client=None,
                 finebi_base_url: str = "", http_client=None,
                 data_api_env: Optional[Dict[str, str]] = None,
                 row_cache_path: Optional[str] = None,
                 membership_options_path: Optional[str] = None,
                 directory_status_path: Optional[str] = None,
                 directory_refresh_hours: int = 6):
        self.storage = storage
        self.permission = permission_service
        self.notifier = notifier
        self.policy = policy or {}
        self.public_base_url = public_base_url.rstrip("/")
        self.dry_run = dry_run
        self.platform = platform
        self.offboard_service = offboard_service
        self.finedb = finedb
        self.bitable = bitable
        self.data_client = data_client
        self.finebi_base_url = str(finebi_base_url or "").rstrip("/")
        self.http_client = http_client
        self._data_api_env = dict(data_api_env or {})
        self._settings_key_path = os.path.join(
            self._default_data_dir(storage), ".settings.key")
        self._fernet = None
        self._permission_status_cache: Dict[tuple, Any] = {}
        self._permission_map_cache: Dict[tuple, Any] = {}
        # 仪表板 → 依赖公共数据集快照（目录刷新生成，用于连带组件数据授权）
        self.deps_json = lineage.DEFAULT_DEPS_JSON
        self._deps_cache: Dict[str, Any] = {"mtime": None, "data": {}}
        # 行/列权限检测与角色/部门权限摘要缓存
        self._row_permission_cache: Dict[tuple, Any] = {}
        self._entity_permission_cache: Dict[tuple, Any] = {}
        self._fields_cache: Dict[str, List[Dict[str, str]]] = {}
        self._table_meta_cache: Dict[str, Dict[str, Any]] = {}
        self._field_values_cache: Dict[tuple, Any] = {}
        self._row_values_api_cache: Dict[str, Any] = {}
        self._lineage_cache: Dict[str, List[Dict[str, str]]] = {}
        self.row_cache_path = row_cache_path or self._default_row_cache_path(storage)
        data_dir = self._default_data_dir(storage)
        self.membership_options_path = (membership_options_path
                                        or os.path.join(data_dir, "membership_options.json"))
        self.directory_status_path = (directory_status_path
                                      or os.path.join(data_dir, "directory_status.json"))
        self.directory_refresh_hours = max(1, int(directory_refresh_hours or 6))
        # 资源/动作/调度强校验：生产（非 dry-run）默认开启；本地 dry-run 联调可放宽，
        # 但白名单、IDOR、CSRF 等校验始终生效。
        self.strict_resource_validation = not bool(dry_run)
        self.catalog_rows_override: Optional[List[Dict[str, Any]]] = None
        self._schedule_cache: Dict[str, Any] = {"at": 0.0, "items": []}
        self._row_cache_lock = threading.Lock()
        self._catalog_cache: Dict[str, Any] = {"mtime": None, "rows": []}
        self._membership_cache: Dict[str, Any] = {"at": 0.0, "data": None}
        self._membership_snapshot: Dict[str, Any] = {"mtime": None, "data": None}
        self.seed_users()
        if self.data_client is None:
            self.configure_data_api()

    # ---------- 管理后台：FineBI 数据接口配置（持久化） ----------
    DATA_API_SETTING = "finebi_data_api"

    def _settings_fernet(self, create: bool = False):
        if self._fernet is not None:
            return self._fernet
        key = b""
        try:
            with open(self._settings_key_path, "rb") as fh:
                key = fh.read().strip()
        except OSError:
            key = b""
        if not key and create:
            key = Fernet.generate_key()
            parent = os.path.dirname(os.path.abspath(self._settings_key_path))
            if parent:
                os.makedirs(parent, exist_ok=True)
            fd = os.open(self._settings_key_path, os.O_WRONLY | os.O_CREAT
                         | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "wb") as fh:
                fh.write(key)
        if not key:
            return None
        self._fernet = Fernet(key)
        return self._fernet

    def load_data_api_config(self) -> Dict[str, Any]:
        raw = self.storage.get_setting(self.DATA_API_SETTING)
        if not raw:
            return {}
        try:
            box = json.loads(raw)
            fernet = self._settings_fernet(create=False)
            if fernet is None:
                return {}
            plain = fernet.decrypt(str(box.get("cipher") or "").encode())
            data = json.loads(plain.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except (ValueError, TypeError, InvalidToken, json.JSONDecodeError):
            LOGGER.warning("读取数据接口持久化配置失败，请后台重新保存")
            return {}

    def _save_data_api_payload(self, payload: Dict[str, Any]) -> None:
        fernet = self._settings_fernet(create=True)
        if fernet is None:
            raise WebApprovalError("无法保存：本地密钥初始化失败")
        encrypted = fernet.encrypt(json.dumps(payload, ensure_ascii=False).encode())
        self.storage.set_setting(self.DATA_API_SETTING, json.dumps({
            "version": 1,
            "cipher": encrypted.decode()}, ensure_ascii=False))

    def data_api_status(self) -> Dict[str, Any]:
        stored = self.load_data_api_config()
        env = self._data_api_env or {}
        stored_configured = bool(stored.get("user_token")
                                 or (stored.get("username") and stored.get("password")))
        env_configured = bool(env.get("user_token")
                              or (env.get("username") and env.get("password")))
        source = "admin" if stored_configured else ("env" if env_configured else "")
        configured = (stored_configured or env_configured) and bool(self.finebi_base_url)
        return {
            "configured": configured,
            "source": source,
            "username": str((stored or env).get("username") or ""),
            "has_password": bool((stored or env).get("password")),
            "has_token": bool((stored or env).get("user_token")),
            "updated_at": str(stored.get("updated_at") or ""),
            "last_test_at": str(stored.get("last_test_at") or ""),
            "last_test_ok": stored.get("last_test_ok"),
            "last_test_message": str(stored.get("last_test_message") or ""),
            "enabled": bool(self.data_client and self.data_client.enabled()),
        }

    def configure_data_api(self, base_url: Optional[str] = None,
                           http_client=None,
                           env: Optional[Dict[str, str]] = None) -> None:
        if base_url is not None:
            self.finebi_base_url = str(base_url or "").rstrip("/")
        if http_client is not None:
            self.http_client = http_client
        if env is not None:
            self._data_api_env = dict(env)
        stored = self.load_data_api_config()
        defaults = self._data_api_env or {}
        token = str(stored.get("user_token") or defaults.get("user_token") or "")
        username = str(stored.get("username") or defaults.get("username") or "")
        password = str(stored.get("password") or defaults.get("password") or "")
        if self.finebi_base_url and (token or (username and password)):
            self.data_client = FineBIDataClient(
                self.finebi_base_url, token, username=username,
                password=password, http=self.http_client)
        else:
            self.data_client = None
        self._field_values_cache.clear()
        self._row_values_api_cache.clear()

    def save_data_api_config(self, username: str = "", password: str = "",
                             user_token: str = "", clear_password: bool = False,
                             clear_token: bool = False,
                             clear_all: bool = False) -> Dict[str, Any]:
        existing = {} if clear_all else self.load_data_api_config()
        payload = dict(existing)
        if username.strip():
            payload["username"] = username.strip()
        if password:
            payload["password"] = password
        elif clear_password:
            payload.pop("password", None)
        if user_token.strip():
            payload["user_token"] = user_token.strip()
        elif clear_token:
            payload.pop("user_token", None)
        payload["updated_at"] = now_iso()
        payload.setdefault("last_test_ok", None)
        payload.setdefault("last_test_message", "")
        self._save_data_api_payload(payload)
        self.configure_data_api()
        return self.data_api_status()

    def test_data_api(self) -> Dict[str, Any]:
        if self.data_client is None or not self.data_client.enabled():
            raise WebApprovalError("尚未配置 FineBI 数据接口账号或 token")
        rows = [r for r in self.resources("table", limit=20)
                if isinstance(r, dict) and r.get("resource_id")]
        if not rows:
            raise WebApprovalError("目录中暂无公共数据集，无法测试")
        result = {"ok": False, "message": "", "table": "", "at": now_iso()}
        errors: List[str] = []
        # 服务账号可能只被授权了部分数据集，逐个尝试，避免“第一个没权限”误判
        for row in rows[:10]:
            table_id = str(row.get("resource_id") or "")
            table_name = str(row.get("name") or "")
            meta = self._table_meta(table_id)
            candidates = [str(meta.get("tableName") or ""),
                          str(meta.get("transferName") or ""),
                          table_id, table_name]
            for candidate in candidates:
                if not candidate:
                    continue
                try:
                    fields, rows_data = self.data_client.preview(
                        candidate, page_size=1)
                    if fields:
                        result.update({
                            "ok": True, "table": table_name or table_id,
                            "message": "连接成功，返回 %d 个字段、%d 行样例"
                                       % (len(fields), len(rows_data))})
                        break
                except Exception as exc:  # noqa: BLE001
                    errors.append("%s：%s" % (table_name or table_id,
                                              str(exc)[:180]))
            if result["ok"]:
                break
        if not result["ok"]:
            detail = "；".join(errors[-3:]) or "接口返回空字段列表"
            result["message"] = "连接失败（已尝试 %d 个数据集）：%s" % (
                min(len(rows), 10), detail[:500])
        payload = self.load_data_api_config()
        payload["last_test_at"] = result["at"]
        payload["last_test_ok"] = result["ok"]
        payload["last_test_message"] = result["message"]
        try:
            self._save_data_api_payload(payload)
        except WebApprovalError:
            LOGGER.warning("保存数据接口测试结果失败")
        return result

    # ---------- 用户 ----------
    def invalidate_permission_cache(self) -> None:
        """权限变更后主动失效，避免 12h 缓存继续显示旧权限。"""
        self._permission_status_cache.clear()
        self._permission_map_cache.clear()

    def seed_users(self) -> None:
        users = (self.policy.get("web_approval") or {}).get("users") or []
        for user in users:
            uid = str(user.get("id") or "").strip()
            if not uid:
                continue
            self.storage.conn.execute(
                "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,created_at) "
                "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,"
                "email=excluded.email,feishu_open_id=excluded.feishu_open_id,"
                "fb_user=excluded.fb_user,roles=excluded.roles,active=excluded.active",
                (uid, user.get("name") or uid, user.get("email") or "",
                 user.get("feishu_open_id") or "", user.get("fb_user") or uid,
                 _json(user.get("roles") or ["applicant"]), 1, now_iso()))
        self.storage.conn.commit()

    def list_users(self) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM web_users WHERE active=1 AND id NOT LIKE 'admin:%' "
            "ORDER BY name").fetchall()
        return [self._user_row(r) for r in rows]

    def ensure_admin_user(self, username: str) -> Dict[str, Any]:
        """后台独立登录账号：本地 web_users 行，id 前缀 admin:，不参与飞书映射。"""
        name = str(username or "").strip()
        if not name:
            raise WebApprovalError("后台用户名不能为空")
        uid = "admin:" + name
        self.storage.conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,feishu_user_id,"
            "fb_user,roles,active,created_at) VALUES(?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name,roles=excluded.roles,"
            "active=excluded.active",
            (uid, "后台管理员", "", "", "", "", _json(["admin"]), 1, now_iso()))
        self.storage.conn.commit()
        user = self.get_user(uid)
        if not user:
            raise WebApprovalError("后台账号创建失败")
        return user

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = self.storage.conn.execute(
            "SELECT * FROM web_users WHERE id=? AND active=1", (user_id,)).fetchone()
        return self._user_row(row) if row else None

    def find_by_feishu_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = self.storage.conn.execute(
            "SELECT * FROM web_users WHERE feishu_user_id=? AND active=1", (user_id,)).fetchone()
        return self._user_row(row) if row else None

    def find_by_open_id(self, open_id: str) -> Optional[Dict[str, Any]]:
        row = self.storage.conn.execute(
            "SELECT * FROM web_users WHERE feishu_open_id=? AND active=1", (open_id,)).fetchone()
        return self._user_row(row) if row else None

    @staticmethod
    def _user_row(row) -> Dict[str, Any]:
        data = dict(row)
        try:
            data["roles"] = json.loads(data.get("roles") or "[]")
        except json.JSONDecodeError:
            data["roles"] = []
        return data

    def users_by_role(self, role: str) -> List[Dict[str, Any]]:
        return [u for u in self.list_users() if role in (u.get("roles") or [])]

    def _build_steps(self, applicant_id: str, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """审批链：角色/部门统一审批人；其他资源数据 Owner → 业务 Owner。

        角色/部门申请只需要配置一个统一审批人；未配置或审批人就是申请人时，
        回退 default_approver/admin。
        """
        applicant_ids = self.identities(applicant_id)
        steps: List[Dict[str, Any]] = []
        if item.get("resource_type") in ("role", "department"):
            owner = self.membership_owner()
            if owner and owner["id"] not in applicant_ids:
                steps.append({"role": "membership_owner",
                              "approver_id": owner["id"]})
        if not steps:
            owners = self._owners_by_type_for_request(
                item.get("resource_type", ""), item.get("resource_id", ""),
                item.get("resource_path", ""))
            for owner_type, role, _label in OWNER_CHAIN:
                candidates = [u for u in owners.get(owner_type, [])
                              if u["id"] not in applicant_ids]
                if candidates:
                    steps.append({"role": role, "approver_id": candidates[0]["id"]})
        if not steps:
            configured = self.default_approver()
            fallback = configured["id"] if configured and self.get_user(configured["id"]) else ""
            if not fallback:
                fallback = (self.policy.get("web_approval") or {}).get("default_approver") or ""
            if not fallback or not self.get_user(fallback):
                admins = self.users_by_role("admin")
                fallback = admins[0]["id"] if admins else ""
            if not fallback or not self.get_user(fallback):
                raise WebApprovalError(
                    "还没有配置审批人：请在后台配置「默认审批人」，"
                    "或给该资源配置数据/业务 Owner")
            steps.append({"role": "owner", "approver_id": fallback})
        for seq, step in enumerate(steps):
            step["seq"] = seq
        return steps

    # ---------- 飞书用户映射 ----------
    def resolve_fb_user(self, mobile: str = "", email: str = "",
                        name: str = "") -> str:
        """用手机号/邮箱/姓名在 FineBI 用户目录里找对应账号。

        客户 FineBI 的飞书集成按**手机号**匹配，因此顺序是：
        FineDB fine_user.mobile → 开放平台 mobile → email → username（完全相等）。
        姓名只接受完全相等的 username：FineBI 的 username 查询是模糊匹配，
        直接取第一条会把飞书昵称 gust 错配到 FineBI 账号 Gust。
        """
        mobiles = mobile_candidates(mobile)
        if mobiles and self.finedb is not None and self.finedb.enabled():
            for value in mobiles:
                try:
                    fb_user = self.finedb.user_by_mobile(value)
                except Exception as exc:  # noqa: BLE001
                    LOGGER.warning("FineDB 手机号匹配失败：%s", exc)
                    fb_user = ""
                if fb_user:
                    return fb_user
        if not self.platform:
            return ""
        attempts = [("mobile", value) for value in mobiles]
        if email:
            attempts.append(("email", email))
        if name:
            attempts.append(("username", name))
        for key, value in attempts:
            try:
                resp = self.platform.query_user_detail(**{key: value})
                data = (resp or {}).get("data") or {}
                items = data.get("items") or []
                if key == "username":
                    for item in items:
                        username = str(item.get("username") or "")
                        if username and username == value:
                            return username
                    continue
                if len(items) == 1 and items[0].get("username"):
                    return str(items[0]["username"])
            except Exception:  # noqa: BLE001
                continue
        return ""

    def fb_user_for_feishu_user(self, feishu_user_id: str) -> str:
        """按飞书 user_id 从 FineDB 映射表反查 FineBI 账号（最可靠）。"""
        if not feishu_user_id or not self.finedb or not self.finedb.enabled():
            return ""
        try:
            return self.finedb.feishu_user_by_id(feishu_user_id) or ""
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("FineDB 飞书映射查询失败：%s", exc)
            return ""

    def update_user_fb_user(self, user_id: str, fb_user: str) -> None:
        """管理员手工修正某条飞书映射对应的 FineBI 账号。"""
        if not self.get_user(user_id):
            raise WebApprovalError("用户不存在：%s" % user_id)
        self.storage.conn.execute(
            "UPDATE web_users SET fb_user=? WHERE id=?", ((fb_user or "").strip(), user_id))
        self.storage.conn.commit()

    def sync_feishu_users(self, feishu_users: List[Dict[str, Any]]) -> int:
        count = 0
        for item in feishu_users or []:
            open_id = str(item.get("open_id") or item.get("user_id") or "")
            if not open_id:
                continue
            name = str(item.get("name") or open_id)
            mobile = str(item.get("mobile") or "")
            email = str(item.get("email") or "")
            fb_user = self.resolve_fb_user(mobile=mobile, email=email, name=name) or open_id
            existing = self.find_by_open_id(open_id)
            if existing:
                self.storage.conn.execute(
                    "UPDATE web_users SET name=?, email=?, fb_user=?, active=1 WHERE id=?",
                    (name, email, fb_user, existing["id"]))
            else:
                self.storage.conn.execute(
                    "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    ("fs_" + open_id, name, email, open_id, fb_user,
                     '["applicant"]', 1, now_iso()))
            count += 1
        self.storage.conn.commit()
        return count

    def sync_finedb_mapping(self) -> int:
        if not self.finedb or not self.finedb.enabled():
            return 0
        count = 0
        try:
            mapping = self.finedb.feishu_mapping()
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("FineDB 飞书映射读取失败，跳过同步：%s", exc)
            return 0
        for item in mapping:
            fb_user = item.get("fb_user") or ""
            feishu_user_id = item.get("feishu_user_id") or ""
            if not fb_user or not feishu_user_id:
                continue
            existing = self.find_by_feishu_user_id(feishu_user_id)
            if existing:
                self.storage.conn.execute(
                    "UPDATE web_users SET fb_user=?, active=1 WHERE id=?",
                    (fb_user, existing["id"]))
            else:
                self.storage.conn.execute(
                    "INSERT INTO web_users(id,name,email,feishu_open_id,feishu_user_id,fb_user,roles,active,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    ("fs_" + feishu_user_id, fb_user, "", "", feishu_user_id,
                     fb_user, '["applicant"]', 1, now_iso()))
            count += 1
        self.storage.conn.commit()
        return count

    def mapping_rows(self) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT id,name,feishu_open_id,feishu_user_id,fb_user,roles FROM web_users "
            "WHERE id NOT LIKE 'admin:%' ORDER BY name").fetchall()
        return [self._user_row(r) for r in rows]

    def mapping_page(self, page: int = 1, page_size: int = 50,
                     keyword: str = "") -> Dict[str, Any]:
        """后台「飞书用户映射」分页查询（人数多时避免一页渲染几百行）。"""
        where = "WHERE id NOT LIKE 'admin:%'"
        params: List[Any] = []
        kw = str(keyword or "").strip()
        if kw:
            where += (" AND (name LIKE ? OR fb_user LIKE ? OR feishu_open_id LIKE ?"
                      " OR feishu_user_id LIKE ?)")
            like = "%" + kw + "%"
            params = [like, like, like, like]
        conn = self.storage.conn
        total = int(conn.execute("SELECT COUNT(*) FROM web_users " + where,
                                 tuple(params)).fetchone()[0])
        page_size = max(10, min(200, int(page_size or 50)))
        pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(int(page or 1), pages))
        offset = (page - 1) * page_size
        rows = conn.execute(
            "SELECT id,name,feishu_open_id,feishu_user_id,fb_user,roles FROM web_users "
            + where + " ORDER BY name LIMIT ? OFFSET ?",
            tuple(params) + (page_size, offset)).fetchall()
        return {"rows": [self._user_row(r) for r in rows], "total": total,
                "page": page, "pages": pages, "page_size": page_size,
                "keyword": kw}

    def identities(self, user_id: str) -> List[str]:
        """同一 FineBI 账号可能有多条飞书映射，审批身份按 fb_user + 姓名合并。

        只合并“同 fb_user 且同名”的账号：这样“Gust-帆软软件”的多条映射可互相
        审批，而申请人 gust 不会因为和审批人共用 FineBI 账号（fb_user=Gust）
        就被当成审批人、出现自己批自己。
        """
        user = self.get_user(user_id)
        ids = {user_id}
        if user and user.get("fb_user"):
            rows = self.storage.conn.execute(
                "SELECT id, name FROM web_users WHERE fb_user=? AND active=1",
                (user["fb_user"],)).fetchall()
            name = str(user.get("name") or "")
            ids.update(str(r["id"]) for r in rows if str(r["name"] or "") == name)
        return sorted(ids)

    def can_approve(self, user_id: str, step: Optional[Dict[str, Any]]) -> bool:
        if not step:
            return False
        return step.get("approver_id") in self.identities(user_id)

    # ---------- 会话 ----------
    def create_session(self, user_id: str, hours: int = 8) -> str:
        sid = new_id("sess")
        now = datetime.now().astimezone()
        self.storage.conn.execute(
            "INSERT INTO web_sessions(id,user_id,created_at,expires_at) VALUES(?,?,?,?)",
            (sid, user_id, now.isoformat(timespec="seconds"),
             (now + timedelta(hours=hours)).isoformat(timespec="seconds")))
        self.storage.conn.commit()
        return sid

    def get_session_user(self, session_id: str) -> Optional[Dict[str, Any]]:
        row = self.storage.conn.execute(
            "SELECT * FROM web_sessions WHERE id=? AND expires_at>?",
            (session_id, now_iso())).fetchone()
        return self.get_user(row["user_id"]) if row else None

    # ---------- 申请 ----------
    @staticmethod
    def _applicant_account(applicant: Dict[str, Any]) -> str:
        return str(applicant.get("fb_user") or applicant.get("id") or applicant.get("name") or "")

    @staticmethod
    def _permission_content(category: str, item: Dict[str, Any]) -> str:
        actions = item.get("permissions") or item.get("actions") or []
        labels = "、".join(ACTION_LABELS.get(str(a), str(a)) for a in actions)
        if category == "membership":
            name = str(item.get("resource_name") or "")
            entity = item.get("entity_permissions") or {}
            summary = entity.get("summary") if entity.get("known") else None
            if not summary:
                return name
            parts: List[str] = []
            tables = summary.get("tables") or {}
            folders = summary.get("folders") or {}
            rows = summary.get("rows") or {}
            dashboards = summary.get("dashboards") or {}
            entries = summary.get("entries") or {}
            if folders.get("count"):
                parts.append("文件夹 %d 个" % folders["count"])
            if tables.get("count"):
                parts.append("数据集 %d 个" % tables["count"])
            if tables.get("component"):
                parts.append("组件数据 %d 个" % tables["component"])
            if rows.get("count"):
                parts.append("行权限 %d 个数据集" % rows["count"])
            if dashboards.get("available") and dashboards.get("view"):
                parts.append("看板 %d 个" % dashboards["view"])
            if entries.get("view"):
                parts.append("目录项 %d 个" % entries["view"])
            return name + (("（" + "、".join(parts) + "）") if parts else "")
        if category == "admin":
            name = str(item.get("resource_name") or item.get("schedule_task")
                       or item.get("module") or "")
            return name + (("（" + labels + "）") if labels else "")
        name = str(item.get("resource_name") or item.get("resource_path")
                   or item.get("resource_id") or "")
        extra = ""
        if item.get("resource_type") == "dashboard_folder":
            extra = "（文件夹下 %d 个仪表板）" % len(item.get("targets") or [])
        content = name + extra
        result = content + (("；权限：" + labels) if labels else "")
        deps = item.get("component_datasets") or []
        if deps:
            names = "、".join(str(d.get("name") or d.get("resource_id") or "")
                             for d in deps if isinstance(d, dict))
            if names:
                result += "（组件数据覆盖数据集：" + names + "）"
        scopes = item.get("component_scopes") or {}
        if scopes:
            configured = [key for key, value in scopes.items()
                          if isinstance(value, dict)
                          and (value.get("row_enabled") or value.get("field_ids"))]
            if configured:
                result += "；组件行/列权限：%d/%d 个数据集" % (
                    len(configured), len(deps or scopes))
        rules = (item.get("data_scope") or {}).get("rules") or []
        if rules and isinstance(rules[0], dict):
            rule = rules[0]
            values = [str(v) for v in (rule.get("filterValue") or [])]
            if values:
                operator = "不属于" if rule.get("type") == "strNotIn" else "属于"
                result += "；行权限：%s %s %s" % (
                    rule.get("fieldId") or "", operator, "、".join(values[:5]))
        field_ids = [str(f) for f in (item.get("field_ids") or []) if str(f)]
        if field_ids:
            result += "；列权限：%d 个字段" % len(field_ids)
        return result

    @staticmethod
    def _permission_time(item: Dict[str, Any]) -> str:
        if str(item.get("period_type") or "") == "long":
            return "长期"
        try:
            days = max(1, int(item.get("days") or 1))
        except (TypeError, ValueError):
            days = 1
        start = datetime.now().astimezone().date()
        end = start + timedelta(days=days - 1)
        return "%s 至 %s（%d 天）" % (start.isoformat(), end.isoformat(), days)

    def card_fields(self, req: Optional[Dict[str, Any]]) -> List[tuple]:
        """飞书卡片/多维表格共用的单据字段。"""
        if not req:
            return []
        payload = req.get("payload") or {}
        applicant = req.get("applicant") or {}
        fields = [
            ("单号", payload.get("request_no")),
            ("日期", payload.get("request_date")),
            ("自增键", payload.get("serial_text")),
            ("申请人", applicant.get("name")),
            ("申请人账号", payload.get("applicant_account")),
            ("权限内容", payload.get("permission_content")),
            ("权限时间", payload.get("permission_time")),
        ]
        if req.get("status") == "pending":
            if (req.get("category") == "public_data"
                    and payload.get("resource_type") == "table"):
                fields.append((
                    "行/列权限",
                    "请在审批详情页按需补充；数据权限通过后再授行/列权限"))
            elif req.get("category") == "membership":
                fields.append((
                    "实体权限",
                    "该角色/部门当前权限摘要见审批详情页，用于辅助判断"))
        return fields

    PERMISSION_STATUS_TTL = 12 * 60 * 60
    # FineBI 数据权限字段 → 前端动作；展示“已有权限”时按字段全量返回，与勾选无关。
    # biView 在 FineBI 数据权限页叫“元数据”（旧文档写作“组件查看 BI7.0 支持”）。
    TABLE_FIELD_ACTIONS = (
        ("usePrivilege", "use"),
        ("managePrivilege", "manage"),
        ("empowerPrivilege", "empower"),
        ("biData", "component"),
        ("biView", "metadata"),
    )
    ENTRY_FIELD_ACTIONS = (
        ("viewPrivilege", "view"),
        ("export", "export"),
        ("editPrivilege", "edit"),
        ("empowerPrivilege", "empower"),
    )
    TEMPLATE_FIELD_ACTIONS = (("view", "view"), ("export", "export"))

    def permission_status(self, user_id: str, resource_type: str = "",
                          resource_id: str = "", entry_id: str = "",
                          resource_path: str = "",
                          actions: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询用户当前已有权限（只读，列出全部已有项，不受表单勾选影响）。"""
        user = self.get_user(user_id)
        fb_user = str((user or {}).get("fb_user") or "")
        perm = self.permission
        if (not fb_user or not perm or not getattr(perm, "finebi", None)
                or not getattr(perm, "handlers", None)):
            return {"known": False}
        key = (fb_user, resource_type, resource_id, entry_id, resource_path)
        now = time.time()
        cached = self._permission_status_cache.get(key)
        if cached and now - cached[0] < self.PERMISSION_STATUS_TTL:
            return cached[1]
        try:
            result = self._permission_status(
                fb_user, str(resource_type or ""), str(resource_id or ""),
                str(entry_id or ""), str(resource_path or ""), perm)
        except Exception:  # noqa: BLE001 - 提示失败不影响申请
            LOGGER.warning("已有权限查询失败", exc_info=True)
            result = {"known": False}
        self._permission_status_cache[key] = (now, result)
        return result

    def permission_map(self, user_id: str, category: str) -> Dict[str, Any]:
        """批量查询用户已有权限，供资源下拉框节点显示“已有：xxx”。

        只做只读接口；单次批量查询失败时返回空表，不影响申请。
        """
        user = self.get_user(user_id)
        fb_user = str((user or {}).get("fb_user") or "")
        finebi = self._finebi_client()
        if not fb_user or finebi is None:
            return {"category": category, "items": {}, "known": False}
        key = (fb_user, category)
        now = time.time()
        cached = self._permission_map_cache.get(key)
        if cached and now - cached[0] < self.PERMISSION_STATUS_TTL:
            return cached[1]
        items: Dict[str, Dict[str, Any]] = {}
        try:
            if category == "public_data":
                tables = [str(r.get("resource_id") or "")
                          for r in self.resources("table", limit=5000)
                          if r.get("resource_id")]
                for start in range(0, len(tables), 200):
                    chunk = tables[start:start + 200]
                    resp = finebi.get_table_permissions_user(fb_user, chunk)
                    data = (resp or {}).get("data") or []
                    for rid, entry in zip(chunk, data):
                        authority = (entry or {}).get("data") if isinstance(
                            entry, dict) else None
                        actions = self._actions_from(authority,
                                                     self.TABLE_FIELD_ACTIONS)
                        if actions:
                            items[rid] = self._permission_item(actions)
            elif category == "dashboard":
                rows = [r for r in self.resources("dashboard", limit=5000)
                        if r.get("entry_id")]
                entries = [str(r.get("entry_id") or "") for r in rows]
                for start in range(0, len(entries), 200):
                    chunk = entries[start:start + 200]
                    resp = finebi.get_entry_authority(fb_user, chunk)
                    data = (resp or {}).get("data") or {}
                    entry_rows = data.get("entry") if isinstance(data, dict) else data
                    if not isinstance(entry_rows, list):
                        continue
                    # 批量接口返回顺序与入参不一致，必须按 entryId 映射，不能 zip。
                    for entry in entry_rows:
                        if not isinstance(entry, dict):
                            continue
                        rid = str(entry.get("entryId") or entry.get("entry") or "")
                        if not rid:
                            continue
                        authority = entry.get("authority")
                        actions = self._actions_from(authority,
                                                     self.ENTRY_FIELD_ACTIONS)
                        if actions:
                            items[rid] = self._permission_item(actions)
        except Exception:  # noqa: BLE001
            LOGGER.warning("批量已有权限查询失败：category=%s", category,
                           exc_info=True)
        result = {"category": category, "items": items, "known": bool(items)}
        self._permission_map_cache[key] = (now, result)
        return result

    @staticmethod
    def _actions_from(authority: Any, mapping) -> List[str]:
        if not isinstance(authority, dict):
            return []
        return [action for field, action in mapping if authority.get(field)]

    @staticmethod
    def _permission_item(actions: List[str]) -> Dict[str, Any]:
        return {"actions": actions,
                "labels": [ACTION_LABELS.get(action, action)
                           for action in actions]}

    @staticmethod
    def _first_authority(resp: Any) -> Any:
        """取 FineBI 批量权限响应的第一条 data（authority 对象）。"""
        if not isinstance(resp, dict):
            return None
        data = resp.get("data")
        if isinstance(data, list) and data:
            item = data[0]
            if isinstance(item, dict):
                return item.get("data")
        return None

    @staticmethod
    def _own_from(authority: Any, mapping) -> Dict[str, bool]:
        cur = authority if isinstance(authority, dict) else {}
        return {action: True for field, action in mapping if bool(cur.get(field))}

    def _permission_status(self, fb_user: str, resource_type: str, resource_id: str,
                           entry_id: str, resource_path: str,
                           perm) -> Dict[str, Any]:
        def read(type_name: str, rid: str):
            handler = (perm.handlers or {}).get(type_name)
            if not handler or not handler.read or not rid:
                return None
            try:
                return self._first_authority(
                    handler.read(perm.clients, fb_user, rid))
            except Exception:  # noqa: BLE001 - 读不到就不提示
                LOGGER.debug("已有权限读取失败：%s %s", type_name, rid,
                             exc_info=True)
                return None

        if resource_type == "dashboard_entry":
            authority = read("dashboard_entry", entry_id or resource_id)
            if authority is None:
                return {"known": False}
            return {"known": True,
                    "own": self._own_from(authority, self.ENTRY_FIELD_ACTIONS)}
        if resource_type in ("dashboard", "dashboard_view", "dashboard_export"):
            own: Dict[str, bool] = {}
            entry_authority = read("dashboard_entry", entry_id)
            if entry_authority is not None:
                own.update(self._own_from(entry_authority,
                                          self.ENTRY_FIELD_ACTIONS))
            template_authority = read("dashboard_view", resource_id)
            if template_authority is not None:
                own.update(self._own_from(template_authority,
                                          self.TEMPLATE_FIELD_ACTIONS))
            if entry_authority is None and template_authority is None:
                return {"known": False}
            public_deps, self_deps = self._component_dependency_sets([resource_id])
            return {"known": True, "own": own,
                    "dependencies": public_deps,
                    "self_service_dependencies": self_deps}
        if resource_type == "dashboard_folder":
            targets = self._dashboards_under_folder(resource_path)
            entries = [str(t.get("entry_id") or "") for t in targets
                       if t.get("entry_id")]
            if not entries:
                return {"known": False}
            try:
                resp = perm.finebi.get_entry_authority(fb_user, entries)
            except Exception:  # noqa: BLE001
                return {"known": False}
            data = (resp or {}).get("data") or {}
            rows = data.get("entry") if isinstance(data, dict) else None
            rows = rows or []
            counts = {action: 0 for _, action in self.ENTRY_FIELD_ACTIONS}
            for row in rows:
                auth = (row or {}).get("authority") or {}
                for field, action in self.ENTRY_FIELD_ACTIONS:
                    if auth.get(field):
                        counts[action] += 1
            own = {action: True for action, count in counts.items()
                   if count >= len(entries)}
            public_deps, self_deps = self._component_dependency_sets(
                [str(t.get("resource_id") or "") for t in targets])
            return {"known": True, "own": own, "folder_counts": counts,
                    "folder_total": len(entries), "dependencies": public_deps,
                    "self_service_dependencies": self_deps}
        if resource_type in ("folder", "table"):
            authority = read(resource_type, resource_id)
            if authority is None:
                return {"known": False}
            return {"known": True,
                    "own": self._own_from(authority, self.TABLE_FIELD_ACTIONS)}
        if resource_type in ("role", "department"):
            handler = (perm.handlers or {}).get(resource_type)
            if not handler or not handler.read or not resource_id:
                return {"known": False}
            item = {"resource_type": resource_type,
                    "resource_id": resource_id, "actions": ["use"],
                    "data_scope": {}}
            try:
                current = handler.read(perm.clients, fb_user, resource_id)
            except Exception:  # noqa: BLE001
                return {"known": False}
            desired = perm._desired(resource_type, item)
            joined = bool(desired) and perm._satisfied(
                resource_type, item, desired, current, fb_user)
            return {"known": True, "own": {"join": True} if joined else {}}
        return {"known": False}

    def _dashboard_deps(self) -> Dict[str, Any]:
        path = getattr(self, "deps_json", lineage.DEFAULT_DEPS_JSON)
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return {}
        cache = getattr(self, "_deps_cache", None) or {}
        if cache.get("mtime") == mtime:
            return cache.get("data") or {}
        data = lineage.load_dashboard_deps(path)
        self._deps_cache = {"mtime": mtime, "data": data}
        return data

    def dashboard_dependencies(self, dashboard_id: str) -> List[Dict[str, str]]:
        """某台仪表板依赖的公共数据集（来自目录刷新快照）。"""
        if not dashboard_id:
            return []
        return lineage.dashboard_datasets(self._dashboard_deps(),
                                          str(dashboard_id))

    # ---------- 行/列权限（审批人补充配置用） ----------
    ROW_PERMISSION_TTL = 300
    ENTITY_PERMISSION_TTL = 300
    SUBJECT_NAMES_LIMIT = 8
    USER_SCAN_LIMIT = 2000

    @staticmethod
    def _first_batch_data(resp: Any) -> List[Any]:
        """FineBI 批量 get 响应 → 每条数据的 data（与入参顺序一致）。"""
        data = (resp or {}).get("data") if isinstance(resp, dict) else None
        if not isinstance(data, list):
            return []
        return [item.get("data") if isinstance(item, dict) else None
                for item in data]

    @staticmethod
    def _rule_present(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, dict):
            return bool(value.get("filterValue") or value.get("filterType"))
        if isinstance(value, list):
            return bool(value)
        return True

    @staticmethod
    def _chunks(items: List[Any], size: int) -> List[List[Any]]:
        size = max(1, int(size or 1))
        return [items[i:i + size] for i in range(0, len(items), size)]

    def _clients(self):
        clients = getattr(self.permission, "clients", None)
        return clients

    def _finebi_client(self):
        return getattr(self._clients(), "finebi", None)

    def _platform_client(self):
        return getattr(self._clients(), "platform", None)

    def _table_row(self, table_id: str) -> Dict[str, Any]:
        return self._catalog_row("table", resource_id=str(table_id or "")) or {}

    def table_fields(self, table_id: str) -> List[Dict[str, str]]:
        """数据集字段（列权限选择器用）。优先目录快照，缺失时查 FineBI。"""
        key = str(table_id or "")
        if not key:
            return []
        cached = self._fields_cache.get(key)
        if cached is not None:
            return list(cached)
        fields: List[Dict[str, str]] = []
        for item in self._table_row(key).get("fields") or []:
            if isinstance(item, dict) and item.get("fieldId"):
                fields.append({"field_id": str(item["fieldId"]),
                               "name": str(item.get("name") or item["fieldId"])})
        if not fields:
            finebi = self._finebi_client()
            if finebi is not None and hasattr(finebi, "get_tables_info"):
                try:
                    resp = finebi.get_tables_info([key])
                    for item in self._first_batch_data(resp):
                        if not isinstance(item, dict):
                            continue
                        for field in item.get("fields") or []:
                            if isinstance(field, dict) and field.get("fieldId"):
                                fields.append({
                                    "field_id": str(field["fieldId"]),
                                    "name": str(field.get("transferName")
                                                or field.get("name")
                                                or field["fieldId"])})
                        break
                except Exception:  # noqa: BLE001
                    LOGGER.warning("读取数据集字段失败：%s", key, exc_info=True)
        self._fields_cache[key] = fields
        return list(fields)

    def _table_meta(self, table_id: str) -> Dict[str, Any]:
        """数据集元数据（含 SQL/连接名），用于从源数据取去重值。"""
        key = str(table_id or "")
        if not key:
            return {}
        cached = self._table_meta_cache.get(key)
        if cached is not None:
            return dict(cached)
        meta: Dict[str, Any] = {}
        finebi = self._finebi_client()
        if finebi is not None and hasattr(finebi, "get_tables_info"):
            try:
                resp = finebi.get_tables_info([key])
                for item in self._first_batch_data(resp):
                    if isinstance(item, dict):
                        meta = dict(item)
                        break
            except Exception:  # noqa: BLE001
                LOGGER.warning("读取数据集元数据失败：%s", key, exc_info=True)
        self._table_meta_cache[key] = meta
        return dict(meta)

    def field_values(self, table_id: str, field_id: str,
                     limit: int = 500) -> Dict[str, Any]:
        """字段去重值：优先直接从数据集 SQL 取真实数据，失败回退行权限规则值。"""
        table = str(table_id or "")
        field = str(field_id or "")
        if not table or not field:
            return {"field_id": field, "values": [], "source": ""}
        cache_key = (table, field)
        cached = self._field_values_cache.get(cache_key)
        if cached and time.time() - cached[0] < 600:
            return dict(cached[1])
        fields = self.table_fields(table)
        name = ""
        for item in fields:
            if str(item.get("field_id") or "") == field:
                name = str(item.get("name") or field)
                break
        if not name:
            return {"field_id": field, "values": [], "source": ""}
        values: List[str] = []
        source = ""
        scan: Dict[str, Any] = {}
        meta = self._table_meta(table)
        source_sql = str(meta.get("sql") or "")
        source_field = name
        for item in meta.get("fields") or []:
            if isinstance(item, dict) and str(item.get("fieldId") or "") == field:
                source_field = str(item.get("transferName") or item.get("name")
                                   or name)
                break
        table_names = [str(meta.get("tableName") or ""),
                       str(meta.get("transferName") or ""), table]
        if self.data_client is not None and getattr(self.data_client, "enabled", lambda: False)():
            try:
                values = self.data_client.field_values(
                    table_names, field, source_field, limit=limit) or []
                scan = dict(getattr(self.data_client, "last_scan", {}) or {})
                if values:
                    source = "data-api"
            except Exception:  # noqa: BLE001
                LOGGER.warning("FineBI 数据接口取去重值失败：%s.%s", table, field,
                               exc_info=True)
        # 兼容旧环境：数据接口未配置/失败时，才尝试 FineDB 同实例 SQL（可选）。
        if not values and source_sql and self.finedb and self.finedb.enabled():
            try:
                values = self.finedb.distinct_values(
                    source_sql, source_field, limit=limit) or []
                if values:
                    source = "data-sql"
            except Exception:  # noqa: BLE001
                LOGGER.warning("字段去重值 SQL 兜底失败：%s.%s", table, field,
                               exc_info=True)
        if not values:
            for option in self.row_values(table, ""):
                if str(option.get("field_id") or "") == field:
                    values = [str(v) for v in option.get("values") or []]
                    source = "rule"
                    break
        result = {"field_id": field, "name": name, "values": values,
                  "source": source,
                  "scanned_rows": int(scan.get("scanned_rows") or 0),
                  "total_rows": int(scan.get("total_rows") or 0),
                  "scanned_pages": int(scan.get("pages") or 0)}
        LOGGER.info("字段去重值：table=%s field=%s source=%s count=%s "
                    "scanned_rows=%s total_rows=%s",
                    table, field, source or "none", len(values),
                    result["scanned_rows"], result["total_rows"])
        self._field_values_cache[cache_key] = (time.time(), result)
        return dict(result)

    def _department_nodes(self) -> List[Dict[str, Any]]:
        platform = self._platform_client()
        if platform is None or not hasattr(platform, "query_departments"):
            return []
        try:
            resp = platform.query_departments([])
        except Exception:  # noqa: BLE001
            LOGGER.warning("读取部门树失败", exc_info=True)
            return []
        items = (resp or {}).get("data") or []
        if isinstance(items, dict):
            items = items.get("items") or []
        return [item for item in items if isinstance(item, dict) and item.get("id")]

    def _department_subjects(self) -> List[Dict[str, str]]:
        """行权限检测主体：部门节点 + 岗位节点（部门/岗位 ID 组合）。"""
        subjects: List[Dict[str, str]] = []
        for item in self._department_nodes():
            node_type = str(item.get("type") or "department")
            name = str(item.get("name") or "")
            if node_type == "position":
                subjects.append({"department": str(item.get("pId") or ""),
                                 "position": str(item.get("id") or ""),
                                 "name": "岗位：" + name})
            else:
                subjects.append({"department": str(item.get("id") or ""),
                                 "position": "",
                                 "name": "部门：" + name})
        return subjects

    def _department_id_for_target(self, target: str) -> str:
        try:
            parts = json.loads(target)
        except (TypeError, ValueError):
            return ""
        if not isinstance(parts, list):
            return ""
        nodes = self._department_nodes()
        by_id = {str(n.get("id")): n for n in nodes}
        for node in nodes:
            if str(node.get("type") or "department") != "department":
                continue
            path: List[str] = []
            current = node
            seen = set()
            while current:
                node_id = str(current.get("id") or "")
                if not node_id or node_id in seen:
                    break
                seen.add(node_id)
                path.insert(0, str(current.get("name") or ""))
                parent = by_id.get(str(current.get("pId") or ""))
                current = parent
            if path == [str(p) for p in parts]:
                return str(node.get("id"))
        return ""

    def _list_usernames(self, limit: int = 2000) -> List[str]:
        platform = self._platform_client()
        if platform is None or not hasattr(platform, "query_users"):
            return []
        users: List[str] = []
        page = 1
        for _ in range(10):
            try:
                resp = platform.query_users(page=page, count=200)
            except Exception:  # noqa: BLE001
                LOGGER.warning("读取用户列表失败（第 %s 页）", page, exc_info=True)
                break
            data = (resp or {}).get("data") or {}
            items = data.get("items") if isinstance(data, dict) else (data or [])
            total = int(data.get("total") or 0) if isinstance(data, dict) else 0
            for item in items or []:
                if not isinstance(item, dict):
                    continue
                if item.get("enable") is False:
                    continue
                username = str(item.get("username") or "")
                if username:
                    users.append(username)
            if not items or len(users) >= limit or (total and len(users) >= total):
                break
            page += 1
        return users[:limit]

    def row_permission_status(self, table_id: str,
                              applicant_fb_user: str = "") -> Dict[str, Any]:
        """检测数据集是否配置了行权限（任意角色/部门/用户），供审批页提示。

        官方接口没有“数据集行权限状态”单接口，这里按主体批量查询：
        角色（19 个一次）、部门/岗位（约 184 个一次）、用户（分批，每批 500）。
        """
        key = (str(table_id or ""), str(applicant_fb_user or ""))
        now = time.time()
        cached = self._row_permission_cache.get(key)
        if cached and now - cached[0] < self.ROW_PERMISSION_TTL:
            return cached[1]
        result = self._row_permission_status(key[0], key[1])
        self._row_permission_cache[key] = (now, result)
        return result

    def _row_permission_status(self, table_id: str,
                               applicant_fb_user: str) -> Dict[str, Any]:
        finebi = self._finebi_client()
        if finebi is None or not table_id:
            return {"known": False, "table_id": table_id}
        table_row = self._table_row(table_id)
        result: Dict[str, Any] = {
            "known": True,
            "table_id": table_id,
            "table_name": str(table_row.get("name") or table_id),
            "configured": False,
            "counts": {"role": 0, "department": 0, "user": 0},
            "subjects": {"roles": [], "departments": [], "user_count": 0},
            "applicant_has_rule": False,
            "checked_at": now_iso(),
        }
        try:
            platform = self._platform_client()
            roles = [r.get("name") for r in collect_roles(platform)
                     if r.get("name")] if platform is not None else []
            if roles and hasattr(finebi, "get_row_filters_roles"):
                values = self._first_batch_data(
                    finebi.get_row_filters_roles(roles, table_id))
                hits = [roles[i] for i, value in enumerate(values)
                        if i < len(roles) and self._rule_present(value)]
                result["counts"]["role"] = len(hits)
                result["subjects"]["roles"] = hits[:self.SUBJECT_NAMES_LIMIT]

            subjects = self._department_subjects()
            if subjects and hasattr(finebi, "get_row_filters_deposts"):
                values = self._first_batch_data(
                    finebi.get_row_filters_deposts(subjects, table_id))
                hits = [subjects[i]["name"] for i, value in enumerate(values)
                        if i < len(subjects) and self._rule_present(value)]
                result["counts"]["department"] = len(hits)
                result["subjects"]["departments"] = hits[:self.SUBJECT_NAMES_LIMIT]

            users = self._list_usernames(self.USER_SCAN_LIMIT)
            if users and hasattr(finebi, "get_row_filters_users"):
                user_hits = 0
                for chunk in self._chunks(users, 500):
                    values = self._first_batch_data(
                        finebi.get_row_filters_users(chunk, table_id))
                    user_hits += sum(1 for value in values
                                     if self._rule_present(value))
                result["counts"]["user"] = user_hits
                result["subjects"]["user_count"] = user_hits

            if applicant_fb_user and hasattr(finebi, "get_row_filter"):
                values = self._first_batch_data(
                    finebi.get_row_filter(applicant_fb_user, table_id))
                result["applicant_has_rule"] = bool(
                    values and self._rule_present(values[0]))
            result["configured"] = sum(result["counts"].values()) > 0
        except Exception as exc:  # noqa: BLE001 - 检测失败不影响审批主流程
            LOGGER.warning("行权限检测失败：%s", table_id, exc_info=True)
            return {"known": False, "table_id": table_id,
                    "error": str(exc)[:200]}
        return result

    def entity_permissions(self, membership_type: str,
                           targets: List[str]) -> Dict[str, Any]:
        """角色/部门当前拥有的权限摘要（辅助成员关系审批）。"""
        clean = [str(t) for t in (targets or []) if str(t)]
        key = (str(membership_type or ""), tuple(clean))
        now = time.time()
        cached = self._entity_permission_cache.get(key)
        if cached and now - cached[0] < self.ENTITY_PERMISSION_TTL:
            return cached[1]
        result = self._entity_permissions(str(membership_type or ""), clean)
        self._entity_permission_cache[key] = (now, result)
        return result

    @staticmethod
    def _flag_counts(values: List[Any], field: str = "usePrivilege") -> int:
        return sum(1 for item in values
                   if isinstance(item, dict) and item.get(field))

    def _entity_permissions(self, membership_type: str,
                            targets: List[str]) -> Dict[str, Any]:
        if membership_type not in ("role", "department") or not targets:
            return {"known": False}
        finebi = self._finebi_client()
        platform = self._platform_client()
        if finebi is None or platform is None:
            return {"known": False}
        target = targets[0]
        rows = self._catalog_rows()
        folders = [r for r in rows if r.get("resource_type") == "folder"
                   and r.get("resource_id")]
        tables = [r for r in rows if r.get("resource_type") == "table"
                  and r.get("resource_id")]
        dashboards = [r for r in rows if r.get("resource_type") == "dashboard"
                      and r.get("resource_id")]
        entry_ids = [str(r.get("entry_id")) for r in dashboards if r.get("entry_id")]
        folder_ids = [str(r["resource_id"]) for r in folders]
        table_ids = [str(r["resource_id"]) for r in tables]
        dash_ids = [str(r["resource_id"]) for r in dashboards]
        warnings: List[str] = []
        ok_calls = 0

        def safe(call, default=None):
            nonlocal ok_calls
            try:
                result = call()
                ok_calls += 1
                return result
            except Exception as exc:  # noqa: BLE001 - 单个维度失败不影响其他维度
                text = str(exc)
                if "Role permission authentication is not enabled" not in text:
                    LOGGER.warning("权限摘要查询失败：%s", text[:200])
                warnings.append(text[:160])
                return default

        if membership_type == "role":
            entity_name = target
            folder_resp = safe(
                lambda: finebi.get_folder_permissions_role(target, folder_ids), {})
            table_resp = safe(
                lambda: finebi.get_table_permissions_role(target, table_ids), {})
            row_resp = safe(
                lambda: finebi.get_row_filters_role(target, table_ids), {})
            dash_resp = safe(
                lambda: finebi.get_dashboard_auth_role(target, dash_ids))
            entry_resp = safe(
                lambda: platform.query_role_entries(target, entry_ids))
        else:
            department_id = self._department_id_for_target(target)
            try:
                parts = json.loads(target)
                entity_name = "/".join(str(p) for p in parts)
            except (TypeError, ValueError):
                entity_name = target
                department_id = department_id or ""
            if not department_id:
                return {"known": False, "entity_type": membership_type,
                        "entity": entity_name,
                        "error": "未找到对应部门（目录快照可能未刷新）"}
            folder_resp = safe(
                lambda: finebi.get_folder_permissions_depost(
                    department_id, "", folder_ids), {})
            table_resp = safe(
                lambda: finebi.get_table_permissions_depost(
                    department_id, "", table_ids), {})
            row_resp = safe(
                lambda: finebi.get_row_filters_depost(
                    department_id, "", table_ids), {})
            dash_resp = safe(
                lambda: finebi.get_dashboard_auth_depost(
                    department_id, "", dash_ids))
            entry_resp = safe(
                lambda: platform.query_depost_entries(
                    department_id, "", entry_ids))

        if ok_calls == 0:
            return {"known": False, "entity_type": membership_type,
                    "entity": entity_name, "error": "；".join(warnings)[:300]
                    or "权限查询接口不可用"}

        folder_data = self._first_batch_data(folder_resp or {})
        table_data = self._first_batch_data(table_resp or {})
        row_data = self._first_batch_data(row_resp or {})
        dash_data = self._first_batch_data(dash_resp or {})

        def names_for(items: List[Dict[str, Any]], data: List[Any],
                      flag: str = "usePrivilege") -> List[str]:
            names = []
            for index, value in enumerate(data):
                if index >= len(items):
                    break
                if isinstance(value, dict) and value.get(flag):
                    names.append(str(items[index].get("name")
                                     or items[index].get("resource_id")))
            return names[:self.SUBJECT_NAMES_LIMIT]

        folder_use = names_for(folders, folder_data, "usePrivilege")
        table_use = names_for(tables, table_data, "usePrivilege")
        row_hits = [str(tables[i].get("name") or tables[i].get("resource_id"))
                    for i, value in enumerate(row_data)
                    if i < len(tables) and self._rule_present(value)]
        dash_view = []
        dash_export = 0
        for index, value in enumerate(dash_data):
            if index >= len(dashboards) or not isinstance(value, dict):
                continue
            name = str(dashboards[index].get("name")
                       or dashboards[index].get("resource_id"))
            if value.get("view"):
                dash_view.append(name)
            if value.get("export"):
                dash_export += 1
        entry_data = (entry_resp or {}).get("data") or {}
        entries = entry_data.get("entry") if isinstance(entry_data, dict) else []
        entries = entries or []
        entry_view = sum(1 for e in entries
                         if isinstance(e, dict)
                         and (e.get("authority") or {}).get("viewPrivilege"))
        entry_export = sum(1 for e in entries
                           if isinstance(e, dict)
                           and (e.get("authority") or {}).get("export"))
        entry_edit = sum(1 for e in entries
                         if isinstance(e, dict)
                         and (e.get("authority") or {}).get("editPrivilege"))

        summary = {
            "folders": {
                "count": sum(1 for v in folder_data
                             if isinstance(v, dict)
                             and any(v.get(k) for k in
                                     ("usePrivilege", "managePrivilege",
                                      "empowerPrivilege", "biData", "biView"))),
                "use": len(folder_use),
                "names": folder_use,
            },
            "tables": {
                "count": sum(1 for v in table_data
                             if isinstance(v, dict)
                             and any(v.get(k) for k in
                                     ("usePrivilege", "managePrivilege",
                                      "empowerPrivilege", "biData", "biView"))),
                "use": len(table_use),
                "component": self._flag_counts(table_data, "biData"),
                "names": table_use,
            },
            "rows": {"count": len(row_hits),
                     "names": row_hits[:self.SUBJECT_NAMES_LIMIT]},
            "dashboards": {"count": len(dash_view),
                           "view": len(dash_view),
                           "export": dash_export,
                           "available": dash_resp is not None,
                           "names": dash_view[:self.SUBJECT_NAMES_LIMIT]},
            "entries": {"count": len(entries),
                        "view": entry_view,
                        "export": entry_export,
                        "edit": entry_edit,
                        "available": entry_resp is not None},
        }
        return {"known": True, "entity_type": membership_type,
                "entity": entity_name, "summary": summary,
                "warnings": warnings[:5], "checked_at": now_iso()}

    def set_approver_scope(self, request_id: str, user_id: str,
                           row_enabled: bool = False, row_field: str = "",
                           row_operator: str = "strIn",
                           row_values: Optional[List[str]] = None,
                           field_ids: Optional[List[str]] = None,
                           scope_table_id: str = "") -> Dict[str, Any]:
        """审批人补充行/列权限（公共数据集或仪表板连带组件数据集）。

        - 公共数据集：写入 payload 顶层 data_scope/field_ids；
        - 仪表板：按 scope_table_id 写入 payload.component_scopes[table_id]，
          授权时先授组件数据权限，再执行该数据集的行/列权限。
        """
        req = self._require_pending(request_id)
        step = self._current_step(req)
        if not self.can_approve(user_id, step):
            raise WebApprovalError("当前用户不是该节点审批人")
        payload = req["payload"]
        category = str(req.get("category") or "")
        if category == "public_data":
            if payload.get("resource_type") != "table":
                raise WebApprovalError("只有公共数据集申请可以补充行/列权限")
            table_id = str(payload.get("resource_id") or "")
            component_scope = False
        elif category == "dashboard":
            deps = payload.get("component_datasets") or []
            allowed = {str((dep or {}).get("resource_id") or "")
                       for dep in deps if isinstance(dep, dict)}
            table_id = str(scope_table_id or "").strip()
            if not table_id or table_id not in allowed:
                raise WebApprovalError("请选择要补充权限的组件数据集")
            if not self._table_row(table_id):
                raise WebApprovalError("该组件数据集不在公共数据目录，无需配置行/列权限")
            component_scope = True
        else:
            raise WebApprovalError("该申请类型不支持补充行/列权限")
        fields = self.table_fields(table_id)
        valid_fields = {str(f["field_id"]) for f in fields}
        clean_field_ids: List[str] = []
        for field_id in field_ids or []:
            text = str(field_id or "")
            if text and text not in clean_field_ids:
                if text not in valid_fields:
                    raise WebApprovalError("列权限字段不存在：%s" % text)
                clean_field_ids.append(text)

        values = [str(v).strip() for v in (row_values or []) if str(v).strip()]
        operator = str(row_operator or "strIn")
        if operator not in ("strIn", "strNotIn"):
            raise WebApprovalError("行权限条件类型不支持：%s" % operator)
        data_scope: Dict[str, Any] = {}
        if row_enabled:
            field_id = str(row_field or "")
            if field_id not in valid_fields:
                raise WebApprovalError("行权限字段不存在：%s" % field_id)
            if not values:
                raise WebApprovalError("行权限至少填写一个值")
            data_scope = {"rules": [{"type": operator, "fieldId": field_id,
                                     "filterValue": values}]}

        scope = {"row_enabled": bool(row_enabled),
                 "data_scope": data_scope,
                 "field_ids": clean_field_ids,
                 "configured_by": user_id,
                 "updated_at": now_iso()}
        if component_scope:
            scopes = dict(payload.get("component_scopes") or {})
            scopes[table_id] = scope
            payload["component_scopes"] = scopes
            payload["permission_content"] = self._permission_content(
                "dashboard", payload)
        else:
            payload["row_enabled"] = bool(row_enabled)
            payload["data_scope"] = data_scope
            payload["field_ids"] = clean_field_ids
            payload["scope_configured_by"] = user_id
            payload["scope_updated_at"] = now_iso()
            payload["permission_content"] = self._permission_content(
                "public_data", payload)
        self.storage.conn.execute(
            "UPDATE web_requests SET payload=?, updated_at=? WHERE id=?",
            (_json(payload), now_iso(), request_id))
        self.storage.conn.commit()
        self.storage.log("INFO", "approver_scope", "审批人补充行/列权限", {
            "request_id": request_id, "user_id": user_id,
            "scope_table_id": table_id if component_scope else "",
            "row_enabled": bool(row_enabled), "row_field": row_field,
            "row_operator": operator,
            "row_values": len(values), "field_ids": len(clean_field_ids)})
        return self.get_request(request_id) or {}

    MEMBERSHIP_SNAPSHOT_HOURS = 12

    @staticmethod
    def _snapshot_fresh(updated_at: str, hours: int) -> bool:
        try:
            dt = datetime.fromisoformat(str(updated_at))
        except (TypeError, ValueError):
            return False
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return (datetime.now().astimezone() - dt).total_seconds() < hours * 3600

    def user_membership(self, user_id: str, refresh: bool = True) -> Dict[str, Any]:
        """当前用户已加入的角色/部门（本地快照优先，缺失/过期再实时读一次）。"""
        user = self.get_user(user_id)
        fb_user = str((user or {}).get("fb_user") or "")
        snap = self.storage.get_user_membership(user_id)
        if snap and self._snapshot_fresh(snap.get("updated_at", ""),
                                         self.MEMBERSHIP_SNAPSHOT_HOURS):
            return {"known": True, "roles": snap["roles"],
                    "departments": snap["departments"],
                    "updated_at": snap["updated_at"]}
        if not refresh or not fb_user or not self.platform:
            if snap:
                return {"known": True, "roles": snap["roles"],
                        "departments": snap["departments"],
                        "updated_at": snap["updated_at"], "stale": True}
            return {"known": False}
        try:
            from ..services.grant import user_departments, user_roles
            resp = self.platform.query_user_detail(username=fb_user)
            roles = user_roles(resp, fb_user)
            departments = user_departments(resp, fb_user)
            self.storage.save_user_membership(user_id, fb_user, roles, departments)
        except Exception:  # noqa: BLE001 - 提示失败不影响申请
            LOGGER.warning("读取用户角色/部门失败：%s", user_id, exc_info=True)
            if snap:
                return {"known": True, "roles": snap["roles"],
                        "departments": snap["departments"],
                        "updated_at": snap["updated_at"], "stale": True}
            return {"known": False}
        snap = self.storage.get_user_membership(user_id) or {}
        return {"known": True, "roles": snap.get("roles") or [],
                "departments": snap.get("departments") or [],
                "updated_at": snap.get("updated_at", "")}

    def refresh_all_memberships(self, sleep_seconds: float = 0.05) -> Dict[str, Any]:
        """定时任务：把所有本地映射用户的角色/部门刷新到快照表。"""
        if not self.platform:
            return {"ok": False, "error": "未配置 FineBI 平台客户端"}
        from ..services.grant import user_departments, user_roles
        rows = self.storage.conn.execute(
            "SELECT id,fb_user FROM web_users WHERE active=1 AND fb_user<>'' "
            "AND id NOT LIKE 'admin:%'").fetchall()
        ok = 0
        errors: List[Dict[str, str]] = []
        for row in rows:
            user_id = str(row["id"])
            fb_user = str(row["fb_user"])
            try:
                resp = self.platform.query_user_detail(username=fb_user)
                self.storage.save_user_membership(
                    user_id, fb_user, user_roles(resp, fb_user),
                    user_departments(resp, fb_user))
                ok += 1
            except Exception as exc:  # noqa: BLE001
                errors.append({"user": fb_user, "error": str(exc)[:200]})
            if sleep_seconds:
                time.sleep(sleep_seconds)
        return {"ok": not errors, "total": len(rows), "synced": ok,
                "errors": errors[:20]}

    def create_request(self, applicant_id: str, payload: Dict[str, Any],
                       category: str = "") -> Dict[str, Any]:
        applicant = self.get_user(applicant_id)
        if not applicant:
            raise WebApprovalError("申请人不存在")
        category = category or self._infer_category(payload)
        item = self._normalize_payload(category, payload)
        # 单据编号：日期(YYYYMMDD) + 当日两位全局流水
        day = datetime.now().astimezone().strftime("%Y-%m-%d")
        serial = self.storage.next_request_serial(day)
        item["request_date"] = day
        item["serial"] = serial
        item["serial_text"] = ("%02d" % serial) if serial <= 99 else str(serial)
        item["request_no"] = day.replace("-", "") + "-" + item["serial_text"]
        item["applicant_account"] = self._applicant_account(applicant)
        item["permission_content"] = self._permission_content(category, item)
        item["permission_time"] = self._permission_time(item)
        risk = self._risk(category, item)
        # 审批链：数据 Owner → 业务 Owner；先算审批人，找不到时不落无人可批的单
        steps = self._build_steps(applicant_id, item)
        rid = new_id("wreq")
        ts = now_iso()
        self.storage.conn.execute(
            "INSERT INTO web_requests(id,applicant_id,status,risk,category,period_type,payload,"
            "current_seq,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (rid, applicant_id, "pending", risk, category, item["period_type"],
             _json(item), 0, ts, ts))
        for step in steps:
            self.storage.conn.execute(
                "INSERT INTO web_steps(id,request_id,seq,role,approver_id,action) "
                "VALUES(?,?,?,?,?,?)",
                (new_id("wstep"), rid, step["seq"], step["role"],
                 step["approver_id"], "pending"))
        self.storage.conn.commit()
        self._sync_bitable(rid, "提交申请")
        self._notify_next(rid)
        return self.get_request(rid) or {}

    @staticmethod
    def _infer_category(payload: Dict[str, Any]) -> str:
        rt = str(payload.get("resource_type") or "")
        if rt in ("role", "department"):
            return "membership"
        if rt in ("dashboard_view", "dashboard_export", "dashboard", "dashboard_edit",
                  "dashboard_entry"):
            return "dashboard"
        if rt == "schedule":
            return "admin"
        return "public_data"

    def _normalize_payload(self, category: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if category == "dashboard":
            return self._normalize_dashboard(payload)
        if category == "admin":
            return self._normalize_schedule(payload)
        if category == "membership":
            return self._normalize_membership(payload)
        return self._normalize_public(payload)

    @staticmethod
    def _period(payload: Dict[str, Any]) -> Dict[str, Any]:
        period_type = str(payload.get("period_type") or "temp").lower()
        if period_type not in ("long", "temp"):
            raise WebApprovalError("申请周期不合法")
        try:
            days = int(payload.get("days") or 90)
        except (TypeError, ValueError):
            raise WebApprovalError("期限必须是整数天")
        if period_type == "long":
            days = LONG_TERM_DAYS
        elif days <= 0 or days > 365:
            raise WebApprovalError("临时期限必须为 1~365 天")
        return {"period_type": period_type, "days": days}

    def _lineage_public_ancestors(self, dataset_id: str,
                                  depth: int = 0) -> List[Dict[str, str]]:
        """沿 FineBI 血缘 fatherTables 向上找公共数据集祖先。"""
        rid = str(dataset_id or "")
        if not rid or depth > 6:
            return []
        cached = self._lineage_cache.get(rid)
        if cached is not None:
            return [dict(item) for item in cached]
        finebi = self._finebi_client()
        if finebi is None or not hasattr(finebi, "get_table_usage"):
            return []
        result: List[Dict[str, str]] = []
        seen = set()
        try:
            resp = finebi.get_table_usage([rid])
            data = (resp or {}).get("data") or []
            node = (data[0].get("data") if data and isinstance(data[0], dict)
                    else {})
            fathers = node.get("fatherTables") if isinstance(node, dict) else []
            for father in fathers or []:
                if not isinstance(father, dict):
                    continue
                fid = str(father.get("tableName") or "")
                if not fid or fid in seen:
                    continue
                seen.add(fid)
                row = self._table_row(fid)
                if row:
                    result.append({"resource_id": fid,
                                   "name": str(row.get("name")
                                               or father.get("transferName")
                                               or fid),
                                   "path": str(row.get("path") or "")})
                else:
                    result.extend(self._lineage_public_ancestors(fid, depth + 1))
            if depth > 0 and not fathers:
                # 再兜底查一次该节点自身是否在目录中（部分接口只回自身）
                row = self._table_row(rid)
                if row:
                    result.append({"resource_id": rid,
                                   "name": str(row.get("name") or rid),
                                   "path": str(row.get("path") or "")})
        except Exception:  # noqa: BLE001
            LOGGER.warning("数据集血缘祖先解析失败：%s", rid, exc_info=True)
        dedup: Dict[str, Dict[str, str]] = {}
        for item in result:
            dedup.setdefault(item["resource_id"], item)
        output = sorted(dedup.values(), key=lambda x: x.get("name") or "")
        if output:
            self._lineage_cache[rid] = output
        return [dict(item) for item in output]

    def _component_dependency_sets(
            self, dashboard_ids: List[str]) -> tuple:
        """返回 (公共数据集依赖, 自助数据集依赖)，沿血缘把自助数据集映射到公共祖先。"""
        public: List[Dict[str, str]] = []
        self_service: List[Dict[str, str]] = []
        public_seen = set()
        self_seen = set()
        for dashboard_id in dashboard_ids:
            for dep in self.dashboard_dependencies(str(dashboard_id or "")):
                rid = str(dep.get("resource_id") or "")
                if not rid:
                    continue
                if self._table_row(rid):
                    if rid not in public_seen:
                        public_seen.add(rid)
                        public.append(dep)
                    continue
                if rid not in self_seen:
                    self_seen.add(rid)
                    self_service.append(dep)
                # 自助数据集本身不授权；沿 fatherTables 找公共始祖
                for ancestor in self._lineage_public_ancestors(rid):
                    aid = str(ancestor.get("resource_id") or "")
                    if aid and aid not in public_seen:
                        public_seen.add(aid)
                        public.append(ancestor)
        for items in (public, self_service):
            items.sort(key=lambda x: str(x.get("name") or ""))
        return public, self_service

    def _resolve_component_datasets(self, dashboard_ids: List[str]) -> List[Dict[str, str]]:
        """多台仪表板依赖的公共数据集取并集（组件数据随单授权，不单独建流程单）。"""
        public, _self_service = self._component_dependency_sets(dashboard_ids)
        return public

    # ---------- 资源 canonical 化 ----------
    @staticmethod
    def _reject_unknown_actions(label: str, actions: List[str],
                                allowed: set) -> None:
        """服务端动作白名单：前端不展示的 action 可能被手工 POST 注入。"""
        invalid = sorted({str(a) for a in actions or [] if str(a) not in allowed})
        if invalid:
            raise WebApprovalError("%s不支持权限项：%s" % (label, "、".join(invalid)))

    def _catalog_dashboard_row(self, resource_id: str = "",
                               entry_id: str = "") -> Optional[Dict[str, Any]]:
        rid = str(resource_id or "").strip()
        eid = str(entry_id or "").strip()
        for row in self._catalog_rows():
            if str(row.get("resource_type") or "") != "dashboard":
                continue
            if rid and str(row.get("resource_id") or "") == rid:
                return row
            if eid and str(row.get("entry_id") or "") == eid:
                return row
        return None

    def _resolve_dashboard_target(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """从目录快照反查仪表板身份，不信任前端传的 name/path/entry。"""
        rid = str(payload.get("resource_id") or "").strip()
        entry_id = str(payload.get("entry_id") or "").strip()
        row = self._catalog_dashboard_row(rid, entry_id)
        if row is None:
            if getattr(self, "strict_resource_validation", True):
                raise WebApprovalError(
                    "仪表板未在目录快照中找到（ID 无效或目录尚未刷新）")
            return {"resource_id": rid, "entry_id": entry_id,
                    "resource_path": str(payload.get("resource_path") or ""),
                    "resource_name": str(payload.get("resource_name") or rid or entry_id)}
        canonical_rid = str(row.get("resource_id") or "")
        canonical_entry = str(row.get("entry_id") or "")
        if rid and canonical_rid and rid != canonical_rid:
            raise WebApprovalError("仪表板 ID 与目录快照不一致")
        if entry_id and canonical_entry and entry_id != canonical_entry:
            raise WebApprovalError("仪表板目录 ID 与资源不匹配")
        return {
            "resource_id": canonical_rid or rid,
            "entry_id": canonical_entry,
            "resource_path": str(row.get("path") or ""),
            "resource_name": str(row.get("name") or canonical_rid or canonical_entry),
        }

    def _resolve_public_target(self, resource_type: str,
                               payload: Dict[str, Any]) -> Dict[str, str]:
        rid = str(payload.get("resource_id") or "").strip()
        for row in self._catalog_rows():
            if str(row.get("resource_type") or "") != resource_type:
                continue
            if str(row.get("resource_id") or "") != rid:
                continue
            return {"resource_id": rid,
                    "resource_path": str(row.get("path") or ""),
                    "resource_name": str(row.get("name") or rid)}
        if getattr(self, "strict_resource_validation", True):
            raise WebApprovalError(
                "数据资源未在目录快照中找到（ID 无效或目录尚未刷新）")
        return {"resource_id": rid,
                "resource_path": str(payload.get("resource_path") or ""),
                "resource_name": str(payload.get("resource_name") or rid)}

    def _schedule_items(self) -> List[Dict[str, str]]:
        """读取定时调度任务列表（带 5 分钟缓存），用于校验 task ID。"""
        platform = self.platform
        if platform is None or not hasattr(platform, "list_schedules"):
            return []
        now = time.time()
        cache = self._schedule_cache or {}
        if cache.get("at") and now - cache["at"] < 300:
            return list(cache.get("items") or [])
        items: List[Dict[str, str]] = []
        seen = set()
        page = 1
        for _ in range(20):
            resp = platform.list_schedules(page=page, per_page=50)
            data = (resp or {}).get("data")
            has_next = False
            if isinstance(data, dict):
                has_next = bool(data.get("hasNext"))
                data = (data.get("list") or data.get("items")
                        or data.get("schedules") or [])
            for item in data or []:
                if not isinstance(item, dict):
                    continue
                sid = str(item.get("id") or item.get("taskId")
                          or item.get("name") or "")
                name = str(item.get("name") or item.get("taskName") or sid)
                if sid and sid not in seen:
                    seen.add(sid)
                    items.append({"id": sid, "name": name})
            if not has_next:
                break
            page += 1
        self._schedule_cache = {"at": now, "items": items}
        return items

    def _resolve_schedule_task(self, task: str) -> Dict[str, str]:
        platform = self.platform
        if platform is None or not hasattr(platform, "list_schedules"):
            # 没有平台客户端（单测/降级）时无法校验，按传入 ID 走
            return {"id": task, "name": task}
        try:
            items = self._schedule_items()
        except Exception as exc:  # noqa: BLE001 - 无法校验时不猜 ID
            if getattr(self, "strict_resource_validation", True):
                raise WebApprovalError("无法校验定时调度任务：%s" % exc)
            items = []
        for item in items:
            if item.get("id") == task:
                return item
        if getattr(self, "strict_resource_validation", True):
            raise WebApprovalError(
                "定时调度任务未找到（可能已删除或无权限读取），请刷新后重试")
        return {"id": task, "name": task}

    def _normalize_dashboard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        permissions = [str(p) for p in payload.get("permissions") or []]
        if not permissions:
            raise WebApprovalError("请选择权限项")
        self._reject_unknown_actions("仪表板", permissions, DASHBOARD_ACTIONS)
        if "export" in permissions and "view" not in permissions:
            permissions.append("view")
        if "edit" in permissions and "view" not in permissions:
            permissions.append("view")
        if "component" in permissions and "view" not in permissions:
            permissions.append("view")
        component_requested = "component" in permissions
        period = self._period(payload)
        resource_type = str(payload.get("resource_type") or "").strip()
        if resource_type == "dashboard_folder":
            # 仪表板文件夹本身没有授权接口：选择文件夹 = 对该目录下所有仪表板一起申请
            folder_path = str(payload.get("resource_path") or "").strip("/")
            if not folder_path:
                raise WebApprovalError("请选择文件夹")
            targets = self._dashboards_under_folder(folder_path)
            if not targets:
                raise WebApprovalError("该文件夹下没有可申请的仪表板")
            folder_name = folder_path.rsplit("/", 1)[-1] + "（文件夹）"
            component_requested_now = component_requested
            public_deps, self_deps = (
                self._component_dependency_sets(
                    [str(t.get("resource_id") or "") for t in targets])
                if component_requested_now else ([], []))
            component_datasets = public_deps
            if component_requested_now and not component_datasets:
                permissions = [p for p in permissions if p != "component"]
            return {
                "resource_type": "dashboard_folder",
                "resource_id": folder_path,
                "resource_path": folder_path,
                "resource_name": folder_name,
                "targets": targets,
                "permissions": permissions,
                "edit_requested": "edit" in permissions,
                "component_requested": bool(component_datasets),
                "component_datasets": component_datasets,
                "component_self_service": self_deps,
                "component_skipped_reason": (
                    ("依赖均为自助数据集，无需组件数据权限"
                     if self_deps else "未匹配到依赖数据集")
                    if component_requested_now and not component_datasets else ""),
                "reason": str(payload.get("reason") or ""),
                **period,
            }
        rid = str(payload.get("resource_id") or "").strip()
        entry_id = str(payload.get("entry_id") or "").strip()
        if not rid and not entry_id:
            raise WebApprovalError("请选择仪表板")
        target = self._resolve_dashboard_target(payload)
        rid = target["resource_id"]
        entry_id = target["entry_id"]
        component_requested_now = component_requested
        public_deps, self_deps = (
            self._component_dependency_sets([rid])
            if component_requested_now else ([], []))
        component_datasets = public_deps
        if component_requested_now and not component_datasets:
            permissions = [p for p in permissions if p != "component"]
        return {
            "resource_type": "dashboard_export" if "export" in permissions else "dashboard_view",
            "resource_id": rid,
            "entry_id": entry_id,
            "resource_path": target["resource_path"],
            "resource_name": target["resource_name"],
            "permissions": permissions,
            "edit_requested": "edit" in permissions,
            "component_requested": bool(component_datasets),
            "component_datasets": component_datasets,
            "component_self_service": self_deps,
            "component_skipped_reason": (
                ("依赖均为自助数据集，无需组件数据权限"
                 if self_deps else "未匹配到依赖数据集")
                if component_requested_now and not component_datasets else ""),
            "reason": str(payload.get("reason") or ""),
            **period,
        }

    def _dashboards_under_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """目录下所有可授权仪表板（含子目录），用于“选文件夹 = 批量申请”。"""
        folder_path = str(folder_path or "").strip("/")
        prefix = folder_path + "/"
        targets: List[Dict[str, Any]] = []
        seen: set = set()
        for row in self._catalog_rows():
            if row.get("resource_type") != "dashboard":
                continue
            path = str(row.get("path") or "").strip("/")
            if path != folder_path and not path.startswith(prefix):
                continue
            rid = str(row.get("resource_id") or "")
            entry_id = str(row.get("entry_id") or "")
            if not rid and not entry_id:
                continue
            key = (rid, entry_id)
            if key in seen:
                continue
            seen.add(key)
            targets.append({"resource_id": rid, "entry_id": entry_id,
                            "resource_path": path,
                            "resource_name": str(row.get("name") or path)})
        targets.sort(key=lambda item: item["resource_path"])
        return targets

    def _normalize_public(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        rt = str(payload.get("resource_type") or "").strip()
        if rt not in (ResourceType.FOLDER, ResourceType.TABLE):
            raise WebApprovalError("公共数据权限只支持文件夹/数据集")
        rid = str(payload.get("resource_id") or "").strip()
        if not rid:
            raise WebApprovalError("请选择数据资源")
        actions = [str(a) for a in payload.get("permissions") or payload.get("actions") or []]
        if not actions:
            raise WebApprovalError("请选择权限项")
        self._reject_unknown_actions("公共数据", actions, PUBLIC_DATA_ACTIONS)
        target = self._resolve_public_target(rt, payload)
        period = self._period(payload)
        data_scope: Dict[str, Any] = {}
        row_enabled = bool(payload.get("row_enabled"))
        if row_enabled:
            field_id = str(payload.get("row_field") or "").strip()
            values = [str(v).strip() for v in payload.get("row_values") or []
                      if str(v).strip()]
            operator = str(payload.get("row_operator") or "strIn")
            if operator not in ("strIn", "strNotIn"):
                raise WebApprovalError("行权限条件类型不支持：%s" % operator)
            if not field_id or not values:
                raise WebApprovalError("行权限需要选择字段并填写至少一个值")
            valid_fields = {str(f["field_id"]) for f in
                            self.table_fields(target["resource_id"])}
            if valid_fields and field_id not in valid_fields:
                raise WebApprovalError("行权限字段不存在：%s" % field_id)
            data_scope = {"rules": [{"type": operator, "fieldId": field_id,
                                     "filterValue": values}]}
        return {
            "resource_type": rt, "resource_id": target["resource_id"],
            "resource_path": target["resource_path"],
            "resource_name": target["resource_name"],
            "actions": actions, "row_enabled": row_enabled,
            "data_scope": data_scope,
            "reason": str(payload.get("reason") or ""),
            **period,
        }

    def _normalize_schedule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        permissions = [str(p) for p in payload.get("permissions") or ["use"]]
        if not permissions:
            raise WebApprovalError("请选择定时调度权限")
        module = str(payload.get("module") or "").strip()
        if module:
            # 平台管理模块（如数据预警 decision-management-warningcenter）必须命中白名单，
            # 避免手工 POST 任意 decision-management-* 模块。
            allowed_modules = set(ALLOWED_ADMIN_MODULES)
            for extra in ((self.policy.get("web_approval") or {})
                          .get("allowed_admin_modules") or []):
                text = str(extra or "").strip()
                if text:
                    allowed_modules.add(text)
            if module not in allowed_modules:
                raise WebApprovalError("不支持的管理模块：%s" % module)
            self._reject_unknown_actions("管理模块", permissions, MODULE_ACTIONS)
            period = self._period(payload)
            return {
                "resource_type": "platform_module", "resource_id": module,
                "resource_name": MODULE_LABELS.get(module) or module,
                "module": module, "permissions": permissions,
                "reason": str(payload.get("reason") or ""),
                **period,
            }
        task = str(payload.get("schedule_task") or "").strip()
        self._reject_unknown_actions("定时调度", permissions, SCHEDULE_ACTIONS)
        if any(p in ("manage", "empower") for p in permissions) and not task:
            raise WebApprovalError("管理/授权权限需要选择定时调度任务")
        period = self._period(payload)
        if task:
            resolved = self._resolve_schedule_task(task)
            rid = resolved["id"]
            name = resolved.get("name") or task
        else:
            rid = "decision-management-schedule"
            name = "定时调度（功能权限）"
        return {
            "resource_type": "schedule", "resource_id": rid,
            "resource_name": name, "schedule_task": task,
            "permissions": permissions,
            "reason": str(payload.get("reason") or ""),
            **period,
        }

    def _normalize_membership(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """申请加入已有角色/部门（分配成员关系，不是给角色/部门授数据权限）。"""
        membership_type = str(payload.get("membership_type") or "").strip().lower()
        if membership_type not in ("role", "department"):
            raise WebApprovalError("请选择申请类型（角色 / 部门）")
        raw_targets = payload.get("targets") or payload.get("target") or []
        if isinstance(raw_targets, str):
            raw_targets = [raw_targets]
        targets: List[str] = []
        for raw in raw_targets:
            if membership_type == "role":
                name = str(raw or "").strip()
                if name and name not in targets:
                    targets.append(name)
                continue
            path: Any = raw
            if isinstance(raw, str):
                try:
                    path = json.loads(raw)
                except (TypeError, ValueError):
                    path = [raw]
            if not isinstance(path, list):
                path = [str(path)]
            clean = [str(part).strip() for part in path if str(part).strip()]
            if not clean:
                continue
            key = json.dumps(clean, ensure_ascii=False)
            if key not in targets:
                targets.append(key)
        if not targets:
            raise WebApprovalError("请选择要加入的角色" if membership_type == "role"
                                   else "请选择要加入的部门")
        period = self._period(payload)
        if membership_type == "role":
            resource_name = "角色：" + "、".join(targets)
        else:
            labels = []
            for key in targets:
                try:
                    labels.append("/".join(json.loads(key)))
                except (TypeError, ValueError):
                    labels.append(key)
            resource_name = "部门：" + "、".join(labels)
        payload = {
            "resource_type": membership_type,
            "resource_id": targets[0],
            "targets": targets,
            "membership_type": membership_type,
            "resource_name": resource_name,
            "reason": str(payload.get("reason") or ""),
            **period,
        }
        return payload

    def membership_permissions(self, request_id: str) -> Dict[str, Any]:
        """成员关系申请的角色/部门权限摘要（详情页异步读取，不阻塞申请提交）。"""
        req = self.get_request(request_id)
        if not req or req.get("category") != "membership":
            return {"known": False}
        payload = req.get("payload") or {}
        membership_type = str(payload.get("membership_type") or "")
        targets = [str(t) for t in (payload.get("targets")
                                    or [payload.get("resource_id")]) if str(t)]
        return self.entity_permissions(membership_type, targets)

    @staticmethod
    def _risk(category: str, item: Dict[str, Any]) -> str:
        if category == "admin":
            return "high"
        if category == "membership":
            # 角色通常自带模块/数据权限，风险高于部门成员关系
            return "high" if item.get("membership_type") == "role" else "medium"
        actions = set(item.get("permissions") or item.get("actions") or [])
        if item.get("period_type") == "long" or actions & HIGH_ACTIONS:
            return "high"
        if actions & MEDIUM_ACTIONS or item.get("days", 0) > 90:
            return "medium"
        return "low"

    # ---------- 查询 ----------
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        row = self.storage.conn.execute(
            "SELECT * FROM web_requests WHERE id=?", (request_id,)).fetchone()
        if not row:
            return None
        req = dict(row)
        req["payload"] = json.loads(req["payload"])
        req["result"] = json.loads(req["result"]) if req.get("result") else None
        req["applicant"] = self.get_user(req["applicant_id"])
        req["steps"] = self.get_steps(request_id)
        for step in req["steps"]:
            step["approver"] = self.get_user(str(step.get("approver_id") or ""))
        req["comments"] = self.get_comments(request_id)
        req["current_step"] = req["steps"][req["current_seq"]] if req["steps"] else None
        req["current_approver"] = None
        if req["current_step"]:
            req["current_approver"] = self.get_user(req["current_step"]["approver_id"])
        return req

    def get_steps(self, request_id: str) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM web_steps WHERE request_id=? ORDER BY seq", (request_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_comments(self, request_id: str) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM web_comments WHERE request_id=? ORDER BY created_at",
            (request_id,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["user"] = self.get_user(item["user_id"])
            result.append(item)
        return result

    def my_requests(self, user_id: str) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM web_requests WHERE applicant_id=? ORDER BY created_at DESC",
            (user_id,)).fetchall()
        return [self.get_request(r["id"]) for r in rows]

    def inbox(self, user_id: str) -> List[Dict[str, Any]]:
        ids = self.identities(user_id)
        marks = ",".join("?" for _ in ids)
        rows = self.storage.conn.execute(
            "SELECT r.* FROM web_requests r JOIN web_steps s ON s.request_id=r.id "
            "WHERE r.status='pending' AND s.action='pending' AND s.approver_id IN (%s) "
            "ORDER BY r.created_at DESC" % marks, ids).fetchall()
        return [self.get_request(r["id"]) for r in rows]

    def my_approvals(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        pending = self.inbox(user_id)
        ids = self.identities(user_id)
        marks = ",".join("?" for _ in ids)
        rows = self.storage.conn.execute(
            "SELECT r.* FROM web_requests r JOIN web_steps s ON s.request_id=r.id "
            "WHERE s.approver_id IN (%s) AND s.action IN ('approved','rejected') "
            "ORDER BY s.acted_at DESC" % marks, ids).fetchall()
        seen = set()
        done = []
        for row in rows:
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            done.append(self.get_request(row["id"]))
        return {"pending": pending, "done": done}

    # ---------- 审批动作 ----------
    def approve(self, request_id: str, user_id: str, comment: str = "") -> Dict[str, Any]:
        req = self._require_pending(request_id)
        step = self._current_step(req)
        if not self.can_approve(user_id, step):
            raise WebApprovalError("当前用户不是该节点审批人")
        # CAS：同一节点只允许第一个请求生效，防并发/重复提交导致重复授权
        if not self._act(step["id"], "approved", comment):
            raise WebApprovalError("该审批节点已被处理，请刷新后重试")
        next_seq = req["current_seq"] + 1
        if next_seq >= len(req["steps"]):
            if self._set_status(request_id, "approved", expect="pending"):
                self._execute(request_id)
        else:
            self.storage.conn.execute(
                "UPDATE web_requests SET current_seq=?, updated_at=? WHERE id=?",
                (next_seq, now_iso(), request_id))
            self.storage.conn.commit()
            self._sync_bitable(request_id, "审批通过（待下一级）")
            self._notify_next(request_id)
        return self.get_request(request_id) or {}

    def reject(self, request_id: str, user_id: str, comment: str = "") -> Dict[str, Any]:
        req = self._require_pending(request_id)
        step = self._current_step(req)
        if not self.can_approve(user_id, step):
            raise WebApprovalError("当前用户不是该节点审批人")
        if not self._act(step["id"], "rejected", comment):
            raise WebApprovalError("该审批节点已被处理，请刷新后重试")
        self._set_status(request_id, "rejected", expect="pending")
        self._sync_bitable(request_id, "审批驳回")
        self._notify_applicant(request_id, "申请被驳回")
        return self.get_request(request_id) or {}

    def withdraw(self, request_id: str, user_id: str) -> Dict[str, Any]:
        req = self._require_pending(request_id)
        if req["applicant_id"] != user_id:
            raise WebApprovalError("只有申请人可以撤回")
        self._set_status(request_id, "withdrawn", expect="pending")
        self._sync_bitable(request_id, "申请人撤回")
        self._notify_applicant(request_id, "申请已撤回")
        return self.get_request(request_id) or {}

    def add_comment(self, request_id: str, user_id: str, content: str) -> None:
        content = (content or "").strip()
        if not content:
            return
        self.storage.conn.execute(
            "INSERT INTO web_comments(id,request_id,user_id,content,created_at) "
            "VALUES(?,?,?,?,?)",
            (new_id("wcmt"), request_id, user_id, content, now_iso()))
        self.storage.conn.commit()

    # ---------- 资源 Owner（数据 Owner / 业务 Owner） ----------
    DASHBOARD_OWNER_TYPES = ("dashboard_view", "dashboard_export", "dashboard_edit",
                             "dashboard_entry", "dashboard")
    OWNER_TYPES = ("data", "business")

    @staticmethod
    def _normalize_owner_type(owner_type: str) -> str:
        value = str(owner_type or "data").strip().lower()
        return value if value in ("data", "business") else "data"

    def _validate_owner_ids(self, owner_user_ids: List[str]) -> List[str]:
        ids: List[str] = []
        for raw in owner_user_ids or []:
            uid = str(raw or "").strip()
            if not uid or uid in ids:
                continue
            if not self.get_user(uid):
                raise WebApprovalError("Owner 用户不存在：%s" % uid)
            ids.append(uid)
        return ids

    def add_owner(self, resource_type: str, resource_id: str, owner_user_id: str,
                  owner_type: str = "data") -> None:
        if not self.get_user(owner_user_id):
            raise WebApprovalError("Owner 用户不存在：%s" % owner_user_id)
        owner_type = self._normalize_owner_type(owner_type)
        self.storage.conn.execute(
            "INSERT INTO resource_owners(id,resource_type,resource_id,owner_user_id,"
            "owner_type,created_at) VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(resource_type,resource_id,owner_type,owner_user_id) DO NOTHING",
            (new_id("own"), resource_type, resource_id, owner_user_id,
             owner_type, now_iso()))
        self.storage.conn.commit()

    def set_owners(self, resource_type: str, resource_id: str,
                   owner_user_ids: List[str], owner_type: str = "data") -> List[str]:
        """覆盖式设置某资源某一类 Owner（传空列表 = 清空该类）。"""
        resource_type = str(resource_type or "").strip()
        resource_id = str(resource_id or "").strip()
        owner_type = self._normalize_owner_type(owner_type)
        if not resource_type or not resource_id:
            raise WebApprovalError("资源和资源 ID 不能为空")
        ids = self._validate_owner_ids(owner_user_ids)
        conn = self.storage.conn
        conn.execute("DELETE FROM resource_owners WHERE resource_type=? AND resource_id=? "
                     "AND owner_type=?", (resource_type, resource_id, owner_type))
        for uid in ids:
            conn.execute(
                "INSERT INTO resource_owners(id,resource_type,resource_id,owner_user_id,"
                "owner_type,created_at) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(resource_type,resource_id,owner_type,owner_user_id) DO NOTHING",
                (new_id("own"), resource_type, resource_id, uid, owner_type, now_iso()))
        conn.commit()
        return ids

    def set_owner_pair(self, resource_type: str, resource_id: str,
                       data_owner_user_ids: List[str],
                       business_owner_user_ids: List[str]) -> Dict[str, List[str]]:
        """一次保存数据 Owner + 业务 Owner（各自覆盖式，空列表 = 清空该类）。"""
        data_ids = self._validate_owner_ids(data_owner_user_ids)
        business_ids = self._validate_owner_ids(business_owner_user_ids)
        resource_type = str(resource_type or "").strip()
        resource_id = str(resource_id or "").strip()
        if not resource_type or not resource_id:
            raise WebApprovalError("资源和资源 ID 不能为空")
        conn = self.storage.conn
        conn.execute("DELETE FROM resource_owners WHERE resource_type=? AND resource_id=?",
                     (resource_type, resource_id))
        for owner_type, ids in (("data", data_ids), ("business", business_ids)):
            for uid in ids:
                conn.execute(
                    "INSERT INTO resource_owners(id,resource_type,resource_id,owner_user_id,"
                    "owner_type,created_at) VALUES(?,?,?,?,?,?) "
                    "ON CONFLICT(resource_type,resource_id,owner_type,owner_user_id) "
                    "DO NOTHING",
                    (new_id("own"), resource_type, resource_id, uid, owner_type, now_iso()))
        conn.commit()
        return {"data": data_ids, "business": business_ids}

    def owners_for(self, resource_type: str, resource_id: str,
                   owner_type: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = ("SELECT owner_user_id,owner_type FROM resource_owners "
               "WHERE resource_type=? AND resource_id=?")
        params: List[Any] = [resource_type, resource_id]
        if owner_type:
            sql += " AND owner_type=?"
            params.append(self._normalize_owner_type(owner_type))
        rows = self.storage.conn.execute(sql, tuple(params)).fetchall()
        return [u for u in (self.get_user(r["owner_user_id"]) for r in rows) if u]

    def _owners_by_type_for_request(self, resource_type: str, resource_id: str = "",
                                    resource_path: str = "") -> Dict[str, List[Dict[str, Any]]]:
        """请求对应的 Owner，按类型分别继承：直接配置优先，其次逐级上级目录。"""
        result: Dict[str, List[Dict[str, Any]]] = {"data": [], "business": []}
        found: set = set()
        for rtype, rid in self._owner_lookup_keys(resource_type, resource_id, resource_path):
            rows = self.storage.conn.execute(
                "SELECT owner_user_id,owner_type FROM resource_owners "
                "WHERE resource_type=? AND resource_id=?",
                (rtype, rid)).fetchall()
            for row in rows:
                owner_type = self._normalize_owner_type(row["owner_type"])
                if owner_type in found:
                    continue
                user = self.get_user(row["owner_user_id"])
                if not user:
                    continue
                result[owner_type].append(user)
                found.add(owner_type)
        return result

    def owners_for_request(self, resource_type: str, resource_id: str = "",
                           resource_path: str = "") -> List[Dict[str, Any]]:
        """兼容接口：返回带 owner_type 的 Owner 列表（直接优先，按类型继承）。"""
        owners = self._owners_by_type_for_request(resource_type, resource_id, resource_path)
        return [{"owner_type": owner_type, "user": user}
                for owner_type in self.OWNER_TYPES for user in owners.get(owner_type, [])]

    # ---------- 角色/部门统一审批人 ----------
    MEMBERSHIP_OWNER_TYPE = "membership"
    MEMBERSHIP_OWNER_ID = "owner"

    def set_membership_owner(self, user_id: str) -> List[str]:
        """配置角色/部门申请的统一审批人（传空字符串 = 清空）。"""
        return self.set_owners(self.MEMBERSHIP_OWNER_TYPE,
                               self.MEMBERSHIP_OWNER_ID,
                               [user_id] if user_id else [], "data")

    def membership_owner(self) -> Optional[Dict[str, Any]]:
        users = self.owners_for(self.MEMBERSHIP_OWNER_TYPE,
                                self.MEMBERSHIP_OWNER_ID, "data")
        return users[0] if users else None

    # ---------- 默认审批人（无 Owner 时兜底） ----------
    DEFAULT_APPROVER_TYPE = "system"
    DEFAULT_APPROVER_ID = "default_approver"

    def set_default_approver(self, user_id: str) -> List[str]:
        """配置兜底审批人（仪表板无 Owner、角色/部门未配统一审批人时使用）。"""
        return self.set_owners(self.DEFAULT_APPROVER_TYPE, self.DEFAULT_APPROVER_ID,
                               [user_id] if user_id else [], "data")

    def default_approver(self) -> Optional[Dict[str, Any]]:
        users = self.owners_for(self.DEFAULT_APPROVER_TYPE,
                                self.DEFAULT_APPROVER_ID, "data")
        return users[0] if users else None

    def _owner_lookup_keys(self, resource_type: str, resource_id: str = "",
                           resource_path: str = "") -> List[tuple]:
        rt = str(resource_type or "").strip()
        rid = str(resource_id or "").strip()
        path = str(resource_path or "").strip("/")
        # 路径只信目录快照：客户端传的 resource_path 可用于伪造 Owner 继承。
        if rt in self.DASHBOARD_OWNER_TYPES:
            direct_type, folder_type = "dashboard", "dashboard_folder"
            row = self._catalog_dashboard_row(rid) if rid else None
            if row is None and path:
                row = self._catalog_row("dashboard", path=path)
            if row is not None:
                rid = str(row.get("resource_id") or rid)
                path = str(row.get("path") or path)
        elif rt == "table":
            direct_type, folder_type = "table", "folder"
            row = self._catalog_row("table", resource_id=rid) if rid else None
            if row is None and path:
                row = self._catalog_row("table", path=path)
            if row is not None:
                rid = str(row.get("resource_id") or rid)
                path = str(row.get("path") or path)
        elif rt == "folder":
            direct_type, folder_type = "folder", "folder"
            row = self._catalog_row("folder", resource_id=rid) if rid else None
            if row is None and path:
                row = self._catalog_row("folder", path=path)
            if row is not None:
                path = str(row.get("path") or "")
            rid = path or rid
        else:
            return [(rt, rid)] if rt and rid else []
        keys: List[tuple] = []
        if rid:
            keys.append((direct_type, rid))
        if rt in self.DASHBOARD_OWNER_TYPES and path:
            # 只有 entryId 的过期发布节点：Owner 可能按路径保存
            keys.append(("dashboard", path))
        parts = [p for p in path.split("/") if p]
        for i in range(len(parts) - 1, 0, -1):
            keys.append((folder_type, "/".join(parts[:i])))
        deduped: List[tuple] = []
        for key in keys:
            if key not in deduped:
                deduped.append(key)
        return deduped

    def _owner_names_by_key_type(self) -> Dict[str, Dict[str, List[str]]]:
        rows = self.storage.conn.execute(
            "SELECT resource_type,resource_id,owner_user_id,owner_type "
            "FROM resource_owners").fetchall()
        result: Dict[str, Dict[str, List[str]]] = {}
        for row in rows:
            user = self.get_user(row["owner_user_id"])
            if not user:
                continue
            key = "%s:%s" % (row["resource_type"], row["resource_id"])
            owner_type = self._normalize_owner_type(row["owner_type"])
            result.setdefault(key, {}).setdefault(owner_type, []).append(
                str(user.get("name") or user["id"]))
        return result

    def owner_ids_map(self) -> Dict[str, List[str]]:
        """{owner_key|owner_type: [user_id...]}，供后台弹窗预选。"""
        rows = self.storage.conn.execute(
            "SELECT resource_type,resource_id,owner_user_id,owner_type "
            "FROM resource_owners").fetchall()
        result: Dict[str, List[str]] = {}
        for row in rows:
            key = "%s:%s|%s" % (row["resource_type"], row["resource_id"],
                                self._normalize_owner_type(row["owner_type"]))
            result.setdefault(key, []).append(str(row["owner_user_id"]))
        return result

    def owner_display_map(self, category: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """树节点 Owner 展示（数据/业务分开）：直接配置优先，没有则显示继承来源。"""
        direct = self._owner_names_by_key_type()
        result: Dict[str, Dict[str, Dict[str, Any]]] = {}

        def walk(nodes: List[Dict[str, Any]], ancestors: List[Dict[str, Any]]) -> None:
            for node in nodes:
                key = str(node.get("owner_key") or "")
                entry: Dict[str, Dict[str, Any]] = {}
                for owner_type in self.OWNER_TYPES:
                    names = list((direct.get(key) or {}).get(owner_type) or [])
                    inherited_from = ""
                    if not names:
                        for ancestor in reversed(ancestors):
                            akey = str(ancestor.get("owner_key") or "")
                            inherited = (direct.get(akey) or {}).get(owner_type) or []
                            if inherited:
                                names = list(inherited)
                                inherited_from = str(ancestor.get("name") or "")
                                break
                    entry[owner_type] = {"names": names,
                                         "inherited": bool(inherited_from),
                                         "from": inherited_from}
                result[key] = entry
                if node.get("children"):
                    walk(node["children"], ancestors + [node])

        walk(self.resource_tree(category), [])
        return result

    def list_owners(self, limit: int = 500) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM resource_owners ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["owner"] = self.get_user(item["owner_user_id"])
            result.append(item)
        return result

    def _catalog_rows(self) -> List[Dict[str, Any]]:
        override = getattr(self, "catalog_rows_override", None)
        if override is not None:
            return list(override)
        path = "data/catalog.json"
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return []
        cache = getattr(self, "_catalog_cache", None) or {}
        if cache.get("mtime") == mtime:
            return cache.get("rows") or []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                rows = json.load(fh).get("rows") or []
        except (OSError, json.JSONDecodeError):
            return []
        self._catalog_cache = {"mtime": mtime, "rows": rows}
        return rows

    def _catalog_row(self, resource_type: str = "", resource_id: str = "",
                     path: str = "") -> Optional[Dict[str, Any]]:
        for row in self._catalog_rows():
            if resource_type and row.get("resource_type") != resource_type:
                continue
            if resource_id and str(row.get("resource_id") or "") != resource_id:
                continue
            if path and str(row.get("path") or "").strip("/") != path:
                continue
            return row
        return None

    def resources(self, category: str = "", limit: int = 300) -> List[Dict[str, Any]]:
        rows = self._catalog_rows()
        if category == "dashboard":
            rows = [r for r in rows if r.get("resource_type") == "dashboard"]
        elif category == "public_data":
            rows = [r for r in rows if r.get("resource_type") in ("folder", "table")]
        return rows[:limit]

    def resource_tree(self, category: str) -> List[Dict[str, Any]]:
        """把 catalog 的 path 转成可折叠树（文件夹可选中，叶子为资源）。

        每个节点带 ``path`` 与 ``owner_key``：Owner 配置按目录继承时用它作为键
        （文件夹键 = 类型:路径，叶子键 = 类型:资源ID/路径）。
        """
        rows = self.resources(category, limit=5000)
        root: List[Dict[str, Any]] = []
        index: Dict[tuple, Dict[str, Any]] = {}
        folder_owner_type = "dashboard_folder" if category == "dashboard" else "folder"
        folder_node_type = "dashboard_folder" if category == "dashboard" else "folder"

        def ensure(parts: tuple, parent: List[Dict[str, Any]]) -> Dict[str, Any]:
            node = index.get(parts)
            if node is None:
                path = "/".join(parts)
                node = {"name": parts[-1], "children": [], "resource_id": "",
                        "resource_type": folder_node_type, "path": path,
                        "owner_key": "%s:%s" % (folder_owner_type, path)}
                parent.append(node)
                index[parts] = node
            return node

        for row in rows:
            if not row.get("resource_id") and not row.get("entry_id"):
                # 既没有 biReportId 也没有 entryId 的回退条目，不放进下拉
                continue
            path = str(row.get("path") or row.get("name") or "")
            parts = tuple(p for p in path.split("/") if p)
            if not parts:
                continue
            cur = root
            prefix: tuple = ()
            for part in parts[:-1]:
                prefix = prefix + (part,)
                cur = ensure(prefix, cur)["children"]
            leaf_name = str(row.get("name") or parts[-1])
            key = prefix + (leaf_name,)
            if row.get("resource_type") == "folder":
                node = ensure(key, cur)
                node.update({"resource_id": row.get("resource_id", ""),
                             "resource_type": "folder"})
            else:
                resource_type = str(row.get("resource_type") or "")
                resource_id = str(row.get("resource_id") or "")
                leaf_path = "/".join(parts)
                if resource_type == "dashboard":
                    owner_id = resource_id or leaf_path
                    owner_key = "dashboard:%s" % owner_id
                else:
                    owner_key = "%s:%s" % (resource_type, resource_id)
                cur.append({"name": leaf_name, "children": [],
                            "resource_id": resource_id,
                            "entry_id": row.get("entry_id", ""),
                            "resource_type": resource_type,
                            "path": leaf_path,
                            "owner_key": owner_key})

        def annotate(nodes: List[Dict[str, Any]]) -> int:
            """给节点补 selectable/count：仪表板文件夹可选（批量申请其下仪表板）。"""
            total = 0
            for node in nodes:
                children = node.get("children") or []
                if children:
                    node["count"] = annotate(children)
                    node["selectable"] = bool(node.get("resource_id")) or (
                        category == "dashboard" and node["count"] > 0)
                else:
                    node["count"] = 1 if (node.get("resource_id")
                                          or node.get("entry_id")) else 0
                    node["selectable"] = bool(node.get("resource_id")
                                              or node.get("entry_id"))
                total += node["count"]
            return total

        annotate(root)

        def sort_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            nodes.sort(key=lambda n: (0 if n.get("children") else 1, n.get("name", "")))
            for n in nodes:
                sort_nodes(n.get("children") or [])
            return nodes

        return sort_nodes(root)

    # ---------- 行权限枚举 ----------
    @staticmethod
    def _default_data_dir(storage: Storage) -> str:
        db_path = getattr(storage, "db_path", "") or ""
        return (os.path.dirname(os.path.abspath(db_path)) if db_path
                else os.path.join(os.getcwd(), "data"))

    @staticmethod
    def _default_row_cache_path(storage: Storage) -> str:
        return os.path.join(WebApprovalService._default_data_dir(storage),
                            "row_value_cache.json")

    def row_values(self, table_id: str, sample_user: str = "") -> List[Dict[str, Any]]:
        """返回某数据集可用于申请的行权限字段/枚举值。

        枚举口径是「全部可选值」，不是参考用户当前已有规则的值：
        1. FineBI 行权限接口读取参考用户的现有规则（value + assist）；
        2. FineDB ``fine_pack_filter`` 合并用户规则与全部全局规则的 assist
           全量枚举；
        3. FineDB 偶发丢连接时用最近一次成功结果（本地缓存）兜底，避免
           下拉框退化成「只有该用户已有的值」；
        4. 都读不到时回退 config 的
           ``policy.web_approval.row_value_options[table_id].fields``。
        """
        api_fields = self._finebi_row_values(table_id, sample_user)
        db_fields = self._finedb_row_values(table_id, sample_user)
        if db_fields:
            self._save_row_cache(table_id, db_fields)
        else:
            db_fields = self._load_row_cache(table_id)
            if db_fields:
                LOGGER.warning("FineDB 行权限枚举读取失败，使用本地缓存：table=%s fields=%s",
                               table_id, len(db_fields))
        fields = self._merge_row_fields(api_fields, db_fields)
        if not fields:
            # FineDB 不可用/未覆盖时，从角色/部门/用户规则里收集“值列表型”枚举。
            # 动态规则（filterType=11）没有固定值，会被跳过。
            fields = self._merge_row_fields(
                self._api_row_values_full(table_id))
        if fields:
            return fields
        options = (self.policy.get("web_approval") or {}).get("row_value_options") or {}
        entry = options.get(table_id) or options.get(str(table_id)) or {}
        return entry.get("fields") or []

    def _finedb_row_values(self, table_id: str, sample_user: str = "") -> List[Dict[str, Any]]:
        if not (self.finedb and self.finedb.enabled()):
            return []
        try:
            return self.finedb.row_filter_options(table_id, sample_user) or []
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("FineDB 行权限枚举读取失败：%s", exc)
            return []

    def _load_row_cache(self, table_id: str) -> List[Dict[str, Any]]:
        with self._row_cache_lock:
            data = self._read_row_cache_file()
        entry = data.get(str(table_id)) or {}
        fields = entry.get("fields") if isinstance(entry, dict) else None
        return fields if isinstance(fields, list) else []

    def _save_row_cache(self, table_id: str, fields: List[Dict[str, Any]]) -> None:
        clean = []
        for item in fields or []:
            field_id = str(item.get("field_id") or "")
            values = sorted(str(v) for v in (item.get("values") or []) if str(v))
            if not field_id or not values:
                continue
            clean.append({"field_id": field_id,
                          "name": str(item.get("name") or field_id),
                          "values": values})
        if not clean:
            return
        with self._row_cache_lock:
            data = self._read_row_cache_file()
            data[str(table_id)] = {"updated_at": now_iso(), "fields": clean}
            tmp = self.row_cache_path + ".tmp"
            try:
                parent = os.path.dirname(os.path.abspath(self.row_cache_path))
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                os.replace(tmp, self.row_cache_path)
            except OSError as exc:
                LOGGER.warning("行权限枚举缓存写入失败：%s", exc)

    def _read_row_cache_file(self) -> Dict[str, Any]:
        try:
            with open(self.row_cache_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _merge_row_fields(*sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged: Dict[str, Dict[str, Any]] = {}
        for fields in sources:
            for item in fields or []:
                field_id = str(item.get("field_id") or "")
                if not field_id:
                    continue
                entry = merged.setdefault(field_id, {"field_id": field_id,
                                                     "name": "", "values": set()})
                name = str(item.get("name") or "")
                # FineBI 行权限接口有时不回 fieldName，上游会用字段 ID 兜底；
                # 此时优先采用 FineDB 里的中文名，别让下拉框显示一长串 ID。
                if not entry["name"] and name and name != field_id:
                    entry["name"] = name
                for value in item.get("values") or []:
                    entry["values"].add(str(value))
        return [{"field_id": k, "name": v["name"] or k, "values": sorted(v["values"])}
                for k, v in merged.items() if v["values"]]

    def _api_row_values_full(self, table_id: str) -> List[Dict[str, Any]]:
        """从角色/部门/用户的行权限规则里收集“值列表型”枚举。

        场景：数据集已配置行权限，但样例用户没有规则，FineDB 又不可用；
        例如客户用角色/部门做动态规则（filterType=11），同时个别用户配置了
        店铺编码值列表。动态规则没有固定值，跳过；只收集 strIn/strNotIn 值。
        """
        now = time.time()
        cached = self._row_values_api_cache.get(table_id)
        if cached and now - cached[0] < 300:
            return [dict(item) for item in cached[1]]
        finebi = self._finebi_client()
        platform = self._platform_client()
        if finebi is None or platform is None:
            return []
        fields: Dict[str, Dict[str, Any]] = {}

        def merge(raw: Any) -> None:
            for item in self._parse_row_rule_options(raw):
                field_id = item["field_id"]
                entry = fields.setdefault(field_id, {
                    "field_id": field_id,
                    "name": item.get("name") or field_id,
                    "values": set()})
                for value in item["values"]:
                    entry["values"].add(str(value))

        roles = [r.get("name") for r in collect_roles(platform)
                 if r.get("name")] if platform is not None else []
        if roles and hasattr(finebi, "get_row_filters_roles"):
            try:
                for raw in self._first_batch_data(
                        finebi.get_row_filters_roles(roles, table_id)):
                    merge(raw)
            except Exception:  # noqa: BLE001
                LOGGER.warning("行权限角色规则枚举失败：%s", table_id, exc_info=True)
        subjects = self._department_subjects()
        if subjects and hasattr(finebi, "get_row_filters_deposts"):
            try:
                for raw in self._first_batch_data(
                        finebi.get_row_filters_deposts(subjects, table_id)):
                    merge(raw)
            except Exception:  # noqa: BLE001
                LOGGER.warning("行权限部门规则枚举失败：%s", table_id, exc_info=True)

        if not fields:
            users = self._list_usernames()
            if users and hasattr(finebi, "get_row_filters_users"):
                for chunk in self._chunks(users, 500):
                    try:
                        for raw in self._first_batch_data(
                                finebi.get_row_filters_users(chunk, table_id)):
                            merge(raw)
                    except Exception:  # noqa: BLE001
                        LOGGER.warning("行权限用户规则枚举失败：%s", table_id,
                                       exc_info=True)
                        break
        result = [{"field_id": key, "name": value.get("name") or key,
                   "values": sorted(value["values"])}
                  for key, value in fields.items() if value["values"]]
        self._row_values_api_cache[table_id] = (now, result)
        return [dict(item) for item in result]

    def _parse_row_rule_options(self, raw: Any) -> List[Dict[str, Any]]:
        """解析单条行权限规则 JSON，返回可枚举的字段/值（跳过动态规则）。"""
        if isinstance(raw, str):
            if not raw.strip():
                return []
            try:
                raw = json.loads(raw)
            except (TypeError, json.JSONDecodeError):
                return []
        if not isinstance(raw, dict):
            return []
        output: Dict[str, Dict[str, Any]] = {}

        def walk(node: Any) -> None:
            if isinstance(node, list):
                for child in node:
                    walk(child)
                return
            if not isinstance(node, dict):
                return
            field_id = str(node.get("fieldId") or "")
            filter_type = node.get("filterType")
            try:
                type_code = int(filter_type)
            except (TypeError, ValueError):
                type_code = 0
            if field_id and type_code in (10, 12):
                value = node.get("filterValue")
                values: List[Any] = []
                assist: List[Any] = []
                if isinstance(value, dict):
                    values = list(value.get("value") or [])
                    assist = list(value.get("assist") or [])
                elif isinstance(value, list):
                    values = value
                if values or assist:
                    name = str(node.get("fieldName") or field_id)
                    name = name.rsplit(".", 1)[-1]
                    entry = output.setdefault(field_id, {
                        "field_id": field_id, "name": name, "values": set()})
                    if name and (not entry["name"] or entry["name"] == field_id):
                        entry["name"] = name
                    for item in values + assist:
                        entry["values"].add(str(item))
            children = node.get("filterValue")
            if isinstance(children, list):
                for child in children:
                    walk(child)

        walk(raw)
        return [{"field_id": key, "name": value["name"],
                 "values": sorted(value["values"])}
                for key, value in output.items() if value["values"]]

    def _finebi_row_values(self, table_id: str, sample_user: str = "") -> List[Dict[str, Any]]:
        if not self.permission or not getattr(self.permission, "finebi", None):
            return []
        user = sample_user or (self.policy.get("web_approval") or {}).get(
            "row_sample_user") or "admin"
        try:
            raw = self.permission.finebi.get_row_filter(user, table_id)
        except Exception:  # noqa: BLE001
            return []
        data = raw.get("data") if isinstance(raw, dict) else None
        if isinstance(data, list) and data:
            data = data[0].get("data") if isinstance(data[0], dict) else None
        if isinstance(data, str):
            if not data.strip():
                return []
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return []
        fields: Dict[str, Dict[str, Any]] = {}
        for node in self._row_filter_nodes(data):
            field_id = str(node.get("fieldId") or "")
            if not field_id:
                continue
            value = node.get("filterValue")
            values = value.get("value") if isinstance(value, dict) else value
            assist = value.get("assist") if isinstance(value, dict) else None
            entry = fields.setdefault(field_id, {
                "name": str(node.get("fieldName") or field_id), "values": set()})
            for item in values or []:
                entry["values"].add(str(item))
            for item in assist or []:
                entry["values"].add(str(item))
        return [{"field_id": k, "name": v["name"], "values": sorted(v["values"])}
                for k, v in fields.items() if v["values"]]

    @staticmethod
    def _row_filter_nodes(data: Any) -> List[Dict[str, Any]]:
        """兼容 FineBI 返回的两种行权限结构：单节点对象 / filterValue 节点数组。"""
        if isinstance(data, list):
            return [n for n in data if isinstance(n, dict)]
        if not isinstance(data, dict):
            return []
        if data.get("fieldId"):
            return [data]
        inner = data.get("filterValue")
        if isinstance(inner, list):
            return [n for n in inner if isinstance(n, dict)]
        return []

    # ---------- 离职交接 ----------
    def offboard(self, source_id: str, target_id: str) -> Dict[str, Any]:
        source = self.get_user(source_id)
        target = self.get_user(target_id)
        if not source or not target:
            raise WebApprovalError("源用户或目标用户不存在")
        source_fb = source.get("fb_user") or source_id
        target_fb = target.get("fb_user") or target_id
        ledgers = self.storage.active_ledger(user=source_fb)
        transferred = []
        for ledger in ledgers:
            try:
                req = self._request_from_ledger(ledger, target_fb)
                result = self.permission.grant(req)
                transferred.append({"ledger": ledger["id"], "status": result.status})
            except Exception as exc:  # noqa: BLE001
                transferred.append({"ledger": ledger["id"], "error": str(exc)})
        report: Dict[str, Any] = {"source": source_fb, "target": target_fb,
                                  "transferred": transferred}
        if self.offboard_service:
            try:
                report["offboard"] = self.offboard_service.offboard(source_fb, target_fb)
            except Exception as exc:  # noqa: BLE001
                report["offboard_error"] = str(exc)
        return report

    @staticmethod
    def _request_from_ledger(ledger: Dict[str, Any], target_user: str) -> PermissionRequest:
        payload = ledger.get("payload") or {}
        rt = ledger["resource_type"]
        if rt == ResourceType.ROW:
            return PermissionRequest(user=target_user, resource_type=rt,
                                     resource_id=ledger["resource_id"],
                                     actions=["use"],
                                     data_scope={"rules": payload.get("rules") or []},
                                     days=90, source="offboard")
        if rt in ("dashboard_view", "dashboard_export"):
            actions = ["view", "export"] if rt == "dashboard_export" else ["view"]
        elif rt == ResourceType.FIELD:
            actions = ["component"]
        elif rt == "schedule":
            actions = ["manage"]
        else:
            authority = payload.get("authority") or {}
            actions = [k for k in ("use", "manage", "empower", "component")
                       if authority.get(k + "Privilege") or authority.get(k)]
            actions = actions or ["use"]
        return PermissionRequest(user=target_user, resource_type=rt,
                                 resource_id=ledger["resource_id"],
                                 actions=actions, days=90, source="offboard")

    # ---------- 执行 ----------
    def _execute(self, request_id: str) -> None:
        req = self.get_request(request_id)
        payload = req["payload"]
        try:
            if req["category"] == "membership":
                result = self._execute_membership(req)
            elif req["category"] == "admin":
                result = self._execute_schedule(req)
            else:
                result = self._execute_permission(req)
            self.storage.conn.execute(
                "UPDATE web_requests SET status=?, result=?, updated_at=? WHERE id=?",
                ("done" if result.get("ok") else "failed", _json(result),
                 now_iso(), request_id))
            self.storage.conn.commit()
            self._sync_bitable(request_id, "授权完成" if result.get("ok") else "授权失败")
            self._notify_applicant(request_id, "审批通过，授权完成" if result.get("ok")
                                   else "审批通过，但授权失败")
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Web 审批授权失败：%s", request_id)
            self.storage.conn.execute(
                "UPDATE web_requests SET status='failed', result=?, updated_at=? WHERE id=?",
                (_json({"ok": False, "error": str(exc)}), now_iso(), request_id))
            self.storage.conn.commit()
            self._sync_bitable(request_id, "授权异常")
        finally:
            self.invalidate_permission_cache()

    def _execute_permission(self, req: Dict[str, Any]) -> Dict[str, Any]:
        if not self.permission:
            return {"ok": False, "error": "未配置授权服务"}
        payload = req["payload"]
        user = (req.get("applicant") or {}).get("fb_user") or req["applicant_id"]
        items: List[Dict[str, Any]] = []
        component_count = 0
        if req["category"] == "dashboard":
            actions = payload.get("permissions") or ["view"]
            grant_type = ("dashboard_export" if "export" in actions
                          else "dashboard_view")
            # 按用户要求：只授“该仪表板自身”的目录 entry 权限，不给父节点；
            # 有 biReportId 时同时写模板认证（view/export）。
            targets = payload.get("targets") or []
            if targets:
                # 选文件夹 = 对该目录下所有仪表板逐台授权（仍只授各自 entry）
                for target in targets:
                    if target.get("resource_id"):
                        items.append({"resource_type": grant_type,
                                      "resource_id": target["resource_id"],
                                      "actions": actions})
                    if target.get("entry_id"):
                        items.append({"resource_type": ResourceType.DASHBOARD_ENTRY,
                                      "resource_id": target["entry_id"],
                                      "actions": actions})
            else:
                if payload.get("resource_id"):
                    items.append({"resource_type": grant_type,
                                  "resource_id": payload["resource_id"],
                                  "actions": actions})
                if payload.get("entry_id"):
                    items.append({"resource_type": ResourceType.DASHBOARD_ENTRY,
                                  "resource_id": payload["entry_id"],
                                  "actions": actions})
            if not items:
                return {"ok": False,
                        "error": "该仪表板缺少 biReportId/entryId，无法授权"}
            # 组件数据：按申请单里列出的依赖数据集连带授予（只写权限、不记台账、
            # 不派生新的申请单/流程单；回收只处理仪表板权限）。
            component_datasets = payload.get("component_datasets") or []
            if not component_datasets and payload.get("component_requested"):
                dep_ids = ([str(payload.get("resource_id") or "")] if not targets
                           else [str(t.get("resource_id") or "") for t in targets])
                component_datasets = self._resolve_component_datasets(dep_ids)
            seen_deps = set()
            component_scopes = payload.get("component_scopes") or {}
            for dep in component_datasets:
                dep_rid = str((dep or {}).get("resource_id") or "")
                if not dep_rid or dep_rid in seen_deps:
                    continue
                seen_deps.add(dep_rid)
                items.append({"resource_type": ResourceType.TABLE,
                              "resource_id": dep_rid,
                              "actions": ["component"],
                              "record_ledger": False,
                              "extra": {"component_data": True}})
                scope = component_scopes.get(dep_rid) or {}
                if not isinstance(scope, dict):
                    continue
                if scope.get("row_enabled"):
                    items.append({"resource_type": ResourceType.ROW,
                                  "resource_id": dep_rid,
                                  "actions": ["use"],
                                  "data_scope": scope.get("data_scope") or {},
                                  "record_ledger": False})
                for field_id in scope.get("field_ids") or []:
                    text = str(field_id or "")
                    if text:
                        items.append({"resource_type": ResourceType.FIELD,
                                      "resource_id": text,
                                      "actions": ["component"],
                                      "record_ledger": False})
            component_count = len(seen_deps)
        else:
            items.append({"resource_type": payload["resource_type"],
                          "resource_id": payload["resource_id"],
                          "actions": payload.get("actions") or ["use"]})
            if payload.get("row_enabled"):
                items.append({"resource_type": ResourceType.ROW,
                              "resource_id": payload["resource_id"],
                              "actions": ["use"],
                              "data_scope": payload.get("data_scope") or {}})
            # 列权限：审批人补充勾选的字段（数据权限/行权限之后再授权）
            for field_id in payload.get("field_ids") or []:
                text = str(field_id or "")
                if text:
                    items.append({"resource_type": ResourceType.FIELD,
                                  "resource_id": text,
                                  "actions": ["component"]})
        row_scope = next((item.get("data_scope") for item in items
                          if item.get("resource_type") == ResourceType.ROW), {})
        request = PermissionRequest(
            user=user,
            resource_type=items[0]["resource_type"],
            resource_id=items[0]["resource_id"],
            actions=items[0]["actions"],
            data_scope=row_scope or {},
            days=payload.get("days") or 90,
            source="web:%s" % req["id"],
            extra={"long_term": payload.get("period_type") == "long"},
            items=items if len(items) > 1 else [],
        )
        result = self.permission.grant(request)
        out = {"ok": result.status in ("granted", "skipped"),
               "result": result.to_dict()}
        if req["category"] == "dashboard":
            out["component_dataset_count"] = component_count
            if payload.get("component_requested") and not component_count:
                out["component_skipped_reason"] = "未匹配到依赖数据集"
        return out

    def _execute_schedule(self, req: Dict[str, Any]) -> Dict[str, Any]:
        if not self.platform:
            return {"ok": False, "error": "未配置平台客户端"}
        payload = req["payload"]
        user = (req.get("applicant") or {}).get("fb_user") or req["applicant_id"]
        permissions = set(payload.get("permissions") or ["use"])
        module = str(payload.get("module") or "")
        if module:
            # 数据预警等平台管理模块：只写模块功能权限（use/empower），不涉及定时调度任务
            if self.dry_run or getattr(self.platform, "dry_run", False):
                return {"ok": True, "dry_run": True, "user": user,
                        "would_write": [{"module": module,
                                         "usePrivilege": "use" in permissions,
                                         "empowerPrivilege": "empower" in permissions}]}
            self.platform.set_user_platform_permission(
                user, module, use="use" in permissions,
                empower="empower" in permissions)
            ledger_ids = [self.storage.add_ledger(
                req["id"], user, "platform_module", module,
                {"permissions": sorted(permissions)},
                self._expire_at(payload["days"]))]
            return {"ok": True, "ledger_ids": ledger_ids}
        task = payload.get("schedule_task") or ""
        if self.dry_run or getattr(self.platform, "dry_run", False):
            # dry-run 与 grant 路径保持一致：只返回将要写入的内容，不写真实权限、不记台账
            would_write = []
            if "use" in permissions:
                would_write.append({"module": "decision-management-schedule",
                                    "usePrivilege": True,
                                    "empowerPrivilege": "empower" in permissions})
            if task and ({"manage", "empower"} & permissions):
                would_write.append({"scheduleTask": task,
                                    "managePrivilege": "manage" in permissions,
                                    "empowerPrivilege": "empower" in permissions})
            return {"ok": True, "dry_run": True, "user": user, "would_write": would_write}
        ledger_ids = []
        if "use" in permissions:
            self.platform.set_user_platform_permission(
                user, "decision-management-schedule", use=True,
                empower="empower" in permissions)
            ledger_ids.append(self.storage.add_ledger(
                req["id"], user, "platform_module", "decision-management-schedule",
                {"permissions": ["use"]}, self._expire_at(payload["days"])))
        if task and ({"manage", "empower"} & permissions):
            self.platform.set_user_schedule_permission(
                user, task, manage="manage" in permissions,
                empower="empower" in permissions)
            ledger_ids.append(self.storage.add_ledger(
                req["id"], user, "schedule", task,
                {"permissions": sorted(permissions)}, self._expire_at(payload["days"])))
        return {"ok": True, "ledger_ids": ledger_ids}

    def _execute_membership(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """审批通过后把用户加入已有角色/部门（只加成员关系，不授数据权限）。"""
        if not self.permission:
            return {"ok": False, "error": "未配置授权服务"}
        payload = req["payload"]
        applicant = req.get("applicant") or {}
        user = self._applicant_fb_user(applicant)
        if not user:
            return {"ok": False,
                    "error": "申请人未绑定 FineBI 账号，无法分配角色/部门；"
                             "请先在后台管理里配置 FineBI 账号"}
        membership_type = str(payload.get("membership_type") or "")
        targets = [str(t) for t in (payload.get("targets") or [payload.get("resource_id")])]
        targets = [t for t in targets if t]
        if not targets:
            return {"ok": False, "error": "申请单没有记录要加入的角色/部门"}
        if self.dry_run or getattr(self.platform, "dry_run", False):
            return {"ok": True, "dry_run": True, "user": user,
                    "would_write": [{"type": membership_type, "target": target}
                                    for target in targets]}
        items: List[Dict[str, Any]] = []
        for target in targets:
            item: Dict[str, Any] = {"resource_type": membership_type,
                                    "resource_id": target, "actions": [],
                                    "extra": {}}
            if membership_type == "role":
                item["role"] = target
            items.append(item)
        request = PermissionRequest(
            user=user,
            resource_type=membership_type,
            resource_id=targets[0],
            actions=[],
            days=payload.get("days") or 90,
            source="web:%s" % req["id"],
            extra={"long_term": payload.get("period_type") == "long",
                   "membership": True},
            items=items,
        )
        result = self.permission.grant(request)
        out: Dict[str, Any] = {"ok": result.status in ("granted", "skipped"),
                               "result": result.to_dict()}
        if not out["ok"]:
            failed = [item for item in result.item_results
                      if item.get("status") == "failed"]
            if failed:
                out["error"] = str(failed[0].get("error")
                                   or failed[0].get("reason") or "角色/部门分配失败")
        return out

    def _applicant_fb_user(self, applicant: Dict[str, Any]) -> str:
        """申请人对应的 FineBI 账号：本地映射 → FineDB 飞书映射 → 姓名/邮箱匹配。

        seed_users 会把 ``fb_user`` 缺省成 web 用户 id（占位值），因此
        ``fb_user == applicant.id`` 不能当作真实 FineBI 账号，需要再解析。
        """
        applicant_id = str(applicant.get("id") or "")
        fb_user = str(applicant.get("fb_user") or "").strip()
        if fb_user and fb_user != applicant_id:
            return fb_user
        feishu_user_id = str(applicant.get("feishu_user_id") or "").strip()
        if feishu_user_id:
            mapped = self.fb_user_for_feishu_user(feishu_user_id)
            if mapped:
                return mapped
        resolved = self.resolve_fb_user(email=str(applicant.get("email") or ""),
                                        name=str(applicant.get("name") or ""))
        if resolved:
            return resolved
        return ""

    def membership_options(self, force: bool = False) -> Dict[str, Any]:
        """可申请加入的角色/部门列表（角色名 + 部门完整路径）。

        优先读取定时刷新任务生成的 ``membership_options.json`` 快照；快照缺失或
        为空时回退实时 FineBI 接口（缓存 10 分钟）。后期新增角色/部门会在下一轮
        定时刷新后自动出现在快照里，不需要改代码或手工维护列表。
        """
        if not force:
            snapshot = self._load_membership_snapshot()
            if snapshot and (snapshot.get("roles") or snapshot.get("departments")):
                snapshot.setdefault("source", "snapshot")
                return snapshot
        cache = self._membership_cache
        now = time.time()
        if not force and cache.get("data") is not None and now - cache.get("at", 0) < 600:
            return cache["data"]
        data: Dict[str, Any] = {"roles": [], "departments": [], "errors": [],
                                "source": "live"}
        if not self.platform:
            data["errors"].append("未配置平台客户端")
            cache.update({"at": now, "data": data})
            return data
        try:
            data["roles"] = collect_roles(self.platform)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("读取角色列表失败：%s", exc)
            data["errors"].append("读取角色列表失败：%s" % str(exc)[:200])
        try:
            data["departments"] = collect_departments(self.platform)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("读取部门树失败：%s", exc)
            data["errors"].append("读取部门树失败：%s" % str(exc)[:200])
        # 读取失败时只缓存 30 秒，避免 FineBI 短暂抖动导致页面 10 分钟不可用
        cache.update({"at": now if not data["errors"] else now - 570, "data": data})
        return data

    def _load_membership_snapshot(self) -> Optional[Dict[str, Any]]:
        path = self.membership_options_path
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return None
        if self._membership_snapshot.get("mtime") == mtime:
            return self._membership_snapshot.get("data")
        data = read_json(path)
        if (not isinstance(data, dict)
                or not isinstance(data.get("roles"), list)
                or not isinstance(data.get("departments"), list)):
            return None
        self._membership_snapshot = {"mtime": mtime, "data": data}
        return data

    def directory_status(self) -> Dict[str, Any]:
        """目录/角色/部门刷新状态（供页面说明与后台管理展示）。"""
        return read_directory_status(self.directory_status_path,
                                     self.directory_refresh_hours)

    @staticmethod
    def _expire_at(days: int) -> str:
        from ..storage import expire_at_from_days
        return expire_at_from_days(days)

    # ---------- 内部 ----------
    def _require_pending(self, request_id: str) -> Dict[str, Any]:
        req = self.get_request(request_id)
        if not req:
            raise WebApprovalError("申请不存在")
        if req["status"] != "pending":
            raise WebApprovalError("当前状态不可审批：%s" % req["status"])
        return req

    @staticmethod
    def _current_step(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        steps = req.get("steps") or []
        seq = req.get("current_seq") or 0
        return steps[seq] if seq < len(steps) else None

    def _act(self, step_id: str, action: str, comment: str) -> bool:
        """CAS 更新节点动作：只有仍为 pending 的节点能被处理一次。

        返回 False 表示节点已被其他请求处理（并发/重复提交），调用方应拒绝本次操作。
        """
        cursor = self.storage.conn.execute(
            "UPDATE web_steps SET action=?, comment=?, acted_at=? "
            "WHERE id=? AND action='pending'",
            (action, comment or "", now_iso(), step_id))
        self.storage.conn.commit()
        return cursor.rowcount > 0

    def _set_status(self, request_id: str, status: str, expect: str = "") -> bool:
        """更新申请单状态；expect 非空时做 CAS（返回 False 表示状态已被别人改掉）。"""
        sql = "UPDATE web_requests SET status=?, updated_at=? WHERE id=?"
        args: List[Any] = [status, now_iso(), request_id]
        if expect:
            sql += " AND status=?"
            args.append(expect)
        cursor = self.storage.conn.execute(sql, args)
        self.storage.conn.commit()
        return cursor.rowcount > 0

    def _notify_next(self, request_id: str) -> None:
        req = self.get_request(request_id)
        step = self._current_step(req) if req else None
        if not step or not step.get("approver_id"):
            return
        user = self.get_user(step["approver_id"])
        if user:
            self._notify(user, "待审批：%s" % (req["payload"].get("resource_name")
                                             or req["payload"]["resource_id"]),
                         "申请单 %s 等待你审批" % request_id, request_id,
                         fields=self.card_fields(req))

    def _notify_applicant(self, request_id: str, title: str) -> None:
        req = self.get_request(request_id)
        user = (req or {}).get("applicant")
        if user:
            self._notify(user, title, "申请单 %s 状态：%s" % (request_id, req["status"]),
                         request_id, fields=self.card_fields(req))

    def _request_link(self, request_id: str) -> str:
        base = (self.public_base_url or "").rstrip("/")
        if not base:
            return ""
        if base.startswith(("http://127.", "http://localhost", "http://[::1]")):
            return ""
        return "%s/requests/%s" % (base, request_id)

    def _sync_bitable(self, request_id: str, action: str = "") -> None:
        """把申请单同步到飞书多维表格（失败不影响主流程）。"""
        if not self.bitable:
            return
        try:
            req = self.get_request(request_id)
            if not req:
                return
            record_id = self.storage.get_bitable_record_id(request_id)
            record_id = self.bitable.upsert(
                req, record_id=record_id, action=action,
                link=self._request_link(request_id))
            if record_id:
                table_id = getattr(self.bitable, "table_id", "")
                self.storage.save_bitable_record_id(request_id, record_id, table_id)
        except Exception:  # noqa: BLE001 - 多维表格失败不影响审批/授权
            LOGGER.warning("多维表格写入失败：%s", request_id, exc_info=True)

    def _notify(self, user: Dict[str, Any], title: str, content: str,
                request_id: str,
                fields: Optional[List[Any]] = None) -> None:
        if not self.notifier:
            return
        link = self._request_link(request_id)
        try:
            open_ids = self._notify_open_ids(user)
            extra = {"fields": fields} if fields else {}
            if open_ids:
                notify_users = getattr(self.notifier, "notify_users", None)
                if callable(notify_users):
                    # webhook 是群播：多收件人只发一次；未配置 webhook 时按 open_id 逐个发
                    try:
                        notify_users(open_ids, title, content, link=link, **extra)
                    except TypeError:
                        notify_users(open_ids, title, content, link=link)
                else:
                    for open_id in open_ids:
                        try:
                            self.notifier.notify_user(open_id, title, content,
                                                      link=link, **extra)
                        except TypeError:
                            self.notifier.notify_user(open_id, title, content, link=link)
            else:
                try:
                    self.notifier.notify_admins(title, content, link=link, **extra)
                except TypeError:
                    self.notifier.notify_admins(title, content, link=link)
        except Exception:  # noqa: BLE001
            LOGGER.warning("审批通知失败", exc_info=True)

    def _notify_open_ids(self, user: Dict[str, Any]) -> List[str]:
        """收件人 open_id：本人优先，其次同姓名/同 fb_user 的其它飞书映射。

        审批人账号可能只有 Feishu user_id、没有 open_id；用同名的其它映射补上，
        避免“没有弹飞书消息”的情况。
        """
        candidates: List[Dict[str, Any]] = [user]
        if user.get("fb_user"):
            rows = self.storage.conn.execute(
                "SELECT id,name,feishu_open_id,fb_user FROM web_users "
                "WHERE fb_user=? AND active=1", (user["fb_user"],)).fetchall()
            for row in rows:
                item = dict(row)
                if item["id"] != user["id"]:
                    candidates.append(item)
        name = str(user.get("name") or "")
        open_ids: List[str] = []
        for item in candidates:
            open_id = str(item.get("feishu_open_id") or "")
            if not open_id or open_id in open_ids:
                continue
            if item["id"] == user["id"] or str(item.get("name") or "") == name:
                open_ids.append(open_id)
        return open_ids
