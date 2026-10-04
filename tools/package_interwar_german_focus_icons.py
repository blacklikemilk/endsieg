"""Package one bespoke icon per German interwar focus.

The source PNG for each focus lives in gfx/interface/interwar_german/focus_source.
Import a generated image with ``--import-generated FOCUS_ID IMAGE``; this only
removes the neutral exterior and rescales the original illustration. Run with
``--package`` after all current sources are present, then ``--check`` to validate.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

from PIL import Image

try:
    from .package_interwar_german_icons import ROOT, remove_neutral_backdrop, shine, sprite
    from .interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge
except ImportError:
    from package_interwar_german_icons import ROOT, remove_neutral_backdrop, shine, sprite
    from interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge


MANIFEST = ROOT / "tools/german_focus_icon_motifs.tsv"
SOURCE = ROOT / "gfx/interface/interwar_german/focus_source"
GOALS = ROOT / "gfx/interface/goals"
GFX = ROOT / "interface/endsieg_interwar_focus_icons.gfx"
FOCUS_SCRIPT = ROOT / "common/national_focus/INT - Germany.txt"


def motifs() -> dict[str, str]:
    rows = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        suffix, motif = line.split("|", 1)
        focus_id = "INT_GER_" + suffix
        if focus_id in rows:
            raise ValueError(f"Duplicate motif for {focus_id}")
        rows[focus_id] = motif
    return rows


def focus_ids() -> list[str]:
    script = FOCUS_SCRIPT.read_text(encoding="utf-8-sig")
    return re.findall(r"(?m)^\s*id\s*=\s*(INT_GER_[a-z0-9_]+)", script)


def verify_manifest() -> list[str]:
    ids = focus_ids()
    expected = motifs()
    if len(ids) != len(set(ids)):
        raise ValueError(f"German focus IDs are duplicated: {ids}")
    missing = set(ids) - set(expected)
    if missing:
        raise ValueError(f"Motif manifest lacks current German focuses: {sorted(missing)}")
    return ids


def source_path(focus_id: str) -> Path:
    return SOURCE / f"{focus_id}.png"


def goal_path(focus_id: str) -> Path:
    return GOALS / f"focus_INT_GER_focus_{focus_id.removeprefix('INT_GER_')}.dds"


def sprite_name(focus_id: str) -> str:
    return f"GFX_goal_INT_GER_focus_{focus_id.removeprefix('INT_GER_')}"


def import_generated(focus_id: str, raw: Path) -> None:
    if focus_id not in motifs():
        raise ValueError(f"Unknown German interwar focus: {focus_id}")
    image = remove_neutral_backdrop(Image.open(raw))
    bounds = image.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"No visible emblem in {raw}")
    image = image.crop(bounds)
    side = max(image.size)
    square = Image.new("RGBA", (side, side))
    square.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    SOURCE.mkdir(parents=True, exist_ok=True)
    solidify_icon_interior(square.resize((256, 256), Image.Resampling.LANCZOS)).save(
        source_path(focus_id), optimize=True
    )


def package(*, complete: bool = True) -> None:
    ids = verify_manifest()
    missing = [focus_id for focus_id in ids if not source_path(focus_id).is_file()]
    if missing and complete:
        raise FileNotFoundError(f"Missing {len(missing)} focus icons, starting with {missing[:5]}")
    available = [focus_id for focus_id in ids if source_path(focus_id).is_file()]
    gfx = ["spriteTypes = {\n"]
    for focus_id in available:
        goal = goal_path(focus_id)
        relative = goal.relative_to(ROOT).as_posix()
        with Image.open(source_path(focus_id)) as master:
            art = master.convert("RGBA")
        art.thumbnail((94, 94), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (96, 96))
        canvas.alpha_composite(art, ((96 - art.width) // 2, (96 - art.height) // 2))
        smooth_icon_edge(canvas).save(goal)
        name = sprite_name(focus_id)
        gfx.append(sprite(name, relative))
        gfx.append(shine(name, relative))
    gfx.append("}\n")
    GFX.write_text("".join(gfx), encoding="utf-8")

    original = FOCUS_SCRIPT.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    script = original.decode("utf-8-sig")
    matched = set()

    def replace(match: re.Match[str]) -> str:
        focus_id = match.group(2)
        if focus_id not in ids:
            raise ValueError(f"Unknown focus in tree: {focus_id}")
        if focus_id not in available:
            return match.group(0)
        if focus_id in matched:
            raise ValueError(f"Duplicate focus icon assignment: {focus_id}")
        matched.add(focus_id)
        return match.group(1) + sprite_name(focus_id)

    pattern = r"(?m)(^\s*id\s*=\s*(INT_GER_[a-z0-9_]+)\r?\n\s*icon\s*=\s*)\S+"
    updated = re.sub(pattern, replace, script)
    if matched != set(available):
        raise ValueError(f"Not all available focus icons assigned: {set(available) - matched}")
    FOCUS_SCRIPT.write_bytes((b"\xef\xbb\xbf" if bom else b"") + updated.encode("utf-8"))
    print(f"Packaged {len(available)} bespoke focus icons; {len(missing)} awaiting artwork")


def validate(*, complete: bool = True) -> None:
    ids = verify_manifest()
    available = [focus_id for focus_id in ids if source_path(focus_id).is_file()]
    if complete and len(available) != len(ids):
        raise ValueError(f"Missing {len(ids)-len(available)} focus sources")
    gfx = GFX.read_text(encoding="utf-8")
    if gfx.count("{") != gfx.count("}"):
        raise ValueError("Unbalanced focus GFX braces")
    names = re.findall(r'\bname\s*=\s*"([^"]+)"', gfx)
    if len(names) != 2 * len(available) or len(set(names)) != len(names):
        raise ValueError(f"Expected {2 * len(available)} unique focus sprites, found {len(names)}")
    script = FOCUS_SCRIPT.read_text(encoding="utf-8-sig")
    references = {}
    for focus_id in ids:
        match = re.search(
            r"(?m)^\s*id\s*=\s*" + re.escape(focus_id) +
            r"\s*\r?\n\s*icon\s*=\s*(\S+)", script
        )
        if not match:
            raise ValueError(f"Missing icon assignment: {focus_id}")
        references[focus_id] = match.group(1)
    available_references = [references[focus_id] for focus_id in available]
    if len(set(available_references)) != len(available):
        raise ValueError(f"Available German focuses reuse bespoke sprites: {available_references}")
    if set(available_references) != {sprite_name(focus_id) for focus_id in available}:
        raise ValueError("Focus references do not match the source manifest")
    shared_gfx = (ROOT / "interface/endsieg_interwar_icons.gfx").read_text(encoding="utf-8")
    shared_names = set(re.findall(r'\bname\s*=\s*"([^"]+)"', shared_gfx))
    if any(name not in names and name not in shared_names for name in references.values()):
        raise ValueError("An interwar focus icon is missing a sprite definition")
    texture_digests = []
    for focus_id in available:
        path = goal_path(focus_id)
        if not source_path(focus_id).is_file() or not path.is_file():
            raise FileNotFoundError(path)
        with Image.open(path) as image:
            if image.size != (96, 96) or image.mode != "RGBA":
                raise ValueError(f"Invalid DDS: {path}: {image.size} {image.mode}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Invalid DDS transparency: {path}")
        texture_digests.append(hashlib.sha256(path.read_bytes()).digest())
    if len(texture_digests) != len(set(texture_digests)):
        raise ValueError("Duplicate focus DDS textures")
    print(f"Verified {len(available)} distinct focus sources, DDS textures, and {len(names)} unique bespoke sprites; {len(ids)-len(available)} shared icons remain")


def validate_sources() -> None:
    ids = verify_manifest()
    present = [focus_id for focus_id in ids if source_path(focus_id).is_file()]
    digests = []
    for focus_id in present:
        path = source_path(focus_id)
        with Image.open(path) as image:
            if (image.size != (96, 96) and min(image.size) < 200) or image.mode != "RGBA":
                raise ValueError(f"Invalid source PNG (expected native 96px or legacy master): {path}: {image.size} {image.mode}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Invalid alpha in {path}")
        digests.append(hashlib.sha256(path.read_bytes()).digest())
    if len(digests) != len(set(digests)):
        raise ValueError("Duplicate source PNG bytes")
    print(f"Verified {len(present)} distinct native/legacy focus sources; {len(ids)-len(present)} remaining")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-generated", nargs=2, metavar=("FOCUS_ID", "IMAGE"))
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--package-available", action="store_true", help="wire completed icons while keeping shared icons for missing ones")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-available", action="store_true")
    parser.add_argument("--check-sources", action="store_true")
    args = parser.parse_args()
    if args.import_generated:
        import_generated(args.import_generated[0], Path(args.import_generated[1]))
    if args.package:
        package()
    if args.package_available:
        package(complete=False)
    if args.check:
        validate()
    if args.check_available:
        validate(complete=False)
    if args.check_sources:
        validate_sources()
