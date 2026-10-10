"""Real local filesystem ownership tests; no host discovery claimed."""
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from nasaq_core import installation as installer


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'SKILL.md').write_text('name: nasaq\nversion one', encoding='utf-8')
        (self.source / 'reference.md').write_text('one', encoding='utf-8')
        self.project = self.root / 'مشروع مع مسافات'

    def preview(self, op='install'):
        return installer.preview(self.project, self.source, 'codex', op)

    def install(self):
        return installer.apply(self.preview())

    def test_preview_does_not_create_project_or_files(self):
        self.assertEqual(2, len(self.preview()['writes']))
        self.assertFalse(self.project.exists())

    def test_install_then_repeat_is_idempotent(self):
        self.install()
        self.assertEqual([], self.preview()['writes'])
        installer.apply(self.preview())
        self.assertEqual(3, len(list((self.project / '.agents/skills/nasaq').iterdir())))

    def test_source_change_after_preview_rejected(self):
        proposal = self.preview()
        (self.source / 'reference.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'install_changed_since_preview'):
            installer.apply(proposal)
        self.assertFalse(self.project.exists())

    def test_target_change_after_preview_rejected(self):
        self.install()
        proposal = self.preview('uninstall')
        (self.project / '.agents/skills/nasaq/reference.md').write_text('user changed')
        with self.assertRaisesRegex(ValueError, 'install_changed_since_preview'):
            installer.apply(proposal)

    def test_update_preserves_unrelated_project_instructions(self):
        self.project.mkdir()
        instructions = self.project / 'AGENTS.md'
        instructions.write_text('user policy')
        self.install()
        (self.source / 'reference.md').write_text('two')
        result = installer.apply(self.preview('update'))
        self.assertIn('reference.md', result['written'])
        self.assertEqual('user policy', instructions.read_text())

    def test_modified_owned_file_blocks_update(self):
        self.install()
        dest = self.project / '.agents/skills/nasaq/reference.md'
        dest.write_text('user modified')
        proposal = self.preview('update')
        self.assertEqual(['reference.md'], proposal['conflicts'])
        with self.assertRaisesRegex(ValueError, 'user_file_conflict'):
            installer.apply(proposal)
        self.assertEqual('user modified', dest.read_text())

    def test_uninstall_preserves_user_modified_and_unowned_files(self):
        self.install()
        target = self.project / '.agents/skills/nasaq'
        (target / 'reference.md').write_text('user modified')
        (target / 'personal.txt').write_text('unowned')
        result = installer.apply(self.preview('uninstall'))
        self.assertEqual(['reference.md'], result['preserved'])
        self.assertFalse((target / 'SKILL.md').exists())
        self.assertEqual('user modified', (target / 'reference.md').read_text())
        self.assertEqual('unowned', (target / 'personal.txt').read_text())

    def test_unowned_identical_file_never_becomes_owned(self):
        target = self.project / '.agents/skills/nasaq'
        target.mkdir(parents=True)
        (target / 'reference.md').write_text('one')
        self.install()
        installer.apply(self.preview('uninstall'))
        self.assertTrue((target / 'reference.md').exists())

    def test_different_unowned_file_blocks_install(self):
        target = self.project / '.agents/skills/nasaq'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('user file')
        with self.assertRaisesRegex(ValueError, 'user_file_conflict'):
            self.install()

    def test_invalid_relative_paths_rejected(self):
        for rel in ('../escape', '/abs', 'x\\y', 'C:/file', 'x/NUL.txt', 'x/end.', 'x/end ', 'x/\u202efile'):
            with self.subTest(rel=rel), self.assertRaises(ValueError):
                installer.safe(self.project, rel)

    def test_source_target_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError, 'source_target_overlap'):
            installer.preview(self.project, self.project / '.agents/skills/nasaq', 'codex')

    def test_hosts_use_distinct_project_roots(self):
        for host, path in installer.HOST_PATHS.items():
            result = installer.preview(self.root / host, self.source, host)
            self.assertEqual(self.root / host / path, Path(result['target']))
