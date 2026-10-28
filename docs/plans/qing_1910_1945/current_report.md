# Qing overhaul, current report

## What is implemented

| Surface | Content |
| --- | --- |
| Chapter one, `qing_ww1`, 1910–1918 | 88 focuses: shared reform trunk, four route settlements, economy, army, Beiyang command, diplomacy, provincial compact, revolution preparation, chapter convergence |
| Chapter two, `qing_interwar`, 1919–1935 | 99 focuses: four route trunks, industry, army, diplomacy, provincial administration, Manchurian crisis, Nationalist question |
| Chapter three, `qing_ww2`, 1936–1945 | 65 focuses: four route wartime governments, war economy, army, Allied diplomacy, fronts and victory |
| Events | 33 events, 76 options, namespace `qing_campaign` |
| Decisions | 38 decisions in five categories, including the balance-of-power family |
| Ideas | 11 national spirits in three slots |
| Balance of power | `QIN_throne_and_assembly`, six ranges, attached decision category |
| Characters | Yuan Shikai, Puyi, Liang Qichao |
| AI | Two focus-order plans, historical and constitutional |
| Localisation | Six English files, all focus, idea, decision, category, event and balance keys |
| Documentation | Spec, TFR study, asset record, this system doc |

## Route coverage

| Required route | Implemented route | Status | Notes |
| --- | --- | --- | --- |
| Constitutional Qing | `qing_settle_constitutional`, `QW1_constitutional_settlement` and four continuations, `QW2_constitutional_*`, `QW3_constitutional_*` | Implemented | Elections, cabinet responsibility, royal prerogative, constitutional court, wartime coalition |
| Authoritarian Qing | `qing_settle_authoritarian`, `QW1_autocratic_settlement` and four continuations, `QW2_authoritarian_*`, `QW3_authoritarian_*` | Implemented | Grand Council, censorate, banner reform, security bureau, court schools |
| Yuan Shikai protects the Qing | `qing_settle_yuan`, `QW1_yuan_premiership` and continuations, `QW2_yuan_*`, `QW3_yuan_*` | Implemented | Military government, officers' compact, succession crisis, unified command |
| Federal Qing | `qing_settle_federal`, `QW1_federal_settlement` and continuations, `QW2_federal_*`, `QW3_federal_*` | Implemented | Provincial charter, fiscal compact, regional armies, federal bank and police |
| Historical collapse | existing `ww1_china` chain, suppressed only by `qing_xinhai_settled` | Implemented | No existing event rewritten, only guarded |

## The revolution chain

| Step | Event | Condition |
| --- | --- | --- |
| Reform warning | `qing_campaign.2` | 1910, once |
| Railway Protection | `qing_campaign.10`, `.11` | 1911 summer |
| Negotiated survival | `qing_campaign.20` | reform 40, loyalty 50, trust 40 |
| Military settlement | `qing_campaign.22` | Beijing held, army 55, and reform 45 or Yuan 60 |
| Court council during war | `qing_campaign.23` | war with the Republic, Beijing held |
| Historical revolution | `ww1_china.3` and the provincial uprisings | `qing_xinhai_settled` not set |

Each settlement clears the other three route flags, sets its own, annexes the Republic, replaces the leader and refreshes the mechanics.
Survival is never tied to one focus: the gate is a combination of three values that focus rewards and decisions move separately.

## Static validation performed

- `check_tree_geometry.py`: 0 errors, 0 warnings on all three chapter files (duplicate ids, coordinates, row spacing, prerequisite direction, mutex sanity).
- `check_content_refs.py`: brace balance, duplicate ids, 642 required localisation keys present, icon references resolved.
- Custom audit: all 238 focus ids, 11 ideas, 38 decisions, 5 categories, 33 events and 76 options have localisation; every referenced event exists; every AI plan focus exists; every scripted effect and trigger call resolves.
- Icon audit against `interface/**/*.gfx` in the mod and the installed game: all focus, decision and idea sprites resolve.
- Token audit against the installed `effects_documentation.md` and `triggers_documentation.md`: `add_army_experience` was found to be an invalid effect name and replaced with `army_experience`, `air_experience` and `navy_experience`; integer-only fields now use literals.
- Brace balance of the three existing files touched: `events/WWI - Chinese Collection Events.txt`, `common/on_actions/endsieg_on_actions.txt`, `history/countries/QIN - Qing Empire.txt`.

## Engine defects found by the first launch and fixed

The first launch attempt logged:

- `Invalid key name at line 1 and column 1` for four localisation files, caused by a doubled BOM in the generator.
- `unexpected token ... near line: 1 ( Overview: )` for eight script files whose header comment had lost its leading `#`, which dropped the script constants, triggers, effects, ideas, characters, opinion modifiers and decisions, and therefore also the tree load.

Both causes are fixed and the localisation files now carry exactly one BOM.
That launch is the only engine run performed, and it did not reach a clean scenario with the tree, so it is not evidence that the tree loads.

## The Republic tranche

The Republic of China was left on the generic WWI tree because nothing assigned it a chapter tree: it is dormant at the 1910 start, so the startup hook skipped it, and the only later assignment came from the generic fallback sweep.
It now has three authored chapters and an explicit routing path.

| Surface | Content |
| --- | --- |
| `rch_republic`, 1912-1919 | 51 focuses: provisional government, assembly and presidency, four route settlements, economy, army, WWI diplomacy and the New Culture |
| `rch_warlord`, 1919-1927 | 50 focuses: Beijing government, four clique settlements, industry, army, Washington system and the national public |
| `rch_nanjing`, 1928-1935 | 45 focuses: Nanjing government, four route trunks, economy, army, treaty revision and the crises of the decade |
| 1936 handover | the existing `china_nationalist_focus` is loaded by id at the boundary |
| Events | 16 events, 38 options |
| Decisions | 17 decisions in three categories |
| Ideas | 10 spirits in three slots |
| AI | historical and parliamentary plans |

Routing: `on_startup` has an explicit `tag = RCH` branch, the generic sweep excludes `RCH`, `on_daily_RCH` self-heals the chapter, and the collapse events call `rch_initialize_campaign` in Republic scope on the day the tag changes.

## Qing chapter one rework

The WWI chapter was compacted and expanded: the diplomacy column moved from x 36-40 to 34-38, the province column from 46-54 to 40-44 and the revolution-preparation column to 48, and eight focuses were added (imperial examinations, the regency household, grain reserves, cotton mills, a steelworks, cavalry reform, railway troops and military telegraph).
The chapter is now 96 focuses with a maximum x of 48 instead of 54.

## Chapter one rebuilt (1910-1919)

Chapter one is now 149 focuses, up from 96, in separated bands with a four-cell gutter between branches instead of two.
New content: a Japan war branch with an invasion root that is available only at war, the Shandong crisis, the 1915 demands with a reject/accept fork, a war of posts, mobilisation and a long-war capstone; a full 1911 crisis chain from the Railway Protection Movement to the abdication question, the Second Revolution, Yuan's monarchy, the National Protection War, Zhang Xun's restoration and the Entente declaration; a society branch (schools, university charter, women's education, press law, students, the New Culture, public health, local self-government, labour); a later economy branch; army reform including an air service and navy; and provincial development.
Four new events (`qing_campaign.60`-`.63`) carry the Tsingtao landing, the Wuchang mutiny, the abdication question and the restoration.

Details, anchors and the layout table are in `chapter_one_expansion.md`.


## Chapter one second pass

158 focuses. The Beiyang command gained nine focuses (Baoding, Yuan's health, three cliques, military governors, its treasury, its army and the army-and-state capstone), all flag-setting and paying in equipment, manpower, opinion or political power.
Four historic constraints became spirits: unequal treaties, provincial autonomy, reformed finance and public schools, with the refresh effect adding or clearing them from focus flags.
The society chain, the 1911 crisis, the Japanese war, the later economy and the provincial additions were re-anchored one to three rows under their parents.
Links longer than three cells: 49 before, 37 after; longest link: 15 cells before, 9 after; no box overlaps; 308 focuses across the three chapters, audit clean.


## Scenario ownership repair

`history/states` hands every Chinese state from QIN to RCH on 1914.1.1 and from RCH to CHI and the warlords on 1936.1.1.
`common/scripted_effects/endsieg_china_ownership.txt` now restores ownership: the Qing tick reclaims after 1914 and after 1936, and the Republic tick reclaims in 1936 if the timed `rch_save_the_republic` mission succeeded. If it did not, the player is handed to CHI so a continuous campaign continues as the central government rather than as a stateless tag.


## Layout rebuild (all six China trees)

Every China focus tree was laid out again from a snapshot of the working copy at `.tmp/layout_snapshot_<ts>/`.
The pass tiers each prerequisite family, orders rows by barycentre, positions x by parent median with two-cell sibling packing, and packs families into shelves so no single row becomes a strip.
Focus IDs, counts, prerequisites, mutual exclusions, rewards, costs, AI weights, availability and bypasses are byte-identical to the snapshot; only x/y changed.

| Tree | Before (cells) | After (cells) | Long links before/after |
| --- | --- | --- | --- |
| qing_ww1 | 58x22 | 50x27 | 49 / 37 |
| qing_interwar | 46x19 | 50x12 | 42 crossings / 16 long before → 0 crossings / 4 long after |
| qing_ww2 | 43x11 | 46x11 | 1 crossing |
| rch_republic | 46x8 | 43x7 | 6 / 3 |
| rch_warlord | 46x7 | 43x6 | 10 / 6 |
| rch_nanjing | 48x8 | 42x4 | 11 / 0 |

The `qing_interwar` row is the 2026-10-27 re-lay, measured with `hoi4.focus_inspect` (`treeId: qing_interwar`, `workspaceId: current`): 99 focuses on a 50 x 12 grid, 118 connectors, 0 crossings, 4 long connectors, 4 diagnostics, `validation.passed: true`, layoutHash `977168ee9e4eb53959425bf5418d8bd406986ded5989de8299b8ade528d3abb1`. The figures it replaced quoted an intermediate pass rather than the shipped chapter.
The HOI4 Agent Tools MCP was used for `focus_inspect`, `focus_rewrite` and `focus_render`.
`focus_rewrite` with `layoutMode: "compact"` succeeded on the three Republic trees but produced a 71-column strip on `rch_republic` (against 43 from this pass), and was blocked with `FOCUS_COMPACT_QUALITY_BLOCKED` on all three Qing trees, so its output was not adopted and its sidecar plan files were removed.

## Interwar reward identities

`hoi4.focus_inspect` reported nine `FOCUS_REPEATED_GENERIC_REWARD` diagnostics on `qing_interwar`: three groups of three focuses paid one generic reward each. Those nine are `QW2_constitutional_trunk`, `QW2_cotton_mills`, `QW2_road_programme`, `QW2_federal_trunk`, `QW2_provincial_administration`, `QW2_local_government`, `QW2_industrial_takeoff`, `QW2_civil_service` and `QW2_tariff_policy`, and each now pays a reward of its own subject.
The whole chapter was then audited for shared rewards, not only those nine: eight two-focus pairs paid identical reward text and three further pairs paid the same effects in a different line order behind different tooltip keys.
One member of each pair and each order-insensitive pair now carries a subject-specific addition or substitution, so no two of the 99 focuses pay the same reward text and no two of the 25 accepted rewards share a gameplay signature.
Twenty-five `completion_reward` blocks differ from the integrated tree, all of them enumerated in `tools`-level tests, and every one states itself through a `custom_effect_tooltip` key in `localisation/english/qing_interwar_l_english.yml`.
Two earlier tooltip faults are corrected: `QW2_federal_trunk`, `QW2_provincial_administration`, `QW2_civil_service` and `QW2_local_government` now name the Balance of Power move they pay, and `QW2_tariff_policy` states that the government gains political capital rather than spending it.
Equipment amounts are `constant:qing_story.equipment_small` and `constant:qing_story.equipment_grant`, including `QW2_cotton_mills`, whose `amount = 500` literal was the last bare number in the chapter's rewards.
Every coordinate, icon, cost, prerequisite, mutual exclusion, availability block, AI weight and search filter is identical to the integrated tree, and the layout is frozen at layoutHash `977168ee9e4eb53959425bf5418d8bd406986ded5989de8299b8ade528d3abb1` with four remaining diagnostics, all long connectors.
`python .tools/tests/test_qing_interwar_rewards.py` pins the 25 accepted rewards, the 74 untouched ones and every non-reward field, and rejects a reintroduced duplicate, an order-permuted duplicate, a dropped tooltip, a dropped localisation key, a constant replaced by a literal, an unstated balance-of-power move and a tooltip that reverses its own effect.

## Pending

- A launch that reaches the 1910 scenario with QIN played, to confirm the tree appears, the values initialise, the balance panel exists, and the first events fire.
- A run through 1911 to confirm the negotiated and historical outcomes.
- A run to 1919 and 1936 to confirm the chapter swaps.
- In-game confirmation that `qing_xinhai_settled` suppresses the historical chain and that the unset case still collapses.
- Portrait and balance-of-power art noted in `qing_assets.md`.

## Historical railroading, the rescue mission, and file formatting

Historical focus is now the railroaded timeline for both countries.
`qing_historical_collapse` wraps `is_historical_focus_on = yes`; `qing_survival_possible` and `qing_can_impose_settlement` both require its absence, and `qing_end_revolution` is a no-op under it, so the dynasty falls on the revolution's own schedule no matter which court path is picked.

The Republic's 1934 rescue is off-script content only: `rch_save_the_republic` now requires `is_historical_focus_on = no` behind a `custom_trigger_tooltip`.
It is also drawn in 1934 alone: `days_mission_timeout` makes it a mission, so the appearance gate is `activation` with `rch_campaign_active = yes`, `date > 1933.12.31` and `date < 1935.1.1`, and the matching `visible` block is inert on a mission.
Its difficulty was raised so that avoiding the 1936 warlord split is possible but demands a near-perfect year: entry at more than 200 political power with a 200 cost, Beijing held, legitimacy 80, stability above 55%, back above 150 political power, no war of any kind, the route settlement of the chosen path, and a second national programme.
Thresholds live in `common/script_constants/rch_campaign.txt` as `legitimacy_rescue`, `rescue_stability`, `rescue_entry_power` and `rescue_remaining_power`.

`QW1_chapter_end` required all four route capstones as separate prerequisite blocks, which made it unreachable because the routes are mutually exclusive.
It is now a single prerequisite block, so it completes on whichever route was taken; this is the only gameplay field changed by the layout work.

The six China tree files were formatted: one coordinate per line, tabs, no trailing whitespace, a single header describing purpose, families and the tree's real bounds, and CRLF line endings like the rest of the working tree.
