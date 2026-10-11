from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from ..models import Admin, User, AuthSession

def find_admin(db, body):
    return db.scalar(select(Admin).where(Admin.email == body.email.lower().strip()))

def insert_user(db, body, password_hash):
    return db.scalar(insert(User).values(email=body.email, name=body.name, password_hash=password_hash).on_conflict_do_nothing(index_elements=['email']).returning(User.id))

def find_user(db, body):
    return db.scalar(select(User).where(User.email == body.email.lower().strip()))

def find_session(db, token_hash):
    return db.scalar(select(AuthSession).where(AuthSession.id == token_hash))

def revoke_other_sessions(db, role, identity, keep_id):
    owner = AuthSession.user_id == identity if role == 'user' else AuthSession.admin_id == identity
    return db.execute(delete(AuthSession).where(owner, AuthSession.id != keep_id))
