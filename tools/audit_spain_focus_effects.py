"""List focuses whose completion_reward does nothing.

A focus that only sets a flag nobody reads, or has no reward block at all, is text with no
mechanic behind it. This prints every such focus so they can be given a real effect.

    python tools/audit_spain_focus_effects.py
"""

from __future__ import annotations

import io
import re
import sys

TREES = [
    'common/national_focus/spain_restoration.txt',
    'common/national_focus/spain_rivera.txt',
    'common/national_focus/spain_republic.txt',
    'common/national_focus/spain_republic_postwar.txt',
]

# Effects that visibly change something for the player.
REAL = {
    'add_ideas', 'add_timed_idea', 'remove_ideas', 'add_stability', 'add_war_support',
    'add_political_power', 'add_manpower', 'add_equipment_to_stockpile', 'army_experience',
    'air_experience', 'navy_experience', 'add_research_slot', 'add_tech_bonus',
    'add_doctrine_cost_reduction', 'add_offensive_war_stability_modifier',
    'add_defensive_war_stability_modifier', 'set_politics', 'add_country_leader_trait',
    'remove_country_leader_trait', 'add_popularity', 'set_rule', 'add_relation_modifier',
    'create_faction', 'add_to_faction', 'puppet', 'annex_country', 'declare_war_on',
    'transfer_state', 'add_state_core', 'add_core_of', 'set_cosmetic_tag',
    'add_dynamic_modifier', 'remove_dynamic_modifier', 'set_variable', 'add_to_variable',
    'subtract_from_variable', 'multiply_variable', 'set_power_balance',
    'add_balance_of_power', 'unlock_decision_category_tooltip',
    'add_decision_category', 'add_named_threat', 'country_event', 'news_event',
    'add_mission_effect', 'add_ai_strategy', 'set_nationality', 'add_opinion_modifier',
    'add_command_power', 'add_fuel', 'add_political_power', 'hidden_effect',
    'complete_national_focus', 'load_focus_tree', 'add_building_construction',
    'add_extra_state_shared_building_slots', 'set_province_controller',
}


def bodies(text):
    for m in re.finditer(r'^\t*focus\s*=\s*\{', text, re.M):
        i = text.index('{', m.start())
        depth, j = 0, i
        while j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        yield text[i:j + 1]


def main() -> int:
    total = 0
    for path in TREES:
        text = io.open(path, encoding='utf-8-sig').read()
        empty = []
        for body in bodies(text):
            fid = re.search(r'\bid\s*=\s*(\S+)', body)
            if not fid:
                continue
            total += 1
            reward = re.search(r'completion_reward\s*=\s*\{(.*)', body, re.S)
            if not reward:
                empty.append((fid.group(1), 'no completion_reward'))
                continue
            chunk = reward.group(1)
            words = set(re.findall(r'\b([a-z_]+)\s*=', chunk))
            if not words & REAL:
                flags = re.findall(r'set_country_flag\s*=\s*(\S+)', chunk)
                empty.append((fid.group(1), 'flags only: ' + ','.join(flags) if flags else 'no real effect'))
        print('%s  %d focuses, %d with no real effect' % (path.split('/')[-1], len(list(bodies(text))), len(empty)))
        for fid, why in empty:
            print('    %-38s %s' % (fid, why))
    print('\ntotal focuses: %d' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
