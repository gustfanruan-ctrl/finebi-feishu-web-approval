"""行权限规范化/合并/序列化。

FineBI 的行权限有两种表示：
- set 入参：`{"type":"or","filterValue":[{"type":"strIn","fieldId":...,"filterValue":[...]}]}`
- get 返回：JSON 字符串，节点用数字 `filterType`，叶子值为 `{"type":1,"value":[...]}`

数字映射在接口文档 ``docs/finebi/开放平台 FineBI接口（对外）.md``（行权限 get 的
响应参数表）中已明确给出：``and:34  or:35  str_in:10  strNotIn:12``。
因此这里给出文档级默认映射；``config.policy.filter_type_map`` 仍可覆盖（见
:func:`resolve_type_map`）。文档未列出的 filterType 仍然报错转人工，不猜测。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..errors import BusinessError


class RowFilterError(BusinessError):
    """行权限结构无法解析或序列化。"""


@dataclass(frozen=True)
class Condition:
    field_id: str
    op: str                      # strIn / strNotIn
    values: Tuple[str, ...]

    def to_set_dict(self) -> Dict[str, Any]:
        return {"type": self.op, "fieldId": self.field_id, "filterValue": list(self.values)}


@dataclass(frozen=True)
class Group:
    """AND 组：组内多个条件取交集。"""
    conditions: Tuple[Condition, ...]


@dataclass(frozen=True)
class RowExpr:
    """OR 组集合：组间取并集。"""
    groups: Tuple[Group, ...]


# 接口文档明确给出：and:34  or:35  str_in:10  strNotIn:12
DEFAULT_TYPE_MAP: Dict[int, str] = {34: "and", 35: "or", 10: "strIn", 12: "strNotIn"}

GROUP_TYPES = ("and", "or")
CONDITION_TYPES = ("strIn", "strNotIn")


def resolve_type_map(type_map: Optional[Dict[Any, str]] = None) -> Dict[int, str]:
    """合并文档默认映射与配置映射（配置优先，键统一为 int）。"""
    resolved: Dict[int, str] = dict(DEFAULT_TYPE_MAP)
    for key, value in (type_map or {}).items():
        try:
            resolved[int(key)] = str(value)
        except (TypeError, ValueError):
            continue
    return resolved


def _lookup(node_type: Any, type_map: Dict[int, str]) -> str:
    try:
        code = int(node_type)
    except (TypeError, ValueError):
        raise RowFilterError("filterType 非数字：%r" % (node_type,))
    name = type_map.get(code)
    if not name:
        raise RowFilterError("未知 filterType：%s（文档未定义该类型，转人工处理）" % code)
    return name


def parse_get(raw: Any, type_map: Optional[Dict[int, str]] = None) -> Optional[RowExpr]:
    """把 get 返回的 JSON 字符串解析为 RowExpr；空值返回 None。"""
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RowFilterError("行权限返回不是合法 JSON") from exc
    elif isinstance(raw, dict):
        data = raw
    else:
        raise RowFilterError("无法识别的行权限返回：%r" % (raw,))
    if not data or not data.get("filterValue"):
        return None
    return _parse_node(data, resolve_type_map(type_map))


def _parse_node(node: Dict[str, Any], type_map: Dict[int, str]) -> RowExpr:
    if not isinstance(node, dict):
        raise RowFilterError("行权限节点不是对象")
    logic = _lookup(node.get("filterType"), type_map)
    if logic in CONDITION_TYPES:
        # 单条件节点：get 直接返回 {filterType:10, fieldId, filterValue:{type:1,value:[...]}}
        return RowExpr(groups=(Group((_parse_condition(node, type_map),)),))
    children = node.get("filterValue")
    if not isinstance(children, list) or not children:
        raise RowFilterError("filterValue 为空或不是数组")
    if logic == "and":
        conditions = tuple(_parse_condition(c, type_map) for c in children)
        return RowExpr(groups=(Group(conditions),))
    if logic == "or":
        groups: List[Group] = []
        for child in children:
            if not isinstance(child, dict):
                raise RowFilterError("OR 子节点不是对象")
            child_logic = _lookup(child.get("filterType"), type_map)
            if child_logic == "and":
                # 嵌套 AND 组（别的系统/手工配置可能写入）：读取时保留整组
                sub_children = child.get("filterValue")
                if not isinstance(sub_children, list) or not sub_children:
                    raise RowFilterError("AND 子节点 filterValue 为空或不是数组")
                groups.append(Group(tuple(_parse_condition(c, type_map)
                                          for c in sub_children)))
            elif child_logic in CONDITION_TYPES:
                groups.append(Group((_parse_condition(child, type_map),)))
            else:
                raise RowFilterError("OR 子节点类型不支持：%s" % child_logic)
        return RowExpr(groups=tuple(groups))
    raise RowFilterError("根节点必须是 and/or，实际为：%s" % logic)


def _parse_condition(node: Dict[str, Any], type_map: Dict[int, str]) -> Condition:
    if not isinstance(node, dict):
        raise RowFilterError("条件节点不是对象")
    op = _lookup(node.get("filterType"), type_map)
    if op not in CONDITION_TYPES:
        raise RowFilterError("P1 仅支持 strIn/strNotIn，实际为：%s" % op)
    field_id = node.get("fieldId")
    if not field_id:
        raise RowFilterError("条件缺少 fieldId")
    value = node.get("filterValue")
    if isinstance(value, dict):
        value = value.get("value")
    if not isinstance(value, list):
        raise RowFilterError("条件值不是数组")
    return Condition(str(field_id), op, tuple(str(v) for v in value))


def to_set_payload(expr: Optional[RowExpr]) -> Optional[Dict[str, Any]]:
    """RowExpr → set 接口入参；None 表示无规则。"""
    if expr is None or not expr.groups:
        return None
    converted: List[Dict[str, Any]] = []
    for group in expr.groups:
        if len(group.conditions) == 1:
            converted.append(group.conditions[0].to_set_dict())
        else:
            converted.append({
                "type": "and",
                "filterValue": [c.to_set_dict() for c in group.conditions],
            })
    return {"type": "or", "filterValue": converted}


def canonical(expr: Optional[RowExpr]) -> str:
    """稳定哈希串：条件/组排序去重，用于比较与幂等。"""
    if expr is None:
        return ""
    groups = []
    for group in expr.groups:
        conditions = sorted(
            ({"f": c.field_id, "op": c.op, "v": sorted(c.values)} for c in group.conditions),
            key=lambda x: (x["f"], x["op"], x["v"]))
        groups.append(conditions)
    groups.sort(key=lambda g: json.dumps(g, ensure_ascii=False, sort_keys=True))
    return json.dumps(groups, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def merge(exprs: Iterable[Optional[RowExpr]]) -> Optional[RowExpr]:
    """多个表达式取并集（OR），按 canonical 去重。"""
    seen = set()
    groups: List[Group] = []
    for expr in exprs:
        if not expr:
            continue
        for group in expr.groups:
            key = canonical(RowExpr(groups=(group,)))
            if key in seen:
                continue
            seen.add(key)
            groups.append(group)
    return RowExpr(groups=tuple(groups)) if groups else None


def rules_to_expr(rules: Sequence[Dict[str, Any]]) -> Optional[RowExpr]:
    """把表单里的规则列表（一个 AND 组）转成 RowExpr。

    rules 形如 [{"type":"strIn","fieldId":...,"filterValue":[...]}]。
    """
    if not rules:
        return None
    conditions = []
    for rule in rules:
        conditions.append(Condition(
            field_id=str(rule["fieldId"]),
            op=str(rule.get("type", "strIn")),
            values=tuple(str(v) for v in rule.get("filterValue", [])),
        ))
    return RowExpr(groups=(Group(tuple(conditions)),))


def expr_to_rules(expr: Optional[RowExpr]) -> List[Dict[str, Any]]:
    """RowExpr → 表单规则列表（用于写台账 payload）。"""
    if not expr:
        return []
    return [c.to_set_dict() for group in expr.groups for c in group.conditions]
