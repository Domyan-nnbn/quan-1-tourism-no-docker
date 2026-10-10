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
    with Session.begin() as db:
        # Recover jobs after a killed worker. Network timeout bounds processing to <2min.
        db.execute(update(Job).where(Job.state=='PROCESSING',Job.updated_at<now()-timedelta(minutes=5)).values(state='RETRY_PENDING',updated_at=now()))
        candidates=select(Job).where(Job.state.in_(['PENDING','RETRY_PENDING']),Job.updated_at<=now()).order_by(Job.created_at).with_for_update(skip_locked=True).limit(1)
        j=db.scalar(candidates)
        if not j:return False
        j.state='PROCESSING';j.attempts+=1;j.updated_at=now();jid=j.id;url=j.source_url;attempt=j.attempts
    try:
        plain,source=fetch_wikipedia(url)
        with Session.begin() as db:
            j=db.get(Job,jid)
            p=db.get(POI,j.poi_id)
            if not p or p.archived: raise ValueError('POI archived')
            c=Content(poi_id=j.poi_id,vi=plain if source['source_language']=='vi' else '',en=plain if source['source_language']=='en' else '',source=source)
            db.add(c);db.flush();j.content_id=c.id;j.state='COMPLETED';j.error='';j.updated_at=now()
    except Exception as exc:
        with Session.begin() as db:
            j=db.get(Job,jid);j.state='FAILED' if attempt>=3 else 'RETRY_PENDING';j.error=f'{type(exc).__name__}: Wikipedia import failed; verify source and network';j.updated_at=now()+timedelta(seconds=2**attempt*5)
    return True

if __name__=='__main__':
    print('Wikipedia worker started',flush=True)
    while True:
        if not run_once(): time.sleep(2)
