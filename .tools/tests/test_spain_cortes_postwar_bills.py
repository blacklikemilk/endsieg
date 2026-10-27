"""Regression test: the postwar chapters keep their legislation, and the checker reads the bills file.

S10 made the six `spain_chapter_*` flags exclusive, which left `common/decisions/spain_cortes.txt`
gating every bill on the Restoration, the Directory and the Republic only. Both postwar chapters
therefore inherited nothing and all six bill decisions disappeared while the `SPR_cortes` category
stayed visible. The same reform added `spain_bills_count_all` to the recount, and the party checker
reported it as an unknown effect because its registry never read the file that defines it.

Four facts are asserted against the shipped source rather than described:

    1. every bill is visible in both postwar chapters, and the chapter set of every bill is exactly
       its pre-S11 chapter set plus the two postwar chapters: no chapter was added to a bill that
       never offered it, and no chapter was dropped;
    2. the postwar gates name `spain_chapter_postwar` and `spain_chapter_republican_postwar` with an
       explicit `has_country_flag`, never through a `NOT`, so S10's exclusivity keeps working;
    3. availability did not become a chapter question: a postwar chamber short of the floor still
       refuses the bill, and one at the floor still opens it, whether or not the chapter flag is
       held. Every field of the file other than the six `visible` blocks is token-identical to the
       pinned pre-change source, so no cost, `days_re_enable`, gate or AI weight moved;
    4. `tools/check_spain_parties.py` exits 0 in this tree, the pre-change checker fails on the same
       tree, and two shadow trees — one with an injected unknown effect, one with the
       `spain_bills_count_all` definition deleted — both fail. A clean run alone would prove nothing.

The pre-change source is read from the immutable pre-S11 commit, and the pre-change checker is
executed from that commit, so both mutants are the real defect and not a paraphrase of it.

This test reuses the harness of `.tools/tests/test_spain_cortes_recount.py` and the decision helpers
of `.tools/tests/test_spain_cortes_runtime.py`. It is a source and tool simulation: no decision was
drawn in a game, no panel rendered, and the game was never launched.

Run from the repository root:

    python .tools/tests/test_spain_cortes_postwar_bills.py           # exit 0 = pass
    python .tools/tests/test_spain_cortes_postwar_bills.py --detail  # print every check
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# The test imports the checker from tools/, which would otherwise leave a __pycache__ behind in a
# directory that is not ignored.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / 'tools'))

import test_spain_cortes_recount as base  # noqa: E402  (the S9 harness, reused on purpose)
import test_spain_cortes_runtime as runtime  # noqa: E402  (decision parsing and trigger evaluation)
import check_spain_parties as checker  # noqa: E402  (the checker under test)

DECISIONS_PATH = 'common/decisions/spain_cortes.txt'
CHECKER_PATH = 'tools/check_spain_parties.py'
BILLS_PATH = 'common/scripted_effects/spain_cortes_bills.txt'

# The pre-S11 tree, pinned by full object name so it stays a mutant after this repair is committed.
PRE_S11_REV = '5ad0945ad1a92944a258a5097680a220cb1c7af6'

# Every file this test reads or stages, printed in the coverage footer.
COVERED_FILES = (DECISIONS_PATH, CHECKER_PATH, BILLS_PATH,
                 'common/scripted_effects/spain_cortes_effects.txt',
                 'common/scripted_effects/spain_cortes_parties.txt',
                 'common/scripted_effects/spain_campaign_effects.txt',
                 'common/scripted_triggers/spain_campaign_triggers.txt')

BILLS = ('budget', 'agrarian', 'labour', 'army', 'statute', 'electoral')
BILL_DECISIONS = {
    'budget': 'SPR_bill_budget',
    'agrarian': 'SPR_bill_agrarian_reform',
    'labour': 'SPR_bill_labour_charter',
    'army': 'SPR_bill_army_budget',
    'statute': 'SPR_bill_regional_statute',
    'electoral': 'SPR_bill_electoral_law',
}
CHAPTERS = ('restoration', 'rivera', 'republic', 'civil_war', 'postwar', 'republican_postwar')
POSTWAR_CHAPTERS = ('postwar', 'republican_postwar')

# The chapters this card adds to every bill's visibility.
ADDED_CHAPTERS = frozenset(POSTWAR_CHAPTERS)

# Everything the checker reads, taken from the checker itself so the shadow tree cannot drift,
# plus the bills file this card is about. That path is added unconditionally: the pre-change
# checker's registry omits it, and a test that raised on the pre-change source instead of reporting
# a failed check would prove nothing about what it can detect.
def checker_files():
    registry = list(checker.EFFECTS) + list(getattr(checker, 'REGISTRY_ONLY', []))
    files = [checker.DECISIONS, checker.CONSTANTS, checker.LOC, checker.CATEGORY] + registry
    if BILLS_PATH not in files:
        files.append(BILLS_PATH)
    return files


SHADOW_FILES = checker_files()


# ---------------------------------------------------------------------------------------------
# Decisions: visible blocks and the parsed fields around them
# ---------------------------------------------------------------------------------------------

def visible_trigger(decisions, decision):
    """The compiled hidden trigger of one decision's `visible` block, or None."""
    entries = decisions.get(decision)
    if entries is None or 'visible' not in entries:
        return None
    for key, value, _line in entries['visible']:
        if key == 'hidden_trigger' and value[0] == 'block':
            return base.compile_trigger(value[1])
    return None


def chapters_named(trigger):
    """Every `spain_chapter_*` flag a compiled trigger names, with its prefix stripped."""
    found = set()

    def walk(entries):
        for key, value in entries:
            if key == 'has_country_flag' and isinstance(value, str) \
                    and value.startswith('spain_chapter_'):
                found.add(value[len('spain_chapter_'):])
            elif isinstance(value, list):
                walk(value)

    walk(trigger)
    return found


def mentions_flag(trigger, flag):
    """Whether a compiled trigger names this flag anywhere, at any depth."""
    for key, value in trigger:
        if key == 'has_country_flag' and value == flag:
            return True
        if isinstance(value, list) and mentions_flag(value, flag):
            return True
    return False


def shape(entries):
    """Parsed entries with their line numbers dropped, so two files compare structurally."""
    out = []
    for key, value, _line in entries:
        if value[0] == 'block':
            out.append((key, ('block', shape(value[1]))))
        else:
            out.append((key, value))
    return out


def negated_chapters(trigger):
    """Chapter flags reached through a NOT, which S10's exclusivity makes a fail-open gate."""
    found = []

    def walk(entries, negated):
        for key, value in entries:
            if key == 'NOT' and isinstance(value, list):
                walk(value, True)
            elif key == 'has_country_flag' and isinstance(value, str) \
                    and value.startswith('spain_chapter_') and negated:
                found.append(value)
            elif isinstance(value, list):
                walk(value, negated)

    walk(trigger, False)
    return found


def flag_state(chapter=None, initialized=True):
    state = base.State()
    if initialized:
        state.flags.add('spain_campaign_initialized')
    if chapter is not None:
        state.flags.add('spain_chapter_' + chapter)
    return state


def visible_in(trigger, chapter, constants):
    return runtime.eval_compiled(trigger, flag_state(chapter), constants)


def strip_visible(text):
    """Tokens of the file with every `visible` block removed: comments never reach the list."""
    tokens = base.tokenize(text)
    out = []
    index = 0
    while index < len(tokens):
        kind, value, _line = tokens[index]
        if (kind == 'word' and value == 'visible' and index + 2 < len(tokens)
                and tokens[index + 1][0] == '=' and tokens[index + 2][0] == '{'):
            depth = 0
            index += 2
            while index < len(tokens):
                if tokens[index][0] == '{':
                    depth += 1
                elif tokens[index][0] == '}':
                    depth -= 1
                    if depth == 0:
                        index += 1
                        break
                index += 1
            continue
        out.append((kind, value))
        index += 1
    return out


def count_visible(text):
    return len(re.findall(r'^\t\tvisible = \{', text, re.M))


# ---------------------------------------------------------------------------------------------
# 1 - visibility is a chapter question
# ---------------------------------------------------------------------------------------------

def test_postwar_visibility(report, decisions, old_decisions, constants):
    report.start('visibility')
    for bill in BILLS:
        decision = BILL_DECISIONS[bill]
        trigger = visible_trigger(decisions, decision)
        report.check('%s has a visible hidden trigger' % bill, trigger is not None)
        if trigger is None:
            continue

        # The pre-S11 chapter set is the baseline; this card adds the two postwar chapters to it.
        old_trigger = visible_trigger(old_decisions, decision)
        old_chapters = chapters_named(old_trigger) if old_trigger is not None else set()
        report.equal('%s kept every chapter it already served' % bill,
                     old_chapters - chapters_named(trigger), set())
        report.equal('%s gained exactly the two postwar chapters' % bill,
                     chapters_named(trigger) - old_chapters, ADDED_CHAPTERS)
        report.equal('%s names no chapter outside its chapter set' % bill,
                     chapters_named(trigger) - set(CHAPTERS), set())

        for chapter in CHAPTERS:
            report.equal('%s visible in %s' % (bill, chapter),
                         visible_in(trigger, chapter, constants),
                         chapter in old_chapters or chapter in ADDED_CHAPTERS)
        report.equal('%s visible with no chapter flag at all' % bill,
                     visible_in(trigger, None, constants), False)

        # Explicit tests, never a NOT: the exclusivity S10 established must not be undone.
        for chapter in POSTWAR_CHAPTERS:
            report.check('%s names %s explicitly' % (bill, chapter),
                         mentions_flag(trigger, 'spain_chapter_' + chapter), repr(trigger))
        report.equal('%s reaches no chapter flag through a NOT' % bill,
                     negated_chapters(trigger), [])
        report.check('%s still requires the campaign flag' % bill,
                     mentions_flag(trigger, 'spain_campaign_initialized'), repr(trigger))


# ---------------------------------------------------------------------------------------------
# 2 - availability stays a support question
# ---------------------------------------------------------------------------------------------

def available_trigger(decisions, decision):
    entries = decisions.get(decision)
    if entries is None or 'available' not in entries:
        return None
    return base.compile_trigger(entries['available'])


def test_postwar_availability(report, script, decisions):
    """A postwar chamber short of the floor still refuses; one at the floor still opens.

    The states are the real recount's: `spain_cortes_recount` in the postwar chapter writes the
    caches and the floor, so the only values varied here are the support the bill needs.
    """
    report.start('availability')
    floor = script.constants['spain_campaign.cortes_majority'] - \
        script.constants['spain_campaign.bill_negotiation_reach']
    for chapter in POSTWAR_CHAPTERS:
        counted = runtime.recount(script, ('spain_chapter_' + chapter,))
        report.equal('%s chamber counts a floor' % chapter,
                     counted.vars.get('spain_bill_floor'), floor)
        for bill in BILLS:
            decision = BILL_DECISIONS[bill]
            trigger = available_trigger(decisions, decision)
            report.check('%s has an available gate in %s' % (bill, chapter), trigger is not None)
            if trigger is None:
                continue

            short = runtime.recount(script, ('spain_chapter_' + chapter,))
            short.vars['spain_bill_votes_' + bill] = 40
            short.vars['spain_government_seats'] = 40
            report.equal('%s refused by a 40-seat postwar chamber in %s' % (bill, chapter),
                         runtime.eval_compiled(trigger, short, script.constants), False)

            enough = runtime.recount(script, ('spain_chapter_' + chapter,))
            enough.vars['spain_bill_votes_' + bill] = floor
            enough.vars['spain_government_seats'] = 40
            report.equal('%s opened at the floor by a postwar chamber in %s' % (bill, chapter),
                         runtime.eval_compiled(trigger, enough, script.constants), True)

            # The refusal is about seats, not about the chapter: the same weak chamber is refused
            # with the chapter flag cleared, so no availability gate reads a chapter at all.
            unchaptered = runtime.recount(script, ())
            unchaptered.vars['spain_bill_votes_' + bill] = 40
            unchaptered.vars['spain_government_seats'] = 40
            report.equal('%s refusal in %s does not depend on the chapter flag'
                         % (bill, chapter),
                         runtime.eval_compiled(trigger, unchaptered, script.constants), False)


# ---------------------------------------------------------------------------------------------
# 3 - nothing but the six visible blocks moved
# ---------------------------------------------------------------------------------------------

def test_arithmetic_untouched(report, decisions, old_decisions):
    report.start('arithmetic')
    shipped = runtime.read(DECISIONS_PATH)
    pinned = runtime.read(DECISIONS_PATH, PRE_S11_REV)

    report.equal('the shipped file has six bill decisions', len(decisions), len(old_decisions))
    report.equal('the shipped file has six visible blocks', count_visible(shipped), len(BILLS))
    report.equal('the pinned file has six visible blocks', count_visible(pinned), len(BILLS))
    report.equal('everything outside the visible blocks is unchanged',
                 strip_visible(shipped), strip_visible(pinned))

    for bill in BILLS:
        decision = BILL_DECISIONS[bill]
        for field in ('cost', 'days_re_enable', 'icon'):
            report.equal('%s %s unchanged' % (bill, field),
                         decisions[decision].get(field), old_decisions[decision].get(field))
        for field in ('available', 'complete_effect', 'ai_will_do'):
            report.equal('%s %s unchanged' % (bill, field),
                         shape(decisions[decision][field]),
                         shape(old_decisions[decision][field]))


# ---------------------------------------------------------------------------------------------
# 4 - the checker reads the bills file and still catches a genuinely unknown effect
# ---------------------------------------------------------------------------------------------

def run_checker(script_path, args=(), cwd=None):
    result = subprocess.run([sys.executable, str(script_path), *args],
                            cwd=str(cwd or ROOT), capture_output=True)
    return result.returncode, (result.stdout + result.stderr).decode('utf-8', 'replace')


def shadow_tree(mutate=None):
    """A tree holding exactly the files the checker reads, optionally with one of them mutated."""
    root = Path(tempfile.mkdtemp(prefix='s11-shadow-'))
    for relative in SHADOW_FILES:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(ROOT / relative, 'r', encoding='utf-8-sig') as handle:
            text = handle.read()
        if mutate is not None and relative == mutate[0]:
            text = mutate[1](text)
        with open(destination, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
    return root


def inject_unknown_effect(text):
    return text.replace('spain_bills_count_all = yes',
                        'spain_bills_count_all = yes\n\tspain_bill_count_phantom = yes', 1)


def drop_count_all(text):
    return re.sub(r'spain_bills_count_all = \{[^}]*\}\n', '', text, count=1)


# The two campaign files the S12b card added to the registry: withdrawing one definition from each
# proves the entry is load-bearing rather than a blanket allowance.
CAMPAIGN_EFFECTS_PATH = 'common/scripted_effects/spain_campaign_effects.txt'
CAMPAIGN_TRIGGERS_PATH = 'common/scripted_triggers/spain_campaign_triggers.txt'


def withdraw_loyalty_helper(text):
    return text.replace('\nspain_loyalty_gain_small = {',
                        '\nspain_loyalty_gain_small_withdrawn = {', 1)


def withdraw_cortes_live_trigger(text):
    return text.replace('\nspain_restoration_cortes_live = {',
                        '\nspain_restoration_cortes_live_withdrawn = {', 1)


def test_checker(report):
    report.start('checker')
    registry = list(checker.EFFECTS) + list(getattr(checker, 'REGISTRY_ONLY', []))
    report.check('the registry reads the bills file', BILLS_PATH in registry, repr(registry))
    report.check('the registry still reads the effects file',
                 'common/scripted_effects/spain_cortes_effects.txt' in registry, repr(registry))
    report.check('the registry reads the campaign effects the S12 call sites resolve against',
                 CAMPAIGN_EFFECTS_PATH in registry, repr(registry))
    report.check('the registry reads the campaign triggers the S12 call sites resolve against',
                 CAMPAIGN_TRIGGERS_PATH in registry, repr(registry))

    code, output = run_checker(ROOT / CHECKER_PATH)
    report.equal('the shipped checker passes on this tree', code, 0)
    report.check('the passing run says so', 'no dangling references' in output, output.strip())

    # Mutant: the pre-change checker on the same tree still fails on the effect it could not see.
    old_checker = Path(tempfile.mkdtemp(prefix='s11-oldchecker-')) / 'old_checker.py'
    old_checker.write_text(runtime.read(CHECKER_PATH, PRE_S11_REV), encoding='utf-8')
    old_code, old_output = run_checker(old_checker)
    report.equal('the pre-change checker fails on this tree', old_code, 1)
    report.check('the pre-change checker names the bills effect',
                 'spain_cortes_effects.txt calls unknown effect: spain_bills_count_all' in old_output,
                 old_output.strip())

    # Control for the two shadow controls: an unmutated shadow passes, so a shadow failure is the
    # mutation and not the staging.
    shadow = shadow_tree()
    try:
        code, output = run_checker(ROOT / CHECKER_PATH, (str(shadow),))
        report.equal('an unmutated shadow tree passes', code, 0)
        report.check('the shadow run reports its own root', str(shadow) in output, output.strip())
    finally:
        shutil.rmtree(shadow, ignore_errors=True)

    # Negative control 1: a name nothing defines must fail, or the checker cannot see unknowns.
    shadow = shadow_tree(('common/scripted_effects/spain_cortes_effects.txt', inject_unknown_effect))
    try:
        code, output = run_checker(ROOT / CHECKER_PATH, (str(shadow),))
        report.equal('an injected unknown effect fails the checker', code, 1)
        report.check('the injected name is the finding',
                     'spain_cortes_effects.txt calls unknown effect: spain_bill_count_phantom'
                     in output, output.strip())
    finally:
        shutil.rmtree(shadow, ignore_errors=True)

    # Negative control 2: deleting the definition proves the bills file is what resolves the call.
    shadow = shadow_tree((BILLS_PATH, drop_count_all))
    try:
        report.check('the shadow really lost the definition',
                     'spain_bills_count_all' not in
                     (shadow / BILLS_PATH).read_text(encoding='utf-8'))
        code, output = run_checker(ROOT / CHECKER_PATH, (str(shadow),))
        report.equal('deleting the definition fails the checker', code, 1)
        report.check('the deleted definition is the finding',
                     'spain_cortes_effects.txt calls unknown effect: spain_bills_count_all'
                     in output, output.strip())
    finally:
        shutil.rmtree(shadow, ignore_errors=True)

    # Negative control 3: the campaign effects entry resolves `spain_loyalty_gain_small` and nothing
    # else, so withdrawing that one definition must put the finding back.
    shadow = shadow_tree((CAMPAIGN_EFFECTS_PATH, withdraw_loyalty_helper))
    try:
        report.check('the campaign effects shadow really lost the helper',
                     '\nspain_loyalty_gain_small = {' not in
                     (shadow / CAMPAIGN_EFFECTS_PATH).read_text(encoding='utf-8'))
        code, output = run_checker(ROOT / CHECKER_PATH, (str(shadow),))
        report.equal('withdrawing the loyalty helper fails the checker', code, 1)
        report.check('the withdrawn helper is the finding',
                     'spain_cortes_parties.txt calls unknown effect: spain_loyalty_gain_small'
                     in output, output.strip())
    finally:
        shutil.rmtree(shadow, ignore_errors=True)

    # Negative control 4: the campaign triggers entry resolves the chapter gate the government
    # effects ask for. Without it the trigger is a name nothing defines.
    shadow = shadow_tree((CAMPAIGN_TRIGGERS_PATH, withdraw_cortes_live_trigger))
    try:
        report.check('the campaign triggers shadow really lost the gate',
                     '\nspain_restoration_cortes_live = {' not in
                     (shadow / CAMPAIGN_TRIGGERS_PATH).read_text(encoding='utf-8'))
        code, output = run_checker(ROOT / CHECKER_PATH, (str(shadow),))
        report.equal('withdrawing the chapter gate fails the checker', code, 1)
        report.check('the withdrawn gate is the finding',
                     'spain_cortes_parties.txt calls unknown effect: spain_restoration_cortes_live'
                     in output, output.strip())
    finally:
        shutil.rmtree(shadow, ignore_errors=True)

    # Negative control 5: a registry input that is missing from the tree must stop the run, not be
    # skipped. The checker reads every file it names, so an absent one is a refusal by construction.
    shadow = shadow_tree()
    try:
        (shadow / CAMPAIGN_TRIGGERS_PATH).unlink()
        code, output = run_checker(ROOT / CHECKER_PATH, (str(shadow),))
        report.check('a missing registry input fails the checker instead of being skipped',
                     code != 0, output.strip())
        report.check('the missing input is named in the failure',
                     'spain_campaign_triggers.txt' in output, output.strip())
    finally:
        shutil.rmtree(shadow, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# 5 - the pre-change decisions file has the defect
# ---------------------------------------------------------------------------------------------

def test_mutant(report, old_decisions, constants):
    report.start('mutant')
    for bill in BILLS:
        trigger = visible_trigger(old_decisions, BILL_DECISIONS[bill])
        report.check('mutant: %s has a visible block' % bill, trigger is not None)
        if trigger is None:
            continue
        for chapter in POSTWAR_CHAPTERS:
            report.check('mutant: %s is invisible in %s' % (bill, chapter),
                         visible_in(trigger, chapter, constants) is False,
                         'the pre-S11 source already offered the bill here, so this test cannot '
                         'detect the defect')
        report.equal('mutant: %s named no postwar chapter' % bill,
                     chapters_named(trigger) & ADDED_CHAPTERS, set())


# ---------------------------------------------------------------------------------------------

def main():
    report = base.Report(detail='--detail' in sys.argv)
    script = runtime.RuntimeScript()
    constants = script.constants
    decisions = runtime.decisions_of(runtime.read(DECISIONS_PATH))
    old_decisions = runtime.decisions_of(runtime.read(DECISIONS_PATH, PRE_S11_REV))

    test_postwar_visibility(report, decisions, old_decisions, constants)
    test_postwar_availability(report, script, decisions)
    test_arithmetic_untouched(report, decisions, old_decisions)
    test_checker(report)
    test_mutant(report, old_decisions, constants)

    print('')
    print('Coverage: source and tool simulation of %d files at HEAD plus the pinned pre-S11 objects:'
          % len(COVERED_FILES))
    for path in COVERED_FILES:
        print('  ' + path)
    print('Shadow trees staged from the checker\'s own file list: %d files' % len(SHADOW_FILES))
    print('Not performed: no game launch, no decision drawn, no panel rendered, no save inspected.')
    print('A clean run proves the script and the checker say this, not that the engine does it.')
    return 0 if report.summary() else 1


if __name__ == '__main__':
    sys.exit(main())
