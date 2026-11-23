"""启动 Web 审批：python -m executor.web --host 127.0.0.1 --port 8080"""
from __future__ import annotations

import argparse
import logging


def main() -> int:
    parser = argparse.ArgumentParser(prog="executor.web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--env", default=".env")
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--forwarded-allow-ips", default="127.0.0.1",
                        help="信任哪些代理的 X-Forwarded-* 头；NGINX 同机部署用 127.0.0.1")
    parser.add_argument("--no-proxy-headers", action="store_true",
                        help="不信任代理头（仅本地直连调试时使用）")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("需要安装 Web 依赖：pip install fastapi uvicorn jinja2 python-multipart")
        return 2
    from ..config import Settings
    from .app import create_app
    settings = Settings.load(args.env, args.config)
    level = getattr(logging, str(settings.log_level or "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    uvicorn.run(create_app(settings), host=args.host, port=args.port,
                proxy_headers=not args.no_proxy_headers,
                forwarded_allow_ips=args.forwarded_allow_ips)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
