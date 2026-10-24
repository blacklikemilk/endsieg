"""Render contact sheets containing only the newly redesigned interwar icons."""

from __future__ import annotations

import json
from pathlib import Path
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

import package_interwar_german_focus_icons as ger
import package_int_sov_focus_icons as sov
import package_int_whr_icons as whr
import package_interwar_idea_icons as ideas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "gfx/interface/interwar_redesign_previews"
ASSIGNMENTS = ROOT / "tools/interwar_icon_assignments.json"
STATUS = ROOT / "tools/INTERWAR_ICON_REDESIGN_STATUS.md"
FOCUS_DIRS = {
    "ger": ROOT / "gfx/interface/interwar_german/focus_source",
    "sov": ROOT / "gfx/interface/interwar_soviet/focus_source",
    "whr": ROOT / "gfx/interface/interwar_whr/focus_source",
}
IDEAS = ROOT / "gfx/interface/interwar_ideas/source"
GERMAN_PREVIEW_IDS = (
    "INT_GER_roaring_twenties", "INT_GER_political_turmoil",
    "INT_GER_food_relief", "INT_GER_reichswehr_compromise",
    "INT_GER_rebuild_economy", "INT_GER_reconstitute_civil_service",
    "INT_GER_reconstruction_commission", "INT_GER_restore_transport_links",
    "INT_GER_municipal_reconstruction", "INT_GER_reparations_crisis",
    "INT_GER_end_ruhr_resistance", "INT_GER_retain_the_republic",
    "INT_GER_hold_national_assembly_1919",
)


def source_ids() -> dict[tuple[str, str], list[str]]:
    assignments = json.loads(ASSIGNMENTS.read_text(encoding="utf-8"))
    status = STATUS.read_text(encoding="utf-8")
    ger_b_section = status.split("these 18 `ger_focus_b` entries:", 1)[1].split(
        "The 15 new White Russian focus IDs", 1
    )[0]
    whr_section = status.split("The 15 new White Russian focus IDs are:", 1)[1].split(
        "Every PNG currently", 1
    )[0]
    ger_b = re.findall(r"`(INT_GER_[A-Za-z0-9_]+)`", ger_b_section)
    whr = re.findall(r"`(WHR_INT_[A-Za-z0-9_]+)`", whr_section)
    if len(ger_b) != 18 or len(whr) != 15:
        raise ValueError("Checkpoint lists changed; update this preview's inventory")
    ger_a = [entry["id"] for entry in assignments["ger_focus_a"][:22]]
    ger = list(dict.fromkeys((*GERMAN_PREVIEW_IDS, *ger_a, *ger_b)))
    sov = sorted(path.stem for path in FOCUS_DIRS["sov"].glob("*.png"))
    all_ideas = sorted(path.stem for path in IDEAS.glob("*.png"))
    result = {
        ("ger", "focus"): ger,
        ("sov", "focus"): sov,
        ("whr", "focus"): whr,
        ("ger", "idea"): [name for name in all_ideas if name.startswith("INT_GER_")],
        ("sov", "idea"): [name for name in all_ideas if not name.startswith(("INT_GER_", "INT_WHR_"))],
        ("whr", "idea"): [name for name in all_ideas if name.startswith("INT_WHR_")],
    }
    expected = {("ger", "focus"): 53, ("sov", "focus"): 23,
                ("whr", "focus"): 15, ("ger", "idea"): 14,
                ("sov", "idea"): 13, ("whr", "idea"): 13}
    for key, count in expected.items():
        if len(result[key]) != count:
            raise ValueError(f"Expected {count} redesigned {key} icons, found {len(result[key])}")
    return result


def font(size: int) -> ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def sheet(country: str, kind: str, ids: list[str], page: int, pages: int) -> Path:
    columns = 8
    size = (96, 96) if kind == "focus" else (60, 68)
    cell = (150, 140) if kind == "focus" else (126, 116)
    rows = (len(ids) + columns - 1) // columns
    title_height = 45
    image = Image.new("RGB", (columns * cell[0], rows * cell[1] + title_height), "#171c20")
    draw = ImageDraw.Draw(image)
    heading = f"{country.upper()} INTERWAR — REDESIGNED {kind.upper()} ICONS"
    if pages > 1:
        heading += f"  ({page}/{pages})"
    draw.text((16, 12), heading, fill="#e7d8b2", font=font(17))
    draw.line((16, 36, image.width - 16, 36), fill="#48525b")
    label_font = font(11)
    for index, icon_id in enumerate(ids):
        x = (index % columns) * cell[0]
        y = (index // columns) * cell[1] + title_height
        package = {"ger": ger, "sov": sov, "whr": whr}[country]
        path = package.goal_path(icon_id) if kind == "focus" else ideas.texture_path(icon_id)
        if not path.is_file():
            raise FileNotFoundError(path)
        with Image.open(path) as original:
            art = original.convert("RGBA")
        if art.size != size:
            raise ValueError(f"Wrong packaged icon size: {path}: {art.size}")
        image.paste(art, (x + (cell[0] - art.width) // 2,
                          y + (size[1] - art.height) // 2 + 3), art)
        short = icon_id.removeprefix("INT_GER_").removeprefix("INT_SOV_")
        short = short.removeprefix("INT_WHR_").removeprefix("SO2_INT_")
        short = short.removeprefix("WHR_INT_").replace("_", " ")
        lines = textwrap.wrap(short, width=18 if kind == "focus" else 16)
        draw.multiline_text((x + 5, y + size[1] + 8), "\n".join(lines[:2]),
                            font=label_font, fill="#e1ddd1", spacing=2)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / f"redesigned_{country}_{kind}_{page}.png"
    image.save(path, optimize=True)
    return path


def main() -> None:
    for (country, kind), ids in source_ids().items():
        per_page = 32 if kind == "focus" else 40
        pages = (len(ids) + per_page - 1) // per_page
        for page in range(pages):
            chunk = ids[page * per_page:(page + 1) * per_page]
            print(sheet(country, kind, chunk, page + 1, pages).relative_to(ROOT))


if __name__ == "__main__":
    main()
