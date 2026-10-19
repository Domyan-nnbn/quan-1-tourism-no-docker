"""Create a clean source ZIP. Run: python scripts/package_clean.py

The original file tree stays intact; secrets, VCS, dependencies and caches are excluded.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT.parent / f'{ROOT.name}-safe-v1.3.3.zip'
BLOCKED_DIRS = {'node_modules', '.venv', '.git', '.expo', '__pycache__',
                '.pytest_cache', 'dist', 'build', 'reports', '.next', '.turbo'}
BLOCKED_NAMES = {'.env', '.env.local', '.env.production', '.env.development',
                 '.DS_Store', 'Thumbs.db', 'id_rsa', 'id_ed25519'}
BLOCKED_SUFFIXES = ('.pyc', '.pyo', '.log', '.key', '.pem', '.p12', '.sqlite', '.db', '.rar', '.zip')

def is_safe(rel):
    return (not any(p in BLOCKED_DIRS for p in rel.parts)
            and not any(p in BLOCKED_NAMES or p.startswith('.env.') and not p.endswith('.example') for p in rel.parts)
            and not rel.name.endswith(BLOCKED_SUFFIXES))

def main():
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and is_safe(p.relative_to(ROOT)))
    with ZipFile(TARGET, 'w', ZIP_DEFLATED, compresslevel=8) as zipfile:
        for file in files:
            zipfile.write(file, arcname=f'{ROOT.name}/{file.relative_to(ROOT).as_posix()}')
    print(f'Wrote {TARGET} ({len(files)} files, {TARGET.stat().st_size // 1024} KiB)')
    with ZipFile(TARGET) as archive:
        assert all(is_safe(Path(name)) for name in archive.namelist())

if __name__ == '__main__':
    main()
