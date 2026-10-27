# C8 | Qing consolidation band and restoration gate — handoff

Status: implementation complete, source-validated, awaiting Director QA admission.
Branch: `TeknoDev-Branch`. No commit, no launch, no push, no premium model.
Baseline revision for every mutation control: `7136c90a37a1dd0686a2ca456efb85563ff194b9` (C7).

## What the package does

**A derived consolidation score.** `qing_consolidation` (0–100) is computed by `qing_consolidation_refresh` and written nowhere else.
Five families each carry a fifth of it:

| Family | Input | Worth |
| --- | --- | --- |
| Court | `qing_legitimacy` | /5 |
| Reform | `qing_reform` | /5 |
| Army | `qing_army_loyalty` | /5 |
| Provinces | `qing_provincial_trust` | /5 |
| Works | `qing_currency_reform`, `qing_railway_north_built`, `qing_hanyang_built`, `qing_civil_service_reformed`, `qing_works_completed` | 4 each |

4 × (100 / 5) + 5 × 4 = 100, clamped by `consolidation_floor` / `consolidation_cap`.
The refresh is called from `qing_refresh_mechanics`, so every existing effect that already refreshes the mechanics also refreshes the score.

**Five visible programmes with progress and failure.** All seven new decisions sit in the existing `qing_imperial_government` category (no new category file, no new idea):

| Decision | Progress | Failure |
| --- | --- | --- |
| `qing_consolidation_court` | 90-day timer, `stability_factor = 0.05`, pays legitimacy +10 | `cancel_trigger = qing_legitimacy_weak`, loses legitimacy, stability, sets `qing_consolidation_court_lapsed` |
| `qing_consolidation_reform` | 120 days, stability, reform +10 | `qing_reform_weak`, reform −10, stability, lapse flag |
| `qing_consolidation_army` | 120 days, `war_support_factor`, army +10, costs 15 army xp | `qing_army_unreliable`, army −10, stability, lapse flag |
| `qing_consolidation_provinces` | 120 days, stability, trust +10 | `qing_provinces_strained`, trust −10, stability, lapse flag |
| `qing_consolidation_works` | 150 days, `production_speed_buildings_factor = 0.10`, completes the `qing_works_completed` receipt and one infrastructure level in Beijing | political power below 25, stability cost, `qing_consolidation_works_lapsed` |
| `qing_consolidation_report` | no timer, recomputes the score | — |
| `qing_convene_interwar` | visible from 1918.6.1, opens the interwar chapter early | blocked until the bar is met, behind `qing_convene_interwar_tt` |

Progress is visible in two places: the running decision's own timer and modifier, and each description's live numbers (`[?qing_legitimacy|0]`, `[?qing_reform|0]`, … `[?qing_consolidation|0]`).

**The interwar chapter is gated on the score, not the date.** The guard sits in four places so no path bypasses it:
`qing_consolidation_settled` (check_variable against `constant:qing_story.consolidation_gate` = 60), inside `qing_open_chapter_two` itself, in the daily tick's chapter-two block (date **and** bar), and in the dormant `qing_route_chapter` self-heal (which previously loaded `qing_interwar` on the date alone and had no callers).
`qing_convene_interwar` gives a consolidated dynasty an early entry from 1918.6.1 with the requirement shown as a localised tooltip; the tick still opens the chapter for anyone who ignores it, but never without the bar.

**The restoration band is gated on a *sustained* score.** `qing_consolidation_sustained` = bar **and** `qing_consolidation_held`; the tick counts `qing_consolidation_days` only while the bar holds, raises the flag at `consolidation_hold_days` (360) and clears both the day the score slips.
14 focuses appended at y 14–18 under `QW2_chapter_end`, all iconic-assigned from sprites already used in this tree, route-neutral in text:
`QW2_restoration_programme` (root, `allow_branch` + tooltip-bearing `available`), then court / reform / army / provinces / treasury (y 15), nobility / code / guard / gentry (y 16), constitution / succession / legation (y 17), `QW2_restoration_proclaimed` (y 18).
The root and the three convergence nodes and the capstone each carry `allow_branch = { qing_consolidation_sustained = yes }`, so a lapse closes the band; rewards are political power, standing, equipment, manpower, a research slot and the flags `qing_restoration_constitution`, `qing_restoration_succession`, `qing_restoration_recognised`, `qing_restoration_proclaimed` for the wartime chapter.

## Files changed (all owned)

- `common/script_constants/qing_campaign.txt` — consolidation constants, `reform_weak`.
- `common/scripted_triggers/qing_campaign.txt` — `qing_consolidation_settled`, `qing_consolidation_sustained`, `qing_reform_weak`, `qing_provinces_strained`.
- `common/scripted_effects/qing_campaign.txt` — `qing_consolidation_refresh`, refresh call in `qing_refresh_mechanics`, tick clock, chapter-two gate, `qing_open_chapter_two` guard, `qing_route_chapter` gate.
- `common/decisions/qing_campaign.txt` — seven decisions in `qing_imperial_government`.
- `common/national_focus/qing_interwar.txt` — 14-focus band, header bounds 85→99 focuses / 14→19 rows.
- `localisation/english/qing_campaign_decisions_l_english.yml` — 14 decision/tooltip keys plus the two flag keys `QIN_constitution_promulgated` and `qing_constitution_1912` that the decision panel previously printed raw (MCP `SCRIPT_FLAG_TOOLTIP_UNLOCALISED`, pre-existing).
- `localisation/english/qing_interwar_l_english.yml` — 28 focus keys and `qing_restoration_band_tt`.
- `.tools/tests/test_qing_consolidation.py` — new six-section source test.
- `docs/plans/qing_1910_1945/subagent_handoffs/consolidation.md` — this file.

## Validation

`python .tools/tests/test_qing_consolidation.py` — **6/6 sections PASS, exit 0**:
1. score derived from five families (arithmetic re-derived: full 100.0, opening 25.0, settled+3 works 56.0, settled+5 works 64.0; single-writer scan across `common/`, `events/`, `common/on_actions/`; every works flag set somewhere).
2. five programmes with progress and failure (7 decisions added, every pre-existing decision in the category byte-identical).
3. interwar gate (settled 59/60/61/unset; tick gate for date-only, gate-only, both, already-open; effect guard; route_chapter gate; baseline control proves the baseline was unguarded).
4. sustained band (sustained for bar-without-time, bar-and-time, time-without-bar; the clock's if/else pair; 14 focuses, all reachable from the root, prerequisites strictly above, all localised).
5. every pre-existing focus preserved (id, icon, x, y, cost, filters, `allow_branch`, `available`, `mutually_exclusive`, prerequisites, reward), no shared cells, same-row spacing ≥ 2 on all 18 rows.
6. constants/references/localisation (65 distinct constants resolve, both files BOM-clean, no `§`/`£`, no duplicate keys, the documented bar of 60 in both tooltips, no raw flag in a decision requirement).
**Non-vacuity:** removing the tick gate and the band's `allow_branch` makes sections 3 and 4 fail (exit 1); restoring both returns exit 0.

MCP evidence (read-only routes, `workspaceId: current`):

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.focus_inspect` | `treeId=qing_interwar` (before) | 85 focuses, layoutHash `71044d10…`, bounds 46×14, nodeIntersection 2, crossings 42, tooClose 0, validation passed |
| `hoi4.focus_inspect` | `treeId=qing_interwar` (after) | 99 focuses, layoutHash `e60e82c2…`, bounds 46×19, nodeIntersection **2**, crossings **42**, tooClose **0**, validation passed, 0 blocking. Resource `hoi4-agent://…/focus-inspect.bcc920c042645814.json` |
| `hoi4.script_validate` | `path=common/decisions/qing_campaign.txt` | valid, 397 commands (was 306 + 2 flag-tooltip warnings), 0 findings |
| `hoi4.script_validate` | `path=common/scripted_effects/qing_campaign.txt` | 507 commands, 0 findings, `SCRIPT_CHECK_PARTIAL` (105 native argument blocks unchecked, 31 scope-less roots) |
| `hoi4.script_validate` | `path=common/scripted_triggers/qing_campaign.txt` | 100 commands, 0 findings, `SCRIPT_CHECK_PARTIAL` (18 native argument blocks) |
| `hoi4.script_validate` | `path=common/national_focus/qing_interwar.txt` | valid, 288 commands, 0 findings |
| `hoi4.decision_inspect` | `mode=inventory` (before) | 4,346 decisions / 1,366 categories, reportHash `fc4e9d82…`, unresolved 0 |
| `hoi4.decision_inspect` | `mode=inspect id=qing_convene_interwar` | **unavailable**: `PROBABILITY_GAME_VERSION_UNSUPPORTED` — adapter target Operation Postern 1.19.2.0 (d245), configured game 1.19.3.0 (5632). One attempt, not retried; the gate was proved by source triggers and the Python evaluator instead. |

Coverage limits: `parametersChecked: false` on every validate run; the decision scenario route could not run at all (version mismatch above); nothing here proves the decisions render, the band appears, or that the AI takes a programme.

## Open items for Director

1. **`docs/systems/qing_campaign.md` is stale in three ways now**: still says a settlement annexes the Republic and that the window precedes Wuchang (carried from C7), and it has no consolidation section at all. It is not my file. Needs the score, the five programmes, the 60 gate and the sustained band.
2. `docs/plans/qing_1910_1945/current_report.md` still lists 85 interwar focuses and has no C8 row; also not mine.
3. `qing_consolidation_works_lapsed` and the four family lapse flags are written and localised only where read; no idea consumes them yet. They are receipts for the wartime chapter, not a live penalty surface — a future card that adds a lapse spirit should read them.
4. `.tools/` is gitignored; the new test needs `git add -f .tools/tests/test_qing_consolidation.py` from Director (same open item C7 raised).
5. The band is deliberately route-neutral; if Director wants route-flavoured restoration text, that is new design, not a defect.

## Not performed

No game launch, no in-game claim, no commit, no push, no premium model, no Obsidian write (serialised through Director), no `focus_rewrite`/`gui_rewrite`/`map_rewrite`, no artwork change, no icon reassignment outside the new band.

## Correction 1 (C8a, 2026-10-26) — the divisor is a documented operand

Raised by QA as the only unverified engine question and admitted by Director as implementation slot 1 of 2.
`divide = constant:qing_story.consolidation_family_divisor` inside a math operand has no vanilla or Endsieg precedent, and the documented failure mode of a math expression that fails to parse is replacement with `0.0` (`documentation/script_concept_documentation.md`, §Math Expressions, "Error Handling").
That would have pinned `qing_consolidation` at its floor, kept `qing_consolidation_settled` false forever and made the whole `qing_interwar` chapter unreachable — a silent failure no source check of the old shape could catch.

**What changed (one hunk, inside `qing_consolidation_refresh`).** The divisor is read into a country variable first, then divided by that variable:

```
	set_variable = { qing_consolidation_divisor = constant:qing_story.consolidation_family_divisor }
	set_variable = { qing_consolidation = { value = qing_legitimacy divide = qing_consolidation_divisor } }
	add_to_variable = { qing_consolidation = { value = qing_reform divide = qing_consolidation_divisor } }
	add_to_variable = { qing_consolidation = { value = qing_army_loyalty divide = qing_consolidation_divisor } }
	add_to_variable = { qing_consolidation = { value = qing_provincial_trust divide = qing_consolidation_divisor } }
```

Both halves are documented, not inferred: §Script Constants says constants are "only supported where explicitly stated" but that "all scoped variables accept script constants … by using the prefix `constant:`", and §Math Expressions says operands may be "constants, scoped variables and mathematical functions" with the example `{ value = 5.0 add = num_factories }`.
Nearest repository precedent for the first line: `common/scripted_effects/iran_campaign.txt:106-110` (29 such `set_variable` assignments exist across `common/`).

**What did not change.** `clamp_variable = { var = qing_consolidation min = constant:qing_story.consolidation_floor max = constant:qing_story.consolidation_cap }` was already the shipped form and is byte-identical; Director's correction to the admission confirms criterion 2 was satisfied by the delivered package, so it was not touched.
The score arithmetic, the five works flags, the five lapse flags, the four gated sites, the 14-focus band with its ids/icons/layout and the other six C8 files are untouched.
`diff` against the pre-correction working tree: 4 lines replaced, 1 declaration and a 4-line comment added, nothing else in the file.

`qing_consolidation_divisor` is bookkeeping: no trigger, tooltip, decision or focus reads it, and it holds the same 5 the constant holds.

**Test change.** `.tools/tests/test_qing_consolidation.py` pins the operand shape in a new `divisor_shape_failures()` helper:
the divisor must be read from `constant:qing_story.consolidation_family_divisor` into `qing_consolidation_divisor`; that read must precede the first division; no `divide`/`multiply`/`add`/`subtract`/`clamp` operand anywhere in the file may be a `constant:`; and no math-block `clamp` may survive.
The pre-correction shape is the mutant control and is rejected with 6 findings.

**Validation (this correction).**

| Check | Result |
| --- | --- |
| `python .tools/tests/test_qing_consolidation.py --detail` | **6/6 sections PASS, exit 0**; `constant-operand mutant: 6 finding(s)`; 99 focuses / 18 rows / 65 constants / 205 focus keys unchanged |
| `divisor_shape_failures` on the shipped body | 0 findings; `divide` operands = `['qing_consolidation_divisor']`; constant operands = `[]`; math-block clamps = `[]` |
| `divisor_shape_failures` on the real pre-correction file (byte copy taken before the edit) | **6 findings** — 4 × `divide operand constant:… is a script constant`, plus the missing declaration and the missing variable divide |
| `python .tools/tests/test_qing_survival.py` (C7 regression) | 8/8 PASS, exit 0, against baseline `f6d12527cc8a` |
| `hoi4.script_validate` `path=common/scripted_effects/qing_campaign.txt` | `SCRIPT_CHECK_PARTIAL`, **0 findings**, 508 commands (was 507), `checksPerformed` = syntax, command_kind, declared_scope, event_popups, known_mistakes, `parametersChecked: false`, 106 argument blocks unchecked, 31 unknown-scope roots, unresolvedCount 0 |
| `hoi4.script_validate` `path=common/script_constants/qing_campaign.txt` | `SCRIPT_CHECK_PARTIAL`, 0 findings, `family: unsupported`, 0 commands checked — the checker does not model `script_constants` files, so this route proves only that the file parses as text |
| `hoi4.source_lookup symbol=qing_consolidation_refresh` (before and after) | 1 definition both times (`mod:common/scripted_effects/qing_campaign.txt`, now lines 101-121); the same 12 references, same files and lines (11 decision sites, `qing_refresh_mechanics` at line 95), so no caller changed |
| `hoi4.source_lookup symbol=qing_consolidation_divisor` (before the edit) | 0 definitions, 0 references — the name was unused, so the new variable cannot collide |

**What remains unverified.** `parametersChecked` is false on both validate runs, so the routes never parsed the math operands themselves; the engine question is now removed by construct choice (the documented constant-into-variable form and the variable operand), not by in-game proof.
A launch is still the only way to read `[?qing_consolidation|0]` on a QIN start, and no launch was performed or authorised.
No commit, no push, no branch switch, no artwork change.

