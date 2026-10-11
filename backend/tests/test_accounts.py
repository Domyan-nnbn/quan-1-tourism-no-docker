from datetime import timedelta
import hashlib
from sqlalchemy import select, func
from test_api import client, auth, make_poi, TRANSLATIONS
from app.db import Session
from app.models import User, Favorite, AuthSession, now
from app.main import attempts

def register(client,email='first@example.test',password='password123'):
    r=client.post('/api/v1/user-auth/register',json={'email':email,'password':password,'name':'Nguyên','role':'admin'})
    assert r.status_code==201,r.text
    return r.json(),{'Authorization':'Bearer '+r.json()['access_token']}

def published(client,auth):
    pid=make_poi(client,auth)
    cid=client.post(f'/api/v1/admin/pois/{pid}/drafts',headers=auth,json={'vi':'Nội dung tiếng Việt đủ dài để kiểm thử.','en':'English narration content used for this integration test.',**TRANSLATIONS}).json()['id']
    assert client.post(f'/api/v1/admin/content/{cid}/approve',headers=auth).status_code==200
    assert client.post(f'/api/v1/admin/content/{cid}/publish',headers=auth).status_code==200
    return pid

def test_registration_roles_and_duplicate_email(client):
    attempts.clear()
    result,h=register(client)
    assert result['account']['role']=='user'
    assert 'password' not in str(result['account'])
    assert client.get('/api/v1/session/me',headers=h).json()['name']=='Nguyên'
    assert client.get('/api/v1/admin/pois',headers=h).status_code==403
    assert client.post('/api/v1/auth/login',json={'email':'first@example.test','password':'password123'}).status_code==401
    r=client.post('/api/v1/user-auth/register',json={'email':' FIRST@example.test ','password':'password123','name':'Test'})
    assert r.status_code==409
    for email,password in [('bad','password123'),('ok@example.test','short')]:
        assert client.post('/api/v1/user-auth/register',json={'email':email,'password':password,'name':'Test'}).status_code==422
    with Session() as db:
        user=db.scalar(select(User).where(User.email=='first@example.test'))
        assert user.password_hash!='password123' and user.password_hash.startswith('$argon2')
        assert db.get(AuthSession,result['access_token']) is None

def test_favorites_are_isolated_persistent_and_idempotent(client,auth):
    attempts.clear()
    a,ha=register(client,'a@example.test');b,hb=register(client,'b@example.test')
    pid=published(client,auth)
    path='/api/v1/users/me/favorites'
    assert client.get(path).status_code==401
    assert client.get(path,headers=auth).status_code==403
    assert client.put(path+'/'+pid,headers=ha).status_code==204
    assert client.put(path+'/'+pid,headers=ha).status_code==204
    assert client.get(path,headers=ha).json()==[pid]
    assert client.get(path,headers=hb).json()==[]
    assert client.delete(path+'/'+pid,headers=hb).status_code==204
    assert client.get(path,headers=ha).json()==[pid]
    assert client.post('/api/v1/session/logout',headers=ha).status_code==204
    assert client.get(path,headers=ha).status_code==401
    login=client.post('/api/v1/user-auth/login',json={'email':'A@example.test','password':'password123'})
    assert login.status_code==200
    fresh={'Authorization':'Bearer '+login.json()['access_token']}
    assert client.get(path,headers=fresh).json()==[pid]
    assert client.delete(path+'/'+pid,headers=fresh).status_code==204
    assert client.get(path,headers=fresh).json()==[]

def test_sessions_expire_and_admin_logout_revokes(client,auth):
    attempts.clear()
    result,h=register(client,'expired@example.test')
    with Session.begin() as db:
        session=db.get(AuthSession,hashlib.sha256(result['access_token'].encode()).hexdigest())
        session.expires_at=now()-timedelta(seconds=1)
    assert client.get('/api/v1/session/me',headers=h).status_code==401
    assert client.get('/api/v1/session/me',headers=auth).json()['role']=='admin'
    assert client.post('/api/v1/session/logout',headers=auth).status_code==204
    assert client.get('/api/v1/admin/pois',headers=auth).status_code==401

def test_accounts_migration_repeatable_and_preserves_data(client):
    from app.migrate_accounts import migrate
    with Session() as db:
        before=db.scalar(select(func.count()).select_from(User))
    migrate();migrate()
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(User))==before

def test_login_throttle(client):
    attempts.clear()
    for _ in range(10):
        assert client.post('/api/v1/user-auth/login',json={'email':'unknown@example.test','password':'bad'}).status_code==401
    assert client.post('/api/v1/user-auth/login',json={'email':'unknown@example.test','password':'bad'}).status_code==429
    attempts.clear()

def test_migration_adds_account_tables_to_legacy_database(client):
    from sqlalchemy import text, inspect
    from app.db import engine
    from app.migrate_accounts import migrate
    with engine.begin() as db:
        before=db.execute(text('SELECT id,vi,en,zh,fr,ja FROM content_versions ORDER BY id')).all()
        for table in ('favorites','auth_sessions','users'): db.execute(text(f'DROP TABLE {table}'))
    migrate()
    with engine.begin() as db:
        assert {'users','favorites','auth_sessions'}.issubset(inspect(db).get_table_names())
        assert db.execute(text('SELECT id,vi,en,zh,fr,ja FROM content_versions ORDER BY id')).all()==before

def test_password_change_revokes_other_sessions_and_preserves_current(client):
    attempts.clear()
    result,current=register(client,'change-password@example.test')
    second=client.post('/api/v1/user-auth/login',json={'email':'change-password@example.test','password':'password123'})
    assert second.status_code==200
    old={'Authorization':'Bearer '+second.json()['access_token']}
    endpoint='/api/v1/session/password'
    assert client.post(endpoint,headers=current,json={'current_password':'wrong','new_password':'new-password-123'}).status_code==401
    assert client.get('/api/v1/session/me',headers=current).status_code==200
    assert client.post(endpoint,headers=current,json={'current_password':'password123','new_password':'new-password-123'}).status_code==200
    assert client.get('/api/v1/session/me',headers=current).status_code==200
    assert client.get('/api/v1/session/me',headers=old).status_code==401
    assert client.post('/api/v1/user-auth/login',json={'email':'change-password@example.test','password':'password123'}).status_code==401
    assert client.post('/api/v1/user-auth/login',json={'email':'change-password@example.test','password':'new-password-123'}).status_code==200
