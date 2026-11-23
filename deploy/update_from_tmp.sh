#!/usr/bin/env bash
# 从 /tmp 上传的部署包更新应用：保留 .env / config.json / data，只覆盖代码和部署文件。
#
# 用法（root）：
#   1) 把 finebi-feishu-configured-*.zip 上传到 /tmp
#   2) sudo bash /data/finebi-feishu/deploy/update_from_tmp.sh
#   或指定包路径：sudo bash deploy/update_from_tmp.sh /tmp/xxx.zip
set -euo pipefail

APP_DIR="${APP_DIR:-/data/finebi-feishu}"
APP_USER="${APP_USER:-finebi}"
DOMAIN="${DOMAIN:-finebi-app.example.com}"

ZIP="${1:-}"
if [[ -z "$ZIP" ]]; then
  ZIP="$(ls -t /tmp/finebi-feishu-configured-*.zip 2>/dev/null | head -n1 || true)"
fi
if [[ -z "$ZIP" || ! -f "$ZIP" ]]; then
  echo "未找到部署包：请先上传 finebi-feishu-configured-*.zip 到 /tmp" >&2
  echo "或：sudo bash $0 /tmp/你的包.zip" >&2
  exit 2
fi
if [[ "$(id -u)" != "0" ]]; then
  echo "请用 root 运行：sudo bash $0" >&2
  exit 1
fi
if [[ ! -d "$APP_DIR" ]]; then
  echo "应用目录不存在：$APP_DIR" >&2
  exit 3
fi

echo "[update] 使用部署包：$ZIP"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
if ! command -v unzip >/dev/null 2>&1; then
  echo "缺少 unzip，请先安装：apt-get install -y unzip / yum install -y unzip" >&2
  exit 4
fi
unzip -q "$ZIP" -d "$TMP_DIR"
SRC="$TMP_DIR/finebi-feishu"
if [[ ! -d "$SRC" ]]; then
  echo "包结构不符合预期：缺少 finebi-feishu/ 目录" >&2
  exit 5
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
echo "[update] 备份 .env / config.json / 台账数据库到 $APP_DIR/_backup/$STAMP"
mkdir -p "$APP_DIR/_backup/$STAMP"
for item in .env config/config.json data/executor.db data/membership_options.json \
            data/contacts_status.json data/directory_status.json; do
  if [[ -f "$APP_DIR/$item" ]]; then
    mkdir -p "$APP_DIR/_backup/$STAMP/$(dirname "$item")"
    cp -a "$APP_DIR/$item" "$APP_DIR/_backup/$STAMP/$item"
  fi
done

# 合并部署包 .env 里新增的配置键（只补缺失，不覆盖已有值/密码）
if [[ -f "$SRC/.env" && -f "$APP_DIR/.env" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in ''|'#'*) continue ;; esac
    key="${line%%=*}"
    [[ -z "$key" ]] && continue
    if ! grep -q "^${key}=" "$APP_DIR/.env"; then
      printf '\n%s\n' "$line" >> "$APP_DIR/.env"
      echo "[update] 补充新配置项：$key"
    fi
  done < "$SRC/.env"
  chown "$APP_USER:$APP_USER" "$APP_DIR/.env" 2>/dev/null || true
  chmod 600 "$APP_DIR/.env"
fi

echo "[update] 同步代码（不覆盖 .env / config.json / data）"
tar -C "$SRC" \
  --exclude='./.env' \
  --exclude='./config/config.json' \
  --exclude='./data' \
  -cf - . | tar -C "$APP_DIR" -xf -

chown -R "$APP_USER:$APP_USER" "$APP_DIR" 2>/dev/null || true
chmod 750 "$APP_DIR"
# 修复 zip 解压丢失的目录执行位
find "$APP_DIR" -type d ! -perm -u+x -exec chmod u+x {} + 2>/dev/null || true

echo "[update] 执行安装脚本（保留 .env，安装/更新 systemd 服务）"
cd "$APP_DIR"
bash deploy/install.sh --domain "$DOMAIN" --app-dir "$APP_DIR" --no-nginx

echo
echo "[update] 完成。建议检查："
echo "  systemctl status finebi-web --no-pager | head -6"
echo "  systemctl status finebi-contacts-refresh.timer --no-pager"
echo "  cat $APP_DIR/data/contacts_status.json"
