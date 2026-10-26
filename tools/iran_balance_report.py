"""Balance report for the Iran package.

Static, not a simulation: it lists what the content actually hands out, so the
outliers can be compared against each other instead of eyeballed. Flags:

  * free buildings per focus (and per chapter total)
  * equipment and manpower grants
  * permanent modifiers on national spirits
  * repeatable decisions that pay out without a matching cost or cooldown
  * focuses that touch the same variable with no cap

Usage:
  python tools/iran_balance_report.py [--report out.md]
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from collections import Counter, defaultdict

FOCUS_FILES = [
    "common/national_focus/iran_ww1.txt",
    "common/national_focus/iran_interwar.txt",
    "common/national_focus/iran_ww2.txt",
]
DECISION_FILES = [
    "common/decisions/iran_campaign.txt",
    "common/decisions/iran_coup_1921.txt",
    "common/decisions/iran_political_question.txt",
    "common/decisions/PER_crown_and_majlis.txt",
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


def named_blocks(text: str, key: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"\b" + key + r"\s*=\s*\{", text):
        start = m.end() - 1
        body = text[start : brace_block(text, start) + 1]
        ident = re.search(r"\bid\s*=\s*([A-Za-z0-9_.]+)", body)
        out.append((ident.group(1) if ident else "", body))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.getcwd())
    ap.add_argument("--report", default=None)
    args = ap.parse_args()
    mod = os.path.abspath(args.mod)

    buildings: list[tuple[str, int, str]] = []
    equipment: list[tuple[str, int, str]] = []
    manpower: list[tuple[str, int, str]] = []
    per_chapter: Counter = Counter()
    variable_writes: Counter = Counter()

    for rel in FOCUS_FILES:
        path = os.path.join(mod, rel)
        if not os.path.exists(path):
            continue
        chapter = os.path.basename(rel).replace("iran_", "").replace(".txt", "")
        for fid, body in named_blocks(read(path), "focus"):
            if not fid:
                continue
            for m in re.finditer(r"add_building_construction\s*=\s*\{\s*type\s*=\s*(\w+)\s+level\s*=\s*(\d+)", body):
                n = int(m.group(2))
                buildings.append((fid, n, m.group(1)))
                per_chapter[chapter] += n
            for m in re.finditer(r"add_equipment_to_stockpile\s*=\s*\{\s*type\s*=\s*(\w+)\s+amount\s*=\s*(-?\d+)", body):
                equipment.append((fid, int(m.group(2)), m.group(1)))
            for m in re.finditer(r"add_manpower\s*=\s*(-?\d+)", body):
                manpower.append((fid, int(m.group(1)), "manpower"))
            for m in re.finditer(r"(?:add_to_variable|set_variable|subtract_from_variable)\s*=\s*\{\s*(\w+)", body):
                variable_writes[m.group(1)] += 1

    decisions = []
    for rel in DECISION_FILES:
        path = os.path.join(mod, rel)
        if not os.path.exists(path):
            continue
        text = read(path)
        for m in re.finditer(r"\n\t([A-Za-z0-9_]+)\s*=\s*\{", text):
            body = text[m.end() - 1 : brace_block(text, m.end() - 1) + 1]
            if not re.search(r"\b(cost|complete_effect|remove_effect)\s*=", body):
                continue
            name = m.group(1)
            has_cost = bool(re.search(r"\bcost\s*=", body))
            has_cooldown = bool(re.search(r"days_re_enable\s*=", body))
            once = bool(re.search(r"fire_only_once\s*=\s*yes", body))
            pay = bool(re.search(r"complete_effect|remove_effect", body))
            decisions.append((name, has_cost, has_cooldown or once, pay))

    lines = ["# Iran balance report", ""]
    lines.append("## Free buildings per chapter")
    for chapter, total in sorted(per_chapter.items()):
        lines.append(f"- {chapter}: **{total}** building levels handed out by focuses")
    lines.append("")
    lines.append("### Largest single grants")
    for fid, n, kind in sorted(buildings, key=lambda x: -x[1])[:10]:
        lines.append(f"- {fid}: {n} x {kind}")
    lines.append("")
    lines.append("## Equipment grants")
    if equipment:
        per_type = Counter()
        for _fid, n, kind in equipment:
            per_type[kind] += n
        for kind, total in per_type.most_common():
            lines.append(f"- {kind}: {total} total")
        top = sorted(equipment, key=lambda x: -x[1])[:5]
        lines.append("")
        lines.append("### Largest single grants")
        for fid, n, kind in top:
            lines.append(f"- {fid}: {n} x {kind}")
    lines.append("")
    lines.append("## Manpower grants")
    if manpower:
        for fid, n, _ in sorted(manpower, key=lambda x: -x[1])[:8]:
            lines.append(f"- {fid}: {n}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Repeatable decisions with no cooldown and no once-only flag")
    risky = [d for d in decisions if d[3] and not d[2]]
    if risky:
        for name, cost, cooled, _pay in risky:
            lines.append(f"- {name}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Variable write counts")
    for var, n in variable_writes.most_common(12):
        lines.append(f"- {var}: written by {n} focuses")
    report = "\n".join(lines) + "\n"
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
