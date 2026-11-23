"""数据模型与行权限规则合并（纯函数，便于单测）。"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


class ResourceType:
    FOLDER = "folder"                    # 公共数据文件夹（pack）
    TABLE = "table"                      # 公共数据数据集（table）
    FIELD = "field"                      # 列权限（field）
    ROW = "row"                          # 行权限（row filter）
    DASHBOARD_VIEW = "dashboard_view"    # 仪表板查看（模板认证）
    DASHBOARD_EXPORT = "dashboard_export"  # 仪表板查看 + 导出
    DASHBOARD_ENTRY = "dashboard_entry"  # 仪表板目录权限（entry，控制目录可见/导出）
    PUBLINK = "publink"                  # 公共链接分享功能
    DASH_SHARE = "dash_share"            # 仪表板分享到目录
    DASHBOARD_DATA = "dashboard_data"    # 目录组件数据权限
    SUBJECT = "subject"                  # 我的分析主题协作
    ROLE = "role"                        # FineBI 平台角色（平台公共接口，无 BI 查询接口）
    DEPARTMENT = "department"            # FineBI 部门成员关系（平台公共接口）

    ALL = (FOLDER, TABLE, FIELD, ROW, DASHBOARD_VIEW, DASHBOARD_EXPORT,
           DASHBOARD_ENTRY, PUBLINK, DASH_SHARE, DASHBOARD_DATA, SUBJECT, ROLE,
           DEPARTMENT)


class Action:
    USE = "use"
    MANAGE = "manage"
    EMPOWER = "empower"
    COMPONENT = "component"
    VIEW = "view"
    EXPORT = "export"
    SHARE = "share"
    EDIT = "edit"


# 权限项 -> FineBI v3 authority 字段
AUTHORITY_FIELDS = {
    Action.USE: "usePrivilege",
    Action.MANAGE: "managePrivilege",
    Action.EMPOWER: "empowerPrivilege",
    Action.COMPONENT: "biData",
    Action.VIEW: "view",
    Action.EXPORT: "export",
}


def build_authority(actions: Iterable[str]) -> Dict[str, bool]:
    """把业务动作转换为 FineBI v3 的 authority 对象。"""
    result: Dict[str, bool] = {}
    for action in actions:
        field_name = AUTHORITY_FIELDS.get(action)
        if field_name:
            result[field_name] = True
    return result


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def new_id(prefix: str = "req") -> str:
    return "%s-%s" % (prefix, uuid.uuid4().hex[:12])


@dataclass
class PermissionRequest:
    """一张审批单解析后的授权意图。"""
    user: str
    resource_type: str
    resource_id: str
    actions: List[str] = field(default_factory=list)
    data_scope: Dict[str, Any] = field(default_factory=dict)  # 行权限：{"rules": [...]}
    role: Optional[str] = None
    days: int = 90
    source: str = ""                       # 飞书审批实例 code
    request_id: str = field(default_factory=lambda: new_id("req"))
    extra: Dict[str, Any] = field(default_factory=dict)
    # 一张审批单可包含多个授权条目（如“数据集使用 + 行权限 + 角色”）。
    # 为空时按单条目处理，兼容旧调用方。
    items: List[Dict[str, Any]] = field(default_factory=list)

    def validate(self, max_days: int = 365) -> None:
        if not self.user:
            raise ValueError("user 不能为空")
        if self.resource_type not in ResourceType.ALL:
            raise ValueError("未知资源类型：%s" % self.resource_type)
        if not self.resource_id:
            raise ValueError("resource_id 不能为空")
        if self.resource_type == ResourceType.ROW and not self.data_scope.get("rules"):
            raise ValueError("行权限申请必须提供 data_scope.rules")
        if self.days <= 0 or self.days > max_days:
            raise ValueError("期限必须为 1~%d 天" % max_days)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "user": self.user,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "actions": list(self.actions),
            "data_scope": self.data_scope,
            "role": self.role,
            "days": self.days,
            "source": self.source,
            "extra": self.extra,
            "items": list(self.items),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionRequest":
        return cls(
            user=data["user"],
            resource_type=data["resource_type"],
            resource_id=data["resource_id"],
            actions=list(data.get("actions", [])),
            data_scope=dict(data.get("data_scope", {})),
            role=data.get("role"),
            days=int(data.get("days", 90)),
            source=data.get("source", ""),
            request_id=data.get("request_id") or new_id("req"),
            extra=dict(data.get("extra", {})),
            items=[dict(item) for item in (data.get("items") or [])],
        )


def rule_key(rule: Dict[str, Any]) -> tuple:
    return (rule.get("fieldId"), rule.get("type"), tuple(rule.get("filterValue") or []))


def merge_row_rules(existing: Iterable[Dict[str, Any]],
                    new_rules: Iterable[Dict[str, Any]],
                    connector: str = "or") -> Dict[str, Any]:
    """合并行权限规则（去重）。

    FineBI 的 `/v3/bi/authority/row/filter/user` 是全量覆盖语义，
    因此每次写入前要把该用户在该数据集上的全部有效规则合并成一个 filter。
    """
    merged: List[Dict[str, Any]] = []
    seen = set()
    for rule in list(existing) + list(new_rules):
        key = rule_key(rule)
        if key in seen:
            continue
        seen.add(key)
        merged.append(rule)
    return {"type": connector, "filterValue": merged}


def remove_row_rules(existing: Iterable[Dict[str, Any]],
                     to_remove: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    remove_keys = {rule_key(rule) for rule in to_remove}
    kept = [rule for rule in existing if rule_key(rule) not in remove_keys]
    return {"type": "or", "filterValue": kept}


@dataclass
class GrantResult:
    status: str                      # granted / skipped / failed / partial
    request_id: str
    ledger_ids: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    item_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "request_id": self.request_id,
            "ledger_ids": self.ledger_ids,
            "details": self.details,
            "items": self.item_results,
        }
