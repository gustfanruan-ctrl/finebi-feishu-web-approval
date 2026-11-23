# -*- coding: utf-8 -*-
"""后台独立登录：密码哈希、管理员账号、前端隔离。"""
import os
import tempfile
import unittest

from executor.config import Settings
from executor.storage import Storage
from executor.web.admin_auth import (admin_configured, hash_password,
                                     verify_password)
from executor.web.service import WebApprovalService


class AdminAuthTest(unittest.TestCase):
    def test_hash_and_verify(self):
        encoded = hash_password("S3cret!")
        self.assertTrue(encoded.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password("S3cret!", encoded))
        self.assertFalse(verify_password("wrong", encoded))
        self.assertFalse(verify_password("S3cret!", ""))
        self.assertFalse(verify_password("S3cret!", "bad-format"))

    def test_admin_configured(self):
        self.assertTrue(admin_configured("admin", hash_password("x")))
        self.assertFalse(admin_configured("", hash_password("x")))
        self.assertFalse(admin_configured("admin", ""))

    def test_settings_load_admin_fields(self):
        tmp = tempfile.TemporaryDirectory()
        env = os.path.join(tmp.name, ".env")
        with open(env, "w", encoding="utf-8") as fh:
            fh.write("FINEBI_BASE_URL=http://127.0.0.1:1\n")
            fh.write("FINEBI_CLIENT_ID=cid\nFINEBI_SECRET=sec\n")
            fh.write("ADMIN_USERNAME=ops\n")
            fh.write("ADMIN_PASSWORD_HASH=%s\n" % hash_password("pw"))
        try:
            settings = Settings.load(env, os.path.join(tmp.name, "none.json"))
            self.assertEqual(settings.admin_username, "ops")
            self.assertTrue(settings.admin_password_hash)
            self.assertTrue(settings.summary()["admin_login"])
        finally:
            tmp.cleanup()


class AdminUserTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))
        self.service = WebApprovalService(self.storage, None, dry_run=True)

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_ensure_admin_user_hidden_from_user_lists(self):
        admin = self.service.ensure_admin_user("admin")
        self.assertEqual(admin["id"], "admin:admin")
        self.assertIn("admin", admin["roles"])
        self.assertEqual(self.service.list_users(), [])
        self.assertEqual(self.service.mapping_rows(), [])
        self.assertIsNotNone(self.service.get_user("admin:admin"))
