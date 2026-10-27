# I10 handoff: derived foreign leverage and separate repayable debt

Card: `t_03a9821b`. Branch `TeknoDev-Branch`, no commit (Director integrates after independent QA).

## What changed

Dependence is now published instead of accumulated. `iran_recompute_leverage` is the only writer of `iran_leverage_landed` and `iran_foreign_leverage`:

- `landed = clamp(iran_leverage_baseline + (british + northern + german influence − iran_influence_baseline) × 0.5, 0, 100)`
- `aggregate = clamp(landed + iran_leverage_debt, 0, 100)`

Credit is the only stored part (`iran_leverage_debt`, opening 0). The three influences are clamped before derivation, so a concession taken at the cap cannot manufacture dependence the patron never gained. The publisher never calls `iran_refresh_mechanics`, so a caller cannot recurse.

Baselines (`iran_leverage_baseline`, `iran_influence_baseline`) are captured once by `iran_leverage_baseline_init`, called at the end of `iran_initialize_campaign` after the chapter openings and before any spirit is published, and defensively from the publisher for an already-active country that has no `iran_leverage_baselined` flag. A chapter transition does not re-base.

## Files

- `common/scripted_effects/iran_campaign.txt`: new `iran_leverage_baseline_init` (lines 9–22) and `iran_recompute_leverage` (29–47); `iran_refresh_mechanics` calls the publisher before the dependence spirit test and no longer clamps the aggregate itself; `iran_initialize_campaign` captures baselines before `iran_route_chapter` / `iran_refresh_mechanics`; `iran_influence_tick` republishes after the monthly drift. The I9 wartime chain is untouched.
- `common/scripted_effects/iran_great_game_acts.txt`: all sixteen concede/reclaim effects drop their `iran_foreign_leverage` write and clamp, and call `iran_recompute_leverage` instead.
- `common/script_constants/iran_campaign.txt`: new `leverage_derivation_weight = 0.5`, `leverage_debt_opening = 0`, `leverage_repayment = 10`. `leverage_gain`/`leverage_loss`/`leverage_dependency` keep their values.
- `common/decisions/iran_campaign.txt`: the oil project's remove effect and the court reform retarget to debt; `iran_repay_foreign_credit` is visible on `iran_leverage_debt > 0` and available on debt ≥ `leverage_repayment`, and subtracts the repayment from debt.
- `common/decisions/iran_foreign_agreements.txt`: the four agreements drop their paired leverage write; customs and the two reform decisions retarget debt.
- `common/decisions/iran_great_powers.txt`, `iran_great_game.txt`, `iran_oil_settlement.txt`, `iran_focus_interwar_b.txt`, `iran_focus_ww1.txt`: paired writes removed where an influence change carried them, unpaired ones retargeted to debt with their magnitudes.
- `events/iran_campaign.txt`: `.14.a/.14.b`, `.15.a`, `.27.b`, `.28.b`, `.40.a` (paired write dropped, the concessions now speak for themselves), `.41.a`, `.42.a`, `.55.a/b`, `.64.a`, `.69`/transit options, and `.71.a`/`.72.a`, which now call `iran_concede_british_small` / `iran_concede_northern_small` once instead of adding leverage.
- `events/iran_focus_interwar.txt`: Abadan deal retargets to debt.
- `common/national_focus/iran_ww1.txt`: `IR1_merchant_credit` (line 688) and `IR1_russian_understanding` (1126) retarget to debt; both already call `iran_refresh_mechanics`.
- `common/national_focus/iran_ww2.txt`: `IR3_american_mission` (1512) retargets to debt and now calls `iran_recompute_leverage` because it has no spirit refresh of its own.
- `localisation/english/iran_variables_l_english.yml`: `iran_foreign_leverage` renamed to "Foreign Dependence"; new `iran_leverage_landed` ("Influence-Held Dependence") and `iran_leverage_debt` ("Repayable Debt").
- `localisation/english/iran_campaign_l_english.yml`: `iran_state_authority_desc`, `iran_sovereignty_desc`, `iran_repay_foreign_credit_desc`, `iran_foreign_dependence_desc` now distinguish influence-held dependence from repayable debt. No keys removed.
- `localisation/english/iran_great_game_acts_l_english.yml`: all sixteen `*_tt` keys restated without the fixed "+10 leverage" claim.
- `docs/systems/iran_great_game.md`: new "Dependence, and what is a loan" section; axis table, agreement table and interactions updated.
- `docs/endsieg_dynamic_effects.md`: new file, documenting `iran_recompute_leverage` and `iran_leverage_baseline_init` (purpose, scope, inputs, outputs, guards, side effects, cadence, example).
- `.tools/tests/test_iran_leverage_derivation.py`: new, 58 checks.

## Localisation keys

Edited: `iran_foreign_leverage`, `iran_state_authority_desc`, `iran_sovereignty_desc`, `iran_repay_foreign_credit_desc`, `iran_foreign_dependence_desc`, sixteen `iran_concede_*_tt` / `iran_reclaim_*_tt`.
New: `iran_leverage_landed`, `iran_leverage_debt`. English only. No new art, no new icons, no new interface.

## Verification

- `python .tools/tests/test_iran_leverage_derivation.py` and `--detail`: **58 checks, 0 failures, exit 0** in both modes. The suite parses the shipped files and executes them: 1910/1919/1936 openings at 60/40/30 with debt 0, one-time baselines, 15 influence → 7.5 (fixed point), upper and lower clamps with the debt held whole, capped concession, credit via the real `.14.a` option, repayment with and without enough debt (gate on debt), all six concede and three reclaim effects, leading-patron ties, repeated refreshes, monthly drift, chapter transition, one-time initialisation of an active country, the 40-point spirit boundary at 38/40/42, and both `.71/.72` payments. Seven mutants (paired write restored, unpaired writer on the aggregate, refresh without recompute, repayment gate on the aggregate, duplicated `.71` concession, unguarded baseline capture) each fail for their own defect.
- `test_iran_flag_readers.py`: 21 checks, 0 failures.
- `tools/iran_audit.py`: 73 files, 328 focuses, 171 events, 112 decisions, 34337 keys, missing focus keys 0. One pre-existing problem: 16 `PER_*` decisions in `common/decisions/PER.txt` have no localisation keys. That file is untouched by this card.
- `tools/iran_reference_check.py --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"`: 327 event references, 155 idea references, 9360 events and 7895 ideas known, "Every reference resolves".
- `test_iran_gulf_rewards.py`: 24 checks, 3 failures, unchanged stale-pin characterisation (`f8f9225b0` pin vs I7 `f8d54678c`), plus the key-count assertion (231 vs 221) from keys other cards added.

### Existing suites that this change breaks (superseded)

Historical record of the first handoff. The Director expanded ownership by three test paths and the integration-scope pass below repaired all three models, which are green. The diagnosis is kept because it explains what each model was pinning.

Three previously green suites failed at the time, each for a reason created by the mandated edits.

- `test_iran_wartime_demands.py`: `Unsupported: unmodelled effect 'iran_recompute_leverage'`. The I9 model executes `iran_influence_tick` against a closed set of effect names and raises on any other. The publisher call the contract requires in the monthly tick is exactly such a name. The fix belongs in that model (treat the helper as a no-op or model it); it is outside this card's write scope.
- `test_iran_bop_transitions.py`: 25 checks, 3 failures, all frame-pin assertions (". changed outside its available block") on the eight agreement and reform decisions in `iran_foreign_agreements.txt`, whose effect bodies this card is required to change.
- `test_iran_focus_tooltips.py`: 590 checks, 1 failure, `IR3_american_mission` "every non-requirement focus field unchanged", caused by the authorised `iran_recompute_leverage` call added to that focus.

## MCP evidence

- `hoi4.script_validate path=common/scripted_effects/iran_campaign.txt`: `SCRIPT_CHECK_PARTIAL`, 0 findings, 472 checked commands, 98 argument blocks unchecked, `parametersChecked false`.
- `hoi4.script_validate path=common/scripted_effects/iran_great_game_acts.txt`: same code, 0 findings, 128 checked, 60 unchecked.
- `hoi4.source_lookup symbol=iran_recompute_leverage view=structure`: 1 definition, `mod:common/scripted_effects/iran_campaign.txt` lines 29–47; with references: 15 callers (12 concede/reclaim acts, `iran_influence_tick` line 492, `iran_refresh_mechanics` line 52, `IR3_american_mission` line 1513).
- `hoi4.source_lookup symbol=iran_refresh_mechanics`: definition 50–145, 168 callers (truncated list), `unresolvedReferenceCount 2582` (workspace-wide).
- `hoi4.event_inspect trace iran_campaign.71` and `.72`, focused, depth 3, 40 nodes: `EVENT_INSPECTED_PARTIAL`, 0 blocking diagnostics, revision `9851e93d…`, graphHash `86a691df…` (both traces share the graph).
- `hoi4.focus_inspect national iran_ww1`: `FOCUS_INSPECTED`, 90 focuses, 7 diagnostics, layoutHash `e27cba64…`, no blocking diagnostics. `iran_ww2`: 99 focuses, 18 diagnostics, layoutHash `75251a2b…`, no blocking diagnostics. Neither tree was re-laid-out; only reward lines changed.
- Weighted-probability comparability: the decision/probability adapter mismatch (1.19.2 vs 1.19.3) is exhausted. No `probability_*` route was retried; the AI gate was reasoned from source instead: `iran_repay_foreign_credit` now asks for real debt, which is a strictly stronger affordability test than the old aggregate one, and every `ai_will_do` body is byte-identical.

## Limits and open work

- No game launch, no save read, no live firing, no tooltip render. Firing order, popup delivery and the in-panel strings remain unproven in the engine.
- Save compatibility for an in-progress campaign relies on the defensive baseline capture; not tested live.
- The three suite failures recorded above were resolved by the Director-scope repair in this file and are green: wartime 48/0, BoP 29/0, tooltips 594/0.
- `tools/iran_reference_check.py` was run with its documented `--game` argument; see Verification.
- Future/standing work untouched: the I2 patron-agenda slices, a post-occupation settlement for the 1941 demands, and any dedicated panel for the three powers.

## Director integration-scope completion: three regression models (24 owned paths)

Director expanded exclusive ownership by `.tools/tests/test_iran_wartime_demands.py`, `.tools/tests/test_iran_bop_transitions.py` and `.tools/tests/test_iran_focus_tooltips.py`. No gameplay source changed in this pass. The three models now describe the accepted I10 semantics instead of obsolete pins.

### 1. test_iran_wartime_demands.py (38/0 to 48/0)

The interpreter now resolves and executes scripted effects defined in the parsed effect file instead of raising on the publisher call. Added set_variable in both forms, multiply_variable, variable-name operands in add, subtract and clamp, and a per-run variable write set.

New checks: the publisher write set read statically and transitively through iran_leverage_baseline_init is a subset of the eight declared leverage and influence variables, writes both published values, and touches no dispatch state except the one-time iran_leverage_baselined receipt; executing the shipped publisher body leaves flags, ideas and dispatch untouched; every declared case republishes both derived values and dispatches and consumes exactly what it does with the call removed, using a control model built from the same text with the call stripped; an effect name the file does not define still raises.

Preservation now allows exactly the paired leverage write removal on 74 and 75, 12 units asserted to sit directly under the 12 point influence gain, and rejects anything else. New mutants: publisher absent (caught by republication, write-set check stays green), publisher writes iran_negotiation_open (caught by the write set and by the dispatch comparison), paired leverage write restored in 74, unrelated reward changed in 74.

### 2. test_iran_bop_transitions.py (25/0 to 29/0)

D1 preservation normalises the baseline body with one declared rule: a leverage write inside a body that also moves patron influence was the paired copy of that move and is dropped; a leverage write with no influence change is real debt and is renamed to iran_leverage_debt with operator and amount preserved. The check asserts 4 paired removals and 4 retargets, then requires structural equality with the shipped effect bodies. A direct-writer census rejects any decision in the file that still writes iran_foreign_leverage. All four availability scenarios and every regime, decree and ideology check are untouched.

New mutants: paired write restored, debt put back on the aggregate, Crown-rule availability branch removed, unrelated reward changed. The Director count of 33 checks and 9 failures came from expanding each failure into its own check; those collapse into the aggregate check now, which is why the repaired total is 29.

### 3. test_iran_focus_tooltips.py (590/1 to 594/0)

Preservation applies one declared focus edit, IR3_american_mission: iran_foreign_leverage becomes iran_leverage_debt and iran_recompute_leverage is called, both at the same position inside completion_reward. Every other field of that focus and every other focus must stay structurally equal, and a separate check requires the accepted edit exactly as declared. New mutant controls: publisher call removed, wider mission reward, unrelated focus reward change.

### Runs (this pass)

| suite | result |
| --- | --- |
| test_iran_leverage_derivation.py | 58 checks 0 failures plain, 58 PASS in --detail |
| test_iran_wartime_demands.py | 48 checks 0 failures plain and --detail |
| test_iran_bop_transitions.py | 29 checks 0 failures |
| test_iran_focus_tooltips.py | 594 checks 0 failures plain and --detail |
| test_iran_flag_readers.py | 21 checks 0 failures |
| test_iran_gulf_rewards.py | 24 checks 3 failures, unchanged stale f8f9225b0 pin against I7 f8d54678c, unowned |
| tools/iran_audit.py | 328 focuses, 171 events, 112 decisions, only the 16 pre-existing PER_* decision localisation gaps |
| tools/iran_reference_check.py --game | 
 ## Every reference resolves
 
  |

### MCP post-edit validation, per-file script_validate, all zero findings

| file | code | checkedCommands | argumentBlocksUnchecked |
| --- | --- | --- | --- |
| common/scripted_effects/iran_campaign.txt | SCRIPT_CHECK_PARTIAL | 472 | 98 |
| common/scripted_effects/iran_great_game_acts.txt | SCRIPT_CHECK_PARTIAL | 128 | 60 |
| common/decisions/iran_foreign_agreements.txt | SCRIPT_CHECKED, 7 pre-existing SCRIPT_FLAG_TOOLTIP_UNLOCALISED warnings | 162 | 46 |
| common/decisions/iran_great_game.txt | SCRIPT_CHECKED | 84 | 23 |
| common/decisions/iran_great_powers.txt | SCRIPT_CHECKED, 4 pre-existing flag-tooltip warnings | 105 | 14 |
| common/decisions/iran_oil_settlement.txt | SCRIPT_CHECKED | 80 | 16 |
| common/decisions/iran_campaign.txt | SCRIPT_CHECKED | 335 | 41 |
| events/iran_campaign.txt | SCRIPT_CHECKED | 375 | 90 |
| events/iran_focus_interwar.txt | SCRIPT_CHECKED | 33 | 10 |
| common/decisions/iran_focus_interwar_b.txt | SCRIPT_CHECKED | 23 | 5 |
| common/decisions/iran_focus_ww1.txt | SCRIPT_CHECKED | 25 | 4 |
| common/national_focus/iran_ww1.txt | SCRIPT_CHECKED | 600 | 110 |
| common/national_focus/iran_ww2.txt | SCRIPT_CHECKED | 737 | 167 |

Every SCRIPT_CHECKED row is valid true with parametersChecked false; the two PARTIAL rows report unresolved argument-block coverage rather than findings. The flag-tooltip warnings are pre-existing requirement tooltips in blocks this card did not author.

### Remaining validation gaps

- Every changed engine-facing source now has its own per-file `script_validate` row, including the three files the first pass had not re-run.
- `common/script_constants/iran_campaign.txt` has no script_validate family; its constants are exercised by the leverage suite through the parsed publisher body.
- `hoi4.source_lookup symbol=iran_recompute_leverage` in this pass: revision `58e8d319…`, one definition at `common/scripted_effects/iran_campaign.txt` 29–47, 15 callers, `referencesComplete false` with `unresolvedReferenceCount 2582` because the workspace index does not resolve every helper edge.
- `hoi4.event_inspect trace` runs focused with `expandHelpers false`, so its `helpers 0` count is a boundary of the analysis, not proof that the chain calls no helpers.
- No game launch, no save read, no engine observation. The probability adapter mismatch remains as recorded above and was not retried.

### Aggregate-writer census (acceptance 2)

Command: `grep -rn iran_foreign_leverage --include=*.txt common events`, then filter to write commands. Every remaining write is inside `common/scripted_effects/iran_campaign.txt` and each is an initialisation or the publisher:

| line | write | role |
| --- | --- | --- |
| 13 | `clamp_variable iran_foreign_leverage` | one-time clamp of an already-active country's current aggregate before its baseline is captured |
| 14 | `set_variable iran_leverage_baseline = iran_foreign_leverage` | baseline capture from that clamped value |
| 43–45 | `set_variable` landed, `add_to_variable` debt, `clamp_variable` | the publisher body |
| 152, 165, 186 | `set_variable iran_foreign_leverage = <era opening>` | 1910 / 1919 / 1936 chapter openings, followed by baseline capture |

No decision, event, focus or act file writes the aggregate. The eight agreement decisions, the customs/regulation decisions, the oil project, the court reform, the two ww1 focuses, the ww2 American mission and the `.14.a/.14.b/.15.a/.27.b/.28.b/.40.a/.41.a/.42.a/.55.a/.55.b/.64.a/.69/.71/.71.a/.72/.72.a` options now write `iran_leverage_debt` or nothing.

### AI weights and the repayment gate (acceptance 5)

Weight bytes are unchanged. `ai_chance` blocks in `events/iran_campaign.txt` (93) and `events/iran_focus_interwar.txt` (6) are a byte-identical multiset against `HEAD`, compared by brace-balanced extraction, and the Iran decision, focus and event diffs contain zero changed `ai_will_do`, `factor =` or `base =` lines. The only behavioural difference is the repayment gate.

The gate changed from `visible iran_foreign_leverage > 0`, `available infantry_equipment > 499` to `visible iran_leverage_debt > 0`, `available infantry_equipment > 499 AND iran_leverage_debt >= leverage_repayment (10)`. Named scenarios, prices in `@normal` multiples of the unchanged `ai_will_do` (a willingness score, not a probability):

| scenario | state | before | after |
| --- | --- | --- | --- |
| S1 opening, no credit | aggregate 60, landed 60, debt 0, 1500 equipment, peace | offered, score 5x (`60 > 49`) | hidden, no score |
| S2 loan taken | aggregate 70, landed 60, debt 10 | offered, score 5x | offered, score 5x, identical |
| S3 influence only | aggregate 45, landed 45, debt 0 | offered, score 1x | hidden, no score |
| S4 part repaid | aggregate 65, landed 60, debt 5 | offered, score 5x | visible, unavailable (5 < 10) |
| S5 debt 15 at war | debt 15, at war | score 0 | score 0, unchanged |
| S6 poor treasury | debt 15, 400 equipment | unavailable | unavailable, unchanged |

S1 and S3 are the intended correction: equipment could previously be spent to buy down dependence that no loan had created, and it no longer can. S2, S5 and S6 keep their eligibility and score. No `probability_*` route was retried, so no probability is reported.

### Consolidated run of the delivered state

One pass, at the state now on disk, having first confirmed the three repaired models were strengthened rather than relaxed (BoP gained a 4-mutant integration block, availability and regime/decree/ideology preservation kept; wartime gained 10 checks and still raises `Unsupported` for any effect the file does not define; tooltips gained field-level preservation plus three replacement mutants).

| command | result |
| --- | --- |
| `test_iran_leverage_derivation.py` | 58 checks, 0 failures, plain and `--detail` |
| `test_iran_wartime_demands.py` | 48 checks, 0 failures, plain and `--detail` |
| `test_iran_bop_transitions.py` | 29 checks, 0 failures, plain and `--detail` |
| `test_iran_focus_tooltips.py` | 594 checks, 0 failures, plain and `--detail` |
| `test_iran_flag_readers.py` | 21 checks, 0 failures |
| `test_iran_gulf_rewards.py` | 24 checks, 3 failures, unowned stale `f8f9225b0` pin against interwar content this card never edited |
| `tools/iran_audit.py` | 73 files, 328 focuses, 171 events, 112 decisions, 34337 keys, missing focus keys 0, only the 16 pre-existing `PER_*` gaps |
| `tools/iran_reference_check.py --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"` | 49 files, 327 event refs, 155 idea refs, 9360 events and 7895 ideas known, every reference resolves |

The BoP count moved from the Director's reproduced 33 checks and 9 failures to 29 checks and 0 failures because the pre-repair run expanded each failing scenario into its own check, while the repaired model reports one aggregate preservation verdict per decision and adds four explicit mutant verdicts. Nothing was deleted from the modelled surface.

All three edited localisation files still start with `EF BB BF`. The six `§` codes in `iran_campaign_l_english.yml` are pre-existing `custom_cost_text` keys on decision and tooltip consumers, none of them edited here.

### Not verified

- No launch, no save read, no engine observation. Firing order, popup delivery, the panel strings and fixed-point display of 7.5 remain source facts.
- Save compatibility for an in-progress campaign rests on the guarded one-time baseline capture and is untested live.
- The second-brain log was not written because this card forbids vault, skill and instruction edits.

## Correction after independent QA round 1

QA rejected two findings on 2026-10-27, and the Director confirmed both in source with no change of scope.

1. Both rewritten strings still said the dependence spirit applies at 50, while `constant:iran_story.leverage_dependency` is 40 and `iran_refresh_mechanics` tests that constant.
2. `iran_recompute_leverage` publishes the two variables but never toggles `iran_foreign_dependence`, which only `iran_refresh_mechanics` adds and removes. Three owned bodies moved `iran_leverage_debt` and stopped at the publisher.

### Source changes in this pass

| path | line | change |
| --- | --- | --- |
| `common/decisions/iran_foreign_agreements.txt` | 196 | `iran_reform_customs_service` gains `iran_refresh_mechanics_hidden = yes` after its debt payment |
| `common/decisions/iran_foreign_agreements.txt` | 219 | `iran_found_national_bank` gains the same hidden refresh |
| `common/national_focus/iran_ww2.txt` | 1513 | `IR3_american_mission` replaces `iran_recompute_leverage = yes` with `hidden_effect = { iran_refresh_mechanics = yes }`, which recomputes first and then republishes the spirit |
| `localisation/english/iran_campaign_l_english.yml` | 172, 218 | `iran_state_authority_desc` and `iran_foreign_dependence_desc` now state the real 40-point threshold |

`iran_refresh_mechanics` calls `iran_recompute_leverage` as its first statement, so the focus site publishes both values and the spirit in one call, exactly as the sibling `IR3_tripartite_treaty` reward already does.
The constant was not moved, and no other key, reward, weight, icon or layout was touched.

### Debt census, re-derived in this pass

A brace walk over `common/`, `events/` and `history/` found 25 `iran_leverage_debt` writes. Exactly three lacked a refresh in their innermost enclosing block before this pass: `iran_foreign_agreements.txt:195`, `iran_foreign_agreements.txt:217` and `iran_ww2.txt:1512`. All three now carry one, and no other debt write changed.
The `iran_campaign.txt:18` capture inside `iran_leverage_baseline_init` is the one write outside a decision, event or focus body; it is called from the publisher before `iran_leverage_landed` is set, which `B5b` asserts.

### Regression models extended rather than relaxed

- `test_iran_leverage_derivation.py`: new `B5` census (every debt write must sit in a block that refreshes), `B5b` publisher-chain assertion, `C22`/`C23` (customs reform and national bank take a 42 aggregate to 37 and remove the spirit), `C24` (the American mission takes a 32 aggregate to 42 and adds it), and mutants `D7` (customs refresh removed: debt 5 but aggregate stays 42 and the spirit stays on) and `D8` (the focus back on the publisher alone: aggregate 42, spirit absent). 58 → 67 checks.
- `test_iran_focus_tooltips.py`: the declared `IR3_american_mission` edit is now the debt substitution plus the hidden refresh. The replacement mutant drops exactly that entry, and the wider-reward and unrelated-reward mutants are unchanged. 594 checks.
- `test_iran_bop_transitions.py`: the agreement model now requires exactly one `iran_refresh_mechanics_hidden = yes` in every decision that writes the repayable debt, and strips refresh calls from both sides before the body comparison so the debt decisions can only differ by that call. One new integration mutant removes the customs refresh and requires the 'does not republish the dependence spirit' failure. 30 checks.
- The wartime model needed no change: it never executes the two decisions or the focus reward, and it still raises `Unsupported` for any effect the parsed file does not define.

### Runs at the corrected state

| command | result |
| --- | --- |
| `test_iran_leverage_derivation.py` | 67 checks, 0 failures, plain and `--detail` |
| `test_iran_focus_tooltips.py` | 594 checks, 0 failures, plain and `--detail` |
| `test_iran_wartime_demands.py` | 48 checks, 0 failures, plain and `--detail` |
| `test_iran_bop_transitions.py` | 30 checks, 0 failures, plain and `--detail` |
| `test_iran_flag_readers.py` | 21 checks, 0 failures |
| `test_iran_gulf_rewards.py` | 24 checks, 3 failures, unchanged and unowned (stale `f8f9225b0` pin against `iran_interwar` content this card never edited) |
| `tools/iran_audit.py` | 328 focuses, 171 events, 112 decisions, 34463 keys, missing focus keys 0, only the 16 pre-existing `PER_*` gaps |
| `tools/iran_reference_check.py --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"` | 49 files, 327 event refs, 155 idea refs, every reference resolves |

The counts in the consolidated table above are superseded by this one.

### MCP evidence for this pass

| route | input | finding |
| --- | --- | --- |
| `hoi4.script_validate` | `path=common/decisions/iran_foreign_agreements.txt` | `SCRIPT_CHECKED`, `valid true`, `checksPerformed` syntax/command_kind/declared_scope/player_text/event_popups/known_mistakes, 0 blockers, 7 pre-existing `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` warnings in `available` blocks this card never edited |
| `hoi4.script_validate` | `path=common/national_focus/iran_ww2.txt` | `SCRIPT_CHECKED`, `valid true`, 0 findings, 738 checked commands, 167 unchecked argument blocks |
| `hoi4.source_lookup` | `symbol=iran_refresh_mechanics_hidden`, `includeReferences=true`, `view=structure` | revision `3f7179dc…`, one definition at 433–435, callers now include `iran_reform_customs_service:196` and `iran_found_national_bank:219` |
| `hoi4.focus_inspect` | `treeId=iran_ww2`, `mode=national` | 99 focuses, `layoutHash 75251a2b…` identical to QA round 1, `validation.passed true`, no blocking diagnostics |
| `hoi4.event_inspect` | `mode=trace`, `iran_campaign.71`, `both`, depth 3 | revision `954f9cae…`, `graphHash 2a087a94…` identical to QA round 1, 0 blocking, focused analysis (0 helpers projected, boundary recorded) |

`decision_inspect` remains unavailable: `PROBABILITY_GAME_VERSION_UNSUPPORTED` (adapter 1.19.2.0 vs game 1.19.3.0). It was not retried.

### Remaining risks

- `iran_state_authority_desc` also says "At 50 authority" while the constitutional-state test uses `authority_reform` (65). That sentence predates this card and the Director restricted this correction to the two dependence sentences, so it was left alone and belongs in its own change.
- No launch, no save read, no in-game observation. Spirit application, the panel strings and the fixed-point 7.5 display remain source facts, and save compatibility for a running campaign still rests on the guarded one-time capture.

