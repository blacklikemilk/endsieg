"""Render a Spanish focus tree from its script, for layout review without the game.

Draws one box per focus on the engine's grid (96 x 130 px per cell), connector lines for
every prerequisite, and colours each focus by the branch family it descends from. It is a
layout tool, not an engine render: it cannot show icons, tooltips or in-game clipping, and
it says nothing about whether a focus is reachable in play.

    python tools/render_spain_tree.py common/national_focus/spain_restoration.txt out.html
"""

from __future__ import annotations

import io
import re
import sys

CELL_W, CELL_H = 96, 130
BOX_W, BOX_H = 78, 96

FAMILY_COLOURS = [
    '#8a6d3b', '#3b6d8a', '#6d3b8a', '#3b8a5d',
    '#8a3b4b', '#5d8a3b', '#8a7b3b', '#3b4b8a',
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

    for f in nodes:
        nodes[f]['abs'] = absolute(f)
    return nodes


def render(path: str, out: str) -> None:
    nodes = parse(path)
    if not nodes:
        print('no focuses in', path)
        return

    xs = [n['abs'][0] for n in nodes.values()]
    ys = [n['abs'][1] for n in nodes.values()]
    min_x, min_y = min(xs), min(ys)
    width = (max(xs) - min_x + 1) * CELL_W
    height = (max(ys) - min_y + 1) * CELL_H

    # family = top-level ancestor, by walking the first prerequisite link
    family = {}

    def fam(fid, seen=None):
        seen = seen or set()
        if fid in family:
            return family[fid]
        if fid in seen:
            return fid
        seen.add(fid)
        groups = nodes[fid]['groups']
        alts = [a for g in groups for a in g if a in nodes]
        if not alts:
            family[fid] = fid
        else:
            family[fid] = fam(alts[0], seen)
        return family[fid]

    for f in nodes:
        fam(f)

    roots = sorted({family[f] for f in nodes})
    colour = {r: FAMILY_COLOURS[i % len(FAMILY_COLOURS)] for i, r in enumerate(roots)}

    def px(fid):
        x, y = nodes[fid]['abs']
        return ((x - min_x) * CELL_W, (y - min_y) * CELL_H)

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">' % (width, height),
           '<rect width="100%%" height="100%%" fill="#1b1a17"/>']

    # connectors first, so boxes sit on top
    for fid, n in nodes.items():
        cx, cy = px(fid)
        for group in n['groups']:
            for alt in group:
                if alt not in nodes:
                    continue
                ax, ay = px(alt)
                x1, y1 = ax + BOX_W / 2, ay + BOX_H
                x2, y2 = cx + BOX_W / 2, cy
                svg.append('<path d="M%.1f %.1f L%.1f %.1f" stroke="#6b6152" stroke-width="2" fill="none"/>'
                           % (x1, y1, x2, y2))

    for fid, n in nodes.items():
        cx, cy = px(fid)
        col = colour[family[fid]]
        svg.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="4" fill="%s" stroke="#0f0e0c"/>'
                   % (cx, cy, BOX_W, BOX_H, col))
        label = fid.replace('SPR1_', '').replace('SPR2_', '').replace('SPR3_', '').replace('SPR4_', '')
        label = label.replace('_', ' ')
        words = label.split()
        lines, cur = [], ''
        for w in words:
            if len(cur) + len(w) + 1 > 13:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + ' ' + w).strip()
        if cur:
            lines.append(cur)
        for i, line in enumerate(lines[:4]):
            svg.append('<text x="%.1f" y="%.1f" fill="#f4efe2" font-family="Segoe UI" font-size="9">%s</text>'
                       % (cx + 6, cy + 16 + i * 11, line))

    svg.append('</svg>')
    html = ('<!doctype html><meta charset="utf-8">'
            '<body style="margin:0;background:#141310">%s</body>' % ''.join(svg))
    io.open(out, 'w', encoding='utf-8', newline='').write(html)
    print('%s -> %s  (%d focuses, %d x %d px)'
          % (path.split('/')[-1], out, len(nodes), width, height))


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2])
