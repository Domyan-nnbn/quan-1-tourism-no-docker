"""API → PostgreSQL queue → real worker → editorial review → public/user APIs.
Only the external Wikipedia network call is replaced with a deterministic source.
"""
from uuid import uuid4
from test_api import client, auth, make_poi, TRANSLATIONS
from app import worker
from app.db import Session
from app.models import Job, Content


def test_complete_editorial_and_user_journey(client, auth, monkeypatch):
    pid = make_poi(client, auth)
    headers = {**auth, 'Idempotency-Key': 'journey-' + str(uuid4())}
    path = f'/api/v1/admin/pois/{pid}/import-wikipedia'
    queued = client.post(path, headers=headers)
    assert queued.status_code == 202, queued.text
    jid = queued.json()['id']
    assert client.post(path, headers=headers).json()['id'] == jid
    assert client.get(f'/api/v1/pois/{pid}').status_code == 404
    monkeypatch.setattr(worker, 'fetch_wikipedia', lambda url: (
        'Văn bản nguồn Wikipedia cần được biên tập và duyệt trước khi xuất bản.',
        {'source_language': 'vi', 'revision_id': 12345, 'type': 'wikipedia_excerpt', 'url': url}))
    assert worker.run_once()
    with Session() as db:
        job = db.get(Job, jid)
        assert job.state == 'COMPLETED'
        imported = db.get(Content, job.content_id)
        assert imported.state == 'DRAFT'
        imported_id = imported.id
    # Import success alone must never expose unreviewed text.
    assert client.get(f'/api/v1/pois/{pid}').status_code == 404
    assert client.post(f'/api/v1/admin/content/{imported_id}/approve', headers=auth).status_code == 409
    scripts = {'vi': 'Bài thuyết minh tiếng Việt đã được biên tập và kiểm duyệt.',
               'en': 'Reviewed English narration for the published destination.', **TRANSLATIONS}
    draft = client.post(f'/api/v1/admin/pois/{pid}/drafts', headers=auth, json=scripts)
    assert draft.status_code == 201
    cid = draft.json()['id']
    assert client.post(f'/api/v1/admin/content/{cid}/publish', headers=auth).status_code == 409
    assert client.post(f'/api/v1/admin/content/{cid}/approve', headers=auth).status_code == 200
    assert client.post(f'/api/v1/admin/content/{cid}/publish', headers=auth).status_code == 200
    public = client.get(f'/api/v1/pois/{pid}').json()
    assert public['content']['version'] == cid
    assert public['content']['source']['revision_id'] == 12345
    assert all(public['content'][lang] == value for lang, value in scripts.items())
    registered = client.post('/api/v1/user-auth/register', json={
        'email': 'journey-' + uuid4().hex + '@example.test', 'password': 'journey-password', 'name': 'Journey'})
    assert registered.status_code == 201
    user = {'Authorization': 'Bearer ' + registered.json()['access_token']}
    assert client.post(f'/api/v1/admin/content/{cid}/publish', headers=user).status_code == 403
    assert client.put(f'/api/v1/users/me/favorites/{pid}', headers=user).status_code == 204
    assert pid in client.get('/api/v1/users/me/favorites', headers=user).json()
    consent = client.post('/api/v1/consent', json={'granted': True}).json()['token']
    event_headers = {'X-Consent-Token': consent}
    event = {'id': str(uuid4()), 'poi_id': pid, 'kind': 'narration_started', 'locale': 'ja'}
    assert client.post('/api/v1/events', headers=event_headers, json=event).status_code == 202
    assert client.post('/api/v1/consent', headers=event_headers, json={'granted': False}).status_code == 200
    assert client.post('/api/v1/events', headers=event_headers, json=event).status_code == 403
    assert client.post('/api/v1/session/logout', headers=user).status_code == 204
    assert client.get('/api/v1/users/me/favorites', headers=user).status_code == 401
    assert client.post(f'/api/v1/admin/pois/{pid}/unpublish', headers=auth).status_code == 200
    assert client.get(f'/api/v1/pois/{pid}').status_code == 404
