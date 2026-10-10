"""Nasaq's local, single-writer workflow-reference bridge. No content generator.

The host reads upstream instructions and authors artifacts; this helper routes
reviewed scripts, records handoffs, and checks integrity on resume. It is not a
sandbox or independent proof that the host followed the instructions.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

from check_selection import ROOT, load_json, validate_selection

COMMIT = '959e866caa3618bf3dc290d5dca33394365af9c6'
STAGES = ('constitution', 'specify', 'clarify', 'plan', 'tasks', 'analyze')
FEATURE = 'specs/001-booking'
OUTPUTS = {
    'constitution': ['.specify/memory/constitution.md'],
    'specify': [f'{FEATURE}/spec.md', f'{FEATURE}/checklists/requirements.md'],
    'clarify': ['evidence/clarification.md'],
    'plan': [f'{FEATURE}/{p}' for p in ['plan.md','research.md','data-model.md','quickstart.md','contracts/booking.md']],
    'tasks': [f'{FEATURE}/tasks.md'],
    'analyze': ['evidence/analysis.md'],
}
SCRIPTS = {
    'constitution': ['resolve-template.ps1','constitution-template','-Json'],
    'specify': ['resolve-template.ps1','spec-template','-Json'],
    'clarify': ['check-prerequisites.ps1','-Json','-PathsOnly'],
    'plan': ['setup-plan.ps1','-Json'],
    'tasks': ['setup-tasks.ps1','-Json'],
    'analyze': ['check-prerequisites.ps1','-Json','-RequireSpec','-RequireTasks','-IncludeTasks'],
}
TEMPLATES = ('constitution','spec','plan','tasks','checklist')
SOURCE_FILES = (['LICENSE'] + [f'templates/commands/{s}.md' for s in STAGES]
    + [f'templates/{t}-template.md' for t in TEMPLATES]
    + [f'scripts/powershell/{s}' for s in ['common.ps1','resolve-template.ps1','setup-plan.ps1','setup-tasks.ps1','check-prerequisites.ps1']])

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError('path escapes run')
    return path

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    tmp.replace(path)

def event(run, action, **details):
    with (run/'events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(dict(time=datetime.now(timezone.utc).isoformat(), action=action, **details),ensure_ascii=False)+'\n')

def stage_outputs(state, stage):
    feature = state.get('feature', FEATURE)
    return [p.replace(FEATURE, feature).replace('contracts/booking.md',
            'contracts/feature.md' if feature != FEATURE else 'contracts/booking.md') for p in OUTPUTS[stage]]

def initialize(run, upstream, request, lang, review, feature_id='001-booking'):
    if lang not in {'ar','en'} or run.exists():
        raise ValueError('language invalid or run already exists')
    if not isinstance(feature_id,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',feature_id):
        raise ValueError('invalid feature identifier')
    feature='specs/'+feature_id
    head = subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'],text=True).strip()
    origin = subprocess.check_output(['git','-C',str(upstream),'remote','get-url','origin'],text=True).strip()
    if head != COMMIT or origin != 'https://github.com/github/spec-kit.git':
        raise ValueError('source identity mismatch')
    if subprocess.check_output(['git','-C',str(upstream),'status','--porcelain'],text=True).strip():
        raise ValueError('source checkout modified')
    reviewed = load_json(review)
    hashes = {p: digest(inside(upstream,p)) for p in SOURCE_FILES}
    if reviewed.get('commit') != COMMIT or reviewed.get('files') != hashes:
        raise ValueError('review does not match exact source bytes')
    selection = {'schema_version':1,'components':{'web':{'tags':['web']}},
        'required_slots':[], 'activation_conflicts':[], 'bindings':[{
        'id':'planning','provider':'spec-kit','capability':'process.specification','component':'web',
        'phase':'planning','role':'primary','writes':['specs','.specify/memory'],
        'scope_contract':'Planning documents only in isolated run; no application execution',
        'activation_mode':'workflow-reference'}]}
    issues=validate_selection(selection,load_json(ROOT/'assets/providers.json'),load_json(ROOT/'assets/capabilities.json'))
    if issues:
        raise ValueError(str(issues))
    run.mkdir(parents=True)
    for folder in ['evidence','.specify/templates','.specify/memory',feature]:
        (run/folder).mkdir(parents=True,exist_ok=True)
    (run/'request.md').write_text(request,encoding='utf-8')
    shutil.copyfile(review,run/'evidence/source-review.json')
    for template in TEMPLATES:
        shutil.copyfile(upstream/f'templates/{template}-template.md',run/f'.specify/templates/{template}-template.md')
    write_json(run/'.specify/feature.json',{'feature_directory':feature})
    write_json(run/'selection.json',selection)
    write_json(run/'source-lock.json',{'commit':head,'origin':origin,'upstream':str(upstream.resolve()),'files':hashes})
    state={'schema_version':1,'run_id':run.name,'language':lang,'mode':'workflow-reference','feature':feature,
        'request_sha256':digest(run/'request.md'),'source_lock_sha256':digest(run/'source-lock.json'),
        'selection_sha256':digest(run/'selection.json'),'paused':False,
        'stages':{s:{'status':'pending'} for s in STAGES}}
    write_json(run/'run.json',state)
    event(run,'nasaq_request_routed',mode=state['mode'],request_sha256=state['request_sha256'])

def checked(run):
    state=load_json(run/'run.json'); lock=load_json(run/'source-lock.json')
    for filename,key in [('request.md','request_sha256'),('source-lock.json','source_lock_sha256'),('selection.json','selection_sha256')]:
        if digest(run/filename)!=state[key]:
            raise ValueError(f'changed input: {filename}; explicit replanning required')
    for name,value in lock['files'].items():
        if digest(inside(Path(lock['upstream']),name))!=value:
            raise ValueError('changed upstream file: '+name)
    for t in TEMPLATES:
        if digest(inside(run,f'.specify/templates/{t}-template.md'))!=lock['files'][f'templates/{t}-template.md']:
            raise ValueError('changed template copy')
    if (run/'.specify/extensions.yml').exists() or (run/'.specify/presets').exists() or (run/'.specify/extensions').exists():
        raise ValueError('unreviewed extension/preset configuration')
    for stage in state['stages'].values():
        if stage['status']=='completed':
            for name,value in stage['output_hashes'].items():
                if digest(inside(run,name))!=value:
                    raise ValueError('changed completed output: '+name)
    return state,lock

def begin(run, stage):
    if stage not in STAGES:
        raise ValueError('unsupported stage')
    state,lock=checked(run)
    if state['paused'] or state['stages'][stage]['status']!='pending':
        raise ValueError('stage not pending or run paused')
    if any(state['stages'][s]['status']!='completed' for s in STAGES[:STAGES.index(stage)]):
        raise ValueError('prerequisite stage incomplete')
    instruction=Path(lock['upstream'])/f'templates/commands/{stage}.md'
    inputs={p:h for s in state['stages'].values() for p,h in s.get('output_hashes',{}).items()}
    state['stages'][stage]={'status':'running','input_hashes':inputs,'instruction_sha256':digest(instruction)}
    write_json(run/'run.json',state)
    event(run,'stage_started',stage=stage,instruction=str(instruction),sha256=digest(instruction))
    env=os.environ.copy()
    env.update(SPECIFY_INIT_DIR=str(run.resolve()),SPECIFY_FEATURE_DIRECTORY=state.get('feature',FEATURE),
               SPECIFY_FEATURE_NO_PERSIST='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',
               TEMP=str(run/'evidence'),TMP=str(run/'evidence'))
    command=['pwsh','-NoProfile','-File',str(Path(lock['upstream'])/'scripts/powershell'/SCRIPTS[stage][0]),*SCRIPTS[stage][1:]]
    result=subprocess.run(command,cwd=run,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60)
    write_json(run/f'evidence/{stage}-script.json',{'command':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode:
        state['stages'][stage]['status']='failed'; write_json(run/'run.json',state)
        event(run,'stage_failed',stage=stage)
        raise ValueError('upstream script failed; inspect evidence')
    parsed=json.loads(result.stdout)
    if stage=='specify':
        (run/state.get('feature',FEATURE)/'spec.md').write_text(parsed['TEMPLATE_CONTENT'],encoding='utf-8')
    packet={'stage':stage,'language':state['language'],'mode':'workflow-reference',
        'request':(run/'request.md').read_text(encoding='utf-8'), 'instruction_path':str(instruction),
        'instructions':instruction.read_text(encoding='utf-8'),'script_result':parsed,
        'input_artifacts':inputs,'expected_outputs':stage_outputs(state,stage),
        'note':'Host must apply original instructions; no generated content is supplied by this bridge. Analysis stays read-only; Nasaq saves its returned report as evidence.'}
    write_json(run/f'evidence/{stage}-handoff.json',packet)
    return packet

def complete(run,stage,note):
    state,lock=checked(run)
    if stage not in STAGES or state['stages'][stage]['status']!='running' or not note.strip():
        raise ValueError('stage not running or missing application note')
    required=stage_outputs(state,stage)
    outputs={p:digest(inside(run,p)) for p in required if inside(run,p).is_file() and inside(run,p).stat().st_size}
    if len(outputs)!=len(required):
        raise ValueError('missing output; cannot complete')
    for name,value in state['stages'][stage]['input_hashes'].items():
        if digest(inside(run,name))!=value:
            raise ValueError('previous output changed; explicit revision required')
    state['stages'][stage].update(status='completed',output_hashes=outputs,application_note=note,
        evidence_paths=[f'evidence/{stage}-handoff.json',f'evidence/{stage}-script.json'])
    write_json(run/'run.json',state); event(run,'stage_completed',stage=stage,output_hashes=outputs)

def submit_outputs(run, stage, contents, note):
    """Persist host responses after a real handoff; never synthesize planning text.

    This is provenance of submission, not independent quality certification.
    Input keys must exactly match the stage contract before any output is written.
    """
    state,_=checked(run)
    if stage not in STAGES or state['paused'] or state['stages'][stage]['status']!='running':
        raise ValueError('no active handoff')
    if not isinstance(note,str) or not note.strip():
        raise ValueError('application note required')
    packet=load_json(run/f'evidence/{stage}-handoff.json')
    if not isinstance(contents,dict) or set(contents)!=set(stage_outputs(state,stage)):
        raise ValueError('output contract mismatch')
    if any(not isinstance(text,str) or not text.strip() for text in contents.values()):
        raise ValueError('empty output')
    if packet['stage']!=stage or packet['expected_outputs']!=stage_outputs(state,stage):
        raise ValueError('handoff mismatch')
    destinations={name:inside(run,name) for name in contents}
    receipt={'schema_version':2,'author':'host-agent applying upstream instructions','stage':stage,
        'handoff_sha256':digest(run/f'evidence/{stage}-handoff.json'),
        'content_sha256':{p:hashlib.sha256(t.encode('utf-8')).hexdigest() for p,t in contents.items()},
        'note':note}
    write_json(run/f'evidence/{stage}-submission.json',receipt)
    event(run,'host_output_submitted',stage=stage,handoff_sha256=receipt['handoff_sha256'])
    for name,path in destinations.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix(path.suffix+'.tmp')
        # Preserve the submitted bytes on Windows too; otherwise CRLF conversion
        # makes the submission digest differ from the saved artifact digest.
        tmp.write_text(contents[name],encoding='utf-8',newline=''); tmp.replace(path)
    complete(run,stage,note)

def pause(run):
    state,_=checked(run)
    if any(s['status']=='running' for s in state['stages'].values()):
        raise ValueError('pause at a completed-stage boundary')
    state['paused']=True; write_json(run/'run.json',state); event(run,'paused')

def resume(run):
    state,_=checked(run)
    if any(s['status'] in {'running','failed'} for s in state['stages'].values()):
        raise ValueError('partial stage requires explicit recovery; not silently rerun')
    state['paused']=False; write_json(run/'run.json',state)
    next_stage=next((s for s in STAGES if state['stages'][s]['status']=='pending'),None)
    event(run,'resumed',next_stage=next_stage,completed_preserved=[s for s in STAGES if state['stages'][s]['status']=='completed'])
    return next_stage

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['init','begin','complete','pause','resume'])
    p.add_argument('--run',type=Path,required=True); p.add_argument('--upstream',type=Path)
    p.add_argument('--request',type=Path); p.add_argument('--review',type=Path)
    p.add_argument('--lang',choices=['ar','en'],default='ar'); p.add_argument('--stage',choices=STAGES)
    p.add_argument('--note',default='')
    a=p.parse_args(); run=a.run.resolve()
    if a.action=='init': initialize(run,a.upstream.resolve(),a.request.read_text(encoding='utf-8'),a.lang,a.review)
    elif a.action=='begin': print(json.dumps(begin(run,a.stage),ensure_ascii=False,indent=2))
    elif a.action=='complete': complete(run,a.stage,a.note)
    elif a.action=='pause': pause(run)
    else: print(resume(run))

if __name__=='__main__': main()
