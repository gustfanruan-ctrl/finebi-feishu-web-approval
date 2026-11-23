-- 资源 Owner 区分数据 Owner / 业务 Owner（审批链：数据 Owner → 业务 Owner）
ALTER TABLE resource_owners ADD COLUMN owner_type TEXT NOT NULL DEFAULT 'data';

DROP INDEX IF EXISTS ux_resource_owner;
CREATE UNIQUE INDEX IF NOT EXISTS ux_resource_owner_type
    ON resource_owners(resource_type, resource_id, owner_type, owner_user_id);
CREATE INDEX IF NOT EXISTS ix_resource_owners_res
    ON resource_owners(resource_type, resource_id);
