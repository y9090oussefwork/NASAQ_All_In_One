"""Project-scoped skill installation with ownership and preview fingerprints.

Copies the current Nasaq source, not arbitrary archives. No host settings,
AGENTS.md or CLAUDE.md are edited. Uninstall removes unchanged owned files only.
"""
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import re

from nasaq_core.state import fingerprint, read, write

HOST_PATHS = {'codex': '.agents/skills/nasaq', 'claude': '.claude/skills/nasaq',
              'cursor': '.cursor/skills/nasaq'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(project, relative):
    if not isinstance(relative, str) or '\\' in relative:
        raise ValueError('invalid_relative_path')
    parts = PurePosixPath(relative).parts
    reserved = re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', re.I)
    if not parts or PurePosixPath(relative).is_absolute() or any(
            p in {'.', '..'} or ':' in p or p.endswith(('.', ' ')) or reserved.match(p)
            or any(ord(c) < 32 or c in '\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069' for c in p)
            for p in parts):
        raise ValueError('unsafe_install_path')
    path = project.joinpath(*parts)
    if path.resolve() != path or not path.is_relative_to(project):
        raise ValueError('install_link_or_escape')
    return path


def source_manifest(source):
    source = Path(source).resolve()
    result = {}
    for item in sorted(source.rglob('*')):
        rel = item.relative_to(source).as_posix()
        if '__pycache__' in item.parts or item.suffix == '.pyc' or item.name.startswith('.'):
            continue
        if item.is_symlink() or item.resolve() != item:
            raise ValueError('source_link_not_allowed')
        if item.is_file():
            result[rel] = digest(item)
    if 'SKILL.md' not in result:
        raise ValueError('skill_entry_missing')
    return result


def preview(project, source, host, operation='install'):
    project = Path(project).resolve()
    source = Path(source).resolve()
    if host not in HOST_PATHS or operation not in {'install', 'update', 'uninstall'}:
        raise ValueError('invalid_install_request')
    target = safe(project, HOST_PATHS[host])
    if source == target or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('source_target_overlap')
    ownership = target / 'nasaq-ownership.json'
    safe(project, ownership.relative_to(project).as_posix())
    old = read(ownership) if ownership.exists() else {'files': {}}
    if ownership.exists() and (old.get('host') != host or old.get('target') != str(target)
                               or old.get('schema_version') != 1):
        raise ValueError('ownership_invalid')
    desired = {} if operation == 'uninstall' else source_manifest(source)
    before, writes, deletes, preserved, conflicts = {}, [], [], [], []
    for rel in sorted(set(desired) | set(old['files'])):
        dest = safe(project, f'{HOST_PATHS[host]}/{rel}')
        actual = digest(dest) if dest.is_file() else None
        if dest.exists() and not dest.is_file():
            raise ValueError('non_file_destination')
        before[rel] = actual
        owned = old['files'].get(rel)
        if actual is not None and (owned is None or owned != actual):
            preserved.append(rel)
            if rel in desired and actual != desired[rel]:
                conflicts.append(rel)
            continue
        if rel in desired and actual != desired[rel]:
            writes.append(rel)
        elif rel not in desired and actual is not None:
            deletes.append(rel)
    proposal = {'schema_version': 1, 'project': str(project), 'source': str(source), 'host': host,
                'target': str(target), 'operation': operation, 'desired': desired,
                'ownership_before': digest(ownership) if ownership.exists() else None,
                'before': before, 'writes': writes, 'deletes': deletes,
                'preserved': preserved, 'conflicts': conflicts}
    return {**proposal, 'digest': fingerprint(proposal)}


def apply(proposal):
    current = preview(proposal['project'], proposal['source'], proposal['host'], proposal['operation'])
    if current['digest'] != proposal.get('digest'):
        raise ValueError('install_changed_since_preview')
    if current['conflicts']:
        raise ValueError('user_file_conflict')
    project, source, target = (Path(current[k]) for k in ('project', 'source', 'target'))
    for rel in current['writes']:
        dest = safe(project, f"{HOST_PATHS[current['host']]}/{rel}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Check exact bytes again immediately before copying. No lifecycle hook.
        if digest(source / rel) != current['desired'][rel]:
            raise ValueError('source_changed_during_install')
        actual = digest(dest) if dest.is_file() else None
        if actual != current['before'][rel]:
            raise ValueError('target_changed_during_install')
        shutil.copyfile(source / rel, dest)
    for rel in current['deletes']:
        dest = safe(project, f"{HOST_PATHS[current['host']]}/{rel}")
        if digest(dest) != current['before'][rel]:
            raise ValueError('target_changed_during_install')
        dest.unlink()
    if current['operation'] == 'uninstall':
        (target / 'nasaq-ownership.json').unlink(missing_ok=True)
    else:
        owned = {rel: digest(target / rel) for rel in current['desired'] if rel not in current['preserved']}
        write(target / 'nasaq-ownership.json', {'schema_version': 1, 'host': current['host'],
                                               'target': str(target), 'files': owned})
    return {'ok': True, 'written': current['writes'], 'removed': current['deletes'],
            'preserved': current['preserved'], 'target': str(target)}
