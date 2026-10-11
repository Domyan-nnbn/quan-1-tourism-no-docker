from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ..db import get_db
from ..security import require_admin
from ..services import operations
router=APIRouter()

@router.get('/health/live')
def live():
    return {'status':'alive'}

@router.get('/health/ready')
def ready(db=Depends(get_db)):
    ok,body=operations.readiness(db)
    return JSONResponse(body,status_code=200 if ok else 503)

@router.get('/api/v1/admin/operations')
def metrics(admin=Depends(require_admin),db=Depends(get_db)):
    return operations.metrics(db)

@router.get('/api/v1/system/status')
def connection(db=Depends(get_db)):
    ok, body = operations.readiness(db)
    return JSONResponse(body, status_code=200 if ok else 503)
