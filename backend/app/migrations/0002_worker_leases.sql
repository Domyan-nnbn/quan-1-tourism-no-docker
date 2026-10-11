ALTER TABLE jobs ADD COLUMN IF NOT EXISTS lease_owner VARCHAR(36);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS lease_until TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS worker_heartbeats (id VARCHAR(36) PRIMARY KEY, seen_at TIMESTAMPTZ NOT NULL);
CREATE INDEX IF NOT EXISTS ix_worker_heartbeats_seen_at ON worker_heartbeats(seen_at);
