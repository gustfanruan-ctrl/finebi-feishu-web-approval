# -*- coding: utf-8 -*-
"""飞书客户端与通知单测：token 刷新/重试、审批查询参数、IM 包装、webhook 去重。"""
import json
import threading
import time
import unittest
import urllib.parse

from executor.errors import ApiError
from executor.feishu.client import BASE_URL, FeishuClient
from executor.services.notify import Notifier, build_card


class FakeHttp:
    """固定响应 Fake：记录调用，可指定返回值或抛异常。"""

    def __init__(self, response=None):
        self.response = response if response is not None else {"code": 0, "data": {}}
        self.calls = []

    def request(self, method, url, headers=None, json_body=None, params=None):
        self.calls.append((method, url, json_body, params, headers))
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


class ScriptedHttp:
    """按顺序返回脚本化结果；元素为 dict 或 BaseException。"""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def request(self, method, url, headers=None, json_body=None, params=None):
        self.calls.append((method, url, json_body, params, dict(headers or {})))
        if not self.script:
            raise AssertionError("没有更多脚本化响应：%s %s" % (method, url))
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    def urls(self):
        return [call[1] for call in self.calls]


class FakeFeishu:
    def __init__(self):
        self.webhook_calls = []
        self.message_calls = []

    def send_webhook(self, url, card):
        self.webhook_calls.append((url, card))
        return {"code": 0}

    def send_card(self, open_id, card, receive_id_type="open_id"):
        self.message_calls.append((open_id, card))
        return {"code": 0}


def token_ok(token, expire=7200):
    return {"code": 0, "msg": "ok", "tenant_access_token": token, "expire": expire}


def token_invalid(code=99991663):
    return ApiError(400, '{"code":%d,"msg":"Invalid access token"}' % code,
                    '{"code":%d,"msg":"Invalid access token"}' % code)


class FeishuClientTest(unittest.TestCase):
    def _client(self, http):
        client = FeishuClient("cli_test", "secret_test", http=http)
        return client

    def test_tenant_token_cached_and_refreshed(self):
        http = ScriptedHttp([token_ok("t1"), token_ok("t2")])
        client = self._client(http)
        self.assertEqual(client.tenant_token(), "t1")
        self.assertEqual(client.tenant_token(), "t1")  # 缓存期内不重复请求
        self.assertEqual(client.tenant_token(force=True), "t2")
        self.assertEqual(sum(1 for url in http.urls()
                             if url.endswith("/tenant_access_token/internal")), 2)

    def test_tenant_token_expiry_uses_monotonic_clock(self):
        http = ScriptedHttp([token_ok("t1"), token_ok("t2")])
        client = self._client(http)
        client.tenant_token()
        client._token_expire_at = time.monotonic() + 30  # 剩余 <60s，应提前刷新
        self.assertEqual(client.tenant_token(), "t2")

    def test_tenant_token_empty_response_raises(self):
        http = FakeHttp({"code": 0, "msg": "ok"})
        client = self._client(http)
        with self.assertRaises(ApiError) as ctx:
            client.tenant_token()
        self.assertEqual(ctx.exception.status, "NO_TOKEN")

    def test_expired_token_retry_once_with_force_refresh(self):
        http = ScriptedHttp([
            token_ok("t1"),
            token_invalid(99991663),
            token_ok("t2"),
            {"code": 0, "data": {"items": []}},
        ])
        client = self._client(http)
        resp = client.list_contact_users(page_size=1)
        self.assertEqual(resp["code"], 0)
        target_calls = [call for call in http.calls
                        if "/contact/v3/users" in call[1]]
        self.assertEqual(len(target_calls), 2)
        self.assertEqual(target_calls[0][4]["Authorization"], "Bearer t1")
        self.assertEqual(target_calls[1][4]["Authorization"], "Bearer t2")
        token_calls = [call for call in http.calls
                       if call[1].endswith("/tenant_access_token/internal")]
        self.assertEqual(len(token_calls), 2)

    def test_token_invalid_after_refresh_is_raised(self):
        http = ScriptedHttp([token_ok("t1"), token_invalid(), token_ok("t2"),
                             token_invalid()])
        client = self._client(http)
        with self.assertRaises(ApiError):
            client.list_contact_users(page_size=1)

    def test_non_token_error_not_retried(self):
        http = ScriptedHttp([
            token_ok("t1"),
            ApiError(400, '{"code":1390002,"msg":"approval code not found"}',
                     '{"code":1390002,"msg":"approval code not found"}'),
        ])
        client = self._client(http)
        with self.assertRaises(ApiError):
            client.get_instance("FAKE")
        self.assertEqual(len(http.calls), 2)

    def test_rate_limit_retried_with_backoff(self):
        from unittest import mock
        http = ScriptedHttp([
            token_ok("t1"),
            {"code": 99991400, "msg": "request trigger frequency limit"},
            {"code": 0, "data": {"items": []}},
        ])
        client = self._client(http)
        with mock.patch("executor.feishu.client.time.sleep") as sleeper:
            resp = client.list_contact_users(page_size=1)
        self.assertEqual(resp["code"], 0)
        self.assertTrue(sleeper.called)
        target_calls = [call for call in http.calls if "/contact/v3/users" in call[1]]
        self.assertEqual(len(target_calls), 2)

    def test_rate_limit_exhausted_raises(self):
        from unittest import mock
        script = [token_ok("t1")] + [
            {"code": 99991400, "msg": "request trigger frequency limit"}
            for _ in range(6)]
        client = self._client(ScriptedHttp(script))
        with mock.patch("executor.feishu.client.time.sleep"):
            with self.assertRaises(ApiError) as ctx:
                client.list_contact_users(page_size=1)
        self.assertEqual(ctx.exception.status, 99991400)

    def test_concurrent_token_refresh_hits_api_once(self):
        class SlowTokenHttp:
            def __init__(self):
                self.calls = []
                self.lock = threading.Lock()

            def request(self, method, url, headers=None, json_body=None, params=None):
                with self.lock:
                    self.calls.append(url)
                if url.endswith("/tenant_access_token/internal"):
                    time.sleep(0.1)
                    return token_ok("shared-token")
                return {"code": 0, "data": {}}

        http = SlowTokenHttp()
        client = self._client(http)
        results = []
        barrier = threading.Barrier(2)

        def grab():
            barrier.wait()
            results.append(client.tenant_token())

        threads = [threading.Thread(target=grab) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=3)
        self.assertEqual(results, ["shared-token", "shared-token"])
        self.assertEqual(len(http.calls), 1)

    def test_query_instances_request_shape(self):
        http = FakeHttp({"code": 0, "data": {}})
        client = self._client(http)
        client._token = "tok"
        client._token_expire_at = time.monotonic() + 3600
        client.query_instances("APPROVAL-CODE", status="APPROVED",
                               start_ms=1000, end_ms=2000, page_size=20,
                               page_token="pg")
        method, url, body, params, headers = http.calls[-1]
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith("/approval/v4/instances/query"))
        self.assertEqual(body["approval_code"], "APPROVAL-CODE")
        self.assertEqual(body["instance_status"], "APPROVED")
        self.assertEqual(body["instance_start_time_from"], "1000")
        self.assertEqual(body["instance_start_time_to"], "2000")
        self.assertEqual(params["page_size"], 20)
        self.assertEqual(params["page_token"], "pg")
        self.assertEqual(headers["Authorization"], "Bearer tok")

    def test_query_instances_validates_limits(self):
        client = self._client(FakeHttp())
        client._token = "tok"
        client._token_expire_at = time.monotonic() + 3600
        with self.assertRaises(ValueError):  # page_size 超出 5~200（真实接口 99992402）
            client.query_instances("CODE", page_size=3)
        with self.assertRaises(ValueError):
            client.query_instances("CODE", page_size=201)
        with self.assertRaises(ValueError):  # 开始/结束必须同时设置
            client.query_instances("CODE", start_ms=1000)
        with self.assertRaises(ValueError):  # 跨度>30 天（真实接口 1390001）
            client.query_instances("CODE", start_ms=0, end_ms=31 * 24 * 3600 * 1000)
        with self.assertRaises(ValueError):
            client.query_instances("CODE", status="DONE")

    def test_list_instance_ids_validates_limits(self):
        client = self._client(FakeHttp({"code": 0, "data": {}}))
        client._token = "tok"
        client._token_expire_at = time.monotonic() + 3600
        client.list_instance_ids("CODE", 1000, 2000, page_size=100)
        with self.assertRaises(ValueError):
            client.list_instance_ids("CODE", 1000, 2000, page_size=0)
        with self.assertRaises(ValueError):
            client.list_instance_ids("CODE", 1000, 2000, page_size=101)
        with self.assertRaises(ValueError):
            client.list_instance_ids("CODE", 2000, 2000)
        # 文档建议≤10 小时，实测服务端不强校验：超跨度只告警不抛错
        client.list_instance_ids("CODE", 0, 20 * 3600 * 1000)

    def test_get_instance_quotes_instance_code(self):
        http = FakeHttp({"code": 0, "data": {}})
        client = self._client(http)
        client._token = "tok"
        client._token_expire_at = time.monotonic() + 3600
        client.get_instance("A/B C")
        url = http.calls[-1][1]
        self.assertTrue(url.endswith("/approval/v4/instances/"
                                     + urllib.parse.quote("A/B C", safe="")))

    def test_send_message_content_is_json_string(self):
        http = FakeHttp({"code": 0, "data": {}})
        client = self._client(http)
        client._token = "tok"
        client._token_expire_at = time.monotonic() + 3600
        client.send_message("ou_x", "interactive", {"a": 1}, receive_id_type="open_id")
        method, url, body, params, _headers = http.calls[-1]
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith("/im/v1/messages"))
        self.assertEqual(body["receive_id"], "ou_x")
        self.assertEqual(body["msg_type"], "interactive")
        self.assertEqual(json.loads(body["content"]), {"a": 1})
        self.assertEqual(params["receive_id_type"], "open_id")

    def test_send_webhook_posts_envelope_without_token(self):
        http = FakeHttp({"code": 0})
        client = FeishuClient("cli", "sec", http=http)
        payload = build_card("标题", "内容")
        client.send_webhook("https://example.test/hook", payload)
        method, url, body, params, headers = http.calls[-1]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "https://example.test/hook")
        self.assertEqual(body["msg_type"], "interactive")
        self.assertNotIn("Authorization", headers or {})
        self.assertEqual(len(http.calls), 1)  # 不请求 tenant token


class NotifyTest(unittest.TestCase):
    def test_webhook_preferred(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, webhook_url="https://example/hook", dry_run=False)
        notifier.notify_user("ou_x", "标题", "内容")
        self.assertEqual(len(feishu.webhook_calls), 1)
        self.assertEqual(feishu.webhook_calls[0][1]["msg_type"], "interactive")

    def test_open_id_fallback(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, dry_run=False)
        notifier.notify_user("ou_x", "标题", "内容")
        self.assertEqual(len(feishu.message_calls), 1)

    def test_admin_broadcast_without_webhook(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, admin_open_ids=["a", "b"], dry_run=False)
        notifier.notify_admins("告警", "内容")
        self.assertEqual([c[0] for c in feishu.message_calls], ["a", "b"])

    def test_admin_broadcast_with_webhook_sends_once(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, webhook_url="https://example/hook",
                            admin_open_ids=["a", "b"], dry_run=False)
        notifier.notify_admins("告警", "内容")
        self.assertEqual(len(feishu.webhook_calls), 1)  # 群播只发一次，不再按 admin 数重复
        self.assertEqual(feishu.message_calls, [])

    def test_notify_users_webhook_once(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, webhook_url="https://example/hook", dry_run=False)
        notifier.notify_users(["ou_a", "ou_b"], "待审批", "内容")
        self.assertEqual(len(feishu.webhook_calls), 1)

    def test_notify_users_app_messages(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, dry_run=False)
        notifier.notify_users(["ou_a", "ou_b"], "待审批", "内容")
        self.assertEqual([c[0] for c in feishu.message_calls], ["ou_a", "ou_b"])

    def test_dry_run_no_call(self):
        feishu = FakeFeishu()
        notifier = Notifier(feishu, webhook_url="https://example/hook", dry_run=True)
        notifier.notify_user("ou_x", "标题", "内容")
        self.assertEqual(feishu.webhook_calls, [])

    def test_card_shape(self):
        card = build_card("标题", "内容", link="https://example")
        self.assertEqual(card["msg_type"], "interactive")
        self.assertEqual(card["card"]["header"]["title"]["content"], "标题")
        self.assertEqual(len(card["card"]["elements"]), 2)

    def test_send_card_unwraps_webhook_envelope(self):
        http = FakeHttp({"code": 0, "data": {}})
        client = FeishuClient("app", "secret", http=http)
        client._token = "token"
        client._token_expire_at = time.monotonic() + 3600
        client.send_card("ou_x", build_card("标题", "内容"))
        body = http.calls[-1][2]
        content = json.loads(body["content"])
        self.assertNotIn("msg_type", content)
        self.assertIn("header", content)


if __name__ == "__main__":
    unittest.main()
