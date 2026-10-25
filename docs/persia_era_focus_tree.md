# Persia era focus trunk

## Overview

`persian_focus_tree` (`common/national_focus/persia.txt`) is the Graveyard of Empires tree for Persia and Iran.
Its original content assumes the 1936 start under Reza Shah.
This change adds an era trunk of 29 focuses above the original roots, so that every start date from 1910 to 1945 begins in the period it belongs to.

The trunk has three eras.
Era I, Qajar Twilight (1910 to 1921), covers the spheres of influence, the army question, the tribal question, the First World War and the Anglo-Persian Agreement.
Era II, Reza Khan's Persia (1921 to 1941), covers the coup, the dynasty or republic fork, the consolidation of the state and the change of the country's name to Iran.
Era III, Occupied Iran (1941 to 1946), covers the 1941 ultimatum, the occupation, the Persian Corridor, the Tehran Declaration and the Azerbaijan crisis.

The original industry, army, air, navy and political roots now open only after the matching trunk focus.
Later start dates complete the part of the trunk that already happened from `history/countries/PER - Persia.txt`.

## Structure

The trunk sits at y = -16 to -2, centred on x = 25.
The camera opens on the trunk (`initial_show_position`), and a shortcut button (`PER_era_shortcut`) jumps to it.

| Row (y) | Focus | Notes |
| --- | --- | --- |
| -16 | `PER_the_persian_question` | Root. Adds `PER_spheres_of_influence` and `PER_weak_central_authority`. |
| -15 | `PER_shuster_mission`, `PER_the_army_question`, `PER_the_tribal_question` | Three columns at x = 19, 25, 31. |
| -14 | `PER_third_power_diplomacy` / `PER_accept_the_spheres`; `PER_swedish_gendarmerie` / `PER_cossack_brigade`; `PER_bakhtiari_alliance` / `PER_provincial_governors` | One exclusive pair per column. |
| -13 | `PER_wartime_neutrality` | Needs one focus from each pair. Opens when the Great War begins (28 July 1914). |
| -12 | `PER_ratify_the_agreement` / `PER_reject_the_agreement` | Exclusive. Open from 1 August 1919. |
| -11 | `PER_the_1921_coup` | Opens from 1 February 1921. Rewards depend on the earlier choices. |
| -10 | `PER_pahlavi_dynasty` / `PER_republic_movement` | Exclusive. Changes the leader and the government. |
| -9 | `PER_constituent_assembly` | Sets elections and the ruling party for the chosen regime. |
| -8 | `PER_pacify_the_provinces`, `PER_codify_the_state`, `PER_universal_conscription` | All three are needed for the capstone. |
| -7 | `PER_the_name_of_iran` | Capstone of Era II. Removes the foreign tutelage spirits. |
| -6 | `PER_the_august_ultimatum` | Opens from 25 August 1941, or at war with Britain or the Soviet Union. |
| -5 | `PER_defend_the_homeland` / `PER_the_tripartite_treaty` / `PER_look_to_berlin` | Mutually exclusive. |
| -4 | `PER_persian_corridor`, `PER_german_agents` | Follow the treaty and the Berlin route. |
| -3 | `PER_tehran_declaration` | Opens from 28 November 1943. |
| -2 | `PER_the_azerbaijan_question` | Opens from 1 August 1945. |

### How the original tree is gated

| Original root | Now requires |
| --- | --- |
| `PER_modernizing_iran` (industry) | `PER_the_name_of_iran` |
| `PER_restructure_army` | `PER_universal_conscription` |
| `PER_establish_airforce` | `PER_the_name_of_iran` |
| `PER_establish_the_navy` | `PER_the_name_of_iran` and a coastal state |
| `PER_the_pahlavi_imperium` | `PER_the_name_of_iran` and a neutrality government |
| `PER_rally_the_reformers` | `PER_the_name_of_iran` |

`PER_fight_for_iran` is an emergency focus that already requires a defensive war, so it is unchanged.
The gates use `available`, so no extra connectors cross the layout.

## History completions

The history blocks run cumulatively, so each start date inherits the earlier ones.
Each block sets `PER_history_start`, completes the listed focuses and clears the flag.
Focus rewards wrap one-off boosts in `PER_not_history_start`, so a later start does not pay political power, experience, opinion shifts, construction or advisors a second time.
Persistent effects (ideas, flags, leader changes, government) are not wrapped.

| Start block | Focuses completed |
| --- | --- |
| 1914 | `PER_the_persian_question`, `PER_shuster_mission`, `PER_accept_the_spheres` |
| 1916 | `PER_the_army_question`, `PER_cossack_brigade` |
| 1918 | `PER_the_tribal_question`, `PER_bakhtiari_alliance`, `PER_wartime_neutrality` |
| 1936 | `PER_reject_the_agreement`, `PER_the_1921_coup`, `PER_pahlavi_dynasty`, `PER_constituent_assembly`, `PER_pacify_the_provinces`, `PER_codify_the_state`, `PER_universal_conscription`, `PER_the_name_of_iran` |
| 1942 | `PER_the_august_ultimatum`, `PER_the_tripartite_treaty` |
| 1943 | `PER_persian_corridor` |
| 1944 (January) | `PER_tehran_declaration` |

The 1936 block runs after the existing `retire_character` and `recruit_character` lines, so the dynasty reward finds Reza Shah already recruited.
The 1939 and 1941 blocks add nothing: the 1941 ultimatum opens by date during play.
The 1944 (November) and 1945 blocks add nothing: `PER_the_azerbaijan_question` opens by date on 1 August 1945.

## National spirits (`common/ideas/PER_era.txt`)

At most three trunk spirits are active at once.

| Spirit | Added by | Removed or replaced by |
| --- | --- | --- |
| `PER_spheres_of_influence` | `PER_the_persian_question` | Replaced by `PER_anglo_persian_tutelage` (`PER_ratify_the_agreement`); removed by `PER_the_1921_coup` after the agreement was rejected; removed by `PER_the_name_of_iran` otherwise |
| `PER_anglo_persian_tutelage` | `PER_ratify_the_agreement` | `PER_the_name_of_iran` |
| `PER_weak_central_authority` | `PER_the_persian_question` | `PER_pacify_the_provinces` |
| `PER_allied_occupation` | `PER_the_tripartite_treaty` | `PER_tehran_declaration` |

## Route logic

Each Era I column is a separate answer to a separate problem, and the choice is used again later.
The flags they set are read by the coup, the pacification and the conscription focuses.

| Flag | Set by | Read by |
| --- | --- | --- |
| `PER_third_power` | `PER_third_power_diplomacy` | `PER_wartime_neutrality` (war support) |
| `PER_accepted_spheres` | `PER_accept_the_spheres` | `PER_wartime_neutrality` (political power) |
| `PER_treasury_reformed` | `PER_shuster_mission` | `PER_codify_the_state` (hires Arthur Millspaugh) |
| `PER_cossack_brigade` | `PER_cossack_brigade` | `PER_the_1921_coup` (army experience), `PER_universal_conscription` (war support) |
| `PER_swedish_gendarmerie` | `PER_swedish_gendarmerie` | `PER_the_1921_coup` (stability) |
| `PER_tribal_alliance` | `PER_bakhtiari_alliance` | `PER_pacify_the_provinces` (stability) |
| `PER_centralizing` | `PER_provincial_governors` | `PER_pacify_the_provinces` (political power, war support) |
| `PER_rejected_agreement` | `PER_reject_the_agreement` | `PER_the_1921_coup` (removes the spheres, Soviet opinion) |
| `PER_british_tutelage` | `PER_ratify_the_agreement` | `PER_the_1921_coup` (British opinion) |
| `PER_pahlavi_dynasty` / `PER_republic` | the fork | `PER_constituent_assembly` (ruling party and elections) |

The dynasty keeps the neutrality government, recruits Reza Shah Pahlavi and retires Ahmad Shah, which opens `PER_the_pahlavi_imperium`.
The republic sets the democratic government, retires Ahmad Shah and recruits Mohammad Ali Foroughi, which opens `PER_rally_the_reformers` with a democratic government.
Era III is a three-way exclusive choice.
Defending the homeland gives experience, war support and manpower and leaves the existing `PER_fight_for_iran` tree to carry the war.
The treaty route adds the occupation spirit, opens the Persian Corridor and ends in the Tehran Declaration with guarantees from Britain, the Soviet Union and the United States.
The Berlin route is a high-risk alternative that ends in German agents.

## Tuning

All amounts that scale with play read from `common/script_constants/PER_focus_tree.txt` (`constant:per_focus_tree.<key>`).
Spirit modifiers are fixed in `common/ideas/PER_era.txt`, because idea modifier blocks do not accept constants.
All authored values are multiples of five (percent or points).

## Scripted helpers

- `PER_not_history_start` (`common/scripted_triggers/PER_focus_triggers.txt`): true outside the start-of-game history script. Scope: country.
- `PER_shift_opinion` (`common/scripted_effects/PER_focus_effects.txt`): applies an opinion modifier toward Persia from a named country when it exists. Inputs: `TAG`, `MODIFIER`. The scope tag is built with `meta_effect`, because a scripted effect parameter cannot be used as a scope key. Example: `PER_shift_opinion = { TAG = GER MODIFIER = medium_increase }`.
- `PER_give_guarantee_if_exists`: the named country guarantees Persia when it exists. Input: `TAG`.

## AI weights

Hand calculations from the script, because the probability analyzer does not support game version 1.19.3.0 (verified for 1.19.2.0).
Weights are independent scores; the AI takes the highest available score, not a share of the total.
"Historical" means `is_historical_focus_on = yes`, which multiplies the historical option by three.

| Fork | Option scores, historical | Option scores, not historical | Notes |
| --- | --- | --- | --- |
| Finance | accept 60, third power 20 | 20 and 20 (tie) | Third power scores 0 when Germany does not exist. |
| Army | Cossack 60, Swedish 20 | 20 and 20 (tie) | |
| Periphery | governors 60, Bakhtiari 20 | 20 and 20 (tie) | |
| Agreement | reject 60, ratify 5 | reject 20, ratify 5 | |
| Regime | dynasty 80, republic 10 | dynasty 80, republic 10 | No historical multiplier. |
| 1941 | treaty 120, defend 10, Berlin 5 | treaty 40, defend 10, Berlin 5 | Berlin is unavailable when Germany does not exist. |

## Icons

All icons are existing vanilla `GFX_goal_generic_*`, `GFX_focus_generic_*` and `GFX_focus_PER_*` sprites, and the spirits reuse `GFX_idea_generic_foreign_capital`, `GFX_idea_chi_warlord_integration` and `GFX_idea_DEN_occupation_laws`.
No new art or `.gfx` entries are needed.
Bespoke icons for the trunk and its spirits are an optional later improvement.

## Characters

`common/characters/PER_restored.txt` restores 37 vanilla Persian characters that the mod's trimmed `common/characters/PER.txt` omitted.
The original tree references several of them (`PER_andre_godard`, `PER_fakhrafagh_parsa`, `PER_abdolsamad_kambakhsh`, `PER_bahram_aryana`, `PER_gholam_ali_oveissi`), and the trunk uses `PER_ali_akbar_davar`, `PER_arthur_millspaugh` and `PER_mohammad_ali_foroughi`.
The blocks are unchanged copies of the installed game's `PER.txt`.

## Route coverage

| Required route | Implemented | Status | Notes |
| --- | --- | --- | --- |
| Era-appropriate opening for 1910 | Era I columns | Done | Three forks and the 1914 neutrality focus. |
| Late-start history | History completions at 1914, 1916, 1918, 1936, 1942, 1943 and 1944 | Done | The 1939, 1941, November 1944 and 1945 blocks add nothing. |
| Political change | Dynasty or republic, constituent assembly | Done | Leader, government and elections change. |
| Original industry, army, air, navy | Gated on the trunk | Done | No content changed inside those branches. |
| Occupation and Allied war | Era III | Done | Defend, treaty or Berlin. |
| Distinct expansion branch | None | Not done | See omissions. |

## Simplifications and omissions

- The trunk is 29 focuses, not a full route set. Each era has one clear spine and two or three forks.
- There is no distinct expansion branch yet. The original tree's expansion content is unchanged.
- No new events or decisions were added. The forks are focuses and flags.
- The republic route reuses the original reformers tree rather than adding its own late branches.
- The Berlin route is two focuses long and ends without its own late-game payoff.
- The original branches still contain 1936-era assumptions (for example the White Revolution), and the date gates apply only to the new trunk.
- Localisation is English only, matching the localisation present in the repository.
- The AI weights were calculated by hand because the probability analyzer does not support this game version.
- No achievement hooks were added.

## Future plans and suggestions

- Add a late-game expansion branch: Bahrain, the Shatt al-Arab frontier, and the Azerbaijan and Kurdish settlements.
- Add decisions for tribal subsidies, gendarmerie posts and the Persian Corridor supply flow, gated by the trunk flags.
- Give each era a small balance-of-power mechanic: crown against Majlis in Era II, and occupation pressure in Era III.
- Add bespoke icons and spirit art so the trunk has its own visual identity.
- Date-gate the original branches that assume the Pahlavi modernisation programme (White Revolution, SAVAK) so earlier starts do not see them.
- Translate the localisation into the project's other languages.
