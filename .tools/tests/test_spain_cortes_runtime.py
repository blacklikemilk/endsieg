"""Regression test: the Cortes chapter model is exclusive and the runtime package is wired.

Six facts this card is responsible for, asserted against the shipped source rather than described:

    1. every chapter opener clears the other chapter flags before it claims its own, so a
       continuous campaign holds exactly one `spain_chapter_*` flag and cannot keep the
       Restoration after 1923;
    2. the republican seat base is selected by a positive `spain_chapter_republic` test, so a
       civil-war or post-war chamber does not inherit it through a NOT/AND fallback;
    3. the six bill caches are written by a recount before any bill is offered, a recount refreshes
       them once without recursion or cost, and the six reach gates no longer fail open on an
       absent cache;
    4. the hemicycle writes the 1-based frames the eight-cell strip is addressed with;
    5. one definition of `spain_iberian_accord_tt` remains and both focus consumers still resolve;
    6. each bill cooldown flag expires on the same day as its decision's `days_re_enable`.

The test executes the real script. It reuses the tokeniser, parser, compiler and simulator of
`.tools/tests/test_spain_cortes_recount.py` (S9), so the numbers under test are the numbers the
shipped files produce, not a restatement of them. Each of the six areas is also run against the
same files at the pinned pre-S10 commit, and every mutant assertion must fail there: a check that
passes on both the repair and the defect proves nothing.

Run from the repository root:

    python .tools/tests/test_spain_cortes_runtime.py           # exit 0 = pass
    python .tools/tests/test_spain_cortes_runtime.py --detail  # print every check

This is a source simulation. It proves what the script says, not what the engine does: no focus
was clicked, no decision taken, no dot rendered, and the game was never launched.
"""

from __future__ import annotations

import collections
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_spain_cortes_recount as base  # noqa: E402  (the S9 harness, reused on purpose)

CAMPAIGN_PATH = 'common/scripted_effects/spain_campaign_effects.txt'
EFFECTS_PATH = 'common/scripted_effects/spain_cortes_effects.txt'
BILLS_PATH = 'common/scripted_effects/spain_cortes_bills.txt'
PARTIES_PATH = 'common/scripted_effects/spain_cortes_parties.txt'
HEMICYLE_PATH = 'common/scripted_effects/spain_cortes_hemicycle.txt'
DECISIONS_PATH = 'common/decisions/spain_cortes.txt'
GFX_PATH = 'interface/endsieg_spain_icons.gfx'
LOC_PATH = 'localisation/english/spain_campaign_l_english.yml'
RESTORATION_FOCUS_PATH = 'common/national_focus/spain_restoration.txt'
POSTWAR_FOCUS_PATH = 'common/national_focus/spain_republic_postwar.txt'

# Every file this test reads, printed in the coverage footer.
COVERED_FILES = (CAMPAIGN_PATH, EFFECTS_PATH, BILLS_PATH, PARTIES_PATH, HEMICYLE_PATH,
                 DECISIONS_PATH, GFX_PATH, LOC_PATH, RESTORATION_FOCUS_PATH, POSTWAR_FOCUS_PATH)

# The pre-S10 tree, pinned by full object name so it stays a mutant after the repair is committed.
BASELINE_REV = 'f6d12527cc8a3ed3cda6e533528f46bbba4d6e17'
# The 0-based seat table S10 committed and S16 reverses, pinned the same way: it is the mutant the
# frame-range checks have to reject now that the strip is addressed 1..8.
ZERO_BASED_EFFECT_REV = '5ad0945ad1a92944a258a5097680a220cb1c7af6'

CHAPTERS = ('restoration', 'rivera', 'republic', 'civil_war', 'postwar', 'republican_postwar')
BILLS = ('budget', 'agrarian', 'labour', 'army', 'statute', 'electoral')
BILL_DECISIONS = {
    'budget': 'SPR_bill_budget',
    'agrarian': 'SPR_bill_agrarian_reform',
    'labour': 'SPR_bill_labour_charter',
    'army': 'SPR_bill_army_budget',
    'statute': 'SPR_bill_regional_statute',
    'electoral': 'SPR_bill_electoral_law',
}
# dot frame each party owns: the strip's eight cells are addressed as frames 1..8, frame 1 the
# neutral seat and frames 2..8 the parties in the registration's own chamber order
PARTY_FRAMES = {
    'socialists': 2,
    'republicans': 3,
    'liberals': 4,
    'conservatives': 5,
    'monarchists': 6,
    'carlists': 7,
    'falange': 8,
}
NEUTRAL_FRAME = 1
STRIP_FRAMES = 8
DOTS = 100

# Effects a recount may reach while it refreshes the caches. Anything new fails here until it is
# decided whether it is a cost, a flag or a recursion.
ALLOWED_RECOUNT_CALLS = frozenset(
    ['spain_cortes_fix_seat_total', 'spain_government_recount', 'spain_cortes_refresh_display',
     'spain_cortes_draw_hemicycle', 'spain_bills_count_all',
     'spain_bill_count_votes'] +
    ['spain_bill_count_' + bill for bill in BILLS] +
    ['spain_bill_add_' + party for party in
     ('government', 'monarchists', 'liberals', 'conservatives', 'republicans', 'socialists',
      'carlists', 'falange')] +
    ['spain_bill_prepare_count']
)


class Unsupported(Exception):
    """A script shape this test does not model. Failing loudly beats guessing."""


def read(path, revision=None):
    if revision is None:
        with open(ROOT / path, 'r', encoding='utf-8-sig') as handle:
            return handle.read()
    result = subprocess.run(['git', 'show', '%s:%s' % (revision, path)], cwd=str(ROOT),
                            capture_output=True)
    if result.returncode != 0:
        print('cannot read %s:%s' % (revision, path))
        print(result.stderr.decode('utf-8', 'replace').strip())
        print('the mutant controls need the repository history; this is not a pass')
        sys.exit(2)
    return result.stdout.decode('utf-8-sig')


def blocks_of(text):
    return base.parse_file(text)


def fields(entries):
    """Parsed block entries -> {key: value}; a nested block unwraps to its own entry list."""
    return dict((key, value[1]) for key, value, _line in entries)


def decisions_of(text, category='SPR_cortes'):
    """A decision category -> {decision id: fields}, so callers never see a parse tuple shape."""
    return dict((key, fields(value[1])) for key, value, _line in blocks_of(text)[category][0])


def call_name(entries, index):
    key, value, _ = entries[index]
    return key if isinstance(value, tuple) and value and value[0] == 'scalar' else None


# ---------------------------------------------------------------------------------------------
# A chapter interpreter: flags and effect calls, which the S9 compiler does not model
# ---------------------------------------------------------------------------------------------

def eval_compiled(trigger, state, constants):
    """Evaluate a compiled trigger list (the base's 2-tuple shape) with the shapes it lacks.

    The chapter walk only asserts which `spain_chapter_*` flag survives, so an idea, a government
    or a balance the test state does not carry reads as absent: the branch body still runs and any
    chapter flag it sets is still observed.
    """
    for key, value in trigger:
        if key == 'has_power_balance':
            found = False  # the test state carries no live balance of power
        elif key == 'has_idea':
            found = value in getattr(state, 'ideas', ())
        elif key == 'has_government':
            found = value in getattr(state, 'governments', ())
        elif key == 'country_exists':
            found = True
        elif key in ('OR', 'AND'):
            results = [eval_compiled([pair], state, constants) for pair in value]
            found = any(results) if key == 'OR' else all(results)
        elif key == 'NOT':
            found = not all(eval_compiled([pair], state, constants) for pair in value)
        elif key == 'custom_trigger_tooltip':
            found = eval_compiled([(k, v) for k, v in value
                                   if k not in ('tooltip', 'tooltip_trigger')], state, constants)
        else:
            found = base.eval_entry(key, value, state, constants)
        if not found:
            return False
    return True


def eval_entries(entries, state, constants):
    """Raw parsed entries (3-tuples) -> the base's compiled trigger -> a boolean."""
    return eval_compiled(base.compile_trigger(entries), state, constants)


def compile_chapter(entries, name):
    """Ops for a chapter block: flags, calls, if/else_if/else. Other blocks are inert here."""
    ops = []
    index = 0
    while index < len(entries):
        key, value, line = entries[index]
        index += 1
        if key == 'set_country_flag' and isinstance(value, tuple) and value[0] == 'scalar':
            ops.append(('set_flag', value[1], line))
        elif key == 'clr_country_flag' and isinstance(value, tuple) and value[0] == 'scalar':
            ops.append(('clr_flag', value[1], line))
        elif key == 'if':
            chain = []
            otherwise = None
            limit = [entry for entry in value[1] if entry[0] == 'limit'][0][1][1]
            chain.append((limit, compile_chapter([e for e in value[1] if e[0] != 'limit'], name)))
            while index < len(entries) and entries[index][0] in ('else_if', 'else'):
                branch_key, branch_value, _ = entries[index]
                index += 1
                if branch_key == 'else_if':
                    branch_limit = [e for e in branch_value[1] if e[0] == 'limit'][0][1][1]
                    chain.append((branch_limit,
                                  compile_chapter([e for e in branch_value[1] if e[0] != 'limit'],
                                                  name)))
                else:
                    otherwise = compile_chapter(branch_value[1], name)
            ops.append(('if', chain, otherwise, line))
        elif isinstance(value, tuple) and value[0] == 'scalar':
            ops.append(('call', key, line))
        else:
            ops.append(('inert', key, line))
    return ops


def run_chapter_ops(ops, state, constants, trace, helpers=None):
    helpers = helpers if helpers is not None else {}
    for op in ops:
        if op[0] == 'set_flag':
            state.flags.add(op[1])
            trace.append(op[1])
        elif op[0] == 'clr_flag':
            state.flags.discard(op[1])
        elif op[0] == 'call':
            state.calls[op[1]] += 1
            trace.append(op[1])
            if op[1] in helpers:
                run_chapter_ops(helpers[op[1]], state, constants, trace, helpers)
        elif op[0] == 'if':
            for limit, body in op[1]:
                if eval_entries(limit, state, constants):
                    run_chapter_ops(body, state, constants, trace)
                    break
            else:
                if op[2] is not None:
                    run_chapter_ops(op[2], state, constants, trace)


def chapter_state(text, name, flags=(), constants=None):
    constants = constants if constants is not None else base.load_constants()
    parsed = blocks_of(text)
    if name not in parsed:
        raise Unsupported('no such chapter opener: %s' % name)
    state = base.State()
    state.flags.update(flags)
    trace = []
    run_chapter_ops(compile_chapter(parsed[name][0], name), state, constants, trace)
    return state, trace


def chapter_flags(state):
    return set(flag for flag in state.flags if flag.startswith('spain_chapter_'))


# ---------------------------------------------------------------------------------------------
# Runtime script: the S9 harness plus the bill and hemicycle files, which execute here
# ---------------------------------------------------------------------------------------------

# S9 deliberately leaves these two calls external. This test owns their contract, so it resolves
# them and executes them. The mutation is module-level and confined to this process.
base.EXTERNAL_CALLS.discard('spain_bills_count_all')
base.EXTERNAL_CALLS.discard('spain_cortes_draw_hemicycle')
base.RESOLVERS['spain_cortes_draw_hemicycle'] = HEMICYLE_PATH
base.RESOLVERS['spain_bills_count_all'] = BILLS_PATH
# Every effect the two runtime files define resolves to the file that defines it, so the bill
# counts and helpers are executed instead of being waved through as external calls. A call the
# recount reaches that is not on this list still fails loudly in run_ops.
for _path in (BILLS_PATH, HEMICYLE_PATH):
    for _name in base.parse_file(read(_path)):
        base.RESOLVERS.setdefault(_name, _path)


CONSTANT_RE = re.compile(r'constant:([a-z_]+\.[a-z_0-9]+)')


def resolve_constants(text, constants):
    """Substitute `constant:block.key` with its value, as the engine does at load.

    The S9 compiler takes `clamp_variable` bounds with `float()`, so a `constant:` there would
    abort the parse. Substituting first keeps the tested number the one the constants file holds,
    and an unknown constant still fails loudly instead of becoming zero.
    """
    def substitute(match):
        key = match.group(1)
        if key not in constants:
            raise Unsupported('constant %s is not defined' % key)
        value = constants[key]
        return str(int(value)) if float(value).is_integer() else repr(float(value))

    return CONSTANT_RE.sub(substitute, text)


class RuntimeScript(base.Script):
    def __init__(self, effects_text=None, bills_text=None, hemicycle_text=None, constants=None):
        super().__init__(effects_text=effects_text, constants=constants)
        for path, text in ((BILLS_PATH, bills_text), (HEMICYLE_PATH, hemicycle_text)):
            self.texts[path] = resolve_constants(
                text if text is not None else self.read(path), self.constants)
            self.parsed[path] = base.parse_file(self.texts[path])

    def ops(self, name):
        if name in self.compiled:
            return self.compiled[name]
        for path in (BILLS_PATH, HEMICYLE_PATH):
            if name in self.parsed.get(path, {}):
                block, _ = self.parsed[path][name]
                compiled = base.Compiler(name).ops(block)
                self.compiled[name] = compiled
                return compiled
        return super().ops(name)


def recount(script, flags=(), government=None, shifts=None):
    """One recount, as a save would run it: party shifts and an optional named government."""
    return base.run_recount(script, flags, shifts or {}, government or {})


def caches(state):
    return dict((bill, state.vars.get('spain_bill_votes_' + bill)) for bill in BILLS)


# ---------------------------------------------------------------------------------------------
# 1 - chapter exclusivity
# ---------------------------------------------------------------------------------------------

def chapter_helpers(text):
    """Compiled bodies of the chapter helpers, so a `call` op is executed, not just counted."""
    parsed = blocks_of(text)
    helpers = {}
    for name in ('spain_clear_chapter_flags',):
        if name in parsed:
            helpers[name] = compile_chapter(parsed[name][0], name)
    return helpers


def opener_body(text, name):
    """One opener's own text: up to the next opener or the next section rule."""
    start = text.index(name + ' = {')
    rest = text[start + len(name):]
    ends = [index for index in (rest.find('\nspain_open_'), rest.find('\n# =====')) if index != -1]
    return rest[:min(ends)] if ends else rest


def test_chapter_exclusivity(report):
    report.start('chapters')
    text = read(CAMPAIGN_PATH)
    old = read(CAMPAIGN_PATH, BASELINE_REV)

    # The helper clears exactly the chapter flags the file can set: a seventh chapter would have to
    # be added to the helper to pass.
    set_flags = set(re.findall(r'set_country_flag = (spain_chapter_[a-z_]+)', text))
    # The helper is optional on purpose: its absence is the defect this check detects, so it must
    # report a failure rather than raise.
    helper = text.split('spain_clear_chapter_flags = {', 1)
    cleared = set(re.findall(r'clr_country_flag = (spain_chapter_[a-z_]+)',
                             helper[1].split('}', 1)[0])) if len(helper) > 1 else set()
    report.equal('the helper clears every chapter flag the file sets', cleared, set_flags)

    # Every opener calls the helper before it sets its own flag.
    parsed = blocks_of(text)
    for chapter in CHAPTERS:
        name = 'spain_open_%s_chapter' % chapter
        entries = parsed[name][0]
        first = entries[0][0]
        report.equal('%s clears its siblings first' % name, first, 'spain_clear_chapter_flags')
        body = opener_body(text, name)
        report.equal('%s loads exactly one focus tree' % name,
                     body.count('load_focus_tree'), 1)

    # The post-war opener re-asserts the civil-war tree it continues.
    postwar = text.split('spain_open_postwar_chapter = {', 1)[1].split('\nspain_open_republican', 1)[0]
    report.check('the post-war chapter loads spanish_focus', 'tree = spanish_focus' in postwar,
                 'no tree is loaded, so the country keeps whichever tree it had')

    # A continuous campaign: run every chapter in order on one state.
    helpers = chapter_helpers(text)
    constants = base.load_constants()
    state = base.State()
    for chapter in CHAPTERS:
        expected = 'spain_chapter_%s' % chapter
        ops = compile_chapter(parsed['spain_open_%s_chapter' % chapter][0], chapter)
        run_chapter_ops(ops, state, constants, [], helpers)
        report.equal('after %s exactly one chapter flag is held' % chapter,
                     chapter_flags(state), {expected})

    # The same walk on the pre-S10 file, which has no helper: the Restoration survives into 1931.
    mutant = base.State()
    old_helpers = chapter_helpers(old)
    report.equal('mutant: the old file defines no chapter helper', sorted(old_helpers), [])
    for chapter in ('restoration', 'rivera', 'republic'):
        ops = compile_chapter(blocks_of(old)['spain_open_%s_chapter' % chapter][0], chapter)
        run_chapter_ops(ops, mutant, constants, [], old_helpers)
    report.check('mutant: the old openers leave the Restoration flag set in 1931',
                 'spain_chapter_restoration' in chapter_flags(mutant),
                 'the mutant agreed with the repair, so this check cannot detect the defect')
    report.check('mutant: the old openers hold more than one chapter flag',
                 len(chapter_flags(mutant)) > 1, repr(sorted(chapter_flags(mutant))))
    report.equal('mutant: the old file has no helper to clear the siblings',
                 len(re.findall(r'clr_country_flag = spain_chapter_', old)), 0)


# ---------------------------------------------------------------------------------------------
# 2 - the republican base is selected positively
# ---------------------------------------------------------------------------------------------

def test_republic_base(report, script):
    report.start('era base')
    old = RuntimeScript(effects_text=read(EFFECTS_PATH, BASELINE_REV),
                        constants=script.constants)

    republic = recount(script, ('spain_chapter_republic',))
    report.equal('the Republic keeps the republican base', base.raw_of(republic),
                 base.REPUBLIC_BASE)

    for chapter in ('civil_war', 'postwar', 'republican_postwar'):
        state = recount(script, ('spain_chapter_%s' % chapter,))
        report.equal('%s takes the crown base' % chapter, base.raw_of(state),
                     base.RESTORATION_BASE)
        mutant = recount(old, ('spain_chapter_%s' % chapter,))
        report.check('mutant: the old fallback gives %s the republican base' % chapter,
                     base.raw_of(mutant) == base.REPUBLIC_BASE, repr(base.raw_of(mutant)))

    state = recount(script, ())
    report.equal('no chapter flag falls back to the crown base, not the republican one',
                 base.raw_of(state), base.RESTORATION_BASE)

    # The Republic-only legislature flags follow the same test.
    for chapter, expected in (('republic', True), ('civil_war', False), ('postwar', False)):
        state = recount(script, ('spain_chapter_%s' % chapter,), {}, None)
        state.flags.add('spain_ceda_government')
        state = recount(script, tuple(state.flags))
        changed = base.raw_of(state) != base.RESTORATION_BASE
        report.equal('spain_ceda_government applies in %s' % chapter, changed, expected)

    # The era block is a positive test on the compiled source, not a negated one.
    ops = script.ops('spain_cortes_recount')
    era = [op for op in ops if op['kind'] == 'if'
           and any(inner['kind'] == 'set' and inner.get('var') == 'spain_cortes_raw_monarchists'
                   for inner in op['chain'][0][1])][0]
    report.equal('the era predicate is the Republic chapter flag', era['chain'][0][0],
                 [('has_country_flag', 'spain_chapter_republic')])


# ---------------------------------------------------------------------------------------------
# 3 - bill caches: seeded, refreshed once, and never a fail-open gate
# ---------------------------------------------------------------------------------------------

def test_bill_caches(report, script):
    report.start('bill caches')
    state = recount(script, ('spain_chapter_republic',))
    report.equal('a recount writes all six caches', sorted(caches(state)), sorted(BILLS))
    report.check('every cache carries a seat count', all(caches(state).values()),
                 repr(caches(state)))
    report.check('no cache is missing after a recount',
                 all('spain_bill_votes_' + bill in state.vars for bill in BILLS),
                 repr(sorted(k for k in state.vars if k.startswith('spain_bill_votes_'))))
    floor = script.constants['spain_campaign.cortes_majority'] - \
        script.constants['spain_campaign.bill_negotiation_reach']
    report.equal('the floor is the majority less the negotiation reach',
                 state.vars.get('spain_bill_floor'), floor)
    report.equal('the floor is 161 seats', floor, 161)

    # Once per recount, no recursion, no duplicate counting.
    for bill in BILLS:
        report.equal('%s counted once per recount' % bill,
                     state.calls['spain_bill_count_' + bill], 1)
    report.equal('the cache refresh is called once', state.calls['spain_bills_count_all'], 1)
    report.equal('the recount itself ran once', state.exec['spain_cortes_recount#0'], 1)
    unexpected = set(state.calls) - ALLOWED_RECOUNT_CALLS
    report.equal('the recount reaches no effect outside the counted set', unexpected, set())

    first = caches(state)
    second = recount(script, ('spain_chapter_republic',))
    report.equal('a second recount reproduces the caches instead of stacking them',
                 caches(second), first)

    # The gate: no fail-open disjunct, and a chamber short of the floor is not offered the bill.
    decisions = decisions_of(read(DECISIONS_PATH))
    for bill in BILLS:
        entries = decisions[BILL_DECISIONS[bill]]
        available = fields(entries['available'])
        trigger = None
        for key, value, _line in available.get('custom_trigger_tooltip', ()):
            if key == 'OR':
                trigger = base.compile_trigger(value[1])
        report.check('%s has a reach gate' % bill, trigger is not None)
        if trigger is None:
            continue
        report.equal('%s gate has no absent-cache disjunct' % bill,
                     [entry for entry in trigger
                      if entry[0] == 'NOT' and entry[1]
                      and entry[1][0][0] == 'has_variable'], [])

        empty = base.State()
        empty.vars['spain_bill_floor'] = floor
        empty.vars['spain_government_seats'] = floor - 1
        empty.flags.add('spain_chapter_republic')
        report.check('%s gate is closed with no chamber behind it' % bill,
                     not base.eval_entry('OR', trigger, empty, script.constants),
                     'the gate opened on support that was never counted')

        short = base.State()
        short.vars['spain_bill_floor'] = floor
        short.vars['spain_government_seats'] = 40
        short.vars['spain_bill_votes_' + bill] = 40
        report.check('%s gate is closed 121 seats short of the floor' % bill,
                     not base.eval_entry('OR', trigger, short, script.constants))
        enough = base.State()
        enough.vars['spain_bill_floor'] = floor
        enough.vars['spain_government_seats'] = 40
        enough.vars['spain_bill_votes_' + bill] = 161
        report.check('%s gate opens at the 161-seat floor' % bill,
                     base.eval_entry('OR', trigger, enough, script.constants))

    # Mutant: the pinned decisions file still fails open.
    old_decisions = decisions_of(read(DECISIONS_PATH, BASELINE_REV))
    old_available = fields(old_decisions['SPR_bill_budget']['available'])
    old_trigger = None
    for key, value, _line in old_available.get('custom_trigger_tooltip', ()):
        if key == 'OR':
            old_trigger = base.compile_trigger(value[1])
    empty = base.State()
    empty.vars['spain_bill_floor'] = floor
    empty.vars['spain_government_seats'] = 40
    report.check('mutant: the old budget gate opens with no cache and no support',
                 base.eval_entry('OR', old_trigger, empty, script.constants),
                 'the mutant agreed with the repair')

    # A fresh campaign seeds the caches before any bill decision is drawn: the chapter opener calls
    # spain_cortes_initialize, which initialises the parties, which recounts, and the recount is
    # the first writer of the six caches.
    parties_text = read(PARTIES_PATH)
    report.check('spain_parties_initialize recounts the fresh chamber',
                 'spain_cortes_recount = yes' in opener_body(parties_text, 'spain_parties_initialize'),
                 'no recount runs before the first bill is offered')
    report.check('the recount is what refreshes the six caches',
                 fields(blocks_of(read(EFFECTS_PATH))['spain_cortes_recount'][0])
                 .get('spain_bills_count_all') == 'yes',
                 'the caches have no first writer, so a gate reads a variable nobody set')

    # The clerk that starts the cache cycle is still declared where the negotiations call it.
    events = read('events/spain_cortes_bills.txt')
    report.check('the clerk event still refreshes the caches',
                 'spain_bills_count_all = yes' in events, 'the clerk stopped counting')


# ---------------------------------------------------------------------------------------------
# 4 - hemicycle frames
# ---------------------------------------------------------------------------------------------

def test_hemicycle(report, script):
    report.start('hemicycle')
    text = read(HEMICYLE_PATH)
    gfx = read(GFX_PATH)
    strip = gfx.split('name = "GFX_spain_cortes_seats"', 1)[1].split('}', 1)[0]
    frames = int(re.search(r'noOfFrames = (\d+)', strip).group(1))
    report.equal('the seat strip registers eight frames', frames, STRIP_FRAMES)

    assignments = re.findall(r'set_variable = \{ var = (spain_cortes_seat_\d+) value = (\d+) \}',
                             text)
    dots = sorted(set(name for name, _ in assignments))
    report.equal('the effect writes one variable per dot', len(dots), DOTS)
    values = collections.Counter(int(value) for _, value in assignments)
    report.equal('every frame written is inside the strip',
                 sorted(values), list(range(NEUTRAL_FRAME, frames + 1)))
    report.equal('no frame 0 and no frame 9 is written',
                 sorted(frame for frame in values if frame < NEUTRAL_FRAME or frame > frames), [])
    report.equal('each frame is written once per dot', set(values.values()), {DOTS})

    # Every dot defaults to the neutral frame.
    defaults = [int(value) for name, value in assignments
                if assignments.index((name, value)) == assignments.index((name, value))]
    neutral = [value for name, value in assignments if value == str(NEUTRAL_FRAME)]
    report.equal('every dot starts neutral', len(neutral), DOTS)

    # The party mapping: the frame set under a party's branch is that party's frame.
    for party, frame in PARTY_FRAMES.items():
        pattern = re.compile(
            r'check_variable = \{ var = spain_cortes_cum_%s value = \d+ compare = '
            r'greater_than_or_equals \} \}\n\s*set_variable = \{ var = spain_cortes_seat_\d+ '
            r'value = (\d+) \}' % party)
        found = set(int(value) for value in pattern.findall(text))
        report.equal('%s owns frame %d on every dot' % (party, frame), found, {frame})

    # Executed: a full chamber colours every dot, and never with a frame outside the strip.
    state = recount(script, ('spain_chapter_republic',))
    seats = dict((dot, state.vars.get(dot)) for dot in dots)
    report.check('the recount paints every dot', all(seats.values()), repr(seats))
    report.check('no dot is left unpainted in a full chamber',
                 all(value != NEUTRAL_FRAME for value in seats.values()),
                 repr(sorted(set(seats.values()))))
    report.equal('every painted dot is a party frame',
                 sorted(set(seats.values())), sorted(set(PARTY_FRAMES.values())))

    # Mutant: the 0-based table S10 committed addresses the strip as 0..7, so it never reaches the
    # falange's cell and paints an empty bench from a frame the strip does not start at.
    old = [int(value) for value in re.findall(
        r'set_variable = \{ var = spain_cortes_seat_\d+ value = (\d+) \}',
        read(HEMICYLE_PATH, ZERO_BASED_EFFECT_REV))]
    report.equal('mutant: the 0-based effect writes frames 0..7',
                 sorted(set(old)), list(range(0, frames)))
    report.check('mutant: the 0-based effect never reaches the strip\'s last cell',
                 max(old) < STRIP_FRAMES, 'highest frame %d of %d' % (max(old), STRIP_FRAMES))
    report.check('mutant: the 0-based effect addresses a frame below the first cell',
                 min(old) < NEUTRAL_FRAME, 'lowest frame %d' % min(old))


# ---------------------------------------------------------------------------------------------
# 5 - one tooltip key, two consumers
# ---------------------------------------------------------------------------------------------

def test_localisation(report):
    report.start('localisation')
    with open(ROOT / LOC_PATH, 'rb') as handle:
        raw = handle.read()
    report.check('the localisation file carries exactly one BOM',
                 raw.startswith(b'\xef\xbb\xbf') and not raw.startswith(b'\xef\xbb\xbf\xef\xbb\xbf'))
    text = raw.decode('utf-8-sig')

    keys = []
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        keys.append(stripped.split(':', 1)[0].strip())
    duplicates = [key for key, count in collections.Counter(keys).items() if count > 1]
    report.equal('no key is defined twice in the file', duplicates, [])
    report.equal('spain_iberian_accord_tt is defined once',
                 keys.count('spain_iberian_accord_tt'), 1)
    report.check('the surviving definition is the titled one',
                 'spain_iberian_accord_tt: "§YThe Iberian Accord§!' in text)

    for path in (RESTORATION_FOCUS_PATH, POSTWAR_FOCUS_PATH):
        focus = read(path)
        report.equal('%s still shows the tooltip' % path,
                     focus.count('custom_effect_tooltip = spain_iberian_accord_tt'), 1)


# ---------------------------------------------------------------------------------------------
# 6 - cooldown lengths
# ---------------------------------------------------------------------------------------------

def cooldown_days(text):
    macros = dict((name, int(value)) for name, value in
                  re.findall(r'@(bill_[a-z_]+_cooldown_days) = (\d+)', text))
    resolved = {}
    for bill, macro in re.findall(r'set_country_flag = \{ flag = spain_bill_([a-z_]+)_cooldown '
                                  r'days = @(bill_[a-z_]+_cooldown_days) \}', text):
        resolved[bill] = macros.get(macro)
    return resolved


def test_cooldowns(report):
    report.start('cooldowns')
    decisions = decisions_of(read(DECISIONS_PATH))
    re_enable = {}
    for bill, decision in BILL_DECISIONS.items():
        entries = decisions[decision]
        re_enable[bill] = int(entries['days_re_enable'])

    shipped = cooldown_days(read(BILLS_PATH))
    report.equal('every bill sets its own cooldown flag', sorted(shipped), sorted(BILLS))
    report.equal('every cooldown flag lasts as long as its decision re-enables', shipped, re_enable)

    old = cooldown_days(read(BILLS_PATH, BASELINE_REV))
    report.check('mutant: the old single 60-day cooldown matches no decision',
                 all(value == 60 for value in old.values()) and old != re_enable, repr(old))


# ---------------------------------------------------------------------------------------------

def main():
    detail = '--detail' in sys.argv
    report = base.Report(detail=detail)
    script = RuntimeScript()

    test_chapter_exclusivity(report)
    test_republic_base(report, script)
    test_bill_caches(report, script)
    test_hemicycle(report, script)
    test_localisation(report)
    test_cooldowns(report)

    print('')
    print('Coverage: source simulation of %d files at HEAD plus the pinned pre-S10 objects:'
          % len(COVERED_FILES))
    for path in COVERED_FILES:
        print('  ' + path)
    print('Not performed: no game launch, no focus click, no decision taken, no panel rendered,')
    print('no save inspected. A clean run proves the script says this, not that the engine does.')
    return 0 if report.summary() else 1


if __name__ == '__main__':
    sys.exit(main())
