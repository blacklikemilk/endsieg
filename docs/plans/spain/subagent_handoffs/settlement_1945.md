# S19 handoff: the Settlement of 1945 as playable decisions (A1 + A3)

Card: t_08b44a33, assignee endsieg-developer, model deepseek-v4.1-flash / opencode-go.
Design source: `docs/specs/spain_1910_1945/continuation_1936_1945.md` §4 A1 and §4 A3, accepted in commit 02042bc42.
Branch: TeknoDev-Branch. No commit, no branch or worktree action, no game launch.
Baseline for every "unchanged" claim: commit 02042bc42, read through `git show HEAD:<path>`.

## What the slice now does

A Nationalist Spain that reaches the post-war chapter gets two decisions in the faction panel it already uses.
`The Succession Question` (50 political power) opens the question the era is about and fires `spain_campaign.62`, which is answered by whichever part of the movement leads.
`The Pact of 1945` (75 political power, one firing) fires `spain_campaign.63`, which signs the settlement, writes the regime through the existing arbitration, and moves allied leverage far enough that the Marshall aid and the United Nations seat either stay open or close.
Historical AI in the Nationalist post-war chapter now follows a plan that names focuses of the tree that chapter actually loads.

## Changed paths

| Path | Change | Lines |
| --- | --- | --- |
| `common/decisions/spain_campaign.txt` | two new decisions inside `SPR_nationalist_factions` | 574-620 |
| `common/decisions/spain_campaign.txt` | `SPR_accept_the_marshall_aid` available gains the Falangist exclusion tooltip | 744-751 |
| `common/decisions/spain_campaign.txt` | `SPR_take_the_un_seat` available gains the settlement route | 770-786 |
| `events/spain_campaign.txt` | `spain_campaign.62` (three answers, decisive since the 2026-10-27 correction) and `spain_campaign.63`, inserted before the news block | 440-873 |
| `common/ai_strategy_plans/SPR_chapter_plans.txt` | `SPR_postwar_plan` re-pointed at the Republican chapter and `SPR_nationalist_postwar_plan` added | 116-171 |
| `common/script_constants/spain_campaign.txt` | appended one constant `succession_tension = 5` | 214-218 |
| `localisation/english/spain_campaign_l_english.yml` | the settlement section, 25 keys, UTF-8 with BOM, CRLF | 525-553 |
| `.tools/tests/test_spain_1945_settlement.py` | new suite, 161 checks, five mutants plus a HEAD negative control | new, gitignored |
| `docs/plans/spain/subagent_handoffs/settlement_1945.md` | this handoff | new |

Touched nothing else. `common/scripted_effects/spain_campaign_effects.txt` (S18), `common/national_focus/spain_republic_postwar.txt` (S17), the categories file, ideas, other localisation files and every Iran/RCH path are untouched in this run; they were read only.

## New ids, flags, keys and one constant

Decisions: `SPR_the_succession_question`, `SPR_the_pact_of_1945`.
Events: `spain_campaign.62`, `spain_campaign.63`. Both are gaps in the namespace, not highest-plus-one: `grep -rn "id = spain_campaign.62\|id = spain_campaign.63"` over `events/` returned nothing before the edit, and `hoi4.mod_index mode=next_id` would have answered `.103`, which is not a gap finder. `.62` and `.63` sit between `.61` (end of the post-war decade block) and the news block.
Flags written: `spain_succession_settled`, `spain_succession_falangist`, `spain_succession_military`, `spain_succession_monarchist`, `spain_settled_1945`, `spain_monarchy_recalled`.
Flags read: `spain_succession_settled` (succession decision gate, pact gate), `spain_settled_1945` and `spain_monarchy_recalled` (the new seat route), `spain_succession_falangist` (Marshall aid exclusion, Allied-settlement option), `spain_succession_military` (Allied-settlement option), `spain_succession_monarchist` (Allied and Crown settlement options).
`spain_monarchy_survived` stays a declared forward edge: it is read by the pact gate and has **no writer anywhere in the tree**, because it belongs to the C1 surviving-Crown route that has not shipped. In the current tree the pact can only open through `spain_succession_settled`.
New localisation keys: `SPR_the_succession_question(_desc)`, `SPR_the_pact_of_1945(_desc)`, `spain_postwar_chapter_tt`, `spain_succession_open_tt`, `spain_pact_open_tt`, `spain_falangist_excluded_tt`, `spain_settled_1945_tt`, `spain_campaign.62.t/.d/.a/.a.tt/.b/.b.tt/.c/.c.tt`, `spain_campaign.63.t/.d/.a/.a.tt/.b/.b.tt/.c/.c.tt`.
Appended constant: `succession_tension = 5`, used by the Crown answers in `.62` and `.63` when they add to `spain_nationalist_tension_carried`. No existing constant was reused for a new meaning and nothing was renumbered.

## Decision gates as shipped

`SPR_the_succession_question`: `date > 1945.1.1`, `spain_in_postwar_chapter` (inside `custom_trigger_tooltip = { tooltip = spain_postwar_chapter_tt ... }`), `NOT has_country_flag = spain_succession_settled` (inside `custom_trigger_tooltip = { tooltip = spain_succession_open_tt ... }`), `cost = 50`, `ai_will_do = { base = 25 }`, `complete_effect` fires `spain_campaign.62`.
`SPR_the_pact_of_1945`: `date > 1945.1.1`, the same chapter tooltip, `OR = { spain_succession_settled spain_monarchy_survived }` (inside `custom_trigger_tooltip = { tooltip = spain_pact_open_tt ... }`), `cost = 75`, `fire_only_once = yes`, `ai_will_do = { base = 20 }`, `complete_effect` fires `spain_campaign.63`.

Deviation from the card's literal `available` text, and why: criterion 1 shows the block with the bare triggers, criterion 7 forbids a flag name on screen. `spain_in_postwar_chapter` is a scripted trigger that expands to `has_country_flag = spain_chapter_postwar`, and there is no localisation for that flag anywhere in the mod, so the raw trigger renders the flag id. Both non-date conditions are therefore wrapped in `custom_trigger_tooltip` with new keys, exactly as installed vanilla does (`Hearts of Iron IV/common/decisions/AST.txt:458`). The triggers themselves are unchanged. Everything else in the block is literal.

## The succession event: who can answer, and why no faction can hold two spirits

| Scenario | Open option | Effect |
| --- | --- | --- |
| `spain_falange_leads` | `.a` | Falange +10, stability +0.10, war support +0.05, allied leverage -10 |
| `spain_army_leads` | `.b` | army +10, `spain_loyalty_gain_small` (loyalty +5, coup pressure -`coup_relief`), stability -0.05 |
| no faction at 30 | `.b` | same residuary answer, which is the same fallback the arbitration applies |
| `spain_monarchists_lead` | `.c` | the answering royal house +10 (the monarchists when they hold more), allied leverage +10, carried tension +5 |
| `spain_carlists_lead` | `.c` | the same answer, and it pushes the Carlists because they hold more, so the arbitration writes the Carlist state |

Proven by the suite: every scenario leaves exactly one option clickable, the Falangist scenario cannot reach `.b` or `.c`, and the army answer cannot be taken while the Falange leads.
No two regime spirits: no option in `.62` or `.63` calls `add_ideas`, every option routes through `spain_faction_resolve_regime` inside `hidden_effect`, and that effect removes all four regime ideas before its `if`/`else_if`/`else` chain adds exactly one. The suite asserts the four removals, the four adds, and that every add sits in an exclusive branch, so the arbitration cannot leave two spirits.
The army answer uses `spain_loyalty_gain_small`; no option writes `spain_coup_pressure` by hand (asserted), which keeps the sign convention stated at `common/scripted_effects/spain_campaign_effects.txt:653-670`.
`.62` is answered by a leading faction, and since the 2026-10-27 correction the answer itself establishes the regime: the answering faction is placed above the largest part of the movement and only parts that would tie it give way, before the shared arbitration reads the balance. See "Correction after the approved S19 diagnostic" below, which supersedes the earlier residual claim in this document.

## The settlement event and the 1945 payoff

`.63` options: `.a` Allied settlement (+20 allied, -10 Axis), `.b` the regime's own terms (-10 allied), `.c` the Crown recalled (+5 allied, carried tension +5, sets `spain_monarchy_recalled`).
Leverage threshold is `leverage_pressure = 40`. A Spain sitting exactly on 40 keeps the Marshall aid and the seat after `.a` and loses both after `.b`; `.c` moves it up by 5 and, with the new seat route, opens the seat even from below the threshold.
Payoff wiring, both inside this slice and inside `available` only:
`SPR_accept_the_marshall_aid` gained `NOT = { has_country_flag = spain_succession_falangist }` as a tooltipped requirement, so a Falangist answer closes American money.
`SPR_take_the_un_seat` now opens on `OR = { spain_allied_leverage_high AND = { spain_settled_1945 spain_monarchy_recalled } }`, so a Crown settlement reaches the seat without leverage while an unsettled Spain still needs leverage.
Everything else on both decisions is unchanged against HEAD, asserted block by block.

## A3: the AI plan split

Before (HEAD): `SPR_postwar_plan` at line 116 was enabled by `has_country_flag = spain_chapter_postwar` (the Nationalist chapter) and listed eleven `SPR4_*` focuses, which live only in `spain_republic_postwar_focus`. The plan could not be followed: the chapter loads `spanish_focus`.
After: `SPR_postwar_plan` is enabled and aborted on `spain_chapter_republican_postwar` and keeps its eleven `SPR4_*` ids byte for byte; `SPR_nationalist_postwar_plan` is enabled and aborted on `spain_chapter_postwar` and lists, in order, `SPA_the_national_syndicalist_state`, `SPA_the_national_and_popular_army_of_spain`, `SPA_national_recovery`, `SPA_join_the_axis`, `SPA_fascist_economic_aid`, `SPA_the_iberian_pact`, `SPA_settle_the_succession_question`.
That order is the order `spain_restore_past_focuses` completes the same branches in for a campaign that arrives by save (`common/scripted_effects/spain_campaign_effects.txt:1297-1325`), so the plan and the catch-up agree on what history did.
`SPA_join_the_allies` is deliberately absent: the tree gates it on `has_government = democratic`, which the Nationalist chapter does not hold, and a plan entry that can never open is the defect this card is fixing. A Spain without the Axis alignment idea simply skips `SPA_join_the_axis` and `SPA_fascist_economic_aid` and falls back to `ai_will_do`.
Machine check, not a hand list: the suite reads both focus files, extracts the focus ids of `spanish_focus` and `spain_republic_postwar_focus`, and asserts every id of each plan exists in its own tree, that no `SPR4_*` id appears in the Nationalist plan, that no `SPA_*` id appears in the Republican plan, and that no id of the Republican tree leaks into the Nationalist plan.

## Validation actually run

New suite, plain and `--detail`:
`python .tools/tests/test_spain_1945_settlement.py` → `161 checks, 0 failures`, exit 0.
Detail areas: decisions 24, succession event 43, settlement event 33, flags 17, localisation 5, ai plans 13, scope 17.
Scenario tables printed by `--detail`: `.62` open options are exactly `['spain_campaign.62.a']` for falange, `['spain_campaign.62.b']` for army, `['spain_campaign.62.b']` for none, `['spain_campaign.62.c']` for monarchists and for carlists. `.63` leverage deltas `{a: 20.0, b: -10.0, c: 5.0}` against threshold `40.0`.
Mutants, each rejected by the area that owns the claim: option without its faction trigger (8 failures in the succession area, e.g. "army leads: exactly one answer is open — got 2, expected 1"), pact without `fire_only_once` (decisions: "the pact signs once — got None"), pact date widened to 1944 (decisions: date gate `('>', '1944.1.1')`), deleted `spain_campaign.63.c.tt` (localisation: referenced key missing), plans with swapped chapter flags (ai plans: Nationalist plan enabled by `spain_chapter_republican_postwar`). Plus the pre-change tree at HEAD, where the decisions and both events do not exist and four areas fail.
The suite fails loudly on unmodelled input: `holds_entry` raises `Unsupported` for any trigger key outside the modelled set, `bare_words` and `focus_ids` raise on an empty parse, and `block_named` raises unless exactly one block matches.

Existing suites, exit codes, none edited: `test_spain_cortes_runtime.py` 0, `test_spain_cortes_recount.py` 0, `test_spain_cortes_postwar_bills.py` 0, `test_spain_coup_relief_sign.py` 0, `test_spain_restoration_loyalty.py` 0, `test_spain_turno.py` 0, `test_spain_hemicycle_builder.py` 0, `test_spain_postwar_catchup.py` 0.

MCP, read-only routes, workspace `endsieg`, documentation revision `9227e238bce49345e9c358598b4dd4940c733d906b72324e8a02a57ecb42093b`:
`hoi4.script_validate` on `common/decisions/spain_campaign.txt` → `SCRIPT_CHECKED`, `valid: true`, 342 commands checked, `unresolvedCount 0`, 79 argument blocks unchecked, 105 roots. 36 findings, all `SCRIPT_FLAG_TOOLTIP_UNLOCALISED`, and every reported line predates the slice (225-558, 707, 746, 787, 809, 830). None is in the new block at 574-620 or in the new gates at 744-786 other than the pre-existing `spain_un_founding` and `spain_marshall_plan` lines.
`hoi4.script_validate` on `events/spain_campaign.txt` → `SCRIPT_CHECKED`, `valid: true`, 240 commands checked, 53 roots; two warnings, both pre-existing colour codes in `spain_campaign.70.d` and `.71.d`.
`hoi4.script_validate` on `common/ai_strategy_plans/SPR_chapter_plans.txt` → `SCRIPT_CHECK_PARTIAL`, `family: "unsupported"`, 0 commands checked, `valid: null`. The installed validator has no strategy-plan family, so this file is source-reviewed and test-covered only. Not a pass.
`hoi4.event_inspect` trace on `spain_campaign.62` and on `spain_campaign.63` → `EVENT_INSPECTED_PARTIAL`, `analysisMode: "focused"`, 0 blocking diagnostics for the chain, revision `138bcd44667cf911a62c71b4c658364c258eb96119affff92d42df50c70ae476`, artifacts `event-trace-138bcd44667c.json` (uri logged on the card). Focused analysis disables the workspace-wide helper and lifecycle passes, so the zero helper count in that report is not evidence that the chain has no helpers.
`hoi4.source_lookup` `spain_faction_resolve_regime` → `definitionCount 1`, not overridden, 8 references: the pre-existing `SPR_unify_the_movement` and `spain_campaign.50`, plus the six new call sites at `events/spain_campaign.txt:474, 510, 539, 585, 606, 634`.
`hoi4.source_lookup` `SPR_the_pact_of_1945` → `definitionCount 1`, no duplicate, source text as shipped.
Not run: `hoi4.probability_inspect` / `probability_analyze` on the two decisions. The card records an adapter mismatch for those routes and forbids a retry, so the weights are stated as source scores (25 and 20, option weights 10-70) and not as probabilities. No decision was clicked and no AI plan was observed in a campaign.

## Residuals and things a reviewer should know

1. `spain_campaign.63` requires at least one option to be open. `.b` has no trigger, so the settlement can always be signed, and the suite asserts that under six scenarios including "nothing settled yet".
2. `.62` can fire with no faction above the lead threshold: it is answered by `.b`, the army's residuary answer. Until the 2026-10-27 correction that answer did not make the army the strongest faction, so the arbitration could install the Falange; the correction places the answering faction above the largest part of the movement and is covered by the execution area. See the superseding section at the end.
3. `spain_un_founding` (line 787) and `spain_marshall_plan` (line 746) still show as raw flag names in requirement tooltips of the two payoff decisions. They predate this slice and criterion 10 forbids changing more of those decisions than the sanctioned arm, so they were left alone and are reported here rather than quietly fixed.
4. `spain_monarchy_survived` is read and never written: an intentional forward edge to C1. Until C1 ships the pact opens only through the succession.
5. The AI plan cannot be validated by the installed MCP validator (unsupported family, 0 commands checked). The suite's tree-inventory check is the only machine evidence for the plan and it proves id existence, not AI behaviour at runtime.
6. Live game: **not performed**. No launch was authorised, so nothing here proves that the panel draws, that the decisions are clickable in 1945, that the options appear in the order intended, or that a 1945 campaign settles as described. Those stay unverified.
7. `.tools/` is gitignored, so the suite is validation evidence and not a committable artifact.
8. No commit, no branch or worktree operation, no push, no HOI4 launch, no MCP write route, no premium model.

## QA round 1 corrections

Round 1 returned three source-provable failures on this card and no others. All three are fixed inside the card's ownership, each with a new suite check and a matching mutant.

### 1. `s19-pact-decision-icon-unregistered`

`common/decisions/spain_campaign.txt:600` now sets `icon = generic_political_address` in place of `generic_foreign_policy`.
A decision icon resolves as `GFX_decision_<name>`, and no `GFX_decision_generic_foreign_policy` sprite exists in the installed game, in its DLC interface files or in the mod, so the old value could only render a fallback.
`GFX_decision_generic_political_address` is registered, and the file already uses it for two other decisions at `:43` and `:90`, so the pact now follows the family's own icon discipline rather than introducing a name that does not resolve.
The suite proves this instead of assuming it: `registered_decision_sprites()` parses every `GFX_decision_*` sprite name from `<HOI4>/interface`, `<HOI4>/dlc` and the mod's `interface` (602 names in this install, from the `HOI4_GAME_DIR` environment variable or the two standard Steam and Paradox install paths) and checks both new decisions against that set. It raises rather than passes when no interface folder is found.
Mutant `pact icon the engine cannot resolve` restores `generic_foreign_policy` and is rejected with `decisions: SPR_the_pact_of_1945 uses an icon the engine can resolve, icon 'generic_foreign_policy'`.

### 2. `s19-succession-decision-double-click`

`common/decisions/spain_campaign.txt:579` now sets `fire_only_once = yes` on `SPR_the_succession_question`.
The decision's only clearing condition was `NOT has_country_flag = spain_succession_settled`, and that flag is written solely by the three options of `spain_campaign.62`, which the decision queues with `days = 1`. The gate therefore stayed true for the whole day after the click, so nothing in the script prevented a second click that paid another 50 political power and queued a second answer with its own outcome flag, faction push, stability payload and arbitration run.
`fire_only_once` closes the window immediately and independently of when the queued event resolves, and it matches the family's own precedent (`SPR_unify_the_movement` in the same block, and the pact next to it).
The `available` block is unchanged, so criterion 1's gate text still holds verbatim.
Mutant `succession without fire_only_once` removes the line and is rejected with `decisions: SPR_the_succession_question can be taken once, got None, expected 'yes'`.

### 3. `s19-crown-answer-spirit-mismatch`

`spain_campaign.62.c` at `events/spain_campaign.txt:515` no longer pushes one fixed royal house.
It now pushes the house that holds more of the movement: `if = { limit = { check_variable = { spain_carlists > spain_monarchists } } add_to_variable = { var = spain_carlists ... } } else = { add_to_variable = { var = spain_monarchists ... } }`, at `:538-544`.
The tooltip at `localisation/english/spain_campaign_l_english.yml:543` was rewritten to match. It no longer promises a Bourbon restoration and no longer says the Carlists are handed a different king. It says the royal house that holds the movement gains ground, the law returns the state to a king, and the other claimant is left outside the settlement.
What this fixes is the case QA named: the Carlists alone above the lead threshold. Under the old text and push, the option added 10 to the monarchists, the arbitration installed `spain_carlist_state`, and the country held `spain_succession_monarchist` beside a tooltip describing the opposite. The Carlists now gain the ground, so the arbitration installs the Carlist state, which is the crown the answer actually named.
`spain_succession_monarchist` names the Crown answer as opposed to the Falangist or military answers, and both royalist spirits are crowns, so the flag, the text and the installed spirit now agree on that branch. The `.63` readers of the flag are unchanged.
The suite no longer models the arbitration: since the 2026-10-27 correction it parses and executes the shipped `spain_faction_resolve_regime` body, so these claims are executed source rather than a copied oracle. See the superseding section at the end.
Mutant `Crown answer pushing one fixed house` was retired in the 2026-10-27 correction and replaced by the coupled-preparation mutants listed in the superseding section at the end.

### Evidence after the corrections

`python .tools/tests/test_spain_1945_settlement.py` → `176 checks, 0 failures`, exit 0.
Areas: decisions 28, succession event 49, settlement event 33, flags 17, localisation 7, ai plans 13, scope 17.
Ten negative controls, all rejected: the HEAD tree (four areas fail), option without its faction trigger (8 failures), pact without `fire_only_once`, succession without `fire_only_once`, unregistered pact icon, Crown answer with the fixed push, pact date widened to 1944, deleted settlement tooltip, plans with swapped chapter flags.
The eight existing Spain suites were rerun, all exit 0, none edited.
Brace balance on the three edited script files: 375/375, 199/199, 36/36.
`hoi4.script_validate` `common/decisions/spain_campaign.txt` → `SCRIPT_CHECKED`, `valid: true`, 342 commands, `unresolvedCount 0`, 36 findings, all pre-existing `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` at lines no later than 558 and then 708 and beyond, so none inside 576-621. `hoi4.script_validate` `events/spain_campaign.txt` → `SCRIPT_CHECKED`, `valid: true`, 244 commands (four more than before, from the if/else), `unresolvedCount 0`, the two pre-existing colour warnings in `.70.d` and `.71.d`.
`hoi4.event_inspect` trace on `spain_campaign.62` and `.63` → `EVENT_INSPECTED_PARTIAL`, focused analysis, revision `6707616600d79c1c3f25323ddb1ced1039a4c075cbfc3d1d23536a7fec3db916`, 0 blocking diagnostics, artifacts `event-trace-6707616600d7.json`. Focused mode still defers helper and lifecycle passes, so its zero helper count is not evidence.

### Residuals after this round

The multi-lead residual stands and is unchanged: with two or more factions above the lead threshold, both the stronger faction's option and the Crown option can be open, and the arbitration still installs the strongest faction, so a player who picks the weaker answer can end with another faction's spirit. The slice declares this instead of claiming determinism, and fixing it would mean making every answer decisive over the balance, which is a design change outside this card.
`spain_un_founding` and `spain_marshall_plan` still render as raw flag names in the two payoff decisions. Both predate the slice.
`spain_monarchy_survived` is still a writer-less forward edge to C1.
The AI plan still has no validator family, so it stays source- and suite-checked only.
Live game: not performed. Panel drawing, icon rendering, decision clickability, the engine's own re-click behaviour and the settlement outcome remain unverified, and source review is not engine validation.

## Correction after the approved S19 diagnostic, 2026-10-27

Card: t_b0b0548f (DeepSeek correction linked to t_08b44a33 after diagnostic t_e83880e2).
Policy: `docs/specs/spain_1910_1945/continuation_1936_1945.md`, "Director ruling after the approved S19 diagnostic, 2026-10-27", committed as 2b15aad63.
Pre-edit baselines of the four reserved paths were verified against the recorded raw blob ids before writing; `git hash-object --no-filters` matched all four, so no unexplained drift was present.

### Root cause this round repairs

`spain_*_leads` are independent threshold flags written by `spain_refresh_faction_leadership` at 30 influence, while `spain_faction_resolve_regime` installs a regime only on a strict numerical maximum and falls back to the military directorate on a tie.
The three answers wrote an outcome flag and added `faction_gain_large` to one faction, which does not make that faction the maximum.
So a chosen answer could leave another faction's spirit: `F45/C25/M35/A20` with the Crown answer tied at 45 and installed the military directorate under a royal flag, and `F29/C15/M10/A5` with the army answer left the Falange at 29 and installed the Falangist state under a military flag.
The earlier round repaired only the royal-house selection and its text; the multi-lead mismatch, the no-lead case and the `.63.c` promise were left standing, and the suite encoded that gap instead of catching it.

### What changed, file by file

`events/spain_campaign.txt`, inside `.62` only:
each answer now computes the largest of the four influences (`spain_succession_top`), derives `spain_succession_result = min(top + faction_gain_large, faction_cap)` (`:487`, `:580`, `:674`), lowers every part that would tie or exceed that result to `result - faction_gain_large`, and only then places the answering faction at the result.
`.a` selects the Falange, `.b` the army, `.c` the stronger royal house with the monarchists answering a royal tie (`:652`, read before any influence moves so a reduction cannot flip the branch).
No option grants a spirit, writes `spain_regime_leader`, changes a constant, or touches upkeep; `spain_faction_resolve_regime` is called exactly once per option and is unmodified.
`spain_campaign.63.c` (`:795`) keeps its route prerequisites and additionally requires a royal house to be the current strict maximum, mirroring the arbitration's own comparisons, so a remembered royal succession cannot recall a crown after a takeover; `.63.b` remains unconditional and `.63` still applies no influence change.
`localisation/english/spain_campaign_l_english.yml`: the three `.62` tooltips (`:539` onward) now state the decisive consequence in-world, and `.63.c.tt` (`:551`) states the current-balance requirement.

`.tools/tests/test_spain_1945_settlement.py` no longer models the regime. It executes the shipped option bodies and the shipped `spain_faction_resolve_regime`, `spain_loyalty_gain_small` and `spain_clamp_campaign_variables` bodies, with `set_temp_variable`/`clamp_variable`/`check_variable` semantics taken from the offline wiki (`paradox_wiki/Data structures - Hearts of Iron IV Wiki.md`) and vanilla precedent (`common/decisions/AST.txt`), and it raises `Unsupported` on any construct it does not model.
The leadership thresholds and flags used by the fixtures are parsed out of `spain_refresh_faction_leadership`, not restated.

### Executed scenarios and what they assert

Sixteen coupled scenarios run through the real option plus the real arbitration: the exact Crown tie `F45/C25/M35/A20`, the Crown losing on numbers `F70/C20/M35/A25`, the no-lead Directory `F29/C15/M10/A5`, Falange-only, army-only, monarchist-only, Carlist-only, a royal-house tie, a civilian tie, all zero, the 30/29 threshold, everything at the cap, just below the cap, plus three stale-cache cases (a stale Falangist flag, a stale royal flag, and no flag at all over a real leader).
Each asserts: the chosen answer is offered; exactly one outcome flag is written and it is the chosen one; the resulting spirit is the one the answer names; the leader variable matches; the answering faction is the strict maximum; no part is above `faction_cap` or below zero; re-running the arbitration, then the real clamp helper, then the arbitration again keeps the same spirit and leader.
Every answer additionally runs from each of the four old regime spirits alone and from all four together and leaves exactly one matching spirit.
The Crown-recall area presents the current-balance requirement: the Crown form opens while a royal house holds the movement, closes after a Falange takeover with the settlement still signable through `.63.b`, keeps the royal regime when signed from a held balance, and the own-terms form recalls no crown.

### Actual results

`python -B .tools/tests/test_spain_1945_settlement.py` -> `454 checks, 0 failures`, exit 0.
Areas: decisions 28, succession event 43, settlement event 33, execution 254, crown recall 24, flags 17, localisation 7, ai plans 13, scope 17; plus the HEAD negative control and fourteen named mutants.
Mutants, all rejected: option without its faction trigger; pact without `fire_only_once`; succession without `fire_only_once`; unregistered pact icon; each of the three answers with its decisive preparation removed (22, 24 and 31 execution failures); the Crown answer reading the wrong royal house (52); answers allowed to overrun the cap (9); the arbitration keeping an old regime spirit (4); the Crown settlement without its royal-winner guard (2 in crown recall); pact date widened to 1944; deleted settlement tooltip; swapped chapter flags.
The cap mutant is what distinguishes a bounded step from an unbounded one: it leaves `spain_monarchists` at 200 in the all-at-cap scenario.
The eight existing Spain suites were rerun unmodified, all exit 0: cortes runtime 113, cortes recount 215, postwar bills 227, coup relief sign 127, restoration loyalty 146, turno 128, hemicycle builder 69, postwar catchup 2235 checks, zero failures each.

### MCP evidence this round

`hoi4.script_validate` on `events/spain_campaign.txt`, workspace `endsieg` -> `SCRIPT_CHECKED`, `valid: true`, 394 commands checked, `unresolvedCount 0`, 140 argument blocks unchecked, `parametersChecked: false`, 53 roots, documentation revision `9227e238bce49345e9c358598b4dd4940c733d906b72324e8a02a57ecb42093b`; two findings, both pre-existing colour codes in `spain_campaign.70.d` and `.71.d`.
`hoi4.event_inspect` trace on `spain_campaign.62`, direction both, helpers expanded -> `EVENT_INSPECTED_PARTIAL`, 0 blocking diagnostics, revision `46103640e2bed40da746400ccb27bd68b90f32e60659db09e4ee4c22131bfcc2`, artifact `event-trace-46103640e2be.json`; focused mode still defers workspace-wide helper and lifecycle passes, so its counts are not per-event proof.
`hoi4.source_lookup spain_faction_resolve_regime` -> `definitionCount 1`, not overridden, 8 references: the pre-existing `SPR_unify_the_movement` and `spain_campaign.50` plus the six `.62`/`.63` call sites.
`hoi4.source_lookup spain_succession_result` -> no definition (temporary variable) and 3 references, one per answer, at `:491`, `:584`, `:678`.
Not run: `probability_inspect`/`probability_analyze` (recorded adapter restriction; no capability change), and no write route.

### Still unverified, and residuals

Live game: not performed and not authorised here. Engine option availability, the actual idea add/remove, popup tooltips, AI option choice and campaign behaviour remain unverified; the interpreter proves what the script says, not what the engine does.
The AI weights and the two payoff decisions are untouched by this round.
`spain_un_founding` and `spain_marshall_plan` still render as raw flag names in the two payoff decisions; both predate S19.
`spain_monarchy_survived` remains a writer-less forward edge to C1.
The AI plan still has no validator family, so it stays source- and suite-checked only.
No commit, staging, branch, push, merge, launch or new card was made; the original t_08b44a33 stays blocked for Director and independent QA.
