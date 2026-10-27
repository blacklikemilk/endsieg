# Shanxi warlord campaign, 1916-1935

Slice 1 of the warlord identity design in `docs/specs/qing_1910_1945/warlord_identity_paths.md`, accepted by the Director on 2026-10-27 (C4).
It covers the release of Shanxi out of the Republic, the rise band (S1) and the clique-war band (S2), and the handover to the existing vanilla warlord tree at 1936.1.1.
Slices 2 (Nanjing decade identity) and 3 (the seat bid and reunification payoffs) are not implemented and are not implied by anything here.

## What it does

Shanxi (`SHX`) does not exist before 6 June 1916.
The Republic owns state 615 from 1914, so the province has to be released rather than loaded.
A generic release takes Shanxi's seat, cores it, records the release and recruits Yan Xishan once.
From that day a per-tag daily tick publishes the province's cohesion band and routes it to exactly one band tree.
The player runs the province that survives by not fighting, then the province that prices its neutrality, and is then handed to the vanilla warlord tree untouched.

## Step by step

1. `on_daily_RCH` runs `rch_campaign_tick` (the Republic's own clock, unchanged) and then one guarded release hook: `date > 1916.6.5` and `china_released_shx` unset.
2. `china_release_warlord_shx` checks that the caller still owns state 615 and that Shanxi does not, sets the caller's permanent release flag, enters Shanxi's scope and calls `china_release_warlord_receive`, which gives Shanxi `china_warlord_released` and transfers the seat named by `china_release_seat`. The wrapper then cores 615 and recruits `SHX_yan_xishan` only when Shanxi does not already hold the character.
3. The hook fires `shx_campaign.1` in Shanxi's scope the first time the flag exists.
4. `on_daily_SHX` runs `shx_campaign_tick`, which does nothing until `china_warlord_released` is set.
5. The tick refreshes the cohesion band, then routes: before 1920.7.14 to `shx_rise`, before 1936.1.1 to `shx_wars`, and after 1935.12.31 it runs `shx_hand_over_to_vanilla`, which closes the band flags, removes the cohesion spirits, sets `shx_handover_complete` and loads the tree the 1936 dispatcher in `common/on_actions/endsieg_on_actions.txt` would have loaded for Shanxi: `china_warlord_sea_focus` with `keep_completed` on No Compromise No Surrender, `china_warlord_focus` on Waking the Tiger, `generic_focus` otherwise. The dispatcher itself sits in `on_startup` and cannot fire again in a campaign that began before 1936, which is why the handover lives in the tick.
6. Each band opener sets its band flag, clears the other, loads its tree and marks the layout dirty. A later pass repairs a replaced tree instead of paying the opening twice.
7. The tick asks Beijing for troops once, a month into the rise band, and presents the patron's bill when `warlord_patronage_debt` has reached its cap and the last answer has matured.
8. The player spends cohesion on decisions: the three patrons, the arrears and offices that buy loyalty, and one action per band. The elite action, a clique war, exists only at the devoted band.

## Cohesion

One variable, `warlord_cohesion`, 0 to 100, and four spirits in `common/ideas/shx_campaign.txt`.
The band is derived by triggers, never stored, so the spirit, the decision gates and the AI weights cannot disagree.

| Band | Range | Spirit | What it gates |
| --- | --- | --- | --- |
| 0 | below 30 | `warlord_cohesion_fractious` | `shx_restore_order` |
| 1 | 30 to 54 | `warlord_cohesion_brittle` | `shx_court_the_gentry` |
| 2 | 55 to 79 | `warlord_cohesion_steady` | `shx_host_the_conference` |
| 3 | 80 and above | `warlord_cohesion_devoted` | `shx_declare_clique_war` |

`shx_refresh_mechanics` clamps the meter and re-applies the current band spirit on every pass.
Each branch clears the three spirits it is not holding and adds its own even when it is already held, so a spirit removed by anything else returns on the next daily tick and the family is never left empty.
The decision category shows one readout row per band, visible only while that band is held, so the row that describes the province changes when the band does.
Each readout row prints the meter in its own description, and the category description prints both mechanics: cohesion as `[?warlord_cohesion|0]` of 100 and the debt as `[?warlord_patronage_debt|0]` of 3, in the three English files this slice owns.
A plain variable readout in a `.yml` value needs no scripted localisation, and the suite fails if either mechanic variable stops appearing in player text.
The conference row is the band-2 action, and its requirement is a `custom_trigger_tooltip` with the Beijing flag inside it, as vanilla `AST` and this mod's Qing chapter do, so the line is red until the demand has been answered rather than always shown.

## Patronage

`warlord_patronage_debt` counts favours owed, 0 to 3, and every cohesion purchase and every patron raises it by one.
At the cap the patron's demand event fires, once the previous answer is three months old.
Each answer writes off a single favour. A refusal costs cohesion and leaves a commander who will not march, which is why a grudging commander closes the clique-war decision.
The three patrons are mutually exclusive flags. A second patron is refused for 365 days by a flag-maturity test on `shx_patron_taken`, and refusing all three is a real choice that costs cohesion and gains war support.
Every purchase row carries the debt as a requirement tooltip, so the current number of favours and the bill waiting at the cap are readable on the row that adds one.

## AI

`common/ai_strategy_plans/SHX_warlord.txt` holds each band's focus order, which is where the engine reads a sequence: the treasury, the arsenal and the compact in that order in the rise band, and the broker's table before the expedition question in the clique-war band.
`ai_will_do` and `ai_chance` scores sit on every focus, decision and event option, and the design's thresholds are gates rather than preferences.
Beijing's demand is refused only at or above `ai_beijing_refuse_above`, which is 40: the refuse focus and the demand event's refusal option both score zero below it, so the province pays instead.
A patron is taken only below `ai_patron_below`, which is 35, and that family scores zero at or above it.
The demand's payment option needs 50 political power, so a province that cannot pay answers the demand by refusing whatever its cohesion is. That is a resource constraint on the option, not a scoring preference.
No weight in this slice is a measured probability, because no campaign has been played.

## Interactions

- **The Republic.** The release hook is the only addition to the Republic's package, one guarded call inside its existing daily action. The Republic's own clock is untouched and still runs first.
- **The 1936 dispatcher.** Left byte-identical. This slice loads the same trees the dispatcher would have loaded, in the same DLC order and with `keep_completed`, and then stops: the tick returns early while `shx_handover_complete` is set, the decision category hides itself and the clique-war trigger closes at 1936.1.1.
- **Autonomy.** Shanxi is never placed on an autonomy level. The only warlord level in this checkout is vanilla's `autonomy_sea_warlord_subject`, which forbids declaring war, and this province needs to be able to fight.
- **Other Chinese tags.** The release is a shared body plus one wrapper per tag. The body holds no tag, seat, character token or per-tag flag, so a later slice adds a wrapper of the same shape and one guarded line in the Republic's daily action.
- **Two bands, not three.** 1928 to 1935 stays on the S2 tree because the Nanjing decade is slice 2. That is a deferred slice, not a defect papered over.

## Dynamic effects

### `china_release_warlord_shx` and `china_release_warlord_receive`

- **Why two effects.** `meta_effect` parameters are definition-internal (installed `effects_documentation.md`, "meta_effect"), so a scripted-effect caller cannot pass a tag, seat or character token into a body. The parameterisation therefore travels through a scope and a variable, and each tag's literals sit in its own short wrapper.
- **`china_release_warlord_receive`:**
  - **Scope:** the receiving tag, entered by the wrapper.
  - **Inputs:** `china_release_seat`, a state id variable set in that scope by the wrapper.
  - **Outputs:** `china_warlord_released` on the receiving tag; ownership and control of the seat, via `transfer_state = var:china_release_seat`.
  - **Defaults:** none. The body holds no tag, seat, character token or per-tag flag.
  - **Side effects:** fires nothing and touches no other state.
- **`china_release_warlord_shx`:**
  - **Scope:** the seat's current owner, in country scope. First consumer is `RCH`.
  - **Inputs:** none. The wrapper carries the literals: `china_released_shx`, seat 615, `SHX_yan_xishan`.
  - **Outputs:** the caller's permanent `china_released_shx`, the body's output, `add_state_core = 615`, and one recruited character.
  - **Re-entry:** the caller's flag, the ownership guard and the `has_character` guard each block a second pass on their own.
  - **Example of a later tag:** a wrapper `china_release_warlord_yun` in this file with its own flag, seat and character, plus one guarded line in `on_daily_RCH` calling it. `china_release_warlord_receive` does not change.

### `shx_refresh_mechanics`

- **Scope:** country, Shanxi.
- **Inputs:** `warlord_cohesion`, `warlord_patronage_debt`, both self-initialised on first run.
- **Outputs:** the matching band spirit, clamped variables.
- **Defaults:** cohesion opens at `constant:shx_story.cohesion_opening`, debt at `constant:shx_story.debt_opening`.
- **Side effects:** removes the three non-matching band spirits. Hidden, so callers show a clean tooltip.
- **Example:** every focus that moves cohesion calls it, and the daily tick calls it unconditionally.

### `shx_hand_over_to_vanilla`

- **Scope:** country, Shanxi.
- **Inputs:** the `has_dlc` checks that mirror the startup dispatcher.
- **Outputs:** `shx_handover_complete` (permanent), band flags and pending-demand flag cleared, the four cohesion spirits removed, and one `load_focus_tree` with `keep_completed`.
- **Defaults:** none.
- **Side effects:** marks the layout dirty. The tick returns early while the flag is set, so the province is not asked again.
- **Example:** the tick calls it once, on the first daily pass after 1935.12.31.

## Tuning

Every number a field accepts as a script constant is in `common/script_constants/shx_campaign.txt` and read as `constant:shx_story.*`.
Fields that reject constants keep their value in exactly one place: focus `cost` and decision `cost`/`days_remove` use the file-scoped macros declared at the top of the consuming file, and the two flag-age comparisons use `@patron_maturity_days` and `@demand_maturity_days` declared at the top of `common/scripted_triggers/shx_campaign.txt`. The constants file does not duplicate those values, and the suite fails on a constant nothing reads and on a macro that nothing declares.
No balance claim is made: no campaign has been played.

## Assets

No new artwork, no new `.gfx` file and no icon collection.
Spirits reuse registered Chinese idea sprites, decisions reuse registered vanilla decision icons, and both trees reuse registered focus icons.
The suite checks every `icon = GFX_…` in both trees against the sprite names registered in this mod's `interface/` and in the installed game's `interface/`, so a tree cannot ship an icon that no `.gfx` declares.
`SHX_suiyuan_question` uses `GFX_focus_ww1_pdx_native_shared_gen_state_claims`, a registered claim icon; the sprite it used before (`…en1_r_neutral_trade`) does not exist in either interface folder.

Icons this slice would use if they existed, for a later artwork pass:

- a Shanxi provincial treasury focus icon (wanted at `GFX_focus_SHX_treasury`, no such sprite)
- a Taiyuan arsenal focus icon (`GFX_focus_SHX_arsenal`, no such sprite)
- a broker's table icon for the S2 root (`GFX_focus_SHX_brokers`, no such sprite)

## Future slices

1. **Slice 2:** the Nanjing decade tree from 1928.1.1, the 1930 coalition, the autonomy charter, and the S3 identity that this slice leaves on the S2 tree.
2. **Slice 3:** the seat bid and the reunification payoffs, which need `china_seat_holder`, `china_reunified_by` and `china_warlord_national` to exist first.
3. **Roster:** the remaining clavicles in the design's section 15, each adding a caller to `china_release_warlord`.

## Limitations

- Source and test evidence only. No launch, no save and no panel render, so the province appearing in a 1916 campaign, the readout rows, decision clickability and the 1936 handover stay unverified.
- The war spends its opening cost in cohesion and army experience, and its own tooltip names both amounts. The province keeps whatever it takes on the map. Nothing in this slice reacts to the war ending, so no cohesion is granted for a won war.
- A warlord released by a later wrapper inherits the same handover shape, but each tree's own 1936 load has to name its tag's vanilla tree, because the dispatcher's tag list is not readable from script.
- The band readout prints the meter in the row's description rather than in the row title, because a dynamic decision title needs scripted localisation and a description readout does not.
- `SHX_model_governor` is still dropped by the character override (D1 in the design). This slice does not touch the character file and took a different reward where the trait would have been used.
