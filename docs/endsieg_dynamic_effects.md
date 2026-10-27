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
