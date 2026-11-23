# -*- coding: utf-8 -*-
"""数据安全加固回归：资源 canonical 化、动作白名单、Owner 路径、IDOR、CSRF、dev 登录。"""
import json
import os
import tempfile
import unittest
from unittest import mock

from executor.config import Settings
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
    {"id": "u_security", "name": "安全", "roles": ["security"]},
    {"id": "u_biadmin", "name": "BI管理员", "roles": ["bi_admin", "admin"]},
]
POLICY = {"web_approval": {"users": USERS}}

CATALOG = [
    {"resource_type": "folder", "resource_id": "p-1", "name": "A",
     "path": "A"},
    {"resource_type": "table", "resource_id": "t1", "name": "订单明细",
     "path": "A/订单明细"},
    {"resource_type": "table", "resource_id": "t-secret", "name": "敏感表",
     "path": "机密/敏感表"},
    {"resource_type": "dashboard", "resource_id": "dash-1", "entry_id": "entry-1",
     "name": "成本管控分析", "path": "A/成本管控分析"},
]


class _PermissionStub:
    """create_request 不需要真实授权服务；approve 前不会调用。"""

    def grant(self, req):  # pragma: no cover - 安全测试不审批
        raise AssertionError("不应执行授权")


def _service(storage, dry_run=False, policy=None, catalog=None):
    service = WebApprovalService(storage, _PermissionStub(),
                                 policy=policy or POLICY, dry_run=dry_run)
    service.catalog_rows_override = list(CATALOG if catalog is None else catalog)
    return service


class ResourceCanonicalizationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "sec.db"))
        self.service = _service(self.storage, dry_run=False)

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_public_payload_uses_catalog_name_and_path(self):
        req = self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t1",
            "resource_name": "伪造名称", "resource_path": "伪造/路径",
            "permissions": ["use"], "period_type": "temp", "days": 30,
        }, "public_data")
        payload = req["payload"]
        self.assertEqual(payload["resource_name"], "订单明细")
        self.assertEqual(payload["resource_path"], "A/订单明细")

    def test_unknown_public_resource_rejected(self):
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "resource_type": "table", "resource_id": "t-not-exist",
                "resource_name": "伪造名称", "permissions": ["use"],
                "period_type": "temp", "days": 30,
            }, "public_data")

    def test_dashboard_pair_is_canonical(self):
        req = self.service.create_request("u_applicant", {
            "resource_id": "dash-1", "entry_id": "entry-1",
            "resource_name": "伪造看板", "resource_path": "伪造/路径",
            "permissions": ["view"], "period_type": "temp", "days": 30,
        }, "dashboard")
        payload = req["payload"]
        self.assertEqual(payload["resource_id"], "dash-1")
        self.assertEqual(payload["entry_id"], "entry-1")
        self.assertEqual(payload["resource_name"], "成本管控分析")
        self.assertEqual(payload["resource_path"], "A/成本管控分析")

    def test_dashboard_entry_mismatch_rejected(self):
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "resource_id": "dash-1", "entry_id": "entry-other",
                "permissions": ["view"], "period_type": "temp", "days": 30,
            }, "dashboard")

    def test_dashboard_entry_only_resolves_resource(self):
        req = self.service.create_request("u_applicant", {
            "entry_id": "entry-1", "permissions": ["view"],
            "period_type": "temp", "days": 30,
        }, "dashboard")
        self.assertEqual(req["payload"]["resource_id"], "dash-1")

    def test_unknown_dashboard_rejected(self):
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "resource_id": "dash-unknown", "entry_id": "entry-unknown",
                "permissions": ["view"], "period_type": "temp", "days": 30,
            }, "dashboard")


class ActionWhitelistTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "sec.db"))
        self.service = _service(self.storage, dry_run=True)

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _create(self, payload, category):
        return self.service.create_request("u_applicant", payload, category)

    def test_public_data_rejects_empower(self):
        with self.assertRaises(WebApprovalError) as ctx:
            self._create({"resource_type": "table", "resource_id": "t1",
                          "permissions": ["use", "empower"],
                          "period_type": "temp", "days": 30}, "public_data")
        self.assertIn("不支持权限项", str(ctx.exception))

    def test_dashboard_rejects_unknown_action(self):
        with self.assertRaises(WebApprovalError):
            self._create({"resource_id": "dash-1", "permissions": ["use"],
                          "period_type": "temp", "days": 30}, "dashboard")

    def test_admin_module_rejects_unknown_module(self):
        with self.assertRaises(WebApprovalError):
            self._create({"module": "decision-management-other",
                          "permissions": ["use"], "period_type": "temp",
                          "days": 30}, "admin")

    def test_admin_module_keeps_canonical_label(self):
        req = self._create({"module": "decision-management-warningcenter",
                            "resource_name": "伪造模块名",
                            "permissions": ["use"], "period_type": "temp",
                            "days": 30}, "admin")
        self.assertEqual(req["payload"]["resource_name"], "数据预警（预警中心）")

    def test_schedule_rejects_unknown_action(self):
        with self.assertRaises(WebApprovalError):
            self._create({"schedule_task": "", "permissions": ["edit"],
                          "period_type": "temp", "days": 30}, "admin")


class OwnerPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "sec.db"))
        self.service = _service(self.storage, dry_run=False)
        self.service.set_owners("folder", "机密", ["u_owner"], "data")
        self.service.set_owners("folder", "公开", ["u_manager"], "data")

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_forged_resource_path_cannot_pick_another_owner(self):
        """客户端传“公开”路径，但目录快照里 t-secret 在“机密”下 → 必须走机密 Owner。"""
        req = self.service.create_request("u_applicant", {
            "resource_type": "table", "resource_id": "t-secret",
            "resource_path": "公开", "resource_name": "普通表",
            "permissions": ["use"], "period_type": "temp", "days": 30,
        }, "public_data")
        self.assertEqual(req["payload"]["resource_path"], "机密/敏感表")
        self.assertEqual([s["approver_id"] for s in req["steps"]], ["u_owner"])


class _FakeSchedulePlatform:
    def list_schedules(self, page=1, per_page=50):
        return {"data": {"list": [
            {"id": "task-1", "name": "日报导出任务"},
        ], "hasNext": False}}


class ScheduleValidationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "sec.db"))
        self.service = WebApprovalService(
            self.storage, _PermissionStub(), policy=POLICY, dry_run=False,
            platform=_FakeSchedulePlatform())

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_known_schedule_task_uses_server_side_name(self):
        req = self.service.create_request("u_applicant", {
            "schedule_task": "task-1", "resource_name": "伪造任务名",
            "permissions": ["manage"], "period_type": "temp", "days": 30,
        }, "admin")
        self.assertEqual(req["payload"]["resource_id"], "task-1")
        self.assertEqual(req["payload"]["resource_name"], "日报导出任务")

    def test_unknown_schedule_task_rejected(self):
        with self.assertRaises(WebApprovalError):
            self.service.create_request("u_applicant", {
                "schedule_task": "task-unknown", "permissions": ["manage"],
                "period_type": "temp", "days": 30,
            }, "admin")


@unittest.skipUnless(HAS_WEB, "需要 fastapi/httpx")
class HttpHardeningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="",
            finebi_secret="", db_path=os.path.join(self.tmp.name, "web.db"),
            dry_run=True, policy={"web_approval": {"users": USERS}},
            web_auth_mode="dev", public_base_url="http://testserver",
            http_timeout=1)
        from executor.web.app import create_app
        self.app = create_app(self.settings)
        self.client = TestClient(self.app)
        self.client.post("/login", data={"user_id": "u_applicant"})

    def tearDown(self):
        try:
            self.app.state.ctx.storage.close()
        except Exception:  # noqa: BLE001
            pass
        self.tmp.cleanup()

    def _create_request(self):
        resp = self.client.post("/requests/new", data={
            "category": "public_data", "resource_type": "table",
            "resource_id": "t1", "resource_name": "订单明细",
            "permissions": ["use"], "period_type": "temp", "days": "30",
        }, follow_redirects=False)
        return resp.headers["location"].rstrip("/").split("/")[-1]

    def _login(self, user_id):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": user_id})
        return client

    def test_outsider_cannot_view_or_comment(self):
        request_id = self._create_request()
        outsider = self._login("u_security")
        self.assertEqual(outsider.get("/requests/%s" % request_id).status_code, 403)
        resp = outsider.post("/requests/%s/comment" % request_id,
                             data={"content": "越权评论"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 403)
        # 审批人仍可查看
        approver = self._login("u_biadmin")
        self.assertEqual(approver.get("/requests/%s" % request_id).status_code, 200)

    def test_row_values_requires_login(self):
        anonymous = TestClient(self.app)
        self.assertEqual(
            anonymous.get("/api/row-values?table=t1").status_code, 401)
        self.assertEqual(
            anonymous.get("/api/field-values?table=t1&field=t1_region").status_code,
            401)
        self.assertEqual(
            anonymous.get("/api/permission-map?category=public_data").status_code,
            401)

    def test_csrf_origin_rejected(self):
        evil = self.client.post("/login", data={"user_id": "u_applicant"},
                                headers={"Origin": "http://evil.example"},
                                follow_redirects=False)
        self.assertEqual(evil.status_code, 403)
        ok = self.client.post("/login", data={"user_id": "u_applicant"},
                              headers={"Origin": "http://testserver"},
                              follow_redirects=False)
        self.assertEqual(ok.status_code, 303)

    def test_strict_mode_rejects_tampered_resource(self):
        strict_settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="",
            finebi_secret="", db_path=os.path.join(self.tmp.name, "strict.db"),
            dry_run=False, policy={"web_approval": {"users": USERS}},
            web_auth_mode="dev", public_base_url="http://127.0.0.1:1",
            http_timeout=1)
        from executor.web.app import create_app
        app = create_app(strict_settings)
        try:
            client = TestClient(app)
            client.post("/login", data={"user_id": "u_applicant"})
            resp = client.post("/requests/new", data={
                "category": "public_data", "resource_type": "table",
                "resource_id": "t-not-exist", "resource_name": "伪造",
                "permissions": ["use"], "period_type": "temp", "days": "30",
            }, follow_redirects=False)
            self.assertEqual(resp.status_code, 303)
            self.assertIn("error=", resp.headers["location"])
            count = app.state.ctx.storage.conn.execute(
                "SELECT COUNT(*) FROM web_requests").fetchone()[0]
            self.assertEqual(count, 0)
        finally:
            app.state.ctx.storage.close()

    def test_dev_login_refused_in_production_config(self):
        from executor.web.app import create_app
        bad = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="",
            finebi_secret="", db_path=os.path.join(self.tmp.name, "bad.db"),
            dry_run=False, policy={"web_approval": {"users": USERS}},
            web_auth_mode="dev", public_base_url="https://prod.example.com",
            http_timeout=1)
        with self.assertRaises(RuntimeError):
            create_app(bad)


if __name__ == "__main__":
    unittest.main()
