-- 台账补充更新时间，供 delayed/extend/status 操作记录
ALTER TABLE ledger ADD COLUMN updated_at TEXT;
