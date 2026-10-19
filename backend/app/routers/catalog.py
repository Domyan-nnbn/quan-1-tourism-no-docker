from fastapi import Depends, APIRouter, Request, Header
from uuid import UUID
from ..db import get_db
from ..schemas import POIInput
from ..security import require_admin

from ..services import catalog as service
router = APIRouter()

@router.get('/api/v1/pois')
def list_pois(db=Depends(get_db)):
    return service.list_pois(db=db)

@router.get('/api/v1/pois/{id}')
def detail(id: str, db=Depends(get_db)):
    return service.detail(id=id, db=db)

@router.post('/api/v1/pois/{id}/listen', status_code=202)
def record_listen(id: str, request: Request, x_listen_id: UUID | None=Header(default=None), db=Depends(get_db)):
    return service.record_listen(id=id, request=request, db=db, listen_id=x_listen_id)

@router.get('/api/v1/admin/pois', dependencies=[Depends(require_admin)])
def admin_pois(db=Depends(get_db)):
    return service.admin_pois(db=db)

@router.post('/api/v1/admin/pois', status_code=201)
def create_poi(body: POIInput, admin=Depends(require_admin), db=Depends(get_db)):
    return service.create_poi(body=body, admin=admin, db=db)

@router.put('/api/v1/admin/pois/{id}')
def update_poi(id: str, body: POIInput, admin=Depends(require_admin), db=Depends(get_db)):
    return service.update_poi(id=id, body=body, admin=admin, db=db)

@router.delete('/api/v1/admin/pois/{id}', status_code=204)
def archive_poi(id: str, admin=Depends(require_admin), db=Depends(get_db)):
    return service.archive_poi(id=id, admin=admin, db=db)
