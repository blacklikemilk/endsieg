"""Straighten mechanically linear focus chains.

`FOCUS_LAYOUT_LINEAR_DETOUR` means a focus with one prerequisite sits one row below it but
offset sideways, so a straight chain is drawn as a zigzag. This pass puts such a child
directly under its parent, moving the child's whole subtree when it has one, and only when
the destination is free. Everything else is left alone.

    python tools/straighten_spain_chains.py --report
    python tools/straighten_spain_chains.py

Always run `tools/measure_spain_layout.py` afterwards: a subtree shift can land inside a
dense row, so a pass is only accepted when the measured minimum gap is still two cells and
`tools/verify_spain_layout_preserved.py` passes.
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
COORD = re.compile(r'\bx\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)')


def read(path):
    return io.open(path, encoding='utf-8-sig').read()


def spans(text):
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
        yield i, j + 1, text[i:j + 1]


def parse(path):
    text = read(path)
    nodes = {}
    for start, end, body in spans(text):
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        pos = COORD.search(body)
        if not fid or not pos:
            continue
        groups = [re.findall(r'focus\s*=\s*(\S+)', pre)
                  for pre in re.findall(r'prerequisite\s*=\s*\{([^{}]*)\}', body)]
        nodes[fid.group(1)] = {
            'x': int(pos.group(1)), 'y': int(pos.group(2)),
            'groups': [g for g in groups if g],
        }
    return text, nodes


def descendants(root, children):
    out, stack = set(), [root]
    while stack:
        cur = stack.pop()
        for c in children.get(cur, []):
            if c not in out:
                out.add(c)
                stack.append(c)
    return out


def straighten(path, write):
    text, nodes = parse(path)
    if not nodes:
        return None

    children = {f: [] for f in nodes}
    for fid, n in nodes.items():
        for group in n['groups']:
            for alt in group:
                if alt in nodes:
                    children[alt].append(fid)

    occupied = {(n['x'], n['y']): f for f, n in nodes.items()}
    moved = 0

    for fid in sorted(nodes, key=lambda f: (nodes[f]['y'], nodes[f]['x'])):
        n = nodes[fid]
        if len(n['groups']) != 1 or len(n['groups'][0]) != 1:
            continue                                    # not a linear chain
        parent = n['groups'][0][0]
        if parent not in nodes:
            continue
        p = nodes[parent]
        if n['y'] != p['y'] + 1 or n['x'] == p['x']:
            continue                                    # already straight, or not adjacent

        dx = p['x'] - n['x']
        group = {fid} | descendants(fid, children)
        moved_pos = {(nodes[f]['x'] + dx, nodes[f]['y']) for f in group}
        blocked = any(
            (pos in occupied and occupied[pos] not in group)
            or ((pos[0] - 1, pos[1]) in occupied and occupied[(pos[0] - 1, pos[1])] not in group)
            or ((pos[0] + 1, pos[1]) in occupied and occupied[(pos[0] + 1, pos[1])] not in group)
            for pos in moved_pos)
        if blocked:
            continue

        for f in group:
            old = (nodes[f]['x'], nodes[f]['y'])
            occupied.pop(old, None)
        for f in group:
            nodes[f]['x'] += dx
            occupied[(nodes[f]['x'], nodes[f]['y'])] = f
        moved += 1

    out, last = [], 0
    for start, end, body in spans(text):
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        if not fid or fid.group(1) not in nodes:
            continue
        n = nodes[fid.group(1)]
        out.append(text[last:start])
        out.append(COORD.sub('x = %d y = %d' % (n['x'], n['y']), body, count=1))
        last = end
    out.append(text[last:])
    new_text = ''.join(out)
    if write:
        io.open(path, 'w', encoding='utf-8', newline='').write(new_text)
    return {'focuses': len(nodes), 'moved': moved}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()
    for path in TREES:
        res = straighten(path, not args.report)
        if res:
            print('%-30s %3d focuses  straightened %2d chains'
                  % (path.split('/')[-1], res['focuses'], res['moved']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
