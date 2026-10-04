"""Package twelve White Russian interwar event and news pictures for HOI4."""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/whr_event_photo_sources.tsv"
SOURCE = ROOT / "gfx/event_pictures/interwar_whr/source"
ORIGINAL = ROOT / "gfx/event_pictures/interwar_whr/original"
GFX = ROOT / "interface/endsieg_int_whr_eventpictures.gfx"
EVENTS = ROOT / "events/INT_WHR_Paths.txt"
NEWS = ROOT / "events/INT_WHR_News.txt"
SIZES = {"event": (210, 176), "news": (397, 153)}


def entries() -> list[tuple[str, str, str, str]]:
    rows = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            parts = line.split("|", 3)
            if len(parts) != 4 or parts[1] not in SIZES:
                raise ValueError(f"Invalid photo source row: {line}")
            rows.append(tuple(parts))
    if len(rows) != 12 or len({row[0] for row in rows}) != 12:
        raise ValueError("Expected 12 distinct event photograph sources")
    for kind, count in (("event", 8), ("news", 4)):
        expected = {f"INT_WHR_{kind}_{i}" for i in range(1, count + 1)}
        if {name for name, found_kind, _, _ in rows if found_kind == kind} != expected:
            raise ValueError(f"Missing {kind} picture keys")
    return rows


def source_path(name: str) -> Path:
    return SOURCE / f"{name}.png"


def target_path(name: str) -> Path:
    return ROOT / f"gfx/event_pictures/{name}.dds"


def import_photo(name: str, raw_path: Path) -> None:
    record = next((row for row in entries() if row[0] == name), None)
    if record is None:
        raise ValueError(f"Unknown picture key: {name}")
    size = SIZES[record[1]]
    source_size = (size[0] * 4, size[1] * 4)
    crop_center = {
        "INT_WHR_event_8": (0.5, 0.08),
        "INT_WHR_news_2": (0.5, 0.08),
        "INT_WHR_news_3": (0.5, 0.02),
    }.get(name, (0.5, 0.5))
    with Image.open(raw_path) as image:
        if name == "INT_WHR_event_5":
            image = image.crop((0, int(image.height * 0.10), image.width, image.height))
        framed = ImageOps.fit(image.convert("RGB"), source_size,
                              method=Image.Resampling.LANCZOS, centering=crop_center)
    SOURCE.mkdir(parents=True, exist_ok=True)
    framed.save(source_path(name), optimize=True)


def fetch_archival_photos() -> None:
    """Download the Commons JPEG originals listed in the source manifest."""
    ORIGINAL.mkdir(parents=True, exist_ok=True)
    source_lines = [
        "# White Russian interwar event/news photographs",
        "",
        "These genuine historical photographs illustrate an alternate-history scenario. They do not depict the fictional events themselves.",
        "Downloaded Commons JPEGs are retained under `interwar_whr/original/`; game crops are under `interwar_whr/source/`. Wikimedia may serve a pre-scaled thumbnail when it rate-limits an original download.",
        "All files except `INT_WHR_event_6` are marked public domain on their Commons pages. `INT_WHR_event_6` is credited to [Garitan](https://commons.wikimedia.org/wiki/User:Garitan), licensed [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); the in-game version is cropped and resized, and its derivative remains under that license.",
        "",
        "| Game picture | Actual subject | Commons source | Downloaded JPEG SHA-256 |",
        "|---|---|---|---|",
    ]
    for name, _, title, subject in entries():
        original_path = ORIGINAL / f"{name}.jpg"
        if original_path.is_file():
            raw = original_path.read_bytes()
        else:
            params = urlencode({"action": "query", "titles": f"File:{title}", "prop": "imageinfo",
                                "iiprop": "url|mime|extmetadata", "iiurlwidth": 1280, "format": "json"})
            request = Request(f"https://commons.wikimedia.org/w/api.php?{params}",
                              headers={"User-Agent": "EndsiegModAssetResearch/1.0 (archival game art)"})
            with urlopen(request, timeout=30) as response:
                pages = json.load(response)["query"]["pages"]
            info = next(iter(pages.values())).get("imageinfo", [{}])[0]
            if info.get("mime") != "image/jpeg" or not info.get("url", "").startswith("https://upload.wikimedia.org/"):
                raise ValueError(f"Expected a Commons JPEG original for {name}: {title}")
            license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "").lower()
            permitted_cc = name == "INT_WHR_event_6" and license_name == "cc by-sa 3.0"
            if not permitted_cc and not any(word in license_name for word in ("public domain", "pd")):
                raise ValueError(f"Check license manually for {name}: {title} ({license_name})")
            raw = None
            for image_url in (info["url"], info.get("thumburl")):
                if not image_url:
                    continue
                image_request = Request(image_url, headers={"User-Agent": "EndsiegModAssetResearch/1.0 (archival game art)"})
                try:
                    with urlopen(image_request, timeout=45) as response:
                        raw = response.read()
                    break
                except HTTPError as error:
                    if error.code != 429:
                        raise
            if raw is None:
                raise RuntimeError(f"Wikimedia rate-limited both original and thumbnail for {name}")
            original_path.write_bytes(raw)
        with Image.open(BytesIO(raw)) as image:
            if image.format != "JPEG":
                raise ValueError(f"Downloaded non-JPEG for {name}")
        import_photo(name, original_path)
        page_url = "https://commons.wikimedia.org/wiki/File:" + quote(title.replace(" ", "_"))
        source_lines.append(f"| `{name}` | {subject} | [Commons file]({page_url}) | `{hashlib.sha256(raw).hexdigest()}` |")
        print(f"Verified real photograph {name}", flush=True)
    (ROOT / "gfx/event_pictures/INT_WHR_IMAGE_SOURCES.md").write_text("\n".join(source_lines) + "\n", encoding="utf-8")


def rewrite_pictures(path: Path, kind: str, available: set[int]) -> None:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    script = raw.decode("utf-8-sig")
    found = set()
    namespace = "INT_whr_paths" if kind == "event" else "INT_whr_news"

    def replace(match: re.Match[str]) -> str:
        number = int(match.group(2))
        if number not in available:
            return match.group(0)
        found.add(number)
        return match.group(1) + f"GFX_INT_WHR_{kind}_{number}"

    pattern = (rf"(?m)(^\s*id = {namespace}\.(\d+)\r?\n"
               rf"\s*title = [^\r\n]+\r?\n"
               rf"\s*desc = [^\r\n]+\r?\n"
               rf"\s*picture = )\S+")
    updated = re.sub(pattern, replace, script)
    if found != available:
        raise ValueError(f"Did not find all {kind} event picture fields: {found}")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + updated.encode("utf-8"))


def preview(kind: str, names: list[str]) -> None:
    target_size = SIZES[kind]
    columns = 4 if kind == "event" else 2
    rows = (len(names) + columns - 1) // columns
    cell_width = target_size[0] + 14
    cell_height = target_size[1] + 28
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), "#171c20")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, name in enumerate(names):
        x = (index % columns) * cell_width + 7
        y = (index // columns) * cell_height + 5
        with Image.open(target_path(name)) as image:
            sheet.paste(image.convert("RGB"), (x, y))
        draw.text((x, y + target_size[1] + 3), name, fill="#f1eadc", font=font)
    sheet.save(ROOT / f"gfx/event_pictures/interwar_whr/{kind}_preview.png", optimize=True)


def package(*, complete: bool = True) -> None:
    records = entries()
    missing = [name for name, *_ in records if not source_path(name).is_file()]
    if missing and complete:
        raise FileNotFoundError(f"Missing event pictures: {missing}")
    available = [row for row in records if source_path(row[0]).is_file()]
    gfx = ["spriteTypes = {\n"]
    for name, kind, _, _ in available:
        size = SIZES[kind]
        target = target_path(name)
        with Image.open(source_path(name)) as image:
            image.convert("RGBA").resize(size, Image.Resampling.LANCZOS).save(target)
        gfx.append("\tspriteType = {\n")
        gfx.append(f'\t\tname = "GFX_{name}"\n')
        gfx.append(f'\t\ttexturefile = "gfx/event_pictures/{name}.dds"\n')
        gfx.append("\t}\n")
    gfx.append("}\n")
    GFX.write_text("".join(gfx), encoding="utf-8")
    rewrite_pictures(EVENTS, "event", {int(name.rsplit("_", 1)[1]) for name, kind, _, _ in available if kind == "event"})
    rewrite_pictures(NEWS, "news", {int(name.rsplit("_", 1)[1]) for name, kind, _, _ in available if kind == "news"})
    for kind in SIZES:
        names = [name for name, found_kind, _, _ in available if found_kind == kind]
        if names:
            preview(kind, names)
    print(f"Packaged {len(available)} White Russian event/news pictures; {len(missing)} awaiting artwork")


def check(*, complete: bool = True) -> None:
    records = entries()
    missing = [name for name, *_ in records if not source_path(name).is_file()]
    if missing and complete:
        raise FileNotFoundError(f"Missing event pictures: {missing}")
    records = [row for row in records if source_path(row[0]).is_file()]
    gfx = GFX.read_text(encoding="utf-8")
    provenance = (ROOT / "gfx/event_pictures/INT_WHR_IMAGE_SOURCES.md").read_text(encoding="utf-8")
    event_script = EVENTS.read_text(encoding="utf-8-sig")
    news_script = NEWS.read_text(encoding="utf-8-sig")
    digests = []
    for name, kind, _, _ in records:
        original_path = ORIGINAL / f"{name}.jpg"
        if not original_path.is_file():
            raise FileNotFoundError(f"Missing archived photograph: {name}")
        original_hash = hashlib.sha256(original_path.read_bytes()).hexdigest()
        if f"`{name}`" not in provenance or f"`{original_hash}`" not in provenance:
            raise ValueError(f"Photograph provenance does not match: {name}")
        with Image.open(original_path) as image:
            if image.format != "JPEG":
                raise ValueError(f"Archived photograph is not JPEG: {name}")
        with Image.open(source_path(name)) as image:
            if image.size != tuple(dim * 4 for dim in SIZES[kind]):
                raise ValueError(f"Wrong picture source size: {name}")
        with Image.open(target_path(name)) as image:
            if image.size != SIZES[kind] or image.mode != "RGBA":
                raise ValueError(f"Wrong DDS size or mode: {name}")
        script = event_script if kind == "event" else news_script
        if f"picture = GFX_{name}" not in script:
            raise ValueError(f"Picture is not used by its event: {name}")
        if f'name = "GFX_{name}"' not in gfx:
            raise ValueError(f"Missing sprite definition: {name}")
        digests.append(hashlib.sha256(target_path(name).read_bytes()).digest())
    if len(digests) != len(set(digests)):
        raise ValueError("Duplicate event picture DDS textures")
    print(f"Verified {len(records)} distinct event/news images, sprites, and references; {len(missing)} awaiting artwork")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-photo", nargs=2, metavar=("PICTURE_KEY", "IMAGE"))
    parser.add_argument("--fetch-archival", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--package-available", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-available", action="store_true")
    args = parser.parse_args()
    if args.import_photo:
        import_photo(args.import_photo[0], Path(args.import_photo[1]))
    if args.fetch_archival:
        fetch_archival_photos()
    if args.package:
        package()
    if args.package_available:
        package(complete=False)
    if args.check:
        check()
    if args.check_available:
        check(complete=False)
