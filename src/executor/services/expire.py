"""到期回收：扫描台账并回收。"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..storage import Storage

LOGGER = logging.getLogger(__name__)


class ExpireService:
    def __init__(self, revoke_service, storage: Storage, notifier=None):
        self.revoke_service = revoke_service
        self.storage = storage
        self.notifier = notifier

    def run_once(self, now: str = "") -> List[Dict[str, Any]]:
        due = self.storage.due_ledger(now or None)
        LOGGER.info("到期台账 %d 条", len(due))
        results = []
        for ledger in due:
            try:
                results.append(self.revoke_service.revoke_ledger(ledger, reason="到期回收"))
            except Exception as exc:  # noqa: BLE001 - 单条失败不影响其他
                LOGGER.exception("到期回收失败：%s", ledger["id"])
                self.storage.log("ERROR", "expire", "到期回收失败：%s" % exc,
                                 {"ledger_id": ledger["id"]})
                results.append({"ledger_id": ledger["id"], "error": str(exc)})
                if self.notifier:
                    self.notifier.notify_admins(
                        "到期回收失败", "台账 `%s` 回收失败：%s" % (ledger["id"], exc),
                        color="red")
        return results
