import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from nasaq_core import workflows


class WorkflowReferenceTests(unittest.TestCase):
    def test_pin_table_is_exact_and_source_modes_are_explicit(self):
        self.assertEqual(workflows.PINS['impeccable'][1], 'd631a8827f99414d2b6daba4ef08b7f8701751d7')
        self.assertEqual(workflows.PINS['vercel-react'][1], '063bee94c3f4df8453406c830b0a7df0f2860278')

    def test_unapproved_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'source.json'
            p.write_text(json.dumps({'source': 'unknown', 'mode': 'workflow-reference'}), encoding='utf-8')
            event = {'data': {'configuration': str(p), 'configuration_sha256': hashlib.sha256(p.read_bytes()).hexdigest()}}
            with self.assertRaisesRegex(ValueError, 'unsupported_workflow_source'):
                workflows.handoff(Path(d), {'execution': {}}, event)


if __name__ == '__main__':
    unittest.main()
