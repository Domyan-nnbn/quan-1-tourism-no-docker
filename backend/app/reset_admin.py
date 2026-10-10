"""Explicitly reset the configured admin's password from environment."""
from sqlalchemy import select, delete
from .config import settings
from .db import Session
from .models import Admin, AuthSession
from .security import passwords
if __name__ == '__main__':
    with Session.begin() as db:
        admin=db.scalar(select(Admin).where(Admin.email==settings.admin_email.lower()))
        if not admin: raise SystemExit('Admin not found. Initialize database first.')
        admin.password_hash=passwords.hash(settings.admin_password)
        db.execute(delete(AuthSession).where(AuthSession.admin_id==admin.id))
    print('Admin password updated from configured environment. Existing sessions have been revoked.')
