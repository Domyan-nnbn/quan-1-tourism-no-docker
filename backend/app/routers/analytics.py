from fastapi import Depends, Header, APIRouter
from ..db import get_db
from ..schemas import ConsentInput, EventInput
from ..security import require_admin

from ..services import analytics as service
router = APIRouter()

@router.post('/api/v1/consent')
def set_consent(body: ConsentInput, x_consent_token: str | None=Header(default=None), db=Depends(get_db)):
    return service.set_consent(body=body, x_consent_token=x_consent_token, db=db)

@router.post('/api/v1/events', status_code=202)
def event(body: EventInput, x_consent_token: str | None=Header(default=None), db=Depends(get_db)):
    return service.event(body=body, x_consent_token=x_consent_token, db=db)

@router.get('/api/v1/admin/analytics', dependencies=[Depends(require_admin)])
def analytics(db=Depends(get_db)):
    return service.analytics(db=db)
