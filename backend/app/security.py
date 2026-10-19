import hashlib
import secrets
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from .db import get_db
from .models import Admin, User, AuthSession, now

passwords = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
# Equal-cost password verification even for unknown accounts.
dummy_hash = passwords.hash(secrets.token_urlsafe(32))

def verify_password(password, stored_hash):
    valid = passwords.verify(password, stored_hash or dummy_hash)
    return bool(stored_hash) and valid

def create_session(db, account, role):
    token = secrets.token_urlsafe(48)
    session = AuthSession(id=hashlib.sha256(token.encode()).hexdigest(), role=role,
        user_id=account.id if role == 'user' else None,
        admin_id=account.id if role == 'admin' else None,
        expires_at=now()+timedelta(hours=8 if role == 'admin' else 24*30))
    db.add(session)
    return {'access_token':token, 'token_type':'bearer', 'expires_at':session.expires_at.isoformat(),
            'account':account_info(account,role)}

def account_info(account, role):
    return {'id':account.id, 'email':account.email, 'name':account.name if role=='user' else 'Admin', 'role':role}

def current_session(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_db)):
    if credentials is None: raise HTTPException(401,'Please sign in / Vui lòng đăng nhập')
    session = db.get(AuthSession, hashlib.sha256(credentials.credentials.encode()).hexdigest())
    if not session or session.expires_at <= now():
        raise HTTPException(401,'Session expired; please sign in / Phiên hết hạn, hãy đăng nhập lại')
    if session.role == 'user':
        user = db.get(User, session.user_id)
        if not user or user.locked:
            raise HTTPException(403, 'Account is locked / Tài khoản đã bị khóa')
    return session

def require_admin(session=Depends(current_session), db=Depends(get_db)):
    if session.role != 'admin': raise HTTPException(403,'Administrator access required')
    account = db.get(Admin,session.admin_id)
    if not account: raise HTTPException(401,'Account not found')
    return account

def require_user(session=Depends(current_session), db=Depends(get_db)):
    if session.role != 'user': raise HTTPException(403,'User account required')
    account = db.get(User,session.user_id)
    if not account: raise HTTPException(401,'Account not found')
    return account
