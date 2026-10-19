-- Deduplicate one TTS playback start across retries / repeated callbacks.
-- Anonymous random UUID only; not linked to accounts, GPS positions or consent.
CREATE TABLE IF NOT EXISTS listen_sessions (
    id VARCHAR(36) PRIMARY KEY,
    poi_id VARCHAR(36) NOT NULL REFERENCES pois(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_listen_sessions_created_at ON listen_sessions (created_at);
