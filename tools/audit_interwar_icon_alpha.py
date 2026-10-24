"""Flag source icons with opaque neutral backdrop in their outer corners."""

import argparse
from pathlib import Path

from PIL import Image

from package_interwar_german_icons import remove_neutral_backdrop


ROOT = Path(__file__).resolve().parents[1]
DIRS = (
    ROOT / "gfx/interface/interwar_german/focus_source",
    ROOT / "gfx/interface/interwar_soviet/focus_source",
    ROOT / "gfx/interface/interwar_whr/focus_source",
    ROOT / "gfx/interface/interwar_ideas/source",
)


def neutral_corner_fraction(path: Path) -> float:
    with Image.open(path) as image:
        image = image.convert("RGBA")
    width, height = image.size
    side = max(4, min(width, height) // 8)
    pixels = image.load()
    count = suspect = 0
    for y in list(range(side)) + list(range(height - side, height)):
        for x in list(range(side)) + list(range(width - side, width)):
            red, green, blue, alpha = pixels[x, y]
            count += 1
            if alpha > 180 and max(red, green, blue) - min(red, green, blue) < 28:
                suspect += 1
    return suspect / count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-idea-backgrounds", action="store_true",
                        help="remove connected baked neutral backdrops from flagged idea sources")
    args = parser.parse_args()
    flagged = []
    for directory in DIRS:
        if directory.is_dir():
            for path in directory.glob("*.png"):
                fraction = neutral_corner_fraction(path)
                if fraction > 0.15:
                    flagged.append((fraction, path.relative_to(ROOT)))
    for fraction, path in sorted(flagged, reverse=True):
        print(f"{fraction:.2f} {path}")
        if args.repair_idea_backgrounds and fraction > 0.75 and str(path).startswith(
            "gfx\\interface\\interwar_ideas\\source\\"
        ):
            absolute = ROOT / path
            with Image.open(absolute) as image:
                repaired = remove_neutral_backdrop(image.convert("RGB"))
            bounds = repaired.getchannel("A").getbbox()
            if bounds is None:
                raise ValueError(f"Backdrop repair removed entire icon: {absolute}")
            repaired.crop(bounds).save(absolute, optimize=True)
            print(f"Repaired {path}")
    print(f"Flagged {len(flagged)} sources for backdrop inspection")


if __name__ == "__main__":
    main()
