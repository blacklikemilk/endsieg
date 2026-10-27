"""Regression test: Qing survival is earned and no longer bought by one focus.

Six source-proven defects in the landed C2 Qing package are checked here against the shipped
script:

    1. **Historical collapse ignored the player.**  `qing_historical_collapse` wrapped
       `is_historical_focus_on = yes` alone, so a human Qing who kept the historical focus was
       scripted out of the dynasty no matter what it did.  It now also requires `is_ai = yes`;
       a human on the historical focus faces a higher survival bar (`qing_historical_pressure`)
       and loses standing when Wuchang rises (`revolution_pressure`), but is never railroaded.
    2. **The settlement window opened before the uprising.**  The revolution window fired at
       `date > 1911.9.1`, five weeks before Wuchang, so a reformed court could settle before the
       revolution it was settling with had begun.  The window now opens only on war with RCH
       after 1911.10.9 (`qing_armistice_open`) and closes on its own deadline through the hidden
       `qing_campaign.19`, so survival can neither pre-empt Wuchang nor outlast the armistice.
    3. **One focus bought all-China survival.**  `qing_campaign.62.b` called
       `qing_settle_constitutional` with no trigger, and that effect annexed the entire Republic
       unconditionally.  The option is now gated by `qing_survival_possible` and the armistice
       behind a `custom_trigger_tooltip`, and the route effects are gated again on the way in.
    4. **The settlement was one unconditional annexation.**  `qing_end_revolution` annexed RCH
       and granted cores on everything the sweep touched.  It is now a router over three
       outcomes with their own gates: partition (the Republic survives in the south, nothing is
       transferred), reunion (the assembly accepts the monarchy, paid for from the treasury) and
       conquest (the army dictates terms in a capital it holds).  No outcome grants southern
       cores.
    5. **The reclaim sweep took Asia.**  `endsieg_china_reclaim_states` transferred every state
       on the Asian continent owned by ten tags, plus 609 and 743 (Qingdao, a German concession
       Qing never owned), and added a core to each.  It is now closed to the 55 states the 1910
       Qing scenario owns that a dated history block hands to a Chinese successor government.
    6. **A partition was overwritten by bookkeeping.**  The 1914 and 1936 ownership repairs ran
       on any settled Qing, which would have handed a partitioned Republic's south back to
       Beijing.  Both are now suppressed while `qing_settlement_partition` is set.

The test reads the shipped sources rather than restating them:

    1. `common/scripted_triggers/qing_campaign.txt` - the survival bar, the historical gate,
       the armistice window and the three outcome gates,
    2. `common/scripted_effects/qing_campaign.txt` - the tick window, the 1914/1936 repairs,
       the settlement router and the route effects,
    3. `events/qing_campaign.txt` - the settlement offers, the `.62` abdication question and
       the hidden armistice deadline,
    4. `common/script_constants/qing_campaign.txt` - every threshold the gates read,
    5. `common/scripted_effects/endsieg_china_ownership.txt` - the narrowed reclaim sweep,
    6. `history/states/*.txt` - the scenario ownership the reclaim set is derived from,
    7. `localisation/english/qing_campaign_events_l_english.yml` - option, tooltip and popup text.

Every repair check also runs against the pinned pre-repair revision and must reject it, which is
the mutant control: a check that passes both revisions would prove nothing.  The negative control
in section 7 is the original defect stated as a test - under the baseline sources the one-focus
path annexes all of China, and under the shipped sources it does nothing at all.

Run from the repository root:

    python .tools/tests/test_qing_survival.py           # exit 0 = pass
    python .tools/tests/test_qing_survival.py --detail  # print every check
    python .tools/tests/test_qing_survival.py --dump    # print the parsed model

This is a source check.  It proves what the script says under the country states it is given; it
does not prove what the engine does when a player clicks the focus or the option.  No game is
launched.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRIGGERS_PATH = 'common/scripted_triggers/qing_campaign.txt'
EFFECTS_PATH = 'common/scripted_effects/qing_campaign.txt'
EVENTS_PATH = 'events/qing_campaign.txt'
CONSTANTS_PATH = 'common/script_constants/qing_campaign.txt'
OWNERSHIP_PATH = 'common/scripted_effects/endsieg_china_ownership.txt'
LOCALISATION_PATH = 'localisation/english/qing_campaign_events_l_english.yml'
STATES_DIR = 'history/states'

# The pre-repair revision every defect below was audited in. Pinned by full object name: a
# mutable `HEAD` stops being a mutant as soon as the repair is committed.
BASELINE_REV = 'f6d12527cc8a3ed3cda6e533528f46bbba4d6e17'

LATE_QING_FOCUS = 'QW1_abdication_question'
ABDICATION_EVENT = 'qing_campaign.62'
ABDICATION_OPTION = 'qing_campaign.62.b'
ARMISTICE_EVENT = 'qing_campaign.19'

# The tags the scenario's dated blocks hand Chinese states to. Tibet, Mongolia, Tannu Tuva,
# Japan, Germany and Mengjiang are deliberately outside this set.
SUCCESSOR_TAGS = frozenset((
    'RCH', 'CHI', 'YUN', 'GXC', 'XSM', 'SIK', 'SHX', 'MAN', 'PRC', 'SND',
))

# The one state the old sweep took that the 1910 scenario never owned: Qingdao, a German lease.
FOREIGN_LEASE_STATE = 743

OUTCOME_EFFECTS = {
    'qing_revolution_partition': 'partition',
    'qing_revolution_reunion': 'reunion',
    'qing_revolution_conquest': 'conquest',
}

ROUTE_EFFECTS = (
    'qing_settle_constitutional',
    'qing_settle_authoritarian',
    'qing_settle_yuan',
    'qing_settle_federal',
)

CONSTANT_REF = re.compile(r'constant:([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)')
DATE = re.compile(r'^\d{4}\.\d{1,2}\.\d{1,2}$')

VERBOSE = '--detail' in sys.argv


class Unsupported(Exception):
    """A script shape this check does not model. Failing loudly beats guessing."""


def note(message):
    if VERBOSE:
        print('    ' + message)


# ---------------------------------------------------------------------------------------------
# Parser: Clausewitz text -> nested (key, value, line) entries
# ---------------------------------------------------------------------------------------------

OPERATORS = ('<', '>', '<=', '>=')


def tokenize(text):
    tokens = []
    index = 0
    line = 1
    length = len(text)
    while index < length:
        char = text[index]
        if char == '#':
            while index < length and text[index] != '\n':
                index += 1
        elif char in '{}=':
            tokens.append((char, char, line))
            index += 1
        elif char in ' \t\r\n':
            if char == '\n':
                line += 1
            index += 1
        else:
            start = index
            while index < length and text[index] not in ' \t\r\n{}=#':
                index += 1
            tokens.append(('word', text[start:index], line))
    return tokens


def parse_block(tokens, index):
    entries = []
    while index < len(tokens):
        kind, text, line = tokens[index]
        if kind == '}':
            return entries, index + 1
        if kind != 'word':
            raise Unsupported('unexpected %r at line %d' % (text, line))
        if index + 1 >= len(tokens):
            raise Unsupported('trailing %s at line %d' % (text, line))
        if tokens[index + 1][0] != '=':
            # `has_political_power > 75` and `date > 1911.10.9`: a comparison.
            if index + 2 < len(tokens) and tokens[index + 1][0] == 'word' \
                    and tokens[index + 1][1] in OPERATORS and tokens[index + 2][0] == 'word':
                entries.append((text, ('compare', tokens[index + 1][1], tokens[index + 2][1]),
                                line))
                index += 3
                continue
            entries.append((text, ('scalar', text), line))
            index += 1
            continue
        if index + 2 >= len(tokens):
            raise Unsupported('trailing %s at line %d' % (text, line))
        value_kind, value_text, _ = tokens[index + 2]
        if value_kind == '{':
            value, index = parse_block(tokens, index + 3)
            entries.append((text, ('block', value), line))
        elif value_kind == 'word':
            entries.append((text, ('scalar', value_text), line))
            index += 3
        else:
            raise Unsupported('unexpected %r after %s at line %d' % (value_text, text, line))
    return entries, index


def parse_text(text):
    entries, _ = parse_block(tokenize(text), 0)
    return entries


def read_repo(path):
    with open(ROOT / path, 'r', encoding='utf-8-sig') as handle:
        return handle.read()


def baseline_text(path):
    """The pinned pre-repair bytes of one file, read from git rather than from the worktree."""
    result = subprocess.run(['git', 'show', '%s:%s' % (BASELINE_REV, path)],
                            cwd=str(ROOT), capture_output=True)
    if result.returncode != 0:
        print('cannot read the pinned baseline %s:%s' % (BASELINE_REV, path))
        print(result.stderr.decode('utf-8', 'replace').strip())
        print('the mutant controls need the repository history; this is not a pass')
        sys.exit(2)
    return result.stdout.decode('utf-8-sig')


# ---------------------------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------------------------

def scalar(entries, key):
    for entry_key, value, _line in entries:
        if entry_key == key and value[0] == 'scalar':
            return value[1]
    return None


def block(entries, key):
    for entry_key, value, _line in entries:
        if entry_key == key and value[0] == 'block':
            return value[1]
    return None


def blocks(entries, key):
    return [value[1] for entry_key, value, _line in entries
            if entry_key == key and value[0] == 'block']


def compare_entry(entries, key):
    for entry_key, value, _line in entries:
        if entry_key == key and value[0] == 'compare':
            return value[1], value[2]
    return None


def keys_of(entries):
    return [key for key, _value, _line in entries]


def normalize(entries):
    """A comparable shape for a block, ignoring line numbers."""
    out = []
    for key, value, _line in entries:
        if value[0] == 'block':
            out.append((key, 'block', normalize(value[1])))
        elif value[0] == 'compare':
            out.append((key, 'compare', value[1], value[2]))
        else:
            out.append((key, 'scalar', value[1]))
    return out


def as_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        raise Unsupported('%r is not a number' % (text,))


def effect_body(text, name):
    for key, value, _line in parse_text(text):
        if key == name and value[0] == 'block':
            return value[1]
    return None


def trigger_body(text, name):
    for key, value, _line in parse_text(text):
        if key == name and value[0] == 'block':
            return value[1]
    return None


def macros_of(text):
    """@name = value file macros, used where a field takes a literal."""
    found = {}
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped.startswith('@'):
            continue
        parts = stripped.split()
        if len(parts) >= 3 and parts[1] == '=':
            found[parts[0][1:]] = as_number(parts[2])
    return found


def scripted_trigger_names(text):
    return set(keys_of(parse_text(text)))


# ---------------------------------------------------------------------------------------------
# Constants and their references
# ---------------------------------------------------------------------------------------------

def constants_of(text):
    """{name: value} for constant:qing_story.<name>."""
    found = {}
    story = block(parse_text(text), 'qing_story')
    if story is None:
        raise Unsupported('no qing_story constant category in %s' % CONSTANTS_PATH)
    for key, value, _line in story:
        if value[0] == 'scalar':
            try:
                found[key] = float(value[1])
            except ValueError:
                continue
    return found


def constant_references(*texts):
    """[(group, name)] for every constant: reference in the given sources."""
    refs = []
    for text in texts:
        for group, name in CONSTANT_REF.findall(text):
            refs.append((group, name))
    return refs


# ---------------------------------------------------------------------------------------------
# Scenario ownership: what the reclaim sweep is allowed to touch
# ---------------------------------------------------------------------------------------------

def state_history(path):
    """(state id, start owner, [(date, owner, removes_qin_core)]) from one history file."""
    # Reuse the tolerant tokenizer: history files mix tabs, inline comments and date blocks.
    entries = parse_text(path.read_text(encoding='utf-8', errors='replace'))
    state = block(entries, 'state')
    if state is None:
        raise Unsupported('no state block in %s' % path.name)
    state_id = int(scalar(state, 'id'))
    history = block(state, 'history')
    if history is None:
        raise Unsupported('no history block in %s' % path.name)
    start = scalar(history, 'owner')
    dated = []
    for key, value, _line in history:
        if not DATE.match(str(key)) or value[0] != 'block':
            continue
        owner = scalar(value[1], 'owner')
        dated.append((key, owner, 'remove_core_of' in keys_of(value[1])))
    return state_id, start, dated


def scenario_reclaim_set():
    """The states the 1910 Qing owns that a dated block hands to a Chinese successor.

    A state belongs to the set when at least one dated block gives it to a successor tag
    without stripping the Qing core, which is the scenario's bookkeeping handover rather
    than a cession. This is an independent derivation from history/states, not a copy of
    the script list.
    """
    directory = ROOT / STATES_DIR
    if not directory.is_dir():
        raise Unsupported('%s is missing' % STATES_DIR)
    reclaimed = set()
    ceded = set()
    outside = set()
    for path in sorted(directory.glob('*.txt')):
        state_id, start, dated = state_history(path)
        if start != 'QIN':
            continue
        handovers = set()
        cessations = set()
        foreign = set()
        for _date, owner, removes in dated:
            if owner is None or owner == 'QIN':
                continue
            if owner not in SUCCESSOR_TAGS:
                foreign.add(state_id)
            elif removes:
                cessations.add(state_id)
            else:
                handovers.add(state_id)
        if handovers:
            reclaimed |= handovers
        elif cessations:
            ceded |= cessations
        elif foreign:
            outside |= foreign
    if not reclaimed:
        raise Unsupported('no QIN scenario states were derived from %s' % STATES_DIR)
    return reclaimed, ceded, outside


# ---------------------------------------------------------------------------------------------
# Country-state model and trigger evaluation
# ---------------------------------------------------------------------------------------------

class Country:
    def __init__(self, flags=(), variables=None, political_power=200, at_war=(), controlled=(),
                 historical=False, ai=False, date='1911.11.1', rch=True):
        self.flags = set(flags)
        self.variables = dict(variables or {})
        self.political_power = political_power
        self.at_war = set(at_war)
        self.controlled = set(controlled)
        self.historical = historical
        self.ai = ai
        self.date = date
        self.rch = rch

    def label(self):
        return '%s%s%s%s pp=%d %s vars=%s' % (
            'ai' if self.ai else 'human',
            '/historical' if self.historical else '',
            '/war' if self.at_war else '',
            '/beijing' if 608 in self.controlled else '',
            self.political_power,
            self.date,
            {name: int(value) for name, value in sorted(self.variables.items())},
        )


COMPARE = {
    'greater_than_or_equals': lambda left, right: left >= right,
    'less_than_or_equals': lambda left, right: left <= right,
    'greater_than': lambda left, right: left > right,
    'less_than': lambda left, right: left < right,
    'equals': lambda left, right: left == right,
}

SYMBOL = {
    '>': lambda left, right: left > right,
    '<': lambda left, right: left < right,
    '>=': lambda left, right: left >= right,
    '<=': lambda left, right: left <= right,
}


def date_tuple(text):
    return tuple(int(part) for part in str(text).split('.'))


class Evaluator:
    """Evaluates the subset of triggers this package uses, resolving scripted triggers."""

    def __init__(self, triggers_text, constants):
        self.triggers = scripted_trigger_names(triggers_text)
        self.triggers_text = triggers_text
        self.constants = constants

    def constant(self, token):
        match = CONSTANT_REF.match(token) if token else None
        if match is None:
            raise Unsupported('%r is not a constant reference' % (token,))
        group, name = match.group(1), match.group(2)
        if group != 'qing_story':
            raise Unsupported('constant group %r is not modelled' % group)
        if name not in self.constants:
            raise Unsupported('constant:qing_story.%s is used but not defined' % name)
        return self.constants[name]

    def value(self, token):
        if token is None:
            raise Unsupported('missing value')
        if token.startswith('constant:'):
            return self.constant(token)
        return as_number(token)

    def trigger(self, entries, country, depth=0):
        if depth > 12:
            raise Unsupported('scripted trigger recursion is deeper than this check models')
        result = True
        for key, value, line in entries:
            if key in ('OR', 'AND', 'NOT'):
                if value[0] != 'block':
                    raise Unsupported('%s without a block at line %d' % (key, line))
                if key == 'OR':
                    outcome = any(self.trigger([entry], country, depth) for entry in value[1])
                else:
                    outcome = self.trigger(value[1], country, depth)
                    if key == 'NOT':
                        outcome = not outcome
                result = result and outcome
            elif key == 'custom_trigger_tooltip':
                if value[0] != 'block' or scalar(value[1], 'tooltip') is None:
                    raise Unsupported('custom_trigger_tooltip shape at line %d' % line)
                inner = [entry for entry in value[1] if entry[0] != 'tooltip']
                result = result and self.trigger(inner, country, depth)
            elif key == 'always':
                result = result and (value[0] == 'scalar' and value[1] == 'yes')
            elif key == 'is_ai':
                result = result and country.ai
            elif key == 'is_historical_focus_on':
                result = result and country.historical
            elif key == 'has_country_flag':
                if value[0] != 'scalar':
                    raise Unsupported('has_country_flag block at line %d' % line)
                result = result and value[1] in country.flags
            elif key == 'has_war_with':
                result = result and value[1] in country.at_war
            elif key == 'country_exists':
                result = result and (value[1] == 'RCH' and country.rch)
            elif key == 'controls_state':
                result = result and int(value[1]) in country.controlled
            elif key == 'state':
                raise Unsupported('state id checks belong to the state model, not the country one')
            elif key == 'has_political_power':
                if value[0] != 'compare':
                    raise Unsupported('has_political_power shape at line %d' % line)
                result = result and SYMBOL[value[1]](country.political_power,
                                                     as_number(value[2]))
            elif key == 'date':
                if value[0] != 'compare':
                    raise Unsupported('date shape at line %d' % line)
                result = result and SYMBOL[value[1]](date_tuple(country.date),
                                                     date_tuple(value[2]))
            elif key == 'check_variable':
                if value[0] != 'block':
                    raise Unsupported('check_variable shape at line %d' % line)
                name = scalar(value[1], 'var')
                comparer = scalar(value[1], 'compare')
                if name is None or comparer not in COMPARE:
                    raise Unsupported('check_variable shape at line %d' % line)
                left = country.variables.get(name, 0.0)
                result = result and COMPARE[comparer](left,
                                                      self.value(scalar(value[1], 'value')))
            elif key in self.triggers:
                if value[0] != 'scalar' or value[1] != 'yes':
                    raise Unsupported('scripted trigger %s used as a value at line %d'
                                      % (key, line))
                result = result and self.trigger(trigger_body(self.triggers_text, key),
                                                 country, depth + 1)
            else:
                raise Unsupported('trigger %r at line %d is not modelled' % (key, line))
        return result


# ---------------------------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------------------------

def events_of(text):
    """event id -> body."""
    found = {}
    for key, value, _line in parse_text(text):
        if key.rsplit('_', 1)[0] in ('country', 'news', 'state') and value[0] == 'block':
            event_id = scalar(value[1], 'id')
            if event_id:
                found[event_id] = value[1]
    if not found:
        raise Unsupported('no events found')
    return found


def options_of(event):
    return [value[1] for key, value, _line in event
            if key == 'option' and value[0] == 'block']


def option_by_name(event, name):
    for option in options_of(event):
        if scalar(option, 'name') == name:
            return option
    return None


def effect_calls(entries):
    """Scripted-effect calls in document order: (name, body)."""
    called = []
    for key, value, _line in entries:
        if value[0] == 'block' and key not in (
                'trigger', 'if', 'else_if', 'else', 'limit', 'custom_trigger_tooltip'):
            called.append((key, value[1]))
    return called


def find_deep(entries, predicate, path=()):
    """Depth-first search over blocks, yielding (key, value, path)."""
    for key, value, _line in entries:
        if value[0] != 'block':
            continue
        here = path + (key,)
        if predicate(key, value[1], here):
            yield key, value[1], here
        yield from find_deep(value[1], predicate, here)


# ---------------------------------------------------------------------------------------------
# Settlement routing model
# ---------------------------------------------------------------------------------------------

def settle_route(effects_text, evaluator, country):
    """What `qing_settle_constitutional` actually does for one country state.

    Returns a short description: 'refused: armistice', 'refused: historical',
    'partition', 'reunion', 'conquest' or 'nothing'.
    """
    body = effect_body(effects_text, 'qing_settle_constitutional')
    if body is None:
        raise Unsupported('qing_settle_constitutional is missing')
    guard = block(body, 'if')
    if guard is not None:
        limit = block(guard, 'limit')
        if limit is None:
            raise Unsupported('route guard without a limit')
        if not evaluator.trigger(limit, country):
            return 'refused: guard'
    return settlement_outcome(effects_text, evaluator, country)


def settlement_outcome(effects_text, evaluator, country):
    """The outcome `qing_end_revolution` selects for one country state."""
    body = effect_body(effects_text, 'qing_end_revolution')
    if body is None:
        raise Unsupported('qing_end_revolution is missing')
    outer = block(body, 'if')
    if outer is None:
        raise Unsupported('qing_end_revolution has no guard')
    limit = block(outer, 'limit')
    if limit is None or not evaluator.trigger(limit, country):
        return 'refused: end'
    for kind, value, _line in outer:
        if kind in ('limit',):
            continue
        if kind == 'if':
            inner = block(value[1], 'limit')
            if inner is not None and evaluator.trigger(inner, country):
                return outcome_name(value[1])
        elif kind == 'else_if':
            inner = block(value[1], 'limit')
            if inner is not None and evaluator.trigger(inner, country):
                return outcome_name(value[1])
        elif kind == 'else':
            return outcome_name(value[1])
    return 'nothing'


def outcome_name(entries):
    for key, value, _line in entries:
        if value[0] == 'scalar' and value[1] == 'yes' and key in OUTCOME_EFFECTS:
            return OUTCOME_EFFECTS[key]
    return 'nothing'


# ---------------------------------------------------------------------------------------------
# Section 1: the historical gate and the pressure it applies
# ---------------------------------------------------------------------------------------------

def check_historical_gate(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    shipped_evaluator = Evaluator(shipped[TRIGGERS_PATH], constants)
    baseline_evaluator = Evaluator(baseline[TRIGGERS_PATH], constants)

    bars = constants['survival_reform'], constants['survival_loyalty'], constants['survival_trust']
    pressure = (constants['survival_reform_pressure'], constants['survival_loyalty_pressure'],
                constants['survival_trust_pressure'])
    variables = dict(zip(('qing_reform', 'qing_army_loyalty', 'qing_provincial_trust'), bars))
    strong = dict(zip(('qing_reform', 'qing_army_loyalty', 'qing_provincial_trust'), pressure))

    scenarios = [
        # (label, country, expected collapse, expected survival)
        ('ai_historical', Country(historical=True, ai=True, variables=strong), True, False),
        ('human_historical', Country(historical=True, variables=strong), False, True),
        ('human_historical_at_base_bar',
         Country(historical=True, variables=variables), False, False),
        ('human_historical_weak', Country(historical=True), False, False),
        ('human_free_play_at_base_bar',
         Country(historical=False, variables=variables), False, True),
    ]

    collapse = trigger_body(shipped[TRIGGERS_PATH], 'qing_historical_collapse')
    survival = trigger_body(shipped[TRIGGERS_PATH], 'qing_survival_possible')
    if collapse is None or survival is None:
        failures.append('qing_historical_collapse or qing_survival_possible is missing')
        return failures

    if key_present(collapse, 'is_ai') is False:
        failures.append('qing_historical_collapse does not require is_ai = yes')

    for label, country, want_collapse, want_survival in scenarios:
        got_collapse = shipped_evaluator.trigger(collapse, country)
        got_survival = shipped_evaluator.trigger(survival, country)
        if got_collapse != want_collapse:
            failures.append('qing_historical_collapse is %s for %s (%s), expected %s'
                            % (got_collapse, label, country.label(), want_collapse))
        if got_survival != want_survival:
            failures.append('qing_survival_possible is %s for %s (%s), expected %s'
                            % (got_survival, label, country.label(), want_survival))
        note('%s: collapse=%s survival=%s' % (label, got_collapse, got_survival))

    # The pressure must be a real second bar, not a copy of the first.
    if not (pressure[0] > bars[0] and pressure[1] > bars[1] and pressure[2] > bars[2]):
        failures.append('the pressure bars are not higher than the base survival bars')
    if 'qing_historical_pressure' not in scripted_trigger_names(shipped[TRIGGERS_PATH]):
        failures.append('qing_historical_pressure is missing')
    if 'qing_historical_pressure' not in shipped[TRIGGERS_PATH].split(
            'qing_survival_possible = {', 1)[-1].split('\n}', 1)[0]:
        failures.append('qing_survival_possible does not read the historical pressure bar')

    # Mutant control: the baseline railroading must fail the human scenarios.
    baseline_collapse = trigger_body(baseline[TRIGGERS_PATH], 'qing_historical_collapse')
    human = Country(historical=True, variables=strong)
    if not baseline_evaluator.trigger(baseline_collapse, human):
        failures.append('the baseline qing_historical_collapse no longer railroads a human, so '
                        'this control proves nothing about the repair')
    else:
        note('baseline rails the human player: as expected')

    # The pressure must also be applied once, when the uprising begins.
    tick = effect_body(shipped[EFFECTS_PATH], 'qing_campaign_tick')
    if tick is None:
        failures.append('qing_campaign_tick is missing')
    elif not any('revolution_pressure' in str(entry) for entry in find_deep(
            tick, lambda key, body, path: key == 'add_to_variable')):
        failures.append('the historical pressure constant is never applied')
    return failures


def key_present(entries, name):
    return any(key == name for key, _value, _line in entries)


# ---------------------------------------------------------------------------------------------
# Section 2: the armistice window is war-gated and has a deadline
# ---------------------------------------------------------------------------------------------

def check_armistice_window(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    evaluator = Evaluator(shipped[TRIGGERS_PATH], constants)

    armistice = trigger_body(shipped[TRIGGERS_PATH], 'qing_armistice_open')
    if armistice is None:
        failures.append('qing_armistice_open is missing')
    else:
        scenarios = [
            ('window_open', Country(flags=('qing_revolution_window_seen',)), True),
            ('no_window', Country(), False),
            ('window_closed', Country(flags=('qing_revolution_window_seen',
                                             'qing_armistice_closed')), False),
        ]
        for label, country, expected in scenarios:
            actual = evaluator.trigger(armistice, country)
            if actual != expected:
                failures.append('qing_armistice_open is %s for %s, expected %s'
                                % (actual, label, expected))
            note('armistice %s: %s' % (label, actual))

    # The window itself: war with RCH after Wuchang, never a pre-uprising date.
    tick = effect_body(shipped[EFFECTS_PATH], 'qing_campaign_tick')
    windows = [body for key, body, _path in find_deep(
        tick or [], lambda k, b, p: k == 'if' and block(b, 'limit') is not None
        and key_present(block(b, 'limit'), 'has_war_with'))]
    window = windows[0] if windows else None
    if window is None:
        failures.append('the tick has no war-gated revolution window')
    else:
        limit = block(window, 'limit')
        if not key_present(limit, 'date'):
            failures.append('the revolution window does not check the date')
        else:
            comparison = compare_entry(limit, 'date')
            if comparison is None:
                failures.append('the revolution window date check is unreadable')
            else:
                operand = comparison[1]
                if date_tuple(operand) < date_tuple('1911.10.9'):
                    failures.append('the revolution window still opens before Wuchang (%s)'
                                    % operand)
        for label, country, expected in (
                ('pre_uprising_with_war', Country(date='1911.9.5', at_war=('RCH',)), False),
                ('post_uprising_without_war', Country(date='1911.11.1'), False),
                ('post_uprising_with_war', Country(date='1911.11.1', at_war=('RCH',)), True)):
            actual = evaluator.trigger(limit, country)
            if actual != expected:
                failures.append('the revolution window is %s for %s (%s), expected %s'
                                % (actual, label, country.label(), expected))
            note('window %s: %s' % (label, actual))

        if not any(key == 'country_event' and scalar(value[1], 'id') == ARMISTICE_EVENT
                   for key, value, _line in window):
            failures.append('the revolution window does not schedule %s' % ARMISTICE_EVENT)

    # The deadline event closes the window and closes nothing else.
    shipped_events = events_of(shipped[EVENTS_PATH])
    deadline = shipped_events.get(ARMISTICE_EVENT)
    if deadline is None:
        failures.append('%s is missing from the event chain' % ARMISTICE_EVENT)
    else:
        if scalar(deadline, 'hidden') != 'yes':
            failures.append('%s is not a hidden timer event' % ARMISTICE_EVENT)
        if scalar(deadline, 'is_triggered_only') != 'yes':
            failures.append('%s is not triggered only' % ARMISTICE_EVENT)
        if 'qing_armistice_closed' not in str(options_of(deadline)):
            failures.append('%s never closes the armistice' % ARMISTICE_EVENT)

    # Every settlement path must refuse outside the window.
    body = effect_body(shipped[EFFECTS_PATH], 'qing_end_revolution')
    guard = block(body, 'if') if body else None
    limit = block(guard, 'limit') if guard else None
    if limit is None or 'qing_armistice_open' not in keys_of(limit):
        failures.append('qing_end_revolution is not gated by the armistice')
    for name in ROUTE_EFFECTS:
        route = effect_body(shipped[EFFECTS_PATH], name)
        guard = block(route, 'if') if route else None
        inner = block(guard, 'limit') if guard else None
        if inner is None or 'qing_armistice_open' not in keys_of(inner):
            failures.append('%s is not gated by the armistice' % name)

    # Mutant control: the baseline had no armistice at all.
    baseline_tick = effect_body(baseline[EFFECTS_PATH], 'qing_campaign_tick')
    baseline_windows = [block(b, 'limit') for key, b, _path in find_deep(
        baseline_tick or [], lambda k, b, p: k == 'if' and block(b, 'limit') is not None
        and key_present(block(b, 'limit'), 'date')
        and not key_present(block(b, 'limit'), 'has_war_with')
        and not any(inner == 'endsieg_china_reclaim_states'
                    for inner in keys_of(b)))]
    if not baseline_windows:
        failures.append('the baseline tick no longer has an undated war-free window, so this '
                        'control proves nothing about the repair')
    else:
        note('baseline window limit: %s' % [key for key, _v, _l in baseline_windows[0] or []])
    return failures


# ---------------------------------------------------------------------------------------------
# Section 3: the abdication option is gated and readable
# ---------------------------------------------------------------------------------------------

def check_abdication_option(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    evaluator = Evaluator(shipped[TRIGGERS_PATH], constants)
    events = events_of(shipped[EVENTS_PATH])
    event = events.get(ABDICATION_EVENT)
    if event is None:
        return ['%s is missing' % ABDICATION_EVENT]
    option = option_by_name(event, ABDICATION_OPTION)
    if option is None:
        return ['%s is missing' % ABDICATION_OPTION]
    trigger = block(option, 'trigger')
    if trigger is None:
        return ['%s has no trigger, so the focus can still settle unconditionally'
                % ABDICATION_OPTION]

    tooltips = [body for key, body, _line in find_deep(
        trigger, lambda key, body, path: key == 'custom_trigger_tooltip')]
    if not tooltips:
        failures.append('%s is gated without a custom_trigger_tooltip' % ABDICATION_OPTION)
    tooltip_key = scalar(tooltips[0], 'tooltip') if tooltips else None
    if tooltip_key is None:
        failures.append('%s has no tooltip localisation key' % ABDICATION_OPTION)
    inner = [entry for entry in tooltips[0] if entry[0] != 'tooltip'] if tooltips else []
    if 'qing_survival_possible' not in keys_of(inner):
        failures.append('%s is not gated by qing_survival_possible' % ABDICATION_OPTION)
    if 'qing_armistice_open' not in keys_of(inner):
        failures.append('%s is not gated by the armistice window' % ABDICATION_OPTION)

    bars = dict(zip(('qing_reform', 'qing_army_loyalty', 'qing_provincial_trust'),
                    (constants['survival_reform_pressure'],
                     constants['survival_loyalty_pressure'],
                     constants['survival_trust_pressure'])))
    scenarios = [
        ('human_historical_in_window',
         Country(flags=('qing_revolution_window_seen',), historical=True, variables=bars), True),
        ('human_historical_before_window', Country(historical=True, variables=bars), False),
        ('human_historical_after_deadline',
         Country(flags=('qing_revolution_window_seen', 'qing_armistice_closed'),
                 historical=True, variables=bars), False),
        ('ai_historical_in_window',
         Country(flags=('qing_revolution_window_seen',), historical=True, ai=True,
                 variables=bars), False),
        ('human_historical_below_bar',
         Country(flags=('qing_revolution_window_seen',), historical=True), False),
    ]
    for label, country, expected in scenarios:
        actual = evaluator.trigger(trigger, country)
        if actual != expected:
            failures.append('%s is %s for %s (%s), expected %s'
                            % (ABDICATION_OPTION, 'selectable' if actual else 'hidden',
                               label, country.label(), expected))
        note('option %s: %s' % (label, actual))

    baseline_event = events_of(baseline[EVENTS_PATH]).get(ABDICATION_EVENT)
    baseline_option = option_by_name(baseline_event, ABDICATION_OPTION) \
        if baseline_event is not None else None
    if baseline_option is None:
        failures.append('the baseline %s is missing, so the control proves nothing'
                        % ABDICATION_OPTION)
    elif block(baseline_option, 'trigger') is not None:
        failures.append('the baseline %s already had a trigger, so the control is vacuous'
                        % ABDICATION_OPTION)
    else:
        note('baseline option b: ungated, as audited')
    return failures


# ---------------------------------------------------------------------------------------------
# Section 4: three distinct outcomes, no unconditional annexation, no free cores
# ---------------------------------------------------------------------------------------------

def check_outcomes(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    evaluator = Evaluator(shipped[TRIGGERS_PATH], constants)
    effects = shipped[EFFECTS_PATH]

    # Every outcome exists exactly once and none of them grants a core or a core conversion.
    for name in OUTCOME_EFFECTS:
        body = effect_body(effects, name)
        if body is None:
            failures.append('%s is missing' % name)
            continue
        text = str(normalize(body))
        if 'add_core_of' in text:
            failures.append('%s grants cores' % name)
        if 'set_state_owner_to' in text:
            failures.append('%s transfers states' % name)
        if 'qing_regime_settled' not in text:
            failures.append('%s does not mark the regime settled' % name)

    partition = effect_body(effects, 'qing_revolution_partition')
    if partition is not None:
        flat = str(normalize(partition))
        if 'annex_country' in flat:
            failures.append('the partition outcome still annexes the Republic')
        if 'white_peace' not in flat:
            failures.append('the partition outcome never ends the war')
        if 'qing_settlement_partition' not in flat:
            failures.append('the partition outcome does not record itself')

    for name, price in (('qing_revolution_reunion', 'settlement_price_reunion'),
                        ('qing_revolution_conquest', 'settlement_price_conquest')):
        body = effect_body(effects, name)
        if body is None:
            continue
        flat = str(normalize(body))
        if 'annex_country' not in flat:
            failures.append('%s does not absorb the Republic government' % name)
        if price not in flat:
            failures.append('%s is not paid for out of the treasury (%s)' % (name, price))
        if constants.get(price, 0.0) >= 0:
            failures.append('%s is not a cost' % price)

    # The router picks the strongest reachable form and nothing else.
    reach = {'qing_reform': 100, 'qing_army_loyalty': 100, 'qing_provincial_trust': 100,
             'qing_yuan_influence': 100}
    scenarios = [
        # (label, country, expected outcome)
        ('army_holds_beijing',
         Country(flags=('qing_revolution_window_seen',), variables=reach, political_power=200,
                 controlled=(608,), at_war=('RCH',)), 'conquest'),
        ('assembly_accepts_no_capital',
         Country(flags=('qing_revolution_window_seen',), variables=reach, political_power=200),
         'reunion'),
        ('poor_and_weak',
         Country(flags=('qing_revolution_window_seen',), political_power=10), 'partition'),
        ('no_window', Country(variables=reach, political_power=200, controlled=(608,),
                              at_war=('RCH',)), 'refused: guard'),
        ('window_closed',
         Country(flags=('qing_revolution_window_seen', 'qing_armistice_closed'),
                 variables=reach, political_power=200, controlled=(608,)), 'refused: guard'),
        ('ai_historical',
         Country(flags=('qing_revolution_window_seen',), historical=True, ai=True,
                 variables=reach, political_power=200, controlled=(608,)), 'refused: guard'),
    ]
    for label, country, expected in scenarios:
        actual = settle_route(effects, evaluator, country)
        if actual != expected:
            failures.append('the settlement %s is %r for %s (%s), expected %r'
                            % (label, actual, label, country.label(), expected))
        note('settlement %s: %s' % (label, actual))

    # The three outcomes must be distinct: no two may be the same shape.
    shapes = {}
    for name, outcome in OUTCOME_EFFECTS.items():
        body = effect_body(effects, name)
        if body is not None:
            shapes[outcome] = str(normalize(body))
    if len(set(shapes.values())) != len(shapes):
        failures.append('the three settlement outcomes are not distinct')

    # Mutant control: the baseline annexes unconditionally with no armistice at all.
    baseline_settlement = effect_body(baseline[EFFECTS_PATH], 'qing_end_revolution')
    if baseline_settlement is None:
        failures.append('the baseline qing_end_revolution is missing')
    else:
        flat = str(normalize(baseline_settlement))
        if 'annex_country' not in flat:
            failures.append('the baseline qing_end_revolution no longer annexes, so the control '
                            'proves nothing about the repair')
        else:
            note('baseline qing_end_revolution annexes directly: as audited')
        if 'qing_armistice_open' in flat:
            failures.append('the baseline already had an armistice gate, so the control is '
                            'vacuous')
    return failures


# ---------------------------------------------------------------------------------------------
# Section 5: the reclaim sweep is closed to the scenario's own states
# ---------------------------------------------------------------------------------------------

def check_reclaim_sweep(shipped, baseline):
    failures = []
    expected, ceded, outside = scenario_reclaim_set()
    note('derived reclaim set: %d states' % len(expected))

    body = effect_body(shipped[OWNERSHIP_PATH], 'endsieg_china_reclaim_states')
    if body is None:
        return ['endsieg_china_reclaim_states is missing']
    every = block(body, 'every_state')
    if every is None:
        return ['endsieg_china_reclaim_states has no every_state']
    limit = block(every, 'limit')
    if limit is None:
        return ['the reclaim sweep has no limit']

    state_ids = sorted(int(value[1]) for key, value, _line in limit
                       if key == 'state' and value[0] == 'scalar')
    if not state_ids:
        # The ids may sit inside the first OR block rather than directly in the limit.
        for key, value, _line in limit:
            if key == 'OR' and value[0] == 'block':
                state_ids = sorted(int(inner_value[1]) for inner, inner_value, _inner_line
                                   in value[1]
                                   if inner == 'state' and inner_value[0] == 'scalar')
                if state_ids:
                    break
    if not state_ids:
        return ['the reclaim sweep lists no state ids']
    if state_ids != sorted(expected):
        missing = sorted(expected - set(state_ids))
        extra = sorted(set(state_ids) - expected)
        failures.append('the reclaim sweep is not the scenario set: missing %s, extra %s'
                        % (missing, extra))
    note('script reclaim set: %d states' % len(state_ids))

    if FOREIGN_LEASE_STATE in state_ids:
        failures.append('the reclaim sweep still takes state %d (Qingdao), which the 1910 '
                        'scenario cedes to Germany' % FOREIGN_LEASE_STATE)
    if any(key == 'is_on_continent' for key, _value, _line in limit):
        failures.append('the reclaim sweep still selects whole continents')
    if ceded and not ceded.isdisjoint(state_ids):
        failures.append('the reclaim sweep includes states the scenario cedes: %s'
                        % sorted(ceded & set(state_ids)))
    for state_id in outside:
        if state_id in state_ids and state_id not in expected:
            failures.append('the reclaim sweep takes state %d from a non-Chinese successor'
                            % state_id)

    # The tag guard stays: a state held by Japan, Tibet or Mongolia is not seized back.
    tag_or = None
    for key, value, _line in limit:
        if key == 'OR' and value[0] == 'block' \
                and any(inner == 'is_owned_by' for inner, _v, _l in value[1]):
            tag_or = value[1]
            break
    if tag_or is None:
        failures.append('the reclaim sweep has no successor-tag guard')
    else:
        guarded = {value[1] for key, value, _line in tag_or if key == 'is_owned_by'}
        if not guarded <= SUCCESSOR_TAGS:
            failures.append('the reclaim sweep takes states from tags outside the successor '
                            'family: %s' % sorted(guarded - SUCCESSOR_TAGS))

    # The core grant must live inside the closed loop and nowhere else.
    core_grants = str(normalize(body)).count("'add_core_of'")
    if core_grants != 1:
        failures.append('the reclaim sweep grants cores %d times' % core_grants)
    elif 'add_core_of' not in keys_of(every):
        failures.append('the core grant is outside the state loop')

    # Mutant control: the baseline is the continent sweep.
    baseline_body = effect_body(baseline[OWNERSHIP_PATH], 'endsieg_china_reclaim_states')
    baseline_flat = str(normalize(baseline_body)) if baseline_body is not None else ''
    if 'is_on_continent' not in baseline_flat:
        failures.append('the baseline sweep is not the continent sweep, so the control proves '
                        'nothing')
    if '743' not in baseline_flat:
        failures.append('the baseline sweep does not take state 743, so the control is vacuous')
    note('baseline sweep: continent-wide with state 743')

    # A partition must not be undone by the bookkeeping repair.
    tick = effect_body(shipped[EFFECTS_PATH], 'qing_campaign_tick')
    repairs = [body for key, body, _path in find_deep(
        tick or [], lambda k, b, p: k == 'if'
        and any(inner == 'endsieg_china_reclaim_states' for inner in keys_of(b)))]
    if len(repairs) != 2:
        failures.append('expected two dated ownership repairs, found %d' % len(repairs))
    for repair in repairs:
        repair_limit = block(repair, 'limit')
        if repair_limit is None \
                or 'qing_settlement_partition' not in str(normalize(repair_limit)):
            failures.append('an ownership repair runs for a partitioned Qing')
    return failures


# ---------------------------------------------------------------------------------------------
# Section 6: preserved ids, options, weights and localisation
# ---------------------------------------------------------------------------------------------

def localisation_keys(text):
    keys = {}
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('l_english'):
            continue
        if ':' not in stripped:
            continue
        key, _sep, value = stripped.partition(':')
        keys[key.strip()] = value.strip()
    return keys


def check_preserved_surfaces(shipped, baseline):
    failures = []
    shipped_events = events_of(shipped[EVENTS_PATH])
    baseline_events = events_of(baseline[EVENTS_PATH])

    added = set(shipped_events) - set(baseline_events)
    removed = set(baseline_events) - set(shipped_events)
    if added != {ARMISTICE_EVENT}:
        failures.append('the event chain gained %s, expected only %s'
                        % (sorted(added), ARMISTICE_EVENT))
    if removed:
        failures.append('the event chain lost %s' % sorted(removed))

    # The only description keys that may move are the three that collided with an option of
    # the same letter, so an option d could never display its own label.
    DESCRIPTION_KEY_REPAIRS = {
        'qing_campaign.20': ('qing_campaign.20.d', 'qing_campaign.20.desc'),
        'qing_campaign.22': ('qing_campaign.22.d', 'qing_campaign.22.desc'),
        'qing_campaign.23': ('qing_campaign.23.d', 'qing_campaign.23.desc'),
    }
    for event_id in sorted(set(baseline_events) & set(shipped_events)):
        old = baseline_events[event_id]
        new = shipped_events[event_id]
        for field in ('title', 'picture', 'is_triggered_only', 'hidden', 'fire_only_once'):
            if scalar(old, field) != scalar(new, field):
                failures.append('%s changed its %s' % (event_id, field))
        if scalar(old, 'desc') != scalar(new, 'desc'):
            before, after = DESCRIPTION_KEY_REPAIRS.get(event_id, (None, None))
            if (scalar(old, 'desc'), scalar(new, 'desc')) != (before, after):
                failures.append('%s changed its desc key from %s to %s'
                                % (event_id, scalar(old, 'desc'), scalar(new, 'desc')))
        old_options = options_of(old)
        new_options = options_of(new)
        if [scalar(option, 'name') for option in old_options] != \
                [scalar(option, 'name') for option in new_options]:
            failures.append('%s changed its option ids' % event_id)
            continue
        for old_option, new_option in zip(old_options, new_options):
            name = scalar(old_option, 'name')
            old_ai = block(old_option, 'ai_chance')
            new_ai = block(new_option, 'ai_chance')
            if normalize(old_ai or []) != normalize(new_ai or []):
                failures.append('%s changed its ai_chance' % name)
            old_effect = [entry for entry in old_option if entry[0] != 'trigger']
            new_effect = [entry for entry in new_option if entry[0] != 'trigger']
            if normalize(old_effect) != normalize(new_effect):
                failures.append('%s changed its effects' % name)
    return failures


def check_localisation(shipped, baseline):
    failures = []
    raw = (ROOT / LOCALISATION_PATH).read_bytes()
    if not raw.startswith(b'\xef\xbb\xbf'):
        failures.append('%s has no UTF-8 BOM' % LOCALISATION_PATH)
    if raw.startswith(b'\xef\xbb\xbf\xef\xbb\xbf'):
        failures.append('%s has a doubled BOM' % LOCALISATION_PATH)
    text = raw.decode('utf-8-sig')
    keys = localisation_keys(text)
    duplicates = [line.split(':')[0].strip() for line in text.split('\n')
                  if line.strip() and not line.strip().startswith('#')
                  and line.strip().split(':')[0].strip() in keys
                  and text.count(line.split(':')[0].strip() + ':') > 1]
    if duplicates:
        failures.append('duplicate localisation keys: %s' % sorted(set(duplicates)))
    if '\u00a7' in text or '\u00a3' in text:
        failures.append('%s contains a colour code or texticon' % LOCALISATION_PATH)

    events = events_of(shipped[EVENTS_PATH])
    required = []
    for event_id, event in events.items():
        required.append(scalar(event, 'title'))
        required.append(scalar(event, 'desc'))
        for option in options_of(event):
            required.append(scalar(option, 'name'))
            for key, body, _line in find_deep(
                    option, lambda key, body, path: key == 'custom_trigger_tooltip'):
                required.append(scalar(body, 'tooltip'))
    required = [key for key in required if key]
    missing = [key for key in required if key not in keys]
    if missing:
        failures.append('%d localisation keys are missing from %s: %s'
                        % (len(missing), LOCALISATION_PATH, missing[:10]))
    note('%d localisation keys required, %d present in the file' % (len(required), len(keys)))

    if ABDICATION_OPTION + '_tt' not in keys:
        failures.append('the abdication option tooltip has no localisation')
    else:
        tooltip = keys[ABDICATION_OPTION + '_tt']
        for word in ('armistice', 'reformed', 'partition', 'reunion'):
            if word not in tooltip:
                failures.append('the abdication tooltip does not explain %r' % word)
    return failures


def check_constants(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    new_sources = (shipped[TRIGGERS_PATH], shipped[EFFECTS_PATH])
    for group, name in constant_references(*new_sources):
        if group != 'qing_story':
            failures.append('unknown constant group %r' % group)
        elif name not in constants:
            failures.append('constant:qing_story.%s is used but not defined' % name)

    # The literals that stand in for constants must agree with them.
    triggers_text = shipped[TRIGGERS_PATH]
    literals = re.findall(r'has_political_power > (\d+)', triggers_text)
    expected = [constants['settlement_treasury_reunion'],
                constants['settlement_treasury_conquest']]
    if [float(value) for value in literals] != expected:
        failures.append('the treasury thresholds in the triggers (%s) do not mirror the '
                        'constants (%s)' % (literals, expected))

    macro = macros_of(shipped[EFFECTS_PATH]).get('qing_armistice_days')
    if macro != constants['armistice_days']:
        failures.append('@qing_armistice_days (%s) does not mirror armistice_days (%s)'
                        % (macro, constants['armistice_days']))
    if constants['armistice_days'] <= 0:
        failures.append('armistice_days is not a deadline')
    return failures


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------

SECTIONS = (
    ('historical gate is AI-only and applies pressure', check_historical_gate),
    ('settlement window is war-gated with a deadline', check_armistice_window),
    ('abdication option is gated and readable', check_abdication_option),
    ('three distinct outcomes replace the annexation', check_outcomes),
    ('reclaim sweep is closed to the scenario states', check_reclaim_sweep),
    ('preserved ids, options and weights', check_preserved_surfaces),
    ('localisation coverage', check_localisation),
    ('constants and their literals', check_constants),
)


def main():
    shipped = {
        TRIGGERS_PATH: read_repo(TRIGGERS_PATH),
        EFFECTS_PATH: read_repo(EFFECTS_PATH),
        EVENTS_PATH: read_repo(EVENTS_PATH),
        OWNERSHIP_PATH: read_repo(OWNERSHIP_PATH),
    }
    baseline = {
        TRIGGERS_PATH: baseline_text(TRIGGERS_PATH),
        EFFECTS_PATH: baseline_text(EFFECTS_PATH),
        EVENTS_PATH: baseline_text(EVENTS_PATH),
        OWNERSHIP_PATH: baseline_text(OWNERSHIP_PATH),
    }

    if '--dump' in sys.argv:
        expected, ceded, outside = scenario_reclaim_set()
        print('reclaim set (%d): %s' % (len(expected), sorted(expected)))
        print('ceded (%d): %s' % (len(ceded), sorted(ceded)))
        print('outside the successor family (%d): %s' % (len(outside), sorted(outside)))
        print('constants: %s' % constants_of(read_repo(CONSTANTS_PATH)))
        return 0

    failures = []
    per_section = []
    for title, check in SECTIONS:
        try:
            found = check(shipped, baseline)
        except Unsupported as exc:
            found = ['unsupported script shape: %s' % exc]
        per_section.append((title, found))
        failures.extend('%s: %s' % (title, failure) for failure in found)

    for title, found in per_section:
        print('%-55s %s' % (title, 'PASS' if not found else 'FAIL (%d)' % len(found)))
        for failure in found:
            print('    - ' + failure)

    if failures:
        print('\n%d check(s) failed' % len(failures))
        return 1
    print('\nall checks passed against %s; the baseline mutant is rejected' % BASELINE_REV[:12])
    return 0


if __name__ == '__main__':
    sys.exit(main())
