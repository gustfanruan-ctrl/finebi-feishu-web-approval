# Linux 部署（NGINX + systemd + 目录定时刷新）

Windows 计划任务 `FineBI-DirectoryRefresh` 只用于本地 MVP 环境（Interactive only，
关机/未登录不补跑）。正式部署到客户 Linux 用本目录的脚本：NGINX 反向代理 + systemd
托管 Web 服务 + 每 6 小时刷新目录/角色/部门。

## 0. 一键部署（推荐）

把部署包解压到任意目录（或直接 `git clone`），以 root 执行：

```bash
sudo bash deploy/install.sh --domain finebi.example.com
# 需要 HTTPS：
sudo bash deploy/install.sh --domain finebi.example.com --tls --email ops@example.com
```

也可以从环境变量读取 FineBI/飞书密钥，做到完全非交互：

```bash
sudo FINEBI_BASE_URL=http://10.0.0.10:1080 \
     FINEBI_CLIENT_ID=xxx FINEBI_SECRET=xxx \
     FEISHU_APP_ID=xxx FEISHU_APP_SECRET=xxx \
     bash deploy/install.sh --domain finebi.example.com --tls --email ops@example.com
```

脚本会完成：

1. 同步代码到 `/opt/finebi-feishu`（`--app-dir` 可改），创建运行用户 `finebi`；
2. 创建 venv 并安装 `requirements.txt`；
3. 生成/校正 `.env`（已有 `.env` 不会被覆盖密钥；首次会交互式询问）；
4. 安装并启动 `finebi-web.service`（只监听 127.0.0.1:18080）；
5. 安装并启用 `finebi-directory-refresh.timer`（每 6 小时）；
6. 安装 NGINX 配置（`deploy/nginx/finebi-feishu.conf`，域名自动替换）；
7. 首次刷新目录/角色/部门快照并做 `/health` 健康检查；
8. `--tls` 时用 certbot 申请证书并配置 80→443 跳转。

可重复执行：代码会更新，`.env`、`data/`、数据库不会被覆盖；适合升级。

## 1. NGINX 适配说明

详细配置逐段说明、查看/修改命令、换客户域名与 HTTPS 步骤见
[`deploy/NGINX配置说明.md`](NGINX配置说明.md)。

代码侧不需要改业务逻辑，但部署时必须注意：

- **必须挂在根路径**：页面里是 `/requests/...`、`/auth/feishu/callback` 等绝对路径，
  用独立域名/子域名代理到 `/`，不要挂 `https://example.com/finebi/` 子路径；
- **保留 Host 和 X-Forwarded 头**：`deploy/nginx/finebi-feishu.conf` 已配置
  `Host` / `X-Real-IP` / `X-Forwarded-For` / `X-Forwarded-Proto`；
- **uvicorn 信任代理头**：`finebi-web.service` 使用
  `--forwarded-allow-ips 127.0.0.1`，只信任同机 NGINX；
- **对外地址**：`.env` 的 `PUBLIC_BASE_URL` 和 `FEISHU_OAUTH_REDIRECT_URI` 必须是
  NGINX 对外地址（HTTPS），否则飞书登录回调/通知链接会错；安装脚本会自动校正；
- **Cookie Secure**：`PUBLIC_BASE_URL` 是 `https://` 时登录 Cookie 自动带 Secure，
  所以 TLS 要在 NGINX 终止；
- 应用没有 WebSocket/SSE/大文件上传，NGINX 默认代理即可；`/health` 已单独放行；
- 飞书开放平台需把 `https://<域名>/auth/feishu/callback` 加入重定向 URL 白名单；
- 防火墙放行 80/443（TLS）以及客户网络到 FineBI/飞书的出站。

## 2. 目录/角色/部门定时刷新

核心命令与平台无关：

```bash
cd /opt/finebi-feishu
PYTHONPATH=src .venv/bin/python -m executor.cli refresh-directory
```

刷新内容：数据目录、仪表板目录、角色、部门 → `data/catalog.json` / `catalog.csv` /
`membership_options.json` / `directory_status.json`。每次重新调用 FineBI 接口，
后期新增的资源会在下一轮刷新后自动出现；Web 后台也提供「立即刷新」。

### 2.1 systemd timer（推荐）

文件：

- `deploy/systemd/finebi-directory-refresh.service`
- `deploy/systemd/finebi-directory-refresh.timer`

一键脚本已自动安装。手工安装：

```bash
sudo cp deploy/systemd/finebi-directory-refresh.* /etc/systemd/system/
sudo sed -i 's#/opt/finebi-feishu#/srv/finebi-feishu#g' \
  /etc/systemd/system/finebi-directory-refresh.service
sudo systemctl daemon-reload
sudo systemctl enable --now finebi-directory-refresh.timer
```

验证：

```bash
systemctl list-timers | grep finebi
sudo systemctl start finebi-directory-refresh.service
journalctl -u finebi-directory-refresh.service -n 100 --no-pager
cat data/directory_status.json
```

说明：

- `OnCalendar=*-*-* 00/6:00:00` 每 6 小时（00/06/12/18）；
- `Persistent=true`：关机/重启期间错过的任务在开机后补跑一次；
- `RandomizedDelaySec=300`：避免整点与其它任务撞车；
- 改周期时同时改 timer 的 `OnCalendar` 与 `.env` 的
  `EXECUTOR_DIRECTORY_REFRESH_HOURS`（后者只影响页面“下次刷新”展示）。

### 2.2 cron（没有 systemd 时）

`deploy/cron/finebi-directory-refresh` 是 `/etc/cron.d/` 格式：

```bash
sudo cp deploy/cron/finebi-directory-refresh /etc/cron.d/
sudo chmod 644 /etc/cron.d/finebi-directory-refresh
# 按实际路径/用户修改文件内容后重启 cron
sudo systemctl restart cron 2>/dev/null || sudo service cron restart
```

cron 不会补跑关机期间错过的任务；对补跑有要求时优先 systemd timer。

## 3. Web 服务（systemd）

`deploy/systemd/finebi-web.service` 只监听 `127.0.0.1:18080`，由 NGINX 对外。
一键脚本已安装；手工方式：

```bash
sudo cp deploy/systemd/finebi-web.service /etc/systemd/system/
sudo sed -i 's#/opt/finebi-feishu#/srv/finebi-feishu#g' /etc/systemd/system/finebi-web.service
sudo systemctl daemon-reload
sudo systemctl enable --now finebi-web
systemctl status finebi-web --no-pager
```

### 3.1 后台管理独立登录（/admin/login）

后台管理是独立入口，用户名/密码登录，与飞书登录完全隔离：

- 普通用户：飞书登录后进入申请页，页面里没有任何后台入口；
- 管理员：直接打开 `https://<域名>/admin/login`，用 `.env` 的 `ADMIN_USERNAME`
  加部署时设置的密码登录；
- 飞书侧管理员（角色 admin）也不能进 `/admin`，只能用独立账号；
- 后台账号 id 前缀 `admin:`，不会出现在用户列表/Owner 下拉里。

首次部署 `install.sh` 会交互式设置密码（至少 8 位），也可非交互：

```bash
sudo ADMIN_USERNAME=admin ADMIN_PASSWORD='强密码' \
  bash deploy/install.sh --domain finebi.example.com
# 已有哈希时（pbkdf2_sha256$迭代数$salt$hash）：
sudo ADMIN_PASSWORD_HASH='pbkdf2_sha256$390000$...' bash deploy/install.sh --domain ...
```

改密码：

```bash
cd /opt/finebi-feishu
printf '新密码' | PYTHONPATH=src .venv/bin/python -m executor.cli admin-password --stdin
# 把输出替换 .env 里的 ADMIN_PASSWORD_HASH= 后
sudo systemctl restart finebi-web
```

密码用 PBKDF2-SHA256（390000 次迭代）哈希，`.env` 不保存明文。

## 4. 权限与路径

- Web 服务与刷新任务使用同一系统用户（默认 `finebi`），保证 `data/` 快照可读写；
- `.env` 放在 WorkingDirectory（服务文件里的 `WorkingDirectory`）下，CLI 会读取；
- Python 用部署 venv：`/opt/finebi-feishu/.venv/bin/python`；
- 升级：重新执行 `install.sh`（或覆盖代码后 `systemctl restart finebi-web`）；
- 手动刷新与定时任务共用文件锁，不会并发。

## 5. 账号与权限要求

| 账号 | 权限 | 说明 |
|---|---|---|
| 部署/运维账号（SSH） | root 或 sudo | 运行 `install.sh` 需要 root：建用户、装包、写 systemd/NGINX、certbot |
| 运行账号 `finebi` | 无 sudo、无登录 shell | 只运行 Web 服务和刷新任务；拥有 `/opt/finebi-feishu` 和 `data/`；只监听 `127.0.0.1:18080` |
| 文件权限 | `APP_DIR` 750 `finebi:finebi`；`.env` 600；systemd/NGINX 配置 root 644 | 不要用 root 跑 Web；`finebi` 不要加入 sudoers |
| FineDB 只读账号 | 仅 `SELECT` | 用于飞书映射/行权限枚举；不建表、不写数据 |
| FineBI 开放平台凭证 | 平台管理员/权限管理权限 | `clientId/secret` 对应 API 调用者，需能授予/回收权限；与飞书 App 凭证分开 |
| 网络入站 | 80/443（TLS） | 18080 只绑定本机，不对公网开放 |
| 网络出站 | FineBI 端口、`open.feishu.cn:443`、FineDB:3306、软件源/Let's Encrypt | 按客户网络策略放行 |

> 如果客户禁止 root SSH：给部署账号 sudo 权限，安装时用 `sudo bash deploy/install.sh ...`；
> 日常运维只需 sudo 执行 `systemctl`/`journalctl`/`nginx -t`，运行账号 `finebi` 保持无特权。

## 6. 验证清单

1. `systemctl status finebi-web`、`curl http://127.0.0.1:18080/health` 正常；
2. 浏览器打开 `https://<域名>`，飞书登录成功；
3. 普通用户页面没有任何“后台管理”入口（tab、按钮、链接都没有）；
4. 浏览器打开 `https://<域名>/admin/login`，用独立管理员账号能登录 `/admin`；
   飞书登录的账号访问 `/admin` 会被踢回 `/admin/login`；
5. 页面顶部显示“每 6 小时自动刷新/上次/下次”，无错误；
6. `systemctl list-timers` 看到下次刷新时间；
7. 新增数据集/仪表板/部门/角色后，等下一轮刷新或后台点「立即刷新」，下拉框出现新资源；
8. `journalctl` 或 `data/directory_refresh.log` 无持续报错。

## 7. 打包部署包

在开发机项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package_deploy.ps1
```

输出 `dist/finebi-feishu-deploy-<时间>.zip`（以及 `.tar.gz`），不包含 `.env`、
数据库、本地 catalog/快照、`tools/ngrok.exe` 等本地资产。

- 域名更换/旧链接失效处理：见 [域名更换操作手册.md](域名更换操作手册.md)。
