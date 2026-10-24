"""Keep an exterior cutout while making the complete emblem interior opaque."""

from __future__ import annotations

from collections import Counter, deque
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def smooth_icon_edge(image: Image.Image) -> Image.Image:
    """Feather the one-pixel outer rim without softening the opaque center."""
    art = image.convert("RGBA").copy()
    alpha = art.getchannel("A")
    soft_rim = alpha.filter(ImageFilter.GaussianBlur(0.7))
    solid_center = alpha.filter(ImageFilter.MinFilter(3))
    alpha = ImageChops.lighter(soft_rim, solid_center)
    # Keep a fully transparent canvas edge even when the feather reaches it.
    alpha.paste(0, (0, 0, art.width, 1))
    alpha.paste(0, (0, art.height - 1, art.width, art.height))
    alpha.paste(0, (0, 0, 1, art.height))
    alpha.paste(0, (art.width - 1, 0, art.width, art.height))
    art.putalpha(alpha)
    return art


def _remove_flat_backing(image: Image.Image) -> tuple[Image.Image, tuple[int, int, int]]:
    """Recover the painted contour from the old flat convex-hull backing."""
    art = image.convert("RGBA").copy()
    transparent_colors = Counter(pixel[:3] for pixel in art.getdata() if pixel[3] == 0)
    opaque_colors = Counter(pixel[:3] for pixel in art.getdata() if pixel[3] == 255)
    exterior = transparent_colors.most_common(1)[0][0] if transparent_colors else (0, 0, 0)
    if exterior == (0, 0, 0):
        common_color, common_count = (opaque_colors.most_common(1)[0]
                                      if opaque_colors else ((29, 27, 24), 0))
        # A single legacy PNG lost its matte RGB in its transparent border.
        # An ordinary generated cutout often has black there too; preserve it.
        if common_count < 5000:
            return art, (29, 27, 24)
        matte = common_color
    else:
        matte = exterior
    # A matching broad flat area is evidence of the previous matte. Small
    # incidental color matches belong to the illustration and must stay.
    if opaque_colors[matte] < 100:
        return art, matte
    pixels = art.load()
    for y in range(art.height):
        for x in range(art.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha and max(abs(red - matte[0]), abs(green - matte[1]),
                             abs(blue - matte[2])) <= 2:
                pixels[x, y] = (red, green, blue, 0)
    return art, matte


def _painted_envelope(image: Image.Image) -> Image.Image:
    """Bridge narrow gaps while following the visible art instead of its hull."""
    alpha = image.getchannel("A")
    span = max(3, round(min(image.size) * 9 / 256))
    diameter = span if span % 2 else span + 1
    support = alpha.point(lambda value: 255 if value >= 64 else 0)
    closed = support.filter(ImageFilter.MaxFilter(diameter)).filter(
        ImageFilter.MinFilter(diameter)
    )
    rgba = Image.merge("RGBA", (closed, closed, closed, closed))
    return ImageChops.lighter(closed, enclosed_holes(rgba, opaque_threshold=128))


def interior_mask(image: Image.Image) -> Image.Image:
    """Opaque painted center, excluding its antialiased outer rim."""
    diameter = max(5, round(min(image.size) * 9 / 256))
    diameter += 1 - diameter % 2
    return _painted_envelope(image.convert("RGBA")).filter(
        ImageFilter.MinFilter(diameter)
    )


def interior_transparent_pixels(image: Image.Image) -> int:
    # Outer antialiasing and intentional gaps between distinct objects are
    # exterior. A transparent island surrounded by the painted emblem is not.
    return enclosed_holes(image, opaque_threshold=255).histogram()[255]


def solidify_icon_interior(image: Image.Image) -> Image.Image:
    """Fill the emblem's center and leave a clean, antialiased painted contour."""
    art, color = _remove_flat_backing(image)
    backing = Image.new("RGBA", art.size, (*color, 0))
    backing.putalpha(_painted_envelope(art))
    return smooth_icon_edge(ensure_exterior_border(Image.alpha_composite(backing, art)))


def ensure_exterior_border(image: Image.Image) -> Image.Image:
    """Retain a clear exterior even for an emblem that fills its square canvas."""
    if image.getchannel("A").getextrema()[0] == 0:
        return image.copy()
    art = image.copy()
    art.thumbnail((max(1, image.width - 2), max(1, image.height - 2)),
                  Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", image.size)
    canvas.alpha_composite(art, ((image.width - art.width) // 2,
                                 (image.height - art.height) // 2))
    return canvas


def enclosed_holes(image: Image.Image, *, opaque_threshold: int = 245) -> Image.Image:
    """Return pixels below opacity threshold that cannot reach the canvas edge."""
    alpha = image.convert("RGBA").getchannel("A")
    width, height = alpha.size
    outside = Image.new("L", (width + 2, height + 2), 255)
    transparent = alpha.point(lambda value: 0 if value >= opaque_threshold else 255)
    outside.paste(transparent, (1, 1))
    ImageDraw.floodfill(outside, (0, 0), 128, thresh=0)
    return outside.crop((1, 1, width + 1, height + 1)).point(
        lambda value: 255 if value == 255 else 0
    )


def hole_pixels(image: Image.Image) -> int:
    return enclosed_holes(image).histogram()[255]


def fill_enclosed_holes(image: Image.Image) -> Image.Image:
    """Fill each enclosed hole with the average color of its opaque border."""
    result = image.convert("RGBA").copy()
    holes = enclosed_holes(result)
    width, height = result.size
    marked = bytearray(holes.tobytes())
    if 255 not in marked:
        return result
    pixels = result.load()
    for start in range(len(marked)):
        if marked[start] != 255:
            continue
        marked[start] = 128
        pending = deque((start,))
        component = []
        boundary = []
        while pending:
            position = pending.popleft()
            component.append(position)
            x, y = position % width, position // width
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                neighbor = ny * width + nx
                if marked[neighbor] == 255:
                    marked[neighbor] = 128
                    pending.append(neighbor)
                elif marked[neighbor] == 0:
                    red, green, blue, alpha = pixels[nx, ny]
                    if alpha >= 245:
                        boundary.append((red, green, blue))
        if boundary:
            count = len(boundary)
            color = tuple(sum(pixel[channel] for pixel in boundary) // count
                          for channel in range(3))
        else:
            color = (45, 42, 38)
        for position in component:
            pixels[position % width, position // width] = (*color, 255)
    return result


def repair_file(path: Path) -> int:
    with Image.open(path) as image:
        original = image.convert("RGBA")
    count = interior_transparent_pixels(original)
    if count or original.getchannel("A").getextrema()[0] > 0:
        solidify_icon_interior(original).save(path)
    return count
