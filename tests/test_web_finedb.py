# -*- coding: utf-8 -*-
import json
import unittest
from unittest import mock

import pymysql

from executor.web.finedb import FineDB


class _FakeCursor:
    def __init__(self, owner):
        self.owner = owner
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=()):
        self.rows = self.owner.script(sql, params)

    def fetchall(self):
        return self.rows


class _FakeConn:
    def __init__(self, script):
        self.script = script
        self.closed = False

    def cursor(self):
        return _FakeCursor(self)

    def close(self):
        self.closed = True


class FineDBQueryTest(unittest.TestCase):
    def _db(self):
        return FineDB("127.0.0.1", 3306, "u", "p", "finedb")

    def test_query_retries_after_lost_connection(self):
        db = self._db()
        attempts = []

        def script(sql, params):
            attempts.append(sql)
            if len(attempts) == 1:
                raise pymysql.err.OperationalError(
                    2013, "Lost connection to MySQL server during query")
            return [("x",)]

        with mock.patch.object(FineDB, "_connect",
                               side_effect=lambda: _FakeConn(script)):
            self.assertEqual(db._query("SELECT 1"), [("x",)])
        self.assertEqual(len(attempts), 2)

    def test_query_raises_non_retryable_error(self):
        db = self._db()

        def script(sql, params):
            raise pymysql.err.OperationalError(1045, "Access denied")

        with mock.patch.object(FineDB, "_connect",
                               side_effect=lambda: _FakeConn(script)):
            with self.assertRaises(pymysql.err.OperationalError):
                db._query("SELECT 1")

    def test_row_filter_options_merges_all_rules_for_table(self):
        db = self._db()
        user_rule = json.dumps({
            "fieldId": "t1_sales", "fieldName": "t1_sales",
            "filterValue": {"value": ["A"], "assist": ["B"]},
        }, ensure_ascii=False)
        global_rule_1 = json.dumps({
            "fieldId": "t1_sales", "fieldName": "销售",
            "filterValue": {"type": 1, "value": ["A"],
                            "assist": ["A", "B", "C", "D"]},
        }, ensure_ascii=False)
        # 存量脏数据：JSON 被二次编码成字符串
        global_rule_2 = json.dumps(json.dumps({
            "fieldId": "t1_sales", "fieldName": "销售",
            "filterValue": {"assist": ["E"]},
        }, ensure_ascii=False), ensure_ascii=False)

        def script(sql, params):
            if "fine_pack_filter" in sql:
                return [(user_rule,), (global_rule_1,), (global_rule_2,)]
            return []

        with mock.patch.object(FineDB, "_connect",
                               side_effect=lambda: _FakeConn(script)):
            fields = db.row_filter_options("t1", "张三")
        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0]["name"], "销售")
        self.assertEqual(fields[0]["values"], ["A", "B", "C", "D", "E"])

    def test_distinct_values_wraps_source_sql_without_parameters(self):
        db = self._db()
        captured = {}

        def query(sql, params=()):
            captured["sql"] = sql
            captured["params"] = params
            return [("A",), ("B",), ("A",)]

        db._query = query
        values = db.distinct_values("select region as `大区` from ads.demo",
                                    "大区", limit=20)
        self.assertEqual(values, ["A", "B"])
        self.assertIn("SELECT DISTINCT `大区`", captured["sql"])
        self.assertIn("ads.demo", captured["sql"])
        self.assertEqual(captured["params"], ())

    def test_distinct_values_skips_parameterized_sql(self):
        db = self._db()
        self.assertEqual(db.distinct_values("select * from t where x='${x}'",
                                            "x"), [])

    def test_row_filter_options_returns_empty_when_no_rules(self):
        db = self._db()

        def script(sql, params):
            return []

        with mock.patch.object(FineDB, "_connect",
                               side_effect=lambda: _FakeConn(script)):
            self.assertEqual(db.row_filter_options("t1", ""), [])


if __name__ == "__main__":
    unittest.main()
