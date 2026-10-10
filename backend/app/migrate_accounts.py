"""Add accounts/sessions/favorites without changing existing content or seeding."""
from sqlalchemy import text, inspect
from .db import engine
from .models import User, AuthSession, Favorite

def migrate():
    with engine.begin() as db:
        db.execute(text('SELECT pg_advisory_xact_lock(7712028)'))
        names=set(inspect(db).get_table_names())
        if not {'pois','admins'}.issubset(names):
            raise RuntimeError('Database chua khoi tao. Kiem tra DATABASE_URL, sau do chay npm.cmd run db:init.')
        for table in (User.__table__,AuthSession.__table__,Favorite.__table__):
            table.create(db,checkfirst=True)
    print('Accounts migration complete. Existing POIs and narration preserved.')

if __name__=='__main__': migrate()
