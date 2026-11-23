# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from executor.models import ResourceType
from executor.services.reconcile import ReconcileService
from executor.storage import Storage


class FakeFineBI:
    def __init__(self, folder_state=None):
        self.folder_state = folder_state or {"usePrivilege": False}
        self.entry_state = {"viewPrivilege": False, "export": False}

    def get_folder_permission(self, user, pack_id):
        return {"status": 200, "data": [{"status": True, "data": dict(self.folder_state)}]}

    def get_entry_authority(self, user, entry_ids):
        return {"status": 200, "data": {"entry": [
            {"entryId": entry_ids[0], "authority": dict(self.entry_state)}]}}


class ReconcileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "test.db"))
        self.finebi = FakeFineBI()

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def _add_ledger(self, resource_type=ResourceType.FOLDER, payload=None):
        return self.storage.add_ledger(
            "req-1", "10086", resource_type, "pack1",
            payload or {"authority": {"usePrivilege": True}}, "2099-01-01T00:00:00+08:00")

    def test_mismatch(self):
        self._add_ledger()
        service = ReconcileService(self.finebi, self.storage)
        diffs = service.run()
        self.assertEqual(diffs[0]["status"], "mismatch")

    def test_ok(self):
        self.finebi.folder_state = {"usePrivilege": True}
        self._add_ledger()
        service = ReconcileService(self.finebi, self.storage)
        self.assertEqual(service.run()[0]["status"], "ok")

    def test_unverifiable_type(self):
        self._add_ledger(ResourceType.PUBLINK, {"authority": {"biShareFun": True}})
        service = ReconcileService(self.finebi, self.storage)
        self.assertEqual(service.run()[0]["status"], "unverifiable")

    def test_row_without_map_unverifiable(self):
        self._add_ledger(ResourceType.ROW, {"rules": []})
        service = ReconcileService(self.finebi, self.storage)
        self.assertEqual(service.run()[0]["status"], "unverifiable")

    def test_dashboard_entry_mismatch_and_ok(self):
        self._add_ledger(ResourceType.DASHBOARD_ENTRY,
                         {"authority": {"viewPrivilege": True, "export": False}})
        service = ReconcileService(self.finebi, self.storage)
        self.assertEqual(service.run()[0]["status"], "mismatch")
        self.finebi.entry_state = {"viewPrivilege": True, "export": False}
        self.assertEqual(service.run()[0]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
