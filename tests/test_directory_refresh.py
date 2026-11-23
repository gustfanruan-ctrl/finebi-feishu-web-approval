# -*- coding: utf-8 -*-
"""目录/角色/部门定时刷新：快照写入、失败保留旧版、文件锁、Web 读取快照。"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from executor.services.directory_refresh import (collect_departments,
                                                 collect_roles,
                                                 read_directory_status,
                                                 refresh_directory)
from executor.storage import Storage
from executor.web.service import WebApprovalService


class FakePlatform:
    def __init__(self):
        self.roles = ["角色A"]
        self.departments = [
            {"id": "d1", "pId": None, "name": "财务部", "type": "department"},
            {"id": "d2", "pId": "d1", "name": "财务一部", "type": "department"},
            {"id": "p1", "pId": "d1", "name": "部长", "type": "position"},
        ]

    def query_roles(self, role="", exact=False):
        return {"data": [{"name": name} for name in self.roles]}

    def query_departments(self, path):
        return {"data": list(self.departments)}


class FakeExporter:
    def __init__(self, summary=None, fail=False):
        self.summary = summary or {"folders": 1, "tables": 2, "dashboards": 3,
                                   "total": 6}
        self.fail = fail

    def export(self):
        if self.fail:
            raise RuntimeError("模拟目录导出失败")
        return {"summary": dict(self.summary), "rows": []}


class RowsExporter:
    """带数据集行的目录导出，用于验证依赖快照生成。"""

    def export(self):
        return {"summary": {"tables": 1, "dashboards": 1},
                "rows": [{"resource_type": "table", "resource_id": "t1",
                          "name": "数据集1", "path": "A/数据集1"}]}


class FakeLineageFineBI:
    def get_table_usage(self, tables):
        return {"data": [{"status": True, "data": {
            "tableName": "t1",
            "usage": [{"id": "dash-1", "name": "看板1"}],
            "sonTables": []}}]}


class DirectoryRefreshTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.platform = FakePlatform()
        self.ctx = SimpleNamespace(finebi=None, platform=self.platform)
        self.paths = {
            "catalog_json": os.path.join(self.tmp.name, "catalog.json"),
            "catalog_csv": os.path.join(self.tmp.name, "catalog.csv"),
            "membership_json": os.path.join(self.tmp.name, "membership_options.json"),
            "status_json": os.path.join(self.tmp.name, "directory_status.json"),
            "lock_path": os.path.join(self.tmp.name, ".refresh.lock"),
            "deps_json": os.path.join(self.tmp.name, "dashboard_deps.json"),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _refresh(self, exporter=None, interval_hours=6):
        return refresh_directory(self.ctx, interval_hours=interval_hours,
                                 exporter=exporter or FakeExporter(), **self.paths)

    def test_refresh_writes_catalog_membership_and_status(self):
        status = self._refresh()
        self.assertTrue(status["ok"])
        self.assertFalse(status["running"])
        self.assertEqual(status["catalog"]["summary"]["dashboards"], 3)
        self.assertEqual(status["membership"]["roles"], 1)
        self.assertEqual(status["membership"]["departments"], 2)
        with open(self.paths["catalog_json"], encoding="utf-8") as fh:
            catalog = json.load(fh)
        self.assertEqual(catalog["summary"]["tables"], 2)
        with open(self.paths["membership_json"], encoding="utf-8") as fh:
            options = json.load(fh)
        self.assertEqual([r["name"] for r in options["roles"]], ["角色A"])
        self.assertEqual([d["full_path"] for d in options["departments"]],
                         ["财务部", "财务部/财务一部"])
        saved = read_directory_status(self.paths["status_json"], 6)
        self.assertTrue(saved["ok"])
        self.assertTrue(saved["next_refresh"])

    def test_refresh_writes_dashboard_dependency_snapshot(self):
        self.ctx.finebi = FakeLineageFineBI()
        status = self._refresh(exporter=RowsExporter())
        self.assertTrue(status["ok"])
        self.assertEqual(status["dependencies"]["dashboards"], 1)
        with open(self.paths["deps_json"], encoding="utf-8") as fh:
            deps = json.load(fh)
        self.assertEqual(deps["dashboards"]["dash-1"]["name"], "看板1")
        self.assertEqual(
            deps["dashboards"]["dash-1"]["datasets"][0]["resource_id"], "t1")

    def test_new_resources_appear_after_next_refresh(self):
        self._refresh()
        self.platform.roles.append("后期新增角色")
        self.platform.departments.append(
            {"id": "d3", "pId": None, "name": "后期新增部门", "type": "department"})
        self._refresh()
        with open(self.paths["membership_json"], encoding="utf-8") as fh:
            options = json.load(fh)
        self.assertIn("后期新增角色", [r["name"] for r in options["roles"]])
        self.assertIn("后期新增部门",
                      [d["full_path"] for d in options["departments"]])

    def test_failure_keeps_previous_snapshot(self):
        first = self._refresh(FakeExporter(summary={"dashboards": 3, "tables": 2}))
        with open(self.paths["catalog_json"], encoding="utf-8") as fh:
            before = fh.read()
        status = self._refresh(FakeExporter(fail=True))
        self.assertFalse(status["ok"])
        self.assertTrue(status["errors"])
        with open(self.paths["catalog_json"], encoding="utf-8") as fh:
            self.assertEqual(fh.read(), before)
        self.assertEqual(status["last_success"], first["last_success"])

    def test_running_lock_prevents_duplicate_refresh(self):
        with open(self.paths["lock_path"], "w", encoding="utf-8") as fh:
            fh.write("other")
        status = self._refresh()
        self.assertTrue(status["running"])
        self.assertFalse(os.path.exists(self.paths["status_json"]))

    def test_next_refresh_aligns_to_six_hour_slots(self):
        from executor.services.directory_refresh import _next_refresh
        tz = timezone(timedelta(hours=8))
        self.assertEqual(_next_refresh(datetime(2026, 11, 16, 15, 45, tzinfo=tz), 6),
                         "2026-11-16T18:00:00+08:00")
        self.assertEqual(_next_refresh(datetime(2026, 11, 16, 18, 0, tzinfo=tz), 6),
                         "2026-11-17T00:00:00+08:00")

    def test_read_status_default_when_missing(self):
        status = read_directory_status(os.path.join(self.tmp.name, "none.json"), 6)
        self.assertIsNone(status["ok"])
        self.assertEqual(status["interval_hours"], 6)

    def test_collect_roles_and_departments_use_current_api_data(self):
        self.assertEqual([r["name"] for r in collect_roles(self.platform)],
                         ["角色A"])
        paths = [d["full_path"] for d in collect_departments(self.platform)]
        self.assertEqual(paths, ["财务部", "财务部/财务一部"])


class WebSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "web.db"))
        self.membership_json = os.path.join(self.tmp.name, "membership_options.json")
        self.status_json = os.path.join(self.tmp.name, "directory_status.json")
        with open(self.membership_json, "w", encoding="utf-8") as fh:
            json.dump({"roles": [{"name": "快照角色"}],
                       "departments": [{"name": "快照部门", "path": ["快照部门"],
                                        "full_path": "快照部门"}]}, fh,
                      ensure_ascii=False)
        with open(self.status_json, "w", encoding="utf-8") as fh:
            json.dump({"ok": True, "last_refresh": "2026-11-16T06:00:00+08:00",
                       "next_refresh": "2026-11-16T12:00:00+08:00",
                       "interval_hours": 6, "catalog": {}, "membership": {},
                       "errors": []}, fh)

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_membership_options_prefers_snapshot(self):
        service = WebApprovalService(
            self.storage, None, dry_run=True, platform=None,
            membership_options_path=self.membership_json,
            directory_status_path=self.status_json)
        data = service.membership_options()
        self.assertEqual([r["name"] for r in data["roles"]], ["快照角色"])
        self.assertEqual(data["source"], "snapshot")

    def test_directory_status_reads_snapshot_status(self):
        service = WebApprovalService(
            self.storage, None, dry_run=True, platform=None,
            membership_options_path=self.membership_json,
            directory_status_path=self.status_json)
        status = service.directory_status()
        self.assertTrue(status["ok"])
        self.assertEqual(status["interval_hours"], 6)
