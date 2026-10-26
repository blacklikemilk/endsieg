"""Re-layout an Iran focus chapter so it renders as one compact block.

The trees were laid out with `relative_position_id` offsets that also carried an
absolute-looking x, so positions accumulated down each chain: iran_ww1 spans 44
grid units (~4,200 px) and iran_interwar 53 (~5,100 px) against roughly 20 for a
vanilla major. Branches exist, but they sit thousands of pixels from the spine.

This computes a fresh absolute layout and writes it back:

  * rows follow the prerequisite depth of each focus
  * a focus is placed as close to its parent's column as a free cell allows
  * `relative_position_id` is removed so nothing accumulates again
  * empty columns are dropped

Usage:
  python tools/relayout_iran_trees.py            # report only
  python tools/relayout_iran_trees.py --apply    # write the new coordinates
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys

CHAPTERS = [
    "common/national_focus/iran_ww1.txt",
    "common/national_focus/iran_interwar.txt",
    "common/national_focus/iran_ww2.txt",
]


def read(path: str) -> str:
    with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def brace_block(text: str, open_index: int) -> int:
    depth = 0
    for i in range(open_index, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def parse(text: str) -> list[dict]:
    out = []
    for m in re.finditer(r"\bfocus = \{", text):
        start = m.end() - 1
        end = brace_block(text, start)
        body = text[start : end + 1]
        fid = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+)", body)
        if not fid:
            continue
        prereq_m = re.search(r"prerequisite\s*=\s*\{", body)
        prereq: list[str] = []
        if prereq_m:
            seg = body[prereq_m.start() : brace_block(body, prereq_m.end() - 1) + 1]
            prereq = re.findall(r"focus\s*=\s*([A-Za-z0-9_]+)", seg)
        rel = re.search(r"relative_position_id\s*=\s*([A-Za-z0-9_]+)", body)
        rx = re.search(r"(?<![a-z_])x\s*=\s*(-?\d+)", body)
        ry = re.search(r"(?<![a-z_])y\s*=\s*(-?\d+)", body)
        out.append(
            {
                "id": fid.group(1),
                "x": int(rx.group(1)) if rx else 0,
                "y": int(ry.group(1)) if ry else 0,
                "start": start,
                "end": end,
                "body": body,
                "prereq": prereq,
                "rel": rel.group(1) if rel else "",
            }
        )
    return out


def depths(focuses: list[dict]) -> dict[str, int]:
    by_id = {f["id"]: f for f in focuses}
    memo: dict[str, int] = {}

    def depth(fid: str, seen: frozenset[str] = frozenset()) -> int:
        if fid in memo:
            return memo[fid]
        f = by_id.get(fid)
        if not f or not f["prereq"] or fid in seen:
            memo[fid] = 0
            return 0
        parents = [p for p in f["prereq"] if p in by_id and p not in seen]
        memo[fid] = 1 + max((depth(p, seen | {fid}) for p in parents), default=-1) if parents else 0
        return memo[fid]

    return {f["id"]: depth(f["id"]) for f in focuses}


def layout(focuses: list[dict]) -> dict[str, tuple[int, int]]:
    by_id = {f["id"]: f for f in focuses}
    depth = depths(focuses)

    # parent: the prerequisite that sits directly above, else the relative target
    parent: dict[str, str] = {}
    for f in focuses:
        up = [p for p in f["prereq"] if p in by_id and depth[p] == depth[f["id"]] - 1]
        if up:
            parent[f["id"]] = up[0]
        elif f["rel"] in by_id:
            parent[f["id"]] = f["rel"]

    def original_x(f: dict, seen: int = 0) -> int:
        """Absolute x under the old relative layout: the author's left-right intent."""
        if not f["rel"] or f["rel"] not in by_id or seen > 40:
            return f["x"]
        return f["x"] + original_x(by_id[f["rel"]], seen + 1)

    occupied: dict[int, set[int]] = {}
    placed: dict[str, tuple[int, int]] = {}

    def original_x(f: dict, seen: int = 0) -> int:
        """Absolute x under the old relative layout: the author's left-right intent."""
        if not f["rel"] or f["rel"] not in by_id or seen > 40:
            return f["x"]
        return f["x"] + original_x(by_id[f["rel"]], seen + 1)

    orig = {f["id"]: original_x(f) for f in focuses}
    rows: dict[int, list[dict]] = {}
    for f in focuses:
        rows.setdefault(depth[f["id"]], []).append(f)

    # Place one row at a time, and within a row keep children of the same parent
    # adjacent: ordering by the parent's already-placed column is what stops the
    # long crossing edges a purely global left-to-right order produces.
    for row in sorted(rows):
        def key(f: dict) -> tuple[int, int, str]:
            par = parent.get(f["id"], "")
            anchor = placed[par][0] if par in placed else orig[f["id"]]
            return (anchor, orig[f["id"]], f["id"])

        used = occupied.setdefault(row, set())
        for f in sorted(rows[row], key=key):
            par = parent.get(f["id"], "")
            anchor = placed[par][0] if par in placed else 0
            col = None
            for step in range(0, 80):
                for sgn in ((0,) if step == 0 else (1, -1)):
                    cand = anchor + sgn * step
                    if cand not in used:
                        col = cand
                        break
                if col is not None:
                    break
            placed[f["id"]] = (col, row)
            used.add(col)

    # drop empty columns so the block is contiguous
    xs = sorted({p[0] for p in placed.values()})
    remap = {x: i for i, x in enumerate(xs)}
    return {fid: (remap[x], y) for fid, (x, y) in placed.items()}


def rewrite(body: str, x: int, y: int) -> str:
    body = re.sub(r"(?m)^\t*relative_position_id\s*=\s*[A-Za-z0-9_]+\s*\n", "", body, count=1)
    if re.search(r"(?<![a-z_])x\s*=\s*-?\d+", body):
        body = re.sub(r"(?<![a-z_])x\s*=\s*-?\d+", f"x = {x}", body, count=1)
    else:
        body = re.sub(r"(\n\t\t)(\S)", rf"\1x = {x}\n\t\t\2", body, count=1)
    if re.search(r"(?<![a-z_])y\s*=\s*-?\d+", body):
        body = re.sub(r"(?<![a-z_])y\s*=\s*-?\d+", f"y = {y}", body, count=1)
    return body


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
        placed = layout(focuses)

        before_xs = [p[0] for p in placed.values()]
        cells = {}
        for fid, xy in placed.items():
            cells.setdefault(xy, []).append(fid)
        collisions = {k: v for k, v in cells.items() if len(v) > 1}

        width = max(before_xs) - min(before_xs)
        height = max(y for _x, y in placed.values())
        print(
            f"{os.path.basename(rel)}: {len(focuses)} focuses -> "
            f"{width + 1} columns x {height + 1} rows "
            f"(~{(width + 1) * 96} x {(height + 1) * 136} px), collisions: {len(collisions)}"
        )

        if args.apply:
            out = []
            last = 0
            for f in focuses:
                out.append(text[last : f["start"]])
                x, y = placed[f["id"]]
                out.append(rewrite(f["body"], x, y))
                last = f["end"] + 1
            out.append(text[last:])
            new = "".join(out)
            if new.count("{") == text.count("{"):
                with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)
                print("   applied")
            else:
                print("   REFUSED: brace count changed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
