# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import tempfile
import time
import unittest

from executor.locks import LockTimeout, ResourceLock


WORKER = r"""
import sys, time
sys.path.insert(0, r"{src}")
from executor.locks import ResourceLock
db, key = sys.argv[1], sys.argv[2]
owner = "worker-%s" % __import__("os").getpid()
lock = ResourceLock(db, ttl=5, wait=10)
lock.acquire(key, owner)
print("start %.6f" % time.time(), flush=True)
time.sleep(1.0)
lock.release(key, owner)
print("end %.6f" % time.time(), flush=True)
"""


class LockTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "lock.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_single_process(self):
        lock = ResourceLock(self.db, ttl=5, wait=1)
        lock.acquire("u:folder:1", "a")
        self.assertTrue(lock.is_locked("u:folder:1"))
        lock.release("u:folder:1", "a")
        self.assertFalse(lock.is_locked("u:folder:1"))

    def test_timeout(self):
        lock1 = ResourceLock(self.db, ttl=5, wait=1)
        lock1.acquire("k", "a")
        lock2 = ResourceLock(self.db, ttl=5, wait=0.3)
        with self.assertRaises(LockTimeout):
            lock2.acquire("k", "b")
        lock1.release("k", "a")

    def test_two_processes_serialized(self):
        src = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
        script = WORKER.format(src=src)
        env = dict(os.environ)
        env["PYTHONPATH"] = src
        procs = [
            subprocess.Popen([sys.executable, "-c", script, self.db, "shared:key"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            for _ in range(2)
        ]
        events = []
        for proc in procs:
            out, err = proc.communicate(timeout=20)
            if proc.returncode != 0:
                self.fail("worker failed: %s" % err)
            for line in out.splitlines():
                parts = line.split()
                if parts and parts[0] in ("start", "end"):
                    events.append((parts[0], float(parts[1])))
        self.assertEqual(len(events), 4)
        events.sort(key=lambda x: x[1])
        # 同一时刻只能有一个持锁：事件序列必须是 start,end,start,end
        self.assertEqual([e[0] for e in events], ["start", "end", "start", "end"])


if __name__ == "__main__":
    unittest.main()
