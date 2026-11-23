"""审批轮询：拉取已通过的审批实例，解析表单，触发授权。

表单字段映射需要按客户审批定义调整：见 FormMapper.mapping 配置。
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from ..models import PermissionRequest
from ..storage import Storage
from .jobs import KIND_GRANT

LOGGER = logging.getLogger(__name__)


def flatten_form(form: Any) -> Dict[str, Any]:
    """把审批实例的 form（控件 JSON 字符串）拍平为 {控件名: 值}。"""
    if isinstance(form, str):
        try:
            form = json.loads(form)
        except json.JSONDecodeError:
            return {}
    values: Dict[str, Any] = {}

    def visit(items: Any) -> None:
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("custom_id")
            value = item.get("value")
            if name:
                values[str(name)] = value
            if isinstance(value, (dict, list)):
                visit(value.get("children") if isinstance(value, dict) else value)
            visit(item.get("children"))

    visit(form)
    return values


class FormMapper:
    def __init__(self, mapping: Optional[Dict[str, Any]] = None):
        self.mapping = mapping or {}

    def parse(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        values = flatten_form(instance.get("form"))
        values["_instance_code"] = instance.get("instance_code") or instance.get("uuid")
        values["_status"] = instance.get("status")
        return values

    def to_request(self, values: Dict[str, Any]) -> PermissionRequest:
        m = self.mapping
        resources = m.get("resources", {})
        resource_key = values.get(m.get("field_resource", "资源"))
        resource = resources.get(resource_key, {}) if resource_key else {}
        resource_type = resource.get("resource_type") or values.get(m.get("field_type", "申请类型"))
        if isinstance(resource_type, str):
            resource_type = m.get("resource_type_map", {}).get(resource_type, resource_type)
        actions_raw = values.get(m.get("field_actions", "权限项")) or []
        if isinstance(actions_raw, str):
            actions_raw = [actions_raw]
        action_map = m.get("action_map", {})
        actions = [action_map.get(a, a) for a in actions_raw]
        scope = self._build_scope(values)
        days = values.get(m.get("field_days", "期限"))
        try:
            days = int(str(days).rstrip("天"))
        except (TypeError, ValueError):
            days = int(m.get("default_days", 90))
        return PermissionRequest(
            user=str(values.get(m.get("field_user", "FineBI账号")) or ""),
            resource_type=str(resource_type or ""),
            resource_id=str(resource.get("resource_id") or values.get("_resource_id") or ""),
            actions=actions,
            data_scope=scope,
            role=values.get(m.get("field_role", "角色")) or None,
            days=days,
            source=str(values.get("_instance_code") or ""),
        )

    def _build_scope(self, values: Dict[str, Any]) -> Dict[str, Any]:
        raw = values.get(self.mapping.get("field_scope", "数据范围")) or ""
        if not raw:
            return {}
        field_ids = self.mapping.get("row_field_ids", {})
        rules: List[Dict[str, Any]] = []
        for part in str(raw).replace("；", ";").split(";"):
            if "=" not in part:
                continue
            dimension, vals = part.split("=", 1)
            dimension = dimension.strip()
            rule = {
                "type": "strIn",
                "fieldId": field_ids.get(dimension, dimension),
                "filterValue": [v.strip() for v in vals.replace("，", ",").split(",") if v.strip()],
            }
            if rule["filterValue"]:
                rules.append(rule)
        return {"rules": rules}


class ApprovalPoller:
    def __init__(self, feishu, permission_service, storage: Storage,
                 approval_code: str, mapper: Optional[FormMapper] = None,
                 since_hours: int = 72, page_size: int = 100):
        self.feishu = feishu
        self.permission_service = permission_service
        self.storage = storage
        self.approval_code = approval_code
        self.mapper = mapper or FormMapper()
        self.since_hours = since_hours
        self.page_size = page_size

    def _fetch_instances(self, start_ms: int, end_ms: int) -> List[Dict[str, Any]]:
        """分页拉取审批实例；单页 page_size 上限 100，避免漏单。"""
        items: List[Dict[str, Any]] = []
        page_token = ""
        for _ in range(50):
            resp = self.feishu.query_instances(
                self.approval_code, status="APPROVED",
                start_ms=start_ms, end_ms=end_ms,
                page_size=self.page_size, page_token=page_token)
            data = (resp or {}).get("data") or {}
            items.extend(data.get("instance_list") or [])
            page_token = str(data.get("page_token") or "")
            if not data.get("has_more") or not page_token:
                break
        return items

    def run_once(self) -> Dict[str, Any]:
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - self.since_hours * 3600 * 1000
        items = self._fetch_instances(start_ms, now_ms)
        summary = {"found": len(items), "granted": 0, "skipped": 0, "failed": 0, "errors": []}
        for item in items:
            instance = item.get("instance") or {}
            code = instance.get("code")
            if not code:
                continue
            if self.storage.request_status(code) == "done":
                summary["skipped"] += 1
                continue
            if self._has_manual_job(code):
                # D-03：已转人工的实例不再重复执行 grant / 重复插入人工待办
                summary["skipped"] += 1
                continue
            try:
                detail = self.feishu.get_instance(code)
                data = (detail or {}).get("data") or {}
                if hasattr(self.mapper, "parse_instance"):
                    # V1.1 §1.2：执行前以实例详情为准，非 APPROVED 不执行
                    req = self.mapper.parse_instance(data, require_approved=True)
                else:
                    values = self.mapper.parse(data)
                    req = self.mapper.to_request(values)
                result = self.permission_service.grant(req)
                if result.status == "granted":
                    summary["granted"] += 1
                elif result.status == "skipped":
                    summary["skipped"] += 1
                else:
                    # 条目级失败/部分成功（grant 不抛异常，返回 GrantResult）
                    summary["failed"] += 1
                    summary["errors"].append({
                        "instance": code,
                        "status": result.status,
                        "error": "; ".join(
                            str(item.get("error") or item.get("reason") or "")
                            for item in result.item_results
                            if item.get("status") == "failed")})
            except Exception as exc:  # noqa: BLE001 - 单条失败不影响其他
                summary["failed"] += 1
                summary["errors"].append({"instance": code, "error": str(exc)})
                LOGGER.exception("处理审批实例失败：%s", code)
                self.storage.log("ERROR", "poll", "处理审批实例失败：%s" % exc,
                                 {"instance": code})
        return summary

    def _has_manual_job(self, instance_code: str) -> bool:
        """该审批实例是否已有未闭环的人工待办（D-03）。

        通过 ``requests.instance_code -> jobs.ref_id=requests.id`` 关联查询，
        不改变 retry 队列语义：只有 ``status='manual'`` 才跳过轮询，
        ``queued/running`` 的重试任务仍按 jobs 调度执行。
        """
        try:
            row = self.storage.conn.execute(
                "SELECT 1 FROM jobs j JOIN requests r ON r.id = j.ref_id "
                "WHERE r.instance_code=? AND j.kind=? AND j.status='manual' LIMIT 1",
                (instance_code, KIND_GRANT)).fetchone()
            return row is not None
        except Exception:  # noqa: BLE001 - 查询失败不影响轮询主流程
            LOGGER.warning("查询实例 %s 的人工待办失败", instance_code, exc_info=True)
            return False
