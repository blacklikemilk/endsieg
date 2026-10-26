"""Reject a UTF-8 BOM in Spain-owned script files.

`common/script_constants/` treats the first token as the schema name, so a BOM makes the
whole category vanish and every `constant:spain_campaign.*` silently read as 0. Decision
files lose their category opener the same way, and a scripted-effects file drops every
function it defines. Localisation `.yml` files are the opposite: they require a BOM.

    python tools/check_script_bom.py
"""

from __future__ import annotations

import os
import sys

ROOTS = ('common', 'events', 'interface')
SCRIPT_SUFFIXES = ('.txt', '.gui', '.gfx')
BOM = b'\xef\xbb\xbf'

# Files that predate this check and are not part of the Spain campaign work.
ALLOWED = {
    os.path.join('common', 'units', 'codenames_operatives', 'SPR_operative_codenames.txt'),
    os.path.join('common', 'units', 'names_divisions', 'SPR_names_divisions.txt'),
    os.path.join('common', 'units', 'names_ships', 'SPR_ship_names.txt'),
    os.path.join('events', 'LAR_Spain.txt'),
    os.path.join('events', 'Spain.txt'),
}


def main() -> int:
    bad = []
    for root in ROOTS:
        for cur, _dirs, files in os.walk(root):
            for name in files:
                low = name.lower()
                if not low.endswith(SCRIPT_SUFFIXES):
                    continue
                if 'spain' not in low and not low.startswith('spr_'):
                    continue
                path = os.path.join(cur, name)
                if path in ALLOWED:
                    continue
                with open(path, 'rb') as handle:
                    if handle.read(3) == BOM:
                        bad.append(path)

    if bad:
        for path in bad:
            print('  BOM in script file: %s' % path)
        print('strip it: localisation needs the BOM, script must not have one')
        return 1
    print('no BOM in Spain-owned script files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
