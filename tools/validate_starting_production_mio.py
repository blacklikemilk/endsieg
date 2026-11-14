"""Check starting production's specialist-first MIO selection without launching HOI4."""
from __future__ import annotations

import argparse
from itertools import permutations
import json
from pathlib import Path

from validate_1194_compatibility import parse, walk


PRIORITIES = {
    'early_infantry_equipment_0': 'generic_infantry_equipment_organization',
    'support_equipment_1': 'generic_support_equipment_organization',
    'rations_1': 'generic_support_equipment_organization',
    'artillery_equipment_1': 'generic_artillery_organization',
    'train_equipment_1': 'generic_train_organization',
    'mechanized_equipment_1': 'generic_motorized_mechanized_organization',
}
GERMAN = {
    'early_infantry_equipment_0': 'GER_mauser_organization',
    'support_equipment_1': 'GER_carl_walther_organization',
    'rations_1': 'GER_carl_walther_organization',
    'artillery_equipment_1': 'GER_rheinmetall_organization',
    'train_equipment_1': 'GER_henschel_kassel_organization',
    'mechanized_equipment_1': 'GER_opel_organization',
}


def child(node, key):
    return next(n for n in node.children if n.key == key)


def scalar(node, key):
    item = next((n for n in node.children if n.key == key), None)
    return item.value if item else None


def identifiers(loop):
    return {n.value for n, _ in walk(loop.children)
            if n.key == 'is_military_industrial_organization'}


def select(effect, available, dlc=True):
    # Interpret the actual restricted effect AST, including the scratch variable.
    manufacturer = 'stale'

    def condition(nodes, current=None):
        result = []
        for n in nodes:
            if n.key == 'OR':
                result.append(any(condition([x], current) for x in n.children))
            elif n.key == 'NOT':
                result.append(not condition(n.children, current))
            elif n.key == 'PREV':
                result.append(condition(n.children, current))
            elif n.key == 'has_variable':
                assert n.value == 'endsieg_starting_manufacturer'
                result.append(manufacturer is not None)
            elif n.key == 'has_dlc':
                assert n.value.strip('"') == 'Arms Against Tyranny'
                result.append(dlc)
            elif n.key == 'is_mio_available':
                result.append(current in available)
            elif n.key == 'is_military_industrial_organization':
                result.append(current == n.value)
            else:
                raise AssertionError(('Unexpected selector condition', n.key))
        return all(result)

    def execute(nodes, current=None):
        nonlocal manufacturer
        for n in nodes:
            if n.key == 'clear_variable':
                assert n.value == 'endsieg_starting_manufacturer'
                manufacturer = None
            elif n.key == 'if':
                if condition(child(n, 'limit').children, current):
                    execute([x for x in n.children if x.key != 'limit'], current)
            elif n.key == 'every_military_industrial_organization':
                for mio in available:
                    if condition(child(n, 'limit').children, mio):
                        execute([x for x in n.children if x.key != 'limit'], mio)
            elif n.key == 'set_variable':
                assert [(x.key, x.value) for x in n.children] == [
                    ('PREV.endsieg_starting_manufacturer', 'THIS')]
                manufacturer = current
            else:
                raise AssertionError(('Unexpected selector effect', n.key))
    execute(effect.children)
    return manufacturer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    root = args.repo
    effects_list = parse((root / 'common/scripted_effects/endsieg_starting_production_mio.txt')
                         .read_text(encoding='utf-8-sig'))
    effects = {n.key: n for n in effects_list}
    assert len(effects) == len(effects_list), 'Duplicate selector definition'
    orgs = {}
    for path in sorted((root / 'common/military_industrial_organization/organizations').glob('*.txt')):
        orgs.update({n.key: n for n in parse(path.read_text(encoding='utf-8-sig')) if n.children})

    def inherits(ident, target, seen=()):
        if ident == target:
            return True
        if ident in seen or ident not in orgs:
            return False
        parent = scalar(orgs[ident], 'include')
        return inherits(parent, target, (*seen, ident)) if parent else False

    checks = 0
    preferred_counts = {}
    german_mios = tuple(dict.fromkeys(GERMAN.values()))
    for suffix, family in PRIORITIES.items():
        effect = effects['endsieg_select_starting_mio_' + suffix]
        loops = [n for n in child(effect, 'if').children
                 if n.key == 'every_military_industrial_organization']
        assert len(loops) == 2, (suffix, 'Need preferred pass and compatible fallback')
        preferred, fallback = map(identifiers, loops)
        assert preferred and preferred <= fallback, suffix
        assert preferred == {ident for ident in fallback if inherits(ident, family)}, suffix
        assert fallback <= orgs.keys(), (suffix, fallback - orgs.keys())
        preferred_counts[suffix] = len(preferred)
        checks += 4
        # Each specialist must win regardless of secondary manufacturers' order.
        for specialist in sorted(preferred):
            assert select(effect, [specialist]) == specialist, (suffix, specialist)
            for secondary in sorted(fallback - preferred):
                for order in ((secondary, specialist), (specialist, secondary)):
                    assert select(effect, order) == specialist, (suffix, order)
                    checks += 1
            checks += 1
        # No preferred company available: preserve the previous compatible fallback.
        for secondary in sorted(fallback - preferred):
            assert select(effect, [secondary]) == secondary, (suffix, secondary)
            checks += 1
        assert select(effect, []) is None
        assert select(effect, german_mios, dlc=False) is None
        checks += 2
        for order in permutations(german_mios):
            assert select(effect, order) == GERMAN[suffix], (suffix, order)
            checks += 1
    # Every existing history call must still resolve to one definition.
    calls = 0
    for path in (root / 'history/units').glob('*.txt'):
        text = path.read_text(encoding='utf-8-sig')
        if 'endsieg_select_starting_mio_' not in text:
            continue
        for n, _ in walk(parse(text)):
            if n.key.startswith('endsieg_select_starting_mio_'):
                assert n.key in effects, (path.name, n.key)
                calls += 1
    print(json.dumps({'passed': True, 'checks': checks, 'resolved_history_calls': calls,
                      'preferred_manufacturers': preferred_counts, 'game_launched': False}, indent=2))


if __name__ == '__main__':
    main()
