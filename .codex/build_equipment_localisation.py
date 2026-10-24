from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from audit_equipment_localisation import inventory,locate_vanilla,value

equipment,text,missing=inventory(locate_vanilla())
names={
 'ww1_armored_car_6':'Early Armored Car VI',
 'superartillery_equipment':'Railway Artillery',
 'artillery_equipment_4':'Artillery IV',
 'bicycle_equipment':'Bicycles',
 'early_railway_gun_equipment':'Early Railway Artillery',
 'early_tank_chassis':'Great War Tank Chassis',
 'early_train_equipment':'Early Trains',
 'icbm_missile_equipment':'Intercontinental Ballistic Missiles',
 'ship_hull_cruiser_modern_aa':'Modern Anti-Air Cruiser Hull',
 'early_small_plane_airframe':'Great War Small Airframe',
 'early_ship_hull_cruiser':'Great War Cruiser Hull',
 'ww1_torpedo_cruiser':'Early Torpedo Cruiser',
 'ww1_ship_hull_torpedo_cruiser':'Early Torpedo Cruiser Hull',
 'ww1_ship_hull_cruiser_panzerschiff':'Early Armored Ship Hull',
 'ww1_ship_hull_cruiser_coastal_defense_ship':'Early Coastal Defense Hull',
 'early_ship_hull_heavy':'Great War Heavy Ship Hull',
 'ww1_ship_hull_pre_dreadnought':'Pre-Dreadnought Hull',
 'early_ship_hull_light':'Great War Destroyer Hull',
 'ww1_ship_hull_cruiser_submarine':'Early Cruiser Submarine Hull',
}
roman={1:'I',2:'II',3:'III',4:'IV'}
for family,name in (('ww1_light_cruiser','Great War Light Cruiser'),('ww1_heavy_cruiser','Armored Cruiser'),('ww1_battleship','Great War Battleship'),('ww1_destroyer','Great War Destroyer'),('ww1_submarine','Great War Submarine')):
 for i in range(1,5):names[f'{family}_{i}']=name+' '+roman[i]
for i in (1,2):names[f'ww1_battle_cruiser_{i}']='Great War Battlecruiser '+roman[i]
assert set(missing[''])<=names.keys(),set(missing[''])-names.keys()

descriptions={
 'ww1_anti_air':'Light guns adapted to engage aircraft, observation balloons and airships.',
 'anti_tank_equipment_0':'Early direct-fire guns firing armor-piercing ammunition against armored vehicles.',
 'ww1_armored_car':'Armored motor vehicles armed with machine guns provide reconnaissance and mobile fire support.',
 'superartillery_equipment':'Heavy guns carried on railway mountings provide long-range fire support but depend on rail access.',
 'early_railway_gun_equipment':'A heavy cannon mounted on a railway carriage for transport and long-range bombardment.',
 'ww1_artillery':'Field guns and howitzers provide indirect fire support to infantry and bombard enemy positions.',
 'artillery_equipment_4':'Improved field artillery combines effective ammunition, range and mobile gun carriages for sustained fire support.',
 'bicycle_equipment':'Military bicycles allow troops to move faster along roads without relying on motor vehicles.',
 'early_tank_chassis':'An early tracked armored chassis designed to cross trenches and provide close support to infantry.',
 'early_train_equipment':'Steam locomotives and railway wagons carry troops and supplies along the rail network.',
 'early_infantry_equipment':'Rifles, machine guns, ammunition and personal field equipment supplied to infantry formations.',
 'icbm_missile_equipment':'A long-range ballistic missile capable of carrying a strategic warhead across intercontinental distances.',
 'early_small_plane_airframe':'A lightweight early airframe for reconnaissance, fighter patrols and limited ground attack, using the aviation materials and engines of the Great War.',
 'ww1_small_plane_airframe':'A lightweight Great War airframe with improved structures and control surfaces for reconnaissance, fighter patrols and limited ground attack.',
 'ww1_medium_plane_airframe':'A larger Great War airframe with space for a crew, observation equipment and a bomb load.',
 'early_ship_hull_cruiser':'A Great War cruiser hull for scouting, fleet screening and service on distant stations.',
 'ww1_ship_hull_cruiser':'A cruiser hull balancing endurance, protection and weapons for scouting and supporting the fleet.',
 'ww1_light_cruiser':'A lightly armored Great War cruiser for reconnaissance, patrols and screening larger warships.',
 'ww1_heavy_cruiser':'An armored cruiser with heavier protection and guns for independent patrols and fleet support.',
 'ww1_torpedo_cruiser':'A cruiser carrying a concentrated torpedo armament for attacks against larger enemy warships.',
 'ww1_ship_hull_torpedo_cruiser':'A cruiser hull arranged around torpedo armament for attacks against larger enemy warships.',
 'ww1_ship_hull_cruiser_panzerschiff':'An early armored warship hull balancing heavy armament, protection and displacement.',
 'ww1_ship_hull_cruiser_coastal_defense_ship':'A compact armored warship hull intended to defend coastal waters rather than conduct long ocean voyages.',
 'early_ship_hull_heavy':'A heavily armored Great War capital-ship hull built to carry large guns and fight in the battle line.',
 'ww1_ship_hull_pre_dreadnought':'A pre-dreadnought capital-ship hull with heavy armor and a mixed battery of large and intermediate guns.',
 'ww1_ship_hull_heavy':'A dreadnought hull designed for heavy main guns, strong protection and service in the battle fleet.',
 'ww1_battleship':'A Great War capital ship armed with heavy guns and protected by armor for combat in the battle line.',
 'ww1_battle_cruiser':'A fast capital ship carrying battleship-scale guns with lighter protection to support scouting and pursuit.',
 'early_ship_hull_light':'An early destroyer hull for torpedo attacks, patrol work and screening larger warships.',
 'ww1_ship_hull_light':'A Great War destroyer hull with space for guns, torpedoes and machinery for fleet screening.',
 'ww1_destroyer':'A fast Great War escort armed with guns and torpedoes to screen the fleet and attack enemy shipping.',
 'early_ship_hull_submarine':'An early submarine hull for covert patrols and torpedo attacks against shipping.',
 'ww1_ship_hull_submarine':'A Great War submarine hull with batteries, engines and torpedo tubes for underwater patrols.',
 'ww1_ship_hull_cruiser_submarine':'A large early submarine hull with the endurance and accommodation required for distant patrols.',
 'ww1_submarine':'A Great War submarine using concealment and torpedoes to attack enemy shipping.',
 'ship_hull_cruiser_modern_aa':'A modern cruiser hull arranged to carry anti-aircraft weapons and protect a fleet from air attack.',
 'ship_hull_heavy_modern':'A modern capital-ship hull combining improved protection, machinery and heavy armament.',
 'modern_battleship':'A modern battleship combining heavy guns, improved protection and anti-aircraft defenses.',
 'repair_ship_hull':'A naval repair-ship hull with workshops and facilities for servicing friendly ships.',
 'support_ship_hull':'A naval support-ship hull carrying supplies and facilities for sustaining fleet operations.',
 'supersonic_fighter_equipment_1':'A jet-powered fighter designed for interception and air combat at supersonic speeds.',
}

def description(eid):
 if eid=='early_train_equipment_3': return 'An armored steam train equipped to protect railway lines and transport troops and supplies through contested territory.'
 if eid=='early_train_equipment_2': return 'A wartime steam locomotive and rolling stock designed to carry military supplies despite demanding conditions.'
 for prefix in sorted(descriptions,key=len,reverse=True):
  if eid==prefix or eid.startswith(prefix+'_'):return descriptions[prefix]
 parent=value(equipment[eid]['data'],'archetype')
 if parent and text.get(parent+'_desc','').strip():return '$'+parent+'_desc$'
 raise ValueError('Description needs review: '+eid)

new={}
for eid in missing['']:new[eid]=names[eid]
for eid in missing['_short']:
 if equipment[eid]['custom'] or eid in missing['']:new[eid+'_short']='$'+eid+'$'
for eid in missing['_desc']:
 if not text.get(eid+'_desc','').strip():new[eid+'_desc']=description(eid)

assert all(not text.get(k,'').strip() for k in new),'Refusing to replace existing text'
lines=['l_english:', ' # Missing generic equipment text; existing country-specific names retain precedence.']
for eid in sorted(equipment):
 keys=[eid+s for s in ('','_short','_desc') if eid+s in new]
 if keys:
  lines.append('')
  for k in keys:
   v=new[k].replace('"','\\"')
   lines.append(f' {k}:0 "{v}"')
dest=ROOT/'localisation/replace/english/endsieg_equipment_missing_l_english.yml'
dest.write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
print(f'Added {len(new)} equipment keys: {len(missing[""])} names, {sum(k.endswith("_short") for k in new)} short names, {sum(k.endswith("_desc") for k in new)} descriptions.')
