# Persia era focus trunk

## Overview

Persia uses two focus trees, chosen by the engine from each tree's `country` score.
The mod's other early-scenario countries already work this way (`WWI - Italy.txt`, `WWI - Germany.txt` and others).

| Tree | File | Used when | Content |
| --- | --- | --- | --- |
| `persian_focus_ww1` | `common/national_focus/WWI - Persia.txt` | `tag = PER`, `date < 1936.1.1` and `has_start_date < 1936.1.1` (score 20000) | Era I and Era II (21 focuses) above the generic WWI shared focuses |
| `persian_focus_tree` | `common/national_focus/persia.txt` | Otherwise, with the Graveyard of Empires DLC | The original 1936 tree plus Era III (8 focuses) above its roots |

Before this change Persia had no WWI tree, so every pre-1936 start fell back to `generic_focus_ww1` (score 10000).
The new tree outscores it for Persia and keeps the same shared focuses (`shared_industrialisation`, `shared_GEN_powered_flight`, `shared_GEN_political_effort`, `shared_GEN_20_cent_military`, `shared_GEN_naval_effort`, `shared_GEN_industrial_effort` and `WW1_WO_GEN_war_council`).
The shared focuses all start at y = 0, so the trunk sits above them at y = -11 to -2.

The trunk has three eras.
Era I, Qajar Twilight (1910 to 1921), covers the spheres of influence, the army question, the tribal question, the First World War and the Anglo-Persian Agreement.
Era II, Reza Khan's Persia (1921 to 1941), covers the coup, the dynasty or republic fork, the consolidation of the state and the change of the country's name to Iran.
Era III, Occupied Iran (1941 to 1946), covers the 1941 ultimatum, the occupation, the Persian Corridor, the Tehran Declaration and the Azerbaijan crisis.

The original 1936 tree keeps its own roots, unchanged.
A game that starts before 1936 moves to `persian_focus_tree` when the date reaches 1936, as for the other WWI trees, and Era III is available there from 1941.

## Structure

### WWI tree (`persian_focus_ww1`), Eras I and II

The camera opens on the root (`initial_show_position` x = 25, y = -11) and a shortcut (`PER_qajar_shortcut`) jumps to it.

| Row (y) | Focus | Notes |
| --- | --- | --- |
| -11 | `PER_the_persian_question` | Root. Adds `PER_spheres_of_influence` and `PER_weak_central_authority`. |
| -10 | `PER_shuster_mission`, `PER_the_army_question`, `PER_the_tribal_question` | Three columns at x = 19, 25, 31. |
| -9 | `PER_third_power_diplomacy` / `PER_accept_the_spheres`; `PER_swedish_gendarmerie` / `PER_cossack_brigade`; `PER_bakhtiari_alliance` / `PER_provincial_governors` | One exclusive pair per column. |
| -8 | `PER_wartime_neutrality` | Needs one focus from each pair. Opens when the Great War begins (28 July 1914). |
| -7 | `PER_ratify_the_agreement` / `PER_reject_the_agreement` | Exclusive. Open from 1 August 1919. |
| -6 | `PER_the_1921_coup` | Opens from 1 February 1921. Rewards depend on the earlier choices. |
| -5 | `PER_pahlavi_dynasty` / `PER_republic_movement` | Exclusive. Changes the leader and the government. |
| -4 | `PER_constituent_assembly` | Sets elections and the ruling party for the chosen regime. |
| -3 | `PER_pacify_the_provinces`, `PER_codify_the_state`, `PER_universal_conscription` | All three are needed for the capstone. |
| -2 | `PER_the_name_of_iran` | Capstone of Era II. Removes the foreign tutelage spirits. |

### 1936 tree (`persian_focus_tree`), Era III

A shortcut (`PER_occupation_shortcut`) jumps to the first focus.
The camera still opens on the original roots.

| Row (y) | Focus | Notes |
| --- | --- | --- |
| -6 | `PER_the_august_ultimatum` | Root. Opens from 25 August 1941, or at war with Britain or the Soviet Union. |
| -5 | `PER_defend_the_homeland` / `PER_the_tripartite_treaty` / `PER_look_to_berlin` | Mutually exclusive. |
| -4 | `PER_persian_corridor`, `PER_german_agents` | Follow the treaty and the Berlin route. |
| -3 | `PER_tehran_declaration` | Opens from 28 November 1943. |
| -2 | `PER_the_azerbaijan_question` | Opens from 1 August 1945. |

## History completions

The history blocks run cumulatively, so each start date inherits the earlier ones.
Each block sets `PER_history_start`, completes the listed focuses and clears the flag.
The three early blocks are wrapped in `limit = { has_start_date < 1936.1.1 }`, because those focuses exist only in the WWI tree.
Focus rewards wrap one-off boosts in `PER_not_history_start`, so a later start does not pay political power, experience, opinion shifts, construction or advisors a second time.
Persistent effects (ideas, flags, leader changes, government) are not wrapped.

| Start block | Focuses completed |
| --- | --- |
| 1914 | `PER_the_persian_question`, `PER_shuster_mission`, `PER_accept_the_spheres` |
| 1916 | `PER_the_army_question`, `PER_cossack_brigade` |
| 1918 | `PER_the_tribal_question`, `PER_bakhtiari_alliance`, `PER_wartime_neutrality` |
| 1942 | `PER_the_august_ultimatum`, `PER_the_tripartite_treaty` |
| 1943 | `PER_persian_corridor` |
| 1944 (January) | `PER_tehran_declaration` |

A 1936 or later start has no Era I or Era II focuses and begins at the original roots.
The 1936, 1939, 1941, November 1944 and 1945 blocks complete nothing: the 1941 ultimatum and `PER_the_azerbaijan_question` open by date during play.

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

The dynasty keeps the neutrality government, recruits Reza Shah Pahlavi and retires Ahmad Shah.
The republic sets the democratic government, retires Ahmad Shah and recruits Mohammad Ali Foroughi.
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
Opinion shifts and guarantees are written inline in the focus rewards, each wrapped in `if = { limit = { country_exists = TAG } ... }`.
They are not a scripted effect with parameters: the focus files are read before scripted effects are known, so a call such as `PER_shift_opinion = { TAG = GER ... }` is parsed as a block of unknown effects and the rest of the file is lost.
A scripted effect called without parameters (`= yes`) or a scripted trigger is resolved later and is safe in a focus file.

## AI weights

Hand calculations from the script, because the probability analyzer does not support game version 1.19.3.0 (verified for 1.19.2.0).
Each option has its own score, and "historical" means `is_historical_focus_on = yes`, which multiplies the historical option by three.

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
| Era-appropriate opening for 1910 | Era I columns in `persian_focus_ww1` | Done | Three forks and the 1914 neutrality focus. |
| Late-start history | History completions at 1914, 1916, 1918, 1942, 1943 and 1944 | Done | 1936 and later starts begin at the original roots. |
| Political change | Dynasty or republic, constituent assembly | Done | Leader, government and elections change. |
| Occupation and Allied war | Era III in `persian_focus_tree` | Done | Defend, treaty or Berlin. |
| Original 1936 branches | Unchanged | Not changed | No content was edited inside those branches. |
| Distinct expansion branch | None | Not done | See omissions. |

## Simplifications and omissions

- The trunk is 29 focuses, not a full route set. Each era has one clear spine and two or three forks.
- There is no distinct expansion branch yet. The original tree's expansion content is unchanged.
- No new events or decisions were added. The forks are focuses and flags.
- The republic route reuses the original reformers tree rather than adding its own late branches.
- The Berlin route is two focuses long and ends without its own late-game payoff.
- The original branches still contain 1936-era assumptions (for example the White Revolution), and no date gates were added to them.
- Era I and Era II are not available to a game that starts in 1936 or later, because those starts use the 1936 tree.
- Localisation is English only, matching the localisation present in the repository.
- The AI weights were calculated by hand because the probability analyzer does not support this game version.
- No achievement hooks were added.

## Future plans and suggestions

- Add a late-game expansion branch: Bahrain, the Shatt al-Arab frontier, and the Azerbaijan and Kurdish settlements.
- Add decisions for tribal subsidies, gendarmerie posts and the Persian Corridor supply flow, gated by the trunk flags.
- Give each era a small balance-of-power mechanic: crown against Majlis in Era II, and occupation pressure in Era III.
- Add bespoke icons and spirit art so the trunk has its own visual identity.
- Date-gate the original branches that assume the Pahlavi modernisation programme (White Revolution, SAVAK).
- Translate the localisation into the project's other languages.
