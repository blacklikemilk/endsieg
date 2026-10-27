# The Restoration turno: appointing a government and the ministerial crisis

> Status: implemented in the S12 slice (card t_cb995ac7) from the accepted S2 design revision 1, slices A+B core; corrected in S12a (card t_47329669) and finished in S12b (card t_00b07993) before integration.
> Source of truth for tuning is `common/script_constants/spain_campaign.txt`; this file explains the system and its arithmetic.

## The hole this closes

Before this card `spain_government_party` was written only twice, both times to `0` (`common/scripted_effects/spain_cortes_parties.txt:20,97`), after which `spain_government_recount` defaulted it from the chapter flag.
Nothing in the mod could therefore replace a government.
An election swung the chamber, `spain_cortes_recount` rebuilt the benches, and the government kept the benches its party happened to hold.
A Restoration Spain whose government was short of 201 seats had no way back to a majority and no way to change who governed.

## What the player can now do

Three routes sit in `SPR_crown_and_cortes_category` (`common/decisions/spain_campaign.txt`), each visible only while `spain_restoration_cortes_live` holds and the government bloc is below `cortes_majority` (201).

1. **Draw Up the Lists** (`SPR_encasillado`) — the turno.
   No political power changes hands.
   The price is Crown patronage, the rot that patronage feeds, and the donors the machine empties.
2. **Go to the Country** (`SPR_honest_election`) — the existing `spain_hold_election`, 50 political power, no guaranteed result.
3. **Rule by Decree** (`SPR_royal_decree`) — 75 political power, no bench moves, the Crown loses ground in the balance and the army loses confidence.

All three end in `spain_appoint_government`, the only place a government is appointed: `PARTY = 0` keeps the sitting party and every route that does not change who governs asks for a re-count this way.
The one other writer of `spain_government_party` is `spain_encasillado`'s fallback, which names the monarchists when the chamber still has no government at all.
`spain_appoint_government` is also the only place that **sets** `spain_ministry_crisis_open`, when the bloc it counts falls short of 201.
The flag is **cleared** in five places, and the appointment is only one of them:

- `spain_appoint_government`'s `else` branch, when the resulting bloc reaches 201;
- `SPR_ministerial_crisis`'s `complete_effect` and its `timeout_effect`;
- `SPR_royal_decree`'s `complete_effect`;
- the single option of `spain_campaign.32`, the Crown's own turno, which clears the flag before it draws so that the draw may legitimately re-open the crisis.

## The appointment

`spain_appoint_government` (`common/scripted_effects/spain_cortes_parties.txt`) takes `PARTY`, `COALITION_1` and `COALITION_2`.
`PARTY = 0` keeps the sitting government, which is how a route that does not change the party asks for a re-count; the value is written to the scratch variable `spain_appoint_party` first because `check_variable` reads a variable name, never a literal.
The effect sets the party and the two coalition slots, increments `spain_government_changes`, then calls `spain_government_recount`, `spain_cortes_refresh_display` and `spain_cortes_redraw_hemicycle` so the panel, the majority gap and the hemicycle all change on the same day.
It sets `spain_ministry_crisis_open` when the resulting bloc is below 201 and clears it when a coalition reaches 201, so an appointment that can legislate closes the crisis on the spot.

The whole effect is a no-op unless `spain_restoration_cortes_live` holds:

- `spain_in_restoration_chapter` — the chapter the machine belongs to.
- `has_power_balance = { id = SPR_crown_and_cortes }` — the balance the effect pushes exists.
- no `spain_coup_in_progress` — a coup has already replaced the question.
- not `spain_chapter_civil_war` — the wartime chapter legislates through neither Crown nor Cortes.

The design's `has_power_balance` guard was replaced by this explicit chapter and state exclusion because the balance is re-created for the Republic, which reads its own chamber.

## The arithmetic of one encasillado

`spain_encasillado` moves 18 raw support points out of four named blocs into the party that governs:

| Donor | Constant | Raw |
| --- | --- | --- |
| Liberals | `turno_from_liberals` | 7 |
| Conservatives | `turno_from_conservatives` | 5 |
| Republicans | `turno_from_republicans` | 4 |
| Socialists | `turno_from_socialists` | 2 |

The four donors sum to `turno_seat_transfer`, so the chamber's raw total is unchanged and only the benches move.
The effect also adds `patronage_gain` (6) to `spain_crown_patronage` clamped at the existing `patronage_cap` (24), calls `spain_push_crown`, calls `spain_loyalty_gain_small` (which, after S14, raises loyalty and lowers coup pressure), sets `spain_election_manufactured`, and increments `spain_encasillados` clamped at `encasillado_cap` (3).
It re-counts the chamber before calling `spain_appoint_government`, so the appointment counts the benches the transfer just made rather than the ones the last election left behind.

Because the Restoration base has no flags set, the seat table the design derived reproduces exactly:

| Encasillados | Patronage | Monarchist seats | Note |
| --- | --- | --- | --- |
| 0 | 0 | 129 | no majority, the crisis opens |
| 1 | 6 | 188 | still short; the crisis stays open |
| 2 | 12 | 245 | a majority on the second draw |
| 3 | 18 | 304 | the donors are at the clamp floor |

The steps are not 18 seats each: seats are `round(raw * 400 / raw_total)` and `spain_cortes_fix_seat_total` gives the rounding residual to the largest party, which is the government's after a draw.
One act alone is never a majority, which is the design's point: the turno is a machine that has to be worked, not a button.

**The table is an arithmetic fixture, not a queue of offers.** `spain_government_short` keeps the three routes on the board only while the bloc is below 201, so the playable sequence out of the opening state is two draws: 129 seats open the crisis, the first draw reaches 188, the second reaches 245 and a majority.
The third row (304 seats) is not a third click in that sequence — at 245 seats the routes are no longer offered, greyed or gone by `visible` — and it is reachable only after something pushes the bloc back below 201 with a draw still in hand, an election the government loses being the obvious case.
The fixture therefore shows what the effect does from a clean Restoration state each time, which is what a source simulation can prove; it is not a promise that a player walks 129 → 188 → 245 → 304 inside one crisis.

## Who the turno pays

`spain_encasillado` pays the party that governs and nobody else.
The zero-party fallback, the seven beneficiary selectors, the monthly minority test, `spain_government_strain` and the incumbent-loss test inside `spain_hold_election` all state `compare = equals`, because the long form of `check_variable` (`var = … value = …` with no `compare`) defaults to `greater_than_or_equals` (offline wiki, `Data structures`, `check_variable` row; `documentation/triggers_documentation.md`, `check_variable` section).
With the comparison omitted, every appointed party 2..7 was reset to the monarchists by the fallback and the seven selectors became multi-recipient `>=` branches.

`test_party_identity` asserts, for each of the seven parties and for the zero fallback, that the party keeps office, that exactly one party is paid `turno_seat_transfer`, that the four donors each lose their own share, that the raw total and the 400-seat chamber are unchanged, and that `spain_encasillados`, `spain_government_changes` and patronage each move once.
A governing donor is not an exception: it pays its own share and nets the difference, so a Liberal government gains 11 raw support (18 minus the 7 it loses), the other three donors lose 5, 4 and 2, and the chamber still totals 400.
That is the arithmetic of the fixed donor list, not a defect; a future route that wants a government to keep the full transfer would have to resolve the donor list against the governing party.

## Rot has a reader

`spain_party_monthly` now reads patronage.
At or above `patronage_rot` (17) it adds `patronage_rot_shift` (1) to `spain_party_shift_republicans` and to `spain_party_shift_carlists`, adds `patronage_rot_coup` (2) to `spain_coup_pressure`, and re-counts so the chamber and the panel stay on the same month as the shift.
Patronage therefore stops being a free majority at the point where the machine is visibly eating the regime.
The two caciquismo idea bands stay a separate follow-up; no idea is added here.

## The ministerial crisis

`SPR_ministerial_crisis` is a mission in the same category, `days_mission_timeout = @crisis_timeout_days` (90, mirrored from `crisis_timeout_days` because native timer fields take literals; the test asserts the pair).
Its `activation` requires `spain_ministry_crisis_open`, so it appears only while a government is short.
Its `available` is the completion condition — `spain_government_seats` at or above 201 — and completion clears the flag.
Its `cancel_trigger` fires when the flag clears, so resolving the crisis by any route removes the mission instead of leaving it to run out.
In the shipped script that cancellation is the normal path: the turno and the election both re-count the chamber inside `spain_appoint_government`, which clears the flag on the same day the bloc reaches 201, so the mission is usually removed rather than completed.
`complete_effect` still carries the reward for the case the order does happen — `spain_court_the_chamber` and `spain_proscribe_party` re-count the chamber without appointing, so either can lift a caretaker government to a majority while the flag is still set — and the deadline stays the failure.
`is_good` is deliberately `no`: the majority is the reward and the deadline is the failure, so the panel must not relabel completion as a failure.
`timeout_effect` clears the flag and fires `spain_campaign.32`, in which the Crown draws up the lists itself.
An ignored crisis therefore costs caciquismo instead of lapsing silently.
When the machine has a draw left the event takes it (which may legitimately re-open the crisis); when the donors are exhausted the bloc loses loyalty, stability and nothing else changes, and the crisis closes.

## Interactions

- **S10 chapter model.** The guard reads `spain_chapter_restoration` and excludes the civil-war chapter explicitly; no chapter transition is changed.
- **Crown balance.** `spain_push_crown` moves the balance toward the Crown, `spain_push_cortes` away from it; the Balance of Power is not redefined.
- **S14 loyalty helpers.** `spain_loyalty_gain_small` raises loyalty and lowers coup pressure; the decree uses `spain_loyalty_loss`, which lowers loyalty and raises pressure. No helper was changed here.
- **Existing decisions.** The five PP-only decisions in `SPR_crown_and_cortes_category` are untouched, and the five coalition decisions in `common/decisions/spain_parties.txt` are untouched.
- **Category metadata** stays in `common/decisions/categories/spain_campaign_categories.txt`, which this slice does not own.

## The S12a correction

The first delivery of this slice shipped nine `check_variable` tests in `common/scripted_effects/spain_cortes_parties.txt` with no `compare`.
The long form resolves an omitted comparison as `greater_than_or_equals`, so `check_variable = { var = spain_government_party value = 0 }` was true for every party and reset the government to the monarchists, and each of the seven beneficiary selectors became a `>=` branch that paid every party at or below the government's id.
A majority government was also charged the monthly minority penalty.

| Where | Before | After |
| --- | --- | --- |
| `spain_encasillado`, zero-party fallback | `value = 0 }` | `value = 0 compare = equals }` |
| `spain_encasillado`, seven selectors | `value = 1 }` … `value = 7 }` | `value = 1 … 7 compare = equals }` |
| `spain_party_monthly`, minority test | `spain_government_majority value = 0 }` | `spain_government_majority value = 0 compare = equals }` |

The local precedent is `spain_government_recount`'s own zero test at lines 105-106, which already stated `compare = equals`; the documentation is `documentation/triggers_documentation.md` (`check_variable` section) and the offline wiki's `Data structures` page, whose `check_variable` row documents the `greater_than_or_equals` default.

Evidence, all of it source-level:

- `python .tools/tests/test_spain_turno.py` → 109 checks, 0 failures; `--detail` → 109 `ok` lines and exit 0. The pre-correction suite was 83 checks, 0 failures, because its seat-table state always started from `spain_government_party = 1`: the one party the old selectors happened to preserve.
- `test_correction_mutants` rebuilds the exact pre-correction file from the shipped one by removing those nine comparisons and asserts the transformation is its own inverse before using it. On that reconstruction the party checks fail for `[2, 3, 4, 5, 6, 7]` and pass for party 1; a mutant that repairs only the zero-party fallback also fails `[2, 3, 4, 5, 6, 7]`, so a one-line repair cannot pass.
- On the pre-correction text the monthly check reports a majority month at `-0.02` stability and `3` coup pressure, where the delivery reports `0` and `0`.
- `test_patronage_cap` draws from 20 of the 24-point cap, a state reachable from the focus grants; the shipped clamp stops at 24 and the removed-clamp mutant returns 26 and then 32.
- Regressions on the same tree: `test_spain_cortes_recount.py` 215/0, `test_spain_cortes_runtime.py` 113/0, `test_spain_restoration_loyalty.py` 146/0, `test_spain_hemicycle_builder.py` 69/0.
- `hoi4.script_validate` on the file: `SCRIPT_CHECK_PARTIAL`, 0 findings, 332 commands checked, `parametersChecked = false`, 193 argument blocks unchecked across 11 unknown-scope roots, docs revision `9227e238…`; `hoi4.source_lookup` resolves `spain_encasillado` (declared once, called by `SPR_encasillado` and `spain_campaign.32`) and `spain_party_monthly` (declared once, called by `on_monthly_SPR`) and returns the corrected bodies at workspace revision `50c02815…`.
- `tools/check_spain_parties.py` resolved its registry from four files, so the helpers the original S12 call sites introduced (`spain_push_crown`, `spain_loyalty_gain_small`, `spain_restoration_cortes_live`) were reported as unknown effects and `.tools/tests/test_spain_cortes_postwar_bills.py` exited 1 with 3 failures in 217 checks. That registry gap was outside S12a's reservation and is the first item of the S12b correction below; it is now closed.

## The S12b finishing correction

Card `t_00b07993` closed two things S12a left open: the same implicit-comparison defect in the two blocks S12a did not own, and the party-reference checker's four-file registry, which made the delivered turno package red before integration.
Tuning, identifiers, costs, AI weights, decision and event content, localisation keys and chapter behaviour are unchanged.

| Where | Before | After |
| --- | --- | --- |
| `spain_government_strain`, `spain_cortes_parties.txt:233` | `spain_government_majority value = 0 }` | `spain_government_majority value = 0 compare = equals }` |
| `spain_hold_election`, incumbent loss, `:280` | `spain_government_majority value = 0 }` | `spain_government_majority value = 0 compare = equals }` |

What the omission did.
`spain_government_strain` is called by the five coalition decisions, `SPR_drop_the_coalition` and `spain_bill_penalise_government`, and it charges `minority_stability` (-0.02) and `minority_coup` (+3) to **every** government, a 245-seat majority included, because the implicit test is `0 >= 0`.
The incumbent-loss `OR` in `spain_hold_election` is the other half: with the majority arm always true, every government lost `incumbent_loss` (-2) support across the four incumbent blocs at every election, and the stability arm never decided anything.
The repair is the comparator and nothing else, so the election weights, the random wave, the recipients and magnitudes, the `election_unrest_threshold` and the recount order are exactly as S12 delivered them.

The local precedent is `spain_government_recount`'s own zero test, which already stated `compare = equals`; the vanilla precedent is `common/scripted_effects/GRE_scripted_effects.txt:23-25`, which compares a counter to `0` the same way, inside a `NOT` as well.
The documentation is the same pair cited above: the offline wiki's `Data structures` `check_variable` row, which names `greater_than_or_equals` as the default, and `documentation/triggers_documentation.md:2110-2132`.

`tools/check_spain_parties.py` now reads `common/scripted_effects/spain_campaign_effects.txt` and `common/scripted_triggers/spain_campaign_triggers.txt` for their declarations only, alongside the bills and hemicycle files it already read.
Both are registry-only for the same reason: the Cortes government call sites use helpers those files define, and their own call sites reach further helpers, so scanning them would report another file's dependency as this checker's finding.
No symbol was silenced and no file was skipped; the checker still resolves every `name = yes` call against one registry, and a withdrawn definition is still a finding.

Evidence, all of it source-level:

- `python .tools/tests/test_spain_turno.py` → 128 checks, 0 failures (109 before this card, all preserved); `--detail` → 128 `ok` lines and exit 0. Nineteen checks are new: the two source assertions, six on the strain observation, five on the incumbent-loss matrix, and six mutant controls.
- The strain observation runs the shipped effect twice. A bloc of zero majorities pays `-0.02` stability and `3` coup pressure; a genuine majority reached the way the machine reaches one (two encasillados, 245 benches) pays `0` and `0`.
- The incumbent matrix evaluates the shipped `OR` at the four combinations: a stable majority fires `False`; an unstable majority, a stable minority and an unstable minority all fire `True`. The stability arms are built from `election_unrest_threshold` itself, not from a literal.
- `test_residual_comparisons` reverts one comparison at a time and asserts the other still holds. Reverting the strain equality alone charges a genuine majority `-0.02`/`3`; reverting the election equality alone makes a stable majority fire the incumbent loss. Both are rejected, and each mutant leaves the other block's checks passing, so the two tests cannot pass on one repair.
- `python tools/check_spain_parties.py` → exit 0, `registry files: 6, decisions: 17, localisation keys: 49`, `no dangling references`.
- `python .tools/tests/test_spain_cortes_postwar_bills.py` → 227 checks, 0 failures plain and `--detail` (217/3 before); its original injected-unknown and deleted-definition controls still fail as required, and three new controls prove the campaign-effects entry, the campaign-triggers entry and a missing registry input are each load-bearing.
- Regressions on the same tree: recount 215/0, runtime 113/0, restoration loyalty 146/0, hemicycle builder 69/0.
- `hoi4.source_lookup` before the edit returned `spain_government_strain` at lines 231-238 with the bare `value = 0 }` and `spain_hold_election` at 247-294 with the same bare test inside its `OR`, at workspace revision `50c02815…`; after the edit both bodies return with `compare = equals` at lines 233 and 280, at revision `ea7dfb2e…`, with `referencesComplete: false` and 2570 workspace-wide unresolved references unchanged.
- `hoi4.script_validate` on the file before and after: `SCRIPT_CHECK_PARTIAL`, 0 findings, 332 commands checked, `parametersChecked = false`, 193 argument blocks unchecked across 11 unknown-scope roots, docs revision `9227e238…`. Identical both times — the route does not evaluate `check_variable`, so it is coverage, not proof of either comparison.

## What only a launch can confirm

The seat table, the party the turno pays, the monthly minority test, the government strain, the incumbent-loss test, the crisis flag, the rot reader, the localisation keys and the mission block are proven by source simulation (`.tools/tests/test_spain_turno.py`), by `hoi4.decision_inspect` on `SPR_ministerial_crisis` (available false at 129 seats, true at 245) and by `hoi4.script_validate`.
Source simulation is not engine proof: it executes the same script the engine loads, but nothing in it proves the engine's own `check_variable` resolution, the panel repaint on the same day, the mission appearing in the category strip within a day of the flag being set, the hemicycle redraw reading the new benches, or the mission timer starting on the day the game activates it.
The engine's `greater_than_or_equals` default and the two corrected comparisons are source-documented and source-simulated; no launch has shown them resolve in a running game.

## Needed icons

No artwork was added and none is required for the slice.
The mission uses `generic_political_address` and the three routes use `generic_political_discourse`, `generic_political_rally` and `generic_monarchy`, all vanilla.
If the routes are later given dedicated art, the icons belong in the existing Spain decision block of `interface/endsieg_spain_icons.gfx` and must be requested with stable sprite names before any image is produced.

## Known limitations

- The transfer names four fixed donors. If the governing party is itself one of them, its net gain is smaller than the transfer (it both gains 18 and loses its donor share): a Liberal government nets 11 raw support and a Socialist government 16, while the chamber still totals 400. The table above is the monarchist case, the one the clean Restoration state produces; a route that wanted a governing donor to keep the whole transfer would have to resolve the donor list against the governing party.
- `crisis_timeout_days` exists both as a constant and as a decision-file macro because native timer fields take literals. They are asserted equal by the test and must be retuned together.
- The emergency decree path is one-way: `spain_restoration_decree_rule` is set and no route clears it in this slice.
  It does **not** hide the route: `SPR_royal_decree`'s `available` block carries a second `custom_trigger_tooltip` gated on the flag, so the route stays on the board greyed with `spain_royal_decree_inforce_tt` instead of vanishing without explanation.
- The comparison class this card closed still appears in three files it does not own: `common/decisions/spain_cortes.txt:345` and `events/spain_cortes_bills.txt:420` weight an `ai_chance` modifier on `check_variable = { var = spain_government_majority value = 0 }`, and `common/national_focus/spain_republic.txt:1180` gates a focus's `available` block on the same test.
  All three therefore read as true for every government — an AI weight that always applies, and a focus availability gate that never blocks — and each needs its own card.
  The two `value = 1` tests in `common/scripted_localisation/spain_cortes_panel.txt:171,189` are the boolean form of the same reader and are correct as written, because the majority is `0` or `1` and `1 >= 1` is exactly "has a majority".
