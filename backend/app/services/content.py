from ..repositories import common as persistence
from fastapi import HTTPException
from ..models import Content, Job, now

from ..repositories import content as repo

from .common import poi_or_404, content_or_404, audit

def draft(id, body, admin, db):
    p = poi_or_404(db, id, lock=True)
    previous = repo.latest_content(db, id)
    source = dict(previous.source) if previous and previous.source else {'url': p.source_url, 'type': 'manual', 'license': 'editor-provided'}
    source['is_modified'] = True
    c = Content(poi_id=id, vi=body.vi.strip(), en=body.en.strip(), zh=body.zh.strip(), fr=body.fr.strip(), ja=body.ja.strip(), source=source)
    persistence.add(db, c)
    db.flush()
    audit(db, admin, 'create_draft', c.id)
    db.commit()
    return {'id': c.id}

def approve(id, admin, db):
    c = content_or_404(db, id)
    poi_or_404(db, c.poi_id, lock=True)
    db.refresh(c)
    if c.state != 'DRAFT':
        raise HTTPException(409, 'Only draft content can be approved')
    missing = [lang for lang in ('vi', 'en', 'zh', 'fr', 'ja') if len(getattr(c, lang).strip()) < 20]
    if missing:
        raise HTTPException(409, 'Review requires all five scripts (min 20 characters). Missing: ' + ', '.join(missing))
    c.state = 'APPROVED'
    c.reviewed_by = admin.id
    audit(db, admin, 'approve', id)
    db.commit()
    return {'state': c.state}

def publish(id, admin, db):
    c = content_or_404(db, id)
    p = poi_or_404(db, c.poi_id, lock=True)
    db.refresh(c)
    if c.state not in ['APPROVED', 'PUBLISHED'] or not c.reviewed_by:
        raise HTTPException(409, 'Human review required before publishing')
    if p.published_version and p.published_version != id:
        persistence.get(db, Content, p.published_version).state = 'APPROVED'
    p.published_version = id
    c.state = 'PUBLISHED'
    audit(db, admin, 'publish', id)
    db.commit()
    return {'state': c.state}

def unpublish(id, admin, db):
    p = poi_or_404(db, id, lock=True)
    if p.published_version:
        persistence.get(db, Content, p.published_version).state = 'APPROVED'
    p.published_version = None
    audit(db, admin, 'unpublish', id)
    db.commit()
    return {'ok': True}

def import_wiki(id, idempotency_key, admin, db):
    p = poi_or_404(db, id, lock=True)
    if not p.source_url:
        raise HTTPException(409, 'Configure Wikipedia source first')
    key = id + ':' + idempotency_key
    job_id = repo.insert_job(db, id, p.source_url, key)
    if job_id:
        audit(db, admin, 'import_wikipedia', job_id)
    j = repo.find_job_by_key(db, key)
    db.commit()
    return {'id': j.id, 'state': j.state}

def jobs(db):
    return [{'id': j.id, 'poi_id': j.poi_id, 'state': j.state, 'attempts': j.attempts, 'error': j.error, 'content_id': j.content_id} for j in repo.recent_jobs(db)]

def retry(id, admin, db):
    j = persistence.get(db, Job, id)
    if not j:
        raise HTTPException(404, 'Job not found')
    if j.state != 'FAILED':
        raise HTTPException(409, 'Only failed jobs may be retried')
    j.state = 'PENDING'
    j.attempts = 0
    j.error = ''
    j.updated_at = now()
    audit(db, admin, 'retry', id)
    db.commit()
    return {'ok': True}
