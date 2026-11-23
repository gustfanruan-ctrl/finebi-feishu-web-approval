# -*- coding: utf-8 -*-
import unittest

from executor.finebi import rowfilter
from executor.models import (build_authority, merge_row_rules,
                             remove_row_rules)


def rule(field, values, op="strIn"):
    return {"type": op, "fieldId": field, "filterValue": values}


class RowRuleTest(unittest.TestCase):
    def test_merge_dedup(self):
        existing = [rule("t_region", ["华东"])]
        new = [rule("t_region", ["华东"]), rule("t_region", ["华南"])]
        merged = merge_row_rules(existing, new)
        self.assertEqual(merged["type"], "or")
        self.assertEqual(len(merged["filterValue"]), 2)

    def test_merge_keeps_existing(self):
        merged = merge_row_rules([rule("a", ["1"])], [rule("b", ["2"])])
        self.assertEqual([r["fieldId"] for r in merged["filterValue"]], ["a", "b"])

    def test_remove_rule(self):
        existing = [rule("a", ["1"]), rule("b", ["2"])]
        result = remove_row_rules(existing, [rule("a", ["1"])])
        self.assertEqual([r["fieldId"] for r in result["filterValue"]], ["b"])

    def test_remove_all(self):
        result = remove_row_rules([rule("a", ["1"])], [rule("a", ["1"])])
        self.assertEqual(result["filterValue"], [])

    def test_parse_single_condition_node(self):
        data = {"filterType": 10, "fieldId": "t_region",
                "filterValue": {"type": 1, "value": ["华东"]}}
        expr = rowfilter.parse_get(data, {10: "strIn"})
        self.assertEqual(rowfilter.expr_to_rules(expr),
                         [{"type": "strIn", "fieldId": "t_region",
                           "filterValue": ["华东"]}])

    def test_build_authority(self):
        self.assertEqual(build_authority(["use", "manage"]),
                         {"usePrivilege": True, "managePrivilege": True})
        self.assertEqual(build_authority(["view", "export"]),
                         {"view": True, "export": True})


if __name__ == "__main__":
    unittest.main()
