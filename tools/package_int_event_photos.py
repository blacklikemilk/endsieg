"""Assign distinct archival photographs to the interwar GER/SOV/WHR events."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html import unescape
from io import BytesIO
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

from audit_int_event_pictures import ROOT, EVENT_DIR, EVENT_START, FIELD, events
from build_interwar_german_news_images import read_source


PICTURES = ROOT / "gfx/event_pictures"
MANIFEST = ROOT / "tools/int_event_photo_sources.tsv"
ORIGINALS = PICTURES / "interwar_event_sources"
GFX = ROOT / "interface/endsieg_int_event_photos.gfx"
SOURCES_DOC = PICTURES / "INT_EVENT_PHOTO_SOURCES.md"
SIZES = {"country_event": (210, 176), "news_event": (397, 153)}


def rows() -> dict[str, dict[str, str]]:
    records = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 4)
        if len(parts) != 5:
            raise ValueError(f"Expected ID|source|subject|x|y: {line}")
        identifier, source, subject, x, y = parts
        if identifier in records or not source.startswith(("local:", "commons:")):
            raise ValueError(f"Duplicate ID or invalid source: {line}")
        records[identifier] = {"source": source, "subject": subject,
                               "x": float(x or "0.5"), "y": float(y or "0.5")}
    valid = {event["id"] for event in events()}
    unknown = set(records) - valid
    if unknown:
        raise ValueError(f"Unknown visible event IDs: {sorted(unknown)}")
    return records


def asset_id(identifier: str) -> str:
    return "INT_photo_" + identifier.replace(".", "_")


def image_path(identifier: str) -> Path:
    return PICTURES / f"{asset_id(identifier)}.dds"


def fetch_commons(identifier: str, title: str) -> tuple[Path, str, str]:
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    cache = ORIGINALS / f"{asset_id(identifier)}.source"
    metadata_cache = ORIGINALS / f"{asset_id(identifier)}.json"
    page_url = "https://commons.wikimedia.org/wiki/File:" + quote(title.replace(" ", "_"))
    cached_info = json.loads(metadata_cache.read_text(encoding="utf-8")) if metadata_cache.is_file() else {}
    cached_title = unquote(urlsplit(cached_info.get("descriptionurl", "")).path).split("/wiki/File:")[-1]
    cache_matches = cached_title.replace("_", " ").casefold() == title.replace("_", " ").casefold()
    if cache.is_file() and cache_matches:
        info = cached_info
    else:
        params = urlencode({"action": "query", "titles": f"File:{title}", "prop": "imageinfo",
                            "iiprop": "url|mime|extmetadata", "iiurlwidth": 1280, "format": "json"})
        request = Request(f"https://commons.wikimedia.org/w/api.php?{params}",
                          headers={"User-Agent": "EndsiegModAssetResearch/1.0 (historical game assets)"})
        for attempt in range(5):
            try:
                with urlopen(request, timeout=30) as response:
                    pages = json.load(response)["query"]["pages"]
                break
            except HTTPError as error:
                if error.code != 429 or attempt == 4:
                    raise
                time.sleep(5 * (attempt + 1))
        info = next(iter(pages.values())).get("imageinfo", [{}])[0]
        if not cache_matches:
            cache.unlink(missing_ok=True)
    if not info.get("mime", "").startswith("image/"):
        raise ValueError(f"Commons source is not an image: {title}")
    metadata = info.get("extmetadata", {})
    license_name = unescape(re.sub(r"<[^>]+>", "", metadata.get("LicenseShortName", {}).get("value", "")))
    if not any(word in license_name.lower() for word in ("public domain", "pd", "cc by", "no restrictions")):
        raise ValueError(f"Review Commons license for {title}: {license_name}")
    if not cache.is_file():
        raw = None
        for attempt in range(4):
            for url in (info.get("thumburl"), info.get("url")):
                if not url:
                    continue
                try:
                    with urlopen(Request(url, headers={"User-Agent": "EndsiegModAssetResearch/1.0 (historical game assets)"}), timeout=45) as response:
                        raw = response.read()
                    break
                except HTTPError as error:
                    if error.code != 429:
                        raise
            if raw is not None:
                break
            time.sleep(5 * (attempt + 1))
        if raw is None:
            raise RuntimeError(f"Commons rate limited both original and thumbnail for {title}")
        with Image.open(BytesIO(raw)) as image:
            image.verify()
        cache.write_bytes(raw)
        time.sleep(2)
    metadata_cache.write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    artist = unescape(re.sub(r"<[^>]+>", "", metadata.get("Artist", {}).get("value", ""))).strip()
    license_url = metadata.get("LicenseUrl", {}).get("value", "")
    credit = f"{artist or 'Unknown photographer'}; "
    credit += f"[{license_name}]({license_url})" if license_url.startswith("https://") else license_name
    return cache, page_url, credit


def rewrite(path: Path, pictures: dict[str, str]) -> None:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    script = raw.decode("utf-8-sig")
    starts = list(EVENT_START.finditer(script))
    chunks = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(script)
        block = script[start.start():end]
        identifier = FIELD("id").search(block)
        if identifier and identifier.group(1) in pictures:
            picture = pictures[identifier.group(1)]
            block, count = re.subn(r"(?m)^(\s*picture\s*=\s*)\S+", rf"\g<1>{picture}", block, count=1)
            if count != 1:
                raise ValueError(f"Missing picture field: {identifier.group(1)} in {path}")
        chunks.append(block)
    updated = script[:starts[0].start()] + "".join(chunks) if starts else script
    path.write_bytes(bom + updated.encode("utf-8"))


def package() -> None:
    manifest = rows()
    records = {event["id"]: event for event in events()}
    gfx = ["spriteTypes = {\n"]
    doc = ["# Interwar event photograph sources", "",
           "The events are alternate history. Historical photographs illustrate their subjects; they do not document fictional outcomes.",
           "Locally sourced Endsieg photographs are adapted from existing event art. Wikimedia sources are linked with their declared reuse terms.",
           "", "| Event | Actual subject | Source | License / status |", "|---|---|---|---|"]
    by_file: dict[str, dict[str, str]] = {}
    for identifier, data in manifest.items():
        source = data["source"]
        if source.startswith("local:"):
            filename = source.removeprefix("local:")
            source_path = PICTURES / filename
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
            link = f"[{filename}]({filename})"
            license_name = "Existing Endsieg asset"
        else:
            source_path, link, license_name = fetch_commons(identifier, source.removeprefix("commons:"))
            link = f"[Commons file]({link})"
        image = read_source(source_path).convert("RGB")
        size = SIZES[records[identifier]["kind"]]
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS,
                             centering=(data["x"], data["y"]))
        image.convert("RGBA").save(image_path(identifier), format="DDS")
        sprite = f"GFX_{asset_id(identifier)}"
        gfx.extend(["\tspriteType = {\n", f'\t\tname = "{sprite}"\n',
                    f'\t\ttexturefile = "gfx/event_pictures/{asset_id(identifier)}.dds"\n', "\t}\n"])
        by_file.setdefault(records[identifier]["file"], {})[identifier] = sprite
        doc.append(f"| `{identifier}` | {data['subject']} | {link} | {license_name} |")
        print(f"Packaged {identifier}", flush=True)
    gfx.append("}\n")
    GFX.write_text("".join(gfx), encoding="utf-8")
    SOURCES_DOC.write_text("\n".join(doc) + "\n", encoding="utf-8")
    for filename, pictures in by_file.items():
        rewrite(EVENT_DIR / filename, pictures)
    print(f"Packaged {len(manifest)} event-specific photographs")


def check(vanilla_root: Path | None = None) -> None:
    from preview_int_event_pictures import sprites

    manifest = rows()
    visible = events()
    pictures = [row["picture"] for row in visible]
    counts = Counter(pictures)
    duplicates = {name: count for name, count in counts.items() if count > 1}
    if duplicates:
        raise ValueError(f"Visible interwar events still reuse pictures: {duplicates}")
    gfx = GFX.read_text(encoding="utf-8")
    manifest_sources = [row["source"] for row in manifest.values()]
    if len(manifest_sources) != len(set(manifest_sources)):
        raise ValueError("Multiple events use the same source photograph")
    hashes = []
    for identifier in manifest:
        path = image_path(identifier)
        if not path.is_file() or f'name = "GFX_{asset_id(identifier)}"' not in gfx:
            raise FileNotFoundError(f"Missing event image/sprite: {identifier}")
        hashes.append(sha256(path.read_bytes()).digest())
    if len(hashes) != len(set(hashes)):
        raise ValueError("Duplicate packaged event images")
    sprite_paths = sprites(vanilla_root)
    all_hashes = []
    unresolved = []
    for record in visible:
        path = sprite_paths.get(record["picture"])
        if path is None or not path.is_file():
            unresolved.append(f"{record['id']} / {record['picture']}")
            continue
        all_hashes.append(sha256(path.read_bytes()).digest())
    if unresolved and vanilla_root is not None:
        raise FileNotFoundError(f"Missing visible event pictures: {unresolved}")
    if len(all_hashes) != len(set(all_hashes)):
        raise ValueError("Visible events reuse an identical image file")
    print(f"Verified {len(visible)} visible interwar events have unique picture keys; "
          f"{len(all_hashes)} picture files checked, {len(unresolved)} need vanilla assets; "
          f"{len(manifest)} packaged sources and images are distinct")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--vanilla-root", type=Path, help="current Hearts of Iron IV installation for vanilla sprites")
    args = parser.parse_args()
    if args.package:
        package()
    if args.check:
        check(args.vanilla_root)
