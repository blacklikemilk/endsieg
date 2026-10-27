"""Regression test: the Restoration turno appoints a government and runs its ministerial crisis.

Before this card no focus, decision, event or scripted effect appointed a governing party:
`spain_government_party` was only reset and then defaulted from the chapter flag, so an election
could swing the chamber against a government that could never be replaced. The five facts this
card is responsible for are asserted against the shipped source:

    1. `spain_appoint_government` sets the governing party, the two coalition partners and the
       change counter, recounts the bloc, refreshes the panel and the hemicycle, and opens or
       closes the ministerial crisis on the resulting 201-seat test. It is a no-op outside
       `spain_restoration_cortes_live`.
    2. `spain_encasillado` transfers 18 raw support points out of four named blocs into the
       governing party, so the design's seat table 129 -> 188 -> 245 -> 304 is reproduced by the
       shipped effect at patronage 0/6/12/18 and one act alone never carries a majority.
    3. The three doors are priced in existing values: the encasillado in patronage and donors,
       the honest election in `election_cost` and the existing `spain_hold_election`, the decree
       in `pp_large`, Crown balance, loyalty and coup pressure. No seat moves under the decree.
    4. Rot has a reader: at or above `patronage_rot` the monthly upkeep feeds the republicans and
       the carlists and raises coup pressure.
    5. The mission `SPR_ministerial_crisis` sits inside `SPR_crown_and_cortes_category`, runs only
       while the crisis is open, completes on a 201-seat bloc, and times out into
       `spain_campaign.32`, where the Crown draws up the lists itself.
    6. `spain_encasillado` pays the party that governs and nobody else. Each of the seven appointed
       parties 1..7 keeps office through the draw, a chamber with no party named yet falls back to
       the monarchists, and only that one party receives the transfer.

The S12a correction (card t_47329669) made the comparisons behind fact 6 explicit. The party
fallback, the seven beneficiary selectors and the monthly minority test all omitted `compare`,
which the offline wiki (`Data structures`, `check_variable` row) documents as
`greater_than_or_equals`: every appointed party 2..7 was reset to the monarchists and the seven
selectors became multi-recipient `>=` branches, while a majority government was charged the
minority penalty every month. `test_party_identity`, `test_monthly_minority` and
`test_correction_mutants` hold the repair in place: the exact pre-correction file is rebuilt from
the shipped one and must fail those checks, a mutant that repairs only the zero-party fallback must
fail them too, and the patronage clamp is exercised from a reachable high-patronage state rather
than only from three draws from zero.

The S12b finishing card (t_00b07993) closed the two comparisons that stayed implicit after S12a:
`spain_government_strain` and the incumbent-loss `OR` inside `spain_hold_election` also read
`check_variable = { var = spain_government_majority value = 0 }` without a comparison, so every
government — a genuine 245-seat majority included — was charged the minority strain and lost
incumbent support at every election. `strain_failures`, `incumbent_failures` and the two
single-block mutants in `test_residual_comparisons` hold that repair in place, and each mutant
proves that one comparison's test is independent of the other's.

The test executes the real script. It reuses the tokeniser, parser, simulator and seat arithmetic
of `.tools/tests/test_spain_cortes_recount.py` (S9): `spain_cortes_recount` is the shipped effect,
so the seats under test are the numbers the mod computes, not a restatement of them. Scripted
effect parameters are substituted, macros (`@name`) resolved, and the `spain_campaign_effects.txt`
loyalty and balance helpers run from their real bodies rather than stubbed.

Two mutant controls must fail: the pre-card parties file (no `spain_encasillado` at all) and a
shadow of the shipped file with the crisis-opening line removed, which must break the seat-table
crisis assertion while leaving the seats intact.

Run from the repository root:

    python .tools/tests/test_spain_turno.py            # exit 0 = pass
    python .tools/tests/test_spain_turno.py --detail   # print every check

This is a source simulation. It proves what the script says, not what the engine does: no
decision was clicked, no mission rendered, no event shown and the game was never launched.
"""

from __future__ import annotations

import collections
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_spain_cortes_recount as base  # noqa: E402  (the S9 harness, reused on purpose)

PARTIES_PATH = 'common/scripted_effects/spain_cortes_parties.txt'
TRIGGERS_PATH = 'common/scripted_triggers/spain_campaign_triggers.txt'
CAMPAIGN_PATH = 'common/scripted_effects/spain_campaign_effects.txt'
CONSTANTS_PATH = 'common/script_constants/spain_campaign.txt'
DECISIONS_PATH = 'common/decisions/spain_campaign.txt'
EVENTS_PATH = 'events/spain_campaign.txt'
LOC_PATH = 'localisation/english/spain_campaign_l_english.yml'

PARTIES = base.PARTIES

# The pre-card file, pinned by full object name: a mutable HEAD stops being a mutant the moment
# the repair is committed. 62676fadc is the integration commit this card was released on.
BASELINE_REV = '62676fadc9ff6a528e8a4096be11de143b378420'

# Effects the recount family owns: executed by the S9 harness, which already models them.
RECOUNT_CALLS = frozenset(('spain_cortes_recount', 'spain_cortes_refresh_display',
                           'spain_cortes_redraw_hemicycle'))

MISSION = 'SPR_ministerial_crisis'
CATEGORY = 'SPR_crown_and_cortes_category'
ROUTES = ('SPR_encasillado', 'SPR_honest_election', 'SPR_royal_decree')
EXISTING = ('SPR_court_appointments', 'SPR_royal_progress', 'SPR_budget_offensive',
            'SPR_parliamentary_inquiry', 'SPR_force_an_election')

# The design's table (S2 R1): act, patronage, machine raw, monarchist seats, donors l/c/r/s.
SEAT_TABLE = (
    (0, 0, 40, 129, (30, 25, 15, 8)),
    (1, 6, 58, 188, (23, 20, 11, 6)),
    (2, 12, 76, 245, (16, 15, 7, 4)),
    (3, 18, 94, 304, (9, 10, 3, 2)),
)


# The comparison operators the parser produces for `key < value` spellings. `has_stability < X` in
# the incumbent-loss OR is the only one the turno tests evaluate; the rest are listed so the trigger
# handler fails on an operator it does not model instead of silently treating it as false.
COMPARISONS = {
    '<': lambda left, right: left < right,
    '<=': lambda left, right: left <= right,
    '>': lambda left, right: left > right,
    '>=': lambda left, right: left >= right,
    '=': lambda left, right: left == right,
}


# ---------------------------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------------------------

def read_text(path):
    with open(ROOT / path, 'r', encoding='utf-8-sig') as handle:
        return handle.read()


def tokens_of(text):
    entries, _ = base.parse_block(base.tokenize(text), 0)
    return entries


def blocks(entries, key):
    """Every block-valued entry with this key, in document order (repeated keys survive)."""
    return [value[1] for entry_key, value, _ in entries
            if entry_key == key and value[0] == 'block']


def entry(entries, key):
    for entry_key, value, line in entries:
        if entry_key == key:
            return value, line
    raise KeyError(key)


def block_of(entries, key):
    value, line = entry(entries, key)
    if value[0] != 'block':
        raise AssertionError('%s is not a block at line %d' % (key, line))
    return value[1]


def scalar_of(entries, key):
    value, line = entry(entries, key)
    if value[0] != 'scalar':
        raise AssertionError('%s is not a scalar at line %d' % (key, line))
    return value[1]


def named(parsed, name):
    """A top-level block by name: `base.parse_file` stores (block, line) per key."""
    return parsed[name][0]


def has(entries, key):
    return any(entry_key == key for entry_key, _, _ in entries)


def replace_tokens(text, params):
    if not params or '$' not in text:
        return text
    return re.sub(r'\$([A-Za-z0-9_]+)\$',
                  lambda match: str(params.get(match.group(1), match.group(0))), text)


def substitute_value(value, params):
    kind, payload = value
    if kind == 'scalar':
        return (kind, replace_tokens(payload, params))
    if kind == 'block':
        return (kind, substitute(payload, params))
    if kind == 'compare':
        return (kind, (payload[0], replace_tokens(payload[1], params)))
    return value


def substitute(entries, params):
    """Scripted-effect parameters are textual, so they are replaced before anything is evaluated."""
    if not params:
        return entries
    return [(key, substitute_value(value, params), line) for key, value, line in entries]


# ---------------------------------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------------------------------

class TurnoState(base.State):
    """The S9 state plus what the campaign helpers write."""

    def __init__(self):
        base.State.__init__(self)
        self.power_balances = set()
        self.political_power = 0.0
        self.stability = 0.0
        self.war_support = 0.0
        self.bop = collections.Counter()
        self.tooltips = []
        self.events = []
        self.hold_elections = 0


class Turno:
    """Executes the turno's real script: parameters, macros, scripted triggers and all."""

    def __init__(self, overrides=None):
        overrides = overrides or {}
        self.raw = {
            'parties': overrides.get(PARTIES_PATH, read_text(PARTIES_PATH)),
            'triggers': overrides.get(TRIGGERS_PATH, read_text(TRIGGERS_PATH)),
            'campaign': overrides.get(CAMPAIGN_PATH, read_text(CAMPAIGN_PATH)),
            'decisions': overrides.get(DECISIONS_PATH, read_text(DECISIONS_PATH)),
            'events': overrides.get(EVENTS_PATH, read_text(EVENTS_PATH)),
        }
        self.constants = base.load_constants()
        self.macros = {}
        for text in self.raw.values():
            for match in re.finditer(r'^@([A-Za-z0-9_]+)\s*=\s*(-?[0-9.]+)\s*$', text, re.M):
                self.macros[match.group(1)] = float(match.group(2))
        self.parsed = {key: base.parse_file(text) for key, text in self.raw.items()}
        self.recount = base.Script(constants=self.constants)
        self.compiled = {}

    # ---- effects ---------------------------------------------------------------------------

    def effect(self, name, params=None):
        return named(self.parsed['parties'], name) if name in self.parsed['parties'] else None

    def run(self, name, state, params=None):
        block = self.effect(name)
        if block is None:
            block = named(self.parsed['campaign'], name) if name in self.parsed['campaign'] else None
        if block is None:
            raise base.Unsupported('cannot resolve scripted effect %s' % name)
        self.run_entries(block, state, params or {})

    def run_entries(self, entries, state, params):
        entries = substitute(entries, params)
        index = 0
        while index < len(entries):
            key, value, line = entries[index]
            index += 1
            if key == 'if':
                branches = [(block_of(value[1], 'limit'),
                             [item for item in value[1] if item[0] != 'limit'])]
                otherwise = None
                while index < len(entries) and entries[index][0] in ('else_if', 'else'):
                    chain_key, chain_value, chain_line = entries[index]
                    index += 1
                    if chain_key == 'else_if':
                        branches.append((block_of(chain_value[1], 'limit'),
                                         [item for item in chain_value[1] if item[0] != 'limit']))
                    else:
                        otherwise = chain_value[1]
                for trigger, body in branches:
                    if self.trigger(trigger, state, params):
                        self.run_entries(body, state, params)
                        break
                else:
                    if otherwise is not None:
                        self.run_entries(otherwise, state, params)
                continue
            if key in ('else_if', 'else'):
                raise base.Unsupported('%s outside a chain at line %d' % (key, line))
            self.run_one(key, value, line, state, params)

    def run_one(self, key, value, line, state, params):
        if key in base.VAR_OPS:
            body = value[1]
            target = scalar_of(body, 'var')
            amount = self.value(scalar_of(body, 'value'), state, params)
            kind = base.VAR_OPS[key]
            current = state.vars.get(target, 0)
            if kind == 'set':
                state.vars[target] = amount
            elif kind == 'add':
                state.vars[target] = current + amount
            elif kind == 'sub':
                state.vars[target] = current - amount
            elif kind == 'mul':
                state.vars[target] = current * amount
            elif kind == 'div':
                state.vars[target] = current / amount
            return
        if key == 'clamp_variable':
            body = value[1]
            target = scalar_of(body, 'var')
            low = self.value(scalar_of(body, 'min'), state, params)
            high = self.value(scalar_of(body, 'max'), state, params)
            state.vars[target] = max(min(state.vars.get(target, 0), high), low)
            return
        if key == 'round_variable':
            state.vars[value[1]] = base.round_half_away_from_zero(state.vars.get(value[1], 0))
            return
        if key == 'if':
            raise base.Unsupported('if must be consumed by run_entries at line %d' % line)
        if key == 'hidden_effect':
            self.run_entries(value[1], state, params)
            return
        if key == 'custom_effect_tooltip':
            if value[0] == 'block':
                state.tooltips.append(scalar_of(value[1], 'tooltip'))
            else:
                state.tooltips.append(value[1])
            return
        if key == 'set_country_flag':
            state.flags.add(value[1])
            return
        if key == 'clr_country_flag':
            state.flags.discard(value[1])
            return
        if key in ('add_political_power', 'add_stability', 'add_war_support'):
            amount = self.value(value[1], state, params)
            if key == 'add_political_power':
                state.political_power += amount
            elif key == 'add_stability':
                state.stability += amount
            else:
                state.war_support += amount
            return
        if key == 'add_power_balance_value':
            body = value[1]
            state.bop[scalar_of(body, 'id')] += self.value(scalar_of(body, 'value'), state, params)
            return
        if key == 'country_event':
            state.events.append(scalar_of(value[1], 'id'))
            return
        # ---- a call: scalar (`x = yes`) or block with parameters
        if value[0] == 'scalar':
            if key in RECOUNT_CALLS:
                self.recount.run(key, state)
            elif key == 'spain_government_recount':
                self.run(key, state)
            elif key == 'spain_hold_election':
                state.hold_elections += 1
                state.calls['spain_hold_election'] += 1
                self.recount.run('spain_cortes_recount', state)
            else:
                state.calls[key] += 1
                self.run(key, state)
            return
        params = dict((param.upper(), param_value[1]) for param, param_value, _ in value[1]
                      if param_value[0] == 'scalar')
        state.calls[key] += 1
        self.run(key, state, params)

    def value(self, token, state, params):
        text = str(token)
        if text.startswith('$') and text.endswith('$') and len(text) > 2:
            name = text[1:-1]
            if name not in params:
                raise base.Unsupported('unpassed scripted-effect parameter %s' % name)
            text = params[name]
            return base.eval_value(text, state, self.constants)
        if text.startswith('@'):
            name = text[1:]
            if name not in self.macros:
                raise base.Unsupported('unknown macro %s' % text)
            return self.macros[name]
        return base.eval_value(text, state, self.constants)

    # ---- triggers --------------------------------------------------------------------------

    def trigger(self, entries, state, params=None):
        # base.parse_block yields (key, value, line); base.compile_trigger yields (key, value),
        # which is the shape base.eval_entry and the recursion below expect.
        entries = substitute(entries, params or {})
        compiled = entries if not entries or len(entries[0]) == 2 else base.compile_trigger(entries)
        return all(self.trigger_one(key, value, state, params or {})
                   for key, value in compiled)

    def trigger_one(self, key, value, state, params):
        if key in ('OR', 'AND', 'NOT'):
            results = [self.trigger_one(child_key, child_value, state, params)
                       for child_key, child_value in value]
            if key == 'AND':
                return all(results)
            if key == 'OR':
                return any(results)
            return not all(results)
        if key == 'hidden_trigger':
            return self.trigger(value, state, params)
        if key == 'custom_trigger_tooltip':
            tooltip = [item for item in value if item[0] == 'tooltip']
            if tooltip:
                state.tooltips.append(tooltip[0][1])
            return self.trigger([item for item in value if item[0] != 'tooltip'], state, params)
        if key in self.parsed['triggers']:
            return self.trigger(named(self.parsed['triggers'], key), state, params)
        if key == 'has_stability':
            # the incumbent-loss OR's second branch, `has_stability < constant:...`: the parsed value
            # is the (operator, operand) pair, and stability is the 0..1 fraction the engine compares.
            if not isinstance(value, tuple) or value[0] not in COMPARISONS:
                raise base.Unsupported('has_stability without a comparison at any line')
            return COMPARISONS[value[0]](state.stability,
                                         self.value(value[1], state, params))
        if key == 'has_power_balance':
            return dict(value).get('id') in state.power_balances
        return base.eval_entry(key, value, state, self.constants)


# ---------------------------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------------------------

def restoration(turno, chapter='spain_chapter_restoration', balance=True, coup=False,
                patronage=0, encasillados=0, shifts=None, party=1):
    state = TurnoState()
    for name in PARTIES:
        state.vars['spain_party_shift_' + name] = (shifts or {}).get(name, 0)
    state.flags.add(chapter)
    if coup:
        state.flags.add('spain_coup_in_progress')
    if balance:
        state.power_balances.add('SPR_crown_and_cortes')
    state.vars['spain_government_party'] = party
    state.vars['spain_coalition_1'] = 0
    state.vars['spain_coalition_2'] = 0
    state.vars['spain_government_changes'] = 0
    state.vars['spain_encasillados'] = encasillados
    state.vars['spain_crown_patronage'] = patronage
    state.vars['spain_coup_pressure'] = 0
    state.vars['spain_military_loyalty'] = 55
    turno.recount.run('spain_cortes_recount', state)
    return state


def seats(state, party='monarchists'):
    return state.vars['spain_cortes_seats_' + party]


def shifts(state, party):
    return state.vars.get('spain_party_shift_' + party, 0)


def crisis_open(state):
    return 'spain_ministry_crisis_open' in state.flags


def seat_table_failures(turno):
    """Run the shipped encasillado three times and return every contradiction with the design."""
    problems = []
    state = restoration(turno)
    act, patronage, machine_raw, bench, donors = SEAT_TABLE[0]
    if seats(state) != bench:
        problems.append('act 0 seats %r != %r' % (seats(state), bench))
    if state.vars['spain_cortes_raw_monarchists'] != machine_raw:
        problems.append('act 0 machine raw %r != %r'
                        % (state.vars['spain_cortes_raw_monarchists'], machine_raw))
    if crisis_open(state):
        problems.append('act 0 opened a crisis')
    for act, patronage, machine_raw, bench, donors in SEAT_TABLE[1:]:
        turno.run('spain_encasillado', state)
        if seats(state) != bench:
            problems.append('act %d seats %r != %r' % (act, seats(state), bench))
        if state.vars['spain_cortes_raw_monarchists'] != machine_raw:
            problems.append('act %d machine raw %r != %r'
                            % (act, state.vars['spain_cortes_raw_monarchists'], machine_raw))
        if state.vars['spain_cortes_raw_total'] != 124:
            problems.append('act %d raw total %r != 124 (transfer was not net zero)'
                            % (act, state.vars['spain_cortes_raw_total']))
        actual_donors = tuple(shifts(state, party) for party in
                              ('liberals', 'conservatives', 'republicans', 'socialists'))
        expected_donors = tuple(value - previous for value, previous in zip(donors, (30, 25, 15, 8)))
        if actual_donors != expected_donors:
            problems.append('act %d donor shifts %r != %r' % (act, actual_donors, expected_donors))
        if state.vars['spain_crown_patronage'] != patronage:
            problems.append('act %d patronage %r != %r'
                            % (act, state.vars['spain_crown_patronage'], patronage))
        if sum(seats(state, party) for party in PARTIES) != 400:
            problems.append('act %d chamber does not total 400' % act)
        should_be_open = bench < 201
        if crisis_open(state) != should_be_open:
            problems.append('act %d crisis flag %r, expected %r'
                            % (act, crisis_open(state), should_be_open))
        if state.vars['spain_government_majority'] != (0 if should_be_open else 1):
            problems.append('act %d majority %r with %r benches'
                            % (act, state.vars['spain_government_majority'], bench))
    if state.vars['spain_government_changes'] != 3:
        problems.append('government changes %r != 3' % state.vars['spain_government_changes'])
    if state.vars['spain_encasillados'] != 3:
        problems.append('encasillado counter %r != 3' % state.vars['spain_encasillados'])
    if 'spain_election_manufactured' not in state.flags:
        problems.append('the manufactured election flag was never set')
    return problems


# ---------------------------------------------------------------------------------------------
# The party the turno pays, and the two comparisons the S12a correction made explicit
# ---------------------------------------------------------------------------------------------

# The four blocs the machine draws from, and the constant that prices each removal.
DONORS = (('liberals', 'turno_from_liberals'),
          ('conservatives', 'turno_from_conservatives'),
          ('republicans', 'turno_from_republicans'),
          ('socialists', 'turno_from_socialists'))

# The nine comparisons the correction made explicit: the zero-party fallback, the seven beneficiary
# selectors, and the monthly minority test. Reverting them rebuilds the exact pre-correction file.
# The party tests are the same text inside `spain_government_recount` and `spain_cortes_fix_seat_total`,
# which already stated `compare = equals` both before and after this card, so both helpers are scoped
# to the block they belong to: a file-wide substitution would fabricate a defect the old file never had.
PARTY_IMPLICIT = 'check_variable = { var = spain_government_party value = %d }'
PARTY_EXPLICIT = 'check_variable = { var = spain_government_party value = %d compare = equals }'
ENCASILLADO = 'spain_encasillado = {'
END_OF_ENCASILLADO = 'spain_government_strain = {'
MONTHLY_EFFECT = 'spain_party_monthly = {'
MAJORITY_IMPLICIT = 'check_variable = { var = spain_government_majority value = 0 }'
MAJORITY_EXPLICIT = 'check_variable = { var = spain_government_majority value = 0 compare = equals }'


def encasillado_span(text):
    """The head, the `spain_encasillado` block and the tail after it, in that order."""
    start = text.index(ENCASILLADO)
    stop = text.index(END_OF_ENCASILLADO, start)
    return text[:start], text[start:stop], text[stop:]


def apply_party_comparisons(text):
    """The correction as the delivery states it: every selector names its comparison."""
    head, body, tail = encasillado_span(text)
    for party in range(0, 8):
        body = body.replace(PARTY_IMPLICIT % party, PARTY_EXPLICIT % party)
    split = tail.index(MONTHLY_EFFECT)
    return head + body + tail[:split] + tail[split:].replace(MAJORITY_IMPLICIT, MAJORITY_EXPLICIT, 1)


def revert_party_comparisons(text):
    """The exact pre-correction delivery: the same file with those nine comparisons omitted."""
    head, body, tail = encasillado_span(text)
    for party in range(0, 8):
        body = body.replace(PARTY_EXPLICIT % party, PARTY_IMPLICIT % party)
    split = tail.index(MONTHLY_EFFECT)
    return head + body + tail[:split] + tail[split:].replace(MAJORITY_EXPLICIT, MAJORITY_IMPLICIT, 1)


def party_draw_failures(turno, party):
    """One encasillado under a government of `party`: who keeps office, who is paid, who pays."""
    problems = []
    constants = turno.constants
    transfer = constants['spain_campaign.turno_seat_transfer']
    shares = dict((name, constants['spain_campaign.' + key]) for name, key in DONORS)
    state = restoration(turno, party=party)
    before = dict((name, shifts(state, name)) for name in PARTIES)
    before_total = state.vars['spain_cortes_raw_total']
    before_patronage = state.vars['spain_crown_patronage']
    before_changes = state.vars['spain_government_changes']
    before_encasillados = state.vars['spain_encasillados']
    turno.run('spain_encasillado', state)

    # only a chamber with no government named yet falls back to the Restoration's own party
    office = party or 1
    if state.vars['spain_government_party'] != office:
        problems.append('party %r left office as %r, expected %r'
                        % (party, state.vars['spain_government_party'], office))
    recipient = PARTIES[office - 1]

    deltas = dict((name, shifts(state, name) - before[name]) for name in PARTIES)
    for name in PARTIES:
        expected = (transfer if name == recipient else 0) - shares.get(name, 0)
        if deltas[name] != expected:
            problems.append('party %r moved %s support by %r, expected %r'
                            % (party, name, deltas[name], expected))
    gained = [name for name in PARTIES if deltas[name] > 0]
    if gained != [recipient]:
        problems.append('party %r paid %r, expected only the %s' % (party, gained, recipient))
    if sum(deltas.values()) != 0:
        problems.append('party %r transfer is not net zero: %r' % (party, sum(deltas.values())))
    if state.vars['spain_cortes_raw_total'] != before_total:
        problems.append('party %r raw total %r != %r'
                        % (party, state.vars['spain_cortes_raw_total'], before_total))
    if sum(seats(state, name) for name in PARTIES) != 400:
        problems.append('party %r leaves the chamber at %r benches'
                        % (party, sum(seats(state, name) for name in PARTIES)))
    if state.vars['spain_encasillados'] != before_encasillados + 1:
        problems.append('party %r counted %r encasillados, expected one'
                        % (party, state.vars['spain_encasillados'] - before_encasillados))
    if state.vars['spain_government_changes'] != before_changes + 1:
        problems.append('party %r counted %r government changes, expected one'
                        % (party, state.vars['spain_government_changes'] - before_changes))
    expected_patronage = min(before_patronage + constants['spain_campaign.patronage_gain'],
                             constants['spain_campaign.patronage_cap'])
    if state.vars['spain_crown_patronage'] != expected_patronage:
        problems.append('party %r patronage %r != %r'
                        % (party, state.vars['spain_crown_patronage'], expected_patronage))
    if state.calls['spain_appoint_government'] != 1:
        problems.append('party %r appointed %r times, expected once'
                        % (party, state.calls['spain_appoint_government']))
    return problems


def monthly_states(turno):
    """Two identical months that differ only in whether the government commands a majority."""
    states = {}
    for majority in (1, 0):
        state = restoration(turno)
        state.vars['spain_government_majority'] = majority
        state.vars['spain_coup_pressure'] = 0
        state.stability = 0.0
        states[majority] = state
    return states


def monthly_failures(turno):
    """Only a minority government pays the monthly penalty; nothing else contributes here."""
    problems = []
    constants = turno.constants
    states = monthly_states(turno)
    before = dict((majority, dict((name, shifts(state, name)) for name in PARTIES))
                  for majority, state in states.items())
    before_seats = dict((majority, dict((name, seats(state, name)) for name in PARTIES))
                        for majority, state in states.items())
    for state in states.values():
        turno.run('spain_party_monthly', state)
    minority, majority = states[0], states[1]

    expected_stability = constants['spain_campaign.minority_stability']
    expected_coup = constants['spain_campaign.minority_coup']
    if minority.stability != expected_stability:
        problems.append('a minority month moved stability %r, expected %r'
                        % (minority.stability, expected_stability))
    if minority.vars['spain_coup_pressure'] != expected_coup:
        problems.append('a minority month moved coup pressure %r, expected %r'
                        % (minority.vars['spain_coup_pressure'], expected_coup))
    if majority.stability != 0:
        problems.append('a majority month moved stability %r, expected 0' % majority.stability)
    if majority.vars['spain_coup_pressure'] != 0:
        problems.append('a majority month moved coup pressure %r, expected 0'
                        % majority.vars['spain_coup_pressure'])
    for majority_value, state in states.items():
        for name in PARTIES:
            if shifts(state, name) != before[majority_value][name]:
                problems.append('majority %r moved %s support by %r with no positive shift and '
                                'no rot' % (majority_value, name,
                                            shifts(state, name) - before[majority_value][name]))
            if seats(state, name) != before_seats[majority_value][name]:
                problems.append('majority %r moved %s seats' % (majority_value, name))
    return problems


def patronage_cap_failures(turno):
    """A reachable high-patronage draw reaches the cap instead of passing it."""
    problems = []
    cap = turno.constants['spain_campaign.patronage_cap']
    start = cap - 4  # 20 of 24: one draw would reach 26 without the clamp
    state = restoration(turno, patronage=start)
    turno.run('spain_encasillado', state)
    if state.vars['spain_crown_patronage'] != cap:
        problems.append('patronage %r after one draw from %r, expected the cap %r'
                        % (state.vars['spain_crown_patronage'], start, cap))
    turno.run('spain_encasillado', state)
    if state.vars['spain_crown_patronage'] != cap:
        problems.append('patronage %r after a second draw, still expected the cap %r'
                        % (state.vars['spain_crown_patronage'], cap))
    return problems


# ---------------------------------------------------------------------------------------------
# The two majority-zero tests the S12b card made explicit
# ---------------------------------------------------------------------------------------------
#
# `spain_government_strain` charges the monthly minority penalty and the incumbent-loss block in
# `spain_hold_election` takes support off a government the country has turned against. Both read the
# majority as a bare `value = 0`, which the long form resolves as `greater_than_or_equals`, so both
# fired for every government including a 245-seat majority. The blocks are named here so the mutants
# can revert one comparison without touching the other.

STRAIN_MARKERS = ('spain_government_strain = {', 'spain_hold_election = {')
ELECTION_MARKERS = ('spain_hold_election = {', 'spain_finance_party = {')


def revert_majority(text, markers):
    """One effect's `spain_government_majority` comparison, reverted to the implicit pre-card form."""
    opener, closer = markers
    start = text.index(opener)
    stop = text.index(closer, start + 1)
    body = text[start:stop]
    if MAJORITY_EXPLICIT not in body:
        raise base.Unsupported('%s states no explicit majority comparison' % opener)
    return text[:start] + body.replace(MAJORITY_EXPLICIT, MAJORITY_IMPLICIT, 1) + text[stop:]


def strain_observation(turno):
    """What the strain effect charges a minority bloc and a genuine majority, measured on the run."""
    observation = {}
    minority = restoration(turno)
    observation['minority_majority'] = minority.vars['spain_government_majority']
    minority.stability = 0.0
    minority.vars['spain_coup_pressure'] = 0
    turno.run('spain_government_strain', minority)
    observation['minority_stability'] = minority.stability
    observation['minority_coup'] = minority.vars['spain_coup_pressure']

    # a genuine majority, reached the way the machine reaches one: two draws from the Restoration
    majority = restoration(turno)
    for _ in range(2):
        turno.run('spain_encasillado', majority)
    observation['majority_majority'] = majority.vars['spain_government_majority']
    observation['majority_seats'] = majority.vars['spain_government_seats']
    majority.stability = 0.0
    majority.vars['spain_coup_pressure'] = 0
    turno.run('spain_government_strain', majority)
    observation['majority_stability'] = majority.stability
    observation['majority_coup'] = majority.vars['spain_coup_pressure']
    return observation


def strain_failures(turno):
    """Everything the strain observation contradicts, as sentences, for the mutant controls."""
    problems = []
    constants = turno.constants
    observation = strain_observation(turno)
    if observation['minority_majority'] != 0:
        problems.append('the minority fixture is not a minority: majority %r'
                        % observation['minority_majority'])
    if observation['minority_stability'] != constants['spain_campaign.minority_stability']:
        problems.append('a minority government moved stability %r, expected %r'
                        % (observation['minority_stability'],
                           constants['spain_campaign.minority_stability']))
    if observation['minority_coup'] != constants['spain_campaign.minority_coup']:
        problems.append('a minority government moved coup pressure %r, expected %r'
                        % (observation['minority_coup'], constants['spain_campaign.minority_coup']))
    if observation['majority_majority'] != 1:
        problems.append('the majority fixture never reached a majority: %r benches'
                        % observation['majority_seats'])
    if observation['majority_stability'] != 0:
        problems.append('a majority month moved stability %r, expected 0'
                        % observation['majority_stability'])
    if observation['majority_coup'] != 0:
        problems.append('a majority month moved coup pressure %r, expected 0'
                        % observation['majority_coup'])
    return problems


def incumbent_or(turno):
    """The shipped `OR` that decides who loses ground, its limit entries and its four payments."""
    body = named(turno.parsed['parties'], 'spain_hold_election')
    for key, value, line in body:
        if key != 'if' or value[0] != 'block':
            continue
        limits = [item for item in value[1]
                  if item[0] == 'limit' and item[1][0] == 'block']
        if not limits:
            continue
        entries = limits[0][1][1]
        if not any(entry_key == 'OR' for entry_key, _, _ in entries):
            continue
        payments = [item for item in value[1]
                    if item[0] == 'add_to_variable'
                    and item[1][0] == 'block'
                    and scalar_of(item[1][1], 'value') == 'constant:spain_campaign.incumbent_loss']
        return entries, payments, line
    raise base.Unsupported('spain_hold_election has no incumbent-loss OR')


def incumbent_matrix(turno):
    """The four majority/stability combinations as (label, fires, expected), from the shipped OR."""
    threshold = turno.constants['spain_campaign.election_unrest_threshold']
    limit, payments, _line = incumbent_or(turno)
    cases = (('a stable majority', 1, threshold + 0.15, False),
             ('an unstable majority', 1, threshold - 0.15, True),
             ('a stable minority', 0, threshold + 0.15, True),
             ('an unstable minority', 0, threshold - 0.15, True))
    matrix = []
    for label, majority, stability, expected in cases:
        state = restoration(turno)
        state.vars['spain_government_majority'] = majority
        state.stability = stability
        matrix.append((label, turno.trigger(limit, state), expected))
    return matrix, payments


def incumbent_failures(turno):
    """Everything the incumbent-loss block contradicts, as sentences, for the mutant controls."""
    problems = []
    matrix, payments = incumbent_matrix(turno)
    if len(payments) != 4:
        problems.append('the incumbent block pays %d recipients through incumbent_loss, expected 4'
                        % len(payments))
    for label, actual, expected in matrix:
        if actual != expected:
            problems.append('%s fires the incumbent loss %r, expected %r'
                            % (label, actual, expected))
    return problems


# ---------------------------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------------------------

def test_seat_table(report, turno):
    report.start('seat table')
    problems = seat_table_failures(turno)
    report.check('the shipped encasillado reproduces 129 -> 188 -> 245 -> 304 at patronage 0/6/12/18',
                 not problems, '; '.join(problems))
    state = restoration(turno)
    turno.run('spain_encasillado', state)
    report.equal('one act alone leaves the government 13 short', 201 - seats(state), 13)
    report.check('one act alone is not a majority', state.vars['spain_government_majority'] == 0)
    report.check('the act explains itself through one curated tooltip',
                 state.tooltips.count('spain_encasillado_tt') == 1, repr(state.tooltips))
    report.check('the act draws the Crown into the appointment',
                 state.bop['SPR_crown_and_cortes'] == turno.macros['bop_crown'],
                 repr(dict(state.bop)))

    # the cap is a trigger, not a comment: after three draws the decision can no longer fire
    state = restoration(turno)
    for _ in range(3):
        turno.run('spain_encasillado', state)
    report.check('at the cap the encasillado trigger is false',
                 not turno.trigger(named(turno.parsed['triggers'], 'spain_encasillado_available'), state))
    turno.run('spain_encasillado', state)
    report.equal('a forced fourth draw cannot pass the cap', state.vars['spain_encasillados'], 3)
    report.equal('a forced fourth draw cannot add another bench', seats(state), 304)


def test_party_identity(report, turno):
    report.start('party identity')
    problems = party_draw_failures(turno, 0)
    report.check('a chamber with no government named yet falls back to the monarchists',
                 not problems, '; '.join(problems))
    for party in range(1, 8):
        problems = party_draw_failures(turno, party)
        report.check('an encasillado drawn by the %s keeps that party in office and pays it alone'
                     % PARTIES[party - 1], not problems, '; '.join(problems))

    # the transfer is the same eighteen points whichever party governs, so a donor that governs
    # still pays its own share: its net gain is the transfer minus that share, not the transfer
    state = restoration(turno, party=2)
    turno.run('spain_encasillado', state)
    report.equal('a governing donor nets the transfer minus its own share',
                 shifts(state, 'liberals'),
                 turno.constants['spain_campaign.turno_seat_transfer']
                 - turno.constants['spain_campaign.turno_from_liberals'])
    report.equal('and the other three donors still pay in full', shifts(state, 'conservatives'),
                 -turno.constants['spain_campaign.turno_from_conservatives'])


def test_monthly_minority(report, turno):
    report.start('monthly minority')
    problems = monthly_failures(turno)
    report.check('a majority government is not charged the minority penalty',
                 not problems, '; '.join(problems))
    states = monthly_states(turno)
    for state in states.values():
        turno.run('spain_party_monthly', state)
    report.equal('a minority month costs exactly the minority stability', states[0].stability,
                 turno.constants['spain_campaign.minority_stability'])
    report.equal('a majority month costs no stability', states[1].stability, 0)
    report.equal('a minority month raises coup pressure by exactly the minority amount',
                 states[0].vars['spain_coup_pressure'],
                 turno.constants['spain_campaign.minority_coup'])
    report.equal('a majority month raises no coup pressure',
                 states[1].vars['spain_coup_pressure'], 0)


def test_patronage_cap(report, turno):
    report.start('patronage cap')
    problems = patronage_cap_failures(turno)
    report.check('a draw from twenty of twenty-four patronage stops at the cap and stays there',
                 not problems, '; '.join(problems))
    cap = turno.constants['spain_campaign.patronage_cap']
    rot = turno.constants['spain_campaign.patronage_rot']
    report.check('the cap sits above the rot line, so a full machine always rots', cap > rot,
                 'cap %r rot %r' % (cap, rot))


def test_appointment(report, turno):
    report.start('appointment')
    state = restoration(turno)
    block = named(turno.parsed['parties'], 'spain_appoint_government')
    turno.run_entries(block, state, {'PARTY': '3', 'COALITION_1': '2', 'COALITION_2': '0'})
    report.equal('the party input appoints the party', state.vars['spain_government_party'], 3)
    report.equal('the first coalition input is stored', state.vars['spain_coalition_1'], 2)
    report.equal('the second coalition input is stored', state.vars['spain_coalition_2'], 0)
    report.equal('the appointment is counted', state.vars['spain_government_changes'], 1)
    turno.run_entries(block, state, {'PARTY': '0', 'COALITION_1': '0', 'COALITION_2': '0'})
    report.equal('PARTY = 0 keeps the party that already governs',
                 state.vars['spain_government_party'], 3)
    report.check('a governing bloc below 201 opens the crisis', crisis_open(state))

    # the bloc a coalition completes closes it again
    state = restoration(turno)
    turno.run_entries(block, state, {'PARTY': '1', 'COALITION_1': '3', 'COALITION_2': '2'})
    report.check('a coalition that reaches 201 closes the crisis', not crisis_open(state),
                 'seats %r' % state.vars['spain_government_seats'])
    gap = state.vars['spain_cortes_govt_gap']
    bloc = state.vars['spain_government_seats']
    report.equal('the panel was refreshed with the same bloc', gap,
                 bloc - 201 if bloc >= 201 else 201 - bloc)

    guarded: tuple[tuple[str, dict], ...] = (
        ('Rivera', dict(chapter='spain_chapter_rivera')),
        ('the Republic', dict(chapter='spain_chapter_republic')),
        ('a coup in progress', dict(coup=True)),
        ('a deleted balance', dict(balance=False)),
        ('the civil-war chapter', dict(chapter='spain_chapter_civil_war')),
    )
    for label, options in guarded:
        state = restoration(turno, **options)
        before = dict((name, state.vars.get(name)) for name in
                      ('spain_government_party', 'spain_government_changes', 'spain_government_seats'))
        turno.run_entries(block, state, {'PARTY': '3', 'COALITION_1': '0', 'COALITION_2': '0'})
        after = dict((name, state.vars.get(name)) for name in before)
        report.check('appointment is a no-op in %s' % label, before == after,
                     '%r -> %r' % (before, after))
        report.check('appointment opens no crisis in %s' % label, not crisis_open(state))


def test_rot_reader(report, turno):
    report.start('rot reader')
    rot = turno.constants['spain_campaign.patronage_rot']
    report.equal('the rot line is the design value', rot, 17)
    below = restoration(turno, patronage=16)
    at = restoration(turno, patronage=17)
    for state in (below, at):
        state.vars['spain_coup_pressure'] = 0
        turno.run('spain_party_monthly', state)
    report.equal('below the rot line the republicans do not gain', shifts(below, 'republicans'), 0)
    report.equal('at the rot line the republicans gain one a month', shifts(at, 'republicans'), 1)
    report.equal('at the rot line the carlists gain one a month', shifts(at, 'carlists'), 1)
    report.equal('the rot raises coup pressure by its own amount',
                 at.vars['spain_coup_pressure'] - below.vars['spain_coup_pressure'],
                 turno.constants['spain_campaign.patronage_rot_coup'])
    report.equal('the rot re-counts the chamber in the same month: republican raw +1',
                 at.vars['spain_cortes_raw_republicans']
                 - below.vars['spain_cortes_raw_republicans'], 1)
    report.check('no idea is added by the rot',
                 'add_ideas' not in turno.raw['parties'])
    for name in ('spain_appoint_government', 'spain_encasillado'):
        report.check('%s adds no idea' % name,
                     'add_ideas' not in str(named(turno.parsed['parties'], name)))


def test_routes(report, turno):
    report.start('routes')
    decisions = named(turno.parsed['decisions'], CATEGORY)
    category_text = turno.raw['decisions']

    report.check('the mission is inside the category, not a top-level decision',
                 has(decisions, MISSION))
    report.check('every route is inside the category',
                 all(has(decisions, route) for route in ROUTES))
    report.check('the five PP-only decisions are still there',
                 all(has(decisions, decision) for decision in EXISTING))

    # the five existing decisions are untouched, byte for byte
    head = subprocess.run(['git', 'show', '%s:%s' % (BASELINE_REV, DECISIONS_PATH)],
                          cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if head.returncode != 0:
        report.note('git show failed for the baseline decisions file: %s'
                    % head.stderr.decode('utf-8', 'replace').strip())
    else:
        old = head.stdout.decode('utf-8-sig')
        start = old.index('\tSPR_court_appointments = {')
        stop = old.index('\n}\n', old.index('\tSPR_force_an_election = {'))
        slice_old = old[start:stop]
        report.check('the five PP-only decisions are byte-identical to the pre-card file',
                     slice_old in turno.raw['decisions'],
                     'the existing block changed')
        report.check('no decision in the category is priced in political power alone',
                     '@election_pp' in category_text and '@decree_pp' in category_text)

    # ---- the honest election
    state = restoration(turno)
    election = block_of(decisions, 'SPR_honest_election')
    turno.run_entries(block_of(election, 'complete_effect'), state, {})
    report.equal('the honest election calls the existing election', state.hold_elections, 1)
    report.equal('the honest election re-appoints a government',
                 state.vars['spain_government_changes'], 1)
    election = block_of(decisions, 'SPR_honest_election')
    report.equal('the honest election costs the existing election price',
                 (scalar_of(election, 'cost'), -turno.constants['spain_campaign.election_cost']),
                 ('@election_pp', 50))
    report.equal('the election macro equals the election cost constant',
                 turno.macros['election_pp'], -turno.constants['spain_campaign.election_cost'])

    # ---- the royal decree
    state = restoration(turno)
    benches = seats(state)
    turno.run_entries(block_of(block_of(decisions, 'SPR_royal_decree'), 'complete_effect'),
                      state, {})
    report.equal('the decree changes no bench', seats(state), benches)
    report.check('the decree moves the balance away from the Crown',
                 state.bop['SPR_crown_and_cortes'] == turno.macros['bop_cortes'],
                 repr(dict(state.bop)))
    report.check('the decree lowers loyalty and raises coup pressure',
                 state.vars['spain_military_loyalty'] < 55 and state.vars['spain_coup_pressure'] > 0,
                 'loyalty %r coup %r' % (state.vars['spain_military_loyalty'],
                                         state.vars['spain_coup_pressure']))
    report.check('the decree is remembered', 'spain_restoration_decree_rule' in state.flags)
    report.check('the decree ends the ministerial crisis', not crisis_open(state))
    decree = block_of(decisions, 'SPR_royal_decree')
    report.equal('the decree costs the large political-power band',
                 turno.value(scalar_of(decree, 'cost'), TurnoState(), {}),
                 turno.constants['spain_campaign.pp_large'])


def test_mission(report, turno):
    report.start('mission')
    decisions = named(turno.parsed['decisions'], CATEGORY)
    mission = block_of(decisions, MISSION)
    report.equal('the mission times out on the crisis constant',
                 turno.value(scalar_of(mission, 'days_mission_timeout'), TurnoState(), {}),
                 turno.constants['spain_campaign.crisis_timeout_days'])
    report.equal('the timeout is 90 days', turno.macros['crisis_timeout_days'], 90)
    report.check('the mission completes when the bloc reaches 201',
                 'cortes_majority' in str(block_of(mission, 'available')))
    report.check('the mission cancels when the crisis flag clears',
                 'spain_ministry_crisis_open' in str(block_of(mission, 'cancel_trigger')))
    report.check('the mission appears only while the crisis is open',
                 'spain_ministry_crisis_open' in str(block_of(mission, 'activation')))
    # the deadline is the failure and the majority is the reward, so the panel must not be told
    # the mission is inverted (is_good = yes relabels completion as "effects when failed")
    report.check('the mission is not inverted, the deadline is its failure',
                 scalar_of(mission, 'is_good') in (None, 'no'),
                 'is_good %r' % scalar_of(mission, 'is_good'))
    report.check('the mission activates itself rather than waiting for a click',
                 not has(mission, 'selectable_mission'))

    state = restoration(turno)
    state.flags.add('spain_ministry_crisis_open')
    turno.run_entries(block_of(mission, 'timeout_effect'), state, {})
    report.check('the timeout clears the crisis flag', not crisis_open(state))
    report.equal('the timeout fires the Crown event', state.events, ['spain_campaign.32'])

    state = restoration(turno)
    state.flags.add('spain_ministry_crisis_open')
    turno.run_entries(block_of(mission, 'complete_effect'), state, {})
    report.check('completion clears the crisis flag', not crisis_open(state))

    # ---- the timeout event
    events = blocks(tokens_of(turno.raw['events']), 'country_event')
    by_id = dict((scalar_of(event, 'id'), event) for event in events)
    report.check('spain_campaign.32 exists', 'spain_campaign.32' in by_id)
    if 'spain_campaign.32' not in by_id:
        return
    event = by_id['spain_campaign.32']
    report.check('the event is triggered only', scalar_of(event, 'is_triggered_only') == 'yes')
    options = blocks(event, 'option')
    report.equal('the Crown acts alone: one option', len(options), 1)
    report.equal('the option explains itself', scalar_of(options[0], 'custom_effect_tooltip'),
                 'spain_campaign.32.a.tt')

    state = restoration(turno)
    state.flags.add('spain_ministry_crisis_open')
    turno.run_entries(block_of(options[0], 'hidden_effect'), state, {})
    report.equal('the ignored crisis is settled with the turno', seats(state), 188)
    report.check('and the still-short bloc re-opens the crisis', crisis_open(state),
                 'seats %r' % state.vars['spain_government_seats'])

    state = restoration(turno, encasillados=3, patronage=18)
    state.flags.add('spain_ministry_crisis_open')
    benches = seats(state)
    turno.run_entries(block_of(options[0], 'hidden_effect'), state, {})
    report.equal('with the donors exhausted no bench moves', seats(state), benches)
    report.check('and the Crown pays for it', state.vars['spain_military_loyalty'] < 55,
                 'loyalty %r' % state.vars['spain_military_loyalty'])
    report.check('the exhausted crisis still closes', not crisis_open(state))


def test_localisation(report, turno):
    report.start('localisation')
    raw = (ROOT / LOC_PATH).read_bytes()
    report.check('the localisation file still opens with a BOM', raw[:3] == b'\xef\xbb\xbf')
    text = raw.decode('utf-8-sig')
    keys = set(match.group(1) for match in re.finditer(r'^\s*([A-Za-z0-9_.]+):', text, re.M))
    wanted = ['SPR_ministerial_crisis', 'SPR_ministerial_crisis_desc']
    for route in ROUTES:
        wanted.extend([route, route + '_desc'])
    wanted.extend(['spain_ministry_crisis_open_tt', 'spain_ministry_crisis_resolved_tt',
                   'spain_ministry_crisis_complete_tt', 'spain_ministry_crisis_timeout_tt',
                   'spain_encasillado_tt', 'spain_encasillado_available_tt',
                   'spain_honest_election_available_tt', 'spain_honest_election_tt',
                   'spain_royal_decree_available_tt', 'spain_royal_decree_tt',
                   'spain_campaign.32.t', 'spain_campaign.32.d', 'spain_campaign.32.a',
                   'spain_campaign.32.a.tt'])
    missing = [key for key in wanted if key not in keys]
    report.check('every new decision, mission, tooltip and event key is localised',
                 not missing, 'missing %r' % missing)

    # every tooltip the shipped script asks for must exist, wherever the repository localises it:
    # spain_campaign.txt is one of several files whose tooltips the campaign already ships, and a
    # key that lives in spain_parties_l_english.yml is just as localised as one that lives here.
    used = set(re.findall(r'tooltip = (spain_[a-z0-9_.]+)', turno.raw['decisions']))
    used |= set(re.findall(r'custom_effect_tooltip = (spain_[a-z0-9_.]+)', turno.raw['decisions']))
    used |= set(re.findall(r'custom_effect_tooltip = (spain_[a-z0-9_.]+)', turno.raw['events']))
    used |= set(re.findall(r'custom_effect_tooltip = (spain_[a-z0-9_.]+)', turno.raw['parties']))
    shipped = set()
    for path in sorted((ROOT / 'localisation').rglob('*.yml')):
        shipped |= set(re.findall(r'^\s*([A-Za-z0-9_.]+):',
                                  path.read_bytes().decode('utf-8-sig'), re.M))
    report.check('every tooltip key the new script uses is localised',
                 all(key in shipped for key in used), 'missing %r' % sorted(used - shipped))
    report.check('the keys this card introduces are localised in the campaign file',
                 all(key in keys for key in wanted), 'missing %r' % sorted(set(wanted) - keys))


def test_identifiers(report, turno):
    report.start('identifiers')
    decisions = turno.raw['decisions']
    parties = turno.raw['parties']
    triggers = turno.raw['triggers']
    report.equal('spain_appoint_government is defined once',
                 len(re.findall(r'^spain_appoint_government = \{', parties, re.M)), 1)
    report.equal('spain_encasillado is defined once',
                 len(re.findall(r'^spain_encasillado = \{', parties, re.M)), 1)
    report.equal('spain_restoration_cortes_live is defined once',
                 len(re.findall(r'^spain_restoration_cortes_live = \{', triggers, re.M)), 1)
    report.equal('the mission is defined once',
                 len(re.findall(r'^\tSPR_ministerial_crisis = \{', decisions, re.M)), 1)
    report.equal('spain_campaign.32 is used by exactly one event id',
                 len(re.findall(r'id = spain_campaign\.32\b', turno.raw['events'])), 1)
    category = named(turno.parsed['decisions'], CATEGORY)
    report.check('the category carries decisions only, its metadata stays in categories/',
                 not any(key in ('icon', 'priority', 'allowed', 'visible')
                         for key, _, _ in category),
                 repr([key for key, _, _ in category if key in ('icon', 'priority', 'allowed', 'visible')]))
    # the coalition decisions this card must not touch
    untouched = subprocess.run(
        ['git', 'diff', '--quiet', BASELINE_REV, '--', 'common/decisions/spain_parties.txt'],
        cwd=str(ROOT))
    report.check('the five coalition decisions are not edited',
                 untouched.returncode == 0,
                 'common/decisions/spain_parties.txt differs from the baseline')


def test_mutant_control(report, turno):
    report.start('mutant control')
    baseline = subprocess.run(['git', 'show', '%s:%s' % (BASELINE_REV, PARTIES_PATH)],
                              cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if baseline.returncode != 0:
        report.note('git show failed for the baseline parties file: %s'
                    % baseline.stderr.decode('utf-8', 'replace').strip())
    else:
        old = Turno(overrides={PARTIES_PATH: baseline.stdout.decode('utf-8-sig')})
        try:
            seat_table_failures(old)
        except base.Unsupported as error:
            report.check('the pre-card parties file cannot even run the turno',
                         'spain_encasillado' in str(error) or 'cannot resolve' in str(error),
                         str(error))
        else:
            report.check('the pre-card parties file cannot even run the turno', False,
                         'the harness ran the pre-card file without complaint')

    # a shadow of the shipped file with the crisis-opening line removed must break the table's
    # crisis assertions while leaving the benches intact
    shadow = turno.raw['parties'].replace(
        '\t\t\tset_country_flag = spain_ministry_crisis_open\n', '', 1)
    if shadow == turno.raw['parties']:
        report.check('the mutation target exists', False, 'crisis flag line not found')
        return
    broken = Turno(overrides={PARTIES_PATH: shadow})
    problems = seat_table_failures(broken)
    report.check('removing the crisis line is caught by the seat-table contract',
                 any('crisis flag' in problem for problem in problems), '; '.join(problems))
    report.check('the mutant still reproduces the benches, so the check is specific',
                 not any('seats' in problem for problem in problems), '; '.join(problems))


def test_correction_mutants(report, turno):
    report.start('correction mutants')
    shipped = turno.raw['parties']
    pre = revert_party_comparisons(shipped)

    # the reconstruction has to be the exact inverse of the correction or the mutant proves nothing
    report.check('the pre-correction file is rebuilt by removing only the nine comparisons',
                 pre != shipped and apply_party_comparisons(pre) == shipped,
                 '%d bytes shorter than the delivery' % (len(shipped) - len(pre)))
    report.check('every selector and the monthly test state their comparison in the delivery',
                 apply_party_comparisons(shipped) == shipped)

    old = Turno(overrides={PARTIES_PATH: pre})
    failed = [party for party in range(1, 8) if party_draw_failures(old, party)]
    report.equal('the pre-correction delivery resets every appointed party 2..7', failed,
                 [2, 3, 4, 5, 6, 7])
    report.check('party 1 survived the old selectors, which is why the original checks passed',
                 party_draw_failures(old, 1) == [], '%r' % (party_draw_failures(old, 1),))
    old_monthly = monthly_failures(old)
    report.check('the pre-correction monthly test penalises a majority government',
                 any('majority month' in problem for problem in old_monthly),
                 '; '.join(old_monthly))

    # a one-line repair of the zero fallback is not a repair: the >= selectors still multi-fire
    half = pre.replace(PARTY_IMPLICIT % 0, PARTY_EXPLICIT % 0)
    report.check('the zero-fallback-only mutant differs from the delivery', half != shipped)
    half_turno = Turno(overrides={PARTIES_PATH: half})
    half_failed = [party for party in range(1, 8) if party_draw_failures(half_turno, party)]
    report.equal('fixing only the zero fallback still fails parties 2..7', half_failed,
                 [2, 3, 4, 5, 6, 7])

    # the patronage clamp, exercised from a reachable high-patronage state rather than from zero
    no_clamp = shipped.replace(
        '\t\t\tclamp_variable = { var = spain_crown_patronage min = 0 '
        'max = constant:spain_campaign.patronage_cap }\n', '', 1)
    report.check('the patronage clamp line exists to remove', no_clamp != shipped)
    clamp_problems = patronage_cap_failures(Turno(overrides={PARTIES_PATH: no_clamp}))
    report.check('removing the patronage clamp is rejected', bool(clamp_problems),
                 '; '.join(clamp_problems))


def test_residual_comparisons(report, turno):
    report.start('residual majority comparisons')
    shipped = turno.raw['parties']
    report.equal('every spain_government_majority test in the file states its comparison',
                 shipped.count(MAJORITY_IMPLICIT), 0)
    report.equal('the strain, election and monthly tests are the three explicit ones',
                 shipped.count(MAJORITY_EXPLICIT), 3)

    constants = turno.constants
    observation = strain_observation(turno)
    report.equal('the strain fixture starts from a bloc of zero majorities',
                 observation['minority_majority'], 0)
    report.equal('a minority bloc pays the minority stability',
                 observation['minority_stability'],
                 constants['spain_campaign.minority_stability'])
    report.equal('a minority bloc pays the minority coup pressure',
                 observation['minority_coup'], constants['spain_campaign.minority_coup'])
    report.equal('the majority fixture is a real majority, drawn up through the machine',
                 (observation['majority_seats'], observation['majority_majority']), (245, 1))
    report.equal('a majority bloc pays no minority stability',
                 observation['majority_stability'], 0)
    report.equal('a majority bloc pays no minority coup pressure', observation['majority_coup'], 0)

    matrix, payments = incumbent_matrix(turno)
    report.equal('the incumbent loss still names its four recipients', len(payments), 4)
    for label, actual, expected in matrix:
        report.equal('%s fires the incumbent loss: %r' % (label, actual), actual, expected)

    # each equality carries its own block: reverting one must fail its own test and only its own
    strain_reverted = revert_majority(shipped, STRAIN_MARKERS)
    report.check('the strain mutation reverted exactly one comparison', strain_reverted != shipped)
    strain_mutant = Turno(overrides={PARTIES_PATH: strain_reverted})
    strain_problems = strain_failures(strain_mutant)
    report.check('reverting the strain comparison is rejected by the majority case',
                 any('a majority month moved stability' in problem for problem in strain_problems),
                 '; '.join(strain_problems))
    report.check('and the election comparison still holds in that mutant',
                 incumbent_failures(strain_mutant) == [],
                 '; '.join(incumbent_failures(strain_mutant)))

    election_reverted = revert_majority(shipped, ELECTION_MARKERS)
    report.check('the election mutation reverted exactly one comparison', election_reverted != shipped)
    election_mutant = Turno(overrides={PARTIES_PATH: election_reverted})
    election_problems = incumbent_failures(election_mutant)
    report.check('reverting the election comparison is rejected by the stable majority',
                 any('a stable majority fires the incumbent loss' in problem
                     for problem in election_problems),
                 '; '.join(election_problems))
    report.check('and the strain comparison still holds in that mutant',
                 strain_failures(election_mutant) == [],
                 '; '.join(strain_failures(election_mutant)))


def main(argv):
    detail = '--detail' in argv
    report = base.Report(detail=detail)
    turno = Turno()
    test_seat_table(report, turno)
    test_party_identity(report, turno)
    test_appointment(report, turno)
    test_monthly_minority(report, turno)
    test_patronage_cap(report, turno)
    test_rot_reader(report, turno)
    test_routes(report, turno)
    test_mission(report, turno)
    test_localisation(report, turno)
    test_identifiers(report, turno)
    test_mutant_control(report, turno)
    test_correction_mutants(report, turno)
    test_residual_comparisons(report, turno)
    ok = report.summary()
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
