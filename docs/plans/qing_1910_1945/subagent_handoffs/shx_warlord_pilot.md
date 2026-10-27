# Handoff — S20 Shanxi warlord pilot (slice 1)

Task `t_ecd7e118`, baseline TeknoDev-Branch `9989c63d9`.
Write ownership respected: 18 new paths plus one additive edit to `common/on_actions/rch_campaign.txt`. Nothing outside the reserved list changed. No commit.

## Changed paths

| Path | State | Contents |
| --- | --- | --- |
| `common/script_constants/shx_campaign.txt` | new | `shx_story` namespace, cohesion bands, debt, costs, payoffs, AI weights |
| `common/scripted_effects/china_warlord_release.txt` | new | generic `china_release_warlord` via `meta_effect`, parameters `TAG`/`STATE`/`FLAG`/`LEADER` |
| `common/scripted_effects/shx_campaign.txt` | new | `shx_campaign_tick`, band openers, `shx_refresh_mechanics`, `shx_clamp_cohesion`, `shx_add_debt`, `shx_pay_debt`, the two demand checks |
| `common/scripted_triggers/shx_campaign.txt` | new | four band triggers, `shx_has_patron`, `shx_patron_open`, `shx_patronage_due`, `shx_beijing_due`, `shx_can_declare_clique_war`, `shx_equipment_affordable` |
| `common/on_actions/shx_campaign.txt` | new | `on_daily_SHX` only |
| `common/on_actions/rch_campaign.txt` | edited | one guarded release hook inside the existing `on_daily_RCH` body. `rch_campaign_tick` still runs first and is unchanged |
| `common/ideas/shx_campaign.txt` | new | the four cohesion spirits |
| `common/decisions/categories/shx_campaign.txt` | new | `shx_provincial_command` |
| `common/decisions/shx_campaign.txt` | new | 15 decisions: four band readouts, three purchases, three patrons, stand-alone, four band actions |
| `events/shx_campaign.txt` | new | `shx_campaign.1` release, `.2` Beijing's demand, `.3` the patron's bill |
| `common/national_focus/shx_rise.txt` | new | 11 focuses |
| `common/national_focus/shx_wars.txt` | new | 10 focuses |
| `common/ai_strategy_plans/SHX_warlord.txt` | new | rise plan and clique-war plan, focus order per band |
| `localisation/english/shx_campaign_l_english.yml` | new | spirits, category, decisions |
| `localisation/english/shx_campaign_events_l_english.yml` | new | three events, every option |
| `localisation/english/shx_focus_l_english.yml` | new | 21 focus titles and descriptions, 6 navigation shortcuts |
| `.tools/tests/test_shx_warlord.py` | new | 263 checks, four mutants, source-executing model |
| `docs/systems/shx_campaign.md` | new | system doc including the dynamic-effect section |
| this file | new | handoff |

## New ids

- **Focuses:** `SHX_model_province`, `SHX_provincial_treasury`, `SHX_arsenal_expansion`, `SHX_three_thirds_compact`, `SHX_officer_school`, `SHX_refuse_beijing`, `SHX_pay_beijing`, `SHX_railway_to_the_coast`, `SHX_provincial_army`, `SHX_price_of_neutrality`, `SHX_the_model_province`; `SHX_brokers_table`, `SHX_sell_passage`, `SHX_sell_munitions`, `SHX_host_arbitration`, `SHX_suiyuan_question`, `SHX_chahar_road`, `SHX_join_the_expedition`, `SHX_wait_out_the_expedition`, `SHX_provincial_army_reform`, `SHX_the_province_endures`. No duplicate ids; every icon is a registered sprite.
- **Trees:** `shx_rise`, `shx_wars`.
- **Spirits:** `warlord_cohesion_fractious`, `_brittle`, `_steady`, `_devoted` (shared by the roster, `allowed = { is_chinese_warlord = yes }`).
- **Decisions:** the 15 listed above.
- **Events:** `shx_campaign.1`–`.3`.
- **Variables:** `warlord_cohesion`, `warlord_patronage_debt`.
- **Flags written:** `china_released_shx`, `china_warlord_released`, `shx_band_rise`, `shx_band_wars`, `shx_patron_taken`, `warlord_patron_japan`, `warlord_patron_britain`, `warlord_patron_soviet`, `shx_no_patron`, `shx_commander_grudge`, `shx_demand_pending`, `shx_demand_last`, `shx_beijing_seen`, `shx_no_troops_to_beijing`, `shx_paid_beijing`. Every one has a reader, proven by the suite's flag census.

## Routing table

| Date | Tree loaded | Band flag |
| --- | --- | --- |
| before 1916.6.6 | none (nothing released) | none |
| 1916.6.6 – 1920.7.13 | `shx_rise` | `shx_band_rise` |
| 1920.7.14 – 1935.12.31 | `shx_wars` | `shx_band_wars` |
| 1936.1.1 onward | none from this slice; `endsieg_on_actions` loads `china_warlord_sea_focus` | cleared |

1928–1935 keeps the S2 tree because the Nanjing decade is slice 2, deliberately deferred, not a defect.

## Release idempotency proof

`china_release_warlord` is guarded three ways: the caller skips when `china_released_shx` is set, the effect itself requires state 615 to be owned by the caller and not by Shanxi, and the recruit sits under `NOT = { has_character = SHX_yan_xishan }`.
The suite runs the shipped `on_daily_RCH` body twice and asserts the recruited list stays at one entry and the release flag's date does not move.

## Test and validation actually run

- `python .tools/tests/test_shx_warlord.py` → **265 checks, 0 failures**, exit 0. Scenarios cover release, routing at 1916.6.5/6.6, 1920.7.13/7.14, 1935.12.31/1936.1.1, band refresh and restoration, the debt cap and payment, patron maturity in both directions, the war gate at each band, a flag-reader census and a localisation census.
- Mutants, each caught: second patron inside the 365-day window, war at the steady band, a refresh that drops the spirit it publishes, and a release that runs twice.
- Existing suites, unmodified: `test_rch_succession.py` exit 0, `test_qing_survival.py` exit 0, `test_qing_consolidation.py` exit 0, `tools/china_audit.py` exit 0.
- Braces balanced on all 13 script files; three localisation files carry a UTF-8 BOM (`efbbbf`); one `on_daily_SHX` in the tree; no duplicate `SHX_` focus ids.

## Not done

- **MCP routes run (all read-only):** `hoi4.script_validate` with `path` on `common/scripted_effects/shx_campaign.txt` (0 findings, `SCRIPT_CHECK_PARTIAL`, 81 commands checked, 18 argument blocks unchecked), `common/scripted_triggers/shx_campaign.txt` (0 findings, PARTIAL, 37 commands), `common/scripted_effects/china_warlord_release.txt` (0 findings, PARTIAL, 1 command, 1 unknown scope root), `common/ideas/shx_campaign.txt` (family unsupported by the adapter, 0 commands checked), `common/on_actions/shx_campaign.txt` (0 findings, PARTIAL, 1 command), `events/shx_campaign.txt` (**SCRIPT_CHECKED, passed = true**, 0 findings, 29 commands), `common/national_focus/shx_rise.txt` (**SCRIPT_CHECKED, passed = true**, 0 findings, 42 commands), `common/national_focus/shx_wars.txt` (**SCRIPT_CHECKED, passed = true**, 0 findings, 33 commands), `common/decisions/shx_campaign.txt` (0 findings after two fixes below, PARTIAL, 118 commands).
  - The events file first returned `SCRIPT_COMMAND_UNRESOLVED` for `add_army_experience` at line 15. The installed effects documentation defines `army_experience`, not `add_army_experience`, so all six occurrences in this slice were corrected and the file re-validated to `SCRIPT_CHECKED`.
  - The decisions file first returned `is_at_war` unresolved inside a `FROM` target block and `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` for `shx_paid_beijing`. The war check became `has_war = yes` in the same scope, and the flag check moved into `hidden_trigger` behind `custom_trigger_tooltip = { tooltip = shx_tt_paid_beijing }`, with the key written in the English file. Re-validation returned 0 findings.
  - Not run: `focus_inspect`, `focus_render`, `decision_inspect`, `source_lookup`, `mod_index`. The trees were validated as script but their layout has not been inspected by the focus adapter.
- **No live game.** No launch, no save, no render. Shanxi appearing in 1916, the readout rows, decision clickability and the 1936 handover are unverified in play.
- **Band readout shows the band name, not the number.** Scripted localisation for Shanxi is outside this slice's 19 paths, so the readout names the band and leaves the exact value to the spirit tooltip.
- **`SHX_model_governor` (D1) still dropped** by the character override. Untouched by design; the rewards avoid it.

## Residual risks

- `meta_effect` string substitution with a dotted or numeric parameter is untested in the engine. The four current parameters are a three-letter tag, a state id, a flag name and a character token, all plain.
- `custom_cost` was avoided, so the equipment purchase exposes its requirement through `shx_equipment_affordable` rather than an inline cost row.
- `shx_host_the_conference` requires `shx_paid_beijing`, so a province that refused Beijing cannot host the conference. That is deliberate symmetry with `shx_three_thirds_compact` requiring the refusal, but it is a design call QA may want to revisit.

## Correction pass 1 (QA round 1, five keys)

QA rejected the first delivery on five keys. All five are corrected in the same 19 paths, with no new file.

| Key | Correction |
| --- | --- |
| `s20-1936-handover-missing` | `shx_hand_over_to_vanilla` added in `common/scripted_effects/shx_campaign.txt` (62-80) and called from `shx_campaign_tick` (14-20). It loads `china_warlord_sea_focus` / `china_warlord_focus` / `generic_focus` with `keep_completed`, mirroring the `on_startup` dispatcher's DLC order, and retires the slice: `shx_handover_complete` set, band flags and `shx_demand_pending` cleared, four cohesion spirits removed. The tick returns early while the flag is set (`shx_campaign.txt:10-14`), the decision category hides itself (`decisions/categories/shx_campaign.txt:7`) and `shx_can_declare_clique_war` closes at `date < 1936.1.1` and on the handover flag (`scripted_triggers/shx_campaign.txt:58-70`). |
| `s20-focus-icon-unregistered` | `SHX_suiyuan_question` now uses `GFX_focus_ww1_pdx_native_shared_gen_state_claims` (`common/national_focus/shx_wars.txt:82`). `hoi4.focus_inspect` on `shx_wars` now returns `validation.passed: true`, 0 blocking diagnostics (revision `4dc7839c17ab1a59`). |
| `s20-release-helper-hardbound` | `meta_effect` removed. `china_release_warlord_receive` is the shared body with no tag, seat, character or per-tag flag, releasing `transfer_state = var:china_release_seat` (vanilla precedent `events/GOE_Raj.txt:669`). `china_release_warlord_shx` is the per-tag wrapper holding the four literals; `common/on_actions/rch_campaign.txt:12` calls the wrapper. Docs example corrected (`docs/systems/shx_campaign.md`, Dynamic effects). |
| `s20-test-vacuous-handover-and-icons` | `run()` now raises on any effect it does not model (`INERT`/`EXTERNAL` are declared with a reason). New `scenario_handover` asserts the vanilla tree at 1936.1.1 and the retirement of flags, spirits, category and war gate. New `scenario_sprites` builds the sprite-name set from this mod's `interface/` plus the installed game's and fails on any unregistered focus icon. |
| `s20-tuning-constants-unused` | Dead keys removed (`demand_maturity_days`, `patron_maturity_days`, `patron_*_cost_power`, `demand_equipment_cost`, `war_cost_power`, `conference_cost_power`, `war_won_cohesion`, `rise_opens_year`, `wars_open_year`, `ai_maturity_hold`, `ai_war_min_tier`, plus `equipment_cost` and `demand_power_cost` found by the new census). The two flag-age values are now `@patron_maturity_days` / `@demand_maturity_days` in the triggers file; `scenario_constants` fails on any constant with no reader and any undeclared macro. |

Also found and fixed by the MCP pass: `owner = ROOT` inside a state scope is reported by `hoi4.script_validate` as `SCRIPT_DYNAMIC_VARIABLE_AS_TRIGGER`; the wrapper guard now uses `owns_state = 615` in country scope. After the fix the file returns 0 findings.

**Evidence, this pass**

- `python .tools/tests/test_shx_warlord.py` -> 500 checks, 0 failures, exit 0.
- Six mutants, each caught by name: second patron inside the window, war at the steady band, refresh dropping the spirit, release running twice, handover that loads no tree, focus with an unregistered sprite.
- Existing suites unchanged and green: `test_rch_succession.py` 0, `test_qing_survival.py` 0, `test_qing_consolidation.py` 0, `tools/china_audit.py` 0.
- `hoi4.focus_inspect` `shx_wars`: 10 focuses, `validation.passed: true`, 0 blocking diagnostics, layout hash unchanged `0f7299ee86707482a4d16d50d385caeb06282cae5dd31797db035907b356088f`.
- `hoi4.script_validate`: `china_warlord_release.txt` PARTIAL, 0 findings, 19 commands; `shx_campaign.txt` effects PARTIAL 0 findings, 97 commands; `shx_campaign.txt` triggers PARTIAL 0 findings, 40 commands.
- `hoi4.source_lookup`: `china_release_warlord_receive` 1 definition + 1 reference (`china_release_warlord_shx`); `shx_hand_over_to_vanilla` 1 definition + 1 reference (`shx_campaign_tick`).

**Still unverified:** no launch, no save, no render. Shanxi appearing in a 1916 campaign, the readout rows, decision clickability and the 1936 handover in play are unverified. `decision_inspect` scenario mode remains blocked by the game-version adapter (1.19.2.0 adapter vs 1.19.3.0 installed).

## Correction pass 2 (QA round 2, three keys)

QA rejected round 2 on three new keys, all first strike, and confirmed the five round-1 keys fixed. Corrected in the same 19 paths, no new file. Where this section and pass 1 disagree, this section is current.

| Key | Correction |
| --- | --- |
| `s20-war-xp-sign-inverted` | `war_cost_army_experience` is now `-25` (`common/script_constants/shx_campaign.txt`, Costs block), because `army_experience` is the additive effect and the mod spends XP with negative values (`common/decisions/BUL.txt:9010`). The decision line is unchanged and now spends. The Costs block states the sign convention, every cost-named constant is audited as negative, and the two positive constants that were named as costs but only ever granted rewards were renamed: `arrears_cost_power` -> `reward_power_major`, `office_cost_power` -> `reward_power_minor` (readers in `shx_rise.txt` x4, `shx_wars.txt` x4, `events/shx_campaign.txt` x1). The war decision also carries `custom_effect_tooltip = shx_tt_war_cost`, so the payment is stated on the row: "spends 25 army experience and 20 cohesion". |
| `s20-mechanic-values-unrendered` | Both mechanic values are now printed. The four band readout descriptions, the category description and the new `shx_tt_debt_state` carry `[?warlord_cohesion|0]` and `[?warlord_patronage_debt|0]` in `localisation/english/shx_campaign_l_english.yml`. The three purchase rows carry `custom_trigger_tooltip = { tooltip = shx_tt_debt_state check_variable = { var = warlord_patronage_debt value = constant:shx_story.debt_cap compare = less_than } }`, so the current debt and the bill waiting at the cap are on the row itself. No scripted localisation is involved. Vanilla precedent for a variable readout inside a `custom_trigger_tooltip`: 47 keys including `CHI_holding_state_mission_trigger` and `PRC_rural_surveyer_tt`; in-mod precedent for the readout itself: `qing_consolidation_*_desc`. |
| `s20-conference-requirement-tooltip-unconditional` | `shx_host_the_conference` no longer has an empty `custom_trigger_tooltip` beside a sibling `hidden_trigger`. The condition is inside the block, as vanilla `AST.txt:2610-2613`, `AFG.txt:732-735` and `qing_campaign.txt:513-516` do: `custom_trigger_tooltip = { tooltip = shx_tt_paid_beijing has_country_flag = shx_paid_beijing }`. The key text was rewritten to a requirement ("Beijing's demand has been answered") so it reads correctly met and unmet, instead of the old "The road to Beijing is open" on a row that was always shown. |

**Suite, this pass**

- `python .tools/tests/test_shx_warlord.py` -> **566 checks, 0 failures**, exit 0.
- The model now executes decision effect bodies (`player_take`), so the war's direction is run, not eyeballed: it asserts experience falls by the constant, cohesion falls by `cohesion_loss_war`, the war is declared, and three repeat declarations after their cooldown each still cost experience.
- New censuses: every cost-named constant is negative; both mechanic variables appear in player text; each band readout states the value; each purchase row names the debt tooltip; the debt tooltip states both demand amounts; every `custom_trigger_tooltip` in the decisions and events files carries a real condition; the conference tooltip carries the Beijing flag.
- Nine mutants, each caught by name: second patron inside the window, war at the steady band, refresh dropping the spirit, release running twice, handover that loads no tree, focus with an unregistered sprite, **war that grants army experience**, **requirement tooltip without a condition**, **band readout without the value**.
- `expect_mutant` now reloads the tuning from the mutated source, so a constant mutant is visible to the model.
- Existing suites unchanged and green: `test_rch_succession.py` 0, `test_qing_survival.py` 0, `test_qing_consolidation.py` 0, `tools/china_audit.py` 0.

**MCP, this pass (read-only)**

- `hoi4.script_validate` `common/decisions/shx_campaign.txt` -> PARTIAL, 0 findings, 120 commands, 22 argument blocks unchecked, 1 unknown scope root (the `targets`/`FROM` decision root, unchanged from earlier rounds).
- `hoi4.script_validate` `events/shx_campaign.txt` -> **SCRIPT_CHECKED, passed.** 29 commands, 6 argument blocks unchecked.
- `hoi4.script_validate` `common/national_focus/shx_rise.txt` -> **SCRIPT_CHECKED, passed.** 42 commands. `common/national_focus/shx_wars.txt` -> **SCRIPT_CHECKED, passed.** 33 commands.
- `hoi4.script_validate` `common/script_constants/shx_campaign.txt` -> family `unsupported`, 0 commands, no findings. The adapter does not validate script constants.
- `hoi4.focus_inspect` `shx_rise` -> 11 focuses, `validation.passed: true`, layout hash unchanged `acdbc31038e04d2ae2552037c8fb41946d673476c93c59049785f6cbf96aac72`, two non-blocking `FOCUS_LAYOUT_LINEAR_DETOUR` warnings. Revision `457e61ea6ec60965…`, artifact `hoi4-agent://workspace/endsieg/artifact/470c76d190ce6ca9940f0a67145bc75277c8bc9fc9ba8be6f49605541587ca7f/3511bcd35a3f3dcdd697359397e356de33f118e9411f34cca040f31ccd449473/focus-inspect.457e61ea6ec60965.json`.
- `hoi4.focus_inspect` `shx_wars` -> 10 focuses, `validation.passed: true`, layout hash unchanged `0f7299ee86707482a4d16d50d385caeb06282cae5dd31797db035907b356088f`, 0 blocking diagnostics. Artifact `hoi4-agent://workspace/endsieg/artifact/51b6083c4e6f39f9da07250196303e7e0c3ce617bd4f28a8867d8a614cbe9edc/3ad0da985409949b1f947667c98b0652d81a05abb83d542391c0b176998cac1a/focus-inspect.457e61ea6ec60965.json`.
- `hoi4.decision_inspect` inventory -> complete, 4382 decisions, 1370 categories, 0 unresolved, report hash `6e80fe50ee60466d99ebbdc6d57e133aab41f17ae9819a12ee012cb38d946bfa`. Scenario mode remains blocked by `PROBABILITY_GAME_VERSION_UNSUPPORTED`; not retried.
- The generic continuous-focus palette reports `FOCUS_LOCALISATION_REFERENCE_MISSING` for vanilla `continuous_restrict_freedom_desc`, which is a vanilla key, not this slice's.

**Still unverified after pass 2:** no launch, no save, no render. That the row descriptions render the variable on screen, that the tooltip shows red before Beijing is answered and green after, and that the war row's tooltip lists its cost are source-and-model conclusions, not engine evidence.

## Correction pass 3 (QA round 3, one key)

QA rejected round 3 on one new key, first strike, and confirmed all five round-1 and all three round-2 keys fixed. Corrected in the same 19 paths, no new file. Where this section and passes 1 and 2 disagree, this section is current.

| Key | Correction |
| --- | --- |
| `s20-ai-beijing-refuse-threshold` | The refusal was a preference where the design states a rule. `SHX_refuse_beijing` scored `@normal` with a x3 modifier above the threshold and nothing below it, and `shx_campaign.2.a` scored `ai_event_refuse_high` with a x3 modifier above it and nothing below, so below cohesion 40 the AI refused 50 percent of the focus race and 43 percent of the event roll. The x3 emphasis is gone from both surfaces and each now carries a zero gate on the same constant: `modifier = { factor = 0 NOT = { check_variable = { var = warlord_cohesion value = constant:shx_story.ai_beijing_refuse_above compare = greater_than_or_equals } } }` (`common/national_focus/shx_rise.txt:113-118`, `events/shx_campaign.txt:34-40`). Below the threshold the refuse weight is 0 and the pay weight is positive, so the province pays, which is what the design's section 12 sentence says. `SHX_pay_beijing` already carried the mirror gate at or above the threshold and is unchanged, and the patron family keeps the same shape against `ai_patron_below`. Both `ai_event_refuse_high` and `ai_event_refuse_low` are still read, so no constant became dead. |

**Suite, this pass**

- `python .tools/tests/test_shx_warlord.py` -> **613 checks, 0 failures**, exit 0. `--detail` shows all twelve mutants caught.
- New `scenario_ai_weights` scores the shipped `ai_will_do` and `ai_chance` blocks through a real evaluator (`ai_weight`: base factor times every modifier whose trigger the model can execute), not a text match. It asserts the refuse focus is 0 at cohesion 39 and positive at 40, the pay focus is positive at 39 and 0 at 40, the demand event's refusal option is 0 at 39 and positive at 40, its payment option is positive at 39, a running war still suppresses the refusal, a patron is 0 at its ceiling and positive one point below it, and the rise plan lists `SHX_model_province`, `SHX_provincial_treasury`, `SHX_arsenal_expansion`, `SHX_three_thirds_compact` in that order, which is where AC8's ordering clause actually lives.
- Three new mutants, each caught by name: **refuse focus open below the threshold**, **demand refusal open below the threshold**, **pay focus open at the threshold**.
- Existing suites unchanged and green: `test_rch_succession.py` 0, `test_qing_survival.py` 0, `test_qing_consolidation.py` 0, `tools/china_audit.py` 0. Its sixteen `PER_*` loc misses remain the parallel Iran package.

**MCP, this pass (read-only)**

- `hoi4.script_validate` `common/national_focus/shx_rise.txt` -> **SCRIPT_CHECKED, passed**, 42 commands, 0 findings, 14 argument blocks unchecked, 0 unresolved, documentation revision `9227e238bce49345e9c358598b4dd4940c733d906b72324e8a02a57ecb42093b`.
- `hoi4.script_validate` `events/shx_campaign.txt` -> **SCRIPT_CHECKED, passed**, 29 commands, 0 findings, 6 argument blocks unchecked.
- `hoi4.focus_inspect` `shx_rise` -> 11 focuses, `validation.passed: true`, layout hash unchanged `acdbc31038e04d2ae2552037c8fb41946d673476c93c59049785f6cbf96aac72`, 13 connectors, 0 crossings, 0 node intersections, the same two non-blocking `FOCUS_LAYOUT_LINEAR_DETOUR` warnings. Revision `1182236c4c43bf2bd28358a6fadf8999be0ff7eae41c11f69d5332b7422d99bc`, artifact `hoi4-agent://workspace/endsieg/artifact/0e223607c185f1fe4b9cef991650d373467ed44f0a5790dfc87a7b53ec10fe3e/b18596c0898dc963898d35de732be00b0cf29d9b3488427390a638a1d61d8e55/focus-inspect.1182236c4c43bf2b.json`. The weight change is invisible to layout, as expected.

**Docs, this pass:** `docs/systems/shx_campaign.md` gained an `## AI` section stating the two thresholds as gates, naming the plan as the place the band's order lives, and recording that a province below 50 political power is forced to refuse because the payment option carries that trigger. That last point is a resource constraint on the option, not a scoring leak.

**Residual after pass 3:** the same live-game gap as passes 1 and 2. No launch, no save, no render, so whether the AI actually pays below 40 in a running campaign is unverified. The model proves the weights, not the engine's race arithmetic, and no share of a selection race is claimed anywhere.
