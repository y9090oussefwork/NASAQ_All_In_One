"""Nasaq unified host entry point. Trusted host events, never attached commands.

JSON approvals record user instructions; they do not authenticate a person.
The host must only attribute actual user messages as origin=user. Old direct
session scripts remain for compatibility; this entry point adds crash guards.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import platform
import shutil
import sqlite3
import sys

import project_session as session
from nasaq_core import state as durable
from nasaq_core.routing import command

USER_ACTIONS = {'start', 'approve_requirements', 'delegate', 'approve_planning',
                'control', 'continue', 'pause', 'resume', 'language', 'recover', 'installation_apply',
                'execution_approve', 'execution_control', 'execution_pause', 'execution_resume', 'execution_continue'}


def identity(project):
    result = subprocess.run(['git', '-C', str(project), 'rev-parse', '--show-toplevel'],
                            capture_output=True, text=True, timeout=10)
    if result.returncode:
        return {'root': str(project.resolve()), 'git': None}
    branch = subprocess.run(['git', '-C', str(project), 'rev-parse', '--abbrev-ref', 'HEAD'],
                            capture_output=True, text=True, timeout=10)
    if branch.returncode:
        raise ValueError('repository_identity_unavailable')
    return {'root': str(Path(result.stdout.strip()).resolve()), 'git': branch.stdout.strip()}


def dispatch(project, event, *, test_mode=False):
    project = Path(project).resolve()
    if not isinstance(event, dict) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', event.get('id', '')):
        raise ValueError('invalid_event_id')
    if not isinstance(event.get('action'), str) or not isinstance(event.get('data', {}), dict):
        raise ValueError('invalid_event')
    event = {**event, 'action': command(event['action'])}
    if event.get('origin') == 'test_fixture' and not test_mode:
        raise ValueError('fixture_origin_forbidden')
    requires_user = event['action'] in USER_ACTIONS or (event['action'] == 'select'
                    and event.get('data', {}).get('choice') != 'delegated')
    if requires_user and (event.get('origin') not in ({'user', 'test_fixture'} if test_mode else {'user'})
                          or not event.get('text', '').strip()):
        raise ValueError('user_message_required')
    if event['action'] == 'doctor':
        return {'ok': True, 'python': sys.version, 'os': platform.platform(), 'sqlite': sqlite3.sqlite_version,
                'available_tools': {name: shutil.which(name) for name in ('git', 'pwsh', 'node', 'npm', 'docker', 'codex', 'claude', 'cursor')},
                'writes': [], 'services_tested': False, 'hosts_tested': False, 'background_execution': False}
    if event['action'] == 'inspect':
        from nasaq_core.project_inspection import inspect
        return inspect(project)
    if event['action'] in {'installation_preview', 'installation_apply'}:
        from nasaq_core import installation
        proposal = installation.preview(project, Path(__file__).resolve().parents[1],
                                        event['data']['host'], event['data'].get('operation', 'install'))
        if event['action'] == 'installation_preview':
            return {'ok': True, 'preview': proposal, 'writes_performed': []}
        if event['data'].get('digest') != proposal['digest']:
            raise ValueError('stale_install_approval')
        return installation.apply(proposal)
    if event['action'] == 'recover':
        durable.clear_dead_writer(project)
    with durable.writer(project) as metadata:
        runtime_path = metadata / 'runtime.json'
        runtime = durable.read(runtime_path) if runtime_path.exists() else {
            'schema_version': 1, 'test_mode': test_mode, 'identity': identity(project),
            'change_id': 'change-001', 'product_language': None}
        if runtime['test_mode'] != test_mode:
            raise ValueError('test_mode_cannot_change')
        if runtime['identity'] != identity(project):
            raise ValueError('project_or_branch_changed')
        journal_path = metadata / 'requests.json'
        journal = durable.read(journal_path) if journal_path.exists() else {'schema_version': 1, 'requests': {}}
        requests = journal['requests']
        digest = durable.fingerprint(event)
        previous = requests.get(event['id'])
        if previous:
            if previous['digest'] != digest:
                raise ValueError('event_id_conflict')
            if previous['status'] == 'completed':
                return {**previous['result'], 'replayed': True}
            raise ValueError('partial_request_recovery_required')
        pending = [key for key, value in requests.items() if value['status'] == 'pending']
        if pending and event['action'] != 'recover':
            raise ValueError('partial_request_recovery_required')
        if event['action'] == 'recover':
            if event['data'].get('resolve') != pending:
                raise ValueError('recovery_selection_mismatch')
            # Integrity checks only; do not replay an external command or infer
            # success from generated files. Abort unresolved requests explicitly.
            if (metadata / 'project.json').exists():
                stored = durable.read(metadata / 'project.json')
                run = session.get_run(project, stored)
                if run:
                    session.bridge.checked(run)
            for key in pending:
                requests[key]['status'] = 'aborted_requires_review'
                requests[key]['recovery_message'] = event['text']
            result = {'ok': True, 'resolved': pending, 'external_actions_replayed': False,
                      'reply': 'راجعت الحالة؛ لم تُعد الأوامر الخارجية.'}
        else:
            requests[event['id']] = {'digest': digest, 'status': 'pending', 'started': durable.now()}
            durable.write(runtime_path, runtime)
            durable.write(journal_path, journal)
            if event['action'].startswith('execution_') or event['action'] in {'source_run', 'source_handoff'}:
                from nasaq_core import execution
                # Rejected validation is a finished request, not a crash. No
                # native source commands run inside this state transition.
                try:
                    if event['action'] == 'source_handoff':
                        from nasaq_core.workflows import handoff
                        result = handoff(project, runtime, event)
                    elif event['action'] == 'source_run':
                        from nasaq_core.tools import run
                        result = run(project, runtime, event)
                    else:
                        result = execution.apply(project, runtime, event)
                except (ValueError, KeyError, OSError) as exc:
                    result = {'ok': False, 'error': str(exc)}
                durable.write(runtime_path, runtime)
            else:
                result = session.dispatch(project, event)
        requests[event['id']] = {'digest': digest, 'status': 'completed', 'result': result,
                                 'completed': durable.now()}
        durable.write(journal_path, journal)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--event', required=True, type=Path)
    parser.add_argument('--test-mode', action='store_true', help='Label an isolated synthetic test session permanently.')
    args = parser.parse_args()
    try:
        result = dispatch(args.project, durable.read(args.event), test_mode=args.test_mode)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        result = {'ok': False, 'error': str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
