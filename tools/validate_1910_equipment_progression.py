"""Validate the WWI equipment curve against an installed vanilla baseline.

This checks definitions, not live combat. Parent links describe model succession;
equipment statistics come from the archetype and explicit model fields.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path

from validate_1194_compatibility import parse


STATS = (
    'defense', 'breakthrough', 'soft_attack', 'hard_attack', 'ap_attack',
    'air_attack', 'hardness', 'armor_value', 'reliability', 'maximum_speed',
    'build_cost_ic',
)
CHAINS = {
    'infantry': [*(f'early_infantry_equipment_{i}' for i in range(6)),
                 'infantry_equipment_0', 'infantry_equipment_1'],
    'artillery': [*(f'ww1_artillery_{i}' for i in range(4)), 'artillery_equipment_1'],
    'anti_air': ['ww1_anti_air_0', 'ww1_anti_air_1', 'anti_air_equipment_1'],
    'anti_tank': ['anti_tank_equipment_0', 'anti_tank_equipment_1'],
}


def definitions(path, group):
    nodes = parse(path.read_text(encoding='utf-8-sig'))
    block = next(n for n in nodes if n.key == group)
    assert len({n.key for n in block.children}) == len(block.children), path
    return {n.key: n for n in block.children}


def values(node):
    result = {}
    for n in node.children:
        if n.key in STATS:
            result[n.key] = Decimal(n.value)
        elif n.key == 'resources':
            result['resources'] = {x.key: Decimal(x.value) for x in n.children}
    return result


def profile(defs, name):
    model = defs[name]
    archetype = next((n.value for n in model.children if n.key == 'archetype'), None)
    result = values(defs[archetype]) if archetype else {}
    result.update(values(model))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--vanilla', type=Path, required=True)
    parser.add_argument('--before', type=Path,
                        help='Optional before-image folder to verify later models are unchanged')
    args = parser.parse_args()
    checks = 0
    report = {}
    for family, chain in CHAINS.items():
        rel = Path('common/units/equipment') / f'{family}.txt'
        mod = definitions(args.repo / rel, 'equipments')
        vanilla = definitions(args.vanilla / rel, 'equipments')
        for previous, current in zip(chain, chain[1:]):
            before, after = profile(mod, previous), profile(mod, current)
            for stat in ('defense', 'breakthrough', 'soft_attack', 'hard_attack', 'ap_attack', 'air_attack', 'reliability'):
                assert after[stat] >= before[stat], (current, stat, before[stat], after[stat])
                checks += 1
            assert after['build_cost_ic'] >= before['build_cost_ic'], current
            checks += 1
        endpoints = [chain[-1]] + (['infantry_equipment_0'] if family == 'infantry' else [])
        for name in endpoints:
            actual, expected = profile(mod, name), profile(vanilla, name)
            assert actual == expected, (name, actual, expected)
            checks += len(expected)
        start, end = profile(mod, chain[0]), profile(mod, chain[-1])
        assert start['soft_attack'] < end['soft_attack'], family
        if family == 'anti_air':
            assert start['air_attack'] < end['air_attack'], family
        report[family] = {
            'first': {'id': chain[0], **start},
            'vanilla_endpoint': {'id': chain[-1], **end},
        }
        if args.before:
            original = definitions(args.before / rel, 'equipments')
            for name in original:
                if name in chain:
                    continue
                assert profile(mod, name) == profile(original, name), ('unrelated equipment changed', name)
                checks += 1
    for family, ident, fields in (
        ('artillery', 'artillery', ('defense', 'breakthrough', 'soft_attack', 'hard_attack')),
        ('anti_tank', 'anti_tank', ('defense', 'breakthrough', 'soft_attack', 'hard_attack', 'ap_attack')),
        ('cavalry', 'cavalry', ('breakthrough',)),
    ):
        rel = Path('common/units') / f'{family}.txt'
        mod = definitions(args.repo / rel, 'sub_units')[ident]
        vanilla = definitions(args.vanilla / rel, 'sub_units')[ident]
        for key in fields:
            actual = next(n.value for n in mod.children if n.key == key)
            expected = next(n.value for n in vanilla.children if n.key == key)
            assert Decimal(actual) == Decimal(expected), (ident, key, actual, expected)
            checks += 1
    print(json.dumps({'checks': checks, 'equipment': report, 'game_launched': False},
                     indent=2, default=str))


if __name__ == '__main__':
    main()
