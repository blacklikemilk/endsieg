# S18 handoff: post-war focus catch-up reachable and route-correct

Card: t_784d10f9 (S18). Branch: TeknoDev-Branch. No commit, no branch switch, no HOI4 launch.

## What was wrong

1. `spain_campaign_tick` calls `spain_campaign_bootstrap` only under `has_country_flag = spain_focus_restore_pending` (`spain_campaign_effects.txt:278-281` before this change). Only the Restoration, Rivera and Republic openers armed that flag. Both post-war openers set `spain_bop_pending` instead, so no post-war bookmark ever reached the bootstrap, the catch-up or the idea refresh.
2. The `SPR4_*` list sat under `limit = { has_country_flag = spain_chapter_postwar }`, while `SPR4_*` ids exist only in `spain_republic_postwar_focus`. The Nationalist chapter loads `spanish_focus` (`:192` after the change), so every post-war bookmark asked the engine to complete ids outside the loaded tree, and the Republican chapter had no list at all.
3. `spain_campaign_bootstrap` rebuilds `SPR_crown_and_cortes` whenever `spain_bop_pending` is set (`:1378-1399` after the change). Arming the restore flag without clearing that flag would have resurrected the balance the post-war openers deliberately delete.

## Changed symbols (`common/scripted_effects/spain_campaign_effects.txt`, the only tracked file changed)

`spain_open_postwar_chapter` (`:184-204`). Replaced `set_country_flag = spain_bop_pending` with two lines:

```
	clr_country_flag = spain_bop_pending
	set_country_flag = spain_focus_restore_pending
```

`spain_open_republican_postwar_chapter` (`:206-225`). Added the same two lines after the chapter flag (`:211-212`). This opener never set the pending balance, but it can inherit a stale one from an earlier chapter, and it deletes the balance four lines later, so it must clear it for the same reason.

Order inside the Nationalist opener now is: clear chapter flags, drop the pending balance, arm the restore, claim the chapter, load `spanish_focus`, remove `SPR_crown_and_cortes` (`:196`), settle the reconstruction idea, refresh ideas. `spain_campaign_bootstrap` therefore runs on the next daily tick with no pending balance, so it skips the `set_power_balance` branch entirely and reaches `spain_restore_past_focuses` (`:1402`).

`spain_restore_past_focuses` (`:1076-1374`):

* Nationalist block, `limit = { has_country_flag = spain_chapter_postwar }` (`:1300`): `SPA_the_national_syndicalist_state`, `SPA_the_national_and_popular_army_of_spain`, `SPA_national_recovery` at `date > 1940.6.1`; the alignment pair as one `if`/`else_if` chain at `date > 1941.6.1` reading `has_idea = spain_axis_alignment` then `has_idea = spain_allied_alignment` (`:1307-1317`); `SPA_the_iberian_pact` at `date > 1943.1.1`; `SPA_settle_the_succession_question` at `date > 1945.6.1`.
* Republican block, `limit = { has_country_flag = spain_chapter_republican_postwar }` (`:1330`): the fifteen ids the old block completed, unchanged and in the same date groups, plus `SPR4_political_police` and `SPR4_the_church_settlement` in the `1941.1.1` group (`:1346-1347`).
* The generated-block comment (`:1077-1080`) now records that the generator's seeds still map `spain_chapter_postwar` to the republican tree, so the two post-war lists are hand-maintained here and the tool must not be re-run against them.

Every id was checked against the tree its own chapter's `load_focus_tree` names, by parsing the focus files (`spanish_focus` -> 281 focuses in `common/national_focus/spain.txt`; `spain_republic_postwar_focus` -> 57 in `common/national_focus/spain_republic_postwar.txt`, both matching `hoi4.focus_inspect` counts).

## Why the completions are not no-ops

`complete_national_focus` is not gated by the target's prerequisites in this engine's shipped vanilla usage: `common/decisions/NOR.txt:58-63` completes `NOR_restart_public_investment` (prerequisites `NOR_social_incrementalism`, `NOR_print_more_money`) and `NOR_rearm_for_defense` (prerequisites `NOR_restore_public_trust_in_the_storting`, `NOR_the_neutrality_guard`), none of which appear in the completed list. The ids in this card's schedule carry prerequisites (`SPA_a_one_party_state`, `SPA_portuguese_aid`, `SPA_confirm_the_fueros`, `SPR4_the_falange_remnant`, `SPR4_amnesty_debate`) that are deliberately **not** added, because the card forbids inventing ids and the spec §4.A2 enumerates this exact list. That reading rests on vanilla source, not on a launch: see residuals.

`SPA_the_national_syndicalist_state`'s reward promotes `SPA_jose_antonio_primo_de_rivera`, who is recruited by the `1936.1.1` history block (`history/countries/SPR - Spain.txt:714`) and is never killed or retired in the mod (`grep kill_character` returns nothing), so a 1939+ start has a live target for that completion.

## The suite

`.tools/tests/test_spain_postwar_catchup.py` (gitignored, evidence only). It parses the shipped effects file with the shared tokeniser from `test_spain_cortes_recount.py`, then executes it:

* routes a bookmark date through `spain_campaign_initialize` and `spain_enter_postwar_chapter` (real `if`/`else_if` evaluation, not a hardcoded map);
* replays each opener's top-level writes in source order onto a country that starts with a stale `spain_bop_pending`;
* evaluates the real schedule block against date, chapter flag and idea set;
* derives focus-id membership from each opener's own `load_focus_tree` target, read from the focus files;
* raises on any effect or trigger it does not model (only `if`/`else_if`/`else`, `limit` with `has_country_flag`/`has_idea`/`has_variable`/`has_government`/`has_power_balance`/`date`, `complete_national_focus`, `set`/`clr_country_flag`, `load_focus_tree`), and asserts the five stepped-over helpers write none of the chapter, restore or balance flags.

## Test commands and real output

```
python .tools/tests/test_spain_postwar_catchup.py            -> 748 checks, 0 failures   (exit 0)
python .tools/tests/test_spain_postwar_catchup.py --detail   -> 748 checks, 0 failures   (exit 0)
    [openers] 66  [routing] 46  [nationalist] 61  [republican] 7  [membership] 550  [cheap] 10
    mutant [SPR4 id inside the Nationalist block] 46 failures, e.g. spain_chapter_postwar completes SPR4_the_republic_endures, which is not in spanish_focus (1941.1.1)
    mutant [alignment gate removed] 45 failures, e.g. axis alignment (1941.6.2): expected [... SPA_join_the_axis], got [... SPA_join_the_axis, SPA_join_the_allies]
    mutant [1941 Republican rows dropped] 2 failures, e.g. SPR4_political_police is not completed at 1941.1.2
    mutant [pending balance not cleared] 2 failures, e.g. spain_open_postwar_chapter does not clear spain_bop_pending
```

Negative control: the suite run against `git show HEAD:common/scripted_effects/spain_campaign_effects.txt` (swapped in, then restored from a byte copy) gives **508 checks, 356 failures, exit 1**, including `1940.1.1 reaches no bootstrap: the catch-up is dead`, `the Republican handover reaches no bootstrap`, and 300+ `spain_chapter_postwar completes SPR4_* ... which is not in spanish_focus`. The suite therefore discriminates the defect rather than describing the current file.

Existing Spain suites, all unmodified, all exit 0:

```
test_spain_cortes_runtime        113 checks, 0 failures
test_spain_cortes_recount        215 checks, 0 failures
test_spain_cortes_postwar_bills  227 checks, 0 failures
test_spain_coup_relief_sign      127 checks, 0 failures
test_spain_restoration_loyalty   146 checks, 0 failures
test_spain_turno                 128 checks, 0 failures
test_spain_hemicycle_builder      69 checks, 0 failures
```

`python tools/spain_audit.py --game "<install>"` exists and was run: exit 0, `274 focuses`, `34337 localisation keys (missing focus keys: 0)`, one pre-existing problem, `108 unregistered sprite reference(s)` (idea pictures for Spain characters, unrelated to this card and not introduced here).

Brace census on the edited file: 892 open, 892 close. Line endings: LF only in both the working copy and HEAD (git's advisory warning only).

Flag census (`grep -rn ... common/ events/`):

* `spain_focus_restore_pending`: writers at `:103`, `:121`, `:141`, `:189`, `:212`; reader and clear at `:278`/`:279`. Five writers, one reader, no orphan.
* `spain_bop_pending`: writers at `:102`, `:120`, `:140`, `:160` (all pre-existing, none in a post-war opener), clearers at `:188`, `:211` (new) and `:1381`, reader at `:1380`. No write-only flag was created and no new flag exists.

## MCP evidence

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.source_lookup` pre-edit | `spain_restore_past_focuses` | 1 definition `:1069-1332`, 1 reference `spain_campaign_bootstrap:1360`, revision `58e8d319…` |
| `hoi4.source_lookup` pre-edit | `spain_campaign_bootstrap` | 1 definition `:1336-1361`, 1 reference `spain_campaign_tick:273` |
| `hoi4.source_lookup` pre-edit | `spain_focus_restore_pending`, `spain_chapter_republican_postwar` | 0 definitions, 0 references: the index resolves scripted effects, not flag tokens, so flag callers were censused by `grep` instead |
| `hoi4.script_validate` pre-edit | `path=common/scripted_effects/spain_campaign_effects.txt` | `SCRIPT_CHECK_PARTIAL`, 0 findings, 1210 commands, 211 argument blocks unchecked, 54/54 roots with unknown scope |
| `hoi4.focus_inspect` | `treeId=spanish_focus` | 281 focuses, `mod:common/national_focus/spain.txt`, 16 blocking diagnostics (pre-existing layout/content, S17/B1 territory), layout hash `c1224f2e…` |
| `hoi4.focus_inspect` | `treeId=spain_republic_postwar_focus` | 57 focuses, `mod:common/national_focus/spain_republic_postwar.txt`, 13 blocking diagnostics (pre-existing), layout hash `069372cf…` |
| `hoi4.script_validate` post-edit | same path | `SCRIPT_CHECK_PARTIAL`, 0 findings, 1236 commands (+26), same 211 unchecked argument blocks, revision `5897e33a…` |
| `hoi4.source_lookup` post-edit | `spain_open_postwar_chapter`, `spain_open_republican_postwar_chapter`, `spain_restore_past_focuses` | definitions at `:184-204`, `:206-225`, `:1076-1374`; references `initialize:38`, `enter_postwar:253`, `enter_postwar:250`, `bootstrap:1402` |

No `hoi4.event_inspect` was needed: no event, option or firing path in `events/spain_campaign.txt` was edited, and the schedule is reached only through the bootstrap that already exists.

## Residuals and unverified

* **No live campaign was run.** Bookmark behaviour (flag timing on the first daily tick, the balance staying deleted, focus completion on a real 1940-1945 start) is source-modelled only.
* **`tools/build_spain_restore_schedule.py` is stale and would clobber this repair.** Its `TREES` map still points `spain_chapter_postwar` at `common/national_focus/spain_republic_postwar.txt`, its `SEEDS` carry an older post-war list, and there is no `spain_chapter_republican_postwar` entry. Re-running it rewrites `spain_restore_past_focuses` and undoes the move. The file is outside this card's ownership; the in-source comment at `:1077-1080` records the constraint. Director/J17 needs a card to fix the seeds and regenerate, or to retire the generator for the post-war chapters.
* **A democratic post-war *bookmark* still lands on the Nationalist chapter**: `spain_campaign_initialize` chooses by date only (`:37-39`), and the government test lives in `spain_enter_postwar_chapter`, which is reached from events, not bookmarks. This is pre-existing, belongs to route C3 (§6), and was not touched. The suite asserts today's behaviour.
* **The civil-war chapter still arms no restore**: `spain_open_civil_war_chapter:160` sets `spain_bop_pending` and never `spain_focus_restore_pending`, so a 1939.1.1 start completes nothing and never builds the balance. Pre-existing, outside this card; the suite pins the 1939 start as completing nothing.
* **Prerequisite-free completion is evidenced by vanilla source, not by a launch.** If QA wants engine proof, it needs a save in which a 1941+ Nationalist start shows `SPA_the_national_syndicalist_state` completed after one tick.
* `docs/systems/` has no `spain_campaign.md` in this tree, so no system doc needed editing; the documentation surface for this change is this handoff plus the in-source comment. Director may want a line in `docs/specs/spain_1910_1945/continuation_1936_1945.md` §4.A2/§5.B3 recording that both openers now arm the restore.
* Working tree contains other agents' changes. `common/national_focus/spain_republic_postwar.txt` is modified (12 lines) by S17's owner, not by this card: it was never opened for writing here. `tools/__pycache__/build_spain_cortes_hemicycle.cpython-314.pyc` is a rebuilt bytecode artifact from running the existing suites. Neither belongs in this card's integration.
* `.tools/` is gitignored: the suite is validation evidence in the working tree, not a committable artifact.

WAITING_FOR=director_qa_admission

---

# Closure repair pass — run 202 (2026-10-27, after Director's corrected scope ruling)

Appended; the run-161 record above stands.

## Delivered

**`common/scripted_effects/spain_campaign_effects.txt`** (3 added lines, plus a comment fix; the openers and the Nationalist `SPA_*` list are unchanged from run 161):

- `:1345-1351` — the `spain_chapter_republican_postwar` `date > 1941.1.1` group now emits, in order, `SPR4_army_of_the_republic`, `SPR4_the_exiled_monarchy`, `SPR4_the_falange_remnant`, `SPR4_amnesty_debate`, `SPR4_political_police`, `SPR4_the_church_settlement`. The three added rows are the ancestors the tree gives the party rows (`SPR4_the_falange_remnant` ← `SPR4_the_exiled_monarchy` ← `SPR4_the_republic_endures`; `SPR4_political_police` ← `SPR4_the_falange_remnant`; `SPR4_the_church_settlement` ← `SPR4_amnesty_debate`), each emitted before its dependent. The Republican list is now closed over its own tree transitively at every bookmark from 1941.1.2 up.
- `:1327-1329` comment states why the ancestors precede the rows.

**`docs/spain_campaign.md:38-50`** — no longer asserts an unproven engine rule as fact and no longer claims the schedule is never hand-edited. It names the generated lists, the hand-maintained post-war lists and the stale generator seeds, and defines closure and order as schedule properties, recording that the Republican list satisfies closure while the Nationalist list does not yet.

**`.tools/tests/test_spain_postwar_catchup.py`** — new `closure` area (19 checks) plus `focus_graph()`, `closure_breaks()` (transitive, emission-order reachability) and `exclusive_pairs()`, and a fifth mutant.

## Blocker: the Nationalist pins need three sides of one exclusive fork

`common/national_focus/spain.txt` declares a symmetric three-way exclusive fork at 673 / 3688 / 5693: `SPA_the_phalanx_ascendant` (664), `SPA_unify_the_nationalist_front` (3679), `SPA_supremacy_of_the_communion` (5684), each excluding the other two. Each pinned post-war target needs a different side:

- `SPA_the_national_syndicalist_state` (1617) ← `SPA_a_one_party_state` (1351, requires both `SPA_establish_the_directory` and `SPA_eliminate_the_carlists`) ← `SPA_suspend_the_constitution` ← `SPA_secure_the_national_defense_council` ← `SPA_the_phalanx_ascendant`
- `SPA_the_iberian_pact` (4112) ← `SPA_portuguese_aid` (4073) ← `SPA_a_methodical_approach` (3970) ← `SPA_unify_the_nationalist_front`
- `SPA_settle_the_succession_question` (6605) ← `SPA_confirm_the_fueros` (6403) ← `SPA_no_compromise_on_carlist_ideals` (5977) ← `SPA_contact_the_union_militar_espanola` and `SPA_unite_the_requetes` ← `SPA_supremacy_of_the_communion`

`SPA_the_phalanx_ascendant` is the only prerequisite block of `SPA_secure_the_national_defense_council`, so there is no alternative route. The seven pins therefore cannot be closed without completing at least two mutually exclusive focuses, which the corrected ruling forbids. Nothing was invented or dropped to get past it: the Nationalist block is byte-identical to the QA-verified run-161 state, and the suite now asserts the diagnosed unclosed set in both directions so any change to it fails loudly.

## Validation

| Check | Result |
| --- | --- |
| `python .tools/tests/test_spain_postwar_catchup.py --detail` | **865 checks, 0 failures, exit 0**; openers 66, routing 46, nationalist 61, republican 13, membership 640, closure 19, cheap 10 |
| Mutants | `SPR4_*` in the Nationalist block 46 failures; alignment gate removed 45; 1941 Republican rows dropped 5; pending balance not cleared 2; `SPR4_the_falange_remnant` ancestor dropped 3 — all caught |
| Seven existing Spain suites | exit 0 each, unmodified |
| `python tools/spain_audit.py` | exit 0 |
| `hoi4.script_validate` on the effects file | `ok`, 0 findings, 1239 commands, 54/54 roots unknown scope, `argumentBlocksUnchecked=211`, code `SCRIPT_CHECK_PARTIAL` (partial coverage, not a pass) |
| `hoi4.source_lookup` `spain_restore_past_focuses` | 1 definition `:1076-1379`, 1 reference `spain_campaign_bootstrap:1407`, `complete=true` |
| Mod tree vs installed `spain.txt` | 281 focuses each, 0 id and 0 prerequisite differences, so the mod file is the authority and the installed copy a safe cross-check |

Not performed: no game launch, no bookmark loaded, no focus clicked, no daily tick, no live campaign.

## Residuals

1. The Nationalist fork above needs a route decision, a pin-list change, or a focus-tree card.
2. `tools/build_spain_restore_schedule.py:26` still maps `spain_chapter_postwar` to `spain_republic_postwar.txt` with no Republican-postwar seed. Re-running it erases both post-war lists.
3. The Republican ledger still completes the pre-existing `SPR4_armed_neutrality` / `SPR4_the_european_war` exclusive pair because AC3 keeps every focus it completes today.
4. Democratic post-war bookmarks still route by date to the Nationalist chapter (route C3), and the civil-war chapter still arms no restore (out of scope).

WAITING_FOR=director_decision_on_nationalist_fork

---

# Route-aware closure pass — run 206 (2026-10-27, card t_7b562c70)

Appended; the run-161 and run-202 records above stand.

## Delivered

**`common/scripted_effects/spain_campaign_effects.txt`**, `spain_restore_past_focuses`, Nationalist block (`:1297-1392`, was `:1297-1323`). The one flat `SPA_*` list is now one `if` / `else_if` / `else` chain over the fork, each branch date-gated on the existing ladder:

| Branch | Detection | `1940.6.1` | `1941.6.1` | `1943.1.1` | `1945.6.1` | lines |
| --- | --- | --- | --- | --- | --- | --- |
| phalanx | `has_completed_focus = SPA_the_phalanx_ascendant` | 9 | `SPA_join_the_axis` | — | — | 10 |
| communion | `has_completed_focus = SPA_supremacy_of_the_communion` | 2 | — | 3 | 2 | 7 |
| default (fused front) | neither, `else` | 18 | axis **or** allies by alignment idea | 3 | — | 23 |

The Nationalist block therefore holds 40 completions, not 7. Republican block untouched.

Route matrix derived from `common/national_focus/spain.txt` (parser in the suite, `need_closure` + `topological_order`):

| Route | Pins it can carry | Pins it cannot, and the ancestor that blocks them |
| --- | --- | --- |
| phalanx | `SPA_the_national_syndicalist_state`, `SPA_the_national_and_popular_army_of_spain`, `SPA_national_recovery`, `SPA_join_the_axis` | `SPA_join_the_allies` (via `SPA_banish_the_party_leaders`, which needs `SPA_extol_the_martyrs_of_the_war` and `SPA_foment_a_carlist_split`, both behind the unify front); `SPA_the_iberian_pact` (`SPA_a_methodical_approach`); `SPA_settle_the_succession_question` (`SPA_prepare_the_carlist_insurrection`) |
| default / unify | `SPA_the_national_and_popular_army_of_spain`, `SPA_national_recovery`, `SPA_join_the_axis`, `SPA_join_the_allies`, `SPA_the_iberian_pact` | `SPA_the_national_syndicalist_state` (`SPA_secure_the_national_defense_council` ← phalanx); `SPA_settle_the_succession_question` (communion) |
| communion | `SPA_settle_the_succession_question` | the other six, all through `SPA_safeguard_the_freedom_of_worship` (needs `SPA_establish_the_directory` or `SPA_extol_the_martyrs_of_the_war`, one per excluded side) or `SPA_a_methodical_approach` |

The default branch completes the route selector `SPA_unify_the_nationalist_front` itself, because a country there completed neither exclusive side. The two detected branches do not re-complete their selector, which the engine guarantees was already taken with its whole ancestor column.

**`docs/spain_campaign.md:44-45`** — the closure property now states the per-route guarantee instead of the "Nationalist list does not satisfy closure" finding. The rest of the file is unchanged. The `| Start | Focuses already completed |` table below it was not re-derived and is out of this card's owned hunk; it still shows the pre-202 numbers and needs its own pass.

## Two corrections to the card body

1. The id is `SPA_extol_the_martyrs_of_the_war` (tree `:3795`), not `SPA_extol_the_martyrs_of_war`-minus-`the` as fact 3 writes it. The schedule uses the real id.
2. Fact 3 reads `SPA_banish_the_party_leaders` as `SPA_extol_the_martyrs_of_the_war` **OR** `SPA_foment_a_carlist_split`. The tree declares them as two separate `prerequisite` blocks (`:4224-4225`), which the engine ANDs under the card's own fact 1. The suite follows the tree, so `SPA_fuse_the_parties` is unify-only and the phalanx route cannot carry `SPA_join_the_allies`. That single difference moves the default route from Director's four reachable pins to five (both join rows are individually reachable there) and the communion route from four to one.

## Suite

`.tools/tests/test_spain_postwar_catchup.py` (gitignored, evidence only; +241 lines). New: `has_completed_focus` in the trigger evaluator; `need_closure`, `topological_order`, `nationalist_branches`, `default_side`, `route_groups`, `route_plan`. `area_nationalist` no longer holds a written expectation: it derives each branch's side from the branch's own detection id, derives the closure of the seven pins from the tree, and asserts (a) the emitted ids equal that closure, (b) each date group is emitted in the prerequisite order the tree forces, (c) gates are ladder dates in non-decreasing order, (d) no exclusive pair, (e) every reachable pin present and every unreachable pin absent, (f) the shipped block agrees with the group plan at each rung and ±1 day under no idea / axis / allied, (g) both join rows never complete together. `NATIONALIST_UNCLOSED` and the `EXPECTED_*` literals are gone; counts are derived from the plan. `area_membership` also runs each route's seed, so a branch-only id is still checked against its loaded tree.

## Tests run

```
python .tools/tests/test_spain_postwar_catchup.py            -> 2235 checks, 0 failures, exit 0
python .tools/tests/test_spain_postwar_catchup.py --detail   -> same, areas:
    [openers] 66  [routing] 46  [nationalist] 171  [republican] 13
    [membership] 1895  [closure] 17  [cheap] 11
```
Mutants, all caught by name (8 total, 4 new):
```
SPR4 id inside the Nationalist block       37 failures  (not in spanish_focus)
alignment gate removed                      5 failures  (both join focuses on 1943.1.1)
Nationalist ancestor dropped                2 failures  (is not closed over the tree)
pin added to a route that cannot carry it   3 failures  (cannot carry)
mutex sibling added to a route              3 failures  (both sides)
1941 Republican rows dropped                5 failures
pending balance not cleared                 2 failures
1941 ancestor row dropped                   3 failures
```
Negative controls (`.tmp/spa_negative_control.py`, no repo write): `git show HEAD:` of the effects file gives 142 checks / 36 failures; the working tree with the run-202 Nationalist list restored gives 142 checks / 3 failures, all `could not be modelled: ... if branch tests 0 completed focuses`, so the route detection is load-bearing rather than decorative.

Existing Spain suites, unmodified, exit 0, 0 failures each: `test_spain_cortes_runtime` 113, `test_spain_cortes_recount` 215, `test_spain_cortes_postwar_bills` 227, `test_spain_coup_relief_sign` 127, `test_spain_restoration_loyalty` 146, `test_spain_turno` 128, `test_spain_hemicycle_builder` 69.

`python tools/spain_audit.py --game "<install>"`: exit 0, 274 focuses, 45 events, 246 decisions, 34465 localisation keys with 0 missing focus keys, and the same pre-existing 108 unregistered idea-picture sprites.

BOM/brace census of the edited file: no BOM (`23204f`), 905 open / 905 close, LF only, 1697 lines. `tools/check_script_bom.py` flags `common/national_focus/spain_restoration.txt`, which is committed, unmodified and outside this card.

## MCP evidence

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.source_lookup` pre-edit | `spain_restore_past_focuses` | 1 definition `:1076-1379`, 1 reference `spain_campaign_bootstrap` (run-202 baseline) |
| `hoi4.script_validate` post-edit | `path=common/scripted_effects/spain_campaign_effects.txt` | `status ok`, 0 findings, 1285 commands (+46), 54/54 roots unknown scope, `argumentBlocksUnchecked=211`, code `SCRIPT_CHECK_PARTIAL` (partial coverage, not a pass) |
| `hoi4.source_lookup` post-edit | `spain_restore_past_focuses` | 1 definition `:1076-1448`, 1 reference `spain_campaign_bootstrap:1476`, `complete=true`, revision `e38d3aac…` |
| `hoi4.source_lookup` post-edit | `spain_chapter_postwar`, `has_completed_focus` | 0 definitions and 0 references: the index resolves scripted effects and focus ids, not country flags or native trigger tokens, so both were censused with `grep` instead |
| `hoi4.focus_inspect` | `treeId=spanish_focus` | 281 focuses, layout hash `c1224f2e…` unchanged from run 202, 16 blocking layout diagnostics (pre-existing, S17/B1 territory), read-only, no tree edit |

No `hoi4.event_inspect` and no render route: no event, decision, GUI or focus source changed.

## Residuals and unverified

1. **No live campaign was run.** Nothing here proves engine behaviour at a bookmark: not that `complete_national_focus` accepts a focus whose `available` block is unmet (`SPA_consolidate_the_north` requires five states), not that re-completing an already-completed focus (five ids overlap the `1941.1.1` history block) is a silent no-op, and not that route detection reads a correct completed set on the first daily tick. All three stay unverified until a 1941/1945 start is inspected.
2. **The 1940.1.1 start still completes nothing** and never catches up, because the schedule runs once and its first gate is `1940.6.1`. Pre-existing ladder convention, asserted by the suite, unchanged by this card.
3. `tools/build_spain_restore_schedule.py` is still stale (`:26` maps `spain_chapter_postwar` to `spain_republic_postwar.txt`, no Republican-postwar seed). Re-running it erases both post-war lists and this route split.
4. Democratic post-war bookmarks still route by date to the Nationalist chapter (route C3), and the civil-war chapter still arms no restore.
5. The `| Start |` completion-count table in `docs/spain_campaign.md` is now older than the schedule it summarises; its own pass is needed outside the lines this card owns.

WAITING_FOR=director_qa_admission
