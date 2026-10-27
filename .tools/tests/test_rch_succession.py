"""Executes the shipped Republic settlement and succession script.

The module does not restate the formula in Python. It parses the Clausewitz blocks that
ship in common/script_constants, common/scripted_triggers, common/scripted_effects,
common/decisions, common/ideas and common/bop, then runs them against a synthetic RCH
country. Any command this harness does not model raises Unsupported, so an unmodelled
effect fails loudly instead of passing silently.

Flag dates: set_country_flag is modelled as leaving an existing flag's set date alone, so
only an explicit clr_country_flag before the set renews a tenure. That is the stricter of
the two readings of the documented "last set date" wording, and it is why every press
clears its reform gate and its family lock before re-setting them. RCH_TEST_ROOT points
the reader at another tree so the pre-implementation source can be run as a control.

Bookkeeping: each claim is a record of named statements, and the shipped source must pass
every one of them. Every effect handler the suite books a claim on is also probed directly
in handler_models(), and every one of them carries a source mutant in handler_mutants()
that must raise a named defect through the same record. A handler that silently stops
booking its command therefore fails twice, once as a model probe and once as a mutant that
no longer bites. The model is a single-country interpreter, not the engine: it does not
debit a decision's cost, does not schedule events, missions or MTTH, and renders no panel,
popup or focus tree.

Read-only reuse: the tokenizer and block parser come from test_qing_survival.py, which
this module does not modify.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def read(path):
    base = Path(os.environ['RCH_TEST_ROOT']) if os.environ.get('RCH_TEST_ROOT') else ROOT
    return (base / path).read_text(encoding='utf-8-sig')


def plain(text):
    """Mutation helpers compare and rewrite single lines, so strip the CR of a CRLF file."""
    return text.replace('\r\n', '\n')
sys.path.insert(0, str(HERE))

from test_qing_survival import parse_text, Unsupported  # noqa: E402

VERBOSE = '--detail' in sys.argv

CONSTANTS = 'common/script_constants/rch_campaign.txt'
TRIGGERS = 'common/scripted_triggers/rch_campaign.txt'
EFFECTS = 'common/scripted_effects/rch_campaign.txt'
DECISIONS = 'common/decisions/rch_campaign.txt'
CATEGORIES = 'common/decisions/categories/rch_campaign.txt'
EVENTS = 'events/rch_campaign.txt'
IDEAS = 'common/ideas/rch_campaign.txt'
BOP = 'common/bop/RCH.txt'
LOC_DECISIONS = 'localisation/english/rch_campaign_l_english.yml'
LOC_EVENTS = 'localisation/english/rch_campaign_events_l_english.yml'

COMPARE = {
    'greater_than_or_equals': lambda left, right: left >= right,
    'less_than_or_equals': lambda left, right: left <= right,
    'greater_than': lambda left, right: left > right,
    'less_than': lambda left, right: left < right,
    'equals': lambda left, right: left == right,
}

FAILURES = []


def normalise(text):
    """The tokenizer has no string literal, so a DLC name with spaces becomes one token."""
    return text.replace('"Arms Against Tyranny"', 'Arms_Against_Tyranny')


def fail(message):
    FAILURES.append(message)
    print('FAIL ' + message)


def ok(message):
    if VERBOSE:
        print('  ok ' + message)


def check(condition, message):
    if condition:
        ok(message)
    else:
        fail(message)
    return condition


def record_defects(record):
    """The named claims in a record that the source under test does not hold."""
    return [claim + ': ' + problem for claim, problem in record.items() if problem]


def record_checks(record):
    """Print one passing or failing check per named claim."""
    for claim, problem in record.items():
        check(problem is None, claim if problem is None else claim + ' -> ' + problem)


def num(token):
    try:
        return float(token)
    except (TypeError, ValueError):
        raise Unsupported('%r is not a number' % (token,))


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


def named(text, name):
    body = block(parse_text(text), name)
    if body is None:
        raise Unsupported('%s is not defined' % name)
    return body


def nested_named(text, name):
    """Looks for a decision inside its category block as well as at the top level."""
    entries = parse_text(text)
    for key, value, _line in entries:
        if key == name and value[0] == 'block':
            return value[1]
    for key, value, _line in entries:
        if value[0] != 'block':
            continue
        for inner_key, inner_value, _inner_line in value[1]:
            if inner_key == name and inner_value[0] == 'block':
                return inner_value[1]
    raise Unsupported('%s is not defined' % name)


SYMBOL = {
    '>': lambda left, right: left > right,
    '<': lambda left, right: left < right,
    '>=': lambda left, right: left >= right,
    '<=': lambda left, right: left <= right,
}


SEAT_FAMILY = ('rch_succession_constitutional', 'rch_succession_contested',
               'rch_succession_garrison', 'rch_succession_dissolved')


def idea_names(value):
    """add_ideas / remove_ideas take either one id or a block of bare ids.

    A block entry is parsed as (identifier, scalar identifier, line), so the id is the
    scalar value. Returning the whole entry tuple leaves removal a no-op and adds tuples
    to the idea set, which is exactly the silent pass this model must not have.
    """
    if value[0] == 'scalar':
        return value[1].split()
    names = []
    for entry in value[1]:
        if entry[1][0] != 'scalar':
            raise Unsupported('add_ideas/remove_ideas entry at line %d is not modelled'
                              % entry[2])
        names.append(entry[1][1])
    return names


def seat_spirits(subject):
    """The seat spirits standing on the country, with any non-identifier entry named."""
    seats = []
    for idea in subject.ideas:
        if not isinstance(idea, str):
            seats.append('not-an-identifier:%r' % (idea,))
        elif idea in SEAT_FAMILY:
            seats.append(idea)
    return sorted(seats)


class Country:
    def __init__(self, flags=(), variables=None, dlc=('Arms_Against_Tyranny',),
                 controlled=(608,), at_war=(), date='1916.6.6', political_power=400,
                 army_xp=100, tag='RCH'):
        self.flags = {}
        for flag in flags:
            self.flags[flag] = None
        self.variables = dict(variables or {})
        self.dlc = set(dlc)
        self.controlled = set(controlled)
        self.at_war = set(at_war)
        self.date = date
        self.tag = tag
        self.political_power = political_power
        self.army_xp = army_xp
        self.ideas = set()
        self.focus_tree = set()
        self.bop = None
        self.bop_writes = []
        self.queued = []
        self.trace = []
        self.stability = 0.5
        self.flag_dates = {}

    def set_flag(self, flag, date=None):
        if flag not in self.flags:
            self.flags[flag] = date
            self.flag_dates[flag] = date

    def clear_flag(self, flag):
        self.flags.pop(flag, None)
        self.flag_dates.pop(flag, None)

    def age(self, flag, date):
        """Records the date a flag was set, for the maturity comparisons."""
        self.set_flag(flag)
        self.flag_dates[flag] = date

    def value(self, name):
        return self.variables.get(name, 0.0)


class Script:
    def __init__(self, effects_text=None, triggers_text=None, constants_text=None):
        self.constants_text = normalise(read(CONSTANTS) if constants_text is None else constants_text)
        self.triggers_text = normalise(read(TRIGGERS) if triggers_text is None else triggers_text)
        self.effects_text = normalise(read(EFFECTS) if effects_text is None else effects_text)
        self.constants = self._constants()
        self.trigger_names = set(key for key, _v, _l in parse_text(self.triggers_text))
        self.effect_names = set(key for key, _v, _l in parse_text(self.effects_text))

    def _constants(self):
        body = named(self.constants_text, 'rch_story')
        found = {}
        for key, value, _line in body:
            if key == 'schema' or value[0] != 'scalar':
                continue
            found[key] = num(value[1])
        return found

    def constant(self, token):
        match = re.match(r'^constant:rch_story\.([A-Za-z0-9_]+)$', token)
        if match is None:
            raise Unsupported('%r is not an rch_story constant' % (token,))
        name = match.group(1)
        if name not in self.constants:
            raise Unsupported('constant:rch_story.%s is used but not defined' % name)
        return self.constants[name]

    def value(self, token, country):
        if token is None:
            raise Unsupported('missing value')
        if token.startswith('constant:'):
            return self.constant(token)
        if token.startswith('var:'):
            return country.value(token[4:])
        return num(token)

    # -- triggers -----------------------------------------------------------------
    def trigger(self, entries, country, depth=0):
        if depth > 16:
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
                inner = [entry for entry in value[1] if entry[0] != 'tooltip']
                result = result and self.trigger(inner, country, depth)
            elif key == 'always':
                result = result and value[1] == 'yes'
            elif key == 'has_country_flag':
                if value[0] == 'scalar':
                    result = result and value[1] in country.flags
                else:
                    flag = scalar(value[1], 'flag')
                    days = None
                    for entry_key, entry_value, _line in value[1]:
                        if entry_key == 'days':
                            if entry_value[0] != 'compare':
                                raise Unsupported('days shape in flag test')
                            days = (entry_value[1], num(entry_value[2]))
                    if flag is None:
                        raise Unsupported('has_country_flag block without flag')
                    present = flag in country.flags
                    if present and days is not None:
                        set_date = country.flag_dates.get(flag)
                        if set_date is None:
                            # A flag set without a recorded date is treated as brand new.
                            present = days[0] in ('<',) and days[1] > 0
                        else:
                            age = day_number(country.date) - day_number(set_date)
                            present = COMPARE_SYMBOL[days[0]](age, days[1])
                    elif present is False and days is not None:
                        present = False
                    result = result and present
            elif key == 'has_dlc':
                result = result and value[1] in country.dlc
            elif key == 'has_power_balance':
                wanted = scalar(value[1], 'id')
                result = result and country.bop == wanted
            elif key == 'has_war_with':
                result = result and value[1] in country.at_war
            elif key == 'has_focus_tree':
                result = result and value[1] in country.focus_tree
            elif key == 'original_tag':
                result = result and value[1] == country.tag
            elif key == 'controls_state':
                result = result and int(value[1]) in country.controlled
            elif key == 'has_political_power':
                if value[0] == 'scalar':
                    result = result and country.political_power >= self.value(value[1], country)
                else:
                    result = result and SYMBOL[value[1]](country.political_power, num(value[2]))
            elif key == 'has_army_experience':
                if value[0] == 'scalar':
                    result = result and country.army_xp >= self.value(value[1], country)
                else:
                    result = result and country.army_xp >= num(value[1])
            elif key == 'date':
                if value[0] != 'compare':
                    raise Unsupported('date shape at line %d' % line)
                result = result and SYMBOL[value[1]](day_number(country.date),
                                                     day_number(value[2]))
            elif key == 'check_variable':
                name = scalar(value[1], 'var')
                comparer = scalar(value[1], 'compare')
                if name is None or comparer not in COMPARE:
                    raise Unsupported('check_variable shape at line %d' % line)
                result = result and COMPARE[comparer](
                    country.value(name), self.value(scalar(value[1], 'value'), country))
            elif key in self.trigger_names:
                if value[0] != 'scalar' or value[1] != 'yes':
                    raise Unsupported('scripted trigger %s used as a value' % key)
                result = result and self.trigger(named(self.triggers_text, key),
                                                 country, depth + 1)
            else:
                raise Unsupported('trigger %r at line %d is not modelled' % (key, line))
        return result

    def holds(self, trigger_name, country):
        return self.trigger(named(self.triggers_text, trigger_name), country)

    # -- effects ------------------------------------------------------------------
    def effect(self, entries, country, depth=0):
        if depth > 24:
            raise Unsupported('scripted effect recursion is deeper than this check models')
        for key, value, line in entries:
            if key in ('if', 'else_if', 'else'):
                raise Unsupported('orphan %s at line %d' % (key, line))
            if key == 'random_list':
                raise Unsupported('random_list is not modelled')
            if key in self.effect_names:
                if value[0] != 'scalar' or value[1] != 'yes':
                    raise Unsupported('scripted effect %s used as a value' % key)
                self._run_block(named(self.effects_text, key), country, depth + 1)
                continue
            if key in ('set_variable', 'add_to_variable', 'subtract_from_variable',
                       'multiply_variable', 'divide_variable'):
                if value[0] != 'block':
                    raise Unsupported('%s shape at line %d' % (key, line))
                name = scalar(value[1], 'var')
                raw = scalar(value[1], 'value')
                if name is None:
                    # Shorthand: set_variable = { rch_x = 3 }
                    pairs = [(k, v) for k, v, _l in value[1]]
                    if len(pairs) != 1:
                        raise Unsupported('%s shorthand at line %d' % (key, line))
                    name, holder = pairs[0]
                    raw = holder[1] if holder[0] == 'scalar' else None
                amount = self.value(raw, country)
                current = country.value(name)
                if key == 'set_variable':
                    country.variables[name] = amount
                elif key == 'add_to_variable':
                    country.variables[name] = current + amount
                elif key == 'subtract_from_variable':
                    country.variables[name] = current - amount
                elif key == 'multiply_variable':
                    country.variables[name] = current * amount
                else:
                    country.variables[name] = current / amount
            elif key == 'clamp_variable':
                name = scalar(value[1], 'var')
                low = self.value(scalar(value[1], 'min'), country)
                high = self.value(scalar(value[1], 'max'), country)
                country.variables[name] = min(max(country.value(name), low), high)
            elif key == 'round_variable':
                name = value[1] if value[0] == 'scalar' else scalar(value[1], 'var')
                current = country.value(name)
                rounded = int(current + 0.5) if current >= 0 else -int(-current + 0.5)
                country.variables[name] = float(rounded)
            elif key == 'set_country_flag':
                country.set_flag(value[1], country.date)
                country.trace.append(('set', value[1]))
            elif key == 'clr_country_flag':
                country.clear_flag(value[1])
                country.trace.append(('clr', value[1]))
            elif key == 'load_focus_tree':
                tree = scalar(value[1], 'tree')
                if tree is None:
                    raise Unsupported('load_focus_tree without a tree at line %d' % line)
                country.focus_tree.add(tree)
            elif key == 'mark_focus_tree_layout_dirty':
                pass
            elif key == 'add_stability':
                country.stability += self.value(value[1], country)
            elif key == 'add_political_power':
                country.political_power += self.value(value[1], country)
            elif key == 'army_experience':
                country.army_xp += self.value(value[1], country)
            elif key == 'add_ideas':
                country.ideas.update(idea_names(value))
            elif key == 'remove_ideas':
                country.ideas.difference_update(idea_names(value))
            elif key == 'set_power_balance':
                country.bop = scalar(value[1], 'id')
                country.bop_writes.append(('set', self.value(scalar(value[1], 'set_value'), country)))
            elif key == 'add_power_balance_value':
                country.bop_writes.append(('add', self.value(scalar(value[1], 'value'), country)))
            elif key == 'country_event':
                country.queued.append((scalar(value[1], 'id'), self.value(scalar(value[1], 'days'), country)))
            else:
                raise Unsupported('effect %r at line %d is not modelled' % (key, line))

    def run(self, name, country):
        """Executes a scripted effect, including its if/else_if/else chain."""
        self._run_block(named(self.effects_text, name), country, 0)

    def _run_block(self, entries, country, depth):
        index = 0
        while index < len(entries):
            key, value, line = entries[index]
            if key == 'if':
                chain = [entries[index]]
                index += 1
                while index < len(entries) and entries[index][0] in ('else_if', 'else'):
                    chain.append(entries[index])
                    index += 1
                for chain_key, chain_value, chain_line in chain:
                    if chain_key == 'else':
                        self._run_block(chain_value[1], country, depth + 1)
                        break
                    limit = block(chain_value[1], 'limit')
                    if limit is None:
                        raise Unsupported('%s without limit at line %d' % (chain_key, chain_line))
                    if self.trigger(limit, country):
                        self._run_block([entry for entry in chain_value[1]
                                         if entry[0] != 'limit'], country, depth + 1)
                        break
                continue
            if key in ('else_if', 'else'):
                raise Unsupported('orphan %s at line %d' % (key, line))
            self.effect([entries[index]], country, depth)
            index += 1


COMPARE_SYMBOL = {
    '>': lambda left, right: left > right,
    '<': lambda left, right: left < right,
    '>=': lambda left, right: left >= right,
    '<=': lambda left, right: left <= right,
}


def day_number(text):
    year, month, day = (int(part) for part in str(text).split('.'))
    return date(year, month, day).toordinal()


# ------------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------------
OPENING = {'rch_legitimacy': 30.0, 'rch_military_influence': 55.0,
           'rch_nationalist_support': 20.0, 'rch_governor_count': 0.0,
           'rch_reform_settled': 0.0, 'rch_bop_band': -1.0}

EMERGENCY = [
    ((35, 45, 30), 35, 2),
    ((41, 45, 34), 38, 2),
    ((45, 37, 34), 42, 2),
    ((51, 37, 34), 44, 2),
    ((57, 37, 34), 46, 1),
]

# The whole score table in one place, so the positive section and the mutants that must
# break it cannot drift apart.
FIXTURES = ([('emergency %d/%d/%d' % dials, dials, {}, score, tier)
             for dials, score, tier in EMERGENCY] + [
    ('full civil', (62, 37, 38), {'settled': 4, 'throne': True}, 88, 0),
    ('three civil', (56, 37, 38), {'settled': 3, 'throne': True}, 78, 1),
    ('military collapse', (18, 77, 20), {'governors': 3}, 0, 3),
    ('base 44', (72, 40, 0), {}, 44, 2),
    ('base 45', (75, 40, 0), {}, 45, 1),
    ('settled 69', (37, 50, 0), {'settled': 4, 'throne': True}, 69, 1),
    ('settled 70', (40, 50, 0), {'settled': 4, 'throne': True}, 70, 0),
])

CHAPTERS = (('rch_open_chapter_one', 'rch_chapter_one', 'rch_republic'),
            ('rch_open_chapter_two', 'rch_chapter_two', 'rch_warlord'),
            ('rch_open_chapter_three', 'rch_chapter_three', 'rch_nanjing'))


def country(dials, **kwargs):
    variables = dict(OPENING)
    variables['rch_legitimacy'] = float(dials[0])
    variables['rch_military_influence'] = float(dials[1])
    variables['rch_nationalist_support'] = float(dials[2])
    variables.update(kwargs.pop('variables', {}))
    return Country(variables=variables, **kwargs)


def decide(script, dials, settled=0, throne=False, governors=0, **kwargs):
    subject = country(dials, variables={'rch_reform_settled': float(settled),
                                        'rch_governor_count': float(governors)}, **kwargs)
    if throne:
        subject.set_flag('rch_gate_throne_refused', '1915.12.13')
    script.run('rch_succession_refresh', subject)
    script.run('rch_succession_evaluate', subject)
    return subject


def display(script):
    print('display')
    record_checks(display_record(script))


def display_record(script):
    """The panel: one creation, one offset per band change, nothing on an unchanged band."""
    record = {}
    subject = country((30, 65, 20))
    script.run('rch_beiyang_refresh', subject)
    record['the panel is created once'] = (
        None if subject.bop == 'RCH_beiyang_order' else 'the panel is %r' % (subject.bop,))
    last = subject.bop_writes[-1] if subject.bop_writes else None
    record['military 65 publishes the upper band'] = (
        None if last == ('add', 0.25) else 'it publishes %r' % (last,))
    writes = len(subject.bop_writes)
    script.run('rch_beiyang_refresh', subject)
    record['an unchanged band publishes nothing further'] = (
        None if len(subject.bop_writes) == writes
        else 'it publishes %d further writes' % (len(subject.bop_writes) - writes))
    # An existing focus, decision or event writer moves the dial, not a new card.
    subject.variables['rch_military_influence'] = 80.0
    script.run('rch_beiyang_refresh', subject)
    tail = subject.bop_writes[writes:]
    record['a band change retires the old offset and applies the new one once'] = (
        None if tail == [('add', -0.25), ('add', 0.85)] else 'it publishes %r' % (tail,))
    writes = len(subject.bop_writes)
    subject.variables['rch_military_influence'] = 20.0
    script.run('rch_beiyang_refresh', subject)
    tail = subject.bop_writes[writes:]
    record['the bottom band is published from the top band exactly once'] = (
        None if tail == [('add', -0.85), ('add', -0.85)] else 'it publishes %r' % (tail,))
    sealed = Country(variables=dict(OPENING), dlc=())
    script.run('rch_beiyang_refresh', sealed)
    record['without the DLC no balance command runs'] = (
        None if sealed.bop is None and not sealed.bop_writes
        else 'it created %r and wrote %r' % (sealed.bop, sealed.bop_writes))
    sealed.variables['rch_military_influence'] = 90.0
    script.run('rch_succession_refresh', sealed)
    script.run('rch_succession_evaluate', sealed)
    record['the succession resolves identically without the DLC'] = (
        None if sealed.value('rch_succession_tier') == 3.0
        else 'it resolves tier %g' % sealed.value('rch_succession_tier'))
    record['the tuning keys are defined in rch_story'] = (
        None if 'pressure_governor_cap' in script.constants and
        'pressure_cooldown_days' in script.constants else 'a tuning key is missing')
    return record


# ------------------------------------------------------------------------------
# Executed anti-exploit guards: the family locks, the gate tenure and the
# literals that must mirror their constants.
# ------------------------------------------------------------------------------
GATE_OF_FAMILY = {
    'constitution': 'rch_gate_constitution',
    'army': 'rch_gate_officer_rotation',
    'provinces': 'rch_gate_civil_governors',
    'money': 'rch_gate_treasury',
}
LOCK_OF_FAMILY = {
    'constitution': 'rch_press_lock_constitution',
    'army': 'rch_press_lock_army',
    'provinces': 'rch_press_lock_provinces',
    'money': 'rch_press_lock_money',
}


def shift(date_text, days):
    """The date a given number of days away from a script date."""
    moved = date.fromordinal(day_number(date_text) + days)
    return '%d.%d.%d' % (moved.year, moved.month, moved.day)


def family_of(card_id):
    return card_id[len('rch_press_'):].rsplit('_', 1)[0]


def card_specs(decisions):
    """Every pressure card with its family, lock flag, lock window and cooldown literal."""
    specs = []
    for key, value, _line in named(decisions, 'rch_beiyang_order_category'):
        if value[0] != 'block':
            continue
        available = block(value[1], 'available')
        if available is None:
            continue
        tooltip = block(available, 'custom_trigger_tooltip')
        or_block = block(tooltip, 'OR') if tooltip is not None else None
        if or_block is None:
            raise Unsupported('%s has no aged family lock' % key)
        fresh = scalar(block(or_block, 'NOT'), 'has_country_flag')
        aged = block(or_block, 'has_country_flag')
        if aged is None:
            raise Unsupported('%s has no aged family lock' % key)
        window = None
        for entry_key, entry_value, _l in aged:
            if entry_key == 'days':
                window = (entry_value[1], int(num(entry_value[2])))
        specs.append({'id': key, 'family': family_of(key), 'available': available,
                      'fresh': fresh, 'flag': scalar(aged, 'flag'), 'window': window,
                      'cooldown': scalar(value[1], 'days_re_enable')})
    return specs


def availability_defects(script, decisions, cooldown):
    """Executes each card's available block across the family window."""
    defects = []
    for spec in card_specs(decisions):
        if spec['family'] not in LOCK_OF_FAMILY:
            defects.append('%s is not in a known family' % spec['id'])
            continue
        if spec['flag'] != LOCK_OF_FAMILY[spec['family']]:
            defects.append('%s tests %r rather than its family lock' % (spec['id'], spec['flag']))
        for age, expected in ((None, True), (0, False), (cooldown, False), (cooldown + 1, True)):
            subject = country((30, 55, 20))
            if age is not None:
                subject.age(spec['flag'], shift(subject.date, -age))
            got = script.trigger(spec['available'], subject)
            if got != expected:
                defects.append('%s is %s with %s aged %s days, expected %s'
                               % (spec['id'], 'available' if got else 'blocked',
                                  spec['flag'], age, 'available' if expected else 'blocked'))
    return defects


def lock_rearm_defects(script, decisions):
    """A second term must push the family lock's date to the press date, not leave the first."""
    defects = []
    specs = {spec['id']: spec for spec in card_specs(decisions)}
    for family, lock in sorted(LOCK_OF_FAMILY.items()):
        civil = 'rch_press_%s_civil' % family
        military = 'rch_press_%s_military' % family
        subject = country((30, 55, 20))
        script.run(civil, subject)
        subject.date = shift(subject.date, 181)
        script.run(civil, subject)
        age = day_number(subject.date) - day_number(subject.flag_dates.get(lock, '1900.1.1'))
        if age != 0:
            defects.append('%s leaves %s %d days old, so the family opens early'
                           % (civil, lock, age))
        if script.trigger(specs[military]['available'], subject):
            defects.append('%s is available one day after %s' % (military, civil))
    return defects


def press_effects(script):
    return sorted(name for name in script.effect_names
                  if name.startswith('rch_press_') and name != 'rch_press_family_available')


def tenure_defects(script):
    """Every press must clear its gate and its lock before re-setting them."""
    defects = []
    for name in press_effects(script):
        family = family_of(name)
        gate = GATE_OF_FAMILY.get(family)
        lock = LOCK_OF_FAMILY.get(family)
        if gate is None or lock is None:
            defects.append('%s is not in a known family' % name)
            continue
        subject = country((30, 55, 20))
        for flag in set(GATE_OF_FAMILY.values()) | set(LOCK_OF_FAMILY.values()):
            subject.age(flag, shift(subject.date, -400))
        subject.trace = []
        script.run(name, subject)
        trace = subject.trace
        if ('clr', gate) not in trace:
            defects.append('%s never clears %s, so an old tenure survives the press' % (name, gate))
        elif ('set', gate) in trace and trace.index(('clr', gate)) > trace.index(('set', gate)):
            defects.append('%s sets %s before clearing it' % (name, gate))
        if ('clr', lock) not in trace:
            defects.append('%s never clears %s, so the family lock keeps its first date' % (name, lock))
        elif ('set', lock) in trace and trace.index(('clr', lock)) > trace.index(('set', lock)):
            defects.append('%s sets %s before clearing it' % (name, lock))
        if ('set', gate) in trace and subject.flag_dates.get(gate) != subject.date:
            defects.append('%s leaves %s dated %s rather than the press date'
                           % (name, gate, subject.flag_dates.get(gate)))
        if ('set', gate) not in trace and gate in subject.flags:
            defects.append('%s leaves %s standing after the bargain' % (name, gate))
        if subject.flag_dates.get(lock) != subject.date:
            defects.append('%s leaves %s dated %s rather than the press date'
                           % (name, lock, subject.flag_dates.get(lock)))
        for other in set(GATE_OF_FAMILY.values()) - {gate}:
            if ('clr', other) in trace or ('set', other) in trace:
                defects.append('%s touches %s, which belongs to another family' % (name, other))
    return defects


def day_literals(entries, found=None):
    """Every days = <n> comparison in a block tree."""
    found = [] if found is None else found
    for key, value, _line in entries:
        if value[0] == 'block':
            day_literals(value[1], found)
        elif key == 'days' and value[0] == 'compare':
            found.append(int(num(value[2])))
    return found


def controls_literals(entries, found=None):
    """Every controls_state = <id> literal in a block tree."""
    found = [] if found is None else found
    for key, value, _line in entries:
        if key == 'controls_state' and value[0] == 'scalar':
            found.append(int(value[1]))
        if value[0] == 'block':
            controls_literals(value[1], found)
    return found


def mirror_defects(script):
    """Every literal the engine fields demand must equal the constant it documents."""
    defects = []
    for key in ('pressure_cooldown_days', 'succession_gate_maturity_days',
                'succession_capital_state'):
        if key not in script.constants:
            defects.append('constant rch_story.%s is not defined' % key)
    if defects:
        return defects
    cooldown = int(script.constants['pressure_cooldown_days'])
    maturity = int(script.constants['succession_gate_maturity_days'])
    capital = int(script.constants['succession_capital_state'])
    for spec in card_specs(read(DECISIONS)):
        if spec['window'] is None:
            defects.append('%s has no aged lock window' % spec['id'])
        elif spec['window'][1] != cooldown:
            defects.append('%s locks for %d days, rch_story.pressure_cooldown_days is %d'
                           % (spec['id'], spec['window'][1], cooldown))
        if spec['cooldown'] is None:
            defects.append('%s has no days_re_enable' % spec['id'])
        elif int(num(spec['cooldown'])) != cooldown:
            defects.append('%s re-enables after %s days, rch_story.pressure_cooldown_days is %d'
                           % (spec['id'], spec['cooldown'], cooldown))
    snapshot = day_literals(named(script.effects_text, 'rch_settlement_snapshot'))
    if not snapshot:
        defects.append('the settlement snapshot has no maturity window to mirror')
    for days in snapshot:
        if days != maturity:
            defects.append('the settlement snapshot counts %d days, '
                           'rch_story.succession_gate_maturity_days is %d' % (days, maturity))
    states = controls_literals(parse_text(read(TRIGGERS)))
    if not states:
        defects.append('no state requirement to mirror the capital constant')
    for state in states:
        if state != capital:
            defects.append('controls_state = %d, rch_story.succession_capital_state is %d'
                           % (state, capital))
    return defects


def mirrors(script):
    print('constant and literal mirrors')
    defects = mirror_defects(script)
    check(not defects, 'every engine literal mirrors its constant: ' + '; '.join(defects))


def locks(script):
    print('family locks')
    decisions = read(DECISIONS)
    cooldown = int(script.constants['pressure_cooldown_days'])
    defects = availability_defects(script, decisions, cooldown)
    check(not defects,
          'each family lock blocks at 0 and %d days and releases at %d: '
          % (cooldown, cooldown + 1) + '; '.join(defects))
    rearm = lock_rearm_defects(script, decisions)
    check(not rearm, 'a second term re-arms the family lock at the press date: ' + '; '.join(rearm))


def tenure(script):
    print('gate tenure')
    defects = tenure_defects(script)
    check(not defects,
          'every press clears its gate and lock before re-setting them: ' + '; '.join(defects))


def daily_tick(script):
    """The tick itself must settle, queue once and republish the display."""
    print('daily tick')
    subject = tick_state(script)
    check(subject.value('rch_succession_final_tier') == 1,
          'the tick settles the succession on the first eligible day')
    check('rch_succession_resolved' in subject.flags, 'the tick records the resolution')
    popups = [event for event, _days in subject.queued if event == 'rch_campaign.5']
    check(popups == ['rch_campaign.5'], 'the tick queues the one succession popup')
    check(subject.bop == 'RCH_beiyang_order', 'the tick republishes the display every day')
    state = (len(subject.queued), sorted(subject.ideas), len(subject.bop_writes), subject.bop)
    script.run('rch_campaign_tick', subject)
    check((len(subject.queued), sorted(subject.ideas), len(subject.bop_writes), subject.bop) == state,
          'a second tick on the same day changes nothing')
    quiet = quiet_tick(script)
    check(quiet.bop == 'RCH_beiyang_order',
          'a quiet day with no chapter, settlement or succession work still publishes the display')
    check('rch_campaign.5' not in [event for event, _days in quiet.queued],
          'a quiet day cannot re-announce a resolved succession')


def quiet_tick(script):
    """A day whose only display work is the daily refresh itself."""
    subject = country((62, 37, 38), date='1917.1.2')
    for flag in ('rch_campaign_active', 'rch_chapter_two', 'rch_succession_resolved'):
        subject.set_flag(flag)
    script.run('rch_campaign_tick', subject)
    return subject


def tick_state(script):
    subject = country((62, 37, 38))
    subject.set_flag('rch_campaign_active')
    script.run('rch_campaign_tick', subject)
    return subject



def main():
    try:
        return run()
    except Unsupported as error:
        fail('a shipped command is not modelled, so the suite cannot pass: %s' % error)
        print()
        print('%d check(s) failed' % len(FAILURES))
        return 1


def run():
    script = Script()
    cards(script)
    chapters(script)
    costs(script)
    succession(script)
    precedence(script)
    maturity(script)
    idempotence(script)
    referential(script)
    display_contract(script)
    score_readout(script)
    display(script)
    mirrors(script)
    locks(script)
    tenure(script)
    daily_tick(script)
    handler_models()
    mutants()
    loc_mutants()
    display_contract_mutants()
    score_readout_mutants()
    guard_mutants()
    handler_mutants()
    if '--no-baseline' not in sys.argv:
        baseline_control()
    print()
    if FAILURES:
        print('%d check(s) failed' % len(FAILURES))
        return 1
    print('all checks passed')
    return 0


def cards(script):
    print('cards')
    decisions = read(DECISIONS)
    expected = {
        'rch_press_constitution_civil': {'rch_legitimacy': 6, 'rch_nationalist_support': 4},
        'rch_press_constitution_military': {'rch_legitimacy': -4, 'rch_military_influence': 8},
        'rch_press_army_civil': {'rch_legitimacy': 4, 'rch_military_influence': -8},
        'rch_press_army_military': {'rch_military_influence': 8},
        'rch_press_provinces_civil': {'rch_legitimacy': 6},
        'rch_press_provinces_military': {'rch_legitimacy': -4},
        'rch_press_money_civil': {'rch_legitimacy': 6},
        'rch_press_money_military': {'rch_military_influence': 6, 'rch_legitimacy': -4},
    }
    body = named(decisions, 'rch_beiyang_order_category')
    present = set(key for key, value, _line in body if value[0] == 'block')
    check(present == set(expected), 'eight pressure cards are defined')
    for card, deltas in sorted(expected.items()):
        card_body = nested_named(decisions, card)
        effect = block(card_body, 'complete_effect')
        subject = country((30, 55, 20))
        script.effect(effect, subject)
        for name, delta in sorted(deltas.items()):
            check(subject.value(name) == OPENING[name] + delta,
                  '%s moves %s by %s' % (card, name, delta))
        check(block(card_body, 'ai_will_do') is not None, '%s carries ai_will_do' % card)
        check(scalar(card_body, 'days_re_enable') == '180', '%s cools down for 180 days' % card)
        available = block(card_body, 'available')
        check(any(entry[0] == 'custom_trigger_tooltip' for entry in available),
              '%s explains its family lock' % card)
    governor = country((30, 55, 20))
    for _ in range(4):
        script.run('rch_press_provinces_military', governor)
    check(governor.value('rch_governor_count') == 3.0, 'governor counter clamps at three')


def chapters(script):
    print('chapters')
    record_checks(chapter_record(script))


def chapter_record(script):
    """One opener, one chapter flag, one tree, even when a stale chapter is standing."""
    record = {}
    chapter_flags = {'rch_chapter_one', 'rch_chapter_two', 'rch_chapter_three'}
    for opener, chapter, tree in CHAPTERS:
        subject = Country()
        for other in sorted(chapter_flags - {chapter}):
            subject.set_flag(other)
        script.run(opener, subject)
        standing = sorted(set(subject.flags) & chapter_flags)
        record['%s leaves only %s' % (opener, chapter)] = (
            None if standing == [chapter] else 'it leaves %s' % (standing,))
        record['%s loads %s' % (opener, tree)] = (
            None if subject.focus_tree == {tree}
            else 'it loads %s' % (sorted(subject.focus_tree),))
    return record


def costs(script):
    print('costs')
    record_checks(cost_record(script))


def cost_record(script):
    """Opposing stability costs: the two civil bargains must pull in opposite directions."""
    record = {}
    gain = script.constants['pressure_stability_gain']
    subject = country((30, 55, 20))
    script.run('rch_press_constitution_civil', subject)
    record['the constitution bargain gains stability'] = (
        None if subject.stability > 0.5 and subject.stability == 0.5 + gain
        else 'stability is %g' % subject.stability)
    cost = script.constants['pressure_stability_cost']
    subject = country((30, 55, 20))
    script.run('rch_press_money_civil', subject)
    record['the treasury bargain costs stability'] = (
        None if subject.stability < 0.5 and subject.stability == 0.5 + cost
        else 'stability is %g' % subject.stability)
    return record


def succession(script):
    print('succession')
    for label, dials, options, score, tier in FIXTURES:
        subject = decide(script, dials, **options)
        check(subject.value('rch_succession_score') == float(score),
              '%s scores %d' % (label, score))
        check(subject.value('rch_succession_tier') == float(tier),
              '%s resolves tier %d' % (label, tier))


def score_record(script):
    """The whole score table as named claims, for the mutants that must break it."""
    record = {}
    for label, dials, options, score, tier in FIXTURES:
        subject = decide(script, dials, **options)
        actual = subject.value('rch_succession_score')
        record['%s scores %d' % (label, score)] = (
            None if actual == float(score) else 'it scores %g' % actual)
        resolved = subject.value('rch_succession_tier')
        record['%s resolves tier %d' % (label, tier)] = (
            None if resolved == float(tier) else 'it resolves tier %g' % resolved)
    return record


def precedence(script):
    print('precedence')
    full = decide(script, (90, 85, 40), settled=4, throne=True)
    floor = decide(script, (15, 40, 20))
    earned = decide(script, (62, 37, 38), settled=4, throne=True)
    governed = decide(script, (62, 37, 38), settled=4, throne=True, governors=3)
    governed.variables['rch_governor_count'] = 3.0
    script.run('rch_succession_evaluate', governed)
    check(full.value('rch_succession_tier') == 3,
          'collapse override beats a full score and a full settlement')
    check(floor.value('rch_succession_tier') == 3, 'legitimacy floor fires')
    check(earned.value('rch_succession_tier') == 0,
          'four settled reforms and the throne reach tier 0')
    check(governed.value('rch_succession_tier') == 1, 'three governors exclude tier 0')
    for subject in (full, floor, earned, governed):
        tiers = [tier for tier, trigger in ((3, 'rch_succession_collapse'),
                                            (0, 'rch_succession_tier_0'),
                                            (1, 'rch_succession_tier_1'))
                 if script.holds(trigger, subject)]
        check(len(set(tiers)) == len(tiers), 'tier triggers are exclusive')


def maturity(script):
    print('maturity')
    for date_text, expected in (('1915.6.14', 4), ('1915.6.15', 0)):
        subject = country((62, 37, 38), date='1915.12.12')
        for flag in ('rch_gate_constitution', 'rch_gate_officer_rotation',
                     'rch_gate_civil_governors', 'rch_gate_treasury'):
            subject.age(flag, date_text)
        script.run('rch_settlement_snapshot', subject)
        check(subject.value('rch_reform_settled') == expected,
              'gates dated %s count %d' % (date_text, expected))
    sealed = country((30, 55, 20), date='1916.1.1')
    script.run('rch_succession_endow', sealed)
    check(sealed.value('rch_reform_settled') == 0, 'a 1916 start receives a sealed zero snapshot')
    check('rch_hongxian' in sealed.flags, 'a 1916 start inherits the Hongxian state')
    check('rch_gate_throne_refused' not in sealed.flags, 'a 1916 start cannot refuse the throne')
    late = Country(variables=dict(OPENING), date='1918.3.21')
    script.run('rch_succession_endow', late)
    check('rch_succession_resolved' in late.flags, 'a 1918 start resolves silently')
    check(not late.queued, 'a 1918 start receives no succession popup')


def idempotence(script):
    print('idempotence')
    record_checks(spirit_record(script))


def spirit_record(script):
    """The settlement record, and what a later mechanics refresh must not disturb.

    A seat spirit from an earlier line is already standing when the settlement runs, so a
    removal that does not actually remove is caught by the seat claim instead of hiding
    behind an idea set that never held a rival seat in the first place.
    """
    record = {}
    subject = country((62, 37, 38), date='1916.6.6',
                      variables={'rch_reform_settled': 4.0})
    subject.set_flag('rch_gate_throne_refused', '1915.12.13')
    subject.ideas.add('rch_succession_dissolved')
    for _ in range(3):
        script.run('rch_succession_resolve', subject)
    record['three same-day resolves queue one popup'] = (
        None if len(subject.queued) == 1 else '%d popups were queued' % len(subject.queued))
    record['resolution is recorded once'] = (
        None if 'rch_succession_resolved' in subject.flags else 'the flag is absent')
    score = subject.value('rch_succession_final_score')
    record['the frozen score is 88'] = (
        None if score == 88.0 else 'the frozen score is %g' % score)
    tier = subject.value('rch_succession_final_tier')
    record['the frozen tier is 0'] = (
        None if tier == 0.0 else 'the frozen tier is %g' % tier)
    seats = seat_spirits(subject)
    record['the settlement leaves exactly one seat spirit'] = (
        None if seats == ['rch_succession_constitutional'] else 'it leaves %s' % (seats,))
    # A seat from an earlier line standing beside another idea: the seat effect must replace
    # the seat and leave the unrelated idea alone.
    seeded = country((62, 37, 38), date='1916.6.6')
    seeded.set_flag('rch_line_unified', '1916.6.6')
    seeded.ideas.update({'rch_succession_dissolved', 'rch_beiyang_republic'})
    script.run('rch_succession_seat_spirit', seeded)
    seats = seat_spirits(seeded)
    record['the seat spirit replaces an earlier seat'] = (
        None if seats == ['rch_succession_constitutional']
        else 'it leaves %s' % (seats,))
    record['the seat spirit leaves an unrelated idea alone'] = (
        None if 'rch_beiyang_republic' in seeded.ideas
        else 'it removed rch_beiyang_republic')
    collapsed = country((18, 77, 20), variables={'rch_governor_count': 3.0}, date='1916.6.6')
    script.run('rch_succession_resolve', collapsed)
    tier = collapsed.value('rch_succession_final_tier')
    record['a collapsed succession freezes tier 3'] = (
        None if tier == 3.0 else 'the frozen tier is %g' % tier)
    script.run('rch_refresh_mechanics', subject)
    subject.variables['rch_legitimacy'] = 5.0
    script.run('rch_refresh_mechanics', subject)
    after = subject.value('rch_succession_final_score')
    record['a mechanics refresh cannot change the frozen score'] = (
        None if after == 88.0 else 'the frozen score became %g' % after)
    seats = seat_spirits(subject)
    record['a mechanics refresh cannot delete the seat spirit'] = (
        None if seats == ['rch_succession_constitutional'] else 'it leaves %s' % (seats,))
    return record


def panel_ids(bop):
    """Every identifier the balance panel draws: its title, both sides and every range."""
    body = '\n'.join(line for line in bop.splitlines() if not line.lstrip().startswith('#'))
    ids = []
    title = body.strip().split('=')[0].strip()
    if title:
        ids.append(title)
    for field in ('left_side', 'right_side'):
        match = re.search(r'^\t' + field + r' = (\w+)', body, re.M)
        if match is None:
            fail('common/bop/RCH.txt does not declare ' + field)
            continue
        ids.append(match.group(1))
    ids.extend(re.findall(r'^\t+id = (\w+)', body, re.M))
    seen = []
    for identifier in ids:
        if identifier not in seen:
            seen.append(identifier)
    return seen


def panel_loc_missing(loc, bop):
    """The panel keys the player would see as raw identifiers."""
    return [identifier for identifier in panel_ids(bop)
            if ' ' + identifier + ':' not in loc]


def family_lock_text(loc):
    """The single localisation value the shared family lock tooltip draws."""
    match = re.search(r'^ rch_press_family_available: "([^"]*)"', loc, re.M)
    return match.group(1) if match else None


def family_lock_defects(loc):
    """Reasons the shared family lock tooltip would contradict the requirement it draws."""
    text = family_lock_text(loc)
    if text is None:
        return ['the tooltip key is missing']
    defects = []
    for word in ('already', 'cards', '180'):
        if word in text:
            defects.append('it states %r, which is the blocked state or the tuning rule' % word)
    if 'has not' not in text:
        defects.append('it does not state what the government has still to do')
    return defects


def family_lock_attachments(text):
    """Every card that attaches the shared lock tooltip, with the flag and the flag it ages."""
    pattern = (r'tooltip = rch_press_family_available\s*OR = \{\s*'
               r'NOT = \{ has_country_flag = (\w+) \}\s*'
               r'has_country_flag = \{ flag = (\w+) days > \d+ \}\s*\}')
    return re.findall(pattern, text)


SETTLEMENT_DATE = '12 December 1915'
SETTLEMENT_WINDOW = 'more than 180 days'
SETTLEMENT_MEASURES = (
    ('constitution', 'rch_press_constitution_civil', 'rch_gate_constitution'),
    ('officer corps', 'rch_press_army_civil', 'rch_gate_officer_rotation'),
    ('civil governors', 'rch_press_provinces_civil', 'rch_gate_civil_governors'),
    ('ministries', 'rch_press_money_civil', 'rch_gate_treasury'),
)
TERRITORIAL_WORDS = ('territor', 'cede', 'cession', 'annex', 'partition')


def loc_value(loc, key):
    """The one English value a key draws, or a loud failure when the key has no text."""
    match = re.search(r'^ ' + re.escape(key) + r': "([^"]*)"', loc, re.M)
    if match is None:
        fail(key + ' has no English value, so the text it should draw cannot be verified')
        return ''
    return match.group(1)


SCORE_VARIABLE = 'rch_succession_final_score'
SCORE_TOKEN = '[?rch_succession_final_score|0]'
SCORE_LABEL = 'Seat standing'
SCORE_RANGE = 'out of 100'
VARIABLE_EXPRESSION = re.compile(r'\[\?([A-Za-z0-9_]+)(\|[^\]\s]*)?\]')

# A consumer prints the frozen score only where the frozen score exists. The popup is drawn
# after rch_succession_settle assigns it, and the four seat spirits are added by the same
# effect, so each of these is reachable exactly when the variable is.
SCORE_CONSUMERS = (
    ('the succession popup', LOC_EVENTS, 'rch_campaign.5.d'),
    ('the constitutional seat', LOC_DECISIONS, 'rch_succession_constitutional_desc'),
    ('the contested seat', LOC_DECISIONS, 'rch_succession_contested_desc'),
    ('the garrison seat', LOC_DECISIONS, 'rch_succession_garrison_desc'),
    ('the dissolved seat', LOC_DECISIONS, 'rch_succession_dissolved_desc'),
)
PHASE_CONSUMERS = (
    ('the settlement announcement', LOC_EVENTS, 'rch_campaign.2.d'),
    ('the succession popup', LOC_EVENTS, 'rch_campaign.5.d'),
)
RESOLUTION_PHRASES = ('judged when the presidency falls', 'judged when the presidency fell',
                      'judged at the succession', 'judged on resolution')
RECORD_CLOSED_PHRASES = ('reform record closes', 'reform record closed', 'record was closed')
FALSE_PHASE_CLAIMS = ('the judgement had been fixed on',
                      'nothing done after the settlement day changed the reckoning',
                      'the judgement falls due on')
TIER_SEAT = {0: 'rch_succession_constitutional', 1: 'rch_succession_contested',
             2: 'rch_succession_garrison', 3: 'rch_succession_dissolved'}


def variable_expressions(text):
    """Every formatted variable a localisation value would draw, as (raw, name, format)."""
    return [(match.group(0), match.group(1), match.group(2))
            for match in VARIABLE_EXPRESSION.finditer(text)]


def score_readout_defects(text):
    """Reasons a value does not print the frozen standing, and only that number."""
    defects = []
    if SCORE_TOKEN not in text:
        defects.append('it does not print the frozen score as ' + SCORE_TOKEN)
    if SCORE_LABEL.lower() not in text.lower():
        defects.append('it does not label the number as the succession standing')
    if SCORE_RANGE not in text:
        defects.append('it does not state the ' + SCORE_RANGE + ' range')
    for raw, name, path in variable_expressions(text):
        if name == 'rch_succession_score':
            defects.append('it prints the live scratch %s instead of the frozen score' % raw)
        elif name != SCORE_VARIABLE:
            defects.append('it prints the unrelated variable %s' % raw)
        elif path != '|0':
            defects.append('it prints %s without integer formatting' % raw)
    for bracket in re.findall(r'\[[^\]]*\]', text):
        if 'rch_succession' in bracket and bracket != SCORE_TOKEN:
            defects.append('it carries the malformed variable expression %s' % bracket)
    return defects


def category_lifetime_defects(text):
    """The pre-resolution category must not draw a score the succession has not set yet."""
    return ['it draws %s before the succession assigns it' % bracket
            for bracket in re.findall(r'\[[^\]]*\]', text) if 'rch_succession' in bracket]


def phase_claim_defects(text):
    """Reasons the text still confuses the December record with the judgement at resolution."""
    defects = []
    lowered = text.lower()
    for claim in FALSE_PHASE_CLAIMS:
        if claim in lowered:
            defects.append('it still claims %r' % claim)
    if not any(phrase in lowered for phrase in RECORD_CLOSED_PHRASES):
        defects.append('it does not say December closes the reform record')
    if not any(phrase in lowered for phrase in RESOLUTION_PHRASES):
        defects.append('it does not say the succession judges the score when it falls')
    return defects


class UndefinedVariable(Exception):
    pass


def interpolate(text, subject):
    """The text a country draws, refusing to default an unset variable to zero."""
    drawn = text
    for raw, name, path in variable_expressions(text):
        if name not in subject.variables:
            raise UndefinedVariable(name)
        number = subject.variables[name]
        drawn = drawn.replace(raw, str(int(round(number))) if path == '|0' else '%g' % number)
    return drawn


def drawn_standing(text, subject):
    """(number, defect): the standing a consumer shows for this country, with absence named."""
    try:
        drawn = interpolate(text, subject)
    except UndefinedVariable as error:
        return None, 'it prints %s, which the country does not hold' % error
    match = re.search(re.escape(SCORE_LABEL) + r': (-?\d+) ' + re.escape(SCORE_RANGE), drawn)
    if match is None:
        return None, 'the drawn text carries no standing number'
    return int(match.group(1)), None


def settlement_rule_defects(text):
    """Reasons the text does not tell the player when the record is judged and how it counts."""
    defects = []
    if SETTLEMENT_DATE not in text:
        defects.append('it does not name the ' + SETTLEMENT_DATE + ' settlement')
    if SETTLEMENT_WINDOW not in text:
        defects.append('it does not state the ' + SETTLEMENT_WINDOW + ' tenure')
    if 'count' not in text:
        defects.append('it does not say what counts toward the seat')
    return defects


def seat_condition_defects(text):
    """Reasons the text does not state the conditions the seat was judged on."""
    defects = []
    for measure, _card, _gate in SETTLEMENT_MEASURES:
        if measure not in text:
            defects.append('it does not name the ' + measure)
    for token in ('crown', 'Beijing', 'Chinese government', 'governors'):
        if token not in text:
            defects.append('it does not state the ' + token + ' condition')
    return defects


def territorial_claim_defects(text):
    """A succession tier is not fragmentation, so the text must claim no territorial loss.

    The words match at a word boundary. A substring test reads the ordinary noun
    'succession', and the variable name rch_succession_final_score, as a cession, which
    would forbid the readout this contract requires; 'cession' as a word is still caught.
    """
    lowered = text.lower()
    return ['it claims a territorial change with %r' % word
            for word in TERRITORIAL_WORDS if re.search(r'\b' + word, lowered)]


def referential(script):
    print('referential integrity')
    ideas = read(IDEAS)
    spirits = ('rch_succession_constitutional', 'rch_succession_contested',
               'rch_succession_garrison', 'rch_succession_dissolved')
    for spirit in spirits:
        check((spirit + ' = {') in ideas, '%s is defined' % spirit)
    removal = str(named(script.effects_text, 'rch_refresh_mechanics'))
    for spirit in spirits:
        check(spirit in removal, '%s is in the refresh removal list' % spirit)
    loc = read(LOC_DECISIONS)
    for key in ('rch_beiyang_order_category', 'rch_beiyang_order_category_desc',
                'rch_press_family_available'):
        check(' ' + key + ':' in loc, '%s is localised' % key)
    body = nested_named(read(DECISIONS), 'rch_beiyang_order_category')
    for key, value, _line in body:
        if value[0] != 'block':
            continue
        check(' ' + key + ':' in loc, '%s has a name' % key)
        check(' ' + key + '_desc:' in loc, '%s has a description' % key)
    for spirit in spirits:
        check(' ' + spirit + ':' in loc, '%s has a name' % spirit)
        check(' ' + spirit + '_desc:' in loc, '%s has a description' % spirit)
    events_loc = read(LOC_EVENTS)
    for event_id in ('rch_campaign.2', 'rch_campaign.5', 'rch_campaign.42'):
        check(' ' + event_id + '.t:' in events_loc, '%s has a title' % event_id)
        check(' ' + event_id + '.d:' in events_loc, '%s has a description' % event_id)
    for option in ('rch_campaign.2.a', 'rch_campaign.42.a', 'rch_campaign.42.b',
                   'rch_campaign.5.a', 'rch_campaign.5.b',
                   'rch_campaign.5.c', 'rch_campaign.5.e'):
        check(' ' + option + ':' in events_loc, '%s is localised' % option)
    crisis = read(EVENTS).split('id = rch_campaign.5')[1].split('country_event')[0]
    check('ai_chance' not in crisis, 'the single visible succession option carries no ai_chance')
    check('immediate' not in crisis, 'the succession popup recomputes nothing')
    bop = read(BOP)
    check('decision_category = rch_beiyang_order_category' in bop,
          'the panel points at the category that exists')
    check('rch_beiyang_order_category = {' in read(CATEGORIES),
          'the category is defined once')
    ids = panel_ids(bop)
    check(len(ids) == 8,
          'the panel declares one title, two sides and five ranges (found %d)' % len(ids))
    missing = panel_loc_missing(loc, bop)
    check(not missing,
          'every panel id is localised, which fails on: ' + ', '.join(missing))
    defects = family_lock_defects(loc)
    check(not defects,
          'the family lock tooltip reads as the requirement it draws, not the lock: '
          + ', '.join(defects))
    attachments = family_lock_attachments(read(DECISIONS))
    check(len(attachments) == 8,
          'all eight cards attach the shared family lock tooltip (found %d)' % len(attachments))
    for lock_flag, age_flag in attachments:
        check(lock_flag == age_flag,
              'the tooltip lock %s is tested against its own flag' % lock_flag)


def mutants():
    print('mutants')
    threshold = read(CONSTANTS).replace('succession_tier1_score = 45',
                                        'succession_tier1_score = 44')
    script = Script(constants_text=threshold)
    subject = decide(script, (72, 40, 0))
    check(subject.value('rch_succession_tier') != 2,
          'mutant succession_tier1_score 45 to 44 breaks the 44 boundary')
    gain = read(CONSTANTS).replace('pressure_legitimacy_gain = 6',
                                   'pressure_legitimacy_gain = 7')
    script = Script(constants_text=gain)
    card = nested_named(read(DECISIONS), 'rch_press_constitution_civil')
    subject = country((30, 55, 20))
    script.effect(block(card, 'complete_effect'), subject)
    check(subject.value('rch_legitimacy') != 36, 'mutant legitimacy gain 6 to 7 is caught')
    loose = read(EFFECTS).replace('days > 180 }', 'days > 0 }', 4)
    script = Script(effects_text=loose)
    subject = country((62, 37, 38), date='1915.12.12')
    for flag in ('rch_gate_constitution', 'rch_gate_officer_rotation',
                 'rch_gate_civil_governors', 'rch_gate_treasury'):
        subject.age(flag, '1915.6.15')
    script.run('rch_settlement_snapshot', subject)
    check(subject.value('rch_reform_settled') != 3,
          'mutant maturity 180 to 0 makes the 1915.6.15 row count four')
    unclamped = read(EFFECTS).replace(
        '\tclamp_variable = { var = rch_governor_count min = constant:rch_story.pressure_governor_floor max = constant:rch_story.pressure_governor_cap }\n', '')
    unclamped = unclamped.replace('\tclamp_variable = { var = rch_governor_count min = constant:rch_story.pressure_governor_floor max = constant:rch_story.pressure_governor_cap }\r\n', '')
    script = Script(effects_text=unclamped)
    subject = country((30, 55, 20))
    for _ in range(4):
        script.run('rch_press_provinces_military', subject)
    check(subject.value('rch_governor_count') == 4.0,
          'mutant without the clamp reaches four governors')


def loc_mutants():
    print('localisation mutants')
    loc = read(LOC_DECISIONS)
    orphans = '\n'.join(line for line in loc.splitlines()
                        if 'RCH_side_' not in line and 'RCH_bop_' not in line)
    missing = panel_loc_missing(orphans, read(BOP))
    check(len(missing) == 7,
          'mutant without the side and range keys leaves seven raw panel ids (found %d)'
          % len(missing))
    check(not panel_loc_missing(loc, read(BOP)),
          'the shipped panel keys are all localised')
    inverted = loc.replace(
        ' rch_press_family_available: "The government has not pressed this matter in the past six months."',
        ' rch_press_family_available: "This family of cards has already acted in the last 180 days."')
    check(inverted != loc, 'the tooltip mutant edits the shipped value')
    check(family_lock_defects(inverted),
          'mutant with the blocked state as the tooltip is caught')
    check(not family_lock_defects(loc),
          'the shipped tooltip passes the same predicate')
    dropped = read(DECISIONS).replace('tooltip = rch_press_family_available',
                                      'tooltip = rch_press_family_clock', 1)
    check(len(family_lock_attachments(dropped)) == 7,
          'mutant with one card off the shared tooltip is caught')


def display_contract(script):
    """The player must be able to read how the seat is judged and on what evidence."""
    print('display contract')
    category = loc_value(read(LOC_DECISIONS), 'rch_beiyang_order_category_desc')
    intro = loc_value(read(LOC_EVENTS), 'rch_campaign.2.d')
    death = loc_value(read(LOC_EVENTS), 'rch_campaign.5.d')
    for name, text in (('the category description', category),
                       ('the settlement announcement', intro),
                       ('the succession popup', death)):
        check(text != '', name + ' carries English text')
        defects = settlement_rule_defects(text)
        check(not defects, name + ' states the settlement rule: ' + ', '.join(defects))
        defects = territorial_claim_defects(text)
        check(not defects, name + ' claims no territorial change: ' + ', '.join(defects))
    for name, text in (('the category description', category),
                       ('the succession popup', death)):
        defects = seat_condition_defects(text)
        check(not defects, name + ' states what the seat was judged on: ' + ', '.join(defects))
    for measure, card_id, gate in SETTLEMENT_MEASURES:
        decision = nested_named(read(DECISIONS), card_id)
        subject = country((30, 55, 20))
        script.effect(block(decision, 'complete_effect'), subject)
        check(gate in subject.flags,
              'the %s the text names is the card that sets %s' % (measure, gate))
    settle = str(named(script.effects_text, 'rch_succession_settle'))
    check('rch_settlement_snapshot' not in settle,
          'the popup path never retakes the settlement the text describes')


def display_contract_mutants():
    """Each clause of the display contract must be load-bearing, not decorative."""
    print('display contract mutants')
    decisions_loc = read(LOC_DECISIONS)
    events_loc = read(LOC_EVENTS)
    category = loc_value(decisions_loc, 'rch_beiyang_order_category_desc')
    death = loc_value(events_loc, 'rch_campaign.5.d')

    paragraphs = category.split('\\n\\n')
    check(len(paragraphs) == 2,
          'the category description states the settlement in its own paragraph (found %d)'
          % len(paragraphs))
    if len(paragraphs) == 2:
        check(settlement_rule_defects(paragraphs[0]),
              'mutant without the settlement paragraph is caught by the rule predicate')
        check(not settlement_rule_defects(category),
              'the shipped category text passes the same rule predicate')

    silent = category.replace('The constitution, the rotation of the officer corps, ',
                              'The rotation of the officer corps, ')
    check(silent != category, 'the counted-reform mutant edits the shipped category text')
    check(seat_condition_defects(silent),
          'mutant that drops one counted reform from the text is caught')

    vague = death.replace(SETTLEMENT_WINDOW, 'a long tenure')
    check(vague != death, 'the tenure mutant edits the shipped popup text')
    check(settlement_rule_defects(vague),
          'mutant that replaces the 180-day tenure with a vague one is caught')

    lost = category + ' The government cedes the northern provinces.'
    check(territorial_claim_defects(lost),
          'mutant that claims a territorial loss in the text is caught')

    ceded = category + ' The government accepts the cession of Shandong.'
    check(any('cession' in defect for defect in territorial_claim_defects(ceded)),
          'mutant that names a cession outright is still caught')
    check(not territorial_claim_defects(death),
          'the noun succession and the score variable are not read as a cession')


def score_readout(script):
    """The frozen standing is readable on the surfaces that exist after it is assigned."""
    print('score readout')
    record_checks(score_readout_record(script))
    for name, path, key in PHASE_CONSUMERS:
        defects = phase_claim_defects(loc_value(read(path), key))
        check(not defects,
              name + ' separates the record from the judgement: ' + ', '.join(defects))


def score_readout_record(script):
    """Every surface the standing reaches, drawn from the variable the shipped settle sets.

    Nothing here seeds rch_succession_final_score: each fixture is resolved through the
    shipped rch_succession_settle, and the number compared is the one that effect assigned.
    """
    record = {}
    texts = {}
    for name, path, key in SCORE_CONSUMERS:
        texts[key] = loc_value(read(path), key)
        defects = score_readout_defects(texts[key])
        record[name + ' prints the frozen standing'] = (
            None if not defects else ', '.join(defects))
    category = loc_value(read(LOC_DECISIONS), 'rch_beiyang_order_category_desc')
    defects = category_lifetime_defects(category)
    record['the pre-resolution category draws no score'] = (
        None if not defects else ', '.join(defects))

    popup = texts['rch_campaign.5.d']
    for label, dials, options, score, tier in FIXTURES:
        subject = decide(script, dials, **options)
        record['%s holds no standing before the succession' % label] = (
            None if SCORE_VARIABLE not in subject.variables
            else 'the score exists before resolution')
        script.run('rch_succession_resolve', subject)
        record['%s freezes the settled score %d' % (label, score)] = (
            None if subject.variables.get(SCORE_VARIABLE) == float(score)
            else 'it froze %r' % (subject.variables.get(SCORE_VARIABLE),))
        number, defect = drawn_standing(popup, subject)
        record['%s popup draws %d' % (label, score)] = (
            defect if defect else None if number == score else 'it draws %r' % (number,))
        seat = TIER_SEAT[tier]
        record['%s leaves the %s standing' % (label, seat)] = (
            None if seat_spirits(subject) == [seat]
            else 'it leaves %s' % (seat_spirits(subject),))
        number, defect = drawn_standing(texts[seat + '_desc'], subject)
        record['%s seat draws %d' % (label, score)] = (
            defect if defect else None if number == score else 'it draws %r' % (number,))

    # A genuine zero must read as zero, and a variable that does not exist must not read as
    # one. Country.value() answers 0.0 for an absent name, which is exactly the trap here.
    collapse = decide(script, (18, 77, 20), governors=3)
    record['an absent standing is not read as zero'] = (
        None if (collapse.value(SCORE_VARIABLE) == 0.0
                 and SCORE_VARIABLE not in collapse.variables
                 and drawn_standing(popup, collapse)[1] is not None)
        else 'absence was read as the number zero')

    # The first eligible tick: it freezes the standing, queues the popup for the tier it
    # froze, and the seat that tick added already carries that number.
    ticked = tick_state(script)
    queued = [event for event, _days in ticked.queued if event == 'rch_campaign.5']
    record['the tick freezes the standing before it queues the popup'] = (
        None if SCORE_VARIABLE in ticked.variables and queued == ['rch_campaign.5']
        else 'it queued %r with the score present: %r'
             % (queued, SCORE_VARIABLE in ticked.variables))
    tier = int(ticked.value('rch_succession_final_tier'))
    option = {0: 'rch_campaign.5.a', 1: 'rch_campaign.5.c',
              2: 'rch_campaign.5.b', 3: 'rch_campaign.5.e'}[tier]
    record['the frozen tier owns the one visible popup option'] = (
        None if (' ' + option + ':') in read(LOC_EVENTS)
        else 'the option for tier %d is missing' % tier)
    number, defect = drawn_standing(popup, ticked)
    frozen = ticked.value(SCORE_VARIABLE)
    record['the ticked popup draws the score the tick froze'] = (
        defect if defect else None if number == frozen
        else 'it draws %r not %g' % (number, frozen))

    # A deferred or absent popup, a refresh, a repeat tick and a changed live dial all leave
    # the frozen standing, and the number the seat shows, exactly as they were.
    held = decide(script, (62, 37, 38), settled=4, throne=True)
    script.run('rch_succession_resolve', held)
    seat_text = texts['rch_succession_constitutional_desc']
    before = drawn_standing(seat_text, held)
    held.variables['rch_legitimacy'] = 2.0
    held.variables['rch_succession_score'] = 5.0
    held.set_flag('rch_campaign_active')
    script.run('rch_refresh_mechanics', held)
    script.run('rch_campaign_tick', held)
    after = drawn_standing(seat_text, held)
    record['a refresh, a repeat tick and changed dials leave the standing fixed'] = (
        None if before == after == (88, None) else 'it drew %r then %r' % (before, after))

    # A post-crisis start resolves silently, so the seat is the only thing that can show it.
    silent = Country(variables=dict(OPENING), date='1918.3.21')
    script.run('rch_succession_endow', silent)
    garrison = texts['rch_succession_garrison_desc']
    number, defect = drawn_standing(garrison, silent)
    record['a silent 1918 start prints the standing it froze'] = (
        defect if defect else None
        if number == int(silent.value(SCORE_VARIABLE)) and not silent.queued
        else 'it drew %r and queued %r' % (number, silent.queued))
    script.run('rch_succession_endow', silent)
    record['a repeated 1918 initialisation changes nothing'] = (
        None if drawn_standing(garrison, silent) == (number, None) and not silent.queued
        else 'the standing moved or a popup was queued')

    for label, dials, options, score, tier in (FIXTURES[5], FIXTURES[7]):
        sealed = decide(script, dials, dlc=(), **options)
        script.run('rch_succession_resolve', sealed)
        number, defect = drawn_standing(texts[TIER_SEAT[tier] + '_desc'], sealed)
        record['%s draws the same standing without the DLC' % label] = (
            defect if defect else None
            if number == score and sealed.bop is None
            else 'it drew %r with the panel %r' % (number, sealed.bop))
    return record


def score_readout_mutants():
    """Every readout, lifetime and phase claim must be load-bearing, not decorative."""
    print('score readout mutants')
    decisions_loc = read(LOC_DECISIONS)
    events_loc = read(LOC_EVENTS)
    popup = loc_value(events_loc, 'rch_campaign.5.d')
    tail = '\\n\\n' + SCORE_LABEL + ': ' + SCORE_TOKEN + ' ' + SCORE_RANGE

    trimmed = popup.replace(tail, '')
    check(trimmed != popup, 'the popup-without-readout mutant edits the shipped popup')
    check(any('does not print the frozen score' in defect
              for defect in score_readout_defects(trimmed)),
          'mutant without the score interpolation in the popup is caught')

    rank = loc_value(decisions_loc, 'rch_succession_garrison_desc')
    bare = rank.replace(tail, '')
    check(bare != rank, 'the one-seat mutant edits the shipped garrison text')
    check(any('does not print the frozen score' in defect
              for defect in score_readout_defects(bare)),
          'mutant without the readout on one seat is caught on that seat')
    check(not score_readout_defects(
        loc_value(decisions_loc, 'rch_succession_constitutional_desc')),
        'the same mutant leaves the other seats passing')

    live = popup.replace(SCORE_TOKEN, '[?rch_succession_score|0]')
    check(live != popup, 'the live-score mutant edits the shipped popup')
    check(any('live scratch' in defect for defect in score_readout_defects(live)),
          'mutant that prints the live scratch score instead of the frozen one is caught')

    for label, broken in (
            ('a misspelt variable',
             popup.replace(SCORE_TOKEN, '[?rch_succession_final_scor|0]')),
            ('a missing question mark',
             popup.replace(SCORE_TOKEN, '[rch_succession_final_score|0]')),
            ('a removed integer format',
             popup.replace(SCORE_TOKEN, '[?rch_succession_final_score]'))):
        check(broken != popup, 'the %s mutant edits the shipped popup' % label)
        check(score_readout_defects(broken), 'mutant with %s is caught' % label)

    leaked = (loc_value(decisions_loc, 'rch_beiyang_order_category_desc') + ' '
              + SCORE_LABEL + ': ' + SCORE_TOKEN + ' ' + SCORE_RANGE)
    check(category_lifetime_defects(leaked),
          'mutant that puts the standing in the pre-resolution category is caught by lifetime')

    stale = popup.replace('The seat was judged when the presidency fell',
                          'The judgement had been fixed on 12 December 1915')
    check(stale != popup, 'the stale-phase mutant edits the shipped popup')
    check(phase_claim_defects(stale),
          'mutant that restores the false December judgement claim is caught')

    effects = plain(read(EFFECTS))
    unassigned = effects.replace(
        '\t\tset_variable = { rch_succession_final_score = var:rch_succession_score }\n', '', 1)
    check(unassigned != effects, 'the unassigned-score mutant edits the shipped settle')
    defects = record_defects(score_readout_record(Script(effects_text=unassigned)))
    check(any('which the country does not hold' in defect for defect in defects),
          'mutant without the frozen-score assignment is caught as an unset variable')
    check(any('military collapse' in defect for defect in defects),
          'the unset variable is caught on a genuine zero score, not read as zero')


def handler_models():
    """Probe every effect handler the suite books a claim on, in both directions."""
    print('effect handler models')
    script = Script()
    subject = Country(variables={'probe': 10.0, 'other': 7.0})

    def booking(snippet):
        script.effect(parse_text(snippet), subject)

    booking('set_variable = { probe = 4 }')
    check(subject.value('probe') == 4.0, 'set_variable assigns the shorthand value')
    booking('add_to_variable = { probe = 3 }')
    check(subject.value('probe') == 7.0, 'add_to_variable adds')
    booking('subtract_from_variable = { probe = 2 }')
    check(subject.value('probe') == 5.0, 'subtract_from_variable subtracts')
    booking('multiply_variable = { probe = 4 }')
    check(subject.value('probe') == 20.0, 'multiply_variable multiplies')
    booking('divide_variable = { probe = 5 }')
    check(subject.value('probe') == 4.0, 'divide_variable divides')
    check(subject.value('other') == 7.0, 'no arithmetic handler touches another variable')
    booking('clamp_variable = { var = probe min = 0 max = 3 }')
    check(subject.value('probe') == 3.0, 'clamp_variable clamps to the ceiling it is given')
    subject.variables['probe'] = 2.5
    booking('round_variable = probe')
    check(subject.value('probe') == 3.0, 'round_variable rounds a half up')

    subject.age('probe_flag', '1916.1.1')
    booking('set_country_flag = probe_flag')
    check(subject.flag_dates['probe_flag'] == '1916.1.1',
          'set_country_flag leaves an existing flag date alone')
    booking('clr_country_flag = probe_flag')
    check('probe_flag' not in subject.flags and 'probe_flag' not in subject.flag_dates,
          'clr_country_flag clears the flag and its date')
    booking('set_country_flag = probe_flag')
    check(subject.flag_dates['probe_flag'] == subject.date,
          'set_country_flag dates a fresh flag at the current date')

    subject.ideas.update({'rch_succession_dissolved', 'probe_keep'})
    booking('remove_ideas = { rch_succession_dissolved }')
    check(subject.ideas == {'probe_keep'},
          'remove_ideas removes the named id from a block and nothing else')
    booking('add_ideas = { probe_one probe_two }')
    check(subject.ideas == {'probe_keep', 'probe_one', 'probe_two'},
          'add_ideas adds bare identifiers from a block')
    booking('add_ideas = probe_three')
    check('probe_three' in subject.ideas, 'add_ideas adds a single id')

    booking('set_power_balance = { id = PROBE set_value = 0.0 }')
    check(subject.bop == 'PROBE' and subject.bop_writes[-1] == ('set', 0.0),
          'set_power_balance creates the panel at the value it is given')
    booking('add_power_balance_value = { id = PROBE value = 0.5 }')
    check(subject.bop_writes[-1] == ('add', 0.5),
          'add_power_balance_value books the offset it is given')

    booking('country_event = { id = probe.1 days = 3 }')
    check(subject.queued[-1] == ('probe.1', 3.0),
          'country_event books the event id and its delay')
    booking('load_focus_tree = { tree = probe_tree keep_completed = yes }')
    check(subject.focus_tree == {'probe_tree'}, 'load_focus_tree records the tree')
    booking('mark_focus_tree_layout_dirty = yes')

    stability, power, experience = subject.stability, subject.political_power, subject.army_xp
    booking('add_stability = 0.05')
    booking('add_political_power = 10')
    booking('army_experience = -25')
    check(subject.stability == stability + 0.05, 'add_stability books the change')
    check(subject.political_power == power + 10, 'add_political_power books the change')
    check(subject.army_xp == experience - 25, 'army_experience books the change')


def handler_mutants():
    """One source mutant per effect handler the suite books a claim on.

    A handler that stops booking its command leaves the claim it guards unguarded, so each
    mutant must raise a named defect through the same record the shipped source passes.
    """
    print('handler mutants')
    effects = plain(read(EFFECTS))
    constants = plain(read(CONSTANTS))

    def caught(handler, claim, script, record):
        defects = record_defects(record(script))
        check(any(claim in defect for defect in defects),
              'mutant without the %s is caught by "%s"' % (handler, claim))

    def cut(handler, fragment):
        mutated = effects.replace(fragment, '', 1)
        check(mutated != effects, 'the %s mutant edits the shipped effects' % handler)
        return mutated

    caught('set_variable', 'the frozen score is 88',
           Script(effects_text=cut('set_variable',
                                   '\tset_variable = { rch_succession_final_score = var:rch_succession_score }\n')), spirit_record)
    caught('set_variable', 'a collapsed succession freezes tier 3',
           Script(effects_text=cut('set_variable',
                                   '\tset_variable = { rch_succession_final_tier = var:rch_succession_tier }\n')), spirit_record)
    caught('add_to_variable', 'full civil scores 88',
           Script(effects_text=cut('add_to_variable',
                                   '\tadd_to_variable = { var = rch_succession_base value = constant:rch_story.legitimacy_cap }\n')), score_record)
    caught('subtract_from_variable', 'full civil scores 88',
           Script(effects_text=cut('subtract_from_variable',
                                   '\tsubtract_from_variable = { var = rch_succession_base value = var:rch_military_influence }\n')), score_record)
    caught('multiply_variable', 'full civil scores 88',
           Script(effects_text=cut('multiply_variable',
                                   '\tmultiply_variable = { var = rch_succession_gate_term value = constant:rch_story.succession_gate_weight }\n')), score_record)
    caught('divide_variable', 'full civil scores 88',
           Script(effects_text=cut('divide_variable',
                                   '\tdivide_variable = { var = rch_succession_base value = constant:rch_story.succession_divisor }\n')), score_record)
    caught('round_variable', 'emergency 45/37/34 scores 42',
           Script(effects_text=cut('round_variable', '\tround_variable = rch_succession_base\n')), score_record)
    caught('clamp_variable', 'military collapse scores 0',
           Script(effects_text=cut('clamp_variable',
                                   '\tclamp_variable = { var = rch_succession_score min = constant:rch_story.succession_score_floor max = constant:rch_story.succession_score_cap }\n')), score_record)
    caught('set_country_flag', 'the settlement leaves exactly one seat spirit',
           Script(effects_text=cut('set_country_flag', '\t\tset_country_flag = rch_line_unified\n')), spirit_record)

    no_clear = re.sub(r'\tclr_country_flag = rch_chapter_\w+\n', '', effects)
    check(no_clear != effects, 'the clr_country_flag mutant edits the shipped openers')
    caught('clr_country_flag', 'leaves only rch_chapter_one',
           Script(effects_text=no_clear), chapter_record)

    caught('add_ideas', 'the settlement leaves exactly one seat spirit',
           Script(effects_text=cut('add_ideas', '\t\tadd_ideas = rch_succession_constitutional\n')), spirit_record)
    caught('remove_ideas', 'the seat spirit replaces an earlier seat',
           Script(effects_text=cut('remove_ideas',
                                   '\tremove_ideas = {\n\t\trch_succession_constitutional rch_succession_contested rch_succession_garrison rch_succession_dissolved\n\t}\n')), spirit_record)
    caught('set_power_balance', 'the panel is created once',
           Script(effects_text=cut('set_power_balance',
                                   '\t\tset_power_balance = { id = RCH_beiyang_order set_value = 0.0 }\n')), display_record)

    no_publish = effects.replace(
        '\t\t\t\t\tlimit = { check_variable = { var = rch_bop_band_new value = 3 compare = equals } }\n'
        '\t\t\t\t\tadd_power_balance_value = { id = RCH_beiyang_order value = 0.25 }\n',
        '\t\t\t\t\tlimit = { check_variable = { var = rch_bop_band_new value = 3 compare = equals } }\n',
        1)
    check(no_publish != effects, 'the add_power_balance_value mutant edits the shipped display')
    caught('add_power_balance_value', 'military 65 publishes the upper band',
           Script(effects_text=no_publish), display_record)

    caught('country_event', 'three same-day resolves queue one popup',
           Script(effects_text=cut('country_event',
                                   '\t\tcountry_event = { id = rch_campaign.5 days = 1 }\n')), spirit_record)

    no_tree = re.sub(r'\tload_focus_tree = \{ tree = \w+ keep_completed = yes \}\n', '', effects)
    check(no_tree != effects, 'the load_focus_tree mutant edits the shipped openers')
    caught('load_focus_tree', 'loads rch_republic',
           Script(effects_text=no_tree), chapter_record)

    caught('add_stability', 'the constitution bargain gains stability',
           Script(effects_text=cut('add_stability',
                                   '\tadd_stability = constant:rch_story.pressure_stability_gain\n')), cost_record)

    flipped = constants.replace('pressure_stability_cost = -0.02', 'pressure_stability_cost = 0.02')
    check(flipped != constants, 'the stability cost mutant edits the shipped constant')
    caught('the stability cost sign', 'the treasury bargain costs stability',
           Script(constants_text=flipped), cost_record)


def guard_mutants():
    """Each anti-exploit guard must fail on the source defect it exists for."""
    print('anti-exploit mutants')
    effects = plain(read(EFFECTS))
    decisions = plain(read(DECISIONS))
    constants = plain(read(CONSTANTS))
    cooldown = int(Script().constants['pressure_cooldown_days'])

    released = decisions.replace('days > %d }' % cooldown, 'days > 0 }')
    check(released != decisions, 'the lock mutant edits the shipped window')
    check(availability_defects(Script(), released, cooldown),
          'mutant with every family lock released at day 0 is caught')

    no_gate_clear = effects.replace(
        '\tclr_country_flag = rch_gate_constitution\n\tset_country_flag = rch_gate_constitution\n',
        '\tset_country_flag = rch_gate_constitution\n', 1)
    check(no_gate_clear != effects, 'the tenure mutant edits the shipped effect')
    check(tenure_defects(Script(effects_text=no_gate_clear)),
          'mutant without the gate clear is caught')

    no_lock_clear = re.sub(r'\tclr_country_flag = rch_press_lock_\w+\n', '', effects)
    check(no_lock_clear != effects, 'the lock-clear mutant edits the shipped effects')
    check(tenure_defects(Script(effects_text=no_lock_clear)),
          'mutant without a family lock clear is caught')

    drifted = constants.replace('pressure_cooldown_days = %d' % cooldown,
                                'pressure_cooldown_days = 200')
    check(drifted != constants, 'the cooldown mutant edits the shipped constant')
    check(mirror_defects(Script(constants_text=drifted)),
          'mutant cooldown 180 to 200 is caught by the literal mirror')

    capital = constants.replace('succession_capital_state = 608', 'succession_capital_state = 611')
    check(capital != constants, 'the capital mutant edits the shipped constant')
    check(mirror_defects(Script(constants_text=capital)),
          'mutant capital 608 to 611 is caught by the literal mirror')

    quiet = without_daily_refresh(effects)
    check(quiet != effects, 'the daily refresh mutant edits the shipped tick')
    check(quiet_tick(Script(effects_text=quiet)).bop is None,
          'mutant without the daily refresh leaves the display unset on a quiet day')


def without_daily_refresh(text):
    """The daily refresh call, removed from the tick, without touching the other caller."""
    kept = []
    drop = False
    for line in text.splitlines(keepends=True):
        if drop and 'rch_beiyang_refresh' in line:
            drop = False
            continue
        kept.append(line)
        if line.lstrip().startswith('# The display is republished daily'):
            drop = True
    return ''.join(kept)


def baseline_control():
    """Run this same suite against the pre-implementation source and require it to fail."""
    print('baseline control')
    tree = Path(tempfile.mkdtemp(prefix='rch_head_'))
    inputs = (CONSTANTS, TRIGGERS, EFFECTS, DECISIONS, CATEGORIES, EVENTS, IDEAS, BOP,
              LOC_DECISIONS, LOC_EVENTS)
    try:
        for path in inputs:
            shown = subprocess.run(['git', 'show', 'HEAD:' + path], cwd=str(ROOT),
                                   capture_output=True)
            target = tree / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(shown.stdout if shown.returncode == 0 else b'')
        environment = dict(os.environ, RCH_TEST_ROOT=str(tree))
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--no-baseline'],
                                cwd=str(ROOT), capture_output=True, text=True, env=environment)
        check(result.returncode != 0,
              'the pre-implementation source fails this suite (exit %d)' % result.returncode)
        check('FAIL' in result.stdout,
              'the baseline run reports a named failing check rather than crashing silently')
        if VERBOSE:
            print('\n'.join(result.stdout.splitlines()[-12:]))
    finally:
        shutil.rmtree(tree, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
