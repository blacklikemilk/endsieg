"""Package the shared German interwar idea and decision icon masters.

The source PNGs in gfx/interface/interwar_german/source are the editable masters.
Run ``python tools/package_interwar_german_icons.py`` after changing a master.
Use ``--import-generated DIR`` once to turn named ImageGen PNGs in DIR into
transparent, 256-pixel masters. This import only removes the neutral backdrop;
the emblem and its frame remain unchanged.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "gfx/interface/interwar_german/source"
THEMES = (
    "republic", "industry", "welfare", "twenties", "finance", "diplomacy",
    "military", "depression", "monarchy", "councils", "treaty", "trade",
    "science", "press", "public_works", "authoritarian",
)
SIZES = {
    "focus": (96, 96),
    "idea": (60, 68),
    "decision": (33, 32),
    "category": (52, 40),
}


def remove_neutral_backdrop(image: Image.Image) -> Image.Image:
    """Flood-fill the connected pale neutral canvas around an emblem."""
    if image.mode == "RGBA" and image.getextrema()[3][0] == 0:
        return image
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    seen = bytearray(width * height)
    queue = deque()

    def neutral(x: int, y: int) -> bool:
        r, g, b = pixels[x, y]
        return max(r, g, b) - min(r, g, b) <= 30

    def add(x: int, y: int) -> None:
        position = y * width + x
        if not seen[position] and neutral(x, y):
            seen[position] = 1
            queue.append((x, y))

    for x in range(width):
        add(x, 0)
        add(x, height - 1)
    for y in range(height):
        add(0, y)
        add(width - 1, y)
    while queue:
        x, y = queue.popleft()
        if x > 0:
            add(x - 1, y)
        if x + 1 < width:
            add(x + 1, y)
        if y > 0:
            add(x, y - 1)
        if y + 1 < height:
            add(x, y + 1)

    rgba = rgb.convert("RGBA")
    rgba.putalpha(Image.frombytes("L", (width, height), bytes(0 if value else 255 for value in seen)))
    return rgba


def import_masters(directory: Path) -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        raw = directory / f"{theme}.png"
        import_one(theme, raw)


def import_one(theme: str, raw: Path) -> None:
    if theme not in THEMES:
        raise ValueError(f"Unknown shared German interwar theme: {theme}")
    if not raw.is_file():
        raise FileNotFoundError(raw)
    image = remove_neutral_backdrop(Image.open(raw))
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError(f"No opaque emblem in {raw}")
    image = image.crop(bounds)
    side = max(image.size)
    square = Image.new("RGBA", (side, side))
    square.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    square.resize((256, 256), Image.Resampling.LANCZOS).save(SOURCE / f"{theme}.png", optimize=True)


def sized_icon(master: Image.Image, kind: str) -> Image.Image:
    width, height = SIZES[kind]
    side = min(width, height)
    image = master.resize((side, side), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height))
    canvas.alpha_composite(image, ((width - side) // 2, (height - side) // 2))
    return canvas


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


def sprite_paths(path: Path) -> dict[str, str]:
    """Read sprite names and texture paths from a GFX definition file."""

    text = path.read_text(encoding="utf-8-sig")
    result: dict[str, str] = {}
    for name, texture in re.findall(
        r'spriteType\s*=\s*\{\s*name\s*=\s*"([^"]+)"\s*'
        r'texturefile\s*=\s*"([^"]+)"', text, flags=re.IGNORECASE
    ):
        if name in result:
            raise ValueError(f"Duplicate sprite name in {path}: {name}")
        result[name] = texture
    return result


def sprite_size(name: str) -> tuple[int, int] | None:
    if name.startswith("GFX_idea_"):
        return SIZES["idea"]
    if name.startswith("GFX_decision_category_"):
        return SIZES["category"]
    if name.startswith("GFX_decision_"):
        return SIZES["decision"]
    if name.startswith("GFX_goal_"):
        return SIZES["focus"]
    return None


def package() -> None:
    gfx = ["spriteTypes = {\n"]
    for theme in THEMES:
        source = SOURCE / f"{theme}.png"
        if not source.is_file():
            raise FileNotFoundError(source)
        master = Image.open(source).convert("RGBA")
        for kind in ("idea", "decision", "category"):
            directory = "decisions" if kind in ("decision", "category") else ("goals" if kind == "focus" else "ideas")
            path = f"gfx/interface/{directory}/{kind}_INT_GER_{theme}.dds"
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            sized_icon(master, kind).save(target)
            prefix = {
                "focus": "GFX_goal_", "idea": "GFX_idea_",
                "decision": "GFX_decision_", "category": "GFX_decision_category_",
            }[kind]
            name = f"{prefix}INT_GER_{theme}"
            gfx.append(sprite(name, path))
    gfx.append("}\n")
    (ROOT / "interface/endsieg_interwar_icons.gfx").write_text("".join(gfx), encoding="utf-8")


def validate() -> None:
    from assign_interwar_german_icons import FILES

    gfx_file = ROOT / "interface/endsieg_interwar_icons.gfx"
    gfx = gfx_file.read_text(encoding="utf-8")
    if gfx.count("{") != gfx.count("}"):
        raise ValueError(f"Unbalanced braces in {gfx_file}")
    shared = sprite_paths(gfx_file)
    names = list(shared)
    if len(names) != len(set(names)):
        raise ValueError("Duplicate sprite names")
    expected_shared = {
        prefix + f"INT_GER_{theme}"
        for theme in THEMES
        for prefix in ("GFX_idea_", "GFX_decision_", "GFX_decision_category_")
    }
    if set(names) != expected_shared:
        raise ValueError(f"Shared theme sprite set differs: {set(names) ^ expected_shared}")
    textures = list(shared.values())
    if len(textures) != len(expected_shared) or len(set(textures)) != len(expected_shared):
        raise ValueError(f"Expected {len(expected_shared)} distinct shared DDS files, found {len(set(textures))}")

    unique_gfx_file = ROOT / "interface/endsieg_interwar_unique_ideas.gfx"
    unique = sprite_paths(unique_gfx_file) if unique_gfx_file.is_file() else {}
    sprites = set(shared) | set(unique)
    all_paths = dict(shared)
    for name, raw_path in unique.items():
        if name in all_paths and all_paths[name] != raw_path:
            raise ValueError(f"Sprite defined with two textures: {name}")
        all_paths[name] = raw_path
    for name, raw_path in all_paths.items():
        expected_size = sprite_size(name)
        if expected_size is None:
            continue
        raw_path = raw_path.replace("\\", "/")
        path = ROOT / raw_path
        if not path.is_file():
            raise FileNotFoundError(path)
        with Image.open(path) as image:
            if image.size != expected_size or image.mode != "RGBA":
                raise ValueError(f"Invalid sprite size or mode: {name}: {path}: {image.size} {image.mode}")
            lo, hi = image.getchannel("A").getextrema()
            if lo != 0 or hi != 255:
                raise ValueError(f"Invalid alpha range: {path}: {lo}..{hi}")
    counts = {}
    prefixes = {
        "focus": "", "idea": "GFX_idea_",
        "decision": "GFX_decision_", "category": "GFX_decision_category_",
    }
    for kind, paths in FILES.items():
        count = 0
        for raw_path in paths:
            script = (ROOT / raw_path).read_text(encoding="utf-8-sig")
            if script.count("{") != script.count("}"):
                raise ValueError(f"Unbalanced braces: {raw_path}")
            field = "picture" if kind == "idea" else "icon"
            for value in re.findall(rf"(?m)^\s*{field}\s*=\s*((?:GFX_goal_)?INT_GER_[A-Za-z0-9_]+)", script):
                name = prefixes[kind] + value
                if name not in sprites:
                    raise ValueError(f"Unresolved icon {name} in {raw_path}")
                count += 1
            if re.search(rf"(?m)^\s*{field}\s*=\s*(?:GFX_goal_generic|generic_)", script):
                raise ValueError(f"Generic icon remains in {raw_path}")
        counts[kind] = count
    print(f"Verified {len(sprites)} shared/bespoke sprites, {len(set(all_paths.values()))} textures, and {counts} assignments")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-generated", type=Path, metavar="DIR")
    parser.add_argument("--import-one", nargs=2, metavar=("THEME", "IMAGE"))
    parser.add_argument("--check", action="store_true", help="validate the existing packaged icons and references")
    args = parser.parse_args()
    if args.check:
        validate()
    else:
        if args.import_generated:
            import_masters(args.import_generated)
        if args.import_one:
            import_one(args.import_one[0], Path(args.import_one[1]))
        package()
