"""Generate the Cortes hemicycle seat dots.

Each dot is a 16x16 antialiased disc in a party colour, written as an uncompressed
32-bit DDS (the format the engine reads for interface sprites). One extra dark dot
is used for seats that no bloc holds, so the ring always reads as a full chamber.

Run from the mod root:
    python tools/build_spain_cortes_dots.py
"""

from __future__ import annotations

import io
import os
import struct
import sys

from PIL import Image, ImageDraw

SIZE = 16
OUT = os.path.join("gfx", "interface", "endsieg_spain_dots")

# political order, left to right around the hemicycle
PARTIES = [
    ("socialists", (186, 46, 42)),
    ("republicans", (58, 122, 84)),
    ("liberals", (198, 162, 44)),
    ("conservatives", (108, 118, 132)),
    ("monarchists", (52, 78, 140)),
    ("carlists", (214, 206, 188)),
    ("falange", (28, 38, 66)),
    ("empty", (46, 44, 40)),
]


def write_dds(img: Image.Image, path: str) -> None:
    """Write an uncompressed 32-bit BGRA DDS with a single mip level."""
    img = img.convert("RGBA")
    w, h = img.size
    pixels = img.tobytes("raw", "BGRA")
    header = bytearray()
    header += b"DDS "
    header += struct.pack("<I", 124)
    header += struct.pack("<I", 0x100F)
    header += struct.pack("<I", h)
    header += struct.pack("<I", w)
    header += struct.pack("<I", w * 4)
    header += struct.pack("<I", 0)
    header += struct.pack("<I", 1)
    header += b"\x00" * 44
    header += struct.pack("<I", 32)
    header += struct.pack("<I", 0x41)
    header += struct.pack("<I", 0)
    header += struct.pack("<I", 32)
    header += struct.pack("<I", 0x00FF0000)
    header += struct.pack("<I", 0x0000FF00)
    header += struct.pack("<I", 0x000000FF)
    header += struct.pack("<I", 0xFF000000)
    header += struct.pack("<I", 0x1000)
    header += b"\x00" * 16
    with io.open(path, "wb") as fh:
        fh.write(bytes(header))
        fh.write(pixels)


def disc(colour: tuple[int, int, int]) -> Image.Image:
    """A disc with a soft edge, drawn at 4x and reduced so it does not look jagged."""
    scale = 4
    big = Image.new("RGBA", (SIZE * scale, SIZE * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    pad = scale  # keeps a one-pixel dark rim inside the sprite
    d.ellipse([pad, pad, SIZE * scale - pad - 1, SIZE * scale - pad - 1],
              fill=colour + (255,), outline=(18, 17, 16, 255), width=scale)
    return big.resize((SIZE, SIZE), Image.LANCZOS)


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    for name, colour in PARTIES:
        path = os.path.join(OUT, "spain_cortes_dot_%s.dds" % name)
        write_dds(disc(colour), path)
        print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
