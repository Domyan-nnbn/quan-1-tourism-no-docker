from ..repositories import common as persistence
import hashlib
import secrets
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from ..models import Consent, Event, now, POI, Content
from sqlalchemy import select, func, case
from sqlalchemy.dialects.postgresql import insert
from datetime import timedelta

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
    inserted_id = db.execute(insert(Event).values(
        id=str(body.id), consent_id=c.id, poi_id=str(body.poi_id), kind=body.kind,
        locale=body.locale, created_at=now()
    ).on_conflict_do_nothing(index_elements=[Event.id]).returning(Event.id)).scalar_one_or_none()
    db.commit()
    return {'ok': True}

def analytics(db):
    events=[{'kind': k, 'count': n} for k, n in repo.count_events(db)]
    starts=sum(x['count'] for x in events if x['kind']=='narration_started')
    completed=sum(x['count'] for x in events if x['kind']=='narration_completed')
    narration_errors=sum(x['count'] for x in events if x['kind']=='narration_error')
    by_poi=db.execute(select(Event.poi_id,POI.name,
        func.sum(case((Event.kind=='narration_started',1),else_=0)),
        func.sum(case((Event.kind=='narration_completed',1),else_=0)))
        .join(POI,POI.id==Event.poi_id).group_by(Event.poi_id,POI.name)
        .order_by(func.sum(case((Event.kind=='narration_started',1),else_=0)).desc())).all()
    by_locale=db.execute(select(Event.locale,func.sum(case((Event.kind=='narration_started',1),else_=0)),
        func.sum(case((Event.kind=='narration_completed',1),else_=0))).group_by(Event.locale).order_by(Event.locale)).all()
    since=now()-timedelta(days=30)
    daily=db.execute(select(func.date(Event.created_at),Event.kind,func.count())
        .where(Event.created_at>=since).group_by(func.date(Event.created_at),Event.kind)
        .order_by(func.date(Event.created_at))).all()
    candidates=db.scalars(select(Content).join(POI,POI.id==Content.poi_id).where(POI.archived==False).order_by(Content.created_at.desc())).all()
    latest=[];seen=set()
    for content in candidates:
        if content.poi_id not in seen:
            seen.add(content.poi_id);latest.append(content)
    missing={lang:sum(1 for c in latest if len(getattr(c,lang).strip())<20) for lang in ('vi','en','zh','fr','ja')}
    aggregate_listens=db.scalar(select(func.coalesce(func.sum(POI.listen_count),0)).where(POI.archived==False)) or 0
    by_poi_listens={p.id:p.listen_count for p in db.scalars(select(POI).where(POI.archived==False))}
    return {'events':events,'published_pois':repo.count_published_pois(db),'total_listens':int(aggregate_listens),'narration_errors':narration_errors,
        'completion_rate':round(completed/starts,4) if starts else 0,
        'missing_translations':missing,
        'by_poi':[{'poi_id':pid,'name':name,'listens':int(by_poi_listens.get(pid,0)),'completed':int(done or 0)} for pid,name,started,done in by_poi],
        'by_locale':[{'locale':locale,'listens':int(started or 0),'completed':int(done or 0)} for locale,started,done in by_locale],
        'daily':[{'date':str(day),'kind':kind,'count':count} for day,kind,count in daily]}
