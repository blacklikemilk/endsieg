"""Check the Cortes party system for dangling references.

Verifies that every decision has a localisation key, every scripted effect it calls is
defined, and every `constant:spain_campaign.*` it uses exists.

    python tools/check_spain_parties.py
"""

from __future__ import annotations

import io
import re
import sys

DECISIONS = 'common/decisions/spain_parties.txt'
EFFECTS = ['common/scripted_effects/spain_cortes_parties.txt',
           'common/scripted_effects/spain_cortes_effects.txt']
ENGINE_OR_TRIGGER = {'mark_focus_tree_layout_dirty'}
CONSTANTS = 'common/script_constants/spain_campaign.txt'
LOC = 'localisation/english/spain_parties_l_english.yml'
CATEGORY = 'common/decisions/categories/spain_parties_category.txt'


def defined_effects(paths):
    names = set()
    for p in paths:
        text = io.open(p, encoding='utf-8-sig').read()
        names |= set(re.findall(r'^([a-z_0-9]+)\s*=\s*\{', text, re.M))
    return names


def main() -> int:
    problems = []
    loc = io.open(LOC, encoding='utf-8-sig').read()
    keys = set(re.findall(r'^\s*([A-Za-z0-9_.]+):', loc, re.M))

    text = io.open(DECISIONS, encoding='utf-8-sig').read()
    ids = re.findall(r'^\t([A-Za-z0-9_]+)\s*=\s*\{', text, re.M)
    effects = defined_effects(EFFECTS + ['common/scripted_effects/spain_cortes_hemicycle.txt'])
    consts = set(re.findall(r'^\s*([a-z_0-9]+)\s*=', io.open(CONSTANTS, encoding='utf-8-sig').read(), re.M))

    called = set(re.findall(r'^\t{0,3}([a-z_0-9]+)\s*=\s*yes', text, re.M))
    used_consts = set(re.findall(r'constant:spain_campaign\.([a-z_0-9]+)', text))

    for e in sorted(called):
        if e not in effects:
            problems.append('decision calls unknown effect: %s' % e)
    for c in sorted(used_consts):
        if c not in consts:
            problems.append('unknown constant in decisions: %s' % c)

    for did in ids:
        if did not in keys:
            problems.append('missing localisation for decision: %s' % did)

    for path in EFFECTS:
        body = io.open(path, encoding='utf-8-sig').read()
        for e in sorted(set(re.findall(r'^\t{0,3}([a-z_0-9]+)\s*=\s*yes', body, re.M))):
            if e in ENGINE_OR_TRIGGER or e.startswith('spain_in_') or e.startswith('spain_nationalist_'):
                continue
            if e not in effects:
                problems.append('%s calls unknown effect: %s' % (path.split('/')[-1], e))
        for c in sorted(set(re.findall(r'constant:spain_campaign\.([a-z_0-9]+)', body))):
            if c not in consts:
                problems.append('%s uses unknown constant: %s' % (path.split('/')[-1], c))

    cat = io.open(CATEGORY, encoding='utf-8-sig').read()
    for k in re.findall(r'^SPR_parties\s*=', cat, re.M) or []:
        pass
    if 'SPR_parties' not in keys:
        problems.append('missing localisation for category: SPR_parties')
    if 'SPR_parties_desc' not in keys:
        problems.append('missing localisation for category description: SPR_parties_desc')

    print('decisions: %d, localisation keys: %d' % (len(ids), len(keys)))
    if problems:
        print('\n'.join('  !! ' + p for p in problems))
        return 1
    print('no dangling references')
    return 0


if __name__ == '__main__':
    sys.exit(main())
