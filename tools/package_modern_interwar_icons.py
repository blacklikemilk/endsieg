"""Import individually generated interwar art without altering gameplay.

The manifest keeps the existing source/texture paths. Import is deliberately
separate from image generation: preserve RGBA artwork, fit a PNG master and
native DDS, and add a sprite/reference only when that icon lacked its own art.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

from PIL import Image, ImageDraw

from package_interwar_german_icons import shine, sprite

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools/interwar_modern_icon_manifest.json"
PROGRESS = ROOT / "tools/interwar_modern_icon_progress.json"
SIZES = {"focus": (96, 96), "idea": (60, 68), "decision": (33, 32), "category": (52, 40)}


def local_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    path.relative_to(ROOT)
    return path


def fitted(image: Image.Image, size: tuple[int, int], margin: int) -> Image.Image:
    bounds = image.getchannel("A").getbbox()
    if not bounds:
        raise ValueError("Empty artwork")
    art = image.crop(bounds)
    art.thumbnail((size[0] - 2 * margin, size[1] - 2 * margin), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size)
    canvas.alpha_composite(art, ((size[0] - art.width) // 2, (size[1] - art.height) // 2))
    return canvas


def snapshot(path: Path, archive: zipfile.ZipFile, known: set[str]) -> None:
    relative = path.relative_to(ROOT).as_posix()
    if path.is_file() and relative not in known:
        archive.write(path, relative)
        known.add(relative)


def write_bytes(path: Path, data: bytes, archive: zipfile.ZipFile, known: set[str]) -> None:
    if path.is_file() and path.read_bytes() == data:
        return
    snapshot(path, archive, known)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def add_sprite(asset: dict, output: dict, archive: zipfile.ZipFile, known: set[str]) -> None:
    kind = output["kind"]
    if asset["kind"] == "theme":
        return  # All theme sprites already exist; only their art changes.
    texture = output["path"]
    token = Path(texture).stem.removeprefix("focus_" if kind == "focus" else "idea_")
    name = ("GFX_goal_" if kind == "focus" else "GFX_idea_") + token
    if kind == "focus":
        files = {"GER": "endsieg_interwar_focus_icons.gfx", "SOV": "endsieg_int_sov_focus_icons.gfx", "WHR": "endsieg_int_whr_focus_icons.gfx"}
        gfx = ROOT / "interface" / files[asset["country"]]
        if name not in re.findall(r'\bname\s*=\s*"([^"]+)"', gfx.read_text(encoding="utf-8-sig")):
            text = gfx.read_bytes().decode("utf-8-sig")
            end = text.rfind("}")
            addition = sprite(name, texture) + shine(name, texture)
            write_bytes(gfx, (text[:end] + addition + text[end:]).encode("utf-8"), archive, known)
        consumer = asset.get("consumer", "common/national_focus/INT - Germany.txt")
        pattern = r"(?m)(^\s*id\s*=\s*" + re.escape(asset["key"]) + r"\s*\r?\n\s*icon\s*=\s*)\S+"
        replacement = name
    else:
        gfx = ROOT / "interface/endsieg_interwar_unique_ideas.gfx"
        text = gfx.read_bytes().decode("utf-8-sig")
        if name not in re.findall(r'\bname\s*=\s*"([^"]+)"', text):
            end = text.rfind("}")
            write_bytes(gfx, (text[:end] + sprite(name, texture) + text[end:]).encode("utf-8"), archive, known)
        consumer = asset["consumer"]
        pattern = r"(\b" + re.escape(asset["key"]) + r"\s*=\s*\{[\s\S]*?\bpicture\s*=\s*)\S+"
        replacement = token
    path = local_path(consumer)
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    updated, count = re.subn(pattern, lambda match: match.group(1) + replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Cannot locate existing icon field for {asset['key']} in {consumer}")
    # Only the value of the matched icon/picture field is replaced.
    write_bytes(path, (b"\xef\xbb\xbf" if bom else b"") + updated.encode("utf-8"), archive, known)


def import_art(incoming: Path, selected: set[str], backup: Path) -> None:
    assets = {entry["key"]: entry for entry in json.loads(MANIFEST.read_text(encoding="utf-8"))["icons"]}
    progress = json.loads(PROGRESS.read_text(encoding="utf-8")) if PROGRESS.exists() else {"completed": []}
    completed = {entry["key"]: entry for entry in progress["completed"]}
    candidates: dict[str, Path] = {}
    for source in sorted(incoming.rglob("*.png")):
        key = source.stem
        if key not in assets or (selected and key not in selected):
            continue
        if key in candidates:
            raise ValueError(f"Duplicate incoming artwork for {key}")
        candidates[key] = source
    backup.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(backup, "a", zipfile.ZIP_DEFLATED) as archive:
        known = set(archive.namelist())
        for key, source in candidates.items():
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if completed.get(key, {}).get("generated_sha256") == digest:
                continue
            asset = assets[key]
            with Image.open(source) as raw:
                if raw.mode != "RGBA" or raw.getchannel("A").getextrema() != (0, 255):
                    raise ValueError(f"Artwork must have a transparent RGBA background: {source}")
                image = raw.copy()
            master = fitted(image, (256, 256), 6)
            target = local_path(asset["source_master"])
            snapshot(target, archive, known)
            target.parent.mkdir(parents=True, exist_ok=True)
            master.save(target, optimize=True)
            for output in asset["outputs"]:
                destination = local_path(output["path"])
                snapshot(destination, archive, known)
                destination.parent.mkdir(parents=True, exist_ok=True)
                native = fitted(master, tuple(output["size"]), 2 if output["kind"] == "focus" else 1)
                native.save(destination, format="DDS")
                add_sprite(asset, output, archive, known)
            completed[key] = {**asset, "generated_source": str(source), "generated_sha256": digest, "tool": "built-in image_gen"}
            print(f"Imported {key}")
    progress.update({"style": "Custom art matching modern vanilla HOI4; integrated painted objects, few frames or people", "method": "built-in image_gen; individually generated assets", "target_masters": len(assets), "completed": list(completed.values()), "remaining": [key for key in assets if key not in completed]})
    PROGRESS.write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")
    print(f"Modern redraw: {len(completed)}/{len(assets)} source masters")


def check() -> None:
    progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
    hashes = set()
    textures = 0
    for asset in progress["completed"]:
        with Image.open(local_path(asset["source_master"])) as source:
            if source.size != (256, 256) or source.mode != "RGBA":
                raise ValueError(f"Invalid source master: {asset['key']}")
        for output in asset["outputs"]:
            path = local_path(output["path"])
            with Image.open(path) as image:
                if image.size != tuple(output["size"]) or image.mode != "RGBA" or image.getchannel("A").getextrema() != (0, 255):
                    raise ValueError(f"Invalid native texture: {path}")
                if any(image.getpixel(point)[3] for point in ((0, 0), (0, image.height - 1), (image.width - 1, 0), (image.width - 1, image.height - 1))):
                    raise ValueError(f"Opaque canvas corner: {path}")
            signature = hashlib.sha256(path.read_bytes()).hexdigest()
            if signature in hashes:
                raise ValueError(f"Duplicate native artwork: {path}")
            hashes.add(signature)
            textures += 1
    print(f"Verified {len(progress['completed'])} modern source masters and {textures} distinct native RGBA DDS textures")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--incoming", type=Path)
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.incoming:
        if not args.backup:
            parser.error("--backup is required for imports")
        import_art(args.incoming, set(args.only), args.backup)
    if args.check:
        check()
