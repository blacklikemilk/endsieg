"""Generate the Cortes seat dot textures.

The chamber is drawn from one sprite strip: eight frames of a 16x16 disc, frame 0 the
neutral seat and frames 1..7 the parties in chamber order. A dot's frame is a country
variable, so the strip has to keep exactly the same party order as
tools/build_spain_cortes_hemicycle.py, which is checked here when that module is importable.
The single dots are still written because the legend swatch of each row uses its own sprite.

Each texture is an uncompressed 32-bit DDS, the format the engine reads for interface sprites.

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
STRIP = "spain_cortes_seats.dds"

# political order, left to right around the hemicycle; frame 0 is written separately
PARTIES = [
    ("socialists", (186, 46, 42)),
    ("republicans", (58, 122, 84)),
    ("liberals", (198, 162, 44)),
    ("conservatives", (108, 118, 132)),
    ("monarchists", (52, 78, 140)),
    ("carlists", (214, 206, 188)),
    ("falange", (48, 58, 108)),   # lifted off the dark panel background so its dots read
]

EMPTY = ("empty", (46, 44, 40))


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


def check_order() -> None:
    """Fail loudly if the strip order drifts from the order the chamber draws in."""
    try:
        from build_spain_cortes_hemicycle import PARTIES as chamber
    except ImportError:
        print("note: hemicycle module not importable, party order not cross-checked")
        return
    expected = [(name, None) for name, _colour in PARTIES]
    found = [(name, None) for name, _label, _govt in chamber]
    if [n for n, _ in expected] != [n for n, _ in found]:
        raise SystemExit("party order differs from tools/build_spain_cortes_hemicycle.py: %s vs %s"
                         % ([n for n, _ in expected], [n for n, _ in found]))
    print("party order matches the chamber generator: %d parties" % len(PARTIES))


def main() -> int:
    check_order()
    os.makedirs(OUT, exist_ok=True)

    frames = [EMPTY] + PARTIES
    strip = Image.new("RGBA", (SIZE * len(frames), SIZE), (0, 0, 0, 0))
    for index, (_name, colour) in enumerate(frames):
        strip.paste(disc(colour), (index * SIZE, 0))
    write_dds(strip, os.path.join(OUT, STRIP))
    print("wrote", os.path.join(OUT, STRIP), "%dx%d, %d frames"
          % (strip.size[0], strip.size[1], len(frames)))

    for name, colour in frames:
        path = os.path.join(OUT, "spain_cortes_dot_%s.dds" % name)
        write_dds(disc(colour), path)
        print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
