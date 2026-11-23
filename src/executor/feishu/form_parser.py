"""飞书审批表单解析：控件 JSON → :class:`PermissionRequest`。

背景
====
审批实例详情返回的 ``form`` 是一个 JSON 字符串，内容是控件数组（见
``docs/feishu/openapi/approval-instance-get.md``「控件值说明」）。控件类型与取值形态差异大：

- ``input`` / ``textarea``：字符串；
- ``radio`` / ``radioV2``：选项文本；
- ``checkbox`` / ``checkboxV2``：选项文本列表；
- ``contact``：用户 user_id 列表（``open_ids`` 为 open_id 列表）；
- ``fieldList``：二维数组（明细/表格）；
- ``mutableGroup``：引用多维表格，按行返回被引用字段（POC-4 待冻结具体结构）。

设计
====
- 字段与控件名/ID 的映射来自配置 ``policy.form_mapping``（见 ``config/config.json``），
  改配置不改代码；兼容旧的扁平映射（``field_user``/``field_resource``/...）与
  设计说明书中的结构化映射（``fields: {user: {widget_id, type}}``）。
- 缺字段、值非法、状态非 APPROVED 时抛 :class:`FormParseError`（业务错误，不重试）。
- 保留与 ``services/poller.py`` 旧 ``FormMapper`` 兼容的 ``parse(instance)`` +
  ``to_request(values)`` 接口：``FormParser`` 可直接替换旧类。
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from ..errors import BusinessError
from ..models import PermissionRequest, ResourceType

# 权限模板展开器接口（P2 只留注入点，模板内容由客户按 POC 冻结后提供）：
# resolver(template_name, context) -> [item dict, ...]，item 结构同 PermissionRequest.items。
TemplateResolver = Callable[[str, Dict[str, Any]], List[Dict[str, Any]]]

# ---------- 控件类型分组 ----------
TEXT_TYPES = {"input", "textarea", "text", "serialNumber"}
RADIO_TYPES = {"radio", "radioV2"}
CHECKBOX_TYPES = {"checkbox", "checkboxV2"}
CONTACT_TYPES = {"contact"}
BITABLE_TYPES = {"mutableGroup"}
FIELD_LIST_TYPES = {"fieldList"}
# 取值可能是数字/日期的文本型控件
SCALAR_TYPES = TEXT_TYPES | RADIO_TYPES | {"number", "amount", "formula", "date", "address"}

_NUMBER_RE = re.compile(r"(\d+)")


class FormParseError(BusinessError):
    """审批表单解析失败（缺控件、值非法、结构未知）。"""


# ---------------------------------------------------------------------------
# 基础解析工具
# ---------------------------------------------------------------------------
def parse_form(form: Any) -> List[Dict[str, Any]]:
    """把审批实例的 ``form`` 字段解析为控件字典列表。

    :raises FormParseError: 空值或非法 JSON。
    """
    if form is None or form == "":
        raise FormParseError("审批实例 form 为空")
    if isinstance(form, str):
        try:
            form = json.loads(form)
        except json.JSONDecodeError as exc:
            raise FormParseError("审批实例 form 不是合法 JSON：%s" % exc) from exc
    if isinstance(form, dict):
        form = [form]
    if not isinstance(form, list):
        raise FormParseError("审批实例 form 结构未知：%r" % type(form).__name__)
    widgets: List[Dict[str, Any]] = []
    for item in form:
        if not isinstance(item, dict):
            raise FormParseError("审批表单控件不是对象：%r" % (item,))
        widgets.append(item)
    return widgets


def flatten_form(form: Any) -> Dict[str, Any]:
    """把 form 拍平为 ``{控件名: 值}``，兼容旧 ``poller.flatten_form``。

    非法 JSON 返回空字典（旧行为），严格校验请用 :func:`parse_form`。
    """
    try:
        widgets = parse_form(form)
    except FormParseError:
        return {}
    values: Dict[str, Any] = {}

    def visit(items: Any) -> None:
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            return
        for item in items:
            if isinstance(item, (list, tuple)):
                visit(item)
                continue
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("custom_id")
            value = item.get("value")
            if name:
                values[str(name)] = value
            if isinstance(value, dict):
                visit(value.get("children"))
            elif isinstance(value, list):
                visit(value)
            visit(item.get("children"))

    visit(widgets)
    return values


def widget_index(widgets: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """按 id / custom_id / name 建控件索引（同名以先出现者为准）。"""
    index: Dict[str, Dict[str, Any]] = {}
    for widget in widgets:
        for key in ("id", "custom_id", "name"):
            raw = widget.get(key)
            if not raw:
                continue
            for candidate in (_norm(raw), str(raw)):
                index.setdefault(candidate, widget)
    return index


def _norm(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower()


def _first_scalar(value: Any) -> Any:
    """从各种控件取值形态里取第一个标量。"""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        for key in ("value", "name", "text", "user_id", "open_id", "id"):
            if key in value:
                found = _first_scalar(value[key])
                if found not in (None, ""):
                    return found
        return None
    if isinstance(value, (list, tuple)):
        for item in value:
            found = _first_scalar(item)
            if found not in (None, ""):
                return found
        return None
    return None


def _as_text(value: Any) -> str:
    scalar = _first_scalar(value)
    return "" if scalar is None else str(scalar).strip()


def _as_list(value: Any) -> List[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _widget_cells_to_record(cells: Any) -> Dict[str, Any]:
    """把明细/多维表格行里的控件数组转成 ``{控件名: 值}``。"""
    if isinstance(cells, dict):
        return dict(cells)
    record: Dict[str, Any] = {}
    for cell in _as_list(cells):
        if not isinstance(cell, dict):
            continue
        for key in ("name", "custom_id", "id"):
            if cell.get(key):
                record[str(cell[key])] = cell.get("value")
                break
    return record


def _as_records(value: Any) -> List[Dict[str, Any]]:
    """把控件取值统一成"记录列表"，每行一个 dict。

    兼容：
    - ``[{"资源ID": "...", ...}]``（引用多维表格直接给对象）；
    - ``[[{控件}, {控件}]]``（明细控件二维数组）；
    - ``{"records": [...]}`` / ``{"value": [...]}``；
    - 普通字符串（资源名称/ID）。
    """
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [{"value": value}]
    if isinstance(value, dict):
        for key in ("records", "rows", "items", "value"):
            if key in value and isinstance(value[key], (list, dict, str)):
                return _as_records(value[key])
        return [dict(value)]
    if not isinstance(value, (list, tuple)):
        return [{"value": value}]
    records: List[Dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            # 单元格形态 {"id","type","value"} 与业务对象形态都可能出现
            if set(item.keys()) <= {"id", "type", "value", "name", "custom_id", "open_ids"}:
                records.append(_widget_cells_to_record(item))
            else:
                records.append(dict(item))
        elif isinstance(item, (list, tuple)):
            records.append(_widget_cells_to_record(item))
        elif item not in (None, ""):
            records.append({"value": item})
    return records


def _pick(record: Dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if not key:
            continue
        if key in record:
            scalar = _first_scalar(record[key])
            if scalar not in (None, ""):
                return scalar
    # 大小写/空白不敏感兜底
    normal = {_norm(k): v for k, v in record.items()}
    for key in keys:
        if key and _norm(key) in normal:
            scalar = _first_scalar(normal[_norm(key)])
            if scalar not in (None, ""):
                return scalar
    return None


def _deterministic_id(instance_code: str) -> str:
    digest = hashlib.sha1(("feishu:" + instance_code).encode("utf-8")).hexdigest()
    return "req-%s" % digest[:12]


# ---------------------------------------------------------------------------
# 解析器
# ---------------------------------------------------------------------------
class FormParser:
    """按 ``policy.form_mapping`` 把审批实例解析为 ``PermissionRequest``。

    :param mapping: ``settings.policy["form_mapping"]``（扁平或结构化均可）。
    :param resources: 资源目录映射（默认取 mapping["resources"]）。
    :param default_days: 默认期限（默认取 mapping["default_days"]，再缺省 90）。
    :param template_resolver: 可选的权限模板展开器（模板名 → 授权条目列表）。
        未注入时只把模板名记入 ``request.extra["template"]``，授权条目仍按单资源解析；
        grant 已支持 ``PermissionRequest.items`` 多条目执行，是模板落地的统一入口。
    """

    def __init__(self, mapping: Optional[Dict[str, Any]] = None,
                 resources: Optional[Dict[str, Any]] = None,
                 default_days: Optional[int] = None,
                 template_resolver: Optional[TemplateResolver] = None):
        self.mapping: Dict[str, Any] = dict(mapping or {})
        self.template_resolver = template_resolver
        fields = self.mapping.get("fields")
        self.fields: Dict[str, Any] = dict(fields) if isinstance(fields, dict) else {}
        merged_resources = dict(self.mapping.get("resources") or {})
        merged_resources.update(resources or {})
        self.resources: Dict[str, Any] = merged_resources
        self.resource_type_map: Dict[str, str] = dict(
            self.mapping.get("resource_type_map") or {})
        self.action_map: Dict[str, str] = dict(self.mapping.get("action_map") or {})
        self.row_field_ids: Dict[str, str] = dict(self.mapping.get("row_field_ids") or {})
        raw_days = default_days if default_days is not None else self.mapping.get("default_days")
        try:
            self.default_days = int(raw_days) if raw_days not in (None, "") else 90
        except (TypeError, ValueError):
            self.default_days = 90
        self.widgets: Dict[str, Dict[str, Any]] = {}
        self.last_values: Dict[str, Any] = {}

    # ---------- 兼容旧 FormMapper 的入口 ----------
    def parse(self, instance: Any) -> Dict[str, Any]:
        """把审批实例（详情 data 或整个响应）拍平为取值字典。

        与旧 ``poller.FormMapper.parse`` 一致：form 非法时不抛错，返回空取值，
        由后续必填校验给出清晰异常。
        """
        data = self._instance_data(instance)
        form = data.get("form")
        try:
            widgets = parse_form(form) if form else []
        except FormParseError:
            widgets = []
        self.widgets = widget_index(widgets)
        values = flatten_form(form)
        # 结构化映射可以直接用控件 ID/custom_id；补一份索引值（不覆盖按名称取到的值）
        for key, widget in self.widgets.items():
            values.setdefault(key, widget.get("value"))
        values["_instance_code"] = (data.get("instance_code") or data.get("code")
                                    or data.get("uuid") or "")
        values["_status"] = data.get("status")
        self.last_values = values
        return values

    def to_request(self, values: Dict[str, Any]) -> PermissionRequest:
        """把 ``parse()`` 的取值字典转成 ``PermissionRequest``。"""
        user = self._required_text(values, "user", "field_user", "FineBI账号")
        actions = self._actions(values)
        days = self._days(values)
        role = self._optional_text(values, "role", "field_role")
        apply_type = self._apply_type(values)
        scope = self._scope(values)
        extra: Dict[str, Any] = {}
        for key, label in (("reason", "field_reason"), ("sensitive", "field_sensitive"),
                           ("export", "field_export")):
            text = self._optional_text(values, key, label)
            if text:
                extra[key] = text
        # 权限模板：P2 只留注入点。模板名先记台账；注入 resolver 后展开为多个授权条目。
        template = self._optional_text(values, "template", "field_template")
        if template:
            extra["template"] = template
        if template and self.template_resolver and not self._resource_configured():
            resources: List[Dict[str, Any]] = []
        else:
            resources = self._resources(values, apply_type)

        items: List[Dict[str, Any]] = []
        if template and self.template_resolver and not resources:
            resolved = self.template_resolver(template, {
                "user": user, "days": days, "role": role,
                "actions": list(actions), "data_scope": dict(scope),
                "extra": dict(extra)})
            items = [self._template_item(raw, template) for raw in (resolved or [])]
            if not items:
                raise FormParseError("权限模板「%s」未展开出授权条目" % template)
        if resources:
            for res in resources:
                resource_type = res.get("resource_type") or apply_type
                resource_type = self.resource_type_map.get(resource_type, resource_type)
                item: Dict[str, Any] = {
                    "resource_type": str(resource_type or ""),
                    "resource_id": str(res.get("resource_id") or ""),
                    "actions": list(actions),
                    "data_scope": dict(scope) if str(resource_type) == ResourceType.ROW else {},
                }
                if role:
                    item["role"] = role
                item["extra"] = {"resource_name": res.get("resource_name") or ""}
                if template:
                    item["extra"]["template"] = template
                items.append(item)
        elif not items and apply_type == ResourceType.ROLE:
            if not role:
                raise FormParseError("申请类型为「角色」，但表单缺少角色字段（字段映射：field_role）")
            resource_type, resource_id = ResourceType.ROLE, role
        elif not items and apply_type:
            raise FormParseError(
                "表单「%s」未选择数据资源（字段映射：field_resource）"
                % self._mapping_label("resource", "field_resource", "数据资源"))
        elif not items:
            raise FormParseError(
                "表单缺少申请类型或数据资源：请检查 policy.form_mapping 配置")

        first_scope: Dict[str, Any] = dict(scope)
        first_actions: List[str] = list(actions)
        if items:
            first = items[0]
            resource_type = first["resource_type"]
            resource_id = first["resource_id"]
            first_scope = dict(first.get("data_scope") or scope)
            first_actions = list(first.get("actions") or actions)
            if not resource_id:
                raise FormParseError("数据资源缺少资源 ID（字段映射：id_column%r）"
                                     % self._id_column())
        if resource_type not in ResourceType.ALL:
            raise FormParseError("无法识别的资源类型：%r（resource_type_map 未映射）"
                                 % (resource_type,))
        if resource_type == ResourceType.ROW and not (first_scope.get("rules")
                                                      or scope.get("rules")):
            raise FormParseError(
                "行权限申请必须填写数据范围（字段映射：field_scope，格式「字段=值1,值2;字段=值」）")

        request = PermissionRequest(
            user=user,
            resource_type=str(resource_type),
            resource_id=str(resource_id),
            actions=first_actions,
            data_scope=dict(first_scope) if resource_type == ResourceType.ROW else {},
            role=role,
            days=days,
            source=str(values.get("_instance_code") or ""),
            extra=extra,
            items=items if len(items) > 1 else [],
        )
        if request.source:
            request.request_id = _deterministic_id(request.source)
        return request

    def parse_instance(self, instance: Any,
                       require_approved: bool = True) -> PermissionRequest:
        """解析审批实例 → ``PermissionRequest``；默认要求状态为 APPROVED。

        设计修订 V1.1 §1.2：执行前以实例详情为准，非 APPROVED 不执行。
        另外拦截 ``reverted=true``（单据已被撤销/替换），避免按旧实例继续授权。
        """
        data = self._instance_data(instance)
        status = str(data.get("status") or "")
        instance_code = str(data.get("instance_code") or data.get("code")
                            or data.get("uuid") or "")
        if require_approved and status != "APPROVED":
            raise FormParseError("审批实例状态不是 APPROVED：%s（instance=%s）"
                                 % (status or "<空>", instance_code or "<空>"))
        if require_approved and data.get("reverted"):
            raise FormParseError("审批实例已被撤销（reverted=true），不执行授权"
                                 "（instance=%s）" % (instance_code or "<空>"))
        request = self.to_request(self.parse(instance))
        extra = {
            "instance_code": instance_code,
            "status": status,
            "serial_number": data.get("serial_number") or "",
            "approval_name": data.get("approval_name") or "",
            "feishu_user_id": data.get("user_id") or "",
            "feishu_open_id": data.get("open_id") or "",
            "reverted": bool(data.get("reverted") or False),
        }
        request.extra.update({k: v for k, v in extra.items() if v not in ("", None, False)})
        if instance_code and not request.source:
            request.source = instance_code
            request.request_id = _deterministic_id(instance_code)
        return request

    # ---------- 字段读取 ----------
    @staticmethod
    def _instance_data(instance: Any) -> Dict[str, Any]:
        if isinstance(instance, dict):
            data = instance.get("data")
            if isinstance(data, dict) and "form" not in instance:
                return data
            return instance
        raise FormParseError("审批实例不是对象：%r" % type(instance).__name__)

    def _normalize_spec(self, key: str, legacy_key: str) -> Optional[Dict[str, Any]]:
        spec = self.fields.get(key)
        if spec is None:
            legacy_name = self.mapping.get(legacy_key)
            if legacy_name:
                spec = legacy_name
        if spec is None:
            return None
        if isinstance(spec, str):
            return {"widget": spec}
        if isinstance(spec, dict):
            return dict(spec)
        raise FormParseError("表单映射 %s 结构不合法：%r" % (legacy_key, spec))

    def _mapping_label(self, key: str, legacy_key: str, default_label: str) -> str:
        spec = self._normalize_spec(key, legacy_key)
        if not spec:
            return default_label
        for candidate in (spec.get("widget_id"), spec.get("widget"), spec.get("name"),
                          spec.get("id"), spec.get("custom_id")):
            if candidate:
                return str(candidate)
        return default_label

    def _find_widget(self, spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        candidates = [spec.get(k) for k in
                      ("widget_id", "widget", "id", "custom_id", "name") if spec.get(k)]
        for candidate in candidates:
            for key in (str(candidate), _norm(candidate)):
                widget = self.widgets.get(key)
                if widget is not None:
                    return widget
        return None

    def _widget_value(self, values: Dict[str, Any], key: str, legacy_key: str,
                      label: str, required: bool) -> Tuple[Any, Dict[str, Any]]:
        spec = self._normalize_spec(key, legacy_key)
        if spec is None:
            if required:
                raise FormParseError(
                    "配置 policy.form_mapping 缺少字段映射：%s（%s）" % (legacy_key, label))
            return None, {}
        widget = self._find_widget(spec)
        if widget is not None:
            return widget.get("value"), widget
        # 兼容直接传入取值字典（旧 FormMapper.parse 的输出）
        for candidate in (spec.get("widget_id"), spec.get("widget"), spec.get("id"),
                          spec.get("custom_id"), spec.get("name"), legacy_key):
            if candidate and str(candidate) in values:
                return values[str(candidate)], {"value": values[str(candidate)]}
        if required:
            raise FormParseError(
                "审批表单缺少必需控件「%s」（字段映射：%s）" % (label, legacy_key))
        return None, {}

    def _required_text(self, values, key: str, legacy_key: str, label: str) -> str:
        raw, _widget = self._widget_value(values, key, legacy_key, label, required=True)
        text = _as_text(raw)
        if not text:
            raise FormParseError("审批表单控件「%s」为空或无法解析（字段映射：%s）"
                                 % (self._mapping_label(key, legacy_key, label), legacy_key))
        return text

    def _optional_text(self, values, key: str, legacy_key: str) -> str:
        raw, _widget = self._widget_value(values, key, legacy_key, legacy_key, required=False)
        return _as_text(raw)

    def _apply_type(self, values: Dict[str, Any]) -> str:
        raw, _widget = self._widget_value(values, "apply_type", "field_type",
                                          "申请类型", required=False)
        text = _as_text(raw)
        if not text:
            return ""
        return self.resource_type_map.get(text, text)

    def _actions(self, values: Dict[str, Any]) -> List[str]:
        raw, _widget = self._widget_value(values, "actions", "field_actions",
                                          "权限项", required=False)
        actions: List[str] = []
        for item in _as_list(raw):
            text = _as_text(item)
            if not text:
                continue
            mapped = self.action_map.get(text, text)
            if mapped not in actions:
                actions.append(mapped)
        return actions

    def _days(self, values: Dict[str, Any]) -> int:
        raw, _widget = self._widget_value(values, "days", "field_days", "使用期限", required=False)
        if raw is None or raw == "" or raw == []:
            return self.default_days
        if isinstance(raw, bool):
            raise FormParseError("使用期限控件值无法解析：%r" % (raw,))
        if isinstance(raw, (int, float)):
            days = int(raw)
        else:
            match = _NUMBER_RE.search(str(raw))
            if not match:
                raise FormParseError("使用期限控件值无法解析：%r（应为 90/90天）" % (raw,))
            days = int(match.group(1))
        if days <= 0:
            raise FormParseError("使用期限必须大于 0：%r" % (raw,))
        return days

    def _scope(self, values: Dict[str, Any]) -> Dict[str, Any]:
        raw, _widget = self._widget_value(values, "row_scope", "field_scope",
                                          "数据范围", required=False)
        if raw is None or raw == "" or raw == [] or raw == {}:
            return {}
        rules: List[Dict[str, Any]] = []
        if isinstance(raw, dict):
            for dimension, dimension_values in raw.items():
                _append_rule(rules, self.row_field_ids, dimension, dimension_values)
        elif isinstance(raw, (list, tuple)):
            for item in raw:
                if isinstance(item, dict):
                    dimension = item.get("field") or item.get("name") or item.get("dimension")
                    dimension_values = (item.get("values") or item.get("value")
                                        or item.get("filterValue"))
                    _append_rule(rules, self.row_field_ids, dimension, dimension_values)
                else:
                    _parse_scope_text(rules, self.row_field_ids, _as_text(item))
        else:
            _parse_scope_text(rules, self.row_field_ids, _as_text(raw))
        return {"rules": rules} if rules else {}

    def _resource_configured(self) -> bool:
        return bool(self._normalize_spec("resource", "field_resource"))

    def _id_column(self) -> str:
        spec = self._normalize_spec("resource", "field_resource") or {}
        return str(spec.get("id_column") or "资源ID")

    def _resources(self, values: Dict[str, Any], apply_type: str) -> List[Dict[str, Any]]:
        if apply_type == ResourceType.ROLE and not self._normalize_spec("resource", "field_resource"):
            return []
        spec = self._normalize_spec("resource", "field_resource")
        raw, widget = self._widget_value(values, "resource", "field_resource",
                                         "数据资源", required=False)
        if raw in (None, "", [], {}) and widget == {}:
            if apply_type == ResourceType.ROLE:
                return []
            if spec is None and not self.mapping.get("field_resource"):
                raise FormParseError(
                    "配置 policy.form_mapping 缺少字段映射：field_resource（数据资源）")
            return []
        records = _as_records(raw)
        resources: List[Dict[str, Any]] = []
        id_keys = [spec.get("id_column") if spec else None, "资源ID", "resource_id",
                   "资源id", "资源编号", "id", "value"]
        name_keys = [spec.get("name_column") if spec else None, "资源名称", "资源名",
                     "name", "资源", "title"]
        type_keys = [spec.get("type_column") if spec else None, "资源类型", "resource_type",
                     "申请类型", "type"]
        for record in records:
            name = _as_string(_pick(record, name_keys))
            if not name and "value" in record:
                # 旧表单把资源名称直接作为文本控件值
                name = _as_string(_pick(record, ["value"]))
            resource_id = _as_string(_pick(record, id_keys))
            raw_type = _as_string(_pick(record, type_keys))
            mapped = self.resources.get(name) if name else None
            if mapped:
                mapped_id = _as_string(mapped.get("resource_id"))
                if mapped_id and (not resource_id or resource_id == name):
                    resource_id = mapped_id
                if not raw_type:
                    raw_type = _as_string(mapped.get("resource_type"))
            if not resource_id and name:
                # 资源名称可能是多维表格里被引用的一列，直接当 ID 用；仍找不到则报错
                resource_id = name
            resource_type = self.resource_type_map.get(raw_type, raw_type) if raw_type else ""
            if not resource_id:
                continue
            resources.append({"resource_id": resource_id,
                              "resource_type": resource_type or apply_type,
                              "resource_name": name})
        if not resources and records:
            raise FormParseError(
                "数据资源控件有值但无法解析出资源 ID（id_column=%r，可用字段：%s）"
                % (self._id_column(), sorted(records[0].keys())))
        return resources


    @staticmethod
    def _template_item(raw: Any, template: str) -> Dict[str, Any]:
        """规范化权限模板展开出的单个授权条目（结构同 PermissionRequest.items）。"""
        if not isinstance(raw, dict):
            raise FormParseError("权限模板「%s」条目必须是对象：%r" % (template, raw))
        resource_type = str(raw.get("resource_type") or raw.get("type") or "")
        resource_id = str(raw.get("resource_id") or raw.get("id") or "")
        if not resource_type:
            raise FormParseError("权限模板「%s」条目缺少 resource_type" % template)
        if not resource_id:
            raise FormParseError("权限模板「%s」条目缺少 resource_id" % template)
        item: Dict[str, Any] = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "actions": [str(action) for action in (raw.get("actions") or [])],
            "data_scope": dict(raw.get("data_scope") or {}),
            "extra": dict(raw.get("extra") or {}),
        }
        if raw.get("role"):
            item["role"] = str(raw["role"])
        item["extra"]["template"] = template
        return item


# 兼容旧 ``services.poller.FormMapper``：同样的构造参数与 parse/to_request 方法。
class FormMapper(FormParser):
    """向后兼容别名：``FormMapper(mapping)`` = ``FormParser(mapping)``。"""


# ---------------------------------------------------------------------------
# 数据范围文本解析
# ---------------------------------------------------------------------------
def _append_rule(rules: List[Dict[str, Any]], field_ids: Dict[str, str],
                 dimension: Any, values: Any) -> None:
    if not dimension:
        return
    dimension = str(dimension).strip()
    value_list = [v.strip() for v in
                  re.split(r"[,，、]", ",".join(str(x) for x in _as_list(values)))
                  if v.strip()]
    if not value_list:
        return
    rules.append({
        "type": "strIn",
        "fieldId": field_ids.get(dimension, dimension),
        "filterValue": value_list,
    })


def _parse_scope_text(rules: List[Dict[str, Any]], field_ids: Dict[str, str],
                      text: str) -> None:
    if not text:
        return
    for part in re.split(r"[;；]", text):
        if "=" not in part:
            continue
        dimension, values = part.split("=", 1)
        _append_rule(rules, field_ids, dimension, values)


def _as_string(value: Any) -> str:
    return "" if value is None else str(value).strip()
