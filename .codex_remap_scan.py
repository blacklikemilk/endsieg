from pathlib import Path
import re, subprocess, traceback
try:
 REV='04ca33c9'
 EVENT=Path('events/WWI - German Kaiserslacht Victory.txt')
 def provinces(text):
  m=re.search(r'\bprovinces\s*=\s*\{([^}]*)\}', text, re.S)
  return {int(x) for x in re.findall(r'\b\d+\b',m.group(1))} if m else set()
 def state_id(text):
  m=re.search(r'\bid\s*=\s*(\d+)',text)
  return int(m.group(1)) if m else None
 refs=set()
 pat=re.compile(r'\b(?:controls_state|owns_state|transfer_state|add_state_core|remove_state_core|add_state_claim)\s*=\s*(\d+)\b|\b(\d+)\s*=\s*\{\s*(?:set_state_name|reset_state_name|is_owned_by|is_controlled_by|CONTROLLER)')
 for line in EVENT.read_text(encoding='utf-8-sig').splitlines():
  content=line.split('#',1)[0]
  for m in pat.finditer(content): refs.add(int(m.group(1) or m.group(2)))
 current={}
 for p in Path('history/states').glob('*.txt'):
  text=p.read_text(encoding='utf-8-sig',errors='ignore')
  ident=state_id(text)
  if ident is not None: current[ident]=(p.name,provinces(text))
 ls=subprocess.run(['git','ls-tree','-r','--name-only',REV,'--','history/states'],capture_output=True,text=True,check=True).stdout.splitlines()
 old={}
 for entry in ls:
  if not entry.endswith('.txt'): continue
  text=subprocess.run(['git','show',f'{REV}:{entry}'],capture_output=True,text=True,check=True).stdout
  ident=state_id(text)
  if ident is not None: old[ident]=(entry,provinces(text))
 print('refs',len(refs),'current',len(current),'old',len(old),flush=True)
 for ident in sorted(refs):
  if ident not in old:
   print(f'{ident}: no state definition at {REV}',flush=True); continue
  oldname, oldprov=old[ident]
  ranked=sorted(((len(oldprov & curprov), cid, name, curprov) for cid,(name,curprov) in current.items()),reverse=True)
  overlap,cid,name,curprov=ranked[0]
  same=(ident in current and current[ident][1]==oldprov)
  if not same:
   pct=(overlap/len(oldprov)*100) if oldprov else 0
   print(f'{ident} {Path(oldname).name} -> {cid} {name}; {overlap}/{len(oldprov)} ({pct:.0f}%), exact={oldprov==curprov}',flush=True)
except Exception:
 traceback.print_exc()
