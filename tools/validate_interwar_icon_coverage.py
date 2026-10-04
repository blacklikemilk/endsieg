"""Verify one working, distinct icon per German, Soviet, and White Russian interwar focus and spirit."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re

from PIL import Image

import package_interwar_german_focus_icons as ger
import package_int_sov_focus_icons as sov
import package_int_whr_icons as whr
import package_interwar_idea_icons as idea


ROOT = Path(__file__).resolve().parents[1]


def sprite_paths(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    result = {}
    for name, texture in re.findall(
        r'spriteType\s*=\s*\{\s*name\s*=\s*"([^"]+)"\s*'
        r'texturefile\s*=\s*"([^"]+)"', text, flags=re.IGNORECASE
    ):
        if name in result:
            raise ValueError(f"Duplicate sprite name in {path}: {name}")
        result[name] = texture
    return result


def focus_icon(script_path: Path, focus_id: str) -> str:
    script = script_path.read_text(encoding="utf-8-sig")
    match = re.search(
        r"(?m)^\s*id\s*=\s*" + re.escape(focus_id) +
        r"\s*\r?\n\s*icon\s*=\s*([A-Za-z0-9_]+)", script
    )
    if not match:
        raise ValueError(f"Missing focus icon reference: {focus_id}")
    return match.group(1)


def idea_picture(script_path: Path, idea_id: str) -> str:
    script = script_path.read_text(encoding="utf-8-sig")
    start = re.search(r"(?m)^\t\t" + re.escape(idea_id) + r"\s*=\s*\{", script)
    if not start:
        raise ValueError(f"Missing idea block: {idea_id}")
    opening = script.index("{", start.start(), start.end())
    cursor, depth = opening + 1, 1
    while depth and cursor < len(script):
        if script[cursor] == "{":
            depth += 1
        elif script[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise ValueError(f"Unbalanced idea: {idea_id}")
    block = script[opening:cursor]
    picture = re.search(r"(?m)^\s*picture\s*=\s*([A-Za-z0-9_]+)", block)
    if not picture:
        raise ValueError(f"Missing idea picture: {idea_id}")
    return picture.group(1)


def check_texture(path: Path, size: tuple[int, int]) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        if image.size != size or image.mode != "RGBA":
            raise ValueError(f"Invalid texture {path}: {image.size} {image.mode}")
        if image.getchannel("A").getextrema() != (0, 255):
            raise ValueError(f"Texture lacks proper alpha: {path}")
        return hashlib.sha256(image.tobytes()).digest()


def check_source(path: Path, allowed_sizes: set[tuple[int, int]]) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        legacy_master = min(image.size) >= 200
        if image.mode != "RGBA" or (image.size not in allowed_sizes and not legacy_master):
            raise ValueError(f"Invalid source {path}: {image.size} {image.mode}; expected native {sorted(allowed_sizes)} or a legacy master")
        if image.getchannel("A").getextrema() != (0, 255):
            raise ValueError(f"Source lacks proper alpha: {path}")


def check_focus_group(
    ids: list[str], script: Path, gfx_path: Path, source, texture, sprite,
    *, complete: bool, source_sizes: set[tuple[int, int]]
) -> list[bytes]:
    sprites = sprite_paths(gfx_path)
    digests = []
    for focus_id in ids:
        if not source(focus_id).is_file():
            if complete:
                raise FileNotFoundError(source(focus_id))
            continue
        name = sprite(focus_id)
        if focus_icon(script, focus_id) != name:
            raise ValueError(f"Focus {focus_id} does not use its own sprite")
        path = texture(focus_id)
        relative = path.relative_to(ROOT).as_posix()
        if sprites.get(name) != relative or sprites.get(name + "_shine") != relative:
            raise ValueError(f"Missing or wrong base/shine sprite: {focus_id}")
        check_source(source(focus_id), source_sizes)
        digests.append(check_texture(path, (96, 96)))
    return digests


def main(*, complete: bool) -> None:
    ger_ids = ger.verify_manifest()
    sov_ids = sov.focus_ids()
    whr_ids = [entry[0] for entry in whr.rows()]
    focus_digests = []
    focus_digests.extend(check_focus_group(
        ger_ids, ger.FOCUS_SCRIPT, ger.GFX, ger.source_path,
        ger.goal_path, ger.sprite_name, complete=complete,
        source_sizes={(96, 96), (256, 256)}
    ))
    focus_digests.extend(check_focus_group(
        sov_ids, sov.TREE, sov.GFX, sov.source_path,
        sov.goal_path, sov.sprite, complete=complete,
        source_sizes={(96, 96), (256, 256)}
    ))
    focus_digests.extend(check_focus_group(
        whr_ids, whr.FOCUSES, whr.GFX, whr.source_path,
        whr.goal_path, whr.sprite_name, complete=complete,
        source_sizes={(96, 96), (256, 256)}
    ))
    if Counter(focus_digests).most_common(1) and Counter(focus_digests).most_common(1)[0][1] > 1:
        raise ValueError("Two focuses share the same rendered icon")

    all_ideas = idea.ideas()
    idea_sprites = sprite_paths(idea.GFX)
    shared_gfx = ROOT / "interface/endsieg_interwar_icons.gfx"
    if shared_gfx.is_file():
        for name, path in sprite_paths(shared_gfx).items():
            if name in idea_sprites and idea_sprites[name] != path:
                raise ValueError(f"Idea sprite has conflicting definitions: {name}")
            idea_sprites.setdefault(name, path)
    idea_digests = []
    for idea_id, script in all_ideas.items():
        if not idea.source_path(idea_id).is_file():
            if complete:
                raise FileNotFoundError(idea.source_path(idea_id))
            continue
        name = idea.token(idea_id)
        if idea_picture(script, idea_id) != name:
            raise ValueError(f"Idea {idea_id} does not use its own picture")
        path = idea.texture_path(idea_id)
        if idea_sprites.get(f"GFX_idea_{name}") != path.relative_to(ROOT).as_posix():
            raise ValueError(f"Idea {idea_id} has no matching sprite definition")
        check_source(idea.source_path(idea_id), {(60, 68), (256, 256)})
        idea_digests.append(check_texture(path, (60, 68)))
    if Counter(idea_digests).most_common(1) and Counter(idea_digests).most_common(1)[0][1] > 1:
        raise ValueError("Two ideas share the same rendered icon")
    suffix = " complete" if complete else " available"
    focus_total = len(ger_ids) + len(sov_ids) + len(whr_ids)
    print(f"Verified {len(focus_digests)}/{focus_total} unique focus icons and "
          f"{len(idea_digests)}/{len(all_ideas)} unique idea icons ({suffix.strip()})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--available", action="store_true", help="check only art already imported")
    args = parser.parse_args()
    main(complete=not args.available)
