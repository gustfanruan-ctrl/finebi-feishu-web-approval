# -*- coding: utf-8 -*-
"""飞书多维表格「权限申请台账」写入。

字段在 Bitable 表里全部用文本类型，便于跨版本稳定写入：
单号 / 日期 / 自增键 / 申请人 / 申请人账号 / 权限内容 / 权限时间 /
申请类型 / 状态 / 审批人 / 申请时间 / 请求ID / 详情链接 / 最近操作
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

FIELD_NAMES = ["单号", "日期", "自增键", "申请人", "申请人账号", "权限内容",
               "权限时间", "申请类型", "状态", "审批人", "申请时间", "请求ID",
               "详情链接", "最近操作"]
PRIMARY_FIELD = "单号"

CATEGORY_LABELS = {
    "dashboard": "仪表板",
    "public_data": "公共数据",
    "membership": "角色/部门",
    "admin": "定时调度",
}
STATUS_LABELS = {
    "pending": "待审批",
    "approved": "已通过",
    "rejected": "已驳回",
    "withdrawn": "已撤回",
    "granting": "授权中",
    "done": "已授权",
    "failed": "授权失败",
}


def request_fields(request: Dict[str, Any], action: str = "",
                   link: str = "") -> Dict[str, Any]:
    """把一条 web 申请转换为 Bitable 字段。"""
    payload = request.get("payload") or {}
    applicant = request.get("applicant") or {}
    steps = request.get("steps") or []
    approvers = [str((s.get("approver") or {}).get("name")
                     or (s.get("approver") or {}).get("id") or "")
                 for s in steps]
    approvers = [x for x in approvers if x]
    created = str(request.get("created_at") or "")
    request_date = str(payload.get("request_date") or created[:10] or "")
    return {
        PRIMARY_FIELD: str(payload.get("request_no") or request.get("id") or ""),
        "日期": request_date,
        "自增键": str(payload.get("serial_text") or ""),
        "申请人": str(applicant.get("name") or ""),
        "申请人账号": str(payload.get("applicant_account") or ""),
        "权限内容": str(payload.get("permission_content")
                       or payload.get("resource_name") or ""),
        "权限时间": str(payload.get("permission_time") or ""),
        "申请类型": CATEGORY_LABELS.get(str(request.get("category") or ""),
                                        str(request.get("category") or "")),
        "状态": STATUS_LABELS.get(str(request.get("status") or ""),
                                  str(request.get("status") or "")),
        "审批人": "、".join(approvers),
        "申请时间": str(request.get("created_at") or "")[:16].replace("T", " "),
        "请求ID": str(request.get("id") or ""),
        "详情链接": str(link or ""),
        "最近操作": str(action or ""),
    }


class BitableLedger:
    """多维表格写入器：首次使用会自动补齐字段。"""

    def __init__(self, feishu, app_token: str, table_id: str,
                 dry_run: bool = False):
        self.feishu = feishu
        self.app_token = str(app_token or "").strip()
        self.table_id = str(table_id or "").strip()
        self.dry_run = dry_run

    def enabled(self) -> bool:
        return bool(self.feishu and self.app_token and self.table_id)

    def ensure_schema(self) -> Dict[str, Any]:
        """确保字段存在；主字段名统一为「单号」。返回变更摘要。"""
        if not self.enabled():
            return {"enabled": False}
        result: Dict[str, Any] = {"enabled": True, "created": [], "renamed": False}
        resp = self.feishu.list_bitable_fields(self.app_token, self.table_id)
        items = ((resp or {}).get("data") or {}).get("items") or []
        primary = next((f for f in items if f.get("is_primary")), None)
        if primary and primary.get("field_name") != PRIMARY_FIELD and not self.dry_run:
            self.feishu.update_bitable_field(
                self.app_token, self.table_id, primary["field_id"],
                field_name=PRIMARY_FIELD, field_type=1)
            result["renamed"] = True
        existing = {str(f.get("field_name") or "") for f in items}
        for name in FIELD_NAMES:
            if name in existing:
                continue
            if not self.dry_run:
                self.feishu.create_bitable_field(
                    self.app_token, self.table_id, name, field_type=1)
            result["created"].append(name)
        return result

    def upsert(self, request: Dict[str, Any], record_id: str = "",
               action: str = "", link: str = "") -> str:
        """写入或更新一条台账记录，返回 record_id。"""
        if not self.enabled():
            return ""
        fields = request_fields(request, action=action, link=link)
        if self.dry_run:
            LOGGER.info("[DRY-RUN][bitable] %s %s", action, fields.get(PRIMARY_FIELD))
            return record_id
        if record_id:
            self.feishu.update_record(self.app_token, self.table_id, record_id, fields)
            return record_id
        resp = self.feishu.create_record(self.app_token, self.table_id, fields)
        data = (resp or {}).get("data") or {}
        record = data.get("record") or {}
        return str(record.get("record_id") or data.get("record_id") or "")


def bitable_status(ledger: Optional[BitableLedger]) -> Dict[str, Any]:
    if ledger is None:
        return {"enabled": False}
    return {"enabled": ledger.enabled(), "app_token": bool(ledger.app_token),
            "table_id": ledger.table_id}
