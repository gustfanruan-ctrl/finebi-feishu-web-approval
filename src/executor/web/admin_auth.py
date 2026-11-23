"""后台管理独立登录：用户名 + PBKDF2 密码哈希（与飞书 OAuth 隔离）。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Optional

PBKDF2_ITERATIONS = 390000
PREFIX = "pbkdf2_sha256"


def hash_password(password: str, salt: Optional[str] = None,
                  iterations: int = PBKDF2_ITERATIONS) -> str:
    """生成 ``pbkdf2_sha256$iterations$salt$hash``，可直接写入 .env。"""
    text = str(password or "")
    if not text:
        raise ValueError("密码不能为空")
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", text.encode("utf-8"),
                                 salt.encode("utf-8"), int(iterations))
    return "%s$%d$%s$%s" % (PREFIX, int(iterations), salt, digest.hex())


def verify_password(password: str, encoded: str) -> bool:
    """校验密码；格式不合法/为空时返回 False，不抛异常。"""
    try:
        prefix, iterations_text, salt, expected = str(encoded or "").split("$", 3)
        if prefix != PREFIX:
            return False
        iterations = int(iterations_text)
        digest = hashlib.pbkdf2_hmac("sha256", str(password or "").encode("utf-8"),
                                     salt.encode("utf-8"), iterations)
        return hmac.compare_digest(digest.hex(), expected)
    except (TypeError, ValueError):
        return False


def admin_configured(username: str, password_hash: str) -> bool:
    return bool(str(username or "").strip()) and bool(str(password_hash or "").strip())
