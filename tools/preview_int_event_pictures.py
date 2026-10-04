"""Render contact sheets of interwar event images for visual auditing."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps

from audit_int_event_pictures import ROOT, events
from build_interwar_german_news_images import read_source


OUT = ROOT / "gfx/event_pictures/interwar_event_audit"


def sprites(vanilla_root: Path | None = None) -> dict[str, Path]:
    result = {}
    paths = (list((vanilla_root / "interface").glob("*.gfx")) if vanilla_root else [])
    paths += list((ROOT / "interface").glob("*.gfx"))
    for path in paths:
        script = path.read_text(encoding="utf-8-sig", errors="replace")
        for match in re.finditer(r"spriteType\s*=\s*\{([^{}]*)\}", script, re.S):
            name = re.search(r'\bname\s*=\s*"([^"]+)"', match.group(1))
            texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', match.group(1))
            if name and texture:
                root = ROOT if path.is_relative_to(ROOT) else vanilla_root
                result[name.group(1)] = root / texture.group(1)
    return result


def render(vanilla_root: Path | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sprite_files = sprites(vanilla_root)
    groups = {
        "GER": [row for row in events() if any(word in row["file"] for word in ("German", "Weimar", "Depression"))],
        "SOV": [row for row in events() if "Soviet" in row["file"] or "SOV" in row["file"]],
        "WHR": [row for row in events() if "White Russia" in row["file"] or "WHR" in row["file"]],
    }
    box = (230, 215)
    for nation, records in groups.items():
        for page_number, offset in enumerate(range(0, len(records), 24), 1):
            page = records[offset:offset + 24]
            sheet = Image.new("RGB", (box[0] * 4, box[1] * 6), "#1a1a1a")
            draw = ImageDraw.Draw(sheet)
            font = ImageFont.load_default()
            for index, record in enumerate(page):
                x, y = (index % 4) * box[0], (index // 4) * box[1]
                picture = sprite_files.get(record["picture"])
                if picture and picture.is_file():
                    try:
                        image = read_source(picture).convert("RGB")
                        image = ImageOps.contain(image, (210, 170), Image.Resampling.LANCZOS)
                        sheet.paste(image, (x + (box[0] - image.width) // 2, y))
                    except Exception as error:
                        draw.text((x + 4, y + 4), str(error)[:32], fill="red", font=font)
                else:
                    draw.text((x + 4, y + 4), "MISSING SPRITE", fill="red", font=font)
                draw.text((x + 4, y + 174), record["id"][:32], fill="white", font=font)
                draw.text((x + 4, y + 188), record["label"][:36], fill="#c9c9c9", font=font)
            path = OUT / f"{nation}_{page_number}.png"
            sheet.save(path, optimize=True)
            print(path)


def render_candidates() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    terms = re.compile(
        r"(german|reich|berlin|ruhr|schacht|hindenburg|hitler|rathenau|kapp|"
        r"prussia|factor|industr|treaty|naval|election|parliament|politic|speech|"
        r"workers|strike|soviet|lenin|stalin|trotsky|kolchak|denikin|kornilov|"
        r"white|cossack|siberia|petrograd|russia|finland|hungary|poland|ukraine|"
        r"baltic|caucasus|persia|royal|romanov|army|rail|grain|land|gold|japan|"
        r"council|civil|soldier|bank|court|crowd|mob|factory|revolt|parade|"
        r"alliance|diploma|delegat|minister|officer|soldier|revolution|terror)",
        re.I,
    )
    pictures = [path for path in sorted((ROOT / "gfx/event_pictures").glob("report_event_*.dds"))
                if terms.search(path.name)]
    box = (205, 175)
    for page_number, offset in enumerate(range(0, len(pictures), 40), 1):
        page = pictures[offset:offset + 40]
        sheet = Image.new("RGB", (box[0] * 5, box[1] * 8), "#1a1a1a")
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default()
        for index, path in enumerate(page):
            x, y = (index % 5) * box[0], (index // 5) * box[1]
            try:
                image = ImageOps.contain(read_source(path).convert("RGB"), (190, 145), Image.Resampling.LANCZOS)
                sheet.paste(image, (x + (box[0] - image.width) // 2, y))
            except Exception as error:
                draw.text((x + 4, y + 4), str(error)[:30], fill="red", font=font)
            draw.text((x + 4, y + 149), path.stem.replace("report_event_", "")[:32], fill="white", font=font)
        target = OUT / f"candidates_{page_number}.png"
        sheet.save(target, optimize=True)
        print(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", action="store_true")
    parser.add_argument("--vanilla-root", type=Path)
    args = parser.parse_args()
    render_candidates() if args.candidates else render(args.vanilla_root)
