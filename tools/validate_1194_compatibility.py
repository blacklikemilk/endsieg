"""Check known 1.19.4 compatibility regressions without starting HOI4.

This structural checker is not a replacement for the game parser or a campaign test.
Run with Python 3; no external packages are required.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|\#[^\r\n]*|\?=|!=|<=|>=|[{}=<>]|[^\s{}=<>#!]+')
OPS = {'=', '?=', '!=', '<', '>', '<=', '>='}
DYNAMIC_ALLOWED = {'has_start_date', 'has_focus_tree', 'date'}
RUNTIME_ADVISOR_FIELDS = {'allowed', 'visible', 'available', 'on_add', 'on_remove', 'on_fire'}
MEX_CHARACTERS = {
    'MEX_WW1_alvaro_obregon', 'MEX_emiliano_zapata', 'MEX_pancho_villa',
    'MEX_WW1_eulalio_gutierrez', 'MEX_WW1_francisco_leon_de_la_barra',
    'MEX_adolfo_de_la_huerta',
}


@dataclass
class Node:
    key: str
    op: str
    value: str | list['Node'] | None
    start: int

    @property
    def children(self):
        return self.value if isinstance(self.value, list) else []


def parse(text):
    tokens = [(m[0], m.start()) for m in TOKEN.finditer(text) if not m[0].startswith('#')]
    index = 0

    def block(nested=False):
        nonlocal index
        nodes = []
        while index < len(tokens):
            key, start = tokens[index]
            index += 1
            if key == '}':
                if not nested:
                    raise ValueError('Unexpected closing brace')
                return nodes
            if key == '{':
                raise ValueError('Unexpected anonymous block')
            op, value = '', None
            if index < len(tokens) and tokens[index][0] in OPS:
                op = tokens[index][0]
                index += 1
                if index == len(tokens):
                    raise ValueError('Missing assignment value')
                value = tokens[index][0]
                index += 1
                if value == '{':
                    value = block(True)
                elif value == '}':
                    raise ValueError('Missing assignment value before closing brace')
            nodes.append(Node(key, op, value, start))
        if nested:
            raise ValueError('Unclosed block')
        return nodes

    return block()


def walk(nodes, ancestors=()):
    for node in nodes:
        yield node, ancestors
        yield from walk(node.children, ancestors + (node,))


def scalar(value):
    return value.strip('"') if isinstance(value, str) else value


def inspect(nodes, rel):
    problems = []
    for n, ancestors in walk(nodes):
        if n.key in DYNAMIC_ALLOWED and any(a.key == 'allowed' for a in ancestors):
            if rel.startswith(('common/decisions/', 'common/ai_strategy_plans/')):
                problems.append((n, 'Dynamic trigger in persistent allowed block'))
        if n.key == 'political_power' and n.op in {'<', '>', '<=', '>='}:
            problems.append((n, 'Use has_political_power for a country PP comparison'))
        if n.key == 'recruit_character' and rel.startswith('common/scripted_effects/'):
            problems.append((n, 'Register characters in country history, not a runtime helper'))
        if n.key in RUNTIME_ADVISOR_FIELDS and any(a.key == 'add_advisor_role' for a in ancestors):
            problems.append((n, 'Runtime advisor role contains a database-only trigger/effect'))
        if rel.startswith('common/collections/') and n.key == 'input':
            if str(scalar(n.value)).startswith('country:'):
                problems.append((n, 'Use a native collection/game input, not country:'))
    if rel.startswith('history/countries/'):
        for date in nodes:
            if not re.fullmatch(r'\d{1,4}\.\d{1,2}\.\d{1,2}(?:\.\d{1,2})?', date.key):
                continue
            for child in date.children:
                if child.key in {'else', 'else_if'}:
                    problems.append((child, 'Dated history branch must use the native nested history conditional'))
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--game', type=Path, help='Optional installed HOI4 directory; verifies the native version')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    repo = args.repo.resolve()
    errors, parsed, registration = [], 0, set()
    folders = ['common/decisions', 'common/ai_strategy_plans', 'common/scripted_effects',
               'common/collections', 'history/countries']
    for folder in folders:
        for path in sorted((repo / folder).rglob('*.txt')):
            rel = path.relative_to(repo).as_posix()
            text = path.read_text(encoding='utf-8-sig')
            try:
                nodes = parse(text)
            except ValueError as exc:
                errors.append({'file': rel, 'message': str(exc)})
                continue
            parsed += 1
            for n, message in inspect(nodes, rel):
                errors.append({'file': rel, 'line': text[:n.start].count('\n') + 1, 'message': message})
            if rel == 'history/countries/MEX - Mexico.txt':
                registration = {scalar(n.value) for n, _ in walk(nodes) if n.key == 'recruit_character'}
    # PP checks must cover diplomatic event options as well as decisions.
    for path in (repo / 'events').glob('ww1_mexico_*.txt'):
        rel = path.relative_to(repo).as_posix()
        text = path.read_text(encoding='utf-8-sig')
        for n, message in inspect(parse(text), rel):
            errors.append({'file': rel, 'line': text[:n.start].count('\n') + 1, 'message': message})
    missing = sorted(MEX_CHARACTERS - registration)
    if missing:
        errors.append({'file': 'history/countries/MEX - Mexico.txt', 'message': 'Missing identity registration: ' + ', '.join(missing)})
    descriptor = (repo / 'descriptor.mod').read_text(encoding='utf-8-sig')
    if not re.search(r'(?m)^supported_version\s*=\s*"1\.19\.4"\s*$', descriptor):
        errors.append({'file': 'descriptor.mod', 'message': 'Expected supported_version="1.19.4"'})
    native = None
    if args.game:
        native = json.loads((args.game / 'launcher-settings.json').read_text(encoding='utf-8-sig'))
        if native.get('rawVersion') != '1.19.4.0':
            errors.append({'file': 'launcher-settings.json', 'message': 'Expected installed 1.19.4.0'})
    result = {'result': 'FAIL' if errors else 'PASS', 'parsed_script_files': parsed,
              'registered_mexican_identities': len(MEX_CHARACTERS - set(missing)),
              'native_version': native.get('version') if native else None,
              'errors': errors, 'game_launched': False,
              'limits': 'Structural checks for known regressions; live rendering, campaign execution and AI behavior require game testing.'}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
