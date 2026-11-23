"""跨进程资源锁：基于 SQLite resource_locks 表，带 TTL 与等待。"""
from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterator, Optional

from .errors import BusinessError


class LockTimeout(BusinessError):
    """获取锁超时（E5001）。"""


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class ResourceLock:
    def __init__(self, db_path: str, ttl: int = 120, wait: int = 30,
                 poll_interval: float = 0.2):
        self.db_path = db_path
        self.ttl = ttl
        self.wait = wait
        self.poll_interval = poll_interval

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5, isolation_level=None)
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("CREATE TABLE IF NOT EXISTS resource_locks("
                     "lock_key TEXT PRIMARY KEY, owner TEXT NOT NULL, expires_at TEXT NOT NULL)")
        return conn

    def acquire(self, key: str, owner: str) -> bool:
        """尝试获取锁；成功返回 True，超时抛 LockTimeout。"""
        deadline = time.time() + self.wait
        while True:
            if self._try_once(key, owner):
                return True
            if time.time() >= deadline:
                raise LockTimeout("获取资源锁超时：%s" % key)
            time.sleep(self.poll_interval)

    def _try_once(self, key: str, owner: str) -> bool:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            now = _now_iso()
            conn.execute("DELETE FROM resource_locks WHERE lock_key=? AND expires_at<=?",
                         (key, now))
            expires = (datetime.now().astimezone()
                       + timedelta(seconds=self.ttl)).isoformat(timespec="seconds")
            try:
                conn.execute("INSERT INTO resource_locks(lock_key, owner, expires_at) "
                             "VALUES(?,?,?)", (key, owner, expires))
                conn.execute("COMMIT")
                return True
            except sqlite3.IntegrityError:
                conn.execute("ROLLBACK")
                return False
        finally:
            conn.close()

    def release(self, key: str, owner: str) -> bool:
        conn = self._connect()
        try:
            cur = conn.execute("DELETE FROM resource_locks WHERE lock_key=? AND owner=?",
                               (key, owner))
            return cur.rowcount > 0
        finally:
            conn.close()

    @contextmanager
    def hold(self, key: str, owner: str) -> Iterator[None]:
        self.acquire(key, owner)
        try:
            yield
        finally:
            self.release(key, owner)

    def is_locked(self, key: str) -> bool:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT 1 FROM resource_locks WHERE lock_key=? AND expires_at>?",
                (key, _now_iso())).fetchone()
            return row is not None
        finally:
            conn.close()
