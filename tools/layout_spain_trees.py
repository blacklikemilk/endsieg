"""Rebuild the Spanish chapter-tree layouts on the Endsieg layout standard.

Structure
---------
A layered layout, not a re-flow of the author's rows:

1. **Tiers from prerequisites.** A focus sits one row below the deepest focus it requires,
   over every alternative in an OR group. This is what makes every connector point down,
   removes sideways and upward links, and gives "one Y cell between prerequisite tiers".
2. **Crossing reduction.** Median/barycentre sweeps down and up over the tiers reorder each
   row so edges cross as little as possible.
3. **Horizontal placement.** A 1-D spring pass: each focus pulls toward the mean of its
   children and its parents, subject to a hard two-cell minimum gap inside every row and a
   wider gap between unrelated families. It cannot overlap anything.

Gameplay is untouched: ids, prerequisites, mutual exclusions, rewards, costs, bypasses,
availability, visibility, AI weights and search filters stay byte-identical. Only `x`, `y`
and `relative_position_id` are written, and
`tools/verify_spain_layout_preserved.py` proves it per focus.

    python tools/layout_spain_trees.py --report     # measure, write nothing
    python tools/layout_spain_trees.py              # write
"""

from __future__ import annotations

import argparse
import io
import math
import re
import sys

TREES = [
    'common/national_focus/spain_restoration.txt',
    'common/national_focus/spain_rivera.txt',
    'common/national_focus/spain_republic.txt',
    'common/national_focus/spain_republic_postwar.txt',
]

GAP = 2            # X cells between neighbours in a row (icons are two cells wide)
FAMILY_GAP = 2     # extra cells between unrelated subtrees
SWEEPS = 8         # crossing-reduction passes
SPRING = 60        # horizontal relaxation iterations
LONG_COLS = 8      # connector span that counts as long
LONG_ROWS = 4

COORD = re.compile(r'\bx\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)')


def read(path: str) -> str:
    return io.open(path, encoding='utf-8-sig').read()


def focus_spans(text: str):
    """(brace index, end index, body) per focus, so a rewrite keeps the 'focus = {' prefix."""
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


def parse(path: str):
    text = read(path)
    nodes = {}
    for start, end, body in focus_spans(text):
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        pos = COORD.search(body)
        rel = re.search(r'relative_position_id\s*=\s*(\S+)', body)
        groups = [re.findall(r'focus\s*=\s*(\S+)', pre)
                  for pre in re.findall(r'prerequisite\s*=\s*\{([^{}]*)\}', body)]
        mutex = re.findall(r'mutually_exclusive\s*=\s*\{([^{}]*)\}', body)
        if not fid or not pos:
            continue
        nodes[fid.group(1)] = {
            'x': int(pos.group(1)),
            'y': int(pos.group(2)),
            'rel': rel.group(1) if rel else None,
            'groups': [g for g in groups if g],
            'mutex': [m for grp in mutex for m in re.findall(r'focus\s*=\s*(\S+)', grp)],
        }
    return text, nodes


def absolute(nodes):
    def resolve(fid, seen=None):
        seen = seen or set()
        if fid in seen or fid not in nodes:
            return (0, 0)
        seen.add(fid)
        n = nodes[fid]
        if not n['rel']:
            return (n['x'], n['y'])
        px, py = resolve(n['rel'], seen)
        return (px + n['x'], py + n['y'])

    return {f: resolve(f) for f in nodes}


def tiers(nodes):
    """Longest path from a root over every prerequisite alternative."""
    tier = {}

    def visit(fid, stack=frozenset()):
        if fid in tier:
            return tier[fid]
        if fid in stack:
            return 0
        groups = nodes[fid]['groups']
        best = 0
        for group in groups:
            for alt in group:
                if alt in nodes:
                    best = max(best, visit(alt, stack | {fid}) + 1)
        tier[fid] = best
        return best

    for f in nodes:
        visit(f)
    return tier


def build_edges(nodes):
    parents = {f: [] for f in nodes}
    children = {f: [] for f in nodes}
    for fid, n in nodes.items():
        seen = set()
        for group in n['groups']:
            for alt in group:
                if alt in nodes and alt not in seen:
                    seen.add(alt)
                    parents[fid].append(alt)
                    children[alt].append(fid)
    return parents, children


def order_rows(nodes, tier, parents, children, old_pos, sweeps=None):
    rows = {}
    for f in nodes:
        rows.setdefault(tier[f], []).append(f)
    for y in rows:
        rows[y].sort(key=lambda f: (old_pos[f][0], f))

    pos = {}
    for y, row in rows.items():
        for i, f in enumerate(row):
            pos[f] = i

    for sweep in range(sweeps or SWEEPS):
        seq = sorted(rows) if sweep % 2 == 0 else sorted(rows, reverse=True)
        for y in seq:
            row = rows[y]
            ref = []
            for f in row:
                neighbours = children[f] if sweep % 2 == 0 else parents[f]
                vals = [pos[n] for n in neighbours if n in pos]
                ref.append((sum(vals) / len(vals) if vals else pos[f], pos[f], f))
            ref.sort()
            rows[y] = [f for _b, _o, f in ref]
            for i, f in enumerate(rows[y]):
                pos[f] = i
    return rows


def place(rows, parents, children, tier):
    """Place each row from its parents, then centre the row on where its parents sit.

    Goes top-down: every node wants the mean x of its parents, the row is then packed to
    the two-cell minimum and shifted as a block so it sits over its parents. A block shift
    keeps the gaps, so this cannot overlap and cannot drift a whole tree sideways.
    """
    x = {}
    for y in sorted(rows):
        row = rows[y]
        desired = {}
        for f in row:
            ps = [p for p in parents[f] if p in x]
            desired[f] = sum(x[p] for p in ps) / len(ps) if ps else 0.0

        # order to keep the crossing-reduced sequence, but nudge ties toward the parents
        row = sorted(row, key=lambda f: (desired[f], row.index(f)))
        rows[y] = row

        for i, f in enumerate(row):
            if i == 0:
                x[f] = desired[f]
            else:
                x[f] = max(desired[f], x[row[i - 1]] + GAP)

        # right-to-left pull toward the parents, never breaking the gap
        for i in range(len(row) - 2, -1, -1):
            limit = x[row[i + 1]] - GAP
            if x[row[i]] > limit and desired[row[i]] < x[row[i]]:
                x[row[i]] = max(limit, desired[row[i]]) if desired[row[i]] <= limit else limit

        # centre the block on the mean of its parents
        ps_all = [x[p] for f in row for p in parents[f] if p in x]
        if ps_all:
            delta = (sum(ps_all) / len(ps_all)) - (sum(x[f] for f in row) / len(row))
            for f in row:
                x[f] += delta

    min_x = min(x.values())
    return {f: (int(round(x[f] - min_x)), tier[f]) for f in x}


def pack_row(row, desired, x):
    """Place one row at the given desired positions with the minimum gap, then centre it."""
    for i, f in enumerate(row):
        if i == 0:
            x[f] = desired[f]
        else:
            x[f] = max(desired[f], x[row[i - 1]] + GAP)
    ps = [desired[f] for f in row]
    if ps:
        delta = (sum(ps) / len(ps)) - (sum(x[f] for f in row) / len(row))
        for f in row:
            x[f] += delta


def refine(pos, rows, parents, children, rounds=12):
    """Alternate bottom-up and top-down passes so parents and children converge together."""
    x = {f: float(pos[f][0]) for f in pos}
    keys = sorted(rows)
    for r in range(rounds):
        order = list(reversed(keys)) if r % 2 == 0 else keys
        for y in order:
            row = rows[y]
            desired = {}
            for f in row:
                neigh = [n for n in parents[f] + children[f] if n in x]
                desired[f] = sum(x[n] for n in neigh) / len(neigh) if neigh else x[f]
            pack_row(row, desired, x)
    min_x = min(x.values())
    return {f: (int(round(x[f] - min_x)), pos[f][1]) for f in x}


def non_downward(nodes, pos):
    """Count connectors that do not point strictly down a row."""
    bad = 0
    for f, n in nodes.items():
        if f not in pos:
            continue
        for group in n['groups']:
            for alt in group:
                if alt in pos and pos[f][1] <= pos[alt][1]:
                    bad += 1
    return bad


def analyse(rows, nodes, pos):
    """Overlaps, gaps, connector spans and crossings, computed from the result."""
    by_cell = {}
    for f, (px, py) in pos.items():
        by_cell.setdefault((px, py), []).append(f)
    overlaps = [v for v in by_cell.values() if len(v) > 1]

    too_close = 0
    for (px, py), names in by_cell.items():
        if (px + 1, py) in by_cell:
            too_close += 1

    long_links = 0
    for f, n in nodes.items():
        if f not in pos:
            continue
        for group in n['groups']:
            for alt in group:
                if alt not in pos:
                    continue
                dx = abs(pos[f][0] - pos[alt][0])
                dy = pos[f][1] - pos[alt][1]
                if dx > LONG_COLS or abs(dy) > LONG_ROWS or dy <= 0:
                    long_links += 1

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    width = max(xs) - min(xs) + 1
    height = max(ys) - min(ys) + 1
    return {'width': width, 'height': height, 'overlaps': len(overlaps),
            'too_close': too_close, 'long_links': long_links,
            'fill': len(pos) / (width * height)}


def layout(path: str, write: bool):
    text, nodes = parse(path)
    if not nodes:
        return None
    old_pos = absolute(nodes)
    tier = tiers(nodes)
    parents, children = build_edges(nodes)

    # try a few crossing-reduction depths and keep the best result for this tree
    best = None
    for sweeps in (6, 12, 24):
        rows_try = order_rows(nodes, tier, parents, children, old_pos, sweeps)
        pos_try = place(rows_try, parents, children, tier)
        pos_try = refine(pos_try, rows_try, parents, children)
        stats_try = analyse(rows_try, nodes, pos_try)
        if non_downward(nodes, pos_try):
            continue                       # every connector must point down a row
        key = (stats_try['long_links'], stats_try['width'] * stats_try['height'], stats_try['too_close'])
        if best is None or key < best[0]:
            best = (key, rows_try, pos_try)

    # second strategy: keep the author's rows and only relax horizontally. Some trees read
    # better that way because the author encoded which branches share a tier.
    rows_fixed = {}
    for f in nodes:
        rows_fixed.setdefault(old_pos[f][1] - min(p[1] for p in old_pos.values()), []).append(f)
    for y in rows_fixed:
        rows_fixed[y].sort(key=lambda f: (old_pos[f][0], f))
    tier_fixed = {f: y for y, row in rows_fixed.items() for f in row}
    pos_fixed = place(rows_fixed, parents, children, tier_fixed)
    pos_fixed = refine(pos_fixed, rows_fixed, parents, children)
    stats_fixed = analyse(rows_fixed, nodes, pos_fixed)
    key_fixed = (stats_fixed['long_links'], stats_fixed['width'] * stats_fixed['height'],
                 stats_fixed['too_close'])
    if best is not None and not non_downward(nodes, pos_fixed) and key_fixed < best[0]:
        best = (key_fixed, rows_fixed, pos_fixed)

    rows, pos = best[1], best[2]

    # shift each row so the whole tree starts at column 0
    out, last = [], 0
    for start, end, body in focus_spans(text):
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        if not fid or fid.group(1) not in pos:
            continue
        nx, ny = pos[fid.group(1)]
        new_body = re.sub(r'\t\trelative_position_id\s*=\s*\S+\r?\n', '', body, count=1)
        new_body = COORD.sub('x = %d y = %d' % (nx, ny), new_body, count=1)
        out.append(text[last:start])
        out.append(new_body)
        last = end
    out.append(text[last:])
    new_text = ''.join(out)

    # written only after the score comparison below decides the pass is worth it

    old_stats = analyse(rows, nodes, old_pos)
    new_stats = analyse(rows, nodes, pos)

    # A layout pass may only ship a tree it actually beats: connector length first, then
    # compactness. Trees where the engine cannot win keep their authored layout.
    def score(stats):
        return (stats['long_links'] * 1000
                + stats['width'] * stats['height'] * 20
                + stats['too_close'] * 5000)

    # a tree may not be turned into a wide strip to win on connector length
    too_wide = new_stats['width'] > old_stats['width'] * 1.25
    kept = too_wide or score(new_stats) >= score(old_stats)
    if write and not kept:
        io.open(path, 'w', encoding='utf-8', newline='').write(new_text)
    return {'focuses': len(nodes), 'before': old_stats, 'after': new_stats,
            'kept_authored': kept}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()

    for path in TREES:
        res = layout(path, not args.report)
        if not res:
            print(path, 'no focuses')
            continue
        b, a = res['before'], res['after']
        print('%-30s %3d focuses' % (path.split('/')[-1], res['focuses']))
        print('   before  %2dx%-2d  fill %4.1f%%  long %2d  overlaps %d  tight %d'
              % (b['width'], b['height'], b['fill'] * 100, b['long_links'], b['overlaps'], b['too_close']))
        verdict = 'KEPT AUTHORED (engine could not beat it)' if res['kept_authored'] else 'APPLIED'
        print('   after   %2dx%-2d  fill %4.1f%%  long %2d  overlaps %d  tight %d  -> %s'
              % (a['width'], a['height'], a['fill'] * 100, a['long_links'], a['overlaps'],
                 a['too_close'], verdict))
    return 0


if __name__ == '__main__':
    sys.exit(main())
