from sqlalchemy import select
from ..models import Content

def content_versions(db, p):
    return db.scalars(select(Content).where(Content.poi_id == p.id).order_by(Content.created_at.desc()))

def get(db, model, identity):
    return db.get(model, identity)

def add(db, entity):
    db.add(entity)

def remove(db, entity):
    db.delete(entity)

def locked(db, model, identity):
    return db.scalar(select(model).where(model.id == identity).with_for_update())
