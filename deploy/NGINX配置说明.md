# NGINX 配置说明（FineBI × 飞书 Web 审批）

> 生产环境不使用 ngrok。ngrok 只用于本地 MVP 联调；正式部署时
> `PUBLIC_BASE_URL` / `FEISHU_OAUTH_REDIRECT_URI` 必须是客户自己的域名。

## 1. 配置装在哪里

一键部署脚本会把模板安装到：

```text
/etc/nginx/conf.d/finebi-feishu.conf
```

应用本身只监听 `127.0.0.1:18080`，对外由 NGINX 反向代理。

## 2. 在服务器上查看配置

```bash
# 看本应用配置
sudo cat /etc/nginx/conf.d/finebi-feishu.conf

# 看 NGINX 实际加载的全部配置（含 include 后的内容）
sudo nginx -T | less

# 只筛本应用 server 段
sudo nginx -T | sed -n '/server_name .*<域名>/,/^}/p'

# 校验语法（改完必须执行）
sudo nginx -t

# 看服务与端口
systemctl status nginx --no-pager
ss -lntp | grep -E ':80|:443|:18080'
```

## 3. 配置模板逐段说明

```nginx
upstream finebi_feishu_app {
    server 127.0.0.1:18080;   # 应用只监听本机，不能填公网 IP
    keepalive 16;
}

server {
    listen 80;
    server_name __DOMAIN__;  # 改成客户域名，例如 finebi-app.example.com

    # 健康检查单独放行
    location = /health {
        proxy_pass http://finebi_feishu_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }

    location / {
        proxy_pass http://finebi_feishu_app;
        proxy_http_version 1.1;

        # 必须保留 Host 和 X-Forwarded-*：
        # 飞书 OAuth 回调、页面跳转、Cookie Secure 都依赖对外地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Connection "";

        proxy_connect_timeout 10s;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
        client_max_body_size 10m;
    }
}
```

注意：

- 必须挂在**根路径** `/`；应用页面里是 `/requests/...`、`/auth/feishu/callback` 绝对路径，
  不要配成 `https://域名/finebi/` 子路径；
- 不要改 `proxy_pass` 成 `https://127.0.0.1:18080`（应用是 HTTP）；
- 应用没有 WebSocket/SSE/大文件上传，不需要额外 Upgrade 配置；
- 如果前面还有客户自己的负载均衡/SLB，必须同样透传 `Host`、`X-Forwarded-Proto`，
  否则飞书回调地址会变成 http 或错误域名。

## 4. 换成客户域名 + HTTPS

### 4.1 先确认 DNS

```bash
nslookup <域名>
# 或 dig +short <域名>
```

A 记录必须指向这台服务器的公网 IP；80/443 入站放行。

### 4.2 方式 A：重新跑一键脚本（推荐）

```bash
cd /opt/finebi-feishu
sudo bash deploy/install.sh --domain <域名> --tls --email <运维邮箱>
```

脚本会自动：

1. 替换 NGINX 模板里的 `__DOMAIN__`；
2. 更新 `.env` 的 `PUBLIC_BASE_URL` 和 `FEISHU_OAUTH_REDIRECT_URI`；
3. 用 certbot 申请证书并配置 80→443；
4. 重载 NGINX、重启 `finebi-web`。

### 4.3 方式 B：手工改

```bash
sudo vi /etc/nginx/conf.d/finebi-feishu.conf
# 把 server_name __DOMAIN__; 改成 server_name <域名>;

sudo vi /opt/finebi-feishu/.env
# PUBLIC_BASE_URL=https://<域名>
# FEISHU_OAUTH_REDIRECT_URI=https://<域名>/auth/feishu/callback
# WEB_AUTH_MODE=feishu
# EXECUTOR_DRY_RUN=false

sudo nginx -t && sudo systemctl reload nginx
sudo systemctl restart finebi-web
```

TLS 证书二选一：

```bash
# certbot 自动改 NGINX
sudo certbot --nginx -d <域名> --redirect

# 或手工在 server 块加：
# listen 443 ssl http2;
# ssl_certificate     /path/fullchain.pem;
# ssl_certificate_key /path/privkey.pem;
```

### 4.4 飞书开放平台同步

把下面这个地址加入飞书应用「安全设置 → 重定向 URL」白名单：

```text
https://<域名>/auth/feishu/callback
```

必须与 `.env` 的 `FEISHU_OAUTH_REDIRECT_URI` **逐字一致**（https、无末尾 `/`）。

### 4.5 客户已有域名时，怎么加监听

先确认域名指向的是这台服务器：

```bash
dig +short <客户域名>
curl -I http://<客户域名>/
```

再查看现有 NGINX 是否已经监听了 80/443、有没有同域名的 server：

```bash
sudo nginx -T | grep -nE 'listen|server_name|ssl_certificate'
ls -l /etc/nginx/conf.d/ /etc/nginx/sites-enabled/ 2>/dev/null
sudo ss -lntp | grep -E ':80|:443'
```

分两种情况：

**A. 新域名/子域名（推荐，最不容易冲突）**

例如客户把 `finebi-app.example.com` 解析到本机，直接新增独立配置：

```bash
sudo tee /etc/nginx/conf.d/finebi-feishu.conf >/dev/null <<'EOF'
upstream finebi_feishu_app {
    server 127.0.0.1:18080;
    keepalive 16;
}

server {
    listen 80;
    server_name finebi-app.example.com;

    location = /health {
        proxy_pass http://finebi_feishu_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }

    location / {
        proxy_pass http://finebi_feishu_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Connection "";
        proxy_read_timeout 120s;
    }
}
EOF
sudo nginx -t && sudo systemctl reload nginx
```

然后二选一加 HTTPS：

```bash
# 自动申请证书并加 443 监听
sudo certbot --nginx -d finebi-app.example.com --redirect
```

或复用客户已有证书（证书必须覆盖该域名）：

```nginx
server {
    listen 443 ssl http2;
    server_name finebi-app.example.com;

    ssl_certificate     /etc/nginx/ssl/example.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com/privkey.pem;

    location / {
        proxy_pass http://finebi_feishu_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name finebi-app.example.com;
    return 301 https://$host$request_uri;
}
```

**B. 客户要把应用挂在已存在的同一域名下**

先看该域名是否已有 `server` 块：

```bash
sudo nginx -T | grep -B3 -A8 'server_name <客户域名>'
```

- 如果该域名只用于这个应用：把上面的 `server` 内容合并进它的 `server` 块，保留原 `listen`/证书配置，只替换 `location /`；
- 如果该域名已有别的网站：**不要直接覆盖**。建议改用子域名（情况 A）；
- 如果前面还有客户自己的 SLB/负载均衡：在 SLB 上转发到本机 80/443，并确保透传 `Host` 和 `X-Forwarded-Proto https`；NGINX 这里按实际入口配置。

改完必须：

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart finebi-web   # 如果改了 .env
```

最后把 `https://<客户域名>/auth/feishu/callback` 加到飞书应用重定向 URL 白名单。

## 5. 改完后的验证

```bash
# 本机应用
curl -fsS http://127.0.0.1:18080/health

# NGINX 到应用（带 Host 模拟域名）
curl -fsS -H "Host: <域名>" http://127.0.0.1/health

# 对外域名
curl -I https://<域名>/
curl -fsS https://<域名>/health

# 浏览器
# https://<域名>/login  → 应跳转飞书授权，回调后正常进入
```

## 6. 常见问题

| 现象 | 检查 |
|---|---|
| 502 Bad Gateway | `systemctl status finebi-web`；`curl 127.0.0.1:18080/health` |
| 打开域名是默认 NGINX 页 | `server_name` 是否写对；是否有其它默认 server 抢占 |
| 飞书登录报 redirect_uri 不匹配 | 飞书后台、`.env`、实际访问域名三者逐字一致 |
| 登录后又跳回登录页 | `PUBLIC_BASE_URL` 是否还是旧 ngrok/旧域名；重启 `finebi-web` |
| HTTPS 证书不受信 | certbot 是否成功；域名 DNS 是否指向本机 |
| 页面样式/跳转异常 | 是否挂在了子路径；必须用独立域名根路径 |
