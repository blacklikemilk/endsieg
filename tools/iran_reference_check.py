"""Resolve every cross-reference the Iran package makes.

A `country_event = { id = x.5 }`, `add_ideas = { some_idea }` or
`iran_some_effect = yes` that resolves to nothing fails silently at runtime: the
decision looks available, the player clicks it, and nothing happens. This walks
the Iran-owned script, collects every such reference, and resolves it against the
mod plus the installed game.

Usage:
  python tools/iran_reference_check.py --game "<HOI4 install>" [--report out.md]
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import glob

IRAN_GLOBS = [
    "common/national_focus/iran_*.txt",
    "common/decisions/iran_*.txt",
    "common/decisions/PER_*.txt",
    "common/decisions/categories/iran_*.txt",
    "common/decisions/categories/PER_*.txt",
    "common/scripted_effects/iran_*.txt",
    "common/scripted_effects/PER_*.txt",
    "common/scripted_triggers/iran_*.txt",
    "common/ideas/iran_*.txt",
    "common/ideas/PER_*.txt",
    "common/ai_strategy_plans/iran_*.txt",
    "common/ai_strategy_plans/PER_*.txt",
    "common/on_actions/iran_*.txt",
    "events/iran_*.txt",
    "events/GOE_Persia.txt",
]

BUILTIN_EFFECTS = {"always", "if", "else", "random", "log", "set_variable"}  # guards against noise


def read(path: str) -> str:
    with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def strip_comments(text: str) -> str:
    return "\n".join(line if line.find("#") < 0 else line[: line.find("#")] for line in text.splitlines())


def collect(pattern_roots: list[str], kind: str) -> set[str]:
    """Names defined by `key = {` at a definition site."""
    found: set[str] = set()
    for path in pattern_roots:
        text = strip_comments(read(path))
        if kind == "event":
            for body in re.finditer(r"(?:country_event|news_event|state_event)\s*=\s*\{", text):
                seg = text[body.end() : body.end() + 400]
                m = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+\.[0-9]+)", seg)
                if m:
                    found.add(m.group(1))
        elif kind == "effect":
            found |= set(re.findall(r"^[ \t]*([A-Za-z0-9_]+)\s*=\s*\{", text, re.M))
        elif kind == "trigger":
            found |= set(re.findall(r"^[ \t]*([A-Za-z0-9_]+)\s*=\s*\{", text, re.M))
        elif kind == "idea":
            found |= set(re.findall(r"^[ \t]*([A-Za-z0-9_]+)\s*=\s*\{", text, re.M))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.getcwd())
    ap.add_argument("--game", required=True)
    ap.add_argument("--report", default=None)
    args = ap.parse_args()
    mod = os.path.abspath(args.mod)
    game = os.path.abspath(args.game)

    owned: list[str] = []
    for pattern in IRAN_GLOBS:
        owned += glob.glob(os.path.join(mod, pattern))
    owned = sorted(set(owned))
    if not owned:
        print("no Iran files found")
        return 1

    # ---- definitions available: mod + game
    all_effects: set[str] = set()
    all_triggers: set[str] = set()
    all_ideas: set[str] = set()
    all_events: set[str] = set()
    for root in (mod, game):
        all_effects |= set(re.findall(r"^[ \t]*([A-Za-z0-9_]+)\s*=\s*\{", "", re.M))
        for path in glob.glob(os.path.join(root, "common", "scripted_effects", "*.txt")):
            all_effects |= set(re.findall(r"^[ \t]*([A-Za-z0-9_]+)\s*=\s*\{", strip_comments(read(path)), re.M))
        for path in glob.glob(os.path.join(root, "common", "scripted_triggers", "*.txt")):
            all_triggers |= set(re.findall(r"^[ \t]*([A-Za-z0-9_]+)\s*=\s*\{", strip_comments(read(path)), re.M))
        for path in glob.glob(os.path.join(root, "common", "ideas", "*.txt")):
            all_ideas |= set(re.findall(r"^\t+([A-Za-z0-9_]+)\s*=\s*\{", strip_comments(read(path)), re.M))
        for path in glob.glob(os.path.join(root, "events", "**", "*.txt"), recursive=True):
            all_events |= set(re.findall(r"\bid\s*=\s*([A-Za-z0-9_]+\.[0-9]+)", strip_comments(read(path))))

    problems: list[str] = []
    counts = {"events": 0, "effects": 0, "triggers": 0, "ideas": 0}

    for path in owned:
        text = strip_comments(read(path))
        rel = os.path.relpath(path, mod)

        # events fired
        for m in re.finditer(r"\b(?:country_event|news_event|state_event)\s*=\s*\{[^{}]*?id\s*=\s*([A-Za-z0-9_]+\.[0-9]+)", text):
            eid = m.group(1)
            counts["events"] += 1
            if eid not in all_events:
                problems.append(f"{rel}: fires event {eid}, which is defined nowhere")

        # scripted effect / trigger calls: `iran_something = yes`
        for m in re.finditer(r"\b((?:iran|PER)_[a-z0-9_]{3,})\s*=\s*yes\b", text):
            name = m.group(1)
            if name in all_effects or name in all_triggers:
                counts["effects"] += 1
                continue
            problems.append(f"{rel}: calls {name} = yes, which is neither a scripted effect nor a trigger")

        # ideas referenced
        for m in re.finditer(r"\b(?:add_ideas|has_idea|remove_ideas)\s*=\s*\{([^}]*)\}", text):
            for idea in re.findall(r"[A-Za-z0-9_]+", m.group(1)):
                if idea in {"yes", "no"}:
                    continue
                counts["ideas"] += 1
                if idea not in all_ideas:
                    problems.append(f"{rel}: references idea {idea}, which is defined nowhere")
        for m in re.finditer(r"\b(?:add_ideas|has_idea)\s*=\s*([A-Za-z0-9_]+)\b", text):
            idea = m.group(1)
            if idea in {"yes", "no"}:
                continue
            counts["ideas"] += 1
            if idea not in all_ideas:
                problems.append(f"{rel}: references idea {idea}, which is defined nowhere")

    # de-duplicate while keeping order
    seen, unique = set(), []
    for p in problems:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    lines = ["# Iran reference check", "", f"Scanned {len(owned)} files.", ""]
    lines.append(f"- event references: {counts['events']}")
    lines.append(f"- idea references: {counts['ideas']}")
    lines.append(f"- events known: {len(all_events)}  ideas known: {len(all_ideas)}")
    lines.append("")
    if unique:
        lines.append(f"## {len(unique)} unresolved reference(s)")
        lines.append("")
        lines.extend(f"- {p}" for p in unique[:60])
    else:
        lines.append("## Every reference resolves")
    report = "\n".join(lines) + "\n"
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with io.open(args.report, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
