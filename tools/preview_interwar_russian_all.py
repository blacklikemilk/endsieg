"""Render complete Russian interwar icon sheets from game DDS textures."""

import argparse
import json
import math
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

import package_int_sov_focus_icons as sov
import package_int_whr_icons as whr
import package_interwar_idea_icons as ideas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "gfx/interface/interwar_redesign_previews"
ASSIGNMENTS = json.loads((ROOT / "tools/interwar_icon_assignments.json").read_text(encoding="utf-8"))


def font(size: int) -> ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def sheet(title: str, ids: list[str], kind: str, destination: Path, *, light: bool) -> None:
    columns = 7 if kind == "focus" else 8
    cell_w, cell_h = (160, 146) if kind == "focus" else (145, 125)
    rows = math.ceil(len(ids) / columns)
    canvas = Image.new("RGB", (columns * cell_w + 32, rows * cell_h + 85),
                       "#e5e2da" if light else "#171c20")
    draw = ImageDraw.Draw(canvas)
    draw.text((18, 12), title, font=font(21), fill="#303840" if light else "#e7dbbe")
    draw.text((18, 44), f"{len(ids)} unique packaged {kind} DDS textures at game size",
              font=font(13), fill="#52606a" if light else "#aeb8bc")
    draw.line((18, 66, canvas.width - 18, 66), fill="#9ba5a8" if light else "#49535c")
    for index, icon_id in enumerate(ids):
        col, row = index % columns, index // columns
        x, y = 18 + col * cell_w, 75 + row * cell_h
        if kind == "focus":
            path = (sov.goal_path(icon_id) if icon_id.startswith("SO2_INT_")
                    else whr.goal_path(icon_id))
            expected = (96, 96)
        else:
            path = ideas.texture_path(icon_id)
            expected = (60, 68)
        with Image.open(path) as image:
            art = image.convert("RGBA")
        if art.size != expected:
            raise ValueError(f"Wrong DDS size for {icon_id}: {art.size}")
        canvas.paste(art, (x + (cell_w - 32 - art.width) // 2, y), art)
        label = icon_id
        for prefix in ("SO2_INT_", "WHR_INT_", "INT_SOV_", "INT_WHR_", "INT_"):
            if label.startswith(prefix):
                label = label[len(prefix):]
                break
        label = " ".join(textwrap.wrap(label.replace("_", " "), width=21)[:2])
        draw.multiline_text((x + 2, y + (100 if kind == "focus" else 73)),
                            "\n".join(textwrap.wrap(label, 20)), font=font(12),
                            fill="#303840" if light else "#e1dbce", spacing=2)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, optimize=True)
    print(destination)


def main(*, light: bool = False) -> None:
    sov_ids = sov.focus_ids()
    whr_ids = [row[0] for row in whr.rows()]
    sov_ideas = [row["id"] for row in ASSIGNMENTS["sov_ideas"]]
    whr_ideas = [row["id"] for row in ASSIGNMENTS["whr_ideas"]]
    for icon_id in sov_ideas + whr_ideas:
        if not ideas.source_path(icon_id).is_file():
            raise FileNotFoundError(f"Missing redesigned idea: {icon_id}")
    suffix = "_light.png" if light else ".png"
    sheet("SOVIET INTERWAR FOCUSES", sov_ids, "focus", OUT / f"soviet_focus_complete{suffix}", light=light)
    sheet("WHITE RUSSIAN INTERWAR FOCUSES", whr_ids, "focus", OUT / f"white_russian_focus_complete{suffix}", light=light)
    sheet("SOVIET AND SHARED INTERWAR IDEAS", sov_ideas, "idea", OUT / f"soviet_ideas_complete{suffix}", light=light)
    sheet("WHITE RUSSIAN INTERWAR IDEAS", whr_ideas, "idea", OUT / f"white_russian_ideas_complete{suffix}", light=light)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--light", action="store_true", help="inspect contours on a light background")
    main(light=parser.parse_args().light)
