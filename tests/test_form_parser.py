# -*- coding: utf-8 -*-
"""form_parser 单测：配置化控件解析、缺字段异常、旧 FormMapper 兼容。"""
import json
import unittest

from executor.feishu.form_parser import (FormMapper, FormParseError, FormParser,
                                         flatten_form, parse_form, widget_index)
from executor.services.poller import FormMapper as LegacyFormMapper

LEGACY_MAPPING = {
    "field_user": "FineBI账号",
    "field_resource": "数据资源",
    "field_actions": "权限项",
    "field_days": "使用期限",
    "field_scope": "数据范围",
    "field_role": "角色",
    "default_days": 90,
    "resource_type_map": {
        "文件夹使用": "folder",
        "数据集使用": "table",
        "行权限": "row",
        "列权限": "field",
    },
    "action_map": {
        "使用": "use", "管理": "manage", "授权": "empower",
        "导出": "export", "查看": "view", "编辑": "edit",
    },
    "row_field_ids": {"大区": "t_region", "渠道": "t_channel"},
    "resources": {
        "销售数据集": {"resource_type": "table", "resource_id": "t-001"},
        "销售文件夹": {"resource_type": "folder", "resource_id": "p-001"},
    },
}

STRUCTURED_MAPPING = {
    "fields": {
        "user": {"widget_id": "fb_account"},
        "resource": {"widget_id": "resources", "id_column": "资源ID",
                     "type_column": "资源类型"},
        "actions": {"widget_id": "perms"},
        "days": {"widget_id": "days"},
        "row_scope": {"widget_id": "row_scope"},
        "role": {"widget_id": "role"},
    },
    "default_days": 30,
    "resource_type_map": LEGACY_MAPPING["resource_type_map"],
    "action_map": LEGACY_MAPPING["action_map"],
    "row_field_ids": LEGACY_MAPPING["row_field_ids"],
}


def widget(name, value, widget_type="input", custom_id="", widget_id=""):
    item = {"id": widget_id or ("w-" + (custom_id or name)),
            "name": name, "type": widget_type, "value": value}
    if custom_id:
        item["custom_id"] = custom_id
    return item


def make_instance(form, status="APPROVED", instance_code="INST-001"):
    return {
        "instance_code": instance_code,
        "status": status,
        "serial_number": "SER-1",
        "approval_name": "测试审批",
        "user_id": "u-feishu-1",
        "form": form if isinstance(form, str) else json.dumps(form, ensure_ascii=False),
    }


def standard_form():
    return [
        widget("FineBI账号", "10086", custom_id="fb_account"),
        widget("数据资源", [{"资源名称": "销售数据集", "资源ID": "t-001",
                             "资源类型": "数据集使用"}],
               widget_type="mutableGroup", custom_id="resources"),
        widget("权限项", ["使用", "管理"], widget_type="checkbox", custom_id="perms"),
        widget("使用期限", "90天", widget_type="radio", custom_id="days"),
        widget("数据范围", "大区=华东,华南;渠道=天猫",
               widget_type="textarea", custom_id="row_scope"),
        widget("角色", "电商-渠道运营", custom_id="role"),
    ]


class FormParserTest(unittest.TestCase):
    def test_parse_legacy_flat_mapping(self):
        parser = FormParser(LEGACY_MAPPING)
        req = parser.parse_instance(make_instance(standard_form()))
        self.assertEqual(req.user, "10086")
        self.assertEqual(req.resource_type, "table")
        self.assertEqual(req.resource_id, "t-001")
        self.assertEqual(req.actions, ["use", "manage"])
        self.assertEqual(req.days, 90)
        self.assertEqual(req.role, "电商-渠道运营")
        self.assertEqual(req.source, "INST-001")
        self.assertEqual(req.extra.get("serial_number"), "SER-1")
        self.assertEqual(req.data_scope, {})  # table 单条不带行规则，规则属于 row 条目
        self.assertEqual(req.items, [])       # 单资源沿用旧单条目结构

    def test_structured_mapping_equivalent(self):
        parser = FormParser(STRUCTURED_MAPPING, resources=LEGACY_MAPPING["resources"])
        req = parser.parse_instance(make_instance(standard_form()))
        self.assertEqual(req.user, "10086")
        self.assertEqual(req.resource_id, "t-001")
        self.assertEqual(req.actions, ["use", "manage"])

    def test_contact_widget_user_value(self):
        form = standard_form()
        form[0] = {"id": "w-user", "custom_id": "fb_account",
                   "name": "FineBI账号", "type": "contact",
                   "value": ["10086"], "open_ids": ["ou_x"]}
        parser = FormParser(LEGACY_MAPPING)
        req = parser.parse_instance(make_instance(form))
        self.assertEqual(req.user, "10086")

    def test_radio_single_action(self):
        form = standard_form()
        form[2] = widget("权限项", "使用", widget_type="radio", custom_id="perms")
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(req.actions, ["use"])

    def test_multiple_resources_become_items(self):
        form = standard_form()
        form[1] = widget("数据资源", [
            {"资源名称": "销售数据集", "资源ID": "t-001", "资源类型": "数据集使用"},
            {"资源名称": "销售文件夹", "资源ID": "p-001", "资源类型": "文件夹使用"},
        ], widget_type="mutableGroup")
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(len(req.items), 2)
        self.assertEqual([i["resource_id"] for i in req.items], ["t-001", "p-001"])
        self.assertEqual(req.resource_id, "t-001")  # 主条目取第一条

    def test_resource_name_fallback_to_catalog(self):
        form = standard_form()
        form[1] = widget("数据资源", [{"资源名称": "销售文件夹"}],
                         widget_type="mutableGroup")
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(req.resource_type, "folder")
        self.assertEqual(req.resource_id, "p-001")

    def test_legacy_text_resource_name(self):
        form = standard_form()
        form[1] = widget("数据资源", "销售数据集")
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(req.resource_type, "table")
        self.assertEqual(req.resource_id, "t-001")

    def test_row_scope_rules(self):
        form = standard_form()
        form[1] = widget("数据资源", [{"资源名称": "销售数据集", "资源ID": "t-001",
                                       "资源类型": "行权限"}],
                         widget_type="mutableGroup")
        form[2] = widget("权限项", ["使用"], widget_type="checkbox")
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(req.resource_type, "row")
        rules = req.data_scope["rules"]
        self.assertEqual({r["fieldId"] for r in rules}, {"t_region", "t_channel"})
        self.assertEqual(rules[0]["type"], "strIn")

    def test_missing_user_raises_clear_error(self):
        form = [w for w in standard_form() if w["name"] != "FineBI账号"]
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertIn("FineBI账号", str(ctx.exception))

    def test_missing_user_mapping_raises(self):
        mapping = dict(LEGACY_MAPPING)
        mapping.pop("field_user")
        with self.assertRaises(FormParseError) as ctx:
            FormParser(mapping).parse_instance(make_instance(standard_form()))
        self.assertIn("field_user", str(ctx.exception))

    def test_missing_resource_value_raises(self):
        form = standard_form()
        form[1] = widget("数据资源", [], widget_type="mutableGroup")
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertIn("数据资源", str(ctx.exception))

    def test_row_without_scope_raises(self):
        form = standard_form()
        form[1] = widget("数据资源", [{"资源名称": "销售数据集", "资源ID": "t-001",
                                       "资源类型": "行权限"}],
                         widget_type="mutableGroup")
        form[2] = widget("权限项", ["使用"], widget_type="checkbox")
        form[4] = widget("数据范围", "", widget_type="textarea")
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertIn("数据范围", str(ctx.exception))

    def test_invalid_form_json_raises(self):
        with self.assertRaises(FormParseError):
            parse_form("{not-json")
        with self.assertRaises(FormParseError):
            parse_form(None)

    def test_invalid_days_raises(self):
        form = standard_form()
        form[3] = widget("使用期限", "很久", widget_type="radio")
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertIn("使用期限", str(ctx.exception))

    def test_empty_status_refused(self):
        """状态为空（详情缺字段/异常响应）不能当 APPROVED 执行。"""
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(
                make_instance(standard_form(), status=""))
        self.assertIn("APPROVED", str(ctx.exception))

    def test_reverted_instance_refused(self):
        """详情 reverted=true（单据已撤销/被新实例替换）不执行授权。"""
        instance = make_instance(standard_form())
        instance["reverted"] = True
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(instance)
        self.assertIn("reverted", str(ctx.exception))
        # require_approved=False 时保留旧行为（仅解析，不执行）
        req = FormParser(LEGACY_MAPPING).parse_instance(instance, require_approved=False)
        self.assertEqual(req.user, "10086")

    def test_default_days_when_missing(self):
        form = [w for w in standard_form() if w["name"] != "使用期限"]
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(req.days, 90)

    def test_numeric_days(self):
        form = standard_form()
        form[3] = widget("使用期限", 60, widget_type="number")
        req = FormParser(LEGACY_MAPPING).parse_instance(make_instance(form))
        self.assertEqual(req.days, 60)

    def test_rejected_instance_refused(self):
        with self.assertRaises(FormParseError) as ctx:
            FormParser(LEGACY_MAPPING).parse_instance(
                make_instance(standard_form(), status="REJECTED"))
        self.assertIn("APPROVED", str(ctx.exception))
        req = FormParser(LEGACY_MAPPING).parse_instance(
            make_instance(standard_form(), status="REJECTED"), require_approved=False)
        self.assertEqual(req.user, "10086")

    def test_deterministic_request_id(self):
        parser = FormParser(LEGACY_MAPPING)
        first = parser.parse_instance(make_instance(standard_form()))
        second = parser.parse_instance(make_instance(standard_form()))
        self.assertTrue(first.request_id.startswith("req-"))
        self.assertEqual(first.request_id, second.request_id)

    def test_flatten_nested_children(self):
        form = [
            {"id": "w1", "name": "明细", "type": "fieldList",
             "value": [[{"id": "w2", "name": "子项", "type": "input", "value": "v2"}]]},
            {"id": "w3", "name": "外层", "type": "input", "value": "v3"},
        ]
        values = flatten_form(form)
        self.assertEqual(values["子项"], "v2")
        self.assertEqual(values["外层"], "v3")

    def test_widget_index_keys(self):
        index = widget_index(parse_form(standard_form()))
        self.assertIn("fb_account", index)
        self.assertIn("FineBI账号", index)

    def test_legacy_formmapper_compatible(self):
        """新旧 FormMapper 对同一旧式表单解析出等价请求。"""
        form = [
            widget("FineBI账号", "10086"),
            widget("数据资源", "销售数据集"),
            widget("权限项", ["使用"], widget_type="checkbox"),
            widget("使用期限", "30天"),
            widget("数据范围", "大区=华东"),
            widget("角色", "运营角色"),
        ]
        instance = make_instance(form)
        legacy = LegacyFormMapper(LEGACY_MAPPING)
        old_req = legacy.to_request(legacy.parse(instance))
        new_req = FormMapper(LEGACY_MAPPING).to_request(FormMapper(LEGACY_MAPPING).parse(instance))
        for attr in ("user", "resource_type", "resource_id", "actions", "role",
                     "days", "source"):
            self.assertEqual(getattr(old_req, attr), getattr(new_req, attr), attr)

    def test_legacy_parse_keys(self):
        instance = make_instance(standard_form())
        parser = FormParser(LEGACY_MAPPING)
        values = parser.parse(instance)
        self.assertEqual(values["_instance_code"], "INST-001")
        self.assertEqual(values["_status"], "APPROVED")
        self.assertEqual(values["FineBI账号"], "10086")

    # ---------- 权限模板接口（P2 只留注入点） ----------
    def test_template_name_recorded_without_resolver(self):
        mapping = dict(LEGACY_MAPPING)
        mapping["field_template"] = "权限模板"
        form = standard_form()
        form.append(widget("权限模板", "标准分析包"))
        req = FormParser(mapping).parse_instance(make_instance(form))
        self.assertEqual(req.extra.get("template"), "标准分析包")

    def test_template_resolver_expands_items(self):
        mapping = {
            "field_user": "FineBI账号",
            "field_template": "权限模板",
            "resource_type_map": {"数据集使用": "table", "行权限": "row"},
            "action_map": {"使用": "use"},
            "row_field_ids": {"大区": "t_region"},
        }

        def resolver(name, context):
            self.assertEqual(name, "标准分析包")
            self.assertEqual(context["user"], "10086")
            return [
                {"resource_type": "table", "resource_id": "t-001",
                 "actions": ["use"]},
                {"resource_type": "row", "resource_id": "t-001",
                 "actions": ["use"],
                 "data_scope": {"rules": [{"type": "strIn", "fieldId": "t_region",
                                           "filterValue": ["华东"]}]}},
            ]

        form = [
            widget("FineBI账号", "10086"),
            widget("权限模板", "标准分析包"),
        ]
        parser = FormParser(mapping, template_resolver=resolver)
        req = parser.parse_instance(make_instance(form))
        self.assertEqual(req.extra.get("template"), "标准分析包")
        self.assertEqual(len(req.items), 2)
        self.assertEqual(req.resource_type, "table")
        self.assertEqual(req.items[1]["resource_type"], "row")
        self.assertEqual(req.items[1]["data_scope"]["rules"][0]["fieldId"], "t_region")

    def test_template_resolver_empty_raises(self):
        mapping = {"field_user": "FineBI账号", "field_template": "权限模板"}
        form = [widget("FineBI账号", "10086"), widget("权限模板", "空模板")]
        parser = FormParser(mapping, template_resolver=lambda name, ctx: [])
        with self.assertRaises(FormParseError) as ctx:
            parser.parse_instance(make_instance(form))
        self.assertIn("未展开出授权条目", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
