"""Regression test: the two interwar Gulf naval rewards build on the Persian Gulf coast.

`IR2_gulf_claims` and `IR2_navy_gulf` used to place a naval base and a dockyard in state 411.
State 411 is Isfahan: every one of its nine provinces is landlocked in `map/definition.csv`, so a
naval base there had no sea to serve and a dockyard had no coastal province to sit in. Both
rewards now target state 413, Khuzestan, which owns the coastal provinces 5005 and 5089.

The test reads the shipped sources rather than restating them:

    1. `common/national_focus/iran_interwar.txt` for the two focus blocks and their rewards,
    2. `history/states/413-Khuzestan.txt` for the province list, category, buildings and owner,
    3. `map/definition.csv` for which of those provinces are actually coastal,
    4. `common/buildings/00_buildings.txt` for the slot class and coastal restriction of the two
       building types,
    5. the vanilla state category for the shared-slot budget of the category 413 uses,
    6. `localisation/english/iran_interwar_l_english.yml` for the focus description, which named a
       port in another state before the repair and has to describe the coast the dockyard is now
       built on.

`audit()` returns the failures it finds for a given focus-file text, so the same checker runs
against the pre-repair revision pinned below and must reject it. That mutant control is what
proves the test detects the defect instead of describing the current file.

Two pins are in play, and they answer different questions:

    * `BASELINE_REV` is the pre-repair file. `audit()` must keep rejecting it, so it stays the
      mutant control and never moves.
    * `PRESERVATION_REV` is the commit that integrated the two Gulf repairs. The preservation
      checks compare the working tree against it, because between the two revisions the interwar
      chapter also wrapped ten raw flag conditions in ten other focuses' requirement blocks in
      English tooltips (its share of the sixteen the same integration wrapped across both
      chapters) and gained ten localisation keys. Both are enumerated by name in
      `ACCEPTED_DRIFT_FOCUSES` and `ACCEPTED_DRIFT_LOC_KEYS` and asserted against the real
      revision diff, so freezing to this commit cannot bless drift the lists do not cover.
    * `ACCEPTED_FOCUS_EDITS` declares the single later reward repair (the Khuzestan route gate)
      as an exact transformation of the preservation body. Any other change to any focus reward,
      and any wider shape of the declared one, still fails.

Run from the repository root:

    python .tools/tests/test_iran_gulf_rewards.py           # exit 0 = pass
    python .tools/tests/test_iran_gulf_rewards.py --detail  # print every check
    python .tools/tests/test_iran_gulf_rewards.py --dump    # print the parsed rewards

This is a source and map-data check. It proves what the script and the map files say, not what
the engine does when the focus is clicked; that still needs a player-run game, which this test
never performs.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FOCUS_PATH = 'common/national_focus/iran_interwar.txt'
STATE_PATH = 'history/states/413-Khuzestan.txt'
OLD_STATE_PATH = 'history/states/411-Hormozgan.txt'
OTHER_STATE_PATH = 'history/states/412-Fars.txt'
DEFINITION_PATH = 'map/definition.csv'
BUILDINGS_PATH = 'common/buildings/00_buildings.txt'
LOC_PATH = 'localisation/english/iran_interwar_l_english.yml'

# The pre-repair file, which built both rewards in state 411. Pinned by full object name: a
# mutable `HEAD` would stop being a mutant once the repair is committed. This revision stays the
# mutant control - `audit()` must keep rejecting it - and is never used for preservation.
BASELINE_REV = 'f8f9225b048874109ff965654c9fb7fa973df0cd'

# The integration commit that landed the two Gulf repairs. The preservation checks compare against
# this revision, because after BASELINE_REV the interwar chapter also wrapped ten raw flag
# conditions in ten other focuses' requirement blocks in English tooltips and gained ten
# localisation keys. Both are enumerated below and asserted against the real revision diff, so this
# pin cannot bless drift the lists do not cover.
PRESERVATION_REV = 'b978f23e6d9588c9131786e4b75da46f24149040'

# focus id -> the ten focuses whose requirement blocks changed between the two revisions. Each one
# differs only inside its `available`/`bypass` block; `focus_drift()` asserts that.
ACCEPTED_DRIFT_FOCUSES = (
    'IR2_reject_the_agreement',
    'IR2_accept_the_agreement',
    'IR2_reza_khan_minister',
    'IR2_jangali_congress',
    'IR2_nationalist_press',
    'IR2_nationalist_officers',
    'IR2_parliamentary_republic',
    'IR2_pahlavi_settlement',
    'IR2_nationalist_front',
    'IR2_socialist_republic',
)

# The ten keys that commit added to the interwar localisation file. No key was removed and only the
# repaired description value changed.
ACCEPTED_DRIFT_LOC_KEYS = (
    'iran_anglo_persian_crisis_open_tt',
    'iran_army_decisive_voice_tt',
    'iran_cossack_refusal_tt',
    'iran_gilan_republic_proclaimed_tt',
    'iran_jangali_congress_held_tt',
    'iran_majlis_ascendant_tt',
    'iran_majlis_predominance_tt',
    'iran_nationalist_front_base_tt',
    'iran_nationalist_movement_organized_tt',
    'iran_reza_at_the_army_tt',
)

# The one focus reward allowed to differ from the preservation revision: the Khuzestan capacity
# project charged the British concession on both of its mutually exclusive entrance branches, so a
# domestic-capital Iran paid for a deal it refused. The declared edit wraps that single call in the
# route test the prerequisites already enforce; nothing else in the focus moves.
ACCEPTED_FOCUS_EDITS = {
    'IR2_khuzestan_oil': 'the route gate on the British concession',
}

KHUZESTAN_CONCESSION = ('iran_concede_british_small', ('scalar', 'yes'))
KHUZESTAN_GATE = ('if', ('block', [
    ('limit', ('block', [
        ('NOT', ('block', [
            ('has_country_flag', ('scalar', 'iran_domestic_capital'), 0),
        ]), 0),
    ]), 0),
    ('iran_concede_british_small', ('scalar', 'yes'), 0),
]), 0)

NAVAL_FOCUS = 'IR2_gulf_claims'
DOCKYARD_FOCUS = 'IR2_navy_gulf'

TARGET_STATE = 413
OLD_STATE = 411
# Both coastal in map/definition.csv, both inside state 413.
COASTAL_PORT = 5005
COASTAL_SLOP = 5089

# State 412 owns province 7982, which vanilla localises as "Bandar e'Abbas"
# (`<game>/localisation/english/victory_points_l_english.yml:779`). The pre-repair description
# named that city while the reward built in a landlocked state, so the name is a map fact rather
# than a wording preference.
OTHER_STATE = 412
ABBAS_PROVINCE = 7982
ABBAS_SPELLINGS = ('Bandar Abbas', "Bandar e'Abbas", 'Abbas')
# The state name from `history/states/413-Khuzestan.txt`, which the description has to match.
TARGET_STATE_NAME = 'Khuzestan'
# The reward builds a dockyard, and the sloop order is the text's other promise.
DESC_REQUIRED_TERMS = ('dockyard', 'sloops')

DESC_KEY = 'IR2_navy_gulf_desc'

# Reward entries inside `completion_reward` that must survive the retarget unchanged, per focus,
# with the exact value each one must keep.
PRESERVED_EFFECTS = {
    NAVAL_FOCUS: [
        ('set_country_flag', 'iran_gulf_claims'),
        ('add_war_support', 'constant:iran_story.war_support_gain'),
    ],
    DOCKYARD_FOCUS: [
        ('set_country_flag', 'iran_gulf_squadron'),
        ('navy_experience', 'constant:iran_story.navy_experience'),
    ],
}

VANILLA_GAME_DIRS = [
    os.environ.get('HOI4_GAME_DIR', ''),
    r'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV',
    r'C:/Program Files/Paradox Interactive/Hearts of Iron IV',
]


class Unsupported(Exception):
    """A script shape or file layout this check does not model. Failing loudly beats guessing."""


# ---------------------------------------------------------------------------------------------
# Parser: Clausewitz text -> nested (key, value, line) entries
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
        elif char in ' \t\r\n':
            if char == '\n':
                line += 1
            index += 1
        else:
            start = index
            while index < length and text[index] not in ' \t\r\n{}=#':
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
        if tokens[index + 1][0] != '=':
            # A bare token inside a block: the province lists and other whitespace-separated
            # value lists used by state and map files.
            entries.append((text, ('scalar', text), line))
            index += 1
            continue
        if index + 2 >= len(tokens):
            raise Unsupported('trailing %s at line %d' % (text, line))
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


def parse_text(text):
    entries, _ = parse_block(tokenize(text), 0)
    return entries


def read_repo(path):
    with open(ROOT / path, 'r', encoding='utf-8-sig') as handle:
        return handle.read()


# ---------------------------------------------------------------------------------------------
# Source readers
# ---------------------------------------------------------------------------------------------

def read_coastal_provinces():
    """province id -> True when map/definition.csv marks it coastal."""
    coastal = {}
    text = read_repo(DEFINITION_PATH)
    for line in text.split('\n'):
        fields = line.strip().split(';')
        if len(fields) < 7:
            continue
        try:
            province = int(fields[0])
        except ValueError:
            continue
        coastal[province] = fields[5] == 'true'
    if not coastal:
        raise Unsupported('definition.csv parsed to no provinces')
    return coastal


def read_state(path):
    """id, provinces, category, owner, shared-slot levels and provincial building levels."""
    entries = parse_text(read_repo(path))
    state = {'path': path, 'provinces': [], 'category': None, 'owner': None,
             'state_buildings': {}, 'provincial_buildings': {}}
    for key, value, _ in entries:
        if key == 'state' and value[0] == 'block':
            for inner_key, inner_value, _ in value[1]:
                if inner_key == 'id' and inner_value[0] == 'scalar':
                    state['id'] = int(inner_value[1])
                elif inner_key == 'provinces' and inner_value[0] == 'block':
                    state['provinces'] = [int(key) for key, value, _ in inner_value[1]
                                          if value[0] == 'scalar' and re.fullmatch(r'\d+', key)]
                elif inner_key == 'state_category' and inner_value[0] == 'scalar':
                    state['category'] = inner_value[1]
                elif inner_key == 'history' and inner_value[0] == 'block':
                    read_state_history(state, inner_value[1])
    if 'id' not in state:
        raise Unsupported('%s has no state id' % path)
    if not state['provinces']:
        raise Unsupported('%s has no province list' % path)
    return state


def read_state_history(state, history_entries):
    for key, value, _ in history_entries:
        if key == 'owner' and value[0] == 'scalar':
            # Only the undated owner: dated blocks are bookmark initialisation, not the
            # standard start the focus reward is measured against.
            state['owner'] = state['owner'] or value[1]
        elif key == 'buildings' and value[0] == 'block':
            for entry_key, entry_value, _ in value[1]:
                if entry_value[0] == 'scalar':
                    state['state_buildings'][entry_key] = int(float(entry_value[1]))
                elif entry_value[0] == 'block' and re.fullmatch(r'\d+', entry_key):
                    province = int(entry_key)
                    for building, level, _ in entry_value[1]:
                        if level[0] != 'scalar':
                            raise Unsupported('nested building block in %s' % state['path'])
                        state['provincial_buildings'].setdefault(province, {})[building] = \
                            int(float(level[1]))


def read_building_kinds():
    """building id -> {'shares_slots': bool, 'only_coastal': bool, 'province_max'/'state_max'}."""
    entries = parse_text(read_repo(BUILDINGS_PATH))
    kinds = {}
    for key, value, _ in entries:
        if key != 'buildings' or value[0] != 'block':
            continue
        for name, body, _ in value[1]:
            if body[0] != 'block':
                continue
            info = {'shares_slots': False, 'only_coastal': False, 'province_max': None,
                    'state_max': None}
            for field, field_value, _ in body[1]:
                if field == 'only_costal' and field_value[0] == 'scalar':
                    info['only_coastal'] = field_value[1] == 'yes'
                elif field == 'level_cap' and field_value[0] == 'block':
                    for cap, cap_value, _ in field_value[1]:
                        if cap_value[0] != 'scalar':
                            continue
                        if cap == 'shares_slots':
                            info['shares_slots'] = cap_value[1] == 'yes'
                        elif cap in ('province_max', 'state_max'):
                            info[cap] = int(float(cap_value[1]))
            kinds[name] = info
    if 'naval_base' not in kinds or 'dockyard' not in kinds:
        raise Unsupported('building definitions missing naval_base or dockyard')
    return kinds


def read_category_slots(category):
    """Shared slot budget for a state category, from the mod or the installed game."""
    for base in [ROOT] + [Path(path) for path in VANILLA_GAME_DIRS if path]:
        folder = base / 'common' / 'state_category'
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob('*.txt')):
            entries = parse_text(path.read_text(encoding='utf-8-sig', errors='replace'))
            for key, value, _ in entries:
                if key != 'state_categories' or value[0] != 'block':
                    continue
                for name, body, _ in value[1]:
                    if name != category or body[0] != 'block':
                        continue
                    for field, field_value, _ in body[1]:
                        if field == 'local_building_slots' and field_value[0] == 'scalar':
                            return int(float(field_value[1])), str(path)
    return None, None


def read_focus_blocks(text):
    """focus id -> list of (key, value, line) entries for every focus in the file.

    Focuses live inside the `focus_tree` block, so the tree bodies are walked as well as the
    top level.
    """
    focuses = {}
    roots = parse_text(text)
    scopes = [roots]
    for key, value, _ in roots:
        if key == 'focus_tree' and value[0] == 'block':
            scopes.append(value[1])
    for entries in scopes:
        for key, value, _ in entries:
            if key != 'focus' or value[0] != 'block':
                continue
            body = value[1]
            focus_id = None
            for field, field_value, _ in body:
                if field == 'id' and field_value[0] == 'scalar':
                    focus_id = field_value[1]
            if focus_id is None:
                raise Unsupported('focus block without an id')
            focuses[focus_id] = body
    if not focuses:
        raise Unsupported('no focus blocks found')
    return focuses


def fields_of(body):
    """field -> list of (value, line) for one focus body."""
    fields = {}
    for field, value, line in body:
        fields.setdefault(field, []).append((value, line))
    return fields


def state_relations(body):
    """The state-scoped relation blocks inside a focus, rewards included.

    `completion_reward` and its siblings are walked, because that is where a focus builds a
    building; a relation sitting directly on the focus would be found too.
    """
    found = []
    for key, value, line in body:
        if value[0] != 'block':
            continue
        if re.fullmatch(r'\d+', key):
            found.append((int(key), value[1], line))
        elif key.endswith('reward') or key == 'completion_reward':
            for inner_key, inner_value, inner_line in value[1]:
                if inner_value[0] == 'block' and re.fullmatch(r'\d+', inner_key):
                    found.append((int(inner_key), inner_value[1], inner_line))
    return found


def constructions_of(body, focus_id):
    """Every state-scoped add_building_construction inside a focus, in document order."""
    found = []
    for state, relation_body, _ in state_relations(body):
        for key, value, line in relation_body:
            if key != 'add_building_construction' or value[0] != 'block':
                continue
            spec = {}
            for field, field_value, _ in value[1]:
                spec[field] = field_value[1] if field_value[0] == 'scalar' else 'filter'
            found.append({'focus': focus_id, 'state': state, 'line': line, 'spec': spec})
    return found


def reward_entries(body):
    """The scalar entries of a focus's `completion_reward`, key -> value."""
    for key, value, _ in body:
        if key == 'completion_reward' and value[0] == 'block':
            return dict((field, field_value[1]) for field, field_value, _ in value[1]
                        if field_value[0] == 'scalar')
    return {}


def normalize(entries, drop_constructions=False):
    """A comparable shape for a block, optionally without its building constructions."""
    out = []
    for key, value, _ in entries:
        if value[0] == 'scalar':
            out.append((key, 'scalar', value[1]))
            continue
        child = value[1]
        if drop_constructions and re.fullmatch(r'\d+', key) \
                and any(inner == 'add_building_construction' for inner, _, _ in child):
            continue
        out.append((key, 'block', normalize(child, drop_constructions)))
    return out


def focus_signature(body):
    """Everything in a focus block except its state-scoped construction lines."""
    return normalize(body, drop_constructions=True)


def apply_accepted_edit(focus_id, body):
    """The preservation body with the declared edit applied, or None when it did not apply.

    The substitution is exact: one `iran_concede_british_small = yes` inside `completion_reward`
    becomes one `if = { limit = { NOT = { has_country_flag = iran_domestic_capital } } ... }`.
    """
    if focus_id not in ACCEPTED_FOCUS_EDITS:
        return None
    applied = False
    out = []
    for key, value, line in body:
        if key != 'completion_reward' or value[0] != 'block':
            out.append((key, value, line))
            continue
        entries = []
        for inner_key, inner_value, inner_line in value[1]:
            if (inner_key, inner_value) == KHUZESTAN_CONCESSION:
                entries.append(KHUZESTAN_GATE)
                applied = True
            else:
                entries.append((inner_key, inner_value, inner_line))
        out.append((key, ('block', entries), line))
    return out if applied else None


def preservation_failures(current, kept, current_text=None, kept_text=None):
    """Every way `current` violates the preservation baseline `kept`."""
    failures = []
    if current_text is not None and kept_text is not None:
        guarded = {NAVAL_FOCUS, DOCKYARD_FOCUS} | set(ACCEPTED_FOCUS_EDITS)
        if code_outside(current_text, guarded) != code_outside(kept_text, guarded):
            failures.append('code outside the two repaired focus blocks and the declared edit '
                            'changed')
    if len(current) != len(kept):
        failures.append('focus count %d vs %d' % (len(current), len(kept)))
    for ident in kept:
        if ident not in current:
            failures.append('%s is missing' % ident)
            continue
        if ident in (NAVAL_FOCUS, DOCKYARD_FOCUS) or ident in ACCEPTED_FOCUS_EDITS:
            continue
        if focus_signature(current[ident]) != focus_signature(kept[ident]):
            failures.append('%s changed a field other than its building construction' % ident)
    for ident in current:
        if ident not in kept:
            failures.append('%s was added' % ident)
    for focus_id in (NAVAL_FOCUS, DOCKYARD_FOCUS):
        if focus_id not in current or focus_id not in kept:
            failures.append('%s is missing' % focus_id)
            continue
        if focus_signature(current[focus_id]) != focus_signature(kept[focus_id]):
            failures.append('%s changed a field other than its building construction' % focus_id)
        if len(state_relations(current[focus_id])) != 1:
            failures.append('%s no longer carries exactly one state relation' % focus_id)
    for focus_id, described in sorted(ACCEPTED_FOCUS_EDITS.items()):
        if focus_id not in current or focus_id not in kept:
            failures.append('%s is missing' % focus_id)
            continue
        expected = apply_accepted_edit(focus_id, kept[focus_id])
        if expected is None or normalize(expected) != normalize(current[focus_id]):
            failures.append('%s does not carry %s' % (focus_id, described))
    return failures


def focus_drift():
    """focus id -> True when only its requirement blocks changed between the two baseline pins.

    False means some other field moved, and 'added'/'removed' means the focus itself did. Used to
    prove the `PRESERVATION_REV` pin covers exactly the focuses named in `ACCEPTED_DRIFT_FOCUSES`.
    """
    before = read_focus_blocks(baseline_file(FOCUS_PATH))
    after = read_focus_blocks(preservation_file(FOCUS_PATH))
    drift = {}
    for ident in after:
        if ident not in before:
            drift[ident] = 'added'
            continue
        if focus_signature(before[ident]) == focus_signature(after[ident]):
            continue
        drift[ident] = (
            normalize([(key, value, line) for key, value, line in before[ident]
                       if key not in ('available', 'bypass')])
            == normalize([(key, value, line) for key, value, line in after[ident]
                          if key not in ('available', 'bypass')]))
    for ident in before:
        if ident not in after:
            drift[ident] = 'removed'
    return drift


def code_outside(text, focus_ids):
    """Tokens of the whole file except the focus blocks under repair."""
    tokens = tokenize(text)
    kept = []
    index = 0
    while index < len(tokens):
        kind, value, line = tokens[index]
        if kind == 'word' and value == 'focus' and index + 2 < len(tokens) \
                and tokens[index + 1][0] == '=' and tokens[index + 2][0] == '{':
            end, block_id = block_span(tokens, index + 2), None
            for inner in range(index + 3, end):
                if tokens[inner][0] == 'word' and tokens[inner][1] == 'id' \
                        and inner + 2 < end and tokens[inner + 1][0] == '=' \
                        and tokens[inner + 2][1] in focus_ids:
                    block_id = tokens[inner + 2][1]
                    break
            if block_id is not None:
                index = end
                continue
        kept.append((kind, value))
        index += 1
    return kept


def block_span(tokens, opening_index):
    depth = 0
    index = opening_index
    while index < len(tokens):
        if tokens[index][0] == '{':
            depth += 1
        elif tokens[index][0] == '}':
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise Unsupported('unbalanced braces')


# ---------------------------------------------------------------------------------------------
# The audit itself
# ---------------------------------------------------------------------------------------------

def audit(text, coastal, state, old_state, kinds, category_slots):
    """Return the list of failures for one version of the focus file."""
    failures = []
    focuses = read_focus_blocks(text)

    def fail(message):
        failures.append(message)

    for focus_id in (NAVAL_FOCUS, DOCKYARD_FOCUS):
        if focus_id not in focuses:
            fail('%s is missing from the tree' % focus_id)
    if failures:
        return failures

    naval = constructions_of(focuses[NAVAL_FOCUS], NAVAL_FOCUS)
    dockyard = constructions_of(focuses[DOCKYARD_FOCUS], DOCKYARD_FOCUS)

    # --- naval base -------------------------------------------------------------------------
    if len(naval) != 1:
        fail('%s must build exactly one building, found %d' % (NAVAL_FOCUS, len(naval)))
    else:
        build = naval[0]
        spec = build['spec']
        if spec.get('type') != 'naval_base':
            fail('%s builds %r, expected naval_base' % (NAVAL_FOCUS, spec.get('type')))
        if build['state'] == OLD_STATE:
            fail('%s still builds in state %d, which has no coastal province'
                 % (NAVAL_FOCUS, OLD_STATE))
        if build['state'] != TARGET_STATE:
            fail('%s builds in state %d, expected %d' % (NAVAL_FOCUS, build['state'], TARGET_STATE))
        if spec.get('level') != '1' or spec.get('instant_build') != 'yes':
            fail('%s changed its level or instant_build: %r' % (NAVAL_FOCUS, spec))
        province = spec.get('province')
        if province is None:
            fail('%s gives no province selector; a naval base is a provincial building, so the '
                 'state scope alone does not place it' % NAVAL_FOCUS)
        elif province == 'filter':
            fail('%s uses a province filter; a coastal filter would add a full level to every '
                 'coastal province in the state and multiply the reward' % NAVAL_FOCUS)
        else:
            try:
                province = int(province)
            except ValueError:
                fail('%s province selector %r is not a province id' % (NAVAL_FOCUS, province))
            else:
                if province not in state['provinces']:
                    fail('naval base province %d is not in state %d (provinces %s)'
                         % (province, TARGET_STATE, state['provinces']))
                if not coastal.get(province, False):
                    fail('naval base province %d is not coastal in %s, so only_costal rejects it'
                         % (province, DEFINITION_PATH))

    # --- dockyard ---------------------------------------------------------------------------
    if len(dockyard) != 1:
        fail('%s must build exactly one building, found %d' % (DOCKYARD_FOCUS, len(dockyard)))
    else:
        build = dockyard[0]
        spec = build['spec']
        if spec.get('type') != 'dockyard':
            fail('%s builds %r, expected dockyard' % (DOCKYARD_FOCUS, spec.get('type')))
        if build['state'] == OLD_STATE:
            fail('%s still builds in state %d, which has no coastal province'
                 % (DOCKYARD_FOCUS, OLD_STATE))
        if build['state'] != TARGET_STATE:
            fail('%s builds in state %d, expected %d'
                 % (DOCKYARD_FOCUS, build['state'], TARGET_STATE))
        if spec.get('level') != '1' or spec.get('instant_build') != 'yes':
            fail('%s changed its level or instant_build: %r' % (DOCKYARD_FOCUS, spec))
        if 'province' in spec:
            fail('%s passes a province selector to a shared-slot state building' % DOCKYARD_FOCUS)

    # --- the building types ----------------------------------------------------------------
    if not kinds['naval_base']['only_coastal']:
        fail('naval_base is no longer coastal-only; this repair targets a coastal province')
    if not kinds['dockyard']['only_coastal']:
        fail('dockyard is no longer coastal-only')
    if not kinds['dockyard']['shares_slots']:
        fail('dockyard is no longer a shared-slot building; the slot budget check is stale')
    naval_province = naval[0]['spec'].get('province') if naval else None
    if naval_province not in (None, 'filter'):
        current = state['provincial_buildings'].get(int(naval_province), {}).get('naval_base', 0)
        wanted = current + 1
        province_max = kinds['naval_base']['province_max']
        if province_max is not None and wanted > province_max:
            fail('naval base at %s would reach level %d above province_max %d'
                 % (naval_province, wanted, province_max))

    # --- the target state -------------------------------------------------------------------
    coastal_in_state = [p for p in state['provinces'] if coastal.get(p, False)]
    if not coastal_in_state:
        fail('state %d has no coastal province, so it cannot host either building' % TARGET_STATE)
    if COASTAL_PORT not in coastal_in_state:
        fail('expected port %d is not a coastal province of state %d'
             % (COASTAL_PORT, TARGET_STATE))

    used_slots = 0
    for name, level in state['state_buildings'].items():
        info = kinds.get(name)
        if info and info['shares_slots']:
            used_slots += level
    if category_slots is None:
        pass  # reported as a coverage gap by main(), never as a pass
    elif used_slots + 1 > category_slots:
        fail('state %d has %d of %d shared slots used in %r, so the dockyard does not fit'
             % (TARGET_STATE, used_slots, category_slots, state['category']))

    # --- ownership --------------------------------------------------------------------------
    if state['owner'] != 'PER':
        fail('state %d starts owned by %r, so the reward would build for another country'
             % (TARGET_STATE, state['owner']))
    if old_state['owner'] != 'PER':
        fail('state %d starts owned by %r' % (OLD_STATE, old_state['owner']))

    # --- preserved rewards ------------------------------------------------------------------
    for focus_id, expected in PRESERVED_EFFECTS.items():
        rewards = reward_entries(focuses[focus_id])
        for key, expected_value in expected:
            if rewards.get(key) != expected_value:
                fail('%s completion_reward %s is %r, expected %r'
                     % (focus_id, key, rewards.get(key), expected_value))

    return failures


# ---------------------------------------------------------------------------------------------
# Localisation
# ---------------------------------------------------------------------------------------------

LOC_LINE = re.compile(r'^\s*(?P<key>[A-Za-z0-9_.-]+):(?P<version>\d*)\s+"(?P<value>.*)"\s*$')


def parse_localisation(text):
    """key -> (value, line, version), plus the file-level facts the check needs."""
    if text.startswith('\ufeff'):
        text = text[1:]
    parsed = {'first_line': None, 'entries': {}, 'duplicates': [], 'unparsed': []}
    for number, line in enumerate(text.split('\n'), 1):
        stripped = line.strip()
        if not stripped:
            continue
        if parsed['first_line'] is None:
            parsed['first_line'] = stripped
            if stripped.startswith('l_') and stripped.endswith(':'):
                continue
        if stripped.startswith('#'):
            continue
        match = LOC_LINE.match(line)
        if match is None:
            parsed['unparsed'].append((number, stripped[:80]))
            continue
        key = match.group('key')
        if key in parsed['entries']:
            parsed['duplicates'].append(key)
        parsed['entries'][key] = (match.group('value'), number, match.group('version'))
    return parsed


def audit_localisation(text, bom, state, other_state):
    """Failures for one version of the interwar localisation file."""
    failures = []
    parsed = parse_localisation(text)
    entries = parsed['entries']

    def fail(message):
        failures.append(message)

    if not bom:
        fail('%s is not UTF-8 with a BOM; the game rejects or mis-reads such a file' % LOC_PATH)
    if parsed['first_line'] != 'l_english:':
        fail('%s starts with %r, expected the l_english: header'
             % (LOC_PATH, parsed['first_line']))
    for number, line in parsed['unparsed']:
        fail('%s line %d is not a `key: "value"` entry: %r' % (LOC_PATH, number, line))
    for key in parsed['duplicates']:
        fail('%s defines %s more than once' % (LOC_PATH, key))

    # The false location is a map fact: province 7982, the vanilla "Bandar e'Abbas", belongs to
    # state 412 and must not belong to the state the dockyard is built in.
    if ABBAS_PROVINCE in state['provinces']:
        fail('%d is a province of state %d, so the wording and the reward would only agree by '
             'accident' % (ABBAS_PROVINCE, TARGET_STATE))
    if ABBAS_PROVINCE not in other_state['provinces']:
        fail('%d is no longer a province of state %d, so the false location this test uses has '
             'moved' % (ABBAS_PROVINCE, OTHER_STATE))
    expected_name = Path(STATE_PATH).stem.split('-', 1)[-1]
    if expected_name.lower() != TARGET_STATE_NAME.lower():
        fail('%s now reads %r, not %r; the expected name in this test is stale'
             % (STATE_PATH, expected_name, TARGET_STATE_NAME))

    if DESC_KEY not in entries:
        fail('%s has no %s' % (LOC_PATH, DESC_KEY))
        return failures

    value, number, version = entries[DESC_KEY]
    lowered = value.lower()

    if version:
        fail('%s:%d uses the version suffix `:%s`; this repository writes unversioned keys'
             % (DESC_KEY, number, version))
    for spelling in ABBAS_SPELLINGS:
        if spelling.lower() in lowered:
            fail('%s:%d names %r, which is province %d in state %d, not the state the dockyard '
                 'is built in' % (DESC_KEY, number, spelling, ABBAS_PROVINCE, OTHER_STATE))
            break
    if TARGET_STATE_NAME.lower() not in lowered:
        fail('%s:%d does not name %s, the state the reward builds the dockyard in'
             % (DESC_KEY, number, TARGET_STATE_NAME))
    for term in DESC_REQUIRED_TERMS:
        if term not in lowered:
            fail('%s:%d no longer mentions %r, so the text no longer describes the reward'
                 % (DESC_KEY, number, term))
    for marker in ('\u00a7', '\u00a3'):
        if marker in value:
            fail('%s:%d contains the raw script marker %r' % (DESC_KEY, number, marker))

    return failures


def localisation_diff(current_entries, baseline_entries):
    """Keys whose value differs from the pinned baseline, the repaired description aside."""
    changed = []
    for key, (value, _number, _version) in current_entries.items():
        if key == DESC_KEY:
            continue
        if key not in baseline_entries:
            changed.append((key, 'added'))
        elif baseline_entries[key][0] != value:
            changed.append((key, 'changed'))
    for key in baseline_entries:
        if key != DESC_KEY and key not in current_entries:
            changed.append((key, 'removed'))
    return changed


# ---------------------------------------------------------------------------------------------
# Baseline and reporting
# ---------------------------------------------------------------------------------------------

def baseline_raw(path):
    """The pinned pre-repair bytes of one file, read from git rather than from the worktree."""
    result = subprocess.run(
        ['git', 'show', '%s:%s' % (BASELINE_REV, path)],
        cwd=str(ROOT), capture_output=True,
    )
    if result.returncode != 0:
        print('cannot read the pinned baseline %s:%s' % (BASELINE_REV, path))
        print(result.stderr.decode('utf-8', 'replace').strip())
        print('the mutant control needs the repository history; this is not a pass')
        sys.exit(2)
    return result.stdout


def baseline_file(path):
    return baseline_raw(path).decode('utf-8-sig')


def preservation_raw(path):
    """The pinned integration bytes of one file, read from git rather than from the worktree."""
    result = subprocess.run(
        ['git', 'show', '%s:%s' % (PRESERVATION_REV, path)],
        cwd=str(ROOT), capture_output=True,
    )
    if result.returncode != 0:
        print('cannot read the preservation baseline %s:%s' % (PRESERVATION_REV, path))
        print(result.stderr.decode('utf-8', 'replace').strip())
        print('the preservation check needs the repository history; this is not a pass')
        sys.exit(2)
    return result.stdout


def preservation_file(path):
    return preservation_raw(path).decode('utf-8-sig')


def preservation_text():
    return preservation_file(FOCUS_PATH)


def baseline_text():
    return baseline_file(FOCUS_PATH)



class Report:
    def __init__(self, detail=False):
        self.detail = detail
        self.checks = []
        self.failures = []
        self.notes = []
        self.group = ''

    def start(self, group):
        self.group = group

    def note(self, text):
        self.notes.append(text)
        print('  note  %s' % text)

    def check(self, label, condition, detail=''):
        self.checks.append(label)
        if not condition:
            self.failures.append('%s: %s%s' % (self.group, label,
                                               (' — ' + detail) if detail else ''))
        elif self.detail:
            print('  ok  [%s] %s%s' % (self.group, label, (' — ' + detail) if detail else ''))

    def summary(self):
        print('%d checks, %d failures' % (len(self.checks), len(self.failures)))
        for failure in self.failures:
            print('  FAIL ' + failure)
        return not self.failures


def main():
    report = Report(detail='--detail' in sys.argv)
    text = read_repo(FOCUS_PATH)
    coastal = read_coastal_provinces()
    state = read_state(STATE_PATH)
    old_state = read_state(OLD_STATE_PATH)
    other_state = read_state(OTHER_STATE_PATH)
    kinds = read_building_kinds()
    slots, slots_source = read_category_slots(state['category'])

    if '--dump' in sys.argv:
        focuses = read_focus_blocks(text)
        for focus_id in (NAVAL_FOCUS, DOCKYARD_FOCUS):
            print(focus_id)
            for build in constructions_of(focuses[focus_id], focus_id):
                print('   line %d state %d %r' % (build['line'], build['state'], build['spec']))
        print('state %d: %s %s owner %s provinces %s'
              % (state['id'], state['category'], state['path'], state['owner'],
                 state['provinces']))
        print('coastal provinces of state %d: %s'
              % (TARGET_STATE, [p for p in state['provinces'] if coastal.get(p, False)]))
        print('shared slots: %r from %s' % (slots, slots_source))
        print('%s: %r' % (DESC_KEY, parse_localisation(read_repo(LOC_PATH))['entries']
                          .get(DESC_KEY, ('<missing>', 0, ''))[0]))
        return 0

    report.start('map')
    report.check('state 413 exists with %d provinces' % len(state['provinces']),
                 len(state['provinces']) > 0)
    report.check('state 413 owns at least one coastal province',
                 any(coastal.get(p, False) for p in state['provinces']),
                 str([p for p in state['provinces'] if coastal.get(p, False)]))
    report.check('state 411 is the landlocked state the rewards left',
                 not any(coastal.get(p, False) for p in old_state['provinces']),
                 str(old_state['provinces']))
    report.check('the port province %d is coastal' % COASTAL_PORT, coastal.get(COASTAL_PORT, False))
    report.check('the fallback coastal province %d is coastal' % COASTAL_SLOP,
                 coastal.get(COASTAL_SLOP, False))
    report.check('the removed location %d, Bandar e\'Abbas, is a province of state %d'
                 % (ABBAS_PROVINCE, OTHER_STATE),
                 ABBAS_PROVINCE in other_state['provinces'], str(other_state['provinces']))
    report.check('the removed location %d is not a province of state %d'
                 % (ABBAS_PROVINCE, TARGET_STATE),
                 ABBAS_PROVINCE not in state['provinces'])
    if slots is None:
        report.note('state category %r slots could not be read from the mod or the installed '
                    'game; the dockyard slot budget is recorded as unverified'
                    % state['category'])
    else:
        report.check('state 413 uses the %r category with %d shared slots'
                     % (state['category'], slots), slots > 0, slots_source or '')

    report.start('rewards')
    failures = audit(text, coastal, state, old_state, kinds, slots)
    for failure in failures:
        report.check(failure, False)
    report.check('both rewards parse and land on a coastal state', not failures,
                 '; '.join(failures))

    report.start('baseline-drift')
    drift = focus_drift()
    report.check('the two baseline pins differ in exactly the %d declared focuses'
                 % len(ACCEPTED_DRIFT_FOCUSES),
                 sorted(drift) == sorted(ACCEPTED_DRIFT_FOCUSES), repr(sorted(drift)))
    report.check('every declared baseline focus differs only inside a requirement block',
                 all(drift.get(ident) is True for ident in ACCEPTED_DRIFT_FOCUSES),
                 repr({ident: drift.get(ident) for ident in ACCEPTED_DRIFT_FOCUSES}))
    before_loc = parse_localisation(baseline_file(LOC_PATH))['entries']
    after_loc = parse_localisation(preservation_file(LOC_PATH))['entries']
    added_keys = sorted(key for key in after_loc if key not in before_loc)
    removed_keys = sorted(key for key in before_loc if key not in after_loc)
    changed_values = sorted(key for key in after_loc
                            if key in before_loc and after_loc[key][0] != before_loc[key][0])
    report.check('the two baseline pins add exactly the %d declared localisation keys'
                 % len(ACCEPTED_DRIFT_LOC_KEYS),
                 added_keys == sorted(ACCEPTED_DRIFT_LOC_KEYS), repr(added_keys))
    report.check('the integration baseline removed no localisation key', not removed_keys,
                 repr(removed_keys))
    report.check('the integration baseline changed only the repaired description value',
                 changed_values == [DESC_KEY], repr(changed_values))

    report.start('preserved')
    focuses = read_focus_blocks(text)
    kept_focuses = read_focus_blocks(preservation_text())
    problems = preservation_failures(focuses, kept_focuses, text, preservation_text())
    for problem in problems:
        report.check(problem, False)
    report.check('every field outside the two repaired blocks and the declared edit is unchanged',
                 not problems, '; '.join(problems))

    report.start('non-blessing')
    declared = dict(kept_focuses)
    for focus_id in ACCEPTED_FOCUS_EDITS:
        edited = apply_accepted_edit(focus_id, kept_focuses[focus_id])
        if edited is None:
            declared = None
            break
        declared[focus_id] = edited
    report.check('the declared edit is accepted in the shape it is written',
                 declared is not None and not preservation_failures(declared, kept_focuses),
                 'the declared edit does not pass the preservation check')

    def widened(body, extra):
        out = []
        for key, value, line in body:
            if key == 'completion_reward' and value[0] == 'block':
                out.append((key, ('block', list(value[1]) + [extra]), line))
            else:
                out.append((key, value, line))
        return out

    unrelated = next((ident for ident in sorted(kept_focuses)
                      if ident not in ({NAVAL_FOCUS, DOCKYARD_FOCUS} | set(ACCEPTED_FOCUS_EDITS))
                      and reward_entries(kept_focuses[ident])), None)
    mutated = dict(kept_focuses)
    if unrelated is not None:
        mutated[unrelated] = widened(mutated[unrelated],
                                     ('add_political_power', ('scalar', '25'), 0))
    failures = preservation_failures(mutated, kept_focuses)
    report.check('a changed reward on an undeclared focus is rejected',
                 unrelated is not None and any(unrelated in failure for failure in failures),
                 'picked %r; failures %r' % (unrelated, failures))

    widened_edits = dict(kept_focuses)
    for focus_id in ACCEPTED_FOCUS_EDITS:
        edited = apply_accepted_edit(focus_id, kept_focuses[focus_id])
        if edited is not None:
            widened_edits[focus_id] = widened(edited,
                                              ('add_war_support', ('scalar', '0.05'), 0))
    failures = preservation_failures(widened_edits, kept_focuses)
    report.check('the declared edit widened by one extra effect is rejected',
                 bool(failures) and all(any(ident in failure for failure in failures)
                                        for ident in ACCEPTED_FOCUS_EDITS),
                 repr(failures))

    report.start('mutant')
    old_failures = audit(baseline_text(), coastal, state, old_state, kinds, slots)
    report.check('the pre-repair source fails the check', bool(old_failures))
    report.check('the pre-repair source is rejected for state 411',
                 any('state 411' in failure for failure in old_failures),
                 '; '.join(old_failures))
    report.check('the pre-repair source is rejected for the missing province selector',
                 any('province selector' in failure for failure in old_failures),
                 '; '.join(old_failures))

    report.start('localisation')
    loc_raw = (ROOT / LOC_PATH).read_bytes()
    loc_text = loc_raw.decode('utf-8-sig')
    loc_failures = audit_localisation(loc_text, loc_raw.startswith(b'\xef\xbb\xbf'),
                                      state, other_state)
    for failure in loc_failures:
        report.check(failure, False)
    report.check('the focus description matches the repaired build', not loc_failures,
                 '; '.join(loc_failures))
    loc = parse_localisation(loc_text)
    kept_loc = parse_localisation(preservation_file(LOC_PATH))
    report.check('the description is the only localisation value that changed',
                 not localisation_diff(loc['entries'], kept_loc['entries']),
                 repr(localisation_diff(loc['entries'], kept_loc['entries'])))
    report.check('localisation key count unchanged',
                 len(loc['entries']) == len(kept_loc['entries']),
                 '%d vs %d' % (len(loc['entries']), len(kept_loc['entries'])))
    report.check('the description names the state the reward builds in',
                 TARGET_STATE_NAME.lower() in loc['entries'][DESC_KEY][0].lower(),
                 loc['entries'][DESC_KEY][0])
    report.note('only localisation/english has an Iran interwar file; the other seven project '
                'languages have none, recorded rather than invented')

    report.start('loc-mutant')
    old_loc_raw = baseline_raw(LOC_PATH)
    old_loc_failures = audit_localisation(old_loc_raw.decode('utf-8-sig'),
                                          old_loc_raw.startswith(b'\xef\xbb\xbf'),
                                          state, other_state)
    report.check('the pre-repair description fails the check', bool(old_loc_failures))
    report.check('the pre-repair description is rejected for the port it named',
                 any('Bandar' in failure for failure in old_loc_failures),
                 '; '.join(old_loc_failures))

    return 0 if report.summary() else 1


if __name__ == '__main__':
    sys.exit(main())
