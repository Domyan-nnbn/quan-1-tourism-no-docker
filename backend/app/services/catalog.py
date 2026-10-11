from ..repositories import common as persistence
from fastapi import HTTPException
from ..models import POI, now

from ..repositories import catalog as repo

from .common import poi_or_404, audit, serialize

def list_pois(db):
    return [serialize(db, p) for p in repo.published_pois(db)]

def detail(id, db):
    p = poi_or_404(db, id)
    if not p.published_version:
        raise HTTPException(404, 'POI not published')
    return serialize(db, p)

def admin_pois(db):
    return [serialize(db, p, True) for p in repo.active_pois(db)]

def create_poi(body, admin, db):
    p = POI(**body.model_dump())
    persistence.add(db, p)
    db.flush()
    audit(db, admin, 'create_poi', p.id)
    db.commit()
    return serialize(db, p, True)

def update_poi(id, body, admin, db):
    p = poi_or_404(db, id, lock=True)
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    audit(db, admin, 'update_poi', id)
    db.commit()
    return serialize(db, p, True)

def archive_poi(id, admin, db):
    p = poi_or_404(db, id, lock=True)
    p.archived = True
    p.published_version = None
    audit(db, admin, 'archive_poi', id)
    db.commit()
