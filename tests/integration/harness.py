# -*- coding: utf-8 -*-
"""集成测试夹具：真实服务编排 + Fake 客户端 + 临时 SQLite 台账。

只使用被测项目的真实实现（FormParser / PermissionService / RevokeService /
ExpireService / OffboardService / ReconcileService / ApprovalPoller / JobService /
Storage / ResourceLock），仅下游 FineBI、飞书与通知替换为内存 Fake，
因此覆盖的是“审批实例 → 解析 → 授权 → 台账 → 回收/到期/离职/对账/重试”的真实链路。

除 ``tests/integration`` 内部复用外，``tests/test_acceptance.py`` 也复用本夹具做验收映射。
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, List

from executor.feishu.form_parser import FormParser
from executor.locks import ResourceLock
from executor.models import PermissionRequest
from executor.services.expire import ExpireService
from executor.services.grant import PermissionService
from executor.services.jobs import (KIND_GRANT, KIND_REVOKE, JobService)
from executor.services.offboard import OffboardService
from executor.services.poller import ApprovalPoller
from executor.services.reconcile import ReconcileService
from executor.services.revoke import RevokeService
from executor.storage import Storage

from .fakes import FakeFeishu, FakeFineBI, FakeNotifier, FakePlatform

# POC-3 待实测的 filterType 映射（测试用固定值，与 test_grant_v2 一致）
TYPE_MAP = {35: "or", 34: "and", 10: "strIn", 12: "strNotIn"}
FULL_AUTHORITY = ("usePrivilege", "managePrivilege", "empowerPrivilege",
                  "biData", "biView")

# 与 config/config.example.json 对齐的表单映射（仅资源 ID 换成测试值）
MAPPING: Dict[str, Any] = {
    "field_user": "FineBI账号",
    "field_type": "申请类型",
    "field_resource": "数据资源",
    "field_actions": "权限项",
    "field_days": "使用期限",
    "field_scope": "数据范围",
    "field_role": "角色",
    "default_days": 90,
    "resource_type_map": {
        "文件夹使用": "folder",
        "数据集使用": "table",
        "行权限": "row",
        "列权限": "field",
        "仪表板查看": "dashboard_view",
        "仪表板导出": "dashboard_export",
        "公共链接": "publink",
        "仪表板分享": "dash_share",
        "目录组件数据": "dashboard_data",
        "主题协作": "subject",
        "角色": "role",
    },
    "action_map": {
        "使用": "use",
        "管理": "manage",
        "授权": "empower",
        "组件数据": "component",
        "查看": "view",
        "导出": "export",
        "编辑": "edit",
    },
    "row_field_ids": {"大区": "t_region", "渠道": "t_channel"},
    "resources": {
        "销售文件夹": {"resource_type": "folder", "resource_id": "p-001"},
        "销售数据集": {"resource_type": "table", "resource_id": "t-001"},
        "客户手机号字段": {"resource_type": "field", "resource_id": "f-phone"},
        "销售仪表板": {"resource_type": "dashboard_view", "resource_id": "d-001"},
    },
}


# ---------------------------------------------------------------------------
# 构造工具
# ---------------------------------------------------------------------------
def widget(name: str, value: Any, widget_type: str = "input",
           custom_id: str = "") -> Dict[str, Any]:
    item = {"id": "w-" + (custom_id or name), "name": name,
            "type": widget_type, "value": value}
    if custom_id:
        item["custom_id"] = custom_id
    return item


def resource(name: str, resource_id: str, resource_type: str) -> Dict[str, Any]:
    return {"资源名称": name, "资源ID": resource_id, "资源类型": resource_type}


def form(user: str = "10086", resources: List[Dict[str, Any]] = None,
         actions: List[str] = None, days="90天", scope: str = "",
         role: str = "", apply_type: str = "") -> List[Dict[str, Any]]:
    """构造标准审批表单控件列表。"""
    widgets = [
        widget("FineBI账号", user),
        widget("数据资源", list(resources or []), widget_type="mutableGroup"),
        widget("权限项", list(actions or []), widget_type="checkbox"),
        widget("使用期限", days, widget_type="radio"),
    ]
    if scope:
        widgets.append(widget("数据范围", scope, widget_type="textarea"))
    if role:
        widgets.append(widget("角色", role))
    if apply_type:
        widgets.append(widget("申请类型", apply_type, widget_type="radio"))
    return widgets


def instance(instance_code: str, form_widgets: List[Dict[str, Any]],
             status: str = "APPROVED", **extra: Any) -> Dict[str, Any]:
    """构造 ``GET /approval/v4/instances/:instance_code`` 的 data 结构。"""
    data = {
        "instance_code": instance_code,
        "status": status,
        "serial_number": "SER-" + instance_code,
        "approval_name": "FineBI 数据权限申请",
        "user_id": "ou-test-user",
        "open_id": "ou-test-open",
        "form": json.dumps(form_widgets, ensure_ascii=False),
    }
    data.update(extra)
    return data


def future(seconds: float = 61.0) -> str:
    return (datetime.now().astimezone()
            + timedelta(seconds=float(seconds))).isoformat(timespec="seconds")


def full_authority(**overrides: bool) -> Dict[str, bool]:
    """五个 authority 字段齐全的现状（模拟 FineBI get 返回）。"""
    base = {field: False for field in FULL_AUTHORITY}
    base.update(overrides)
    return base


def folder_request(**kwargs: Any) -> PermissionRequest:
    base = dict(user="10086", resource_type="folder", resource_id="p-001",
                actions=["use"], days=90)
    base.update(kwargs)
    return PermissionRequest(**base)


def table_request(**kwargs: Any) -> PermissionRequest:
    base = dict(user="10086", resource_type="table", resource_id="t-001",
                actions=["use"], days=90)
    base.update(kwargs)
    return PermissionRequest(**base)


def row_request(rules: List[Dict[str, Any]], **kwargs: Any) -> PermissionRequest:
    base = dict(user="10086", resource_type="row", resource_id="t-001",
                actions=["use"], data_scope={"rules": rules}, days=90)
    base.update(kwargs)
    return PermissionRequest(**base)


def row_rule(values: List[str], field_id: str = "t_region") -> Dict[str, Any]:
    return {"type": "strIn", "fieldId": field_id, "filterValue": list(values)}


# ---------------------------------------------------------------------------
# 夹具
# ---------------------------------------------------------------------------
class IntegrationHarness:
    """一套隔离的端到端运行环境（临时库 + Fake 下游 + 真实服务编排）。"""

    def __init__(self, adopt_existing: bool = False,
                 row_clear_strategy: str = "manual",
                 dry_run: bool = False,
                 type_map: Dict[Any, str] = None,
                 lock_wait: float = 5.0) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "executor.db")
        self.storage = Storage(self.db_path)
        self.finebi = FakeFineBI()
        self.platform = FakePlatform()
        self.feishu = FakeFeishu()
        self.notifier = FakeNotifier()
        self.type_map = dict(TYPE_MAP if type_map is None else type_map)
        self.dry_run = dry_run
        self._closed = False

        self.jobs = JobService(self.storage, notifier=self.notifier)
        self.lock = ResourceLock(self.db_path, ttl=120, wait=lock_wait,
                                 poll_interval=0.05)
        common = dict(platform=self.platform, dry_run=dry_run, lock=self.lock,
                      notifier=self.notifier, jobs=self.jobs, type_map=self.type_map)
        self.permission = PermissionService(
            self.finebi, self.storage, max_days=365,
            adopt_existing=adopt_existing, **common)
        self.revoke = RevokeService(
            self.finebi, self.storage, row_clear_strategy=row_clear_strategy,
            **common)
        self.expire = ExpireService(self.revoke, self.storage,
                                    notifier=self.notifier)
        self.offboard = OffboardService(
            self.finebi, self.storage, platform=self.platform,
            revoke_service=self.revoke, dry_run=dry_run, notifier=self.notifier)
        self.reconcile = ReconcileService(
            self.finebi, self.storage, platform=self.platform,
            type_map=self.type_map)
        # 未配置 filterType 映射的对账实例：行权限应标 unverifiable（POC-3 未结论）
        self.reconcile_unmapped = ReconcileService(
            self.finebi, self.storage, platform=self.platform, type_map=None)
        self.parser = FormParser(MAPPING, resources=MAPPING["resources"])
        self.poller = ApprovalPoller(self.feishu, self.permission, self.storage,
                                     approval_code="APPROVAL-001",
                                     mapper=self.parser)
        self._register_runtime_jobs()

    # ---------- 与 runtime.build 一致的 jobs 接线（覆盖服务默认回放） ----------
    def _register_runtime_jobs(self) -> None:
        def grant_job(request_id: str) -> Any:
            row = self.storage.get_request(request_id)
            if not row:
                raise ValueError("request not found: %s" % request_id)
            return self.permission.grant(
                PermissionRequest.from_dict(row["payload"]))

        def revoke_job(ledger_id: str) -> Any:
            ledger = self.storage.get_ledger(ledger_id)
            if not ledger:
                raise ValueError("ledger not found: %s" % ledger_id)
            return self.revoke.revoke_ledger(ledger, reason="重试回收")

        self.jobs.register_handler(KIND_GRANT, grant_job)
        self.jobs.register_handler(KIND_REVOKE, revoke_job)

    # ---------- 审批实例 ----------
    def add_instance(self, instance_code: str,
                     form_widgets: List[Dict[str, Any]],
                     status: str = "APPROVED", **extra: Any) -> Dict[str, Any]:
        data = instance(instance_code, form_widgets, status=status, **extra)
        self.feishu.add_instance(data)
        return data

    def grant_instance(self, instance_code: str,
                       form_widgets: List[Dict[str, Any]],
                       status: str = "APPROVED", **extra: Any):
        """审批实例 JSON → FormParser.parse_instance → grant，返回 GrantResult。"""
        request = self.parser.parse_instance(
            instance(instance_code, form_widgets, status=status, **extra))
        return self.permission.grant(request)

    def poll_once(self) -> Dict[str, Any]:
        return self.poller.run_once()

    # ---------- 台账 / 任务 / 日志查询 ----------
    def ledger_rows(self, user: str = None) -> List[Dict[str, Any]]:
        return self.storage.active_ledger(user=user)

    def all_ledger_rows(self) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM ledger ORDER BY created_at").fetchall()
        return [dict(row) for row in rows]

    def request_rows(self) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM requests ORDER BY created_at").fetchall()
        return [dict(row) for row in rows]

    def request_row(self, request_id: str) -> Dict[str, Any]:
        return self.storage.get_request(request_id)

    def item_rows(self, request_id: str) -> List[Dict[str, Any]]:
        return self.storage.list_request_items(request_id)

    def job_rows(self) -> List[Dict[str, Any]]:
        rows = self.storage.conn.execute(
            "SELECT * FROM jobs ORDER BY created_at").fetchall()
        return [dict(row) for row in rows]

    def log_actions(self, limit: int = 100) -> List[str]:
        return [row["action"] for row in self.storage.recent_logs(limit)]

    # ---------- 时间推进 ----------
    @staticmethod
    def due_after(job: Dict[str, Any], seconds: float = 1.0) -> str:
        base = datetime.fromisoformat(job["next_run_at"])
        return (base + timedelta(seconds=float(seconds))).isoformat(timespec="seconds")

    # ---------- 清理 ----------
    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.storage.close()
        finally:
            self.tmp.cleanup()

    def __enter__(self) -> "IntegrationHarness":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


__all__ = [
    "TYPE_MAP", "MAPPING", "FULL_AUTHORITY",
    "widget", "resource", "form", "instance", "future", "full_authority",
    "folder_request", "table_request", "row_request", "row_rule",
    "IntegrationHarness",
]
