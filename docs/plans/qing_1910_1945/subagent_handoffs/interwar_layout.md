# qing_interwar layout repair — two shelves instead of a lattice

Owner: endsieg-developer, card `t_7b3ac7a0`, 2026-10-27.
Owned writes: `common/national_focus/qing_interwar.txt` (focus `x`/`y` values and the overview layout comment only), `.tools/tests/test_qing_interwar_layout.py` (new), `docs/plans/qing_1910_1945/current_report.md` (two factual lines plus a source note), this handoff.
No gameplay field, icon, prerequisite, mutual exclusion, cost, AI weight, idea, spirit, localisation string, sprite or interface file was touched.
Nothing staged, nothing committed, no branch change, no game launch, no premium model. `hoi4.focus_rewrite` was not used (not authorised for this card).

## What changed in the composition

The chapter is recomposed as two shelves on a 50 x 12 grid, one contiguous band per family, instead of the interleaved lattice it was.

| Block | Cells | Rows | Shape |
| --- | --- | --- | --- |
| 1919 political chapter | x 0-37 | 0-5 | settlement government centred over four route bands (yuan x 0-6, constitutional x 9-17, authoritarian x 22-28, federal x 31-37) with the civil-service spine at x 19 between them; each band's capstone sits under its own centre, all four converge on `QW2_chapter_end` at (19, 5) |
| Industrial programme | x 40-49 | 0-6 | root with four start lanes; the cotton chain descends at x 40, the rail/port/telegraph/tariff children hang directly under their parents, `QW2_economy_capstone` closes at (41, 6) |
| Provincial administration | x 0-10 | 6-10 | root over a six-province row, southern integration and the Nationalist question as a straight column at x 2 |
| Manchurian defence | x 12 | 6-8 | three-step vertical chain between the provinces and the restoration band |
| Restoration band | x 15-23 | 6-10 | `QW2_restoration_programme` directly under the chapter convergence, five lanes, three-lane convergence, `QW2_restoration_proclaimed` at (19, 10) |
| New Army | x 26-32 | 6-11 | root, air/navy/manpower row, doctrine, three-school row, fortifications, capstone |
| Versailles diplomacy | x 34-42 | 6-9 | Washington and Soviet lanes, their four children, `QW2_league_seat` between them |

Every connector now runs one row, except the four structural opening/convergence edges below and two three-row capstone edges. The whole tree is 50 columns and 12 rows instead of 46 x 19, so total Manhattan connector length falls from 624 to 382 while the chapter keeps every family in its own cluster.

## Measured before and after

Both runs are the same route on the same file: `hoi4.focus_inspect` with `{treeId: "qing_interwar", workspaceId: "current"}`.

| Metric | Before (Director baseline, reproduced) | After |
| --- | --- | --- |
| focuses | 99 | 99 |
| `validation.passed` | true | true |
| blocking diagnostics | 0 | 0 |
| `diagnosticCount` | 114 | **13** |
| bounds | 46 x 19 (x 0-45, y 0-18) | **50 x 12** (x 0-49, y 0-11) |
| connectors | 118 | 118 |
| crossings | 42 | **0** |
| `FOCUS_AVOIDABLE_CONNECTOR_CROSSING` | 42 | **0** |
| `FOCUS_LAYOUT_CONNECTOR_CROSSING_UNSATISFIED` | 42 | **0** |
| connector through node | 2 | **0** |
| long connectors | 16 | **4** |
| linear detours | 3 | **0** |
| max horizontal span | 26 | 16 |
| max vertical span | 9 | 3 |
| max Manhattan span | 27 | **17** |
| total Manhattan span | 624 | **382** |
| min same-row spacing / too close | 2 / 0 | 2 / 0 |
| `layoutHash` | `e60e82c2ef983e83c0964c89fc04bdda15743119227738e4d8e62acb6a7558f1` | `977168ee9e4eb53959425bf5418d8bd406986ded5989de8299b8ade528d3abb1` |

Remaining diagnostic mix: 9 `FOCUS_REPEATED_GENERIC_REWARD` (the pre-existing reward-design note, explicitly out of scope) and 4 `FOCUS_LAYOUT_LONG_CONNECTOR`. No crossing diagnostic of either code remains, so nothing has to be reported as an unsatisfiable crossing pair.

### The four remaining long connectors, and why coordinates cannot remove them

| Connector | Span | Why it is topology, not placement |
| --- | --- | --- |
| `QW2_settlement_government -> QW2_yuan_trunk` | 16 columns, 1 row | the 1919 opening is one parent with five children: four route bands, each 7-9 columns wide because a band of four or five siblings needs two-cell clearance, plus the civil-service spine. The five trunks span x 3-34. A parent within 8 columns of the outer trunk (x 3) is at least 13 from the other outer trunk (x 34), so at most three of the five can ever be short. Moving the root to either end trades two long edges for three. |
| `QW2_settlement_government -> QW2_federal_trunk` | 15 columns, 1 row | same fan, opposite end. |
| `QW2_yuan_capstone -> QW2_chapter_end` | 16 columns, 1 row | the four route capstones sit at x 3, 13, 25 and 34, each under its own band. For a single convergence point to be within 8 columns of all four, the two outer capstones would have to be at most 16 apart; they are 31 apart. Pulling the outer capstones off their band centres to banish one edge moves that cost onto their own four-way inbound fans instead. |
| `QW2_federal_capstone -> QW2_chapter_end` | 15 columns, 1 row | same convergence, opposite end. |

Two long connectors are therefore structural per fork, four in total, which is exactly the card's ceiling. They are the two genuine forks of the chapter — the 1919 opening and the 1935 convergence — not filler edges, and neither can be shortened without deleting a prerequisite or re-parenting a focus, both of which this card forbids.

## Preservation evidence (criterion 4)

- 99 focus ids before and after, identical as a set; `git diff --stat` on the tree is 132 insertions / 128 deletions, all coordinate value lines plus the seven-line overview comment that replaced three.
- Byte comparison of the working copy against the pre-edit snapshot (`.tmp/qing_interwar_before.txt`, sha256 `e97e4245022df74da6cd294b6fa563e55dc25445f702048b14aad6154d059c0c`, taken before the first write): after the `focus_tree` line the two files are line-for-line identical except **125 differing lines, every one of them an `x =` or `y =` value line**. 73 coordinate values were already correct and were left alone.
- Structural counts unchanged: 118 `prerequisite`, 99 `completion_reward`, 0 `mutually_exclusive` (the tree declares none, before or after), 5 `shortcut` blocks, `initial_show_position` and `continuous_focus_position` untouched, no `relative_position_id` fields exist, final brace depth 0.
- Encoding: single UTF-8 BOM, 1539 CRLF and **0 bare LF**, first character `#`. The file is plain UTF-8 with the BOM the rest of the working tree carries; the edit script wrote bytes rather than text so no BOM was added or doubled.
- `.tools/tests/test_qing_interwar_layout.py` pins a sha256 of every focus body with only its `x`/`y` value lines removed (digests computed from the pre-edit snapshot) and compares parsed blocks, not counts. Its negative control mutates a reward constant, inserts a reward line, swaps an icon, renames a leaf id, reverses a prerequisite, duplicates a cell and tightens a row; all seven mutants are rejected.

## MCP evidence

- Route: `hoi4.focus_inspect`, input `{treeId: "qing_interwar", workspaceId: "current"}`
  - Before: 99 focuses, `layoutHash e60e82c2…`, `diagnosticCount 114`, `validation.passed true`, 46 x 19.
  - After: 99 focuses, `layoutHash 977168ee…`, `diagnosticCount 13`, `validation.passed true`, 50 x 12.
  - Resource URIs: before `…/2dba68202ea8663a…/focus-inspect.2cc5433f0a939c5b.json`, after `…/5eae949f0299b0c2…/focus-inspect.a8d3ac2c981ebf13.json`.
- Route: `hoi4.script_validate`, input `{path: "common/national_focus/qing_interwar.txt", workspaceId: "current"}`
  - Result: `status ok`, `valid true`, `checkedCommands 288`, 0 findings, `argumentBlocksUnchecked 122`, `unresolvedCount 0`, 136 roots with 0 unknown-scope roots.
  - `checksPerformed`: syntax, command_kind, declared_scope, player_text, event_popups, known_mistakes. `parametersChecked: false`, so effect arguments are not covered.
- Route: `hoi4.focus_render`, input `{relativePath: "common/national_focus/qing_interwar.txt", treeId: "qing_interwar", reviewScale: 0.4, cropFocusIds: [QW2_settlement_government, QW2_chapter_end, QW2_restoration_proclaimed, QW2_army_capstone]}`
  - Result: 3571 x 605 PNG, sha256 `bbe35558270ee9d8e25887829e635d51be4d309ffb12312688d9452cc913bee8`, `layoutHash 977168ee…` (render and inspect agree), plus four close-ups and the HTML/SVG/source-map set, all under `hoi4-agent://workspace/endsieg/artifact/bbe35558270ee9d8…/`.
- Route unavailable: `hoi4.focus_inspect` with `relativePath: ".tmp/qing_interwar_candidate.txt"` returned `FOCUS_SOURCE_NOT_FOUND` ("No active focus source matched the request") on one attempt; the route resolves only indexed focus sources, so candidate layouts cannot be scored before writing. Not retried. The layout was instead scored with a local replica of the tool's geometry (`176/116` grid, `144 x 76` node, 24-segment cubic, the same crossing, through-node, long-connector and detour rules), which reproduces the Director baseline exactly (42 crossings, 16 long, 2 through, 27 max Manhattan, 46 x 19, the same 16 long edges) before being used to design the new one. The live route then confirmed the designed numbers without a single discrepancy.

None of this is in-game proof: no focus was clicked, no tree was drawn by the engine, no launch was authorised.

### Render, honestly

The PNG above is generated from the post-repair layout hash and is available to review. This session has no image route, so **I did not look at it**; a reviewer with vision must still judge "readable at normal zoom". What is objective is the occupancy map of the shipped coordinates (`P` politics, `E` industry, `V` provinces, `M` Manchuria, `R` restoration, `A` army, `D` diplomacy):

```text
    01234567890123456789012345678901234567890123456789
 0  ...................P.......................E......
 1  ...P.........P.....P.....P........P.....E..E..E..E
 2  P.P.P.P..P.P.P.P.P.P..P.P.P.P..P.P.P.P..E.E.E.E..E
 3  .P.......P.........P..P.P......P.P......E.E.......
 4  ...P.........P...........P........P.....E.........
 5  ...................P....................E.........
 6  .....V......M......R.........A.......D...E........
 7  V.V.V.V.V.V.M..R.R.R.R.R..A..A..A.D...D...........
 8  ..V.V.......M..R.R.R.R....A..A....D.D.D.D.D.......
 9  ..V.............R..R..R....A.A.A.....D............
10  ..V................R.......A......................
11  ............................A.....................
```

## Checks run

| Command | Result |
| --- | --- |
| `python .tools/tests/test_qing_interwar_layout.py` | 4/4 PASS: crossing-detector sanity, identity and non-layout preservation, layout invariants (cells, spacing, parent-above, bounds, 0 crossings, <= 4 long), seven-mutant negative control |
| `python .tools/tests/test_qing_survival.py` | all 9 sections PASS, "all checks passed against f6d12527cc8a; the baseline mutant is rejected" |
| `python .tools/tests/test_qing_ww1_layout.py` | PASS, exit 0 |
| `python .tools/tests/test_qing_consolidation.py` | **5 of 6 sections PASS; section 5 fails** — see below |
| `python tools/china_audit.py` | exit 0: 468 focuses, 0 missing focus keys, 34509 localisation keys; the single reported problem is the pre-existing 16 `PER_*` decision localisation gaps |
| `python tools/check_mutex_overlap.py --tree qing_interwar` | `OVERLAP: 0  NON-RECIPROCAL: 0  SELF: 0`; the tree declares no `mutually_exclusive` fields before or after, so there is no pre-existing non-reciprocal pair to carry forward |

### The one red check, and the ownership reason it was not fixed here

`test_qing_consolidation.py` section 5 ("every pre-existing focus is preserved") compares the shipped `qing_interwar.txt` against pinned revision `7136c90a37a1dd0686a2ca456efb85563ff194b9` for a field list that **includes `x` and `y`** (`check_preserved_layout`, line 1228). It reports 108 failures, every one of them "changed its x" or "changed its y". Any accepted layout pass on this file fails that pin by construction, so the check cannot be green while the layout changes it is meant to permit.

The fix is one line in `.tools/tests/test_qing_consolidation.py`: drop `x` and `y` from that field tuple (the section's own intent, "the restoration band did not disturb pre-existing gameplay", is already covered by the digests in `test_qing_interwar_layout.py`), or re-pin `BASELINE_REV` after integration. That file is not one of this card's four owned paths and the Director comment explicitly forbids editing any test other than the new one, so I did not touch it. **Director either grants that one-line ownership or makes the edit at integration; without it criterion 8 cannot be reported green.**

## Not done, not claimed

- No engine load and no in-game check (not authorised). Nothing here proves the tree appears, draws, or that a focus is clickable.
- No image was viewed by me; the render exists and is linked, the judgement is not mine.
- No commit, no stage, no push, no branch change, no launch, no `focus_rewrite`.
- No Obsidian/second-brain write from this worker: team protocol serialises shared-vault writes through Director.
- The 9 `FOCUS_REPEATED_GENERIC_REWARD` notes are a reward-design question for a later card, untouched.
- `common/national_focus/qing_ww1.txt`, the other Qing/RCH/SHX trees, `common/decisions/PER.txt` and `.tools/tests/test_rch_succession.py` were not opened for writing.

## Re-verification pass, 2026-10-27 (retry run 244)

The first run was cut off by its iteration budget after writing this handoff but before the lifecycle transition, so the retry re-derived every number instead of taking the handoff on trust. All the figures above reproduce.

### Independent preservation proof (my own script, not the new test)

`git show HEAD:common/national_focus/qing_interwar.txt` against the working copy, compared from the `focus_tree = {` line onward with every `x =` / `y =` value line removed:

- body is **1530 lines on both sides** and **0 lines differ** after coordinate stripping;
- 198 coordinate value lines exist on both sides (99 x + 99 y); **125 changed, 73 untouched**;
- 118 `prerequisite`, 99 `completion_reward`, 99 `focus = {` on both sides; 0 `mutually_exclusive`, 0 `relative_position_id`;
- 99 parsed focus blocks, **99 unique cells, 0 duplicate cells**;
- single UTF-8 BOM, 1539 CRLF, **0 bare LF**, first character `#`;
- the only other difference in the file is the overview comment, 6 lines → 10.

This is the same conclusion the digest-pinned test reaches, arrived at a different way, so criterion 4 rests on two independent comparisons rather than one.

### Why four long connectors is the minimum, not a leftover

For a single parent feeding children at x = 3, 13, 19, 25, 34 (the 1919 fan), a parent at any x has `|x-3|` and `|x-34|`; both are ≤ 8 only if the children span ≤ 16 columns, and they span 31. The parent at x = 19 gives spans 16, 6, 0, 6, 15 — **exactly two** over the threshold, which is the smallest achievable. The same argument applies to the 1935 convergence over capstones at x = 3, 13, 25, 34: x = 19 gives 16, 6, 6, 15, again the minimum two. So the shipped 4 is the provable floor for this prerequisite topology, and the 114 → 13 result buys nothing by hiding a route.

### Grid, from the shipped coordinates

```
y=0  settlement_government@19                       industrial_takeoff@43
y=1  yuan@3  constitutional@13  civil_service@19  authoritarian@25  federal@34 | mills@40 coal@43 irrigation@46 roads@49
y=2  four children per trunk (0-6, 9-17, 22-28, 31-37); press_law@19 | industry row 40-49
y=3  yuan_succession_crisis@1 constitutional_cabinet@9 local_government@19 ... public_health@40 land_reform@42
y=4  yuan_capstone@3 constitutional@13 authoritarian@25 federal@34 | state_bank@40
y=5  chapter_end@19 | heavy_industry@40
y=6  provincial_administration@5 manchurian_defence@12 restoration_programme@19 army_establishment@29 versailles_revision@37 economy_capstone@41
y=7  provinces 0-10 | manchuria@12 | restoration 15-23 | army 26-32 | diplomacy 34-42
y=8  southern_integration@2 kmt_question@2 chain | manchurian_crisis_prep@12 | restoration 15-21 | army 26-29 | diplomacy 34-42
y=9  restoration_constitution@16 succession@19 legation@22 | army_academies@27 arsenals@29 armour@31 | league_seat@37
y=10 northern_expedition@2 | restoration_proclaimed@19 | army_fortifications@27
y=11 army_capstone@28
```

Every family occupies one contiguous band, every child sits below each of its prerequisites (the test asserts this for all 99), and the two shelves read in order: the 1919 political chapter with its industry programme beside it on top, the 1920s-30s country chapters below. `minimumSameRowSpacing` 2 and `maximumSiblingDeviation` 0 mean no sibling is nudged off its family anchor.

### Checks re-run in this pass

| Command | Result |
| --- | --- |
| `python .tools/tests/test_qing_interwar_layout.py` | 4/4 PASS, **exit 0** |
| `python .tools/tests/test_qing_survival.py` | PASS, exit 0 |
| `python .tools/tests/test_qing_ww1_layout.py` | PASS, exit 0 |
| `python .tools/tests/test_qing_consolidation.py` | **exit 1**, 108 failures, every one `changed its x` / `changed its y` |
| `python tools/check_mutex_overlap.py --tree qing_interwar` | `OVERLAP: 0  NON-RECIPROCAL: 0  SELF: 0` |
| `python tools/china_audit.py` | exit 0, 468 focuses, 0 missing focus keys, 34509 loc keys, only the 16 pre-existing `PER_*` gaps |
| `hoi4.focus_inspect {treeId: qing_interwar, workspaceId: current}` | 99 focuses, 13 diagnostics, 0 crossings, 4 long, 0 through-node, 50x12, passed true, layoutHash `977168ee…`, artifact `focus-inspect.a8d3ac2c981ebf13.json` |
| `hoi4.script_validate {path: common/national_focus/qing_interwar.txt}` | ok, valid, 288 commands, 0 findings, 122 argument blocks unchecked, `parametersChecked: false` |

Two honest notes on the tooling. `check_mutex_overlap.py --tree` filters the **problem list** (`line 285`), not the scan: it read 133 files and 14572 focuses, so the zero is a global zero and holds for `qing_interwar` a fortiori. `script_validate` leaves 122 native argument blocks unchecked, so its "0 findings" covers command names, scopes and syntax, not effect arguments.

### The two things this retry found that the first handoff did not record

1. **`docs/plans/qing_1910_1945/current_report.md` is not solely this card's diff.** Against HEAD it changes in four places: the focus count 85 → 99, the grid row, the new source note, and — unattributed to this card — one `rch_campaign` paragraph line about `days_mission_timeout`, plus a reduction of the file's leading BOMs from three to two. The `rch_campaign` card (`t_6ff7bb84`) is editing that subject in the same working tree, so this is another session's uncommitted hunk, not mine. **It was left untouched**: reverting it would delete another card's work. Director should attribute that hunk when integrating, and should not read the BOM change as this card's.
2. **The consolidation failure is a test-design pin, not content drift.** `check_preserved_layout` (`.tools/tests/test_qing_consolidation.py:1217`, field tuple at `:1228`) compares the shipped tree to `BASELINE_REV 7136c90a…` including `x` and `y`, so any layout pass on this file fails it by construction. Its own cell, row-spacing and `parent-above-child` assertions run on the shipped tree and pass; only the coordinate freeze fails. The one-line remedy (drop `'x', 'y'` from that tuple, or re-pin `BASELINE_REV` at integration) sits outside this card's four owned paths and outside the Director's explicit "do not edit any test other than the new one" ruling.

## Status at handoff

Criteria 1, 2, 3, 4, 5, 6, 7 are met on the evidence above. **Criterion 8 is not met**: four of the five commands are green, `test_qing_consolidation.py` is red for the pin reason above and cannot be made green from inside this card's ownership. That is the one decision blocking a clean completion, and it needs Director, not another implementation pass.
