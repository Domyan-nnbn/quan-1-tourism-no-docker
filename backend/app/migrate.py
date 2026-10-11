"""Transactional, checksum-verified migrations. Run explicitly before deployment."""
import hashlib
from pathlib import Path
from sqlalchemy import inspect, text
from .db import engine, Base
from . import models  # register expected schema

DIRECTORY = Path(__file__).with_name('migrations')

def revisions():
    return [(p.stem, hashlib.sha256(p.read_text().encode()).hexdigest(), p.read_text())
            for p in sorted(DIRECTORY.glob('*.sql'))]

def schema_matches(connection):
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    for table in Base.metadata.sorted_tables:
        if table.name not in tables:
            return False
        columns = {c['name']: c for c in inspector.get_columns(table.name)}
        for column in table.columns:
            actual = columns.get(column.name)
            if actual is None or actual['nullable'] != column.nullable:
                return False
            if actual['type']._type_affinity is not column.type._type_affinity:
                return False
    return True

def version_matches(connection):
    if not inspect(connection).has_table('schema_migrations'):
        return False
    actual = dict(connection.execute(text('SELECT version, checksum FROM schema_migrations')).all())
    return actual == {v: checksum for v, checksum, sql in revisions()}

def migrate():
    with engine.begin() as connection:
        connection.execute(text('SELECT pg_advisory_xact_lock(71012026)'))
        connection.execute(text('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, checksum VARCHAR(64) NOT NULL, applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)'))
        applied = dict(connection.execute(text('SELECT version, checksum FROM schema_migrations')).all())
        expected = {v: checksum for v, checksum, sql in revisions()}
        if any(v not in expected or expected[v] != c for v, c in applied.items()):
            raise RuntimeError('Unknown or modified migration; restore original release before upgrading')
        pending_seen = False
        for version, checksum, sql in revisions():
            if version in applied:
                if pending_seen:
                    raise RuntimeError('Migration history is not a contiguous prefix')
                continue
            pending_seen = True
            # psycopg executes the frozen SQL without parameter interpolation.
            connection.exec_driver_sql(sql)
            connection.execute(text('INSERT INTO schema_migrations(version, checksum) VALUES (:v,:c)'), {'v':version,'c':checksum})
        if not schema_matches(connection):
            raise RuntimeError('Schema drift detected; migration rolled back. Review missing/changed columns.')
    print('Schema current: ' + revisions()[-1][0])

if __name__ == '__main__':
    migrate()
