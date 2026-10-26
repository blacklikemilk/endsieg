> **Superseded (icons):** the user rejected the painted `GFX_iran_focus_*` illustration set. Any recommendation below to use, register or generate those sprites is void; Iran focus icons stay vanilla/DLC-style (see `docs/plans/iran_1910_1945/icon_policy.md`).

# TFR reference study and application to Iran

## Purpose

This note records what was actually inspected in The Fire Rises (`3350890356`) and the design rules taken from it, so the Iran package can be judged against a stated benchmark instead of an impression.

## Files examined

| Path under `3350890356` | What was measured |
| --- | --- |
| `common/national_focus/TFR_national_focus_GER.txt` | 163 focuses, 4 roots, max chain depth 7, y span 0-6, 114 `available`, 12 `bypass`, 9 `allow_branch`, 70 mutually exclusive pairs, 25 `search_filters` uses |
| `common/national_focus/TFR_national_focus_FRA.txt` | 205 focuses, 19 roots, depth 9, y span -5 to 8, 75 mutually exclusive, 116 `allow_branch` |
| `common/national_focus/TFR_national_focus_USB.txt` | 310 focuses, depth 16, y span -5 to 11 (their longest tree) |
| `common/national_focus/TFR_national_focus_SOV.txt` + `_medvedev` (654) + `_fascist` (449) + `_communist_new` (327) | Branch sets that replace the whole tree per political outcome rather than coexisting |
| `common/national_focus/` (60 files) | Median focus count among trees of 40+ is 98 |
| `interface/TFR_goals.gfx` | 5,942 sprite registrations, `GFX_focus_<TAG>_<topic>` naming, texturefile to PNG |
| `gfx/interface/goals/<TAG>/` | 6,063 icon files; size distribution 150-190 x 134-170, RGBA, about 25% of each canvas fully transparent |
| `interface/nationalfocusview.gfx` | Their focus-tree view overrides (frame-animated ongoing/highlight sprites) |
| 10 GER focus icons supplied by the maintainer | Composition and technique below |

No file under `GFX_focus_tree_bg` is declared anywhere in TFR, and no `focus_tree` in their files carries a `background` field. **TFR does not ship custom focus-tree backgrounds.** The tree sits on the vanilla backdrop and the visual identity comes from a global interface skin plus the icons themselves. That answers the background question for this project: do not build per-era tree backgrounds; spend the effort on icons and the shared skin.

## Tree geometry

| Tree | Focuses | Roots | Max depth | Depth 3-5 share | y span |
| --- | --- | --- | --- | --- | --- |
| TFR Germany | 163 | 4 | 7 | 69% | 0-6 |
| TFR France | 205 | 19 | 9 | 62% | -5-8 |
| TFR (longest, USB) | 310 | 8 | 16 | 30% | -5-11 |
| Endsieg Iran WW1 (before) | 85 | 8 | 11 | 42% | 0-12 |
| Endsieg Iran interwar (before) | 129 | 5 | 15 | 24% | 0-19 |
| Endsieg Iran WW2 (before) | 93 | 4 | 14 | 20% | 0-22 |

The single largest discrepancy is direction. TFR builds **wide and shallow**: most content sits three to five steps from a root, with long horizontal fans either side of a political centre. The Iran chapters were built **narrow and deep**: long vertical ladders reaching fourteen or fifteen steps.

## Principles extracted

1. **Horizontal fans, not vertical ladders.** A branch grows sideways as it develops; depth is reserved for a genuine escalation, not for sequencing parallel projects.
2. **Relative positioning.** 199 of 205 French focuses and 160 of 163 German ones declare `relative_position_id`. Positions follow the design, and moving a parent carries its children, which is what keeps large trees coherent.
3. **Political centres fan out, they do not stack.** Germany keeps its ideology space at the centre and hangs economy left, army right, with `allow_branch` hiding the losing side (9 uses in Germany, 116 in France where whole governments are replaced).
4. **Mutual exclusion carries the narrative.** 70 exclusive pairs in a 163-focus tree. Most of the authored content is never seen in one run; the tree's size is the sum of possible governments, not a checklist.
5. **Separate trees for separate regimes.** The Soviet files replace the entire tree per outcome (654 / 449 / 327 focuses across three trees) rather than branching inside one.
6. **Density without clutter.** `available` (114 uses in Germany) hides dead options in place, so the tree stays visually full but only shows what is currently plausible.

## Icon technique

Measured directly from `gfx/interface/goals/` (5,850 PNG across 23 countries; 574 German, 787 French, 2,002 Soviet) and read visually from a 16-icon German sample.

- **Canvas**: median 175x150, range 140-218 wide and 120-190 high. 90% are wider than tall. Median 28% of the canvas is fully transparent, and 30% of the visible pixels are near-black.
- **Background**: a second, very dark, desaturated photographic layer — a shadowed room, dusk ridge, crowd or skyline — graded to near-black at the edges with a soft radial falloff. It is **not flat black**, and it is not a clean rectangle of scenery either.
- **Subject**: for figure icons, a bust or half-figure filling 40-60% of the tile, with the head at roughly a quarter to a third of the tile height. Crowd icons shrink individuals to 10-25% and let a flag or banner carry the mass.
- **Construction**: painted photobash from period photographs, over-painted and relit into one image, not clean-cut photo collage. Faces are softened and unified; edges are dark contours rather than hard alpha cut-outs.
- **Colour**: fully desaturated base plus one or two saturated accents — most often a crimson banner or drape placed *behind* the subject as a halo. Gold, blue or green appear as a secondary accent. Skin stays muted.
- **Tagged devices reused across the set**: red banner behind the subject, radial spotlight glow, skyline or map band, silhouetted crowd, duotone wash, dark vignette.
- **Separation**: dark contour lines, contact shadow, rim highlights and vignette. No outlines, no outer glow, no sticker border.
- **Lighting**: single dominant warm rim light from one side against a cool shadow side, high contrast.
- **Typography**: TFR uses it inside icons. Endsieg's house rule forbids generated text, so that device is deliberately dropped.

An earlier note in this file claimed the icons were hard alpha cut-outs on pure black. That was wrong, and the correction above is what the new candidates are built to.

## What is being applied to Iran

- Regenerate every Iran focus icon to the technique above, at 188x150 rather than 94x86, with the black field, two accents (Qajar crimson, brass gold), and one graphic overlay per icon where it helps.
- Keep the approved reference plates: the Cossack rider is the standard the rest must match.
- Do not build era-specific tree backgrounds; TFR has none and the mod's shared interface already supplies the backdrop.
- The geometry rework (wide and shallow, relative positioning, political centres that fan out) is the next content task after the icon set; changing it now would invalidate the icon-to-focus mapping being built.

## Status of the previous icon set

The 47 icons currently wired in `gfx/interface/goals/iran_campaign/` were produced before this study, in a different technique (opaque 94x86 painted squares). They are functional but do not meet this benchmark and are being replaced rather than extended.
