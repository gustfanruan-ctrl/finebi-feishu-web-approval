-- 飞书 user_id 映射（FineDB fine_feishu_user_relation 的 feiShuUser 是 user_id，不是 open_id）
ALTER TABLE web_users ADD COLUMN feishu_user_id TEXT;
CREATE INDEX IF NOT EXISTS ix_web_users_feishu_user ON web_users(feishu_user_id);
