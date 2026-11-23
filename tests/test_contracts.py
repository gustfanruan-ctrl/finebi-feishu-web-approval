# -*- coding: utf-8 -*-
import json
import os
import re
import unittest

from executor.finebi.client import FineBIClient
from executor.finebi import paths

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
CLIENT_SOURCE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src", "executor", "finebi", "client.py")


def load_json(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


class FakeHttp:
    def __init__(self, response=None):
        self.response = response or {"status": 200, "data": [{"status": True, "data": "success"}]}
        self.calls = []

    def request(self, method, url, headers=None, json_body=None, params=None):
        self.calls.append({"method": method, "url": url, "body": json_body, "params": params})
        return self.response


class ContractTest(unittest.TestCase):
    def _client(self, response=None, dry_run=False):
        http = FakeHttp(response)
        return FineBIClient("http://bi.test:8075", "cid", "sec", http=http, dry_run=dry_run), http

    def test_folder_set_body_matches_doc(self):
        client, http = self._client()
        body = load_json("folder_set_request.json")
        client.set_folder_permission(body[0]["user"], body[0]["packId"], body[0]["authority"])
        self.assertEqual(http.calls[0]["method"], "POST")
        self.assertTrue(http.calls[0]["url"].endswith(paths.AUTHORITY_PACK_USER))
        self.assertEqual(http.calls[0]["body"], body)

    def test_template_auth_body_matches_doc(self):
        client, http = self._client()
        body = load_json("template_auth_set_request.json")
        client.set_dashboard_template_auth(
            body[0]["user"], body[0]["biReportId"],
            view=body[0]["authority"]["view"], export=body[0]["authority"]["export"])
        self.assertEqual(http.calls[0]["body"], body)
        self.assertTrue(http.calls[0]["url"].endswith(paths.AUTHORITY_DASH_AUTH))

    def test_folder_get_response_shape(self):
        client, _ = self._client(load_json("folder_get_response.json"))
        resp = client.get_folder_permission("10086", "pack1")
        self.assertEqual(resp["status"], 200)
        self.assertEqual(resp["data"][0]["status"], True)

    def test_publish_info_request(self):
        """entry.templateId → biReportId：GET /v3/bi/publish/info?templateIds=[...]。"""
        client, http = self._client()
        resp = client.get_publish_info(["tpl-1", "tpl-2"])
        call = http.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertTrue(call["url"].endswith(paths.PUBLISH_INFO))
        self.assertEqual(json.loads(call["params"]["templateIds"]), ["tpl-1", "tpl-2"])
        self.assertEqual(resp["status"], 200)

    def test_dry_run_blocks_write_methods_only(self):
        """dry_run 只拦写接口；查询类 POST（get_*）不能被误拦。"""
        client, http = self._client(dry_run=True)
        writes = [
            lambda: client.set_folder_permission("u", "p", {"usePrivilege": True}),
            lambda: client.set_table_permission("u", "t", {"usePrivilege": True}),
            lambda: client.set_field_permission("u", "f"),
            lambda: client.set_row_filter("u", "t", {"type": "or", "filterValue": []}),
            lambda: client.set_dashboard_template_auth("u", "d", True),
            lambda: client.set_entry_authority("u", "e", {"viewPrivilege": True}),
            lambda: client.set_publink_share("u", True),
            lambda: client.share_dashboard(["u"], "d"),
            lambda: client.set_dashboard_data_permission("u", "e"),
            lambda: client.set_subject_cooperation("u", "s"),
            lambda: client.handover_start("a", "b"),
        ]
        for call in writes:
            result = call()
            self.assertTrue(result.get("dry_run"), result)
        self.assertEqual(http.calls, [])
        reads = [
            lambda: client.get_folder_permission("u", "p"),
            lambda: client.get_table_permission("u", "t"),
            lambda: client.get_field_permission("u", "f"),
            lambda: client.get_row_filter("u", "t"),
            lambda: client.get_dashboard_template_auth("u", "d"),
            lambda: client.get_entry_authority("u", ["e"]),
        ]
        for call in reads:
            call()
        self.assertEqual(len(http.calls), len(reads))

    def test_batch_failure_raises(self):
        client, _ = self._client({"status": 200, "data": [
            {"status": True, "data": {}},
            {"status": False, "errorMsg": "user not exist"}]})
        with self.assertRaises(Exception) as ctx:
            client.get_folder_permission("u", "p")
        self.assertIn("BATCH", str(ctx.exception))

    def test_top_level_error_raises(self):
        client, _ = self._client({"status": 403, "errorCode": "403",
                                  "errorMsg": "FORBIDDEN!NO PRIVILEGE!"})
        with self.assertRaises(Exception) as ctx:
            client.list_folders()
        self.assertIn("403", str(ctx.exception))

    def test_error_code_without_status_raises(self):
        """get 类接口也可能只回 errorCode/errorMsg（无 data），同样必须抛错。"""
        client, _ = self._client({"errorCode": "E1001", "errorMsg": "user not exist"})
        with self.assertRaises(Exception) as ctx:
            client.get_folder_info(["p1"])
        self.assertIn("E1001", str(ctx.exception))

    def test_handover_start_separates_analysis_packs(self):
        client, http = self._client()
        client.handover_start("u1", "u2", pack_ids=["p1"], table_names=["t1"],
                              subject_ids=["s1"], analysis_pack_ids=["a1"])
        body = http.calls[0]["body"]
        self.assertEqual(body[0]["resourceInPublicData"],
                         {"packIds": ["p1"], "tableNames": ["t1"]})
        self.assertEqual(body[0]["resourceInUserAnalysis"],
                         {"packIds": ["a1"], "subjectIds": ["s1"]})

    def test_platform_dry_run_only_blocks_write_paths(self):
        from executor.finebi.platform import FineBIPlatformClient
        http = FakeHttp({"status": 200, "data": {"items": []}})
        client = FineBIPlatformClient("http://bi.test:8075", "cid", "sec",
                                      http=http, dry_run=True)
        # 写接口被拦截
        client.set_user_roles("u1", add=["r1"])
        self.assertEqual(http.calls, [])
        # 查询类 POST 不被误拦
        client.query_role_users(["r1"])
        self.assertEqual(len(http.calls), 1)
        self.assertTrue(http.calls[0]["url"].endswith("/v3/role/user"))

    def test_client_has_no_delete_and_paths_whitelisted(self):
        with open(CLIENT_SOURCE, "r", encoding="utf-8") as fh:
            source = fh.read()
        self.assertNotIn('_call("DELETE"', source)
        for forbidden in paths.FORBIDDEN_PATHS:
            self.assertNotIn(forbidden, source)
        used = set(re.findall(r'_call\("(?:GET|POST|PUT)",\s*"([^"]+)"', source))
        allowed = paths.READ_PATHS | paths.WRITE_PATHS
        self.assertTrue(used.issubset(allowed), "未在白名单中的路径：%s" % (used - allowed))


if __name__ == "__main__":
    unittest.main()
