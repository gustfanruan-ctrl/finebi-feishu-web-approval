r"""命令行入口。

用法（项目根目录）：
    $env:PYTHONPATH = "$PWD\src"
    python -m executor.cli check
    python -m executor.cli grant --file examples\grant-folder.json
    python -m executor.cli revoke --user 10086
    python -m executor.cli expire
    python -m executor.cli offboard --user 10086 --accepter 10087
    python -m executor.cli poll
    python -m executor.cli serve --port 8080
"""
from __future__ import annotations

import argparse
import getpass
import json
import logging
import sys
from typing import Any, Dict

from .config import Settings
from .models import PermissionRequest
from .runtime import build


def _dump(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="executor", description="FineBI × 飞书 权限自动化执行器")
    parser.add_argument("--env", default=".env", help="环境变量文件路径")
    parser.add_argument("--config", default="config/config.json", help="策略配置文件路径")
    parser.add_argument("--log-level", default="", help="日志级别，默认读取配置")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check", help="校验配置与联调连通性")
    p.add_argument("--ping", action="store_true", help="调用 FineBI 接口探活")

    p = sub.add_parser("grant", help="执行一次授权")
    p.add_argument("--file", required=True, help="PermissionRequest JSON 文件")

    p = sub.add_parser("revoke", help="回收权限")
    p.add_argument("--ledger-id", default="", help="台账 ID")
    p.add_argument("--user", default="", help="按用户回收全部有效授权")
    p.add_argument("--reason", default="手动回收")

    p = sub.add_parser("expire", help="执行到期回收")
    p.add_argument("--no-jobs", action="store_true", help="不执行到期重试任务")

    p = sub.add_parser("offboard", help="离职/转岗回收")
    p.add_argument("--user", required=True)
    p.add_argument("--accepter", default="")

    p = sub.add_parser("poll", help="轮询审批实例并执行授权")
    p.add_argument("--since-hours", type=int, default=72)
    p.add_argument("--no-jobs", action="store_true", help="不执行到期重试任务")

    p = sub.add_parser("reconcile", help="台账与 FineBI 现状对账")
    p.add_argument("--limit", type=int, default=500)

    p = sub.add_parser("jobs", help="执行到期的重试/人工任务")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("catalog", help="导出数据目录/仪表板目录（供飞书下拉或 Bitable）")
    p.add_argument("--out", default="data/catalog.json")
    p.add_argument("--csv", default="data/catalog.csv")

    p = sub.add_parser("refresh-directory",
                       help="刷新数据/仪表板目录 + 角色/部门快照（定时任务用）")
    p.add_argument("--interval-hours", type=int, default=0,
                   help="刷新周期（小时），默认读 EXECUTOR_DIRECTORY_REFRESH_HOURS")
    p.add_argument("--catalog-json", default="data/catalog.json")
    p.add_argument("--catalog-csv", default="data/catalog.csv")
    p.add_argument("--membership-json", default="data/membership_options.json")
    p.add_argument("--status-json", default="data/directory_status.json")
    p.add_argument("--deps-json", default="data/dashboard_deps.json",
                   help="仪表板依赖数据集快照（组件数据连带授权用）")

    p = sub.add_parser("sync-contacts",
                       help="同步飞书通讯录到本地映射（定时任务用）")
    p.add_argument("--page-delay", type=float, default=0.1)
    p.add_argument("--status-json", default="data/contacts_status.json")

    p = sub.add_parser("sync-membership",
                       help="刷新用户角色/部门快照（定时任务用）")
    p.add_argument("--status-json", default="data/membership_sync_status.json")

    p = sub.add_parser("bitable-init",
                       help="初始化飞书多维表格「权限申请台账」字段")
    p.add_argument("--app-token", default="")
    p.add_argument("--table-id", default="")

    p = sub.add_parser("bitable-sync",
                       help="把历史申请补录到多维表格台账")
    p.add_argument("--limit", type=int, default=500)

    p = sub.add_parser("admin-password", help="生成后台管理员密码哈希（写入 ADMIN_PASSWORD_HASH）")
    p.add_argument("--password", default="", help="非交互传入密码（会出现在进程参数里，不推荐）")
    p.add_argument("--stdin", action="store_true", help="从 stdin 读一行密码（供脚本调用）")

    p = sub.add_parser("report", help="输出月度申请/授权/异常汇总")
    p.add_argument("--month", default="", help="YYYY-MM，默认本月")

    p = sub.add_parser("web", help="启动自建 Web 审批（需要 fastapi/uvicorn/jinja2）")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)

    p = sub.add_parser("serve", help="启动 HTTP 服务（需要 fastapi/uvicorn）")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.load(args.env, args.config)
    logging.basicConfig(
        level=getattr(logging, (args.log_level or settings.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s")

    if args.command == "check":
        info: Dict[str, Any] = {"settings": settings.summary(),
                                "resources": len(settings.resource_map)}
        if args.ping:
            ctx = build(settings)
            try:
                info["finebi_ping"] = ctx.finebi.list_folders()
            except Exception as exc:  # noqa: BLE001 - 探活失败要显示原因
                info["finebi_ping_error"] = str(exc)
        _dump(info)
        return 0

    if args.command == "web":
        try:
            import uvicorn
        except ImportError:
            print("需要安装 Web 依赖：pip install fastapi uvicorn jinja2 python-multipart", file=sys.stderr)
            return 2
        from .web.app import create_app
        uvicorn.run(create_app(settings), host=args.host, port=args.port)
        return 0

    if args.command == "serve":
        try:
            import uvicorn
        except ImportError:
            print("需要安装 fastapi/uvicorn：pip install -r requirements.txt", file=sys.stderr)
            return 2
        from .api.app import create_app
        uvicorn.run(create_app(settings), host=args.host, port=args.port)
        return 0

    ctx = build(settings)
    if args.command == "grant":
        with open(args.file, "r", encoding="utf-8") as fh:
            req = PermissionRequest.from_dict(json.load(fh))
        _dump(ctx.permission.grant(req).to_dict())
        return 0
    if args.command == "revoke":
        if args.ledger_id:
            rows = [r for r in ctx.storage.active_ledger() if r["id"] == args.ledger_id]
            if not rows:
                print("未找到台账：%s" % args.ledger_id, file=sys.stderr)
                return 1
            _dump(ctx.revoke.revoke_ledger(rows[0], args.reason))
            return 0
        if args.user:
            _dump({"results": ctx.revoke.revoke_user(args.user, args.reason)})
            return 0
        print("需要 --ledger-id 或 --user", file=sys.stderr)
        return 1
    if args.command == "expire":
        result = {"results": ctx.expire.run_once()}
        if not args.no_jobs:
            result["jobs"] = ctx.jobs.run_due()
        _dump(result)
        return 0
    if args.command == "offboard":
        _dump(ctx.offboard.offboard(args.user, args.accepter))
        return 0
    if args.command == "poll":
        ctx.poller.since_hours = args.since_hours
        result = ctx.poller.run_once()
        if not args.no_jobs:
            result["jobs"] = ctx.jobs.run_due()
        _dump(result)
        return 0
    if args.command == "reconcile":
        ctx.reconcile.limit = args.limit
        _dump({"diffs": ctx.reconcile.run()})
        return 0
    if args.command == "jobs":
        _dump(ctx.jobs.run_due(limit=args.limit))
        return 0
    if args.command == "catalog":
        from .services.catalog import CatalogExporter
        result = CatalogExporter(ctx.finebi, ctx.platform).export()
        CatalogExporter.to_json(result, args.out)
        CatalogExporter.to_csv(result, args.csv)
        _dump({"summary": result["summary"], "json": args.out, "csv": args.csv})
        return 0
    if args.command == "refresh-directory":
        from .services.directory_refresh import refresh_directory
        interval = args.interval_hours or settings.directory_refresh_hours
        status = refresh_directory(
            ctx, interval_hours=interval,
            catalog_json=args.catalog_json, catalog_csv=args.catalog_csv,
            membership_json=args.membership_json, status_json=args.status_json,
            deps_json=args.deps_json)
        _dump(status)
        return 0 if status.get("ok") else 1
    if args.command == "sync-contacts":
        from .web.contacts import collect_contact_users, write_status
        from .web.finedb import FineDB
        from .web.service import WebApprovalService
        finedb = FineDB(settings.fine_db_host, settings.fine_db_port,
                        settings.fine_db_user, settings.fine_db_password,
                        settings.fine_db_name)
        service = WebApprovalService(
            ctx.storage, ctx.permission, ctx.notifier, policy=settings.policy,
            public_base_url=settings.public_base_url, dry_run=settings.dry_run,
            platform=ctx.platform, offboard_service=ctx.offboard, finedb=finedb)
        try:
            items, stats = collect_contact_users(ctx.feishu,
                                                 page_delay=args.page_delay)
            count = service.sync_feishu_users(items) if items else 0
            write_status(args.status_json, ok=not stats.get("dept_error"),
                         total=len(items), synced=count, stats=stats,
                         error=str(stats.get("dept_error") or ""))
            _dump({"ok": not stats.get("dept_error"), "total": len(items),
                   "synced": count, "stats": stats})
            return 0 if not stats.get("dept_error") else 1
        except Exception as exc:  # noqa: BLE001
            write_status(args.status_json, ok=False, error=str(exc))
            print("通讯录同步失败：%s" % exc, file=sys.stderr)
            return 1
    if args.command == "sync-membership":
        from .web.contacts import write_status
        from .web.service import WebApprovalService
        service = WebApprovalService(
            ctx.storage, ctx.permission, ctx.notifier, policy=settings.policy,
            public_base_url=settings.public_base_url, dry_run=settings.dry_run,
            platform=ctx.platform, offboard_service=ctx.offboard)
        try:
            result = service.refresh_all_memberships()
            write_status(args.status_json, ok=bool(result.get("ok")),
                         total=int(result.get("total") or 0),
                         synced=int(result.get("synced") or 0),
                         error=str(result.get("errors") or ""))
            _dump(result)
            return 0 if result.get("ok") else 1
        except Exception as exc:  # noqa: BLE001
            write_status(args.status_json, ok=False, error=str(exc))
            print("角色/部门快照刷新失败：%s" % exc, file=sys.stderr)
            return 1
    if args.command == "bitable-init":
        from .web.bitable import BitableLedger
        app_token = args.app_token or settings.bitable_app_token
        table_id = (args.table_id or settings.bitable_request_table_id
                    or settings.bitable_ledger_table_id)
        ledger = BitableLedger(ctx.feishu, app_token, table_id,
                               dry_run=settings.dry_run)
        if not ledger.enabled():
            print("未配置多维表格 app_token/table_id（.env FEISHU_BITABLE_*)",
                  file=sys.stderr)
            return 2
        _dump(ledger.ensure_schema())
        return 0
    if args.command == "bitable-sync":
        from .web.bitable import BitableLedger
        from .web.service import WebApprovalService
        app_token = settings.bitable_app_token
        table_id = (settings.bitable_request_table_id
                    or settings.bitable_ledger_table_id)
        ledger = BitableLedger(ctx.feishu, app_token, table_id,
                               dry_run=settings.dry_run)
        if not ledger.enabled():
            print("未配置多维表格 app_token/table_id（.env FEISHU_BITABLE_*）",
                  file=sys.stderr)
            return 2
        _dump(ledger.ensure_schema())
        service = WebApprovalService(
            ctx.storage, ctx.permission, ctx.notifier, policy=settings.policy,
            public_base_url=settings.public_base_url, dry_run=settings.dry_run,
            platform=ctx.platform, offboard_service=ctx.offboard, bitable=ledger)
        rows = ctx.storage.conn.execute(
            "SELECT id FROM web_requests ORDER BY created_at DESC LIMIT ?",
            (args.limit,)).fetchall()
        synced = 0
        for row in rows:
            service._sync_bitable(row["id"], "历史补录")
            if ctx.storage.get_bitable_record_id(row["id"]):
                synced += 1
        print("历史申请补录完成：%d/%d 条" % (synced, len(rows)))
        return 0 if synced == len(rows) else 1
    if args.command == "admin-password":
        from .web.admin_auth import hash_password
        password = args.password
        if not password and args.stdin:
            password = sys.stdin.readline().rstrip("\n")
        if not password:
            password = getpass.getpass("后台管理员密码: ")
            confirm = getpass.getpass("再次输入: ")
            if password != confirm:
                print("两次输入的密码不一致")
                return 2
        if not password:
            print("密码不能为空")
            return 2
        print(hash_password(password))
        return 0
    if args.command == "report":
        _dump(ctx.report(args.month))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
