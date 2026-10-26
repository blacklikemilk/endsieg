"""Build the scenario-selection interface artwork for Endsieg.

Purpose
-------
Turns the generated source paintings in ``.tmp/scenario_art`` into the sprites the
scenario (bookmark) screen uses, and draws every piece of typography and framing in
code so the result is pixel-exact and never depends on an image model spelling the
letters correctly.

Outputs (all DXT5 `.dds` under ``gfx/interface/scenario_select``):
    card_<scenario>.dds  228x132  scenario plates, scaled from the 180x104 originals
    card_frame.dds       496x192  two frames of 248x192 side by side: normal, selected
    scenario_bg.dds     1600x800  header wordmark, card field, detail panel, footer

The engine fills each card's painting (``icon``) from the bookmark's ``picture``
sprite, its ``date`` label from the start date, and switches the frame to frame 1
while the card is selected. Everything else on the screen is static art drawn here:
the ENDSIEG wordmark, the "1910 - 1945" plate and the compass inset. The year burned
into each painting is language-neutral; the exact date comes from the engine label
underneath it.

Sources live in ``.tmp/scenario_art`` (ignored by git); the built sprites are
committed, so the mod does not need the sources to ship.

Usage
-----
    python tools/build_scenario_art.py            # build every sprite
    python tools/build_scenario_art.py --preview  # also write .tmp/card_preview.png
    python tools/build_scenario_art.py --check    # report crop sizes only
"""

from __future__ import annotations

import argparse
import math
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, ".tmp", "scenario_art")
OUT_DIR = os.path.join(ROOT, "gfx", "interface", "scenario_select")

# Serif for the wordmark, the years and the plates. Falls back to Pillow's bitmap
# default if the host has none of these (this is a dev-machine build tool).
FONT_CANDIDATES = (
    "C:/Windows/Fonts/constanb.ttf",
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/timesbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
)

# sprite stem -> (source file, pixels cut from the bottom, year burned into the art)
SOURCE_DIR = os.path.join(ROOT, "gfx", "interface")

# sprite stem -> original Endsieg year plate, kept in gfx/interface
SOURCES = {
    "card_1910": "select_date_1910.dds",
    "card_1914": "select_date_1914.dds",
    "card_1916": "select_date_1916.dds",
    "card_1918": "select_date_1918.dds",
    "card_1936": "select_date_1936.dds",
    "card_1939": "select_date_1939.dds",
    "card_1941": "select_date_1941.dds",
    "card_1942": "select_date_1942.dds",
    "card_1943": "select_date_1943.dds",
    "card_1944_06": "select_date_1944.dds",
    "card_1944_12": "select_date_1945.dds",
    "card_1945_03": "select_date_1945_2.dds",
}

ART_W, ART_H = 228, 132          # painting size inside the card; the icon is drawn 1:1
CARD_W, CARD_H = ART_W, ART_H    # iconType has no scale/size, so art is built at display size
FRAME_W, FRAME_H = 248, 192      # bookmark_entry size in frontendgamesetupview.gui
BG_W, BG_H = 1600, 800           # gamesetup_scenario_window size

PANEL_TOP = 566                  # top of the detail panel in the background sprite

# Per-source tone correction, measured on the contact sheet: the dark cabinet and
# trench scenes need lifting so they still read at card size.
# stem -> (brightness, contrast)
TONE = {
    "card_1910": (1.45, 1.10),
    "card_1914": (1.05, 1.05),
    "card_1916": (1.32, 1.16),
    "card_1918": (1.10, 1.15),
    "card_1936": (1.10, 1.10),
    "card_1939": (1.06, 1.08),
    "card_1941": (1.02, 1.05),
    "card_1942": (1.04, 1.05),
    "card_1943": (1.05, 1.05),
    "card_1944_06": (1.16, 1.10),
    "card_1944_12": (1.18, 1.10),
    "card_1945_03": (1.12, 1.10),
}

GOLD = (201, 169, 107)
GOLD_BRIGHT = (232, 214, 170)
GOLD_DIM = (125, 106, 69)
STEEL = (42, 40, 37)
STEEL_LIGHT = (75, 70, 64)


def font(size: int):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def tracked(text: str, face, spacing: int) -> Image.Image:
    """Render text with letter spacing on a transparent canvas (white alpha mask)."""
    boxes = [face.getbbox(ch) for ch in text]
    widths = [b[2] - b[0] for b in boxes]
    total = sum(widths) + spacing * max(0, len(text) - 1)
    height = max(b[3] for b in boxes) + 6
    img = Image.new("RGBA", (max(1, total + 8), height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 4
    for ch, box, w in zip(text, boxes, widths):
        d.text((x - box[0], 2 - box[1]), ch, font=face, fill=(255, 255, 255, 255))
        x += w + spacing
    return img


def gold_fill(mask: Image.Image) -> Image.Image:
    """Fill a white alpha mask with a vertical gold gradient."""
    w, h = mask.size
    grad = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / float(max(1, h - 1))
        gd.line([(0, y), (w, y)],
                fill=tuple(int(GOLD_BRIGHT[i] + (GOLD[i] - GOLD_BRIGHT[i]) * t) for i in range(3)))
    out = grad.convert("RGBA")
    out.putalpha(mask.getchannel("A"))
    return out


def embossed(canvas: Image.Image, art: Image.Image, xy, strength: float = 0.55) -> None:
    """Composite art onto `canvas` with a soft dark drop shadow."""
    shadow = Image.new("RGBA", art.size, (0, 0, 0, 210))
    shadow.putalpha(art.getchannel("A").point(lambda v: int(v * strength)))
    canvas.alpha_composite(shadow, (xy[0] + 2, xy[1] + 3))
    canvas.alpha_composite(art, xy)


def crop_to(img: Image.Image, ratio: float, vertical_bias: float = 0.45) -> Image.Image:
    """Crop to a target width/height ratio, keeping the horizontal centre."""
    w, h = img.size
    if w / h > ratio:
        new_w = int(round(h * ratio))
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(round(w / ratio))
    top = int(round((h - new_h) * vertical_bias))
    return img.crop((0, top, w, top + new_h))


def build_cards(check_only: bool = False) -> None:
    for stem, name in SOURCES.items():
        path = os.path.join(SOURCE_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with Image.open(path) as im:
            im = im.convert("RGB")
            w, h = im.size
            card = crop_to(im, ART_W / ART_H)
            if check_only:
                print(f"{stem}: {name} {w}x{h} -> {card.size}")
                continue
            # The 180x104 originals carry their own year, grain and vignette, so
            # they are only scaled up to the card window (1.27x), never redrawn.
            card = card.resize((CARD_W, CARD_H), Image.LANCZOS)
            card = ImageEnhance.Contrast(card).enhance(1.04)
            card.convert("RGBA").save(os.path.join(OUT_DIR, stem + ".dds"), pixel_format="DXT5")
            print(f"wrote {stem}.dds")


def _panel(frame: int) -> Image.Image:
    """One card frame, drawn on transparent."""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    selected = frame == 1

    outer = GOLD if selected else STEEL
    inner = (224, 197, 138) if selected else STEEL_LIGHT
    band_top = (34, 31, 27) if selected else (27, 25, 22)
    band_bottom = (18, 17, 15) if selected else (12, 11, 10)
    art_bottom = 10 + ART_H          # first row of the caption band
    right = FRAME_W - 5

    d.rectangle([4, 4, right, FRAME_H - 5], fill=band_bottom)
    d.rectangle([4, 4, right, art_bottom - 1], fill=(20, 19, 17))

    for y in range(art_bottom, FRAME_H - 4):
        t = (y - art_bottom) / float(FRAME_H - 5 - art_bottom)
        colour = tuple(int(band_top[i] + (band_bottom[i] - band_top[i]) * t) for i in range(3))
        d.line([(4, y), (right, y)], fill=colour + (255,))

    d.rectangle([4, 4, right, FRAME_H - 5], outline=outer + (255,))
    d.rectangle([5, 5, FRAME_W - 6, FRAME_H - 6], outline=inner + (110 if not selected else 200,))
    d.line([(5, art_bottom - 1), (FRAME_W - 6, art_bottom - 1)],
           fill=GOLD + (255 if selected else 150,))

    if selected:
        d.rectangle([6, 6, FRAME_W - 7, FRAME_H - 7], outline=GOLD_BRIGHT + (130,))
        d.rectangle([7, 7, FRAME_W - 8, FRAME_H - 8], outline=(232, 205, 150, 60))
        d.line([(5, FRAME_H - 6), (FRAME_W - 6, FRAME_H - 6)], fill=GOLD + (255,))
        d.line([(5, art_bottom - 2), (FRAME_W - 6, art_bottom - 2)], fill=GOLD_BRIGHT + (200,))

    d.rectangle([3, 3, FRAME_W - 4, FRAME_H - 4], outline=(0, 0, 0, 90))
    return img


def build_frame() -> None:
    # HOI4 splits a multi-frame sprite sheet horizontally (vanilla's own
    # bookmark_entry_bg is 464x211 for two 232x211 frames), so the selected
    # frame goes to the right of the normal one, not below it.
    sheet = Image.new("RGBA", (FRAME_W * 2, FRAME_H), (0, 0, 0, 0))
    sheet.paste(_panel(0), (0, 0))
    sheet.paste(_panel(1), (FRAME_W, 0))
    sheet.save(os.path.join(OUT_DIR, "card_frame.dds"), pixel_format="DXT5")
    print("wrote card_frame.dds")


def _texture(name: str, size: tuple[int, int]) -> Image.Image:
    with Image.open(os.path.join(SRC_DIR, name)) as im:
        im = im.convert("RGB")
        return crop_to(im, size[0] / size[1]).resize(size, Image.LANCZOS)


def _shade(img: Image.Image, factor: float) -> Image.Image:
    return Image.eval(img, lambda v: min(255, int(v * factor)))


def _vignette(img: Image.Image, strength: int) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w * 0.35, -h * 0.45, w * 1.35, h * 1.45], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) // 5))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(img, Image.blend(img, dark, strength / 100.0), mask)


def _compass(canvas: Image.Image, cx: int, cy: int, radius: int, alpha: int) -> None:
    """Engraved compass rose, composited onto `canvas`."""
    size = radius * 2 + 4
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    o = radius + 2
    for i in range(16):
        ang = math.radians(i * 22.5)
        reach = radius if i % 4 == 0 else radius * 0.55
        d.line([(o, o), (o + math.sin(ang) * reach, o - math.cos(ang) * reach)],
               fill=GOLD_DIM + (alpha,), width=1)
    r = radius * 0.28
    d.ellipse([o - r, o - r, o + r, o + r], outline=GOLD_DIM + (alpha,))
    canvas.alpha_composite(layer, (cx - o, cy - o))


def build_background() -> None:
    bg = _texture("tex_ash.png", (BG_W, BG_H))
    bg = _shade(bg, 0.55)
    bg = Image.blend(bg, Image.new("RGB", (BG_W, BG_H), (18, 17, 16)), 0.45)
    bg = _vignette(bg, 55).convert("RGBA")

    # Faint cartographic graticule behind the cards.
    grid = Image.new("RGBA", (BG_W, BG_H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, BG_W, 80):
        gd.line([(x, 150), (x, PANEL_TOP - 8)], fill=(150, 140, 118, 8))
    for y in range(150, PANEL_TOP - 8, 80):
        gd.line([(0, y), (BG_W, y)], fill=(150, 140, 118, 8))
    bg = Image.alpha_composite(bg, grid)

    # --- header plate -------------------------------------------------------
    header = Image.new("RGB", (BG_W, 150), (15, 14, 13))
    header = Image.blend(header, _texture("tex_ash.png", (BG_W, 150)), 0.30)
    bg.paste(header.convert("RGBA"), (0, 0))

    mark = gold_fill(tracked("ENDSIEG", font(82), 11))
    embossed(bg, mark, ((BG_W - mark.size[0]) // 2, 18), 0.5)

    d = ImageDraw.Draw(bg)
    cy = 112
    d.line([(430, cy), (768, cy)], fill=GOLD_DIM + (255,))
    d.line([(832, cy), (1170, cy)], fill=GOLD_DIM + (255,))
    cx = BG_W // 2
    d.polygon([(cx, cy - 7), (cx + 7, cy), (cx, cy + 7), (cx - 7, cy)], outline=GOLD + (255,))
    d.line([(0, 147), (BG_W, 147)], fill=(0, 0, 0))
    d.line([(0, 148), (BG_W, 148)], fill=GOLD_DIM)
    d.line([(0, 149), (BG_W, 149)], fill=(0, 0, 0))

    # --- detail panel -------------------------------------------------------
    panel = Image.new("RGB", (BG_W, BG_H - PANEL_TOP), (16, 15, 14))
    panel = Image.blend(panel, _texture("tex_ash.png", (BG_W, BG_H - PANEL_TOP)), 0.10)
    panel = _shade(panel, 0.82)
    bg.paste(panel.convert("RGBA"), (0, PANEL_TOP))

    d = ImageDraw.Draw(bg)
    for i in range(1, 10):
        alpha = int(110 * (1 - i / 10.0) ** 1.5)
        d.line([(0, PANEL_TOP - i), (BG_W, PANEL_TOP - i)], fill=(0, 0, 0, alpha))
    d.line([(0, PANEL_TOP - 1), (BG_W, PANEL_TOP - 1)], fill=(0, 0, 0))
    d.line([(0, PANEL_TOP), (BG_W, PANEL_TOP)], fill=GOLD_DIM)
    d.line([(0, PANEL_TOP + 1), (BG_W, PANEL_TOP + 1)], fill=(58, 52, 41))

    # Compass inset on the right of the panel, where the design would carry a map.
    _compass(bg, 1270, (PANEL_TOP + BG_H) // 2 - 4, 100, 225)
    d = ImageDraw.Draw(bg)
    d.line([(1100, PANEL_TOP + 30), (1100, BG_H - 34)], fill=(90, 80, 56, 90))
    for x, y, sx, sy in (
        (1140, PANEL_TOP + 22, 1, 1),
        (1400, PANEL_TOP + 22, -1, 1),
        (1140, BG_H - 24, 1, -1),
        (1400, BG_H - 24, -1, -1),
    ):
        d.line([(x, y), (x + sx * 22, y)], fill=GOLD + (150,))
        d.line([(x, y), (x, y + sy * 22)], fill=GOLD + (150,))

    d.line([(0, BG_H - 10), (BG_W, BG_H - 10)], fill=(0, 0, 0))

    # Screen corner brackets.
    inset, arm = 10, 46
    for cx0, cy0, dx, dy in (
        (inset, inset, 1, 1),
        (BG_W - inset - 1, inset, -1, 1),
        (inset, BG_H - inset - 1, 1, -1),
        (BG_W - inset - 1, BG_H - inset - 1, -1, -1),
    ):
        d.line([(cx0, cy0), (cx0 + dx * arm, cy0)], fill=(110, 96, 66), width=2)
        d.line([(cx0, cy0), (cx0, cy0 + dy * arm)], fill=(110, 96, 66), width=2)

    bg.convert("RGB").save(os.path.join(OUT_DIR, "scenario_bg.dds"), pixel_format="DXT5")
    print("wrote scenario_bg.dds")


def build_preview() -> str:
    """A contact sheet of the finished cards at their in-game pixel size."""
    tiles = sorted(SOURCES)
    cols, gap = 6, 10
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new(
        "RGB",
        (cols * (ART_W + gap) + gap, rows * (ART_H + gap) + gap),
        (24, 23, 21),
    )
    for i, stem in enumerate(tiles):
        with Image.open(os.path.join(OUT_DIR, stem + ".dds")) as im:
            tile = im.convert("RGB").resize((ART_W, ART_H), Image.LANCZOS)
        x = gap + (i % cols) * (ART_W + gap)
        y = gap + (i // cols) * (ART_H + gap)
        sheet.paste(tile, (x, y))
    out = os.path.join(ROOT, ".tmp", "card_preview.png")
    sheet.save(out)
    print("preview ->", out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    if args.check:
        build_cards(check_only=True)
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    build_cards()
    build_frame()
    build_background()
    if args.preview:
        build_preview()


if __name__ == "__main__":
    main()
