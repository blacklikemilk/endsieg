# Iran focus icon assignment (vanilla and DLC art)

Every Iran focus points at a sprite that ships with Hearts of Iron IV or one of its DLC.
No custom art is needed and nothing is registered in `interface/iran_campaign.gfx` any more.

Regenerate with `python tools/assign_iran_icons.py --game <install> --mod <mod root>`;
verify with the same command plus `--check`.

## Pool

Vanilla ships a 272-focus Persian tree whose icons are purpose-made for Iran - the Trans-Iranian Railway,
the oil nationalisation, the Qajar restoration, SAVAK, the Bakhtiari levy. Those are used first in every family;
Afghan, Iraqi and Turkish art fills the gaps, then generic economic and military sprites.

## Coverage

- 307 focuses assigned, 117 distinct icons, 0 unresolved.
- Families: parliament 58, army 42, government 30, industry 29, monarchy 28, hand-picked 16, oil 15, socialism 12, finance 11, sovereignty 7, expansion 7, education 7, air 5, navy 5, tribes 4, intel 4, food 4, britain 4, media 3, railway 3, soviet 3, succession 3, trade 2, germany 2, invasion 2, religion 1.
- Most repeated icon: `GFX_focus_generic_treaty` on 12 focuses.

## Assignment by family

### air (5)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_air_detachment` | A Persian Air Detachment | `GFX_focus_PER_establish_airforce` |
| `IR2_air_and_gulf_services` | Air and Gulf Services | `GFX_focus_PER_raf_planes` |
| `IR2_air_force_1930` | The Persian Air Force | `GFX_focus_PER_luftwaffe_planes` |
| `IR3_air_wing` | An Air Wing | `GFX_focus_SOV_flying_clubs` |
| `IR3_airfield_network` | An Airfield Network | `GFX_goal_generic_build_airforce` |

### army (42)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_azerbaijan_command` | The Azerbaijan Command | `GFX_focus_PER_special_forces_program` |
| `IR1_cossack_command` | The Cossack Command | `GFX_focus_generic_military_academy` |
| `IR1_cossack_pay` | Pay the Cossack Brigade | `GFX_goal_generic_allies_build_infantry` |
| `IR1_divided_command` | A Divided Command | `GFX_focus_PER_restructure_army` |
| `IR1_frontier_posts` | Frontier Posts | `GFX_focus_generic_truck` |
| `IR1_military_finance` | Military Finance | `GFX_focus_generic_military_mission` |
| `IR1_officers_college` | An Officers' College | `GFX_goal_generic_army_artillery` |
| `IR1_reserve_service` | Reserve Service | `GFX_focus_generic_limited_social_mobilization` |
| `IR1_rifle_contracts` | Rifle Contracts | `GFX_focus_PER_desert_training` |
| `IR1_swedish_officers` | The Swedish Officers | `GFX_focus_PER_expand_imperial_guard` |
| `IR1_wartime_mobilization` | Wartime Mobilization | `GFX_focus_generic_full_social_mobilization` |
| `IR2_armored_detachment` | An Armoured Detachment | `GFX_focus_generic_military_mission` |
| `IR2_arms_purchasing` | Arms Purchases | `GFX_focus_BRA_acquire_german_tanks` |
| `IR2_army_capstone` | The Army of the State | `GFX_focus_PER_czech_tanks` |
| `IR2_civilian_control` | Civilian Command | `GFX_focus_secret_rearmament` |
| `IR2_conscription_law` | The Conscription Law | `GFX_focus_PER_special_forces_program` |
| `IR2_cossack_brigade` | The Cossack Command | `GFX_focus_PER_czech_tanks` |
| `IR2_domestic_capital` | Mobilize Domestic Capital | `GFX_goal_generic_allies_build_infantry` |
| `IR2_frontier_divisions` | Frontier Divisions | `GFX_focus_generic_limited_social_mobilization` |
| `IR2_frontier_supply` | Supply the Frontiers | `GFX_focus_PER_desert_training` |
| `IR2_land_to_the_peasants` | Land to the Villagers | `GFX_focus_PER_expand_imperial_guard` |
| `IR2_national_militia` | The National Militia | `GFX_focus_PER_restructure_army` |
| `IR2_nationalist_officers` | Officers of the Nation | `GFX_focus_BRA_acquire_german_tanks` |
| `IR2_provincial_army` | A Provincial Army | `GFX_focus_generic_truck` |
| `IR2_red_gendarmes` | The Red Gendarmes | `GFX_focus_generic_military_academy` |
| `IR2_supply_corps` | The Supply Corps | `GFX_focus_generic_full_social_mobilization` |
| `IR2_unified_command` | A Unified Command | `GFX_goal_generic_army_artillery` |
| `IR3_armoured_brigade` | An Armoured Brigade | `GFX_focus_generic_military_mission` |
| `IR3_army_capstone` | The Army of Iran | `GFX_focus_BRA_acquire_german_tanks` |
| `IR3_conscription_expansion` | Expand the Conscription | `GFX_focus_PER_desert_training` |
| `IR3_defence_of_iran` | The Defence of Iran | `GFX_goal_generic_army_artillery` |
| `IR3_development_corps` | A Development Corps | `GFX_focus_PER_restructure_army` |
| `IR3_mountain_brigades` | Mountain Brigades | `GFX_focus_generic_limited_social_mobilization` |
| `IR3_national_army` | A National Army | `GFX_focus_generic_military_academy` |
| `IR3_national_mobilisation` | National Mobilisation | `GFX_focus_PER_expand_imperial_guard` |
| `IR3_national_resistance` | National Resistance | `GFX_focus_secret_rearmament` |
| `IR3_officer_corps_1940` | The Officer Corps | `GFX_focus_PER_czech_tanks` |
| `IR3_peoples_army` | A People's Army | `GFX_goal_generic_allies_build_infantry` |
| `IR3_professional_reserves` | Professional Reserves | `GFX_focus_generic_truck` |
| `IR3_resistance_council` | A Council of Resistance | `GFX_focus_secret_rearmament` |
| `IR3_supply_network` | The Supply Network | `GFX_focus_generic_full_social_mobilization` |
| `IR3_zagros_defences` | Defend the Western Approaches | `GFX_focus_PER_special_forces_program` |

### britain (4)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_british_loan` | A British Loan | `GFX_focus_PER_our_place_in_empire` |
| `IR1_entente_understanding` | An Entente Understanding | `GFX_goal_tripartite_pact` |
| `IR2_british_advisers` | The Armitage-Smith Mission | `GFX_goal_generic_intelligence_exchange` |
| `IR3_british_ultimatum_response` | The British Ultimatum | `GFX_focus_generic_commonwealth_build_infantry` |

### education (7)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR2_iranian_academy` | The Iranian Academy | `GFX_focus_PER_shiraz_university` |
| `IR2_military_academy` | The Military Academy | `GFX_focus_PER_university_of_isfahan` |
| `IR2_officer_academy` | A Staff College | `GFX_focus_PER_imperial_funded_universities` |
| `IR2_schools_and_workshops` | Schools and Workshops | `GFX_focus_generic_university_1` |
| `IR2_tehran_university` | The University of Tehran | `GFX_focus_research` |
| `IR3_agriculture_1940` | The Land in Wartime | `GFX_focus_generic_university_2` |
| `IR3_technical_education` | Technical Education | `GFX_focus_PER_national_museum` |

### expansion (7)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_niedermayer_expedition` | The Niedermayer Mission | `GFX_focus_PER_demand_iraqi_territory` |
| `IR2_afghan_influence` | Influence in Afghanistan | `GFX_focus_PER_proclaim_greater_iran` |
| `IR2_caucasus_interest` | Interests in the Caucasus | `GFX_focus_PER_secure_afghanistan` |
| `IR2_gulf_claims` | Claims in the Gulf | `GFX_focus_PER_demand_afghan_territory` |
| `IR2_gulf_islands` | The Gulf Islands | `GFX_focus_generic_attack_afghanistan` |
| `IR2_mesopotamia_interest` | The Mesopotamian Question | `GFX_focus_generic_attack_iraq` |
| `IR2_shatt_al_arab` | The Shatt al-Arab Question | `GFX_focus_PER_secure_iraq` |

### finance (11)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_a_national_budget` | A National Budget | `GFX_focus_usa_reestablish_the_gold_standard` |
| `IR1_belgian_advisers` | Belgian Customs Advisers | `GFX_focus_generic_university_2` |
| `IR1_customs_revenue` | Put Customs to Work | `GFX_focus_PER_abolish_feudalism` |
| `IR1_empty_treasury` | The Empty Treasury | `GFX_focus_PER_national_bank` |
| `IR1_shuster_mission` | Shuster's Financial Mission | `GFX_focus_mex_privatisation` |
| `IR1_state_bank` | A State Bank | `GFX_focus_PER_national_bank` |
| `IR1_wartime_budget` | A Wartime Budget | `GFX_focus_mex_privatisation` |
| `IR2_american_advisers` | The American Financial Mission | `GFX_focus_generic_university_2` |
| `IR2_economic_capstone` | The National Economy | `GFX_focus_usa_reestablish_the_gold_standard` |
| `IR2_treasury_commission` | The Treasury Commission | `GFX_focus_PER_abolish_feudalism` |
| `IR3_economy_capstone` | A Balanced Economy | `GFX_focus_PER_national_bank` |

### food (4)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_agricultural_relief` | Relief for the Countryside | `GFX_focus_generic_agricultural_subsidies` |
| `IR1_protect_the_harvest` | Protect the Harvest | `GFX_focus_mex_privatisation` |
| `IR1_the_great_famine` | The Hunger Years | `GFX_focus_PER_abolish_feudalism` |
| `IR3_grain_reserves` | Grain Reserves | `GFX_focus_generic_land_reclamation` |

### germany (2)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_german_opening` | A German Opening | `GFX_goal_generic_positive_trade_relations` |
| `IR3_german_opening` | The German Opening | `GFX_focus_chi_mission_to_germany` |

### government (30)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_army_of_the_constitution` | An Army of the Constitution | `GFX_focus_generic_support_the_left_right` |
| `IR1_defend_constitution` | Defend the Constitution | `GFX_focus_ICE_state_corporatism` |
| `IR1_law_in_the_provinces` | Law in the Provinces | `GFX_focus_generic_treaty` |
| `IR1_officer_loyalty` | Officers and the Government | `GFX_focus_PER_iran_first` |
| `IR1_public_granaries_1917` | Public Granaries | `GFX_goal_generic_construct_civ_factory` |
| `IR1_refugee_administration` | Refugees and the Provinces | `GFX_focus_AFG_parliamentary_democracy` |
| `IR2_agricultural_credit` | Credit for the Villages | `GFX_focus_PER_iran_first` |
| `IR2_cabinet_responsibility` | A Cabinet Answerable to the Majlis | `GFX_focus_ICE_state_corporatism` |
| `IR2_command_and_cabinet` | Command and Cabinet | `GFX_focus_generic_treaty` |
| `IR2_constitutional_army` | An Army under the Law | `GFX_focus_AFG_parliamentary_democracy` |
| `IR2_constitutional_capstone` | The Constitutional Order | `GFX_focus_generic_treaty` |
| `IR2_landlord_settlement` | A Settlement with the Landlords | `GFX_goal_generic_construct_civ_factory` |
| `IR2_parliamentary_republic` | A Parliamentary Republic | `GFX_focus_generic_support_the_left_right` |
| `IR2_provincial_compacts_ii` | Compacts with the Provinces | `GFX_focus_PER_iran_first` |
| `IR2_republic_capstone` | The Republic Established | `GFX_focus_generic_support_the_left_right` |
| `IR2_republican_constitution` | The Republican Constitution | `GFX_goal_generic_construct_civ_factory` |
| `IR2_responsible_government` | Responsible Government | `GFX_focus_ICE_state_corporatism` |
| `IR2_urban_works` | Public Works in the Capital | `GFX_focus_AFG_parliamentary_democracy` |
| `IR3_cabinet_stability` | A Cabinet That Lasts | `GFX_focus_AFG_parliamentary_democracy` |
| `IR3_civil_defence` | Civil Defence | `GFX_focus_generic_support_the_left_right` |
| `IR3_constitutional_1945` | The Constitution Holds | `GFX_focus_generic_treaty` |
| `IR3_constitutional_wartime` | Constitutional Government at War | `GFX_focus_PER_iran_first` |
| `IR3_direct_administration` | Direct Administration | `GFX_focus_ICE_state_corporatism` |
| `IR3_northern_settlement` | The Northern Settlement | `GFX_focus_AFG_parliamentary_democracy` |
| `IR3_provincial_compacts` | Provincial Compacts | `GFX_focus_generic_treaty` |
| `IR3_public_granaries` | Public Granaries | `GFX_goal_generic_construct_civ_factory` |
| `IR3_republic_wartime` | A Republic at War | `GFX_focus_ICE_state_corporatism` |
| `IR3_republican_defence` | Defence of the Republic | `GFX_goal_generic_construct_civ_factory` |
| `IR3_tehran_water` | Water for Tehran | `GFX_focus_PER_iran_first` |
| `IR3_wartime_government` | A Wartime Government | `GFX_focus_generic_support_the_left_right` |

### hand-picked (16)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_bushehr_trade` | Trade through Bushehr | `GFX_focus_generic_merchant_fleet` |
| `IR1_diplomatic_corps` | A Diplomatic Corps | `GFX_goal_generic_major_alliance` |
| `IR1_foreign_advisers` | Foreign Advisers | `GFX_focus_generic_military_mission` |
| `IR1_grain_requisition` | Requisition the Harvest | `GFX_focus_generic_agricultural_subsidies` |
| `IR1_gulf_ports` | Ports of the Gulf | `GFX_focus_PER_persian_gulf_fleet` |
| `IR1_second_majlis` | The Second Majlis | `GFX_focus_POL_complete_april_constitution` |
| `IR2_german_economic_mission` | The German Economic Mission | `GFX_goal_generic_positive_trade_relations` |
| `IR2_industrial_bank` | An Industrial Bank | `GFX_focus_PER_national_bank` |
| `IR2_press_restraint` | Restraint of the Press | `GFX_focus_SWE_radiotjanst` |
| `IR2_soviet_trade` | Trade with the Soviet Union | `GFX_focus_PER_tehran_moscow_pact` |
| `IR2_soviet_treaty_1921` | The Treaty of 1921 | `GFX_focus_chi_mission_to_the_soviet_union` |
| `IR2_textile_industry` | A Textile Industry | `GFX_goal_generic_construct_civ_factory` |
| `IR2_trans_iranian_railway` | The Trans-Iranian Railway | `GFX_focus_generic_railroad` |
| `IR3_occupation_government` | Government under Occupation | `GFX_focus_CZE_german_puppet` |
| `IR3_persian_corridor` | The Persian Corridor | `GFX_focus_PER_expand_tehran_abbas` |
| `IR3_republic_1945` | The Republic in the Peace | `GFX_focus_PER_iran_first` |

### industry (29)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_caspian_communications` | Caspian Communications | `GFX_focus_generic_low_cost_housing` |
| `IR1_domestic_workshops` | Support Persian Workshops | `GFX_goal_generic_construct_civ_factory` |
| `IR1_gulf_lifeline` | The Gulf Lifeline | `GFX_focus_ARG_develop_the_electricity_sector` |
| `IR1_road_to_the_caspian` | The Road to the Caspian | `GFX_goal_generic_construct_mil_factory` |
| `IR1_tabriz_workshops` | Workshops in Tabriz | `GFX_focus_generic_modernize_industry` |
| `IR1_tehran_arsenal` | The Tehran Arsenal | `GFX_focus_generic_industry_3` |
| `IR2_an_integrated_market` | An Integrated Market | `GFX_goal_generic_construct_civ_factory` |
| `IR2_arsenal_expansion` | The Tehran Arsenal | `GFX_focus_ARG_develop_the_electricity_sector` |
| `IR2_arsenal_network` | An Arsenal Network | `GFX_focus_generic_low_cost_housing` |
| `IR2_caspian_fisheries` | The Caspian Fisheries | `GFX_goal_generic_construct_civ_factory` |
| `IR2_caspian_roads_project` | The Caspian Road | `GFX_goal_generic_construct_mil_factory` |
| `IR2_mining_survey` | The Mining Survey | `GFX_focus_generic_modernize_industry` |
| `IR2_road_programme` | The Trunk Roads | `GFX_focus_generic_industry_3` |
| `IR2_state_enterprises` | State Factories | `GFX_focus_generic_rubber` |
| `IR2_third_power_contacts` | Third-Power Contacts | `GFX_focus_generic_rubber` |
| `IR3_a_country_at_work` | A Country at Work | `GFX_goal_generic_construct_mil_factory` |
| `IR3_american_mission` | The American Mission | `GFX_goal_generic_construct_civ_factory` |
| `IR3_arsenal_programme` | The Arsenal Programme | `GFX_focus_generic_rubber` |
| `IR3_bandar_shahpur` | Bandar Shahpur | `GFX_focus_generic_modernize_industry` |
| `IR3_cement_and_power` | Cement and Electric Power | `GFX_goal_generic_construct_mil_factory` |
| `IR3_industrial_programme` | The Industrial Programme | `GFX_focus_generic_modernize_industry` |
| `IR3_logistics_commission` | The Logistics Commission | `GFX_focus_ARG_develop_the_electricity_sector` |
| `IR3_national_workshops` | National Workshops | `GFX_focus_generic_industry_3` |
| `IR3_price_controls` | Price Controls | `GFX_focus_generic_industry_3` |
| `IR3_reconstruction_1945` | Reconstruction Begins | `GFX_focus_ARG_develop_the_electricity_sector` |
| `IR3_seventh_plan` | The Seventh Plan | `GFX_focus_generic_rubber` |
| `IR3_steel_mill` | A Steel Mill | `GFX_goal_generic_construct_civ_factory` |
| `IR3_trans_iranian_connections` | Trans-Iranian Connections | `GFX_focus_generic_low_cost_housing` |
| `IR3_wartime_industry` | Wartime Industry | `GFX_focus_generic_low_cost_housing` |

### intel (4)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_gendarmerie_recruitment` | Recruit the Gendarmerie | `GFX_goal_generic_intelligence_exchange` |
| `IR1_gendarmerie_resistance` | The Gendarmerie Stands | `GFX_focus_generic_conspiracy` |
| `IR1_national_gendarmerie` | A National Gendarmerie | `GFX_focus_generic_secret_service_agency` |
| `IR1_treasury_gendarmerie` | A Treasury Gendarmerie | `GFX_focus_PER_form_savak` |

### invasion (2)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_armistice_watch` | The Armistice | `GFX_focus_PER_push_to_deserts` |
| `IR1_independence_at_the_peace` | Independence at the Peace | `GFX_focus_generic_provoke_border_clashes` |

### media (3)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_press_and_debate` | Press and Debate | `GFX_focus_SWE_radiotjanst` |
| `IR2_land_reform_debate` | The Land Question | `GFX_focus_PER_stage_mass_protests` |
| `IR2_nationalist_press` | The Nationalist Press | `GFX_focus_generic_workers` |

### monarchy (28)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_army_of_the_crown` | An Army of the Crown | `GFX_focus_generic_monarchy_1` |
| `IR1_constitution_or_crown` | Constitution or Crown | `GFX_focus_PER_his_fathers_footsteps` |
| `IR1_court_and_cabinet` | Court and Cabinet | `GFX_focus_research` |
| `IR1_court_patronage` | The Court's Patronage | `GFX_focus_generic_monarchy_1` |
| `IR1_palace_guard` | The Palace Guard | `GFX_focus_generic_monarchy_2` |
| `IR1_regency_council` | A Council of Regency | `GFX_focus_PER_emperor_for_people` |
| `IR1_royal_household` | The Royal Household | `GFX_focus_PER_shahanshah` |
| `IR1_royal_prerogative` | The Royal Prerogative | `GFX_focus_PER_embrace_opulence` |
| `IR1_the_young_shah` | The Young Shah | `GFX_focus_PER_choose_a_shahbanu` |
| `IR2_constitutional_crown` | The Constitutional Crown | `GFX_focus_generic_monarchy_2` |
| `IR2_court_ministries` | Ministries of the Court | `GFX_focus_PER_his_fathers_footsteps` |
| `IR2_governors_of_the_crown` | Governors of the Crown | `GFX_focus_PER_embrace_opulence` |
| `IR2_household_brigade` | The Household Brigade | `GFX_focus_research` |
| `IR2_pahlavi_army` | The Pahlavi Army | `GFX_focus_generic_monarchy_2` |
| `IR2_pahlavi_capstone` | The Pahlavi State | `GFX_focus_PER_choose_a_shahbanu` |
| `IR2_pahlavi_settlement` | The Pahlavi Settlement | `GFX_focus_PER_choose_a_shahbanu` |
| `IR2_qajar_restoration` | The Restoration of the Qajars | `GFX_focus_PER_shahanshah` |
| `IR2_royal_administration` | A Royal Administration | `GFX_focus_PER_shahanshah` |
| `IR2_royal_authority` | The Crown's Authority | `GFX_focus_PER_emperor_for_people` |
| `IR2_royal_works` | Works of the Crown | `GFX_focus_generic_monarchy_1` |
| `IR3_court_wartime` | The Court in Wartime | `GFX_focus_PER_shahanshah` |
| `IR3_household_army` | The Household Regiments | `GFX_focus_generic_monarchy_2` |
| `IR3_mohammad_reza` | The Young Shah | `GFX_focus_PER_emperor_for_people` |
| `IR3_pahlavi_1945` | The Crown Endures | `GFX_focus_generic_monarchy_1` |
| `IR3_pahlavi_progress` | The Pahlavi Programme | `GFX_focus_PER_embrace_opulence` |
| `IR3_royal_army` | The Royal Army | `GFX_focus_research` |
| `IR3_royal_finance` | The Royal Finances | `GFX_focus_PER_choose_a_shahbanu` |
| `IR3_wartime_regency` | A Council of Regency | `GFX_focus_PER_his_fathers_footsteps` |

### navy (5)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_gulf_flotilla` | A Gulf Flotilla | `GFX_focus_PER_establish_the_navy` |
| `IR2_gulf_harbour_project` | The Gulf Harbour | `GFX_focus_PER_persian_gulf_fleet` |
| `IR2_navy_gulf` | The Gulf Squadron | `GFX_focus_PER_bolster_the_caspian` |
| `IR3_gulf_service` | The Gulf Service | `GFX_goal_generic_construct_naval_dockyard` |
| `IR3_naval_patrol` | Naval Patrol | `GFX_focus_FIN_coastal_defense` |

### oil (15)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_abadan_concession` | The Abadan Concession | `GFX_focus_PER_nationalize_oil_fields` |
| `IR1_concession_guarantees` | Guarantees for the Concession | `GFX_goal_generic_oil_refinery` |
| `IR1_oil_royalty_share` | Reopen the Royalty | `GFX_focus_PER_form_oil_company` |
| `IR1_south_persia_oil` | Oil in the South | `GFX_focus_PER_oil_baron` |
| `IR2_anti_concession` | Against the Concessions | `GFX_focus_PER_donate_oil_fields` |
| `IR2_apoc_negotiation_1933` | Negotiating with the Company | `GFX_focus_PER_oil_baron` |
| `IR2_foreign_concessions` | Foreign Concessions | `GFX_focus_generic_resource_extraction` |
| `IR2_khuzestan_oil` | Khuzestan Oil | `GFX_focus_PER_nationalize_oil_fields` |
| `IR2_oil_renegotiation` | The Oil Agreement of 1933 | `GFX_focus_PER_form_oil_company` |
| `IR2_oil_revision` | Revising the Concession | `GFX_focus_PER_increase_oil_sales` |
| `IR2_sugar_refinery` | The Sugar Refinery | `GFX_goal_generic_oil_refinery` |
| `IR3_abadan_capacity` | Expand Abadan's Capacity | `GFX_focus_PER_donate_oil_fields` |
| `IR3_oil_debate` | The Oil Debate | `GFX_focus_PER_nationalize_oil_fields` |
| `IR3_oil_refinery` | A National Refinery | `GFX_focus_generic_resource_extraction` |
| `IR3_oil_sovereignty` | Oil Sovereignty | `GFX_focus_PER_increase_oil_sales` |

### parliament (58)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_anjoman_elections` | Anjoman Elections | `GFX_goal_generic_national_unity` |
| `IR1_assembly_of_1918` | An Assembly in Wartime | `GFX_focus_generic_support_the_left_right` |
| `IR1_between_empires` | Between the Empires | `GFX_focus_AFG_parliamentary_democracy` |
| `IR1_hague_appeal` | Appeal to the Hague | `GFX_focus_PER_constitutional_monarchy` |
| `IR1_majlis_budget_authority` | The Budget and the Majlis | `GFX_focus_generic_treaty` |
| `IR1_ottoman_frontier` | The Ottoman Frontier | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR1_parliamentary_mandate` | A Parliamentary Mandate | `GFX_focus_POL_complete_april_constitution` |
| `IR1_persia_at_the_conference` | Persia at the Conference | `GFX_goal_generic_national_unity` |
| `IR1_provincial_assemblies` | Work with the Anjomans | `GFX_focus_PER_constitutional_monarchy` |
| `IR1_south_persia_rifles` | The South Persia Rifles | `GFX_goal_generic_political_pressure` |
| `IR1_tabriz_consulates` | Consulates in the North | `GFX_focus_POL_complete_april_constitution` |
| `IR2_accept_the_agreement` | Accept the 1919 Agreement | `GFX_goal_generic_political_pressure` |
| `IR2_afghan_relations` | Relations with Kabul | `GFX_focus_generic_treaty` |
| `IR2_bahrain_question` | The Bahrain Question | `GFX_focus_PER_constitutional_monarchy` |
| `IR2_budget_control` | The Budget under the Majlis | `GFX_focus_POL_complete_april_constitution` |
| `IR2_civil_code` | A Civil Code | `GFX_goal_generic_national_unity` |
| `IR2_civil_service` | A Civil Service | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR2_diplomacy_capstone` | A Foreign Policy of Standing | `GFX_goal_generic_political_pressure` |
| `IR2_elections_1928` | The Elections of 1928 | `GFX_focus_PER_constitutional_monarchy` |
| `IR2_electoral_law` | An Electoral Law | `GFX_focus_AFG_parliamentary_democracy` |
| `IR2_land_registry` | The Land Registry | `GFX_goal_generic_political_pressure` |
| `IR2_league_of_nations` | A Seat at Geneva | `GFX_focus_POL_complete_april_constitution` |
| `IR2_majlis_restored` | The Majlis Restored | `GFX_focus_AFG_parliamentary_democracy` |
| `IR2_ministers_before_the_majlis` | Ministers before the Majlis | `GFX_goal_generic_political_pressure` |
| `IR2_national_union` | A National Union | `GFX_focus_generic_treaty` |
| `IR2_nationalist_front` | The National Front | `GFX_focus_generic_support_the_left_right` |
| `IR2_nationalist_movement` | The Nationalist Movement | `GFX_goal_generic_national_unity` |
| `IR2_northern_treaty` | The Northern Treaty | `GFX_focus_AFG_parliamentary_democracy` |
| `IR2_postwar_settlement` | The Postwar Settlement | `GFX_focus_generic_treaty` |
| `IR2_provincial_governors` | Governors from Tehran | `GFX_focus_PER_constitutional_monarchy` |
| `IR2_regional_ambitions` | Ambitions in the Region | `GFX_focus_AFG_parliamentary_democracy` |
| `IR2_regional_capstone` | The Regional Settlement | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR2_regional_nonaggression` | Regional Nonaggression | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR2_reject_the_agreement` | Reject the 1919 Agreement | `GFX_focus_generic_support_the_left_right` |
| `IR2_reza_khan_minister` | Reza Khan at the War Ministry | `GFX_focus_POL_complete_april_constitution` |
| `IR2_saadabad_prelude` | Toward Saadabad | `GFX_focus_generic_support_the_left_right` |
| `IR2_the_coup_of_1921` | The Coup of February 1921 | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR2_the_final_settlement` | The Final Settlement | `GFX_focus_generic_treaty` |
| `IR2_the_state_in_1935` | The State in 1935 | `GFX_focus_generic_support_the_left_right` |
| `IR2_turkish_frontier` | The Turkish Frontier | `GFX_goal_generic_national_unity` |
| `IR3_allied_cooperation` | Cooperate with the Allies | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR3_arab_neighbours` | The Arab Neighbours | `GFX_focus_generic_support_the_left_right` |
| `IR3_azerbaijan_crisis` | The Azerbaijan Crisis | `GFX_focus_POL_complete_april_constitution` |
| `IR3_between_the_blocs` | Between the Blocs | `GFX_focus_AFG_parliamentary_democracy` |
| `IR3_final_settlement` | The 1945 Settlement | `GFX_focus_PER_constitutional_monarchy` |
| `IR3_inheritance_of_the_state` | The State We Inherit | `GFX_focus_POL_complete_april_constitution` |
| `IR3_name_of_the_nation` | The Name of the Nation | `GFX_focus_PER_constitutional_monarchy` |
| `IR3_nationalist_1945` | The National Front | `GFX_goal_generic_political_pressure` |
| `IR3_postwar_alignment` | Choosing a Side | `GFX_focus_AFG_parliamentary_democracy` |
| `IR3_postwar_settlement` | The Postwar Settlement | `GFX_focus_AFG_revive_the_1923_constitution` |
| `IR3_regional_guarantees` | Regional Guarantees | `GFX_focus_POL_complete_april_constitution` |
| `IR3_restoration_1945` | The Restoration Settled | `GFX_focus_generic_support_the_left_right` |
| `IR3_tehran_declaration` | The Tehran Declaration | `GFX_focus_PER_constitutional_monarchy` |
| `IR3_the_route_we_keep` | The Road We Keep | `GFX_goal_generic_national_unity` |
| `IR3_tripartite_treaty` | The Tripartite Treaty | `GFX_goal_generic_national_unity` |
| `IR3_turkish_border` | The Turkish Border | `GFX_focus_generic_treaty` |
| `IR3_united_nations` | The United Nations | `GFX_goal_generic_political_pressure` |
| `IR3_wartime_majlis` | The Wartime Majlis | `GFX_focus_generic_treaty` |

### railway (3)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_telegraph_network` | The Telegraph Lines | `GFX_focus_generic_railroad` |
| `IR2_telecommunications` | Telegraph and Telephone | `GFX_focus_PER_expand_tabriz_masshad` |
| `IR3_double_track` | Double Track | `GFX_focus_PER_expand_tehran_emam` |

### religion (1)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR2_secular_courts` | Secular Courts | `GFX_focus_PER_forced_secularization` |

### socialism (12)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_jangali_movement` | The Jangali Movement | `GFX_focus_PER_strengthen_the_tudeh` |
| `IR2_gilan_republic` | The Gilan Republic | `GFX_focus_SWE_refuge_for_revolutionaries` |
| `IR2_jangali_congress` | The Jangali Congress | `GFX_focus_generic_land_reclamation` |
| `IR2_labour_law` | A Labour Law | `GFX_focus_generic_communist_industry` |
| `IR2_socialist_capstone` | The Republic of Councils | `GFX_goal_generic_soviet_construction` |
| `IR2_socialist_congress` | A Congress of Workers and Peasants | `GFX_focus_SOV_builder_of_the_red_army` |
| `IR2_socialist_republic` | The Socialist Republic | `GFX_focus_generic_workers_and_farmers_rise` |
| `IR2_workers_councils` | Workers' Councils | `GFX_focus_PER_elevate_the_iran_party` |
| `IR3_socialist_1945` | The Workers' Republic | `GFX_focus_PER_strengthen_the_tudeh` |
| `IR3_tudeh_organisation` | The Tudeh Party | `GFX_focus_ETH_freedom_at_gunpoint` |
| `IR3_tudeh_question` | The Tudeh Question | `GFX_focus_SWE_refuge_for_revolutionaries` |
| `IR3_workers_war_effort` | The Workers' War Effort | `GFX_focus_generic_workers` |

### sovereignty (7)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_guarded_neutrality` | Guarded Neutrality | `GFX_focus_PER_limit_foreign_influence` |
| `IR1_neutrality_declaration` | Declare Neutrality | `GFX_focus_PER_subserviant_to_noone` |
| `IR2_economic_independence` | Economic Independence | `GFX_focus_PER_stand_with_giants` |
| `IR2_nationalist_capstone` | The Sovereign Nation | `GFX_focus_PER_wether_the_storm` |
| `IR2_treaties_of_sovereignty` | Treaties of Sovereignty | `GFX_focus_generic_resource_extraction` |
| `IR3_armed_neutrality` | Armed Neutrality | `GFX_focus_PER_limit_foreign_influence` |
| `IR3_sovereignty_under_pressure` | Sovereignty under Pressure | `GFX_focus_PER_subserviant_to_noone` |

### soviet (3)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_russian_understanding` | An Understanding with Russia | `GFX_focus_chi_mission_to_the_soviet_union` |
| `IR2_soviet_accord` | Supplies from Moscow | `GFX_focus_PER_tehran_moscow_pact` |
| `IR3_soviet_trade_pact` | The Northern Trade | `GFX_focus_research2` |

### succession (3)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR2_dynastic_question` | The Dynastic Question | `GFX_focus_rom_abdicate` |
| `IR2_restoration_capstone` | A Dynasty Restored | `GFX_focus_PER_assassinate_reza_shah` |
| `IR3_succession_crisis` | The Succession Question | `GFX_focus_PER_his_fathers_footsteps` |

### trade (2)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_merchant_credit` | Credit for Merchants | `GFX_goal_generic_positive_trade_relations` |
| `IR2_customs_reform` | The Customs Tariff | `GFX_focus_usa_reestablish_the_gold_standard` |

### tribes (4)

| Focus | Title | Icon |
| --- | --- | --- |
| `IR1_bakhtiari_bargain` | The Bakhtiari Bargain | `GFX_focus_generic_full_social_mobilization` |
| `IR1_tribal_frontier_pact` | A Frontier Pact | `GFX_focus_PER_clamp_kurdish_dissidence` |
| `IR1_tribal_levies` | Tribal Levies | `GFX_focus_PER_recruit_bakhtiari` |
| `IR2_tribal_disarmament` | Disarming the Tribes | `GFX_focus_PER_clamp_azerbaijani_dissidence` |
