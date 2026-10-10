"""Inspect distribution archives without executing or extracting their members."""
from pathlib import Path, PurePosixPath
import stat
import zipfile

from nasaq_core.installation import safe


def inspect_archive(archive_path):
    archive_path = Path(archive_path)
    if archive_path.stat().st_size > 25 * 1024 * 1024:
        raise ValueError('archive_size_limit')
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if len(infos) > 2000:
            raise ValueError('archive_entry_limit')
        total, names, skills = 0, set(), []
        for info in infos:
            # zipfile normalizes Windows backslashes on read. Validate the raw
            # archive spelling as well, before accepting its normalized path.
            name = info.orig_filename.rstrip('/')
            safe(Path.cwd().resolve(), name)
            key = name.casefold()
            if key in names:
                raise ValueError('archive_duplicate_name')
            names.add(key)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                raise ValueError('archive_link_or_special_file')
            if info.flag_bits & 1:
                raise ValueError('archive_encrypted')
            total += info.file_size
            if total > 100 * 1024 * 1024 or info.file_size > 20 * 1024 * 1024:
                raise ValueError('archive_expanded_size_limit')
            if info.file_size > 1024 * 1024 and info.file_size / max(1, info.compress_size) > 200:
                raise ValueError('archive_compression_ratio_limit')
            if PurePosixPath(name).name == 'SKILL.md':
                skills.append(name)
        if len(skills) != 1 or skills[0] not in {'SKILL.md', 'nasaq/SKILL.md'}:
            raise ValueError('archive_requires_single_skill_entry')
        if archive.testzip() is not None:
            raise ValueError('archive_crc_mismatch')
        return {'ok': True, 'entries': len(infos), 'uncompressed_bytes': total,
                'skill_entry': skills[0], 'extracted': False}
