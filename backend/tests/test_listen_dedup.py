"""Listen replay protection, data validation and multi-process persistence."""
from uuid import uuid4
from sqlalchemy import select, func
from test_api import client, auth, make_poi, TRANSLATIONS
from app.db import Session
from app.models import POI, ListenSession

def _publish(client, auth):
    poi=make_poi(client, auth)
    draft=client.post(f'/api/v1/admin/pois/{poi}/drafts',headers=auth,json={
        'vi':'Bài thuyết minh mẫu để kiểm tra hệ thống.',
        'en':'This is a validated test narration script.', **TRANSLATIONS}).json()['id']
    assert client.post(f'/api/v1/admin/content/{draft}/approve',headers=auth).status_code==200
    assert client.post(f'/api/v1/admin/content/{draft}/publish',headers=auth).status_code==200
    return poi

def test_listen_replay_uuid_is_deduplicated(client,auth):
    poi=_publish(client,auth)
    identifier=str(uuid4())
    endpoint=f'/api/v1/pois/{poi}/listen'
    r=client.post(endpoint,headers={'X-Listen-ID':identifier})
    assert r.status_code==202 and r.json()=={'ok':True,'counted':True}
    assert client.post(endpoint,headers={'X-Listen-ID':identifier}).json()['counted'] is False
    assert client.post(endpoint,headers={'X-Listen-ID':str(uuid4())}).json()['counted'] is True
    assert client.post(endpoint,headers={'X-Listen-ID':'invalid-uuid'}).status_code==422
    with Session() as db:
        assert db.get(POI,poi).listen_count==2
        assert db.scalar(select(func.count()).select_from(ListenSession).where(ListenSession.poi_id==poi))==2

def test_unpublished_poi_does_not_create_session(client,auth):
    poi=make_poi(client,auth)
    r=client.post(f'/api/v1/pois/{poi}/listen',headers={'X-Listen-ID':str(uuid4())})
    assert r.status_code==404
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(ListenSession).where(ListenSession.poi_id==poi))==0
