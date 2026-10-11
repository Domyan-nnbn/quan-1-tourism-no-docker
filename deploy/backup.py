"""Executed with release venv; PostgreSQL client must match server major version."""
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from sqlalchemy.engine import make_url
from app.config import settings
url=make_url(settings.database_url)
env={**os.environ,'PGHOST':url.host or 'localhost','PGPORT':str(url.port or 5432),
     'PGUSER':url.username or '', 'PGPASSWORD':url.password or '', 'PGDATABASE':url.database or ''}
for key in ('sslmode','sslrootcert','sslcert','sslkey'):
    if key in url.query:env['PG'+key.upper()]=str(url.query[key])
os.umask(0o077)
subprocess.run(['pg_dump','--format=custom','--file',sys.argv[1]],env=env,check=True)
if Path(sys.argv[1]).stat().st_size==0:raise RuntimeError('Empty database backup')
