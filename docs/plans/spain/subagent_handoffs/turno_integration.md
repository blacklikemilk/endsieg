# S12b — Turno integration finished: two majority comparisons and the party-reference registry

Card: `t_00b07993`. Branch: `TeknoDev-Branch`. Base commit: `ce6247246`. No launch, no commit, no staging, no push.
This package finishes the original S12 (`t_cb995ac7`) and S12a (`t_47329669`) delivery for combined integration. Nothing here is a live game test.
Approval basis: Director admission comment on `t_00b07993` reserving exactly six write paths and keeping the original S12 five read-only through integration.

## What was wrong

`spain_government_strain` charged `minority_stability` (-0.02) and `minority_coup` (+3) to every government, a genuine 245-seat majority included, because its `spain_government_majority` test omitted `compare` and the long form of `check_variable` defaults to `greater_than_or_equals` — `0 >= 0` is true.
The incumbent-loss `OR` in `spain_hold_election` had the same omission, so the majority arm was always true, every government lost `incumbent_loss` (-2) support across the four incumbent blocs at every election, and the stability arm never decided anything.
Separately, the delivered turno package failed the real party-reference checker: `tools/check_spain_parties.py` built its registry from four files, so `spain_push_crown`, `spain_loyalty_gain_small` and the `spain_restoration_cortes_live` trigger — all defined in the campaign effects and triggers files — were reported as unknown, and `.tools/tests/test_spain_cortes_postwar_bills.py` exited 1 with 3 failures in 217 checks.
Both defects were pre-existing at `f8d54678c` and confirmed by QA run 126; neither is caused by S12 or S12a.

## Changed files (all inside the card's six owned paths)

| File | Change |
| --- | --- |
| `common/scripted_effects/spain_cortes_parties.txt` | Two tokens: `compare = equals` added to the majority test in `spain_government_strain` (:233) and in the incumbent-loss `OR` inside `spain_hold_election` (:280). No other byte of the S12/S12a delivery changed; the file holds exactly three explicit majority comparisons (those two plus the S12a monthly test at :384) and none implicit. |
| `tools/check_spain_parties.py` | `REGISTRY_ONLY` gains `common/scripted_effects/spain_campaign_effects.txt` and `common/scripted_triggers/spain_campaign_triggers.txt`; the module docstring and the block comment above the list state what each entry resolves and why they are registry-only. No allowlist, no skipped file, no silenced symbol: every `name = yes` call is still resolved against one registry. |
| `.tools/tests/test_spain_turno.py` | New `test_residual_comparisons` with 19 checks; `has_stability < <operand>` support in the trigger evaluator (the incumbent `OR`'s second arm); scoped `revert_majority` helper and `STRAIN_MARKERS` / `ELECTION_MARKERS` so one comparison can be reverted without touching the other. The 109 existing checks are unchanged and all still run. |
| `.tools/tests/test_spain_cortes_postwar_bills.py` | Registry coverage only: two assertions that the new entries are present, three negative controls (withdrawn `spain_loyalty_gain_small`, withdrawn `spain_restoration_cortes_live`, a registry input deleted from the tree), and `COVERED_FILES` extended by the two campaign files so the footer still states what is staged. The original injected-unknown and deleted-definition controls are untouched and still fail as required. |
| `docs/specs/spain_1910_1945/restoration_turno.md` | Status line, the "who the turno pays" comparison list, a new "The S12b finishing correction" section with the before/after table and the S12a registry bullet reconciled, and the stale "two comparisons stay implicit" limitation replaced by the three same-class sites outside this card. No redesign, no tuning or identifier change. |
| `docs/plans/spain/subagent_handoffs/turno_integration.md` | This handoff. |

Untouched, as reserved: `common/scripted_triggers/spain_campaign_triggers.txt`, `common/script_constants/spain_campaign.txt`, `common/decisions/spain_campaign.txt`, `events/spain_campaign.txt`, `localisation/english/spain_campaign_l_english.yml`, every focus file, artwork, the D1 docs and the C3 design doc.

## Combined S12 / S12a / S12b package status

Eleven paths make up the integrated package. Eight are the reserved S12/S12a set; three are this card's documentation and regression surface.

| Path | Status | State on disk |
| --- | --- | --- |
| `common/scripted_triggers/spain_campaign_triggers.txt` | S12, unmodified by this card | modified vs `ce6247246` (S12 delivery) |
| `common/script_constants/spain_campaign.txt` | S12, unmodified | modified (S12 delivery) |
| `common/decisions/spain_campaign.txt` | S12, unmodified | modified (S12 delivery) |
| `events/spain_campaign.txt` | S12, unmodified | modified (S12 delivery) |
| `localisation/english/spain_campaign_l_english.yml` | S12, unmodified; no key added, changed or removed here | modified (S12 delivery) |
| `common/scripted_effects/spain_cortes_parties.txt` | S12a + S12b's two tokens | modified |
| `tools/check_spain_parties.py` | S12b registry repair | modified |
| `.tools/tests/test_spain_turno.py` | S12a suite + S12b's 19 checks | untracked (`gitignore` `.gitignore:5`) — needs `git add -f` at integration |
| `.tools/tests/test_spain_cortes_postwar_bills.py` | S12b registry fixture coverage | modified (tracked) |
| `docs/specs/spain_1910_1945/restoration_turno.md` | S12 + S12a + S12b reconciled | untracked (new in S12) |
| `docs/plans/spain/subagent_handoffs/turno_integration.md` | new | untracked |

Other dirty paths in the tree are not mine and were left exactly as found: `docs/systems/crown_and_majlis.md`, `docs/systems/iran_negotiations.md`, `docs/systems/qing_campaign.md`, `tools/__pycache__/build_spain_cortes_hemicycle.cpython-314.pyc`, `docs/plans/campaign/`, `docs/plans/docs/`, `docs/plans/qing_1910_1945/republic_fragmentation.md`.

## Evidence actually run

```
python .tools/tests/test_spain_turno.py                  -> 128 checks, 0 failures (exit 0); 109 before, all preserved
python .tools/tests/test_spain_turno.py --detail         -> 128 ok lines, 0 FAIL (exit 0)
python .tools/tests/test_spain_cortes_postwar_bills.py   -> 227 checks, 0 failures (exit 0); 217/3 before
python .tools/tests/test_spain_cortes_postwar_bills.py --detail -> 227 ok lines, 0 FAIL (exit 0)
python tools/check_spain_parties.py                      -> exit 0, "registry files: 6, decisions: 17, localisation keys: 49", "no dangling references"
python .tools/tests/test_spain_cortes_recount.py         -> 215 checks, 0 failures
python .tools/tests/test_spain_cortes_runtime.py         -> 113 checks, 0 failures
python .tools/tests/test_spain_restoration_loyalty.py    -> 146 checks, 0 failures
python .tools/tests/test_spain_hemicycle_builder.py      -> 69 checks, 0 failures
```

Before-state, same tree, for contrast: turno 109/0, recount 215/0, runtime 113/0, loyalty 146/0, hemicycle 69/0, postwar 217 checks with 3 failures, checker exit 1 with the three unknown calls.

### The nineteen new turno checks

- Two source assertions: zero implicit `spain_government_majority` comparisons in the file, exactly three explicit ones.
- Six on the strain observation, both halves run through the shipped effect: a bloc of zero majorities pays `-0.02` / `3.0`; a genuine majority (two encasillados → 245 benches, majority 1) pays `0` / `0`.
- Five on the incumbent-loss matrix, the shipped `OR` evaluated at all four combinations: a stable majority `False`; an unstable majority, a stable minority and an unstable minority all `True`. The stable/unstable arms are derived from `election_unrest_threshold`, not literals. Plus an assertion that the block still names its four recipients.
- Six mutant controls.

### Real mutants (not simulated expectations)

`revert_majority` removes exactly one `compare = equals` inside one effect's span; each mutant is a full `Turno` rebuilt from the mutated text.

- Reverting the strain comparison alone: `strain_failures` reports `a majority month moved stability -0.02, expected 0` and `a majority month moved coup pressure 3.0, expected 0`; `incumbent_failures` stays empty.
- Reverting the election comparison alone: `incumbent_failures` reports `a stable majority fires the incumbent loss True, expected False`; `strain_failures` stays empty.
- Reverting both (the pre-card state) reproduces both findings at once.
- Registry mutants in the postwar suite: withdrawing `spain_loyalty_gain_small` → exit 1, `spain_cortes_parties.txt calls unknown effect: spain_loyalty_gain_small`; withdrawing `spain_restoration_cortes_live` → exit 1, same shape; deleting `spain_campaign_triggers.txt` from a staged tree → exit 1 with the file named (a missing registry input is refused, not skipped).
- The suite's original controls still fire: injected `spain_bill_count_phantom` → exit 1; deleted `spain_bills_count_all` → exit 1; the pre-change checker still fails on this tree.

## MCP evidence (own, before and after)

Route: `hoi4_agent_tools` (HOI4 Agent Tools), `workspaceId: current`.

- `hoi4.source_lookup` `spain_government_strain`, before: 1 definition, `mod:common/scripted_effects/spain_cortes_parties.txt` lines 231-238, body `check_variable = { var = spain_government_majority value = 0 }` with no comparison; 7 callers (`SPR_coalition_monarchists` :212, `_liberals` :232, `_conservatives` :252, `_republicans` :272, `_socialists` :293, `SPR_drop_the_coalition` :312, `spain_bill_penalise_government` :312); workspace revision `50c02815d1cc49a7a2491e2d278480f4cd4cf1aafb7f17a2b951c7dac8757d81`, `referencesComplete: false`, `unresolvedReferenceCount: 2570`, no artifact URI.
- `hoi4.source_lookup` `spain_government_strain`, after: same lines 231-238 with `compare = equals` at 233, same 7 references, revision `ea7dfb2ecadf32fdc41c8d1c853b569fb978d6bfe745d9b8161830af39bea92c`.
- `hoi4.source_lookup` `spain_hold_election`, before: 1 definition lines 247-294, body to :284 shows the `OR` with `check_variable = { var = spain_government_majority value = 0 }`; 4 callers (`SPR_honest_election` decisions/spain_campaign.txt:166, `SPR_call_election` decisions/spain_parties.txt:25, `spain_bill_pass_electoral` :555, `spain_bill_water_electoral` :564).
- `hoi4.source_lookup` `spain_hold_election`, after: same block, `OR` arm now `compare = equals` at :280 (body returns to :280 column 81; `nextLine: 281`).
- `hoi4.script_validate` `path=common/scripted_effects/spain_cortes_parties.txt`, before and after: `SCRIPT_CHECK_PARTIAL`, `totalFindings: 0`, `checkedCommands: 332`, `parametersChecked: false`, `argumentBlocksUnchecked: 193`, `unresolvedCount: 0`, `file.roots: 11`, `file.unknownScopeRoots: 11`, docs revision `9227e238bce49345e9c358598b4dd4940c733d906b72324e8a02a57ecb42093b`. Identical both times, because the route does not evaluate `check_variable`.
- `hoi4.decision_inspect` was deliberately not retried: the adapter/game-version failure is exhausted and the changed inputs are scripted-effect comparisons it does not evaluate. No changed information addresses it.
- No write route was used.

## Documentation and precedent

- Offline wiki `paradox_wiki/Data structures - Hearts of Iron 4 Wiki.md:566` — the `check_variable` row: `compare` "Defaults to `greater_than_or_equals`".
- Installed `documentation/triggers_documentation.md:2110-2132` — the `check_variable` section and its compare values.
- Vanilla precedent `common/scripted_effects/GRE_scripted_effects.txt:23-25` — `check_variable = { var = … value = 0 compare = equals }`, including inside a `NOT`.
- Local precedent `spain_government_recount`'s own zero test, which already carried `compare = equals` before this card.

## Not performed

No HOI4 launch, no live playtest, no save inspection, no desktop operation, no panel repaint, no mission-strip check, no mission-timer check, no hemicycle redraw, no AI campaign observation, no branch or worktree operation, no staging, commit, push or merge, no premium model, no vault write.
Source simulation, the checker and the MCP routes prove what the script says; they do not prove the engine's `check_variable` resolution, the panel or the mission strip.

## Residuals for Director (outside this card's owned paths)

1. **Three same-class implicit comparisons remain outside `spain_cortes_parties.txt`**: `common/decisions/spain_cortes.txt:345` and `events/spain_cortes_bills.txt:420` weight an `ai_chance` modifier on `check_variable = { var = spain_government_majority value = 0 }`, so the modifier always applies; `common/national_focus/spain_republic.txt:1180` uses the same test in a focus `available` `OR`, so that arm is always true. Each needs its own card. The `value = 1` tests at `common/scripted_localisation/spain_cortes_panel.txt:171,189` are the boolean form and are correct as written.
2. **`.tools/` is gitignored** (`.gitignore:5`), so `test_spain_turno.py` is durable on disk but needs `git add -f` to enter the integration commit; `test_spain_cortes_postwar_bills.py` is already tracked and only needs staging.
3. **`tools/check_script_bom.py` exits 1 on `common/national_focus/spain_restoration.txt`** (BOM at offset 0). It is committed at HEAD, outside this card, and was already recorded as residual 3 in the S10 handoff; left untouched. The two scripts this card edited carry no BOM (first bytes of the parties file are `# Ove`).
4. **A missing registry input fails with a Python traceback rather than a one-line message.** The new control asserts the nonzero exit and that the missing file is named, which is what criterion 4 requires; leaving the checker's error handling alone kept this card's checker change to the registry and its docstring.
5. **`hoi4.source_lookup` still reports `referencesComplete: false` with 2570 unresolved references workspace-wide** — the index's standing coverage limit, not this package.
6. **`spain_election_manufactured` and `spain_government_changes` remain write-only** (unchanged since S12); the band-idea card owns that hook.
7. **The mission still normally cancels rather than completes** because the appointment clears `spain_ministry_crisis_open` as the bloc crosses 201 (unchanged, by design per the spec).

## Open questions for QA

- Is a two-token change plus a registry expansion enough to justify the 19 new turno checks and 10 new postwar checks, or is any of them redundant with an existing assertion? The strain and incumbent checks were written to fail on the pre-card text and on each single-block revert, which the mutant controls demonstrate.
- Should the three same-class sites in residual 1 be carded together as one comparison-class sweep, or separately by file ownership (decision, event, focus)?
