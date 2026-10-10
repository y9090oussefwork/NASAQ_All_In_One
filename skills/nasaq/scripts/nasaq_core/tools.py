"""Small reviewed CLI/library runner. No shell and no arbitrary command strings.

Project code is still executable code. This gate is authorization/provenance,
not an OS sandbox; the host must review project/source changes before running.
"""
import hashlib
import os
from pathlib import Path
import re
import subprocess

from nasaq_core.state import fingerprint, now, read, write
from nasaq_core.execution import apply as execution_action, path_in

VERSIONS = {'django': '5.2.18', 'playwright': '1.63.0', 'bandit': '1.9.4',
            'pip-audit': '2.10.1', 'schemathesis': '4.30.0'}


def command(toolchain, source, action, arguments, project):
    python = Path(toolchain['python']).resolve()
    if not python.is_file() or hashlib.sha256(python.read_bytes()).hexdigest() != toolchain.get('python_sha256'):
        raise ValueError('toolchain_interpreter_changed')
    if source not in VERSIONS or toolchain.get('versions', {}).get(source) != VERSIONS[source]:
        raise ValueError('unsupported_or_unconfigured_tool_version')
    if not isinstance(arguments, dict):
        raise ValueError('invalid_tool_arguments')
    base = [str(python), '-B']
    if source == 'django':
        if action == 'startproject' and set(arguments) == {'name'}:
            name = arguments['name']
            if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}', name) or name in {'django', 'test'}:
                raise ValueError('invalid_django_project_name')
            if (project / 'manage.py').exists() or (project / name).exists():
                raise ValueError('existing_project_bootstrap_forbidden')
            return base + ['-m', 'django', 'startproject', name, '.']
        if action not in {'check', 'test', 'migrate', 'makemigrations', 'startapp'}:
            raise ValueError('unsupported_django_action')
        if not (project / 'manage.py').is_file() or path_in(project, 'manage.py').resolve() != project / 'manage.py':
            raise ValueError('django_manage_missing')
        if action in {'check', 'test', 'migrate'} and arguments:
            raise ValueError('unsupported_tool_arguments')
        if action in {'makemigrations', 'startapp'}:
            if set(arguments) != {'app'} or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}', arguments['app']):
                raise ValueError('invalid_django_app_name')
            return base + ['manage.py', action, arguments['app']]
        return base + ['manage.py', action] + (['--noinput'] if action in {'migrate', 'test'} else [])
    if source == 'bandit' and action == 'scan' and set(arguments) == {'target'}:
        target = path_in(project, arguments['target'])
        return base + ['-m', 'bandit', '-r', str(target), '-f', 'json']
    raise ValueError('source_action_not_implemented')


def run(project, runtime, event):
    data = event['data']
    execution = runtime.get('execution')
    if not execution or not execution.get('approval') or execution.get('approval', {}).get('digest') != execution.get('digest'):
        raise ValueError('execution_not_approved')
    if execution.get('paused'):
        raise ValueError('paused')
    if data.get('phase') not in execution['phases']:
        raise ValueError('execution_phase_missing')
    if execution['phases'][data['phase']]['status'] != 'running':
        raise ValueError('execution_phase_not_open')
    contract = next(p for p in execution['plan']['phases'] if p['id'] == data['phase'])
    if not contract or contract['id'] != data['phase'] or data['source'] != contract['source']:
        raise ValueError('source_outside_phase_contract')
    if 'local_process' not in contract['permissions']:
        raise ValueError('local_process_not_approved')
    config = Path(data['toolchain']).resolve()
    if hashlib.sha256(config.read_bytes()).hexdigest() != data.get('toolchain_sha256'):
        raise ValueError('toolchain_review_changed')
    toolchain = read(config)
    if toolchain.get('schema_version') != 1 or not toolchain.get('reviewed'):
        raise ValueError('toolchain_not_reviewed')
    lock = Path(toolchain['requirements_lock']).resolve()
    if hashlib.sha256(lock.read_bytes()).hexdigest() != toolchain['requirements_lock_sha256']:
        raise ValueError('toolchain_dependency_lock_changed')
    argv = command(toolchain, data['source'], data['action'], data.get('arguments', {}), project)
    receipt = project / '.nasaq/evidence' / (event['id'] + '-source-run.json')
    path_in(project, receipt.relative_to(project).as_posix())
    if receipt.exists():
        raise ValueError('source_run_receipt_exists')
    started = now()
    # Persist intention before the subprocess; a crash never becomes a receipt
    # claiming completion. The outer request journal requires explicit recovery.
    write(receipt, {'status': 'running', 'started': started, 'source': data['source'],
                    'argv': argv, 'phase': contract['id'], 'plan_digest': execution['digest']})
    environment = os.environ.copy()
    temp = project / '.nasaq/tmp'
    temp.mkdir(exist_ok=True)
    environment.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', TEMP=str(temp), TMP=str(temp),
                       PIP_CACHE_DIR=str(temp / 'pip-cache'), PLAYWRIGHT_BROWSERS_PATH=toolchain.get('browsers', str(temp / 'browsers')))
    # Versions are checked by the configured interpreter, not the caller's env.
    version = subprocess.run([argv[0], '-B', '-c',
                              'import importlib.metadata,sys;print(importlib.metadata.version(sys.argv[1]))', data['source']],
                             env=environment, cwd=temp, capture_output=True, text=True, timeout=20)
    if version.returncode or version.stdout.strip() != VERSIONS[data['source']]:
        raise ValueError('installed_source_version_changed')
    result = subprocess.run(argv, cwd=project, env=environment, capture_output=True,
                            encoding='utf-8', errors='replace', timeout=120, shell=False)
    record = {'schema_version': 1, 'status': 'passed' if result.returncode == 0 else 'failed',
              'started': started, 'finished': now(), 'source': data['source'], 'version': VERSIONS[data['source']],
              'phase': contract['id'], 'integration_mode': 'reviewed-cli/library',
              'plan_digest': execution['digest'], 'toolchain_sha256': data['toolchain_sha256'],
              'requirements_lock_sha256': toolchain['requirements_lock_sha256'], 'argv': argv,
              'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
              'evidence_kind': 'actual-process-on-test-fixture' if runtime['test_mode'] else 'actual-process'}
    write(receipt, record)
    return {'ok': result.returncode == 0, 'receipt': receipt.relative_to(project).as_posix(),
            'receipt_sha256': hashlib.sha256(receipt.read_bytes()).hexdigest(), 'result': record}
