"""Import and wire one original icon for each Soviet interwar focus."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re

from PIL import Image

try:
    from .package_interwar_german_icons import shine
    from .interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge
except ImportError:
    from package_interwar_german_icons import shine
    from interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge


ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "common/national_focus/INT - RCW - Soviet Russia.txt"
SOURCE = ROOT / "gfx/interface/interwar_soviet/focus_source"
GOALS = ROOT / "gfx/interface/goals"
GFX = ROOT / "interface/endsieg_int_sov_focus_icons.gfx"


def focus_ids() -> list[str]:
    script = TREE.read_text(encoding="utf-8-sig")
    ids = re.findall(r"(?m)^\s*id\s*=\s*(SO2_INT_[A-Za-z0-9_]+)\s*$", script)
    if len(ids) != len(set(ids)):
        raise ValueError(f"Soviet interwar focus IDs are duplicated: {ids}")
    return ids


def source_path(focus_id: str) -> Path:
    return SOURCE / f"{focus_id}.png"


def goal_path(focus_id: str) -> Path:
    return GOALS / f"focus_{focus_id}.dds"


def sprite(focus_id: str) -> str:
    return f"GFX_goal_{focus_id}"


def import_generated(focus_id: str, image_path: Path) -> None:
    if focus_id not in focus_ids():
        raise ValueError(f"Unknown Soviet interwar focus: {focus_id}")
    with Image.open(image_path) as image:
        art = image.convert("RGBA")
    alpha = art.getchannel("A")
    if alpha.getextrema()[0] == 255:
        raise ValueError(f"Icon background is opaque: {image_path}")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError(f"Icon has no visible artwork: {image_path}")
    SOURCE.mkdir(parents=True, exist_ok=True)
    art = art.crop(bounds)
    art.thumbnail((256, 256), Image.Resampling.LANCZOS)
    solidify_icon_interior(art).save(source_path(focus_id), optimize=True)


def package() -> None:
    ids = focus_ids()
    available = [focus_id for focus_id in ids if source_path(focus_id).is_file()]
    gfx = ["spriteTypes = {\n"]
    for focus_id in available:
        with Image.open(source_path(focus_id)) as image:
            art = image.convert("RGBA")
        art.thumbnail((94, 94), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (96, 96))
        canvas.alpha_composite(art, ((96 - art.width) // 2, (96 - art.height) // 2))
        smooth_icon_edge(canvas).save(goal_path(focus_id))
        path = goal_path(focus_id).relative_to(ROOT).as_posix()
        gfx.extend((
            "\tspriteType = {\n",
            f'\t\tname = "{sprite(focus_id)}"\n',
            f'\t\ttexturefile = "{path}"\n',
            "\t}\n",
            shine(sprite(focus_id), path),
        ))
    gfx.append("}\n")
    GFX.write_text("".join(gfx), encoding="utf-8")

    raw = TREE.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    script = raw.decode("utf-8-sig")
    for focus_id in available:
        pattern = (r"(?m)(^\s*id\s*=\s*" + re.escape(focus_id) +
                   r"\s*\r?\n\s*icon\s*=\s*)\S+")
        script, count = re.subn(pattern, lambda m: m.group(1) + sprite(focus_id),
                                script, count=1)
        if count != 1:
            raise ValueError(f"Cannot assign icon for {focus_id}")
    TREE.write_bytes((b"\xef\xbb\xbf" if bom else b"") + script.encode("utf-8"))
    print(f"Packaged {len(available)} of {len(ids)} Soviet interwar focus icons")


def check() -> None:
    ids = focus_ids()
    available = [focus_id for focus_id in ids if source_path(focus_id).is_file()]
    script = TREE.read_text(encoding="utf-8-sig")
    gfx = GFX.read_text(encoding="utf-8") if GFX.is_file() else ""
    hashes = []
    for focus_id in available:
        if f"icon = {sprite(focus_id)}" not in script:
            raise ValueError(f"Focus icon reference missing: {focus_id}")
        if f'name = "{sprite(focus_id)}"' not in gfx:
            raise ValueError(f"Focus sprite missing: {focus_id}")
        if f'name = "{sprite(focus_id)}_shine"' not in gfx:
            raise ValueError(f"Focus shine sprite missing: {focus_id}")
        path = goal_path(focus_id)
        if not path.is_file():
            raise ValueError(f"Focus texture missing or wrong size: {focus_id}")
        with Image.open(path) as image:
            if image.size != (96, 96) or image.mode != "RGBA":
                raise ValueError(f"Focus texture missing or wrong size/mode: {focus_id}: {image.size} {image.mode}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Focus texture lacks proper alpha: {focus_id}")
        with Image.open(source_path(focus_id)) as image:
            if (image.size != (96, 96) and min(image.size) < 200) or image.mode != "RGBA":
                raise ValueError(f"Invalid native/legacy source: {source_path(focus_id)}: {image.size}")
        hashes.append(hashlib.sha256(source_path(focus_id).read_bytes()).digest())
    if Counter(hashes).most_common(1) and Counter(hashes).most_common(1)[0][1] > 1:
        raise ValueError("Duplicate Soviet interwar focus artwork")
    print(f"Verified {len(available)} distinct Soviet interwar focus icons")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-generated", nargs=2, metavar=("FOCUS_ID", "IMAGE"))
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list-ids", action="store_true")
    args = parser.parse_args()
    if args.list_ids:
        print("\n".join(focus_ids()))
    if args.import_generated:
        import_generated(args.import_generated[0], Path(args.import_generated[1]))
    if args.package:
        package()
    if args.check:
        check()


if __name__ == "__main__":
    main()
