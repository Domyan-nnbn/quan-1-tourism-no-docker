from sqlalchemy import select
from ..models import Content, Job

def latest_content(db, id):
    return db.scalar(select(Content).where(Content.poi_id == id).order_by(Content.created_at.desc()))

def find_job_by_key(db, key):
    return db.scalar(select(Job).where(Job.key == key))

def recent_jobs(db):
    return db.scalars(select(Job).order_by(Job.created_at.desc()).limit(100))

def insert_job(db, poi_id, source_url, key):
    from sqlalchemy.dialects.postgresql import insert
    return db.scalar(insert(Job).values(poi_id=poi_id,source_url=source_url,key=key)
        .on_conflict_do_nothing(index_elements=['key']).returning(Job.id))
