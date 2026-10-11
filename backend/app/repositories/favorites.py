from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from ..models import POI, Favorite

def published_favorites(db, user):
    return db.scalars(select(Favorite.poi_id).join(POI, POI.id == Favorite.poi_id).where(Favorite.user_id == user.id, POI.archived == False, POI.published_version != None).order_by(Favorite.created_at))

def insert_favorite(db, poi_id, user):
    return db.execute(insert(Favorite).values(user_id=user.id, poi_id=poi_id).on_conflict_do_nothing())

def delete_favorite(db, poi_id, user):
    return db.execute(delete(Favorite).where(Favorite.user_id == user.id, Favorite.poi_id == poi_id))
