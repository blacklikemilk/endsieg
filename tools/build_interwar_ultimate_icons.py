"""Compose compact HOI4 icons from the reusable Ultimate-HOI4-GFX pieces.

The compositor deliberately works at the game's native icon sizes.  A manifest
names the frame/background and the small transparent component images; this
keeps the art recipe reviewable and avoids baking a large, stale copy of a
vanilla interface into the mod.

Example::

    python tools/build_interwar_ultimate_icons.py \
        --source-dir "C:/.../Ultimate-HOI4-GFX/source" \
        --manifest tools/interwar_ultimate_icons.json \
        --output-root gfx/interface/ultimate \
        --preview-dir .tmp/ultimate-preview

Entries may use the compact ``output``/``size`` form or the richer
``outputs: [{"path": ..., "size": [w, h]}]`` form. ``source_masters`` uses the
same richer form for native PNG masters written alongside derived DDS outputs.
Component paths are relative to the source library unless absolute. PNG, TGA,
DDS, and flattened/merged PSD files are accepted. A ``finished`` (or
``finished_icon``/``native_icon``) path may provide an already-painted native
icon; it is copied/resized directly to every declared output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import textwrap
from typing import Any, Iterable, Sequence

from PIL import Image, ImageChops, ImageDraw


DEFAULT_SIZES = {
    "focus": (96, 96),
    "idea": (60, 68),
    "decision": (33, 32),
    "category": (52, 40),
}

# ``max_size`` is the visible component area, rather than the output canvas.
# Keeping these numbers close to native resolution is intentional: resampling
# a 50px figure several times is much softer than composing it once at 96px.
PRESETS: dict[str, dict[str, tuple[int, int] | tuple[float, float]]] = {
    "focus_center": {"primary_max": (52, 52), "primary_anchor": (0.50, 0.49), "secondary_max": (25, 25), "secondary_anchor": (0.72, 0.70), "badge_max": (19, 19), "badge_anchor": (0.27, 0.25)},
    "focus_diagonal": {"primary_max": (49, 49), "primary_anchor": (0.38, 0.43), "secondary_max": (27, 27), "secondary_anchor": (0.70, 0.69), "badge_max": (17, 17), "badge_anchor": (0.25, 0.27)},
    "focus_tall": {"primary_max": (43, 58), "primary_anchor": (0.50, 0.48), "secondary_max": (23, 23), "secondary_anchor": (0.73, 0.75), "badge_max": (17, 17), "badge_anchor": (0.27, 0.23)},
    "idea_center": {"primary_max": (35, 42), "primary_anchor": (0.50, 0.46), "secondary_max": (17, 20), "secondary_anchor": (0.76, 0.74), "badge_max": (13, 14), "badge_anchor": (0.25, 0.26)},
    "idea_diagonal": {"primary_max": (32, 38), "primary_anchor": (0.40, 0.43), "secondary_max": (18, 20), "secondary_anchor": (0.72, 0.72), "badge_max": (13, 14), "badge_anchor": (0.25, 0.25)},
    "decision_center": {"primary_max": (25, 24), "primary_anchor": (0.50, 0.47), "secondary_max": (11, 12), "secondary_anchor": (0.77, 0.73), "badge_max": (10, 10), "badge_anchor": (0.25, 0.26)},
    "category_center": {"primary_max": (35, 29), "primary_anchor": (0.50, 0.47), "secondary_max": (14, 14), "secondary_anchor": (0.77, 0.73), "badge_max": (12, 12), "badge_anchor": (0.25, 0.24)},
}

LAYOUT_ALIASES = {
    "stack": "{kind}_center",
    "cross": "{kind}_diagonal",
    "flank": "{kind}_tall",
}


class ManifestError(ValueError):
    """An actionable manifest or source error."""


def _u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def _packbits_row(data: bytes, offset: int, width: int) -> tuple[bytes, int]:
    out = bytearray()
    while len(out) < width:
        if offset >= len(data):
            raise ManifestError("truncated PSD PackBits row")
        code = data[offset]
        offset += 1
        if code <= 127:
            count = code + 1
            out.extend(data[offset : offset + count])
            offset += count
        elif code >= 129:
            count = 257 - code
            if offset >= len(data):
                raise ManifestError("truncated PSD PackBits repeat")
            out.extend(data[offset : offset + 1] * count)
            offset += 1
        # 128 is a no-op, as specified by PackBits.
    if len(out) != width:
        raise ManifestError("invalid PSD PackBits row length")
    return bytes(out), offset


def _open_flattened_psd(path: Path) -> Image.Image:
    """Read the flattened 8-bit RGB/RGBA channels in a PSD.

    Ultimate-HOI4-GFX includes flattened PSD templates with alpha in the
    fourth channel.  ``psd_tools`` is intentionally not required for this
    utility; layer metadata is skipped and the image data is decoded directly.
    """

    data = path.read_bytes()
    if len(data) < 26 or data[:4] != b"8BPS":
        raise ManifestError(f"not a PSD file: {path}")
    channels = int.from_bytes(data[12:14], "big")
    height = _u32(data, 14)
    width = _u32(data, 18)
    depth = int.from_bytes(data[22:24], "big")
    color_mode = int.from_bytes(data[24:26], "big")
    if depth != 8 or color_mode != 3 or channels < 3:
        raise ManifestError(f"unsupported PSD format (channels={channels}, depth={depth}, mode={color_mode}): {path}")
    cursor = 26
    for _ in range(3):
        section_length = _u32(data, cursor)
        cursor += 4 + section_length
    if cursor + 2 > len(data):
        raise ManifestError(f"PSD has no image data: {path}")
    compression = int.from_bytes(data[cursor : cursor + 2], "big")
    cursor += 2
    planes: list[bytes] = []
    plane_count = min(channels, 4)
    if compression == 0:
        plane_bytes = width * height
        for _ in range(plane_count):
            end = cursor + plane_bytes
            if end > len(data):
                raise ManifestError(f"truncated PSD channel data: {path}")
            planes.append(data[cursor:end])
            cursor = end
    elif compression == 1:
        row_count = channels * height
        lengths_end = cursor + row_count * 2
        if lengths_end > len(data):
            raise ManifestError(f"truncated PSD row lengths: {path}")
        lengths = [int.from_bytes(data[cursor + i * 2 : cursor + i * 2 + 2], "big") for i in range(row_count)]
        cursor = lengths_end
        for channel in range(plane_count):
            rows = bytearray()
            for row in range(height):
                row_length = lengths[channel * height + row]
                encoded = data[cursor : cursor + row_length]
                if len(encoded) != row_length:
                    raise ManifestError(f"truncated PSD RLE channel data: {path}")
                decoded, _ = _packbits_row(encoded, 0, width)
                rows.extend(decoded)
                cursor += row_length
            planes.append(bytes(rows))
    else:
        raise ManifestError(f"unsupported PSD compression {compression}: {path}")
    if len(planes) == 3:
        planes.append(bytes([255]) * (width * height))
    return Image.merge("RGBA", [Image.frombytes("L", (width, height), plane) for plane in planes[:4]])


def open_rgba(path: Path) -> Image.Image:
    """Open a source image and preserve alpha across common HOI4 formats."""

    try:
        if path.suffix.casefold() == ".psd":
            try:
                return _open_flattened_psd(path)
            except ManifestError:
                # Pillow can decode some merged PSDs that do not match the
                # small flattened RGB/RGBA reader above.
                with Image.open(path) as image:
                    return image.convert("RGBA")
        with Image.open(path) as image:
            return image.convert("RGBA")
    except (OSError, ValueError) as exc:
        raise ManifestError(f"cannot read image {path}: {exc}") from exc


@dataclass(frozen=True)
class SourceResolver:
    root: Path

    def resolve(self, raw: str | Path) -> Path:
        candidate = Path(str(raw))
        if not candidate.is_absolute():
            candidate = (self.root / candidate).resolve()
            try:
                candidate.relative_to(self.root.resolve())
            except ValueError as exc:
                raise ManifestError(f"source path escapes source root: {raw}") from exc
        if candidate.is_file():
            return candidate
        # Recipes are easier to read when they can name ``Tank.png`` without
        # repeating the pack's category directory.  Reject ambiguous matches.
        name = Path(str(raw)).name.casefold()
        matches = [path for path in self.root.rglob("*") if path.is_file() and path.name.casefold() == name]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise ManifestError(f"source asset not found: {raw}")
        raise ManifestError("source asset is ambiguous; use its relative path: " + str(raw) + " -> " + ", ".join(str(p.relative_to(self.root)) for p in matches))


def _as_pair(value: Any, label: str) -> tuple[int, int]:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        try:
            return (int(value[0]), int(value[1]))
        except (TypeError, ValueError):
            pass
    raise ManifestError(f"{label} must be a two-element size")


def _component_values(entry: dict[str, Any], name: str) -> list[Any]:
    """Accept both singular recipe fields and the plural aliases used by drafts."""

    aliases = {
        "frame": ("frame", "frame_source"),
        "primary": ("primary", "primary_component"),
        "secondary": ("secondary", "secondary_component", "optional_secondary"),
        "badge": ("badge", "badge_component"),
        "source_master": ("source_master", "source_master_input"),
    }[name]
    for alias in aliases:
        if alias in entry and entry[alias] is not None:
            value = entry[alias]
            if isinstance(value, list) and name in {"source_master", "primary", "secondary", "badge"}:
                return value
            return [value]
    return []


def _finished_values(entry: dict[str, Any]) -> list[Any]:
    """Return optional finished/native icon inputs, if a recipe supplies one."""

    for alias in ("finished", "finished_icon", "finished_native", "native_icon", "finished_source"):
        if alias not in entry or entry[alias] is None:
            continue
        value = entry[alias]
        return value if isinstance(value, list) else [value]
    return []


def _format_path(raw: str, entry: dict[str, Any]) -> str:
    try:
        return raw.format(key=entry.get("key", ""), kind=entry.get("kind", ""), country=entry.get("country", ""))
    except (KeyError, ValueError) as exc:
        raise ManifestError(f"invalid output path template {raw!r}: {exc}") from exc


def _output_specs(entry: dict[str, Any], output_root: Path) -> list[tuple[Path, tuple[int, int]]]:
    """Return all derived outputs and optional native source-master outputs."""

    kind = str(entry.get("kind", "focus")).casefold()
    default_size = DEFAULT_SIZES.get(kind)
    if default_size is None:
        raise ManifestError(f"unknown icon kind {kind!r}; expected focus, idea, decision or category")
    raw_outputs = entry.get("outputs")
    if raw_outputs is None:
        raw_outputs = entry.get("output", entry.get("output_path"))
    if raw_outputs is None:
        raw_outputs = [f"{kind}_{entry.get('key', 'icon')}.dds"]
    if not isinstance(raw_outputs, list):
        raw_outputs = [raw_outputs]
    specs: list[tuple[Path, tuple[int, int]]] = []
    for raw in raw_outputs:
        if isinstance(raw, dict):
            raw_path = raw.get("path", raw.get("output"))
            raw_size = raw.get("size", default_size)
        else:
            raw_path = raw
            raw_size = entry.get("size", default_size)
        if not raw_path:
            raise ManifestError(f"{entry.get('key')}: output needs path")
        specs.append((_output_path(str(raw_path), entry, output_root), _as_pair(raw_size, "output.size")))
    # Masters are explicit output paths (usually PNG) at a native size.  They
    # may coexist with one or more derived DDS sizes in ``outputs``.
    raw_masters = entry.get("source_masters", [])
    if not isinstance(raw_masters, list):
        raw_masters = [raw_masters]
    for raw in raw_masters:
        if isinstance(raw, dict):
            raw_path = raw.get("path", raw.get("output"))
            raw_size = raw.get("size", default_size)
        else:
            raw_path = raw
            raw_size = default_size
        if not raw_path:
            raise ManifestError(f"{entry.get('key')}: source master needs path")
        specs.append((_output_path(str(raw_path), entry, output_root), _as_pair(raw_size, "source_master.size")))
    return specs


def _output_path(raw: str, entry: dict[str, Any], output_root: Path) -> Path:
    path = Path(_format_path(raw, entry))
    root = output_root.resolve()
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManifestError(f"output path escapes output root: {raw}") from exc
    return resolved


def _preset(entry: dict[str, Any], size: tuple[int, int]) -> dict[str, Any]:
    kind = str(entry.get("kind", "focus")).casefold()
    selected = entry.get("layout", f"{kind}_center")
    if isinstance(selected, dict):
        values = dict(selected)
    else:
        name = LAYOUT_ALIASES.get(str(selected), str(selected)).format(kind=kind)
        if name not in PRESETS:
            raise ManifestError(f"unknown layout preset {name!r}")
        values = dict(PRESETS[name])
    # Scale the native presets when a manifest asks for a deliberate alternate
    # output size, while preserving the intended relative placement.
    native = DEFAULT_SIZES.get(kind, size)
    factor_x, factor_y = size[0] / native[0], size[1] / native[1]
    for name in ("primary_max", "secondary_max", "badge_max"):
        if name in values:
            pair = _as_pair(values[name], name)
            values[name] = (max(1, round(pair[0] * factor_x)), max(1, round(pair[1] * factor_y)))
    return values


def _component_spec(value: Any) -> tuple[str, dict[str, Any]]:
    if isinstance(value, str):
        return value, {}
    if isinstance(value, dict):
        raw = value.get("path", value.get("source"))
        if not raw:
            raise ManifestError("component object needs path/source")
        return str(raw), value
    raise ManifestError("component must be a path or object with path/source")


def _fit(image: Image.Image, max_size: tuple[int, int], scale: float = 1.0) -> Image.Image:
    width, height = image.size
    if not width or not height:
        raise ManifestError("component has an empty image")
    factor = min(max_size[0] / width, max_size[1] / height) * float(scale)
    dimensions = (max(1, round(width * factor)), max(1, round(height * factor)))
    if dimensions == image.size:
        return image
    return image.resize(dimensions, Image.Resampling.LANCZOS)


def _trim_transparent(image: Image.Image) -> Image.Image:
    """Crop only fully transparent margins from an object component."""

    rgba = image.convert("RGBA")
    bounds = rgba.getchannel("A").getbbox()
    return rgba.crop(bounds) if bounds else rgba


def _paste_center(canvas: Image.Image, image: Image.Image, anchor: tuple[float, float], position: Any = None) -> None:
    if position is None:
        x = round(anchor[0] * canvas.width - image.width / 2)
        y = round(anchor[1] * canvas.height - image.height / 2)
    else:
        x, y = _as_pair(position, "position")
    canvas.alpha_composite(image, (x, y))


def _opaque_enclosed_pixels(image: Image.Image) -> Image.Image:
    """Make only enclosed sub-255 alpha pixels opaque.

    Pixels connected to the canvas border through alpha below 255 are the
    antialiased exterior and remain unchanged. This bounded flood-fill avoids
    convex hulls or backing mattes, so separate objects and exterior gaps keep
    their original transparency and RGB values.
    """

    art = image.convert("RGBA").copy()
    alpha = art.getchannel("A")
    width, height = alpha.size
    values = alpha.tobytes()
    exterior = bytearray(width * height)
    pending: list[int] = []
    for x in range(width):
        for y in (0, height - 1):
            index = y * width + x
            if values[index] < 255 and not exterior[index]:
                exterior[index] = 1
                pending.append(index)
    for y in range(height):
        for x in (0, width - 1):
            index = y * width + x
            if values[index] < 255 and not exterior[index]:
                exterior[index] = 1
                pending.append(index)
    cursor = 0
    while cursor < len(pending):
        index = pending[cursor]
        cursor += 1
        x, y = index % width, index // width
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            neighbor = ny * width + nx
            if values[neighbor] < 255 and not exterior[neighbor]:
                exterior[neighbor] = 1
                pending.append(neighbor)
    changed = bytearray(alpha.tobytes())
    for index, value in enumerate(values):
        if value < 255 and not exterior[index]:
            changed[index] = 255
    art.putalpha(Image.frombytes("L", (width, height), bytes(changed)))
    return art


def _render(entry: dict[str, Any], resolver: SourceResolver, size: tuple[int, int]) -> Image.Image:
    finished = _finished_values(entry)
    if finished:
        image = open_rgba(resolver.resolve(_component_spec(finished[0])[0]))
        # A finished native icon is authoritative artwork: preserve its alpha
        # and RGB values while adapting only its declared output dimensions.
        return image if image.size == size else image.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    frame_alpha: Image.Image | None = None
    # Source masters are composited first. This accommodates a supplied
    # painted backing image while leaving the frame as the final edge treatment.
    for raw in _component_values(entry, "source_master"):
        image = open_rgba(resolver.resolve(_component_spec(raw)[0]))
        image = image.resize(size, Image.Resampling.LANCZOS)
        canvas.alpha_composite(image)
    frame_values = _component_values(entry, "frame")
    if frame_values:
        frame = open_rgba(resolver.resolve(_component_spec(frame_values[0])[0]))
        # Focus templates are 100x88 and deliberately wider than the native
        # 96x96 slot. Keep their proportions and leave the two-pixel safety
        # margin used by the game. Native idea templates (60x68) stay native.
        if frame.size == size:
            fitted_frame = frame
        else:
            fitted_frame = _fit(frame, (max(1, size[0] - 4), max(1, size[1] - 4)))
        frame_layer = Image.new("RGBA", size, (0, 0, 0, 0))
        frame_layer.alpha_composite(fitted_frame, ((size[0] - fitted_frame.width) // 2, (size[1] - fitted_frame.height) // 2))
        frame_alpha = frame_layer.getchannel("A")
        canvas.alpha_composite(frame_layer)

    layout = _preset(entry, size)
    for role in ("primary", "secondary", "badge"):
        values = _component_values(entry, role)
        if not values:
            continue
        for value in values:
            raw_path, options = _component_spec(value)
            image = _trim_transparent(open_rgba(resolver.resolve(raw_path)))
            max_size = _as_pair(options.get("max_size", layout.get(f"{role}_max", (size[0], size[1]))), f"{role}.max_size")
            image = _fit(image, max_size, float(options.get("scale", 1.0)))
            if "opacity" in options:
                opacity = max(0, min(255, round(float(options["opacity"]) * 255 if float(options["opacity"]) <= 1 else float(options["opacity"]))))
                image.putalpha(image.getchannel("A").point(lambda value: value * opacity // 255))
            if "rotate" in options:
                image = image.rotate(float(options["rotate"]), resample=Image.Resampling.BICUBIC, expand=True)
            anchor = options.get("anchor", layout.get(f"{role}_anchor", (0.5, 0.5)))
            if not isinstance(anchor, (list, tuple)) or len(anchor) != 2:
                raise ManifestError(f"{role}.anchor must be two normalized coordinates")
            _paste_center(canvas, image, (float(anchor[0]), float(anchor[1])), options.get("position"))

    if frame_alpha is not None and entry.get("clip_to_frame", True):
        # A frame's transparent exterior must remain transparent even when a
        # component intentionally hangs beyond its inner opening.
        # Use a minimum mask (rather than Image.composite, which applies the
        # frame alpha as a second interpolation and squares antialiased edges).
        canvas.putalpha(ImageChops.darker(canvas.getchannel("A"), frame_alpha))
    if entry.get("opaque_interior", False):
        canvas = _opaque_enclosed_pixels(canvas)
    return canvas


def _write(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = image.convert("RGBA")
    if path.suffix.casefold() == ".dds":
        image.save(path, format="DDS")
    else:
        image.save(path, format="PNG", optimize=True)


def _preview_label(entry: dict[str, Any]) -> str:
    """Return a compact human label plus a key suffix for contact sheets."""

    key = str(entry.get("key", "icon"))
    # Pillow's default bitmap font in the supported runtime is Latin-1 only.
    # Keep contact-sheet generation robust for typographic dashes/quotes in
    # human titles while leaving manifest/output data untouched.
    title = str(entry.get("title", entry.get("name", ""))).strip().encode("ascii", "replace").decode("ascii")
    suffix = key[-18:]
    if title and title.casefold() != key.casefold():
        first = textwrap.shorten(title, width=20, placeholder="...")
        return f"{first}\n{suffix}"
    words = key.replace("_", " ")
    lines = textwrap.wrap(words, width=20)[:2]
    return "\n".join(lines) if lines else key


def _preview_sheet(rendered: list[tuple[str, Image.Image]], directory: Path) -> None:
    if not rendered:
        return
    directory.mkdir(parents=True, exist_ok=True)
    # A rerun may contain fewer recipes than an earlier gallery. Remove only
    # this tool's generated contact sheets so stale pages cannot be mistaken
    # for current QA output; unrelated files in the preview directory remain.
    for old in directory.glob("contact_sheet_dark_*.png"):
        old.unlink()
    for old in directory.glob("contact_sheet_light_*.png"):
        old.unlink()
    cell_w, cell_h = 128, 132
    columns = 8
    page_capacity = 72  # 8x9 cells keeps large galleries practical to inspect.
    for page_start in range(0, len(rendered), page_capacity):
        page = rendered[page_start : page_start + page_capacity]
        rows = (len(page) + columns - 1) // columns
        page_number = page_start // page_capacity + 1
        for name, background in (("dark", (31, 35, 41, 255)), ("light", (220, 220, 214, 255))):
            sheet = Image.new("RGBA", (columns * cell_w, rows * cell_h), background)
            draw = ImageDraw.Draw(sheet)
            for index, (label, icon) in enumerate(page):
                x, y = (index % columns) * cell_w, (index // columns) * cell_h
                # Paste at the true native dimensions. The cell is only a
                # visual gutter and must not rescale a 60x68 idea to 96x96.
                sheet.alpha_composite(icon, (x + (cell_w - icon.width) // 2, y + 2))
                draw.multiline_text((x + 3, y + 100), label, spacing=1, fill=(245, 245, 245, 255) if name == "dark" else (20, 20, 20, 255))
            native_path = directory / f"contact_sheet_{name}_{page_number:02d}.png"
            sheet.convert("RGB").save(native_path, optimize=True)
            # Keep the native sheet for pixel-level checks and provide a
            # nearest-neighbour 2x sheet for clearer inspection of tiny
            # 33x32 decision/category art and two-line labels.
            doubled = sheet.resize((sheet.width * 2, sheet.height * 2), Image.Resampling.NEAREST)
            doubled.convert("RGB").save(directory / f"contact_sheet_{name}_2x_{page_number:02d}.png", optimize=True)


def _entries(manifest: Path) -> tuple[list[dict[str, Any]], str | None]:
    try:
        raw = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest {manifest}: {exc}") from exc
    status: str | None = None
    if isinstance(raw, dict):
        raw_status = raw.get("status", raw.get("state"))
        if isinstance(raw_status, str):
            status = raw_status.casefold()
        raw = raw.get("entries", raw.get("icons", raw.get("assets")))
    if not isinstance(raw, list) or not all(isinstance(entry, dict) for entry in raw):
        raise ManifestError("manifest must be a list or an object containing an entries list")
    return raw, status


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path, help="Ultimate-HOI4-GFX source library")
    parser.add_argument("--manifest", required=True, type=Path, help="JSON icon recipe manifest")
    parser.add_argument("--output-root", required=True, type=Path, help="root for relative output paths")
    parser.add_argument("--preview-dir", type=Path, help="write dark/light contact sheets")
    parser.add_argument("--dry-run", action="store_true", help="validate and list recipes without writing images")
    parser.add_argument("--only", metavar="KEY", help="build one manifest key (useful for a quick preview)")
    parser.add_argument("--allow-draft", action="store_true", help="explicitly permit manifests/entries marked draft or rejected")
    args = parser.parse_args(argv)
    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        raise ManifestError(f"source directory does not exist: {source_dir}")
    resolver = SourceResolver(source_dir)
    entries, manifest_status = _entries(args.manifest)
    blocked_statuses = {"draft", "rejected", "disabled", "unusable", "not_installed"}
    if manifest_status in blocked_statuses and not args.allow_draft:
        raise ManifestError(f"manifest status {manifest_status!r} blocks building; pass --allow-draft to override")
    seen: set[str] = set()
    output_paths: set[Path] = set()
    rendered: list[tuple[str, Image.Image]] = []
    planned = 0
    for entry in entries:
        key = str(entry.get("key", "")).strip()
        if not key:
            raise ManifestError("each manifest entry needs a key")
        if key in seen:
            raise ManifestError(f"duplicate manifest key: {key}")
        seen.add(key)
        entry_status = entry.get("status", entry.get("state"))
        if isinstance(entry_status, str) and entry_status.casefold() in blocked_statuses and not args.allow_draft:
            raise ManifestError(f"{key}: entry status {entry_status!r} blocks building; pass --allow-draft to override")
        if args.only and key != args.only:
            continue
        outputs = _output_specs(entry, args.output_root)
        if not outputs:
            raise ManifestError(f"{key}: no output or source master declared")
        for output, _ in outputs:
            if output in output_paths:
                raise ManifestError(f"duplicate output path: {output}")
            output_paths.add(output)
        # Resolve every declared asset before rendering so a typo cannot leave
        # a half-built collection on disk.
        for field in ("source_master", "frame", "primary", "secondary", "badge"):
            for value in _component_values(entry, field):
                resolver.resolve(_component_spec(value)[0])
        for value in _finished_values(entry):
            resolver.resolve(_component_spec(value)[0])
        if not _component_values(entry, "primary") and not _finished_values(entry):
            raise ManifestError(f"{key}: primary component or finished icon is required")
        preview_taken = False
        for output, size in outputs:
            planned += 1
            if args.dry_run:
                print(f"{key}: {size[0]}x{size[1]} -> {output}")
                continue
            image = _render(entry, resolver, size)
            _write(image, output)
            if args.preview_dir and not preview_taken:
                # One representative (the first derived output, or first
                # source master when there are no derived outputs) per recipe.
                rendered.append((_preview_label(entry), image))
                preview_taken = True
    if args.preview_dir and not args.dry_run:
        _preview_sheet(rendered, args.preview_dir)
    print(f"{'Validated' if args.dry_run else 'Built'} {planned} icon output(s) from {len(entries)} recipe(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
