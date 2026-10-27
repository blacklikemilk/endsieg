# S10 — Cortes chapter model made exclusive and runtime-correct

Card: `t_ac5216ee`. Branch: `TeknoDev-Branch`. Base commit: `f6d12527c`. No launch, no commit, no push.
This is a source and MCP package. Nothing here is a live game test.

## What the player-visible defect was

A continuous campaign never lost its chapter: the six `spain_chapter_*` flags were only ever set, never
cleared, so a Spain that reached 1931 still held `spain_chapter_restoration`. Because the recount chose
the republican chamber by the *absence* of the Restoration and Directory flags, and because
`spain_ensure_chapter_tree` runs on the daily tick, the Restoration and the Republic trees then
alternately mounted on consecutive days. Two further silent failures rode along: the bill-reach gates
opened on a cache that no recount had written yet, and the hemicycle asked an eight-frame sprite strip
for frames 1..8 (an off-by-one; frame 0 is the first frame).

## Changed files (all inside the card's owned list)

| File | Change |
| --- | --- |
| `common/scripted_effects/spain_campaign_effects.txt` | New `spain_clear_chapter_flags` helper clearing all six chapter flags; every one of the six `spain_open_*_chapter` blocks calls it as its first statement. `spain_open_postwar_chapter` now loads `spanish_focus` with `keep_completed`, closing the Director's R10 residual (it previously loaded no tree at all). |
| `common/scripted_effects/spain_cortes_effects.txt` | Both era selections replace the `NOT restoration / NOT rivera` test with `has_country_flag = spain_chapter_republic`. The recount ends with `spain_bills_count_all = yes`. S9's era → flags/shifts → clamp order untouched. |
| `common/scripted_effects/spain_cortes_bills.txt` | One shared `@bill_cooldown_days = 60` replaced by six per-bill macros mirroring each decision's `days_re_enable`. |
| `common/decisions/spain_cortes.txt` | The six fail-open `NOT = { has_variable = spain_bill_votes_<bill> }` gate disjuncts removed. Bill effects and costs unchanged. |
| `common/scripted_effects/spain_cortes_hemicycle.txt` | Every dot's frame value shifted 1..8 → 0..7; header comment states the strip is 0-based. |
| `localisation/english/spain_campaign_l_english.yml` | Duplicate `spain_iberian_accord_tt` removed (the untitled duplicate at old line 347); the titled `§YThe Iberian Accord§!` definition survives. Both focus consumers still reference it once each. |
| `.tools/tests/test_spain_cortes_runtime.py` | New durable source test, 111 checks, reusing the S9 harness. |
| `docs/plans/spain/subagent_handoffs/cortes_runtime.md` | This handoff. |

`events/spain_cortes_bills.txt` is owned by the card for a bootstrap call but needed no change: the
caches are already seeded on a fresh campaign because `spain_cortes_initialize` →
`spain_parties_initialize` (which ends in `spain_cortes_recount`) → the recount's `spain_bills_count_all`.
The test asserts that chain rather than assuming it.

## Evidence actually run

```
python .tools/tests/test_spain_cortes_runtime.py                 -> 111 checks, 0 failures (exit 0)
python .tools/tests/test_spain_cortes_recount.py                 -> 215 checks, 0 failures (S9 regression)
python <scratch>/mutate_baseline.py (suite vs f6d12527c source)  -> 111 checks, 56 failures (required)
python tools/check_spain_parties.py                              -> exit 1, one finding: "spain_cortes_effects.txt calls unknown effect: spain_bills_count_all"
python tools/check_script_bom.py                                 -> exit 1, one finding: BOM in common/national_focus/spain_restoration.txt
```

Both non-zero exits are attributed below and are not this change.

### The negative control

The mutation harness re-runs the same 111 checks with every read pinned to `f6d12527c`. 56 fail there,
0 on the repaired tree, so no section is vacuous: chapter exclusivity, the era base, all six gate
disjuncts, the cache first-writer, and all nine hemicycle frame checks each fail on the defect source and
pass on the repair. Two assertions that previously *raised* on the defect source instead of reporting
(the missing helper, and a tautological cache comparison that indexed a variable it had just read) were
rewritten during this pass — a negative control that crashes is not a negative control.

## MCP routes run (read-only)

- `hoi4.script_validate` on all five changed script files: **0 findings** in every one.
  `common/decisions/spain_cortes.txt` returned `SCRIPT_CHECKED`, `passed: true` (62 commands, 0 unresolved).
  The four scripted-effects files returned `SCRIPT_CHECK_PARTIAL` (syntax, command kind and declared scope
  clean; 211/137/143/1500 argument blocks unchecked and all roots "unknown scope", which is the family's
  normal state because a scripted effect declares no scope). Coverage is partial, not proof.
- `hoi4.source_lookup spain_clear_chapter_flags`: 1 definition (`spain_campaign_effects.txt:86-93`),
  6 references — the six openers at lines 96, 114, 134, 155, 185, 204. No other definition, no override.
- `hoi4.source_lookup spain_bills_count_all`: 1 definition (`spain_cortes_bills.txt:271-278`),
  2 references — `spain_cortes_recount:166` and `spain_bills.90:469`. Exactly the two intended call sites.
- No `hoi4.focus_inspect` run: no focus file was touched. Both referenced focus trees were read as text
  only, to confirm the tooltip consumer count.

## Coverage limits and unperformed checks

- **No game launch, no playtest, no save inspected.** A clean static pass does not prove the daily tree
  assert stops alternating, that the panel renders frames 0..7 as the eight registered sprites, or that a
  bill is actually offered the day the Republic opens. Only a load and a played campaign can show that.
- The test simulates the script's own semantics (flags, effects, if/else, clamps, variables). It does not
  model the engine, the AI, tooltips, or `has_power_balance` (the test state carries no live balance, so
  those guards read as absent).
- `hoi4.decision_inspect` was not attempted; the parent audit recorded it blocked by an adapter/game
  version mismatch, so there is still no AI-probability evidence for the bill decisions.
- `localisation/` contains only `english` and `replace`, so an all-language check is unperformable, not
  passed (inherited from S1).

## Residuals for Director (not in this card's owned paths)

1. **`tools/build_spain_cortes_hemicycle.py` still generates 1-based frames** (`FRAME_EMPTY = 1`,
   `frame_of = party_index + 1`, and a comment asserting "Sprite frames are 1-based in HOI4"). The
   shipped effect is now 0-based as the frame strip requires, so **regenerating the hemicycle silently
   reverts outcome 4**. The generator needs the same shift, or the file needs a note that it was
   hand-corrected.
2. **`tools/check_spain_parties.py` builds its effect registry from the effects file plus the hemicycle
   only**, so it cannot see `spain_cortes_bills.txt` and reports `spain_bills_count_all` as unknown. The
   effect is defined at `spain_cortes_bills.txt:271` and was already called from
   `events/spain_cortes_bills.txt:469` before this card; the finding is a checker gap.
3. **Pre-existing BOM at offset 0 of `common/national_focus/spain_restoration.txt`** — present at
   `f6d12527c`, unmodified by this card, flagged by `tools/check_script_bom.py`. Left untouched.
4. **`docs/spain_cortes_bills.md` still documents a 60-day cooldown** (lines 65 and 85) after the
   per-bill cooldowns. Stale, outside the owned paths.
5. `hoi4.source_lookup` reports `referencesComplete: false` with 2570 unresolved references workspace-wide;
   that is the index's standing coverage limit, not this card's files.
6. **`.tools/` is gitignored** (`.gitignore:5`), so the new test is durable on disk but will not enter a
   commit without `git add -f`. `test_iran_gulf_rewards.py` is the one file already force-added there;
   `test_spain_cortes_recount.py` (S9) is untracked for the same reason. Director's call whether to
   force-add `test_spain_cortes_runtime.py` alongside it.

