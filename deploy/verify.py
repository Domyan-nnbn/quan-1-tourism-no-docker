"""Read-only deployment verification. Requires a running API and worker."""
import argparse
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from release import smoke

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',required=True)
    parser.add_argument('--report',type=Path,default=Path('verification.json'))
    args=parser.parse_args()
    url=urlsplit(args.url)
    if url.username or url.password or url.query or url.fragment or url.path not in ('','/'):
        parser.error('Use an API origin without credentials, path or query')
    if url.scheme!='https' and not (url.scheme=='http' and url.hostname in ('localhost','127.0.0.1')):
        parser.error('Use HTTPS, or localhost HTTP for local checks')
    result={'checked_at':time.time(),'origin':args.url,'passed':False}
    try:
        smoke(args.url)
        result['passed']=True
    except Exception as exc:
        # Do not include responses or credentials in saved evidence.
        result['error_type']=type(exc).__name__
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Verification passed' if result['passed'] else 'Verification failed: '+result['error_type'])
    raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__':main()
