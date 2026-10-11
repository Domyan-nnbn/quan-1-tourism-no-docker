#!/usr/bin/env python3
"""No-Docker release manager for a pre-provisioned Linux/systemd host.
Run as the deployment user, never as root. See docs/OPERATIONS.md.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import time
import urllib.request


def run(args, **kwargs):
    subprocess.run([str(a) for a in args],check=True,**kwargs)


def python(release):
    return release/'backend/.venv/bin/python'


def check_schema(release):
    result=subprocess.run([str(python(release)),'-c',
        'from app.db import engine; from app.migrate import version_matches,schema_matches; '
        'c=engine.connect(); ok=version_matches(c) and schema_matches(c); c.close(); raise SystemExit(0 if ok else 1)'],
        cwd=release/'backend',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return result.returncode==0


def restart(environment):
    run(['sudo','-n','systemctl','restart',f'quan1-api@{environment}',f'quan1-worker@{environment}'])


def swap(link, target):
    temporary=link.with_name(link.name+'.next')
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(target,target_is_directory=True)
    temporary.replace(link)


def smoke(base):
    with urllib.request.urlopen(base.rstrip('/')+'/health/ready',timeout=5) as response:
        body=json.load(response)
    if body.get('status')!='ready' or not body.get('worker_required') or not all(body.get('checks',{}).get(k) for k in ('database','schema','worker')):
        raise RuntimeError('Readiness requires database, exact schema and a fresh worker')
    with urllib.request.urlopen(base.rstrip('/')+'/api/v1/pois',timeout=5) as response:
        if not isinstance(json.load(response),list):raise RuntimeError('Catalog smoke check failed')


def wait_ready(local_url, public_url):
    for attempt in range(20):
        try:
            smoke(local_url)
            smoke(public_url)
            return
        except Exception:
            if attempt==19:raise
            time.sleep(2)


def activate(root, target, environment, public_url):
    current=root/'current'
    previous=current.resolve() if current.is_symlink() else None
    swap(current,target)
    local_url='http://127.0.0.1:'+('8001' if environment=='staging' else '8000')
    try:
        restart(environment)
        wait_ready(local_url,public_url)
    except Exception as original:
        if previous and check_schema(previous):
            swap(current,previous)
            restart(environment)
            wait_ready(local_url,public_url)
            raise RuntimeError('New release failed smoke checks; previous release restored and checked') from original
        # Do not silently start code incompatible with an upgraded database.
        raise RuntimeError('Release unhealthy; automatic rollback unavailable because there is no schema-compatible previous release. Follow database recovery runbook.') from original
    if previous and previous!=target:
        swap(root/'previous',previous)
    (root/'last-success.json').write_text(json.dumps({'release':target.name,'previous':previous.name if previous else None,'checked_at':time.time()}))


def validate_target(root, target, environment, recover_stopped=False):
    if check_schema(target):
        return
    previous=(root/'current').resolve() if (root/'current').is_symlink() else None
    if recover_stopped and previous and check_schema(previous):
        restart(environment)
    raise RuntimeError('Target release is not compatible with the current database; activation blocked')


def unpack(bundle, target):
    with tarfile.open(bundle,'r:gz') as archive:
        for member in archive.getmembers():
            path=Path(member.name)
            if path.is_absolute() or '..' in path.parts or member.issym() or member.islnk():
                raise RuntimeError('Unsafe release archive')
        archive.extractall(target,filter='data')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['deploy','rollback'])
    parser.add_argument('--environment',choices=['staging','production'],required=True)
    parser.add_argument('--release',required=True,help='Full immutable Git commit SHA')
    parser.add_argument('--bundle',type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--public-url',required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',args.release):parser.error('Release must be a full Git SHA')
    if not args.public_url.startswith('https://'):parser.error('Public URL must use HTTPS')
    root=Path('/opt/quan1-'+args.environment)
    if not (root/'shared/backend.env').is_file():parser.error('Provision shared/backend.env first')
    import fcntl
    with (root/'deploy.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        target=root/'releases'/args.release
        if args.action=='deploy':
            if not args.bundle or not args.sha256:parser.error('Bundle and checksum are required')
            if hashlib.sha256(args.bundle.read_bytes()).hexdigest()!=args.sha256:raise RuntimeError('Artifact checksum mismatch')
            if target.exists():raise RuntimeError('Immutable release already exists; select rollback to activate an existing release')
            target.mkdir(parents=True)
            unpack(args.bundle,target)
            run([sys.executable,'-m','venv',target/'backend/.venv'])
            run([python(target),'-m','pip','install','-r',target/'backend/requirements.lock'])
            (target/'backend/.env').symlink_to(root/'shared/backend.env')
            backup=root/'backups'/f'{args.release}-{int(time.time())}.dump'
            backup.parent.mkdir(exist_ok=True)
            # Credentials passed to pg_dump via environment, never process arguments/logs.
            run([python(target),target/'deploy/backup.py',backup],cwd=target/'backend')
            # Stop old processes before changing schema; maintenance window is deliberate.
            run(['sudo','-n','systemctl','stop',f'quan1-api@{args.environment}',f'quan1-worker@{args.environment}'])
            try:
                run([python(target),'-m','app.migrate'],cwd=target/'backend')
            except Exception:
                previous=(root/'current').resolve() if (root/'current').is_symlink() else None
                if previous and check_schema(previous):restart(args.environment)
                raise
        elif not target.is_dir():
            raise RuntimeError('Target release does not exist on this host')
        validate_target(root,target,args.environment,recover_stopped=args.action=='deploy')
        activate(root,target,args.environment,args.public_url)
        print('Release active and smoke checks passed: '+args.release)

if __name__=='__main__':main()
