# -*- coding: utf-8 -*-
import os
import unittest

from executor.config import _get_optional, _normalize_finebi_base_url


class FineBIBaseUrlTest(unittest.TestCase):
    def test_strips_webroot_decision_and_trailing_slash(self):
        self.assertEqual(
            _normalize_finebi_base_url("http://finebi.example.com:8080/webroot/decision/"),
            "http://finebi.example.com:8080")
        self.assertEqual(
            _normalize_finebi_base_url("http://finebi.example.com:8080"),
            "http://finebi.example.com:8080")
        self.assertEqual(
            _normalize_finebi_base_url("http://host/webroot/decision"),
            "http://host")


class DecUserConfigTest(unittest.TestCase):
    """FineBI 应用身份不能带 decUser；显式留空必须保持为空。"""

    def setUp(self):
        self._saved = os.environ.get("FINEBI_DEC_USER")

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("FINEBI_DEC_USER", None)
        else:
            os.environ["FINEBI_DEC_USER"] = self._saved

    def test_blank_env_stays_blank(self):
        os.environ["FINEBI_DEC_USER"] = ""
        self.assertEqual(_get_optional("FINEBI_DEC_USER", "api_bot"), "")

    def test_whitespace_env_stays_blank(self):
        os.environ["FINEBI_DEC_USER"] = "   "
        self.assertEqual(_get_optional("FINEBI_DEC_USER", "api_bot"), "")

    def test_unset_env_uses_default(self):
        os.environ.pop("FINEBI_DEC_USER", None)
        self.assertEqual(_get_optional("FINEBI_DEC_USER", "api_bot"), "api_bot")

    def test_value_is_trimmed(self):
        os.environ["FINEBI_DEC_USER"] = "  api_bot  "
        self.assertEqual(_get_optional("FINEBI_DEC_USER", ""), "api_bot")


if __name__ == "__main__":
    unittest.main()
