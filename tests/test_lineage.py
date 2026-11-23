# -*- coding: utf-8 -*-
"""仪表板依赖数据集血缘：反查、递归 sonTables、自助数据集不授权、快照读写。"""
import os
import tempfile
import unittest

from executor.services.lineage import (build_dashboard_deps, dashboard_datasets,
                                       load_dashboard_deps, write_dashboard_deps)


class FakeUsageFineBI:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get_table_usage(self, table_names):
        self.calls.append(list(table_names))
        return self.response


def _item(table_name, usage=None, sons=None):
    return {"status": True, "data": {"tableName": table_name,
                                     "usage": usage or [],
                                     "sonTables": sons or []}}


TABLES = [
    {"resource_type": "table", "resource_id": "t-public-1",
     "name": "天猫客服销售日汇总表", "path": "IT部门/客服部-客服销售数据/天猫客服销售日汇总表"},
    {"resource_type": "table", "resource_id": "t-public-2",
     "name": "抖店客服销售数据日汇总表", "path": "IT部门/客服部-客服销售数据/抖店客服销售数据日汇总表"},
    {"resource_type": "folder", "resource_id": "p-1", "name": "客服部-客服销售数据",
     "path": "IT部门/客服部-客服销售数据"},
]


class LineageTest(unittest.TestCase):
    def test_builds_dashboard_to_public_datasets_with_recursive_sons(self):
        response = {"data": [
            _item("t-public-1", sons=[
                {"tableName": "son-1",
                 "usage": [{"id": "dash-1", "name": "客服销售主题分析"}],
                 "tables": [
                     {"tableName": "son-2",
                      "usage": [{"id": "dash-1", "name": "客服销售主题分析"}]},
                 ]},
            ]),
            _item("t-public-2", usage=[{"id": "dash-1", "name": "客服销售主题分析"}]),
        ]}
        finebi = FakeUsageFineBI(response)
        deps = build_dashboard_deps(finebi, TABLES)
        self.assertIsNotNone(deps)
        self.assertEqual(deps["summary"]["datasets"], 2)
        self.assertEqual(deps["summary"]["dashboards"], 1)
        datasets = dashboard_datasets(deps, "dash-1")
        self.assertEqual([d["resource_id"] for d in datasets],
                         ["t-public-1", "t-public-2"])
        # 自助数据集（son-1/son-2）只用于反查，不作为授权对象
        self.assertNotIn("son-1", [d["resource_id"] for d in datasets])
        self.assertEqual(finebi.calls, [["t-public-1", "t-public-2"]])

    def test_missing_finebi_returns_none(self):
        self.assertIsNone(build_dashboard_deps(None, TABLES))

    def test_snapshot_roundtrip(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            path = os.path.join(tmp.name, "dashboard_deps.json")
            deps = {"refreshed_at": "2026-11-20T18:00:00+08:00",
                    "summary": {"datasets": 1, "dashboards": 1},
                    "dashboards": {"dash-1": {"name": "看板", "datasets": [
                        {"resource_id": "t-1", "name": "数据集"}]}}}
            write_dashboard_deps(deps, path)
            loaded = load_dashboard_deps(path)
            self.assertEqual(loaded["summary"]["dashboards"], 1)
            self.assertEqual(dashboard_datasets(loaded, "dash-1")[0]["resource_id"],
                             "t-1")
            self.assertEqual(dashboard_datasets(loaded, "dash-x"), [])
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
