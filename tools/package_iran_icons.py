#!/usr/bin/env python3
"""Package Iran focus icons: PNG sources to HOI4-ready 188x150 BGRA DDS.

The TFR benchmark icons are roughly 150-190 px wide, RGBA, on a pure black field.
This keeps that presentation: fit the art to 188x150 over black, no alpha
channel games, single mip level, uncompressed BGRA.

Usage:
    python tools/package_iran_icons.py --src <png dir> --out gfx/interface/goals/iran_campaign

Each <name>.png becomes <name>.dds. Names must match the GFX_<name> sprites in
interface/iran_campaign.gfx.
"""
from __future__ import annotations

import argparse
import os
import struct
import sys

from PIL import Image

WIDTH, HEIGHT = 188, 150


def write_dds(img: Image.Image, path: str) -> None:
    """Write an uncompressed 32-bit BGRA DDS with a single mip level."""
    img = img.convert("RGBA")
    w, h = img.size
    pixels = img.tobytes("raw", "BGRA")
    header = bytearray()
    header += b"DDS "
    header += struct.pack("<I", 124)                 # dwSize
    header += struct.pack("<I", 0x100F)              # CAPS|HEIGHT|WIDTH|PITCH|PIXELFORMAT
    header += struct.pack("<I", h)
    header += struct.pack("<I", w)
    header += struct.pack("<I", w * 4)               # pitch
    header += struct.pack("<I", 0)                   # depth
    header += struct.pack("<I", 1)                   # mipMapCount
    header += b"\x00" * 44                           # reserved
    header += struct.pack("<I", 32)                  # pf.dwSize
    header += struct.pack("<I", 0x41)                # DDPF_RGB|DDPF_ALPHAPIXELS
    header += struct.pack("<I", 0)                   # fourCC
    header += struct.pack("<I", 32)                  # rgbBitCount
    header += struct.pack("<I", 0x00FF0000)          # r mask
    header += struct.pack("<I", 0x0000FF00)          # g mask
    header += struct.pack("<I", 0x000000FF)          # b mask
    header += struct.pack("<I", 0xFF000000)          # a mask
    header += struct.pack("<I", 0x1000)              # DDSCAPS_TEXTURE
    header += struct.pack("<I", 0)                   # caps2
    header += struct.pack("<I", 0)                   # caps3
    header += struct.pack("<I", 0)                   # caps4
    header += struct.pack("<I", 0)                   # reserved2
    assert len(header) == 128, len(header)
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(pixels)


def fit_black(img: Image.Image) -> Image.Image:
    """Fit to the target canvas over black, preserving aspect and centring."""
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    art = img.convert("RGBA")
    art.thumbnail((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    canvas.paste(art, ((WIDTH - art.width) // 2, (HEIGHT - art.height) // 2), art)
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder of <name>.png icon sources")
    ap.add_argument("--out", required=True, help="target folder for <name>.dds")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    names = sorted(f for f in os.listdir(args.src) if f.lower().endswith(".png"))
    if not names:
        print("no PNG sources found", file=sys.stderr)
        return 1

    written = 0
    for name in names:
        stem = os.path.splitext(name)[0]
        src = os.path.join(args.src, name)
        dst = os.path.join(args.out, stem + ".dds")
        with Image.open(src) as img:
            write_dds(fit_black(img), dst)
        written += 1
        print(f"{stem}.dds  {WIDTH}x{HEIGHT}")
    print(f"\n{written} DDS written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
