# Shanxi slice 2: the Nanjing decade band (S21 / t_2db9e517)

Handoff for the card `S21 | China: the Nanjing decade band for Shanxi (S3 identity, slice 2)`.
Workspace `C:/Users/Christopher/Documents/Paradox Interactive/Hearts of Iron IV/mod/endsieg`, branch TeknoDev-Branch, base commit `10d7c6b7d`.
No commit was made: Director integrates after independent QA.

## What was built

`SHX` now has a third band between the clique wars and the vanilla 1936 warlord tree.
The band is the Nanjing decade: submission to a government the province does not obey, a provincial autonomy statute, the 1930 northern coalition that the province joins and loses, and Japanese economic penetration of the north.
It runs on the same `warlord_cohesion` meter and the same four tier spirits as slices 1 and 2, and it retires itself in the 1936 handover exactly as the two earlier bands do.

## Routing table (verified in the shipped source)

| Date | Band flag set | SHX tree |
| --- | --- | --- |
| 1916.6.5 or earlier | none | none (the province is not released) |
| 1916.6.6 | `shx_band_rise` | `shx_rise` |
| 1920.7.13 | `shx_band_rise` | `shx_rise` |
| 1920.7.14 | `shx_band_wars` | `shx_wars` |
| 1927.12.31 | `shx_band_wars` | `shx_wars` |
| 1928.1.1 | `shx_band_nanjing` | `shx_nanjing` |
| 1935.12.31 | `shx_band_nanjing` | `shx_nanjing` |
| 1936.1.1 | none (`shx_handover_complete`) | the dispatcher's DLC order: `china_warlord_sea_focus`, else `china_warlord_focus`, else `generic_focus` |

Boundary behaviour: the tick tests the handover first, then rise, then wars, then the decade, so exactly one branch runs per pass.
Each opener sets its own flag and clears the other two. A later tick in the same band only re-loads when `NOT = { has_focus_tree = ... }`, so a second pass on the same day performs no load.

## Changed paths

New:

- `common/national_focus/shx_nanjing.txt` (201 lines, 10 focuses, tree id `shx_nanjing`)
- `.tools/tests/test_shx_nanjing.py` (1654 checks, four named mutants)
- this file

Edited (append or additive only):

- `common/scripted_effects/shx_campaign.txt`: band-3 split at 40-73 (`else` became `else_if = { limit = { date < 1928.1.1 } }` plus a new `else`), `shx_band_nanjing` cleared in the wars branch at 48, `shx_band_nanjing` cleared in the handover at 88, `shx_open_nanjing` at 124-130, `shx_nanjing_demand` at 207-213, and one comment line added to the file header at 7-8. Every slice-1 body is intact.
- `common/scripted_triggers/shx_campaign.txt`: the Nanjing section at 76-107 (`@squeeze_maturity_days`, `shx_nanjing_squeeze_due`, `shx_cohesion_tier_three`, `shx_charter_open`, `shx_coalition_open`). The six slice-1 triggers, `@patron_maturity_days` and `@demand_maturity_days` are untouched, and `shx_can_declare_clique_war` is byte-identical.
- `common/script_constants/shx_campaign.txt`: keys 73-104 only, under `shx_story`. Every pre-existing key keeps its value and still has a reader.
- `common/decisions/shx_campaign.txt`: three cost macros at 11-13 (`@charter_cost` 60, `@coalition_cost` 80, `@buyback_cost` 75) and the `shx_nanjing_government` category block at 297-366 with `shx_enact_the_statute`, `shx_join_the_coalition` and `shx_buy_back_the_concession`.
- `common/decisions/categories/shx_campaign.txt`: `shx_nanjing_government` at 12, visible on `shx_band_nanjing` and hidden after `shx_handover_complete`.
- `common/ideas/shx_campaign.txt`: one spirit, `shx_japanese_concession` at 55-66. The four cohesion spirits are untouched.
- `events/shx_campaign.txt`: `shx_campaign.4` at 102 and `shx_campaign.5` at 127. `.1`-`.3` untouched, one `add_namespace`.
- `common/ai_strategy_plans/SHX_warlord.txt`: `SHX_nanjing_plan` at 53-75, enabled by `shx_band_nanjing`, aborted without the tree.
- `localisation/english/shx_focus_l_english.yml` (+25 keys), `shx_campaign_l_english.yml` (+14 keys), `shx_campaign_events_l_english.yml` (+8 keys). UTF-8 with BOM, `key: "text"`, no `:0`, no leading space, no `§` or `£`.
- `.tools/tests/test_shx_warlord.py`: 18 insertions, 6 deletions, all listed under residuals below.
- `docs/systems/shx_campaign.md`: third band, its panels, its readers, its interactions, two new Dynamic effects entries, updated AI, assets, future slices and limitations.
- `docs/endsieg_dynamic_effects.md`: `shx_open_nanjing` and `shx_nanjing_demand` appended in the file's shape, and the `shx_hand_over_to_vanilla` entry now says it clears all three band flags.

## New ids, flags, constants and keys

- Tree: `shx_nanjing`.
- Focuses: `SHX_answers_nanjing`, `SHX_nominal_submission`, `SHX_real_submission`, `SHX_autonomy_statute`, `SHX_the_charter`, `SHX_nanjing_command`, `SHX_northern_arsenal`, `SHX_the_squeeze`, `SHX_garrison_reform`, `SHX_the_decade_closes`. Shortcuts: `shx_nanjing_submission_navigation`, `shx_nanjing_statute_navigation`, `shx_nanjing_arsenal_navigation`.
- Effects: `shx_open_nanjing`, `shx_nanjing_demand`.
- Triggers: `shx_nanjing_squeeze_due`, `shx_cohesion_tier_three`, `shx_charter_open`, `shx_coalition_open`.
- Flags: `shx_band_nanjing`, `shx_autonomy_charter`, `shx_nanjing_squeeze_seen`, `shx_concession_granted`, `shx_coalition_lost`. Every one has a reader (census in the suite).
- Decisions: `shx_enact_the_statute`, `shx_join_the_coalition`, `shx_buy_back_the_concession`, category `shx_nanjing_government`.
- Idea: `shx_japanese_concession`.
- Events: `shx_campaign.4` (two options), `shx_campaign.5` (report).
- Constants (`shx_story`): `cohesion_gain_submission`, `cohesion_gain_statute`, `cohesion_gain_charter`, `cohesion_loss_real_submission`, `cohesion_loss_garrison`, `cohesion_gain_squeeze`, `cohesion_gain_garrison`, `cohesion_gain_statute_enacted`, `cohesion_loss_coalition`, `cohesion_gain_concession`, `cohesion_loss_refusal`, `cohesion_gain_buyback`, `coalition_stability_cost`, `ai_nanjing_political`, `ai_nanjing_settlement`, `ai_nanjing_command`, `ai_nanjing_charter`, `ai_nanjing_coalition`, `ai_nanjing_concession`, `ai_nanjing_refusal`, `ai_nanjing_buyback`.
- Macro: `@squeeze_maturity_days = 120` in the triggers file, because `has_country_flag = { days > }` rejects a constant.

## Acceptance criteria

1. Third band, loaded once: `shx_open_nanjing` at effects:124 has the slice-1 shape, the tick guards it with the band flag, and the routing table above is asserted at all four boundaries. `scenario_one_tree` proves no second load in the same day and `scenario_handover` proves the 1936 handover clears all three band flags and loads the dispatcher's tree.
2. The band's fantasy: ten focuses covering answer, submission fork, statute, charter, arsenal, command, squeeze, garrison and capstone. Each pays a visible change (political power, army experience, equipment, infrastructure, a building slot and factory, or cohesion) and each has a prerequisite. `hoi4.focus_inspect` reports 12 connectors, 0 crossings, 0 node intersections, 0 long connectors.
3. Charter hand-forward: `shx_autonomy_charter` is written only by `shx_enact_the_statute`, never cleared, and read by `shx_coalition_open` (triggers:101-106) and by the `SHX_the_charter` reward (tree:108-112).
4. Coalition as defeat: one decision, `fire_only_once = yes`, gated on `shx_coalition_open` (band, charter, no war, tier three), 80 political power, 18 cohesion, 4 percent stability, sets `shx_coalition_lost`, fires `shx_campaign.5`, grants no state, no seat, no core and no war goal. No `china_seat_holder`, `china_reunified_by` or `china_warlord_national` appears anywhere.
5. Cohesion gates and no farming: two of the three new rows are gated by `shx_cohesion_tier_three`; every new focus, decision and event option reads an `ai_nanjing_*` or existing `constant:shx_story.*` weight; none of the three new decisions grants political power, manpower or equipment, and the once-only rows cannot be re-entered.
6. Japanese penetration: `shx_campaign.4` sells the line for `shx_japanese_concession` (industrial capacity -5 percent, political power gain -5 percent, stability -5 percent) and 6 cohesion, or refuses for -8 cohesion and -4 percent stability with nothing gained. The concession is removable only through the 75 political power buy-back, which clears `shx_concession_granted`, so the flag is never left unread.
7. Every string: keys exist for all ten focuses, three decisions, two events (title, description, every option), the category, the two requirement tooltips, the loss tooltip and the spirit. The suite asserts definition and reference in both directions, BOM, and no `§`/`£`.
8. Suite: `.tools/tests/test_shx_nanjing.py` parses the shipped files, models the routing, the band guard, the handover, the charter reader, the coalition cost and once-only behaviour, the cohesion gate, the debt cap, the flag and constant censuses and the localisation coverage. It fails on an unmodelled block and runs four named mutants: band opened twice, coalition replayed, charter flag unread, routing gap at 1928. All four are caught.
9. Existing suites: listed under validation below.
10. Nothing else moved: `shx_rise.txt`, `shx_wars.txt`, `china_warlord_sea.txt`, `china_warlord.txt`, `rch_warlord.txt`, `common/on_actions/rch_campaign.txt` and `common/scripted_effects/rch_campaign.txt` are untouched, as are `history/`, `.gfx`, artwork, characters and country leaders. No new sprite was needed.
11. No new world hook: the band is driven by the existing `on_daily_SHX`; no `on_actions` file was edited.
12. Docs: `docs/systems/shx_campaign.md` and `docs/endsieg_dynamic_effects.md` carry the band, its flow, its readers, its interactions and both new helpers.

## Validation

Commands run from the mod root, `python` = the workspace interpreter.

| Command | Result |
| --- | --- |
| `python .tools/tests/test_shx_nanjing.py` | 1654 checks, 0 failures, exit 0 |
| `python .tools/tests/test_shx_nanjing.py --detail` | the four named mutants print `ok`; the unread-charter run fails the flag census as intended |
| `python .tools/tests/test_shx_warlord.py` | 769 checks, 0 failures, exit 0 |
| `python .tools/tests/test_rch_succession.py` | all checks passed, exit 0 |
| `python .tools/tests/test_qing_survival.py` | all checks passed, exit 0 |
| `python .tools/tests/test_qing_consolidation.py` | all checks passed, exit 0 |
| `python tools/china_audit.py` | exit 0, 468 focuses, 72 decisions, 0 missing focus keys, the 16 `PER_*` decisions belong to the parallel Iran session |
| brace counts on the nine edited script files | open equals close in every file |
| sprite census | every `GFX_focus_*`, `GFX_decision_*`, `GFX_idea_*` and report picture named by the band is registered in the mod or the installed game |

MCP routes used (all read-only, no write route was invoked):

- `hoi4.source_lookup` `shx_campaign_tick`: one definition at `mod:common/scripted_effects/shx_campaign.txt:11-78`, referenced from `on_daily_SHX` at `common/on_actions/shx_campaign.txt:4`. Workspace revision `6037fe71fa24d25d6b14653eb851e90045a1d2cdded9073efa66172d9dc24376`.
- `hoi4.source_lookup` `shx_open_nanjing`: one definition at effects:124-130, one reference from `shx_campaign_tick` at effects:61.
- `hoi4.source_lookup` `shx_autonomy_charter`: 0 definitions. Expected, because it is a country flag and not a script symbol. The reader proof is the suite's flag census plus triggers:101-106.
- `hoi4.focus_inspect` `shx_nanjing` (national): 1 tree, 10 focuses, 0 tree diagnostics, 12 connectors, crossing 0, node intersections 0, long connectors 0, sibling deviation 0, layout hash `4f153938f5513ffa99a3a279f3ff33f010800700dae663b5ab6e47f74271846d`. Artifact `focus-inspect.3a3b3c7fefc72d3c.json`. The same response carries 19 `FOCUS_TREE_NOT_FOUND` warnings for other files in `common/national_focus/` that hold no tree (shared branch fragments, titlebar styles); they are not this card's files.
- `hoi4.script_validate` `path`: `common/national_focus/shx_nanjing.txt` and `events/shx_campaign.txt` return `SCRIPT_CHECKED`, valid, 0 findings, 43 and 36 commands. `common/scripted_effects/shx_campaign.txt`, `common/scripted_triggers/shx_campaign.txt`, `common/decisions/shx_campaign.txt`, `common/decisions/categories/shx_campaign.txt`, `common/ideas/shx_campaign.txt` and `common/ai_strategy_plans/SHX_warlord.txt` return `SCRIPT_CHECK_PARTIAL`: 0 findings, 0 unresolved commands, partial because scripted-effect and scripted-trigger roots carry no declared scope (`unknownScopeRoots` 12, 14, 1) and argument blocks stay unchecked. The three non-script families are `family: unsupported` with 0 commands checked, so those three paths are effectively unvalidated by this route.
- `hoi4.mod_index` `overview`: mod indexed, 3994 files, `focus_tree` 103, `decision_category` 1372, `script_constant` 552. Namespace list truncated by the tool (`omittedNamespaces` 333), so `shx_campaign` is not visible in the summary.
- `hoi4.decision_inspect` and the probability routes were not run: the card records the 1.19.2-vs-1.19.3 scenario adapter failure, and no decision weight in this band was balanced against a scenario. No probability claim is made.

## Mutants

| Mutant | Scenario | Result |
| --- | --- | --- |
| band opened twice (band guard becomes `always = yes`) | `scenario_one_tree` | caught |
| coalition replayed (drop `shx_coalition_lost` gate and `fire_only_once`) | `scenario_coalition` | caught |
| charter flag unread (writer renames the flag) | `scenario_flags_and_loc` | caught |
| routing gap at 1928 (wars keep the decade) | `scenario_routing` | caught |

## Residuals, simplifications and blockers

- **Live play not performed.** No launch was authorised. The 1928 tree switch, the `shx_nanjing_government` panel, the 120-day squeeze clock, the coalition row and the 1936 handover are unverified in the game. They are verified in source and in the suite only.
- **Card-body correction, `test_shx_warlord.py`.** The card allows edits to that file only where the 1928 split changes routing expectations. Two of its censuses are not routing assertions and still had to learn about the new content, because they enumerate the slice-1 file list: `scenario_constants` counts `constant:shx_story.*` readers across `OWNED`, and `scenario_flags_and_loc` builds its referenced-loc set from `shx_rise.txt` and `shx_wars.txt` only. Adding slice-2 keys and constants to the shared files therefore failed 43 checks that are about the shared files, not about slice 1. The fix was additive and removed no check: `common/national_focus/shx_nanjing.txt` joined `OWNED` and the two loc-reference scans, `shx_nanjing_government` joined the explicit category keys, the two routing expectations changed from `shx_wars` to `shx_nanjing` at and after 1928, the 1935 handover check now expects all three band flags cleared, and `DECISIONS` also parses the `shx_nanjing_government` block. The suite went 613 to 769 checks because the censuses now cover the third tree; its twelve mutants still run and pass. Three of its own `check` lines were rewritten in place and none was deleted.
- **`DECISIONS` now holds rows from both categories.** Slice-1 helpers such as `decision_visible` therefore see the new rows too. That is intended for the censuses, and no slice-1 assertion regressed.
- **Two validation gaps in MCP coverage.** `common/ideas/shx_campaign.txt`, `common/decisions/categories/shx_campaign.txt` and `common/ai_strategy_plans/SHX_warlord.txt` are `family: unsupported` for `script_validate`, so their command coverage is zero in that route. The suite parses and asserts them instead, and that is source evidence, not engine evidence.
- **`shx_autonomy_charter` cannot be found by `source_lookup`.** Flags are not script symbols. A QA pass looking for a definition through that route will get 0 and should read triggers:101-106 instead.
- **Sprite the band wanted and could not find:** a dedicated Shanxi statute focus icon (`GFX_focus_SHX_statute`) and a Japanese railway-survey icon (`GFX_focus_SHX_railway_survey`). Neither exists, and no new artwork was authorised, so the band reuses registered Chinese and generic focus icons.
- **No probability claim.** The `ai_nanjing_*` constants are authored scores, not measured shares. No campaign was observed and no probability scenario was built.
- **Coalition content is off-map.** The 1930 campaign is represented by the decision, its cost and the report event. No war, no war goal and no participants were created for it, which is the design the card asked for (a defeat, not a reward).

## Correction pass after QA round 1 (run 221)

Two problem keys, both fixed in source, both now covered by an executed check and a named mutant.

### `shx-tier-three-admits-fractious`

`shx_cohesion_tier_three` was `NOT = { shx_cohesion_brittle = yes }`.
The brittle band is bounded on both sides (`>= 30` and `< 55`), so its negation was true below 30 as well as at 55 and above: the gate admitted the fractious tier and excluded the brittle one, the inverse of its own comment and of both requirement tooltips.

- `common/scripted_triggers/shx_campaign.txt:86-95` — the body is now the union of the two upper tiers, `OR = { shx_cohesion_steady = yes shx_cohesion_devoted = yes }`, so the gate is read from the same two triggers that publish the spirit the player sees. Neither consumer changed: `shx_charter_open` (triggers:102) and `shx_coalition_open` (triggers:111) still call the gate. The two decision rows (decisions:306, decisions:331) and both tooltips (`shx_tt_statute_terms`, `shx_tt_coalition_terms`, which promise "A Province That Obeys or better") are now true statements.
- `.tools/tests/test_shx_nanjing.py` — new `scenario_tier_three`: the gate is executed at cohesion 0, 10, 20, 29, 30, 40, 54, 55, 56, 70, 79, 80, 95, 100 and must be shut below 55; the gate must agree with the spirit `shx_refresh_mechanics` publishes at each of those values; the statute row and the coalition row are executed at 0/10/29/30/54 (shut) and 55/56/80 (open); the band panel's `visible` is executed at the same values.

### `shx-concession-survives-handover`

`shx_japanese_concession` outlived the band while its only exit, `shx_buy_back_the_concession`, sat in `shx_nanjing_government`, which closes at 1936.1.1. A late concession was therefore a permanent -5 percent industrial capacity, -5 percent political power gain and -5 percent stability with no reachable remedy, and `shx_concession_granted` was written and never read again.

- `common/scripted_effects/shx_campaign.txt:80-110` — `shx_hand_over_to_vanilla` now removes `shx_japanese_concession` with the four cohesion spirits, and clears the band's one-shot records `shx_nanjing_squeeze_seen`, `shx_concession_granted` and `shx_coalition_lost`. `shx_autonomy_charter` still survives, because AC3 makes it permanent and it is the province's own statute rather than band state. The header comment now states this and why.
- `.tools/tests/test_shx_nanjing.py` — new `scenario_handover_concession`: a 1935.6.1 province holding the concession, the charter, `shx_coalition_lost` and the squeeze guard is run across 1936.1.1; the spirit must be gone, no spirit may remain, `shx_concession_granted` and the other one-shot records must be cleared, the panel and its buy-back row must be closed, and the charter must survive. New helper `category_visible` executes the category's own `visible` block, so "the row is gone" is proved with its parent panel rather than on the row alone.
- Documentation kept aligned: `docs/systems/shx_campaign.md` (step 5, the northern squeeze, the `shx_hand_over_to_vanilla` entry), `docs/endsieg_dynamic_effects.md` (same entry), the `shx_japanese_concession` comment in `common/ideas/shx_campaign.txt` and the `shx_campaign.4` comment in `events/shx_campaign.txt` all said or implied the spirit was permanent.

### Mutants (now six)

| Mutant | Scenario | Result |
| --- | --- | --- |
| band opened twice | `scenario_one_tree` | caught |
| coalition replayed | `scenario_coalition` | caught |
| charter flag unread | `scenario_flags_and_loc` | caught |
| routing gap at 1928 | `scenario_routing` | caught |
| tier three admits the fractious band (body reverted to `NOT = { shx_cohesion_brittle = yes }`) | `scenario_tier_three` | caught |
| concession survives the handover (`shx_japanese_concession` dropped from the handover's `remove_ideas`) | `scenario_handover_concession` | caught |

### Validation of this pass

- `.tools/tests/test_shx_nanjing.py`: 1778 checks, 0 failures, exit 0 (was 1654). `--detail` shows the new checks and both new mutants caught.
- `.tools/tests/test_shx_warlord.py`: 769 checks, 0 failures, exit 0. No slice-1 assertion touched in this pass; the handover edit did not collide with its mutant anchors.
- `test_rch_succession.py`, `test_qing_survival.py`, `test_qing_consolidation.py`, `tools/china_audit.py`: exit 0 (audit still reports the 16 `PER_*` keys that belong to the parallel Iran session).
- Independent probe (not importing the suite, reading only the shipped files): the gate is shut at 0/10/20/29/30/40/54 and open at 55/56/70/79/80/95/100; the handover removes every spirit the band can add; every cleared flag still has a writer; the charter still has readers. 0 failures.
- `hoi4.script_validate` `path common/scripted_effects/shx_campaign.txt`: `SCRIPT_CHECK_PARTIAL`, 0 findings, 126 commands (was 123), 25 argument blocks unchecked, `unknownScopeRoots` 12.
- `hoi4.script_validate` `path common/scripted_triggers/shx_campaign.txt`: `SCRIPT_CHECK_PARTIAL`, 0 findings, 59 commands (was 58), 12 argument blocks unchecked, `unknownScopeRoots` 14.
- `hoi4.source_lookup shx_cohesion_tier_three`: one definition, triggers:90-95, body as shipped, four references (decisions:306, decisions:331, triggers:102, triggers:111).
- `hoi4.source_lookup shx_hand_over_to_vanilla`: one definition, effects:88-110, text showing the concession removal and the three flag clears, one reference from `shx_campaign_tick:21`.
- **Not performed:** no game launch, so the corrected gate, the handover and the concession remain unverified in play. No commit and no review request from this worker.


## 2026-10-27 — the 1918 bookmark start

Christopher's live 1918 report showed three defects in one session: the rescue mission drawn in 1918, the generic Republic tree, and Shanxi appearing only after unpausing. This pass repairs the last two and the mission's window and text; the reasoning is in `docs/systems/rch_campaign.md` and `docs/systems/shx_campaign.md`.

### Root causes and paths

- `common/decisions/rch_campaign.txt:141-195` — `rch_save_the_republic` kept its year and entry gates in `available`, so `visible` drew it from 1912 as a card the player could not take, and nothing stated the `remove_trigger` terms.
- `common/on_actions/endsieg_on_actions.txt:126-238` — the pre-1936 tree pass loads a chapter inside `every_country`, so a start after the RCH history's own `shared_GEN_*` completions could keep the generic tree; the RCH branch alone was not a reliable bookmark initializer.
- `common/on_actions/rch_campaign.txt:10-16` — Shanxi was released on the first `on_daily_RCH` tick, while `history/states/615-Shanxi.txt` gives the state to the Republic from 1914 and to Shanxi only in 1936. A 1918 start had no Shanxi until the player unpaused.

### What changed

- `activation` on `rch_save_the_republic` now requires `rch_campaign_active`, `date > 1933.12.31` and `date < 1935.1.1` as well as the two settlement flags. `days_mission_timeout` makes the block a mission, so `activation` is the gate the engine checks daily, and the identical `visible` block stays only as the card's stated window and is inert. `available` keeps the off-script and entry gates untouched.
- `complete_effect` publishes `custom_effect_tooltip = rch_save_the_republic_terms_tt`, a new English key that states all seven success conditions in plain prose, and `rch_save_the_republic_desc` no longer promises a 1936 division the mission exists to prevent.
- `on_startup` carries two bounded blocks after the tree pass. The first re-asserts the chapter for `country_exists = RCH` and `date < 1936.1.1` through `rch_initialize_campaign` then `rch_route_chapter`; the second runs `china_release_warlord_shx` for `date > 1916.6.5` and `date < 1936.1.1`, and only when the release landed and the flag was unset does `SHX` take `shx_campaign.1` once plus `shx_campaign_tick`, so the province loads with its rise band tree instead of an empty panel.
- The daily hook, the continuous 1916 release and the 1936 handover are untouched. No date block was added to `history/states/615-Shanxi.txt`.

### Tests and routes

- `.tools/tests/test_china_1918_bookmark.py` (new): startup structure, the shipped 1918 world, two negative controls that delete the repair and the pre-release from the same text, and the 1916.6.5 / 1936.1.1 boundaries. All checks passed.
- `.tools/tests/test_rch_succession.py`: all checks passed, including `rescue window` (the mission's `activation` is hidden at 1918.3.21 and 1933.12.31, drawn 1934.1.1 to 1934.12.31, hidden at 1935.1.1, hidden off-script, once saved and once failed, and the inert `visible` copy must agree on every boundary date) and `rescue mutants`, which catch a deleted `activation` (the `visible`-only shape), a removed window, a removed campaign gate, a renamed tooltip key and a terms text missing one condition. A further mutant deletes the inert `visible` copy alone and is required to leave every verdict intact, so the group cannot pass by measuring the block the engine ignores.
- `.tools/tests/test_shx_nanjing.py`: 1778 checks, 0 failures. `.tools/tests/test_shx_warlord.py`: 769 checks, 0 failures.
- `hoi4.script_validate path common/decisions/rch_campaign.txt`: `SCRIPT_CHECKED`, 0 findings, 220 commands, `unknownScopeRoots` 0. `path common/on_actions/endsieg_on_actions.txt`: `SCRIPT_CHECK_PARTIAL`, 14 unresolved, all pre-existing (six character tokens used as effects, eight raw `TAG` triggers at 1918, 1919, 1931, 1932, 1939, 1940, 1947 and 1948), none in the two startup blocks. `hoi4.decision_inspect mode inventory`: `DECISION_ANALYZED`, 4385 decisions, 0 unresolved. `decision_inspect` inspect and scenario modes are blocked here by `PROBABILITY_GAME_VERSION_UNSUPPORTED` (adapter 1.19.2.0, installed game 1.19.4.0).
- **Not performed:** no game launch, so the tree the engine holds after the effect returns, the focus panel repaint at load, Shanxi's capital and politics after a startup release, and the 1934 mission card remain live checks. No commit and no review request from this worker; the card is queued for `director_qa_admission`.

### Correction after QA round 1

QA rejected the first delivery under `rch-save-the-republic-mission-gated-by-visible`. `rch_save_the_republic` declares `days_mission_timeout = 365`, which makes it a mission, and the offline wiki says twice that `visible` does nothing in missions while `activation` is the daily-checked gate that decides whether the card is drawn (`paradox_wiki/Decision modding - Hearts of Iron 4 Wiki.md:95` and `:473`, revision `7713b9bc…`; route `hoi4.reference_search` hit `1143d7db…`). The `visible` block this pass added could not hide the card, and the suite evaluated that same block through its own trigger model, so it agreed with the defect instead of catching it.

What changed in the correction:

- `common/decisions/rch_campaign.txt` — `rch_save_the_republic` now declares `activation` with `rch_campaign_active`, `date > 1933.12.31`, `date < 1935.1.1` and the two settlement flags. The identical `visible` block stays as the card's stated window and the comment records that the engine ignores it for missions.
- `.tools/tests/test_rch_succession.py` — the `rescue window` group now reads `activation` for every verdict and asserts that the decision really is a mission, that the inert `visible` copy agrees with `activation` on every boundary date, and that a failed republic hides the card. `rescue mutants` deletes `activation` (the exact rejected shape), the activation date window, the activation campaign gate; it also removes the inert `visible` copy and requires the verdicts to be unchanged.
- `docs/systems/rch_campaign.md` — the rescue section states the `activation`/`visible` split, records that a 365-day timer can outlive the window, and the validation list now reports 220 commands, eight raw `TAG` triggers (1947 and 1948 included) and the reference-search citation.

Re-run after the correction: `test_rch_succession.py` all checks passed, `test_china_1918_bookmark.py` all checks passed, `test_shx_nanjing.py` 1778/0, `test_shx_warlord.py` 769/0, `test_qing_survival.py` and `test_qing_ww1_layout.py` exit 0, `hoi4.script_validate` on the decision `SCRIPT_CHECKED` 0 findings.

`test_qing_consolidation.py` now reports 108 failures, all of them `QW2_*` focus `x`/`y` moves in `common/national_focus/qing_interwar.txt`, which was relaid out by another session at 15:52 while this pass was running (125 insertions and 125 deletions, coordinates only). That file is outside this card's ownership and was not touched here, so the failures are recorded rather than repaired.
