"""回收编排：按台账回收 + handler 注册表 + 跨进程锁 + 行权限重算 + 角色引用判断。

行为约定（设计说明书 §5.7、§5.8，设计修订 V1.1 §2）：

- 普通权限：只回收台账涉及、且没有被其他 active 台账引用的字段；文件夹/数据集仍按
  E2 要求“读现状 → 目标字段置 false → 提交完整五字段”，避免误伤其他权限。
- 行权限：取该用户该数据集其他 active 台账的剩余规则重算并写回；最后一条规则清空时
  按 ``ROW_CLEAR_STRATEGY``（默认 ``manual``）处理，manual 记 failed 台账并生成人工待办。
- 角色：仅当没有其他 active 台账引用该角色时才移除（兼容旧台账 payload.role 格式）。
- 可验证类型回收后复核一次，不一致重写一次，仍不一致抛 E3004。
- 失败进入 ``jobs`` 重试（1/5/15 分钟），非重试类转 manual。
- 保持 ``RevokeService(finebi, storage, platform=None, dry_run=False)`` 构造兼容。
"""
from __future__ import annotations

import json
import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from ..domain.handlers import (HANDLERS, PLATFORM_RESOURCE_TYPES, get_handler)
from ..domain.validators import check_parent_empower
from ..errors import BusinessError, is_template_auth_not_applicable
from ..locks import ResourceLock
from ..models import ResourceType, new_id, rule_key
from ..storage import Storage
from .grant import (FULL_AUTHORITY_FIELDS, error_code_of, first_data,
                    groups_to_set_payload, merge_full_authority,
                    merge_rule_groups, normalize_type_map,
                    row_rule_groups_from_read)
from .jobs import (KIND_REVOKE, KIND_ROW_CLEAR, KIND_SHARE_REVOKE, JobService,
                   NullNotifier, is_retryable)

LOGGER = logging.getLogger(__name__)

ROW_CLEAR_STRATEGIES = ("manual", "empty", "deny")
_VERIFIABLE_AUTHORITY = (ResourceType.FOLDER, ResourceType.TABLE)
_REVOCABLE_TYPES = set(ResourceType.ALL) | {"role"} | set(PLATFORM_RESOURCE_TYPES)


class RevokeService:
    """回收服务。``revoke_ledger(ledger)`` / ``revoke_user(user)`` 为公开入口。"""

    def __init__(self, finebi, storage: Storage, platform=None,
                 dry_run: bool = False,
                 lock: Optional[ResourceLock] = None,
                 handlers: Optional[Dict[str, Any]] = None,
                 notifier: Any = None,
                 row_clear_strategy: str = "manual",
                 jobs: Optional[JobService] = None,
                 lock_ttl: int = 120, lock_wait: int = 30,
                 type_map: Optional[Dict[Any, str]] = None,
                 resources: Optional[Dict[str, Any]] = None):
        self.finebi = finebi
        self.platform = platform
        self.storage = storage
        self.dry_run = dry_run
        self.clients = SimpleNamespace(finebi=finebi, platform=platform)
        self.handlers = dict(HANDLERS) if handlers is None else dict(handlers)
        self.lock = lock if lock is not None else \
            ResourceLock(storage.db_path, ttl=lock_ttl, wait=lock_wait)
        self.notifier = notifier or NullNotifier()
        self.type_map = normalize_type_map(type_map)
        strategy = str(row_clear_strategy or "manual").lower()
        if strategy not in ROW_CLEAR_STRATEGIES:
            raise ValueError("ROW_CLEAR_STRATEGY 只能是 %s" % (ROW_CLEAR_STRATEGIES,))
        self.row_clear_strategy = strategy
        self.jobs = jobs if jobs is not None else JobService(storage, notifier=self.notifier)
        self.resources = resources or {}
        self.owner = "revoke-%s" % new_id("worker")[7:]
        if not self.jobs.has_handler(KIND_REVOKE):
            self.jobs.register_handler(KIND_REVOKE, self._replay_revoke)

    # ---------- 公开入口 ----------
    def revoke_ledger(self, ledger: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
        return self._revoke(ledger, reason, schedule=True)

    def revoke_user(self, user: str, reason: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for ledger in self.storage.active_ledger(user=user):
            try:
                results.append(self.revoke_ledger(ledger, reason))
            except Exception as exc:  # noqa: BLE001 - 单条失败不影响其他条
                LOGGER.exception("回收失败：%s", ledger.get("id"))
                results.append({"ledger_id": ledger.get("id"), "user": user,
                                "error": "%s: %s" % (type(exc).__name__, exc),
                                "error_code": error_code_of(exc)})
        return results

    # ---------- 主流程 ----------
    def _revoke(self, ledger: Dict[str, Any], reason: str,
                schedule: bool) -> Dict[str, Any]:
        payload = ledger.get("payload") or {}
        rt = ledger.get("resource_type") or ""
        user = ledger.get("user") or ""
        rid = str(ledger.get("resource_id") or "")
        detail: Dict[str, Any] = {
            "ledger_id": ledger.get("id"), "user": user,
            "resource": "%s:%s" % (rt, rid), "reason": reason}
        if ledger.get("status") and ledger.get("status") != "active":
            detail.update({"skipped": True,
                           "reason": "台账不是 active：%s" % ledger.get("status")})
            return detail

        try:
            result = self._run_locked(ledger, payload)
        except Exception as exc:  # noqa: BLE001 - 记录、入重试后抛给上层
            detail.update({"error": "%s: %s" % (type(exc).__name__, exc),
                           "error_code": error_code_of(exc)})
            self.storage.log("ERROR", "revoke", "回收失败", detail)
            if schedule and not self.dry_run:
                self._schedule_failure(ledger, exc)
            raise

        detail.update(result)
        # 旧格式：角色记在主台账 payload.role 中，回收主权限时判断是否还需要该角色
        if rt != ResourceType.ROLE and payload.get("role"):
            detail["role"] = self._maybe_remove_role(
                user, str(payload["role"]), excluding=str(ledger.get("id") or ""))

        if self.dry_run:
            detail["dry_run"] = True
            self.storage.log("INFO", "revoke", "回收演练（dry-run）", detail)
            return detail

        if detail.get("ledger_status") == "failed":
            self._set_ledger_status(str(ledger.get("id")), "failed")
        else:
            self.storage.mark_revoked(str(ledger.get("id")), reason)
        self.storage.log("INFO", "revoke", "回收完成", detail)
        return detail

    def _run_locked(self, ledger: Dict[str, Any],
                    payload: Dict[str, Any]) -> Dict[str, Any]:
        rt = ledger.get("resource_type") or ""
        user = ledger.get("user") or ""
        rid = str(ledger.get("resource_id") or "")
        if rt not in _REVOCABLE_TYPES:
            raise BusinessError("未知资源类型：%s" % rt)
        key = self._lock_key(user, rt, rid)
        if self.dry_run:
            return self._revoke_item(ledger, payload)
        with self.lock.hold(key, self.owner):
            return self._revoke_item(ledger, payload)

    def _revoke_item(self, ledger: Dict[str, Any],
                     payload: Dict[str, Any]) -> Dict[str, Any]:
        rt = ledger.get("resource_type") or ""
        user = ledger.get("user") or ""
        rid = str(ledger.get("resource_id") or "")
        siblings = self._siblings(user, rt, rid, exclude=str(ledger.get("id") or ""))

        if rt in _VERIFIABLE_AUTHORITY:
            return self._revoke_authority(ledger, payload, siblings)
        if rt == ResourceType.FIELD:
            if siblings:
                return {"skipped": True, "reason": "同一列权限仍有其他有效台账"}
            if self.dry_run:
                return {"dry_run": True, "would": "biData=false"}
            resp = get_handler(rt).revoke(self.clients, user, rid,
                                          {"authority": {"biData": True}})
            return {"resp": resp, "revoked": ["biData"]}
        if rt == ResourceType.ROW:
            return self._revoke_row(ledger, payload, siblings)
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            return self._revoke_dashboard(ledger, payload, siblings)
        if rt == ResourceType.DASHBOARD_ENTRY:
            return self._revoke_entry(ledger, payload, siblings)
        if rt == ResourceType.ROLE:
            return self._revoke_role(ledger, siblings)
        if rt == ResourceType.DEPARTMENT:
            return self._revoke_department(ledger, siblings)
        if rt in PLATFORM_RESOURCE_TYPES:
            return self._revoke_platform(ledger, payload, siblings)
        if rt in (ResourceType.PUBLINK, ResourceType.DASH_SHARE,
                  ResourceType.DASHBOARD_DATA, ResourceType.SUBJECT):
            return self._revoke_simple(ledger, payload, siblings)
        raise BusinessError("未知资源类型：%s" % rt)

    # ---------- 普通权限 ----------
    def _revoke_authority(self, ledger: Dict[str, Any], payload: Dict[str, Any],
                          siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        rt = ledger["resource_type"]
        user = ledger["user"]
        rid = str(ledger["resource_id"])
        targets = {str(field) for field, value in (payload.get("authority") or {}).items()
                   if value}
        if not targets:
            return {"skipped": True, "reason": "台账未记录权限字段"}
        sibling_fields: set = set()
        for sibling in siblings:
            sibling_fields.update(
                str(field) for field, value
                in ((sibling.get("payload") or {}).get("authority") or {}).items() if value)
        kept = targets & sibling_fields
        remaining = targets - sibling_fields
        if not remaining:
            return {"skipped": True, "reason": "权限仍被其他有效台账引用",
                    "kept_fields": sorted(kept)}
        if rt == ResourceType.FOLDER and "empowerPrivilege" in remaining:
            check_parent_empower(self.finebi, self.resources, user, rid)
        if self.dry_run:
            return {"dry_run": True, "would_revoke": sorted(remaining),
                    "kept_fields": sorted(kept)}

        handler = get_handler(rt)
        current = first_data(handler.read(self.clients, user, rid))
        authority = merge_full_authority(current if isinstance(current, dict) else {}, {})
        for field in FULL_AUTHORITY_FIELDS:
            if field in remaining:
                authority[field] = False
        resp = handler.write(self.clients, user, rid, {"authority": authority})
        if not self._verify_authority(rt, user, rid, authority):
            LOGGER.warning("回收后复核不一致，重写一次：%s %s:%s", user, rt, rid)
            resp = handler.write(self.clients, user, rid, {"authority": authority})
            if not self._verify_authority(rt, user, rid, authority):
                raise BusinessError("回收后复核不一致（E3004），已重写一次仍不通过")
        return {"resp": resp, "revoked_fields": sorted(remaining),
                "kept_fields": sorted(kept), "authority": authority}

    def _verify_authority(self, rt: str, user: str, rid: str,
                          authority: Dict[str, Any]) -> bool:
        handler = get_handler(rt)
        current = first_data(handler.read(self.clients, user, rid))
        current = current if isinstance(current, dict) else {}
        return all(bool(current.get(field)) == bool(value)
                   for field, value in authority.items())

    # ---------- 行权限 ----------
    def _revoke_row(self, ledger: Dict[str, Any], payload: Dict[str, Any],
                    siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        user = ledger["user"]
        rid = str(ledger["resource_id"])
        handler = get_handler(ResourceType.ROW)
        current = first_data(handler.read(self.clients, user, rid))
        groups, error = row_rule_groups_from_read(current, self.type_map)
        if error:
            return self._to_manual(
                ledger, "行权限现状无法解析，转人工处理：" + error, KIND_ROW_CLEAR)
        groups = groups or []
        if any(len(group) > 1 for group in groups):
            # D-01：存量 AND 组结构未（POC-3 前）验证，不猜测写回
            return self._to_manual(
                ledger,
                "现有行权限包含 AND 组（多字段交集），嵌套 and 结构需 POC-3 确认，转人工处理",
                KIND_ROW_CLEAR)
        target_rules = [rule for rule in payload.get("rules") or [] if isinstance(rule, dict)]
        target_keys = {rule_key(rule) for rule in target_rules}
        # 现状里除本台账规则外的规则（含非台账授予的存量规则）必须保留
        remaining_groups = [group for group in groups
                            if rule_key(group[0]) not in target_keys]
        for sibling in siblings:
            sibling_rules = [rule for rule in
                             ((sibling.get("payload") or {}).get("rules") or [])
                             if isinstance(rule, dict)]
            if len({str(rule.get("fieldId") or "") for rule in sibling_rules}) > 1:
                # D-01 同步：其他台账的多字段规则同样不能在 POC-3 前猜测 AND 结构
                return self._to_manual(
                    ledger,
                    "其他有效台账的行权限包含多字段规则，嵌套 and 结构需 POC-3 确认，转人工处理",
                    KIND_ROW_CLEAR)
            remaining_groups.extend([[dict(rule)] for rule in sibling_rules])
        merged_groups = merge_rule_groups(remaining_groups, [])
        merged = groups_to_set_payload(merged_groups)
        detail: Dict[str, Any] = {"remaining_rules": merged}
        if merged["filterValue"]:
            if self.dry_run:
                return dict(detail, dry_run=True)
            resp = handler.revoke(self.clients, user, rid, {"filter": merged})
            detail.update({"resp": resp})
            detail.update(self._verify_row_groups(user, rid, merged_groups, handler))
            return detail

        strategy = self.row_clear_strategy
        if strategy == "empty":
            detail["warning"] = "按 empty 写空 filter；空 filter 语义需 POC-2 验证"
            if self.dry_run:
                detail["dry_run"] = True
                return detail
            resp = handler.revoke(
                self.clients, user, rid,
                {"filter": {"type": "or", "filterValue": []}})
            detail["resp"] = resp
            detail["verified"] = "skipped（filterType 映射未配置，POC-3）"
            return detail
        # manual（默认）与尚未通过 POC 的 deny 均转人工
        warning = ("行权限已清空最后一条规则，按 ROW_CLEAR_STRATEGY=%s 转人工处理"
                   "（POC-2 未结论；BI 管理员需确认数据集是否变为全量可见）" % strategy)
        if strategy == "deny":
            warning = ("deny 策略需 POC-2 结论与哨兵字段配置，当前降级为人工处理；" + warning)
        detail.update(self._to_manual(ledger, warning, KIND_ROW_CLEAR))
        return detail

    def _verify_row_groups(self, user: str, rid: str, expected_groups: List[List[Dict[str, Any]]],
                           handler: Any) -> Dict[str, Any]:
        """行权限写后复核：写回后反查，规则集合不一致时重写一次。

        只有配置了 filterType 映射时才复核——未配置映射时 get 返回的数字结构无法
        解析（D4），此时按“不可复核”返回，不猜测。
        """
        if not self.type_map:
            return {"verified": "skipped（filterType 映射未配置，POC-3）"}
        expected = {rule_key(condition)
                    for group in expected_groups for condition in group}
        for attempt in range(2):
            current = first_data(handler.read(self.clients, user, rid))
            groups, error = row_rule_groups_from_read(current, self.type_map)
            if error:
                return {"verified": "skipped（写后反查无法解析：%s）" % error}
            actual = {rule_key(condition)
                      for group in groups or [] for condition in group}
            if actual == expected:
                return {"verified": True}
            if attempt == 0:
                LOGGER.warning("行权限回收后复核不一致，重写一次：%s %s", user, rid)
                handler.revoke(self.clients, user, rid,
                               {"filter": groups_to_set_payload(expected_groups)})
        raise BusinessError("行权限回收后复核不一致（E3004），已重写一次仍不通过")

    # ---------- 仪表板 ----------
    def _revoke_dashboard(self, ledger: Dict[str, Any], payload: Dict[str, Any],
                          siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        user = ledger["user"]
        rid = str(ledger["resource_id"])
        targets = {str(field) for field, value in (payload.get("authority") or {}).items()
                   if value}
        if not targets:
            return {"skipped": True, "reason": "台账未记录权限字段"}
        sibling_view = any(bool(((s.get("payload") or {}).get("authority") or {}).get("view"))
                           for s in siblings)
        sibling_export = any(bool(((s.get("payload") or {}).get("authority") or {}).get("export"))
                             for s in siblings)
        handler = get_handler(ledger["resource_type"])
        try:
            current = first_data(handler.read(self.clients, user, rid))
        except Exception as exc:  # noqa: BLE001
            if is_template_auth_not_applicable(exc):
                return {"skipped": True,
                        "reason": "该仪表板未纳入模板认证，无需回收模板授权"}
            raise
        current = current if isinstance(current, dict) else {}
        view = bool(current.get("view"))
        export = bool(current.get("export"))
        if "view" in targets and not sibling_view:
            view = False
        if "export" in targets and not sibling_export:
            export = False
        if not view:
            export = False  # 查看关闭必须导出关闭（FR-GRN-05）
        if view == bool(current.get("view")) and export == bool(current.get("export")):
            return {"skipped": True, "reason": "权限仍被其他有效台账引用或已关闭"}
        if self.dry_run:
            return {"dry_run": True, "would_write": {"view": view, "export": export}}
        try:
            resp = handler.write(self.clients, user, rid,
                                 {"authority": {"view": view, "export": export}})
        except Exception as exc:  # noqa: BLE001
            if is_template_auth_not_applicable(exc):
                return {"skipped": True,
                        "reason": "该仪表板未纳入模板认证，无需回收模板授权"}
            raise
        return {"resp": resp, "authority": {"view": view, "export": export}}

    # ---------- 目录权限（entry） ----------
    def _revoke_entry(self, ledger: Dict[str, Any], payload: Dict[str, Any],
                      siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """回收仪表板目录权限（四字段全量覆盖）。

        与模板认证一致：只关闭本台账授予、且没有被其他有效台账引用的字段；
        本次未涉及的 edit/empower 保留现状，避免误伤后台手工配置的权限。
        """
        user = ledger["user"]
        rid = str(ledger["resource_id"])
        targets = {str(field) for field, value in (payload.get("authority") or {}).items()
                   if value}
        if not targets:
            return {"skipped": True, "reason": "台账未记录权限字段"}
        handler = get_handler(ResourceType.DASHBOARD_ENTRY)
        current = first_data(handler.read(self.clients, user, rid))
        current = current if isinstance(current, dict) else {}
        sibling_view = any(
            bool(((s.get("payload") or {}).get("authority") or {}).get("viewPrivilege"))
            for s in siblings)
        sibling_export = any(
            bool(((s.get("payload") or {}).get("authority") or {}).get("export"))
            for s in siblings)
        sibling_edit = any(
            bool(((s.get("payload") or {}).get("authority") or {}).get("editPrivilege"))
            for s in siblings)
        view = bool(current.get("viewPrivilege"))
        export = bool(current.get("export"))
        edit = bool(current.get("editPrivilege"))
        if "viewPrivilege" in targets and not sibling_view:
            view = False
        if "export" in targets and not sibling_export:
            export = False
        if "editPrivilege" in targets and not sibling_edit:
            edit = False
        if not view:
            export = False  # 查看关闭必须导出关闭
        if (view == bool(current.get("viewPrivilege"))
                and export == bool(current.get("export"))
                and edit == bool(current.get("editPrivilege"))):
            return {"skipped": True,
                    "reason": "权限仍被其他有效台账引用或已关闭"}
        authority = {"viewPrivilege": view, "export": export,
                     "editPrivilege": edit,
                     "empowerPrivilege": bool(current.get("empowerPrivilege"))}
        if self.dry_run:
            return {"dry_run": True, "would_write": authority}
        resp = handler.write(self.clients, user, rid, {"authority": authority})
        return {"resp": resp, "authority": authority,
                "revoked": sorted(targets & {"viewPrivilege", "export", "editPrivilege"})}

    # ---------- 平台权限台账（自建 Web 审批写入） ----------
    def _revoke_platform(self, ledger: Dict[str, Any], payload: Dict[str, Any],
                         siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        rt = ledger["resource_type"]
        user = ledger["user"]
        rid = str(ledger["resource_id"])
        if siblings:
            return {"skipped": True, "reason": "权限仍被其他有效台账引用"}
        if self.platform is None:
            return self._to_manual(
                ledger, "未配置平台客户端，%s:%s 需人工回收" % (rt, rid), KIND_REVOKE)
        if self.dry_run:
            return {"dry_run": True, "would_revoke": "%s:%s" % (rt, rid)}
        resp = get_handler(rt).revoke(self.clients, user, rid, payload)
        return {"resp": resp, "verifiable": False, "revoked": [rt]}

    # ---------- 角色 ----------
    def _revoke_role(self, ledger: Dict[str, Any],
                     siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        user = ledger["user"]
        role = str(ledger["resource_id"])
        if (ledger.get("payload") or {}).get("preexisting"):
            return {"skipped": True,
                    "reason": "角色在申请前已存在，回收时不删除原有成员关系"}
        if self._role_still_used(user, role, str(ledger.get("id") or "")):
            return {"skipped": True, "reason": "仍有其他有效授权引用该角色"}
        if self.dry_run:
            return {"dry_run": True, "would_remove_role": role}
        if self.platform is None:
            return {"manual": True, "warning": "未配置平台客户端，角色需人工移除"}
        handler = get_handler(ResourceType.ROLE)
        resp = handler.revoke(self.clients, user, role, {})
        return {"resp": resp, "role_removed": role}

    def _revoke_department(self, ledger: Dict[str, Any],
                           siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        user = ledger["user"]
        department = str(ledger["resource_id"])
        if (ledger.get("payload") or {}).get("preexisting"):
            return {"skipped": True,
                    "reason": "部门在申请前已存在，回收时不删除原有成员关系"}
        if siblings:
            return {"skipped": True, "reason": "仍有其他有效授权引用该部门"}
        if self.dry_run:
            return {"dry_run": True, "would_remove_department": department}
        if self.platform is None:
            return {"manual": True, "warning": "未配置平台客户端，部门成员关系需人工移除"}
        handler = get_handler(ResourceType.DEPARTMENT)
        resp = handler.revoke(self.clients, user, department, {})
        return {"resp": resp, "department_removed": department}

    def _maybe_remove_role(self, user: str, role: str,
                           excluding: str) -> Dict[str, Any]:
        if self._role_still_used(user, role, excluding):
            return {"skipped": True, "reason": "仍有其他有效授权使用该角色"}
        if self.dry_run:
            return {"dry_run": True, "would_remove_role": role}
        if self.platform is None:
            return {"skipped": True, "reason": "未配置平台客户端"}
        try:
            resp = self.platform.set_user_roles(user, remove=[role])
        except Exception as exc:  # noqa: BLE001 - 角色移除失败降级为人工
            LOGGER.warning("角色移除失败：%s %s", user, role, exc_info=True)
            return {"manual": True, "warning": "角色移除失败：%s" % exc}
        return {"role_removed": role, "resp": resp}

    def _role_still_used(self, user: str, role: str, excluding: str) -> bool:
        for item in self.storage.active_ledger(user=user):
            if str(item.get("id")) == excluding:
                continue
            if (item.get("resource_type") == ResourceType.ROLE
                    and str(item.get("resource_id")) == role):
                return True
            if str((item.get("payload") or {}).get("role") or "") == role:
                return True
        return False

    # ---------- 不可复核四类 ----------
    def _revoke_simple(self, ledger: Dict[str, Any], payload: Dict[str, Any],
                       siblings: List[Dict[str, Any]]) -> Dict[str, Any]:
        rt = ledger["resource_type"]
        user = ledger["user"]
        rid = str(ledger["resource_id"])
        if siblings:
            return {"skipped": True, "reason": "权限仍被其他有效台账引用"}
        if rt == ResourceType.DASH_SHARE:
            # D-02：接口只支持授予，取消分享需人工；按行权限 manual 对齐（failed + 待办 + 通知）
            return self._to_manual(
                ledger,
                "仪表板分享接口仅支持授予，取消分享需在 FineBI 后台人工处理",
                KIND_SHARE_REVOKE)
        if self.dry_run:
            return {"dry_run": True}
        resp = get_handler(rt).revoke(self.clients, user, rid, payload)
        return {"resp": resp, "verifiable": False}

    # ---------- 台账 / 锁 / 通知 ----------
    def _siblings(self, user: str, rt: str, rid: str,
                  exclude: str = "") -> List[Dict[str, Any]]:
        # 仪表板查看/导出共用同一 biReportId，互相视为同一资源的台账
        if rt in (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT):
            types = (ResourceType.DASHBOARD_VIEW, ResourceType.DASHBOARD_EXPORT)
        else:
            types = (rt,)
        result = []
        for item in self.storage.active_ledger(user=user):
            if str(item.get("id")) == exclude:
                continue
            if (item.get("resource_type") in types
                    and str(item.get("resource_id")) == str(rid)):
                result.append(item)
        return result

    def _set_ledger_status(self, ledger_id: str, status: str) -> None:
        setter = getattr(self.storage, "set_ledger_status", None)
        if callable(setter):
            setter(ledger_id, status)
            return
        try:
            self.storage.conn.execute(
                "UPDATE ledger SET status=?, revoked_at=? WHERE id=?",
                (status, None, ledger_id))
            self.storage.conn.commit()
        except Exception:  # noqa: BLE001 - 状态更新失败不影响回收结果
            LOGGER.warning("更新台账状态失败：%s -> %s", ledger_id, status, exc_info=True)

    def _to_manual(self, ledger: Dict[str, Any], warning: str,
                   kind: str = KIND_ROW_CLEAR) -> Dict[str, Any]:
        """转人工统一处理（D-02）：台账置 failed + 人工待办 + 通知管理员。"""
        detail: Dict[str, Any] = {"manual": True, "ledger_status": "failed",
                                  "warning": warning}
        if self.dry_run:
            detail["dry_run"] = True
            return detail
        ref_id = str(ledger.get("id") or "")
        self._enqueue_manual_job(kind, ref_id, warning)
        titles = {KIND_ROW_CLEAR: "行权限回收需人工处理",
                  KIND_SHARE_REVOKE: "仪表板分享取消需人工处理"}
        self._notify_admins(
            titles.get(kind, "权限回收需人工处理"),
            "台账 %s（用户 %s，资源 %s:%s）：%s"
            % (ref_id, ledger.get("user"), ledger.get("resource_type"),
               ledger.get("resource_id"), warning))
        return detail

    def _enqueue_manual_job(self, kind: str, ref_id: str, error: str) -> None:
        try:
            self.jobs.enqueue_manual(kind, ref_id, error=error)
        except Exception:  # noqa: BLE001 - 待办入队失败不影响返回
            LOGGER.warning("人工待办入队失败：%s %s", kind, ref_id, exc_info=True)

    def _schedule_failure(self, ledger: Dict[str, Any], exc: BaseException) -> None:
        ref_id = str(ledger.get("id") or "")
        has_open = getattr(self.jobs, "has_open_job", None)
        if callable(has_open) and has_open(KIND_REVOKE, ref_id):
            self._notify_admins("回收失败", "台账 %s（用户 %s）回收失败：%s，等待重试任务处理。"
                                % (ref_id, ledger.get("user"), exc))
            return
        has_manual = getattr(self.jobs, "has_manual_job", None)
        if callable(has_manual) and has_manual(KIND_REVOKE, ref_id):
            self._notify_admins("回收失败", "台账 %s（用户 %s）回收失败：%s，人工待办已存在。"
                                % (ref_id, ledger.get("user"), exc))
            return
        try:
            if is_retryable(exc):
                self.jobs.schedule_retry(KIND_REVOKE, ref_id, failed_attempts=1)
            else:
                self.jobs.enqueue_manual(KIND_REVOKE, ref_id, error=str(exc))
        except Exception:  # noqa: BLE001 - 入队失败不影响抛出的原始异常
            LOGGER.warning("回收失败任务入队失败", exc_info=True)
        self._notify_admins("回收失败", "台账 %s（用户 %s）回收失败：%s"
                            % (ledger.get("id"), ledger.get("user"), exc))

    def _notify_admins(self, title: str, content: str) -> None:
        try:
            self.notifier.notify_admins(title, content)
        except Exception:  # noqa: BLE001 - 通知失败不影响主流程
            LOGGER.warning("通知发送失败：%s", title, exc_info=True)

    @staticmethod
    def _lock_key(user: str, rt: str, rid: str) -> str:
        return "fb_user:%s:%s:%s" % (user, rt, rid)

    # ---------- 重试回放 ----------
    def _replay_revoke(self, ledger_id: str) -> Dict[str, Any]:
        getter = getattr(self.storage, "get_ledger", None)
        ledger = getter(ledger_id) if callable(getter) else None
        if ledger is None:
            row = self.storage.conn.execute(
                "SELECT * FROM ledger WHERE id=?", (ledger_id,)).fetchone()
            if not row:
                raise BusinessError("重试任务找不到台账：%s" % ledger_id)
            ledger = dict(row)
            payload = ledger.get("payload")
            if isinstance(payload, str):
                try:
                    ledger["payload"] = json.loads(payload)
                except json.JSONDecodeError:
                    ledger["payload"] = {}
        if ledger.get("status") != "active":
            return {"ledger_id": ledger_id, "status": ledger.get("status"),
                    "skipped": True, "reason": "台账不是 active"}
        return self._revoke(ledger, "重试回收", schedule=False)
