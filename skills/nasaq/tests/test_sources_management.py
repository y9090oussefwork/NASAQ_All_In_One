import tempfile
import unittest
from pathlib import Path
import subprocess

from nasaq_core.sources import inventory, rollback_checkout


class SourceManagementTests(unittest.TestCase):
    def make_repo(self, root, name, commit='a' * 40):
        path = root / name
        path.mkdir()
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=path, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], cwd=path, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Nasaq Test'], cwd=path, check=True)
        (path / 'README').write_text('source', encoding='utf-8')
        subprocess.run(['git', 'add', '.'], cwd=path, check=True)
        subprocess.run(['git', 'commit', '-q', '-m', 'source'], cwd=path, check=True)
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip()
        subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/example/source.git'], cwd=path, check=True)
        return path, actual

    def test_inventory_verified_and_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            path, actual = self.make_repo(Path(d), 'source')
            rows = inventory([{'name': 'source', 'path': path, 'commit': actual,
                               'origin': 'https://github.com/example/source.git'}])
            self.assertEqual(rows[0]['status'], 'verified')
            (path / 'README').write_text('changed', encoding='utf-8')
            self.assertEqual(inventory([{'path': path, 'commit': actual,
                                         'origin': 'https://github.com/example/source.git'}])[0]['status'], 'mismatch')

    def test_inventory_missing(self):
        with tempfile.TemporaryDirectory() as d:
            row = inventory([{'path': Path(d) / 'missing', 'commit': 'a' * 40,
                              'origin': 'https://github.com/example/source.git'}])[0]
            self.assertEqual(row['status'], 'missing')

    def test_rollback_preserves_previous_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / 'current'; archived = root / 'archived'
            target.mkdir(); archived.mkdir()
            (target / 'state').write_text('new', encoding='utf-8')
            (archived / 'state').write_text('approved', encoding='utf-8')
            result = rollback_checkout(target, archived)
            self.assertEqual(result['status'], 'rolled_back')
            self.assertEqual((target / 'state').read_text(encoding='utf-8'), 'approved')
            self.assertEqual((root / 'current.before-rollback' / 'state').read_text(encoding='utf-8'), 'new')

    def test_rollback_rejects_nested_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); target = root / 'current'; target.mkdir()
            with self.assertRaises(ValueError):
                rollback_checkout(target, target / 'nested')


if __name__ == '__main__':
    unittest.main()
