# Scenario selection screen

The bookmark screen (Single Player → New Game → the grid of start dates) is driven by three things: `common/bookmarks/*.txt`, the `bookmark_entry` template and the `gamesetup_scenario_window` window in `interface/frontendgamesetupview.gui`, and the sprites those two reference.

This document covers the Endsieg redesign of that screen: what the engine fills in, what is static art, and what to change when a scenario is added.

## What the engine owns

The screen is not a scripted GUI; nothing on it can be branched per scenario except through these four elements:

| Element | Filled by the engine with |
| --- | --- |
| `bookmark_entry` `background` | `GFX_bookmark_entry_bg`, frame 0 normally, frame 1 while that card is selected |
| `bookmark_entry` `icon` | the bookmark's `picture = GFX_...` sprite, 1:1, no scaling |
| `bookmark_entry` `date` | the bookmark's start date, formatted per language (`1 January, 1914`) |
| `bookmark_title` / `bookmark_desc` | `name =` and `desc =` localisation of the selected bookmark |

Everything else on the window is static: the ENDSIEG wordmark, the `1910 - 1945` plate, the compass inset and all rules are baked into `scenario_bg.dds`, and the years burned into each painting come from the sprite itself. That is the ceiling of the layout - there is no per-scenario picture element, no metadata panel and no way to dim unselected cards.

## Layout

Coordinates are in the 1600x800 space of `gamesetup_scenario_window`, which HOI4 centres and scales like any other window (so the screen is resolution independent; at 2560x1440 with `gui_scale = 1` everything is drawn 1.33x larger).

| Band | y | Contents |
| --- | --- | --- |
| Header | 0 - 150 | wordmark art, diamond rule, `ENDSIEG_SELECT_SCENARIO` text at 126, date plate top right |
| Cards | 160 - 560 | `bookmarks` container at (36,160), grid slots 254x200, 6 columns x 2 rows |

The `bookmarks_grid` must carry an explicit pixel `size` (1524x400, exactly 6x2 slots) and the container `clipping = yes`. With `size = { width = 100%% height = 100%% }` inside an unsized container the grid resolves against the window instead, lays out four rows of slots and paints the unfilled ones as flat grey boxes over the detail panel.
| Detail panel | 566 - 786 | `bookmark_title` at (46,576), `bookmark_desc` at (46,620), compass inset right |
| Footer | 786 - 800 | `back_button` (40,-34) and `select_button` (-40,-34) |

Each card is 248x192: a 228x142 painting at (10,10), a caption band from y=152 with the engine's date, and a 1px frame that turns gold when selected.

## Files

- `interface/frontendgamesetupview.gui` - `bookmark_entry` template and `gamesetup_scenario_window`.
- `interface/endsieg_scenario_select.gfx` - `GFX_bookmark_entry_bg`, `GFX_select_date_bg` and one `GFX_select_date_*` per scenario. These names are the ones `common/bookmarks/` points at; keep them stable.
- `gfx/interface/scenario_select/` - built sprites (DXT5): `card_frame.dds` (248x384, two frames), `scenario_bg.dds` (1600x800), `card_<scenario>.dds` (228x142, one pixel per screen pixel).
- `tools/build_scenario_art.py` - builds every sprite above from the generated paintings in `.tmp/scenario_art/`.
- `localisation/replace/english/bookmarks_l_english.yml` - scenario names, descriptions and the two screen strings.

`localisation/replace/` is used because vanilla ships a file of the same name: the vanilla 1936 and 1939 bookmarks still load (the mod does not replace `common/bookmarks`), so their `GATHERING_STORM_*` and `BLITZKRIEG_*` keys are redefined here. Without them those two cards would show raw keys.

## Rebuilding the art

1. Put the source paintings in `.tmp/scenario_art/` (`1910_balkan_v2.png`, `1914_great_war_v2.png`, ... - the mapping is the `SOURCES` dict).
2. `python tools/build_scenario_art.py --preview`
3. Check `.tmp/card_preview.png` (cards at real size) and `.tmp/screen_mock.png` (`python .tmp/screen_mock.py`) before launching.

The painter is cropped to 228x142, tone-corrected per source (`TONE`), and the year is drawn with Constantia Bold rather than by the image model, so the numerals are always crisp and correctly spelled.

## Adding a scenario

1. Add the bookmark file to `common/bookmarks/`.
2. Add a `GFX_select_date_<name>` sprite in `interface/endsieg_scenario_select.gfx` pointing at a new card sprite, and set `picture =` in the bookmark to it.
3. Add a source entry to `SOURCES` in the build script and rebuild.
4. Add name and description keys to `bookmarks_l_english.yml`.
5. The grid holds twelve cards (6x2). A thirteenth bookmark will not render: raise `max_slots` and re-flow `slotsize`, `card` size in the `bookmark_entry`, and the detail panel in the same commit.

## Known limits

- No per-scenario detail image is possible; the mock-up's large preview panel cannot be built from engine data.
- No per-scenario metadata (playable nations, key features) exists in the bookmark format.
- `buttonText` for the confirm button is localised (`ENDSIEG_START_SCENARIO`) but its sprite is the vanilla `GFX_button_221x34`, so it cannot be made visually primary without new button art.
- The card grid at 6 columns is the practical maximum: 12 scenarios in two rows leaves 254px per column at 1600px width.

## Future plans

- Scenario-specific card art for any bookmark added later (the 1933 and 1950 sprites are kept in the gfx file for this reason).
- A gold primary button sprite (`GFX_button_221x34_gold`) to give START GAME more weight than BACK.

## Icons and art needed

| Asset | Sprite | File | Size |
| --- | --- | --- | --- |
| Card frame, normal + selected | `GFX_bookmark_entry_bg` | `gfx/interface/scenario_select/card_frame.dds` | 248x384 (DXT5) |
| Screen background | `GFX_select_date_bg` | `gfx/interface/scenario_select/scenario_bg.dds` | 1600x800 (DXT5) |
| Scenario paintings | `GFX_select_date_*` | `gfx/interface/scenario_select/card_*.dds` | 228x142 (DXT5) |
| Primary button (wanted) | - | `gfx/interface/scenario_select/button_gold.dds` | 221x34, 2 frames |
