# -*- coding: utf-8 -*-
"""端到端集成测试（一）：审批实例 → FormParser → grant → ledger/request_items。

覆盖：多类型资源审批单、轮询全链路与重复轮询幂等、非 APPROVED/撤回拦截、
一张单多条目、存量直授权限（ADOPT_EXISTING false/true）、四类不可复核只按台账、
写后复核不一致（重写一次后转人工）、文件夹授权保留未涉及字段、行权限两单合并。
"""
import json
import unittest

from executor.errors import ApiError, BusinessError
from executor.feishu.form_parser import FormParseError
from executor.models import PermissionRequest

from .harness import (IntegrationHarness, folder_request, form, full_authority,
                      instance, resource)


class ApprovalGrantE2ETest(unittest.TestCase):
    def setUp(self):
        self.h = IntegrationHarness()

    def tearDown(self):
        self.h.close()

    # ---------- 工具 ----------
    def add_standard_instances(self):
        """登记 7 条审批实例：文件夹/数据集/列/行/仪表板查看/仪表板导出/角色。"""
        h = self.h
        h.add_instance("INST-FOLDER", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        h.add_instance("INST-TABLE", form(
            resources=[resource("销售数据集", "t-001", "数据集使用")],
            actions=["使用"]))
        h.add_instance("INST-FIELD", form(
            resources=[resource("客户手机号字段", "f-phone", "列权限")],
            actions=["组件数据"]))
        h.add_instance("INST-ROW", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华东"))
        h.add_instance("INST-DASH-VIEW", form(
            resources=[resource("销售仪表板", "d-001", "仪表板查看")],
            actions=["查看"]))
        h.add_instance("INST-DASH-EXPORT", form(
            resources=[resource("销售仪表板", "d-001", "仪表板导出")],
            actions=["导出"]))
        h.add_instance("INST-ROLE", form(
            resources=[], actions=["使用"], role="电商-渠道运营",
            apply_type="角色"))

    # ---------- 用例 ----------
    def test_poll_full_chain_writes_ledger_and_finebi_state(self):
        self.add_standard_instances()
        summary = self.h.poll_once()
        self.assertEqual(summary["found"], 7)
        self.assertEqual(summary["granted"], 7, summary["errors"])
        self.assertEqual(summary["failed"], 0, summary["errors"])

        # 台账：7 条 active，覆盖 7 类资源
        ledgers = self.h.ledger_rows()
        self.assertEqual(len(ledgers), 7)
        self.assertEqual({l["resource_type"] for l in ledgers},
                         {"folder", "table", "field", "row",
                          "dashboard_view", "dashboard_export", "role"})
        self.assertTrue(all(l["expire_at"] for l in ledgers))
        folder_ledger = [l for l in ledgers if l["resource_type"] == "folder"][0]
        self.assertTrue(folder_ledger["trace_id"].startswith("trace-"))

        # 申请单台账：7 条 done，且每条申请条目完成
        requests = self.h.request_rows()
        self.assertEqual(len(requests), 7)
        self.assertEqual({r["status"] for r in requests}, {"done"})
        self.assertEqual({r["instance_code"] for r in requests},
                         {"INST-FOLDER", "INST-TABLE", "INST-FIELD", "INST-ROW",
                          "INST-DASH-VIEW", "INST-DASH-EXPORT", "INST-ROLE"})
        for request in requests:
            items = self.h.item_rows(request["id"])
            self.assertEqual([item["status"] for item in items], ["done"])

        # FineBI 现状
        self.assertTrue(self.h.finebi.folder[("10086", "p-001")]["usePrivilege"])
        self.assertTrue(self.h.finebi.table[("10086", "t-001")]["usePrivilege"])
        self.assertTrue(self.h.finebi.field[("10086", "f-phone")])
        row_state = self.h.finebi.row[("10086", "t-001")]
        self.assertEqual(row_state["filterValue"][0]["fieldId"], "t_region")
        self.assertEqual(row_state["filterValue"][0]["filterValue"], ["华东"])
        self.assertEqual(self.h.finebi.dash[("10086", "d-001")],
                         {"view": True, "export": True})
        self.assertIn("电商-渠道运营", self.h.platform.roles["10086"])

    def test_poll_twice_is_idempotent(self):
        self.add_standard_instances()
        first = self.h.poll_once()
        self.assertEqual(first["granted"], 7)
        writes_before = self.h.finebi.count("set_")
        second = self.h.poll_once()
        self.assertEqual(second["found"], 7)
        self.assertEqual(second["granted"], 0)
        self.assertEqual(second["skipped"], 7)
        self.assertEqual(second["failed"], 0)
        # 不重复写、不重复台账
        self.assertEqual(self.h.finebi.count("set_"), writes_before)
        self.assertEqual(len(self.h.ledger_rows()), 7)
        self.assertEqual(len(self.h.request_rows()), 7)

    def test_non_approved_instance_is_refused(self):
        # 直接解析：非 APPROVED 一律拒绝（V1.1 §1.2）
        for status in ("REJECTED", "CANCELED", "REVERTED"):
            with self.assertRaises(FormParseError) as ctx:
                self.h.parser.parse_instance(instance(
                    "INST-" + status, form(
                        resources=[resource("销售文件夹", "p-001", "文件夹使用")],
                        actions=["使用"]), status=status))
            self.assertIn("APPROVED", str(ctx.exception))
        self.assertEqual(self.h.ledger_rows(), [])
        self.assertEqual(self.h.request_rows(), [])

    def test_poll_skips_instance_reverted_between_query_and_detail(self):
        """轮询查到实例后、取详情时状态已变（撤回）：不建单、不授权。"""
        code = "INST-STALE"
        self.h.feishu.add_instance(instance(code, form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]), status="REVERTED"))
        # 模拟查询结果仍返回该实例（状态在查询与详情之间变化）
        self.h.feishu.query_instances = lambda *a, **k: {
            "code": 0, "data": {"instance_list": [{"instance": {"code": code}}]}}
        summary = self.h.poll_once()
        self.assertEqual(summary["failed"], 1)
        self.assertIn("APPROVED", summary["errors"][0]["error"])
        self.assertEqual(self.h.storage.request_exists(code), False)
        self.assertEqual(self.h.ledger_rows(), [])
        self.assertEqual(self.h.finebi.count("set_"), 0)

    def test_multi_item_approval_creates_one_request_with_items(self):
        """一张审批单包含文件夹/数据集/行权限 + 角色，逐条目执行并写 request_items。"""
        result = self.h.grant_instance("INST-MULTI", form(
            resources=[
                resource("销售文件夹", "p-001", "文件夹使用"),
                resource("销售数据集", "t-001", "数据集使用"),
                resource("销售数据集", "t-001", "行权限"),
            ],
            actions=["使用"], scope="大区=华东", role="电商-渠道运营"))
        self.assertEqual(result.status, "granted", result.details)
        self.assertEqual(len(result.item_results), 4)  # 3 资源条目 + 1 角色条目
        self.assertEqual(len(result.ledger_ids), 4)
        items = self.h.item_rows(result.request_id)
        self.assertEqual(len(items), 4)
        self.assertEqual([item["status"] for item in items], ["done"] * 4)
        self.assertEqual([item["resource_type"] for item in items],
                         ["folder", "table", "row", "role"])
        self.assertEqual(self.h.request_row(result.request_id)["status"], "done")
        self.assertEqual(len(self.h.ledger_rows(user="10086")), 4)

    def test_multi_item_partial_failure_records_partial_status(self):
        self.h.finebi.fail_methods["set_table_permission"] = [ApiError(500, "boom")]
        result = self.h.grant_instance("INST-PARTIAL", form(
            resources=[
                resource("销售文件夹", "p-001", "文件夹使用"),
                resource("销售数据集", "t-001", "数据集使用"),
            ],
            actions=["使用"]))
        self.assertEqual(result.status, "partial")
        self.assertEqual(self.h.request_row(result.request_id)["status"], "partial")
        self.assertEqual([i["status"] for i in self.h.item_rows(result.request_id)],
                         ["done", "failed"])
        # 失败条目进入重试队列（1 次）
        jobs = self.h.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["status"], "queued")
        self.assertEqual(jobs[0]["attempts"], 1)

    def test_partial_failure_retry_only_retries_failed_items(self):
        """部分成功后重试：已成功条目不重复写，只补失败条目。"""
        self.h.finebi.fail_methods["set_table_permission"] = [ApiError(500, "boom")]
        result = self.h.grant_instance("INST-PARTIAL-RETRY", form(
            resources=[
                resource("销售文件夹", "p-001", "文件夹使用"),
                resource("销售数据集", "t-001", "数据集使用"),
            ],
            actions=["使用"]))
        self.assertEqual(result.status, "partial")
        job = self.h.job_rows()[0]
        summary = self.h.jobs.run_due(now=job["next_run_at"])
        self.assertEqual(summary["done"], 1)
        self.assertEqual(self.h.request_row(result.request_id)["status"], "done")
        # 已成功条目在重试时被幂等跳过，失败条目补齐
        self.assertEqual([i["status"] for i in
                          self.h.item_rows(result.request_id)],
                         ["skipped", "done"])
        self.assertEqual(self.h.finebi.count("set_folder"), 1)
        self.assertEqual(self.h.finebi.count("set_table"), 2)  # 失败 1 次 + 重试成功
        self.assertEqual(len(self.h.ledger_rows()), 2)

    def test_row_with_unparsable_existing_filter_goes_manual(self):
        """POC-3 映射未配置时，带存量数字结构行权限不猜测、转人工（设计修订 D4）。"""
        with IntegrationHarness(type_map={}) as harness:
            harness.finebi.row[("10086", "t-001")] = {
                "filterType": 35,
                "filterValue": [{"filterType": 10, "fieldId": "t_region",
                                 "filterValue": {"type": 1, "value": ["华东"]}}],
            }
            result = harness.grant_instance("INST-ROW-UNPARSABLE", form(
                resources=[resource("销售数据集", "t-001", "行权限")],
                actions=["使用"], scope="大区=华南"))
            self.assertEqual(result.status, "failed")
            self.assertIn("POC-3", result.item_results[0]["error"])
            self.assertEqual(harness.finebi.count("set_row"), 0)
            self.assertEqual(harness.job_rows()[0]["status"], "manual")

    def test_adopt_existing_false_skips_and_marks_reconcile_diff(self):
        """ADOPT_EXISTING=false：存量权限已满足但无台账 → skipped + SKIP_ADOPT + 通知。"""
        self.h.finebi.folder[("10086", "p-001")] = full_authority(
            usePrivilege=True, biData=True, biView=True)
        result = self.h.grant_instance("INST-ADOPT", form(
            resources=[resource("销售文件夹", "p-001", "文件夹使用")],
            actions=["使用"]))
        self.assertEqual(result.status, "skipped")
        item = result.item_results[0]
        self.assertEqual(item["status"], "skipped")
        self.assertEqual(item["error_code"], "SKIP_ADOPT")
        self.assertEqual(item["reconcile"], "diff")
        self.assertFalse(item["adopt_existing"])
        self.assertEqual(self.h.finebi.count("set_folder"), 0)
        self.assertEqual(self.h.ledger_rows(), [])
        self.assertIn("grant_adopt_skip", self.h.log_actions())
        self.assertTrue(self.h.notifier.admin_calls)
        self.assertIn("存量权限未纳管", self.h.notifier.admin_calls[0][0])
        # 已知缺口：reconcile 只扫描 active 台账，“无台账有权限”扫不出来（G-10）
        self.assertEqual(self.h.reconcile.run(), [])

    def test_adopt_existing_true_creates_baseline_ledger(self):
        with IntegrationHarness(adopt_existing=True) as harness:
            harness.finebi.folder[("10086", "p-001")] = full_authority(
                usePrivilege=True, biData=True, biView=True)
            result = harness.grant_instance("INST-ADOPT-TRUE", form(
                resources=[resource("销售文件夹", "p-001", "文件夹使用")],
                actions=["使用"]))
            self.assertEqual(result.status, "skipped")
            self.assertEqual(harness.finebi.count("set_folder"), 0)
            ledgers = harness.ledger_rows(user="10086")
            self.assertEqual(len(ledgers), 1)
            self.assertEqual(ledgers[0]["payload"]["origin"], "baseline")
            self.assertEqual(ledgers[0]["payload"]["authority"],
                             {"usePrivilege": True, "biData": True, "biView": True})

    def test_four_non_verifiable_resources_use_ledger_only(self):
        cases = [
            (PermissionRequest(user="10086", resource_type="publink",
                               resource_id="publink", days=90), "set_publink"),
            (PermissionRequest(user="10086", resource_type="dash_share",
                               resource_id="d-001", days=90), "share_dash"),
            (PermissionRequest(user="10086", resource_type="dashboard_data",
                               resource_id="entry-1", days=90,
                               extra={"entry": "entry-1"}), "set_dashboard_data"),
            (PermissionRequest(user="10086", resource_type="subject",
                               resource_id="s-001", days=90), "set_subject"),
        ]
        for request, write_prefix in cases:
            first = self.h.permission.grant(request)
            self.assertEqual(first.status, "granted", request.resource_type)
            self.assertEqual(self.h.finebi.count(write_prefix), 1,
                             request.resource_type)
            # 重复申请：无查询接口，只能按台账幂等
            second = self.h.permission.grant(PermissionRequest.from_dict(
                request.to_dict()))
            self.assertEqual(second.status, "skipped", request.resource_type)
            self.assertEqual(self.h.finebi.count(write_prefix), 1,
                             request.resource_type)
        # 全程没有任何 get 查询调用
        self.assertEqual(self.h.finebi.count("get_"), 0)
        # 对账：四类全部标 unverifiable
        diffs = self.h.reconcile.run()
        self.assertEqual(len(diffs), 4)
        self.assertEqual({d["status"] for d in diffs}, {"unverifiable"})
        self.assertTrue(all("无查询" in d["reason"] for d in diffs))

        # 回收：三类可自动收回，dash_share 只支持授予 → 转人工
        ledgers = {l["resource_type"]: l for l in self.h.ledger_rows()}
        publink = self.h.revoke.revoke_ledger(ledgers["publink"], reason="到期回收")
        self.assertEqual(publink.get("verifiable"), False)
        self.assertFalse(self.h.finebi.publink["10086"])
        subject = self.h.revoke.revoke_ledger(ledgers["subject"], reason="到期回收")
        self.assertFalse(subject.get("manual"))
        self.assertEqual(self.h.finebi.subject[("10086", "s-001")],
                         {"use": False, "edit": False})
        data = self.h.revoke.revoke_ledger(ledgers["dashboard_data"],
                                           reason="到期回收")
        self.assertFalse(data.get("manual"))
        self.assertFalse(self.h.finebi.dashboard_data[("10086", "entry-1")])
        shared = self.h.revoke.revoke_ledger(ledgers["dash_share"],
                                             reason="到期回收")
        self.assertTrue(shared.get("manual"))
        self.assertIn("人工", shared["warning"])
        self.assertEqual(self.h.ledger_rows(), [])

    def test_write_verify_mismatch_rewrites_once_then_manual(self):
        """写后复核不一致：重写一次仍不一致 → E3004 转人工（UC-GRN-09）。"""
        self.h.finebi.ignore_writes = True
        result = self.h.permission.grant(folder_request())
        self.assertEqual(result.status, "failed")
        self.assertEqual(self.h.finebi.count("set_folder"), 2)  # 写 + 重写一次
        item = result.item_results[0]
        self.assertIn("E3004", item["error"])
        jobs = self.h.job_rows()
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.h.notifier.admin_calls)

    def test_folder_grant_preserves_unrelated_authority_fields(self):
        self.h.finebi.folder[("10086", "p-001")] = full_authority(biData=True)
        result = self.h.permission.grant(folder_request(actions=["use"]))
        self.assertEqual(result.status, "granted")
        written = self.h.finebi.call_args("set_folder")[0][3]
        self.assertEqual(set(written),
                         {"usePrivilege", "managePrivilege", "empowerPrivilege",
                          "biData", "biView"})
        self.assertTrue(written["usePrivilege"])
        self.assertTrue(written["biData"])  # 未涉及的存量权限保留
        self.assertEqual(self.h.ledger_rows()[0]["payload"]["authority"],
                         {"usePrivilege": True, "biData": True, "biView": True})

    def test_row_permissions_from_two_approvals_merge(self):
        first = self.h.grant_instance("INST-ROW-A", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华东"))
        second = self.h.grant_instance("INST-ROW-B", form(
            resources=[resource("销售数据集", "t-001", "行权限")],
            actions=["使用"], scope="大区=华南"))
        self.assertEqual(first.status, "granted")
        self.assertEqual(second.status, "granted")
        written = self.h.finebi.row[("10086", "t-001")]
        values = sorted(rule["filterValue"] for rule in written["filterValue"])
        self.assertEqual(values, [["华东"], ["华南"]])
        row_ledgers = [l for l in self.h.ledger_rows()
                       if l["resource_type"] == "row"]
        self.assertEqual(len(row_ledgers), 2)

    def test_unknown_action_grant_is_skipped_without_write(self):
        """actions 为空 → 无法构建期望权限，跳过且不写。"""
        result = self.h.permission.grant(PermissionRequest(
            user="10086", resource_type="folder", resource_id="p-001",
            actions=[], days=90))
        self.assertEqual(result.status, "skipped")
        self.assertIn("未指定权限项", result.item_results[0]["reason"])
        self.assertEqual(self.h.finebi.count("set_folder"), 0)
        self.assertEqual(self.h.ledger_rows(), [])


if __name__ == "__main__":
    unittest.main()
