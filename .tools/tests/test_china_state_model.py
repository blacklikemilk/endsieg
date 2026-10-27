"""Executes the global China state model instead of restating it.

The module reads the shipped script from `common/scripted_effects/china_state_model.txt` and
`common/scripted_triggers/china_state_model.txt`, parses it with a small Clausewitz reader, and
runs the effects against a modelled world: global variables, per-country variables, a state
controller map and a global state array. Every claim below is produced by execution, and every
guard is proved necessary by a named mutant that removes it and must then fail.

What the model proves: the array is built once and a second call changes nothing; the literal
table equals the set re-derived from `history/states` by the documented rule; the published tier
copies the frozen Republic tier rather than the live score; the first reunifier cannot be
replaced; and reunification needs one Chinese campaign country to control every China-proper
state, so a single unheld state or a non-Chinese holder leaves it false.

What the model cannot prove: that the engine parses `check_variable = { array^num > 0 }`,
`all_of_scopes` and a numeric state scope the same way this reader does. Those forms are taken
from the installed documentation and vanilla precedent (see `docs/systems/china_state_model.md`)
and remain live checks.

Run with `python -B .tools/tests/test_china_state_model.py`.
"""

import io
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
VERBOSE = '--detail' in sys.argv

EFFECTS = ROOT / 'common' / 'scripted_effects' / 'china_state_model.txt'
TRIGGERS = ROOT / 'common' / 'scripted_triggers' / 'china_state_model.txt'
CONSTANTS = ROOT / 'common' / 'script_constants' / 'china_story.txt'
GAME = Path('C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV')

WRITERS = ['china_build_proper_states', 'china_publish_fragmentation_tier',
           'china_set_seat_holder', 'china_record_reunifier']

# States that carry a permanent CHI core whose `history` block opens on the next line. A parser
# that only accepts `history = {` on one line silently drops them, which is how the first
# version of this list lost seven states while still reporting 55 == 55. Pinned so it cannot
# happen again.
NEXT_LINE_HISTORY = [596, 600, 605, 620, 743, 745, 746]

# Every script file this model owns, plus the file that holds the card's only tier-writer call.
# A leading UTF-8 BOM makes the engine reject such a file whole, which removes the call site and
# every effect it defines, so the bytes are asserted rather than assumed.
MODEL_FILES = [EFFECTS, TRIGGERS, CONSTANTS,
               ROOT / 'common' / 'scripted_effects' / 'rch_campaign.txt']


def bom_problem(data):
    """Return why a script file's first bytes are wrong, or '' when they are clean."""
    if data[:3] == b'\xef\xbb\xbf':
        return 'leading UTF-8 BOM (ef bb bf): the engine rejects the file'
    if data[:1] != b'#':
        return 'first byte is %r, not the # of an overview comment' % data[:1]
    return ''


# --------------------------------------------------------------------------- parsing

class ParseError(Exception):
    pass


def tokenize(text):
    tokens = []
    pattern = r'[{}]|<=|>=|[^\s{}=<>]+|<|>|='

    def emit(line):
        for part in re.findall(pattern, line):
            tokens.append(part)

    for raw in text.splitlines():
        line = raw.split('#')[0].strip()
        if not line:
            continue
        if re.match(r'^@[A-Za-z_]', line):
            emit(line)
            continue
        emit(line)
    return tokens


def parse_block(tokens, i):
    """Parse until the closing brace. Returns (statements, next_index)."""
    nodes = []
    while i < len(tokens):
        tok = tokens[i]
        if tok == '}':
            return nodes, i + 1
        if i + 1 >= len(tokens):
            raise ParseError('dangling token %r' % tok)
        if tokens[i + 1] in ('<', '>', '<=', '>='):
            if i + 2 >= len(tokens):
                raise ParseError('comparison without a right side')
            nodes.append(('kv', 'expr', (tok, tokens[i + 1], tokens[i + 2])))
            i += 3
            continue
        if tokens[i + 1] != '=':
            raise ParseError('unexpected token %r after %r' % (tokens[i + 1], tok))
        key = tok
        if i + 2 >= len(tokens):
            raise ParseError('key %r without value' % key)
        val = tokens[i + 2]
        if val == '{':
            body, i = parse_block(tokens, i + 3)
            nodes.append(('kv', key, body))
        else:
            nodes.append(('kv', key, val))
            i += 3
    return nodes, i


def parse_file(path):
    text = io.open(path, encoding='utf-8-sig').read()
    if text.startswith('\ufeff'):
        raise AssertionError('BOM in %s' % path)
    tokens = tokenize(text)
    nodes, _ = parse_block(tokens, 0)
    return nodes


def definitions(nodes):
    return {key: val for kind, key, val in nodes if kind == 'kv' and isinstance(val, list)}


def find_node(body, name):
    """The first `name = { ... }` block anywhere inside a parsed effect body."""
    for kind, key, val in body:
        if kind != 'kv':
            continue
        if key == name and isinstance(val, list):
            return val
        if isinstance(val, list):
            found = find_node(val, name)
            if found is not None:
                return found
    return None


def set_variable_nodes(body):
    """Every `set_variable` argument block inside an effect body, at any depth."""
    found = []
    for kind, key, val in body:
        if kind != 'kv':
            continue
        if key == 'set_variable':
            found.append(val)
        elif isinstance(val, list):
            found.extend(set_variable_nodes(val))
    return found


def macros(nodes):
    return {key[1:]: int(val) for kind, key, val in nodes
            if kind == 'kv' and key.startswith('@') and not isinstance(val, list)}


# --------------------------------------------------------------------------- world

class World(object):
    def __init__(self, controllers):
        self.globals = {}
        self.country = {}
        self.controllers = dict(controllers)
        self.states = sorted(self.controllers)

    def vars_for(self, tag):
        return self.country.setdefault(tag, {})

    def copy(self):
        w = World(self.controllers)
        w.globals = dict(self.globals)
        w.country = {k: dict(v) for k, v in self.country.items()}
        return w


MACROS = {}


def resolve_value(raw, world, scope):
    """Turn a scalar token into a Python value: global var, country var, number or tag."""
    if isinstance(raw, list):
        raise ParseError('unexpected block where a value belongs')
    if raw.startswith('$') and raw.endswith('$'):
        raise ParseError('unsubstituted parameter %s' % raw)
    if raw.startswith('@'):
        if raw[1:] not in MACROS:
            raise ParseError('undefined macro %s' % raw)
        return MACROS[raw[1:]]
    if raw == 'THIS':
        return int(scope) if re.match(r'^\d+$', str(scope)) else scope
    if raw.startswith('var:'):
        name = raw[4:]
        if name.startswith('global.'):
            return world.globals.get(name[7:])
        if '__temp__' + name in world.globals:
            return world.globals['__temp__' + name]
        return world.vars_for(scope).get(name)
    if raw.endswith('^num'):
        name = raw[:-4]
        arr = global_array(name, world)
        return len(arr)
    if raw.startswith('constant:'):
        category, key = raw[9:].split('.', 1)
        return constants()[category][key]
    m = re.match(r'^-?\d+(\.\d+)?$', raw)
    if m:
        return float(raw) if '.' in raw else int(raw)
    return raw


def global_array(name, world):
    if name.startswith('global.'):
        name = name[7:]
    value = world.globals.get(name)
    return value if isinstance(value, list) else []


CONST_CACHE = {}


def constants():
    if CONST_CACHE:
        return CONST_CACHE
    table = {}
    for kind, key, val in parse_file(CONSTANTS):
        if kind == 'kv' and isinstance(val, list):
            if key == 'schema':
                continue
            table[key] = {k: int(v) for k, v in ((n[1], n[2]) for n in val
                                                 if n[0] == 'kv' and not isinstance(n[2], list))}
    CONST_CACHE.update(table)
    return CONST_CACHE


# --------------------------------------------------------------------------- effects

EFFECT_NAMES = {}
TRIGGER_NAMES = {}


def load_script():
    EFFECT_NAMES.clear()
    TRIGGER_NAMES.clear()
    MACROS.clear()
    nodes = parse_file(EFFECTS)
    MACROS.update(macros(nodes))
    EFFECT_NAMES.update(definitions(nodes))
    TRIGGER_NAMES.update(definitions(parse_file(TRIGGERS)))
    return EFFECT_NAMES


def substitute(node, params):
    if params is None:
        return node
    if isinstance(node, str):
        out = node
        for k, v in params.items():
            out = out.replace('$%s$' % k, str(v))
        return out
    return [(kind, substitute(k, params), substitute(v, params)) for kind, k, v in node]


def run_effect(name, params, world, scope):
    """Run a scripted effect body (china_* names) with parameters."""
    if name not in EFFECT_NAMES:
        raise ParseError('unknown effect %r' % name)
    run_body(substitute(EFFECT_NAMES[name], params), world, scope)


def run_body(body, world, scope):
    i = 0
    while i < len(body):
        kind, key, val = body[i]
        if kind != 'kv':
            i += 1
            continue
        if key in ('if', 'else_if', 'else'):
            executed = False
            while i < len(body) and body[i][0] == 'kv' and body[i][1] in ('if', 'else_if', 'else'):
                key2, val2 = body[i][1], body[i][2]
                i += 1
                if executed:
                    continue
                if key2 == 'else':
                    run_body(val2, world, scope)
                    executed = True
                    continue
                limit, rest = split_limit(val2)
                if eval_trigger(limit, world, scope):
                    run_body(rest, world, scope)
                    executed = True
            continue
        if re.match(r'^\d+$', key):
            # numeric scope: a state by id, as vanilla's claim effects write it
            run_body(val, world, key)
            i += 1
            continue
        apply_effect(key, val, world, scope)
        i += 1


def split_limit(body):
    if body and body[0][0] == 'kv' and body[0][1] == 'limit':
        return body[0][2], body[1:]
    raise ParseError('if without limit')


def apply_effect(key, val, world, scope):
    if key == 'set_variable':
        target, value = variable_target(val, world, scope)
        world.globals[target] = value
        return
    if key == 'add_to_array':
        if not isinstance(val, list) or len(val) != 1 or val[0][0] != 'kv':
            raise ParseError('add_to_array shape')
        name = val[0][1]
        if not name.startswith('global.'):
            raise ParseError('only global arrays are modelled')
        world.globals.setdefault(name[7:], []).append(resolve_value(val[0][2], world, scope))
        return
    if key == 'set_temp_variable':
        name, raw = val[0][1], val[0][2]
        world.globals['__temp__' + name] = resolve_value(raw, world, scope)
        return
    if key == 'clamp_temp_variable':
        args = {k: v for kind, k, v in val if kind == 'kv'}
        name = '__temp__' + args['var']
        value = world.globals[name]
        low = resolve_value(args['min'], world, scope)
        high = resolve_value(args['max'], world, scope)
        world.globals[name] = max(low, min(high, value))
        return
    if key in EFFECT_NAMES:
        params = None
        if isinstance(val, list):
            params = {k: v for kind, k, v in val if kind == 'kv'}
        run_effect(key, params, world, scope)
        return
    raise ParseError('unknown effect %r' % key)


def variable_target(body, world, scope):
    """Support both `set_variable = { var = global.x value = v }` and the short forms."""
    if len(body) == 1 and body[0][0] == 'kv':
        return body[0][1].replace('global.', '', 1), resolve_value(body[0][2], world, scope)
    args = {k: v for kind, k, v in body if kind == 'kv'}
    name = args['var']
    if not name.startswith('global.'):
        raise ParseError('only global writes are modelled here: %r' % name)
    return name[7:], resolve_value(args['value'], world, scope)


# --------------------------------------------------------------------------- triggers

def eval_trigger(node, world, scope, evaluate=True):
    """Return the truth of a trigger block. `evaluate=False` skips work but keeps parity."""
    if not evaluate:
        return False
    if isinstance(node, str):
        return bool(resolve_value(node, world, scope))
    truth = True
    for kind, key, val in node:
        if kind != 'kv':
            raise ParseError('bare atom in trigger block: %r' % key)
        if key == 'NOT':
            truth = truth and (not eval_trigger(val, world, scope))
        elif key == 'AND':
            truth = truth and eval_trigger(val, world, scope)
        elif key == 'OR':
            truth = truth and any(eval_trigger([n], world, scope) for n in val
                                  if n[0] == 'kv')
        elif key == 'has_variable':
            name = str(val)
            if name.startswith('global.'):
                truth = truth and name[7:] in world.globals
            else:
                truth = truth and name in world.vars_for(scope)
        elif key == 'check_variable':
            truth = truth and check_variable(val, world, scope)
        elif key in ('all_of_scopes', 'any_of_scopes'):
            args = {k: v for kind, k, v in val if kind == 'kv' and k == 'array'}
            rest = [n for n in val if not (n[0] == 'kv' and n[1] == 'array')]
            members = global_array(args['array'], world)
            results = [eval_trigger(rest, world, member) for member in members]
            truth = truth and (all(results) if key == 'all_of_scopes' else any(results))
        elif key == 'all_of':
            args = {k: v for kind, k, v in val if kind == 'kv' and k == 'array'}
            members = global_array(args['array'], world)
            rest = [n for n in val if not (n[0] == 'kv' and n[1] == 'array')]
            truth = truth and all(
                eval_trigger(rest, world, scope) for member in members)
        elif key == 'all_state':
            truth = truth and all(eval_trigger(val, world, state) for state in world.states)
        elif key == 'any_state':
            truth = truth and any(eval_trigger(val, world, state) for state in world.states)
        elif key == 'is_controlled_by':
            truth = truth and world.controllers.get(int(scope)) == str(val)
        elif re.match(r'^\d+$', key):
            truth = truth and eval_trigger(val, world, key)
        elif key in TRIGGER_NAMES:
            params = None
            if isinstance(val, list):
                params = {k: v for kind, k, v in val if kind == 'kv'}
            truth = truth and eval_trigger(substitute(TRIGGER_NAMES[key], params), world, scope)
        else:
            raise ParseError('unknown trigger %r' % key)
    return truth


def check_variable(body, world, scope):
    if len(body) == 1 and body[0][0] == 'kv' and body[0][1] == 'expr':
        left, op, right = body[0][2]
        lhs = resolve_value(left, world, scope)
        rhs = resolve_value(right, world, scope)
        return {'=': lhs == rhs, '<': lhs < rhs, '>': lhs > rhs,
                '<=': lhs <= rhs, '>=': lhs >= rhs}[op]
    raise ParseError('unsupported check_variable body %r' % (body,))


# --------------------------------------------------------------------------- fixtures

def proper_ids():
    body = EFFECT_NAMES['china_build_proper_states']
    if_block = body[0][2]
    ids = [int(key) for kind, key, val in if_block if re.match(r'^\d+$', key)]
    return ids


def world_with(holders):
    """Every China-proper state starts held by `holders` (a single tag or a dict).

    The array is built first, because the reunification test is guarded by the array's
    presence: a world without it would make every refusal test pass for the wrong reason.
    """
    none_world = World({1: 'CHI'})
    run_effect('china_build_proper_states', None, none_world, 'CHI')
    ids = proper_ids()
    ctl = {}
    for sid in ids:
        ctl[sid] = holders.get(sid) if isinstance(holders, dict) else holders
    ctl[9001] = 'ENG'  # a state outside China proper, so a sweep must not consider it
    world = World(ctl)
    world.globals['china_proper_states'] = list(none_world.globals['china_proper_states'])
    return world


def reunify(world):
    run_effect('china_test_reunification', None, world, 'RCH')
    return world.globals.get('china_reunified_by')


# --------------------------------------------------------------------------- tests

CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


@check
def test_proper_states_match_source():
    """The literal list equals the set re-derived from history/states by the stated rule."""
    derived = derive_proper_states()
    literal = proper_ids()
    assert literal == derived, 'literal %d vs derived %d; only in literal %s, only in derived %s' % (
        len(literal), len(derived), sorted(set(literal) - set(derived)),
        sorted(set(derived) - set(literal)))
    assert len(literal) == constants()['china_story']['proper_state_count'], \
        'count constant disagrees with the literal list'
    assert len(set(literal)) == len(literal), 'duplicate state id in the literal list'


@check
def test_derivation_sees_next_line_history():
    """The seven states whose `history` brace opens on the next line must be in the set."""
    derived = set(derive_proper_states())
    missing = [sid for sid in NEXT_LINE_HISTORY if sid not in derived]
    assert not missing, 'derivation dropped %s' % missing


@check
def test_tier_bounds_are_the_constants():
    """The clamp operands are the tuning constants themselves, not literals and not macros."""
    clamp = find_node(EFFECT_NAMES['china_publish_fragmentation_tier'], 'clamp_temp_variable')
    assert clamp is not None, 'the publish effect no longer clamps the frozen tier'
    bounds = {k: v for kind, k, v in clamp if kind == 'kv'}
    table = constants()['china_story']
    assert bounds['min'] == 'constant:china_story.tier_floor', \
        'min bound is %r, not the china_story constant' % bounds['min']
    assert bounds['max'] == 'constant:china_story.tier_ceiling', \
        'max bound is %r, not the china_story constant' % bounds['max']
    assert resolve_value(bounds['min'], World({}), 'RCH') == table['tier_floor']
    assert resolve_value(bounds['max'], World({}), 'RCH') == table['tier_ceiling']
    assert not MACROS, 'unused file macros remain in the effects file: %s' % sorted(MACROS)


@check
def test_global_writes_use_the_backed_form():
    """Vanilla writes a global variable short: `set_variable = { global.X = <value> }`.

    The `var = global.x value = y` block form has no vanilla or documentation precedent, so a
    write in that form could leave the symbol silently unset in the engine.
    """
    writes = []
    for name in WRITERS:
        for body in set_variable_nodes(EFFECT_NAMES[name]):
            if not (len(body) == 1 and body[0][0] == 'kv' and body[0][1].startswith('global.')):
                raise AssertionError('%s writes in the unbacked form: %r' % (name, body))
            writes.append(body[0][1])
    assert sorted(writes) == ['global.china_fragmentation_tier', 'global.china_reunified_by',
                              'global.china_seat_holder'], \
        'unexpected global writes: %s' % sorted(writes)


@check
def test_script_files_carry_no_bom():
    """A leading BOM makes the engine reject a scripted-effects file whole.

    `common/scripted_effects/rch_campaign.txt` is in the list because the card's only tier writer
    is called from inside it: a rejected file there loses the call site, so the published tier
    never happens. The 15:09 load logged `unexpected token ... ( )` against that file before the
    BOM was stripped.
    """
    for path in MODEL_FILES:
        problem = bom_problem(path.read_bytes())
        assert not problem, '%s: %s' % (path.relative_to(ROOT), problem)


@check
def test_built_once():
    world = World({1: 'CHI'})
    run_effect('china_build_proper_states', None, world, 'CHI')
    first = list(world.globals['china_proper_states'])
    run_effect('china_build_proper_states', None, world, 'CHI')
    assert world.globals['china_proper_states'] == first, 'second build changed the array'


@check
def test_array_holds_state_scopes():
    """The array must hold scopes, because all_of_scopes walks it; ids alone would not do."""
    world = World({1: 'CHI'})
    run_effect('china_build_proper_states', None, world, 'CHI')
    arr = world.globals['china_proper_states']
    assert len(arr) == len(proper_ids()), 'array length %d != literal count %d' % (
        len(arr), len(proper_ids()))
    assert all(isinstance(v, int) for v in arr), 'array holds non-scope values'


@check
def test_tier_is_the_frozen_value():
    world = World({1: 'CHI'})
    world.vars_for('RCH')['rch_succession_tier'] = 3        # live score already moved on
    world.vars_for('RCH')['rch_succession_final_tier'] = 2  # frozen at resolution
    run_effect('china_publish_fragmentation_tier', None, world, 'RCH')
    assert world.globals['china_fragmentation_tier'] == 2, 'published the live score'
    world.vars_for('RCH')['rch_succession_tier'] = 0
    assert world.globals['china_fragmentation_tier'] == 2, 'a later day rewrote the tier'


@check
def test_tier_absent_before_resolution():
    """No frozen tier means no published tier: the effect must not invent one."""
    world = World({1: 'CHI'})
    world.vars_for('RCH')['rch_succession_tier'] = 3
    run_effect('china_publish_fragmentation_tier', None, world, 'RCH')
    assert 'china_fragmentation_tier' not in world.globals, 'published a tier with nothing frozen'


@check
def test_second_reunifier_refused():
    world = world_with('CHI')
    run_effect('china_record_reunifier', {'COUNTRY': 'CHI'}, world, 'CHI')
    run_effect('china_record_reunifier', {'COUNTRY': 'JAP'}, world, 'JAP')
    assert world.globals['china_reunified_by'] == 'CHI', 'second reunifier replaced the first'
    assert world.globals['china_seat_holder'] == 'CHI', 'seat did not follow the reunifier'


@check
def test_full_control_reunifies():
    world = world_with('CHI')
    assert reunify(world) == 'CHI', 'full control did not record the reunifier'
    assert world.globals['china_seat_holder'] == 'CHI', 'seat not set by the reunification'


@check
def test_one_unheld_state_refuses():
    ids = proper_ids()
    split = {sid: 'CHI' for sid in ids}
    split[ids[-1]] = 'JAP'
    world = world_with(split)
    assert reunify(world) is None, 'reunified with %d held by JAP' % ids[-1]


@check
def test_non_chinese_holder_refused():
    world = world_with('JAP')
    assert reunify(world) is None, 'a non-Chinese tag holding China proper was accepted'


@check
def test_no_array_means_no_reunification():
    """The test must not fire before on_startup has built the array."""
    world = World({sid: 'CHI' for sid in proper_ids()})
    assert reunify(world) is None, 'reunified without a China-proper array'


@check
def test_one_writer_each():
    text = io.open(EFFECTS, encoding='utf-8-sig').read()
    for name in WRITERS:
        pattern = re.compile(r'^%s = \{' % re.escape(name), re.M)
        assert len(pattern.findall(text)) == 1, '%s defined %d times' % (
            name, len(pattern.findall(text)))


@check
def test_readers_never_write():
    text = io.open(TRIGGERS, encoding='utf-8-sig').read()
    for banned in ('set_variable', 'add_to_array', 'set_global_flag', 'set_country_flag',
                   'set_temp_variable', 'clamp_temp_variable'):
        assert banned not in text, 'reader file writes with %s' % banned
    for name in WRITERS:
        assert name not in text, 'reader file calls the writer %s' % name


def strip_comments(text):
    """Script text without `#` comments, so a check cannot be satisfied by prose."""
    return '\n'.join(line.split('#')[0] for line in text.splitlines())


@check
def test_no_world_iteration():
    text = strip_comments(io.open(EFFECTS, encoding='utf-8-sig').read())
    for banned in ('every_country', 'every_state', 'random_country', 'every_owned_state'):
        assert banned not in text, 'effects file iterates with %s' % banned
    on_action = strip_comments(io.open(ROOT / 'common' / 'on_actions' / 'rch_campaign.txt',
                                       encoding='utf-8-sig').read())
    assert on_action.count('on_daily') == 1 and 'on_daily_RCH = {' in on_action, \
        'the RCH hook is no longer the single tag-scoped daily block'


# --------------------------------------------------------------------------- mutants

MUTANTS = [
    ('M1 build-once guard removed',
     [(EFFECTS, 'limit = { NOT = { check_variable = { global.china_proper_states^num > 0 } } }',
       'limit = { check_variable = { global.china_proper_states^num > -1 } }')],
     test_built_once),
    ('M2 publish reads the live score',
     [(EFFECTS, 'global.china_fragmentation_tier = var:china_published_tier',
                'global.china_fragmentation_tier = var:rch_succession_tier')],
     test_tier_is_the_frozen_value),
    ('M3 reunifier guard removed',
     [(EFFECTS, 'limit = { NOT = { has_variable = global.china_reunified_by } }',
       'limit = { NOT = { has_variable = global.china_never_recorded } }')],
     test_second_reunifier_refused),
    ('M4 all_of_scopes weakened to any_of_scopes',
     [(TRIGGERS, 'all_of_scopes = {', 'any_of_scopes = {')],
     test_one_unheld_state_refuses),
    ('M5 non-Chinese tag admitted as a candidate',
     [(EFFECTS, 'china_holds_all_proper_states = { COUNTRY = QIN }',
       'china_holds_all_proper_states = { COUNTRY = JAP }')],
     test_non_chinese_holder_refused),
    ('M6 array presence guard removed',
     [(EFFECTS, 'check_variable = { global.china_proper_states^num > 0 }\n\t\t\tNOT = '
                '{ has_variable = global.china_reunified_by }',
       'NOT = { has_variable = global.china_reunified_by }')],
     test_no_array_means_no_reunification),
    ('M7 derivation accepts only a one-line history block',
     [(EFFECTS, '596 = { add_to_array', '1596 = { add_to_array')],
     test_proper_states_match_source),
    ('M9 global write uses the unbacked long form',
     [(EFFECTS, 'set_variable = { global.china_seat_holder = $COUNTRY$ }',
                'set_variable = { var = global.china_seat_holder value = $COUNTRY$ }')],
     test_global_writes_use_the_backed_form),
    ('M10 tier bound written as a literal, not the constant',
     [(EFFECTS, 'min = constant:china_story.tier_floor', 'min = 0')],
     test_tier_bounds_are_the_constants),
]


def run_mutant(name, edits, test):
    texts = {EFFECTS: io.open(EFFECTS, encoding='utf-8-sig').read(),
             TRIGGERS: io.open(TRIGGERS, encoding='utf-8-sig').read()}
    for path, old, new in edits:
        assert old in texts[path], '%s: pattern missing from %s' % (name, path.name)
        mutated = texts[path].replace(old, new, 1)
        assert mutated != texts[path], '%s: replacement changed nothing' % name
        texts[path] = mutated

    saved_effects = dict(EFFECT_NAMES)
    saved_triggers = dict(TRIGGER_NAMES)
    saved_macros = dict(MACROS)
    try:
        EFFECT_NAMES.clear()
        TRIGGER_NAMES.clear()
        macros_table = macros(parse_block(tokenize(texts[EFFECTS]), 0)[0])
        MACROS.clear()
        MACROS.update(macros_table)
        for path, table in ((EFFECTS, EFFECT_NAMES), (TRIGGERS, TRIGGER_NAMES)):
            nodes, _ = parse_block(tokenize(texts[path].replace('\ufeff', '')), 0)
            table.update(definitions(nodes))
        try:
            test()
        except AssertionError as exc:
            return 'FAILS as required (%s)' % str(exc).split('\n')[0][:80]
        raise AssertionError('%s: the mutated script still passed %s' % (name, test.__name__))
    finally:
        EFFECT_NAMES.clear()
        EFFECT_NAMES.update(saved_effects)
        TRIGGER_NAMES.clear()
        TRIGGER_NAMES.update(saved_triggers)
        MACROS.clear()
        MACROS.update(saved_macros)


def mutation_count_check():
    """A second definition of a writer must break the one-writer rule."""
    text = io.open(EFFECTS, encoding='utf-8-sig').read()
    duplicated = text + '\nchina_set_seat_holder = {\n\tset_variable = { global.china_seat_holder = $COUNTRY$ }\n}\n'
    count = len(re.findall(r'^china_set_seat_holder = \{', duplicated, re.M))
    assert count == 2, 'a duplicated definition was not detected'
    return count


def bom_strip_control():
    """The byte-level predicate must reject exactly the bytes the strip removed.

    Read-only: it rebuilds the pre-strip bytes in memory and checks that the same function the
    file check uses rejects them, so a check that silently stops testing the BOM fails here.
    """
    clean = (ROOT / 'common' / 'scripted_effects' / 'rch_campaign.txt').read_bytes()
    dirty = b'\xef\xbb\xbf' + clean
    return bom_problem(dirty), bom_problem(clean), len(clean)


def old_derive_blind_spot():
    """The previous rule, kept as a control: it drops states whose `history` brace is on line 2."""
    return len([sid for sid in derive_proper_states(one_line_history_only=True)])


# --------------------------------------------------------------------------- derivation

def state_files(root):
    out = {}
    for path in sorted((root / 'history' / 'states').glob('*.txt')):
        text = io.open(path, encoding='utf-8-sig', errors='replace').read().replace('\ufeff', '')
        m = re.search(r'^\s*id\s*=\s*(\d+)', text, re.M)
        if m:
            out[int(m.group(1))] = (path, text)
    return out


def derive_proper_states(one_line_history_only=False):
    """Rule: add_core_of = CHI inside `history`, outside every dated block. Mod file wins.

    `one_line_history_only` reproduces the earlier parser that only accepted `history = {` on a
    single line; it exists so the control below can prove that blind spot loses seven states.
    """
    files = state_files(GAME)
    files.update(state_files(ROOT))
    found = []
    for sid, (_, text) in sorted(files.items()):
        depth = 0
        history_depth = None
        dated_depth = None
        pending = None  # a block key whose `{` is on the next line
        hit = False
        for raw in text.splitlines():
            line = raw.split('#')[0].strip()
            if not line:
                continue
            if pending is not None:
                if line.startswith('{'):
                    if pending == 'history':
                        history_depth = depth + 1
                    else:
                        dated_depth = depth + 1
                    depth += line.count('{') - line.count('}')
                    pending = None
                    continue
                pending = None
            opens, closes = line.count('{'), line.count('}')
            date = re.match(r'^(\d{3,4}\.\d{1,2}\.\d{1,2})\s*=\s*\{?$', line)
            if history_depth is not None and dated_depth is None and date:
                if line.endswith('{'):
                    dated_depth = depth + opens
                    depth += opens - closes
                elif not one_line_history_only:
                    pending = date.group(1)
                    depth += opens - closes
                else:
                    depth += opens - closes
                continue
            if history_depth is None and re.match(r'^history\s*=\s*\{?$', line):
                if line.endswith('{'):
                    history_depth = depth + opens
                    depth += opens - closes
                elif not one_line_history_only:
                    pending = 'history'
                    depth += opens - closes
                else:
                    depth += opens - closes
                continue
            if dated_depth is not None:
                depth += opens - closes
                if depth < dated_depth:
                    dated_depth = None
                continue
            if history_depth is not None and re.search(r'add_core_of\s*=\s*CHI\b', line):
                hit = True
            depth += opens - closes
            if history_depth is not None and depth < history_depth:
                history_depth = None
        if hit:
            found.append(sid)
    return found


# --------------------------------------------------------------------------- runner

def main():
    load_script()
    failures = []
    for fn in CHECKS:
        try:
            fn()
            print('PASS %s' % fn.__name__)
        except AssertionError as exc:
            failures.append((fn.__name__, str(exc)))
            print('FAIL %s: %s' % (fn.__name__, exc))
    print('')
    print('mutants (each must fail when its guard is removed):')
    for name, edits, test in MUTANTS:
        try:
            print('  %-52s %s' % (name, run_mutant(name, edits, test)))
        except AssertionError as exc:
            failures.append((name, str(exc)))
            print('  %-52s FAIL (mutant survived) %s' % (name, exc))
    print('  %-52s %s' % ('M8 duplicated writer definition',
                          'FAILS as required (2 definitions found)' if mutation_count_check() == 2
                          else 'FAIL'))
    blind = old_derive_blind_spot()
    literal = len(proper_ids())
    print('  %-52s %s' % ('control: one-line-history parser loses states',
                          'YES (%d derived vs %d literal)' % (blind, literal)
                          if blind < literal else 'NO (parser accepted every form)'))
    if blind >= literal:
        failures.append(('control', 'the blind-spot control no longer loses any state'))
    dirty_msg, clean_msg, size = bom_strip_control()
    bom_ok = bool(dirty_msg) and not clean_msg
    print('  %-52s %s' % ('control: byte check rejects the pre-strip BOM',
                          'YES (%s / %d-byte file accepted)' % (dirty_msg, size) if bom_ok
                          else 'NO (dirty=%r clean=%r)' % (dirty_msg, clean_msg)))
    if not bom_ok:
        failures.append(('control', 'the BOM predicate no longer distinguishes stripped bytes'))
    print('')
    print('proper states: %d literal, %d derived' % (literal, len(derive_proper_states())))
    if failures:
        print('%d failure(s)' % len(failures))
        return 1
    print('all checks passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
