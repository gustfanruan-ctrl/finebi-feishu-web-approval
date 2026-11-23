"""组装运行上下文（客户端 + 服务 + 存储）。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from .config import Settings
from .feishu import FeishuClient
from .feishu.form_parser import FormParser
from .finebi import FineBIClient, FineBIPlatformClient
from .http import HttpClient
from .locks import ResourceLock
from .models import PermissionRequest
from .services import (ApprovalPoller, ExpireService, Notifier, OffboardService,
                       PermissionService, ReconcileService, RevokeService)
from .services.jobs import JobService, KIND_GRANT, KIND_REVOKE
from .storage import Storage


@dataclass
class Context:
    settings: Settings
    http: HttpClient
    finebi: FineBIClient
    platform: FineBIPlatformClient
    feishu: FeishuClient
    storage: Storage
    permission: PermissionService
    revoke: RevokeService
    expire: ExpireService
    offboard: OffboardService
    poller: ApprovalPoller
    notifier: Notifier
    jobs: JobService
    reconcile: ReconcileService

    def report(self, month: str = "") -> Dict[str, Any]:
        month = month or datetime.now().strftime("%Y-%m")
        like = month + "%"
        q = self.storage.conn.execute
        return {
            "month": month,
            "requests": dict(q("SELECT status, COUNT(*) FROM requests WHERE created_at LIKE ? GROUP BY status", (like,)).fetchall()),
            "ledger": dict(q("SELECT status, COUNT(*) FROM ledger WHERE created_at LIKE ? GROUP BY status", (like,)).fetchall()),
            "ledger_by_type": dict(q("SELECT resource_type, COUNT(*) FROM ledger WHERE status='active' GROUP BY resource_type").fetchall()),
            "logs_error": q("SELECT COUNT(*) FROM logs WHERE level='ERROR' AND ts LIKE ?", (like,)).fetchone()[0],
            "jobs_manual": q("SELECT COUNT(*) FROM jobs WHERE status='manual'").fetchone()[0],
        }


def build(settings: Settings) -> Context:
    http = HttpClient(timeout=settings.http_timeout)
    finebi = FineBIClient(settings.finebi_base_url, settings.finebi_client_id,
                          settings.finebi_secret, settings.finebi_dec_user,
                          http=http, dry_run=settings.dry_run)
    platform = FineBIPlatformClient(settings.finebi_base_url, settings.finebi_client_id,
                                    settings.finebi_secret, settings.finebi_dec_user,
                                    http=http, dry_run=settings.dry_run)
    feishu = FeishuClient(settings.feishu_app_id, settings.feishu_app_secret, http=http)
    storage = Storage(settings.db_path)
    lock = ResourceLock(settings.db_path, ttl=settings.lock_ttl)
    notifier = Notifier(feishu, webhook_url=settings.feishu_webhook_url,
                        admin_open_ids=settings.admin_open_ids, dry_run=settings.dry_run)
    jobs = JobService(storage, notifier=notifier)
    type_map = settings.policy.get("filter_type_map", {}) or {}
    permission = PermissionService(finebi, storage, platform=platform,
                                   max_days=settings.max_days, dry_run=settings.dry_run,
                                   lock=lock, notifier=notifier,
                                   adopt_existing=settings.adopt_existing,
                                   jobs=jobs, lock_ttl=settings.lock_ttl,
                                   type_map=type_map)
    revoke = RevokeService(finebi, storage, platform=platform, dry_run=settings.dry_run,
                           lock=lock, notifier=notifier,
                           row_clear_strategy=settings.row_clear_strategy,
                           jobs=jobs, lock_ttl=settings.lock_ttl,
                           type_map=type_map, resources=settings.resource_map)
    expire = ExpireService(revoke, storage, notifier=notifier)
    offboard = OffboardService(finebi, storage, platform=platform,
                               revoke_service=revoke, dry_run=settings.dry_run,
                               notifier=notifier)

    def _grant_job(request_id: str):
        row = storage.get_request(request_id)
        if not row:
            raise ValueError("request not found: %s" % request_id)
        return permission.grant(PermissionRequest.from_dict(row["payload"]))

    def _revoke_job(ledger_id: str):
        ledger = storage.get_ledger(ledger_id)
        if not ledger:
            raise ValueError("ledger not found: %s" % ledger_id)
        return revoke.revoke_ledger(ledger, reason="重试回收")

    jobs.register_handler(KIND_GRANT, _grant_job)
    jobs.register_handler(KIND_REVOKE, _revoke_job)

    def _template_resolver(name: str, ctx: Dict[str, Any]):
        raw = (settings.templates or {}).get(name)
        if raw is None:
            raw = (settings.policy.get("templates") or {}).get(name)
        if raw is None:
            raise ValueError("权限模板不存在：%s（config.templates）" % name)
        items = raw.get("items") if isinstance(raw, dict) else raw
        defaults = raw if isinstance(raw, dict) else {}
        result = []
        for item in items or []:
            item = dict(item)
            item.setdefault("actions", defaults.get("actions") or ctx.get("actions") or [])
            if "role" not in item and defaults.get("default_role"):
                item["role"] = defaults["default_role"]
            result.append(item)
        return result

    mapper = FormParser(settings.policy.get("form_mapping", {}),
                        template_resolver=_template_resolver)
    poller = ApprovalPoller(feishu, permission, storage,
                            approval_code=settings.feishu_approval_code, mapper=mapper)
    reconcile = ReconcileService(finebi, storage, platform=platform,
                                 type_map=type_map)
    return Context(settings, http, finebi, platform, feishu, storage,
                   permission, revoke, expire, offboard, poller,
                   notifier, jobs, reconcile)
