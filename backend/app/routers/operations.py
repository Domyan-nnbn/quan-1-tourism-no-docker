from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ..db import get_db
from ..models import AppSetting, Audit, Admin
from ..schemas import AdminSettingsInput
from sqlalchemy import select
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

@router.get('/api/v1/admin/system')
def admin_system(admin=Depends(require_admin),db=Depends(get_db)):
    _,body=operations.readiness(db)
    return body

@router.get('/api/v1/admin/settings')
def admin_settings(admin=Depends(require_admin),db=Depends(get_db)):
    saved=db.get(AppSetting,'admin_config')
    return saved.value if saved else AdminSettingsInput().model_dump()

@router.put('/api/v1/admin/settings')
def update_admin_settings(body: AdminSettingsInput,admin=Depends(require_admin),db=Depends(get_db)):
    saved=db.get(AppSetting,'admin_config')
    if saved:
        saved.value=body.model_dump()
    else:
        db.add(AppSetting(key='admin_config',value=body.model_dump()))
    db.add(Audit(admin_id=admin.id,action='update_settings',target='configuration'))
    db.commit()
    return body.model_dump()

@router.get('/api/v1/app/config')
def public_app_config(db=Depends(get_db)):
    saved=db.get(AppSetting,'admin_config')
    return saved.value if saved else AdminSettingsInput().model_dump()

@router.get('/api/v1/admin/audit')
def audit_history(admin=Depends(require_admin),db=Depends(get_db)):
    rows=db.execute(select(Audit,Admin.email).join(Admin,Admin.id==Audit.admin_id)
        .order_by(Audit.created_at.desc()).limit(100)).all()
    return [{'action':a.action,'target':a.target,'admin_email':email,'created_at':a.created_at.isoformat()} for a,email in rows]

@router.get('/api/v1/system/status')
def connection(db=Depends(get_db)):
    ok, body = operations.readiness(db)
    return JSONResponse(body, status_code=200 if ok else 503)
