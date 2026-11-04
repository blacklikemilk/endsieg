"""Pack the new painted field-equipment UI into native-size HOI4 textures.

The painted masters supply corners, rails and blank faces. Existing title and
paper layers preserve the frontend's content and contrast. The game supplies
dynamic labels and values. Original dimensions, frame counts and alpha remain
authoritative.
"""
from __future__ import annotations

import argparse
import base64
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import zlib

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageMath, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = Path(__file__).with_name('endsieg_ui_spec.json')
SPEC = json.loads(SPEC_PATH.read_text(encoding='utf-8'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


@lru_cache(None)
def master(name):
    record = SPEC['artwork'][name]
    path = ROOT / record['path']
    if digest(path.read_bytes()) != record['sha256']:
        raise ValueError('Painted source changed; re-audit: ' + record['path'])
    return Image.open(path).convert('RGBA').crop(tuple(record['crop']))


@lru_cache(None)
def collar():
    im = master('housing')
    w, h = im.size
    return im.crop((int(w*.07), int(h*.07), int(w*.93), int(h*.93)))


def nine_slice(source, size, target_border, source_fraction=.24):
    """Scale the blank face while retaining the painted hardware at each edge."""
    w, h = size
    if isinstance(target_border, int):
        left = top = right = bottom = target_border
    elif len(target_border) == 2:
        left = right = target_border[0]
        top = bottom = target_border[1]
    else:
        left, top, right, bottom = target_border
    left, right = min(left, (w-1)//2), min(right, (w-1)//2)
    top, bottom = min(top, (h-1)//2), min(bottom, (h-1)//2)
    sw, sh = source.size
    if isinstance(source_fraction, tuple):
        fx, fy = source_fraction
    else:
        fx = fy = source_fraction
    sx = [0, int(sw*fx), sw-int(sw*fx), sw]
    sy = [0, int(sh*fy), sh-int(sh*fy), sh]
    dx, dy = [0, left, w-right, w], [0, top, h-bottom, h]
    out = Image.new('RGBA', size, (16, 18, 18, 255))
    for iy in range(3):
        for ix in range(3):
            tw, th = dx[ix+1]-dx[ix], dy[iy+1]-dy[iy]
            if tw <= 0 or th <= 0:
                continue
            part = source.crop((sx[ix], sy[iy], sx[ix+1], sy[iy+1]))
            part = part.resize((tw, th), Image.Resampling.LANCZOS)
            out.alpha_composite(part, (dx[ix], dy[iy]))
    return out


def native_tile(source, size, border):
    """Repeat native UI tile interiors while retaining their fixed corners."""
    sw, sh = source.size
    w, h = size
    sx, sy = [0,border,sw-border,sw], [0,border,sh-border,sh]
    dx, dy = [0,border,w-border,w], [0,border,h-border,h]
    out = Image.new('RGBA',size)
    for iy in range(3):
        for ix in range(3):
            tw, th = dx[ix+1]-dx[ix],dy[iy+1]-dy[iy]
            tile = source.crop((sx[ix],sy[iy],sx[ix+1],sy[iy+1]))
            piece = Image.new('RGBA',(tw,th))
            for y in range(0,th,tile.height):
                for x in range(0,tw,tile.width):
                    piece.paste(tile,(x,y))
            out.alpha_composite(piece,(dx[ix],dy[iy]))
    return out


def housing(size, style='panel'):
    if style == 'asymmetric':
        return nine_slice(master('housing'), size, (4, 4, 22, 4))
    if style in {'panel', 'panel_solid'}:
        im = nine_slice(master('housing'), size, 24)
        if style == 'panel':
            # Radio-grille finish is subtle, and confined to the readable inset.
            d = ImageDraw.Draw(im)
            for y in range(28, size[1]-28, 3):
                for x in range(28+(y%2), size[0]-28, 3):
                    p = im.getpixel((x, y))
                    d.point((x, y), fill=tuple(max(0, c-2) for c in p[:3])+(255,))
        return im
    if style in {'thin', 'thin_solid'}:
        return nine_slice(master('housing'), size, 8)
    if style == 'tooltip':
        return nine_slice(master('housing'), size, 12)
    # Blank glass/enamel apertures remain dark under the real native numbers.
    return nine_slice(master('housing'), size, (9, 5))


def push_key(size, state=0, style='button'):
    w, h = size
    source = master('push_key')
    im = nine_slice(source, size, (min(12, max(4, w//8)), min(7, max(3, h//5))), (.15, .28))
    factor = [.87, 1.04, .95][min(state, 2)]
    if style == 'disabled':
        factor = .63
    elif style == 'light':
        factor += .13
    im = ImageEnhance.Brightness(im).enhance(factor)
    if state:
        d = ImageDraw.Draw(im)
        # Native selected/hover frame: an amber retaining lip, not a new control.
        color = (146, 125, 76) if state == 1 else (182, 154, 95)
        d.rounded_rectangle((2, 2, w-3, h-3), radius=min(4, h//4), outline=color)
    return im


def selection_rim(im, state, inset=3):
    if state:
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((inset, inset, im.width-inset-1, im.height-inset-1),
                            radius=2, outline=(171, 145, 92), width=2)
    return im


def white_paper(source, regions=None, exclusions=None, neutral=False, protect_red=False):
    """Grade original paper into restrained newsprint without removing texture.

    Native luminance variation and folds remain continuous. No high-pass ink
    extraction, thresholded wear masks, flat fill or invented grain is used.
    """
    rgb = source.convert('RGB')
    r, g, b = rgb.split()
    luminance = ImageOps.grayscale(rgb)
    if neutral:
        # Actual newspaper stock is already grey: make only a small adjustment.
        tone = luminance.point([min(252, round(v*.98+12)) for v in range(256)])
        retain_chroma = .60
    else:
        # Preserve 94% of the source tonal range and a trace of its warm dye.
        tone = luminance.point([min(252, round(v*.94+33)) for v in range(256)])
        retain_chroma = .12
    paper = Image.merge('RGB', (tone.point(lambda v:min(255,v+1)), tone,
                                tone.point(lambda v:max(0,v-2))))
    paper = Image.blend(paper, rgb, retain_chroma)
    def smooth(v):
        t = max(0, min(1, (v-85)/105))
        return round(255*t*t*(3-2*t))
    mask = luminance.point([smooth(v) for v in range(256)])
    if not neutral and protect_red:
        # Yellow stock can be neutralised while printed rust/red pigment keeps
        # its colour. Smooth weights avoid cut-out edges and brown fragments.
        warmth = ImageMath.eval("convert(((g-b)-(r-g)+5)*255/30,'L')",r=r,g=g,b=b)
        warmth = warmth.point([round(255*(v/255)**2*(3-2*v/255)) for v in range(256)])
        mask = ImageChops.multiply(mask, warmth)
        # Hot edges in the burn atlas are coloured effects, not paper dye.
        scorch = ImageMath.eval("convert((b*100-r*35)*255/(r*10+1),'L')",r=r,b=b)
        mask = ImageChops.multiply(mask, scorch)
    for expression in ["convert(255-(g-r)*51,'L')", "convert(255-(b-g)*51,'L')"]:
        pigment = ImageMath.eval(expression,r=r,g=g,b=b)
        mask = ImageChops.multiply(mask,pigment)
    geometry = Image.new('L', source.size, 0 if regions else 255)
    draw = ImageDraw.Draw(geometry)
    for x0,y0,x1,y1 in regions or []:
        draw.rectangle((x0,y0,x1-1,y1-1),fill=255)
    for x0,y0,x1,y1 in exclusions or []:
        draw.rectangle((x0,y0,x1-1,y1-1),fill=0)
    mask = ImageChops.multiply(mask,geometry)
    mask = ImageChops.multiply(mask,source.getchannel('A').point(lambda p:255 if p else 0))
    out = Image.composite(paper,rgb,mask).convert('RGBA')
    out.putalpha(source.getchannel('A'))
    return out


def frontend(size, style, state, asset):
    """Frame existing content; portrait/flag holes are restored by build_asset."""
    w, h = size
    if style == 'scenario':
        im = housing(size, 'panel')
        # Genuine native title mount and briefing frame inside our outer case.
        plate = master('vanilla_scenario_titleplate')
        im.alpha_composite(plate, ((w-plate.width)//2, 4))
        im.alpha_composite(nine_slice(master('housing'), (526, 48), (14, 8)), (1044, 90))
        paper_asset = next(a for a in SPEC['assets']
                           if a['path']=='gfx/interface/tiles/tiled_paper_w_frame_bg.dds')
        im.alpha_composite(native_tile(build_asset(paper_asset), (526,590),64), (1044,142))
        return im
    if style == 'scenario_art':
        return master(asset['artwork']).resize(size, Image.Resampling.LANCZOS)
    if style == 'scenario_card':
        im = nine_slice(master('housing'), size, 8)
        im.alpha_composite(push_key((w-16, 36), state), (8, 148))
        return selection_rim(im, state, 2)
    if style == 'country_screen':
        im = Image.new('RGBA', size, (16, 18, 18, 255))
        im.alpha_composite(housing((w, h-35), 'panel'), (0, 35))
        # Vanilla internal fittings sit inside the shared Endsieg outer case.
        # Native coordinates preserve all live portrait, text and icon anchors.
        native = master('vanilla_country_screen')
        # Copy the raised title's native edge alpha without compositing it twice.
        im.paste(native.crop((378, 0, 849, 44)), (378, 0))
        im.alpha_composite(native.crop((8, 317, w-8, 360)), (8, 317))
        paper = white_paper(native, regions=[[26,453,424,700], [803,453,1199,700]])
        im.alpha_composite(paper.crop((12, 429, w-12, h-12)), (12, 429))
        return im
    if style == 'country_card':
        im = nine_slice(master('housing'), size, (10, 10))
        im.alpha_composite(nine_slice(master('housing'), (130, 179), 6), (10, 14))
        im.alpha_composite(nine_slice(master('housing'), (112, 60), 6), (18, 183))
        im.alpha_composite(push_key((142, 28), state), (4, 243))
        return selection_rim(im, state, 10)
    if style in {'country_minor', 'country_mini'}:
        # Native flag mounts have transparent margins, as well as a central
        # flag aperture. Put metal at the visible bounds, not outside that mask.
        alpha = Image.frombytes('L', tuple(asset['size']),
                                zlib.decompress(base64.b64decode(asset['alpha_zlib_base64'])))
        box = alpha.crop((state*w, 0, (state+1)*w, h)).point(lambda p: 255 if p>64 else 0).getbbox()
        x0, y0, x1, y1 = box
        mount = nine_slice(master('housing'), (x1-x0, y1-y0), 8 if h>50 else 4)
        if state:
            mount = ImageEnhance.Brightness(mount).enhance(1.13)
        selection_rim(mount, state, 1)
        im = Image.new('RGBA', size, (16, 18, 18, 255))
        im.alpha_composite(mount, (x0, y0))
        return im
    if style == 'country_filter':
        # Existing GUI starts at frame=2 (plain); frame=1 carries active accents.
        return push_key(size, 1 if state == 0 else 0)
    if style == 'frontend_bar':
        return nine_slice(master('housing'), size, (14, 8))
    if style == 'lobby_details':
        im = housing(size, 'panel')
        im.alpha_composite(housing((w-28, h-150), 'thin'), (14, 134))
        return im
    if style in {'lobby_settings', 'game_settings'}:
        return housing(size, 'panel')
    if style == 'play':
        # FE_START/READY are native text; the animated readiness mask is separate.
        im = nine_slice(master('housing'), size, (12, 9))
        face = push_key((w-24, h-18), state).convert('RGB')
        im.alpha_composite(face.convert('RGBA'), (12, 9))
        return im
    raise ValueError('Unknown frontend component: '+style)


def topbar(size, extended=False):
    im = nine_slice(master('housing'), size, (14, 6))
    # A blank shield mount sits behind the existing dynamic 82x52 flag.
    well = housing((92, 64), 'recess')
    im.alpha_composite(well, (6, 8))
    # Navigation glyphs and all value/progress widgets are separate native
    # controls. Never bake their positions, symbols or readings into this art.
    return im


def render_frame(asset, size, state):
    style = asset['style']
    if style in {'panel', 'panel_solid', 'asymmetric', 'thin', 'thin_solid', 'recess', 'tooltip', 'clock'}:
        im = housing(size, style)
        if state:
            im = ImageEnhance.Brightness(im).enhance(1.08)
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((2, 2, size[0]-3, size[1]-3), radius=3, outline=(150, 126, 75))
        return im
    if style in {'button', 'lobby', 'disabled', 'light'}:
        return push_key(size, state, style)
    if style in {'header', 'category'}:
        return nine_slice(master('housing'), size, (14, 8))
    if style in {'topbar', 'topbar_extended'}:
        return topbar(size, style == 'topbar_extended')
    if style == 'divider':
        source = master('housing')
        strip = source.crop((int(source.width*.24), 0, int(source.width*.76), int(source.height*.055)))
        return strip.resize(size, Image.Resampling.LANCZOS)
    if style == 'scroll':
        im = push_key(size)
        d = ImageDraw.Draw(im)
        x, y = size[0]//2, size[1]//2
        for delta in (-3, 0, 3):
            d.line((max(3, x-3), y+delta, min(size[0]-4, x+3), y+delta), fill=(13, 15, 14))
            d.line((max(3, x-3), y+delta+1, min(size[0]-4, x+3), y+delta+1), fill=(110, 109, 96))
        return im
    return frontend(size, style, state, asset)


def build_asset(asset):
    w, h = asset['size']
    frames = asset['frames']
    if asset['style'] == 'native_source':
        return master(asset['artwork']).copy()
    if asset['style'] == 'paper_surface':
        # Operative dossiers include 24 burn-animation frames. Transform their
        # original atlas in place, preserving all frame boundaries and holes.
        original = master(asset['artwork'])
        out = white_paper(original, asset.get('paper_regions'),
                          asset.get('paper_exclusions'), asset.get('neutral_paper', False),
                          asset.get('paper_protect_red', False))
        if asset.get('paper_reference_artwork'):
            # Selection hatching is printed status information, not yellowed
            # paper. Isolate its pigment against the unselected sheet.
            ar, ag, ab = original.convert('RGB').split()
            nr, ng, nb = master(asset['paper_reference_artwork']).convert('RGB').split()
            ink = ImageMath.eval("convert(255*((((ar-ag)-(nr-ng)>7)+((ag-ab)-(ng-nb)>9))>0),'L')",
                                 ar=ar, ag=ag, ab=ab, nr=nr, ng=ng, nb=nb)
            out.paste(original, (0, 0), ink)
        return out
    if w % frames:
        raise ValueError('Invalid horizontal sprite strip: '+asset['path'])
    out = Image.new('RGBA', (w, h))
    for i in range(frames):
        out.paste(render_frame(asset, (w//frames, h), i), (i*(w//frames), 0))
    alpha = zlib.decompress(base64.b64decode(asset['alpha_zlib_base64']))
    if len(alpha) != w*h:
        raise ValueError('Invalid native alpha: '+asset['path'])
    out.putalpha(Image.frombytes('L', (w, h), alpha))
    return out


def validate(game=None):
    errors, total = [], 0
    for name in SPEC['artwork']:
        master(name)
    for a in SPEC['assets']:
        p = ROOT/a['path']
        try:
            im = Image.open(p).convert('RGBA')
        except (OSError, ValueError) as exc:
            errors.append(a['path']+': '+str(exc))
            continue
        total += p.stat().st_size
        if list(im.size) != a['size']:
            errors.append(a['path']+': native dimensions changed')
        if digest(im.getchannel('A').tobytes()) != a['alpha_sha256']:
            errors.append(a['path']+': original alpha/click silhouette changed')
        if im.tobytes() != build_asset(a).tobytes():
            errors.append(a['path']+': does not match source component composition')
        fw = im.width//a['frames']
        states = {digest(im.crop((j*fw, 0, (j+1)*fw, im.height)).tobytes()) for j in range(a['frames'])}
        if len(states) != a['frames']:
            errors.append(a['path']+': sprite states became identical')
        raw = p.read_bytes()
        if raw[:4] != b'DDS ' or raw[84:88] != b'\x00\x00\x00\x00':
            errors.append(a['path']+': expected standard RGBA DDS')
        if game and a.get('native_size'):
            native = game/a['path']
            if not native.exists() or list(Image.open(native).size) != a['native_size']:
                errors.append(a['path']+': vanilla geometry needs re-audit')
    return {'result':'FAIL' if errors else 'PASS', 'assets':len(SPEC['assets']),
            'source_components':len(SPEC['artwork']), 'original_dimensions_preserved':not errors,
            'original_alpha_preserved':not errors, 'horizontal_frames_checked':True,
            'legacy_rgba_dds':True, 'installed_bytes':total, 'no_gui_binding_changes':True,
            'scenario_corner_logo':False, 'no_baked_readings_or_fake_gauges':True,
            'errors':errors, 'game_launched':False,
            'limits':'Asset and source checks only. Live composition, display scaling and UI interactions require an in-game test.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--game', type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    if not args.validate:
        for a in SPEC['assets']:
            p = ROOT/a['path']
            p.parent.mkdir(parents=True, exist_ok=True)
            build_asset(a).save(p, format='DDS')
    report = validate(args.game)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return int(bool(report['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
