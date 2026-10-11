from ..repositories import common as persistence
from fastapi import HTTPException
from ..models import POI, Content, Audit

from ..repositories import common as repo

def poi_or_404(db, id, lock=False):
    poi = persistence.locked(db, POI, id) if lock else persistence.get(db, POI, id)
    if not poi or poi.archived:
        raise HTTPException(404, 'POI not found')
    return poi

def content_or_404(db, id):
    c = persistence.get(db, Content, id)
    if not c:
        raise HTTPException(404, 'Content not found')
    return c

def audit(db, admin, action, target):
    persistence.add(db, Audit(admin_id=admin.id, action=action, target=target))

def serialize(db, p, admin=False):
    result = {k: getattr(p, k) for k in ['id', 'name', 'name_en', 'category', 'address', 'latitude', 'longitude', 'radius', 'source_url', 'published_version']}
    c = persistence.get(db, Content, p.published_version) if p.published_version else None
    result['content'] = {'vi': c.vi, 'en': c.en, 'zh': c.zh, 'fr': c.fr, 'ja': c.ja, 'source': c.source, 'version': c.id} if c else None
    if admin:
        result['drafts'] = [{'id': v.id, 'vi': v.vi, 'en': v.en, 'zh': v.zh, 'fr': v.fr, 'ja': v.ja, 'state': v.state, 'source': v.source, 'created_at': v.created_at.isoformat()} for v in repo.content_versions(db, p)]
    return result
