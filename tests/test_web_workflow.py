# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from executor.errors import ApiError
from executor.finebi.platform import API_ROOT, FineBIPlatformClient
from executor.models import GrantResult
from executor.services.grant import PermissionService
from executor.services.offboard import OffboardService
from executor.storage import Storage
from executor.web.service import WebApprovalError, WebApprovalService

POLICY = {"web_approval": {"users": [
    {"id": "u_applicant", "name": "申请人", "roles": ["applicant"], "fb_user": "10086"},
    {"id": "u_manager", "name": "上级", "roles": ["manager"]},
    {"id": "u_owner", "name": "Owner", "roles": ["owner"]},
    {"id": "u_security", "name": "安全", "roles": ["security"]},
    {"id": "u_biadmin", "name": "BI管理员", "roles": ["bi_admin", "admin"]},
]}}


class FakePermission:
    def __init__(self):
        self.calls = []

    def grant(self, req):
        self.calls.append(req)
        return GrantResult("granted", "req-1", ["led-1"], {"dry_run": True})


class _FakeFineBI:
    def __init__(self, payload):
        self.payload = payload

    def get_row_filter(self, user, table):
        return {"status": 200, "data": [{"status": True, "data": self.payload}]}


class _FakeFineDB:
    def enabled(self):
        return True

    def row_filter_options(self, table, user):
        return [{"field_id": "t1_sales", "name": "销售", "values": ["B", "C"]}]


class _BrokenFineDB:
    def enabled(self):
        return True

    def row_filter_options(self, table, user):
        raise RuntimeError("(2013, 'Lost connection to MySQL server during query')")


class _FakePlatform:
    def __init__(self, items_by_key):
        self.items_by_key = items_by_key

    def query_user_detail(self, **kwargs):
        key, value = next(iter(kwargs.items()))
        return {"data": {"items": self.items_by_key.get((key, value)) or []}}


class _FakeMappingDB:
    def enabled(self):
        return True

    def feishu_user_by_id(self, feishu_user_id):
        return {"949dbaee": "测试人员"}.get(feishu_user_id, "")


class _RecordingNotifier:
    def __init__(self):
        self.users = []
        self.admins = []
        self.links = []

    def notify_user(self, open_id, title, content, link=""):
        self.users.append((open_id, title))
        self.links.append(link)

    def notify_admins(self, title, content, link=""):
        self.admins.append(title)
        self.links.append(link)


class _MembershipSnapshotPlatform:
    def __init__(self):
        self.calls = []

    def query_user_detail(self, username="", **kwargs):
        self.calls.append(username)
        return {"data": {"items": [{
            "username": username,
            "roles": [{"name": "运营角色"}],
            "departmentPosts": [
                {"department": {"fullPath": "财务部/财务一部"}}],
        }]}}


class _RecordingBitable:
    def __init__(self):
        self.table_id = "tbl_test"
        self.calls = []

    def upsert(self, request, record_id="", action="", link=""):
        self.calls.append((request["id"], action, record_id))
        return record_id or "rec_1"


class WebWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))
        self.permission = FakePermission()
        self.service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                          public_base_url="https://example.test")

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _payload(self, actions=None, days=90):
        return {"resource_type": "table", "resource_id": "t1",
                "resource_name": "订单明细", "actions": actions or ["use"],
                "days": days, "reason": "测试"}

    def _write_deps(self, dashboards):
        path = os.path.join(self.tmp.name, "dashboard_deps.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"dashboards": dashboards}, fh, ensure_ascii=False)
        self.service.deps_json = path

    def test_low_risk_chain_and_grant(self):
        self.service.set_owner_pair("table", "t1", ["u_owner"], ["u_manager"])
        req = self.service.create_request("u_applicant", self._payload())
        self.assertEqual(req["risk"], "low")
        self.assertEqual([s["role"] for s in req["steps"]],
                         ["data_owner", "business_owner"])
        self.service.approve(req["id"], "u_owner", "同意")
        self.assertEqual(self.service.get_request(req["id"])["current_seq"], 1)
        done = self.service.approve(req["id"], "u_manager", "同意")
        self.assertEqual(done["status"], "done")
        self.assertEqual(len(self.permission.calls), 1)

    def test_high_risk_chain(self):
        self.service.set_owner_pair("table", "t1", ["u_owner"], ["u_manager"])
        req = self.service.create_request(
            "u_applicant", self._payload(actions=["manage"], days=200))
        self.assertEqual(req["risk"], "high")
        self.assertEqual([s["role"] for s in req["steps"]],
                         ["data_owner", "business_owner"])

    def test_reject_and_withdraw(self):
        req = self.service.create_request("u_applicant", self._payload())
        rejected = self.service.reject(req["id"], req["steps"][0]["approver_id"],
                                       "资料不足")
        self.assertEqual(rejected["status"], "rejected")
        req2 = self.service.create_request("u_applicant", self._payload())
        withdrawn = self.service.withdraw(req2["id"], "u_applicant")
        self.assertEqual(withdrawn["status"], "withdrawn")

    def test_wrong_approver(self):
        self.service.set_owner_pair("table", "t1", ["u_owner"], ["u_manager"])
        req = self.service.create_request("u_applicant", self._payload())
        with self.assertRaises(WebApprovalError):
            self.service.approve(req["id"], "u_security")

    def test_session(self):
        sid = self.service.create_session("u_applicant")
        self.assertEqual(self.service.get_session_user(sid)["id"], "u_applicant")

    def test_permission_status_unknown_without_clients(self):
        status = self.service.permission_status(
            "u_applicant", "dashboard_entry", "e-1", actions=["view"])
        self.assertFalse(status["known"])

    def test_user_membership_snapshot_and_refresh_all(self):
        platform = _MembershipSnapshotPlatform()
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     platform=platform)
        first = service.user_membership("u_applicant")
        self.assertTrue(first["known"])
        self.assertEqual(first["roles"], ["运营角色"])
        self.assertEqual(first["departments"], ["财务部/财务一部"])
        service.user_membership("u_applicant")
        self.assertEqual(len(platform.calls), 1)  # 快照命中，不再请求接口
        result = service.refresh_all_memberships(sleep_seconds=0)
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["synced"], 1)

    def test_request_serial_and_document_fields(self):
        req1 = self.service.create_request("u_applicant", self._payload())
        payload1 = req1["payload"]
        self.assertRegex(payload1["request_no"], r"^\d{8}-01$")
        self.assertEqual(payload1["serial_text"], "01")
        self.assertEqual(payload1["permission_content"],
                         "订单明细；权限：使用")
        self.assertIn(" 至 ", payload1["permission_time"])
        fields = dict(self.service.card_fields(req1))
        self.assertEqual(fields["单号"], payload1["request_no"])
        self.assertEqual(fields["日期"], payload1["request_date"])
        self.assertEqual(fields["申请人"], "申请人")
        req2 = self.service.create_request("u_applicant", self._payload())
        self.assertEqual(req2["payload"]["serial_text"], "02")

    def test_bitable_synced_on_create_approve_and_done(self):
        bitable = _RecordingBitable()
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     bitable=bitable)
        service.set_owner_pair("table", "t1", ["u_owner"], ["u_manager"])
        req = service.create_request("u_applicant", self._payload())
        self.assertEqual(bitable.calls[0][1], "提交申请")
        service.approve(req["id"], "u_owner", "同意")
        actions = [c[1] for c in bitable.calls]
        self.assertIn("审批通过（待下一级）", actions)
        service.approve(req["id"], "u_manager", "同意")
        actions = [c[1] for c in bitable.calls]
        self.assertIn("授权完成", actions)
        self.assertEqual(self.storage.get_bitable_record_id(req["id"]), "rec_1")

    def test_dashboard_category_chain(self):
        self.service.set_owner_pair("dashboard", "dash-1", ["u_owner"], ["u_manager"])
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "测试看板",
            "permissions": ["view", "export"], "period_type": "temp", "days": 30,
        }, "dashboard")
        self.assertEqual(req["category"], "dashboard")
        self.assertEqual([s["role"] for s in req["steps"]],
                         ["data_owner", "business_owner"])
        self.service.approve(req["id"], "u_owner", "同意")
        self.service.approve(req["id"], "u_manager", "同意")
        self.assertEqual(self.service.get_request(req["id"])["status"], "done")

    def test_dashboard_edit_permission_implies_view(self):
        self.service.set_owner_pair("dashboard", "dash-1", ["u_owner"], ["u_manager"])
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "测试看板",
            "permissions": ["edit"], "days": 30,
        }, "dashboard")
        self.assertIn("view", req["payload"]["permissions"])
        self.assertIn("edit", req["payload"]["permissions"])
        self.assertTrue(req["payload"]["edit_requested"])

    def test_default_approver_is_fallback_when_no_owners(self):
        policy = {"web_approval": {"users": POLICY["web_approval"]["users"],
                                   "default_approver": "u_owner"}}
        service = WebApprovalService(self.storage, self.permission, policy=policy,
                                     public_base_url="https://example.test")
        req = service.create_request("u_applicant", self._payload())
        self.assertEqual([s["approver_id"] for s in req["steps"]], ["u_owner"])
        self.assertTrue(service.can_approve("u_owner", req["steps"][0]))

    def test_default_approver_may_be_applicant(self):
        policy = {"web_approval": {"users": POLICY["web_approval"]["users"],
                                   "default_approver": "u_applicant"}}
        service = WebApprovalService(self.storage, self.permission, policy=policy,
                                     public_base_url="https://example.test")
        req = service.create_request("u_applicant", self._payload())
        self.assertTrue(service.can_approve("u_applicant", req["steps"][0]))
        service.approve(req["id"], "u_applicant", "本人通过")
        self.assertEqual(service.get_request(req["id"])["status"], "done")

    def test_configured_default_approver_used_when_no_owners(self):
        policy = {"web_approval": {"users": POLICY["web_approval"]["users"]}}
        service = WebApprovalService(self.storage, self.permission, policy=policy,
                                     public_base_url="https://example.test")
        service.set_default_approver("u_owner")
        req = service.create_request("u_applicant", self._payload())
        self.assertEqual([s["approver_id"] for s in req["steps"]], ["u_owner"])
        self.assertTrue(service.can_approve("u_owner", req["steps"][0]))

    def test_row_values_parses_api_single_node(self):
        payload = json.dumps({
            "fieldId": "t1_sales",
            "fieldName": "销售",
            "filterValue": {"value": ["A"], "assist": ["B", "A", "C"]},
        }, ensure_ascii=False)
        permission = FakePermission()
        permission.finebi = _FakeFineBI(payload)
        service = WebApprovalService(self.storage, permission, policy=POLICY,
                                     public_base_url="https://example.test")
        self.assertEqual(service.row_values("t1", "u_applicant"),
                         [{"field_id": "t1_sales", "name": "销售",
                           "values": ["A", "B", "C"]}])

    def test_row_values_parses_legacy_node_list(self):
        payload = json.dumps({
            "filterValue": [{"fieldId": "t1_sales",
                             "filterValue": ["A", "B"]}],
        }, ensure_ascii=False)
        permission = FakePermission()
        permission.finebi = _FakeFineBI(payload)
        service = WebApprovalService(self.storage, permission, policy=POLICY,
                                     public_base_url="https://example.test")
        self.assertEqual(service.row_values("t1", "u_applicant"),
                         [{"field_id": "t1_sales", "name": "t1_sales",
                           "values": ["A", "B"]}])

    def test_row_values_merges_api_and_finedb(self):
        payload = json.dumps({
            "fieldId": "t1_sales", "fieldName": "销售",
            "filterValue": {"value": ["A"], "assist": ["B"]},
        }, ensure_ascii=False)
        permission = FakePermission()
        permission.finebi = _FakeFineBI(payload)
        service = WebApprovalService(self.storage, permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     finedb=_FakeFineDB())
        self.assertEqual(service.row_values("t1", "u_applicant"),
                         [{"field_id": "t1_sales", "name": "销售",
                           "values": ["A", "B", "C"]}])

    def test_row_values_uses_cache_when_finedb_unavailable(self):
        """FineDB 偶发丢连接时，枚举必须仍是全量值，而不是退化成用户已有值。"""
        payload = json.dumps({
            "fieldId": "t1_sales", "fieldName": "销售",
            "filterValue": {"value": ["A"], "assist": ["B"]},
        }, ensure_ascii=False)
        permission = FakePermission()
        permission.finebi = _FakeFineBI(payload)
        # 第一次 FineDB 正常，写入全量枚举缓存
        warm = WebApprovalService(self.storage, permission, policy=POLICY,
                                  public_base_url="https://example.test",
                                  finedb=_FakeFineDB())
        self.assertEqual(warm.row_values("t1", "u_applicant")[0]["values"],
                         ["A", "B", "C"])
        # 第二次 FineDB 丢连接，应读缓存拿到同样的全量枚举
        broken = WebApprovalService(self.storage, permission, policy=POLICY,
                                    public_base_url="https://example.test",
                                    finedb=_BrokenFineDB())
        self.assertEqual(broken.row_values("t1", "u_applicant")[0]["values"],
                         ["A", "B", "C"])

    def test_row_values_cache_isolated_per_table(self):
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     finedb=_BrokenFineDB())
        self.assertEqual(service.row_values("t1", "u_applicant"), [])

    def test_row_values_prefers_human_field_name(self):
        """FineBI 接口不回 fieldName 时，用 FineDB 的中文字段名，不显示字段 ID。"""
        payload = json.dumps({
            "fieldId": "t1_sales", "filterValue": {"value": ["A"]},
        }, ensure_ascii=False)
        permission = FakePermission()
        permission.finebi = _FakeFineBI(payload)
        service = WebApprovalService(self.storage, permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     finedb=_FakeFineDB())
        fields = service.row_values("t1", "u_applicant")
        self.assertEqual(fields[0]["name"], "销售")

    def test_dashboard_requires_any_id(self):
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "resource_name": "成本管控分析", "permissions": ["view"],
                "period_type": "temp", "days": 30,
            }, "dashboard")

    def test_dashboard_entry_only_request(self):
        req = self.service.create_request("u_applicant", {
            "resource_name": "成本管控分析", "entry_id": "entry-1",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        for step in req["steps"]:
            self.service.approve(req["id"], step["approver_id"], "同意")
        call = self.permission.calls[0]
        self.assertEqual(call.resource_type, "dashboard_entry")
        self.assertEqual(call.resource_id, "entry-1")
        self.assertEqual(call.items, [])

    def test_dashboard_grant_template_and_own_entry_no_parent(self):
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "成本管控分析",
            "entry_id": "entry-1", "permissions": ["view", "export"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        for step in req["steps"]:
            self.service.approve(req["id"], step["approver_id"], "同意")
        call = self.permission.calls[0]
        self.assertEqual(call.resource_type, "dashboard_export")
        self.assertEqual(call.resource_id, "dash-1")
        # 只额外授仪表板自身 entry，不含父节点
        self.assertEqual(len(call.items), 2)
        entry_items = [item for item in call.items
                       if item["resource_type"] == "dashboard_entry"]
        self.assertEqual(len(entry_items), 1)
        self.assertEqual(entry_items[0]["resource_id"], "entry-1")
        self.assertEqual(entry_items[0]["actions"], ["view", "export"])

    def test_dashboard_component_data_listed_and_granted_with_request(self):
        """依赖数据集只列在申请单里，组件数据随查看一起授权，不另建流程单。"""
        self.service.catalog_rows_override = [
            {"resource_type": "table", "resource_id": "t-1",
             "name": "天猫客服销售日汇总表", "path": "A/t-1", "fields": []},
            {"resource_type": "table", "resource_id": "t-2",
             "name": "抖店客服销售数据日汇总表", "path": "A/t-2", "fields": []},
            {"resource_type": "dashboard", "resource_id": "dash-1",
             "entry_id": "entry-1", "name": "客服销售主题分析",
             "path": "A/客服销售主题分析", "fields": []},
        ]
        self._write_deps({"dash-1": {"name": "客服销售主题分析", "datasets": [
            {"resource_id": "t-2", "name": "抖店客服销售数据日汇总表"},
            {"resource_id": "t-1", "name": "天猫客服销售日汇总表"},
        ]}})
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "entry_id": "entry-1",
            "resource_name": "客服销售主题分析",
            "permissions": ["view", "component"],
            "period_type": "temp", "days": 30, "reason": "看板数据",
        }, "dashboard")
        payload = req["payload"]
        self.assertEqual([d["name"] for d in payload["component_datasets"]],
                         ["天猫客服销售日汇总表", "抖店客服销售数据日汇总表"])
        self.assertIn("组件数据覆盖数据集", payload["permission_content"])
        for step in req["steps"]:
            self.service.approve(req["id"], step["approver_id"], "同意")
        call = self.permission.calls[0]
        table_items = [item for item in call.items
                       if item["resource_type"] == "table"]
        self.assertEqual([item["resource_id"] for item in table_items],
                         ["t-1", "t-2"])
        self.assertTrue(all(item["record_ledger"] is False
                            for item in table_items))

    def test_dashboard_component_data_unmatched_keeps_request_visible(self):
        """快照里没有依赖数据集时，组件数据不进入权限项，但记录原因供审批人看到。"""
        self.service.deps_json = os.path.join(self.tmp.name, "no_deps.json")
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-2", "entry_id": "entry-2",
            "resource_name": "空依赖看板",
            "permissions": ["view", "component"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        self.assertEqual(req["payload"]["permissions"], ["view"])
        self.assertEqual(req["payload"]["component_skipped_reason"],
                         "未匹配到依赖数据集")

    def test_row_permission_requires_values(self):
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "resource_type": "table", "resource_id": "t1",
                "permissions": ["use"], "row_enabled": True,
                "row_field": "", "row_values": [],
            }, "public_data")

    def test_long_period_is_high_risk(self):
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "permissions": ["view"],
            "period_type": "long", "days": 30,
        }, "dashboard")
        self.assertEqual(req["risk"], "high")


    def test_long_term_request_passes_long_term_flag(self):
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "测试看板",
            "permissions": ["view"], "period_type": "long", "days": 90,
        }, "dashboard")
        for step in req["steps"]:
            self.service.approve(req["id"], step["approver_id"], "同意")
        self.assertEqual(self.permission.calls[0].days, 3650)
        self.assertTrue(self.permission.calls[0].extra.get("long_term"))

    def test_identities_merge_same_name_only(self):
        conn = self.storage.conn
        now = "2026-01-01T00:00:00+08:00"
        for uid, name, open_id in (
                ("fs_app_gust", "gust", "ou_app"),
                ("fs_owner_a", "Gust-帆软软件", ""),
                ("fs_owner_b", "Gust-帆软软件", "ou_owner")):
            conn.execute(
                "INSERT INTO web_users(id,name,email,feishu_open_id,feishu_user_id,"
                "fb_user,roles,active,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (uid, name, "", open_id, "", "Gust", '["applicant"]', 1, now))
        conn.commit()
        self.assertNotIn("fs_owner_a", self.service.identities("fs_app_gust"))
        self.assertEqual(self.service.identities("fs_owner_a"),
                         ["fs_owner_a", "fs_owner_b"])
        step = {"approver_id": "fs_owner_a"}
        self.assertFalse(self.service.can_approve("fs_app_gust", step))
        self.assertTrue(self.service.can_approve("fs_owner_b", step))

    def test_notify_uses_alias_open_id(self):
        notifier = _RecordingNotifier()
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     notifier=notifier)
        conn = self.storage.conn
        now = "2026-01-01T00:00:00+08:00"
        for uid, open_id in (("fs_owner_a", ""), ("fs_owner_b", "ou_owner")):
            conn.execute(
                "INSERT INTO web_users(id,name,email,feishu_open_id,feishu_user_id,"
                "fb_user,roles,active,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (uid, "Gust-帆软软件", "", open_id, "", "Gust",
                 '["owner","admin"]', 1, now))
        conn.commit()
        service._notify({"id": "fs_owner_a", "name": "Gust-帆软软件",
                         "fb_user": "Gust", "feishu_open_id": ""},
                        "待审批", "内容", "wreq-1")
        self.assertEqual([u[0] for u in notifier.users], ["ou_owner"])


    def test_notify_omits_loopback_link(self):
        notifier = _RecordingNotifier()
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="http://127.0.0.1:8081",
                                     notifier=notifier)
        service._notify({"id": "u_owner", "name": "Owner", "fb_user": "",
                         "feishu_open_id": "ou_x"}, "待审批", "内容", "wreq-1")
        self.assertEqual(notifier.users[0][0], "ou_x")
        self.assertEqual(notifier.links, [""])


    def test_notify_uses_public_link(self):
        notifier = _RecordingNotifier()
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     notifier=notifier)
        service._notify({"id": "u_owner", "name": "Owner", "fb_user": "",
                         "feishu_open_id": "ou_x"}, "待审批", "内容", "wreq-1")
        self.assertEqual(notifier.links,
                         ["https://example.test/requests/wreq-1"])


    def test_resolve_fb_user_requires_exact_username(self):
        platform = _FakePlatform({
            ("username", "gust"): [{"username": "Gust"}],
            ("username", "Gust"): [{"username": "Gust"}],
        })
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     platform=platform)
        self.assertEqual(service.resolve_fb_user(name="gust"), "")
        self.assertEqual(service.resolve_fb_user(name="Gust"), "Gust")

    def test_resolve_fb_user_mobile_first_and_normalized(self):
        # 客户 FineBI 飞书集成按手机号匹配；手机号要归一化后优先匹配
        platform = _FakePlatform({
            ("mobile", "13800000000"): [{"username": "u_mobile"}],
            ("email", "a@b.c"): [{"username": "u_email"}],
        })
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     platform=platform)
        self.assertEqual(service.resolve_fb_user(
            mobile="+86 138-0000-0000", email="a@b.c", name="x"), "u_mobile")

    def test_resolve_fb_user_uses_finedb_mobile(self):
        class _DB:
            def enabled(self):
                return True

            def user_by_mobile(self, mobile):
                return "fb_mobile" if mobile == "8613800000000" else ""

        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     platform=_FakePlatform({}), finedb=_DB())
        # 输入 11 位，FineBI 里存 86 前缀的 13 位也能匹配
        self.assertEqual(service.resolve_fb_user(mobile="138 0000 0000"), "fb_mobile")

    def test_fb_user_from_finedb_mapping(self):
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     finedb=_FakeMappingDB())
        self.assertEqual(service.fb_user_for_feishu_user("949dbaee"), "测试人员")
        self.assertEqual(service.fb_user_for_feishu_user("unknown"), "")

    def test_update_user_fb_user(self):
        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test")
        service.update_user_fb_user("u_applicant", "测试人员")
        self.assertEqual(service.get_user("u_applicant")["fb_user"], "测试人员")


class _FakeSchedulePlatform:
    """平台客户端 Fake：记录调用；dry_run 属性可控。"""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.calls = []

    def set_user_platform_permission(self, user, module, use=True, empower=False):
        self.calls.append(("platform", user, module, use, empower))
        return {"data": [{"status": True}]}

    def set_user_schedule_permission(self, user, schedule_task, manage=True, empower=False):
        self.calls.append(("schedule", user, schedule_task, manage, empower))
        return {"data": [{"status": True}]}


class WebScheduleExecuteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _service(self, dry_run=True, platform=None):
        return WebApprovalService(
            self.storage, FakePermission(), policy=POLICY,
            public_base_url="https://example.test", dry_run=dry_run,
            platform=platform or _FakeSchedulePlatform())

    @staticmethod
    def _approve_all(service, req):
        for step in req["steps"]:
            service.approve(req["id"], step["approver_id"], "同意")

    def test_dry_run_schedule_does_not_write_permission_or_ledger(self):
        platform = _FakeSchedulePlatform()
        service = self._service(dry_run=True, platform=platform)
        req = service.create_request("u_applicant", {
            "schedule_task": "测试定时调度", "permissions": ["use", "manage"],
            "period_type": "temp", "days": 30}, "admin")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertTrue(final["result"]["ok"])
        self.assertTrue(final["result"]["dry_run"])
        self.assertEqual(platform.calls, [])  # dry-run 不调用真实平台接口
        self.assertEqual(self.storage.active_ledger(), [])

    def test_real_schedule_writes_module_and_task_ledger(self):
        platform = _FakeSchedulePlatform(dry_run=False)
        service = self._service(dry_run=False, platform=platform)
        req = service.create_request("u_applicant", {
            "schedule_task": "测试定时调度", "permissions": ["use", "manage", "empower"],
            "period_type": "temp", "days": 30}, "admin")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertIn(("platform", "10086", "decision-management-schedule", True, True),
                      platform.calls)
        self.assertIn(("schedule", "10086", "测试定时调度", True, True), platform.calls)
        types = sorted(ledger["resource_type"] for ledger in self.storage.active_ledger())
        self.assertEqual(types, ["platform_module", "schedule"])

    def test_platform_dry_run_flag_is_honoured(self):
        # service 层 dry_run=False，但平台客户端自身 dry_run=True 时也不应写台账
        platform = _FakeSchedulePlatform(dry_run=True)
        service = self._service(dry_run=False, platform=platform)
        req = service.create_request("u_applicant", {
            "schedule_task": "", "permissions": ["use"],
            "period_type": "temp", "days": 30}, "admin")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertTrue(final["result"].get("dry_run"))
        self.assertEqual(self.storage.active_ledger(), [])

    def test_warning_module_writes_platform_permission_and_ledger(self):
        platform = _FakeSchedulePlatform(dry_run=False)
        service = self._service(dry_run=False, platform=platform)
        req = service.create_request("u_applicant", {
            "module": "decision-management-warningcenter",
            "resource_name": "数据预警（预警中心）",
            "permissions": ["use"], "period_type": "temp", "days": 30}, "admin")
        self.assertEqual(req["payload"]["resource_type"], "platform_module")
        self.assertEqual(req["payload"]["resource_id"],
                         "decision-management-warningcenter")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertIn(("platform", "10086", "decision-management-warningcenter",
                       True, False), platform.calls)
        ledgers = self.storage.active_ledger()
        self.assertEqual([l["resource_type"] for l in ledgers], ["platform_module"])
        self.assertEqual(ledgers[0]["resource_id"],
                         "decision-management-warningcenter")

    def test_warning_module_dry_run_does_not_write(self):
        platform = _FakeSchedulePlatform(dry_run=False)
        service = self._service(dry_run=True, platform=platform)
        req = service.create_request("u_applicant", {
            "module": "decision-management-warningcenter",
            "permissions": ["use"], "period_type": "temp", "days": 30}, "admin")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertTrue(final["result"].get("dry_run"))
        self.assertEqual(platform.calls, [])
        self.assertEqual(self.storage.active_ledger(), [])


class _FakeMembershipPlatform:
    """角色/部门成员关系平台 Fake：支持 user/detail、角色/部门列表和写入。"""

    def __init__(self):
        self.calls = []
        self.roles = {}
        self.departments = {}   # username -> [[部门路径...], ...]
        self.role_list = [{"name": "角色A"}, {"name": "角色B"}]
        self.department_children = {
            (): [
                {"id": "d1", "pId": None, "name": "财务部", "type": "department"},
                {"id": "d2", "pId": "d1", "name": "财务一部", "type": "department"},
                {"id": "d3", "pId": None, "name": "销售部", "type": "department"},
                {"id": "p1", "pId": "d1", "name": "部长", "type": "position"},
            ],
        }

    def query_user_detail(self, username="", email="", mobile="", page=1, count=200):
        self.calls.append(("query_user", username))
        if username not in ("10086",):
            return {"data": {"total": 0, "items": []}}
        items = [{
            "username": username,
            "roles": [{"name": name} for name in self.roles.get(username, [])],
            "departmentPosts": [
                {"department": {"name": path[-1], "fullPath": "/".join(path)}}
                for path in self.departments.get(username, [])],
        }]
        return {"data": {"total": 1, "items": items}}

    def set_user_roles(self, user, add=None, remove=None):
        self.calls.append(("set_roles", user, list(add or []), list(remove or [])))
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

    def query_roles(self, role="", exact=False):
        self.calls.append(("query_roles", role, exact))
        return {"status": 200, "data": list(self.role_list)}

    def query_departments(self, department):
        self.calls.append(("query_departments", tuple(department)))
        return {"status": 200, "data": list(
            self.department_children.get(tuple(department), []))}


class WebMembershipTest(unittest.TestCase):
    """申请加入已有角色/部门：审批通过后只加成员关系，到期只回收本次新增部分。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))
        self.platform = _FakeMembershipPlatform()

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _service(self, dry_run=False):
        permission = PermissionService(
            None, self.storage, platform=self.platform, max_days=365,
            dry_run=dry_run, adopt_existing=False)
        return WebApprovalService(
            self.storage, permission, policy=POLICY,
            public_base_url="https://example.test", dry_run=dry_run,
            platform=self.platform)

    @staticmethod
    def _approve_all(service, req):
        for step in req["steps"]:
            service.approve(req["id"], step["approver_id"], "同意")

    def test_role_membership_grant_and_ledger(self):
        service = self._service(dry_run=False)
        req = service.create_request("u_applicant", {
            "membership_type": "role", "targets": ["角色A", "角色B"],
            "period_type": "temp", "days": 30, "reason": "测试"}, "membership")
        self.assertEqual(req["category"], "membership")
        self.assertEqual(req["payload"]["resource_type"], "role")
        self.assertEqual(req["payload"]["resource_name"], "角色：角色A、角色B")
        self.assertEqual([s["approver_id"] for s in req["steps"]], ["u_biadmin"])
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertTrue(final["result"]["ok"])
        self.assertEqual(self.platform.roles["10086"], ["角色A", "角色B"])
        ledgers = self.storage.active_ledger(user="10086")
        self.assertEqual(sorted(l["resource_type"] for l in ledgers), ["role", "role"])

    def test_department_membership_grant_and_ledger(self):
        service = self._service(dry_run=False)
        rid = json.dumps(["财务部", "财务一部"], ensure_ascii=False)
        req = service.create_request("u_applicant", {
            "membership_type": "department", "targets": [rid],
            "period_type": "temp", "days": 30, "reason": "测试"}, "membership")
        self.assertEqual(req["payload"]["resource_type"], "department")
        self.assertEqual(req["payload"]["resource_name"], "部门：财务部/财务一部")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertIn(["财务部", "财务一部"], self.platform.departments["10086"])
        ledgers = self.storage.active_ledger(user="10086")
        self.assertEqual([l["resource_type"] for l in ledgers], ["department"])
        self.assertEqual(ledgers[0]["resource_id"], rid)

    def test_preexisting_role_is_not_duplicated_or_ledgered(self):
        self.platform.roles["10086"] = ["角色A"]
        service = self._service(dry_run=False)
        req = service.create_request("u_applicant", {
            "membership_type": "role", "targets": ["角色A"],
            "period_type": "temp", "days": 30}, "membership")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "done")
        self.assertEqual([c for c in self.platform.calls if c[0] == "set_roles"], [])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_dry_run_does_not_write_membership(self):
        service = self._service(dry_run=True)
        req = service.create_request("u_applicant", {
            "membership_type": "role", "targets": ["角色A"],
            "period_type": "temp", "days": 30}, "membership")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertTrue(final["result"].get("dry_run"))
        self.assertEqual([c for c in self.platform.calls if c[0].startswith("set_")], [])
        self.assertEqual(self.storage.active_ledger(user="10086"), [])

    def test_membership_requires_type_and_targets(self):
        service = self._service(dry_run=False)
        with self.assertRaises(WebApprovalError):
            service.create_request("u_applicant", {
                "membership_type": "", "targets": ["角色A"]}, "membership")
        with self.assertRaises(WebApprovalError):
            service.create_request("u_applicant", {
                "membership_type": "role", "targets": []}, "membership")

    def test_membership_owner_configured_used_as_approver(self):
        service = self._service(dry_run=False)
        service.set_membership_owner("u_owner")
        self.assertEqual(service.membership_owner()["id"], "u_owner")
        req = service.create_request("u_applicant", {
            "membership_type": "role", "targets": ["角色A"],
            "period_type": "temp", "days": 30}, "membership")
        self.assertEqual([(s["role"], s["approver_id"]) for s in req["steps"]],
                         [("membership_owner", "u_owner")])
        service.approve(req["id"], "u_owner", "同意")
        self.assertEqual(service.get_request(req["id"])["status"], "done")

    def test_membership_owner_falls_back_when_not_configured(self):
        service = self._service(dry_run=False)
        req = service.create_request("u_applicant", {
            "membership_type": "department", "targets": [
                json.dumps(["财务部"], ensure_ascii=False)],
            "period_type": "temp", "days": 30}, "membership")
        self.assertEqual(req["steps"][0]["role"], "owner")
        self.assertEqual(req["steps"][0]["approver_id"], "u_biadmin")

    def test_membership_options_roles_and_department_tree(self):
        service = self._service(dry_run=False)
        options = service.membership_options()
        self.assertEqual([r["name"] for r in options["roles"]], ["角色A", "角色B"])
        self.assertEqual([d["full_path"] for d in options["departments"]],
                         ["财务部", "财务部/财务一部", "销售部"])
        self.assertEqual(options["errors"], [])
        calls = len([c for c in self.platform.calls if c[0] == "query_roles"])
        service.membership_options()  # 命中缓存
        self.assertEqual(len([c for c in self.platform.calls
                              if c[0] == "query_roles"]), calls)

    def test_membership_requires_bound_finebi_account(self):
        service = self._service(dry_run=False)
        req = service.create_request("u_biadmin", {
            "membership_type": "role", "targets": ["角色A"],
            "period_type": "temp", "days": 30}, "membership")
        self._approve_all(service, req)
        final = service.get_request(req["id"])
        self.assertEqual(final["status"], "failed")
        self.assertIn("未绑定 FineBI 账号", final["result"]["error"])


class WebConcurrencyGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))
        self.permission = FakePermission()
        self.service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                          public_base_url="https://example.test")

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _payload(self):
        return {"resource_type": "table", "resource_id": "t1",
                "resource_name": "订单明细", "actions": ["use"], "days": 30}

    def test_stale_step_action_is_rejected(self):
        req = self.service.create_request("u_applicant", self._payload())
        step = req["steps"][0]
        # 模拟并发/重复提交：另一个请求已把该节点处理掉
        self.assertTrue(self.service._act(step["id"], "approved", "first"))
        with self.assertRaises(WebApprovalError) as ctx:
            self.service.approve(req["id"], step["approver_id"], "second")
        self.assertIn("已被处理", str(ctx.exception))
        self.assertEqual(len(self.permission.calls), 0)  # 未触发授权

    def test_status_cas_only_first_transition_wins(self):
        req = self.service.create_request("u_applicant", self._payload())
        self.assertTrue(self.service._set_status(req["id"], "approved", expect="pending"))
        self.assertFalse(self.service._set_status(req["id"], "approved", expect="pending"))

    def test_missing_approver_rejected_before_insert(self):
        # 独立库：setUp 里已 seed 完整 POLICY 用户，不能复用
        tmp = tempfile.TemporaryDirectory()
        storage = Storage(os.path.join(tmp.name, "only-applicant.db"))
        try:
            policy = {"web_approval": {"users": [
                {"id": "u_applicant", "name": "申请人", "roles": ["applicant"],
                 "fb_user": "10086"},
            ]}}
            service = WebApprovalService(storage, self.permission, policy=policy,
                                         public_base_url="https://example.test")
            with self.assertRaises(WebApprovalError) as ctx:
                service.create_request("u_applicant", self._payload())
            self.assertIn("Owner", str(ctx.exception))
            count = storage.conn.execute(
                "SELECT COUNT(*) FROM web_requests").fetchone()[0]
            self.assertEqual(count, 0)
        finally:
            storage.close()
            tmp.cleanup()

    def test_notify_uses_notify_users_for_multiple_aliases(self):
        calls = []

        class _NotifierWithBatch:
            def notify_users(self, open_ids, title, content, link=""):
                calls.append((list(open_ids), title, link))

            def notify_user(self, open_id, title, content, link=""):
                calls.append(([open_id], title, link))

            def notify_admins(self, title, content, link=""):
                calls.append(([], title, link))

        service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                     public_base_url="https://example.test",
                                     notifier=_NotifierWithBatch())
        ok = service._notify({"id": "u_owner", "name": "Owner", "fb_user": "",
                              "feishu_open_id": "ou_owner"}, "待审批", "内容", "wreq-1")
        self.assertIsNone(ok)
        self.assertEqual(calls[0][0], ["ou_owner"])


class PlatformClientTest(unittest.TestCase):
    def _client(self, response, dry_run=False):
        class _Http:
            def __init__(self):
                self.calls = []

            def request(self, method, url, headers=None, json_body=None, params=None):
                self.calls.append({"method": method, "url": url,
                                   "body": json_body, "params": params})
                return response

        http = _Http()
        client = FineBIPlatformClient("http://bi.test:8075", "cid", "sec",
                                      "api_bot", http=http, dry_run=dry_run)
        return client, http

    def test_top_level_error_envelope_raises(self):
        # 真实探测：GET /v3/department 参数不合法时 HTTP 200 + status=400 信封
        client, _ = self._client({"status": 400, "errorCode": "E000101",
                                  "errorMsg": "department not exist"})
        with self.assertRaises(ApiError) as ctx:
            client.query_departments(["财务部"])
        self.assertEqual(ctx.exception.status, 400)

    def test_batch_item_failure_raises(self):
        client, _ = self._client({"status": 200, "data": [
            {"status": False, "errorMsg": "role not exist"}]})
        with self.assertRaises(ApiError) as ctx:
            client.set_user_roles("10086", add=["不存在角色"])
        self.assertEqual(ctx.exception.status, "BATCH")

    def test_success_response_passthrough(self):
        client, http = self._client({"status": 200, "data": [{"id": "t1"}]})
        resp = client.list_schedules(page=2, per_page=20)
        self.assertEqual(resp["data"], [{"id": "t1"}])
        self.assertEqual(http.calls[0]["params"],
                         {"page": 2, "perPage": 20, "decUser": "api_bot"})

    def test_empty_dec_user_omits_param(self):
        # 客户 FineBI 没有 api_bot 用户，应用身份必须不带 decUser
        client, http = self._client({"status": 200, "data": []})
        client.dec_user = ""
        client.list_schedules(page=1)
        self.assertNotIn("decUser", http.calls[0]["params"])

    def test_departments_query_is_json_array(self):
        client, http = self._client({"status": 200, "data": []})
        client.query_departments(["财务部"])
        self.assertEqual(http.calls[0]["params"]["department"], '["财务部"]')

    def test_department_users_body_matches_doc(self):
        client, http = self._client({"status": 200, "data": []})
        client.query_department_users(["财务部"], recursive=True)
        body = http.calls[0]["body"]
        self.assertEqual(body, [{"department": '["财务部"]', "recursive": True}])

    def test_user_department_body_matches_doc(self):
        client, http = self._client({"status": 200, "data": [{"status": True}]})
        client.set_user_departments(
            "10086", add=[["财务部", "财务二部"]], remove=[["财务部"]])
        call = http.calls[0]
        self.assertEqual(call["method"], "PUT")
        self.assertTrue(call["url"].endswith(API_ROOT + "/v3/user/department"))
        self.assertEqual(call["body"], [{
            "user": "10086",
            "add": [{"department": '["财务部", "财务二部"]'}],
            "remove": [{"department": '["财务部"]'}],
        }])

    def test_user_department_write_respects_dry_run(self):
        client, http = self._client({"status": 200, "data": [{"status": True}]},
                                    dry_run=True)
        resp = client.set_user_departments("10086", add=[["财务部"]])
        self.assertTrue(resp.get("dry_run"))
        self.assertEqual(http.calls, [])

    def test_entry_tree_query(self):
        client, http = self._client({"status": 200, "data": []})
        client.get_entry_tree("pc")
        self.assertEqual(http.calls[0]["method"], "GET")
        self.assertTrue(http.calls[0]["url"].endswith(API_ROOT + "/v3/entry/tree"))
        self.assertEqual(http.calls[0]["params"]["device"], "pc")

    def test_platform_permission_body_uses_singular_module(self):
        client, http = self._client({"status": 200, "data": [{"status": True}]})
        client.set_user_platform_permission("10086", "decision-management-schedule",
                                            use=True, empower=False)
        self.assertEqual(http.calls[0]["body"], [{
            "user": "10086", "module": "decision-management-schedule",
            "authority": {"usePrivilege": True, "empowerPrivilege": False}}])

    def test_schedule_permission_body_matches_doc(self):
        client, http = self._client({"status": 200, "data": [{"status": True}]})
        client.set_user_schedule_permission("10086", "测试定时调度",
                                            manage=True, empower=False)
        self.assertEqual(http.calls[0]["body"], [{
            "user": "10086", "scheduleTask": "测试定时调度",
            "authority": {"managePrivilege": True, "empowerPrivilege": False}}])

    def test_user_detail_default_count_matches_doc(self):
        # username 模糊匹配，count 用文档默认 200，避免目标用户被截断到第一页外
        client, http = self._client({"status": 200, "data": {"items": []}})
        client.query_user_detail(username="a")
        params = http.calls[0]["params"]
        self.assertEqual(params["count"], 200)
        self.assertEqual(params["page"], 1)

    def test_execute_schedule_body_uses_task_field(self):
        # 文档请求体是 [{"task": "任务ID/名称"}]，旧实现误用 id 字段
        client, http = self._client({"status": 200, "data": [{"status": True}]})
        client.execute_schedule("2ffd26c7-6ee1-4e07-b940-adf0ca62667f")
        self.assertEqual(http.calls[0]["body"],
                         [{"task": "2ffd26c7-6ee1-4e07-b940-adf0ca62667f"}])


class _FakeHandoverFineBI:
    """按 docs/finebi 资源交接响应结构造数据。"""

    def __init__(self, analysis, public, support_analysis_packs=True,
                 fail_resource=None):
        self.analysis = analysis
        self.public = public
        self.support_analysis_packs = support_analysis_packs
        self.fail_resource = fail_resource
        self.args = None

    def handover_analysis(self, user):
        return {"data": self.analysis}

    def handover_public(self, user):
        return {"data": self.public}

    def handover_start(self, sender, accepter, pack_ids=None, table_names=None,
                       subject_ids=None, **kwargs):
        self.args = {"sender": sender, "accepter": accepter,
                     "pack_ids": list(pack_ids or []),
                     "table_names": list(table_names or []),
                     "subject_ids": list(subject_ids or [])}
        if "analysis_pack_ids" in kwargs:
            if not self.support_analysis_packs:
                raise TypeError("unexpected keyword argument 'analysis_pack_ids'")
            self.args["analysis_pack_ids"] = list(kwargs["analysis_pack_ids"] or [])
        fail = self.fail_resource or {
            "resourceInPublicData": {"tableNames": [], "packIds": []},
            "resourceInUserAnalysis": {"subjectIds": [], "packIds": []}}
        return {"status": 200, "data": [{"status": True, "data": {
            "userRoleEqual": False, "success": True, "failResource": fail}}]}


class OffboardServiceTest(unittest.TestCase):
    ANALYSIS = {
        "id": "__my_analysis__user1",
        "folders": [
            {"id": "af1", "folders": [
                {"id": "af2", "folders": [], "subjects": [{"id": "as2"}]}],
             "subjects": [{"id": "as1"}]},
        ],
        "subjects": [{"id": "as0"}],
    }
    PUBLIC = {
        "id": "__root_group__",
        "folders": [
            {"id": "pf1", "folders": [], "tables": [{"id": "pt1"}]},
            {"id": "pf2", "folders": [], "tables": []},
        ],
        "tables": [],
    }

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _service(self, finebi, dry_run=False):
        return OffboardService(finebi, self.storage, platform=None,
                               revoke_service=None, dry_run=dry_run)

    def test_handover_splits_public_and_user_analysis(self):
        finebi = _FakeHandoverFineBI(self.ANALYSIS, self.PUBLIC)
        summary = self._service(finebi).offboard("10086", accepter="10087")
        self.assertEqual(finebi.args["sender"], "10086")
        self.assertEqual(finebi.args["accepter"], "10087")
        # 公共数据只传公共文件夹/表；我的分析主题单独传；分析文件夹不混进公共 packIds
        self.assertEqual(finebi.args["pack_ids"], ["pf1", "pf2"])
        self.assertEqual(finebi.args["table_names"], ["pt1"])
        self.assertEqual(finebi.args["subject_ids"], ["as0", "as1", "as2"])
        self.assertEqual(finebi.args["analysis_pack_ids"], ["af1", "af2"])
        self.assertEqual(summary["resources"]["packs"], ["af1", "af2", "pf1", "pf2"])
        self.assertEqual(summary["resources"]["public"]["packs"], ["pf1", "pf2"])
        self.assertIn("handover_done", summary["steps"])
        self.assertNotIn("__root_group__", summary["resources"]["packs"])
        self.assertNotIn("__my_analysis__user1", summary["resources"]["packs"])

    def test_handover_fallback_when_client_lacks_analysis_packs(self):
        finebi = _FakeHandoverFineBI(self.ANALYSIS, self.PUBLIC,
                                     support_analysis_packs=False)
        summary = self._service(finebi).offboard("10086", accepter="10087")
        self.assertNotIn("analysis_pack_ids", finebi.args)
        self.assertEqual(finebi.args["subject_ids"], ["as0", "as1", "as2"])
        self.assertIn("handover_done", summary["steps"])
        joined = " ".join(summary.get("warnings") or [])
        self.assertIn("我的分析文件夹未自动交接", joined)

    def test_handover_reports_failed_resources(self):
        finebi = _FakeHandoverFineBI(self.ANALYSIS, self.PUBLIC, fail_resource={
            "resourceInPublicData": {"tableNames": ["pt-missing"], "packIds": []},
            "resourceInUserAnalysis": {"subjectIds": [], "packIds": []}})
        summary = self._service(finebi).offboard("10086", accepter="10087")
        joined = " ".join(summary.get("warnings") or [])
        self.assertIn("pt-missing", joined)
        self.assertIn("部分资源交接失败", joined)

    def test_no_accepter_marks_handover_skipped(self):
        finebi = _FakeHandoverFineBI(self.ANALYSIS, self.PUBLIC)
        summary = self._service(finebi).offboard("10086")
        self.assertTrue(summary["handover"].get("skipped"))
        self.assertIsNone(finebi.args)

    def test_dry_run_does_not_call_handover(self):
        finebi = _FakeHandoverFineBI(self.ANALYSIS, self.PUBLIC)
        summary = self._service(finebi, dry_run=True).offboard("10086", accepter="10087")
        self.assertIsNone(finebi.args)
        self.assertTrue(summary["handover"].get("dry_run"))


class WebOwnerConfigTest(unittest.TestCase):
    """后台 Owner 配置：数据/业务两类、目录继承、覆盖式保存、审批链。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))
        self.permission = FakePermission()
        self.service = WebApprovalService(self.storage, self.permission, policy=POLICY,
                                          public_base_url="https://example.test")

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_set_owners_replaces_and_clears(self):
        self.service.set_owners("dashboard_folder", "A/B", ["u_owner", "u_manager"],
                                "data")
        self.assertEqual(
            sorted(u["id"] for u in self.service.owners_for("dashboard_folder", "A/B", "data")),
            ["u_manager", "u_owner"])
        self.service.set_owners("dashboard_folder", "A/B", ["u_security"], "data")
        self.assertEqual(
            [u["id"] for u in self.service.owners_for("dashboard_folder", "A/B", "data")],
            ["u_security"])
        self.service.set_owners("dashboard_folder", "A/B", [], "data")
        self.assertEqual(self.service.owners_for("dashboard_folder", "A/B", "data"), [])

    def test_set_owner_pair_saves_both_types(self):
        saved = self.service.set_owner_pair("table", "t1", ["u_owner"], ["u_manager"])
        self.assertEqual(saved, {"data": ["u_owner"], "business": ["u_manager"]})
        self.assertEqual([u["id"] for u in self.service.owners_for("table", "t1", "data")],
                         ["u_owner"])
        self.assertEqual([u["id"] for u in self.service.owners_for("table", "t1", "business")],
                         ["u_manager"])

    def test_dashboard_folder_owner_inherited(self):
        self.service.set_owners("dashboard_folder", "Irene测试/发布方式区别",
                                ["u_owner"], "data")
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "成本管控分析",
            "resource_path": "Irene测试/发布方式区别/成本管控分析",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        steps = {s["role"]: s["approver_id"] for s in req["steps"]}
        self.assertEqual(steps, {"data_owner": "u_owner"})

    def test_direct_owner_overrides_inherited_folder_owner(self):
        self.service.set_owners("dashboard_folder", "A", ["u_owner"], "data")
        self.service.set_owners("dashboard", "dash-1", ["u_security"], "data")
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "看板",
            "resource_path": "A/看板",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        steps = {s["role"]: s["approver_id"] for s in req["steps"]}
        self.assertEqual(steps, {"data_owner": "u_security"})

    def test_table_folder_owner_inherited(self):
        self.service.set_owners("folder", "Cyan", ["u_owner"], "data")
        req = self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t1",
            "resource_name": "订单数据", "resource_path": "Cyan/订单数据",
            "permissions": ["use"], "period_type": "temp", "days": 90,
        }, "public_data")
        steps = {s["role"]: s["approver_id"] for s in req["steps"]}
        self.assertEqual(steps, {"data_owner": "u_owner"})

    def test_entry_only_dashboard_matches_owner_by_path(self):
        self.service.set_owners("dashboard", "Irene测试/看板", ["u_security"], "data")
        req = self.service.create_request("u_applicant", {
            "entry_id": "entry-1", "resource_name": "看板",
            "resource_path": "Irene测试/看板",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        steps = {s["role"]: s["approver_id"] for s in req["steps"]}
        self.assertEqual(steps, {"data_owner": "u_security"})

    def test_business_owner_is_second_step(self):
        self.service.set_owner_pair("table", "t1", ["u_owner"], ["u_manager"])
        req = self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t1",
            "resource_name": "订单数据", "permissions": ["use"],
            "period_type": "temp", "days": 90,
        }, "public_data")
        self.assertEqual([s["role"] for s in req["steps"]],
                         ["data_owner", "business_owner"])
        self.assertEqual([s["approver_id"] for s in req["steps"]],
                         ["u_owner", "u_manager"])

    def test_owner_types_inherit_independently(self):
        # 目录只配了数据 Owner；资源自己只配业务 Owner → 两级审批各取各的
        self.service.set_owners("dashboard_folder", "A", ["u_owner"], "data")
        self.service.set_owners("dashboard", "dash-1", ["u_manager"], "business")
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "看板",
            "resource_path": "A/看板",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        steps = {s["role"]: s["approver_id"] for s in req["steps"]}
        self.assertEqual(steps, {"data_owner": "u_owner",
                                 "business_owner": "u_manager"})

    def test_dashboard_folder_request_expands_targets(self):
        rows = [
            {"resource_type": "dashboard", "name": "d1", "path": "A/d1",
             "resource_id": "d1", "entry_id": "e1"},
            {"resource_type": "dashboard", "name": "d2", "path": "A/B/d2",
             "resource_id": "d2", "entry_id": "e2"},
            {"resource_type": "dashboard", "name": "x", "path": "X/x",
             "resource_id": "x", "entry_id": "ex"},
        ]
        self.service._catalog_rows = lambda: rows
        self.service.set_owners("dashboard_folder", "A", ["u_owner"], "data")
        req = self.service.create_request("u_applicant", {
            "resource_type": "dashboard_folder", "resource_path": "A",
            "resource_name": "A", "permissions": ["view"],
            "period_type": "temp", "days": 30, "reason": "文件夹批量",
        }, "dashboard")
        payload = req["payload"]
        self.assertEqual(payload["resource_type"], "dashboard_folder")
        self.assertEqual(payload["resource_id"], "A")
        self.assertEqual(payload["resource_name"], "A（文件夹）")
        self.assertEqual(sorted(t["resource_id"] for t in payload["targets"]),
                         ["d1", "d2"])
        # 文件夹 Owner 参与审批链
        self.assertEqual([s["approver_id"] for s in req["steps"]], ["u_owner"])
        self.service.approve(req["id"], "u_owner", "同意")
        granted = self.permission.calls[0]
        self.assertEqual(len(granted.items), 4)
        self.assertEqual(sorted(i["resource_type"] for i in granted.items),
                         ["dashboard_entry", "dashboard_entry",
                          "dashboard_view", "dashboard_view"])

    def test_dashboard_folder_without_dashboards_raises(self):
        self.service._catalog_rows = lambda: [
            {"resource_type": "dashboard", "name": "x", "path": "X/x",
             "resource_id": "x", "entry_id": "ex"}]
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "resource_type": "dashboard_folder", "resource_path": "A",
                "resource_name": "A", "permissions": ["view"],
                "period_type": "temp", "days": 30,
            }, "dashboard")

    def test_resource_tree_nodes_have_path_and_owner_key(self):
        rows = [
            {"resource_type": "folder", "name": "A", "path": "A", "resource_id": "f1"},
            {"resource_type": "table", "name": "t", "path": "A/t", "resource_id": "t1"},
            {"resource_type": "dashboard", "name": "d", "path": "A/d",
             "resource_id": "d1", "entry_id": "e1"},
        ]
        self.service._catalog_rows = lambda: rows
        dash = self.service.resource_tree("dashboard")[0]
        self.assertEqual(dash["owner_key"], "dashboard_folder:A")
        self.assertEqual(dash["path"], "A")
        self.assertTrue(dash["selectable"])
        self.assertEqual(dash["count"], 1)
        leaf = dash["children"][0]
        self.assertEqual(leaf["owner_key"], "dashboard:d1")
        self.assertEqual(leaf["path"], "A/d")
        public = self.service.resource_tree("public_data")[0]
        self.assertEqual(public["owner_key"], "folder:A")
        self.assertTrue(public["selectable"])
        self.assertEqual(public["children"][0]["owner_key"], "table:t1")

    def test_configured_owner_wins_over_default_approver(self):
        policy = {"web_approval": {"users": POLICY["web_approval"]["users"],
                                   "default_approver": "u_biadmin"}}
        service = WebApprovalService(self.storage, FakePermission(), policy=policy,
                                     public_base_url="https://example.test")
        service.set_owners("dashboard_folder", "A", ["u_owner"], "data")
        req = service.create_request("u_applicant", {
            "resource_id": "dash-1", "resource_name": "看板",
            "resource_path": "A/看板",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        self.assertEqual([s["approver_id"] for s in req["steps"]], ["u_owner"])

    def test_owner_display_map_marks_inherited(self):
        rows = [
            {"resource_type": "folder", "name": "A", "path": "A", "resource_id": "f1"},
            {"resource_type": "dashboard", "name": "看板", "path": "A/看板",
             "resource_id": "d1", "entry_id": "e1"},
        ]
        self.service._catalog_rows = lambda: rows
        self.service.set_owners("dashboard_folder", "A", ["u_owner"], "data")
        display = self.service.owner_display_map("dashboard")
        self.assertEqual(display["dashboard_folder:A"]["data"]["names"], ["Owner"])
        self.assertFalse(display["dashboard_folder:A"]["data"]["inherited"])
        self.assertEqual(display["dashboard_folder:A"]["business"]["names"], [])
        self.assertEqual(display["dashboard:d1"]["data"]["names"], ["Owner"])
        self.assertTrue(display["dashboard:d1"]["data"]["inherited"])
        self.assertEqual(display["dashboard:d1"]["data"]["from"], "A")


if __name__ == "__main__":
    unittest.main()
