"""Validate and draw the five expanded interwar trees without launching HOI4.

Run with --baseline PATH to also check that earlier working focus IDs and rewards
were preserved. PNG/SVG/HTML previews are written to --output (a temp directory by
default), leaving the game files untouched.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import html
import io
import json
from pathlib import Path
import re
import tempfile

from PIL import Image, ImageDraw, ImageFont
from validate_focus_split import TOKEN, nodes

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = {
    "Japan": "japan", "France": "france", "United Kingdom": "uk",
    "Italy": "italy", "United States": "usa",
}


def text(path):
    return path.read_text(encoding="utf-8-sig")


def field(block, key, default=None):
    return next((n for n in block["children"] if n["key"] == key), default)


def value(block, key, default=None):
    n = field(block, key)
    return n["value"].strip('"') if n else default


def descend(block):
    for n in block["children"]:
        yield n
        yield from descend(n)


def focus_data(path):
    source = text(path)
    roots = nodes(source)
    tree = next(n for n in roots if n["key"] == "focus_tree")
    focuses = [n for n in tree["children"] if n["key"] == "focus"]
    return source, tree, focuses


def normalized(source, block):
    if not block:
        return ""
    return " ".join(m[0] for m in TOKEN.finditer(source[block["start"]:block["end"]])
                    if not m[0].startswith("#"))


def strict_balance(source, label, errors):
    depth = 0
    for m in TOKEN.finditer(source):
        if m[0] == "{":
            depth += 1
        elif m[0] == "}":
            depth -= 1
            if depth < 0:
                errors.append(f"{label}: extra closing brace")
                return
    if depth:
        errors.append(f"{label}: unbalanced braces")


def declarations(folders, root_key, levels):
    out = set()
    for folder in folders:
        if not folder.exists():
            continue
        for path in folder.glob("*.txt"):
            try:
                for n in nodes(text(path)):
                    if n["key"] != root_key:
                        continue
                    blocks = [n]
                    for _ in range(levels):
                        blocks = [c for b in blocks for c in b["children"]
                                  if c["value"] == "{"]
                    out.update(b["key"] for b in blocks)
            except (ValueError, UnicodeError):
                continue
    return out


def available_date(block):
    available = field(block, "available")
    if not available:
        return (0, 0, 0)
    dates = [tuple(map(int, n["value"].split(".")[:3]))
             for n in descend(available) if n["key"] == "date" and n["op"] in (">", ">=")
             and re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", n["value"])]
    return max(dates, default=(0, 0, 0))


def fonts(size):
    for name in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def wrap(title, limit=23):
    lines, current = [], ""
    for word in title.split():
        if current and len(current) + len(word) + 1 > limit:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    lines.append(current)
    return lines


def sprite_map(vanilla):
    sprites = {}
    for folder in (vanilla / "interface", ROOT / "interface"):
        if not folder.exists():
            continue
        for path in folder.glob("*.gfx"):
            try:
                for root in nodes(text(path)):
                    for n in root["children"]:
                        name, texture = value(n, "name"), value(n, "texturefile")
                        if name:
                            sprites[name] = texture
            except (ValueError, UnicodeError):
                continue
    return sprites


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vanilla", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--layout-only", action="store_true",
                        help="Require a baseline and preserve all non-layout tree content")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.layout_only and not args.baseline:
        parser.error("--layout-only requires --baseline")
    out = args.output or Path(tempfile.mkdtemp(prefix="endsieg_interwar_previews_"))
    out.mkdir(parents=True, exist_ok=True)
    errors, warnings, reports = [], [], []
    sprites = sprite_map(args.vanilla)
    ideas = declarations([args.vanilla / "common/ideas", ROOT / "common/ideas"], "ideas", 2)
    event_ids = set()
    for folder in (args.vanilla / "events", ROOT / "events"):
        for path in folder.glob("*.txt"):
            event_ids.update(re.findall(r"(?m)^\s*id\s*=\s*([A-Za-z0-9_]+\.\d+)\b", text(path)))
    state_ids = set()
    for path in (ROOT / "history/states").glob("*.txt"):
        source = text(path)
        # State files are outside this focus-tree audit. A malformed unrelated
        # history block must not prevent drawing and checking the five trees.
        match = re.search(r"\bstate\s*=\s*\{\s*id\s*=\s*(\d+)", source)
        if match:
            state_ids.add(match[1])
    script_ids = set()
    for folder in (ROOT / "common/scripted_effects", ROOT / "common/scripted_triggers"):
        for path in folder.glob("*.txt"):
            try:
                script_ids.update(n["key"] for n in nodes(text(path)) if n["value"] == "{")
            except (ValueError, UnicodeError):
                continue
    loc = {}
    for folder in (args.vanilla / "localisation/english", ROOT / "localisation"):
        for path in folder.rglob("*_l_english.yml"):
            for key, title in re.findall(r'^\s*([^\s:]+):\d*\s+"(.*)"\s*$', text(path), re.M):
                loc[key] = title
    global_ids = Counter()
    for path in (ROOT / "common/national_focus").glob("*.txt"):
        try:
            for n in nodes(text(path)):
                if n["key"] == "focus_tree":
                    global_ids.update(value(f, "id") for f in n["children"] if f["key"] == "focus")
                elif n["key"] in ("shared_focus", "joint_focus") and n["value"] == "{":
                    global_ids.update([value(n, "id")])
        except (ValueError, UnicodeError):
            continue
    icon_cache = {}

    def icon(name):
        if name not in icon_cache:
            result = None
            texture = sprites.get(name)
            if texture:
                for base in (ROOT, args.vanilla):
                    path = base / texture
                    if path.exists():
                        try:
                            result = Image.open(path).convert("RGBA")
                            result.thumbnail((46, 46), Image.Resampling.LANCZOS)
                        except OSError:
                            pass
                        break
            icon_cache[name] = result
        return icon_cache[name]

    galleries, thumbnails = [], []
    for country, slug in COUNTRIES.items():
        path = ROOT / f"common/national_focus/INT - {country}.txt"
        source, tree, raw = focus_data(path)
        strict_balance(source, path.name, errors)
        idea_path = ROOT / f"common/ideas/INT - {country}.txt"
        strict_balance(text(idea_path), idea_path.name, errors)
        country_loc = ROOT / f"localisation/replace/english/endsieg_interwar_{slug}_l_english.yml"
        if not country_loc.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{country}: localisation is missing UTF-8 BOM")
        own_keys = Counter(re.findall(r'^\s*([^\s:]+):\d*\s+".*"\s*$', text(country_loc), re.M))
        for key, count in own_keys.items():
            if count > 1:
                errors.append(f"{country}: duplicate localisation key {key}")
        by_id = {value(f, "id"): f for f in raw}
        if len(by_id) != len(raw):
            errors.append(f"{country}: duplicate focus within tree")
        positions = {}

        def position(ident, trail=()):
            if ident in positions:
                return positions[ident]
            if ident in trail:
                raise ValueError(f"{country}: relative-position cycle {trail + (ident,)}")
            block = by_id[ident]
            x, y = int(value(block, "x", 0)), int(value(block, "y", 0))
            relative = value(block, "relative_position_id")
            if relative:
                if relative not in by_id:
                    errors.append(f"{country}: missing relative position {relative}")
                else:
                    dx, dy = position(relative, trail + (ident,))
                    x, y = x + dx, y + dy
            positions[ident] = x, y
            return x, y

        edges = []
        baseline = {}
        if args.baseline:
            oldpath = args.baseline / f"common/national_focus/INT - {country}.txt"
            oldsource, oldtree, oldraw = focus_data(oldpath)
            baseline = {value(f, "id"): f for f in oldraw}
            if value(oldtree, "id") != value(tree, "id"):
                errors.append(f"{country}: focus-tree ID changed")
            if args.layout_only:
                def content_fields(block, source, omit):
                    return [normalized(source, n) for n in block["children"] if n["key"] not in omit]
                if set(by_id) != set(baseline):
                    errors.append(f"{country}: focus set changed during layout-only edit")
                if content_fields(oldtree, oldsource, {"focus", "initial_show_position", "continuous_focus_position"}) != content_fields(tree, source, {"focus", "initial_show_position", "continuous_focus_position"}):
                    errors.append(f"{country}: non-layout tree settings changed")
                for ident in set(by_id) & set(baseline):
                    if content_fields(baseline[ident], oldsource, {"x", "y", "relative_position_id"}) != content_fields(by_id[ident], source, {"x", "y", "relative_position_id"}):
                        errors.append(f"{country}: non-layout focus content changed: {ident}")
            for ident, old in baseline.items():
                if ident not in by_id:
                    errors.append(f"{country}: removed original focus {ident}")
                elif normalized(oldsource, field(old, "completion_reward")) != normalized(source, field(by_id[ident], "completion_reward")):
                    warnings.append(f"{country}: original reward changed: {ident}")
        for ident, block in by_id.items():
            position(ident)
            if global_ids[ident] != 1:
                errors.append(f"{country}: global focus ID occurs {global_ids[ident]} times: {ident}")
            for suffix in ("", "_desc"):
                if ident + suffix not in loc:
                    errors.append(f"{country}: missing localisation {ident + suffix}")
            if value(block, "icon") not in sprites:
                errors.append(f"{country}: undefined sprite {value(block, 'icon')}")
            for n in descend(block):
                if n["key"] in ("country_event", "news_event") and n["value"] == "{":
                    event = value(n, "id")
                    if event and event not in event_ids:
                        errors.append(f"{country}: undefined event {event} in {ident}")
                if n["key"].startswith("INT_") and n["value"] == "yes" and n["key"] not in script_ids:
                    errors.append(f"{country}: undefined scripted effect/trigger {n['key']} in {ident}")
                state = n["key"] if n["key"].isdigit() and n["value"] == "{" else None
                if n["key"] in ("owns_state", "controls_state", "has_full_control_of_state", "transfer_state", "add_state_core", "set_capital") and n["value"].isdigit():
                    state = n["value"]
                if state and state not in state_ids:
                    errors.append(f"{country}: undefined state {state} in {ident}")
                if n["key"] in ("focus", "has_completed_focus", "complete_national_focus", "relative_position_id") and n["value"] != "{" and n["value"] not in global_ids:
                    errors.append(f"{country}: unresolved focus {n['value']} in {ident}")
                if n["key"] in ("add_ideas", "remove_ideas", "idea"):
                    if n["value"] == "{":
                        values = [m[0] for m in TOKEN.finditer(source[n["start"]:n["end"]])][3:-1]
                    else:
                        values = [n["value"]]
                    for idea in values:
                        if re.fullmatch(r"INT_[A-Z]+_[A-Za-z0-9_]+", idea) and idea not in ideas:
                            errors.append(f"{country}: undefined idea {idea} in {ident}")
            for p in [n for n in block["children"] if n["key"] == "prerequisite"]:
                for n in p["children"]:
                    if n["key"] == "focus" and n["value"] in by_id:
                        parent = n["value"]
                        edges.append((parent, ident))
                        if position(parent)[1] >= position(ident)[1]:
                            errors.append(f"{country}: prerequisite is not above its child: {parent} -> {ident}")
                        if ident not in baseline and available_date(by_id[parent]) > available_date(block) != (0, 0, 0):
                            warnings.append(f"{country}: earlier dated child follows later parent: {parent} -> {ident}")
        for ident, (x, y) in positions.items():
            for other, (ox, oy) in positions.items():
                if ident < other and y == oy and abs(x - ox) < 3:
                    errors.append(f"{country}: nodes too close at row {y}: {ident} ({x}), {other} ({ox})")
        parents = {ident: [] for ident in by_id}
        for parent, child in edges:
            parents[child].append(parent)

        def cycle(ident, trail=()):
            if ident in trail:
                errors.append(f"{country}: prerequisite cycle {' -> '.join(trail + (ident,))}")
                return
            for parent in parents[ident]:
                cycle(parent, trail + (ident,))
        for ident in by_id:
            cycle(ident)
        xs, ys = zip(*positions.values())
        continuous = field(tree, "continuous_focus_position")
        if continuous and int(value(continuous, "y", 0)) <= (max(ys) + 1) * 130:
            warnings.append(f"{country}: continuous-focus panel may overlap the expanded tree")
        report = {"country": country, "tree": value(tree, "id"), "focuses": len(raw),
                  "added": len(set(by_id) - set(baseline)), "bounds": [min(xs), min(ys), max(xs), max(ys)]}
        reports.append(report)
        width, height = (max(xs) - min(xs)) * 50 + 190, max(ys) * 116 + 180
        canvas = Image.new("RGB", (width, height), "#101722")
        draw = ImageDraw.Draw(canvas)
        titlefont, labelfont = fonts(26), fonts(12)
        draw.text((25, 18), f"{country} · {len(raw)} interwar focuses", font=titlefont, fill="#f1d8a5")
        coords = {ident: (95 + (x - min(xs)) * 50, 78 + y * 116) for ident, (x, y) in positions.items()}
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
               '<rect width="100%" height="100%" fill="#101722"/>',
               f'<text x="25" y="40" fill="#f1d8a5" font-family="Segoe UI,Arial,sans-serif" font-size="26">{html.escape(country)} · {len(raw)} interwar focuses</text>']
        for parent, child in edges:
            px, py = coords[parent]
            cx, cy = coords[child]
            mid = cy - 16
            points = [(px, py + 88), (px, mid), (cx, mid), (cx, cy)]
            draw.line(points, fill="#628596", width=2)
            svg.append(f'<path d="M {px} {py+88} V {mid} H {cx} V {cy}" fill="none" stroke="#628596" stroke-width="2"/>')
        for ident, block in by_id.items():
            cx, cy = coords[ident]
            title = loc.get(ident, ident)
            lines = wrap(title)
            border = "#d7b573" if not parents[ident] else "#435b71"
            draw.rounded_rectangle((cx - 70, cy, cx + 70, cy + 88), radius=9, fill="#1c2838", outline=border, width=2)
            picture = icon(value(block, "icon"))
            if picture:
                canvas.paste(picture, (round(cx - picture.width / 2), cy + 5), picture)
            else:
                draw.ellipse((cx - 18, cy + 7, cx + 18, cy + 43), outline="#d7b573", width=2)
            for row, line in enumerate(lines[:3]):
                draw.text((cx, cy + 51 + row * 12), line, font=labelfont, fill="#e2e7ef", anchor="mt")
            desc = loc.get(ident + "_desc", "")
            tooltip = html.escape(f"{title}\n{ident}\n{desc}")
            svg.append(f'<g><title>{tooltip}</title><rect x="{cx-70}" y="{cy}" width="140" height="88" rx="9" fill="#1c2838" stroke="{border}" stroke-width="2"/>')
            if picture:
                buf = io.BytesIO()
                picture.save(buf, format="PNG")
                uri = base64.b64encode(buf.getvalue()).decode("ascii")
                svg.append(f'<image x="{cx-picture.width/2}" y="{cy+5}" width="{picture.width}" height="{picture.height}" href="data:image/png;base64,{uri}"/>')
            for row, line in enumerate(lines[:3]):
                svg.append(f'<text x="{cx}" y="{cy+62+row*12}" text-anchor="middle" fill="#e2e7ef" font-family="Segoe UI,Arial,sans-serif" font-size="12">{html.escape(line)}</text>')
            svg.append('</g>')
        svg.append('</svg>')
        svgpath = out / f"{slug}.svg"
        svgpath.write_text("\n".join(svg), encoding="utf-8")
        canvas.save(out / f"{slug}.png")
        thumb = canvas.copy()
        thumb.thumbnail((1100, 780), Image.Resampling.LANCZOS)
        thumbnails.append((country, thumb))
        galleries.append(f'<option value="{slug}.svg">{html.escape(country)} ({len(raw)} focuses)</option>')
    row_heights = [max(thumb.height for _, thumb in thumbnails[i:i+2]) + 95
                   for i in range(0, len(thumbnails), 2)]
    row_tops = [sum(row_heights[:i]) for i in range(len(row_heights))]
    overview = Image.new("RGB", (2200, sum(row_heights)), "#101722")
    for i, (country, thumb) in enumerate(thumbnails):
        col, row = i % 2, i // 2
        ImageDraw.Draw(overview).text((col * 1100 + 25, row_tops[row] + 10), country, font=fonts(30), fill="#f1d8a5")
        overview.paste(thumb, (col * 1100 + (1100 - thumb.width) // 2, row_tops[row] + 60))
    overview.save(out / "overview.png")
    page = '<!doctype html><html><head><meta charset="utf-8"><title>Endsieg interwar layouts</title><style>body{margin:0;background:#101722;color:#eef0f5;font:16px Segoe UI,Arial}header{position:sticky;top:0;padding:14px 24px;background:#1c2838;display:flex;gap:16px;align-items:center}select,button{font:inherit;background:#101722;color:#fff;border:1px solid #5b7487;padding:6px}main{overflow:auto;height:calc(100vh - 68px)}object{display:block;transform-origin:top left}</style></head><body><header><strong>Endsieg interwar layouts</strong><select id="country">'+''.join(galleries)+'</select><button id="minus">−</button><span id="scale">100%</span><button id="plus">+</button><button id="fit">Fit width</button><span>Hover a focus for its description.</span></header><main id="view"><object id="tree" type="image/svg+xml" data="japan.svg"></object></main><script>let zoom=1;const tree=document.getElementById("tree"),view=document.getElementById("view");function apply(){tree.style.zoom=zoom;document.getElementById("scale").textContent=Math.round(zoom*100)+"%"}document.getElementById("country").onchange=e=>{tree.data=e.target.value;view.scrollTo(0,0)};document.getElementById("minus").onclick=()=>{zoom=Math.max(.1,zoom-.1);apply()};document.getElementById("plus").onclick=()=>{zoom=Math.min(2,zoom+.1);apply()};document.getElementById("fit").onclick=()=>{zoom=(view.clientWidth-20)/(tree.contentDocument.documentElement.width.baseVal.value);apply()};</script></body></html>'
    (out / "index.html").write_text(page, encoding="utf-8")
    result = {"trees": reports, "errors": sorted(set(errors)), "warnings": sorted(set(warnings)), "output": str(out)}
    (out / "validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
