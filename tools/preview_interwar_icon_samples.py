"""Show representative completed interwar focus and idea icons at game size."""

import argparse
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

import package_interwar_german_focus_icons as ger
import package_int_sov_focus_icons as sov
import package_int_whr_icons as whr
import package_interwar_idea_icons as ideas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "gfx/interface/interwar_redesign_previews/completed_samples.png"
SAMPLES = {
    "GERMANY": {
        "focus": (
            "INT_GER_roaring_twenties", "INT_GER_establish_the_reichstag",
            "INT_GER_chemical_industry", "INT_GER_social_partnership",
        ),
        "idea": (
            "INT_GER_dawes_credit", "INT_GER_currency_stabilized",
            "INT_GER_unemployment_insurance_idea", "INT_GER_presidential_cabinet",
        ),
    },
    "SOVIET UNION": {
        "focus": (
            "SO2_INT_republics_council", "SO2_INT_union_constitution",
            "SO2_INT_red_army_academies", "SO2_INT_tractor_works",
        ),
        "idea": (
            "INT_SOV_nep_compromise", "INT_SOV_first_plan",
            "INT_SOV_public_health", "INT_SOV_collective_farms",
        ),
    },
    "WHITE RUSSIA": {
        "focus": (
            "WHR_INT_reconstruction_cabinet", "WHR_INT_constituent_elections",
            "WHR_INT_officer_government", "WHR_INT_village_land_titles",
        ),
        "idea": (
            "INT_WHR_white_coalition", "INT_WHR_constitutional_republic",
            "INT_WHR_land_titles", "INT_WHR_pacific_trade",
        ),
    },
}


def source(country: str, kind: str, icon_id: str) -> Path:
    if kind == "idea":
        return ideas.texture_path(icon_id)
    package = {"GERMANY": ger, "SOVIET UNION": sov, "WHITE RUSSIA": whr}[country]
    return package.goal_path(icon_id)


def font(size: int) -> ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def main(*, contrast: bool = False) -> None:
    sheet = Image.new("RGB", (1200, 650), "#171c20")
    draw = ImageDraw.Draw(sheet)
    heading, label = font(17), font(12)
    draw.text((20, 12), "INTERWAR ICON REDESIGN — COMPLETED SAMPLES", font=heading,
              fill="#ebe5d4")
    subtitle = ("Actual DDS textures — checkerboard reveals exterior transparency" if contrast else
                "Focus icons: 96 × 96    •    Idea icons: 60 × 68")
    draw.text((20, 37), subtitle,
              font=label, fill="#aab4b8")
    for row, (country, groups) in enumerate(SAMPLES.items()):
        top = 68 + row * 190
        draw.text((20, top), country, font=heading, fill="#e5c887")
        draw.text((166, top), "FOCUSES", font=label, fill="#aab4b8")
        draw.text((688, top), "IDEAS", font=label, fill="#aab4b8")
        draw.line((20, top + 24, 1180, top + 24), fill="#48525b", width=1)
        for kind, start in (("focus", 156), ("idea", 682)):
            size = (96, 96) if kind == "focus" else (60, 68)
            for index, icon_id in enumerate(groups[kind]):
                path = source(country, kind, icon_id)
                if not path.is_file():
                    raise FileNotFoundError(path)
                x = start + index * 128
                y = top + 32
                with Image.open(path) as image:
                    art = image.convert("RGBA")
                if art.size != size:
                    raise ValueError(f"Wrong packaged icon size: {path}: {art.size}")
                if contrast:
                    for cy in range(0, size[1], 8):
                        for cx in range(0, size[0], 8):
                            color = "#c2cbd0" if (cx // 8 + cy // 8) % 2 else "#edf2f4"
                            draw.rectangle((x + cx, y + cy,
                                            x + min(cx + 7, size[0] - 1),
                                            y + min(cy + 7, size[1] - 1)), fill=color)
                sheet.paste(art, (x + (size[0] - art.width) // 2,
                                  y + (size[1] - art.height) // 2), art)
                short = icon_id.replace("INT_GER_", "").replace("INT_SOV_", "")
                short = short.replace("INT_WHR_", "").replace("SO2_INT_", "")
                short = short.replace("WHR_INT_", "")
                lines = textwrap.wrap(short.replace("_", " "), width=17)
                draw.multiline_text((x, y + 103), "\n".join(lines[:2]), font=label,
                                    fill="#e1ddd1", spacing=2)
    output = OUT.with_name("completed_samples_opaque_check.png") if contrast else OUT
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contrast", action="store_true", help="show alpha over a bright checkerboard")
    args = parser.parse_args()
    main(contrast=args.contrast)
