# Spain 1936-1945 continuation — design addendum and handoff

Companion to `docs/specs/spain_1910_1945/continuation_1936_1945.md` (the spec). This file records how the design was reached, what it deliberately does not do, and what the implementation cards must and must not touch.
Base commit: `21ed2c3de` on `TeknoDev-Branch`. Card `t_9105df3b` (S6). Status: proposal awaiting Director design review; no gameplay credit.

## Decisions taken, and the alternative each rejected

1. **The Nationalist 1939-45 era gets decisions and events, not focuses.** Rejected: a new `SPA_*` band appended to `spanish_focus`. Reasons: the tree is a 281-focus La Resistance inheritance whose `focus_inspect` result is already 175 diagnostics with 16 blocking, ten of its post-war branches are shipped and gated on `scw_over`, and the era's real gaps are a missing 1945 endpoint and an unsettled regime, both of which are decision-shaped. Adding focus count to a 13,428-line file to express a settlement would satisfy nobody but a counter.
2. **The Republican 1939-45 era is repaired in place, not redesigned.** Rejected: replanning the 57-focus tree's layout from scratch. The two blocking diagnostics are two wrong rows plus two knock-on rows; a full re-layout would invalidate every coordinate the S12/S15 work established and would mix a layout change into a content card. The 17 stacked nodes get a stopgap band and a named separate review.
3. **One 1945 settlement serves three routes.** Rejected: a Nationalist settlement, a Crown settlement and a Republican settlement as three chains. `spain_campaign.63` reads `spain_regime_leader` and the faction flags that already exist, and the Crown route reaches it through `spain_monarchy_survived`. One decision, three entry conditions, no duplicated text.
4. **No 1931-36 focus band for a surviving Crown** — declined explicitly rather than deferred silently, as S4's handoff required. The Crown plays the Restoration tree's uncompleted remainder plus the existing civil-war-preparation decisions.
5. **`spain_chapter_republican_postwar` is added to the reconstruction decision tests** even though the reconstruction idea currently covers it. Rejected: leaving the reliance on `spain_civil_war_reconstruction` implicit. `spain_reconstruction_weekly` removes that idea on completion (`spain_campaign_effects.txt:1053-1060`); a later retune that removes it earlier would silently empty the panel on the Republican route only.

## MCP routes executed (read-only)

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.focus_inspect` | `mode: national`, `relativePath: common/national_focus/spain_republic_postwar.txt`, `treeId: spain_republic_postwar_focus` | `validation.passed: false`; 57 focuses; `diagnosticCount: 80`; **2 blocking** `FOCUS_LAYOUT_PARENT_NOT_ABOVE`; 17 `CONNECTOR_THROUGH_NODE`; 1 `CONNECTOR_CROSSING_UNSATISFIED`; layoutMetrics `minimumX: 2`, `maximumX: 34`, `layoutDecisionCount: 57` |
| `hoi4.focus_inspect` | `mode: national`, `treeId: spanish_focus` (file auto-resolved to `common/national_focus/spain.txt`) | 281 focuses; `diagnosticCount: 175`; **16 blocking**; 15 `CONNECTOR_THROUGH_NODE`; 368 connectors |
| `hoi4.focus_render` | `relativePath: common/national_focus/spain_republic_postwar.txt`, `treeId: spain_republic_postwar_focus` | PNG/SVG/HTML/JSON produced (5936×1280, `layoutHash 3b4f79f5…`); same 2 blocking diagnostics. **Picture not reviewed** — no image review was performed in this session |
| `hoi4.source_lookup` | `symbol: spain_enter_postwar_chapter` | one definition, `scripted_effect`, `spain_campaign_effects.txt:240-249`; one call site, `spain_campaign.60` at `events/spain_campaign.txt:422` |
| `hoi4.reference_context` | `surface: focus`, "complete a focus by script for a late bookmark start" | installed `effects_documentation.md:2870` `complete_national_focus` (COUNTRY scope); offline wiki `Effects`; wiki `Country creation:317-326` distinguishes `complete_national_focus` (grants effects) from `unlock_national_focus` (bypasses) — the distinction the catch-up schedule depends on |
| `hoi4.decision_inspect` | not called | known unavailable at adapter 1.19.2.0 vs game 1.19.3.0; recorded, not retried, per the card |

`hoi4.focus_inspect` on `spanish_focus` also emits 16 `FOCUS_TREE_NOT_FOUND` warnings from generating unrelated files; they are build noise, not findings about `spain.txt`.

## Evidence classes

* **Source/static (this session):** every line and symbol cited in the spec was re-read at `21ed2c3de` with `read_file`/`grep`; the postwar tree's id/x/y/prerequisite table was extracted with a brace-aware parser (`.tmp`-class scratch script, not committed).
* **MCP (this session):** the two inspections, the render, one symbol lookup, one reference lookup — as tabulated above.
* **Renderer:** artifacts exist; **no visual review**.
* **Live game:** **not performed.** No launch was authorised or attempted. Every statement about what a player sees is derived from declared coordinates and script, and the spec says so where it matters (§3.2).

## Failure-ledger entries applied

* *Line citations from another session's dirty hunks do not resolve at the recorded commit* — every citation here is from `21ed2c3de` source read directly, not from another card's comment.
* *A designer claim about layout must come from the tool, not from reading coordinates* — the blocking causes were confirmed by `focus_inspect` before being written down, and the 17-node overlap is flagged as declared-coordinate evidence with in-game clickability explicitly unverified.
* *A count in a report can be stale* — S0's R10 ("no explicit tree load" for the Nationalist post-war chapter) is contradicted by `spain_campaign_effects.txt:188` and is recorded as superseded rather than repeated.

## Implementation order suggested to Director

1. **B1** (layout-only, one file, no localisation, `2 blocking → 0`) — smallest change with a hard acceptance test.
2. **A2 + B3** (one scripted-effects edit, both catch-up blocks) — fixes a live schedule defect that affects six bookmarks.
3. **B2** (Hendaye gate + four `available` tests) — two files, no new text.
4. **C1** (`.20` option c, `.27` gateway, 1936 gate) — the first slice that changes what a route can reach.
5. **A1 + C3** (settlement decisions/events, shared) — needs new English localisation and AI weights.
6. **C2** (Crown's 1936 outcomes and the carry-over block).
7. **A3** (post-war AI plan) — last, because it orders focuses the earlier slices assume exist.

Cards 1-3 are independent of 4-7 and of each other's files; cards 4-7 share `common/decisions/spain_campaign.txt`, `events/spain_campaign.txt` and `common/scripted_effects/spain_campaign_effects.txt`, so they must be serialised, not run concurrently.

## Open questions for Director (not blockers to this design)

1. Does the 1931-36 Crown deserve a focus band? S6 declines it; if Director wants it, it is a new card with its own layout review and its own icon decision (existing art only, no new collection).
2. `spain_campaign.17` — wire it into the post-war era as A1's opening scene (its picture and options suit a general-strike crisis, not a settlement) or delete it? S6 leaves it as a recorded orphan rather than repurposing it.
3. The 17 stacked nodes: stopgap band (B1) or full re-layout of the domestic wing in a dedicated card? B1 assumes the stopgap is acceptable for one release.
4. `spain_bop_pending` is set and immediately made inert by `spain_open_postwar_chapter` (`effects:186` vs `:192`). S6 records it as low severity and does not touch it; a one-line removal is available if Director prefers the flag gone.

## What this card did not do

No repository script, localisation, interface, `.gfx`, asset or test write. No vault write (the card reserves none and Director serialises Obsidian writes). No Git commit, no branch or worktree change, no HOI4 launch, no asset replacement, no id rename, no new card.
