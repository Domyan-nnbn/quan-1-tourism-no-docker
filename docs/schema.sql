-- Initial schema for NEW databases. For existing databases use migrate_5_languages.sql.


CREATE TABLE admins (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	password_hash TEXT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;


CREATE TABLE consents (
	id VARCHAR(36) NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	granted BOOLEAN NOT NULL, 
	policy VARCHAR(20) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (token_hash)
)

;


CREATE TABLE pois (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	name_en VARCHAR(150) NOT NULL, 
	category VARCHAR(40) NOT NULL, 
	address VARCHAR(250) NOT NULL, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	radius INTEGER NOT NULL, 
	source_url TEXT NOT NULL, 
	published_version VARCHAR(36), 
	archived BOOLEAN NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (latitude BETWEEN -90 AND 90), 
	CHECK (longitude BETWEEN -180 AND 180), 
	CHECK (radius BETWEEN 10 AND 500)
)

;

CREATE INDEX ix_pois_category ON pois (category);


CREATE TABLE analytics_events (
	id VARCHAR(36) NOT NULL, 
	consent_id VARCHAR(36) NOT NULL, 
	poi_id VARCHAR(36) NOT NULL, 
	kind VARCHAR(30) NOT NULL, 
	locale VARCHAR(5) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(consent_id) REFERENCES consents (id), 
	FOREIGN KEY(poi_id) REFERENCES pois (id)
)

;

CREATE INDEX ix_analytics_events_consent_id ON analytics_events (consent_id);


CREATE TABLE audit_logs (
	id VARCHAR(36) NOT NULL, 
	admin_id VARCHAR(36) NOT NULL, 
	action VARCHAR(50) NOT NULL, 
	target VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_id) REFERENCES admins (id)
)

;


CREATE TABLE content_versions (
	id VARCHAR(36) NOT NULL, 
	poi_id VARCHAR(36) NOT NULL, 
	vi TEXT NOT NULL, 
	en TEXT NOT NULL, 
	zh TEXT DEFAULT '' NOT NULL, 
	fr TEXT DEFAULT '' NOT NULL, 
	ja TEXT DEFAULT '' NOT NULL, 
	state VARCHAR(24) NOT NULL, 
	source JSON NOT NULL, 
	reviewed_by VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(poi_id) REFERENCES pois (id), 
	FOREIGN KEY(reviewed_by) REFERENCES admins (id)
)

;

CREATE INDEX ix_content_versions_poi_id ON content_versions (poi_id);


CREATE TABLE jobs (
	id VARCHAR(36) NOT NULL, 
	poi_id VARCHAR(36) NOT NULL, 
	source_url TEXT NOT NULL, 
	key VARCHAR(200) NOT NULL, 
	state VARCHAR(24) NOT NULL, 
	attempts INTEGER NOT NULL, 
	error TEXT NOT NULL, 
	content_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(poi_id) REFERENCES pois (id), 
	UNIQUE (key)
)

;

CREATE INDEX ix_jobs_poi_id ON jobs (poi_id);

CREATE INDEX ix_jobs_state ON jobs (state);

ALTER TABLE pois ADD CONSTRAINT fk_poi_published_version FOREIGN KEY(published_version) REFERENCES content_versions (id);
-- Accounts extension. Existing installations use npm.cmd run db:accounts instead.
CREATE TABLE users (
 id VARCHAR(36) PRIMARY KEY,
 email VARCHAR(254) NOT NULL UNIQUE,
 name VARCHAR(100) NOT NULL,
 password_hash TEXT NOT NULL,
 created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TABLE auth_sessions (
 id VARCHAR(64) PRIMARY KEY,
 role VARCHAR(10) NOT NULL,
 user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
 admin_id VARCHAR(36) REFERENCES admins(id) ON DELETE CASCADE,
 expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
 CHECK ((role='user' AND user_id IS NOT NULL AND admin_id IS NULL) OR
        (role='admin' AND admin_id IS NOT NULL AND user_id IS NULL))
);
CREATE INDEX ix_auth_sessions_expires_at ON auth_sessions(expires_at);
CREATE TABLE favorites (
 user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 poi_id VARCHAR(36) NOT NULL REFERENCES pois(id) ON DELETE CASCADE,
 created_at TIMESTAMP WITH TIME ZONE NOT NULL,
 PRIMARY KEY(user_id,poi_id)
);
