> **Superseded (icons):** the user rejected the painted `GFX_iran_focus_*` illustration set. Any recommendation below to use, register or generate those sprites is void; Iran focus icons stay vanilla/DLC-style (see `docs/plans/iran_1910_1945/icon_policy.md`).

# Iran 1910-1945 implementation report

## Status

Implementation is active and substantially complete at the source level.
The maintainer authorized replacing Iran-only focus content with a bespoke era-changing country package based on TFR's structural and visual approach.
Design authority: `docs/specs/iran_1910_1945/iran_1910_1945_spec.md` (accepted) and `docs/specs/iran_1910_1945/addendum_density_routes.md` (route coverage and asset list).

## Delivered content

| Item | Before this session | Now |
| --- | --- | --- |
| Focuses in the era chapters | 81 | 307 (`iran_ww1` 85, `iran_interwar` 129, `iran_ww2` 93) |
| Political settlements with continuation | 3 | 6, each with 8 `allow_branch`-locked focuses per chapter |
| Decisions | 21 | 37 in six categories |
| Events | 19 | 48 |
| National spirits | 6 | 10 including four route institutions |
| Focus icons | 0 custom (all vanilla generics) | 47 custom sprites in one Iran family |
| AI focus plans for the new campaign | none | `IRAN_historical_plan`, `IRAN_alternate_plan` |
| Localisation | 348 keys | 935 keys across five chapter files |

## Chapter routing and state

`iran_initialize_campaign` runs from the `on_startup` hook for PER before 1936 and after, sets authority, foreign leverage and socialist support, and routes to the chapter matching the date.
`iran_campaign_tick` runs from `on_daily_PER` only (no world-iterating hook), calls `iran_route_chapter`, and fires the chapter milestone and the 1941 crisis once each behind flags.
Route choice is stored in country flags, and `iran_refresh_mechanics` maps those flags onto the institution spirit, so a chapter swap never resets the government.

## Route coverage

The full table is in `docs/specs/iran_1910_1945/addendum_density_routes.md`. All nine requested routes are implemented: Qajar constitutional, Qajar restoration, historical Pahlavi, alternative Pahlavi, parliamentary republic, socialist republic (via the Gilan support track), nationalist front, decentralised provincial settlement, and regional ambition.

## Chapter-range decisions

Each settlement is mutually exclusive with the other five, and all of its continuation focuses carry `allow_branch`, so only the chosen branch is drawn after a settlement. The nationalist front is gated behind its own press and officer chain rather than a settlement flag alone.
The socialist settlement requires `iran_socialist_support` at or above 50, built only through the Gilan, Jangali and Soviet-accord chain.

## Assets

47 focus icons were produced for this chapter set and registered in `interface/iran_campaign.gfx` (one sprite per icon, no orphans: every declared sprite has a DDS and every DDS is referenced).
They are 94x86 RGBA DDS written with a valid 124-byte header, generated as four 4x4 painted atlases and cropped per icon; source atlases, processed previews, a contact sheet, the prompts and a per-icon table live in `docs/assets/iran_campaign/`.
The occupation-administration focus reuses the law icon because no dedicated curfew plate was produced.
The four new idea spirits still use vanilla pictures; a dedicated 64x64 idea-icon family is the remaining art gap.

Two tooling findings from that work:
- `mcp__hoi4_image_gptimage__generate_image` failed with `model_not_found` because `.tools/image_generation/providers/gptimage/src/codex.js` defaulted to `gpt-5.5`. The default is now `gpt-6.1-sol`, which this account accepts, and `GPTIMAGE_MODEL` still overrides it.
- The generator returned 1254x1254 plates for a 1024x1024 request; the atlases were resampled once so the 4x4 grid lands on exact 256 px cells.

## Validation performed

- `check_content_refs.py` over the seven script files, six localisation files and the new interface file: brace balance, duplicate ids, localisation coverage for every focus, idea, decision, category, event and option, and icon resolution.
- Coordinate resolution for all three trees: no two focuses in a chapter share a coordinate, and every `relative_position_id` resolves to an id in the same tree.
- Every `prerequisite` and `mutually_exclusive` target exists in its own tree.
- Every effect and trigger key used in the new files was checked against the installed `effects_documentation.md` and `triggers_documentation.md`; `add_consumer_goods_factor` was rejected and replaced with `add_timed_idea`.
- Localisation files checked for BOM, duplicate keys across all Iran files, and stray section-sign or pound characters.

## Corrected defects found during the session

- `stability > 0.70` in the bread-distribution AI weight was an invalid trigger; it is now `has_stability > 0.70` (this was logging a script error at load).
- 11 character availability gates referenced focuses from the retired Persian tree and could never be satisfied; they now accept the equivalent new campaign flag while keeping the old focus check.
- Ahmad Shah's leader expiry of 1925.12.15 would have removed the head of state on a Qajar survival route; it is now 1946.1.1.

## Outstanding

- In-game verification has not been run in this session. Nothing here is engine evidence.
- Idea icons for the four new spirits are generic pictures.
- The legacy `persian_focus_tree` (280 focuses) remains in the repository with its country selector pinned to `always = no`; it is dead weight but preserves foreign references and should be deleted once nothing names its focus ids.
- The 1941 bookmark initialises the Pahlavi state directly, so a player starting there never sees the interwar decisions; this is intended but worth a playtest.
