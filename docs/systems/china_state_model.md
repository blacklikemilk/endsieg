# China: the global seat, fragmentation-tier and China-proper state model

Built by C5m (`t_6674607a`). Contract: `docs/specs/qing_1910_1945/continuity_1928_1945.md` section 5.

## What the four symbols are

| Symbol | Kind | Single writer | Written at |
|---|---|---|---|
| `global.china_proper_states` | global state-scope array, 62 entries | `china_build_proper_states` | `on_startup` (one call in `common/on_actions/endsieg_on_actions.txt`) |
| `global.china_fragmentation_tier` | global variable, 0–3 | `china_publish_fragmentation_tier` | the freeze site in `rch_succession_settle` (`common/scripted_effects/rch_campaign.txt`) |
| `global.china_seat_holder` | global country variable | `china_set_seat_holder = { COUNTRY = TAG }` | only from `china_record_reunifier` in this card; a later seat transfer calls it with the new holder |
| `global.china_reunified_by` | global country variable | `china_record_reunifier = { COUNTRY = TAG }` | `china_test_reunification`, and never cleared |

Writers live in `common/scripted_effects/china_state_model.txt`; nothing else writes these symbols.
Readers live in `common/scripted_triggers/china_state_model.txt` and write nothing:
`china_has_reunified`, `china_seat_is_held`, `china_fragmentation_tier_is_at_least = { TIER = n }` and
`china_holds_all_proper_states = { COUNTRY = TAG }`.

Tuning lives in `common/script_constants/china_story.txt` (`china_story.tier_floor = 0`, `tier_ceiling = 3`, `proper_state_count = 62`).
The clamp bounds are those constants read directly — `clamp_temp_variable = { var = china_published_tier min = constant:china_story.tier_floor max = constant:china_story.tier_ceiling }`, shipped in that form.
No source in this checkout or in vanilla shows a `constant:` operand inside `clamp_temp_variable`: the repository's clamp precedent is `clamp_variable`, a different effect-type (`common/scripted_effects/iran_campaign.txt:13`, `min = constant:iran_story.authority_floor max = constant:iran_story.authority_cap`), and vanilla's constant in variable arithmetic is a `set_variable` right-hand value (`common/decisions/SIA.txt:419`, `set_variable = { SIA_new_propaganda_campaign_duration = constant:propaganda.SIA.default_propaganda_campaign_duration }`), not a clamp bound.
Both operands are therefore shipped but not engine-tested, and `Live checks nobody has run` carries them as such.
No file macro mirrors them, so the constants file is the only place the two numbers exist, and `.tools/tests/test_china_state_model.py` asserts the packaged operands are the `constant:` tokens rather than literals.

## Engine forms and why they were chosen

- `check_variable = { global.china_proper_states^num > 0 }` is the presence and once-only guard.
  `has_variable` is documented as "checks if a variable exists in a scope" and the array documentation never states that it covers arrays, while `array^num` is documented as the element count and vanilla uses it as a guard (`common/on_actions/10_toa_on_actions.txt:43`, `common/decisions/GER.txt:16333`).
- The array holds **state scopes** (`283 = { add_to_array = { global.china_proper_states = THIS } }`), because the holding test walks it with `all_of_scopes`. Vanilla fills global arrays with `THIS` inside a state iteration (`common/on_actions/13_goe_on_actions.txt:146`, `common/on_actions/00_on_actions.txt:72,115,146`). An array of bare ids could not be scoped into, and `is_in_array = { value = THIS }` against ids has no precedent.
- `all_of_scopes` scopes into each element (wiki `Data structures`, array triggers), so the holding test costs 62 checks and needs no `all_state` world sweep. The exact shape used here is vanilla's: `all_of_scopes = { array = global.PRC_starting_PRC_core_states is_owned_and_controlled_by = PRC }` (`common/achievements.txt:7283-7286`), and the same block with `array = AFG.AFG_himalaya_states_array` / `is_controlled_by = AFG` at `common/achievements.txt:6854-6857`.
- `clamp_temp_variable = { var = X min = <n> max = <n> }` is vanilla's block form, and the model writes that block over four lines.
  The one-line examples carry literal bounds and often only `max` (`common/occupation_laws/occupation_laws.txt:391` `max = 8`, `:433` `max = 40`); the multiline examples are literal as well (`common/operations/00_operations.txt:374-377` `min = 24`, `:1227-1230` `min = 0.1`).
  A line break inside the block is formatting: it is not a different engine form and it does not restrict which operands the effect accepts, so the model's multiline layout is the same effect vanilla writes.
  Its operands are the `china_story` constants. `constant:` inside `clamp_variable` (`common/scripted_effects/iran_campaign.txt:13`) is an analogous effect and does not establish support in this one, and an operand that no sampled source happens to show is not thereby an invalid one.
  The installed documentation gives the keys as `var`, `min` and `max` taking "two a values or another variables" (`documentation/effects_documentation.md:2681-2693`), which describes literals and variables and neither confirms nor forbids a constant token.
- The two country-valued symbols are written with vanilla's **short** global assignment, `set_variable = { global.china_seat_holder = GER }`: `common/decisions/POR.txt:2137` (`set_variable = { global.POR_iberian_summit_target = GER }`), `common/national_focus/austria.txt:4734` (`set_variable = { global.AH_originator_country = ROOT }`). The long `set_variable = { var = global.x value = y }` form occurs nowhere in vanilla (`grep -rn "set_variable = { var = global\."` → 0 hits), so a write in that shape could leave `china_seat_holder` and `china_reunified_by` silently unset; the test rejects it, and mutant M9 restores it to prove the test bites.
- The tier copy assigns another variable through the same short form, `set_variable = { global.china_fragmentation_tier = var:china_published_tier }`. `set_variable` is documented as setting a variable "to a value, another variable, or a math expression", and `= var:<name>` as a right-hand operand is what vanilla writes on temp variables (`common/raids/land_infiltration_custom.txt:260`).

## China proper: the rule and the table

Rule: a state belongs to China proper when its **effective** `history/states` entry (the mod's file where one exists, otherwise the game's) carries `add_core_of = CHI` inside its `history` block, outside every dated block.
Measured in this checkout: 62 such states, 0 dated `add_core_of = CHI` / `remove_core_of = CHI` blocks in either tree, so the set is identical at every bookmark and is not an ownership snapshot.
It includes the treaty ports and leases held by other powers in 1936 — Hong Kong 326, Macau 729, Guangzhouwan 728, Taiwan 524, Qingdao 743, Dalian 745, Weihaiwei 1040 — and the Manchurian and frontier states.

```
283 287 325 326 328 524 591 592 593 594 595 596 597 598 599 600 601 602 603 604 605 606
607 608 609 610 611 612 613 614 615 616 617 618 619 620 621 622 714 715 716 717 728 729
743 744 745 746 747 748 749 750 751 752 753 754 755 756 759 760 761 1040
```

`.tools/tests/test_china_state_model.py` re-derives that list from source by the same rule and asserts the literal table equals the derivation, the count equals `china_story.proper_state_count`, and the seven states whose `history` brace opens on the next line (596 Zhejiang, 600 Jiangxi, 605 Sichuan, 620 China 17, 743 Qingdao, 745 Dalian, 746 Ordos) are present.
That last pin exists because the first version of both the list and the derivation accepted only `history = {` on one line and therefore dropped those seven while still reporting 55 == 55; the test's control `one-line-history parser loses states` proves the difference (55 derived vs 62 literal).

## Reunification

`china_test_reunification` is called from the existing `on_daily_RCH` in `common/on_actions/rch_campaign.txt`, and nowhere else; no new `on_daily_<TAG>` and no world-iterating hook was added.
Order of work: the array must exist and no reunifier may be recorded (two variable checks a day once resolved), then a bounded list of Chinese campaign countries — QIN, RCH, CHI, PRC, SHX, SIK, YUN, GXC, XSM, GDC, XIC, SND, KHM, NXM, GSM, SIC, KUM, HBC, RNG — each tested with one pass over the 62-state array. Never `every_country`.
A tag outside that list cannot be recorded as reunifier; a country released mid-campaign, or a tag the design later promotes to a China candidate, needs the list extended in the effect (and its own test fixture).

The hook's reach is the Republic's: the offline wiki's on-actions table defines `on_daily_TAG` as "triggers each day for the specified country only" and records that it "only runs the effects if the country exists" (`paradox_wiki/On actions - Hearts of Iron 4 Wiki.md:97`).
So the test runs on every day the Republic exists as a country and stops if the Republic is removed from the game state before any Chinese tag controls all of China proper.
Capitulation is not covered by that sentence and this card draws no conclusion from it; the only reachability condition asserted here is country existence.
The gap is deliberate and is not this card's to close: the hook was fixed by the card and by Director's ruling, so a general `on_daily` guard or a call from the effect that removes the Republic belongs to the follow-up card recorded below.

## What is still unbuilt on top of this

- No continuity row, no handover event, no alternate-unifier row, no seat spirit and no player-facing surface reads these symbols yet; this card is the gate, not gameplay, and adds no localisation key.
- The seat is only written by the reunifier path. A peacetime transfer of the seat between Chinese tags (a warlord absorbing another, a dynasty falling) still has to call `china_set_seat_holder` from the effect that performs the transfer.
- `china_seat_is_held`, `china_has_reunified` and `china_fragmentation_tier_is_at_least` have no callers in the mod yet. They are written for the follow-up card and are covered by the model test only.
- **Hook reachability.** `china_test_reunification` runs only while the Republic exists (see `Reunification`). A design that must record a reunification after the Republic is gone needs a different caller: a general `on_daily` block, or a call from the resolution effect of whatever removes the Republic. That is a Director design decision with its own performance and ownership review, not a change this model may make; the follow-up continuity card owns it, and `docs/systems/china_state_model.md` is where the decision must be recorded.
- **The call-site file.** The single tier-writer call lives in `common/scripted_effects/rch_campaign.txt`. That file carried a leading UTF-8 BOM until the correction recorded in `docs/systems/rch_campaign.md`; the 15:09 load rejected the file and its callers logged `Unknown effect-type: rch_*`, which is why a BOM is now a tested property of that file rather than an observation. What that log says about the file, it does not say about this model: it predates the model's first run and no load has executed the model.

## Live checks nobody has run

- Whether the engine accepts `check_variable = { global.china_proper_states^num > 0 }` as an array-presence guard and `all_of_scopes` over a global array of state scopes — both are documented and have vanilla precedent, but no load has been done.
- Whether `clamp_temp_variable` accepts the two `constant:` operands. The effect-type, the block shape, the multiline layout and the `min`/`max` keys all have vanilla precedent; the constant operands do not, and nothing here establishes that the engine resolves `constant:` inside this effect instead of failing to parse the bound. The test asserts the packaged token text, which is a statement about the script and not about the engine.
- Whether `on_startup` runs before `on_daily_RCH` on the first day, as assumed by the presence guard.
- Whether a save can hold the game state without the initialized array. The offline table defines `on_startup` as running "at the first day of a new game" and records that it "doesn't work with save loading" (`paradox_wiki/On actions - Hearts of Iron 4 Wiki.md:95`), so a load never re-runs the initializer and what a load sees depends on the saved state; the array is a global variable written on startup, so the consequence concerns only a save whose state lacks it. In that case the presence guard in `china_test_reunification` can never pass and the model stays inert for the rest of that campaign. No migration, extra initializer or new caller was added, so the gap is unmitigated and unverified.
- Whether the 62 states resolve, and whether `is_controlled_by` is the right reading of "holds" for the design (control, not ownership).

## No magic numbers, no localisation

Every number in the model is either a `china_story` constant or a historical state id, which is content rather than tuning.
No localisation key, sprite, event picture, focus id or artwork was added or changed.
