"""资源目录导出：给飞书表单下拉/多维表格资源目录提供数据。

接口依据：
- 数据文件夹树：``GET /v3/bi/conf/groups``（只含文件夹）
- 文件夹下的数据集：``GET /v3/bi/conf/pack/info?packs=[...]`` 的 ``tableList``
- 数据集字段：``GET /v3/bi/table/info?tables=[...]`` 的 ``fields[]``
- 仪表板目录：``GET /v3/entry/tree?device=pc``，筛选 ``entryType=201``，取
  ``text`` / ``templateId`` / ``parentNames``
- entry 的 ``templateId`` 不是 biReportId（模板认证接口不认），用
  ``GET /v3/bi/publish/info?templateIds=[...]`` 的 ``resources[itemType=1].id``
  换成真实 biReportId；发布信息缺失时再退回 ``dash/user/all`` 按名称唯一匹配。

飞书表单不能直连内网 FineBI，推荐把导出的 CSV 导入多维表格，再用
“引用多维表格”控件做下拉；执行器按资源 ID 授权。
"""
from __future__ import annotations

import csv
import json
import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

CSV_HEADERS = ["资源类型", "资源名称", "资源路径", "资源ID", "父级ID", "字段列表"]

# publish/info 单次最多查多少个 templateId（批量中任一 ID 失效整批报 BATCH，
# 因此失败时退回逐个查询，避免一条过期发布拖垮整个目录导出）
PUBLISH_BATCH_SIZE = 20
BATCH_SIZE = 50


def _data(resp: Any) -> Any:
    if isinstance(resp, dict):
        return resp.get("data")
    return None


def _batch(items: List[Any], size: int = BATCH_SIZE) -> List[List[Any]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


class CatalogExporter:
    def __init__(self, finebi, platform=None):
        self.finebi = finebi
        self.platform = platform

    # ---------- 数据目录 ----------
    def _folders(self) -> List[Dict[str, Any]]:
        tree = _data(self.finebi.list_folders()) or []
        rows: List[Dict[str, Any]] = []

        def walk(nodes: List[Dict[str, Any]], parent_id: str, parent_path: str) -> None:
            for node in nodes or []:
                if not isinstance(node, dict):
                    continue
                fid = str(node.get("id") or "")
                name = str(node.get("name") or "")
                path = (parent_path + "/" + name).strip("/") if parent_path else name
                rows.append({"resource_type": "folder", "name": name, "path": path,
                             "resource_id": fid, "parent_id": parent_id,
                             "fields": []})
                walk(node.get("packs") or [], fid, path)

        walk(tree, "", "")
        return rows

    def _datasets(self, folders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ids = [f["resource_id"] for f in folders if f["resource_id"]]
        info: Dict[str, Dict[str, Any]] = {}
        for chunk in _batch(ids):
            resp = self.finebi.get_folder_info(chunk)
            for item in _data(resp) or []:
                if isinstance(item, dict) and item.get("status") and isinstance(item.get("data"), dict):
                    info[str(item["data"].get("id"))] = item["data"]

        table_names: List[str] = []
        rows: List[Dict[str, Any]] = []
        for folder in folders:
            data = info.get(folder["resource_id"])
            if not data:
                continue
            for table in data.get("tableList") or []:
                if not isinstance(table, dict):
                    continue
                name = str(table.get("name") or "")
                transfer = str(table.get("transferName") or name)
                rows.append({"resource_type": "table", "name": transfer,
                             "path": folder["path"] + "/" + transfer,
                             "resource_id": name, "parent_id": folder["resource_id"],
                             "fields": []})
                table_names.append(name)

        fields: Dict[str, List[Dict[str, str]]] = {}
        for chunk in _batch(table_names):
            resp = self.finebi.get_tables_info(chunk)
            for item in _data(resp) or []:
                if isinstance(item, dict) and item.get("status") and isinstance(item.get("data"), dict):
                    table = item["data"]
                    fields[str(table.get("tableName"))] = [
                        {"fieldId": str(f.get("fieldId") or ""),
                         "name": str(f.get("transferName") or f.get("name") or "")}
                        for f in table.get("fields") or [] if isinstance(f, dict)]
        for row in rows:
            row["fields"] = fields.get(row["resource_id"], [])
        return rows

    # ---------- 仪表板目录 ----------
    @staticmethod
    def _publish_resources(resp: Any) -> Dict[str, str]:
        """解析 publish/info 响应：templateId → 仪表板 biReportId（resources.itemType=1）。"""
        mapping: Dict[str, str] = {}
        for item in _data(resp) or []:
            if not isinstance(item, dict) or not item.get("status"):
                continue
            data = item.get("data")
            if not isinstance(data, dict):
                continue
            template_id = str(data.get("templateId") or "")
            if not template_id:
                continue
            for resource in data.get("resources") or []:
                if (isinstance(resource, dict) and resource.get("itemType") == 1
                        and resource.get("id")):
                    mapping[template_id] = str(resource["id"])
                    break
        return mapping

    def _publish_map(self, template_ids: List[str]) -> Dict[str, str]:
        """批量解析 templateId → biReportId。

        批量查询里任一 templateId 已失效会让整批返回 status=false（客户端抛 BATCH），
        因此失败后逐个重试，过期节点只记日志、不阻断目录导出。
        """
        mapping: Dict[str, str] = {}
        if not template_ids or not hasattr(self.finebi, "get_publish_info"):
            return mapping
        for chunk in _batch(list(template_ids), PUBLISH_BATCH_SIZE):
            try:
                mapping.update(self._publish_resources(self.finebi.get_publish_info(chunk)))
                continue
            except Exception as exc:  # noqa: BLE001 - 见 docstring
                LOGGER.warning("publish/info 批量查询失败，改为逐个查询：%s", exc)
            for template_id in chunk:
                try:
                    mapping.update(self._publish_resources(
                        self.finebi.get_publish_info([template_id])))
                except Exception as exc:  # noqa: BLE001 - 过期发布节点跳过
                    LOGGER.warning("publish/info 查询失败（templateId=%s）：%s",
                                   template_id, exc)
        return mapping

    def _dashboards(self) -> List[Dict[str, Any]]:
        """仪表板目录：以平台 entry/tree 为准（含文件夹路径与 entryId），
        再把 entry 的 ``templateId`` 经 ``publish/info`` 换成模板认证所需的
        biReportId；发布信息缺失时才退回 ``dash/user/all`` 按名称唯一匹配。

        entry/tree 的 templateId 不是 biReportId（权限接口不认）。两条路径都拿不到
        biReportId 的条目仍保留，用 entryId 走目录权限授权。
        """
        rows: List[Dict[str, Any]] = []
        nodes: List[Dict[str, Any]] = []
        if self.platform:
            try:
                tree = _data(self.platform.get_entry_tree("pc")) or []
                nodes = [n for n in tree if isinstance(n, dict)]
            except Exception as exc:  # noqa: BLE001 - entry/tree 不可用时目录不完整
                LOGGER.warning("entry/tree 查询失败，仪表板目录将不完整：%s", exc)
                nodes = []
        node_by_id = {str(n.get("id")): n for n in nodes}
        template_ids: List[str] = []
        for node in nodes:
            if node.get("entryType") != 201:
                continue
            name = str(node.get("text") or "")
            parents = [str(p) for p in (node.get("parentNames") or [])]
            path = "/".join(parents + [name]) if parents else name
            # 目录权限按 FineBI 层级生效：只授直接父目录，避免把整棵目录树暴露给用户
            parent = str(node.get("pId") or "")
            ancestors: List[str] = []
            if parent and parent != "decision-directory-root" and parent in node_by_id:
                ancestors = [parent]
            template_id = str(node.get("templateId") or "")
            if template_id and template_id not in template_ids:
                template_ids.append(template_id)
            rows.append({"resource_type": "dashboard", "name": name, "path": path,
                         "resource_id": "", "entry_id": str(node.get("id") or ""),
                         "template_id": template_id, "parent_id": parent,
                         "entry_ancestors": ancestors, "fields": [],
                         "match": "", "source": "entry/tree"})

        by_template = self._publish_map(template_ids)
        for row in rows:
            rid = by_template.get(row["template_id"]) or ""
            if rid:
                row["resource_id"] = rid
                row["match"] = "publish/info"

        # publish/info 没覆盖到的条目：退回 dash/user/all 名称唯一匹配（best effort）
        reports: List[Any] = []
        try:
            for item in _data(self.finebi.list_user_dashboards()) or []:
                if not isinstance(item, dict):
                    continue
                rid = str(item.get("biReportId") or item.get("dashId") or "")
                name = str(item.get("biReportName") or item.get("dashName") or rid)
                if rid and name:
                    reports.append((name, rid))
        except Exception as exc:  # noqa: BLE001 - 补名映射失败不影响 entry 结构
            LOGGER.warning("dash/user/all 查询失败，仪表板名称兜底缺失：%s", exc)
            reports = []
        by_name: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            if not row["resource_id"]:
                by_name.setdefault(row["name"], []).append(row)
        used = {row["resource_id"] for row in rows if row["resource_id"]}
        for name, rid in reports:
            candidates = by_name.get(name) or []
            if len(candidates) == 1 and rid not in used:
                candidates[0]["resource_id"] = rid
                candidates[0]["match"] = "name"
                used.add(rid)
        for name, rid in reports:
            if rid in used:
                continue
            rows.append({"resource_type": "dashboard", "name": name, "path": name,
                         "resource_id": rid, "entry_id": "",
                         "template_id": "", "parent_id": "",
                         "entry_ancestors": [], "fields": [],
                         "match": "dash/user/all", "source": "dash/user/all"})
            used.add(rid)
        return rows

    def export(self) -> Dict[str, Any]:
        folders = self._folders()
        tables = self._datasets(folders)
        dashboards = self._dashboards()
        rows = folders + tables + dashboards
        return {
            "summary": {"folders": len(folders), "tables": len(tables),
                        "dashboards": len(dashboards), "total": len(rows)},
            "rows": rows,
        }

    # ---------- 输出 ----------
    @staticmethod
    def to_json(result: Dict[str, Any], path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)

    @staticmethod
    def to_csv(result: Dict[str, Any], path: str) -> None:
        with open(path, "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(CSV_HEADERS)
            for row in result.get("rows") or []:
                fields = ";".join("%s:%s" % (f.get("fieldId"), f.get("name"))
                                  for f in row.get("fields") or [])
                writer.writerow([row.get("resource_type"), row.get("name"),
                                 row.get("path"), row.get("resource_id"),
                                 row.get("parent_id"), fields])
