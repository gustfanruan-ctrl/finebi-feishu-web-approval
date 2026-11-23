"""项目异常类型。"""


class ExecutorError(Exception):
    """执行器基础异常。"""


class ConfigError(ExecutorError):
    """配置缺失或不合法。"""


class ApiError(ExecutorError):
    """下游接口返回错误。"""

    def __init__(self, status, message, payload=None):
        super().__init__("[%s] %s" % (status, message))
        self.status = status
        self.message = message
        self.payload = payload


class BusinessError(ExecutorError):
    """业务校验失败（非重试类错误）。"""


def is_template_auth_not_applicable(exc: BaseException) -> bool:
    """仪表板模板认证不可用时，模板认证接口报错应跳过而不是判失败。

    两种情况：
    - 该仪表板未纳入模板认证：``Unrecognized entityId``；
    - FineBI 全局未开启模板认证/角色权限认证：
      ``Role permission authentication is not enabled!``。
    此时看板访问由目录 entry 权限控制，模板授权对它不适用。
    """
    text = str(exc).lower()
    return ("unrecognized entityid" in text
            or "authentication is not enabled" in text)

