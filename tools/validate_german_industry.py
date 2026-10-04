"""Static checks for the German interwar industry branch; does not launch HOI4."""
from pathlib import Path
from collections import Counter
import re
from validate_focus_split import nodes, get, ident, TOKEN

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'common/national_focus/INT - Germany.txt',
    'common/decisions/INT_German_Industry.txt',
    'common/decisions/categories/INT_German_Industry.txt',
    'common/ideas/INT_German_Industry.txt',
    'common/scripted_effects/INT_German_Industry.txt',
    'events/INT_German_Industry.txt',
    'events/INT - Great Depression.txt',
]

def walk(ns):
    for n in ns:
        yield n
        yield from walk(n['children'])

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vanilla', type=Path, help='Installed Hearts of Iron IV directory for sprite checks')
    args = parser.parse_args()
    errors = []
    parsed = {}
    for name in FILES:
        p = ROOT / name
        if not p.exists():
            errors.append(f'Missing file: {name}')
            continue
        text = p.read_text(encoding='utf-8-sig')
        depth = 0
        for t in TOKEN.finditer(text):
            depth += (t[0] == '{') - (t[0] == '}')
            if depth < 0:
                errors.append(f'Unexpected closing brace: {name}')
                break
        if depth:
            errors.append(f'Unbalanced braces: {name}')
        parsed[name] = nodes(text)
    if errors:
        raise SystemExit('\n'.join(errors))
    tree = get(parsed[FILES[0]], 'focus_tree')
    focuses = [n for n in tree['children'] if n['key'] == 'focus']
    ids = [ident(n) for n in focuses]
    for fid, count in Counter(ids).items():
        if count != 1: errors.append(f'Duplicate focus: {fid}')
    positions = Counter((get(n['children'], 'x')['value'], get(n['children'], 'y')['value']) for n in focuses)
    for pos, count in positions.items():
        if count > 1: errors.append(f'Focus position collision: {pos}')
    refs = {}
    for f in focuses:
        fid = ident(f)
        groups = [[c['value'] for c in n['children'] if c['key'] == 'focus'] for n in f['children'] if n['key'] == 'prerequisite']
        refs[fid] = groups
        for group in groups:
            for ref in group:
                if ref not in ids: errors.append(f'Missing prerequisite: {fid} -> {ref}')
    # Both exclusive policy choices must leave the final industry focus reachable.
    for excluded in ['INT_GER_public_works', 'INT_GER_austerity']:
        reachable = set()
        while True:
            added = {fid for fid, groups in refs.items() if fid != excluded and all(any(ref in reachable for ref in group) for group in groups)}
            if added <= reachable: break
            reachable |= added
        if 'INT_GER_industrial_recovery' not in reachable:
            errors.append(f'Industry recovery is unreachable when {excluded} is excluded')
    # Date and dynamic availability require in-game validation; this catches structural loops.
    visiting, visited = set(), set()
    def visit(fid):
        if fid in visiting:
            errors.append(f'Focus dependency cycle at {fid}')
            return
        if fid in visited or fid not in refs: return
        visiting.add(fid)
        for group in refs[fid]:
            for ref in group: visit(ref)
        visiting.remove(fid); visited.add(fid)
    for fid in ids: visit(fid)
    loc = Counter()
    for p in (ROOT / 'localisation/replace/english').glob('*.yml'):
        for key in re.findall(r'^\s*([\w.]+):', p.read_text(encoding='utf-8-sig'), re.M): loc[key] += 1
    required_loc = set()
    for fid in ids:
        required_loc.update([fid, fid + '_desc'])
    effects = {n['key'] for n in parsed[FILES[4]]}
    idea_names = {n['key'] for n in get(get(parsed[FILES[3]], 'ideas')['children'], 'country')['children']}
    event_ids = {ident(n) for n in parsed[FILES[5]] if n['key'] in ('country_event', 'news_event')}
    decision_categories = parsed[FILES[2]]
    for cat in decision_categories:
        required_loc.update([cat['key'], cat['key'] + '_desc'])
    for cat in parsed[FILES[1]]:
        for dec in cat['children']:
            required_loc.update([dec['key'], dec['key'] + '_desc'])
    for idea in idea_names:
        required_loc.update([idea, idea + '_desc'])
    for name, ns in parsed.items():
        for n in walk(ns):
            key, val = n['key'], n['value']
            if key.startswith('INT_GER_industry_') and val == 'yes' and key not in effects:
                errors.append(f'Undefined scripted effect: {key} ({name})')
            if key == 'has_completed_focus' and val.startswith('INT_GER_') and val not in ids:
                errors.append(f'Undefined German focus: {val} ({name})')
            if key in ('title', 'desc', 'text', 'custom_effect_tooltip') and val.startswith(('INT_GER_', 'INT_ger_industry.')):
                required_loc.add(val)
            if key == 'name' and (val.startswith(('INT_GER_industry_', 'INT_ger_industry.')) or val in ('INT_GER_grid_bonus', 'INT_GER_industrial_recovery_bonus')):
                required_loc.add(val)
            if key in ('add_ideas', 'remove_ideas', 'has_idea', 'idea') and val.startswith('INT_GER_industry_') and val not in idea_names:
                errors.append(f'Undefined industry idea: {val} ({name})')
            if key == 'id' and val.startswith('INT_ger_industry.') and val not in event_ids:
                errors.append(f'Undefined industry event: {val} ({name})')
    for key in sorted(required_loc):
        if not loc[key]: errors.append(f'Missing English localization: {key}')
        elif loc[key] > 1: errors.append(f'Duplicate English localization: {key}')
    for name in ['endsieg_german_industry_l_english.yml', 'endsieg_german_industry_focus_l_english.yml']:
        if not (ROOT / 'localisation/replace/english' / name).read_bytes().startswith(b'\xef\xbb\xbf'):
            errors.append(f'Missing UTF-8 BOM: {name}')
    if args.vanilla:
        sprites = set()
        for folder in [ROOT / 'interface', args.vanilla / 'interface']:
            for p in folder.rglob('*.gfx'):
                sprites.update(re.findall(r'\bname\s*=\s*"([^"]+)"', p.read_text(encoding='utf-8-sig', errors='replace')))
        def sprite(value, prefix):
            name = value if value.startswith('GFX_') else prefix + value
            if name not in sprites: errors.append(f'Missing sprite: {name}')
        for cat in parsed[FILES[2]]:
            sprite(get(cat['children'], 'icon')['value'], 'GFX_decision_category_')
        for cat in parsed[FILES[1]]:
            for dec in cat['children']:
                sprite(get(dec['children'], 'icon')['value'], 'GFX_decision_')
                if get(dec['children'], 'fire_only_once')['value'] != 'yes':
                    errors.append(f'Investment is repeatable: {dec["key"]}')
        for idea in get(get(parsed[FILES[3]], 'ideas')['children'], 'country')['children']:
            sprite(get(idea['children'], 'picture')['value'], 'GFX_idea_')
        for event in parsed[FILES[5]]:
            if event['key'] == 'country_event': sprite(get(event['children'], 'picture')['value'], '')
        for focus in focuses:
            sprite(get(focus['children'], 'icon')['value'], '')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(FILES)} script files balanced; {len(ids)} unique German focuses with no position collisions or dependency cycles.')
    print(f'PASS: both recovery policies structurally reach final industry focus; {len(required_loc)} localization keys resolve uniquely.')
    print('PASS: new industry effect, event, idea and focus references resolve. Static validation only; playtesting required.')

if __name__ == '__main__':
    main()
