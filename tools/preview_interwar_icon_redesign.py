"""Build labeled, game-size contact sheets for the redesigned interwar icons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENTS = ROOT / "tools/interwar_icon_assignments.json"
PREVIEWS = ROOT / "gfx/interface/interwar_redesign_previews"
FOCUS_DIRS = {
    "GER": ROOT / "gfx/interface/interwar_german/focus_source",
    "SOV": ROOT / "gfx/interface/interwar_soviet/focus_source",
    "WHR": ROOT / "gfx/interface/interwar_whr/focus_source",
}
IDEA_DIR = ROOT / "gfx/interface/interwar_ideas/source"


def entries(country: str, kind: str) -> list[str]:
    assignments = json.loads(ASSIGNMENTS.read_text(encoding="utf-8"))
    if kind == "focus":
        if country == "GER":
            all_ids = [entry["id"] for key in ("ger_focus_a", "ger_focus_b")
                       for entry in assignments[key]]
            return sorted(set(all_ids) | {
                "INT_GER_roaring_twenties", "INT_GER_political_turmoil",
                "INT_GER_food_relief", "INT_GER_reichswehr_compromise",
                "INT_GER_rebuild_economy", "INT_GER_reconstitute_civil_service",
                "INT_GER_reconstruction_commission", "INT_GER_restore_transport_links",
                "INT_GER_municipal_reconstruction", "INT_GER_reparations_crisis",
                "INT_GER_end_ruhr_resistance", "INT_GER_retain_the_republic",
                "INT_GER_hold_national_assembly_1919",
            })
        key = "sov_focus" if country == "SOV" else "whr_focus"
        keys = (key + "_a", key + "_b") if country == "SOV" else (key,)
        return [entry["id"] for part in keys for entry in assignments[part]]
    key = country.lower() + "_ideas"
    all_ids = [entry["id"] for entry in assignments[key]]
    return all_ids + (["INT_GER_dawes_credit"] if country == "GER" else [])


def source(country: str, kind: str, icon_id: str) -> Path:
    directory = FOCUS_DIRS[country] if kind == "focus" else IDEA_DIR
    return directory / f"{icon_id}.png"


def preview(country: str, kind: str) -> None:
    icon_ids = entries(country, kind)
    size = (96, 96) if kind == "focus" else (60, 68)
    width, height = (154, 134) if kind == "focus" else (126, 112)
    columns, per_page = 8, 48
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    missing = []
    for page_index, start in enumerate(range(0, len(icon_ids), per_page), 1):
        subset = icon_ids[start:start + per_page]
        rows = (len(subset) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * width, rows * height), "#191d20")
        draw = ImageDraw.Draw(sheet)
        for index, icon_id in enumerate(subset):
            path = source(country, kind, icon_id)
            x = (index % columns) * width + (width - size[0]) // 2
            y = (index // columns) * height + 4
            if path.is_file():
                with Image.open(path) as image:
                    art = image.convert("RGBA")
                art.thumbnail((size[0] - 2, size[1] - 2), Image.Resampling.LANCZOS)
                position = (x + (size[0] - art.width) // 2,
                            y + (size[1] - art.height) // 2)
                sheet.paste(art, position, art)
            else:
                missing.append(icon_id)
                draw.rectangle((x, y, x + size[0], y + size[1]), outline="#6b3434")
            label = icon_id.removeprefix("INT_GER_").removeprefix("SO2_INT_")
            label = label.removeprefix("INT_SOV_").removeprefix("INT_WHR_")
            label = label.removeprefix("WHR_INT_")
            lines = textwrap.wrap(label, width=17 if kind == "idea" else 21,
                                  break_long_words=True, break_on_hyphens=False)
            draw.text((index % columns * width + 4, y + size[1] + 6),
                      "\n".join(lines[:2]), font=font, fill="#ddd9ca")
        out = PREVIEWS / f"{country.lower()}_{kind}_{page_index}.png"
        sheet.save(out, optimize=True)
        print(out.relative_to(ROOT))
    print(f"{country} {kind}: {len(icon_ids) - len(missing)}/{len(icon_ids)} sources present")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--country", choices=("GER", "SOV", "WHR"), required=True)
    parser.add_argument("--kind", choices=("focus", "idea"), required=True)
    args = parser.parse_args()
    preview(args.country, args.kind)


if __name__ == "__main__":
    main()
