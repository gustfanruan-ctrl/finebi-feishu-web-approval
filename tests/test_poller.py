# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from executor.models import GrantResult, PermissionRequest
from executor.services.poller import ApprovalPoller
from executor.storage import Storage


class _FakeFeishu:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []
        self.detail_calls = []

    def query_instances(self, approval_code, status="APPROVED", start_ms=None,
                        end_ms=None, page_size=100, page_token=""):
        self.calls.append({"page_token": page_token, "page_size": page_size})
        return self.pages.pop(0)

    def get_instance(self, code, locale="zh-CN"):
        self.detail_calls.append(code)
        return {"data": {"code": code, "status": "APPROVED"}}


class _FakeMapper:
    def parse_instance(self, data, require_approved=True):
        return PermissionRequest(user="10086", resource_type="folder",
                                 resource_id="p-001", actions=["use"],
                                 days=90, source=data.get("code"))


class _FakePermission:
    def __init__(self):
        self.calls = []

    def grant(self, req):
        self.calls.append(req)
        return GrantResult("granted", req.request_id, ["led-1"], {})


class PollerPaginationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "poller.db"))

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()

    def test_pagination_fetches_all_pages(self):
        feishu = _FakeFeishu([
            {"data": {"instance_list": [{"instance": {"code": "I1"}}],
                      "has_more": True, "page_token": "t1"}},
            {"data": {"instance_list": [{"instance": {"code": "I2"}}],
                      "has_more": False, "page_token": ""}},
        ])
        permission = _FakePermission()
        poller = ApprovalPoller(feishu, permission, self.storage,
                                approval_code="code", mapper=_FakeMapper(),
                                page_size=100)
        summary = poller.run_once()
        self.assertEqual(summary["found"], 2)
        self.assertEqual(summary["granted"], 2)
        self.assertEqual([c["page_token"] for c in feishu.calls], ["", "t1"])
        self.assertEqual(feishu.detail_calls, ["I1", "I2"])
        self.assertEqual(len(permission.calls), 2)

    def test_single_page_stops(self):
        feishu = _FakeFeishu([
            {"data": {"instance_list": [{"instance": {"code": "I1"}}],
                      "has_more": False, "page_token": ""}},
        ])
        poller = ApprovalPoller(feishu, _FakePermission(), self.storage,
                                approval_code="code", mapper=_FakeMapper())
        summary = poller.run_once()
        self.assertEqual(summary["found"], 1)
        self.assertEqual(len(feishu.calls), 1)


if __name__ == "__main__":
    unittest.main()
