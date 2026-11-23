# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from executor.web.contacts import collect_contact_users, write_status


class _PagedFeishu:
    def __init__(self, root_pages, departments, dept_users):
        self.root_pages = root_pages
        self.departments = departments
        self.dept_users = dept_users

    def list_contact_users(self, page_size=50, page_token="", department_id="0",
                           user_id_type="open_id"):
        index = int(page_token or "0")
        items = self.root_pages[index]
        has_more = index + 1 < len(self.root_pages)
        return {"data": {"items": items, "has_more": has_more,
                         "page_token": str(index + 1) if has_more else ""}}

    def list_departments(self, parent_department_id="0", fetch_child=True,
                         page_size=50, page_token=""):
        return {"data": {"items": self.departments, "has_more": False}}

    def list_department_users(self, department_id, page_size=50, page_token=""):
        return {"data": {"items": self.dept_users.get(department_id, []),
                         "has_more": False}}


class CollectContactUsersTest(unittest.TestCase):
    def test_root_pagination_departments_and_dedupe(self):
        feishu = _PagedFeishu(
            root_pages=[
                [{"open_id": "ou_1", "name": "甲"}],
                [{"open_id": "ou_2", "name": "乙"}],
            ],
            departments=[{"open_department_id": "od_1"}],
            dept_users={"od_1": [{"open_id": "ou_2", "name": "乙"},
                                 {"open_id": "ou_3", "name": "丙"}]})
        items, stats = collect_contact_users(feishu, page_delay=0)
        self.assertEqual([it["open_id"] for it in items], ["ou_1", "ou_2", "ou_3"])
        self.assertEqual(stats["root"], 2)
        self.assertEqual(stats["departments"], 1)
        self.assertEqual(stats["department_users"], 1)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["dept_error"], "")

    def test_department_failure_keeps_root_users(self):
        class BrokenDepartments(_PagedFeishu):
            def list_departments(self, *args, **kwargs):
                raise RuntimeError("no dept authority")

        feishu = BrokenDepartments(
            root_pages=[[{"open_id": "ou_1", "name": "甲"}]],
            departments=[{"open_department_id": "od_1"}],
            dept_users={})
        items, stats = collect_contact_users(feishu, page_delay=0)
        self.assertEqual(len(items), 1)
        self.assertIn("no dept authority", stats["dept_error"])


class WriteStatusTest(unittest.TestCase):
    def test_write_status_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data", "contacts_status.json")
            write_status(path, ok=True, total=10, synced=9,
                         stats={"departments": 2})
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        self.assertTrue(data["ok"])
        self.assertEqual(data["total"], 10)
        self.assertEqual(data["synced"], 9)
        self.assertTrue(data["last_refresh"])


class CliParserTest(unittest.TestCase):
    def test_sync_contacts_subcommand(self):
        from executor.cli import build_parser
        args = build_parser().parse_args(["sync-contacts"])
        self.assertEqual(args.command, "sync-contacts")
        self.assertEqual(args.status_json, "data/contacts_status.json")

    def test_sync_membership_subcommand(self):
        from executor.cli import build_parser
        args = build_parser().parse_args(["sync-membership"])
        self.assertEqual(args.command, "sync-membership")
        self.assertEqual(args.status_json, "data/membership_sync_status.json")


if __name__ == "__main__":
    unittest.main()
