-- Per-POI geofence settings; existing locations retain their circle settings.
ALTER TABLE pois ADD COLUMN IF NOT EXISTS geofence_type VARCHAR(12) NOT NULL DEFAULT 'circle';
ALTER TABLE pois ADD COLUMN IF NOT EXISTS polygon_coordinates JSONB;
ALTER TABLE pois ADD COLUMN IF NOT EXISTS exit_buffer_m INTEGER NOT NULL DEFAULT 20;
ALTER TABLE pois ADD COLUMN IF NOT EXISTS dwell_seconds INTEGER NOT NULL DEFAULT 10;
ALTER TABLE pois ADD COLUMN IF NOT EXISTS gps_accuracy_threshold_m INTEGER NOT NULL DEFAULT 25;
ALTER TABLE pois ADD CONSTRAINT ck_geofence_type CHECK (geofence_type IN ('circle','polygon'));
ALTER TABLE pois ADD CONSTRAINT ck_geofence_exit CHECK (exit_buffer_m BETWEEN 5 AND 100);
ALTER TABLE pois ADD CONSTRAINT ck_geofence_dwell CHECK (dwell_seconds BETWEEN 1 AND 60);
ALTER TABLE pois ADD CONSTRAINT ck_geofence_accuracy CHECK (gps_accuracy_threshold_m BETWEEN 5 AND 50);
