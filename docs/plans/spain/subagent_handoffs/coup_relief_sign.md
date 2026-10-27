# S15 handoff — coup relief subtracts in all four non-Restoration chapters

Card: `t_99deaa4a`. Branch `TeknoDev-Branch`, HEAD `36c6ebc4d5291ef7424808a4e0960269afe8f02b`
(`b2774a393` at first delivery; three unrelated commits landed since and touched none of these paths).
No commit, no push, no launch, no branch switch. Nine owned paths only, after the Director expanded
this card by the one localisation file in round 2.

## What was wrong, and what changed

`spain_military_loyalty` is a loyalty rating and `spain_coup_pressure` is a risk rating
(`spain_coup_risk` compares it with `coup_attempt_floor` 35; `spain_coup_check` multiplies the coup
branch 1.50× at `coup_collapse` 80). The `coup_relief*` constants are therefore magnitudes that
must be subtracted. S14 fixed the four officer-corps helpers in the Restoration chapter; thirteen
sites in the other three trees and the bill/decision effects still **added** the same constants,
so garrisoning the cities, amnestying the juntas or passing the army budget paid political power
and equipment to push the coup chance toward the coup.

All thirteen now use `subtract_from_variable` on `spain_coup_pressure`, with the identical
constant and the identical magnitude. No constant, identifier, decision id, focus id, icon,
cost, cooldown, availability, prerequisite, mutex or AI weight was touched, and no localisation key
was invented or renamed — round 2 corrected the value of one existing key that this repair had
inverted (see below).

Each site was re-verified by content before editing, not by the card's line list. **None** of the
thirteen turned out to be an escalation: every one reads as relief in its own text (garrison the
cities, amnesty for the juntas, secure the garrisons, public order, amnesty of 1931, political
police, army reorganisation, somatén, the plot that fizzles, the failed coup, and the three army
budget outcomes).

| File | Line | Scope | Constant | Before → after |
| --- | --- | --- | --- | --- |
| `common/decisions/spain_campaign.txt` | 276 | `SPR_garrison_the_cities` | `coup_relief_large` (15) | add → subtract |
| `common/decisions/spain_campaign.txt` | 290 | `SPR_amnesty_for_the_juntas` | `coup_relief` (8) | add → subtract |
| `common/decisions/spain_campaign.txt` | 887 | `SPR_secure_the_garrisons` | `coup_relief_large` (15) | add → subtract |
| `common/scripted_effects/spain_cortes_bills.txt` | 472 | `spain_bill_pass_army` | `coup_relief` (8) | add → subtract |
| `common/scripted_effects/spain_cortes_bills.txt` | 483 | `spain_bill_concede_army` | `coup_relief` (8) | add → subtract |
| `common/scripted_effects/spain_cortes_bills.txt` | 493 | `spain_bill_water_army` | `bill_coup_relief_half` (4) | add → subtract |
| `common/scripted_effects/spain_campaign_effects.txt` | 717 | `spain_coup_check`, 40-weight fizzle branch | `coup_relief` (8) | add → subtract |
| `common/scripted_effects/spain_campaign_effects.txt` | 731 | `spain_coup_outcome_failed` | `coup_relief_large` (15) | add → subtract |
| `common/national_focus/spain_republic.txt` | 611 | `SPR3_public_order` | `coup_relief` (8) | add → subtract |
| `common/national_focus/spain_republic.txt` | 1003 | `SPR3_amnesty_1931` | `coup_relief_large` (15) | add → subtract |
| `common/national_focus/spain_republic_postwar.txt` | 444 | `SPR4_political_police` | `coup_relief_large` (15) | add → subtract |
| `common/national_focus/spain_rivera.txt` | 291 | `SPR2_army_reorganisation` | `coup_relief` (8) | add → subtract |
| `common/national_focus/spain_rivera.txt` | 743 | `SPR2_somaten` | `coup_relief` (8) | add → subtract |

`git diff --stat` over the six source files: **6 files changed, 13 insertions(+), 13 deletions(−)**.
Nothing else in any owned file changed, and the two new files are added separately.

## Round 2 — the corrected army-budget tooltip

QA rejected round 1 on one item and was right to. `spain_bill_concede_army` went from a net **+11**
(+8 added relief, +3 `coup_gain`) to a net **−5** (−8 subtracted relief, +3 `coup_gain`), which
inverted the only visible description of the option that runs it. Residual 4 of this document then
denied that any such string existed, which would have let Director integrate a mechanic whose only
visible cost description states the opposite of its effect.

The Director authorised the correction itself and expanded this card by that one path (nine owned
paths in total): rather than ship knowingly inverted player text, the string now states the truth
and keeps its key, its colour codes and its barracks suspicion.

| | `spain_bills.4.b.tt`, `localisation/english/spain_cortes_bills_l_english.yml:67` |
| --- | --- |
| before | `§YThe credits pass with a commission of enquiry attached.§! The army is paid and insulted at once: coup pressure rises instead of falling, and the republican benches lose ground with the officers' friends.` |
| after | `§YThe credits pass with a commission of enquiry attached.§! The army is paid and insulted at once: coup pressure falls, though not as far as a clean vote would have taken it, and the barracks keep the insult. The republican benches lose ground with the officers' friends.` |

Every clause is true of the shipped code: the meter falls on net (−5), it falls less than the clean
pass (−8) that option 4.a delivers, the barracks keep their grievance (the option still pays and
insults at once), and the republicans do lose ground (`bill_concession_shift` −3 against the
liberals' +2). The key, the option names, the `§Y`/`§!` codes, every other key in the file, the BOM
and the CRLF endings are untouched — `git diff` on that file is **1 insertion, 1 deletion**.

The event option was traced rather than assumed: `events/spain_cortes_bills.txt` option
`spain_bills.4.b` carries `custom_effect_tooltip = spain_bills.4.b.tt` and calls
`spain_bill_concede_army`; `spain_bill_credit_government` and `spain_cortes_recount` write no coup
pressure, so nothing offsets the −5. The other three options were checked too: 4.a says "falls"
(−8), 4.c says "falls less" (−4) and 4.e says "grows" (no direct write; the growth reachable only
through the minority-government strain helper, see residual 6).

## Net deltas, computed by the test from the constants

| Scope | Own lines | With loyalty helper resolved |
| --- | --- | --- |
| `SPR_garrison_the_cities` | −15 | −15 |
| `SPR_amnesty_for_the_juntas` | −8 | −16 (`spain_loyalty_gain_small`) |
| `SPR_secure_the_garrisons` | −15 | −12 (`spain_loyalty_loss_small` pays +3) |
| `spain_bill_pass_army` | −8 | −23 (`spain_loyalty_gain`) |
| `spain_bill_concede_army` | **−5** (relief 8 less `coup_gain` 3) | −20 |
| `spain_bill_water_army` | **−4** | −12 (`spain_loyalty_gain_small`) |
| `spain_coup_check` fizzle branch | −8 (block total 0: two legacy +4 adds offset it) | −8 |
| `spain_coup_outcome_failed` | −15 | −15 |
| `SPR3_public_order` | −8 | −8 |
| `SPR3_amnesty_1931` | −15 | −15 |
| `SPR4_political_police` | −15 | −15 |
| `SPR2_army_reorganisation` | −8 | −23 (`spain_loyalty_gain`) |
| `SPR2_somaten` | −8 | −8 |

`spain_bill_concede_army` now nets −5 on its own lines, matching its own comment ("the barracks
are paid and suspicious at the same time"): relief subtracted, `coup_gain` still added.
`spain_coup_outcome_dictatorship` is untouched — `set_variable = { var = spain_coup_pressure value = 0 }`
still the only write.

## Test added

`.tools/tests/test_spain_coup_relief_sign.py` (new, **127 checks** after the round-2 extension):

- resolves the relief constants from `common/script_constants/spain_campaign.txt` and asserts the
  set is exactly `coup_relief` 8 / `coup_relief_large` 15 / `bill_coup_relief_half` 4 — a renamed
  or added relief constant fails;
- locates each of the thirteen scopes in the shipped file, requires exactly one pressure write
  reading a relief constant, asserts it is `subtract_from_variable`, reads the constant the site
  named, and equals that constant's magnitude;
- asserts no scope in any of the six files adds a relief constant, and that every relief write in
  them is a subtraction;
- asserts every atomic site's expanded delta is negative, concede = −5 and water = −4 on their own
  lines, and that the fizzle sits in the `40` branch of `spain_coup_check` and never in `60`;
- asserts the deliberate raisers survive: `spain_loyalty_loss_small` +3, `spain_loyalty_loss` +6,
  `spain_loyalty_loss_large` +6, `SPR1_juntas_de_defensa` +9, `SPR1_the_coup_that_waits` +12 (read
  from the unowned Restoration tree), and the dictatorship reset;
- **round 2, "bill text" area (27 checks):** reads event `spain_bills.4` from
  `events/spain_cortes_bills.txt`, resolves each option's `custom_effect_tooltip` in
  `localisation/english/spain_cortes_bills_l_english.yml`, and requires the claim in the text to
  agree with the sign of the effect that option actually runs — 4.a "falls" against −8, 4.b "falls"
  against −5, 4.c "falls" against −4, 4.e "grows" against the conditional minority-strain path
  (its own lines write nothing, which the area asserts). It also asserts the corrected text carries
  no `rises instead of falling`, keeps the barracks suspicion, and that **only** that one key
  differs from the pre-repair text — every other key in the file must be byte-identical to
  `62676fadc`, so a wider localisation edit fails;
- negative controls: the pre-repair tree `62676fadc`, an additive-everywhere in-memory copy, a
  single-line flip back to `add_to_variable` at each of the thirteen sites, a renamed `coup_relief`,
  the pre-repair bill text, and a copy with the corrected tooltip key deleted.

Result: `python .tools/tests/test_spain_coup_relief_sign.py` → **127 checks, 0 failures**, exit 0.
Same with `--detail`, which also prints every scope's direct and expanded delta and each bill
option's claimed direction. Area split: constants 2, sites 66, no additive relief 2, raisers 5,
reset 2, bill text 27, plus 23 negative-control checks.

Mutant figures from `--detail`:

| Mutant | Result |
| --- | --- |
| pre-repair tree `62676fadc` | 35 site failures, every one of the 13 scopes named (e.g. `SPR_garrison_the_cities … line 132: add_to_variable`); additive-relief area fails; constants, raisers and reset pass on both trees, proving the repair is what the test discriminates |
| additive everywhere | 39 site failures, 2 additive findings |
| single-site flip back | 13 of 13 sites rejected by name |
| `coup_relief` renamed | 4 site failures, 2 constant failures |
| pre-repair bill text (only the localisation reverted) | 5 text failures, e.g. `spain_bills.4.b says the coup pressure falls — got 'rise', expected 'fall'` |
| corrected tooltip key deleted | 5 text failures, e.g. `spain_bills.4.b tooltip resolves — key 'spain_bills.4.b.tt'` |

## Regressions

| Suite | Result |
| --- | --- |
| `test_spain_restoration_loyalty.py` | 146 checks, 0 failures |
| `test_spain_cortes_recount.py` | 215 checks, 0 failures |
| `test_spain_cortes_runtime.py` | 113 checks, 0 failures |
| `test_spain_cortes_postwar_bills.py` | 227 checks, 0 failures |
| `tools/check_spain_parties.py` | registry 6 files, 17 decisions, 49 keys, no dangling references, exit 0 |

All five match the baselines the Director set for this card.

## MCP evidence

`hoi4.reference_context` (surface `general`, question "subtract_from_variable variable write sign"):
offline wiki `Data structures` heading `subtract_from_variable` line 569 and `Effects` line 710,
installed `effects_documentation.md` lines 8210-8218 — `subtract_from_variable = { var = … value = … }`
is the documented negative write; `omittedSources: []`, `missing: []`.

`hoi4.reference_context` (surface `localisation`, question "custom_effect_tooltip localisation key
formatting colour codes") for the round-2 text: installed `loc_formatter_documentation.md` line 35,
`script_concept_documentation.md` line 174 (`custom_effect_tooltip` takes a standard loc key), and
offline wiki `Effects` line 4582 (`custom_effect_tooltip = my_localisation_key` puts an arbitrary
paragraph in the effect tooltip). `omittedSources: []`, `missing: []`, `coverage.game_doc` and
`coverage.wiki` both included, `script_doc` unavailable. So the corrected key is still the
documented form for the tooltip that carries it.

`hoi4.script_validate path=` before and after, identical in both passes (and identical again in the
round-2 re-run, since no script file changed after the first pass):

| File | Code | Commands | Findings | `checksPerformed` |
| --- | --- | --- | --- | --- |
| `common/decisions/spain_campaign.txt` | `SCRIPT_CHECKED` valid true | 333 | 36 warnings, all pre-existing `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` at line 225+ | syntax, command_kind, declared_scope, player_text, event_popups, known_mistakes |
| `common/scripted_effects/spain_cortes_bills.txt` | `SCRIPT_CHECK_PARTIAL` | 308 | 0 | syntax, command_kind, declared_scope, event_popups, known_mistakes |
| `common/scripted_effects/spain_campaign_effects.txt` | `SCRIPT_CHECK_PARTIAL` | 1210 | 0 | same |
| `common/national_focus/spain_republic.txt` | `SCRIPT_CHECKED` valid true | 379 | 0 | same plus player_text |
| `common/national_focus/spain_republic_postwar.txt` | `SCRIPT_CHECKED` valid true | 335 | 0 | same |
| `common/national_focus/spain_rivera.txt` | `SCRIPT_CHECKED` valid true | 318 | 0 | same |

The two `SCRIPT_CHECK_PARTIAL` codes are the pre-existing unresolved-coverage form for
scripted_effects (`argumentBlocksUnchecked` 143 and 211, all roots unknown-scope); `parametersChecked`
is false everywhere, so this route confirms syntax, command kind and declared scope only — it does
not evaluate the sign of a variable write. **The sign proof is the test and the grep, not this route.**

`hoi4.source_lookup symbol=spain_coup_pressure` before and after: `referenceCount` 65 both times,
`referencesComplete: false` with `unresolvedReferenceCount: 2570` (index incompleteness), identical
reference list including `SPR_garrison_the_cities` decisions:276, `SPR_amnesty_for_the_juntas`:290,
`SPR_secure_the_garrisons`:887, `SPR3_public_order` republic:611, `SPR3_amnesty_1931`:1003,
`SPR4_political_police` postwar:444. The index records `variable_write` **without the operator**, so
it cannot prove the sign; the proof that no additive relief remains is the direct scan
(`grep add_to_variable … coup_relief` → none) plus the test's "no additive relief" area.

`hoi4.focus_inspect` before and after — layout hashes identical, so no focus moved:

| Tree | focusCount | layoutHash before | layoutHash after |
| --- | --- | --- | --- |
| `spain_republic_focus` | 76 | `d9444cc029204c1e3e84352d99b7f5193397f87c0d744929fc8123d26235d8b5` | same |
| `spain_republic_postwar_focus` | 57 | `3b4f79f5f35b0c63259399d43914a1e257620388abad322b554e2578f539b1fe` | same |
| `spain_rivera_focus` | 64 | `8799c24a3cae987a2c6d72872d75a380b3a5a1ad75c31864d03a50b4fe63bf2d` | same |

The postwar tree still reports the two blocking diagnostics it carried at baseline
(`validation.passed: false`, `diagnosticCount` 80) — unchanged by this card and outside its scope.

`hoi4.decision_inspect` was **not** retried: per the admission, the adapter version failure
(`PROBABILITY_GAME_VERSION_UNSUPPORTED`, adapter 1.19.2.0 vs game 1.19.3.0) is exhausted and this
card changed no decision trigger, cost or AI block.

`hoi4.focus_render`: not applicable — no focus file changed shape (layout hashes identical).

## Residuals for the Director (none is a criterion failure)

1. **Compound relief totals.** Criterion 1 keeps every site's constant identical, so the two sites
   that also call a gain helper now relieve more in total than their own line: `spain_bill_pass_army`
   −23 and `SPR2_army_reorganisation` −23 against `coup_open` 10 and `coup_gain` 3. That is the
   arithmetic the card asked for; whether such a swing is the intended balance is a tuning decision
   for a later card, not a sign question, so nothing was changed here.
2. **`spain_coup_check` fizzle branch totals zero on its own block**, because the two
   `coup_legacy_pressure` adds (+4 each) offset the −8 relief when both legacy flags are set. The
   relief write itself is correct and the test asserts it sits in the `40` branch.
3. **Clamp timing.** `spain_clamp_campaign_variables` holds the meter between `loyalty_floor` 0 and
   `coup_cap` 100 but runs from `spain_campaign_weekly`, so a large relief can leave the variable
   negative for up to a week. Nothing reads the raw value for display (no scripted GUI or interface
   file references `spain_coup_pressure`), and `spain_coup_risk` compares against 35, so the
   behaviour is unaffected; only a launch could show whether any panel ever surfaces it.
4. **Player text.** The repair inverted exactly one player-visible string, `spain_bills.4.b.tt`,
   corrected in round 2 under the Director's authorisation (see that section). I checked the other
   twelve sites' text by content and none stated a direction this repair inverted:
   `SPR_garrison_the_cities_desc` already says the action "makes a coup harder to organise";
   `SPR_amnesty_for_the_juntas_desc` says it "removes the grievance"; `SPR_secure_the_garrisons_desc`
   says it "weakens the plot"; and the eight Rivera/Republic/postwar focus descriptions make no coup
   claim at all. A repository-wide scan of English localisation for lines that mention both the coup
   and a direction word returns only these four bill tooltips and one unrelated Persia focus. The
   three other bill tooltips (4.a "falls", 4.c "falls less", 4.e "grows") now agree with the code.
5. **Unverified without a launch**: that the coup meter actually falls on the panel after the army
   budget passes, the failure event's tooltip, the corrected concession tooltip's rendering and line
   length in the event window, and the AI's willingness to spend on relief now that it lowers risk.
   AI weights were deliberately not touched.
6. **`spain_bills.4.e.tt` says "coup pressure grows" and is only conditionally true** — pre-existing
   and not caused by this card. `spain_bill_fail_army` writes no coup pressure; the growth it
   promises reaches the meter only through `spain_bill_penalise_government` →
   `spain_government_strain`, which adds `minority_coup` +3 behind a
   `spain_government_majority = 0` guard. A majority government can withdraw the army budget with no
   coup effect, so the text overstates. The test asserts the reachable path rather than rewording a
   string outside this repair's authorised scope.
7. **Pre-existing BOM outside this card.** `tools/check_script_bom.py` reports a UTF-8 BOM in
   `common/national_focus/spain_restoration.txt`. It is present at `62676fadc` and at HEAD, and that
   file is not owned here, so I did not touch it. Its first line is a comment (`# Overview: …`), so
   the first real token is intact, but the checker flags it and a Director-owned cleanup should strip
   it.

## Rejection record

Round 1 was rejected once on `s15-inverted-tooltip-residual-unreported` (structured ledger count 1,
kept as history and not reset). Round 2 addresses exactly that problem key by correcting the string
and the residual claim; no other criterion changed and no other part of the delivery was reworked.

## Integration note — the new test needs `git add -f`

`.gitignore` line 5 is `.tools/`, so the new test is invisible to a plain `git add` / `git status`
(the existing suites in `.tools/tests/` are already tracked, which is why they survive the ignore
rule). Director must stage it explicitly. The nine owned paths:

```
git add -f .tools/tests/test_spain_coup_relief_sign.py
git add docs/plans/spain/subagent_handoffs/coup_relief_sign.md
git add common/decisions/spain_campaign.txt common/scripted_effects/spain_cortes_bills.txt \
        common/scripted_effects/spain_campaign_effects.txt common/national_focus/spain_republic.txt \
        common/national_focus/spain_republic_postwar.txt common/national_focus/spain_rivera.txt \
        localisation/english/spain_cortes_bills_l_english.yml
```

Nothing was staged by this card. Three `rch_campaign` files and a `tools/__pycache__` entry are dirty
in the same tree from other work; they are not mine and must not travel with this change.

## Not performed

No HOI4 launch, no live playtest, no save inspection, no decision click, no focus completion, no
coup roll, no tooltip render, no commit, no push, no branch or worktree change, no artwork edit, no
vault or skill edit (per admission).
