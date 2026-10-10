import os
os.environ.setdefault('JWT_SECRET','test-secret-only-012345678901234567890123456789')
os.environ.setdefault('ADMIN_PASSWORD','integration-test-only-password')
os.environ.setdefault('SEED_DEMO','false')
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.db import Base, engine, Session
from app.models import Admin, Content, Job, POI
from app.security import passwords
from app.main import app
from app.config import settings
from app import worker
TRANSLATIONS={'zh':'这是经过审核的中文示例解说内容，适合测试语言支持。','fr':'Texte de narration française relu pour ce test.','ja':'これは言語対応を確認するための日本語の解説文です。'}

@pytest.fixture(scope='module')
def client():
    # Destructive operations are restricted to a dedicated database name.
    assert engine.url.database.endswith('_test'), 'Use a DATABASE_URL ending in _test'
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine)
    with Session.begin() as db:db.add(Admin(email=settings.admin_email,password_hash=passwords.hash(settings.admin_password)))
    with TestClient(app) as c:yield c
    Base.metadata.drop_all(engine)

@pytest.fixture
def auth(client):
    r=client.post('/api/v1/auth/login',json={'email':settings.admin_email,'password':settings.admin_password})
    assert r.status_code==200
    return {'Authorization':'Bearer '+r.json()['access_token']}

def make_poi(client,auth):
    r=client.post('/api/v1/admin/pois',headers=auth,json={'name':'Test POI','name_en':'Test place','category':'heritage','address':'District 1','latitude':10.77,'longitude':106.7,'radius':30,'source_url':'https://vi.wikipedia.org/wiki/Test'})
    assert r.status_code==201,r.text
    return r.json()['id']

def test_publication_is_reviewed_and_versioned(client,auth):
    assert client.get('/api/v1/admin/pois').status_code==401
    pid=make_poi(client,auth)
    assert client.get('/api/v1/pois/'+pid).status_code==404
    cid=client.post(f'/api/v1/admin/pois/{pid}/drafts',headers=auth,json={'vi':'Nội dung tiếng Việt đã kiểm tra.','en':'Reviewed English narration text.',**TRANSLATIONS}).json()['id']
    assert client.post(f'/api/v1/admin/content/{cid}/publish',headers=auth).status_code==409
    assert client.post(f'/api/v1/admin/content/{cid}/approve',headers=auth).status_code==200
    assert client.post(f'/api/v1/admin/content/{cid}/publish',headers=auth).status_code==200
    assert client.get('/api/v1/pois/'+pid).json()['content']['ja']==TRANSLATIONS['ja']
    old=client.get('/api/v1/pois/'+pid).json()['content']
    client.post(f'/api/v1/admin/pois/{pid}/drafts',headers=auth,json={'vi':'Bản mới chưa được duyệt để phát hành.','en':'New unapproved content version.',**TRANSLATIONS})
    assert client.get('/api/v1/pois/'+pid).json()['content']==old
    assert client.post(f'/api/v1/admin/pois/{pid}/unpublish',headers=auth).status_code==200
    assert client.get('/api/v1/pois/'+pid).status_code==404

def test_bilingual_gate_and_source_validation(client,auth):
    pid=make_poi(client,auth)
    cid=client.post(f'/api/v1/admin/pois/{pid}/drafts',headers=auth,json={'vi':'Nội dung tiếng Việt để kiểm tra.'}).json()['id']
    assert client.post(f'/api/v1/admin/content/{cid}/approve',headers=auth).status_code==409
    for url in ['http://127.0.0.1/test','https://vi.wikipedia.org.evil.test/wiki/Test','https://user@vi.wikipedia.org/wiki/Test']:
        r=client.post('/api/v1/admin/pois',headers=auth,json={'name':'Test','name_en':'Test','category':'heritage','address':'test','latitude':10,'longitude':106,'source_url':url})
        assert r.status_code==422

def test_durable_job_idempotency_and_review(client,auth,monkeypatch):
    pid=make_poi(client,auth)
    h={**auth,'Idempotency-Key':'test-import-1234'}
    first=client.post(f'/api/v1/admin/pois/{pid}/import-wikipedia',headers=h)
    assert first.status_code==202
    assert client.post(f'/api/v1/admin/pois/{pid}/import-wikipedia',headers=h).json()['id']==first.json()['id']
    monkeypatch.setattr(worker,'fetch_wikipedia',lambda url:('Văn bản nguồn Wikipedia chưa được biên tập.',{'source_language':'vi','revision_id':123,'type':'wikipedia_excerpt'}))
    assert worker.run_once()
    with Session() as db:
        j=db.get(Job,first.json()['id']);assert j.state=='COMPLETED'
        assert db.get(Content,j.content_id).state=='DRAFT'
        assert db.get(POI,pid).published_version is None

def test_consent_enforced_and_revocation_deletes_events(client,auth):
    from uuid import uuid4
    pid=make_poi(client,auth)
    cid=client.post(f'/api/v1/admin/pois/{pid}/drafts',headers=auth,json={'vi':'Kịch bản mẫu đã duyệt tiếng Việt.','en':'English script reviewed for this test.',**TRANSLATIONS}).json()['id']
    client.post(f'/api/v1/admin/content/{cid}/approve',headers=auth);client.post(f'/api/v1/admin/content/{cid}/publish',headers=auth)
    event={'id':str(uuid4()),'poi_id':pid,'kind':'narration_started','locale':'zh'}
    assert client.post('/api/v1/events',json=event).status_code==403
    token=client.post('/api/v1/consent',json={'granted':True}).json()['token'];h={'X-Consent-Token':token}
    assert client.post('/api/v1/events',json=event,headers=h).status_code==202
    assert client.post('/api/v1/events',json=event,headers=h).status_code==202
    assert client.get('/api/v1/admin/analytics',headers=auth).json()['events'][0]['count']==1
    client.post('/api/v1/consent',headers=h,json={'granted':False})
    assert client.post('/api/v1/events',headers=h,json=event).status_code==403
    assert client.get('/api/v1/admin/analytics',headers=auth).json()['events']==[]

def test_manifest_only_published(client):
    data=client.get('/api/v1/offline/manifest').json()
    assert data['schema']==1 and len(data['version'])==64
    assert all(p['published_version'] and p['content'] for p in data['pois'])
    assert data['map_offline'] is False


def test_language_migration_is_repeatable_and_preserves_content(client):
    from app.migrate_languages import migrate
    from sqlalchemy import text
    with engine.begin() as db:
        before=db.execute(text('SELECT id, vi, en FROM content_versions ORDER BY id')).all()
        for lang in ('zh','fr','ja'): db.execute(text(f'ALTER TABLE content_versions DROP COLUMN {lang}'))
    migrate();migrate()
    with engine.begin() as db:
        after=db.execute(text('SELECT id, vi, en FROM content_versions ORDER BY id')).all()
        assert before==after
        assert all(row==('', '', '') for row in db.execute(text('SELECT zh,fr,ja FROM content_versions')))


def test_demo_import_only_fills_missing_unedited_scripts(client):
    from app.seed import PLACES
    from app.import_demo_translations import run
    row=PLACES[0]
    with Session.begin() as db:
        p=POI(name=row[0],name_en=row[1],category=row[2],address=row[3],latitude=row[4],longitude=row[5],radius=30)
        db.add(p);db.flush()
        original=Content(poi_id=p.id,vi=row[-2],en=row[-1],zh='',fr='',ja='既存の日本語原稿は変更されません。',source={'type':'demo_original'})
        edited=Content(poi_id=p.id,vi=row[-2]+' Đã sửa.',en=row[-1],zh='',fr='',ja='',source={'type':'demo_original'})
        db.add_all([original,edited]);db.flush();original_id=original.id;edited_id=edited.id
    run();run()
    with Session() as db:
        c=db.get(Content,original_id);assert c.zh and c.fr;assert c.ja=='既存の日本語原稿は変更されません。'
        c=db.get(Content,edited_id);assert (c.zh,c.fr,c.ja)==('','','')
