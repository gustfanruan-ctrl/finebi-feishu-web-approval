# -*- coding: utf-8 -*-
"""审批人行/列权限补充 + 角色/部门权限摘要 单测。"""
import json
import os
import tempfile
import unittest
from types import SimpleNamespace

from executor.models import GrantResult, ResourceType
from executor.storage import Storage
from executor.web.service import WebApprovalError, WebApprovalService

try:
    from fastapi.testclient import TestClient
    HAS_WEB = True
except ImportError:  # pragma: no cover
    HAS_WEB = False

USERS = [
    {"id": "u_applicant", "name": "申请人", "roles": ["applicant"], "fb_user": "10086"},
    {"id": "u_manager", "name": "上级", "roles": ["manager"]},
    {"id": "u_owner", "name": "Owner", "roles": ["owner"]},
]
POLICY = {"web_approval": {"users": USERS}}
CATALOG = [
    {"resource_type": "folder", "resource_id": "p-1", "name": "A",
     "path": "A", "fields": []},
    {"resource_type": "table", "resource_id": "t1", "name": "订单明细",
     "path": "A/订单明细", "fields": [
         {"fieldId": "t1_region", "name": "大区"},
         {"fieldId": "t1_amount", "name": "金额"}]},
    {"resource_type": "dashboard", "resource_id": "d-1", "entry_id": "e-1",
     "name": "成本看板", "path": "A/成本看板", "fields": []},
]


class FakeFineBI:
    def __init__(self):
        self.role_rules = {"运营主管"}
        self.dept_rules = {"部门：华东区"}
        self.user_rules = {"zhangsan"}
        self.applicant_rule = ""
        self.calls = []

    def get_row_filters_roles(self, roles, table_name):
        self.calls.append(("role", tuple(roles), table_name))
        return {"data": [{"status": True,
                          "data": '{"filterType":10}' if r in self.role_rules else ""}
                         for r in roles]}

    def get_row_filters_deposts(self, subjects, table_name):
        self.calls.append(("depost", len(subjects), table_name))
        return {"data": [{"status": True,
                          "data": '{"filterType":10}'
                          if s.get("name") in self.dept_rules else ""}
                         for s in subjects]}

    def get_row_filters_users(self, users, table_name):
        self.calls.append(("users", tuple(users), table_name))
        return {"data": [{"status": True,
                          "data": '{"filterType":10}' if u in self.user_rules else ""}
                         for u in users]}

    def get_row_filter(self, user, table_name):
        self.calls.append(("applicant", user, table_name))
        return {"data": [{"status": True, "data": self.applicant_rule}]}

    def get_tables_info(self, tables):
        return {"data": [{"status": True, "data": {
            "tableName": tables[0],
            "fields": [{"fieldId": "t1_region", "name": "大区",
                        "transferName": "大区"},
                       {"fieldId": "t1_amount", "name": "金额",
                        "transferName": "金额"}]}}]}

    def get_folder_permissions_role(self, role, pack_ids):
        return {"data": [{"status": True,
                          "data": {"usePrivilege": bool(pack_ids)}}]}

    def get_table_permissions_role(self, role, table_names):
        return {"data": [{"status": True,
                          "data": {"usePrivilege": True, "biData": True}}]}

    def get_dashboard_auth_role(self, role, ids):
        return {"data": [{"status": True, "data": {"view": True, "export": False}}]}

    def get_row_filters_role(self, role, table_names):
        return {"data": [{"status": True, "data": '{"filterType":10}'}]}

    def get_folder_permissions_depost(self, department, position, pack_ids):
        return {"data": [{"status": True,
                          "data": {"usePrivilege": True}}]}

    def get_table_permissions_depost(self, department, position, table_names):
        return {"data": [{"status": True,
                          "data": {"usePrivilege": True, "biData": False}}]}

    def get_dashboard_auth_depost(self, department, position, ids):
        return {"data": [{"status": True, "data": {"view": True}}]}

    def get_row_filters_depost(self, department, position, table_names):
        return {"data": [{"status": True, "data": ""}]}


class FakePlatform:
    def query_roles(self, role="", exact=False):
        return {"data": [{"name": "运营主管"}, {"name": "运营"}]}

    def query_departments(self, department):
        return {"data": [
            {"id": "d-1", "pId": None, "name": "华东区", "type": "department"},
            {"id": "pos-1", "pId": "d-1", "name": "经理", "type": "position"},
        ]}

    def query_users(self, username="", email="", page=1, count=200):
        items = [{"username": "zhangsan", "enable": True},
                 {"username": "lisi", "enable": True}]
        return {"data": {"total": 2, "items": items}}

    def query_role_entries(self, role, entries):
        return {"data": {"entry": [
            {"entryId": entries[0] if entries else "e-1",
             "authority": {"viewPrivilege": True, "export": False,
                           "editPrivilege": False}}]}}

    def query_depost_entries(self, department, position, entries):
        return {"data": {"entry": [
            {"entryId": entries[0] if entries else "e-1",
             "authority": {"viewPrivilege": True}}]}}


class FakePermission:
    def __init__(self):
        self.clients = SimpleNamespace(finebi=FakeFineBI(), platform=FakePlatform())
        self.calls = []

    def grant(self, req):
        self.calls.append(req)
        return GrantResult("granted", req.request_id, [], {})


class ApprovalScopeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "scope.db"))
        self.permission = FakePermission()
        self.service = WebApprovalService(
            self.storage, self.permission, policy=POLICY, dry_run=False)
        self.service.catalog_rows_override = list(CATALOG)
        self.service.set_default_approver("u_manager")

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _public_request(self):
        return self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t1",
            "permissions": ["use"], "period_type": "temp", "days": 30,
        }, "public_data")

    def test_row_permission_detection(self):
        status = self.service.row_permission_status("t1", "10086")
        self.assertTrue(status["known"])
        self.assertTrue(status["configured"])
        self.assertEqual(status["counts"]["role"], 1)
        self.assertEqual(status["counts"]["department"], 1)
        self.assertEqual(status["counts"]["user"], 1)
        self.assertTrue(status["applicant_has_rule"] is False)

    def test_approver_sets_row_and_column_scope(self):
        req = self._public_request()
        updated = self.service.set_approver_scope(
            req["id"], "u_manager", row_enabled=True, row_field="t1_region",
            row_values=["华东", "华南"], field_ids=["t1_region", "t1_amount"])
        payload = updated["payload"]
        self.assertTrue(payload["row_enabled"])
        self.assertEqual(payload["data_scope"]["rules"][0]["fieldId"], "t1_region")
        self.assertEqual(payload["field_ids"], ["t1_region", "t1_amount"])
        self.assertEqual(payload["scope_configured_by"], "u_manager")
        self.assertIn("行权限", payload["permission_content"])
        self.assertIn("列权限", payload["permission_content"])

    def test_only_current_approver_can_set_scope(self):
        req = self._public_request()
        with self.assertRaises(WebApprovalError):
            self.service.set_approver_scope(
                req["id"], "u_applicant", row_enabled=False)

    def test_approver_scope_allows_free_values_and_not_in(self):
        req = self._public_request()
        updated = self.service.set_approver_scope(
            req["id"], "u_manager", row_enabled=True,
            row_field="t1_region", row_operator="strNotIn",
            row_values=["外部门店"], field_ids=[])
        rule = updated["payload"]["data_scope"]["rules"][0]
        self.assertEqual(rule["type"], "strNotIn")
        self.assertEqual(rule["filterValue"], ["外部门店"])
        self.assertIn("不属于", updated["payload"]["permission_content"])

    def test_scope_field_must_exist(self):
        req = self._public_request()
        with self.assertRaises(WebApprovalError):
            self.service.set_approver_scope(
                req["id"], "u_manager", field_ids=["not-exist"])

    def test_execute_order_data_then_row_then_field(self):
        req = self._public_request()
        self.service.set_approver_scope(
            req["id"], "u_manager", row_enabled=True, row_field="t1_region",
            row_values=["华东"], field_ids=["t1_region"])
        for step in req["steps"]:
            self.service.approve(req["id"], step["approver_id"], "同意")
        granted = self.permission.calls[-1]
        types = [item["resource_type"] for item in granted.items]
        self.assertEqual(types[0], "table")
        self.assertEqual(types[1], "row")
        self.assertEqual(types[2], "field")
        self.assertEqual(granted.items[2]["resource_id"], "t1_region")

    def test_row_values_falls_back_to_other_user_rules(self):
        """参考用户没有规则时，从其他用户的固定值规则里收集枚举。"""
        fake = self.permission.clients.finebi

        def role_rules(roles, table):
            dynamic = json.dumps({
                "filterType": 35,
                "filterValue": [{"filterType": 11, "fieldId": "t1_region",
                                 "filterValue": "role_id_REALNAME"}],
            }, ensure_ascii=False)
            return {"data": [{"status": True, "data": dynamic}
                             for _ in roles]}

        def depost_rules(subjects, table):
            return {"data": [{"status": True, "data": ""} for _ in subjects]}

        def user_rules(users, table):
            value_rule = json.dumps({
                "filterType": 10, "fieldId": "t1_region",
                "fieldName": "订单明细.大区",
                "filterValue": {"type": 1, "value": ["华东", "华南"]},
            }, ensure_ascii=False)
            return {"data": [{"status": True,
                              "data": value_rule if user == "zhangsan" else ""}
                             for user in users]}

        fake.get_row_filters_roles = role_rules
        fake.get_row_filters_deposts = depost_rules
        fake.get_row_filters_users = user_rules
        fields = self.service.row_values("t1", "10086")
        self.assertEqual([f["field_id"] for f in fields], ["t1_region"])
        self.assertEqual(fields[0]["values"], ["华东", "华南"])

    def test_membership_role_permission_summary(self):
        req = self.service.create_request("u_applicant", {
            "membership_type": "role", "targets": ["运营主管"],
            "period_type": "temp", "days": 30,
        }, "membership")
        summary = self.service.membership_permissions(req["id"])
        self.assertTrue(summary["known"])
        self.assertEqual(summary["summary"]["tables"]["use"], 1)
        self.assertGreaterEqual(summary["summary"]["dashboards"]["view"], 1)
        # 权限摘要异步加载，不阻塞申请单创建
        self.assertNotIn("entity_permissions", req["payload"])

    def test_membership_department_permission_summary(self):
        req = self.service.create_request("u_applicant", {
            "membership_type": "department",
            "targets": ['["华东区"]'],
            "period_type": "temp", "days": 30,
        }, "membership")
        summary = self.service.membership_permissions(req["id"])
        self.assertTrue(summary["known"])
        self.assertEqual(summary["entity"], "华东区")
        self.assertEqual(summary["summary"]["folders"]["use"], 1)

    def test_field_values_prefers_source_data_distinct(self):
        fake = self.permission.clients.finebi
        fake.get_tables_info = lambda tables: {"data": [{"status": True, "data": {
            "tableName": tables[0],
            "sql": "select region as '大区' from ads.demo",
            "fields": [{"fieldId": "t1_region", "name": "大区",
                        "transferName": "大区"}]}}]}

        class FakeDataClient:
            def enabled(self):
                return True

            def field_values(self, tables, field_id, field_name, limit=500):
                return ["华东", "华南", "华北"]

        self.service.data_client = FakeDataClient()
        result = self.service.field_values("t1", "t1_region")
        self.assertEqual(result["source"], "data-api")
        self.assertEqual(result["values"], ["华东", "华南", "华北"])

    def test_resources_table_excludes_folders_and_dashboards(self):
        """目录按 table 查询时不能把文件夹/仪表板当数据集。"""
        rows = self.service.resources("table", limit=100)
        self.assertEqual([r["resource_id"] for r in rows], ["t1"])

    def test_data_api_skips_folder_rows(self):
        """连接测试只探测真正的 table；文件夹不能传给 v5 数据接口。"""
        class FakeDataClient:
            def __init__(self):
                self.calls = []

            def enabled(self):
                return True

            def preview(self, table_name, page_index=1, page_size=1000):
                self.calls.append(table_name)
                return ([{"fieldId": "f1", "name": "字段"}], [])

        fake = FakeDataClient()
        self.service.data_client = fake
        self.service.catalog_rows_override = list(CATALOG) + [{
            "resource_type": "folder", "resource_id": "p-cost",
            "name": "成本+贴标+物流", "path": "A/成本+贴标+物流", "fields": []}]
        result = self.service.test_data_api()
        self.assertTrue(result["ok"], result["message"])
        self.assertNotIn("成本+贴标+物流", fake.calls)
        self.assertIn("t1", fake.calls)

    def test_dashboard_component_scope_saved_and_executed(self):
        deps_path = os.path.join(self.tmp.name, "deps.json")
        with open(deps_path, "w", encoding="utf-8") as fh:
            json.dump({"dashboards": {"d-1": {"name": "成本看板", "datasets": [
                {"resource_id": "t1", "name": "订单明细"}]}}}, fh,
                ensure_ascii=False)
        self.service.deps_json = deps_path
        req = self.service.create_request("u_applicant", {
            "resource_id": "d-1", "entry_id": "e-1",
            "resource_name": "成本看板", "permissions": ["view", "component"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        self.assertEqual([d["resource_id"] for d in
                          req["payload"]["component_datasets"]], ["t1"])
        updated = self.service.set_approver_scope(
            req["id"], "u_manager", row_enabled=True,
            row_field="t1_region", row_values=["华东"],
            field_ids=["t1_amount"], scope_table_id="t1")
        scope = updated["payload"]["component_scopes"]["t1"]
        self.assertTrue(scope["row_enabled"])
        self.assertEqual(scope["data_scope"]["rules"][0]["type"], "strIn")
        req2 = self.service.get_request(req["id"])
        result = self.service._execute_permission(req2)
        self.assertTrue(result["ok"])
        items = self.permission.calls[-1].items
        types = [item["resource_type"] for item in items]
        self.assertIn(ResourceType.ROW, types)
        self.assertIn(ResourceType.FIELD, types)
        self.assertIn("组件行/列权限",
                      self.service._permission_content("dashboard", req2["payload"]))

    def test_dashboard_lineage_maps_self_service_to_public_ancestor(self):
        deps_path = os.path.join(self.tmp.name, "dash_lineage.json")
        with open(deps_path, "w", encoding="utf-8") as fh:
            json.dump({"dashboards": {"d-1": {"name": "成本看板", "datasets": [
                {"resource_id": "self-t2", "name": "自助数据集"}]}}}, fh,
                ensure_ascii=False)
        self.service.deps_json = deps_path
        fake = self.permission.clients.finebi
        fake.get_table_usage = lambda tables: {"data": [{"status": True, "data": {
            "tableName": "self-t2", "fatherTables": [{
                "tableName": "t1", "transferName": "订单明细"}]}}]}
        req = self.service.create_request("u_applicant", {
            "resource_id": "d-1", "entry_id": "e-1",
            "resource_name": "成本看板", "permissions": ["view", "component"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        public = [d["resource_id"] for d in req["payload"]["component_datasets"]]
        self_service = [d["resource_id"] for d in
                        req["payload"]["component_self_service"]]
        self.assertEqual(public, ["t1"])
        self.assertEqual(self_service, ["self-t2"])

    def test_permission_map_marks_owned_tables(self):
        fake = self.permission.clients.finebi
        fake.get_table_permissions_user = lambda user, tables: {
            "data": [{"status": True, "data": {
                "usePrivilege": True, "managePrivilege": False,
                "empowerPrivilege": False, "biData": False, "biView": False}}
                for _ in tables]}
        result = self.service.permission_map("u_applicant", "public_data")
        self.assertTrue(result["known"])
        self.assertEqual(result["items"]["t1"]["labels"], ["使用"])

    def test_permission_map_dashboard_maps_by_entry_id(self):
        fake = self.permission.clients.finebi
        fake.get_entry_authority = lambda user, entries: {
            "data": {"entry": [
                {"entryId": "e-1", "authority": {
                    "viewPrivilege": True, "export": True}}]}}
        result = self.service.permission_map("u_applicant", "dashboard")
        self.assertTrue(result["known"])
        self.assertEqual(result["items"]["e-1"]["labels"], ["查看", "导出"])

    def test_public_request_keeps_row_operator(self):
        req = self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t1",
            "permissions": ["use"], "period_type": "temp", "days": 30,
            "row_enabled": True, "row_field": "t1_region",
            "row_operator": "strNotIn", "row_values": ["外部门店"],
        }, "public_data")
        rule = req["payload"]["data_scope"]["rules"][0]
        self.assertEqual(rule["type"], "strNotIn")
        self.assertEqual(rule["filterValue"], ["外部门店"])


@unittest.skipUnless(HAS_WEB, "需要 fastapi/httpx")
class ScopeHttpTest(unittest.TestCase):
    def setUp(self):
        from executor.config import Settings
        from executor.web.app import create_app
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="",
            finebi_secret="", db_path=os.path.join(self.tmp.name, "scope_web.db"),
            dry_run=True, policy=POLICY, web_auth_mode="dev",
            public_base_url="http://testserver", http_timeout=1)
        self.app = create_app(self.settings)
        self.service = self.app.state.service
        self.service.catalog_rows_override = list(CATALOG)
        self.service.set_default_approver("u_manager")
        # 不访问真实 FineBI
        self.service.row_permission_status = lambda table_id, fb_user="": {
            "known": True, "configured": True, "counts": {
                "role": 1, "department": 0, "user": 0},
            "subjects": {"roles": ["运营主管"], "departments": [],
                         "user_count": 0},
            "applicant_has_rule": False, "table_id": table_id,
            "table_name": "订单明细", "checked_at": "2026-11-22T21:00:00+08:00"}
        self.service.row_values = lambda table_id, sample="": [
            {"field_id": "t1_region", "name": "大区", "values": ["华东", "华南"]}]
        self.approver = TestClient(self.app)
        self.approver.post("/login", data={"user_id": "u_manager"},
                           follow_redirects=False)
        self.applicant = TestClient(self.app)
        self.applicant.post("/login", data={"user_id": "u_applicant"},
                            follow_redirects=False)

    def tearDown(self):
        try:
            self.app.state.ctx.storage.close()
        except Exception:  # noqa: BLE001
            pass
        self.tmp.cleanup()

    def _create(self):
        req = self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t1",
            "permissions": ["use"], "period_type": "temp", "days": 30,
        }, "public_data")
        return req["id"]

    def test_detail_page_shows_scope_form_for_approver(self):
        request_id = self._create()
        page = self.approver.get("/requests/%s" % request_id)
        self.assertEqual(page.status_code, 200)
        self.assertIn("行/列权限（可选，审批人补充）", page.text)
        self.assertIn("t1_region", page.text)
        # 申请人也能看详情，但没有补充配置表单
        applicant_page = self.applicant.get("/requests/%s" % request_id)
        self.assertEqual(applicant_page.status_code, 200)
        self.assertNotIn("行/列权限（可选，审批人补充）", applicant_page.text)
        outsider = TestClient(self.app)
        outsider.post("/login", data={"user_id": "u_owner"},
                      follow_redirects=False)
        self.assertEqual(outsider.get("/requests/%s" % request_id).status_code, 403)
        fields = self.applicant.get("/api/table-fields?table=t1")
        self.assertEqual(fields.status_code, 200)
        self.assertEqual([f["field_id"] for f in fields.json()["fields"]],
                         ["t1_region", "t1_amount"])
        values = self.applicant.get("/api/field-values?table=t1&field=t1_region")
        self.assertEqual(values.status_code, 200)
        self.assertIn("values", values.json())
        permission_map = self.applicant.get(
            "/api/permission-map?category=public_data")
        self.assertEqual(permission_map.status_code, 200)
        self.assertIn("items", permission_map.json())

    def test_dashboard_detail_shows_component_scope_form(self):
        deps_path = os.path.join(self.tmp.name, "dash_deps.json")
        with open(deps_path, "w", encoding="utf-8") as fh:
            json.dump({"dashboards": {"d-1": {"name": "成本看板", "datasets": [
                {"resource_id": "t1", "name": "订单明细"}]}}}, fh,
                ensure_ascii=False)
        self.service.deps_json = deps_path
        req = self.service.create_request("u_applicant", {
            "resource_id": "d-1", "entry_id": "e-1",
            "resource_name": "成本看板", "permissions": ["view", "component"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        page = self.approver.get("/requests/%s" % req["id"])
        self.assertEqual(page.status_code, 200)
        self.assertIn("连带组件数据：行/列权限", page.text)
        self.assertIn("scope_table_id", page.text)
        self.assertIn("component-scope-form", page.text)
        fields = self.approver.get(
            "/api/table-fields?request_id=%s&table_id=t1" % req["id"])
        self.assertEqual(fields.status_code, 200)
        self.assertEqual([f["field_id"] for f in fields.json()["fields"]],
                         ["t1_region", "t1_amount"])

    def test_dashboard_self_service_component_skips_scope(self):
        deps_path = os.path.join(self.tmp.name, "dash_deps2.json")
        with open(deps_path, "w", encoding="utf-8") as fh:
            json.dump({"dashboards": {"d-1": {"name": "成本看板", "datasets": [
                {"resource_id": "t1", "name": "订单明细"},
                {"resource_id": "self-t2", "name": "自助数据集"}]}}}, fh,
                ensure_ascii=False)
        self.service.deps_json = deps_path
        req = self.service.create_request("u_applicant", {
            "resource_id": "d-1", "entry_id": "e-1",
            "resource_name": "成本看板", "permissions": ["view", "component"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        page = self.approver.get("/requests/%s" % req["id"])
        self.assertIn("自助数据集（无需配置行/列权限）", page.text)
        self.assertNotIn('value="self-t2"', page.text)
        with self.assertRaises(WebApprovalError):
            self.service.set_approver_scope(
                req["id"], "u_manager", row_enabled=True,
                row_field="x", row_values=["y"], scope_table_id="self-t2")

    def test_membership_department_permission_summary(self):
        request_id = self._create()
        denied = self.applicant.get(
            "/api/row-permission-status?request_id=%s" % request_id)
        self.assertEqual(denied.status_code, 403)
        allowed = self.approver.get(
            "/api/row-permission-status?request_id=%s" % request_id)
        self.assertEqual(allowed.status_code, 200)
        self.assertTrue(allowed.json()["configured"])
        fields = self.approver.get(
            "/api/table-fields?request_id=%s" % request_id)
        self.assertEqual([f["field_id"] for f in fields.json()["fields"]],
                         ["t1_region", "t1_amount"])

        saved = self.approver.post(
            "/requests/%s/scope" % request_id,
            data={"row_enabled": "true", "row_field": "t1_region",
                  "row_values": ["华东"], "field_ids": ["t1_amount"]},
            follow_redirects=False)
        self.assertEqual(saved.status_code, 303)
        req = self.service.get_request(request_id)
        self.assertTrue(req["payload"]["row_enabled"])
        self.assertEqual(req["payload"]["field_ids"], ["t1_amount"])
        self.assertEqual(req["payload"]["data_scope"]["rules"][0]["filterValue"],
                         ["华东"])


    def test_membership_detail_loads_entity_permissions(self):
        self.service.entity_permissions = lambda membership_type, targets: {
            "known": True, "entity_type": membership_type,
            "entity": "运营主管", "checked_at": "2026-11-22T21:00:00+08:00",
            "summary": {
                "folders": {"count": 1, "use": 1, "names": ["客服部"]},
                "tables": {"count": 2, "use": 2, "component": 1,
                           "names": ["天猫客服销售日汇总表", "订单明细"]},
                "rows": {"count": 1, "names": ["订单明细"]},
                "dashboards": {"count": 1, "view": 1, "export": 0,
                               "names": ["成本看板"]},
                "entries": {"count": 1, "view": 1, "export": 0, "edit": 0},
            }}
        req = self.service.create_request("u_applicant", {
            "membership_type": "role", "targets": ["运营主管"],
            "period_type": "temp", "days": 30,
        }, "membership")
        page = self.applicant.get("/requests/%s" % req["id"])
        self.assertEqual(page.status_code, 200)
        self.assertIn("该角色/部门当前拥有的权限（辅助审批）", page.text)
        data = self.applicant.get(
            "/api/entity-permissions?request_id=%s" % req["id"])
        self.assertEqual(data.status_code, 200)
        payload = data.json()
        self.assertTrue(payload["known"])
        self.assertEqual(payload["summary"]["tables"]["use"], 2)
        outsider = TestClient(self.app)
        outsider.post("/login", data={"user_id": "u_owner"},
                      follow_redirects=False)
        self.assertEqual(outsider.get(
            "/api/entity-permissions?request_id=%s" % req["id"]).status_code, 403)


if __name__ == "__main__":
    unittest.main()
