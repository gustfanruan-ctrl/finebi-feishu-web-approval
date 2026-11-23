-- 自建 Web 审批：用户、会话、申请、审批步骤、评论
CREATE TABLE IF NOT EXISTS web_users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    feishu_open_id TEXT,
    fb_user TEXT,
    roles TEXT NOT NULL DEFAULT '[]',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS web_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_web_sessions_expire ON web_sessions(expires_at);

CREATE TABLE IF NOT EXISTS web_requests (
    id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    status TEXT NOT NULL,            -- pending/approved/rejected/withdrawn/granting/done/failed
    risk TEXT NOT NULL,
    payload TEXT NOT NULL,
    result TEXT,
    current_seq INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_web_requests_status ON web_requests(status, updated_at);

CREATE TABLE IF NOT EXISTS web_steps (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    role TEXT NOT NULL,
    approver_id TEXT,
    action TEXT,                     -- pending/approved/rejected/skipped
    comment TEXT,
    acted_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_web_steps_seq ON web_steps(request_id, seq);

CREATE TABLE IF NOT EXISTS web_comments (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_web_comments_req ON web_comments(request_id, created_at);
