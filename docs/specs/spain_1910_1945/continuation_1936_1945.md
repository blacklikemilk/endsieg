# Spain 1936-1945 — continuation design (Nationalist, Republican, surviving Crown)

Status: **proposal**, not approval. Written for Director design review under card `t_9105df3b` (S6).
Base: `TeknoDev-Branch` `21ed2c3de`, read with `git show`-clean source, working tree dirty with other sessions' Iran/Qing edits that were not read as evidence.
Every claim below cites a path and a symbol or line from that commit.
No gameplay, localisation, interface, `.gfx` or asset file is written by this card; the slices are for later implementation cards.

## 1. What the era already is

The campaign is a sequence of chapter flags, each owning one focus tree (`common/scripted_effects/spain_campaign_effects.txt:86-93` clears every sibling so exactly one is live).

| Chapter | Flag | Tree | Entry | Writers |
| --- | --- | --- | --- | --- |
| Restoration | `spain_chapter_restoration` | `spain_restoration_focus` (77 focuses) | `spain_open_restoration_chapter` (`:95-111`), bookmark before 1923.9.13 (`:21-24`) | `.16` a is *not* it; only `spain_open_restoration_chapter` |
| Directory | `spain_chapter_rivera` | `spain_rivera_focus` (64) | `spain_open_rivera_chapter` (`:113-131`), bookmark 1923.9.13-1931.4.13 | `.10` option that calls `spain_enter_rivera_chapter` (`:225-228`) |
| Republic | `spain_chapter_republic` | `spain_republic_focus` (76) | `spain_open_republic_chapter` (`:133-152`) | `.16` a (`events/spain_campaign.txt:145`), `.20` a and b (`:173`, `:188`) |
| Civil war | `spain_chapter_civil_war` | `spanish_focus` (281, La Resistance) | `spain_enter_civil_war_chapter` (`:235-238`) | `.25` single option (`events/spain_campaign.txt:237-240`) |
| Nationalist post-war | `spain_chapter_postwar` | `spanish_focus`, reloaded (`:188`) | `spain_open_postwar_chapter` (`:184-201`) | `spain_enter_postwar_chapter` else-arm (`:245-247`); `.60` (`events:420-423`) |
| Republican post-war | `spain_chapter_republican_postwar` | `spain_republic_postwar_focus` (57) | `spain_open_republican_postwar_chapter` (`:203-218`) | `spain_enter_postwar_chapter` democratic/communist arm (`:241-244`) |

`spain_enter_postwar_chapter` (`:240-249`) is the only gate between the war chapter and the two post-war chapters, and it decides by **government type only**: `has_government = democratic` or `communism` sends the country to the Republican tree, everything else to `spanish_focus`.
That single test is the origin of two of the defects in §3.

## 2. Route states at 1936, and who owns 1936-1945 today

### A. Nationalist victory — `spain_chapter_postwar`

Owned already, need not be rebuilt:

* `spanish_focus`'s post-war branches, all gated on `has_global_flag = scw_over`: `SPA_the_national_syndicalist_state` (`common/national_focus/spain.txt:1617`), `SPA_the_national_and_popular_army_of_spain` (`:2627`), `SPA_join_the_axis` (`:2921`), `SPA_national_recovery` (`:3383`), `SPA_the_iberian_pact` (`:4112`), `SPA_the_latin_bloc` (`:4144`), `SPA_fuse_the_parties` (`:4251`), `SPA_join_the_allies` (`:4316`), `SPA_settle_the_succession_question` (`:6605`), `SPA_prosperity_of_the_empire` (`:6801`).
* The faction struggle: `spain_refresh_faction_leadership` (`effects:885-943`, post-war tension `+10` at `:898`), `spain_faction_resolve_regime` (`:947-984`), crisis event `spain_campaign.50` (`events:376-407`), panel `SPR_nationalist_factions` (`common/decisions/categories/spain_campaign_categories.txt:69-87`, visible post-war with `fascism`/`neutrality`).
* Wartime diplomacy: `SPR_wartime_diplomacy` category (`categories:89-98`, `spain_post_civil_war` + date > 1939.3.31) and its decisions `SPR_negotiate_with_germany`, `SPR_negotiate_with_britain`, `SPR_wolfram_exports`, `SPR_the_blue_division`, `SPR_close_the_pyrenees`, `SPR_declare_armed_neutrality`, `SPR_accept_the_marshall_aid`, `SPR_take_the_un_seat` (`common/decisions/spain_campaign.txt:579-740`).
* Reconstruction: `SPR_reconstruction` category (`categories:113-122`) with `SPR_rebuild_the_railways`, `SPR_restore_the_industry`, `SPR_housing_programme`, `SPR_veterans_pension` (`decisions:741-822`), driven by `spain_reconstruction_weekly` (`effects:1043-1062`).
* Hendaye: `spain_campaign.71` (`events:582-612`) fired from `spain_chapter_events` at `effects:379-387`.

What is actually missing on this route:

1. No 1945 endpoint. The Republican tree closes on `SPR4_the_pact_of_1945` / `SPR4_the_1945_settlement` / `SPR4_a_place_in_europe` (`spain_republic_postwar.txt`), the Nationalist route simply stops firing content after `SPR_take_the_un_seat` becomes unavailable.
2. The post-war regime is never settled. `spain_faction_resolve_regime` writes a spirit and stops (`effects:947-984`); no decision or event turns the winning faction into a constitutional outcome, a succession answer or a 1945 diplomatic position.
3. `spain_campaign.17` is defined, localised and fired by nothing (`events:471-497`; the only occurrences in `common/` and `events/` are its own definition).

### B. Republican victory — `spain_chapter_republican_postwar`

Owned already: the 57-focus tree `spain_republic_postwar_focus` (`common/national_focus/spain_republic_postwar.txt:12-36`; country gate `original_tag = SPR`, `date > 1939.3.31`, `democratic`/`communism`), the chamber re-initialised by the opener (`effects:209-210`), `SPR_wartime_diplomacy` and `SPR_reconstruction` (visible on `spain_post_civil_war`, `triggers:31-36`), `spain_campaign.61` (`events:426-438`).
The tree already reads real systems: seat swings with recounts at `:110-111`, `:127-128`, `:144-146`, `:161-162`, `:408-411`, `:458-460`, `:477-478`; army loyalty at `:46`, `:377`, `:644`, `:893`; coup pressure at `:273-274`, `:444`; leverage at `:375-377`, `:595`, `:893`; `spain_reconstruction_advanced` at `:659` and `:941`.

Missing, and it is structural rather than cosmetic:

1. Two **blocking** layout diagnostics (§3.1) and a block of 17 focuses that declare near-identical coordinates (§3.2).
2. No Hendaye: `spain_chapter_events` gates `.71` on `has_country_flag = spain_chapter_postwar` (`effects:381`), so the Republican chapter never receives the war's central diplomatic scene, although its tree has `SPR4_gibraltar_question` and `SPR4_wolfram_trade`.
3. No catch-up: `spain_restore_past_focuses`'s post-war block is gated on `spain_chapter_postwar` but completes `SPR4_*` ids (`effects:1289-1330`), which belong to the *other* chapter's tree.

### C. Restoration or Directory carried forward — no chapter exists

Today this route is **unreachable**, not merely thin:

* `.16` option b sets `spain_monarchy_endures` and nothing else (`events:150-156`); the flag is read nowhere.
* `.20` has two options and both call `spain_enter_republic_chapter` (`events:170-193`); there is no third door.
* The 1936 transition tests only `spain_in_republic_chapter` (`effects:327-335`), so a chapter that is not the Republic never fires `.25`.
* The 1939 transition already lists the Restoration (`effects:339-354`, `:344`), and `.60` then routes by government: a surviving constitutional monarchy is `democratic` and would therefore be loaded into the **Republican** post-war tree (`effects:241-247`).

S4 (`t_119dabe4`, accepted) decided the shape of the missing door — `.20` option c re-entering the Restoration with `spain_monarchy_survived`, and the 1936 gate extended to fire `.25` from the Restoration. None of it is in the source at `21ed2c3de`. S6 owns the continuation, so §6 turns that contract into slices and declines the one piece S4 left open (1931-36 focus content).

## 3. Repair items that block any honest continuation

### 3.1 The two blocking diagnostics on `spain_republic_postwar_focus`

`hoi4.focus_inspect` (`mode: national`, `relativePath: common/national_focus/spain_republic_postwar.txt`, `treeId: spain_republic_postwar_focus`) returns `validation.passed: false`, `diagnosticCount: 80`, message `2 blocking focus diagnostics`. Both are `FOCUS_LAYOUT_PARENT_NOT_ABOVE`, and both are fixed-coordinate mistakes:

| Focus | Declared | Prerequisite | Prerequisite declared | Why it blocks |
| --- | --- | --- | --- | --- |
| `SPR4_the_merchant_fleet` (`spain_republic_postwar.txt:484-496`) | `x = 30 y = 1` | `SPR4_rebuild_the_industry` (`:199-213`) | `x = 14 y = 1` | parent and child are on the **same row**; the connector cannot go down |
| `SPR4_volunteer_question` (`:526-540`) | `x = 32 y = 2` | `SPR4_the_air_force` (`:511-525`) | `x = 30 y = 3` | parent is **one row below** the child |

Neither is a content problem: the prerequisite graph is acyclic and the rewards resolve. Both are the column `x = 30…34` having been built upwards while the tree grows downwards elsewhere. The same block produces 17 `FOCUS_LAYOUT_CONNECTOR_THROUGH_NODE` warnings and one `FOCUS_LAYOUT_CONNECTOR_CROSSING_UNSATISFIED` (`SPR4_rebuild_the_industry → SPR4_reconstruction_complete` crossing `SPR4_the_hydroelectric_grid → SPR4_railway_restoration`).

### 3.2 Seventeen focuses declare the same coordinates

`SPR4_rationing_ends`, `SPR4_black_market`, `SPR4_hospital_programme`, `SPR4_orphanages`, `SPR4_exile_amnesty`, `SPR4_officer_oath`, `SPR4_army_cuts`, `SPR4_tank_corps`, `SPR4_aircraft_licence`, `SPR4_catalan_industry`, `SPR4_basque_steel`, `SPR4_galician_wolfram`, `SPR4_blue_division_myth`, `SPR4_gibraltar_negotiation`, `SPR4_marshall_plan`, `SPR4_exiles_return_wave`, `SPR4_the_pact_of_1945` all declare `x = -2…4, y = 1…2`, with the pair `(0, 1)` repeated five times and `(0, 2)` repeated three times.
The inspector's layout **normalises** them (`layoutDecisionCount: 57`, `layoutMetrics.bounds.minimumX: 2`), which is why its `tooCloseSameRowPairCount` is 0 and why this does not appear as a blocking diagnostic. The game reads `x`/`y` literally, so on screen those seventeen nodes sit on top of each other and the player sees one of them. Treat in-game clickability as **unverified** — no launch was authorised — but the declared coordinates are unambiguous in source.

### 3.3 Catch-up schedule inverted

`spain_restore_past_focuses` (`effects:1069-1332`) is a date-gated `complete_national_focus` schedule for bookmarks. Its post-war block:

```text
if = { limit = { has_country_flag = spain_chapter_postwar }   # :1290
    ... complete_national_focus = SPR4_the_republic_endures ... # :1293-1329
```

`SPR4_*` ids live only in `spain_republic_postwar_focus`, which the Nationalist chapter does not load (`effects:188` loads `spanish_focus`). So on the 1941, 1942, 1943, 1944, 1944.11 and 1945 bookmarks — all Nationalist starts — the schedule asks the engine to complete focuses that are not in the loaded tree, and the Republican chapter (`spain_chapter_republican_postwar`) has no block at all. Two consequences: the intended catch-up never happens on either post-war route, and every post-war bookmark start exercises a `complete_national_focus` call for an id outside the current tree.

### 3.4 Republican chapter excluded from Hendaye and from two category tests

* `spain_chapter_events` fires `.71` only for `spain_chapter_postwar` (`effects:381`).
* `SPR_reconstruction` decisions test `OR = { has_idea = spain_civil_war_reconstruction has_country_flag = spain_chapter_postwar }` (`decisions:745`, `:766`, `:787`, `:804`). The Republican opener adds the idea (`effects:214`), so the branch survives today; it survives only because of that idea, and the flag itself is never in the test.

### 3.5 Stale claims to correct, not repeat

* S0's R10 ("the Nationalist post-war chapter has no explicit tree load") no longer holds: `spain_open_postwar_chapter` loads `spanish_focus` at `effects:188`.
* `spain_open_postwar_chapter` still sets `spain_bop_pending` (`effects:186`) although it deletes the balance four lines later (`:192`). `spain_campaign_bootstrap` only runs from `spain_focus_restore_pending` (`:271-274`), which no post-war opener sets, so the flag is inert today — but it is a live trap for any later chapter that reuses the pending flag. Low severity, exact lines recorded.
* `spain_campaign.17` remains dead (§2.A.3).

## 4. Route A slices — Nationalist victory

Bounded at three. No new focuses: the era is already owned by ten shipped branches and four decision categories, and adding focus count here would be inflation.

### A1 — "The Settlement of 1945" (decisions + events only)

Panel: `SPR_nationalist_factions` (`categories:69-87`) — the player acts from the Nationalist faction category he already uses. Its four live decisions already gate on `OR = { has_country_flag = spain_factions_opened has_country_flag = spain_chapter_postwar }` (`decisions:495`, `:510`, `:525`, `:540`), so the category is not empty in 1939-45 and A1 adds to a working panel rather than opening a dead one.

* New decision `SPR_the_succession_question` in `common/decisions/spain_campaign.txt` inside `SPR_nationalist_factions` (`:491`): `cost = 50`, `available = { spain_in_postwar_chapter = yes date > 1945.1.1 NOT = { has_country_flag = spain_succession_settled } }`, `complete_effect` fires `spain_campaign.62`.
* New decision `SPR_the_pact_of_1945`: `cost = 75`, `fire_only_once = yes`, `available = { spain_in_postwar_chapter = yes date > 1945.1.1 OR = { has_country_flag = spain_succession_settled has_country_flag = spain_monarchy_survived } }`, `complete_effect` fires `spain_campaign.63`.
* `spain_campaign.62` (new, id free): three options selected by the *existing* faction flags — `spain_falange_leads` / `spain_army_leads` / `spain_monarchists_lead` (`triggers:103-106`), each with `ai_chance` and each setting one outcome flag plus one existing spirit: `spain_falangist_state`, `spain_military_directorate`, `spain_monarchist_state` (`effects:947-984`). Options differ in what they cost and grant: stability and war support for the Falangist continuation, army loyalty and `spain_coup_pressure` relief for the Directory, allied leverage and Carlist tension for the monarchist answer.
* `spain_campaign.63` (new): the settlement itself. Sets `spain_settled_1945`, writes `spain_regime_leader` (`effects:953-977`), grants the matching 1945 spirit and shifts leverage so that `SPR_take_the_un_seat` (`decisions`, `:150-175` region) and `SPR_accept_the_marshall_aid` become reachable or not. That is the payoff: the settlement decides which of the existing 1945 decisions the country can still take, not how many focuses it owns.

Readers created by A1 must be named in the same slice: `spain_succession_settled`, `spain_settled_1945`, `spain_monarchy_recalled` (added to nothing else; each is read by the decision `available` blocks above so no flag is write-only).

### A2 — Post-war catch-up, Nationalist half

In `spain_restore_past_focuses` (`effects:1069-1332`), the `spain_chapter_postwar` block becomes a Nationalist list and the `SPR4_*` list moves to `spain_chapter_republican_postwar` (§5.3). Nationalist completions by date, all existing ids: `SPA_the_national_syndicalist_state`, `SPA_the_national_and_popular_army_of_spain`, `SPA_national_recovery` at 1940.6.1; `SPA_join_the_axis` **or** `SPA_join_the_allies` cannot both be completed — the schedule must branch on the government's alignment idea (`spain_axis_alignment` / `spain_allied_alignment`, `effects:995-1003`) and complete the one that matches, leaving the other to the player; `SPA_the_iberian_pact` at 1943.1.1; `SPA_settle_the_succession_question` at 1945.6.1.

### A3 — AI and English localisation

* New AI plan `SPR_postwar_plan` in `common/ai_strategy_plans/SPR_chapter_plans.txt` (file has one plan per chapter, each `enable`d on its flag and `abort`ed on the next): `enable = { is_historical_focus_on = yes has_country_flag = spain_chapter_postwar }`, `ai_national_focuses` drawn from the post-war branches above in a plausible order. Without it, historical AI on a 1939+ start keeps picking pre-war branches.
* `ai_will_do` on both decisions (`base = 25` for the succession, `base = 20` for the pact) and `ai_chance` per `.62`/`.63` option, weighted by the faction that leads.
* English keys in `localisation/english/spain_campaign_l_english.yml`: `SPR_the_succession_question`, `SPR_the_succession_question_desc`, `SPR_the_pact_of_1945`, `SPR_the_pact_of_1945_desc`, `spain_campaign.62.t/.d/.a/.b/.c`, `spain_campaign.63.t/.d/.a/.b/.c`, `spain_settled_1945_tt`. Player text describes the settlement, never the system.

## 5. Route B slices — Republican victory

### B1 — Layout repair (no content change)

Minimum, exactly two changed rows, enough to clear both blocking diagnostics:

| Focus | From | To | Check |
| --- | --- | --- | --- |
| `SPR4_the_merchant_fleet` | `x = 30 y = 1` (`:488`) | `x = 30 y = 2` | parent `SPR4_rebuild_the_industry` at `(14, 1)` is now above |
| `SPR4_volunteer_question` | `x = 32 y = 2` (`:530`) | `x = 32 y = 4` | parent `SPR4_the_air_force` at `(30, 3)` is now above |

Two knock-on moves are mandatory in the same edit or the repair creates new faults: `SPR4_coal_and_steel` `(30, 2)` → `(30, 3)` (its parent moved onto its old row) and `SPR4_wolfram_trade` `(32, 3)` → `(32, 5)` (its parent moved onto its old row). `SPR4_the_un_question` `(30, 5)` stays; `SPR4_gibraltar_question` `(30, 4)` stays and its child `SPR4_pyrenees_defences` `(34, 5)` stays.
Acceptance for B1: `hoi4.focus_inspect` returns `2 blocking` → `0 blocking`, and no new `CONNECTOR_THROUGH_NODE` for the moved nodes.

B1 also carries the stopgap for §3.2: move the seventeen stacked focuses out of the `x = -2…4, y = 1…2` block into a dedicated band below the tree (rows `y = 10…13`, two columns apart), which is legal because every one of their parents sits at `y ≤ 9`. A proper re-layout of that wing is **not** part of B1 — it is a separate layout review card, and B1 must not touch icons or rewards.

### B2 — Hendaye and category parity

* `spain_chapter_events`: change the `.71` gate from `has_country_flag = spain_chapter_postwar` (`effects:381`) to `spain_post_civil_war = yes` (`triggers:31-36`) so both post-war chapters get Hendaye. `.71`'s options already write only leverage, opinion and stability (`events:589-611`), which the Republican tree reads (`SPR4_gibraltar_question`, `:555-…`; `SPR4_wolfram_trade`, `:541-554`).
* Add `has_country_flag = spain_chapter_republican_postwar` to the four `SPR_reconstruction` `available` tests (`decisions:743`, `:764`, `:787`, `:808`) so the panel survives if the reconstruction idea is ever removed later than `spain_reconstruction_weekly` expects (`effects:1053-1060`).

### B3 — Catch-up parity

The `SPR4_*` list currently under `spain_chapter_postwar` (`effects:1289-1330`) moves to `if = { limit = { has_country_flag = spain_chapter_republican_postwar } }`, and additionally completes `SPR4_political_police` and `SPR4_the_church_settlement` at 1941.1.1 so a 1941+ Republican start does not open on a tree whose first two rows are empty.

## 6. Route C slices — the Crown that survives

Three slices, all decisions/events; no new focuses (see C2's explicit decline).

### C1 — The missing door out of 1931

* `.20` gains option c (`events:163-194`): `ai_chance = { base = 15 }`, `spain_open_restoration_chapter = yes`, `set_country_flag = spain_monarchy_survived`, `add_stability = constant:spain_campaign.stability_cost`, `add_to_variable = { var = spain_military_loyalty value = constant:spain_campaign.loyalty_gain_small }`. This is S4's contract, unchanged.
* `spain_campaign_transition_check` 1936 branch (`effects:327-335`) gains a Restoration arm: `OR = { spain_in_republic_chapter = yes AND = { spain_in_restoration_chapter = yes has_country_flag = spain_monarchy_survived } }`, firing `spain_campaign.27` instead of `.25` for the monarchy.
* `.16` option b's dead flag (`events:155`) either feeds `spain_monarchy_survived` or is removed; leaving a written-but-unread flag is not acceptable in the same file that gains its reader.

### C2 — 1936 for a Crown, and the explicit decline

`spain_campaign.27` (new, id free) is the monarchy's 1936 gateway, one option per outcome:

* **a. The rising comes**: `spain_enter_civil_war_chapter = yes`, keeps `spain_monarchy_survived`, and `spain_carry_over_choices` gains a Restoration block (`effects:1391-1473` is the Rivera-from-Restoration block; a sibling gated `has_country_flag = spain_chapter_civil_war` + `spain_monarchy_survived` sets `spain_legacy_crown_survived`, `+5` loyalty and `-10` to `spain_nationalist_tension_carried`) so the Crown fights the rising as the legitimate government.
* **b. The Crown pre-empts it**: costs political power, uses the existing `spain_coup_pressure` and `spain_military_loyalty` meters — if `spain_coup_risk` (`triggers:48-53`) is true the rising happens anyway and option b resolves as a failed pre-emption (`spain_loyalty_loss`, `add_to_variable spain_coup_pressure constant:spain_campaign.coup_gain`). If the coup is not yet at the floor, the rising is deferred: `spain_chapter_restoration` continues, the 1936 event is re-armed once in 1937.

**Declined, explicitly:** no 1931-36 focus band for a surviving Crown. The Restoration tree's 77 focuses are 1910-23 content (`spain_restoration_focus`), a surviving monarchy plays its uncompleted remainder plus `SPR_civil_war_preparation` (`decisions:824-917`, visible `date > 1931.1.1`, `categories:100-111`) and the Crown/Cortes panel. If Director judges that too thin, a dedicated 1931-36 band is a separate design card with its own layout review; it must not be smuggled into C1 and it must not reuse the 1910-23 icon set unexamined.

### C3 — 1939-1945 for a Crown

* `spain_enter_postwar_chapter` (`effects:240-249`) gains a monarchy arm **before** the government test: `if = { limit = { has_country_flag = spain_monarchy_survived } spain_open_postwar_chapter = yes }`. Without it a democratic Crown is loaded into `spain_republic_postwar_focus` (the branch at `:241-244` cannot tell a constitutional monarch from a republic).
* The 1945 settlement is A1's, shared: `SPR_the_pact_of_1945`'s `available` already accepts `spain_monarchy_survived` (§4.A1), and `spain_campaign.63` resolves the Crown's answer into `spain_monarchy_recalled` or a regency, writing the same `spain_regime_leader` and spirit set. One decision, three routes, one settlement — this is why A1 and C3 are not two designs.
* The post-war opener initialises the chamber (`effects:191`), so the settlement can be put to the Cortes through the existing bill machinery (`common/scripted_effects/spain_cortes_bills.txt:1-22`) rather than a popup alone.

## 7. Ownership map and what is protected

| Slice | Files | Owner class |
| --- | --- | --- |
| A1, A3 | `common/decisions/spain_campaign.txt` (`SPR_nationalist_factions`), `events/spain_campaign.txt` (new `.62`, `.63`), `common/ai_strategy_plans/SPR_chapter_plans.txt`, `localisation/english/spain_campaign_l_english.yml` | implementation card, shared with C1/C3 (same files) |
| A2, B3 | `common/scripted_effects/spain_campaign_effects.txt` (`spain_restore_past_focuses`, `:1289-1330`) | implementation card |
| B1 | `common/national_focus/spain_republic_postwar.txt` (coordinates only) | implementation card, layout-only |
| B2, C1, C3 | `common/scripted_effects/spain_campaign_effects.txt` (`:240-249`, `:327-335`, `:1391-1473`), `events/spain_campaign.txt` (`.20`, `.27`), `common/decisions/spain_campaign.txt` (`:745`, `:766`, `:787`, `:804`) | implementation card |

Retained untouched, by decision: every existing focus id, icon, reward and localisation key in `spanish_focus`, `spain_restoration_focus`, `spain_rivera_focus`, `spain_republic_focus` and `spain_republic_postwar_focus`; the La Resistance civil-war layer (`common/decisions/SPR.txt`, `events/LAR_Spain.txt`, `common/ideas/spain_nationalist.txt`, `common/ideas/spain_republic.txt`); the balance `SPR_crown_and_cortes` and its five ranges.

Layout reviews kept separate (criterion 3): `spanish_focus` reports 175 diagnostics / 16 blocking from `focus_inspect`, almost all inherited vanilla fixed-coordinate habits in a 281-focus tree — out of scope here and must not be "fixed" inside a continuation card. `spain_republic_postwar_focus`'s 23 warnings and the 17 stacked nodes are B1's stopgap plus one dedicated review.

## 8. Validation the implementation card must run

Source/static: `source_lookup` on every new symbol, `script_validate` on each new effect/decision block, grep for every new flag's readers in `common/` and `events/`, and a brace/parse pass over each edited file.
Renderer: `focus_inspect` on `spain_republic_postwar_focus` and `focus_render` after B1, expecting `2 blocking → 0`; `focus_render` after C1 only if a focus is added (it is not).
Localisation: keys present in all eight language folders per the project rule; B1, A1 and C1 all ship English text in the same change as their script.
Not performed by this card and not claimed: any in-game launch, clickability of the 17 stacked nodes, the AI actually choosing the new decisions, and the visual look of the repaired right column.

## Director ruling after the approved S19 diagnostic, 2026-10-27

Disposition: accepted clarification of A1's existing matching-answer contract within Christopher's approved Spain campaign, for linked DeepSeek correction after diagnostic `t_e83880e2` run 227.
The diagnostic and native original `t_08b44a33` remain the evidence for the two rejected attempts, not implementation acceptance.
The shared `spain_faction_resolve_regime` remains the only writer of the regime leader and its spirit.

### Succession answers establish their named regime

Existing threshold flags remain eligibility, so several answers can be offered when several factions qualify.
The Directory remains available when no civilian faction qualifies, and the player always has an answer.
An eligible selected answer must establish a strict numerical winner before the unchanged shared resolver runs exactly once.
The Crown answer represents either royal house, including the Carlists, and selects the house with greater current influence, retaining the monarchist preference when the two houses tie.
The generic `spain_succession_monarchist` flag records that Crown answer rather than an exclusive Alfonsine claimant.

The selected faction advances above the largest current faction influence by the existing `faction_gain_large` margin, bounded by the existing `faction_cap`.
Only rivals whose influence would tie or exceed that bounded result are lowered to the selected result minus the same existing margin.
This cap-safe rebalance is authorized within the three succession answers and must be explained by their visible tooltips.
It preserves a decisive answer after ordinary upkeep without exceeding the campaign cap or altering the shared resolver, constants, upkeep or AI weights.
All other option payloads remain as specified.

### The subsequent pact recognizes the current balance

The Crown-recall option in `.63.c` keeps its existing route prerequisites and additionally requires a royal house to be the current strict numerical winner under the shared resolver's actual comparisons.
A remembered royal succession alone cannot recall the Crown after a later non-royal takeover.
The pact does not apply another decisive faction rebalance.
Its own-terms option stays available, so a changed balance never traps the settlement popup.
The existing leverage consequences, three settlement options, costs, once-only guards and registered icons remain intact.

### Required correction proof

Execute real option effects and the real shared resolver from coherent numerical states rather than a copied arbitration function.
Reproduce the Crown tie `F45/C25/M35/A20` and no-lead Directory `F29/C15/M10/A5` before correction, then verify matching answer flag, leader and exactly one spirit afterwards.
Cover every eligible answer, both royal houses, royal ties, values at zero and the lead threshold, competing maxima, the cap, stale flags, each old spirit and all four old spirits together.
Run actual clamp/upkeep semantics after the answer and check both unchanged and deliberately changed balance before the pact.
A `.63.c` guard-deletion mutant must expose the false recall, and fixed-push, wrong-house and spirit-removal mutants must fail coupled checks.
Retain the original eight Spain regressions and mandatory independent DeepSeek QA with the canonical `s19-crown-answer-spirit-mismatch` history at two rejections.

The rejected alternatives were fixed positive pushes that do not guarantee the named regime, an uncapped maximum-plus-margin that loses its victory at upkeep, direct local spirit overrides, and changing the shared resolver owned by S18b.
None satisfies the existing matching-answer promise as safely within the four-path correction.
This ruling does not accept S19, authorize another premium attempt or authorize a game launch.
