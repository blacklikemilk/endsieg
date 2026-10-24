"""Import, wire, and check one illustrated icon per White Russian interwar focus.

The motif manifest records the prompt subjects. Import a generated image with
``--import-generated FOCUS_ID IMAGE``, then run ``--package`` and ``--check``.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

try:
    from .interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge
except ImportError:
    from interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/whr_focus_icon_motifs.tsv"
SOURCE = ROOT / "gfx/interface/interwar_whr/focus_source"
GOALS = ROOT / "gfx/interface/goals"
GFX = ROOT / "interface/endsieg_int_whr_focus_icons.gfx"
FOCUSES = ROOT / "common/national_focus/INT - WHR Paths.txt"
PREVIEW = ROOT / "gfx/interface/interwar_whr/focus_preview.png"


def rows() -> list[tuple[str, str, str, str]]:
    result = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            pieces = line.split("|")
            if len(pieces) != 4:
                raise ValueError(f"Invalid motif row: {line}")
            result.append(tuple(pieces))
    ids = [row[0] for row in result]
    if len(ids) != len(set(ids)):
        raise ValueError("White Russian focus motifs contain duplicate IDs")
    focus_ids = re.findall(r"(?m)^\s*id\s*=\s*(WHR_INT_[a-z0-9_]+)",
                           FOCUSES.read_text(encoding="utf-8-sig"))
    if set(ids) != set(focus_ids) or len(focus_ids) != len(set(focus_ids)):
        raise ValueError(f"Motifs do not match focus IDs: {set(ids) ^ set(focus_ids)}")
    return result


def source_path(focus_id: str) -> Path:
    return SOURCE / f"{focus_id}.png"


def goal_path(focus_id: str) -> Path:
    return GOALS / f"focus_{focus_id}.dds"


def sprite_name(focus_id: str) -> str:
    return f"GFX_goal_{focus_id}"


def import_generated(focus_id: str, raw_path: Path) -> None:
    if focus_id not in {row[0] for row in rows()}:
        raise ValueError(f"Unknown White Russian focus: {focus_id}")
    image = Image.open(raw_path).convert("RGBA")
    bounds = image.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"No visible artwork in {raw_path}")
    image = image.crop(bounds)
    side = max(image.size)
    square = Image.new("RGBA", (side, side))
    square.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    SOURCE.mkdir(parents=True, exist_ok=True)
    solidify_icon_interior(square.resize((256, 256), Image.Resampling.LANCZOS)).save(
        source_path(focus_id), optimize=True
    )


def sprite(name: str, path: str) -> str:
    return f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "{path}"\n\t}}\n'


def shine(name: str, path: str) -> str:
    lines = [
        "\tSpriteType = {",
        f'\t\tname = "{name}_shine"',
        f'\t\ttexturefile = "{path}"',
        '\t\teffectFile = "gfx/FX/buttonstate.lua"',
    ]
    for rotation in (-90.0, 90.0):
        lines.extend([
            "\t\tanimation = {",
            f'\t\t\tanimationmaskfile = "{path}"',
            '\t\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"',
            f"\t\t\tanimationrotation = {rotation}",
            "\t\t\tanimationlooping = no",
            "\t\t\tanimationtime = 0.75",
            "\t\t\tanimationdelay = 0",
            '\t\t\tanimationblendmode = "add"',
            '\t\t\tanimationtype = "scrolling"',
            "\t\t\tanimationrotationoffset = { x = 0.0 y = 0.0 }",
            "\t\t\tanimationtexturescale = { x = 1.0 y = 1.0 }",
            "\t\t}",
        ])
    lines.extend(["\t\tlegacy_lazy_load = no", "\t}"])
    return "\n".join(lines) + "\n"


def package() -> None:
    entries = rows()
    missing = [focus_id for focus_id, *_ in entries if not source_path(focus_id).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing {len(missing)} icon sources: {missing[:5]}")
    gfx = ["spriteTypes = {\n"]
    for focus_id, *_ in entries:
        target = goal_path(focus_id)
        with Image.open(source_path(focus_id)) as image:
            art = image.convert("RGBA")
        art.thumbnail((94, 94), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (96, 96))
        canvas.alpha_composite(art, ((96 - art.width) // 2, (96 - art.height) // 2))
        smooth_icon_edge(canvas).save(target)
        relative = target.relative_to(ROOT).as_posix()
        name = sprite_name(focus_id)
        gfx.extend((sprite(name, relative), shine(name, relative)))
    gfx.append("}\n")
    GFX.write_text("".join(gfx), encoding="utf-8")

    original = FOCUSES.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    script = original.decode("utf-8-sig")
    matched = set()

    def replace(match: re.Match[str]) -> str:
        focus_id = match.group(2)
        matched.add(focus_id)
        return match.group(1) + sprite_name(focus_id)

    updated = re.sub(
        r"(?m)(^\s*id\s*=\s*(WHR_INT_[a-z0-9_]+)\r?\n\s*icon\s*=\s*)\S+",
        replace, script,
    )
    if matched != {row[0] for row in entries}:
        raise ValueError(f"Unassigned focus icons: {set(row[0] for row in entries) - matched}")
    FOCUSES.write_bytes((b"\xef\xbb\xbf" if bom else b"") + updated.encode("utf-8"))

    width, height = 8 * 150, 6 * 135
    preview = Image.new("RGB", (width, height), "#171c20")
    draw = ImageDraw.Draw(preview)
    font = ImageFont.load_default()
    for index, (focus_id, *_rest) in enumerate(entries):
        x = (index % 8) * 150 + 27
        y = (index // 8) * 135 + 3
        with Image.open(source_path(focus_id)) as icon:
            preview.paste(icon.resize((96, 96), Image.Resampling.LANCZOS), (x, y),
                          icon.resize((96, 96), Image.Resampling.LANCZOS))
        short = focus_id.removeprefix("WHR_INT_")
        draw.text((x - 20, y + 101), short[:22], font=font, fill="#e4ded1")
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW, optimize=True)
    print(f"Packaged {len(entries)} unique White Russian focus icons")


def check() -> None:
    entries = rows()
    gfx = GFX.read_text(encoding="utf-8")
    script = FOCUSES.read_text(encoding="utf-8-sig")
    names = re.findall(r'\bname = "([^"]+)"', gfx)
    expected_count = 2 * len(entries)
    if len(names) != expected_count or len(names) != len(set(names)):
        raise ValueError(f"Expected {expected_count} distinct base and shine sprites")
    references = re.findall(r"(?m)^\s*icon\s*=\s*(GFX_goal_WHR_INT_[a-z0-9_]+)", script)
    if len(references) != len(entries) or len(references) != len(set(references)):
        raise ValueError(f"Each of the {len(entries)} focuses must use a unique icon")
    if set(references) != {sprite_name(row[0]) for row in entries}:
        raise ValueError("Focus icons and sprite definitions differ")
    digests = []
    for focus_id, *_ in entries:
        source = source_path(focus_id)
        target = goal_path(focus_id)
        with Image.open(source) as image:
            if (image.size != (96, 96) and min(image.size) < 200) or image.mode != "RGBA":
                raise ValueError(f"Invalid source (expected native 96px or legacy 256px): {source}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Source lacks transparency: {source}")
        with Image.open(target) as image:
            if image.size != (96, 96) or image.mode != "RGBA":
                raise ValueError(f"Invalid DDS: {target}")
        digests.append(hashlib.sha256(target.read_bytes()).digest())
    if len(digests) != len(set(digests)):
        raise ValueError("Duplicate focus textures")
    print(f"Verified {len(entries)} distinct focus sprites and DDS textures")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-generated", nargs=2, metavar=("FOCUS_ID", "IMAGE"))
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.import_generated:
        import_generated(args.import_generated[0], Path(args.import_generated[1]))
    if args.package:
        package()
    if args.check:
        check()
