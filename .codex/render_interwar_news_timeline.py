from pathlib import Path
from datetime import date,timedelta
from collections import Counter
import json,re

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'.codex/interwar_news_inventory.json').read_text(encoding='utf-8'))

def calls(cs):
    for c in cs:
        yield c
        yield from calls(c['upstream'])

def timing(row):
    constraints=[s for c in calls(row['calls']) for s in c['conditions'] if s.startswith('date ')]
    low=[]; high=[]
    for s in constraints:
        m=re.fullmatch(r'date ([<>]) (\d+)\.(\d+)\.(\d+)',s)
        if m:
            d=date(*map(int,m.groups()[1:]))
            (low if m[1]=='>' else high).append(d)
    lower=max(low) if low else None
    upper=min(high) if high else None
    if row['id']=='INT_turkey_news.13': lower=date(1920,8,9)
    if row['id'] in ('INT_russian_news.9','INT_russian_news.10','INT_russian_news.11','INT_russian_news.12','INT_russian_news.13'): lower=date(1919,4,1)
    first=lower+timedelta(days=1) if lower else None
    last=upper-timedelta(days=1) if upper else None
    if first and last and row['type']=='DATED': window=first.isoformat() if first==last else f'{first.isoformat()}–{last.isoformat()}'
    elif first: window='From '+first.isoformat()+(f'; before {upper.isoformat()}' if upper and upper<date(1936,1,1) else '')
    else: window='No fixed date'
    if row['id'] in ('INT_russian_news.9','INT_russian_news.10','INT_russian_news.11','INT_russian_news.12','INT_russian_news.13'): window += '; White victory branch'
    row['first']=first.isoformat() if first else '9999-12-31'
    row['window']=window
    fs=list(dict.fromkeys(c['caller'][6:] for c in calls(row['calls']) if c['caller'].startswith('focus:')))
    row['focuses']=fs
    if row['id']=='INT_turkey_news.1': row['window']='1923-07-24 onward; Lausanne focus/fallback'
    if row['id']=='INT_turkey_news.2': row['window']='1923-10-29 onward; republic focus/fallback'
    if row['id']=='INT_turkey_news.16': row['window']='1922-11-01 onward; sultanate focus/fallback'
    if row['id']=='INT_ireland_news.5': row['window']='Government victory; ceasefire fallback from 1923-05-24'
    if row['id']=='INT_ireland_news.9': row['window']='Republican victory in the civil war'
    if row['id']=='INT_uk_news.1': row['window']='Unused definition; no active caller'

for r in rows: timing(r)
assert len(rows)==159 and len({r['id'] for r in rows})==159
parts=['# All 159 interwar news definitions and their scripted timeline','',
'Inventory of the current Endsieg scripts. Dates below are the source trigger windows, not a promise that every headline fires on that date. Country choices, required focuses, flags, wars and the usual short event delays still apply. This is a script inventory, not a claim that every focus window matches the real-world date.', '',
'The count includes multiple national headlines about the same incident, alternative-history reports, and one unused British treaty definition. All 159 definitions have `major = yes`; that broadcasts a report to all countries once its source actually calls it. Broadcasting does not create a source trigger.', '',
'Historical major-country schedulers generally require their interwar tree, a date before 1936 and no Central Powers victory. Several French and German reports additionally require Compiègne/Versailles and their appropriate political route. Turkey combines focus completion with settlement safeguards; its Lausanne, republic and sultanate steps have dated fallbacks. Irish reports have their own phase, ownership and war checks.', '',
'The three Irish-chain reports `endsieg_news.60` (War of Independence), `.61` (Anglo-Irish Treaty) and `.62` (civil-war outbreak) are existing non-INT definitions and are **additional to these 159**. Their source dates are 1919-01-21, 1921-12-06 and 1922-06-28 respectively, subject to chain progress.', '',
'## Dated or dated-fallback reports (112)','',
'Dates show the calendar days within the strict `date >` / `date <` bounds. A news report scheduled after a source event or its chosen option can arrive later.', '',
'| Trigger window | Event ID | Headline | Source |','| --- | --- | --- | --- |']
def link(path,line,label): return f'[{label}](<{(ROOT/path).as_posix()}:{line}>)'
def source(r):
    if not r['calls']: return 'None'
    cs=r['calls']
    return '; '.join(link(c['file'],c['line'],c['caller'].replace('focus:','')) for c in cs)
for r in sorted((r for r in rows if r['type']=='DATED'),key=lambda r:(r['first'],r['id'])):
    parts.append(f"| {r['window']} | `{r['id']}` | {r['title']} | {source(r)} |")
parts+=['','## Focus-driven reports (44)','',
'These dates unlock focuses or bound the announcement; the report follows focus completion. They are not automatically scheduled on the opening date. White Russia and a surviving Ottoman parliamentary path are alternative-history outcomes.', '',
'| Timing | Event ID | Headline | Required focus |','| --- | --- | --- | --- |']
for r in sorted((r for r in rows if r['type']=='FOCUS'),key=lambda r:(r['first'],r['id'])):
    parts.append(f"| {r['window']} | `{r['id']}` | {r['title']} | {', '.join('`'+x+'`' for x in r['focuses'])} |")
parts+=['','## Outcome-driven reports and unused definition (3)','',
'| Condition | Event ID | Headline |','| --- | --- | --- |']
for r in rows:
    if r['type'] in ('OUTCOME','UNUSED'): parts.append(f"| {r['window']} | `{r['id']}` | {r['title']} |")
parts+=['','The unused `INT_uk_news.1` is replaced in the active Irish chain by `endsieg_news.61`; it is retained to preserve the existing ID.','',
'## Count by namespace','', '| Namespace | Definitions |','| --- | --- |']
for ns,n in Counter(r['id'].split('.')[0] for r in rows).items(): parts.append(f'| `{ns}` | {n} |')
parts.append('| **Total** | **159** |')
parts+=['', 'Checked against the local mod files without launching HOI4. No gameplay scripts were changed for this inventory.','']
out=ROOT/'tools/INTERWAR_NEWS_TIMELINE.md'
out.write_text('\n'.join(parts),encoding='utf-8')
(ROOT/'.codex/interwar_news_timeline_rows.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
print(str(out))
print('Rows:',Counter(r['type'] for r in rows))
