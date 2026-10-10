"""Conversational new-web-project intake and approval boundary for Nasaq.

The host interprets conversation and applies upstream workflow instructions.
This module stores attributed facts/decisions, renders reviewable replies, and
delegates ALL planning-stage state to spec_kit_bridge. Single writer; no daemon.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import spec_kit_bridge as bridge
from check_selection import ROOT, load_json

FIELDS={'kind','idea','goals','features','roles','acceptance','excluded','constraints','competitors'}
REQUIRED=('kind','idea','features','roles','acceptance','excluded')
QUESTIONS={
 'kind':('هل المشروع جديد أم قائم؟','Is this a new or existing project?'),
 'idea':('ما الفكرة والهدف الذي يخدمه المشروع؟','What is the idea and the goal it serves?'),
 'features':('ما المميزات الأساسية المطلوبة؟ يمكنك إرسالها كلها معًا.','What core features do you need? You can send them together.'),
 'roles':('من المستخدمون، وما صلاحيات كل دور؟','Who are the users, and what can each role do?'),
 'acceptance':('كيف نعرف أن المميزات حققت المطلوب؟','How will we know the features meet your needs?'),
 'excluded':('ما الوظائف المستبعدة من النطاق الحالي؟','What is excluded from the current scope?'),
}
PERMISSIONS=['planning_documents','reviewed_source_scripts']
LABELS={'kind':'نوع المشروع','idea':'الفكرة','goals':'الأهداف','features':'المميزات','roles':'الأدوار',
        'acceptance':'معايير القبول','excluded':'خارج النطاق','constraints':'القيود','competitors':'المنافسون'}
STATUS_AR={'confirmed':'مؤكد','assumption':'افتراض','deferred':'مؤجل'}
ERROR_AR={'requirements_incomplete':'ما زالت معلومات أو أسئلة مؤثرة تحتاج استكمالًا.',
          'requirements_not_approved':'راجع ملخص المتطلبات واعتمده أولًا.',
          'selection_not_approved':'اختيار التقنيات والمصادر لم يُعتمد بعد.',
          'planning_not_approved':'نحتاج اعتماد نطاق التخطيط المحدد قبل تشغيله.',
          'prior_approval_missing':'اعتماد المتطلبات أو الاختيار الحالي غير مكتمل.',
          'stale_summary':'تغير الملخص؛ راجع النسخة الحالية قبل اعتمادها.',
          'stale_proposal':'تغير الترشيح؛ راجع النسخة الحالية قبل اختياره.',
          'delegation_exceeded':'الاختيار يتجاوز حدود التفويض المحفوظة.',
          'scope_exceeded':'الطلب يتجاوز نطاق التخطيط المحلي المعتمد.',
          'paused':'المسار متوقف؛ اطلب الاستئناف أولًا.',
          'unavailable_integration':'المصدر المختار غير قابل للتشغيل عبر هذا المسار الحالي.',
          'unsupported_or_out_of_scope_action':'هذا الإجراء غير منفذ أو خارج نطاق التخطيط الحالي.',
          'change_control_to_extend_limit':'وصلنا الحد المحدد؛ يلزم تغيير وضع التحكم لتمديده.'}

def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def tr(state,ar,en): return ar if state['language']=='ar' else en

def location(project): return project/'.nasaq'

def revision_hash(state):
    return fingerprint({'facts':state['facts'],'questions':state['questions']})

def approval_hash(state):
    return fingerprint({'requirements':revision_hash(state),'proposal':state['proposal'],
                        'source':state['source'],'permissions':PERMISSIONS})

def message_evidence(ev):
    if ev.get('origin') not in {'user','test_fixture'} or not ev.get('text','').strip():
        raise ValueError('user_message_required')
    return {'origin':ev['origin'],'text':ev['text'],'message_id':ev['id']}

def missing(state):
    keys=[k for k in REQUIRED if not state['facts'].get(k,{}).get('value') or state['facts'][k]['status']=='deferred']
    questions=[QUESTIONS[k][state['language']=='en'] for k in keys]
    return questions+[q['question'] for q in state['questions'] if q['blocking']]

def summarize(state):
    lines=[tr(state,'ملخص قابل للتعديل — لا تخطيط قبل الاعتماد','Editable summary — approval required before planning')]
    for key,fact in state['facts'].items():
        value=fact['value']
        label=LABELS[key] if state['language']=='ar' else key
        status=STATUS_AR[fact['status']] if state['language']=='ar' else fact['status']
        lines.append(f"{label} [{status}]: "+(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)))
    for q in state['questions']:
        lines.append(f"{'blocking' if q['blocking'] else 'deferred'}: {q['question']}")
    lines.append(tr(state,'يمكنك تعديل الملخص أو اعتماده ببصمته المعروضة.','You may revise or approve this exact summary.'))
    return '\n'.join(lines)

def source_config(evidence_run):
    state,lock=bridge.checked(evidence_run)
    if lock.get('commit')!=bridge.COMMIT or any(state['stages'][s]['status']!='completed' for s in bridge.STAGES):
        raise ValueError('source_evidence_incomplete')
    review=evidence_run/'evidence/source-review.json'
    return {'provider':'spec-kit','commit':lock['commit'],'upstream':lock['upstream'],
        'review':str(review.resolve()),'review_sha256':bridge.digest(review),
        'evidence_run':str(evidence_run.resolve()),'mode':'workflow-reference',
        'tested_scope':'one planning fixture on Windows, ar/en; no native host integration'}

def readiness(state,pid):
    registry={p['id']:p for p in load_json(ROOT/'assets/providers.json')['providers']}
    if pid not in registry: raise ValueError('unknown_source')
    if pid=='spec-kit':
        return {'status':state['source'].get('readiness_status','tested_scoped'),'runnable_here':True,'scope':state['source']['tested_scope'],'mode':'workflow-reference'}
    return {'status':'catalog_only','runnable_here':False,'scope':registry[pid]['limitations_ar'],
            'review_level':registry[pid].get('review',{}).get('level','not_reviewed'),
            'review_note':'Catalog/documentation review is not a pinned executable integration review.'}

def validate_proposal(state,proposal):
    if not isinstance(proposal,dict) or set(proposal)!={'architecture','technologies','sources','rationale','costs','permissions','deferred'}:
        raise ValueError('invalid_proposal')
    for key in ['architecture','rationale','costs']:
        if not isinstance(proposal[key],str) or not proposal[key].strip(): raise ValueError('invalid_proposal')
    if not isinstance(proposal['technologies'],list) or not proposal['technologies'] or not all(isinstance(t,str) and t for t in proposal['technologies']):
        raise ValueError('invalid_technologies')
    if proposal['permissions']!=PERMISSIONS or not isinstance(proposal['deferred'],list):
        raise ValueError('scope_exceeded')
    sources=proposal['sources']
    if not isinstance(sources,list) or not sources: raise ValueError('invalid_sources')
    planning=[]
    for source in sources:
        if not isinstance(source,dict) or set(source)!={'id','purpose','use'} or source['use'] not in {'planning','candidate'}:
            raise ValueError('invalid_sources')
        readiness(state,source['id'])
        if source['use']=='planning': planning.append(source['id'])
    if len({s['id'] for s in sources})!=len(sources) or len(planning)!=1:
        raise ValueError('conflicting_planning_sources')

def check_delegation(state,proposal):
    limits=state['delegation']['limits']
    if any(t not in limits['allowed_technologies'] for t in proposal['technologies']):
        raise ValueError('delegation_exceeded')
    if any(s['id'] not in limits['allowed_sources'] for s in proposal['sources']):
        raise ValueError('delegation_exceeded')

def planning_ready(state):
    rh=revision_hash(state)
    if state['requirements_approval'].get('digest')!=rh: raise ValueError('requirements_not_approved')
    if not state['proposal'] or state['selection_approval'].get('digest')!=fingerprint(state['proposal']):
        raise ValueError('selection_not_approved')
    if state['planning_approval'].get('digest')!=approval_hash(state): raise ValueError('planning_not_approved')
    planning=[s['id'] for s in state['proposal']['sources'] if s['use']=='planning']
    if planning!=['spec-kit']: raise ValueError('unavailable_integration')
    if bridge.digest(Path(state['source']['review']))!=state['source']['review_sha256']:
        raise ValueError('source_review_changed')

def get_run(project,state):
    return bridge.inside(location(project),state['active_run']) if state['active_run'] else None

def completed_count(project,state):
    run=get_run(project,state)
    if not run: return 0
    rs,_=bridge.checked(run)
    return sum(s['status']=='completed' for s in rs['stages'].values())

def checkpoint(state,count):
    mode=state['control']['mode']
    if mode=='all': return False
    if mode=='until': return count>=state['control']['stage']
    interval=1 if mode=='each' else state['control']['count']
    return count-state['acknowledged']>=interval

def invalidate(state):
    state['requirements_approval']={}; state['selection_approval']={}; state['planning_approval']={}
    state['proposal']=None
    if state['active_run']:
        state['retained_runs'].append({'path':state['active_run'],'reason':'requirements changed; retained, not current evidence'})
        state['active_run']=None
    state['acknowledged']=0

def apply_action(project,state,ev):
    action=ev['action']; data=ev.get('data',{})
    if action=='intake':
        message_evidence(ev)
        facts=data.get('facts',{})
        if not isinstance(facts,dict) or not set(facts).issubset(FIELDS): raise ValueError('invalid_facts')
        before=revision_hash(state)
        for key,fact in facts.items():
            if not isinstance(fact,dict) or set(fact)!={'value','status'} or fact['status'] not in {'confirmed','assumption','deferred'}:
                raise ValueError('invalid_fact')
            old=state['facts'].get(key,{})
            if old.get('value')!=fact['value'] or old.get('status')!=fact['status']:
                state['facts'][key]=dict(fact,message_id=ev['id'])
        if 'questions' in data:
            if not isinstance(data['questions'],list): raise ValueError('invalid_questions')
            for q in data['questions']:
                if not isinstance(q,dict) or set(q)!={'id','question','blocking'} or not isinstance(q['question'],str) or type(q['blocking']) is not bool:
                    raise ValueError('invalid_questions')
            state['questions']=data['questions']
        if before!=revision_hash(state):
            invalidate(state); state['revision']+=1
        if state['facts'].get('kind',{}).get('value')=='existing':
            return {'reply':tr(state,'المشروع قائم: انتقل لفحص الملفات قراءةً فقط؛ المسار التنفيذي الحالي للمشروع الجديد.','Existing project: route to read-only audit; this executable slice handles new projects.'),'blocked':'existing_project_audit_required'}
        qs=missing(state)
        return {'reply':qs[0] if qs else summarize(state),'questions':qs,'summary_digest':revision_hash(state)}
    if action=='summary':
        return {'reply':summarize(state),'summary_digest':revision_hash(state),'questions':missing(state)}
    if action=='approve_requirements':
        evidence=message_evidence(ev)
        if missing(state) or state['facts']['kind']['value']!='new': raise ValueError('requirements_incomplete')
        if data.get('digest')!=revision_hash(state): raise ValueError('stale_summary')
        state['requirements_approval']={'digest':revision_hash(state),'evidence':evidence}
        return {'reply':tr(state,'اعتمدت المتطلبات. اختر التقنيات بنفسك، أو راجع ترشيح نَسَق، أو فوّض اختيارًا مقيدًا.','Requirements approved. Choose your stack, review a recommendation, or delegate within explicit limits.')}
    if action=='propose':
        if state['requirements_approval'].get('digest')!=revision_hash(state): raise ValueError('requirements_not_approved')
        proposal=data.get('proposal'); validate_proposal(state,proposal)
        if state['proposal']!=proposal:
            state['proposal']=proposal; state['selection_approval']={}; state['planning_approval']={}
            if state['active_run']:
                state['retained_runs'].append({'path':state['active_run'],'reason':'selection changed'})
                state['active_run']=None; state['acknowledged']=0
        choices=[dict(s,readiness=readiness(state,s['id'])) for s in proposal['sources']]
        return {'reply':tr(state,'ترشيح للمراجعة؛ لا تشغيل قبل اختيارك واعتماد نطاق التخطيط.','Recommendation for review; selection and planning-scope approval are still required.'),
                'proposal':proposal,'sources':choices,'proposal_digest':fingerprint(proposal)}
    if action=='delegate':
        evidence=message_evidence(ev); limits=data.get('limits',{})
        if set(limits)!={'allowed_sources','allowed_technologies','permissions'} or limits['permissions']!=PERMISSIONS:
            raise ValueError('delegation_scope_invalid')
        if not all(isinstance(limits[k],list) and limits[k] and all(isinstance(x,str) and x for x in limits[k]) for k in ['allowed_sources','allowed_technologies']):
            raise ValueError('delegation_scope_invalid')
        state['delegation']={'limits':limits,'evidence':evidence}
        if state['selection_approval'].get('mode')=='delegated':
            state['selection_approval']={}; state['planning_approval']={}
        return {'reply':tr(state,'حُفظ تفويض الاختيار فقط؛ اعتماد نطاق تشغيل التخطيط ما زال مطلوبًا.','Selection delegation saved; planning execution still needs its own scope approval.')}
    if action=='select':
        choice=data.get('choice')
        if choice=='reject':
            message_evidence(ev); state['selection_approval']={}; state['planning_approval']={}
            return {'reply':tr(state,'رُفض الترشيح. سنراجع البدائل ضمن احتياجاتك.','Recommendation rejected. We will revise alternatives within your needs.')}
        if choice not in {'manual','accept','delegated'} or not state['proposal']: raise ValueError('invalid_selection')
        if data.get('digest')!=fingerprint(state['proposal']): raise ValueError('stale_proposal')
        if choice=='delegated':
            if not state['delegation']: raise ValueError('delegation_missing')
            check_delegation(state,state['proposal']); evidence=state['delegation']['evidence']
        else: evidence=message_evidence(ev)
        state['selection_approval']={'digest':fingerprint(state['proposal']),'mode':choice,'evidence':evidence}
        return {'reply':tr(state,'حُفظ الاختيار. اعتمد النطاق: وثائق التخطيط وسكربتات المصدر المراجعة فقط.','Selection saved. Approve scope: planning documents and reviewed source scripts only.'),'planning_digest':approval_hash(state)}
    if action=='approve_planning':
        evidence=message_evidence(ev)
        if state['requirements_approval'].get('digest')!=revision_hash(state) or not state['proposal'] or state['selection_approval'].get('digest')!=fingerprint(state['proposal']):
            raise ValueError('prior_approval_missing')
        if data.get('digest')!=approval_hash(state) or data.get('permissions')!=PERMISSIONS: raise ValueError('scope_exceeded')
        state['planning_approval']={'digest':approval_hash(state),'permissions':PERMISSIONS,'evidence':evidence}
        return {'reply':tr(state,'اعتمد نطاق التخطيط المحلي فقط.','Local planning scope approved only.')}
    if action=='control':
        evidence=message_evidence(ev); mode=data.get('mode')
        if mode not in {'each','until','every','all'}: raise ValueError('invalid_control')
        if mode=='until' and (type(data.get('stage')) is not int or not 1<=data['stage']<=len(bridge.STAGES)): raise ValueError('invalid_control')
        if mode=='every' and (type(data.get('count')) is not int or data['count']<1): raise ValueError('invalid_control')
        state['control']={**data,'evidence':evidence}; state['acknowledged']=completed_count(project,state)
        return {'reply':tr(state,'حُفظ وضع التحكم لمراحل التخطيط الست فقط؛ لا تشغيل في الخلفية بعد انتهاء الجلسة.','Control saved for the six planning stages only; no background execution after the session ends.')}
    if action=='continue':
        message_evidence(ev); state['acknowledged']=completed_count(project,state)
        if state['control']['mode']=='until' and state['acknowledged']>=state['control']['stage']:
            raise ValueError('change_control_to_extend_limit')
        return {'reply':tr(state,'سُجلت مراجعة نقطة التوقف.','Checkpoint review recorded.')}
    if action=='pause':
        message_evidence(ev); state['paused']=True
        return {'reply':tr(state,'توقف المسار وحُفظت حالته. لا أعمال خلفية.','Paused with state saved. No background work.')}
    if action=='resume':
        message_evidence(ev)
        run=get_run(project,state)
        if run: bridge.checked(run)
        state['paused']=False
        return {'reply':tr(state,'قُرئت الحالة وتحققت البصمات؛ الاستئناف يحترم الموافقات ونقاط المراجعة.','State loaded and hashes checked; approvals and checkpoints still apply.')}
    if action=='advance':
        planning_ready(state)
        if state['paused']: raise ValueError('paused')
        run=get_run(project,state)
        if not run:
            name=f'runs/revision-{state["revision"]}-{len(state["retained_runs"])+1}'
            run=bridge.inside(location(project),name)
            request=summarize(state)+'\n\nApproved selection:\n'+json.dumps(state['proposal'],ensure_ascii=False,indent=2)
            bridge.initialize(run,Path(state['source']['upstream']),request,state['language'],Path(state['source']['review']),feature_id='001-project')
            state['active_run']=name
            # Persist the run pointer before any source script can fail or the
            # host can disappear; the bridge owns recovery of its stage state.
            bridge.write_json(location(project)/'project.json',state)
        rs,_=bridge.checked(run)
        count=sum(s['status']=='completed' for s in rs['stages'].values())
        if count==len(bridge.STAGES):
            return {'reply':tr(state,'اكتمل التخطيط؛ التطبيق لم يُبنَ.','Planning complete; no application built.'),'complete':True,'run':str(run),
                    'artifacts':{k:v['output_hashes'] for k,v in rs['stages'].items()}}
        if checkpoint(state,count):
            return {'reply':tr(state,'وصلنا نقطة المراجعة المحددة. راجع المخرجات قبل الاستمرار.','Reached your review checkpoint. Review outputs before continuing.'),'checkpoint':True,'completed_stages':count}
        current=next(s for s in bridge.STAGES if rs['stages'][s]['status']!='completed')
        if rs['stages'][current]['status']=='running':
            packet_path=run/f'evidence/{current}-handoff.json'
            if not packet_path.exists(): raise ValueError('partial_stage_recovery_required')
            packet=load_json(packet_path)
            if packet['instructions']!=(Path(state['source']['upstream'])/f'templates/commands/{current}.md').read_text(encoding='utf-8'):
                raise ValueError('handoff_modified')
            return {'reply':tr(state,'استعادة تسليم المرحلة المفتوحة دون إعادة سكربت المصدر.','Restored the open handoff without rerunning its source script.'),'handoff':packet,'run':str(run),'resumed_handoff':True}
        if rs['stages'][current]['status']=='failed': raise ValueError('source_stage_failed')
        return {'reply':tr(state,'يطبق الوكيل الآن تعليمات المصدر الأصلية.','The host now applies original source instructions.'),'handoff':bridge.begin(run,current),'run':str(run)}
    if action=='submit':
        planning_ready(state)
        if state['paused']: raise ValueError('paused')
        run=get_run(project,state)
        if not run: raise ValueError('no_run')
        bridge.submit_outputs(run,data['stage'],data['contents'],data['note'])
        return {'reply':tr(state,'حُفظ مخرج المرحلة وأدلته؛ ليس شهادة جودة مستقلة.','Stage output and evidence saved; not independent quality certification.'),'completed_stages':completed_count(project,state)}
    if action=='language':
        message_evidence(ev)
        if data.get('language') not in {'ar','en'}: raise ValueError('invalid_language')
        state['language']=data['language']
        return {'reply':tr(state,'العرض بالعربية؛ لا تتغير الموافقات أو لغة المخرجات السابقة.','Display switched to English; approvals and prior artifact language remain unchanged.')}
    if action=='status':
        run=get_run(project,state)
        rs=bridge.checked(run)[0] if run else None
        return {'reply':tr(state,'حالة المشروع الحالية','Current project status'),'revision':state['revision'],
            'paused':state['paused'],'requirements_approved':state['requirements_approval'].get('digest')==revision_hash(state),
            'selection_approved':bool(state['selection_approval']),'planning_approved':bool(state['planning_approval']),
            'stage_state':rs,'run':str(run) if run else None,'control':state['control'],'retained_runs':state['retained_runs']}
    raise ValueError('unsupported_or_out_of_scope_action')

def dispatch(project,ev):
    project=project.resolve(); meta=location(project)
    if not isinstance(ev,dict) or not all(isinstance(ev.get(k),str) and ev[k] for k in ['id','action']):
        raise ValueError('invalid_event')
    if not ev['id'].isascii() or not ev['id'].replace('-','').replace('_','').isalnum(): raise ValueError('invalid_event_id')
    if ev['action']=='start':
        message_evidence(ev)
        if (meta/'project.json').exists(): raise ValueError('project_already_started')
        if ev['data'].get('source_configuration'):
            from nasaq_core.sources import checked_configuration
            source=checked_configuration(Path(ev['data']['source_configuration']).resolve())
        else:
            # Historical pilot path retained for old clients/evidence. New
            # installation uses a reviewed configuration, never a required pilot.
            source=source_config(Path(ev['data']['source_evidence_run']).resolve())
        lang=ev['data'].get('language','ar')
        if lang not in {'ar','en'}: raise ValueError('invalid_language')
        state={'schema_version':1,'language':lang,'revision':0,'facts':{},'questions':[],
            'requirements_approval':{},'selection_approval':{},'planning_approval':{},'proposal':None,'delegation':{},
            'control':{'mode':'each'},'acknowledged':0,'paused':False,'active_run':None,'retained_runs':[],
            'source':source,'event_ids':[],'transcript':[]}
        meta.mkdir(parents=True,exist_ok=True)
        response={'reply':tr(state,'هل المشروع جديد أم قائم؟ أرسل التفاصيل كلها أو نستكمل سؤالًا بسؤال.','Is this a new or existing project? Send all details together or we can go question by question.')}
        if ev['data'].get('facts'):
            response=apply_action(project,state,{**ev,'action':'intake','data':{'facts':ev['data']['facts'],'questions':ev['data'].get('questions',[])}})
    else:
        state=load_json(meta/'project.json')
        if ev['id'] in state['event_ids']: raise ValueError('duplicate_event_id')
        state=copy.deepcopy(state)
        try: response=apply_action(project,state,ev)
        except (ValueError,KeyError,OSError) as exc:
            bridge.event(meta,'request_rejected',action_requested=ev['action'],message_id=ev['id'],reason=str(exc))
            return {'ok':False,'error':str(exc),'reply':tr(state,ERROR_AR.get(str(exc),'تعذر تنفيذ الطلب؛ يلزم مراجعة المدخلات أو دليل المرحلة.'),'Request not executed: '+str(exc))}
    state['event_ids'].append(ev['id'])
    public={k:v for k,v in response.items() if k not in {'handoff','stage_state'}}
    state['transcript'].append({'id':ev['id'],'origin':ev.get('origin','host'),'action':ev['action'],'text':ev.get('text',''),
        'data_digest':fingerprint(ev.get('data',{})),'response':public})
    bridge.write_json(meta/'project.json',state)
    bridge.event(meta,'conversation_action',message_id=ev['id'],action_requested=ev['action'],revision=state['revision'])
    return {'ok':True,**response}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',required=True,type=Path); p.add_argument('--event',required=True,type=Path)
    args=p.parse_args()
    try: result=dispatch(args.project,load_json(args.event))
    except (ValueError,KeyError,OSError) as exc: result={'ok':False,'error':str(exc)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
