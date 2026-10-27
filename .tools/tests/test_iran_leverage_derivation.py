"""Regression test: Iran's foreign dependence is derived from patron influence, debt is repayable.

The I2 review (slice A) found that `iran_foreign_leverage` was still *stored*: 48
`add_to_variable` / `subtract_from_variable` sites across ten files wrote it, so a
concession could move dependence twice (once in the act, once in the hand-written
line) or not at all, and credit and patronage shared one number.

The accepted repair publishes dependence instead of accumulating it:

    landed = clamp(baseline + (sum of patron influence - influence baseline) * weight, 0, 100)
    total  = clamp(landed + repayable debt, 0, 100)

`iran_recompute_leverage` is the only publisher. This file checks the repair against
the shipped script rather than against a retyped copy of the formula: it parses
`common/scripted_effects/iran_campaign.txt`, `common/scripted_effects/
iran_great_game_acts.txt`, `common/script_constants/iran_campaign.txt`, the seven
Iran decision files, both Iran event files and the two chapter focus files, then
executes the parsed blocks under declared country state.

Checks:

    A. the publisher exists, is the only writer of both derived values, clamps the
       influences before deriving, and is called from `iran_refresh_mechanics`
       before the dependence spirit test and from the monthly drift;
    B. census: every remaining write of `iran_foreign_leverage` in Iran content is
       either the publisher, the three chapter openings, or the one-time baseline
       capture - no raw aggregate writer survives in a decision, event or focus, and
       every write of the repayable debt sits in a body that republishes the
       dependence spirit;
    C. behaviour, by executing parsed source: the 1910/1919/1936 openings, the
       fractional 7.5 step, capped influence, both clamps, credit gain, repayment
       with and without debt, all sixteen patron acts and both leading-patron ties,
       repeated refreshes, monthly drift, a chapter transition, one-time
       initialisation of an already-active country, the 40-point dependence
       boundary, both 71/72 payments, and the spirit following a debt payment on
       both decisions and on the American mission;
    D. negatives: the pre-edit aggregate writer, a restored paired write, an
       unpaired writer left on the aggregate, a refresh without the recompute, a
       repayment gate on the aggregate, a duplicated 71/72 concession, an unguarded
       baseline capture, a debt payment without its refresh and a credit reward that
       only recomputes must each fail for their own defect.

Run from the repository root:

    python .tools/tests/test_iran_leverage_derivation.py            # exit 0 = pass
    python .tools/tests/test_iran_leverage_derivation.py --detail   # every check

This is a source check. It proves what the script says when the parsed blocks are
executed under a declared country state. It does not prove what the engine does in a
running campaign, and no game is launched.
"""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EFFECTS = 'common/scripted_effects/iran_campaign.txt'
ACTS = 'common/scripted_effects/iran_great_game_acts.txt'
CONSTANTS = 'common/script_constants/iran_campaign.txt'
DECISIONS = [
    'common/decisions/iran_campaign.txt',
    'common/decisions/iran_foreign_agreements.txt',
    'common/decisions/iran_oil_settlement.txt',
    'common/decisions/iran_great_powers.txt',
    'common/decisions/iran_great_game.txt',
    'common/decisions/iran_focus_interwar_b.txt',
    'common/decisions/iran_focus_ww1.txt',
]
EVENTS = ['events/iran_campaign.txt', 'events/iran_focus_interwar.txt']
FOCUS = ['common/national_focus/iran_ww1.txt', 'common/national_focus/iran_ww2.txt']

AGG = 'iran_foreign_leverage'
LANDED = 'iran_leverage_landed'
DEBT = 'iran_leverage_debt'
BASELINE = 'iran_leverage_baseline'
INF_BASELINE = 'iran_influence_baseline'
BASELINE_FLAG = 'iran_leverage_baselined'
INFLUENCES = ('iran_british_influence', 'iran_northern_influence', 'iran_german_influence')

DETAIL = '--detail' in sys.argv
CHECKS = []
FAILURES = []


def check(name, ok, detail=''):
    CHECKS.append(name)
    if ok:
        if DETAIL:
            print('PASS %s%s' % (name, (' - ' + detail) if detail else ''))
        return True
    FAILURES.append('%s%s' % (name, (' - ' + detail) if detail else ''))
    print('FAIL %s%s' % (name, (' - ' + detail) if detail else ''))
    return False


# --------------------------------------------------------------------------- parsing

def read(rel):
    return (ROOT / rel).read_bytes().decode('utf-8')


def strip_comments(text):
    return re.sub(r'#[^\n]*', '', text)


def find_block(text, name):
    """Return the body of the first `name = { ... }` block, or None."""
    match = re.search(r'(?m)^[ \t]*%s[ \t]*=[ \t]*\{' % re.escape(name), text)
    if not match:
        return None
    start = match.end()
    depth = 1
    index = start
    while index < len(text):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:index]
        index += 1
    raise ValueError('unclosed block %s' % name)


def find_event(text, event_id):
    """Return the body text of the `country_event = { ... }` block whose id is event_id."""
    match = re.search(r'(?m)^[ \t]*id[ \t]*=[ \t]*%s\b' % re.escape(event_id), text)
    if not match:
        return None
    opening = text.rfind('{', 0, match.start())
    if opening < 0:
        return None
    depth = 1
    index = opening + 1
    start = index
    while index < len(text):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:index]
        index += 1
    return None


def complete_effect(text, name):
    """Return the `complete_effect` ops of the decision block `name`."""
    body = find_block(text, name)
    if body is None:
        return None
    for key, value in parse(body):
        if key == 'complete_effect' and isinstance(value, list):
            return value
    return None


def focus_reward(text, ident):
    """Return the `completion_reward` ops of the focus whose id is `ident`."""
    match = re.search(r'(?m)^[ \t]*id[ \t]*=[ \t]*%s\b' % re.escape(ident), text)
    if not match:
        return None
    opening = text.rfind('{', 0, match.start())
    if opening < 0:
        return None
    depth = 1
    index = opening + 1
    while index < len(text):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                break
        index += 1
    for key, value in parse(text[opening + 1:index]):
        if key == 'completion_reward' and isinstance(value, list):
            return value
    return None


def innermost_block(text, offset):
    """Body of the smallest `{ ... }` span containing `offset`."""
    spans = []
    stack = []
    for index, char in enumerate(text):
        if char == '{':
            stack.append(index)
        elif char == '}' and stack:
            start = stack.pop()
            spans.append((start, index))
    best = None
    for start, end in spans:
        if start < offset < end and (best is None or end - start < best[1] - best[0]):
            best = (start, end)
    return text[best[0]:best[1]] if best else ''


def parse(body):
    """Parse a Clausewitz body into a list of (key, value) pairs; value is str or list."""
    ops = []
    index = 0
    length = len(body)
    while index < length:
        while index < length and body[index] in ' \t\r\n':
            index += 1
        if index >= length:
            break
        start = index
        while index < length and body[index] not in ' \t\r\n={}':
            index += 1
        key = body[start:index]
        while index < length and body[index] in ' \t\r\n':
            index += 1
        has_equals = False
        if index < length and body[index] == '=':
            index += 1
            has_equals = True
            while index < length and body[index] in ' \t\r\n':
                index += 1
        elif index < length and body[index] in '<>':
            operator = body[index]
            index += 1
            if index < length and body[index] == '=':
                operator += '='
                index += 1
            while index < length and body[index] in ' \t\r\n':
                index += 1
            start = index
            while index < length and body[index] not in ' \t\r\n}':
                index += 1
            ops.append((key, operator + ' ' + body[start:index]))
            continue
        if index < length and body[index] == '{':
            inner, index = read_block(body, index + 1)
            ops.append((key, inner))
        elif index < length and body[index] == '}':
            ops.append(('_bare', key))
        else:
            start = index
            while index < length and body[index] not in ' \t\r\n}':
                index += 1
            if start == index:
                ops.append(('_bare', key))
            else:
                ops.append((key, body[start:index]))
    return ops


def read_block(body, index):
    depth = 1
    start = index
    while index < len(body):
        char = body[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return parse(body[start:index]), index + 1
        index += 1
    raise ValueError('unclosed inner block')


def constants():
    body = find_block(strip_comments(read(CONSTANTS)), 'iran_story')
    values = {}
    for key, value in parse(body):
        if isinstance(value, list):
            continue
        try:
            values[key] = float(value)
        except ValueError:
            continue
    return values


# ------------------------------------------------------------------------ execution

class Env:
    def __init__(self, date='1910.1.1', flags=None, ideas=None, equipment=0):
        self.vars = {}
        self.flags = set(flags or ())
        self.ideas = set(ideas or ())
        self.equipment = equipment
        self.date = date
        self.calls = []

    def copy(self):
        other = Env(self.date, self.flags, self.ideas, self.equipment)
        other.vars = dict(self.vars)
        return other


def date_key(value):
    return tuple(int(part) for part in value.split('.'))


def idea_names(value):
    """Flatten an idea list.

    `remove_ideas = { a b c }` is a block of bare tokens, so the parser returns
    them as key/value pairs of whatever tokens happened to sit next to each other
    (and a `_bare` marker when the count is odd). Both halves of every pair are
    idea names, so both are kept.
    """
    if isinstance(value, str):
        return [value]
    names = []
    for key, item in value:
        if key != '_bare':
            names.append(key)
        if isinstance(item, str):
            names.append(item)
    return names


def compare(left, right, op):
    if op in ('greater_than', '>'):
        return left > right
    if op in ('less_than', '<'):
        return left < right
    if op in ('greater_than_or_equals', '>='):
        return left >= right
    if op in ('less_than_or_equals', '<='):
        return left <= right
    return left == right


class Engine:
    def __init__(self, sources, consts):
        self.sources = sources          # rel path -> text
        self.consts = consts
        self.effects = {}
        for rel in (EFFECTS, ACTS):
            text = strip_comments(sources[rel])
            for match in re.finditer(r'(?m)^([a-z_0-9]+)[ \t]*=[ \t]*\{', text):
                name = match.group(1)
                self.effects[name] = find_block(text, name)

    def value(self, env, token):
        token = token.strip()
        if token.startswith('constant:'):
            key = token.split('.', 1)[1]
            if key not in self.consts:
                raise KeyError(token)
            return self.consts[key]
        try:
            return float(token)
        except ValueError:
            return float(env.vars.get(token, 0))

    def trigger(self, env, ops):
        for key, value in ops:
            if key == 'NOT':
                if self.trigger(env, value):
                    return False
            elif key == 'OR':
                if not any(self.trigger(env, [item]) for item in value):
                    return False
            elif key == 'AND':
                if not self.trigger(env, value):
                    return False
            elif key == 'has_country_flag':
                if value not in env.flags:
                    return False
            elif key == 'has_idea':
                if value not in env.ideas:
                    return False
            elif key == 'country_exists':
                if value not in ('ENG', 'SOV', 'GER', 'USA', 'RUS'):
                    return False
            elif key == 'has_equipment':
                checks = value if isinstance(value, list) else [(None, value)]
                for _, item in checks:
                    required = re.search(r'>[ \t]*(\d+)', str(item))
                    if required and env.equipment <= int(required.group(1)):
                        return False
            elif key == 'check_variable':
                if isinstance(value, str):
                    match = re.search(r'(\w+)\s*([<>]=?)\s*(\S+)', value)
                    left = float(env.vars.get(match.group(1), 0))
                    if not compare(left, self.value(env, match.group(3)), match.group(2)):
                        return False
                else:
                    fields = dict((k, v) for k, v in value if isinstance(v, str))
                    left = float(env.vars.get(fields.get('var'), 0))
                    if not compare(left, self.value(env, fields.get('value', '0')),
                                   fields.get('compare', 'equals')):
                        return False
            elif key == 'date':
                if isinstance(value, str):
                    op = '>' if '>' in value else '<'
                    target = value.replace('>', '').replace('<', '').strip()
                    left = date_key(env.date)
                    right = date_key(target)
                    if op == '>' and not left > right:
                        return False
                    if op == '<' and not left < right:
                        return False
                else:
                    passed = False
                    for item in value:
                        op = '>' if item[0] == 'date' else '<'
                        target = item[1]
                    return passed
            elif key in ('original_tag', 'has_dlc', 'has_war'):
                return True
            elif key == 'always':
                if value != 'yes':
                    return False
            elif key in ('is_subject', 'has_capitulated'):
                return False
            else:
                return False
        return True

    def run(self, env, ops, depth=0):
        if depth > 40:
            raise RecursionError('effect recursion')
        index = 0
        while index < len(ops):
            key, value = ops[index]
            index += 1
            if key == 'hidden_effect':
                self.run(env, value, depth + 1)
            elif key in ('if', 'else_if'):
                branch = value
                matched = False
                while True:
                    fields = dict((k, v) for k, v in branch if isinstance(v, list))
                    if not matched and self.trigger(env, fields.get('limit', [])):
                        matched = True
                        self.run(env, [item for item in branch if item[0] != 'limit'], depth + 1)
                    if index < len(ops) and ops[index][0] in ('else_if', 'else'):
                        kind, following = ops[index]
                        index += 1
                        if kind == 'else':
                            if not matched:
                                self.run(env, following, depth + 1)
                            break
                        branch = following
                        continue
                    break
            elif key == 'else':
                self.run(env, value, depth + 1)
            elif key == 'set_variable':
                name, raw = self.variable_block(value)
                env.vars[name] = self.value(env, raw)
            elif key == 'add_to_variable':
                name, raw = self.variable_block(value)
                env.vars[name] = env.vars.get(name, 0) + self.value(env, raw)
            elif key == 'subtract_from_variable':
                name, raw = self.variable_block(value)
                env.vars[name] = env.vars.get(name, 0) - self.value(env, raw)
            elif key == 'multiply_variable':
                fields = dict((k, v) for k, v in value if isinstance(v, str))
                env.vars[fields['var']] = env.vars.get(fields['var'], 0) * self.value(env, fields['value'])
            elif key == 'divide_variable':
                fields = dict((k, v) for k, v in value if isinstance(v, str))
                env.vars[fields['var']] = env.vars.get(fields['var'], 0) / self.value(env, fields['value'])
            elif key == 'clamp_variable':
                fields = dict((k, v) for k, v in value if isinstance(v, str))
                current = env.vars.get(fields['var'], 0)
                low = self.value(env, fields.get('min', '0'))
                high = self.value(env, fields.get('max', '100'))
                env.vars[fields['var']] = max(low, min(high, current))
            elif key == 'set_country_flag':
                env.flags.add(value)
            elif key == 'clr_country_flag':
                env.flags.discard(value)
            elif key in ('add_ideas', 'remove_ideas'):
                for idea in idea_names(value):
                    if key == 'add_ideas':
                        env.ideas.add(idea)
                    else:
                        env.ideas.discard(idea)
            elif key in ('add_equipment_to_stockpile', 'add_political_power', 'add_stability',
                         'add_war_support', 'army_experience', 'add_fuel', 'add_opinion_modifier',
                         'add_timed_idea', 'set_politics', 'add_popularity', 'promote_character',
                         'mark_focus_tree_layout_dirty', 'custom_effect_tooltip', 'load_focus_tree',
                         'complete_national_focus', 'add_extra_state_shared_building_slots',
                         'add_building_construction', 'add_resource', 'build_railway', 'add_manpower',
                         'add_research_slot', 'give_guarantee', 'country_event', 'add_days_mission_timeout',
                         'remove_mission', 'set_global_flag', 'set_variable_tooltip', 'add_mission'):
                pass
            elif key in self.effects and value == 'yes':
                env.calls.append(key)
                self.run(env, parse(self.effects[key]), depth + 1)
            elif key == 'PER' and isinstance(value, list):
                self.run(env, value, depth + 1)
            elif key in ('PER_bop_sync', 'PER_bop_sign_agreement', 'iran_coup_init',
                         'iran_route_chapter', 'iran_apply_historical_start',
                         'PER_bop_push_crown_small', 'iran_negotiation_tick',
                         'PER_bop_resurgence_check', 'iran_settle_pahlavi'):
                if key in self.effects:
                    env.calls.append(key)
                    self.run(env, parse(self.effects[key]), depth + 1)
            elif isinstance(value, list):
                # unknown scope block (state id, capital_scope, ENG, ...): not Iran's variables
                pass

    @staticmethod
    def variable_block(value):
        if not isinstance(value, list):
            raise ValueError('expected block')
        fields = [(k, v) for k, v in value if isinstance(v, str)]
        if fields and fields[0][0] == 'var':
            return fields[0][1], fields[1][1]
        return fields[0][0], fields[0][1]


# ---------------------------------------------------------------------------- cases

def fresh_iran(engine, date, aggregate, influences=None):
    env = Env(date=date, flags={BASELINE_FLAG} if aggregate is None else set())
    if influences:
        for name, amount in influences.items():
            env.vars[name] = amount
    return env


def run_file_block(engine, env, rel, name):
    body = find_block(strip_comments(engine.sources[rel]), name)
    if body is None:
        raise KeyError('%s not in %s' % (name, rel))
    engine.run(env, parse(body))
    return env


def opening(engine, date):
    """Execute the shipped chapter initialisation for a bookmark date."""
    env = Env(date=date, flags=set())
    body = find_block(strip_comments(engine.sources[EFFECTS]), 'iran_initialize_campaign')
    engine.run(env, parse(body))
    return env


def main():
    sources = {}
    for rel in [EFFECTS, ACTS, CONSTANTS] + DECISIONS + EVENTS + FOCUS:
        sources[rel] = read(rel)
    consts = constants()
    engine = Engine(sources, consts)
    weight = consts['leverage_derivation_weight']
    floor = consts['authority_floor']
    cap = consts['authority_cap']

    refresh = find_block(strip_comments(sources[EFFECTS]), 'iran_refresh_mechanics')
    recompute = find_block(strip_comments(sources[EFFECTS]), 'iran_recompute_leverage')
    init = find_block(strip_comments(sources[EFFECTS]), 'iran_initialize_campaign')
    tick = find_block(strip_comments(sources[EFFECTS]), 'iran_influence_tick')

    # ---------------------------------------------------------------- A: structure
    check('A1 publisher exists', recompute is not None)
    check('A2 weight is 0.5', weight == 0.5, repr(weight))
    check('A3 refresh calls the publisher before the dependence spirit',
          refresh.index('iran_recompute_leverage') < refresh.index('leverage_dependency'))
    check('A4 publisher does not call refresh (no recursion)',
          'iran_refresh_mechanics' not in recompute)
    check('A5 publisher clamps influences before deriving',
          recompute.index('clamp_variable = { var = iran_british_influence')
          < recompute.index('set_variable = { iran_leverage_landed'))
    check('A6 monthly drift republishes', 'iran_recompute_leverage = yes' in tick)
    check('A7 baseline captured after the chapter openings, before publication',
          init.index('iran_leverage_baseline_init') > init.index('leverage_late_start')
          and init.index('iran_leverage_baseline_init') < init.index('iran_refresh_mechanics'))

    # ------------------------------------------------------------- B: writer census
    def census(src):
        """Every line that writes the aggregate across the owned decision, event and focus files."""
        hits = []
        for rel in DECISIONS + EVENTS + FOCUS:
            for number, line in enumerate(strip_comments(src[rel]).splitlines(), 1):
                if AGG in line and re.search(
                        r'(set_variable|add_to_variable|subtract_from_variable|multiply_variable'
                        r'|clamp_variable)[^\n]*\b%s\b' % AGG, line):
                    hits.append('%s:%d' % (rel, number))
        return hits

    raw_writers = census(sources)
    check('B1 no aggregate writer outside the publisher', not raw_writers, ', '.join(raw_writers[:4]))

    publisher_text = strip_comments(sources[EFFECTS])
    writes = [line for line in publisher_text.splitlines()
              if re.search(r'(set_variable|add_to_variable|subtract_from_variable)[^\n]*\b%s\b' % AGG, line)]
    check('B2 the aggregate is written only by the publisher, the baseline capture and the openings',
          len(writes) == 6, '%d writes' % len(writes))

    # every one of those writes must sit inside the publisher, the baseline capture or a chapter opening
    allowed_blocks = [
        find_block(strip_comments(sources[EFFECTS]), 'iran_recompute_leverage') or '',
        find_block(strip_comments(sources[EFFECTS]), 'iran_leverage_baseline_init') or '',
        find_block(strip_comments(sources[EFFECTS]), 'iran_initialize_campaign') or '',
    ]
    inside = 0
    for block in allowed_blocks:
        for line in block.splitlines():
            if re.search(r'(set_variable|add_to_variable|subtract_from_variable)[^\n]*\b%s\b' % AGG, line):
                inside += 1
    check('B2b every aggregate write is inside a declared block', inside == len(writes),
          '%d inside, %d total' % (inside, len(writes)))

    check('B3 acts no longer book leverage', not re.search(r'foreign_leverage', strip_comments(sources[ACTS])))

    landed_writes = [line for line in strip_comments(sources[EFFECTS]).splitlines()
                     if re.search(r'(set_variable|add_to_variable|subtract_from_variable|multiply_variable'
                                  r'|clamp_variable)[^\n]*\b%s\b' % LANDED, line)]
    landed_inside = [line for line in recompute.splitlines()
                     if re.search(r'(set_variable|add_to_variable|subtract_from_variable|multiply_variable'
                                  r'|clamp_variable)[^\n]*\b%s\b' % LANDED, line)]
    check('B4 the influence-held value is written only inside the publisher',
          bool(landed_writes) and len(landed_writes) == len(landed_inside),
          '%d in the file, %d in the publisher' % (len(landed_writes), len(landed_inside)))

    # B5: a debt change is published by a refresh, not by the publisher alone. The
    # dependence idea is toggled only inside `iran_refresh_mechanics`, so a body that
    # moves debt and stops at `iran_recompute_leverage` can cross the threshold and
    # leave the spirit on the old band.
    stale_band = []
    for rel in DECISIONS + EVENTS + FOCUS:
        text = strip_comments(sources[rel])
        for match in re.finditer(
                r'(?m)^[ \t]*(?:add_to_variable|subtract_from_variable|set_variable)'
                r'[ \t]*=[ \t]*\{[ \t]*%s\b' % DEBT, text):
            block = innermost_block(text, match.start())
            if 'iran_refresh_mechanics' not in block:
                stale_band.append('%s:%d' % (rel, text[:match.start()].count('\n') + 1))
    check('B5 every debt change republishes the dependence spirit', not stale_band,
          ', '.join(stale_band[:4]))
    check('B5b the effects-file debt capture runs inside the publisher chain',
          bool(recompute)
          and recompute.index('iran_leverage_baseline_init')
          < recompute.index('set_variable = { %s' % LANDED))

    # -------------------------------------------------------------- C: behaviour
    for date, expected in (('1910.1.1', 60), ('1919.6.1', 40), ('1936.6.1', 30)):
        env = opening(engine, date)
        check('C1 %s opens at %s' % (date, expected),
              abs(env.vars[AGG] - expected) < 0.001 and abs(env.vars[LANDED] - expected) < 0.001
              and env.vars[DEBT] == 0,
              'aggregate %s landed %s debt %s' % (env.vars.get(AGG), env.vars.get(LANDED), env.vars.get(DEBT)))
        check('C2 %s captures its baseline once' % date,
              env.vars[BASELINE] == expected and BASELINE_FLAG in env.flags)

    env = opening(engine, '1910.1.1')
    env.vars['iran_british_influence'] += 15
    engine.run(env, parse(recompute))
    check('C3 fifteen influence adds 7.5 (fixed point, not 7)',
          abs(env.vars[LANDED] - 67.5) < 0.001 and abs(env.vars[AGG] - 67.5) < 0.001,
          '%s' % env.vars[LANDED])

    clamp = opening(engine, '1910.1.1')
    clamp.vars[BASELINE] = 100
    clamp.vars[INF_BASELINE] = 85
    clamp.vars['iran_british_influence'] = 125
    clamp.vars['iran_northern_influence'] = 0
    clamp.vars['iran_german_influence'] = 0
    clamp.vars[DEBT] = 10
    engine.run(clamp, parse(recompute))
    check('C4 the upper clamp holds at 100 while the debt stays whole',
          clamp.vars[LANDED] == 100 and clamp.vars[DEBT] == 10 and clamp.vars[AGG] == 100,
          'landed %s debt %s aggregate %s' % (clamp.vars[LANDED], clamp.vars[DEBT], clamp.vars[AGG]))

    clamp.vars[BASELINE] = 0
    clamp.vars[DEBT] = 0
    clamp.vars['iran_british_influence'] = 0
    engine.run(clamp, parse(recompute))
    check('C5 the lower clamp holds at 0', clamp.vars[LANDED] == 0 and clamp.vars[AGG] == 0,
          'landed %s' % clamp.vars[LANDED])

    capped = opening(engine, '1910.1.1')
    capped.vars['iran_british_influence'] = 96
    engine.run(capped, parse(recompute))
    before = capped.vars[LANDED]
    engine.run(capped, parse(engine.effects['iran_concede_british_small']))
    check('C6 a capped concession cannot manufacture dependence',
          abs(capped.vars['iran_british_influence'] - 100) < 0.001
          and abs(capped.vars[LANDED] - (before + 4 * weight)) < 0.001,
          'influence %s landed %s' % (capped.vars['iran_british_influence'], capped.vars[LANDED]))

    credit = opening(engine, '1910.1.1')
    body14 = find_event(strip_comments(sources[EVENTS[0]]), 'iran_campaign.14')
    borrow = [item for item in parse(body14)
              if item[0] == 'option' and 'iran_campaign.14.a' in str(item[1])]
    check('C7a event 14 keeps a credit option', len(borrow) == 1)
    engine.run(credit, [item for item in borrow[0][1]
                        if item[0] not in ('name', 'trigger', 'ai_chance')])
    check('C7 credit adds repayable debt without moving influence-held dependence',
          credit.vars[LANDED] == 60 and abs(credit.vars[AGG] - 70) < 0.001,
          'landed %s aggregate %s' % (credit.vars[LANDED], credit.vars[AGG]))

    repay_body = find_block(strip_comments(sources[DECISIONS[0]]), 'iran_repay_foreign_credit')
    check('C8 repayment is gated on repayable debt, not the aggregate',
          'iran_leverage_debt' in repay_body and
          not re.search(r'(visible|available)[^\n]*iran_foreign_leverage', repay_body))
    payer = credit.copy()
    payer.equipment = 1000
    for key, value in parse(repay_body):
        if key == 'complete_effect':
            engine.run(payer, value)
    check('C9 repayment consumes the debt', abs(payer.vars[DEBT]) < 0.001 and payer.vars[AGG] == 60)
    payer.vars[DEBT] = 4
    engine.run(payer, parse(recompute))
    check('C10 less debt than the payment is refused by the trigger',
          engine.trigger(payer, [item for item in parse(repay_body) if item[0] == 'available'][0][1])
          is False)

    # acts: every patron, both tiers, both directions, plus the leading ties
    for act, patron, tier in (
            ('iran_concede_british_small', 'iran_british_influence', 'small'),
            ('iran_concede_northern_small', 'iran_northern_influence', 'small'),
            ('iran_concede_german_small', 'iran_german_influence', 'small'),
            ('iran_concede_british_large', 'iran_british_influence', 'large'),
            ('iran_concede_northern_large', 'iran_northern_influence', 'large'),
            ('iran_concede_german_large', 'iran_german_influence', 'large')):
        delta = consts['concede_%s_influence' % tier]
        env = opening(engine, '1936.6.1')
        env.vars[patron] = 40
        engine.run(env, parse(recompute))
        before = env.vars[LANDED]
        engine.run(env, parse(engine.effects[act]))
        check('C11 %s moves dependence with influence' % act,
              abs(env.vars[patron] - (40 + delta)) < 0.001
              and abs(env.vars[LANDED] - (before + delta * weight)) < 0.001,
              'influence %s landed %s' % (env.vars[patron], env.vars[LANDED]))
    for act, patron, tier in (
            ('iran_reclaim_british_small', 'iran_british_influence', 'small'),
            ('iran_reclaim_northern_large', 'iran_northern_influence', 'large'),
            ('iran_reclaim_german_large', 'iran_german_influence', 'large')):
        delta = -consts['reclaim_%s_influence' % tier]
        env = opening(engine, '1936.6.1')
        env.vars[patron] = 40
        engine.run(env, parse(recompute))
        before = env.vars[LANDED]
        engine.run(env, parse(engine.effects[act]))
        check('C12 %s moves dependence with influence' % act,
              abs(env.vars[patron] - (40 + delta)) < 0.001
              and abs(env.vars[LANDED] - (before + delta * weight)) < 0.001,
              'influence %s landed %s' % (env.vars[patron], env.vars[LANDED]))

    for act, patron, rival in (
            ('iran_concede_leading_small', 'iran_british_influence', 'iran_northern_influence'),
            ('iran_reclaim_leading_large', 'iran_northern_influence', 'iran_british_influence')):
        env = opening(engine, '1936.6.1')
        env.vars['iran_british_influence'] = 50
        env.vars['iran_northern_influence'] = 50
        env.vars['iran_german_influence'] = 50
        engine.run(env, parse(recompute))
        before = env.vars[LANDED]
        engine.run(env, parse(engine.effects[act]))
        moved = env.vars['iran_british_influence'] - 50
        check('C13 %s resolves a three-way tie to Britain' % act, abs(moved) > 0.001,
              'british moved %s' % moved)
        check('C14 %s republished dependence' % act,
              abs(env.vars[LANDED] - (before + moved * weight)) < 0.001)

    env = opening(engine, '1936.6.1')
    first = dict(env.vars)
    engine.run(env, parse(refresh))
    engine.run(env, parse(refresh))
    check('C15 repeated refreshes are idempotent',
          all(abs(env.vars[key] - first[key]) < 0.001 for key in (AGG, LANDED, DEBT, BASELINE)))

    drift = opening(engine, '1919.6.1')
    drift.flags.add('iran_customs_reformed')
    drift.vars['iran_british_influence'] = 70
    engine.run(drift, parse(tick))
    check('C16 monthly drift republishes after it moves values',
          abs(drift.vars[LANDED] - (40 + (70 + 40 - 85) * weight)) < 0.001,
          'landed %s' % drift.vars[LANDED])

    chapter = opening(engine, '1910.1.1')
    chapter.date = '1919.6.1'
    chapter.vars['iran_british_influence'] = 60
    engine.run(chapter, parse(refresh))
    check('C17 a chapter transition does not re-base the baselines',
          chapter.vars[BASELINE] == 60 and chapter.vars[INF_BASELINE] == 85,
          'baseline %s influence baseline %s' % (chapter.vars[BASELINE], chapter.vars[INF_BASELINE]))

    legacy = Env(date='1925.1.1', flags={'iran_campaign_active'})
    legacy.vars.update({AGG: 55, 'iran_british_influence': 40, 'iran_northern_influence': 30,
                        'iran_german_influence': 5})
    engine.run(legacy, parse(recompute))
    check('C18 an active country without baselines keeps its current dependence once',
          abs(legacy.vars[BASELINE] - 55) < 0.001 and abs(legacy.vars[LANDED] - 55) < 0.001
          and legacy.vars[DEBT] == 0 and BASELINE_FLAG in legacy.flags,
          'baseline %s landed %s' % (legacy.vars[BASELINE], legacy.vars[LANDED]))

    dependency = consts['leverage_dependency']
    for delta, expected in ((-2, False), (0, True), (2, True)):
        band = opening(engine, '1936.6.1')
        target = band.vars[INF_BASELINE] + (dependency + delta - band.vars[BASELINE]) / weight
        band.vars['iran_british_influence'] = target - band.vars['iran_northern_influence']
        engine.run(band, parse(refresh))
        check('C19 dependence spirit at %s against the %s threshold'
              % (band.vars[LANDED], dependency),
              ('iran_foreign_dependence' in band.ideas) == expected)

    for option, patron, act in (
            ('iran_campaign.71', 'iran_british_influence', 'iran_concede_british_small'),
            ('iran_campaign.72', 'iran_northern_influence', 'iran_concede_northern_small')):
        env = opening(engine, '1919.6.1')
        body = find_event(strip_comments(sources[EVENTS[0]]), option)
        paid = [item for item in parse(body) if item[0] == 'option' and 'demand_paid' in str(item[1])]
        check('C20 %s has a paying option' % option, len(paid) == 1)
        before = env.vars[patron]
        engine.run(env, paid[0][1])
        check('C21 %s payment is a concession, exactly once' % option,
              abs(env.vars[patron] - (before + consts['concede_small_influence'])) < 0.001
              and env.calls.count(act) == 1,
              'influence %s calls %s' % (env.vars[patron], env.calls))

    # C22-C24: a debt payment must move the published band, not only the aggregate.
    # Landed 32 with 10 of credit sits at 42, above the 40 threshold; settling 5 of the
    # debt takes dependence to 37, where the spirit has to come off again.
    def band_env():
        env = opening(engine, '1936.6.1')
        env.vars['iran_british_influence'] = 49          # 30 + 4 * 0.5 = 32 landed
        env.vars[DEBT] = 10
        engine.run(env, env_body(engine, 'iran_refresh_mechanics'))
        return env

    customs = band_env()
    check('C22a the customs reform opens above the dependence threshold',
          abs(customs.vars[LANDED] - 32) < 0.001 and abs(customs.vars[AGG] - 42) < 0.001
          and 'iran_foreign_dependence' in customs.ideas,
          'landed %s aggregate %s ideas %s' % (customs.vars[LANDED], customs.vars[AGG],
                                               sorted(customs.ideas)))
    engine.run(customs, complete_effect(strip_comments(sources[DECISIONS[1]]),
                                        'iran_reform_customs_service') or [])
    check('C22 the customs reform republishes the dependence spirit after paying debt',
          abs(customs.vars[DEBT] - 5) < 0.001 and abs(customs.vars[AGG] - 37) < 0.001
          and 'iran_foreign_dependence' not in customs.ideas,
          'debt %s aggregate %s ideas %s' % (customs.vars[DEBT], customs.vars[AGG],
                                             sorted(customs.ideas)))

    bank = band_env()
    engine.run(bank, complete_effect(strip_comments(sources[DECISIONS[1]]),
                                     'iran_found_national_bank') or [])
    check('C23 the national bank republishes the dependence spirit after paying debt',
          abs(bank.vars[DEBT] - 5) < 0.001 and abs(bank.vars[AGG] - 37) < 0.001
          and 'iran_foreign_dependence' not in bank.ideas,
          'debt %s aggregate %s ideas %s' % (bank.vars[DEBT], bank.vars[AGG],
                                             sorted(bank.ideas)))

    mission = opening(engine, '1936.6.1')
    mission.vars['iran_british_influence'] = 49
    engine.run(mission, env_body(engine, 'iran_refresh_mechanics'))
    check('C24a the American mission opens below the dependence threshold',
          abs(mission.vars[AGG] - 32) < 0.001 and 'iran_foreign_dependence' not in mission.ideas,
          'aggregate %s' % mission.vars[AGG])
    engine.run(mission, focus_reward(strip_comments(sources[FOCUS[1]]),
                                     'IR3_american_mission') or [])
    check('C24 the American mission republishes the dependence spirit after taking credit',
          abs(mission.vars[DEBT] - 10) < 0.001 and abs(mission.vars[AGG] - 42) < 0.001
          and 'iran_foreign_dependence' in mission.ideas,
          'debt %s aggregate %s ideas %s' % (mission.vars[DEBT], mission.vars[AGG],
                                             sorted(mission.ideas)))

    # --------------------------------------------------------------- D: negatives
    def replace(src, old, new):
        if old not in src:
            raise SystemExit('mutation anchor missing: %r' % old[:60])
        return src.replace(old, new, 1)

    # D1: the pre-edit paired act write, restored after the publisher. The old line booked
    # dependence beside the influence it came from, so one concession moved it twice.
    copy1 = dict(sources)
    copy1[ACTS] = replace(copy1[ACTS], '\t\tiran_recompute_leverage = yes',
                          '\t\tiran_recompute_leverage = yes\n'
                          '\t\tadd_to_variable = { iran_foreign_leverage = constant:iran_story.leverage_gain }')
    check('D1 a restored paired act write is caught by the acts census',
          bool(re.search(r'foreign_leverage', strip_comments(copy1[ACTS]))))
    broken1 = Engine(copy1, consts)
    env = opening(broken1, '1936.6.1')
    env.vars['iran_british_influence'] = 40
    broken1.run(env, parse(broken1.effects['iran_concede_british_small']))
    clean = opening(engine, '1936.6.1')
    clean.vars['iran_british_influence'] = 40
    engine.run(clean, parse(engine.effects['iran_concede_british_small']))
    check('D1b the double-booked aggregate is caught',
          abs(env.vars[AGG] - (clean.vars[AGG] + consts['leverage_gain'])) < 0.001,
          'mutant %s clean %s' % (env.vars[AGG], clean.vars[AGG]))

    # D2: an unpaired credit writer left on the aggregate instead of the debt
    copy2 = dict(sources)
    copy2[DECISIONS[0]] = replace(copy2[DECISIONS[0]], 'subtract_from_variable = { iran_leverage_debt',
                                  'subtract_from_variable = { iran_foreign_leverage')
    check('D2 an unpaired writer left on the aggregate is caught', bool(census(copy2)),
          ', '.join(census(copy2)[:3]))

    # D3: a refresh that no longer republishes leaves the aggregate on the old band
    copy3 = dict(sources)
    copy3[EFFECTS] = replace(copy3[EFFECTS], '\t\tiran_recompute_leverage = yes\n\t\tclamp_variable = { var = iran_authority',
                             '\t\tclamp_variable = { var = iran_authority')
    broken3 = Engine(copy3, consts)
    env = opening(broken3, '1910.1.1')
    env.vars['iran_british_influence'] = 60
    before = env.vars[AGG]
    broken3.run(env, env_body(broken3, 'iran_refresh_mechanics'))
    check('D3 a refresh without the recompute leaves a stale aggregate', env.vars[AGG] == before,
          'aggregate %s' % env.vars[AGG])

    # D4: the repayment gate put back on the aggregate the player cannot lower by paying
    copy4 = dict(sources)
    copy4[DECISIONS[0]] = replace(
        copy4[DECISIONS[0]],
        'visible = { check_variable = { var = iran_leverage_debt value = 0 compare = greater_than } }',
        'visible = { check_variable = { var = iran_foreign_leverage value = 0 compare = greater_than } }')
    body4 = find_block(strip_comments(copy4[DECISIONS[0]]), 'iran_repay_foreign_credit')
    gate = [item for item in parse(body4) if item[0] == 'visible'][0][1]
    check('D4 a repayment gate on the aggregate is caught',
          AGG in str(gate) and DEBT not in str(gate))

    # D5: the 71 payment conceding twice
    copy5 = dict(sources)
    copy5[EVENTS[0]] = replace(copy5[EVENTS[0]], '\t\tiran_concede_british_small = yes\n\t\tadd_to_variable = { iran_british_standing',
                               '\t\tiran_concede_british_small = yes\n\t\tiran_concede_british_small = yes\n\t\tadd_to_variable = { iran_british_standing')
    broken5 = Engine(copy5, consts)
    env = opening(broken5, '1919.6.1')
    body5 = find_event(strip_comments(copy5[EVENTS[0]]), 'iran_campaign.71')
    paid5 = [item for item in parse(body5) if item[0] == 'option' and 'demand_paid' in str(item[1])]
    broken5.run(env, paid5[0][1])
    check('D5 a duplicated concession is caught', env.calls.count('iran_concede_british_small') == 2,
          '%d calls' % env.calls.count('iran_concede_british_small'))

    # D6: the baseline captured on every recompute instead of once
    copy6 = dict(sources)
    copy6[EFFECTS] = replace(copy6[EFFECTS],
                             'limit = { NOT = { has_country_flag = iran_leverage_baselined } }',
                             'limit = { always = yes }')
    broken6 = Engine(copy6, consts)
    env = opening(broken6, '1910.1.1')
    env.vars['iran_british_influence'] += 15
    broken6.run(env, env_body(broken6, 'iran_recompute_leverage'))
    check('D6 an unguarded baseline capture is caught', abs(env.vars[LANDED] - 67.5) > 0.1,
          'landed %s' % env.vars[LANDED])

    # D7: the customs payment left without its refresh. The aggregate still moves, the
    # spirit keeps its old band, which is exactly the defect the debt writers had.
    copy7 = dict(sources)
    copy7[DECISIONS[1]] = replace(
        copy7[DECISIONS[1]],
        'subtract_from_variable = { iran_leverage_debt = constant:iran_story.influence_erosion }\n'
        '\t\t\tiran_refresh_mechanics_hidden = yes\n'
        '\t\t\tadd_political_power = -25',
        'subtract_from_variable = { iran_leverage_debt = constant:iran_story.influence_erosion }\n'
        '\t\t\tadd_political_power = -25')
    broken7 = Engine(copy7, consts)
    env = opening(broken7, '1936.6.1')
    env.vars['iran_british_influence'] = 49
    env.vars[DEBT] = 10
    broken7.run(env, env_body(broken7, 'iran_refresh_mechanics'))
    broken7.run(env, complete_effect(strip_comments(copy7[DECISIONS[1]]),
                                     'iran_reform_customs_service'))
    check('D7 a debt payment without its refresh leaves the spirit stale',
          abs(env.vars[DEBT] - 5) < 0.001 and abs(env.vars[AGG] - 42) < 0.001
          and 'iran_foreign_dependence' in env.ideas,
          'debt %s aggregate %s ideas %s' % (env.vars[DEBT], env.vars[AGG], sorted(env.ideas)))

    # D8: the American mission back on the publisher alone, the pre-fix shape. The focus
    # file ships CRLF, so the mutant copy is normalised before the anchor is applied.
    copy8 = dict(sources)
    focus_src = copy8[FOCUS[1]].replace('\r\n', '\n')
    copy8[FOCUS[1]] = replace(
        focus_src,
        'add_to_variable = { iran_leverage_debt = constant:iran_story.leverage_gain }\n'
        '\t\t\thidden_effect = { iran_refresh_mechanics = yes }',
        'add_to_variable = { iran_leverage_debt = constant:iran_story.leverage_gain }\n'
        '\t\t\tiran_recompute_leverage = yes')
    broken8 = Engine(copy8, consts)
    env = opening(broken8, '1936.6.1')
    env.vars['iran_british_influence'] = 49
    broken8.run(env, env_body(broken8, 'iran_refresh_mechanics'))
    broken8.run(env, focus_reward(strip_comments(copy8[FOCUS[1]]), 'IR3_american_mission'))
    check('D8 a credit reward that only recomputes leaves the spirit stale',
          abs(env.vars[AGG] - 42) < 0.001 and 'iran_foreign_dependence' not in env.ideas,
          'aggregate %s ideas %s' % (env.vars[AGG], sorted(env.ideas)))

    print('')
    print('%d checks, %d failures' % (len(CHECKS), len(FAILURES)))
    for failure in FAILURES:
        print('  ' + failure)
    return 1 if FAILURES else 0


def env_body(engine, name):
    return parse(engine.effects.get(name) or find_block(strip_comments(engine.sources[EFFECTS]), name))


if __name__ == '__main__':
    raise SystemExit(main())
