# S11 — Postwar legislative visibility and the party-check registry

Card: `t_7f704b60`. Branch: `TeknoDev-Branch`. Base commit: `5ad0945ad` (S10 integrated).
No game launch, no commit, no push, no branch switch by this worker.
This is a source, tool and MCP package; nothing here is a live game test.

## What the player-visible defect was

S10 made the six `spain_chapter_*` flags exclusive, but `common/decisions/spain_cortes.txt` still gated
every bill on the Restoration, the Directory and the Republic only.
A Spain that reached 1939 held `spain_chapter_postwar` or `spain_chapter_republican_postwar`, inherited
nothing from those gates, and therefore lost all six bill decisions while the `SPR_cortes` category
itself stayed visible — a chamber with no legislation in it.

The same reform made `spain_cortes_recount` call `spain_bills_count_all`, and
`tools/check_spain_parties.py` reported that real effect as unknown because its registry never read
`common/scripted_effects/spain_cortes_bills.txt`.
The effect exists (`spain_cortes_bills.txt:271-278`, MCP-confirmed); the finding was the checker's gap.

## Changed files (all inside the card's owned list)

| File | Change |
| --- | --- |
| `common/decisions/spain_cortes.txt` | Both postwar chapter flags added to all six `visible` gates, as explicit `has_country_flag` tests inside the existing `OR`. One comment paragraph states the chapter/support split. Nothing outside the six `visible` blocks changed. |
| `tools/check_spain_parties.py` | New `REGISTRY_ONLY` list holding `spain_cortes_bills.txt` and `spain_cortes_hemicycle.txt`; the effect registry is built from the scanned files plus those. New optional `<root>` argument and a `load(root, path)` helper so a test can run the real checker against a shadow tree. Printed header now names the root and the registry size. |
| `.tools/tests/test_spain_cortes_postwar_bills.py` | New durable test, 217 checks, reusing the S9 harness and the S10 decision helpers. |
| `docs/plans/spain/subagent_handoffs/cortes_postwar_bills.md` | This handoff. |

`git diff --stat`: `common/decisions/spain_cortes.txt` 26 insertions / 3 deletions, `tools/check_spain_parties.py` 53 insertions / 16 deletions.
The decisions diff is seven hunks: one comment block and the six `visible` gates, nothing else.

## Criterion 1 — the six gates, chapter by chapter

Every gate keeps its pre-S11 chapter set and gains both postwar chapters; no bill gained a chapter it
never offered and none lost one.
The test derives each expected set from the pinned pre-S11 file plus the two postwar chapters, so a
future widening of the electoral law to the Directory (or any other silent change) fails it.

| Bill | Decision | Visible in, before | Added by this card |
| --- | --- | --- | --- |
| Budget | `SPR_bill_budget` | restoration, rivera, republic | postwar, republican_postwar |
| Agrarian reform | `SPR_bill_agrarian_reform` | republic | postwar, republican_postwar |
| Labour charter | `SPR_bill_labour_charter` | republic | postwar, republican_postwar |
| Army budget | `SPR_bill_army_budget` | restoration, rivera, republic | postwar, republican_postwar |
| Regional statute | `SPR_bill_regional_statute` | republic | postwar, republican_postwar |
| Electoral law | `SPR_bill_electoral_law` | restoration, republic (the Directory excluded, as before) | postwar, republican_postwar |

Verified state for all six: `SPR`, `spain_campaign_initialized` held, exactly one chapter flag held
(S10 exclusivity), no `spain_cortes_dissolved`, no cooldown flag, no bill-passed flag.
In that state the six are visible in `postwar` and in `republican_postwar`, invisible with no chapter
flag, and still invisible in `civil_war` — which offered no bills before this card and is out of scope.
The gates name the postwar flags with `has_country_flag`, reach no chapter through a `NOT`, and still
require `spain_campaign_initialized`; all three facts are asserted per bill.

## Criterion 2 — availability stays a support question

For every bill, in both postwar chapters, the `available` block is evaluated on the real recount of that
chapter (`spain_cortes_recount` writes the six caches and `spain_bill_floor`), with only support varied:

- a 40-seat chamber (`spain_bill_votes_<bill>` 40, `spain_government_seats` 40) is refused — 40 seats short of the 161-seat floor;
- a chamber at the floor (`spain_bill_votes_<bill>` 161, `spain_government_seats` 40) opens;
- the same 40-seat chamber is refused with the chapter flag cleared as well, so no availability gate reads a chapter at all.

The 161-seat floor, the negotiation reach, the political-power costs and the six `days_re_enable` values
are unchanged: every token of the file outside the six `visible` blocks is identical to the pinned
pre-S11 source, and `cost`, `days_re_enable`, `icon`, `available`, `complete_effect` and `ai_will_do`
are additionally compared field by field.

## Criterion 3 — the registry, and the negative controls that prove it

`spain_bills_count_all` now resolves, so `spain_cortes_effects.txt:166` no longer produces a finding.
Four runs are asserted by the test, and a clean exit alone is not one of them:

| Run | Expected | Observed |
| --- | --- | --- |
| Shipped checker on this tree | 0 | 0, "no dangling references" |
| Pre-change checker (`5ad0945ad`) on this tree | 1 | 1, `spain_cortes_effects.txt calls unknown effect: spain_bills_count_all` |
| Shadow tree, unmutated (control for the controls) | 0 | 0, and it reports its own root |
| Shadow tree with `spain_bill_count_phantom = yes` injected into the effects file | 1 | 1, naming `spain_bill_count_phantom` |
| Shadow tree with the `spain_bills_count_all` definition deleted from the bills file | 1 | 1, naming `spain_bills_count_all` |

The shadow trees are staged from the checker's own file list (`checker.EFFECTS` + `REGISTRY_ONLY` +
the four data files, eight files), so the harness cannot drift from the checker.
The deleted-definition control is the one that proves the bills file is what resolves the call rather
than some other file in the registry.

## Evidence actually run

```
python .tools/tests/test_spain_cortes_postwar_bills.py          -> 217 checks, 0 failures (exit 0)
python .tools/tests/test_spain_cortes_runtime.py                -> 111 checks, 0 failures (S10 regression)
python .tools/tests/test_spain_cortes_recount.py                -> 215 checks, 0 failures (S9 regression)
python tools/check_spain_parties.py                             -> exit 0, "registry files: 4, decisions: 17"
python <pre-S11 worktree>/.tools/tests/test_spain_cortes_postwar_bills.py -> 217 checks, 36 failures (exit 1)
```

### The negative control

A detached worktree at `HEAD` (`5ad0945ad`) held the pre-change source while the same two shipped test
modules were copied in, so only `common/decisions/spain_cortes.txt` and `tools/check_spain_parties.py`
differed from this tree.
The suite reported 36 failures there and 0 here: twelve `visible` failures per pattern across the six
bills (both postwar chapters invisible, no postwar chapter named, the chapter set unchanged), plus the
registry, shipped-checker, shadow-control and injected-name checks.
The worktree was removed with `git worktree remove` and `git worktree prune`; `git worktree list` now
shows only the main tree, and no branch was created or switched.

## MCP evidence

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.decision_inspect` `inventory` | `id=SPR_cortes` | `DECISION_ANALYZED`, 1366 categories, 4346 decisions, 0 overrides, `unresolvedDefinitions` 0, `validation.passed` true. Artifact `hoi4-agent://workspace/endsieg/artifact/389670c9…/2229e686…/decision-0b3e798f41cc6a419f5aee3a.json` (3,220,591 bytes) |
| `hoi4.decision_inspect` `inspect` | `id=SPR_bill_budget`, scenario `postwar`, flags `spain_campaign_initialized` + `spain_chapter_postwar` | **unavailable**: `PROBABILITY_GAME_VERSION_UNSUPPORTED`, adapter `Operation Postern 1.19.2.0 (d245)`, observed `Operation Postern v1.19.3.0.c01a (5632)`, source `…/launcher-settings.json`. Not worked around; recorded as the standing block |
| `hoi4.source_lookup` | `spain_bills_count_all` | 1 definition `common/scripted_effects/spain_cortes_bills.txt:271-278`, 2 references (`spain_cortes_effects.txt:166`, `events/spain_cortes_bills.txt:469`), `referencesComplete` false, 2570 unresolved workspace-wide |
| `hoi4.source_lookup` | `spain_chapter_postwar` | 0 definitions, 0 references. The index resolves scripted effects at the same revision (above), so this is flag coverage, not staleness: `has_country_flag = <flag>` is not indexed as a reference |
| `hoi4.script_validate` | `path=common/decisions/spain_cortes.txt` | `SCRIPT_CHECKED`, valid true, 0 findings, `checksPerformed` syntax/command_kind/declared_scope/player_text/event_popups/known_mistakes, `checkedCommands` 77, `unresolvedCount` 0, `argumentBlocksUnchecked` 24, roots 18, unknown-scope roots 0 |
| `hoi4.script_validate` | `path=common/scripted_effects/spain_cortes_bills.txt` | `SCRIPT_CHECK_PARTIAL`, 0 findings, `checkedCommands` 308, `unresolvedCount` 0, `argumentBlocksUnchecked` 143, roots 49, 49 unknown-scope roots — identical to S10's reading; the file is unmodified by this card |

`hoi4.gui_render` was not run: the six bills are ordinary `decision` entries inside the `SPR_cortes`
category, so the bill buttons are drawn by the decision category and not by the Cortes window, and no
window was touched.

## Not verified / what only a launch can confirm

- No game launch, so the category's on-screen appearance in a real 1939 save is unverified; what is
  proven is that the `visible` triggers now evaluate true in both postwar chapters.
- No save inspected, so no real 1939 Spain's flag set was read; the chapter state was constructed from
  the shipped flags and the shipped recount.
- The decision category's own visibility (`SPR_cortes`) is untouched by this card and was already
  passing in the postwar chapters; only the six bills behind it changed.
- The hemicycle, the panel and the localisation keys are untouched; the S9 400-seat invariant and the
  S10 exclusivity are re-run green by their own suites.

## Residuals for Director (outside the owned paths)

1. **`docs/spain_cortes_bills.md` is stale in four places** and needs one editorial pass: line 57 still
   says the era test is `spain_chapter_restoration`, `spain_chapter_rivera` or `spain_chapter_republic`;
   lines 65, 85 and 122 still describe a 60-day cooldown, which S10 replaced with per-bill macros. The
   first item is new from this card, the other three were already reported by S10.
2. **`.tools/` is gitignored** (`.gitignore:5`), so `.tools/tests/test_spain_cortes_postwar_bills.py`
   needs `git add -f` at integration, as the card says; `test_spain_cortes_runtime.py` is already
   tracked from S10, `test_spain_cortes_recount.py` (S9) is not.
3. `hoi4.decision_inspect` `inspect` remains blocked by the adapter/game-version mismatch, so no
   AI-probability evidence exists for the six bills; `ai_will_do` is only proven unchanged token-for-token.
4. `tools/check_spain_parties.py` still holds a dead loop over the category file (`for k in …: pass`) left
   from before this card. It is harmless and was left alone to keep this diff a registry fix.

## Ownership and git

Only the four owned paths were touched; `git status` shows `common/decisions/spain_cortes.txt` and
`tools/check_spain_parties.py` modified and the two new files untracked.
The Iran and Qing modifications and the S14 edits to `spain_campaign_effects.txt` and
`spain_restoration.txt` that appear in the same working tree belong to other workers and were not read
beyond what the tests execute, and not modified.
No commit, no push, no branch switch, no worktree left behind, no artwork touched.
