# -*- coding: utf-8 -*-
import unittest

from executor.domain.validators import ParentChildError, check_parent_empower


class FakeFineBI:
    def __init__(self, empower):
        self.empower = empower

    def get_folder_permission(self, user, pack_id):
        return {"status": 200, "data": [{"status": True,
                                         "data": {"empowerPrivilege": self.empower}}]}


RESOURCES = {
    "child": {"resource_id": "child", "parent": "parent"},
    "parent": {"resource_id": "parent"},
}


class ParentChildTest(unittest.TestCase):
    def test_parent_empower_blocks_child_close(self):
        with self.assertRaises(ParentChildError):
            check_parent_empower(FakeFineBI(True), RESOURCES, "10086", "child")

    def test_parent_without_empower_allows(self):
        check_parent_empower(FakeFineBI(False), RESOURCES, "10086", "child")

    def test_no_hierarchy_skips(self):
        check_parent_empower(FakeFineBI(True), {}, "10086", "child")

    def test_unknown_resource_skips(self):
        check_parent_empower(FakeFineBI(True), RESOURCES, "10086", "missing")


if __name__ == "__main__":
    unittest.main()
