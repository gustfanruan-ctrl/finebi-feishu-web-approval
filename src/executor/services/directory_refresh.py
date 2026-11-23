"""目录/角色/部门快照定时刷新。

每 6 小时滚动执行一次（Windows 计划任务 / 管理员手动触发），把 FineBI 当前的
数据目录、仪表板目录、角色、部门写成前端选择框使用的快照文件：

- ``data/catalog.json`` / ``data/catalog.csv``：数据文件夹、数据集、仪表板目录；
- ``data/membership_options.json``：角色与部门（含完整路径）；
- ``data/directory_status.json``：上次/下次刷新时间、数量、错误，供前端说明。

快照每次重新调用 FineBI 接口，**不写死任何资源 ID**：后期新增的数据集、仪表板、
部门、角色都会在下一轮刷新后自动出现在下拉框里；刷新失败时保留上一版快照。
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models import now_iso
from .catalog import CatalogExporter
from .lineage import (DEFAULT_DEPS_JSON, build_dashboard_deps,
                      write_dashboard_deps)

LOGGER = logging.getLogger(__name__)

DEFAULT_INTERVAL_HOURS = 6
DEFAULT_CATALOG_JSON = "data/catalog.json"
DEFAULT_CATALOG_CSV = "data/catalog.csv"
DEFAULT_MEMBERSHIP_JSON = "data/membership_options.json"
DEFAULT_STATUS_JSON = "data/directory_status.json"
DEFAULT_LOCK_PATH = "data/.directory_refresh.lock"
LOCK_STALE_SECONDS = 1800
DEPARTMENT_MAX_NODES = 500


def atomic_write_json(path: str, data: Any) -> None:
    """先写临时文件再替换，避免前端读到半截 JSON。"""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, path)


def read_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def collect_roles(platform: Any) -> List[Dict[str, Any]]:
    """读取 FineBI 全部角色（不写死角色名，后期新增角色自动纳入）。"""
    resp = platform.query_roles(role="", exact=False)
    payload = (resp or {}).get("data")
    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("list") or []
    else:
        items = payload or []
    roles: List[Dict[str, Any]] = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("roleName") or "").strip()
        if name and name not in seen:
            seen.add(name)
            roles.append({"name": name,
                          "description": str(item.get("description") or "")})
    roles.sort(key=lambda row: row["name"])
    return roles


def collect_departments(platform: Any,
                        max_nodes: int = DEPARTMENT_MAX_NODES) -> List[Dict[str, Any]]:
    """读取部门树（``GET /v3/department?department=[]``）。

    实测根查询一次返回整棵扁平树（含子部门与岗位节点），节点靠 id/pId 关联；
    按 pId 回溯完整路径，岗位节点（type=position）不参与成员关系申请。
    """
    resp = platform.query_departments([])
    items = (resp or {}).get("data") or []
    if isinstance(items, dict):
        items = items.get("items") or []
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and item.get("id"):
            by_id[str(item["id"])] = item

    def path_of(node: Dict[str, Any], seen: set) -> List[str]:
        name = str(node.get("name") or "").strip()
        parent_id = str(node.get("pId") or "")
        if not parent_id or parent_id not in by_id or parent_id in seen:
            return [name] if name else []
        return path_of(by_id[parent_id], seen | {parent_id}) + ([name] if name else [])

    result: List[Dict[str, Any]] = []
    seen_paths: set = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        if str(item.get("type") or "department") != "department":
            continue
        path = path_of(item, set())
        if not path:
            continue
        key = json.dumps(path, ensure_ascii=False)
        if key in seen_paths:
            continue
        seen_paths.add(key)
        result.append({"name": path[-1], "path": path, "full_path": "/".join(path)})
        if len(result) >= max_nodes:
            break
    result.sort(key=lambda row: row["full_path"])
    return result


def collect_membership_options(platform: Any) -> Dict[str, Any]:
    """角色 + 部门快照；后期新增的角色/部门会在下一轮刷新自动出现。"""
    roles = collect_roles(platform)
    departments = collect_departments(platform)
    return {"roles": roles, "departments": departments,
            "generated_at": now_iso()}


def _acquire_lock(lock_path: str) -> Optional[int]:
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode("ascii"))
        return fd
    except FileExistsError:
        try:
            age = time.time() - os.path.getmtime(lock_path)
        except OSError:
            age = 0
        if age > LOCK_STALE_SECONDS:
            try:
                os.remove(lock_path)
            except OSError:
                return None
            return _acquire_lock(lock_path)
        return None


def _release_lock(lock_path: str, fd: Optional[int]) -> None:
    if fd is not None:
        try:
            os.close(fd)
        except OSError:
            pass
    try:
        os.remove(lock_path)
    except OSError:
        pass


def _next_refresh(now: datetime, interval_hours: int) -> str:
    """按固定 6 小时槽位计算下次刷新（与 Windows 计划任务 00/06/12/18 对齐）。

    例如 15:45 刷新后，下次是 18:00；18:00 刷新后，下次是次日 00:00。
    """
    interval = max(1, int(interval_hours or DEFAULT_INTERVAL_HOURS))
    slot = now.replace(minute=0, second=0, microsecond=0)
    add_hours = interval - (slot.hour % interval)
    return (slot + timedelta(hours=add_hours)).isoformat(timespec="seconds")


def refresh_directory(ctx: Any, interval_hours: int = DEFAULT_INTERVAL_HOURS,
                      catalog_json: str = DEFAULT_CATALOG_JSON,
                      catalog_csv: str = DEFAULT_CATALOG_CSV,
                      membership_json: str = DEFAULT_MEMBERSHIP_JSON,
                      status_json: str = DEFAULT_STATUS_JSON,
                      lock_path: str = DEFAULT_LOCK_PATH,
                      deps_json: str = DEFAULT_DEPS_JSON,
                      exporter: Any = None) -> Dict[str, Any]:
    """刷新目录与角色/部门快照，返回状态字典（同时写 status_json）。

    - 任一来源失败时保留该来源的上一版快照，错误写入状态文件；
    - 用文件锁避免定时任务与管理员手动刷新同时执行；
    - 每次重新调用 FineBI 接口，后期新增资源自动纳入。
    """
    lock_fd = _acquire_lock(lock_path)
    if lock_fd is None:
        previous = read_json(status_json) or {}
        return {"ok": False, "running": True,
                "message": "已有目录刷新任务在执行，请稍后重试",
                "last_refresh": previous.get("last_refresh", ""),
                "interval_hours": interval_hours, "errors": []}
    started = time.time()
    now = datetime.now().astimezone()
    previous = read_json(status_json) or {}
    atomic_write_json(status_json, {
        "running": True, "started_at": now.isoformat(timespec="seconds"),
        "last_refresh": previous.get("last_refresh", ""),
        "last_success": previous.get("last_success", ""),
        "interval_hours": interval_hours,
        "next_refresh": previous.get("next_refresh", ""),
        "catalog": previous.get("catalog") or {},
        "membership": previous.get("membership") or {},
        "dependencies": previous.get("dependencies") or {},
        "errors": previous.get("errors") or [],
    })
    errors: List[str] = []
    catalog_summary: Dict[str, Any] = {}
    deps_summary: Dict[str, Any] = {}
    membership_counts: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None
    try:
        try:
            export = exporter or CatalogExporter(ctx.finebi, ctx.platform)
            result = export.export()
            CatalogExporter.to_json(result, catalog_json)
            CatalogExporter.to_csv(result, catalog_csv)
            catalog_summary = dict(result.get("summary") or {})
        except Exception as exc:  # noqa: BLE001 - 保留上一版快照
            LOGGER.exception("刷新数据/仪表板目录失败")
            errors.append("数据/仪表板目录刷新失败：%s" % exc)
        if result is not None:
            try:
                deps = build_dashboard_deps(
                    getattr(ctx, "finebi", None),
                    [row for row in (result.get("rows") or [])
                     if str((row or {}).get("resource_type") or "") == "table"])
                if deps is not None:
                    write_dashboard_deps(deps, deps_json)
                    deps_summary = dict(deps.get("summary") or {})
            except Exception as exc:  # noqa: BLE001 - 依赖失败不影响目录快照
                LOGGER.exception("刷新仪表板依赖失败")
                errors.append("仪表板依赖刷新失败：%s" % exc)
        try:
            options = collect_membership_options(ctx.platform)
            atomic_write_json(membership_json, options)
            membership_counts = {"roles": len(options.get("roles") or []),
                                 "departments": len(options.get("departments") or [])}
        except Exception as exc:  # noqa: BLE001 - 保留上一版快照
            LOGGER.exception("刷新角色/部门快照失败")
            errors.append("角色/部门刷新失败：%s" % exc)
        ok = not errors
        status = {
            "ok": ok,
            "running": False,
            "last_refresh": now.isoformat(timespec="seconds"),
            "last_success": now.isoformat(timespec="seconds") if ok
            else previous.get("last_success", ""),
            "interval_hours": interval_hours,
            "next_refresh": _next_refresh(now, interval_hours),
            "duration_seconds": round(time.time() - started, 1),
            "catalog": {"summary": catalog_summary, "path": catalog_json},
            "membership": {**membership_counts, "path": membership_json},
            "dependencies": {**deps_summary, "path": deps_json},
            "errors": errors,
        }
        atomic_write_json(status_json, status)
        return status
    finally:
        _release_lock(lock_path, lock_fd)


def read_directory_status(status_json: str = DEFAULT_STATUS_JSON,
                          interval_hours: int = DEFAULT_INTERVAL_HOURS) -> Dict[str, Any]:
    """读取刷新状态；文件缺失时返回默认值，供页面展示。"""
    status = read_json(status_json) or {}
    if not status:
        return {"ok": None, "running": False, "last_refresh": "",
                "next_refresh": "", "interval_hours": interval_hours,
                "catalog": {}, "membership": {}, "errors": [],
                "message": "尚未执行过目录刷新"}
    status.setdefault("interval_hours", interval_hours)
    status.setdefault("errors", [])
    if status.get("running"):
        started_at = str(status.get("started_at") or "")
        try:
            started = datetime.fromisoformat(started_at)
            if (datetime.now().astimezone() - started).total_seconds() > LOCK_STALE_SECONDS:
                status["running"] = False
                status["message"] = "上次刷新未正常结束，等待下一轮自动重试"
        except ValueError:
            pass
    return status
