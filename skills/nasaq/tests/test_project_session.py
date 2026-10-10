"""Synthetic conversation inputs exercise real session code; no provider runs here."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import project_session as s
import spec_kit_bridge as b

def facts():
    return {k:{'value':v,'status':'confirmed'} for k,v in {
        'kind':'new','idea':'Studio directory','features':['List studios','Filter city'],
        'roles':['Visitor'],'acceptance':['Only matching cities appear'],'excluded':['Bookings','Payments']}.items()}

def proposal():
    return {'architecture':'Small read-only web app','technologies':['HTML','Python'],
        'sources':[{'id':'spec-kit','purpose':'Plan only','use':'planning'},
                   {'id':'impeccable','purpose':'Future design candidate','use':'candidate'}],
        'rationale':'Read-only directory requires no scheduling service','costs':'Local planning only',
        'permissions':s.PERMISSIONS,'deferred':['Production hosting']}

class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name)/'project'; self.counter=0
        review=Path(self.tmp.name)/'review.json'; review.write_text('{}')
        self.source={'provider':'spec-kit','commit':b.COMMIT,'upstream':str(Path(self.tmp.name)/'source'),
                     'review':str(review),'review_sha256':b.digest(review),'tested_scope':'synthetic evidence, not live',
                     'mode':'workflow-reference'}
        self.source_patch=patch.object(s,'source_config',return_value=self.source)
        self.source_patch.start(); self.addCleanup(self.source_patch.stop)
    def call(self,action,data=None,text='fixture user message',origin='test_fixture'):
        self.counter+=1
        return s.dispatch(self.project,{'id':f'm{self.counter}','action':action,'origin':origin,'text':text,'data':data or {}})
    def start(self,lang='en',f=None):
        return self.call('start',{'language':lang,'source_evidence_run':'unused synthetic path','facts':f or {}})
    def approve_facts(self):
        summary=self.call('summary')
        return self.call('approve_requirements',{'digest':summary['summary_digest']})
    def selected(self):
        self.start(f=facts()); self.approve_facts()
        p=self.call('propose',{'proposal':proposal()})
        return self.call('select',{'choice':'accept','digest':p['proposal_digest']})
    def approved(self):
        picked=self.selected()
        return self.call('approve_planning',{'digest':picked['planning_digest'],'permissions':s.PERMISSIONS})
    def test_arabic_and_english_start_ask_missing_only(self):
        out=self.start('ar',{'kind':{'value':'new','status':'confirmed'},'idea':{'value':'دليل استوديوهات','status':'confirmed'}})
        self.assertIn('المميزات',out['reply']); self.assertNotIn('جديد أم قائم',out['reply'])
        self.call('language',{'language':'en'})
        out=self.call('intake',{'facts':{}})
        self.assertIn('features',out['reply'])
    def test_all_features_at_once_are_preserved(self):
        self.start(f=facts()); self.assertTrue(self.approve_facts()['ok'])
        state=json.loads((self.project/'.nasaq/project.json').read_text())
        self.assertEqual(facts()['features']['value'],state['facts']['features']['value'])
    def test_blocking_question_prevents_approval(self):
        self.start(f=facts())
        self.call('intake',{'questions':[{'id':'privacy','question':'Public or private directory?','blocking':True}]})
        self.assertEqual('requirements_incomplete',self.approve_facts()['error'])
        self.call('intake',{'facts':{'constraints':{'value':'Public directory','status':'confirmed'}},'questions':[]})
        self.assertTrue(self.approve_facts()['ok'])
    def test_revised_summary_rejects_stale_digest(self):
        old=self.start(f=facts())
        self.call('intake',{'facts':{'features':{'value':['List studios'],'status':'confirmed'}}})
        self.assertEqual('stale_summary',self.call('approve_requirements',{'digest':old['summary_digest']})['error'])
    def test_assumptions_and_deferred_distinct(self):
        f=facts(); f['constraints']={'value':'Small catalog','status':'assumption'}
        f['competitors']={'value':'No competitor research requested','status':'deferred'}
        out=self.start(f=f)
        self.assertIn('[assumption]',out['reply']); self.assertIn('[deferred]',out['reply'])
    def test_unapproved_advance_never_calls_bridge(self):
        self.start(f=facts())
        with patch.object(b,'initialize') as init:
            self.assertEqual('requirements_not_approved',self.call('advance')['error'])
            init.assert_not_called()
    def test_selection_is_not_execution_approval(self):
        self.selected()
        with patch.object(b,'initialize') as init:
            self.assertEqual('planning_not_approved',self.call('advance')['error']); init.assert_not_called()
    def test_rejected_recommendation_blocks_planning(self):
        picked=self.selected(); self.call('select',{'choice':'reject'})
        self.assertEqual('prior_approval_missing',self.call('approve_planning',{'digest':picked['planning_digest'],'permissions':s.PERMISSIONS})['error'])
    def test_manual_choice_supported(self):
        self.start(f=facts()); self.approve_facts()
        p=self.call('propose',{'proposal':proposal()})
        self.assertTrue(self.call('select',{'choice':'manual','digest':p['proposal_digest']})['ok'])
    def test_recommendation_status_does_not_promote_candidates(self):
        self.start(f=facts()); self.approve_facts(); p=self.call('propose',{'proposal':proposal()})
        self.assertEqual('tested_scoped',p['sources'][0]['readiness']['status'])
        self.assertFalse(p['sources'][1]['readiness']['runnable_here'])
    def test_delegated_choice_is_bounded(self):
        self.start(f=facts()); self.approve_facts()
        limits={'allowed_sources':['spec-kit'],'allowed_technologies':['HTML'],'permissions':s.PERMISSIONS}
        self.call('delegate',{'limits':limits})
        p=self.call('propose',{'proposal':proposal()})
        self.assertEqual('delegation_exceeded',self.call('select',{'choice':'delegated','digest':p['proposal_digest']},origin='host')['error'])
        bounded=proposal(); bounded['sources']=bounded['sources'][:1]; bounded['technologies']=['HTML']
        p=self.call('propose',{'proposal':bounded})
        self.assertTrue(self.call('select',{'choice':'delegated','digest':p['proposal_digest']},origin='host')['ok'])
    def test_source_alternative_can_be_reviewed_but_not_run(self):
        self.start(f=facts()); self.approve_facts()
        p=proposal(); p['sources'][0]['id']='openspec'
        candidate=self.call('propose',{'proposal':p})
        chosen=self.call('select',{'choice':'manual','digest':candidate['proposal_digest']})
        self.call('approve_planning',{'digest':chosen['planning_digest'],'permissions':s.PERMISSIONS})
        self.assertEqual('unavailable_integration',self.call('advance')['error'])
    def test_influential_revision_invalidates_only_current_planning(self):
        self.approved()
        self.call('intake',{'facts':{'features':{'value':['List','Filter','View details'],'status':'confirmed'}}})
        self.assertFalse(self.call('status')['requirements_approved'])
        self.assertEqual('requirements_not_approved',self.call('advance')['error'])
    def test_same_answers_and_language_do_not_revoke_approval(self):
        self.approved(); self.call('intake',{'facts':facts()}); self.call('language',{'language':'ar'})
        status=self.call('status'); self.assertTrue(status['requirements_approved']); self.assertTrue(status['planning_approved'])
    def test_same_proposal_keeps_existing_approval(self):
        self.approved(); self.call('propose',{'proposal':proposal()})
        self.assertTrue(self.call('status')['planning_approved'])
    def test_technology_revision_keeps_requirements_but_revokes_selection(self):
        self.approved()
        changed=proposal(); changed['technologies']=['HTML','CSS','JavaScript']
        self.call('propose',{'proposal':changed})
        status=self.call('status')
        self.assertTrue(status['requirements_approved'])
        self.assertFalse(status['selection_approved']); self.assertFalse(status['planning_approved'])
    def test_changed_delegation_revokes_delegated_selection(self):
        self.start(f=facts()); self.approve_facts()
        limits={'allowed_sources':['spec-kit','impeccable'],'allowed_technologies':['HTML','Python'],'permissions':s.PERMISSIONS}
        self.call('delegate',{'limits':limits})
        p=self.call('propose',{'proposal':proposal()})
        chosen=self.call('select',{'choice':'delegated','digest':p['proposal_digest']},origin='host')
        self.call('approve_planning',{'digest':chosen['planning_digest'],'permissions':s.PERMISSIONS})
        limits['allowed_sources']=['spec-kit']
        self.call('delegate',{'limits':limits})
        self.assertFalse(self.call('status')['selection_approved'])
        self.assertFalse(self.call('status')['planning_approved'])
    def test_host_cannot_invent_approval(self):
        self.start(f=facts()); summary=self.call('summary')
        self.assertEqual('user_message_required',self.call('approve_requirements',{'digest':summary['summary_digest']},origin='host')['error'])
    def test_high_risk_actions_rejected_even_with_all_mode(self):
        self.approved(); self.call('control',{'mode':'all'})
        for action in ['publish','install','delete_production','implement','android']:
            self.assertEqual('unsupported_or_out_of_scope_action',self.call(action)['error'])
    def test_scope_cannot_be_widened_in_approval(self):
        picked=self.selected()
        self.assertEqual('scope_exceeded',self.call('approve_planning',{'digest':picked['planning_digest'],'permissions':s.PERMISSIONS+['publish']})['error'])
    def test_modes_and_boundaries(self):
        self.start()
        for mode,params,expected in [('each',{},True),('every',{'count':3},False),('until',{'stage':5},False),('all',{},False)]:
            self.assertTrue(self.call('control',{'mode':mode,**params})['ok'])
            state=json.loads((self.project/'.nasaq/project.json').read_text())
            self.assertEqual(expected,s.checkpoint(state,1))
        self.assertFalse(self.call('control',{'mode':'until','stage':7})['ok'])
    def test_persistent_pause_blocks_execution_until_resume(self):
        self.approved(); self.call('pause')
        self.assertEqual('paused',self.call('advance')['error'])
        self.assertTrue(self.call('resume')['ok']); self.assertFalse(self.call('status')['paused'])
    def test_existing_project_routes_to_read_only_audit(self):
        f=facts(); f['kind']['value']='existing'
        out=self.start(f=f); self.assertEqual('existing_project_audit_required',out['blocked'])
        self.assertFalse(self.approve_facts()['ok'])
    def test_resume_reads_persisted_state_in_new_dispatch(self):
        self.approved()
        out=s.dispatch(self.project,{'id':'new-process','action':'status','text':'','data':{}})
        self.assertTrue(out['planning_approved']); self.assertEqual(1,out['revision'])
    def test_duplicate_messages_not_reapplied(self):
        self.start()
        ev={'id':'duplicate','action':'language','origin':'test_fixture','text':'English','data':{'language':'en'}}
        s.dispatch(self.project,ev)
        with self.assertRaisesRegex(ValueError,'duplicate'): s.dispatch(self.project,ev)

if __name__=='__main__': unittest.main()
