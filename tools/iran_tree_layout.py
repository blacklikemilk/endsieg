"""Lay out an Iran focus chapter as separated sections, not one block.

Each of the chapter's roots is treated as a section. Sections are laid side by
side with a visible gutter, and each is packed internally at vanilla's two-unit
spacing, so the tree reads as four or five distinct branches rather than a single
wall of focuses. A final per-row sweep guarantees no two focuses in a row are
closer than two units.

Usage:
  python tools/iran_tree_layout.py            # report widths and section counts
  python tools/iran_tree_layout.py --apply    # write coordinates
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
GAP = 2          # vanilla's dominant horizontal spacing
GUTTER = 4       # empty space between sections


def read(path: str) -> str:
    with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def parse(text: str) -> list[dict]:
    out = []
    for m in re.finditer(r"\bfocus = \{", text):
        start = m.end() - 1
        depth = 0
        i = start
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
        body = text[start : i + 1]
        fid = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+)", body)
        if not fid:
            continue
        x = re.search(r"(?<![a-z_])x\s*=\s*(-?\d+)", body)
        y = re.search(r"(?<![a-z_])y\s*=\s*(-?\d+)", body)
        rel = re.search(r"relative_position_id\s*=\s*([A-Za-z0-9_]+)", body)
        pre = re.search(r"prerequisite\s*=\s*\{", body)
        prereq: list[str] = []
        if pre:
            seg = body[pre.start() : body.find("}", pre.start()) + 1]
            prereq = re.findall(r"focus\s*=\s*([A-Za-z0-9_]+)", seg)
        out.append(
            {
                "id": fid.group(1),
                "x": int(x.group(1)) if x else 0,
                "y": int(y.group(1)) if y else 0,
                "start": start,
                "end": i,
                "body": body,
                "rel": rel.group(1) if rel else "",
                "pre": prereq,
                "order": len(out),
            }
        )
    return out


def sectional(focuses: list[dict]) -> tuple[dict[str, tuple[int, int]], int]:
    by = {f["id"]: f for f in focuses}
    parent: dict[str, str] = {}
    for f in focuses:
        cand = [p for p in f["pre"] if p in by]
        parent[f["id"]] = cand[0] if cand else (f["rel"] if f["rel"] in by else "")

    def root_of(fid: str, depth: int = 0) -> str:
        p = parent.get(fid, "")
        return fid if (not p or depth > 60) else root_of(p, depth + 1)

    def depth_of(fid: str, depth: int = 0) -> int:
        p = parent.get(fid, "")
        return 0 if not p else 1 + depth_of(p, depth + 1)

    depth = {f["id"]: depth_of(f["id"]) for f in focuses}
    groups: dict[str, list[str]] = defaultdict(list)
    for f in focuses:
        groups[root_of(f["id"])].append(f["id"])

    placed: dict[str, tuple[int, int]] = {}
    cursor = 0
    for root in sorted(groups, key=lambda r: by[r]["order"]):
        ids = set(groups[root])
        kids: dict[str, list[str]] = defaultdict(list)
        for i in ids:
            if parent[i] in ids:
                kids[parent[i]].append(i)
        for k in kids:
            kids[k].sort(key=lambda i: by[i]["order"])
        order: list[str] = []

        def walk(i: str) -> None:
            order.append(i)
            for c in kids[i]:
                walk(c)

        walk(root)
        occupied: dict[int, set[int]] = {}
        local: dict[str, tuple[int, int]] = {}
        for i in order:
            row = depth[i]
            used = occupied.setdefault(row, set())
            anchor = local[parent[i]][0] if parent.get(i) in local else 0
            col = None
            for step in range(0, 160):
                for sign in ((0,) if step == 0 else (1, -1)):
                    cand = anchor + sign * GAP
                    if cand not in used:
                        col = cand
                        break
                if col is not None:
                    break
            if col is None:
                col = (max(used) + GAP) if used else 0
            local[i] = (col, row)
            used.add(col)
        lo = min(v[0] for v in local.values())
        hi = max(v[0] for v in local.values())
        for i, (lx, ly) in local.items():
            placed[i] = (lx - lo + cursor, ly)
        cursor += (hi - lo) + GUTTER + GAP

    # per-row sweep: the guarantee that nothing ends up closer than GAP
    rows: dict[int, list[str]] = defaultdict(list)
    for i, (_x, y) in placed.items():
        rows[y].append(i)
    for y, ids in rows.items():
        ids.sort(key=lambda i: placed[i][0])
        last = None
        for i in ids:
            x, _ = placed[i]
            if last is not None and x - last < GAP:
                x = last + GAP
            placed[i] = (x, y)
            last = x
    return placed, len(groups)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.getcwd())
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    mod = os.path.abspath(args.mod)

    for rel in CHAPTERS:
        path = os.path.join(mod, rel.replace("/", os.sep))
        if not os.path.exists(path):
            continue
        text = read(path)
        focuses = parse(text)
        placed, sections = sectional(focuses)

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

        check = parse(new)
        cells: dict[tuple[int, int], list[str]] = defaultdict(list)
        for f in check:
            cells[(f["x"], f["y"])].append(f["id"])
        stacked = [c for c, v in cells.items() if len(v) > 1]
        tight = sum(
            1
            for f in check
            for g in check
            if f["y"] == g["y"] and 0 < g["x"] - f["x"] < GAP
        )
        width = max(f["x"] for f in check) + 1
        height = max(f["y"] for f in check) + 1
        print(
            f"{os.path.basename(rel)}: {len(focuses)} focuses, {sections} sections, "
            f"{width} cols ({width * 96}px) x {height} rows, stacked={len(stacked)}, too-close={tight}"
        )
        if args.apply and not stacked and not tight and new.count("{") == text.count("{"):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
            print("   applied")
        elif args.apply:
            print("   refused: layout not clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
