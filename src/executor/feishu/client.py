"""飞书客户端：tenant_access_token、审批实例、多维表格记录。

参考：docs/feishu/openapi/*.md
真实接口约定（2026-11 只读探测确认）：
- 无效/缺失 tenant_access_token 返回 HTTP 400，body ``code=99991661/99991663/99991668``；
  客户端需强制刷新 token 后重试一次（写接口此时尚未执行，重试安全）。
- 审批实例查询 page_size 取值 5~200、时间跨度不得大于 30 天，非法值返回
  ``99992402 field validation failed`` / ``1390001 query time range exceeds 30 days``。
- 批量获取实例 ID page_size 取值 1~100。
"""
from __future__ import annotations

import json
import logging
import threading
import time
import urllib.parse
from typing import Any, Dict, List, Optional

from ..errors import ApiError
from ..http import HttpClient

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://open.feishu.cn/open-apis"

# 需要强制刷新 tenant_access_token 后重试的错误码（token 无效/缺失/过期）
TOKEN_INVALID_CODES = {99991661, 99991663, 99991668}

# 飞书接口限流：HTTP 429 或业务码 99991400/99991401/99991402
RATE_LIMIT_CODES = {429, 99991400, 99991401, 99991402}
RATE_LIMIT_RETRIES = 5
RATE_LIMIT_BASE_DELAY = 0.5

# 审批实例状态（/approval/v4/instances/query 的 instance_status）
INSTANCE_STATUSES = {"PENDING", "RECALL", "REJECT", "DELETED", "APPROVED", "ALL"}


class FeishuClient:
    def __init__(self, app_id: str, app_secret: str,
                 http: Optional[HttpClient] = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.http = http or HttpClient()
        self._token = ""
        # 用单调时钟记过期，避免系统时间被调整后 token 缓存判断失真
        self._token_expire_at = 0.0
        self._token_lock = threading.Lock()

    # ---------- 认证 ----------
    def tenant_token(self, force: bool = False) -> str:
        if not force and self._cached_token(60):
            return self._token
        with self._token_lock:
            # 双检：并发请求只刷新一次
            if not force and self._cached_token(60):
                return self._token
            resp = self.http.request(
                "POST", BASE_URL + "/auth/v3/tenant_access_token/internal",
                json_body={"app_id": self.app_id, "app_secret": self.app_secret})
            self._check(resp)
            token = str((resp or {}).get("tenant_access_token") or "")
            if not token:
                raise ApiError("NO_TOKEN", "tenant_access_token 响应缺少 token", resp)
            try:
                expire = int((resp or {}).get("expire") or 7200)
            except (TypeError, ValueError):
                expire = 7200
            self._token = token
            self._token_expire_at = time.monotonic() + expire
            LOGGER.info("刷新 tenant_access_token，有效期 %ss", expire)
            return self._token

    def _cached_token(self, margin: int) -> bool:
        return bool(self._token) and time.monotonic() < self._token_expire_at - margin

    @staticmethod
    def _error_code(exc: ApiError) -> Any:
        """从 ApiError.payload 里取飞书业务错误码（HTTP 400 时 body 是 JSON 字符串）。"""
        payload = getattr(exc, "payload", None)
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                return None
        if isinstance(payload, dict):
            return payload.get("code")
        return None

    def _is_token_invalid(self, exc: ApiError) -> bool:
        return self._error_code(exc) in TOKEN_INVALID_CODES

    def _call(self, method: str, path: str, body: Any = None,
              query: Optional[Dict[str, Any]] = None) -> Any:
        rate_attempt = 0
        while True:
            for attempt in range(2):
                headers = {"Authorization": "Bearer " + self.tenant_token(force=attempt > 0)}
                try:
                    resp = self.http.request(method, BASE_URL + path, headers=headers,
                                             json_body=body, params=query)
                    self._check(resp)
                except ApiError as exc:
                    # token 失效时请求尚未执行（鉴权阶段被拒），强制刷新后重试一次是安全的
                    if attempt == 0 and self._is_token_invalid(exc):
                        LOGGER.info("tenant_access_token 失效（code=%s），刷新后重试一次",
                                    self._error_code(exc))
                        continue
                    if self._is_rate_limited(exc) and rate_attempt < RATE_LIMIT_RETRIES:
                        delay = RATE_LIMIT_BASE_DELAY * (2 ** rate_attempt)
                        rate_attempt += 1
                        LOGGER.warning("飞书接口限流（code=%s），%.1fs 后重试 %d/%d",
                                       self._error_code(exc), delay,
                                       rate_attempt, RATE_LIMIT_RETRIES)
                        time.sleep(delay)
                        break
                    raise
                return resp
            else:
                raise ApiError("TOKEN_RETRY", "刷新 tenant_access_token 后仍失败")
            continue

    @staticmethod
    def _is_rate_limited(exc: ApiError) -> bool:
        code = exc.status
        try:
            if int(code) in RATE_LIMIT_CODES:
                return True
        except (TypeError, ValueError):
            pass
        text = str(exc).lower()
        return ("frequency" in text or "rate limit" in text
                or "too many request" in text or "限流" in text)


    @staticmethod
    def _check(resp: Any) -> None:
        if isinstance(resp, dict) and resp.get("code", 0) != 0:
            raise ApiError(resp.get("code"), str(resp.get("msg")), resp)

    # ---------- 审批 ----------
    def query_instances(self, approval_code: str, status: str = "APPROVED",
                        start_ms: Optional[int] = None, end_ms: Optional[int] = None,
                        page_size: int = 100, page_token: str = "") -> Dict[str, Any]:
        """查询审批实例列表（POST /approval/v4/instances/query）。

        文档/真实接口约束：page_size 5~200；时间跨度≤30 天且开始/结束必须同时设置。
        """
        if not approval_code:
            raise ValueError("approval_code 不能为空")
        status = (status or "").upper()
        if status and status not in INSTANCE_STATUSES:
            raise ValueError("instance_status 不合法：%r（可选 %s）"
                             % (status, sorted(INSTANCE_STATUSES)))
        if (start_ms is None) != (end_ms is None):
            raise ValueError("instance_start_time_from/to 必须同时设置或同时不设置")
        if start_ms is not None and end_ms is not None:
            start_ms, end_ms = int(start_ms), int(end_ms)
            if end_ms <= start_ms:
                raise ValueError("审批实例查询结束时间必须大于开始时间")
            if end_ms - start_ms > 30 * 24 * 3600 * 1000:
                raise ValueError("审批实例查询时间跨度不得大于 30 天")
        page_size = int(page_size)
        if not 5 <= page_size <= 200:
            raise ValueError("审批实例查询 page_size 必须在 5~200：%s" % page_size)
        body: Dict[str, Any] = {"approval_code": approval_code}
        if status:
            body["instance_status"] = status
        if start_ms is not None:
            body["instance_start_time_from"] = str(start_ms)
        if end_ms is not None:
            body["instance_start_time_to"] = str(end_ms)
        query = {"page_size": page_size}
        if page_token:
            query["page_token"] = page_token
        return self._call("POST", "/approval/v4/instances/query", body=body, query=query)

    def list_instance_ids(self, approval_code: str, start_ms: int, end_ms: int,
                          page_size: int = 100, page_token: str = "") -> Dict[str, Any]:
        """批量获取审批实例 ID（GET /approval/v4/instances，page_size 1~100）。

        文档建议单次查询时间范围不超过 10 小时；实测服务端未强校验，
        超过时只记 warning（调用方按需要自行分片）。
        """
        if not approval_code:
            raise ValueError("approval_code 不能为空")
        start_ms, end_ms = int(start_ms), int(end_ms)
        if end_ms <= start_ms:
            raise ValueError("审批实例查询结束时间必须大于开始时间")
        if end_ms - start_ms > 10 * 3600 * 1000:
            LOGGER.warning("list_instance_ids 时间跨度 %d 小时超过文档建议的 10 小时",
                           (end_ms - start_ms) // 3600000)
        page_size = int(page_size)
        if not 1 <= page_size <= 100:
            raise ValueError("批量获取审批实例 ID 的 page_size 必须在 1~100：%s" % page_size)
        query = {"approval_code": approval_code, "start_time": start_ms,
                 "end_time": end_ms, "page_size": page_size}
        if page_token:
            query["page_token"] = page_token
        return self._call("GET", "/approval/v4/instances", query=query)

    def get_instance(self, instance_code: str, locale: str = "zh-CN") -> Dict[str, Any]:
        """获取单个审批实例详情（GET /approval/v4/instances/:instance_code）。"""
        if not instance_code:
            raise ValueError("instance_code 不能为空")
        return self._call(
            "GET", "/approval/v4/instances/" + urllib.parse.quote(str(instance_code), safe=""),
            query={"locale": locale})

    # ---------- 多维表格 ----------
    def list_bitable_fields(self, app_token: str, table_id: str,
                            page_size: int = 100) -> Dict[str, Any]:
        return self._call("GET",
                          "/bitable/v1/apps/%s/tables/%s/fields" % (app_token, table_id),
                          query={"page_size": page_size})

    def create_bitable_field(self, app_token: str, table_id: str, field_name: str,
                             field_type: int = 1) -> Dict[str, Any]:
        return self._call("POST",
                          "/bitable/v1/apps/%s/tables/%s/fields" % (app_token, table_id),
                          body={"field_name": field_name, "type": int(field_type)})

    def update_bitable_field(self, app_token: str, table_id: str, field_id: str,
                             field_name: str = "", field_type: int = 1) -> Dict[str, Any]:
        body: Dict[str, Any] = {"type": int(field_type)}
        if field_name:
            body["field_name"] = field_name
        return self._call("PUT",
                          "/bitable/v1/apps/%s/tables/%s/fields/%s" % (app_token, table_id, field_id),
                          body=body)

    def create_record(self, app_token: str, table_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self._call("POST",
                          "/bitable/v1/apps/%s/tables/%s/records" % (app_token, table_id),
                          body={"fields": fields})

    def update_record(self, app_token: str, table_id: str, record_id: str,
                      fields: Dict[str, Any]) -> Dict[str, Any]:
        return self._call("PUT",
                          "/bitable/v1/apps/%s/tables/%s/records/%s" % (app_token, table_id, record_id),
                          body={"fields": fields})

    def list_records(self, app_token: str, table_id: str, page_size: int = 100,
                     page_token: str = "") -> Dict[str, Any]:
        page_size = int(page_size)
        if not 1 <= page_size <= 500:
            raise ValueError("多维表格记录分页 page_size 必须在 1~500：%s" % page_size)
        query: Dict[str, Any] = {"page_size": page_size}
        if page_token:
            query["page_token"] = page_token
        return self._call("GET",
                          "/bitable/v1/apps/%s/tables/%s/records" % (app_token, table_id),
                          query=query)

    def batch_create_records(self, app_token: str, table_id: str,
                             records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not 1 <= len(records or []) <= 1000:
            raise ValueError("多维表格批量新增记录数必须在 1~1000：%s" % len(records or []))
        return self._call("POST",
                          "/bitable/v1/apps/%s/tables/%s/records/batch_create" % (app_token, table_id),
                          body={"records": records})

    # ---------- 消息通知 ----------
    def send_message(self, receive_id: str, msg_type: str, content: Dict[str, Any],
                     receive_id_type: str = "open_id") -> Dict[str, Any]:
        """发送消息（POST /im/v1/messages）。content 会序列化为 JSON 字符串。"""
        return self._call(
            "POST", "/im/v1/messages",
            body={"receive_id": receive_id, "msg_type": msg_type,
                  "content": json.dumps(content, ensure_ascii=False)},
            query={"receive_id_type": receive_id_type})

    def send_card(self, receive_id: str, card: Dict[str, Any],
                  receive_id_type: str = "open_id") -> Dict[str, Any]:
        # build_card() 返回的是 webhook 信封（msg_type + card）；应用消息只收 card 本体
        if isinstance(card, dict) and "msg_type" in card and isinstance(card.get("card"), dict):
            card = card["card"]
        return self.send_message(receive_id, "interactive", card, receive_id_type)

    def send_webhook(self, webhook_url: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """自定义机器人 webhook（URL 完整，无需 tenant token）。"""
        resp = self.http.request("POST", webhook_url, json_body=card)
        if isinstance(resp, dict) and resp.get("code") not in (None, 0):
            raise ApiError(resp.get("code"), str(resp.get("msg")), resp)
        return resp

    # ---------- 通讯录 ----------
    def list_contact_users(self, page_size: int = 50, page_token: str = "",
                           department_id: str = "0",
                           user_id_type: str = "open_id") -> Dict[str, Any]:
        query = {"page_size": page_size, "department_id": department_id,
                 "user_id_type": user_id_type}
        if page_token:
            query["page_token"] = page_token
        return self._call("GET", "/contact/v3/users", query=query)

    def list_departments(self, parent_department_id: str = "0",
                         fetch_child: bool = True, page_size: int = 50,
                         page_token: str = "") -> Dict[str, Any]:
        """获取部门列表；fetch_child=true 时递归返回全部子部门。"""
        query = {"parent_department_id": parent_department_id,
                 "fetch_child": "true" if fetch_child else "false",
                 "page_size": page_size,
                 "department_id_type": "open_department_id"}
        if page_token:
            query["page_token"] = page_token
        return self._call("GET", "/contact/v3/departments", query=query)

    def list_department_users(self, department_id: str, page_size: int = 50,
                              page_token: str = "") -> Dict[str, Any]:
        """获取部门直属用户列表。"""
        query = {"department_id": department_id, "page_size": page_size,
                 "user_id_type": "open_id",
                 "department_id_type": "open_department_id"}
        if page_token:
            query["page_token"] = page_token
        return self._call("GET", "/contact/v3/users/find_by_department", query=query)
