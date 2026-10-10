"""Pinned source preflight. Discovery entries never authorize execution."""
import hashlib
import shutil
from pathlib import Path
import re
import subprocess

from nasaq_core.state import read


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_configuration(path):
    config = read(path)
    if config.get('provider') != 'spec-kit' or config.get('mode') != 'workflow-reference':
        raise ValueError('unsupported_source_configuration')
    import spec_kit_bridge as bridge
    if config.get('commit') != bridge.COMMIT:
        raise ValueError('source_commit_not_supported')
    upstream = Path(config['upstream']).resolve()
    review = Path(config['review']).resolve()
    if file_hash(review) != config.get('review_sha256'):
        raise ValueError('source_review_changed')
    reviewed = read(review)
    if reviewed.get('commit') != bridge.COMMIT:
        raise ValueError('review_commit_mismatch')
    required = {item: file_hash(bridge.inside(upstream, item)) for item in bridge.SOURCE_FILES}
    if reviewed.get('files') != required:
        raise ValueError('review_source_bytes_mismatch')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(upstream), *args], text=True,
                                       timeout=15).strip()
    if git('rev-parse', 'HEAD') != bridge.COMMIT:
        raise ValueError('source_identity_mismatch')
    if git('remote', 'get-url', 'origin') != 'https://github.com/github/spec-kit.git':
        raise ValueError('source_origin_mismatch')
    if git('status', '--porcelain'):
        raise ValueError('source_checkout_modified')
    return {**config, 'upstream': str(upstream), 'review': str(review),
            'tested_scope': config.get('tested_scope', 'reviewed source; this configuration has not run planning yet')}


def validate_pin(source):
    if not re.fullmatch(r'[a-f0-9]{40}', source.get('commit', '')):
        raise ValueError('exact_source_commit_required')
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', source.get('repository', '')):
        raise ValueError('official_repository_required')
    if source.get('integration_mode') not in {'workflow-reference', 'library', 'reviewed-cli',
                                              'reviewed-cli/library', 'container'}:
        raise ValueError('unknown_integration_mode')
    return source


def inventory(checkouts):
    """Inspect pinned source checkouts without authorizing execution."""
    results = []
    for item in checkouts:
        path = Path(item['path']).resolve()
        row = {'name': item.get('name', path.name), 'path': str(path),
               'expected_commit': item.get('commit'), 'expected_origin': item.get('origin')}
        if not path.exists():
            row.update(status='missing', verified=False)
            results.append(row)
            continue
        try:
            def git(*args):
                return subprocess.check_output(['git', '-C', str(path), *args],
                                               text=True, stderr=subprocess.STDOUT,
                                               timeout=15).strip()
            row['actual_commit'] = git('rev-parse', 'HEAD')
            row['actual_origin'] = git('remote', 'get-url', 'origin')
            row['dirty'] = bool(git('status', '--porcelain'))
            row['verified'] = (row['actual_commit'] == item.get('commit') and
                               row['actual_origin'] == item.get('origin') and
                               not row['dirty'])
            row['status'] = 'verified' if row['verified'] else 'mismatch'
        except (subprocess.SubprocessError, OSError) as exc:
            row.update(status='blocked', verified=False, error=type(exc).__name__)
        results.append(row)
    return results


def rollback_checkout(target, archived):
    """Restore an approved checkout, preserving the current tree for recovery."""
    target = Path(target).resolve()
    archived = Path(archived).resolve()
    if not archived.is_dir() or target == archived or archived in target.parents:
        raise ValueError('invalid_rollback_source')
    backup = target.with_name(target.name + '.before-rollback')
    if backup.exists():
        raise ValueError('rollback_backup_exists')
    try:
        if target.exists():
            target.rename(backup)
        shutil.copytree(archived, target)
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup.exists():
            backup.rename(target)
        raise
    return {'target': str(target), 'archived': str(archived),
            'backup': str(backup) if backup.exists() else None, 'status': 'rolled_back'}
