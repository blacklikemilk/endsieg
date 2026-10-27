# qing_ww1 presentation repair — branch-first recomposition (pass 3)

Supersedes the pass-1 and pass-2 handoffs. Owner: endsieg-developer, card `t_13a9541f`.
Written paths: `common/national_focus/qing_ww1.txt` (focus `x`/`y` values and the overview layout comment only), `.tools/tests/test_qing_ww1_layout.py` (three mutation anchors retargeted), `localisation/english/qing_ww1_l_english.yml` (one existing key value), this file.
No focus, icon, reward, prerequisite, mutually-exclusive, cost, search-filter, AI, bypass, visibility or shortcut field was touched. Nothing staged or committed. No game launch.

## What changed in the composition, not just the counters

The whole view is recomposed as ten contiguous family blocks on a 41 x 23 grid, each block anchored by its own root and reading top to bottom:

| Block | Cells | Rows | Shape |
| --- | --- | --- | --- |
| Court and constitution (P) | x 1-21 | 0-11 | root at x11 centred over the reform and resistance forks; constitutional route x 6-10, autocratic route x 12-16, culture/education lane a straight column at x1 |
| Provinces (V) | x 24-33 | 0-5 | root centred, federal cluster left, Manchurian cluster right |
| Beiyang command (B) | x 36-40 | 0-10 | symmetric double lane converging at root, premiership, succession and state |
| 1911 crisis (C) | x 26-33 | 7-14 | straight descending chain, abdication fork on row 12 |
| Loyalist preparation (R) | x 6 | 8-11 | four-step lane beside the culture lane instead of stranded across the canvas |
| New Army (A) | x 0-10 | 13-22 | root, academy fork, corps fork, capstone, equipment fan |
| Treasury (E) | x 13-22 | 13-19 | three start lanes (salt, land, railway) merging into the currency capstone |
| Foreign office (D) | x 28-40 | 16-22 | Japan crisis lane left, powers lane right, capstone between them |
| Japanese war (J) | x 28-30 | 16-19 | invasion directly above the crisis it feeds |
| Chapter end | x 21 | row 8 | single convergence between the court capstones and the province/Beiyang block |

Named defects from the card, all resolved by re-laying the branch rather than by pushing endpoints apart:

- `court_resistance -> banner_privilege` 25 columns -> 1 (the resistance subtree is now a compact right-hand fork).
- `grand_council -> court_appointments` 24 -> 1; `regency_end -> autocratic_settlement` 26 -> 1.
- `legal_code -> new_schools` 28 -> straight column.
- `yuan_succession -> chapter_end` no longer cuts `dynastic_legitimacy`/`manchu_garrisons`; the whole tree's connector-through-node count is 0.
- Economy staircases (`currency_board -> modern_banking -> national_budget`, `hanyang_arsenal -> foreign_loans -> arsenal_expansion`) are straight columns: `FOCUS_LAYOUT_STAIRCASE_CHAIN` 2 -> 0, `FOCUS_LAYOUT_LINEAR_DETOUR` 7 -> 0.
- The row-13 parking is gone: the crisis starts at row 7, the army and treasury at row 13, the foreign office at row 16, each directly under the block it belongs to.

## MCP evidence (workspaceId `current`, treeId `qing_ww1`, `common/national_focus/qing_ww1.txt`)

| Metric | Director baseline | pass 2 (rejected) | this pass |
| --- | --- | --- | --- |
| focuses | 158 | 158 | 158 |
| bbox columns x rows | 47 x 27 | 45 x 23 | **41 x 23** |
| fill | 12.5 % | 15.27 % | **16.76 %** |
| connectors | 177 | 177 | 177 |
| crossings | 33 | 9 | **1** |
| connector-through-node | 11 | 2 | **0** |
| long connectors | 8 | 1 | 2 |
| max horizontal span | 28 | 15 | 15 |
| max manhattan span | 20 | 20 | 18 |
| max vertical span | 3 | 3 | 3 |
| min same-row spacing | 2 | 2 | 2 (required 2, too-close pairs 0) |
| staircase chains | 2 | 0 | 0 |
| linear detours | 7 | 3 | **0** |
| `validation.passed` | true | true | true |

`layoutHash` **ae024b64e4b66a5fc90dc7575fe90722385b058a3a377eea13614b00340fcc01** (inspect and render agree). 8 diagnostics: 4 pre-existing `FOCUS_REPEATED_GENERIC_REWARD` design notes, 1 vanilla continuous-focus localisation gap, 3 residual layout items below.

Inspect artifact: `hoi4-agent://workspace/endsieg/artifact/c087ba2fd359133531735ef70fd9f3f7853453844602f6fd58586c9a51a02a8b/d385e2912f3e76afae2d9dd001554d4c721eafc0c98d1ef9ee1c191b1e11be70/focus-inspect.50ec52111ea719b9.json`

Render (`reviewScale` 0.4, full tree plus nine close-ups): 2938 x 1115, 395 212 bytes, PNG sha256 `317207d71173601d7f3bc448f3d1a90b168e7197e797bdc10069d89eee64c461`, same layout hash:
`hoi4-agent://workspace/endsieg/artifact/317207d71173601d7f3bc448f3d1a90b168e7197e797bdc10069d89eee64c461/1b2151f7997b941a2e40717e374e6466c16dd23d78c448afbd7930a32aa6e16f/qing_ww1.focus.png`

Close-ups (each under 55 KB, listed in `qing_ww1.focus-problem-crops.json` in the same artifact set): `QW1_regency_council`, `QW1_constitutional_capstone`, `QW1_provincial_governors`, `QW1_beiyang_command`, `QW1_imperial_treasury`, `QW1_new_army_budget`, `QW1_foreign_office`, `QW1_railway_guard`, `QW1_chapter_end`.

### Eye review — still owed, not claimed

This session has no vision tool, so I did not look at the render. What is proven is that the PNG was generated from this layout hash and can be fetched whole. A reviewer with an image route must still judge "readable at normal zoom"; the geometry and the occupancy map below are objective evidence, not a substitute.

Occupancy map of the final coordinates (`.` empty, letter = family):

```
    01234567890123456789012345678901234567890
 0  ...........P................V.........B..
 1  .....P.....P....P........V.....V....B...B
 2  ..P.P...P....P....P.....V.V...V..V....B..
 3  .P.P...P.P..P.P...P.....V.V..V.V....B...B
 4  .P......P....P..........V.V.V...V...B...B
 5  .P......P....P............V.........B....
 6  .P....P.P.P.P.P.P.....................B.B
 7  .P......P.....P..............C........B.B
 8  .P....R..............P.......C........B.B
 9  .P....R......................C........B.B
10  .P....R......................C.........B.
11  .P....R.....................C..C.........
12  ..........................C...C..C.......
13  ....A............E............C..C.......
14  ..A..A........E..E....E.....C.C..........
15  ...A...A......E..E....E..................
16  .A...A........E.E.E...E.......J.......D..
17  A..A..A.......E.E.E.E.E.....J........D..D
18  ...A..A.A.A.....E...E.E.....J.....D..D..D
19  .....A.......E.E.E.E........J.D..D.D.D..D
20  ..A.A.A..A....................D..D.D.....
21  ..A.A.A......................D.D.D.D.D...
22  ..A.........................D............
```

## Residual layout warnings (exact ids)

1. `QW1_constitutional_capstone -> QW1_chapter_end` 13 columns / 1 row, and `QW1_yuan_succession -> QW1_chapter_end` 15 columns / 3 rows. Structural: `chapter_end` is the single convergence of four parents spread over x 8, x 14, x 26 and x 36, so every position leaves at least one long edge. The Beiyang edge leaves through free cells under the provinces block; it no longer passes through a focus.
2. `QW1_boxer_indemnity -> QW1_japanese_relations` crosses `QW1_treaty_ports -> QW1_british_understanding`. `japanese_relations` requires both treaty ports and the Boxer indemnity while `british_understanding` hangs off treaty ports, so the two fan-outs share a row band; MCP reports the pair as `FOCUS_LAYOUT_CONNECTOR_CROSSING_UNSATISFIED` with `movableFocusIds: []`. Two alternatives tried this session (mirroring the treaty/boxer columns; pulling `japanese_relations` further left) each produced two new detours and a fresh crossing, so this arrangement is the best measured one.
3. `FOCUS_REPEATED_GENERIC_REWARD` on `QW1_cotton_mills`, `QW1_womens_education`, `QW1_industrial_labour`, `QW1_manchurian_development` — reward design, predates this card, outside its ownership.

## Preservation (AC1/AC4/AC5)

Immutable pre-edit snapshot `qing_ww1.before.txt` in this session's scratch dir, byte-identical to `git show HEAD:common/national_focus/qing_ww1.txt` after line-ending normalisation (sha256 `caa52718fa2167ce7e7a91226b12e58d434e3156b7c3e597c07b162e5b1d5cfa`); not regenerated at any point.

- 158 focuses before and after; id order identical; **0 bodies differ beyond their own `x`/`y` value lines**.
- 159 outside-focus segments compared byte for byte: **1 differs**, and only the owned overview `# Layout:` comment (2 lines replaced by 5, text updated to the real 41 x 23 geometry).
- Field counts untouched: 158 icons, 164 prerequisite blocks, 7 `mutually_exclusive`, 158 search_filters, 158 ai_will_do, 158 cost, 158 completion_reward, 6 shortcut blocks; `initial_show_position` and `continuous_focus_position` unchanged; no relative-position field exists in this tree.
- Plain UTF-8, no BOM, CRLF preserved. `git diff` over the tree (247 added / 244 removed lines) contains only `x`/`y` lines and that comment hunk; a filter for any other changed line returns nothing.
- `localisation/english/qing_ww1_l_english.yml`: the one owned value `qing_japan_navigation` changed from the raw key to `"Japan and Shandong"`; single BOM intact, rest of the file untouched.

## Checks run

- `python tools/check_mutex_overlap.py --tree qing_ww1` -> `OVERLAP: 0 SELF: 0`, exit 0, run after the last coordinate edit. The one `NON-RECIPROCAL` (`QW1_imperial_redoubt -> QW1_abdication_question`) is a `mutually_exclusive` data field this card does not own and was left alone.
- `.tools/tests/test_qing_ww1_layout.py` -> 3/3: body-hash preservation, layout invariants, and the eight-mutation negative control (reward constant rename, inserted reward line, icon swap, leaf id rename, reversed prerequisite, duplicate cell, tight row, mutex intruder). Three mutation anchors were retargeted to the new coordinates; no assertion was relaxed.
- `.tools/tests/test_qing_survival.py` and `.tools/tests/test_qing_consolidation.py` -> all checks pass with their baseline mutants rejected, so no gameplay test was coordinate-pinned.
- Invocation: `test_*` functions run through a path loader (no pytest in this repo); survival and consolidation run as scripts.

## Not done / not claimed

- No engine load and no in-game check (not permitted on this card). Everything above is static, geometric and MCP-render evidence.
- No image viewed by me (no vision route this session).
- No commit, no stage, no launch, no branch change. `focus_rewrite` was not used: targeted source patches were sufficient and provably coordinate-only.
