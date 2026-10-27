"""Regression test: the coup meter moves in the direction the relief text promises.

`spain_military_loyalty` is a loyalty rating (high is good) and `spain_coup_pressure` is a risk
rating (high is bad: `spain_coup_risk` compares it with `coup_attempt_floor`, and
`spain_coup_check` multiplies the coup branch 1.50x at `coup_collapse`). The `coup_relief*`
constants in common/script_constants/spain_campaign.txt are therefore magnitudes that must be
SUBTRACTED from the risk meter.

S14 repaired the two officer-corps gain helpers in the Restoration chapter. Thirteen sites in
the other four chapters still added the same constants, so a player who garrisoned the cities,
amnestied the juntas or passed the army budget paid political power and equipment to move the
coup chance towards the coup. This test executes the shipped source to prove that all thirteen
now subtract, and that the deliberate raisers still add.

Asserted, from the files the game loads:

    1. the three relief constants resolve to 8 / 15 / 4 and no fourth `coup_relief*` name exists;
    2. each of the thirteen sites carries exactly one write of `spain_coup_pressure` that reads a
       relief constant, it is `subtract_from_variable`, and it reads the same constant it read
       before the repair;
    3. no scope anywhere in the six changed files adds a `coup_relief*` constant to the meter;
    4. every atomic site's fully expanded delta (loyalty helpers resolved into their constants)
       is negative; `spain_bill_concede_army` writes -5 directly, because it still pays its
       `coup_gain` on top of the relief its own comment describes, and `spain_bill_water_army`
       writes -4; the plot that fizzles sits in the 40-weight branch of `spain_coup_check` and
       never in the 60-weight coup branch;
    5. `spain_coup_outcome_dictatorship` still resets the meter to 0 and writes no relief;
    6. the deliberate raisers are untouched: the three `spain_loyalty_loss*` helpers and the two
       Restoration focuses that pay +6 loyalty loss with +3/+6 coup gain (+9 and +12 in total);
    7. the shipped player text agrees with that arithmetic. Event `spain_bills.4` is read from
       events/spain_cortes_bills.txt, and each option's `custom_effect_tooltip` is resolved in
       localisation/english/spain_cortes_bills_l_english.yml: the option that pays the Liberals'
       price (`spain_bills.4.b`) runs `spain_bill_concede_army`, so its text must say the coup
       pressure falls, must not carry the pre-repair "rises instead of falling" claim, and must
       keep the barracks suspicion. Every other key in that file is byte-identical to the
       pre-repair baseline, so the repair changed one tooltip and nothing else.

Negative controls, each of which must FAIL: the pre-repair tree at 62676fadc, an
additive-everywhere copy, a single-line flip back to `add_to_variable` at each of the thirteen
sites, a renamed relief constant, the pre-repair bill text and a copy with the corrected tooltip
key deleted.

Run from the repository root:

    python .tools/tests/test_spain_coup_relief_sign.py            # exit 0 = pass
    python .tools/tests/test_spain_coup_relief_sign.py --detail    # print every check

This is a source simulation. It proves what the script says, not what the engine does: no
decision was clicked, no focus completed, no coup rolled and no tooltip drawn, and the game was
never launched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_spain_cortes_recount as base  # noqa: E402
import test_spain_restoration_loyalty as loyalty  # noqa: E402  (tokeniser, parser, git reader)

Unsupported = loyalty.Unsupported

CONSTANTS = 'common/script_constants/spain_campaign.txt'
EFFECTS = 'common/scripted_effects/spain_campaign_effects.txt'
BILLS = 'common/scripted_effects/spain_cortes_bills.txt'
DECISIONS = 'common/decisions/spain_campaign.txt'
REPUBLIC = 'common/national_focus/spain_republic.txt'
POSTWAR = 'common/national_focus/spain_republic_postwar.txt'
RIVERA = 'common/national_focus/spain_rivera.txt'
RESTORATION = 'common/national_focus/spain_restoration.txt'
LOC_BILLS = 'localisation/english/spain_cortes_bills_l_english.yml'
EVENT_BILLS = 'events/spain_cortes_bills.txt'
PARTIES = 'common/scripted_effects/spain_cortes_parties.txt'

# The six files this repair owns, plus the Restoration tree it only reads.
MUTABLE = (DECISIONS, BILLS, EFFECTS, REPUBLIC, POSTWAR, RIVERA)
# Read to prove the shipped player text matches the shipped arithmetic.
READ_ONLY = (LOC_BILLS, EVENT_BILLS, PARTIES)
COVERED_FILES = MUTABLE + (CONSTANTS, RESTORATION) + READ_ONLY

# The tree the repair starts from: S14 integrated, all thirteen sites still additive.
BASELINE_REV = '62676fadc9ff6a528e8a4096be11de143b378420'

PRESSURE = 'spain_coup_pressure'
RELIEF_CONSTANTS = {
    'spain_campaign.coup_relief': 8.0,
    'spain_campaign.coup_relief_large': 15.0,
    'spain_campaign.bill_coup_relief_half': 4.0,
}

HELPERS = (
    'spain_loyalty_gain_small',
    'spain_loyalty_gain',
    'spain_loyalty_gain_large',
    'spain_loyalty_loss_small',
    'spain_loyalty_loss',
    'spain_loyalty_loss_large',
)

# file, kind, scope, relief constant the site already named, mode.
# mode 'net' asserts the whole block's expanded delta is negative; mode 'branch' asserts where
# inside a compound effect the relief sits, because that block carries unrelated pressure adds.
SITES = (
    (DECISIONS, 'block', 'SPR_garrison_the_cities', 'spain_campaign.coup_relief_large', 'net'),
    (DECISIONS, 'block', 'SPR_amnesty_for_the_juntas', 'spain_campaign.coup_relief', 'net'),
    (DECISIONS, 'block', 'SPR_secure_the_garrisons', 'spain_campaign.coup_relief_large', 'net'),
    (BILLS, 'block', 'spain_bill_pass_army', 'spain_campaign.coup_relief', 'net'),
    (BILLS, 'block', 'spain_bill_concede_army', 'spain_campaign.coup_relief', 'net'),
    (BILLS, 'block', 'spain_bill_water_army', 'spain_campaign.bill_coup_relief_half', 'net'),
    (EFFECTS, 'block', 'spain_coup_check', 'spain_campaign.coup_relief', 'branch'),
    (EFFECTS, 'block', 'spain_coup_outcome_failed', 'spain_campaign.coup_relief_large', 'net'),
    (REPUBLIC, 'focus', 'SPR3_public_order', 'spain_campaign.coup_relief', 'net'),
    (REPUBLIC, 'focus', 'SPR3_amnesty_1931', 'spain_campaign.coup_relief_large', 'net'),
    (POSTWAR, 'focus', 'SPR4_political_police', 'spain_campaign.coup_relief_large', 'net'),
    (RIVERA, 'focus', 'SPR2_army_reorganisation', 'spain_campaign.coup_relief', 'net'),
    (RIVERA, 'focus', 'SPR2_somaten', 'spain_campaign.coup_relief', 'net'),
)

# The two deliberate raisers the card protects, and the helper deltas they are built from.
RAISER_HELPER_NETS = {
    'spain_loyalty_loss_small': 3.0,
    'spain_loyalty_loss': 6.0,
    'spain_loyalty_loss_large': 6.0,
}
RAISER_FOCUSES = (
    ('SPR1_juntas_de_defensa', 9.0),
    ('SPR1_the_coup_that_waits', 12.0),
)

DICTATORSHIP = 'spain_coup_outcome_dictatorship'

# The army-budget event and the one option whose text this repair inverts.
BILL_EVENT = 'spain_bills.4'
CONCESSION_TOOLTIP = 'spain_bills.4.b.tt'
CONCESSION_OPTION = 'spain_bills.4.b'
INVERTED_PHRASE = 'rises instead of falling'

# option name -> (effect the option runs, direction its tooltip must state).
EXPECTED_OPTIONS = (
    ('spain_bills.4.a', 'spain_bill_pass_army', 'fall'),
    ('spain_bills.4.b', 'spain_bill_concede_army', 'fall'),
    ('spain_bills.4.c', 'spain_bill_water_army', 'fall'),
    ('spain_bills.4.e', 'spain_bill_fail_army', 'rise'),
)

# "coup pressure falls", not "stability falls ... coup pressure grows": the verb is read from the
# clause that actually names the meter.
COUP_CLAIM = re.compile(r'coup pressure\s+(falls|fall|rises|rise|grows|grow|climbs|climb|'
                        r'drops|drop|eases|ease)\b', re.IGNORECASE)
FALL_VERBS = ('falls', 'fall', 'drops', 'drop', 'eases', 'ease')


# ---------------------------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------------------------

def load_world(revision=None):
    """The six owned files plus everything read alongside them, as text, so mutants stay in memory."""
    return {
        'texts': {path: loyalty.read_text(path, revision)
                  for path in MUTABLE + (CONSTANTS, RESTORATION) + READ_ONLY},
        'constants': loyalty.parse_constants(loyalty.read_text(CONSTANTS, revision)),
    }


def structural_world(world, path, text):
    out = dict(world['texts'])
    out[path] = text
    return {'texts': out, 'constants': world['constants']}


def top_entries(text):
    entries, _ = loyalty.parse_block(loyalty.tokenize(text), 0)
    return entries


def walk(entries, path=()):
    """(key, value, line, path) for every node, descending every block."""
    for key, value, line in entries:
        yield key, value, line, path
        if value[0] == 'block':
            yield from walk(value[1], path + (key,))


def find_block_anywhere(entries, name):
    for key, value, line, _ in walk(entries):
        if key == name and value[0] == 'block':
            return value[1]
    raise Unsupported('block %s not found' % name)


def find_focus(entries, focus_id):
    for key, value, line, _ in walk(entries):
        if key != 'focus' or value[0] != 'block':
            continue
        try:
            if loyalty.scalar(value[1], 'id') == focus_id:
                return value[1]
        except Unsupported:
            continue
    raise Unsupported('focus %s not found' % focus_id)


def scope_of(text, kind, name):
    entries = top_entries(text)
    if kind == 'focus':
        return find_focus(entries, name)
    return find_block_anywhere(entries, name)


def amount_of(token, constants):
    return loyalty.amount_of(token, constants)


def is_relief(token):
    return isinstance(token, str) and 'coup_relief' in token


def pressure_writes(entries, constants, helpers=None, seen=()):
    """Every write of `spain_coup_pressure` in a scope, with helper calls expanded.

    Returns (op, signed amount, token, line, path). `op` is the raw command, so a caller can
    tell a subtraction from a paid addition; `set_variable` is kept at 0 because a reset is a
    direction of its own.
    """
    found = []
    for key, value, line, path in walk(entries):
        if key in ('add_to_variable', 'subtract_from_variable', 'set_variable') \
                and value[0] == 'block':
            body = value[1]
            if loyalty.optional_scalar(body, 'var') != PRESSURE:
                continue
            token = loyalty.optional_scalar(body, 'value')
            if key == 'set_variable':
                found.append((key, 0.0, token, line, path))
                continue
            amount = amount_of(token, constants)
            found.append((key, amount, token, line, path))
        elif helpers and key in helpers and value[0] == 'scalar' and value[1] == 'yes':
            if key in seen:
                raise Unsupported('recursive helper %s' % key)
            found.extend(pressure_writes(helpers[key], constants, helpers, seen + (key,)))
    return found


def delta(writes):
    """Unambiguous total for a meter, or None when the block resets it to zero."""
    if any(op == 'set_variable' for op, _, _, _, _ in writes):
        return None
    return sum((-1 if op == 'subtract_from_variable' else 1) * amount
               for op, amount, _, _, _ in writes)


def helper_bodies(effects_text):
    return {name: find_block_anywhere(top_entries(effects_text), name) for name in HELPERS}


def relief_write(entries, constants):
    """The single write that carries a relief constant, or Unsupported."""
    relief = [write for write in pressure_writes(entries, constants) if is_relief(write[2])]
    if len(relief) != 1:
        raise Unsupported('%d relief writes, expected exactly one' % len(relief))
    return relief[0]


def normalise(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


def localisation(text):
    """key -> (value, line) for a flat English localisation file."""
    entries = {}
    for index, line in enumerate(normalise(text).split('\n'), 1):
        match = re.match(r'^\s*([A-Za-z0-9_.\-]+):\s*"(.*)"\s*$', line)
        if match:
            entries[match.group(1)] = (match.group(2), index)
    return entries


def event_block(entries, event_id):
    for key, value, line, _ in walk(entries):
        if key != 'country_event' or value[0] != 'block':
            continue
        try:
            if loyalty.scalar(value[1], 'id', line) == event_id:
                return value[1]
        except Unsupported:
            continue
    raise Unsupported('event %s not found' % event_id)


def event_options(text, event_id=BILL_EVENT):
    """(name, tooltip key, effect the option runs, line) for every option of a bill event."""
    options = []
    for key, value, line in event_block(top_entries(text), event_id):
        if key != 'option' or value[0] != 'block':
            continue
        name = loyalty.scalar(value[1], 'name', line)
        tooltip = loyalty.optional_scalar(value[1], 'custom_effect_tooltip')
        effect = None
        for inner_key, inner_value, _ in value[1]:
            if inner_value[0] == 'scalar' and inner_value[1] == 'yes' \
                    and inner_key.startswith('spain_bill_') and inner_key.endswith(('army', 'budget')):
                effect = inner_key
        options.append((name, tooltip, effect, line))
    return options


def stated_direction(text):
    """What the player text claims about the coup meter, or None when it claims nothing."""
    match = COUP_CLAIM.search(text)
    if not match:
        return None
    return 'fall' if match.group(1).lower() in FALL_VERBS else 'rise'


def calls(entries, name):
    return any(key == name and value[0] == 'scalar' and value[1] == 'yes'
               for key, value, _ in entries)


def raw_block(text, name, span=30):
    """The source lines from `name = {` downwards, for assertions about a guard's meaning."""
    lines = normalise(text).split('\n')
    for index, line in enumerate(lines):
        if line.strip().startswith(name + ' = {'):
            return '\n'.join(lines[index:index + span])
    raise Unsupported('block %s not found in raw text' % name)


# ---------------------------------------------------------------------------------------------
# Areas
# ---------------------------------------------------------------------------------------------

def check_constants(report, world):
    report.start('constants')
    relief = {name: value for name, value in world['constants'].items() if 'coup_relief' in name}
    report.equal('the relief constants are exactly the three the card names', relief,
                 RELIEF_CONSTANTS)
    report.check('no fourth relief constant was introduced',
                 set(relief) == set(RELIEF_CONSTANTS), 'found %r' % sorted(relief))


def check_sites(report, world):
    report.start('sites')
    constants = world['constants']
    helpers = helper_bodies(world['texts'][EFFECTS])
    for path, kind, name, constant, mode in SITES:
        label = '%s (%s)' % (name, constant.split('.')[-1])
        try:
            entries = scope_of(world['texts'][path], kind, name)
            op, amount, token, line, at = relief_write(entries, constants)
        except Unsupported as error:
            report.check('%s subtracts its relief' % label, False, str(error))
            continue
        report.check('%s subtracts its relief' % label, op == 'subtract_from_variable',
                     'line %d: %s' % (line, op))
        report.equal('%s reads the constant it named' % label, token, 'constant:' + constant)
        report.equal('%s magnitude' % label, amount, RELIEF_CONSTANTS[constant])
        direct = delta(pressure_writes(entries, constants))
        if mode == 'branch':
            report.check('%s sits in the branch that ends the plot' % label,
                         '40' in at and '60' not in at, 'path %r' % (at,))
            continue
        expanded = delta(pressure_writes(entries, constants, helpers))
        report.check('%s lowers coup pressure overall' % label,
                     expanded is not None and expanded < 0, 'expanded delta %r' % (expanded,))
        report.check('%s lowers coup pressure on its own lines' % label,
                     direct is not None and direct < 0, 'direct delta %r' % (direct,))

    # The two sums the card names, stated as the arithmetic of the block rather than as a sign.
    concede = scope_of(world['texts'][BILLS], 'block', 'spain_bill_concede_army')
    report.equal('spain_bill_concede_army nets -5 before its loyalty helper',
                 delta(pressure_writes(concede, constants)), -5.0)
    water = scope_of(world['texts'][BILLS], 'block', 'spain_bill_water_army')
    report.equal('spain_bill_water_army nets -4 before its loyalty helper',
                 delta(pressure_writes(water, constants)), -4.0)


def check_no_additive_relief(report, world):
    report.start('no additive relief')
    constants = world['constants']
    additive = []
    for path in MUTABLE:
        for key, value, line, where in walk(top_entries(world['texts'][path])):
            if key != 'add_to_variable' or value[0] != 'block':
                continue
            if loyalty.optional_scalar(value[1], 'var') != PRESSURE:
                continue
            token = loyalty.optional_scalar(value[1], 'value')
            if is_relief(token):
                additive.append('%s:%d %s' % (path, line, token))
    report.equal('no file adds a relief constant to the coup meter', additive, [])

    # Every relief write in the six files is a subtraction, wherever it lives.
    wrong = []
    for path in MUTABLE:
        for op, amount, token, line, where in pressure_writes(
                top_entries(world['texts'][path]), constants):
            if is_relief(token) and op != 'subtract_from_variable':
                wrong.append('%s:%d %s' % (path, line, op))
    report.equal('every relief write is a subtraction', wrong, [])


def check_raisers(report, world):
    report.start('raisers')
    constants = world['constants']
    helpers = helper_bodies(world['texts'][EFFECTS])
    for name, expected in RAISER_HELPER_NETS.items():
        net = delta(pressure_writes(helpers[name], constants))
        report.equal('%s still feeds the coup meter' % name, net, expected)
    restoration = world['texts'][RESTORATION]
    for focus_id, expected in RAISER_FOCUSES:
        entries = scope_of(restoration, 'focus', focus_id)
        net = delta(pressure_writes(entries, constants, helpers))
        report.equal('%s still raises the coup meter' % focus_id, net, expected)


def check_reset(report, world):
    report.start('reset')
    constants = world['constants']
    entries = scope_of(world['texts'][EFFECTS], 'block', DICTATORSHIP)
    writes = pressure_writes(entries, constants)
    report.check('%s still resets the coup meter' % DICTATORSHIP,
                 len(writes) == 1 and writes[0][0] == 'set_variable' and writes[0][2] == '0',
                 'writes %r' % (writes,))
    report.check('%s writes no relief constant' % DICTATORSHIP,
                 not any(is_relief(write[2]) for write in writes), 'writes %r' % (writes,))


def check_player_text(report, world):
    """The shipped bill text must state the direction the shipped code produces."""
    report.start('bill text')
    constants = world['constants']
    helpers = helper_bodies(world['texts'][EFFECTS])
    loc = localisation(world['texts'][LOC_BILLS])
    options = event_options(world['texts'][EVENT_BILLS])

    report.equal('the army budget offers the four options this repair reads',
                 [option[0] for option in options], [option[0] for option in EXPECTED_OPTIONS])

    seen = {}
    for name, tooltip, effect, line in options:
        expected = dict((option[0], option[1:]) for option in EXPECTED_OPTIONS).get(name)
        if expected is None:
            report.check('%s is an option this test knows' % name, False, 'option at line %d' % line)
            continue
        expected_effect, expected_direction = expected
        seen[name] = (tooltip, effect, expected_direction)
        report.equal('%s runs the effect its text describes' % name, effect, expected_effect)
        report.check('%s has a custom effect tooltip' % name, tooltip is not None,
                     'option at line %d' % line)
        if tooltip is None or tooltip not in loc:
            report.check('%s tooltip resolves' % name, tooltip in loc, 'key %r' % (tooltip,))
            continue
        text = loc[tooltip][0]
        report.equal('%s says the coup pressure %ss' % (name, expected_direction),
                     stated_direction(text), expected_direction)

        entries = scope_of(world['texts'][BILLS], 'block', expected_effect)
        if expected_effect == 'spain_bill_fail_army':
            # Withdrawing the budget charges the government, and only a minority government is
            # where that strain reaches the coup meter. The claim is conditional, and this is the
            # path it names.
            report.equal('%s writes no coup pressure of its own' % expected_effect,
                         delta(pressure_writes(entries, constants)), 0.0)
            report.check('%s charges the government' % expected_effect,
                         calls(entries, 'spain_bill_penalise_government'), repr(entries)[:80])
            strain = scope_of(world['texts'][PARTIES], 'block', 'spain_government_strain')
            growth = [write for write in pressure_writes(strain, constants)
                      if write[0] == 'add_to_variable']
            report.equal('the growth an unpaid army promises is +minority_coup',
                         [write[1] for write in growth],
                         [constants['spain_campaign.minority_coup']])
            report.check('that growth sits in the minority-government branch',
                         bool(growth) and 'if' in growth[0][4]
                         and 'spain_government_majority' in raw_block(world['texts'][PARTIES],
                                                                     'spain_government_strain'),
                         'path %r' % (growth[0][4] if growth else None,))
            continue
        net = delta(pressure_writes(entries, constants, helpers))
        report.check('%s really moves the meter the way its text says' % expected_effect,
                     net is not None and net < 0, 'expanded delta %r' % (net,))

    # The specific inversion QA caught: the concession still nets -5, so its tooltip must say so.
    tooltip, effect, direction = seen.get(CONCESSION_OPTION, (None, None, None))
    report.equal('the concession option carries the corrected tooltip', tooltip, CONCESSION_TOOLTIP)
    report.equal('the concession option still runs the concession', effect, 'spain_bill_concede_army')
    corrected = loc.get(CONCESSION_TOOLTIP, ('', 0))[0]
    report.equal('the corrected text states a fall', stated_direction(corrected), 'fall')
    report.check('the corrected text drops "rises instead of falling"',
                 INVERTED_PHRASE not in corrected.lower(), repr(corrected[:120]))
    report.check('the corrected text keeps the barracks suspicion',
                 'insulted' in corrected.lower() and 'barracks' in corrected.lower(),
                 repr(corrected[:120]))

    # Scope: only that one tooltip may differ from the pre-repair text.
    baseline = localisation(loyalty.read_text(LOC_BILLS, BASELINE_REV))
    report.equal('the localisation keeps exactly its pre-repair keys', sorted(loc), sorted(baseline))
    changed = sorted(key for key in loc if key in baseline and loc[key][0] != baseline[key][0])
    report.equal('only the concession tooltip differs from the pre-repair text', changed,
                 [CONCESSION_TOOLTIP])


AREAS = (
    ('constants', check_constants),
    ('sites', check_sites),
    ('no additive relief', check_no_additive_relief),
    ('raisers', check_raisers),
    ('reset', check_reset),
    ('bill text', check_player_text),
)


# ---------------------------------------------------------------------------------------------
# Mutants
# ---------------------------------------------------------------------------------------------

def area_failures(function, world):
    report = base.Report(detail=False)
    try:
        function(report, world)
    except Unsupported as error:
        report.check('%s can read the world' % function.__name__, False, str(error))
    return report.checks, report.failures


def failure_text(failures):
    return ' | '.join(failures)


def flips_to_additive(world):
    """Every relief subtraction in all six files turned back into an addition."""
    texts = {}
    for path in MUTABLE:
        text = world['texts'][path]
        lines = text.split('\n')
        for index, line in enumerate(lines):
            if 'subtract_from_variable = { var = %s value = constant:spain_campaign' % PRESSURE \
                    not in line or 'coup_relief' not in line:
                continue
            lines[index] = line.replace('subtract_from_variable', 'add_to_variable', 1)
        texts[path] = '\n'.join(lines)
    return {'texts': texts, 'constants': world['constants']}


def flip_one_site(world, path, line_number):
    lines = world['texts'][path].split('\n')
    old = lines[line_number - 1]
    if 'subtract_from_variable' not in old:
        raise Unsupported('line %d is not a subtraction: %r' % (line_number, old))
    lines[line_number - 1] = old.replace('subtract_from_variable', 'add_to_variable', 1)
    return structural_world(world, path, '\n'.join(lines))


def renamed_constant(world):
    constants = dict(world['constants'])
    if 'spain_campaign.coup_relief' in constants:
        constants.pop('spain_campaign.coup_relief')
    constants['spain_campaign.coup_relief_renamed'] = 8.0
    return {'texts': world['texts'], 'constants': constants}


def pre_repair_text(world):
    """Only the localisation reverts, so the tooltip is the sole cause of the failure."""
    return structural_world(world, LOC_BILLS, loyalty.read_text(LOC_BILLS, BASELINE_REV))


def deleted_tooltip(world):
    lines = normalise(world['texts'][LOC_BILLS]).split('\n')
    kept = [line for line in lines if not line.strip().startswith(CONCESSION_TOOLTIP + ':')]
    if len(kept) == len(lines):
        raise Unsupported('cannot delete %s' % CONCESSION_TOOLTIP)
    return structural_world(world, LOC_BILLS, '\n'.join(kept))


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
            print('  %d checks in this area, %d failures' % (len(area_checks), len(area_fails))
                  + ('' if area_fails else ''))
            if name == 'sites':
                constants = live['constants']
                helpers = helper_bodies(live['texts'][EFFECTS])
                for path, kind, scope, constant, mode in SITES:
                    entries = scope_of(live['texts'][path], kind, scope)
                    direct_net = delta(pressure_writes(entries, constants))
                    expanded = delta(pressure_writes(entries, constants, helpers))
                    print('    %-32s %-8s direct %6r  expanded %6r'
                          % (scope, mode, direct_net, expanded))
            if name == 'bill text':
                loc = localisation(live['texts'][LOC_BILLS])
                for option, effect, _ in EXPECTED_OPTIONS:
                    claimed = stated_direction(loc.get(option + '.tt', ('<no tooltip>', 0))[0])
                    print('    %-16s %-26s text claims %-6r' % (option, effect, claimed))

    # --- the shipped defect ---------------------------------------------------------------------
    baseline = load_world(BASELINE_REV)
    _, baseline_site_failures = area_failures(check_sites, baseline)
    text = failure_text(baseline_site_failures)
    checks += 1
    missing = [site[2] for site in SITES if site[2] not in text]
    if missing:
        failures.append('negative control: the pre-repair tree at %s does not reject %r'
                        % (BASELINE_REV[:9], missing))
    _, baseline_additive = area_failures(check_no_additive_relief, baseline)
    checks += 1
    if not baseline_additive:
        failures.append('negative control: the additive-relief area passes on %s'
                        % BASELINE_REV[:9])
    # The constants and the deliberate raisers did not move, so they must pass on both trees.
    for name, function in (('constants', check_constants), ('raisers', check_raisers),
                           ('reset', check_reset)):
        _, baseline_fails = area_failures(function, baseline)
        checks += 1
        if baseline_fails:
            failures.append('negative control: %s fails on %s, so this repair is not what it '
                            'tests: %s' % (name, BASELINE_REV[:9], failure_text(baseline_fails)))
    if detail:
        print('  mutant [pre-repair tree] %d site failures, e.g. %s'
              % (len(baseline_site_failures), baseline_site_failures[0]))

    # --- additive everywhere --------------------------------------------------------------------
    additive = flips_to_additive(live)
    _, additive_fails = area_failures(check_sites, additive)
    checks += 1
    text = failure_text(additive_fails)
    missing = [site[2] for site in SITES if site[2] not in text]
    if missing:
        failures.append('negative control: an additive-everywhere copy does not reject %r'
                        % (missing,))
    _, additive_area = area_failures(check_no_additive_relief, additive)
    checks += 1
    if not additive_area:
        failures.append('negative control: the additive-relief area passes on an additive copy')
    if detail:
        print('  mutant [additive everywhere] %d site failures, %d additive findings'
              % (len(additive_fails), len(additive_area)))

    # --- one site at a time ---------------------------------------------------------------------
    flipped = 0
    for path, kind, scope, constant, mode in SITES:
        entries = scope_of(live['texts'][path], kind, scope)
        _, _, _, line, _ = relief_write(entries, live['constants'])
        mutant = flip_one_site(live, path, line)
        _, mutant_fails = area_failures(check_sites, mutant)
        checks += 1
        if not any(scope in failure for failure in mutant_fails):
            failures.append('negative control: flipping %s back to add_to_variable is not '
                            'rejected' % scope)
        else:
            flipped += 1
    if detail:
        print('  mutant [single-site flips] %d of %d sites rejected by name' % (flipped, len(SITES)))

    # --- a renamed constant ---------------------------------------------------------------------
    renamed = renamed_constant(live)
    _, renamed_sites = area_failures(check_sites, renamed)
    _, renamed_constants = area_failures(check_constants, renamed)
    checks += 1
    if not renamed_sites or not renamed_constants:
        failures.append('negative control: renaming coup_relief is not rejected '
                        '(sites %d, constants %d)' % (len(renamed_sites), len(renamed_constants)))
    if detail:
        print('  mutant [renamed constant] %d site failures, %d constant failures'
              % (len(renamed_sites), len(renamed_constants)))

    # --- the shipped bill text ------------------------------------------------------------------
    for label, mutant in (('pre-repair text', pre_repair_text(live)),
                          ('deleted tooltip key', deleted_tooltip(live))):
        _, text_fails = area_failures(check_player_text, mutant)
        checks += 1
        if not any(CONCESSION_OPTION in failure for failure in text_fails):
            failures.append('negative control: the %s mutant is not rejected at %s'
                            % (label, CONCESSION_OPTION))
        if detail:
            print('  mutant [%s] %d text failures, e.g. %s'
                  % (label, len(text_fails), text_fails[0] if text_fails else 'none'))

    print('%d checks, %d failures' % (checks, len(failures)))
    for failure in failures:
        print('  FAIL ' + failure)
    print('Read: ' + ', '.join(COVERED_FILES))
    print('Not performed: no game launch, no decision clicked, no focus completed, no coup '
          'rolled, no tooltip rendered.')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
