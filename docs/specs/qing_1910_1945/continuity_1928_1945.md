# China Continuity 1928–1945: CHI, PRC, Qing, unified Republic and warlord unifiers

Status: design proposal for Director review under card C5 (`t_c019f526`), 2026-10-27.
This is a design contract, not approval, not implementation and not gameplay completion.
It writes no script, no localisation, no `.gfx`, no vault note and no new card.
The only file this card writes is this document.

Evidence classes are marked on every load-bearing claim:

- **[src]** — repository file and line in this checkout.
- **[game]** — the installed Hearts of Iron IV 1.19.3 tree.
- **[wiki]** — the offline snapshot in `paradox_wiki/`.
- **[tool]** — a read-only MCP route run during this card.
- **[plan]** — the master plan in the vault, not verified in the tree.
- **[proposal]** — my design decision, requiring Director acceptance.

Baseline: `TeknoDev-Branch` at `9989c63d9`.
The working tree also contains another lane's uncommitted Iran, Spain and `rch_*` edits; none of that is described here as accepted or mine.

---

## 1. What the checkout actually contains

| Fact | Evidence |
| --- | --- |
| `CHI` exists as a tag with `capital = 605` (Nanjing) and history date blocks at 1910, 1914, 1916, 1918, 1936, 1939, 1941, 1942, 1943, 1944.6.15, 1944.12.1, 1945 and 1946. | **[src]** `history/countries/CHI - China.txt:1`, `:5,106,187,274,398,948,1233,1431,1620,1826,2025,2238,2426` |
| The 1918 `CHI` history block is technology only and its OOB is commented out; it grants no state, no unit and no leader. | **[src]** same file `:274-277` (`#oob = "CHI_1918"`) |
| No state is owned by `CHI` before `1936.1.1`. State 608 Beijing goes QIN → RCH (`1914.1.1`) → CHI (`1936.1.1`); state 613 Shanghai the same; state 592 Guangzhou goes QIN → RCH → GXC in 1936. | **[src]** `history/states/608-Beijing.txt:28-35`, `613-China 12.txt:33-39`, `592-Guangzhou.txt:33-47` |
| 32 state files give `CHI` cores or ownership; the ownership transfers are all dated 1936 or later. | **[src]** count over `history/states`, sampled above |
| `PRC` exists as a tag with `capital = 622` and the same 1910–1945 date-block pattern, and owns nothing before 1936. | **[src]** `history/countries/PRC - ComChina.txt:1`, `:5,104,185,272,413,818,1113,1296,1466,1658,1842,2042` |
| In every shipping bookmark the 1910 map is QIN all China, the 1914/1916/1918 maps are RCH all China, and CHI and PRC are dormant country definitions. | **[src]** state history above; **[plan]** §16 |
| Bookmark/date history blocks run only when the start date is strictly later than the block, so a continuous campaign never applies the `1936.1.1` CHI/warlord transfers. | **[wiki]** `Bookmark modding - Hearts of Iron 4 Wiki.md:163` |
| Pre-1936 startup routes QIN to `qing_initialize_campaign`, RCH to `rch_initialize_campaign`, and every other country to `generic_focus_ww1`. | **[src]** `common/on_actions/endsieg_on_actions.txt:221-235` |
| The same generic sweep later gives `generic_focus_ww1` to any country not in its exclusion list, which names Chinese tags only as QIN and RCH. | **[src]** same file `:1449-1455` |
| The 1936+ startup dispatcher gives CHI, PRC, RNG and thirteen warlord tags their DLC trees, and `generic_focus` to everything else. QIN and RCH have **no branch** in it. | **[src]** same file `:250-572` |
| DLC ladders are NCNS → WTT → generic, already written for CHI (`china_nationalist_sea_focus` / `china_nationalist_focus`) and PRC (`china_communist_focus_sea` / `china_communist_focus`). | **[src]** same file `:510-536` |
| A second, narrow DLC loader exists for the continuous handover: `rch_load_handover_tree`, guarded by `has_focus_tree` and branching NCNS → WTT → generic. | **[src]** `common/scripted_effects/rch_campaign.txt:269-296` |
| The continuous handover itself is `rch_route_chapter` → `rch_settle_1936` → `CHI = { change_tag_from = ROOT }`, or the RCH branch when `rch_republic_saved` is set. | **[src]** `common/scripted_effects/rch_campaign.txt:144-155`, `:239-263` |
| `change_tag_from` moves the player to the scoped country; the scoped country must be the destination, and nothing happens if the target is AI-controlled. It does not transfer states. | **[wiki]** `Effects - Hearts of Iron 4 Wiki.md:912` |
| Therefore the existing handover moves a human player onto the country object `CHI`, which owns no states and has no army in continuous play, and leaves the state-holding RCH under AI. The defect P3 is confirmed by the wiki, not by a launch. | **[src]** above plus **[wiki]** `:912` |
| The five global China symbols do not exist: `china_seat_holder`, `china_reunified_by`, `china_warlord_national`, `china_fragmentation_tier`, `china_proper_states`. | **[tool]** `hoi4.source_lookup` on the first three: `definitionCount = 0` each; **[src]** symbol sweep, zero files; Director admission comment, 2026-10-27 |
| Nothing that would carry a unified line exists at tag level either: the Republic's line is a country flag pair produced by the C3 succession (`rch_line_unified` …), and the Qing's outcome is carried by `qing_regime_settled` plus `qing_settlement_partition` / `qing_settlement_reunion`. | **[src]** `common/scripted_effects/rch_campaign.txt:616-645`; `common/scripted_effects/qing_campaign.txt:477,496,520` |
| The Qing's own chapter clock reaches its war chapter at the 1936 boundary and loads `qing_ww2`, so a surviving Qing in continuous play is already served without the 1936+ dispatcher. | **[src]** `common/scripted_effects/qing_campaign.txt:185-211`; `common/on_actions/qing_campaign.txt:3-5` |
| The Republic's chapter clock stops being authoritative at 1936 because `rch_route_chapter` then only runs the settlement and the handover tree, and RCH has no 1936+ chapter tree. | **[src]** `common/scripted_effects/rch_campaign.txt:239-263` |
| NCNS start-up arrays are built once, at `on_startup`, in the vanilla-derived on_action: `CHI.core_and_claimed_states`, `CHI.mtac_core_states`, `CHI.nine_power_treaty_signatories`, `global.is_chinese_warlord`, three `press_warlord_*` costs, `YUN.political_power_warlord_integration_cost` and `JAP.JAP_strategic_offensives_targets_array`. | **[src]** `common/on_actions/14_sea_on_actions.txt:3-108` |
| That on_action runs at every start, including 1910, so those arrays are built against the wrong map and are never rebuilt when a campaign later reaches 1936. | **[src]** same file; **[plan]** P5 |
| `rch_nanjing` is 45 focuses, 42 columns, 0 too-close same-row pairs, 0 crossings, 2 long connectors, and the tool reports no blocking diagnostic. | **[tool]** `hoi4.focus_inspect rch_nanjing`, revision `5cd3feaafe8df4aa`, `validation.passed = true` |
| `qing_ww2` is 65 focuses, 43 columns, 1 crossing, 8 long connectors, `validation.passed = true`. | **[tool]** `hoi4.focus_inspect qing_ww2`, revision `76459893b556e3b4` |
| `china_nationalist_sea_focus` is 275 focuses, 148 columns, 34 crossings, 16 node intersections, and the tool reports 30 blocking diagnostics, `validation.passed = false`. | **[tool]** `hoi4.focus_inspect china_nationalist_sea_focus`, same revision |
| The 1936+ dispatcher's `every_country` loop requires an owned capital, so dormant tags are skipped; this is the existing guard against initialising CHI or PRC on a 1910 map. | **[src]** `endsieg_on_actions.txt:252-256` |

---

## 2. Decisions

Each decision is written as a decision, not as quoted plan prose.
Where the master plan and this checkout disagree, the checkout wins.

### D1 — `CHI` enters as the Nanjing seat in 1928, not as a Canton government in 1917

The Nationalist tag becomes the state-holding country at the 1928 seat transfer, not by a 1917 spawn.

- **Rejected: the master-plan 1917 spawn.** **[plan]** §7.1/§11.1 would put CHI in Guangzhou from September 1917 with `chi_canton` and `chi_expedition` trees.
  It requires a state handover from RCH before 1928, a new 60-focus tree, an 86-focus second tree, a rewritten 1918 bookmark map and a second national claimant before the seat model exists.
  None of `chi_canton`, `chi_expedition` or `chi_nanjing` exists in this checkout. **[src]** `common/national_focus` listing: only `china_*`, `rch_*`, `qing_*`.
- **Accepted: the Canton and expedition fantasy stays inside the Republic for 1917–1928.** The KMT route already exists as `rch_route_kmt`, and the expedition marker `rch_northern_expedition` is already set for a Republic initialised after 1927. **[src]** `common/scripted_effects/rch_campaign.txt:83-85`, `common/scripted_triggers/rch_campaign.txt:82-88`.
  The Canton government, Chen Jiongming's break, Whampoa and the Northern Expedition become the content of the `rch_warlord` KMT branch, which already carries the `RC2_kmt_settlement` route focus. **[src]** `common/national_focus/rch_warlord.txt:169-175`.
- **Rejected: `change_tag` on the live RCH object.** There is no `change_tag` precedent in the mod or in the vanilla tree, and no wiki entry for it; an unprecedented tag-swap onto an existing dormant country object is not a design I will specify. **[src]** grep over `common/` and `events/`; **[wiki]** `Effects` table has no `change_tag` row.
- **Accepted handover mechanism:** transfer the states to CHI first, then move the player, then dispose of RCH (section 4.1). This uses only `transfer_state`, `change_tag_from` and `annex`, all precedented in this checkout. **[src]** `events/WWI - Chinese Collection Events.txt:71,451,473,494,762`; `common/scripted_effects/rch_campaign.txt:153`.
- **Consequence:** vanilla `original_tag = CHI` systems work from mid-1928 onward, which is what P4 needs, without an 11-year second government.

### D2 — `PRC` enters as the Chinese Soviet Republic in 1931, and only when it can be given a tree

- **Founding and spawning are separate.** The 1927 Nanchang rupture sets a movement flag on the Republic or the Qing, not a tag.
  The tag spawns in the Jiangxi Soviet on the `1931.11.7` anchor, from the state owner that controls the chosen base states. **[plan]** §3 P6, §11.2.
- **The spawn requires `prc_soviet`.** With no tree, a spawned PRC would fall through the generic sweep to `generic_focus_ww1`, which is exactly P11. **[src]** `endsieg_on_actions.txt:1449-1455`.
  Therefore PRC does not spawn until `prc_soviet` exists; the flag stays set on the parent and the spawn is the first content of that tree's owning card.
  A half entry (tag with generic tree) is refused.
- **Historical line only at first.** On the unified and Qing lines the communist movement stays a political condition inside the existing tag until a later design says otherwise. **[plan]** §11.2 rows 2–3.
- **Vanilla from the 1936 floor.** `china_communist_focus_sea` / `china_communist_focus` are the continuous trees, loaded by the same single loader as CHI (D9).

### D3 — Reunification and the seat are consumed from one global model, never re-implemented here

- `china_seat_holder`, `china_reunified_by`, `china_proper_states` and `china_fragmentation_tier` do not exist. **[tool]** `definitionCount = 0`.
- This design **specifies** that model (section 5) and **consumes** it.
  It writes no parallel flag, no second array and no country-scoped substitute for any of the four, and it does not re-open C4's deferred seat bid.
- Until C1 creates the model, no continuity effect may test or set it; the historical line resolves entirely through existing country flags and the tag handover, and the alternate unifier paths stay unshipped.
  This is a gate, not a fallback: shipping a country-scoped `china_reunified_by` lookalike would be the second state model the Director forbade.

### D4 — The Northern Expedition is a Republic campaign with three named outcomes

| Outcome | Condition (design) | Map and tag result | Continuity carrier |
| --- | --- | --- | --- |
| Nanjing seat (historical) | Expedition objectives met by mid-1928 and the Beiyang government loses Beijing | RCH transfers the seat states to CHI; CHI holds Nanjing from June 1928; RCH survives only as a northern rump or is annexed | `rch_northern_expedition` + `rch_line_garrison`; new `china_chi_handover_done` |
| Beiyang holds the north | The seat holder keeps Beijing and the expedition stalls | RCH keeps the seat; no CHI; RCH continues on `rch_beiyang_restored` | `rch_line_garrison`, `rch_path_beiyang` |
| Wuhan left government | The 1927 split resolves to the left | RCH keeps the seat but takes the left KMT branch; PRC may stay legal | `rch_path_kmt` plus a split-outcome flag on RCH |

- **The expedition is not a new campaign system.** It reuses the C4-era limited-war architecture and the existing `rch_northern_expedition` marker. **[src]** `common/scripted_triggers/rch_campaign.txt:82-88`; **[plan]** §9.5.
- **Seat transfer is not a reward screen.** Its payoffs are the seat states and the CHI tree; there is no political-power or equipment dump on transfer. The C3 lesson (a card cannot pay twice for being bought) is applied to the transfer. **[src]** `docs/specs/qing_1910_1945/republic_succession.md:34`.

### D5 — Surviving Qing continuity works and is protected from the 1936+ dispatcher

- In continuous play the Qing needs nothing new: `qing_campaign_tick` reaches chapter three and loads `qing_ww2`. **[src]** `common/scripted_effects/qing_campaign.txt:185-211`.
- At a 1936+ **start** the Qing holds no states in any shipping bookmark, so the dispatcher's `any_owned_state` guard skips it and no wrong tree is loaded. **[src]** `endsieg_on_actions.txt:252-256`; **[src]** `docs/specs/qing_1910_1945/qing_1910_1945_spec.md:84`.
- **New requirement, returned to the dispatcher owner:** if a later bookmark ever gives QIN states at 1936+, the 1936+ dispatcher has no QIN branch and would give it `generic_focus`. The branch must be added before such a bookmark ships. This is diagnostic D1, not fixed here.
- Qing wartime branches stay behind `qing_ww2`'s existing route locks; this design adds no branch, icon or focus id.

### D6 — A unified Republic stays `RCH` and never borrows vanilla CHI content

- On `rch_line_unified`, RCH never runs the 1928 seat handover and never enters the vanilla loader.
  The unified line needs its own `rch_unified_1936` tree (master plan U3). **[plan]** §8.4.
- **Rejected: renaming the unified Republic to CHI in 1936 to inherit vanilla content.** It would discard the unified line's identity, its route flags and its whole pre-1936 record, and it would make the 1936 map identical to the historical one.
- **Consequence, stated plainly:** vanilla NCNS Chinese mechanics gate on `original_tag = CHI`. A unified RCH does not get them.
  It may use only `china_shared` focuses that survive an effect audit, as the plan already allows. **[plan]** §8.4, §13.2.
  This is a content gap, not a bug, and it belongs in the unified line's own card.

### D7 — Warlord unifiers are defined by role, and the national tree is a hard prerequisite

- Historical warlords hand over unchanged to the vanilla trees in 1936; this design adds nothing to that path and must not, because the NCNS warlord tree already carries 30 blocking diagnostics of its own class in the Nationalist tree and the warlord tree is measured at 202. **[tool]** `china_warlord_sea_focus` measured on C4 (`validation.passed = false`); **[src]** `docs/specs/qing_1910_1945/warlord_identity_paths.md:121`.
- A warlord that wins the national seat needs `china_warlord_national`. It does not exist. **[tool]** `definitionCount = 0`.
- C4 slice 1 (Shanxi release, bands S1/S2) and slice 2 (band S3 identity, no seat bid) are already fixed and are respected; this design adds no seat-bid content. Director admission, 2026-10-27.
- The continuity contract for a warlord unifier is therefore: role flag + seat from the global model + `china_warlord_national` + the four-part integration lane. Until all four exist, the unifier path is deferred, exactly as C4 deferred it.

### D8 — Bookmark and continuous initialisation are two different mechanisms, each used once

| Start kind | What initialises | What must never happen |
| --- | --- | --- |
| Bookmark 1910/1914/1916/1918 | Country and state history date blocks, then `on_startup` pre-1936 branch (`qing_initialize_campaign` / `rch_initialize_campaign`) | No handover effect, no CHI/PRC spawn, no vanilla loader |
| Bookmark 1936 and later | Vanilla/Endsieg history blocks, then the 1936+ dispatcher (DLC ladder per tag) | No campaign initialiser for a tag that owns no states; no second tree load |
| Continuous campaign crossing 1928 / 1931 / 1936 | Effect-driven handover at the era boundary, guarded by a permanent flag | No reliance on a date block, and no second initialiser on a reload |

- The rule is the wiki's: date blocks run only for a later start date. **[wiki]** `Bookmark modding:163`.
- Every initialiser is idempotent: a permanent flag, a `has_focus_tree` test and a variable/array presence test.
  A reload, a second daily tick and a save reload must all be no-ops.

### D9 — One vanilla tree loader, called once per country

- `rch_load_handover_tree` is the correct ladder and is reused as the single loader, renamed to `china_load_vanilla_tree` when the C1/C9 owner moves it into shared script.
  It branches NCNS → WTT → generic and is guarded by `has_focus_tree`. **[src]** `common/scripted_effects/rch_campaign.txt:269-296`.
- **Rule:** no other effect, event or decision may call `load_focus_tree` for a vanilla Chinese tree.
  The 1936+ dispatcher keeps its own branches for bookmark starts because it is the only thing that runs there; when both could run, `has_focus_tree` plus the loader's own flag make the second call a no-op.
- **Rule:** the loader is per country, not per tag. A tag change during play does not re-run it; the country that received the tree keeps it.

### D10 — The NCNS bootstrap runs once, and only for continuous campaigns

- The five arrays and the warlord cost variables are built at `on_startup` against whatever map the campaign starts on. **[src]** `14_sea_on_actions.txt:3-108`.
- A 1936+ start therefore needs no bootstrap; a continuous campaign that reaches 1936 needs all of it rebuilt.
- **Guard:** `china_vanilla_bootstrap` requires `has_global_flag = china_continuous_campaign`, set by the pre-1936 initialiser of whichever Chinese tag the campaign began as, and by nothing else.
  It clears each array before rebuilding it, sets `has_global_flag = china_vanilla_bootstrapped`, and refuses to run again.
- **It is not a vanilla edit.** It is an Endsieg effect that repeats the vanilla logic. **[plan]** §14.7.
- The full list is fixed by C9 from the vanilla file, the CHI/PRC/warlord/Manchu history files and the NCNS effects; this design fixes only the guard, the order and the once-only rule.

### D11 — Japanese pressure and the wartime phase are consumed, not invented

- Phase, line and fragmentation tier belong to the global model (section 5). This design adds no phase variable.
- Interim continuity for the historical line keys on war state and date floors only: a Chinese government at war with JAP, or the `1937.7.6` floor, is in the resistance band.
  The 1938 ceiling in the plan is a global-model rule and is not implemented here. **[plan]** §14.1.
- Japanese-side content (M8) stays out of this design. The plan's open question 5 is decided in section 7.

### D12 — 1945 is the end of the line, and the 1945 bookmark is vanilla's

- The 1945.3.20 bookmark loads through the 1936+ dispatcher (`date > 1935.12.31`), so CHI and the vanilla warlords get their DLC trees and the vanilla 1945 history blocks apply. **[src]** `endsieg_on_actions.txt:250-256`; bookmark date read from `common/bookmarks` (`1945.3.20.1`).
- No Endsieg wartime tree is added for CHI in this design; CHI's 1936–1945 content is vanilla NCNS/WTT.
- Alternate tags (surviving Qing, unified or Beiyang Republic) at a 1945 **start** cannot occur through a shipping bookmark; through a save they keep whatever tree the campaign already loaded. That is acceptable because the chapter clocks are continuous, not start-driven.

---

## 3. Continuation table: what runs in 1928–1945

This is the row set the eventual router must satisfy; it deliberately keeps the C4 boundaries.

| Role / line | 1928–1931 | 1931–1936 | 1936–1945 | Initialiser |
| --- | --- | --- | --- | --- |
| RCH historical, KMT route | `rch_nanjing` → seat handover to CHI in Jun 1928 | — (CHI) | — | `china_handover_to_chi` (D1) |
| RCH historical, Beiyang route | `rch_beiyang_restored` (required) | same | `rch_beiyang_war` (required) | existing RCH tick |
| RCH unified | `rch_warlord` then `rch_unified_1925` (required) | `rch_unified_1925` | `rch_unified_1936` (required), vanilla `china_shared` after audit | existing RCH tick |
| RCH southern republic (Qing partition) | `rch_unified_1916` → `1925` | same | `rch_unified_1936` | existing RCH tick |
| CHI (Nationalist) | `chi_nanjing` (retarget of `rch_nanjing`, ids preserved) | same | vanilla NCNS/WTT | `china_handover_to_chi`, then `china_load_vanilla_tree` |
| PRC | — | `prc_soviet` (required) from the 1931 spawn | vanilla NCNS/WTT | `china_spawn_prc`, then the loader |
| QIN, any outcome | `qing_interwar` / `qing_restoration` per C4 | same | `qing_ww2` | existing Qing tick |
| Warlord (historical) | `china_warlord_nanjing` (C6/C7) | same | vanilla warlord tree | 1936+ dispatcher or existing C6 router |
| Warlord unifier | `china_warlord_national` (required) | same | vanilla or Endsieg wartime content after audit | seat transfer + global model |

"Required" marks a tree that does not exist in this checkout and is returned to Director in section 8.
No row here creates a tag, an icon or a focus id.

---

## 4. Handover contracts

These are implementation contracts for the card that builds them; no script is written here.

### 4.1 `china_handover_to_chi` — the 1928 Nanjing seat

**Scope:** country scope, called on RCH.

**Preconditions:** `original_tag = RCH`; `rch_campaign_active`; `date > 1928.6.7`; `rch_path_kmt = yes`; `rch_line_garrison = yes` or `rch_line_contested = yes`; `controls_state = 608` is **not** required for the handover, because the historical seat move happens after Beijing falls; `NOT = { has_country_flag = china_chi_handover_done }`; `country_exists = CHI` is false.

**Steps, in this order:**

1. Set `china_chi_handover_done` first, so no later step can re-enter.
2. Move the capital to 605 before any state transfer, so the destination has a capital when it gains states.
3. For every state RCH owns that `is_core_of = CHI`, add the core to CHI if missing, then `transfer_state = CHI`; keep controllers consistent.
4. Copy the continuity state CHI's trees read: `rch_legitimacy`, `rch_military_influence`, `rch_nationalist_support`, `rch_succession_tier`, `rch_path_*`, `rch_line_*`, `rch_1936_settled` semantics translated by name, not by value.
   The copy is explicit and one-way; no variable is read through both tags afterwards.
5. Recruit the CHI leadership roster that the 1928 state has (not the 1936 roster), guarded by `NOT = { has_character = … }`.
6. Move the human player with `CHI = { change_tag_from = ROOT }` **only after** CHI owns the states and has a capital. For AI RCH, do the same transfer without the player move.
7. Dispose of RCH per D4: keep it as a northern rump on the Beiyang route, otherwise `annex` it into CHI.
8. Call `china_load_vanilla_tree` on CHI only if the date is at or past the 1936 floor; in 1928 CHI takes `chi_nanjing` instead.
9. Clear `rch_campaign_active` on the RCH remnant and set `china_chi_handover_done` on both countries so neither tick retries.

**Postconditions:** CHI owns Nanjing, has a capital and an army, holds the continuity variables, and RCH either exists as a rump with its own tree or is gone.
**Anti-repeat:** the flag is set before step 2 and never cleared.
**Falsifiers:** two live countries with tag CHI; a player on a stateless country; a second handover after reload; an AI RCH moved into CHI while the player watches.

### 4.2 `china_spawn_prc` — the 1931 Soviet base

**Preconditions:** `prc_soviet` exists (hard), date past the 1931 anchor, a chosen base state list held by one Chinese government, `NOT = { country_exists = PRC }`, `NOT = { has_global_flag = china_prc_spawned }`.
**Steps:** set the global flag; transfer the base states with cores; recruit the leadership roster; set the movement flags the tree reads; load `prc_soviet`; queue one event.
**Anti-repeat:** the global flag is permanent.
**Refusal:** if `prc_soviet` is missing, the effect must not run at all. A tag on a generic tree is worse than no tag.

### 4.3 `china_load_vanilla_tree` — one loader

Reuse `rch_load_handover_tree` unchanged in behaviour: NCNS → WTT → generic, guarded by `has_focus_tree`, plus a country flag `china_vanilla_tree_loaded`.
Called from: the 1928 handover when the date is past 1936, the PRC spawn, the 1936+ dispatcher for bookmark starts, and nowhere else.

### 4.4 `china_vanilla_bootstrap` — arrays once

**Preconditions:** `has_global_flag = china_continuous_campaign`; `date > 1935.12.31`; `NOT = { has_global_flag = china_vanilla_bootstrapped }`.
**Order:** clear each array, rebuild from the current map, then set the done flag.
**Arrays and variables:** every symbol listed in section 1's NCNS row, plus anything C9 extracts that this design has not seen.
**Out of scope:** JAP-side arrays that require editing a Japanese file are C9's, with the approval the plan already reserves. **[plan]** §15.

---

## 5. The global state model this design requires

Returned to Director as a requirement, not created here.

| Symbol | Scope | Kind | Written by | Read by | Lifetime |
| --- | --- | --- | --- | --- | --- |
| `china_seat_holder` | global | country variable | seat transfer effects (C1/C7) | every continuity initialiser | permanent, replaced on each transfer |
| `china_reunified_by` | global | country variable | the reunification test (C1) | every post-unification row | permanent, first reunifier only |
| `china_proper_states` | global | state array | one `on_startup` build (C1) | the reunification test | once per campaign |
| `china_fragmentation_tier` | global | variable 0–3 | the C3 succession, published not recomputed | warlord creation and continuity | permanent after the crisis |
| `china_warlord_national` | — | focus tree id | C7 content | warlord unifier row | — |

Rules this design imposes on that model:

- One writer per symbol; readers never write.
- The tier is published by the succession that already resolves it, not recalculated by continuity. **[src]** `republic_succession.md:53-56`.
- `china_reunified_by` is set once and never cleared; a second reunifier is refused.
- `china_proper_states` is built once and is not rebuilt by the bootstrap, because it describes China proper, not ownership.

---

## 6. Acceptance scenarios

No launch is authorised. These are the scenarios the implementation and QA must construct, with the dependency that makes each one pass.

| # | Scenario | Expected | Dependency | Falsifier |
| --- | --- | --- | --- | --- |
| A1 | 1936.1.1 bookmark, CHI | `china_nationalist_sea_focus`, NCNS arrays populated by vanilla `on_startup`, 1936 history army and states, no Endsieg effect runs | none (works today) | generic tree; empty arrays; missing OOB |
| A2 | 1936.1.1 bookmark, PRC | `china_communist_focus_sea`, vanilla 1936 states | none (works today) | generic tree |
| A3 | 1936.1.1 bookmark, warlord (SHX) | `china_warlord_sea_focus` | none (works today); C4 slice 1 must not alter it | Endsieg band tree at a 1936 start |
| A4 | 1936.1.1 bookmark, QIN or RCH | Tag owns no state, so no tree load; no error | D5/D6; D1 diagnostic | a wrong tree loaded on a dormant tag |
| A5 | 1937.7.1 continuous from 1910, historical | CHI at war with JAP on the vanilla tree, arrays rebuilt, PRC spawned with `prc_soviet` | D1, D2, D9, D10; C8 trees | player stateless; empty arrays; PRC on generic tree |
| A6 | 1937.7.1 continuous, unified RCH | `rch_unified_1936`, no vanilla CHI content, at war with JAP | D6; `rch_unified_1936` required | RCH silently converted to CHI |
| A7 | 1937.7.1 continuous, surviving Qing (consolidated) | `qing_ww2` on its route branch, at war with JAP | none new (C4 owns it) | `generic_focus` |
| A8 | 1945.3.20 bookmark, CHI | Vanilla 1945 tree and history; no Endsieg handover | none (works today) | Endsieg wartime tree; missing 1945 OOB |
| A9 | Reload of A5 at 1937 | No second handover, no second bootstrap, no duplicated tree load, no duplicate leader | D8/D9/D10 guards | second CHI transfer, duplicated characters |
| A10 | Alternate warlord unifier | Blocked until the global model and `china_warlord_national` exist | D3/D7 | any invented seat flag |

---

## 7. Master-plan open questions, decided

| # | Question | Decision | Why |
| --- | --- | --- | --- |
| 1 | Guominjun: XIC cosmetic or a fourth tag | **XIC cosmetic tag** for 1924–1930, and the Northeast Army conversion to XIC stays as history has it | No new tag, no new colour, no new flag art; the 1936 XIC capital is in the northwest as the plan notes. Binds C4 slice 9 when it is admitted; nothing is implemented here |
| 2 | Hongxian Empire: cosmetic RCH or a new tag | **Cosmetic tag of RCH** | The C3 contract already carries `rch_hongxian` as a flag, not a country; a separate tag would duplicate the seat |
| 3 | Southern republic after a Qing partition: RCH or CHI | **RCH** | Matches the accepted C2 boundary that RCH holds the south; CHI does not exist before 1928 in this design |
| 4 | Achievement set | **Deferred, out of scope** | Needs user approval and art; forbidden by this card |
| 5 | May M8 touch `INT_japan` / `JAP_ww1_focus` | **China-side only for now** | This card may not authorise Japanese-file edits; Japanese hooks stay C9 with the plan's reserved approval |
| 6 | Playable pre-1936 Tibet and Mongolia | **Out of scope** | They are reassertion targets only; making them playable needs their own design and trees |

---

## 8. Requirements returned to Director

No new tag, icon, focus id or global symbol is created by this design; each of these is a requirement for the named owner.

1. **C1:** the global state model of section 5, in `common/script_constants/china_story.txt` and one routing file, with the one-writer rule.
2. **C1/C9:** the 1936+ dispatcher gains QIN and RCH branches before any bookmark gives them states at 1936+ (D1 diagnostic), and the generic sweep at `endsieg_on_actions.txt:1449-1455` learns `is_chinese_campaign_country` so dynamically created Chinese tags do not get `generic_focus_ww1`.
3. **C8:** `chi_nanjing` as the `rch_nanjing` retarget with focus ids and localisation keys preserved (45 focuses, measured clean), `prc_soviet`, and — deferred — `chi_canton` / `chi_expedition`.
4. **C8:** `china_handover_to_chi` and `china_spawn_prc` as section 4, plus their entries in `docs/endsieg_dynamic_effects.md`.
5. **C7:** `china_warlord_national`; no seat bid before the global model.
6. **C9:** `china_vanilla_bootstrap` with the exact extracted array list; the `china_load_vanilla_tree` move to shared script; the 30 blocking diagnostics on `china_nationalist_sea_focus` (measured) are pre-existing and C9's, not this card's.
7. **Localisation owner:** one key per new handover event, option, decision and flag tooltip, in the eight shipped languages; Milestone 1 is English-only for new content, so the other seven are the localisation owner's pass.
8. **AI owner:** a handover-scenario plan and the historical-AI weights for D4's three outcomes.

---

## 9. Validation

### Run on this card

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.source_lookup` | `china_seat_holder` | 0 definitions, 0 references, workspace revision `d66851e1…` |
| `hoi4.source_lookup` | `china_reunified_by` | 0 definitions, 0 references |
| `hoi4.source_lookup` | `china_warlord_national` | 0 definitions, 0 references |
| `hoi4.focus_inspect` | `rch_nanjing` | 45 focuses, 42 columns, 0 too-close pairs, 0 crossings, 2 long connectors, `validation.passed = true` |
| `hoi4.focus_inspect` | `qing_ww2` | 65 focuses, 43 columns, 1 crossing, 8 long connectors, `validation.passed = true` |
| `hoi4.focus_inspect` | `china_nationalist_sea_focus` | 275 focuses, 148 columns, 34 crossings, 16 node intersections, 30 blocking diagnostics, `validation.passed = false` |

The three `focus_inspect` runs also emitted a repeated `FOCUS_TREE_NOT_FOUND` warning against unrelated files in the inline inventory.
That is a tool inventory artefact, not a finding about these trees: each run resolved the requested tree and its source path, and the per-tree validation line is the one used above.

### Not run, and why

- No game launch, no save, no AI campaign and no panel render: none is authorised, and live playtesting is the user's.
- No `focus_render`: the trees inspected are existing ones and the card changes no layout.
- No localisation audit: this card writes no localisation.
- No engine proof of `change_tag_from` behaviour: the wiki semantics are quoted, and the first implementation card must prove the handover in a user run.

---

## 10. Anti-repeat and exploit guards

| Risk | Guard |
| --- | --- |
| Handover runs twice, or after a reload | `china_chi_handover_done` set before the first transfer |
| Player left on a stateless CHI | States and capital move before `change_tag_from`; contract step 2 and 6 |
| Second bootstrap on a reload | `china_vanilla_bootstrapped` global flag |
| Bootstrap in a 1936 bookmark | Requires `china_continuous_campaign`, set only by a pre-1936 initialiser |
| Vanilla tree loaded twice | `has_focus_tree` plus `china_vanilla_tree_loaded` per country |
| PRC spawned without content | Effect refuses when `prc_soviet` is absent |
| Reunification paid twice | `china_reunified_by` set once; every payoff behind a permanent flag |
| Warlord seat bid before the model exists | C4 deferral kept; no seat content in this design |
| Cross-tree `has_completed_focus` | Continuity is flags and variables only; the existing loader already uses `keep_completed` |
| Leader recruited twice | Every recruit guarded by `NOT = { has_character = … }` |

---

## 11. Diagnostics raised, outside this card's ownership

- **D1.** The 1936+ startup dispatcher has no QIN or RCH branch, so any future bookmark that gives those tags states at 1936+ would send them to `generic_focus` instead of `qing_ww2` or an RCH 1936 tree. **[src]** `endsieg_on_actions.txt:250-572`.
- **D2.** The existing continuous handover moves the human player to `CHI` before CHI owns any state, leaving the state-holding country under AI. Confirmed from the wiki's `change_tag_from` semantics; P3 in the plan is therefore a real defect, not a stale claim. **[src]** `rch_campaign.txt:144-155`; **[wiki]** `Effects:912`.
- **D3.** `china_nationalist_sea_focus` carries 30 blocking focus diagnostics and 16 node intersections at 275 focuses; C9 inherits a tree that the tool already refuses. **[tool]** `focus_inspect`.
- **D4.** The generic WWI sweep excludes only QIN and RCH among Chinese tags, so any dynamically created Chinese tag before 1936 receives `generic_focus_ww1`. **[src]** `endsieg_on_actions.txt:1449-1455`.
- **D5.** The 1936+ dispatch and the continuous handover implement the same DLC ladder twice, in two files, with different guards. They must be unified by C9 or they will drift.

---

## 12. What this design refuses to do

1. No code, no localisation, no `.gfx`, no vault note, no card.
2. No new tag: not `ZHL`, `ANH`, `FNG`, and not a Hongxian tag.
3. No 1917 `chi_canton` spawn, and no claim that `chi_canton`, `chi_expedition`, `prc_soviet`, `chi_nanjing`, `rch_unified_*`, `rch_beiyang_*` or `china_warlord_national` exist.
4. No second China state model, and no country-scoped substitute for the four missing globals.
5. No artwork change and no new icon collection.
6. No edits to Japanese files.
7. No 1936+ content for the alternate tags beyond what their own chapter clocks already carry.
8. No claim of playability. Nothing here has been launched, saved or observed.

---

## Director acceptance notes (added 2026-10-27 by `endsieg`, integration)

Accepted as a design contract, not as implementation and not as gameplay.
The twelve decisions, the section 4 handover contracts, the section 5 model requirement and the section 6 scenarios stand as the binding specification for the cards that build them.
The text above is the designer's and is preserved verbatim; only this appendix is Director-authored.

**Checks the Director re-ran against the checkout at `9989c63d9`.** `CHI` capital is 605. The 1918 block's OOB is commented out. State 608 moves QIN → RCH on `1914.1.1` and to CHI on `1936.1.1`; state 592 goes to GXC on `1936.1.1`. Across the 40 state files that mention CHI there are **zero** pre-1936 `owner`/`controller` occurrences, and the earliest dated CHI block in 23 of them is 1936. `change_tag` appears nowhere in `common/` or `events/` (0 occurrences), so D1's rejection of a live tag swap holds. `rch_route_kmt` and `rch_northern_expedition` are set together at `common/scripted_effects/rch_campaign.txt:83-84`. `rch_settle_1936` still moves the player with `CHI = { change_tag_from = ROOT }` and transfers no state. `rch_load_handover_tree` is still the NCNS → WTT → generic ladder at `:269-296`. The 1936+ dispatcher still guards on `any_owned_state = { is_capital = yes }` and the generic sweep at `:1449-1455` still excludes only QIN and RCH among Chinese tags. `RC2_kmt_settlement` exists at `common/national_focus/rch_warlord.txt:169`. All five global symbols and all seven "required" trees listed in section 3 still resolve to zero files.

**Correction 1, section 1 evidence row.** "32 state files give `CHI` cores or ownership" conflates two different numbers. 32 files give CHI **ownership**; 62 files carry a root-level `add_core_of = CHI` that is outside any date block, so CHI already holds cores on 62 states from the first day of any bookmark, including 1910. The consequence is favourable and is recorded so no implementer re-derives it: section 4.1 step 3's add-core is defensive, not load-bearing, and `CHI.core_and_claimed_states` is non-empty at `on_startup` even in a 1910 campaign.

**Correction 2, section 8 labels.** The owner labels `C1`, `C7`, `C8` and `C9` in section 8 are master-plan sections, not native board cards with those identifiers. Native `C1`, `C7`, `C8`/`C8a` are done and carry unrelated scope, and native `C9` is the Republic pressure package in QA. No native card inherits a requirement from this list; a future implementation card states its own native id and its own exact ownership.

**What this acceptance does not authorise.** No implementation card, no script, no localisation, no asset, no commit of gameplay and no admission ahead of the still-missing global China state model of section 5. The C4 deferral of the seat bid stands, and the unifier rows stay deferred until the model and `china_warlord_national` exist. D2's defect is confirmed from source and the wiki's `change_tag_from` semantics, not from a launch: no campaign, save, render or panel was observed for any part of this design.
