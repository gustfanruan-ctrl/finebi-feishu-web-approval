CREATE TABLE IF NOT EXISTS user_membership_snapshot(
    user_id TEXT PRIMARY KEY,
    fb_user TEXT NOT NULL,
    roles TEXT NOT NULL DEFAULT '[]',
    departments TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL
);
