# I5 handoff: the two interwar Gulf naval rewards moved to a coastal state

Task t_fb63882e (I5), era 1919-1935, branch TeknoDev-Branch, base commit `f8f9225b048874109ff965654c9fb7fa973df0cd`.
Card-approved narrow correction of residual R1 from I0 t_369b0c51: both rewards targeted state 411, which has no coastal province.
The Developer made no commit; Director integration follows independent QA.
No branch change, launch, artwork or layout change occurred.

## Changed files

| File | Change |
| --- | --- |
| `common/national_focus/iran_interwar.txt` | Two `completion_reward` construction lines only: `IR2_gulf_claims` line 1092 and `IR2_navy_gulf` line 1954 |
| `localisation/english/iran_interwar_l_english.yml` | `IR2_navy_gulf_desc` only, line 165 |
| `.tools/tests/test_iran_gulf_rewards.py` | New durable static test with pinned pre-repair mutant controls for the focus file and the description |
| `docs/plans/iran_1910_1945/subagent_handoffs/gulf_reward_coast.md` | This handoff |

`git status` before the focus write showed `common/national_focus/iran_interwar.txt` clean and only Spain files modified by another agent.
Before the localisation write, `git status -- localisation/english/iran_interwar_l_english.yml` showed it clean as well.
`git diff --stat` now reports two changed lines in the focus file (one per focus) and one in the localisation file.
Director's 2026-10-26 amendment added the localisation key to this card, because the repaired reward made the old description's city false.

## Before and after

Before, from the pinned base revision:

```
			set_country_flag = iran_gulf_claims
			add_war_support = constant:iran_story.war_support_gain
			411 = { add_building_construction = { type = naval_base level = 1 instant_build = yes } }
```

```
			411 = { add_building_construction = { type = dockyard level = 1 instant_build = yes } }
			navy_experience = constant:iran_story.navy_experience
			set_country_flag = iran_gulf_squadron
```

After:

```
			set_country_flag = iran_gulf_claims
			add_war_support = constant:iran_story.war_support_gain
			413 = { add_building_construction = { type = naval_base level = 1 instant_build = yes province = 5005 } }
```

```
			413 = { add_building_construction = { type = dockyard level = 1 instant_build = yes } }
			navy_experience = constant:iran_story.navy_experience
			set_country_flag = iran_gulf_squadron
```

Every other field of both focuses is byte-identical: id, icon, x/y, prerequisite, allow_branch, available, cost, search_filters and ai_will_do.
The reward amount, `instant_build`, the country flags, war support and navy experience are unchanged.

Localisation, line 165:

```
- IR2_navy_gulf_desc: "A dockyard is built at Bandar Abbas and two sloops are ordered for the customs service. ..."
+ IR2_navy_gulf_desc: "A dockyard is built on the Khuzestan coast and two sloops are ordered for the customs service. ..."
```

The rest of the sentence, the title `IR2_navy_gulf`, `IR2_gulf_claims` and `IR2_gulf_claims_desc` are untouched.
The test proves that by comparing every other key in the file against the pinned base revision.

## Why the description had to move with the reward

The reward now builds in state 413, Khuzestan.
Bandar Abbas is province 7982, which vanilla localisation renders as `Bandar e'Abbas` in `<game>/localisation/english/victory_points_l_english.yml:779`, and 7982 belongs to state 412 (Fars), not 413.
The description therefore named a port in a different province of a different state, and leaving it would have made the text contradict the tooltip.
"On the Khuzestan coast" changes the location and nothing else.

## Map evidence

`map/definition.csv` (column 6 is the coastal flag) marks all nine provinces of state 411 landlocked: 1963, 2026, 4928, 4983, 5067, 8031, 8074, 10828, 12756 are all `false`.
State 413 `history/states/413-Khuzestan.txt` owns 1922, 5005, 5089, 7953; 5005 (desert) and 5089 (mountain) are `true`.
State 412 `history/states/412-Fars.txt` owns 7982 among its nine provinces, which is where the city the old text named actually is.
The state file's name is `STATE_413` and vanilla `localisation/english/state_names_l_english.yml:557` renders it as Khuzestan.
Note for future readers: `history/states/411-Hormozgan.txt` is a misnomer; its own header comment says `# Isfahan` and vanilla localisation renders `STATE_411` as Isfahan, so the file name is stale, not the state id.

## Why the naval base carries a province selector and the dockyard does not

`common/buildings/00_buildings.txt:150` gives `naval_base` `only_costal = yes` and `level_cap = { province_max = 10 }`, so it is a provincial building and needs a province.
The offline wiki `Effects`, row `add_building_construction` (line 3614) states that `province = <id>` selects the exact province, that provincial buildings must be built inside the containing state's scope, and that the effect does nothing in a country scope.
Vanilla precedents use both forms: `common/national_focus/argentina.txt:3919` and `:3940` use `province = <id>` for `naval_base`, and `common/national_focus/afghanistan.txt:2180` and `common/factions/goals/faction_goals_medium_term.txt:3670` use the `province = { all_provinces = yes limit_to_naval_base/coastal = yes }` filter.
The filter form was rejected here on purpose: `level = 1` per matched province would add a full level to both 5005 and 5089 and double the reward, so the exact province is the only form that keeps the reward amount.
`common/buildings/00_buildings.txt:225` gives `dockyard` `level_cap = { shares_slots = yes state_max = 20 }` and `only_costal = yes`, so it is a shared-slot state building with no province argument.
Vanilla `common/national_focus/argentina.txt:3908` builds a dockyard with the plain state scope, which is the form used here.

## Slot and ownership assumptions

State 413 is `state_category = rural`; the installed `common/state_category/rural.txt` gives `local_building_slots = 2`.
The state history contains `infrastructure = 3` (state_max, not slot shared) and `naval_base = 1` at province 5005 (provincial), so zero of the two shared slots are occupied and a level-1 dockyard fits.
`common/terrain/00_terrain.txt` sets no `buildings_max_level` for `dockyard` or `naval_base` in desert or mountain, so terrain does not cap either building.
Adding a level to 5005 raises the existing base from level 1 to level 2, well under `province_max = 10`.
Ownership: state 413 starts owned by PER, which is what the reward needs, and so does 411.
The dated `1943.1.1 = { owner = ENG controller = ENG }` block in the same state file is bookmark initialisation, not a scheduled transfer: per `paradox_wiki/Bookmark modding - Hearts of Iron 4 Wiki.md:163` a state history date block executes only when the chosen start date is strictly later than that date, so a continuous 1919 or 1936 campaign keeps 413 Persian and a post-1943 bookmark start would hand the construction to the controller.
Independent QA resolved that hypothetical exposure: `iran_campaign.txt:172` loads the interwar tree only before 1936, so a post-1943 bookmark does not offer these interwar focuses.
No ownership gate or reward requirement was changed.

## Localisation

All four keys live in `localisation/english/iran_interwar_l_english.yml`:

| Key | Line | Text | State |
| --- | --- | --- | --- |
| `IR2_gulf_claims` | 102 | Claims in the Gulf | unchanged |
| `IR2_gulf_claims_desc` | 103 | "... A station on the coast, a few vessels and a customs service turn a diplomatic note into a presence." | unchanged, names no province |
| `IR2_navy_gulf` | 164 | The Gulf Squadron | unchanged |
| `IR2_navy_gulf_desc` | 165 | "A dockyard is built on the Khuzestan coast ..." | changed under the amendment |

`IR2_gulf_claims_desc` needed no edit: it already described a coast station without naming a city.
`IR2_navy_gulf_desc` named Bandar Abbas, which is in state 412, so the text and the repaired build disagreed; the card's amendment resolved that by naming Khuzestan instead.
Director's amendment covers this key only, and the test enforces that no other key in the file changed.

Rules applied, from `paradox_wiki/Localisation - Hearts of Iron 4 Wiki.md:59-72` read through `hoi4.reference_read`: UTF-8-BOM, an `l_english:` first line, a key of letters, digits, underscores, dots and hyphens, and a single-line value in straight quotes.
The version suffix is optional there; this repository writes unversioned keys, so the edited line keeps that form and the test rejects a `:0`.
The file still starts with the BOM, has 223 lines, LF endings, 221 parsed keys and no non-ASCII character, checked before and after the edit.
Only `localisation/english` exists for Iran interwar content: `braz_por`, `english_tag`, `french`, `german`, `polish`, `russian` and `spanish` have no such file, and that gap is recorded rather than invented.

## Durable test

`.tools/tests/test_iran_gulf_rewards.py` parses the shipped focus file, both state files, `map/definition.csv`, the building definitions, the state category and the localisation file, and it checks target state, coastal province membership, the province selector form, level, `instant_build`, slot budget, province cap, ownership, the preserved reward lines and the description.
It also compares the whole focus file and every other localisation key against the pinned base revision, and fails if anything outside the two focus blocks or the one description changed.
The pre-repair revision is read with `git show f8f9225b0:<path>`, and both the focus text and the description must be rejected by the same checkers, which is the mutant control.

Actual output, from the repository root:

```
python .tools/tests/test_iran_gulf_rewards.py
note  only localisation/english has an Iran interwar file; the other seven project languages have none, recorded rather than invented
24 checks, 0 failures
EXIT=0
```

```
python .tools/tests/test_iran_gulf_rewards.py --detail
  ok  [map] state 413 exists with 4 provinces
  ok  [map] state 413 owns at least one coastal province — [5005, 5089]
  ok  [map] state 411 is the landlocked state the rewards left — [1963, 2026, 4928, 4983, 5067, 8031, 8074, 10828, 12756]
  ok  [map] the port province 5005 is coastal
  ok  [map] the fallback coastal province 5089 is coastal
  ok  [map] the removed location 7982, Bandar e'Abbas, is a province of state 412 — [1889, 4959, 4966, 7982, 8117, 10797, 10881, 12832, 13312]
  ok  [map] the removed location 7982 is not a province of state 413
  ok  [map] state 413 uses the 'rural' category with 2 shared slots — .../common/state_category/rural.txt
  ok  [rewards] both rewards parse and land on a coastal state
  ok  [preserved] nothing outside the two repaired focus blocks changed
  ok  [preserved] focus count unchanged — 139 vs 139
  ok  [preserved] IR2_gulf_claims keeps every non-construction field
  ok  [preserved] IR2_gulf_claims still carries exactly one state relation — [413]
  ok  [preserved] IR2_navy_gulf keeps every non-construction field
  ok  [preserved] IR2_navy_gulf still carries exactly one state relation — [413]
  ok  [mutant] the pre-repair source fails the check
  ok  [mutant] the pre-repair source is rejected for state 411 — IR2_gulf_claims still builds in state 411, which has no coastal province; ...
  ok  [mutant] the pre-repair source is rejected for the missing province selector — IR2_gulf_claims gives no province selector; a naval base is a provincial building, so the state scope alone does not place it; ...
  ok  [localisation] the focus description matches the repaired build
  ok  [localisation] the description is the only localisation value that changed — []
  ok  [localisation] localisation key count unchanged — 221 vs 221
  ok  [localisation] the description names the state the reward builds in — A dockyard is built on the Khuzestan coast and two sloops are ordered for the customs service. ...
  ok  [loc-mutant] the pre-repair description fails the check
  ok  [loc-mutant] the pre-repair description is rejected for the port it named — IR2_navy_gulf_desc:165 names 'Bandar Abbas', which is province 7982 in state 412, not the state the dockyard is built in; IR2_navy_gulf_desc:165 does not name Khuzestan, the state the reward builds the dockyard in
```

Additional one-off discrimination probe, run outside the repository and not part of the suite, confirms the checker rejects each wrong shape independently: a non-coastal province (1922), a missing selector, the other coastal state (412), a raised dockyard level and a changed flag were all rejected with their own message.
A second probe covers the description half: the shipped text passes, and a text that also names Bandar Abbas, one that names the old port only, one that names no state, one that drops the dockyard, a file without the BOM, a key with a `:0` version suffix and a line with an unterminated quote are each rejected with their own message.

At implementation delivery, `.gitignore:5` ignored the whole `.tools/` folder under the HOI4 Mod Setup managed rules, `git ls-files .tools` returned zero files, and the Spain counterpart was untracked for the same reason.
Director integration includes this exact test with `git add -f`, without changing `.gitignore` or sweeping in other tooling.

## MCP evidence

All routes ran with `workspaceId: "current"`.

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.reference_context` | surface `focus`, question about focus rewards that build in a state | ok, 12 sections, `omittedSources: []`, `missing: []`, script_doc unavailable |
| `hoi4.reference_search` | `add_building_construction province naval_base`, limit 8 | ok, hit id `0f817f631ed352b778d103b6ff8f00fabc89044d8c8dabb5746c943a3465ecea` |
| `hoi4.reference_read` | that id, revision `997ddb09...96aa0c`, source `wiki` | the `add_building_construction` argument table at line 3614 |
| `hoi4.reference_search` | `localisation key unversioned l_english file format quotes` | ok, 38 hits, best hit `Localisation - Quick checklist` (`9ff4fd1c...a53ffe6`) |
| `hoi4.reference_read` | that hit, revision `1a8f7236...cc9d3a064`, lines 59-72 | BOM, `l_english:` header, key alphabet and single-line quoted value rules; a first request at line 55 returned `REFERENCE_POSITION_OUTSIDE_SECTION` and the corrected retry at line 59 succeeded |
| `hoi4.source_lookup` | symbol `add_building_construction` | 0 definitions and 0 references; native commands are not indexed, so vanilla precedent was read directly instead |
| `hoi4.source_lookup` | symbol `IR2_navy_gulf_desc` | 0 definitions and 0 references; localisation keys are not indexed either (`unresolvedReferenceCount` 2566), so the file was read directly |
| `hoi4.script_validate` | path `common/national_focus/iran_interwar.txt`, before and after both edits | `valid: true`, 956 commands, 10 findings (all pre-existing `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` at lines 50, 70, 228, 249, 360, 379, 480 twice, 505, 522), `unresolvedCount: 0`, `argumentBlocksUnchecked: 175` |
| `hoi4.focus_inspect` | `treeId: iran_interwar`, before and after | 139 focuses, validation passed, 0 blockers, `resolvedTitleCount` 139, layoutHash `8e91e790309c0326b58de2b9d8a2a8bcc0d0a76fd1f2e131baa82839b20bdb0f` both times, `nodeIntersectionCount: 0` |
| `hoi4.focus_render` | `relativePath: common/national_focus/iran_interwar.txt`, `treeId: iran_interwar`, crops for the two focus ids | `FOCUS_RASTERIZED`, 12448x2092, same layoutHash, 18 pre-existing layout warnings, none for these two focuses; the render indexed `mod:localisation/english/iran_interwar_l_english.yml` and reported no missing key for `IR2_navy_gulf_desc` |

Resources: post-edit focus inspect `hoi4-agent://workspace/endsieg/artifact/4e20d6d3426b08850511b0c475d5ba47bf8528d19e58eca5a121850b9703adfe/b39f268575de642a05e7e03bdc30ad956378bbe5b6247e2bff13dce5f9d63310/focus-inspect.e9e1a728f4ae0bbe.json`; render `hoi4-agent://workspace/endsieg/artifact/f017ef993427cde665d5bb027d3b5d61b81ae9b37341ad644fe752c050aaa7b8/47cdf2070936cc4f9b9cb2f75ec47b932c212a8da350a406a8c416d4e1efbba0/iran_interwar.focus.png` plus its json, svg, html and source-map companions.

`script_validate` reports `parametersChecked: false` and 175 unchecked argument blocks, so it does not resolve the `province = 5005` argument itself; that argument is covered by the wiki table, the two vanilla precedents and the test, not by the validator.
No MCP route parses localisation values, so the description is covered by the wiki localisation rules, the pinned-file comparison and the durable test instead of a validator.
One corrected retry was needed, on the reference read only; no route reported a blocker.

## Repository audits re-run

`python tools/iran_audit.py`: 328 focuses, 171 events, 112 decisions, 34194 localisation keys, 0 missing focus keys, and one problem that is not this card's: 16 `PER_*` decision names with no localisation, first of them `PER_boost_stability` from `common/decisions/PER.txt:779`.
That finding cannot come from this card: `check_loc` in `tools/iran_audit.py:263` compares `decision_ids()` from the Iran decision files against the loaded localisation keys, this card modified no decision file, changed one existing focus description value without adding or removing a key, and the same run reports 0 missing focus keys with the key total unchanged at 34194.
It reproduces at base commit `f8f9225b0` by construction and it is outside the assigned files.

`python tools/iran_reference_check.py --game "<vanilla>"`: 327 event references, 155 idea references, every reference resolves.

## Known residuals not fixed here

1. `IR2_gulf_harbour_project_desc` at line 125 still opens with "Bandar Abbas is dredged", while that focus builds infrastructure in state 411 (Isfahan), not in the port's state.
   It is a different focus, a different reward and outside this card's ownership; recorded for a Director-owned card rather than edited.
2. The hypothetical 1943 bookmark ownership exposure was resolved by independent QA: that bookmark does not load the pre-1936 interwar tree.
3. The ignored test is included through an exact-path force-add at Director integration, not a broad ignore-rule change.

## Not verified

No game was launched, so the click-to-construction behaviour, the produced dockyard and naval base on the map, the production-menu appearance of the new building and the in-game focus tooltip text are unproven by this card and remain a user-side live check.

## Disposition

Implemented with evidence inside the assigned ownership, including Director's single-key localisation amendment.
Independent QA passed on native run 57 of `t_fb63882e`.
QA re-read the map, state/building definitions and vanilla syntax, reproduced all 24 suite checks and independently rejected 15 reconstructed invalid mutations with zero mismatches.
QA independently ran focus inspection/render, script validation, map lookup, source lookup and reference search, retaining the argument-coverage and no-launch limits above.
Director re-read the exact two-line focus diff and single-key localisation diff and re-ran the 24-check suite before integrating only this card's four owned files.
The actual click-to-construction result, production-menu appearance and live tooltip remain unverified; static acceptance is not engine proof.
