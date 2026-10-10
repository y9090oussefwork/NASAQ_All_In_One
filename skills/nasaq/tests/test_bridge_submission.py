import hashlib
import json
import unittest
import test_spec_kit_bridge as fixtures
import spec_kit_bridge as b

class SubmissionTests(unittest.TestCase):
    setUp=fixtures.BridgeStateTests.setUp
    save=fixtures.BridgeStateTests.save
    def active(self,stage='constitution',feature=None):
        if feature: self.state['feature']=feature
        self.state['stages'][stage]={'status':'running','input_hashes':{}}
        self.save()
        b.write_json(self.run/f'evidence/{stage}-handoff.json',{'stage':stage,'expected_outputs':b.stage_outputs(self.state,stage)})
    def test_submission_writes_exact_utf8_and_records_bytes(self):
        self.active()
        name=b.OUTPUTS['constitution'][0]; text='# دستور\n\nقاعدة\n'
        b.submit_outputs(self.run,'constitution',{name:text},'Synthetic host response, not live evidence')
        self.assertEqual(text.encode('utf-8'),(self.run/name).read_bytes())
        receipt=json.loads((self.run/'evidence/constitution-submission.json').read_text())
        self.assertEqual(hashlib.sha256((self.run/name).read_bytes()).hexdigest(),receipt['content_sha256'][name])
    def test_unknown_output_rejected_before_writes(self):
        self.active()
        with self.assertRaisesRegex(ValueError,'contract'):
            b.submit_outputs(self.run,'constitution',{'../escape.py':'x'},'note')
        self.assertFalse((self.base/'escape.py').exists())
        self.assertFalse((self.run/'evidence/constitution-submission.json').exists())
    def test_missing_output_does_not_mark_complete(self):
        self.active()
        with self.assertRaisesRegex(ValueError,'contract'): b.submit_outputs(self.run,'constitution',{},'note')
        self.assertEqual('running',b.checked(self.run)[0]['stages']['constitution']['status'])
    def test_output_requires_real_open_handoff(self):
        with self.assertRaisesRegex(ValueError,'active handoff'):
            b.submit_outputs(self.run,'constitution',{b.OUTPUTS['constitution'][0]:'x'},'note')
    def test_generic_feature_paths_preserve_legacy_default(self):
        self.assertEqual(b.OUTPUTS['plan'],b.stage_outputs({},'plan'))
        outputs=b.stage_outputs({'feature':'specs/001-project'},'plan')
        self.assertIn('specs/001-project/contracts/feature.md',outputs)
        self.assertFalse(any('booking' in p for p in outputs))
    def test_generic_submission_uses_selected_contract(self):
        self.active('plan','specs/001-project')
        files={p:'Synthetic content\n' for p in b.stage_outputs(self.state,'plan')}
        b.submit_outputs(self.run,'plan',files,'Synthetic generic contract test')
        self.assertEqual(set(files),set(b.checked(self.run)[0]['stages']['plan']['output_hashes']))

if __name__=='__main__': unittest.main()
