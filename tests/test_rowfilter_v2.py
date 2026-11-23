# -*- coding: utf-8 -*-
import json
import unittest

from executor.finebi.rowfilter import (DEFAULT_TYPE_MAP, Condition, Group, RowExpr,
                                       RowFilterError, canonical, expr_to_rules,
                                       merge, parse_get, resolve_type_map,
                                       rules_to_expr, to_set_payload)

TYPE_MAP = {34: "and", 35: "or", 10: "strIn", 12: "strNotIn"}


class RowFilterV2Test(unittest.TestCase):
    def test_default_type_map_matches_doc(self):
        """接口文档明确：and:34  or:35  str_in:10  strNotIn:12。"""
        self.assertEqual(DEFAULT_TYPE_MAP, {34: "and", 35: "or",
                                           10: "strIn", 12: "strNotIn"})

    def test_resolve_type_map_keeps_defaults_and_allows_override(self):
        resolved = resolve_type_map({"12": "strNotIn", "99": "custom"})
        self.assertEqual(resolved[35], "or")
        self.assertEqual(resolved[99], "custom")
        self.assertEqual(resolve_type_map()[34], "and")

    def test_parse_without_type_map_uses_doc_defaults(self):
        raw = json.dumps({
            "filterType": 35,
            "filterValue": [
                {"filterType": 10, "fieldId": "t_region",
                 "filterValue": {"type": 1, "value": ["华东"]}},
                {"filterType": 12, "fieldId": "t_region",
                 "filterValue": {"type": 1, "value": ["华南"]}},
            ],
        })
        expr = parse_get(raw)
        self.assertEqual([group.conditions[0].op for group in expr.groups],
                         ["strIn", "strNotIn"])

    def test_parse_nested_and_under_or(self):
        """OR 子节点是 AND 组（手工/其他系统写入）时按整组保留。"""
        raw = json.dumps({
            "filterType": 35,
            "filterValue": [
                {"filterType": 34, "filterValue": [
                    {"filterType": 10, "fieldId": "t_channel",
                     "filterValue": {"type": 1, "value": ["天猫"]}},
                    {"filterType": 12, "fieldId": "t_status",
                     "filterValue": {"type": 1, "value": ["退款"]}},
                ]},
                {"filterType": 10, "fieldId": "t_region",
                 "filterValue": {"type": 1, "value": ["华东"]}},
            ],
        })
        expr = parse_get(raw)
        self.assertEqual(len(expr.groups), 2)
        self.assertEqual(len(expr.groups[0].conditions), 2)
        self.assertEqual(expr.groups[1].conditions[0].field_id, "t_region")

    def test_parse_or_flat(self):
        raw = json.dumps({
            "filterType": 35,
            "filterValue": [
                {"filterType": 10, "fieldId": "t_region", "filterValue": {"type": 1, "value": ["华东"]}},
                {"filterType": 10, "fieldId": "t_region", "filterValue": {"type": 1, "value": ["华南"]}},
            ],
        })
        expr = parse_get(raw, TYPE_MAP)
        self.assertIsNotNone(expr)
        self.assertEqual(len(expr.groups), 2)

    def test_parse_and_group(self):
        raw = json.dumps({
            "filterType": 34,
            "filterValue": [
                {"filterType": 10, "fieldId": "t_channel", "filterValue": {"type": 1, "value": ["天猫"]}},
                {"filterType": 12, "fieldId": "t_status", "filterValue": {"type": 1, "value": ["退款"]}},
            ],
        })
        expr = parse_get(raw, TYPE_MAP)
        self.assertEqual(len(expr.groups), 1)
        self.assertEqual(len(expr.groups[0].conditions), 2)

    def test_unknown_filter_type_raises(self):
        raw = json.dumps({"filterType": 99, "filterValue": [
            {"filterType": 10, "fieldId": "x", "filterValue": {"type": 1, "value": ["1"]}}]})
        with self.assertRaises(RowFilterError):
            parse_get(raw, TYPE_MAP)

    def test_empty_returns_none(self):
        self.assertIsNone(parse_get(None, TYPE_MAP))
        self.assertIsNone(parse_get("", TYPE_MAP))
        self.assertIsNone(parse_get("{}", TYPE_MAP))

    def test_to_set_payload_single_condition(self):
        expr = rules_to_expr([{"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}])
        payload = to_set_payload(expr)
        self.assertEqual(payload["type"], "or")
        self.assertEqual(payload["filterValue"][0]["type"], "strIn")

    def test_to_set_payload_and_group(self):
        expr = RowExpr(groups=(
            Group((
                Condition("t_channel", "strIn", ("天猫",)),
                Condition("t_status", "strIn", ("已支付",)),
            )),
        ))
        payload = to_set_payload(expr)
        self.assertEqual(payload["type"], "or")
        self.assertEqual(payload["filterValue"][0]["type"], "and")

    def test_merge_dedup(self):
        a = rules_to_expr([{"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}])
        b = rules_to_expr([{"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}])
        c = rules_to_expr([{"type": "strIn", "fieldId": "t_region", "filterValue": ["华南"]}])
        merged = merge([a, b, c])
        self.assertEqual(len(merged.groups), 2)

    def test_canonical_order_insensitive(self):
        a = rules_to_expr([
            {"type": "strIn", "fieldId": "b", "filterValue": ["2"]},
            {"type": "strIn", "fieldId": "a", "filterValue": ["1"]},
        ])
        b = rules_to_expr([
            {"type": "strIn", "fieldId": "a", "filterValue": ["1"]},
            {"type": "strIn", "fieldId": "b", "filterValue": ["2"]},
        ])
        self.assertEqual(canonical(a), canonical(b))

    def test_expr_to_rules(self):
        expr = rules_to_expr([{"type": "strIn", "fieldId": "t_region", "filterValue": ["华东"]}])
        rules = expr_to_rules(expr)
        self.assertEqual(rules[0]["fieldId"], "t_region")


if __name__ == "__main__":
    unittest.main()
