# Spain, 1910-1945

## What this is

Spain plays as a sequence of chapters rather than one frozen tree.
Four new chapter trees cover the periods that had no Spanish content at all, and the existing La Résistance civil-war tree remains the war chapter.
Six scripted systems run underneath all of them, so a decision taken in 1912 still matters in 1944.

| Chapter | Tree | Window | Opened by |
| --- | --- | --- | --- |
| I Restoration | `spain_restoration_focus` | 1910 to 1923 | `spain_open_restoration_chapter` |
| II Dictatorship | `spain_rivera_focus` | 1923 to 1930 | `spain_open_rivera_chapter` |
| III Republic | `spain_republic_focus` | 1931 to 1936 | `spain_open_republic_chapter` |
| IV Civil War | `spanish_focus` (existing vanilla tree) | 1936 to 1939 | `spain_open_civil_war_chapter` |
| V Nationalist Spain | `spanish_focus` (existing) | 1939 to 1945 | `spain_open_postwar_chapter` |
| V Republican Spain | `spain_republic_postwar_focus` | 1939 to 1945 | `spain_open_republican_postwar_chapter` |

## What is reused, and what is new

Reused unchanged: `common/national_focus/spain.txt` (281 focuses), `common/decisions/SPR.txt` (178 decisions in 11 categories), `events/LAR_Spain.txt`, `events/LAR_NewsEvents.txt`, `common/ideas/spain_nationalist.txt`, `common/ideas/spain_republic.txt`, `common/scripted_effects/SPR_scripted_effects.txt`, `common/scripted_triggers/SPR_scripted_triggers.txt`, `05_lar_on_actions.txt`, and every SPA/SPB/SPC/SPD civil-war tag.
The Nationalist, Carlist, Falangist, anarchist and communist wartime paths therefore keep working exactly as before, including vanilla's `SPA_garrison_control` mechanic.

New: four chapter trees (284 focuses), six system layers, 38 decisions, 21 events, 46 national spirits, one balance of power, and the campaign state that ties them together.

| Tree | Focuses |
| --- | --- |
| `spain_restoration_focus` | 89 |
| `spain_rivera_focus` | 64 |
| `spain_republic_focus` | 74 |
| `spain_republic_postwar_focus` | 57 |

### Layout
Branches are positioned with `relative_position_id` from their parent, the way the Iran chapter trees do it, so a branch hugs the focus that opens it instead of spreading across a fixed grid.
81 of the 284 focuses are placed that way.
A focus whose reward changes the political state calls `mark_focus_tree_layout_dirty = yes` so newly revealed conditional branches are drawn immediately.
Each tree also carries five navigation shortcuts (politics, crown, economy, army, diplomacy).

### Late starts
A player who begins in 1914, 1916, 1918 or 1936 does not start from an untouched tree.
`spain_restore_past_focuses` completes the focuses the country would plausibly have finished by that date, 78 of them across the three pre-war chapters.
Completion is gated by date, promoted so a focus is never completed before its prerequisites, and emitted in prerequisite order.
A 1918 start therefore enters the war years with the Restoration's political and economic groundwork already done, rather than replaying 1910.

### Startup order
Chapter openers only load the tree, set flags and add the opening spirits.
The balance of power, chapter history and the late-start completions run from `spain_campaign_bootstrap` on the first daily tick, not during `on_startup`.
That keeps engine systems out of the frontend-to-game transition, and it is where the previous crash at scenario start came from.

Touched existing files, narrowly:
- `common/on_actions/endsieg_on_actions.txt`: two added calls, one in the pre-1936 tree-assignment branch, one in the 1936+ branch.
- `common/ai_strategy_plans/SPR_historical_strategy_plan.txt`: a `date > 1935.12.31` gate on all three plans, so the civil-war party line does not steer focus selection in 1910-1935.

## Systems

### The Crown and the Cortes
A native balance of power, `SPR_crown_and_cortes`, defined in `common/bop/SPR_crown_and_cortes.txt`.
Two sides, five ranges, real modifiers in each range, and `on_activate` events at both extremes.
Its decision category (`SPR_crown_and_cortes_category`) is attached to the balance, so it is played from the balance panel.
Values: -1 is royal government, +1 is parliamentary sovereignty, and the deadlock band is -0.25 to +0.25.
Restoration opens at -0.15; the Republic opens at +0.45; the post-war chapters remove the balance entirely.

### The officer corps
`spain_military_loyalty`, 0 to 100, opening at 55.
Three spirits swap automatically at 40 and 70: estranged, restive, loyal.
Loyalty sets `spain_coup_pressure`, and both feed three outcomes: coup attempts, the number of garrisons that defect at the civil-war outbreak, and whether the 1936 rising is treated as a plot or a war.

### Coups
`spain_coup_check` runs weekly. When loyalty is below 40 and pressure is at least 35, a weighted draw fires `spain_campaign.40`.
Three answers: resist, concede, or buy the ringleaders.
Resisting succeeds or fails on loyalty; success opens the military chapter through `spain_campaign.41`.

### The Rif War
`SPR_rif_war` holds four operations, each with a duration, a modifier while it runs, and a real cost in equipment or manpower.
`spain_rif_commitment` records the campaign, and the 1925 landing and the pacification are focus-driven milestones.

### Regional control in the civil war
`spain_refresh_regional_control` tests seven regions against `controls_state` and grants or removes a holding spirit: Catalonia, the Cantabrian north, Aragon, the Levante, Andalusia, the Meseta and the African protectorate.
It runs weekly while `spanish_civil_war` is set, and the flags survive into the post-war chapters.

### The Nationalist faction struggle
Four influences: `spain_falange`, `spain_carlists`, `spain_monarchists`, `spain_army_faction`.
`spain_nationalist_tension` rises with the number of factions above 50 and with the war itself.
High tension fires `spain_campaign.50`; `spain_faction_resolve_regime` then applies one of four regime spirits, and `SPR_unify_the_movement` lets the player settle it deliberately.

### Wartime diplomacy
`spain_axis_leverage` and `spain_allied_leverage` move through negotiation, wolfram contracts, the Blue Division, closing the Pyrenees and a declaration of armed neutrality.
Alignment is expressed through three mutually exclusive spirits rather than a hidden number.

### National development
`spain_industry`, `spain_agriculture`, `spain_infrastructure`, `spain_education`, each 0 to 12.
Three tier spirits per sector swap at 3, 6 and 9, and the variables are never reset, so development persists across chapter changes and the civil war.

### Reconstruction
`spain_reconstruction` plus `spain_civil_war_reconstruction` (a real debuff: -15% factory output, +10% consumer goods, -20% construction speed, -10% stability).
The `SPR_reconstruction` decisions raise the value; at 100 the debuff is replaced by `spain_reconstruction_advanced`.

## Flow

1. `on_startup` calls `spain_campaign_initialize` for SPR in both the pre-1936 and the 1936+ branch of `endsieg_on_actions.txt`.
2. The initialiser opens the chapter that matches the start date and loads its tree.
3. `on_daily_SPR` calls `spain_campaign_tick`, which runs the transition check daily and the full weekly pass every seventh day.
4. Transitions are always fired by an event option, so the player sees the milestone. `load_focus_tree` uses `keep_completed = yes`, so completed focuses stay completed.
5. The civil-war revolter SPA has no daily on_action of its own, so the original country initialises it once and drives its weekly pass from `spain_campaign_tick`.

## Bookmark behaviour

`spain_campaign_initialize` branches on the start date, so every existing bookmark gets a complete state:

| Start | Chapter | Notes |
| --- | --- | --- |
| 1910, 1914, 1916, 1918 | Restoration | balance at -0.15, caciquismo and army privileges in place |
| 1936.1.1 | Civil war | vanilla tree, still before the rising |
| 1939, 1941, 1942, 1943, 1944, 1945 | Post-war | reconstruction spirit and programme, no balance |

## AI

Focus weights are inline (`@high`, `@priority`, `@low`), chosen so historical AI takes the historical option in every exclusive pair: repression over conciliation, the statute over centralism, the Popular Front over the National Front, and armed neutrality over intervention.
Decisions carry `ai_will_do` bases in the same direction.
The three SPR strategy plans are gated to 1936 and later so they cannot steer the chapter trees.
Debug decisions are `is_debug = yes` and `is_ai = no`.

## Tuning

All values live in `common/script_constants/spain_campaign.txt` and are read as `constant:spain_campaign.<key>`.
Focus durations use file macros (`@short`, `@normal`, `@long`) because the field needs a literal.

## Icons

Every focus, spirit, decision and category currently reuses an existing sprite, so nothing is missing at runtime.
Custom art is pending for:

| Asset | Sprite name | File | Consumers |
| --- | --- | --- | --- |
| Crown side emblem | `GFX_bop_SPR_crown_side` | `interface/endsieg_spain_icons.gfx` | balance of power (currently points at the vanilla monarchism category art) |
| Cortes side emblem | `GFX_bop_SPR_cortes_side` | `interface/endsieg_spain_icons.gfx` | balance of power (currently vanilla democracy art) |
| Restoration focus family | `GFX_focus_SPR1_*` | `interface/endsieg_spain_icons.gfx` | 36 focuses, currently generic goals |
| Dictatorship focus family | `GFX_focus_SPR2_*` | same | 24 focuses |
| Republic focus family | `GFX_focus_SPR3_*` | same | 29 focuses |
| Republican post-war family | `GFX_focus_SPR4_*` | same | 22 focuses |
| Spanish spirit family | `GFX_idea_spain_*` | same | 46 spirits |
| Decision category art | `GFX_decision_category_SPR_*` | same | 8 categories |

## Validation status

Statically checked: brace balance on every new file, no duplicate focus ids, every `focus =` reference resolves inside its tree, every `spain_*` effect and trigger call is defined, every idea, event, category and tooltip key referenced by script exists in localisation, and every icon reference resolves to a real sprite in this mod or the installed vanilla files.
Not checked: in-game behaviour. No launch was performed; the transition dates, AI path choices and balance feel need one playtest per bookmark.

## Future plans

- A custom scripted GUI for the Crown and Cortes panel with the two chambers and the current ministry.
- A regional map-mode interface for civil-war control instead of decision-only feedback.
- Generated icon families listed above.
- Achievements for the surviving Republic, a Carlist restoration and a Falangist victory.
- Portrait and character production for Sanjurjo, Companys, Durruti, Gil Robles and Miguel Primo de Rivera, who currently exist only in event text.
