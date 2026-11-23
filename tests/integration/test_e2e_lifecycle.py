# -*- coding: utf-8 -*-
"""端到端集成测试（二）：授权后生命周期。

覆盖：幂等重复申请、行权限两单叠加与回收一单、最后一条行规则清空转人工、
仪表板 view/export 互斥与回收、四类不可复核权限、失败重试 1/5/15 分钟三次后转人工、
锁串行化与锁超时可重试、到期回收、离职交接/回收/禁用、对账差异。
"""
import threading
import unittest
from datetime import datetime

from executor.errors import ApiError, BusinessError
from executor.locks import ResourceLock
from executor.models import PermissionRequest
from executor.services.grant import PermissionService
from executor.storage import Storage, expire_at_from_days

from .fakes import FakeFineBI
from .harness import (IntegrationHarness, folder_request, form, full_authority,
                      resource, row_rule, table_request)


class LifecycleE2ETest(unittest.TestCase):
    def setUp(self):
        self.h = IntegrationHarness()

    def tearDown(self):
        self.h.close()

    # ---------- 幂等 ----------
    def test_duplicate_application_same_permission_is_idempotent(self):
        first = self.h.grant_instance("INST-DUP-1", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        second = self.h.grant_instance("INST-DUP-2", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        self.assertEqual(first.status, "granted")
        self.assertEqual(second.status, "skipped")
        self.assertIn("不重复写入", second.item_results[0]["reason"])
        self.assertEqual(self.h.finebi.count("set_folder"), 1)
        self.assertEqual(len(self.h.ledger_rows()), 1)
        # 两条申请单都有记录，但只有一条授权台账
        self.assertEqual(len(self.h.request_rows()), 2)
        statuses = {r["instance_code"]: r["status"]
                    for r in self.h.request_rows()}
        self.assertEqual(statuses, {"INST-DUP-1": "done", "INST-DUP-2": "done"})

    # ---------- 行权限叠加与回收 ----------
    def test_revoke_one_row_order_keeps_the_other(self):
        self.h.grant_instance("INST-ROW-A", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华东"))
        self.h.grant_instance("INST-ROW-B", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华南"))
        row_ledgers = [l for l in self.h.ledger_rows()
                       if l["resource_type"] == "row"]
        self.assertEqual(len(row_ledgers), 2)

        detail = self.h.revoke.revoke_ledger(row_ledgers[0], reason="到期回收")
        self.assertFalse(detail.get("manual"))
        remaining = self.h.finebi.row[("10086", "t-001")]["filterValue"]
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["filterValue"], ["华南"])
        active = [l for l in self.h.ledger_rows()
                  if l["resource_type"] == "row"]
        self.assertEqual([l["id"] for l in active], [row_ledgers[1]["id"]])
        revoked = [l for l in self.h.all_ledger_rows()
                   if l["id"] == row_ledgers[0]["id"]][0]
        self.assertEqual(revoked["status"], "revoked")

    def test_last_row_rule_cleared_goes_manual_with_job(self):
        """ROW_CLEAR_STRATEGY=manual：最后一条行规则清空不静默写空 filter。"""
        self.h.grant_instance("INST-ROW-ONLY", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华东"))
        ledger = self.h.ledger_rows()[0]
        detail = self.h.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail["manual"])
        self.assertEqual(detail["ledger_status"], "failed")
        # 不自动写空 filter，保留原规则等待人工确认
        self.assertEqual(
            self.h.finebi.row[("10086", "t-001")]["filterValue"],
            [row_rule(["华东"])])
        # 台账置 failed、生成 row_clear 人工待办、已通知管理员
        rows = {l["id"]: l for l in self.h.all_ledger_rows()}
        self.assertEqual(rows[ledger["id"]]["status"], "failed")
        jobs = self.h.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["kind"], "row_clear")
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.h.notifier.admin_calls)

    # ---------- 仪表板 view/export ----------
    def test_dashboard_view_export_mutex_and_revoke(self):
        view = self.h.grant_instance("INST-DASH-V", form(
            resources=[resource("销售仪表板", "d-001", "仪表板查看")],
            actions=["查看"]))
        export = self.h.grant_instance("INST-DASH-E", form(
            resources=[resource("销售仪表板", "d-001", "仪表板导出")],
            actions=["导出"]))
        self.assertEqual(view.status, "granted")
        self.assertEqual(export.status, "granted")
        self.assertEqual(self.h.finebi.dash[("10086", "d-001")],
                         {"view": True, "export": True})
        self.assertEqual(len(self.h.ledger_rows()), 2)

        ledgers = {l["resource_type"]: l for l in self.h.ledger_rows()}
        detail = self.h.revoke.revoke_ledger(ledgers["dashboard_view"],
                                             reason="到期回收")
        self.assertTrue(detail.get("skipped"))  # 导出台账仍引用查看
        self.assertEqual(self.h.finebi.dash[("10086", "d-001")],
                         {"view": True, "export": True})
        detail = self.h.revoke.revoke_ledger(ledgers["dashboard_export"],
                                             reason="到期回收")
        self.assertFalse(detail.get("skipped"))
        # 查看关闭时导出必须一起关闭（FR-GRN-05）
        self.assertEqual(self.h.finebi.dash[("10086", "d-001")],
                         {"view": False, "export": False})
        self.assertEqual(self.h.ledger_rows(), [])

    def test_dashboard_export_only_application_auto_adds_view(self):
        """只申请导出时当前实现自动补 view=true（验收口径要求记录实际行为）。"""
        result = self.h.grant_instance("INST-DASH-EXPORT-ONLY", form(
            resources=[resource("销售仪表板", "d-002", "仪表板查看")],
            actions=["导出"]))
        self.assertEqual(result.status, "granted")
        self.assertEqual(self.h.finebi.dash[("10086", "d-002")],
                         {"view": True, "export": True})
        self.assertIn("set_dash", [c[0] for c in self.h.finebi.calls])

    # ---------- 失败重试 ----------
    def test_retry_three_times_with_backoff_then_manual(self):
        self.h.finebi.fail_methods["set_folder_permission"] = [
            ApiError(500, "boom") for _ in range(4)]
        result = self.h.permission.grant(folder_request())
        self.assertEqual(result.status, "failed")
        job = self.h.job_rows()[0]
        self.assertEqual(job["status"], "queued")
        self.assertEqual(job["attempts"], 1)
        # 首次失败：60s 后重试
        first_gap = (datetime.fromisoformat(job["next_run_at"])
                     - datetime.now().astimezone()).total_seconds()
        self.assertGreaterEqual(first_gap, 55)
        self.assertLessEqual(first_gap, 65)

        expected_gaps = [300, 900]
        for index, expected_gap in enumerate(expected_gaps):
            job = self.h.job_rows()[0]
            next_at = job["next_run_at"]
            summary = self.h.jobs.run_due(now=next_at)
            self.assertEqual(summary["retried"], 1)
            job = self.h.job_rows()[0]
            self.assertEqual(job["status"], "queued")
            self.assertEqual(job["attempts"], index + 2)
            gap = (datetime.fromisoformat(job["next_run_at"])
                   - datetime.fromisoformat(next_at)).total_seconds()
            self.assertGreaterEqual(gap, expected_gap - 1)
            self.assertLessEqual(gap, expected_gap + 1)

        # 第 3 次重试仍失败（累计失败 4 次）→ 转人工
        job = self.h.job_rows()[0]
        summary = self.h.jobs.run_due(now=job["next_run_at"])
        self.assertEqual(summary["manual"], 1)
        job = self.h.job_rows()[0]
        self.assertEqual(job["status"], "manual")
        self.assertEqual(job["attempts"], 4)
        # 任务 last_error 只记录“处理函数返回失败状态”，具体原因需查 request_items/logs
        self.assertTrue(job["last_error"])
        items = self.h.item_rows(result.request_id)
        self.assertIn("boom", items[0]["error_msg"])
        self.assertEqual(self.h.request_row(result.request_id)["status"], "failed")
        self.assertTrue(self.h.notifier.admin_calls)

        # 人工修复后可重新执行（manual 任务不会被自动调度）
        self.assertEqual(self.h.storage.due_jobs(), [])
        fixed = self.h.permission.grant(PermissionRequest.from_dict(
            self.h.storage.get_request(result.request_id)["payload"]))
        self.assertEqual(fixed.status, "granted")
        self.assertEqual(self.h.request_row(result.request_id)["status"], "done")

    def test_retry_recovers_when_downstream_recovers(self):
        self.h.finebi.fail_methods["set_table_permission"] = [ApiError(503, "busy")]
        result = self.h.permission.grant(table_request())
        self.assertEqual(result.status, "failed")
        job = self.h.job_rows()[0]
        self.h.jobs.run_due(now=job["next_run_at"])
        job = self.h.job_rows()[0]
        self.assertEqual(job["status"], "done")
        self.assertEqual(self.h.request_row(result.request_id)["status"], "done")
        self.assertTrue(self.h.finebi.table[("10086", "t-001")]["usePrivilege"])
        self.assertEqual(len(self.h.ledger_rows()), 1)

    def test_non_retryable_failure_goes_manual_without_retry(self):
        """用户未映射等业务错误：直接转人工，不重试（FR-GRN-01）。"""
        self.h.finebi.fail_methods["set_folder_permission"] = [
            BusinessError("FineBI 用户不存在：10086")]
        result = self.h.permission.grant(folder_request())
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.item_results[0]["error_code"], "E1003")
        jobs = self.h.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertEqual(jobs[0]["attempts"], 4)
        # 后续调度不会再碰这个任务
        self.assertEqual(self.h.jobs.run_due()["scanned"], 0)
        self.assertTrue(self.h.notifier.admin_calls)

    # ---------- 锁 ----------
    def test_resource_lock_serializes_concurrent_grants(self):
        first_storage = self.h.storage
        second_storage = Storage(self.h.db_path)
        second = PermissionService(
            self.h.finebi, second_storage, platform=self.h.platform,
            lock=self.h.lock, notifier=self.h.notifier, jobs=self.h.jobs,
            type_map=self.h.type_map)
        self.h.finebi.write_delay = 0.15
        barrier = threading.Barrier(2)
        results = []

        def worker(service, action):
            barrier.wait()
            results.append(service.grant(folder_request(actions=[action])))

        threads = [
            threading.Thread(target=worker,
                             args=(self.h.permission, "use")),
            threading.Thread(target=worker,
                             args=(second, "manage")),
        ]
        try:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=20)
        finally:
            second_storage.close()
        self.assertEqual(len(results), 2)
        self.assertEqual([r.status for r in results], ["granted", "granted"])
        # 同一资源同一时刻只允许一个写操作（锁串行化）
        self.assertEqual(self.h.finebi.concurrent_write_violations, 0)
        self.assertEqual(self.h.finebi.count("set_folder"), 2)
        self.assertEqual(len(self.h.ledger_rows()), 2)
        final = self.h.finebi.folder[("10086", "p-001")]
        self.assertTrue(final["usePrivilege"])
        self.assertTrue(final["managePrivilege"])

    def test_lock_timeout_is_retryable_and_succeeds_after_release(self):
        harness = IntegrationHarness(lock_wait=0.2)
        try:
            holder = ResourceLock(harness.db_path, ttl=120, wait=1)
            key = "fb_user:10086:folder:p-001"
            holder.acquire(key, "external-holder")
            try:
                result = harness.permission.grant(folder_request())
            finally:
                holder.release(key, "external-holder")
            self.assertEqual(result.status, "failed")
            item = result.item_results[0]
            self.assertEqual(item["error_code"], "E5001")
            self.assertTrue(item["retryable"])
            job = harness.job_rows()[0]
            self.assertEqual(job["status"], "queued")
            # 锁释放后重试成功
            harness.jobs.run_due(now=job["next_run_at"])
            self.assertEqual(len(harness.ledger_rows()), 1)
            self.assertEqual(harness.job_rows()[0]["status"], "done")
        finally:
            harness.close()

    # ---------- 到期回收 ----------
    def test_expire_revokes_due_ledger_only(self):
        self.h.grant_instance("INST-EXPIRE-F", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        self.h.grant_instance("INST-EXPIRE-T", form(
            resources=[resource("销售数据集", "t-001", "数据集使用")],
            actions=["使用"]))
        ledgers = {l["resource_type"]: l for l in self.h.ledger_rows()}
        self.h.storage.conn.execute(
            "UPDATE ledger SET expire_at=? WHERE id=?",
            ("2000-01-01T00:00:00+08:00", ledgers["table"]["id"]))
        self.h.storage.conn.commit()

        results = self.h.expire.run_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ledger_id"], ledgers["table"]["id"])
        self.assertEqual(len(self.h.ledger_rows()), 1)
        self.assertEqual(self.h.ledger_rows()[0]["resource_type"], "folder")
        # 到期权限回收：五字段置 false 且不误伤其他字段
        table_state = self.h.finebi.table[("10086", "t-001")]
        self.assertFalse(table_state["usePrivilege"])
        self.assertTrue(self.h.finebi.folder[("10086", "p-001")]["usePrivilege"])
        rows = {l["id"]: l for l in self.h.all_ledger_rows()}
        self.assertEqual(rows[ledgers["table"]["id"]]["status"], "revoked")

    # ---------- 离职 ----------
    def test_offboard_handover_revoke_all_and_disable(self):
        self.h.grant_instance("INST-OFF-F", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        self.h.grant_instance("INST-OFF-T", form(
            resources=[resource("销售数据集", "t-001", "数据集使用")],
            actions=["使用"]))
        self.h.grant_instance("INST-OFF-R", form(
            resources=[], actions=["使用"], role="电商-渠道运营",
            apply_type="角色"))
        self.assertEqual(len(self.h.ledger_rows()), 3)
        self.assertIn("电商-渠道运营", self.h.platform.roles["10086"])

        summary = self.h.offboard.offboard("10086", accepter="10087")
        # 资源交接
        self.assertEqual(summary["resources"]["packs"], ["p-handover"])
        self.assertEqual(summary["resources"]["tables"], ["t-handover"])
        self.assertEqual(summary["resources"]["subjects"], ["s-handover"])
        self.assertEqual(self.h.finebi.handover_start_args["accepter"], "10087")
        self.assertEqual(self.h.finebi.handover_start_args["analysis_pack_ids"],
                         ["p-handover"])
        self.assertEqual(self.h.finebi.handover_start_args["pack_ids"], [])
        self.assertIn("handover_done", summary["steps"])
        # 台账全部回收、FineBI 权限清零、角色移除、账号禁用
        self.assertEqual(summary["steps"].count("permissions_revoked"), 1)
        self.assertEqual(len(summary["revoked"]), 3)
        self.assertEqual(self.h.ledger_rows(), [])
        self.assertEqual({row["status"] for row in self.h.all_ledger_rows()},
                         {"revoked"})
        self.assertFalse(self.h.finebi.folder[("10086", "p-001")]["usePrivilege"])
        self.assertFalse(self.h.finebi.table[("10086", "t-001")]["usePrivilege"])
        self.assertNotIn("电商-渠道运营", self.h.platform.roles.get("10086", []))
        self.assertTrue(summary["disabled"])
        self.assertFalse(self.h.platform.enabled["10086"])
        self.assertTrue(self.h.notifier.admin_calls)

    # ---------- 对账 ----------
    def test_reconcile_reports_ok_mismatch_and_unverifiable(self):
        expire_at = expire_at_from_days(30)
        ok_id = self.h.storage.add_ledger(
            "req-manual", "10086", "folder", "p-ok",
            {"authority": {"usePrivilege": True}}, expire_at)
        bad_id = self.h.storage.add_ledger(
            "req-manual", "10086", "folder", "p-bad",
            {"authority": {"usePrivilege": True}}, expire_at)
        export_id = self.h.storage.add_ledger(
            "req-manual", "10086", "dashboard_export", "d-001",
            {"authority": {"view": True, "export": True}}, expire_at)
        publink_id = self.h.storage.add_ledger(
            "req-manual", "10086", "publink", "publink",
            {"authority": {"biShareFun": True}}, expire_at)
        row_id = self.h.storage.add_ledger(
            "req-manual", "10086", "row", "t-001",
            {"rules": [row_rule(["华东"])]}, expire_at)
        self.h.finebi.folder[("10086", "p-ok")] = full_authority(
            usePrivilege=True)
        self.h.finebi.folder[("10086", "p-bad")] = full_authority()
        self.h.finebi.dash[("10086", "d-001")] = {"view": True, "export": False}

        diffs = {d["ledger_id"]: d for d in self.h.reconcile.run()}
        self.assertEqual(set(diffs),
                         {ok_id, bad_id, export_id, publink_id, row_id})
        self.assertEqual(diffs[ok_id]["status"], "ok")
        self.assertEqual(diffs[bad_id]["status"], "mismatch")
        self.assertEqual(diffs[bad_id]["diff"]["usePrivilege"],
                         {"expected": True, "actual": False})
        self.assertEqual(diffs[export_id]["status"], "mismatch")
        self.assertEqual(diffs[export_id]["diff"]["export"],
                         {"expected": True, "actual": False})
        self.assertEqual(diffs[publink_id]["status"], "unverifiable")
        self.assertEqual(diffs[publink_id]["reason"], "接口无查询能力")

        # 行权限：POC-3 映射未配置时对账标 unverifiable，不猜测
        unmapped = {d["ledger_id"]: d
                    for d in self.h.reconcile_unmapped.run()}
        self.assertEqual(unmapped[row_id]["status"], "unverifiable")
        self.assertIn("POC-3", unmapped[row_id]["reason"])

    def test_dry_run_never_writes_or_creates_ledger(self):
        harness = IntegrationHarness(dry_run=True)
        try:
            result = harness.grant_instance("INST-DRY", form(
                resources=[resource("销售文件夹", "p-001", "文件夹使用")],
                actions=["使用"]))
            self.assertEqual(result.status, "skipped")
            self.assertTrue(result.details["dry_run"])
            self.assertEqual(harness.finebi.count("set_"), 0)
            self.assertEqual(harness.ledger_rows(), [])
            items = harness.item_rows(result.request_id)
            self.assertEqual([i["status"] for i in items], ["skipped"])
        finally:
            harness.close()


if __name__ == "__main__":
    unittest.main()
