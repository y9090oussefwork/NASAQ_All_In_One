"""Local state tests use synthetic files; live evidence tests never run a provider."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import spec_kit_bridge as b

class BridgeStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.run=self.base/'run'; self.run.mkdir()
        self.up=self.base/'source'; self.up.mkdir()
        for name in ['evidence','.specify/templates']:
            (self.run/name).mkdir(parents=True,exist_ok=True)
        for name in b.SOURCE_FILES:
            p=b.inside(self.up,name); p.parent.mkdir(parents=True,exist_ok=True); p.write_text('synthetic '+name)
        for t in b.TEMPLATES:
            (self.run/f'.specify/templates/{t}-template.md').write_bytes((self.up/f'templates/{t}-template.md').read_bytes())
        (self.run/'request.md').write_text('synthetic request')
        b.write_json(self.run/'selection.json',{})
        b.write_json(self.run/'source-lock.json',{'upstream':str(self.up),'files':{p:b.digest(self.up/p) for p in b.SOURCE_FILES}})
        self.state={'paused':False,'stages':{s:{'status':'pending'} for s in b.STAGES},
            'request_sha256':b.digest(self.run/'request.md'),'selection_sha256':b.digest(self.run/'selection.json'),
            'source_lock_sha256':b.digest(self.run/'source-lock.json')}
        self.save()
    def save(self): b.write_json(self.run/'run.json',self.state)
    def test_changed_request_blocks_resume(self):
        (self.run/'request.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed input'): b.resume(self.run)
    def test_changed_upstream_blocks_resume(self):
        (self.up/'LICENSE').write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed upstream'): b.resume(self.run)
    def test_changed_template_blocks_resume(self):
        (self.run/'.specify/templates/plan-template.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'template'): b.resume(self.run)
    def test_changed_selection_blocks_resume(self):
        b.write_json(self.run/'selection.json',{'different':True})
        with self.assertRaisesRegex(ValueError,'changed input'): b.resume(self.run)
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): b.inside(self.run,'../elsewhere')
    def test_implementation_not_routable(self):
        with self.assertRaisesRegex(ValueError,'unsupported'): b.begin(self.run,'implement')
    def test_cannot_skip_prerequisites(self):
        with self.assertRaisesRegex(ValueError,'prerequisite'): b.begin(self.run,'tasks')
    def test_partial_stage_requires_recovery(self):
        self.state['stages']['constitution']['status']='running'; self.save()
        with self.assertRaisesRegex(ValueError,'partial stage'): b.resume(self.run)
        with self.assertRaises(ValueError): b.pause(self.run)
    def test_missing_artifact_cannot_complete(self):
        self.state['stages']['constitution']={'status':'running','input_hashes':{}}; self.save()
        with self.assertRaisesRegex(ValueError,'missing output'): b.complete(self.run,'constitution','synthetic note')
    def test_pause_resume_preserves_completed_output(self):
        out=self.run/b.OUTPUTS['constitution'][0]; out.parent.mkdir(exist_ok=True); out.write_text('synthetic output')
        self.state['stages']['constitution']={'status':'running','input_hashes':{}}; self.save()
        b.complete(self.run,'constitution','synthetic, not upstream evidence')
        before=out.stat().st_mtime_ns,b.digest(out)
        b.pause(self.run)
        with self.assertRaises(ValueError): b.begin(self.run,'specify')
        self.assertEqual('specify',b.resume(self.run))
        self.assertEqual(before,(out.stat().st_mtime_ns,b.digest(out)))
        with self.assertRaises(ValueError): b.begin(self.run,'constitution')
    def test_modified_completed_output_not_reused(self):
        out=self.run/'evidence/output'; out.write_text('old')
        self.state['stages']['constitution']={'status':'completed','output_hashes':{'evidence/output':b.digest(out)}}; self.save()
        out.write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed completed'): b.resume(self.run)
    def test_hooks_cannot_be_silently_executed(self):
        (self.run/'.specify/extensions.yml').write_text('hooks: {}')
        with self.assertRaisesRegex(ValueError,'unreviewed'): b.checked(self.run)

class LivePilotEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.pilot=ROOT.parents[1]/'.nasaq-local/experiments/spec-kit-planning-001'
        if not (self.pilot/'evidence/pause-snapshot.json').exists():
            self.skipTest('Live pilot evidence not present; never download or fabricate it')
    def test_both_runs_complete_with_real_upstream_scripts(self):
        for lang in ['ar','en']:
            run=self.pilot/'runs'/lang
            state,lock=b.checked(run)
            self.assertEqual(b.COMMIT,lock['commit'])
            self.assertEqual('workflow-reference',state['mode'])
            for s in b.STAGES:
                self.assertEqual('completed',state['stages'][s]['status'])
                result=json.loads((run/f'evidence/{s}-script.json').read_text(encoding='utf-8'))
                self.assertEqual(0,result['exit_code'])
                packet=json.loads((run/f'evidence/{s}-handoff.json').read_text(encoding='utf-8'))
                self.assertEqual((Path(lock['upstream'])/f'templates/commands/{s}.md').read_text(encoding='utf-8'),packet['instructions'])
    def test_pause_resume_kept_bytes_and_mtimes(self):
        snapshot=json.loads((self.pilot/'evidence/pause-snapshot.json').read_text())
        for lang,files in snapshot.items():
            run=self.pilot/'runs'/lang
            for name,old in files.items():
                self.assertEqual(old['sha256'],b.digest(run/name))
                self.assertEqual(old['mtime_ns'],(run/name).stat().st_mtime_ns)
            events=[json.loads(line) for line in (run/'events.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(1,sum(e['action']=='stage_started' and e['stage']=='specify' for e in events))
            self.assertIn('paused',[e['action'] for e in events])
            self.assertEqual('clarify',next(e for e in events if e['action']=='resumed')['next_stage'])
    def test_ordered_handoff_before_completion(self):
        for lang in ['ar','en']:
            events=[json.loads(line) for line in (self.pilot/'runs'/lang/'events.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual('nasaq_request_routed',events[0]['action'])
            started=[e['stage'] for e in events if e['action']=='stage_started']
            finished=[e['stage'] for e in events if e['action']=='stage_completed']
            self.assertEqual(list(b.STAGES),started); self.assertEqual(started,finished)
            for s in b.STAGES:
                self.assertLess(next(i for i,e in enumerate(events) if e['action']=='stage_started' and e['stage']==s),next(i for i,e in enumerate(events) if e['action']=='stage_completed' and e['stage']==s))
    def test_equivalent_requirement_ids_and_unexecuted_tasks(self):
        import re
        specs=[]
        for lang in ['ar','en']:
            p=self.pilot/'runs'/lang/b.FEATURE
            specs.append(set(re.findall(r'\*\*(FR-\d+|SC-\d+)\*\*',(p/'spec.md').read_text(encoding='utf-8'))))
            tasks=(p/'tasks.md').read_text(encoding='utf-8')
            self.assertEqual(15,len(re.findall(r'^- \[ \] T\d{3}',tasks,re.M)))
            self.assertNotIn('- [x]',tasks)
            self.assertTrue(all(key in tasks for key in specs[-1]))
        self.assertEqual(specs[0],specs[1]); self.assertEqual(9,len(specs[0]))

if __name__=='__main__': unittest.main()
