from sqlalchemy import select
from ..models import POI

def published_pois(db):
    return db.scalars(select(POI).where(POI.archived == False, POI.published_version != None).order_by(POI.name))

def active_pois(db):
    return db.scalars(select(POI).where(POI.archived == False).order_by(POI.updated_at.desc()))
