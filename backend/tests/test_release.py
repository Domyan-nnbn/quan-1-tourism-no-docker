"""Check rollback control flow without contacting a server or stopping real services."""
import importlib.util
from pathlib import Path
from unittest.mock import Mock
import pytest

spec=importlib.util.spec_from_file_location('release',Path(__file__).resolve().parents[2]/'deploy/release.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)

def test_failed_smoke_restores_previous_compatible_release(tmp_path,monkeypatch):
    old=tmp_path/'releases/old';new=tmp_path/'releases/new';old.mkdir(parents=True);new.mkdir()
    (tmp_path/'current').symlink_to(old)
    monkeypatch.setattr(release,'restart',Mock())
    checks=Mock(side_effect=[RuntimeError('bad new API'),None]);monkeypatch.setattr(release,'wait_ready',checks)
    monkeypatch.setattr(release,'check_schema',lambda _:True)
    with pytest.raises(RuntimeError,match='previous release restored'):
        release.activate(tmp_path,new,'staging','https://api.example')
    assert (tmp_path/'current').resolve()==old
    assert release.restart.call_count==2 and checks.call_count==2

def test_incompatible_schema_blocks_automatic_rollback(tmp_path,monkeypatch):
    old=tmp_path/'old';new=tmp_path/'new';old.mkdir();new.mkdir();(tmp_path/'current').symlink_to(old)
    monkeypatch.setattr(release,'restart',Mock())
    monkeypatch.setattr(release,'wait_ready',Mock(side_effect=RuntimeError('bad API')))
    monkeypatch.setattr(release,'check_schema',lambda _:False)
    with pytest.raises(RuntimeError,match='schema-compatible'):
        release.activate(tmp_path,new,'production','https://api.example')
    assert (tmp_path/'current').resolve()==new
    assert release.restart.call_count==1


def test_smoke_checks_catalog_and_rejects_missing_worker(monkeypatch):
    import io
    import json
    from contextlib import contextmanager
    ready = {'status': 'ready', 'worker_required': True,
             'checks': {'database': True, 'schema': True, 'worker': True}}
    calls = []
    @contextmanager
    def response(url, timeout):
        calls.append(url)
        yield io.BytesIO(json.dumps(ready if url.endswith('/health/ready') else []).encode())
    monkeypatch.setattr(release.urllib.request, 'urlopen', response)
    release.smoke('https://api.example')
    assert calls == ['https://api.example/health/ready', 'https://api.example/api/v1/pois']
    ready['checks']['worker'] = False
    with pytest.raises(RuntimeError, match='fresh worker'):
        release.smoke('https://api.example')


def test_smoke_rejects_invalid_catalog(monkeypatch):
    import io
    import json
    from contextlib import contextmanager
    @contextmanager
    def response(url, timeout):
        data = {'status': 'ready', 'worker_required': True,
                'checks': {'database': True, 'schema': True, 'worker': True}} if url.endswith('/health/ready') else {'error': 'bad catalog'}
        yield io.BytesIO(json.dumps(data).encode())
    monkeypatch.setattr(release.urllib.request, 'urlopen', response)
    with pytest.raises(RuntimeError, match='Catalog'):
        release.smoke('https://api.example')


def test_successful_activation_records_release(tmp_path, monkeypatch):
    import json
    old = tmp_path/'old'; new = tmp_path/'new'
    old.mkdir(); new.mkdir(); (tmp_path/'current').symlink_to(old)
    monkeypatch.setattr(release, 'restart', Mock())
    monkeypatch.setattr(release, 'wait_ready', Mock())
    release.activate(tmp_path, new, 'staging', 'https://api.example')
    assert (tmp_path/'current').resolve() == new
    assert (tmp_path/'previous').resolve() == old
    assert json.loads((tmp_path/'last-success.json').read_text())['release'] == 'new'


def test_unpack_rejects_path_traversal_and_symlinks(tmp_path):
    import io
    import tarfile
    for index, name in enumerate(['../escape', '/absolute', 'link']):
        bundle = tmp_path/f'{index}.tar.gz'
        with tarfile.open(bundle, 'w:gz') as archive:
            member = tarfile.TarInfo(name)
            if name == 'link':
                member.type = tarfile.SYMTYPE; member.linkname = '../outside'
                archive.addfile(member)
            else:
                member.size = 1; archive.addfile(member, io.BytesIO(b'x'))
        with pytest.raises(RuntimeError, match='Unsafe'):
            release.unpack(bundle, tmp_path/f'extract-{index}')


@pytest.mark.parametrize('compatible,expected_restarts', [(True, 1), (False, 0)])
def test_failed_post_migration_validation_only_restarts_compatible_old_code(tmp_path, monkeypatch, compatible, expected_restarts):
    old=tmp_path/'old';new=tmp_path/'new';old.mkdir();new.mkdir();(tmp_path/'current').symlink_to(old)
    monkeypatch.setattr(release, 'check_schema', lambda target: target==old and compatible)
    monkeypatch.setattr(release, 'restart', Mock())
    with pytest.raises(RuntimeError, match='activation blocked'):
        release.validate_target(tmp_path, new, 'staging', recover_stopped=True)
    assert release.restart.call_count==expected_restarts
    assert (tmp_path/'current').resolve()==old
