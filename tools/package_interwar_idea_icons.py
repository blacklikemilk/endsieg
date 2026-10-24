"""Package distinct painted national-spirit icons for the interwar trees.

Import generated PNGs with ``--import-generated IDEA_ID IMAGE``. ``--package``
wires available icons without changing ideas whose artwork is still pending.
``--check`` verifies every imported texture and its matching script reference.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re

from PIL import Image

try:
    from .interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge
except ImportError:
    from interwar_icon_alpha import solidify_icon_interior, smooth_icon_edge


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "gfx/interface/interwar_ideas/source"
TEXTURES = ROOT / "gfx/interface/ideas"
GFX = ROOT / "interface/endsieg_interwar_unique_ideas.gfx"
FILES = (
    "common/ideas/INT - Germany.txt",
    "common/ideas/INT_German_Industry.txt",
    "common/ideas/INT_German_Paths.txt",
    "common/ideas/INT - Soviet Russia.txt",
    "common/ideas/INT - Soviet Union.txt",
    "common/ideas/INT_SOV_Paths.txt",
    "common/ideas/INT_WHR_Paths.txt",
    "common/ideas/INT - White Russia.txt",
    "common/ideas/INT - Great Depression.txt",
)
LEGACY_WHR = {"white_terror", "land_reforms", "recognized_by_west", "grain_confiscation"}
SHARED_DEPRESSION = {
    "INT_great_depression", "INT_SOV_great_depression", "INT_depression_aftershock"
}
IDEA_HEADER = re.compile(r"(?m)^\t\t([A-Za-z0-9_]+)\s*=\s*\{")


def ids_for_file(path: Path) -> list[str]:
    names = IDEA_HEADER.findall(path.read_text(encoding="utf-8-sig"))
    if path.name == "INT - White Russia.txt":
        return [name for name in names if name in LEGACY_WHR]
    if path.name == "INT - Great Depression.txt":
        return [name for name in names if name in SHARED_DEPRESSION]
    return names


def ideas() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for relative in FILES:
        path = ROOT / relative
        for name in ids_for_file(path):
            if name in result:
                raise ValueError(f"Duplicate idea ID: {name}")
            result[name] = path
    return result


def token(idea_id: str) -> str:
    return "INT_WHR_legacy_" + idea_id if idea_id in LEGACY_WHR else idea_id


def source_path(idea_id: str) -> Path:
    return SOURCE / f"{idea_id}.png"


def texture_path(idea_id: str) -> Path:
    return TEXTURES / f"idea_{token(idea_id)}.dds"


def import_generated(idea_id: str, image_path: Path) -> None:
    if idea_id not in ideas():
        raise ValueError(f"Unknown interwar idea: {idea_id}")
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
    solidify_icon_interior(art).save(source_path(idea_id), optimize=True)


def render_icon(idea_id: str) -> None:
    with Image.open(source_path(idea_id)) as image:
        art = image.convert("RGBA")
    art.thumbnail((58, 66), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (60, 68))
    canvas.alpha_composite(art, ((60 - art.width) // 2, (68 - art.height) // 2))
    smooth_icon_edge(canvas).save(texture_path(idea_id))


def replace_picture(script: str, idea_id: str, value: str) -> str:
    match = re.search(r"(?m)^\t\t" + re.escape(idea_id) + r"\s*=\s*\{", script)
    if match is None:
        raise ValueError(f"Missing idea block: {idea_id}")
    opening = script.index("{", match.start(), match.end())
    depth = 1
    cursor = opening + 1
    while depth and cursor < len(script):
        if script[cursor] == "{":
            depth += 1
        elif script[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise ValueError(f"Unbalanced idea block: {idea_id}")
    block = script[match.start():cursor]
    picture = re.compile(r"(?m)^(\t\t\tpicture\s*=\s*)\S+")
    if picture.search(block):
        block = picture.sub(lambda m: m.group(1) + value, block, count=1)
    else:
        block = block.replace("{", "{\n\t\t\tpicture = " + value, 1)
    return script[:match.start()] + block + script[cursor:]


def package() -> None:
    all_ideas = ideas()
    available = [name for name in all_ideas if source_path(name).is_file()]
    gfx = ["spriteTypes = {\n"]
    for name in available:
        render_icon(name)
        gfx.append(
            f'\tspriteType = {{\n\t\tname = "GFX_idea_{token(name)}"\n'
            f'\t\ttexturefile = "{texture_path(name).relative_to(ROOT).as_posix()}"\n\t}}\n'
        )
    gfx.append("}\n")
    GFX.write_text("".join(gfx), encoding="utf-8")
    for path in set(all_ideas.values()):
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        script = raw.decode("utf-8-sig")
        for name in available:
            if all_ideas[name] == path:
                script = replace_picture(script, name, token(name))
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + script.encode("utf-8"))
    print(f"Packaged {len(available)} of {len(all_ideas)} unique interwar idea icons")


def check() -> None:
    all_ideas = ideas()
    available = [name for name in all_ideas if source_path(name).is_file()]
    gfx = GFX.read_text(encoding="utf-8") if GFX.is_file() else ""
    hashes = []
    for name in available:
        texture = texture_path(name)
        if not texture.is_file():
            raise ValueError(f"Missing texture for {name}")
        with Image.open(texture) as image:
            if image.size != (60, 68) or image.mode != "RGBA":
                raise ValueError(f"Wrong idea size/mode for {name}: {image.size} {image.mode}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Idea texture lacks proper alpha for {name}")
        if f'name = "GFX_idea_{token(name)}"' not in gfx:
            raise ValueError(f"Missing GFX sprite for {name}")
        script = all_ideas[name].read_text(encoding="utf-8-sig")
        if f"picture = {token(name)}" not in script:
            raise ValueError(f"Idea does not reference unique picture: {name}")
        source = source_path(name)
        with Image.open(source) as image:
            if (image.size != (60, 68) and min(image.size) < 200) or image.mode != "RGBA":
                raise ValueError(f"Invalid native/legacy source for {name}: {image.size} {image.mode}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Idea source lacks proper alpha for {name}")
        hashes.append(hashlib.sha256(source_path(name).read_bytes()).digest())
    if Counter(hashes).most_common(1) and Counter(hashes).most_common(1)[0][1] > 1:
        raise ValueError("Duplicate idea artwork")
    print(f"Verified {len(available)} unique interwar idea icons")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-generated", nargs=2, metavar=("IDEA_ID", "IMAGE"))
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list-ids", action="store_true")
    args = parser.parse_args()
    if args.list_ids:
        print("\n".join(ideas()))
    if args.import_generated:
        import_generated(args.import_generated[0], Path(args.import_generated[1]))
    if args.package:
        package()
    if args.check:
        check()


if __name__ == "__main__":
    main()
