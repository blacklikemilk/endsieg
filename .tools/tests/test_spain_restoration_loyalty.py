"""Regression test: the Restoration officer-corps rewards move in the documented direction.

The Restoration chapter shipped two officer-corps helpers that called themselves "gain" while
adding positive `coup_relief` to `spain_coup_pressure`, so ten focuses raised the chance of a
pronunciation while their text claimed to secure the army. This test executes that claim against
the shipped source instead of restating it.

Six facts are asserted, from the files the game loads:

    1. every one of the six loyalty helpers writes both meters with the sign its name promises
       (a gain raises loyalty and relieves coup pressure, a loss lowers loyalty and feeds it),
       against the constant each one reads;
    2. each of the ten focuses that calls a gain helper ends with more loyalty and less coup
       pressure, computed by expanding the helper call into the constant it resolves to;
    3. no focus anywhere in the tree pairs a loyalty gain with a positive coup-pressure write,
       and no focus in this era writes `coup_relief` outside a subtraction;
    4. the three focuses that used to share one payload now pay three different things, each the
       thing its own tooltip claims (seats for the Court Party, seats plus patronage for the
       cacique machine, a balance collision for the constitutional crisis);
    5. every focus that sets a flag the recount turns into seats recounts on completion, so no
       tooltip promises Cortes seats the focus does not move, and every `..._seats_tt` promise
       matches the direction of the recount rule it relies on;
    6. the ten repaired focuses show the officer-corps effect, and the localisation key exists
       once.

The same checks are then run against the pre-repair tree, pinned by full object name, and each
area must fail there: a check that passes on both the repair and the defect proves nothing.

Run from the repository root:

    python .tools/tests/test_spain_restoration_loyalty.py            # exit 0 = pass
    python .tools/tests/test_spain_restoration_loyalty.py --detail    # print every check

This is a source simulation. It proves what the script says, not what the engine does: no focus
was clicked, no coup rolled, no tooltip drawn, and the game was never launched.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_spain_cortes_recount as base  # noqa: E402  (the shared tokeniser and parser)

EFFECTS_PATH = 'common/scripted_effects/spain_campaign_effects.txt'
FOCUS_PATH = 'common/national_focus/spain_restoration.txt'
CORTES_PATH = 'common/scripted_effects/spain_cortes_effects.txt'
LOC_FOCUS_PATH = 'localisation/english/spain_campaign_focus_l_english.yml'
LOC_SYSTEM_PATH = 'localisation/english/spain_campaign_l_english.yml'
CONSTANTS_PATH = 'common/script_constants/spain_campaign.txt'

COVERED_FILES = (EFFECTS_PATH, FOCUS_PATH, CORTES_PATH, LOC_FOCUS_PATH, LOC_SYSTEM_PATH,
                 CONSTANTS_PATH)

# The pre-repair tree, pinned by full object name so it stays a mutant after the repair lands.
BASELINE_REV = '5ad0945ad1a92944a258a5097680a220cb1c7af6'

LOYALTY = 'spain_military_loyalty'
PRESSURE = 'spain_coup_pressure'

# name -> (loyalty direction, pressure direction); +1 gain, -1 loss, 0 reset to zero.
HELPERS = {
    'spain_loyalty_gain_small': (1, -1),
    'spain_loyalty_gain': (1, -1),
    'spain_loyalty_gain_large': (1, 0),
    'spain_loyalty_loss_small': (-1, 1),
    'spain_loyalty_loss': (-1, 1),
    'spain_loyalty_loss_large': (-1, 1),
}
GAIN_HELPERS = tuple(name for name, (loyalty, _) in HELPERS.items() if loyalty > 0)

# The ten focuses D1 named, six on the small helper and four on the large one.
AFFECTED = (
    'SPR1_conservative_party',
    'SPR1_repress_the_cnt',
    'SPR1_civil_guard_expansion',
    'SPR1_suppress_the_mancomunitat',
    'SPR1_military_academy',
    'SPR1_the_army_settles',
    'SPR1_royal_guard',
    'SPR1_africanist_command',
    'SPR1_spanish_legion',
    'SPR1_peninsular_reform',
)

TRIO = ('SPR1_court_party', 'SPR1_cacique_deputies', 'SPR1_constitutional_crisis')
OFFICER_TOOLTIP = 'spain_officer_corps_calms_tt'

PARTY_NAMES = {
    'monarchists': 'monarchists',
    'liberals': 'liberals',
    'conservatives': 'conservatives',
    'republicans': 'republicans',
    'socialists': 'socialists',
    'carlists': 'carlists',
    'falangists': 'falange',
}


class Unsupported(Exception):
    """A script shape this test does not model. Failing loudly beats guessing."""


# ---------------------------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------------------------

def read_text(path, revision=None):
    if revision is None:
        with open(ROOT / path, 'r', encoding='utf-8-sig') as handle:
            return handle.read()
    result = subprocess.run(['git', 'show', '%s:%s' % (revision, path)], cwd=str(ROOT),
                            capture_output=True)
    if result.returncode != 0:
        print('cannot read %s:%s' % (revision, path))
        print(result.stderr.decode('utf-8', 'replace').strip())
        print('the negative controls need repository history; this is not a pass')
        sys.exit(2)
    return result.stdout.decode('utf-8-sig')


def parse_constants(text):
    constants = {}
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        key, value = stripped.split('=', 1)
        try:
            constants['spain_campaign.' + key.strip()] = float(value.strip())
        except ValueError:
            continue
    if len(constants) < 50:
        raise Unsupported('constants parsed to only %d values' % len(constants))
    return constants


def load_world(revision=None):
    return {
        'effects': read_text(EFFECTS_PATH, revision),
        'focus': read_text(FOCUS_PATH, revision),
        'cortes': read_text(CORTES_PATH, revision),
        'loc_focus': read_text(LOC_FOCUS_PATH, revision),
        'loc_system': read_text(LOC_SYSTEM_PATH, revision),
        'constants': parse_constants(read_text(CONSTANTS_PATH, revision)),
    }


# ---------------------------------------------------------------------------------------------
# Parser. The shared harness models `key = value` and comparisons; a focus tree also carries
# bare-word lists (`search_filters = { FOCUS_FILTER_POLITICAL }`), so this test keeps its own
# reader and reuses only the shared report format.
# ---------------------------------------------------------------------------------------------

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
        elif char in '<>':
            if index + 1 < length and text[index + 1] == '=':
                tokens.append(('op', char + '=', line))
                index += 2
            else:
                tokens.append(('op', char, line))
                index += 1
        elif char in ' \t\r\n':
            if char == '\n':
                line += 1
            index += 1
        else:
            start = index
            while index < length and text[index] not in ' \t\r\n{}=#<>':
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
        following = tokens[index + 1]
        if following[0] == 'op':
            if index + 2 >= len(tokens) or tokens[index + 2][0] != 'word':
                raise Unsupported('bad comparison after %s at line %d' % (text, line))
            entries.append((text, ('compare', (following[1], tokens[index + 2][1])), line))
            index += 3
            continue
        if following[0] != '=':
            # A bare word inside a list: `search_filters = { FOCUS_FILTER_POLITICAL }`.
            entries.append((text, ('bare', None), line))
            index += 1
            continue
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


def parse_file(text):
    entries, _ = parse_block(tokenize(text), 0)
    blocks = {}
    for key, value, line in entries:
        if value[0] == 'block':
            blocks[key] = (value[1], line)
    return blocks


def block_of(text, name):
    parsed = parse_file(text)
    if name not in parsed:
        raise Unsupported('%s not found' % name)
    return parsed[name][0]


def scalar(entries, key, line='?'):
    for entry_key, value, entry_line in entries:
        if entry_key == key:
            if value[0] != 'scalar':
                raise Unsupported('%s is not a value at line %s' % (key, entry_line))
            return value[1]
    raise Unsupported('missing %s at line %s' % (key, line))


def optional_scalar(entries, key):
    for entry_key, value, entry_line in entries:
        if entry_key == key and value[0] == 'scalar':
            return value[1]
    return None


def focus_blocks(text):
    tree = block_of(text, 'focus_tree')
    found = {}
    for key, value, line in tree:
        if key != 'focus' or value[0] != 'block':
            continue
        body = value[1]
        found[scalar(body, 'id', line)] = body
    return found


def reward_of(body):
    for key, value, line in body:
        if key == 'completion_reward' and value[0] == 'block':
            return value[1]
    return []


VAR_WRITES = {'add_to_variable': 1, 'subtract_from_variable': -1, 'set_variable': 0}


def var_writes(entries):
    """Every variable write at this level of a block, as (var, op, value token, line)."""
    writes = []
    for key, value, line in entries:
        if key in VAR_WRITES and value[0] == 'block':
            writes.append((optional_scalar(value[1], 'var'), key,
                           optional_scalar(value[1], 'value'), line))
    return writes


def amount_of(token, constants):
    if not isinstance(token, str):
        raise Unsupported('unreadable value %r' % (token,))
    if token.startswith('constant:'):
        name = token[len('constant:'):]
        if name not in constants:
            raise Unsupported('unknown constant %s' % name)
        return constants[name]
    try:
        return float(token)
    except ValueError:
        raise Unsupported('a meter written from a variable (%s) is not modelled' % token)


def meter_ops(entries, constants, helpers=None):
    """Signed writes to the two officer-corps meters, with helper calls expanded.

    Returns {'spain_military_loyalty': [(sign, amount)], 'spain_coup_pressure': [...]} where the
    sign is the operation and the amount is the constant as written, which for a loss is already
    negative. A sign of 0 means the block resets the meter to a literal.
    """
    ops = {LOYALTY: [], PRESSURE: []}
    for var, key, token, line in var_writes(entries):
        if var not in ops:
            continue
        ops[var].append((VAR_WRITES[key], amount_of(token, constants)))
    for key, value, line in entries:
        if helpers and key in helpers and value[0] == 'scalar' and value[1] == 'yes':
            for var in ops:
                for sign, amount in helpers[key].get(var, ()):
                    ops[var].append((sign, amount))
    return ops


def net(ops):
    """Unambiguous delta for a meter, or None when the block resets it to zero."""
    if any(sign == 0 for sign, _ in ops):
        return None
    return sum(sign * amount for sign, amount in ops)


def helper_table(effects_text, constants):
    table = {}
    for name in HELPERS:
        body = block_of(effects_text, name)
        table[name] = meter_ops(body, constants)
    return table


# ---------------------------------------------------------------------------------------------
# The recount's flag readers
# ---------------------------------------------------------------------------------------------

def flag_readers(cortes_text):
    """flag -> {party: signed delta} for every flag the recount turns into seats."""
    recount = block_of(cortes_text, 'spain_cortes_recount')
    readers = {}
    for key, value, line in recount:
        if key != 'if' or value[0] != 'block':
            continue
        body = value[1]
        flag = None
        for entry_key, entry_value, _ in body:
            if entry_key == 'limit' and entry_value[0] == 'block':
                flag = optional_scalar(entry_value[1], 'has_country_flag')
        if not flag:
            continue
        deltas = {}
        for var, op, token, _ in var_writes(body):
            if not var or not var.startswith('spain_cortes_raw_'):
                continue
            if op not in ('add_to_variable', 'subtract_from_variable'):
                continue
            party = var[len('spain_cortes_raw_'):]
            deltas[party] = deltas.get(party, 0) + VAR_WRITES[op] * abs(float(token))
        if deltas:
            readers[flag] = deltas
    return readers


def flags_of(entries):
    return [value[1] for key, value, _ in entries
            if key == 'set_country_flag' and value[0] == 'scalar']


def promised_seats(text):
    """(party, direction) pairs promised by a `..._seats_tt` line."""
    promises = []
    for party, direction in re.findall(r'(\w+)\s+(gain|lose)s?\b', text):
        key = PARTY_NAMES.get(party.lower())
        if key:
            promises.append((key, 1 if direction == 'gain' else -1))
    return promises


# ---------------------------------------------------------------------------------------------
# Areas
# ---------------------------------------------------------------------------------------------

def check_helpers(report, world):
    table = helper_table(world['effects'], world['constants'])
    for name in HELPERS:
        loyalty_want, pressure_want = HELPERS[name]
        ops = table[name]
        loyalty = net(ops[LOYALTY])
        pressure = net(ops[PRESSURE])
        report.check('%s writes military loyalty' % name, bool(ops[LOYALTY]),
                     'no loyalty write at all')
        report.check('%s loyalty moves %s' % (name, 'up' if loyalty_want > 0 else 'down'),
                     loyalty is not None and loyalty * loyalty_want > 0,
                     'loyalty delta %r' % (loyalty,))
        if pressure_want == 0:
            report.check('%s resets coup pressure' % name,
                         ops[PRESSURE] and ops[PRESSURE][0][0] == 0,
                         'pressure ops %r' % (ops[PRESSURE],))
        else:
            report.check('%s coup pressure moves %s' % (name, 'down' if pressure_want < 0 else 'up'),
                         pressure is not None and pressure * pressure_want > 0,
                         'pressure delta %r' % (pressure,))

    # The inversion itself, stated as a property: a helper named "gain" may never add risk. A
    # helper that resets the meter to zero relieves it, which is the same direction.
    for name in GAIN_HELPERS:
        pressure = net(table[name][PRESSURE])
        relieved = bool(table[name][PRESSURE]) and (pressure is None or pressure < 0)
        report.check('%s does not add coup pressure' % name, relieved,
                     'pressure delta %r' % (pressure,))


def check_affected_focuses(report, world):
    forces = helper_table(world['effects'], world['constants'])
    focuses = focus_blocks(world['focus'])
    with_gain = []
    for focus_id, body in focuses.items():
        entries = reward_of(body)
        ops = meter_ops(entries, world['constants'], forces)
        calls = [key for key, value, _ in entries
                 if key in GAIN_HELPERS and value[0] == 'scalar' and value[1] == 'yes']
        if calls:
            with_gain.append(focus_id)
            loyalty = net(ops[LOYALTY])
            pressure = net(ops[PRESSURE])
            report.check('%s raises loyalty' % focus_id,
                         loyalty is not None and loyalty > 0, 'loyalty delta %r' % (loyalty,))
            report.check('%s lowers coup pressure' % focus_id,
                         pressure is not None and pressure < 0, 'pressure delta %r' % (pressure,))
    report.equal('the focuses calling a loyalty-gain helper', sorted(with_gain), sorted(AFFECTED))

    # No focus in the file may write the relief constants directly at all: the helper owns them.
    for focus_id in focuses:
        for key, value, line in reward_of(focuses[focus_id]):
            if key in ('add_to_variable', 'subtract_from_variable') and value[0] == 'block':
                token = optional_scalar(value[1], 'value') or ''
                if 'coup_relief' in token:
                    report.check('%s does not write coup_relief itself' % focus_id, False,
                                 'line %d %s = %s' % (line, key, token))


def check_trio(report, world):
    focuses = focus_blocks(world['focus'])
    rewards = {focus_id: reward_of(focuses[focus_id]) for focus_id in TRIO}

    def variables(entries):
        return [var for var, _, _, _ in var_writes(entries) if var]

    def effects(entries):
        return [key for key, _, _ in entries if key not in ('custom_effect_tooltip',
                                                            'mark_focus_tree_layout_dirty')]

    signatures = {focus_id: (tuple(sorted(variables(entries))), tuple(sorted(effects(entries))))
                  for focus_id, entries in rewards.items()}
    seen = {}
    for focus_id, signature in signatures.items():
        if signature in seen:
            report.check('%s pays something %s does not' % (focus_id, seen[signature]), False,
                         'identical payload')
        seen.setdefault(signature, focus_id)

    court = variables(rewards['SPR1_court_party'])
    cacique = variables(rewards['SPR1_cacique_deputies'])
    crisis = variables(rewards['SPR1_constitutional_crisis'])
    report.check('SPR1_court_party moves monarchist seats', 'spain_party_shift_monarchists' in court)
    report.check('SPR1_cacique_deputies moves the patronage machine',
                 'spain_crown_patronage' in cacique)
    report.check('SPR1_cacique_deputies moves monarchist seats',
                 'spain_party_shift_monarchists' in cacique)
    report.check('SPR1_cacique_deputies carries more seats than the Court Party',
                 'spain_party_shift_monarchists' in cacique
                 and 'constant:spain_campaign.swing_medium'
                 in [optional_scalar(value[1], 'value') for key, value, _ in rewards['SPR1_cacique_deputies']
                     if key == 'add_to_variable' and value[0] == 'block'
                     and optional_scalar(value[1], 'var') == 'spain_party_shift_monarchists'])
    calls = [key for key, value, _ in rewards['SPR1_constitutional_crisis']
             if value[0] == 'scalar']
    report.check('SPR1_constitutional_crisis moves both sides of the balance',
                 'spain_push_cortes_small' in calls and 'spain_push_crown_small' in calls,
                 'calls %r' % (calls,))

    # Every seats promise of the trio is honoured by the script its own tooltip describes.
    for focus_id, tooltip in (('SPR1_court_party', 'spain_court_party_tt'),
                              ('SPR1_cacique_deputies', 'spain_cacique_deputies_tt')):
        text = world['loc_system']
        match = re.search(r'^\s*%s:\s*"(.*)"\s*$' % re.escape(tooltip), text, re.MULTILINE)
        report.check('%s tooltip resolves' % tooltip, match is not None)
        if match and 'seat' in match.group(1):
            report.check('%s promises seats and the focus moves them' % focus_id,
                         'spain_party_shift_monarchists' in variables(rewards[focus_id])
                         or 'spain_crown_patronage' in variables(rewards[focus_id]))
        report.check('%s recounts its own chamber change' % focus_id,
                     any(key == 'spain_cortes_recount' for key, _, _ in rewards[focus_id]))


def check_seats(report, world):
    readers = flag_readers(world['cortes'])
    focuses = focus_blocks(world['focus'])
    loc = world['loc_focus']
    tooltip_rewards = {}
    for focus_id, body in focuses.items():
        for key, value, _ in reward_of(body):
            if key == 'custom_effect_tooltip' and value[0] == 'scalar' \
                    and value[1].endswith('_seats_tt'):
                tooltip_rewards.setdefault(value[1], []).append(focus_id)

    report.check('the tree carries the nine seat tooltips', len(tooltip_rewards) == 9,
                 'found %d: %r' % (len(tooltip_rewards), sorted(tooltip_rewards)))

    for tooltip, owners in tooltip_rewards.items():
        match = re.search(r'^\s*%s:\s*"(.*)"\s*$' % re.escape(tooltip), loc, re.MULTILINE)
        report.check('%s is defined once in the focus localisation' % tooltip,
                     match is not None and len(re.findall(r'^\s*%s:' % re.escape(tooltip), loc, re.MULTILINE)) == 1)
        if not match:
            continue
        promises = promised_seats(match.group(1))
        report.check('%s promises at least one party' % tooltip, bool(promises))
        for focus_id in owners:
            entries = reward_of(focuses[focus_id])
            flags = [flag for flag in flags_of(entries) if flag in readers]
            report.check('%s sets a flag the recount reads' % focus_id, bool(flags),
                         'flags %r' % (flags_of(entries),))
            report.check('%s recounts on completion' % focus_id,
                         any(key == 'spain_cortes_recount' for key, _, _ in entries))
            for flag in flags:
                deltas = readers[flag]
                for party, direction in promises:
                    actual = deltas.get(party)
                    report.check('%s: %s %s seats as promised' % (focus_id, party,
                                                                  'gains' if direction > 0 else 'loses'),
                                 actual is not None and actual * direction > 0,
                                 'recount moves %r for %s' % (actual, flag))
                for party, delta in deltas.items():
                    report.check('%s: the tooltip also mentions %s' % (focus_id, party),
                                 (party, 1 if delta > 0 else -1) in promises,
                                 'recount moves %r without a tooltip line' % (delta,))

    # The general rule behind those nine: a focus that sets a seat flag must recount itself,
    # because the completion hook is not this card's and the monthly recount is conditional.
    for focus_id, body in focuses.items():
        entries = reward_of(body)
        flags = [flag for flag in flags_of(entries) if flag in readers]
        if not flags:
            continue
        report.check('%s recounts the seats its flags move' % focus_id,
                     any(key == 'spain_cortes_recount' for key, _, _ in entries),
                     'flags %r' % (flags,))


def check_tooltips(report, world):
    focuses = focus_blocks(world['focus'])
    loc = world['loc_focus']
    report.equal('the officer-corps tooltip is defined once',
                 len(re.findall(r'^\s*%s:' % OFFICER_TOOLTIP, loc, re.MULTILINE)), 1)
    for focus_id in AFFECTED:
        entries = reward_of(focuses[focus_id])
        report.check('%s shows the officer-corps effect' % focus_id,
                     any(key == 'custom_effect_tooltip' and value[0] == 'scalar'
                         and value[1] == OFFICER_TOOLTIP for key, value, _ in entries))


AREAS = (
    ('helpers', check_helpers),
    ('affected focuses', check_affected_focuses),
    ('shared payload', check_trio),
    ('seats', check_seats),
    ('tooltips', check_tooltips),
)

# What each area must reject on the pre-repair tree.
MUTANT_EXPECTATIONS = {
    'helpers': ('spain_loyalty_gain_small', 'spain_loyalty_gain coup pressure'),
    'affected focuses': ('SPR1_royal_guard', 'SPR1_peninsular_reform'),
    'shared payload': ('SPR1_court_party',),
    'seats': ('SPR1_electoral_machine',),
    'tooltips': ('SPR1_royal_guard',),
}


def area_failures(function, world):
    report = base.Report(detail=False)
    function(report, world)
    return report.checks, report.failures


def main():
    detail = '--detail' in sys.argv
    live = load_world()
    checks = 0
    failures = []

    for name, function in AREAS:
        if detail:
            print('[%s]' % name)
        area_checks, area_fails = area_failures(function, live)
        checks += len(area_checks)
        failures.extend(area_fails)
        if detail:
            print('  %d checks in this area' % len(area_checks))

    # --- the negative control ------------------------------------------------------------------
    baseline = load_world(BASELINE_REV)
    mutant_fails = {}
    for name, function in AREAS:
        _, area_fails = area_failures(function, baseline)
        mutant_fails[name] = area_fails
        checks += 1
        if not area_fails:
            failures.append('negative control: %s passes on %s, so it discriminates nothing'
                            % (name, BASELINE_REV[:9]))
            continue
        wanted = MUTANT_EXPECTATIONS[name]
        missing = [token for token in wanted
                   if not any(token in failure for failure in area_fails)]
        checks += 1
        if missing:
            failures.append('negative control: %s does not reject %r on the pre-repair tree'
                            % (name, missing))
        if detail:
            print('  mutant [%s] %d failures, e.g. %s'
                  % (name, len(area_fails), area_fails[0]))

    print('%d checks, %d failures' % (checks, len(failures)))
    for failure in failures:
        print('  FAIL ' + failure)
    print('Read: ' + ', '.join(COVERED_FILES))
    print('Not performed: no game launch, no focus click, no coup roll, no tooltip rendered.')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
