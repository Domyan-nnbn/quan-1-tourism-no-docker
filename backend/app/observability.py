"""JSON logs contain route templates, never tokens, query strings or request bodies."""
from datetime import datetime, timezone
import json
import logging
import re
from collections import deque
from threading import Lock
from time import monotonic
from uuid import uuid4
from fastapi.responses import JSONResponse

logger=logging.getLogger('quan1.operations')
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.propagate=False
lock=Lock()
samples=deque(maxlen=10000)

def log_event(event, **fields):
    logger.info(json.dumps({'timestamp':datetime.now(timezone.utc).isoformat(),'event':event,**fields},ensure_ascii=False))

def snapshot():
    with lock:
        recent=[s for s in samples if s[0]>=monotonic()-300]
    n=len(recent)
    return {'scope':'this API process; last 300 seconds, at most 10000 requests',
            'requests':n,'errors_5xx':sum(s[1]>=500 for s in recent),
            'error_rate_5xx':sum(s[1]>=500 for s in recent)/n if n else 0,
            'error_rate_4xx':sum(400<=s[1]<500 for s in recent)/n if n else 0,
            'mean_duration_ms':round(sum(s[2] for s in recent)/n,2) if n else 0}

def install_observability(app):
    @app.middleware('http')
    async def observe(request, call_next):
        supplied=request.headers.get('X-Request-ID','')
        request_id=supplied if re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',supplied) else uuid4().hex
        request.state.request_id=request_id
        started=monotonic()
        try:
            response=await call_next(request)
        except Exception as exc:
            log_event('request_exception',request_id=request_id,error_type=type(exc).__name__)
            response=JSONResponse({'detail':'Internal server error','request_id':request_id},status_code=500)
        duration=round((monotonic()-started)*1000,2)
        response.headers['X-Request-ID']=request_id
        route=request.scope.get('route')
        log_event('http_request',request_id=request_id,method=request.method,
                  route=getattr(route,'path','unmatched'),status=response.status_code,duration_ms=duration)
        with lock:
            samples.append((monotonic(),response.status_code,duration))
        return response
