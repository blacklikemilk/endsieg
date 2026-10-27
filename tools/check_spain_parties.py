"""Check the Cortes party system for dangling references.

Verifies that every decision has a localisation key, every scripted effect it calls is
defined, and every `constant:spain_campaign.*` it uses exists. The effect registry is built from
the party and effects files that are scanned, plus the bills and hemicycle files that are read for
their declarations only: `spain_cortes_recount` calls `spain_bills_count_all`, which
`common/scripted_effects/spain_cortes_bills.txt` defines, and a registry without that file reports
a working effect as unknown.

    python tools/check_spain_parties.py            # check this repository
    python tools/check_spain_parties.py <root>     # check another tree root

The root argument exists for the negative controls in
`.tools/tests/test_spain_cortes_postwar_bills.py`: a shadow tree carrying an injected unknown
effect has to fail, otherwise a clean run proves nothing about what the checker can detect.
"""

from __future__ import annotations

import io
import os
import re
import sys

DECISIONS = 'common/decisions/spain_parties.txt'
# Files whose own call sites are checked.
EFFECTS = ['common/scripted_effects/spain_cortes_parties.txt',
           'common/scripted_effects/spain_cortes_effects.txt']
# Files read for the effect registry only. They declare effects the scanned files call; their own
# call sites reach campaign and party helpers through other files, so scanning them here would
# report a different file's dependency as this checker's finding.
REGISTRY_ONLY = ['common/scripted_effects/spain_cortes_bills.txt',
                 'common/scripted_effects/spain_cortes_hemicycle.txt']
ENGINE_OR_TRIGGER = {'mark_focus_tree_layout_dirty'}
CONSTANTS = 'common/script_constants/spain_campaign.txt'
LOC = 'localisation/english/spain_parties_l_english.yml'
CATEGORY = 'common/decisions/categories/spain_parties_category.txt'


def load(root, path):
    return io.open(os.path.join(root, path), encoding='utf-8-sig').read()


def defined_effects(root, paths):
    names = set()
    for path in paths:
        names |= set(re.findall(r'^([a-z_0-9]+)\s*=\s*\{', load(root, path), re.M))
    return names


def main(root='.') -> int:
    problems = []
    loc = load(root, LOC)
    keys = set(re.findall(r'^\s*([A-Za-z0-9_.]+):', loc, re.M))

    text = load(root, DECISIONS)
    ids = re.findall(r'^\t([A-Za-z0-9_]+)\s*=\s*\{', text, re.M)
    effects = defined_effects(root, EFFECTS + REGISTRY_ONLY)
    consts = set(re.findall(r'^\s*([a-z_0-9]+)\s*=', load(root, CONSTANTS), re.M))

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
        body = load(root, path)
        for e in sorted(set(re.findall(r'^\t{0,3}([a-z_0-9]+)\s*=\s*yes', body, re.M))):
            if e in ENGINE_OR_TRIGGER or e.startswith('spain_in_') or e.startswith('spain_nationalist_'):
                continue
            if e not in effects:
                problems.append('%s calls unknown effect: %s' % (path.split('/')[-1], e))
        for c in sorted(set(re.findall(r'constant:spain_campaign\.([a-z_0-9]+)', body))):
            if c not in consts:
                problems.append('%s uses unknown constant: %s' % (path.split('/')[-1], c))

    cat = load(root, CATEGORY)
    for k in re.findall(r'^SPR_parties\s*=', cat, re.M) or []:
        pass
    if 'SPR_parties' not in keys:
        problems.append('missing localisation for category: SPR_parties')
    if 'SPR_parties_desc' not in keys:
        problems.append('missing localisation for category description: SPR_parties_desc')

    print('root: %s' % os.path.abspath(root))
    print('registry files: %d, decisions: %d, localisation keys: %d'
          % (len(EFFECTS + REGISTRY_ONLY), len(ids), len(keys)))
    if problems:
        print('\n'.join('  !! ' + p for p in problems))
        return 1
    print('no dangling references')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
