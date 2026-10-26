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

New: four chapter trees (272 focuses), six system layers, 38 decisions, 21 events, 46 national spirits, one balance of power, and the campaign state that ties them together.

| Tree | Focuses |
| --- | --- |
| `spain_restoration_focus` | 77 |
| `spain_rivera_focus` | 64 |
| `spain_republic_focus` | 74 |
| `spain_republic_postwar_focus` | 57 |

### Layout
Branches are positioned with `relative_position_id` from their parent, the way the Iran chapter trees do it, so a branch hugs the focus that opens it instead of spreading across a fixed grid.
56 of the 272 focuses are placed that way; the Restoration tree uses a fixed lane grid instead, with paired branches two columns apart.
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


## The Cortes

`SPR_cortes` is a decision category that mounts a chamber panel (`interface/endsieg_spain_cortes.gui`, wired in `common/scripted_guis/spain_cortes_scripted_gui.txt`).
The chamber has 400 seats across seven blocs: monarchists, liberals, conservatives, republicans, socialists, Carlists and Falange.
Raw support is written to `spain_cortes_raw_*` by `spain_cortes_recount` and normalised to exactly 400 seats, so a majority is always 201.
Support moves with the campaign flags: electoral reform and a free press shift seats left, managed elections and suppression shift them right, and from 1931 the whole chamber is recalculated as a republican one.

Bills are ordinary decisions in the same category, each gated on the bloc that would carry it:

| Bill | Requires |
| --- | --- |
| Budget | right bloc above 200 |
| Army budget | right bloc above 200 |
| Agrarian bill | left bloc above 200 |
| Labour charter | left bloc above 200 |
| Regional statute | left bloc above 200, from 1931 |
| Electoral law | left bloc above 200, holds an election |
| Dissolve the Cortes | left bloc below 201, hands power to the Crown |

So the chamber you build decides what the government can legislate, and a government without a majority can only dissolve parliament.

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

## Era handover

Each chapter opener ends by calling `spain_carry_over_choices` (in `common/scripted_effects/spain_campaign_effects.txt`).
It converts the flags a finished era set into the persistent variables the next era reads, so a player's choices survive the tree that made them rather than dying with it.
One guard flag per era (`spain_carried_restoration`, `spain_carried_rivera`, `spain_carried_republic`) means a reload cannot apply it twice.

| From | Flag | Becomes |
| --- | --- | --- |
| Restoration | `spain_army_settled`, `spain_coup_prepared` | `spain_military_loyalty` down, `spain_coup_pressure` up, `spain_legacy_politicised_army` |
| Restoration | `spain_electoral_reform` | `spain_legacy_parliamentary`, political power |
| Restoration | `spain_labour_conciliation` / `spain_labour_repression` | `spain_nationalist_tension` down / up, matching legacy flag |
| Restoration | `spain_mining_districts`, `spain_agrarian_credit` | `spain_industry`, `spain_agriculture` |
| Restoration | `spain_mancomunitat`, `spain_basque_fueros` | `spain_catalan_autonomy`, `spain_basque_autonomy` |
| Dictatorship | `spain_constitution_suspended`, `spain_consultative_assembly` | tension up and `spain_legacy_decree_rule`, or `spain_legacy_assembly` |
| Dictatorship | `spain_alhucemas_landed`, `spain_aircraft_industry`, `spain_iberian_railway` | loyalty, `spain_industry`, `spain_infrastructure` |
| Republic | `spain_agrarian_reform_started`, `spain_catalan_statute_started` | `spain_agriculture`, `spain_catalan_autonomy` |
| Republic | `spain_army_plot`, `spain_calvo_sotelo_dead` | loyalty down and pressure up, tension up |
| Republic | `spain_arms_for_militias` | `spain_legacy_armed_militias` |

## Decision availability

Decisions appear when their own question opens, not at scenario start.
Each era-specific decision reads the flag or date that begins its era: the Protectorate's columns need `spain_rif_war_active`, the officer decisions need the Juntas or the army question, the faction decisions need the civil war, reconstruction needs `spain_civil_war_reconstruction` or the postwar chapter, and wartime diplomacy needs its own date.
A decision whose gate reads a flag nothing sets is a decision that never appears, so `python .tmp/check_decisions.py` verifies every gate flag against the setters in the mod.

## Chapter events

`spain_chapter_events` runs on the weekly tick and fires the era conversations that are not tied to a focus: `spain_campaign.70` (the Pact of San Sebastian, August 1930) and `spain_campaign.71` (Hendaye, October 1940).
Both are triggered-only and guarded by a seen flag, so they fire once per campaign.

## Continuous focus placement

Every focus tree in the mod carries `continuous_focus_position = { x = 1500 y = 6000 }`.
A tree without the key falls back to a default that draws the continuous panel over its last rows, which is why the Iran chapter trees overlapped until they were given the key.
Tree ids using the key must be listed in that form; `INT - WHR Paths.txt` holds shared focuses only and correctly has none.

## AI focus order

`common/ai_strategy_plans/SPR_chapter_plans.txt` holds one plan per chapter: Restoration, dictatorship, Republic and Republican post-war.
Each is enabled only while that chapter is current and only with historical AI on, so ahistorical games keep the per-focus `ai_will_do` weighting instead of being herded down the historical lane.
Chapter flags accumulate, so each plan also checks that no later chapter has opened; without that, every earlier plan would stay enabled for the rest of the campaign.

## Legacy flags and what reads them

The handover writes `spain_legacy_*` flags, and each one has a consumer: a politicised army and a prepared plot add coup pressure on every coup check, armed militias put infantry equipment in the stockpile when the civil war opens, and a parliamentary or corporatist settlement carries stability or war support into it.
A flag that nothing reads is dead state, which is why the flags are listed here rather than left to be discovered.

## The Cortes panel

`common/scripted_guis/spain_cortes_scripted_gui.txt` mounts `spain_cortes_window` from the `SPR_cortes` decision category.
The seat figures are interface text bindings of the form `[?spain_cortes_seats_<bloc>]`; the engine fills them from the variables `spain_cortes_recount` writes, and the panel itself is gated on `spain_cortes_total`.
The `|0` format suffix used in localisation is not valid here and was removed.

## The chamber as a hemicycle

`interface/endsieg_spain_cortes.gui` is generated by `tools/build_spain_cortes_hemicycle.py`; do not hand-edit it.
The chamber is 54 dots on four concentric arcs spanning a full semicircle from x=120 to x=380, each dot carrying about seven of the 400 seats.
Dots are coloured by the bloc that holds them, swept left to right in the political order of the house, so government and opposition read as bands.

How the colouring works, end to end:

1. `spain_cortes_recount` normalises the raw support of each bloc to 400 seats, writes `spain_cortes_cum_*` cumulative totals left to right, and calls `spain_cortes_draw_hemicycle`.
2. `common/scripted_effects/spain_cortes_hemicycle.txt` gives every dot a bloc number (1 socialists … 7 Falange, 8 empty).
3. `common/scripted_guis/spain_cortes_scripted_gui.txt` declares one image property per dot, `image = "[spain_cortes_dot_N_img]"`.
4. `localisation/english/spain_cortes_dots_l_english.yml` holds one `defined_text` per dot that maps the bloc number to a `GFX_spain_cortes_dot_*` sprite.

Seat art is generated by `tools/build_spain_cortes_dots.py` — eight 16px discs written as uncompressed DDS in `gfx/interface/endsieg_spain_dots/`, registered in `interface/endsieg_spain_icons.gfx`.

## Dissolving the Cortes

Dissolution is not a decision. `SPR3_the_choice_of_war` ends in a mutually exclusive pair:

| Focus | Effect |
| --- | --- |
| `SPR3_uphold_the_cortes` | `spain_uphold_the_cortes` — stability, political power, officer goodwill, clears `spain_cortes_suspended` |
| `SPR3_rule_without_the_cortes` | `spain_dissolve_the_cortes` — removes `SPR_crown_and_cortes`, costs 150 political power, −25% stability, +20 tension, −10 officer loyalty, +15 coup pressure, grants `spain_cortes_suspended` |

The `SPR_cortes` category hides on `spain_cortes_dissolved`, so the chamber closes with the chamber.
Forcing an election costs 150, not 75.

## Validation status

Statically checked: brace balance on every new file, no duplicate focus ids, every `focus =` reference resolves inside its tree, every `spain_*` effect and trigger call is defined, every idea, event, category and tooltip key referenced by script exists in localisation, and every icon reference resolves to a real sprite in this mod or the installed vanilla files.
Not checked: in-game behaviour. No launch was performed; the transition dates, AI path choices and balance feel need one playtest per bookmark.

## Future plans

- A custom scripted GUI for the Crown and Cortes panel with the two chambers and the current ministry.
- A regional map-mode interface for civil-war control instead of decision-only feedback.
- Generated icon families listed above.
- Achievements for the surviving Republic, a Carlist restoration and a Falangist victory.
- Portrait and character production for Sanjurjo, Companys, Durruti, Gil Robles and Miguel Primo de Rivera, who currently exist only in event text.

Re-audited with `.tmp/audit_spain2.py`, `.tmp/validate_layout.py`, `.tmp/analyse_focus.py`, `.tmp/flag_readers.py`, `.tmp/list_decisions.py` and `.tmp/check_decisions.py`:
no duplicate focus ids, no overlapping slots, no icon one column from its neighbour, every icon resolves, every focus has `ai_will_do`, no focus whose only reward is experience, all four trees balanced, every decision gate flag has a setter, and every event and tooltip key localised.
Not checked: in-game behaviour. The handover, the new event firing and the decision gates need one playtest per bookmark.
