# -*- coding: utf-8 -*-
"""飞书通讯录快照收集：根部门分页 + 递归部门分页 + 去重 + 统计。

网页后台不再实时遍历通讯录（120 个部门要一分钟）；
由定时任务（或手动「从飞书通讯录同步」）调用本模块，把结果写进本地 mapping。
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


def write_status(path: str, ok: bool, total: int = 0, synced: int = 0,
                 stats: Optional[Dict[str, Any]] = None, error: str = "") -> None:
    """写通讯录同步状态文件，后台展示上次同步时间/人数。"""
    from ..models import now_iso
    payload = {"ok": bool(ok), "last_refresh": now_iso(), "total": int(total or 0),
               "synced": int(synced or 0), "error": str(error or ""),
               "stats": stats or {}}
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def collect_contact_users(feishu, page_size: int = 50,
                          page_delay: float = 0.1,
                          max_pages: int = 200) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """拉取全量飞书通讯录用户，返回 (users, stats)。"""
    items: List[Dict[str, Any]] = []
    seen = set()
    stats: Dict[str, Any] = {"root": 0, "department_users": 0, "departments": 0,
                             "pages": 0, "dept_error": ""}

    def absorb(users: List[Dict[str, Any]]) -> None:
        for item in users or []:
            open_id = str((item or {}).get("open_id") or "")
            if not open_id or open_id in seen:
                continue
            seen.add(open_id)
            items.append(item)

    def fetch_users(fetcher, *args) -> None:
        page_token = ""
        for _ in range(max_pages):
            resp = fetcher(*args, page_size=page_size, page_token=page_token)
            data = (resp or {}).get("data") or {}
            absorb(data.get("items") or [])
            stats["pages"] += 1
            page_token = str(data.get("page_token") or "")
            if not data.get("has_more") or not page_token:
                break
            if page_delay:
                time.sleep(page_delay)

    fetch_users(feishu.list_contact_users)
    stats["root"] = len(items)

    departments: List[Dict[str, Any]] = []
    try:
        page_token = ""
        for _ in range(max_pages):
            resp = feishu.list_departments(page_token=page_token)
            data = (resp or {}).get("data") or {}
            departments.extend(data.get("items") or [])
            stats["pages"] += 1
            page_token = str(data.get("page_token") or "")
            if not data.get("has_more") or not page_token:
                break
            if page_delay:
                time.sleep(page_delay)
    except Exception as exc:  # noqa: BLE001
        stats["dept_error"] = "部门列表读取失败：%s" % exc
        LOGGER.warning("飞书部门列表读取失败：%s", exc)

    before = len(items)
    for dept in departments:
        dept_id = str(dept.get("open_department_id")
                      or dept.get("department_id") or "")
        if not dept_id or dept_id == "0":
            continue
        try:
            fetch_users(feishu.list_department_users, dept_id)
        except Exception as exc:  # noqa: BLE001
            if not stats["dept_error"]:
                stats["dept_error"] = "部门 %s 用户读取失败：%s" % (dept_id, exc)
            LOGGER.warning("飞书部门 %s 用户读取失败：%s", dept_id, exc)
    stats["department_users"] = len(items) - before
    stats["departments"] = len(departments)
    stats["total"] = len(items)
    return items, stats
