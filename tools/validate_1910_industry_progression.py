"""Validate research-driven prewar industry without launching HOI4.

Uses the installed vanilla technology payloads, exact preserved-field fingerprints,
and a restricted interpreter of the actual country-effect DSL. Technology values
are additive modifier points; country laws, focuses and spirits are outside scope.
Run: python tools/validate_1910_industry_progression.py --vanilla ".../Hearts of Iron IV"
"""
from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import argparse,hashlib,json,re,math
from validate_1194_compatibility import parse

def child(n,k):return next(x for x in n.children if x.key==k)
def scalar(n,k):
 x=next((x for x in n.children if x.key==k),None)
 return x.value.strip('"') if x is not None and isinstance(x.value,str) else None
def ast(n):return (n.key,n.op or None,tuple(ast(x) for x in n.children) if isinstance(n.value,list) else n.value)
def read(p):
 raw=p.read_bytes();s=raw.decode('utf-8-sig');return raw,s,parse(s)
def write_json(p,data):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
def hashast(n):return hashlib.sha256(json.dumps(ast(n),separators=(',',':')).encode()).hexdigest()
u=SimpleNamespace(child=child,scalar=scalar,ast=ast,read=read,write_json=write_json)
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
ap.add_argument('--vanilla',type=Path,required=True)
ap.add_argument('--report',type=Path)
args=ap.parse_args();R=args.repo;V=args.vanilla
checks=0
cfg = {'groups': [{'stat': 'production_factory_max_efficiency_factor',
             'base': -0.15,
             'sources': {'early_machine_tools': 0.03,
                         'improved_early_machine_tools': 0.03,
                         'advanced_early_machine_tools': 0.03,
                         'demobilization_machine_tools': 0.03,
                         'basic_machine_tools': 0.03},
             'mature': ['basic_machine_tools',
                        'improved_machine_tools',
                        'advanced_machine_tools',
                        'assembly_line_production',
                        'flexible_line',
                        'streamlined_line',
                        'flexible_line_a',
                        'streamlined_line_a',
                        'streamlined_line_b',
                        'streamlined_line_c',
                        'streamlined_line_d'],
             'variable': 'endsieg_industry_production_factory_max_efficiency_factor'},
            {'stat': 'industrial_capacity_factory',
             'base': -0.2,
             'sources': {'total_war1': 0.04,
                         'total_war2': 0.04,
                         'total_war3': 0.04,
                         'demobilization2': 0.03,
                         'concentrated_industry': 0.05,
                         'dispersed_industry': 0.05},
             'mature': ['concentrated_industry',
                        'concentrated_industry2',
                        'concentrated_industry3',
                        'concentrated_industry4',
                        'concentrated_industry5',
                        'dispersed_industry',
                        'dispersed_industry2',
                        'dispersed_industry3',
                        'dispersed_industry4',
                        'dispersed_industry5',
                        'concentrated_industry_a',
                        'dispersed_industry_a',
                        'concentrated_industry_b',
                        'dispersed_industry_b',
                        'concentrated_industry_c',
                        'dispersed_industry_c',
                        'concentrated_industry_d',
                        'dispersed_industry_d'],
             'variable': 'endsieg_industry_industrial_capacity_factory'},
            {'stat': 'industrial_capacity_dockyard',
             'base': -0.15,
             'sources': {'total_war1': 0.03,
                         'total_war2': 0.03,
                         'total_war3': 0.03,
                         'demobilization2': 0.01,
                         'concentrated_industry': 0.05,
                         'dispersed_industry': 0.05},
             'mature': ['concentrated_industry',
                        'concentrated_industry2',
                        'concentrated_industry3',
                        'concentrated_industry4',
                        'concentrated_industry5',
                        'dispersed_industry',
                        'dispersed_industry2',
                        'dispersed_industry3',
                        'dispersed_industry4',
                        'dispersed_industry5',
                        'concentrated_industry_a',
                        'dispersed_industry_a',
                        'concentrated_industry_b',
                        'dispersed_industry_b',
                        'concentrated_industry_c',
                        'dispersed_industry_c',
                        'concentrated_industry_d',
                        'dispersed_industry_d'],
             'variable': 'endsieg_industry_industrial_capacity_dockyard'},
            {'stat': 'production_speed_buildings_factor',
             'base': -0.25,
             'sources': {'construction1': 0.025,
                         'construction2': 0.025,
                         'construction3': 0.025,
                         'construction4': 0.025,
                         'constructiondemob': 0.025,
                         'construction5': 0.05,
                         'construction6': 0.025,
                         'construction7': 0.05},
             'mature': ['construction7',
                        'construction8',
                        'construction9',
                        'construction10',
                        'construction11',
                        'construction_a',
                        'construction_b',
                        'construction_c',
                        'construction_d'],
             'variable': 'endsieg_industry_production_speed_buildings_factor'},
            {'stat': 'local_resources_factor',
             'base': -0.2,
             'sources': {'construction1': 0.025,
                         'construction2': 0.025,
                         'construction3': 0.025,
                         'construction4': 0.025,
                         'constructiondemob': 0.025,
                         'construction5': 0.025,
                         'construction6': 0.025,
                         'construction7': 0.025},
             'mature': ['construction7',
                        'construction8',
                        'construction9',
                        'construction10',
                        'construction11',
                        'construction_a',
                        'construction_b',
                        'construction_c',
                        'construction_d',
                        'excavation1',
                        'excavation2',
                        'excavation3',
                        'excavation4',
                        'excavation5',
                        'excavation_a',
                        'excavation_b',
                        'excavation_c',
                        'excavation_d'],
             'variable': 'endsieg_industry_local_resources_factor'}],
 'stat_changes': {'early_machine_tools': {'production_factory_max_efficiency_factor': 0.03},
                  'improved_early_machine_tools': {'production_factory_max_efficiency_factor': 0.03},
                  'advanced_early_machine_tools': {'production_factory_max_efficiency_factor': 0.03},
                  'demobilization_machine_tools': {'production_factory_max_efficiency_factor': 0.03},
                  'basic_machine_tools': {'production_factory_max_efficiency_factor': 0.13,
                                          'equipment_conversion_speed': 0.2},
                  'total_war1': {'industrial_capacity_factory': 0.04,
                                 'industrial_capacity_dockyard': 0.03,
                                 'production_factory_max_efficiency_factor': 0.02,
                                 'global_building_slots_factor': 0.10},
                  'total_war2': {'industrial_capacity_factory': 0.04,
                                 'industrial_capacity_dockyard': 0.03,
                                 'production_factory_max_efficiency_factor': 0.02,
                                 'global_building_slots_factor': 0.10},
                  'total_war3': {'industrial_capacity_factory': 0.04,
                                 'industrial_capacity_dockyard': 0.03,
                                 'production_factory_max_efficiency_factor': 0.02,
                                 'global_building_slots_factor': 0.10},
                  'demobilization2': {'industrial_capacity_factory': 0.03,
                                      'industrial_capacity_dockyard': 0.01,
                                      'production_factory_max_efficiency_factor': -0.06,
                                      'global_building_slots_factor': -0.30},
                  'concentrated_industry': {'industrial_capacity_factory': 0.2,
                                            'industrial_capacity_dockyard': 0.15},
                  'dispersed_industry': {'industrial_capacity_factory': 0.15,
                                         'industrial_capacity_dockyard': 0.15,
                                         'industry_air_damage_factor': -0.15},
                  'construction1': {'production_speed_buildings_factor': 0.025,
                                    'local_resources_factor': 0.025},
                  'construction2': {'production_speed_buildings_factor': 0.025,
                                    'local_resources_factor': 0.025},
                  'construction3': {'production_speed_buildings_factor': 0.025,
                                    'local_resources_factor': 0.025},
                  'construction4': {'production_speed_buildings_factor': 0.025,
                                    'local_resources_factor': 0.025},
                  'constructiondemob': {'production_speed_buildings_factor': 0.025,
                                        'local_resources_factor': 0.025},
                  'construction5': {'production_speed_buildings_factor': 0.05,
                                    'local_resources_factor': 0.025},
                  'construction6': {'production_speed_buildings_factor': 0.025,
                                    'local_resources_factor': 0.025},
                  'construction7': {'production_speed_buildings_factor': 0.15,
                                    'local_resources_factor': 0.025,
                                    'industry_repair_factor': 0.1},
                  'improved_machine_tools': {'equipment_conversion_speed': 0.2},
                  'advanced_machine_tools': {'equipment_conversion_speed': 0.2,
                                             'production_factory_max_efficiency_factor': 0.1},
                  'construction8': {'industry_repair_factor': 0.1},
                  'construction9': {'industry_repair_factor': 0.1,
                                    'production_speed_buildings_factor': 0.1},
                  'excavation1': {'local_resources_coal_factor': 0.05},
                  'excavation2': {'local_resources_coal_factor': 0.05},
                  'excavation3': {'local_resources_coal_factor': 0.05}},
 'watched': ['advanced_early_machine_tools',
             'advanced_machine_tools',
             'assembly_line_production',
             'basic_machine_tools',
             'concentrated_industry',
             'concentrated_industry2',
             'concentrated_industry3',
             'concentrated_industry4',
             'concentrated_industry5',
             'concentrated_industry_a',
             'concentrated_industry_b',
             'concentrated_industry_c',
             'concentrated_industry_d',
             'construction1',
             'construction10',
             'construction11',
             'construction2',
             'construction3',
             'construction4',
             'construction5',
             'construction6',
             'construction7',
             'construction8',
             'construction9',
             'construction_a',
             'construction_b',
             'construction_c',
             'construction_d',
             'constructiondemob',
             'demobilization2',
             'demobilization_machine_tools',
             'dispersed_industry',
             'dispersed_industry2',
             'dispersed_industry3',
             'dispersed_industry4',
             'dispersed_industry5',
             'dispersed_industry_a',
             'dispersed_industry_b',
             'dispersed_industry_c',
             'dispersed_industry_d',
             'early_machine_tools',
             'excavation1',
             'excavation2',
             'excavation3',
             'excavation4',
             'excavation5',
             'excavation_a',
             'excavation_b',
             'excavation_c',
             'excavation_d',
             'flexible_line',
             'flexible_line_a',
             'improved_early_machine_tools',
             'improved_machine_tools',
             'streamlined_line',
             'streamlined_line_a',
             'streamlined_line_b',
             'streamlined_line_c',
             'streamlined_line_d',
             'total_war1',
             'total_war2',
             'total_war3'],
 'description_keys': ['constructiondemob_desc',
                      'demobilization2_desc',
                      'demobilization_machine_tools_desc']}
groups=cfg["groups"]
PROTECTED = {'early_machine_tools': '95e0e1b9e3226be7f788fa6fe80df149512af28f24719f02c46e2e3354738a38',
 'improved_early_machine_tools': '8222345790432ddd76684a0d0513ed47ca396681ac00186053707c31097e407c',
 'advanced_early_machine_tools': 'eead9951e6628bd944bc365d5c4d48e350a4b1b9cd86e3c07a766d1b60650f13',
 'demobilization_machine_tools': 'ae3b03aa2b6b5ec37076cde808b3e9a871de2cd3cb79fb4c6b11b6c9f08d5556',
 'basic_machine_tools': '5d3157f2cd6c34fc1b7eb4cc312b512ef270a31deb70336cfd4cf9d2646caade',
 'improved_machine_tools': 'c9760389dd7d7d20df64a3101f845f2481bfda7b8d4f9c9bd23cab9d6ba70ec1',
 'advanced_machine_tools': 'ab11b0648f8c2a0b521c6a262e5930eed09985fe505a9ad7a267858cc7a6f21d',
 'assembly_line_production': '2894d3a8b99ef45773df0a7994b4c2a5ba47c4bb22f56d6c395b7402dbd4f9b3',
 'flexible_line': '26f1e30ebf446327d7741ad307692780078cdf03ad1b21d29458e58253587779',
 'streamlined_line': '15c0a9c40d83d268bed33119addc7b97a142fcbc825c05b526df3bef62281417',
 'flexible_line_a': 'aa2fbc654b5d44c83362061cd331ae54986ac19e746eb866617395f1a3e5055a',
 'streamlined_line_a': '8f5da72120a0355a4b7e6763b1cae993d96265e5a9c22078b15df48113aa908f',
 'streamlined_line_b': '90b4cdff8fc17c5e6ae152fad70b016114fabd8c7166c8f207278de020186cc2',
 'streamlined_line_c': '80f82e9636474614882c776132830f62236f288e4925b5c927dc547facc80b7a',
 'streamlined_line_d': '4500b4a1e270b591daac7d84f929fa73b0533b56c9856ad16764d5e45a77425b',
 'total_war1': '7cdc1f8d83b84e2ce1635bc16da40e99017455f184b875f9b10697708082522b',
 'total_war2': 'ca5bff745cad098754e3092e74deb1a994172fd7093148d4e8b5bf245e4d12e0',
 'total_war3': 'a9460232683a252ff5cdb3101e614e983177c744591b8e677e6b3cf5c66c5e78',
 'demobilization2': '864047154f9afb7824108a79e24913c346af01a1d6b591ba3594c3da456123ff',
 'concentrated_industry': '8dc31138ad32cd9f9b7e2aadbb01a2a8603666ef3df5c48f3f130493c5454379',
 'concentrated_industry2': '369e299a21f8042bc2f9d2fc8085fec953b7682c0138c25090e7fbb7c07f308f',
 'concentrated_industry3': '15afcc07213beda146c94d24467535e79efcacf2104d1af42793d74c1e9322b3',
 'concentrated_industry4': '15b7871fa5d221d14f3578ad4a437f9a9685db9856cc438b0116c1b3cbc0caaa',
 'concentrated_industry5': 'bdfee2429b01edfa0dbaebba4985ffe4396a84ee733df10648dd1f96da7fd812',
 'dispersed_industry': '6c746c679ea2393e6ff76bdb2d6288f2710d182287817677ad58e0020dc5c749',
 'dispersed_industry2': '0a820b97e944a705f0761fa32ebc45238bcb5aa948b972baaa56beb773e355d3',
 'dispersed_industry3': '55642b55c83cad4a8b9764a63680b8e04516ee11b19e0a833e38cc8c1f7e1391',
 'dispersed_industry4': '57e56fac71175d113ec08f9289707a6fcbb0f2a9e115e51aef3486c510f75afb',
 'dispersed_industry5': 'c85503126608a1d92ad419b6b3af90fc02f60d0192d5c005a1e093700aad00db',
 'concentrated_industry_a': 'acac0eb9e0967db7e19aed3f9a33c50a6ae7078298bf9bcdf66e4bf121357f65',
 'dispersed_industry_a': 'af21427e11a274f48abc60e8f252e770f0cad40a34f49fcba0af6a28ecedd4ae',
 'concentrated_industry_b': '85140711ae6713a67df71a88b30e2b6823a2a8dbd9020b7df8902a7804d2d82b',
 'dispersed_industry_b': 'b2a31ec81134005f47dc6060ed18a685cc5b3d2d9220b612442b0be533a6a99a',
 'concentrated_industry_c': '472ff195f4fb3c3ad617ba9a7fad9216af06c36ba0410d11edf93814bb61c3ba',
 'dispersed_industry_c': 'fa6f4505ba5160d1e2b2aef44664c1096be3e55f8355a4f25d13e5908ecb779e',
 'concentrated_industry_d': 'e3ecc573da9e8098725822b9da9491a31f6638c333ea02a83bdf907f1a5e2b50',
 'dispersed_industry_d': '4adb83ba700822473839ee2b9e824a8c32823629f48a04dd59daeb9766d5b4f6',
 'fuel_silos': '3c263e9af816957c3d1dc7ec55f795f6477acf0aa5433eb740e3c65dcc609428',
 'fuel_refining': '77d33fda32e4516886a06f6aa0f1bae45d03423ea9a51e2464b68a3e5ce356dd',
 'fuel_refining2': '6e42dc00fa8ed0ac5716e96e9084151e485df648eca04bd6d50b930ba7055c12',
 'fuel_refining3': '000f24c65822837ad2aa1b06d830f8a3f0b6541185b9ac2fc8543887b1a33b6c',
 'fuel_refining4': '9b230580ef7aeabf3606c2ec65b0990df0e18c1e58f8a07d61db225b39067045',
 'fuel_refining5': '4400166debe9d5f023c73da70e44161c78dc48194b4feef143df38408c5e8025',
 'synth_oil_experiments': 'ac2af404ce9e1dc9fa304f6057fea658bd51026c68af4a318d421f25ce5d8267',
 'oil_plant': 'cd023ca8d5e022b1df9b987ad66a8764c8eb5feca5185c17cf9c72d6a473cc4f',
 'improved_oil_plant': 'fbeffbc8eeb0d1ae16f7482a3807020a1f7fdfca922cd20f0cfea3b4bc123b21',
 'advanced_oil_plant': '6f91ae24b042301c83e567e2f7fdfead0968e523a756835fcf010eb8b8287357',
 'advanced_oil_plant_2': 'be7566a5b3c11b4aa9c467f1fb10fceda1b2372e733108a4943c3a7af9757548',
 'advanced_oil_plant_3': '55c186b12c87b048d8cec986429c754d496759f0060154278067ffd8e9274f67',
 'synth_rubber_experiments': '1e14e2b199a7ead1af257272742ab74b8ca46636685e794735f2dfb99c4139f9',
 'rubber_plant': '585300d666e4952aa57d54447d1866d63221c2bf1ea75f07f8a1bc3514f9b3f3',
 'improved_rubber_plant': '67593db324da45aa7b647b87db50ce6fa1ed37030f3070924a570452bbffae91',
 'advanced_rubber_plant': '5f522e0aaa720661d122b26e0827cb6863d2246c364873c82095a3deae1cf241',
 'advanced_rubber_plant_2': 'de64b64735ffcc182477362aaa2df3a96061017c6aef2ba6accf8c2fec0b8951',
 'advanced_rubber_plant_3': 'f24ba3983fd0817c78f678acf6781e46f235ea026d41d05c76b63658471863a7',
 'trench_warfare': '14d816dbb4db17f611d13b3255cb0469f396f43374d88a460f405f53c75a6929',
 'wood_flooring': 'c0000961fe753a1481b4b6d0c51db5269a228d313e5b2f23a2f2aa3b90aadab3',
 'better_trench_conditions': '5e51b203eb15b62d4937e1d890c1b8a7f46ef35d4543907de0acc201ab7f0658',
 'anti_air52': 'e3d3263f0710ac1213dd62441da90dbca5371f5925a0fc04aacbe06153ad4a98',
 'construction1': '54e4d9117590b0f995cab3692702369da344ae67088087555e0009753d5212c6',
 'construction2': '734284c9a82dda87d5bb644fb1190f612352a5c1187fecc17d1e8d38775ea92c',
 'construction3': 'f8444449c32ea3c23661a5266e747d32f5e857c6538f22d7316ae365d79e3e2a',
 'construction4': '3d166c74762cc7761a635fcd20ad5687aad1a5b250f86a494ee1768a42e725d4',
 'constructiondemob': '3a285bc05a60ca5d944ecad7020bd1411bfc80abd6765296e4daa3f666852efa',
 'construction5': 'ddad27aea05122783b50cf160811b7dec912b91a62c7fc2d656191844bb41c11',
 'construction6': 'b7a427a1ef21c9e6c09e21070da405ac34434ffd0d4624989a523e14085d4403',
 'construction7': 'f8b944adb1d25f8901e5e86646d7458b2dcc9bdda719ddbbadf491acef4930d9',
 'excavation1': '683a8cdb7435dccf0c9da90b5bc819a2642ad50fbdceff408b10f43b845fcce0',
 'construction8': 'e35e5e9692b6997a86823678046ae18466e861dd04f942437ab2f57b8f78c50a',
 'excavation2': 'c246331f38f7425bfd98de70b6cf609c4e47bfb589754376705f1f4609868aa9',
 'construction9': 'ee50d1f4d9f54e8be145afbc662a44aa9d1df8c6b2d8eea550609945c606adf8',
 'excavation3': '45a9b97920dd438dd0bd21e078771fc738dd7de9f375ea1a779c3fb1f172b63c',
 'construction10': '1257366ee3521b0becdccbf5b91ad2ed9ff04ac826aa447e217d5491d4208f93',
 'excavation4': '15aefb2d44a86c4e82b3533f10a8c887c598ad0ed68f7f9b8a628187d97db978',
 'construction11': '28a4d7ed60454171157e2bd3088f4b1db836ce0483193c47951c87668490fa9b',
 'excavation5': 'e1856a96ca0b9616e2f171abbf5ceeb44d7e11fe407fb2219cc32fdf2aebd726',
 'construction_a': 'f3c1b232cef15c29dedccb3433f12c75a4caa4ae3ee7481d2f49bea154287346',
 'excavation_a': '2caa34aba2666a64e98580b7e73367a00201ebdf96f95e9862473fa6768830c1',
 'construction_b': 'e0f4cd2aa27ae931f863a73b7088d4046365fdff0411a98efaba31c0f3c6799d',
 'excavation_b': '416bc6b43018410aaa6e5c708f8eae60c9ea5b0ef4d8cb66368bb033a344a440',
 'construction_c': '44fac47eaa7824f373f5652f46b5431752c85b00897cd4861f61945ea5398743',
 'excavation_c': '44c9f98415307e2f39457655502d95c22f9bb92bd0deaac2758660b69f0bd641',
 'construction_d': 'd59c5ab6966e698506a752a212410286401b4780c4eef18c562abfa49cbcb922',
 'excavation_d': 'b059337ed3d49bd1f6836d05fe90f94f2b12e535bc5449a978b50f80f4245c9b',
 'oil_processing': '57c23bf490260013cc39b0f757316f8e9a0bdd67448eb01a8aa3898f12c74f73',
 'improved_oil_processing': '93d4fb65f5eb06bfbbf5b623c8ad7212ac167f6bd1daec31bdc5107a0e232961'}
LATE = {'assembly_line_production': '2894d3a8b99ef45773df0a7994b4c2a5ba47c4bb22f56d6c395b7402dbd4f9b3',
 'flexible_line': '26f1e30ebf446327d7741ad307692780078cdf03ad1b21d29458e58253587779',
 'streamlined_line': '15c0a9c40d83d268bed33119addc7b97a142fcbc825c05b526df3bef62281417',
 'flexible_line_a': 'aa2fbc654b5d44c83362061cd331ae54986ac19e746eb866617395f1a3e5055a',
 'streamlined_line_a': '8f5da72120a0355a4b7e6763b1cae993d96265e5a9c22078b15df48113aa908f',
 'streamlined_line_b': '90b4cdff8fc17c5e6ae152fad70b016114fabd8c7166c8f207278de020186cc2',
 'streamlined_line_c': '80f82e9636474614882c776132830f62236f288e4925b5c927dc547facc80b7a',
 'streamlined_line_d': '4500b4a1e270b591daac7d84f929fa73b0533b56c9856ad16764d5e45a77425b',
 'concentrated_industry4': '15b7871fa5d221d14f3578ad4a437f9a9685db9856cc438b0116c1b3cbc0caaa',
 'concentrated_industry5': 'bdfee2429b01edfa0dbaebba4985ffe4396a84ee733df10648dd1f96da7fd812',
 'dispersed_industry4': '57e56fac71175d113ec08f9289707a6fcbb0f2a9e115e51aef3486c510f75afb',
 'dispersed_industry5': 'c85503126608a1d92ad419b6b3af90fc02f60d0192d5c005a1e093700aad00db',
 'concentrated_industry_a': 'acac0eb9e0967db7e19aed3f9a33c50a6ae7078298bf9bcdf66e4bf121357f65',
 'dispersed_industry_a': 'af21427e11a274f48abc60e8f252e770f0cad40a34f49fcba0af6a28ecedd4ae',
 'concentrated_industry_b': '85140711ae6713a67df71a88b30e2b6823a2a8dbd9020b7df8902a7804d2d82b',
 'dispersed_industry_b': 'b2a31ec81134005f47dc6060ed18a685cc5b3d2d9220b612442b0be533a6a99a',
 'concentrated_industry_c': '472ff195f4fb3c3ad617ba9a7fad9216af06c36ba0410d11edf93814bb61c3ba',
 'dispersed_industry_c': 'fa6f4505ba5160d1e2b2aef44664c1096be3e55f8355a4f25d13e5908ecb779e',
 'concentrated_industry_d': 'e3ecc573da9e8098725822b9da9491a31f6638c333ea02a83bdf907f1a5e2b50',
 'dispersed_industry_d': '4adb83ba700822473839ee2b9e824a8c32823629f48a04dd59daeb9766d5b4f6',
 'fuel_refining3': '000f24c65822837ad2aa1b06d830f8a3f0b6541185b9ac2fc8543887b1a33b6c',
 'fuel_refining4': '9b230580ef7aeabf3606c2ec65b0990df0e18c1e58f8a07d61db225b39067045',
 'fuel_refining5': '4400166debe9d5f023c73da70e44161c78dc48194b4feef143df38408c5e8025',
 'improved_oil_plant': '6c0d0bd1255f4787c336864eba45e269f645c0d2ed510ae3ebe233fd9fb63f41',
 'advanced_oil_plant': '2336ef84837858e9f0ce0feaee9206cab08daa888c84340001664873465ac872',
 'advanced_oil_plant_2': 'a62d26a899493e59257982ad2804a3582c6404667d173425691217d83ed760a9',
 'advanced_oil_plant_3': 'b0c722ac43dfd277b0f2db39bef7bd120a7b65ee68ed51ea79686a36bfd73d86',
 'improved_rubber_plant': '11f00f236a71434c2c0133bf8a3384fc05b97ad115a8d7a3d4873d4f245ee310',
 'advanced_rubber_plant': '353b8305619d55b7c997bd7cdbe86d3040914ee9a3d2048103f3c4865afa4f5d',
 'advanced_rubber_plant_2': 'c8094d4b556fbfccabb9c931d122aae32a3cf35fdb57481e01c7e7ec0f61c586',
 'advanced_rubber_plant_3': 'a922f8190b3e8792351ec00a66a5e6e9dc4d41472f47f81aa34f6da3d3833190',
 'construction10': '1257366ee3521b0becdccbf5b91ad2ed9ff04ac826aa447e217d5491d4208f93',
 'excavation4': '15aefb2d44a86c4e82b3533f10a8c887c598ad0ed68f7f9b8a628187d97db978',
 'construction11': '28a4d7ed60454171157e2bd3088f4b1db836ce0483193c47951c87668490fa9b',
 'excavation5': 'e1856a96ca0b9616e2f171abbf5ceeb44d7e11fe407fb2219cc32fdf2aebd726',
 'construction_a': 'f3c1b232cef15c29dedccb3433f12c75a4caa4ae3ee7481d2f49bea154287346',
 'excavation_a': '2caa34aba2666a64e98580b7e73367a00201ebdf96f95e9862473fa6768830c1',
 'construction_b': 'e0f4cd2aa27ae931f863a73b7088d4046365fdff0411a98efaba31c0f3c6799d',
 'excavation_b': '416bc6b43018410aaa6e5c708f8eae60c9ea5b0ef4d8cb66368bb033a344a440',
 'construction_c': '44fac47eaa7824f373f5652f46b5431752c85b00897cd4861f61945ea5398743',
 'excavation_c': '44c9f98415307e2f39457655502d95c22f9bb92bd0deaac2758660b69f0bd641',
 'construction_d': 'd59c5ab6966e698506a752a212410286401b4780c4eef18c562abfa49cbcb922',
 'excavation_d': 'b059337ed3d49bd1f6836d05fe90f94f2b12e535bc5449a978b50f80f4245c9b'}
TRENCH = {'trench_warfare': '14d816dbb4db17f611d13b3255cb0469f396f43374d88a460f405f53c75a6929',
 'wood_flooring': 'c0000961fe753a1481b4b6d0c51db5269a228d313e5b2f23a2f2aa3b90aadab3',
 'better_trench_conditions': '5e51b203eb15b62d4937e1d890c1b8a7f46ef35d4543907de0acc201ab7f0658'}
def check(ok,label):
 global checks
 checks+=1
 if not ok:raise AssertionError(label)

def nodes(p):return u.read(p)[2]
def tree(p):return {n.key:n for n in nodes(p)[0].children}
after=tree(R/'common/technologies/industry.txt');native=tree(V/'common/technologies/industry.txt')
check(list(PROTECTED)==list(after),'technology IDs/order preserved')
watched=set(cfg['watched']);stat_changes=cfg['stat_changes']
for k,n in after.items():
 new=deepcopy(n)
 new.value=[x for x in new.children if x.key not in stat_changes.get(k,{})]
 if k in watched:
  callbacks=[x for x in new.children if x.key=='on_research_complete']
  check(len(callbacks)==1,k+' single callback')
  cb=callbacks[0]
  added=[x for x in cb.children if x.key=='hidden_effect' and any(z.key=='endsieg_industry_reconcile' for z in x.children)]
  check(len(added)==1,k+' exact added callback')
  cb.value=[x for x in cb.children if x not in added]
  if not cb.children:new.value.remove(cb)
 check(hashast(new)==PROTECTED[k],k+' protected AST: other gameplay/layout fields')
for k,h in TRENCH.items():check(hashast(after[k])==h,k+' authorized single-level trench technology, rewards and layout preserved')
for k,h in LATE.items():
 new=deepcopy(after[k]);new.value=[x for x in new.children if x.key!='on_research_complete']
 check(hashast(new)==h,k+'1940+ exact rewards unchanged')
for k,changes in stat_changes.items():
 for st,val in changes.items():
  actual=u.scalar(after[k],st)
  check(actual is None if val is None else abs(float(actual)-val)<1e-9,k+' planned scalar '+st)
# Temporary industrial capacity is cancelled by the demobilization technology.
for stat in ('global_building_slots_factor', 'production_factory_max_efficiency_factor'):
 total = sum(float(u.scalar(after[k],stat) or 0) for k in ('total_war1','total_war2','total_war3','demobilization2'))
 check(abs(total)<1e-9,stat+' wartime bonus fully removed on demobilization')
# Execute the actual installed restricted DSL, rather than reproducing its conditional text.
def pred(n,state):
 if n.key in ['limit','AND']:return all(pred(x,state) for x in n.children)
 if n.key=='OR':return any(pred(x,state) for x in n.children)
 if n.key=='NOT':return not all(pred(x,state) for x in n.children)
 if n.key=='always':return n.value=='yes'
 if n.key=='has_tech':return n.value in state['techs']
 if n.key=='has_start_date':
  a=state['start'];b=tuple(map(int,str(n.value).strip('"').split('.')))
  return {'>':a>b,'<':a<b,'=':a==b,'>=':a>=b,'<=':a<=b}[n.op]
 if n.key=='has_country_flag':return n.value in state['flags']
 if n.key=='has_dynamic_modifier':return n.value in state['modifiers']
 raise AssertionError('unmodeled trigger '+n.key)
def execute(ns,state):
 for n in ns:
  if n.key in ['set_variable','add_to_variable']:
   x=n.children[0];val=float(x.value)
   state['variables'][x.key]=val+(state['variables'].get(x.key,0) if n.key=='add_to_variable' else 0)
  elif n.key=='if':
   if pred(u.child(n,'limit'),state):execute([x for x in n.children if x.key!='limit'],state)
  elif n.key=='add_dynamic_modifier':state['modifiers'].add(u.scalar(n,'modifier'))
  elif n.key=='set_country_flag':state['flags'].add(n.value)
  elif n.key=='endsieg_industry_reconcile':execute(helper.children,state)
  elif n.key=='hidden_effect':execute(n.children,state)
  else:raise AssertionError('unmodeled effect '+n.key)
def state(ts=(),start=(1910,1,1)):
 return {'techs':set(ts),'start':start,'variables':{},'flags':set(),'modifiers':set()}
helper=nodes(R/'common/scripted_effects/endsieg_industry_progression.txt')[0]
check(helper.key=='endsieg_industry_reconcile','helper resolved')
# Group-independent exhaustive tests cover every incomplete/out-of-order source stack,
# all possible mature endpoints, modern starts, no early-tech reward exploits and monotonic progress.
helpernodes=helper.children
scenario_count=0
for i,g in enumerate(groups):
 group_nodes=helpernodes[i*2:i*2+2];src=list(g['sources']);st=g['stat'];v=g['variable']
 check(group_nodes[0].key=='set_variable' and group_nodes[1].key=='if',st+' modeled AST split')
 for bits in range(1<<len(src)):
  subset={src[j] for j in range(len(src)) if bits>>j&1}
  for start in [(1910,1,1),(1936,1,1),(1939,8,14)]:
   for endpoint in [None]+g['mature']:
    ts=subset|({endpoint} if endpoint else set());s=state(ts,start)
    execute(group_nodes,s);scenario_count+=1
    mature=start>=(1936,1,1) or bool(set(g['mature'])&ts)
    recovery=sum(vv for t,vv in g['sources'].items() if t in ts)
    expected=-recovery if mature else g['base']
    check(math.isclose(s['variables'][v],expected,abs_tol=1e-9),st+' exact offset subset/start/endpoint')
    total=s['variables'][v]+sum(float(u.scalar(after[t],st) or 0) for t in ts)
    native_total=sum(float(u.scalar(after[t],st) or 0)-g['sources'].get(t,0) for t in ts)
    check(math.isclose(total,native_total if mature else native_total+recovery+g['base'],abs_tol=1e-9),st+' no double benefit or missing-predecessor penalty')
    # Existing-variable corruption and reloads cannot compound bonuses.
    s['variables'][v]=99;execute(group_nodes,s)
    check(math.isclose(s['variables'][v],expected,abs_tol=1e-9),st+' reconcile resets old variables')
 # Every nonendpoint source researched improves early-campaign results and never lowers modern results.
 for bits in range(1<<len(src)):
  ts={src[j] for j in range(len(src)) if bits>>j&1}
  for t in src:
   if t in ts:continue
   for start in [(1910,1,1),(1936,1,1)]:
    a=state(ts,start);b=state(ts|{t},start);execute(group_nodes,a);execute(group_nodes,b)
    av=a['variables'][v]+sum(float(u.scalar(after[x],st) or 0) for x in ts)
    bv=b['variables'][v]+sum(float(u.scalar(after[x],st) or 0) for x in ts|{t})
    check(bv+1e-9>=av,st+' research cannot reduce statistic')
# Full-chain comparisons to the exact native1936,1937,1939 tech payloads.
allpre=set().union(*(set(g['sources']) for g in groups)) - {'concentrated_industry','dispersed_industry'}
for branch in ['concentrated_industry','dispersed_industry']:
 for level,extra in [(0,[]),(1,['improved_machine_tools','construction8','excavation2',branch+'2']),(2,['improved_machine_tools','construction8','excavation2',branch+'2','advanced_machine_tools','construction9','excavation3',branch+'3'])]:
  ts=allpre|{branch,'excavation1'}|set(extra);s=state(ts);execute(helper.children,s)
  nv=['basic_machine_tools',branch,'construction1','excavation1']
  if level>=1:nv+=['improved_machine_tools',branch+'2','construction2','excavation2']
  if level>=2:nv+=['advanced_machine_tools',branch+'3','construction3','excavation3']
  # Nonrecovery native values include building slots, retention, base efficiency and conversion.
  stats={g['stat'] for g in groups}|{'global_building_slots_factor','industry_repair_factor','equipment_conversion_speed','local_resources_coal_factor','line_change_production_efficiency_factor','production_factory_start_efficiency_factor','industry_air_damage_factor'}
  for st in stats:
   val=sum(float(u.scalar(after[x],st) or 0) for x in ts)
   g=next((g for g in groups if g['stat']==st),None)
   if g:val+=s['variables'][g['variable']]
   want=sum(float(u.scalar(native[x],st) or 0) for x in nv)
   check(math.isclose(val,want,abs_tol=1e-9),f'{branch} level{level} native parity {st}: {val} != {want}')
# Direct1936 baseline remains neutral even when no early technologies were granted.
for start in [(1910,1,1),(1914,8,14),(1936,1,1),(1939,8,14),(1944,6,6)]:
 for ts in [set(),allpre,{'basic_machine_tools','concentrated_industry','construction7','excavation1'},{'early_machine_tools','construction1','construction6'},{'advanced_machine_tools','concentrated_industry3','construction9','excavation3'}]:
  s=state(ts,start);execute(helper.children,s);old=deepcopy(s);execute(helper.children,s)
  check(s==old,'full helper idempotence')
  check(s['flags']=={'endsieg_industry_progression_v1'} and s['modifiers']=={'endsieg_industry_development'},'exact receipt and one consolidated modifier')
# Old-save/released-country once-only monthly path and actual on-startup form.
oa=nodes(R/'common/on_actions/endsieg_industry_progression.txt')[0]
monthly=u.child(u.child(oa,'on_monthly'),'effect')
for start in [(1910,1,1),(1936,1,1),(1939,8,14)]:
 for existing_flag,existing_mod in [(False,False),(True,False),(False,True),(True,True)]:
  s=state({'early_machine_tools','construction1'},start)
  if existing_flag:s['flags'].add('endsieg_industry_progression_v1')
  if existing_mod:s['modifiers'].add('endsieg_industry_development')
  execute(monthly.children,s)
  check(bool(s['variables'])==(not existing_flag or not existing_mod),'monthly migration only if missing receipt/modifier')
  before_second=deepcopy(s);execute(monthly.children,s)
  check(s==before_second,'second monthly is a no-op')
startup=u.child(u.child(oa,'on_startup'),'effect')
check(len(startup.children)==1 and startup.children[0].key=='every_country','startup initializes country scopes')
# No calendar-controlled stat reset, free research, recurring bonus or unsupported UI keyword.
NEWFILES=['common/scripted_effects/endsieg_industry_progression.txt','common/dynamic_modifiers/endsieg_industry_progression.txt','common/on_actions/endsieg_industry_progression.txt']
newtxt='\n'.join((R/x).read_text(encoding='utf-8-sig') for x in NEWFILES)
check(not re.search(r'(?m)^\s*date\s*[<>=]',newtxt),'no calendar stat reset')
check(not re.search(r'\b(set_technology|add_ideas|add_timed_idea|add_tech_bonus|on_daily)\s*=',newtxt),'no free research/idea/daily scan')
dmod=nodes(R/'common/dynamic_modifiers/endsieg_industry_progression.txt')[0]
check({x.key for x in dmod.children}=={'enable'}|{g['stat'] for g in groups},'only native dynamic keys; no GUI icon or invented hidden keyword')
loc=R/'localisation/replace/english/endsieg_industry_progression_l_english.yml'
check(loc.read_bytes().startswith(b'\xef\xbb\xbf'),'new English localization BOM')
locs=dict(re.findall(r'(?m)^\s*([^#\s:]+):\d*\s+"([^\r\n]*)"',loc.read_text(encoding='utf-8-sig')))
check(set(locs)=={'endsieg_industry_development','endsieg_industry_development_desc'},'modifier localization resolves')
# Output a concise progression table as additive modifier points, excluding national spirits/laws.
order=[('1910',set()),('1912',{'early_machine_tools','construction1'}),('1914',{'early_machine_tools','improved_early_machine_tools','construction1','construction2','total_war1'}),('1916',{'early_machine_tools','improved_early_machine_tools','advanced_early_machine_tools','construction1','construction2','construction3','total_war1','total_war2'}),('1920',set(cfg['groups'][0]['sources'])-{'basic_machine_tools'}|{'construction1','construction2','construction3','construction4','constructiondemob','total_war1','total_war2','total_war3','demobilization2'}),('1930',allpre-{'basic_machine_tools','construction7'}),('1934 concentrated',allpre|{'concentrated_industry','excavation1'}),('1934 dispersed',allpre|{'dispersed_industry','excavation1'})]
table=[]
for label,ts in order:
 s=state(ts);execute(helper.children,s)
 row={'stage':label}
 for g in groups:row[g['stat']]=round(s['variables'][g['variable']]+sum(float(u.scalar(after[x],g['stat']) or 0) for x in ts),8)
 table.append(row)
report={'result':'PASS','checks':checks,'exhaustive_partial_history_scenarios':scenario_count,'technologies_preserved':len(PROTECTED),'research_callbacks':len(watched),'mod_files':6,'validator_files':1,'progression':table,'limitation':'Static source/DSL validation only; no HOI4 launch. Existing saves initialize on their next country monthly tick if startup does not run. Country-specific laws/spirits and factory counts are unchanged.1940+ technology payloads remain Endsieg values.'}
if args.report:write_json(args.report,report)
print(json.dumps(report,indent=2))
