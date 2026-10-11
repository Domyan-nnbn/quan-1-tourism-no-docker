from datetime import timedelta
from sqlalchemy import select, func, text
from ..models import Job, WorkerHeartbeat, now
from ..config import settings
from ..migrate import schema_matches, version_matches

def checks(db):
    db.execute(text('SELECT 1'))
    schema=version_matches(db.connection()) and schema_matches(db.connection())
    worker=False
    if schema:
        worker=bool(db.scalar(select(func.count()).select_from(WorkerHeartbeat).where(
            WorkerHeartbeat.seen_at>now()-timedelta(seconds=settings.worker_stale_seconds))))
    return {'database':True,'schema':schema,'worker':worker}

def job_counts(db):
    return dict(db.execute(select(Job.state,func.count()).group_by(Job.state)).all())
