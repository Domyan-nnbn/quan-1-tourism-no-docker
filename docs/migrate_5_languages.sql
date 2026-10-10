-- Run once in pgAdmin Query Tool on the tourism database.
-- May be run again safely. Does not delete or overwrite existing scripts.
BEGIN;
ALTER TABLE content_versions ADD COLUMN IF NOT EXISTS zh TEXT NOT NULL DEFAULT '';
ALTER TABLE content_versions ADD COLUMN IF NOT EXISTS fr TEXT NOT NULL DEFAULT '';
ALTER TABLE content_versions ADD COLUMN IF NOT EXISTS ja TEXT NOT NULL DEFAULT '';
COMMIT;
