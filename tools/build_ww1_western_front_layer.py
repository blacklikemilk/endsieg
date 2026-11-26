"""Build the operations map from Endsieg's province bitmap and country colours (Pillow 12 or newer)."""
import colorsys
import csv
from io import BytesIO
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageFilter, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
ART = Path("gfx/interface/endsieg_ww1_western_plans/live")
GFX = ROOT / "interface/endsieg_ww1_frontline_atlas.gfx"
GUI = ROOT / "interface/endsieg_ww1_western_plans.gui"
SCRIPT = ROOT / "common/scripted_guis/endsieg_ww1_western_plans.txt"
LOC = ROOT / "localisation/english/endsieg_ww1_western_plans_ui_l_english.yml"
TEXT = ROOT / "common/scripted_localisation/WWI_western_plans_ui.txt"
# Top-down bitmap crops, panel dimensions and origins in the decision window.
MAPS = {
    "west": ((2770, 482, 2986, 606), (466, 268), (17, 61)),
    "east": ((3085, 467, 3160, 515), (122, 80), (25, 232)),
}
# Keep the principal armies and neighbours distinct, including the two Russias.
INK_TAGS = "GER FRA BEL ENG HOL SWI LUX RIE POL AUH SOV USA ITA BUL ROM TUR JAP DEN SWE POR SPR WHR".split()


def replace_section(path, name, lines, before=None, indentation=""):
    original = path.read_bytes()
    text = original.decode("utf-8").replace("\r\n", "\n")
    begin = f"{indentation}# BEGIN generated map {name}\n"
    end = f"{indentation}# END generated map {name}\n"
    block = begin + "\n".join(lines) + "\n" + end
    if begin in text:
        left, rest = text.split(begin, 1)
        _, right = rest.split(end, 1)
        text = left + block + right
    elif before:
        assert text.count(before) == 1, before
        text = text.replace(before, block + before)
    else:
        text = text.rstrip("\n") + "\n" + block
    if b"\r\n" in original:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode())


def palette():
    countries = {}
    for f in (ROOT / "common/country_tags").glob("*.txt"):
        tags = re.sub(r"#.*", "", f.read_text(encoding="utf-8-sig")).split("dynamic_tags")[0]
        countries.update(re.findall(r'(?m)^\s*(\w{3})\s*=\s*"([^"]+)"', tags))
    pattern = r'\bcolor\s*=\s*(rgb|hsv)?\s*\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}'
    def rgb(match):
        mode, *values = match
        values = [float(v) for v in values]
        if mode.lower() == "hsv":
            values = [255 * c for c in colorsys.hsv_to_rgb(*values)]
        return tuple(min(255, round(v)) for v in values)
    colors = {}
    for tag, filename in countries.items():
        path = ROOT / "common" / filename
        if path.exists():
            matches = re.findall(pattern, path.read_text(encoding="utf-8-sig", errors="replace"), re.I)
            if matches:
                colors[tag] = rgb(matches[0])
    overrides = re.sub(r"#.*", "", (ROOT / "common/countries/colors.txt").read_text(encoding="utf-8-sig"))
    for tag, *value in re.findall(r'(\w{3})\s*=\s*\{\s*' + pattern, overrides, re.I):
        if tag in countries:
            colors[tag] = rgb(value)
    inks = {tag: colors[tag] for tag in INK_TAGS}
    groups = defaultdict(list)
    for tag, color in sorted(colors.items()):
        if tag not in inks:
            closest = min(inks, key=lambda ink: sum((a-b)**2 for a,b in zip(color, inks[ink])))
            groups[closest].append(tag)
    inks["other"] = (137, 135, 125)
    return inks, groups


def tiles(grid, width, height, inset):
    provinces, edges = defaultdict(list), defaultdict(list)
    for y in range(height):
        for x in range(width):
            if inset and (x in (0, width-1) or y in (0, height-1)):
                continue
            i = y*width+x
            pid = grid[i]
            if not pid:
                continue
            right = grid[i+1] if x+1 < width else pid
            down = grid[i+width] if y+1 < height else pid
            provinces[pid].append((x,y, 195 if pid != right or pid != down else 255))
            for neighbor in (right, down):
                if neighbor and neighbor != pid:
                    edges[tuple(sorted((pid,neighbor)))].append((x,y,255))
    for kind, collection in (("land", provinces), ("line", edges)):
        for key, points in sorted(collection.items()):
            xs, ys, _ = zip(*points)
            padding = int(kind == "line")
            x, y = max(0,min(xs)-padding), max(0,min(ys)-padding)
            w = min(width, max(xs)+padding+1)-x
            h = min(height, max(ys)+padding+1)-y
            mask = Image.new("L",(w,h))
            for px, py, value in points:
                mask.putpixel((px-x,py-y),value)
            yield kind, key, x, y, mask


def save_sheet(name, image, frames, gfx, hit_test=False):
    rel = ART / (name + ".dds")
    path = ROOT / rel
    encoded = BytesIO()
    image.save(encoded, format="DDS", pixel_format="DXT3" if hit_test else "DXT5")
    data = encoded.getvalue()
    if hit_test:
        # HOI4 reads BC2 alpha for province hit testing. Pillow can turn
        # partially transparent 4x4 blocks opaque, so pack the source mask.
        data = bytearray(data)
        assert data[84:88] == b"DXT3" and image.width % 4 == image.height % 4 == 0
        alpha = image.getchannel("A").tobytes()
        offset = 128
        for y in range(0, image.height, 4):
            for x in range(0, image.width, 4):
                for row in range(4):
                    start = (y + row) * image.width + x
                    a, b, c, d = alpha[start:start + 4]
                    data[offset + 2 * row] = (a >> 4) | (b & 0xf0)
                    data[offset + 2 * row + 1] = (c >> 4) | (d & 0xf0)
                offset += 16
        assert offset == len(data)
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
    hit = " transparencecheck = yes" if hit_test else ""
    gfx.append(f'\tspriteType = {{ name = "GFX_{name}" texturefile = "{rel.as_posix()}" noOfFrames = {frames}{hit} }}')


def main():
    # Older Pillow silently writes an uncompressed DDS when pixel_format is set.
    if int(pillow_version.split(".")[0]) < 12:
        raise RuntimeError("Building the DXT3 controller atlas requires Pillow 12 or later.")
    (ROOT / ART).mkdir(parents=True, exist_ok=True)
    inks, groups = palette()
    lookup = {}
    with (ROOT / "map/definition.csv").open(encoding="utf-8-sig") as f:
        for row in csv.reader(f, delimiter=";"):
            lookup[tuple(map(int,row[1:4]))] = int(row[0]) if row[4] == "land" else 0
    banks = defaultdict(list)
    with Image.open(ROOT / "map/provinces.bmp") as original:
        for view,(crop,size,_) in MAPS.items():
            pixels = original.crop(crop).convert("RGB").resize(size, Image.Resampling.NEAREST)
            pixels_rgb = pixels.get_flattened_data() if hasattr(pixels, "get_flattened_data") else pixels.getdata()
            grid = [lookup[pixel] for pixel in pixels_rgb]
            for kind, key, x, y, mask in tiles(grid, *size, view == "east"):
                step = 32 if kind=="land" else 16
                w,h = ((n+step-1)//step*step for n in mask.size)
                banks[kind,w,h].append((view,key,x,y,mask))

    old_assets = set(re.findall(r'texturefile = "([^"]+)"', GFX.read_text()))
    gfx, properties, checks, texts = [], [], [], []
    tooltips = {}
    layers = defaultdict(list)
    east_visible = "WW1_western_frontline_available = no WW1_western_plan_ui_kronprinz = yes"
    for (kind,w,h), items in sorted(banks.items()):
        capacity = min(64,2048//w)
        for start in range(0,len(items),capacity):
            batch = items[start:start+capacity]
            bank = f"wf_{kind}_{w}x{h}_{start//capacity}"
            alpha = Image.new("L",(w*len(batch),h))
            for index,(view,key,x,y,mask) in enumerate(batch):
                alpha.paste(mask,(index*w,0))
                frame = index+1
                if kind=="land":
                    scope = f"?global.province_controllers^{key}"
                    name = f"wf_{view}_p{key}"
                    tooltip = f"WW1_WP_controller_{key}"
                    tooltips[key] = f' {tooltip}:0 "Province {key}  |  Controller  \u00a7Y[{scope}.GetNameWithFlag]\u00a7!"'
                    properties.append(f'\t\t\t{name} = {{ image = "[{scope}.Get_{bank}]" frame = {frame} }}')
                    sprite = bank+"_other"
                    extra = f"pdx_tooltip = {tooltip}"
                    if view == "east":
                        checks.append(f"\t\t\t{name}_visible = {{ {east_visible} }}")
                else:
                    a,b = key
                    name = f"wf_{view}_line_{a}_{b}"
                    sprite = bank
                    extra = "alwaystransparent = yes"
                    gate = east_visible + " " if view == "east" else ""
                    checks.append(f"\t\t\t{name}_visible = {{ {gate}var:global.province_controllers^{a} = {{ var:global.province_controllers^{b} = {{ has_war_with = PREV }} }} }}")
                layers[view,kind].append(f'\t\t\ticonType = {{ name = "{name}" position = {{ x = {x} y = {y} }} spriteType = "GFX_{sprite}" frame = {frame} {extra} }}')
            if kind=="line":
                # Pad each shape independently so the halo cannot bleed across frames.
                image = Image.new("RGBA",alpha.size)
                for i,(_,_,_,_,mask) in enumerate(batch):
                    tile = Image.new("RGBA",mask.size,(151,42,34,0))
                    tile.putalpha(mask.filter(ImageFilter.MaxFilter(3)).point(lambda v:round(v*.88)))
                    tile.paste((255,231,184,255),(0,0,*mask.size),mask)
                    image.paste(tile,(i*w,0))
                save_sheet(bank,image,len(batch),gfx)
                continue
            text = [f"defined_text = {{\n\tname = Get_{bank}"]
            for ink,color in inks.items():
                # Darken province edges; alpha is binary so transparent pixels never take hover.
                image = Image.merge("RGBA", tuple(alpha.point(lambda v,c=c:round(v*c/255)) for c in color)
                                    +(alpha.point(lambda v:255 if v else 0),))
                save_sheet(bank+"_"+ink,image,len(batch),gfx,True)
                if ink!="other":
                    text.append(f'\ttext = {{ trigger = {{ tag = {ink} }} localization_key = "GFX_{bank}_{ink}" }}')
            for ink,tags in groups.items():
                choices = " ".join(f"original_tag = {tag}" for tag in [ink,*tags])
                text.append(f'\ttext = {{ trigger = {{ OR = {{ {choices} }} }} localization_key = "GFX_{bank}_{ink}" }}')
            text.extend([f'\ttext = {{ localization_key = "GFX_{bank}_other" }}',"}"])
            texts.extend(text)
    checks.append(f"\t\t\twf_east_control_visible = {{ {east_visible} }}")
    for view,(_,size,origin) in MAPS.items():
        x,y=origin;w,h=size
        panel=['\t\tcontainerWindowType = {',f'\t\t\tname = "wf_{view}_control"',
               f"\t\t\tposition = {{ x = {x} y = {y} }}",f"\t\t\tsize = {{ width = {w} height = {h} }}",
               *layers[view,"land"],*layers[view,"line"],"\t\t}"]
        next_icon = "western_plan_eastern_inset" if view=="west" else "western_plan_area_liege_active"
        replace_section(GUI,view,panel,f'\t\ticonType = {{\n\t\t\tname = "{next_icon}"',"\t\t")
    replace_section(SCRIPT,"controllers",["\t\tproperties = {",*properties,"\t\t}"],"\t\ttriggers = {","\t\t")
    replace_section(SCRIPT,"fronts",checks,"\t\t\twestern_plan_title_visible = ","\t\t\t")
    replace_section(LOC,"tooltips",[tooltips[i] for i in sorted(tooltips)])
    replace_section(TEXT,"inks",texts)
    index = "spriteTypes = {\n"+"\n".join(gfx)+"\n}\n"
    GFX.write_text(index,encoding="utf-8")
    new_assets = set(re.findall(r'texturefile = "([^"]+)"',index))
    for path in sorted(old_assets-new_assets):
        p = ROOT / path
        assert p.resolve().parent == (ROOT/ART).resolve() and re.fullmatch(r"wf_\w+\.(dds|tga)",p.name)
        p.unlink(missing_ok=True)
    print(f"{len(tooltips)} provinces, {len(properties)} controller bindings, {len(gfx)} atlas sheets")


if __name__ == "__main__":
    main()
