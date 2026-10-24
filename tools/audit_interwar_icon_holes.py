"""Audit all transparency inside the solid envelope of interwar icons."""

from __future__ import annotations

import argparse

from PIL import Image

import package_interwar_german_focus_icons as ger
import package_int_sov_focus_icons as sov
import package_int_whr_icons as whr
import package_interwar_idea_icons as idea
from interwar_icon_alpha import solidify_icon_interior, interior_transparent_pixels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", action="store_true", help="audit source PNGs instead of game DDS")
    parser.add_argument("--repair", action="store_true", help="make source PNG interiors fully opaque")
    args = parser.parse_args()
    if args.repair and not args.sources:
        parser.error("--repair requires --sources; repackage DDS textures afterward")
    groups = {
        "German focuses": [(name, ger.source_path(name) if args.sources else ger.goal_path(name))
                           for name in ger.verify_manifest()],
        "Soviet focuses": [(name, sov.source_path(name) if args.sources else sov.goal_path(name))
                           for name in sov.focus_ids()],
        "White Russian focuses": [(name, whr.source_path(name) if args.sources else whr.goal_path(name))
                                  for name, *_ in whr.rows()],
        "Ideas": [(name, idea.source_path(name) if args.sources else idea.texture_path(name))
                  for name in idea.ideas()],
    }
    total_affected = 0
    for group, entries in groups.items():
        affected = []
        for name, path in entries:
            if path.is_file():
                with Image.open(path) as icon:
                    art = icon.convert("RGBA")
                count = interior_transparent_pixels(art)
                if count or (args.repair and art.getchannel("A").getextrema()[0] > 0):
                    affected.append((count, name))
                    if args.repair:
                        corrected = solidify_icon_interior(art)
                        if interior_transparent_pixels(corrected):
                            raise ValueError(f"Interior opacity correction failed: {name}")
                        corrected.save(path, optimize=True)
        print(f"{group}: {len(affected)} icons with transparent interior pixels")
        total_affected += len(affected)
        for count, name in sorted(affected, reverse=True)[:20]:
            print(f"  {count:5} {name}")
    if total_affected and not args.repair:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
