# Endsieg dynamic scripted effects

Reusable `common/scripted_effects` helpers whose behaviour depends on the caller's country state rather than on a fixed payload.

Each entry records purpose, scope, inputs, outputs, guards, side effects and one usage example.
Every helper here is safe to call more than once with the same state unless the entry says otherwise.

## iran_recompute_leverage

- **Purpose:** publishes Iran's foreign dependence from the patron influence the country is actually under, plus the credit it has taken.
- **File:** `common/scripted_effects/iran_campaign.txt`.
- **Scope:** country scope, Iran only. Not used in state, character or global scope.
- **Reads:** `iran_british_influence`, `iran_northern_influence`, `iran_german_influence`, `iran_leverage_baseline`, `iran_influence_baseline`, `iran_leverage_debt`.
- **Writes:** `iran_leverage_landed`, `iran_foreign_leverage`, and the debt clamp on `iran_leverage_debt`.
- **Formula:** `landed = clamp(baseline + (influence sum - influence baseline) * constant:iran_story.leverage_derivation_weight, 0, 100)`, then `aggregate = clamp(landed + debt, 0, 100)`.
- **Guards:** clamps each influence to `authority_floor`–`authority_cap` before deriving, so a concession taken at the cap cannot manufacture dependence the patron did not gain.
- **Side effects:** calls `iran_leverage_baseline_init`, which captures the two baselines and clears the debt the first time it runs and does nothing afterwards. It does not toggle `iran_foreign_dependence`: that idea is added and removed only inside `iran_refresh_mechanics`. It never calls `iran_refresh_mechanics`, so a caller cannot recurse through the spirit refresh.
- **Cadence:** call after any influence change, after the monthly influence drift, and from `iran_refresh_mechanics` before the dependence spirit is tested.
Any body that writes `iran_leverage_debt` calls `iran_refresh_mechanics_hidden` (decisions) or wraps `iran_refresh_mechanics` in a `hidden_effect` (focus rewards) in the same block, so a debt change that crosses `leverage_dependency` moves the spirit with it.
- **Example:**

```
iran_concede_british_small = {
	hidden_effect = {
		add_to_variable = { iran_british_influence = constant:iran_story.concede_small_influence }
		clamp_variable = { var = iran_british_influence min = 0 max = 100 }
		iran_recompute_leverage = yes
	}
}
```

## iran_leverage_baseline_init

- **Purpose:** captures the one-time opening dependence and influence sum that later derivation is measured against.
- **File:** `common/scripted_effects/iran_campaign.txt`.
- **Scope:** country scope, Iran only.
- **Reads:** `iran_foreign_leverage`, the three patron influences, `constant:iran_story.leverage_debt_opening`.
- **Writes:** `iran_leverage_baseline`, `iran_influence_baseline`, `iran_leverage_debt`, and sets `iran_leverage_baselined`.
- **Guards:** does nothing once `iran_leverage_baselined` is set, so a chapter transition never re-bases a running campaign.
- **Side effects:** none beyond the writes above.
- **Cadence:** called from `iran_initialize_campaign` after the chapter's opening values exist, and from `iran_recompute_leverage` for a country that is already active without baselines.
- **Example:** `iran_leverage_baseline_init = yes` at the end of the opening block in `iran_initialize_campaign`, before `iran_refresh_mechanics`.

## china_release_warlord_receive

- **Purpose:** the shared body that turns a state held by the Republic into an independent Chinese warlord state, once, without carrying any tag's literals.
- **File:** `common/scripted_effects/china_warlord_release.txt`.
- **Scope:** the receiving tag, in country scope, entered by a per-tag wrapper such as `china_release_warlord_shx`.
- **Reads:** `china_release_seat` (state id variable, set by the wrapper in the receiving tag's scope); the seat's current owner and the receiving tag's `china_warlord_released` flag.
- **Writes:** state ownership and control of `var:china_release_seat`, the receiving tag's `china_warlord_released`.
- **Guards:** returns unless the seat is RCH-owned and the receiving tag does not already own it, and returns if `china_warlord_released` is already set, so a second pass does nothing.
- **Side effects:** none beyond the transfer; it fires no event and touches no other state. Callers wrap their own notification event.
- **Cadence:** one guarded call per tag from the Republic's existing daily action, never from a periodic world hook.
- **Example:** `china_release_warlord_shx = yes` inside the `date > 1916.6.5` guard in `on_daily_RCH`.

## china_release_warlord_shx

- **Purpose:** the Shanxi wrapper that supplies the literals the shared body cannot receive as parameters.
- **File:** `common/scripted_effects/china_warlord_release.txt`.
- **Scope:** the seat's current owner, in country scope. First consumer is `RCH`.
- **Reads:** the caller's `china_released_shx` and the state-615 owner.
- **Writes:** `china_released_shx` on the caller, the shared body's outputs, `add_state_core = 615`, and one recruitment of `SHX_yan_xishan` under `NOT = { has_character = SHX_yan_xishan }`.
- **Guards:** the caller's flag, the body's ownership test and the `has_character` test each block a second release on their own.
- **Side effects:** recruits a character into the new tag; it does not touch the Shanxi character file or its traits.
- **Cadence:** called once per campaign from `on_daily_RCH`; later tags add their own wrapper of the same shape.
- **Example:** a later `china_release_warlord_yun` wrapper with its own flag, seat and character, plus one guarded line in the same daily action; the shared body does not change.

## shx_refresh_mechanics

- **Purpose:** re-applies Shanxi's current cohesion band spirit and clamps the two mechanic variables.
- **File:** `common/scripted_effects/shx_campaign.txt`.
- **Scope:** country, Shanxi only.
- **Reads:** `warlord_cohesion`, `warlord_patronage_debt`.
- **Writes:** the matching band spirit and the two clamped variables; initialises both variables on first run from `constant:shx_story.cohesion_opening` and `constant:shx_story.debt_opening`.
- **Guards:** removes only the three non-matching band spirits, so a refresh never deletes the family and never leaves the province without a tier.
- **Side effects:** hidden, so callers show a clean tooltip. Every focus that moves cohesion calls it, and the daily tick calls it unconditionally.
- **Cadence:** daily and after every cohesion or debt change.
- **Example:** `hidden_effect = { shx_refresh_mechanics = yes }` inside a focus reward that adds cohesion.

## shx_hand_over_to_vanilla

- **Purpose:** hands Shanxi to the existing 1936 warlord tree in the same DLC order the startup dispatcher uses, then stops the mod's own band logic.
- **File:** `common/scripted_effects/shx_campaign.txt`.
- **Scope:** country, Shanxi only.
- **Reads:** the `has_dlc` checks for No Compromise, No Surrender and Waking the Tiger.
- **Writes:** `shx_handover_complete` (permanent), clears all three band flags, the pending-demand flag and the band's one-shot records (`shx_nanjing_squeeze_seen`, `shx_concession_granted`, `shx_coalition_lost`), removes the four cohesion spirits and `shx_japanese_concession`, and issues one `load_focus_tree` with `keep_completed`. Leaves `shx_autonomy_charter` standing as the province's own record.
- **Guards:** the tick returns early while `shx_handover_complete` is set, so the province is not handed over twice. The northern concession is removed here because its only exit, `shx_buy_back_the_concession`, sits in the band panel this pass closes: a spirit left behind would be a penalty no row could lift.
- **Side effects:** marks the focus layout dirty on the handover day.
- **Cadence:** once, on the first daily pass after 1935.12.31.
- **Example:** called from `shx_campaign_tick`, not from a focus reward.

## shx_open_nanjing

- **Purpose:** opens Shanxi's third band, the Nanjing decade, and retires the two earlier band flags.
- **File:** `common/scripted_effects/shx_campaign.txt`.
- **Scope:** country, Shanxi only.
- **Reads:** nothing.
- **Writes:** `shx_band_nanjing`, clears `shx_band_rise` and `shx_band_wars`, one `load_focus_tree` of `shx_nanjing` with `keep_completed`, and the layout-dirty mark.
- **Guards:** the caller tests `NOT = { has_country_flag = shx_band_nanjing }` before calling it, and the tick repairs a replaced tree separately with `has_focus_tree`, so a second daily pass cannot open the band twice or reload the tree.
- **Side effects:** none beyond the flags and the one load.
- **Cadence:** once per campaign, on the first daily pass at or after 1928.1.1.
- **Example:** `shx_open_nanjing = yes` inside the band-3 `if` of `shx_campaign_tick`.

## shx_nanjing_demand

- **Purpose:** asks the northern-squeeze question once, inside the Nanjing decade.
- **File:** `common/scripted_effects/shx_campaign.txt`.
- **Scope:** country, Shanxi only.
- **Reads:** `shx_nanjing_squeeze_due`, which needs `shx_band_nanjing` older than `@squeeze_maturity_days` and no `shx_nanjing_squeeze_seen`.
- **Writes:** `shx_nanjing_squeeze_seen` and `shx_campaign.4`, delayed one day.
- **Guards:** the seen flag is written before the event is queued, so the next daily pass cannot ask again while the player is still reading the first question; the trigger also requires the band flag, so the question cannot arrive outside its band.
- **Side effects:** none beyond the flag and the queued event.
- **Cadence:** daily from the band-3 branch of `shx_campaign_tick`, effective once.
- **Example:** `shx_nanjing_demand = yes` at the end of the band-3 branch, beside `shx_beijing_demand` and `shx_patronage_demand`.

## china_build_proper_states

- Purpose: build the global state array `global.china_proper_states` once per campaign, holding the 62 states of China proper as state scopes.
- Scope: any (called from `on_startup` in `common/on_actions/endsieg_on_actions.txt`).
- Inputs: none. The ids are literal in the effect body, because China proper is a historical set, not a current-ownership query.
- Outputs: `global.china_proper_states` (array of state scopes); no other state changes.
- Defaults: no parameters. Re-running is a no-op because the guard refuses when `global.china_proper_states^num > 0`.
- Side effects: none outside the array. A second call changes nothing, including after a reload.
- Example: `china_build_proper_states = yes`

## china_publish_fragmentation_tier

- Purpose: publish the frozen Republic succession tier as the global `china_fragmentation_tier`, the only value any continuity reader may test.
- Scope: any country scope (called once from the freeze site in `rch_succession_settle`).
- Inputs: country variable `rch_succession_final_tier`, set one line earlier by the same effect.
- Outputs: `global.china_fragmentation_tier`, clamped to `constant:china_story.tier_floor`..`constant:china_story.tier_ceiling` (0..3; the constants themselves, no mirrored macro).
- Defaults: when `rch_succession_final_tier` does not exist the effect does nothing at all, so a campaign that has not resolved has no tier rather than a zero tier.
- Side effects: none. It never reads the live score, so a later day cannot rewrite the published value.
- Example: `china_publish_fragmentation_tier = yes`

## china_set_seat_holder

- Purpose: write the single seat symbol, replacing the previous holder on every transfer.
- Scope: any; the holder is passed explicitly, so the effect is correct from any scope.
- Inputs: `$COUNTRY$`, a country tag.
- Outputs: `global.china_seat_holder`.
- Defaults: none. No parameter means a parse error rather than a silent no-op.
- Side effects: replaces the previous holder, so no stale seat survives a transfer. Never called from a reader.
- Example: `china_set_seat_holder = { COUNTRY = QIN }`

## china_record_reunifier

- Purpose: record the first reunifier permanently and give it the seat.
- Scope: any country scope.
- Inputs: `$COUNTRY$`, a country tag.
- Outputs: `global.china_reunified_by` and, through `china_set_seat_holder`, `global.china_seat_holder`.
- Defaults: none. The guard refuses every write once `global.china_reunified_by` exists, so a second unifier cannot take the seat from the first.
- Side effects: both globals are permanent; nothing in this card clears them.
- Example: `china_record_reunifier = { COUNTRY = CHI }`

## china_test_reunification

- Purpose: test whether one Chinese campaign country holds every China-proper state, and record it as the reunifier if so.
- Scope: any country scope; called from the existing `on_daily_RCH` and nowhere else.
- Inputs: `global.china_proper_states`, `global.china_reunified_by`, and per-state control.
- Outputs: the two globals above when a candidate holds all 62 states; nothing otherwise.
- Defaults: two guards first (array present, no reunifier yet), then a bounded candidate list of 19 Chinese tags. No `every_country`, no world sweep, no new tag hook.
- Side effects: only on a successful match, and then once per campaign. A resolved campaign pays two variable checks a day.
- Example: `china_test_reunification = yes`
