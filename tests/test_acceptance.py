# -*- coding: utf-8 -*-
"""验收用例映射：需求书 §11.3 的 15 条验收用例（P2 范围内可自动化的部分）。

每条用例对应 ``docs/testing/验收用例.md`` §10.1 的映射关系，使用与
``tests/integration`` 相同的真实服务编排 + Fake 下游，在本地无网络环境执行。

说明：
- 需求书 §11.3 #11（非法父子目录组合）当前实现未提供校验器（UC-GRN-10 / G-03），
  本文件不写假通过用例，未覆盖情况见 ``docs/testing/测试报告.md``。
- #10 的“拒绝实例记 requests”尚未实现（G-02），本文件只验证“不授权、不建台账”。
"""
import os
import sys
import unittest
from datetime import datetime

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from integration.harness import (IntegrationHarness, folder_request, form,  # noqa: E402
                                 full_authority, resource, row_rule)
from executor.errors import ApiError, BusinessError  # noqa: E402
from executor.feishu.form_parser import FormParseError  # noqa: E402
from executor.models import PermissionRequest  # noqa: E402
from executor.storage import expire_at_from_days  # noqa: E402


class AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.h = IntegrationHarness()

    def tearDown(self):
        self.h.close()

    # ------------------------------------------------------------------
    # #1 低风险文件夹使用 90 天（E2E-01 / UC-GRN-02 / UC-LED-01/02）
    # ------------------------------------------------------------------
    def test_ac01_low_risk_folder_90days(self):
        self.h.add_instance("INST-ACC01", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"], days="90天"))
        summary = self.h.poll_once()
        self.assertEqual(summary["granted"], 1, summary["errors"])
        ledgers = self.h.ledger_rows(user="10086")
        self.assertEqual(len(ledgers), 1)
        self.assertEqual(ledgers[0]["resource_type"], "folder")
        self.assertEqual(ledgers[0]["payload"]["authority"],
                         {"usePrivilege": True, "biData": True, "biView": True})
        expire = datetime.fromisoformat(ledgers[0]["expire_at"])
        days = (expire - datetime.now().astimezone()).total_seconds() / 86400.0
        self.assertGreaterEqual(days, 89.0)
        self.assertLessEqual(days, 91.0)
        self.assertTrue(self.h.finebi.folder[("10086", "p-001")]["usePrivilege"])
        request = self.h.request_rows()[0]
        self.assertEqual(request["status"], "done")
        self.assertEqual(request["user"], "10086")
        self.assertEqual(request["instance_code"], "INST-ACC01")

    # ------------------------------------------------------------------
    # #2 重复申请同一权限（E2E-02 / UC-GRN-08 / UC-APP-06）
    # ------------------------------------------------------------------
    def test_ac02_duplicate_application_is_idempotent(self):
        for code in ("INST-ACC02-A", "INST-ACC02-B"):
            self.h.add_instance(code, form(
                resources=[resource("销售文件夹", "p-001", "文件夹使用")],
                actions=["使用"]))
        summary = self.h.poll_once()
        self.assertEqual(summary["found"], 2)
        self.assertEqual(summary["granted"], 1)
        self.assertEqual(summary["skipped"], 1)
        self.assertEqual(self.h.finebi.count("set_folder"), 1)
        self.assertEqual(len(self.h.ledger_rows()), 1)
        # 同一实例重复轮询不重复授权（E2E-02）
        again = self.h.poll_once()
        self.assertEqual(again["granted"], 0)
        self.assertEqual(again["skipped"], 2)
        self.assertEqual(self.h.finebi.count("set_folder"), 1)

    # ------------------------------------------------------------------
    # #3 行权限两单叠加（E2E-03 / UC-GRN-03）
    # ------------------------------------------------------------------
    def test_ac03_row_permissions_two_orders_union(self):
        for code, scope in (("INST-ACC03-A", "大区=华东"),
                            ("INST-ACC03-B", "大区=华南")):
            self.h.add_instance(code, form(
                resources=[resource("销售数据集", "t-001", "行权限")],
                actions=["使用"], scope=scope))
        summary = self.h.poll_once()
        self.assertEqual(summary["granted"], 2, summary["errors"])
        written = self.h.finebi.row[("10086", "t-001")]
        values = sorted(rule["filterValue"] for rule in written["filterValue"])
        self.assertEqual(values, [["华东"], ["华南"]])
        self.assertEqual(
            len([l for l in self.h.ledger_rows() if l["resource_type"] == "row"]),
            2)

    # ------------------------------------------------------------------
    # #4 回收其中一单（UC-REV-02 / E2E-03）
    # ------------------------------------------------------------------
    def test_ac04_revoke_one_row_order_keeps_other(self):
        self.h.grant_instance("INST-ACC04-A", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华东"))
        self.h.grant_instance("INST-ACC04-B", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华南"))
        row_ledgers = [l for l in self.h.ledger_rows()
                       if l["resource_type"] == "row"]
        self.h.revoke.revoke_ledger(row_ledgers[0], reason="回收单1")
        remaining = self.h.finebi.row[("10086", "t-001")]["filterValue"]
        self.assertEqual([rule["filterValue"] for rule in remaining], [["华南"]])
        active_rows = [l for l in self.h.ledger_rows()
                       if l["resource_type"] == "row"]
        self.assertEqual([l["id"] for l in active_rows], [row_ledgers[1]["id"]])

    # ------------------------------------------------------------------
    # #5 到期回收（E2E-04 / UC-REV-01/02）
    # ------------------------------------------------------------------
    def test_ac05_expire_revokes_due_permission(self):
        self.h.grant_instance("INST-ACC05", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        ledger = self.h.ledger_rows()[0]
        self.h.storage.conn.execute(
            "UPDATE ledger SET expire_at=? WHERE id=?",
            ("2000-01-01T00:00:00+08:00", ledger["id"]))
        self.h.storage.conn.commit()
        results = self.h.expire.run_once()
        self.assertEqual(len(results), 1)
        self.assertFalse(self.h.finebi.folder[("10086", "p-001")]["usePrivilege"])
        self.assertEqual(self.h.ledger_rows(), [])
        row = [l for l in self.h.all_ledger_rows() if l["id"] == ledger["id"]][0]
        self.assertEqual(row["status"], "revoked")

    # ------------------------------------------------------------------
    # #6 列权限 / 仪表板导出与 view-export 互斥（UC-GRN-04/05）
    # ------------------------------------------------------------------
    def test_ac06_field_and_dashboard_view_export(self):
        self.h.add_instance("INST-ACC06-F", form(
            resources=[resource("客户手机号字段", "f-phone", "列权限")],
            actions=["组件数据"]))
        self.h.add_instance("INST-ACC06-V", form(
            resources=[resource("销售仪表板", "d-001", "仪表板查看")],
            actions=["查看"]))
        self.h.add_instance("INST-ACC06-E", form(
            resources=[resource("销售仪表板", "d-001", "仪表板导出")],
            actions=["导出"]))
        summary = self.h.poll_once()
        self.assertEqual(summary["granted"], 3, summary["errors"])
        self.assertTrue(self.h.finebi.field[("10086", "f-phone")])
        self.assertEqual(self.h.finebi.dash[("10086", "d-001")],
                         {"view": True, "export": True})
        # 非法“只导出不查看”当前自动补 view=true（验收口径要求记录实际行为）
        only_export = self.h.grant_instance("INST-ACC06-X", form(
            resources=[resource("销售仪表板", "d-002", "仪表板查看")],
            actions=["导出"]))
        self.assertEqual(only_export.status, "granted")
        self.assertEqual(self.h.finebi.dash[("10086", "d-002")],
                         {"view": True, "export": True})
        # 回收查看连带处理导出（只针对 d-001 的两条台账）
        d001 = [l for l in self.h.ledger_rows() if l["resource_id"] == "d-001"]
        view_ledger = [l for l in d001
                       if l["resource_type"] == "dashboard_view"][0]
        export_ledger = [l for l in d001
                         if l["resource_type"] == "dashboard_export"][0]
        self.h.revoke.revoke_ledger(view_ledger, reason="到期回收")
        self.h.revoke.revoke_ledger(export_ledger, reason="到期回收")
        self.assertEqual(self.h.finebi.dash[("10086", "d-001")],
                         {"view": False, "export": False})

    # ------------------------------------------------------------------
    # #7 角色自动分配（UC-GRN-07）
    # ------------------------------------------------------------------
    def test_ac07_role_auto_assignment(self):
        result = self.h.grant_instance("INST-ACC07", form(
            resources=[], actions=["使用"], role="电商-渠道运营",
            apply_type="角色"))
        self.assertEqual(result.status, "granted")
        self.assertIn("电商-渠道运营", self.h.platform.roles["10086"])
        role_ledgers = [l for l in self.h.ledger_rows()
                        if l["resource_type"] == "role"]
        self.assertEqual(len(role_ledgers), 1)
        self.assertEqual(role_ledgers[0]["resource_id"], "电商-渠道运营")
        # 回收后角色移除（无其他引用）
        self.h.revoke.revoke_ledger(role_ledgers[0], reason="到期回收")
        self.assertNotIn("电商-渠道运营",
                         self.h.platform.roles.get("10086", []))

    # ------------------------------------------------------------------
    # #8 离职（E2E-05 / UC-OFF-01～05）
    # ------------------------------------------------------------------
    def test_ac08_offboard_closure(self):
        self.h.grant_instance("INST-ACC08-F", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        self.h.grant_instance("INST-ACC08-T", form(
            resources=[resource("销售数据集", "t-001", "数据集使用")],
            actions=["使用"]))
        self.h.grant_instance("INST-ACC08-R", form(
            resources=[], actions=["使用"], role="电商-渠道运营",
            apply_type="角色"))
        summary = self.h.offboard.offboard("10086", accepter="10087")
        self.assertEqual(len(summary["revoked"]), 3)
        self.assertIn("handover_done", summary["steps"])
        self.assertTrue(summary["disabled"])
        self.assertEqual(self.h.ledger_rows(), [])
        self.assertFalse(self.h.finebi.folder[("10086", "p-001")]["usePrivilege"])
        self.assertFalse(self.h.finebi.table[("10086", "t-001")]["usePrivilege"])
        self.assertNotIn("电商-渠道运营",
                         self.h.platform.roles.get("10086", []))
        self.assertFalse(self.h.platform.enabled["10086"])
        # 清理报告所需字段齐全（resources/revoked/steps）
        for key in ("user", "accepter", "resources", "revoked", "steps"):
            self.assertIn(key, summary)

    # ------------------------------------------------------------------
    # #9 接口 500/超时：重试 3 次后转人工（UC-NOT-02 / S6）
    # ------------------------------------------------------------------
    def test_ac09_retry_three_times_then_manual(self):
        self.h.finebi.fail_methods["set_folder_permission"] = [
            ApiError(500, "boom") for _ in range(4)]
        result = self.h.permission.grant(folder_request())
        self.assertEqual(result.status, "failed")
        job = self.h.job_rows()[0]
        self.assertEqual(job["attempts"], 1)
        gaps = []
        for _ in range(3):
            job = self.h.job_rows()[0]
            next_at = job["next_run_at"]
            gaps.append((datetime.fromisoformat(next_at)
                         - datetime.now().astimezone()).total_seconds()
                        if not gaps else
                        (datetime.fromisoformat(next_at)
                         - datetime.fromisoformat(prev_at)).total_seconds())
            prev_at = next_at
            self.h.jobs.run_due(now=next_at)
        job = self.h.job_rows()[0]
        self.assertEqual(job["status"], "manual")
        self.assertEqual(job["attempts"], 4)
        self.assertGreaterEqual(gaps[0], 55)
        self.assertLessEqual(gaps[0], 65)
        self.assertGreaterEqual(gaps[1], 299)
        self.assertLessEqual(gaps[1], 301)
        self.assertGreaterEqual(gaps[2], 899)
        self.assertLessEqual(gaps[2], 901)
        self.assertTrue(self.h.notifier.admin_calls)
        self.assertIn("jobs", self.h.log_actions())

    # ------------------------------------------------------------------
    # #10 审批撤回/拒绝（V1.1 E1 修订；UC-APP-06）
    # ------------------------------------------------------------------
    def test_ac10_rejected_instance_has_no_authorization_or_ledger(self):
        rejected = self.h.add_instance("INST-ACC10-R", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]), status="REJECTED")
        self.assertEqual(rejected["status"], "REJECTED")
        with self.assertRaises(FormParseError):
            self.h.parser.parse_instance(rejected)
        # 轮询只查 APPROVED：拒绝实例不会被处理
        summary = self.h.poll_once()
        self.assertEqual(summary["found"], 0)
        self.assertEqual(self.h.ledger_rows(), [])
        self.assertEqual(self.h.request_rows(), [])
        self.assertEqual(self.h.finebi.count("set_"), 0)
        # 已知缺口 G-02：“拒绝实例记一条 requests”尚未实现，故此处 request_rows 为空

    # ------------------------------------------------------------------
    # #12 用户未映射（UC-GRN-01）
    # ------------------------------------------------------------------
    def test_ac12_unmapped_user_goes_manual_without_retry(self):
        self.h.finebi.fail_methods["set_folder_permission"] = [
            BusinessError("用户 10086 未映射到 FineBI 用户")]
        result = self.h.permission.grant(folder_request())
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.item_results[0]["error_code"], "E1003")
        job = self.h.job_rows()[0]
        self.assertEqual(job["status"], "manual")
        self.assertIn("未映射", job["last_error"])
        # 非重试类：不会被自动调度
        self.assertEqual(self.h.jobs.run_due()["scanned"], 0)
        self.assertEqual(self.h.ledger_rows(), [])

    # ------------------------------------------------------------------
    # #13 行权限清空（UC-REV-03 / POC-02）
    # ------------------------------------------------------------------
    def test_ac13_row_clear_manual_strategy(self):
        self.h.grant_instance("INST-ACC13-A", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华东"))
        self.h.grant_instance("INST-ACC13-B", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华南"))
        row_ledgers = [l for l in self.h.ledger_rows()
                       if l["resource_type"] == "row"]
        self.h.revoke.revoke_ledger(row_ledgers[0], reason="回收一单")
        detail = self.h.revoke.revoke_ledger(row_ledgers[1], reason="回收最后一单")
        self.assertTrue(detail["manual"])
        self.assertEqual(detail["ledger_status"], "failed")
        # manual 策略：不静默写空 filter，保留原规则并生成人工待办
        self.assertEqual(
            [r["filterValue"] for r in
             self.h.finebi.row[("10086", "t-001")]["filterValue"]],
            [["华南"]])
        jobs = self.h.job_rows()
        self.assertEqual(jobs[0]["kind"], "row_clear")
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.h.notifier.admin_calls)

    # ------------------------------------------------------------------
    # #14 对账差异清单（UC-REC-01）
    # ------------------------------------------------------------------
    def test_ac14_reconcile_reports_diff(self):
        expire_at = expire_at_from_days(30)
        ok_id = self.h.storage.add_ledger(
            "req-acc14", "10086", "folder", "p-ok",
            {"authority": {"usePrivilege": True}}, expire_at)
        bad_id = self.h.storage.add_ledger(
            "req-acc14", "10086", "folder", "p-bad",
            {"authority": {"usePrivilege": True}}, expire_at)
        publink_id = self.h.storage.add_ledger(
            "req-acc14", "10086", "publink", "publink",
            {"authority": {"biShareFun": True}}, expire_at)
        self.h.finebi.folder[("10086", "p-ok")] = full_authority(
            usePrivilege=True)
        self.h.finebi.folder[("10086", "p-bad")] = full_authority()

        diffs = {d["ledger_id"]: d for d in self.h.reconcile.run()}
        self.assertEqual(diffs[ok_id]["status"], "ok")
        self.assertEqual(diffs[bad_id]["status"], "mismatch")
        self.assertEqual(diffs[bad_id]["diff"]["usePrivilege"]["actual"], False)
        # 四类不可复核单列标注，不猜测
        self.assertEqual(diffs[publink_id]["status"], "unverifiable")

    # ------------------------------------------------------------------
    # #15 审计抽样 / traceId（UC-LED-03/04）
    # ------------------------------------------------------------------
    def test_ac15_audit_traceability(self):
        self.h.grant_instance("INST-ACC15", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        ledger = self.h.ledger_rows()[0]
        self.assertTrue(ledger["trace_id"].startswith("trace-"))
        # traceId 可从台账反查（接口响应 → ledger.trace_id）
        row = self.h.storage.conn.execute(
            "SELECT * FROM ledger WHERE trace_id=?",
            (ledger["trace_id"],)).fetchone()
        self.assertIsNotNone(row)
        # 申请单可追溯：来源实例号、用户、payload 均在 requests 表
        request = self.h.request_rows()[0]
        self.assertEqual(request["instance_code"], "INST-ACC15")
        self.assertEqual(request["user"], "10086")
        stored = self.h.request_row(request["id"])
        self.assertIn("source", stored["payload"])
        self.assertEqual(stored["payload"]["source"], "INST-ACC15")
        # 执行日志可按 action 检索，且 grant_item 日志包含资源与台账
        actions = self.h.log_actions()
        self.assertIn("grant", actions)
        self.assertIn("grant_item", actions)
        grant_item = [log for log in self.h.storage.recent_logs(100)
                      if log["action"] == "grant_item"][0]
        self.assertIn("folder:p-001", grant_item["payload"]["resource"])
        self.assertEqual(grant_item["payload"]["ledger_id"], ledger["id"])


if __name__ == "__main__":
    unittest.main()
