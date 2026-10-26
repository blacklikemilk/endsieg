"""Measure the Spanish chapter-tree layouts: overlaps, gaps, connector lengths, crossings.

The numbers this prints are the acceptance evidence for a layout pass, because the MCP
focus tools are unavailable in this session. It reads script only; it cannot judge icons or
in-game clipping.

    python tools/measure_spain_layout.py [--baseline DIR]
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys

TREES = [
    ('spain_restoration', 'common/national_focus/spain_restoration.txt'),
    ('spain_rivera', 'common/national_focus/spain_rivera.txt'),
    ('spain_republic', 'common/national_focus/spain_republic.txt'),
    ('spain_republic_postwar', 'common/national_focus/spain_republic_postwar.txt'),
]


def read(path: str) -> str:
    return io.open(path, encoding='utf-8-sig').read()


def parse(path: str):
    text = read(path)
    nodes = {}
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
        if not fid:
            continue
        pos = re.search(r'\bx\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)', body)
        rel = re.search(r'relative_position_id\s*=\s*(\S+)', body)
        groups = [re.findall(r'focus\s*=\s*(\S+)', pre)
                  for pre in re.findall(r'prerequisite\s*=\s*\{([^{}]*)\}', body)]
        nodes[fid.group(1)] = {
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

    for f, n in nodes.items():
        n['abs'] = absolute(f)
    return nodes


def measure(nodes):
    pos = {f: n['abs'] for f, n in nodes.items()}
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    width = max(xs) - min(xs) + 1
    height = max(ys) - min(ys) + 1
    cells = width * height
    occupied = len(nodes)
    fill = occupied / cells if cells else 0

    # duplicate / overlapping cells
    by_cell = {}
    for f, p in pos.items():
        by_cell.setdefault(p, []).append(f)
    overlaps = {p: v for p, v in by_cell.items() if len(v) > 1}

    # side-by-side neighbours (icons are two columns wide)
    too_close = []
    for (x, y), names in by_cell.items():
        if (x + 1, y) in by_cell:
            too_close.append((x, y, names[0], by_cell[(x + 1, y)][0]))

    # rows and their spacing
    rows = {}
    for f, (x, y) in pos.items():
        rows.setdefault(y, []).append(x)
    row_gaps = []
    for y, xs_row in rows.items():
        xs_row.sort()
        row_gaps.extend(b - a for a, b in zip(xs_row, xs_row[1:]))

    # connectors
    long_links, spans = [], []
    for f, n in nodes.items():
        for group in n['groups']:
            for alt in group:
                if alt not in pos:
                    continue
                dy = pos[f][1] - pos[alt][1]
                dx = abs(pos[f][0] - pos[alt][0])
                spans.append(dy)
                if dy > 1 or dx > 2:
                    long_links.append((alt, f, dy, dx))

    # empty rows (rows with no focus at all inside the bounding box are impossible, but
    # a row holding one focus is a sign of a lone straggler)
    thin_rows = sorted(y for y, xs_row in rows.items() if len(xs_row) == 1)

    return {
        'focuses': len(nodes), 'width': width, 'height': height, 'fill': fill,
        'overlaps': overlaps, 'too_close': too_close,
        'min_row_gap': min(row_gaps) if row_gaps else 0,
        'long_links': long_links, 'max_row_count': max(len(v) for v in rows.values()),
        'rows': len(rows), 'thin_rows': thin_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', default=None, help='directory holding the pre-change copies')
    args = ap.parse_args()

    for name, path in TREES:
        old = os.path.join(args.baseline, os.path.basename(path)) if args.baseline else None
        cur = measure(parse(path))
        line = ('%-24s %3d focuses  %3dx%-2d  fill %4.1f%%  min gap %d  long links %2d  rows %d'
                % (name, cur['focuses'], cur['width'], cur['height'], cur['fill'] * 100,
                   cur['min_row_gap'], len(cur['long_links']), cur['rows']))
        print(line)
        if cur['overlaps']:
            print('   OVERLAPS:', list(cur['overlaps'].items())[:3])
        if cur['too_close']:
            print('   ONE COLUMN APART:', cur['too_close'][:3])
        if cur['long_links']:
            print('   LONG LINKS:', cur['long_links'][:4])
        if old and os.path.exists(old):
            before = measure(parse(old))
            print('   before: %3dx%-2d fill %4.1f%%  min gap %d  long links %2d  rows %d'
                  % (before['width'], before['height'], before['fill'] * 100,
                     before['min_row_gap'], len(before['long_links']), before['rows']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
