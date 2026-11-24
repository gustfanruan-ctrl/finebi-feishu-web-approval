# -*- coding: utf-8 -*-
import unittest
from types import SimpleNamespace

from executor.domain.handlers import (HANDLERS, NON_VERIFIABLE, PLATFORM_MODULE,
                                       SCHEDULE, get_handler)
from executor.models import ResourceType


class FakeFineBI:
    def __init__(self):
        self.calls = []
        self.entry_authority = {}

    def set_folder_permission(self, *args):
        self.calls.append(("folder", args))
        return {"ok": True}

    def set_table_permission(self, *args):
        self.calls.append(("table", args))
        return {"ok": True}

    def set_row_filter(self, *args):
        self.calls.append(("row", args))
        return {"ok": True}

    def get_folder_permission(self, *args):
        self.calls.append(("get_folder", args))
        return {"data": []}

    def get_entry_authority(self, user, entry_ids):
        self.calls.append(("get_entry", user, tuple(entry_ids)))
        entry_id = entry_ids[0] if entry_ids else ""
        return {"status": 200, "data": {"entry": [{
            "entryId": entry_id,
            "authority": self.entry_authority.get((user, entry_id), {
                "viewPrivilege": False, "export": False,
                "editPrivilege": False, "empowerPrivilege": False})}]}}

    def set_entry_authority(self, user, entry_id, authority):
        self.calls.append(("set_entry", user, entry_id, dict(authority)))
        return {"status": 200, "data": [{"status": True}]}


class FakePlatform:
    def __init__(self):
        self.calls = []

    def set_user_roles(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return {"ok": True}

    def set_user_platform_permission(self, user, module, use=True, empower=False):
        self.calls.append(("platform_module", user, module, use, empower))
        return {"ok": True}

    def set_user_schedule_permission(self, user, schedule_task,
                                     manage=True, empower=False):
        self.calls.append(("schedule", user, schedule_task, manage, empower))
        return {"ok": True}


class HandlerRegistryTest(unittest.TestCase):
    def setUp(self):
        self.finebi = FakeFineBI()
        self.platform = FakePlatform()
        self.clients = SimpleNamespace(finebi=self.finebi, platform=self.platform)

    def test_registry_complete(self):
        expected = set(ResourceType.ALL) | {"role", SCHEDULE, PLATFORM_MODULE}
        self.assertEqual(set(HANDLERS), expected)

    def test_four_non_verifiable(self):
        self.assertEqual(NON_VERIFIABLE, {
            ResourceType.PUBLINK, ResourceType.DASH_SHARE,
            ResourceType.DASHBOARD_DATA, ResourceType.SUBJECT,
            SCHEDULE, PLATFORM_MODULE,
        })
        for resource_type in NON_VERIFIABLE:
            handler = get_handler(resource_type)
            self.assertFalse(handler.verifiable)
            self.assertIsNone(handler.read)

    def test_folder_write(self):
        handler = get_handler(ResourceType.FOLDER)
        handler.write(self.clients, "10086", "pack1", {"authority": {"usePrivilege": True}})
        self.assertEqual(self.finebi.calls[0][0], "folder")
        self.assertEqual(self.finebi.calls[0][1][2], {"usePrivilege": True})

    def test_role_write(self):
        handler = get_handler("role")
        handler.write(self.clients, "10086", "电商-渠道运营", {})
        args, kwargs = self.platform.calls[0]
        self.assertEqual(kwargs.get("add"), ["电商-渠道运营"])

    def test_role_write_keeps_existing_roles(self):
        """防御性回归：即使 FineBI 把 add 当全量列表，也不能覆盖已有角色。"""
        handler = get_handler("role")
        handler.write(self.clients, "10086", "新角色",
                      {"keep_roles": ["已有角色A", "已有角色B"]})
        args, kwargs = self.platform.calls[0]
        self.assertEqual(kwargs.get("add"),
                         ["新角色", "已有角色A", "已有角色B"])

    def test_row_write(self):
        handler = get_handler(ResourceType.ROW)
        row_filter = {"type": "or", "filterValue": []}
        handler.write(self.clients, "10086", "t1", {"filter": row_filter})
        self.assertEqual(self.finebi.calls[0][0], "row")
        self.assertEqual(self.finebi.calls[0][1][2], row_filter)

    def test_entry_read_unwraps_entry_authority(self):
        self.finebi.entry_authority[("10086", "e1")] = {
            "viewPrivilege": True, "export": False,
            "editPrivilege": False, "empowerPrivilege": False}
        handler = get_handler(ResourceType.DASHBOARD_ENTRY)
        resp = handler.read(self.clients, "10086", "e1")
        self.assertEqual(resp["data"][0]["data"]["viewPrivilege"], True)
        # 复用统一批量响应解析：first_data 能取到 authority
        self.assertEqual(self.finebi.calls[0], ("get_entry", "10086", ("e1",)))

    def test_entry_read_missing_entry_returns_empty_authority(self):
        self.finebi.get_entry_authority = lambda user, ids: {
            "status": 200, "data": {"entry": []}}
        handler = get_handler(ResourceType.DASHBOARD_ENTRY)
        resp = handler.read(self.clients, "10086", "e1")
        self.assertEqual(resp["data"][0]["data"], {})

    def test_entry_write_uses_entry_field(self):
        handler = get_handler(ResourceType.DASHBOARD_ENTRY)
        authority = {"viewPrivilege": True, "export": True,
                     "editPrivilege": False, "empowerPrivilege": False}
        handler.write(self.clients, "10086", "e1", {"authority": authority})
        self.assertEqual(self.finebi.calls[0], ("set_entry", "10086", "e1", authority))

    def test_entry_revoke_clears_all_four_fields(self):
        handler = get_handler(ResourceType.DASHBOARD_ENTRY)
        handler.revoke(self.clients, "10086", "e1", {})
        authority = self.finebi.calls[0][3]
        self.assertEqual(authority, {"viewPrivilege": False, "export": False,
                                     "editPrivilege": False, "empowerPrivilege": False})

    def test_schedule_and_platform_module_revoke(self):
        get_handler(PLATFORM_MODULE).revoke(self.clients, "10086",
                                            "decision-management-schedule", {})
        self.assertEqual(self.platform.calls[0],
                         ("platform_module", "10086", "decision-management-schedule",
                          False, False))
        get_handler(SCHEDULE).revoke(self.clients, "10086", "task-1",
                                     {"permissions": ["manage"]})
        self.assertEqual(self.platform.calls[1],
                         ("schedule", "10086", "task-1", False, False))

    def test_get_unknown(self):
        with self.assertRaises(KeyError):
            get_handler("unknown")


if __name__ == "__main__":
    unittest.main()
