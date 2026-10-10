"""Read original pinned instructions through an approved Nasaq phase.

The host applies these instructions. Loading them never proves application or
quality; execution_complete still requires output hashes and check evidence.
"""
from pathlib import Path
import subprocess

from nasaq_core import execution
from nasaq_core.sources import file_hash, inventory
from nasaq_core.state import read, write, now

PINS = {
    'impeccable': ('https://github.com/pbakaus/impeccable.git',
                   'd631a8827f99414d2b6daba4ef08b7f8701751d7'),
    'vercel-react': ('https://github.com/vercel-labs/agent-skills.git',
                     '063bee94c3f4df8453406c830b0a7df0f2860278'),
}


def handoff(project, runtime, event):
    data = event['data']
    config_path = Path(data['configuration']).resolve()
    if file_hash(config_path) != data['configuration_sha256']:
        raise ValueError('workflow_configuration_changed')
    config = read(config_path)
    source = config['source']
    if source not in PINS or config.get('mode') != 'workflow-reference':
        raise ValueError('unsupported_workflow_source')
    origin, commit = PINS[source]
    if config.get('commit') != commit or config.get('origin') != origin:
        raise ValueError('workflow_pin_mismatch')
    checkout = Path(config['checkout']).resolve()
    result = inventory([{'path': checkout, 'commit': commit, 'origin': origin}])[0]
    if not result['verified']:
        raise ValueError('workflow_checkout_unverified')
    files = config.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('workflow_instructions_missing')
    documents = {}
    for relative, digest in files.items():
        path = execution.path_in(checkout, relative)
        if file_hash(path) != digest:
            raise ValueError('workflow_instruction_changed')
        if path.suffix != '.md' or path.stat().st_size > 256000:
            raise ValueError('workflow_instruction_not_text')
        documents[relative] = path.read_text(encoding='utf-8')
    active = runtime.get('execution', {})
    contract = next((p for p in active.get('plan', {}).get('phases', [])
                     if active['phases'][p['id']]['status'] != 'completed'), None)
    if not contract or contract['id'] != data.get('phase') or contract['source'] != source:
        raise ValueError('workflow_outside_phase_contract')
    if 'project_write' not in contract['permissions']:
        raise ValueError('workflow_receipt_write_not_approved')
    boundary = execution.apply(project, runtime, {**event, 'action': 'execution_begin', 'data': {}})
    if boundary.get('checkpoint'):
        return boundary
    receipt = execution.path_in(project, '.nasaq/evidence/' + event['id'] + '-workflow.json')
    if receipt.exists():
        raise ValueError('workflow_receipt_exists')
    record = {'schema_version': 1, 'phase': contract['id'], 'source': source,
              'mode': 'workflow-reference', 'commit': commit, 'origin': origin,
              'instruction_hashes': files, 'input_hashes': execution.hashes(project, contract['inputs']),
              'configuration_sha256': data['configuration_sha256'], 'at': now(),
              'plan_digest': active['digest'], 'status': 'instructions_loaded',
              'source_executable_ran': False, 'host_application_required': True}
    write(receipt, record)
    return {'ok': True, 'receipt': receipt.relative_to(project).as_posix(),
            'receipt_sha256': file_hash(receipt), 'documents': documents,
            'integration_mode': 'workflow-reference', 'application_proven': False}
