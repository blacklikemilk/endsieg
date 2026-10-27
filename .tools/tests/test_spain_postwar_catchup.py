"""Regression test: the post-war bookmark catch-up is reachable and completes the loaded tree.

`spain_restore_past_focuses` is the schedule a late start runs to inherit the focuses history
had already completed. Two defects made it dead on every post-war bookmark:

  * only the Restoration, Rivera and Republic openers set `spain_focus_restore_pending`, the one
    flag `spain_campaign_tick` tests before it calls `spain_campaign_bootstrap`; both post-war
    openers set `spain_bop_pending` instead, so no post-war chapter ever reached the bootstrap,
    the catch-up or the idea refresh;
  * the `SPR4_*` completion list sat under `spain_chapter_postwar`, while `SPR4_*` ids live only
    in `spain_republic_postwar_focus`; the Nationalist chapter loads `spanish_focus`, and the
    Republican chapter had no list at all.

The repair does three things in `common/scripted_effects/spain_campaign_effects.txt`: both
post-war openers now clear the pending balance and arm the restore flag, the Nationalist list
completes the `SPA_*` post-war branches, and the `SPR4_*` list moves under the Republican
chapter with its two 1941 rows added.

This test reads the shipped source and executes it. Nothing here restates the schedule:

    1. the chapter a bookmark reaches is read by evaluating `spain_campaign_initialize` (and,
       for the live handover, `spain_enter_postwar_chapter`) from the file;
    2. the flag state an opener leaves is built from its own top-level writes, in order,
       starting from a country that still carries a stale `spain_bop_pending`;
    3. every completion is produced by evaluating the shipped `if`/`else_if`/`limit` chain
       against a date, the chapter flag, the completed focuses and the idea set;
    4. membership is computed from the focus file the opener's own `load_focus_tree` names, so
       an id that does not exist in the loaded tree fails even if it looks plausible;
    5. the Nationalist branch a run reaches, the pins that branch can carry, and the order it
       must emit them in are all derived from `common/national_focus/spain.txt` plus the
       `has_completed_focus` id each branch tests, so no route table and no expected id list is
       written down here;
    6. an effect or trigger shape this simulator does not model raises, it never passes quietly.
       The effects it steps over are listed by name and asserted inert for the four flags under
       test, so "ignored" cannot hide a writer.

Eight mutants are applied to the same text and must be rejected by name: an `SPR4_*` id left in
the Nationalist block, the alignment gate removed so both join focuses complete, a Nationalist
ancestor dropped, a pin added to a route whose fork cannot carry it, a mutex sibling added to a
route, the two 1941 Republican rows dropped, a Republican ancestor dropped, and the pending
balance no longer cleared by an opener.

Run from the repository root:

    python .tools/tests/test_spain_postwar_catchup.py            # exit 0 = pass
    python .tools/tests/test_spain_postwar_catchup.py --detail    # print every area and mutant

This is a source simulation. It proves what the script says, not what the engine does: no
bookmark was loaded, no focus was clicked, no daily tick ran, and the game was never launched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_spain_cortes_recount as base  # noqa: E402  (the shared tokeniser and parser)

EFFECTS_PATH = 'common/scripted_effects/spain_campaign_effects.txt'
EFFECTS_DIR = 'common/scripted_effects'
FOCUS_DIR = 'common/national_focus'

SCHEDULE = 'spain_restore_past_focuses'
BOOTSTRAP = 'spain_campaign_bootstrap'
TICK = 'spain_campaign_tick'
INITIALIZE = 'spain_campaign_initialize'
ENTER_POSTWAR = 'spain_enter_postwar_chapter'

POSTWAR_CHAPTERS = (
    ('spain_chapter_postwar', 'spain_open_postwar_chapter'),
    ('spain_chapter_republican_postwar', 'spain_open_republican_postwar_chapter'),
)
CHAPTER_FLAGS = frozenset(flag for flag, _opener in POSTWAR_CHAPTERS) | frozenset((
    'spain_chapter_restoration', 'spain_chapter_rivera', 'spain_chapter_republic',
    'spain_chapter_civil_war',
))
POSTWAR_FLAGS = frozenset(flag for flag, _opener in POSTWAR_CHAPTERS)

RESTORE_FLAG = 'spain_focus_restore_pending'
BOP_FLAG = 'spain_bop_pending'
GUARDED_FLAGS = frozenset((RESTORE_FLAG, BOP_FLAG)) | CHAPTER_FLAGS

AXIS = 'spain_axis_alignment'
ALLIED = 'spain_allied_alignment'

# The seven post-war pins the design names. Which of them a route can carry is derived from the
# tree below, never written here.
NATIONALIST_PINS = ('SPA_the_national_syndicalist_state',
                    'SPA_the_national_and_popular_army_of_spain',
                    'SPA_national_recovery', 'SPA_join_the_axis', 'SPA_join_the_allies',
                    'SPA_the_iberian_pact', 'SPA_settle_the_succession_question')
# The post-war date ladder the design fixes: the catch-up runs at no other date.
POSTWAR_LADDER = ('1940.6.1', '1941.6.1', '1943.1.1', '1945.6.1')
REPUBLICAN_1941 = ('SPR4_the_exiled_monarchy', 'SPR4_the_falange_remnant', 'SPR4_amnesty_debate',
                   'SPR4_political_police', 'SPR4_the_church_settlement')

# Every id the Republican list completed before the repair.
REPUBLICAN_LEDGER = (
    'SPR4_the_republic_endures', 'SPR4_constitution_of_1939', 'SPR4_rebuild_the_industry',
    'SPR4_army_of_the_republic', 'SPR4_the_air_force', 'SPR4_volunteer_question',
    'SPR4_wolfram_trade', 'SPR4_the_hydroelectric_grid', 'SPR4_railway_restoration',
    'SPR4_diplomacy_with_the_allies', 'SPR4_western_orientation', 'SPR4_the_iberian_pact',
    'SPR4_armed_neutrality', 'SPR4_the_european_war', 'SPR4_the_1945_settlement',
)

BOOKMARKS = ('1939.1.1', '1940.1.1', '1941.1.1', '1942.1.1', '1943.1.1', '1944.1.1',
             '1944.11.1', '1945.1.1', '1945.6.2')

PREWAR_LINES = 92            # restoration, Rivera and republic lists, untouched by this card

# Native effects an opener may call. None of them writes a country flag.
NATIVE_IGNORED = frozenset((
    'mark_focus_tree_layout_dirty', 'remove_power_balance', 'set_power_balance', 'add_ideas',
    'remove_ideas', 'set_variable', 'add_equipment_to_stockpile', 'add_stability',
    'add_war_support', 'news_event', 'country_event',
))
# Scripted helpers an opener may call that this simulator does not expand. Every one is
# asserted below to write none of the chapter, restore or balance flags.
HELPER_IGNORED = frozenset((
    'spain_cortes_initialize', 'spain_refresh_campaign_ideas', 'spain_carry_over_choices',
    'spain_ensure_campaign_state', 'spain_ensure_chapter_tree',
))
IGNORED = NATIVE_IGNORED | HELPER_IGNORED

LOOP_KEYS = ('every_', 'random_', 'for_loop', 'while_loop', 'random_list', 'for_each')


class Unsupported(Exception):
    """A shape this simulator does not model. Failing loudly beats reporting a pass."""


# ---------------------------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------------------------

def read_text(relative):
    return (ROOT / relative).read_text(encoding='utf-8-sig')


def strip_comments(text):
    """Blank out `#` comments without moving any offset."""
    result = []
    in_comment = False
    for char in text:
        if in_comment:
            if char == '\n':
                in_comment = False
                result.append(char)
            else:
                result.append(' ')
        elif char == '#':
            in_comment = True
            result.append(' ')
        else:
            result.append(char)
    return ''.join(result)


def brace_block(text, start):
    """The balanced {...} region that begins at or after `start`."""
    opening = text.index('{', start)
    depth, cursor = 0, opening
    while cursor < len(text):
        if text[cursor] == '{':
            depth += 1
        elif text[cursor] == '}':
            depth -= 1
            if depth == 0:
                return text[opening:cursor + 1]
        cursor += 1
    raise Unsupported('unbalanced block at offset %d' % start)


def definition_bodies(name):
    """Every source body that defines `name`, across the scripted-effect files."""
    bodies = []
    pattern = re.compile(r'(?m)^\t*%s\s*=\s*\{' % re.escape(name))
    for path in sorted((ROOT / EFFECTS_DIR).glob('*.txt')):
        text = strip_comments(path.read_text(encoding='utf-8-sig'))
        for match in pattern.finditer(text):
            bodies.append((path.relative_to(ROOT).as_posix(), brace_block(text, match.start())))
    return bodies


def focus_tree_index():
    """focus tree id -> source path, scanned from the shipped focus files."""
    index = {}
    for path in sorted((ROOT / FOCUS_DIR).glob('*.txt')):
        body = strip_comments(path.read_text(encoding='utf-8-sig'))
        for match in re.finditer(r'focus_tree\s*=\s*\{', body):
            header = brace_block(body, match.start())[:2000]
            found = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', header)
            if found:
                index.setdefault(found.group(1), path.relative_to(ROOT).as_posix())
    return index


def focus_ids(relative):
    """Focus ids declared in one tree file."""
    text = strip_comments(read_text(relative))
    ids = set()
    for match in re.finditer(r'^\t*focus\s*=\s*\{', text, re.M):
        body = brace_block(text, match.start())
        found = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', body)
        if found:
            ids.add(found.group(1))
    return ids


# ---------------------------------------------------------------------------------------------
# Evaluator: flags, trigger limits, if chains, complete_national_focus
# ---------------------------------------------------------------------------------------------

def date_tuple(text):
    parts = text.split('.')
    if len(parts) != 3:
        raise Unsupported('date %r is not year.month.day' % text)
    return tuple(int(part) for part in parts)


class State:
    def __init__(self, date, flags=(), ideas=(), government=None, tree=None, completed=(),
                 power_balances=(), variables=()):
        self.date = date_tuple(date)
        self.flags = set(flags)
        self.ideas = set(ideas)
        self.government = government
        self.tree = tree
        self.completed = list(completed)
        self.power_balances = set(power_balances)
        self.variables = set(variables)
        self.ignored = []


def holds(trigger_entries, state, where):
    for key, value, line in trigger_entries:
        kind = value[0]
        if key == 'has_country_flag' and kind == 'scalar':
            if value[1] not in state.flags:
                return False
        elif key == 'has_idea' and kind == 'scalar':
            if value[1] not in state.ideas:
                return False
        elif key == 'has_completed_focus' and kind == 'scalar':
            if value[1] not in state.completed:
                return False
        elif key == 'has_variable' and kind == 'scalar':
            if value[1] not in state.variables:
                return False
        elif key == 'has_government' and kind == 'scalar':
            if state.government != value[1]:
                return False
        elif key == 'has_power_balance' and kind == 'block':
            ident = next((sub_value[1] for sub_key, sub_value, _sub_line in value[1]
                          if sub_key == 'id' and sub_value[0] == 'scalar'), None)
            if ident is None:
                raise Unsupported('has_power_balance without id at %s line %d'
                                  % (where, line))
            if ident not in state.power_balances:
                return False
        elif key == 'date' and kind == 'compare':
            operator, raw = value[1]
            left, right = state.date, date_tuple(raw)
            if operator == '>':
                if not left > right:
                    return False
            elif operator == '<':
                if not left < right:
                    return False
            else:
                raise Unsupported('date comparison %r at %s line %d'
                                  % (operator, where, line))
        elif key == 'NOT' and kind == 'block':
            if holds(value[1], state, where):
                return False
        elif key == 'AND' and kind == 'block':
            if not holds(value[1], state, where):
                return False
        elif key == 'OR' and kind == 'block':
            if not any(holds([entry], state, where) for entry in value[1]):
                return False
        else:
            raise Unsupported('trigger %s at %s line %d' % (key, where, line))
    return True


def limit_of(body, where):
    if not body:
        raise Unsupported('empty block at %s' % where)
    key, value, line = body[0]
    if key != 'limit' or value[0] != 'block':
        raise Unsupported('%s block does not open with limit (line %d)' % (where, line))
    return value[1], body[1:]


def run_body(body, state, where, blocks, on_call, depth=0):
    """Evaluate a statement body: if/else_if/else chains interleaved with plain effects."""
    if depth > 6:
        raise Unsupported('helper expansion deeper than six levels at %s' % where)
    index = 0
    while index < len(body):
        key, value, line = body[index]
        if key in ('else_if', 'else'):
            raise Unsupported('%s without a preceding if at %s line %d' % (key, where, line))
        if key != 'if':
            effect_entry(key, value, line, state, where, blocks, on_call, depth)
            index += 1
            continue
        chain = [body[index]]
        index += 1
        while index < len(body) and body[index][0] in ('else_if', 'else'):
            chain.append(body[index])
            index += 1
            if chain[-1][0] == 'else':
                break
        for branch, branch_value, branch_line in chain:
            if branch_value[0] != 'block':
                raise Unsupported('%s without a block at %s line %d'
                                  % (branch, where, branch_line))
            branch_body = branch_value[1]
            if branch == 'else':
                run_body(branch_body, state, where, blocks, on_call, depth)
                break
            trigger, action = limit_of(branch_body, where)
            if holds(trigger, state, where):
                run_body(action, state, where, blocks, on_call, depth)
                break


def effect_entry(key, value, line, state, where, blocks, on_call, depth):
    kind = value[0]
    if key == 'complete_national_focus':
        if kind == 'scalar':
            state.completed.append(value[1])
            return
        if kind == 'block':
            body = value[1]
            if len(body) != 1 or body[0][0] != 'focus' or body[0][1][0] != 'scalar':
                raise Unsupported('complete_national_focus block shape at %s line %d'
                                  % (where, line))
            state.completed.append(body[0][1][1])
            return
        raise Unsupported('complete_national_focus value at %s line %d' % (where, line))
    if key == 'set_country_flag' and kind == 'scalar':
        state.flags.add(value[1])
        return
    if key == 'clr_country_flag' and kind == 'scalar':
        state.flags.discard(value[1])
        return
    if key == 'load_focus_tree' and kind == 'block':
        for sub_key, sub_value, _sub_line in value[1]:
            if sub_key == 'tree' and sub_value[0] == 'scalar':
                state.tree = sub_value[1]
                return
        raise Unsupported('load_focus_tree without tree at %s line %d' % (where, line))
    if key in NATIVE_IGNORED:
        state.ignored.append(key)
        return
    if kind == 'scalar' and key in HELPER_IGNORED:
        state.ignored.append(key)
        return
    if kind == 'scalar' and key in blocks:
        if on_call is not None:
            on_call(key, state)
            return
        run_body(blocks[key][0], state, key, blocks, None, depth + 1)
        return
    raise Unsupported('effect %s at %s line %d' % (key, where, line))


# ---------------------------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------------------------

class World:
    def __init__(self, effects_text=None):
        self.effects_text = read_text(EFFECTS_PATH) if effects_text is None else effects_text
        self.blocks = base.parse_file(self.effects_text)
        self.trees = focus_tree_index()
        self.focus = {}

    def tree_ids(self, tree_id):
        if tree_id not in self.trees:
            raise Unsupported('focus tree %r is not declared in %s' % (tree_id, FOCUS_DIR))
        if tree_id not in self.focus:
            self.focus[tree_id] = focus_ids(self.trees[tree_id])
        return self.focus[tree_id]

    def block(self, name):
        if name not in self.blocks:
            raise Unsupported('scripted effect %r is missing from %s' % (name, EFFECTS_PATH))
        return self.blocks[name][0]


def top_level_writes(entries):
    """The literal writes an opener performs at its top level, in source order."""
    writes = []
    for key, value, _line in entries:
        if key in ('set_country_flag', 'clr_country_flag') and value[0] == 'scalar':
            writes.append((key, value[1]))
        elif key == 'load_focus_tree' and value[0] == 'block':
            for sub_key, sub_value, _sub_line in value[1]:
                if sub_key == 'tree' and sub_value[0] == 'scalar':
                    writes.append(('tree', sub_value[1]))
    return writes


def route_for(world, date, government=None, via='initialize'):
    """Evaluate the shipped routing chain and return the opener it reaches."""
    reached = []

    def call(name, state):
        reached.append(name)

    state = State(date, government=government)
    if via == 'initialize':
        run_body(world.block(INITIALIZE), state, INITIALIZE, world.blocks, call)
    elif via == 'handover':
        run_body(world.block(ENTER_POSTWAR), state, ENTER_POSTWAR, world.blocks, call)
    else:
        raise Unsupported('unknown route %r' % via)
    if not reached:
        raise Unsupported('no chapter was reached for %s via %s' % (date, via))
    return reached[0], state


def run_bookmark(world, date, stale_bop=True, via='initialize', government=None):
    """A bookmark start: routing, opener writes, first-tick schedule, all from the source."""
    opener, state = route_for(world, date, government=government, via=via)
    if stale_bop:
        state.flags.add(BOP_FLAG)
    for key, value in top_level_writes(world.block(opener)):
        if key == 'set_country_flag':
            state.flags.add(value)
        elif key == 'clr_country_flag':
            state.flags.discard(value)
        elif key == 'tree':
            state.tree = value
    reachable = RESTORE_FLAG in state.flags
    if reachable:
        state.flags.discard(RESTORE_FLAG)
        state.completed = []
        run_body(world.block(BOOTSTRAP), state, BOOTSTRAP, world.blocks, None)
    return {'opener': opener, 'flags': set(state.flags), 'tree': state.tree,
            'reachable': reachable, 'completed': list(state.completed)}


def run_schedule(world, chapter_flag, date, ideas=(), completed=()):
    state = State(date, flags={chapter_flag}, ideas=ideas, completed=completed)
    run_body(world.block(SCHEDULE), state, SCHEDULE, world.blocks, None)
    return list(state.completed)


# ---------------------------------------------------------------------------------------------
# Areas
# ---------------------------------------------------------------------------------------------

def area_openers(world):
    checks = 0
    failures = []

    for chapter, opener in POSTWAR_CHAPTERS:
        entries = world.block(opener)
        keys = top_level_writes(entries)

        checks += 1
        if ('set_country_flag', RESTORE_FLAG) not in keys:
            failures.append('%s does not arm %s' % (opener, RESTORE_FLAG))
        checks += 1
        if ('clr_country_flag', BOP_FLAG) not in keys:
            failures.append('%s does not clear %s' % (opener, BOP_FLAG))
        checks += 1
        if ('set_country_flag', BOP_FLAG) in keys:
            failures.append('%s still sets %s, so the bootstrap rebuilds the deleted balance'
                            % (opener, BOP_FLAG))
        checks += 1
        if ('set_country_flag', chapter) not in keys:
            failures.append('%s does not set %s' % (opener, chapter))
        checks += 1
        arm = keys.index(('set_country_flag', RESTORE_FLAG)) if (
            'set_country_flag', RESTORE_FLAG) in keys else -1
        clear = keys.index(('clr_country_flag', BOP_FLAG)) if (
            'clr_country_flag', BOP_FLAG) in keys else 10 ** 6
        if arm >= 0 and clear < 10 ** 6 and arm < clear:
            failures.append('%s arms the restore before it clears %s' % (opener, BOP_FLAG))

        # The observable contract: a country that still carries a stale pending balance ends
        # the opener with the restore armed and no pending balance left behind.
        state = State('1944.1.1', flags={BOP_FLAG})
        run_body(entries, state, opener, world.blocks, None)
        checks += 1
        if BOP_FLAG in state.flags:
            failures.append('%s leaves %s set: the bootstrap would recreate the balance'
                            % (opener, BOP_FLAG))
        checks += 1
        if RESTORE_FLAG not in state.flags:
            failures.append('%s does not leave %s armed' % (opener, RESTORE_FLAG))
        checks += 1
        if state.tree is None:
            failures.append('%s loads no focus tree' % opener)

    checks += 1
    if SCHEDULE not in [entry[0] for entry in world.block(BOOTSTRAP)]:
        failures.append('%s no longer calls %s' % (BOOTSTRAP, SCHEDULE))

    for name in (BOOTSTRAP, SCHEDULE):
        checks += 1
        calls = len(re.findall(r'(?m)^\t*%s = yes' % name, world.effects_text))
        if calls != 1:
            failures.append('%s has %d call sites, expected 1' % (name, calls))

    checks += 1
    guarded = False

    def walks_to_bootstrap(entries):
        """True where a limit tests the restore flag and the guarded body calls the bootstrap."""
        index = 0
        while index < len(entries):
            key, value, line = entries[index]
            if key != 'if' or value[0] != 'block':
                index += 1
                continue
            body = value[1]
            trigger, action = limit_of(body, TICK)
            flags_tested = [entry[1][1] for entry in trigger
                            if entry[0] == 'has_country_flag' and entry[1][0] == 'scalar']
            if RESTORE_FLAG in flags_tested and any(entry[0] == BOOTSTRAP for entry in action):
                return True
            if walks_to_bootstrap(action) or walks_to_bootstrap(trigger):
                return True
            index += 1
        return False

    guarded = walks_to_bootstrap(world.block(TICK))
    if not guarded:
        failures.append('%s no longer calls the bootstrap under %s' % (TICK, RESTORE_FLAG))
    checks += 1
    if 'clr_country_flag = %s' % RESTORE_FLAG not in world.effects_text:
        failures.append('nothing clears %s, so the catch-up would repeat every tick'
                        % RESTORE_FLAG)

    # The stepped-over helpers must not be able to write the flags this test reasons about.
    for name in sorted(HELPER_IGNORED):
        bodies = definition_bodies(name)
        checks += 1
        if not bodies:
            failures.append('ignored helper %s is defined nowhere, so its inertness is unproven'
                            % name)
            continue
        for path, text in bodies:
            for flag in GUARDED_FLAGS:
                checks += 1
                if re.search(r'(?:set|clr)_country_flag\s*=\s*(?:\{\s*flag\s*=\s*)?%s\b'
                             % re.escape(flag), text):
                    failures.append('ignored helper %s (%s) writes %s' % (name, path, flag))
    return checks, failures


def area_routing(world):
    checks = 0
    failures = []

    for date in BOOKMARKS:
        result = run_bookmark(world, date)
        checks += 1
        if date == '1939.1.1':
            if result['opener'] != 'spain_open_civil_war_chapter':
                failures.append('1939.1.1 routes to %s' % result['opener'])
            if result['completed']:
                failures.append('the 1939 civil-war start completes %s' % result['completed'])
            continue
        checks += 1
        if result['opener'] != 'spain_open_postwar_chapter':
            failures.append('%s routes to %s, not the post-war chapter'
                            % (date, result['opener']))
        checks += 1
        if not result['reachable']:
            failures.append('%s reaches no bootstrap: the catch-up is dead' % date)
        checks += 1
        if date in ('1940.1.1',) and result['completed']:
            failures.append('%s completes %s before the first gate' % (date, result['completed']))
        checks += 1
        if date not in ('1940.1.1',) and not result['completed']:
            failures.append('%s reached the bootstrap but completed nothing' % date)

    # The Republican chapter is reached by the live handover, not by the date chain.
    opener, _state = route_for(world, '1944.1.1', government='democratic', via='handover')
    checks += 1
    if opener != 'spain_open_republican_postwar_chapter':
        failures.append('a democratic handover routes to %s' % opener)
    republican = run_bookmark(world, '1944.1.1', via='handover', government='democratic')
    checks += 1
    if republican['tree'] != 'spain_republic_postwar_focus':
        failures.append('the Republican chapter loads %s' % republican['tree'])
    checks += 1
    if not republican['reachable']:
        failures.append('the Republican handover reaches no bootstrap')
    checks += 1
    if not republican['completed']:
        failures.append('the Republican handover completes nothing')
    checks += 1
    if any(not focus.startswith('SPR4_') for focus in republican['completed']):
        failures.append('the Republican handover completes %s' % republican['completed'])
    return checks, failures


def area_nationalist(world):
    """Each route completes the closure its own fork side implies, and nothing else."""
    checks = 0
    failures = []

    for route in route_plan(world):
        side = route['side']
        graph = route['graph']
        seed = tuple(sorted(route['seed']))
        try:
            groups = route_groups(route['body'], SCHEDULE)
            done, emitted = set(route['seed']), []
            for date, _trigger, ids in groups:
                try:
                    ordered = topological_order(ids, done, graph)
                except Unsupported as error:
                    failures.append('%s route is not closed over the tree at %s: %s'
                                    % (side, date, error))
                    ordered = list(ids)
                if list(ids) != ordered:
                    failures.append('%s route is not closed over the tree at %s: emits %s, '
                                    'the tree needs %s' % (side, date, list(ids), ordered))
                done |= set(ids)
                emitted.extend(ids)
                checks += 1
        except Unsupported as error:
            checks += 1
            failures.append('%s route is not closed over the tree: %s' % (side, error))
            continue

        # The gates are rungs of the design ladder, in order, and the ids they carry are exactly
        # the closure the tree forces for this side.
        previous = None
        for date, _trigger, _ids in groups:
            checks += 1
            if date not in POSTWAR_LADDER:
                failures.append('%s route gates on %s, which is not a post-war ladder date'
                                % (side, date))
            checks += 1
            if previous is not None and date_tuple(date) < date_tuple(previous):
                failures.append('%s route gates %s after %s' % (side, date, previous))
            previous = date

        checks += 1
        if set(emitted) != set(route['order']):
            failures.append('%s route is not closed over the tree: emits %s, the tree needs %s'
                            % (side, sorted(set(emitted)), sorted(set(route['order']))))

        checks += 1
        pairs = exclusive_pairs(list(route['seed']) + emitted, graph)
        if pairs:
            failures.append('%s route completes both sides of %s' % (side, pairs))

        # The pins this fork side can carry are scheduled and the ones behind a locked-out side
        # are not, so a route that cannot carry a pin neither forces it nor drops it silently.
        for pin in NATIONALIST_PINS:
            checks += 1
            if pin in route['pins'] and pin not in emitted:
                failures.append('%s route does not complete %s, which it can carry'
                                % (side, pin))
            checks += 1
            if pin not in route['pins'] and pin in emitted:
                failures.append('%s route completes %s, which the route cannot carry'
                                % (side, pin))

        # The shipped block agrees with the plan at every rung and on both sides of it.
        for date in POSTWAR_LADDER + ('1940.6.2', '1941.6.2', '1943.1.2', '1945.6.2'):
            for ideas in ((), (AXIS,), (ALLIED,)):
                state = State(date, flags={'spain_chapter_postwar'}, ideas=ideas,
                              completed=seed)
                expected = set()
                for _gate, trigger, ids in groups:
                    if holds(trigger, state, SCHEDULE):
                        expected.update(ids)
                got = [focus for focus in
                       run_schedule(world, 'spain_chapter_postwar', date, ideas=ideas,
                                    completed=seed) if focus not in route['seed']]
                checks += 1
                if set(got) != expected:
                    failures.append('%s route on %s with %s completes %s, expected %s'
                                    % (side, date, list(ideas) or 'no idea', got,
                                       sorted(expected)))
            got = [focus for focus in
                   run_schedule(world, 'spain_chapter_postwar', date, ideas=(AXIS, ALLIED),
                                completed=seed) if focus not in route['seed']]
            checks += 1
            if 'SPA_join_the_axis' in got and 'SPA_join_the_allies' in got:
                failures.append('%s route completes both join focuses on %s' % (side, date))
    return checks, failures


def area_republican(world):
    checks = 0
    failures = []

    deepest = run_schedule(world, 'spain_chapter_republican_postwar', '1945.6.2')
    checks += 1
    missing = [focus for focus in REPUBLICAN_LEDGER if focus not in deepest]
    if missing:
        failures.append('the Republican list dropped %s' % missing)

    at_1941 = run_schedule(world, 'spain_chapter_republican_postwar', '1941.1.2')
    for focus in REPUBLICAN_1941:
        checks += 1
        if focus not in at_1941:
            failures.append('%s is not completed at 1941.1.2 (got %s)' % (focus, at_1941))

    before_1941 = run_schedule(world, 'spain_chapter_republican_postwar', '1941.1.1')
    for focus in REPUBLICAN_1941:
        checks += 1
        if focus in before_1941:
            failures.append('%s completes on the 1941.1.1 boundary' % focus)

    checks += 1
    if len(deepest) != len(set(deepest)):
        failures.append('the Republican list completes an id twice: %s' % deepest)

    checks += 1
    if set(deepest) == set(run_schedule(world, 'spain_chapter_postwar', '1945.6.2',
                                        ideas=(AXIS,))):
        failures.append('both chapters resolve to the same schedule')
    return checks, failures


def area_membership(world):
    checks = 0
    failures = []

    loaded = {}
    for chapter, opener in POSTWAR_CHAPTERS:
        tree = next((value for key, value in top_level_writes(world.block(opener))
                     if key == 'tree'), None)
        checks += 1
        if tree is None:
            failures.append('%s loads no tree' % opener)
            continue
        loaded[chapter] = (tree, world.tree_ids(tree))

    seen = {}
    route_seeds = [()] + [tuple(sorted(route['seed'])) for route in route_plan(world)
                          if route['seed']]
    for chapter, (tree, ids) in loaded.items():
        checks += 1
        if not ids:
            failures.append('tree %s declares no focus id' % tree)
        seeds = route_seeds if chapter == 'spain_chapter_postwar' else [()]
        for date in BOOKMARKS + ('1940.6.2', '1941.6.2', '1941.1.2', '1943.1.2', '1945.6.2'):
            for ideas in ((), (AXIS,), (ALLIED,)):
                for completed in seeds:
                    for focus in run_schedule(world, chapter, date, ideas=ideas,
                                              completed=completed):
                        seen.setdefault(focus, set()).add(chapter)
                        checks += 1
                        if focus not in ids:
                            failures.append('%s completes %s, which is not in %s (%s)'
                                            % (chapter, focus, tree, date))

    checks += 1
    crossed = sorted(focus for focus, chapters in seen.items() if len(chapters) > 1)
    if crossed:
        failures.append('a focus is scheduled in both chapters: %s' % crossed)

    national = set(run_schedule(world, 'spain_chapter_postwar', '1945.6.2', ideas=(AXIS,)))
    checks += 1
    if any(focus.startswith('SPR4_') for focus in national):
        failures.append('the Nationalist chapter still completes SPR4_* ids: %s'
                        % sorted(focus for focus in national if focus.startswith('SPR4_')))
    checks += 1
    if not all(focus.startswith('SPA_') for focus in national):
        failures.append('the Nationalist list carries a non-SPA id: %s' % sorted(national))
    republican = set(run_schedule(world, 'spain_chapter_republican_postwar', '1945.6.2'))
    checks += 1
    if any(focus.startswith('SPA_') for focus in republican):
        failures.append('the Republican chapter completes SPA_* ids: %s'
                        % sorted(focus for focus in republican if focus.startswith('SPA_')))

    # The same invariant on real bookmarks, routed through the shipped openers.
    for date in BOOKMARKS:
        result = run_bookmark(world, date)
        if result['tree'] is None:
            checks += 1
            failures.append('%s loads no tree' % date)
            continue
        ids = world.tree_ids(result['tree'])
        for focus in result['completed']:
            checks += 1
            if focus not in ids:
                failures.append('bookmark %s completes %s outside %s'
                                % (date, focus, result['tree']))
    return checks, failures


def count_completions(entries):
    total = 0
    for key, value, _line in entries:
        if key == 'complete_national_focus':
            total += 1
        elif value[0] == 'block' and key in ('if', 'else_if', 'else'):
            total += count_completions(value[1])
    return total


def effect_keys(entries):
    """Every non-structural effect key reachable in a block."""
    keys = set()
    for key, value, _line in entries:
        if key == 'limit':
            continue
        if key in ('if', 'else_if', 'else') and value[0] == 'block':
            keys |= effect_keys(value[1][1:] if value[1] and value[1][0][0] == 'limit'
                                else value[1])
            continue
        keys.add(key)
    return keys


def focus_graph(relative):
    """Focus id -> (prerequisite blocks as OR alternatives, mutually exclusive ids)."""
    text = strip_comments(read_text(relative))
    graph = {}
    for match in re.finditer(r'^\t*focus\s*=\s*\{', text, re.M):
        body = brace_block(text, match.start())
        found = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', body)
        if not found:
            continue
        blocks = []
        for pre in re.finditer(r'prerequisite\s*=\s*\{', body):
            alts = tuple(re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)', brace_block(body, pre.end() - 1)))
            if alts:
                blocks.append(alts)
        excl = set()
        for mark in re.finditer(r'mutually_exclusive\s*=\s*\{', body):
            excl.update(re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)',
                                   brace_block(body, mark.end() - 1)))
        graph[found.group(1)] = (tuple(blocks), frozenset(excl))
    return graph


def closure_breaks(order, graph):
    """Scheduled ids that their own tree cannot reach, and the prerequisite blocks responsible.

    A prerequisite block is an OR group, so one reachable member satisfies it, and an id is
    reachable only if every one of its blocks is. The effect chain is emitted top to bottom, so
    reachability is accumulated in emission order, which also covers two ids sharing a date.
    """
    reachable = set()
    blocked = []
    for focus in order:
        blocks, _exclusive = graph.get(focus, ((), frozenset()))
        missing = tuple(alternatives for alternatives in blocks
                        if not any(alternative in reachable for alternative in alternatives))
        if missing:
            blocked.append((focus, missing))
        else:
            reachable.add(focus)
    return blocked


def exclusive_pairs(order, graph):
    """Pairs of scheduled ids the tree declares mutually exclusive."""
    scheduled = {focus: index for index, focus in enumerate(order)}
    pairs = set()
    for focus in order:
        _blocks, exclusive = graph.get(focus, ((), frozenset()))
        for other in exclusive:
            if other in scheduled:
                pairs.add(tuple(sorted((focus, other))))
    return sorted(pairs)


# The Nationalist post-war rows sit on the three sides of one exclusive fork in
# `common/national_focus/spain.txt`: `SPA_the_phalanx_ascendant`, `SPA_unify_the_nationalist_front`
# and `SPA_supremacy_of_the_communion` each exclude the other two, and each post-war pin hangs off
# one of the three. Which branch completes which row is therefore a property of the tree plus the
# `has_completed_focus` id the branch tests, and everything below derives it from both instead of
# restating it: `need_closure` closes one side over its prerequisites, `topological_order` states
# the order those prerequisites force, and `route_plan` runs both for the side each branch serves.

REPUBLICAN_PREEXISTING_EXCLUSIVE = (('SPR4_armed_neutrality', 'SPR4_the_european_war'),)


def need_closure(focus, taken, banned, graph):
    """What a route must complete before `focus`, given what it already holds.

    A `prerequisite` block is satisfied by one of its members and every block must be satisfied,
    so each block contributes the first alternative that can itself be closed. `banned` holds the
    ids the route's exclusive side forbids, including the siblings of anything already chosen, so
    an alternative behind a locked-out side is never taken. Returns `(taken, banned)` or None when
    the route cannot carry the focus at all.
    """
    if focus in taken:
        return taken, banned
    if focus in banned or focus not in graph:
        return None
    taken, banned = taken | {focus}, banned | graph[focus][1]
    for alternatives in graph[focus][0]:
        if any(alternative in taken for alternative in alternatives):
            continue
        closed = None
        for alternative in alternatives:
            candidate = need_closure(alternative, taken, banned, graph)
            if candidate is not None:
                closed = candidate
                break
        if closed is None:
            return None
        taken, banned = closed
    return taken, banned


def topological_order(focuses, taken, graph):
    """`focuses` in prerequisite order, ties broken by the tree's own declaration order."""
    rank = {focus: index for index, focus in enumerate(graph)}
    remaining, done, order = set(focuses), set(taken), []
    while remaining:
        ready = sorted((focus for focus in remaining
                        if all(any(alternative in done for alternative in block)
                               for block in graph[focus][0])),
                       key=lambda focus: rank[focus])
        if not ready:
            raise Unsupported('no prerequisite order for %s' % sorted(remaining))
        for focus in ready:
            order.append(focus)
            done.add(focus)
            remaining.discard(focus)
    return order


def nationalist_branches(world):
    """The route branches of the Nationalist chapter, read from the shipped schedule.

    Returns `(selector, body)` per branch in source order. A selector is the fork side the branch
    tests with `has_completed_focus`, and the `else` branch carries None because it serves the
    side a country reaches when it completed neither tested side.
    """
    for key, value, _line in world.block(SCHEDULE):
        if key != 'if' or value[0] != 'block':
            continue
        trigger, body = limit_of(value[1], SCHEDULE)
        flags = [entry[1][1] for entry in trigger
                 if entry[0] == 'has_country_flag' and entry[1][0] == 'scalar']
        if 'spain_chapter_postwar' not in flags:
            continue
        branches, shape = [], []
        for branch, branch_value, branch_line in body:
            if branch_value[0] != 'block':
                raise Unsupported('%s branch %s without a block at line %d'
                                  % (SCHEDULE, branch, branch_line))
            if branch == 'else':
                branches.append((None, branch_value[1]))
                shape.append('else')
                continue
            if branch not in ('if', 'else_if'):
                raise Unsupported('%s branch carries %s at line %d'
                                  % (SCHEDULE, branch, branch_line))
            branch_trigger, action = limit_of(branch_value[1], SCHEDULE)
            tested = [entry[1][1] for entry in branch_trigger
                      if entry[0] == 'has_completed_focus' and entry[1][0] == 'scalar']
            if len(tested) != 1:
                raise Unsupported('%s %s branch tests %d completed focuses'
                                  % (SCHEDULE, branch, len(tested)))
            branches.append((tested[0], action))
            shape.append(branch)
        if shape != ['if', 'else_if', 'else']:
            raise Unsupported('the route branches are %s, not one if / else_if / else chain'
                              % shape)
        return branches
    raise Unsupported('%s has no Nationalist chapter block' % SCHEDULE)


def default_side(branches, graph):
    """The fork side the `else` branch serves: the one both tested sides exclude."""
    tested = [selector for selector, _body in branches if selector is not None]
    candidates = sorted(focus for focus, (_blocks, exclusive) in graph.items()
                        if all(side in exclusive for side in tested))
    if len(candidates) != 1:
        raise Unsupported('the excluded side is ambiguous: %s' % candidates)
    return candidates[0]


def route_groups(body, where):
    """A branch's date-gated groups in emission order: `(date, trigger, ids)`."""
    groups = []
    for key, value, line in body:
        if key not in ('if', 'else_if'):
            raise Unsupported('%s emits %s outside a date gate at line %d' % (where, key, line))
        trigger, action = limit_of(value[1], where)
        dates = [(entry[1][1][0], entry[1][1][1]) for entry in trigger
                 if entry[0] == 'date' and entry[1][0] == 'compare']
        if len(dates) != 1 or dates[0][0] != '>':
            raise Unsupported('%s gate at line %d is not one "date >" test' % (where, line))
        ids = []
        for sub_key, sub_value, sub_line in action:
            if sub_key != 'complete_national_focus' or sub_value[0] != 'scalar':
                raise Unsupported('%s group carries %s at line %d'
                                  % (where, sub_key, sub_line))
            ids.append(sub_value[1])
        groups.append((dates[0][1], trigger, tuple(ids)))
    return groups


def route_plan(world):
    """Per-branch expectations derived from the tree and the branch's own route detection.

    Each entry carries the side the branch serves, the ids that side is detected from (empty for
    the default branch, whose side the schedule has to complete itself), the closure of the seven
    pins that side can carry in prerequisite order, and the pins it cannot carry.
    """
    tree = next(value for key, value in
                top_level_writes(world.block('spain_open_postwar_chapter')) if key == 'tree')
    graph = focus_graph(world.trees[tree])
    branches = nationalist_branches(world)
    excluded = default_side(branches, graph)
    sides = [selector if selector is not None else excluded for selector, _body in branches]
    if len(sides) != 3 or len(set(sides)) != 3:
        raise Unsupported('the branches serve %s, not the three fork sides' % sides)

    plan = []
    for (selector, body), side in zip(branches, sides):
        seed = set() if selector is None else {side}
        taken, banned = set(seed), set(graph[side][1])
        if selector is None:
            closed = need_closure(side, set(), set(graph[side][1]), graph)
            if closed is None:
                raise Unsupported('the default side %s cannot be completed' % side)
            taken, banned = closed
        pins = []
        for pin in NATIONALIST_PINS:
            closed = need_closure(pin, set(taken), set(banned), graph)
            if closed is None:
                continue
            pins.append(pin)
            taken, banned = closed
        plan.append({'selector': selector, 'side': side, 'seed': seed, 'tree': tree,
                     'graph': graph, 'body': body,
                     'order': topological_order(taken - seed, seed, graph),
                     'pins': tuple(pins),
                     'blocked': tuple(pin for pin in NATIONALIST_PINS if pin not in pins)})
    return plan


def area_closure(world):
    """Every scheduled id is closed over its own tree, and no exclusive pair is manufactured."""
    checks = 0
    failures = []

    trees = {}
    for chapter, opener in POSTWAR_CHAPTERS:
        tree = next((value for key, value in top_level_writes(world.block(opener))
                     if key == 'tree'), None)
        checks += 1
        if tree is None:
            failures.append('%s loads no tree' % opener)
            continue
        trees[chapter] = (tree, focus_graph(world.trees[tree]))

    for date in ('1941.1.2', '1943.1.2', '1945.6.2'):
        order = run_schedule(world, 'spain_chapter_republican_postwar', date)
        tree, graph = trees['spain_chapter_republican_postwar']
        breaks = closure_breaks(order, graph)
        checks += 1
        if breaks:
            failures.append('%s on %s completes %s before their prerequisites: %s'
                            % (tree, date, [focus for focus, _ in breaks], breaks))
        checks += 1
        pairs = [tuple(pair) for pair in exclusive_pairs(order, graph)]
        if date == '1945.6.2':
            checks += 1
            if pairs != list(REPUBLICAN_PREEXISTING_EXCLUSIVE):
                failures.append('%s on %s completes exclusive pairs %s, expected only the pair '
                                'the ledger already carried' % (tree, date, pairs))
        elif pairs:
            failures.append('%s on %s completes exclusive pairs %s before the ledger date'
                            % (tree, date, pairs))

    # The Nationalist half is derived per route in area_nationalist. The invariant every route
    # shares is checked here on the real bookmarks, so a chapter that gains an id from a routing
    # change cannot slip past the per-route samples.
    chapter_of = {opener: chapter for chapter, opener in POSTWAR_CHAPTERS}
    for date in BOOKMARKS:
        result = run_bookmark(world, date)
        if result['tree'] is None:
            checks += 1
            failures.append('%s loads no tree' % date)
            continue
        chapter = chapter_of.get(result['opener'])
        if chapter is None:
            continue
        tree, graph = trees[chapter]
        order = result['completed']
        checks += 1
        if exclusive_pairs(order, graph):
            failures.append('%s completes both sides of %s' % (date, exclusive_pairs(order, graph)))
        if chapter == 'spain_chapter_republican_postwar':
            checks += 1
            if closure_breaks(order, graph):
                failures.append('%s leaves %s unclosed' % (date, closure_breaks(order, graph)))
    return checks, failures


def area_cheap(world):
    checks = 0
    failures = []

    start = world.effects_text.index('\n' + SCHEDULE + ' = {')
    end = world.effects_text.index('\n' + BOOTSTRAP + ' = {')
    schedule_text = world.effects_text[start:end]

    checks += 1
    for key in LOOP_KEYS:
        if key in schedule_text:
            failures.append('the schedule uses %r, which is not a date-gated chain' % key)
    checks += 1
    if 'on_daily' in schedule_text:
        failures.append('the schedule is driven by an on_daily hook')

    # The post-war chapters do one thing only: complete an existing focus. No variable, flag,
    # idea or balance write means a second run on the same date cannot duplicate an effect.
    post_war_keys = set()
    for key, value, _line in world.block(SCHEDULE):
        if key == 'if' and value[0] == 'block':
            limit, body = value[1][0], value[1][1:]
            flags_tested = [entry[1][1] for entry in limit[1][1]
                            if entry[0] == 'has_country_flag' and entry[1][0] == 'scalar']
            if any(flag in POSTWAR_FLAGS for flag in flags_tested):
                post_war_keys |= effect_keys(body)
    checks += 1
    if post_war_keys != {'complete_national_focus'}:
        failures.append('a post-war chapter writes %s, not only focus completions'
                        % sorted(post_war_keys - {'complete_national_focus'}))

    plan = route_plan(world)
    default = next(route for route in plan if route['selector'] is None)
    ledger = len(set(REPUBLICAN_LEDGER) | set(REPUBLICAN_1941))
    national = run_schedule(world, 'spain_chapter_postwar', '1945.6.2', ideas=(ALLIED,))
    republican = run_schedule(world, 'spain_chapter_republican_postwar', '1945.6.2')
    checks += 1
    if len(republican) != ledger:
        failures.append('the Republican ledger completes %d focuses, expected %d'
                        % (len(republican), ledger))
    # The default route carries both join rows and only one of them can fire, so a run on an
    # allied country completes the derived closure minus the axis row.
    expected = len(default['order']) - 1 + ledger
    checks += 1
    if len(national) + len(republican) != expected:
        failures.append('a 1945 run completes %d focuses, expected %d'
                        % (len(national) + len(republican), expected))

    # The same date evaluated twice returns the same ordered list and repeats no id, which is
    # the source-level half of "re-running it does not error or duplicate".
    for chapter in ('spain_chapter_postwar', 'spain_chapter_republican_postwar'):
        first = run_schedule(world, chapter, '1945.6.2', ideas=(ALLIED,))
        second = run_schedule(world, chapter, '1945.6.2', ideas=(ALLIED,))
        checks += 1
        if first != second:
            failures.append('%s does not evaluate identically twice' % chapter)
        checks += 1
        if len(first) != len(set(first)):
            failures.append('%s repeats an id in one run: %s' % (chapter, first))

    checks += 1
    inside = count_completions(world.block(SCHEDULE))
    derived = PREWAR_LINES + sum(len(route['order']) for route in plan) + ledger
    if inside != derived:
        failures.append('the schedule holds %d completions, expected %d'
                        % (inside, derived))
    checks += 1
    postwar = 0
    for key, value, _line in world.block(SCHEDULE):
        if key == 'if' and value[0] == 'block':
            limit = value[1][0]
            flags_tested = [entry[1][1] for entry in limit[1][1]
                            if entry[0] == 'has_country_flag' and entry[1][0] == 'scalar']
            if any(flag in POSTWAR_FLAGS for flag in flags_tested):
                postwar += count_completions(value[1][1:])
    if postwar != sum(len(route['order']) for route in plan) + ledger:
        failures.append('the post-war chapters hold %d lines, expected %d'
                        % (postwar, sum(len(route['order']) for route in plan) + ledger))
    return checks, failures


AREAS = (
    ('openers', area_openers),
    ('routing', area_routing),
    ('nationalist', area_nationalist),
    ('republican', area_republican),
    ('membership', area_membership),
    ('closure', area_closure),
    ('cheap', area_cheap),
)


# ---------------------------------------------------------------------------------------------
# Mutants
# ---------------------------------------------------------------------------------------------

def mutate_spr4_in_nationalist(text):
    anchor = ('\t\t\t\tlimit = { date > 1940.6.1 }\n'
              '\t\t\t\tcomplete_national_focus = SPA_secure_the_national_defense_council\n')
    if anchor not in text:
        raise Unsupported('the phalanx route anchor moved')
    return text.replace(
        anchor, anchor + '\t\t\t\tcomplete_national_focus = SPR4_the_republic_endures\n', 1)


def mutate_both_join(text):
    first = 'limit = { date > 1941.6.1 has_idea = spain_axis_alignment }'
    second = '\t\t\telse_if = {\n\t\t\t\tlimit = { date > 1941.6.1 has_idea = spain_allied_alignment }'
    if first not in text or second not in text:
        raise Unsupported('the alignment gate moved')
    mutated = text.replace(first, 'limit = { date > 1941.6.1 }', 1)
    mutated = mutated.replace(second, '\t\t\tif = {\n\t\t\t\tlimit = { date > 1941.6.1 }', 1)
    if mutated == text:
        raise Unsupported('the alignment mutation changed nothing')
    return mutated


def mutate_nationalist_ancestor(text):
    line = '\t\t\t\tcomplete_national_focus = SPA_suspend_the_constitution\n'
    if line not in text:
        raise Unsupported('the phalanx ancestor row is missing before mutation')
    return text.replace(line, '', 1)


def mutate_pin_on_wrong_route(text):
    line = '\t\t\t\tcomplete_national_focus = SPA_join_the_axis\n'
    if line not in text:
        raise Unsupported('the phalanx join row is missing before mutation')
    return text.replace(line, line + '\t\t\t\tcomplete_national_focus = SPA_the_iberian_pact\n', 1)


def mutate_mutex_sibling(text):
    line = '\t\t\t\tcomplete_national_focus = SPA_secure_the_national_defense_council\n'
    if line not in text:
        raise Unsupported('the phalanx directory row is missing before mutation')
    return text.replace(
        line, '\t\t\t\tcomplete_national_focus = SPA_unify_the_nationalist_front\n' + line, 1)


def mutate_drop_1941(text):
    dropped = 0
    for focus in REPUBLICAN_1941:
        line = '\t\t\tcomplete_national_focus = %s\n' % focus
        if line not in text:
            raise Unsupported('the %s row is missing before mutation' % focus)
        text = text.replace(line, '', 1)
        dropped += 1
    if dropped != len(REPUBLICAN_1941):
        raise Unsupported('only %d 1941 rows were dropped' % dropped)
    return text


def mutate_bop_not_cleared(text):
    line = '\tclr_country_flag = %s\n' % BOP_FLAG
    if text.count(line) < 2:
        raise Unsupported('only %d openers clear the pending balance' % text.count(line))
    return text.replace(line, '', 1)


def mutate_drop_ancestor(text):
    line = '\t\t\tcomplete_national_focus = SPR4_the_falange_remnant\n'
    if line not in text:
        raise Unsupported('the falange ancestor row is missing before mutation')
    return text.replace(line, '', 1)


MUTANTS = (
    ('SPR4 id inside the Nationalist block', mutate_spr4_in_nationalist,
     ('membership',), 'not in spanish_focus'),
    ('alignment gate removed', mutate_both_join, ('nationalist',), 'both join focuses'),
    ('Nationalist ancestor dropped', mutate_nationalist_ancestor, ('nationalist',),
     'is not closed over the tree'),
    ('pin added to a route that cannot carry it', mutate_pin_on_wrong_route, ('nationalist',),
     'cannot carry'),
    ('mutex sibling added to a route', mutate_mutex_sibling, ('nationalist',), 'both sides'),
    ('1941 Republican rows dropped', mutate_drop_1941, ('republican',), '1941.1.2'),
    ('pending balance not cleared', mutate_bop_not_cleared, ('openers',), BOP_FLAG),
    ('1941 ancestor row dropped', mutate_drop_ancestor, ('closure',), 'before their prerequisites'),
)


# ---------------------------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------------------------

def main(argv):
    detail = '--detail' in argv
    checks = 0
    failures = []

    world = World()
    for name, function in AREAS:
        try:
            area_checks, area_fails = function(world)
        except Unsupported as error:
            checks += 1
            failures.append('%s could not be modelled: %s' % (name, error))
            continue
        checks += area_checks
        failures.extend(area_fails)
        if detail:
            print('[%s] %d checks, %d failures' % (name, area_checks, len(area_fails)))

    for label, mutate, areas, token in MUTANTS:
        try:
            mutant = World(mutate(world.effects_text))
        except Unsupported as error:
            checks += 1
            failures.append('mutant %r could not be applied: %s' % (label, error))
            continue
        caught = []
        for name in areas:
            function = dict(AREAS)[name]
            try:
                _area_checks, area_fails = function(mutant)
            except Unsupported as error:
                area_fails = ['not modelled: %s' % error]
            caught.extend(area_fails)
        checks += 1
        if not caught:
            failures.append('mutant %r passes, so this test discriminates nothing' % label)
            continue
        checks += 1
        if not any(token in failure for failure in caught):
            failures.append('mutant %r is caught, but not for %r: %s'
                            % (label, token, caught[0]))
        if detail:
            print('  mutant [%s] %d failures, e.g. %s' % (label, len(caught), caught[0]))

    print('%d checks, %d failures' % (checks, len(failures)))
    for failure in failures:
        print('  FAIL ' + failure)
    print('Read: ' + EFFECTS_PATH + ', ' + FOCUS_DIR + '/spain.txt, '
          + FOCUS_DIR + '/spain_republic_postwar.txt')
    print('Not performed: no game launch, no bookmark loaded, no focus clicked, no daily tick.')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
