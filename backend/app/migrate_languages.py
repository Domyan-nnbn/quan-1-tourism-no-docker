"""Additive migration; preserves POIs, content and published pointers."""
from sqlalchemy import text
from .db import engine

def migrate():
    with engine.begin() as db:
        db.execute(text('SELECT pg_advisory_xact_lock(7712027)'))
        for name in ('zh','fr','ja'):
            db.execute(text(f"ALTER TABLE content_versions ADD COLUMN IF NOT EXISTS {name} TEXT NOT NULL DEFAULT ''"))
    print('Migration complete: zh/fr/ja added; existing content preserved. Enter translations before publishing new versions.')

if __name__=='__main__': migrate()
