"""Validate interwar support normalization without launching Hearts of Iron IV.

Uses the repository's Clausewitz parser and Python standard library. Tests the
actual technology/effect AST for partial histories, research order, repeated
reconciliation, removed research, and the one-time monthly migration receipt.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal
from itertools import permutations, product
import json
from pathlib import Path

from validate_1194_compatibility import parse, walk, scalar


FAMILIES = {
    'tech_engineers5': ('tech_engineers', ['tech_engineers2', 'tech_engineers3', 'tech_engineers4']),
    'tech_recon5': ('tech_recon', ['tech_recon2', 'tech_recon3', 'tech_recon4']),
    'tech_military_police_5': ('tech_military_police', ['tech_military_police2', 'tech_military_police3', 'tech_military_police4']),
    'tech_maintenance_company5': ('tech_maintenance_company', ['tech_maintenance_company2', 'tech_maintenance_company3', 'tech_maintenance_company4']),
    'marines3': ('marines', ['marines2']),
    'interwar_antiair': ('antiair', ['anti_air3']),
}
UNIT_SCOPES = {
    'engineer', 'recon', 'category_recon', 'military_police',
    'maintenance_company', 'marine', 'anti_air', 'anti_air_brigade',
    'infantry', 'cavalry', 'mountaineers',
}
FINALIZER = 'endsieg_interwar_finalize_unit_offsets'
RECEIPT = 'endsieg_interwar_support_offsets_initialized_v1'


def child(nodes, key):
    return next((node for node in nodes if node.key == key), None)


def numeric(nodes, prefix=()):
    result = {}
    for node in nodes:
        if node.children:
            result.update(numeric(node.children, prefix + (node.key,)))
        elif node.key != 'name':
            result[prefix + (node.key,)] = Decimal(node.value)
    return result


def nonzero(values):
    return {key: value for key, value in values.items() if value}


class Country:
    def __init__(self, effects):
        self.effects = effects
        self.owned = set()
        self.flags = set()
        self.bonuses = defaultdict(Decimal)
        self.variables = defaultdict(Decimal)
        self.dynamic_modifiers = set()
        self.finalizer_calls = 0

    def condition(self, nodes):
        values = []
        for node in nodes:
            if node.key == 'has_tech':
                value = scalar(node.value) in self.owned
            elif node.key == 'has_country_flag':
                value = scalar(node.value) in self.flags
            elif node.key == 'has_dynamic_modifier':
                value = scalar(node.value) in self.dynamic_modifiers
            elif node.key == 'NOT':
                value = not self.condition(node.children)
            elif node.key == 'OR':
                value = any(self.condition([item]) for item in node.children)
            elif node.key == 'AND':
                value = self.condition(node.children)
            else:
                raise ValueError('Unmodeled condition ' + node.key)
            values.append(value)
        return all(values)

    def run(self, nodes):
        previous = False
        for node in nodes:
            if node.key in {'if', 'else_if'}:
                limit = child(node.children, 'limit')
                execute = self.condition(limit.children) and (node.key == 'if' or not previous)
                previous = execute if node.key == 'if' else previous or execute
                if execute:
                    self.run([item for item in node.children if item.key != 'limit'])
            elif node.key == 'add_unit_bonus':
                for key, value in numeric(node.children).items():
                    self.bonuses[key] += value
            elif node.key == 'set_country_flag':
                self.flags.add(scalar(node.value))
            elif node.key == 'clr_country_flag':
                self.flags.discard(scalar(node.value))
            elif node.key in {'set_variable', 'add_to_variable'}:
                for item in node.children:
                    if node.key == 'set_variable':
                        self.variables[item.key] = Decimal(item.value)
                    else:
                        self.variables[item.key] += Decimal(item.value)
            elif node.key == 'add_dynamic_modifier':
                self.dynamic_modifiers.add(scalar(child(node.children, 'modifier').value))
            elif node.key == 'remove_dynamic_modifier':
                self.dynamic_modifiers.discard(scalar(child(node.children, 'modifier').value))
            elif node.key == 'every_country':
                # One modeled country suffices to verify the startup receipt.
                self.run(node.children)
            elif node.key in self.effects:
                if node.key == FINALIZER:
                    self.finalizer_calls += 1
                self.run(self.effects[node.key].children)
            else:
                raise ValueError('Unmodeled effect ' + node.key)

    def reconcile(self):
        self.run(self.effects[FINALIZER].children)

    def totals(self, tech_modifiers, keys):
        result = defaultdict(Decimal)
        for ident in self.owned:
            for key, value in tech_modifiers[ident].items():
                if key in keys:
                    result[key] += value
        for key, value in self.bonuses.items():
            if key in keys:
                result[key] += value
        return nonzero(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    techs = {}
    for rel in ['common/technologies/support.txt', 'common/technologies/infantry.txt', 'common/technologies/artillery.txt']:
        roots = parse((repo / rel).read_text(encoding='utf-8-sig'))
        techs.update({node.key: node for root in roots if root.key == 'technologies' for node in root.children})
    tech_modifiers = {
        ident: numeric([node for node in tech.children if node.key in UNIT_SCOPES])
        for ident, tech in techs.items()
    }
    effects = {}
    for name in ['endsieg_interwar_unit_offsets.txt', 'endsieg_interwar_support_offsets.txt']:
        effects.update({node.key: node for node in parse((repo / 'common/scripted_effects' / name).read_text(encoding='utf-8-sig'))})
    checks = 0
    failures = []

    def check(passed, message):
        nonlocal checks
        checks += 1
        if not passed:
            failures.append(message)

    for endpoint, (prefix, sources) in FAMILIES.items():
        keys = {key for ident in sources for key in tech_modifiers[ident]}
        check(bool(keys), endpoint + ' has source modifiers')
        check(not any(key in keys for key in tech_modifiers[endpoint]), endpoint + ' has no extra1936 combat bonus')
        gates = [endpoint]
        for ident, tech in techs.items():
            year = child(tech.children, 'start_year')
            if ident.startswith(prefix) and year and Decimal(year.value) >= 1936 and ident not in gates:
                gates.append(ident)
        for gate in gates:
            for bits in product([False, True], repeat=len(sources)):
                selected = {ident for ident, bit in zip(sources, bits) if bit}
                country = Country(effects)
                country.owned = {gate} | selected
                country.reconcile()
                expected = {key: value for key, value in tech_modifiers[gate].items() if key in keys and value}
                check(country.totals(tech_modifiers, keys) == expected, gate + ' partial-source cancellation')
                before = dict(country.bonuses)
                country.reconcile()
                check(country.bonuses == before, gate + ' repeat reconciliation')
                for ident in sources:
                    country.owned.add(ident)
                    country.reconcile()
                    check(country.totals(tech_modifiers, keys) == expected, gate + ' later source ' + ident)
                for ident in sources:
                    country.owned.remove(ident)
                    country.reconcile()
                    check(country.totals(tech_modifiers, keys) == expected, gate + ' removed source ' + ident)
        for order in permutations([endpoint] + sources):
            country = Country(effects)
            for ident in order:
                country.owned.add(ident)
                country.reconcile()
            check(not country.totals(tech_modifiers, keys), endpoint + ' research order ' + ', '.join(order))
            country.owned.remove(endpoint)
            country.reconcile()
            expected = defaultdict(Decimal)
            for ident in sources:
                for key, value in tech_modifiers[ident].items():
                    expected[key] += value
            check(country.totals(tech_modifiers, keys) == nonzero(expected), endpoint + ' removal restores source bonuses')
        if endpoint in {'tech_engineers5', 'interwar_antiair'}:
            old_endpoint = 'interwars_infantry_equip2' if endpoint == 'tech_engineers5' else 'howitzer6'
            country = Country(effects)
            country.owned = {old_endpoint} | set(sources)
            country.reconcile()
            check(not country.totals(tech_modifiers, keys), endpoint + ' former endpoint')
            before = dict(country.bonuses)
            country.owned.add(endpoint)
            country.reconcile()
            check(country.bonuses == before, endpoint + ' shared old-save flags avoid double subtraction')
            country.owned.remove(old_endpoint)
            country.reconcile()
            check(not country.totals(tech_modifiers, keys), endpoint + ' new endpoint replaces old gate')

    check(not tech_modifiers['modern_support_weapons'], '1936 modern support has no extra infantry bonus')
    check(not tech_modifiers['infantry_weapons1'], '1936 infantry equipment unlock has no extra unit bonus')
    for endpoint, (_, sources) in FAMILIES.items():
        for ident in [endpoint] + sources:
            callback = child(techs[ident].children, 'on_research_complete')
            check(callback is not None and any(node.key == FINALIZER for node, _ in walk(callback.children)), ident + ' research reconciles offsets')

    on_actions = parse((repo / 'common/on_actions/endsieg_interwar_support_offsets.txt').read_text(encoding='utf-8-sig'))
    on_actions = child(on_actions, 'on_actions').children
    startup = child(child(on_actions, 'on_startup').children, 'effect')
    monthly = child(child(on_actions, 'on_monthly').children, 'effect')
    check(any(node.key == 'every_country' for node in startup.children), 'startup country scope')
    for label, pulse in [('new game', startup), ('old save', monthly)]:
        country = Country(effects)
        country.owned = {endpoint for endpoint in FAMILIES}
        country.run(pulse.children)
        check(RECEIPT in country.flags and country.finalizer_calls == 1, label + ' one-time reconciliation')
        before = dict(country.bonuses)
        country.run(monthly.children)
        check(country.finalizer_calls == 1 and country.bonuses == before, label + ' completed monthly receipt skips work')
    country = Country(effects)
    country.run(monthly.children)
    check(RECEIPT in country.flags and country.finalizer_calls == 1, 'new country monthly receipt')

    report = {'passed': not failures, 'checks': checks, 'failures': failures}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
