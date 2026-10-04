"""Render geographic references from Endsieg's own province map.

These small images guide illustration edits; they are not game UI textures.
Europe uses the mod's land/sea province types, while Saarland uses the exact
province color assigned to state 1019 in this repository.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "gfx/interface/interwar_german/map_references"
DEFINITION = ROOT / "map/definition.csv"
PROVINCES = ROOT / "map/provinces.bmp"


def province_types() -> tuple[dict[tuple[int, int, int], str], dict[int, tuple[int, int, int]]]:
    types = {}
    ids = {}
    for line in DEFINITION.read_text(encoding="utf-8-sig").splitlines():
        fields = line.split(";")
        if len(fields) < 5:
            continue
        number = int(fields[0])
        color = tuple(map(int, fields[1:4]))
        types[color] = fields[4]
        ids[number] = color
    return types, ids


def europe(provinces: Image.Image, types: dict[tuple[int, int, int], str]) -> None:
    # The crop covers Iberia to western Russia, Scandinavia to North Africa.
    crop = provinces.crop((2600, 220, 3550, 920))
    sea = (29, 60, 76)
    land = (225, 210, 170)
    water = (52, 95, 112)
    result = Image.new("RGB", crop.size)
    result.putdata([land if types.get(pixel) == "land" else water if types.get(pixel) == "lake" else sea for pixel in crop.getdata()])
    result.thumbnail((760, 560), Image.Resampling.NEAREST)
    canvas = Image.new("RGB", (800, 600), (243, 239, 226))
    canvas.paste(result, ((800 - result.width) // 2, (600 - result.height) // 2))
    draw = ImageDraw.Draw(canvas)
    draw.text((18, 16), "ENDSIEG PROVINCE MAP: EUROPEAN LAND/SEA OUTLINE", fill=(30, 39, 43))
    draw.text((18, 577), "Reference only. Preserve the coastline; omit uncertain interior borders.", fill=(30, 39, 43))
    canvas.save(OUT / "europe_coastline.png")


def saar(provinces: Image.Image, ids: dict[int, tuple[int, int, int]]) -> None:
    color = ids[11531]
    diff = ImageChops.difference(provinces, Image.new("RGB", provinces.size, color))
    red, green, blue = diff.split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    mask = maximum.point(lambda value: 255 if value == 0 else 0)
    box = mask.getbbox()
    if not box:
        raise ValueError("Saarland province 11531 missing from provinces.bmp")
    region = mask.crop(box)
    region = region.resize((region.width * 16, region.height * 16), Image.Resampling.NEAREST)
    canvas = Image.new("RGB", (512, 400), (243, 239, 226))
    shape = Image.new("RGB", region.size, (169, 114, 47))
    canvas.paste(shape, ((512 - region.width) // 2, (400 - region.height) // 2), region)
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 16), "ENDSIEG SAARLAND: STATE 1019 / PROVINCE 11531", fill=(30, 39, 43))
    draw.text((16, 377), "Preserve this exact region silhouette in the plebiscite icon.", fill=(30, 39, 43))
    canvas.save(OUT / "saarland_shape.png")


def world(provinces: Image.Image, types: dict[tuple[int, int, int], str]) -> None:
    reduced = provinces.resize((1024, 372), Image.Resampling.NEAREST)
    sea = (29, 60, 76)
    land = (225, 210, 170)
    result = Image.new("RGB", reduced.size)
    result.putdata([land if types.get(pixel) == "land" else sea for pixel in reduced.getdata()])
    canvas = Image.new("RGB", (1056, 416), (243, 239, 226))
    canvas.paste(result, (16, 28))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 8), "ENDSIEG PROVINCE MAP: WORLD LAND/SEA OUTLINE", fill=(30, 39, 43))
    draw.text((16, 400), "Use coastline shapes for globes; omit modern political borders.", fill=(30, 39, 43))
    canvas.save(OUT / "world_coastline.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    types, ids = province_types()
    with Image.open(PROVINCES) as source:
        provinces = source.convert("RGB")
        europe(provinces, types)
        saar(provinces, ids)
        world(provinces, types)
    print("Rendered Europe, Saarland, and world reference shapes from map/provinces.bmp")
