"""Strip character portrait references that resolve to no sprite.

A `portraits = { large = GFX_portrait_X }` whose sprite is never registered makes
the game log an unknown-sprite error and draw a blank frame. This tool removes
only the unresolvable references (and the sub-blocks they leave empty), keeping
every portrait that does resolve. Characters that lose their only portrait fall
back to the engine's default, which is correct behaviour.

Usage:
  python tools/prune_dead_portraits.py [--apply] [--game "<HOI4 install>"]
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys

FILES = [
    "common/characters/PER.txt",
    "common/characters/PER_restored.txt",
    "common/characters/WWI - PER.txt",
    "common/characters/iran_campaign.txt",
]


def read(path: str) -> str:
    with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def registered_sprites(mod: str, game: str | None) -> set[str]:
    names: set[str] = set()
    roots = [os.path.join(mod, "interface")]
    if game:
        roots.append(os.path.join(game, "interface"))
    for root in roots:
        for dirpath, _d, files in os.walk(root):
            for n in files:
                if n.endswith(".gfx"):
                    names |= set(re.findall(r'name\s*=\s*"([A-Za-z0-9_]+)"', read(os.path.join(dirpath, n))))
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.getcwd())
    ap.add_argument("--game", default=None)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    mod = os.path.abspath(args.mod)
    sprites = registered_sprites(mod, args.game)
    print(f"{len(sprites)} sprites registered")

    for rel in FILES:
        path = os.path.join(mod, rel)
        if not os.path.exists(path):
            continue
        text = read(path)
        removed: list[str] = []
        out = []
        for line in text.splitlines(keepends=True):
            m = re.match(r"\s*(large|small)\s*=\s*\"?([A-Za-z0-9_]+)\"?\s*$", line.rstrip("\r\n"))
            if m and m.group(2) not in sprites:
                removed.append(f"{m.group(1)}={m.group(2)}")
                continue
            out.append(line)
        text = "".join(out)

        # prune sub-blocks and the portraits block that the removals emptied
        before = len(text)
        while True:
            new = re.sub(r"\n\t*[a-z_]+\s*=\s*\{\s*\}", "", text)
            new = re.sub(r"\n\t*portraits\s*=\s*\{\s*\}", "", new)
            if new == text:
                break
            text = new
        if removed:
            print(f"{rel}: removed {len(removed)} dead portrait ref(s), {before - len(text)} chars of empty blocks")
            for r in removed[:6]:
                print(f"    {r}")
            if len(removed) > 6:
                print(f"    ... and {len(removed) - 6} more")
        if args.apply and text != read(path):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            print(f"    written")

    return 0


if __name__ == "__main__":
    sys.exit(main())
