# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from executor.storage import Storage, expire_at_from_days


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "t.db"))

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_request_status(self):
        self.assertIsNone(self.storage.request_status("inst-1"))
        self.storage.upsert_request("req-1", "inst-1", "10086", {"a": 1})
        self.assertEqual(self.storage.request_status("inst-1"), "pending")
        self.storage.set_request_status("req-1", "done")
        self.assertEqual(self.storage.request_status("inst-1"), "done")

    def test_ledger_lifecycle(self):
        lid = self.storage.add_ledger("req-1", "10086", "folder", "pack1",
                                      {"authority": {"usePrivilege": True}},
                                      expire_at_from_days(-1))
        self.assertEqual(len(self.storage.active_ledger("10086")), 1)
        self.assertEqual(len(self.storage.due_ledger()), 1)
        self.storage.mark_revoked(lid, "test")
        self.assertEqual(self.storage.active_ledger("10086"), [])
        self.assertEqual(len(self.storage.due_ledger()), 0)

    def test_log(self):
        self.storage.log("INFO", "test", "hello", {"k": "v"})
        logs = self.storage.recent_logs()
        self.assertEqual(logs[0]["action"], "test")

    def test_migrations_and_p1_tables(self):
        versions = {r[0] for r in self.storage.conn.execute("SELECT version FROM schema_migrations")}
        self.assertTrue({"0001_init", "0002_p1"}.issubset(versions))
        tables = {r[0] for r in self.storage.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"request_items", "jobs", "resource_locks"}.issubset(tables))

    def test_request_items(self):
        self.storage.upsert_request("req-1", "inst-1", "10086", {"a": 1})
        ids = self.storage.add_request_items("req-1", [
            {"resource_type": "table", "resource_id": "t1", "payload": {"authority": {}}},
            {"resource_type": "row", "resource_id": "t1", "payload": {"rules": []}},
        ])
        self.assertEqual(len(ids), 2)
        self.storage.update_request_item(ids[0], "done", ledger_id="led-1")
        items = self.storage.list_request_items("req-1")
        self.assertEqual(items[0]["status"], "done")
        self.assertEqual(items[1]["status"], "pending")

    def test_jobs(self):
        job_id = self.storage.enqueue_job("retry", "req-1", expire_at_from_days(-1))
        due = self.storage.due_jobs()
        self.assertEqual(len(due), 1)
        self.storage.update_job(job_id, "manual", attempts=4, last_error="boom")
        self.assertEqual(self.storage.due_jobs(), [])


if __name__ == "__main__":
    unittest.main()
