# Endsieg gameplay quality benchmark

Disposition: accepted as the B0 review benchmark on 2026-10-26, not authorization to rewrite existing countries.
Source: native board `endsieg-development`, B0 `t_99b610fd`, Designer deliverables in comments 93/106/129 and independent Director acceptance run 50.
Reviewed source baseline: `TeknoDev-Branch` at `a03205963`.
The reviewer used a separate token-level lexer, re-tested earlier rejected measurements, and completed the native review rather than accepting the Designer's self-report.
The historical measurement ledger remains at two rejections; the final candidate passed, so no further correction or premium investigation was needed.

## Purpose and limits

Use existing Germany, Russia and USA content as concrete precedents and counterexamples, not templates to copy or focus-count targets.
A good route changes what the player can do and has a meaningful cost, a distinct identity, connected systems and a visible consequence.
Trace effects through their helpers and consumers before deciding whether a reward is functional.
A variable or flag can support a meaningful mechanic when a real reader turns it into gameplay and visible feedback; an unread terminal flag cannot.
The token census below is a reproducible screening aid, not proof that a branch is coherent, an idea is effective, the AI follows a plan, or the interface works.
Passing a percentage never overrides a confirmed broken reward, missing route, wrong era or unapproved artwork replacement.
This benchmark does not weaken `CLAUDE.md`, project skills, the eight-language requirement, independent QA, file ownership or the no-launch rule.

## Reproducible measurement units

Strip comments before counting braces, retain strings as values rather than command tokens, and distinguish command arguments from executable effects.
Do not use line-anchored key matching for files with inline blocks.
Do not count `localization_key`, `CATEGORY`, `DESC` or `add_popularity`'s `popularity` argument as separate effects.
Do not classify a scripted-effect wrapper as a bare statistic without following its body.

| Rule | Unit |
| --- | --- |
| U1 | A tree focus is a `focus = { ... }` block with an `id`; shared/joint/continuous definitions are outside this census. |
| U2 | A payable reward has at least one actual effect in `completion_reward`, excluding structure, trigger limits and tooltip arguments. |
| U3 | Stat-only means every reward effect is one of political power, stability, war support, army/navy/air experience, command power, manpower, stockpile equipment, fuel, opinion or popularity, and the focus contains no U4 token. |
| U4 | Visible-token coverage means the focus body names an idea/timed idea/dynamic modifier, event/news event, research slot/tech bonus/breakthrough, mission, decision unlock or explicit effect/idea/decision tooltip. |
| U5 | No-effect means U2 fails; an external decision/event/idea/UI reader must be traced before declaring the focus ineffective. |
| U6 | Report raw, commented and live `ai_will_do` separately; a flat block has exactly one factor and no modifier block. |
| U7 | Plan coverage is the union of exact tree-focus IDs named across `common/ai_strategy_plans/*.txt`; reference coverage is not proof of live selection. |
| U8 | Durable-token coverage means `completion_reward` names `add_ideas`, `add_timed_idea`, `add_dynamic_modifier`, `country_event`, `news_event`, `add_research_slot`, `add_tech_bonus` or `add_mission`; tooltip-only tokens are excluded. |

U8 applies to the reward, not the whole focus body.
For example, the idea in `USA_USACE_projects`' bypass must not inflate its durable-reward score.
Bare `check_variable` and numeric identity selectors require separate semantic review; a passing census does not validate their comparison behaviour.

## Independently accepted benchmark measurements

| Tree | Focuses | Payable | No effect in reward | Visible U4 | Stat-only U3 | Durable U8 | Plan IDs U7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Germany | 438 | 424 | 14 | 397 (90.6%) | 0 | 259 (59.1%) | 258 (58.9%) |
| WWI Russia | 143 | 143 | 0 | 99 (69.2%) | 12 (8.4%) | 99 (69.2%) | 40 (28.0%) |
| USA | 135 | 133 | 2 | 112 (83.0%) | 3 (2.2%) | 75 (55.6%) | 89 (65.9%) |

Live `ai_will_do` counts are 113, 143 and 104 respectively; raw/commented counts are Germany 114/1, Russia 143/0 and USA 136/32.
Germany's corrected no-effect count includes `GER_integration_of_puppet_economies`, whose reward is a parameterized tooltip and whose decision-category reader provides the external payoff.
The seven advisor-ascension/chancellor rewards incorrectly omitted by earlier extraction contain real hidden effects and events and are payable.
Russia's `RUS_ww1_national_defence_council` calls `WW1_support_neutrality_programme` and is not stat-only.
The USA pension and war-propaganda rewards call Congress helpers that change senator/representative support and refresh UI frames; they are not stat-only.

## Route-level precedents and weaknesses

| Chain | Actual connection | Lesson |
| --- | --- | --- |
| Germany `GER_proletarian_solidarity` | Focus unlock/tooltip to the vanilla German decision, target event `wuw_GER_diplomacy.84`, and solidarity national spirits. | A reward outside the focus file can be meaningful, but the reader and target scopes must resolve. |
| Germany `GER_hegemony_over_europe` | War goals and diplomatic teardown, a formable-decision unlock and the Reichstag/Volkshalle payoff. | Expansion should change the map and political order rather than end in a passive statistic. |
| Russia `RUS_war_front_1` | Timed coordination spirit, `ww1_russia.10`, and the 50-PP/30-day staff-exercise programme. | A temporary reward gains depth through a costed, gated follow-up; the historical plan supplies its AI route. |
| Russia postwar constitution to `RUS_ww1_a_state_for_the_new_decade` | Eleven routes converge before a terminal 100-PP reward. | This is a weakness, not a standard to copy: choices lose distinction and the terminal lacks a durable route payoff. |
| USA `USA_manhattan_project` | Tech-aware conditional reward, alternative breakthrough progress and the project spirit. | Both existing-tech and missing-tech cases need a real payoff; the focus must not void itself. |
| USA `USA_secure_asia` | Events in valid target countries/controllers, subject/existence/war bypasses and invalidation handling. | Diplomacy needs valid targets and recovery conditions rather than a permanent dependency on one foreign state. |

The two German chains have no explicit `ai_will_do` or plan mention in the reviewed source.
Russia's postwar convergence and the USA Asia terminal are not named in the reviewed plan union, so good reward chains are not automatically good AI precedents.

## Accepted audit standards

### S1 — meaningful rewards

Require a reachable observable change, an effective spirit lifecycle or a traced external payoff.
Use a stat-only share of at most 10% as the screening threshold, met by the three measured benchmarks.
A branch terminal at depth three or greater must not end in a bare-stat reward; the Russian 100-PP terminal is a named counterexample.
Every U5 focus requires its external payoff to be traced; every flag/variable payoff requires an actual reader.

### S2 — route cost and identity

Every meaningful fork needs a real commitment or cost and a distinct payoff.
Review convergence explicitly; a second convergence or identical reward for otherwise distinct routes fails the reviewed route-cost test.
The Russian staff exercise provides the concrete 50-PP/30-day/90-day-reenable cost precedent, not a universal tuning value.

### S3 — era identity

Require a named initialization and transition mechanism for every chapter and route.
Either individual focus gates or chapter loading plus branch/tree gates must keep the correct content in the correct era.
Russia's 143 focus-level date gates are one precedent, not permission to copy 1936 content into earlier chapters.
Bookmark `has_start_date` checks and dated history blocks do not schedule continuous-campaign transitions.

### S4 — readable layout

The reviewed screening targets are zero too-close same-row pairs, single-digit node intersections per 100 focuses, maximum Manhattan connector span at most 21, and no more than one crossing per seven focuses.
Renderer metrics support review but do not replace inspecting the picture or the live tree.
Preserve existing icons, IDs and gameplay during layout-only work.

### S5 — visible feedback

Use at least 65% visible-token coverage under U4 and at least 55% durable-reward coverage under U8 as the reviewed screening thresholds.
All three benchmark trees meet both numerical clauses; this does not prove every reward is good.
A promise in localisation still has to match its real effect and visible consumer.
Spain's reviewed `spain.txt` census fails both clauses: 180/281 visible (64.1%) and 126/281 durable (44.8%), not a pass rounded upward.
Iran's durable counts are 22/25/28 across its three chapter trees, and Qing's are 10/6/0; helper/reader and presentation audits are needed before selecting repairs.

### S6 — AI reachability

Trace every supported terminal through the AI plan/order and distinguish mutually exclusive choices with meaningful scenario-dependent weights.
Use 65% plan-reference coverage as the reviewed screening target, achieved by the measured USA tree; 80% is an aspiration, not a benchmark-derived fact.
Coverage alone is not selection probability or live campaign behaviour.
Run the required probability audit before changing weights; preserve exact unsupported-adapter and unresolved-scenario limitations.

### S7 — localisation

Audit the real English and replacement-English key sources rather than trusting a mod-only lookup that excludes replacement or vanilla content.
The reviewed checkout has a repository-wide gap for the other seven required languages; record it without inventing translations or calling all-language coverage passed.
New player-visible content remains subject to the project's full language and tooltip rules.

## Country application and implementation handoffs

Spain designs must name the campaign loader, connect government choices to the real chamber and bill readers, and preserve Civil War/postwar content.
Iran designs must trace existing meters, agreement flags, settlement spirits and Crown/Majlis effects before treating old reward audits as current defects.
Qing/China designs must distinguish historical collapse, demanding survival, Republic succession, warlord roles and later DLC routing without creating effortless all-China rewards or wrong-era trees.
Each accepted design hands off a small executable slice with exact IDs, owned script/localisation/test/docs files, visible outcome, AI scenarios, costs, cleanup and validation.
No design delivery is reported as completed gameplay.

## Verification and remaining limits

Independent B0 review recomputed disputed counts with its own lexer and re-tested earlier AI/plan measurements before native completion on run 50.
Director additionally inspected the German tooltip-only reward and six Spanish popularity-only rewards and reproduced the U8 table from source.
Read-only HOI4 MCP inspection supported the review; source/index coverage limits and known diagnostic false positives remain explicit.
No HOI4 launch, live AI observation or renderer-picture acceptance was performed for B0.
Thirteen of the fourteen German U5 focuses and both USA U5 focuses still need their external reader trails audited before those individual rewards are accepted.
The benchmark is accepted; those country-level audits and live functionality checks are not silently marked complete.
