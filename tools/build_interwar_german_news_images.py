"""Package the six additional German interwar news photographs and check all 18.

The four external photographs are saved in gfx/event_pictures/interwar_news_sources.
The other two sources are existing Endsieg news images in 16-bit DDS format.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PICTURES = ROOT / "gfx" / "event_pictures"
SOURCES = PICTURES / "interwar_news_sources"
EVENTS = ROOT / "events" / "INT - German News.txt"
SIZE = (397, 153)

# The crop positions keep the event's subject within the very wide HOI4 news slot.
NEW_IMAGES = {
    "rapallo": ("news_event_rapallo.dds", None),
    "ruhr_occupation": ("news_event_ruhr_occupation.dds", None),
    "hyperinflation": ("hyperinflation.jpg", 0.50),
    "lausanne": ("lausanne.jpg", 0.36),
    "enabling_act": ("enabling_act.jpg", 0.78),
    "hindenburg_funeral": ("hindenburg_funeral.jpg", 0.63),
}


def read_source(path: Path) -> Image.Image:
    try:
        with Image.open(path) as source:
            return source.convert("RGBA")
    except OSError:
        pass

    # Older Endsieg photos use uncompressed A1R5G5B5 DDS, unsupported by Pillow.
    data = path.read_bytes()
    if data[:4] != b"DDS " or struct.unpack_from("<I", data, 88)[0] != 16:
        raise ValueError(f"Unsupported DDS source: {path}")
    height, width = struct.unpack_from("<II", data, 12)
    red, green, blue, alpha = struct.unpack_from("<IIII", data, 92)
    if (red, green, blue, alpha) != (0x7C00, 0x03E0, 0x001F, 0x8000):
        raise ValueError(f"Unexpected DDS channel masks: {path}")
    pixels = struct.unpack_from(f"<{width * height}H", data, 128)
    colors = [
        ((value >> 10 & 31) * 255 // 31,
         (value >> 5 & 31) * 255 // 31,
         (value & 31) * 255 // 31,
         255)
        for value in pixels
    ]
    image = Image.new("RGBA", (width, height))
    image.putdata(colors)
    return image


def news_crop(image: Image.Image, vertical_position: float | None) -> Image.Image:
    if vertical_position is None and image.size == SIZE:
        return image
    width, height = image.size
    target_ratio = SIZE[0] / SIZE[1]
    if width / height < target_ratio:
        crop_height = round(width / target_ratio)
        top = round((height - crop_height) * (vertical_position or 0.5))
        image = image.crop((0, top, width, top + crop_height))
    else:
        crop_width = round(height * target_ratio)
        left = (width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, height))
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def build() -> None:
    for name, (filename, vertical_position) in NEW_IMAGES.items():
        source = (SOURCES if filename.endswith(".jpg") else PICTURES) / filename
        image = news_crop(read_source(source), vertical_position)
        image.save(PICTURES / f"int_ger_news_{name}.dds", format="DDS")
    preview()


def preview() -> None:
    from audit_int_event_pictures import events
    from preview_int_event_pictures import sprites

    news = [record for record in events() if record["file"] == EVENTS.name]
    textures = sprites()
    sheet = Image.new("RGB", (SIZE[0] * 3, 180 * 6), "#202225")
    draw = ImageDraw.Draw(sheet)
    font_path = Path("C:/Windows/Fonts/consola.ttf")
    font = ImageFont.truetype(str(font_path), 11) if font_path.exists() else ImageFont.load_default()
    for index, record in enumerate(news):
        with Image.open(textures[record["picture"]]) as source:
            image = source.convert("RGB")
        x, y = (index % 3) * SIZE[0], (index // 3) * 180
        sheet.paste(image, (x, y))
        draw.text((x + 4, y + 157), f"{index + 1:02d}  {record['id']}", fill="white", font=font)
    sheet.save(PICTURES / "interwar_news_preview.png")


def check() -> None:
    from audit_int_event_pictures import events
    from preview_int_event_pictures import sprites

    references = [record["picture"] for record in events() if record["file"] == EVENTS.name]
    textures = sprites()
    if len(references) != 18 or len(set(references)) != 18:
        raise AssertionError("All 18 German interwar news events need distinct pictures")
    hashes = set()
    for reference in references:
        path = textures.get(reference)
        if path is None:
            raise AssertionError(f"Missing sprite: {reference}")
        with Image.open(path) as image:
            if image.size != SIZE:
                raise AssertionError(f"Wrong news picture dimensions: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:
            raise AssertionError(f"Duplicate news picture: {path}")
        hashes.add(digest)
    print("Verified 18 unique German interwar news images, sprites, and event references")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate packaged images and references")
    args = parser.parse_args()
    check() if args.check else build()
