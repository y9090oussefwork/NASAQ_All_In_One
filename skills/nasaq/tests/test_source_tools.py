"""Actual source configuration and runner boundary tests.

The successful Django invocation is recorded separately under the release
evidence. These tests verify that later calls cannot bypass its gates.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from nasaq_core.sources import checked_configuration
from nasaq_core.tools import run


class SourceToolsTests(unittest.TestCase):
    def test_real_spec_kit_configuration_matches_clean_pinned_source(self):
        root = ROOT.parents[1]
        run_dir = root / '.nasaq-local/experiments/spec-kit-planning-001/runs/ar'
        config_path = root / '.nasaq-local/web-release-1/evidence/P1/spec-kit-source-config.json'
        self.assertTrue(config_path.exists())
        config = checked_configuration(config_path)
        self.assertEqual('959e866caa3618bf3dc290d5dca33394365af9c6', config['commit'])
        self.assertEqual('workflow-reference', config['mode'])
        self.assertEqual(run_dir.resolve(), Path(config['review']).parents[1].resolve())

    def test_runner_rejects_missing_execution_approval_before_process(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            runtime = {'execution': {'digest': 'x', 'approval': None, 'phases': {}}}
            event = {'data': {'phase': 'x'}, 'id': 'x', 'text': 'run', 'origin': 'user'}
            with self.assertRaisesRegex(ValueError, 'execution_not_approved'):
                run(project, runtime, event)

    def test_runner_rejects_unreviewed_toolchain(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder); config = project / 'tool.json'; lock = project / 'lock.txt'
            lock.write_text('Django==5.2.18 --hash=sha256:fixture\n')
            config.write_text(json.dumps({'schema_version': 1, 'reviewed': False,
                'requirements_lock': str(lock), 'requirements_lock_sha256': hashlib.sha256(lock.read_bytes()).hexdigest()}))
            digest = 'x'; phase = {'id': 'p', 'source': 'django', 'permissions': ['local_process'], 'outputs': [], 'inputs': []}
            runtime = {'execution': {'digest': digest, 'approval': {'digest': digest}, 'paused': False,
                       'plan': {'phases': [phase]}, 'phases': {'p': {'status': 'running'}}}}
            event = {'id': 'x', 'text': 'run', 'origin': 'user', 'data': {'phase': 'p', 'source': 'django',
                     'toolchain': str(config), 'toolchain_sha256': hashlib.sha256(config.read_bytes()).hexdigest()}}
            with self.assertRaisesRegex(ValueError, 'toolchain_not_reviewed'):
                run(project, runtime, event)

    def test_source_run_receipt_is_actual_process_evidence(self):
        root = ROOT.parents[1]
        evidence = root / '.nasaq-local/web-release-1/evidence/P1/source-run-actual.json'
        self.assertTrue(evidence.exists())
        record = json.loads(evidence.read_text(encoding='utf-8'))
        self.assertTrue(record['actual_process'])
        self.assertEqual(0, record['result']['result']['exit_code'])
        self.assertEqual('reviewed-cli/library', record['integration_mode'])

