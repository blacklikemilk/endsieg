# Reward audit — Iran 1910–1918 focus tree (`common/national_focus/iran_ww1.txt`)

Read-only audit. Every reward below was expanded by hand and checked against the scripted effects,
scripted triggers, decisions, ideas, events and state history it ultimately touches. No focus file was
modified; this report is the only file written.

**Scope note:** the file contains **90** focus blocks (`id = IR1_*`), not 91. All 90 are covered.
Focuses auto-completed by `iran_apply_historical_start` (1911+/1916 bookmarks) are marked as such.

## Evidence base

| Claim | Where it was checked |
| --- | --- |
| Focus rewards, costs, `available`, `ai_will_do` | `common/national_focus/iran_ww1.txt` (parsed programmatically, 90/90) |
| What each scripted effect really does | `common/scripted_effects/iran_campaign.txt`, `iran_great_game_acts.txt`, `PER_bop_effects.txt`, `iran_regime_shift.txt` |
| Which flags are read, and where | repo-wide rg over `common/`, `events/`, `history/` for all 93 flags the rewards set |
| Decision payoffs and gates | `common/decisions/iran_campaign.txt`, `iran_focus_ww1.txt`, `PER_crown_and_majlis.txt`, `iran_great_game.txt`, `iran_foreign_agreements.txt` |
| Path trigger consumers | `common/scripted_triggers/iran_continuity.txt` + its 7 consumers in `iran_interwar.txt` / `iran_ww2.txt` |
| Ideas | `common/ideas/iran_campaign.txt`, `PER_era.txt` |
| State ownership / coast | `history/states/266,411,412,413,417,419,420`; `map/definition.csv` coastal column |
| Building ids | `common/buildings/00_buildings.txt` (`rail_way`, not `railway`) |
| Balance of power | `common/bop/PER.txt`, `PER_bop_sync` in `PER_bop_effects.txt` (needs `Arms Against Tyranny`) |
| Clock wiring | `common/on_actions/iran_campaign.txt` (`on_monthly_PER`, `on_daily_PER`) |
| Localisation | all 90 ids and `_desc` present; `iran_campaign_l_english.yml` + `iran_ww1_l_english.yml` |

## Classification counts

| Class | Count | Focuses |
| --- | --- | --- |
| FUNCTIONAL | 50 | see table |
| CONDITIONAL-MEANINGFUL | 19 | palace_guard, law_in_the_provinces, shuster_mission, treasury_gendarmerie, a_national_budget, state_bank, oil_royalty_share, grain_requisition, swedish_officers, cossack_command, frontier_posts, rifle_contracts, military_finance, air_detachment, gendarmerie_resistance, guarded_neutrality, refugee_administration, gilan_congress, tabriz_consulates |
| INEFFECTIVE | 6 | diplomatic_corps, agricultural_relief, russian_understanding, ottoman_frontier, jangali_movement, provincial_tax_risings |
| BROKEN | 9 | road_to_the_caspian, bushehr_trade, gulf_ports, gulf_flotilla, officer_loyalty, independence_at_the_peace, hague_appeal, armistice_watch, persia_at_the_conference |
| MISLEADING | 3 | constitution_or_crown, the_great_famine, protect_the_harvest |
| REDUNDANT | 3 | merchant_credit, south_persia_oil, foreign_advisers |

Four systemic problems sit behind most of the individual rows:

1. **The 1917–19 diplomatic capstone is unreachable.** `IR1_independence_at_the_peace.available` requires
   `iran_relief_delivered`, which is set only by the `iran_bread_distribution` decision (`visible` requires
   `date > 1939.9.1`) or by `iran_initialize_campaign` (`date > 1941.9.16`). The `iran_ww1` tree is replaced by
   `iran_interwar` on 1919.1.1 (`iran_route_chapter`), so the flag cannot exist while these focuses do. That kills
   four focuses (`independence_at_the_peace`, `hague_appeal`, `armistice_watch`, `persia_at_the_conference` — the
   only `@grand` focus in the chapter) and the `iran_paris_memorandum` decision they gate.
2. **Three building rewards target a landlocked state, one targets a building id that does not exist.**
   State 411 (file `411-Hormozgan.txt`, internally `# Isfahan`) has **0 coastal provinces**, so `naval_base`
   (`bushehr_trade`, `gulf_ports`) and `dockyard` (`gulf_flotilla`) cannot be built there. `road_to_the_caspian`
   uses `add_building_construction = { type = railway }`; the building id is `rail_way`, so nothing is built.
3. **The most common reward is invisible.** 28 rewards write a country variable; the single most frequent is
   `iran_authority` (+10, 23 focuses). There is no loc key for `iran_authority`, `iran_foreign_paths` or
   `iran_socialist_support` (only `iran_sovereignty` has one), so those lines render as a raw key
   (`iran_authority: 10`), and authority only changes anything at the 65 threshold that swaps
   `iran_fragmented_authority` for `iran_constitutional_state`.
4. **Flags carry the design, but most read only through OR-groups.** 93 flags are set; 21 are never read outside
   this file, and ~35 more only feed an `iran_path_*` trigger that any one of 5–8 flags satisfies. Only the
   "programme" flags (`iran_security_programme`, `iran_treasury_programme`, `iran_construction_programme`,
   `iran_oil_programme`, `iran_workshop_subsidy`, `iran_caspian_priority`, `iran_gulf_priority`,
   `iran_air_programme`, `iran_foreign_programme`) open a decision, i.e. a real payoff.

## Per-focus table

Legend: F = FUNCTIONAL, C = CONDITIONAL-MEANINGFUL, I = INEFFECTIVE, B = BROKEN, M = MISLEADING, R = REDUNDANT.
Cost is weeks. Rewards in the last column are script-ready (single line, HOI4 accepts whitespace-separated effects).

| id | class | what it actually does (expanded) | problem | proposed reward |
| --- | --- | --- | --- | --- |
| IR1_second_majlis (5w) | F | `PER_bop_push_majlis` (+0.20 Majlis, AAT only), event .10 (+50 PP), +50 PP, +5% stability | BOP needs AAT but tooltip always prints; rest is generic | — |
| IR1_parliamentary_mandate (5w) | F | Majlis push, `iran_constitutionalist`, `iran_treasury_programme` (opens `iran_treasury_reform` decision), +10 authority, PP, stability | authority invisible; treasury flag is the real payload | — |
| IR1_court_patronage (5w) | F | `PER_bop_push_crown_small`, `iran_court_compromise` (allow_branch gate), +50 PP, `iran_concede_leading_small` (→ Britain +8 influence, −3 sovereignty, +10 leverage), stability | gives away influence with no text explaining it; AI weight 0 | — |
| IR1_provincial_assemblies (5w) | F | `iran_security_programme` (opens 3 decisions), `iran_anjomans`, +5% stability, event .11, +50 PP | — | — |
| IR1_bakhtiari_bargain (5w) | F | `iran_security_programme`, `iran_bakhtiari_pact`, +8000 manpower, event .11, +5% stability | — | — |
| IR1_anjoman_elections (5w) | F | Majlis push small, `iran_anjoman_elections`, +50 PP, +10 authority, stability | authority line unlocalised | — |
| IR1_royal_household (5w) | F | Crown push (−0.20), `iran_royal_household`, +50 PP, +25 command power, stability | AI weight 0 | — |
| IR1_press_and_debate (5w) | F | `iran_free_press`, +5% stability, **+1 research slot** | best value/effort in the political branch; free press flag only feeds an OR | — |
| IR1_palace_guard (5w) | C | Crown push small, `iran_palace_guard`, +25 army XP, +10% war support; terminal | 5 weeks for 25 XP and 10% WS; the Cossack guard never appears | `PER_bop_push_crown_small = yes if = { limit = { NOT = { has_idea = iran_foreign_military_mission } } add_ideas = iran_foreign_military_mission } add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } hidden_effect = { 266 = { add_building_construction = { type = bunker level = 1 instant_build = yes } } iran_refresh_mechanics = yes }` |
| IR1_law_in_the_provinces (10w) | C | Gate focus (`iran_provincial_compact`): +5% stability, +10 authority, `iran_constitution_secured`, `iran_courts_established` (dead), PP | 10 weeks for a gate; `iran_courts_established` is read nowhere | `PER_bop_push_majlis = yes add_stability = constant:iran_story.stability_major_gain set_country_flag = iran_constitution_secured set_country_flag = iran_courts_established set_country_flag = iran_constitutional_programme hidden_effect = { iran_refresh_mechanics = yes }` (sets the flag that opens the repeatable `iran_constitutional_petitions` decision) |
| IR1_the_young_shah (5w) | F | Crown push small, event .17 (real choice: Majlis or court), `iran_shah_majority`, PP, stability | — | — |
| IR1_regency_council (10w) | F | Crown push small, `iran_regency_council`, +10 authority, stability, PP | 10 weeks for PP/stability/authority | — |
| IR1_diplomatic_corps (10w) | I | Majlis push small, `iran_diplomatic_corps` (dead), +50 PP, +5% stability, `custom_effect_tooltip` promising a diplomatic service | the tooltip describes an institution that is never added; 10 weeks for PP | `PER_bop_push_majlis_small = yes add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } if = { limit = { country_exists = ENG } add_opinion_modifier = { target = ENG modifier = iran_treaty_relations } } if = { limit = { country_exists = RUS } add_opinion_modifier = { target = RUS modifier = iran_treaty_relations } } hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_constitution_or_crown (10w) | M | `PER_bop_pull_to_centre`, +50 PP, +5% stability, a tooltip that restates the question | title/desc promise the settlement of the constitutional question; the focus decides nothing and adds no consequence | `if = { limit = { has_country_flag = iran_constitutionalist } PER_bop_push_majlis = yes else = { PER_bop_push_crown = yes } } add_to_variable = { iran_authority = constant:iran_story.authority_gain } add_political_power = constant:iran_story.political_capital add_stability = constant:iran_story.stability_gain hidden_effect = { iran_refresh_mechanics = yes }` and delete `iran_constitution_or_crown_tt` |
| IR1_defend_constitution (10w) | F | Majlis push, `iran_defended_constitution`, `iran_constitutionalist`, +10% stability, +10 authority, PP | — | — |
| IR1_royal_prerogative (10w) | F | `iran_royal_prerogative`, +20 authority, −5% stability, +50 PP | the authority gain is the real payload but renders as a raw key | — |
| IR1_majlis_budget_authority (10w) | F | Majlis push, `iran_budget_authority`, +8 sovereignty, +10 authority, +50 PP, `iran_budget_established` | — | — |
| IR1_court_and_cabinet (10w) | F | Crown push, `iran_court_cabinet`, +50 PP, `iran_concede_leading_small`, stability, text tooltip | concedes influence for nothing in return | — |
| IR1_assembly_of_1918 (10w) | F | Majlis push small, `iran_assembly_1918` (dead), +50 PP, +10 authority, event .18, stability | the assembly flag itself is dead | — |
| IR1_republican_committee (10w) | F | `iran_republic_candidate` → opens `iran_proclaim_the_republic` decision (1919+, sovereignty ≥ 55), Majlis push, +50 PP, +10 authority, event f1.3 | the only route seed to the republic; AI weight 0 | — |
| IR1_empty_treasury (5w) | F | `iran_treasury_programme` (opens `iran_treasury_reform`), event .12, +50 PP, stability | — | — |
| IR1_shuster_mission (10w) | C | `iran_financial_mission`, `PER_treasury_reformed` (feeds `iran_path_treasury`), +10 authority, text tooltip | the mission itself is not modelled; no revenue effect; tooltip promises supervision | `set_country_flag = iran_financial_mission set_country_flag = PER_treasury_reformed set_country_flag = iran_customs_reformed add_to_variable = { iran_authority = constant:iran_story.authority_gain } PER_bop_push_majlis_small = yes hidden_effect = { iran_refresh_mechanics = yes }` (`iran_customs_reformed` is read by `iran_influence_tick`: +1 sovereignty/month while < 80) |
| IR1_customs_revenue (10w) | F | `iran_construction_programme` (opens the projects category), `iran_customs_service`, +50 PP, +10 authority, stability | projects category decisions need other flags | — |
| IR1_treasury_gendarmerie (5w) | C | `iran_security_programme` (usually already set), +25 army XP, +10% war support | 5 weeks for one flag and 25 XP; the "treasury gendarmerie" is not modelled | `set_country_flag = iran_security_programme add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.security_equipment } add_manpower = constant:iran_story.gendarmerie_manpower add_war_support = constant:iran_story.war_support_gain` |
| IR1_domestic_workshops (10w) | F | 266: +1 slot, +1 industrial complex (instant); `iran_workshop_subsidy` (opens `iran_tehran_workshops` decision: another factory) | — | — |
| IR1_a_national_budget (10w) | C | Gate (`iran_tax_reformed`): `iran_budget_established`, +5% stability, +20 authority, PP | mostly a gate; the authority is the only new value | `set_country_flag = iran_budget_established set_country_flag = iran_treasury_programme add_to_variable = { iran_authority = constant:iran_story.authority_major_gain } add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } add_political_power = constant:iran_story.political_capital hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_belgian_advisers (10w) | F | `iran_belgian_advisers` (dead), +10 authority, **+1 research slot** | flag dead, slot is the whole reward | — |
| IR1_state_bank (10w) | C | `iran_state_bank`, `iran_imperial_bank_question` (dead), `iran_reclaim_british_small` (−8 British influence, +4 sovereignty, −10 leverage), +50 PP, stability | the bank itself is not modelled; the two flags are dead except `iran_state_bank` in `iran_path_treasury` | `iran_reclaim_british_small = yes add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } add_to_variable = { iran_foreign_leverage = constant:iran_story.leverage_loss } set_country_flag = iran_state_bank add_political_power = constant:iran_story.political_capital hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_telegraph_network (10w) | F | `iran_concede_british_small`, 266 +1 infrastructure, 412 +1 infrastructure, +1 research slot, `iran_telegraph_built` (dead) | a focus that builds its own telegraph pays a concession to Britain with no text explaining why | — (keep reward, fix the `iran_concede_british_small` line or move it to a "British loan of engineers" framing) |
| IR1_agricultural_relief (10w) | I | `iran_agricultural_relief` (dead), +5% stability, 417 +1 infrastructure | 10 weeks for 1 infrastructure and 5% stability; "grain and seed" is not modelled | `set_country_flag = iran_agricultural_relief add_stability = constant:iran_story.stability_gain add_manpower = constant:iran_story.tribal_manpower 417 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` (or delete: leaf, removable) |
| IR1_abadan_concession (10w) | F | `iran_oil_programme` (opens `iran_khuzestan_capacity`), `iran_apoc_concession`, 413 +10 oil, `iran_concede_british_large` (−6 sovereignty), event .24 | the concession is a real cost and is stated; fine | — |
| IR1_oil_royalty_share (10w) | C | `iran_royalty_renegotiation`, `iran_reclaim_british_small`, +50 PP, stability, text tooltip | the "renegotiation" is only a tooltip; no oil or revenue change | `iran_reclaim_british_small = yes add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } set_country_flag = iran_royalty_renegotiation if = { limit = { has_country_flag = iran_oil_programme } 413 = { add_resource = { type = oil amount = 5 } } } add_political_power = constant:iran_story.political_capital hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_concession_guarantees (10w) | F | `iran_concession_guarantees`, `iran_concede_british_small`, +500 infantry equipment (ENG) | a stated trade, works | — |
| IR1_road_to_the_caspian (7w) | B | `iran_caspian_priority` (opens `iran_caspian_roads`), `iran_construction_programme`, `iran_concede_northern_small`, **420 railway level 2** | `type = railway` is not a building id (`rail_way` is), so the railway is never built and an error is logged | `set_country_flag = iran_caspian_priority set_country_flag = iran_construction_programme iran_concede_northern_small = yes 420 = { add_building_construction = { type = infrastructure level = 2 instant_build = yes } }` |
| IR1_bushehr_trade (7w) | B | `iran_gulf_priority` (opens `iran_gulf_harbour`), `iran_construction_programme`, `iran_reclaim_british_small`, **411 naval base** | state 411 has 0 coastal provinces → no naval base can be built; Bushehr is in 412 | `set_country_flag = iran_gulf_priority set_country_flag = iran_construction_programme iran_reclaim_british_small = yes 412 = { add_building_construction = { type = naval_base level = 1 instant_build = yes } }` |
| IR1_gulf_ports (10w) | B | `iran_concede_british_small`, **411 naval base**, +25 navy XP, `iran_gulf_service` (dead) | same landlocked state; description explicitly promises "a base at Bushehr" | `iran_concede_british_small = yes 412 = { add_building_construction = { type = dockyard level = 1 instant_build = yes } } navy_experience = constant:iran_story.navy_experience set_country_flag = iran_gulf_service` |
| IR1_the_great_famine (5w) | M | `iran_relief_programme` (no in-chapter effect: its only decision is 1939+), **adds `iran_supply_emergency`** (−15% stability, −15% IC), −5% stability, event .16 | titled as relief; grants a permanent-until-1939 penalty spirit and nothing else | keep the crisis, but pair it with a cure: `set_country_flag = iran_relief_programme add_ideas = iran_supply_emergency if = { limit = { NOT = { has_country_flag = iran_relief_event_seen } } set_country_flag = iran_relief_event_seen country_event = { id = iran_campaign.16 } }` and make `IR1_public_granaries_1917` remove the spirit (see next rows) |
| IR1_grain_requisition (7w) | C | `iran_concede_british_small`, `iran_grain_requisition`, **100** equipment (ENG), −5% stability, +10% war support | 100 rifles for a 7-week focus and a concession; flag only feeds unused `iran_path_humiliated` | `iran_concede_british_small = yes set_country_flag = iran_grain_requisition add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_small producer = ENG } add_manpower = constant:iran_story.reserve_manpower add_stability = constant:iran_story.stability_cost add_war_support = constant:iran_story.war_support_gain` |
| IR1_public_granaries_1917 (7w) | F | `iran_public_granaries`, +10% stability, 266 +1 infrastructure | does not end the famine spirit it is supposed to answer | `remove_ideas = iran_supply_emergency set_country_flag = iran_public_granaries add_stability = constant:iran_story.stability_major_gain 266 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` |
| IR1_wartime_budget (10w) | F | `iran_wartime_budget` (dead), +50 PP, +10 authority, `iran_wartime_economy` 730 days (−5% consumer goods), stability | good reward, but the flag is dead | — |
| IR1_merchant_credit (10w) | R | `iran_merchant_credit` (dead), +50 PP, 266 +1 slot +1 industrial complex | duplicates `IR1_domestic_workshops` (same state, same building) | `set_country_flag = iran_merchant_credit add_political_power = constant:iran_story.political_capital add_to_variable = { iran_foreign_leverage = constant:iran_story.leverage_loss } 417 = { add_extra_state_shared_building_slots = constant:iran_story.project_slots add_building_construction = { type = industrial_complex level = 1 instant_build = yes } }` |
| IR1_tabriz_workshops (10w) | F | 419 +1 slot +1 industrial complex, `iran_concede_northern_small`, `iran_tabriz_workshops` (dead) | — | — |
| IR1_divided_command (5w) | F | `iran_security_programme`, +25 army XP, +25 command power | — | — |
| IR1_swedish_officers (10w) | C | `iran_gendarmerie_tradition`, `PER_swedish_gendarmerie`, +8 sovereignty, +25 XP, +10% WS | 10 weeks for XP/WS/sovereignty; no Swedish officer corps is modelled | `set_country_flag = iran_gendarmerie_tradition set_country_flag = PER_swedish_gendarmerie if = { limit = { NOT = { has_idea = iran_foreign_military_mission } } add_ideas = iran_foreign_military_mission } add_manpower = constant:iran_story.gendarmerie_manpower add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_cossack_command (10w) | C | `iran_cossack_tradition`, `PER_cossack_brigade`, +25 XP, +10% WS | same shape as the Swedish focus; neither changes the army | `set_country_flag = iran_cossack_tradition set_country_flag = PER_cossack_brigade add_manpower = constant:iran_story.tribal_manpower add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } army_experience = constant:iran_story.army_experience` |
| IR1_gendarmerie_recruitment (7w) | F | +5000 manpower, `iran_gendarmerie_recruits`, +10% WS | — | — |
| IR1_cossack_pay (7w) | F | `iran_cossack_paid`, `iran_concede_northern_small`, +500 equipment (RUS), +25 command power | stated trade, works | — |
| IR1_officers_college (10w) | F | Gate (`iran_gendarmerie_ready`): `iran_professional_officers`, `iran_reserve_programme`, +25 XP, +1 research slot | — | — |
| IR1_frontier_posts (10w) | C | `iran_build_frontier_posts` (1 bunker in 419, once), +25 XP, +10% WS, +10 authority | one bunker for 10 weeks | `iran_build_frontier_posts = yes 419 = { add_building_construction = { type = bunker level = 1 instant_build = yes } } 420 = { add_building_construction = { type = bunker level = 1 instant_build = yes } } add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.security_equipment } army_experience = constant:iran_story.army_experience add_war_support = constant:iran_story.war_support_gain` |
| IR1_tehran_arsenal (10w) | F | `iran_build_tehran_arsenal` (266: +1 slot, +1 arms factory, once), +25 XP, +500 equipment | — | — |
| IR1_tribal_levies (7w) | F | +8000 manpower, `iran_tribal_levies`, +10% WS | — | — |
| IR1_rifle_contracts (7w) | C | +1000 equipment, `iran_rifle_contracts` (dead) | one line; no production or supplier effect | `add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_grant } set_country_flag = iran_rifle_contracts set_country_flag = iran_arsenal_programme` (opens the repeatable `iran_expand_arsenal` decision) |
| IR1_national_gendarmerie (10w) | F | Majlis push small, `iran_national_gendarmerie`, +10 authority, +25 XP, +10% WS | — | — |
| IR1_azerbaijan_command (7w) | F | +8000 manpower, crown push small, 419 bunker, `iran_azerbaijan_command` | — | — |
| IR1_south_persia_rifles (7w) | F | 412 bunker, +500 equipment (ENG), `iran_concede_british_small`, `iran_south_persia_rifles` (dead), +25 opinion ENG | the stated cost is real; AI weight 0 | — |
| IR1_military_finance (7w) | C | `iran_military_finance` (dead), +50 PP, +500 equipment | no budget is modelled | `set_country_flag = iran_military_finance set_country_flag = iran_arsenal_programme add_political_power = constant:iran_story.political_capital add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_small }` |
| IR1_air_detachment (7w) | C | `iran_concede_leading_small`, +25 air XP, `iran_air_programme` (opens `iran_tehran_airfield`), +10% WS | air XP is nearly worthless (no planes, no air techs in 1910); only the flag pays | `iran_concede_leading_small = yes set_country_flag = iran_air_programme 266 = { add_building_construction = { type = air_base level = 1 instant_build = yes } } add_war_support = constant:iran_story.war_support_gain` |
| IR1_army_of_the_constitution (10w) | F | Majlis push small, `iran_constitutional_army`, +10 authority, +5% stability, +25 XP | — | — |
| IR1_army_of_the_crown (10w) | F | Crown push small, `iran_royal_army`, +20 authority, +10% WS, +25 command power | AI weight 0 blocks `IR1_gulf_flotilla` behind it | — |
| IR1_reserve_service (10w) | F | `iran_reserve_established`, +10000 manpower, +10% WS | — | — |
| IR1_gulf_flotilla (10w) | B | **411 dockyard**, +25 navy XP, `iran_gulf_flotilla` (dead) | 411 is landlocked → no dockyard; the entire focus delivers 25 navy XP | `set_country_flag = iran_gulf_flotilla 412 = { add_building_construction = { type = dockyard level = 1 instant_build = yes } } navy_experience = constant:iran_story.navy_experience set_country_flag = iran_gulf_priority` |
| IR1_wartime_mobilization (5w) | F | `iran_mobilized`, +10% WS, +25 XP, event .19 (real choice) | — | — |
| IR1_gendarmerie_resistance (7w) | C | `iran_gendarme_resistance`, +500 equipment, +10% WS | one equipment line and war support for 7 weeks | `set_country_flag = iran_gendarme_resistance set_country_flag = iran_security_programme add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.security_equipment } add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } add_war_support = constant:iran_story.war_support_gain` |
| IR1_officer_loyalty (7w) | B | `set_country_flag = iran_officer_loyalty` — a **flag** named like the variable — plus +5% stability, +25 command power, +50 PP | the `iran_officer_loyalty` **variable** (read by `iran_coup_1921`, `iran_loyal_officer_corps`, `iran_refresh_mechanics` < 40 penalty) is never changed; the focus does nothing for the officers | `add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } set_country_flag = iran_officer_loyalty_confirmed add_stability = constant:iran_story.stability_gain add_command_power = constant:iran_story.command_power hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_between_empires (5w) | F | `iran_foreign_programme` (opens the sovereignty decision category), event .13, +50 PP, +25 command power, stability | — | — |
| IR1_guarded_neutrality (5w) | C | `iran_armed_neutrality`, `PER_neutral_1914`, +10% WS, +5% stability | both flags only feed `iran_path_armed_neutrality`; nothing changes in play | `PER_bop_push_crown_small = yes set_country_flag = iran_armed_neutrality set_country_flag = PER_neutral_1914 add_war_support = constant:iran_story.war_support_gain add_to_variable = { iran_authority = constant:iran_story.authority_gain } hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_entente_understanding (5w) | F | `iran_foreign_paths` +1 (dead), event .14 (500 equipment + leverage), +500 equipment ENG, `iran_concede_british_small`, opinion | 6-line tooltip; `iran_foreign_paths` is read only by `iran_path_foreign_count`, which nothing uses | — |
| IR1_german_opening (5w) | F | `iran_foreign_paths` +1 (dead), `iran_third_power` (read by `iran_great_game` decisions + `iran_path_germany`), event .15, 500 equipment GER, opinion, +50 PP | AI weight 0 | — |
| IR1_british_loan (7w) | F | +500 equipment ENG, `iran_concede_british_large` (−6 sovereignty, +15 British influence, +10 leverage), `iran_british_credit` | works, but the price (a large concession, i.e. two sovereignty bands) is much steeper than the 500 rifles | — (rebalance cost, no structural fix needed) |
| IR1_russian_understanding (7w) | I | `iran_foreign_paths` +1 (dead), `iran_russian_understanding`, +50 PP, +25 opinion RUS/SOV | 7 weeks for PP and an opinion modifier; the understanding changes nothing | `set_country_flag = iran_russian_understanding add_to_variable = { iran_northern_standing = constant:iran_story.negotiation_standing_grant } add_to_variable = { iran_foreign_leverage = constant:iran_story.leverage_gain } if = { limit = { country_exists = RUS } add_opinion_modifier = { target = RUS modifier = iran_treaty_relations } } 419 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` |
| IR1_ottoman_frontier (7w) | I | `iran_ottoman_frontier`, +25 army XP, +25 opinion TUR | 25 XP and an opinion modifier; and the flag *removes* `iran_path_intact` downstream | `set_country_flag = iran_ottoman_frontier 419 = { add_building_construction = { type = bunker level = 1 instant_build = yes } } army_experience = constant:iran_story.army_experience add_war_support = constant:iran_story.war_support_gain if = { limit = { country_exists = TUR } add_opinion_modifier = { target = TUR modifier = iran_treaty_relations } }` |
| IR1_niedermayer_expedition (7w) | F | `iran_niedermayer`, `iran_concede_german_small`, +10% WS, +500 equipment GER, opinion | AI weight 0 | — |
| IR1_neutrality_declaration (5w) | F | `iran_neutrality_declared`, +10% stability, +50 PP, event .27 (real choice with transit costs) | — | — |
| IR1_south_persia_oil (10w) | R | `iran_oil_programme`, `iran_british_oil_interest`, 413 +10 oil, `iran_concede_british_small`, opinion | duplicates `IR1_abadan_concession` (same flag, same +10 oil in 413, same concession); both are reachable in one run | delete (leaf of `IR1_british_loan`; the branch connects without it) or differentiate: `set_country_flag = iran_oil_programme 413 = { add_resource = { type = oil amount = 5 } } 411 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } } if = { limit = { NOT = { has_idea = iran_oil_revenue_dividend } } add_timed_idea = { idea = iran_oil_revenue_dividend days = 1825 } } iran_concede_british_small = yes` |
| IR1_tribal_frontier_pact (7w) | F | `iran_tribal_frontier`, +8000 manpower, +5% stability | — | — |
| IR1_protect_the_harvest (10w) | M | `iran_relief_programme` (dead pre-1939), event .16 whose `immediate` **adds `iran_supply_emergency`** (−15% stability, −15% IC), +5% stability, +5000 manpower, +50 PP | a "protect the harvest" focus that permanently cripples industry and stability; the player is not warned | `set_country_flag = iran_relief_programme add_manpower = constant:iran_story.reserve_manpower add_stability = constant:iran_story.stability_gain add_political_power = constant:iran_story.political_capital if = { limit = { NOT = { has_country_flag = iran_relief_event_seen } } set_country_flag = iran_relief_event_seen country_event = { id = iran_campaign.16 } }` and delete `add_ideas = iran_supply_emergency` from `iran_campaign.16`'s `immediate` |
| IR1_caspian_communications (10w) | F | `iran_construction_programme`, `iran_caspian_priority`, 420 +1 infrastructure, +500 equipment | — | — |
| IR1_gulf_lifeline (10w) | F | `iran_construction_programme`, `iran_gulf_priority`, 411 +1 infrastructure, +25 navy XP | infrastructure is buildable in 411 (only naval bases are not) | — |
| IR1_refugee_administration (7w) | C | `iran_refugee_administration`, +5% stability, 419 +1 infrastructure | the flag only feeds the unused `iran_path_humiliated` and *disables* `iran_path_intact` — taking it is mildly negative downstream | `set_country_flag = iran_refugee_administration add_stability = constant:iran_story.stability_gain add_manpower = constant:iran_story.gendarmerie_manpower 419 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` and drop `iran_refugee_administration` from `iran_path_intact`'s NOT-list |
| IR1_foreign_advisers (7w) | R | `iran_foreign_advisers` (dead), +1 research slot, +50 PP | second research-slot focus in the chapter (after `IR1_belgian_advisers`); flag is dead | `set_country_flag = iran_foreign_advisers if = { limit = { NOT = { has_idea = iran_foreign_military_mission } } add_ideas = iran_foreign_military_mission } add_political_power = constant:iran_story.political_capital add_to_variable = { iran_authority = constant:iran_story.authority_gain }` (or delete: leaf, branch connects without it) |
| IR1_independence_at_the_peace (10w) | B | `iran_independence_claim` (dead), +10 authority, +50 PP, stability | `available` needs `iran_relief_delivered`, unobtainable before 1939 → **focus can never be taken**; gates 3 more focuses | `available = { date > 1917.1.1 has_country_flag = iran_relief_programme }` and reward `set_country_flag = iran_independence_claim iran_reclaim_leading_small = yes add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } add_political_power = constant:iran_story.political_capital hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_jangali_movement (7w) | I | `iran_jangali_rising` (dead), +10% WS, +25 XP | the movement is never modelled and its flag is read nowhere | `set_country_flag = iran_jangali_rising 420 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } } add_to_variable = { iran_socialist_support = constant:iran_story.socialist_support_gain } iran_reclaim_british_small = yes add_war_support = constant:iran_story.war_support_gain` |
| IR1_gilan_congress (10w) | C | `iran_jangali_congress` (read by `IR2`-era socialist gate), +15 socialist support, `iran_reclaim_british_small`, +10% WS, event f1.2 (+15 support) | reaches 30 of the 50 support the interwar socialist focus needs, so the route dies one step short | `set_country_flag = iran_jangali_congress add_to_variable = { iran_socialist_support = constant:iran_story.socialist_support_gain } add_to_variable = { iran_socialist_support = constant:iran_story.socialist_support_gain } PER_bop_push_majlis = yes iran_reclaim_british_small = yes country_event = { id = iran_f1.2 } hidden_effect = { iran_refresh_mechanics = yes }` (30 + 15 event + 15 from `jangali_movement` = 60 > 50) |
| IR1_tabriz_consulates (7w) | C | `iran_reclaim_northern_small`, `iran_consular_service` (dead), +50 PP, stability | the consulates are not modelled | `iran_reclaim_northern_small = yes set_country_flag = iran_consular_service add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } if = { limit = { country_exists = RUS } add_opinion_modifier = { target = RUS modifier = iran_treaty_relations } } 419 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` |
| IR1_hague_appeal (7w) | B | `iran_hague_appeal`, +5% stability, +50 PP, text tooltip | unreachable (prerequisite `IR1_independence_at_the_peace`) | fix the gate above; then `PER_bop_push_majlis_small = yes add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } set_country_flag = iran_hague_appeal add_stability = constant:iran_story.stability_gain hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_armistice_watch (5w) | B | `iran_armistice_watch` (dead), +50 PP, event .28, stability | unreachable | fix the gate; then `set_country_flag = iran_armistice_watch add_political_power = constant:iran_story.political_capital country_event = { id = iran_campaign.28 } PER_bop_pull_to_centre = yes` |
| IR1_persia_at_the_conference (14w) | B | `iran_paris_conference` (opens `iran_paris_memorandum`), `iran_reclaim_leading_large`, Majlis push small, +20 authority, +8 sovereignty, stability, +50 PP, conditional removal of `iran_foreign_customs_administration`, event .29 | unreachable — the chapter's only `@grand` capstone and its decision are dead content; also the longest tooltip in the tree (9 lines) | fix the gate; then keep the reward and wrap the variable lines: `set_country_flag = iran_paris_conference iran_reclaim_leading_large = yes PER_bop_push_majlis_small = yes add_to_variable = { iran_authority = constant:iran_story.authority_major_gain } add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } add_political_power = constant:iran_story.political_capital if = { limit = { has_idea = iran_foreign_customs_administration } remove_ideas = iran_foreign_customs_administration } country_event = { id = iran_campaign.29 } hidden_effect = { iran_refresh_mechanics = yes }` |
| IR1_russian_ultimatum_1911 (5w) | F | Crown push small, `iran_russian_ultimatum` (dead), `iran_concede_northern_small`, −10 authority, −5% stability, `iran_refresh_mechanics` | a working cost focus; calls the refresh unhidden (inconsistent but harmless after the body was hidden) | — |
| IR1_dismissal_of_shuster (5w) | F | Crown push, `iran_shuster_dismissed` (dead), −10 authority, `iran_concede_northern_large`, +10% WS, −5% stability | works as a humiliation beat; both flags dead | — |
| IR1_provincial_tax_risings (5w) | I | `iran_tax_risings` (dead), +10 authority, −5% stability, 250 equipment | net value ≈ 250 rifles for 5 weeks and a stability hit; the rising is not modelled | `set_country_flag = iran_tax_risings add_to_variable = { iran_authority = constant:iran_story.authority_gain } add_stability = constant:iran_story.stability_cost add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.security_equipment } 417 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` (or delete: leaf) |

## (a) Ideas referenced by focus rewards

Only three ideas are added or removed directly by this file, and all three exist in
`common/ideas/iran_campaign.txt` with `allowed = { original_tag = PER }`, so none is a broken reference.

| idea | defined? | added by | removed by | can Iran hold it on each route here? |
| --- | --- | --- | --- | --- |
| `iran_supply_emergency` (−15% stability, −15% IC) | yes (`iran_campaign.txt:75`) | `IR1_the_great_famine`; `iran_campaign.16` `immediate` (fired by `IR1_the_great_famine` and `IR1_protect_the_harvest`) | `iran_bread_distribution` decision (visible only after **1939.9.1**); `iran_ww2` focuses | yes, on every route — and that is the problem: once added in 1916 it cannot be removed before the chapter ends |
| `iran_wartime_economy` (−5% consumer goods) | yes (`:68`) | `IR1_wartime_budget` via `add_timed_idea days = 730` | auto-expiry after 730 days; nowhere else | yes, all routes |
| `iran_foreign_customs_administration` | yes (`:195`) | `iran_foreign_agreements` decision only (never by this chapter) | `IR1_persia_at_the_conference`, guarded by `has_idea` | no route in this chapter ever grants it, so the conditional removal never fires (harmless, but dead code until the focus is made reachable) |

Ideas added/removed **indirectly** through `iran_refresh_mechanics` (the state-spirit family). This is the
only mechanism by which the 15–20 authority focuses pay off, so it is listed for completeness:

| idea family | added by | removed by |
| --- | --- | --- |
| `iran_fragmented_authority` / `iran_constitutional_state` | `iran_refresh_mechanics` (authority ≥ 65 → constitutional, else fragmented) | `iran_refresh_mechanics` (strips all of them first) |
| `iran_qajar_state` / `iran_socialist_state` / `iran_nationalist_state` / `iran_pahlavi_state` / `iran_parliamentary_state` + their `_consolidated` twins | `iran_refresh_mechanics`, keyed on `iran_qajar_restoration`, `iran_socialist`, `iran_nationalist_front`, `iran_pahlavi`, `iran_republic` (+ `_settled` flags set by `iran_settle_*`, all 1919+) | same |
| `iran_foreign_dependence` | `iran_refresh_mechanics` when `iran_foreign_leverage ≥ 40` (opening value is 60, so Iran starts with it) | `iran_refresh_mechanics` when leverage < 40 |
| `iran_british_preference` / `iran_soviet_preference` / `iran_balancing_powers` | `iran_refresh_mechanics` from `iran_*_standing` ≥ 60 / 45 | same |
| `iran_sovereignty_capitulations` / `_constrained` / `_assertive` / `_sovereign` | `iran_influence_tick` (monthly) at 25 / 50 / 75 thresholds | same |
| `iran_divided_officer_corps` | `iran_refresh_mechanics` when `iran_officer_loyalty < 40` **and** `date > 1918.12.31` | same (so it can never appear in this chapter) |

No idea is removed that Iran cannot possess, except `iran_foreign_customs_administration`, which is guarded.

## (b) Focus tooltips likely to be long

Counted after expansion, excluding `hidden_effect`, `set_country_flag` (no tooltip in HOI4) and
`mark_focus_tree_layout_dirty`.

| focus | visible lines | why |
| --- | --- | --- |
| `IR1_persia_at_the_conference` | 9 | reclaim + BOP + 2 variables + stability + PP + remove_ideas + event |
| `IR1_russian_understanding` | 6 | variable + PP + 2 conditional opinions (+ the dead `iran_foreign_paths` line) |
| `IR1_german_opening` | 6 | variable + event + equipment + opinion + PP |
| `IR1_entente_understanding` | 6 | variable + event + equipment + concession + opinion |

No focus exceeds 6 lines apart from the capstone, so the lead's `iran_refresh_mechanics` fix removed the
real tooltip bloat. Two residual presentation problems remain:

- **Unlocalised variable lines.** 28 rewards write a variable and only `iran_sovereignty` has a loc key, so
  `add_to_variable = { iran_authority = 10 }` renders as `iran_authority: 10` in every language.
  Fix: add `iran_authority`, `iran_foreign_paths`, `iran_socialist_support` loc keys, or wrap each in
  `hidden_effect` plus a `custom_effect_tooltip`.
- **Three focuses call `iran_refresh_mechanics` without `hidden_effect`**: `IR1_russian_ultimatum_1911`,
  `IR1_dismissal_of_shuster`, `IR1_provincial_tax_risings`. Harmless now that the body is hidden, but any
  future un-hiding of that effect will dump 13 spirit removals into exactly these tooltips.

## (c) AI value

Every focus has `ai_will_do` (none missing). Thirteen are hard-zeroed for a historical-focus AI, and because
several of them are the only doors into a branch, the AI can never see that branch's content:

| focus | factor | consequence |
| --- | --- | --- |
| `IR1_court_patronage` | 0 (historical) | the entire court branch (`bakhtiari_bargain`, `royal_household`, `palace_guard`) is unreachable for a historical AI |
| `IR1_royal_household`, `IR1_palace_guard`, `IR1_court_and_cabinet`, `IR1_royal_prerogative` | 0 (historical) | same branch; `IR1_court_and_cabinet` also closes the crown side of the 1918 assembly |
| `IR1_defend_constitution` | 0 (historical) | historical AI takes only `IR1_majlis_budget_authority` out of `IR1_constitution_or_crown` |
| `IR1_army_of_the_crown` | 0 (historical) | **`IR1_gulf_flotilla` requires it, so the navy branch is dead for a historical AI** (no bypass exists) |
| `IR1_south_persia_rifles` | 0 (historical) | ok — `IR1_army_of_the_crown`'s OR-prerequisite is still met by `IR1_military_finance` |
| `IR1_republican_committee` | 0 (historical) | the republic decision seed is never taken by AI |
| `IR1_german_opening`, `IR1_niedermayer_expedition` | 0 (historical) | the German path only ever opens through `IR1_third_power` from another chapter |
| `IR1_jangali_movement`, `IR1_gilan_congress` | 0 (historical) | the Gilan/socialist seed is never taken by AI, so `iran_socialist_support` never reaches 50 |
| `IR1_constitution_or_crown` | priority 50 | AI takes it, then `custom_effect_tooltip`-only reward — AI pays 10 weeks for PP |
| `IR1_protect_the_harvest` | priority 50 | AI takes it and eats `iran_supply_emergency` (−15% IC and stability) for the rest of the campaign; this is the single worst AI-facing bug in the file |
| `IR1_the_great_famine` | priority 50 | same penalty, guaranteed by weight |
| `IR1_independence_at_the_peace` | priority 50 | AI never gets it (`available` always false) — dead weight in the AI's focus pool |

Real deadlock: none of the branches is mutually blocking, but two structural gaps behave like deadlocks —
(a) the 1917–19 diplomacy chain is unreachable for player and AI alike, and (b) `IR1_gulf_flotilla` sits behind
a historical-zero focus with no `bypass`, so a historical AI Iran never builds a navy. The file contains **no
`bypass` blocks at all**, which is why a failed `available` (e.g. `IR1_british_loan` after an Anglo-Iranian war,
`IR1_german_opening` if GER is gone) silently removes content instead of routing around it.

## Removal candidates (branch still connects without them)

`IR1_south_persia_oil` (leaf of `IR1_british_loan`), `IR1_foreign_advisers` (leaf of `IR1_protect_the_harvest`),
`IR1_agricultural_relief` (leaf of `IR1_state_bank`), `IR1_provincial_tax_risings` (leaf of
`IR1_anjoman_elections`). `IR1_merchant_credit` must **not** be deleted — `IR1_tabriz_workshops` requires it —
so it is differentiated instead.
