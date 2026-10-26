"""Prove a layout pass changed coordinates and nothing else.

Every focus body is compared byte-for-byte after removing the lines a layout pass is
allowed to touch (x, y and relative_position_id). Focus ids, counts, prerequisites,
mutual exclusions, rewards, costs, bypasses, availability, visibility, AI weights and
search filters must be identical, or the pass is rejected.

    python tools/verify_spain_layout_preserved.py .tmp/spain_layout_before
"""

from __future__ import annotations

import io
import os
import re
import sys

TREES = ['spain_restoration.txt', 'spain_rivera.txt', 'spain_republic.txt',
         'spain_republic_postwar.txt']
LIVE = 'common/national_focus'

COORD = re.compile(r'^\s*(x|y|relative_position_id)\s*=\s*[^\r\n]*\r?\n', re.M)


def read(path: str) -> str:
    return io.open(path, encoding='utf-8-sig').read()


def bodies(text: str):
    out = {}
    for m in re.finditer(r'^\t*focus\s*=\s*\{', text, re.M):
        i = text.index('{', m.start())
        depth, j = 0, i
        while j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = text[i:j + 1]
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        if fid:
            out[fid.group(1)] = COORD.sub('', body)
    return out


def main() -> int:
    baseline = sys.argv[1] if len(sys.argv) > 1 else '.tmp/spain_layout_before'
    failures = 0

    for name in TREES:
        live = os.path.join(LIVE, name)
        old = os.path.join(baseline, name)
        if not os.path.exists(old):
            print('%-32s no baseline' % name)
            continue
        before, after = bodies(read(old)), bodies(read(live))

        missing = sorted(set(before) - set(after))
        added = sorted(set(after) - set(before))
        changed = sorted(f for f in before if f in after and before[f] != after[f])

        status = 'OK' if not (missing or added or changed) else 'REJECT'
        print('%-32s %3d -> %3d focuses  %s' % (name, len(before), len(after), status))
        if missing:
            print('   removed:', missing[:5])
            failures += 1
        if added:
            print('   added  :', added[:5])
            failures += 1
        for f in changed[:5]:
            failures += 1
            old_lines = before[f].split('\n')
            new_lines = after[f].split('\n')
            print('   changed body:', f)
            for a, b in zip(old_lines, new_lines):
                if a != b:
                    print('      before: %s' % a.strip()[:90])
                    print('      after : %s' % b.strip()[:90])
                    break

    print()
    print('gameplay preservation:', 'PASS' if failures == 0 else 'FAIL (%d)' % failures)
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
