"""极简 JSON HTTP 客户端：重试、超时、错误封装（仅标准库）。"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from .errors import ApiError

LOGGER = logging.getLogger(__name__)


class HttpClient:
    def __init__(self, timeout: int = 20, retries: int = 3, backoff: float = 0.8):
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff

    def request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                json_body: Any = None, params: Optional[Dict[str, Any]] = None,
                retry: Optional[bool] = None) -> Any:
        method = method.upper()
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(clean)
        data = None
        final_headers = {"Accept": "application/json"}
        if json_body is not None:
            data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
            final_headers["Content-Type"] = "application/json; charset=utf-8"
        if headers:
            final_headers.update(headers)

        # 非幂等方法默认不重试：POST/PUT 可能已产生副作用，重试会重复授权/重复发消息。
        # 429 是限流（请求未执行），任何方法都允许重试。
        should_retry = retry if retry is not None else method in ("GET", "HEAD", "OPTIONS")

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                req = urllib.request.Request(url, data=data, headers=final_headers, method=method)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                    return self._parse(raw)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                retryable = exc.code in (429, 500, 502, 503, 504)
                if retryable and (should_retry or exc.code == 429) and attempt < self.retries:
                    self._sleep(attempt, "HTTP %s" % exc.code)
                    continue
                raise ApiError(exc.code, body[:500], body) from exc
            except urllib.error.URLError as exc:
                last_error = exc
                if should_retry and attempt < self.retries:
                    self._sleep(attempt, str(exc.reason))
                    continue
                raise ApiError("NETWORK", str(exc.reason)) from exc
        raise ApiError("NETWORK", str(last_error or "unknown"))

    def _sleep(self, attempt: int, reason: str) -> None:
        wait = self.backoff * (2 ** (attempt - 1))
        LOGGER.warning("请求失败（%s），%.1fs 后重试（%d/%d）", reason, wait, attempt, self.retries)
        time.sleep(wait)

    @staticmethod
    def _parse(raw: str) -> Any:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ApiError("NON_JSON", "响应不是合法 JSON：%s" % raw[:200]) from exc
