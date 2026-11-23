# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from executor.services.notify import build_card
from executor.storage import Storage
from executor.web.bitable import BitableLedger, request_fields


class FakeFeishu:
    def __init__(self, fields=None):
        self.fields = fields or [{"field_id": "fld1", "field_name": "文本",
                                  "is_primary": True}]
        self.created_fields = []
        self.renamed = []
        self.records = {}
        self.updates = []

    def list_bitable_fields(self, app_token, table_id, page_size=100):
        return {"code": 0, "data": {"items": self.fields}}

    def create_bitable_field(self, app_token, table_id, field_name, field_type=1):
        self.created_fields.append(field_name)
        self.fields.append({"field_id": "f_" + field_name, "field_name": field_name})
        return {"code": 0}

    def update_bitable_field(self, app_token, table_id, field_id, field_name="",
                             field_type=1):
        self.renamed.append((field_id, field_name))
        return {"code": 0}

    def create_record(self, app_token, table_id, fields):
        record_id = "rec_%d" % (len(self.records) + 1)
        self.records[record_id] = fields
        return {"code": 0, "data": {"record": {"record_id": record_id}}}

    def update_record(self, app_token, table_id, record_id, fields):
        self.records[record_id] = fields
        self.updates.append(record_id)
        return {"code": 0}


REQUEST = {
    "id": "wreq_1", "category": "dashboard", "status": "pending",
    "created_at": "2026-11-20T10:00:00+08:00",
    "applicant": {"id": "u1", "name": "成乐乐", "fb_user": "cheng"},
    "payload": {
        "request_no": "20261120-01", "request_date": "2026-11-20",
        "serial_text": "01", "applicant_account": "cheng",
        "permission_content": "销售看板；权限：查看",
        "permission_time": "2026-11-20 至 2027-02-17（90 天）",
    },
    "steps": [{"approver": {"name": "郑嘉璇"}}],
}


class RequestFieldsTest(unittest.TestCase):
    def test_fields_mapping(self):
        fields = request_fields(REQUEST, action="提交申请", link="https://x/requests/1")
        self.assertEqual(fields["单号"], "20261120-01")
        self.assertEqual(fields["日期"], "2026-11-20")
        self.assertEqual(fields["自增键"], "01")
        self.assertEqual(fields["申请人"], "成乐乐")
        self.assertEqual(fields["申请人账号"], "cheng")
        self.assertEqual(fields["申请类型"], "仪表板")
        self.assertEqual(fields["状态"], "待审批")
        self.assertEqual(fields["审批人"], "郑嘉璇")
        self.assertEqual(fields["最近操作"], "提交申请")


class BitableLedgerTest(unittest.TestCase):
    def test_ensure_schema_renames_primary_and_creates_fields(self):
        feishu = FakeFeishu()
        ledger = BitableLedger(feishu, "app", "tbl")
        result = ledger.ensure_schema()
        self.assertTrue(result["renamed"])
        self.assertIn("日期", result["created"])
        self.assertIn(("fld1", "单号"), feishu.renamed)

    def test_upsert_create_then_update(self):
        feishu = FakeFeishu()
        ledger = BitableLedger(feishu, "app", "tbl")
        record_id = ledger.upsert(REQUEST, action="提交申请")
        self.assertTrue(record_id)
        self.assertEqual(feishu.records[record_id]["单号"], "20261120-01")
        ledger.upsert(REQUEST, record_id=record_id, action="审批通过")
        self.assertEqual(feishu.updates, [record_id])
        self.assertEqual(feishu.records[record_id]["最近操作"], "审批通过")

    def test_disabled_without_config(self):
        ledger = BitableLedger(None, "", "")
        self.assertFalse(ledger.enabled())
        self.assertEqual(ledger.upsert(REQUEST), "")


class SerialTest(unittest.TestCase):
    def test_daily_serial_increments_and_resets(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Storage(os.path.join(tmp, "x.db"))
            try:
                self.assertEqual(storage.next_request_serial("2026-11-20"), 1)
                self.assertEqual(storage.next_request_serial("2026-11-20"), 2)
                self.assertEqual(storage.next_request_serial("2026-11-21"), 1)
            finally:
                storage.close()


class CardFieldsTest(unittest.TestCase):
    def test_card_renders_fields(self):
        card = build_card("待审批", "等待审批", fields=[("日期", "2026-11-20"),
                                                       ("自增键", "01")])
        fields = card["card"]["elements"][0]["fields"]
        self.assertEqual(fields[0]["text"]["content"], "**日期**\n2026-11-20")
        self.assertEqual(fields[1]["text"]["content"], "**自增键**\n01")


if __name__ == "__main__":
    unittest.main()
