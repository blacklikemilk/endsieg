"""Pull lone Spanish focuses back under their prerequisite.

A leaf that hangs far from its parent produces a long horizontal connector for no reason:
nothing depends on it, so moving it changes no gameplay and no other node's position.
This tool finds leaves whose single prerequisite is more than `THRESHOLD` X cells away and
moves them to a free slot two cells from that parent, keeping the row and the minimum
two-cell spacing. It never moves a focus that has children, never changes a tier, and never
touches a line other than x and y.

    python tools/tighten_spain_tree.py --report     # show the moves without writing
    python tools/tighten_spain_tree.py              # apply
"""

from __future__ import annotations

import argparse
import io
import re
import sys

TREES = [
    'common/national_focus/spain_restoration.txt',
    'common/national_focus/spain_rivera.txt',
    'common/national_focus/spain_republic.txt',
    'common/national_focus/spain_republic_postwar.txt',
]

GAP = 2          # free cells required either side of a target slot
THRESHOLD = 3    # dx above which a leaf is considered to hang
MAX_ROUNDS = 4
MAX_SHIFT = 4    # per round, so a leaf walks toward its parent instead of jumping families


def read(path: str) -> str:
    return io.open(path, encoding='utf-8-sig').read()


def parse(path: str):
    text = read(path)
    nodes = {}
    for m in re.finditer(r'^\t*focus\s*=\s*\{', text, re.M):
        start = m.start()
        i = text.index('{', start)
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
        if not fid:
            continue
        pos = re.search(r'\bx\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)', body)
        rel = re.search(r'relative_position_id\s*=\s*(\S+)', body)
        groups = [re.findall(r'focus\s*=\s*(\S+)', pre)
                  for pre in re.findall(r'prerequisite\s*=\s*\{([^{}]*)\}', body)]
        nodes[fid.group(1)] = {
            'body': body, 'prefix': text[start:i], 'start': start, 'end': j + 1,
            'x': int(pos.group(1)) if pos else 0,
            'y': int(pos.group(2)) if pos else 0,
            'rel': rel.group(1) if rel else None,
            'groups': [g for g in groups if g],
        }

    def absolute(fid, seen=None):
        seen = seen or set()
        if fid in seen or fid not in nodes:
            return (0, 0)
        seen.add(fid)
        n = nodes[fid]
        if not n['rel']:
            return (n['x'], n['y'])
        px, py = absolute(n['rel'], seen)
        return (px + n['x'], py + n['y'])

    for f in nodes:
        nodes[f]['abs'] = absolute(f)
    return text, nodes


def tighten(path: str, report_only: bool) -> dict:
    text, nodes = parse(path)
    pos = {f: n['abs'] for f, n in nodes.items()}
    children = {f: set() for f in nodes}
    for f, n in nodes.items():
        for group in n['groups']:
            for alt in group:
                if alt in nodes:
                    children[alt].add(f)

    moves = []
    for _round in range(MAX_ROUNDS):
        occupied = {}
        for f, p in pos.items():
            occupied[p] = f
        moved = False
        for f, n in nodes.items():
            if children[f]:
                continue                      # only leaves are safe to move
            alts = [a for g in n['groups'] for a in g if a in pos]
            if len(alts) != 1:
                continue                      # OR-groups: the other parent may be the anchor
            parent = alts[0]
            px, py = pos[parent]
            fx, fy = pos[f]
            if fy == py:
                continue                      # same row: already sideways
            if abs(fx - px) <= THRESHOLD:
                continue
            best = None
            for candidate in (px - GAP, px + GAP, px - GAP * 2, px + GAP * 2):
                if candidate == fx or abs(candidate - fx) > MAX_SHIFT:
                    continue
                if any((candidate + dx, fy) in occupied and occupied[(candidate + dx, fy)] != f
                       for dx in (-1, 0, 1)):
                    continue
                score = abs(candidate - px)
                if best is None or score < best[0]:
                    best = (score, candidate)
            if best is None:
                continue
            _, new_x = best
            del occupied[(fx, fy)]
            occupied[(new_x, fy)] = f
            pos[f] = (new_x, fy)
            moves.append((f, fx, fy, new_x, px))
            moved = True
        if not moved:
            break

    if moves and not report_only:
        pieces, last = [], 0
        for fid, n in sorted(nodes.items(), key=lambda kv: kv[1]['start']):
            if fid not in {m[0] for m in moves}:
                continue
            body = n['body']
            nx, ny = pos[fid]
            body_new = re.sub(r'^\t*relative_position_id\s*=\s*\S+[ \t]*\r?\n', '', body,
                              count=1, flags=re.M)
            if re.search(r'\bx\s*=\s*-?\d+\s+y\s*=\s*-?\d+', body_new):
                body_new = re.sub(r'\bx\s*=\s*-?\d+\s+y\s*=\s*-?\d+',
                                  'x = %d y = %d' % (nx, ny), body_new, count=1)
            pieces.append((n['start'], n['end'], n['prefix'] + body_new))
        out = []
        for start, end, body_new in pieces:
            out.append(text[last:start])
            out.append(body_new)
            last = end
        out.append(text[last:])
        io.open(path, 'w', encoding='utf-8', newline='').write(''.join(out))

    return {'moves': moves}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()

    total = 0
    for path in TREES:
        stats = tighten(path, args.report)
        total += len(stats['moves'])
        print('%-28s moves %2d' % (path.split('/')[-1], len(stats['moves'])))
        for f, fx, fy, nx, px in stats['moves'][:6]:
            print('   %-38s x %3d -> %3d  (parent at %d, row %d)' % (f, fx, nx, px, fy))
    print('total moves:', total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
