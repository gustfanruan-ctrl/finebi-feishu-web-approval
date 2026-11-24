# -*- coding: utf-8 -*-
"""P2 授权 / 回收服务单测：handler 注册表、锁、幂等、台账、重试、行权限重算、角色引用。"""
import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta

from executor.errors import ApiError, BusinessError
from executor.feishu.form_parser import FormParser
from executor.models import PermissionRequest
from executor.services.grant import PermissionService
from executor.services.jobs import (JobService, KIND_GRANT, KIND_ROW_CLEAR,
                                    KIND_SHARE_REVOKE)
from executor.services.poller import ApprovalPoller
from executor.services.revoke import RevokeService
from executor.storage import Storage, expire_at_from_days

FULL_AUTHORITY = {"usePrivilege", "managePrivilege", "empowerPrivilege",
                  "biData", "biView"}

# POC-3 待实测的 filterType 映射（测试用）
NUMERIC_TYPE_MAP = {35: "or", 34: "and", 10: "strIn", 12: "strNotIn"}


def numeric_row_filter(*values):
    """模拟 FineBI get 接口返回的数字 filterType 结构（每个值一个条件节点）。"""
    return {"filterType": 35, "filterValue": [
        {"filterType": 10, "fieldId": "t_region",
         "filterValue": {"type": 1, "value": [value]}} for value in values]}


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------
class FakeFineBI:
    """纯内存 FineBI 客户端；支持故障注入与“写成功但不生效”模拟复核失败。"""

    def __init__(self):
        self.calls = []
        self.folder = {}
        self.table = {}
        self.row = {}
        self.field = {}
        self.dash = {}
        self.publink = {}
        self.subject = {}
        self.dashboard_data = {}
        self.dash_share = {}
        self.fail_methods = {}
        self.ignore_writes = False
        self.entry = {}

    def _maybe_fail(self, method):
        value = self.fail_methods.get(method)
        if not value:
            return
        if isinstance(value, list):
            raise value.pop(0)
        raise value

    @staticmethod
    def _wrap(data):
        return {"data": [{"status": True, "data": data}]}

    # 文件夹
    def get_folder_permission(self, user, rid):
        self.calls.append(("get_folder", user, rid))
        self._maybe_fail("get_folder_permission")
        return self._wrap(self.folder.get((user, rid), {}))

    def set_folder_permission(self, user, rid, authority):
        self.calls.append(("set_folder", user, rid, dict(authority)))
        self._maybe_fail("set_folder_permission")
        if not self.ignore_writes:
            self.folder[(user, rid)] = dict(authority)
        return {"traceId": "trace-folder", "data": [{"status": True, "data": "success"}]}

    # 数据集
    def get_table_permission(self, user, rid):
        self.calls.append(("get_table", user, rid))
        self._maybe_fail("get_table_permission")
        return self._wrap(self.table.get((user, rid), {}))

    def set_table_permission(self, user, rid, authority):
        self.calls.append(("set_table", user, rid, dict(authority)))
        self._maybe_fail("set_table_permission")
        if not self.ignore_writes:
            self.table[(user, rid)] = dict(authority)
        return {"data": [{"status": True, "data": "success"}]}

    # 列权限
    def get_field_permission(self, user, rid):
        self.calls.append(("get_field", user, rid))
        self._maybe_fail("get_field_permission")
        return self._wrap({"biData": self.field.get((user, rid), False)})

    def set_field_permission(self, user, rid, bi_data=True):
        self.calls.append(("set_field", user, rid, bi_data))
        self._maybe_fail("set_field_permission")
        if not self.ignore_writes:
            self.field[(user, rid)] = bool(bi_data)
        return {"ok": True}

    # 行权限
    def get_row_filter(self, user, rid):
        self.calls.append(("get_row", user, rid))
        self._maybe_fail("get_row_filter")
        return self._wrap(self.row.get((user, rid), ""))

    def set_row_filter(self, user, rid, row_filter):
        self.calls.append(("set_row", user, rid, dict(row_filter)))
        self._maybe_fail("set_row_filter")
        if not self.ignore_writes:
            self.row[(user, rid)] = dict(row_filter)
        return {"ok": True}

    # 仪表板模板认证
    def get_dashboard_template_auth(self, user, rid):
        self.calls.append(("get_dash", user, rid))
        self._maybe_fail("get_dashboard_template_auth")
        return self._wrap(self.dash.get((user, rid), {}))

    def set_dashboard_template_auth(self, user, rid, view, export=False):
        self.calls.append(("set_dash", user, rid, view, export))
        self._maybe_fail("set_dashboard_template_auth")
        if not self.ignore_writes:
            self.dash[(user, rid)] = {"view": bool(view), "export": bool(export)}
        return {"ok": True}

    # 四类不可复核
    def set_publink_share(self, user, enabled=True):
        self.calls.append(("set_publink", user, enabled))
        self._maybe_fail("set_publink_share")
        if not self.ignore_writes:
            self.publink[user] = bool(enabled)
        return {"ok": True}

    def share_dashboard(self, users, rid):
        self.calls.append(("share_dash", tuple(users), rid))
        self._maybe_fail("share_dashboard")
        return {"ok": True}

    def set_dashboard_data_permission(self, user, entry, bi_data=True):
        self.calls.append(("set_dashboard_data", user, entry, bi_data))
        self._maybe_fail("set_dashboard_data_permission")
        if not self.ignore_writes:
            self.dashboard_data[(user, entry)] = bool(bi_data)
        return {"ok": True}

    def set_subject_cooperation(self, user, subject, use=True, edit=False):
        self.calls.append(("set_subject", user, subject, use, edit))
        self._maybe_fail("set_subject_cooperation")
        if not self.ignore_writes:
            self.subject[(user, subject)] = {"use": bool(use), "edit": bool(edit)}
        return {"ok": True}

    # 目录权限（entry）
    def get_entry_authority(self, user, entry_ids):
        self.calls.append(("get_entry", user, tuple(entry_ids)))
        self._maybe_fail("get_entry_authority")
        entry_id = entry_ids[0] if entry_ids else ""
        authority = self.entry.get((user, entry_id), {
            "viewPrivilege": False, "export": False,
            "editPrivilege": False, "empowerPrivilege": False})
        return {"status": 200, "data": {"entry": [{
            "entryId": entry_id, "authority": dict(authority)}]}}

    def set_entry_authority(self, user, entry_id, authority):
        self.calls.append(("set_entry", user, entry_id, dict(authority)))
        self._maybe_fail("set_entry_authority")
        if not self.ignore_writes:
            self.entry[(user, entry_id)] = dict(authority)
        return {"status": 200, "data": [{"status": True}]}

    # 统计
    def count(self, prefix):
        return sum(1 for call in self.calls if call[0].startswith(prefix))


class FakePlatform:
    def __init__(self):
        self.calls = []
        self.roles = {}
        self.departments = {}   # username -> [[部门路径...], ...]
        self.fail_methods = {}
        self.platform_modules = {}
        self.schedules = {}
        self.entry_tree_nodes = []
        # 模拟 user/detail 的 username 模糊匹配：会在目标用户之外多返回这些条目
        self.extra_detail_items = {}

    def _maybe_fail(self, method):
        value = self.fail_methods.get(method)
        if value:
            raise value if not isinstance(value, list) else value.pop(0)

    def get_entry_tree(self, device="pc"):
        self.calls.append(("get_entry_tree", device))
        return {"data": self.entry_tree_nodes}

    def query_user_detail(self, username="", email="", mobile="", page=1, count=20):
        self.calls.append(("query_user", username))
        self._maybe_fail("query_user_detail")
        roles = [{"id": "r-" + name, "name": name}
                 for name in self.roles.get(username, [])]
        department_posts = [
            {"department": {"name": path[-1], "fullPath": "/".join(path)}}
            for path in self.departments.get(username, [])]
        items = [{"username": username, "roles": roles,
                  "departmentPosts": department_posts}]
        items.extend(self.extra_detail_items.get(username) or [])
        return {"data": {"total": len(items), "items": items}}

    def set_user_roles(self, user, add=None, remove=None):
        self.calls.append(("set_roles", user, list(add or []), list(remove or [])))
        self._maybe_fail("set_user_roles")
        names = self.roles.setdefault(user, [])
        for role in add or []:
            if role not in names:
                names.append(role)
        for role in remove or []:
            if role in names:
                names.remove(role)
        return {"ok": True}

    def set_user_departments(self, user, add=None, remove=None):
        self.calls.append(("set_departments", user, list(add or []), list(remove or [])))
        self._maybe_fail("set_user_departments")
        paths = self.departments.setdefault(user, [])
        for value in add or []:
            path = json.loads(value) if isinstance(value, str) else list(value)
            if path not in paths:
                paths.append(path)
        for value in remove or []:
            path = json.loads(value) if isinstance(value, str) else list(value)
            if path in paths:
                paths.remove(path)
        return {"ok": True}

    def set_user_platform_permission(self, user, module, use=True, empower=False):
        self.calls.append(("set_platform", user, module, bool(use), bool(empower)))
        self._maybe_fail("set_user_platform_permission")
        self.platform_modules.setdefault(user, {})[module] = (bool(use), bool(empower))
        return {"ok": True}

    def set_user_schedule_permission(self, user, schedule_task, manage=True,
                                     empower=False):
        self.calls.append(("set_schedule", user, schedule_task,
                           bool(manage), bool(empower)))
        self._maybe_fail("set_user_schedule_permission")
        self.schedules.setdefault(user, {})[schedule_task] = (bool(manage), bool(empower))
        return {"ok": True}


class FakeLock:
    def __init__(self):
        self.held = []
        self.released = []

    @contextmanager
    def hold(self, key, owner):
        self.held.append(key)
        try:
            yield
        finally:
            self.released.append(key)


class FakeNotifier:
    def __init__(self):
        self.admin_calls = []
        self.user_calls = []

    def notify_admins(self, title, content, link="", color="orange"):
        self.admin_calls.append((title, content))

    def notify_user(self, open_id, title, content, link="", color="blue"):
        self.user_calls.append((open_id, title, content))


class FakeFeishu:
    """审批轮询用 Fake：query_instances + get_instance。"""

    def __init__(self):
        self.instances = {}
        self.get_instance_calls = []

    def add_instance(self, code, data):
        self.instances[code] = data

    def query_instances(self, approval_code, status="APPROVED", start_ms=None,
                        end_ms=None, page_size=100, page_token=""):
        return {"data": {"instance_list": [
            {"instance": {"code": code}} for code in self.instances]}}

    def get_instance(self, code, locale="zh-CN"):
        self.get_instance_calls.append(code)
        return {"data": self.instances[code]}


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------
def folder_request(**kwargs):
    base = dict(user="10086", resource_type="folder", resource_id="p-001",
                actions=["use"], days=90)
    base.update(kwargs)
    return PermissionRequest(**base)


def future_now(seconds=61):
    return (datetime.now().astimezone()
            + timedelta(seconds=seconds)).isoformat(timespec="seconds")


class ServiceCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "test.db"))
        self.finebi = FakeFineBI()
        self.platform = FakePlatform()
        self.lock = FakeLock()
        self.notifier = FakeNotifier()
        self.make_service()

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def make_service(self, dry_run=False, adopt_existing=False, platform="default",
                     row_clear_strategy="manual", type_map=None):
        jobs = JobService(self.storage, notifier=self.notifier)
        kwargs = dict(platform=self.platform if platform == "default" else platform,
                      max_days=365, dry_run=dry_run, lock=self.lock,
                      notifier=self.notifier, adopt_existing=adopt_existing, jobs=jobs,
                      type_map=type_map)
        self.service = PermissionService(self.finebi, self.storage, **kwargs)
        self.revoke = RevokeService(self.finebi, self.storage,
                                    platform=kwargs["platform"], dry_run=dry_run,
                                    lock=self.lock, notifier=self.notifier,
                                    row_clear_strategy=row_clear_strategy, jobs=jobs,
                                    type_map=type_map)
        return self.service

    def job_rows(self):
        return [dict(row) for row in
                self.storage.conn.execute("SELECT * FROM jobs ORDER BY created_at")]

    def ledger_rows(self):
        return [dict(row) for row in
                self.storage.conn.execute("SELECT * FROM ledger ORDER BY created_at")]

    def log_actions(self):
        return [row["action"] for row in self.storage.recent_logs(50)]


# ---------------------------------------------------------------------------
# 授权
# ---------------------------------------------------------------------------
class GrantV2Test(ServiceCase):
    def test_long_term_grant_allows_over_max_days(self):
        req = PermissionRequest(user="10086", resource_type="folder",
                                resource_id="p-001", actions=["use"],
                                days=3650, extra={"long_term": True})
        result = self.service.grant(req)
        self.assertEqual(result.status, "granted")
        self.assertTrue(self.storage.active_ledger(user="10086"))
        with self.assertRaises(ValueError):
            self.service.grant(PermissionRequest(
                user="10086", resource_type="folder", resource_id="p-002",
                actions=["use"], days=3650))

    def test_folder_grant_writes_full_authority(self):
        result = self.service.grant(folder_request(actions=["use", "manage"]))
        self.assertEqual(result.status, "granted")
        self.assertEqual(len(result.ledger_ids), 1)
        set_calls = [c for c in self.finebi.calls if c[0] == "set_folder"]
        self.assertEqual(len(set_calls), 1)
        authority = set_calls[0][3]
        self.assertEqual(set(authority), FULL_AUTHORITY)
        self.assertTrue(authority["usePrivilege"])
        self.assertTrue(authority["managePrivilege"])
        ledger = self.storage.active_ledger(user="10086")[0]
        self.assertEqual(ledger["payload"]["authority"],
                         {"usePrivilege": True, "managePrivilege": True,
                          "biData": True, "biView": True})
        items = self.storage.list_request_items(result.request_id)
        self.assertEqual([i["status"] for i in items], ["done"])
        self.assertEqual(self.storage.get_request(result.request_id)["status"], "done")
        self.assertIn("fb_user:10086:folder:p-001", self.lock.held)

    def test_folder_grant_idempotent_by_ledger(self):
        first = self.service.grant(folder_request())
        self.assertEqual(first.status, "granted")
        second = self.service.grant(folder_request())
        self.assertEqual(second.status, "skipped")
        self.assertEqual(self.finebi.count("set_folder"), 1)
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_second_grant_extends_ledger_expiry(self):
        self.service.grant(folder_request(days=10))
        first_expire = self.storage.active_ledger(user="10086")[0]["expire_at"]
        result = self.service.grant(folder_request(days=30))
        self.assertEqual(result.status, "skipped")
        updated = self.storage.active_ledger(user="10086")[0]
        self.assertGreater(updated["expire_at"], first_expire)
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_adopt_existing_false_skips_and_notifies(self):
        self.finebi.folder[("10086", "p-001")] = merge_authority(
            {"usePrivilege": True, "biData": True, "biView": True})
        result = self.service.grant(folder_request())
        self.assertEqual(result.status, "skipped")
        self.assertEqual(self.finebi.count("set_folder"), 0)
        self.assertEqual(self.storage.active_ledger(user="10086"), [])
        item = result.item_results[0]
        self.assertEqual(item["status"], "skipped")
        self.assertEqual(item["error_code"], "SKIP_ADOPT")
        self.assertTrue(item["reconcile"])
        self.assertTrue(self.notifier.admin_calls)
        self.assertIn("grant_adopt_skip", self.log_actions())
        items = self.storage.list_request_items(result.request_id)
        self.assertEqual(items[0]["status"], "skipped")
        self.assertEqual(items[0]["error_code"], "SKIP_ADOPT")

    def test_adopt_existing_true_creates_baseline_ledger(self):
        self.make_service(adopt_existing=True)
        self.finebi.folder[("10086", "p-001")] = merge_authority(
            {"usePrivilege": True, "biData": True, "biView": True})
        result = self.service.grant(folder_request())
        self.assertEqual(result.status, "skipped")
        self.assertEqual(self.finebi.count("set_folder"), 0)
        ledger = self.storage.active_ledger(user="10086")[0]
        self.assertEqual(ledger["payload"]["origin"], "baseline")
        self.assertEqual(ledger["payload"]["authority"],
                         {"usePrivilege": True, "biData": True, "biView": True})
        self.assertEqual(result.item_results[0]["status"], "skipped")
        self.assertTrue(result.item_results[0]["adopt_existing"])

    def test_row_grant_merges_and_creates_new_ledger(self):
        rule_a = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        rule_b = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华南"]}
        first = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": [rule_a]}, days=90))
        self.assertEqual(first.status, "granted")
        second = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": [rule_b]}, days=30))
        self.assertEqual(second.status, "granted")
        self.assertEqual(len([l for l in self.storage.active_ledger(user="10086")
                              if l["resource_type"] == "row"]), 2)
        written = self.finebi.row[("10086", "t-001")]
        self.assertEqual(len(written["filterValue"]), 2)
        ledgers = [l for l in self.storage.active_ledger(user="10086")
                   if l["resource_type"] == "row"]
        self.assertEqual(ledgers[0]["payload"]["rules"], [rule_a])
        self.assertEqual(ledgers[1]["payload"]["rules"], [rule_b])

    def test_row_grant_with_numeric_existing_without_type_map_goes_manual(self):
        """POC-3 映射未配置时，带存量数字结构的行权限不猜测、转人工（D4）。"""
        self.finebi.row[("10086", "t-001")] = numeric_row_filter("华东")
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], days=90,
            data_scope={"rules": [{"type": "strIn", "fieldId": "t_region",
                                   "filterValue": ["华南"]}]}))
        self.assertEqual(result.status, "failed")
        self.assertIn("POC-3", result.item_results[0]["error"])
        self.assertEqual(self.finebi.count("set_row"), 0)
        self.assertEqual(self.job_rows()[0]["status"], "manual")

    def test_row_grant_with_numeric_existing_and_type_map_merges(self):
        self.make_service(type_map=NUMERIC_TYPE_MAP)
        self.finebi.row[("10086", "t-001")] = numeric_row_filter("华东")
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], days=90,
            data_scope={"rules": [{"type": "strIn", "fieldId": "t_region",
                                   "filterValue": ["华南"]}]}))
        self.assertEqual(result.status, "granted")
        written = self.finebi.row[("10086", "t-001")]
        self.assertEqual(written["type"], "or")
        self.assertEqual(sorted(r["filterValue"] for r in written["filterValue"]),
                         [["华东"], ["华南"]])

    def test_row_multi_field_request_goes_manual(self):
        """D-01：单申请单多字段 scope 是 AND 组，POC-3 前不得静默 OR 扩权。"""
        rules = [
            {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]},
            {"type": "strIn", "fieldId": "t_channel", "filterValue": ["天猫"]},
        ]
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": rules}, days=90))
        self.assertEqual(result.status, "failed")
        item = result.item_results[0]
        self.assertIn("多个字段", item["error"])
        self.assertIn("POC-3", item["error"])
        self.assertEqual(self.finebi.count("set_row"), 0)
        self.assertEqual(self.storage.active_ledger(user="10086"), [])
        jobs = self.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.notifier.admin_calls)
        self.assertEqual(self.storage.list_request_items(result.request_id)[0]["status"],
                         "failed")

    def test_merge_rule_groups_preserves_existing_and_group(self):
        """D-01 回归：已有 AND 组不能被拍平成单条件 OR；写回前必须转人工。"""
        from executor.services.grant import merge_rule_groups

        existing = [[
            {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]},
            {"type": "strIn", "fieldId": "t_channel", "filterValue": ["天猫"]},
        ]]
        with self.assertRaises(BusinessError):
            merge_rule_groups(existing, [])

    def test_merge_full_authority_rejects_missing_current(self):
        """读不到五字段现状时不能按全 False 覆盖。"""
        from executor.services.grant import merge_full_authority

        with self.assertRaises(BusinessError):
            merge_full_authority(None, {"usePrivilege": True})
        merged = merge_full_authority(
            {"usePrivilege": True, "managePrivilege": True},
            {"usePrivilege": True})
        self.assertTrue(merged["managePrivilege"])

    def test_row_duplicate_rule_skipped(self):
        rule = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        request = dict(user="10086", resource_type="row", resource_id="t-001",
                       actions=["use"], data_scope={"rules": [rule]}, days=90)
        self.service.grant(PermissionRequest(**request))
        result = self.service.grant(PermissionRequest(**request))
        self.assertEqual(result.status, "skipped")
        self.assertEqual(self.finebi.count("set_row"), 1)

    def test_non_verifiable_ledger_idempotent(self):
        request = dict(user="10086", resource_type="publink",
                       resource_id="publink", days=90)
        first = self.service.grant(PermissionRequest(**request))
        self.assertEqual(first.status, "granted")
        self.assertEqual(self.finebi.count("set_publink"), 1)
        second = self.service.grant(PermissionRequest(**request))
        self.assertEqual(second.status, "skipped")
        self.assertEqual(self.finebi.count("set_publink"), 1)
        ledger = self.storage.active_ledger(user="10086")[0]
        self.assertFalse(ledger["payload"].get("origin") == "baseline")

    def test_dashboard_export_implies_view(self):
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_export", resource_id="d-1",
            actions=["export"], days=90))
        self.assertEqual(result.status, "granted")
        self.assertEqual(self.finebi.dash[("10086", "d-1")],
                         {"view": True, "export": True})
        ledger = self.storage.active_ledger(user="10086")[0]
        self.assertEqual(ledger["payload"]["authority"],
                         {"view": True, "export": True})

    def test_dashboard_view_without_actions_skipped(self):
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_view", resource_id="d-1",
            actions=[], days=90))
        self.assertEqual(result.status, "skipped")
        self.assertEqual(self.finebi.count("set_dash"), 0)
        self.assertIn("未指定权限项", result.item_results[0]["reason"])

    def test_dashboard_template_auth_not_applicable_is_skipped(self):
        """仪表板未纳入模板认证：读模板权限报 Unrecognized entityId，应跳过而非失败。"""
        self.finebi.fail_methods["get_dashboard_template_auth"] = ApiError(
            "BATCH", "java.lang.IllegalArgumentException: Unrecognized entityId [d-1]")
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_view", resource_id="d-1",
            actions=["view"], days=90))
        self.assertEqual(result.status, "skipped")
        self.assertIn("模板认证", result.item_results[0]["reason"])
        self.assertEqual(self.finebi.count("set_dash"), 0)
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_dashboard_template_auth_write_not_applicable_is_skipped(self):
        self.finebi.fail_methods["set_dashboard_template_auth"] = ApiError(
            "BATCH", "java.lang.IllegalArgumentException: Unrecognized entityId [d-1]")
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_view", resource_id="d-1",
            actions=["view"], days=90))
        self.assertEqual(result.status, "skipped")
        self.assertIn("模板认证", result.item_results[0]["reason"])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_template_auth_not_enabled_read_is_skipped(self):
        # FineBI 全局未开启模板认证/角色权限认证：跳过模板授权，不判失败
        self.finebi.fail_methods["get_dashboard_template_auth"] = ApiError(
            "BATCH", "java.lang.IllegalArgumentException: "
                     "Role permission authentication is not enabled!")
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_view", resource_id="d-1",
            actions=["view"], days=90))
        self.assertEqual(result.status, "skipped")
        self.assertIn("模板认证", result.item_results[0]["reason"])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_template_auth_not_enabled_write_is_skipped(self):
        self.finebi.fail_methods["set_dashboard_template_auth"] = ApiError(
            "BATCH", "java.lang.IllegalArgumentException: "
                     "Role permission authentication is not enabled!")
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_view", resource_id="d-1",
            actions=["view"], days=90))
        self.assertEqual(result.status, "skipped")
        self.assertIn("模板认证", result.item_results[0]["reason"])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_dashboard_data_uses_entry(self):
        request = PermissionRequest(
            user="10086", resource_type="dashboard_data", resource_id="entry-1",
            actions=[], days=90, extra={"entry": "entry-1"})
        self.service.grant(request)
        self.assertTrue(self.finebi.dashboard_data[("10086", "entry-1")])

    def test_role_grant_creates_separate_ledger_and_skips_when_existing(self):
        request = dict(user="10086", resource_type="folder", resource_id="p-001",
                       actions=["use"], role="电商-渠道运营", days=90)
        first = self.service.grant(PermissionRequest(**request))
        self.assertEqual(first.status, "granted")
        self.assertEqual(len(first.item_results), 2)
        self.assertEqual(len(first.ledger_ids), 2)
        set_role_calls = [c for c in self.platform.calls if c[0] == "set_roles"]
        self.assertEqual(len(set_role_calls), 1)
        self.assertIn("电商-渠道运营", self.platform.roles["10086"])
        role_ledgers = [l for l in self.storage.active_ledger(user="10086")
                        if l["resource_type"] == "role"]
        self.assertEqual(len(role_ledgers), 1)
        second = self.service.grant(PermissionRequest(**request))
        self.assertEqual(second.status, "skipped")
        self.assertEqual(len([c for c in self.platform.calls if c[0] == "set_roles"]), 1)

    def test_role_without_platform_skipped(self):
        self.make_service(platform=None)
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="folder", resource_id="p-001",
            actions=["use"], role="运营", days=90))
        self.assertEqual(result.status, "granted")
        role_items = [i for i in result.item_results if i["resource_type"] == "role"]
        self.assertEqual(role_items[0]["status"], "skipped")
        self.assertIn("platform", role_items[0]["reason"])

    def test_multi_item_partial_failure_queues_retry(self):
        self.finebi.fail_methods["set_table_permission"] = [ApiError(500, "boom")]
        request = PermissionRequest(
            user="10086", resource_type="", resource_id="", days=90,
            items=[
                {"resource_type": "folder", "resource_id": "p-001",
                 "actions": ["use"]},
                {"resource_type": "table", "resource_id": "t-001",
                 "actions": ["use"]},
            ])
        result = self.service.grant(request)
        self.assertEqual(result.status, "partial")
        self.assertEqual(len(result.ledger_ids), 1)
        self.assertEqual(self.storage.get_request(result.request_id)["status"], "partial")
        statuses = {i["resource_type"]: i["status"] for i in result.item_results}
        self.assertEqual(statuses, {"folder": "granted", "table": "failed"})
        jobs = self.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["kind"], KIND_GRANT)
        self.assertEqual(jobs[0]["status"], "queued")
        self.assertEqual(jobs[0]["attempts"], 1)

    def test_non_retryable_failure_goes_manual(self):
        self.finebi.fail_methods["set_folder_permission"] = BusinessError("用户未映射")
        result = self.service.grant(folder_request())
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.item_results[0]["error_code"], "E1003")
        jobs = self.job_rows()
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.notifier.admin_calls)

    def test_verify_failure_rewrites_once_then_fails(self):
        self.finebi.ignore_writes = True
        result = self.service.grant(folder_request())
        self.assertEqual(result.status, "failed")
        self.assertEqual(self.finebi.count("set_folder"), 2)
        self.assertIn("E3004", result.item_results[0]["error"])
        jobs = self.job_rows()
        self.assertEqual(jobs[0]["status"], "manual")

    def test_dry_run_does_not_write_or_create_ledger(self):
        self.make_service(dry_run=True)
        result = self.service.grant(folder_request())
        self.assertEqual(result.status, "skipped")
        self.assertTrue(result.details["dry_run"])
        self.assertEqual(self.finebi.count("set_folder"), 0)
        self.assertEqual(self.storage.active_ledger(user="10086"), [])
        self.assertEqual(self.lock.held, [])
        items = self.storage.list_request_items(result.request_id)
        self.assertEqual(items[0]["status"], "skipped")

    def test_dry_run_does_not_extend_existing_ledger(self):
        """dry-run 演练不得顺延真实台账的到期时间。"""
        self.service.grant(folder_request(days=10))
        before = self.storage.active_ledger(user="10086")[0]["expire_at"]
        self.make_service(dry_run=True)
        result = self.service.grant(folder_request(days=90))
        self.assertEqual(result.status, "skipped")
        self.assertIn("dry-run", result.item_results[0]["reason"])
        after = self.storage.active_ledger(user="10086")[0]["expire_at"]
        self.assertEqual(before, after)
        self.assertEqual(self.finebi.count("set_folder"), 1)

    def test_dry_run_does_not_write_baseline_ledger(self):
        """ADOPT_EXISTING 的基线纳管在 dry-run 下只报告、不落台账。"""
        self.make_service(dry_run=True, adopt_existing=True)
        self.finebi.folder[("10086", "p-001")] = merge_authority(
            {"usePrivilege": True, "biData": True, "biView": True})
        result = self.service.grant(folder_request())
        self.assertEqual(result.status, "skipped")
        item = result.item_results[0]
        self.assertTrue(item.get("would_adopt"))
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_role_satisfied_requires_exact_user(self):
        """user/detail 是模糊匹配：其他用户带该角色不能算本用户已满足。"""
        self.platform.extra_detail_items["10086"] = [
            {"username": "100861", "roles": [{"id": "r-x", "name": "电商-渠道运营"}]}]
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="folder", resource_id="p-001",
            actions=["use"], role="电商-渠道运营", days=90))
        self.assertEqual(result.status, "granted")
        role_items = [i for i in result.item_results if i["resource_type"] == "role"]
        self.assertEqual(role_items[0]["status"], "granted")
        self.assertIn("电商-渠道运营", self.platform.roles["10086"])

    def test_partial_filter_type_map_fills_documented_defaults(self):
        """配置只写 35/10 时，文档定义的 12=strNotIn 仍应能解析（不再整单转人工）。"""
        from executor.services.grant import normalize_type_map

        normalized = normalize_type_map({"35": "or", "10": "strIn"})
        self.assertEqual(normalized[34], "and")
        self.assertEqual(normalized[12], "strNotIn")
        self.make_service(type_map={"35": "or", "10": "strIn"})
        self.finebi.row[("10086", "t-001")] = {"filterType": 35, "filterValue": [
            {"filterType": 10, "fieldId": "t_region",
             "filterValue": {"type": 1, "value": ["华东"]}},
            {"filterType": 12, "fieldId": "t_region",
             "filterValue": {"type": 1, "value": ["华南"]}},
        ]}
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], days=90,
            data_scope={"rules": [{"type": "strIn", "fieldId": "t_region",
                                   "filterValue": ["华北"]}]}))
        self.assertEqual(result.status, "granted")
        written = self.finebi.row[("10086", "t-001")]
        self.assertEqual(len(written["filterValue"]), 3)
        self.assertIn("strNotIn",
                      [rule["type"] for rule in written["filterValue"]])

    def test_dashboard_entry_grant_preserves_existing_edit_privilege(self):
        """目录权限是四字段全量覆盖：本次没申请的 edit/empower 要保留现状。"""
        self.finebi.entry[("10086", "e-1")] = {
            "viewPrivilege": False, "export": False,
            "editPrivilege": True, "empowerPrivilege": True}
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view"], days=90))
        self.assertEqual(result.status, "granted")
        self.assertEqual(self.finebi.entry[("10086", "e-1")], {
            "viewPrivilege": True, "export": False,
            "editPrivilege": True, "empowerPrivilege": True})

    def test_existing_ledger_but_permission_missing_rewrites(self):
        """台账还在但 FineBI 权限被清空时，必须重写而不是只延期台账。"""
        self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view"], days=90))
        self.finebi.entry[("10086", "e-1")] = {}  # 模拟被 FineBI 侧清掉
        again = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view"], days=90))
        self.assertEqual(again.status, "granted")
        self.assertTrue(self.finebi.entry[("10086", "e-1")]["viewPrivilege"])

    def test_component_data_item_writes_without_ledger(self):
        """随仪表板连带授予的组件数据：写 biData，但不记台账（回收不处理）。"""
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="table", resource_id="t-c1",
            actions=["component"], days=90,
            items=[{"resource_type": "table", "resource_id": "t-c1",
                    "actions": ["component"], "record_ledger": False}]))
        self.assertEqual(result.status, "granted")
        self.assertTrue(self.finebi.table[("10086", "t-c1")]["biData"])
        self.assertEqual(self.ledger_rows(), [])

    def test_permission_status_reports_existing_permissions(self):
        from executor.web.service import WebApprovalService
        self.storage.conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,"
            "created_at) VALUES(?,?,?,?,?,?,?,?)",
            ("fs_u1", "测试用户", "", "ou_x", "10086", '["applicant"]', 1,
             "2026-01-01T00:00:00+08:00"))
        self.storage.conn.commit()
        web = WebApprovalService(self.storage, self.service, policy={})
        self.finebi.entry[("10086", "e-1")] = {
            "viewPrivilege": True, "export": False,
            "editPrivilege": False, "empowerPrivilege": False}
        self.finebi.dash[("10086", "dash-1")] = {"view": True, "export": False}
        status = web.permission_status(
            "fs_u1", "dashboard_view", "dash-1", entry_id="e-1",
            actions=["view", "export"])
        self.assertTrue(status["known"])
        self.assertEqual(status["own"], {"view": True})
        entry_status = web.permission_status(
            "fs_u1", "dashboard_entry", "e-1", actions=["view", "export"])
        self.assertTrue(entry_status["known"])
        self.assertEqual(entry_status["own"], {"view": True})

    def test_permission_status_table_lists_all_existing_fields(self):
        """只勾“使用”也要列出全部已有：使用/管理/组件数据/元数据。"""
        from executor.web.service import WebApprovalService
        self.storage.conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,"
            "created_at) VALUES(?,?,?,?,?,?,?,?)",
            ("fs_u2", "测试用户", "", "ou_y", "10086", '["applicant"]', 1,
             "2026-01-01T00:00:00+08:00"))
        self.storage.conn.commit()
        self.finebi.table[("10086", "t-1")] = {
            "usePrivilege": True, "managePrivilege": True,
            "empowerPrivilege": False, "biData": True, "biView": True}
        web = WebApprovalService(self.storage, self.service, policy={})
        web.deps_json = os.path.join(self.tmp.name, "no_deps.json")
        status = web.permission_status("fs_u2", "table", "t-1",
                                       actions=["use"])
        self.assertTrue(status["known"])
        self.assertEqual(status["own"], {"use": True, "manage": True,
                                         "component": True, "metadata": True})

    def test_permission_status_dashboard_edit_only_lists_all_four(self):
        """仪表板只勾“编辑”时，也把 查看/导出/编辑/权限设置 全部列出。"""
        from executor.web.service import WebApprovalService
        self.storage.conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,"
            "created_at) VALUES(?,?,?,?,?,?,?,?)",
            ("fs_u3", "测试用户", "", "ou_z", "10086", '["applicant"]', 1,
             "2026-01-01T00:00:00+08:00"))
        self.storage.conn.commit()
        self.finebi.entry[("10086", "e-2")] = {
            "viewPrivilege": True, "export": True,
            "editPrivilege": True, "empowerPrivilege": True}
        web = WebApprovalService(self.storage, self.service, policy={})
        web.deps_json = os.path.join(self.tmp.name, "no_deps.json")
        status = web.permission_status("fs_u3", "dashboard", "dash-2",
                                       entry_id="e-2", actions=["edit"])
        self.assertTrue(status["known"])
        self.assertEqual(status["own"], {"view": True, "export": True,
                                         "edit": True, "empower": True})

    def test_dashboard_entry_grant_fills_missing_ancestor_view(self):
        self.platform.entry_tree_nodes = [
            {"id": "e-1", "pId": "folder-1"},
            {"id": "folder-1", "pId": "decision-directory-root"},
        ]
        self.finebi.entry[("10086", "folder-1")] = {
            "viewPrivilege": False, "export": False,
            "editPrivilege": False, "empowerPrivilege": True}
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view"], days=90))
        self.assertEqual(result.status, "granted")
        self.assertTrue(self.finebi.entry[("10086", "folder-1")]["viewPrivilege"])
        self.assertTrue(self.finebi.entry[("10086", "folder-1")]["empowerPrivilege"])
        self.assertTrue(self.finebi.entry[("10086", "e-1")]["viewPrivilege"])

    def test_dashboard_entry_export_degrades_when_incomplete_authorize(self):
        self.platform.entry_tree_nodes = [
            {"id": "e-1", "pId": "decision-directory-root"}]
        self.finebi.fail_methods["set_entry_authority"] = [ApiError(
            "BATCH",
            "java.lang.IllegalArgumentException: forbid incomplete authorize exception")]
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view", "export"], days=90))
        self.assertEqual(result.status, "granted")
        self.assertTrue(result.item_results[0].get("export_skipped"))
        authority = self.finebi.entry[("10086", "e-1")]
        self.assertTrue(authority["viewPrivilege"])
        self.assertFalse(authority["export"])
        ledgers = self.storage.active_ledger(user="10086")
        self.assertEqual(len(ledgers), 1)
        self.assertFalse(ledgers[0]["payload"]["authority"].get("export"))

    def test_dashboard_entry_grant_edit_privilege(self):
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view", "edit"], days=90))
        self.assertEqual(result.status, "granted")
        authority = self.finebi.entry[("10086", "e-1")]
        self.assertTrue(authority["viewPrivilege"])
        self.assertTrue(authority["editPrivilege"])
        self.assertFalse(authority["export"])

    def test_dashboard_entry_revoke_clears_edit_privilege(self):
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_entry", resource_id="e-1",
            actions=["view", "edit"], days=90))
        ledger = self.storage.active_ledger(user="10086")[0]
        self.revoke.revoke_ledger(ledger, "测试回收")
        authority = self.finebi.entry[("10086", "e-1")]
        self.assertFalse(authority["editPrivilege"])
        self.assertFalse(authority["viewPrivilege"])

    def test_form_parser_to_grant_end_to_end(self):
        """审批表单 → FormParser → grant → 台账；重复轮询同实例幂等。"""
        from executor.feishu.form_parser import FormParser

        mapping = {
            "field_user": "FineBI账号",
            "field_resource": "数据资源",
            "field_actions": "权限项",
            "field_days": "使用期限",
            "resource_type_map": {"数据集使用": "table"},
            "action_map": {"使用": "use"},
            "resources": {"销售数据集": {"resource_type": "table",
                                          "resource_id": "t-001"}},
        }
        form = [
            {"id": "w1", "name": "FineBI账号", "type": "input", "value": "10086"},
            {"id": "w2", "name": "数据资源", "type": "mutableGroup",
             "value": [{"资源名称": "销售数据集", "资源ID": "t-001",
                        "资源类型": "数据集使用"}]},
            {"id": "w3", "name": "权限项", "type": "checkbox", "value": ["使用"]},
            {"id": "w4", "name": "使用期限", "type": "radio", "value": "30天"},
        ]
        instance = {"instance_code": "INST-E2E", "status": "APPROVED",
                    "form": json.dumps(form, ensure_ascii=False)}
        parser = FormParser(mapping)
        request = parser.parse_instance(instance)
        result = self.service.grant(request)
        self.assertEqual(result.status, "granted")
        stored = self.storage.get_request(result.request_id)
        self.assertEqual(stored["instance_code"], "INST-E2E")
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

        again = self.service.grant(parser.parse_instance(instance))
        self.assertEqual(again.status, "skipped")
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_default_replay_retries_before_manual(self):
        """D-05：服务默认注册的回放处理函数不得把可重试失败包成 BusinessError。

        首次失败入队 attempts=1；第 1 次重试仍 500 → 应继续退避（attempts=2），
        第 2 次重试成功 → done；而不是第 1 次重试就 manual。
        """
        self.finebi.fail_methods["set_table_permission"] = [
            ApiError(500, "boom"), ApiError(500, "boom")]
        request = PermissionRequest(user="10086", resource_type="table",
                                    resource_id="t-001", actions=["use"], days=90)
        first = self.service.grant(request)
        self.assertEqual(first.status, "failed")
        self.assertEqual(self.job_rows()[0]["attempts"], 1)

        # 第 1 次重试仍失败：可重试 → 继续排队，不能转 manual
        self.service.jobs.run_due(now=future_now(61))
        job = self.job_rows()[0]
        self.assertEqual(job["status"], "queued")
        self.assertEqual(job["attempts"], 2)
        self.assertNotEqual(job["status"], "manual")

        # 第 2 次重试成功
        self.service.jobs.run_due(now=future_now(1000))
        job = self.job_rows()[0]
        self.assertEqual(job["status"], "done")
        self.assertEqual(self.storage.get_request(first.request_id)["status"], "done")
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_non_retryable_failure_manual_job_not_duplicated(self):
        """D-03 配套：同一申请重复触发非重试失败时，人工待办不重复插入。"""
        self.finebi.fail_methods["set_folder_permission"] = BusinessError("用户未映射")
        request = folder_request()
        first = self.service.grant(request)
        self.assertEqual(first.status, "failed")
        self.assertEqual(len(self.job_rows()), 1)
        replay = PermissionRequest.from_dict(request.to_dict())
        self.assertEqual(replay.request_id, first.request_id)
        second = self.service.grant(replay)
        self.assertEqual(second.status, "failed")
        self.assertEqual(len(self.job_rows()), 1)

    def test_validation_errors_raise(self):
        with self.assertRaises(ValueError):
            self.service.grant(folder_request(days=999))
        with self.assertRaises(ValueError):
            self.service.grant(folder_request(user=""))
        with self.assertRaises(ValueError):
            self.service.grant(folder_request(resource_type="unknown"))
        with self.assertRaises(ValueError):
            self.service.grant(PermissionRequest(
                user="10086", resource_type="row", resource_id="t-001",
                actions=["use"], days=90))

    def test_retry_job_replays_and_succeeds(self):
        self.finebi.fail_methods["set_table_permission"] = [ApiError(500, "boom")]
        request = PermissionRequest(user="10086", resource_type="table",
                                    resource_id="t-001", actions=["use"], days=90)
        result = self.service.grant(request)
        self.assertEqual(result.status, "failed")
        job = self.job_rows()[0]
        self.assertEqual(job["status"], "queued")
        self.assertEqual(job["attempts"], 1)

        summary = self.service.jobs.run_due(now=future_now(61))
        self.assertEqual(summary["done"], 1)
        jobs = self.job_rows()
        self.assertEqual(jobs[0]["status"], "done")
        self.assertEqual(self.storage.get_request(result.request_id)["status"], "done")
        self.assertTrue(self.finebi.table[("10086", "t-001")]["usePrivilege"])
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_runtime_style_job_handler_replays_without_duplicate_jobs(self):
        """与 runtime._grant_job 相同的接线：处理函数直接调公开 grant。"""
        self.finebi.fail_methods["set_table_permission"] = [
            ApiError(500, "boom"), ApiError(500, "boom")]
        request = PermissionRequest(user="10086", resource_type="table",
                                    resource_id="t-001", actions=["use"], days=90)
        first = self.service.grant(request)
        self.assertEqual(first.status, "failed")
        self.assertEqual(len(self.job_rows()), 1)

        def runtime_style_handler(request_id):
            row = self.storage.get_request(request_id)
            return self.service.grant(PermissionRequest.from_dict(row["payload"]))

        self.service.jobs.register_handler(KIND_GRANT, runtime_style_handler)

        # 第 1 次重试仍失败：任务原地退避，不产生重复任务
        self.service.jobs.run_due(now=future_now(61))
        jobs = self.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["attempts"], 2)
        self.assertEqual(jobs[0]["status"], "queued")

        # 第 2 次重试成功
        self.service.jobs.run_due(now=future_now(600))
        jobs = self.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["status"], "done")
        self.assertEqual(self.storage.get_request(first.request_id)["status"], "done")
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_grant_replay_same_request_id_has_no_duplicate_items(self):
        self.finebi.fail_methods["set_table_permission"] = [ApiError(500, "boom")]
        request = PermissionRequest(user="10086", resource_type="table",
                                    resource_id="t-001", actions=["use"], days=90)
        first = self.service.grant(request)
        self.assertEqual(first.status, "failed")
        second = self.service.grant(PermissionRequest.from_dict(request.to_dict()))
        self.assertEqual(second.request_id, first.request_id)
        self.assertEqual(second.status, "granted")
        item_ids = [i["id"] for i in self.storage.list_request_items(first.request_id)]
        self.assertEqual(len(item_ids), 1)


# ---------------------------------------------------------------------------
# 回收
# ---------------------------------------------------------------------------
class RevokeV2Test(ServiceCase):
    def _add_ledger(self, rt, rid, payload, user="10086", days=30):
        return self.storage.add_ledger(
            request_id="req-manual", user=user, resource_type=rt,
            resource_id=rid, payload=payload, expire_at=expire_at_from_days(days))

    def test_revoke_folder_keeps_unrelated_fields(self):
        self.finebi.folder[("10086", "p-001")] = merge_authority(
            {"usePrivilege": True, "biData": True, "biView": True,
             "empowerPrivilege": True})
        result = self.service.grant(folder_request(actions=["use", "manage"]))
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertEqual(detail["revoked_fields"],
                         ["biData", "biView", "managePrivilege", "usePrivilege"])
        state = self.finebi.folder[("10086", "p-001")]
        self.assertFalse(state["usePrivilege"])
        self.assertFalse(state["managePrivilege"])
        self.assertTrue(state["empowerPrivilege"])  # 未在台账里的已有权限不被误伤
        self.assertEqual(self.storage.due_ledger(), [])
        self.assertEqual(result.status, "granted")

    def test_revoke_row_recomputes_remaining_rules(self):
        rule_a = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        rule_b = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华南"]}
        self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": [rule_a]}, days=90))
        self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": [rule_b]}, days=90))
        ledgers = [l for l in self.storage.active_ledger(user="10086")
                   if l["resource_type"] == "row"]
        detail = self.revoke.revoke_ledger(ledgers[0], reason="到期回收")
        self.assertEqual(len(detail["remaining_rules"]["filterValue"]), 1)
        self.assertEqual(detail["remaining_rules"]["filterValue"][0]["filterValue"], ["华南"])
        self.assertEqual(len(self.finebi.row[("10086", "t-001")]["filterValue"]), 1)
        active = self.storage.active_ledger(user="10086")
        self.assertEqual([l["id"] for l in active], [ledgers[1]["id"]])

    def test_revoke_row_with_numeric_current_without_type_map_goes_manual(self):
        rule = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        self._add_ledger("row", "t-001", {"rules": [rule]})
        self.finebi.row[("10086", "t-001")] = numeric_row_filter("华东", "华南")
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail["manual"])
        self.assertIn("POC-3", detail["warning"])
        self.assertEqual(self.finebi.count("set_row"), 0)
        failed = [l for l in self.ledger_rows() if l["status"] == "failed"]
        self.assertEqual(len(failed), 1)

    def test_revoke_row_with_numeric_current_and_type_map_recomputes(self):
        self.make_service(type_map=NUMERIC_TYPE_MAP)
        rule = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        self._add_ledger("row", "t-001", {"rules": [rule]})
        self.finebi.row[("10086", "t-001")] = numeric_row_filter("华东", "华南")
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertFalse(detail.get("manual"))
        written = self.finebi.row[("10086", "t-001")]
        self.assertEqual([r["filterValue"] for r in written["filterValue"]], [["华南"]])
        self.assertTrue(detail["verified"])  # 配置映射后可写后反查

    def test_revoke_row_verify_failure_rewrites_once_then_manual(self):
        """写后反查不一致：重写一次仍不一致 → E3004 转人工（可验证类型统一策略）。"""
        self.make_service(type_map=NUMERIC_TYPE_MAP)
        rule = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        self._add_ledger("row", "t-001", {"rules": [rule]})
        self.finebi.row[("10086", "t-001")] = numeric_row_filter("华东", "华南")
        self.finebi.ignore_writes = True
        ledger = self.storage.active_ledger(user="10086")[0]
        with self.assertRaises(BusinessError):
            self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertEqual(self.finebi.count("set_row"), 2)  # 首次 + 重写一次
        self.assertEqual(self.job_rows()[0]["status"], "manual")

    def test_revoke_row_with_and_group_current_goes_manual(self):
        """D-01 回收同步：现状含存量 AND 组（多字段交集）时不猜测写回。"""
        rule_a = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        rule_b = {"type": "strIn", "fieldId": "t_channel", "filterValue": ["天猫"]}
        self._add_ledger("row", "t-001", {"rules": [rule_a]})
        self.finebi.row[("10086", "t-001")] = {
            "type": "or",
            "filterValue": [{"type": "and", "filterValue": [rule_a, rule_b]}],
        }
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail["manual"])
        self.assertIn("AND", detail["warning"])
        self.assertIn("POC-3", detail["warning"])
        self.assertEqual(self.finebi.count("set_row"), 0)
        failed = [l for l in self.ledger_rows() if l["status"] == "failed"]
        self.assertEqual(len(failed), 1)
        jobs = self.job_rows()
        self.assertEqual(jobs[0]["kind"], KIND_ROW_CLEAR)
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.notifier.admin_calls)

    def test_revoke_last_row_rule_manual_strategy(self):
        rule = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": [rule]}, days=90))
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail["manual"])
        self.assertEqual(detail["ledger_status"], "failed")
        self.assertEqual(self.finebi.row[("10086", "t-001")]["filterValue"],
                         [rule])  # 不自动写空 filter
        failed = [l for l in self.ledger_rows() if l["status"] == "failed"]
        self.assertEqual(len(failed), 1)
        jobs = self.job_rows()
        self.assertEqual(jobs[0]["kind"], KIND_ROW_CLEAR)
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertTrue(self.notifier.admin_calls)
        ok_items = self.storage.list_request_items(result.request_id)
        self.assertEqual(ok_items[0]["status"], "done")

    def test_revoke_last_row_rule_empty_strategy(self):
        self.make_service(row_clear_strategy="empty")
        rule = {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}
        self.service.grant(PermissionRequest(
            user="10086", resource_type="row", resource_id="t-001",
            actions=["use"], data_scope={"rules": [rule]}, days=90))
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertFalse(detail.get("manual"))
        self.assertEqual(self.finebi.row[("10086", "t-001")]["filterValue"], [])
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 0)

    def test_revoke_role_only_when_no_other_reference(self):
        request = dict(user="10086", resource_type="folder", resource_id="p-001",
                       actions=["use"], role="电商-渠道运营", days=90)
        self.service.grant(PermissionRequest(**request))
        ledgers = self.storage.active_ledger(user="10086")
        folder_ledger = [l for l in ledgers if l["resource_type"] == "folder"][0]
        role_ledger = [l for l in ledgers if l["resource_type"] == "role"][0]
        # 回收文件夹台账不动角色台账，角色仍被角色台账引用
        self.revoke.revoke_ledger(folder_ledger, reason="到期回收")
        self.assertIn("电商-渠道运营", self.platform.roles["10086"])
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)
        self.revoke.revoke_ledger(role_ledger, reason="到期回收")
        self.assertNotIn("电商-渠道运营", self.platform.roles["10086"])

    def test_revoke_role_kept_when_sibling_ledger_references(self):
        role = "电商-渠道运营"
        self._add_ledger("role", role, {"role": role, "authority": {}})
        second_id = self._add_ledger("role", role, {"role": role, "authority": {}})
        first = [l for l in self.storage.active_ledger(user="10086")
                 if l["id"] != second_id][0]
        detail = self.revoke.revoke_ledger(first, reason="到期回收")
        self.assertTrue(detail.get("skipped"))
        self.assertEqual(len([c for c in self.platform.calls if c[0] == "set_roles"]), 0)
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_grant_department_membership_and_revoke(self):
        path = ["财务部", "财务一部"]
        rid = json.dumps(path, ensure_ascii=False)
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="department", resource_id=rid,
            actions=[], days=30))
        self.assertEqual(result.status, "granted")
        self.assertIn(path, self.platform.departments["10086"])
        ledgers = self.storage.active_ledger(user="10086")
        self.assertEqual([l["resource_type"] for l in ledgers], ["department"])
        detail = self.revoke.revoke_ledger(ledgers[0], reason="到期回收")
        self.assertEqual(detail.get("department_removed"), rid)
        self.assertNotIn(path, self.platform.departments["10086"])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_grant_department_preexisting_membership_skipped(self):
        path = ["财务部"]
        self.platform.departments["10086"] = [path]
        result = self.service.grant(PermissionRequest(
            user="10086", resource_type="department",
            resource_id=json.dumps(path, ensure_ascii=False),
            actions=[], days=30))
        self.assertEqual(result.status, "skipped")
        self.assertEqual([c for c in self.platform.calls
                          if c[0] == "set_departments"], [])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_revoke_department_preexisting_ledger_is_noop(self):
        path = ["财务部"]
        rid = json.dumps(path, ensure_ascii=False)
        self.platform.departments["10086"] = [path]
        self._add_ledger("department", rid,
                         {"department": rid, "preexisting": True, "authority": {}})
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail.get("skipped"))
        self.assertIn(path, self.platform.departments["10086"])
        self.assertEqual([c for c in self.platform.calls
                          if c[0] == "set_departments"], [])

    def test_revoke_role_preexisting_ledger_is_noop(self):
        role = "电商-渠道运营"
        self.platform.roles["10086"] = [role]
        self._add_ledger("role", role,
                         {"role": role, "preexisting": True, "authority": {}})
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail.get("skipped"))
        self.assertIn(role, self.platform.roles["10086"])
        self.assertEqual([c for c in self.platform.calls if c[0] == "set_roles"], [])

    def test_revoke_publink_skipped_when_sibling_ledger_active(self):
        self._add_ledger("publink", "publink", {"authority": {"biShareFun": True}})
        self._add_ledger("publink", "publink", {"authority": {"biShareFun": True}})
        ledgers = self.storage.active_ledger(user="10086")
        detail = self.revoke.revoke_ledger(ledgers[0], reason="到期回收")
        self.assertTrue(detail.get("skipped"))
        self.assertEqual(self.finebi.count("set_publink"), 0)
        self.revoke.revoke_ledger(ledgers[1], reason="到期回收")
        self.assertEqual(self.finebi.count("set_publink"), 1)

    def test_revoke_dashboard_keeps_sibling_export(self):
        self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_view", resource_id="d-1",
            actions=["view"], days=90))
        self.service.grant(PermissionRequest(
            user="10086", resource_type="dashboard_export", resource_id="d-1",
            actions=["export"], days=90))
        ledgers = self.storage.active_ledger(user="10086")
        view_ledger = [l for l in ledgers if l["resource_type"] == "dashboard_view"][0]
        detail = self.revoke.revoke_ledger(view_ledger, reason="到期回收")
        self.assertTrue(detail.get("skipped"))
        self.assertEqual(self.finebi.dash[("10086", "d-1")],
                         {"view": True, "export": True})
        export_ledger = [l for l in self.storage.active_ledger(user="10086")][0]
        detail = self.revoke.revoke_ledger(export_ledger, reason="到期回收")
        self.assertEqual(self.finebi.dash[("10086", "d-1")],
                         {"view": False, "export": False})

    def test_revoke_user_continues_after_failure(self):
        self._add_ledger("folder", "p-fail", {"authority": {"usePrivilege": True}})
        self._add_ledger("table", "t-ok", {"authority": {"usePrivilege": True}})
        self.finebi.folder[("10086", "p-fail")] = merge_authority({"usePrivilege": True})
        self.finebi.table[("10086", "t-ok")] = merge_authority({"usePrivilege": True})
        self.finebi.fail_methods["set_folder_permission"] = BusinessError("模拟失败")
        results = self.revoke.revoke_user("10086", reason="离职回收")
        self.assertEqual(len(results), 2)
        errors = [r for r in results if r.get("error")]
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

    def test_revoke_dry_run_keeps_ledger_active(self):
        self.service.grant(folder_request())
        ledger = self.storage.active_ledger(user="10086")[0]
        self.make_service(dry_run=True)
        detail = self.revoke.revoke_ledger(ledger, reason="演练")
        self.assertTrue(detail["dry_run"])
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)
        self.assertEqual(self.finebi.count("set_folder"), 1)  # 只有授权时写入
    def test_revoke_unknown_type_raises(self):
        ledger_id = self._add_ledger("weird", "x", {})
        ledger = self.storage.active_ledger(user="10086")[0]
        with self.assertRaises(BusinessError):
            self.revoke.revoke_ledger(ledger, reason="test")

    def test_revoke_dash_share_goes_manual(self):
        """D-02：dash_share 取消分享转人工时，台账置 failed + 人工待办 + 通知。"""
        ledger_id = self._add_ledger("dash_share", "d-1", {"authority": {"view": True}})
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail["manual"])
        self.assertEqual(detail["ledger_status"], "failed")
        self.assertIn("人工", detail["warning"])
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 0)
        rows = [l for l in self.ledger_rows() if l["id"] == ledger_id]
        self.assertEqual(rows[0]["status"], "failed")
        jobs = self.job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["kind"], KIND_SHARE_REVOKE)
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertEqual(jobs[0]["ref_id"], ledger_id)
        self.assertTrue(self.notifier.admin_calls)
        self.assertIn("分享", self.notifier.admin_calls[0][0])

    def test_revoke_already_revoked_skipped(self):
        ledger_id = self._add_ledger("folder", "p-001",
                                     {"authority": {"usePrivilege": True}})
        self.storage.mark_revoked(ledger_id, "test")
        ledger = [l for l in self.ledger_rows() if l["id"] == ledger_id][0]
        detail = self.revoke.revoke_ledger(ledger, reason="test")
        self.assertTrue(detail["skipped"])

    def test_revoke_folder_with_empower_permission(self):
        """回收带“授权”权限的文件夹台账：父子校验依赖 check_parent_empower（回归 NameError）。"""
        result = self.service.grant(folder_request(actions=["use", "empower"]))
        self.assertEqual(result.status, "granted")
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertEqual(detail["revoked_fields"],
                         ["biData", "biView", "empowerPrivilege", "usePrivilege"])
        state = self.finebi.folder[("10086", "p-001")]
        self.assertFalse(state["usePrivilege"])
        self.assertFalse(state["empowerPrivilege"])
        self.assertFalse(state["biData"])
        self.assertFalse(state["biView"])
        self.assertEqual(self.storage.due_ledger(), [])

    def test_revoke_folder_empower_checks_parent_chain(self):
        """父目录已开启“授权”时，关闭子目录授权应被父子校验拦下（E2002 转人工）。"""
        from executor.domain.validators import ParentChildError

        result = self.service.grant(folder_request(actions=["use", "empower"]))
        self.assertEqual(result.status, "granted")
        ledger = self.storage.active_ledger(user="10086")[0]
        self.revoke.resources = {"p-001": {"resource_id": "p-001", "parent": "p-parent"}}
        self.finebi.folder[("10086", "p-parent")] = merge_authority(
            {"usePrivilege": True, "empowerPrivilege": True})
        with self.assertRaises(ParentChildError):
            self.revoke.revoke_ledger(ledger, reason="到期回收")
        jobs = self.job_rows()
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertEqual(self.finebi.count("set_folder"), 1)  # 未发生回收写入

    def test_revoke_entry_skipped_when_sibling_ledger_keeps_view(self):
        self.finebi.entry[("10086", "e-1")] = {
            "viewPrivilege": True, "export": True,
            "editPrivilege": False, "empowerPrivilege": False}
        view_id = self._add_ledger("dashboard_entry", "e-1",
                                   {"authority": {"viewPrivilege": True,
                                                  "export": False}})
        self._add_ledger("dashboard_entry", "e-1",
                         {"authority": {"viewPrivilege": True, "export": True}})
        view_ledger = [l for l in self.storage.active_ledger(user="10086")
                       if l["id"] == view_id][0]
        detail = self.revoke.revoke_ledger(view_ledger, reason="到期回收")
        self.assertTrue(detail.get("skipped"))
        self.assertEqual(self.finebi.entry[("10086", "e-1")]["viewPrivilege"], True)
        # 回收最后一条台账：查看/导出关闭
        export_ledger = self.storage.active_ledger(user="10086")[0]
        self.revoke.revoke_ledger(export_ledger, reason="到期回收")
        state = self.finebi.entry[("10086", "e-1")]
        self.assertFalse(state["viewPrivilege"])
        self.assertFalse(state["export"])

    def test_revoke_entry_preserves_manual_edit_privilege(self):
        self.finebi.entry[("10086", "e-1")] = {
            "viewPrivilege": True, "export": False,
            "editPrivilege": True, "empowerPrivilege": True}
        self._add_ledger("dashboard_entry", "e-1",
                         {"authority": {"viewPrivilege": True, "export": False}})
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertFalse(detail.get("skipped"))
        self.assertEqual(self.finebi.entry[("10086", "e-1")], {
            "viewPrivilege": False, "export": False,
            "editPrivilege": True, "empowerPrivilege": True})

    def test_revoke_schedule_ledger_calls_platform(self):
        self._add_ledger("schedule", "task-1", {"permissions": ["manage"]})
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertFalse(detail.get("manual"))
        self.assertIn(("set_schedule", "10086", "task-1", False, False),
                      self.platform.calls)
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_revoke_platform_module_ledger_calls_platform(self):
        self._add_ledger("platform_module", "decision-management-schedule",
                         {"permissions": ["use"]})
        ledger = self.storage.active_ledger(user="10086")[0]
        self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertIn(("set_platform", "10086", "decision-management-schedule",
                       False, False), self.platform.calls)
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_revoke_platform_ledger_without_platform_goes_manual(self):
        self.make_service(platform=None)
        self._add_ledger("schedule", "task-1", {"permissions": ["manage"]})
        ledger = self.storage.active_ledger(user="10086")[0]
        detail = self.revoke.revoke_ledger(ledger, reason="到期回收")
        self.assertTrue(detail["manual"])
        self.assertEqual(detail["ledger_status"], "failed")
        self.assertEqual(self.job_rows()[0]["kind"], "revoke")
        self.assertEqual(self.job_rows()[0]["status"], "manual")
        self.assertEqual(self.storage.active_ledger(user="10086"), [])


POLL_MAPPING = {
    "field_user": "FineBI账号",
    "field_resource": "数据资源",
    "field_actions": "权限项",
    "field_days": "使用期限",
    "resource_type_map": {"文件夹使用": "folder"},
    "action_map": {"使用": "use"},
    "resources": {"销售文件夹": {"resource_type": "folder", "resource_id": "p-001"}},
}


def poll_form():
    return [
        {"id": "w1", "name": "FineBI账号", "type": "input", "value": "10086"},
        {"id": "w2", "name": "数据资源", "type": "mutableGroup",
         "value": [{"资源名称": "销售文件夹", "资源ID": "p-001",
                    "资源类型": "文件夹使用"}]},
        {"id": "w3", "name": "权限项", "type": "checkbox", "value": ["使用"]},
        {"id": "w4", "name": "使用期限", "type": "radio", "value": "90天"},
    ]


class PollerManualJobTest(unittest.TestCase):
    """D-03：已转人工的审批实例不再被轮询重复 grant / 重复插 manual job。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "poll.db"))
        self.finebi = FakeFineBI()
        self.platform = FakePlatform()
        self.feishu = FakeFeishu()
        self.notifier = FakeNotifier()
        self.lock = FakeLock()
        self.jobs = JobService(self.storage, notifier=self.notifier)
        self.permission = PermissionService(
            self.finebi, self.storage, platform=self.platform, max_days=365,
            dry_run=False, lock=self.lock, notifier=self.notifier,
            jobs=self.jobs)
        self.poller = ApprovalPoller(
            self.feishu, self.permission, self.storage, approval_code="APPROVAL-T",
            mapper=FormParser(POLL_MAPPING))
        self.feishu.add_instance("INST-MANUAL", {
            "instance_code": "INST-MANUAL", "status": "APPROVED",
            "serial_number": "SER-1", "approval_name": "测试",
            "form": json.dumps(poll_form(), ensure_ascii=False)})

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _job_rows(self):
        return [dict(row) for row in
                self.storage.conn.execute("SELECT * FROM jobs ORDER BY created_at")]

    def test_poller_skips_instance_with_manual_job(self):
        self.finebi.fail_methods["set_folder_permission"] = [
            BusinessError("用户 10086 未映射")]
        first = self.poller.run_once()
        self.assertEqual(first["failed"], 1)
        jobs = self._job_rows()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["status"], "manual")
        self.assertEqual(len(self.feishu.get_instance_calls), 1)
        self.assertEqual(self.finebi.count("set_folder"), 1)

        second = self.poller.run_once()
        self.assertEqual(second["skipped"], 1)
        self.assertEqual(second["failed"], 0)
        # 未再次拉详情、未再次 grant、未新增待办
        self.assertEqual(len(self.feishu.get_instance_calls), 1)
        self.assertEqual(self.finebi.count("set_folder"), 1)
        self.assertEqual(len(self._job_rows()), 1)

    def test_poller_still_processes_retryable_queued_job(self):
        """D-03 不破坏重试语义：queued/running 任务不算“已人工闭环”。"""
        self.finebi.fail_methods["set_folder_permission"] = [ApiError(500, "boom")]
        first = self.poller.run_once()
        self.assertEqual(first["failed"], 1)
        job = self._job_rows()[0]
        self.assertEqual(job["status"], "queued")
        self.assertFalse(self.jobs.has_manual_job(KIND_GRANT, job["ref_id"]))
        self.assertTrue(self.jobs.has_open_job(KIND_GRANT, job["ref_id"]))
        # 重试任务可正常被调度执行（清空故障后可恢复）
        self.finebi.fail_methods.pop("set_folder_permission", None)
        summary = self.jobs.run_due(now=job["next_run_at"])
        self.assertEqual(summary["done"], 1)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
def merge_authority(desired, current=None):
    base = {field: False for field in FULL_AUTHORITY}
    base.update(current or {})
    base.update(desired)
    return base


if __name__ == "__main__":
    unittest.main()

