# Endsieg field-equipment interface

The decisions sidebar is the finish reference for the shared controls and
frontend: warm metal frames, brown-black Bakelite keys, recessed counter
windows, dark enamel label plates and restrained amber selection rims.

The game supplies the text, values, flags, symbols, progress fills and input
bindings. The physical component art frames those live controls. The scenario
header has no corner logo; values and indicators remain live.

## Components and coverage

- Cast-steel instrument casings for major windows and device panels.
- Smaller metal retaining bezels for secondary panels and tooltips.
- Brown Bakelite push-caps for buttons, menu keys and selectable icon plates.
- Recessed dark counter windows around existing numeric fields.
- An unlabelled topbar housing and shield mount behind the dynamic country flag.
- Dark enamel title bars and a mechanical scroll grip.

The pack exports 128 existing texture paths. Sprite names, original dimensions,
horizontal frame counts and complete alpha channels are preserved. The unusual
right-hand gutter, DLC-sensitive navigation positions, original symbols,
decision completion stamp and live ratio bars remain supported.

The rebuilt scenario window, all twelve scenario-card frames, country portrait/flag
mounts, country filters, lobby panels, upper/lower frontend rails and Start/Ready
buttons use the same finish. The scenario catalogue now has four chronological
columns and three rows, with a separate paper briefing on the right. All twelve
original Endsieg year pictures are restored at their existing 228x132 size.
Scenario cards now use vanilla's original 232x211 mounts and selected glow;
the pictures are displayed in their native 180x104 apertures. Centered vanilla
headings, the original raised title mount and the native cornered paper frame
are mixed with the Endsieg outer case and brown footer buttons. The paper frame
uses its native 64px corners and tiled interior, preserving its grain.
The selected title and description still come from the
original bookmark. Dates, portraits, flags and input bindings are retained.
Country information and history retain their light paper behind the existing
black typewriter fonts.
Country selection now mixes native portrait/flag mounts and their original
selected glow with the Endsieg outer case and brown filter/footer controls.
The native title mount, filter rail and riveted information, idea and focus
fittings retain their original coordinates. Paper uses the same newspaper grade
as the scenario briefing. Both screens share the vanilla heading font; all
portrait, flag, dropdown and keyboard bindings remain unchanged.
The country window's centering bounds match the full 1225x728 background;
bottom-anchored button offsets retain their original local y675 position.
The preview gallery centers narrower images within the page.
The main and medium rows now use a 1200px field at x12: eight 150px slots fit
with 12/13px outer margins. Italy is a major selection in all four WW1 starts,
between the Entente-side countries and the three Central Powers. Other Countries
remains available in the minor list. WWII groups the four Allied selections on
the left, Other Countries in the middle and the three Axis selections on the
right. All twelve bookmarks disable unplayed-content-first sorting so that this
order remains stable. Existing dates, default selections, country histories,
DLC variants and campaign effects are retained; Italy has four new period
briefings and uses its existing WW1 monarch portrait and national spirits.
The filter strip retains its reversed active/plain frame order. Arrow glyphs,
map-mode icons, checkboxes and the readiness animation mask are unchanged.

## Paper material

Only existing paper receives a restrained grey-white newspaper tint. The update covers 57 original
paper textures plus the scenario and country paper fields: event clipboards,
newsprint, operative dossiers, super-event documents, personnel sheets, unit
and design ledgers, intelligence and operations, research paper, faction
documents, ship histories, graph paper and special-project documents.

The original texture is graded continuously: fibres, mottling and folds retain
their native tonal variation. The earlier flat whitening and thresholded wear
extraction are removed. Existing grey newsprint receives only a small lift.
The source layers retain paper outlines, ink, rules, seals and all alpha channels.
Geometry masks protect neighbouring metal, brown controls, folder
backing and photo apertures. Active selection hatching retains its original
pigment. All 24 operative burn-animation frames keep their native holes and
scorched silhouettes. Fonts, GUI/GFX definitions, event text, pictures, layouts
and gameplay are unchanged by the paper update. Blueprints and bronze plaques
retain their original materials.

## Painted source artwork

The built-in image generation tool produced two blank hardware components:

- `tools/ui_devices/art/housing.png`
- `tools/ui_devices/art/push_key.png`

The exact prompts are in `tools/ui_devices/prompts.json`. These are immutable
authoring masters; they are not loaded by the game. Additional source layers
retain the native country paper fields and the former title lettering, which
is no longer rendered. `endsieg_ui_spec.json` records their hashes, crop bounds,
provenance and original output geometry/alpha masks. The twelve original
scenario picture layers record their source path, hash and original dimensions.
Original paper sources and their geometry/pigment guards are recorded under
`tools/ui_devices/art/paper_sources` and in the specification.
The native bookmark and country-selection fittings are retained as hashed source
layers, with their installed-game texture paths recorded in the specification.

`build_endsieg_ui.py` packs the painted corners, rails and blank faces into the
game's final DDS sizes. It creates state-specific lighting and a restrained
selection rim while retaining the original atlas layout. Source PNGs remain
unchanged. Shipping files use standard BGRA DDS without a DX10-only header.

## Build and validate

Python and Pillow are required:

```powershell
python tools/build_endsieg_ui.py
python tools/build_endsieg_ui.py --validate --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"
```

Validation checks source hashes, all 128 output dimensions, exact alpha masks,
sprite-state separation, deterministic composition, native references and DDS
headers. No game is launched. Paths retain their native case for Linux.

## In-game check

Restart HOI4 to load the skin. Check the main menu, topbar, decisions, research,
construction, production and both imperial stability interfaces at supported
resolutions and UI scales, plus scenario and country selection. Test
country/news/operative events, document ledgers and research paper as well.
Test hover/selection/disabled states and verify the 18px native numbers and 8px
live ratio bars fit their counter windows. Static asset checks do not verify
live rendering or campaign UI behaviour.

## Historical material references

- [Australian War Memorial: Wireless Set No. 19 connector](https://www.awm.gov.au/collection/C1219031)
  documents Bakelite, metal and oxidised copper in wartime communications equipment.
- [Minnesota Historical Society: German military field telephone](https://mnhs.gitlab.io/archive/education-resources/www.mnhs.org/education/resources/german-military-field-telephone.html)
  provides a First World War field-telephone reference.
