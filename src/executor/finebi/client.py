"""FineBI BI 权限接口（数据目录、行列权限、仪表板、协作、交接）。

接口前缀：/webroot/decision/sp/client/api
参考：docs/finebi/开放平台 FineBI接口（对外）.md（BI6.x(V3) 段）
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ..errors import ApiError
from ..http import HttpClient
from .paths import WRITE_PATHS

LOGGER = logging.getLogger(__name__)

API_ROOT = "/webroot/decision/sp/client/api"


class FineBIClient:
    def __init__(self, base_url: str, client_id: str, secret: str,
                 dec_user: Optional[str] = None, http: Optional[HttpClient] = None,
                 dry_run: bool = False):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.secret = secret
        self.dec_user = dec_user
        self.http = http or HttpClient()
        self.dry_run = dry_run

    # ---------- 基础请求 ----------
    def _call(self, method: str, path: str, body: Any = None,
              query: Optional[Dict[str, Any]] = None) -> Any:
        url = self.base_url + API_ROOT + path
        headers = {"clientId": self.client_id, "secret": self.secret}
        params = dict(query or {})
        if self.dec_user:
            params.setdefault("decUser", self.dec_user)
        if self.dry_run and method.upper() in ("POST", "PUT", "DELETE") and path in WRITE_PATHS:
            LOGGER.info("[DRY-RUN] %s %s body=%s", method, path, body)
            return {"dry_run": True, "method": method, "path": path}
        resp = self.http.request(method, url, headers=headers, json_body=body, params=params)
        self._assert_top_level(resp)
        self._assert_batch_status(resp)
        return resp

    @staticmethod
    def _assert_top_level(resp: Any) -> None:
        """处理顶层失败：{status:403, errorCode, errorMsg, traceId}。"""
        if not isinstance(resp, dict) or resp.get("dry_run"):
            return
        status = resp.get("status")
        if isinstance(status, int) and status >= 400:
            raise ApiError(status, str(resp.get("errorMsg") or resp.get("message") or resp), resp)
        if resp.get("errorCode") and "data" not in resp:
            raise ApiError(resp.get("errorCode"), str(resp.get("errorMsg") or resp), resp)

    @staticmethod
    def _assert_batch_status(resp: Any) -> None:
        if not isinstance(resp, dict):
            return
        data = resp.get("data")
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("status") is False:
                    raise ApiError("BATCH", str(item.get("errorMsg") or item), item)

    # ---------- 数据权限：文件夹（pack） ----------
    def set_folder_permission(self, user: str, pack_id: str, authority: Dict[str, bool]) -> Any:
        return self._call("POST", "/v3/bi/authority/pack/user",
                          [{"user": user, "packId": pack_id, "authority": authority}])

    def get_folder_permission(self, user: str, pack_id: str) -> Any:
        return self._call("POST", "/v3/bi/authority/pack/user/get",
                          [{"user": user, "packId": pack_id}])

    # ---------- 数据权限：数据集（table） ----------
    def set_table_permission(self, user: str, table_name: str, authority: Dict[str, bool]) -> Any:
        return self._call("POST", "/v3/bi/authority/table/user",
                          [{"user": user, "tableName": table_name, "authority": authority}])

    def get_table_permission(self, user: str, table_name: str) -> Any:
        return self._call("POST", "/v3/bi/authority/table/user/get",
                          [{"user": user, "tableName": table_name}])

    def get_table_permissions_user(self, user: str,
                                   table_names: List[str]) -> Any:
        """批量查询用户对多个数据集的数据权限（返回顺序与入参一致）。"""
        return self._call("POST", "/v3/bi/authority/table/user/get",
                          [{"user": user, "tableName": name}
                           for name in table_names])

    def get_folder_permissions_user(self, user: str,
                                    pack_ids: List[str]) -> Any:
        """批量查询用户对多个文件夹的目录权限。"""
        return self._call("POST", "/v3/bi/authority/pack/user/get",
                          [{"user": user, "packId": rid} for rid in pack_ids])

    # ---------- 列权限（field） ----------
    def set_field_permission(self, user: str, field_id: str, bi_data: bool = True) -> Any:
        return self._call("POST", "/v3/bi/authority/field/user",
                          [{"user": user, "fieldId": field_id, "authority": {"biData": bi_data}}])

    def get_field_permission(self, user: str, field_id: str) -> Any:
        return self._call("POST", "/v3/bi/authority/field/user/get",
                          [{"user": user, "fieldId": field_id}])

    # ---------- 行权限（全量覆盖，需合并） ----------
    def set_row_filter(self, user: str, table_name: str, row_filter: Dict[str, Any]) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/user",
                          [{"user": user, "tableName": table_name, "filter": row_filter}])

    def get_row_filter(self, user: str, table_name: str) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/user/get",
                          [{"user": user, "tableName": table_name}])

    # 行权限：按角色/部门/用户批量查询（审批页判断数据集是否配置了行权限/列权限）
    def get_row_filters_roles(self, roles: List[str], table_name: str) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/role/get",
                          [{"role": role, "tableName": table_name}
                           for role in roles])

    def get_row_filters_deposts(self, subjects: List[Dict[str, str]],
                                table_name: str) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/depost/get",
                          [{"department": item.get("department") or "",
                            "position": item.get("position") or "",
                            "tableName": table_name} for item in subjects])

    def get_row_filters_role(self, role: str, table_names: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/role/get",
                          [{"role": role, "tableName": name}
                           for name in table_names])

    def get_row_filters_depost(self, department: str, position: str,
                               table_names: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/depost/get",
                          [{"department": department,
                            "position": position or "",
                            "tableName": name} for name in table_names])

    def get_row_filters_users(self, users: List[str], table_name: str) -> Any:
        return self._call("POST", "/v3/bi/authority/row/filter/user/get",
                          [{"user": user, "tableName": table_name}
                           for user in users])

    # 角色/部门的数据权限、目录权限、模板认证（申请单辅助审批展示用）
    def get_folder_permissions_role(self, role: str, pack_ids: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/pack/role/get",
                          [{"role": role, "packId": rid} for rid in pack_ids])

    def get_table_permissions_role(self, role: str, table_names: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/table/role/get",
                          [{"role": role, "tableName": name} for name in table_names])

    def get_dashboard_auth_role(self, role: str,
                                bi_report_ids: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/dash/template/auth/role/get",
                          [{"role": role, "biReportId": rid}
                           for rid in bi_report_ids])

    def get_folder_permissions_depost(self, department: str, position: str,
                                      pack_ids: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/pack/depost/get",
                          [{"department": department, "position": position or "",
                            "packId": rid} for rid in pack_ids])

    def get_table_permissions_depost(self, department: str, position: str,
                                     table_names: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/table/depost/get",
                          [{"department": department, "position": position or "",
                            "tableName": name} for name in table_names])

    def get_dashboard_auth_depost(self, department: str, position: str,
                                  bi_report_ids: List[str]) -> Any:
        return self._call("POST", "/v3/bi/authority/dash/template/auth/depost/get",
                          [{"department": department, "position": position or "",
                            "biReportId": rid} for rid in bi_report_ids])

    # ---------- 仪表板 ----------
    def set_dashboard_template_auth(self, user: str, bi_report_id: str,
                                    view: bool, export: bool = False) -> Any:
        if export and not view:
            raise ValueError("导出权限必须同时开启查看权限")
        return self._call("POST", "/v3/bi/authority/dash/template/auth/user",
                          [{"user": user, "biReportId": bi_report_id,
                            "authority": {"view": view, "export": export}}])

    def get_dashboard_template_auth(self, user: str, bi_report_id: str) -> Any:
        return self._call("POST", "/v3/bi/authority/dash/template/auth/user/get",
                          [{"user": user, "biReportId": bi_report_id}])

    # ---------- 目录权限（entry，控制仪表板在目录中的可见/导出） ----------
    def set_entry_authority(self, user: str, entry_id: str,
                            authority: Dict[str, Any]) -> Any:
        return self._call("POST", "/v3/auth/user/entry",
                          [{"user": user, "entry": entry_id,
                            "authority": authority}])

    def get_entry_authority(self, user: str, entry_ids: List[str]) -> Any:
        return self._call("POST", "/v3/auth/user/entry/list",
                          {"user": user, "entries": list(entry_ids)})

    def set_publink_share(self, user: str, enabled: bool = True) -> Any:
        return self._call("POST", "/v3/bi/authority/dash/publink/user",
                          [{"user": user, "authority": {"biShareFun": enabled}}])

    def share_dashboard(self, users: List[str], bi_report_id: str) -> Any:
        return self._call("PUT", "/v3/bi/share/dash/user",
                          {"users": users, "biReport": bi_report_id, "authority": {"view": True}})

    def set_dashboard_data_permission(self, user: str, entry: str, bi_data: bool = True) -> Any:
        return self._call("POST", "/v3/bi/authority/dashboard/data/user/set",
                          [{"user": user, "entry": entry, "biData": bi_data}])

    # ---------- 主题协作 ----------
    def set_subject_cooperation(self, user: str, subject: str,
                                use: bool = True, edit: bool = False) -> Any:
        return self._call("PUT", "/v3/bi/cooperation/subject/user",
                          {"user": user, "subject": subject,
                           "authority": {"use": use, "edit": edit}})

    # ---------- 资源查询 ----------
    def list_folders(self) -> Any:
        return self._call("GET", "/v3/bi/conf/groups")

    def get_folder_info(self, packs: List[str]) -> Any:
        """文件夹详情：GET /v3/bi/conf/pack/info?packs=[]。

        注意：不带 /info 的 pack 查询路径是 DELETE 删除接口，禁止封装。
        """
        return self._call("GET", "/v3/bi/conf/pack/info",
                          query={"packs": json.dumps(packs, ensure_ascii=False)})

    def get_dashboard_info(self, bi_reports: List[str]) -> Any:
        """仪表板信息：GET /v3/bi/dash/info?biReports=[]。

        注意：不带 /info 的 dash 查询路径是 DELETE 删除接口，禁止封装。
        """
        return self._call("GET", "/v3/bi/dash/info",
                          query={"biReports": json.dumps(bi_reports, ensure_ascii=False)})

    def get_tables_info(self, table_names: List[str]) -> Any:
        return self._call("GET", "/v3/bi/table/info",
                          query={"tables": json.dumps(table_names, ensure_ascii=False)})

    def get_table_usage(self, table_names: List[str]) -> Any:
        """数据集血缘：返回 usage（引用该数据集的仪表板）与 sonTables（派生数据集）。"""
        return self._call("GET", "/v3/bi/table/usage",
                          query={"tables": json.dumps(table_names, ensure_ascii=False)})

    def get_publish_info(self, template_ids: List[str]) -> Any:
        """发布信息：GET /v3/bi/publish/info?templateIds=[...]。

        返回 ``data[].data.resources[]``，其中 ``itemType == 1`` 的资源 id 即
        仪表板 ID（biReportId），用于把平台目录 entry 的 ``templateId`` 映射到
        模板认证接口所需的 ``biReportId``（模板认证接口不认 templateId）。
        """
        return self._call("GET", "/v3/bi/publish/info",
                          query={"templateIds": json.dumps(template_ids, ensure_ascii=False)})

    def list_user_dashboards(self) -> Any:
        return self._call("GET", "/v3/bi/dash/user/all")

    # ---------- 资源交接 ----------
    def handover_analysis(self, user: str) -> Any:
        return self._call("GET", "/v3/bi/conf/handover/analysis/get", query={"user": user})

    def handover_public(self, user: str) -> Any:
        return self._call("GET", "/v3/bi/conf/handover/table/get", query={"user": user})

    def handover_start(self, sender: str, accepter: str,
                       pack_ids: Optional[List[str]] = None,
                       table_names: Optional[List[str]] = None,
                       subject_ids: Optional[List[str]] = None,
                       analysis_pack_ids: Optional[List[str]] = None) -> Any:
        return self._call("POST", "/v3/bi/conf/handover/start", [{
            "sender": sender,
            "accepter": accepter,
            "resourceInPublicData": {"packIds": pack_ids or [], "tableNames": table_names or []},
            "resourceInUserAnalysis": {"packIds": analysis_pack_ids or [],
                                       "subjectIds": subject_ids or []},
        }])
