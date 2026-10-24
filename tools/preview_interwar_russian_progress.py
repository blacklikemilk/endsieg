"""Render Russian interwar icon batches from packaged game DDS files."""

import argparse
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "gfx/interface/interwar_redesign_previews/russian_icons_2026_10_01.png"
GROUPS = (
    ("SOVIET FOCUSES", "focus", (
        "SO2_INT_first_five_year_plan", "SO2_INT_peasant_incentives",
        "SO2_INT_gradual_industrialization", "SO2_INT_international_bureau",
        "SO2_INT_industrial_democracy", "SO2_INT_collectivize_agriculture",
    )),
    ("WHITE RUSSIAN FOCUSES", "focus", (
        "WHR_INT_university_reopening", "WHR_INT_debt_commission",
        "WHR_INT_renegotiate_loans", "WHR_INT_officer_academies",
        "WHR_INT_emigre_networks",
    )),
    ("SOVIET IDEAS", "idea", (
        "INT_SOV_grain_requisition", "INT_SOV_collective_mechanization",
        "INT_SOV_plan_quotas", "INT_SOV_rural_clinic_network",
        "INT_SOV_local_soviets",
    )),
    ("WHITE RUSSIAN IDEAS", "idea", (
        "INT_WHR_austerity", "INT_WHR_officer_academies",
        "INT_WHR_mobile_reserve", "INT_WHR_recovered_economy",
        "INT_WHR_trade_missions",
    )),
)

EXTRA = (
    ("SOVIET FOCUSES", "focus", (
        "SO2_INT_build_magnitogorsk", "SO2_INT_cooperative_farms",
        "SO2_INT_left_industrial_plan", "SO2_INT_stabilize_collective_farms",
        "SO2_INT_second_five_year_plan", "SO2_INT_cooperative_industrialization",
        "SO2_INT_workers_republic", "SO2_INT_heavy_industry_1935",
        "SO2_INT_nep_recovery_1935",
    )),
    ("WHITE RUSSIAN FOCUSES", "focus", (
        "WHR_INT_pacific_trade", "WHR_INT_border_commissions",
        "WHR_INT_nonaggression_treaties", "WHR_INT_foreign_recognition",
        "WHR_INT_siberian_command", "WHR_INT_motor_transport",
        "WHR_INT_artillery_school", "WHR_INT_mobile_reserve",
        "WHR_INT_aircraft_bureaus",
    )),
    ("SOVIET IDEAS", "idea", (
        "INT_SOV_factory_councils", "INT_SOV_officer_schools",
        "INT_SOV_plan_quality", "INT_SOV_union_commissars",
        "INT_SOV_grain_compromise",
    )),
    ("WHITE RUSSIAN IDEAS", "idea", (
        "INT_WHR_private_credit", "INT_WHR_state_lending",
        "INT_WHR_public_works", "INT_WHR_industrial_consortia",
        "INT_WHR_loan_settlement",
    )),
)


def main(*, extra: bool = False) -> None:
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 13) if font_path.is_file() else ImageFont.load_default()
    title_font = ImageFont.truetype(str(font_path), 20) if font_path.is_file() else font
    groups = EXTRA if extra else GROUPS
    rows = [(heading + (" (CONT.)" if i else ""), kind, ids[i:i + 6])
            for heading, kind, ids in groups for i in range(0, len(ids), 6)]
    sheet = Image.new("RGB", (1120, 82 + len(rows) * 164), "#171c20")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 18), "RUSSIAN INTERWAR REDESIGN — GAME-SIZE PREVIEW", font=title_font, fill="#e9e0ce")
    draw.text((24, 48), "Packaged focus DDS: 96×96  •  idea DDS: 60×68", font=font, fill="#aeb8bc")
    for row, (heading, kind, ids) in enumerate(rows):
        top = 82 + row * 164
        draw.text((24, top), heading, font=title_font, fill="#dfc486")
        draw.line((24, top + 27, 1095, top + 27), fill="#48525b")
        for col, icon_id in enumerate(ids):
            x, y = 38 + col * 177, top + 36
            token = icon_id.removeprefix("SO2_INT_").removeprefix("WHR_INT_")
            token = token.removeprefix("INT_SOV_").removeprefix("INT_WHR_")
            path = ROOT / "gfx/interface" / ("goals" if kind == "focus" else "ideas")
            path /= f"{'focus' if kind == 'focus' else 'idea'}_{icon_id}.dds"
            with Image.open(path) as image:
                art = image.convert("RGBA")
            expected = (96, 96) if kind == "focus" else (60, 68)
            if art.size != expected:
                raise ValueError(f"Unexpected game texture size: {path}: {art.size}")
            sheet.paste(art, (x + (96 - art.width) // 2, y), art)
            draw.multiline_text((x, y + 103), "\n".join(textwrap.wrap(token.replace("_", " "), 20)[:2]),
                                font=font, fill="#e3ded2", spacing=2)
    output = OUT.with_name("russian_icons_extra_2026_10_01.png") if extra else OUT
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra", action="store_true", help="render the second October 1 batch")
    main(extra=parser.parse_args().extra)
