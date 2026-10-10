"""Build a clean local Nasaq skill archive from one source directory."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills' / 'nasaq'
DIST = ROOT / 'dist' / 'nasaq-web-1.0.0-rc.3'
ZIP = DIST / 'skill.zip'
EXCLUDE_DIRS = {'.git', '__pycache__', 'tests'}
EXCLUDE_SUFFIXES = {'.pyc'}


def safe_name(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('unsafe package path')
    return name


def files():
    for path in sorted(SOURCE.rglob('*')):
        if not path.is_file() or any(part in EXCLUDE_DIRS for part in path.parts) or path.suffix in EXCLUDE_SUFFIXES:
            continue
        relative = path.relative_to(SOURCE).as_posix()
        safe_name(relative)
        if path.is_symlink() or path.resolve() != path:
            raise ValueError('package source symlink')
        yield path, relative


def main():
    if not (SOURCE / 'SKILL.md').is_file():
        raise SystemExit('SKILL.md missing')
    if not DIST.resolve().is_relative_to(ROOT.resolve()) or DIST.is_symlink():
        raise SystemExit('unsafe output directory')
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    manifest = []
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, relative in files():
            archive_name = 'nasaq/' + relative
            archive.write(path, archive_name)
            manifest.append({'path': archive_name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': path.stat().st_size})
    if sum(1 for item in manifest if item['path'].endswith('/SKILL.md')) != 1:
        raise SystemExit('package must contain one SKILL.md')
    result = {'schema_version': 1, 'package': 'nasaq-web-1.0.0-rc.3', 'source': 'skills/nasaq',
              'entries': manifest, 'zip_sha256': hashlib.sha256(ZIP.read_bytes()).hexdigest(),
              'size_bytes': ZIP.stat().st_size, 'external_sources_included': False,
              'node_modules_included': False, 'private_evidence_included': False}
    (DIST / 'source-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (DIST / 'README.md').write_text('# نَسَق — حزمة ويب محلية\n\nثبّت المهارة في جذر اختبار بعد مراجعة المعاينة. لا تتضمن الحزمة مصادر خارجية أو بيئات تنفيذ. راجع الأدلة العربية في المستودع.\n', encoding='utf-8')
    (DIST / 'README.en.md').write_text('# Nasaq — Local web package\n\nInstall the skill in a test root after reviewing the preview. The package contains no external sources or runtimes.\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()





