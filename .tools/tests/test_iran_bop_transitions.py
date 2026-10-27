"""Regression test: Iran's regime transitions, Pahlavi agreements, decree veto and party id.

Four source-proven defects from the I1 audit of the landed I3 Crown/Majlis integration are checked
here against the shipped script:

    1. **Pahlavi foreign agreements.**  Under the 1925 Pahlavi settlement `PER_bop_sync` removes
       the balance of power and clears the side flags, so an `available` block that needs
       `PER_bop_crown_side` or `power_balance_value > -0.10` can never be satisfied again: all
       four agreements were permanently greyed out.  They now also accept "the Court rules alone"
       (`NOT = { has_power_balance = { id = PER_crown_and_majlis } }`), the pattern the coup
       decisions and the negotiation options already use.
    2. **Regime shifts out of Pahlavi.**  Two layered faults.  A shift ran its settlement push
       first, which is guarded by `has_power_balance` and therefore did nothing, and then
       `PER_bop_sync` decided the balance from scratch: `iran_story.bop_opening_interwar` is
       -0.15, so a republic or a socialist state was created in `PER_bop_crown_ascendant` with
       `PER_bop_crown_side` set.  Each shift now opens the balance at the constitutional centre
       (`PER_bop_open_regime`) before its own settlement push places it.  Separately,
       `PER_bop_sync` read `PER_pahlavi_dynasty` as the autocracy, but `iran_shift_to_constitutional`
       keeps the Shah and binds him, so that one shift lost the balance it had just created and had
       `iran_pahlavi_autocracy` re-added: its settlement was a silent no-op and the country ended
       with no balance at all.  The autocracy branch of `PER_bop_sync` - and the 1941 resurgence
       test that shares it - now also require that no successor regime has been proclaimed.
    3. **The decree veto.**  `iran_decree_treaty` was set by four negotiation options and cleared
       nowhere, so `PER_bop_budget_vote` - the yearly mission that is the core loop of the whole
       balance - could never be completed again.  It is now a timed flag.
    4. **The socialist party id.**  `iran_shift_to_socialist` installed `ruling_party = communist`,
       which is not an ideology id, so the party could never be installed.  The id is `communism`.

The test reads the shipped sources rather than restating them:

    1. `common/decisions/iran_foreign_agreements.txt` - the four agreements, evaluated against
       declared country states,
    2. `common/scripted_effects/iran_regime_shift.txt` - the five shifts and the order of their
       calls,
    3. `common/scripted_effects/PER_bop_effects.txt` - the settlement pushes, the centre pull, the
       new regime opening effect, the balance values they use and the two regime tests
       (`PER_bop_sync`, `PER_bop_resurgence_check`),
    4. `common/bop/PER.txt` - the ranges, their bounds and the side flag each range sets,
    5. `common/script_constants/iran_campaign.txt` - the opening, centre and budget values,
    6. `events/iran_negotiations.txt` - the four decree options and their duration macro,
    7. `common/decisions/PER_crown_and_majlis.txt` - the budget-vote gate and its own cycle,
    8. `common/ideologies/00_ideologies.txt` - the ideology ids that actually exist.

Every defect check also runs against the pinned pre-repair revision and must reject it, which is
the mutant control: a check that passes both revisions would prove nothing.

Run from the repository root:

    python .tools/tests/test_iran_bop_transitions.py           # exit 0 = pass
    python .tools/tests/test_iran_bop_transitions.py --detail  # print every check
    python .tools/tests/test_iran_bop_transitions.py --dump    # print the parsed model

This is a source check.  It proves what the script says under the country states it is given; it
does not prove what the engine does when a player clicks the decision.  No game is launched.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

AGREEMENTS_PATH = 'common/decisions/iran_foreign_agreements.txt'
SHIFTS_PATH = 'common/scripted_effects/iran_regime_shift.txt'
BOP_EFFECTS_PATH = 'common/scripted_effects/PER_bop_effects.txt'
BOP_PATH = 'common/bop/PER.txt'
CONSTANTS_PATH = 'common/script_constants/iran_campaign.txt'
NEGOTIATIONS_PATH = 'events/iran_negotiations.txt'
BUDGET_PATH = 'common/decisions/PER_crown_and_majlis.txt'
IDEOLOGIES_PATH = 'common/ideologies/00_ideologies.txt'

# The pre-repair revision, which is the state every defect below was audited in. Pinned by full
# object name: a mutable `HEAD` stops being a mutant as soon as the repair is committed.
BASELINE_REV = 'f6d12527cc8a3ed3cda6e533528f46bbba4d6e17'

BALANCE_ID = 'PER_crown_and_majlis'
CROWN_FLAG = 'PER_bop_crown_side'
MAJLIS_FLAG = 'PER_bop_majlis_side'

AGREEMENTS = (
    'iran_accept_british_loan',
    'iran_accept_northern_railway',
    'iran_accept_military_mission',
    'iran_accept_customs_officers',
)

# shift effect -> (settlement effect, expected range, expected side flag)
SHIFTS = {
    'iran_shift_to_qajar': ('PER_bop_settle_qajar', 'PER_bop_crown_ascendant', CROWN_FLAG),
    'iran_shift_to_republic': ('PER_bop_settle_republic', 'PER_bop_majlis_ascendant', MAJLIS_FLAG),
    'iran_shift_to_constitutional': ('PER_bop_settle_constitution',
                                     'PER_bop_constitutional_settlement', None),
    'iran_shift_to_socialist': ('PER_bop_settle_socialist', 'PER_bop_majlis_ascendant',
                                MAJLIS_FLAG),
    'iran_shift_to_nationalist': ('PER_bop_settle_nationalist', 'PER_bop_crown_ascendant',
                                  CROWN_FLAG),
}
OPEN_EFFECT = 'PER_bop_open_regime'
SYNC_EFFECT = 'PER_bop_sync'
RESURGENCE_EFFECT = 'PER_bop_resurgence_check'
CLEAR_FLAGS_EFFECT = 'iran_clear_regime_flags'
AUTOCRACY_IDEA = 'iran_pahlavi_autocracy'
RESURGENCE_FLAG = 'PER_majlis_resurgence'

# The regime flag each shift proclaims. These are the same flags iran_clear_regime_flags clears, and
# a proclaimed one means the country is no longer the Pahlavi autocracy even when the dynasty remains.
SHIFT_REGIME = {
    'iran_shift_to_qajar': 'iran_qajar_restoration',
    'iran_shift_to_republic': 'iran_republic',
    'iran_shift_to_constitutional': 'iran_constitutional_monarchy',
    'iran_shift_to_socialist': 'iran_socialist',
    'iran_shift_to_nationalist': 'iran_nationalist_front',
}
SUCCESSOR_FLAGS = tuple(SHIFT_REGIME[name] for name in sorted(SHIFT_REGIME))

# The flags a country holds when it leaves the Pahlavi autocracy, and the balance state with them.
# `iran_initialize_campaign` sets the first set for any start after 1925.12.14. A pre-1925 start
# played forward reaches the 1936 chapter through the PER_pahlavi_dynasty focus, which sets the
# dynasty flag without iran_pahlavi. In both cases no balance exists: PER_bop_sync has already
# removed it, which is the whole reason a shift has to open one.
PAHLAVI_START_FLAGS = frozenset(('iran_campaign_active', 'iran_pahlavi', 'PER_pahlavi_dynasty',
                                 'iran_regime_settled'))
FOCUS_PAHLAVI_START_FLAGS = frozenset(('iran_campaign_active', 'PER_pahlavi_dynasty'))
START_STATES = (('1936_pahlavi_start', PAHLAVI_START_FLAGS),
                ('pre_1925_played_forward', FOCUS_PAHLAVI_START_FLAGS))

DECREE_FLAG = 'iran_decree_treaty'
DECREE_OPTION_COUNT = 4
DECREE_SETTING_FOLDERS = ('events', 'common/decisions', 'common/scripted_effects',
                          'common/national_focus')


class Unsupported(Exception):
    """A script shape this check does not model. Failing loudly beats guessing."""


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
            # `has_political_power > 99` and `value > -0.10`: a comparison, not an assignment.
            if index + 2 < len(tokens) and tokens[index + 1][0] == 'word' \
                    and tokens[index + 1][1] in OPERATORS and tokens[index + 2][0] == 'word':
                entries.append((text, ('compare', tokens[index + 1][1], tokens[index + 2][1]),
                                line))
                index += 3
                continue
            # A bare token: province lists and other whitespace-separated value lists.
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


def compare_entry(entries, key):
    """The (operator, operand) of a `key > value` comparison."""
    for entry_key, value, _line in entries:
        if entry_key == key and value[0] == 'compare':
            return value[1], value[2]
    return None


def macros_of(text):
    """@name = value file macros, which day fields and balance values are written with."""
    found = {}
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped.startswith('@'):
            continue
        parts = stripped.split()
        if len(parts) >= 3 and parts[1] == '=':
            try:
                found[parts[0][1:]] = float(parts[2])
            except ValueError:
                raise Unsupported('macro %s is not numeric: %r' % (parts[0], parts[2]))
    return found


def as_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        raise Unsupported('%r is not a number' % (text,))


def resolve(token, macros):
    if token is None:
        raise Unsupported('missing value')
    if token.startswith('@'):
        name = token[1:]
        if name not in macros:
            raise Unsupported('macro %s is used but not defined' % name)
        return macros[name]
    return as_number(token)


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


def effect_body(text, name):
    for key, value, _line in parse_text(text):
        if key == name and value[0] == 'block':
            return value[1]
    return None


def calls_of(body):
    """The scripted-effect calls in a body, in document order."""
    return [key for key, value, _line in body
            if value[0] == 'scalar' and value[1] == 'yes']


# ---------------------------------------------------------------------------------------------
# Decisions in one file
# ---------------------------------------------------------------------------------------------

DECISION_FIELDS = frozenset((
    'icon', 'allowed', 'visible', 'available', 'activation', 'cost', 'priority',
    'fire_only_once', 'days_re_enable', 'days_remove', 'days_mission_timeout', 'is_good',
    'complete_effect', 'timeout_effect', 'ai_will_do', 'selectable_mission', 'cancel_trigger',
    'cancel_effect', 'targets', 'target_trigger', 'target_root_trigger', 'state_trigger',
))


def decision_scopes(text):
    """[(category, body)] for the top-level decision categories of a decision file."""
    scopes = [(key, value[1]) for key, value, _line in parse_text(text) if value[0] == 'block']
    if not scopes:
        raise Unsupported('no decision categories found')
    return scopes


def decision_bodies(text):
    """decision id -> body, for every decision in one decision file."""
    found = {}
    for _category, body in decision_scopes(text):
        for key, value, _line in body:
            if key in DECISION_FIELDS or value[0] != 'block':
                continue
            found[key] = value[1]
    if not found:
        raise Unsupported('no decisions found')
    return found


def available_of(body):
    available = block(body, 'available')
    if available is None:
        raise Unsupported('decision without an available block')
    return available


# ---------------------------------------------------------------------------------------------
# Country-state model and trigger evaluation (agreement availability)
# ---------------------------------------------------------------------------------------------

class Country:
    def __init__(self, flags=(), balance=None, political_power=200, variables=None):
        self.flags = set(flags)
        self.balance = balance
        self.political_power = political_power
        self.variables = dict(variables or {})

    def label(self):
        side = 'no balance' if self.balance is None else 'balance %+.2f' % self.balance
        return '%s, %s' % (sorted(self.flags) or ['no flags'], side)


# Every declared state holds the other requirements open, so each one measures the balance gate
# alone: the patron influence the military mission wants and the sovereignty the customs
# agreement wants are both satisfied.
SCENARIO_VARIABLES = {'iran_british_influence': 50, 'iran_northern_influence': 50,
                      'iran_sovereignty': 100}


def balance_gate(available):
    """The OR in `available` that asks who can carry the agreement.

    The military mission has a second OR for patron influence, so the gate is the OR that mentions
    the balance or the Crown-side flag, not simply the first one in the block.
    """
    for key, value, _line in available:
        if key != 'OR' or value[0] != 'block':
            continue
        names = [inner for inner, _, _ in value[1]]
        if 'power_balance_value' in names or 'has_country_flag' in names \
                or 'has_power_balance' in names:
            return value[1]
    return None


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


def eval_trigger(entries, country):
    """Evaluate one trigger block for one country state. Unmodelled shapes raise Unsupported."""
    result = True
    for key, value, line in entries:
        if key in ('OR', 'AND', 'NOT'):
            if value[0] != 'block':
                raise Unsupported('%s without a block at line %d' % (key, line))
            if key == 'OR':
                outcome = any(eval_trigger([entry], country) for entry in value[1])
            else:
                outcome = eval_trigger(value[1], country)
                if key == 'NOT':
                    outcome = not outcome
            result = result and outcome
        elif key == 'always':
            result = result and (value[0] == 'scalar' and value[1] == 'yes')
        elif key == 'has_country_flag':
            if value[0] != 'scalar':
                raise Unsupported('has_country_flag block at line %d' % line)
            result = result and value[1] in country.flags
        elif key == 'has_power_balance':
            if value[0] != 'block' or scalar(value[1], 'id') != BALANCE_ID:
                raise Unsupported('has_power_balance shape at line %d' % line)
            result = result and country.balance is not None
        elif key == 'power_balance_value':
            if value[0] != 'block':
                raise Unsupported('power_balance_value shape at line %d' % line)
            comparison = compare_entry(value[1], 'value')
            if comparison is None:
                raise Unsupported('power_balance_value comparison at line %d' % line)
            operator, operand = comparison[0], as_number(comparison[1])
            if country.balance is None:
                result = False
            else:
                result = result and SYMBOL[operator](country.balance, operand)
        elif key == 'has_political_power':
            if value[0] != 'compare':
                raise Unsupported('has_political_power shape at line %d' % line)
            result = result and SYMBOL[value[1]](country.political_power, as_number(value[2]))
        elif key == 'check_variable':
            if value[0] != 'block':
                raise Unsupported('check_variable shape at line %d' % line)
            name = scalar(value[1], 'var')
            quoted = scalar(value[1], 'value')
            comparer = scalar(value[1], 'compare')
            if name is None or quoted is None or comparer not in COMPARE:
                raise Unsupported('check_variable shape at line %d' % line)
            left = country.variables.get(name, 0.0)
            result = result and COMPARE[comparer](left, as_number(quoted))
        else:
            raise Unsupported('trigger %r at line %d is not modelled' % (key, line))
    return result


# ---------------------------------------------------------------------------------------------
# D1: the four agreements under Pahlavi rule
# ---------------------------------------------------------------------------------------------

def agreement_failures(text):
    """D1 failures for one version of the agreement decision file."""
    failures = []
    decisions = decision_bodies(text)

    def fail(message):
        failures.append(message)

    scenarios = [
        ('pahlavi_rule_alone', Country(flags=('iran_campaign_active', 'iran_pahlavi'),
                                       balance=None,
                                       variables=SCENARIO_VARIABLES), True),
        ('crown_ascendant', Country(flags=(CROWN_FLAG,), balance=-0.20,
                                    variables=SCENARIO_VARIABLES), True),
        ('majlis_ascendant', Country(flags=(MAJLIS_FLAG,), balance=0.30,
                                     variables=SCENARIO_VARIABLES), True),
        # The one state the gate is meant to refuse: a balance pushed to the Crown, without the
        # Crown-side flag. Adding the no-balance branch must not open this one.
        ('crown_dominant_without_flag', Country(balance=-0.50,
                                                variables=SCENARIO_VARIABLES), False),
    ]

    for decision_id in AGREEMENTS:
        if decision_id not in decisions:
            fail('%s is missing from the agreement category' % decision_id)
            continue
        available = available_of(decisions[decision_id])
        alternatives = balance_gate(available)
        if alternatives is None:
            fail('%s has no OR between the Crown and the Majlis' % decision_id)
            continue
        has_no_balance = any(
            key == 'NOT' and value[0] == 'block'
            and any(name == 'has_power_balance' for name, _, _ in value[1])
            for key, value, _line in alternatives)
        has_crown_flag = any(key == 'has_country_flag' and value[0] == 'scalar'
                             and value[1] == CROWN_FLAG for key, value, _line in alternatives)
        has_balance_limit = any(key == 'power_balance_value' for key, _, _line in alternatives)
        if not has_no_balance:
            fail('%s does not accept "the Court rules alone" (no power balance)' % decision_id)
        if not has_crown_flag:
            fail('%s no longer accepts the Crown-side flag' % decision_id)
        if not has_balance_limit:
            fail('%s no longer accepts a balance above -0.10' % decision_id)

        for label, country, expected in scenarios:
            actual = eval_trigger(available, country)
            if actual != expected:
                fail('%s is %s under %s (%s), expected %s'
                     % (decision_id, 'available' if actual else 'unavailable', label,
                        country.label(), 'available' if expected else 'unavailable'))

    # Nothing outside the four availability gates may move.
    old = decision_bodies(baseline_text(AGREEMENTS_PATH))
    if set(old) != set(decisions):
        fail('the decision ids in %s changed: %s'
             % (AGREEMENTS_PATH, sorted(set(old) ^ set(decisions))))
    for decision_id in sorted(set(old) & set(decisions)):
        old_rest = [entry for entry in old[decision_id] if entry[0] != 'available']
        new_rest = [entry for entry in decisions[decision_id] if entry[0] != 'available']
        if normalize(old_rest) != normalize(new_rest):
            fail('%s changed outside its available block' % decision_id)
    return failures


# ---------------------------------------------------------------------------------------------
# D2: what a regime shift does to the balance
# ---------------------------------------------------------------------------------------------

def balance_ranges(text):
    """[(range id, min, max, side flag set on activation or None)] from common/bop/PER.txt."""
    definition = None
    for key, value, _line in parse_text(text):
        if key == BALANCE_ID and value[0] == 'block':
            definition = value[1]
    if definition is None:
        raise Unsupported('%s not found in %s' % (BALANCE_ID, BOP_PATH))

    ranges = []

    def walk(entries):
        for key, value, _line in entries:
            if value[0] != 'block':
                continue
            if key == 'side':
                walk(value[1])
            elif key == 'range':
                body = value[1]
                range_id = scalar(body, 'id')
                low, high = scalar(body, 'min'), scalar(body, 'max')
                if range_id is None or low is None or high is None:
                    raise Unsupported('range without id/min/max in %s' % BOP_PATH)
                activation = block(body, 'on_activate') or []
                set_flags = [inner[1] for name, inner, _line in activation
                             if name == 'set_country_flag' and inner[0] == 'scalar']
                # The settlement range sets PER_bop_settled, which is not a side.
                side = next((flag for flag in set_flags if flag in (CROWN_FLAG, MAJLIS_FLAG)), None)
                ranges.append((range_id, as_number(low), as_number(high), side))

    walk(definition)
    if not ranges:
        raise Unsupported('no ranges parsed from %s' % BOP_PATH)
    return ranges


def range_for(value, ranges):
    """The one range that contains a value. A boundary hit fails loudly rather than guessing."""
    matches = [entry for entry in ranges if entry[1] <= value <= entry[2]]
    if len(matches) != 1:
        raise Unsupported('value %+.3f falls in %d ranges: %s'
                          % (value, len(matches), [entry[0] for entry in matches]))
    return matches[0]


def balance_values(effects_text):
    """The signed balance values the pushes use, resolved through the file's macros."""
    macros = macros_of(effects_text)
    pushes = {}
    for key, value, _line in parse_text(effects_text):
        if not key.startswith('PER_bop_push_') or value[0] != 'block':
            continue
        hidden = block(value[1], 'hidden_effect')
        if hidden is None:
            raise Unsupported('%s has no hidden_effect' % key)
        guard = False
        amount = None
        for inner_key, inner_value, _line in hidden:
            if inner_key != 'if' or inner_value[0] != 'block':
                continue
            body = inner_value[1]
            limit = block(body, 'limit')
            if limit is None or not any(name == 'has_power_balance' for name, _, _ in limit):
                raise Unsupported('%s is not guarded by has_power_balance' % key)
            guard = True
            add = block(body, 'add_power_balance_value')
            if add is None or scalar(add, 'id') != BALANCE_ID:
                raise Unsupported('%s does not move %s' % (key, BALANCE_ID))
            amount = resolve(scalar(add, 'value'), macros)
        if not guard or amount is None:
            raise Unsupported('%s has no guarded value' % key)
        pushes[key] = amount
    if not pushes:
        raise Unsupported('no PER_bop_push_* effects found')
    return pushes, macros


def pull_to_centre(effects_text):
    """(threshold, step) for PER_bop_pull_to_centre, read from its own comparisons."""
    body = effect_body(effects_text, 'PER_bop_pull_to_centre')
    if body is None:
        raise Unsupported('PER_bop_pull_to_centre not found')
    thresholds = []
    steps = []
    for key, value, _line in body:
        if key != 'hidden_effect' or value[0] != 'block':
            continue
        for inner_key, inner_value, _line in value[1]:
            if inner_key != 'if' or inner_value[0] != 'block':
                continue
            for branch_key, branch_value, _line in inner_value[1]:
                if branch_key not in ('if', 'else_if') or branch_value[0] != 'block':
                    continue
                branch = branch_value[1]
                for test_key, test_value, _line in block(branch, 'limit') or []:
                    if test_key == 'power_balance_value' and test_value[0] == 'block':
                        comparison = compare_entry(test_value[1], 'value')
                        if comparison is not None:
                            thresholds.append(abs(as_number(comparison[1])))
                add = block(branch, 'add_power_balance_value')
                if add is not None:
                    steps.append(abs(as_number(scalar(add, 'value'))))
    if not thresholds or not steps:
        raise Unsupported('PER_bop_pull_to_centre thresholds were not parsed')
    if len(set(thresholds)) != 1 or len(set(steps)) != 1:
        raise Unsupported('PER_bop_pull_to_centre uses different thresholds: %s %s'
                          % (thresholds, steps))
    return thresholds[0], steps[0]


def regime_opening(effects_text):
    """The value PER_bop_open_regime creates the balance with, or None when it does not exist."""
    body = effect_body(effects_text, OPEN_EFFECT)
    if body is None:
        return None
    hidden = block(body, 'hidden_effect')
    if hidden is None:
        raise Unsupported('%s has no hidden_effect guard' % OPEN_EFFECT)
    for key, value, _line in hidden:
        if key != 'if' or value[0] != 'block':
            continue
        inner = value[1]
        limit = block(inner, 'limit')
        if limit is None:
            raise Unsupported('%s has no guard' % OPEN_EFFECT)
        guarded_by_absence = any(
            name == 'NOT' and entry[0] == 'block'
            and any(inner_name == 'has_power_balance' for inner_name, _, _ in entry[1])
            for name, entry, _line in limit)
        if not guarded_by_absence:
            raise Unsupported('%s does not check that the balance is absent' % OPEN_EFFECT)
        created = block(inner, 'set_power_balance')
        if created is None or scalar(created, 'id') != BALANCE_ID:
            raise Unsupported('%s does not create %s' % (OPEN_EFFECT, BALANCE_ID))
        return scalar(created, 'set_value')
    raise Unsupported('%s has no creation branch' % OPEN_EFFECT)


def constant(constants_text, name):
    body = block(parse_text(constants_text), 'iran_story')
    if body is None:
        raise Unsupported('no iran_story constants block')
    token = scalar(body, 'bop_' + name)
    if token is None:
        raise Unsupported('iran_story.bop_%s is not defined' % name)
    return as_number(token)


def settle_pushes(effects_text):
    """settlement effect -> the push effect it calls."""
    pushes = {}
    for key, value, _line in parse_text(effects_text):
        if not key.startswith('PER_bop_settle_') or value[0] != 'block':
            continue
        called = [name for name, inner, _line in value[1]
                  if inner[0] == 'scalar' and inner[1] == 'yes']
        if len(called) != 1:
            raise Unsupported('%s calls %s effects' % (key, len(called)))
        pushes[key] = called[0]
    if not pushes:
        raise Unsupported('no PER_bop_settle_* effects found')
    return pushes


def shift_outcome(body, opening, settled, pushes, push_values, centre, threshold, step):
    """The balance value a shift leaves behind.

    `settled` says whether the settlement push can reach a live balance. A shift out of the
    Pahlavi autocracy runs with no balance, and every push is guarded by `has_power_balance`, so
    without an opening call the push is a no-op and the value that survives is the one
    `PER_bop_sync` creates afterwards - the era opening passed in as `opening`.
    """
    if not settled:
        return opening
    for name in calls_of(body):
        if name not in pushes:
            continue
        push = pushes[name]
        if push == 'PER_bop_pull_to_centre':
            if -threshold <= opening <= threshold:
                return centre
            return opening - step if opening > 0 else opening + step
        if push not in push_values:
            raise Unsupported('%s calls unknown push %s' % (name, push))
        return opening + push_values[push]
    raise Unsupported('a shift calls no settlement effect')


def shift_failures(text, effects_text, constants_text, ranges):
    """D2 failures for one version of the regime-shift file."""
    failures = []
    pushes = settle_pushes(effects_text)
    push_values, _macros = balance_values(effects_text)
    threshold, step = pull_to_centre(effects_text)
    token = regime_opening(effects_text)
    if token is None:
        centre = None
    else:
        if not token.startswith('constant:iran_story.'):
            failures.append('%s opens the balance with %r, not an iran_story constant'
                            % (OPEN_EFFECT, token))
        centre = constant(constants_text, 'centre')
    era_openings = {'pre_1919': constant(constants_text, 'opening_constitutional'),
                    '1936_interwar': constant(constants_text, 'opening_interwar')}

    for name, (settle, expected_range, expected_flag) in SHIFTS.items():
        body = effect_body(text, name)
        if body is None:
            failures.append('%s is missing' % name)
            continue
        if settle not in pushes:
            failures.append('%s calls %s, which is not a settlement effect' % (name, settle))
            continue
        ordered = calls_of(body)
        if SYNC_EFFECT not in ordered:
            failures.append('%s no longer syncs the regime' % name)
        if token is None:
            openings = era_openings
            settled = False
        else:
            if OPEN_EFFECT not in ordered:
                failures.append('%s never opens the balance, so its settlement can only be a '
                                'no-op' % name)
                continue
            if ordered.index(OPEN_EFFECT) > ordered.index(settle):
                failures.append('%s pushes its settlement before it opens the balance' % name)
                continue
            if SYNC_EFFECT in ordered and ordered.index(SYNC_EFFECT) < ordered.index(settle):
                failures.append('%s syncs the regime before the settlement pushes it' % name)
            openings = {'regime_opening': centre}
            settled = True
        for era, start in openings.items():
            value = shift_outcome(body, start, settled, pushes, push_values, centre, threshold,
                                  step)
            range_id, _low, _high, flag = range_for(value, ranges)
            if range_id != expected_range or flag != expected_flag:
                failures.append('%s from %s (%+.2f) lands at %+.2f in %s%s, expected %s%s'
                                % (name, era, start, value, range_id,
                                   ' with ' + flag if flag else '', expected_range,
                                   ' with ' + expected_flag if expected_flag else ''))
    return failures


# ---------------------------------------------------------------------------------------------
# D2 (post-sync): the autocracy test must not swallow a proclaimed successor regime
# ---------------------------------------------------------------------------------------------

def _first_if(entries, where):
    """The body of the first `if = { }` in a block."""
    for key, value, _line in entries:
        if key == 'if' and value[0] == 'block':
            return value[1]
    raise Unsupported('%s: no if branch found' % where)


def regime_limit(effects_text, effect_name, depth):
    """(limit, branch body) of an effect's regime test.

    `PER_bop_sync` wraps its regime test inside the campaign and DLC guard, so its branch sits one
    level deeper than the single `if` of `PER_bop_resurgence_check`.
    """
    body = effect_body(effects_text, effect_name)
    if body is None:
        raise Unsupported('%s is missing from %s' % (effect_name, BOP_EFFECTS_PATH))
    entries = block(body, 'hidden_effect')
    if entries is None:
        raise Unsupported('%s has no hidden_effect' % effect_name)
    for _step in range(depth):
        entries = _first_if(entries, effect_name)
    limit = block(entries, 'limit')
    if not limit:
        raise Unsupported('%s: the regime branch has no limit' % effect_name)
    return limit, entries


def flag_names(entries):
    """Every flag named by a has_country_flag below `entries`."""
    names = set()
    for key, value, _line in entries:
        if key == 'has_country_flag' and value[0] == 'scalar':
            names.add(value[1])
        elif value[0] == 'block':
            names |= flag_names(value[1])
    return names


def accepts_flag(entries, flag):
    """True when the block itself asks for the flag, outside any NOT."""
    for key, value, _line in entries:
        if key == 'has_country_flag' and value[0] == 'scalar' and value[1] == flag:
            return True
        if key in ('OR', 'AND') and value[0] == 'block' and accepts_flag(value[1], flag):
            return True
    return False


def excludes_flag(limit, flag):
    """True when some NOT branch of the limit rules the flag out."""
    for key, value, _line in limit:
        if key == 'NOT' and value[0] == 'block' and flag in flag_names(value[1]):
            return True
    return False


def effects_named(entries, target):
    """Every value of an effect call named `target` below `entries`."""
    found = []
    for key, value, _line in entries:
        if key == target:
            found.append(value)
        elif value[0] == 'block':
            found.extend(effects_named(value[1], target))
    return found


def regime_only(limit):
    """The flag branches of a limit, with the campaign and date guards left out.

    Only the question "does the regime test admit this country state" is asked of these blocks; the
    campaign and DLC guards around them are taken as satisfied, because the whole subsystem is
    inert without them (`iran_campaign_active`, `has_dlc`). The sync limit contains nothing but
    flags, so this is used only for the resurgence test.
    """
    return [entry for entry in limit
            if entry[0] in ('OR', 'NOT', 'AND')
            or (entry[0] == 'has_country_flag' and entry[1][0] == 'scalar')]


def shift_flags(shifts_text, name):
    """(cleared, set) country flags one shift leaves behind, expanding iran_clear_regime_flags."""
    body = effect_body(shifts_text, name)
    if body is None:
        raise Unsupported('%s is missing from %s' % (name, SHIFTS_PATH))
    clear_body = effect_body(shifts_text, CLEAR_FLAGS_EFFECT)
    if clear_body is None:
        raise Unsupported('%s is missing' % CLEAR_FLAGS_EFFECT)
    shared_clears = set()
    for key, value, _line in clear_body:
        if key == 'clr_country_flag' and value[0] == 'scalar':
            shared_clears.add(value[1])
    cleared, set_flags = set(), set()
    for key, value, _line in body:
        if key == CLEAR_FLAGS_EFFECT:
            cleared.update(shared_clears)
        elif key == 'clr_country_flag' and value[0] == 'scalar':
            cleared.add(value[1])
        elif key == 'set_country_flag' and value[0] == 'scalar':
            set_flags.add(value[1])
    return cleared, set_flags


def sync_rows(shifts_text, effects_text, constants_text, start_flags):
    """One row per shift: (name, flags left, settlement value, value after PER_bop_sync, autocracy).

    A missing `PER_bop_open_regime` is not an error here: that is the pre-repair shape, where the
    settlement push had no balance to reach and the value arriving at the sync was the era opening
    the autocracy branch had just created.
    """
    pushes = settle_pushes(effects_text)
    push_values, _macros = balance_values(effects_text)
    threshold, step = pull_to_centre(effects_text)
    centre = constant(constants_text, 'centre')
    opening = constant(constants_text, 'opening_interwar')
    limit, _branch = regime_limit(effects_text, SYNC_EFFECT, 2)
    opened = regime_opening(effects_text) is not None

    rows = []
    for name in sorted(SHIFTS):
        settle, _range, _flag = SHIFTS[name]
        body = effect_body(shifts_text, name)
        if body is None:
            raise Unsupported('%s is missing from %s' % (name, SHIFTS_PATH))
        ordered = calls_of(body)
        if settle not in ordered:
            raise Unsupported('%s no longer calls %s' % (name, settle))
        if opened:
            if OPEN_EFFECT not in ordered or ordered.index(OPEN_EFFECT) > ordered.index(settle):
                raise Unsupported('%s settles before it opens the balance' % name)
            value = shift_outcome(body, centre, True, pushes, push_values, centre, threshold,
                                  step)
        else:
            value = opening
        cleared, set_flags = shift_flags(shifts_text, name)
        flags = (frozenset(start_flags) - cleared) | set_flags
        # The autocracy branch removes the balance; the other branch leaves an existing one alone.
        autocracy = eval_trigger(limit, Country(flags=flags, balance=value))
        rows.append((name, flags, value, None if autocracy else value, autocracy))
    return rows


def sync_failures(shifts_text, effects_text, constants_text, ranges):
    """D2 post-sync failures: what each shift's balance is once PER_bop_sync has run."""
    failures = []
    limit, branch = regime_limit(effects_text, SYNC_EFFECT, 2)

    for flag in ('iran_pahlavi', 'PER_pahlavi_dynasty'):
        if not accepts_flag(limit, flag):
            failures.append('%s no longer recognises Pahlavi rule (%s)' % (SYNC_EFFECT, flag))
    for flag in SUCCESSOR_FLAGS:
        if not excludes_flag(limit, flag):
            failures.append('%s still calls a state with %s the Pahlavi autocracy'
                            % (SYNC_EFFECT, flag))
    if not effects_named(branch, 'remove_power_balance'):
        failures.append('%s no longer removes the balance under the autocracy' % SYNC_EFFECT)
    if AUTOCRACY_IDEA not in [value[1] for value in effects_named(branch, 'add_ideas')
                              if value[0] == 'scalar']:
        failures.append('%s no longer re-adds %s under the autocracy'
                        % (SYNC_EFFECT, AUTOCRACY_IDEA))

    for label, start_flags in START_STATES:
        for name, flags, settlement, value, autocracy in sync_rows(shifts_text, effects_text,
                                                                  constants_text, start_flags):
            if autocracy:
                failures.append('%s from %s re-adds %s after %s (%s)'
                                % (name, label, AUTOCRACY_IDEA, SYNC_EFFECT,
                                   ', '.join(sorted(flags))))
            if value is None:
                failures.append('%s from %s leaves no balance after %s, discarding the '
                                'settlement value %+.2f' % (name, label, SYNC_EFFECT, settlement))
                continue
            range_id, _low, _high, flag = range_for(value, ranges)
            _settle, expected_range, expected_flag = SHIFTS[name]
            if range_id != expected_range or flag != expected_flag:
                failures.append('%s from %s leaves %+.2f in %s%s, expected %s%s'
                                % (name, label, value, range_id,
                                   ' with ' + flag if flag else '', expected_range,
                                   ' with ' + expected_flag if expected_flag else ''))
    return failures


def resurgence_failures(effects_text):
    """The 1941 abdication report must not fire for a country that already has a sitting chamber."""
    failures = []
    limit, _branch = regime_limit(effects_text, RESURGENCE_EFFECT, 1)
    regime = regime_only(limit)
    for flag in SUCCESSOR_FLAGS:
        if not excludes_flag(limit, flag):
            failures.append('%s still calls a state with %s the Pahlavi autocracy'
                            % (RESURGENCE_EFFECT, flag))
    if not accepts_flag(limit, 'PER_pahlavi_dynasty'):
        failures.append('%s no longer recognises the Pahlavi dynasty' % RESURGENCE_EFFECT)
    occupied = {'iran_campaign_active', 'iran_pahlavi', 'PER_pahlavi_dynasty', 'iran_occupied'}
    if not eval_trigger(regime, Country(flags=occupied, balance=None)):
        failures.append('%s no longer fires for an occupied Pahlavi autocracy' % RESURGENCE_EFFECT)
    for flag in SUCCESSOR_FLAGS:
        state = (occupied - {'iran_pahlavi'}) | {flag}
        if eval_trigger(regime, Country(flags=state, balance=0.0)):
            failures.append('%s still fires for a proclaimed %s' % (RESURGENCE_EFFECT, flag))
    return failures


# ---------------------------------------------------------------------------------------------
# D3: the decree veto expires
# ---------------------------------------------------------------------------------------------

def decree_failures(text, budget_text):
    """D3 failures for one version of the negotiation events file."""
    failures = []
    macros = macros_of(text)
    decree_days = macros.get('decree_treaty_days')
    if decree_days is None:
        failures.append('%s defines no @decree_treaty_days macro' % NEGOTIATIONS_PATH)
    timed = []
    permanent = []

    def walk(entries):
        for key, value, _line in entries:
            if key == 'set_country_flag':
                if value[0] == 'scalar' and value[1] == DECREE_FLAG:
                    permanent.append(value[1])
                elif value[0] == 'block' and scalar(value[1], 'flag') == DECREE_FLAG:
                    timed.append(value[1])
            elif value[0] == 'block':
                walk(value[1])

    walk(parse_text(text))

    if permanent:
        failures.append('%d option(s) still set %s permanently, so the Budget Vote never '
                        'returns' % (len(permanent), DECREE_FLAG))
    if len(timed) != DECREE_OPTION_COUNT:
        failures.append('%d timed %s setters, expected %d'
                        % (len(timed), DECREE_FLAG, DECREE_OPTION_COUNT))
    for setter in timed:
        try:
            days = resolve(scalar(setter, 'days'), macros)
        except Unsupported as error:
            failures.append('a %s setter: %s' % (DECREE_FLAG, error))
            continue
        if days < 1:
            failures.append('a %s setter lasts %s days' % (DECREE_FLAG, days))

    # No other Iran-owned script may set it permanently either.
    for folder in DECREE_SETTING_FOLDERS:
        for path in sorted((ROOT / folder).rglob('*.txt')):
            if path == ROOT / NEGOTIATIONS_PATH:
                continue
            try:
                body = path.read_text(encoding='utf-8-sig', errors='replace')
            except OSError:
                continue
            if DECREE_FLAG not in body:
                continue
            for line in body.split('\n'):
                stripped = line.strip()
                if stripped.startswith('#') or DECREE_FLAG not in stripped:
                    continue
                if stripped == 'set_country_flag = %s' % DECREE_FLAG:
                    failures.append('%s still sets %s permanently'
                                    % (path.relative_to(ROOT).as_posix(), DECREE_FLAG))

    # The gate that reads the flag must exist, and the veto must be shorter than one full cycle of
    # the mission it blocks, or a single decree could still starve the core loop.
    mission = decision_bodies(budget_text).get('PER_bop_budget_vote')
    if mission is None:
        failures.append('PER_bop_budget_vote is missing from %s' % BUDGET_PATH)
        return failures
    gate = block(mission, 'available') or []
    if not any(key == 'custom_trigger_tooltip' and DECREE_FLAG in repr(value)
               for key, value, _line in gate):
        failures.append('the Budget Vote no longer reads %s, so the flag vetoes nothing'
                        % DECREE_FLAG)
    cycle_macros = macros_of(budget_text)
    if 'budget_cooldown_days' not in cycle_macros:
        failures.append('%s no longer defines @budget_cooldown_days' % BUDGET_PATH)
        return failures
    cycle = as_number(scalar(mission, 'days_mission_timeout')) + \
        cycle_macros['budget_cooldown_days']
    if decree_days is not None and decree_days > cycle:
        failures.append('a decree vetoes the Budget Vote for %d days, longer than its own '
                        '%d-day cycle' % (int(decree_days), int(cycle)))
    return failures


# ---------------------------------------------------------------------------------------------
# D4: the socialist shift installs a party that exists
# ---------------------------------------------------------------------------------------------

def ideology_ids(text):
    body = block(parse_text(text), 'ideologies')
    if body is None:
        raise Unsupported('no ideologies block in %s' % IDEOLOGIES_PATH)
    ids = set(key for key, value, _line in body if value[0] == 'block')
    if not ids:
        raise Unsupported('no ideology ids parsed')
    return ids


def socialist_failures(text, ideologies):
    failures = []
    body = effect_body(text, 'iran_shift_to_socialist')
    if body is None:
        return ['iran_shift_to_socialist is missing']
    politics = block(body, 'set_politics')
    if politics is None:
        return ['iran_shift_to_socialist no longer sets the government']
    party = scalar(politics, 'ruling_party')
    if party is None:
        return ['iran_shift_to_socialist sets no ruling party']
    if party not in ideologies:
        failures.append('iran_shift_to_socialist installs %r, which is not an ideology id (%s)'
                        % (party, ', '.join(sorted(ideologies))))
    if party != 'communism':
        failures.append('iran_shift_to_socialist installs %r, expected communism' % party)
    return failures


# ---------------------------------------------------------------------------------------------
# Preservation of the effects this repair does not touch
# ---------------------------------------------------------------------------------------------

def _is_successor_guard(key, value):
    """The `NOT = { OR = { <successor regime flags> } }` branch of a regime test."""
    return (key == 'NOT' and value[0] == 'block'
            and bool(flag_names(value[1]) & set(SUCCESSOR_FLAGS)))


def without_entry(entries, predicate):
    """A copy of the parsed tree with every entry the predicate matches removed, at any depth."""
    kept = []
    for key, value, line in entries:
        if predicate(key, value):
            continue
        if value[0] == 'block':
            kept.append((key, ('block', without_entry(value[1], predicate)), line))
        else:
            kept.append((key, value, line))
    return kept


def preserved_effect_failures(text):
    """Every pre-existing balance effect keeps its body.

    Two documented deltas are allowed, and nothing else: `PER_bop_open_regime` is added, and the
    regime test of `PER_bop_sync` and `PER_bop_resurgence_check` gains the successor-regime guard
    that `sync_failures` and `resurgence_failures` pin separately. Stripping that guard must leave
    each effect byte-for-byte equal to the pinned baseline.
    """
    failures = []
    current = dict((key, value[1]) for key, value, _line in parse_text(text)
                   if value[0] == 'block' and key.startswith('PER_bop_'))
    old = dict((key, value[1]) for key, value, _line in parse_text(
        baseline_text(BOP_EFFECTS_PATH)) if value[0] == 'block' and key.startswith('PER_bop_'))
    missing = sorted(set(old) - set(current))
    if missing:
        failures.append('%s lost %s' % (BOP_EFFECTS_PATH, missing))
    added = sorted(set(current) - set(old))
    if added != [OPEN_EFFECT]:
        failures.append('%s added %s, expected only %s' % (BOP_EFFECTS_PATH, added, OPEN_EFFECT))
    for name in sorted(set(old) & set(current)):
        body = current[name]
        if name in (SYNC_EFFECT, RESURGENCE_EFFECT):
            body = without_entry(body, _is_successor_guard)
        if normalize(old[name]) != normalize(body):
            failures.append('%s changed %s' % (BOP_EFFECTS_PATH, name))
    return failures


def preserved_shift_failures(text):
    """Every shift keeps its own effects, gains only the opening call, and fixes only the party."""
    failures = []
    current = dict((key, value[1]) for key, value, _line in parse_text(text)
                   if value[0] == 'block' and key.startswith('iran_shift_to_'))
    old = dict((key, value[1]) for key, value, _line in parse_text(baseline_text(SHIFTS_PATH))
               if value[0] == 'block' and key.startswith('iran_shift_to_'))
    if set(current) != set(old):
        failures.append('the shift effects changed: %s' % sorted(set(current) ^ set(old)))
    for name in sorted(set(old) & set(current)):
        old_rest = [entry for entry in old[name]
                    if name != 'iran_shift_to_socialist' or entry[0] != 'set_politics']
        new_rest = [entry for entry in current[name]
                    if entry[0] != OPEN_EFFECT
                    and (name != 'iran_shift_to_socialist' or entry[0] != 'set_politics')]
        if normalize(old_rest) != normalize(new_rest):
            failures.append('%s changed outside the opening call' % name)
    return failures


# ---------------------------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------------------------

class Report:
    def __init__(self, detail=False):
        self.detail = detail
        self.checks = []
        self.failures = []
        self.notes = []
        self.group = ''

    def start(self, group):
        self.group = group

    def note(self, text):
        self.notes.append(text)
        print('  note  %s' % text)

    def check(self, label, condition, detail=''):
        self.checks.append(label)
        if not condition:
            self.failures.append('%s: %s%s' % (self.group, label,
                                               (' — ' + detail) if detail else ''))
        elif self.detail:
            print('  ok  [%s] %s%s' % (self.group, label, (' — ' + detail) if detail else ''))

    def summary(self):
        print('%d checks, %d failures' % (len(self.checks), len(self.failures)))
        for failure in self.failures:
            print('  FAIL ' + failure)
        return not self.failures


def main():
    report = Report(detail='--detail' in sys.argv)
    agreements = read_repo(AGREEMENTS_PATH)
    shifts = read_repo(SHIFTS_PATH)
    effects = read_repo(BOP_EFFECTS_PATH)
    constants = read_repo(CONSTANTS_PATH)
    negotiations = read_repo(NEGOTIATIONS_PATH)
    budget = read_repo(BUDGET_PATH)
    ideologies = ideology_ids(read_repo(IDEOLOGIES_PATH))
    ranges = balance_ranges(read_repo(BOP_PATH))

    if '--dump' in sys.argv:
        pushes, _macros = balance_values(effects)
        print('ranges: %s' % [(entry[0], entry[1], entry[2], entry[3]) for entry in ranges])
        print('pushes: %s' % pushes)
        print('pull to centre: threshold %s step %s' % pull_to_centre(effects))
        print('regime opening: %s' % regime_opening(effects))
        print('decree_treaty_days: %s' % macros_of(negotiations).get('decree_treaty_days'))
        print('centre: %s interwar: %s'
              % (constant(constants, 'centre'), constant(constants, 'opening_interwar')))
        for name in SHIFTS:
            print('%s calls %s' % (name, calls_of(effect_body(shifts, name) or [])))
        for row in sync_rows(shifts, effects, constants, PAHLAVI_START_FLAGS):
            print('%s: settlement %s, after PER_bop_sync %s, autocracy %s'
                  % (row[0], row[2], row[3], row[4]))
        return 0

    report.start('balance')
    report.check('%s declares %d ranges' % (BALANCE_ID, len(ranges)), len(ranges) == 7,
                 str([entry[0] for entry in ranges]))
    report.check('zero is the constitutional settlement',
                 range_for(0.0, ranges)[0] == 'PER_bop_constitutional_settlement')
    report.check('the Crown half is negative and the Majlis half positive',
                 range_for(-0.20, ranges)[3] == CROWN_FLAG
                 and range_for(0.20, ranges)[3] == MAJLIS_FLAG)
    report.check('the era opening value sits on the autocracy side',
                 range_for(constant(constants, 'opening_interwar'), ranges)[3] == CROWN_FLAG,
                 'bop_opening_interwar = %+.2f' % constant(constants, 'opening_interwar'))

    report.start('D1-agreements')
    failures = agreement_failures(agreements)
    for failure in failures:
        report.check(failure, False)
    report.check('all four agreements are available to the Crown ruling alone', not failures,
                 '; '.join(failures))

    report.start('D1-mutant')
    old_failures = agreement_failures(baseline_text(AGREEMENTS_PATH))
    report.check('the pre-repair gate fails the check', bool(old_failures))
    report.check('the pre-repair gate is rejected for the Pahlavi state',
                 any('pahlavi_rule_alone' in failure for failure in old_failures),
                 '; '.join(old_failures))

    report.start('D2-settlement')
    failures = shift_failures(shifts, effects, constants, ranges)
    for failure in failures:
        report.check(failure, False)
    report.check('every shift lands in its own half of the range', not failures,
                 '; '.join(failures))

    report.start('D2-settlement-mutant')
    old_failures = shift_failures(baseline_text(SHIFTS_PATH), baseline_text(BOP_EFFECTS_PATH),
                                  constants, ranges)
    report.check('the pre-repair shift order fails the check', bool(old_failures))
    report.check('without the opening call only the era opening places a shift, so the republic '
                 'lands on the Crown side',
                 any('iran_shift_to_republic' in failure
                     and 'PER_bop_crown_ascendant' in failure for failure in old_failures),
                 '; '.join(old_failures))

    report.start('D2-sync')
    failures = sync_failures(shifts, effects, constants, ranges) + resurgence_failures(effects)
    for failure in failures:
        report.check(failure, False)
    report.check('every shift keeps its balance after PER_bop_sync', not failures,
                 '; '.join(failures))
    for label, start_flags in START_STATES:
        row = [entry for entry in sync_rows(shifts, effects, constants, start_flags)
               if entry[0] == 'iran_shift_to_constitutional'][0]
        value, autocracy = row[3], row[4]
        settled = (value is not None
                   and range_for(value, ranges)[0] == 'PER_bop_constitutional_settlement'
                   and range_for(value, ranges)[3] is None
                   and not autocracy)
        report.check('the constitutional shift from a %s ends in the settlement band' % label,
                     settled,
                     'balance %s, %s re-added %s'
                     % (value, AUTOCRACY_IDEA, autocracy))

    report.start('D2-sync-mutant')
    old_failures = sync_failures(baseline_text(SHIFTS_PATH), baseline_text(BOP_EFFECTS_PATH),
                                 constants, ranges)
    report.check('the pre-repair sync chain fails the check', bool(old_failures))
    report.check('the pre-repair constitutional shift keeps no balance at all',
                 any('iran_shift_to_constitutional' in failure and 'no balance' in failure
                     for failure in old_failures), '; '.join(old_failures))
    report.check('the pre-repair republic and socialist shifts land on the Crown side',
                 any('iran_shift_to_republic' in failure
                     and 'PER_bop_crown_ascendant' in failure for failure in old_failures)
                 and any('iran_shift_to_socialist' in failure
                         and 'PER_bop_crown_ascendant' in failure for failure in old_failures),
                 '; '.join(old_failures))
    old_resurgence = resurgence_failures(baseline_text(BOP_EFFECTS_PATH))
    report.check('the pre-repair resurgence test fails the check', bool(old_resurgence),
                 '; '.join(old_resurgence))

    report.start('D3-decree')
    failures = decree_failures(negotiations, budget)
    for failure in failures:
        report.check(failure, False)
    report.check('the decree veto is temporary in all four options', not failures,
                 '; '.join(failures))

    report.start('D3-mutant')
    old_failures = decree_failures(baseline_text(NEGOTIATIONS_PATH), budget)
    report.check('the pre-repair permanent flag fails the check', bool(old_failures))
    report.check('the pre-repair flag is rejected as permanent',
                 any('permanently' in failure for failure in old_failures),
                 '; '.join(old_failures))

    report.start('D4-ideology')
    failures = socialist_failures(shifts, ideologies)
    report.check('the socialist shift installs communism', not failures, '; '.join(failures))
    report.check('communism is a real ideology id', 'communism' in ideologies)
    report.check('the pre-repair id does not exist', 'communist' not in ideologies,
                 'the old value could never install a party')
    old_failures = socialist_failures(baseline_text(SHIFTS_PATH), ideologies)
    report.check('the pre-repair party id fails the check', bool(old_failures),
                 '; '.join(old_failures))

    report.start('preserved')
    failures = preserved_effect_failures(effects) + preserved_shift_failures(shifts)
    for failure in failures:
        report.check(failure, False)
    report.check('no working balance effect or shift was rewritten', not failures,
                 '; '.join(failures))

    report.note('the decree veto is read by the yearly Budget Vote mission; the engine expiry of '
                'a timed country flag is not proven here')
    report.note('no game was launched: availability, the balance ranges and the party change are '
                'source facts under the declared country states, not engine observations')
    return 0 if report.summary() else 1


if __name__ == '__main__':
    sys.exit(main())
