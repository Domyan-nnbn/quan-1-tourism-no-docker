"""Short transactions only: never hold a row lock while fetching a remote page."""
from datetime import timedelta
from uuid import uuid4
from sqlalchemy import select, update, delete, case
from sqlalchemy.dialects.postgresql import insert
from ..db import Session
from ..models import Job, Content, POI, WorkerHeartbeat, now
from ..config import settings

def heartbeat(worker_id):
    with Session.begin() as db:
        db.execute(insert(WorkerHeartbeat).values(id=worker_id, seen_at=now()).on_conflict_do_update(
            index_elements=['id'], set_={'seen_at': now()}))
        db.execute(delete(WorkerHeartbeat).where(WorkerHeartbeat.seen_at < now()-timedelta(days=1)))

def forget_worker(worker_id):
    with Session.begin() as db:
        db.execute(delete(WorkerHeartbeat).where(WorkerHeartbeat.id == worker_id))

def claim():
    with Session.begin() as db:
        timestamp = now()
        db.execute(update(Job).where(Job.state=='PROCESSING',
            (Job.lease_until < timestamp) | (Job.lease_until.is_(None))).values(
            state=case((Job.attempts>=3,'FAILED'),else_='RETRY_PENDING'),
            lease_owner=None, lease_until=None, updated_at=timestamp,
            error='Worker lease expired; interrupted attempt recovered'))
        job = db.scalar(select(Job).where(Job.state.in_(['PENDING','RETRY_PENDING']),
            Job.updated_at<=timestamp).order_by(Job.created_at).with_for_update(skip_locked=True).limit(1))
        if not job:
            return None
        job.state='PROCESSING'
        job.attempts+=1
        job.lease_owner=str(uuid4())
        job.lease_until=timestamp+timedelta(seconds=settings.job_lease_seconds)
        job.updated_at=timestamp
        return {'id':job.id,'owner':job.lease_owner,'url':job.source_url,'attempt':job.attempts}

def owned_job(db, claim):
    return db.scalar(select(Job).where(Job.id==claim['id'],Job.state=='PROCESSING',
        Job.lease_owner==claim['owner'],Job.lease_until>now()).with_for_update())

def complete(claim, plain, source):
    with Session.begin() as db:
        job=owned_job(db,claim)
        if job is None:
            return False  # a restarted worker already owns this attempt
        poi=db.get(POI,job.poi_id)
        if not poi or poi.archived:
            raise ValueError('POI archived')
        content=Content(poi_id=poi.id,vi=plain if source['source_language']=='vi' else '',
            en=plain if source['source_language']=='en' else '',source=source)
        db.add(content);db.flush()
        job.content_id=content.id;job.state='COMPLETED';job.error=''
        job.lease_owner=None;job.lease_until=None;job.updated_at=now()
        return True

def fail(claim, error_type):
    with Session.begin() as db:
        job=owned_job(db,claim)
        if job is None:
            return False
        job.state='FAILED' if job.attempts>=3 else 'RETRY_PENDING'
        job.error=error_type+': Wikipedia import failed; verify source and network'
        job.updated_at=now()+timedelta(seconds=2**job.attempts*5)
        job.lease_owner=None;job.lease_until=None
        return True
