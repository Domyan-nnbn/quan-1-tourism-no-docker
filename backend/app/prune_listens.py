"""Remove stale anonymous replay-idempotency UUIDs, keep POI counters intact.

Recommended via Windows Task Scheduler / cron once a day. Does not read .env values.
"""
from datetime import timedelta
from sqlalchemy import delete
from .db import Session
from .models import ListenSession, now

RETENTION_DAYS = 45

def prune():
    with Session.begin() as db:
        result = db.execute(delete(ListenSession).where(
            ListenSession.created_at < now() - timedelta(days=RETENTION_DAYS)))
        print(f'Expired listen UUIDs removed: {result.rowcount} (older than {RETENTION_DAYS} days)')

if __name__ == '__main__':
    prune()
