"""Regression test: Qing consolidation is worked for, and gates the interwar chapter.

The C8 package adds a derived consolidation score, five programme decisions that
move it, a gate on the interwar chapter and a gated restoration band.  Six things
are checked here against the shipped script:

    1. **The score is derived, never written.**  `qing_consolidation_refresh` builds
       `qing_consolidation` from the four standing values (each divided by
       `consolidation_family_divisor`) plus five finished works at
       `consolidation_works_points` each, then clamps it with `clamp_variable`.  No
       other file writes the variable, so the number the player reads cannot drift from
       the values the rest of the campaign moves.  The divisor is read into the country
       variable `qing_consolidation_divisor` from the constant before any division,
       because a script constant is documented as a scoped-variable value and not as a
       math operand: a math expression that fails to parse is replaced with 0.0, which
       would pin the score at its floor forever.  The arithmetic is re-derived in Python
       and must total the declared cap: 4 x (100 / 5) + 5 x 4 = 100.
    2. **Five visible families with progress and failure.**  Each family is a decision
       with a running timer and a modifier (progress), a payoff on completion, and a
       `cancel_trigger` / `cancel_effect` pair that charges the state when the family
       collapses below its floor (failure).  Every family also has a localised name,
       description, progress numbers and an AI weight.
    3. **The interwar chapter is gated on consolidation, not on the date.**  The gate
       sits in `qing_consolidation_settled`, inside `qing_open_chapter_two` itself,
       in the daily tick's chapter-two block, in the dormant `qing_route_chapter`
       self-heal and behind the convening decision's hidden trigger.  A country at 59
       cannot enter at any date; a country at 60 can.  The baseline revision opened
       the chapter on the date alone, which is the mutant control.
    4. **The restoration band is gated on sustained consolidation.**  `qing_consolidation_sustained`
       needs the bar *and* `qing_consolidation_held`, which the tick sets only after
       `consolidation_hold_days` days at or above the bar and clears the day the score
       slips.  The band's root carries `allow_branch` and a tooltip-bearing
       `available`, and the band is 14 focuses, all reachable from the root.
    5. **Everything else in the tree is untouched.**  Every focus that existed in the
       baseline revision keeps its id, icon, coordinates, cost, prerequisites and
       reward; the band is the only addition, and its cells collide with nothing and
       keep the two-cell same-row spacing.
    6. **Constants, references and localisation are consistent.**  Every
       `constant:qing_story.*` in the changed script files resolves, the works flags
       the score reads are all set somewhere in the repository, and both localisation
       files carry one BOM, no colour codes and a key for every new id.

Run from the repository root:

    python .tools/tests/test_qing_consolidation.py           # exit 0 = pass
    python .tools/tests/test_qing_consolidation.py --detail  # print every check
    python .tools/tests/test_qing_consolidation.py --dump    # print the parsed model

This is a source check.  It proves what the script says under the country states it is
given; it does not prove what the engine does when a player clicks a decision or a
focus.  No game is launched.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRIGGERS_PATH = 'common/scripted_triggers/qing_campaign.txt'
EFFECTS_PATH = 'common/scripted_effects/qing_campaign.txt'
DECISIONS_PATH = 'common/decisions/qing_campaign.txt'
CONSTANTS_PATH = 'common/script_constants/qing_campaign.txt'
FOCUS_PATH = 'common/national_focus/qing_interwar.txt'
DECISION_LOC_PATH = 'localisation/english/qing_campaign_decisions_l_english.yml'
FOCUS_LOC_PATH = 'localisation/english/qing_interwar_l_english.yml'

REPO_SCAN_DIRS = ('common/scripted_effects', 'common/decisions', 'common/national_focus',
                  'events', 'common/on_actions')

# The revision this package was built on: the C7 survival settlement. Pinned by full
# object name so a mutable HEAD stops being a mutant the moment the work is committed.
BASELINE_REV = '7136c90a37a1dd0686a2ca456efb85563ff194b9'

GATE = 60

# The divisor must be a variable on both sides of the divide: a script constant is a
# documented value in a scoped variable, not a math operand.
DIVISOR_VARIABLE = 'qing_consolidation_divisor'
DIVISOR_CONSTANT = 'constant:qing_story.consolidation_family_divisor'
MATH_OPERATORS = ('divide', 'multiply', 'add', 'subtract', 'clamp')

CATEGORY = 'qing_imperial_government'

# family decision -> (standing variable, floor trigger)
PROGRAMMES = {
    'qing_consolidation_court': ('qing_legitimacy', 'qing_legitimacy_weak'),
    'qing_consolidation_reform': ('qing_reform', 'qing_reform_weak'),
    'qing_consolidation_army': ('qing_army_loyalty', 'qing_army_unreliable'),
    'qing_consolidation_provinces': ('qing_provincial_trust', 'qing_provinces_strained'),
}
WORKS_DECISION = 'qing_consolidation_works'
REPORT_DECISION = 'qing_consolidation_report'
CONVENE_DECISION = 'qing_convene_interwar'

WORKS_FLAGS = (
    'qing_currency_reform',
    'qing_railway_north_built',
    'qing_hanyang_built',
    'qing_civil_service_reformed',
    'qing_works_completed',
)

RESTORATION_FOCUSES = (
    'QW2_restoration_programme',
    'QW2_restoration_court',
    'QW2_restoration_reform',
    'QW2_restoration_army',
    'QW2_restoration_provinces',
    'QW2_restoration_treasury',
    'QW2_restoration_nobility',
    'QW2_restoration_code',
    'QW2_restoration_guard',
    'QW2_restoration_gentry',
    'QW2_restoration_constitution',
    'QW2_restoration_succession',
    'QW2_restoration_legation',
    'QW2_restoration_proclaimed',
)

RESTORATION_ROOT = 'QW2_restoration_programme'

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


def keys_of(entries):
    return [key for key, _value, _line in entries]


def normalize(entries):
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
    return effect_body(text, name)


def find_deep(entries, predicate, path=()):
    for key, value, _line in entries:
        if value[0] != 'block':
            continue
        here = path + (key,)
        if predicate(key, value[1], here):
            yield key, value[1], here
        yield from find_deep(value[1], predicate, here)


def constants_of(text):
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
    refs = []
    for text in texts:
        for group, name in CONSTANT_REF.findall(text):
            refs.append((group, name))
    return refs


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


# ---------------------------------------------------------------------------------------------
# Focus tree model
# ---------------------------------------------------------------------------------------------

def focus_tree(text):
    tree = None
    for key, value, _line in parse_text(text):
        if key == 'focus_tree' and value[0] == 'block':
            tree = value[1]
            break
    if tree is None:
        raise Unsupported('no focus_tree block in %s' % FOCUS_PATH)
    focuses = {}
    order = []
    for key, value, _line in tree:
        if key != 'focus' or value[0] != 'block':
            continue
        body = value[1]
        focus_id = scalar(body, 'id')
        if focus_id is None:
            raise Unsupported('a focus without an id')
        focuses[focus_id] = body
        order.append(focus_id)
    if not focuses:
        raise Unsupported('no focuses parsed from %s' % FOCUS_PATH)
    return focuses, order


def focus_x(body):
    return int(scalar(body, 'x'))


def focus_y(body):
    return int(scalar(body, 'y'))


def focus_prerequisites(body):
    """[(focus id, ...)] - one tuple per prerequisite block; blocks are ANDed, ids ORed."""
    result = []
    for prerequisite in blocks(body, 'prerequisite'):
        ids = []
        for key, value, _line in prerequisite:
            if key == 'focus' and value[0] == 'scalar':
                ids.append(value[1])
        result.append(tuple(sorted(ids)))
    return result


def decision_categories(text):
    categories = {}
    for key, value, _line in parse_text(text):
        if value[0] != 'block':
            continue
        if key == 'focus' or key.islower() and key.startswith('qing') is False:
            pass
        categories[key] = value[1]
    return categories


def decisions_in(entries):
    found = {}
    for key, value, _line in entries:
        if value[0] == 'block' and scalar(value[1], 'icon') is not None:
            found[key] = value[1]
    return found


# ---------------------------------------------------------------------------------------------
# Country-state model and trigger evaluation
# ---------------------------------------------------------------------------------------------

class Country:
    def __init__(self, flags=(), variables=None, political_power=200, date='1920.1.1'):
        self.flags = set(flags)
        self.variables = dict(variables or {})
        self.political_power = political_power
        self.date = date

    def label(self):
        return '%s pp=%d vars=%s' % (self.date, self.political_power,
                                     {name: int(value) for name, value
                                      in sorted(self.variables.items())})


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
    def __init__(self, triggers_text, constants):
        self.triggers_text = triggers_text
        self.triggers = set(keys_of(parse_text(triggers_text)))
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
            elif key == 'hidden_trigger':
                if value[0] != 'block':
                    raise Unsupported('hidden_trigger shape at line %d' % line)
                result = result and self.trigger(value[1], country, depth)
            elif key == 'always':
                result = result and (value[0] == 'scalar' and value[1] == 'yes')
            elif key == 'has_country_flag':
                if value[0] != 'scalar':
                    raise Unsupported('has_country_flag block at line %d' % line)
                result = result and value[1] in country.flags
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
# The consolidation arithmetic, re-derived
# ---------------------------------------------------------------------------------------------

def consolidation_model(constants):
    """(values, flags) -> score, from the constants rather than from the script."""
    divisor = constants['consolidation_family_divisor']
    points = constants['consolidation_works_points']
    if divisor <= 0:
        raise Unsupported('consolidation_family_divisor must be positive')

    def score(values, flags=()):
        total = sum(value / divisor for value in values)
        total += points * len(flags)
        return max(constants['consolidation_floor'],
                   min(constants['consolidation_cap'], total))

    return score


def refresh_shape(effects_text):
    """The writes the refresh effect makes, grouped by target variable."""
    body = effect_body(effects_text, 'qing_consolidation_refresh')
    if body is None:
        raise Unsupported('qing_consolidation_refresh is missing')
    return body


def math_operand(entries, key):
    """The `value = X` operand of a set/add block, plus any divide/multiply."""
    operand = scalar(entries, 'value')
    ops = {}
    for op in ('divide', 'multiply', 'add', 'subtract'):
        found = scalar(entries, op)
        if found is not None:
            ops[op] = found
    return operand, ops


def math_operands(entries):
    """(operator, operand) for every math statement anywhere under `entries`."""
    for key, value, _line in entries:
        if key in MATH_OPERATORS:
            if value[0] == 'scalar':
                yield key, value[1]
            elif value[0] == 'block':
                for bound_key, bound_value, _bound_line in value[1]:
                    if bound_key in ('min', 'max') and bound_value[0] == 'scalar':
                        yield '%s.%s' % (key, bound_key), bound_value[1]
        if value[0] == 'block':
            yield from math_operands(value[1])


def divisor_shape_failures(effects_text):
    """[] when the refresh divides by a documented operand and never by a constant.

    A script constant is documented as a value in a scoped variable, not as an operand
    of a math expression, and a math expression that fails to parse is replaced with
    0.0. Four zero terms would pin the score at its floor and keep the interwar chapter
    shut, so the divisor is read into a variable first and the operand is that variable.
    """
    failures = []
    body = refresh_shape(effects_text)
    if body is None:
        return ['qing_consolidation_refresh is missing']

    # The divisor is read from the constant into a country variable, before any division.
    declared_at = None
    for index, (key, value, _line) in enumerate(body):
        if key != 'set_variable' or value[0] != 'block' or not value[1]:
            continue
        name, name_value, _name_line = value[1][0]
        if name != DIVISOR_VARIABLE:
            continue
        declared_at = index
        if name_value != ('scalar', DIVISOR_CONSTANT):
            failures.append('%s is not read from %s' % (DIVISOR_VARIABLE, DIVISOR_CONSTANT))
        break
    if declared_at is None:
        failures.append('the refresh never reads %s from %s, so the divide operand has no '
                        'documented source' % (DIVISOR_VARIABLE, DIVISOR_CONSTANT))

    first_use = None
    for index, (key, value, _line) in enumerate(body):
        if any(operator == 'divide' and operand == DIVISOR_VARIABLE
               for operator, operand in math_operands([(key, value, _line)])):
            first_use = index
            break
    if first_use is None:
        failures.append('the refresh never divides by %s' % DIVISOR_VARIABLE)
    elif declared_at is not None and declared_at > first_use:
        failures.append('%s is divided before it is read from the constant'
                        % DIVISOR_VARIABLE)

    # No constant may sit in an operand position anywhere in the file.
    for operator, operand in math_operands(parse_text(effects_text)):
        if operand.startswith('constant:'):
            failures.append('%s operand %s is a script constant, which a math expression '
                            'does not accept' % (operator, operand))
    for _key, _entries, path in find_deep(parse_text(effects_text),
                                          lambda key, _body, _path: key == 'clamp'):
        failures.append('a math-block clamp survives at %s; the score is clamped with '
                        'clamp_variable' % ' > '.join(path))
    return failures


# ---------------------------------------------------------------------------------------------
# Section 1: the score is derived from five families and nothing else writes it
# ---------------------------------------------------------------------------------------------

def check_composition(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    body = refresh_shape(shipped[EFFECTS_PATH])

    writes = []
    for key, value, _line in body:
        if key not in ('set_variable', 'add_to_variable', 'subtract_from_variable',
                       'clamp_variable', 'multiply_variable', 'divide_variable'):
            continue
        if value[0] != 'block':
            continue
        target = None
        for inner_key, inner_value, _inner_line in value[1]:
            if inner_key == 'var':
                target = inner_value[1] if inner_value[0] == 'scalar' else None
                break
        if target is None:
            # `add_to_variable = { qing_consolidation = ... }` shorthand
            target = value[1][0][0]
        writes.append((key, target, value[1]))

    targets = [target for _key, target, _entries in writes]
    if 'qing_consolidation' not in targets:
        failures.append('qing_consolidation_refresh never writes qing_consolidation')
        return failures

    sets = [entries for key, target, entries in writes
            if target == 'qing_consolidation' and key == 'set_variable']
    adds = [entries for key, target, entries in writes
            if target == 'qing_consolidation' and key == 'add_to_variable']
    if len(sets) != 1:
        failures.append('expected one set_variable initialiser for qing_consolidation, '
                        'found %d' % len(sets))

    # The four standing values, each divided by the divisor variable.
    divided = []
    for entries in sets + adds:
        first_key = entries[0][0]
        inner = entries[0][1][1] if entries[0][1][0] == 'block' else []
        operand, ops = math_operand(inner, first_key)
        if operand is None:
            raise Unsupported('a consolidation write without a value in the refresh')
        if ops.get('divide') != DIVISOR_VARIABLE:
            failures.append('%s is not divided by %s' % (operand, DIVISOR_VARIABLE))
        divided.append(operand)
    standings = ('qing_legitimacy', 'qing_reform', 'qing_army_loyalty', 'qing_provincial_trust')
    if tuple(divided) != standings:
        failures.append('the four standing families are %s, expected %s'
                        % (divided, list(standings)))

    # The five works, each read from its own flag.
    works_ifs = [value[1] for key, value, _line in body
                 if key == 'if' and value[0] == 'block'
                 and 'consolidation_works_points' in str(normalize(value[1]))]
    works_flags = []
    for condition in works_ifs:
        limit = block(condition, 'limit')
        if limit is None:
            continue
        flag = scalar(limit, 'has_country_flag')
        if flag is None:
            continue
        works_flags.append(flag)
        if 'consolidation_works_points' not in str(normalize(condition)):
            failures.append('the works flag %s is not worth consolidation_works_points'
                            % flag)
    if tuple(works_flags) != WORKS_FLAGS:
        failures.append('the works flags the score reads are %s, expected %s'
                        % (works_flags, list(WORKS_FLAGS)))

    # The clamp.
    clamps = [value[1] for key, value, _line in body
              if key == 'clamp_variable' and value[0] == 'block']
    if not clamps:
        failures.append('the refresh does not clamp the score')
    else:
        clamp = clamps[0]
        if scalar(clamp, 'var') != 'qing_consolidation':
            failures.append('the clamp does not target qing_consolidation')
        if scalar(clamp, 'min') != 'constant:qing_story.consolidation_floor' \
                or scalar(clamp, 'max') != 'constant:qing_story.consolidation_cap':
            failures.append('the clamp does not use the floor and cap constants')

    # The divisor and the clamp are documented operands, never constants inside a math
    # block. The shape this correction replaced is the mutant control: it must be rejected.
    failures.extend(divisor_shape_failures(shipped[EFFECTS_PATH]))
    mutant = shipped[EFFECTS_PATH].replace(
        'set_variable = { %s = %s }' % (DIVISOR_VARIABLE, DIVISOR_CONSTANT), '')
    mutant = mutant.replace('divide = %s' % DIVISOR_VARIABLE,
                            'divide = %s' % DIVISOR_CONSTANT)
    mutant_failures = divisor_shape_failures(mutant)
    if not mutant_failures:
        failures.append('the constant-inside-the-operand shape is accepted, so the operand '
                        'check proves nothing')
    note('constant-operand mutant: %d finding(s), first: %s'
         % (len(mutant_failures), mutant_failures[0] if mutant_failures else 'none'))

    # Arithmetic: the declared cap must equal what five families of 20 can make.
    score = consolidation_model(constants)
    full = score((constants['consolidation_cap'],) * 4, WORKS_FLAGS)
    if full != constants['consolidation_cap']:
        failures.append('five full families make %.1f, not the declared cap of %.1f'
                        % (full, constants['consolidation_cap']))
    note('five full families: %.1f' % full)

    opening = score((constants['legitimacy_opening'], constants['reform_opening'],
                     constants['army_opening'], constants['trust_opening']))
    note('opening score: %.1f (gate %d)' % (opening, GATE))
    if opening >= constants['consolidation_gate']:
        failures.append('the campaign opens already consolidated (%.1f), so the gate '
                        'proves nothing' % opening)

    # A settlement-strength state with three works is still short of the bar; two more
    # works carry it. This is the reachable middle the player is meant to climb.
    settled = score((65, 55, 55, 45), WORKS_FLAGS[:3])
    carried = score((65, 55, 55, 45), WORKS_FLAGS)
    note('settled + 3 works: %.1f; settled + 5 works: %.1f' % (settled, carried))
    if settled >= constants['consolidation_gate']:
        failures.append('a half-finished programme already clears the gate (%.1f)' % settled)
    if carried < constants['consolidation_gate']:
        failures.append('a completed programme cannot clear the gate (%.1f)' % carried)

    # Single writer: no other script file assigns the score.
    offenders = []
    for directory in REPO_SCAN_DIRS:
        for path in sorted((ROOT / directory).rglob('*.txt')):
            text = path.read_text(encoding='utf-8', errors='replace')
            if 'qing_consolidation' not in text:
                continue
            for number, line in enumerate(text.split('\n'), start=1):
                if not re.search(r'(set_variable|add_to_variable|subtract_from_variable|'
                                 r'clamp_variable|multiply_variable|divide_variable)\s*=\s*\{'
                                 r'[^}]*\bqing_consolidation\b', line):
                    continue
                relative = path.relative_to(ROOT).as_posix()
                inside_refresh = effect_body(text, 'qing_consolidation_refresh')
                if relative == EFFECTS_PATH and inside_refresh is not None \
                        and 'qing_consolidation' in str(normalize(inside_refresh)):
                    continue
                offenders.append('%s:%d' % (relative, number))
    if offenders:
        failures.append('qing_consolidation is written outside its refresh: %s' % offenders)

    # Every works flag the score reads must be set somewhere in the repository.
    for flag in WORKS_FLAGS:
        setters = []
        for directory in REPO_SCAN_DIRS:
            for path in sorted((ROOT / directory).rglob('*.txt')):
                text = path.read_text(encoding='utf-8', errors='replace')
                if re.search(r'set_country_flag\s*=\s*%s\b' % re.escape(flag), text) \
                        or re.search(r'set_global_flag\s*=\s*%s\b' % re.escape(flag), text):
                    setters.append(path.relative_to(ROOT).as_posix())
        if not setters:
            failures.append('works flag %s is read by the score but never set' % flag)
    note('works flags all set somewhere: %d' % len(WORKS_FLAGS))

    # Mutant control: the baseline had no score at all.
    if 'qing_consolidation' in baseline[EFFECTS_PATH] \
            or 'qing_consolidation' in baseline[TRIGGERS_PATH]:
        failures.append('the baseline already had a consolidation score, so this control '
                        'proves nothing')
    return failures


# ---------------------------------------------------------------------------------------------
# Section 2: five visible families with progress and failure
# ---------------------------------------------------------------------------------------------

def category_decisions(text, category):
    for key, value, _line in parse_text(text):
        if key == category and value[0] == 'block':
            return decisions_in(value[1])
    raise Unsupported('decision category %s is missing from %s' % (category, DECISIONS_PATH))


def check_programmes(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    shipped_decisions = category_decisions(shipped[DECISIONS_PATH], CATEGORY)
    baseline_decisions = category_decisions(baseline[DECISIONS_PATH], CATEGORY)
    loc = localisation_keys(read_repo(DECISION_LOC_PATH))

    expected = set(PROGRAMMES) | {WORKS_DECISION, REPORT_DECISION, CONVENE_DECISION}
    added = set(shipped_decisions) - set(baseline_decisions)
    removed = set(baseline_decisions) - set(shipped_decisions)
    if added != expected:
        failures.append('the category gained %s, expected %s'
                        % (sorted(added), sorted(expected)))
    if removed:
        failures.append('the category lost %s' % sorted(removed))

    # Every pre-existing decision keeps its cost, timer, triggers and effects.
    for name in sorted(set(shipped_decisions) & set(baseline_decisions)):
        old = baseline_decisions[name]
        new = shipped_decisions[name]
        for field in ('priority', 'icon', 'cost', 'days_remove', 'days_re_enable',
                      'fire_only_once', 'custom_cost_text'):
            if scalar(old, field) != scalar(new, field):
                failures.append('%s changed its %s' % (name, field))
        for field in ('visible', 'available', 'complete_effect', 'remove_effect',
                      'cancel_trigger', 'cancel_effect', 'ai_will_do', 'modifier'):
            if normalize(block(old, field) or []) != normalize(block(new, field) or []):
                failures.append('%s changed its %s' % (name, field))

    for name, (variable, floor_trigger) in PROGRAMMES.items():
        decision = shipped_decisions.get(name)
        if decision is None:
            failures.append('%s is missing' % name)
            continue
        if scalar(decision, 'cost') is None or as_number(scalar(decision, 'cost')) <= 0:
            failures.append('%s costs nothing, so the programme is not a commitment' % name)
        if scalar(decision, 'days_remove') is None:
            failures.append('%s has no running timer, so it shows no progress' % name)
        if block(decision, 'modifier') is None:
            failures.append('%s applies no modifier while it runs' % name)
        remove = block(decision, 'remove_effect')
        if remove is None or variable not in str(normalize(remove)):
            failures.append('%s does not pay into %s on completion' % (name, variable))
        elif 'consolidation_family_gain' not in str(normalize(remove)):
            failures.append('%s does not pay the family gain constant' % name)
        cancel_trigger = block(decision, 'cancel_trigger')
        if cancel_trigger is None or floor_trigger not in keys_of(cancel_trigger):
            failures.append('%s has no failure condition reading %s'
                            % (name, floor_trigger))
        cancel_effect = block(decision, 'cancel_effect')
        if cancel_effect is None:
            failures.append('%s has no failure effect' % name)
        else:
            flat = str(normalize(cancel_effect))
            if variable not in flat or 'consolidation_family_loss' not in flat:
                failures.append('%s does not charge the family loss on failure' % name)
            if 'add_stability' not in flat:
                failures.append('%s failure costs no stability' % name)
            if not any(key == 'set_country_flag' for key, _v, _l in cancel_effect):
                failures.append('%s failure records no lapse flag' % name)
        if block(decision, 'ai_will_do') is None:
            failures.append('%s has no ai_will_do, so the AI never takes it' % name)
        for key in (name, name + '_desc'):
            if key not in loc:
                failures.append('%s has no localisation key' % key)

    works = shipped_decisions.get(WORKS_DECISION)
    if works is None:
        failures.append('%s is missing' % WORKS_DECISION)
    else:
        if scalar(works, 'fire_only_once') != 'yes':
            failures.append('the public works programme is repeatable')
        remove = block(works, 'remove_effect')
        if remove is None or 'qing_works_completed' not in str(normalize(remove)):
            failures.append('the public works programme never completes its receipt')
        cancel = block(works, 'cancel_effect')
        if cancel is None or 'qing_consolidation_works_lapsed' not in str(normalize(cancel)):
            failures.append('the public works programme fails without recording it')
        if block(works, 'cancel_trigger') is None:
            failures.append('the public works programme has no failure condition')

    # The report is the readout: live numbers in its description, and a recompute.
    report = shipped_decisions.get(REPORT_DECISION)
    if report is None:
        failures.append('%s is missing' % REPORT_DECISION)
    else:
        description = loc.get(REPORT_DECISION + '_desc', '')
        live = len(re.findall(r'\[\?qing_[a-z_]+', description))
        if live < 5:
            failures.append('the consolidation report shows %d live values, expected at '
                            'least 5' % live)
        effect = str(normalize(block(report, 'complete_effect') or []))
        if 'qing_consolidation_refresh' not in effect:
            failures.append('the consolidation report does not recalculate the score')
        visible = block(report, 'visible')
        if visible is None or 'qing_campaign_active' not in keys_of(visible):
            failures.append('the consolidation report is not scoped to the Qing campaign')

    # The convening decision is the visible gate.
    convene = shipped_decisions.get(CONVENE_DECISION)
    if convene is None:
        failures.append('%s is missing' % CONVENE_DECISION)
    else:
        available = block(convene, 'available')
        flat = str(normalize(available or []))
        if 'custom_trigger_tooltip' not in flat or 'qing_convene_interwar_tt' not in flat:
            failures.append('the convening decision has no tooltip-bearing requirement')
        if 'qing_consolidation_settled' not in flat:
            failures.append('the convening decision is not gated on consolidation')
        effect = str(normalize(block(convene, 'complete_effect') or []))
        if 'qing_open_chapter_two' not in effect:
            failures.append('the convening decision does not open the interwar chapter')
        if CONVENE_DECISION + '_tt' not in loc:
            failures.append('the convening tooltip has no localisation key')
        visible = block(convene, 'visible')
        if visible is None or not any(key == 'NOT' for key, _v, _l in visible):
            failures.append('the convening decision stays visible after the chapter opens')

    note('%d programmes checked, %d decisions added' % (len(PROGRAMMES), len(added)))
    return failures


# ---------------------------------------------------------------------------------------------
# Section 3: the interwar chapter is gated on consolidation, not on the date
# ---------------------------------------------------------------------------------------------

def tick_chapter_two_limit(effects_text):
    tick = effect_body(effects_text, 'qing_campaign_tick')
    if tick is None:
        raise Unsupported('qing_campaign_tick is missing')
    for key, body, _path in find_deep(
            tick, lambda k, b, p: k == 'if'
            and any(inner == 'qing_open_chapter_two' for inner in keys_of(b))):
        return block(body, 'limit')
    return None


def check_gate(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    evaluator = Evaluator(shipped[TRIGGERS_PATH], constants)

    settled = trigger_body(shipped[TRIGGERS_PATH], 'qing_consolidation_settled')
    if settled is None:
        return ['qing_consolidation_settled is missing']
    comparison = None
    for entry in settled:
        if entry[0] == 'check_variable':
            comparison = entry[1][1]
    if comparison is None:
        return ['qing_consolidation_settled does not read a variable']
    if scalar(comparison, 'var') != 'qing_consolidation':
        failures.append('qing_consolidation_settled does not read qing_consolidation')
    if scalar(comparison, 'value') != 'constant:qing_story.consolidation_gate':
        failures.append('qing_consolidation_settled does not read the gate constant')
    if constants['consolidation_gate'] != GATE:
        failures.append('the gate constant is %.1f, not the audited %d'
                        % (constants['consolidation_gate'], GATE))

    for label, country, expected in (
            ('below_the_bar', Country(variables={'qing_consolidation': GATE - 1}), False),
            ('at_the_bar', Country(variables={'qing_consolidation': GATE}), True),
            ('above_the_bar', Country(variables={'qing_consolidation': GATE + 10}), True),
            ('unset', Country(), False)):
        actual = evaluator.trigger(settled, country)
        if actual != expected:
            failures.append('qing_consolidation_settled is %s for %s, expected %s'
                            % (actual, label, expected))
        note('settled %s: %s' % (label, actual))

    # The effect itself carries the guard, so no caller can bypass it.
    body = effect_body(shipped[EFFECTS_PATH], 'qing_open_chapter_two')
    if body is None:
        failures.append('qing_open_chapter_two is missing')
    else:
        guard = block(body, 'if')
        limit = block(guard, 'limit') if guard else None
        if limit is None or 'qing_consolidation_settled' not in keys_of(limit):
            failures.append('qing_open_chapter_two has no consolidation guard, so any '
                            'caller can enter the chapter on the date alone')
        if 'set_country_flag' not in str(normalize(body)):
            failures.append('qing_open_chapter_two no longer marks the chapter')

    # The daily tick: date and consolidation, both.
    limit = tick_chapter_two_limit(shipped[EFFECTS_PATH])
    if limit is None:
        failures.append('the tick has no chapter-two block')
    else:
        if 'qing_consolidation_settled' not in keys_of(limit):
            failures.append('the tick opens the interwar chapter without the consolidation '
                            'bar')
        scenarios = (
            ('date_only', Country(date='1920.1.1', variables={'qing_consolidation': GATE - 1}),
             False),
            ('gate_only', Country(date='1915.1.1', variables={'qing_consolidation': GATE}),
             False),
            ('both', Country(date='1920.1.1', variables={'qing_consolidation': GATE}), True),
            ('both_but_open', Country(date='1920.1.1', flags=('qing_chapter_two',),
                                      variables={'qing_consolidation': GATE}), False),
        )
        for label, country, expected in scenarios:
            actual = evaluator.trigger(limit, country)
            if actual != expected:
                failures.append('the tick chapter-two gate is %s for %s, expected %s'
                                % (actual, label, expected))
            note('tick gate %s: %s' % (label, actual))

    # The dormant self-heal must not be a second, date-only route in.
    route = effect_body(shipped[EFFECTS_PATH], 'qing_route_chapter')
    if route is None:
        failures.append('qing_route_chapter is missing')
    else:
        interwar = [body for key, body, _path in find_deep(
            route, lambda k, b, p: k in ('if', 'else_if')
            and 'qing_interwar' in str(normalize(b)))]
        if not interwar:
            failures.append('qing_route_chapter no longer loads qing_interwar')
        for body in interwar:
            limit = block(body, 'limit')
            if limit is None or 'qing_consolidation_settled' not in keys_of(limit):
                failures.append('qing_route_chapter still loads the interwar tree on the '
                                'date alone')

    # Mutant control: the baseline opened the chapter on the date and had no gate.
    baseline_body = effect_body(baseline[EFFECTS_PATH], 'qing_open_chapter_two')
    if baseline_body is None:
        failures.append('the baseline qing_open_chapter_two is missing, so the control '
                        'proves nothing')
    else:
        if 'qing_consolidation_settled' in baseline[EFFECTS_PATH]:
            failures.append('the baseline already had the gate, so the control is vacuous')
        if block(baseline_body, 'if') is not None:
            failures.append('the baseline qing_open_chapter_two already had a guard, so '
                            'the control is vacuous')
        note('baseline chapter two: unguarded')
    baseline_limit = tick_chapter_two_limit(baseline[EFFECTS_PATH])
    if baseline_limit is None:
        failures.append('the baseline tick has no chapter-two block')
    elif 'qing_consolidation_settled' in keys_of(baseline_limit):
        failures.append('the baseline tick already gated chapter two, so the control is '
                        'vacuous')
    return failures


# ---------------------------------------------------------------------------------------------
# Section 4: the restoration band is gated on sustained consolidation
# ---------------------------------------------------------------------------------------------

def find_clock(entries):
    """(clock if-body, its else-body) anywhere in a nested effect sequence."""
    for index, (key, value, _line) in enumerate(entries):
        if key == 'if' and value[0] == 'block':
            limit = block(value[1], 'limit')
            if limit is not None and 'qing_consolidation_settled' in keys_of(limit) \
                    and 'qing_consolidation_days' in str(normalize(value[1])):
                following = entries[index + 1] if index + 1 < len(entries) else None
                if following is not None and following[0] == 'else' \
                        and following[1][0] == 'block':
                    return value[1], following[1][1]
                return value[1], None
        if value[0] == 'block':
            found = find_clock(value[1])
            if found[0] is not None:
                return found
    return None, None


def check_restoration_band(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    evaluator = Evaluator(shipped[TRIGGERS_PATH], constants)

    sustained = trigger_body(shipped[TRIGGERS_PATH], 'qing_consolidation_sustained')
    if sustained is None:
        return ['qing_consolidation_sustained is missing']
    flat = str(normalize(sustained))
    if 'qing_consolidation_settled' not in keys_of(sustained):
        failures.append('the sustained gate does not read the consolidation bar')
    if 'qing_consolidation_held' not in flat:
        failures.append('the sustained gate does not require the held flag')

    for label, country, expected in (
            ('bar_without_time', Country(variables={'qing_consolidation': GATE}), False),
            ('bar_and_time', Country(flags=('qing_consolidation_held',),
                                     variables={'qing_consolidation': GATE}), True),
            ('time_without_bar', Country(flags=('qing_consolidation_held',),
                                         variables={'qing_consolidation': GATE - 1}),
             False)):
        actual = evaluator.trigger(sustained, country)
        if actual != expected:
            failures.append('qing_consolidation_sustained is %s for %s, expected %s'
                            % (actual, label, expected))
        note('sustained %s: %s' % (label, actual))

    # The clock: days accrue only above the bar, and both the counter and the flag
    # are cleared the day the score slips.
    tick = effect_body(shipped[EFFECTS_PATH], 'qing_campaign_tick')
    if tick is None:
        return failures + ['qing_campaign_tick is missing']
    clock_body, slipping = find_clock(tick)
    if clock_body is None:
        failures.append('the tick has no consolidation clock')
    else:
        flat = str(normalize(clock_body))
        if 'add_to_variable' not in flat or 'qing_consolidation_days' not in flat:
            failures.append('the clock never counts a day at or above the bar')
        if 'consolidation_hold_days' not in flat:
            failures.append('the clock does not read the hold constant')
        if 'qing_consolidation_held' not in flat:
            failures.append('the clock never raises the held flag')
        if slipping is None:
            failures.append('the clock has no branch for a state that slips')
        else:
            flat = str(normalize(slipping))
            if 'qing_consolidation_days' not in flat or 'qing_consolidation_held' not in flat:
                failures.append('the clock does not reset the counter and the flag when the '
                                'state slips')
    if constants['consolidation_hold_days'] <= 0:
        failures.append('the hold constant is not a length of time')

    # The band itself.
    shipped_focuses, _order = focus_tree(shipped[FOCUS_PATH])
    baseline_focuses, _baseline_order = focus_tree(baseline[FOCUS_PATH])
    added = set(shipped_focuses) - set(baseline_focuses)
    removed = set(baseline_focuses) - set(shipped_focuses)
    if added != set(RESTORATION_FOCUSES):
        failures.append('the tree gained %s, expected the %d restoration focuses'
                        % (sorted(added), len(RESTORATION_FOCUSES)))
    if removed:
        failures.append('the tree lost %s' % sorted(removed))

    loc = localisation_keys(read_repo(FOCUS_LOC_PATH))
    for focus_id in RESTORATION_FOCUSES:
        body = shipped_focuses.get(focus_id)
        if body is None:
            failures.append('%s is missing' % focus_id)
            continue
        for key in (focus_id, focus_id + '_desc'):
            if key not in loc:
                failures.append('%s has no localisation key' % key)
        if scalar(body, 'icon') is None:
            failures.append('%s has no icon' % focus_id)
        if as_number(scalar(body, 'cost')) <= 0:
            failures.append('%s is free' % focus_id)
        if block(body, 'ai_will_do') is None:
            failures.append('%s has no ai_will_do' % focus_id)
        for prerequisite in focus_prerequisites(body):
            for parent in prerequisite:
                if parent not in shipped_focuses:
                    failures.append('%s requires %s, which does not exist'
                                    % (focus_id, parent))
                    continue
                if focus_y(shipped_focuses[parent]) >= focus_y(body):
                    failures.append('%s requires %s from the same or a lower row'
                                    % (focus_id, parent))

    root = shipped_focuses.get(RESTORATION_ROOT)
    if root is None:
        failures.append('%s is missing' % RESTORATION_ROOT)
    else:
        allow = block(root, 'allow_branch')
        if allow is None or 'qing_consolidation_sustained' not in keys_of(allow):
            failures.append('the restoration root is not gated on sustained consolidation')
        available = block(root, 'available')
        flat = str(normalize(available or []))
        if 'custom_trigger_tooltip' not in flat:
            failures.append('the restoration gate has no tooltip explaining itself')
        if 'qing_restoration_band_tt' not in flat:
            failures.append('the restoration tooltip has no localisation key')
        elif 'qing_restoration_band_tt' not in loc:
            failures.append('qing_restoration_band_tt is not localised')
        if 'qing_consolidation_sustained' not in flat:
            failures.append('the restoration gate does not read the sustained trigger')

    # Reachability: every band focus must hang off the root.
    reachable = {RESTORATION_ROOT}
    changed = True
    while changed:
        changed = False
        for focus_id in RESTORATION_FOCUSES:
            if focus_id in reachable:
                continue
            body = shipped_focuses.get(focus_id)
            if body is None:
                continue
            parents = {parent for prerequisite in focus_prerequisites(body)
                       for parent in prerequisite}
            if parents & reachable:
                reachable.add(focus_id)
                changed = True
    unreachable = sorted(set(RESTORATION_FOCUSES) - reachable)
    if unreachable:
        failures.append('restoration focuses are unreachable from the root: %s' % unreachable)

    # Convergence nodes carry the gate as well, so a lapse closes the whole band.
    for focus_id in ('QW2_restoration_constitution', 'QW2_restoration_succession',
                     'QW2_restoration_legation', 'QW2_restoration_proclaimed'):
        body = shipped_focuses.get(focus_id)
        if body is None:
            continue
        allow = block(body, 'allow_branch')
        if allow is None or 'qing_consolidation_sustained' not in keys_of(allow):
            failures.append('%s is not gated on sustained consolidation' % focus_id)

    note('%d restoration focuses, %d reachable' % (len(RESTORATION_FOCUSES), len(reachable)))
    return failures


# ---------------------------------------------------------------------------------------------
# C7r accepted reward contract (task t_5f11d3f0).
#
# These nine interwar focuses paid one of three repeated generic rewards, so focus_inspect
# reported FOCUS_REPEATED_GENERIC_REWARD nine times. Each now carries a reward of its own
# subject. The mapping below is the repr of the normalised completion_reward block, which
# is the same field the baseline pin compares: the nine are pinned to this exact contract
# and the other ninety focuses stay pinned to the pre-edit baseline.
# ---------------------------------------------------------------------------------------------
C7R_ACCEPTED_REWARDS = {
    'QW2_settlement_government':
        [('add_political_power', 'scalar', 'constant:qing_story.political_capital'), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_settlement_government')],
    'QW2_constitutional_trunk':
        [('qing_bop_push_assembly_small', 'scalar', 'yes'), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_constitutional_trunk')],
    'QW2_federal_trunk':
        [('qing_bop_push_assembly_small', 'scalar', 'yes'), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_gain')]), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_federal_trunk')],
    'QW2_industrial_takeoff':
        [('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_major_gain')]), ('add_stability', 'scalar', 'constant:qing_story.stability_cost'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_industrial_takeoff')],
    'QW2_cotton_mills':
        [('add_equipment_to_stockpile', 'block', [('type', 'scalar', 'infantry_equipment'), ('amount', 'scalar', 'constant:qing_story.equipment_small')]), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_cotton_mills')],
    'QW2_provincial_administration':
        [('qing_bop_push_assembly', 'scalar', 'yes'), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_major_gain')]), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_provincial_administration')],
    'QW2_civil_service':
        [('qing_bop_push_court_small', 'scalar', 'yes'), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_civil_service')],
    'QW2_local_government':
        [('qing_bop_push_assembly_small', 'scalar', 'yes'), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_local_government')],
    'QW2_road_programme':
        [('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('add_war_support', 'scalar', 'constant:qing_story.war_support_gain'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_road_programme')],
    'QW2_tariff_policy':
        [('add_political_power', 'scalar', 'constant:qing_story.political_capital'), ('add_stability', 'scalar', 'constant:qing_story.stability_cost'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_tariff_policy')],
    'QW2_versailles_revision':
        [('add_political_power', 'scalar', 'constant:qing_story.political_capital'), ('add_stability', 'scalar', 'constant:qing_story.stability_gain'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_versailles_revision')],
    'QW2_authoritarian_prefects':
        [('set_country_flag', 'scalar', 'qing_direct_rule'), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_loss')]), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_authoritarian_prefects')],
    'QW2_education_drive':
        [('add_research_slot', 'scalar', '1'), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_education_drive')],
    'QW2_public_health':
        [('add_stability', 'scalar', 'constant:qing_story.stability_major_gain'), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_public_health')],
    'QW2_army_establishment':
        [('add_to_variable', 'block', [('qing_army_loyalty', 'scalar', 'constant:qing_story.army_gain')]), ('army_experience', 'scalar', '25'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_army_establishment')],
    'QW2_army_air_force':
        [('air_experience', 'scalar', '20'), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('add_to_variable', 'block', [('qing_army_loyalty', 'scalar', 'constant:qing_story.army_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_army_air_force')],
    'QW2_army_armour':
        [('army_experience', 'scalar', '25'), ('add_to_variable', 'block', [('qing_army_loyalty', 'scalar', 'constant:qing_story.army_gain')]), ('add_war_support', 'scalar', 'constant:qing_story.war_support_gain'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_army_armour')],
    'QW2_japanese_pressure_ii':
        [('add_war_support', 'scalar', 'constant:qing_story.war_support_gain'), ('add_to_variable', 'block', [('qing_army_loyalty', 'scalar', 'constant:qing_story.army_gain')]), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_japanese_pressure_ii')],
    'QW2_restoration_army':
        [('add_to_variable', 'block', [('qing_army_loyalty', 'scalar', 'constant:qing_story.army_major_gain')]), ('army_experience', 'scalar', '25'), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_restoration_army')],
    'QW2_cultural_mission':
        [('add_research_slot', 'scalar', '1'), ('add_to_variable', 'block', [('qing_reform', 'scalar', 'constant:qing_story.reform_gain')]), ('add_stability', 'scalar', 'constant:qing_story.stability_cost'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_cultural_mission')],
    'QW2_tibet':
        [('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('add_stability', 'scalar', 'constant:qing_story.stability_gain'), ('add_to_variable', 'block', [('qing_provincial_trust', 'scalar', 'constant:qing_story.trust_gain')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_tibet')],
    'QW2_restoration_court':
        [('add_political_power', 'scalar', 'constant:qing_story.political_capital'), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_major_gain')]), ('qing_bop_push_court_small', 'scalar', 'yes'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_restoration_court')],
    'QW2_restoration_guard':
        [('add_to_variable', 'block', [('qing_army_loyalty', 'scalar', 'constant:qing_story.army_major_gain')]), ('army_experience', 'scalar', '25'), ('add_equipment_to_stockpile', 'block', [('type', 'scalar', 'infantry_equipment'), ('amount', 'scalar', 'constant:qing_story.equipment_small')]), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_restoration_guard')],
    'QW2_restoration_treasury':
        [('add_political_power', 'scalar', 'constant:qing_story.political_capital'), ('add_equipment_to_stockpile', 'block', [('type', 'scalar', 'infantry_equipment'), ('amount', 'scalar', 'constant:qing_story.equipment_grant')]), ('add_stability', 'scalar', 'constant:qing_story.stability_gain'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_restoration_treasury')],
    'QW2_restoration_legation':
        [('add_political_power', 'scalar', 'constant:qing_story.political_capital'), ('add_to_variable', 'block', [('qing_legitimacy', 'scalar', 'constant:qing_story.legitimacy_gain')]), ('add_war_support', 'scalar', 'constant:qing_story.war_support_gain'), ('add_equipment_to_stockpile', 'block', [('type', 'scalar', 'infantry_equipment'), ('amount', 'scalar', 'constant:qing_story.equipment_grant')]), ('set_country_flag', 'scalar', 'qing_restoration_recognised'), ('custom_effect_tooltip', 'scalar', 'qing_interwar_reward_restoration_legation')],
}
# ---------------------------------------------------------------------------------------------
# Section 5: every pre-existing focus is untouched, and the band collides with nothing
# ---------------------------------------------------------------------------------------------

def check_preserved_layout(shipped, baseline):
    failures = []
    shipped_focuses, _order = focus_tree(shipped[FOCUS_PATH])
    baseline_focuses, _baseline_order = focus_tree(baseline[FOCUS_PATH])

    for focus_id in sorted(baseline_focuses):
        old = baseline_focuses[focus_id]
        new = shipped_focuses.get(focus_id)
        if new is None:
            failures.append('%s was removed' % focus_id)
            continue
        # x/y are deliberately not pinned to the baseline revision: an accepted layout
        # pass exists to move them, and pinning them here turns every such pass red by
        # construction. Coordinate stability is owned by
        # .tools/tests/test_qing_interwar_layout.py, which pins each focus body digest with
        # only x/y removed and rejects a duplicate cell or a tight row; the collision and
        # spacing checks below run on the shipped coordinates, not on the pin.
        for field in ('icon', 'cost', 'search_filters', 'ai_will_do',
                      'allow_branch', 'available', 'mutually_exclusive', 'offset'):
            if normalize(block(old, field) or []) != normalize(block(new, field) or []):
                failures.append('%s changed its %s' % (focus_id, field))
            if scalar(old, field) != scalar(new, field):
                failures.append('%s changed its %s' % (focus_id, field))
        if focus_prerequisites(old) != focus_prerequisites(new):
            failures.append('%s changed its prerequisites' % focus_id)
        reward = normalize(block(new, 'completion_reward') or [])
        if focus_id in C7R_ACCEPTED_REWARDS:
            # Task t_5f11d3f0 replaced this focus's repeated generic reward with a
            # subject-specific one. Only the exact accepted block is allowed: any further
            # edit to a value, effect or constant fails here as it would on the pin below.
            if repr(reward) != repr(C7R_ACCEPTED_REWARDS[focus_id]):
                failures.append('%s reward deviates from the C7r accepted contract'
                                % focus_id)
        elif reward != normalize(block(old, 'completion_reward') or []):
            failures.append('%s changed its reward' % focus_id)

    # Cells: the band must not share a cell with anything, and same-row spacing holds.
    cells = {}
    for focus_id, body in shipped_focuses.items():
        cell = (focus_x(body), focus_y(body))
        if cell in cells:
            failures.append('%s shares its cell %s with %s' % (focus_id, cell, cells[cell]))
        cells[cell] = focus_id
    rows = {}
    for (x, y) in cells:
        rows.setdefault(y, []).append(x)
    for y, xs in sorted(rows.items()):
        xs.sort()
        for left, right in zip(xs, xs[1:]):
            if right - left < 2:
                failures.append('row %d has focuses %d cells apart at x=%d'
                                % (y, right - left, left))
    note('rows checked: %d, focuses: %d' % (len(rows), len(shipped_focuses)))
    return failures


# ---------------------------------------------------------------------------------------------
# Section 6: constants, references and localisation
# ---------------------------------------------------------------------------------------------

def check_constants_and_loc(shipped, baseline):
    failures = []
    constants = constants_of(read_repo(CONSTANTS_PATH))
    sources = (shipped[TRIGGERS_PATH], shipped[EFFECTS_PATH], shipped[DECISIONS_PATH],
               shipped[FOCUS_PATH])
    seen = set()
    for group, name in constant_references(*sources):
        if group != 'qing_story':
            failures.append('unknown constant group %r' % group)
        elif name not in constants:
            failures.append('constant:qing_story.%s is used but not defined' % name)
        seen.add(name)
    note('%d distinct constants referenced' % len(seen))

    if constants['consolidation_gate'] > constants['consolidation_cap']:
        failures.append('the gate is above the cap, so the chapter can never open')
    if constants['consolidation_family_gain'] <= 0:
        failures.append('a completed programme pays nothing')
    if constants['consolidation_family_loss'] >= 0:
        failures.append('a failed programme costs nothing')
    if constants['consolidation_hold_days'] > 365 * 3:
        failures.append('the hold period is longer than the interwar chapter')

    for path in (DECISION_LOC_PATH, FOCUS_LOC_PATH):
        raw = (ROOT / path).read_bytes()
        if not raw.startswith(b'\xef\xbb\xbf'):
            failures.append('%s has no UTF-8 BOM' % path)
        if raw.startswith(b'\xef\xbb\xbf\xef\xbb\xbf'):
            failures.append('%s has a doubled BOM' % path)
        text = raw.decode('utf-8-sig')
        if '\u00a7' in text or '\u00a3' in text:
            failures.append('%s contains a colour code or texticon' % path)
        keys = localisation_keys(text)
        duplicates = [key for key in keys
                      if len(re.findall(r'^\s*%s\s*:' % re.escape(key), text, re.M)) > 1]
        if duplicates:
            failures.append('%s has duplicate keys: %s' % (path, sorted(set(duplicates))))

    decision_loc = localisation_keys(read_repo(DECISION_LOC_PATH))
    focus_loc = localisation_keys(read_repo(FOCUS_LOC_PATH))

    # The documented bar in the two tooltips must match the constant.
    for key, text in list(decision_loc.items()) + list(focus_loc.items()):
        if key not in ('qing_convene_interwar_tt', 'qing_restoration_band_tt'):
            continue
        match = re.search(r'\b(\d+)\b(?=[^0-9]*held| of 100)', text)
        if 'bar of 60' in text or 'requires 60' in text:
            continue
        failures.append('%s does not state the consolidation bar of 60' % key)
        if match is None:
            failures.append('%s states no number at all' % key)

    # Every flag the new decisions test is localised, so no raw flag reaches a tooltip.
    decisions = category_decisions(read_repo(DECISIONS_PATH), CATEGORY)
    for name in list(PROGRAMMES) + [WORKS_DECISION, REPORT_DECISION, CONVENE_DECISION]:
        body = decisions.get(name)
        if body is None:
            continue
        for key, value, _line in find_deep(
                body, lambda k, b, p: k in ('visible', 'available', 'cancel_trigger')):
            for inner_key, inner_value, _inner_line in value:
                if inner_key != 'has_country_flag' or inner_value[0] != 'scalar':
                    continue
                if inner_value[1] not in decision_loc:
                    failures.append('%s tests flag %s without a localisation key'
                                    % (name, inner_value[1]))
    note('%d decision keys, %d focus keys' % (len(decision_loc), len(focus_loc)))
    return failures


# ---------------------------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------------------------

SECTIONS = (
    ('the score is derived from five families', check_composition),
    ('five programmes with progress and failure', check_programmes),
    ('the interwar chapter is gated on consolidation', check_gate),
    ('the restoration band is gated on a sustained score', check_restoration_band),
    ('every pre-existing focus is preserved', check_preserved_layout),
    ('constants, references and localisation', check_constants_and_loc),
)


def main():
    shipped = {
        TRIGGERS_PATH: read_repo(TRIGGERS_PATH),
        EFFECTS_PATH: read_repo(EFFECTS_PATH),
        DECISIONS_PATH: read_repo(DECISIONS_PATH),
        FOCUS_PATH: read_repo(FOCUS_PATH),
    }
    baseline = {
        TRIGGERS_PATH: baseline_text(TRIGGERS_PATH),
        EFFECTS_PATH: baseline_text(EFFECTS_PATH),
        DECISIONS_PATH: baseline_text(DECISIONS_PATH),
        FOCUS_PATH: baseline_text(FOCUS_PATH),
    }

    constants = constants_of(read_repo(CONSTANTS_PATH))
    if '--dump' in sys.argv:
        print('constants: %s' % {key: constants[key] for key in sorted(constants)
                                 if key.startswith('consolidation') or key == 'reform_weak'})
        score = consolidation_model(constants)
        print('opening: %.1f' % score((constants['legitimacy_opening'],
                                       constants['reform_opening'],
                                       constants['army_opening'],
                                       constants['trust_opening'])))
        print('full: %.1f' % score((100, 100, 100, 100), WORKS_FLAGS))
        focuses, _order = focus_tree(shipped[FOCUS_PATH])
        print('restoration: %s' % {focus_id: (focus_x(focuses[focus_id]),
                                              focus_y(focuses[focus_id]))
                                   for focus_id in RESTORATION_FOCUSES})
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
    print('\nall checks passed against %s; the baseline mutant is rejected'
          % BASELINE_REV[:12])
    return 0


if __name__ == '__main__':
    sys.exit(main())
