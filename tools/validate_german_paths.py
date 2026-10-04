"""Validate the German interwar political and diplomatic paths without launching HOI4."""
from pathlib import Path
from collections import Counter
import argparse, re
from validate_focus_split import nodes, get, ident, TOKEN

ROOT = Path(__file__).resolve().parents[1]
FOCUS_FILE = ROOT / 'common/national_focus/INT - Germany.txt'
NAMES = [
 'common/decisions/INT_German_Paths.txt',
 'common/decisions/categories/INT_German_Paths.txt',
 'common/ideas/INT_German_Paths.txt',
 'events/INT_German_Paths.txt',
]
EXPECTED = '''parliamentary_commissions civic_education social_compromise local_government_reform republican_crisis_cabinet defend_constitution shop_floor_committees workers_planning_board socialist_welfare red_training_schools workers_republic_constitution prussian_administration federal_chambers restored_court royal_railways monarchist_reconciliation rapallo_commission eastern_trade_network eastern_exercises joint_aviation_trials diplomatic_treaty_revision foreign_press_campaign hidden_procurement officer_professionalization party_administration controlled_press reich_labor_front state_contracts arms_contracts'''.split()

def walk(seq):
 for n in seq:
  yield n
  yield from walk(n['children'])

def main():
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--vanilla',type=Path,help='Installed Hearts of Iron IV root for sprite checks')
 args=a.parse_args()
 errors=[]; parsed={}
 for path in [FOCUS_FILE]+[ROOT/name for name in NAMES]:
  if not path.exists():errors.append(f'Missing file: {path}');continue
  data=path.read_text(encoding='utf-8-sig');depth=0
  for t in TOKEN.finditer(data):
   depth+=(t[0]=='{')-(t[0]=='}')
   if depth<0:errors.append(f'Unexpected closing brace: {path}');break
  if depth:errors.append(f'Unbalanced braces: {path}')
  parsed[path]=nodes(data)
 if errors:raise SystemExit('\n'.join(errors))
 fs=[n for n in get(parsed[FOCUS_FILE],'focus_tree')['children'] if n['key']=='focus']
 ids=[ident(f) for f in fs]
 for key,num in Counter(ids).items():
  if num!=1:errors.append(f'Duplicate focus: {key}')
 for key in EXPECTED:
  if 'INT_GER_'+key not in ids:errors.append(f'Missing new focus: {key}')
 coords=Counter((get(f['children'],'x')['value'],get(f['children'],'y')['value']) for f in fs)
 for xy,num in coords.items():
  if num>1:errors.append(f'Focus position collision: {xy}')
 req={}
 for f in fs:
  fid=ident(f)
  req[fid]=[[c['value'] for c in n['children'] if c['key']=='focus'] for n in f['children'] if n['key']=='prerequisite']
  for group in req[fid]:
   for ref in group:
    if ref not in ids:errors.append(f'Unresolved prerequisite: {fid} -> {ref}')
 for blocked,target in [
  ({'INT_GER_a_new_leaf','INT_GER_dismantle_the_republic','INT_GER_appoint_hitler'},'INT_GER_defend_constitution'),
  ({'INT_GER_retain_the_republic','INT_GER_dismantle_the_republic'},'INT_GER_workers_republic_constitution'),
  ({'INT_GER_retain_the_republic','INT_GER_a_new_leaf','INT_GER_instate_new_monarchy'},'INT_GER_monarchist_reconciliation'),
  ({'INT_GER_retain_the_republic','INT_GER_a_new_leaf','INT_GER_continuation_of_democracy'},'INT_GER_restored_court'),
  ({'INT_GER_a_new_leaf','INT_GER_dismantle_the_republic','INT_GER_defend_democracy'},'INT_GER_arms_contracts'),
 ]:
  reached=set()
  while True:
   candidates={fid for fid,groups in req.items() if fid not in blocked and all(any(r in reached for r in g) for g in groups)}
   if candidates<=reached:break
   reached|=candidates
  if target not in reached:errors.append(f'Route to {target} fails when {blocked} excluded')
 cats=parsed[ROOT/NAMES[1]]; decisions=[d for c in parsed[ROOT/NAMES[0]] for d in c['children']]
 if len(cats)<5:errors.append(f'Expected at least 5 path categories; found {len(cats)}')
 if len(decisions)<12:errors.append(f'Expected at least 12 path decisions; found {len(decisions)}')
 for d in decisions:
  try:
   if get(d['children'],'fire_only_once')['value']!='yes':errors.append(f'Repeatable decision: {d["key"]}')
   if int(get(d['children'],'cost')['value'])<20:errors.append(f'Low-cost decision: {d["key"]}')
  except (KeyError,ValueError):errors.append(f'Missing one-time/cost field: {d["key"]}')
 ideas=get(get(parsed[ROOT/NAMES[2]],'ideas')['children'],'country')['children']
 idea_ids={n['key'] for n in ideas}
 # Scripted effects can list several ideas inside an anonymous Clausewitz block.
 for script in [FOCUS_FILE, ROOT/NAMES[0], ROOT/NAMES[3]]:
  raw=script.read_text(encoding='utf-8-sig')
  for n in walk(parsed[script]):
   if n['key'] in ('add_ideas','remove_ideas','has_idea','idea') and n['value'].startswith('INT_GER_paths_') and n['value'] not in idea_ids:
    errors.append(f'Undefined path idea: {n["value"]} in {script.name}')
  for block in re.findall(r'\b(?:add_ideas|remove_ideas)\s*=\s*\{([^{}]*)\}',raw):
   for key in re.findall(r'\bINT_GER_paths_[A-Za-z0-9_]+\b',block):
    if key not in idea_ids:errors.append(f'Undefined listed path idea: {key} in {script.name}')
 events=[n for n in parsed[ROOT/NAMES[3]] if n['key'] in ('country_event','news_event')]
 ev_ids=[ident(n) for n in events]
 for i in range(1,8):
  if 'INT_ger_paths.'+str(i) not in ev_ids:errors.append(f'Missing branch event {i}')
 for e in events:
  if get(e['children'],'is_triggered_only')['value']!='yes':errors.append(f'Unexpected automatic event: {ident(e)}')
  if len([n for n in e['children'] if n['key']=='option'])<2 and ident(e) in {'INT_ger_paths.'+str(i) for i in range(1,8)}:
   errors.append(f'Missing choice in {ident(e)}')
  for option in [n for n in e['children'] if n['key']=='option']:
   gates=[n for n in option['children'] if n['key']=='if']
   if not gates or not any(n['key']=='else' for n in option['children']):
    errors.append(f"Event choice lacks late-state fallback: {ident(e)} / {get(option['children'], 'name')['value']}")
   elif not any(n['key']=='has_focus_tree' and n['value']=='INT_germany' for n in walk(gates)):
    errors.append(f'Event choice lacks interwar-tree guard: {ident(e)}')
 loc=Counter()
 for p in (ROOT/'localisation/replace/english').glob('*.yml'):
  loc.update(re.findall(r'^\s*([\w.]+):',p.read_text(encoding='utf-8-sig'),re.M))
 needed=set()
 for key in EXPECTED:
  needed.update(['INT_GER_'+key,'INT_GER_'+key+'_desc'])
 for n in cats+decisions+ideas:
  needed.update([n['key'],n['key']+'_desc'])
 for n in walk(parsed[ROOT/NAMES[3]]):
  if n['key'] in ('title','desc','name','text') and n['value'].startswith('INT_ger_paths.'):
   needed.add(n['value'])
 for n in walk(parsed[ROOT/NAMES[0]]):
  if n['key']=='name' and n['value'].startswith('INT_GER_paths_'):
   needed.add(n['value'])
 for n in walk(parsed[FOCUS_FILE]):
  if n['key']=='id' and n['value'].startswith('INT_ger_paths.') and n['value'] not in ev_ids:
   errors.append(f'Unresolved focus event: {n["value"]}')
  if n['key']=='name' and n['value'].startswith('INT_GER_') and n['value'] not in loc:
   # Existing bonus names can be unlocalized; new bonus labels are in the focus localization file.
   if n['value'] in (ROOT/'localisation/replace/english/endsieg_german_paths_focus_l_english.yml').read_text(encoding='utf-8-sig'):
    needed.add(n['value'])
 for key in needed:
  if loc[key]!=1:errors.append(f'Localization count {loc[key]} for {key}')
 for name in ['endsieg_german_paths_l_english.yml','endsieg_german_paths_focus_l_english.yml']:
  p=ROOT/'localisation/replace/english'/name
  if not p.exists() or not p.read_bytes().startswith(b'\xef\xbb\xbf'):
   errors.append(f'Missing UTF-8 BOM: {p}')
 if args.vanilla:
  sprites=set()
  for folder in [ROOT/'interface',args.vanilla/'interface']:
   for p in folder.rglob('*.gfx'):
    sprites.update(re.findall(r'\bname\s*=\s*"([^"]+)"',p.read_text(encoding='utf-8-sig',errors='replace')))
  def check(value,prefix):
   key=value if value.startswith('GFX_') else prefix+value
   if key not in sprites:errors.append(f'Missing sprite: {key}')
  for f in fs:check(get(f['children'],'icon')['value'],'')
  for n in cats:check(get(n['children'],'icon')['value'],'GFX_decision_category_')
  for n in decisions:check(get(n['children'],'icon')['value'],'GFX_decision_')
  for n in ideas:check(get(n['children'],'picture')['value'],'GFX_idea_')
  for n in events:check(get(n['children'],'picture')['value'],'')
 if errors:raise SystemExit('\n'.join(errors))
 print(f'PASS: {len(fs)} focus IDs, {len(EXPECTED)} new focuses, {len(decisions)} one-time decisions, {len(events)} choice events and {len(needed)} localized path keys.')
 print('PASS: path dependencies, branch reachability, braces, references and vanilla sprites (when supplied). Static validation only.')

if __name__=='__main__':main()
