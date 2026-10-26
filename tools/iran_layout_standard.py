"""Rebuild an Iran chapter layout to the Endsieg focus-layout standard.

Rules implemented (from hoi4-focus-trees/references/layout-rules.md):

  * two X cells between same-row siblings
  * one Y cell between prerequisite tiers
  * roughly four X cells between unrelated families (subtrees under different roots)
  * parents centred over their children, so forks are balanced and convergences
    meet in the middle instead of stepping sideways
  * no duplicate cells, and every prerequisite parent strictly above its child

Only x, y and relative_position_id are touched. Every other field is compared
against a snapshot before the file is written, and a layout that fails any check
is refused.

Usage:
  python tools/iran_layout_standard.py --snapshot <dir>            # report
  python tools/iran_layout_standard.py --snapshot <dir> --apply    # write
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from collections import defaultdict

CHAPTERS = [
    "common/national_focus/iran_ww1.txt",
    "common/national_focus/iran_interwar.txt",
    "common/national_focus/iran_ww2.txt",
]
SIBLING = 2
TIER = 1
FAMILY = 4


def read(path: str) -> str:
    with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def parse(text: str) -> list[dict]:
    out: list[dict] = []
    for m in re.finditer(r"\bfocus = \{", text):
        start = m.end() - 1
        depth = 0
        end = start
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        body = text[start : end + 1]
        fid = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+)", body)
        if not fid:
            continue
        rx = re.search(r"(?<![a-z_])x\s*=\s*(-?\d+)", body)
        ry = re.search(r"(?<![a-z_])y\s*=\s*(-?\d+)", body)
        rel = re.search(r"relative_position_id\s*=\s*([A-Za-z0-9_]+)", body)
        prereq: list[str] = []
        pm = re.search(r"prerequisite\s*=\s*\{", body)
        if pm:
            seg = body[pm.start() : body.find("}", pm.start()) + 1]
            prereq = re.findall(r"focus\s*=\s*([A-Za-z0-9_]+)", seg)
        out.append(
            {
                "id": fid.group(1),
                "x": int(rx.group(1)) if rx else 0,
                "y": int(ry.group(1)) if ry else 0,
                "start": start,
                "end": end,
                "body": body,
                "rel": rel.group(1) if rel else "",
                "pre": prereq,
                "order": len(out),
            }
        )
    return out


def signature(body: str) -> str:
    """Everything except the three layout fields."""
    text = re.sub(r"(?m)^\t*relative_position_id\s*=\s*[A-Za-z0-9_]+\s*\n", "", body)
    text = re.sub(r"(?<![a-z_])x\s*=\s*-?\d+", "x", text, count=1)
    text = re.sub(r"(?<![a-z_])y\s*=\s*-?\d+", "y", text, count=1)
    return " ".join(text.split())


def tidy(focuses: list[dict]) -> tuple[dict[str, tuple[int, int]], int]:
    by = {f["id"]: f for f in focuses}
    parent: dict[str, str] = {}
    for f in focuses:
        cand = [p for p in f["pre"] if p in by]
        parent[f["id"]] = cand[0] if cand else (f["rel"] if f["rel"] in by else "")

    def root_of(fid: str, depth: int = 0) -> str:
        p = parent.get(fid, "")
        return fid if (not p or depth > 60) else root_of(p, depth + 1)

    def depth_of(fid: str, seen: frozenset[str] = frozenset()) -> int:
        """Longest path from a root, counting every prerequisite.

        Using only one parent puts a focus above a prerequisite that belongs to
        another family, which the layout rules forbid.
        """
        if fid in seen:
            return 0
        parents = [p for p in (by[fid]["pre"] if fid in by else []) if p in by]
        if not parents:
            return 0
        return 1 + max(depth_of(p, seen | {fid}) for p in parents)

    depth = {f["id"]: depth_of(f["id"]) for f in focuses}
    groups: dict[str, list[str]] = defaultdict(list)
    for f in focuses:
        groups[root_of(f["id"])].append(f["id"])

    placed: dict[str, tuple[int, int]] = {}
    cursor = 0
    # Order families so the ones that share prerequisites sit next to each other.
    # Pure definition order produced 45 cross-family lines longer than eight cells
    # in the interwar chapter; affinity ordering shortens them.
    def affinity_order(roots: list[str]) -> list[str]:
        cross: dict[tuple[str, str], int] = defaultdict(int)
        fam = {fid: r for r in roots for fid in groups[r]}
        for f in focuses:
            for p in f["pre"]:
                if p in fam and f["id"] in fam and fam[p] != fam[f["id"]]:
                    cross[(fam[p], fam[f["id"]])] += 1
        remaining = sorted(roots, key=lambda r: by[r]["order"])
        ordered = [remaining.pop(0)]
        while remaining:
            def score(r: str) -> tuple[int, int]:
                links = sum(cross.get((o, r), 0) + cross.get((r, o), 0) for o in ordered)
                return (-links, by[r]["order"])
            ordered.append(min(remaining, key=score))
            remaining.remove(ordered[-1])
        return ordered

    for root in affinity_order(list(groups)):
        ids = set(groups[root])
        kids: dict[str, list[str]] = defaultdict(list)
        for i in ids:
            if parent[i] in ids:
                kids[parent[i]].append(i)
        for k in kids:
            kids[k].sort(key=lambda i: by[i]["order"])

        slot = [0]
        row_taken: dict[int, set[int]] = {}

        def free_col(row: int, start: int) -> int:
            """Nearest free cell to `start`, searched symmetrically.

            Scanning only rightwards pushed a parent off-centre whenever the
            ideal cell was taken, which showed up as a lopsided fork.
            """
            used = row_taken.setdefault(row, set())
            step = 0
            while True:
                for cand in ((start,) if step == 0 else (start + step, start - step)):
                    if cand >= 0 and cand not in used:
                        used.add(cand)
                        return cand
                step += SIBLING

        def place(node: str) -> int:
            children = kids.get(node, [])
            if not children:
                col = free_col(depth[node], slot[0])
                slot[0] = col + SIBLING
                placed[node] = (col, depth[node])
                return col
            cols = [place(c) for c in children]
            centre = (min(cols) + max(cols)) // 2
            centre -= centre % SIBLING
            col = free_col(depth[node], centre)
            placed[node] = (col, depth[node])
            return col

        place(root)
        lo = min(placed[i][0] for i in ids)
        hi = max(placed[i][0] for i in ids)
        for i in ids:
            x, y = placed[i]
            placed[i] = (x - lo + cursor, y)
        cursor += (hi - lo) + FAMILY + SIBLING
    return placed, len(groups)


def verify(focuses: list[dict], placed: dict[str, tuple[int, int]]) -> list[str]:
    problems: list[str] = []
    cells: dict[tuple[int, int], list[str]] = defaultdict(list)
    for fid, xy in placed.items():
        cells[xy].append(fid)
    for cell, ids in cells.items():
        if len(ids) > 1:
            problems.append(f"stacked cell {cell}: {ids}")
    rows: dict[int, list[int]] = defaultdict(list)
    for _fid, (x, y) in placed.items():
        rows[y].append(x)
    for y, xs in rows.items():
        xs.sort()
        for a, b in zip(xs, xs[1:]):
            if b - a < SIBLING:
                problems.append(f"row {y}: spacing {b - a} at x={a}")
    for f in focuses:
        for p in f["pre"]:
            if p in placed and placed[p][1] >= placed[f["id"]][1]:
                problems.append(f"{f['id']} not below prerequisite {p}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.getcwd())
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    mod = os.path.abspath(args.mod)
    snap = os.path.abspath(args.snapshot)

    for rel in CHAPTERS:
        path = os.path.join(mod, rel.replace("/", os.sep))
        name = os.path.basename(path)
        if not os.path.exists(path):
            continue
        text = read(path)
        baseline = read(os.path.join(snap, name))
        before = {f["id"]: signature(f["body"]) for f in parse(baseline)}
        focuses = parse(text)
        placed, families = tidy(focuses)

        problems = verify(focuses, placed)
        after = {f["id"]: signature(f["body"]) for f in focuses}
        if set(before) != set(after):
            problems.append("focus id set differs from the snapshot")
        changed = [fid for fid in before if fid in after and before[fid] != after[fid]]
        if changed:
            problems.append(f"gameplay differs from the snapshot: {changed[:4]}")

        out, last = [], 0
        for f in focuses:
            out.append(text[last : f["start"]])
            x, y = placed[f["id"]]
            body = re.sub(r"(?m)^\t*relative_position_id\s*=\s*[A-Za-z0-9_]+\s*\n", "", f["body"], count=1)
            body = re.sub(r"(?<![a-z_])x\s*=\s*-?\d+", f"x = {x}", body, count=1)
            body = re.sub(r"(?<![a-z_])y\s*=\s*-?\d+", f"y = {y}", body, count=1)
            out.append(body)
            last = f["end"] + 1
        out.append(text[last:])
        new = "".join(out)

        width = max(p[0] for p in placed.values()) + 1
        height = max(p[1] for p in placed.values()) + 1
        print(f"{name}: {len(focuses)} focuses, {families} families, {width} cols ({width * 96}px) x {height} rows, problems={len(problems)}")
        for p in problems[:4]:
            print(f"   ! {p}")

        if args.apply and not problems and new.count("{") == text.count("{"):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
            print("   applied")
        elif args.apply:
            print("   refused")
    return 0


if __name__ == "__main__":
    sys.exit(main())
