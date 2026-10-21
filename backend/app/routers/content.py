from fastapi import Depends, Header, APIRouter
from ..db import get_db
from ..schemas import DraftInput, WikipediaImportInput
from ..security import require_admin

from ..services import content as service
from ..services.wikipedia_import import import_from_wikipedia
router = APIRouter()

@router.post('/api/v1/admin/wikipedia/import')
def import_wikipedia_url(body: WikipediaImportInput, admin=Depends(require_admin), db=Depends(get_db)):
    return import_from_wikipedia(source_url=body.source_url, admin=admin, db=db)

@router.post('/api/v1/admin/pois/{id}/drafts', status_code=201)
def draft(id: str, body: DraftInput, admin=Depends(require_admin), db=Depends(get_db)):
    return service.draft(id=id, body=body, admin=admin, db=db)

@router.post('/api/v1/admin/content/{id}/approve')
def approve(id: str, admin=Depends(require_admin), db=Depends(get_db)):
    return service.approve(id=id, admin=admin, db=db)

@router.post('/api/v1/admin/content/{id}/publish')
def publish(id: str, admin=Depends(require_admin), db=Depends(get_db)):
    return service.publish(id=id, admin=admin, db=db)

@router.post('/api/v1/admin/pois/{id}/unpublish')
def unpublish(id: str, admin=Depends(require_admin), db=Depends(get_db)):
    return service.unpublish(id=id, admin=admin, db=db)

@router.post('/api/v1/admin/pois/{id}/import-wikipedia', status_code=202)
def import_wiki(id: str, idempotency_key: str=Header(min_length=8, max_length=100), admin=Depends(require_admin), db=Depends(get_db)):
    return service.import_wiki(id=id, idempotency_key=idempotency_key, admin=admin, db=db)

@router.get('/api/v1/admin/jobs', dependencies=[Depends(require_admin)])
def jobs(db=Depends(get_db)):
    return service.jobs(db=db)

@router.post('/api/v1/admin/jobs/{id}/retry')
def retry(id: str, admin=Depends(require_admin), db=Depends(get_db)):
    return service.retry(id=id, admin=admin, db=db)
