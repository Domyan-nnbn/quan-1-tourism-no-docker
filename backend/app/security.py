from datetime import timedelta
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from .config import settings
from .db import get_db
from .models import Admin, now

passwords = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def token_for(admin):
    return jwt.encode({'sub': admin.id, 'role':'admin', 'exp': now()+timedelta(hours=8), 'iat':now()}, settings.jwt_secret, algorithm='HS256')

def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_db)):
    try:
        if credentials is None: raise ValueError()
        data = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=['HS256'])
        admin = db.get(Admin, data['sub'])
        if data.get('role') != 'admin' or not admin: raise ValueError()
        return admin
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(401, 'Please sign in as administrator')
