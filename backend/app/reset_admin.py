"""Explicitly reset the configured admin's password from environment."""
from sqlalchemy import select
from .config import settings
from .db import Session
from .models import Admin
from .security import passwords
if __name__ == '__main__':
    with Session.begin() as db:
        admin=db.scalar(select(Admin).where(Admin.email==settings.admin_email.lower()))
        if not admin: raise SystemExit('Admin not found. Initialize database first.')
        admin.password_hash=passwords.hash(settings.admin_password)
    print('Admin password updated from configured environment. Existing tokens expire within 8 hours.')
