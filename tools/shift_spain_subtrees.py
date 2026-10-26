"""Drop a whole dependent subtree so its prerequisite sits strictly above it.

Nine prerequisites in these trees sit on the same row as their child, or below it, which
draws sideways or upward connectors. The children cannot simply move down one row because
their own children occupy that row, so the whole subtree moves together — and only when
every target cell is free.

Availability comes from the prerequisite graph, so rows are presentation only: no focus
changes behaviour.

    python tools/shift_spain_subtrees.py --report
    python tools/shift_spain_subtrees.py
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

MAX_ROUNDS = 20


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

    return text, nodes, {f: absolute(f) for f in nodes}


def descendants(root, children):
    out, stack = set(), [root]
    while stack:
        cur = stack.pop()
        for c in children.get(cur, ()):
            if c not in out:
                out.add(c)
                stack.append(c)
    return out


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
        fixed = False
        for f in list(nodes):
            fx, fy = pos[f]
            parents = [a for g in nodes[f]['groups'] for a in g if a in pos]
            if not parents:
                continue
            floor = max(pos[a][1] for a in parents)
            if fy > floor:
                continue
            drop = floor + 1 - fy
            block = {f} | descendants(f, children)
            occupied = {p: n for n, p in pos.items()}
            targets = {n: (pos[n][0], pos[n][1] + drop) for n in block}
            if any(t in occupied and occupied[t] not in block for t in targets.values()):
                continue
            # a shift must not push anything past its own children that stay behind
            for n in nodes:
                if n in block:
                    continue
                for a in [a for g in nodes[n]['groups'] for a in g if a in pos]:
                    if a in block and pos[a][1] >= pos[n][1]:
                        block = None
                        break
                if block is None:
                    break
            if block is None:
                continue
            for n in block:
                pos[n] = targets[n]
            moves.append((sorted(block), drop, floor))
            fixed = True
        if not fixed:
            break

    if moves and not report_only:
        moved = {n for block, _d, _f in moves for n in block}
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
        total += sum(len(block) for block, _d, _f in moves)
        print('%-28s subtree moves %d, focuses shifted %d'
              % (path.split('/')[-1], len(moves), sum(len(b) for b, _d, _f in moves)))
        for block, drop, floor in moves[:4]:
            print('   drop %d from row %d: %s' % (drop, floor, ', '.join(sorted(block)[:4])))
    print('total focuses shifted:', total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
