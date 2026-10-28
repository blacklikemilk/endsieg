"""The settlement of 1945: the two decisions, the two events and the chapter-correct AI plan.

Spain's 1939-45 Nationalist chapter ends with a question the era is actually about: who inherits
the movement, and what the regime signs with the powers that won the war. This test reads the
files the game loads and proves that

    1. `SPR_the_succession_question` and `SPR_the_pact_of_1945` sit inside the live
       `SPR_nationalist_factions` decision block with their costs, their gates and the event each
       one fires, and that the only player-visible requirement lines are localised tooltips;
    2. `spain_campaign.62` offers exactly three options, each reachable only under the faction
       that answers, and that no option can leave the country with two regime spirits because no
       option grants a spirit itself and the shared arbitration strips all four first;
    3. `spain_campaign.63` signs the settlement through the same arbitration and moves allied
       leverage far enough to open or close the Marshall aid and the United Nations seat that
       already existed;
    4. every flag the slice writes is read somewhere else in the slice, and the one flag that has
       no writer (`spain_monarchy_survived`) is still only a declared forward edge;
    5. the AI plan for the Nationalist post-war chapter names only focuses of the tree that
       chapter loads, and the Republican plan keeps its `SPR4_*` list under the flag of the
       chapter that actually loads that tree;
    6. every localisation key the new blocks reference exists, every key the new localisation
       section defines is referenced, and the text carries no formatting glyphs;
    7. nothing outside the slice moved: the four faction decisions and events .60/.61/.70/.71 are
       unchanged against the pinned pre-slice commit, and the two payoff decisions changed only
       inside `available`.

Negative controls, each of which must FAIL: the pre-change tree at the pinned pre-slice commit
`2b15aad63`, an option left without its faction trigger, the pact with `fire_only_once` removed,
the succession with `fire_only_once` removed, the pact's 1945 date gate widened to 1944, a pact
icon the engine cannot resolve, the Crown answer reverted to pushing one fixed royal house, a
deleted settlement tooltip key, and the two AI plans with their chapter flags swapped.

Run from the repository root:

    python .tools/tests/test_spain_1945_settlement.py            # exit 0 = pass
    python .tools/tests/test_spain_1945_settlement.py --detail    # print every check

This is a source simulation. It proves what the script says, not what the engine does: no
decision was clicked, no event fired, no tooltip drawn and the game was never launched.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_spain_cortes_recount as base  # noqa: E402  (Report)
import test_spain_restoration_loyalty as harness  # noqa: E402  (tokeniser, parser, git reader)

Unsupported = harness.Unsupported
Report = base.Report

DECISIONS = 'common/decisions/spain_campaign.txt'
EVENTS = 'events/spain_campaign.txt'
PLANS = 'common/ai_strategy_plans/SPR_chapter_plans.txt'
LOC = 'localisation/english/spain_campaign_l_english.yml'
CONSTANTS = 'common/script_constants/spain_campaign.txt'
NATIONAL_TREE = 'common/national_focus/spain.txt'
REPUBLIC_TREE = 'common/national_focus/spain_republic_postwar.txt'
EFFECTS = 'common/scripted_effects/spain_campaign_effects.txt'
IDEAS = 'common/ideas/spain_campaign.txt'

TEXT_FILES = (DECISIONS, EVENTS, PLANS, LOC)
CONSTANT_FILE = CONSTANTS
READ_ONLY = (NATIONAL_TREE, REPUBLIC_TREE, EFFECTS, IDEAS)
BASELINE = '2b15aad63f224711ece7f44cd1103f1f5ecbb8bf'

# --- the ids this slice owns -------------------------------------------------------------
CATEGORY = 'SPR_nationalist_factions'
SUCCESSION = 'SPR_the_succession_question'
PACT = 'SPR_the_pact_of_1945'
SUCCESSION_EVENT = 'spain_campaign.62'
SETTLEMENT_EVENT = 'spain_campaign.63'
MARSHALL = 'SPR_accept_the_marshall_aid'
UN_SEAT = 'SPR_take_the_un_seat'

# --- the flags this slice writes and reads -----------------------------------------------
SETTLED = 'spain_succession_settled'
OUTCOME_FLAGS = ('spain_succession_falangist', 'spain_succession_military',
                 'spain_succession_monarchist')
SIGNED = 'spain_settled_1945'
RECALLED = 'spain_monarchy_recalled'
FORWARD_EDGE = 'spain_monarchy_survived'
WRITTEN_FLAGS = (SETTLED, SIGNED, RECALLED) + OUTCOME_FLAGS

# --- the factions and the triggers the options key on -------------------------------------
FACTION_TRIGGERS = {
    'spain_falange_leads': 'spain_faction_falange_leads',
    'spain_army_leads': 'spain_faction_army_leads',
    'spain_monarchists_lead': 'spain_faction_monarchists_lead',
    'spain_carlists_lead': 'spain_faction_carlists_lead',
}
LEVERAGE_HIGH = 'spain_allied_leverage_high'
LOYALTY_LOW = 'spain_loyalty_low'
LOYALTY_HIGH = 'spain_loyalty_high'
AXIS_HIGH = 'spain_axis_leverage_high'

# Facts a scenario may assert. Anything else in a trigger is unmodelled and raises.
MODELED_FACTS = frozenset({LEVERAGE_HIGH, LOYALTY_LOW, LOYALTY_HIGH, AXIS_HIGH,
                           'is_historical_focus_on'})
FACTS = frozenset(FACTION_TRIGGERS) | MODELED_FACTS

# The influence a faction has to hold before the leadership refresh raises its flag, and the flag
# the refresh writes. Filled from the source in `load_world`; a change there changes the fixtures.
LEAD_RULES = {}

REGIME_IDEAS = ('spain_falangist_state', 'spain_carlist_state', 'spain_monarchist_state',
                'spain_military_directorate')
RESOLVER = 'spain_faction_resolve_regime'

# The decisions and events that must not move at all.
UNTOUCHED_DECISIONS = ('SPR_back_the_falange', 'SPR_back_the_carlists',
                       'SPR_back_the_monarchists', 'SPR_back_the_army')
UNTOUCHED_EVENTS = ('spain_campaign.60', 'spain_campaign.61', 'spain_campaign.70',
                    'spain_campaign.71')

# The two plans and the tree each one may name.
NATIONAL_PLAN = 'SPR_nationalist_postwar_plan'
REPUBLICAN_PLAN = 'SPR_postwar_plan'
NATIONALCHAPTER_FLAG = 'spain_chapter_postwar'
REPUBLICAN_CHAPTER_FLAG = 'spain_chapter_republican_postwar'

# Scenarios: name -> facts asserted true.
SUCCESSION_SCENARIOS = {
    'falange leads': {'spain_falange_leads'},
    'army leads': {'spain_army_leads'},
    'monarchists lead': {'spain_monarchists_lead'},
    'carlists lead': {'spain_carlists_lead'},
    'no faction leads': set(),
}
SETTLEMENT_SCENARIOS = {
    'ally leverage, succession answered': {LEVERAGE_HIGH, SETTLED},
    'ally leverage, falangist answer': {LEVERAGE_HIGH, SETTLED, 'spain_succession_falangist'},
    'ally leverage, military answer': {LEVERAGE_HIGH, SETTLED, 'spain_succession_military'},
    'crown answer, no leverage': {SETTLED, 'spain_succession_monarchist'},
    'no leverage, army answer': {SETTLED, 'spain_succession_military'},
    'nothing settled yet': set(),
}

LOC_SECTION = 'the settlement of 1945'

# Where the installed game keeps its interface sprites, so a decision icon can be proven to
# resolve instead of assumed. The mod's own folder is scanned as well.
VANILLA_GAME_DIRS = [
    os.environ.get('HOI4_GAME_DIR', ''),
    r'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV',
    r'C:/Program Files/Paradox Interactive/Hearts of Iron IV',
]
_SPRITES = None


def registered_decision_sprites():
    """Every `GFX_decision_*` sprite the game and the mod define, or a loud failure."""
    global _SPRITES
    if _SPRITES is not None:
        return _SPRITES
    bases = [ROOT] + [Path(path) for path in VANILLA_GAME_DIRS if path]
    found = set()
    scanned = []
    for index, base in enumerate(bases):
        for folder in [base / 'interface'] + ([base / 'dlc'] if index else []):
            if not folder.is_dir():
                continue
            scanned.append(str(folder))
            for path in folder.rglob('*.gfx'):
                text = path.read_text(encoding='utf-8-sig', errors='replace')
                found.update(re.findall(r'name\s*=\s*"(GFX_decision_[A-Za-z0-9_]+)"', text))
    if not scanned:
        raise Unsupported('no interface folder found under %r'
                          % ([str(base) for base in bases],))
    _SPRITES = found
    return found


# ---------------------------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------------------------

def load_world():
    world = {'texts': {path: harness.read_text(path) for path in TEXT_FILES},
             'read': {path: harness.read_text(path) for path in READ_ONLY}}
    world['texts'][CONSTANTS] = harness.read_text(CONSTANTS)
    world['constants'] = harness.parse_constants(world['texts'][CONSTANTS])
    WORLD_CONSTANTS.update(world['constants'])
    LEAD_RULES.update(lead_thresholds(world))
    return world


def with_text(world, path, text):
    texts = dict(world['texts'])
    texts[path] = text
    return {'texts': texts, 'read': world['read'], 'constants': world['constants']}


def with_read(world, path, text):
    read = dict(world['read'])
    read[path] = text
    return {'texts': world['texts'], 'read': read, 'constants': world['constants']}


def parse(text):
    entries, _ = harness.parse_block(harness.tokenize(text), 0)
    return entries


def walk(entries, path=()):
    for key, value, line in entries:
        yield key, value, line, path
        if value[0] == 'block':
            yield from walk(value[1], path + (key,))


def blocks_named(entries, name):
    return [value[1] for key, value, line, _ in walk(entries) if key == name and value[0] == 'block']


def block_named(entries, name):
    found = blocks_named(entries, name)
    if len(found) != 1:
        raise Unsupported('%d blocks named %s, expected exactly one' % (len(found), name))
    return found[0]


def scalars(entries, key):
    return [value[1] for entry_key, value, line in entries
            if entry_key == key and value[0] == 'scalar']


def bare_words(entries, key):
    """The bare-word list of a block, as focus plans write `ai_national_focuses = { A B }`."""
    body = optional_block(entries, key)
    if body is None:
        raise Unsupported('no %s list' % key)
    words = [entry_key for entry_key, value, line in body if value[0] == 'bare']
    if not words:
        raise Unsupported('%s parsed to no bare words' % key)
    return words


def optional_block(entries, key):
    for entry_key, value, line in entries:
        if entry_key == key and value[0] == 'block':
            return value[1]
    return None


def required_block(entries, key, where):
    found = optional_block(entries, key)
    if found is None:
        raise Unsupported('%s has no %s block' % (where, key))
    return found


def events(text):
    """event id -> its entries, for every country_event in the file."""
    found = {}
    for key, value, line, _ in walk(parse(text)):
        if key != 'country_event' or value[0] != 'block':
            continue
        try:
            event_id = harness.scalar(value[1], 'id')
        except Unsupported:
            raise Unsupported('a country_event at line %d has no id' % line)
        found[event_id] = value[1]
    return found


def options(event_entries, event_id):
    return [value[1] for key, value, line in event_entries if key == 'option' and value[0] == 'block']


def option_names(event_entries):
    return [harness.scalar(option, 'name') for option in options(event_entries, '')]


def decision_block(text, name):
    """The decision's own block, wherever it sits in the file."""
    found = blocks_named(parse(text), name)
    if len(found) != 1:
        raise Unsupported('%d blocks named %s, expected exactly one' % (len(found), name))
    return found[0]


def canonical(entries):
    """Entries without line numbers, for comparing a block against its committed version."""
    out = []
    for key, value, line in entries:
        if value[0] == 'block':
            out.append((key, 'block', canonical(value[1])))
        else:
            out.append((key, value[0], value[1] if len(value) > 1 else None))
    return out


# ---------------------------------------------------------------------------------------------
# Trigger model
# ---------------------------------------------------------------------------------------------

def holds(entries, facts):
    """Evaluate a modelled trigger block against a fact set or a full execution state."""
    return trigger_holds(entries, as_state(facts))


def reachable(option, facts):
    trigger = optional_block(option, 'trigger')
    if trigger is None:
        return True
    return holds(trigger, facts)


def reachable_names(option_list, facts):
    return [harness.scalar(option, 'name') for option in option_list if reachable(option, facts)]


# ---------------------------------------------------------------------------------------------
# Arithmetic helpers
# ---------------------------------------------------------------------------------------------

def variable_writes(entries, variable):
    """(command, signed amount) for every write of one variable in a block."""
    writes = []
    for key, value, line, _ in walk(entries):
        if key not in ('add_to_variable', 'subtract_from_variable', 'set_variable'):
            continue
        if value[0] != 'block':
            raise Unsupported('%s is not a block at line %d' % (key, line))
        if harness.optional_scalar(value[1], 'var') != variable:
            continue
        token = harness.optional_scalar(value[1], 'value')
        if key == 'set_variable':
            writes.append((key, 0.0))
            continue
        amount = harness.amount_of(token, WORLD_CONSTANTS)
        writes.append((key, amount if key == 'add_to_variable' else -amount))
    return writes


WORLD_CONSTANTS = {}


def leverage_delta(option):
    return sum(amount for command, amount in variable_writes(option, 'spain_allied_leverage'))


def lead_thresholds(world):
    """(trigger name, variable, threshold) for the four leadership flags, read from the refresh.

    The thresholds are not restated here: they are parsed out of `spain_refresh_faction_leadership`,
    so a change in the script changes what "leads" means to this test as well.
    """
    body = block_named(parse(world['read'][EFFECTS]), 'spain_refresh_faction_leadership')
    rules = {}
    for key, value, line, path in walk(body):
        if key != 'if' or value[0] != 'block':
            continue
        limit = optional_block(value[1], 'limit')
        if limit is None:
            continue
        flags = [v[1] for k, v, l in value[1] if k == 'set_country_flag' and v[0] == 'scalar']
        flags = [flag for flag in flags if flag in FACTION_TRIGGERS.values()]
        if len(flags) != 1:
            continue
        checks = [entry for entry in limit if entry[0] == 'check_variable']
        if len(checks) != 1 or checks[0][1][0] != 'block':
            raise Unsupported('the lead rule for %s is not one check_variable' % flags[0])
        inner = checks[0][1][1]
        variable = harness.optional_scalar(inner, 'var')
        token = harness.optional_scalar(inner, 'value')
        compare = harness.optional_scalar(inner, 'compare')
        if variable is None or token is None or compare != 'greater_than_or_equals':
            raise Unsupported('the lead rule for %s is not a >= threshold' % flags[0])
        rules[flags[0]] = (variable, literal(token))
    if len(rules) != len(FACTION_TRIGGERS):
        raise Unsupported('the leadership refresh defines %d lead flags, expected %d'
                          % (len(rules), len(FACTION_TRIGGERS)))
    return rules


def literal(token):
    """A number or a constant, with no state involved."""
    if token.startswith('constant:'):
        return constant_of(token)
    try:
        return float(token)
    except ValueError:
        raise Unsupported('%r is not a number or a constant' % (token,))


def coherent_facts(values):
    """The leadership flags the refresh would write for these influence values."""
    facts = set()
    for trigger, flag in FACTION_TRIGGERS.items():
        variable, threshold = LEAD_RULES[flag]
        if values.get(variable, 0.0) >= threshold:
            facts.add(trigger)
    return facts


# ---------------------------------------------------------------------------------------------
# Executing the shipped effects
#
# The settlement is a numeric invariant, so this test does not restate it. It runs the option body
# and the shared arbitration as the files the game loads write them, then asks whether the answer
# that was chosen is the regime that came out.
# ---------------------------------------------------------------------------------------------

COMPARISONS = {
    '<': lambda left, right: left < right,
    '>': lambda left, right: left > right,
    '=': lambda left, right: left == right,
}

COMPARE_TYPES = {
    'equals': lambda left, right: left == right,
    'not_equals': lambda left, right: left != right,
    'less_than': lambda left, right: left < right,
    'less_than_or_equals': lambda left, right: left <= right,
    'greater_than': lambda left, right: left > right,
    'greater_than_or_equals': lambda left, right: left >= right,
}

# Scripted effects the settlement runs. Their bodies are read from the effects file, so a change
# there is part of the behaviour under test even though this test may not edit that file.
EXECUTED_EFFECTS = (RESOLVER, 'spain_loyalty_gain_small', 'spain_clamp_campaign_variables')

VARIABLE_OPERATORS = {
    'set_variable': ('variables', 'set'),
    'add_to_variable': ('variables', 'add'),
    'subtract_from_variable': ('variables', 'subtract'),
    'set_temp_variable': ('temps', 'set'),
    'add_to_temp_variable': ('temps', 'add'),
    'subtract_from_temp_variable': ('temps', 'subtract'),
}

# Entries that carry data for the engine rather than an executed effect.
NOT_EXECUTED = frozenset(('name', 'trigger', 'ai_chance', 'custom_effect_tooltip',
                          'custom_trigger_tooltip', 'limit', 'log'))


def constant_of(token):
    if not token.startswith('constant:'):
        raise Unsupported('%r is not a constant reference' % (token,))
    key = token.split(':', 1)[1]
    if key not in WORLD_CONSTANTS:
        raise Unsupported('constant %s is not in the constants file' % key)
    return WORLD_CONSTANTS[key]


def number_of(token, state):
    token = token.strip()
    if token.startswith('constant:'):
        return constant_of(token)
    if token.startswith('var:'):
        token = token[4:]
    try:
        return float(token)
    except ValueError:
        pass
    if token in state['temps']:
        return state['temps'][token]
    if token in state['variables']:
        return state['variables'][token]
    if re.fullmatch(r'spain_[a-z0-9_]+', token):
        # The engine reads an unset variable as zero, and the campaign owns these names.
        return 0.0
    raise Unsupported('%r is neither a number, a constant nor a campaign variable' % (token,))


def trigger_holds(entries, state):
    return all(trigger_entry_holds(key, value, line, state) for key, value, line in entries)


def trigger_entry_holds(key, value, line, state):
    if key == 'NOT':
        return not trigger_holds(value[1], state)
    if key == 'AND':
        return trigger_holds(value[1], state)
    if key == 'OR':
        return any(trigger_holds([entry], state) for entry in value[1])
    if key == 'check_variable':
        return check_variable_holds(value[1], state, line)
    if key == 'has_idea':
        return value[1] in state['ideas']
    if key == 'has_country_flag':
        return value[1] in state['flags']
    if key in FACTION_TRIGGERS:
        return FACTION_TRIGGERS[key] in state['flags'] or key in state['flags']
    if key in MODELED_FACTS:
        return key in state['flags']
    raise Unsupported('%s at line %d is not a trigger this test executes' % (key, line))


def check_variable_holds(entries, state, line=0):
    if len(entries) == 1:
        key, value, entry_line = entries[0]
        if value[0] == 'compare':
            kind, (operator, right) = value
            if operator not in COMPARISONS:
                raise Unsupported('comparison %r at line %d' % (operator, entry_line))
            return COMPARISONS[operator](number_of(key, state), number_of(right, state))
        if value[0] == 'scalar':
            # `check_variable = { name = value }` arrives as an ordinary assignment.
            return number_of(key, state) == number_of(value[1], state)
    name = harness.optional_scalar(entries, 'var')
    token = harness.optional_scalar(entries, 'value')
    compare = harness.optional_scalar(entries, 'compare') or 'greater_than_or_equals'
    if name is None or token is None:
        raise Unsupported('check_variable at line %d is not a form this test executes' % line)
    if compare not in COMPARE_TYPES:
        raise Unsupported('comparison %r at line %d' % (compare, line))
    return COMPARE_TYPES[compare](number_of(name, state), number_of(token, state))


def new_state(world, values, flags=(), ideas=()):
    bodies = {name: block_named(parse(world['read'][EFFECTS]), name) for name in EXECUTED_EFFECTS}
    return {'variables': dict(values), 'temps': {}, 'flags': set(flags), 'ideas': set(ideas),
            'bodies': bodies, 'stability': 0.0, 'war_support': 0.0}


def as_state(facts):
    """A plain fact set, for the trigger fixtures the older checks use."""
    if isinstance(facts, set):
        return {'variables': {}, 'temps': {}, 'flags': set(facts), 'ideas': set(), 'bodies': {}}
    return facts


def execute(entries, state):
    index = 0
    while index < len(entries):
        key, value, line = entries[index]
        if key == 'if':
            index = execute_chain(entries, index, state)
            continue
        if key in ('else', 'else_if'):
            raise Unsupported('a %s without an if at line %d' % (key, line))
        run_effect(key, value, line, state)
        index += 1


def execute_chain(entries, index, state):
    """An `if`, then its own `else_if`/`else` arms; a following `if` is a new chain."""
    key, value, line = entries[index]
    if value[0] != 'block':
        raise Unsupported('%s at line %d is not a block' % (key, line))
    limit = optional_block(value[1], 'limit')
    if limit is None:
        raise Unsupported('an if at line %d has no limit' % (line,))
    taken = trigger_holds(limit, state)
    if taken:
        execute([entry for entry in value[1] if entry[0] != 'limit'], state)
    index += 1
    while index < len(entries) and entries[index][0] in ('else_if', 'else'):
        key, value, line = entries[index]
        if value[0] != 'block':
            raise Unsupported('%s at line %d is not a block' % (key, line))
        if key == 'else':
            if not taken:
                execute([entry for entry in value[1] if entry[0] != 'limit'], state)
                taken = True
        else:
            arm = optional_block(value[1], 'limit')
            if arm is None:
                raise Unsupported('an else_if at line %d has no limit' % (line,))
            if not taken and trigger_holds(arm, state):
                execute([entry for entry in value[1] if entry[0] != 'limit'], state)
                taken = True
        index += 1
    return index


def run_effect(key, value, line, state):
    if key == 'set_country_flag':
        state['flags'].add(value[1])
        return
    if key == 'clr_country_flag':
        state['flags'].discard(value[1])
        return
    if key in VARIABLE_OPERATORS:
        store, how = VARIABLE_OPERATORS[key]
        name, token = variable_write(value[1], key, line)
        write(state[store], name, how, number_of(token, state))
        return
    if key == 'clamp_variable':
        name = harness.optional_scalar(value[1], 'var')
        low = harness.optional_scalar(value[1], 'min')
        high = harness.optional_scalar(value[1], 'max')
        if name is None or low is None or high is None:
            raise Unsupported('clamp_variable at line %d is not a form this test executes' % line)
        current = state['variables'].get(name, 0.0)
        state['variables'][name] = min(max(current, number_of(low, state)),
                                       number_of(high, state))
        return
    if key == 'add_stability':
        state['stability'] += number_of(value[1], state)
        return
    if key == 'add_war_support':
        state['war_support'] += number_of(value[1], state)
        return
    if key == 'add_ideas':
        state['ideas'].add(value[1])
        return
    if key == 'remove_ideas':
        state['ideas'].discard(value[1])
        return
    if key == 'hidden_effect':
        execute(value[1], state)
        return
    if key in EXECUTED_EFFECTS and value[0] == 'scalar' and value[1] == 'yes':
        execute(state['bodies'][key], state)
        return
    if key in NOT_EXECUTED:
        return
    raise Unsupported('%s at line %d is not an effect this test executes' % (key, line))


def variable_write(entries, key, line):
    """(variable, value token) for a variable operator in either of its two spellings."""
    name = harness.optional_scalar(entries, 'var')
    if name is not None:
        token = harness.optional_scalar(entries, 'value')
    elif len(entries) == 1 and entries[0][1][0] == 'scalar':
        name, token = entries[0][0], entries[0][1][1]
        if name.startswith('var:'):
            name = name[4:]
    else:
        raise Unsupported('%s at line %d is not a form this test executes' % (key, line))
    if token is None:
        raise Unsupported('%s at line %d has no value' % (key, line))
    return name, token


def write(store, name, how, amount):
    current = store.get(name, 0.0)
    if how == 'set':
        store[name] = amount
    elif how == 'add':
        store[name] = current + amount
    else:
        store[name] = current - amount


def run_arbitration(state):
    """Run the shared arbitration again on the balance as it now stands."""
    execute(state['bodies'][RESOLVER], state)


def clamp_campaign(state):
    execute(state['bodies']['spain_clamp_campaign_variables'], state)


def spirits_of(state):
    return sorted(state['ideas'] & set(REGIME_IDEAS))


def leader_of(state):
    return state['variables'].get('spain_regime_leader')


def option_effects(option):
    return [entry for entry in option if entry[0] not in ('name', 'trigger', 'ai_chance')]


def event_named(world, event_id):
    found = events(world['texts'][EVENTS])
    if event_id not in found:
        raise Unsupported('%s is not in the events file' % event_id)
    return found[event_id]


def option_named(world, event_id, name):
    found = [option for option in options(event_named(world, event_id), event_id)
             if harness.scalar(option, 'name') == name]
    if len(found) != 1:
        raise Unsupported('%d options named %s, expected exactly one' % (len(found), name))
    return found[0]


def expected_answer(values, answer):
    """(answer flag, spirit, leader) the chosen answer must produce."""
    if answer.endswith('.62.a'):
        return 'spain_succession_falangist', 'spain_falangist_state', 1
    if answer.endswith('.62.b'):
        return 'spain_succession_military', 'spain_military_directorate', 4
    carlist = values['spain_carlists'] > values['spain_monarchists']
    return ('spain_succession_monarchist',
            'spain_carlist_state' if carlist else 'spain_monarchist_state',
            2 if carlist else 3)


def strongest(values):
    return max(values, key=lambda name: values[name])


# ---------------------------------------------------------------------------------------------
# Areas
# ---------------------------------------------------------------------------------------------

def check_decisions(report, world):
    report.start('decisions')
    entries = parse(world['texts'][DECISIONS])
    category = block_named(entries, CATEGORY)

    for name, cost, event_id in ((SUCCESSION, '50', SUCCESSION_EVENT),
                                 (PACT, '75', SETTLEMENT_EVENT)):
        decision = decision_block(world['texts'][DECISIONS], name)
        report.equal('%s sits inside %s' % (name, CATEGORY),
                     name in [key for key, value, line in category], True)
        report.equal('%s costs %s' % (name, cost), harness.scalar(decision, 'cost'), cost)
        report.equal('%s can be taken once' % name,
                     harness.optional_scalar(decision, 'fire_only_once'), 'yes')
        icon = harness.optional_scalar(decision, 'icon')
        report.check('%s uses an icon the engine can resolve' % name,
                     icon is not None and 'GFX_decision_' + icon in registered_decision_sprites(),
                     'icon %r' % (icon,))
        complete = required_block(decision, 'complete_effect', name)
        fired = [harness.optional_scalar(body, 'id') for key, value, _ in complete
                 for body in [value[1]] if key == 'country_event' and value[0] == 'block']
        report.equal('%s fires %s' % (name, event_id), fired, [event_id])
        report.check('%s keeps an ai_will_do' % name,
                     optional_block(decision, 'ai_will_do') is not None, '')
        available = required_block(decision, 'available', name)
        report.equal('%s opens at 1945.1.1' % name,
                     [value[1] for key, value, line in available
                      if key == 'date' and value[0] == 'compare'], [('>', '1945.1.1')])
        report.equal('%s shows the chapter as a tooltip, never a flag' % name,
                     [harness.optional_scalar(body, 'tooltip') for key, value, _ in available
                      for body in [value[1]] if key == 'custom_trigger_tooltip'],
                     ['spain_postwar_chapter_tt',
                      'spain_succession_open_tt' if name == SUCCESSION else 'spain_pact_open_tt'])
        raw = [key for key, value, line in available if key == 'has_country_flag']
        report.equal('%s exposes no raw flag line' % name, raw, [])

    succession = decision_block(world['texts'][DECISIONS], SUCCESSION)
    available = required_block(succession, 'available', SUCCESSION)
    tooltips = [harness.optional_scalar(body, 'tooltip') for key, value, _ in available
                for body in [value[1]] if key == 'custom_trigger_tooltip']
    report.equal('the succession questions the settlement once',
                 tooltips, ['spain_postwar_chapter_tt', 'spain_succession_open_tt'])
    gate = [value[1] for key, value, _ in available for body in [value[1]]
            if key == 'custom_trigger_tooltip' for k2, v2, _ in body if k2 == 'NOT']
    report.check('the succession closes after it is answered',
                 any(SETTLED in repr(entry) for entry in gate), 'gate %r' % (gate,))

    pact = decision_block(world['texts'][DECISIONS], PACT)
    report.equal('the pact signs once', harness.optional_scalar(pact, 'fire_only_once'), 'yes')
    pact_available = required_block(pact, 'available', PACT)
    gates = [body for key, value, _ in pact_available
             for body in [value[1]] if key == 'custom_trigger_tooltip']
    pact_gate = [body for body in gates
                 if harness.optional_scalar(body, 'tooltip') == 'spain_pact_open_tt']
    report.equal('the pact gate is the only requirement it names itself', len(pact_gate), 1)
    gate = pact_gate[0] if pact_gate else None
    report.check('the pact waits for the succession or the surviving Crown',
                 gate is not None and SETTLED in repr(gate) and FORWARD_EDGE in repr(gate),
                 'gate %r' % (gate,))

    report.equal('the succession carries the agreed AI weight',
                 harness.optional_scalar(required_block(
                     decision_block(world['texts'][DECISIONS], SUCCESSION), 'ai_will_do', SUCCESSION),
                     'base'), '25')
    report.equal('the pact carries the agreed AI weight',
                 harness.optional_scalar(required_block(
                     decision_block(world['texts'][DECISIONS], PACT), 'ai_will_do', PACT),
                     'base'), '20')

    # The payoff decisions changed only where the card allows it.
    for name, key in ((MARSHALL, 'spain_falangist_excluded_tt'),
                      (UN_SEAT, 'spain_settled_1945_tt')):
        decision = decision_block(world['texts'][DECISIONS], name)
        available = required_block(decision, 'available', name)
        tooltips = [harness.optional_scalar(body, 'tooltip') for k, v, _ in available
                    for body in [v[1]] if k == 'custom_trigger_tooltip']
        report.equal('%s gains its new requirement as a tooltip' % name, tooltips, [key])
    seat = required_block(decision_block(world['texts'][DECISIONS], UN_SEAT), 'available', UN_SEAT)
    route = optional_block(required_block(seat, 'custom_trigger_tooltip', UN_SEAT), 'OR')
    report.check('the seat opens on the settlement that recalled the Crown',
                 route is not None and SIGNED in repr(route) and RECALLED in repr(route),
                 'route %r' % (route,))


def check_succession_event(report, world):
    report.start('succession event')
    found = events(world['texts'][EVENTS])
    for event_id in (SUCCESSION_EVENT, SETTLEMENT_EVENT):
        report.check('%s exists as a triggered country event' % event_id, event_id in found, '')
    if SUCCESSION_EVENT not in found:
        return
    event = found[SUCCESSION_EVENT]
    report.equal('%s is triggered only' % SUCCESSION_EVENT,
                 harness.optional_scalar(event, 'is_triggered_only'), 'yes')
    option_list = options(event, SUCCESSION_EVENT)
    report.equal('%s offers three answers' % SUCCESSION_EVENT,
                 [harness.scalar(option, 'name') for option in option_list],
                 [SUCCESSION_EVENT + suffix for suffix in ('.a', '.b', '.c')])

    for option in option_list:
        name = harness.scalar(option, 'name')
        report.check('%s carries an ai_chance' % name,
                     optional_block(option, 'ai_chance') is not None, '')
        report.check('%s explains itself with a tooltip' % name,
                     harness.optional_scalar(option, 'custom_effect_tooltip') is not None, '')
        written = [flag for flag in scalars(option, 'set_country_flag')
                   if flag.startswith('spain_succession_')]
        report.equal('%s sets one outcome flag and the settlement flag' % name,
                     sorted(written), sorted([SETTLED] + [flag for flag in OUTCOME_FLAGS
                                                          if flag in written]))
        report.equal('%s sets exactly one outcome flag' % name,
                     len([flag for flag in written if flag in OUTCOME_FLAGS]), 1)
        report.equal('%s grants no national spirit of its own' % name,
                     scalars(option, 'add_ideas'), [])
        hidden = required_block(option, 'hidden_effect', name)
        report.equal('%s writes the regime through the shared arbitration' % name,
                     scalars(hidden, RESOLVER), ['yes'])

    # Every scenario must leave exactly one answer clickable, and each answer must belong to the
    # faction it names.
    for label, facts in SUCCESSION_SCENARIOS.items():
        names = reachable_names(option_list, facts)
        report.equal('%s: exactly one answer is open' % label, len(names), 1)
    expected = {
        'falange leads': SUCCESSION_EVENT + '.a',
        'army leads': SUCCESSION_EVENT + '.b',
        'monarchists lead': SUCCESSION_EVENT + '.c',
        'carlists lead': SUCCESSION_EVENT + '.c',
        'no faction leads': SUCCESSION_EVENT + '.b',
    }
    for label, answer in expected.items():
        report.equal('%s is answered by %s' % (label, answer),
                     reachable_names(option_list, SUCCESSION_SCENARIOS[label]), [answer])

    # A falange-led movement cannot be answered by the army or the Crown.
    falange = option_list[0]
    report.check('the army answer is not open while the Falange leads',
                 not reachable(option_list[1], SUCCESSION_SCENARIOS['falange leads']), '')
    report.check('the Crown answer is not open while the Falange leads',
                 not reachable(option_list[2], SUCCESSION_SCENARIOS['falange leads']), '')

    # The army answer is the one that gives coup relief through the shared helper.
    report.equal('the army answer relieves the coup through the shared helper',
                 scalars(option_list[1], 'spain_loyalty_gain_small'), ['yes'])
    report.equal('no answer writes coup pressure by hand',
                 [key for option in option_list for key, value, line, _ in walk(option)
                  if value[0] == 'block'
                  and key in ('add_to_variable', 'subtract_from_variable', 'set_variable')
                  and harness.optional_scalar(value[1], 'var') == 'spain_coup_pressure'], [])

    # Two regime spirits cannot coexist: the arbitration strips all four and every add sits in an
    # exclusive branch. What the answers themselves do to the balance is executed, not read, in
    # the `execution` area below.
    resolver = block_named(parse(world['read'][EFFECTS]), RESOLVER)
    removed = sorted(flag for key, value, line, _ in walk(resolver) if key == 'remove_ideas'
                     for flag in [value[1] if value[0] == 'scalar' else None] if flag)
    report.equal('the arbitration removes all four regime spirits first',
                 removed, sorted(REGIME_IDEAS))
    adds = [(path, key) for key, value, line, path in walk(resolver) if key == 'add_ideas']
    report.equal('the arbitration adds the regime once, inside the exclusive chain',
                 len(adds), 4)
    exclusive = any('else_if' in path or 'else' in path for path, key in adds)
    report.check('every arbitration add sits in an exclusive branch', exclusive, 'adds %r' % (adds,))

    # The regime spirits the arbitration grants are the ones the ideas file defines.
    ideas = world['read'][IDEAS]
    for flag in REGIME_IDEAS:
        report.check('%s is a defined national spirit' % flag,
                     re.search(r'^\s*%s\s*=\s*\{' % re.escape(flag), ideas, re.M) is not None, '')


# ---------------------------------------------------------------------------------------------
# The invariant: the answer that is chosen is the regime that comes out
# ---------------------------------------------------------------------------------------------

CROWN_TIE = {'spain_falange': 45.0, 'spain_carlists': 25.0, 'spain_monarchists': 35.0,
             'spain_army_faction': 20.0}
CROWN_OVERRUN = {'spain_falange': 70.0, 'spain_carlists': 20.0, 'spain_monarchists': 35.0,
                 'spain_army_faction': 25.0}
NO_LEAD = {'spain_falange': 29.0, 'spain_carlists': 15.0, 'spain_monarchists': 10.0,
           'spain_army_faction': 5.0}
FALANGE_ONLY = {'spain_falange': 55.0, 'spain_carlists': 10.0, 'spain_monarchists': 10.0,
                'spain_army_faction': 20.0}
ARMY_ONLY = {'spain_falange': 10.0, 'spain_carlists': 10.0, 'spain_monarchists': 15.0,
             'spain_army_faction': 40.0}
MONARCHIST_ONLY = {'spain_falange': 10.0, 'spain_carlists': 15.0, 'spain_monarchists': 50.0,
                   'spain_army_faction': 20.0}
CARLIST_ONLY = {'spain_falange': 20.0, 'spain_carlists': 45.0, 'spain_monarchists': 20.0,
                'spain_army_faction': 25.0}
CROWN_HOUSE_TIE = {'spain_falange': 10.0, 'spain_carlists': 35.0, 'spain_monarchists': 35.0,
                   'spain_army_faction': 12.0}
CIVILIAN_TIE = {'spain_falange': 40.0, 'spain_carlists': 40.0, 'spain_monarchists': 12.0,
                'spain_army_faction': 10.0}
EVERYTHING_ZERO = {'spain_falange': 0.0, 'spain_carlists': 0.0, 'spain_monarchists': 0.0,
                   'spain_army_faction': 0.0}
AT_THE_THRESHOLD = {'spain_falange': 30.0, 'spain_carlists': 29.0, 'spain_monarchists': 30.0,
                    'spain_army_faction': 29.0}
ALL_AT_CAP = {'spain_falange': 100.0, 'spain_carlists': 100.0, 'spain_monarchists': 100.0,
              'spain_army_faction': 100.0}
JUST_BELOW_CAP = {'spain_falange': 92.0, 'spain_carlists': 90.0, 'spain_monarchists': 88.0,
                  'spain_army_faction': 40.0}

# label, values, answer, leadership facts (`None` = the flags the refresh would raise)
EXECUTED_SCENARIOS = (
    ('the Crown answers a Falangist tie', CROWN_TIE, '.62.c', None),
    ('the Crown answers a movement the Falange dominates', CROWN_OVERRUN, '.62.c', None),
    ('the army answers where no civilian part leads', NO_LEAD, '.62.b', None),
    ('the Falange answers its own lead', FALANGE_ONLY, '.62.a', None),
    ('the army answers its own lead', ARMY_ONLY, '.62.b', None),
    ('the monarchists answer', MONARCHIST_ONLY, '.62.c', None),
    ('the Carlists answer', CARLIST_ONLY, '.62.c', None),
    ('the royal houses tie and the monarchists answer', CROWN_HOUSE_TIE, '.62.c', None),
    ('two civilians tie and the Falange answers', CIVILIAN_TIE, '.62.a', None),
    ('the movement stands at zero', EVERYTHING_ZERO, '.62.b', None),
    ('the movement stands at the lead threshold', AT_THE_THRESHOLD, '.62.a', None),
    ('every part stands at the cap', ALL_AT_CAP, '.62.c', None),
    ('the movement stands just below the cap', JUST_BELOW_CAP, '.62.c', None),
    # Stale or absent cache: eligibility is a remembered flag, so the answer must still win.
    ('a stale Falangist flag answers a movement the army holds', ARMY_ONLY, '.62.a',
     {'spain_falange_leads'}),
    ('a stale royal flag answers a movement the army holds', ARMY_ONLY, '.62.c',
     {'spain_monarchists_lead'}),
    ('no leadership flag answers a movement the Falange holds', FALANGE_ONLY, '.62.b', set()),
)

ANSWERING_VARIABLE = {'spain_campaign.62.a': 'spain_falange',
                      'spain_campaign.62.b': 'spain_army_faction'}
CROWN_VARIABLES = ('spain_carlists', 'spain_monarchists')


def answer_name(suffix):
    """The full option name for a `.62.x` suffix."""
    return 'spain_campaign' + suffix


def run_answer(world, values, flags, answer, ideas=()):
    """Execute one succession answer against a real numerical state."""
    state = new_state(world, values, flags, ideas)
    execute(option_effects(option_named(world, SUCCESSION_EVENT, answer)), state)
    return state


def answering_variable(values, answer):
    if answer in ANSWERING_VARIABLE:
        return ANSWERING_VARIABLE[answer]
    return 'spain_carlists' if values['spain_carlists'] > values['spain_monarchists'] \
        else 'spain_monarchists'


def check_execution(report, world):
    report.start('execution')
    option_list = options(event_named(world, SUCCESSION_EVENT), SUCCESSION_EVENT)
    cap = WORLD_CONSTANTS['spain_campaign.faction_cap']

    scenarios = [(label, values, answer_name(answer),
                  coherent_facts(values) if given is None else set(given))
                 for label, values, answer, given in EXECUTED_SCENARIOS]
    for label, values, answer, flags in scenarios:
        names = reachable_names(option_list, new_state(world, values, flags))
        report.check('%s: %s can be chosen' % (label, answer), answer in names,
                     'open %r' % (names,))
        state = run_answer(world, values, flags, answer)
        flag, spirit, leader = expected_answer(values, answer)
        report.equal('%s: the answer writes %s' % (label, flag),
                     sorted(state['flags'] & set(OUTCOME_FLAGS)), [flag])
        report.equal('%s: the regime is %s' % (label, spirit), spirits_of(state), [spirit])
        report.equal('%s: the leader is %s' % (label, leader), leader_of(state), leader)
        winner = answering_variable(values, answer)
        others = [name for name in values if name != winner]
        report.check('%s: %s is the strict winner afterwards' % (label, winner),
                     all(state['variables'][winner] > state['variables'][name] for name in others),
                     'balance %r' % (state['variables'],))
        report.check('%s: no part is pushed past the campaign cap' % label,
                     max(state['variables'][name] for name in values) <= cap,
                     'balance %r' % (state['variables'],))
        report.check('%s: no part is driven below zero' % label,
                     min(state['variables'][name] for name in values) >= 0,
                     'balance %r' % (state['variables'],))
        # The settlement writes the regime again from the balance as it then stands.
        run_arbitration(state)
        report.equal('%s: signing the pact keeps %s' % (label, spirit), spirits_of(state), [spirit])
        clamp_campaign(state)
        run_arbitration(state)
        report.equal('%s: upkeep and the pact keep %s' % (label, spirit),
                     spirits_of(state), [spirit])
        report.equal('%s: the leader survives upkeep' % label, leader_of(state), leader)

    # Every answer must end with exactly one spirit, whatever regime the movement started under.
    for suffix, values in (('.62.a', FALANGE_ONLY), ('.62.b', NO_LEAD), ('.62.c', CROWN_TIE)):
        for start in REGIME_IDEAS + ('all four',):
            ideas = set(REGIME_IDEAS) if start == 'all four' else {start}
            state = run_answer(world, values, coherent_facts(values),
                               answer_name(suffix), ideas)
            _, spirit, leader = expected_answer(values, answer_name(suffix))
            report.equal('%s from %s leaves one spirit' % (suffix, start),
                         spirits_of(state), [spirit])
            report.equal('%s from %s leaves its own leader' % (suffix, start),
                         leader_of(state), leader)

    # The answering faction advances above the largest part of the movement by the campaign's own
    # step, bounded by its own cap, and only the parts that would tie it give way.
    step = WORLD_CONSTANTS['spain_campaign.faction_gain_large']
    for label, values, answer, given in EXECUTED_SCENARIOS:
        flags = coherent_facts(values) if given is None else set(given)
        state = run_answer(world, values, flags, answer_name(answer))
        winner = answering_variable(values, answer_name(answer))
        expected = min(max(values.values()) + step, cap)
        report.equal('%s: %s is advanced to the bounded step' % (label, winner),
                     state['variables'][winner], expected)
        for name in values:
            if name == winner:
                continue
            report.check('%s: %s only gives way when it would tie' % (label, name),
                         values[name] < expected
                         or state['variables'][name] == expected - step,
                         '%s %r -> %r' % (name, values[name], state['variables'][name]))


def check_crown_recall(report, world):
    report.start('crown recall')
    option_list = options(event_named(world, SETTLEMENT_EVENT), SETTLEMENT_EVENT)
    crown = option_named(world, SETTLEMENT_EVENT, SETTLEMENT_EVENT + '.c')
    report.check('the Crown settlement reads the current balance in its own trigger',
                 'check_variable' in repr(optional_block(crown, 'trigger')), '')
    for option in option_list:
        name = harness.scalar(option, 'name')
        for variable in ('spain_falange', 'spain_carlists', 'spain_monarchists',
                         'spain_army_faction'):
            report.equal('%s does not move %s' % (name, variable),
                         variable_writes(option, variable), [])

    # A succession the Crown answered, with the Crown still holding the movement.
    held = run_answer(world, CROWN_TIE, coherent_facts(CROWN_TIE), SUCCESSION_EVENT + '.c')
    note = new_state(world, held['variables'], held['flags'] | {SETTLED}, held['ideas'])
    open_names = reachable_names(option_list, note)
    report.check('a Crown that holds the movement can seal the settlement with it',
                 SETTLEMENT_EVENT + '.c' in open_names, 'open %r' % (open_names,))
    report.check('the own-terms form stays open beside it',
                 SETTLEMENT_EVENT + '.b' in open_names, 'open %r' % (open_names,))

    # The same answer, but the movement has since changed hands: a remembered crown is not one.
    taken = dict(note)
    taken['flags'] = set(note['flags'])
    taken['variables'] = dict(note['variables'])
    taken['variables']['spain_falange'] = 70.0
    taken['variables']['spain_monarchists'] = 30.0
    taken['variables']['spain_army_faction'] = 20.0
    taken['variables']['spain_carlists'] = 15.0
    open_names = reachable_names(option_list, taken)
    report.check('a crown overtaken by the Falange cannot be recalled',
                 SETTLEMENT_EVENT + '.c' not in open_names, 'open %r' % (open_names,))
    report.check('a settlement is still possible after the takeover',
                 SETTLEMENT_EVENT + '.b' in open_names, 'open %r' % (open_names,))

    # Signing with the Crown from the state that holds it keeps the royal regime.
    sealed = dict(note)
    sealed['flags'] = set(note['flags'])
    sealed['variables'] = dict(note['variables'])
    sealed['ideas'] = set(note['ideas'])
    sealed['temps'] = {}
    execute(option_effects(crown), sealed)
    _, spirit, leader = expected_answer(CROWN_TIE, SUCCESSION_EVENT + '.c')
    report.equal('sealing with the Crown keeps the royal regime', spirits_of(sealed), [spirit])
    report.equal('sealing with the Crown keeps the royal leader', leader_of(sealed), leader)
    report.check('sealing with the Crown recalls it', RECALLED in sealed['flags'], '')
    report.check('sealing with the Crown signs the settlement', SIGNED in sealed['flags'], '')

    # The own-terms form is always available and never writes a crown.
    own = new_state(world, MONARCHIST_ONLY, {SETTLED})
    execute(option_effects(option_named(world, SETTLEMENT_EVENT, SETTLEMENT_EVENT + '.b')), own)
    report.equal('the own-terms settlement leaves one spirit', len(spirits_of(own)), 1)
    report.check('the own-terms settlement recalls no crown', RECALLED not in own['flags'], '')
    report.check('the own-terms settlement signs the settlement', SIGNED in own['flags'], '')


def check_settlement_event(report, world):
    report.start('settlement event')
    found = events(world['texts'][EVENTS])
    report.check('%s exists as a triggered country event' % SETTLEMENT_EVENT,
                 SETTLEMENT_EVENT in found, '')
    if SETTLEMENT_EVENT not in found:
        return
    event = found[SETTLEMENT_EVENT]
    report.equal('%s is triggered only' % SETTLEMENT_EVENT,
                 harness.optional_scalar(event, 'is_triggered_only'), 'yes')
    option_list = options(event, SETTLEMENT_EVENT)
    report.equal('%s signs in three forms' % SETTLEMENT_EVENT,
                 [harness.scalar(option, 'name') for option in option_list],
                 [SETTLEMENT_EVENT + suffix for suffix in ('.a', '.b', '.c')])

    for option in option_list:
        name = harness.scalar(option, 'name')
        report.equal('%s signs the settlement' % name, SIGNED in scalars(option, 'set_country_flag'),
                     True)
        report.equal('%s grants no national spirit of its own' % name,
                     scalars(option, 'add_ideas'), [])
        hidden = required_block(option, 'hidden_effect', name)
        report.equal('%s writes the regime through the shared arbitration' % name,
                     scalars(hidden, RESOLVER), ['yes'])
        report.check('%s carries an ai_chance' % name,
                     optional_block(option, 'ai_chance') is not None, '')
        report.check('%s explains itself with a tooltip' % name,
                     harness.optional_scalar(option, 'custom_effect_tooltip') is not None, '')

    report.equal('only the Crown settlement recalls the Crown',
                 [harness.scalar(option, 'name') for option in option_list
                  if RECALLED in scalars(option, 'set_country_flag')],
                 [SETTLEMENT_EVENT + '.c'])

    for label, facts in SETTLEMENT_SCENARIOS.items():
        names = reachable_names(option_list, facts)
        report.check('%s: at least one form can be signed' % label, bool(names), 'none open')
    report.equal('a fascinated answer cannot sign with the Allies',
                 SETTLEMENT_EVENT + '.a' in reachable_names(
                     option_list, SETTLEMENT_SCENARIOS['ally leverage, falangist answer']), False)
    report.equal('a military answer cannot sign with the Allies',
                 SETTLEMENT_EVENT + '.a' in reachable_names(
                     option_list, SETTLEMENT_SCENARIOS['ally leverage, military answer']), False)
    report.equal('the Crown answer opens the Allied form without leverage',
                 SETTLEMENT_EVENT + '.a' in reachable_names(
                     option_list, SETTLEMENT_SCENARIOS['crown answer, no leverage']), True)

    # Leverage arithmetic against the threshold the two payoff decisions test.
    pressure = world['constants']['spain_campaign.leverage_pressure']
    deltas = {harness.scalar(option, 'name'): leverage_delta(option) for option in option_list}
    allies = deltas[SETTLEMENT_EVENT + '.a']
    own = deltas[SETTLEMENT_EVENT + '.b']
    crown = deltas[SETTLEMENT_EVENT + '.c']
    report.check('the Allied form raises allied leverage', allies > 0, 'delta %r' % (allies,))
    report.check('the regime\'s own form lowers allied leverage', own < 0, 'delta %r' % (own,))
    report.check('a Spain at the threshold keeps the aid after signing with the Allies',
                 pressure + allies > pressure, 'delta %r' % (allies,))
    report.check('a Spain at the threshold loses the aid by signing on its own terms',
                 pressure + own < pressure, 'delta %r' % (own,))
    report.check('the Crown form raises allied leverage a little',
                 0 < crown < allies, 'delta %r' % (crown,))


def check_flags(report, world):
    report.start('flags')
    decision_text = world['texts'][DECISIONS]
    event_text = world['texts'][EVENTS]
    plan_text = world['texts'][PLANS]
    everything = decision_text + event_text + plan_text

    new_events = events(event_text)
    writers = {}
    for event_id in (SUCCESSION_EVENT, SETTLEMENT_EVENT):
        for option in options(new_events[event_id], event_id):
            for flag in scalars(option, 'set_country_flag'):
                writers.setdefault(flag, []).append(harness.scalar(option, 'name'))
    for flag in sorted(writers):
        report.check('%s is written by this slice' % flag, flag in WRITTEN_FLAGS, 'option %r' % writers[flag])

    for flag in WRITTEN_FLAGS:
        readers = len(re.findall(r'has_country_flag\s*=\s*%s\b' % re.escape(flag), everything))
        report.check('%s is read somewhere' % flag, readers > 0, 'readers %d' % readers)

    # The three flags the decisions gate on must have a reader outside the event that writes them.
    for flag in (SETTLED, SIGNED, RECALLED):
        outside = len(re.findall(r'has_country_flag\s*=\s*%s\b' % re.escape(flag), decision_text))
        report.check('%s gates a decision' % flag, outside > 0, 'decision readers %d' % outside)

    report.equal('%s has no writer in this slice' % FORWARD_EDGE,
                 FORWARD_EDGE in writers, False)
    report.check('%s is still declared as the pact\'s forward edge' % FORWARD_EDGE,
                 FORWARD_EDGE in decision_text, '')


def check_localisation(report, world):
    report.start('localisation')
    text = world['texts'][LOC]
    with open(ROOT / LOC, 'rb') as handle:
        raw = handle.read()
    report.check('the localisation file keeps its BOM', raw[:3] == b'\xef\xbb\xbf', '')
    values = {}
    for index, line in enumerate(text.replace('\r\n', '\n').split('\n'), 1):
        match = re.match(r'^\s*([A-Za-z0-9_.\-]+):\s*"(.*)"\s*$', line)
        if match:
            values[match.group(1)] = (match.group(2), index)

    new_events = events(world['texts'][EVENTS])
    referenced = set()
    for name in (SUCCESSION, PACT):
        decision = decision_block(world['texts'][DECISIONS], name)
        referenced.add(name)
        referenced.add(name + '_desc')
        available = required_block(decision, 'available', name)
        for key, value, _ in available:
            if key == 'custom_trigger_tooltip':
                referenced.add(harness.scalar(value[1], 'tooltip'))
    for event_id in (SUCCESSION_EVENT, SETTLEMENT_EVENT):
        event = new_events[event_id]
        referenced.add(harness.scalar(event, 'title'))
        referenced.add(harness.scalar(event, 'desc'))
        for option in options(event, event_id):
            referenced.add(harness.scalar(option, 'name'))
            tooltip = harness.optional_scalar(option, 'custom_effect_tooltip')
            if tooltip:
                referenced.add(tooltip)
    for name in (MARSHALL, UN_SEAT):
        available = required_block(decision_block(world['texts'][DECISIONS], name), 'available', name)
        for key, value, _ in available:
            if key == 'custom_trigger_tooltip':
                referenced.add(harness.scalar(value[1], 'tooltip'))

    missing = sorted(key for key in referenced if key not in values)
    report.equal('every referenced key exists', missing, [])

    section = text.replace('\r\n', '\n').split(' # ================================================================ ' + LOC_SECTION, 1)
    report.check('the settlement text is one section', len(section) == 2, 'sections %d' % len(section))
    defined = set()
    if len(section) == 2:
        for line in section[1].split('\n'):
            match = re.match(r'^\s*([A-Za-z0-9_.\-]+):', line)
            if match:
                defined.add(match.group(1))
    report.equal('every key in the settlement section is referenced', sorted(defined - referenced), [])

    bad = []
    for key in sorted(defined):
        value = values.get(key, ('', 0))[0]
        if '\u00a7' in value or '\u00a3' in value:
            bad.append('%s carries a formatting glyph' % key)
        if re.search(r':\d+$', value):
            bad.append('%s carries a version suffix' % key)
        if not value.strip():
            bad.append('%s is empty' % key)
    report.equal('the settlement text is plain, unversioned and non-empty', bad, [])

    # The Crown answer must not name one royal house while the arbitration may install the other.
    crown = values.get('spain_campaign.62.c.tt', ('', 0))[0]
    report.check('the Crown answer never claims the Carlists were handed another king',
                 'handed a different' not in crown and 'Bourbon' not in crown, crown[:80])
    report.check('the Crown answer names the claimant left outside the settlement',
                 'other claimant' in crown, crown[:80])


def tree_blocks(text):
    """(tree id, focus ids) for every focus_tree in a focus file, read tolerantly.

    The shared tokeniser models the `key = value` grammar and chokes on focus-tree rows that
    carry `@` tokens, so tree inventory uses a brace scan: find `focus_tree = {`, read its own
    `id`, then collect the `id` of every `focus = {` inside it.
    """
    trees = []
    for match in re.finditer(r'^\s*focus_tree\s*=\s*\{', text, re.M):
        start = match.end() - 1
        depth = 0
        end = start
        for index in range(start, len(text)):
            if text[index] == '{':
                depth += 1
            elif text[index] == '}':
                depth -= 1
                if depth == 0:
                    end = index
                    break
        body = text[start + 1:end]
        tree_id = re.search(r'^\s*id\s*=\s*([A-Za-z0-9_]+)', body, re.M)
        focuses = []
        for focus in re.finditer(r'^\s*focus\s*=\s*\{', body, re.M):
            fstart = focus.end() - 1
            fdepth = 0
            fend = fstart
            for index in range(fstart, len(body)):
                if body[index] == '{':
                    fdepth += 1
                elif body[index] == '}':
                    fdepth -= 1
                    if fdepth == 0:
                        fend = index
                        break
            found = re.search(r'^\s*id\s*=\s*([A-Za-z0-9_]+)', body[fstart + 1:fend], re.M)
            if found:
                focuses.append(found.group(1))
        trees.append((tree_id.group(1) if tree_id else None, focuses))
    return trees


def focus_ids(text, tree_id):
    """The focus ids of the tree with this id, and nothing from any other tree."""
    matches = [focuses for found, focuses in tree_blocks(text) if found == tree_id]
    if len(matches) != 1:
        raise Unsupported('%d trees with id %s in the file' % (len(matches), tree_id))
    if len(matches[0]) < 10:
        raise Unsupported('tree %s parsed to only %d focuses' % (tree_id, len(matches[0])))
    return matches[0]


def plan(text, name):
    return block_named(parse(text), name)


def check_ai_plans(report, world):
    report.start('ai plans')
    text = world['texts'][PLANS]
    national = plan(text, NATIONAL_PLAN)
    republican = plan(text, REPUBLICAN_PLAN)

    national_enable = required_block(national, 'enable', NATIONAL_PLAN)
    national_abort = required_block(national, 'abort', NATIONAL_PLAN)
    report.equal('the Nationalist plan is enabled by the Nationalist chapter',
                 scalars(national_enable, 'has_country_flag'), [NATIONALCHAPTER_FLAG])
    report.equal('the Nationalist plan is only for historical AI',
                 scalars(national_enable, 'is_historical_focus_on'), ['yes'])
    report.check('the Nationalist plan aborts symmetrically',
                 NATIONALCHAPTER_FLAG in repr(national_abort), 'abort %r' % (national_abort,))

    republican_enable = required_block(republican, 'enable', REPUBLICAN_PLAN)
    republican_abort = required_block(republican, 'abort', REPUBLICAN_PLAN)
    report.equal('the Republican plan is enabled by the Republican chapter',
                 scalars(republican_enable, 'has_country_flag'), [REPUBLICAN_CHAPTER_FLAG])
    report.check('the Republican plan aborts symmetrically',
                 REPUBLICAN_CHAPTER_FLAG in repr(republican_abort), 'abort %r' % (republican_abort,))
    report.equal('the two plans are never enabled by the same chapter',
                 NATIONALCHAPTER_FLAG in repr(republican_enable), False)

    national_spanish = focus_ids(world['read'][NATIONAL_TREE], 'spanish_focus')
    republican_tree = focus_ids(world['read'][REPUBLIC_TREE], 'spain_republic_postwar_focus')

    national_list = bare_words(national, 'ai_national_focuses')
    republican_list = bare_words(republican, 'ai_national_focuses')
    report.check('the Nationalist plan names focuses', len(national_list) >= 5,
                 'list %r' % (national_list,))
    report.check('the Republican plan kept its list', len(republican_list) >= 10,
                 'list length %d' % len(republican_list))

    stray = [focus for focus in national_list if focus not in national_spanish]
    report.equal('every focus the Nationalist plan names exists in spanish_focus', stray, [])
    stray = [focus for focus in republican_list if focus not in republican_tree]
    report.equal('every focus the Republican plan names exists in its own tree', stray, [])
    report.equal('the Nationalist plan names no SPR4 focus',
                 [focus for focus in national_list if focus.startswith('SPR4_')], [])
    report.equal('the Republican plan names no SPA focus',
                 [focus for focus in republican_list if focus.startswith('SPA_')], [])
    cross = [focus for focus in national_list if focus in republican_tree]
    report.equal('no focus of the Republican tree leaks into the Nationalist plan', cross, [])


def check_nothing_else_moved(report, world):
    report.start('scope')
    baseline = {path: harness.read_text(path, BASELINE) for path in (DECISIONS, EVENTS)}

    live_decisions = parse(world['texts'][DECISIONS])
    old_decisions = parse(baseline[DECISIONS])
    for name in UNTOUCHED_DECISIONS:
        report.equal('%s is unchanged' % name,
                     repr(decision_block(world['texts'][DECISIONS], name)),
                     repr(decision_block(baseline[DECISIONS], name)))

    live_events = events(world['texts'][EVENTS])
    old_events = events(baseline[EVENTS])
    for event_id in UNTOUCHED_EVENTS:
        report.equal('%s is unchanged' % event_id,
                     canonical(live_events.get(event_id, [])),
                     canonical(old_events.get(event_id, [])))

    # The two payoff decisions may change only inside `available`.
    for name, key, dropped in ((MARSHALL, 'spain_falangist_excluded_tt', None),
                               (UN_SEAT, 'spain_settled_1945_tt', 'spain_allied_leverage_high')):
        live = decision_block(world['texts'][DECISIONS], name)
        old = decision_block(baseline[DECISIONS], name)
        strip = lambda entries: canonical([entry for entry in entries
                                           if entry[0] != 'available'])
        report.equal('%s keeps every block but available' % name, strip(live), strip(old))
        live_available = canonical(required_block(live, 'available', name))
        old_available = canonical(required_block(old, 'available', name))
        added = [entry for entry in live_available if entry not in old_available]
        removed = [entry for entry in old_available if entry not in live_available]
        report.equal('%s gained exactly one requirement block' % name, len(added), 1)
        report.check('%s gained the %s tooltip' % (name, key), key in repr(added), repr(added)[:80])
        if dropped:
            report.equal('%s only replaced its leverage line' % name,
                         [entry[0] for entry in removed], [dropped])
        else:
            report.equal('%s removed nothing' % name, removed, [])

    report.equal('the slice adds no new regime spirit',
                 harness.read_text(IDEAS) == harness.read_text(IDEAS, BASELINE), True)
    del live_decisions, old_decisions


AREAS = (
    ('decisions', check_decisions),
    ('succession event', check_succession_event),
    ('settlement event', check_settlement_event),
    ('execution', check_execution),
    ('crown recall', check_crown_recall),
    ('flags', check_flags),
    ('localisation', check_localisation),
    ('ai plans', check_ai_plans),
    ('scope', check_nothing_else_moved),
)


# ---------------------------------------------------------------------------------------------
# Mutants
# ---------------------------------------------------------------------------------------------

def area_failures(function, world):
    report = Report(detail=False)
    try:
        function(report, world)
    except Unsupported as error:
        report.check('%s can read the world' % function.__name__, False, str(error))
    return report.checks, report.failures


def failure_text(failures):
    return ' | '.join(failures)


def mutate(world, path, old, new):
    text = world['texts'][path]
    if old not in text:
        raise Unsupported('mutant anchor %r is not in %s' % (old, path))
    return with_text(world, path, text.replace(old, new, 1))


def drop_option_trigger(world):
    """The Falangist option answers whether or not the Falange leads."""
    old = """	option = {
		name = spain_campaign.62.a
		trigger = { spain_falange_leads = yes }
"""
    new = """	option = {
		name = spain_campaign.62.a
"""
    return mutate(world, EVENTS, old, new)


def drop_fire_only_once(world):
    old = """	SPR_the_pact_of_1945 = {
		icon = generic_political_address
		cost = 75
		fire_only_once = yes
"""
    new = """	SPR_the_pact_of_1945 = {
		icon = generic_political_address
		cost = 75
"""
    return mutate(world, DECISIONS, old, new)


def drop_succession_fire_only_once(world):
    old = """	SPR_the_succession_question = {
		icon = generic_political_discourse
		cost = 50
		fire_only_once = yes
"""
    new = """	SPR_the_succession_question = {
		icon = generic_political_discourse
		cost = 50
"""
    return mutate(world, DECISIONS, old, new)


def unregistered_pact_icon(world):
    old = "	SPR_the_pact_of_1945 = {\n		icon = generic_political_address\n"
    new = "	SPR_the_pact_of_1945 = {\n		icon = generic_foreign_policy\n"
    return mutate(world, DECISIONS, old, new)


def revert_crown_preparation(world):
    """The Crown answer adds its fixed step again and lets the arbitration arbitrate."""
    old = """		if = {
			limit = { check_variable = { spain_succession_carlist = 1 } }
			set_temp_variable = { spain_succession_step = spain_succession_result }
			subtract_from_temp_variable = { spain_succession_step = spain_carlists }
			add_to_variable = { var = spain_carlists value = spain_succession_step }
		}
		else = {
			set_temp_variable = { spain_succession_step = spain_succession_result }
			subtract_from_temp_variable = { spain_succession_step = spain_monarchists }
			add_to_variable = { var = spain_monarchists value = spain_succession_step }
		}
"""
    new = """		if = {
			limit = { check_variable = { spain_succession_carlist = 1 } }
			add_to_variable = { var = spain_carlists value = constant:spain_campaign.faction_gain_large }
		}
		else = {
			add_to_variable = { var = spain_monarchists value = constant:spain_campaign.faction_gain_large }
		}
"""
    return mutate(world, EVENTS, old, new)


def revert_army_preparation(world):
    """The army answer is a fixed push again, so the strongest civilian still wins."""
    old = """		set_temp_variable = { spain_succession_step = spain_succession_result }
		subtract_from_temp_variable = { spain_succession_step = spain_army_faction }
		add_to_variable = { var = spain_army_faction value = spain_succession_step }
"""
    new = ("		add_to_variable = { var = spain_army_faction "
           "value = constant:spain_campaign.faction_gain_large }\n")
    return mutate(world, EVENTS, old, new)


def swap_crown_house(world):
    """The Crown answer always reads the wrong royal house."""
    old = "			limit = { check_variable = { spain_carlists > spain_monarchists } }\n" \
          "			set_temp_variable = { spain_succession_carlist = 1 }\n"
    new = "			limit = { check_variable = { spain_monarchists > spain_carlists } }\n" \
          "			set_temp_variable = { spain_succession_carlist = 1 }\n"
    return mutate(world, EVENTS, old, new)


def drop_crown_recall_guard(world):
    """The Crown settlement goes back to accepting a remembered succession alone."""
    old = """			OR = {
				AND = {
					check_variable = { spain_monarchists > spain_falange }
					check_variable = { spain_monarchists > spain_carlists }
					check_variable = { spain_monarchists > spain_army_faction }
				}
				AND = {
					check_variable = { spain_carlists > spain_falange }
					check_variable = { spain_carlists > spain_monarchists }
					check_variable = { spain_carlists > spain_army_faction }
				}
			}
"""
    return mutate(world, EVENTS, old, '')


def drop_resolver_removal(world):
    """The shared arbitration forgets to strip one old regime, in memory only."""
    old = "	if = { limit = { has_idea = spain_falangist_state } remove_ideas = spain_falangist_state }\n"
    text = world['read'][EFFECTS]
    if old not in text:
        raise Unsupported('the arbitration removal anchor is not in %s' % EFFECTS)
    return with_read(world, EFFECTS, text.replace(old, '', 1))


def drop_succession_winner_step(world):
    """The Falange answer stops establishing a winner and only pays its other rewards."""
    old = """		set_temp_variable = { spain_succession_step = spain_succession_result }
		subtract_from_temp_variable = { spain_succession_step = spain_falange }
		add_to_variable = { var = spain_falange value = spain_succession_step }
"""
    return mutate(world, EVENTS, old, '')


def raise_faction_cap(world):
    """The answers overrun the campaign cap instead of stopping at it."""
    old = "			set_temp_variable = { spain_succession_result = constant:spain_campaign.faction_cap }"
    new = "			set_temp_variable = { spain_succession_result = 200 }"
    text = world['texts'][EVENTS]
    if text.count(old) != 3:
        raise Unsupported('the cap line appears %d times, expected three' % text.count(old))
    return with_text(world, EVENTS, text.replace(old, new))


def widen_pact_date(world):
    old = """		available = {
			date > 1945.1.1
			custom_trigger_tooltip = {
				tooltip = spain_postwar_chapter_tt
				spain_in_postwar_chapter = yes
			}
			custom_trigger_tooltip = {
				tooltip = spain_pact_open_tt
"""
    new = old.replace('date > 1945.1.1', 'date > 1944.1.1')
    return mutate(world, DECISIONS, old, new)


def delete_tooltip_key(world):
    text = world['texts'][LOC]
    lines = text.split('\n')
    kept = [line for line in lines if ' spain_campaign.63.c.tt:' not in line]
    if len(kept) == len(lines):
        raise Unsupported('cannot delete spain_campaign.63.c.tt')
    return with_text(world, LOC, '\n'.join(kept))


def swap_plan_flags(world):
    text = world['texts'][PLANS]
    swapped = text.replace(NATIONALCHAPTER_FLAG, '@@TMP@@').replace(
        REPUBLICAN_CHAPTER_FLAG, NATIONALCHAPTER_FLAG).replace('@@TMP@@', REPUBLICAN_CHAPTER_FLAG)
    return with_text(world, PLANS, swapped)


MUTANTS = (
    ('option without its faction trigger', EVENTS, drop_option_trigger, 'succession event'),
    ('pact without fire_only_once', DECISIONS, drop_fire_only_once, 'decisions'),
    ('succession without fire_only_once', DECISIONS, drop_succession_fire_only_once, 'decisions'),
    ('pact icon the engine cannot resolve', DECISIONS, unregistered_pact_icon, 'decisions'),
    ('Falange answer without its decisive preparation', EVENTS, drop_succession_winner_step,
     'execution'),
    ('army answer without its decisive preparation', EVENTS, revert_army_preparation, 'execution'),
    ('Crown answer without its decisive preparation', EVENTS, revert_crown_preparation,
     'execution'),
    ('Crown answer reading the wrong royal house', EVENTS, swap_crown_house, 'execution'),
    ('answers allowed to overrun the campaign cap', EVENTS, raise_faction_cap, 'execution'),
    ('arbitration that keeps an old regime spirit', EFFECTS, drop_resolver_removal, 'execution'),
    ('Crown settlement without its royal-winner guard', EVENTS, drop_crown_recall_guard,
     'crown recall'),
    ('pact date widened to 1944', DECISIONS, widen_pact_date, 'decisions'),
    ('deleted settlement tooltip', LOC, delete_tooltip_key, 'localisation'),
    ('plans with swapped chapter flags', PLANS, swap_plan_flags, 'ai plans'),
)


def main():
    detail = '--detail' in sys.argv
    live = load_world()
    WORLD_CONSTANTS.update(live['constants'])
    checks = 0
    failures = []

    for name, function in AREAS:
        if detail:
            print('[%s]' % name)
        area_checks, area_fails = area_failures(function, live)
        checks += len(area_checks)
        failures.extend(area_fails)
        if detail:
            print('  %d checks in this area, %d failures' % (len(area_checks), len(area_fails)))
            if name == 'succession event' and SUCCESSION_EVENT in events(live['texts'][EVENTS]):
                event = events(live['texts'][EVENTS])[SUCCESSION_EVENT]
                for label, facts in SUCCESSION_SCENARIOS.items():
                    print('    %-20s open: %s' % (label, reachable_names(options(event, SUCCESSION_EVENT), facts)))
            if name == 'settlement event' and SETTLEMENT_EVENT in events(live['texts'][EVENTS]):
                event = events(live['texts'][EVENTS])[SETTLEMENT_EVENT]
                print('    leverage deltas: %r (threshold %r)'
                      % ({harness.scalar(option, 'name'): leverage_delta(option)
                          for option in options(event, SETTLEMENT_EVENT)},
                         live['constants']['spain_campaign.leverage_pressure']))

    # --- the pre-change tree, where none of this exists -----------------------------------
    baseline = {'texts': {}, 'read': live['read'], 'constants': live['constants']}
    for path in TEXT_FILES:
        try:
            baseline['texts'][path] = harness.read_text(path, BASELINE)
        except SystemExit:
            print('the negative controls need repository history; this is not a pass')
            return 2
    for name, function in (('decisions', check_decisions),
                           ('succession event', check_succession_event),
                           ('settlement event', check_settlement_event),
                           ('ai plans', check_ai_plans)):
        _, baseline_fails = area_failures(function, baseline)
        checks += 1
        if not baseline_fails:
            failures.append('negative control: %s passes on the pre-change tree at %s'
                            % (name, BASELINE))
    if detail:
        print('  mutant [pre-change tree] %s' % BASELINE)

    # --- the named mutants ----------------------------------------------------------------
    for label, path, builder, area in MUTANTS:
        try:
            mutant = builder(live)
        except Unsupported as error:
            checks += 1
            failures.append('negative control: the %s mutant cannot be built: %s' % (label, error))
            continue
        _, mutant_fails = area_failures(dict(AREAS)[area], mutant)
        checks += 1
        if not mutant_fails:
            failures.append('negative control: the %s mutant is not rejected by %s' % (label, area))
        if detail:
            print('  mutant [%s] %d failures in %s, e.g. %s'
                  % (label, len(mutant_fails), area, mutant_fails[0] if mutant_fails else 'none'))

    print('%d checks, %d failures' % (checks, len(failures)))
    for failure in failures:
        print('  FAIL ' + failure)
    print('Read: ' + ', '.join(TEXT_FILES + READ_ONLY))
    print('Not performed: no game launch, no decision clicked, no event fired, no tooltip '
          'rendered, no AI plan observed in a campaign.')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
