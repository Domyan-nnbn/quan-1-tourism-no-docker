import hashlib
import json
import secrets
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from time import monotonic
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, text, delete
from sqlalchemy.exc import IntegrityError
from .config import settings
from .db import get_db, engine
from .models import Admin, POI, Content, Job, Consent, Event, Audit, User, Favorite, now
from .schemas import Login, POIInput, DraftInput, ConsentInput, EventInput, Register
from .security import require_admin, require_user, passwords, verify_password, create_session, current_session, account_info

app = FastAPI(title='QUAN 1 TOURISM API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(','), allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Authorization','Content-Type','Idempotency-Key','X-Consent-Token'])

@app.middleware('http')
async def request_id(request: Request, call_next):
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers['X-Request-ID'] = request.state.request_id
    return response

@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(status_code=exc.status_code, content={'error':{'code':f'HTTP_{exc.status_code}', 'message':str(exc.detail), 'request_id':getattr(request.state,'request_id','')}})

@app.get('/health')
def health(): return {'status':'ok'}

@app.get('/health/ready')
def ready(db=Depends(get_db)):
    db.execute(text('SELECT 1'))
    return {'status':'ready','database':'postgresql'}

attempts = defaultdict(deque)
def throttle(request, kind):
    key = (kind, request.client.host if request.client else 'local')
    now_m = monotonic()
    # Bound idle IP entries in this single-process pilot.
    for old_key in list(attempts):
        if not attempts[old_key] or attempts[old_key][-1] < now_m-60: del attempts[old_key]
    times = attempts[key]
    while times and times[0] < now_m-60: times.popleft()
    if len(times)>=10: raise HTTPException(429,'Too many attempts; wait one minute / Thử lại sau một phút')
    times.append(now_m)

@app.post('/api/v1/auth/login')
def login(body: Login, request: Request, db=Depends(get_db)):
    throttle(request, 'admin')
    admin = db.scalar(select(Admin).where(Admin.email==body.email.lower().strip()))
    if not verify_password(body.password, admin.password_hash if admin else None):
        raise HTTPException(401,'Email or password is incorrect / Email hoặc mật khẩu không đúng')
    result=create_session(db,admin,'admin');db.commit();return result

@app.post('/api/v1/user-auth/register',status_code=201)
def register(body: Register, request: Request, db=Depends(get_db)):
    throttle(request, 'register')
    from sqlalchemy.dialects.postgresql import insert
    user_id=db.scalar(insert(User).values(email=body.email,name=body.name,
        password_hash=passwords.hash(body.password)).on_conflict_do_nothing(index_elements=['email']).returning(User.id))
    if not user_id: raise HTTPException(409,'Email already registered / Email đã được đăng ký')
    user=db.get(User,user_id)
    result=create_session(db,user,'user');db.commit();return result

@app.post('/api/v1/user-auth/login')
def user_login(body: Login, request: Request, db=Depends(get_db)):
    throttle(request, 'user')
    user=db.scalar(select(User).where(User.email==body.email.lower().strip()))
    if not verify_password(body.password,user.password_hash if user else None):
        raise HTTPException(401,'Email or password is incorrect / Email hoặc mật khẩu không đúng')
    result=create_session(db,user,'user');db.commit();return result

@app.get('/api/v1/session/me')
def me(session=Depends(current_session),db=Depends(get_db)):
    account=db.get(User,session.user_id) if session.role=='user' else db.get(Admin,session.admin_id)
    if not account: raise HTTPException(401,'Account not found')
    return account_info(account,session.role)

@app.post('/api/v1/session/logout',status_code=204)
def logout(session=Depends(current_session),db=Depends(get_db)):
    db.delete(session);db.commit()

@app.get('/api/v1/users/me/favorites')
def favorites(user=Depends(require_user),db=Depends(get_db)):
    return list(db.scalars(select(Favorite.poi_id).join(POI,POI.id==Favorite.poi_id).where(
        Favorite.user_id==user.id,POI.archived==False,POI.published_version!=None).order_by(Favorite.created_at)))

@app.put('/api/v1/users/me/favorites/{poi_id}',status_code=204)
def add_favorite(poi_id:str,user=Depends(require_user),db=Depends(get_db)):
    from sqlalchemy.dialects.postgresql import insert
    p=poi_or_404(db,poi_id)
    if not p.published_version: raise HTTPException(404,'POI not published')
    db.execute(insert(Favorite).values(user_id=user.id,poi_id=poi_id).on_conflict_do_nothing())
    db.commit()

@app.delete('/api/v1/users/me/favorites/{poi_id}',status_code=204)
def remove_favorite(poi_id:str,user=Depends(require_user),db=Depends(get_db)):
    db.execute(delete(Favorite).where(Favorite.user_id==user.id,Favorite.poi_id==poi_id));db.commit()

def poi_or_404(db, id):
    poi=db.get(POI,id)
    if not poi or poi.archived: raise HTTPException(404,'POI not found')
    return poi

def content_or_404(db,id):
    c=db.get(Content,id)
    if not c: raise HTTPException(404,'Content not found')
    return c

def audit(db,admin,action,target): db.add(Audit(admin_id=admin.id,action=action,target=target))

def serialize(db,p,admin=False):
    result={k:getattr(p,k) for k in ['id','name','name_en','category','address','latitude','longitude','radius','source_url','published_version']}
    c=db.get(Content,p.published_version) if p.published_version else None
    result['content']={'vi':c.vi,'en':c.en,'zh':c.zh,'fr':c.fr,'ja':c.ja,'source':c.source,'version':c.id} if c else None
    if admin:
        result['drafts']=[{'id':v.id,'vi':v.vi,'en':v.en,'zh':v.zh,'fr':v.fr,'ja':v.ja,'state':v.state,'source':v.source,'created_at':v.created_at.isoformat()} for v in db.scalars(select(Content).where(Content.poi_id==p.id).order_by(Content.created_at.desc()))]
    return result

@app.get('/api/v1/pois')
def list_pois(db=Depends(get_db)):
    return [serialize(db,p) for p in db.scalars(select(POI).where(POI.archived==False,POI.published_version!=None).order_by(POI.name))]

@app.get('/api/v1/offline/manifest')
def manifest(db=Depends(get_db)):
    pois=list_pois(db)
    checksum=hashlib.sha256(json.dumps(pois,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    return {'schema':1,'version':checksum,'generated_at':now().isoformat(),'pois':pois,'audio_mode':'device_tts','map_offline':False}

@app.get('/api/v1/pois/{id}')
def detail(id:str,db=Depends(get_db)):
    p=poi_or_404(db,id)
    if not p.published_version: raise HTTPException(404,'POI not published')
    return serialize(db,p)

@app.get('/api/v1/admin/pois', dependencies=[Depends(require_admin)])
def admin_pois(db=Depends(get_db)):
    return [serialize(db,p,True) for p in db.scalars(select(POI).where(POI.archived==False).order_by(POI.updated_at.desc()))]

@app.post('/api/v1/admin/pois',status_code=201)
def create_poi(body:POIInput,admin=Depends(require_admin),db=Depends(get_db)):
    p=POI(**body.model_dump()); db.add(p);db.flush();audit(db,admin,'create_poi',p.id);db.commit()
    return serialize(db,p,True)

@app.put('/api/v1/admin/pois/{id}')
def update_poi(id:str,body:POIInput,admin=Depends(require_admin),db=Depends(get_db)):
    p=poi_or_404(db,id)
    for k,v in body.model_dump().items(): setattr(p,k,v)
    audit(db,admin,'update_poi',id);db.commit()
    return serialize(db,p,True)

@app.delete('/api/v1/admin/pois/{id}',status_code=204)
def archive_poi(id:str,admin=Depends(require_admin),db=Depends(get_db)):
    p=poi_or_404(db,id);p.archived=True;p.published_version=None;audit(db,admin,'archive_poi',id);db.commit()

@app.post('/api/v1/admin/pois/{id}/drafts',status_code=201)
def draft(id:str,body:DraftInput,admin=Depends(require_admin),db=Depends(get_db)):
    p=poi_or_404(db,id)
    # Every edit creates a version; published content is never overwritten.
    previous=db.scalar(select(Content).where(Content.poi_id==id).order_by(Content.created_at.desc()))
    source=dict(previous.source) if previous and previous.source else {'url':p.source_url,'type':'manual','license':'editor-provided'}
    source['is_modified']=True
    c=Content(poi_id=id,vi=body.vi.strip(),en=body.en.strip(),zh=body.zh.strip(),fr=body.fr.strip(),ja=body.ja.strip(),source=source)
    db.add(c);db.flush();audit(db,admin,'create_draft',c.id);db.commit()
    return {'id':c.id}

@app.post('/api/v1/admin/content/{id}/approve')
def approve(id:str,admin=Depends(require_admin),db=Depends(get_db)):
    c=content_or_404(db,id);poi_or_404(db,c.poi_id)
    if c.state!='DRAFT': raise HTTPException(409,'Only draft content can be approved')
    missing=[lang for lang in ('vi','en','zh','fr','ja') if len(getattr(c,lang).strip())<20]
    if missing: raise HTTPException(409,'Review requires all five scripts (min 20 characters). Missing: '+', '.join(missing))
    c.state='APPROVED';c.reviewed_by=admin.id;audit(db,admin,'approve',id);db.commit()
    return {'state':c.state}

@app.post('/api/v1/admin/content/{id}/publish')
def publish(id:str,admin=Depends(require_admin),db=Depends(get_db)):
    c=content_or_404(db,id);p=poi_or_404(db,c.poi_id)
    if c.state not in ['APPROVED','PUBLISHED'] or not c.reviewed_by: raise HTTPException(409,'Human review required before publishing')
    # Expo pilot uses device speech; production audio-ready gate is explicitly deferred.
    if p.published_version and p.published_version!=id:
        db.get(Content,p.published_version).state='APPROVED'
    p.published_version=id;c.state='PUBLISHED';audit(db,admin,'publish',id);db.commit()
    return {'state':c.state}

@app.post('/api/v1/admin/pois/{id}/unpublish')
def unpublish(id:str,admin=Depends(require_admin),db=Depends(get_db)):
    p=poi_or_404(db,id)
    if p.published_version: db.get(Content,p.published_version).state='APPROVED'
    p.published_version=None;audit(db,admin,'unpublish',id);db.commit();return {'ok':True}

@app.post('/api/v1/admin/pois/{id}/import-wikipedia',status_code=202)
def import_wiki(id:str,idempotency_key:str=Header(min_length=8,max_length=100),admin=Depends(require_admin),db=Depends(get_db)):
    p=poi_or_404(db,id)
    if not p.source_url: raise HTTPException(409,'Configure Wikipedia source first')
    key=id+':'+idempotency_key
    j=db.scalar(select(Job).where(Job.key==key))
    if not j:
        j=Job(poi_id=id,source_url=p.source_url,key=key);db.add(j)
        try: db.flush();audit(db,admin,'import_wikipedia',j.id);db.commit()
        except IntegrityError:
            db.rollback();j=db.scalar(select(Job).where(Job.key==key))
    return {'id':j.id,'state':j.state}

@app.get('/api/v1/admin/jobs',dependencies=[Depends(require_admin)])
def jobs(db=Depends(get_db)):
    return [{'id':j.id,'poi_id':j.poi_id,'state':j.state,'attempts':j.attempts,'error':j.error,'content_id':j.content_id} for j in db.scalars(select(Job).order_by(Job.created_at.desc()).limit(100))]

@app.post('/api/v1/admin/jobs/{id}/retry')
def retry(id:str,admin=Depends(require_admin),db=Depends(get_db)):
    j=db.get(Job,id)
    if not j: raise HTTPException(404,'Job not found')
    if j.state!='FAILED': raise HTTPException(409,'Only failed jobs may be retried')
    j.state='PENDING';j.attempts=0;j.error='';j.updated_at=now();audit(db,admin,'retry',id);db.commit();return {'ok':True}

def consent_from_token(db,token):
    return db.scalar(select(Consent).where(Consent.token_hash==hashlib.sha256(token.encode()).hexdigest()).with_for_update()) if token else None

@app.post('/api/v1/consent')
def set_consent(body:ConsentInput,x_consent_token:str|None=Header(default=None),db=Depends(get_db)):
    c=consent_from_token(db,x_consent_token)
    token=x_consent_token
    if not c:
        token=secrets.token_urlsafe(32);c=Consent(token_hash=hashlib.sha256(token.encode()).hexdigest());db.add(c);db.flush()
    c.granted=body.granted;c.policy=body.policy;c.updated_at=now()
    if not body.granted: db.execute(delete(Event).where(Event.consent_id==c.id))
    db.commit();return {'token':token,'granted':c.granted}

@app.post('/api/v1/events',status_code=202)
def event(body:EventInput,x_consent_token:str|None=Header(default=None),db=Depends(get_db)):
    c=consent_from_token(db,x_consent_token)
    if not c or not c.granted: raise HTTPException(403,'Analytics consent required')
    p=poi_or_404(db,str(body.poi_id))
    if not p.published_version: raise HTTPException(404,'POI not published')
    if not db.get(Event,str(body.id)):
        db.add(Event(id=str(body.id),consent_id=c.id,poi_id=str(body.poi_id),kind=body.kind,locale=body.locale))
        try: db.commit()
        except IntegrityError: db.rollback()
    return {'ok':True}

@app.get('/api/v1/admin/analytics',dependencies=[Depends(require_admin)])
def analytics(db=Depends(get_db)):
    return {'events':[{'kind':k,'count':n} for k,n in db.execute(select(Event.kind,func.count()).group_by(Event.kind))], 'published_pois':db.scalar(select(func.count()).select_from(POI).where(POI.archived==False,POI.published_version!=None))}
