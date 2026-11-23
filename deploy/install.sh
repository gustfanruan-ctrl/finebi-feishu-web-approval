#!/usr/bin/env bash
# FineBI × 飞书自建 Web 审批：Linux 一键部署（NGINX + systemd + 定时刷新）
#
# 用法（root）：
#   sudo bash deploy/install.sh --domain finebi.example.com
#   sudo bash deploy/install.sh --domain finebi.example.com --tls --email ops@example.com
#   sudo FINEBI_BASE_URL=... FINEBI_CLIENT_ID=... ... bash deploy/install.sh --domain ...
#
# 说明：
# - 脚本可重复执行：代码会同步到 APP_DIR，.env 和 data/ 不会被覆盖；
# - 首次部署若没有 .env，会交互式生成（或从环境变量读取），需要 FineBI/飞书密钥；
# - 后台管理（/admin/login）使用独立用户名/密码，首次部署会交互式设置，
#   也可用 ADMIN_USERNAME/ADMIN_PASSWORD（或 ADMIN_PASSWORD_HASH）非交互传入；
# - TLS 使用 certbot --nginx（需要域名已解析到本机且 80/443 可访问）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="${APP_DIR:-/opt/finebi-feishu}"
APP_USER="${APP_USER:-finebi}"
DOMAIN="${DOMAIN:-}"
ENABLE_TLS="${ENABLE_TLS:-0}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"
INSTALL_NGINX="${INSTALL_NGINX:-1}"
SKIP_COPY="${SKIP_COPY:-0}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
ADMIN_USERNAME_EXPLICIT="${ADMIN_USERNAME:-}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"

usage() {
  cat <<'EOF'
用法: sudo bash deploy/install.sh --domain <域名> [选项]
  --domain DOMAIN       对外域名（必填，例如 finebi.example.com）
  --app-dir DIR         安装目录，默认 /opt/finebi-feishu
  --user USER           运行用户，默认 finebi
  --tls                 用 certbot 申请并配置 HTTPS
  --email EMAIL         certbot 邮箱（--tls 时必填）
  --no-nginx            只装应用/systemd，不安装 NGINX
  --skip-copy           包已解压在 APP_DIR 时跳过代码同步
  --admin-user NAME     后台管理员用户名，默认 admin（密码首次部署时交互输入）
  -h, --help            显示帮助

环境变量（非交互部署）：
  ADMIN_USERNAME        后台管理员用户名（默认 admin）
  ADMIN_PASSWORD        后台管理员密码明文（仅用于首次生成哈希，不会写入 .env）
  ADMIN_PASSWORD_HASH   已生成的密码哈希（pbkdf2_sha256$...，优先于 ADMIN_PASSWORD）
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    --app-dir) APP_DIR="${2:-}"; shift 2 ;;
    --user) APP_USER="${2:-}"; shift 2 ;;
    --tls) ENABLE_TLS=1; shift ;;
    --email) CERTBOT_EMAIL="${2:-}"; shift 2 ;;
    --no-nginx) INSTALL_NGINX=0; shift ;;
    --skip-copy) SKIP_COPY=1; shift ;;
    --admin-user) ADMIN_USERNAME="${2:-}"; ADMIN_USERNAME_EXPLICIT=1; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数：$1"; usage; exit 2 ;;
  esac
done

if [[ "$(id -u)" != "0" ]]; then
  echo "请用 root 运行：sudo $0 --domain <域名>"
  exit 1
fi
if [[ -z "$DOMAIN" ]]; then
  echo "缺少 --domain（例如 finebi.example.com）"
  usage
  exit 2
fi
if [[ "$ENABLE_TLS" == "1" && -z "$CERTBOT_EMAIL" ]]; then
  echo "--tls 需要同时提供 --email（certbot 账号邮箱）"
  exit 2
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "找不到 $PYTHON_BIN，请先安装 Python 3.10+"
  exit 2
fi
"$PYTHON_BIN" - <<'PY' || { echo "Python 版本过低，需要 3.10+"; exit 2; }
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY

log() { printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
warn() { printf '\n[警告] %s\n' "$*" >&2; }

# ---------- 1. 同步代码 ----------
log "同步代码到 $APP_DIR"
mkdir -p "$APP_DIR"
if [[ "$SKIP_COPY" != "1" && "$ROOT" != "$APP_DIR" ]]; then
  tar -C "$ROOT" \
    --exclude='./.git' --exclude='./.venv' --exclude='./__pycache__' \
    --exclude='./.env' --exclude='./logs' --exclude='./dist' \
    --exclude='./data/*.db' --exclude='./data/*.db-*' \
    --exclude='./data/catalog.json' --exclude='./data/catalog.csv' \
    --exclude='./data/membership_options.json' \
    --exclude='./data/directory_status.json' \
    --exclude='./data/directory_refresh.log' \
    --exclude='./data/.directory_refresh.lock' \
    --exclude='./tools/ngrok.exe' \
    -cf - . | tar -C "$APP_DIR" -xf -
fi
mkdir -p "$APP_DIR/data" "$APP_DIR/logs"
# 配置包自带 .env 时复制到安装目录（不覆盖已有 .env）；随后按 --domain 校正对外地址
if [[ -f "$ROOT/.env" && ! -f "$APP_DIR/.env" ]]; then
  cp "$ROOT/.env" "$APP_DIR/.env"
  chown "$APP_USER":"$APP_USER" "$APP_DIR/.env" 2>/dev/null || true
  chmod 600 "$APP_DIR/.env"
fi
# 首次部署用配置模板生成 config.json；客户实际的用户/审批策略需按需修改
if [[ ! -f "$APP_DIR/config/config.json" && -f "$APP_DIR/config/config.example.json" ]]; then
  cp "$APP_DIR/config/config.example.json" "$APP_DIR/config/config.json"
  warn "已生成空的 config/config.json（无演示用户/资源）；部署后请登录 /admin 同步飞书用户并配置审批人、Owner"
fi

# ---------- 2. 运行用户 ----------
if ! id "$APP_USER" >/dev/null 2>&1; then
  log "创建系统用户 $APP_USER"
  useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER" 2>/dev/null \
    || useradd -r -d "$APP_DIR" -s /sbin/nologin "$APP_USER"
fi
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
chmod 750 "$APP_DIR"
# Windows 下打包/解压的 zip 会让目录丢掉执行位（drw-r--r--），
# 运行用户无法进入 src/ 子目录，启动时报 No module named 'executor'
find "$APP_DIR" -type d ! -perm -u+x -exec chmod u+x {} + 2>/dev/null || true
find "$APP_DIR" -type f ! -perm -u+r -exec chmod u+r {} + 2>/dev/null || true

# ---------- 3. Python venv + 依赖 ----------
log "安装 Python 依赖"
if [[ ! -x "$APP_DIR/.venv/bin/python" ]]; then
  "$PYTHON_BIN" -m venv "$APP_DIR/.venv"
fi
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip >/dev/null
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

# 导入自检：目录权限/依赖缺失在这里提前失败，避免 systemd 反复重启
log "自检：$APP_USER 用户导入 executor.web"
if command -v sudo >/dev/null 2>&1; then
  RUN_AS=(sudo -u "$APP_USER")
else
  RUN_AS=(runuser -u "$APP_USER" --)
fi
if ! "${RUN_AS[@]}" env PYTHONPATH="$APP_DIR/src" \
    "$APP_DIR/.venv/bin/python" -c "import executor.web" \
    >/dev/null 2>"$APP_DIR/logs/import_check.log"; then
  echo "自检失败：$APP_USER 用户无法导入 executor.web" >&2
  cat "$APP_DIR/logs/import_check.log" >&2 || true
  echo "常见原因：解压 zip 后目录缺少执行位。可执行后重跑：" >&2
  echo "  sudo find $APP_DIR -type d -exec chmod u+x {} +" >&2
  exit 1
fi

# ---------- 4. .env ----------
ENV_FILE="$APP_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  log "生成 .env"
  if [[ -n "${FINEBI_BASE_URL:-}" && -n "${FINEBI_CLIENT_ID:-}" \
        && -n "${FINEBI_SECRET:-}" && -n "${FEISHU_APP_ID:-}" \
        && -n "${FEISHU_APP_SECRET:-}" ]]; then
    PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-}"
    if [[ -z "$PUBLIC_BASE_URL" ]]; then
      if [[ "$ENABLE_TLS" == "1" ]]; then PUBLIC_BASE_URL="https://$DOMAIN"; else PUBLIC_BASE_URL="http://$DOMAIN"; fi
    fi
    # FineBI 客户端自己会拼 /webroot/decision/sp/client/api，这里剥掉浏览器路径
    FINEBI_BASE_URL="${FINEBI_BASE_URL%/}"
    FINEBI_BASE_URL="${FINEBI_BASE_URL%/webroot/decision}"
    FINEBI_BASE_URL="${FINEBI_BASE_URL%/}"
    umask 077
    cat > "$ENV_FILE" <<EOF
FINEBI_BASE_URL=$FINEBI_BASE_URL
FINEBI_CLIENT_ID=$FINEBI_CLIENT_ID
FINEBI_SECRET=$FINEBI_SECRET
FINEBI_DEC_USER=${FINEBI_DEC_USER-}
FEISHU_APP_ID=$FEISHU_APP_ID
FEISHU_APP_SECRET=$FEISHU_APP_SECRET
EXECUTOR_DRY_RUN=false
EXECUTOR_DB_PATH=data/executor.db
EXECUTOR_DIRECTORY_REFRESH_HOURS=6
WEB_AUTH_MODE=feishu
PUBLIC_BASE_URL=$PUBLIC_BASE_URL
FEISHU_OAUTH_REDIRECT_URI=$PUBLIC_BASE_URL/auth/feishu/callback
# 后台管理独立登录（/admin/login），哈希在下一步生成
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH:-}
FINE_DB_HOST=${FINE_DB_HOST:-}
FINE_DB_PORT=${FINE_DB_PORT:-3306}
FINE_DB_USER=${FINE_DB_USER:-}
FINE_DB_PASSWORD=${FINE_DB_PASSWORD:-}
FINE_DB_NAME=${FINE_DB_NAME:-finedb}
EOF
  elif [[ -t 0 ]]; then
    echo "未提供环境变量，进入交互式配置（密钥输入不回显）"
    read -rp "FineBI 地址（只填协议+主机+端口，如 http://10.0.0.10:1080，不要带 /webroot/decision）: " FINEBI_BASE_URL
    read -rp "FineBI clientId: " FINEBI_CLIENT_ID
    read -rsp "FineBI secret: " FINEBI_SECRET; echo
    read -rp "飞书 App ID: " FEISHU_APP_ID
    read -rsp "飞书 App Secret: " FEISHU_APP_SECRET; echo
    FINEBI_BASE_URL="${FINEBI_BASE_URL%/}"
    FINEBI_BASE_URL="${FINEBI_BASE_URL%/webroot/decision}"
    FINEBI_BASE_URL="${FINEBI_BASE_URL%/}"
    if [[ "$ENABLE_TLS" == "1" ]]; then PUBLIC_BASE_URL="https://$DOMAIN"; else PUBLIC_BASE_URL="http://$DOMAIN"; fi
    umask 077
    cat > "$ENV_FILE" <<EOF
FINEBI_BASE_URL=$FINEBI_BASE_URL
FINEBI_CLIENT_ID=$FINEBI_CLIENT_ID
FINEBI_SECRET=$FINEBI_SECRET
FINEBI_DEC_USER=
FEISHU_APP_ID=$FEISHU_APP_ID
FEISHU_APP_SECRET=$FEISHU_APP_SECRET
EXECUTOR_DRY_RUN=false
EXECUTOR_DB_PATH=data/executor.db
EXECUTOR_DIRECTORY_REFRESH_HOURS=6
WEB_AUTH_MODE=feishu
PUBLIC_BASE_URL=$PUBLIC_BASE_URL
FEISHU_OAUTH_REDIRECT_URI=$PUBLIC_BASE_URL/auth/feishu/callback
# 后台管理独立登录（/admin/login），哈希在下一步生成
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH:-}
EOF
  else
    echo "没有 .env 且未提供环境变量；请先编辑 $ENV_FILE（参考 .env.example）后重跑"
    exit 2
  fi
fi
chown "$APP_USER":"$APP_USER" "$ENV_FILE"
chmod 600 "$ENV_FILE"

# 已有 .env 时只校正对外地址相关项，不覆盖密钥
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-}"
if [[ -z "$PUBLIC_BASE_URL" ]]; then
  # 入口 NGINX 在别的机器终止 TLS 时，.env 里已经是 https；重跑安装不能被降级成 http
  EXISTING_BASE="$(grep -E '^PUBLIC_BASE_URL=' "$ENV_FILE" 2>/dev/null | head -n1 | cut -d= -f2- || true)"
  if [[ "$ENABLE_TLS" == "1" || "$EXISTING_BASE" == https://* ]]; then
    PUBLIC_BASE_URL="https://$DOMAIN"
  else
    PUBLIC_BASE_URL="http://$DOMAIN"
  fi
fi
python3 - "$ENV_FILE" "$PUBLIC_BASE_URL" <<'PY'
import sys
path, base = sys.argv[1], sys.argv[2]
wanted = {
    "PUBLIC_BASE_URL": base,
    "FEISHU_OAUTH_REDIRECT_URI": base.rstrip("/") + "/auth/feishu/callback",
    "WEB_AUTH_MODE": "feishu",
    "EXECUTOR_DRY_RUN": "false",
    "EXECUTOR_DIRECTORY_REFRESH_HOURS": "6",
}
lines = []
seen = set()
with open(path, encoding="utf-8") as fh:
    for line in fh.read().splitlines():
        key = line.split("=", 1)[0].strip()
        if key in wanted:
            lines.append("%s=%s" % (key, wanted[key]))
            seen.add(key)
        else:
            lines.append(line)
for key, value in wanted.items():
    if key not in seen:
        lines.append("%s=%s" % (key, value))
with open(path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
PY
chown "$APP_USER":"$APP_USER" "$ENV_FILE"
chmod 600 "$ENV_FILE"

# ---------- 4.5 后台管理员（/admin/login 独立入口） ----------
log "配置后台管理员登录（/admin/login）"
env_get() {
  "$PYTHON_BIN" - "$ENV_FILE" "$1" <<'PY'
import sys
path, key = sys.argv[1], sys.argv[2]
try:
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith(key + "="):
                print(line.split("=", 1)[1].rstrip("\n"))
                break
except OSError:
    pass
PY
}
env_set() {
  "$PYTHON_BIN" - "$ENV_FILE" "$@" <<'PY'
import sys
path = sys.argv[1]
updates = {}
for item in sys.argv[2:]:
    key, value = item.split("=", 1)
    updates[key] = value
lines, seen = [], set()
try:
    with open(path, encoding="utf-8") as fh:
        for line in fh.read().splitlines():
            key = line.split("=", 1)[0].strip() if "=" in line else ""
            if key in updates:
                lines.append("%s=%s" % (key, updates[key]))
                seen.add(key)
            else:
                lines.append(line)
except OSError:
    pass
for key, value in updates.items():
    if key not in seen:
        lines.append("%s=%s" % (key, value))
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
PY
}
CURRENT_ADMIN_HASH="$(env_get ADMIN_PASSWORD_HASH)"
CURRENT_ADMIN_USER="$(env_get ADMIN_USERNAME)"
if [[ -z "$ADMIN_USERNAME_EXPLICIT" && -n "$CURRENT_ADMIN_USER" ]]; then
  ADMIN_USERNAME="$CURRENT_ADMIN_USER"
fi
NEW_ADMIN_HASH=""
if [[ -z "$CURRENT_ADMIN_HASH" ]]; then
  if [[ -n "${ADMIN_PASSWORD_HASH:-}" ]]; then
    NEW_ADMIN_HASH="$ADMIN_PASSWORD_HASH"
  elif [[ -n "${ADMIN_PASSWORD:-}" ]]; then
    NEW_ADMIN_HASH="$(printf '%s\n' "$ADMIN_PASSWORD" | PYTHONPATH="$APP_DIR/src" \
      "$APP_DIR/.venv/bin/python" -m executor.cli admin-password --stdin)"
    log "已根据 ADMIN_PASSWORD 生成后台管理员密码哈希"
  elif [[ -t 0 ]]; then
    echo "后台管理（/admin/login）需要独立账号，与飞书登录无关。"
    read -rp "后台管理员用户名 [${ADMIN_USERNAME}]: " input_admin_user
    ADMIN_USERNAME="${input_admin_user:-$ADMIN_USERNAME}"
    while true; do
      read -rsp "后台管理员密码（至少 8 位）: " input_admin_pw; echo
      read -rsp "再次输入后台管理员密码: " input_admin_pw2; echo
      if [[ ${#input_admin_pw} -lt 8 ]]; then
        echo "密码至少 8 位，请重试"
        continue
      fi
      if [[ "$input_admin_pw" != "$input_admin_pw2" ]]; then
        echo "两次输入不一致，请重试"
        continue
      fi
      break
    done
    NEW_ADMIN_HASH="$(printf '%s\n' "$input_admin_pw" | PYTHONPATH="$APP_DIR/src" \
      "$APP_DIR/.venv/bin/python" -m executor.cli admin-password --stdin)"
    unset input_admin_pw input_admin_pw2
    log "已生成后台管理员密码哈希"
  else
    warn "未设置 ADMIN_PASSWORD_HASH / ADMIN_PASSWORD，后台 /admin/login 暂不可用。"
    warn "可执行：printf '你的密码' | PYTHONPATH=$APP_DIR/src $APP_DIR/.venv/bin/python -m executor.cli admin-password --stdin"
    warn "把输出的哈希写入 $ENV_FILE 的 ADMIN_PASSWORD_HASH= 后 systemctl restart finebi-web"
  fi
fi
ENV_UPDATES=("ADMIN_USERNAME=$ADMIN_USERNAME")
if [[ -n "$NEW_ADMIN_HASH" ]]; then
  ENV_UPDATES+=("ADMIN_PASSWORD_HASH=$NEW_ADMIN_HASH")
fi
if [[ -z "$CURRENT_ADMIN_HASH" && -n "$NEW_ADMIN_HASH" ]] || [[ -n "$CURRENT_ADMIN_HASH" ]]; then
  env_set "${ENV_UPDATES[@]}"
fi
chown "$APP_USER":"$APP_USER" "$ENV_FILE" 2>/dev/null || true
chmod 600 "$ENV_FILE"
if [[ -n "$(env_get ADMIN_PASSWORD_HASH)" ]]; then
  log "后台管理员账号：$ADMIN_USERNAME（入口 $PUBLIC_BASE_URL/admin/login）"
else
  warn "后台管理员密码未配置，部署完成后需手工补 ADMIN_PASSWORD_HASH 并重启服务"
fi

# ---------- 5. systemd ----------
log "安装 systemd 服务"
install -m 0644 "$APP_DIR/deploy/systemd/finebi-web.service" /etc/systemd/system/finebi-web.service
install -m 0644 "$APP_DIR/deploy/systemd/finebi-directory-refresh.service" /etc/systemd/system/finebi-directory-refresh.service
install -m 0644 "$APP_DIR/deploy/systemd/finebi-directory-refresh.timer" /etc/systemd/system/finebi-directory-refresh.timer
install -m 0644 "$APP_DIR/deploy/systemd/finebi-contacts-refresh.service" /etc/systemd/system/finebi-contacts-refresh.service
install -m 0644 "$APP_DIR/deploy/systemd/finebi-contacts-refresh.timer" /etc/systemd/system/finebi-contacts-refresh.timer
install -m 0644 "$APP_DIR/deploy/systemd/finebi-membership-refresh.service" /etc/systemd/system/finebi-membership-refresh.service
install -m 0644 "$APP_DIR/deploy/systemd/finebi-membership-refresh.timer" /etc/systemd/system/finebi-membership-refresh.timer
sed -i "s#/opt/finebi-feishu#$APP_DIR#g" /etc/systemd/system/finebi-web.service \
  /etc/systemd/system/finebi-directory-refresh.service \
  /etc/systemd/system/finebi-contacts-refresh.service \
  /etc/systemd/system/finebi-membership-refresh.service
sed -i "s/^User=finebi$/User=$APP_USER/; s/^Group=finebi$/Group=$APP_USER/" /etc/systemd/system/finebi-web.service
sed -i "s/^User=finebi$/User=$APP_USER/; s/^Group=finebi$/Group=$APP_USER/" /etc/systemd/system/finebi-directory-refresh.service
sed -i "s/^User=finebi$/User=$APP_USER/; s/^Group=finebi$/Group=$APP_USER/" /etc/systemd/system/finebi-contacts-refresh.service
sed -i "s/^User=finebi$/User=$APP_USER/; s/^Group=finebi$/Group=$APP_USER/" /etc/systemd/system/finebi-membership-refresh.service
systemctl daemon-reload
systemctl enable finebi-web.service >/dev/null
systemctl restart finebi-web.service
systemctl enable finebi-directory-refresh.timer >/dev/null
systemctl restart finebi-directory-refresh.timer
systemctl enable finebi-contacts-refresh.timer >/dev/null
systemctl restart finebi-contacts-refresh.timer
systemctl enable finebi-membership-refresh.timer >/dev/null
systemctl restart finebi-membership-refresh.timer

# ---------- 6. NGINX ----------
if [[ "$INSTALL_NGINX" == "1" ]]; then
  if ! command -v nginx >/dev/null 2>&1; then
    log "安装 NGINX"
    if command -v apt-get >/dev/null 2>&1; then
      apt-get update -y && apt-get install -y nginx
    elif command -v dnf >/dev/null 2>&1; then
      dnf install -y nginx
    elif command -v yum >/dev/null 2>&1; then
      yum install -y nginx
    else
      warn "未识别的包管理器，请手工安装 NGINX 后重跑"
    fi
  fi
  if command -v nginx >/dev/null 2>&1; then
    log "写入 NGINX 配置：$DOMAIN"
    install -m 0644 "$APP_DIR/deploy/nginx/finebi-feishu.conf" /etc/nginx/conf.d/finebi-feishu.conf
    sed -i "s/__DOMAIN__/$DOMAIN/g" /etc/nginx/conf.d/finebi-feishu.conf
    nginx -t
    systemctl enable nginx >/dev/null 2>&1 || true
    systemctl reload nginx 2>/dev/null || systemctl restart nginx
  fi
fi

# ---------- 7. 首次刷新 + 健康检查 ----------
log "首次刷新目录/角色/部门快照（失败不阻塞部署）"
if command -v sudo >/dev/null 2>&1; then
  sudo -u "$APP_USER" env PYTHONPATH="$APP_DIR/src" \
    "$APP_DIR/.venv/bin/python" -m executor.cli refresh-directory \
    >> "$APP_DIR/data/directory_refresh.log" 2>&1 || warn "首次刷新失败，请检查 .env / FineBI 连通性后执行 systemctl start finebi-directory-refresh.service"
else
  runuser -u "$APP_USER" -- env PYTHONPATH="$APP_DIR/src" \
    "$APP_DIR/.venv/bin/python" -m executor.cli refresh-directory \
    >> "$APP_DIR/data/directory_refresh.log" 2>&1 || warn "首次刷新失败，请检查 .env / FineBI 连通性后执行 systemctl start finebi-directory-refresh.service"
fi

log "首次同步飞书通讯录快照（失败不阻塞部署，定时任务会重试）"
if command -v sudo >/dev/null 2>&1; then
  sudo -u "$APP_USER" env PYTHONPATH="$APP_DIR/src" \
    "$APP_DIR/.venv/bin/python" -m executor.cli sync-contacts \
    >> "$APP_DIR/data/contacts_refresh.log" 2>&1 \
    || warn "首次通讯录同步失败，请检查 .env / 飞书权限后执行 systemctl start finebi-contacts-refresh.service"
else
  runuser -u "$APP_USER" -- env PYTHONPATH="$APP_DIR/src" \
    "$APP_DIR/.venv/bin/python" -m executor.cli sync-contacts \
    >> "$APP_DIR/data/contacts_refresh.log" 2>&1 \
    || warn "首次通讯录同步失败，请检查 .env / 飞书权限后执行 systemctl start finebi-contacts-refresh.service"
fi

log "等待 Web 服务健康检查"
for i in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:18080/health" >/dev/null 2>&1; then
    curl -fsS "http://127.0.0.1:18080/health"; echo
    break
  fi
  sleep 1
  if [[ "$i" == "20" ]]; then
    warn "健康检查未通过，查看：journalctl -u finebi-web -n 100 --no-pager"
  fi
done

# ---------- 8. TLS ----------
if [[ "$ENABLE_TLS" == "1" ]]; then
  log "申请 HTTPS 证书（certbot --nginx）"
  if ! command -v certbot >/dev/null 2>&1; then
    if command -v apt-get >/dev/null 2>&1; then
      apt-get install -y certbot python3-certbot-nginx
    elif command -v dnf >/dev/null 2>&1; then
      dnf install -y certbot python3-certbot-nginx
    elif command -v yum >/dev/null 2>&1; then
      yum install -y certbot python3-certbot-nginx
    fi
  fi
  if command -v certbot >/dev/null 2>&1; then
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$CERTBOT_EMAIL" --redirect \
      || warn "certbot 失败：请确认域名解析、80/443 端口放行，或手工配置证书"
    systemctl reload nginx 2>/dev/null || true
  else
    warn "certbot 未安装，跳过 HTTPS；可手工配置证书后 reload nginx"
  fi
fi

# ---------- 9. 汇总 ----------
log "部署完成"
cat <<EOF

应用目录：$APP_DIR
运行用户：$APP_USER
对外地址：$PUBLIC_BASE_URL
Feishu OAuth 回调：$PUBLIC_BASE_URL/auth/feishu/callback
（请在飞书开放平台把该回调加入重定向 URL 白名单）
后台管理入口：$PUBLIC_BASE_URL/admin/login
（用户名：$ADMIN_USERNAME；密码为部署时设置，未配置哈希则不可用）

常用命令：
  systemctl status finebi-web
  systemctl status finebi-directory-refresh.timer
  systemctl start finebi-directory-refresh.service   # 立即刷新目录/角色/部门
  journalctl -u finebi-web -n 200 --no-pager
  journalctl -u finebi-directory-refresh -n 200 --no-pager
  cat $APP_DIR/data/directory_status.json

注意：
  1) NGINX 必须把应用代理在根路径（独立域名/子域名），不要挂 /finebi/ 子路径；
  2) 防火墙放行 80/443，FineBI/飞书出站按客户网络策略放行；
  3) 修改 .env 后：systemctl restart finebi-web；
  4) 目录/角色/部门每 6 小时刷新，页面顶部会显示上次/下次时间；
  5) 后台管理是独立入口 /admin/login（用户名密码），与飞书登录互不影响；
     改密码：printf '新密码' | PYTHONPATH=$APP_DIR/src $APP_DIR/.venv/bin/python -m executor.cli admin-password --stdin
     把输出的哈希替换 $APP_DIR/.env 的 ADMIN_PASSWORD_HASH 后重启服务。
EOF
