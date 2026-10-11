from sqlalchemy import select, func, delete
import hashlib
from ..models import POI, Consent, Event

def lock_consent(db, token):
    return db.scalar(select(Consent).where(Consent.token_hash == hashlib.sha256(token.encode()).hexdigest()).with_for_update())

def delete_consent_events(db, c):
    return db.execute(delete(Event).where(Event.consent_id == c.id))

def count_events(db):
    return db.execute(select(Event.kind, func.count()).group_by(Event.kind))

def count_published_pois(db):
    return db.scalar(select(func.count()).select_from(POI).where(POI.archived == False, POI.published_version != None))
