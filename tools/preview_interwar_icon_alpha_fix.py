"""Show cleaned game DDS contours against dark and bright UI colors."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import package_interwar_german_focus_icons as ger
import package_int_sov_focus_icons as sov
import package_int_whr_icons as whr
import package_interwar_idea_icons as idea


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "gfx/interface/interwar_redesign_previews/clean_border_preview.png"
SAMPLES = (
    ("GER clandestine staff training", ger.goal_path("INT_GER_clandestine_staff_training")),
    ("GER railway workers councils", ger.goal_path("INT_GER_railway_workers_councils")),
    ("GER restore transport links", ger.goal_path("INT_GER_restore_transport_links")),
    ("SOV cooperative credit", sov.goal_path("SO2_INT_cooperative_credit")),
    ("WHR white coalition", whr.goal_path("WHR_INT_white_coalition")),
    ("WHR pacific trade", whr.goal_path("WHR_INT_pacific_trade")),
    ("SOV cooperative industry idea", idea.texture_path("INT_SOV_cooperative_industry")),
    ("WHR Cossack compact idea", idea.texture_path("INT_WHR_cossack_compact")),
)


def main() -> None:
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 15) if font_path.is_file() else ImageFont.load_default()
    sheet = Image.new("RGB", (900, len(SAMPLES) * 190 + 42), "#171c20")
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 10), "CLEANED GAME DDS ICONS — DARK / LIGHT BACKGROUNDS", font=font, fill="#f0ddae")
    for row, (label, path) in enumerate(SAMPLES):
        with Image.open(path) as icon:
            original = icon.convert("RGBA")
        y = row * 190 + 42
        draw.text((12, y + 65), label, font=font, fill="#ebe5d4")
        for x, background in ((315, "#26313a"), (590, "#83b5c2")):
            view = original.copy()
            draw.rectangle((x, y, x + 149, y + 149), fill=background)
            sheet.paste(view, (x + (150 - view.width) // 2,
                              y + (150 - view.height) // 2), view)
        draw.line((12, y + 178, 888, y + 178), fill="#445058")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
