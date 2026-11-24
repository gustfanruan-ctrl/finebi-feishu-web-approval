"""资源处理器注册表：每类资源统一的 read/write/revoke 入口。

四类只有设置接口、没有查询接口（publink / dash_share / dashboard_data / subject），
因此 `verifiable=False`：不能写前查、写后核，幂等只能依赖台账。

另有两个由自建 Web 审批直接写入台账的平台权限类型（不属于 BI 开放平台资源）：
``platform_module``（定时调度功能权限）与 ``schedule``（定时调度任务权限）。
它们同样没有可用的查询接口，回收走平台接口 set_user_platform_permission /
set_user_schedule_permission，否则到期/离职回收会因“未知资源类型”永远失败。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from ..models import ResourceType

PLATFORM_MODULE = "platform_module"   # web 审批台账：定时调度功能权限
SCHEDULE = "schedule"                 # web 审批台账：定时调度任务管理/授权
PLATFORM_RESOURCE_TYPES = (PLATFORM_MODULE, SCHEDULE)


@dataclass(frozen=True)
class Handler:
    type: str
    verifiable: bool
    read: Optional[Callable[[Any, str, str], Any]]
    write: Callable[[Any, str, str, Dict[str, Any]], Any]
    revoke: Callable[[Any, str, str, Dict[str, Any]], Any]


# ---------- read ----------
def _read_folder(c, user, rid):
    return c.finebi.get_folder_permission(user, rid)


def _read_table(c, user, rid):
    return c.finebi.get_table_permission(user, rid)


def _read_field(c, user, rid):
    return c.finebi.get_field_permission(user, rid)


def _read_row(c, user, rid):
    return c.finebi.get_row_filter(user, rid)


def _read_dashboard(c, user, rid):
    return c.finebi.get_dashboard_template_auth(user, rid)


def _read_dashboard_entry(c, user, rid):
    resp = c.finebi.get_entry_authority(user, [rid])
    data = (resp or {}).get("data") or {}
    entries = data.get("entry") if isinstance(data, dict) else None
    authority = (entries[0].get("authority") if entries else {}) or {}
    return {"data": [{"status": True, "data": authority}]}


def _read_role(c, user, rid):
    # user/detail 返回 roles；username 为模糊匹配，调用方需精确过滤
    return c.platform.query_user_detail(username=user)


def _read_department(c, user, rid):
    # user/detail 返回 departmentPosts[].department.fullPath
    return c.platform.query_user_detail(username=user)


# ---------- write ----------
def _write_folder(c, user, rid, payload):
    return c.finebi.set_folder_permission(user, rid, payload["authority"])


def _write_table(c, user, rid, payload):
    return c.finebi.set_table_permission(user, rid, payload["authority"])


def _write_field(c, user, rid, payload):
    return c.finebi.set_field_permission(user, rid, payload.get("authority", {}).get("biData", True))


def _write_row(c, user, rid, payload):
    return c.finebi.set_row_filter(user, rid, payload["filter"])


def _write_dashboard(c, user, rid, payload):
    authority = payload.get("authority", {})
    return c.finebi.set_dashboard_template_auth(
        user, rid, view=bool(authority.get("view", True)),
        export=bool(authority.get("export", False)))


def _write_dashboard_entry(c, user, rid, payload):
    return c.finebi.set_entry_authority(user, rid, payload["authority"])


def _write_publink(c, user, rid, payload):
    return c.finebi.set_publink_share(user, True)


def _write_dash_share(c, user, rid, payload):
    return c.finebi.share_dashboard([user], rid)


def _write_dashboard_data(c, user, rid, payload):
    return c.finebi.set_dashboard_data_permission(user, payload.get("entry", rid), True)


def _write_subject(c, user, rid, payload):
    authority = payload.get("authority", {})
    return c.finebi.set_subject_cooperation(
        user, rid, use=bool(authority.get("use", True)),
        edit=bool(authority.get("edit", False)))


def _write_role(c, user, rid, payload):
    add = list(dict.fromkeys([str(rid)] + [
        str(value) for value in (payload.get("keep_roles") or []) if value]))
    return c.platform.set_user_roles(user, add=add)


def _write_department(c, user, rid, payload):
    # rid 是部门路径 JSON 字符串（如 '["财务部", "财务二部"]'）
    add = list(dict.fromkeys([str(rid)] + [
        str(value) for value in (payload.get("keep_departments") or []) if value]))
    return c.platform.set_user_departments(user, add=add)


def _write_platform_module(c, user, rid, payload):
    authority = payload.get("authority") or {}
    return c.platform.set_user_platform_permission(
        user, rid, use=bool(authority.get("usePrivilege", True)),
        empower=bool(authority.get("empowerPrivilege", False)))


def _write_schedule(c, user, rid, payload):
    authority = payload.get("authority") or {}
    return c.platform.set_user_schedule_permission(
        user, rid, manage=bool(authority.get("managePrivilege", True)),
        empower=bool(authority.get("empowerPrivilege", False)))


# ---------- revoke ----------
def _revoke_folder(c, user, rid, payload):
    authority = {f: False for f in (payload.get("authority") or {})}
    return c.finebi.set_folder_permission(user, rid, authority)


def _revoke_table(c, user, rid, payload):
    authority = {f: False for f in (payload.get("authority") or {})}
    return c.finebi.set_table_permission(user, rid, authority)


def _revoke_field(c, user, rid, payload):
    return c.finebi.set_field_permission(user, rid, False)


def _revoke_row(c, user, rid, payload):
    return c.finebi.set_row_filter(user, rid, payload.get("filter") or {"type": "or", "filterValue": []})


def _revoke_dashboard(c, user, rid, payload):
    return c.finebi.set_dashboard_template_auth(user, rid, view=False, export=False)


def _revoke_dashboard_entry(c, user, rid, payload):
    return c.finebi.set_entry_authority(user, rid, {
        "viewPrivilege": False, "export": False,
        "editPrivilege": False, "empowerPrivilege": False})


def _revoke_publink(c, user, rid, payload):
    return c.finebi.set_publink_share(user, False)


def _revoke_dash_share(c, user, rid, payload):
    # 接口只支持授予，取消分享需后台操作
    raise NotImplementedError("dash_share 取消分享需人工处理")


def _revoke_dashboard_data(c, user, rid, payload):
    return c.finebi.set_dashboard_data_permission(user, payload.get("entry", rid), False)


def _revoke_subject(c, user, rid, payload):
    return c.finebi.set_subject_cooperation(user, rid, use=False, edit=False)


def _revoke_role(c, user, rid, payload):
    return c.platform.set_user_roles(user, remove=[rid])


def _revoke_department(c, user, rid, payload):
    return c.platform.set_user_departments(user, remove=[rid])


def _revoke_platform_module(c, user, rid, payload):
    return c.platform.set_user_platform_permission(user, rid, use=False, empower=False)


def _revoke_schedule(c, user, rid, payload):
    return c.platform.set_user_schedule_permission(user, rid, manage=False, empower=False)


HANDLERS: Dict[str, Handler] = {
    ResourceType.FOLDER: Handler(ResourceType.FOLDER, True, _read_folder, _write_folder, _revoke_folder),
    ResourceType.TABLE: Handler(ResourceType.TABLE, True, _read_table, _write_table, _revoke_table),
    ResourceType.FIELD: Handler(ResourceType.FIELD, True, _read_field, _write_field, _revoke_field),
    ResourceType.ROW: Handler(ResourceType.ROW, True, _read_row, _write_row, _revoke_row),
    ResourceType.DASHBOARD_VIEW: Handler(
        ResourceType.DASHBOARD_VIEW, True, _read_dashboard, _write_dashboard, _revoke_dashboard),
    ResourceType.DASHBOARD_EXPORT: Handler(
        ResourceType.DASHBOARD_EXPORT, True, _read_dashboard, _write_dashboard, _revoke_dashboard),
    ResourceType.DASHBOARD_ENTRY: Handler(
        ResourceType.DASHBOARD_ENTRY, True, _read_dashboard_entry,
        _write_dashboard_entry, _revoke_dashboard_entry),
    ResourceType.PUBLINK: Handler(ResourceType.PUBLINK, False, None, _write_publink, _revoke_publink),
    ResourceType.DASH_SHARE: Handler(ResourceType.DASH_SHARE, False, None, _write_dash_share, _revoke_dash_share),
    ResourceType.DASHBOARD_DATA: Handler(
        ResourceType.DASHBOARD_DATA, False, None, _write_dashboard_data, _revoke_dashboard_data),
    ResourceType.SUBJECT: Handler(ResourceType.SUBJECT, False, None, _write_subject, _revoke_subject),
    "role": Handler("role", True, _read_role, _write_role, _revoke_role),
    ResourceType.DEPARTMENT: Handler(
        ResourceType.DEPARTMENT, True, _read_department,
        _write_department, _revoke_department),
    PLATFORM_MODULE: Handler(PLATFORM_MODULE, False, None,
                             _write_platform_module, _revoke_platform_module),
    SCHEDULE: Handler(SCHEDULE, False, None, _write_schedule, _revoke_schedule),
}

NON_VERIFIABLE = {t for t, h in HANDLERS.items() if not h.verifiable}


def get_handler(resource_type: str) -> Handler:
    try:
        return HANDLERS[resource_type]
    except KeyError as exc:
        raise KeyError("未注册的资源处理器：%s" % resource_type) from exc
