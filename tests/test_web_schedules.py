# -*- coding: utf-8 -*-
import unittest
from types import SimpleNamespace

from executor.web.app import _schedules


class _FakePlatform:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def list_schedules(self, page=1, per_page=50):
        self.calls.append(page)
        return self.pages.pop(0)


class SchedulePaginationTest(unittest.TestCase):
    def test_reads_all_pages_and_dedupes(self):
        platform = _FakePlatform([
            {"data": {"hasNext": True, "items": [
                {"id": "t1", "taskName": "任务1"},
                {"id": "t2", "taskName": "任务2"},
            ]}},
            {"data": {"hasNext": False, "items": [
                {"id": "t2", "taskName": "任务2"},
                {"id": "t3", "taskName": "任务3"},
            ]}},
        ])
        result = _schedules(SimpleNamespace(platform=platform))
        self.assertEqual([r["id"] for r in result], ["t1", "t2", "t3"])
        self.assertEqual(platform.calls, [1, 2])

    def test_single_page(self):
        platform = _FakePlatform([
            {"data": {"hasNext": False, "items": [{"id": "t1", "taskName": "任务1"}]}},
        ])
        result = _schedules(SimpleNamespace(platform=platform))
        self.assertEqual(result, [{"id": "t1", "name": "任务1"}])


if __name__ == "__main__":
    unittest.main()
