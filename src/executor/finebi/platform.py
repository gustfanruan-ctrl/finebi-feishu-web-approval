"""FineBI 平台公共模块接口（V3）：用户、部门、角色、消息、定时调度。

参考：docs/finebi/开放平台 平台接口（对外）.md（平台(V3) 段）
关键接口：
  - PUT /v3/user/role        用户角色关联（add/remove）
  - PUT /v3/role/user        编辑角色下用户
  - PUT /v3/user/enable      启用/禁用用户
  - POST /v3/message/user/push 推送系统消息
  - GET  /v3/schedule        定时调度列表
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ..errors import ApiError
from ..http import HttpClient

LOGGER = logging.getLogger(__name__)
API_ROOT = "/webroot/decision/sp/client/api"

# 写接口白名单：dry-run 只拦截这些 path+method；查询类 POST（role/user、
# department/user、auth/user/schedule/list 等）必须照常发请求，否则 dry-run
# 下会被当成空数据。同一路径可能读写复用（如 /v3/role/user：PUT 写、POST 查）。
PLATFORM_WRITE_PATHS = {
    "/v3/user": {"POST", "PUT"},
    "/v3/user/enable": {"PUT"},
    "/v3/user/role": {"PUT"},
    "/v3/user/department": {"PUT"},
    "/v3/role": {"POST"},
    "/v3/role/user": {"PUT"},
    "/v3/message/user/push": {"POST"},
    "/v3/message/role/push": {"POST"},
    "/v3/schedule/execute": {"POST"},
    "/v3/auth/user/schedule": {"POST"},
    "/v3/auth/user/platform": {"POST"},
}


class FineBIPlatformClient:
    def __init__(self, base_url: str, client_id: str, secret: str,
                 dec_user: Optional[str] = None, http: Optional[HttpClient] = None,
                 dry_run: bool = False):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.secret = secret
        self.dec_user = dec_user
        self.http = http or HttpClient()
        self.dry_run = dry_run

    def _call(self, method: str, path: str, body: Any = None,
              query: Optional[Dict[str, Any]] = None) -> Any:
        url = self.base_url + API_ROOT + path
        headers = {"clientId": self.client_id, "secret": self.secret}
        params = dict(query or {})
        if self.dec_user:
            params.setdefault("decUser", self.dec_user)
        if (self.dry_run and path in PLATFORM_WRITE_PATHS
                and method.upper() in PLATFORM_WRITE_PATHS[path]):
            LOGGER.info("[DRY-RUN] %s %s body=%s", method, path, body)
            return {"dry_run": True, "method": method, "path": path}
        resp = self.http.request(method, url, headers=headers, json_body=body, params=params)
        self._assert_top_level(resp)
        self._assert_batch_status(resp)
        return resp

    @staticmethod
    def _assert_top_level(resp: Any) -> None:
        """平台接口失败时可能 HTTP 200 但信封里 status>=400（真实探测确认）。

        例如 ``GET /v3/department`` 参数不合法返回
        ``{"status":400,"errorCode":"E000101","errorMsg":...}``，
        不校验会被调用方当成成功、拿到 ``data=None``。
        """
        if not isinstance(resp, dict) or resp.get("dry_run"):
            return
        status = resp.get("status")
        if isinstance(status, int) and status >= 400:
            raise ApiError(status, str(resp.get("errorMsg") or resp.get("message") or resp), resp)
        if resp.get("errorCode") and "data" not in resp:
            raise ApiError(resp.get("errorCode"), str(resp.get("errorMsg") or resp), resp)

    @staticmethod
    def _assert_batch_status(resp: Any) -> None:
        data = resp.get("data") if isinstance(resp, dict) else None
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("status") is False:
                    raise ApiError("BATCH", str(item.get("errorMsg") or item), item)

    # ---------- 用户 ----------
    def add_users(self, users: List[Dict[str, Any]]) -> Any:
        return self._call("POST", "/v3/user", users)

    def update_users(self, users: List[Dict[str, Any]]) -> Any:
        return self._call("PUT", "/v3/user", users)

    def set_user_enabled(self, user: str, enabled: bool) -> Any:
        return self._call("PUT", "/v3/user/enable", [{"user": user, "enable": enabled}])

    def set_user_roles(self, user: str, add: Optional[List[str]] = None,
                       remove: Optional[List[str]] = None) -> Any:
        """用户角色关联：add/remove 为角色名或角色 id。"""
        return self._call("PUT", "/v3/user/role",
                          [{"user": user, "add": add or [], "remove": remove or []}])

    def set_user_departments(self, user: str,
                             add: Optional[List[Any]] = None,
                             remove: Optional[List[Any]] = None) -> Any:
        """用户部门关联：add/remove 为部门路径（数组）或部门路径 JSON 字符串。

        文档 body 里 department 必须是 JSON 数组字符串，例如
        ``[{"department": "[\\"财务部\\"]"}]``；调用方既可传 ``["财务部"]``
        也可直接传已序列化的 JSON 字符串（台账 resource_id 就是后者）。
        """
        def entries(values: Optional[List[Any]]) -> List[Dict[str, str]]:
            result: List[Dict[str, str]] = []
            for value in values or []:
                if isinstance(value, str):
                    department = value
                else:
                    department = json.dumps(value, ensure_ascii=False)
                result.append({"department": department})
            return result

        return self._call("PUT", "/v3/user/department",
                          [{"user": user, "add": entries(add),
                            "remove": entries(remove)}])

    def query_users(self, username: str = "", email: str = "", page: int = 1,
                    count: int = 200) -> Any:
        return self._call("GET", "/v3/user", query={
            "username": username, "email": email, "page": page, "count": count})

    def query_user_detail(self, username: str = "", email: str = "", mobile: str = "",
                          page: int = 1, count: int = 200) -> Any:
        """查询用户详细信息。

        username 是**模糊匹配**（实测 "a" 能匹配 19 个用户），调用方必须按
        username 精确过滤；count 用文档默认值 200，避免匹配项多时把目标用户截断到
        第一页之外（映射/角色只读调用依赖完整结果）。
        """
        return self._call("GET", "/v3/user/detail", query={
            "username": username, "email": email, "mobile": mobile,
            "page": page, "count": count})

    # ---------- 角色 ----------
    def add_role(self, role_name: str, description: str = "") -> Any:
        return self._call("POST", "/v3/role", [{"roleName": role_name, "description": description}])

    def query_roles(self, role: str = "", exact: bool = False) -> Any:
        return self._call("GET", "/v3/role", query={"role": role, "exact": str(exact).lower()})

    def add_role_users(self, role: str, users: List[str]) -> Any:
        return self._call("PUT", "/v3/role/user", [{"id": role, "add": users, "remove": []}])

    def remove_role_users(self, role: str, users: List[str]) -> Any:
        return self._call("PUT", "/v3/role/user", [{"id": role, "add": [], "remove": users}])

    def query_role_users(self, roles: List[str]) -> Any:
        return self._call("POST", "/v3/role/user", roles)

    # ---------- 部门 ----------
    def query_departments(self, department: List[str]) -> Any:
        """查询部门：GET /v3/department?department=JSON数组。

        文档要求 department 传 JSON 数组字符串（[] 表示根部门）；
        Python 的 str(list) 是单引号形态，实测会被接口判为不存在（真实 400）。
        """
        return self._call("GET", "/v3/department",
                          query={"department": json.dumps(department, ensure_ascii=False)})

    def query_department_users(self, department: List[str], post: str = "",
                               recursive: bool = False) -> Any:
        """查询部门下用户：POST /v3/department/user。

        文档 body 是数组，且 department 为 JSON 数组字符串（不是数组本身），
        实测传 dict/数组会 400 反序列化失败。
        """
        item: Dict[str, Any] = {"department": json.dumps(department, ensure_ascii=False)}
        if post:
            item["post"] = post
        if recursive:
            item["recursive"] = True
        return self._call("POST", "/v3/department/user", [item])

    # ---------- 消息 ----------
    def push_message_to_user(self, user: str, content: str, url: str = "") -> Any:
        return self._call("POST", "/v3/message/user/push",
                          [{"user": user, "content": content, "url": url}])

    def push_message_to_role(self, role: str, content: str, url: str = "") -> Any:
        return self._call("POST", "/v3/message/role/push",
                          [{"role": role, "content": content, "url": url}])

    # ---------- 定时调度 ----------
    def list_schedules(self, page: int = 1, per_page: int = 50) -> Any:
        return self._call("GET", "/v3/schedule", query={"page": page, "perPage": per_page})

    def execute_schedule(self, task_id: str) -> Any:
        """执行一次定时调度任务：POST /v3/schedule/execute，body 字段是 task。"""
        return self._call("POST", "/v3/schedule/execute", [{"task": task_id}])

    # ---------- 平台目录（仪表板/报表目录） ----------
    def get_entry_tree(self, device: str = "pc") -> Any:
        """查询平台目录树：GET /v3/entry/tree?device=pc。

        返回当前 API 调用者可见的目录树；BI 仪表板节点 entryType=201，
        templateId 为仪表板 ID（需用 /v3/bi/dash/info 复核）。
        """
        return self._call("GET", "/v3/entry/tree", query={"device": device})

    def query_entries(self, keyword: str = "", entry: Optional[List[str]] = None) -> Any:
        """多条件查询平台目录：GET /v3/entry。

        keyword 非空时按名称模糊查询；否则按 entry（目录 ID/路径）查询子节点，
        根目录传 []。接口不分页。
        """
        query: Dict[str, Any] = {}
        if keyword:
            query["keyword"] = keyword
        if entry is not None:
            query["entry"] = json.dumps(entry, ensure_ascii=False)
        return self._call("GET", "/v3/entry", query=query)

    def query_role_entries(self, role: str, entries: List[str]) -> Any:
        """根据角色查询目录权限：POST /v3/auth/role/entry/list。"""
        return self._call("POST", "/v3/auth/role/entry/list",
                          {"role": role, "entries": list(entries)})

    def query_depost_entries(self, department: str, position: str,
                             entries: List[str]) -> Any:
        """根据部门职务查询目录权限：POST /v3/auth/depost/entry/list。"""
        return self._call("POST", "/v3/auth/depost/entry/list",
                          {"department": department,
                           "position": position or "",
                           "entries": list(entries)})

    # ---------- 定时调度权限 ----------
    def set_user_schedule_permission(self, user: str, schedule_task: str,
                                     manage: bool = True, empower: bool = False) -> Any:
        return self._call("POST", "/v3/auth/user/schedule", [{
            "user": user,
            "scheduleTask": schedule_task,
            "authority": {"managePrivilege": manage, "empowerPrivilege": empower},
        }])

    def get_user_schedule_permission(self, user: str, schedule_tasks: List[str]) -> Any:
        return self._call("POST", "/v3/auth/user/schedule/list", {
            "user": user, "scheduleTasks": schedule_tasks})

    def set_user_platform_permission(self, user: str, module: str,
                                     use: bool = True, empower: bool = False) -> Any:
        """配置管理系统的功能权限（如定时调度 decision-management-schedule）。"""
        return self._call("POST", "/v3/auth/user/platform", [{
            "user": user,
            "module": module,
            "authority": {"usePrivilege": use, "empowerPrivilege": empower},
        }])
