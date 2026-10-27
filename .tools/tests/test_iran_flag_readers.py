"""Regression test: Iran's continuity gate and the readers for the flags it now consumes.

The I1 and I3 audits of the Iran package found the same defect twice: the chapters write
outcome flags that nothing reads, and the cross-era continuity gate in
`common/scripted_triggers/iran_continuity.txt` only ever looked at flags the 1910-18
chapter sets. A 1919, 1925 and 1936 boundary therefore could not tell how the previous
chapter ended, and the decisions and events that should react to the route never saw it.

Three repairs are checked here against the shipped script:

    1. **The gate reads the later chapters.**  The settlement, coup, armistice, conference,
       northern, oil and great-game outcomes of 1919-45 are folded into the named paths, so
       `iran_path_majlis`, `_court`, `_army`, `_tribal`, `_armed_neutrality`, `_humiliated`,
       `_oil_concession`, `_oil_national`, `_entente` and `_germany` answer "how did the
       chapter end", not only "how did it begin".
    2. **`iran_path_intact` means intact.**  It used to also require armed neutrality, which
       classified a Persia that permitted transit, or fought alongside a patron, as neither
       intact nor humiliated. It is now the negation of `iran_path_humiliated`.
    3. **The unread flags gain visible readers.**  Each flag below is now tested by a
       decision's `visible` block or an event option's `trigger`, both of which change what
       the player can actually see and click:
       - `iran_british_demand_refused`, `iran_british_demand_deflected`,
         `iran_soviet_demand_refused` open the German mission before 1935;
       - `iran_british_demand_paid`, `iran_soviet_demand_paid` close it;
       - `iran_path_armed_neutrality` removes the Anglo-Persian ratification;
       - `iran_path_intact` removes the refusal of it;
       - `iran_armistice_claims` / `iran_armistice_accepted` shape the peace-conference
         options in `iran_campaign.29`;
       - `iran_agreement_transit_axis` closes the defiant answer in `iran_campaign.76`.

The German window is *evaluated* under declared flag and date states, not grepped for
flag names: a flag mentioned inside a condition that cannot fail (an `OR` repeating an
outer `date` conjunct) is present in the text and still changes nothing, which is exactly
what an earlier revision of this repair shipped.

Every check also runs against the pinned pre-repair revision and must reject it, and the
reader checks are re-run against in-memory mutants, because a check that passes the old
source or a broken mutant proves nothing.

Run from the repository root:

    python .tools/tests/test_iran_flag_readers.py            # exit 0 = pass
    python .tools/tests/test_iran_flag_readers.py --detail   # print every check

This is a source check. It proves what the script says under the country states it is
given; it does not prove what the engine does when a player reaches the decision. No game
is launched.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRIGGERS_PATH = 'common/scripted_triggers/iran_continuity.txt'
DECISIONS_PATH = 'common/decisions/iran_great_powers.txt'
EVENTS_PATH = 'events/iran_campaign.txt'
NEGOTIATIONS_PATH = 'events/iran_negotiations.txt'

# The pre-repair revision this card started from (I6 integrated). Pinned by full object
# name: a mutable HEAD stops being a mutant as soon as the repair is committed.
BASELINE_REV = 'ad0169dd1c6f67b4b8904f9f1d90f73f3f47754a'

# trigger -> the chapter-outcome flags this repair folded into it
PATH_FLAGS = {
    'iran_path_majlis': ('iran_shah_with_parliament', 'iran_assembly_endorsed',
                         'iran_coup_resisted', 'iran_conference_petition'),
    'iran_path_court': ('iran_shah_with_court', 'iran_assembly_managed'),
    'iran_path_army': ('iran_coup_settled', 'iran_tribes_disarmed'),
    'iran_path_tribal': ('iran_congress_declared', 'iran_tribes_negotiated'),
    'iran_path_armed_neutrality': ('iran_neutrality_proclaimed',),
    'iran_path_humiliated': ('iran_armistice_accepted',),
    'iran_path_oil_concession': ('iran_oil_settlement',),
    'iran_path_oil_national': ('iran_oil_dispute',),
    'iran_path_entente': ('iran_withdrawal_guaranteed', 'iran_gulf_arbitration_accepted'),
    'iran_path_germany': ('iran_german_mission_accepted', 'iran_agreement_transit_axis'),
}

# The two route triggers that stopped requiring a flag and started delegating
INTACT_TRIGGER = 'iran_path_intact'

# decision id -> flags its `visible` block must test
DECISION_VISIBLE_FLAGS = {
    'iran_invite_german_mission': ('iran_british_demand_paid', 'iran_soviet_demand_paid',
                                   'iran_british_demand_refused',
                                   'iran_british_demand_deflected',
                                   'iran_soviet_demand_refused'),
    'iran_crisis_anglo_persian_ratify': ('iran_path_armed_neutrality',),
    'iran_crisis_anglo_persian_reject': ('iran_path_intact',),
}

# event id -> flags its option triggers must test
EVENT_OPTION_FLAGS = {
    'iran_campaign.29': ('iran_armistice_claims', 'iran_armistice_accepted'),
    'iran_campaign.76': ('iran_agreement_transit_axis',),
}

# The German avenue, evaluated rather than grepped: (label, flags, date, expected).
# The pre-1935 rows are the ones the round-1 review found dead. While the outer
# `date > 1934.12.31` conjunct stood, the OR repeated it, so the three refusal flags
# decided nothing and every pre-1935 row read False. Presence checks cannot see that.
GERMAN_MISSION = 'iran_invite_german_mission'
GERMAN_MISSION_STATES = (
    ('1919, no patron answered', {'iran_campaign_active'}, (1919, 6, 1), False),
    ('1919, British bill refused',
     {'iran_campaign_active', 'iran_british_demand_refused'}, (1919, 6, 1), True),
    ('1932, British bill deflected',
     {'iran_campaign_active', 'iran_british_demand_deflected'}, (1932, 6, 1), True),
    ('1932, Soviet bill refused',
     {'iran_campaign_active', 'iran_soviet_demand_refused'}, (1932, 6, 1), True),
    ('1936, no patron answered', {'iran_campaign_active'}, (1936, 6, 1), True),
    ('1936, British bill paid',
     {'iran_campaign_active', 'iran_british_demand_paid'}, (1936, 6, 1), False),
    ('1936, Soviet bill paid',
     {'iran_campaign_active', 'iran_soviet_demand_paid'}, (1936, 6, 1), False),
    ('1936, mission already signed',
     {'iran_campaign_active', 'iran_british_demand_refused',
      'iran_agreement_german_mission'}, (1936, 6, 1), False),
    ('1942, refusal on record',
     {'iran_campaign_active', 'iran_british_demand_refused'}, (1942, 6, 1), False),
)

ALL_READER_FLAGS = tuple(sorted({flag for group in PATH_FLAGS.values() for flag in group}))

# Decisions the repair must not disturb: id -> (cost, ai_will_do factor or None)
PRESERVED_DECISIONS = {
    'iran_invite_german_mission': (100, 3),
    'iran_german_barter_trade': (50, 2),
    'iran_expel_the_german_mission': (100, 2),
    'iran_crisis_anglo_persian_begin': (None, None),
    'iran_crisis_anglo_persian_ratify': (75, 1),
    'iran_crisis_anglo_persian_reject': (75, 3),
}

# Event options the repair must leave in place
PRESERVED_OPTIONS = {
    'iran_campaign.29': ('iran_campaign.29.a', 'iran_campaign.29.b'),
    'iran_campaign.76': ('iran_campaign.76.a', 'iran_campaign.76.b'),
    'iran_campaign.55': ('iran_campaign.55.a', 'iran_campaign.55.b'),
    'iran_campaign.40': ('iran_campaign.40.a', 'iran_campaign.40.b', 'iran_campaign.40.c'),
}

DECREE_FLAG = 'iran_decree_treaty'


class Unsupported(Exception):
    """A script shape this check does not model. Failing loudly beats guessing."""


# ---------------------------------------------------------------------------------------------
# Source access
# ---------------------------------------------------------------------------------------------

def read(relative):
    return (ROOT / relative).read_text(encoding='utf-8-sig', errors='ignore')


def baseline(relative):
    result = subprocess.run(['git', 'show', '%s:%s' % (BASELINE_REV, relative)],
                            cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8',
                            errors='replace')
    if result.returncode != 0:
        raise Unsupported('cannot read %s at %s: %s'
                          % (relative, BASELINE_REV, result.stderr.strip()))
    return result.stdout


def repo_text(relative):
    return (ROOT / relative).read_text(encoding='utf-8-sig', errors='ignore')


# ---------------------------------------------------------------------------------------------
# Minimal Clausewitz reader: enough to walk named blocks and option triggers
# ---------------------------------------------------------------------------------------------

def strip_comments(text):
    return '\n'.join(line.split('#', 1)[0] for line in text.splitlines())


def match_brace(text, start):
    """Text[start] is '{'. Return the index just past its matching '}'."""
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return index + 1
    raise Unsupported('unbalanced braces after offset %d' % start)


def named_block(text, name):
    """Body of the first `name = { ... }` in text, or None."""
    match = re.search(r'(?<![\w])%s\s*=\s*\{' % re.escape(name), text)
    if not match:
        return None
    open_index = text.index('{', match.start())
    return text[open_index + 1:match_brace(text, open_index) - 1]


def blocks_of(text, key):
    """Every body of `key = { ... }` in text, in file order."""
    bodies = []
    for match in re.finditer(r'(?<![\w])%s\s*=\s*\{' % re.escape(key), text):
        open_index = text.index('{', match.start())
        bodies.append(text[open_index + 1:match_brace(text, open_index) - 1])
    return bodies


def flags_in(text):
    return set(re.findall(r'has_country_flag\s*=\s*([A-Za-z0-9_]+)', text))


def event_block(text, event_id):
    """Body of the country_event whose id is event_id, or None."""
    for body in blocks_of(text, 'country_event'):
        if re.search(r'(?<![\w])id\s*=\s*%s(?![\w.])' % re.escape(event_id), body):
            return body
    return None


def tokens(text):
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in ' \t\r\n':
            index += 1
        elif char in '{}<>=':
            out.append(char)
            index += 1
        else:
            start = index
            while index < len(text) and text[index] not in ' \t\r\n{}<>#=':
                index += 1
            out.append(text[start:index])
    return out


def parse(text):
    """Tokens -> nested list of (key, value) pairs; value is a str or a list."""
    position = 0

    def walk():
        nonlocal position
        entries = []
        while position < len(tokens_):
            token = tokens_[position]
            if token == '}':
                position += 1
                return entries
            if token == '{':
                position += 1
                entries.append(('{}', walk()))
                continue
            # `date > 1934.12.31` tokenises as three tokens; keep the comparison
            # together so the evaluator can answer it.
            if (token == 'date' and position + 2 < len(tokens_)
                    and tokens_[position + 1] in ('<', '>')
                    and re.fullmatch(r'\d{1,4}\.\d{1,2}\.\d{1,2}', tokens_[position + 2])):
                entries.append(('date', ('cmp', tokens_[position + 1],
                                         date_of(tokens_[position + 2]))))
                position += 3
                continue
            if position + 1 < len(tokens_) and tokens_[position + 1] == '=':
                key = token
                position += 2
                if position < len(tokens_) and tokens_[position] == '{':
                    position += 1
                    entries.append((key, walk()))
                else:
                    entries.append((key, tokens_[position] if position < len(tokens_) else ''))
                    position += 1
                continue
            entries.append((token, None))
            position += 1
        return entries

    tokens_ = tokens(text)
    return walk()


def date_of(text):
    """'1934.12.31' -> (1934, 12, 31), comparable as a tuple."""
    year, month, day = text.split('.')
    return (int(year), int(month), int(day))


class State:
    """A declared country state: flags set and, where a block tests it, the date."""

    def __init__(self, flags, date=None):
        self.flags = set(flags)
        self.date = date


def evaluate(nodes, state):
    """True/False for the trigger shapes the Iran script uses:
    a bare flag list (implicit AND), has_country_flag, NOT, OR, AND, date, yes/no.

    `state` is either a plain set of flags (no date: a date test then raises, because
    guessing one would make the answer meaningless) or a State."""
    flags = state.flags if isinstance(state, State) else state
    result = True
    for key, value in nodes:
        if key == 'has_country_flag':
            result = result and (value in flags)
        elif key == 'date':
            if not (isinstance(value, tuple) and len(value) == 3 and value[0] == 'cmp'):
                raise Unsupported('date without a comparison')
            if not isinstance(state, State) or state.date is None:
                raise Unsupported('date comparison evaluated without a date')
            operator, operand = value[1], value[2]
            if operator == '>':
                result = result and state.date > operand
            elif operator == '<':
                result = result and state.date < operand
            else:
                raise Unsupported('date operator %r' % operator)
        elif key == 'NOT':
            result = result and not evaluate(value, state)
        elif key == 'OR':
            result = result and any(evaluate([entry], state) for entry in value)
        elif key == 'AND':
            result = result and evaluate(value, state)
        elif key in ('yes', 'no'):
            continue
        elif isinstance(value, list) or value is None:
            raise Unsupported('unsupported trigger key %r' % key)
        else:
            raise Unsupported('unsupported trigger key %r' % key)
    return result


def trigger_flags(nodes):
    """Every country flag the parsed trigger tree tests, with its polarity."""
    found = []

    def walk(entries, negated):
        for key, value in entries:
            if key == 'has_country_flag':
                found.append((value, negated))
            elif key == 'NOT':
                walk(value, not negated)
            elif key in ('OR', 'AND'):
                walk(value, negated)
            elif isinstance(value, list):
                walk(value, negated)

    walk(nodes, False)
    return found


# ---------------------------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------------------------

class Report:
    def __init__(self, detail):
        self.detail = detail
        self.checks = 0
        self.failures = []

    def start(self, name):
        if self.detail:
            print('== %s' % name)

    def check(self, label, passed, note=''):
        self.checks += 1
        if not passed:
            self.failures.append('%s -- %s' % (label, note)
                                 if note else label)
        if self.detail or not passed:
            print('%s %s%s' % ('PASS' if passed else 'FAIL', label,
                               (' (%s)' % note) if note and not passed else ''))

    def note(self, text):
        if self.detail:
            print('   note: %s' % text)

    def summary(self):
        print('%d checks, %d failures' % (self.checks, len(self.failures)))
        for failure in self.failures:
            print('  FAILED: %s' % failure)
        return not self.failures


# ---------------------------------------------------------------------------------------------
# The checks, each usable against any revision so the baseline can be rejected
# ---------------------------------------------------------------------------------------------

def gate_failures(trigger_text):
    failures = []
    for trigger, expected in PATH_FLAGS.items():
        body = named_block(trigger_text, trigger)
        if body is None:
            failures.append('%s is missing' % trigger)
            continue
        present = flags_in(body)
        missing = [flag for flag in expected if flag not in present]
        if missing:
            failures.append('%s does not read %s' % (trigger, ', '.join(missing)))
    return failures


def intact_failures(trigger_text):
    failures = []
    body = named_block(trigger_text, INTACT_TRIGGER)
    if body is None:
        return ['%s is missing' % INTACT_TRIGGER]
    if 'iran_path_armed_neutrality' in body:
        failures.append('iran_path_intact still requires armed neutrality')
    for flag in ('iran_ottoman_frontier', 'iran_refugee_administration'):
        if flag in body:
            failures.append('iran_path_intact still restates %s instead of delegating'
                            % flag)
    if 'iran_path_humiliated' not in body:
        failures.append('iran_path_intact does not delegate to iran_path_humiliated')
    return failures


def decision_failures(decision_text, mapping):
    failures = []
    for decision, flags in mapping.items():
        body = named_block(decision_text, decision)
        if body is None:
            failures.append('%s is missing' % decision)
            continue
        visible = named_block(body, 'visible')
        if visible is None:
            failures.append('%s has no visible block' % decision)
            continue
        missing = [flag for flag in flags if flag not in visible]
        if missing:
            failures.append('%s.visible does not read %s' % (decision, ', '.join(missing)))
    return failures


def german_mission_failures(decision_text):
    """Evaluate the German decision's visible block under declared states.

    A textual check cannot tell a reader from a restatement: the round-1 defect had all
    three refusal flags present in the block and still changed nothing, because the OR
    repeated an outer date conjunct. This walks the block instead.
    """
    failures = []
    body = named_block(decision_text, GERMAN_MISSION)
    if body is None:
        return ['%s is missing' % GERMAN_MISSION]
    visible = named_block(body, 'visible')
    if visible is None:
        return ['%s has no visible block' % GERMAN_MISSION]
    try:
        tree = parse(visible)
    except Unsupported as error:
        return ['%s.visible cannot be evaluated: %s' % (GERMAN_MISSION, error)]
    for label, flags, date, expected in GERMAN_MISSION_STATES:
        try:
            actual = evaluate(tree, State(flags, date))
        except Unsupported as error:
            failures.append('%s.visible cannot be evaluated at %s: %s'
                            % (GERMAN_MISSION, label, error))
            continue
        if actual is not expected:
            failures.append('%s.visible is %s at %s (expected %s)'
                            % (GERMAN_MISSION, 'true' if actual else 'false', label,
                               'true' if expected else 'false'))
    return failures


def event_failures(event_text, mapping):
    failures = []
    for event_id, flags in mapping.items():
        body = event_block(event_text, event_id)
        if body is None:
            failures.append('%s is missing' % event_id)
            continue
        trigger_text = '\n'.join(named_block(option, 'trigger') or ''
                                 for option in blocks_of(body, 'option'))
        seen = flags_in(trigger_text)
        missing = [flag for flag in flags if flag not in seen]
        if missing:
            failures.append('%s option triggers do not read %s'
                            % (event_id, ', '.join(missing)))
    return failures


def preservation_failures(decision_text, event_text):
    failures = []
    for decision, (cost, factor) in PRESERVED_DECISIONS.items():
        body = named_block(decision_text, decision)
        if body is None:
            failures.append('%s was removed' % decision)
            continue
        if cost is not None and not re.search(r'cost\s*=\s*%d\b' % cost, body):
            failures.append('%s lost cost %d' % (decision, cost))
        if factor is not None and not re.search(r'factor\s*=\s*%d\b' % factor, body):
            failures.append('%s lost ai factor %d' % (decision, factor))
    for event_id, options in PRESERVED_OPTIONS.items():
        body = event_block(event_text, event_id)
        if body is None:
            failures.append('%s was removed' % event_id)
            continue
        for option in options:
            if not re.search(r'name\s*=\s*%s\b' % re.escape(option), body):
                failures.append('%s lost option %s' % (event_id, option))
    return failures


def option_reachability_failures(event_text, event_id, states):
    """No country state may leave an event with zero available options."""
    failures = []
    body = event_block(event_text, event_id)
    if body is None:
        return ['%s is missing' % event_id]
    options = []
    for option in blocks_of(body, 'option'):
        name = re.search(r'name\s*=\s*([A-Za-z0-9_.]+)', option)
        trigger = named_block(option, 'trigger')
        options.append((name.group(1) if name else '?',
                        parse(trigger) if trigger else None))
    for label, state in states:
        available = [name for name, tree in options
                     if tree is None or evaluate(tree, state)]
        if not available:
            failures.append('%s offers no option in state %s' % (event_id, label))
    return failures


# ---------------------------------------------------------------------------------------------
# Mutants: the repair must reject a broken version of itself
# ---------------------------------------------------------------------------------------------

def mutants(trigger_text, decision_text, event_text):
    """(label, mutated text, checks the mutation must fail) triples."""
    out = []

    # 1. One chapter-outcome flag dropped from a path trigger
    broken = trigger_text.replace('\t\thas_country_flag = iran_oil_dispute\n', '')
    out.append(('gate loses iran_oil_dispute', broken, 'gate'))

    # 2. The intact trigger put back the way the baseline had it
    restored = trigger_text.replace(
        'iran_path_intact = {\n\tNOT = { iran_path_humiliated = yes }\n}',
        'iran_path_intact = {\n\tNOT = { has_country_flag = iran_ottoman_frontier }\n'
        '\tNOT = { has_country_flag = iran_refugee_administration }\n'
        '\tiran_path_armed_neutrality = yes\n}')
    out.append(('intact restored to the baseline body', restored, 'intact'))

    # 3. A reader deleted from the decision layer
    broken_decisions = decision_text.replace(
        '\t\t\tNOT = { has_country_flag = iran_soviet_demand_paid }\n', '')
    out.append(('german mission ignores the Soviet bill', broken_decisions, 'decisions'))

    # 4. A reader deleted from the event layer
    broken_events = event_text.replace(
        '\t\ttrigger = { NOT = { has_country_flag = iran_agreement_transit_axis } }\n', '')
    out.append(('expulsion event ignores the German transit', broken_events, 'events'))

    # 5. The three refusal disjuncts pulled out of the German window, leaving the
    #    date-only OR that made them no-ops in round 1.
    broken_window = decision_text.replace(
        '\t\t\t\thas_country_flag = iran_british_demand_refused\n'
        '\t\t\t\thas_country_flag = iran_british_demand_deflected\n'
        '\t\t\t\thas_country_flag = iran_soviet_demand_refused\n', '')
    out.append(('german window ignores the patron refusals', broken_window, 'states'))
    return out


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------

def main(argv):
    detail = '--detail' in argv
    report = Report(detail)

    trigger_text = strip_comments(read(TRIGGERS_PATH))
    decision_text = strip_comments(read(DECISIONS_PATH))
    event_text = strip_comments(read(EVENTS_PATH))

    report.start('A. the gate reads the later chapters')
    failures = gate_failures(trigger_text)
    for failure in failures:
        report.check(failure, False)
    report.check('%d route triggers still read %d chapter-outcome flags'
                 % (len(PATH_FLAGS), len(ALL_READER_FLAGS)), not failures)

    report.start('B. iran_path_intact means intact')
    failures = intact_failures(trigger_text)
    for failure in failures:
        report.check(failure, False)
    report.check('the intact trigger delegates to iran_path_humiliated', not failures)

    report.start('C. the decisions react to the route')
    failures = decision_failures(decision_text, DECISION_VISIBLE_FLAGS)
    for failure in failures:
        report.check(failure, False)
    report.check('%d decisions carry %d route flags in visible'
                 % (len(DECISION_VISIBLE_FLAGS),
                    sum(len(v) for v in DECISION_VISIBLE_FLAGS.values())), not failures)

    # C2: presence is not effect. The German window is evaluated under declared states,
    # because round 1 shipped every refusal flag in the block and none of them mattered.
    window_failures = german_mission_failures(decision_text)
    for failure in window_failures:
        report.check(failure, False)
    report.check('the German window opens before 1935 only for a refused patron '
                 '(%d states)' % len(GERMAN_MISSION_STATES), not window_failures)

    report.start('D. the events react to the route')
    failures = event_failures(event_text, EVENT_OPTION_FLAGS)
    for failure in failures:
        report.check(failure, False)
    report.check('%d events carry route flags in option triggers'
                 % len(EVENT_OPTION_FLAGS), not failures)

    report.start('E. every reader flag has a writer')
    writers = {}
    for path in ('events/iran_campaign.txt', 'common/decisions/iran_great_powers.txt',
                 'common/scripted_effects/iran_campaign.txt'):
        for flag in re.findall(r'set_country_flag\s*=\s*([A-Za-z0-9_]+)',
                               strip_comments(repo_text(path))):
            writers.setdefault(flag, set()).add(path)
    missing = [flag for flag in ALL_READER_FLAGS if flag not in writers]
    report.check('all %d reader flags are set by Iran script' % len(ALL_READER_FLAGS),
                 not missing, ', '.join(missing))

    report.start('F. no permanent treaty gate was restored')
    owned = trigger_text + decision_text + event_text
    report.check('the decree veto is not mentioned in the owned files',
                 DECREE_FLAG not in owned)
    negotiations = strip_comments(repo_text(NEGOTIATIONS_PATH))
    timed = re.findall(r'set_country_flag\s*=\s*\{\s*flag\s*=\s*%s\b[^}]*days\s*='
                       % DECREE_FLAG, negotiations)
    permanent = re.findall(r'set_country_flag\s*=\s*%s\b' % DECREE_FLAG, negotiations)
    report.check('the veto is set as a timed flag %d times' % len(timed), len(timed) == 4,
                 '%d timed setters' % len(timed))
    report.check('no permanent setter of the veto remains', not permanent,
                 '%d bare setters' % len(permanent))

    report.start('G. nothing else was disturbed')
    failures = preservation_failures(decision_text, event_text)
    for failure in failures:
        report.check(failure, False)
    report.check('%d decisions and %d events kept their cost, AI factor and options'
                 % (len(PRESERVED_DECISIONS), len(PRESERVED_OPTIONS)), not failures)

    report.start('H. the peace-conference options stay reachable')
    states = [('none', set()),
              ('claims only', {'iran_armistice_claims'}),
              ('accepted only', {'iran_armistice_accepted'}),
              ('both', {'iran_armistice_claims', 'iran_armistice_accepted'}),
              ('claimed and refused to sign', {'iran_armistice_claims'})]
    failures = option_reachability_failures(event_text, 'iran_campaign.29', states)
    for failure in failures:
        report.check(failure, False)
    report.check('the conference always offers an option', not failures)

    report.start('I. the pre-repair source is rejected')
    old_triggers = strip_comments(baseline(TRIGGERS_PATH))
    old_decisions = strip_comments(baseline(DECISIONS_PATH))
    old_events = strip_comments(baseline(EVENTS_PATH))
    old_gate = gate_failures(old_triggers)
    old_intact = intact_failures(old_triggers)
    old_decisions_failures = decision_failures(old_decisions, DECISION_VISIBLE_FLAGS)
    old_window_failures = german_mission_failures(old_decisions)
    old_event_failures = event_failures(old_events, EVENT_OPTION_FLAGS)
    report.check('the baseline gate fails', bool(old_gate), '%d missing reads' % len(old_gate))
    report.check('the baseline intact trigger fails', bool(old_intact),
                 '; '.join(old_intact))
    report.check('the baseline decisions fail', bool(old_decisions_failures),
                 '%d missing readers' % len(old_decisions_failures))
    report.check('the baseline German window is rejected', bool(old_window_failures),
                 '%d wrong states' % len(old_window_failures))
    report.check('the baseline events fail', bool(old_event_failures),
                 '%d missing readers' % len(old_event_failures))
    report.note('baseline %s: %d gate, %d intact, %d decision, %d window and %d event '
                'defects'
                % (BASELINE_REV[:9], len(old_gate), len(old_intact),
                   len(old_decisions_failures), len(old_window_failures),
                   len(old_event_failures)))

    report.start('J. mutant control')
    for label, mutated, layer in mutants(trigger_text, decision_text, event_text):
        if layer == 'gate':
            failed = gate_failures(mutated)
        elif layer == 'intact':
            failed = intact_failures(mutated)
        elif layer == 'decisions':
            failed = decision_failures(mutated, DECISION_VISIBLE_FLAGS)
        elif layer == 'states':
            failed = german_mission_failures(mutated)
        else:
            failed = event_failures(mutated, EVENT_OPTION_FLAGS)
        report.check('mutant rejected: %s' % label, bool(failed), 'the mutant passed')

    report.note('the decree veto timer is read by the yearly budget mission; engine expiry '
                'of the timed flag is not proven here')
    report.note('no game was launched: option visibility, decision visibility and the gate '
                'are source facts under the declared flag states, not engine observations')
    return 0 if report.summary() else 1


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Unsupported as error:
        print('UNSUPPORTED: %s' % error)
        sys.exit(3)
