-- Web 授权页改版：申请分类、周期类型、资源 Owner
ALTER TABLE web_requests ADD COLUMN category TEXT NOT NULL DEFAULT 'dashboard';
ALTER TABLE web_requests ADD COLUMN period_type TEXT NOT NULL DEFAULT 'temp';

CREATE TABLE IF NOT EXISTS resource_owners (
    id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    owner_user_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_resource_owner
    ON resource_owners(resource_type, resource_id, owner_user_id);
CREATE INDEX IF NOT EXISTS ix_resource_owners_res
    ON resource_owners(resource_type, resource_id);
