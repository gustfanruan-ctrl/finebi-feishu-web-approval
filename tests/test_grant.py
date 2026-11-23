# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from executor.models import PermissionRequest
from executor.services.grant import PermissionService
from executor.storage import Storage


class FakeFineBI:
    def __init__(self):
        self.calls = []
        self.folder = {}
        self.table = {}
        self.row = {}

    @staticmethod
    def _wrap(data):
        return {"data": [{"status": True, "data": data}]}

    def get_folder_permission(self, user, pack_id):
        return self._wrap(self.folder.get((user, pack_id), {}))

    def set_folder_permission(self, user, pack_id, authority):
        self.calls.append(("folder", user, pack_id, authority))
        self.folder.setdefault((user, pack_id), {}).update(authority)
        return {"ok": True}

    def get_table_permission(self, user, table_name):
        return self._wrap(self.table.get((user, table_name), {}))

    def set_table_permission(self, user, table_name, authority):
        self.calls.append(("table", user, table_name, authority))
        self.table.setdefault((user, table_name), {}).update(authority)
        return {"ok": True}

    def get_row_filter(self, user, table_name):
        return self._wrap(self.row.get((user, table_name)))

    def set_row_filter(self, user, table_name, row_filter):
        self.calls.append(("row", user, table_name, row_filter))
        self.row[(user, table_name)] = json.dumps(row_filter)
        return {"ok": True}

    def get_field_permission(self, user, field_id):
        return self._wrap({})

    def set_field_permission(self, user, field_id, bi_data=True):
        self.calls.append(("field", user, field_id, bi_data))
        return {"ok": True}


def make_request(**kwargs):
    base = dict(user="10086", resource_type="folder", resource_id="pack1",
                actions=["use"], days=90)
    base.update(kwargs)
    return PermissionRequest(**base)


class GrantServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "test.db"))
        self.finebi = FakeFineBI()
        self.service = PermissionService(self.finebi, self.storage, max_days=365)

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_grant_folder_then_idempotent(self):
        req = make_request()
        result = self.service.grant(req)
        self.assertEqual(result.status, "granted")
        authority = self.finebi.calls[0][3]
        self.assertTrue(authority["usePrivilege"])
        self.assertEqual(set(authority), {"usePrivilege", "managePrivilege", "empowerPrivilege", "biData", "biView"})
        self.assertEqual(len(self.storage.active_ledger(user="10086")), 1)

        again = self.service.grant(make_request(request_id="req-2"))
        self.assertEqual(again.status, "skipped")
        self.assertEqual(len(self.finebi.calls), 1)

    def test_row_merge(self):
        existing = {"type": "or", "filterValue": [
            {"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}]}
        self.finebi.row[("10086", "t1")] = json.dumps(existing)
        req = make_request(resource_type="row", resource_id="t1",
                           data_scope={"rules": [
                               {"type": "strIn", "fieldId": "t_region",
                                "filterValue": ["华南"]}]})
        self.service.grant(req)
        written = json.loads(self.finebi.row[("10086", "t1")])
        self.assertEqual(len(written["filterValue"]), 2)

    def test_validate_rejects_bad_days(self):
        with self.assertRaises(ValueError):
            self.service.grant(make_request(days=999))


if __name__ == "__main__":
    unittest.main()
