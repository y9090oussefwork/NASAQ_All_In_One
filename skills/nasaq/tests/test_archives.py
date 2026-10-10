"""Malicious local synthetic archives; no external source execution."""
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nasaq_core.archives import inspect_archive


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'fixture.zip'

    def create(self, name='nasaq/reference.md', content=b'text'):
        with zipfile.ZipFile(self.path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('nasaq/SKILL.md', 'name: nasaq')
            # ZipInfo(name) silently converts backslashes on Windows. Override
            # after construction to actually place malformed spelling in bytes.
            info = zipfile.ZipInfo('placeholder')
            info.filename = name
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)

    def test_valid_archive_inspection_never_extracts(self):
        self.create()
        self.assertFalse(inspect_archive(self.path)['extracted'])
        self.assertEqual(['fixture.zip'], [p.name for p in self.path.parent.iterdir()])

    def test_traversal_absolute_windows_and_direction_paths_rejected(self):
        for name in ('../outside', '/absolute', 'C:/file', 'nasaq\\file', 'nasaq/CON', 'nasaq/\u202efile'):
            self.create(name)
            with self.subTest(name=name), self.assertRaises(ValueError):
                inspect_archive(self.path)

    def test_case_collisions_rejected(self):
        self.create('nasaq/skill.md')
        with self.assertRaisesRegex(ValueError, 'duplicate_name'):
            inspect_archive(self.path)

    def test_second_skill_entry_rejected(self):
        self.create('nasaq/other/SKILL.md')
        with self.assertRaisesRegex(ValueError, 'single_skill_entry'):
            inspect_archive(self.path)

    def test_symlink_entry_rejected(self):
        self.create()
        with zipfile.ZipFile(self.path, 'a') as archive:
            info = zipfile.ZipInfo('nasaq/link')
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, '../outside')
        with self.assertRaisesRegex(ValueError, 'link_or_special_file'):
            inspect_archive(self.path)

    def test_compression_bomb_rejected(self):
        self.create(content=b'x' * (2 * 1024 * 1024))
        with self.assertRaisesRegex(ValueError, 'compression_ratio_limit'):
            inspect_archive(self.path)
