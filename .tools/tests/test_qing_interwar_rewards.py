"""Reward-identity regression test for the Qing 1919-1935 (qing_interwar) chapter.

Task t_5f11d3f0 replaced every repeated `completion_reward` in the chapter with a
reward belonging to each focus's own subject. This suite guards the result:

  * every one of the 99 focuses keeps its pre-edit non-reward fields, coordinates
    included, so a reward pass cannot quietly move or retune anything else;
  * the 63 focuses the task did not accept keep their pre-edit reward (pinned by the
    digest they already had), and each of the 36 accepted focuses pays exactly the
    accepted reward written out below;
  * no two focuses in the chapter pay the same reward, compared two ways: the reward
    text itself, and a semantic signature that drops presentation, sorts the effects and
    expands the chapter's scripted effects to their bodies. Identical gameplay written in
    a different order or behind a different tooltip key therefore still fails;
  * every accepted reward states itself through a `custom_effect_tooltip` whose
    localisation key exists, is non-empty, reads as player text, names every balance of
    power move it pays and does not claim the government spends political capital when
    the reward grants it;
  * every tuning value in an accepted reward is a `constant:qing_story.*` reference.
    The only literals allowed are the count fields the installed documentation keeps
    integral (army, air and navy experience, research slots, manpower), and each must
    mirror its named constant; `add_equipment_to_stockpile`'s amount, which the docs say
    may be a variable and which this repository already writes as a constant, is checked
    chapter-wide for a bare number.

The negative controls at the end prove the checks can fail: a reintroduced duplicate, the
same effects reordered behind a different tooltip key, a dropped tooltip line, a dropped
localisation key, a constant replaced by a literal, a balance-of-power push the tooltip
does not state, a tariff tooltip that reverses its own effect, an unauthorised reward edit
on a changed and on an unchanged focus, an icon swap, a prerequisite edit and a coordinate
move. Every control prints caught or MISSED.

Run it with `python .tools/tests/test_qing_interwar_rewards.py`. There is no pytest in
this repository and importing the module runs nothing.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
TREE = os.path.join(ROOT, 'common', 'national_focus', 'qing_interwar.txt')
CONSTANTS = os.path.join(ROOT, 'common', 'script_constants', 'qing_campaign.txt')
EFFECTS = os.path.join(ROOT, 'common', 'scripted_effects', 'qing_campaign.txt')
LOC = os.path.join(ROOT, 'localisation', 'english', 'qing_interwar_l_english.yml')

FOCUS_COUNT = 99
FOCUS_START = re.compile(r'^\tfocus\s*=\s*\{', re.M)

# The 36 focuses this card accepted, and the reward each now pays. One entry per line,
# exactly as scripted: a line added, removed or retuned fails.
ACCEPTED_REWARDS = {
    'QW2_settlement_government': [
        'add_political_power = constant:qing_story.political_capital',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'custom_effect_tooltip = qing_interwar_reward_settlement_government',
    ],
    'QW2_constitutional_trunk': [
        'qing_bop_push_assembly_small = yes',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'custom_effect_tooltip = qing_interwar_reward_constitutional_trunk',
    ],
    'QW2_federal_trunk': [
        'qing_bop_push_assembly_small = yes',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_gain }',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'custom_effect_tooltip = qing_interwar_reward_federal_trunk',
    ],
    'QW2_industrial_takeoff': [
        'add_to_variable = { qing_reform = constant:qing_story.reform_major_gain }',
        'add_stability = constant:qing_story.stability_cost',
        'custom_effect_tooltip = qing_interwar_reward_industrial_takeoff',
    ],
    'QW2_cotton_mills': [
        'add_equipment_to_stockpile = { type = infantry_equipment amount = constant:qing_story.equipment_small }',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'custom_effect_tooltip = qing_interwar_reward_cotton_mills',
    ],
    'QW2_provincial_administration': [
        'qing_bop_push_assembly = yes',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_major_gain }',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'custom_effect_tooltip = qing_interwar_reward_provincial_administration',
    ],
    'QW2_civil_service': [
        'qing_bop_push_court_small = yes',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'custom_effect_tooltip = qing_interwar_reward_civil_service',
    ],
    'QW2_local_government': [
        'qing_bop_push_assembly_small = yes',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_gain }',
        'custom_effect_tooltip = qing_interwar_reward_local_government',
    ],
    'QW2_road_programme': [
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'add_war_support = constant:qing_story.war_support_gain',
        'custom_effect_tooltip = qing_interwar_reward_road_programme',
    ],
    'QW2_tariff_policy': [
        'add_political_power = constant:qing_story.political_capital',
        'add_stability = constant:qing_story.stability_cost',
        'custom_effect_tooltip = qing_interwar_reward_tariff_policy',
    ],
    'QW2_versailles_revision': [
        'add_political_power = constant:qing_story.political_capital',
        'add_stability = constant:qing_story.stability_gain',
        'custom_effect_tooltip = qing_interwar_reward_versailles_revision',
    ],
    'QW2_authoritarian_prefects': [
        'set_country_flag = qing_direct_rule',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_loss }',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'custom_effect_tooltip = qing_interwar_reward_authoritarian_prefects',
    ],
    'QW2_education_drive': [
        'add_research_slot = 1',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_gain }',
        'custom_effect_tooltip = qing_interwar_reward_education_drive',
    ],
    'QW2_public_health': [
        'add_stability = constant:qing_story.stability_major_gain',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_gain }',
        'custom_effect_tooltip = qing_interwar_reward_public_health',
    ],
    'QW2_army_establishment': [
        'add_to_variable = { qing_army_loyalty = constant:qing_story.army_gain }',
        'army_experience = 25',
        'custom_effect_tooltip = qing_interwar_reward_army_establishment',
    ],
    'QW2_army_air_force': [
        'air_experience = 20',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'add_to_variable = { qing_army_loyalty = constant:qing_story.army_gain }',
        'custom_effect_tooltip = qing_interwar_reward_army_air_force',
    ],
    'QW2_army_armour': [
        'army_experience = 25',
        'add_to_variable = { qing_army_loyalty = constant:qing_story.army_gain }',
        'add_war_support = constant:qing_story.war_support_gain',
        'custom_effect_tooltip = qing_interwar_reward_army_armour',
    ],
    'QW2_japanese_pressure_ii': [
        'add_war_support = constant:qing_story.war_support_gain',
        'add_to_variable = { qing_army_loyalty = constant:qing_story.army_gain }',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'custom_effect_tooltip = qing_interwar_reward_japanese_pressure_ii',
    ],
    'QW2_restoration_army': [
        'add_to_variable = { qing_army_loyalty = constant:qing_story.army_major_gain }',
        'army_experience = 25',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'custom_effect_tooltip = qing_interwar_reward_restoration_army',
    ],
    'QW2_cultural_mission': [
        'add_research_slot = 1',
        'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
        'add_stability = constant:qing_story.stability_cost',
        'custom_effect_tooltip = qing_interwar_reward_cultural_mission',
    ],
    'QW2_tibet': [
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'add_stability = constant:qing_story.stability_gain',
        'add_to_variable = { qing_provincial_trust = constant:qing_story.trust_gain }',
        'custom_effect_tooltip = qing_interwar_reward_tibet',
    ],
    'QW2_restoration_court': [
        'add_political_power = constant:qing_story.political_capital',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_major_gain }',
        'qing_bop_push_court_small = yes',
        'custom_effect_tooltip = qing_interwar_reward_restoration_court',
    ],
    'QW2_restoration_guard': [
        'add_to_variable = { qing_army_loyalty = constant:qing_story.army_major_gain }',
        'army_experience = 25',
        'add_equipment_to_stockpile = { type = infantry_equipment amount = constant:qing_story.equipment_small }',
        'custom_effect_tooltip = qing_interwar_reward_restoration_guard',
    ],
    'QW2_restoration_treasury': [
        'add_political_power = constant:qing_story.political_capital',
        'add_equipment_to_stockpile = { type = infantry_equipment amount = constant:qing_story.equipment_grant }',
        'add_stability = constant:qing_story.stability_gain',
        'custom_effect_tooltip = qing_interwar_reward_restoration_treasury',
    ],
    'QW2_restoration_legation': [
        'add_political_power = constant:qing_story.political_capital',
        'add_to_variable = { qing_legitimacy = constant:qing_story.legitimacy_gain }',
        'add_war_support = constant:qing_story.war_support_gain',
        'add_equipment_to_stockpile = { type = infantry_equipment amount = constant:qing_story.equipment_grant }',
        'set_country_flag = qing_restoration_recognised',
        'custom_effect_tooltip = qing_interwar_reward_restoration_legation',
    ],
}

# sha256 of every focus body with only its completion_reward block emptied. Coordinates,
# icon, cost, prerequisites, mutual exclusions, availability, AI weights and filters are
# pinned, for all 99 focuses.
NON_REWARD_DIGESTS = {
    'QW2_army_academies':
        '42124f6af4e0908167c89340b4b98d8752d673db17e2c4c9f29c76fb8b5c3004',
    'QW2_army_air_academy':
        'e3a84b6a395e6820c585e749b932525963e769f77ab85f7fa848485bf67533c8',
    'QW2_army_air_force':
        'e413fc0bcb30c614a0f3ad88f7e02c16c1c917c609425d279224dcb8b93eb1c6',
    'QW2_army_armour':
        'd19c1929aead0e7ccd171ef3c732d5ac14294c812bd781c42acacbacc671c995',
    'QW2_army_arsenals':
        '6ba2a741e9551bf96895d5bb349949bae4547a81d1ad38eb688876134822970c',
    'QW2_army_capstone':
        'a96f9078defb9a12430176674e719d4bc99e109835f3d4607f440da90867e694',
    'QW2_army_doctrine':
        '01dfc60078dfba38ecca634b26634f3bd9ddf4aa130959d5231a426c1bf49761',
    'QW2_army_establishment':
        '8ce7fecec6f89f2b6d28d3677e24ea09da3db20e99f24629ee78218b4ba14a6d',
    'QW2_army_fortifications':
        'e939abb41421daf6e92cec67fa6b34f77991eebccf9d1d907845992b987078c3',
    'QW2_army_manpower':
        '2ca3849d2b27a2c016c6ab6718df2c44037f94d20bc86ddfdc6905ce577192bc',
    'QW2_army_navy':
        '871981379fdae88a75d8bd03917b3c949674e3c5d1d4b00ffdd88c2dbad325b0',
    'QW2_authoritarian_capstone':
        'b5c3958a03e70b845cdd8c39f6ef2c76aa228bae2844c691d2c07a322444eaa1',
    'QW2_authoritarian_censorate':
        'b4cea4d20f5aa24b750bc5bf794914a99d22a349fb35e7a96464ce3f1d017968',
    'QW2_authoritarian_court_schools':
        '48abdf52ac073ccd74205685a8f365faabf6405b93b6d5a76a94cada58ee488d',
    'QW2_authoritarian_opposition':
        'cdee0d26439992a3fb7f93a2bd20eb7f6328703f37053366f53aae7ba6c9b2fb',
    'QW2_authoritarian_prefects':
        '676bd68d42a39f491600ee24dfb5c2c700a810075e2e5217576c6924c011b7ba',
    'QW2_authoritarian_provinces':
        'b478ea47d9ce89ef2dc186880e5bd83625d18def3fb632977e3a463ea4e7afbb',
    'QW2_authoritarian_schools':
        'a2fe985ff44f6ac8814c70cc7381e215ad693074ae04e3a7c30d8075ba3d802c',
    'QW2_authoritarian_trunk':
        '74684f4ce2dff1878dbcc4acb3c782b9efd13d73ef6245fe405f542a6e0eb153',
    'QW2_chapter_end':
        'b8a623126b77b0206e7854da756b93b968d637c9c0b5e31e8a7fd1a8b6935df7',
    'QW2_civil_service':
        '05a8febc6196ba579b920a01b8445bdd08997a33b21ad39352f632dfabdfc7a5',
    'QW2_coal_and_steel':
        'c3e6cdf9b6f965b1c6c8fbb9221416bbf163e5cf77e25f1a1df64e9ce53ee708',
    'QW2_concessions_return':
        '938668c48e683ac537101b110b510460cce90b8863bef55f9c2e0b1308661543',
    'QW2_constitutional_cabinet':
        '991df5e2cabb0c6b8c16600206810025f576fe961c440cff1577082ce17474ac',
    'QW2_constitutional_capstone':
        'b98e175b552a28de62bbf90a1085e834198d0059a335bb7bbfe4aab0c8d45093',
    'QW2_constitutional_crisis':
        '4d4a5fda287155b219750b2bef82808952d1f0874c4b0e56539c25c9db9ad808',
    'QW2_constitutional_elections':
        '048cc6f8d5a133f75ffd7cf4a1c40ac1901daa18bbfd0f4d15289791f0de38b3',
    'QW2_constitutional_judiciary':
        '3593ccdcbf5c0ce43049e20f30ccff91f125bf74a9a2b804e3801668fd9841eb',
    'QW2_constitutional_parties':
        'bb456ddc187e75be0f9ed452516ad54a71d50a9116f0e5203647c61c1b977554',
    'QW2_constitutional_press':
        'e5439609ec8f226454e5011fac92ef92339ec48925fd965e8aca9ca97d875992',
    'QW2_constitutional_trunk':
        '6f4ef9133bc1100d29096f20df37643a6504043b75c8770c5df365d9fae9e811',
    'QW2_cotton_mills':
        '3de685f3e40ea1c13f9c5c1e5dca5de73404e4156374f913e2357b91bcac3078',
    'QW2_cultural_mission':
        '122e36d447be80e54000a06f39bc9f3a24a923a08dece7e12163e99027073c68',
    'QW2_economy_capstone':
        '6c206e281973e14d735d50af730c97c79ccbd5ee8e65438a9fb656ddfdfa1d45',
    'QW2_education_drive':
        '02da60539c5991fb1a6951bc64db2c37a08a55e1c61936deaba6d537f56abc14',
    'QW2_famine_1930':
        '00962758c8dbcb062aa6f3d133ff3910d30ac3f3916fbf8ca2fd83188ae61f21',
    'QW2_federal_armies':
        'f48ab4ee4c18148355edbeebffe90313bfe33a16beb44c5ed558909e837603a5',
    'QW2_federal_bank':
        '6855ea85c0d97cf75e4d8963e3b3f623a88ea15a3000953b5465bfe7c1d2a0ef',
    'QW2_federal_capstone':
        'bcb25dbf5abba1dd5b62e0f41742f4ab8c538acd37476d25148f179352694f3b',
    'QW2_federal_compromise':
        'd3bc6fcbb0206e9cc6ef0ca7a31f312042d565db0176b6b0f2897e9471d132af',
    'QW2_federal_police':
        'cd9120b92b38e35e402f0374505262207b5e40599c95d928db898cbaad49b3c6',
    'QW2_federal_provinces':
        'acae0c7c8fd63ac49b42224911e3799f884cd2954b910970150747c0b226d4a3',
    'QW2_federal_taxation':
        'e4f774233593f4470d96a3b2758695ddaa71577f2247be11712f6c747cf7ac9e',
    'QW2_federal_trunk':
        '3f76674f151e501623f3ca014842b79953e7c27ce7c953652a365f598b8a5b39',
    'QW2_flood_relief':
        '816ce060b505370243e918ed05b41d1b404383720f7c34dc8d48b5345a9f993e',
    'QW2_foreign_loans_ii':
        'b7a79a6671654b2f68007e70d0c2765c87c2c3dde0250ebb89aa575279f8eea6',
    'QW2_german_advisers_ii':
        '9cce18805a0d1c47e29a50a84fde29d522d90eb708c1b9995351d7b28ddc716e',
    'QW2_heavy_industry':
        '275e248903218250efe204b25d42fa5c12c5fab7e527e6d546b86a39981f05c6',
    'QW2_industrial_takeoff':
        '3ff50cfefbc3b7ceeed9ff6f18fde3564ebaa04e920fa5100aa58b54a5adf18d',
    'QW2_irrigation':
        '555ea33e9961862d36faa843292be4b677e9a071e70f6060c4fa3f9773b5e8a6',
    'QW2_japanese_pressure_ii':
        '949548bf76447459f96067b4244da46fb79a6cec2ddb7c12a2178d67da64ad23',
    'QW2_kmt_question':
        '2daf65a52995f38df1ddc3550e51265d356b4f66c30cfd9ac62a22b2b6b42b3b',
    'QW2_land_reform':
        '52219149272421fd9563c96e4011360cbeaaefe0bdbe4f42f502f58d4bcf5398',
    'QW2_league_seat':
        '2a9768e677abeb7b516b03560d097cda1dd9d55be6803551256eeb69a79da02a',
    'QW2_local_government':
        'e48e4d5da4b90bbc3a7cd1b3654c9f3e4807ac920fcb3cc3e671afe116de01a2',
    'QW2_manchurian_crisis_prep':
        '1df5c3d1ed8b8f2a53bbe472c3a7f2aa70f38d0f1fb1575a9f1e9de2a9bae3eb',
    'QW2_manchurian_defence':
        '774bb5d579ace445b281929e48f44d2dc4c77cd1366fa8a510b370bf2fd26981',
    'QW2_manchurian_industry':
        '6e5d4c68ee5debb2a194a10f3d3dfd5f601dc3c2a2a12740ef1f1803159cfd8a',
    'QW2_northern_expedition':
        'cb1724417d0d0f6622307934fe59ed78f362098ff6c231213e2647a909b32b2a',
    'QW2_press_law':
        'a7cb682d550a4b6fc9f00241b0ba82759c6c417802d83760c1e47d687d77eb4e',
    'QW2_provincial_administration':
        'c18cfbe5de19d2fb2130982f7915cae5a72e76d1d43a412e59af1bce5dd0447b',
    'QW2_provincial_army_law':
        'd5e34bdfc567c28be6272f18d09963fcd4319d8e513a29ed226a2ac5c4bea310',
    'QW2_public_health':
        '95e13c7efaa1488efdd5c8a0ab5db0bf33d195634610d42cda5828ea57441742',
    'QW2_railway_expansion':
        '51fd233b5de4a186242fd0985b1786d43a2baf7937fb88d15920bd06d3cdb4a6',
    'QW2_restoration_army':
        '313e67874af0345a5d76f5d792b8311a0fa05970075740e021c2df287282a658',
    'QW2_restoration_code':
        '7b487d98f21bf44b7d4bc8cb6e6e216ef4962bdf57a4a3bb50feab3c3d887218',
    'QW2_restoration_constitution':
        '4bb76da012239dea53e6d5c2bfb634e2a534d36b236c400e5cb534328b2d8051',
    'QW2_restoration_court':
        '7d0b93ee7f466e09ef96a5f44af558dea2b35b29c27fc2d9c3f510bb3c31ea60',
    'QW2_restoration_gentry':
        '4de608adac35c8ba6fbfb097c3c8ca9beb6b1f36ea1072c70731c09d37c91de1',
    'QW2_restoration_guard':
        '54be84c9f8314c45198d1a32c414e6b53bec42e973a0afe9a80ca7d69c001164',
    'QW2_restoration_legation':
        '08e66cb97501894dbea573d1a882037cda7e35f1576df7a23ff882f2e412ca77',
    'QW2_restoration_nobility':
        'a81b0c5b6956b2db5af4c88c15dcf8d083429bb3bbef6dae2183cc8dae99f466',
    'QW2_restoration_proclaimed':
        '78bd057b618cabf26c52acf0e65c954a930423af9179e475001ef6ee81e58512',
    'QW2_restoration_programme':
        '707ddd463b9cc8330b2ff8e87117ab232fd44c69cdc316637f7aadebf13976c8',
    'QW2_restoration_provinces':
        '8af8585f23fbcb3251c99e87fe8db40bde160468f6a92f0d6155945055fab91d',
    'QW2_restoration_reform':
        '922a31e78c0aaf1b4e37c819c096df152b92fee2b494bc53f1105bd71cef7e2b',
    'QW2_restoration_succession':
        '9e4b989e51119ac7bb5e5037f9929affa47a743b13da876014f6a6f52a6694fa',
    'QW2_restoration_treasury':
        '87cd8146f54927e4eef54d5fd28f99caf4de432d48c82205b1b13f5ac3696d57',
    'QW2_road_programme':
        'e06b69dd982b0d0a706f7445fa30f8087525f998188b57d418f34da4c914ef91',
    'QW2_settlement_government':
        '4fa257184da2aa5e498813ead6dd0d6dd8064494c55f02f11ee3ade56e7bbafc',
    'QW2_shanghai_port':
        'c08aa7bbb62a246557207caa71f599751aedca61ecde865ef0ef81cd5581781a',
    'QW2_southern_integration':
        '6bda1ca5e451a6de27d04ae3a3ba85db1e2bb5753b0df4ab89b850af4bbc1abe',
    'QW2_soviet_relations':
        '23ec9719c2b9b62a8fb8fff7e80efea8b188c59eeacb472ec14fb2bf4f9e1d72',
    'QW2_state_bank':
        '8bbbfd8aa39775ebfe460a5047fac2c62b89f1e2f47b53c7dfc2dab6f8785201',
    'QW2_tariff_policy':
        'd51d10d9d595088d337f9ee3d252e28f10e80b2e2b0ba11984820e5abd89bdec',
    'QW2_telegraph_ii':
        '6680075ef2a2ab5d2471079ea6dc9411fedd7c70b227bf462cd9f58489bf5941',
    'QW2_tibet':
        'a6b3245af819964c901024432e9fa2c8d56a76332e24ec71d292b374da892adc',
    'QW2_versailles_revision':
        '02b46545ac19fcdd6da3b931cd806de84083ea30ae2fa70f8733e426ba0ff65c',
    'QW2_warlord_amnesty':
        '7f0b52f777db196905bc38add4db6c2b3d54ba29346555601380284dde5c4ee3',
    'QW2_washington_system':
        '323c13bc37ebc4689966945a4de30bd0161dc4f62f5b67aaf23a16ccef2cc7b3',
    'QW2_xinjiang':
        'e144a1675c61114661fdd7900f65bb8512293229393f1c91dd6ab93a8c8e2562',
    'QW2_yuan_army_state':
        '860ed0bd1200f2c735249f3e7edfd5071cbe17f8e37ee57d59fe7d3f4d395de7',
    'QW2_yuan_capstone':
        '81e8bee8475aaace08e26771f00f0a9eb20a98395c57c616f6f4de6f57f3a280',
    'QW2_yuan_education':
        '1d2528c030534a16e3fa430c17864bbd932e6294c69f7080ab694c5467c106c0',
    'QW2_yuan_finance':
        '7c80c73f7ff4af8b9d60c6c2119ab619fcc3fa6034f72313bc19de6e14692d23',
    'QW2_yuan_officers':
        'dce76334e525805a70e5bb55df8b18cfc39fa7ce42a70eb9c334be59fdf4e4c9',
    'QW2_yuan_succession_crisis':
        '71c33207260466f05f38eeeb4f694de66022fff387e0da430171a0b6f30973a2',
    'QW2_yuan_trunk':
        '7a028419b984bd392ef85039b2fd59f16a6c0be304492602384512d039f080b9',
    'QW2_yunnan':
        'a726716e21603ef7615d8b7d3d562c418fb906621e0affc5f5c20f8e78e61e54',
}

# sha256 of the normalised completion_reward text of every focus before this task, so an
# edit to a focus the task did not accept is reported by name.
BASELINE_REWARD_DIGESTS = {
    'QW2_constitutional_elections':
        'dfb32f546f7c2754e9517b5063f5d01f5ba4acb27a53cb898c1535b057dbc629',
    'QW2_constitutional_parties':
        '2f5816a8dd884cd1c0cf7c0ce6ea8ee48d5aa9be6f4bcaef8d1839c52618a2e1',
    'QW2_constitutional_cabinet':
        '35b49e12d529d7c3bb86e881c8d892eb6f24a43e4c8ac348501ca25d7ca20194',
    'QW2_constitutional_crisis':
        '88ec5044d937347372f414694f79bf09fc48eb318b7e13f7b9849d55388f25ef',
    'QW2_constitutional_capstone':
        'ac98abd9d7b1e3f2e5096e76ae75717167dbacf9162bc53e9dd900cae05d8a0e',
    'QW2_authoritarian_trunk':
        '78a4fc9b8264cdcbd06ce78841fdbb6d9ceac1d09a8e2a2514ee6971ebdfa60d',
    'QW2_authoritarian_provinces':
        'a95144e2fb2a6804339e65b086f0b0491e4314abfe6071a395aa0974971806e0',
    'QW2_authoritarian_censorate':
        '881d470452828bba917e601cad14aad58a66e91f50e16c4cc7d83876a6b6e6d1',
    'QW2_authoritarian_schools':
        '0e60950aedf0582c8fb0b88d8427e974bb3f84fd412df94f7e93784898be1f1e',
    'QW2_authoritarian_opposition':
        '387029577d10b346ce05065929ad04309b65f0a4adad64a328bb417508c91646',
    'QW2_authoritarian_capstone':
        '6ad448ab8303f592ce279fcbf374ecc407bded910c42cb97e8c9b87ced5b51a4',
    'QW2_yuan_trunk':
        '43b6ed3ff479713e9aaa42116ca7c77725932066414644bd2e4087fab135ac5d',
    'QW2_yuan_army_state':
        '2b9fa7a1de999c080f5e5c048300bd08281110d1305b9e3330c2923c2cd8b54d',
    'QW2_yuan_finance':
        'e24babd3d4cce5b693bfee51102591beba78d0ca4c5f29abfac3ba16d3760fec',
    'QW2_yuan_succession_crisis':
        '2cc89fbda47bc596d7867442a0c9a9e32d2e46ac15d711565bdf7bdc6d8b9dee',
    'QW2_yuan_capstone':
        'b836d0f02f03693704518340037c387534714726c939f6ff42b6267548a11b9d',
    'QW2_federal_provinces':
        'd9c37d4bbd73100d2a4f41a85038aff2d71ca7a5191dbb7477e6028bff3806f1',
    'QW2_federal_taxation':
        '5b92b348c644d3adee4a4e51dfa57e1386d709e388b54c1222c6d5ce93b75e91',
    'QW2_federal_armies':
        'a6b10266ef326d6a3d627d4fb7b427021fa4c270c2c44a92e44e76aed075400c',
    'QW2_federal_compromise':
        '4a4df838858d7a0d8e150ea4cbaed2774c49894a7705514ee28e95fb3d381d45',
    'QW2_federal_capstone':
        'e927f045f1543907fedfebe01b6413b96c118a3202f526499847201a74446ae9',
    'QW2_coal_and_steel':
        '4b9afefd90ccc68da6a24f5f4d6cda44c545be116d66dc6b60af0788699fcc44',
    'QW2_railway_expansion':
        '0878485bf14b267c586285d959fc6e4de9c03cbee632b1007188fcc0f6e3e841',
    'QW2_shanghai_port':
        'b3df2448641a7f49380d820de1faae1d15d512990abba6b6b7bcefca71e81d00',
    'QW2_land_reform':
        '6c3d4b492b6a1f3bfceb97ed21e299cb3492bde676aa9089dab5caf51913ebad',
    'QW2_state_bank':
        'e3ab4aeb2fab2d5dad7ec3b2933c209c1fb77638e897e1182733f1c8eb9d70b2',
    'QW2_heavy_industry':
        'a50c214032069e331aecd421fb4f6e14341779fe54b2ef9ce51476dc740c185e',
    'QW2_economy_capstone':
        '026851f85cd2099bc0466c84a856f7bc6469dfe0cd3e841970e21e526565951c',
    'QW2_army_navy':
        'ca2f4e1daa4f989f9f33f00661537ae23ff65030d1d34981169e26439508f2c1',
    'QW2_army_doctrine':
        'fef5e19b9c401c5d0add8b2e55dc82e4670af6d0b61b0e3fa07dfce12a2aedef',
    'QW2_army_academies':
        '3a94964646d27dfa2e9784eb952f0896145fda579aa3f3fd79698d08ca3c0738',
    'QW2_army_arsenals':
        '96dfe96f4616d2d79f2ea06a2a4c006ca50d410b504d8ba70eaf03926bd58272',
    'QW2_army_fortifications':
        '29505d2052bd2416a70c242a2e73bca6035f4aecdf91a6cb2dc015ac55ae1363',
    'QW2_army_capstone':
        '6bad723245a409ea2787614fa66fb50d8a0cdb74febaf1e839426423400c9968',
    'QW2_washington_system':
        'aed4f692f1e00734cfeb5e1b3c359731714f20c3cb9e259d335f50ae3a1ffa1e',
    'QW2_soviet_relations':
        'ea57fa545d2c34d5fca40a181f4a582cadc54c3175483e22426f1e97880fea8b',
    'QW2_german_advisers_ii':
        'fdd8510d64d59966c980b1430379f1888060aace6188a7c98bba65f2180774f0',
    'QW2_concessions_return':
        '4a5be8a9dc5483448e7527aefa87671adde6ff2ad0c1235eab45bbb7c63297c3',
    'QW2_league_seat':
        'b188867c67da00ae7711604b514077b28e5b932b6e21208a9abe16c23735f6a9',
    'QW2_warlord_amnesty':
        'd845a9d5749a38a3f552212549ba4454c2ae261c00aa1d742aad3d701200d1f9',
    'QW2_provincial_army_law':
        '69bbedcf557226f3e4cd87402838e8421d1d6b3d47c0ffef4d8e4e24f2a0c9b5',
    'QW2_southern_integration':
        'f67ab52c1a21f2218ee22e3bc6031159a6753c6fdaf07a597b4d984f761ebbf2',
    'QW2_manchurian_defence':
        '95a8ec122d0bd3d23bc2d6066465207971d328ae770a48c1d912a6f1d0671f4a',
    'QW2_manchurian_industry':
        '54489b04741ec440ce37ecbcb39d735415303bff3aea2659db628edee4044086',
    'QW2_manchurian_crisis_prep':
        '2a791e49bb230dc3f0a51e3c43e7a7c5fc5db968dfdb25e8ad578211e5fdc390',
    'QW2_kmt_question':
        '8383bd78a18f49e54a40fa6e233d5e7d674d557b0a5be267c55d8c248ad517ef',
    'QW2_northern_expedition':
        'bb4bab7405ccdb8a13a78a179579eb195ba8afa3ccc9cf84e90ff1a3a1c2ea68',
    'QW2_press_law':
        '0f34fed729d1f537bcfd59eae31cb8c3ef413b37c72e6d2c80272037e4aea613',
    'QW2_irrigation':
        'e7bb2fb8bffce7bff95428342a881698dad08b76e47a2cbb97a0125b21c9e054',
    'QW2_telegraph_ii':
        'ca542f62f9daa169f71aa06fdc27fe9188d01cd1b29f09b3b910fc670112cc97',
    'QW2_army_manpower':
        'b38cb80393346248639e39eecc06d8b94d5f89243101b71c3655847280b23164',
    'QW2_army_air_academy':
        'f284a9d94abbca6dd54e3c74fecebcebb38f669a271921f4a6cd6dbf0eb7cbee',
    'QW2_foreign_loans_ii':
        'e210c36664480eef9136a371b1e1b03ca4c8ff18aa1cef4938a77ea0779f5a57',
    'QW2_yunnan':
        'e2315fcdff65f1f42474af6b8349d6be7a7fab77999909dcaa1fd73d22c69b6d',
    'QW2_xinjiang':
        '714cd319542fafba0d8e5d9c190662eeb572dc6c24030061ac0dd6dfa6f73d54',
    'QW2_famine_1930':
        'eb587e1825876d425cb5838584cfec161991545f696acb59b45fc50db7095e93',
    'QW2_flood_relief':
        'e14cbe6e77394daa09e6f552f23adb76fe0a809016d8096069efae1d542da788',
    'QW2_constitutional_press':
        '28ccec196e17bf88ac01cd9bcd9063fa453c3057458928f5f5620dd19151877a',
    'QW2_constitutional_judiciary':
        '3d7fb31852bfb147b09da355b933ce924ddf958962808f90e0e0718c33adc7c1',
    'QW2_authoritarian_court_schools':
        '095589b01a308a6c7fcfaa0f4de2f6a7defa3697eb69f8d78e3e1d887f6e6fe3',
    'QW2_yuan_officers':
        'f2f50f95f2320334d03c76a771a32077487480b955b5f33ad647916a23748aaf',
    'QW2_yuan_education':
        '46d21e38c2c97d9b2532430aba066e5d18175653100b049bff5a06e2d2a1df4f',
    'QW2_federal_bank':
        'cf5da7957206fe94ce351bb2433dd36d69a5bfebc4de8301a85331139d075ea2',
    'QW2_federal_police':
        '0ac978527b055e88e30d57a8ab2803126eb9a3af7ae7b2348d045813beecbb9b',
    'QW2_chapter_end':
        'b6cb57c482e4ea4d7e75762d6b0ece0c8b80d49dc9d81242e6c6d148b0dab86f',
    'QW2_restoration_programme':
        '2136128fe6c3ef4eaaf636278cf70bba177255980e8ee8a8aee2ccc9176286d1',
    'QW2_restoration_reform':
        '26ef938c7acdab48580e65efc93da2bd589ad2293bc4f71666c5aa316414d8f5',
    'QW2_restoration_provinces':
        'c860e12213577361c6acd2b7c0f1d5725fd6923877d853d02bc8fc0fb18689d4',
    'QW2_restoration_nobility':
        '6cc4bc104a44a41ba89d76d2d0efc5413faad0690554e396ba5c8edd6c7e5706',
    'QW2_restoration_code':
        '7b046220280215116f77ededc5e99758bee4727a6e7ba4c251902952a77c9324',
    'QW2_restoration_gentry':
        '6cfbc7036e591b4ef02afc7c5ef2e0746b6a9072d3c25e48cf0049cd04901e6f',
    'QW2_restoration_constitution':
        '4f88924e86f743a633c15a5adb94acd1666c2c52c58bf657ad8a4fa9600eb750',
    'QW2_restoration_succession':
        'cec9a232ea86cede7e1d0f58429c0655113f583526621c6317c2a8babd1ec63e',
    'QW2_restoration_proclaimed':
        '01354ebab6100572e798bc3f0a1e593aa563e3a04a0d677dd167ecc3167b20fa',
}

# Effects the engine renders a tooltip for on its own, plus scripted effects of this
# chapter whose body shifts the balance of power.
VISIBLE_EFFECTS = (
    'add_stability', 'add_war_support', 'add_political_power', 'add_manpower',
    'add_research_slot', 'add_opinion_modifier', 'add_equipment_to_stockpile',
    'army_experience', 'air_experience', 'navy_experience', 'country_event',
    'add_idea', 'set_power_balance', 'add_power_balance_value', 'custom_effect_tooltip',
    'qing_bop_push_assembly', 'qing_bop_push_assembly_small', 'qing_bop_push_court',
    'qing_bop_push_court_small', 'qing_bop_pull_to_centre',
)

# Count fields the installed effects documentation keeps integral. The project writes the
# literal and mirrors the value in common/script_constants/qing_campaign.txt; a literal
# that stops mirroring its constant fails. Every other value must be a `constant:`.
ALLOWED_LITERAL_FIELDS = {
    'army_experience': 'army_experience',
    'air_experience': 'air_experience',
    'navy_experience': 'navy_experience',
    'add_research_slot': 'project_slots',
    'add_manpower': 'manpower_gain',
}

# Scripted effects expanded before two rewards are compared, so identical gameplay
# written through a helper is still recognised as identical.
EXPANDED_EFFECTS = (
    'qing_bop_push_court', 'qing_bop_push_court_small', 'qing_bop_push_assembly',
    'qing_bop_push_assembly_small', 'qing_bop_pull_to_centre',
)

RAW_IDENTIFIER = re.compile(r'\b[a-z][a-z0-9]*_[a-z0-9_]+\b')


def strip_comments(text):
    out = []
    for line in text.split('\n'):
        quote = False
        cut = len(line)
        for index, char in enumerate(line):
            if char == '"':
                quote = not quote
            elif char == '#' and not quote:
                cut = index
                break
        out.append(line[:cut] + ' ' * (len(line) - cut))
    return '\n'.join(out)


def span(text, start):
    index = text.index('{', start)
    depth = 0
    while index < len(text):
        char = text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise ValueError('unbalanced block')


def parse_text(text):
    text = strip_comments(text.replace('\r\n', '\n'))
    focuses = {}
    order = []
    for match in FOCUS_START.finditer(text):
        body = text[match.start():span(text, match.start())]
        focus_id = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', body).group(1)
        focuses[focus_id] = body
        order.append(focus_id)
    return focuses, order


def reward_lines(body):
    start = body.index('completion_reward')
    end = span(body, start)
    inner = body[body.index('{', start) + 1:end - 1]
    return [line.strip() for line in inner.split('\n') if line.strip()]


def reward_key(reward):
    return ' '.join(' '.join(reward).split())


def read(path):
    with open(path, encoding='utf-8-sig') as handle:
        return handle.read()


def declared_constants(text):
    declared = {}
    block = None
    for line in text.split('\n'):
        stripped = line.strip()
        match = re.match(r'^([a-z0-9_]+)\s*=\s*\{$', stripped)
        if match and block is None:
            block = match.group(1)
            continue
        if block is not None and stripped == '}':
            block = None
            continue
        if block is not None:
            key = re.match(r'^([a-z0-9_]+)\s*=', stripped)
            if key:
                declared.setdefault(block, set()).add(key.group(1))
    return declared


def constant_values(text):
    values = {}
    for match in re.finditer(r'(?m)^\t([a-z_]+)\s*=\s*(-?[0-9.]+)\s*$', text):
        values.setdefault(match.group(1), match.group(2))
    return values


def non_reward_digest(body):
    start = body.index('completion_reward')
    stripped = body[:start] + 'completion_reward = { }' + body[span(body, start):]
    normalised = '\n'.join(line.rstrip() for line in stripped.split('\n'))
    return hashlib.sha256(normalised.encode('utf-8')).hexdigest()


def check_accepted_rewards(focuses):
    failures = []
    for focus_id, expected in sorted(ACCEPTED_REWARDS.items()):
        body = focuses.get(focus_id)
        if body is None:
            failures.append('%s is missing from the chapter' % focus_id)
            continue
        actual = reward_lines(body)
        if actual != expected:
            failures.append('%s pays %r, not the accepted reward %r'
                            % (focus_id, actual, expected))
    return failures


def check_unchanged_rewards(focuses):
    failures = []
    for focus_id, digest in sorted(BASELINE_REWARD_DIGESTS.items()):
        if focus_id in ACCEPTED_REWARDS:
            continue
        body = focuses.get(focus_id)
        if body is None:
            failures.append('%s is missing from the chapter' % focus_id)
            continue
        actual = hashlib.sha256(reward_key(reward_lines(body)).encode('utf-8')).hexdigest()
        if actual != digest:
            failures.append('%s changed a reward the task did not accept' % focus_id)
    return failures


def reward_groups(focuses):
    groups = {}
    for focus_id, body in focuses.items():
        groups.setdefault(reward_key(reward_lines(body)), []).append(focus_id)
    return groups


def effect_bodies(text):
    """Bodies of the chapter's scripted effects, keyed by name, comments stripped."""
    cleaned = strip_comments(text.replace('\r\n', '\n'))
    bodies = {}
    for match in re.finditer(r'(?m)^([a-z_][a-z0-9_]*)\s*=\s*\{', cleaned):
        name = match.group(1)
        body = cleaned[match.start():span(cleaned, match.start())]
        inner = body[body.index('{') + 1:-1]
        bodies[name] = [line.strip() for line in inner.split('\n') if line.strip()]
    return bodies


def semantic_signature(reward, bodies=None):
    """The reward with presentation removed, helpers expanded and effects sorted."""
    leaves = []
    for line in reward:
        head = line.split('=')[0].strip()
        if head == 'custom_effect_tooltip':
            continue
        if head in EXPANDED_EFFECTS and bodies and head in bodies:
            leaves.extend(semantic_signature(bodies[head], bodies))
            continue
        leaves.append(' '.join(line.split()))
    return tuple(sorted(leaves))


def check_no_duplicate_reward(focuses, bodies=None):
    failures = []
    for text, ids in sorted(reward_groups(focuses).items()):
        if len(ids) > 1:
            failures.append('reward text shared by %s -> %s' % (sorted(ids), text))
    # Order-insensitive identity, checked across the focuses this card accepted: two
    # rewards that differ only in line order or in the tooltip key are the same reward.
    signatures = {}
    for focus_id in ACCEPTED_REWARDS:
        body = focuses.get(focus_id)
        if body is None:
            failures.append('%s is missing from the chapter' % focus_id)
            continue
        signatures.setdefault(semantic_signature(reward_lines(body), bodies), []).append(focus_id)
    for signature, ids in sorted(signatures.items()):
        if len(ids) > 1:
            failures.append('identical reward gameplay shared by %s -> %s'
                            % (sorted(ids), ' | '.join(signature)))
    return failures


def check_constants(focuses, constants_text):
    failures = []
    declared = declared_constants(constants_text)
    values = constant_values(constants_text)
    for focus_id in sorted(ACCEPTED_REWARDS):
        body = focuses.get(focus_id)
        lines = reward_lines(body) if body is not None else ACCEPTED_REWARDS[focus_id]
        for line in lines:
            for block, name in re.findall(r'constant:([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)', line):
                if name not in declared.get(block, set()):
                    failures.append('%s names an undeclared constant %s.%s'
                                    % (focus_id, block, name))
            for field, literal in re.findall(
                    r'(?<![\w.])([a-z_]+)\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)(?![\w.])', line):
                if field not in ALLOWED_LITERAL_FIELDS:
                    failures.append('%s pays the literal %s = %s where a constant is required'
                                    % (focus_id, field, literal))
                    continue
                mirror = ALLOWED_LITERAL_FIELDS[field]
                if values.get(mirror) != literal:
                    failures.append('%s literal %s = %s does not mirror qing_story.%s'
                                    % (focus_id, field, literal, mirror))
    # add_equipment_to_stockpile's amount may be a variable, so the chapter must not carry
    # a bare number there at all.
    for focus_id, body in focuses.items():
        for line in reward_lines(body):
            if 'add_equipment_to_stockpile' not in line:
                continue
            match = re.search(r'amount\s*=\s*([^\s}]+)', line)
            if not match or not match.group(1).startswith('constant:'):
                failures.append('%s pays an equipment amount that is not a constant: %s'
                                % (focus_id, line))
    return failures


def read_loc(path=None):
    keys = {}
    for line in read(path or LOC).split('\n'):
        match = re.match(r'^\s*([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', line.rstrip('\r'))
        if match:
            keys[match.group(1)] = match.group(2)
    return keys


def check_player_visible(focuses, loc):
    failures = []
    for focus_id, expected in sorted(ACCEPTED_REWARDS.items()):
        visible = [line for line in expected
                   if line.split(' ')[0].split('=')[0].strip() in VISIBLE_EFFECTS]
        if not visible:
            failures.append('%s states no reward the engine renders for the player' % focus_id)
        tooltips = re.findall(r'custom_effect_tooltip\s*=\s*([A-Za-z0-9_]+)', ' '.join(expected))
        if not tooltips:
            failures.append('%s pays a reward with no custom_effect_tooltip' % focus_id)
        reward_text = ' '.join(expected)
        for key in tooltips:
            if key not in loc:
                failures.append('%s tooltip key %s is not localised' % (focus_id, key))
                continue
            text = loc[key]
            if not text.strip():
                failures.append('%s tooltip %s is empty' % (focus_id, key))
            if ';' in text or '\u2014' in text or '$' in text:
                failures.append('%s tooltip %s carries raw punctuation' % (focus_id, key))
            if RAW_IDENTIFIER.search(text):
                failures.append('%s tooltip %s shows a raw identifier' % (focus_id, key))
            if 'qing_bop_' in reward_text and 'Balance of Power' not in text:
                failures.append('%s tooltip %s does not state the balance of power move it pays'
                                % (focus_id, key))
            if 'add_political_power = constant:qing_story.political_capital' in reward_text \
                    and re.search(r'\bspends?\b', text, re.I):
                failures.append('%s tooltip %s says the government spends political capital '
                                'while the reward grants it' % (focus_id, key))
            if 'add_stability = constant:qing_story.stability_cost' in reward_text \
                    and 'cost to public order' not in text:
                failures.append('%s tooltip %s does not state the cost to public order'
                                % (focus_id, key))
    return failures


def check_preservation(focuses):
    failures = []
    if len(focuses) != FOCUS_COUNT:
        failures.append('the chapter has %d focuses, not %d' % (len(focuses), FOCUS_COUNT))
    for focus_id, digest in sorted(NON_REWARD_DIGESTS.items()):
        body = focuses.get(focus_id)
        if body is None:
            failures.append('%s is missing from the chapter' % focus_id)
            continue
        if non_reward_digest(body) != digest:
            failures.append('%s changed a field outside completion_reward' % focus_id)
    return failures


# ---------------------------------------------------------------------------------------------
# Negative controls: every class of edit this task forbids must be reported by name.
# ---------------------------------------------------------------------------------------------

def mutated_tree(old, new):
    assert old in TREE_TEXT, 'mutation anchor missing: %r' % old
    return TREE_TEXT.replace(old, new, 1)


def run_mutants():
    focuses, _order = parse_text(TREE_TEXT)
    loc = read_loc()
    cases = []

    # Reintroducing the identical reward on two focuses is the regression the task exists
    # to prevent: the inspector counts one diagnostic per focus in the group.
    trunk_reward = '\n'.join('\t\t\t%s' % line for line in ACCEPTED_REWARDS[
        'QW2_constitutional_trunk'])
    civil_reward = '\n'.join('\t\t\t%s' % line for line in ACCEPTED_REWARDS['QW2_civil_service'])
    duplicated = parse_text(mutated_tree(civil_reward, trunk_reward))[0]
    cases.append(('duplicate reward reintroduced', check_no_duplicate_reward(duplicated),
                  'reward text shared by'))
    cases.append(('accepted reward replaced by another accepted reward',
                  check_accepted_rewards(duplicated), 'not the accepted reward'))

    cases.append(('reward tooltip line removed',
                  check_accepted_rewards(parse_text(mutated_tree(
                      '\t\t\tcustom_effect_tooltip = qing_interwar_reward_civil_service\n',
                      ''))[0]), 'not the accepted reward'))

    missing_key = dict(loc)
    missing_key.pop('qing_interwar_reward_cotton_mills', None)
    cases.append(('reward tooltip key removed from localisation',
                  check_player_visible(focuses, missing_key), 'is not localised'))

    literal = parse_text(mutated_tree(
        'add_war_support = constant:qing_story.war_support_gain\n'
        '\t\t\tcustom_effect_tooltip = qing_interwar_reward_road_programme',
        'add_war_support = 0.1\n'
        '\t\t\tcustom_effect_tooltip = qing_interwar_reward_road_programme'))[0]
    cases.append(('constant replaced by a literal, reward pin',
                  check_accepted_rewards(literal), 'not the accepted reward'))
    cases.append(('constant replaced by a literal, constants check',
                  check_constants(literal, CONSTANTS_TEXT), 'where a constant is required'))

    cases.append(('unauthorised reward edit on a changed focus',
                  check_accepted_rewards(parse_text(mutated_tree(
                      '\t\t\tadd_to_variable = { qing_reform = constant:qing_story.reform_gain }\n'
                      '\t\t\tcustom_effect_tooltip = qing_interwar_reward_civil_service',
                      '\t\t\tadd_to_variable = { qing_reform = '
                      'constant:qing_story.reform_major_gain }\n'
                      '\t\t\tcustom_effect_tooltip = qing_interwar_reward_civil_service'))[0]),
                  'not the accepted reward'))

    irrigation_reward = ('\t\t\tadd_stability = constant:qing_story.stability_major_gain\n'
                         '\t\t\tadd_to_variable = { qing_legitimacy = '
                         'constant:qing_story.legitimacy_gain }\n\t\t}\n\t}\n\tfocus = {\n'
                         '\t\tid = QW2_road_programme')
    cases.append(('unauthorised reward edit on an unchanged focus',
                  check_unchanged_rewards(parse_text(mutated_tree(
                      irrigation_reward,
                      irrigation_reward.replace('stability_major_gain',
                                                'stability_gain')))[0]),
                  'changed a reward the task did not accept'))

    cases.append(('icon swap on an accepted focus',
                  check_preservation(parse_text(mutated_tree(
                      'icon = GFX_focus_PER_constitutional_monarchy',
                      'icon = GFX_focus_generic_monarchy_1'))[0]),
                  'changed a field outside completion_reward'))
    cases.append(('prerequisite edit on an accepted focus',
                  check_preservation(parse_text(mutated_tree(
                      '\t\tid = QW2_cotton_mills\n\t\ticon = GFX_focus_generic_industry_2\n'
                      '\t\tx = 40\n\t\ty = 1\n\t\tcost = 7\n'
                      '\t\tprerequisite = { focus = QW2_industrial_takeoff }',
                      '\t\tid = QW2_cotton_mills\n\t\ticon = GFX_focus_generic_industry_2\n'
                      '\t\tx = 40\n\t\ty = 1\n\t\tcost = 7\n'
                      '\t\tprerequisite = { focus = QW2_coal_and_steel }'))[0]),
                  'changed a field outside completion_reward'))
    cases.append(('coordinate move on an accepted focus',
                  check_preservation(parse_text(mutated_tree(
                      '\t\tid = QW2_cotton_mills\n\t\ticon = GFX_focus_generic_industry_2\n'
                      '\t\tx = 40',
                      '\t\tid = QW2_cotton_mills\n\t\ticon = GFX_focus_generic_industry_2\n'
                      '\t\tx = 41'))[0]),
                  'changed a field outside completion_reward'))

    survivors = []
    for label, failures, expected in cases:
        named = ' '.join(failures)
        caught = expected in named
        print('mutant %-46s %s' % (label, 'caught' if caught else 'MISSED'))
        if not caught:
            survivors.append(label)
    assert not survivors, 'negative controls survived: %s' % survivors


TREE_TEXT = read(TREE)
LOC_TEXT = read(LOC)
CONSTANTS_TEXT = read(CONSTANTS)


def test_chapter_fields_are_frozen():
    failures = check_preservation(parse_text(TREE_TEXT)[0])
    assert not failures, '\n  '.join(failures)


def test_accepted_rewards_are_exact():
    failures = check_accepted_rewards(parse_text(TREE_TEXT)[0])
    assert not failures, '\n  '.join(failures)


def test_untouched_rewards_are_unchanged():
    failures = check_unchanged_rewards(parse_text(TREE_TEXT)[0])
    assert not failures, '\n  '.join(failures)


def test_no_repeated_reward_remains():
    failures = check_no_duplicate_reward(parse_text(TREE_TEXT)[0])
    assert not failures, '\n  '.join(failures)


def test_every_accepted_reward_is_localised():
    failures = check_player_visible(parse_text(TREE_TEXT)[0], read_loc())
    assert not failures, '\n  '.join(failures)


def test_every_tuning_value_is_a_constant():
    failures = check_constants(parse_text(TREE_TEXT)[0], CONSTANTS_TEXT)
    assert not failures, '\n  '.join(failures)


def test_negative_controls_report_named_failures():
    run_mutants()


def _run_all():
    failures = 0
    for name, function in sorted(globals().items()):
        if not name.startswith('test_') or not callable(function):
            continue
        try:
            function()
        except AssertionError as error:
            failures += 1
            print('FAIL %s: %s' % (name, error))
        else:
            print('PASS %s' % name)
    return failures


if __name__ == '__main__':
    raise SystemExit(1 if _run_all() else 0)
