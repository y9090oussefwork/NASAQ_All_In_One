"""Synthetic phase contracts verify boundaries, not external integrations."""
import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nasaq_core import execution as e
from nasaq_core import state
import project_session as session


class ExecutionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.stored = {'facts': {'idea': {'value': 'fixture'}}, 'questions': [],
                       'proposal': {'sources': [{'id': 'django'}]}, 'requirements_approval': {},
                       'selection_approval': {}}
        self.stored['requirements_approval']['digest'] = session.revision_hash(self.stored)
        self.stored['selection_approval']['digest'] = session.fingerprint(self.stored['proposal'])
        state.write(self.project / '.nasaq/project.json', self.stored)
        self.plan = {'change_id': 'change-1', 'requirements_digest': session.revision_hash(self.stored),
                     'selection_digest': session.fingerprint(self.stored['proposal']), 'profile': 'W2',
                     'product_language': 'ar', 'phases': [self.phase('backend', 'backend.txt'), self.phase('tests', 'tests.txt')]}
        self.runtime = {}
        # Synthetic completed planning evidence for unit-level state tests.
        # Live source use is tested separately, never inferred from this patch.
        self.run_patch = patch.object(session, 'get_run', return_value=self.project / 'synthetic-plan')
        self.checked_patch = patch.object(session.bridge, 'checked', return_value=({'stages': {'plan': {'status': 'completed'}}}, {}))
        self.run_patch.start()
        self.checked_patch.start()
        self.addCleanup(self.run_patch.stop)
        self.addCleanup(self.checked_patch.stop)

    def phase(self, name, output):
        return {'id': name, 'owner': 'fixture-host', 'capability': name, 'component': 'web', 'source': 'django',
                'inputs': [], 'outputs': [output], 'permissions': ['project_write', 'local_process'],
                'acceptance': ['criterion-' + name]}

    def call(self, action, data=None):
        return e.apply(self.project, self.runtime, {'id': 'test', 'action': action, 'origin': 'test_fixture',
                       'text': 'synthetic instruction', 'data': data or {}})

    def approved(self):
        proposal = self.call('execution_propose', {'plan': self.plan})
        self.call('execution_approve', {'digest': proposal['plan_digest']})

    def receipt(self, phase='backend', status='passed'):
        output = phase + '.txt'
        (self.project / output).write_text('fixture artifact')
        evidence = self.project / 'test-result.txt'
        evidence.write_text('synthetic check, no source run')
        source = self.project / 'source-use.txt'
        source.write_text('synthetic source receipt, no source run')
        receipt = {'phase': phase, 'source': 'django', 'plan_digest': self.runtime['execution']['digest'],
                   'output_hashes': e.hashes(self.project, [output]), 'evidence_kind': 'synthetic',
                   'source_evidence': source.name, 'source_evidence_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'checks': [{'criterion': 'criterion-' + phase, 'status': status, 'evidence': evidence.name,
                               'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()}]}
        state.write(self.project / 'receipt.json', receipt)
        return {'phase': phase, 'receipt': 'receipt.json'}

    def test_execution_requires_separate_exact_approval(self):
        self.call('execution_propose', {'plan': self.plan})
        with self.assertRaisesRegex(ValueError, 'execution_not_approved'):
            self.call('execution_begin')
        with self.assertRaisesRegex(ValueError, 'stale_execution_approval'):
            self.call('execution_approve', {'digest': 'old'})

    def test_incomplete_planning_blocks_execution_proposal(self):
        with patch.object(session.bridge, 'checked', return_value=({'stages': {'plan': {'status': 'pending'}}}, {})):
            with self.assertRaisesRegex(ValueError, 'planning_incomplete'):
                self.call('execution_propose', {'plan': self.plan})

    def test_one_owner_per_artifact(self):
        self.plan['phases'][1]['outputs'] = ['backend.txt']
        with self.assertRaisesRegex(ValueError, 'artifact_owner_conflict'):
            self.call('execution_propose', {'plan': self.plan})

    def test_unselected_source_never_enters_execution(self):
        self.plan['phases'][0]['source'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'unselected_execution_source'):
            self.call('execution_propose', {'plan': self.plan})

    def test_publication_is_not_local_execution_permission(self):
        self.plan['phases'][0]['permissions'].append('publish')
        with self.assertRaisesRegex(ValueError, 'invalid_phase_contract'):
            self.call('execution_propose', {'plan': self.plan})

    def test_outputs_cannot_escape_project(self):
        self.plan['phases'][0]['outputs'] = ['../outside.txt']
        with self.assertRaisesRegex(ValueError, 'artifact_path_escape'):
            self.call('execution_propose', {'plan': self.plan})

    def test_pause_resume_does_not_repeat_completed_phase(self):
        self.approved()
        self.call('execution_begin')
        self.call('execution_complete', self.receipt())
        self.call('execution_pause')
        with self.assertRaisesRegex(ValueError, 'paused'):
            self.call('execution_begin')
        self.call('execution_resume')
        self.assertTrue(self.call('execution_begin')['checkpoint'])
        self.call('execution_continue')
        result = self.call('execution_begin')
        self.assertEqual('tests', result['phase']['id'])

    def test_until_limit_cannot_be_extended_by_continue(self):
        self.approved()
        self.call('execution_control', {'mode': 'until', 'phase': 'backend'})
        self.call('execution_begin')
        self.call('execution_complete', self.receipt())
        self.call('execution_continue')
        self.assertTrue(self.call('execution_begin')['limit_reached'])

    def test_skipped_or_failed_verification_is_never_passed(self):
        self.approved()
        self.call('execution_begin')
        for status in ('skipped', 'failed', 'blocked', 'not_run'):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, 'quality_gate_not_passed'):
                self.call('execution_complete', self.receipt(status=status))
        self.assertEqual('running', self.runtime['execution']['phases']['backend']['status'])

    def test_later_requirements_change_blocks_old_approval(self):
        self.approved()
        self.stored['facts']['idea']['value'] = 'changed'
        state.write(self.project / '.nasaq/project.json', self.stored)
        with self.assertRaisesRegex(ValueError, 'stale_execution_inputs'):
            self.call('execution_begin')

    def test_completed_output_changed_invalidates_progress(self):
        self.approved()
        self.call('execution_control', {'mode': 'all-approved'})
        self.call('execution_begin')
        self.call('execution_complete', self.receipt())
        (self.project / 'backend.txt').write_text('changed after verification')
        with self.assertRaisesRegex(ValueError, 'completed_artifact_changed'):
            self.call('execution_begin')

    def test_changed_input_blocks_open_handoff(self):
        (self.project / 'input.txt').write_text('one')
        self.plan['phases'][0]['inputs'] = ['input.txt']
        self.approved()
        self.call('execution_begin')
        (self.project / 'input.txt').write_text('two')
        with self.assertRaisesRegex(ValueError, 'phase_input_changed'):
            self.call('execution_begin')

    def test_product_language_is_separate_from_display(self):
        self.approved()
        self.assertEqual('ar', self.runtime['product_language'])
        self.assertNotIn('language', self.runtime)
