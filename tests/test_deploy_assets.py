# -*- coding: utf-8 -*-
"""部署包配置模板回归：模板里不能出现开发环境的演示用户/资源。"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEMO_MARKERS = ("Gust", "测试申请人", "测试BI管理员", "测试上级",
                "测试数据Owner", "测试数据安全", "u_applicant", "u_biadmin",
                "u_manager", "u_owner", "u_security")


class ExampleConfigTest(unittest.TestCase):
    def setUp(self):
        path = os.path.join(ROOT, "config", "config.example.json")
        with open(path, encoding="utf-8") as fh:
            self.cfg = json.load(fh)

    def test_web_approval_users_empty(self):
        wa = self.cfg.get("policy", {}).get("web_approval", {})
        self.assertEqual(wa.get("users"), [])
        self.assertEqual(wa.get("default_approver"), "")
        self.assertEqual(wa.get("default_owner"), "")

    def test_no_dev_demo_accounts(self):
        text = json.dumps(self.cfg, ensure_ascii=False)
        for marker in DEMO_MARKERS:
            self.assertNotIn(marker, text)

    def test_dev_resources_not_baked_in(self):
        self.assertEqual(self.cfg.get("resources"), {})
        self.assertEqual(self.cfg.get("templates"), {})
        form = self.cfg.get("policy", {}).get("form_mapping", {})
        self.assertEqual(form.get("resources"), {})


if __name__ == "__main__":
    unittest.main()
