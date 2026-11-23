"""FineDB 只读查询：飞书用户映射、数据集行权限枚举。

仅执行 SELECT；连接串来自 .env，不写日志。
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

# 远端 FineDB 偶发在建连阶段丢包（2013/2003/2006），重试几次即可
_RETRYABLE_CODES = (2003, 2006, 2013, 2026)


class FineDB:
    def __init__(self, host: str, port: int = 3306, user: str = "",
                 password: str = "", database: str = "finedb"):
        self.host = host
        self.port = int(port or 3306)
        self.user = user
        self.password = password
        self.database = database or "finedb"

    def enabled(self) -> bool:
        return bool(self.host and self.user)

    def _connect(self, attempts: int = 3):
        import pymysql
        last_error = None
        for attempt in range(attempts):
            try:
                return pymysql.connect(
                    host=self.host, port=self.port, user=self.user, password=self.password,
                    database=self.database, connect_timeout=5, read_timeout=20,
                    charset="utf8mb4", ssl_disabled=True)
            except pymysql.err.OperationalError as exc:
                code = exc.args[0] if exc.args else None
                last_error = exc
                if code not in _RETRYABLE_CODES or attempt == attempts - 1:
                    raise
                LOGGER.warning("FineDB 建连失败（%s），重试 %s/%s", code, attempt + 1, attempts - 1)
                time.sleep(0.3 * (attempt + 1))
        raise last_error  # pragma: no cover

    def _query(self, sql: str, params: tuple = (), attempts: int = 3):
        """只读查询；建连后偶发丢连接（2013/2006）时换新连接重试。"""
        last_error = None
        for attempt in range(attempts):
            con = self._connect()
            try:
                with con.cursor() as cur:
                    cur.execute(sql, params)
                    return list(cur.fetchall())
            except Exception as exc:  # noqa: BLE001
                code = exc.args[0] if getattr(exc, "args", None) else None
                last_error = exc
                if code not in _RETRYABLE_CODES or attempt == attempts - 1:
                    raise
                LOGGER.warning("FineDB 查询失败（%s），重试 %s/%s", code,
                               attempt + 1, attempts - 1)
                time.sleep(0.4 * (attempt + 1))
            finally:
                con.close()
        raise last_error  # pragma: no cover

    # ---------- 数据值去重（行权限下拉） ----------
    def distinct_values(self, source_sql: str, field_name: str,
                        limit: int = 500) -> List[str]:
        """从数据集的 SQL 里取某字段的去重值（只读、限量）。

        说明：FineDB 与客户数据源通常在同一 MySQL 实例，数据集的 SQL 可由
        FineDB 账号直接执行；SQL 来自 FineBI ``table/info`` 元数据，不接受
        用户输入。源库不在同一实例、SQL 带参数或账号无权限时返回空，由调用方
        回退到行权限规则里的值。
        """
        if not self.enabled():
            return []
        sql = str(source_sql or "").strip().rstrip(";")
        field = str(field_name or "").strip()
        if not sql or not field:
            return []
        # 参数化 SQL 不能直接执行；带分号、注释/多语句的 SQL 也不放行
        if "${" in sql or "?" in sql or ";" in sql:
            return []
        safe_field = field.replace("`", "``")
        row_limit = max(1, min(int(limit or 500), 1000))
        query = (
            "SELECT DISTINCT `%s` AS __v FROM (%s) AS __web_src "
            "WHERE `%s` IS NOT NULL AND `%s` <> '' LIMIT %d"
            % (safe_field, sql, safe_field, safe_field, row_limit)
        )
        try:
            rows = self._query(query)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("数据值去重查询失败（源库可能不在同一实例）：%s",
                           str(exc)[:160])
            return []
        values: List[str] = []
        for row in rows or []:
            if not row:
                continue
            value = row[0]
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8", "replace")
                except Exception:  # noqa: BLE001
                    value = str(value)
            text = str(value).strip() if value is not None else ""
            if text and text not in values:
                values.append(text)
        return values

    # ---------- 飞书映射 ----------
    def feishu_mapping(self) -> List[Dict[str, str]]:
        if not self.enabled():
            return []
        rows = self._query("SELECT fsUser, feiShuUser FROM fine_feishu_user_relation")
        return [{"fb_user": str(r[0] or ""), "feishu_user_id": str(r[1] or "")}
                for r in rows if r and r[0]]

    def feishu_user_by_id(self, feishu_user_id: str) -> str:
        """飞书 user_id → FineBI 用户名（登录时最可靠的映射来源）。"""
        if not self.enabled() or not feishu_user_id:
            return ""
        rows = self._query(
            "SELECT fsUser FROM fine_feishu_user_relation "
            "WHERE feiShuUser=%s LIMIT 1", (feishu_user_id,))
        return str(rows[0][0]) if rows and rows[0] and rows[0][0] else ""

    def user_by_mobile(self, mobile: str) -> str:
        """手机号 → FineBI 用户名。

        客户 FineBI 的飞书集成按手机号匹配用户，因此登录/同步时优先用
        ``fine_user.mobile`` 直查，比调开放平台接口更可靠。
        """
        if not self.enabled():
            return ""
        digits = "".join(ch for ch in str(mobile or "") if ch.isdigit())
        if not digits:
            return ""
        candidates = [digits]
        if len(digits) == 13 and digits.startswith("86"):
            candidates.append(digits[2:])
        elif len(digits) == 11:
            candidates.append("86" + digits)
        for value in candidates:
            try:
                rows = self._query(
                    "SELECT username FROM fine_user WHERE mobile=%s LIMIT 1", (value,))
            except Exception as exc:  # noqa: BLE001 - 无 mobile 列/无权限时按无匹配处理
                LOGGER.warning("FineDB 手机号查询失败：%s", exc)
                return ""
            if rows and rows[0] and rows[0][0]:
                return str(rows[0][0])
        return ""

    # ---------- 行权限枚举 ----------
    @staticmethod
    def _parse_filter(raw: Any) -> Any:
        """fine_pack_filter.filter 可能是 JSON 字符串，也可能被二次编码。"""
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", "ignore")
        if isinstance(raw, str):
            raw = raw.strip()
            if not raw:
                return None
            try:
                raw = json.loads(raw)
            except (TypeError, json.JSONDecodeError):
                return None
            # 少数存量规则存的是「JSON 字符串的 JSON 字符串」
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except (TypeError, json.JSONDecodeError):
                    return None
        return raw

    @staticmethod
    def _filter_nodes(data: Any) -> List[Dict[str, Any]]:
        """递归取出行权限节点（兼容 and/or 嵌套）。"""
        result: List[Dict[str, Any]] = []

        def walk(node: Any) -> None:
            if isinstance(node, list):
                for child in node:
                    walk(child)
                return
            if not isinstance(node, dict):
                return
            value = node.get("filterValue")
            if node.get("fieldId") and isinstance(value, (dict, list)):
                result.append(node)
            if isinstance(value, list):
                for child in value:
                    walk(child)

        walk(data)
        return result

    def row_filter_options(self, table_id: str, fb_user: str = "") -> List[Dict[str, Any]]:
        """读取 fine_pack_filter 中该数据集的行权限字段/枚举值。

        读取该数据集全部启用规则（角色/部门/所有用户），把值列表型规则里的
        ``value``/``assist`` 合并成候选枚举。这样即使参考用户自己没有规则，
        也能拿到其他角色/用户已配置的店铺编码等可选值；动态规则
        （filterType=11，按登录用户属性过滤）没有固定值，会被跳过。
        """
        if not self.enabled():
            return []
        raw_rules: List[Any] = [
            r[0] for r in self._query(
                "SELECT filter FROM fine_pack_filter WHERE tableId=%s "
                "AND enable=1", (table_id,))]
        merged: Dict[str, Dict[str, Any]] = {}
        for raw in raw_rules:
            for node in self._filter_nodes(self._parse_filter(raw)):
                field_id = str(node.get("fieldId") or "")
                if not field_id:
                    continue
                name = str(node.get("fieldName") or "")
                entry = merged.setdefault(field_id, {
                    "field_id": field_id,
                    "name": name or field_id,
                    "values": set()})
                # 用户级规则可能把字段 ID 当字段名存；全局规则里有中文名时优先用中文名
                if name and name != field_id and entry["name"] == field_id:
                    entry["name"] = name
                value = node.get("filterValue")
                if isinstance(value, dict):
                    for item in (value.get("value") or []):
                        entry["values"].add(str(item))
                    for item in (value.get("assist") or []):
                        entry["values"].add(str(item))
                elif isinstance(value, list):
                    for item in value:
                        entry["values"].add(str(item))
        return [{"field_id": k, "name": v["name"], "values": sorted(v["values"])}
                for k, v in merged.items() if v["values"]]
