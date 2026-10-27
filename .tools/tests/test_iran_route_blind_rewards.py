"""Regression test: the Khuzestan oil project charges no concession on the domestic route.

`IR2_khuzestan_oil` is opened by either `IR2_domestic_capital` or `IR2_foreign_concessions`, and
those two focuses are `mutually_exclusive`. Until this repair its reward called
`iran_concede_british_small` unconditionally, so an Iran that had taken the domestic route —
reclaiming British holding and subsidising its own workshops — still paid a foreign concession:
British influence rose, sovereignty fell, and `iran_recompute_leverage` republished foreign
dependence from a deal that player never made. The historical AI takes the domestic route, so the
defect fired in ordinary play rather than in an edge case.

The reward now gates the concession on the route flag:

    if = {
        limit = { NOT = { has_country_flag = iran_domestic_capital } }
        iran_concede_british_small = yes
    }

Because the pair is mutually exclusive and those are the only two entrances to the focus, the
absence of `iran_domestic_capital` is exactly "took the foreign concessions". The gate is also
what gives that flag its first reader, so it is a real route test rather than a dead symbol.

The suite reads the shipped files and executes the shipped reward body:

    1. `common/national_focus/iran_interwar.txt` for the three focus blocks and their rewards,
    2. `common/scripted_effects/iran_great_game_acts.txt` for `iran_concede_british_small`,
    3. `common/scripted_effects/iran_campaign.txt` for `iran_recompute_leverage`,
    4. `common/script_constants/iran_campaign.txt` for the concession magnitudes,
    5. `common/`, `events/` and `history/` for the flag census,
    6. the two English localisation files for the tooltip and the focus description,
    7. `git show <BASELINE_REV>:` for the pre-repair file, which the preservation and mutant
       checks compare against.

`audit()` returns the failures it finds for a given focus-file text, so the same battery runs
against the shipped file and against four mutants of it (gate removed, gate inverted, concession
duplicated, gate hidden). Each mutant has to be rejected by the check that names its defect; that
control is what proves the suite detects the defect instead of describing the current file.

Modelled simplification: the evaluator resolves flags, `if`/`limit`, `hidden_effect` and the
scripted effects this reward calls. The `iran_path_oil_national` trigger inside the oil-national
bonus is treated as false, because that bonus only adds political power and authority and never
touches influence or sovereignty; the structural check below pins that it stays that way.

Run from the repository root:

    python .tools/tests/test_iran_route_blind_rewards.py           # exit 0 = pass
    python .tools/tests/test_iran_route_blind_rewards.py --detail  # print every check
    python .tools/tests/test_iran_route_blind_rewards.py --dump    # print the parsed reward

This is a source check. It proves what the script says when the parsed reward is executed under a
declared country state, not what the engine does when a player clicks the focus; that still needs
a played campaign, which this test never starts.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Read-only reuse: the Clausewitz parser and the script evaluator come from the leverage suite,
# so this file executes the shipped reward with the same semantics that suite already pins.
from test_iran_leverage_derivation import (  # noqa: E402
    Engine,
    Env,
    constants,
    focus_reward,
    parse,
    read,
    strip_comments,
)

ROOT = Path(__file__).resolve().parents[2]

FOCUS = 'common/national_focus/iran_interwar.txt'
ACTS = 'common/scripted_effects/iran_great_game_acts.txt'
EFFECTS = 'common/scripted_effects/iran_campaign.txt'
CONSTANTS = 'common/script_constants/iran_campaign.txt'
ACTS_LOC = 'localisation/english/iran_great_game_acts_l_english.yml'
FOCUS_LOC = 'localisation/english/iran_campaign_l_english.yml'

FOCUS_ID = 'IR2_khuzestan_oil'
DOMESTIC = 'IR2_domestic_capital'
FOREIGN = 'IR2_foreign_concessions'
DOMESTIC_FLAG = 'iran_domestic_capital'
CONCESSION = 'iran_concede_british_small'
CONCESSION_TT = 'iran_concede_british_small_tt'
OIL_FLAG = 'iran_oil_programme'
OIL_BONUS_TT = 'iran_oil_national_bonus_tt'
OIL_EVENT = 'iran_campaign.24'
OIL_STATE = '413'
BASELINE_FLAG = 'iran_leverage_baselined'

# The pre-repair file, pinned by full object name: a moving `HEAD` would stop being a mutant the
# moment the repair is committed.
BASELINE_REV = 'b978f23e6d9588c9131786e4b75da46f24149040'

# Every effect key this reward is expected to contain. An op outside this set means the reward
# grew something this suite does not model, which would otherwise let a new defect pass unseen.
EFFECT_OPS = {
    'limit',
    'if',
    'else_if',
    'hidden_effect',
    'set_country_flag',
    'country_event',
    'add_resource',
    'add_political_power',
    'add_to_variable',
    'custom_effect_tooltip',
    OIL_STATE,
    CONCESSION,
}
TRIGGER_OPS = {'NOT', 'OR', 'AND', 'has_country_flag', 'iran_path_oil_national'}

# A mid-band Iranian state: far enough from both ends of every clamp that a single concession
# cannot be masked by a clamp, and with the leverage baseline already captured so the run measures
# the concession rather than a one-time initialisation.
OPENING = {
    'iran_british_influence': 20,
    'iran_northern_influence': 10,
    'iran_german_influence': 5,
    'iran_sovereignty': 50,
    'iran_foreign_leverage': 30,
    'iran_leverage_landed': 30,
    'iran_leverage_debt': 0,
    'iran_influence_baseline': 35,
    'iran_leverage_baseline': 17,
    'iran_authority': 40,
}

INFLUENCE = 'iran_british_influence'
SOVEREIGNTY = 'iran_sovereignty'

DETAIL = '--detail' in sys.argv


class Unsupported(Exception):
    """A script shape this suite does not model. Failing loudly beats guessing."""


# ------------------------------------------------------------------------------- source reading

def repo_text(rel):
    return read(rel).replace('\r\n', '\n')


def structured(text):
    """The script with comments removed: the imported parser keeps `#` as an ordinary token."""
    return strip_comments(text.replace('\r\n', '\n'))


def baseline_text(rel):
    result = subprocess.run(
        ['git', 'show', '%s:%s' % (BASELINE_REV, rel)],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode != 0:
        raise Unsupported('git show %s:%s failed: %s'
                          % (BASELINE_REV, rel, result.stderr.decode('utf-8', 'replace').strip()))
    return result.stdout.decode('utf-8-sig').replace('\r\n', '\n')


def focus_span(text, ident):
    """Character span of the `focus = { ... }` block whose id is `ident`."""
    match = re.search(r'(?m)^[ \t]*id[ \t]*=[ \t]*%s\b' % re.escape(ident), text)
    if not match:
        return None
    opening = text.rfind('{', 0, match.start())
    if opening < 0:
        return None
    depth = 0
    index = opening
    while index < len(text):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return opening, index + 1
        index += 1
    raise Unsupported('unclosed focus block for %s' % ident)


def focus_ops(text, ident):
    code = structured(text)
    span = focus_span(code, ident)
    if span is None:
        return None
    return parse(code[span[0] + 1:span[1] - 1])


def field(ops, key):
    """First value of `key` in a parsed block, or None."""
    for item_key, value in ops:
        if item_key == key:
            return value
    return None


def fields(ops, key):
    return [value for item_key, value in ops if item_key == key]


def code_outside(text, ident):
    span = focus_span(text, ident)
    if span is None:
        raise Unsupported('focus %s not found' % ident)
    return text[:span[0]] + text[span[1]:]


# ------------------------------------------------------------------------------- reward shape

def walk_effects(nodes, hidden=0, gate=None, sites=None, unknown=None, in_trigger=False):
    """Collect concession call sites and any effect key this suite does not model."""
    sites = [] if sites is None else sites
    unknown = [] if unknown is None else unknown
    for key, value in nodes:
        allowed = TRIGGER_OPS if in_trigger else EFFECT_OPS
        if key not in allowed:
            unknown.append(key)
        if key == 'limit':
            walk_effects(value, hidden, gate, sites, unknown, in_trigger=True)
        elif key in ('if', 'else_if'):
            limit = [item for item in value if item[0] == 'limit']
            body = [item for item in value if item[0] != 'limit']
            inner_gate = limit[0][1] if limit else gate
            walk_effects(body, hidden, inner_gate, sites, unknown, in_trigger)
        elif key == 'hidden_effect':
            walk_effects(value, hidden + 1, gate, sites, unknown, in_trigger)
        elif key == CONCESSION:
            sites.append({'hidden': hidden, 'gate': gate})
    return sites, unknown


def gate_is_domestic_test(gate):
    """`NOT = { has_country_flag = iran_domestic_capital }`, parsed, and nothing else."""
    if gate is None:
        return False
    return gate == [('NOT', [('has_country_flag', DOMESTIC_FLAG)])]


# ------------------------------------------------------------------------------- execution

def build_engine():
    sources = {rel: repo_text(rel) for rel in (EFFECTS, ACTS, CONSTANTS)}
    return Engine(sources, constants())


def run_reward(engine, text, flags):
    reward = focus_reward(structured(text), FOCUS_ID)
    if reward is None:
        raise Unsupported('completion_reward of %s not found' % FOCUS_ID)
    env = Env(flags=set(flags) | {BASELINE_FLAG})
    env.vars = dict(OPENING)
    engine.run(env, reward)
    return env


# ------------------------------------------------------------------------------- flag census

def flag_census():
    """flag -> {'writers': [...], 'readers': [...]} across common/, events/ and history/."""
    census = {}
    roots = [ROOT / 'common', ROOT / 'events', ROOT / 'history']
    writer = re.compile(r'\b(set_country_flag|clr_country_flag)[ \t]*=[ \t]*([A-Za-z0-9_]+)')
    reader = re.compile(r'\bhas_country_flag[ \t]*=[ \t]*([A-Za-z0-9_]+)')
    for root in roots:
        for path in sorted(root.rglob('*.txt')):
            rel = path.relative_to(ROOT).as_posix()
            try:
                text = path.read_text(encoding='utf-8-sig', errors='replace')
            except OSError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                code = line.split('#', 1)[0]
                if not code.strip():
                    continue
                for match in writer.finditer(code):
                    entry = census.setdefault(match.group(2), {'writers': [], 'readers': []})
                    entry['writers'].append('%s:%d' % (rel, number))
                for match in reader.finditer(code):
                    entry = census.setdefault(match.group(1), {'writers': [], 'readers': []})
                    entry['readers'].append('%s:%d' % (rel, number))
    return census


def flags_touched_by_reward(reward):
    """Flags the reward writes, plus flags its trigger limits read."""
    written, read_flags = [], []

    def walk(nodes, in_trigger=False):
        for key, value in nodes:
            if key in ('set_country_flag', 'clr_country_flag'):
                written.append(value)
            elif key == 'has_country_flag':
                read_flags.append(value)
            elif key == 'limit':
                walk(value, True)
            elif key in ('if', 'else_if', 'hidden_effect'):
                walk(value, in_trigger)

    walk(reward)
    return written, read_flags


def flags_written_in_file(text):
    text = text.replace('\r\n', '\n')
    flags = []
    for match in re.finditer(r'(?m)^[ \t]*set_country_flag[ \t]*=[ \t]*([A-Za-z0-9_]+)', text):
        flags.append(match.group(1))
    return flags


# ------------------------------------------------------------------------------- checks

class Report:
    def __init__(self, detail=False):
        self.detail = detail
        self.checks = 0
        self.failures = []
        self.notes = []

    def fail(self, ident, label, detail=''):
        self.failures.append('%s %s%s' % (ident, label, (' — ' + detail) if detail else ''))

    def check(self, ident, label, condition, detail=''):
        self.checks += 1
        if not condition:
            self.fail(ident, label, detail)
        elif self.detail:
            print('  ok  [%s] %s%s' % (ident, label, (' — ' + detail) if detail else ''))

    def note(self, text):
        self.notes.append(text)
        print('  note  %s' % text)


def audit(report, text, engine, baseline, census, preservation=True):
    reward = focus_reward(structured(text), FOCUS_ID)
    if reward is None:
        raise Unsupported('completion_reward of %s not found in the audited text' % FOCUS_ID)

    # --- structure -----------------------------------------------------------------------------
    sites, unknown = walk_effects(reward)
    report.check('S1', 'the reward parses with a completion_reward', bool(reward),
                 '%d top-level entries' % len(reward))
    report.check('S2', 'every effect and trigger in the reward is modelled by this suite',
                 not unknown, 'unmodelled: %r' % sorted(set(unknown)))
    report.check('S3', 'the concession is invoked exactly once in the reward', len(sites) == 1,
                 '%d invocation(s)' % len(sites))
    site = sites[0] if len(sites) == 1 else (sites[0] if sites else None)
    report.check('S4', 'the concession sits inside a conditional block, not at the top level',
                 site is not None and site['gate'] is not None,
                 'gate: %r' % (None if site is None else site['gate']))
    report.check('S5', 'that condition is exactly NOT has_country_flag iran_domestic_capital',
                 site is not None and gate_is_domestic_test(site['gate']),
                 repr(None if site is None else site['gate']))
    report.check('S6', 'the conditional block is renderable, so the concession tooltip survives',
                 site is not None and site['hidden'] == 0,
                 'hidden_effect depth: %r' % (None if site is None else site['hidden']))

    keys = [key for key, _ in reward]
    base_reward = focus_reward(structured(baseline), FOCUS_ID)
    base_keys = [key for key, _ in base_reward]
    replaced = [index for index in range(min(len(keys), len(base_keys)))
                if keys[index] != base_keys[index]]
    report.check('S7', 'the reward keeps the baseline order, with the concession wrapped in place',
                 len(keys) == len(base_keys)
                 and keys == [('if' if index in replaced else base_keys[index])
                              for index in range(len(base_keys))]
                 and all(keys[index] == 'if' for index in replaced),
                 '%r vs %r' % (keys, base_keys))
    report.check('S8', 'the oil flag, event, state, political power and oil-national tooltip remain',
                 field(reward, 'set_country_flag') == OIL_FLAG
                 and field(reward, 'country_event') == [('id', OIL_EVENT)]
                 and field(reward, OIL_STATE) is not None
                 and field(reward, 'add_political_power') == 'constant:iran_story.political_capital'
                 and field(reward, 'custom_effect_tooltip') == OIL_BONUS_TT,
                 repr([(key, value) for key, value in reward if key != 'if']))

    # --- behaviour -----------------------------------------------------------------------------
    domestic = run_reward(engine, text, {DOMESTIC_FLAG})
    foreign = run_reward(engine, text, set())

    report.check('B1', 'domestic route: the concession is never invoked',
                 domestic.calls.count(CONCESSION) == 0, 'calls: %r' % domestic.calls)
    report.check('B2', 'domestic route: British influence and sovereignty are untouched',
                 domestic.vars.get(INFLUENCE) == OPENING[INFLUENCE]
                 and domestic.vars.get(SOVEREIGNTY) == OPENING[SOVEREIGNTY],
                 'influence %r sovereignty %r' % (domestic.vars.get(INFLUENCE),
                                                  domestic.vars.get(SOVEREIGNTY)))
    report.check('B3', 'domestic route: the leverage model is not republished',
                 'iran_recompute_leverage' not in domestic.calls
                 and domestic.vars.get('iran_foreign_leverage') == OPENING['iran_foreign_leverage'],
                 'calls: %r leverage %r' % (domestic.calls,
                                            domestic.vars.get('iran_foreign_leverage')))

    report.check('B4', 'foreign route: the concession is invoked exactly once',
                 foreign.calls.count(CONCESSION) == 1, 'calls: %r' % foreign.calls)
    report.check('B5', 'foreign route: influence rises and sovereignty falls by the constants',
                 foreign.vars.get(INFLUENCE) == OPENING[INFLUENCE] + engine.consts['concede_small_influence']
                 and foreign.vars.get(SOVEREIGNTY) == OPENING[SOVEREIGNTY] - engine.consts['concede_small_sovereignty'],
                 'influence %r sovereignty %r' % (foreign.vars.get(INFLUENCE),
                                                  foreign.vars.get(SOVEREIGNTY)))
    report.check('B6', 'foreign route: the concession republishes leverage',
                 'iran_recompute_leverage' in foreign.calls,
                 'calls: %r' % foreign.calls)

    # --- branches ------------------------------------------------------------------------------
    domestic_ops = focus_ops(text, DOMESTIC)
    foreign_ops = focus_ops(text, FOREIGN)
    reward_ops = focus_ops(text, FOCUS_ID)
    if domestic_ops is None or foreign_ops is None or reward_ops is None:
        raise Unsupported('one of the three focus blocks is missing')

    excludes = [value for value in fields(domestic_ops, 'mutually_exclusive')]
    report.check('M1', '%s excludes %s' % (DOMESTIC, FOREIGN),
                 any(item == [('focus', FOREIGN)] for item in excludes), repr(excludes))
    excludes = [value for value in fields(foreign_ops, 'mutually_exclusive')]
    report.check('M2', '%s excludes %s' % (FOREIGN, DOMESTIC),
                 any(item == [('focus', DOMESTIC)] for item in excludes), repr(excludes))

    prerequisites = fields(reward_ops, 'prerequisite')
    entrance = [value for value in prerequisites if isinstance(value, list)]
    report.check('M3', 'the two branches are the only entrances, in one prerequisite block',
                 len(entrance) == 1
                 and [item[1] for item in entrance[0] if item[0] == 'focus'] == [DOMESTIC, FOREIGN],
                 repr(prerequisites))
    domestic_reward = focus_reward(structured(text), DOMESTIC)
    foreign_reward = focus_reward(structured(text), FOREIGN)
    report.check('M4', 'the flag the gate reads is written by the domestic branch itself',
                 ('set_country_flag', DOMESTIC_FLAG) in (domestic_reward or [])
                 and ('set_country_flag', DOMESTIC_FLAG) not in (foreign_reward or []),
                 repr([op for op in (domestic_reward or []) if op[0] == 'set_country_flag']))

    # --- flags ---------------------------------------------------------------------------------
    written, read_flags = flags_touched_by_reward(reward)
    missing = []
    for flag in sorted(set(written) | set(read_flags)):
        entry = census.get(flag, {'writers': [], 'readers': []})
        if not entry['readers']:
            missing.append(flag)
    report.check('F1', 'every flag the reward sets or reads has at least one reader',
                 not missing, 'unread: %r' % missing)
    report.check('F2', 'the gate gave iran_domestic_capital its first reader',
                 len(census.get(DOMESTIC_FLAG, {}).get('readers', [])) == 1
                 and census[DOMESTIC_FLAG]['readers'][0].endswith(str(line_of(text, DOMESTIC_FLAG))),
                 repr(census.get(DOMESTIC_FLAG, {})))

    # --- preservation --------------------------------------------------------------------------
    if preservation:
        report.check('P1', 'nothing outside the repaired focus block changed at all',
                     code_outside(text, FOCUS_ID) == code_outside(baseline, FOCUS_ID),
                     'compared with %s' % BASELINE_REV[:9])
        report.check('P2', 'the focus keeps its id, position, icon, cost, filters and AI weight',
                     [item for item in focus_ops(text, FOCUS_ID) if item[0] != 'completion_reward']
                     == [item for item in focus_ops(baseline, FOCUS_ID) if item[0] != 'completion_reward'],
                     repr([item for item in focus_ops(text, FOCUS_ID) if item[0] != 'completion_reward']))

    return reward


def line_of(text, flag):
    """1-based line of the `has_country_flag = <flag>` read, for the census cross-check."""
    for number, line in enumerate(text.replace('\r\n', '\n').splitlines(), 1):
        if re.search(r'has_country_flag[ \t]*=[ \t]*%s\b' % re.escape(flag), line.split('#', 1)[0]):
            return number
    return -1


# ------------------------------------------------------------------------------- localisation

def localisation_value(text, key):
    match = re.search(r'(?m)^[ \t]*%s[ \t]*:[ \t]*"((?:[^"\\]|\\.)*)"' % re.escape(key), text)
    return None if match is None else match.group(1)


def loc_failures(acts_loc, focus_loc, baseline_focus_loc):
    failures = []
    if CONCESSION_TT not in acts_loc:
        failures.append('%s is missing from %s' % (CONCESSION_TT, ACTS_LOC))
    current = localisation_value(focus_loc, 'IR2_khuzestan_oil_desc')
    before = localisation_value(baseline_focus_loc, 'IR2_khuzestan_oil_desc')
    if current is None:
        failures.append('IR2_khuzestan_oil_desc is missing from %s' % FOCUS_LOC)
    elif current != before:
        failures.append('IR2_khuzestan_oil_desc changed, which this repair did not need')
    elif 'concession' in current.lower():
        failures.append('the description promises a concession, which the domestic route does not make')
    return failures


# ------------------------------------------------------------------------------- mutants

MUTANTS = [
    ('X1', 'gate removed',
     """\t\t\tif = {
\t\t\t\tlimit = { NOT = { has_country_flag = iran_domestic_capital } }
\t\t\t\tiran_concede_british_small = yes
\t\t\t}""",
     """\t\t\tiran_concede_british_small = yes""",
     'B1'),
    ('X2', 'gate inverted to the domestic route',
     '\t\t\t\tlimit = { NOT = { has_country_flag = iran_domestic_capital } }',
     '\t\t\t\tlimit = { has_country_flag = iran_domestic_capital }',
     'B1'),
    ('X3', 'concession duplicated inside the gate',
     """\t\t\t\tiran_concede_british_small = yes""",
     """\t\t\t\tiran_concede_british_small = yes
\t\t\t\tiran_concede_british_small = yes""",
     'S3'),
    ('X4', 'gate hidden, so the tooltip disappears',
     """\t\t\tif = {
\t\t\t\tlimit = { NOT = { has_country_flag = iran_domestic_capital } }
\t\t\t\tiran_concede_british_small = yes
\t\t\t}""",
     """\t\t\thidden_effect = {
\t\t\t\tif = {
\t\t\t\t\tlimit = { NOT = { has_country_flag = iran_domestic_capital } }
\t\t\t\t\tiran_concede_british_small = yes
\t\t\t\t}
\t\t\t}""",
     'S6'),
]


def main():
    text = repo_text(FOCUS)
    baseline = baseline_text(FOCUS)
    engine = build_engine()
    census = flag_census()
    report = Report(detail=DETAIL)

    if '--dump' in sys.argv:
        for number, op in enumerate(focus_reward(structured(text), FOCUS_ID) or [], 1):
            print('%d  %r' % (number, op))
        sites, _ = walk_effects(focus_reward(structured(text), FOCUS_ID))
        print('concession sites: %r' % sites)
        return 0

    print('== shipped source')
    audit(report, text, engine, baseline, census)

    print('== mutants')
    for ident, label, old, new, expected in MUTANTS:
        if text.count(old) != 1:
            raise Unsupported('mutant %s (%s) does not match the shipped reward exactly once: %d hits'
                              % (ident, label, text.count(old)))
        mutant = text.replace(old, new, 1)
        mutant_report = Report(detail=False)
        try:
            audit(mutant_report, mutant, engine, baseline, census, preservation=False)
        except Unsupported as error:
            report.check(ident, 'mutant %r is rejected before it can pass' % label, False, str(error))
            continue
        caught = [failure for failure in mutant_report.failures
                  if failure.split()[0] == expected]
        report.check(ident, 'mutant %r is caught by %s' % (label, expected), bool(caught),
                     '; '.join(mutant_report.failures) or 'no failure at all')

    print('== localisation')
    acts_loc = repo_text(ACTS_LOC)
    focus_loc = repo_text(FOCUS_LOC)
    for failure in loc_failures(acts_loc, focus_loc, baseline_text(FOCUS_LOC)):
        report.check('T', failure, False)
    report.check('T1', 'the concession tooltip key exists and the description is unchanged',
                 not loc_failures(acts_loc, focus_loc, baseline_text(FOCUS_LOC)),
                 'IR2_khuzestan_oil_desc: %r' % localisation_value(focus_loc, 'IR2_khuzestan_oil_desc'))
    report.note('only localisation/english carries an Iran interwar file; the other project '
                'languages have none, recorded rather than invented')

    # --- file-wide census, reported and deliberately not enforced (out of this repair's scope) --
    write_only = []
    for flag in sorted(set(flags_written_in_file(text))):
        entry = census.get(flag, {'readers': []})
        if not entry['readers']:
            write_only.append(flag)
    report.note('%d flag(s) written in %s still have no reader anywhere; out of scope here: %s'
                % (len(write_only), FOCUS, ', '.join(write_only) or 'none'))

    print('%d checks, %d failures' % (report.checks, len(report.failures)))
    for failure in report.failures:
        print('  FAIL ' + failure)
    return 0 if not report.failures else 1


if __name__ == '__main__':
    sys.exit(main())
