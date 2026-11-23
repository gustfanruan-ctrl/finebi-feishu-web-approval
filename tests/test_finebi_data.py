"""FineBI v5 数据预览接口解析测试。"""
import unittest

from executor.finebi.data import FineBIDataClient


class FakeHttp:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, method, url, headers=None, json_body=None, params=None, retry=None):
        self.calls.append({"url": url, "body": json_body})
        return self.response


class FineBIDataClientTest(unittest.TestCase):
    def test_field_values_parses_preview_and_dedupes(self):
        response = {
            "success": True,
            "code": "200",
            "data": {
                "fields": [
                    {"id": "t1_store", "name": "店铺编码",
                     "transferName": "店铺编码"},
                ],
                "data": [["001"], ["002"], ["001"], [None]],
            },
        }
        http = FakeHttp(response)
        client = FineBIDataClient("http://finebi", "token", http=http)
        values = client.field_values(["t1"], "t1_store", "店铺编码",
                                     limit=10, max_pages=1)
        self.assertEqual(values, ["001", "002"])
        self.assertIn("/v5/api/tables/fields/page", http.calls[0]["url"])
        self.assertEqual(http.calls[0]["body"]["tableName"], "t1")

    def test_field_values_returns_empty_on_bad_response(self):
        client = FineBIDataClient("http://finebi", "token", http=FakeHttp({}))
        self.assertEqual(
            client.field_values(["t1"], "t1_store", "店铺编码", max_pages=1), [])

    def test_disabled_without_token(self):
        self.assertFalse(FineBIDataClient("http://finebi", "").enabled())


if __name__ == "__main__":
    unittest.main()
