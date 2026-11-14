"""Restore vanilla window fills while retaining Endsieg hardware and newsprint.

Pass the installed HOI4 directory; outputs retain native dimensions and the
existing alpha channel. The scenario window has no matching vanilla asset, so
its empty field uses the centre tile from the native window instead.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / 'tools/endsieg_ui_spec.json').read_text(encoding='utf-8'))
STYLES = {'panel', 'panel_solid', 'thin', 'thin_solid', 'asymmetric', 'recess',
          'tooltip', 'scenario', 'country_screen', 'topbar', 'topbar_extended',
          'clock', 'lobby_details', 'lobby_settings', 'game_settings'}

def inset_mask(size, frames, edges):
    from PIL import ImageDraw
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    fw = w // frames
    l, t, r, b = edges
    for i in range(frames):
        if fw > l + r and h > t + b:
            draw.rectangle((i*fw+l, t, (i+1)*fw-r-1, h-b-1), fill=255)
    return mask

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vanilla', type=Path)
    ap.add_argument('--backup', type=Path, required=True)
    args = ap.parse_args()
    from PIL import ImageDraw
    native_window = Image.open(args.vanilla / 'gfx/interface/tiles/tiled_window_1b_border.dds').convert('RGBA')
    tile = native_window.crop((64, 64, 126, 126))
    count = 0
    for asset in SPEC['assets']:
        style = asset['style']
        if style not in STYLES:
            continue
        path = ROOT / asset['path']
        original = Image.open(path).convert('RGBA')
        if list(original.size) != asset['size']:
            raise ValueError(f'Unexpected mod dimensions: {path}')
        w, h = original.size
        if style == 'scenario':
            native = Image.new('RGBA', (w, h))
            for y in range(0, h, tile.height):
                for x in range(0, w, tile.width):
                    native.paste(tile, (x, y))
            mask = Image.new('L', (w, h), 0)
            ImageDraw.Draw(mask).rectangle((24, 48, 1032, h-25), fill=255)
        else:
            native_path = args.vanilla / asset['path']
            if not native_path.is_file():
                raise FileNotFoundError(native_path)
            native = Image.open(native_path).convert('RGBA')
            if native.size != original.size:
                raise ValueError(f'Native dimensions differ: {native_path}')
            if style == 'country_screen':
                mask = Image.new('L', (w,h), 0)
                ImageDraw.Draw(mask).rectangle((24,44,w-25,316),fill=255)
            elif style == 'lobby_details':
                mask = Image.new('L', (w,h), 0)
                d = ImageDraw.Draw(mask)
                d.rectangle((24,24,w-25,133),fill=255)
                d.rectangle((22,142,w-23,h-25),fill=255)
            elif style in {'topbar', 'topbar_extended'}:
                mask = inset_mask((w,h), 1, (14,6,14,6))
                ImageDraw.Draw(mask).rectangle((0,0,99,74),fill=0)
            else:
                edges = {'panel': (24,24,24,24), 'panel_solid': (24,24,24,24),
                         'asymmetric': (4,4,22,4), 'thin': (8,8,8,8),
                         'thin_solid': (8,8,8,8), 'tooltip': (12,12,12,12),
                         'recess': (9,5,9,5), 'clock': (9,5,9,5),
                         'lobby_settings': (24,24,24,24),
                         'game_settings': (24,24,24,24)}[style]
                # Mirror the frame limits used by the existing theme builder.
                fw = w // asset['frames']
                l,t,r,b = edges
                edges = (min(l,(fw-1)//2),min(t,(h-1)//2),min(r,(fw-1)//2),min(b,(h-1)//2))
                mask = inset_mask((w,h), asset['frames'], edges)
        result = Image.composite(native, original, mask)
        result.putalpha(original.getchannel('A'))
        # Frame pixels and alpha must remain unchanged.
        if ImageChops.difference(result.getchannel('A'), original.getchannel('A')).getbbox():
            raise ValueError(f'Alpha changed: {path}')
        backup = args.backup / asset['path']
        backup.parent.mkdir(parents=True,exist_ok=True)
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        result.save(path, format='DDS')
        verify = Image.open(path).convert('RGBA')
        if ImageChops.difference(verify.convert('RGB'), result.convert('RGB')).getbbox() or ImageChops.difference(verify.getchannel('A'), original.getchannel('A')).getbbox():
            raise ValueError(f'DDS round trip failed: {path}')
        count += 1
    print(f'Restored vanilla fills in {count} UI textures; original files backed up in {args.backup}')

if __name__ == '__main__':
    main()
