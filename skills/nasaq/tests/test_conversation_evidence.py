"""Read actual CLI journey evidence; simulated user turns are explicitly labelled."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import spec_kit_bridge as b

class ConversationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.base=ROOT.parents[1]/'.nasaq-local/experiments/conversation-001'
        if not (self.base/'evidence/en/43-status-output.json').exists():
            self.skipTest('Real CLI journey evidence absent; no source is run by this evidence check')
    def read(self,lang,name):
        return json.loads((self.base/'evidence'/lang/name).read_text(encoding='utf-8'))
    def run_for(self,lang):
        project=self.base/'projects'/lang
        state=json.loads((project/'.nasaq/project.json').read_text(encoding='utf-8'))
        return project/'.nasaq'/state['active_run'],state
    def test_interactive_inputs_revised_approved_and_routed(self):
        for lang in ['ar','en']:
            run,state=self.run_for(lang)
            self.assertNotIn('favorites' if lang=='en' else 'مفضلة',state['facts']['features']['value'])
            self.assertEqual('test_fixture',state['requirements_approval']['evidence']['origin'])
            self.assertFalse(self.read(lang,'04-blocked-approval-output.json')['ok'])
            self.assertFalse(self.read(lang,'13-before-approval-output.json')['ok'])
            self.assertTrue(self.read(lang,'41-results-output.json')['complete'])
            self.assertEqual('workflow-reference',b.checked(run)[0]['mode'])
            self.assertIn(state['facts']['idea']['value'],(run/'request.md').read_text(encoding='utf-8'))
    def test_source_scripts_and_handoffs_are_real_and_ordered(self):
        for lang in ['ar','en']:
            run,state=self.run_for(lang); rs,lock=b.checked(run)
            for stage in b.STAGES:
                self.assertEqual('completed',rs['stages'][stage]['status'])
                result=json.loads((run/f'evidence/{stage}-script.json').read_text(encoding='utf-8'))
                self.assertEqual(0,result['exit_code'])
                handoff=json.loads((run/f'evidence/{stage}-handoff.json').read_text(encoding='utf-8'))
                self.assertEqual((Path(lock['upstream'])/f'templates/commands/{stage}.md').read_text(encoding='utf-8'),handoff['instructions'])
            events=[json.loads(x) for x in (run/'events.jsonl').read_text(encoding='utf-8').splitlines()]
            for stage in b.STAGES:
                matching=[e['action'] for e in events if e.get('stage')==stage]
                self.assertEqual(['stage_started','host_output_submitted','stage_completed'],matching)
    def test_outputs_are_submitted_through_nasaq_with_traceable_bytes(self):
        for lang in ['ar','en']:
            run,_=self.run_for(lang)
            for stage in b.STAGES:
                receipt=json.loads((run/f'evidence/{stage}-submission.json').read_text(encoding='utf-8'))
                self.assertEqual(b.digest(run/f'evidence/{stage}-handoff.json'),receipt['handoff_sha256'])
                for name,value in receipt['content_sha256'].items():
                    if receipt.get('schema_version')==2:
                        self.assertEqual(b.digest(run/name),value)
                    else:
                        # Historical v1 saved submitted-text hashes before Windows
                        # newline conversion. run.json independently checks file bytes.
                        logical=(run/name).read_text(encoding='utf-8').encode('utf-8')
                        self.assertEqual(hashlib.sha256(logical).hexdigest(),value)
                self.assertEqual(set(receipt['content_sha256']),set(b.stage_outputs(b.checked(run)[0],stage)))
    def test_checkpoint_and_interrupted_handoff_preserve_completed_work(self):
        snapshot=json.loads((self.base/'evidence/resume-snapshot.json').read_text())
        for lang in ['ar','en']:
            run,_=self.run_for(lang)
            for name,old in snapshot[lang].items():
                self.assertEqual(old['sha256'],b.digest(run/name))
                self.assertEqual(old['mtime_ns'],(run/name).stat().st_mtime_ns)
            self.assertTrue(self.read(lang,'24-still-checkpoint-output.json')['checkpoint'])
            self.assertTrue(self.read(lang,'28-interrupted-resume-output.json')['resumed_handoff'])
            self.assertFalse(self.read(lang,'42-no-publish-output.json')['ok'])
        self.assertEqual('change_control_to_extend_limit',self.read('en','31-no-limit-bypass-output.json')['error'])
    def test_final_artifacts_match_both_languages_and_scope(self):
        import re
        identifiers=[]
        for lang in ['ar','en']:
            run,_=self.run_for(lang)
            spec=(run/'specs/001-project/spec.md').read_text(encoding='utf-8')
            tasks=(run/'specs/001-project/tasks.md').read_text(encoding='utf-8')
            identifiers.append(set(re.findall(r'\*\*(FR-\d+|SC-\d+)\*\*',spec)))
            self.assertEqual(14,len(re.findall(r'^- \[ \] T\d{3}',tasks,re.M)))
            self.assertNotIn('- [x]',tasks)
            self.assertTrue(all(i in tasks for i in identifiers[-1]))
            self.assertFalse((run/'web').exists())
        self.assertEqual(identifiers[0],identifiers[1]); self.assertEqual(10,len(identifiers[0]))

if __name__=='__main__': unittest.main()
