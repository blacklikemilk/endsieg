# C9 implementation handoff — Republic pressure and earned succession

Task `t_22f1a4e8`, assignee `endsieg-developer`, model `deepseek-v4.1-flash` / `opencode-go`.
Binding contract: `docs/specs/qing_1910_1945/republic_succession.md` (accepted, read-only for this card).
Branch `TeknoDev-Branch`. No commit, no staging, no branch action, no launch.
Git was rechecked immediately before the first write: the only dirty paths were the parallel Spain/Iran session's (`common/decisions/spain_campaign.txt`, four `common/national_focus` files, two `common/scripted_effects` files, one Spain localisation file, one `.pyc`, `docs/plans/campaign/`, `docs/plans/spain/subagent_handoffs/`). None is in this card's ownership and none was touched.

## Changed paths

| Path | Change |
| --- | --- |
| `common/script_constants/rch_campaign.txt` | 47 new `rch_story` keys: succession arithmetic, thresholds, display bands and offsets, card costs and deltas, throne payloads, route-keyed AI weights |
| `common/scripted_triggers/rch_campaign.txt` | new `rch_gate_constitution`, `rch_gate_officer_rotation`, `rch_gate_civil_governors`, `rch_gate_treasury`, `rch_gate_throne_refused`, `rch_gate_settled_count`, `rch_succession_governors_below_three`, `rch_succession_collapse`, `rch_chinese_war`, `rch_succession_tier_0`, `rch_succession_tier_1` |
| `common/scripted_effects/rch_campaign.txt` | new `rch_settlement_snapshot`, `rch_succession_refresh`, `rch_succession_evaluate`, `rch_succession_seat_spirit`, `rch_succession_settle`, `rch_succession_resolve`, `rch_succession_endow`, `rch_beiyang_bootstrap`, `rch_beiyang_refresh`, `rch_governor_increment` and the eight `rch_press_*` effects; edits to `rch_refresh_mechanics`, `rch_initialize_campaign`, `rch_campaign_tick` |
| `common/bop/RCH.txt` (new) | `RCH_beiyang_order`, sides `RCH_side_civil` / `RCH_side_military`, five ranges, `decision_category = rch_beiyang_order_category` |
| `common/decisions/categories/rch_campaign.txt` | new `rch_beiyang_order_category`, not DLC-gated |
| `common/decisions/rch_campaign.txt` | `rch_beiyang_order_category` block with the eight cards |
| `events/rch_campaign.txt` | new `rch_campaign.2` and `rch_campaign.42`; `rch_campaign.5` rewritten into four exclusive tier options with no `immediate` and no `ai_chance` |
| `common/ideas/rch_campaign.txt` | four seat spirits |
| `localisation/english/rch_campaign_events_l_english.yml` | `.5.*` rewritten, `.2.*` and `.42.*` added |
| `localisation/english/rch_campaign_l_english.yml` | category name and description, `rch_press_family_available`, the eight balance-panel identifiers, eight card names and descriptions, four spirit names and descriptions |
| `docs/systems/rch_campaign.md` | new "The 1915 settlement and the 1916 succession" section |
| `.tools/tests/test_rch_succession.py` (new) | executing harness |
| `docs/plans/qing_1910_1945/republic_fragmentation.md` | disposition section only; no redesign, no later-slice retirement |
| this file (new) | handoff |

## Behaviour

- **Cards.** Eight decisions in `rch_beiyang_order_category`. Civil constitution 50 PP, army 45 PP and 25 army XP, provinces 40 PP, money 45 PP; every military card 35 PP. Deltas exactly as the revision-four table. Each family sets one shared lock, both sides carry the same lock clause inside a `custom_trigger_tooltip`, and both sides have `days_re_enable = 180`.
- **Gates and governors.** A civil card clears and re-sets its gate, so a re-earned reform restarts its date. The military card in the family clears the gate. `rch_governor_count` is clamped to 0..3 after every increment and does not reuse the existing `rch_military_governors` flag.
- **Settlement.** `rch_campaign_tick` takes one snapshot on 12 December 1915 (`rch_settlement_taken`), counting only gates older than 180 days, and offers `rch_campaign.42` once in 12–31 December 1915.
- **Endowment.** A start at or after 1 January 1916 receives `rch_hongxian`, `rch_throne_choice_seen` and a sealed zero snapshot. A start after 5 June 1916 resolves silently at initialisation with no popup.
- **Resolution.** The tick owns it on the first day after 5 June 1916: refresh, evaluate, freeze `rch_succession_final_score` and `rch_succession_final_tier`, one line flag, one seat spirit, clear `rch_hongxian`, and only then queue `rch_campaign.5` with `days = 1`. The popup's `immediate` is removed and each option triggers on exact tier equality.
- **Refresh safety.** `rch_refresh_mechanics` removes and reapplies the seat spirit from the frozen line flag, so a later refresh cannot delete it.
- **Display.** `rch_beiyang_refresh` reads `rch_military_influence`, creates the panel once under the DLC, and publishes one of five literal offsets with `add_power_balance_value`, retiring the previous band from `rch_bop_band`. It is called daily from the tick and from `rch_refresh_mechanics`, so existing focus, decision and event writers are mirrored within a day. Without *Arms Against Tyranny* no balance command runs and every card and outcome is unchanged.
- **AI.** Route-keyed `ai_will_do` blocks: civil 3/2/1 and military 1/1/2 for parliamentary, KMT and provincial, and zero for the Beiyang route (no modifier matches it). The throne option weights are 4 accept and 1 refuse.

## Test evidence

`python .tools/tests/test_rch_succession.py` exits 0 with `all checks passed`.

The harness imports only the tokenizer and block parser from `.tools/tests/test_qing_survival.py` (unmodified) and executes the shipped Clausewitz blocks. It raises `Unsupported` on any command it does not model. Every claim is a named statement in a record. Sections: `cards`, `chapters`, `costs`, `succession`, `precedence`, `maturity`, `idempotence`, `referential integrity`, `display`, `constant and literal mirrors`, `family locks`, `gate tenure`, `daily tick`, `effect handler models`, `mutants`, `localisation mutants`, `anti-exploit mutants`, `handler mutants` and `baseline control`.

Covered and passing:

- eight cards, each with its published deltas, `ai_will_do`, `days_re_enable` 180 and the family-lock tooltip;
- five emergency rows `(35,45,30) (41,45,34) (45,37,34) (51,37,34) (57,37,34)` to scores 35/38/42/44/46 and tiers 2/2/2/2/1;
- full civil `(62,37,38)` plus four settled reforms and the refused throne to 88 and tier 0;
- three civil `(56,37,38)` to 78 and tier 1;
- all military `(18,77,20)` with three governors to a clamped 0 and tier 3;
- boundaries 44/45 and 69/70 on the shipped triggers, and tier-trigger exclusivity in four states including the collapse override;
- settlement boundary: gates dated 1915.6.14 count 4, gates dated 1915.6.15 count 0 (the strict comparison, not the proposal's "three" fixture);
- sealed 1916 start (zero snapshot, Hongxian inherited, refusal gate impossible) and silent 1918 start (resolved, no popup);
- three same-day resolves queue one popup, freeze one tier, apply one seat spirit, and a later `rch_refresh_mechanics` neither changes the frozen score nor deletes the spirit; the same run also proves the values are the shipped 88 and tier 0, and a second fixture proves a collapsed succession freezes tier 3;
- the seat effect run against a standing earlier seat and an unrelated idea: the earlier seat is replaced, exactly one seat stands, and the unrelated idea is untouched;
- chapter routing: each opener run with the other two chapter flags already standing leaves exactly its own chapter flag and loads its own tree;
- costs: the civil constitution bargain raises stability and the civil treasury bargain lowers it, read from the shipped constants;
- display: panel created once, unchanged band publishes nothing, 65 to 80 publishes `-0.25` then `+0.85`, 80 to 20 publishes `-0.85` then `-0.85`, no-DLC run performs no balance command and still resolves tier 3;
- mutants: `succession_tier1_score` 45 to 44, `pressure_legitimacy_gain` 6 to 7, maturity `days > 180` to `days > 0`, and a deleted governor `clamp_variable` are each caught;
- baseline control: `git show HEAD:` of the effects file contains no `rch_succession_settle`, so the suite cannot pass vacuously against pre-implementation source.

Regressions run and passing:

- `.tools/tests/test_qing_survival.py` — `all checks passed against f6d12527cc8a; the baseline mutant is rejected`.
- `.tools/tests/test_qing_consolidation.py` — `all checks passed against 7136c90a37a1; the baseline mutant is rejected`.
- `tools/china_audit.py` — exit 0, 468 focuses, 57 events in `qing_campaign` and `rch_campaign`, 72 decisions, 34,327 localisation keys, 0 missing focus keys. Its one reported problem is 16 unlocalised `PER_*` decisions from the parallel Iran session, outside this card's ownership and untouched.

## MCP evidence

Pre-edit baseline:

- `hoi4.source_lookup` (`symbol: rch_refresh_mechanics`, `includeReferences: true`, revision `9a8ab2a90bfce956…`): one definition at `mod:common/scripted_effects/rch_campaign.txt:5-55`, seven callers (initialisation `:92`, chapter openers `:113`/`:123`, route settlements `:370`/`:385`/`:400`/`:415`), no daily caller, `referencesComplete: false`, 2,570 unresolved.
- `hoi4.event_inspect` (`mode: trace`, `selector rch_campaign.5`, revision `33196bbabcc7…`): `EVENT_INSPECTED_PARTIAL`, `analysisMode: focused`, 9,316 events, 14,569 options, 2,414 diagnostics, 0 blocking. Resource `hoi4-agent://workspace/endsieg/artifact/d7ad817f56a2cc11…/41ebc69f51bb7cb9…/event-trace-33196bbabcc7.json`. Focused analysis returns workspace counts only, so the `.5` option shape came from reading `events/rch_campaign.txt` directly.
- `hoi4.mod_index` (`mode: next_id`, `kind: event`, `namespace: rch_campaign`, `layer: all`): used 18, highest 41, `nextId rch_campaign.42`, `firstGapId rch_campaign.2`. Both ids were free and are the two used.
- `hoi4.focus_inspect` (`treeId: rch_republic`, revision `cecf9603ed5e9662…`): 51 focuses, `layoutHash 650779d3f13499f749e352949f6bf957e6f5678746420deac838fcd1e1bd2ed9`, 0 too-close same-row pairs, 3 crossings, 18 non-blocking `FOCUS_TREE_NOT_FOUND` sweep warnings.

Post-edit:

- `hoi4.script_validate` `path: common/decisions/rch_campaign.txt` — `SCRIPT_CHECKED`, `valid: true`, 209 commands, 0 findings, 29 argument blocks unchecked, 111 roots, 0 unknown-scope roots.
- `hoi4.script_validate` `path: events/rch_campaign.txt` — `SCRIPT_CHECKED`, `valid: true`, 68 commands, 0 findings, 30 argument blocks unchecked, checks include `player_text` and `event_popups`.
- `hoi4.script_validate` `path: common/scripted_effects/rch_campaign.txt` — `SCRIPT_CHECK_PARTIAL`, 577 commands, 0 findings, 144 argument blocks unchecked, 38 roots all reported as unknown-scope roots because a scripted-effect file declares no scope. `SCRIPT_CHECK_PARTIAL` is the tool's own coverage statement, not a defect finding.
- `hoi4.script_validate` `path: common/scripted_triggers/rch_campaign.txt` — `SCRIPT_CHECK_PARTIAL`, 70 commands, 0 findings, 11 argument blocks unchecked, 28 unknown-scope roots for the same reason.
- `hoi4.focus_inspect` (`treeId: rch_republic`, post-edit revision `2984a248bdaf419b…`): 51 focuses and the identical `layoutHash 650779d3…`, so no focus file moved.
- `hoi4.source_lookup` (`symbol: rch_succession_refresh`, revision `ce960ab4cacc359c…`): one definition at `:539-568`, one recorded caller (`rch_succession_settle`, `:622`), `referencesComplete: false` with 2,582 unresolved, so the caller list is a sample and not proof of the full call graph.
- `hoi4.event_inspect` (`mode: trace`, `selector rch_campaign.42`, revision `c2b0f91701fc…`): `EVENT_INSPECTED_PARTIAL`, `analysisMode: focused`, 9,318 events, 14,572 options, 2,416 diagnostics, 0 blocking. Resource `hoi4-agent://workspace/endsieg/artifact/4ec05ad3486569e6…/32d56d605e340329…/event-trace-c2b0f91701fc.json`.

Not run: `hoi4.decision_inspect` and `hoi4.probability_analyze`. Both were reported unavailable in the accepted design (adapter 1.19.2.0 against installed game 1.19.3.0); that mismatch is recorded here rather than retried. Their absence means the card visibility, availability, cost rows and the AI weight ordering are proved by source and by the executing harness only.

## Deliberate residual limits

- No launch, so nothing here is engine or live evidence. The panel has never been rendered, the popup never presented, the category never seen, and no campaign has been played to 1916. Visual acceptance is not claimed.
- The balance-of-power ranges carry no `modifier` block. Whether a modifier-less range parses is the design's open gate G2a and is not proved by source.
- The display publishes deltas rather than absolute values, so at a clamped extreme the panel can sit one band away from the dial; the accepted design chose delta publication over repeated `set_power_balance` for exactly this reason.
- `rch_chinese_war` enumerates the Chinese tags that exist in `common/country_tags` (CHI, GDC, GXC, PRC, QIN, SHX, SIK, SND, XSM, YUN) and deliberately excludes MAN, because a war with Manchukuo is a war with Japan. A Chinese tag added by a later slice must be added to that trigger.
- `controls_state = 608` and `days > 180` are literals because those fields take no constant; `succession_capital_state` and `succession_gate_maturity_days` declare the intended values and the harness asserts the arithmetic they produce.
- `rch_campaign.2` (the introduction) is fired once from initialisation and has one acknowledgement option. It is presentation only.
- The tier is a variable plus one line flag. No tag is released, no state transferred, no leader changed, no focus tree touched. Later territorial, leader and clique obligations in `docs/plans/qing_1910_1945/republic_fragmentation.md` remain open and untouched.
- The `rch_military_governors` focus flag and all existing chapter routing, focus rewards, layouts and icons are unchanged; `tools/china_audit.py` reports no missing focus keys and the focus layout hash is identical.

## QA round 1 corrections (run 156)

QA rejected two player-visible defects at run 153. Both were real. Both are fixed inside the existing fourteen-path reservation, with no new path, no cost, delta, lock, AI weight, id or focus change.

| Problem key | What was wrong | Correction |
| --- | --- | --- |
| `rch_bop_panel_localisation_missing` | `common/bop/RCH.txt` declares `RCH_beiyang_order`, `RCH_side_civil`, `RCH_side_military` and five `RCH_bop_*` ranges, and no English key existed for any of them, so the panel would have drawn raw identifiers for its title, both sides and every band label | Added the eight keys to `localisation/english/rch_campaign_l_english.yml:82-89`, beside the category they belong to, BOM and LF endings preserved |
| `rch_press_family_available_tooltip_inverted` | The text read "This family of cards has already acted in the last 180 days" while being attached to the availability clause of all eight cards, so a satisfied requirement stated the blocked condition | Reworded to the requirement it draws: "The government has not pressed this matter in the past six months." No day count, no card vocabulary, no tuning rule in player text. No card condition changed |

Panel labels: `RCH_beiyang_order` "The Beiyang Order", `RCH_side_civil` "The Civil Government", `RCH_side_military` "The Military Governors", `RCH_bop_settlement` "The Shared Presidency", `RCH_bop_civil_ascendant` "The Ministries Ascendant", `RCH_bop_civil_supremacy` "Government by the Assembly", `RCH_bop_military_government` "The Commanders in the Cabinet", `RCH_bop_military_supremacy` "Rule by the Garrison".

### Harness coverage added

`.tools/tests/test_rch_succession.py` now reads the identifiers rather than trusting the handoff:

- `panel_ids()` parses `common/bop/RCH.txt` (comments stripped) for the balance title, `left_side`, `right_side` and every `id =` and asserts exactly eight identifiers.
- `panel_loc_missing()` fails the run and names each panel identifier that has no English key.
- `family_lock_attachments()` asserts all eight cards still attach `rch_press_family_available` and that each one ages its own family flag (`NOT has_country_flag = X` against `flag = X`).
- `family_lock_defects()` is the predicate for the tooltip wording: missing key, the word `already`, the word `cards`, the number `180`, or a text without `has not` are each a defect.
- New `localisation mutants` section proves the checks bite: dropping the side and range keys leaves seven raw identifiers, restoring the old blocked-state wording is caught, and moving one card off the shared tooltip is caught. The shipped text passes the same predicate, so the checks are not vacuous.

`python .tools/tests/test_rch_succession.py` exits 0, `all checks passed`, with the new `localisation mutants` section reporting six passes.

### MCP evidence for the correction

- `hoi4.source_lookup` `path: common/bop/RCH.txt`, `line: 5` (revision `6bdd33f07db0f07dc1bef2a86804e8aaf0d9f11786a146989d718f9dd4359ce7`): the line parses as `RCH_beiyang_order = {` at `loadOrder 47`, `shadowed: false`, `chain [5-50]`. The panel id is the only owner.
- `hoi4.source_lookup` `path: localisation/english/rch_campaign_l_english.yml`, `line: 82` (revision `f28e0484c991beef68dc4e91e022abc12086e39d0f098194432a2cbf357563ad`): owner `l_english:RCH_beiyang_order`, `overridden: false`. Same route at `line: 84` returns owner `l_english:RCH_side_military` and at `line: 89` owner `l_english:RCH_bop_military_supremacy`, both not overridden.
- `hoi4.script_validate` `path: common/decisions/rch_campaign.txt`: `SCRIPT_CHECKED`, `valid: true`, 209 commands, 0 findings, 111 roots, 0 unknown-scope roots. The card file is unchanged by this correction and still validates.
- `hoi4.script_validate` `path: common/bop/RCH.txt`: `SCRIPT_CHECK_PARTIAL`, family `unsupported`, 0 commands checked. Recorded as unsupported coverage, not a pass.
- Localisation keys are not a `script_validate` family, so the English file is covered only by the owner lookup above and by the executing harness. Nothing in this correction is claimed as engine evidence.

### Unverified after the correction

- No launch, so the panel labels, the tooltip sentence and the popup have still never been drawn in game. Visual acceptance is not claimed.
- Whether the engine resolves the eight keys case-sensitively is untested here. The keys are written in the exact case the `bop` ids use, which is safe either way.
- The tooltip says "in the past six months" while the gate is `pressure_cooldown_days = 180`. Six months is one to four days longer than the gate, so for that short window the line can still read unmet while the sentence implies the window has passed. The exact day count was kept out of player text on instruction; the alternative wording (naming 180 days) was rejected for that reason.
- `hoi4.decision_inspect` and `hoi4.probability_analyze` remain unavailable at the recorded adapter mismatch and were not retried.
- Every residual limit listed above still stands.

## QA round 2 corrections (run 163)

QA rejected one problem key at run 159: `rch_harness_antiexploit_guards_unproven`, with three failed checks and the root cause stated accurately, the shipped script was right, the proof was not. The family lock was asserted as text with a wildcard day count, no section executed a lock in either direction, no section executed a gate clear-then-re-earn, and no mutant touched a family lock or the mirrored constants. The correction is the harness, plus one source hardening the executed lock scenarios exposed.

| Failed check | Defect | Correction |
| --- | --- | --- |
| `family_lock_release_executed` | Lock loosened to `days > 0` in all eight cards still passed | `availability_defects()` executes each card's `available` block with its lock absent, fresh, exactly at `rch_story.pressure_cooldown_days` and one day past it. The window comes from the constant, not from the literal under test, so a loosened literal fails |
| `gate_tenure_reset_executed` | Deleting `clr_country_flag = rch_gate_constitution` still passed | `tenure_defects()` runs all eight press effects with every gate and lock aged 400 days and reads the executed trace: each press must clear its own gate and its own lock before setting them, leave the gate dated at the press, leave a military bargain with no gate standing, and touch no other family's gate |
| `constant_literal_mirror_asserted` | `pressure_cooldown_days` 180→200 and `succession_capital_state` 608→611 still passed | `mirror_defects()` compares every `days_re_enable`, every lock window, the settlement maturity window and every `controls_state` literal with the constant each one documents |

The executed lock scenarios exposed one real source defect that no earlier pass had proved. A press re-set its family lock but never cleared it, and `set_country_flag` on a flag that already exists does not reliably restart its date: on the strict reading of the documented "last set date" wording, the second term of a family left the lock dated at the first press, so the other side of that family opened 181 days after the first press instead of 180 days after the later one. `common/scripted_effects/rch_campaign.txt` now clears each family lock before setting it, in all eight press effects, exactly as the gates were already handled. No cost, delta, cooldown, window, AI weight, id, tooltip or focus changed. under the looser engine reading the extra clear is a no-op and the behaviour is identical.

### Harness coverage added

- `mirrors()` / `mirror_defects()`, the four literal families listed above, parsed from the shipped blocks.
- `locks()` / `availability_defects()`, 32 executed availability evaluations, four per card, plus `lock_rearm_defects()`, which presses the same family twice a term apart and requires the lock date to move to the later press and the other side to stay blocked.
- `tenure()` / `tenure_defects()`, eight executed press effects with a trace-based clear-before-set proof and cross-family isolation.
- `daily_tick()`, executes `rch_campaign_tick` itself on 1916.6.6 and on a quiet 1917.1.2 day. The first proves the tick settles, records the resolution, queues exactly one `rch_campaign.5`, republishes the display and is silent on a repeat call. the second proves the daily refresh is the tick's own call and not a side effect of the chapter opener, which is what the deleted-refresh mutant needs.
- `guard_mutants()`, six hostile edits, each of which must be caught, and each of which is also caught when applied to a real scratch copy of the tree rather than in memory.
- `baseline_control()` now runs the whole suite against the `HEAD` version of all ten inputs through `RCH_TEST_ROOT` and requires a named failure there, replacing the old `git show` substring test.
- The interpreter gained `has_focus_tree`, `original_tag`, `load_focus_tree`, `mark_focus_tree_layout_dirty`, an executed flag trace, and scalar forms of `has_political_power` / `has_army_experience`, so the tick and the card availability run for real. Any other unmodelled command still raises `Unsupported`, and `main()` turns that into a named failure rather than a traceback.

### Test evidence for the correction

- `python .tools/tests/test_rch_succession.py` exits 0, `all checks passed`, fourteen sections, including `constant and literal mirrors`, `family locks`, `gate tenure`, `daily tick`, `anti-exploit mutants` and `baseline control`.
- `baseline control` reports `the pre-implementation source fails this suite (exit 1)` and the baseline run's own named failure (`rch_beiyang_order_category is not defined`), so the same suite cannot pass on the tree without the slice.
- Six tree-level mutants were run on scratch copies of the shipped tree, not only in memory, and each fails with a named check:

| Mutant | Exit | Failing check |
| --- | --- | --- |
| all eight locks `days > 180` → `days > 0` | 1 | `each family lock blocks at 0 and 180 days and releases at 181` |
| `clr_country_flag = rch_gate_constitution` deleted | 1 | `every press clears its gate and lock before re-setting them` |
| `pressure_cooldown_days = 200`, `succession_capital_state = 611` | 1 | `every engine literal mirrors its constant` |
| daily `rch_beiyang_refresh` deleted from the tick | 1 | `a quiet day with no chapter, settlement or succession work still publishes the display` |
| all eight `clr_country_flag = rch_press_lock_*` deleted | 1 | `a second term re-arms the family lock at the press date` |
| clean shipped tree, same mirror | 0 | none |

- `python .tools/tests/test_qing_survival.py` exit 0, `python .tools/tests/test_qing_consolidation.py` exit 0, `python tools/china_audit.py` exit 0 with 468 focuses, 72 decisions and 0 missing focus keys. The audit's only problem is still the 16 unlocalised `PER_*` decisions from the parallel Iran session, outside this card.

### MCP evidence for the correction

- `hoi4.script_validate` `path: common/scripted_effects/rch_campaign.txt` → `SCRIPT_CHECK_PARTIAL`, 585 commands checked, 0 findings, 144 argument blocks unchecked, 38 unknown-scope roots, documentation revision `9227e238…`. Recorded as unresolved coverage, not a pass.
- `hoi4.script_validate` `path: common/decisions/rch_campaign.txt` → `SCRIPT_CHECKED`, `valid: true`, 209 commands, 0 findings, 111 roots, 0 unknown-scope roots. The card file was not edited this round and still validates.
- `hoi4.source_lookup` `symbol: rch_press_constitution_civil` (index revision `dade6ccd…`) → two definitions, decision `common/decisions/rch_campaign.txt:400-426` and scripted effect `common/scripted_effects/rch_campaign.txt:775-784`, neither overridden or shadowed. the effect text shows `clr_country_flag`/`set_country_flag` for the gate and the lock. one `scripted_helper_call` from the decision at `:418`. `referencesComplete: false`, 2,582 unresolved references in the workspace index.
- `hoi4.source_lookup` `symbol: rch_press_lock_constitution` → 0 definitions, because country flags are not script symbols in that index. Recorded as unsupported coverage. the flag is proved by execution, not by lookup.
- `hoi4.decision_inspect` and `hoi4.probability_analyze` remain blocked at the recorded adapter mismatch (1.19.2.0 against game 1.19.3.0) and were not retried.

### Unverified after this correction

- No launch, so nothing below is engine evidence: the lock, the tenure and the tick are proved by a Python model of the shipped blocks, not by the game. The flag-date reading is the one place a model could part from the engine, and the clear-before-set pair is what makes the shipped script correct under either reading.
- Every residual limit listed above still stands, including the unproven `constants` support inside `ai_will_do` and the unsurfaced score and per-reform maturity.

## QA round 3 corrections (run 173)

QA rejected one problem key at run 169: `rch_harness_idea_removal_unmodelled`, count 1. The reading was correct and the defect was real. `idea_names()` returned the whole parsed entry `('scalar', <id>)` for a block-form `add_ideas` / `remove_ideas`, so `remove_ideas` removed nothing, `add_ideas` inserted tuples, and the spirit-persistence claim could not fail. It passed because it could not observe removal, not because the shipped script was wrong.

| Failed check | Defect | Correction |
| --- | --- | --- |
| `idea_names_block_ids` | Block form yielded `('scalar', name)` tuples, so removal was a no-op and additions were tuples | `idea_names()` now takes the scalar identifier out of each block entry and raises `Unsupported` on any entry shape it does not model |
| `spirit_refresh_persistence_executed` | Deleting `rch_succession_seat_spirit = yes` from `rch_refresh_mechanics` still printed `all checks passed` | `spirit_record()` resolves with an earlier seat already standing, then runs two mechanics refreshes and requires the shipped 88, tier 0, one seat spirit and survival of both the score and the spirit |
| harness sweep | Bookkeeping handlers were trusted rather than probed | `handler_models()` probes every effect handler the suite books a claim on, and `handler_mutants()` gives each of them a source mutant through the same record |

### What the suite now proves about its own model

`handler_models()` runs a synthetic probe for every handler the suite leans on: the five arithmetic commands, the clamp, the round, the flag set (including the strict "an existing flag keeps its date" reading), the flag clear (flag and date), block and single `add_ideas`, block `remove_ideas` (the named id goes, the unrelated idea stays), panel creation, one published offset, the queued event with its delay, the focus tree, the layout-dirty no-op, stability, political power and army experience, plus one isolation check that no arithmetic command touches a second variable. A handler that stops booking fails there directly.

`handler_mutants()` then mutates the shipped source once per handler and requires a named defect from the same record the clean tree passes. Each mutant also asserts that it actually edited the shipped text, so a drifted fragment fails loudly instead of passing quietly.

| Mutant | Record claim it must break |
| --- | --- |
| `set_variable` frozen score deleted | `the frozen score is 88` |
| `set_variable` frozen tier deleted | `a collapsed succession freezes tier 3` |
| `add_to_variable` legitimacy cap term deleted | `full civil scores 88` |
| `subtract_from_variable` military term deleted | `full civil scores 88` |
| `multiply_variable` gate weight deleted | `full civil scores 88` |
| `divide_variable` divisor deleted | `full civil scores 88` |
| `round_variable` on the base deleted | `emergency 45/37/34 scores 42` |
| `clamp_variable` on the score deleted | `military collapse scores 0` |
| `set_country_flag = rch_line_unified` deleted | `the settlement leaves exactly one seat spirit` |
| all `clr_country_flag = rch_chapter_*` deleted | `rch_open_chapter_one leaves only rch_chapter_one` |
| `add_ideas = rch_succession_constitutional` deleted | `the settlement leaves exactly one seat spirit` |
| the seat `remove_ideas` block deleted | `the seat spirit replaces an earlier seat` |
| `set_power_balance` deleted | `the panel is created once` |
| one published `add_power_balance_value` deleted | `military 65 publishes the upper band` |
| `country_event` `rch_campaign.5` deleted | `three same-day resolves queue one popup` |
| all `load_focus_tree` lines deleted | `rch_open_chapter_one loads rch_republic` |
| `add_stability` deleted from the constitution press | `the constitution bargain gains stability` |
| `pressure_stability_cost` sign flipped | `the treasury bargain costs stability` |

`add_political_power`, `army_experience` and `mark_focus_tree_layout_dirty` are probed by `handler_models()` but carry no gameplay claim of their own, so they get no mutant. That is stated here rather than implied.

### QA's two named mutants, re-run outside the deliverable

Both were reproduced against scratch copies of the shipped tree, not in memory.

| Mutant | Command | Result |
| --- | --- | --- |
| `rch_succession_seat_spirit = yes` deleted from `rch_refresh_mechanics` (line 60) | `RCH_TEST_ROOT=<scratch> python .tools/tests/test_rch_succession.py --no-baseline` | exit 1, `FAIL the settlement leaves exactly one seat spirit -> it leaves []` and `FAIL a mechanics refresh cannot delete the seat spirit -> it leaves []` |
| `idea_names()` restored to the tuple form (the model QA found) | copied suite against its own tree | exit 1, `FAIL remove_ideas removes the named id from a block and nothing else`, `FAIL add_ideas adds bare identifiers from a block`, and three seat claims naming `['rch_succession_constitutional', 'rch_succession_dissolved']` |

### Test evidence for this correction

- `python .tools/tests/test_rch_succession.py` exits 0 with `all checks passed`, nineteen sections, 259 named checks in `--detail`.
- `baseline control` still fails the pre-source tree with a named check, so the suite cannot pass on the tree without the slice.
- `python .tools/tests/test_qing_survival.py` exit 0, `all checks passed against f6d12527cc8a; the baseline mutant is rejected`.
- `python .tools/tests/test_qing_consolidation.py` exit 0, `all checks passed against 7136c90a37a1; the baseline mutant is rejected`.
- `python tools/china_audit.py` exit 0. Its one problem is still the 16 unlocalised `PER_*` decisions from the parallel Iran session, outside this card and untouched.

### Documentation reconciled

- `docs/systems/rch_campaign.md` now lists what the harness executes, states that each handler claim is probed and carries a mutant, and states the model limits plainly: no decision-cost debit, no event, mission or MTTH scheduling, no panel, popup, focus-tree or tooltip rendering.
- This handoff's covered list and section list were corrected to match the shipped harness, and the earlier overclaim about executed spirit survival is replaced by the record above.

### Unchanged by this correction

No file outside `.tools/tests/test_rch_succession.py`, `docs/systems/rch_campaign.md` and this handoff was edited. No card cost, delta, lock, cooldown, AI weight, decision id, event id, idea id, localisation value, focus or balance range changed.

### Still unverified

- No launch, so the panel, the tooltip and the popup have never been rendered and no campaign has been played into 1916.
- The model is a single-country interpreter. It does not debit a decision's `cost`, does not schedule the queued popup or any MTTH, and cannot observe the engine's own flag-date semantics, which is why the shipped script clears before setting.

## Round-4 correction: `rch_succession_display_contract_unexposed`

QA rejected one problem key in the canonical native rejection ledger runs 182 and 193 of `t_22f1a4e8` (this section previously said run 176, which was stale; the ledger is authoritative and its two-run count stands): the binding spec (`docs/specs/qing_1910_1945/republic_succession.md:80`) requires the score and the four settled-reform requirements to be exposed through truthful category, decision or event text, and nothing in the shipped surface stated the settlement, the maturity rule, the four counted measures or the conditions the seat was judged on.
The reading was correct. The mechanic was fully implemented and completely invisible, so a player could only discover the settlement after it had already judged them.

### What changed

| Path | Change |
| --- | --- |
| `localisation/english/rch_campaign_l_english.yml` | `rch_beiyang_order_category_desc` gains a second paragraph: the 12 December 1915 settlement, the more-than-180-days tenure, the four counted measures, and every condition the seat is judged on |
| `localisation/english/rch_campaign_events_l_english.yml` | `rch_campaign.2.d` gains the settlement date and the tenure a reform needs; `rch_campaign.5.d` gains the judgement paragraph naming the four measures, the crown, the dials, the governors, Beijing and war with another Chinese government |
| `.tools/tests/test_rch_succession.py` | New `display contract` section, new `display contract mutants` section, and the predicates behind them |
| `docs/systems/rch_campaign.md` | New "What the player is told" subsection with the surface table and the unstated numeric score, plus the display-contract sentence in the validation state |
| this handoff | The section below |

Nothing else moved. No card cost, delta, family lock, cooldown, AI weight, decision id, event id, event option or trigger, idea id, spirit payload, focus or balance range changed, and no script file was edited in this round.
`events/rch_campaign.txt` and `common/decisions/rch_campaign.txt` are byte-identical to the delivered candidate, so the popup still carries one visible option, no `immediate` and no `ai_chance`, which the suite re-asserts.
File timestamps confirm the same thing: the eight script and data files still carry their earlier delivery times (03:54 to 05:18), while only the two localisation files (07:26), the harness (07:27), `docs/systems/rch_campaign.md` (07:29) and this handoff (07:29) were written in this round.

### What the text now states, and why it is truthful

`rch_beiyang_order_category_desc` and `rch_campaign.5.d` name the same four measures the four civil cards set: the constitution, the rotation of the officer corps, the civil governors and the funding of the ministries.
The date is the settlement date, the tenure is `more than 180 days` because that is the strict comparison the snapshot runs, and the conditions listed match `rch_succession_tier_0` term by term: four settled reforms, a refused crown, fewer than three governors, control of state 608 (Beijing) and no war with another Chinese government.
The dials are described as legitimacy, nationalist support and the army's share of power, which is the direction the arithmetic uses.
None of the three values claims a territorial change, and the suite now enforces that.

Length was checked against the consumer, not guessed. The category description is now 779 characters in two paragraphs, and vanilla decision categories already run to 788 characters with eight paragraph breaks (`GRE_pay_back_debt_to_the_ifc_category_desc`), 673 with six (`AST_union_control_1_cat_desc`) and 546 with five (`NOR_democratic_preparation_decisions_category_desc`), all drawn by the same `decision_category_desc` element in `interface/countrydecisionview.gui`.
The popup values are 678 and 1,143 characters, which is ordinary for a multi-paragraph event description.
No render was produced, so this is a length comparison against shipped vanilla text, not a visual check.

### Harness

`display_contract()` reads the three values out of the shipped English files and fails when any of them loses the settlement date, the tenure, the counted measures, the crown, Beijing, the Chinese-war condition or the governors.
It also executes the four civil cards and requires the gate the text names to be the gate the card sets, so the prose cannot drift away from the script, and it requires `rch_succession_settle` to take no further settlement snapshot, so the popup cannot promise a judgement it recomputes.

`display_contract_mutants()` proves the section bites: the settlement paragraph cut from the category description, one counted measure cut from it, the tenure replaced with a vague phrase in the popup, and a territorial claim inserted are each caught. Every mutant that replaces shipped text asserts it actually matched before mutating, so a drifted fragment fails loudly instead of passing quietly.

### Test evidence

- `python .tools/tests/test_rch_succession.py` exits 0, `all checks passed`, twenty-one sections and 283 named checks in `--detail`, including `display contract`, `display contract mutants` and the pre-source `baseline control` (which still fails the `HEAD` tree on a named check).
- Tree-level mutants through `RCH_TEST_ROOT`, each a full mirror of the ten inputs with one edit, each run separately: clean mirror exit 0, category description without the settlement paragraph exit 1 with `FAIL the category description states the settlement rule: it does not name the 12 December 1915 settlement, it does not state the more than 180 days tenure, it does not say what counts toward the seat`, popup without the judgement sentence exit 1 with `FAIL the succession popup states what the seat was judged on: it does not name the constitution, ...`, settlement announcement without the tenure clause exit 1 with `FAIL the settlement announcement states the settlement rule: it does not state the more than 180 days tenure`.
- `python .tools/tests/test_qing_survival.py` exit 0, `all checks passed against f6d12527cc8a; the baseline mutant is rejected`.
- `python .tools/tests/test_qing_consolidation.py` exit 0, `all checks passed against 7136c90a37a1; the baseline mutant is rejected`.
- `python tools/china_audit.py` exit 0, 468 focuses, 72 decisions, 0 missing focus keys. Its one problem remains the 16 unlocalised `PER_*` decisions from the parallel Iran session, outside this card.

### MCP routes run this round

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.script_validate` | `path: localisation/english/rch_campaign_l_english.yml` | `SCRIPT_CHECKED`, family `unsupported`, 0 commands checked, 3 findings: one `SOURCE_STRING_TOO_LONG` and two `SOURCE_UNSUPPORTED_ESCAPE` on the edited line 81, revision `9227e238bce49345e9c358598b4dd4940c733d906b72324e8a02a57ecb42093b` |
| `hoi4.script_validate` | `path: localisation/english/rch_campaign_events_l_english.yml` | `SCRIPT_CHECKED`, family `unsupported`, 0 commands checked, 13 findings of the same two codes, 1 omitted |
| `hoi4.event_inspect` | `mode: trace`, `selector: {kind: event, eventId: rch_campaign.5}`, direction both | `EVENT_INSPECTED_PARTIAL`, focused analysis, 9,323 events / 1,215 entries / 14,584 options / 0 blocking diagnostics, revision `6707616600d79c1c3f25323ddb1ced1039a4c075cbfc3d1d23536a7fec3db916`, report artifact `hoi4-agent://workspace/endsieg/artifact/6dd606a3.../event-trace-6707616600d7.json` (989,886 bytes, sha256 `6dd606a3...`) |
| `hoi4.event_inspect` | `mode: trace`, `selector: {kind: event, eventId: rch_campaign.2}`, direction both | same revision and counts, artifact sha256 `05ae811e...` |
| `hoi4.event_inspect` | `mode: lint`, `selector: {kind: file, sourcePath: events/rch_campaign.txt}` | `EVENT_INSPECTED_PARTIAL`, same revision, 0 blocking diagnostics, 2,416 workspace diagnostics carried by the report, artifact sha256 `8e98b8c2...` (1,903,676 bytes) |

Two limits are stated rather than glossed.
The localisation files are validated as Clausewitz script because the validator has no localisation family, so its two finding codes are format artifacts on this surface: vanilla English localisation carries 783 lines longer than 255 characters and 3,302 lines containing `\n` escapes, so neither is a defect here, and the values were re-read as UTF-8 to confirm the glyphs.
The event routes return workspace-wide counts and a very large linked report, so the per-event facts that matter for this round (one visible tier option, no `immediate`, no `ai_chance`, frozen-score option triggers) are established by direct source read and by the executed suite, not by the trace counts.
None of this is engine proof.

### Residuals

- The live numeric score is not printed anywhere. A per-campaign number needs a `common/scripted_localisation` entry with a `defined_text` selector, and that path is outside this card's fourteen owned files. The text therefore states how the judgement is composed instead of the number. That is recorded as a residual, not as coverage.
- The family lock card text still says "in the past six months" for the 180-day window, deliberately, because the exact figure the player must plan around is the settlement tenure and the lock is a round repeat period. The wording was fixed in round 1 and is unchanged here.
- `rch_chinese_war` still excludes `MAN`, so "war with another Chinese government" is accurate for every 1916 start, and a later Manchukuo war is out of its scope by design rather than by omission.
- No launch, so none of the three values has been read in the category window, the 1912 event or the popup, and no claim is made about length or wrapping in those consumers.

## Round-5 correction: the score itself, printed after it is frozen

The approved diagnostic on `t_a571aa0f` established that round 4 answered the contract with prose and left the number unexposed, and that the round-4 residual claiming a `common/scripted_localisation` entry was needed was wrong.
This round implements that plan inside the same five owned paths and no others.

### What was wrong

- `rch_succession_final_score` is assigned once by `rch_succession_settle` (line 624) before the line flags, the seat spirit and the queued popup, so it is the authoritative number a player should read. No localisation value anywhere contained it.
- The residual above said a per-campaign number needs a `common/scripted_localisation` entry. It does not: an ordinary English value prints a formatted country variable, and vanilla already does exactly that in a spirit description (`TAOG_ideas_l_english.yml:488`, `AST_IRE_stationed_troops_idea_desc`, `[?AST_IRE_stationed_troops_count_var|Y0]`).
- The old timing sentence claimed the judgement was fixed on 12 December 1915 and that nothing afterwards changed the reckoning. The settlement freezes only `rch_reform_settled`; the score is judged at resolution from that frozen count plus the dials, the crown, the governors, Beijing and any Chinese war, all of which can still move until the succession falls. `rch_campaign.2.d` also called December the judgement date rather than the date the reform record closes.
- The display harness checked prose tokens and the settlement arithmetic but never a numeric readout, which is why it stayed green with no score printed anywhere.

### What changed

| Path | Change |
| --- | --- |
| `localisation/english/rch_campaign_events_l_english.yml` | `rch_campaign.5.d` now states that December closed the reform record and that the seat was judged at resolution, and prints `Seat standing: [?rch_succession_final_score|0] out of 100.`; `rch_campaign.2.d` now says the record closes on 12 December 1915 and that the seat is judged when the presidency falls |
| `localisation/english/rch_campaign_l_english.yml` | the same frozen readout appended to all four seat spirits: `rch_succession_constitutional_desc`, `rch_succession_contested_desc`, `rch_succession_garrison_desc`, `rch_succession_dissolved_desc` |
| `.tools/tests/test_rch_succession.py` | new `score readout` and `score readout mutants` sections, their predicates, a strict defined-variable interpolation, and one word-boundary fix in `territorial_claim_defects` |
| `docs/systems/rch_campaign.md` | the display table names all six consumers, the false scripted-localisation paragraph is replaced by the real variable lifetime, and the validation state names the new section |
| this handoff | this section |

No gameplay file was edited: `common/scripted_effects/rch_campaign.txt`, `common/decisions/`, `events/`, `common/ideas/`, `common/bop/` and `common/script_constants/` are byte-identical to the delivered candidate.
No score recomputation, no `immediate` in the popup, no new event, idea, decision, constant, GUI or AI weight.

### Harness

`score_readout_record()` reads the six localisation values, requires the exact `[?rch_succession_final_score|0]` token with the `Seat standing` label and the `out of 100` range, and rejects a live `rch_succession_score`, an unrelated variable, a misspelling, a missing `?` and a missing `|0`.
It then resolves every fixture in `FIXTURES` through the shipped `rch_succession_settle` — nothing in the test assigns `rch_succession_final_score` — and compares the number the popup and the standing seat spirit would draw with the score the effect froze, for all four tiers, scores 88, 78, 69, 70, 46, 45, 44, 0 and the five emergency rows.
It asserts that the pre-resolution category prints no score, that a 1912/December-1915/January-1916 country holds no `rch_succession_final_score` at all, that `Country.value()`'s absent-name zero is not accepted as a score, that a refresh, a repeat tick and changed dials leave the printed number alone, that a silent 1918 start prints it without a popup, and that no-DLC play prints the same numbers.
`score_readout_mutants()` deletes the readout from the popup and from one seat, substitutes the scratch score, breaks the token three ways, leaks the score into the category, restores the false December claim, and deletes the `final_score` assignment from the shipped settle — each caught by a named defect, the last one on a genuine zero score.

### One oracle defect found and fixed

`territorial_claim_defects()` tested `'cession' in text`, which matches the ordinary noun `succession` and the variable name `rch_succession_final_score`, so it forbade the readout the same file requires.
It now matches at a word boundary (`\bcession`), which still catches a real cession; a new mutant (`The government accepts the cession of Shandong.`) proves it still bites, and a control proves the shipped popup is not read as one.
The territorial clause is otherwise unchanged, and the player-facing label is `Seat standing` rather than a phrase that would have tripped it.

### Test evidence

- Before the localisation change, the suite failed on the new section: `47 check(s) failed`, every failure in `score readout`, `score readout mutants` or the two phase claims, with `FAIL ... -> the drawn text carries no standing number`. That is the reproducer for this round, distinct from the older `HEAD` baseline.
- After the change, `PYTHONDONTWRITEBYTECODE=1 python -B .tools/tests/test_rch_succession.py --detail` exits 0 with `all checks passed`, 381 passing checks including the 77 in `score readout`, and the `baseline control` still rejecting the `HEAD` tree on a named check.
- `python -B .tools/tests/test_qing_survival.py` exits 0, `all checks passed against f6d12527cc8a; the baseline mutant is rejected`.
- `python -B .tools/tests/test_qing_consolidation.py` exits 0, `all checks passed against 7136c90a37a1; the baseline mutant is rejected`.
- `python -B tools/china_audit.py` exits 0 with its one pre-existing problem, the 16 unlocalised `PER_*` decisions from the parallel Iran session, outside this card.

### MCP evidence

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.source_lookup` | `symbol: rch_succession_final_score`, references on | before the edit: 0 definitions, exactly one reference, a `variable_write` in `rch_succession_settle` at `common/scripted_effects/rch_campaign.txt:624`; `referencesComplete: false`, 2,587 unresolved, revision `3bc6397b…` |
| `hoi4.event_inspect` | `mode: trace`, `selector: {kind: event, eventId: rch_campaign.5}`, direction both | before and after: `EVENT_INSPECTED_PARTIAL`, revision `daaf65f9…`, 9,325 events, 1,215 entries, 14,587 options, 0 blocking diagnostics, artifact `6a6b1487…` (989,832 bytes) |
| `hoi4.script_validate` | `path: localisation/english/rch_campaign_events_l_english.yml` | `SCRIPT_CHECKED`, family `unsupported`, 0 commands checked, 15 findings, all `SOURCE_STRING_TOO_LONG` or `SOURCE_UNSUPPORTED_ESCAPE` on the edited lines 15 and 70 |
| `hoi4.script_validate` | `path: localisation/english/rch_campaign_l_english.yml` | `SCRIPT_CHECKED`, same family, 15 findings, same two codes on lines 81, 110, 112 and 114 |

The two validator codes are format artifacts on a localisation surface, as the round-4 section already recorded: vanilla English localisation carries 783 lines longer than 255 characters and 3,302 lines containing `\n` escapes.
No engine-facing `.txt` file changed, so no `.txt` validation was required this round.

### Supersedes

- The Residuals bullet above claiming a `common/scripted_localisation` entry is needed, and that the number is therefore not printed: both are wrong and are replaced by the variable and its consumers described here.
- The round-4 system-table row calling every judgement input fixed at the settlement, and the popup sentence saying nothing after 12 December 1915 changed the reckoning: the settlement freezes the reform count only.
- The `run 176` reference: the canonical ledger records runs 182 and 193 under the same problem key.

### Still unverified

- No launch and no render, so the panel, the tooltip, the popup and the four spirit descriptions have never been drawn, and native substitution of `[?rch_succession_final_score|0]` in a spirit description is proven by installed documentation and a vanilla precedent, not by this session's engine.
- The model is a single-country interpreter: it validates token binding and value lifetime, not text layout, wrapping or the engine's own number formatting.
- The 1918 path is exercised through `rch_succession_endow`; `rch_initialize_campaign` is not itself executed by the harness, and says so rather than implying coverage.


