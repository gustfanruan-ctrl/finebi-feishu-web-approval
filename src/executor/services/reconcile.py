"""对账：台账（active）与 FineBI 现状逐条比对。

- 可验证类型（folder/table/field/row/dashboard）：read 后比对期望值。
- 不可验证四类（publink/share/dashboard_data/subject）：标记 unverifiable。
- row 需要 filterType 映射；映射未配置时标 unverifiable，不猜测。
"""
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from ..domain.handlers import get_handler
from ..finebi.rowfilter import RowFilterError, parse_get
from ..models import ResourceType
from ..storage import Storage

LOGGER = logging.getLogger(__name__)


def _first_data(resp: Any) -> Any:
    if not isinstance(resp, dict):
        return None
    data = resp.get("data")
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict):
            return item.get("data")
    return data


class ReconcileService:
    def __init__(self, finebi, storage: Storage, platform=None,
                 type_map: Optional[Dict[int, str]] = None, limit: int = 500):
        self.clients = SimpleNamespace(finebi=finebi, platform=platform)
        self.storage = storage
        self.type_map = type_map or {}
        self.limit = limit

    def run(self) -> List[Dict[str, Any]]:
        diffs: List[Dict[str, Any]] = []
        for ledger in self.storage.active_ledger()[: self.limit]:
            diffs.append(self.check_one(ledger))
        self.storage.log("INFO", "reconcile", "对账完成",
                         {"checked": len(diffs), "mismatch": sum(
                             1 for d in diffs if d["status"] == "mismatch")})
        return diffs

    def check_one(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        rt = ledger["resource_type"]
        user = ledger["user"]
        rid = ledger["resource_id"]
        payload = ledger.get("payload") or {}
        base = {"ledger_id": ledger["id"], "user": user,
                "resource": "%s:%s" % (rt, rid)}
        try:
            handler = get_handler(rt)
        except KeyError:
            return dict(base, status="unverifiable", reason="未注册处理器")

        if not handler.verifiable:
            return dict(base, status="unverifiable", reason="接口无查询能力")

        if rt == ResourceType.ROW and not self.type_map:
            return dict(base, status="unverifiable", reason="filterType 映射未配置（POC-3）")

        try:
            raw = handler.read(self.clients, user, rid)
        except Exception as exc:  # noqa: BLE001
            return dict(base, status="error", error=str(exc))

        expected = self._expected(rt, payload)
        actual = self._actual(rt, raw)
        if expected is None or actual is None:
            return dict(base, status="unverifiable",
                        expected=expected, actual=actual)
        mismatch = {k: {"expected": v, "actual": actual.get(k)} for k, v in expected.items()
                    if bool(actual.get(k)) != bool(v)}
        if mismatch:
            return dict(base, status="mismatch", diff=mismatch)
        return dict(base, status="ok")

    @staticmethod
    def _expected(rt: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if rt in (ResourceType.FOLDER, ResourceType.TABLE):
            return dict(payload.get("authority") or {})
        if rt == ResourceType.FIELD:
            return {"biData": True}
        if rt == ResourceType.DASHBOARD_VIEW:
            return {"view": True}
        if rt == ResourceType.DASHBOARD_EXPORT:
            return {"view": True, "export": True}
        if rt == ResourceType.DASHBOARD_ENTRY:
            authority = payload.get("authority") or {}
            return {str(k): bool(v) for k, v in authority.items() if v}
        return {}

    def _actual(self, rt: str, raw: Any) -> Optional[Dict[str, Any]]:
        if rt == ResourceType.ROW:
            try:
                expr = parse_get(_first_data(raw), self.type_map)
            except RowFilterError:
                return None
            return {"expr": bool(expr)} if expr else {}
        data = _first_data(raw)
        if isinstance(data, dict):
            return data
        return None
