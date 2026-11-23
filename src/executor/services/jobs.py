"""重试 / 人工待办队列：与 storage.jobs 表配套。

规则（需求书 FR-NOT-02、设计说明书 §5.5）：

- 失败按 ``[60, 300, 900]`` 秒退避（1/5/15 分钟）；
- 连续失败超过 ``max_attempts``（默认 3）次转 ``manual``，由 BI 管理员处理；
- 处理函数按 ``kind`` 注册，签名 ``handler(ref_id) -> Any``；抛异常视为失败；
- 非重试类异常（业务校验、用户/资源不存在、403 等）直接转 manual，不浪费重试；
- 处理函数可注入（测试与 CLI 共用同一实现），本模块不发起任何网络调用。
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Tuple

from ..errors import ApiError, BusinessError
from ..locks import LockTimeout
from ..models import now_iso
from ..storage import Storage

LOGGER = logging.getLogger(__name__)

# 退避秒数：第 1 次失败 60s，第 2 次 300s，第 3 次 900s，再失败转 manual
BACKOFF_SECONDS: Tuple[int, ...] = (60, 300, 900)
MAX_ATTEMPTS = 3

# 任务类型约定（处理函数由 runtime/cli 注册）
KIND_GRANT = "grant"            # ref_id = request_id
KIND_REVOKE = "revoke"          # ref_id = ledger_id
KIND_ROW_CLEAR = "row_clear"    # ref_id = ledger_id，行权限清空人工待办
KIND_SHARE_REVOKE = "share_revoke"  # ref_id = ledger_id，仪表板分享取消人工待办

JobHandler = Callable[[str], Any]


class JobError(BusinessError):
    """任务执行失败（非重试类）。"""


class JobResultFailure(Exception):
    """处理函数没有抛异常、但返回结果显示任务失败（如 GrantResult.status=failed）。"""

    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable


def is_retryable(exc: BaseException) -> bool:
    """判断异常是否值得重试。

    - 网络/5xx/限频（ApiError 的 NETWORK、408/429/5xx）：重试；
    - 业务校验失败（BusinessError 及子类）：不重试，直接人工（锁竞争除外）；
    - 处理函数返回失败结果（JobResultFailure）：按其 retryable 标记；
    - 其他未知异常：保守重试。
    """
    if isinstance(exc, JobResultFailure):
        return exc.retryable
    if isinstance(exc, LockTimeout):
        return True
    if isinstance(exc, BusinessError):
        return False
    if isinstance(exc, ApiError):
        status = exc.status
        if isinstance(status, int):
            return status in (408, 429) or status >= 500
        return str(status).upper() in ("NETWORK", "TIMEOUT")
    return True


def add_seconds(iso_time: str, seconds: int) -> str:
    """在 ISO 时间串上增加秒数，返回同时区 ISO 串。"""
    try:
        base = datetime.fromisoformat(iso_time)
    except (TypeError, ValueError):
        base = datetime.now().astimezone()
    return (base + timedelta(seconds=int(seconds))).isoformat(timespec="seconds")


class NullNotifier:
    """空通知器：未注入通知服务时占位，避免主流程依赖。"""

    def notify_admins(self, title: str, content: str, link: str = "",
                      color: str = "orange") -> None:  # noqa: D401 - 协议方法
        LOGGER.info("[notify-placeholder] %s：%s", title, content)

    def notify_user(self, open_id: str, title: str, content: str,
                    link: str = "", color: str = "blue") -> None:
        LOGGER.info("[notify-placeholder] %s -> %s：%s", title, open_id, content)


class JobService:
    """jobs 表的读写封装：入队、到点执行、退避、转人工。"""

    def __init__(self, storage: Storage,
                 backoff: Tuple[int, ...] = BACKOFF_SECONDS,
                 max_attempts: int = MAX_ATTEMPTS,
                 handlers: Optional[Dict[str, JobHandler]] = None,
                 notifier: Any = None):
        self.storage = storage
        self.backoff = tuple(backoff) if backoff else BACKOFF_SECONDS
        self.max_attempts = int(max_attempts)
        self.handlers: Dict[str, JobHandler] = dict(handlers or {})
        self.notifier = notifier or NullNotifier()

    # ---------- 注册 ----------
    def register_handler(self, kind: str, handler: JobHandler) -> None:
        if not callable(handler):
            raise TypeError("job handler 必须可调用：%r" % (handler,))
        self.handlers[kind] = handler

    def has_handler(self, kind: str) -> bool:
        return kind in self.handlers

    def has_open_job(self, kind: str, ref_id: str) -> bool:
        """是否已有排队/执行中的同目标任务（避免处理函数内部重复入队）。"""
        try:
            row = self.storage.conn.execute(
                "SELECT 1 FROM jobs WHERE kind=? AND ref_id=? "
                "AND status IN ('queued','running') LIMIT 1",
                (kind, ref_id)).fetchone()
            return row is not None
        except Exception:  # noqa: BLE001 - 查询失败时按“无排队任务”处理
            LOGGER.warning("查询未完成任务失败：%s %s", kind, ref_id, exc_info=True)
            return False

    def has_manual_job(self, kind: str, ref_id: str) -> bool:
        """是否已有未闭环的人工待办（D-03：轮询跳过已转人工的实例）。"""
        try:
            row = self.storage.conn.execute(
                "SELECT 1 FROM jobs WHERE kind=? AND ref_id=? AND status='manual' LIMIT 1",
                (kind, ref_id)).fetchone()
            return row is not None
        except Exception:  # noqa: BLE001 - 查询失败时按“无待办”处理
            LOGGER.warning("查询人工待办失败：%s %s", kind, ref_id, exc_info=True)
            return False

    # ---------- 入队 ----------
    def enqueue(self, kind: str, ref_id: str, next_run_at: Optional[str] = None,
                attempts: int = 0, status: str = "queued") -> str:
        """入队；``attempts``/``status`` 可变，用于兼容 storage 的简化签名。"""
        run_at = next_run_at or now_iso()
        job_id = self.storage.enqueue_job(kind, ref_id, run_at, status=status)
        if attempts or status != "queued":
            self.storage.update_job(job_id, status, attempts=attempts, next_run_at=run_at)
        return job_id

    def enqueue_manual(self, kind: str, ref_id: str, error: str = "") -> str:
        """直接进人工待办（不重试）。"""
        job_id = self.enqueue(kind, ref_id, status="manual", attempts=self.max_attempts + 1)
        self.storage.update_job(job_id, "manual", attempts=self.max_attempts + 1,
                                last_error=error or "转人工")
        return job_id

    def schedule_retry(self, kind: str, ref_id: str, failed_attempts: int = 1,
                       now: Optional[str] = None) -> str:
        """按失败次数安排下一次重试；超过上限转 manual。"""
        attempts = max(1, int(failed_attempts))
        if attempts > self.max_attempts:
            return self.enqueue_manual(kind, ref_id,
                                       error="重试 %d 次仍失败" % self.max_attempts)
        delay = self.backoff[min(attempts - 1, len(self.backoff) - 1)]
        return self.enqueue(kind, ref_id, next_run_at=add_seconds(now or now_iso(), delay),
                            attempts=attempts, status="queued")

    # ---------- 执行 ----------
    def run_due(self, now: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """执行到点任务；单条失败不影响其他条。"""
        now = now or now_iso()
        due = self.storage.due_jobs(now)[:int(limit)]
        summary: Dict[str, Any] = {"scanned": len(due), "done": 0, "retried": 0,
                                   "manual": 0, "results": []}
        for job in due:
            result = self._run_one(job, now)
            summary[result["status"]] = summary.get(result["status"], 0) + 1
            summary["results"].append(result)
        if due:
            self.storage.log("INFO", "jobs", "重试队列执行完成",
                             {"scanned": summary["scanned"], "done": summary["done"],
                              "retried": summary["retried"], "manual": summary["manual"]})
        return summary

    def _run_one(self, job: Dict[str, Any], now: str) -> Dict[str, Any]:
        kind = job["kind"]
        ref_id = job["ref_id"]
        job_id = job["id"]
        handler = self.handlers.get(kind)
        base = {"job_id": job_id, "kind": kind, "ref_id": ref_id}
        if handler is None:
            error = "未注册处理函数：%s" % kind
            self.storage.update_job(job_id, "manual", last_error=error)
            self._notify_manual(kind, ref_id, error)
            return dict(base, status="manual", error=error)

        self.storage.update_job(job_id, "running", attempts=job.get("attempts", 0),
                                next_run_at=now)
        try:
            payload = handler(ref_id)
            failure = self._failure_of_result(payload)
            if failure is not None:
                raise failure
        except Exception as exc:  # noqa: BLE001 - 任务失败按退避策略处理
            return self._on_failure(job, exc, now, base)

        self.storage.update_job(job_id, "done", attempts=job.get("attempts", 0) + 1,
                                next_run_at=now)
        self.storage.log("INFO", "jobs", "任务执行成功：%s" % kind,
                         {"job_id": job_id, "ref_id": ref_id})
        return dict(base, status="done", result=self._safe(payload))

    @staticmethod
    def _failure_of_result(payload: Any) -> Optional[JobResultFailure]:
        """处理函数返回失败结果时转成异常，让重试/转人工机制生效。

        D-04：消息携带首条失败条目的 error_code/error，``last_error`` 可直接定位根因。
        """
        status = getattr(payload, "status", None) or (
            payload.get("status") if isinstance(payload, dict) else None)
        if status not in ("failed", "partial"):
            return None
        item_results = getattr(payload, "item_results", None)
        if item_results is None and isinstance(payload, dict):
            item_results = payload.get("items") or payload.get("item_results") or []
        failed = [item for item in item_results or []
                  if isinstance(item, dict) and item.get("status") == "failed"]
        retryable = any(bool(item.get("retryable")) for item in failed)
        message = "处理函数返回失败状态：%s" % status
        if failed:
            first = failed[0]
            resource = "%s:%s" % (first.get("resource_type") or "",
                                  first.get("resource_id") or "")
            code = str(first.get("error_code") or "")
            reason = str(first.get("error") or first.get("reason") or "")
            message += "；首条失败 %s %s%s" % (
                resource, ("[%s] " % code) if code else "", reason or "（无错误信息）")
        return JobResultFailure(message, retryable=retryable)

    def _on_failure(self, job: Dict[str, Any], exc: BaseException,
                    now: str, base: Dict[str, Any]) -> Dict[str, Any]:
        attempts = int(job.get("attempts", 0)) + 1
        error = "%s: %s" % (type(exc).__name__, exc)
        retryable = is_retryable(exc)
        if not retryable:
            self.storage.update_job(job["id"], "manual", attempts=attempts, last_error=error)
            self._notify_manual(job["kind"], job["ref_id"], error)
            return dict(base, status="manual", attempt=attempts, error=error,
                        retryable=False)
        if attempts > self.max_attempts:
            self.storage.update_job(job["id"], "manual", attempts=attempts, last_error=error)
            self._notify_manual(job["kind"], job["ref_id"], error)
            return dict(base, status="manual", attempt=attempts, error=error,
                        retryable=True)
        delay = self.backoff[min(attempts - 1, len(self.backoff) - 1)]
        self.storage.update_job(job["id"], "queued", attempts=attempts,
                                next_run_at=add_seconds(now, delay), last_error=error)
        LOGGER.warning("任务 %s 第 %d 次失败，%ss 后重试：%s",
                       job["id"], attempts, delay, error)
        return dict(base, status="retried", attempt=attempts, error=error,
                    next_run_at=add_seconds(now, delay))

    @staticmethod
    def _safe(payload: Any) -> Any:
        try:
            import json
            json.dumps(payload)
            return payload
        except (TypeError, ValueError):
            return str(payload)

    def _notify_manual(self, kind: str, ref_id: str, error: str) -> None:
        try:
            self.notifier.notify_admins(
                "任务转人工：%s" % kind,
                "任务 %s 的目标 %s 处理失败：%s，请人工处理。" % (kind, ref_id, error))
        except Exception:  # noqa: BLE001 - 通知失败不影响主流程
            LOGGER.warning("转人工通知发送失败", exc_info=True)
