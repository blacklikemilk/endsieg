# Iran 1919-1935 focus-reward audit

Scope: `common/national_focus/iran_interwar.txt`, focus tree `iran_interwar`, **139 focuses** (the brief said 140; the file parses to 139 `focus = { id = IR2_* }` blocks).
Read-only audit: nothing outside this file was modified.

Method: every `completion_reward` was parsed and expanded one level through the scripted effects it calls
(`iran_concede_*` / `iran_reclaim_*`, `PER_bop_push_*`, `iran_settle_*`, `iran_build_*`, `iran_coup_clamp`,
`iran_refresh_mechanics`), then every flag it sets was grepped across `common/`, `events/`, `history/` and
`localisation/` (about 5,700 files) to see whether anything reads it, every state it targets was checked against
`history/states` ownership, and every event it fires was read.

Route note: there is **no 1919 bookmark** (`common/bookmarks/the_red_scare.txt` is entirely commented out), and the
interwar tree is loaded by `iran_route_chapter` for `date > 1918.12.31` and `< 1936.1.1`. So the only way into this
tree is to play the 1918 `kaiserchlacht` (or an earlier) campaign forward. That matters for one point below:
`iran_initialize_campaign` runs only from `on_startup`, so its `date > 1918.12.31` block — which pre-sets
`iran_treasury_programme`, `iran_security_programme`, `iran_construction_programme`, `iran_provincial_compact`,
`iran_tax_reformed`, `PER_treasury_reformed`, `iran_gendarmerie_ready` — **never runs** on the reachable route.
Those flags are therefore genuinely produced by the focuses that set them, not redundant. `has_dlc =
"Arms Against Tyranny"` is required by `PER_bop_sync`; without it no Crown/Majlis balance ever exists.


## Counts

| class | focuses |
| --- | --- |
| FUNCTIONAL | 89 |
| CONDITIONAL-MEANINGFUL | 30 |
| INEFFECTIVE | 8 |
| BROKEN | 6 |
| MISLEADING | 6 |
| REDUNDANT | 0 |
| **total** | **139** |

FUNCTIONAL 89 + CONDITIONAL 30 + INEFFECTIVE 8 + BROKEN 6 + MISLEADING 6 = 139.
No focus qualifies as REDUNDANT in the strict sense (branch still connects without it) except `IR2_arsenal_expansion`, which is a childless leaf and is listed under BROKEN with that noted.


## Per-focus table

| id | class | what it actually does | problem | proposed reward (script-ready) |
| --- | --- | --- | --- | --- |
| `IR2_postwar_settlement` | FUNCTIONAL | opens `iran_treasury_programme` + `iran_security_programme` (gate 3 decisions), event 21, +50 PP, +5% stab, +10 authority | event 21 only sets `iran_debt_settlement_programme`, which nothing reads | keep; drop event 21 or make its flag feed a decision (`visible = { has_country_flag = iran_debt_settlement_programme }` on `iran_repay_foreign_credit`) |
| `IR2_reject_the_agreement` | FUNCTIONAL | `iran_reclaim_british_large` (−15 ENG influence, +8 sovereignty, −10 leverage), +50 PP, +5% stab | — | keep |
| `IR2_accept_the_agreement` | FUNCTIONAL | +500 inf eq from ENG, `iran_concede_british_large` (+15 influence, −6 sovereignty, +10 leverage), event 14 (another 500 eq on option a) | credit is paid twice (focus + event 14.a) and the concession is not in the description | remove the `add_equipment_to_stockpile` line and let event 14 carry the credit; add `custom_effect_tooltip = iran_concede_british_large_tt` is already in the effect |
| `IR2_majlis_restored` | CONDITIONAL-MEANINGFUL | +0.20 Majlis, +10 authority, +5% stab, +50 PP; flag feeds `iran_path_majlis` | Crown/Majlis push is a no-op under the Pahlavi settlement and without Arms Against Tyranny | add a route-independent floor: `add_to_variable = { iran_authority = constant:iran_story.authority_gain } add_political_power = 25` (keep the push) |
| `IR2_british_advisers` | CONDITIONAL-MEANINGFUL | +10 authority, `iran_concede_british_small` (+8 influence, −3 sovereignty); +25 XP and 500 eq only if `iran_path_entente` | the XP/equipment half is dead on every route that is not already the entente | drop the `if = { limit = { iran_path_entente = yes } }` guard and pay 25 XP + 500 eq unconditionally |
| `IR2_command_and_cabinet` | FUNCTIONAL | event 22 → choice of `iran_cossack_tradition`+`iran_dynastic_assembly`+25 XP, or `iran_constitution_secured` (both read); +25 CP, +10 authority | — | keep |
| `IR2_cabinet_responsibility` | FUNCTIONAL | +0.20 Majlis, +10 authority, +5% stab, +50 PP; flag feeds `iran_path_majlis` and event 50 | — | keep |
| `IR2_the_coup_of_1921` | FUNCTIONAL | +0.30 Crown, +30 `iran_reza_influence`, +25 CP, event 50 (choice) | — | keep |
| `IR2_cossack_brigade` | FUNCTIONAL | +25 XP, +0.10 WS, +0.10 Crown; `iran_cossack_ascendant` drives the monthly Reza drift | — | keep |
| `IR2_loyal_division` | CONDITIONAL-MEANINGFUL | +10 officer loyalty, −15 Reza, +0.30 Majlis, +25 CP, +5% stab, event f2.1 | `available` needs loyalty ≥ 60 but the campaign opens at 50: only reachable after `iran_buy_the_brigade` (100 PP, 120-day cooldown), and nothing says so | lower the requirement to 55, or add `custom_trigger_tooltip = { tooltip = iran_officer_loyalty_tt ... }` text that names the decision; keep the reward |
| `IR2_gilan_republic` | CONDITIONAL-MEANINGFUL | +15 socialist support, +0.10 WS, +25 CP, event 51 | `iran_gilan_republic` is never read | keep the support and add `add_popularity = { ideology = communism popularity = 0.02 }` + `set_country_flag = iran_gendarmerie_ready`; or read the flag in `IR2_jangali_congress.available` |
| `IR2_reza_khan_minister` | FUNCTIONAL | +20 Reza, +0.30 Crown, +25 XP, +10 authority, +0.10 WS | — | keep |
| `IR2_jangali_congress` | FUNCTIONAL | +15 socialist support, event 52 (−5% stab, +50 PP or +8000 MP) | flag unread; support only matters against the 50 threshold | keep, and make `IR2_soviet_accord.available` require `iran_jangali_congress` (it already sits below it, so nothing is lost) |
| `IR2_soviet_accord` | FUNCTIONAL | `iran_concede_northern_small` (+8 northern influence, −3 sovereignty), +15 socialist support, 1000 eq from SOV, +25 SOV opinion | the concession is invisible in the description | the effect already prints `iran_concede_northern_small_tt`; only the `_desc` needs to admit the concession |
| `IR2_socialist_congress` | CONDITIONAL-MEANINGFUL | +15 socialist support, +50 PP, +5% stab | a 10-week focus whose only product is +15 of a counter | add `add_manpower = constant:iran_story.tribal_manpower` and `set_country_flag = iran_provincial_compact` (opens `iran_tribal_regiment`) |
| `IR2_landlord_settlement` | MISLEADING | +5% stab and one infrastructure level in state 413 (Khuzestan) | the text promises a quiet countryside and harvests to market; the reward is a road in the oil province | `412 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` (Fars, the landed south) plus `add_stability = 0.05` |
| `IR2_provincial_governors` | CONDITIONAL-MEANINGFUL | +20 authority, +50 PP, −5% stab, refresh | a 7-week focus that yields only an invisible counter and a PP/stability wash | add `419 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` and `set_country_flag = iran_centralizing_programme` (opens `iran_provincial_security`) |
| `IR2_dynastic_question` | FUNCTIONAL | event 23 (+10 authority), layout refresh, +50 PP, −5% stab | the only payoff is one event option worth +10 authority | add `PER_bop_pull_to_centre = yes` (the assembly is a constitutional moment) — already guarded for the balance |
| `IR2_nationalist_movement` | INEFFECTIVE | +50 PP, +0.10 WS; `iran_nationalist_movement` is read nowhere | a 7-week focus with no effect on any system; its two children are not gated on it | `add_popularity = { ideology = fascism popularity = 0.03 } add_to_variable = { iran_authority = constant:iran_story.authority_gain }` and add `available = { has_country_flag = iran_nationalist_movement }` to the two children |
| `IR2_nationalist_press` | CONDITIONAL-MEANINGFUL | +10 authority, +5% stab, +50 PP; flag unread | nothing distinguishes it from a generic political focus | add `add_popularity = { ideology = fascism popularity = 0.02 }` and `iran_reclaim_leading_small = yes` (the press attacks the concessions, per its own text) |
| `IR2_nationalist_officers` | FUNCTIONAL | +25 XP, +25 CP, +0.10 Crown, +0.10 WS; the flag is the gate on `IR2_nationalist_front` | — | keep |
| `IR2_the_final_settlement` | FUNCTIONAL | gate for the six settlements; +50 PP, +5% stab, layout, `iran_settlement_choice_tt` | carries no reward of its own for a 5-week focus | add `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` and `PER_bop_pull_to_centre = yes` |
| `IR2_qajar_restoration` | FUNCTIONAL | regime change + `iran_restoration_settled` route, `iran_reclaim_leading_large`, 1000 eq, +25 CP, +5% stab | 11 visible tooltip lines because `iran_settle_qajar_restoration` is not hidden | wrap the call: `hidden_effect = { iran_settle_qajar_restoration = yes }` + `custom_effect_tooltip = iran_settle_qajar_tt` |
| `IR2_court_and_concessions` | FUNCTIONAL | `iran_reclaim_british_large` (+8 sovereignty), +0.20 Crown, +50 PP | flag `iran_court_sovereignty` is read only by the 1933 decision, which needs `iran_oil_settlement_open` | add `set_country_flag = iran_oil_settlement_open` so the decision it advertises actually appears |
| `IR2_constitutional_crown` | FUNCTIONAL | regime change, +1 research slot, +50 PP, +10% stab | 7 tooltip lines (settle body unhidden) | hide `iran_settle_constitution` behind `hidden_effect` + one `custom_effect_tooltip` |
| `IR2_parliamentary_republic` | FUNCTIONAL | regime change (democratic +30%), +50 PP, +5% stab, +0.20 Majlis | 10 tooltip lines; `PER_bop_push_majlis` is redundant the day the balance is rebuilt at +0.05 under a republic | hide the settle body; drop the explicit push |
| `IR2_pahlavi_settlement` | FUNCTIONAL | regime change (no elections), +25 XP, +25 CP, +10 authority, +5% stab | 9 tooltip lines | hide `iran_settle_pahlavi` behind `hidden_effect` + one tooltip |
| `IR2_nationalist_front` | FUNCTIONAL | regime change (fascism +30%), +10000 MP, +25 XP, +0.10 WS | 10 tooltip lines | hide `iran_settle_nationalist` behind `hidden_effect` |
| `IR2_socialist_republic` | FUNCTIONAL | regime change (communism +30%), +10000 MP, +50 PP, −5% stab | 10 tooltip lines | hide `iran_settle_socialist` behind `hidden_effect` |
| `IR2_royal_authority` | CONDITIONAL-MEANINGFUL | +20 authority, +50 PP, +5% stab; flag unread | pure counter inflation | add `PER_bop_push_crown = yes` and `set_country_flag = iran_royal_household` (read by the Qajar AI weight) |
| `IR2_court_ministries` | CONDITIONAL-MEANINGFUL | +0.20 Crown, +5% stab, +50 PP | nothing at all under the Pahlavi settlement or without Arms Against Tyranny | add `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` outside the guarded push |
| `IR2_governors_of_the_crown` | CONDITIONAL-MEANINGFUL | +0.10 Crown, +10 authority, refresh | same single-axis dependency | add `set_country_flag = iran_centralizing_programme` (opens two decisions) |
| `IR2_household_brigade` | CONDITIONAL-MEANINGFUL | +25 XP, +25 CP, +0.10 WS | a 10-week focus that raises no unit and builds nothing, despite its text | `266 = { add_building_construction = { type = arms_factory level = 1 instant_build = yes } }` or `add_manpower = constant:iran_story.gendarmerie_manpower` |
| `IR2_press_restraint` | MISLEADING | `iran_concede_leading_small` (the leading patron +8 influence, Iran −3 sovereignty, +10 leverage), +5% stab, +50 PP | the text describes licensing newspapers; the reward hands a concession to a foreign power and is not mentioned | keep the concession but say so in `_desc`, or replace it with `add_stability = 0.05 add_to_variable = { iran_authority = 5 }` |
| `IR2_royal_works` | FUNCTIONAL | +1 shared slot and a civilian factory in 266, +0.10 Crown | — | keep |
| `IR2_restoration_capstone` | FUNCTIONAL | `iran_restoration_settled` (upgrades the Qajar spirit), +0.30 Crown, `iran_reclaim_leading_small`, +10% stab, +10 authority | — | keep |
| `IR2_ministers_before_the_majlis` | FUNCTIONAL | +0.20 Majlis; `iran_civil_service` (characters) and `iran_constitutional_programme` (opens `iran_constitutional_petitions`) | — | keep |
| `IR2_electoral_law` | INEFFECTIVE | +50 PP, +5% stab; `iran_electoral_law` only feeds `iran_path_majlis`, which this branch's ancestors already satisfy | no observable change and no new content | `add_popularity = { ideology = democratic popularity = 0.03 }` + `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` + gate `IR2_elections_1928.available` on the flag |
| `IR2_provincial_compacts_ii` | FUNCTIONAL | +8000 MP, +10 authority; `iran_provincial_compact` opens the `iran_tribal_regiment` decision | — | keep |
| `IR2_civil_service` | FUNCTIONAL | +1 research slot; `iran_civil_service` is read by characters and the 1936 tree | — | keep |
| `IR2_budget_control` | FUNCTIONAL | `iran_budget_established` (continuity + 1936 tree), `iran_reclaim_leading_small`, +50 PP, +5% stab | — | keep |
| `IR2_constitutional_army` | FUNCTIONAL | +0.10 Majlis, +25 XP, +25 CP, +0.10 WS; flag feeds `iran_path_army` | — | keep |
| `IR2_constitutional_capstone` | FUNCTIONAL | `iran_constitutional_settled`, +0.30 Majlis, `iran_reclaim_british_small`, +5% democratic, +10% stab | — | keep |
| `IR2_responsible_government` | FUNCTIONAL | `iran_constitutional_programme` (decision), `iran_civil_service` (characters); `iran_electoral_programme` is read nowhere | one of its three flags is dead | replace `iran_electoral_programme` with `set_country_flag = iran_electoral_law` (read by `iran_path_majlis`) |
| `IR2_republican_constitution` | FUNCTIONAL | event 53 (choice), +0.20 Majlis, +10% stab, +50 PP | — | keep |
| `IR2_elections_1928` | CONDITIONAL-MEANINGFUL | +0.10 Majlis, +50 PP, +5% stab; `iran_elections_held` is read by the character files | the visible half is a trickle | add `add_popularity = { ideology = democratic popularity = 0.03 }` |
| `IR2_civil_code` | FUNCTIONAL | +1 research slot, +10 authority, `iran_reclaim_leading_small` | — | keep |
| `IR2_land_reform_debate` | FUNCTIONAL | +10000 MP, infrastructure in 417, −5% stab | shares an identical payload with `IR2_land_to_the_peasants` | differentiate: give 417 `add_extra_state_shared_building_slots` here |
| `IR2_civilian_control` | CONDITIONAL-MEANINGFUL | +25 XP, +5% stab; flag unread | a republican army reform worth one training cycle | add `PER_bop_push_majlis_small = yes` and `add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }` |
| `IR2_republic_capstone` | FUNCTIONAL | `iran_republic_settled`, `iran_reclaim_leading_large`, +10% democratic, +10% stab | — | keep |
| `IR2_royal_administration` | FUNCTIONAL | `iran_centralizing_programme` (opens `iran_provincial_security` and `iran_punitive_expedition`), `iran_civil_service` | — | keep |
| `IR2_pahlavi_army` | FUNCTIONAL | +10000 MP, +25 XP | flag unread but the payload is real | keep |
| `IR2_secular_courts` | FUNCTIONAL | +10 authority, `iran_reclaim_british_small`, −5% stab | — | keep |
| `IR2_tribal_disarmament` | FUNCTIONAL | +20 authority, +8000 MP, event 54, extra PP/stab if `iran_path_gendarmerie` | 7 tooltip lines; the `if`-limited bonus prints as a conditional block | keep, but move the gendarmerie bonus into `hidden_effect` with a `custom_effect_tooltip` |
| `IR2_military_academy` | CONDITIONAL-MEANINGFUL | +25 XP, +25 CP, +0.10 WS | the officers it trains never appear as a value | add `add_to_variable = { iran_officer_loyalty = constant:iran_story.officer_gain }` (an existing variable the 1941 check reads) |
| `IR2_state_enterprises` | MISLEADING | +1 slot and an **arms** factory in 266 | the text promises mills, a cement works and a sugar plant — civil industry | `266 = { add_building_construction = { type = industrial_complex level = 1 instant_build = yes } }` (and leave the arsenal to `IR2_arsenal_expansion`) |
| `IR2_pahlavi_capstone` | FUNCTIONAL | `iran_pahlavi_settled`, `iran_reclaim_british_large`, civ factory + slot in 266, +20 authority | 6 tooltip lines | acceptable; consider one `custom_effect_tooltip` for the factory block |
| `IR2_national_union` | CONDITIONAL-MEANINGFUL | +0.30 Crown, +50 PP, +5% stab; flag unread | a 10-week focus with a balance push and nothing else | add `add_popularity = { ideology = fascism popularity = 0.03 }` and `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` |
| `IR2_economic_independence` | FUNCTIONAL | civilian factory + slot in 413, `iran_reclaim_leading_large` | — | keep |
| `IR2_national_militia` | FUNCTIONAL | +10000 MP, +25 XP, +0.10 WS | flag unread | keep |
| `IR2_iranian_academy` | FUNCTIONAL | +1 research slot, +5% stab | — | keep |
| `IR2_oil_revision` | FUNCTIONAL | event 55 (−10 leverage, or +0.10 WS and a dispute), `iran_reclaim_british_small`, +50 PP | — | keep |
| `IR2_gulf_claims` | FUNCTIONAL | naval base in 411, +0.10 WS | — | keep |
| `IR2_nationalist_capstone` | FUNCTIONAL | `iran_nationalist_settled`, `iran_reclaim_british_large`, +5% fascism, +10 authority | — | keep |
| `IR2_workers_councils` | FUNCTIONAL | civilian factory in 266, +0.20 Majlis, −5% stab | — | keep |
| `IR2_land_to_the_peasants` | FUNCTIONAL | +10000 MP, infrastructure in 417, −5% stab | identical payload to `IR2_land_reform_debate` one branch over | give this one `set_country_flag = iran_provincial_compact` (opens `iran_tribal_regiment`) instead of duplicating the road |
| `IR2_red_gendarmes` | CONDITIONAL-MEANINGFUL | +25 XP, +0.10 WS; flag unread | a 10-week focus for one training cycle | add `add_equipment_to_stockpile = { type = infantry_equipment amount = 500 }` and `set_country_flag = iran_gendarmerie_ready` |
| `IR2_soviet_trade` | FUNCTIONAL | `iran_concede_northern_small`, infrastructure in 420, +25 SOV opinion | the concession is not in the description | say so in `_desc`; keep the rest |
| `IR2_labour_law` | CONDITIONAL-MEANINGFUL | +5000 MP, +0.10 Majlis, +5% stab | the organised workers it legalises produce no support | add `add_to_variable = { iran_socialist_support = constant:iran_story.socialist_support_gain }` |
| `IR2_anti_concession` | FUNCTIONAL | `iran_reclaim_leading_large`, +0.10 WS, +50 PP | — | keep |
| `IR2_socialist_capstone` | FUNCTIONAL | `iran_socialist_settled`, `iran_reclaim_leading_large`, +5% communism, +10 authority | — | keep |
| `IR2_the_state_in_1935` | FUNCTIONAL | events f2.3 and 56, +20 authority, +50 PP, `iran_reclaim_leading_small`, +5% stab | 6 tooltip lines; two events on one reward | fine, but consider dropping event 56 (it only adds authority +50 PP again) |
| `IR2_treasury_commission` | FUNCTIONAL | opens the `iran_national_projects` decision category (`iran_construction_programme`), `PER_treasury_reformed`, +10 authority (+10 more on the treasury path) | 6 tooltip lines because of the `if`-limited double payment | move the path bonus into `hidden_effect` + `custom_effect_tooltip` |
| `IR2_domestic_capital` | FUNCTIONAL | `iran_workshop_subsidy` (opens the `iran_tehran_workshops` decision), `iran_reclaim_leading_small` | the reclaim tooltip is the only visible line | acceptable |
| `IR2_foreign_concessions` | FUNCTIONAL | +500 eq from ENG, event 14 (another 500), `iran_concede_british_small` (+8 influence), and the same concession again on the oil path | 7 tooltip lines; on the oil path the concession is applied twice for +16 influence | delete the duplicate `iran_concede_british_small` inside the `if`-limit |
| `IR2_khuzestan_oil` | FUNCTIONAL | +10 oil in 413, event 24 (`iran_oil_programme` → opens `iran_khuzestan_capacity`), `iran_concede_british_small` | 7 tooltip lines; concession not described | keep, hide the concession arithmetic (already one line) and trim the `if` block |
| `IR2_trans_iranian_railway` | BROKEN | infrastructure in 410, 413 (+slot), **415**, 421; +10 authority | state 415 (South Khorasan) is owned by AFG: the focus builds a railway in Afghanistan; 6 tooltip lines | replace `415` with `414` (Kerman) or `416`; wrap the whole block in `hidden_effect` + `custom_effect_tooltip` |
| `IR2_state_railways` | BROKEN | infrastructure in 410 and **415**; `iran_railway_programme`; +50 PP | same 415-is-Afghan bug, and it sets the identical flag as `IR2_trans_iranian_railway` | replace `415` with `414`; add `mutually_exclusive = { focus = IR2_trans_iranian_railway }` |
| `IR2_schools_and_workshops` | FUNCTIONAL | +1 research slot, `iran_education_programme` (opens `iran_technical_college`), `iran_workshop_subsidy` | — | keep |
| `IR2_an_integrated_market` | FUNCTIONAL | `iran_budget_established`, `iran_reclaim_leading_small`, +500 eq, +10 authority, +50 PP | — | keep |
| `IR2_caspian_roads_project` | FUNCTIONAL | infrastructure in 420, `iran_caspian_priority` (opens the `iran_caspian_roads` decision) | — | keep |
| `IR2_gulf_harbour_project` | FUNCTIONAL | infrastructure in 411, `iran_gulf_priority` (opens `iran_gulf_harbour`) | — | keep |
| `IR2_oil_renegotiation` | FUNCTIONAL | +10 oil in 413, `iran_oil_settlement_open` (opens the 1933 decision), +50 PP | — | keep |
| `IR2_textile_industry` | FUNCTIONAL | civilian factory + slot in 410 | — | keep |
| `IR2_sugar_refinery` | FUNCTIONAL | civilian factory + slot in 416 | — | keep |
| `IR2_agricultural_credit` | FUNCTIONAL | +8000 MP, +5% stab | the bank itself is only manpower | add `add_stability` is already there; consider `417 { add_building_construction = { type = infrastructure ... } }` or keep |
| `IR2_land_registry` | CONDITIONAL-MEANINGFUL | +10 authority, +50 PP, +5% stab; flag unread | a land register that changes no number the game reads | add `iran_reclaim_leading_small = yes` (registered title is exactly what lets the state tax concessions) |
| `IR2_tehran_university` | FUNCTIONAL | +1 research slot, infrastructure in 266; `iran_tehran_university` is read by the character files | — | keep |
| `IR2_state_university` | FUNCTIONAL | +1 research slot, +5% stab; sets the same `iran_tehran_university` flag | two focuses produce the identical flag and slot | acceptable as settlement-gated alternatives |
| `IR2_industrial_bank` | CONDITIONAL-MEANINGFUL | `iran_reclaim_leading_small`, +50 PP (+50 more on the treasury path), +5% stab | a 10-week focus that mostly pays political power | add `add_research_slot` is wrong here; use `413 { add_extra_state_shared_building_slots = 1 }` and `add_equipment_to_stockpile = { type = infantry_equipment amount = 250 }`? prefer: `set_country_flag = iran_budget_established` |
| `IR2_mining_survey` | FUNCTIONAL | +6 steel in 414 | — | keep |
| `IR2_road_programme` | BROKEN | infrastructure in 421 and **415** | 415 belongs to AFG; the eastern road is built in Afghanistan | replace `415` with `416` (Razavi Khorasan, the Khorasan road its text names) |
| `IR2_customs_reform` | BROKEN | +10 authority, +50 PP, +5% stab; sets `iran_customs_reform` | the system reads `iran_customs_reformed` (influence tick and the ‘end the foreign customs administration’ decision); the missing `-ed` makes this focus unable to start the sovereignty recovery it exists for | `set_country_flag = iran_customs_reformed` (and add `add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain }`) |
| `IR2_national_tariff_office` | BROKEN | `iran_reclaim_leading_small`, +10 authority; sets `iran_customs_reform` | same dead flag as `IR2_customs_reform` | same fix: set `iran_customs_reformed` |
| `IR2_telecommunications` | FUNCTIONAL | infrastructure in 266 and 412 | — | keep |
| `IR2_urban_works` | MISLEADING | an anti-air building in 266, +5% stab | the text describes paved streets, piped water and public buildings; the reward is a flak battery | `266 = { add_building_construction = { type = infrastructure level = 1 instant_build = yes } }` (or reword to civil defence) |
| `IR2_economic_capstone` | CONDITIONAL-MEANINGFUL | `iran_reclaim_leading_large`, +50 PP, +5% stab; flag unread | the capstone of the whole economic spine is a leverage adjustment and a trickle | add `add_research_slot = 1` is already used twice in this spine; prefer `set_country_flag = iran_budget_established add_to_variable = { iran_authority = constant:iran_story.authority_major_gain }` |
| `IR2_unified_command` | FUNCTIONAL | `iran_security_programme` (opens `iran_equip_gendarmerie` and `iran_provincial_compact`), +25 XP, +0.10 WS | flag duplicates `IR2_general_staff` | fine as settlement-gated alternatives |
| `IR2_general_staff` | FUNCTIONAL | same flag, +25 XP, +25 CP, +0.10 WS | duplicate flag | fine |
| `IR2_provincial_army` | FUNCTIONAL | `iran_professional_officers` (feeds `iran_path_army`) and `iran_reserve_programme` (read by ww1/ww2), +25 XP | — | keep |
| `IR2_arsenal_network` | FUNCTIONAL | `iran_build_tehran_arsenal` (1 slot + arms factory in 266, once per campaign) | the reward is silent if the arsenal already exists, and the focus shows no line at all | add `custom_effect_tooltip = iran_arsenal_built_tt` and an `else` branch paying `add_equipment_to_stockpile = { type = infantry_equipment amount = 250 }` |
| `IR2_frontier_supply` | FUNCTIONAL | `iran_build_frontier_posts` (bunker in 419, guarded by ownership), `iran_frontier_programme` (opens `iran_frontier_subsidy`) | the bunker silently does nothing if 419 is lost | acceptable; the decision it unlocks is the durable half |
| `IR2_conscription_law` | FUNCTIONAL | +10000 MP, +0.10 WS | flag unread | keep |
| `IR2_volunteer_levy` | FUNCTIONAL | +8000 MP, +25 XP, +0.10 WS; sets the same `iran_conscription_law` flag | shares a flag with its alternative, which nothing reads | harmless |
| `IR2_air_and_gulf_services` | FUNCTIONAL | +25 air XP, +25 navy XP, `iran_air_programme`, `iran_gulf_priority` (both read) | — | keep |
| `IR2_officer_academy` | FUNCTIONAL | +25 XP, +1 research slot | flag unread | keep |
| `IR2_armored_detachment` | MISLEADING | +25 XP and 1000 **infantry** equipment | the text promises a squadron of light tanks and armoured cars | `add_equipment_to_stockpile = { type = light_tank_equipment amount = 150 }` (keep the infantry line only if the text changes) |
| `IR2_arsenal_expansion` | BROKEN | calls `iran_build_tehran_arsenal`, which its own ancestor `IR2_arsenal_network` has already run (`iran_tehran_arsenal_built`) | guaranteed no-op on every route: the focus prints no tooltip and changes nothing; it is also a leaf with no children, so the branch connects without it | give it a distinct payload: `266 = { add_building_construction = { type = arms_factory level = 2 instant_build = yes } } add_equipment_to_stockpile = { type = infantry_equipment amount = 500 }`, or fold it into `IR2_arsenal_network` |
| `IR2_frontier_divisions` | FUNCTIONAL | bunkers in 419 and 412 | flag unread | keep |
| `IR2_air_force_1930` | FUNCTIONAL | air base in 266, +25 air XP | — | keep |
| `IR2_navy_gulf` | FUNCTIONAL | dockyard in 411, +25 navy XP | — | keep |
| `IR2_supply_corps` | CONDITIONAL-MEANINGFUL | +25 XP, +0.10 WS | a 10-week focus for one training cycle | add `add_equipment_to_stockpile = { type = infantry_equipment amount = 500 }` and `set_country_flag = iran_reserve_programme` |
| `IR2_army_capstone` | FUNCTIONAL | +10000 MP, +25 CP, +25 XP | flag unread | keep |
| `IR2_treaties_of_sovereignty` | FUNCTIONAL | opens the whole `iran_sovereignty` decision category (`iran_foreign_programme`) | event 25 only re-sets the flag the focus already set | drop event 25 or give it a different payload (e.g. `add_to_variable = { iran_sovereignty = 3 }`) |
| `IR2_northern_treaty` | CONDITIONAL-MEANINGFUL | event 26: +25 SOV opinion | that is the entire reward; `iran_northern_treaty` is read nowhere | add `add_to_variable = { iran_northern_standing = 15 }` (the standing the preference spirits read) and `set_country_flag = iran_soviet_treaty` |
| `IR2_third_power_contacts` | FUNCTIONAL | event 15 (option a: 500 eq from GER), `iran_third_power` (feeds `iran_path_germany`) | — | keep |
| `IR2_soviet_treaty_1921` | FUNCTIONAL | `iran_reclaim_northern_large` (+8 sovereignty), +50 PP, +5% stab | — | keep |
| `IR2_apoc_negotiation_1933` | FUNCTIONAL | +10 oil in 413, +25 ENG opinion, `iran_oil_settlement_open` | duplicates `IR2_oil_renegotiation`'s outcome (they are mutually exclusive, so fine) | keep |
| `IR2_regional_nonaggression` | FUNCTIONAL | `iran_regional_programme` opens `iran_regional_assurances` (three guarantees) | the focus itself is a trickle | acceptable; the decision is the reward |
| `IR2_league_of_nations` | INEFFECTIVE | +50 PP, +5% stab; flag unread | a 7-week focus whose text claims a seat at Geneva but which changes nothing a decision or event can see | `add_to_variable = { iran_sovereignty = 5 }` + `add_opinion_modifier = { target = ENG modifier = iran_treaty_relations }` + keep the flag and read it in `IR2_regional_nonaggression.available` |
| `IR2_american_advisers` | CONDITIONAL-MEANINGFUL | +10 authority, +50 PP, +25 USA opinion, `PER_treasury_reformed` | the treasury flag is normally already set by then, so the reward is authority and opinion | add `set_country_flag = iran_customs_reformed` (the mission ran the customs) and `add_to_variable = { iran_sovereignty = constant:iran_story.sovereignty_reform_gain }` |
| `IR2_shatt_al_arab` | FUNCTIONAL | `iran_shatt_programme` opens `iran_shatt_negotiations` (event 60 to IRQ) | the focus itself pays only PP and stability | acceptable |
| `IR2_bahrain_question` | FUNCTIONAL | `iran_gulf_diplomacy_programme` opens `iran_gulf_arbitration` (ENG event 64 can cut leverage) | reward is PP/WS/stability only | acceptable |
| `IR2_turkish_frontier` | CONDITIONAL-MEANINGFUL | +25 TUR opinion, +5% stab; flag unread | the survey and the demarcation line exist only in the text | add `419 = { add_building_construction = { type = bunker level = 1 instant_build = yes } }` (the western frontier) and read the flag in `iran_frontier_subsidy` |
| `IR2_afghan_relations` | CONDITIONAL-MEANINGFUL | +25 AFG opinion, +10 authority; flag unread | same | add `set_country_flag = iran_regional_programme` (opens the guarantees decision) |
| `IR2_german_economic_mission` | FUNCTIONAL | +1000 eq from GER, civilian factory + slot in 266, `iran_concede_german_large`, +25 GER opinion, +50 PP/25 XP on the Germany path | 9 tooltip lines; the concession (German influence) is invisible in the text | hide the `if`-limited path bonus behind `hidden_effect`; mention the concession in `_desc` |
| `IR2_saadabad_prelude` | INEFFECTIVE | +50 PP, +5% stab; flag unread | it is the gate for `IR2_diplomacy_capstone` and pays nothing for itself; the pact it describes never exists | `give_guarantee = TUR` / `IRQ` / `AFG` behind `country_exists` guards, and `add_opinion_modifier` for each — the same mechanics `iran_regional_assurances` already uses |
| `IR2_arms_purchasing` | FUNCTIONAL | +1000 eq, +25 XP | flag unread | keep |
| `IR2_diplomacy_capstone` | CONDITIONAL-MEANINGFUL | +10 authority, +50 PP, +5% stab; flag unread | the capstone of the foreign spine changes no foreign value | add `add_to_variable = { iran_sovereignty = 5 }` and `add_opinion_modifier` on the four neighbours, or set `iran_regional_programme` |
| `IR2_regional_ambitions` | INEFFECTIVE | +50 PP, +5% stab; flag unread | the opening focus of the regional branch has no effect, and (see AI) the historical AI never takes it | `add_war_support = constant:iran_story.war_support_gain` + `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` + read the flag in `IR2_caucasus_interest.available` |
| `IR2_caucasus_interest` | INEFFECTIVE | `custom_effect_tooltip` that says the USSR will react, +50 PP, +5% stab | no reaction exists: the tooltip promises a mechanic that is not scripted, and the flag is read only by its own localisation line | `add_to_variable = { iran_northern_standing = -10 }` + `iran_concede_northern_small = yes` (a sphere intrusion costs sovereignty) + `set_country_flag = iran_regional_programme` |
| `IR2_mesopotamia_interest` | INEFFECTIVE | `custom_effect_tooltip` that says Iraq and Britain will react, +0.10 WS, +5% stab | same: no reaction is scripted | `add_to_variable = { iran_british_standing = -10 }` + `add_war_support = 0.10` + `set_country_flag = iran_shatt_programme` (opens the Shatt negotiations) |
| `IR2_gulf_islands` | INEFFECTIVE | `custom_effect_tooltip` claiming Britain will refuse to negotiate, +0.10 WS, +50 PP | nothing follows from the claim; `iran_gulf_islands_claim` is read nowhere | `iran_reclaim_british_small = yes` (−8 ENG influence, +4 sovereignty) + `add_opinion_modifier = { target = ENG modifier = iran_oil_dispute }` (an existing −30 modifier) |
| `IR2_afghan_influence` | CONDITIONAL-MEANINGFUL | +25 AFG opinion, +50 PP; flag unread | consuls and schools produce no presence | add `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` and `set_country_flag = iran_regional_programme` |
| `IR2_caspian_fisheries` | FUNCTIONAL | infrastructure in 420, `iran_reclaim_northern_small` (+4 sovereignty) | — | keep (fix the duplicate title, see next row) |
| `IR2_regional_capstone` | CONDITIONAL-MEANINGFUL | +10 authority, +50 PP, +5% stab; flag unread | the regional capstone is indistinguishable from a mid-tree political focus | add `add_to_variable = { iran_sovereignty = 8 }` and `add_research_slot = 1` is out of place; prefer `set_country_flag = iran_regional_programme add_opinion_modifier` on the four neighbours |
| `IR2_shatt_navigation_rights` | CONDITIONAL-MEANINGFUL | +50 PP, +25 IRQ opinion; flag unread | a treaty focus with no treaty consequence | add `add_to_variable = { iran_british_standing = 5 } add_to_variable = { iran_sovereignty = 4 }` and `set_country_flag = iran_shatt_settled` is set by IRQ, so read it here instead |
| `IR2_caucasus_refugees` | CONDITIONAL-MEANINGFUL | +8000 MP, −5% stab | the registration the text describes produces no administration | add `add_to_variable = { iran_authority = constant:iran_story.authority_gain }` |
| `IR2_caspian_caviar_trade` | MISLEADING | +400 fuel, +50 PP, +5% stab | its title is identical to `IR2_caspian_fisheries` (‘The Caspian Fisheries’) although its localisation key differs, and it gives no ground on the concession it describes | rename the loc key to ‘The Caviar Trade’; add `iran_reclaim_northern_small = yes` |


## (a) Ideas referenced by focus rewards

**No `completion_reward` in `iran_interwar.txt` contains `add_ideas` or `remove_ideas`.** Every national spirit in this
chapter arrives through `iran_refresh_mechanics` (state spirits, Great Game preference spirits, foreign dependence,
divided officer corps) or through the four `iran_settle_*` effects. That is why so many focuses feel like they do
nothing: on a settled route the refresh removes and re-adds the identical list.

| idea | defined? | who adds it | who removes it | reachable on which route |
| --- | --- | --- | --- | --- |
| `iran_fragmented_authority` | yes, `common/ideas/iran_campaign.txt` | `iran_refresh_mechanics` (no settlement flag, authority < 65) | same effect | all, until authority ≥ 65 or a settlement flag exists |
| `iran_constitutional_state` / `_consolidated` | yes | refresh (`iran_constitutional_settled`) | refresh | constitutional only |
| `iran_qajar_state` / `_consolidated` | yes | refresh (`iran_qajar_restoration`, `iran_restoration_settled`) | refresh / settle | Qajar only |
| `iran_pahlavi_state` / `_consolidated` | yes | refresh (`iran_pahlavi`, `iran_pahlavi_settled`) | refresh | Pahlavi only |
| `iran_parliamentary_state` / `_consolidated` | yes | refresh (`iran_republic`, `iran_republic_settled`) | refresh | republic only |
| `iran_nationalist_state` / `_consolidated` | yes | refresh (`iran_nationalist_front`, `iran_nationalist_settled`) | refresh | nationalist front only |
| `iran_socialist_state` / `_consolidated` | yes | refresh (`iran_socialist`, `iran_socialist_settled`) | refresh | socialist only |
| `iran_foreign_dependence` | yes | refresh while `iran_foreign_leverage ≥ 40` | refresh | all |
| `iran_divided_officer_corps` | yes | refresh while `iran_officer_loyalty < 40` and date > 1919 | refresh | all |
| `iran_british_preference` / `iran_soviet_preference` / `iran_balancing_powers` | yes | refresh, from the two standings vs 60/45 | refresh | all |
| `iran_pahlavi_autocracy` | yes | `PER_bop_sync` under a Pahlavi flag without `PER_majlis_resurgence` | `PER_bop_sync` | Pahlavi only (needs Arms Against Tyranny) |
| `iran_competing_concessions` | yes | `iran_influence_tick` (British loan + northern railway) | `iran_influence_tick` | all |
| `iran_sovereignty_capitulations` / `_constrained` / `_assertive` / `_sovereign` | yes | `iran_influence_tick` by sovereignty band | `iran_influence_tick` | all |

No focus in this file can add a spirit Iran cannot possess: every id above is defined and every one of them is granted
by a route that exists. The reverse problem is real, however: **13 state/consolidated spirits and
`iran_foreign_dependence` / `iran_divided_officer_corps` are never tested by any `has_idea` trigger** — they work only
through their modifiers, so a focus that merely re-runs the refresh is invisible in play.

## (b) Tooltips likely to be long

Estimated visible lines after expanding the effects (flags, `hidden_effect`, `iran_refresh_mechanics` and
`mark_focus_tree_layout_dirty` contribute none). Mean is 3.4 lines; 16 focuses reach 6 or more:

| lines | focus | cause |
| --- | --- | --- |
| 11 | `IR2_qajar_restoration` | `iran_settle_qajar_restoration` body is not hidden |
| 10 | `IR2_socialist_republic` | `iran_settle_socialist` body not hidden |
| 10 | `IR2_parliamentary_republic` | `iran_settle_republic` body not hidden |
| 10 | `IR2_nationalist_front` | `iran_settle_nationalist` body not hidden |
| 9 | `IR2_pahlavi_settlement` | `iran_settle_pahlavi` body not hidden |
| 9 | `IR2_german_economic_mission` | equipment + factory + slot + disposal + two `if` blocks |
| 7 | `IR2_tribal_disarmament` | `if`-limited gendarmerie bonus prints as a block |
| 7 | `IR2_khuzestan_oil` | event + resource + PP + concession + `if` block |
| 7 | `IR2_foreign_concessions` | event + equipment + concession, twice |
| 7 | `IR2_constitutional_crown` | settle body + 3 payouts |
| 6 | `IR2_treasury_commission` | double authority payment in an `if` |
| 6 | `IR2_trans_iranian_railway` | four state blocks |
| 6 | `IR2_the_state_in_1935` | two events + 4 payouts |
| 6 | `IR2_pahlavi_capstone` | factory + slot + disposal + payouts |
| 6 | `IR2_loyal_division` | 5 payouts + event |
| 6 | `IR2_constitutional_capstone` | disposal + push + popularity + payouts |

The single largest cause is the six settlement focuses: the four `iran_settle_*` effects are called unhidden, so each
prints `set_politics`, `promote_character`, the authority line and the stability line. Wrapping each call in
`hidden_effect = { ... }` with one `custom_effect_tooltip` removes ~6 lines from five of the six.

## (c) AI value

`ai_will_do` is present on all 139 focuses (none falls back to the default 1). 24 focuses carry a `factor = 0`
modifier, i.e. the AI never takes them under some condition:

- **`is_historical_focus_on` = 0 (17):** `IR2_accept_the_agreement`, `IR2_british_advisers`, `IR2_gilan_republic`,
  `IR2_jangali_congress`, `IR2_soviet_accord`, `IR2_socialist_congress`, `IR2_nationalist_movement`,
  `IR2_nationalist_press`, `IR2_nationalist_officers`, `IR2_qajar_restoration`, `IR2_constitutional_crown`,
  `IR2_parliamentary_republic`, `IR2_nationalist_front`, `IR2_socialist_republic`, `IR2_american_advisers`,
  `IR2_regional_ambitions`.
- **`has_war` = 0 (6):** `IR2_gulf_claims`, `IR2_shatt_al_arab`, `IR2_bahrain_question`, `IR2_gulf_islands`,
  `IR2_caucasus_interest`, `IR2_mesopotamia_interest`.
- **`has_country_flag = iran_republic` = 0:** `IR2_foreign_concessions`.

Consequences and risks:

1. **Five of the six settlements are worth 0 to the historical AI.** Only `IR2_pahlavi_settlement` has weight
   (`@priority` ×5). Its `available` needs `iran_reza_influence ≥ 60` **and** (`iran_cossack_ascendant` or
   `iran_reza_khan_minister`) **and** (`iran_path_army` or not `iran_path_majlis`). If the historical AI reaches 1925
   on a Majlis-tinted path (event 22 option b sets `iran_constitution_secured`, which makes `iran_path_majlis` true and
   `iran_path_army` false), **no settlement is available to it at all** and the tree dead-ends at y=8 until
   `iran_campaign_tick` force-settles Pahlavi after 1936.6.30. Option 22.b has `factor = 0` under historical AI, so in
   practice the deadlock is avoided by a weight, not by a gate — worth an explicit fallback.
2. **The whole regional branch is dead for the AI.** `IR2_regional_ambitions` has `factor = 0` under historical AI, and
   every other focus in the branch sits below it, so ten focuses never open
   (`IR2_caucasus_interest`, `IR2_mesopotamia_interest`, `IR2_gulf_islands`, `IR2_afghan_influence`,
   `IR2_caspian_fisheries`, `IR2_shatt_navigation_rights`, `IR2_caucasus_refugees`, `IR2_regional_capstone`,
   `IR2_caspian_caviar_trade`). They are also the weakest rewards in the file (see table).
3. **The Gilan/socialist chain is AI-dead** (`IR2_gilan_republic`, `IR2_jangali_congress`, `IR2_soviet_accord`,
   `IR2_socialist_congress` = 0 historical), which is consistent: `IR2_socialist_republic` also needs
   `iran_jangali_congress`, so the socialist settlement can never be reached by the AI at all.
4. **The Pahlavi/alternative programme pairs are gated by settlement flags, not by `mutually_exclusive`.**
   `IR2_trans_iranian_railway` / `IR2_state_railways`, `IR2_unified_command` / `IR2_general_staff`,
   `IR2_conscription_law` / `IR2_volunteer_levy`, `IR2_tehran_university` / `IR2_state_university`,
   `IR2_customs_reform` / `IR2_national_tariff_office` are all siblings that both stay legal for a player who takes one
   before settling and the other after (e.g. railway infrastructure is added to 410 twice). Add
   `mutually_exclusive` to each pair.
5. **No `ai_will_do` is missing**, so the AI never stalls on a focus it cannot weight; the stall risk is entirely in
   `available`.

## Systemic findings (worst first)

1. **`IR2_customs_reform` and `IR2_national_tariff_office` set `iran_customs_reform`; the game reads
   `iran_customs_reformed`.** The only writer of the correct flag is a decision in `common/decisions/iran_foreign_agreements.txt`.
   Neither focus can start the monthly sovereignty recovery they exist to start (one character).
2. **`IR2_arsenal_expansion` can never do anything.** Its ancestor `IR2_arsenal_network` always runs
   `iran_build_tehran_arsenal` first, which is guarded by `iran_tehran_arsenal_built`; the later focus is a silent no-op,
   and it is a childless leaf.
3. **Three focuses build in state 415, which is owned by Afghanistan** (`IR2_trans_iranian_railway`,
   `IR2_state_railways`, `IR2_road_programme`). The Trans-Iranian Railway and the Khorasan road are partly built abroad.
4. **76 flags set by rewards are read nowhere** — e.g. `iran_nationalist_movement`, `iran_league_member`,
   `iran_saadabad_prelude`, `iran_regional_ambitions`, `iran_civil_code`, `iran_army_settled`, `iran_interwar_settled`.
   These are the "reward looks like nothing happened" cases.
5. **Three focuses are a bare `custom_effect_tooltip` that promises a reaction no script produces**
   (`IR2_caucasus_interest`, `IR2_mesopotamia_interest`, `IR2_gulf_islands`). The tooltips say the USSR, Iraq/Britain and
   Britain "will react"; nothing reads `iran_caucasus_interest`, `iran_mesopotamia_interest` or
   `iran_gulf_islands_claim` outside their own localisation lines.
6. **Eight focuses are pure political-power/stability trickles** (`IR2_nationalist_movement`, `IR2_electoral_law`,
   `IR2_saadabad_prelude`, `IR2_league_of_nations`, `IR2_regional_ambitions`, `IR2_caucasus_interest`,
   `IR2_mesopotamia_interest`, `IR2_gulf_islands`) — the class the brief calls INEFFECTIVE.
7. **The four settlement effects print their whole body** into six capstone tooltips (up to 11 lines). This is the same
   class of bug the lead already fixed for `iran_refresh_mechanics`, one layer out.
8. **Reward text and reward effect disagree** in six places: `IR2_urban_works` (streets → anti-air gun),
   `IR2_state_enterprises` (mills → arms factory), `IR2_armored_detachment` (tanks → infantry equipment),
   `IR2_landlord_settlement` (harvests → a road in Khuzestan), `IR2_press_restraint` (licensing newspapers → a
   concession to a foreign power) and `IR2_caspian_caviar_trade` (title duplicates `IR2_caspian_fisheries`).
9. **Two focuses pay the same credit twice**: `IR2_accept_the_agreement` gives 500 equipment and then fires event 14,
   whose option a gives another 500; `IR2_foreign_concessions` applies `iran_concede_british_small` twice on the oil path.
10. **Every Crown/Majlis push in this file is conditional on `has_power_balance`.** 21 focuses contain one, and under
    the Pahlavi settlement the balance is removed while without Arms Against Tyranny it is never created. For three of
    them (`IR2_court_ministries`, `IR2_national_union`, `IR2_elections_1928`) the push is the entire reward, so on those
    routes they pay only political power and stability.

## Not verified

Nothing here has been run in game. The state-ownership findings come from `history/states/*.txt` `owner =` lines and
should be re-checked if any Iran state is transferred by event before these focuses fire. Tooltip line counts are
estimates from the script, not screenshots.
