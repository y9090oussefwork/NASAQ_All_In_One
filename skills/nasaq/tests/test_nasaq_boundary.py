"""Boundary tests are synthetic except the explicitly labelled crash process."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import nasaq
from nasaq_core import state


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'عربي with spaces'
        self.ev = {'id': 'status-1', 'action': 'status', 'origin': 'host', 'data': {}}

    def test_fixture_approval_cannot_enter_user_mode(self):
        ev = {**self.ev, 'action': 'start', 'origin': 'test_fixture', 'text': 'fixture'}
        with self.assertRaisesRegex(ValueError, 'fixture_origin_forbidden'):
            nasaq.dispatch(self.project, ev)
        self.assertFalse(self.project.exists())

    def test_host_cannot_fabricate_direct_approval(self):
        for action in nasaq.USER_ACTIONS:
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, 'user_message_required'):
                nasaq.dispatch(self.project, {**self.ev, 'action': action, 'text': 'approve'})

    def test_completed_request_is_not_executed_twice(self):
        with patch.object(nasaq.session, 'dispatch', return_value={'ok': True, 'count': 1}) as call:
            first = nasaq.dispatch(self.project, self.ev)
            second = nasaq.dispatch(self.project, self.ev)
        self.assertEqual(1, call.call_count)
        self.assertEqual(first['count'], second['count'])
        self.assertTrue(second['replayed'])

    def test_id_reuse_with_new_payload_is_rejected(self):
        with patch.object(nasaq.session, 'dispatch', return_value={'ok': True}):
            nasaq.dispatch(self.project, self.ev)
        with self.assertRaisesRegex(ValueError, 'event_id_conflict'):
            nasaq.dispatch(self.project, {**self.ev, 'data': {'different': True}})

    def test_pending_failure_never_replays_implicitly(self):
        with patch.object(nasaq.session, 'dispatch', side_effect=OSError('injected crash')):
            with self.assertRaisesRegex(OSError, 'injected crash'):
                nasaq.dispatch(self.project, self.ev)
        with patch.object(nasaq.session, 'dispatch') as call:
            with self.assertRaisesRegex(ValueError, 'partial_request_recovery_required'):
                nasaq.dispatch(self.project, {**self.ev, 'id': 'next'})
            call.assert_not_called()
        journal = state.read(self.project / '.nasaq/requests.json')
        self.assertEqual('pending', journal['requests']['status-1']['status'])

    def test_explicit_recovery_aborts_pending_does_not_claim_success(self):
        with patch.object(nasaq.session, 'dispatch', side_effect=OSError('partial')):
            with self.assertRaises(OSError):
                nasaq.dispatch(self.project, self.ev)
        ev = {'id': 'recover-1', 'action': 'recover', 'origin': 'user',
              'text': 'Reviewed effects; abort this unresolved request', 'data': {'resolve': ['status-1']}}
        result = nasaq.dispatch(self.project, ev)
        self.assertFalse(result['external_actions_replayed'])
        journal = state.read(self.project / '.nasaq/requests.json')
        self.assertEqual('aborted_requires_review', journal['requests']['status-1']['status'])

    def test_writer_excludes_another_writer(self):
        with state.writer(self.project):
            with self.assertRaisesRegex(ValueError, 'writer_busy'):
                with state.writer(self.project):
                    self.fail('second writer acquired lock')
        self.assertFalse((self.project / '.nasaq/writer.lock').exists())

    def test_recovery_cannot_steal_live_writer(self):
        with state.writer(self.project):
            with self.assertRaisesRegex(ValueError, 'writer_still_alive'):
                state.clear_dead_writer(self.project)

    def test_real_killed_writer_requires_explicit_recovery(self):
        # Actual child termination, not a mock. No external provider is run.
        script = ('import sys,time;sys.path.insert(0,sys.argv[1]);'
                  'from nasaq_core.state import writer;from pathlib import Path;'
                  'ctx=writer(Path(sys.argv[2]));ctx.__enter__();'
                  'Path(sys.argv[3]).write_text("ready");time.sleep(30)')
        ready = Path(self.temp.name) / 'ready'
        process = subprocess.Popen([sys.executable, '-B', '-c', script, str(SCRIPTS),
                                    str(self.project), str(ready)], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 10
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(ready.exists(), 'child failed to acquire lock')
            process.kill()
            process.wait(timeout=5)
            with self.assertRaisesRegex(ValueError, 'writer_busy'):
                with state.writer(self.project):
                    self.fail('stale lock silently stolen')
            self.assertTrue(state.clear_dead_writer(self.project))
            with state.writer(self.project):
                self.assertTrue((self.project / '.nasaq/writer.lock').exists())
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stderr.close()

    def test_branch_or_project_change_blocks_action(self):
        with patch.object(nasaq.session, 'dispatch', return_value={'ok': True}):
            nasaq.dispatch(self.project, self.ev)
        with patch.object(nasaq, 'identity', return_value={'root': 'other', 'git': 'different'}):
            with self.assertRaisesRegex(ValueError, 'project_or_branch_changed'):
                nasaq.dispatch(self.project, {**self.ev, 'id': 'next'})

    def test_test_mode_cannot_be_enabled_on_production_state(self):
        with patch.object(nasaq.session, 'dispatch', return_value={'ok': True}):
            nasaq.dispatch(self.project, self.ev)
        with self.assertRaisesRegex(ValueError, 'test_mode_cannot_change'):
            nasaq.dispatch(self.project, {**self.ev, 'id': 'next'}, test_mode=True)

    def test_unicode_payload_survives_atomic_write(self):
        path = Path(self.temp.name) / 'العربية.json'
        payload = {'text': 'نَسَق\r\nEnglish\u202e — C:\\x with space', 'emoji': '🌍'}
        state.write(path, payload)
        self.assertEqual(payload, state.read(path))
        self.assertEqual([], list(path.parent.glob('*.tmp')))

    def test_symlink_metadata_is_rejected_without_target_write(self):
        target = Path(self.temp.name) / 'target'
        target.mkdir()
        self.project.mkdir()
        link = self.project / '.nasaq'
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            if os.name != 'nt':
                raise
            completed = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                                       capture_output=True, text=True)
            self.assertEqual(0, completed.returncode, completed.stderr)
        with self.assertRaisesRegex(ValueError, 'metadata_link_not_allowed'):
            nasaq.dispatch(self.project, self.ev)
        self.assertEqual([], list(target.iterdir()))
