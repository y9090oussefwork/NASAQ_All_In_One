"""Bounded read-only project facts. No installs/builds/tests or shell commands."""
import json
import os
from pathlib import Path

IGNORE = {'.git', '.nasaq', '.nasaq-local', 'node_modules', '.venv', 'venv', '__pycache__',
          '.agents', '.claude', '.cursor', '.env', 'dist', 'build'}
INSTRUCTIONS = ('AGENTS.md', 'CLAUDE.md', 'PRODUCT.md', 'DESIGN.md')


def inspect(project):
    project = Path(project).resolve()
    if not project.is_dir():
        raise ValueError('project_missing')
    files, links, stack, errors = [], [], [], []
    for folder, directories, filenames in os.walk(project, followlinks=False):
        base = Path(folder)
        kept = []
        for name in directories:
            item = base / name
            if name in IGNORE or name.startswith('.env'):
                continue
            if item.resolve() != item:
                links.append(item.relative_to(project).as_posix())
            else:
                kept.append(name)
        directories[:] = kept
        for name in filenames:
            if name in IGNORE or name.startswith('.env'):
                continue
            item = base / name
            if item.resolve() != item:
                links.append(item.relative_to(project).as_posix())
                continue
            files.append(item.relative_to(project).as_posix())
            if len(files) >= 2000:
                errors.append('file_count_limit; map incomplete')
                break
        if errors:
            break
    package = project / 'package.json'
    if package.is_file() and package.resolve() == package and package.stat().st_size <= 1024 * 1024:
        try:
            manifest = json.loads(package.read_text(encoding='utf-8-sig'))
            deps = {**manifest.get('dependencies', {}), **manifest.get('devDependencies', {})}
            stack.extend(name for name in ('react', 'vue', 'next', 'vite', '@angular/core') if name in deps)
        except (ValueError, TypeError):
            errors.append('package_manifest_invalid')
    for name in ('requirements.txt', 'pyproject.toml'):
        manifest = project / name
        if manifest.is_file() and manifest.resolve() == manifest and manifest.stat().st_size <= 1024 * 1024:
            text = manifest.read_text(encoding='utf-8').lower()
            stack.extend(name for name in ('django', 'flask', 'fastapi') if name in text)
    if not stack and any(f.endswith('.html') for f in files):
        stack.append('static')
    supported = not any(name in stack for name in ('vue', 'next', '@angular/core', 'flask', 'fastapi'))
    profile = 'W3' if supported and {'react', 'django'} <= set(stack) else 'W2' if supported and 'django' in stack else 'W1' if stack == ['static'] else None
    return {'ok': True, 'mode': 'read-only', 'files': files, 'skipped_links': links,
            'instructions': [name for name in INSTRUCTIONS if name in files], 'stack': sorted(set(stack)),
            'execution_profile': profile, 'execution_status': 'needs_review' if profile else 'unsupported-execution',
            'issues': errors, 'commands_run': [], 'writes': [],
            'unknown': ['feature coverage', 'authentication needs', 'database runtime', 'actual test results']}
