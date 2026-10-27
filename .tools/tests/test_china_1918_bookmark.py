"""Executes the shipped China 1918 bookmark startup, and its two repairs.

The module does not restate the bookmark in Python. It reads `on_startup` from
common/on_actions/endsieg_on_actions.txt, takes the two guarded blocks that name RCH, and runs
them against a modelled world: the Republic's own chapter script from
common/scripted_effects/rch_campaign.txt through the single-country interpreter in
test_rch_succession.py, and the generic warlord release from
common/scripted_effects/china_warlord_release.txt through the same interpreter extended with a
tag scope, `transfer_state`, `add_state_core` and `recruit_character`.

What the model proves: that the startup pass, as written, leaves the Republic on `rch_republic`
at 1918 and Shanxi owning state 615 before any daily tick; that running it twice pays nothing
twice; and that removing either block restores the reported defect, so neither block is
decoration. What the model cannot prove: what the engine does with a loaded tree or a released
tag after the effect returns, and whether the focus panel, the map or the decision panel draw
any of it. Those remain live checks.

Negative controls: the same startup text with one block deleted is run as `--without-repair` and
`--without-release` fixtures, and the pre-1916 and post-1936 boundaries are run as ordinary
cases, so the guards cannot be satisfied by accident.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

from test_qing_survival import parse_text, scalar, Unsupported  # noqa: E402
from test_rch_succession import (  # noqa: E402
    Country, Script, block, plain, read,
)

VERBOSE = '--detail' in sys.argv

ON_ACTIONS = 'common/on_actions/endsieg_on_actions.txt'
RCH_DAILY = 'common/on_actions/rch_campaign.txt'
RELEASE = 'common/scripted_effects/china_warlord_release.txt'

SEAT = 615
BEIPING = 608
FAILURES = []


def fail(message):
    FAILURES.append(message)
    print('FAIL ' + message)


def ok(message):
    if VERBOSE:
        print('  ok ' + message)


def check(condition, message):
    if condition:
        ok(message)
    else:
        fail(message)
    return condition


def commands(entries, found=None):
    """Every command in a block, nested or not, as (key, operator, operand) in file order."""
    found = [] if found is None else found
    for key, value, _line in entries:
        if value[0] == 'scalar':
            found.append((key, '=', value[1]))
        elif value[0] == 'compare':
            found.append((key, value[1], value[2]))
        else:
            commands(value[1], found)
    return found


def on_startup(text):
    actions = block(parse_text(text), 'on_actions')
    if actions is None:
        raise Unsupported('on_actions is not defined in the on_action file')
    startup = block(actions, 'on_startup')
    if startup is None:
        raise Unsupported('on_startup is not defined')
    effect = block(startup, 'effect')
    if effect is None:
        raise Unsupported('on_startup carries no effect block')
    return effect


def daily_release(text):
    """The release hook inside on_daily_RCH, found by the command it calls."""
    actions = block(parse_text(text), 'on_actions')
    daily = block(actions, 'on_daily_RCH')
    if daily is None:
        raise Unsupported('on_daily_RCH is not defined')
    effect = block(daily, 'effect')
    for key, value, line in effect:
        if key == 'if' and ('china_release_warlord_shx', '=', 'yes') in commands(value[1]):
            return (line, value[1])
    raise Unsupported('on_daily_RCH has no Shanxi release hook')


def tree_loop(text):
    """The line of the every_country pass that loads the WWI-era trees."""
    for key, value, line in on_startup(text):
        if key != 'if' or value[0] != 'block':
            continue
        if any(entry[0] == 'every_country' for entry in value[1]):
            if ('date', '<', '1936.1.1') in commands(value[1]):
                return line
    raise Unsupported('on_startup has no date < 1936.1.1 every_country tree pass')


def startup_blocks(text):
    """The two guarded RCH blocks of on_startup, keyed by the repair each one performs."""
    found = {}
    for key, value, line in on_startup(text):
        if key != 'if' or value[0] != 'block':
            continue
        limit = block(value[1], 'limit')
        if limit is None:
            continue
        names = commands(limit)
        if ('country_exists', '=', 'RCH') not in names:
            continue
        body = commands(value[1])
        keys = [name for name, _op, _operand in body]
        if 'rch_initialize_campaign' in keys:
            found.setdefault('repair', (line, value[1], names, keys))
        elif 'china_release_warlord_shx' in keys:
            found.setdefault('release', (line, value[1], names, keys))
    return found


def guarded(entries, command):
    """The first `if` body, at any depth, whose own entries hold one command."""
    for key, value, _line in entries:
        if value[0] != 'block':
            continue
        if key == 'if' and command in [entry[0] for entry in value[1]]:
            return value[1]
        found = guarded(value[1], command)
        if found is not None:
            return found
    return None


class World:
    """Countries by tag, states by owner, and the cores each country records."""

    def __init__(self):
        self.states = {}
        self.cores = {}
        self.countries = {}

    def add(self, tag, country):
        country.tag = tag
        country.characters = set()
        self.countries[tag] = country
        return country

    def owns(self, country, state):
        return self.states.get(state) == country.tag


class ChinaScript(Script):
    """The Republic interpreter, extended with the release commands and the 1918 world."""

    def __init__(self, world):
        Script.__init__(self)
        self.world = world
        self.extra_effects = dict(
            (key, value[1]) for key, value, _line in parse_text(read(RELEASE))
            if value[0] == 'block')

    def trigger(self, entries, country, depth=0):
        for entry in entries:
            key, value, _line = entry
            if key in self.world.countries and value[0] == 'block':
                if not self.trigger(value[1], self.world.countries[key], depth + 1):
                    return False
            elif key == 'any_owned_state':
                if not any(self.world.owns(country, state) for state in sorted(self.world.states)):
                    return False
            elif key == 'owns_state':
                if not self.world.owns(country, int(value[1])):
                    return False
            elif key == 'country_exists':
                if value[1] not in self.world.countries:
                    return False
            elif key == 'has_character':
                if value[1] not in country.characters:
                    return False
            elif key == 'tag':
                if value[1] != country.tag:
                    return False
            elif not Script.trigger(self, [entry], country, depth):
                return False
        return True

    def effect(self, entries, country, depth=0):
        for entry in entries:
            key, value, _line = entry
            if key in self.world.countries and value[0] == 'block':
                self._run_block(value[1], self.world.countries[key], depth + 1)
            elif key in self.extra_effects:
                self._run_block(self.extra_effects[key], country, depth + 1)
            elif key == 'transfer_state':
                if value[0] != 'scalar':
                    raise Unsupported('transfer_state without a target at line %d' % _line)
                state = int(self.value(value[1], country))
                self.world.states[state] = country.tag
                country.trace.append(('transfer_state', state))
            elif key == 'add_state_core':
                self.world.cores.setdefault(country.tag, set()).add(int(value[1]))
            elif key == 'recruit_character':
                country.characters.add(value[1])
                country.trace.append(('recruit', value[1]))
            elif key == 'shx_campaign_tick':
                country.trace.append(('tick', key))
            elif key == 'load_focus_tree':
                # One tree per country: a load replaces the tree that was standing.
                tree = scalar(value[1], 'tree')
                if tree is None:
                    raise Unsupported('load_focus_tree without a tree at line %d' % _line)
                country.focus_tree = set([tree])
                country.trace.append(('tree', tree))
            else:
                Script.effect(self, [entry], country, depth)


def opening_variables():
    return {'rch_legitimacy': 30.0, 'rch_military_influence': 55.0,
            'rch_nationalist_support': 20.0, 'rch_governor_count': 0.0,
            'rch_reform_settled': 0.0, 'rch_bop_band': -1.0}


def bookmark_1918(started):
    """A 1918 Republic holding Beiping, the seat, and the generic tree the report showed.

    `started` is the case where the tree loop above already reached the Republic: its campaign
    flag and its chapter flag stand, but the tree is still the generic WWI one. The other case is
    the loop missing the Republic altogether, so nothing about the campaign is set.
    """
    world = World()
    rch = world.add('RCH', Country(
        date='1918.3.21',
        controlled=(BEIPING, SEAT),
        political_power=200,
        variables=opening_variables() if started else {}))
    rch.focus_tree = set(['generic_focus_ww1'])
    if started:
        rch.set_flag('rch_campaign_active', '1918.3.21')
        rch.set_flag('rch_chapter_one', '1918.3.21')
    world.add('SHX', Country(date='1918.3.21', controlled=()))
    world.countries['SHX'].focus_tree = set()
    world.states[BEIPING] = 'RCH'
    world.states[SEAT] = 'RCH'
    return world


def run_startup(world, blocks, text, with_repair=True, with_release=True):
    script = ChinaScript(world)
    rch = world.countries['RCH']
    chosen = []
    if with_repair and 'repair' in blocks:
        chosen.append(('if', ('block', blocks['repair'][1]), blocks['repair'][0]))
    if with_release and 'release' in blocks:
        chosen.append(('if', ('block', blocks['release'][1]), blocks['release'][0]))
    script._run_block(chosen, rch, 0)
    return script


def run_daily_release(world, text):
    script = ChinaScript(world)
    line, body = daily_release(text)
    script._run_block([('if', ('block', body), line)], world.countries['RCH'], 0)
    return script


def structural(text):
    print('startup structure')
    blocks = startup_blocks(text)
    check('repair' in blocks, 'on_startup carries the bounded RCH chapter repair')
    check('release' in blocks, 'on_startup carries the bounded Shanxi pre-release')
    if 'repair' not in blocks or 'release' not in blocks:
        return blocks
    line, body, names, keys = blocks['repair']
    check(('date', '<', '1936.1.1') in names,
          'the chapter repair is bounded to starts before 1936')
    check(keys.index('rch_initialize_campaign') < keys.index('rch_route_chapter'),
          'the chapter repair initialises before it routes')
    check(line > tree_loop(text),
          'the chapter repair runs after the every_country tree pass')
    line, body, names, keys = blocks['release']
    check(('date', '>', '1916.6.5') in names,
          'the pre-release begins only after the 1916 succession date')
    check(('date', '<', '1936.1.1') in names, 'the pre-release stops before the 1936 handover')
    outer = guarded(body, 'china_release_warlord_shx')
    check(outer is not None, 'the release wrapper sits inside its own guard')
    limit = block(outer, 'limit') if outer is not None else None
    check(limit is not None
          and ('has_country_flag', '=', 'china_released_shx') in commands(limit)
          and any(entry[0] == 'NOT' for entry in limit),
          'the release wrapper is entered only while its flag is unset')
    released = outer or []
    inners = [value[1] for key, value, _line in released
              if key == 'if' and value[0] == 'block']
    check(len(inners) == 1, 'the release pass carries one post-release guard')
    if inners:
        inner = inners[0]
        inner_limit = block(inner, 'limit')
        check(inner_limit is not None
              and ('has_country_flag', '=', 'china_released_shx') in commands(inner_limit),
              'the province event is fired only once the release landed')
        province = block(inner, 'SHX')
        check(province is not None, 'the post-release pass runs in Shanxi scope')
        event = block(province or [], 'country_event')
        check(event is not None and scalar(event, 'id') == 'shx_campaign.1',
              'the province event is shx_campaign.1')
    check(('shx_campaign_tick', '=', 'yes') in commands(released),
          'the released province is routed to its opening band in the same pass')
    return blocks


def shipped_startup():
    print('1918 startup, as shipped')
    text = read(ON_ACTIONS)
    blocks = startup_blocks(text)
    if 'repair' not in blocks or 'release' not in blocks:
        check(False, 'the startup blocks the acceptance depends on are both present')
        return

    for started in (True, False):
        label = 'campaign already open' if started else 'campaign never opened'
        world = bookmark_1918(started)
        run_startup(world, blocks, text)
        rch = world.countries['RCH']
        shx = world.countries['SHX']
        check('rch_republic' in rch.focus_tree,
              '%s: the Republic holds rch_republic at 1918 load (%s)'
              % (label, sorted(rch.focus_tree)))
        check('generic_focus_ww1' not in rch.focus_tree,
              '%s: the generic WWI tree is gone' % label)
        check('rch_campaign_active' in rch.flags,
              '%s: the campaign is active after startup' % label)
        check('rch_1936_settled' not in rch.flags,
              '%s: the 1936 settlement does not run at 1918' % label)
        chapters = [event for event, _days in rch.queued if event == 'rch_campaign.1']
        expected = 0 if started else 1
        check(len(chapters) == expected,
              '%s: the chapter one event is queued %d time(s) (%d)'
              % (label, expected, len(chapters)))

        check(world.states[SEAT] == 'SHX',
              '%s: Shanxi owns state %d at load' % (label, SEAT))
        check('china_released_shx' in rch.flags,
              '%s: the Republic records the release' % label)
        check('china_warlord_released' in shx.flags,
              '%s: Shanxi carries china_warlord_released' % label)
        check('SHX_yan_xishan' in shx.characters,
              '%s: Yan Xishan leads the province' % label)
        check(SEAT in world.cores.get('SHX', set()),
              '%s: Shanxi cores its seat' % label)
        events = [event for event, _days in shx.queued if event == 'shx_campaign.1']
        check(events == ['shx_campaign.1'],
              '%s: the province event is queued once (%d)' % (label, len(events)))
        check(('tick', 'shx_campaign_tick') in shx.trace,
              '%s: the province is routed to its opening band at startup' % label)

        # A second pass, as a reload or a duplicated hook would produce.
        before_chapters, before_events = len(chapters), len(events)
        run_startup(world, blocks, text)
        chapters = [event for event, _days in rch.queued if event == 'rch_campaign.1']
        events = [event for event, _days in shx.queued if event == 'shx_campaign.1']
        check(len(chapters) == before_chapters,
              '%s: a second startup pass pays no second chapter event' % label)
        check(len(events) == before_events,
              '%s: a second startup pass fires no second province event' % label)
        check(sorted(rch.focus_tree) == ['rch_republic'],
              '%s: a second startup pass leaves exactly one chapter tree' % label)
        check(world.states[SEAT] == 'SHX', '%s: a second pass transfers nothing further' % label)


def negative_controls():
    print('negative controls')
    blocks = startup_blocks(plain(read(ON_ACTIONS)))
    if 'repair' not in blocks or 'release' not in blocks:
        check(False, 'the controls cannot run without both startup blocks')
        return
    without_repair = plain(read(ON_ACTIONS))
    start = without_repair.index('            # The Republic\'s country history completes')
    end = without_repair.index('            # A start after the 1916 succession begins')
    stripped = without_repair[:start] + without_repair[end:]
    control = startup_blocks(stripped)
    check('repair' not in control, 'the repaired control is stripped of the chapter repair')
    world = bookmark_1918(True)
    run_startup(world, control, stripped)
    check('generic_focus_ww1' in world.countries['RCH'].focus_tree,
          'without the chapter repair the Republic keeps the generic WWI tree')
    check(world.states[SEAT] == 'SHX',
          'without the chapter repair the province still exists, so only the tree regresses')

    start = without_repair.index('            # A start after the 1916 succession begins')
    end = without_repair.index('            if = {\n                limit = { country_exists = TUR }')
    stripped = without_repair[:start] + without_repair[end:]
    control = startup_blocks(stripped)
    check('release' not in control, 'the released control is stripped of the pre-release')
    world = bookmark_1918(True)
    run_startup(world, control, stripped)
    check(world.states[SEAT] == 'RCH',
          'without the pre-release the Republic still owns state %d at load' % SEAT)
    check('china_warlord_released' not in world.countries['SHX'].flags,
          'without the pre-release Shanxi is dormant at load')
    run_daily_release(world, read(RCH_DAILY))
    check(world.states[SEAT] == 'SHX',
          'the daily hook then releases the province, which is the reported pop on unpause')
    check('china_warlord_released' in world.countries['SHX'].flags,
          'the daily hook leaves the province on its campaign')


def boundaries():
    print('date boundaries')
    text = read(ON_ACTIONS)
    blocks = startup_blocks(text)
    if 'repair' not in blocks or 'release' not in blocks:
        check(False, 'the boundary cases cannot run without both startup blocks')
        return
    early = bookmark_1918(False)
    early.countries['RCH'].date = '1916.6.5'
    run_startup(early, blocks, text)
    check(early.states[SEAT] == 'RCH',
          'on 1916.6.5 the province is still the Republic, as the daily hook requires')
    check('rch_republic' in early.countries['RCH'].focus_tree,
          'on 1916.6.5 the Republic still takes its chapter one tree')
    late = bookmark_1918(False)
    for tag in ('RCH', 'SHX'):
        late.countries[tag].date = '1936.1.1'
    run_startup(late, blocks, text)
    check(late.states[SEAT] == 'RCH',
          'at 1936.1.1 the pre-release does not run, so the state history handover stands')
    check('rch_republic' not in late.countries['RCH'].focus_tree,
          'at 1936.1.1 the chapter repair does not run')


def main():
    try:
        run()
    except Unsupported as error:
        fail('a shipped command is not modelled, so the suite cannot pass: %s' % error)
    print()
    if FAILURES:
        print('%d check(s) failed' % len(FAILURES))
        return 1
    print('all checks passed')
    return 0


def run():
    structural(read(ON_ACTIONS))
    shipped_startup()
    negative_controls()
    boundaries()
    return 0


if __name__ == '__main__':
    sys.exit(main())
