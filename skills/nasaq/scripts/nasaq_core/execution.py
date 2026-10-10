"""Approved phase boundaries, not a planner or application generator.

The host supplies a concrete plan. This module owns only approval, checkpoints,
input/output integrity and verification receipts. Source runners own execution.
"""
import hashlib
from pathlib import Path
import re

from nasaq_core.state import fingerprint, now, read

PERMISSIONS = {'project_write', 'local_process', 'local_download', 'loopback_server', 'isolated_database'}


def path_in(project, relative):
    if not isinstance(relative, str) or '\\' in relative or ':' in relative:
        raise ValueError('invalid_artifact_path')
    path = project / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or path.resolve() != path or path == project:
        raise ValueError('artifact_path_escape_or_link')
    return path


def hashes(project, names):
    return {name: hashlib.sha256(path_in(project, name).read_bytes()).hexdigest() for name in names}


def validate(plan, project):
    if not isinstance(plan, dict) or set(plan) != {'change_id', 'requirements_digest', 'selection_digest', 'profile', 'product_language', 'phases'}:
        raise ValueError('invalid_execution_plan')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', plan['change_id']):
        raise ValueError('invalid_change_id')
    if plan['profile'] not in {'W1', 'W2', 'W3'} or plan['product_language'] not in {'ar', 'en', 'bilingual'}:
        raise ValueError('invalid_execution_profile_or_language')
    phases = plan['phases']
    if not isinstance(phases, list) or not 1 <= len(phases) <= 32:
        raise ValueError('invalid_execution_phases')
    ids, outputs, slots = set(), set(), set()
    for phase in phases:
        if set(phase) != {'id', 'owner', 'capability', 'component', 'source', 'inputs', 'outputs', 'permissions', 'acceptance'}:
            raise ValueError('invalid_phase_contract')
        if not all(isinstance(phase[k], str) and phase[k] for k in ('id', 'owner', 'capability', 'component', 'source')):
            raise ValueError('invalid_phase_contract')
        if phase['id'] in ids or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', phase['id']):
            raise ValueError('duplicate_or_invalid_phase')
        ids.add(phase['id'])
        slot = (phase['capability'], phase['component'], phase['id'])
        if slot in slots:
            raise ValueError('phase_owner_conflict')
        slots.add(slot)
        for key in ('inputs', 'outputs', 'permissions', 'acceptance'):
            if not isinstance(phase[key], list) or not all(isinstance(x, str) and x for x in phase[key]) or len(set(phase[key])) != len(phase[key]):
                raise ValueError('invalid_phase_contract')
        if not phase['outputs'] or not phase['acceptance'] or not set(phase['permissions']) <= PERMISSIONS:
            raise ValueError('invalid_phase_contract')
        for name in phase['inputs'] + phase['outputs']:
            path_in(project, name)
        if outputs.intersection(phase['outputs']):
            raise ValueError('artifact_owner_conflict')
        outputs.update(phase['outputs'])
    return plan


def apply(project, runtime, event):
    data, action = event['data'], event['action']
    execution = runtime.get('execution')
    if action == 'execution_propose':
        from project_session import fingerprint as session_fingerprint, load_json, revision_hash, get_run, bridge
        stored = load_json(project / '.nasaq/project.json')
        plan = validate(data['plan'], project)
        if stored['requirements_approval'].get('digest') != revision_hash(stored) or stored['selection_approval'].get('digest') != session_fingerprint(stored['proposal']):
            raise ValueError('prior_approval_missing')
        if plan['requirements_digest'] != revision_hash(stored) or plan['selection_digest'] != session_fingerprint(stored['proposal']):
            raise ValueError('stale_execution_inputs')
        run = get_run(project, stored)
        if not run or any(s['status'] != 'completed' for s in bridge.checked(run)[0]['stages'].values()):
            raise ValueError('planning_incomplete')
        selected = {s['id'] for s in stored['proposal']['sources']}
        if any(p['source'] not in selected for p in plan['phases']):
            raise ValueError('unselected_execution_source')
        if execution and execution['plan'] == plan:
            return {'ok': True, 'plan_digest': execution['digest'], 'unchanged': True}
        if execution and any(p['status'] == 'running' for p in execution['phases'].values()):
            raise ValueError('open_phase_change_requires_pause_review')
        runtime.setdefault('retained_executions', [])
        if execution:
            runtime['retained_executions'].append(execution)
        runtime['execution'] = {'plan': plan, 'digest': fingerprint(plan), 'approval': None,
                                'phases': {p['id']: {'status': 'pending'} for p in plan['phases']},
                                'paused': False, 'control': {'mode': 'each'}, 'acknowledged': 0}
        runtime['change_id'], runtime['product_language'] = plan['change_id'], plan['product_language']
        return {'ok': True, 'plan_digest': fingerprint(plan), 'plan': plan}
    if not execution:
        raise ValueError('execution_plan_missing')
    if action == 'execution_approve':
        if data.get('digest') != execution['digest']:
            raise ValueError('stale_execution_approval')
        execution['approval'] = {'digest': execution['digest'], 'message_id': event['id'],
                                 'origin': event['origin'], 'text': event['text'], 'at': now()}
        return {'ok': True, 'approved': execution['digest']}
    if action == 'execution_control':
        mode = data.get('mode')
        if mode not in {'each', 'until', 'every', 'all-approved'}:
            raise ValueError('invalid_control')
        if mode == 'until' and data.get('phase') not in execution['phases']:
            raise ValueError('invalid_control')
        if mode == 'every' and (type(data.get('count')) is not int or data['count'] < 1):
            raise ValueError('invalid_control')
        execution['control'] = data
        execution['acknowledged'] = sum(p['status'] == 'completed' for p in execution['phases'].values())
        return {'ok': True, 'control': data, 'background_execution': False}
    if action in {'execution_pause', 'execution_resume'}:
        execution['paused'] = action == 'execution_pause'
        return {'ok': True, 'paused': execution['paused'], 'background_execution': False}
    if action == 'execution_status':
        return {'ok': True, 'execution': execution, 'product_language': runtime['product_language']}
    if action == 'execution_continue':
        execution['acknowledged'] = sum(p['status'] == 'completed' for p in execution['phases'].values())
        return {'ok': True, 'review_recorded': True}
    if execution['paused']:
        raise ValueError('paused')
    from project_session import fingerprint as sf, load_json, revision_hash
    stored = load_json(project / '.nasaq/project.json')
    if (execution['plan']['requirements_digest'] != revision_hash(stored)
            or execution['plan']['selection_digest'] != sf(stored['proposal'])
            or stored['requirements_approval'].get('digest') != revision_hash(stored)
            or stored['selection_approval'].get('digest') != sf(stored['proposal'])):
        raise ValueError('stale_execution_inputs')
    if not execution['approval'] or execution['approval']['digest'] != execution['digest']:
        raise ValueError('execution_not_approved')
    for phase in execution['phases'].values():
        if phase['status'] == 'completed' and hashes(project, list(phase['output_hashes'])) != phase['output_hashes']:
            raise ValueError('completed_artifact_changed')
        if phase['status'] == 'completed':
            receipt_path = path_in(project, phase['receipt'])
            if hashlib.sha256(receipt_path.read_bytes()).hexdigest() != phase['receipt_sha256']:
                raise ValueError('completed_receipt_changed')
            receipt = read(receipt_path)
            for check in receipt['checks']:
                if hashlib.sha256(path_in(project, check['evidence']).read_bytes()).hexdigest() != check['sha256']:
                    raise ValueError('verification_evidence_changed')
            if hashlib.sha256(path_in(project, receipt['source_evidence']).read_bytes()).hexdigest() != receipt['source_evidence_sha256']:
                raise ValueError('source_evidence_changed')
    index = next((i for i, p in enumerate(execution['plan']['phases']) if execution['phases'][p['id']]['status'] != 'completed'), None)
    if index is None:
        return {'ok': True, 'complete': True}
    contract = execution['plan']['phases'][index]
    phase = execution['phases'][contract['id']]
    if action == 'execution_begin':
        mode = execution['control']['mode']
        if mode == 'until' and index > next(i for i, p in enumerate(execution['plan']['phases']) if p['id'] == execution['control']['phase']):
            return {'ok': True, 'checkpoint': True, 'limit_reached': True}
        cadence = 1 if mode == 'each' else execution['control'].get('count', 1)
        if mode in {'each', 'every'} and index - execution['acknowledged'] >= cadence:
            return {'ok': True, 'checkpoint': True}
        if phase['status'] == 'running':
            if hashes(project, contract['inputs']) != phase['input_hashes']:
                raise ValueError('phase_input_changed')
            return {'ok': True, 'phase': contract, 'resumed_handoff': True,
                    'note': 'Restore the recorded source handoff; do not rerun the source.'}
        if phase['status'] != 'pending':
            raise ValueError('phase_recovery_required')
        phase.update(status='running', input_hashes=hashes(project, contract['inputs']), started=now())
        return {'ok': True, 'phase': contract, 'source_handoff_required': True,
                'note': 'Boundary open; source use and verification remain required before completion.'}
    if action == 'execution_complete':
        if data.get('phase') != contract['id'] or phase['status'] != 'running':
            raise ValueError('phase_not_running')
        if hashes(project, contract['inputs']) != phase['input_hashes']:
            raise ValueError('phase_input_changed')
        receipt_path = path_in(project, data['receipt'])
        receipt = read(receipt_path)
        outputs = hashes(project, contract['outputs'])
        if (receipt.get('phase') != contract['id'] or receipt.get('source') != contract['source']
                or receipt.get('output_hashes') != outputs or receipt.get('plan_digest') != execution['digest']):
            raise ValueError('verification_receipt_mismatch')
        checks = receipt.get('checks', [])
        if not checks or {c['criterion'] for c in checks} != set(contract['acceptance']) or any(c.get('status') != 'passed' for c in checks):
            raise ValueError('quality_gate_not_passed')
        for check in checks:
            evidence = path_in(project, check['evidence'])
            if hashlib.sha256(evidence.read_bytes()).hexdigest() != check.get('sha256'):
                raise ValueError('verification_evidence_changed')
        source_evidence = path_in(project, receipt['source_evidence'])
        if hashlib.sha256(source_evidence.read_bytes()).hexdigest() != receipt.get('source_evidence_sha256'):
            raise ValueError('source_evidence_changed')
        phase.update(status='completed', output_hashes=outputs, receipt=data['receipt'],
                     receipt_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(), completed=now())
        return {'ok': True, 'phase_completed': contract['id'], 'evidence_kind': receipt.get('evidence_kind', 'host-recorded')}
    raise ValueError('unknown_execution_action')
