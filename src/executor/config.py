"""配置加载：环境变量优先，支持简单 .env 与 JSON 配置文件。

凭证只从环境变量/`.env` 读取；JSON 配置文件用于非敏感的策略项。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .errors import ConfigError

TRUE_VALUES = {"1", "true", "yes", "on"}


def _load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _get(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return default if value is None or value.strip() == "" else value.strip().lstrip("\ufeff")


def _get_optional(name: str, default: str = "") -> str:
    """区分“未设置”与“显式留空”：未设置取 default，显式留空返回空串。

    FineBI 应用身份调用开放平台时不能带 decUser（客户环境没有 api_bot 用户），
    因此 FINEBI_DEC_USER= 必须保持为空而不是回退到默认用户。
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lstrip("\ufeff")


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ConfigError("环境变量 %s 必须是整数" % name) from exc


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in TRUE_VALUES


def _load_config_file(path: str) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    if path.lower().endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise ConfigError("读取 YAML 配置需要安装 PyYAML：pip install PyYAML") from exc
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _normalize_finebi_base_url(value: str) -> str:
    """FineBI 客户端会自动拼 /webroot/decision/sp/client/api。

    用户常把浏览器地址（.../webroot/decision）直接填进来；这里统一剥掉，
    避免变成 /webroot/decision/webroot/decision/...。
    """
    text = str(value or "").strip().rstrip("/")
    suffix = "/webroot/decision"
    if text.lower().endswith(suffix):
        text = text[:-len(suffix)].rstrip("/")
    return text


@dataclass
class Settings:
    # FineBI 开放平台
    finebi_base_url: str
    finebi_client_id: str
    finebi_secret: str
    finebi_dec_user: str = ""
    # FineBI v5 数据表预览接口的登录 token（fine_auth_token，不是 OpenAPI client secret）
    finebi_user_token: str = ""
    # 或使用只读服务账号自动登录/刷新（密码只从环境变量读取，不写日志）
    finebi_api_username: str = ""
    finebi_api_password: str = ""
    # 飞书
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_approval_code: str = ""
    bitable_app_token: str = ""
    bitable_ledger_table_id: str = ""
    bitable_resource_table_id: str = ""
    # Web 审批「权限申请台账」表（写入申请/审批/授权状态）
    bitable_request_table_id: str = ""
    # 运行参数
    db_path: str = "data/executor.db"
    dry_run: bool = True
    default_days: int = 90
    max_days: int = 365
    http_timeout: int = 20
    log_level: str = "INFO"
    # 通知
    feishu_webhook_url: str = ""
    admin_open_ids: List[str] = field(default_factory=list)
    # 运行/安全
    api_token: str = ""
    lock_ttl: int = 120
    row_clear_strategy: str = "manual"
    role_mode: str = "api"
    adopt_existing: bool = False
    bitable_write: bool = False
    # 自建 Web 审批
    web_auth_mode: str = "dev"
    public_base_url: str = ""
    feishu_oauth_redirect_uri: str = ""
    # 飞书 OAuth 额外申请的权限（空格分隔），如 contact:user.phone:readonly
    feishu_oauth_scope: str = ""
    # 后台管理独立登录（与飞书 OAuth 分离）
    admin_username: str = "admin"
    admin_password_hash: str = ""
    # 目录/角色/部门定时刷新（小时）
    directory_refresh_hours: int = 6
    # FineDB（只读，用于飞书映射/行权限枚举）
    fine_db_host: str = ""
    fine_db_port: int = 3306
    fine_db_user: str = ""
    fine_db_password: str = ""
    fine_db_name: str = "finedb"
    # 策略配置（config/*.json|yaml）
    policy: Dict[str, Any] = field(default_factory=dict)
    resource_map: Dict[str, Any] = field(default_factory=dict)
    templates: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, env_path: str = ".env", config_path: str = "config/config.json") -> "Settings":
        _load_dotenv(env_path)
        cfg = _load_config_file(config_path)
        policy = cfg.get("policy", {})
        resource_map = cfg.get("resources", {})
        templates = cfg.get("templates", {})
        settings = cls(
            finebi_base_url=_normalize_finebi_base_url(
                _get("FINEBI_BASE_URL", "http://127.0.0.1:8075")),
            finebi_client_id=_get("FINEBI_CLIENT_ID", ""),
            finebi_secret=_get("FINEBI_SECRET", ""),
            finebi_dec_user=_get_optional("FINEBI_DEC_USER", ""),
            finebi_user_token=_get_optional("FINEBI_USER_TOKEN", ""),
            finebi_api_username=_get_optional("FINEBI_API_USERNAME", ""),
            finebi_api_password=_get_optional("FINEBI_API_PASSWORD", ""),
            feishu_app_id=_get("FEISHU_APP_ID", ""),
            feishu_app_secret=_get("FEISHU_APP_SECRET", ""),
            feishu_approval_code=_get("FEISHU_APPROVAL_CODE", ""),
            bitable_app_token=_get("FEISHU_BITABLE_APP_TOKEN", ""),
            bitable_ledger_table_id=_get("FEISHU_BITABLE_LEDGER_TABLE_ID", ""),
            bitable_resource_table_id=_get("FEISHU_BITABLE_RESOURCE_TABLE_ID", ""),
            bitable_request_table_id=_get("FEISHU_BITABLE_REQUEST_TABLE_ID", ""),
            db_path=_get("EXECUTOR_DB_PATH", "data/executor.db"),
            dry_run=_get_bool("EXECUTOR_DRY_RUN", True),
            default_days=_get_int("EXECUTOR_DEFAULT_DAYS", 90),
            max_days=_get_int("EXECUTOR_MAX_DAYS", 365),
            http_timeout=_get_int("EXECUTOR_HTTP_TIMEOUT", 20),
            log_level=_get("EXECUTOR_LOG_LEVEL", "INFO"),
            feishu_webhook_url=_get("FEISHU_WEBHOOK_URL", ""),
            admin_open_ids=[x.strip() for x in (_get("FEISHU_ADMIN_OPEN_IDS", "") or "").split(",") if x.strip()],
            api_token=_get("EXECUTOR_API_TOKEN", ""),
            lock_ttl=_get_int("EXECUTOR_LOCK_TTL", 120),
            row_clear_strategy=_get("EXECUTOR_ROW_CLEAR_STRATEGY", "manual").lower(),
            role_mode=_get("EXECUTOR_ROLE_MODE", "api").lower(),
            adopt_existing=_get_bool("EXECUTOR_ADOPT_EXISTING", False),
            bitable_write=_get_bool("EXECUTOR_BITABLE_WRITE", False),
            web_auth_mode=_get("WEB_AUTH_MODE", "dev").lower(),
            public_base_url=_get("PUBLIC_BASE_URL", ""),
            feishu_oauth_redirect_uri=_get("FEISHU_OAUTH_REDIRECT_URI", ""),
            feishu_oauth_scope=_get("FEISHU_OAUTH_SCOPE", ""),
            admin_username=_get("ADMIN_USERNAME", "admin"),
            admin_password_hash=_get("ADMIN_PASSWORD_HASH", ""),
            directory_refresh_hours=_get_int("EXECUTOR_DIRECTORY_REFRESH_HOURS", 6),
            fine_db_host=_get("FINE_DB_HOST", ""),
            fine_db_port=_get_int("FINE_DB_PORT", 3306),
            fine_db_user=_get("FINE_DB_USER", ""),
            fine_db_password=_get("FINE_DB_PASSWORD", ""),
            fine_db_name=_get("FINE_DB_NAME", "finedb"),
            policy=policy,
            resource_map=resource_map,
            templates=templates,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.finebi_base_url.startswith("http"):
            raise ConfigError("FINEBI_BASE_URL 必须以 http(s):// 开头")
        if not self.dry_run:
            missing = [
                name for name, value in (
                    ("FINEBI_CLIENT_ID", self.finebi_client_id),
                    ("FINEBI_SECRET", self.finebi_secret),
                    ("FEISHU_APP_ID", self.feishu_app_id),
                    ("FEISHU_APP_SECRET", self.feishu_app_secret),
                ) if not value
            ]
            if missing:
                raise ConfigError("非 dry-run 模式缺少配置：%s" % ", ".join(missing))
        if self.default_days <= 0 or self.max_days < self.default_days:
            raise ConfigError("期限配置不合法：default_days=%s, max_days=%s"
                              % (self.default_days, self.max_days))
        if self.row_clear_strategy not in ("manual", "deny", "empty"):
            raise ConfigError("ROW_CLEAR_STRATEGY 必须是 manual/deny/empty")
        if self.role_mode not in ("api", "manual"):
            raise ConfigError("ROLE_MODE 必须是 api/manual")
        if self.web_auth_mode not in ("dev", "feishu"):
            raise ConfigError("WEB_AUTH_MODE 必须是 dev/feishu")
        if self.directory_refresh_hours <= 0:
            raise ConfigError("EXECUTOR_DIRECTORY_REFRESH_HOURS 必须大于 0")

    def summary(self) -> Dict[str, Any]:
        return {
            "finebi_base_url": self.finebi_base_url,
            "finebi_client_id": self.finebi_client_id[:6] + "***" if self.finebi_client_id else "",
            "feishu_app_id": self.feishu_app_id[:8] + "***" if self.feishu_app_id else "",
            "approval_code": self.feishu_approval_code,
            "db_path": self.db_path,
            "dry_run": self.dry_run,
            "default_days": self.default_days,
            "row_clear_strategy": self.row_clear_strategy,
            "role_mode": self.role_mode,
            "adopt_existing": self.adopt_existing,
            "bitable_write": self.bitable_write,
            "notify": bool(self.feishu_webhook_url or self.admin_open_ids),
            "web_auth_mode": self.web_auth_mode,
            "public_base_url": self.public_base_url,
            "admin_login": bool(self.admin_username and self.admin_password_hash),
            "directory_refresh_hours": self.directory_refresh_hours,
            "finedb": bool(self.fine_db_host),
        }
