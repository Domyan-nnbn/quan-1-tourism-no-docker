from ..repositories import common as persistence
from collections import defaultdict, deque
from time import monotonic
from threading import Lock
from fastapi import HTTPException
from ..models import Admin, User
from ..security import passwords, verify_password, create_session, account_info

from ..repositories import accounts as repo


attempts = defaultdict(deque)
attempts_lock = Lock()

def throttle(request, kind):
    with attempts_lock:
        key = (kind, request.client.host if request.client else 'local')
        now_m = monotonic()
        for old_key in list(attempts):
            if not attempts[old_key] or attempts[old_key][-1] < now_m - 60:
                del attempts[old_key]
        times = attempts[key]
        while times and times[0] < now_m - 60:
            times.popleft()
        if len(times) >= 10:
            raise HTTPException(429, 'Too many attempts; wait one minute / Thử lại sau một phút')
        times.append(now_m)

def login(body, request, db):
    throttle(request, 'admin')
    admin = repo.find_admin(db, body)
    if not verify_password(body.password, admin.password_hash if admin else None):
        raise HTTPException(401, 'Email or password is incorrect / Email hoặc mật khẩu không đúng')
    result = create_session(db, admin, 'admin')
    db.commit()
    return result

def register(body, request, db):
    throttle(request, 'register')
    user_id = repo.insert_user(db, body, passwords.hash(body.password))
    if not user_id:
        raise HTTPException(409, 'Email already registered / Email đã được đăng ký')
    user = persistence.get(db, User, user_id)
    result = create_session(db, user, 'user')
    db.commit()
    return result

def user_login(body, request, db):
    throttle(request, 'user')
    user = repo.find_user(db, body)
    if not verify_password(body.password, user.password_hash if user else None):
        raise HTTPException(401, 'Email or password is incorrect / Email hoặc mật khẩu không đúng')
    result = create_session(db, user, 'user')
    db.commit()
    return result

def me(session, db):
    account = persistence.get(db, User, session.user_id) if session.role == 'user' else persistence.get(db, Admin, session.admin_id)
    if not account:
        raise HTTPException(401, 'Account not found')
    return account_info(account, session.role)

def logout(session, db):
    persistence.remove(db, session)
    db.commit()

def change_password(body, request, session, db):
    throttle(request, 'password')
    model = User if session.role == 'user' else Admin
    identity = session.user_id if session.role == 'user' else session.admin_id
    account = persistence.locked(db, model, identity)
    # Serialize password changes for the account and check that the calling session
    # was not revoked by another transaction while waiting for the lock.
    fresh = repo.find_session(db, session.id)
    if not fresh:
        raise HTTPException(401, 'Session revoked; please sign in again')
    if not account or not verify_password(body.current_password, account.password_hash):
        raise HTTPException(401, 'Current password is incorrect / Mật khẩu hiện tại không đúng')
    if body.current_password == body.new_password:
        raise HTTPException(422, 'Choose a different password / Hãy chọn mật khẩu khác')
    if session.role == 'admin' and len(body.new_password) < 12:
        raise HTTPException(422, 'Admin password needs at least 12 characters')
    account.password_hash = passwords.hash(body.new_password)
    repo.revoke_other_sessions(db, session.role, identity, session.id)
    db.commit()
    return {'ok': True, 'other_sessions_revoked': True}
