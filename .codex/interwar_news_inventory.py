from pathlib import Path
from collections import defaultdict
import re, json, bisect

ROOT = Path(__file__).resolve().parents[1]
LEX = re.compile(r'"(?:\\.|[^"\\])*"|\#[^\r\n]*|\?=|!=|<=|>=|[{}=<>]|[^\s{}=<>#!]+')
OPS = {'=', '>', '<', '>=', '<=', '!=', '?='}

def parse(path):
    source = path.read_text(encoding='utf-8-sig', errors='replace')
    lines = [m.start() for m in re.finditer('\n', source)]
    ts = [(m.group(), bisect.bisect_left(lines, m.start()) + 1) for m in LEX.finditer(source) if not m.group().startswith('#')]
    pos = 0
    def block(nested=False):
        nonlocal pos
        out = []
        while pos < len(ts):
            key, line = ts[pos]; pos += 1
            if key == '}': return out
            if pos < len(ts) and ts[pos][0] in OPS:
                op = ts[pos][0]; pos += 1
                value = ts[pos][0]; pos += 1
                if value == '{': value = block(True)
                out.append((key, op, value, line))
            else: out.append((key, None, None, line))
        return out
    return block()

def get(nodes, key, default=None):
    return next((v for k, o, v, l in nodes if k == key), default)

def dates(nodes):
    result = []
    for k,o,v,l in nodes:
        if k in ('date','has_start_date'): result.append(f'{k} {o} {v}')
        elif isinstance(v,list) and k in ('AND','OR','NOT','limit','available','trigger'):
            result.extend(dates(v))
    return result

news = {}
events = {}
incoming = defaultdict(list)
localisation = {}
for p in sorted((ROOT/'localisation').rglob('*l_english.yml'), key=lambda p: ('replace' in p.parts, str(p))):
    for m in re.finditer(r'^\s*([^\s:#]+):\d*\s*"(.*)"',p.read_text(encoding='utf-8-sig',errors='replace'),re.M):
        localisation[m[1]]=m[2]

def scan(nodes, path, label, context=()):
    local = list(context)
    for c in ('limit','available','trigger'):
        v=get(nodes,c)
        if isinstance(v,list): local += dates(v)
    for k,o,v,line in nodes:
        if not isinstance(v,list):
            if k in ('country_event','news_event') and isinstance(v,str):
                incoming[v.strip('"')].append({'caller':label,'conditions':local,'delay':'0','file':str(path.relative_to(ROOT)),'line':line})
            if o=='=' and v=='yes' and k.startswith('INT_'):
                incoming[k].append({'caller':label,'conditions':local,'file':str(path.relative_to(ROOT)),'line':line})
            continue
        if k in ('country_event','news_event'):
            ident=get(v,'id')
            if ident:
                incoming[ident].append({'caller':label,'conditions':local,'delay':get(v,'days',get(v,'hours','0')),'file':str(path.relative_to(ROOT)),'line':line})
        scan(v,path,label,tuple(local))

for folder in ('events','common/scripted_effects','common/national_focus','common/on_actions','common/decisions'):
    for p in (ROOT/folder).rglob('*.txt'):
        ast=parse(p)
        for k,o,n,line in ast:
            if not isinstance(n,list): continue
            if k in ('country_event','news_event'):
                eid=get(n,'id'); label=eid
                events[eid]={'file':str(p.relative_to(ROOT)),'line':line,'conditions':dates(get(n,'trigger',[]))}
                if k=='news_event' and p.name.startswith('INT'):
                    news[eid]={'id':eid,'title':localisation.get(get(n,'title'),get(n,'title')),'file':str(p.relative_to(ROOT)),'line':line}
                scan(n,p,label)
            elif folder=='common/scripted_effects': scan(n,p,k)
            elif folder=='common/national_focus':
                if k in ('focus','shared_focus'): scan(n,p,'focus:'+get(n,'id','?'))
                else:
                    for fk,fo,fn,fl in n:
                        if fk=='focus' and isinstance(fn,list): scan(fn,p,'focus:'+get(fn,'id','?'))
            else: scan(n,p,str(p.relative_to(ROOT))+':'+k)

def routes(target,seen=(),depth=0):
    if depth>5 or target in seen: return []
    out=[]
    for call in incoming.get(target,[]):
        item=dict(call)
        parent=call['caller']
        ancestor=routes(parent,seen+(target,),depth+1)
        item['upstream']=ancestor
        if parent in events: item['conditions']=item['conditions']+events[parent]['conditions']
        out.append(item)
    return out

for eid,n in news.items(): n['calls']=routes(eid)
destination=ROOT/'.codex/interwar_news_inventory.json'
destination.write_text(json.dumps(list(news.values()),indent=2,ensure_ascii=False),encoding='utf-8')
for n in news.values():
    def fmt(cs):
        return '; '.join(c['caller']+' ['+', '.join(c['conditions'])+']'+ (' <- '+fmt(c['upstream']) if c['upstream'] else '') for c in cs)
    print(n['id']+' | '+str(n['title'])+' | '+(fmt(n['calls']) or 'NO CALLER'))
print('TOTAL',len(news))
