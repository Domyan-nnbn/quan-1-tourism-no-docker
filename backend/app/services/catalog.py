from ..repositories import common as persistence
from fastapi import HTTPException
from ..models import POI, Favorite, ListenSession
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from uuid import uuid4
from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from ..repositories import catalog as repo

from .common import poi_or_404, audit, serialize

listen_attempts=defaultdict(deque)
listen_attempts_lock=Lock()

def list_pois(db):
    return [serialize(db, p) for p in repo.published_pois(db)]

def detail(id, db):
    p = poi_or_404(db, id)
    if not p.published_version:
        raise HTTPException(404, 'POI not published')
    return serialize(db, p)

def admin_pois(db):
    pois=list(repo.active_pois(db))
    counts=dict(db.execute(select(Favorite.poi_id,func.count()).where(
        Favorite.poi_id.in_([p.id for p in pois])
    ).group_by(Favorite.poi_id)).all()) if pois else {}
    return [{**serialize(db,p,True),'favorite_count':int(counts.get(p.id,0))} for p in pois]

def record_listen(id, request, db, listen_id=None):
    client=request.client.host if request.client else 'local'
    with listen_attempts_lock:
        current=monotonic()
        for old_client in list(listen_attempts):
            while listen_attempts[old_client] and listen_attempts[old_client][0] <= current-60:
                listen_attempts[old_client].popleft()
            if not listen_attempts[old_client]:
                del listen_attempts[old_client]
        attempts=listen_attempts[client]
        if len(attempts)>=60:
            raise HTTPException(429,'Too many listen events; please wait and retry')
        attempts.append(current)
    # Keep the insert + counter increment in ONE transaction. A reused UUID can
    # never count twice, even if a mobile request is retried or API replicas race.
    # Clients that omit the header still work, but cannot deduplicate retries.
    key=str(listen_id or uuid4())
    published=db.scalar(select(POI.id).where(
        POI.id==id, POI.archived==False, POI.published_version!=None
    ))
    if not published:
        raise HTTPException(404,'POI not published')
    inserted=db.execute(insert(ListenSession).values(id=key,poi_id=id)
        .on_conflict_do_nothing(index_elements=[ListenSession.id])
        .returning(ListenSession.id)).scalar_one_or_none()
    if inserted:
        result=db.execute(update(POI).where(
            POI.id==id, POI.archived==False, POI.published_version!=None
        ).values(listen_count=POI.listen_count+1))
        if result.rowcount!=1:
            db.rollback()
            raise HTTPException(404,'POI not published')
    db.commit()
    return {'ok':True,'counted':bool(inserted)}

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
