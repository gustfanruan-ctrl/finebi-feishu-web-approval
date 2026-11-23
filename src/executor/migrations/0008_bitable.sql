CREATE TABLE IF NOT EXISTS request_serials(
    day TEXT PRIMARY KEY,
    seq INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bitable_records(
    request_id TEXT PRIMARY KEY,
    record_id TEXT NOT NULL,
    table_id TEXT DEFAULT '',
    updated_at TEXT NOT NULL
);
