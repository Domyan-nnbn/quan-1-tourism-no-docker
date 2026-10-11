"""Durable PostgreSQL queue for Wikipedia import. No AI output is simulated."""
import hashlib
import time
from datetime import timedelta
from urllib.parse import urlsplit, unquote
import httpx
from sqlalchemy import select, update
from .db import Session
from .models import Job, Content, POI, now

def fetch_wikipedia(url):
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc not in ['vi.wikipedia.org','en.wikipedia.org'] or not u.path.startswith('/wiki/'):
        raise ValueError('Wikipedia source is not allowed')
    title=unquote(u.path[6:]).replace('_',' ')
    # Request revision first; parse that exact revision to avoid attribution races.
    with httpx.Client(timeout=25,follow_redirects=False,headers={'User-Agent':'Quan1TourismStudent/1.0 (educational prototype)'}) as client:
        base=f'https://{u.netloc}/w/api.php'
        r=client.get(base,params={'action':'query','format':'json','formatversion':2,'redirects':1,'prop':'revisions|pageprops','rvprop':'ids','titles':title})
        r.raise_for_status();page=r.json()['query']['pages'][0]
        if page.get('missing') or 'disambiguation' in page.get('pageprops',{}): raise ValueError('Missing or disambiguation article')
        revision=page['revisions'][0]['revid']
        r=client.get(base,params={'action':'parse','format':'json','oldid':revision,'prop':'text','disableeditsection':1})
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(r.json()['parse']['text']['*'],'html.parser')
        for node in soup.select('table, sup, style, script, .mw-editsection, .navbox'): node.decompose()
        plain='\n'.join(p.get_text(' ',strip=True) for p in soup.select('p') if p.get_text(strip=True))[:12000]
        if len(plain)<100: raise ValueError('Source article too short')
        return plain, {'url':url,'title':page['title'],'article_id':page['pageid'],'revision_id':revision,'revision_url':f'https://{u.netloc}/w/index.php?oldid={revision}','retrieved_at':now().isoformat(),'content_hash':hashlib.sha256(plain.encode()).hexdigest(),'source_language':u.netloc[:2],'license':'CC BY-SA 4.0','is_modified':True,'type':'wikipedia_excerpt'}

def run_once():
    from .repositories import queue
    from .observability import log_event
    claim=queue.claim()
    if not claim:
        return False
    started=time.monotonic()
    try:
        plain,source=fetch_wikipedia(claim['url'])
        accepted=queue.complete(claim,plain,source)
        log_event('job_finished',job_id=claim['id'],attempt=claim['attempt'],accepted=accepted,
                  duration_ms=round((time.monotonic()-started)*1000,2))
    except Exception as exc:
        queue.fail(claim,type(exc).__name__)
        log_event('job_failed',job_id=claim['id'],attempt=claim['attempt'],error_type=type(exc).__name__)
    return True

def main():
    import signal
    from uuid import uuid4
    from threading import Event
    from .repositories import queue
    from .observability import log_event
    from .migrate import schema_matches, version_matches
    from .db import engine
    with engine.connect() as connection:
        if not version_matches(connection) or not schema_matches(connection):
            raise RuntimeError('Run python -m app.migrate before starting worker')
    worker_id=str(uuid4());stop=Event()
    for sig in (signal.SIGTERM,signal.SIGINT):
        signal.signal(sig,lambda *_:stop.set())
    # Heartbeat represents progress through the loop. A stuck fetch becomes unhealthy.
    # No separate heartbeat thread falsely advertises a hung worker as healthy.
    log_event('worker_started',worker_id=worker_id)
    try:
        while not stop.is_set():
            queue.heartbeat(worker_id)
            try:
                worked=run_once()
            except Exception as exc:
                log_event('worker_error',error_type=type(exc).__name__)
                stop.wait(2)
                continue
            if not worked:
                stop.wait(2)
    finally:
        queue.forget_worker(worker_id)
        log_event('worker_stopped',worker_id=worker_id)

if __name__=='__main__':
    main()
