# -*- coding: utf-8 -*-
"""jobs 重试队列单测：入队、退避 [60,300,900]、3 次后转 manual、处理函数注入。"""
import os
import tempfile
import unittest
from datetime import datetime, timedelta

from executor.errors import ApiError, BusinessError
from executor.locks import LockTimeout
from executor.services.jobs import (BACKOFF_SECONDS, JobService, add_seconds,
                                    is_retryable)

FUTURE = (datetime.now().astimezone() + timedelta(hours=2)).isoformat(timespec="seconds")


class JobsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        from executor.storage import Storage
        self.storage = Storage(os.path.join(self.tmp.name, "jobs.db"))
        self.jobs = JobService(self.storage)
        self.calls = []

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _due_at(self, job_id):
        row = self.storage.conn.execute(
            "SELECT next_run_at FROM jobs WHERE id=?", (job_id,)).fetchone()
        return row["next_run_at"]

    def _job(self, job_id):
        row = self.storage.conn.execute(
            "SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

    # ---------- 入队 ----------
    def test_enqueue_is_due_immediately(self):
        job_id = self.jobs.enqueue("grant", "req-1")
        due = self.storage.due_jobs()
        self.assertEqual([j["id"] for j in due], [job_id])
        self.assertEqual(due[0]["attempts"], 0)

    def test_enqueue_with_attempts(self):
        self.jobs.enqueue("grant", "req-1", attempts=2)
        job = self.storage.due_jobs()[0]
        self.assertEqual(job["attempts"], 2)

    def test_enqueue_manual_not_due(self):
        job_id = self.jobs.enqueue_manual("grant", "req-1", error="人工处理")
        job = self._job(job_id)
        self.assertEqual(job["status"], "manual")
        self.assertEqual(self.storage.due_jobs(), [])

    # ---------- 注册与执行 ----------
    def test_register_handler_and_run_due(self):
        self.jobs.register_handler("grant", lambda ref: self.calls.append(ref) or {"ok": True})
        job_id = self.jobs.enqueue("grant", "req-1")
        summary = self.jobs.run_due()
        self.assertEqual(summary["done"], 1)
        self.assertEqual(self.calls, ["req-1"])
        self.assertEqual(self._job(job_id)["status"], "done")
        self.assertEqual(self.storage.due_jobs(), [])

    def test_missing_handler_goes_manual(self):
        job_id = self.jobs.enqueue("unknown", "ref-1")
        summary = self.jobs.run_due()
        self.assertEqual(summary["manual"], 1)
        job = self._job(job_id)
        self.assertEqual(job["status"], "manual")
        self.assertIn("未注册处理函数", job["last_error"])

    def test_has_handler(self):
        self.assertFalse(self.jobs.has_handler("grant"))
        self.jobs.register_handler("grant", lambda ref: None)
        self.assertTrue(self.jobs.has_handler("grant"))
        with self.assertRaises(TypeError):
            self.jobs.register_handler("bad", "not-callable")

    # ---------- 退避 ----------
    def test_retryable_failure_backoff_sequence_until_manual(self):
        attempts = {"n": 0}

        def failing(ref):
            attempts["n"] += 1
            raise ApiError(500, "boom")

        self.jobs.register_handler("grant", failing)
        job_id = self.jobs.enqueue("grant", "req-1")

        # 第 1 次失败：attempts=1，60s 后重试
        before = datetime.now().astimezone()
        self.jobs.run_due(now=before.isoformat(timespec="seconds"))
        job = self._job(job_id)
        self.assertEqual(job["status"], "queued")
        self.assertEqual(job["attempts"], 1)
        first_next = datetime.fromisoformat(job["next_run_at"])
        gap1 = (first_next - before).total_seconds()
        self.assertGreaterEqual(gap1, 59)
        self.assertLessEqual(gap1, 61)

        # 第 2 次失败：attempts=2，300s 后重试
        self.jobs.run_due(now=first_next.isoformat(timespec="seconds"))
        job = self._job(job_id)
        self.assertEqual(job["attempts"], 2)
        second_next = datetime.fromisoformat(job["next_run_at"])
        gap2 = (second_next - first_next).total_seconds()
        self.assertGreaterEqual(gap2, 299)
        self.assertLessEqual(gap2, 301)

        # 第 3 次失败：attempts=3，900s 后重试
        self.jobs.run_due(now=second_next.isoformat(timespec="seconds"))
        job = self._job(job_id)
        self.assertEqual(job["attempts"], 3)
        self.assertEqual(job["status"], "queued")
        third_next = datetime.fromisoformat(job["next_run_at"])
        gap3 = (third_next - second_next).total_seconds()
        self.assertGreaterEqual(gap3, 899)
        self.assertLessEqual(gap3, 901)

        # 第 4 次失败：attempts=4 > 3 → manual
        self.jobs.run_due(now=third_next.isoformat(timespec="seconds"))
        job = self._job(job_id)
        self.assertEqual(job["attempts"], 4)
        self.assertEqual(job["status"], "manual")
        self.assertEqual(attempts["n"], 4)

    def test_backoff_gap_is_300_seconds(self):
        def failing(ref):
            raise ApiError("NETWORK", "timeout")

        self.jobs.register_handler("grant", failing)
        job_id = self.jobs.enqueue("grant", "req-1")
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        self.jobs.run_due(now=now)
        first_next = datetime.fromisoformat(self._job(job_id)["next_run_at"])
        self.jobs.run_due(now=first_next.isoformat(timespec="seconds"))
        second_next = datetime.fromisoformat(self._job(job_id)["next_run_at"])
        self.assertGreaterEqual((second_next - first_next).total_seconds(), 299)
        self.assertLessEqual((second_next - first_next).total_seconds(), 301)

    def test_non_retryable_goes_manual_immediately(self):
        def failing(ref):
            raise BusinessError("用户未映射")

        self.jobs.register_handler("grant", failing)
        job_id = self.jobs.enqueue("grant", "req-1")
        summary = self.jobs.run_due()
        self.assertEqual(summary["manual"], 1)
        job = self._job(job_id)
        self.assertEqual(job["status"], "manual")
        self.assertEqual(job["attempts"], 1)

    def test_lock_timeout_is_retryable(self):
        self.assertTrue(is_retryable(LockTimeout("忙")))

    def test_error_classification(self):
        self.assertTrue(is_retryable(ApiError(500, "boom")))
        self.assertTrue(is_retryable(ApiError(503, "boom")))
        self.assertTrue(is_retryable(ApiError(429, "limit")))
        self.assertTrue(is_retryable(ApiError("NETWORK", "timeout")))
        self.assertFalse(is_retryable(ApiError(403, "forbidden")))
        self.assertFalse(is_retryable(ApiError("BATCH", "业务失败")))
        self.assertFalse(is_retryable(BusinessError("校验失败")))
        self.assertTrue(is_retryable(RuntimeError("未知")))

    def test_one_failure_does_not_block_others(self):
        calls = []

        def handler(ref):
            if ref == "bad":
                raise ApiError(500, "boom")
            calls.append(ref)

        self.jobs.register_handler("grant", handler)
        self.jobs.enqueue("grant", "bad")
        self.jobs.enqueue("grant", "good")
        summary = self.jobs.run_due()
        self.assertEqual(summary["done"], 1)
        self.assertEqual(summary["retried"], 1)
        self.assertEqual(calls, ["good"])

    def test_run_due_respects_limit_and_ordering(self):
        self.jobs.register_handler("grant", lambda ref: {"ok": True})
        first = self.storage.enqueue_job("grant", "r1", "2020-01-01T00:00:00+08:00")
        second = self.storage.enqueue_job("grant", "r2", "2020-01-02T00:00:00+08:00")
        summary = self.jobs.run_due(limit=1)
        self.assertEqual(summary["scanned"], 1)
        self.assertEqual(self._job(first)["status"], "done")
        self.assertEqual(self._job(second)["status"], "queued")

    def test_handler_can_raise_retryable_and_recover(self):
        state = {"fail": True}

        def handler(ref):
            if state["fail"]:
                state["fail"] = False
                raise ApiError(500, "temporary")
            return {"ok": True}

        self.jobs.register_handler("grant", handler)
        job_id = self.jobs.enqueue("grant", "req-1")
        self.jobs.run_due()
        self.assertEqual(self._job(job_id)["status"], "queued")
        self.jobs.run_due(now=add_seconds(self._job(job_id)["next_run_at"], 1))
        self.assertEqual(self._job(job_id)["status"], "done")

    def test_add_seconds(self):
        self.assertEqual(add_seconds("2026-01-01T00:00:00+08:00", 60),
                         "2026-01-01T00:01:00+08:00")

    # ---------- 返回失败结果（不抛异常）----------
    def test_failed_result_triggers_retry(self):
        from types import SimpleNamespace

        def handler(ref):
            return SimpleNamespace(status="failed",
                                   item_results=[{"status": "failed", "retryable": True}])

        self.jobs.register_handler("grant", handler)
        job_id = self.jobs.enqueue("grant", "req-1")
        summary = self.jobs.run_due()
        self.assertEqual(summary["retried"], 1)
        job = self._job(job_id)
        self.assertEqual(job["status"], "queued")
        self.assertEqual(job["attempts"], 1)

    def test_failed_result_non_retryable_goes_manual(self):
        from types import SimpleNamespace

        def handler(ref):
            return SimpleNamespace(status="failed",
                                   item_results=[{"status": "failed", "retryable": False}])

        self.jobs.register_handler("grant", handler)
        job_id = self.jobs.enqueue("grant", "req-1")
        self.jobs.run_due()
        self.assertEqual(self._job(job_id)["status"], "manual")

    def test_successful_result_marks_done(self):
        from types import SimpleNamespace

        def handler(ref):
            return SimpleNamespace(status="granted", item_results=[])

        self.jobs.register_handler("grant", handler)
        job_id = self.jobs.enqueue("grant", "req-1")
        self.jobs.run_due()
        self.assertEqual(self._job(job_id)["status"], "done")

    def test_has_open_job(self):
        job_id = self.jobs.enqueue("grant", "req-1")
        self.assertTrue(self.jobs.has_open_job("grant", "req-1"))
        self.assertFalse(self.jobs.has_open_job("grant", "req-2"))
        self.jobs.register_handler("grant", lambda ref: {"ok": True})
        self.jobs.run_due()
        self.assertFalse(self.jobs.has_open_job("grant", "req-1"))
        self.assertEqual(self._job(job_id)["status"], "done")

    def test_has_manual_job(self):
        self.assertFalse(self.jobs.has_manual_job("grant", "req-1"))
        self.jobs.enqueue("grant", "req-1")
        self.assertFalse(self.jobs.has_manual_job("grant", "req-1"))
        self.jobs.enqueue_manual("grant", "req-2", error="转人工")
        self.assertTrue(self.jobs.has_manual_job("grant", "req-2"))
        self.assertFalse(self.jobs.has_open_job("grant", "req-2"))

    def test_failed_result_last_error_contains_item_cause(self):
        """D-04：转 manual 时 last_error 带上首条失败条目的 error_code/error。"""
        from types import SimpleNamespace

        def handler(ref):
            return SimpleNamespace(status="failed", item_results=[{
                "status": "failed", "retryable": False,
                "resource_type": "table", "resource_id": "t-001",
                "error_code": "E1003",
                "error": "BusinessError: 用户 10086 未映射",
            }])

        self.jobs.register_handler("grant", handler)
        job_id = self.jobs.enqueue("grant", "req-1")
        self.jobs.run_due()
        job = self._job(job_id)
        self.assertEqual(job["status"], "manual")
        self.assertIn("E1003", job["last_error"])
        self.assertIn("未映射", job["last_error"])
        self.assertIn("table:t-001", job["last_error"])


if __name__ == "__main__":
    unittest.main()
