"""Regression test: Iran's wartime Great Game demands are era-correct and serialised.

The I2 design review found that `iran_influence_tick` dispatched three wartime
demands — British transit (`iran_campaign.74`), the northern corridor
(`iran_campaign.75`) and the Allied demand over the German mission
(`iran_campaign.76`) — as three independent `if` blocks:

    1. the British branch had no era gate at all, so a Britain at war in 1914
       satisfied it and burned `iran_transit_demand_seen` a full generation
       before the wartime corridor existed;
    2. the northern and Allied branches had no `iran_negotiation_open` guard,
       so a demand could be spent while another negotiation was already on the
       table;
    3. all three could dispatch in the same monthly tick, which put three
       incompatible corridor demands in front of the player on one day.

This file checks the repair against the shipped script rather than against a
retyped copy of it. It parses `common/scripted_effects/iran_campaign.txt`,
`common/scripted_triggers/iran_campaign.txt`, `common/script_constants/
iran_campaign.txt` and `common/on_actions/iran_campaign.txt`, then executes the
parsed `iran_influence_tick` body with the engine's own `if` / `else_if`
precedence: a member of the chain runs only when no earlier member of the same
chain ran.

Checks:

    A. structure: the three demands form one `if` / `else_if` / `else_if` chain
       in source order, the incompatible-obligations branch after it is still an
       independent `if`, and each branch sets only its own seen flag;
    B. era fences: 74 and 76 are fenced at `date > 1940.12.31`, 75 keeps its
       `date > 1941.1.1`;
    C. negotiation: all three branches wait while `iran_negotiation_open` is set;
    D. behaviour, by executing the parsed tick: the 1914 case, the three
       boundary dates, the one-demand-per-tick sequence, the all-seen case, the
       negotiation cases, the shared transit agreement, absent and not-at-war
       patrons, a non-Iran country, and the independent branches that follow the
       chain;
    E. preservation: the three event definitions, their options and their
       `ai_chance` weights, and their existing localisation, are byte-identical
       to the pre-edit revision;
    F. the wiring: `on_monthly_PER` is the hook that calls the effect, and the
       standing-demand helper does not carry the wartime branches.

Every structural or behavioural check is also run against the pre-edit revision
(`BASELINE_REV`) and must reject it, and the behavioural cases are re-run
against in-memory mutants that restore the missing era fence, either missing
negotiation guard, or the independent `if` blocks. A check that passes broken
source proves nothing.

Run from the repository root:

    python .tools/tests/test_iran_wartime_demands.py            # exit 0 = pass
    python .tools/tests/test_iran_wartime_demands.py --detail   # every check

This is a source check. It proves what the script says when the parsed tick is
executed under a declared country state. It does not prove what the engine does
in a running campaign, and no game is launched.
"""

from __future__ import annotations

import io
import re
import subprocess
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EFFECTS_PATH = 'common/scripted_effects/iran_campaign.txt'
TRIGGERS_PATH = 'common/scripted_triggers/iran_campaign.txt'
CONSTANTS_PATH = 'common/script_constants/iran_campaign.txt'
ON_ACTIONS_PATH = 'common/on_actions/iran_campaign.txt'
EVENTS_PATH = 'events/iran_campaign.txt'
LOC_PATH = 'localisation/english/iran_great_powers_l_english.yml'

TICK = 'iran_influence_tick'
STANDING_TICK = 'iran_great_game_tick'

# The pre-edit revision this card started from. Pinned by full object name so a
# mutable HEAD stops being a usable mutant once the repair is committed.
BASELINE_REV = 'ce6247246a18b0c70b36a91747897ee0d463eafd'

BRITISH = 'iran_campaign.74'
NORTHERN = 'iran_campaign.75'
ALLIED = 'iran_campaign.76'
CHAIN = (BRITISH, NORTHERN, ALLIED)

SEEN_FLAG = {
    BRITISH: 'iran_transit_demand_seen',
    NORTHERN: 'iran_soviet_transit_seen',
    ALLIED: 'iran_allied_demand',
}

ERA_FENCE = {
    BRITISH: (1940, 12, 31),
    NORTHERN: (1941, 1, 1),
    ALLIED: (1940, 12, 31),
}

NEGOTIATION_FLAG = 'iran_negotiation_open'
TRANSIT_AGREEMENT = 'iran_agreement_transit_allied'
GERMAN_MISSION = 'iran_agreement_german_mission'
INCOMPATIBLE_EVENT = 'iran_campaign.73'
COMPETING_IDEA = 'iran_competing_concessions'
CAPITULATION_IDEA = 'iran_sovereignty_capitulations'


class Unsupported(Exception):
    """A script shape this check does not model. Failing loudly beats guessing."""


# ---------------------------------------------------------------------------------------------
# Source access
# ---------------------------------------------------------------------------------------------

def read(relative):
    with io.open(ROOT / relative, encoding='utf-8-sig', errors='replace', newline='') as handle:
        return handle.read()


def baseline(relative):
    result = subprocess.run(['git', 'show', '%s:%s' % (BASELINE_REV, relative)],
                            cwd=str(ROOT), capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    if result.returncode != 0:
        raise Unsupported('cannot read %s at %s: %s'
                          % (relative, BASELINE_REV, result.stderr.strip()))
    return result.stdout


# ---------------------------------------------------------------------------------------------
# Minimal Clausewitz reader
# ---------------------------------------------------------------------------------------------

def strip_comments(text):
    return '\n'.join(line.split('#', 1)[0] for line in text.splitlines())


def match_brace(text, start):
    """Text[start] is '{'. Return the index just past its matching '}'."""
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return index + 1
    raise Unsupported('unbalanced braces after offset %d' % start)


def named_block(text, name):
    """Body text of the first `name = { ... }`, or None.

    The search runs over the raw text so match offsets address the same string
    the body is sliced from. Comments are removed later, inside parse().
    """
    match = re.search(r'(?<![\w])%s\s*=\s*\{' % re.escape(name), text)
    if not match:
        return None
    open_index = text.index('{', match.start())
    return text[open_index + 1:match_brace(text, open_index) - 1]


def date_of(text):
    year, month, day = text.split('.')
    return (int(year), int(month), int(day))


def tokens(text):
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in ' \t\r\n':
            index += 1
        elif char in '{}<>=':
            out.append(char)
            index += 1
        else:
            start = index
            while index < len(text) and text[index] not in ' \t\r\n{}<>#=':
                index += 1
            out.append(text[start:index])
    return out


def parse(text):
    """Tokens -> nested list of (key, value) pairs; value is a str or a list."""
    position = 0

    def walk():
        nonlocal position
        entries = []
        while position < len(token_list):
            token = token_list[position]
            if token == '}':
                position += 1
                return entries
            if token == '{':
                position += 1
                entries.append(('{}', walk()))
                continue
            # `date > 1940.12.31` arrives as three tokens; keep the comparison
            # together so the evaluator can answer it.
            if (token == 'date' and position + 2 < len(token_list)
                    and token_list[position + 1] in ('<', '>')
                    and re.fullmatch(r'\d{1,4}\.\d{1,2}\.\d{1,2}', token_list[position + 2])):
                entries.append(('date', ('cmp', token_list[position + 1],
                                         date_of(token_list[position + 2]))))
                position += 3
                continue
            if position + 1 < len(token_list) and token_list[position + 1] == '=':
                key = token
                position += 2
                if position < len(token_list) and token_list[position] == '{':
                    position += 1
                    entries.append((key, walk()))
                else:
                    entries.append((key, token_list[position] if position < len(token_list) else ''))
                    position += 1
                continue
            entries.append((token, None))
            position += 1
        return entries

    token_list = tokens(strip_comments(text))
    return walk()


def sub_blocks(entries, key):
    return [value for name, value in entries if name == key and isinstance(value, list)]


def first_value(entries, key):
    for name, value in entries:
        if name == key and not isinstance(value, list):
            return value
    return None


# ---------------------------------------------------------------------------------------------
# Country state
# ---------------------------------------------------------------------------------------------

class Patron:
    def __init__(self, exists=True, at_war=False):
        self.exists = exists
        self.at_war = at_war


class State:
    def __init__(self, tag='PER', flags=(), date=None, variables=None, ideas=(),
                 patrons=None):
        self.tag = tag
        self.flags = set(flags)
        self.date = date
        self.variables = dict(variables or {})
        self.ideas = set(ideas)
        self.patrons = dict(patrons or {})

    def clone(self):
        return State(self.tag, self.flags, self.date, self.variables, self.ideas,
                     self.patrons)


def patron(state, tag):
    return state.patrons.get(tag)


# ---------------------------------------------------------------------------------------------
# Interpreter: the engine's if / else_if precedence, over parsed source
# ---------------------------------------------------------------------------------------------

class Model:
    """One parsed source tree: the tick body, its scripted triggers and constants."""

    def __init__(self, effects_text, triggers_text=None, constants_text=None):
        body = named_block(effects_text, TICK)
        if body is None:
            raise Unsupported('%s is missing' % TICK)
        self.tick = parse(body)
        self.triggers = {}
        trigger_source = triggers_text if triggers_text is not None else read(TRIGGERS_PATH)
        self.triggers['iran_campaign_country'] = parse(
            named_block(trigger_source, 'iran_campaign_country') or '')
        self.constants = parse_constants(
            constants_text if constants_text is not None else read(CONSTANTS_PATH))

    # -- effects -------------------------------------------------------------------------

    def run_tick(self, state):
        dispatched = []
        self.execute(self.tick, state, dispatched)
        return dispatched

    def execute(self, entries, state, dispatched):
        index = 0
        while index < len(entries):
            key, value = entries[index]
            if key == 'if':
                matched = self.limit_holds(value, state)
                if matched:
                    self.execute(value, state, dispatched)
                cursor = index + 1
                while cursor < len(entries) and entries[cursor][0] in ('else_if', 'else'):
                    member_key, member_body = entries[cursor]
                    if not matched:
                        if member_key == 'else':
                            self.execute(member_body, state, dispatched)
                            matched = True
                        else:
                            matched = self.limit_holds(member_body, state)
                            if matched:
                                self.execute(member_body, state, dispatched)
                    cursor += 1
                index = cursor
                continue
            if key in ('else_if', 'else'):
                raise Unsupported('a dangling %s with no preceding if' % key)
            self.effect(key, value, state, dispatched)
            index += 1

    def limit_holds(self, body, state):
        limits = sub_blocks(body, 'limit')
        if not limits:
            return True
        if len(limits) > 1:
            raise Unsupported('more than one limit in one if body')
        return self.evaluate(limits[0], state)

    def effect(self, key, value, state, dispatched):
        if key == 'limit':
            return
        if key == 'set_country_flag':
            state.flags.add(value)
            return
        if key == 'clr_country_flag':
            state.flags.discard(value)
            return
        if key == 'country_event':
            event_id = first_value(value, 'id')
            if event_id is None:
                raise Unsupported('country_event without an id')
            dispatched.append(event_id)
            return
        if key == 'add_ideas':
            for idea in idea_names(value):
                state.ideas.add(idea)
            return
        if key == 'remove_ideas':
            for idea in idea_names(value):
                state.ideas.discard(idea)
            return
        if key in ('add_to_variable', 'subtract_from_variable'):
            if not isinstance(value, list) or len(value) != 1:
                raise Unsupported('%s with %r' % (key, value))
            name, operand = value[0]
            amount = self.number(operand)
            current = state.variables.get(name, 0)
            state.variables[name] = current + (amount if key == 'add_to_variable' else -amount)
            return
        if key == 'clamp_variable':
            name = first_value(value, 'var')
            low = self.number(first_value(value, 'min')) if first_value(value, 'min') else None
            high = self.number(first_value(value, 'max')) if first_value(value, 'max') else None
            current = state.variables.get(name, 0)
            if low is not None:
                current = max(low, current)
            if high is not None:
                current = min(high, current)
            state.variables[name] = current
            return
        if key == 'hidden_effect':
            self.execute(value, state, dispatched)
            return
        raise Unsupported('unmodelled effect %r' % key)

    def number(self, token):
        if isinstance(token, list):
            raise Unsupported('nested number %r' % (token,))
        if token is None:
            raise Unsupported('missing number')
        if token.startswith('constant:'):
            category, name = token.split(':', 1)[1].split('.', 1)
            if category not in self.constants or name not in self.constants[category]:
                raise Unsupported('unknown constant %s' % token)
            return self.constants[category][name]
        try:
            return float(token)
        except ValueError:
            raise Unsupported('non-numeric operand %r' % token)

    # -- triggers ------------------------------------------------------------------------

    def evaluate(self, nodes, state):
        result = True
        for key, value in nodes:
            if key == 'has_country_flag':
                result = result and (value in state.flags)
            elif key == 'has_idea':
                result = result and (value in state.ideas)
            elif key == 'country_exists':
                existing = patron(state, value)
                result = result and bool(existing and existing.exists)
            elif key == 'iran_campaign_country':
                result = result and self.evaluate(self.triggers['iran_campaign_country'], state)
            elif key == 'original_tag':
                result = result and (state.tag == value)
            elif key == 'date':
                if state.date is None:
                    raise Unsupported('date comparison evaluated without a date')
                operator, operand = value[1], value[2]
                if operator == '>':
                    result = result and state.date > operand
                elif operator == '<':
                    result = result and state.date < operand
                else:
                    raise Unsupported('date operator %r' % operator)
            elif key == 'check_variable':
                result = result and self.check_variable(value, state)
            elif key == 'NOT':
                result = result and not self.evaluate(value, state)
            elif key == 'OR':
                result = result and any(self.evaluate([entry], state) for entry in value)
            elif key == 'AND':
                result = result and self.evaluate(value, state)
            elif key in ('yes', 'no'):
                continue
            elif re.fullmatch(r'[A-Z]{3}', key):
                result = result and self.patron_holds(key, value, state)
            else:
                raise Unsupported('unmodelled trigger %r' % key)
        return result

    def patron_holds(self, tag, nodes, state):
        scope = patron(state, tag)
        if scope is None or not scope.exists:
            return False
        result = True
        for key, value in nodes:
            if key == 'has_war':
                result = result and (scope.at_war == (value == 'yes'))
            else:
                raise Unsupported('unmodelled country scope trigger %r' % key)
        return result

    def check_variable(self, nodes, state):
        name = first_value(nodes, 'var')
        compare = first_value(nodes, 'compare')
        operand = first_value(nodes, 'value')
        if name is None or compare is None or operand is None:
            raise Unsupported('check_variable with %r' % (nodes,))
        current = state.variables.get(name, 0)
        target = self.number(operand)
        if compare == 'greater_than_or_equals':
            return current >= target
        if compare == 'greater_than':
            return current > target
        if compare == 'less_than_or_equals':
            return current <= target
        if compare == 'less_than':
            return current < target
        if compare == 'equals':
            return current == target
        raise Unsupported('comparison %r' % compare)


def idea_names(value):
    if isinstance(value, list):
        return [name for name, nested in value if nested is None]
    return [value]


def parse_constants(text):
    """common/script_constants file -> {schema: {key: value}} using fixed_point numbers."""
    out = {}
    for name, body in parse(text):
        if not isinstance(body, list):
            continue
        values = {}
        for key, value in body:
            if isinstance(value, list) or value is None:
                continue
            try:
                values[key] = float(value)
            except ValueError:
                continue
        out[name] = values
    return out


# ---------------------------------------------------------------------------------------------
# Structure of the chain
# ---------------------------------------------------------------------------------------------

def event_ids(body):
    found = []
    stack = [body]
    while stack:
        entries = stack.pop()
        for key, value in entries:
            if not isinstance(value, list):
                continue
            if key == 'country_event':
                event_id = first_value(value, 'id')
                if event_id:
                    found.append(event_id)
            stack.append(value)
    return found


def chain_members(tree):
    """[(index, key, event_id, body)] for the entries that dispatch a chain event."""
    members = []
    for index, (key, value) in enumerate(tree):
        if key in ('if', 'else_if', 'else'):
            for event_id in event_ids(value):
                if event_id in CHAIN:
                    members.append((index, key, event_id, value))
                    break
    return members


def limit_entries(body):
    limits = sub_blocks(body, 'limit')
    if len(limits) != 1:
        raise Unsupported('expected exactly one limit, got %d' % len(limits))
    return limits[0]


def date_fences(entries):
    return [(value[1], value[2]) for key, value in entries
            if key == 'date' and isinstance(value, tuple)]


def guards(entries):
    """Country flag names tested with NOT = { has_country_flag = ... } in a limit."""
    found = []
    for key, value in entries:
        if key == 'NOT' and isinstance(value, list):
            for inner_key, inner_value in value:
                if inner_key == 'has_country_flag':
                    found.append(inner_value)
    return found


def structure_failures(effects_text):
    failures = []
    body = named_block(effects_text, TICK)
    if body is None:
        return ['%s is missing' % TICK]
    tree = parse(body)
    members = chain_members(tree)

    if [member[2] for member in members] != list(CHAIN):
        failures.append('the chain dispatches %r instead of %r'
                        % ([member[2] for member in members], list(CHAIN)))
        return failures

    keys = [member[1] for member in members]
    if keys != ['if', 'else_if', 'else_if']:
        failures.append('the chain is %r, not one if with two else_if members' % (keys,))

    indexes = [member[0] for member in members]
    if indexes != [indexes[0], indexes[0] + 1, indexes[0] + 2]:
        failures.append('the chain members are not adjacent entries: %r' % (indexes,))
    else:
        following = tree[indexes[-1] + 1] if indexes[-1] + 1 < len(tree) else None
        if following is None:
            failures.append('nothing follows the chain')
        elif following[0] != 'if':
            failures.append('the branch after the chain is %r, so it is attached to the '
                            'chain instead of standing on its own' % following[0])
        elif INCOMPATIBLE_EVENT not in event_ids(following[1]):
            failures.append('the branch after the chain is not the incompatible-obligations '
                            'branch (%s)' % INCOMPATIBLE_EVENT)

    for index, key, event_id, member_body in members:
        entries = limit_entries(member_body)
        expected = ERA_FENCE[event_id]
        fences = [fence for fence in date_fences(entries) if fence == ('>', expected)]
        if not fences:
            failures.append('%s is not fenced at date > %d.%d.%d (found %r)'
                            % (event_id, expected[0], expected[1], expected[2],
                               date_fences(entries)))
        if NEGOTIATION_FLAG not in guards(entries):
            failures.append('%s does not wait while %s is set'
                            % (event_id, NEGOTIATION_FLAG))
        flag = SEEN_FLAG[event_id]
        flag_settings = [value for name, value in member_body
                         if name == 'set_country_flag']
        if flag_settings != [flag]:
            failures.append('%s sets %r instead of only %s'
                            % (event_id, flag_settings, flag))
        elsewhere = sum(1 for name, value in tree_entries(tree)
                        if name == 'set_country_flag' and value == flag)
        if elsewhere != 1:
            failures.append('%s is set %d times in the tick' % (flag, elsewhere))

    if re.search(r'[<>]=', strip_comments(body)):
        failures.append('the tick contains <= or >=')
    return failures


def tree_entries(tree):
    """Every (key, value) pair in the tick, at any depth."""
    out = []
    stack = [tree]
    while stack:
        entries = stack.pop()
        for key, value in entries:
            out.append((key, value))
            if isinstance(value, list):
                stack.append(value)
    return out


# ---------------------------------------------------------------------------------------------
# Behavioural cases, executed against the parsed tick
# ---------------------------------------------------------------------------------------------

ALL_PATRONS = {
    'ENG': Patron(exists=True, at_war=True),
    'SOV': Patron(exists=True, at_war=True),
    'GER': Patron(exists=True, at_war=True),
}

BASE_FLAGS = ('iran_campaign_active', GERMAN_MISSION)


def case_state(date, flags=(), variables=None, ideas=(), tag='PER', patrons=None,
               mission=True):
    base = ('iran_campaign_active',) + ((GERMAN_MISSION,) if mission else ())
    return State(tag=tag, flags=base + tuple(flags), date=date,
                 variables=variables or {}, ideas=ideas,
                 patrons=patrons if patrons is not None else dict(ALL_PATRONS))


AT_PEACE = {
    'ENG': Patron(exists=True, at_war=False),
    'SOV': Patron(exists=True, at_war=False),
    'GER': Patron(exists=True, at_war=False),
}

NO_BRITAIN = {
    'ENG': Patron(exists=False),
    'SOV': Patron(exists=True, at_war=True),
    'GER': Patron(exists=True, at_war=True),
}

NO_NORTHERN_WAR = {
    'ENG': Patron(exists=True, at_war=True),
    'SOV': Patron(exists=True, at_war=False),
    'GER': Patron(exists=True, at_war=True),
}

NO_GERMAN_WAR = {
    'ENG': Patron(exists=True, at_war=True),
    'SOV': Patron(exists=True, at_war=True),
    'GER': Patron(exists=True, at_war=False),
}

CASES = (
    ('tick: 1914 Britain at war dispatches nothing',
     lambda: case_state((1914, 8, 1)), []),
    ('tick: the 1919 standing-demand era dispatches nothing',
     lambda: case_state((1919, 6, 1)), []),
    ('tick: 1940.12.31 is still outside the corridor era',
     lambda: case_state((1940, 12, 31)), []),
    ('tick: 1941.1.1 dispatches only the British transit',
     lambda: case_state((1941, 1, 1)), [BRITISH]),
    ('tick: all three eligible dispatch only the British transit',
     lambda: case_state((1941, 1, 2)), [BRITISH]),
    ('tick: after the British demand, the northern corridor follows',
     lambda: case_state((1941, 1, 2), flags=(SEEN_FLAG[BRITISH],)), [NORTHERN]),
    ('tick: after both corridors, the Allied demand follows',
     lambda: case_state((1941, 1, 2),
                        flags=(SEEN_FLAG[BRITISH], SEEN_FLAG[NORTHERN])), [ALLIED]),
    ('tick: every demand already seen dispatches nothing',
     lambda: case_state((1943, 6, 1), flags=tuple(SEEN_FLAG.values())), []),
    ('tick: negotiation open blocks all three demands',
     lambda: case_state((1941, 6, 1), flags=(NEGOTIATION_FLAG,)), []),
    ('tick: negotiation open blocks the northern demand too',
     lambda: case_state((1941, 6, 1),
                        flags=(NEGOTIATION_FLAG, SEEN_FLAG[BRITISH])), []),
    ('tick: negotiation open blocks the Allied demand too',
     lambda: case_state((1941, 6, 1),
                        flags=(NEGOTIATION_FLAG, SEEN_FLAG[BRITISH],
                               SEEN_FLAG[NORTHERN])), []),
    ('tick: the transit agreement removes both corridors but not the Allied demand',
     lambda: case_state((1941, 6, 1), flags=(TRANSIT_AGREEMENT,)), [ALLIED]),
    ('tick: an absent Britain lets the northern demand through',
     lambda: case_state((1941, 6, 1), patrons=NO_BRITAIN), [NORTHERN]),
    ('tick: patrons at peace dispatch nothing',
     lambda: case_state((1941, 6, 1), patrons=AT_PEACE), []),
    ('tick: a northern power at peace leaves only the Allied demand',
     lambda: case_state((1941, 6, 1), flags=(SEEN_FLAG[BRITISH],),
                        patrons=NO_NORTHERN_WAR), [ALLIED]),
    ('tick: a Germany at peace ends the chain after both corridors',
     lambda: case_state((1941, 6, 1),
                        flags=(SEEN_FLAG[BRITISH], SEEN_FLAG[NORTHERN]),
                        patrons=NO_GERMAN_WAR), []),
    ('tick: without the German mission the Allied demand is not made',
     lambda: case_state((1941, 6, 1),
                        flags=(SEEN_FLAG[BRITISH], SEEN_FLAG[NORTHERN]),
                        mission=False), []),
    ('tick: a country that is not Iran dispatches nothing',
     lambda: case_state((1941, 6, 1), tag='ENG'), []),
)


def independent_branch_case():
    """A demand dispatch must not suppress the branches that follow the chain."""
    return case_state((1941, 6, 1),
                      flags=('iran_agreement_british_loan', 'iran_agreement_northern_railway'),
                      variables={'iran_sovereignty': 20, 'iran_british_influence': 60})


def run_cases(model):
    """[(label, expected, dispatched, added_flags, state)] for every case."""
    out = []
    for label, factory, expected in CASES:
        state = factory()
        before = set(state.flags)
        dispatched = model.run_tick(state)
        out.append((label, expected, dispatched, sorted(state.flags - before), state))
    return out


def case_failures(model):
    """[(label, [problem, ...])] so every case reports its own verdict."""
    out = []
    for label, expected, dispatched, added, state in run_cases(model):
        problems = []
        if dispatched != expected:
            problems.append('dispatched %r, expected %r' % (dispatched, expected))
        consumed = [flag for flag in added if flag in SEEN_FLAG.values()]
        earned = [SEEN_FLAG[event] for event in dispatched if event in SEEN_FLAG]
        if sorted(consumed) != sorted(earned):
            problems.append('consumed %r while dispatching %r' % (consumed, dispatched))
        out.append((label, problems))
    return out


def flat(failures):
    return ['%s: %s' % (label, problem) for label, problems in failures
            for problem in problems]


def independent_branch_failures(model):
    problems = []
    state = independent_branch_case()
    dispatched = model.run_tick(state)
    if dispatched != [BRITISH, INCOMPATIBLE_EVENT]:
        problems.append('the demand chain and the incompatible-obligations branch do not '
                        'both run in one tick: %r' % (dispatched,))
    if COMPETING_IDEA not in state.ideas:
        problems.append('the incompatible-obligations branch did not add %s' % COMPETING_IDEA)
    if CAPITULATION_IDEA not in state.ideas:
        problems.append('the sovereignty band did not follow a shrunken sovereignty value '
                        '(sovereignty %r, ideas %r)'
                        % (state.variables.get('iran_sovereignty'), sorted(state.ideas)))
    return problems


# ---------------------------------------------------------------------------------------------
# Wiring, structure and preservation checks
# ---------------------------------------------------------------------------------------------

def wiring_failures(on_actions_text):
    failures = []
    block = named_block(on_actions_text, 'on_actions')
    if block is None:
        return ['no on_actions block']
    tree = parse(block)
    monthly = sub_blocks(tree, 'on_monthly_PER')
    daily = sub_blocks(tree, 'on_daily_PER')
    if not monthly:
        failures.append('on_monthly_PER is missing')
    else:
        body = parse_wiring(monthly[0])
        if TICK not in body:
            failures.append('on_monthly_PER does not call %s (calls %r)' % (TICK, body))
    for entries in daily:
        if TICK in parse_wiring(entries):
            failures.append('on_daily_PER calls %s, which would run the monthly tick daily'
                            % TICK)
    return failures


def parse_wiring(entries):
    """Effect names named directly inside an `effect = { ... }` block."""
    names = set()
    for key, value in entries:
        if key == 'effect' and isinstance(value, list):
            for inner_key, inner_value in value:
                if inner_value == 'yes':
                    names.add(inner_key)
        elif isinstance(value, list):
            names |= parse_wiring(value)
    return names


def standing_tick_failures(effects_text):
    failures = []
    body = named_block(effects_text, STANDING_TICK)
    if body is None:
        return ['%s is missing' % STANDING_TICK]
    carried = [event_id for event_id in event_ids(parse(body)) if event_id in CHAIN]
    if carried:
        failures.append('%s carries the wartime demands %r' % (STANDING_TICK, carried))
    return failures


def event_block(text, event_id):
    for match in re.finditer(r'(?<![\w])country_event\s*=\s*\{', text):
        open_index = text.index('{', match.start())
        body = text[open_index + 1:match_brace(text, open_index) - 1]
        if re.search(r'(?<![\w])id\s*=\s*%s(?![\w.])' % re.escape(event_id), body):
            return body
    return None


def option_weight(text, event_id):
    body = event_block(text, event_id)
    if body is None:
        return None
    options = sub_blocks(parse(body), 'option')
    out = []
    for option in options:
        name = first_value(option, 'name')
        chance = sub_blocks(option, 'ai_chance')
        factor = first_value(chance[0], 'factor') if chance else None
        out.append((name, factor))
    return tuple(out)


def preservation_failures():
    failures = []
    working_events = read(EVENTS_PATH)
    baseline_events = baseline(EVENTS_PATH)
    for event_id in CHAIN:
        before = event_block(baseline_events, event_id)
        after = event_block(working_events, event_id)
        if after is None:
            failures.append('%s is missing from the event file' % event_id)
        elif before != after:
            failures.append('%s changed outside the routing repair' % event_id)
        weights_before = option_weight(baseline_events, event_id)
        weights_after = option_weight(working_events, event_id)
        if weights_before != weights_after:
            failures.append('%s option weights changed: %r -> %r'
                            % (event_id, weights_before, weights_after))

    working_loc = read(LOC_PATH)
    baseline_loc = baseline(LOC_PATH)
    for event_id in CHAIN:
        prefix = event_id + '.'
        keys_before = localisation_values(baseline_loc, prefix)
        keys_after = localisation_values(working_loc, prefix)
        if keys_before != keys_after:
            failures.append('%s localisation changed: %r'
                            % (event_id, sorted(set(keys_before) ^ set(keys_after))))
    return failures


def localisation_values(text, prefix):
    found = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix) and ':' in stripped:
            key, value = stripped.split(':', 1)
            found[key] = value
    return found


# ---------------------------------------------------------------------------------------------
# Mutants
# ---------------------------------------------------------------------------------------------

def mutate(text, old, new):
    if old not in text:
        raise Unsupported('mutant pattern not present: %r' % old[:60])
    mutated = text.replace(old, new, 1)
    if mutated == text:
        raise Unsupported('mutant changed nothing: %r' % old[:60])
    return mutated


BRITISH_FENCE = ('\t\t\tENG = { has_war = yes }\n'
                 '\t\t\tdate > 1940.12.31\n')
BRITISH_FENCE_REVERTED = ('\t\t\tENG = { has_war = yes }\n')

NORTHERN_GUARD = ('\t\t\tNOT = { has_country_flag = iran_soviet_transit_seen }\n'
                  '\t\t\tNOT = { has_country_flag = iran_negotiation_open }\n')
NORTHERN_GUARD_REVERTED = '\t\t\tNOT = { has_country_flag = iran_soviet_transit_seen }\n'

ALLIED_GUARD = ('\t\t\tNOT = { has_country_flag = iran_allied_demand }\n'
                '\t\t\tNOT = { has_country_flag = iran_negotiation_open }\n')
ALLIED_GUARD_REVERTED = '\t\t\tNOT = { has_country_flag = iran_allied_demand }\n'

NORTHERN_CHAIN = ('\telse_if = {\n'
                  '\t\tlimit = {\n'
                  '\t\t\tiran_campaign_country = yes\n'
                  '\t\t\tcountry_exists = SOV\n')
NORTHERN_CHAIN_REVERTED = ('\tif = {\n'
                           '\t\tlimit = {\n'
                           '\t\t\tiran_campaign_country = yes\n'
                           '\t\t\tcountry_exists = SOV\n')

ALLIED_CHAIN = ('\telse_if = {\n'
                '\t\tlimit = {\n'
                '\t\t\tiran_campaign_country = yes\n'
                '\t\t\tcountry_exists = GER\n')
ALLIED_CHAIN_REVERTED = ('\tif = {\n'
                         '\t\tlimit = {\n'
                         '\t\t\tiran_campaign_country = yes\n'
                         '\t\t\tcountry_exists = GER\n')

MUTANTS = (
    ('British era fence reverted',
     lambda text: mutate(text, BRITISH_FENCE, BRITISH_FENCE_REVERTED),
     'tick: 1914 Britain at war dispatches nothing',
     [BRITISH]),
    ('northern negotiation guard reverted',
     lambda text: mutate(text, NORTHERN_GUARD, NORTHERN_GUARD_REVERTED),
     'tick: negotiation open blocks the northern demand too',
     [NORTHERN]),
    ('Allied negotiation guard reverted',
     lambda text: mutate(text, ALLIED_GUARD, ALLIED_GUARD_REVERTED),
     'tick: negotiation open blocks the Allied demand too',
     [ALLIED]),
    ('independent if blocks restored',
     lambda text: mutate(mutate(text, NORTHERN_CHAIN, NORTHERN_CHAIN_REVERTED),
                         ALLIED_CHAIN, ALLIED_CHAIN_REVERTED),
     'tick: all three eligible dispatch only the British transit',
     [BRITISH, NORTHERN, ALLIED]),
)


# ---------------------------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------------------------

class Report:
    def __init__(self, detail):
        self.detail = detail
        self.checks = 0
        self.failures = []

    def start(self, name):
        if self.detail:
            print('== %s' % name)

    def check(self, label, passed, note=''):
        self.checks += 1
        if not passed:
            self.failures.append('%s -- %s' % (label, note) if note else label)
        if self.detail or not passed:
            print('%s %s%s' % ('PASS' if passed else 'FAIL', label,
                               (' (%s)' % note) if note and not passed else ''))

    def note(self, text):
        if self.detail:
            print('   note: %s' % text)

    def summary(self):
        print('%d checks, %d failures' % (self.checks, len(self.failures)))
        for failure in self.failures:
            print('  FAILED: %s' % failure)
        return not self.failures


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------

def main(argv):
    detail = '--detail' in argv
    report = Report(detail)
    effects_text = read(EFFECTS_PATH)

    report.start('structure of the chain')
    structural = structure_failures(effects_text)
    report.check('the three wartime demands form one era-fenced, negotiation-guarded chain',
                 not structural, '; '.join(structural))

    report.start('wiring')
    wiring = wiring_failures(read(ON_ACTIONS_PATH))
    report.check('on_monthly_PER calls the influence tick once per month', not wiring,
                 '; '.join(wiring))
    standing = standing_tick_failures(effects_text)
    report.check('the standing-demand helper does not carry the wartime branches',
                 not standing, '; '.join(standing))

    report.start('behaviour of the parsed tick')
    model = Model(effects_text)
    for label, problems in case_failures(model):
        report.check(label, not problems, '; '.join(problems))
    independent = independent_branch_failures(model)
    report.check('the incompatible-obligations and sovereignty branches still run after a '
                 'demand dispatch', not independent, '; '.join(independent))

    report.start('preservation')
    preserved = preservation_failures()
    report.check('the three events, their option weights and their localisation are '
                 'unchanged', not preserved, '; '.join(preserved))

    report.start('pre-edit source is rejected')
    snapshot = baseline(EFFECTS_PATH)
    snapshot_structural = structure_failures(snapshot)
    report.check('the pre-edit chain is rejected by the structural check',
                 bool(snapshot_structural), 'the pre-edit revision passes')
    if snapshot_structural:
        report.note('; '.join(snapshot_structural[:4]))
    snapshot_model = Model(snapshot)
    snapshot_failures = flat(case_failures(snapshot_model))
    report.check('the pre-edit tick dispatches a British demand in 1914',
                 any('1914' in failure for failure in snapshot_failures),
                 'the pre-edit revision does not trip the 1914 case')
    report.check('the pre-edit tick dispatches all three demands in one month',
                 any('all three eligible' in failure for failure in snapshot_failures),
                 'the pre-edit revision does not trip the multi-dispatch case')
    if snapshot_failures:
        report.note('%d pre-edit behaviour failures' % len(snapshot_failures))

    report.start('mutants')
    for name, mutate_source, target, expected_dispatch in MUTANTS:
        try:
            mutated = mutate_source(effects_text)
        except Unsupported as error:
            report.check('mutant %s applied' % name, False, str(error))
            continue
        mutant_model = Model(mutated)
        mutant_failures = (flat(case_failures(mutant_model))
                           + independent_branch_failures(mutant_model))
        dispatched = {label: dispatch for label, expected, dispatch, added, state
                      in run_cases(mutant_model)}
        actual = dispatched.get(target)
        report.check('mutant %s dispatches %r where the repair dispatches nothing else'
                     % (name, expected_dispatch),
                     actual == expected_dispatch,
                     'for %r it dispatched %r' % (target, actual))
        report.check('mutant %s fails for its own reason' % name,
                     any(target in failure for failure in mutant_failures),
                     'expected %r to fail, got %r' % (target, mutant_failures))
        report.check('mutant %s does not break every case' % name,
                     len(mutant_failures) < len(CASES),
                     'the mutant failed all %d cases' % len(CASES))

    return 0 if report.summary() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
