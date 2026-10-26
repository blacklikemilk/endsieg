"""Fix prerequisites that are level with or below their child.

A focus whose prerequisite sits on the same row or lower draws a sideways or upward
connector, which the layout standard forbids. Availability is decided by the prerequisite
graph, not by rows, so pushing such a child one row lower changes nothing in play.

Only coordinate lines are touched. A move is skipped when it would put the child above one
of its own children, or when no free slot exists.

    python tools/fix_spain_upward_edges.py --report
    python tools/fix_spain_upward_edges.py
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

GAP = 1          # free cells either side of the target slot on the new row
MAX_ROUNDS = 12


def parse(path: str):
    text = io.open(path, encoding='utf-8-sig').read()
    nodes = {}
    for m in re.finditer(r'^\t*focus\s*=\s*\{', text, re.M):
        start = m.start()
        i = text.index('{', start)
        d, j = 0, i
        while j < len(text):
            if text[j] == '{':
                d += 1
            elif text[j] == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        body = text[i:j + 1]
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        pos = re.search(r'\bx\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)', body)
        rel = re.search(r'relative_position_id\s*=\s*(\S+)', body)
        groups = [re.findall(r'focus\s*=\s*(\S+)', p)
                  for p in re.findall(r'prerequisite\s*=\s*\{([^{}]*)\}', body)]
        if fid and pos:
            nodes[fid.group(1)] = {
                'prefix': text[start:i], 'body': body, 'start': start, 'end': j + 1,
                'x': int(pos.group(1)), 'y': int(pos.group(2)),
                'rel': rel.group(1) if rel else None,
                'groups': [g for g in groups if g],
            }

    def absolute(f, seen=None):
        seen = seen or set()
        if f in seen or f not in nodes:
            return (0, 0)
        seen.add(f)
        n = nodes[f]
        if not n['rel']:
            return (n['x'], n['y'])
        px, py = absolute(n['rel'], seen)
        return (px + n['x'], py + n['y'])

    pos = {f: absolute(f) for f in nodes}
    return text, nodes, pos


def run(path: str, report_only: bool) -> list:
    text, nodes, pos = parse(path)
    children = {f: set() for f in nodes}
    for f, n in nodes.items():
        for group in n['groups']:
            for alt in group:
                if alt in nodes:
                    children[alt].add(f)

    moves = []
    for _round in range(MAX_ROUNDS):
        occupied = {p: f for f, p in pos.items()}
        fixed = False
        for f in list(nodes):
            fx, fy = pos[f]
            parents = [a for g in nodes[f]['groups'] for a in g if a in pos]
            if not parents:
                continue
            worst = max(pos[a][1] for a in parents)
            if fy > worst:
                continue                      # already below every prerequisite
            target_y = worst + 1
            placed = False
            for shift in (0, -2, 2, -4, 4, -6, 6, -8, 8, -10, 10, -12, 12):
                cand = (fx + shift, target_y)
                if cand[0] < 0:
                    continue
                if any((cand[0] + dx, cand[1]) in occupied and occupied[(cand[0] + dx, cand[1])] != f
                       for dx in (-1, 0, 1)):
                    continue
                # never end up above one of its own children
                if any(pos[c][1] <= target_y for c in children[f]):
                    continue
                del occupied[(fx, fy)]
                occupied[cand] = f
                pos[f] = cand
                moves.append((f, fx, fy, cand[0], target_y, worst))
                placed = True
                fixed = True
                break
            if not placed:
                pass
        if not fixed:
            break

    if moves and not report_only:
        moved = {m[0] for m in moves}
        pieces, last = [], 0
        for fid, n in sorted(nodes.items(), key=lambda kv: kv[1]['start']):
            if fid not in moved:
                continue
            nx, ny = pos[fid]
            body = re.sub(r'^\t*relative_position_id\s*=\s*\S+[ \t]*\r?\n', '', n['body'],
                          count=1, flags=re.M)
            body = re.sub(r'\bx\s*=\s*-?\d+\s+y\s*=\s*-?\d+', 'x = %d y = %d' % (nx, ny), body, count=1)
            pieces.append((n['start'], n['end'], n['prefix'] + body))
        out = []
        for start, end, body_new in pieces:
            out.append(text[last:start])
            out.append(body_new)
            last = end
        out.append(text[last:])
        io.open(path, 'w', encoding='utf-8', newline='').write(''.join(out))

    return moves


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()
    total = 0
    for path in TREES:
        moves = run(path, args.report)
        total += len(moves)
        print('%-28s moves %2d' % (path.split('/')[-1], len(moves)))
        for f, ox, oy, nx, ny, worst in moves[:8]:
            print('   %-38s (%d,%d) -> (%d,%d)  prerequisite at row %d' % (f, ox, oy, nx, ny, worst))
    print('total moves:', total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
