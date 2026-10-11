from fastapi import Depends, Request, APIRouter
from ..db import get_db
from ..schemas import Login, Register, ChangePassword
from ..security import current_session

from ..services import accounts as service
router = APIRouter()

@router.post('/api/v1/auth/login')
def login(body: Login, request: Request, db=Depends(get_db)):
    return service.login(body=body, request=request, db=db)

@router.post('/api/v1/user-auth/register', status_code=201)
def register(body: Register, request: Request, db=Depends(get_db)):
    return service.register(body=body, request=request, db=db)

@router.post('/api/v1/user-auth/login')
def user_login(body: Login, request: Request, db=Depends(get_db)):
    return service.user_login(body=body, request=request, db=db)

@router.get('/api/v1/session/me')
def me(session=Depends(current_session), db=Depends(get_db)):
    return service.me(session=session, db=db)

@router.post('/api/v1/session/logout', status_code=204)
def logout(session=Depends(current_session), db=Depends(get_db)):
    return service.logout(session=session, db=db)

@router.post('/api/v1/session/password')
def change_password(body: ChangePassword, request: Request, session=Depends(current_session), db=Depends(get_db)):
    return service.change_password(body=body, request=request, session=session, db=db)
