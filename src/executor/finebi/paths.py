"""FineBI 接口路径白名单。

约束：不允许在客户端封装任何 DELETE 资源接口；文件夹/仪表板的
“不带 /info 的 ?packs=/?biReports=” 路径是删除接口，必须排除。
"""
from __future__ import annotations

AUTHORITY_PACK_USER = "/v3/bi/authority/pack/user"
AUTHORITY_PACK_USER_GET = "/v3/bi/authority/pack/user/get"
AUTHORITY_TABLE_USER = "/v3/bi/authority/table/user"
AUTHORITY_TABLE_USER_GET = "/v3/bi/authority/table/user/get"
AUTHORITY_FIELD_USER = "/v3/bi/authority/field/user"
AUTHORITY_FIELD_USER_GET = "/v3/bi/authority/field/user/get"
AUTHORITY_ROW_USER = "/v3/bi/authority/row/filter/user"
AUTHORITY_ROW_USER_GET = "/v3/bi/authority/row/filter/user/get"
AUTHORITY_ROW_ROLE_GET = "/v3/bi/authority/row/filter/role/get"
AUTHORITY_ROW_DEPOST_GET = "/v3/bi/authority/row/filter/depost/get"
AUTHORITY_PACK_ROLE_GET = "/v3/bi/authority/pack/role/get"
AUTHORITY_TABLE_ROLE_GET = "/v3/bi/authority/table/role/get"
AUTHORITY_DASH_AUTH_ROLE_GET = "/v3/bi/authority/dash/template/auth/role/get"
AUTHORITY_PACK_DEPOST_GET = "/v3/bi/authority/pack/depost/get"
AUTHORITY_TABLE_DEPOST_GET = "/v3/bi/authority/table/depost/get"
AUTHORITY_DASH_AUTH_DEPOST_GET = "/v3/bi/authority/dash/template/auth/depost/get"
AUTHORITY_DASH_AUTH = "/v3/bi/authority/dash/template/auth/user"
AUTHORITY_DASH_AUTH_GET = "/v3/bi/authority/dash/template/auth/user/get"
AUTHORITY_ENTRY_USER = "/v3/auth/user/entry"
AUTHORITY_ENTRY_USER_LIST = "/v3/auth/user/entry/list"
AUTHORITY_ENTRY_ROLE_LIST = "/v3/auth/role/entry/list"
AUTHORITY_ENTRY_DEPOST_LIST = "/v3/auth/depost/entry/list"
AUTHORITY_PUBLINK = "/v3/bi/authority/dash/publink/user"
SHARE_DASH = "/v3/bi/share/dash/user"
DASHBOARD_DATA = "/v3/bi/authority/dashboard/data/user/set"
COOPERATION_SUBJECT = "/v3/bi/cooperation/subject/user"

CONF_GROUPS = "/v3/bi/conf/groups"
CONF_PACK_INFO = "/v3/bi/conf/pack/info"
CONF_TABLE_INFO = "/v3/bi/table/info"
CONF_TABLE_USAGE = "/v3/bi/table/usage"
DASH_USER_ALL = "/v3/bi/dash/user/all"
DASH_INFO = "/v3/bi/dash/info"
PUBLISH_INFO = "/v3/bi/publish/info"
HANDOVER_ANALYSIS = "/v3/bi/conf/handover/analysis/get"
HANDOVER_TABLE = "/v3/bi/conf/handover/table/get"
HANDOVER_START = "/v3/bi/conf/handover/start"

PLATFORM_USER = "/v3/user"
PLATFORM_USER_DETAIL = "/v3/user/detail"
PLATFORM_USER_ENABLE = "/v3/user/enable"
PLATFORM_USER_ROLE = "/v3/user/role"
PLATFORM_ROLE = "/v3/role"
PLATFORM_ROLE_USER = "/v3/role/user"
PLATFORM_DEPARTMENT = "/v3/department"
PLATFORM_DEPARTMENT_USER = "/v3/department/user"
PLATFORM_MESSAGE_USER = "/v3/message/user/push"
PLATFORM_MESSAGE_ROLE = "/v3/message/role/push"
PLATFORM_SCHEDULE = "/v3/schedule"
PLATFORM_SCHEDULE_EXECUTE = "/v3/schedule/execute"
PLATFORM_OPERATE_LOG = "/v3/operate/log"
PLATFORM_BEHAVIOR_LOG = "/v3/user/behavior/log"

WRITE_PATHS = {
    AUTHORITY_PACK_USER, AUTHORITY_TABLE_USER, AUTHORITY_FIELD_USER,
    AUTHORITY_ROW_USER, AUTHORITY_DASH_AUTH, AUTHORITY_PUBLINK,
    AUTHORITY_ENTRY_USER,
    SHARE_DASH, DASHBOARD_DATA, COOPERATION_SUBJECT,
    HANDOVER_START, PLATFORM_USER, PLATFORM_USER_ENABLE, PLATFORM_USER_ROLE,
    PLATFORM_ROLE, PLATFORM_ROLE_USER, PLATFORM_MESSAGE_USER,
    PLATFORM_MESSAGE_ROLE, PLATFORM_SCHEDULE_EXECUTE,
}
READ_PATHS = {
    AUTHORITY_PACK_USER_GET, AUTHORITY_TABLE_USER_GET, AUTHORITY_FIELD_USER_GET,
    AUTHORITY_ROW_USER_GET, AUTHORITY_ROW_ROLE_GET, AUTHORITY_ROW_DEPOST_GET,
    AUTHORITY_PACK_ROLE_GET, AUTHORITY_TABLE_ROLE_GET, AUTHORITY_DASH_AUTH_ROLE_GET,
    AUTHORITY_PACK_DEPOST_GET, AUTHORITY_TABLE_DEPOST_GET,
    AUTHORITY_DASH_AUTH_DEPOST_GET,
    AUTHORITY_DASH_AUTH_GET, AUTHORITY_ENTRY_USER_LIST,
    AUTHORITY_ENTRY_ROLE_LIST, AUTHORITY_ENTRY_DEPOST_LIST,
    CONF_GROUPS, CONF_PACK_INFO, CONF_TABLE_INFO, CONF_TABLE_USAGE,
    DASH_USER_ALL, DASH_INFO,
    PUBLISH_INFO, HANDOVER_ANALYSIS, HANDOVER_TABLE,
    PLATFORM_USER_DETAIL, PLATFORM_ROLE, PLATFORM_ROLE_USER,
    PLATFORM_DEPARTMENT, PLATFORM_DEPARTMENT_USER, PLATFORM_SCHEDULE,
    PLATFORM_OPERATE_LOG, PLATFORM_BEHAVIOR_LOG,
}

# 明确禁止的删除类路径（不带 /info 的 pack/dash 查询实际是 DELETE）
FORBIDDEN_PATHS = (
    "/v3/bi/conf/pack?packs=",   # DELETE 删除文件夹
    "/v3/bi/dash?biReports=",    # DELETE 删除仪表板
)
ALLOWED_METHODS = {"GET", "POST", "PUT"}
