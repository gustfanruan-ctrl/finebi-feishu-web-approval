"""Web 审批登录：本地开发账号 / 飞书 OAuth。

飞书 OAuth 流程（2026-11 真实环境已验证到回调建用户）：
1. 浏览器跳 ``authen/v1/authorize``（app_id/redirect_uri/state）；
2. 回调带 ``code``：用 ``app_access_token`` 调 ``authen/v1/oidc/access_token`` 换
   ``user_access_token``；
3. ``authen/v1/user_info`` 取 ``open_id``/``user_id``/``mobile``/``email``；
4. 映射优先级：FineDB 飞书映射（user_id）> 本地 web_users（user_id/open_id）>
   手机号/邮箱/姓名匹配 FineBI 账号 > open_id 占位。

state 用于防 CSRF：:meth:`WebAuth.create_state` 生成带 HMAC 签名与 TTL 的 state，
:meth:`WebAuth.verify_state` 校验；路由层（web/app.py）负责把 state 透传到回调。
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from ..config import Settings
from ..errors import ApiError
from ..http import HttpClient
from ..models import now_iso
from .service import WebApprovalService

LOGGER = logging.getLogger(__name__)

FEISHU_AUTHORIZE = "https://open.feishu.cn/open-apis/authen/v1/authorize"
FEISHU_APP_TOKEN = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
FEISHU_OIDC_TOKEN = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
FEISHU_USER_INFO = "https://open.feishu.cn/open-apis/authen/v1/user_info"

STATE_TTL_SECONDS = 600


class AuthError(Exception):
    pass


def _response_error(resp: Any) -> str:
    """把飞书响应压成 ``code=.. msg=..``，避免把含 token 的整包响应带进错误/日志。"""
    if not isinstance(resp, dict):
        return "响应不是 JSON 对象"
    code = resp.get("code")
    msg = str(resp.get("msg") or resp.get("message") or "")[:120]
    if code in (None, 0) and not msg:
        return "响应无 code/msg"
    return "code=%s msg=%s" % (code, msg)


class WebAuth:
    def __init__(self, settings: Settings, service: WebApprovalService,
                 http: Optional[HttpClient] = None):
        self.settings = settings
        self.service = service
        self.http = http or HttpClient(timeout=settings.http_timeout)
        # HMAC 用 app_secret；dev 模式下没配 secret 时用进程内随机 key（重启后旧 state 失效）
        self._state_key = (getattr(settings, "feishu_app_secret", "") or "").encode("utf-8")
        if not self._state_key:
            self._state_key = secrets.token_bytes(32)

    @property
    def mode(self) -> str:
        return (getattr(self.settings, "web_auth_mode", "dev") or "dev").lower()

    def login_dev(self, user_id: str) -> str:
        if not self.service.get_user(user_id):
            raise AuthError("用户不存在：%s" % user_id)
        return self.service.create_session(user_id)

    # ---------- OAuth state（CSRF） ----------
    def create_state(self, ttl: int = STATE_TTL_SECONDS) -> str:
        """生成 ``timestamp.nonce.signature`` 形式的 state（无需服务端存储）。"""
        issued = int(time.time())
        nonce = secrets.token_urlsafe(16)
        payload = "%d.%s" % (issued, nonce)
        signature = hmac.new(self._state_key, payload.encode("utf-8"),
                             hashlib.sha256).hexdigest()
        return "%s.%s" % (payload, signature)

    def verify_state(self, state: str, ttl: int = STATE_TTL_SECONDS) -> None:
        """校验 state；不合法/过期抛 :class:`AuthError`（路由层据此拒绝回调）。"""
        text = str(state or "")
        parts = text.split(".")
        if len(parts) != 3:
            raise AuthError("state 不合法")
        issued_text, nonce, signature = parts
        if not issued_text.isdigit():
            raise AuthError("state 不合法")
        issued = int(issued_text)
        now = int(time.time())
        if issued > now + 60:
            raise AuthError("state 不合法（时间戳异常）")
        if now - issued > ttl:
            raise AuthError("state 已过期，请重新登录")
        payload = "%d.%s" % (issued, nonce)
        expected = hmac.new(self._state_key, payload.encode("utf-8"),
                            hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise AuthError("state 校验失败")

    # ---------- 飞书 OAuth ----------
    def redirect_uri(self) -> str:
        return (getattr(self.settings, "feishu_oauth_redirect_uri", "")
                or (self.settings.public_base_url.rstrip("/") + "/auth/feishu/callback"))

    def authorize_url(self, state: str = "") -> str:
        query = {
            "app_id": self.settings.feishu_app_id,
            "redirect_uri": self.redirect_uri(),
            "state": state or self.create_state(),
        }
        # 需要手机号/邮箱匹配 FineBI 账号时，必须在授权 URL 里显式申请对应 scope
        scope = str(getattr(self.settings, "feishu_oauth_scope", "") or "").strip()
        if scope:
            query["scope"] = scope
        return FEISHU_AUTHORIZE + "?" + urlencode(query)

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        try:
            return self.http.request(method, url, **kwargs)
        except ApiError as exc:
            # 网络/HTTP 错误统一转 AuthError，避免回调页面 500；错误只留 code/msg 级别信息
            LOGGER.warning("飞书 OAuth 请求失败（%s）：%s", url, exc)
            raise AuthError("飞书 OAuth 请求失败：%s" % str(getattr(exc, "message", exc))[:200])

    def handle_callback(self, code: str, state: str = "") -> Dict[str, Any]:
        if not code:
            raise AuthError("缺少 code")
        if state:
            self.verify_state(state)
        app_resp = self._request("POST", FEISHU_APP_TOKEN, json_body={
            "app_id": self.settings.feishu_app_id,
            "app_secret": self.settings.feishu_app_secret,
        })
        if isinstance(app_resp, dict) and app_resp.get("code") not in (None, 0):
            raise AuthError("获取 app_access_token 失败（%s）" % _response_error(app_resp))
        app_token = ((app_resp or {}).get("app_access_token")
                     or ((app_resp or {}).get("data") or {}).get("app_access_token"))
        if not app_token:
            raise AuthError("获取 app_access_token 失败（响应缺少 app_access_token）")
        token_resp = self._request(
            "POST", FEISHU_OIDC_TOKEN,
            headers={"Authorization": "Bearer " + app_token},
            json_body={"grant_type": "authorization_code", "code": code})
        if isinstance(token_resp, dict) and token_resp.get("code") not in (None, 0):
            raise AuthError("换取 user_access_token 失败（%s）" % _response_error(token_resp))
        data = (token_resp or {}).get("data") or token_resp or {}
        user_token = data.get("access_token") if isinstance(data, dict) else ""
        if not user_token:
            raise AuthError("换取 user_access_token 失败（响应缺少 access_token）")
        user_resp = self._request(
            "GET", FEISHU_USER_INFO,
            headers={"Authorization": "Bearer " + user_token})
        if isinstance(user_resp, dict) and user_resp.get("code") not in (None, 0):
            raise AuthError("获取飞书用户信息失败（%s）" % _response_error(user_resp))
        info = (user_resp or {}).get("data") or {}
        if not isinstance(info, dict) or not info:
            raise AuthError("获取飞书用户信息失败（响应缺少 data）")
        open_id = str(info.get("open_id") or "")
        if not open_id:
            # open_id 是飞书身份的稳定标识；缺失时不能用 user_id 冒充（会污染映射）
            raise AuthError("获取飞书用户信息失败（响应缺少 open_id）")
        user_id = str(info.get("user_id") or "")
        user = None
        if user_id:
            user = self.service.find_by_feishu_user_id(user_id)
        if user:
            self.service.storage.conn.execute(
                "UPDATE web_users SET feishu_open_id=? WHERE id=?", (open_id, user["id"]))
            self.service.storage.conn.commit()
            return self.service.get_user(user["id"]) or user
        user = self.service.find_by_open_id(open_id)
        if user:
            mapped = self.service.fb_user_for_feishu_user(user_id) if user_id else ""
            if mapped:
                # FineDB 映射表最可靠：直接修正错配的 FineBI 账号
                if user.get("fb_user") != mapped:
                    self.service.storage.conn.execute(
                        "UPDATE web_users SET fb_user=?, feishu_user_id=? WHERE id=?",
                        (mapped, user_id, user["id"]))
                    self.service.storage.conn.commit()
                    user = self.service.get_user(user["id"]) or user
            elif not user.get("fb_user") or str(user.get("fb_user", "")).startswith("ou_"):
                # 旧会话用户可能只有 open_id 占位；按手机号/邮箱再匹配一次 FineBI 账号
                fb_user = self.service.resolve_fb_user(
                    mobile=str(info.get("mobile") or ""),
                    email=str(info.get("email") or ""),
                    name=str(info.get("name") or ""))
                if fb_user:
                    self.service.storage.conn.execute(
                        "UPDATE web_users SET fb_user=?, feishu_user_id=? WHERE id=?",
                        (fb_user, user_id, user["id"]))
                    self.service.storage.conn.commit()
                    user = self.service.get_user(user["id"]) or user
            return user
        # 首次登录：优先 FineDB 映射表，其次手机号/邮箱/姓名；匹配不到则用 open_id 占位
        fb_user = (self.service.fb_user_for_feishu_user(user_id)
                   or self.service.resolve_fb_user(
                       mobile=str(info.get("mobile") or ""),
                       email=str(info.get("email") or ""),
                       name=str(info.get("name") or ""))
                   or open_id)
        uid = "fs_" + open_id
        self.service.storage.conn.execute(
            "INSERT INTO web_users(id,name,email,feishu_open_id,feishu_user_id,fb_user,roles,active,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (uid, info.get("name") or open_id, info.get("email") or "", open_id,
             user_id, fb_user, '["applicant"]', 1, now_iso()))
        self.service.storage.conn.commit()
        return self.service.get_user(uid) or {}
