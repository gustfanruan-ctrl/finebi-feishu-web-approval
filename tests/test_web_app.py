# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest
import urllib.parse
from unittest import mock

try:
    from fastapi.testclient import TestClient
    HAS_WEB = True
except ImportError:  # pragma: no cover
    HAS_WEB = False

from executor.config import Settings
from executor.errors import ApiError
from executor.storage import Storage
from executor.web.admin_auth import hash_password
from executor.web.auth import AuthError, WebAuth
from executor.web.service import WebApprovalService

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin-test-pass"
ADMIN_HASH = hash_password(ADMIN_PASSWORD)


USERS = [
    {"id": "u_applicant", "name": "申请人", "roles": ["applicant"], "fb_user": "10086"},
    {"id": "u_manager", "name": "上级", "roles": ["manager"]},
    {"id": "u_owner", "name": "Owner", "roles": ["owner"]},
    {"id": "u_security", "name": "安全", "roles": ["security"]},
    {"id": "u_biadmin", "name": "BI管理员", "roles": ["bi_admin", "admin"]},
]


@unittest.skipUnless(HAS_WEB, "需要 fastapi/httpx")
class WebAppTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="", finebi_secret="",
            db_path=os.path.join(self.tmp.name, "web.db"), dry_run=True,
            policy={"web_approval": {"users": USERS}},
            web_auth_mode="dev", public_base_url="http://testserver", http_timeout=1,
            admin_username=ADMIN_USERNAME, admin_password_hash=ADMIN_HASH)
        from executor.web.app import create_app
        self.app = create_app(self.settings)

    def _admin_login(self, client):
        resp = client.post("/admin/login", data={
            "username": ADMIN_USERNAME, "password": ADMIN_PASSWORD,
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.headers["location"].startswith("/admin"))
        return client

    def tearDown(self):
        try:
            self.app.state.ctx.storage.close()
        except Exception:
            pass
        self.tmp.cleanup()

    def test_login_and_create_request(self):
        client = TestClient(self.app)
        resp = client.get("/login")
        self.assertEqual(resp.status_code, 200)
        resp = client.post("/login", data={"user_id": "u_applicant"},
                           follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        resp = client.post("/requests/new", data={
            "category": "public_data", "resource_type": "table",
            "resource_id": "t1", "resource_name": "订单明细",
            "permissions": ["use"], "period_type": "temp", "days": "90", "reason": "测试",
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertIn("/requests/", resp.headers["location"])

    def test_alert_module_request_and_tab(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        page = client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("数据预警权限", page.text)
        self.assertIn("decision-management-warningcenter", page.text)
        resp = client.post("/requests/new", data={
            "category": "admin", "module": "decision-management-warningcenter",
            "resource_name": "数据预警（预警中心）", "permissions": ["use"],
            "period_type": "temp", "days": "30", "reason": "测试",
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        request_id = resp.headers["location"].rstrip("/").split("/")[-1]
        row = self.app.state.ctx.storage.conn.execute(
            "SELECT payload FROM web_requests WHERE id=?", (request_id,)).fetchone()
        payload = json.loads(row["payload"])
        self.assertEqual(payload["resource_type"], "platform_module")
        self.assertEqual(payload["resource_id"], "decision-management-warningcenter")

    def test_membership_request_and_tab(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        page = client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("角色/部门申请", page.text)
        self.assertIn("role-targets", page.text)
        self.assertIn("department-targets", page.text)
        resp = client.post("/requests/new", data={
            "category": "membership", "membership_type": "role",
            "targets": ["角色A", "角色B"], "period_type": "temp",
            "days": "30", "reason": "测试",
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        request_id = resp.headers["location"].rstrip("/").split("/")[-1]
        row = self.app.state.ctx.storage.conn.execute(
            "SELECT payload, category FROM web_requests WHERE id=?",
            (request_id,)).fetchone()
        payload = json.loads(row["payload"])
        self.assertEqual(row["category"], "membership")
        self.assertEqual(payload["resource_type"], "role")
        self.assertEqual(payload["targets"], ["角色A", "角色B"])
        self.assertEqual(payload["resource_name"], "角色：角色A、角色B")

    def test_membership_options_api_returns_lists(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        resp = client.get("/api/membership-options")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("roles", data)
        self.assertIn("departments", data)
        self.assertIn("errors", data)

    def test_directory_refresh_note_rendered(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        page = client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("每 6 小时自动刷新", page.text)
        self.assertIn("directory-status-note", page.text)
        # 普通前端不再出现后台管理入口
        self.assertNotIn("后台管理", page.text)
        self.assertNotIn("admin_panel", page.text)

        admin_client = self._admin_login(TestClient(self.app))
        admin_page = admin_client.get("/admin")
        self.assertEqual(admin_page.status_code, 200)
        self.assertIn("目录与角色/部门刷新", admin_page.text)

    def test_dashboard_tree_renders_folder_pick(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        page = client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn('data-type="dashboard_folder"', page.text)
        self.assertIn("dashboard-folder-hint", page.text)

    def test_dashboard_form_passes_entry_id(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        resp = client.post("/requests/new", data={
            "category": "dashboard", "resource_id": "dash-1",
            "entry_id": "entry-1", "resource_path": "A/成本管控分析",
            "resource_name": "成本管控分析",
            "resource_type": "dashboard", "permissions": ["view"],
            "period_type": "temp", "days": "30", "reason": "测试",
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        request_id = resp.headers["location"].rstrip("/").split("/")[-1]
        row = self.app.state.ctx.storage.conn.execute(
            "SELECT payload FROM web_requests WHERE id=?", (request_id,)).fetchone()
        self.assertIsNotNone(row)
        payload = json.loads(row["payload"])
        self.assertEqual(payload["entry_id"], "entry-1")
        self.assertEqual(payload["resource_path"], "A/成本管控分析")

    def test_admin_membership_owner_save(self):
        client = self._admin_login(TestClient(self.app))
        page = client.get("/admin")
        self.assertIn("角色/部门申请审批人", page.text)
        saved = client.post("/admin/membership-owner", data={
            "owner_ref": "local:u_owner",
        }, follow_redirects=False)
        self.assertEqual(saved.status_code, 303)
        row = self.app.state.ctx.storage.conn.execute(
            "SELECT resource_type,resource_id,owner_user_id,owner_type "
            "FROM resource_owners").fetchone()
        self.assertEqual(dict(row), {
            "resource_type": "membership", "resource_id": "owner",
            "owner_user_id": "u_owner", "owner_type": "data",
        })
        page = client.get("/admin")
        self.assertIn("当前：", page.text)

    def test_admin_default_approver_save(self):
        client = self._admin_login(TestClient(self.app))
        page = client.get("/admin")
        self.assertIn("默认审批人（兜底）", page.text)
        saved = client.post("/admin/default-approver", data={
            "owner_ref": "local:u_biadmin",
        }, follow_redirects=False)
        self.assertEqual(saved.status_code, 303)
        row = self.app.state.ctx.storage.conn.execute(
            "SELECT resource_type,resource_id,owner_user_id,owner_type "
            "FROM resource_owners").fetchone()
        self.assertEqual(dict(row), {
            "resource_type": "system", "resource_id": "default_approver",
            "owner_user_id": "u_biadmin", "owner_type": "data",
        })

    def test_admin_mapping_pagination(self):
        conn = self.app.state.ctx.storage.conn
        now = "2026-01-01T00:00:00+08:00"
        for i in range(60):
            conn.execute(
                "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,"
                "active,created_at) VALUES(?,?,?,?,?,?,?,?)",
                ("fs_page_%02d" % i, "分页用户%02d" % i, "", "ou_page_%02d" % i,
                 "", '["applicant"]', 1, now))
        conn.commit()
        client = self._admin_login(TestClient(self.app))
        page1 = client.get("/admin?map_page=1")
        self.assertEqual(page1.status_code, 200)
        self.assertIn("第 1 / 2 页", page1.text)
        page2 = client.get("/admin?map_page=2")
        self.assertIn("第 2 / 2 页", page2.text)
        searched = client.get("/admin?map_q=分页用户01")
        self.assertIn("共 1 条", searched.text)

    def test_admin_owner_tree_page_and_save(self):
        client = self._admin_login(TestClient(self.app))
        page = client.get("/admin")
        self.assertEqual(page.status_code, 200)
        self.assertIn("资源 Owner 配置", page.text)
        self.assertIn("owner-tree-dashboard", page.text)
        self.assertIn("owner-tree-public", page.text)
        self.assertIn("owner-dialog", page.text)
        saved = client.post("/admin/owners", data={
            "resource_type": "dashboard_folder",
            "resource_id": "A/发布方式区别",
            "data_owner_ref": "local:u_owner",
            "business_owner_ref": "local:u_manager",
        }, follow_redirects=False)
        self.assertEqual(saved.status_code, 303)
        owners = self.app.state.ctx.storage.conn.execute(
            "SELECT resource_type,resource_id,owner_user_id,owner_type "
            "FROM resource_owners ORDER BY owner_type").fetchall()
        self.assertEqual([dict(o) for o in owners], [
            {"resource_type": "dashboard_folder", "resource_id": "A/发布方式区别",
             "owner_user_id": "u_manager", "owner_type": "business"},
            {"resource_type": "dashboard_folder", "resource_id": "A/发布方式区别",
             "owner_user_id": "u_owner", "owner_type": "data"},
        ])
        page = client.get("/admin")
        self.assertIn("数据：", page.text)
        self.assertIn("业务：", page.text)

    def test_admin_data_api_save_persists_and_encrypts(self):
        client = self._admin_login(TestClient(self.app))
        page = client.get("/admin")
        self.assertIn("FineBI 数据接口（行权限去重值）", page.text)
        saved = client.post("/admin/data-api", data={
            "username": "svc_finebi", "password": "test-secret-pass",
            "user_token": "",
        }, follow_redirects=False)
        self.assertEqual(saved.status_code, 303)
        row = self.app.state.ctx.storage.conn.execute(
            "SELECT value FROM app_settings WHERE key='finebi_data_api'"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertNotIn("test-secret-pass", row[0])
        status = self.app.state.service.data_api_status()
        self.assertTrue(status["configured"])
        self.assertEqual(status["username"], "svc_finebi")
        self.assertTrue(status["has_password"])

        # 模拟重启：同一个 DB 重新建服务，配置仍在
        from executor.web.app import create_app
        restarted = create_app(self.settings)
        status2 = restarted.state.service.data_api_status()
        self.assertEqual(status2["username"], "svc_finebi")
        self.assertTrue(status2["has_password"])

        cleared = client.post("/admin/data-api", data={"clear_all": "true"},
                              follow_redirects=False)
        self.assertEqual(cleared.status_code, 303)
        self.assertFalse(self.app.state.service.data_api_status()["configured"])

    def test_admin_login_required_and_isolated(self):
        client = TestClient(self.app)
        # 未登录访问后台 -> 登录页
        resp = client.get("/admin", follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.headers["location"].startswith("/admin/login"))
        # 飞书管理员不能进入后台（后台只认独立账号）
        client.post("/login", data={"user_id": "u_biadmin"})
        resp = client.get("/admin", follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.headers["location"].startswith("/admin/login"))
        page = client.get("/")
        self.assertNotIn("后台管理", page.text)
        # 错误密码
        resp = client.post("/admin/login", data={
            "username": ADMIN_USERNAME, "password": "wrong-password"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("用户名或密码错误", resp.text)
        # 正确登录 -> /admin
        resp = client.post("/admin/login", data={
            "username": ADMIN_USERNAME, "password": ADMIN_PASSWORD,
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertEqual(resp.headers["location"], "/admin")
        admin_page = client.get("/admin")
        self.assertEqual(admin_page.status_code, 200)
        self.assertIn("后台管理", admin_page.text)
        # 后台会话访问普通首页会被送回 /admin
        resp = client.get("/", follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertEqual(resp.headers["location"], "/admin")
        # 退出后台
        resp = client.post("/admin/logout", follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertEqual(resp.headers["location"], "/admin/login")

    def test_admin_actions_require_admin_session(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_biadmin"})
        resp = client.post("/admin/owners", data={
            "resource_type": "dashboard_folder", "resource_id": "A",
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.headers["location"].startswith("/admin/login"))
        resp = client.get("/api/contacts")
        self.assertEqual(resp.status_code, 403)

    def test_contacts_api_requires_admin(self):
        client = TestClient(self.app)
        client.post("/login", data={"user_id": "u_applicant"})
        resp = client.get("/api/contacts")
        self.assertEqual(resp.status_code, 403)

    def test_contacts_api_prefers_local_mapped_users(self):
        from unittest import mock
        from executor.feishu import FeishuClient
        conn = self.app.state.ctx.storage.conn
        conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,"
            "created_at) VALUES(?,?,?,?,?,?,?,?)",
            ("fs_ou_local", "本地飞书用户", "local@example.com", "ou_local", "10086",
             '["applicant"]', 1, "2026-01-01T00:00:00+08:00"))
        conn.commit()
        client = self._admin_login(TestClient(self.app))
        with mock.patch.object(FeishuClient, "list_contact_users",
                               side_effect=AssertionError("不应实时拉通讯录")):
            resp = client.get("/api/contacts")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([it["ref"] for it in resp.json()["items"]],
                         ["feishu:ou_local"])

    def test_admin_owner_save_with_local_mapped_feishu_user(self):
        from unittest import mock
        from executor.feishu import FeishuClient
        conn = self.app.state.ctx.storage.conn
        conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,fb_user,roles,active,"
            "created_at) VALUES(?,?,?,?,?,?,?,?)",
            ("fs_ou_local", "本地飞书用户", "local@example.com", "ou_local", "10086",
             '["applicant"]', 1, "2026-01-01T00:00:00+08:00"))
        conn.commit()
        client = self._admin_login(TestClient(self.app))
        with mock.patch.object(FeishuClient, "list_contact_users",
                               side_effect=AssertionError("不应实时拉通讯录")):
            resp = client.post("/admin/owners", data={
                "resource_type": "dashboard_folder", "resource_id": "A",
                "data_owner_ref": "feishu:ou_local"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        row = conn.execute(
            "SELECT owner_user_id FROM resource_owners "
            "WHERE resource_type='dashboard_folder' AND resource_id='A'").fetchone()
        self.assertEqual(row["owner_user_id"], "fs_ou_local")

    def test_owner_from_feishu_contact_without_bi_account(self):
        class FakeFeishu:
            def list_contact_users(self, page_size=50, page_token="",
                                   department_id="0", user_id_type="open_id"):
                return {"data": {"items": [{
                    "open_id": "ou_test_owner", "name": "飞书Owner",
                    "user_id": "uid-test-owner"}], "has_more": False}}

            def list_departments(self, parent_department_id="0", fetch_child=True,
                                 page_size=50, page_token=""):
                return {"data": {"items": [], "has_more": False}}

        self.app.state.ctx.feishu = FakeFeishu()
        client = self._admin_login(TestClient(self.app))
        resp = client.post("/admin/owners", data={
            "resource_type": "dashboard_folder",
            "resource_id": "A/发布方式区别",
            "data_owner_ref": "feishu:ou_test_owner",
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        owner = self.app.state.ctx.storage.conn.execute(
            "SELECT owner_user_id,owner_type FROM resource_owners").fetchone()
        self.assertEqual(owner["owner_user_id"], "fs_ou_test_owner")
        self.assertEqual(owner["owner_type"], "data")
        user = self.app.state.ctx.storage.conn.execute(
            "SELECT name,feishu_open_id,feishu_user_id,fb_user FROM web_users WHERE id=?",
            ("fs_ou_test_owner",)).fetchone()
        self.assertEqual(user["name"], "飞书Owner")
        self.assertEqual(user["feishu_open_id"], "ou_test_owner")
        self.assertEqual(user["feishu_user_id"], "uid-test-owner")
        # 没有 FineBI 账号也能当 Owner/审批人
        self.assertEqual(user["fb_user"], "")

    def test_detail_and_reject(self):
        applicant = TestClient(self.app)
        applicant.post("/login", data={"user_id": "u_applicant"})
        resp = applicant.post("/requests/new", data={
            "category": "public_data", "resource_type": "table",
            "resource_id": "t1", "resource_name": "订单明细",
            "permissions": ["use"], "period_type": "temp", "days": "90", "reason": "测试",
        }, follow_redirects=False)
        request_id = resp.headers["location"].rstrip("/").split("/")[-1]
        # 未配置 Owner 时回退到管理员审批
        approver = TestClient(self.app)
        approver.post("/login", data={"user_id": "u_biadmin"})
        detail = approver.get("/requests/%s" % request_id)
        self.assertEqual(detail.status_code, 200)
        rejected = approver.post("/requests/%s/reject" % request_id,
                                 data={"comment": "资料不足"}, follow_redirects=False)
        self.assertEqual(rejected.status_code, 303)
        final = applicant.get("/requests/%s" % request_id)
        self.assertIn("已驳回", final.text)


class ScriptedHttp:
    """按顺序返回 OAuth 各步骤响应（dict 或异常）。"""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def request(self, method, url, headers=None, json_body=None, params=None):
        self.calls.append({"method": method, "url": url, "headers": headers or {},
                           "body": json_body})
        if not self.script:
            raise AssertionError("没有更多脚本化响应：%s" % url)
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class SyncUsersRouteTest(unittest.TestCase):
    """后台同步：FineDB 映射为空时也要从飞书通讯录拉用户。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="", finebi_secret="",
            db_path=os.path.join(self.tmp.name, "web.db"), dry_run=True,
            policy={}, web_auth_mode="dev", public_base_url="http://testserver",
            http_timeout=1, admin_username=ADMIN_USERNAME,
            admin_password_hash=ADMIN_HASH)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _contacts():
        return {"data": {"items": [
            {"open_id": "ou_test1", "name": "张三", "mobile": "13800000000",
             "email": "zhangsan@example.com"}], "has_more": False}}

    def _login(self, client):
        return client.post("/admin/login", data={
            "username": ADMIN_USERNAME, "password": ADMIN_PASSWORD,
        }, follow_redirects=False)

    def _location(self, resp):
        return urllib.parse.unquote(resp.headers["location"])

    @staticmethod
    def _no_departments():
        return {"data": {"items": [], "has_more": False}}

    def test_sync_pulls_feishu_contacts(self):
        from executor.feishu import FeishuClient
        from executor.web.app import create_app
        from executor.web.service import WebApprovalService

        with mock.patch.object(FeishuClient, "list_contact_users",
                               return_value=self._contacts()), \
                mock.patch.object(FeishuClient, "list_departments",
                                  return_value=self._no_departments()), \
                mock.patch.object(WebApprovalService, "resolve_fb_user",
                                  return_value=""):
            app = create_app(self.settings)
            try:
                client = TestClient(app)
                self.assertEqual(self._login(client).status_code, 303)
                resp = client.post("/admin/sync-users", follow_redirects=False)
                self.assertEqual(resp.status_code, 303)
                self.assertIn("同步飞书用户 1 个", self._location(resp))
                rows = app.state.ctx.storage.conn.execute(
                    "SELECT id, feishu_open_id FROM web_users "
                    "WHERE id NOT LIKE 'admin:%'").fetchall()
                self.assertEqual([(r["id"], r["feishu_open_id"]) for r in rows],
                                 [("fs_ou_test1", "ou_test1")])
            finally:
                app.state.ctx.storage.close()

    def test_sync_includes_department_users(self):
        from executor.feishu import FeishuClient
        from executor.web.app import create_app
        from executor.web.service import WebApprovalService

        def dept_users(department_id, page_size=50, page_token=""):
            if department_id == "od_1":
                return {"data": {"items": [{"open_id": "ou_dept1", "name": "李四"}],
                                 "has_more": False}}
            return {"data": {"items": [], "has_more": False}}

        with mock.patch.object(FeishuClient, "list_contact_users",
                               return_value=self._contacts()), \
                mock.patch.object(
                    FeishuClient, "list_departments",
                    return_value={"data": {
                        "items": [{"open_department_id": "od_1"}],
                        "has_more": False}}), \
                mock.patch.object(FeishuClient, "list_department_users",
                                  side_effect=dept_users), \
                mock.patch.object(WebApprovalService, "resolve_fb_user",
                                  return_value=""):
            app = create_app(self.settings)
            try:
                client = TestClient(app)
                self.assertEqual(self._login(client).status_code, 303)
                resp = client.post("/admin/sync-users", follow_redirects=False)
                self.assertEqual(resp.status_code, 303)
                self.assertIn("同步飞书用户 2 个", self._location(resp))
                rows = app.state.ctx.storage.conn.execute(
                    "SELECT id FROM web_users WHERE id NOT LIKE 'admin:%'"
                ).fetchall()
                self.assertEqual(sorted(r["id"] for r in rows),
                                 ["fs_ou_dept1", "fs_ou_test1"])
            finally:
                app.state.ctx.storage.close()

    def test_sync_falls_back_to_feishu_when_finedb_mapping_empty(self):
        from executor.feishu import FeishuClient
        from executor.web import app as web_app
        from executor.web.service import WebApprovalService

        class _EmptyFineDB:
            def __init__(self, *args, **kwargs):
                pass

            def enabled(self):
                return True

            def feishu_mapping(self):
                return []

        with mock.patch.object(web_app, "FineDB", _EmptyFineDB), \
                mock.patch.object(FeishuClient, "list_contact_users",
                                  return_value=self._contacts()), \
                mock.patch.object(FeishuClient, "list_departments",
                                  return_value=self._no_departments()), \
                mock.patch.object(WebApprovalService, "resolve_fb_user",
                                  return_value=""):
            app = web_app.create_app(self.settings)
            try:
                client = TestClient(app)
                self.assertEqual(self._login(client).status_code, 303)
                resp = client.post("/admin/sync-users", follow_redirects=False)
                self.assertEqual(resp.status_code, 303)
                self.assertIn("同步飞书用户 1 个", self._location(resp))
                count = app.state.ctx.storage.conn.execute(
                    "SELECT COUNT(*) FROM web_users WHERE id='fs_ou_test1'"
                ).fetchone()[0]
                self.assertEqual(count, 1)
            finally:
                app.state.ctx.storage.close()


class WebAuthTest(unittest.TestCase):
    """飞书 OAuth：state 防伪、回调字段、错误处理（不联网）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "auth.db"))
        self.settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="", finebi_secret="",
            db_path=os.path.join(self.tmp.name, "auth.db"), dry_run=True,
            policy={"web_approval": {"users": []}}, web_auth_mode="feishu",
            public_base_url="https://example.test", http_timeout=1,
            feishu_app_id="cli_test", feishu_app_secret="secret_test")
        self.service = WebApprovalService(self.storage, None, policy=self.settings.policy)

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _auth(self, script):
        return WebAuth(self.settings, self.service, http=ScriptedHttp(script))

    @staticmethod
    def _ok_script(open_id="ou_test", user_id="u1"):
        return [
            {"code": 0, "app_access_token": "app-token", "expire": 7200},
            {"code": 0, "data": {"access_token": "user-token", "token_type": "Bearer"}},
            {"code": 0, "data": {"open_id": open_id, "user_id": user_id,
                                 "name": "测试用户", "email": "t@example.com"}},
        ]

    def test_state_roundtrip_and_tamper(self):
        auth = self._auth([])
        state = auth.create_state()
        auth.verify_state(state)  # 合法 state 不抛错
        with self.assertRaises(AuthError):
            auth.verify_state(state + "x")
        with self.assertRaises(AuthError):
            auth.verify_state("bad-state")
        with self.assertRaises(AuthError):
            auth.verify_state(state, ttl=-1)  # 已过期

    def test_authorize_url_contains_signed_state(self):
        auth = self._auth([])
        url = auth.authorize_url()
        self.assertIn("app_id=cli_test", url)
        self.assertIn("state=", url)
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(url).query)
        auth.verify_state(query["state"][0])

    def test_authorize_url_includes_configured_scope(self):
        self.settings.feishu_oauth_scope = (
            "contact:user.phone:readonly contact:user.email:readonly")
        auth = self._auth([])
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(auth.authorize_url()).query)
        self.assertEqual(query["scope"][0],
                         "contact:user.phone:readonly contact:user.email:readonly")

    def test_callback_creates_user_with_open_id_mapping(self):
        auth = self._auth(self._ok_script())
        user = auth.handle_callback("code-1")
        self.assertEqual(user["id"], "fs_ou_test")
        self.assertEqual(user["feishu_open_id"], "ou_test")
        self.assertEqual(user["feishu_user_id"], "u1")
        self.assertEqual(user["fb_user"], "ou_test")  # 无 FineDB 映射时用 open_id 占位
        self.assertEqual(len(self.storage.conn.execute(
            "SELECT * FROM web_users").fetchall()), 1)

    def test_callback_verifies_state_when_provided(self):
        state = self._auth([]).create_state()
        with self.assertRaises(AuthError):
            self._auth([]).handle_callback("code-1", state="tampered")
        # 合法 state 会继续走 OAuth：网络错误仍以 AuthError 返回，而不是 state 校验失败
        auth = self._auth([ApiError(500, "boom")])
        with self.assertRaises(AuthError) as ctx:
            auth.handle_callback("code-1", state=state)
        self.assertIn("飞书 OAuth", str(ctx.exception))

    def test_callback_wraps_transport_error_as_auth_error(self):
        auth = self._auth([ApiError(500, "boom")])
        with self.assertRaises(AuthError) as ctx:
            auth.handle_callback("code-1")
        self.assertIn("飞书 OAuth", str(ctx.exception))

    def test_app_token_error_redacts_response(self):
        auth = self._auth([{"code": 99991, "msg": "invalid app_id",
                            "app_access_token": "SHOULD_NOT_LEAK"}])
        with self.assertRaises(AuthError) as ctx:
            auth.handle_callback("code-1")
        message = str(ctx.exception)
        self.assertIn("code=99991", message)
        self.assertNotIn("SHOULD_NOT_LEAK", message)

    def test_token_exchange_error_raises(self):
        auth = self._auth([
            {"code": 0, "app_access_token": "app-token"},
            {"code": 20003, "msg": "invalid code"},
        ])
        with self.assertRaises(AuthError) as ctx:
            auth.handle_callback("bad-code")
        self.assertIn("code=20003", str(ctx.exception))

    def test_user_info_without_open_id_raises(self):
        auth = self._auth([
            {"code": 0, "app_access_token": "app-token"},
            {"code": 0, "data": {"access_token": "user-token"}},
            {"code": 0, "data": {"user_id": "u1", "name": "只有 user_id"}},
        ])
        with self.assertRaises(AuthError) as ctx:
            auth.handle_callback("code-1")
        self.assertIn("open_id", str(ctx.exception))
        self.assertEqual(self.storage.conn.execute(
            "SELECT COUNT(*) FROM web_users").fetchone()[0], 0)


@unittest.skipUnless(HAS_WEB, "需要 fastapi/httpx")
class OAuthStateRouteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.settings = Settings(
            finebi_base_url="http://127.0.0.1:1", finebi_client_id="", finebi_secret="",
            db_path=os.path.join(self.tmp.name, "web.db"), dry_run=True,
            policy={"web_approval": {"users": USERS}},
            web_auth_mode="feishu", public_base_url="http://testserver",
            feishu_app_id="app-id", feishu_app_secret="app-secret", http_timeout=1)
        from executor.web.app import create_app
        self.app = create_app(self.settings)

    def tearDown(self):
        try:
            self.app.state.ctx.storage.close()
        except Exception:
            pass
        self.tmp.cleanup()

    def test_login_redirects_with_signed_state(self):
        client = TestClient(self.app)
        resp = client.get("/login", follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertIn("state=", resp.headers["location"])

    def test_callback_without_state_is_rejected(self):
        client = TestClient(self.app)
        resp = client.get("/auth/feishu/callback", params={"code": "x"},
                          follow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertIn("error=", resp.headers["location"])


if __name__ == "__main__":
    unittest.main()
