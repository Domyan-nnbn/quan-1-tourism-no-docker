ALTER TABLE pois ADD COLUMN IF NOT EXISTS listen_count INTEGER NOT NULL DEFAULT 0;
UPDATE pois p SET listen_count = counts.total
FROM (
    SELECT poi_id, COUNT(*)::INTEGER AS total
    FROM analytics_events
    WHERE kind = 'narration_started'
    GROUP BY poi_id
) counts
WHERE p.id = counts.poi_id;
DO $$ BEGIN
    ALTER TABLE pois ADD CONSTRAINT ck_pois_listen_count_nonnegative CHECK (listen_count >= 0);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
