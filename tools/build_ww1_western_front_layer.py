"""Build the German General Staff panel's live province and front-line overlays.

Run from any directory with Python 3 and Pillow. Coordinates are top-down in
Endsieg's provinces.bmp. Province IDs and state ownership come from the mod.
Only the marked sections of the two hand-maintained UI files are regenerated.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CROP = (2770, 482, 2986, 606)
SIZE = (466, 268)
TEXTURES = ROOT / "gfx/interface/endsieg_ww1_western_plans/live"
BEGIN = "# BEGIN generated western province layer"
END = "# END generated western province layer"


def province_grid():
    lookup = {}
    with (ROOT / "map/definition.csv").open(encoding="utf-8-sig") as f:
        for row in csv.reader(f, delimiter=";"):
            lookup[tuple(map(int, row[1:4]))] = int(row[0]) if row[4] == "land" else 0
    with Image.open(ROOT / "map/provinces.bmp") as original:
        cropped = original.crop(CROP).convert("RGB").resize(SIZE, Image.Resampling.NEAREST)
    return [lookup[pixel] for pixel in cropped.getdata()]


def province_states():
    states = {}
    for f in sorted((ROOT / "history/states").glob("*.txt")):
        text = re.sub(r"#.*", "", f.read_text(encoding="utf-8-sig", errors="replace"))
        state = re.search(r"\bid\s*=\s*(\d+)", text)
        ids = re.search(r"\bprovinces\s*=\s*\{([^}]+)\}", text)
        if state and ids:
            for number in map(int, re.findall(r"\b\d+\b", ids[1])):
                states[number] = int(state[1])
    return states


def geometry(grid):
    w, h = SIZE
    provinces, borders = defaultdict(list), defaultdict(list)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            pid = grid[i]
            if not pid:
                continue
            provinces[pid].append((x, y))
            for neighbour in (grid[i + 1] if x < w - 1 else 0,
                              grid[i + w] if y < h - 1 else 0):
                if neighbour and pid != neighbour:
                    borders[tuple(sorted((pid, neighbour)))].append((x, y))
    return provinces, borders


def tiles(points, border):
    """Crop every shape tightly. Adjacent provinces use the same hatch origin."""
    xs, ys = zip(*points)
    pad = int(border)
    x0, y0 = max(0, min(xs) - pad), max(0, min(ys) - pad)
    width = min(SIZE[0] - 1, max(xs) + pad) - x0 + 1
    height = min(SIZE[1] - 1, max(ys) + pad) - y0 + 1
    images = []
    if border:
        core = Image.new("L", (width, height))
        for x, y in points:
            core.putpixel((x - x0, y - y0), 255)
        image = Image.new("RGBA", (width, height), (151, 42, 34, 0))
        image.putalpha(core.filter(ImageFilter.MaxFilter(3)).point(lambda p: p * 0.88))
        image.paste((255, 231, 184, 255), (0, 0, width, height), core)
        images.append(image)
    else:
        for fill, stripe in [((128, 80, 16, 106), (250, 193, 82, 192)),
                             ((25, 75, 111, 130), (125, 201, 239, 200))]:
            image = Image.new("RGBA", (width, height))
            for x, y in points:
                image.putpixel((x - x0, y - y0), stripe if (x + y) % 6 == 0 else fill)
            images.append(image)
    return (x0, y0), images


def pack_atlases(shapes):
    # HOI4 sprites have uniformly sized horizontal frames. Bucket similar
    # tiles together and cap atlas width to avoid GPU-size assumptions.
    buckets = defaultdict(list)
    for name, pos, image, test in shapes:
        dims = tuple((n + 7) // 8 * 8 for n in image.size)
        buckets[dims].append((name, pos, image, test))
    gfx, icons, checks = [], [], []
    TEXTURES.mkdir(parents=True, exist_ok=True)
    for (width, height), group in sorted(buckets.items()):
        count = min(2048 // width, 64)
        for start in range(0, len(group), count):
            items = group[start:start + count]
            name = f"wf_{width}x{height}_{start // count}"
            sprite = "GFX_" + name
            atlas = Image.new("RGBA", (width * len(items), height))
            for index, (key, (x, y), image, test) in enumerate(items):
                atlas.paste(image, (index * width, 0))
                icons.append(f'\t\t\ticonType = {{ name = "{key}" position = {{ x = {x} y = {y} }} spriteType = "{sprite}" frame = {index+1} alwaystransparent = yes }}')
                checks.append(f"\t\t\t{key}_visible = {{ {test} }}")
            atlas.save(TEXTURES / (name + ".dds"))
            gfx.append(f'\tspriteType = {{ name = "{sprite}" texturefile = "gfx/interface/endsieg_ww1_western_plans/live/{name}.dds" noOfFrames = {len(items)} }}')
    # Atlas order is independent of draw order. All border icons follow fills.
    icons.sort(key=lambda line: ('name = "wf_line_' in line, line))
    (ROOT / "interface/endsieg_ww1_frontline_atlas.gfx").write_text(
        "spriteTypes = {\n" + "\n".join(gfx) + "\n}\n", encoding="utf-8")
    return icons, checks


def put_block(path, anchor, body, indent):
    # Preserve the rest of the file, including its original BOM and newlines.
    old = path.read_bytes()
    crlf = b"\r\n" in old
    text = old.decode("utf-8").replace("\r\n", "\n")
    begin, end = indent + BEGIN + "\n", indent + END + "\n"
    block = begin + "\n".join(body) + "\n" + end
    if begin in text:
        left, right = text.split(begin, 1)
        _, right = right.split(end, 1)
        text = left + block + right
    else:
        assert text.count(anchor) == 1, f"Expected exactly one insertion point: {path}"
        text = text.replace(anchor, block + anchor)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def main():
    provinces, borders = geometry(province_grid())
    states = province_states()
    shapes = []
    for pid, points in sorted(provinces.items()):
        pos, (ours, theirs) = tiles(points, False)
        for side, image, relation in [
            ("ours", ours, "OR = { tag = GER is_in_faction_with = GER has_war_together_with = GER }"),
            ("enemy", theirs, "has_war_with = GER"),
        ]:
            test = f"var:global.province_controllers^{pid} = {{ NOT = {{ owns_state = {states[pid]} }} {relation} }}"
            shapes.append((f"wf_{side}_{pid}", pos, image, test))
    for (a, b), points in sorted(borders.items()):
        pos, (line,) = tiles(points, True)
        # Evaluate from the actual controller scopes; neutral/friendly borders
        # and coastlines are never drawn as fronts.
        test = (f"var:global.province_controllers^{a} = {{ "
                f"var:global.province_controllers^{b} = {{ has_war_with = PREV }} }}")
        shapes.append((f"wf_line_{a}_{b}", pos, line, test))
    icons, checks = pack_atlases(shapes)
    panel = ['\t\tcontainerWindowType = {', '\t\t\tname = "wf_control_layer"',
             '\t\t\tposition = { x = 17 y = 61 }',
             f'\t\t\tsize = {{ width = {SIZE[0]} height = {SIZE[1]} }}',
             *icons, '\t\t}']
    put_block(ROOT / "interface/endsieg_ww1_western_plans.gui",
              '\t\ticonType = {\n\t\t\tname = "western_frontline_flanders_supply"', panel, "\t\t")
    checks.insert(0, "\t\t\twf_control_layer_visible = { WW1_western_frontline_available = yes }")
    put_block(ROOT / "common/scripted_guis/endsieg_ww1_western_plans.txt",
              "\t\t\twestern_plan_title_visible = ", checks, "\t\t\t")
    print(f"Built {len(provinces)} province masks and {len(borders)} shared land borders.")


if __name__ == "__main__":
    main()
