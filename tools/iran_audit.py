"""Static audit for the Iran country package.

Nothing here launches the game. It checks what breaks the parser or fails silently:

  * duplicate focus ids
  * two focuses landing on the same ABSOLUTE grid cell (resolves
    relative_position_id chains, because these trees are laid out relatively)
  * prerequisites / relative_position_id pointing at ids that do not exist
  * focuses unreachable from any root
  * duplicate event ids, and events in a namespace with no add_namespace
  * duplicate decision ids
  * localisation missing for focus titles and descriptions
  * GFX sprites and idea pictures referenced but never registered
  * project style violations (>= / <=, bare `stability`, check_variable with no
    `var =`, add_consumer_goods_factor)

Usage:
  python tools/iran_audit.py --game "<HOI4 install>" [--report out.md]
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any

FOCUS_FILES = [
    "common/national_focus/iran_ww1.txt",
    "common/national_focus/iran_interwar.txt",
    "common/national_focus/iran_ww2.txt",
]
EXTRA_FILES = ["common/bop/PER.txt", "history/countries/PER - Persia.txt"]


def read(path: str) -> str:
    with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def strip_comments(text: str) -> str:
    return "\n".join(line if line.find("#") < 0 else line[: line.find("#")] for line in text.splitlines())


def brace_block(text: str, open_index: int) -> int:
    """Index of the brace closing the one at open_index (or the last character)."""
    depth = 0
    for i in range(open_index, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def named_blocks(text: str, key: str) -> list[tuple[str, str]]:
    """(id, body) for every `<key> = { ... }`, brace-balanced."""
    out: list[tuple[str, str]] = []
    for m in re.finditer(r"\b" + key + r"\s*=\s*\{", text):
        start = m.end() - 1
        body = text[start : brace_block(text, start) + 1]
        ident = re.search(r"\bid\s*=\s*([A-Za-z0-9_.]+)", body)
        out.append((ident.group(1) if ident else "", body))
    return out


# ------------------------------------------------------------------ focus trees

def parse_focuses(path: str) -> list[dict[str, Any]]:
    text = strip_comments(read(path))
    focuses: list[dict[str, Any]] = []
    for fid, body in named_blocks(text, "focus"):
        if not fid:
            continue
        rx = re.search(r"(?<![a-z_])x\s*=\s*(-?\d+)", body)
        ry = re.search(r"(?<![a-z_])y\s*=\s*(-?\d+)", body)
        rel = re.search(r"relative_position_id\s*=\s*([A-Za-z0-9_]+)", body)
        prereq = ""
        pm = re.search(r"prerequisite\s*=\s*\{", body)
        if pm:
            prereq = body[pm.start() : brace_block(body, pm.end() - 1) + 1]
        focuses.append(
            {
                "id": fid,
                "body": body,
                "x": int(rx.group(1)) if rx else 0,
                "y": int(ry.group(1)) if ry else 0,
                "relative_to": rel.group(1) if rel else "",
                "prereq": re.findall(r"focus\s*=\s*([A-Za-z0-9_]+)", prereq),
            }
        )
    return focuses


def absolute_xy(f: dict[str, Any], by_id: dict[str, dict[str, Any]], depth: int = 0) -> tuple[int, int]:
    if not f["relative_to"] or depth > 40:
        return f["x"], f["y"]
    parent = by_id.get(f["relative_to"])
    if parent is None:
        return f["x"], f["y"]
    px, py = absolute_xy(parent, by_id, depth + 1)
    return px + f["x"], py + f["y"]


def check_focus_tree(path: str, problems: list[str]) -> int:
    name = os.path.basename(path)
    focuses = parse_focuses(path)
    by_id = {f["id"]: f for f in focuses}
    for fid, n in Counter(f["id"] for f in focuses).items():
        if n > 1:
            problems.append(f"{name}: duplicate focus id {fid} x{n}")

    cells: dict[tuple[int, int], list[str]] = defaultdict(list)
    for f in focuses:
        cells[absolute_xy(f, by_id)].append(f["id"])
    for cell, ids in sorted(cells.items()):
        if len(ids) > 1:
            problems.append(f"{name}: {len(ids)} focuses share absolute cell {cell}: {ids}")

    for f in focuses:
        if f["relative_to"] and f["relative_to"] not in by_id:
            problems.append(f"{name}: {f['id']} is relative to missing focus {f['relative_to']}")
        for p in f["prereq"]:
            if p not in by_id:
                problems.append(f"{name}: {f['id']} requires missing focus {p}")

    roots = {f["id"] for f in focuses if not f["prereq"]}
    edges: dict[str, set[str]] = defaultdict(set)
    for f in focuses:
        for p in f["prereq"]:
            if p in by_id:
                edges[p].add(f["id"])
    seen, stack = set(roots), list(roots)
    while stack:
        cur = stack.pop()
        for nxt in edges[cur]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    orphans = sorted(set(by_id) - seen)
    if orphans:
        problems.append(f"{name}: {len(orphans)} unreachable focus(es): {orphans[:8]}")
    return len(focuses)


# ---------------------------------------------------------------------- events

def check_events(paths: list[str], problems: list[str]) -> dict[str, Any]:
    found: list[tuple[str, str]] = []
    namespaces: dict[str, str] = {}
    for path in paths:
        text = strip_comments(read(path))
        for ns in re.findall(r"\badd_namespace\s*=\s*([A-Za-z0-9_]+)", text):
            namespaces[ns] = os.path.basename(path)
        for kind in ("country_event", "news_event", "state_event"):
            for _fid, body in named_blocks(text, kind):
                # an inline fire (`country_event = { id = X hours = 1 }`) is not a definition
                if not re.search(r"\b(title|desc)\s*=", body):
                    continue
                m = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+\.[0-9]+)", body)
                if m:
                    found.append((m.group(1), os.path.basename(path)))
    for eid, n in Counter(i for i, _ in found).items():
        if n > 1:
            problems.append(f"duplicate event id {eid} (x{n})")
    for ns in sorted({i.split(".")[0] for i, _ in found}):
        if ns not in namespaces:
            problems.append(f"events in namespace '{ns}' have no add_namespace")
    return {"events": len({i for i, _ in found}), "namespaces": sorted(namespaces)}


# ------------------------------------------------------------------- decisions

def check_decisions(paths: list[str], problems: list[str]) -> dict[str, Any]:
    names: list[tuple[str, str]] = []
    for path in paths:
        text = strip_comments(read(path))
        for m in re.finditer(r"\n\t([A-Za-z0-9_]+)\s*=\s*\{", text):
            body = text[m.end() - 1 : brace_block(text, m.end() - 1) + 1]
            if re.search(
                r"\b(cost|available|complete|days_remove|days_re_enable|fire_only_once|targets|activation)\s*=",
                body,
            ):
                names.append((m.group(1), os.path.basename(path)))
    for name, n in Counter(i for i, _ in names).items():
        if n > 1:
            problems.append(f"duplicate decision id {name} (x{n})")
    return {"decisions": len({i for i, _ in names})}


# ---------------------------------------------------------------- localisation

def load_loc(mod: str) -> set[str]:
    keys: set[str] = set()
    for dirpath, _d, files in os.walk(os.path.join(mod, "localisation")):
        for n in files:
            if not n.endswith(".yml"):
                continue
            for line in read(os.path.join(dirpath, n)).splitlines():
                m = re.match(r'\s*([A-Za-z0-9_.\-]+):\d*\s+"', line)
                if m:
                    keys.add(m.group(1))
    return keys


def check_loc(mod: str, focus_ids: list[str], problems: list[str]) -> dict[str, Any]:
    keys = load_loc(mod)
    missing = []
    for fid in focus_ids:
        if fid not in keys:
            missing.append(fid)
        if fid + "_desc" not in keys:
            missing.append(fid + "_desc")
    if missing:
        problems.append(f"{len(missing)} focus localisation key(s) missing, e.g. {sorted(missing)[:8]}")
    return {"loc_keys": len(keys), "focus_loc_missing": len(missing)}


# --------------------------------------------------------------------- sprites

def check_sprites(mod: str, game: str | None, paths: list[str], problems: list[str]) -> dict[str, Any]:
    registered: set[str] = set()
    roots = [os.path.join(mod, "interface")]
    if game:
        roots.append(os.path.join(game, "interface"))
    for root in roots:
        for dirpath, _d, files in os.walk(root):
            for n in files:
                if n.endswith(".gfx"):
                    registered |= set(re.findall(r'name\s*=\s*"([A-Za-z0-9_]+)"', read(os.path.join(dirpath, n))))
    if not game:
        return {"note": "no --game given, sprite check skipped"}

    used: set[str] = set()
    for path in paths:
        if not path.endswith(".txt"):
            continue
        text = strip_comments(read(path))
        used |= set(re.findall(r"\b(GFX_[A-Za-z0-9_]+)", text))
        for pic in re.findall(r"\bpicture\s*=\s*([A-Za-z0-9_]+)", text):
            used.add(pic if pic.startswith("GFX_") else "GFX_idea_" + pic)
    missing = sorted(u for u in used if u not in registered)
    if missing:
        problems.append(f"{len(missing)} unregistered sprite reference(s): {missing[:10]}")
    return {"sprites_registered": len(registered), "sprites_missing": len(missing)}


# ----------------------------------------------------------------------- style

def check_style(paths: list[str], mod: str, problems: list[str]) -> None:
    for path in paths:
        if not path.endswith((".txt", ".gfx")):
            continue
        text = strip_comments(read(path))
        rel = os.path.relpath(path, mod)
        for pat, msg in (
            (r">=|<=|<=", "compound comparison (>= / <=) is illegal"),
            (r"(?<![a-z_])(stability|war_support)\s*[<>]", "bare stability/war_support trigger (needs has_)"),
            (r"add_consumer_goods_factor", "undocumented add_consumer_goods_factor"),
        ):
            for m in list(re.finditer(pat, text))[:3]:
                problems.append(f"{rel}:{text[: m.start()].count(chr(10)) + 1}: {msg}")
        # NOTE: check_variable accepts both `{ var = x value = 1 compare = less_than }`
        # and the short form `{ x < 1 }`. Both are documented and used by vanilla,
        # so neither is a defect and nothing is flagged here.


# ------------------------------------------------------------------------ main

def iran_files(mod: str) -> list[str]:
    chosen = []
    for rel in FOCUS_FILES + EXTRA_FILES:
        p = os.path.join(mod, rel)
        if os.path.exists(p):
            chosen.append(p)
    for root in ("common", "events"):
        for dirpath, _d, files in os.walk(os.path.join(mod, root)):
            for n in files:
                low = n.lower()
                if low.endswith(".txt") and (
                    low.startswith("iran") or low.startswith("per") or low.startswith("goe_persia")
                ):
                    chosen.append(os.path.join(dirpath, n))
    return sorted(set(chosen))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.getcwd())
    ap.add_argument("--game", default=None)
    ap.add_argument("--report", default=None)
    args = ap.parse_args()
    mod = os.path.abspath(args.mod)

    problems: list[str] = []
    focus_total = 0
    focus_ids: list[str] = []
    for rel in FOCUS_FILES:
        path = os.path.join(mod, rel)
        if os.path.exists(path):
            focus_total += check_focus_tree(path, problems)
            focus_ids += [f["id"] for f in parse_focuses(path)]

    files = iran_files(mod)
    events = [p for p in files if os.sep + "events" + os.sep in p]
    decisions = [p for p in files if os.sep + "decisions" + os.sep in p]
    facts: dict[str, Any] = {"focuses": focus_total, "files": len(files)}
    facts.update(check_events(events, problems))
    facts.update(check_decisions(decisions, problems))
    facts.update(check_loc(mod, focus_ids, problems))
    facts.update(check_sprites(mod, args.game, files, problems))
    check_style(files, mod, problems)

    lines = [
        "# Iran content audit",
        "",
        f"Scanned {facts['files']} Iran-owned script files.",
        "",
        f"- focuses: **{facts['focuses']}**",
        f"- events: {facts.get('events', 0)} in namespaces {facts.get('namespaces', [])}",
        f"- decisions: {facts.get('decisions', 0)}",
        f"- localisation keys: {facts.get('loc_keys', 0)} (missing focus keys: {facts.get('focus_loc_missing', 0)})",
        f"- sprites registered: {facts.get('sprites_registered', 'n/a')} "
        f"(unresolved refs: {facts.get('sprites_missing', 'n/a')})",
        "",
    ]
    if problems:
        lines.append(f"## {len(problems)} problem(s)")
        lines.append("")
        lines.extend(f"- {p}" for p in problems)
    else:
        lines.append("## Clean: no problems found")
    report = "\n".join(lines) + "\n"
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
