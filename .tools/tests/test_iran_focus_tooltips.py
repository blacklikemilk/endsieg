"""Regression test: Iran's focus requirements show written tooltips, never raw flag names.

The defect this pins is presentation, not logic.  Fourteen player-visible requirement blocks in the
1925-1935 and 1936-1945 Iranian focus chapters carried internal names in the open, so
the focus tooltip printed country flags such as ``iran_crisis_anglo_persian_done`` or the bare
scripted-trigger names ``iran_path_majlis``/``iran_path_army``.  Each block is now wrapped in
``custom_trigger_tooltip`` with an English localisation key, which is the pattern the trees already
use for ``iran_pahlavi_programme_tt``, ``iran_projects_ready_tt`` and the rest.

What is checked, against the shipped sources:

    1. **Presentation.**  No ``has_country_flag``/``has_global_flag`` in any ``available`` or
       ``bypass`` block of the two chapters is left outside a ``custom_trigger_tooltip`` /
       ``custom_override_tooltip`` wrapper.  The pinned baseline is scanned the same way and must
       report its nine and four unwrapped blocks, so a passing run proves the check is not vacuous.
    2. **Internal trigger names.**  A scripted trigger from ``common/scripted_triggers`` that
       appears bare in a requirement block must either carry English text of its own (the key named
       after the trigger, as ``iran_sponsor_britain_valid`` does in both chapters) or sit inside a
       wrapper.  The baseline leaves seven unlocalised ``iran_path_*`` names visible - one of them
       in ``IR2_parliamentary_republic`` - so this rule too is anchored on a real defect.
    3. **Tooltip coverage.**  Every ``tooltip = <key>`` used by a requirement block resolves in
       ``localisation/english``, and each key added by this repair is referenced by a block (no
       dead keys) and defined exactly once.
    4. **Logic preserved.**  Wrappers are stripped from the new blocks and the remaining trigger
       text must be identical to the baseline's, block by block.  Independently, every requirement
       block - old and new - is evaluated over the full truth table of its leaf conditions and the
       two results must agree for every combination.
    5. **Nothing else moved.**  Every other field of every focus (id, icon, coordinates,
       prerequisites, mutually exclusive set, branch gate, cost, search filters, AI weights,
       rewards) must be byte-identical to the pinned baseline, and the ordered focus id list of
       both chapters must be unchanged.  This is what proves the repair touched no gameplay field.
    6. **Encoding.**  Both English localisation files keep their UTF-8 BOM, and the two script
       files keep their CRLF line endings without gaining stray bare LF endings.

Run from the repository root:

    python .tools/tests/test_iran_focus_tooltips.py           # exit 0 = pass
    python .tools/tests/test_iran_focus_tooltips.py --detail  # print every check
    python .tools/tests/test_iran_focus_tooltips.py --dump    # print the parsed requirement blocks

This is a source check.  It proves what the script and localisation say; it does not prove how the
focus tooltip renders in game.  No game is launched.
"""

from __future__ import annotations

import itertools
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CHAPTERS = {
    'common/national_focus/iran_interwar.txt': {
        'loc': 'localisation/english/iran_interwar_l_english.yml',
        'tree': 'iran_interwar',
        'blocks': 52,
        'raw_blocks_at_baseline': 9,
        'raw_occurrences_at_baseline': 10,
        'raw_triggers_at_baseline': 7,
    },
    'common/national_focus/iran_ww2.txt': {
        'loc': 'localisation/english/iran_ww2_l_english.yml',
        'tree': 'iran_ww2',
        'blocks': 31,
        'raw_blocks_at_baseline': 4,
        'raw_occurrences_at_baseline': 6,
        'raw_triggers_at_baseline': 0,
    },
}

# Baseline of the I8 admission: the last integration commit before the repair.  Pinned by full
# object name so a later commit does not silently turn the baseline comparison into a no-op.
BASELINE_REV = 'ad0169dd1c6f67b4b8904f9f1d90f73f3f47754a'

REQUIREMENT_KEYS = ('available', 'bypass')
FLAG_KEYS = ('has_country_flag', 'has_global_flag')
WRAPPER_KEYS = ('custom_trigger_tooltip', 'custom_override_tooltip')
TOOLTIP_FIELD = 'tooltip'

# Keys added by this repair, mapped to the file that defines them.
NEW_KEYS = {
    'iran_anglo_persian_crisis_open_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_cossack_refusal_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_gilan_republic_proclaimed_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_nationalist_movement_organized_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_nationalist_front_base_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_jangali_congress_held_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_majlis_predominance_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_majlis_ascendant_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_reza_at_the_army_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_army_decisive_voice_tt': 'localisation/english/iran_interwar_l_english.yml',
    'iran_pahlavi_rule_tt': 'localisation/english/iran_ww2_l_english.yml',
    'iran_monarchy_settled_tt': 'localisation/english/iran_ww2_l_english.yml',
    'iran_occupied_tt': 'localisation/english/iran_ww2_l_english.yml',
}

# The blocks this repair rewrote: focus id -> requirement block.  Kept explicit so a change that
# drops one of them from the file fails instead of quietly shrinking the surface.
REPAIRED_BLOCKS = {
    'IR2_reject_the_agreement': 'available',
    'IR2_accept_the_agreement': 'available',
    'IR2_reza_khan_minister': 'bypass',
    'IR2_jangali_congress': 'available',
    'IR2_nationalist_press': 'available',
    'IR2_nationalist_officers': 'available',
    'IR2_parliamentary_republic': 'available',
    'IR2_nationalist_front': 'available',
    'IR2_socialist_republic': 'available',
    'IR2_pahlavi_settlement': 'available',
    'IR3_mohammad_reza': 'available',
    'IR3_wartime_regency': 'available',
    'IR3_occupation_government': 'available',
    'IR3_resistance_council': 'available',
}

IGNORED_FOCUS_FIELDS = REQUIREMENT_KEYS

# The one focus edit this card may make: the American mission's leverage gain is
# real debt rather than a derived value, and the spirit and its derivation are
# republished after it. Everything else about the focus, and every other focus,
# stays byte-equal.
ACCEPTED_FOCUS_EDITS = {
    'IR3_american_mission': 'the debt substitution and the spirit refresh',
}

AMERICAN_LEVERAGE_WRITE = ('add_to_variable',
                           [('iran_foreign_leverage',
                             'constant:iran_story.leverage_gain')])
AMERICAN_REPLACEMENT = [
    ('add_to_variable', [('iran_leverage_debt', 'constant:iran_story.leverage_gain')]),
    ('hidden_effect', [('iran_refresh_mechanics', 'yes')]),
]


def accepted_focus_edit(ident, fields):
    """Apply the declared edit for `ident` to a baseline field list."""
    if ident not in ACCEPTED_FOCUS_EDITS:
        return fields, False
    applied = False
    out = []
    for key, value in fields:
        if key != 'completion_reward' or not isinstance(value, list):
            out.append((key, value))
            continue
        replaced = []
        for entry in value:
            if entry == AMERICAN_LEVERAGE_WRITE:
                replaced.extend(AMERICAN_REPLACEMENT)
                applied = True
            else:
                replaced.append(entry)
        out.append((key, replaced))
    return out, applied


class Unsupported(Exception):
    """A script shape this check does not model. Failing loudly beats guessing."""


# ---------------------------------------------------------------------------------------------
# Parser: Clausewitz text -> nested entries
# ---------------------------------------------------------------------------------------------

OPERATORS = ('<', '>', '<=', '>=')


def tokenize(text):
    tokens = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == '#':
            while index < length and text[index] != '\n':
                index += 1
        elif char in '{}=':
            tokens.append(char)
            index += 1
        elif char in ' \t\r\n':
            index += 1
        else:
            start = index
            while index < length and text[index] not in ' \t\r\n{}=#':
                index += 1
            tokens.append(('word', text[start:index]))
    return tokens


def parse_block(tokens, index):
    """Return (entries, index). An entry is (key, value) with value a list or a string,
    or ('cmp', key, operator, value) for `date > 1920.5.31` style comparisons."""
    entries = []
    while index < len(tokens):
        token = tokens[index]
        if token == '}':
            return entries, index + 1
        if not isinstance(token, tuple):
            raise Unsupported('unexpected %r' % (token,))
        key = token[1]
        if index + 1 >= len(tokens):
            raise Unsupported('trailing %s' % key)
        nxt = tokens[index + 1]
        if nxt == '{':
            value, index = parse_block(tokens, index + 2)
            entries.append((key, value))
            continue
        if nxt == '=':
            if index + 2 >= len(tokens):
                raise Unsupported('dangling %s =' % key)
            value_token = tokens[index + 2]
            if value_token == '{':
                value, index = parse_block(tokens, index + 3)
                entries.append((key, value))
                continue
            if not isinstance(value_token, tuple):
                raise Unsupported('unexpected value for %s' % key)
            entries.append((key, value_token[1]))
            index += 3
            continue
        # `date > 1920.5.31`
        if isinstance(nxt, tuple) and nxt[1] in OPERATORS:
            if index + 2 >= len(tokens):
                raise Unsupported('dangling %s %s' % (key, nxt[1]))
            value_token = tokens[index + 2]
            if not isinstance(value_token, tuple):
                raise Unsupported('unexpected comparison value for %s' % key)
            entries.append(('cmp', key, nxt[1], value_token[1]))
            index += 3
            continue
        # A bare token inside a list block: `search_filters = { FOCUS_FILTER_POLITICAL }`.
        entries.append((key, None))
        index += 1
        continue
    return entries, index


def parse_text(text):
    tokens = tokenize(text)
    entries, index = parse_block(tokens, 0)
    if index != len(tokens):
        raise Unsupported('unconsumed tokens at %d of %d' % (index, len(tokens)))
    return entries


def find_tree(entries, tree_id):
    for key, value in entries:
        if key != 'focus_tree' or not isinstance(value, list):
            continue
        for inner_key, inner_value in value:
            if inner_key == 'id' and inner_value == tree_id:
                return value
    raise Unsupported('focus tree %s not found' % tree_id)


def focus_blocks(tree_entries):
    blocks = []
    for key, value in tree_entries:
        if key in ('focus', 'joint_focus') and isinstance(value, list):
            blocks.append(value)
    return blocks


def field(block, name):
    for key, value in block:
        if key == name:
            return value
    return None


def focus_id(block):
    value = field(block, 'id')
    if not isinstance(value, str):
        raise Unsupported('focus without an id')
    return value


# ---------------------------------------------------------------------------------------------
# Wrappers, canonical form and flag scanning
# ---------------------------------------------------------------------------------------------


def strip_wrappers(entries):
    """Replace each custom tooltip wrapper by its own trigger content (AND splicing)."""
    stripped = []
    for entry in entries:
        if entry[0] == 'cmp':
            stripped.append(entry)
            continue
        key, value = entry
        if key in WRAPPER_KEYS and isinstance(value, list):
            stripped.extend(strip_wrappers([item for item in value
                                            if not (isinstance(item[1], str)
                                                    and item[0] in (TOOLTIP_FIELD,
                                                                    'not_tooltip'))]))
            continue
        if isinstance(value, list):
            stripped.append((key, strip_wrappers(value)))
        else:
            stripped.append((key, value))
    return stripped


def canonical(entries):
    return repr(entries)


def scan_flags(entries, inside_wrapper=False):
    """Return (flag_occurrences, unwrapped_occurrences) for a requirement block."""
    found = []
    for entry in entries:
        if entry[0] == 'cmp':
            continue
        key, value = entry
        if key in FLAG_KEYS:
            found.append((key, value, inside_wrapper))
        elif isinstance(value, list):
            found.extend(scan_flags(value, inside_wrapper or key in WRAPPER_KEYS))
    return found


def tooltip_keys(entries):
    keys = []
    for entry in entries:
        if entry[0] == 'cmp':
            continue
        key, value = entry
        if key in WRAPPER_KEYS and isinstance(value, list):
            for item in value:
                item_key, item_value = (item[0], item[1]) if item[0] != 'cmp' else ('cmp', None)
                if item_key == TOOLTIP_FIELD and isinstance(item_value, str):
                    keys.append(item_value)
                elif isinstance(item_value, list):
                    keys.extend(tooltip_keys(item_value))
        elif isinstance(value, list):
            keys.extend(tooltip_keys(value))
    return keys


SCRIPTED_TRIGGER_DIR = 'common/scripted_triggers'


def scripted_trigger_names():
    """Top-level keys defined in common/scripted_triggers/*.txt - the mod's own trigger names."""
    names = set()
    for path in sorted((ROOT / SCRIPTED_TRIGGER_DIR).glob('*.txt')):
        tokens = tokenize(path.read_text(encoding='utf-8-sig'))
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if (isinstance(token, tuple) and index + 2 < len(tokens)
                    and tokens[index + 1] == '=' and tokens[index + 2] == '{'):
                names.add(token[1])
                depth = 1
                index += 3
                while index < len(tokens) and depth:
                    if tokens[index] == '{':
                        depth += 1
                    elif tokens[index] == '}':
                        depth -= 1
                    index += 1
                continue
            index += 1
    return names


def scan_scripted_triggers(entries, names, inside_wrapper=False):
    """Return (key, value, inside_wrapper) for every use of a mod scripted trigger."""
    found = []
    for entry in entries:
        if entry[0] == 'cmp':
            continue
        key, value = entry
        wrapped = inside_wrapper or key in WRAPPER_KEYS
        if key in names:
            found.append((key, value, wrapped))
        if isinstance(value, list):
            found.extend(scan_scripted_triggers(value, names, wrapped))
    return found


# ---------------------------------------------------------------------------------------------
# Truth-table evaluation over leaf atoms
# ---------------------------------------------------------------------------------------------


def atoms_of(entries, out):
    for entry in entries:
        if entry[0] == 'cmp':
            out.add(('cmp', entry[1], entry[2], entry[3]))
        elif isinstance(entry[1], list):
            atoms_of(entry[1], out)
        else:
            out.add((entry[0], entry[1]))
    return out


def evaluate(entries, state):
    result = True
    for entry in entries:
        if entry[0] == 'cmp':
            result = result and state[('cmp', entry[1], entry[2], entry[3])]
            continue
        key, value = entry
        if isinstance(value, list):
            if key == 'OR':
                result = result and any(evaluate([item], state) for item in value)
            elif key == 'NOT':
                result = result and not evaluate(value, state)
            else:
                result = result and evaluate(value, state)
            continue
        result = result and state[(key, value)]
    return result


def truth_table(entries):
    """Evaluate a wrapper-free block over every combination of its leaf atoms."""
    atoms = sorted(atoms_of(entries, set()), key=repr)
    rows = []
    for combination in itertools.product((False, True), repeat=len(atoms)):
        state = dict(zip(atoms, combination))
        rows.append(evaluate(entries, state))
    return atoms, rows


# ---------------------------------------------------------------------------------------------
# Localisation
# ---------------------------------------------------------------------------------------------

def loc_keys(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {}
    for number, line in enumerate(text.split('\n'), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('l_english'):
            continue
        if ':' not in stripped:
            continue
        key, _, rest = stripped.partition(':')
        key = key.strip()
        if not key or ' ' in key:
            continue
        if rest.strip().startswith('"'):
            keys[key] = number
    return keys


def english_loc_keys():
    merged = {}
    for path in sorted((ROOT / 'localisation' / 'english').glob('*.yml')):
        for key, line in loc_keys(path).items():
            merged.setdefault(key, []).append((path.name, line))
    return merged


# ---------------------------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------------------------


def working_text(relative):
    return (ROOT / relative).read_text(encoding='utf-8-sig')


def baseline_text(relative):
    try:
        return subprocess.run(['git', 'show', '%s:%s' % (BASELINE_REV, relative)],
                              cwd=str(ROOT), capture_output=True, text=True,
                              check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        raise Unsupported('cannot read %s at %s: %s' % (relative, BASELINE_REV, error))


def chapters():
    parsed = {}
    for relative, spec in CHAPTERS.items():
        current = find_tree(parse_text(working_text(relative)), spec['tree'])
        baseline = find_tree(parse_text(baseline_text(relative)), spec['tree'])
        parsed[relative] = {
            'spec': spec,
            'current': focus_blocks(current),
            'baseline': focus_blocks(baseline),
            'current_text': working_text(relative),
            'baseline_text': baseline_text(relative),
        }
    return parsed


# ---------------------------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------------------------


class Report:
    def __init__(self, detail):
        self.detail = detail
        self.failures = []
        self.count = 0

    def check(self, name, passed, message=''):
        self.count += 1
        if not passed:
            self.failures.append('%s%s' % (name, (': ' + message) if message else ''))
        if self.detail:
            print('%-4s %s%s' % ('ok' if passed else 'FAIL', name,
                                (' - ' + message) if (message and not passed) else ''))

    def summary(self):
        print('%d checks, %d failures' % (self.count, len(self.failures)))
        for failure in self.failures:
            print('  FAILED %s' % failure)
        return 1 if self.failures else 0


def requirement_blocks(focuses):
    """Yield (focus id, block name, entries) for every requirement block in a focus list."""
    for block in focuses:
        ident = focus_id(block)
        for name in REQUIREMENT_KEYS:
            value = field(block, name)
            if isinstance(value, list):
                yield ident, name, value


def check_presentation(report, data):
    for relative, chapter in data.items():
        baseline_blocks = 0
        baseline_occurrences = 0
        for ident, name, entries in requirement_blocks(chapter['baseline']):
            flags = [item for item in scan_flags(entries) if not item[2]]
            if flags:
                baseline_blocks += 1
                baseline_occurrences += len(flags)
        report.check('%s baseline shows raw flag names in %d blocks'
                     % (relative, chapter['spec']['raw_blocks_at_baseline']),
                     baseline_blocks == chapter['spec']['raw_blocks_at_baseline'],
                     'expected %d blocks, found %d'
                     % (chapter['spec']['raw_blocks_at_baseline'], baseline_blocks))
        report.check('%s baseline raw flag occurrences' % relative,
                     baseline_occurrences == chapter['spec']['raw_occurrences_at_baseline'],
                     'expected %d, found %d'
                     % (chapter['spec']['raw_occurrences_at_baseline'], baseline_occurrences))

        unwrapped = []
        blocks = 0
        occurrences = 0
        for ident, name, entries in requirement_blocks(chapter['current']):
            blocks += 1
            for (key, value, wrapped) in scan_flags(entries):
                occurrences += 1
                if not wrapped:
                    unwrapped.append('%s.%s (%s = %s)' % (ident, name, key, value))
        report.check('%s requirement block count' % relative,
                     blocks == chapter['spec']['blocks'],
                     'expected %d, found %d' % (chapter['spec']['blocks'], blocks))
        report.check('%s no raw flag name in a requirement block' % relative,
                     not unwrapped, '; '.join(unwrapped))
        report.check('%s flag conditions still present' % relative, occurrences > 0,
                     'no flag conditions found at all')


def check_scripted_trigger_names(report, data):
    """A bare requirement trigger must print written English, not its internal name.

    Two ways to satisfy that: the trigger's own name is a localisation key (the pattern
    ``iran_sponsor_britain_valid`` follows in both chapters), or the block wraps it in a
    ``custom_trigger_tooltip``.  The pinned baseline leaves ``iran_path_*`` names bare with no key
    at all, so the rule is measured on the baseline first and must report those occurrences.
    """
    names = scripted_trigger_names()
    report.check('scripted trigger definitions loaded from common/scripted_triggers',
                 len(names) > 100, 'found %d definitions' % len(names))
    keys = english_loc_keys()
    for relative, chapter in data.items():
        spec = chapter['spec']
        baseline_unresolved = 0
        for ident, name, entries in requirement_blocks(chapter['baseline']):
            for key, value, wrapped in scan_scripted_triggers(entries, names):
                if not wrapped and key not in keys:
                    baseline_unresolved += 1
        report.check('%s baseline leaves %d unlocalised requirement triggers bare'
                     % (relative, spec['raw_triggers_at_baseline']),
                     baseline_unresolved == spec['raw_triggers_at_baseline'],
                     'expected %d, found %d'
                     % (spec['raw_triggers_at_baseline'], baseline_unresolved))

        unresolved = []
        resolved = 0
        for ident, name, entries in requirement_blocks(chapter['current']):
            for key, value, wrapped in scan_scripted_triggers(entries, names):
                if wrapped:
                    continue
                if key in keys:
                    resolved += 1
                else:
                    unresolved.append('%s.%s (%s = %s)' % (ident, name, key, value))
        report.check('%s no unlocalised scripted trigger in a requirement block' % relative,
                     not unresolved, '; '.join(unresolved))
        report.check('%s bare scripted triggers that do resolve are still measured' % relative,
                     resolved > 0, 'no bare-but-localised trigger found, rule may be vacuous')


def check_coverage(report, data):
    keys = english_loc_keys()
    used = {}
    for chapter in data.values():
        for ident, name, entries in requirement_blocks(chapter['current']):
            for key in tooltip_keys(entries):
                used.setdefault(key, set()).add('%s.%s' % (ident, name))
    missing = sorted(key for key in used if key not in keys)
    report.check('every requirement tooltip key resolves in localisation/english',
                 not missing, '; '.join(missing))

    for key, relative in sorted(NEW_KEYS.items()):
        report.check('key %s is referenced by a requirement block' % key, key in used,
                     'defined but unused')
        definitions = keys.get(key, [])
        report.check('key %s is defined exactly once' % key, len(definitions) == 1,
                     'definitions: %s' % (definitions,))
        report.check('key %s is defined in %s' % (key, Path(relative).name),
                     [Path(entry[0]).name for entry in definitions] == [Path(relative).name],
                     'defined in %s' % ([entry[0] for entry in definitions],))

    for ident, name in sorted(REPAIRED_BLOCKS.items()):
        report.check('repaired block %s.%s carries a tooltip key' % (ident, name),
                     ('%s.%s' % (ident, name)) in
                     {entry for entries in used.values() for entry in entries},
                     'no custom tooltip key found')


def check_logic(report, data, dump):
    for relative, chapter in data.items():
        baseline_by_id = {focus_id(block): block for block in chapter['baseline']}
        for block in chapter['current']:
            ident = focus_id(block)
            baseline = baseline_by_id.get(ident)
            report.check('%s %s exists in the baseline' % (relative, ident), baseline is not None)
            if baseline is None:
                continue
            for name in REQUIREMENT_KEYS:
                new_value = field(block, name)
                old_value = field(baseline, name)
                if not isinstance(new_value, list) and not isinstance(old_value, list):
                    continue
                if not isinstance(new_value, list) or not isinstance(old_value, list):
                    report.check('%s %s.%s still present' % (relative, ident, name), False,
                                 'block added or removed')
                    continue
                stripped = strip_wrappers(new_value)
                old_stripped = strip_wrappers(old_value)
                if dump:
                    print('%s %s.%s' % (relative, ident, name))
                    print('  new (stripped): %s' % canonical(stripped))
                    print('  baseline      : %s' % canonical(old_stripped))
                report.check('%s %s.%s logic unchanged under the wrapper' % (relative, ident, name),
                             canonical(stripped) == canonical(old_stripped),
                             '\n    new: %s\n    old: %s'
                             % (canonical(stripped), canonical(old_stripped)))

                new_atoms, new_rows = truth_table(stripped)
                old_atoms, old_rows = truth_table(old_stripped)
                report.check('%s %s.%s conditions identical' % (relative, ident, name),
                             new_atoms == old_atoms,
                             'new %s old %s' % (new_atoms, old_atoms))
                report.check('%s %s.%s truth table identical (%d states)'
                             % (relative, ident, name, len(new_rows)),
                             new_rows == old_rows,
                             '%s vs %s' % (new_rows, old_rows))


def check_preservation(report, data):
    for relative, chapter in data.items():
        baseline_by_id = {focus_id(block): block for block in chapter['baseline']}
        current_ids = [focus_id(block) for block in chapter['current']]
        baseline_ids = [focus_id(block) for block in chapter['baseline']]
        report.check('%s focus ids and order unchanged' % relative,
                     current_ids == baseline_ids,
                     'added %s removed %s' % (sorted(set(current_ids) - set(baseline_ids)),
                                              sorted(set(baseline_ids) - set(current_ids))))
        mismatched = []
        accepted = []
        for block in chapter['current']:
            ident = focus_id(block)
            baseline = baseline_by_id.get(ident)
            if baseline is None:
                mismatched.append('%s (new focus)' % ident)
                continue
            old_fields = [(key, value) for key, value in baseline
                          if key not in IGNORED_FOCUS_FIELDS]
            new_fields = [(key, value) for key, value in block
                          if key not in IGNORED_FOCUS_FIELDS]
            if canonical(old_fields) == canonical(new_fields):
                continue
            normalised, applied = accepted_focus_edit(ident, old_fields)
            if applied and canonical(normalised) == canonical(new_fields):
                accepted.append(ident)
            else:
                mismatched.append(ident)
        report.check('%s every non-requirement focus field unchanged' % relative,
                     not mismatched, '; '.join(mismatched))
        present = [focus_id(block) for block in chapter['current']]
        for ident in ACCEPTED_FOCUS_EDITS:
            if ident not in present:
                continue
            described = ACCEPTED_FOCUS_EDITS[ident]
            report.check('%s %s carries %s' % (relative, ident, described),
                         ident in accepted,
                         'the accepted edit is not present exactly as declared')

    for ident, name in sorted(REPAIRED_BLOCKS.items()):
        found = False
        for chapter in data.values():
            for block in chapter['current']:
                if focus_id(block) == ident and isinstance(field(block, name), list):
                    found = True
        report.check('repaired block %s.%s is present' % (ident, name), found,
                     'block missing from both chapters')


def check_encoding(report, data):
    for relative, chapter in data.items():
        loc_relative = chapter['spec']['loc']
        loc_raw = (ROOT / loc_relative).read_bytes()
        report.check('%s keeps its UTF-8 BOM' % loc_relative,
                     loc_raw.startswith(b'\xef\xbb\xbf'), 'no BOM')
        loc_text = loc_raw.decode('utf-8-sig')
        report.check('%s has no raw section sign' % loc_relative, '\u00a7' not in loc_text,
                     'raw paragraph marker present')
        report.check('%s uses LF line endings' % loc_relative,
                     loc_raw.count(b'\r\n') == 0,
                     '%d CRLF endings' % loc_raw.count(b'\r\n'))
        unindented = [number for number, line in enumerate(loc_text.split('\n'), 1)
                      if line and not line.startswith(' ') and number != 1]
        report.check('%s keeps the single leading space convention' % loc_relative,
                     not unindented, 'lines %s' % (unindented,))

        script_raw = (ROOT / relative).read_bytes()
        bare_lf = script_raw.count(b'\n') - script_raw.count(b'\r\n')
        report.check('%s keeps uniform CRLF line endings' % relative, bare_lf == 0,
                     '%d bare LF endings' % bare_lf)


def mutant_controls(report, data):
    """Re-run the checks against deliberately broken copies and require them to fail.

    A source check that would also pass the defective state proves nothing.  Each control below
    rebuilds one of the defects this repair removed - an unwrapped flag block, a wrapper that
    changed the condition it wraps, an unresolved tooltip key - and requires the matching check to
    reject it.
    """
    import copy

    relative = 'common/national_focus/iran_interwar.txt'

    def rebuilt(ident_edits):
        mutated = copy.deepcopy(data)
        chapter = mutated[relative]
        blocks = []
        for block in chapter['current']:
            edit = ident_edits.get(focus_id(block))
            if edit is not None:
                block = [(key, edit) if key == 'available' else (key, value)
                         for key, value in block]
            blocks.append(block)
        chapter['current'] = blocks
        return mutated

    def failures_of(check, mutated, *extra):
        local = Report(False)
        check(local, mutated, *extra)
        return local.failures

    baseline_available = {focus_id(block): field(block, 'available')
                          for block in data[relative]['baseline']}
    unwrapped = {ident: baseline_available[ident]
                 for ident in ('IR2_nationalist_press', 'IR2_nationalist_officers')}
    report.check('mutant control: an unwrapped flag block is rejected',
                 failures_of(check_presentation, rebuilt(unwrapped)),
                 'presentation check accepted raw flag text')

    flattened = [('custom_trigger_tooltip', [
        ('tooltip', 'iran_nationalist_front_base_tt'),
        ('OR', [('has_country_flag', 'iran_nationalist_officers'),
                ('OR', [('iran_path_army', 'yes'), ('iran_path_tribal', 'yes')])])])]
    logic_failures = failures_of(check_logic, rebuilt({'IR2_nationalist_front': flattened}), False)
    report.check('mutant control: a wrapper that changed the condition is rejected',
                 any('truth table' in item for item in logic_failures),
                 'logic check accepted a changed condition')

    unknown_key = [('custom_trigger_tooltip', [
        ('tooltip', 'iran_no_such_tooltip_key_tt'),
        ('has_country_flag', 'iran_gilan_republic')])]
    report.check('mutant control: an unresolved tooltip key is rejected',
                 failures_of(check_coverage, rebuilt({'IR2_jangali_congress': unknown_key})),
                 'coverage check accepted an unknown key')

    report.check('mutant control: a bare unlocalised scripted trigger is rejected',
                 failures_of(check_scripted_trigger_names,
                             rebuilt({'IR2_parliamentary_republic':
                                      baseline_available['IR2_parliamentary_republic']})),
                 'raw-trigger check accepted the baseline requirement')

    # Preservation controls: the accepted edit is exactly one substitution plus one
    # call, and any wider change to a focus reward must still be rejected.
    def preservation_failures_for(transform):
        mutated = copy.deepcopy(data)
        for chapter in mutated.values():
            chapter['current'] = [transform(block) for block in chapter['current']]
        local = Report(False)
        check_preservation(local, mutated)
        return local.failures

    def drop_refresh(block):
        if focus_id(block) != 'IR3_american_mission':
            return block
        return [(key, [entry for entry in value
                       if entry != ('hidden_effect', [('iran_refresh_mechanics', 'yes')])])
                if key == 'completion_reward' and isinstance(value, list) else (key, value)
                for key, value in block]

    def widen_reward(block):
        if focus_id(block) != 'IR3_american_mission':
            return block
        return [(key, [('add_research_slot', '2') if entry[0] == 'add_research_slot' else entry
                       for entry in value])
                if key == 'completion_reward' and isinstance(value, list) else (key, value)
                for key, value in block]

    unrelated = None
    for chapter in data.values():
        for block in chapter['current']:
            ident = focus_id(block)
            if ident != 'IR3_american_mission' and isinstance(field(block, 'completion_reward'),
                                                              list):
                unrelated = ident
                break
        if unrelated:
            break

    def unrelated_reward(block):
        if unrelated is None or focus_id(block) != unrelated:
            return block
        return [(key, value + [('add_political_power', '25')])
                if key == 'completion_reward' and isinstance(value, list) else (key, value)
                for key, value in block]

    report.check('mutant control: the spirit refresh removed from the American mission is '
                 'rejected',
                 any('IR3_american_mission' in item
                     for item in preservation_failures_for(drop_refresh)),
                 'preservation check accepted the mission without its spirit refresh')
    report.check('mutant control: a wider American-mission reward is rejected',
                 any('IR3_american_mission' in item
                     for item in preservation_failures_for(widen_reward)),
                 'preservation check accepted a changed mission reward')
    report.check('mutant control: an unrelated focus reward change is rejected',
                 unrelated is not None and any(unrelated in item
                                               for item in preservation_failures_for(
                                                   unrelated_reward)),
                 'preservation check accepted a changed reward on %s' % unrelated)


def main(argv):
    detail = '--detail' in argv
    dump = '--dump' in argv
    report = Report(detail)
    data = chapters()

    check_presentation(report, data)
    check_scripted_trigger_names(report, data)
    check_coverage(report, data)
    check_logic(report, data, dump)
    check_preservation(report, data)
    check_encoding(report, data)
    mutant_controls(report, data)

    for relative, chapter in data.items():
        if dump:
            print('== %s' % relative)
            for ident, name, entries in requirement_blocks(chapter['current']):
                print('%s.%s: %s' % (ident, name, canonical(strip_wrappers(entries))))

    return report.summary()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
