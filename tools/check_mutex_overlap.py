"""Flag mutually exclusive focus pairs with another focus sitting between them.

Mutually exclusive focuses carry a marker in the space beside them. When a third focus
occupies that space - on the same row between the pair, or in the same column - the marker
lands on that focus's frame instead of on clear ground, which is what the Spanish
"Conciliate the CNT / The Church and the State / Repress the CNT" row shows in game.

Scope of the claim: this tool reports geometry only. The rendering consequence is inferred
from a screenshot of the Spanish row and has not been verified by a game launch, so treat a
hit as "look at this pair", not "the engine draws a line".
Vanilla content contains many of the same patterns; review the mod's own trees first.

    python tools/check_mutex_overlap.py                    # every focus file, summary by file
    python tools/check_mutex_overlap.py --tree spain_restoration
    python tools/check_mutex_overlap.py --file common/national_focus/spain_restoration.txt
    python tools/check_mutex_overlap.py --json

Exit status is 0 when clean or when the run was unscoped, 1 when a scoped run finds overlaps,
2 on a read or parse error.

Rules reported:
  OVERLAP          a focus sits between a mutually exclusive pair
  NON-RECIPROCAL   A declares exclusivity with B but B does not declare it back
  SELF             a focus lists itself as mutually exclusive
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FOCUS_ROOT = Path("common/national_focus")
ID_RE = re.compile(r"^\s*id\s*=\s*([A-Za-z0-9_.-]+)\s*$")
ID_INLINE_RE = re.compile(r"\bid\s*=\s*([A-Za-z0-9_.-]+)")
X_RE = re.compile(r"\bx\s*=\s*(-?\d+)")
Y_RE = re.compile(r"\by\s*=\s*(-?\d+)")
REL_RE = re.compile(r"^\s*relative_position_id\s*=\s*([A-Za-z0-9_.-]+)\s*$")
REL_INLINE_RE = re.compile(r"\brelative_position_id\s*=\s*([A-Za-z0-9_.-]+)")
MUTEX_START_RE = re.compile(r"^\s*mutually_exclusive\s*=\s*\{")
MUTEX_ITEM_RE = re.compile(r"focus\s*=\s*([A-Za-z0-9_.-]+)")


@dataclass
class Focus:
    id: str
    x: int = 0
    y: int = 0
    rel: str | None = None
    mutex: list[str] = field(default_factory=list)
    tree: str = ""
    file: str = ""
    line: int = 0


def strip_comment(line: str) -> str:
    out = []
    in_string = False
    for index, char in enumerate(line):
        if char == '"':
            in_string = not in_string
        if char == "#" and not in_string:
            break
        out.append(char)
    return "".join(out)


def parse_file(path: Path) -> tuple[list[Focus], list[str]]:
    """Return the focuses declared in a file and any structural warnings."""
    focuses: list[Focus] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()

    depth = 0
    current_tree = ""
    # track brace depth at which a focus block opened, so nested blocks cannot confuse us
    stack: list[tuple[int, Focus]] = []
    offset = 0
    mutex_at_depth: int | None = None

    for index, raw in enumerate(lines, start=1):
        line = strip_comment(raw)
        if not line.strip():
            continue
        stripped = line.strip()

        # a new focus block starts when we see "focus = {" at tree-body depth
        if re.match(r"^focus\s*=\s*\{", stripped):
            # single-line form: focus = { id = X x = 1 y = 2 ... }
            if line.count("{") == line.count("}") and ID_INLINE_RE.search(stripped):
                inline = Focus(id="", tree=current_tree, file=str(path), line=index)
                id_match = ID_INLINE_RE.search(stripped)
                if id_match:
                    inline.id = id_match.group(1)
                x_match = X_RE.search(stripped)
                y_match = Y_RE.search(stripped)
                rel_match = REL_INLINE_RE.search(stripped)
                if x_match:
                    inline.x = int(x_match.group(1))
                if y_match:
                    inline.y = int(y_match.group(1))
                if rel_match:
                    inline.rel = rel_match.group(1)
                if MUTEX_START_RE.search(stripped):
                    inline.mutex = MUTEX_ITEM_RE.findall(stripped)
                focuses.append(inline)
                continue
            new_focus = Focus(id="", tree=current_tree, file=str(path), line=index)
            stack.append((depth + line.count("{") - line.count("}"), new_focus))
            focuses.append(new_focus)
            depth += line.count("{") - line.count("}")
            continue

        if re.match(r"^focus_tree\s*=\s*\{", stripped):
            depth += line.count("{") - line.count("}")
            offset = depth
            current_tree = ""
            continue

        if not stack and re.match(r"^id\s*=", stripped) and depth == offset:
            match = re.match(r"^id\s*=\s*([A-Za-z0-9_.-]+)", stripped)
            if match:
                current_tree = match.group(1)
            depth += line.count("{") - line.count("}")
            continue

        if stack:
            active = stack[-1][1]
            id_match = ID_RE.match(line)
            rel_match = REL_RE.match(line)
            if id_match and not active.id:
                active.id = id_match.group(1)
            elif rel_match:
                active.rel = rel_match.group(1)
            elif MUTEX_START_RE.match(line):
                mutex_at_depth = depth + 1
                for target in MUTEX_ITEM_RE.findall(line):
                    active.mutex.append(target)
            elif mutex_at_depth is not None and depth == mutex_at_depth:
                for target in MUTEX_ITEM_RE.findall(line):
                    active.mutex.append(target)
            elif "x" in line or "y" in line:
                x_match = X_RE.search(line)
                y_match = Y_RE.search(line)
                if x_match and "x =" in line.replace(" ", " x ="):
                    active.x = int(x_match.group(1))
                if y_match:
                    active.y = int(y_match.group(1))

        depth += line.count("{") - line.count("}")
        if mutex_at_depth is not None and depth < mutex_at_depth:
            mutex_at_depth = None
        while stack and depth <= stack[-1][0] - 1:
            closed_depth, closed = stack.pop()
            if not closed.id:
                warnings.append(f"{path}:{closed.line}: focus block with no id")

    return [focus for focus in focuses if focus.id], warnings


def resolve(focuses: dict[str, Focus]) -> None:
    """Fold relative_position_id into absolute coordinates, with cycle protection."""

    def absolute(focus: Focus, seen: frozenset[str]) -> tuple[int, int]:
        if not focus.rel or focus.rel in seen or focus.rel not in focuses:
            return focus.x, focus.y
        parent = focuses[focus.rel]
        parent_x, parent_y = absolute(parent, seen | {focus.id})
        return focus.x + parent_x, focus.y + parent_y

    for focus in focuses.values():
        focus.x, focus.y = absolute(focus, frozenset({focus.id}))


def find_overlaps(focuses: dict[str, Focus], max_gap: int = 2) -> list[dict[str, object]]:
    by_tree: dict[str, list[Focus]] = {}
    for focus in focuses.values():
        by_tree.setdefault(focus.tree, []).append(focus)

    problems: list[dict[str, object]] = []
    for tree, members in sorted(by_tree.items()):
        for focus in sorted(members, key=lambda item: item.id):
            for partner_id in focus.mutex:
                if partner_id == focus.id:
                    problems.append(
                        {
                            "kind": "SELF",
                            "tree": tree,
                            "a": focus.id,
                            "b": focus.id,
                            "file": focus.file,
                            "between": [],
                        }
                    )
                    continue
                partner = focuses.get(partner_id)
                if partner is None:
                    continue
                if focus.id not in partner.mutex:
                    problems.append(
                        {
                            "kind": "NON-RECIPROCAL",
                            "tree": tree,
                            "a": focus.id,
                            "b": partner_id,
                            "file": focus.file,
                            "between": [],
                        }
                    )
                if focus.id > partner_id:
                    continue  # report each pair once
                between = []
                nearest: list[tuple[int, str]] = []
                for other in members:
                    if other.id in {focus.id, partner.id}:
                        continue
                    # a focus that is itself in the exclusivity set owns its own marker: skip it
                    if (
                        other.id in focus.mutex
                        or other.id in partner.mutex
                        or focus.id in other.mutex
                        or partner.id in other.mutex
                    ):
                        continue
                    if focus.y == partner.y and other.y == focus.y and min(focus.x, partner.x) < other.x < max(focus.x, partner.x):
                        gap = min(abs(other.x - focus.x), abs(other.x - partner.x))
                        nearest.append((gap, f"{other.id} ({other.x},{other.y})"))
                    elif focus.x == partner.x and other.x == focus.x and min(focus.y, partner.y) < other.y < max(focus.y, partner.y):
                        gap = min(abs(other.y - focus.y), abs(other.y - partner.y))
                        nearest.append((gap, f"{other.id} ({other.x},{other.y})"))
                # the marker sits within one cell of its focus, so only a focus that close collides
                between = [name for gap, name in sorted(nearest) if gap <= max_gap]
                if between:
                    problems.append(
                        {
                            "kind": "OVERLAP",
                            "tree": tree,
                            "a": focus.id,
                            "b": partner.id,
                            "file": focus.file,
                            "between": sorted(between),
                            "a_pos": f"({focus.x},{focus.y})",
                            "b_pos": f"({partner.x},{partner.y})",
                        }
                    )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", action="append", default=[], help="a focus file to check")
    parser.add_argument("--tree", default="", help="only report this focus_tree id")
    parser.add_argument("--max-gap", type=int, default=2, help="cells between an endpoint and a focus that counts as a collision (default 2)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    files = [Path(item) for item in args.file]
    if not files:
        if not FOCUS_ROOT.is_dir():
            print(f"no focus folder at {FOCUS_ROOT.resolve()}", file=sys.stderr)
            return 2
        files = sorted(FOCUS_ROOT.glob("*.txt"))

    focuses: dict[str, Focus] = {}
    warnings: list[str] = []
    for path in files:
        try:
            parsed, file_warnings = parse_file(path)
        except OSError as exc:
            print(f"cannot read {path}: {exc}", file=sys.stderr)
            return 2
        warnings.extend(file_warnings)
        for focus in parsed:
            if focus.id in focuses:
                warnings.append(f"{path}:{focus.line}: duplicate focus id {focus.id} (already in {focuses[focus.id].file})")
                continue
            focuses[focus.id] = focus

    resolve(focuses)
    problems = find_overlaps(focuses, args.max_gap)
    if args.tree:
        problems = [item for item in problems if item["tree"] == args.tree]

    if args.json:
        print(json.dumps({"focuses": len(focuses), "warnings": warnings, "problems": problems}, indent=2))
        return 1 if any(item["kind"] == "OVERLAP" for item in problems) else 0

    overlaps = [item for item in problems if item["kind"] == "OVERLAP"]
    reciprocity = [item for item in problems if item["kind"] == "NON-RECIPROCAL"]
    selves = [item for item in problems if item["kind"] == "SELF"]

    def crossed(item: dict[str, object]) -> str:
        value = item["between"]
        return ", ".join(value) if isinstance(value, list) else str(value)

    print(f"focus files: {len(files)}   focuses: {len(focuses)}")
    print(f"OVERLAP: {len(overlaps)}   NON-RECIPROCAL: {len(reciprocity)}   SELF: {len(selves)}   warnings: {len(warnings)}")

    scoped = bool(args.tree or args.file)
    if overlaps:
        if scoped:
            print("\nOVERLAP — a focus sits between a mutually exclusive pair")
            for item in overlaps:
                print(f"  [{item['tree']}] {item['a']} {item.get('a_pos', '')} <-> {item['b']} {item.get('b_pos', '')}")
                print(f"      crossed: {crossed(item)}")
                print(f"      {item['file']}")
        else:
            per_file: dict[str, int] = {}
            for item in overlaps:
                per_file[str(item["file"])] = per_file.get(str(item["file"]), 0) + 1
            print("\nOVERLAP by file (rerun with --file or --tree for the pairs)")
            for name, count in sorted(per_file.items(), key=lambda pair: (-pair[1], pair[0])):
                print(f"  {count:4d}  {name}")
    if reciprocity and scoped:
        print("\nNON-RECIPROCAL — declared on one side only")
        for item in reciprocity:
            print(f"  [{item['tree']}] {item['a']} -> {item['b']}")
    if selves:
        print("\nSELF — a focus lists itself")
        for item in selves:
            print(f"  [{item['tree']}] {item['a']}")
    if warnings and scoped:
        print("\nWARNINGS")
        for warning in warnings[:20]:
            print(f"  {warning}")
    return 1 if (overlaps and scoped) else 0


if __name__ == "__main__":
    raise SystemExit(main())
