# S14 — Restoration loyalty/coup inversion and misleading reward payloads

Card: `t_d55f9e63` (created as S12, relabelled S14 by Director). Branch: `TeknoDev-Branch`.
Base commit: `5ad0945ad`. No launch, no commit, no push, no staging.
This is a source and MCP package. Nothing here is a live game test.

## The sign convention, derived before anything was edited

Both meters are defined in `common/script_constants/spain_campaign.txt` and read by
`common/scripted_triggers/spain_campaign_triggers.txt`:

- `spain_military_loyalty` is a **loyalty rating**: high is good. `spain_loyalty_high` requires
  `loyalty_loyal` (70) with `greater_than_or_equals`; `spain_loyalty_low` requires
  `less_than` `loyalty_wavering` (40). The gain constants are positive (`loyalty_gain_small` 5,
  `loyalty_gain` 10, `loyalty_gain_large` 15) and the loss constants are negative (-5, -10, -15).
- `spain_coup_pressure` is a **risk rating**: high is bad. `spain_coup_risk` requires
  `greater_than_or_equals` `coup_attempt_floor` (35), and `spain_coup_check` multiplies the
  coup event by 1.50 at `greater_than_or_equals` `coup_collapse` (80).
- The coup constants are therefore **magnitudes whose name says which way they move**: `coup_gain`
  (3) and `coup_gain_fast` (6) are added, `coup_relief` (8) and `coup_relief_large` (15) must be
  subtracted. Three independent precedents in the same file agree: `spain_loyalty_gain_large`
  **sets** the meter to 0, and both non-coup outcomes (`spain_coup_outcome_failed`,
  `spain_coup_outcome_conceded`) set it to 0.

The shipped defect was that the two smaller gain helpers **added** `coup_relief` and
`coup_relief_large`, so a "loyalty gain" moved the risk meter 8 or 15 points *towards* a coup, and
two focuses (`SPR1_royal_guard`, `SPR1_peninsular_reform`) added a third +8 on top for +23.

## Changed files (all inside the card's owned list)

| File | Change |
| --- | --- |
| `common/scripted_effects/spain_campaign_effects.txt` | `spain_loyalty_gain_small` and `spain_loyalty_gain` now `subtract_from_variable` the relief constants instead of adding them. The six-helper block carries the sign convention as a comment. The loss helpers, `spain_loyalty_gain_large` and every coup branch are untouched. |
| `common/national_focus/spain_restoration.txt` | The two direct `add_to_variable … coup_relief` writes inside rewards (`SPR1_royal_guard`, `SPR1_peninsular_reform`) are deleted; the helper now delivers the relief once. `SPR1_court_party` gains `spain_party_shift_monarchists = swing_small` + recount, `SPR1_cacique_deputies` gains `spain_crown_patronage = patronage_gain` + `spain_party_shift_monarchists = swing_medium` + recount, `SPR1_constitutional_crisis` gains `spain_push_cortes_small` + `spain_push_crown_small`. The eight focuses that set a recount-read seat flag without recounting themselves (Electoral Machine, Press Freedom, Liberal Party, Conservative Party, Conciliate the CNT, Repress the CNT, Mancomunitat, Suppress the Mancomunitat) now call `spain_cortes_recount = yes` immediately after the flag. The ten loyalty-gain focuses show a new `custom_effect_tooltip = spain_officer_corps_calms_tt`. No id, icon, coordinate, cost, prerequisite, `mutually_exclusive` or `ai_will_do` changed. |
| `localisation/english/spain_campaign_focus_l_english.yml` | One new key, `spain_officer_corps_calms_tt`. BOM and CRLF preserved byte-for-byte; no other line touched. |
| `.tools/tests/test_spain_restoration_loyalty.py` | New source-driven test, 146 checks, with the pre-repair tree as the negative control. |
| `docs/plans/spain/subagent_handoffs/restoration_loyalty.md` | This file. |

## Evidence actually run

`python .tools/tests/test_spain_restoration_loyalty.py` → **146 checks, 0 failures**.
Areas: helpers 21, affected focuses 21, shared payload 11, seats 72, tooltips 11, plus 10
negative-control checks. What it asserts:

1. all six helpers write both meters with the sign their name promises, resolving the constant
   each one reads from `common/script_constants/spain_campaign.txt` (5/10/15 gain, 8/15 relief, 3/6 risk);
2. the ten focuses that call a gain helper net **+5 or +10 loyalty and −8 or −15 pressure**,
   computed by expanding the helper call, and the set of such focuses is exactly those ten;
3. no focus rewards the relief constants itself;
4. the three ex-duplicate focuses now pay three different things and each pays what its own text
   claims;
5. all nine `…_seats_tt` tooltips match the direction of the recount rule behind them, every
   focus that sets a recount-read flag recounts on completion, and no recount rule moves a party
   the tooltip does not mention;
6. the ten repaired focuses carry the officer-corps tooltip and the key exists once.

Regression: `test_spain_cortes_recount.py` 215 checks / 0 failures and
`test_spain_cortes_runtime.py` 111 checks / 0 failures still pass on the same tree.

### The negative control

The same five areas run against `5ad0945ad` and must each fail there:

| Area | Failures on the pre-repair tree | Example |
| --- | --- | --- |
| helpers | 4 | `spain_loyalty_gain_small` pressure delta **+8.0** |
| affected focuses | 12 | `SPR1_royal_guard` pressure delta **+23.0** — S5's worked figure reproduced exactly |
| shared payload | 11 | `SPR1_cacique_deputies pays something SPR1_court_party does not` — identical payload |
| seats | 16 | `SPR1_electoral_machine recounts on completion` |
| tooltips | 11 | `the officer-corps tooltip is defined once — got 0, expected 1` |

## MCP routes run (read-only)

| Route | Parameters | Result | Resource |
| --- | --- | --- | --- |
| `hoi4.focus_inspect` | `treeId: spain_restoration_focus`, working tree reverted to `5ad0945ad` for this call | 77 focuses, layoutHash `7d5f866660b88d1766fc64d99d150a87618d01e18703bd97baabb126a1e79f5a`, 88 connectors, 2 crossings, 4 node intersections, 0 long connectors, 0 too-close pairs, bounds 33×10, 23 diagnostics, 0 blockers, `validation.passed: true`, source revision `ed44eaef…` | `hoi4-agent://workspace/endsieg/artifact/92415c82…/focus-inspect.ed44eaef0c8bcbbe.json` |
| `hoi4.focus_inspect` | same, after the repair (re-run after restoring the file, to prove the restore) | identical layoutHash and every metric; 23 diagnostics, 0 blockers, `validation.passed: true`, source revision `67e4b510…` | `hoi4-agent://workspace/endsieg/artifact/8f1e3635…/focus-inspect.67e4b510c4bc21da.json` |
| `hoi4.focus_render` | `relativePath: common/national_focus/spain_restoration.txt`, `treeId: spain_restoration_focus`, `png: false` | 5936×1280, layoutHash `7d5f8666…`, **19 layout warnings** — 11 `FOCUS_LAYOUT_LINEAR_DETOUR`, 4 `FOCUS_LAYOUT_CONNECTOR_THROUGH_NODE`, 2 `FOCUS_LAYOUT_STAIRCASE_CHAIN`, 1 `FOCUS_AVOIDABLE_CONNECTOR_CROSSING`, 1 `FOCUS_LAYOUT_CONNECTOR_CROSSING_UNSATISFIED`; identical to S5's list, no new warning | `hoi4-agent://workspace/endsieg/artifact/bb94c126…/spain_restoration_focus.focus.json` (+ source-map, plan, html, svg) |
| `hoi4.script_validate` | `path: common/national_focus/spain_restoration.txt`, `limit: 32` | `SCRIPT_CHECKED`, valid true, 481 commands, 0 findings, 82 roots, 0 unknown-scope roots; 84 argument blocks unchecked, `parametersChecked: false`. S5 recorded 458 commands on the same file, so the 23 new statements are the difference | inline |
| `hoi4.script_validate` | `path: common/scripted_effects/spain_campaign_effects.txt`, `limit: 32` | `SCRIPT_CHECK_PARTIAL`, 0 findings, 1210 commands, 54 roots all unknown-scope for this file, 211 argument blocks unchecked. Command count is identical to the pre-change count in the S10 handoff, so the partial status is pre-existing, not new | inline |
| `hoi4.source_lookup` | `symbol: spain_loyalty_gain` | 1 definition (`spain_campaign_effects.txt:659-662`, `overridden: false`) and 27 references, 10 shown (decisions and both Republic trees included) | inline |

Layout warnings recorded, not repaired: repairing them is a coordinates change, which this card
forbids. `layoutHash` is **unchanged** before and after on the same tree, which is the proof that
no node moved.

## Coverage limits and unperformed checks

- **No game launch, no playtest, no save, no rendered PNG review.** `png: false` was used on
  purpose: the layout verdict comes from the renderer's JSON and geometry, not from a picture, and
  this session cannot eye-review an image. The tree is **not** visually verified.
- `parametersChecked: false` on both script-validate runs, so native argument blocks stay
  unchecked; the tool's own coverage gap, not a pass.
- `hoi4.probability_inspect` / `decision_inspect` were not run: the adapter/game version mismatch
  that has blocked both since S1 (adapter 1.19.2.0 vs installed 1.19.3.0) is unchanged. No AI
  evidence exists for this package, and `ai_will_do` was not modified.
- English only; the repo ships `english` and `replace` only (S0 R9).

## Residuals for Director (outside this card's owned paths — reported, not touched)

1. **The same inversion is still live outside the Restoration.** The additive relief pattern
   remains at `common/decisions/spain_campaign.txt:132,146,743`,
   `common/scripted_effects/spain_cortes_bills.txt:472,483,493`,
   `common/national_focus/spain_republic.txt:611,1003`,
   `common/national_focus/spain_republic_postwar.txt:444`,
   `common/national_focus/spain_rivera.txt:291,743`, and inside the coup machinery itself at
   `common/scripted_effects/spain_campaign_effects.txt:709` (the fizzle branch *adds* `coup_relief`)
   and `:723` (`spain_coup_outcome_failed` adds `coup_relief_large`). S5's own scope warning. The
   Restoration is now internally consistent; the other four chapters are not, and the coup
   machinery contradicts itself. One shared sign card is still owed.
2. **`on_national_focus_complete` remains unverified and lives in a file this card does not own**
   (`common/on_actions/spain_campaign.txt:15`). Evidence: no occurrence in the installed vanilla or
   DLC `common/on_actions`, no entry in the offline wiki on-actions page, no entry in the installed
   `documentation/`. I re-tested the binary-string probe and it is worthless here — the
   definitely-valid `on_yearly` and `on_war_declared` are also absent from `hoi4.exe`, so a
   negative result proves nothing. I did **not** invent a handler. What this card did instead is
   make the chapter independent of it: the eight seat-flag focuses now recount in their own reward,
   which is the supported mechanism, so the seat tooltips no longer depend on that hook. If the name
   is valid the recount simply runs twice and produces the same chamber (the recount rebuilds raw
   support from the era base, the flags and the shifts, so it is idempotent). The dead-looking block
   itself still needs its owner.
3. **The stale focus count is in two documentation files, neither owned here.**
   `docs/plans/spain/current_report.md:34` says the Restoration tree has 36 focuses (it has 77) and
   `docs/spain_campaign.md:172` says "36 focuses" while the same file's table at `:27` says 77.
   S5's D3 and S0's R8 already own the report; the campaign doc needs the same correction.
4. **`spain_royal_guard_tt` still promises troops** ("household troops answer to the Crown alone")
   while the focus pays loyalty and stability and adds no unit, division or manpower. Its text
   lives in `localisation/english/spain_campaign_l_english.yml` (not owned here). With the sign
   fixed the focus now genuinely secures the Crown, so the remaining gap is the unit, not the
   loyalty.
5. **Two focuses double-count on purpose-preserved payloads, left alone.**
   `SPR1_juntas_de_defensa` (`spain_loyalty_loss` + a direct `coup_gain`, so +12 risk) and
   `SPR1_the_coup_that_waits` (`spain_loyalty_loss` + `coup_gain_fast`, +12) are directionally
   correct — a loss focus may raise risk — so they are not part of the inversion. Removing the
   duplicate would halve their bite, which is a balance decision for the owner, not a bug fix.
6. **Vault write deferred.** `TEAM.md` serialises Obsidian writes through Director, so this
   handoff is the durable record and the vault log is left to Director.
