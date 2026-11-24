# -*- coding: utf-8 -*-
"""集成测试共用的内存 Fake 客户端（不联网、可注入故障）。

Fake 的接口签名与 ``src/executor`` 中的真实客户端保持一致；响应结构按
``docs/finebi``、``docs/feishu`` 接口原文简化，仅保留执行器消费的字段：

- FineBI BI 权限接口：``{"data": [{"status": true, "data": ...}]}``；
- FineBI 平台接口：``{"data": {...}}``；
- 飞书审批：``{"data": {"instance_list": [...]}}`` / ``{"data": <instance>}``。

``FakeFineBI`` 额外提供故障注入（``fail_methods``）、写不生效
（``ignore_writes``）以及并发写检测（``concurrent_write_violations``），
供重试、写后复核、锁串行化等用例构造场景。
"""
from __future__ import annotations

import copy
import threading
import time
from typing import Any, Dict, List


class FakeFineBI:
    """内存版 FineBI 客户端（BI 权限 + 资源交接）。"""

    def __init__(self) -> None:
        self.calls: List[tuple] = []
        self.folder: Dict[tuple, Dict[str, Any]] = {}
        self.table: Dict[tuple, Dict[str, Any]] = {}
        self.field: Dict[tuple, bool] = {}
        self.row: Dict[tuple, Dict[str, Any]] = {}
        self.dash: Dict[tuple, Dict[str, Any]] = {}
        self.publink: Dict[str, bool] = {}
        self.subject: Dict[tuple, Dict[str, bool]] = {}
        self.dashboard_data: Dict[tuple, bool] = {}
        self.dash_share: Dict[tuple, bool] = {}
        self.handover_start_args: Dict[str, Any] = {}
        self.fail_methods: Dict[str, Any] = {}
        self.ignore_writes = False
        self.write_delay = 0.0
        self.concurrent_write_violations = 0
        self.active_writes = 0
        self._lock = threading.RLock()
        self._trace_seq = 0

    # ---------- 内部工具 ----------
    def _record(self, name: str, *args: Any) -> None:
        with self._lock:
            self.calls.append((name,) + args)

    def _maybe_fail(self, method: str) -> None:
        with self._lock:
            value = self.fail_methods.get(method)
            if value is None:
                return
            if isinstance(value, list):
                if not value:
                    return
                exc = value.pop(0)
            else:
                exc = value
        raise exc

    def _new_trace(self) -> str:
        with self._lock:
            self._trace_seq += 1
            return "trace-fake-%04d" % self._trace_seq

    def _wrap(self, data: Any) -> Dict[str, Any]:
        return {"traceId": self._new_trace(),
                "data": [{"status": True, "data": copy.deepcopy(data)}]}

    def _begin_write(self) -> None:
        with self._lock:
            self.active_writes += 1
            if self.active_writes > 1:
                self.concurrent_write_violations += 1
            delay = self.write_delay
        if delay:
            time.sleep(delay)

    def _end_write(self) -> None:
        with self._lock:
            self.active_writes -= 1

    def count(self, prefix: str) -> int:
        with self._lock:
            return sum(1 for call in self.calls if call[0].startswith(prefix))

    def call_args(self, name: str) -> List[tuple]:
        with self._lock:
            return [call for call in self.calls if call[0] == name]

    # ---------- 文件夹（pack） ----------
    def get_folder_permission(self, user: str, pack_id: str) -> Dict[str, Any]:
        self._record("get_folder", user, pack_id)
        self._maybe_fail("get_folder_permission")
        return self._wrap(self.folder.get((user, pack_id), {}))

    def set_folder_permission(self, user: str, pack_id: str,
                              authority: Dict[str, bool]) -> Dict[str, Any]:
        self._record("set_folder", user, pack_id, dict(authority))
        self._maybe_fail("set_folder_permission")
        self._begin_write()
        try:
            if not self.ignore_writes:
                self.folder[(user, pack_id)] = dict(authority)
        finally:
            self._end_write()
        return {"traceId": "trace-folder",
                "data": [{"status": True, "data": "success"}]}

    # ---------- 数据集（table） ----------
    def get_table_permission(self, user: str, table_name: str) -> Dict[str, Any]:
        self._record("get_table", user, table_name)
        self._maybe_fail("get_table_permission")
        return self._wrap(self.table.get((user, table_name), {}))

    def set_table_permission(self, user: str, table_name: str,
                             authority: Dict[str, bool]) -> Dict[str, Any]:
        self._record("set_table", user, table_name, dict(authority))
        self._maybe_fail("set_table_permission")
        self._begin_write()
        try:
            if not self.ignore_writes:
                self.table[(user, table_name)] = dict(authority)
        finally:
            self._end_write()
        return {"data": [{"status": True, "data": "success"}]}

    # ---------- 列权限（field） ----------
    def get_field_permission(self, user: str, field_id: str) -> Dict[str, Any]:
        self._record("get_field", user, field_id)
        self._maybe_fail("get_field_permission")
        return self._wrap({"biData": bool(self.field.get((user, field_id), False))})

    def set_field_permission(self, user: str, field_id: str,
                             bi_data: bool = True) -> Dict[str, Any]:
        self._record("set_field", user, field_id, bool(bi_data))
        self._maybe_fail("set_field_permission")
        self._begin_write()
        try:
            if not self.ignore_writes:
                self.field[(user, field_id)] = bool(bi_data)
        finally:
            self._end_write()
        return {"ok": True}

    # ---------- 行权限（get 返回 set 结构，等价于本执行器写回格式） ----------
    def get_row_filter(self, user: str, table_name: str) -> Dict[str, Any]:
        self._record("get_row", user, table_name)
        self._maybe_fail("get_row_filter")
        return self._wrap(self.row.get((user, table_name), ""))

    def set_row_filter(self, user: str, table_name: str,
                       row_filter: Dict[str, Any]) -> Dict[str, Any]:
        self._record("set_row", user, table_name, copy.deepcopy(row_filter))
        self._maybe_fail("set_row_filter")
        self._begin_write()
        try:
            if not self.ignore_writes:
                self.row[(user, table_name)] = copy.deepcopy(row_filter)
        finally:
            self._end_write()
        return {"ok": True}

    # ---------- 仪表板模板认证（view/export 互斥） ----------
    def get_dashboard_template_auth(self, user: str,
                                    bi_report_id: str) -> Dict[str, Any]:
        self._record("get_dash", user, bi_report_id)
        self._maybe_fail("get_dashboard_template_auth")
        return self._wrap(self.dash.get((user, bi_report_id), {}))

    def set_dashboard_template_auth(self, user: str, bi_report_id: str,
                                    view: bool, export: bool = False) -> Dict[str, Any]:
        if export and not view:
            # 与 FineBIClient 的本地校验保持一致：导出必须同时有查看权限
            raise ValueError("导出权限必须同时开启查看权限")
        self._record("set_dash", user, bi_report_id, bool(view), bool(export))
        self._maybe_fail("set_dashboard_template_auth")
        self._begin_write()
        try:
            if not self.ignore_writes:
                self.dash[(user, bi_report_id)] = {"view": bool(view),
                                                   "export": bool(export)}
        finally:
            self._end_write()
        return {"ok": True}

    # ---------- 四类不可复核权限 ----------
    def set_publink_share(self, user: str, enabled: bool = True) -> Dict[str, Any]:
        self._record("set_publink", user, bool(enabled))
        self._maybe_fail("set_publink_share")
        if not self.ignore_writes:
            self.publink[user] = bool(enabled)
        return {"ok": True}

    def share_dashboard(self, users: List[str], bi_report_id: str) -> Dict[str, Any]:
        self._record("share_dash", tuple(users), bi_report_id)
        self._maybe_fail("share_dashboard")
        if not self.ignore_writes:
            for user in users:
                self.dash_share[(user, bi_report_id)] = True
        return {"ok": True}

    def set_dashboard_data_permission(self, user: str, entry: str,
                                      bi_data: bool = True) -> Dict[str, Any]:
        self._record("set_dashboard_data", user, entry, bool(bi_data))
        self._maybe_fail("set_dashboard_data_permission")
        if not self.ignore_writes:
            self.dashboard_data[(user, entry)] = bool(bi_data)
        return {"ok": True}

    def set_subject_cooperation(self, user: str, subject: str,
                                use: bool = True, edit: bool = False) -> Dict[str, Any]:
        self._record("set_subject", user, subject, bool(use), bool(edit))
        self._maybe_fail("set_subject_cooperation")
        if not self.ignore_writes:
            self.subject[(user, subject)] = {"use": bool(use), "edit": bool(edit)}
        return {"ok": True}

    # ---------- 资源交接 ----------
    def handover_analysis(self, user: str) -> Dict[str, Any]:
        self._record("handover_analysis", user)
        self._maybe_fail("handover_analysis")
        return {"data": {
            "folders": [{"id": "p-handover", "folders": [], "tables": []}],
            "tables": [{"id": "t-handover"}],
            "subjects": [{"id": "s-handover"}],
        }}

    def handover_public(self, user: str) -> Dict[str, Any]:
        self._record("handover_public", user)
        self._maybe_fail("handover_public")
        return {"data": {"folders": [], "tables": [], "subjects": []}}

    def handover_start(self, sender: str, accepter: str,
                       pack_ids: List[str] = None, table_names: List[str] = None,
                       subject_ids: List[str] = None,
                       analysis_pack_ids: List[str] = None) -> Dict[str, Any]:
        self._record("handover_start", sender, accepter)
        self._maybe_fail("handover_start")
        self.handover_start_args = {
            "sender": sender, "accepter": accepter,
            "pack_ids": list(pack_ids or []),
            "table_names": list(table_names or []),
            "subject_ids": list(subject_ids or []),
            "analysis_pack_ids": list(analysis_pack_ids or []),
        }
        return {"data": {"failResource": []}}


class FakePlatform:
    """内存版 FineBI 平台客户端（用户/角色/启停）。"""

    def __init__(self) -> None:
        self.calls: List[tuple] = []
        self.roles: Dict[str, List[str]] = {}
        self.enabled: Dict[str, bool] = {}
        self.fail_methods: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def _record(self, name: str, *args: Any) -> None:
        with self._lock:
            self.calls.append((name,) + args)

    def _maybe_fail(self, method: str) -> None:
        with self._lock:
            value = self.fail_methods.get(method)
            if value is None:
                return
            if isinstance(value, list):
                if not value:
                    return
                exc = value.pop(0)
            else:
                exc = value
        raise exc

    def query_user_detail(self, username: str = "", email: str = "",
                          mobile: str = "", page: int = 1,
                          count: int = 20) -> Dict[str, Any]:
        self._record("query_user", username)
        self._maybe_fail("query_user_detail")
        roles = [{"id": "r-" + name, "name": name}
                 for name in self.roles.get(username, [])]
        return {"data": {"total": 1,
                         "items": [{"username": username, "roles": roles}]}}

    def set_user_roles(self, user: str, add: List[str] = None,
                       remove: List[str] = None) -> Dict[str, Any]:
        self._record("set_roles", user, list(add or []), list(remove or []))
        self._maybe_fail("set_user_roles")
        names = self.roles.setdefault(user, [])
        for role in add or []:
            if role not in names:
                names.append(role)
        for role in remove or []:
            if role in names:
                names.remove(role)
        return {"ok": True}

    def set_user_enabled(self, user: str, enabled: bool) -> Dict[str, Any]:
        self._record("set_enabled", user, bool(enabled))
        self._maybe_fail("set_user_enabled")
        self.enabled[user] = bool(enabled)
        return {"ok": True}


class FakeFeishu:
    """内存版飞书审批客户端：只实现执行器用到的实例查询与详情。"""

    def __init__(self) -> None:
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.calls: List[tuple] = []

    def add_instance(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        self.instances[instance["instance_code"]] = instance
        return instance

    def query_instances(self, approval_code: str, status: str = "APPROVED",
                        start_ms: int = None, end_ms: int = None,
                        page_size: int = 100,
                        page_token: str = "") -> Dict[str, Any]:
        self.calls.append(("query_instances", approval_code, status))
        items = [{"instance": {"code": code}}
                 for code, inst in self.instances.items()
                 if not status or inst.get("status") == status]
        return {"code": 0,
                "data": {"instance_list": items, "has_more": False}}

    def get_instance(self, instance_code: str,
                     locale: str = "zh-CN") -> Dict[str, Any]:
        self.calls.append(("get_instance", instance_code))
        if instance_code not in self.instances:
            return {"code": 40004, "msg": "instance not found"}
        return {"code": 0, "data": copy.deepcopy(self.instances[instance_code])}

    def count(self, prefix: str) -> int:
        return sum(1 for call in self.calls if call[0].startswith(prefix))


class FakeNotifier:
    """记录通知调用，供断言“失败/转人工/存量未纳管已通知”。"""

    def __init__(self) -> None:
        self.admin_calls: List[tuple] = []
        self.user_calls: List[tuple] = []

    def notify_admins(self, title: str, content: str, link: str = "",
                      color: str = "orange") -> None:
        self.admin_calls.append((title, content))

    def notify_user(self, open_id: str, title: str, content: str,
                    link: str = "", color: str = "blue") -> None:
        self.user_calls.append((open_id, title, content))
