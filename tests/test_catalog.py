# -*- coding: utf-8 -*-
import csv
import os
import tempfile
import unittest

from executor.errors import ApiError
from executor.services.catalog import CatalogExporter


class FakeFineBI:
    """模拟 BI 开放平台：文件夹树 / pack info / table info / 仪表板 / 发布信息。"""

    def __init__(self):
        self.publish = {"tpl-1": "dash-1", "tpl-2": "dash-2"}
        self.fail_templates = set()
        self.publish_calls = []

    def list_folders(self):
        return {"status": 200, "data": [{"id": "root", "name": "公共数据", "packs": [
            {"id": "child", "name": "电商", "packs": []}]}]}

    def get_folder_info(self, packs):
        data = {
            "root": {"id": "root", "name": "公共数据",
                     "tableList": [{"name": "t1", "transferName": "订单明细"}]},
            "child": {"id": "child", "name": "电商",
                      "tableList": [{"name": "t2", "transferName": "渠道汇总"}]},
        }
        return {"status": 200,
                "data": [{"status": True, "data": data[p]} for p in packs]}

    def list_user_dashboards(self):
        return {"status": 200, "data": [
            {"biReportId": "dash-9", "biReportName": "名称兜底看板"},
            {"biReportId": "dash-keep", "biReportName": "调用方自己的看板"},
        ]}

    def get_tables_info(self, names):
        fields = {
            "t1": [{"fieldId": "t1_region", "transferName": "大区"}],
            "t2": [{"fieldId": "t2_channel", "transferName": "渠道"}],
        }
        return {"data": [{"status": True, "data": {"tableName": n, "fields": fields[n]}}
                         for n in names]}

    def get_publish_info(self, template_ids):
        self.publish_calls.append(list(template_ids))
        if any(t in self.fail_templates for t in template_ids):
            raise ApiError("BATCH", "templateId [%s] does not exist."
                           % sorted(self.fail_templates & set(template_ids))[0])
        items = []
        for template_id in template_ids:
            resources = [{"id": "comp-1", "name": "组件", "itemType": 2}]
            if template_id in self.publish:
                resources.append({"id": self.publish[template_id],
                                  "name": "仪表板", "itemType": 1})
            items.append({"status": True, "data": {
                "templateId": template_id, "resources": resources}})
        return {"status": 200, "data": items}


class FakePlatform:
    def __init__(self):
        self.tree = {"data": [
            {"id": "e1", "pId": "dir", "text": "销售看板", "entryType": 201,
             "templateId": "tpl-1", "parentNames": ["行业应用", "电商"]},
            {"id": "e2", "pId": "dir", "text": "名称兜底看板", "entryType": 201,
             "templateId": "tpl-missing", "parentNames": ["行业应用"]},
            {"id": "e3", "pId": "dir", "text": "待办看板", "entryType": 201,
             "templateId": "tpl-bad", "parentNames": []},
            {"id": "dir", "pId": "decision-directory-root", "text": "电商",
             "entryType": 3},
        ]}

    def get_entry_tree(self, device="pc"):
        return self.tree


class CatalogPublishMappingTest(unittest.TestCase):
    def setUp(self):
        self.finebi = FakeFineBI()
        self.exporter = CatalogExporter(self.finebi, FakePlatform())
        self.result = self.exporter.export()

    def _dash(self, name):
        return next(r for r in self.result["rows"]
                    if r["resource_type"] == "dashboard" and r["name"] == name)

    def test_summary(self):
        self.assertEqual(self.result["summary"],
                         {"folders": 2, "tables": 2, "dashboards": 4, "total": 8})

    def test_paths_and_fields(self):
        rows = self.result["rows"]
        table = next(r for r in rows if r["resource_id"] == "t2")
        self.assertEqual(table["path"], "公共数据/电商/渠道汇总")
        self.assertEqual(table["fields"][0]["fieldId"], "t2_channel")

    def test_template_id_resolved_by_publish_info(self):
        dash = self._dash("销售看板")
        self.assertEqual(dash["resource_id"], "dash-1")
        self.assertEqual(dash["match"], "publish/info")
        self.assertEqual(dash["parent_id"], "dir")
        self.assertEqual(dash["entry_ancestors"], ["dir"])
        self.assertEqual(dash["path"], "行业应用/电商/销售看板")

    def test_name_fallback_when_publish_info_missing(self):
        dash = self._dash("名称兜底看板")
        self.assertEqual(dash["resource_id"], "dash-9")
        self.assertEqual(dash["match"], "name")

    def test_stale_template_falls_back_to_name_or_empty(self):
        # tpl-bad 让整批 publish/info 报 BATCH，逐个重试后仍失败：条目保留、ID 留空
        self.finebi.fail_templates.add("tpl-bad")
        exporter = CatalogExporter(self.finebi, FakePlatform())
        result = exporter.export()
        bad = next(r for r in result["rows"]
                   if r["resource_type"] == "dashboard" and r["name"] == "待办看板")
        self.assertEqual(bad["resource_id"], "")
        good = next(r for r in result["rows"]
                    if r["resource_type"] == "dashboard" and r["name"] == "销售看板")
        self.assertEqual(good["resource_id"], "dash-1")
        # 批量失败后应改为逐个查询
        self.assertGreater(len(self.finebi.publish_calls), 1)
        self.assertEqual(result["summary"]["dashboards"], 4)

    def test_dash_user_all_rows_without_entry_are_kept(self):
        row = self._dash("调用方自己的看板")
        self.assertEqual(row["source"], "dash/user/all")
        self.assertEqual(row["resource_id"], "dash-keep")

    def test_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "catalog.csv")
            self.exporter.to_csv(self.result, path)
            with open(path, "r", encoding="utf-8-sig", newline="") as fh:
                rows = list(csv.reader(fh))
        self.assertEqual(rows[0][0], "资源类型")
        self.assertEqual(len(rows), 9)


class CatalogWithoutPublishApiTest(unittest.TestCase):
    """未升级客户端（没有 get_publish_info）时仍应能导出目录。"""

    def test_falls_back_to_name_match(self):
        class LegacyFineBI(FakeFineBI):
            def get_publish_info(self, template_ids):
                raise AssertionError("legacy 客户端不应调用 publish/info")

        finebi = LegacyFineBI()
        exporter = CatalogExporter(finebi, FakePlatform())
        # 模拟老客户端：方法不存在
        exporter.finebi = type("Legacy", (), {
            "list_folders": finebi.list_folders,
            "get_folder_info": finebi.get_folder_info,
            "list_user_dashboards": finebi.list_user_dashboards,
            "get_tables_info": finebi.get_tables_info,
        })()
        result = exporter.export()
        dash = next(r for r in result["rows"]
                    if r["resource_type"] == "dashboard"
                    and r["name"] == "名称兜底看板")
        self.assertEqual(dash["resource_id"], "dash-9")


if __name__ == "__main__":
    unittest.main()
