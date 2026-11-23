-- P1 增量迁移：申请条目、重试/待办任务、跨进程资源锁
CREATE TABLE IF NOT EXISTS request_items (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES requests(id),
    seq INTEGER NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',   -- pending/done/skipped/failed/rejected
    error_code TEXT,
    error_msg TEXT,
    ledger_id TEXT,
    updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_items_req_seq ON request_items(request_id, seq);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    ref_id TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    next_run_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',    -- queued/running/done/manual
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_jobs_due ON jobs(status, next_run_at);

CREATE TABLE IF NOT EXISTS resource_locks (
    lock_key TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_locks_expire ON resource_locks(expires_at);
