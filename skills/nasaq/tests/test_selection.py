import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('selection',ROOT/'scripts/check_selection.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
REG=m.load_json(ROOT/'assets/providers.json')
CAP=m.load_json(ROOT/'assets/capabilities.json')
EX=m.load_json(ROOT/'assets/examples/web-selection.draft.json')

class SelectionTests(unittest.TestCase):
    def setUp(self): self.plan=copy.deepcopy(EX)
    def codes(self, ready=False, plan=None, reg=None):
        return {x['code'] for x in m.validate_selection(self.plan if plan is None else plan,REG if reg is None else reg,CAP,ready=ready)}
    def test_valid_example(self): self.assertEqual(self.codes(),set())
    def test_duplicate_primary(self):
        x=copy.deepcopy(self.plan['bindings'][1]); x['id']='extra'; x['writes']=[]
        self.plan['bindings'].append(x)
        self.assertIn('duplicate_primary',self.codes())
    def test_duplicate_id(self):
        self.plan['bindings'].append(copy.deepcopy(self.plan['bindings'][0]))
        self.assertIn('duplicate_or_invalid_id',self.codes())
    def test_related_designers(self):
        p=m.load_json(ROOT/'assets/examples/conflicting-design.draft.json')
        self.assertTrue({'duplicate_primary','duplicate_lineage','output_overlap'} <= self.codes(plan=p))
    def test_reviewer_read_only(self):
        x=self.plan['bindings'][1];x['provider']='agency-ui-review';x['role']='reviewer'
        self.assertIn('read_only_role_writes',self.codes())
    def test_reviewer_cannot_be_primary(self):
        self.plan['bindings'][1]['provider']='agency-ui-review'
        self.assertIn('reviewer_role',self.codes())
    def test_reference_needs_adaptation(self):
        x=self.plan['bindings'][1];x['role']='reference';x['writes']=[]
        self.assertIn('adaptation_required',self.codes())
    def test_stack_mismatch(self):
        self.plan['components']['web']['tags']=['python']
        self.assertIn('stack_mismatch',self.codes())
    def test_unknown_provider(self):
        self.plan['bindings'][0]['provider']='not-registered'
        self.assertIn('unknown_provider',self.codes())
    def test_unsupported_capability(self):
        self.plan['bindings'][1]['capability']='data.postgres'
        self.assertIn('invalid_scope',self.codes())
    def test_missing_contract(self):
        self.plan['bindings'][1]['scope_contract']=' '
        self.assertIn('missing_contract',self.codes())
    def test_output_overlap_exact_and_directory_and_case(self):
        for path in ['apps/web/','apps/web/src/main.ts','APPS/WEB/']:
            with self.subTest(path=path):
                self.plan['bindings'][3]['writes']=[path]
                self.assertIn('output_overlap',self.codes())
    def test_different_phases_do_not_imply_simultaneous_writes(self):
        self.plan['bindings'][3]['writes']=['apps/web/']
        self.plan['bindings'][3]['phase']='verification'
        self.assertNotIn('output_overlap',self.codes())
    def test_unsafe_path_variants(self):
        for path in ['../secret','/etc/passwd','C:/private','a\\b','a/../b','a//b','CON.txt','a/\u202eb','x/*.ts']:
            with self.subTest(path=path):
                self.plan['bindings'][1]['writes']=[path]
                self.assertIn('unsafe_write_path',self.codes())
    def test_arabic_write_path(self):
        self.plan['bindings'][1]['writes']=['docs/\u062a\u0635\u0645\u064a\u0645.md']
        self.assertNotIn('unsafe_write_path',self.codes())
    def test_missing_required_owner(self):
        self.plan['bindings']=self.plan['bindings'][1:]
        self.assertIn('uncovered_slot',self.codes())
    def test_unresolved_activation_conflict(self):
        self.plan['activation_conflicts']=[{'source':'global-hook','status':'unresolved'}]
        self.assertIn('active_conflict',self.codes())
    def test_conflict_resolution_requires_evidence(self):
        self.plan['activation_conflicts']=[{'source':'global-hook','status':'isolated'}]
        self.assertIn('conflict_without_evidence',self.codes())
    def test_declared_conflict_evidence(self):
        self.plan['activation_conflicts']=[{'source':'global-hook','status':'isolated','evidence_ref':'EV-001'}]
        self.assertEqual(self.codes(),set())
    def test_draft_not_ready(self):
        self.assertTrue({'unresolved_source','stale_or_missing_approval'} <= self.codes(ready=True))
    def resolve(self):
        for x in self.plan['bindings']:
            x['resolved']={'pinned_ref':'fixture-revision-001','sha256':'a'*64,'license_reviewed':True,'scope_reviewed':True,'permissions_approved':True,'adapter_status':'tested'}
        self.plan['approval']={'confirmed_by_user':True,'plan_sha256':m.plan_digest(self.plan)}
    def test_ready_checks_declared_fields_only(self):
        self.resolve();self.assertEqual(self.codes(ready=True),set())
    def test_float_pin_rejected(self):
        self.resolve();self.plan['bindings'][0]['resolved']['pinned_ref']='main'
        self.assertIn('unpinned_source',self.codes(ready=True))
    def test_bad_digest(self):
        self.resolve();self.plan['bindings'][0]['resolved']['sha256']='a'
        self.assertIn('missing_digest',self.codes(ready=True))
    def test_false_and_integer_are_not_approval(self):
        self.resolve()
        for val in [False,1,'true',None]:
            with self.subTest(value=val):
                self.plan['bindings'][0]['resolved']['license_reviewed']=val
                self.assertIn('license_pending',self.codes(ready=True))
    def test_adapter_not_tested(self):
        self.resolve();self.plan['bindings'][8]['resolved']['adapter_status']='mocked'
        self.assertIn('adapter_unverified',self.codes(ready=True))
    def test_changed_plan_invalidates_approval(self):
        self.resolve();self.plan['bindings'][0]['scope_contract']='changed'
        self.assertIn('stale_or_missing_approval',self.codes(ready=True))
    def test_tool_not_policy_owner(self):
        self.plan['bindings'][8]['role']='primary'
        self.assertIn('tool_role',self.codes())
    def test_invalid_mode_type(self):
        self.plan['bindings'][0]['activation_mode']=[]
        self.assertIn('invalid_mode',self.codes())
    def test_bad_registry(self):
        r=copy.deepcopy(REG);del r['providers'][0]['kind']
        self.assertIn('invalid_registry',self.codes(reg=r))
    def test_bad_components(self):
        self.plan['components']['web']['tags']='react'
        self.assertIn('invalid_components',self.codes())
    def test_boolean_schema_not_integer(self):
        self.plan['schema_version']=True
        self.assertIn('invalid_plan',self.codes())
    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):m.load_json(p)
    def test_size_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_bytes(b' '*(m.MAX_BYTES+1))
            with self.assertRaises(ValueError):m.load_json(p)
    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"x":NaN}')
            with self.assertRaises(ValueError):m.load_json(p)
    def test_cli_ar_and_en_and_exit_codes(self):
        for lang,extra,expect in [('ar',[],0),('en',['--ready'],1)]:
            run=subprocess.run([sys.executable,str(ROOT/'scripts/check_selection.py'),str(ROOT/'assets/examples/web-selection.draft.json'),'--lang',lang,'--json']+extra,capture_output=True,text=True,check=False)
            self.assertEqual(run.returncode,expect,run.stderr)
            data=json.loads(run.stdout)
            self.assertIn('limitation',data)
    def test_cli_does_not_modify_input(self):
        p=ROOT/'assets/examples/web-selection.draft.json';before=p.read_bytes()
        subprocess.run([sys.executable,str(ROOT/'scripts/check_selection.py'),str(p)],capture_output=True,check=True)
        self.assertEqual(before,p.read_bytes())
    def test_catalog_integrity(self):
        sources={x['id'] for x in REG['providers']}
        self.assertEqual(len(sources),len(REG['providers']))
        for c in CAP['capabilities']:
            self.assertLessEqual(len(c['primary_candidates']),3)
            self.assertTrue(set(c['primary_candidates']+c['complements'])<=sources)
        for x in REG['providers']:
            self.assertIsNone(x['binding']['pinned_ref'])
            self.assertFalse(x['binding']['installed_by_this_delivery'])
    def test_locale_keys_match(self):
        locales=m.load_json(ROOT/'assets/validator_messages.json')
        self.assertEqual(set(locales['ar']),set(locales['en']))

if __name__=='__main__':unittest.main()
