# Iran 1936-1945: reward audit of every focus in `common/national_focus/iran_ww2.txt`

Audit of all 99 focuses defined in `iran_ww2.txt` (the tree's 100th entry is the shared focus
`SSB_the_saadabad_pact`, which lives in `goe_shared_saadabad_branch.txt` and is out of scope here).
Read-only pass: no script was changed. Every reward was expanded by hand against the scripted effects,
triggers, ideas, decisions and events it calls; every flag it sets was grepped across `common/`, `events/`
and `history/` for a reader; every idea was checked against `common/ideas/`; every state against
`history/states/`.

## Counts

| class | focuses |
|---|---|
| FUNCTIONAL | 65 |
| CONDITIONAL-MEANINGFUL | 7 |
| INEFFECTIVE | 20 |
| BROKEN | 0 |
| MISLEADING | 7 |
| REDUNDANT | 0 |
| **total** | **99** |

No focus is BROKEN in the strict sense (no wrong scope, no missing idea, no building in a state Iran
does not own - states 266, 410-413, 417-421 are all `owner = PER`). The only branch that is broken in
effect is the socialist one: its four focuses are unreachable from a fresh 1936 bookmark because the decision
that opens the branch needs support the branch itself produces (section E.6). They are filed
CONDITIONAL-MEANINGFUL with that note rather than BROKEN, because a campaign carried over from 1919 can
still take them. No focus is REDUNDANT: every one of the 99 is on a live path (the tree is a
ladder, not a lattice) - the duplications found are duplicate *flags*, not duplicate focuses.

## Rubric used

- **FUNCTIONAL** - produces a durable, observable change: a building, a resource, manpower, equipment,
  a research slot, an idea, a variable some other script reads, a flag that opens a decision, or an event
  whose options branch.
- **CONDITIONAL-MEANINGFUL** - the durable part lands only on some routes, dates or flags (Majlis/Crown
  shifts that are inert under Pahlavi or without *Arms Against Tyranny*; `iran_occupied` gates;
  `iran_resistance` gates).
- **INEFFECTIVE** - the reward reduces to political power, stability, experience or command power plus
  flags nothing reads. The player pays 25-70 days and sees a number move for a week.
- **MISLEADING** - the title and description promise something the reward does not do (a water scheme
  that builds nothing, a brigade with no vehicles, a Zagros line built in Tehran).
- **BROKEN** - an effect that cannot work as written.
- **REDUNDANT** - the branch still connects without the focus.

In the proposal column `;` separates lines of the effect block, so a cell can be pasted into
`completion_reward = { ... }` with one newline per `;`. Every proposal is built from mechanics that
already exist in the mod (constants, Great Game acts, Crown/Majlis pushes, variables the campaign reads,
flags a decision already tests, buildings in states Iran owns), and is guarded so no line appears in a
tooltip where it does nothing. No proposal adds a new focus; the two proposals that would need a new
national spirit are quarantined in section G.

## Per-focus table

### Politics - the state and its succession

| id | class | what it actually does | problem | proposed reward |
|---|---|---|---|---|
| `IR3_inheritance_of_the_state` | INEFFECTIVE | iran_campaign.31 (its only option re-runs iran_refresh_mechanics, no payload); flags iran_security_programme + iran_treasury_programme; 50 pp; +5% stability | Both flags are already set by iran_initialize_campaign on a 1936 start (history/countries + scripted_effects), so the focus grants nothing but pp and stability; the event is empty | country_event = { id = iran_campaign.31 }; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain }; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_provincial_compacts` | CONDITIONAL-MEANINGFUL | iran_constitutional_programme (opens iran_constitutional_petitions decision, +ai_chance in iran_f3.1); iran_provincial_compact (already set at start; also opens iran_tribal_regiment); iran_civil_service (already set at start); +10% stability; 50 pp; PER_bop_push_majlis (+0.20) | 2 of 3 flags duplicate the 1936 start; the Majlis push does nothing while Iran is Pahlavi and before the 1941 resurgence, and nothing at all without Arms Against Tyranny | set_country_flag = iran_constitutional_programme; add_stability = constant:iran_story.stability_major_gain; add_political_power = constant:iran_story.political_capital; if = { limit = { has_power_balance = { id = PER_crown_and_majlis } } PER_bop_push_majlis = yes } else = { add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } }; if = { limit = { NOT = { has_country_flag = iran_provincial_compact } } set_country_flag = iran_provincial_compact } |
| `IR3_direct_administration` | CONDITIONAL-MEANINGFUL | iran_centralizing_programme (opens repeatable iran_provincial_security decision, +20 authority each); iran_civil_service (already set); +20 authority; -5% stability; 50 pp; PER_bop_push_crown (-0.20) | Authority is only read by the 65-point reform threshold in iran_refresh_mechanics, which the Pahlavi branch bypasses, so +20 authority is invisible on the only route that can take the focus early; the Crown push is inert under Pahlavi | set_country_flag = iran_centralizing_programme; add_stability = constant:iran_story.stability_cost; add_political_power = constant:iran_story.political_capital; if = { limit = { has_power_balance = { id = PER_crown_and_majlis } } PER_bop_push_crown = yes } else = { add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } }; add_to_variable = { iran_authority = constant:iran_story.authority_major_gain }; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_name_of_the_nation` | MISLEADING | flag iran_named_iran (0 readers anywhere); 50 pp; +5% stability; iran_campaign.33 (option sets iran_name_adopted, also 0 readers) | The description promises that the renaming changes how the powers deal with Iran; nothing changes - no country-name localisation switch, no decision, no variable. Two write-only flags and a pp/stability trickle | country_event = { id = iran_campaign.33 }; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain }; if = { limit = { country_exists = ENG } add_opinion_modifier = { target = ENG modifier = iran_treaty_relations } }; if = { limit = { country_exists = SOV } add_opinion_modifier = { target = SOV modifier = iran_treaty_relations } } |
| `IR3_public_granaries` | CONDITIONAL-MEANINGFUL | iran_relief_programme (opens iran_bread_distribution decision); +5% stability; 50 pp; 8000 manpower; ai_will_do x5 if has_idea iran_supply_emergency | The ai modifier tests an idea Iran can never have on a 1936 start (only the 1910-18 tree grants iran_supply_emergency), so it never fires; the bread decision is visible anyway once at war or occupied | set_country_flag = iran_relief_programme; add_stability = constant:iran_story.stability_major_gain; add_political_power = constant:iran_story.political_capital; add_manpower = constant:iran_story.tribal_manpower; if = { limit = { has_idea = iran_supply_emergency } remove_ideas = iran_supply_emergency }; 266 = { add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } |
| `IR3_a_country_at_work` | INEFFECTIVE | flag iran_budget_established (already set at start; only read by iran_path_treasury); remove_ideas = iran_supply_emergency; +10 authority; hidden refresh | Iran cannot hold iran_supply_emergency on a 1936 start, so remove_ideas removes nothing and the focus shows an empty tooltip; authority is inert under Pahlavi. The whole reward is one pre-set flag | add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; if = { limit = { has_idea = iran_supply_emergency } remove_ideas = iran_supply_emergency }; 266 = { add_extra_state_shared_building_slots = constant:iran_story.project_slots; add_building_construction = { type = industrial_complex level = 1 instant_build = yes } }; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_wartime_government` | INEFFECTIVE | flag iran_wartime_government (0 readers); 50 pp; +5% stability; iran_campaign.34 sets iran_wartime_cabinet or iran_wartime_majlis_cabinet (both 0 readers) | Every flag in the chain is write-only, so the cabinet reorganization has no mechanical existence; pp and stability only | country_event = { id = iran_campaign.34 }; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_command_power = constant:iran_story.command_power; if = { limit = { has_power_balance = { id = PER_crown_and_majlis } } PER_bop_push_crown_small = yes } else = { add_war_support = constant:iran_story.war_support_gain } |
| `IR3_succession_crisis` | CONDITIONAL-MEANINGFUL | flag iran_succession_question, which is one of the three keys of iran_political_question_republic (the only way into the republican branch); 50 pp; +5% stability; iran_campaign.35 (flags write-only) | The focus is load-bearing only as the republic gate - the pp/stability and the event flags do nothing; the 35 options set iran_succession_prepared / _managed which nothing reads | set_country_flag = iran_succession_question; country_event = { id = iran_campaign.35 }; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; mark_focus_tree_layout_dirty = yes |
| `IR3_mohammad_reza` | INEFFECTIVE | flag iran_mohammad_reza (0 readers); promote_character = PER_mohammed_reza_pahlavi; -5% stability; 50 pp | PER_mohammed_reza_pahlavi is defined only as a theorist advisor in common/characters/PER.txt, so promoting him changes no leader and no minister slot; the only real effect is the stability cost | if = { limit = { has_character = PER_mohammed_reza_pahlavi } recruit_character = PER_mohammed_reza_pahlavi }; add_stability = constant:iran_story.stability_cost; add_political_power = constant:iran_story.political_capital; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; set_country_flag = iran_mohammad_reza |
| `IR3_wartime_regency` | CONDITIONAL-MEANINGFUL | PER_bop_push_crown_small (-0.10); flag iran_wartime_regency (0 readers); +10% stability; +10 authority; refresh; 50 pp | Only the Crown shift is real, and only for a Qajar or constitutional Iran (the AI weight is 0 under Pahlavi, where the shift would be inert anyway) | PER_bop_push_crown_small = yes; set_country_flag = iran_wartime_regency; add_stability = constant:iran_story.stability_major_gain; add_to_variable = { iran_authority = constant:iran_story.authority_gain }; if = { limit = { NOT = { has_power_balance = { id = PER_crown_and_majlis } } } add_stability = constant:iran_story.stability_gain }; add_political_power = constant:iran_story.political_capital; iran_refresh_mechanics = yes |
| `IR3_the_route_we_keep` | INEFFECTIVE | 50 pp; custom_effect_tooltip iran_wartime_route_tt; layout dirty; +5% stability | The hub that unlocks all six regime branches pays only pp and stability - it is structural, not rewarding; the tooltip is the only content | add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_command_power = constant:iran_story.command_power; custom_effect_tooltip = iran_wartime_route_tt; mark_focus_tree_layout_dirty = yes |

### Politics - occupation and the six regime continuations

| id | class | what it actually does | problem | proposed reward |
|---|---|---|---|---|
| `IR3_occupation_government` | CONDITIONAL-MEANINGFUL | needs iran_occupied; flag iran_occupation_administration (0 readers); -5% stability; -10 authority; 50 pp; iran_concede_british_small + iran_concede_northern_small (-6 sovereignty, +16 influence, +20 leverage) | The concession mechanics carry the focus and they work; the authority loss is invisible under Pahlavi and the flag is dead, so the cost side reads weaker than it is | set_country_flag = iran_occupation_administration; add_stability = constant:iran_story.stability_cost; add_political_power = constant:iran_story.political_capital; iran_concede_british_small = yes; if = { limit = { country_exists = SOV } iran_concede_northern_small = yes }; set_country_flag = iran_resistance; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_resistance_council` | CONDITIONAL-MEANINGFUL | needs iran_occupied; flag iran_resistance_council (0 readers); +10% war support; 5000 manpower; +5 sovereignty | The council cannot be used to reach the resistance branch: iran_resistance is only ever set by option b of iran_campaign.40, so a player who answered the ultimatum with cooperation can never take IR3_national_resistance; 5000 manpower is trivial | set_country_flag = iran_resistance_council; set_country_flag = iran_resistance; add_war_support = constant:iran_story.war_support_gain; add_manpower = constant:iran_story.gendarmerie_manpower; add_to_variable = { iran_sovereignty = 5 }; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } |
| `IR3_pahlavi_progress` | INEFFECTIVE | flag iran_pahlavi_progress (0 readers); +10 authority; +5% stability; refresh; 50 pp | On the only route that can take it (allow_branch iran_pahlavi) authority is never read and the balance does not exist, so the entire reward is 50 pp and 5% stability | set_country_flag = iran_pahlavi_progress; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; if = { limit = { has_country_flag = iran_pahlavi_settled } add_stability = constant:iran_story.stability_gain } |
| `IR3_royal_army` | INEFFECTIVE | flag iran_royal_army_1940 (0 readers); 25 army xp; 25 command power; +10% war support | 25 xp is about two weeks of one division exercising - no equipment, no manpower, so the rebuilt army never appears | set_country_flag = iran_royal_army_1940; army_experience = constant:iran_story.army_experience; add_command_power = constant:iran_story.command_power; add_war_support = constant:iran_story.war_support_gain; add_manpower = constant:iran_story.reserve_manpower; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } |
| `IR3_development_corps` | FUNCTIONAL | 1 civilian factory + 1 shared slot in state 266 (Tehran, owned) | Fine; the flag iran_development_corps is dead but the building is real | no change |
| `IR3_pahlavi_1945` | INEFFECTIVE | flag iran_pahlavi_enduring (no such idea exists; 0 readers); +10% stability; 50 pp; iran_reclaim_leading_small (-8 influence of the leading patron, +4 sovereignty, -10 leverage) | This is the only one of the six 1945 capstones that grants no end-state spirit - the flag is named like an idea that was never written, so a Pahlavi run reaches 1945 with nothing the other five routes get | set_country_flag = iran_pahlavi_enduring; add_stability = constant:iran_story.stability_major_gain; add_political_power = constant:iran_story.political_capital; iran_reclaim_leading_small = yes; set_country_flag = iran_pahlavi_settled; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_constitutional_wartime` | FUNCTIONAL | PER_bop_push_majlis_small (+0.10); flag iran_constitutional_wartime (0 readers); +5% stability; 50 pp | Thin - balance shift plus pp/stability only - but the shift is live on this route (a non-Pahlavi regime creates the balance) and three of these move the Majlis spirit tier | no change (optional: drop the dead flag) |
| `IR3_wartime_majlis` | FUNCTIONAL | PER_bop_push_majlis (+0.20); flag iran_wartime_majlis (0 readers); +5% stability; +10 authority; refresh; 50 pp | Fine on this route; authority still inert | no change |
| `IR3_cabinet_stability` | FUNCTIONAL | flag iran_cabinet_stability (0 readers); +10% stability; 50 pp; PER_bop_push_majlis (+0.20) | Fine; flag dead | no change |
| `IR3_constitutional_1945` | FUNCTIONAL | strips the six end-state ideas, add_ideas iran_constitutional_enduring (exists: +10% stability, +10% pp); +10% stability; +10 authority; refresh; 50 pp; PER_bop_push_majlis | Tooltip is at the 6-line edge and the flag iran_constitutional_enduring duplicates the idea name | no change |
| `IR3_republic_wartime` | FUNCTIONAL | PER_bop_push_majlis (+0.20); flag iran_republic_wartime (0 readers); +5% stability; 50 pp | Thin but live | no change |
| `IR3_republican_defence` | FUNCTIONAL | flag iran_republican_defence (0 readers); 10000 manpower; 1 bunker in state 412 (Fars, owned) | A citizens militia that builds its bunker in Fars rather than on a frontier; manpower only | no change (optional: move the bunker to state 419 Azerbaijan) |
| `IR3_civil_defence` | FUNCTIONAL | flag iran_civil_defence (0 readers); +10% stability; +10% war support; PER_bop_push_majlis (+0.20) | Thin: the air-raid organization is abstracted into stability and a Majlis shift, with no building | no change |
| `IR3_republic_1945` | FUNCTIONAL | strips six ideas, add_ideas iran_republic_enduring (exists: +15% pp, +5% research); +10% stability; 50 pp; +1 research slot | Fine | no change |
| `IR3_court_wartime` | FUNCTIONAL | PER_bop_push_crown_small (-0.10); flag iran_court_wartime (0 readers); +10 authority; +5% stability; refresh; 50 pp | Fine on the Qajar route, which is itself hard to enter (see systemic note) | no change |
| `IR3_household_army` | FUNCTIONAL | flag iran_household_army (0 readers); 25 army xp; 25 command power; +10% war support; PER_bop_push_crown_small | The palaces regiments are xp and command power only - no manpower, no equipment | no change (optional: add add_manpower = constant:iran_story.gendarmerie_manpower) |
| `IR3_royal_finance` | FUNCTIONAL | flag iran_royal_finance (0 readers); iran_reclaim_leading_small; 50 pp; refresh; +5% stability | Works, but reads oddly: a court treasury that takes influence from the leading patron and cuts leverage | no change |
| `IR3_restoration_1945` | FUNCTIONAL | strips six ideas, add_ideas iran_restoration_enduring (exists); +10% stability; +10 authority; refresh; 50 pp; PER_bop_push_crown | Fine | no change |
| `IR3_national_mobilisation` | INEFFECTIVE | flag iran_national_mobilisation (0 readers); +10% war support; 10000 manpower; PER_bop_push_crown | No durable change beyond manpower; the Crown push is the only non-manpower line and it is a no-op wherever the balance is absent | set_country_flag = iran_national_mobilisation; add_war_support = constant:iran_story.war_support_gain; add_manpower = constant:iran_story.reserve_manpower; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; if = { limit = { has_power_balance = { id = PER_crown_and_majlis } } PER_bop_push_crown = yes } else = { add_manpower = constant:iran_story.reserve_manpower } |
| `IR3_oil_sovereignty` | FUNCTIONAL | iran_reclaim_british_large (-15 British influence, +8 sovereignty, -10 leverage); +10 authority; iran_campaign.55; refresh | Works; the event option adds pp/authority and sets iran_thirty_five_named, which nothing reads | no change |
| `IR3_national_army` | FUNCTIONAL | flag iran_national_army (0 readers); 25 army xp; 1000 infantry equipment | Thin - 1000 equipment is about half a division - but real | no change (optional: raise to constant:iran_story.credit_equipment and add manpower) |
| `IR3_nationalist_1945` | FUNCTIONAL | strips six ideas, add_ideas iran_nationalist_enduring (exists); +10% war support; +10 authority; refresh; +5% stability; iran_reclaim_british_large | Fine | no change |
| `IR3_workers_war_effort` | FUNCTIONAL | flag iran_workers_war_effort (0 readers); -5% stability; 1 civilian factory in 266; PER_bop_push_majlis | Fine | no change |
| `IR3_tudeh_organisation` | INEFFECTIVE | flag iran_tudeh_organisation (read only by a character allowed block); 50 pp; 5000 manpower | The party that exists to build socialist support never raises iran_socialist_support, which is the single variable the socialist route gate needs | set_country_flag = iran_tudeh_organisation; add_political_power = constant:iran_story.political_capital; add_manpower = constant:iran_story.gendarmerie_manpower; add_to_variable = { iran_socialist_support = constant:iran_story.socialist_support_gain } |
| `IR3_peoples_army` | INEFFECTIVE | flag iran_peoples_army (0 readers); 25 army xp; +10% war support | The party militia is 25 xp and war support: no manpower, no equipment, no unit | set_country_flag = iran_peoples_army; army_experience = constant:iran_story.army_experience; add_war_support = constant:iran_story.war_support_gain; add_manpower = constant:iran_story.reserve_manpower; add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_grant } |
| `IR3_socialist_1945` | FUNCTIONAL | strips six ideas, add_ideas iran_socialist_enduring (exists); +5% stability; 50 pp; iran_reclaim_northern_small; +15 socialist support | Fine, but see the systemic note: only a republic that ran the Tudeh coalition can ever reach iran_socialist_support 25 and unlock this branch | no change |

### Economy - the seven-year programme, oil and the corridor

| id | class | what it actually does | problem | proposed reward |
|---|---|---|---|---|
| `IR3_industrial_programme` | FUNCTIONAL | iran_construction_programme (already set at start; opens the decision category), iran_workshop_subsidy (opens iran_tehran_workshops); 50 pp; 1 civilian factory + 1 slot in 266 | One of the two flags duplicates the start | no change |
| `IR3_abadan_capacity` | FUNCTIONAL | iran_oil_programme (opens iran_khuzestan_capacity and iran_renegotiate_abadan_deal); iran_debt_settlement_programme (0 readers); +10 oil in 413; iran_concede_british_small; concession ledger + iran_f3.1 | Fine; the debt-settlement flag is dead | no change (optional: drop iran_debt_settlement_programme) |
| `IR3_national_workshops` | FUNCTIONAL | iran_arsenal_programme (opens iran_expand_arsenal decision); 1 arms factory + 1 slot in 266 | Fine | no change |
| `IR3_trans_iranian_connections` | FUNCTIONAL | iran_railway_programme + iran_gulf_priority + iran_caspian_priority (each opens a decision); 1 infrastructure in 266 and 420; 50 pp | Fine; three programme flags for two railway levels | no change |
| `IR3_technical_education` | FUNCTIONAL | iran_education_programme (already set at start; opens iran_technical_college, already visible); +1 research slot | The research slot is the only new content - the flag is a duplicate | no change (optional: drop the flag) |
| `IR3_logistics_commission` | FUNCTIONAL | iran_corridor_programme (opens iran_corridor_deliveries); +5% stability; 50 pp; iran_concede_british_small; concession ledger + iran_f3.1 | Fine | no change |
| `IR3_seventh_plan` | INEFFECTIVE | flag iran_seventh_plan (0 readers); 50 pp; +10 authority; hidden refresh; +5% stability | The plan builds nothing: in an economy ladder whose every other rung lays a factory or a railway, the plan itself is pp and stability | set_country_flag = iran_seventh_plan; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; 266 = { add_extra_state_shared_building_slots = constant:iran_story.project_slots }; if = { limit = { has_country_flag = iran_railway_programme } 420 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } } } |
| `IR3_steel_mill` | FUNCTIONAL | flag iran_steel_mill (0 readers); 1 civilian factory + 1 slot and +6 steel in 410 (Sistan) | Fine; ore is described near Kerman but built in Sistan | no change |
| `IR3_cement_and_power` | FUNCTIONAL | flag iran_cement_and_power (0 readers); 1 infrastructure in 266 and 418 | Fine | no change |
| `IR3_tehran_water` | MISLEADING | flag iran_tehran_water (0 readers); +5% stability; 8000 manpower | A water-supply scheme that builds nothing and moves no infrastructure - the description promises what every household can see, the reward is stability and manpower | set_country_flag = iran_tehran_water; add_stability = constant:iran_story.stability_gain; add_manpower = constant:iran_story.tribal_manpower; 266 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } } |
| `IR3_bandar_shahpur` | FUNCTIONAL | flag iran_bandar_shahpur (0 readers); 1 naval base in 413 (Khuzestan); 25 navy xp | Fine | no change |
| `IR3_double_track` | FUNCTIONAL | iran_railway_north + iran_railway_south (open two decisions) + iran_double_track (dead); 1 infrastructure in 413; 25 navy xp; 50 pp; iran_concede_northern_small; concession ledger + iran_f3.1 | 7 visible tooltip lines; the railway flags are also pre-set by iran_initialize_campaign on a post-1938 start | wrap the ledger block in hidden_effect so the tooltip keeps the railway, the concession and the pp only |
| `IR3_oil_refinery` | FUNCTIONAL | flag iran_oil_refinery (0 readers); 1 civilian factory + 1 slot in 413 | Fine, though iran_domestic_refining is the decision that actually builds a refinery | no change |
| `IR3_agriculture_1940` | FUNCTIONAL | flag iran_agriculture_1940 (0 readers); +5% stability; 1 infrastructure in 417 (Golestan) | Thin but real | no change |
| `IR3_grain_reserves` | MISLEADING | flag iran_grain_reserves (0 readers); remove_ideas = iran_supply_emergency; +10% stability; 50 pp | The description is about ending the supply emergency, but iran_supply_emergency cannot exist on a 1936 start, so the removal is a no-op and the ai weight x5 never applies | set_country_flag = iran_grain_reserves; add_stability = constant:iran_story.stability_major_gain; add_political_power = constant:iran_story.political_capital; if = { limit = { has_idea = iran_supply_emergency } remove_ideas = iran_supply_emergency }; add_manpower = constant:iran_story.tribal_manpower |
| `IR3_price_controls` | FUNCTIONAL | flag iran_price_controls (0 readers); +5% stability; add_timed_idea iran_wartime_economy 730 days (consumer goods -5%); 50 pp | Fine - the only economy focus whose payoff is an idea | no change |
| `IR3_wartime_industry` | FUNCTIONAL | flag iran_wartime_industry (0 readers); 1 arms factory + 1 slot in 266 | Fine | no change |
| `IR3_reconstruction_1945` | FUNCTIONAL | flag iran_reconstruction (0 readers); +10% stability; 1 infrastructure in 266 | Thin but real | no change |
| `IR3_economy_capstone` | FUNCTIONAL | flag iran_economy_enduring (0 readers); iran_reclaim_leading_large (-15 influence of the leading patron, +8 sovereignty, -10 leverage); 50 pp; refresh; +5% stability | Fine; no settlement idea, unlike the political capstones | no change |

### Army, air and navy

| id | class | what it actually does | problem | proposed reward |
|---|---|---|---|---|
| `IR3_defence_of_iran` | INEFFECTIVE | 25 army xp; iran_security_programme (already set at start); +10% war support | The army tree root pays xp and a duplicate flag | army_experience = constant:iran_story.army_experience; add_war_support = constant:iran_story.war_support_gain; add_manpower = constant:iran_story.reserve_manpower; add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_small } |
| `IR3_professional_reserves` | FUNCTIONAL | iran_reserve_programme (0 readers); iran_frontier_programme (opens iran_frontier_subsidy); 10000 manpower; +10% war support | Fine | no change |
| `IR3_conscription_expansion` | FUNCTIONAL | flag iran_conscription_expansion (0 readers); 10000 manpower; +10% war support | Thin: conscription raises manpower once and leaves no standing effect | no change (optional: repeat the manpower and add army_experience) |
| `IR3_arsenal_programme` | FUNCTIONAL | iran_build_tehran_arsenal (1 arms factory + 1 slot in 266, once); 25 army xp; 1000 infantry equipment | Fine | no change |
| `IR3_zagros_defences` | FUNCTIONAL | iran_build_frontier_posts (1 bunker in 419 Azerbaijan, once); iran_defensive_mobilization (0 readers); 25 army xp; +10% war support | Fine, though the flag is dead | no change |
| `IR3_airfield_network` | FUNCTIONAL | iran_air_programme (opens iran_tehran_airfield); 25 air xp; 1 air base in 266 | Fine | no change |
| `IR3_gulf_service` | FUNCTIONAL | iran_gulf_priority (opens iran_gulf_harbour); 25 navy xp; 1 dockyard in 411 (Hormozgan) | Fine | no change |
| `IR3_armoured_brigade` | MISLEADING | flag iran_armoured_brigade (0 readers); 25 army xp; 1000 infantry equipment | No armoured unit is formed and no armour is delivered - the brigade is 25 xp and half a division of rifles | set_country_flag = iran_armoured_brigade; army_experience = constant:iran_story.army_experience; add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_grant }; add_manpower = constant:iran_story.reserve_manpower; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain } |
| `IR3_mountain_brigades` | FUNCTIONAL | flag iran_mountain_brigades (0 readers); 8000 manpower; 25 army xp | Thin but real | no change |
| `IR3_air_wing` | MISLEADING | flag iran_air_wing (0 readers); 25 air xp; 1 air base in 412 (Fars) | No aircraft, no wing: an air base in Fars and 25 xp | set_country_flag = iran_air_wing; air_experience = constant:iran_story.air_experience; 412 = { add_building_construction = { type = air_base level = 1 instant_build = yes } }; add_equipment_to_stockpile = { type = fighter_equipment_1 amount = 50 } |
| `IR3_naval_patrol` | MISLEADING | flag iran_naval_patrol (0 readers); 25 navy xp; +10% war support | A patrol force with no ships and no dockyard | set_country_flag = iran_naval_patrol; navy_experience = constant:iran_story.navy_experience; add_war_support = constant:iran_story.war_support_gain; 411 = { add_building_construction = { type = dockyard level = 1 instant_build = yes } } |
| `IR3_supply_network` | FUNCTIONAL | flag iran_supply_network (0 readers); 1 infrastructure in 421 (Kurdistan) and 419 (Azerbaijan) | Fine | no change |
| `IR3_officer_corps_1940` | INEFFECTIVE | flag iran_officer_corps_1940 (0 readers); 25 army xp; 25 command power; +10% war support | The officer corps never touches iran_officer_loyalty, the one number the campaign reads for the army (iran_army_stands_firm, iran_divided_officer_corps) | set_country_flag = iran_officer_corps_1940; army_experience = constant:iran_story.army_experience; add_command_power = constant:iran_story.command_power; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_army_capstone` | FUNCTIONAL | flag iran_army_enduring (0 readers); +10% war support; 25 army xp; 10000 manpower; iran_reclaim_leading_small | Fine, though the capstone has no holding or organisation bonus | no change |

### Diplomacy, the war and the peace

| id | class | what it actually does | problem | proposed reward |
|---|---|---|---|---|
| `IR3_between_the_blocs` | INEFFECTIVE | iran_foreign_programme (already set at start); iran_campaign.36 (sets the same flag); 50 pp; 25 command power; +5% stability; +5% more stability if iran_path_armed_neutrality | The only flag is pre-set at start and the event re-sets it; nothing here plays the blocs off | country_event = { id = iran_campaign.36 }; add_political_power = constant:iran_story.political_capital; add_command_power = constant:iran_story.command_power; add_stability = constant:iran_story.stability_gain; add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } |
| `IR3_armed_neutrality` | FUNCTIONAL | iran_armed_neutrality (read by iran_path_armed_neutrality / iran_path_intact); iran_defensive_mobilization (0 readers); +10% war support; 25 command power | Fine, though the path flag is only read by this chapter's own if-limits | no change |
| `IR3_allied_cooperation` | FUNCTIONAL | iran_allied_cooperation (read by the 1941 resurgence check and iran_corridor_deliveries); iran_campaign.32; 500 infantry equipment from ENG; opinion; iran_concede_british_small; +50 pp if iran_path_entente | The iran_path_entente bonus can never fire on a 1936 start (its flags are 1910-18 only) | no change (optional: replace iran_path_entente with has_power_balance/tier check, or drop the branch) |
| `IR3_german_opening` | FUNCTIONAL | iran_german_alignment (opens iran_renegotiate_german_pact); iran_campaign.15; 500 infantry equipment from GER; opinion; iran_concede_german_small; +50 pp if iran_path_germany | The iran_path_germany bonus can never fire on a 1936 start; the AI weight is 0 on historical, so only a player ever takes it | no change (optional: drop the dead branch or key it to iran_agreement_german_mission) |
| `IR3_soviet_trade_pact` | FUNCTIONAL | flag iran_soviet_trade_pact (0 readers); 1000 infantry equipment from SOV; iran_concede_northern_small; opinion; refresh | Fine, though the flag is dead and the pact costs influence for equipment | no change |
| `IR3_british_ultimatum_response` | FUNCTIONAL | flag iran_ultimatum_answered (0 readers); -5% stability; +10% war support; iran_campaign.40 (the occupation crisis, once); iran_f3.2 if a German mission is held | Fine - this is the focus that actually starts the 1941 war | no change |
| `IR3_german_industrial_mission` | FUNCTIONAL | iran_german_industrial_mission; iran_german_technical_mission for 1825 days (+5% research, +5% industry, -3% pp); +1 research slot; iran_concede_german_small; 1 arms factory + 1 slot in 266 | Fine; the AI weight is 0 on historical | no change |
| `IR3_sovereignty_under_pressure` | INEFFECTIVE | iran_campaign.40 if not yet seen; +10% war support; 50 pp; +10% more war support if iran_path_intact | If the crisis already fired (the usual case - the monthly clock fires it from 1941), the focus is war support and pp; iran_path_intact is only ever true with iran_path_armed_neutrality | if = { limit = { NOT = { has_country_flag = iran_crisis_seen } } set_country_flag = iran_crisis_seen country_event = { id = iran_campaign.40 } }; add_war_support = constant:iran_story.war_support_gain; add_political_power = constant:iran_story.political_capital; add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain } |
| `IR3_persian_corridor` | FUNCTIONAL | iran_corridor_programme (opens iran_corridor_deliveries); +5% stability; 50 pp; iran_concede_british_large; 1000 infantry equipment from ENG | Fine | no change |
| `IR3_national_resistance` | INEFFECTIVE | iran_defensive_mobilization (0 readers); 25 army xp; +10% war support; 10000 manpower | No resistance mechanic: no occupation penalty on the occupier, no garrison cost, no sabotage decision | set_country_flag = iran_resistance_council; army_experience = constant:iran_story.army_experience; add_war_support = constant:iran_story.war_support_gain; add_manpower = constant:iran_story.reserve_manpower; add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }; add_to_variable = { iran_sovereignty = constant:iran_story.reclaim_small_sovereignty } |
| `IR3_northern_settlement` | FUNCTIONAL | iran_northern_settlement_programme (opens iran_northern_administration); iran_campaign.44; +10% stability; 8000 manpower; +10 authority; iran_reclaim_northern_small | Fine | no change |
| `IR3_regional_guarantees` | FUNCTIONAL | iran_regional_programme (opens iran_regional_assurances) + iran_shatt_programme (opens iran_shatt_negotiations); 50 pp; +5% stability | Fine | no change |
| `IR3_tehran_declaration` | FUNCTIONAL | iran_tehran_declaration (0 readers) + iran_withdrawal_programme (opens iran_withdrawal_guarantees); +10 authority; iran_campaign.43; refresh; +4 sovereignty | Fine | no change |
| `IR3_tripartite_treaty` | FUNCTIONAL | iran_tripartite_treaty (0 readers); iran_reclaim_leading_large; +5% stability; refresh; 50 pp | Fine | no change |
| `IR3_american_mission` | FUNCTIONAL | iran_american_mission (0 readers); PER_treasury_reformed (read by characters and iran_path_treasury); +1 research slot; opinion; +10 leverage | Odd cost: the honest American mission increases iran_foreign_leverage, i.e. it makes Iran more dependent | no change (optional: replace the leverage gain with add_to_variable = { iran_authority = constant:iran_story.authority_gain }) |
| `IR3_turkish_border` | FUNCTIONAL | flag iran_turkish_border (0 readers); opinion with TUR; +5% stability | Thin - an opinion modifier and stability | no change |
| `IR3_arab_neighbours` | FUNCTIONAL | flag iran_arab_neighbours (0 readers); opinion with IRQ and SAU; 50 pp | Thin - two opinion modifiers and pp | no change |
| `IR3_united_nations` | INEFFECTIVE | flag iran_united_nations (0 readers); 50 pp; +10 authority; refresh; +5% stability | Founding membership of the UN leaves no trace: no standing, no sovereignty, no guarantee | set_country_flag = iran_united_nations; add_political_power = constant:iran_story.political_capital; add_stability = constant:iran_story.stability_gain; add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain }; add_to_variable = { iran_british_standing = constant:iran_story.great_game_court_gain }; add_to_variable = { iran_northern_standing = constant:iran_story.great_game_court_gain } |
| `IR3_postwar_alignment` | INEFFECTIVE | flag iran_postwar_alignment (0 readers); +10% stability; 50 pp | Choosing a bloc at the end of the war changes nothing | set_country_flag = iran_postwar_alignment; add_stability = constant:iran_story.stability_major_gain; add_political_power = constant:iran_story.political_capital; if = { limit = { check_variable = { var = iran_british_standing value = iran_northern_standing compare = greater_than } } add_to_variable = { iran_british_standing = constant:iran_story.great_game_court_gain } } else = { add_to_variable = { iran_northern_standing = constant:iran_story.great_game_court_gain } } |
| `IR3_postwar_settlement` | FUNCTIONAL | flag iran_postwar_settlement (0 readers); +10 authority; iran_campaign.37; refresh; PER_bop_pull_to_centre | The pull-to-centre is inert under Pahlavi (no balance) - the one institutional effect of the settlement can silently do nothing | set_country_flag = iran_postwar_settlement; add_to_variable = { iran_authority = constant:iran_story.authority_gain }; country_event = { id = iran_campaign.37 }; if = { limit = { has_power_balance = { id = PER_crown_and_majlis } } PER_bop_pull_to_centre = yes }; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_azerbaijan_crisis` | FUNCTIONAL | flag iran_azerbaijan_crisis (0 readers); iran_campaign.38 sets iran_azerbaijan_restored or iran_azerbaijan_negotiated, both read by IR3_oil_debate and IR3_final_settlement | Fine - a real branching event | no change |
| `IR3_tudeh_question` | FUNCTIONAL | flag iran_tudeh_question (0 readers); -5% stability; 50 pp; iran_f3.3 sets iran_tudeh_proscribed / _tolerated / _coalition, all read downstream | Fine | no change |
| `IR3_oil_debate` | FUNCTIONAL | iran_reclaim_british_small; 50 pp; refresh; +5% stability; branches on iran_azerbaijan_* and iran_tudeh_* | About 11 visible tooltip lines - the longest in the tree after IR3_final_settlement | wrap the branch rewards in hidden_effect and keep one custom_effect_tooltip summarising the chamber's argument |
| `IR3_final_settlement` | FUNCTIONAL | strips the six end-state ideas, add_ideas iran_settlement_enduring; +10% stability; +20 authority; iran_campaign.39; refresh; 50 pp; branches on azerbaijan and tudeh flags | About 14 visible tooltip lines - the single worst tooltip in the tree | put the azerbaijan/tudeh branches in hidden_effect and add one custom_effect_tooltip; keep the idea, the authority and the event visible |

### Late additions - army, air and logistics

| id | class | what it actually does | problem | proposed reward |
|---|---|---|---|---|
| `IR3_zagros_fortification_line` | MISLEADING | 1 bunker in state 266 (Tehran); 25 army xp; +5% stability | A Zagros line is built in the capital: state 266 is Tehran, not the Zagros (Kurdistan 421, Khuzestan 413) | 421 = { add_building_construction = { type = bunker level = 2 instant_build = yes } }; army_experience = constant:iran_story.army_experience; add_stability = constant:iran_story.stability_gain |
| `IR3_reserve_mobilisation_plan` | INEFFECTIVE | 10000 manpower; +10% war support; hidden refresh | The plan has no plan: one manpower injection and no equipment, no reserve mechanic | add_manpower = constant:iran_story.reserve_manpower; add_war_support = constant:iran_story.war_support_gain; add_equipment_to_stockpile = { type = infantry_equipment amount = constant:iran_story.equipment_grant }; hidden_effect = { iran_refresh_mechanics = yes } |
| `IR3_bandar_abbas_batteries` | FUNCTIONAL | 25 navy xp; 400 fuel; 25 command power | Thin - no coastal fort in 411 Hormozgan despite the name | no change (optional: add 411 = { add_building_construction = { type = coastal_bunker level = 1 instant_build = yes } }) |
| `IR3_tehran_air_defence` | FUNCTIONAL | 1 anti-air building in 266; 25 air xp | Thin but real | no change |
| `IR3_corridor_supply_depots` | FUNCTIONAL | 1 infrastructure in 266; 250 infantry equipment | Fine | no change |

## A. Ideas referenced by focus rewards

| idea | defined? | added by | removed by | can Iran hold it on this focus's route? |
|---|---|---|---|---|
| `iran_supply_emergency` | yes, `common/ideas/iran_campaign.txt` (+stability -0.15, industry -0.15) | only the 1910-18 tree (`iran_ww1.txt` via `iran_campaign.16`); nothing in the 1936 chapter | `IR3_a_country_at_work`, `IR3_grain_reserves` (+ the `iran_bread_distribution` and second bread decision remove_effect) | **No** on a 1936 bookmark - the idea is never granted, so both `remove_ideas` calls are no-ops and the `has_idea` AI weights never fire |
| `iran_constitutional_enduring` | yes (+10% stability, +10% pp) | `IR3_constitutional_1945` | all six 1945 capstones, `IR3_final_settlement` | Yes, only on the constitutional route (allow_branch) |
| `iran_republic_enduring` | yes (+15% pp, +5% research) | `IR3_republic_1945` | all six 1945 capstones, `IR3_final_settlement` | Yes, republican route only |
| `iran_restoration_enduring` | yes (+15% stability, +5% pp) | `IR3_restoration_1945` | all six, `IR3_final_settlement` | Yes, Qajar route only |
| `iran_nationalist_enduring` | yes (+10% WS, +5% morale) | `IR3_nationalist_1945` | all six, `IR3_final_settlement` | Yes, nationalist route only |
| `iran_socialist_enduring` | yes (+10% industry, +10% conscription) | `IR3_socialist_1945` | all six, `IR3_final_settlement` | Yes, socialist route only (hard to reach - section E) |
| `iran_settlement_enduring` | yes (+10% stability, +10% pp, +5% WS) | `IR3_final_settlement` | the 1945 capstones | Yes, every route |
| `iran_wartime_economy` (timed 730d) | yes (consumer goods -5%) | `IR3_price_controls`, also the 1910-18 tree | nothing (expires) | Yes, every route |
| `iran_german_technical_mission` (timed 1825d) | yes (+5% research, +5% industry, -3% pp) | `IR3_german_industrial_mission`, `iran_invite_german_mission` decision, the German negotiation | `iran_expel_german_mission_effects` (shared by `iran_f3.2` and the expel decision) | Yes, every route that takes the German opening |

No focus reward adds or removes an idea that does not exist. The one asymmetry is the Pahlavi capstone:
`IR3_pahlavi_1945` sets the flag `iran_pahlavi_enduring` but there is no such idea, so the Pahlavi run
is the only one of the six that reaches 1945 without an end-state spirit.

## B. Tooltips that are too long

Counting only lines that actually render (flags and `hidden_effect` bodies excluded):

| focus | visible lines | cause | fix |
|---|---|---|---|
| `IR3_final_settlement` | ~14 | six `remove_ideas` + `add_ideas` + stability + authority + event + pp, then four inline `if`/`else_if` branches on the Azerbaijan and Tudeh outcomes | keep the idea swap, authority and event visible; move the branch rewards into `hidden_effect` and add one `custom_effect_tooltip` |
| `IR3_oil_debate` | ~11 | `iran_reclaim_british_small` + pp + stability + three inline branch chains | same treatment |
| `IR3_double_track` | ~7 | three flags, infrastructure, navy xp, pp, `iran_concede_northern_small`, and the inline concession-ledger `if` with its event | wrap the ledger block in `hidden_effect` |
| `IR3_constitutional_1945`, `IR3_restoration_1945`, `IR3_nationalist_1945`, `IR3_socialist_1945` | ~6 | the six-idea `remove_ideas` list plus `add_ideas`, stability, authority, pp, one Crown/Majlis shift | borderline; a `remove_ideas` list only prints the spirits actually held, so in practice ~4 lines - leave as is |

Everything else is 2-5 lines. The `iran_concede_*` / `iran_reclaim_*` and `PER_bop_*` effects each
render exactly one custom tooltip and hide their arithmetic, and `iran_refresh_mechanics` is now fully
wrapped in `hidden_effect` (the lead's fix), so no focus leaks the state-spirit swap any more. Note that
`add_to_variable` lines do render: the sixteen focuses that touch two or more variables sit at the top of
the 4-5 line band for that reason alone.

## C. AI value and branch exclusivity

Every focus has an `ai_will_do`. Four carry `factor = 0` modifiers:

| focus | zero-weight condition | verdict |
|---|---|---|
| `IR3_direct_administration` | `has_country_flag = iran_republic` | correct: the mutex partner is weighted x5 for a republic |
| `IR3_wartime_regency` | `has_country_flag = iran_pahlavi` | correct: under Pahlavi the AI takes `IR3_mohammad_reza` |
| `IR3_german_opening` | `is_historical_focus_on = yes`, and `iran_authority < 50` | correct on historical; on non-historical it means a post-1941 Iran with authority under 50 can never open to Germany |
| `IR3_german_industrial_mission` | `is_historical_focus_on = yes` | correct: the German mission is a player-only path on historical |

Branch exclusivity does not deadlock the AI in the political spine: `IR3_mohammad_reza` / `IR3_wartime_regency`
resolve by regime flag, and the armed-neutrality trio resolves because `IR3_allied_cooperation` needs a live,
non-belligerent ENG and `IR3_german_opening` needs a live, non-belligerent GER, so `IR3_armed_neutrality` is
the fallback. `IR3_persian_corridor` / `IR3_national_resistance` resolve on `iran_allied_cooperation` +
`iran_transit_agreement` versus `iran_resistance`, which the 1941 event sets exclusively.

Two real AI hazards:

1. **`IR3_a_country_at_work` is on the critical path.** It is the only prerequisite of
   `IR3_wartime_government`, which gates the whole political half of the tree, and it is `available` only
   with `iran_relief_delivered`, which only the `iran_bread_distribution` decision sets (visible from
   1939.9.1, needs 100 infantry equipment). An AI Iran that spends its equipment elsewhere - or that is at
   war and short of it - cannot progress the political tree at all.
2. **The socialist branch is effectively closed to the AI.** `iran_political_question_socialist` needs
   `iran_socialist_support >= 25`; in the 1936 chapter the only sources are `iran_f3.3` option c (+15,
   needs `iran_socialist` or `iran_republic`) and `IR3_oil_debate` (+15, needs `iran_tudeh_coalition`), i.e.
   both sit behind the gate they unlock, and both are 1945 content. The AI will never get there.

## D. Flags set by rewards and never read

Set by a focus reward (or by the event it fires) and never tested by any
`has_country_flag` in `common/`, `events/` or `history/`: **67 of the 102 distinct flags** the rewards touch.
The dead ones, in file order:

`iran_named_iran`, `iran_name_adopted`, `iran_wartime_government`, `iran_wartime_cabinet`, `iran_wartime_majlis_cabinet`,
`iran_succession_prepared`, `iran_succession_managed`, `iran_mohammad_reza`, `iran_wartime_regency`,
`iran_occupation_administration`, `iran_resistance_council`, `iran_pahlavi_progress`, `iran_royal_army_1940`,
`iran_development_corps`, `iran_pahlavi_enduring`, `iran_constitutional_wartime`, `iran_wartime_majlis`,
`iran_cabinet_stability`, `iran_constitutional_enduring` (the flag; the idea of that name is fine),
`iran_republic_wartime`, `iran_republican_defence`, `iran_civil_defence`, `iran_republic_enduring` (flag),
`iran_court_wartime`, `iran_household_army`, `iran_royal_finance`, `iran_restoration_enduring` (flag),
`iran_national_mobilisation`, `iran_oil_sovereignty`, `iran_national_army`, `iran_nationalist_enduring` (flag),
`iran_workers_war_effort`, `iran_peoples_army`, `iran_socialist_enduring` (flag), `iran_debt_settlement_programme`,
`iran_seventh_plan`, `iran_steel_mill`, `iran_cement_and_power`, `iran_tehran_water`, `iran_bandar_shahpur`,
`iran_double_track`, `iran_oil_refinery`, `iran_agriculture_1940`, `iran_grain_reserves`, `iran_price_controls`,
`iran_wartime_industry`, `iran_reconstruction`, `iran_economy_enduring`, `iran_reserve_programme`,
`iran_conscription_expansion`, `iran_defensive_mobilization`, `iran_armoured_brigade`, `iran_mountain_brigades`,
`iran_air_wing`, `iran_naval_patrol`, `iran_supply_network`, `iran_officer_corps_1940`, `iran_army_enduring`,
`iran_soviet_trade_pact`, `iran_ultimatum_answered`, `iran_tehran_declaration`, `iran_tripartite_treaty`,
`iran_american_mission`, `iran_turkish_border`, `iran_arab_neighbours`, `iran_united_nations`,
`iran_postwar_alignment`, `iran_postwar_settlement`, `iran_azerbaijan_crisis`, `iran_tudeh_question`,
`iran_oil_debate`, `iran_1945_settlement`.

The chapter narrates itself in flags that nothing reads. The flags a reward can safely be built on - because
something actually tests them - are `iran_security_programme`, `iran_treasury_programme`,
`iran_provincial_compact`, `iran_constitutional_programme`, `iran_centralizing_programme`,
`iran_relief_programme`, `iran_arsenal_programme`, `iran_education_programme`, `iran_workshop_subsidy`,
`iran_oil_programme`, `iran_caspian_priority`, `iran_gulf_priority`, `iran_railway_programme`,
`iran_railway_north`, `iran_railway_south`, `iran_air_programme`, `iran_corridor_programme`,
`iran_frontier_programme`, `iran_regional_programme`, `iran_shatt_programme`,
`iran_northern_settlement_programme`, `iran_withdrawal_programme`, `iran_construction_programme`,
`iran_foreign_programme`, `iran_allied_cooperation`, `iran_german_alignment`, `iran_succession_question`,
`iran_german_industrial_mission`, `PER_treasury_reformed`, plus the flags other content sets and this tree
only reads: `iran_resistance`, `iran_occupied`, `iran_rule_by_decree`, `iran_azerbaijan_restored`,
`iran_azerbaijan_negotiated`, `iran_tudeh_proscribed`, `iran_tudeh_coalition`, `iran_tudeh_tolerated`.

## E. Systemic findings

1. **The Crown and the Majlis only exist after 1941, and only with Arms Against Tyranny.**
   `PER_bop_sync` creates the balance only when `has_dlc = "Arms Against Tyranny"`, and it *removes* it
   whenever Iran is Pahlavi without `PER_majlis_resurgence` - which is the whole 1936-41 period. So every
   `PER_bop_push_crown*` / `PER_bop_push_majlis*` line in the politics ladder is a silent no-op until the
   1941 occupation fires the resurgence, and for the Pahlavi branch it stays a no-op even then unless the
   player is occupied or cooperating. The mod does not declare AAT as a dependency (`descriptor.mod` has
   no `dependencies` block), so on a bare install the entire Crown/Majlis ladder pays nothing.
2. **`iran_authority` is inert on the main route.** Its only readers are the 65-point threshold in
   `iran_refresh_mechanics` (which the `iran_pahlavi` branch short-circuits) and the
   `iran_cancel_the_concession` / `iran_domestic_refining` / `iran_purge_the_cossacks` decisions. Fifteen
   focuses spend `add_to_variable = { iran_authority = ... }` on the Pahlavi route and change nothing.
3. **The consolidated state spirits are unreachable in this chapter.** `iran_*_consolidated` is granted by
   `iran_refresh_mechanics` only when the matching `iran_*_settled` flag is set, and all six `_settled`
   flags are set only by the 1925-35 interwar tree. A 1936 start can never upgrade its state spirit.
4. **The 1936 start already owns eleven of the flags the tree pays out.** `iran_initialize_campaign` sets
   `iran_security_programme`, `iran_treasury_programme`, `iran_construction_programme`,
   `iran_provincial_compact`, `iran_budget_established`, `iran_foreign_programme`,
   `iran_education_programme`, `iran_civil_service`, `iran_tax_reformed`, `PER_treasury_reformed`,
   `iran_gendarmerie_ready` at game start, so `IR3_inheritance_of_the_state`, `IR3_provincial_compacts`,
   `IR3_a_country_at_work`, `IR3_between_the_blocs`, `IR3_industrial_programme`, `IR3_technical_education` and
   `IR3_defence_of_iran` all pay for something the player already had.
5. **The political spine is date-locked twice before it starts.** `IR3_a_country_at_work` needs
   `iran_relief_delivered` (bread decision, 1939.9.1+), then `IR3_wartime_government` needs 1939.9, then
   `IR3_succession_crisis` needs 1941.8.24. Measured on the prerequisite graph, 36 of the 99 focuses cannot
   be completed before 1939.9 and 34 cannot be completed before 1941.8.24.
6. **The socialist route is unreachable in practice.** See C.2: the gate needs 25 socialist support and the
   only sources in this chapter are inside the branch it unlocks or inside 1945 content. The Qajar gate
   (`iran_authority < 40` against a start of 60) is reachable only after several -10 authority events.
7. **`iran_supply_emergency` does not exist in this chapter.** Two focuses and one AI weight depend on it.
8. **Two focuses promise buildings they do not build** (`IR3_tehran_water`, `IR3_bandar_abbas_batteries`) and
   one builds its line in the wrong province (`IR3_zagros_fortification_line` in Tehran).

## F. Adjacent fixes outside the focus file (not applied)

- `iran_initialize_campaign` (1936 branch): stop pre-setting `iran_budget_established`,
  `iran_education_programme`, `iran_provincial_compact`, `iran_construction_programme`,
  `iran_security_programme`, `iran_treasury_programme`, `iran_foreign_programme`, `iran_civil_service`;
  let the seven focuses that name them grant them. This alone revives seven rewards.
- `iran_campaign.31` and `iran_campaign.36` are empty flavour events whose only option re-runs
  `iran_refresh_mechanics` or re-sets a flag the country already has; give their options a real effect or
  drop the `country_event` line from the focus.
- `iran_campaign.34`, `.35` set four flags nothing reads; make `iran_wartime_cabinet` /
  `iran_wartime_majlis_cabinet` gate a decision, or drop them.
- `iran_political_question_socialist`: lower the support gate to 15, or grant 10 socialist support from
  `IR3_public_granaries` / `IR3_workers_war_effort`'s neighbours so the route can be entered before 1945.
- `IR3_british_ultimatum_response` and `IR3_sovereignty_under_pressure` share the `iran_crisis_seen` guard;
  the second one is then only war support and pp. Give the second one its own payload.

## G. Where nothing existing fits (new content required - flagged, not proposed)

- **A Pahlavi end-state spirit.** The other five 1945 capstones grant an `iran_*_enduring` idea; there is no
  Pahlavi equivalent. The audit's proposal reuses `iran_pahlavi_settled` so the existing
  `iran_pahlavi_consolidated` spirit appears instead, but if the intent was a distinct 1945 spirit, one
  new idea is needed.
- **A food or granary mechanic.** `IR3_public_granaries`, `IR3_grain_reserves` and `IR3_tehran_water` all
  want a food/water effect and the mod has no such variable; the proposals fall back on stability, manpower
  and a civilian factory.
- **A resistance-against-occupation mechanic.** `IR3_resistance_council` and `IR3_national_resistance`
  describe sabotage and non-cooperation; there is no occupier-side cost to model it, so the proposals use
  war support, manpower, officer loyalty and sovereignty.

