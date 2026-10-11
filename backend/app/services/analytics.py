from ..repositories import common as persistence
import hashlib
import secrets
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from ..models import Consent, Event, now

from ..repositories import analytics as repo

from .common import poi_or_404

def consent_from_token(db, token):
    return repo.lock_consent(db, token) if token else None

def set_consent(body, x_consent_token, db):
    c = consent_from_token(db, x_consent_token)
    token = x_consent_token
    if not c:
        token = secrets.token_urlsafe(32)
        c = Consent(token_hash=hashlib.sha256(token.encode()).hexdigest())
        persistence.add(db, c)
        db.flush()
    c.granted = body.granted
    c.policy = body.policy
    c.updated_at = now()
    if not body.granted:
        repo.delete_consent_events(db, c)
    db.commit()
    return {'token': token, 'granted': c.granted}

def event(body, x_consent_token, db):
    c = consent_from_token(db, x_consent_token)
    if not c or not c.granted:
        raise HTTPException(403, 'Analytics consent required')
    p = poi_or_404(db, str(body.poi_id))
    if not p.published_version:
        raise HTTPException(404, 'POI not published')
    if not persistence.get(db, Event, str(body.id)):
        persistence.add(db, Event(id=str(body.id), consent_id=c.id, poi_id=str(body.poi_id), kind=body.kind, locale=body.locale))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    return {'ok': True}

def analytics(db):
    return {'events': [{'kind': k, 'count': n} for k, n in repo.count_events(db)], 'published_pois': repo.count_published_pois(db)}
