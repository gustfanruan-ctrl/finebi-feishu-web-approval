# -*- coding: utf-8 -*-
import io
import json
import unittest
import urllib.error
from unittest import mock

from executor.errors import ApiError
from executor.http import HttpClient


class _Resp:
    def __init__(self, body):
        self._body = body.encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _http_error(code, body="{}"):
    return urllib.error.HTTPError(
        "http://example", code, "err", {}, io.BytesIO(body.encode("utf-8")))


class HttpClientTest(unittest.TestCase):
    def setUp(self):
        self.client = HttpClient(timeout=5, retries=3, backoff=0)

    def test_get_retries_on_500(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=[_http_error(500), _Resp('{"ok": true}')]) as m:
            self.assertEqual(self.client.request("GET", "http://example"), {"ok": True})
            self.assertEqual(m.call_count, 2)

    def test_post_does_not_retry_on_500(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=[_http_error(500, '{"msg": "boom"}')]) as m:
            with self.assertRaises(ApiError) as ctx:
                self.client.request("POST", "http://example", json_body={"a": 1})
            self.assertEqual(ctx.exception.status, 500)
            self.assertEqual(m.call_count, 1)

    def test_post_retries_on_429(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=[_http_error(429), _Resp('{"ok": true}')]) as m:
            self.assertEqual(self.client.request("POST", "http://example"), {"ok": True})
            self.assertEqual(m.call_count, 2)

    def test_non_json_raises(self):
        with mock.patch("urllib.request.urlopen", return_value=_Resp("not-json")):
            with self.assertRaises(ApiError) as ctx:
                self.client.request("GET", "http://example")
            self.assertEqual(ctx.exception.status, "NON_JSON")

    def test_params_encoded(self):
        with mock.patch("urllib.request.urlopen", return_value=_Resp("{}")) as m:
            self.client.request("GET", "http://example/api", params={"a": "1", "b": None})
            url = m.call_args[0][0].full_url
            self.assertIn("a=1", url)
            self.assertNotIn("b=", url)

    def test_empty_body_returns_none(self):
        with mock.patch("urllib.request.urlopen", return_value=_Resp("")):
            self.assertIsNone(self.client.request("GET", "http://example"))


if __name__ == "__main__":
    unittest.main()
