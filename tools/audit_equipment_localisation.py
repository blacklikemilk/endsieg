"""Audit equipment and module text against mod and installed vanilla English text.

This does not launch HOI4. Optional vanilla short names and descriptions are
reported separately from required names and custom equipment text.
"""
from pathlib import Path
from collections import Counter
import argparse
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|\#[^\r\n]*|\?=|!=|<=|>=|[{}=<>]|[^\s{}=<>#!]+')
OPS = {'=', '<', '>', '<=', '>=', '!=', '?='}


def locate_vanilla():
    candidates = []
    if os.environ.get('HOI4_INSTALL'):
        candidates.append(Path(os.environ['HOI4_INSTALL']))
    for variable in ('PROGRAMFILES(X86)', 'PROGRAMFILES'):
        if not os.environ.get(variable):
            continue
        steamapps = Path(os.environ[variable]) / 'Steam/steamapps'
        candidates.append(steamapps / 'common/Hearts of Iron IV')
        libraries = steamapps / 'libraryfolders.vdf'
        if libraries.is_file():
            for library in re.findall(r'"path"\s+"([^"]+)"', libraries.read_text(encoding='utf-8-sig')):
                candidates.append(Path(library.replace('\\\\', '\\')) / 'steamapps/common/Hearts of Iron IV')
    return next((p for p in candidates if (p / 'common/units/equipment').is_dir()), None)


def parse(path):
    source = path.read_text(encoding='utf-8-sig', errors='replace')
    tokens = [m.group() for m in TOKEN.finditer(source) if not m.group().startswith('#')]
    index = 0

    def block(nested=False):
        nonlocal index
        result = []
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == '}':
                if not nested:
                    raise ValueError(f'{path}: unexpected closing brace')
                return result
            if key == '{' or key in OPS:
                raise ValueError(f'{path}: unexpected token {key}')
            if index < len(tokens) and tokens[index] in OPS:
                operation = tokens[index]
                index += 1
                if index >= len(tokens):
                    raise ValueError(f'{path}: assignment without value')
                value = tokens[index]
                index += 1
                if value == '{':
                    value = block(True)
                elif value == '}':
                    raise ValueError(f'{path}: assignment before closing brace')
                result.append((key, operation, value))
            else:
                result.append((key, None, None))
        if nested:
            raise ValueError(f'{path}: missing closing brace')
        return result

    return block()


def value(nodes, key, default=None):
    return next((v for k, op, v in nodes if k == key), default)


def effective_equipment(vanilla):
    files = {}
    for base in (vanilla, ROOT):
        for path in (base / 'common/units/equipment').glob('*.txt'):
            files[path.name] = path
    definitions = {}
    vanilla_ids = set()
    for path in (vanilla / 'common/units/equipment').glob('*.txt'):
        for key, op, block in parse(path):
            if key == 'equipments' and isinstance(block, list):
                vanilla_ids.update(k for k, o, v in block if isinstance(v, list))
    for path in sorted(files.values(), key=lambda p: p.name):
        for key, op, block in parse(path):
            if key == 'equipments' and isinstance(block, list):
                for key, op, node in block:
                    if isinstance(node, list):
                        definitions[key] = {'file': str(path), 'data': node, 'custom': key not in vanilla_ids}
    return definitions


def english_localisation(vanilla):
    # Mod files shadow files at the same relative path; replacement folders
    # then take precedence over ordinary localisation keys.
    files = {}
    for base in (vanilla, ROOT):
        for path in (base / 'localisation').rglob('*l_english.yml'):
            files[path.relative_to(base / 'localisation')] = path
    entries = {}
    for relative, path in sorted(files.items(), key=lambda item: ('replace' in item[0].parts, item[1].is_relative_to(ROOT), str(item[0]))):
        for match in re.finditer(r'^\s*([^\s:#]+):\d*\s*"(.*)"', path.read_text(encoding='utf-8-sig', errors='replace'), re.M):
            entries[match[1]] = match[2]
    return entries


def unresolved(key, entries, seen=()):
    if key in seen or not entries.get(key, '').strip():
        return True
    for reference in re.findall(r'\$([A-Za-z0-9_.]+)\$', entries[key]):
        if unresolved(reference, entries, seen + (key,)):
            return True
    return False


def inventory(vanilla):
    equipment = effective_equipment(vanilla)
    text = english_localisation(vanilla)
    missing = {suffix: [key for key in equipment if unresolved(key + suffix, text)] for suffix in ('', '_short', '_desc')}
    return equipment, text, missing


def module_inventory(vanilla, equipment, text):
    files = {}
    for base in (vanilla, ROOT):
        for path in (base / 'common/units/equipment/modules').glob('*.txt'):
            files[path.name] = path
    modules = {}
    for path in sorted(files.values(), key=lambda p: p.name):
        for key, op, block in parse(path):
            if key == 'equipment_modules' and isinstance(block, list):
                for key, op, node in block:
                    # Engine condition blocks are not module definitions.
                    if isinstance(node, list) and value(node, 'category') is not None:
                        modules[key] = node
    categories = set()
    slots = set()

    def walk(nodes):
        for key, op, node in nodes:
            if key == 'allowed_module_categories' and isinstance(node, list):
                categories.update(k for k, o, v in node if o is None)
            if key == 'module_slots' and isinstance(node, list):
                slots.update(k for k, o, v in node if isinstance(v, list))
            if isinstance(node, list):
                walk(node)

    for node in modules.values():
        category = value(node, 'category')
        if isinstance(category, list):
            categories.update(k for k, o, v in category if o is None)
        else:
            categories.add(category)
    for entry in equipment.values():
        walk(entry['data'])
    keys = {
        'module name': sorted(modules),
        'module description': [k + '_desc' for k in sorted(modules)],
        'module category': [f'EQ_MOD_CAT_{k}_TITLE' for k in sorted(categories)],
        'designer slot': [f'EQ_MOD_SLOT_{k}_TITLE' for k in sorted(slots)],
    }
    missing = {kind: [key for key in names if unresolved(key, text)] for kind, names in keys.items()}
    return keys, missing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='Write the full equipment/localisation inventory')
    args = parser.parse_args()
    vanilla = locate_vanilla()
    if vanilla is None:
        raise SystemExit('Current vanilla equipment directory could not be located')
    equipment, text, missing = inventory(vanilla)
    module_keys, module_missing = module_inventory(vanilla, equipment, text)
    counts = Counter(entry['custom'] for entry in equipment.values())
    print(f'Equipment: {len(equipment)} effective definitions ({counts[True]} custom IDs).')
    for suffix, keys in missing.items():
        custom = [k for k in keys if equipment[k]['custom']]
        print(f'Missing {suffix or "name"}: {len(keys)} total; {len(custom)} custom.')
        if suffix == '' or custom:
            print(', '.join(keys if suffix == '' else custom))
    for kind, keys in module_keys.items():
        print(f'{kind.capitalize()}: {len(keys)} checked; {len(module_missing[kind])} missing.')
        if module_missing[kind]:
            print(', '.join(module_missing[kind]))
    if args.json:
        args.json.write_text(json.dumps({'vanilla': str(vanilla), 'entries': equipment, 'loc': text, 'missing': missing, 'module_keys': module_keys, 'module_missing': module_missing}, ensure_ascii=False, indent=2), encoding='utf-8')
    if missing[''] or any(equipment[k]['custom'] for suffix in ('_short','_desc') for k in missing[suffix]) or any(module_missing.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
