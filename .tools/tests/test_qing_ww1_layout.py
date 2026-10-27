"""Regression test for the Qing 1910 (qing_ww1) focus tree.

Two properties are guarded, and both matter:

  * identity and non-layout content -- every focus id from the accepted 158-focus
    tree is still present, and each focus body is byte-identical to the baseline
    once only its own x/y value lines are removed. This is what makes a layout
    pass provably gameplay-neutral: a reward, prerequisite, icon, cost, ai_will_do,
    search-filter, bypass, availability or localisation-key edit changes the digest.
  * layout validity -- no two focuses share a cell, same-row pairs keep the engine's
    two-cell clearance, every prerequisite sits on a row above its child, coordinates
    stay inside the declared grid, and no third focus sits inside the marker space of
    a mutually exclusive pair.

Individual coordinates are intentionally NOT pinned: a future layout pass may move
any focus as long as both properties hold. The negative control at the end proves the
checks can fail, including on a reward edit and an icon swap.
"""
import hashlib
import os
import re
import shutil
import sys
import tempfile

TREE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'common', 'national_focus', 'qing_ww1.txt')

FOCUS_COUNT = 158
MAX_X = 44
MAX_Y = 22
MUTEX_GAP = 2

# sha256 of each focus body with only its x/y value lines removed, taken from the
# gameplay-state the layout pass started from.
BASELINE = {
    'QW1_regency_council':
        '22fe97ab909c043e9bb9e77aa10f648a05856e8764f197c572a36cfc05c271cf',
    'QW1_edict_of_reform':
        '05517c7e83e9552c0431bc03a01ab9ac901ca7726970ffd819bcf406deda4d4e',
    'QW1_court_resistance':
        '78e08bde858f8c5225b19c904bfd12395c56b4e24f1edc578713dc8077db7959',
    'QW1_provincial_assemblies':
        '029b5d3b781a0944df3c5467b18e68e54c14c1fe823058622a3a775b9af4d260',
    'QW1_legal_code':
        'e778947f9d93c0f97d05a3ae50bbab318254fbdbab15b6a9d57156e26bf2ba32',
    'QW1_grand_council':
        '5dfafdf07fcce64ea3556c2cadd5e89b79ea387471844dc742542882315532c8',
    'QW1_banner_privilege':
        'a44966e902b8c8e131f0739bd59a08749a5905ade5a49090a032f33134a5736e',
    'QW1_elective_assembly':
        '33520a0902e523a2627324cafda5bee9827d62f277f4213e785e9793ee7004c1',
    'QW1_budget_authority':
        '16efc863b6cc413608a61a767648b641bcf22185360424c17f34dfcf0b4e5153',
    'QW1_judicial_reform':
        '825c70e02019143416251e179111e96e69964624defc7832b69ffb8f8d9759ff',
    'QW1_court_appointments':
        '6c6558e2152b62a14dced03c8393fe1e44d6f05ece1dcea066500b56ccb8401c',
    'QW1_imperial_guard':
        '3c2e1e97e6feba2ac3b9eb1eb1799fdd4867186d6ff810ed0a7b9fea15375c62',
    'QW1_regency_end':
        'bcf840d8145e0d3244d2cc55b89c70521ddb3a7e2034887ffd379fec577f2c05',
    'QW1_constitutional_settlement':
        '2d416c6056d6e63be3754d70a1df6a07caf6c0b361d782359cad13b4c7c6cacb',
    'QW1_constitution_draft':
        '5ac13e15706464c594303c47af234edadfaa2be4eadf763b7fc03ecc2a2f55a5',
    'QW1_party_politics':
        'dfb5438e93f0b0568ed63b525f55a680dc01b26a04fcf09a264b767c6d49c8b5',
    'QW1_cabinet_responsibility':
        '7c297a51c2671b5f9062777f7de8c44c999b1747f9272c32ae27f0e21e9fd07f',
    'QW1_royal_prerogative':
        'ae94690cb9325a310d98cfd7ba0dfc67355949a11f6514d6717359f5a0d0f6f2',
    'QW1_constitutional_capstone':
        '56cd00b936d2859a3760d5af31cf41ca4d25d0a9408184c503b7ef8927c0025b',
    'QW1_autocratic_settlement':
        'd10af9cfa0460df105942f8016e82ee19436482e5bf8771edf15073318da28aa',
    'QW1_imperial_edicts':
        '230d21866c6c254819a3e54f795ee9f4d7db2c1cee842baa8d6cf1b9ab9baffb',
    'QW1_censorate':
        '5bf9464614bfc18f3ee476a52b72ee6229aff05a62ac82ffedf8b09e4400f96d',
    'QW1_dynastic_legitimacy':
        '8dcf672f9c80a107181015d609c1659f0778858ffcf3051170fb39a2a397d71a',
    'QW1_manchu_garrisons':
        '8e50575d36fd216a06f234e72d5d3dbfb77ac49374eb08c73595dfe77f61b665',
    'QW1_authoritarian_capstone':
        '2aa2c900e89172c31a900ad5131f816808057536afd7312ba77aa9132b208c6c',
    'QW1_imperial_treasury':
        '8ee053f8853fcef27580d593f49034b6ff982d0751f4efc5daabbfb6f0768d62',
    'QW1_salt_gabelle':
        'a654c78acacb595a2c69fa6fc916db21850bf95f9e4a48a219efc7020dd92731',
    'QW1_land_tax_survey':
        '4c11002590bd684a0a79a86182476d59f154efe4aa90c64923ccd27b75126826',
    'QW1_railway_programme':
        '4b91ca12c6ec4f5156c2ffec874229187bf204551bfe11d9826c7066b1891c63',
    'QW1_currency_board':
        'c8f7ef5b6b3122dffab80648d381c9db3ae16fb2c9c90f25b1c96e9f181ffc42',
    'QW1_telegraph_network':
        '0267bf14ed8470ef164e499d221d0f2af25014aa4d865b171bf6344ea63621d8',
    'QW1_hanyang_arsenal':
        'd9c34cdf56d04aa1dcfa605080704fd9322dea2a8ae5d400e1bf8972fa0cf368',
    'QW1_modern_banking':
        'e5c4598ac5588abcc7ddac7066faac64b28fbe5f0840f97c99ff8de2f2fcde42',
    'QW1_industrial_mission':
        'e269f575392dfdb80e278137d2b9b46e6b19f931f126dbf14c67335bb3f04b10',
    'QW1_national_budget':
        '97dafd9db8d7eef4fd882b877c07aa365b857d88fb73bd9eb0f039948b8012e2',
    'QW1_foreign_loans':
        '13349976cb10955c3e1d094e0eb93fa140263dd9eb54a82548eb144af5adebaa',
    'QW1_famine_administration':
        'e7c7a5a9048e980d48a338f4387234ca95a33f0430eae6b603f292be76a952fe',
    'QW1_arsenal_expansion':
        '97bdfa42359c57492bb5c0a174d4d5a9ac4085d971a81185d9f996a8b3a7a5af',
    'QW1_currency_capstone':
        'b055fe5bc05a75a21e5b30b232a7edf7e9220e86f71923569c0175b95e6c5c20',
    'QW1_new_army_budget':
        '77b53344046a9ec51014e94279b56a4ce6047158252a4f5a5388316ec53cd184',
    'QW1_officer_schools':
        'e57c480f6a5fe14285447f1c4313ab4dd90ca3087a0b37b14903bdd1963b43e8',
    'QW1_modern_drill':
        '1c68c482db9aa2219e9d7a1dfbd91b37d7fdef6a714d3bfd1b1c21784f21a725',
    'QW1_military_academy':
        '77b5de47201366aa35c3d0ca4f15872f04397fa7deedfec5d0a981d0c6b1d676',
    'QW1_artillery_corps':
        'afe630863c6991eda2146cf5a918f4716637fb1eb89fb6c20f0ccf05c0ac5662',
    'QW1_engineering_corps':
        'd156c745ec8ad786e2ae26a1cb148ec671454df7c855209e621f7c90f618e2c7',
    'QW1_german_instructors':
        'e91a886d859d72559bb53360539eacb92eca5d66d634dc23128320a2507ab84e',
    'QW1_national_arsenals':
        '0c5ae7e639d8284f49304968f362d890713e2df6088e0f89fb8669e4f14f4930',
    'QW1_supply_service':
        '550f5341f72bc11e6b9a102362b765b76e262cdb3e7e4eeabec9dcc4751062a5',
    'QW1_general_staff':
        'db415417efd86d4f95bff1008bab00a5e4b2d510b4716f2d6dbc4288e024540f',
    'QW1_frontier_garrisons':
        'fd20af064c6c5687742cf6617bb82568712da1edd0ad5c1d501a8c00e9dc718a',
    'QW1_army_capstone':
        '8e1c3d32790bcb18e8372ee04dc73ef8084e14a744dc1e7e84b17cb05c2d8771',
    'QW1_beiyang_command':
        '87c5698032f32de124da323a6a49fed550af82a4b53c5076891964da346f7cf4',
    'QW1_yuan_shikai_rise':
        '00a834791da4c088c7270f809f050ff48b2319f4df231848bdeb928c504a7824',
    'QW1_beiyang_officers':
        '9b5d2c95fdb5eeb436db380d3f1a7b2d08079e53c55dce9f86e5c44a5dd2f492',
    'QW1_yuan_premiership':
        '37a339526dd21e099c3f573d539499b9ad04a5846f0f708d2e63906a5c5f7c17',
    'QW1_yuan_cabinet':
        '329870f72ea30bd4da8bb0905c6b1e792583dfa3234116f1f1ebad24af47f4ae',
    'QW1_beiyang_loyalty':
        'da6b9a22c716958edc2629d61c994b5aa94981c3db883d65698e2482dd97e86b',
    'QW1_military_finance':
        '5a63169a00e25944a75f684b603d697850e6ae936ac58b16ff7329afa9b22e06',
    'QW1_army_politics':
        '21e6674f16b0f4402015be572a537a84905b81ca1744b18248f79d444d6e6e53',
    'QW1_yuan_succession':
        'e15c3eaf8c7b6a257000923efa5c150f35b9b91e6e30e8691dda3e36d0a2518a',
    'QW1_provincial_governors':
        'ac9ac1ccbe412a8ebc69fc5e63723f528e52625e9a745513d16a11b551102ac0',
    'QW1_gentry_compact':
        '25de7ffa566e7efe4788411654d1e2bb146688eafe2911508ddbc6d2b031c211',
    'QW1_provincial_assemblies_ii':
        '4a2c666f662f8c0ac183dd8e60db7c1ff75ec270c1248e9648cbccf10188234c',
    'QW1_provincial_taxation':
        'a73edbeb089a4600489059a5d4f99bbc79d422b598fd7f7ec69947ac68198fad',
    'QW1_local_militia':
        'b333095bc27758773eb4f3be404383df741746a2d92114c8d826e2e54c5916aa',
    'QW1_border_marches':
        '7f7e359fad9efa991b4a4fd769951a37c5e9bd3ecd19bd60bea9e2933bd7652b',
    'QW1_federal_settlement':
        '95592b6b281cc421e61abc076f594e9185a01de4d2d1b1598492e5384882aa0c',
    'QW1_provincial_charter':
        '6ca7561f367b257f54c92f1d9f5705d0756fef4b82c8e85309b0cc68bc7b16e7',
    'QW1_fiscal_compact':
        'b7fb5a25f54b883477e2da46f21f46547f69b55e9aaf47a3d1235365fb1673fe',
    'QW1_regional_armies':
        '0e5136ff09a77a31530fa1aafca0eeb9ed1fbd3f3e3cf87c73c3dd4e8bd7ff2e',
    'QW1_federal_capstone':
        '2e72355cbe2a0f022cb90f5320b740a4c52422b2e0ccf2cc9eaa24c1f381852e',
    'QW1_foreign_office':
        '466efc113fcb33daee7292fa48816a8cf572d505bc079db0dcc1b74e965a61ae',
    'QW1_treaty_ports':
        'ee40e36690adfe328b426a6672a371dcaca6251028a6021eec609f560f0c8f79',
    'QW1_boxer_indemnity':
        'c99f1bdded2aa205cb0b314cf44218599296f17d396be05d579ff5a92cfedeb2',
    'QW1_british_understanding':
        'a0d2a8e16fd9631df8a35fc9b1de55846faa920f2d439a1c86c60152b9c308dd',
    'QW1_german_military_mission':
        'fb63b93fc3ed14536f999c35b32bf3076892f72a4cec94abb48a3b423b751e72',
    'QW1_japanese_relations':
        'b1bfa6257f182d986510a34b7c0a4a8dd230a39ec29c38cd2fc95234205ceb08',
    'QW1_american_open_door':
        '055e7a7382e1cfc18ecd136f12f4d46e818ed237acd1683584808fcf42d17bd8',
    'QW1_french_mission':
        '45b4b49eebb1e4918a278fa31b0f520cf3516d2d458fdbdfc26ec7314d3800a8',
    'QW1_shandong_question':
        '2115812e28fcea1347286fb4938cb27e520b5929b465d2f4a761db7434790eba',
    'QW1_foreign_concessions':
        'e3557b459b4500c824e6f49233a9d0f49c60af8ad236f365f56a0de334e7a8fe',
    'QW1_diplomacy_capstone':
        '22ea7edad4e72a668d373d60c6ef91a1816e3dae9ae7d65069f05439b5d42864',
    'QW1_railway_guard':
        '59ffcc5f6f48ffa26bc11a9b7b1dcaaefe0e1b55daead0f359d9906e48b8aafc',
    'QW1_wuchang_garrison':
        'c0eecaee6eb0182ad7e511370d71ef997ee71a73d8fa9072e644dd5e30d5fa12',
    'QW1_provincial_loyalty':
        'd472f5c9fe6e84824d961ed72d7e73f3ef742515b7c9914064ecee42d2621de1',
    'QW1_capital_defences':
        '5b293bc2f681b878c91a49ecabf2dcf2dcedbeed372e1365e63a8e24fb18c07a',
    'QW1_revolution_prepared':
        'c7f1fd2fec652a9182c6f8dd41382f12dcc5a78cb640769744ac654a8c156553',
    'QW1_chapter_end':
        'f9d323db2a3cb3b2d83e7673240e11bc2a8270a92717141d9891ab29a53d2e92',
    'QW1_imperial_examinations':
        '3b1524ce1e0cd37ae8389bc08fc1fc0466b6b5df6f04cd0b396700435eca46e6',
    'QW1_regency_household':
        'd55c4ac09ce1b1d18cfd9e58bf41ef32e067a8ec33fda458e79adb19b3fa7fc1',
    'QW1_grain_reserves':
        '00a8588eab0564b4b53a1ba991f42c367ae6f071801488e615d30894e88cd83e',
    'QW1_cotton_mills':
        '59cf155f8b9a46b45992f6643dbfd3e38ce631b242f48e68b87df2594ee8086b',
    'QW1_steelworks':
        '77a478ae5d0952a083792898f46538062cb0465bbcb2e2d32b5cd15b9f483988',
    'QW1_cavalry_reform':
        '5703face1258458860a570d2ade932669622bfe32bd0bf7c81f0b75ad47e0af2',
    'QW1_railway_troops':
        'fd31d255a63e3b1a07ffcc58e34ea4a6233029081e66a801572aaada4f393182',
    'QW1_military_telegraph':
        'e31db58eefdcaa63b12212bb98086faa939148b82bcbc3e47338e75f62ea0721',
    'QW1_japanese_invasion':
        'efb2dad18f761ca9239669d90b8754c65984515b2cb8c7baaed94b1bf0694a15',
    'QW1_shandong_crisis':
        'e543ce638ffa4c0e6950212011eeaf663f58904d0ccede0327b5c42704d86e13',
    'QW1_defend_the_railway_zone':
        '6b2b80c6152312765f31a399bd14fd4c9c0ac61a154a02c0580c32a1e807e0c9',
    'QW1_boycott_japanese_goods':
        '4202477b250908bb175e55fe6e6817fa52d0021478621a3a7a3a5c4377813378',
    'QW1_arms_from_abroad':
        '6395df5758491ed5c2d2a7aeefe6e96e03cf41565f93b196556af5d50f2a8746',
    'QW1_appeal_to_the_powers':
        'd5e1d8f09c23a8d26b9a3cae0f172fb388c1d8383daaacb44363588d9d26e66d',
    'QW1_war_of_posts':
        'df771b38b507586238f310cef60c8c33a5e1b781c18607f7d2080fbe5c6ae049',
    'QW1_the_demands':
        '547ebecb1068bbea295f32addfeb2ab3b31244819561f4084e27e7827df27596',
    'QW1_reject_the_demands':
        '48cf46dab4ae2975566d5597e2c2770f995cea502de072b32d1625b62cebd8e2',
    'QW1_accept_and_endure':
        'f5064847bf7edbb6e1109bc54ed9129339fcff4ad74072aa384f1d8c30049a6b',
    'QW1_mobilise_the_north':
        '500d86d04f552a55e0965d27b14cb02ed230bce796231c062e843b2b4a86efd5',
    'QW1_national_humiliation':
        '5f21f3fd4eda8e5cae5a9ef4d9fd8d63c293dfbed3b531e48e3df3da4ec881f1',
    'QW1_long_war':
        'c0a6ec63ea7d24fef3aaf3218f11118fd675d81cd43f9fbc38812def59fd9a7f',
    'QW1_railway_protection':
        'ce3980ca5e31b6ca4d2607bee8e08e35db773ee1b5ee2ca20150d4200ed422b2',
    'QW1_sichuan_revolt':
        '57c79d2f7b817f2d3d64c5e91307d45275199bedd1985bbffe3d99e0bf15ddae',
    'QW1_wuchang_mutiny':
        '171bb2ad85d2e8112386a93e67b31747589d56c4b64427970973d6d1b98c1d5e',
    'QW1_provinces_declare':
        '918430bbe5b1de2affc929b0ba309f808583a82dc997f962360a04295ab77d55',
    'QW1_beiyang_terms':
        '2bd439b5b50f619288d06b266250b2c7275453d4fa7a90b2bc20963bcc915de7',
    'QW1_abdication_question':
        'acd5061ebd3aadc05fe606661d5810b9f59907e444ba90504ff55e04b34baf8b',
    'QW1_imperial_redoubt':
        '57df2532d03bcf12d3f6d24bdbc66195d242d8d275009d36f70959d998569dfe',
    'QW1_second_revolution':
        '52c4d16fc41e11ed95e0ceea154f11f2729c23f523e39e8d51bf1bf02f016421',
    'QW1_yuan_monarchy':
        '7b4861de91c410c0ee88debf1ad6c2e8b46546154e497a1394f4786993a31b15',
    'QW1_national_protection_war':
        '8b18883d167ceae0d4d493409c9f0c86815a71d9eadbfb362b6d5beeb2548e46',
    'QW1_restoration_1917':
        '452fbcbb2baa55ebeded769c470630eb350e2ba5b366f90affa16a541a453bd7',
    'QW1_join_the_war':
        '8a300d1060a0c71052441277021f0f3000e9914858db611d220ef7f41efa7c28',
    'QW1_new_schools':
        '7e121ea179d2d1d109801c959c5c82485a962689c11e587af7fc3db327a0aa99',
    'QW1_university_charter':
        'adb4969ac537182024c152d5a451917b1ff33b5e03af5c78cb28a3eee6741c18',
    'QW1_womens_education':
        'e22914bffd3c0c8940da48b501c68bcd6a7320d5e3f1d75f3635d7089bc21c81',
    'QW1_press_law':
        '1ca9e16866de6ff659058d19bc50748c317b65ff32c216bffdbd668a7a73c792',
    'QW1_student_politics':
        'cf789c353baba415e382bbea56bef2f8a17f7b02f53a26bb2bfd9b5a707dce24',
    'QW1_new_culture':
        '3f9206e29e74c4033acd10c90e3e7d909ba5705d7006bc47ead514eee8db066c',
    'QW1_public_health':
        'c1aa7214534d86ac0e7b9825c6c3903c9e128960c304dbc450dfac486c6fea89',
    'QW1_local_self_government':
        '18add541c74642dc20d0053691c7a782fff3df7050a7d729ee6a437f59569d7c',
    'QW1_labour_question':
        '8b4839377b737dcd5675d56a0638041bb73a4d95e459a20085dab18efb3d1db5',
    'QW1_land_tax_reform':
        '8d5fc5b75db21d7bbe03ec21c8e2867c411848084b37e1d93b8eb6759d8a8a74',
    'QW1_railway_finance':
        '534ea584d7f9f4b598caa3ea1974d9a8d46da568e8038bf1600a01551c4fd5b9',
    'QW1_grain_trade':
        '2ebf06530541f7163ceced82fcaaa1894f936a6a61f0e8025a5fc95a28a8fc6d',
    'QW1_industrial_labour':
        '43c587da83c0678ebf9fa5d0dc4a3270eceac1974e1b8537572647c909b0eb8b',
    'QW1_foreign_investment':
        '39deabb6fb2f8d299835e0e58af5c1d9b9c91fcb4073d84ce6aeee28863d38a8',
    'QW1_national_bank':
        '04bb367c00d3e8ce12d79bd115ee55c1e0bdb341d0107ede870f474c1593c4aa',
    'QW1_division_reorganisation':
        '24e0a2a5564ecf6a633107add415e24ce63036c6cfef280f8ee9ac17c84be9d3',
    'QW1_heavy_artillery':
        '70b6e2b713fafab39d65cab1a01857c61c61acc07e045a0999c312cd574c2744',
    'QW1_military_schools':
        '20a229e26675eb8fc77dbd25e6ea6265b7cfca02896d592fbf08dd32d5574607',
    'QW1_air_service':
        '81c7d67037adfaf2eabc2a5fb27599a76413c11a9e736224a79f2bba1ad55dae',
    'QW1_navy_reform':
        '0af904685a8b1d0552d56c78899d32ccc33e1db99be8204e5a9d58c34a671a26',
    'QW1_manchurian_garrisons':
        '57f6e75ec2f0efc99dde79eb68cef50d597addd4c78de9baa73d84c09dbd5e29',
    'QW1_military_industry':
        '4f2101389328463afab95638c0d8fa028ef3c089bda359c0cb78ecae70f36427',
    'QW1_conscription':
        'ab7498898c580b3dfaef0816b85f2b1f3bbfe8e5defab1eed5ea95db470b78a2',
    'QW1_railway_nationalisation':
        'f139a96676847e2dc5c5cb7c780d2c0de2faaa645b9c8fad673a958d25ecceea',
    'QW1_border_settlements':
        '47475108af813b3a33dd53c3164cc3aab608ba3845389e55bb3bfddfd6fd4b14',
    'QW1_manchurian_development':
        '19fd034f3a45d2a75614dd5230ec8a886cd4d684e1a845671bcfa6ec81cf171e',
    'QW1_southern_provinces':
        '68251840814abed36d3d7c1bb186a2f5e468eaf34979ece0bd81f377ebd2680e',
    'QW1_provincial_capstone':
        'f76bdce292099ab9a7a8f1c2e1eb42db557b691f5b6bdab68d493b93f5d0a276',
    'QW1_baoding_academy':
        '2580d0ea884be01db57ea17813b4f2fcfda742bf611761eda993174c743dba52',
    'QW1_yuan_health':
        '97845b2735565ee60d3941b8a9ed1ac626ca27f002169b38ebf0b47026b1f9b4',
    'QW1_zhili_clique':
        '4f4eae812c56451356647971564d8100208d9ea4a99b1acd793fbb5562219f39',
    'QW1_anhui_clique':
        '868465b4b9c9783a09bf79a787b91483ede42d849eb27a2cf753657e0a948fc4',
    'QW1_fengtian_clique':
        '6256d87e8506eb4758a3d5106d015a33419d66bc5b72293616aad4c4272c3f49',
    'QW1_military_governors':
        'f1a1be9334f7e5d6f3296a5078ad1fc2022669f535021d3f83420b68d4edad54',
    'QW1_beiyang_finance':
        '5f5896b77f893da02151080464d39052867fdb7b78027f11098701c00e5c6dd2',
    'QW1_beiyang_army':
        'd674e89345c9c36b18ef04eb9cf1c581a360b3a73d32a5f92605b3b3c07e481a',
    'QW1_beiyang_state':
        'c02e883d776ab8920d0a7cddd51a0c71f93b8a26973a83b6441aeb5158132b39',
}

FOCUS_START = re.compile(r'^\tfocus\s*=\s*\{', re.M)


def _strip_comments(text):
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


def _span(text, start):
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
    raise ValueError('unbalanced focus block')


def _normalise(body):
    lines = []
    for line in body.split('\n'):
        if re.match(r'^\s*[xy]\s*=\s*-?\d+\s*$', line):
            continue
        lines.append(line.rstrip())
    return '\n'.join(lines)


def parse(path):
    text = _strip_comments(open(path, encoding='utf-8-sig').read().replace('\r\n', '\n'))
    focuses = {}
    order = []
    for match in FOCUS_START.finditer(text):
        body = text[match.start():_span(text, match.start())]
        focus_id = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', body).group(1)
        x = int(re.search(r'^\s*x\s*=\s*(-?\d+)', body, re.M).group(1))
        y = int(re.search(r'^\s*y\s*=\s*(-?\d+)', body, re.M).group(1))
        groups = re.findall(r'prerequisite\s*=\s*\{([^}]*)\}', body)
        parents = [p for group in groups for p in re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)', group)]
        mutex = []
        for block in re.finditer(r'mutually_exclusive\s*=\s*\{([^}]*)\}', body):
            mutex += re.findall(r'focus\s*=\s*([A-Za-z0-9_]+)', block.group(1))
        focuses[focus_id] = {
            'x': x,
            'y': y,
            'parents': parents,
            'mutex': mutex,
            'digest': hashlib.sha256(_normalise(body).encode('utf-8')).hexdigest(),
        }
        order.append(focus_id)
    return focuses, order


def problems(focuses, order, baseline=None):
    baseline = BASELINE if baseline is None else baseline
    found = []
    if len(focuses) != FOCUS_COUNT:
        found.append('declares %d focuses, expected %d' % (len(focuses), FOCUS_COUNT))
    missing = sorted(set(baseline) - set(focuses))
    extra = sorted(set(focuses) - set(baseline))
    for focus_id in missing:
        found.append('missing focus %s' % focus_id)
    for focus_id in extra:
        found.append('unexpected focus %s' % focus_id)
    for focus_id in sorted(set(focuses) & set(baseline)):
        if focuses[focus_id]['digest'] != baseline[focus_id]:
            found.append('%s changed outside its x/y coordinates' % focus_id)
    cells = {}
    for focus_id, data in focuses.items():
        cells.setdefault((data['x'], data['y']), []).append(focus_id)
    for cell, ids in cells.items():
        if len(ids) > 1:
            found.append('duplicate cell %s: %s' % (cell, ', '.join(sorted(ids))))
    rows = {}
    for focus_id, data in focuses.items():
        rows.setdefault(data['y'], []).append((data['x'], focus_id))
    for y, items in rows.items():
        items.sort()
        for (x1, id1), (x2, id2) in zip(items, items[1:]):
            if x2 - x1 < 2:
                found.append('row %d: %s at x=%d is %d cell from %s at x=%d'
                             % (y, id2, x2, x2 - x1, id1, x1))
    for focus_id, data in focuses.items():
        for parent in data['parents']:
            if parent not in focuses:
                found.append('%s has a prerequisite naming missing focus %s' % (focus_id, parent))
            elif focuses[parent]['y'] >= data['y']:
                found.append('%s (y=%d) is not below its prerequisite %s (y=%d)'
                             % (focus_id, data['y'], parent, focuses[parent]['y']))
        if data['x'] < 0 or data['x'] > MAX_X or data['y'] < 0 or data['y'] > MAX_Y:
            found.append('%s at (%d,%d) is outside the declared %dx%d grid'
                         % (focus_id, data['x'], data['y'], MAX_X, MAX_Y))
    # mutually exclusive marker space: a third focus within MUTEX_GAP cells of either
    # endpoint, on the same row between the pair or in the same column, owns the space
    # the engine draws the exclusivity marker in.
    for focus_id in order:
        for partner_id in focuses[focus_id]['mutex']:
            if partner_id not in focuses or focus_id > partner_id:
                continue
            partner = focuses[partner_id]
            mine = focuses[focus_id]
            related = {focus_id, partner_id} | set(mine['mutex']) | set(partner['mutex'])
            for other_id, other in focuses.items():
                if other_id in related:
                    continue
                if partner['y'] == mine['y'] == other['y'] and \
                        min(mine['x'], partner['x']) < other['x'] < max(mine['x'], partner['x']) and \
                        min(abs(other['x'] - mine['x']), abs(other['x'] - partner['x'])) <= MUTEX_GAP:
                    found.append('mutex marker space of %s/%s is occupied by %s at (%d,%d)'
                                 % (focus_id, partner_id, other_id, other['x'], other['y']))
                elif partner['x'] == mine['x'] == other['x'] and \
                        min(mine['y'], partner['y']) < other['y'] < max(mine['y'], partner['y']) and \
                        min(abs(other['y'] - mine['y']), abs(other['y'] - partner['y'])) <= MUTEX_GAP:
                    found.append('mutex marker space of %s/%s is occupied by %s at (%d,%d)'
                                 % (focus_id, partner_id, other_id, other['x'], other['y']))
    return found


def _mutant(edit):
    """Copy the tree to a temp file, apply edit(text) -> text, return the problems."""
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, 'qing_ww1.txt')
        text = open(TREE, encoding='utf-8-sig').read()
        changed = edit(text)
        assert changed != text, 'mutation did not change the file'
        with open(path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(changed)
        focuses, order = parse(path)
        return problems(focuses, order)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_identity_and_non_layout_preservation():
    focuses, order = parse(TREE)
    found = [p for p in problems(focuses, order) if 'cell' not in p and 'row ' not in p
             and 'prerequisite' not in p and 'mutex marker' not in p]
    assert not found, 'non-layout content drifted:\n  ' + '\n  '.join(found)


def test_layout_invariants():
    found = problems(*parse(TREE))
    assert not found, 'layout problems:\n  ' + '\n  '.join(found)


def test_negative_control_detects_reward_icon_and_layout_mutations():
    """Every class of edit the pass must not make has to be caught."""
    def edit(file_text, old, new):
        assert old in file_text, 'mutation anchor missing: %r' % old
        return file_text.replace(old, new, 1)

    NL = chr(10)
    TB = chr(9)
    tab2 = TB * 2
    tab3 = TB * 3

    cases = {
        # reward tuning constant renamed inside a completion_reward block
        'reward constant': lambda t: edit(
            t, 'qing_reform = constant:qing_story.reform_gain',
            'qing_reform = constant:qing_story.reform_gain_next'),
        # one extra reward line inserted into an existing block
        'extra reward line': lambda t: edit(
            t, 'add_to_variable = { qing_reform = constant:qing_story.reform_gain }',
            'add_stability = constant:qing_story.stability_gain' + NL + tab3
            + 'add_to_variable = { qing_reform = constant:qing_story.reform_gain }'),
        # different artwork, same focus
        'icon swap': lambda t: edit(
            t, 'icon = GFX_focus_generic_monarchy_1', 'icon = GFX_focus_generic_monarchy_3'),
        # a leaf renamed
        'leaf id rename': lambda t: edit(t, 'id = QW1_conscription', 'id = QW1_conscription_renamed'),
        # prerequisite repointed at a focus far below the child
        'prerequisite reversed': lambda t: edit(
            t, 'prerequisite = { focus = QW1_regency_council }',
            'prerequisite = { focus = QW1_labour_question }'),
        # two focuses on one cell
        'duplicate cell': lambda t: edit(
            t, 'id = QW1_court_resistance' + NL + tab2 + 'icon = GFX_focus_generic_monarchy_2'
            + NL + tab2 + 'x = 16',
            'id = QW1_court_resistance' + NL + tab2 + 'icon = GFX_focus_generic_monarchy_2'
            + NL + tab2 + 'x = 11'),
        # same-row clearance below the engine minimum
        'tight row': lambda t: edit(
            t, 'id = QW1_regency_household' + NL + tab2 + 'icon = GFX_focus_generic_monarchy_2'
            + NL + tab2 + 'x = 11',
            'id = QW1_regency_household' + NL + tab2 + 'icon = GFX_focus_generic_monarchy_2'
            + NL + tab2 + 'x = 6'),
        # third focus inside a mutually exclusive pair's marker space
        'mutex intruder': lambda t: edit(
            t, 'id = QW1_university_charter' + NL + tab2 + 'icon = GFX_focus_generic_university_2'
            + NL + tab2 + 'x = 1',
            'id = QW1_university_charter' + NL + tab2 + 'icon = GFX_focus_generic_university_2'
            + NL + tab2 + 'x = 11'),
    }
    missed = []
    for name, mutation in cases.items():
        try:
            found = _mutant(mutation)
        except AssertionError:
            missed.append(name + ' (anchor missing)')
            continue
        if not found:
            missed.append(name)
    assert not missed, 'mutations the test does not detect: ' + ', '.join(missed)
