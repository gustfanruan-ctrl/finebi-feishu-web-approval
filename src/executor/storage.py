"""SQLite 台账与迁移：申请单、条目、授权记录、执行日志、任务、资源锁表。"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import new_id, now_iso

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        parent = os.path.dirname(os.path.abspath(db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self._migrate()

    # ---------- 迁移 ----------
    def _migrate(self) -> None:
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations("
            "version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
        applied = {row[0] for row in self.conn.execute("SELECT version FROM schema_migrations")}
        if not os.path.isdir(MIGRATIONS_DIR):
            self.conn.commit()
            return
        for name in sorted(os.listdir(MIGRATIONS_DIR)):
            if not name.endswith(".sql"):
                continue
            version = name[:-4]
            if version in applied:
                continue
            with open(os.path.join(MIGRATIONS_DIR, name), "r", encoding="utf-8") as fh:
                sql = fh.read()
            # 兼容旧库：0001 的表已存在时只登记版本，不重复建表
            baseline = version.startswith("0001") and self._table_exists("requests")
            if not baseline:
                self.conn.executescript(sql)
            self.conn.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES(?, ?)",
                (version, now_iso()))
            self.conn.commit()

    def _table_exists(self, name: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
        return row is not None

    # ---------- requests ----------
    def upsert_request(self, request_id: str, instance_code: str, user: str,
                       payload: Dict[str, Any], status: str = "pending") -> None:
        ts = now_iso()
        self.conn.execute(
            "INSERT INTO requests(id, instance_code, user, payload, status, created_at, updated_at) "
            "VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, "
            "status=excluded.status, updated_at=excluded.updated_at",
            (request_id, instance_code, user, json.dumps(payload, ensure_ascii=False), status, ts, ts))
        self.conn.commit()

    def set_request_status(self, request_id: str, status: str) -> None:
        self.conn.execute("UPDATE requests SET status=?, updated_at=? WHERE id=?",
                          (status, now_iso(), request_id))
        self.conn.commit()

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
        return self._row_to_dict(row)

    def request_status(self, instance_code: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT status FROM requests WHERE instance_code=? ORDER BY created_at DESC LIMIT 1",
            (instance_code,)).fetchone()
        return row["status"] if row else None

    def request_exists(self, instance_code: str) -> bool:
        row = self.conn.execute("SELECT 1 FROM requests WHERE instance_code=? LIMIT 1",
                                (instance_code,)).fetchone()
        return row is not None

    # ---------- request_items ----------
    def add_request_items(self, request_id: str, items: List[Dict[str, Any]]) -> List[str]:
        """写入申请条目（逐项执行与部分成功）。items 至少含 resource_type/resource_id/payload。"""
        ids: List[str] = []
        ts = now_iso()
        for seq, item in enumerate(items, 1):
            item_id = new_id("itm")
            ids.append(item_id)
            self.conn.execute(
                "INSERT INTO request_items(id, request_id, seq, resource_type, resource_id, "
                "payload, status, updated_at) VALUES(?,?,?,?,?,?,?,?)",
                (item_id, request_id, seq, item["resource_type"], item["resource_id"],
                 json.dumps(item.get("payload", item), ensure_ascii=False),
                 item.get("status", "pending"), ts))
        self.conn.commit()
        return ids

    def update_request_item(self, item_id: str, status: str, error_code: str = "",
                            error_msg: str = "", ledger_id: str = "") -> None:
        self.conn.execute(
            "UPDATE request_items SET status=?, error_code=?, error_msg=?, ledger_id=?, "
            "updated_at=? WHERE id=?",
            (status, error_code or None, error_msg or None, ledger_id or None, now_iso(), item_id))
        self.conn.commit()

    def list_request_items(self, request_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM request_items WHERE request_id=? ORDER BY seq", (request_id,))
        return [self._row_to_dict(r) for r in rows]

    # ---------- ledger ----------
    def add_ledger(self, request_id: str, user: str, resource_type: str,
                   resource_id: str, payload: Dict[str, Any], expire_at: str,
                   trace_id: str = "") -> str:
        ledger_id = new_id("led")
        self.conn.execute(
            "INSERT INTO ledger(id, request_id, user, resource_type, resource_id, payload, "
            "status, expire_at, trace_id, created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (ledger_id, request_id, user, resource_type, resource_id,
             json.dumps(payload, ensure_ascii=False), "active", expire_at, trace_id, now_iso()))
        self.conn.commit()
        return ledger_id

    def get_ledger(self, ledger_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM ledger WHERE id=?", (ledger_id,)).fetchone()
        return self._row_to_dict(row)

    def active_ledger(self, user: Optional[str] = None) -> List[Dict[str, Any]]:
        if user:
            rows = self.conn.execute(
                "SELECT * FROM ledger WHERE status='active' AND user=? ORDER BY created_at", (user,))
        else:
            rows = self.conn.execute(
                "SELECT * FROM ledger WHERE status='active' ORDER BY created_at")
        return [self._row_to_dict(r) for r in rows]

    def due_ledger(self, now: Optional[str] = None) -> List[Dict[str, Any]]:
        now = now or now_iso()
        rows = self.conn.execute(
            "SELECT * FROM ledger WHERE status='active' AND expire_at<=? ORDER BY expire_at", (now,))
        return [self._row_to_dict(r) for r in rows]

    def extend_ledger(self, ledger_id: str, expire_at: str) -> None:
        self.conn.execute("UPDATE ledger SET expire_at=?, updated_at=? WHERE id=?",
                          (expire_at, now_iso(), ledger_id))
        self.conn.commit()

    def set_ledger_status(self, ledger_id: str, status: str) -> None:
        self.conn.execute("UPDATE ledger SET status=?, updated_at=? WHERE id=?",
                          (status, now_iso(), ledger_id))
        self.conn.commit()

    def mark_revoked(self, ledger_id: str, note: str = "") -> None:
        self.conn.execute("UPDATE ledger SET status='revoked', revoked_at=? WHERE id=?",
                          (now_iso(), ledger_id))
        self.conn.commit()

    # ---------- jobs（重试/人工待办） ----------
    def enqueue_job(self, kind: str, ref_id: str, next_run_at: str,
                    status: str = "queued") -> str:
        job_id = new_id("job")
        ts = now_iso()
        self.conn.execute(
            "INSERT INTO jobs(id, kind, ref_id, attempts, next_run_at, status, created_at, updated_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (job_id, kind, ref_id, 0, next_run_at, status, ts, ts))
        self.conn.commit()
        return job_id

    def due_jobs(self, now: Optional[str] = None) -> List[Dict[str, Any]]:
        now = now or now_iso()
        rows = self.conn.execute(
            "SELECT * FROM jobs WHERE status='queued' AND next_run_at<=? ORDER BY next_run_at",
            (now,))
        return [self._row_to_dict(r) for r in rows]

    def update_job(self, job_id: str, status: str, attempts: Optional[int] = None,
                   next_run_at: Optional[str] = None, last_error: str = "") -> None:
        current = self.conn.execute("SELECT attempts FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not current:
            return
        self.conn.execute(
            "UPDATE jobs SET status=?, attempts=?, next_run_at=?, last_error=?, updated_at=? "
            "WHERE id=?",
            (status, attempts if attempts is not None else current["attempts"],
             next_run_at or now_iso(), last_error or None, now_iso(), job_id))
        self.conn.commit()

    # ---------- logs ----------
    def log(self, level: str, action: str, message: str, payload: Any = None) -> None:
        self.conn.execute(
            "INSERT INTO logs(ts, level, action, message, payload) VALUES(?,?,?,?,?)",
            (now_iso(), level.upper(), action, message,
             json.dumps(payload, ensure_ascii=False) if payload is not None else None))
        self.conn.commit()

    def recent_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        return [self._row_to_dict(r) for r in rows]

    # ---------- 申请单号 / 多维表格记录 ----------
    def next_request_serial(self, day: str) -> int:
        """按天分配两位自增键（从 1 开始）。"""
        self.conn.execute(
            "INSERT INTO request_serials(day, seq) VALUES(?, 1) "
            "ON CONFLICT(day) DO UPDATE SET seq=seq+1", (day,))
        row = self.conn.execute(
            "SELECT seq FROM request_serials WHERE day=?", (day,)).fetchone()
        self.conn.commit()
        return int(row[0]) if row else 1

    def get_bitable_record_id(self, request_id: str) -> str:
        row = self.conn.execute(
            "SELECT record_id FROM bitable_records WHERE request_id=?",
            (request_id,)).fetchone()
        return str(row[0]) if row and row[0] else ""

    def save_bitable_record_id(self, request_id: str, record_id: str,
                               table_id: str = "") -> None:
        self.conn.execute(
            "INSERT INTO bitable_records(request_id, record_id, table_id, updated_at) "
            "VALUES(?,?,?,?) ON CONFLICT(request_id) DO UPDATE SET "
            "record_id=excluded.record_id, table_id=excluded.table_id, "
            "updated_at=excluded.updated_at",
            (request_id, record_id, table_id, now_iso()))
        self.conn.commit()

    # ---------- 用户角色/部门快照 ----------
    def save_user_membership(self, user_id: str, fb_user: str,
                             roles: List[str], departments: List[str]) -> None:
        self.conn.execute(
            "INSERT INTO user_membership_snapshot(user_id, fb_user, roles, departments, "
            "updated_at) VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET "
            "fb_user=excluded.fb_user, roles=excluded.roles, "
            "departments=excluded.departments, updated_at=excluded.updated_at",
            (user_id, fb_user, json.dumps(roles or [], ensure_ascii=False),
             json.dumps(departments or [], ensure_ascii=False), now_iso()))
        self.conn.commit()

    def get_user_membership(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM user_membership_snapshot WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        for key in ("roles", "departments"):
            try:
                data[key] = json.loads(data.get(key) or "[]")
            except (TypeError, ValueError):
                data[key] = []
        return data

    # ---------- 持久化运行配置 ----------
    def get_setting(self, key: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row and row[0] is not None else None

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO app_settings(key, value, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
            "updated_at=excluded.updated_at",
            (key, value, now_iso()))
        self.conn.commit()

    def delete_setting(self, key: str) -> None:
        self.conn.execute("DELETE FROM app_settings WHERE key=?", (key,))
        self.conn.commit()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Optional[Dict[str, Any]]:
        if row is None:
            return None
        data = dict(row)
        for key in ("payload",):
            if key in data and isinstance(data[key], str):
                try:
                    data[key] = json.loads(data[key])
                except json.JSONDecodeError:
                    pass
        return data

    def close(self) -> None:
        self.conn.close()


def expire_at_from_days(days: int) -> str:
    return (datetime.now().astimezone() + timedelta(days=days)).isoformat(timespec="seconds")
