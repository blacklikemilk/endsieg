# I7 handoff - Iran continuity gate and real readers for unread flags

Card: t_70883498 (endsieg-developer). Baseline: `ad0169dd1c6f67b4b8904f9f1d90f73f3f47754a`
(I6 integrated, QA PASS). Branch: TeknoDev-Branch. No commit: Director integrates.

## Round 2 correction (QA round 1 rejection `i7-german-mission-visible-or-tautology`)

Round 1 shipped `iran_invite_german_mission.visible` with the outer conjunct
`date > 1934.12.31` and an `OR` whose first disjunct repeated the same date test.
On every date the block admitted, the OR was already satisfied by that date, so the
three refusal flags decided nothing, and the reachability claim below was false.
The block now holds no outer date conjunct above 1935: the `OR` is the only place the
lower bound appears, so the three refusal flags genuinely decide the pre-1935 window.
The check that missed it was textual (flag name present in `visible`).
The test now *evaluates* the block under nine declared flag and date states, including
the pre-1935 rows, and rejects the exact round-1 text with 3 wrong states (1919 refused,
1932 deflected, 1932 Soviet refused).
Mutant 5 (the three flag disjuncts deleted from the OR) is rejected with the same 3.

## What was wrong

Two findings from the accepted I1/I3 audits met in the same place.

1. `common/scripted_triggers/iran_continuity.txt` only read flags the 1910-18 chapter
   sets. The 1919-25 settlement, coup, armistice, conference, northern, oil and
   great-game outcomes were written by `events/iran_campaign.txt` and read by nothing.
   The era boundary therefore saw how the previous chapter *began*, never how it ended.
2. Three triggers in that file had **no live reader at all** (`iran_path_intact`,
   `iran_path_armed_neutrality`, `iran_path_humiliated`). MCP `source_lookup` before the
   repair: 1 definition, 0 references for `iran_path_intact`.

## What changed

### `common/scripted_triggers/iran_continuity.txt`

Ten route triggers now fold in the later chapters' outcomes (18 flags, all previously
written and never read):

| trigger | flags added | set by |
| --- | --- | --- |
| `iran_path_majlis` | `iran_shah_with_parliament`, `iran_assembly_endorsed`, `iran_coup_resisted`, `iran_conference_petition` | `iran_campaign.17.a`, `.18.a`, `.50.b`, `.29.a` |
| `iran_path_court` | `iran_shah_with_court`, `iran_assembly_managed` | `.17.b`, `.18.b` |
| `iran_path_army` | `iran_coup_settled`, `iran_tribes_disarmed` | `.50.a`, `.54.a` |
| `iran_path_tribal` | `iran_congress_declared`, `iran_tribes_negotiated` | `.52.a`, `.54.b` |
| `iran_path_armed_neutrality` | `iran_neutrality_proclaimed` | `.27.a` |
| `iran_path_humiliated` | `iran_armistice_accepted` | `.28.b` |
| `iran_path_oil_concession` | `iran_oil_settlement` | `.55.a` |
| `iran_path_oil_national` | `iran_oil_dispute` | `.55.b` |
| `iran_path_entente` | `iran_withdrawal_guaranteed`, `iran_gulf_arbitration_accepted` | `.61.a`, `.64.a` |
| `iran_path_germany` | `iran_german_mission_accepted`, `iran_agreement_transit_axis` | `.70.a/.c`, `.74.c` |

`iran_path_intact` is now the negation of `iran_path_humiliated`. It used to also require
`iran_path_armed_neutrality`, so a Persia that permitted transit, or fought alongside a
patron, and lost no frontier was classified as neither intact nor humiliated: the
boundary could not tell the routes apart. The trigger now answers one question ("did the
war leave Persia whole?"), and neutrality is its own path.

`iran_path_foreign_count` is unchanged and is **not** given a reader this pass: its only
inputs are `IR1_entente_understanding` and `IR1_german_opening`, which stop moving in
1918, so no 1919+ object can read a value that is already fixed. It is left in place for
the 1914-18 owner rather than deleted here.

### `common/decisions/iran_great_powers.txt` (readers)

| decision | block | new condition | reachable because |
| --- | --- | --- | --- |
| `iran_invite_german_mission` | `visible` | `NOT iran_british_demand_paid`, `NOT iran_soviet_demand_paid` | `.71.a`/`.72.a` fire from the monthly `iran_great_game_tick` at standing >= 70, then the mission is never offered again |
| `iran_invite_german_mission` | `visible` | the `OR` is the only lower date bound in the block: `OR = { date > 1934.12.31, iran_british_demand_refused, iran_british_demand_deflected, iran_soviet_demand_refused }` | `.71.b`, `.71.c`, `.72.b` set the refusal flags from the monthly `iran_great_game_tick`, which runs from campaign start, so a government that told a patron no sees the German option before 1935 instead of waiting for the calendar |
| `iran_crisis_anglo_persian_ratify` | `visible` | `NOT iran_path_armed_neutrality` | a neutrality route that took `IR1_guarded_neutrality` (`PER_neutral_1914`) or `.27.a`, inside the 1919-21 crisis window |
| `iran_crisis_anglo_persian_reject` | `visible` | `iran_path_intact` | a Persia carrying an Ottoman frontier, refugee administration or grain requisition loses the refusal and the draft imposes itself on timeout |

Conditions were deliberately put in `visible`, not `available`, so no new raw-flag
requirement tooltip is created (I8 owns tooltip localisation). MCP `script_validate` on
this file reports the same four pre-existing unlocalised-flag warnings as before the
change (`iran_rule_by_decree`, `iran_agreement_german_mission`,
`iran_german_mission_withdrawn`, `iran_allied_demand`) and none from the new conditions.

### `events/iran_campaign.txt` (readers)

* `iran_campaign.29` (peace conference, fired from an `iran_ww1` focus): both options now
  carry triggers. Petitioning requires "pressed claims at the armistice OR did not sign
  it"; boycotting requires "did not press claims OR signed it". No flag state leaves the
  event with zero options - checked for all four combinations.
* `iran_campaign.76.b` (defy the Allies over the German mission) requires
  `NOT iran_agreement_transit_axis`: a government that already handed the railway to
  Berlin cannot plead that the mission is only technical.
* The `.55` comment no longer says `iran_oil_settlement` "nothing reads" - it is read.

## Test

`.tools/tests/test_iran_flag_readers.py` (new, gitignored directory, needs `git add -f`):

```
python .tools/tests/test_iran_flag_readers.py --detail
21 checks, 0 failures
```

* the German window is evaluated, not grepped: nine declared flag/date states, including
  the pre-1935 refusal rows that a presence check cannot distinguish from a no-op;
* baseline `ad0169dd1`: 10 gate defects, 4 intact defects, 3 decision defects, 5 window
  defects, 2 event defects - the test fails on the pre-repair source;
* the exact round-1 text (outer `date > 1934.12.31` restored above the `OR`) is rejected
  with 3 wrong states, so the defect QA found cannot ship green again;
* mutant control, 5 mutants rejected: gate without `iran_oil_dispute`, intact restored to
  the baseline body, decision without the Soviet bill, event without the transit guard,
  German window without the three refusal disjuncts (3 wrong states);
* preservation: the six decision costs/AI factors and four events' options are unchanged;
* no permanent treaty gate: the owned files never mention `iran_decree_treaty`, the
  negotiations file still sets it as a timed flag exactly 4 times and never bare.

## Checks run

| check | result |
| --- | --- |
| `python .tools/tests/test_iran_flag_readers.py` | 21 checks, 0 failures, EXIT=0 |
| `python tools/iran_audit.py --game <HOI4>` | Clean, 0 missing focus keys, 0 unresolved sprites |
| `python tools/iran_reference_check.py --game <HOI4>` | Every reference resolves |
| MCP `script_validate` iran_continuity.txt | 0 findings, 92 commands, `unresolvedCount` 0, `argumentBlocksUnchecked` 1, `SCRIPT_CHECK_PARTIAL` (14 unknown-scope roots: a trigger file declares no scope) |
| MCP `script_validate` iran_great_powers.txt | 0 errors, 4 pre-existing warnings, 107 commands, `unresolvedCount` 0, `argumentBlocksUnchecked` 16, `SCRIPT_CHECKED` |
| MCP `script_validate` events/iran_campaign.txt | 0 findings, 378 commands, `unresolvedCount` 0, `argumentBlocksUnchecked` 95, `SCRIPT_CHECKED` |
| MCP `event_inspect` scan events/iran_campaign.txt | `EVENT_INSPECTED_PARTIAL`, 0 blocking diagnostics, 2414 diagnostics workspace-wide, 9315 events |
| MCP `decision_inspect` inventory | 4353 decisions, 0 unresolved definitions, 1366 categories |
| MCP `source_lookup` `iran_path_intact` | 1 definition, 1 reference (`iran_crisis_anglo_persian_reject`, line 189) - was 0 |
| MCP `source_lookup` `iran_path_majlis` | 1 definition, 13 references (2 focuses, 5 decisions, 2 events, effects) |
| MCP `source_lookup` on a country flag (`iran_british_demand_paid`, `iran_armistice_accepted`) | returns 0 definitions and 0 references: country flags are not indexed symbols. Flag liveness was proved by the test's writer/reader scan instead. |
| MCP `decision_inspect` inspect | **unavailable**: `PROBABILITY_GAME_VERSION_UNSUPPORTED`, adapter `Operation Postern 1.19.2.0 (d245)` vs installed `1.19.3.0.c01a (5632)` |
| MCP `source_lookup` `iran_invite_german_mission` | 1 definition, 0 callers; the returned text is the repaired `visible` block, so the route's own source is what is quoted |
| MCP `source_lookup` `iran_british_demand_refused` | 0 definitions and 0 references: country flags are not indexed symbols, so flag liveness is proved by the test and the probe |
| probe `i7_r2_probe.py` | shipped source 0 wrong states, round-1 text 3, refusal-disjunct mutant 3 |

## Known route outcome (QA round 1, non-blocking)

`IR1_neutrality_declaration` -> `iran_campaign.27.a` and `IR1_armistice_watch` ->
`iran_campaign.28.b` are on separate branches with no mutual exclusion, so one state can
hold both `iran_neutrality_proclaimed` and `iran_armistice_accepted`.
On that state the ratify decision (`NOT iran_path_armed_neutrality`) and the reject
decision (`iran_path_intact`) are both invisible, and the 300-day
`iran_crisis_anglo_persian_begin` timeout imposes the draft, which the ratify comment
already allows for.
Deciding whether neutrality should keep the refusal is a design question for the
interwar owner, not a reader this card can fix without inventing a new path rule.

## Not verified

* No HOI4 launch. Decision visibility, option visibility and the gate are source facts
  under declared flag states, not engine observations.
* Whether the AI values the newly visible German mission the way `ai_will_do = { factor = 3 }`
  intends, and whether a player notices the decision appearing in 1925, are in-game
  questions.
* `event_inspect` and `script_validate` are PARTIAL for the event and trigger files (no
  declared scope); no route proves cross-file flag liveness in the engine.

## Allowlist - flags that stay terminal, and why

The pre-repair scan found 206 Iran flags written and never read. 18 now have readers.
The rest stay terminal for one of these reasons:

1. **Focus-completion mirrors** (`iran_road_programme`, `iran_steel_mill`,
   `iran_air_force`, `iran_land_registry`, `iran_conscription_law`, ... roughly 120 of the
   206). The flag duplicates `has_completed_focus`, which is what any future content
   should test. Adding a flag reader would create a second, weaker source of truth.
2. **Narrative terminal markers with no downstream content**: `iran_thirty_five_named`,
   `iran_name_adopted`, `iran_campaign_concluded`, `iran_postwar_programme`,
   `iran_conference_boycott`, `iran_wartime_cabinet`, `iran_wartime_majlis_cabinet`,
   `iran_succession_prepared`, `iran_succession_managed`, `iran_northern_compromise`,
   `iran_northern_centralization`. Their only natural readers are 1936-tree focus
   prerequisites, and focus rewrites are out of scope for this card; the interwar/ww2
   owner should take them.
3. **Flags whose reader lives in a file this card does not own**: `iran_shatt_settled`,
   `iran_shatt_refused`, `iran_gulf_arbitration_refused`, `iran_guarantee_refused`,
   `iran_anglo_persian_rejected`, `iran_german_credit`, `iran_transit_permitted`. The
   honest reader is one of the four Pahlavi agreement decisions or the Crown/Majlis
   decisions, both owned by I6 (`iran_foreign_agreements.txt`,
   `PER_crown_and_majlis.txt`) and explicitly excluded here.
4. **Duplicate state**: `iran_transit_permitted` (1914-18 transit) is superseded by
   `iran_agreement_transit_allied`, which `iran_influence_tick` already reads;
   `iran_public_granaries`, `iran_defensive_mobilization` and `iran_tehran_declaration`
   are re-set by `iran_initialize_campaign` for later starts, so a reader would fire for
   every 1941+ start.
5. **Chapter-1 military/programme flags** (`iran_security_programme`,
   `iran_treasury_programme` and the rest of the "programme" family) that already gate
   decisions: they are read, they were only listed as unread by the older per-chapter
   scans.

## Findings for other owners (not edited here)

* `common/decisions/iran_great_powers.txt` carries four pre-existing
  `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` warnings in `available` blocks (listed above). I8
  owns tooltip localisation; I did not add a fifth.
* I6 QA's seven unlocalised-flag warnings on the four Pahlavi agreement requirements in
  `common/decisions/iran_foreign_agreements.txt` are unchanged and still belong to that
  owner.
* `iran_path_foreign_count` still has no consumer. Its input variable is written only by
  two 1914-18 focuses; the 1914-18 owner should either retire it or give it a ww1-era
  reader.
