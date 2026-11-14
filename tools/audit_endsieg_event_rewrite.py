"""Read-only event and picture inventory for the Endsieg writing/art rewrite.

The CSV records every event id and resolved image when possible. Counts compare
image pixels when Pillow can decode the file, rather than sprite names alone.
"""
from pathlib import Path
from collections import Counter
import csv, hashlib, re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV')
OUT=Path(r'C:/Users/adam0/Documents/Codex/2026-10-15/ma/outputs/event_rewrite_audit')

def read(p):
 try:return p.read_text(encoding='utf-8-sig')
 except UnicodeError:return p.read_text(encoding='cp1252',errors='replace')

def blocks(text, pattern):
 for m in re.finditer(pattern,text,re.M):
  opening=text.index('{',m.start());depth=0;quoted=False;comment=False;escape=False
  for i in range(opening,len(text)):
   ch=text[i]
   if comment:
    if ch=='\n':comment=False
    continue
   if ch=='"' and not escape:quoted=not quoted
   if not quoted:
    if ch=='#':comment=True;continue
    if ch=='{':depth+=1
    elif ch=='}':
     depth-=1
     if depth==0:
      yield text[m.start():i+1];break
   escape=(ch=='\\' and not escape)

def gfx_index():
 idx={}
 for base in (GAME,ROOT):
  for p in (base/'interface').glob('*.gfx'):
   for b in blocks(read(p),r'(?m)^\s*spriteType\s*=\s*\{'):
    n=re.search(r'\bname\s*=\s*"?(GFX_[\w]+)"?',b);t=re.search(r'\btexturefile\s*=\s*"([^"]+)"',b,re.I)
    if n and t:idx[n.group(1)]=t.group(1).replace('\\','/')
 return idx

def photo_key(path):
 for base in (ROOT,GAME):
  p=base/path
  if p.is_file():
   try:
    with Image.open(p) as im:
     im=im.convert('RGBA');return 'pixels:'+hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest(),str(p)
   except Exception:return 'bytes:'+hashlib.sha256(p.read_bytes()).hexdigest(),str(p)
 return '', ''

def main():
 OUT.mkdir(parents=True,exist_ok=True);gfx=gfx_index();cache={};rows=[]
 for p in sorted((ROOT/'events').glob('*.txt')):
  for b in blocks(read(p),r'(?m)^\s*(?:country_event|news_event|state_event)\s*=\s*\{'):
   match=re.search(r'\bid\s*=\s*([\w.]+)',b)
   if not match:continue
   ident=match.group(1);pic=re.search(r'\bpicture\s*=\s*"?(GFX_\w+)',b);pic=pic.group(1) if pic else ''
   title=re.search(r'\btitle\s*=\s*([\w.]+)',b);hidden=bool(re.search(r'(?m)^\s*hidden\s*=\s*yes',b))
   path=gfx.get(pic,'')
   if path and path not in cache:cache[path]=photo_key(path)
   key,full=cache[path] if path else ('','')
   rows.append({'event_id':ident,'file':p.name,'title_key':title.group(1) if title else '', 'picture_sprite':pic,'image_path':full,'picture_key':key,'hidden':hidden})
 uses=Counter(x['picture_key'] for x in rows if x['picture_key'] and not x['hidden'])
 for x in rows:x['visible_uses']=uses.get(x['picture_key'],0)
 target=OUT/'event_pictures.csv'
 with target.open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 visible=[x for x in rows if not x['hidden']];reused=sum(x['visible_uses']>1 for x in visible)
 print('events:',len(rows),'visible:',len(visible),'visible with duplicated image:',reused,'unique resolved pictures:',len(uses),'unresolved sprites:',sum(bool(x['picture_sprite']) and not x['picture_key'] for x in visible))
 print('inventory:',target)
if __name__=='__main__':main()
