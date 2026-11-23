"""授权编排：handler 注册表 + 跨进程锁 + 幂等 + 行权限合并 + 条目化执行 + 台账 + 重试。

行为约定（设计修订 V1.1 / 设计说明书 §5.3、§5.5、§5.7）：

- 条目级：一张申请拆成多条 ``request_items`` 逐项执行，支持部分成功；重试只补未完成项。
- 权限级幂等：写前 ``read`` 比对；已有 active 台账不再重复写，按需延长到期时间。
- 存量直授权限：``ADOPT_EXISTING=false``（默认）时记 ``skipped``、不建台账、通知管理员、
  并留对账标记；``true`` 时补建 ``origin=baseline`` 台账。
- 四类无查询接口的资源（publink / dash_share / dashboard_data / subject）只按台账判断。
- 写后复核（可验证类型）：不一致立即重写一次，仍不一致转人工。
- 失败进入 ``jobs``：重试类按 1/5/15 分钟退避，非重试类直接 manual。
- 保持 ``PermissionService(finebi, storage, platform=None, max_days=365, dry_run=False)``
  构造兼容，新增参数一律有默认值。
"""
from __future__ import annotations

import json
import logging
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..domain.handlers import HANDLERS, get_handler
from ..errors import (ApiError, BusinessError, is_template_auth_not_applicable)
from ..finebi import rowfilter
from ..finebi.entries import EntryAncestorResolver
from ..locks import LockTimeout, ResourceLock
from ..models import (Action, GrantResult, PermissionRequest, ResourceType,
                      build_authority, new_id, rule_key)
from ..storage import Storage, expire_at_from_days
from .jobs import KIND_GRANT, JobService, NullNotifier, is_retryable

LOGGER = logging.getLogger(__name__)

# 文件夹/数据集 authority 五个字段在接口文档中均标必填，
# 写入时必须“读回现状 → 覆盖本次变更 → 提交完整五字段”。
FULL_AUTHORITY_FIELDS = ("usePrivilege", "managePrivilege", "empowerPrivilege",
                         "biData", "biView")


# ---------------------------------------------------------------------------
# 兼容旧模块的纯函数（revoke / 外部脚本仍可 import）
# ---------------------------------------------------------------------------
def merge_full_authority(current: dict, desired: dict) -> dict:
    full = {field: bool((current or {}).get(field, False)) for field in FULL_AUTHORITY_FIELDS}
    full.update({k: v for k, v in (desired or {}).items() if k in full})
    return full


def first_data(resp: Any) -> Any:
    """取 FineBI 批量响应中的第一条 data。"""
    if not isinstance(resp, dict):
        return None
    data = resp.get("data")
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict):
            return item.get("data")
    return None


def parse_row_filter(value: Any) -> List[Dict[str, Any]]:
    """把 get 接口返回的行权限解析为规则列表（set 结构）。"""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []
    if isinstance(value, dict):
        rules = value.get("filterValue")
        if isinstance(rules, list):
            return [r for r in rules if isinstance(r, dict)]
    return []


def merge_rule_lists(existing: Iterable[Dict[str, Any]],
                     new_rules: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """合并行权限规则（set 结构，保留给旧调用方/脚本的兼容入口）。

    D-01 修复：``new_rules`` 是一张申请单的规则，语义上是 **一个 AND 组**，
    不能在组内逐条 OR。POC-3 冻结嵌套 and 结构前，单请求含 ≥2 个字段
    直接抛 :class:`BusinessError` 转人工；``existing`` 视为历史多条单条件组。
    """
    existing_groups = [[dict(rule)] for rule in existing if isinstance(rule, dict)]
    new_groups = request_rule_groups(new_rules)
    merged = merge_rule_groups(existing_groups, new_groups)
    return groups_to_set_payload(merged)


def normalize_type_map(mapping: Optional[Dict[Any, str]]) -> Dict[int, str]:
    """把配置里的 filterType 映射（JSON 的键是字符串）规范化为 int 键。

    ``mapping`` 为空（None 或 {}）表示调用方未提供映射（保持 D4 的“转人工”语义）；
    一旦提供了非空映射（运行时会传 config.policy.filter_type_map），先用接口文档
    明确给出的 and:34 or:35 str_in:10 strNotIn:12 打底，再用配置覆盖，避免配置
    只写了部分类型时把 AND/strNotIn 结构误判为未知。
    """
    if not mapping:
        return {}
    result: Dict[int, str] = dict(rowfilter.DEFAULT_TYPE_MAP)
    for key, value in mapping.items():
        try:
            result[int(key)] = str(value)
        except (TypeError, ValueError):
            continue
    return result


def row_rules_from_read(raw: Any,
                        type_map: Optional[Dict[int, str]] = None) -> Tuple[
                            Optional[List[Dict[str, Any]]], Optional[str]]:
    """把 get 返回的行权限现状解析为 set 结构规则。

    返回 ``(rules, error)``：

    - ``([], None)``：现状无规则；
    - ``(rules, None)``：可规范化（本身是 set 结构，或 filterType 可映射）；
    - ``(None, error)``：结构无法解析（转人工，不猜测）。

    filterType 数字映射取自接口文档（and:34 or:35 str_in:10 strNotIn:12），
    ``type_map`` 可覆盖；文档未定义的类型仍按 D4 转人工。
    """
    if raw is None or raw == "" or raw == {}:
        return [], None
    data = raw
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None, "行权限现状不是合法 JSON"
    if not isinstance(data, dict):
        return None, "行权限现状结构未知：%r" % type(data).__name__
    rules = data.get("filterValue")
    if not rules:
        return [], None
    if isinstance(rules, dict):
        # 单条件节点：get 直接返回一个 strIn/strNotIn 节点
        if type_map:
            try:
                expr = rowfilter.parse_get(data, type_map)
            except rowfilter.RowFilterError as exc:
                return None, "行权限现状解析失败：%s" % exc
            return rowfilter.expr_to_rules(expr), None
        return None, ("存量行权限为单条件数字结构，POC-3 映射未配置；"
                      "按设计修订 V1.1 §3 转人工处理")
    if not isinstance(rules, list):
        return None, "行权限 filterValue 不是数组"
    # 已是 set 结构（本执行器写回的格式）
    set_rules = [r for r in rules
                 if isinstance(r, dict)
                 and r.get("type") in ("strIn", "strNotIn")
                 and r.get("fieldId")]
    if len(set_rules) == len(rules):
        return set_rules, None
    # get 返回的数字 filterType 结构：需要映射才能往返转换
    if type_map:
        try:
            expr = rowfilter.parse_get(data, type_map)
        except rowfilter.RowFilterError as exc:
            return None, "行权限现状解析失败：%s" % exc
        return rowfilter.expr_to_rules(expr), None
    return None, ("存量行权限为 filterType 数字结构，POC-3 映射未配置；"
                  "按设计修订 V1.1 §3 转人工处理")


# ---------------------------------------------------------------------------
# D-01：单申请单 rules = 一个 AND 组；申请单之间才 OR
# ---------------------------------------------------------------------------
def _normalize_condition(node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": str(node.get("type") or "strIn"),
        "fieldId": str(node.get("fieldId") or ""),
        "filterValue": [str(value) for value in (node.get("filterValue") or [])],
    }


def row_rule_groups_from_read(raw: Any, type_map: Optional[Dict[int, str]] = None
                              ) -> Tuple[Optional[List[List[Dict[str, Any]]]],
                                         Optional[str]]:
    """把 get 返回的行权限现状解析为「组列表」，组内 AND、组间 OR。

    返回 ``(groups, error)``：

    - ``([], None)``：现状无规则；
    - ``([[cond], ...], None)``：组列表（组内 AND、组间 OR）；数字 filterType 用
      接口文档映射（and:34 or:35 str_in:10 strNotIn:12）解析，``type_map`` 可覆盖；
    - ``(None, error)``：无法解析（文档未定义的 filterType 等）。
    """
    if raw is None or raw == "" or raw == {}:
        return [], None
    data = raw
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None, "行权限现状不是合法 JSON"
    if not isinstance(data, dict):
        return None, "行权限现状结构未知：%r" % type(data).__name__
    nodes = data.get("filterValue")
    if not nodes:
        return [], None
    if isinstance(nodes, dict):
        # 单条件节点：get 直接返回一个 strIn/strNotIn 节点
        if type_map:
            try:
                expr = rowfilter.parse_get(data, type_map)
            except rowfilter.RowFilterError as exc:
                return None, "行权限现状解析失败：%s" % exc
            return [[condition.to_set_dict() for condition in group.conditions]
                    for group in expr.groups], None
        return None, ("存量行权限为单条件数字结构，POC-3 映射未配置；"
                      "按设计修订 V1.1 §3 转人工处理")
    if not isinstance(nodes, list):
        return None, "行权限 filterValue 不是数组"

    def _leaf(node: Any) -> bool:
        return (isinstance(node, dict)
                and node.get("type") in ("strIn", "strNotIn")
                and node.get("fieldId"))

    groups: List[List[Dict[str, Any]]] = []
    set_format = True
    for node in nodes:
        if _leaf(node):
            groups.append([_normalize_condition(node)])
        elif (isinstance(node, dict) and node.get("type") == "and"
              and isinstance(node.get("filterValue"), list)
              and all(_leaf(child) for child in node["filterValue"])):
            groups.append([_normalize_condition(child) for child in node["filterValue"]])
        else:
            set_format = False
            break
    if set_format:
        return groups, None

    # get 返回的数字 filterType 结构：需要映射才能往返转换
    if type_map:
        try:
            expr = rowfilter.parse_get(data, type_map)
        except rowfilter.RowFilterError as exc:
            return None, "行权限现状解析失败：%s" % exc
        return [[condition.to_set_dict() for condition in group.conditions]
                for group in expr.groups], None
    return None, ("存量行权限为 filterType 数字结构，POC-3 映射未配置；"
                  "按设计修订 V1.1 §3 转人工处理")


def request_rule_groups(rules: Iterable[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """单张申请单的 rules → 一个 AND 组（D-01 / POC-3 安全退化）。

    - 多字段：嵌套 AND 结构未冻结，直接抛 ``BusinessError`` 转人工，
      不允许逐条 OR 静默放大可见范围；
    - 同字段多条：同比较类型合并取值，不同类型转人工。
    """
    clean = [rule for rule in (rules or []) if isinstance(rule, dict)]
    if not clean:
        return []
    fields = sorted({str(rule.get("fieldId") or "") for rule in clean})
    if any(not field for field in fields):
        raise BusinessError("行权限规则缺少 fieldId，转人工处理")
    if len(fields) > 1:
        raise BusinessError(
            "同一申请单包含多个字段的行权限规则（%s）：AND 组结构需 POC-3 确认，"
            "按设计修订 V1.1 §3 转人工处理，不自动展开为 OR" % "、".join(fields))
    if len(clean) == 1:
        return [[_normalize_condition(clean[0])]]
    types = {str(rule.get("type") or "strIn") for rule in clean}
    if len(types) > 1:
        raise BusinessError(
            "同一申请单对字段 %s 存在多种比较类型（%s），转人工处理"
            % (fields[0], "、".join(sorted(types))))
    values: List[str] = []
    for rule in clean:
        for value in rule.get("filterValue") or []:
            text = str(value)
            if text not in values:
                values.append(text)
    return [[{"type": next(iter(types)), "fieldId": fields[0], "filterValue": values}]]


def _group_key(group: List[Dict[str, Any]]) -> tuple:
    return tuple(sorted((rule_key(condition) for condition in group), key=repr))


def merge_rule_groups(existing_groups: Iterable[List[Dict[str, Any]]],
                      new_groups: Iterable[List[Dict[str, Any]]]
                      ) -> List[List[Dict[str, Any]]]:
    """组间 OR 合并 + 去重（D-01：组内 AND 保持完整，不拆散）。"""
    merged: List[List[Dict[str, Any]]] = []
    seen = set()
    for group in list(existing_groups) + list(new_groups):
        clean = [ _normalize_condition(condition) for condition in (group or [])
                  if isinstance(condition, dict)]
        if not clean:
            continue
        if len(clean) > 1:
            raise BusinessError(
                "现有行权限包含 AND 组（多字段交集）：嵌套 and 结构需 POC-3 确认，"
                "按设计修订 V1.1 §3 转人工处理，不猜测写回结构")
        key = _group_key(clean)
        if key in seen:
            continue
        seen.add(key)
        merged.append(clean)
    return merged


def groups_to_set_payload(groups: Iterable[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """组列表 → set 接口入参：``{"type":"or","filterValue":[单条件 或 and 组...]}``。"""
    nodes: List[Dict[str, Any]] = []
    for group in groups:
        clean = [dict(condition) for condition in (group or []) if isinstance(condition, dict)]
        if not clean:
            continue
        if len(clean) == 1:
            nodes.append(clean[0])
        else:
            nodes.append({"type": "and", "filterValue": clean})
    return {"type": "or", "filterValue": nodes}


def user_roles(resp: Any, user: str = "") -> List[str]:
    """从 ``GET /v3/user/detail`` 响应中解析角色名列表。

    响应形如 ``{"data": {"total": N, "items": [{"username": ..., "roles": [{"name": ...}]}]}}``；
    ``username`` 为模糊匹配，传入 user 时按用户名精确过滤（设计修订 V1.1 §4）。
    """
    if not isinstance(resp, dict):
        return []
    data = resp.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        data = data[0].get("data")
    items: List[Any] = []
    if isinstance(data, dict):
        items = data.get("items") or []
    elif isinstance(data, list):
        items = data
    names: List[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if user and str(item.get("username") or "") != str(user):
            continue
        for role in item.get("roles") or []:
            if isinstance(role, dict):
                name = role.get("name") or role.get("roleName") or role.get("id")
            else:
                name = role
            if name:
                names.append(str(name))
    return names


def user_departments(resp: Any, user: str = "") -> List[str]:
    """从 ``GET /v3/user/detail`` 响应中解析部门完整路径（``/`` 分隔）。

    响应里是 ``departmentPosts[].department.fullPath``（如 ``财务部/财务一部``）；
    ``username`` 为模糊匹配，传入 user 时按用户名精确过滤。
    """
    if not isinstance(resp, dict):
        return []
    data = resp.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        data = data[0].get("data")
    items: List[Any] = []
    if isinstance(data, dict):
        items = data.get("items") or []
    elif isinstance(data, list):
        items = data
    paths: List[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if user and str(item.get("username") or "") != str(user):
            continue
        for entry in item.get("departmentPosts") or []:
            department = (entry or {}).get("department") if isinstance(entry, dict) else None
            if not isinstance(department, dict):
                continue
            full_path = department.get("fullPath") or department.get("name")
            if full_path:
                paths.append(str(full_path).strip("/"))
    return paths


def department_path_of(resource_id: str) -> str:
    """把部门台账的 resource_id（路径 JSON 字符串）转成 ``/`` 分隔的完整路径。"""
    text = str(resource_id or "").strip()
    if not text:
        return ""
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError):
        return text.strip("/")
    if isinstance(parsed, list):
        return "/".join(str(part).strip("/") for part in parsed if str(part).strip())
    return str(parsed or "").strip("/")


def error_code_of(exc: BaseException) -> str:
    """把异常映射为需求书错误码（用于台账与日志检索）。"""
    if isinstance(exc, LockTimeout):
        return "E5001"
    if isinstance(exc, ApiError):
        status = exc.status
        if isinstance(status, int):
            if status == 403:
                return "E3003"
            if status == 429 or status >= 500:
                return "E3001"
            return "E3002"
        if str(status).upper() in ("NETWORK", "TIMEOUT"):
            return "E3001"
        return "E3002"
    if isinstance(exc, BusinessError):
        return "E1003"
    return "E9999"


def trace_id_of(resp: Any) -> str:
    if not isinstance(resp, dict):
        return ""
    for key in ("traceId", "trace_id"):
        if resp.get(key):
            return str(resp[key])
    data = resp.get("data")
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            for key in ("traceId", "trace_id"):
                if item.get(key):
                    return str(item[key])
    return ""


class PermissionService:
    """授权服务。``grant(req) -> GrantResult`` 为唯一公开入口。"""

    def __init__(self, finebi, storage: Storage, platform=None,
                 max_days: int = 365, dry_run: bool = False,
                 lock: Optional[ResourceLock] = None,
                 handlers: Optional[Dict[str, Any]] = None,
                 notifier: Any = None,
                 adopt_existing: bool = False,
                 jobs: Optional[JobService] = None,
                 lock_ttl: int = 120, lock_wait: int = 30,
                 type_map: Optional[Dict[Any, str]] = None):
        self.finebi = finebi
        self.platform = platform
        self.storage = storage
        self.max_days = max_days
        self.dry_run = dry_run
        self.clients = SimpleNamespace(finebi=finebi, platform=platform)
        self.entry_resolver = EntryAncestorResolver(platform) if platform else None
        self.handlers = dict(HANDLERS) if handlers is None else dict(handlers)
        self.lock = lock if lock is not None else \
            ResourceLock(storage.db_path, ttl=lock_ttl, wait=lock_wait)
        self.notifier = notifier or NullNotifier()
        self.adopt_existing = bool(adopt_existing)
        self.type_map = normalize_type_map(type_map)
        self.jobs = jobs if jobs is not None else JobService(storage, notifier=self.notifier)
        self.owner = "grant-%s" % new_id("worker")[7:]
        if not self.jobs.has_handler(KIND_GRANT):
            self.jobs.register_handler(KIND_GRANT, self._replay_request)

    # ---------- 公开入口 ----------
    def grant(self, req: PermissionRequest) -> GrantResult:
        return self._grant(req, enqueue=True)

    # ---------- 主流程 ----------
    def _grant(self, req: PermissionRequest, enqueue: bool) -> GrantResult:
        items = self._normalize_items(req)
        self._validate(req, items)
        self.storage.upsert_request(req.request_id, req.source, req.user, req.to_dict())
        self._reset_request_items(req.request_id)
        self.storage.log("INFO", "grant", "开始执行授权申请", {
            "request_id": req.request_id, "user": req.user, "items": len(items),
            "source": req.source, "dry_run": self.dry_run})

        item_ids = self.storage.add_request_items(req.request_id, items)
        outcomes: List[Dict[str, Any]] = []
        for seq, item in enumerate(items):
            outcome = self._run_locked(req, item)
            outcome["seq"] = seq + 1
            outcome["item_id"] = item_ids[seq]
            outcome["resource_type"] = item["resource_type"]
            outcome["resource_id"] = item["resource_id"]
            self.storage.update_request_item(
                item_ids[seq], self._item_status(outcome["status"]),
                error_code=str(outcome.get("error_code") or ""),
                error_msg=str(outcome.get("error") or outcome.get("reason") or ""),
                ledger_id=str(outcome.get("ledger_id") or ""))
            outcomes.append(outcome)

        ledger_ids = [str(o["ledger_id"]) for o in outcomes if o.get("ledger_id")]
        failed = [o for o in outcomes if o["status"] == "failed"]
        granted = [o for o in outcomes if o["status"] == "granted"]
        if failed:
            status = "partial" if granted else "failed"
            request_status = "partial" if granted else "failed"
        else:
            status = "granted" if granted else "skipped"
            request_status = "done"
        self.storage.set_request_status(req.request_id, request_status)
        self.storage.log(
            "ERROR" if failed else "INFO", "grant",
            "授权%s" % ("部分失败" if status == "partial" else
                        ("失败" if status == "failed" else "完成")),
            {"request_id": req.request_id, "user": req.user, "status": status,
             "ledger_ids": ledger_ids,
             "items": [{"seq": o["seq"], "resource": "%s:%s" % (
                 o["resource_type"], o["resource_id"]),
                 "status": o["status"], "reason": o.get("reason") or o.get("error") or ""}
                 for o in outcomes]})
        if failed and enqueue and not self.dry_run:
            self._schedule_failure(req, failed)
        detail = {
            "items": outcomes,
            "dry_run": self.dry_run,
            "request_status": request_status,
        }
        return GrantResult(status=status, request_id=req.request_id,
                           ledger_ids=ledger_ids, details=detail,
                           item_results=outcomes)

    def _reset_request_items(self, request_id: str) -> None:
        """重放同一申请时清掉旧条目（request_items(request_id, seq) 唯一）。"""
        try:
            self.storage.conn.execute(
                "DELETE FROM request_items WHERE request_id=?", (request_id,))
            self.storage.conn.commit()
        except Exception:  # noqa: BLE001 - 清理失败时仍尝试追加（冲突会暴露为失败）
            LOGGER.warning("清理旧申请条目失败：%s", request_id, exc_info=True)

    def _normalize_items(self, req: PermissionRequest) -> List[Dict[str, Any]]:
        raw_items = list(getattr(req, "items", None) or [])
        items: List[Dict[str, Any]] = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                raise ValueError("items 元素必须是对象：%r" % (raw,))
            items.append(self._normalize_item(raw, req))
        if not items:
            items.append(self._normalize_item({}, req))
        if req.role and not any(i["resource_type"] == ResourceType.ROLE for i in items):
            items.append({
                "resource_type": ResourceType.ROLE,
                "resource_id": str(req.role),
                "actions": [],
                "data_scope": {},
                "role": str(req.role),
                "extra": {"role": str(req.role)},
                "authority": {},
            })
        return items

    @staticmethod
    def _normalize_item(raw: Dict[str, Any], req: PermissionRequest) -> Dict[str, Any]:
        resource_type = str(raw.get("resource_type") or req.resource_type or "")
        resource_id = str(raw.get("resource_id") or req.resource_id or "")
        role = raw.get("role")
        if resource_type == ResourceType.ROLE and not role:
            role = resource_id or req.role
        item = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "actions": [str(a) for a in (raw.get("actions")
                                         if raw.get("actions") is not None else req.actions) or []],
            "data_scope": dict(raw.get("data_scope")
                               if raw.get("data_scope") is not None else req.data_scope),
            "role": role,
            "extra": dict(raw.get("extra") or {}),
            "authority": dict(raw.get("authority") or {}),
            # 随仪表板申请连带授予的组件数据：只写权限、不记台账（回收只处理仪表板权限）
            "record_ledger": bool(raw.get("record_ledger", True)),
        }
        if resource_type == ResourceType.ROLE and not item["resource_id"] and role:
            item["resource_id"] = str(role)
        return item

    def _validate(self, req: PermissionRequest, items: List[Dict[str, Any]]) -> None:
        if not req.user:
            raise ValueError("user 不能为空")
        if req.days <= 0 or (req.days > self.max_days and not req.extra.get("long_term")):
            raise ValueError("期限必须为 1~%d 天" % self.max_days)
        for item in items:
            rt = item["resource_type"]
            if rt not in ResourceType.ALL:
                raise ValueError("未知资源类型：%s" % rt)
            if not item["resource_id"]:
                raise ValueError("resource_id 不能为空")
            if rt == ResourceType.ROW and not (item["data_scope"].get("rules") or []):
                raise ValueError("行权限申请必须提供 data_scope.rules")

    # ---------- 单条目执行 ----------
    def _run_locked(self, req: PermissionRequest, item: Dict[str, Any]) -> Dict[str, Any]:
        key = self._lock_key(req.user, item["resource_type"], item["resource_id"])
        try:
            if self.dry_run:
                return self._run_item(req, item)
            with self.lock.hold(key, self.owner):
                return self._run_item(req, item)
        except Exception as exc:  # noqa: BLE001 - 条目失败不阻断其他条目
            return self._failure(exc, item)

    def _run_item(self, req: PermissionRequest, item: Dict[str, Any]) -> Dict[str, Any]:
        rt = item["resource_type"]
        rid = item["resource_id"]
        if rt == ResourceType.ROLE and self.platform is None:
            LOGGER.warning("未配置平台客户端，跳过角色分配：%s -> %s", req.user, rid)
            return {"status": "skipped", "reason": "未配置平台客户端（platform），跳过角色分配",
                    "changed": False}
        handler = get_handler(rt)
        desired = self._desired(rt, item)
        if not desired:
            return {"status": "skipped", "reason": "未指定权限项（actions/authority 为空）",
                    "changed": False}
        if rt == ResourceType.ROW:
            # D-01：单申请单是一个 AND 组；POC-3 前多字段直接转人工，不静默 OR 扩权
            request_rule_groups(desired.get("rules") or [])

        existing = self._existing_ledgers(req.user, rt, rid)
        if (item.get("record_ledger", True) and existing
                and self._covered_by_ledgers(rt, desired, existing)):
            # 台账有效不代表 FineBI 里权限还在（可能被 FineBI 侧重置/人工清空），
            # 先读实际权限；实际缺失就重新写，不能只延期台账。
            still_covered = True
            if handler.verifiable and handler.read and not self.dry_run:
                try:
                    current_now = handler.read(self.clients, req.user, rid)
                    still_covered = self._satisfied(rt, item, desired, current_now, req.user)
                except Exception as exc:  # noqa: BLE001
                    if (rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT)
                            and is_template_auth_not_applicable(exc)):
                        still_covered = False
                    else:
                        LOGGER.warning("台账覆盖校验读取失败，按台账继续：%s", exc)
            if still_covered:
                if self.dry_run:
                    # dry-run 不得改动真实台账到期时间，否则演练会顺延线上权限
                    return {"status": "skipped",
                            "reason": "dry-run：已有有效台账覆盖本次权限（未延长台账）",
                            "changed": False, "dry_run": True,
                            "ledger_id": existing[0]["id"]}
                extended = [ledger["id"] for ledger in existing
                            if self._extend_ledger(ledger, req.days)]
                return {"status": "skipped", "reason": "已有有效台账覆盖本次权限，不重复写入",
                        "changed": False, "ledger_id": existing[0]["id"],
                        "extended": extended}
            LOGGER.info("台账存在但 FineBI 实际权限缺失，重新授权：%s %s:%s",
                        req.user, rt, rid)

        current: Any = None
        if handler.verifiable and handler.read:
            try:
                current = handler.read(self.clients, req.user, rid)
            except Exception as exc:  # noqa: BLE001
                if (rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT)
                        and is_template_auth_not_applicable(exc)):
                    return self._template_auth_skip_result()
                raise
            if self._satisfied(rt, item, desired, current, req.user):
                if not self.adopt_existing:
                    self._notify_adopt_skip(req, item)
                    return {"status": "skipped",
                            "reason": "存量权限未纳管（ADOPT_EXISTING=false）",
                            "error_code": "SKIP_ADOPT", "changed": False,
                            "adopt_existing": False, "reconcile": "diff"}
                if self.dry_run:
                    # dry-run 不写基线台账，避免把演练变成真实纳管
                    return {"status": "skipped",
                            "reason": "dry-run：存量权限可纳管为基线台账（未写入）",
                            "changed": False, "dry_run": True, "would_adopt": True,
                            "adopt_existing": True}
                fragment = self._baseline_fragment(rt, item, current)
                fragment["origin"] = "baseline"
                ledger_id = self._write_ledger(req, item, fragment)
                self.storage.log("INFO", "grant_adopt", "存量权限纳管为基线台账", {
                    "ledger_id": ledger_id, "user": req.user,
                    "resource": "%s:%s" % (rt, rid)})
                return {"status": "skipped", "reason": "存量权限已纳管为基线台账",
                        "changed": False, "ledger_id": ledger_id, "adopt_existing": True}

        payload = self._build_payload(rt, item, desired, current)
        if self.dry_run:
            return {"status": "skipped", "reason": "dry-run 未写权限", "changed": False,
                    "dry_run": True, "would_write": payload}
        if rt == ResourceType.DASHBOARD_ENTRY:
            # FineBI 要求祖先链完整：只授仪表板 entry 而不授所属文件夹 view
            # 会报 forbid incomplete authorize exception。
            self._ensure_entry_ancestors(req.user, rid)

        export_fallback = False
        try:
            resp = handler.write(self.clients, req.user, rid, payload)
        except Exception as exc:  # noqa: BLE001
            if (rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT)
                    and is_template_auth_not_applicable(exc)):
                return self._template_auth_skip_result()
            # FineBI 未开模板认证时，entry 同时写 export 会报 incomplete authorize；
            # 降级为只授查看，导出需等 FineBI 开启模板认证后重新申请。
            if (rt == ResourceType.DASHBOARD_ENTRY
                    and isinstance(payload.get("authority"), dict)
                    and payload["authority"].get("export")
                    and self._is_incomplete_authorize(exc)):
                retry_payload = {"authority": dict(payload["authority"], export=False)}
                resp = handler.write(self.clients, req.user, rid, retry_payload)
                payload = retry_payload
                desired = dict(desired, export=False)
                export_fallback = True
                LOGGER.warning("FineBI 未开启模板认证，entry 导出降级为仅查看：%s", rid)
            else:
                raise
        if handler.verifiable and handler.read:
            try:
                verified = self._verify(rt, item, desired, handler, req.user)
            except Exception as exc:  # noqa: BLE001
                if (rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT)
                        and is_template_auth_not_applicable(exc)):
                    return self._template_auth_skip_result()
                raise
            if not verified:
                LOGGER.warning("写后复核不一致，重写一次：%s %s:%s", req.user, rt, rid)
                resp = handler.write(self.clients, req.user, rid, payload)
                if not self._verify(rt, item, desired, handler, req.user):
                    raise BusinessError("写后复核不一致（E3004），已重写一次仍不通过")
        fragment = self._ledger_fragment(rt, item, desired, payload)
        if not item.get("record_ledger", True):
            # 组件数据随仪表板申请连带授予：按要求只写 FineBI、不记台账，
            # 到期/离职回收只处理仪表板权限，不对组件数据做回收。
            self.storage.log("INFO", "grant_component",
                             "随单授予组件数据（不记台账，回收不处理）", {
                                 "user": req.user,
                                 "resource": "%s:%s" % (rt, rid),
                                 "authority": fragment.get("authority") or {}})
            return {"status": "granted", "changed": True,
                    "authority": desired, "payload": payload,
                    "trace_id": trace_id_of(resp), "record_ledger": False}
        ledger_id = self._write_ledger(req, item, fragment, trace_id=trace_id_of(resp))
        self.storage.log("INFO", "grant_item", "条目授权完成", {
            "ledger_id": ledger_id, "user": req.user,
            "resource": "%s:%s" % (rt, rid), "payload": fragment})
        result = {"status": "granted", "changed": True, "ledger_id": ledger_id,
                  "authority": desired, "payload": payload,
                  "trace_id": trace_id_of(resp)}
        if export_fallback:
            result["export_skipped"] = True
            result["reason"] = ("FineBI 模板认证未开启，仅授予查看权限；"
                                "导出需在 FineBI 开启模板认证后重新申请")
        return result

    # ---------- 期望值与比对 ----------
    def _desired(self, rt: str, item: Dict[str, Any]) -> Dict[str, Any]:
        actions = item.get("actions") or []
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            desired = build_authority(actions)
            for key, value in (item.get("authority") or {}).items():
                if value:
                    desired[str(key)] = bool(value)
            if desired.get("usePrivilege"):
                # FineBI 要求：开 usePrivilege 时必须同时开 biData、biView
                desired.setdefault("biData", True)
                desired.setdefault("biView", True)
            return desired
        if rt == ResourceType.FIELD:
            return {"biData": True}
        if rt == ResourceType.ROW:
            rules = [r for r in item["data_scope"].get("rules") or [] if isinstance(r, dict)]
            return {"rules": rules} if rules else {}
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            export = (Action.EXPORT in actions
                      or rt == ResourceType.DASHBOARD_EXPORT)
            view = (Action.VIEW in actions or export)
            if not view and not export:
                return {}
            return {"view": bool(view), "export": bool(export)}
        if rt == ResourceType.DASHBOARD_ENTRY:
            export = Action.EXPORT in actions
            edit = Action.EDIT in actions
            return {"viewPrivilege": bool(Action.VIEW in actions or export or edit),
                    "export": bool(export), "editPrivilege": bool(edit)}
        if rt == ResourceType.PUBLINK:
            return {"biShareFun": True}
        if rt == ResourceType.DASH_SHARE:
            return {"view": True}
        if rt == ResourceType.DASHBOARD_DATA:
            return {"biData": True}
        if rt == ResourceType.SUBJECT:
            return {"use": True, "edit": Action.EDIT in actions}
        if rt == ResourceType.ROLE:
            return {"role": item["resource_id"]}
        if rt == ResourceType.DEPARTMENT:
            return {"department": item["resource_id"]}
        return {}

    def _satisfied(self, rt: str, item: Dict[str, Any], desired: Dict[str, Any],
                   current: Any, user: str = "") -> bool:
        data = first_data(current)
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            cur = data if isinstance(data, dict) else {}
            return bool(desired) and all(bool(cur.get(k)) for k, v in desired.items() if v)
        if rt == ResourceType.FIELD:
            cur = data if isinstance(data, dict) else {}
            return bool(cur.get("biData"))
        if rt == ResourceType.ROW:
            groups, error = row_rule_groups_from_read(data, self.type_map)
            if error or groups is None or any(len(group) > 1 for group in groups):
                return False
            existing_keys = {rule_key(group[0]) for group in groups}
            wanted = [group[0] for group in
                      request_rule_groups(desired.get("rules") or [])]
            return bool(wanted) and all(rule_key(rule) in existing_keys
                                        for rule in wanted)
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            cur = data if isinstance(data, dict) else {}
            return ((not desired.get("view") or bool(cur.get("view")))
                    and (not desired.get("export") or bool(cur.get("export"))))
        if rt == ResourceType.DASHBOARD_ENTRY:
            cur = data if isinstance(data, dict) else {}
            return ((not desired.get("viewPrivilege") or bool(cur.get("viewPrivilege")))
                    and (not desired.get("export") or bool(cur.get("export")))
                    and (not desired.get("editPrivilege") or bool(cur.get("editPrivilege"))))
        if rt == ResourceType.ROLE:
            role = str(item.get("resource_id") or "")
            # user/detail 的 username 是模糊匹配，必须按目标用户精确过滤，
            # 否则同名片段的其他用户有该角色会被误判为“已满足”而跳过授权。
            return bool(role) and role in user_roles(current, user)
        if rt == ResourceType.DEPARTMENT:
            path = department_path_of(str(item.get("resource_id") or ""))
            return bool(path) and path in user_departments(current, user)
        return False

    def _build_payload(self, rt: str, item: Dict[str, Any], desired: Dict[str, Any],
                       current: Any) -> Dict[str, Any]:
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            cur = first_data(current)
            return {"authority": merge_full_authority(
                cur if isinstance(cur, dict) else {}, desired)}
        if rt == ResourceType.FIELD:
            return {"authority": {"biData": True}}
        if rt == ResourceType.ROW:
            groups, error = row_rule_groups_from_read(first_data(current), self.type_map)
            if error:
                raise BusinessError(error)
            merged = merge_rule_groups(groups or [],
                                       request_rule_groups(desired.get("rules") or []))
            return {"filter": groups_to_set_payload(merged)}
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            return {"authority": {"view": bool(desired.get("view")),
                                  "export": bool(desired.get("export"))}}
        if rt == ResourceType.DASHBOARD_ENTRY:
            # entry 权限是四字段全量覆盖：本次未申请的 edit/empower 保留现状
            cur = first_data(current)
            cur = cur if isinstance(cur, dict) else {}
            return {"authority": {
                "viewPrivilege": bool(desired.get("viewPrivilege")),
                "export": bool(desired.get("export")),
                "editPrivilege": bool(desired.get("editPrivilege")
                                      or cur.get("editPrivilege")),
                "empowerPrivilege": bool(cur.get("empowerPrivilege"))}}
        if rt == ResourceType.PUBLINK:
            return {"authority": {"biShareFun": True}}
        if rt == ResourceType.DASH_SHARE:
            return {}
        if rt == ResourceType.DASHBOARD_DATA:
            entry = item["extra"].get("entry") or item["resource_id"]
            return {"entry": entry}
        if rt == ResourceType.SUBJECT:
            return {"authority": {"use": True, "edit": bool(desired.get("edit"))}}
        return {}

    def _verify(self, rt: str, item: Dict[str, Any], desired: Dict[str, Any],
                handler: Any, user: str) -> bool:
        current = handler.read(self.clients, user, item["resource_id"])
        return self._satisfied(rt, item, desired, current, user)

    # ---------- 台账 ----------
    @staticmethod
    def _ledger_types(rt: str) -> Tuple[str, ...]:
        """同一底层资源对应的台账类型组：仪表板查看/导出共用资源。"""
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            return (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT)
        return (rt,)

    @staticmethod
    def _item_status(status: str) -> str:
        """把内部执行状态映射为 request_items 表的状态枚举。"""
        return {"granted": "done", "failed": "failed", "skipped": "skipped"}.get(
            status, status)

    def _existing_ledgers(self, user: str, rt: str,
                          rid: str) -> List[Dict[str, Any]]:
        """该用户在该资源上的全部 active 台账。

        角色兼容旧格式：旧台账把角色记在主台账 ``payload.role`` 中；
        仪表板查看/导出共享同一 ``biReportId``，按类型组合并判断。
        """
        types = self._ledger_types(rt)
        ledgers: List[Dict[str, Any]] = []
        for ledger in self.storage.active_ledger(user=user):
            if (ledger["resource_type"] in types
                    and str(ledger["resource_id"]) == str(rid)):
                ledgers.append(ledger)
                continue
            if rt == ResourceType.ROLE:
                payload = ledger.get("payload") or {}
                if str(payload.get("role") or "") == str(rid):
                    ledgers.append(ledger)
        return ledgers

    def _covered_by_ledgers(self, rt: str, desired: Dict[str, Any],
                            ledgers: List[Dict[str, Any]]) -> bool:
        """台账并集是否已覆盖本次期望权限（权限级幂等）。"""
        if not ledgers:
            return False
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            granted: set = set()
            for ledger in ledgers:
                authority = (ledger.get("payload") or {}).get("authority") or {}
                granted.update(str(f) for f, v in authority.items() if v)
            return bool(desired) and all(str(k) in granted
                                         for k, v in desired.items() if v)
        if rt == ResourceType.FIELD:
            return any(bool(((ledger.get("payload") or {}).get("authority") or {})
                            .get("biData")) for ledger in ledgers)
        if rt == ResourceType.ROW:
            covered: set = set()
            for ledger in ledgers:
                for rule in (ledger.get("payload") or {}).get("rules") or []:
                    if isinstance(rule, dict):
                        covered.add(rule_key(rule))
            wanted = desired.get("rules") or []
            return bool(wanted) and all(rule_key(rule) in covered for rule in wanted)
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            view = export = False
            for ledger in ledgers:
                authority = (ledger.get("payload") or {}).get("authority") or {}
                view = view or bool(authority.get("view"))
                export = export or bool(authority.get("export"))
            return (not desired.get("view") or view) and (not desired.get("export") or export)
        if rt == ResourceType.DASHBOARD_ENTRY:
            view = export = False
            for ledger in ledgers:
                authority = (ledger.get("payload") or {}).get("authority") or {}
                view = view or bool(authority.get("viewPrivilege"))
                export = export or bool(authority.get("export"))
            return ((not desired.get("viewPrivilege") or view)
                    and (not desired.get("export") or export))
        if rt == ResourceType.ROLE:
            return bool(ledgers)
        # 四类无查询接口的资源：只按台账判断（D3）
        return True

    def _extend_ledger(self, ledger: Dict[str, Any], days: int) -> bool:
        new_expire = expire_at_from_days(days)
        old_expire = str(ledger.get("expire_at") or "")
        if old_expire and new_expire <= old_expire:
            return False
        extender = getattr(self.storage, "extend_ledger", None)
        if callable(extender):
            try:
                extender(ledger["id"], new_expire)
                return True
            except Exception:  # noqa: BLE001 - 退化为直接 SQL
                LOGGER.warning("storage.extend_ledger 调用失败，改用直接 SQL", exc_info=True)
        try:
            cursor = self.storage.conn.execute(
                "UPDATE ledger SET expire_at=? WHERE id=? AND status='active'",
                (new_expire, ledger["id"]))
            self.storage.conn.commit()
            return (cursor.rowcount or 0) > 0
        except Exception:  # noqa: BLE001 - 延长到期失败不影响幂等跳过
            LOGGER.warning("延长台账到期时间失败：%s", ledger["id"], exc_info=True)
            return False

    def _write_ledger(self, req: PermissionRequest, item: Dict[str, Any],
                      fragment: Dict[str, Any], trace_id: str = "") -> str:
        payload = dict(fragment)
        payload.setdefault("origin", "request")
        payload["source"] = req.source
        if item.get("extra"):
            payload["extra"] = dict(item["extra"])
        return self.storage.add_ledger(
            request_id=req.request_id, user=req.user,
            resource_type=item["resource_type"], resource_id=item["resource_id"],
            payload=payload, expire_at=expire_at_from_days(req.days), trace_id=trace_id)

    def _ledger_fragment(self, rt: str, item: Dict[str, Any], desired: Dict[str, Any],
                         payload: Dict[str, Any]) -> Dict[str, Any]:
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            return {"authority": desired}
        if rt == ResourceType.FIELD:
            return {"authority": {"biData": True}}
        if rt == ResourceType.ROW:
            return {"rules": list(desired.get("rules") or []),
                    "filter": payload.get("filter")}
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            return {"authority": dict(desired)}
        if rt == ResourceType.DASHBOARD_ENTRY:
            return {"authority": dict(desired)}
        if rt == ResourceType.PUBLINK:
            return {"authority": {"biShareFun": True}}
        if rt == ResourceType.DASH_SHARE:
            return {"authority": {"view": True}}
        if rt == ResourceType.DASHBOARD_DATA:
            return {"authority": {"biData": True}, "entry": payload.get("entry")}
        if rt == ResourceType.SUBJECT:
            return {"authority": dict(desired)}
        if rt == ResourceType.ROLE:
            return {"role": item["resource_id"], "authority": {}}
        if rt == ResourceType.DEPARTMENT:
            return {"department": item["resource_id"], "authority": {}}
        return {}

    def _baseline_fragment(self, rt: str, item: Dict[str, Any],
                           current: Any) -> Dict[str, Any]:
        """存量纳管（origin=baseline）时，台账记录“现状全部权限”，回收才能完整退回。"""
        data = first_data(current)
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            full = merge_full_authority(data if isinstance(data, dict) else {}, {})
            return {"authority": {field: value for field, value in full.items() if value}}
        if rt == ResourceType.ROW:
            groups, error = row_rule_groups_from_read(data, self.type_map)
            if error:
                # 无法解析现状时不纳管（避免覆盖存量规则），由调用方转人工
                return {"authority": {}, "unparsed_rules": str(data)}
            groups = groups or []
            return {"rules": [group[0] for group in groups],
                    "filter": groups_to_set_payload(groups)}
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            cur = data if isinstance(data, dict) else {}
            return {"authority": {"view": bool(cur.get("view")),
                                  "export": bool(cur.get("export"))}}
        if rt == ResourceType.DASHBOARD_ENTRY:
            cur = data if isinstance(data, dict) else {}
            return {"authority": {"viewPrivilege": bool(cur.get("viewPrivilege")),
                                  "export": bool(cur.get("export"))}}
        if rt == ResourceType.FIELD:
            return {"authority": {"biData": True}}
        if rt in (ResourceType.ROLE, ResourceType.DEPARTMENT):
            # 存量纳管：成员关系申请前已存在，回收时不能把原有成员关系删掉
            key = "role" if rt == ResourceType.ROLE else "department"
            return {key: item["resource_id"], "preexisting": True, "authority": {}}
        return self._ledger_fragment(rt, item, self._desired(rt, item), {})

    # ---------- 失败 / 通知 ----------
    @staticmethod
    def _is_incomplete_authorize(exc: BaseException) -> bool:
        return "incomplete authorize" in str(exc).lower()

    def _ensure_entry_ancestors(self, user: str, entry_id: str) -> None:
        """补授仪表板所属文件夹的查看权限，保证 entry 祖先链完整。"""
        resolver = self.entry_resolver
        if resolver is None or not self.platform:
            return
        ancestors = resolver.ancestors(entry_id)
        if not ancestors:
            return
        try:
            resp = self.finebi.get_entry_authority(user, ancestors)
            data = (resp or {}).get("data") or {}
            rows = data.get("entry") if isinstance(data, dict) else None
            by_id = {str((row or {}).get("entryId")): (row or {}).get("authority") or {}
                     for row in rows or [] if isinstance(row, dict)}
        except Exception as exc:  # noqa: BLE001 - 读不到就交给子节点写入报错
            LOGGER.warning("读取祖先 entry 权限失败：%s", exc)
            return
        for ancestor in ancestors:
            authority = by_id.get(ancestor) or {}
            if authority.get("viewPrivilege"):
                continue
            payload = {"viewPrivilege": True,
                       "export": bool(authority.get("export")),
                       "editPrivilege": bool(authority.get("editPrivilege")),
                       "empowerPrivilege": bool(authority.get("empowerPrivilege"))}
            try:
                self.finebi.set_entry_authority(user, ancestor, payload)
                LOGGER.info("补授祖先 entry 查看权限：%s -> %s", user, ancestor)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("补授祖先 entry 权限失败（%s）：%s", ancestor, exc)

    @staticmethod
    def _template_auth_skip_result() -> Dict[str, Any]:
        return {"status": "skipped",
                "reason": "FineBI 未开启模板认证或该仪表板未纳入模板认证，跳过模板授权；目录权限仍正常授予",
                "error_code": "TEMPLATE_AUTH_NOT_APPLICABLE",
                "changed": False}

    def _failure(self, exc: BaseException, item: Dict[str, Any]) -> Dict[str, Any]:
        code = error_code_of(exc)
        message = "%s: %s" % (type(exc).__name__, exc)
        LOGGER.error("条目执行失败 %s:%s -> %s", item.get("resource_type"),
                     item.get("resource_id"), message)
        self.storage.log("ERROR", "grant_item", "条目执行失败", {
            "resource": "%s:%s" % (item.get("resource_type"), item.get("resource_id")),
            "error_code": code, "error": message})
        return {"status": "failed", "error": message, "error_code": code,
                "retryable": is_retryable(exc)}

    def _schedule_failure(self, req: PermissionRequest,
                          failed: List[Dict[str, Any]]) -> None:
        retryable = any(o.get("retryable") for o in failed)
        error = "; ".join(str(o.get("error")) for o in failed)
        # 由 jobs 触发的重放或已有排队任务时，不再重复入队（由任务队列统一退避计次）
        has_open = getattr(self.jobs, "has_open_job", None)
        if callable(has_open) and has_open(KIND_GRANT, req.request_id):
            self._notify_admins("授权失败", "申请 %s（用户 %s）执行失败：%s，等待重试任务处理。"
                                % (req.request_id, req.user, error))
            return
        # 已有未闭环人工待办时不重复插单（轮询/人工重试均可能再次触发同一申请）
        has_manual = getattr(self.jobs, "has_manual_job", None)
        if callable(has_manual) and has_manual(KIND_GRANT, req.request_id):
            self._notify_admins("授权失败", "申请 %s（用户 %s）执行失败：%s，人工待办已存在。"
                                % (req.request_id, req.user, error))
            return
        try:
            if retryable:
                self.jobs.schedule_retry(KIND_GRANT, req.request_id, failed_attempts=1)
            else:
                self.jobs.enqueue_manual(KIND_GRANT, req.request_id, error=error)
        except Exception:  # noqa: BLE001 - 入队失败不影响返回结果
            LOGGER.warning("授权失败任务入队失败：%s", req.request_id, exc_info=True)
        self._notify_admins(
            "授权失败%s" % ("（重试类，将自动重试）" if retryable else "（已转人工）"),
            "申请 %s（用户 %s）执行失败：%s" % (req.request_id, req.user, error))

    def _notify_adopt_skip(self, req: PermissionRequest,
                           item: Dict[str, Any]) -> None:
        message = ("用户 %s 对 %s:%s 已具备权限但无台账（ADOPT_EXISTING=false），"
                   "本次未纳管、不参与到期回收，已列入对账差异。"
                   % (req.user, item["resource_type"], item["resource_id"]))
        self.storage.log("WARNING", "grant_adopt_skip", message, {
            "request_id": req.request_id, "user": req.user,
            "resource": "%s:%s" % (item["resource_type"], item["resource_id"])})
        self._notify_admins("存量权限未纳管", message)

    def _notify_admins(self, title: str, content: str) -> None:
        try:
            self.notifier.notify_admins(title, content)
        except Exception:  # noqa: BLE001 - 通知失败不影响主流程
            LOGGER.warning("通知发送失败：%s", title, exc_info=True)

    @staticmethod
    def _lock_key(user: str, rt: str, rid: str) -> str:
        return "fb_user:%s:%s:%s" % (user, rt, rid)

    # ---------- 重试回放 ----------
    def _replay_request(self, request_id: str) -> Any:
        """jobs 重试处理函数：重放失败的申请（幂等跳过已成功条目）。

        D-05：返回 GrantResult 而不是把失败包成 BusinessError——
        ``JobService`` 会按 ``item_results`` 的 retryable 标记决定继续退避还是转人工。
        """
        row = self.storage.get_request(request_id)
        if not row:
            raise BusinessError("重试任务找不到申请：%s" % request_id)
        payload = row.get("payload") or {}
        req = PermissionRequest.from_dict(payload if isinstance(payload, dict) else {})
        self.storage.set_request_status(request_id, "pending")
        return self._grant(req, enqueue=False)

