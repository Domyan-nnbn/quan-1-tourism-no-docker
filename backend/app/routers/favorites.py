from fastapi import Depends, APIRouter
from ..db import get_db
from ..security import require_user

from ..services import favorites as service
router = APIRouter()

@router.get('/api/v1/users/me/favorites')
def favorites(user=Depends(require_user), db=Depends(get_db)):
    return service.favorites(user=user, db=db)

@router.put('/api/v1/users/me/favorites/{poi_id}', status_code=204)
def add_favorite(poi_id: str, user=Depends(require_user), db=Depends(get_db)):
    return service.add_favorite(poi_id=poi_id, user=user, db=db)

@router.delete('/api/v1/users/me/favorites/{poi_id}', status_code=204)
def remove_favorite(poi_id: str, user=Depends(require_user), db=Depends(get_db)):
    return service.remove_favorite(poi_id=poi_id, user=user, db=db)
