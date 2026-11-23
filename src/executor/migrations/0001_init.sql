CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    instance_code TEXT,
    user TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_requests_instance ON requests(instance_code);

CREATE TABLE IF NOT EXISTS ledger (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    user TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    expire_at TEXT NOT NULL,
    trace_id TEXT,
    created_at TEXT NOT NULL,
    revoked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_ledger_user ON ledger(user, status);
CREATE INDEX IF NOT EXISTS idx_ledger_expire ON ledger(status, expire_at);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    level TEXT NOT NULL,
    action TEXT NOT NULL,
    message TEXT NOT NULL,
    payload TEXT
);
