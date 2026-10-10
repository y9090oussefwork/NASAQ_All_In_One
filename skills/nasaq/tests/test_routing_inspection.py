"""Read-only project inspection and command-only normalization."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nasaq_core.routing import command
from nasaq_core.project_inspection import inspect
import nasaq


class RoutingInspectionTests(unittest.TestCase):
    def test_arabic_diacritics_and_english_same_action(self):
        for name in ('نَسَق الحَالَة', 'نسق حالة', 'Nasaq status', 'status'):
            self.assertEqual('status', command(name))

    def test_unknown_deletion_does_not_guess(self):
        self.assertNotIn(command('حزف'), {'delete', 'uninstall', 'installation_apply'})

    def test_inspection_respects_existing_stack_and_instructions(self):
        with tempfile.TemporaryDirectory() as root:
            project = Path(root)
            (project / 'package.json').write_text('{"dependencies":{"next":"15.0.0"}}')
            (project / 'AGENTS.md').write_text('Preserve existing provider')
            (project / '.env').write_text('do not read')
            before = {p.name: p.read_bytes() for p in project.iterdir()}
            result = inspect(project)
            self.assertEqual('unsupported-execution', result['execution_status'])
            self.assertIn('next', result['stack'])
            self.assertEqual(['AGENTS.md'], result['instructions'])
            self.assertNotIn('.env', result['files'])
            self.assertEqual(before, {p.name: p.read_bytes() for p in project.iterdir()})

    def test_nasaq_inspect_has_zero_state_writes(self):
        with tempfile.TemporaryDirectory() as root:
            project = Path(root)
            (project / 'index.html').write_text('<h1>Example</h1>')
            result = nasaq.dispatch(project, {'id': 'read-1', 'action': 'افحص المشروع', 'data': {}})
            self.assertEqual('W1', result['execution_profile'])
            self.assertFalse((project / '.nasaq').exists())

    def test_doctor_reports_presence_without_claiming_host_test(self):
        with tempfile.TemporaryDirectory() as root:
            result = nasaq.dispatch(Path(root) / 'absent', {'id': 'doctor-1', 'action': 'doctor', 'data': {}})
            self.assertFalse(result['hosts_tested'])
            self.assertFalse((Path(root) / 'absent').exists())
