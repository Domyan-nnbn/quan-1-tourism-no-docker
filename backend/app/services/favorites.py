from fastapi import HTTPException

from ..repositories import favorites as repo

from .common import poi_or_404

def favorites(user, db):
    return list(repo.published_favorites(db, user))

def add_favorite(poi_id, user, db):
    p = poi_or_404(db, poi_id)
    if not p.published_version:
        raise HTTPException(404, 'POI not published')
    repo.insert_favorite(db, poi_id, user)
    db.commit()

def remove_favorite(poi_id, user, db):
    repo.delete_favorite(db, poi_id, user)
    db.commit()
