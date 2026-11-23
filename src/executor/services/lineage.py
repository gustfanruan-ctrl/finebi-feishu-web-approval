"""仪表板依赖数据集（组件数据）血缘反查。

FineBI 没有“仪表板 → 数据集”的直查接口，只有数据集维度的血缘：
``GET /v3/bi/table/usage?tables=[...]`` 返回每个数据集的 ``usage``（引用了它的
仪表板）以及 ``sonTables``（由它派生的自助数据集，子节点里同样带 ``usage``）。

因此以公共数据目录的数据集为起点批量查询、递归 ``sonTables``，把
“数据集 → 仪表板”反转成“仪表板 → 公共数据集”，得到每台仪表板在展示数据时
需要“组件数据（biData）”权限的数据集清单。

只保留公共数据目录里的数据集；自助数据集不单独授权（有仪表板权限即可查看）。
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Iterable, List, Optional

from ..models import now_iso

LOGGER = logging.getLogger(__name__)

DEFAULT_DEPS_JSON = "data/dashboard_deps.json"
BATCH_SIZE = 40
MAX_DEPTH = 6
MAX_TABLES = 2000


def atomic_write_json(path: str, data: Any) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, path)


def load_dashboard_deps(path: str = DEFAULT_DEPS_JSON) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_dashboard_deps(data: Dict[str, Any],
                         path: str = DEFAULT_DEPS_JSON) -> None:
    atomic_write_json(path, data)


def dashboard_datasets(deps: Dict[str, Any],
                       dashboard_id: str) -> List[Dict[str, str]]:
    """从快照取某台仪表板的公共数据集依赖（去重、按名称排序）。"""
    row = ((deps or {}).get("dashboards") or {}).get(str(dashboard_id or ""))
    if not isinstance(row, dict):
        return []
    result: List[Dict[str, str]] = []
    seen = set()
    for item in row.get("datasets") or []:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("resource_id") or "")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        result.append({"resource_id": rid,
                       "name": str(item.get("name") or rid),
                       "path": str(item.get("path") or "")})
    result.sort(key=lambda x: x["name"])
    return result


def _collect_usages(node: Any, out: List[Dict[str, str]],
                    depth: int = 0) -> None:
    """递归收集节点自身与所有派生数据集上的仪表板 usage。"""
    if not isinstance(node, dict) or depth > MAX_DEPTH:
        return
    for usage in node.get("usage") or []:
        if isinstance(usage, dict) and usage.get("id"):
            out.append({"id": str(usage["id"]),
                        "name": str(usage.get("name") or "")})
    for key in ("sonTables", "tables"):
        for child in node.get(key) or []:
            _collect_usages(child, out, depth + 1)


def build_dashboard_deps(finebi: Any,
                         tables: Iterable[Dict[str, Any]],
                         max_tables: int = MAX_TABLES) -> Optional[Dict[str, Any]]:
    """构建“仪表板 → 依赖公共数据集”快照。

    ``tables`` 为 catalog 中的数据集行（``resource_type == "table"``），需要
    ``resource_id``（数据集原始名）与 ``name``（转义名）。``finebi`` 为空或
    不支持血缘接口时返回 ``None``，调用方跳过即可。
    """
    if finebi is None or not hasattr(finebi, "get_table_usage"):
        return None
    public: Dict[str, Dict[str, str]] = {}
    for row in tables or []:
        if not isinstance(row, dict):
            continue
        if row.get("resource_type") and str(row.get("resource_type")) != "table":
            continue
        rid = str(row.get("resource_id") or "")
        if not rid:
            continue
        public[rid] = {"resource_id": rid,
                       "name": str(row.get("name") or rid),
                       "path": str(row.get("path") or "")}
    names = sorted(public)[: max(1, int(max_tables))]
    if not names:
        return {"refreshed_at": now_iso(),
                "summary": {"datasets": 0, "dashboards": 0, "errors": []},
                "dashboards": {}}

    by_table: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []
    for start in range(0, len(names), BATCH_SIZE):
        chunk = names[start:start + BATCH_SIZE]
        try:
            resp = finebi.get_table_usage(chunk)
        except Exception as exc:  # noqa: BLE001 - 单批失败不影响其他批
            LOGGER.warning("数据集血缘批量查询失败（%d 个）：%s", len(chunk), exc)
            errors.append("血缘查询失败：%s" % exc)
            continue
        for item in (resp or {}).get("data") or []:
            if not isinstance(item, dict) or not item.get("status"):
                continue
            data = item.get("data")
            if not isinstance(data, dict):
                continue
            table_name = str(data.get("tableName") or "")
            if table_name:
                by_table[table_name] = data

    dashboards: Dict[str, Dict[str, Any]] = {}
    for table_name, node in by_table.items():
        usages: List[Dict[str, str]] = []
        _collect_usages(node, usages)
        for usage in usages:
            dash_id = usage["id"]
            entry = dashboards.setdefault(dash_id, {
                "name": usage.get("name") or dash_id, "datasets": {}})
            entry["datasets"][table_name] = public.get(table_name) or {
                "resource_id": table_name, "name": table_name, "path": ""}

    result_dashboards: Dict[str, Any] = {}
    for dash_id, entry in dashboards.items():
        datasets = sorted(entry["datasets"].values(),
                          key=lambda x: (x.get("name") or "", x["resource_id"]))
        result_dashboards[dash_id] = {
            "name": entry.get("name") or dash_id,
            "datasets": datasets,
        }
    return {
        "refreshed_at": now_iso(),
        "summary": {"datasets": len(public),
                    "matched_datasets": len(by_table),
                    "dashboards": len(result_dashboards),
                    "errors": errors},
        "dashboards": result_dashboards,
    }
