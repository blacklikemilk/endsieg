from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_equipment_localisation import locate_vanilla, parse, value, english_localisation, unresolved

vanilla = locate_vanilla()
text = english_localisation(vanilla)
for relative in (
    'localisation/replace/english/endsieg_research_l_english.yml',
):
    path = ROOT / relative
    assert path.read_bytes().startswith(b'\xef\xbb\xbf'), relative
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    assert lines[0] == 'l_english:', relative
    keys = []
    for line in lines[1:]:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'\s+([^\s:#]+):\d*\s*"(?:[^"\\]|\\.)*"\s*', line)
        assert match, (relative, line)
        keys.append(match[1])
    assert not [key for key, count in Counter(keys).items() if count > 1], relative
    assert not [key for key in keys if unresolved(key, text)], relative
    print(f'{path.name}: {len(keys)} unique keys, valid BOM and aliases.')

gfx = ROOT / 'interface/endsieg_ww1_aircraft_equipment.gfx'
new_sprites = value(parse(gfx), 'spriteTypes')
new_names = [value(node, 'name').strip('"') for key, op, node in new_sprites if isinstance(node, list)]
assert len(new_names) == len(set(new_names)), 'Duplicate new sprites'
existing = set()
for base in (vanilla, ROOT):
    for path in (base / 'interface').rglob('*.gfx'):
        if path == gfx:
            continue
        existing.update(re.findall(r'\bname\s*=\s*"(GFX_[^"\r\n]+)"', path.read_text(encoding='utf-8-sig', errors='replace')))
assert not set(new_names) & existing, sorted(set(new_names) & existing)
for key, op, node in new_sprites:
    if not isinstance(node, list):
        continue
    texture = value(node, 'texturefile').strip('"')
    assert any((base / texture).is_file() for base in (ROOT, vanilla)), texture
print(f'WW1 aircraft sprites: {len(new_names)} unique definitions; all textures exist.')

database = ROOT / 'gfx/interface/equipmentdesigner/graphic_db/endsieg_ww1_plane_icons.txt'
pools = parse(database)
airframes = {f'ww1_small_plane_airframe_{i}' for i in range(4)} | {f'ww1_medium_plane_airframe_{i}' for i in range(3)}
equipment = value(parse(ROOT / 'common/units/equipment/ww1_plane_airframe.txt'), 'equipments')
assert airframes <= {key for key, op, node in equipment}
assert {key for key, op, node in value(pools, 'default')} == airframes
known_sprites = existing | set(new_names)
pool_count = 0
for country, op, nodes in pools:
    for airframe, op, node in nodes:
        assert airframe in airframes, airframe
        for key, op, pool in node:
            assert key == 'pool', key
            for sprite, op, node in value(pool, 'icons'):
                assert sprite in known_sprites, sprite
            pool_count += 1
print(f'WW1 aircraft designer: {pool_count} pools across {len(pools) - 1} countries; all sprite references resolve.')

for relative in ('interface/endsieg_ww1_aircraft_equipment.gfx', 'gfx/interface/equipmentdesigner/graphic_db/endsieg_ww1_plane_icons.txt', 'tools/audit_equipment_localisation.py'):
    for number, line in enumerate((ROOT / relative).read_text(encoding='utf-8-sig').splitlines(), 1):
        assert line == line.rstrip(), (relative, number, 'trailing whitespace')
print('Script structure and whitespace checks passed.')
