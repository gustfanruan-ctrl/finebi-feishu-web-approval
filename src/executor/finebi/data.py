"""FineBI 数据表预览接口（v5）。

v5 接口需要 FineBI 登录用户的 token（`fine_auth_token`），不是 OpenAPI 的
clientId/secret。支持两种配置：
- ``FINEBI_USER_TOKEN``：直接配置已有 token（适合临时联调）；
- ``FINEBI_API_USERNAME / FINEBI_API_PASSWORD``：服务账号自动登录并刷新 token。
"""
from __future__ import annotations

import base64
import http.cookiejar
import json
import logging
import re
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from ..errors import ApiError
from ..http import HttpClient

LOGGER = logging.getLogger(__name__)
API_PATH = "/webroot/decision/v5/api/tables/fields/page"
LOGIN_PATH = "/webroot/decision/login"


def _parse_json_body(resp: Any) -> Dict[str, Any]:
    if isinstance(resp, dict):
        return resp
    if not isinstance(resp, str):
        return {}
    text = resp.strip()
    match = re.match(r"^[A-Za-z_$][\w$]*\((.*)\)\s*;?\s*$", text, re.S)
    if match:
        text = match.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _batch_item(resp: Dict[str, Any]) -> Dict[str, Any]:
    """兼容 callback({success, data:{...}}) 和 data 为单条对象。"""
    data = resp.get("data")
    if isinstance(data, list) and data:
        data = data[0]
        if isinstance(data, dict) and "data" in data:
            data = data.get("data")
    if isinstance(data, dict):
        return data
    return {}


class FineBIDataClient:
    def __init__(self, base_url: str, user_token: str = "",
                 username: str = "", password: str = "",
                 http: Optional[HttpClient] = None):
        self.base_url = str(base_url or "").rstrip("/")
        self.user_token = str(user_token or "").strip().strip('"')
        self.username = str(username or "").strip()
        self.password = str(password or "")
        self.http = http or HttpClient()
        self._token = ""
        self._token_at = 0.0
        self._token_ttl = 1800
        self._cookie_header = ""
        self.last_page_info: Dict[str, Any] = {}
        self.last_scan: Dict[str, Any] = {}

    def enabled(self) -> bool:
        return bool(self.base_url and (
            self.user_token or (self.username and self.password)))

    def _extract_system(self, html: str) -> Dict[str, Any]:
        match = re.search(r"Dec\.system = JSON\.parse\('(.*?)'\);", html, re.S)
        if not match:
            return {}
        raw = match.group(1).replace("\\/", "/").replace("\\'", "'")
        for candidate in (raw, raw.replace('\\"', '"')):
            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue
        return {}

    def _login(self) -> str:
        if not (self.username and self.password):
            return ""
        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar))
        with opener.open(self.base_url + LOGIN_PATH,
                         timeout=self.http.timeout) as resp:
            html = resp.read().decode("utf-8", "replace")
        system = self._extract_system(html)
        key_text = str(system.get("encryptionKey") or "").replace("\\n", "\n")
        if not key_text:
            raise ApiError("FINEBI_LOGIN", "FineBI 登录页未返回加密公钥")
        if "BEGIN" in key_text:
            public_key = serialization.load_pem_public_key(key_text.encode())
        else:
            public_key = serialization.load_der_public_key(
                base64.b64decode(key_text))
        encrypted = public_key.encrypt(self.password.encode("utf-8"),
                                       padding.PKCS1v15())
        body = {
            "username": self.username,
            "password": base64.b64encode(encrypted).decode(),
            "validity": 0,
            "origin": "",
            "encrypted": True,
        }
        request = urllib.request.Request(
            self.base_url + LOGIN_PATH,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8",
                     "Accept": "application/json",
                     "transEncryptLevel": "1",
                     "X-Requested-With": "XMLHttpRequest"},
            method="POST")
        with opener.open(request, timeout=self.http.timeout) as resp:
            text = resp.read().decode("utf-8", "replace")
        parsed = _parse_json_body(text)
        data = parsed.get("data") if isinstance(parsed, dict) else None
        token = ""
        if isinstance(data, dict):
            token = str(data.get("accessToken") or data.get("token") or "")
        if not token:
            error = parsed.get("errorMsg") if isinstance(parsed, dict) else ""
            raise ApiError("FINEBI_LOGIN", str(error or "FineBI 登录失败"))
        cookies = []
        for cookie in jar:
            cookies.append("%s=%s" % (cookie.name, cookie.value))
        self._cookie_header = "; ".join(cookies)
        self._token = token
        self._token_at = time.time()
        return token

    def _get_token(self) -> str:
        if self.user_token:
            return self.user_token
        if self._token and time.time() - self._token_at < self._token_ttl:
            return self._token
        return self._login()

    def _request(self, body: Dict[str, Any]) -> Any:
        """依次尝试 FineBI v5 可能接受的 token 携带方式。"""
        token = self._get_token()
        if not token:
            raise ApiError("FINEBI_LOGIN", "未配置 FineBI 登录 token/服务账号")
        url = self.base_url + API_PATH
        base_headers = {"X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json"}
        modes = [
            ("bearer", {"Authorization": "Bearer " + token}, None),
            ("fine_auth_token-header", {"fine_auth_token": token}, None),
            ("fine_auth_token-query", None, {"fine_auth_token": token}),
            ("bearer+header+query",
             {"Authorization": "Bearer " + token, "fine_auth_token": token},
             {"fine_auth_token": token}),
        ]
        if self._cookie_header:
            modes.extend([
                ("cookie+token", {"Cookie": self._cookie_header}, None),
                ("cookie+bearer",
                 {"Cookie": self._cookie_header,
                  "Authorization": "Bearer " + token}, None),
            ])
        errors: List[str] = []
        for name, extra_headers, params in modes:
            headers = dict(base_headers)
            headers.update(extra_headers or {})
            try:
                resp = self.http.request("POST", url, json_body=body,
                                         headers=headers, params=params)
                parsed = _parse_json_body(resp)
                if parsed.get("success") is False:
                    errors.append("%s: %s" % (
                        name, str(parsed.get("errorMsg") or "接口返回失败")[:120]))
                    continue
                return parsed
            except Exception as exc:  # noqa: BLE001
                text = str(exc)
                title = ""
                match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
                if match:
                    title = re.sub(r"\s+", " ", match.group(1)).strip()[:80]
                errors.append("%s: %s%s" % (
                    name, text.split("\n", 1)[0][:120],
                    (" / " + title) if title else ""))
        detail = "；".join(errors[-3:])
        LOGGER.warning("FineBI v5 数据接口鉴权失败（尝试 %s 种方式）：%s",
                       len(errors), detail)
        raise ApiError("FINEBI_API",
                       "v5 数据接口拒绝访问（%s）。请确认账号有公共数据预览权限，"
                       "或改用有权限的只读账号。%s"
                       % (len(errors), detail))

    def preview(self, table_name: str, page_index: int = 1,
                page_size: int = 1000) -> Tuple[List[Dict[str, Any]], List[List[Any]]]:
        """返回 (fields, rows)；失败抛异常。"""
        body = {
            "tableName": str(table_name or ""),
            "pageIndex": str(page_index),
            "pageSize": str(page_size),
            "limit": str(page_size),
        }
        resp = self._request(body)
        data = _batch_item(resp)
        self.last_page_info = data.get("pageInfo") or {}
        fields = [item for item in (data.get("fields") or [])
                  if isinstance(item, dict)]
        rows = [item for item in (data.get("data") or [])
                if isinstance(item, list)]
        return fields, rows

    def field_values(self, table_names: List[str], field_id: str,
                     field_name: str, limit: int = 500,
                     max_pages: int = 50) -> List[str]:
        """分页预览并去重；默认最多 50 页 × 1000 行，按 totalRows 提前结束。"""
        want = str(field_id or "")
        wanted_name = str(field_name or "")
        values: List[str] = []
        total_rows = 0
        scanned_rows = 0
        page_size = 1000
        for table_name in table_names:
            if not table_name:
                continue
            try:
                for page in range(1, max(1, max_pages) + 1):
                    fields, rows = self.preview(table_name, page_index=page,
                                                page_size=page_size)
                    page_info = self.last_page_info or {}
                    try:
                        total_rows = int(page_info.get("totalRows") or 0)
                    except (TypeError, ValueError):
                        total_rows = 0
                    try:
                        effective_size = int(page_info.get("pageSize")
                                             or len(rows) or page_size)
                    except (TypeError, ValueError):
                        effective_size = len(rows) or page_size
                    scanned_rows += len(rows)
                    if not fields or not rows:
                        break
                    index = -1
                    for pos, field in enumerate(fields):
                        fid = str(field.get("id") or field.get("fieldId") or "")
                        name = str(field.get("name") or "")
                        transfer = str(field.get("transferName") or "")
                        if (want and (fid == want or fid.endswith(want))) \
                                or (wanted_name and wanted_name in (name, transfer)):
                            index = pos
                            break
                    if index < 0:
                        break
                    for row in rows:
                        if index < len(row):
                            value = row[index]
                            text = "" if value is None else str(value).strip()
                            if text and text not in values:
                                values.append(text)
                    if len(values) >= limit:
                        break
                    if total_rows and scanned_rows >= total_rows:
                        break
                    if effective_size and len(rows) < effective_size:
                        break
            except Exception:  # noqa: BLE001
                LOGGER.warning("FineBI 数据预览失败：table=%s", table_name,
                               exc_info=True)
                continue
            if values:
                self.last_scan = {"scanned_rows": scanned_rows,
                                  "total_rows": total_rows,
                                  "pages": page,
                                  "page_size": effective_size}
                return values[:limit]
        self.last_scan = {"scanned_rows": scanned_rows,
                          "total_rows": total_rows,
                          "pages": 0, "page_size": page_size}
        return values[:limit]
