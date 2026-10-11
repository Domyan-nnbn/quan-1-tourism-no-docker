"""Failure recovery contracts. Concurrency tests require native PostgreSQL."""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4
import pytest
from sqlalchemy import text, select, func
from test_api import client, auth, make_poi
from app.db import engine, Session
from app.models import Job, Content, WorkerHeartbeat, now
from app.config import settings
from app.migrate import migrate, revisions
from app.repositories import queue


def new_job(client, auth, key=None):
    pid=make_poi(client,auth)
    result=client.post(f'/api/v1/admin/pois/{pid}/import-wikipedia',headers={**auth,'Idempotency-Key':key or str(uuid4())})
    assert result.status_code==202
    return result.json()['id']


def test_migration_repeatable_and_checksum_guard(client):
    migrate();migrate()
    with engine.begin() as db:
        assert db.scalar(text('SELECT count(*) FROM schema_migrations'))==len(revisions())
        db.execute(text("UPDATE schema_migrations SET checksum='modified' WHERE version='0001_baseline'"))
    try:
        assert client.get('/health/ready').status_code==503
        with pytest.raises(RuntimeError,match='modified migration'):migrate()
    finally:
        with engine.begin() as db:
            db.execute(text("UPDATE schema_migrations SET checksum=:c WHERE version='0001_baseline'"),{'c':revisions()[0][1]})


def test_readiness_detects_schema_drift_and_stale_worker(client,monkeypatch):
    monkeypatch.setattr(settings,'worker_required',True)
    assert client.get('/health/live').status_code==200
    assert client.get('/health/ready').status_code==503
    wid=str(uuid4());queue.heartbeat(wid)
    assert client.get('/health/ready').status_code==200
    with Session.begin() as db:db.get(WorkerHeartbeat,wid).seen_at=now()-timedelta(minutes=5)
    assert client.get('/health/ready').status_code==503
    monkeypatch.setattr(settings,'worker_required',False)
    with engine.begin() as db:db.execute(text('ALTER TABLE jobs RENAME COLUMN lease_owner TO missing_lease_owner'))
    try:assert client.get('/health/ready').status_code==503
    finally:
        with engine.begin() as db:db.execute(text('ALTER TABLE jobs RENAME COLUMN missing_lease_owner TO lease_owner'))
    assert client.get('/health/ready').status_code==200


def test_dead_worker_recovery_fences_late_result(client,auth):
    jid=new_job(client,auth)
    old=queue.claim();assert old['id']==jid
    # Equivalent persistent state after SIGKILL: PROCESSING row remains until lease expiry.
    with Session.begin() as db:db.get(Job,jid).lease_until=now()-timedelta(seconds=1)
    replacement=queue.claim();assert replacement['id']==jid and replacement['owner']!=old['owner']
    source={'source_language':'vi','type':'test'}
    assert queue.complete(old,'stale result',source) is False
    assert queue.fail(old,'Timeout') is False
    assert queue.complete(replacement,'valid recovered result',source) is True
    assert queue.complete(replacement,'duplicate result',source) is False
    with Session() as db:
        j=db.get(Job,jid)
        assert j.attempts==2 and j.state=='COMPLETED'
        assert db.scalar(select(func.count()).select_from(Content).where(Content.poi_id==j.poi_id))==1


def test_network_failure_retries_then_stops(client,auth,monkeypatch):
    from app import worker
    jid=new_job(client,auth)
    def offline(_):raise TimeoutError('secret-url-and-token-must-not-be-recorded')
    monkeypatch.setattr(worker,'fetch_wikipedia',offline)
    for attempt in range(1,4):
        assert worker.run_once()
        with Session.begin() as db:
            j=db.get(Job,jid);assert j.attempts==attempt
            assert j.state==('FAILED' if attempt==3 else 'RETRY_PENDING')
            assert 'secret-url' not in j.error
            j.updated_at=now()-timedelta(seconds=1)
    assert queue.claim() is None


def test_request_ids_metrics_and_log_redaction(client,auth,capsys):
    from app import observability
    from unittest.mock import patch
    with patch.object(observability.logger,'info') as log:
        response=client.get('/api/v1/pois?secret=do-not-log',headers={'X-Request-ID':'trace_123','Authorization':'Bearer token-do-not-log'})
        assert response.headers['X-Request-ID']=='trace_123'
        records=' '.join(str(c) for c in log.call_args_list)
        assert 'trace_123' in records and 'duration_ms' in records
        assert 'do-not-log' not in records
    assert client.get('/api/v1/admin/operations').status_code==401
    data=client.get('/api/v1/admin/operations',headers=auth).json()
    assert data['http']['requests']>0 and 'error_rate_5xx' in data['http']
    assert 'jobs' in data


native=pytest.mark.skipif(os.getenv('NATIVE_POSTGRES')!='1',reason='requires native PostgreSQL with concurrent connections (CI enables this)')

@native
def test_parallel_workers_claim_distinct_jobs(client,auth):
    ids={new_job(client,auth) for _ in range(4)}
    barrier=Barrier(4)
    def claim():barrier.wait();return queue.claim()
    with ThreadPoolExecutor(max_workers=4) as pool:claims=list(pool.map(lambda _:claim(),range(4)))
    assert {c['id'] for c in claims}==ids
    for c in claims:assert queue.complete(c,'parallel result',{'source_language':'vi'})

@native
def test_concurrent_idempotent_import_returns_one_job(client,auth):
    pid=make_poi(client,auth);key=str(uuid4());barrier=Barrier(4)
    def submit(_):
        barrier.wait()
        return client.post(f'/api/v1/admin/pois/{pid}/import-wikipedia',headers={**auth,'Idempotency-Key':key})
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(submit,range(4)))
    assert all(r.status_code==202 for r in results)
    assert len({r.json()['id'] for r in results})==1
    with Session() as db:assert db.scalar(select(func.count()).select_from(Job).where(Job.poi_id==pid))==1

@native
def test_killed_worker_process_is_recovered(client,auth,tmp_path,monkeypatch):
    import subprocess,sys,time
    from app import worker
    # Consume the previous idempotency test's pending job, then kill a real child process.
    monkeypatch.setattr(worker,'fetch_wikipedia',lambda _:('test',{'source_language':'vi'}))
    while worker.run_once():pass
    jid=new_job(client,auth);marker=tmp_path/'fetch-started'
    code="from app import worker; from pathlib import Path; import time; "
    code+=f"worker.fetch_wikipedia=lambda url:(Path({str(marker)!r}).write_text('claimed'),time.sleep(300)); worker.run_once()"
    process=subprocess.Popen([sys.executable,'-c',code])
    try:
        deadline=time.monotonic()+15
        while not marker.exists() and time.monotonic()<deadline:
            if process.poll() is not None:pytest.fail('Worker exited before claiming')
            time.sleep(.05)
        assert marker.exists()
        process.kill();process.wait(timeout=5)
        with Session.begin() as db:
            job=db.get(Job,jid);assert job.state=='PROCESSING'
            job.lease_until=now()-timedelta(seconds=1)
        assert worker.run_once()
        with Session() as db:assert db.get(Job,jid).state=='COMPLETED'
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=5)

def test_adopt_legacy_database_without_reseeding(client):
    # Simulate an installation before the version ledger and worker lease extension.
    with engine.begin() as db:
        before=db.execute(text('SELECT id,vi,en FROM content_versions ORDER BY id')).all()
        db.execute(text('DROP TABLE schema_migrations'))
        db.execute(text('DROP TABLE worker_heartbeats'))
        db.execute(text('ALTER TABLE jobs DROP COLUMN lease_owner, DROP COLUMN lease_until'))
    migrate();migrate()
    with engine.begin() as db:
        assert db.execute(text('SELECT id,vi,en FROM content_versions ORDER BY id')).all()==before
    assert client.get('/health/ready').status_code==200

@native
def test_parallel_favorite_updates_keep_one_user_scoped_row(client,auth):
    from test_accounts import register,published
    from app.models import Favorite
    user,headers=register(client,'parallel-favorite@example.test');pid=published(client,auth)
    barrier=Barrier(4)
    def add(_):
        barrier.wait()
        return client.put('/api/v1/users/me/favorites/'+pid,headers=headers)
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(add,range(4)))
    assert all(r.status_code==204 for r in results)
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(Favorite).where(Favorite.user_id==user['account']['id'],Favorite.poi_id==pid))==1

@native
def test_concurrent_publish_has_exactly_one_current_published_version(client,auth):
    from test_api import TRANSLATIONS
    pid=make_poi(client,auth);versions=[]
    for _ in range(2):
        cid=client.post(f'/api/v1/admin/pois/{pid}/drafts',headers=auth,json={'vi':'Nội dung đủ dài đã duyệt tiếng Việt.','en':'Reviewed English narration content.',**TRANSLATIONS}).json()['id']
        assert client.post(f'/api/v1/admin/content/{cid}/approve',headers=auth).status_code==200
        versions.append(cid)
    barrier=Barrier(2)
    def publish(cid):
        barrier.wait()
        return client.post(f'/api/v1/admin/content/{cid}/publish',headers=auth)
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(publish,versions))
    assert all(r.status_code==200 for r in results)
    from app.models import POI
    with Session() as db:
        current=db.get(POI,pid).published_version
        published=list(db.scalars(select(Content.id).where(Content.poi_id==pid,Content.state=='PUBLISHED')))
        assert published==[current]
