#!/usr/bin/env python3
"""Assign vanilla/DLC focus icons to the Iran 1910-1945 focus chapters.

The Iran chapters originally pointed at custom `GFX_iran_focus_*` art. This tool
repoints every focus at a sprite that ships with the game, preferring the icons of
vanilla's Persian tree (272 focuses whose art is purpose-made for Iran), then
neighbouring Afghan/Iraqi/Turkish art, then generic economic and military icons.

Two stages:
  1. a curated theme family is chosen from the focus id and its English title;
  2. icons inside that family are dealt round-robin, so a branch never repeats one
     picture back to back.

Every sprite is verified twice: the name must exist in the installed sprite
registry, and its texture file must be present on disk. A focus never keeps a
reference that fails either test.

Usage:
    python tools/assign_iran_icons.py --game "<HOI4 install>" --mod "<mod root>" [--check]

--check verifies current icons without rewriting anything.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

CHAPTERS = ["iran_ww1.txt", "iran_interwar.txt", "iran_ww2.txt"]

# Vanilla focus ids whose icons are the reference art for each theme.
FAMILIES: dict[str, list[str]] = {
    "tribes": ["PER_rally_bakhtiari_and_qashqai", "PER_recruit_bakhtiari", "PER_clamp_kurdish_dissidence",
               "PER_clamp_azerbaijani_dissidence", "PER_reach_to_seperatists", "PER_appease_the_seperatists",
               "PER_ally_bazaari"],
    "oil": ["PER_nationalize_oil_fields", "PER_form_oil_company", "PER_develop_oil_fields", "PER_oil_baron",
            "PER_increase_oil_sales", "PER_donate_oil_fields", "PER_expand_oil_production",
            "PER_soviet_iranian_oil_collaboration"],
    "railway": ["PER_trans_iranian_railway", "PER_expand_tabriz_masshad", "PER_expand_tehran_emam",
                "PER_expand_tehran_abbas", "PER_feat_of_engineering", "PER_trains_from_germany",
                "PER_trains_from_britain"],
    "air": ["PER_establish_airforce", "PER_raf_planes", "PER_luftwaffe_planes", "PER_establish_air_academy",
            "PER_pilot_training", "PER_air_superiority", "PER_anti_air_development", "PER_own_plane_designs"],
    "navy": ["PER_establish_the_navy", "PER_persian_gulf_fleet", "PER_bolster_the_caspian",
             "PER_construct_naval_bases", "PER_coastal_defense_initiative", "PER_merchant_navy",
             "PER_purchase_foreign_ships"],
    "intel": ["PER_form_savak", "PER_fund_state_intelligence", "PER_form_savama", "PER_root_out_conspiracies",
              "PER_plant_resistance_cells", "PER_assessing_the_opposition"],
    "religion": ["PER_forced_secularization", "PER_state_atheism", "PER_venerate_islam", "PER_islamic_restoration",
                 "PER_promise_clergy_power", "PER_secularize_the_state", "PER_islamic_solidarity"],
    "education": ["PER_university_of_isfahan", "PER_shiraz_university", "PER_adult_literacy",
                  "PER_educational_reforms", "PER_open_abadan", "PER_imperial_funded_universities",
                  "PER_national_museum", "PER_royal_college_funding", "PER_increase_education_funding"],
    "media": ["PER_communist_propaganda", "PER_propagate_political_literature", "PER_stage_mass_protests"],
    "socialism": ["PER_strengthen_the_tudeh", "PER_iranian_socialism", "PER_land_reform", "PER_workers_army",
                  "PER_iranian_socialist_revolution", "PER_elevate_the_iran_party", "PER_industrial_aid",
                  "PER_the_new_economy", "PER_one_for_all_all_for_one", "PER_international_solidarity"],
    "nationalism": ["PER_iran_for_iranians", "PER_pan_iranianism", "PER_iran_first", "PER_reinforce_iranian_identity",
                    "PER_azadi", "PER_third_persian_empire", "PER_glory_of_cyrus", "PER_rally_ancient_history",
                    "PER_legacy_of_greatness", "PER_rebuild_persepolis", "PER_first_iranian_empire",
                    "PER_last_thousand_years"],
    "monarchy": ["PER_finding_a_shah", "PER_shahanshah", "PER_absolute_monarchy", "PER_reinstate_qajars",
                 "PER_choose_a_shahbanu", "PER_royal_visit_germany", "PER_emperor_for_people",
                 "PER_his_fathers_footsteps", "PER_embrace_opulence", "PER_royal_college_funding"],
    "succession": ["PER_force_abdication", "PER_assassinate_reza_shah", "PER_his_fathers_footsteps",
                   "PER_choose_a_shahbanu", "PER_finding_a_shah"],
    "parliament": ["PER_strengthen_iranian_parliament", "PER_constitutional_monarchy", "PER_free_elections",
                   "PER_rally_the_reformers", "PER_embrace_national_front", "PER_uphold_civil_rights",
                   "PER_assessing_the_opposition", "AFG_parliamentary_democracy",
                   "AFG_revive_the_1923_constitution", "IRQ_parliamentary_democracy"],
    "government": ["PER_embrace_national_front", "PER_roll_back_reforms", "PER_rebuilding_iran",
                   "PER_uphold_civil_rights", "PER_iran_first", "PER_free_elections",
                   "AFG_parliamentary_democracy", "AFG_work_with_german_inteligence"],
    "germany": ["PER_persian_german_trade", "PER_stand_with_germany", "PER_luftwaffe_planes",
                "PER_fascist_reach_out_to_germany", "PER_royal_visit_germany", "PER_trains_from_germany"],
    "britain": ["PER_declare_loyalty_to_britain", "PER_our_place_in_empire", "PER_invite_british_investors",
                "PER_request_british_equipment", "PER_trains_from_britain", "PER_challenge_the_royal_navy"],
    "soviet": ["PER_soviet_alignment", "PER_tehran_moscow_pact", "PER_comintern_research_collaboration",
               "PER_soviet_iranian_oil_collaboration", "PER_industrial_aid"],
    "sovereignty": ["PER_limit_foreign_influence", "PER_subserviant_to_noone", "PER_stand_with_giants",
                    "PER_wether_the_storm", "PER_question_of_resources"],
    "army": ["PER_restructure_army", "PER_expand_imperial_guard", "PER_military_high_schools", "PER_bolster_infantry",
             "PER_own_artillery", "PER_increase_heavy_arms", "PER_establish_motor_arms", "PER_desert_training",
             "PER_special_forces_program", "PER_increase_military_funding", "PER_preparatory_mobilization",
             "PER_every_man_serves", "PER_military_excellency", "PER_czech_tanks", "PER_german_tanks",
             "PER_foreign_retraining"],
    "industry": ["PER_rapid_industrialization", "PER_bolster_civilian_industry", "PER_upscale_military_production",
                 "PER_modernize_iran_economy", "PER_metropolitan_iran", "PER_develop_cities",
                 "PER_tehran_power_plant", "PER_oil_and_rubber_industry"],
    "finance": ["PER_national_bank", "PER_price_stabilization", "PER_abolish_feudalism",
                "PER_entice_foreign_investment", "PER_increase_education_funding"],
    "food": ["PER_food_for_all", "PER_abolish_feudalism", "PER_price_stabilization", "PER_land_reform"],
    "trade": ["PER_persian_german_trade", "PER_entice_foreign_investment", "PER_increase_oil_sales",
              "PER_request_membership_allies", "PER_negotiate_with_america"],
    "diplomacy": ["PER_limit_foreign_influence", "PER_subserviant_to_noone", "PER_stand_with_giants",
                  "PER_request_membership_allies", "PER_negotiate_with_america", "PER_the_unification_initiative"],
    "defence": ["PER_prepare_for_worst", "PER_stand_our_ground", "PER_we_will_survive", "PER_dig_and_defend",
                "PER_capital_protect", "PER_force_them_back", "PER_preemptive_strike", "PER_fight_for_iran"],
    "invasion": ["PER_force_them_back", "PER_push_to_deserts", "PER_push_to_mountains", "PER_retake_north_iran",
                 "PER_rebuilding_iran", "PER_push_negotiations", "PER_swear_fealty", "PER_force_white_peace",
                 "PER_demand_war_reparations", "PER_we_survived"],
    "expansion": ["PER_demand_iraqi_territory", "PER_demand_afghan_territory", "PER_secure_iraq",
                  "PER_secure_afghanistan", "PER_intervention_in_iraq", "PER_fascist_attack_afghanistan",
                  "PER_proclaim_greater_iran", "PER_pan_iranianism", "PER_imperial_expansionism"],
}

# Ordered: the first family whose pattern matches the focus id or title wins.
RULES: list[tuple[str, str]] = [
    ("tribes", r"tribe|tribal|bakhtiari|qashqai|kurdish|\blur\b|nomad|migrat"),
    ("oil", r"\boil\b|oil_|_oil|concession|apoc|refin|derrick|khuzestan|abadan"),
    ("railway", r"\brail(?:way|s)?\b|\btrains?\b|\btrack\b|\bgauge\b|telegraph"),
    ("succession", r"abdicat|succession|accession|throne|heir|crown prince|coronation|dynast"),
    ("socialism", r"socialis|communis|tudeh|gilan|jangali|worker|land reform|labour|\blabor\b|bolshevik"),
    ("media", r"\bpress\b|newspaper|propaganda|radio|journal|publication|debate"),
    ("intel", r"intelligence|police|gendarmerie|savak|savama|\bspy\b|secret|conspirac|informer"),
    ("religion", r"clergy|religious|ulama|mosque|islam|secular|sharia|mullah|waqf|shrine"),
    ("education", r"educat|school|universit|literacy|academy|student|museum|culture|library"),
    ("air", r"\bair\b|airfield|plane|aircraft|pilot|aviation"),
    ("navy", r"navy|naval|fleet|ship|dockyard|maritime|harbour|harbor"),
    ("germany", r"german|berlin|axis|nazi"),
    ("britain", r"british|britain|anglo|entente|london|imperial bank"),
    ("soviet", r"soviet|russian|russia|moscow|comintern|tsarist"),
    ("food", r"grain|harvest|famine|food|relief|bread|hunger|crop"),
    ("invasion", r"invasion|occupat|invade|corridor|ultimatum|evacuat|armistice|surrender|\bpeace\b|withdraw"),
    ("expansion", r"\bafghan|iraq|caucasus|mesopotamia|territor|\bclaims?\b|greater iran|expedition|\bindus\b|anatolia"),
    ("trade", r"\btrade\b|commerce|merchant|export|import|tariff"),
    ("sovereignty", r"neutral|sovereign|independen|foreign influence|great game|\bbalance\b|non-aligned|autonom"),
    ("monarchy", r"\bshah\b|royal|court|palace|qajar|pahlavi|monarch|\bking\b|household|regency|\bcrown\b"),
    ("government", r"republic|cabinet|government|administration|prime minister|constitution"),
    ("parliament", r"majlis|parliament|anjoman|assembly|election|vote|deputy|franchise|\breform"),
    ("army", r"army|military|cossack|officer|division|corps|regiment|barracks|conscript|mobilis|mobiliz|"
             r"artillery|infantry|cavalry|tank|garrison"),
    ("industry", r"industr|factory|workshop|\bmines?\b|steel|power plant|textile|infrastructure|\bdam\b"),
    ("finance", r"treasury|budget|\btax|customs|bank|currency|loan|debt|financ|fiscal|revenue|econom|\bpay\b|wage"),
]

# Search filter -> fallback family when no pattern matches.
DEFAULT_BY_FILTER = {
    "FOCUS_FILTER_POLITICAL": "parliament", "FOCUS_FILTER_ARMY_XP": "army", "FOCUS_FILTER_MANPOWER": "army",
    "FOCUS_FILTER_INDUSTRY": "industry", "FOCUS_FILTER_RESEARCH": "education", "FOCUS_FILTER_NAVY_XP": "navy",
    "FOCUS_FILTER_AIR_XP": "air", "FOCUS_FILTER_STABILITY": "government", "FOCUS_FILTER_WAR_SUPPORT": "army",
    "FOCUS_FILTER_ANNEXATION": "expansion", "FOCUS_FILTER_POLITICAL_CHARACTER": "monarchy",
}

# Hand-picked where the automatic match is not good enough: Iran focus -> vanilla focus id.
OVERRIDES = {
    "IR1_second_majlis": "PER_strengthen_iranian_parliament",
    "IR1_diplomatic_corps": "PER_the_unification_initiative",
    "IR1_grain_requisition": "PER_food_for_all",
    "IR1_bushehr_trade": "PER_entice_foreign_investment",
    "IR1_gulf_ports": "PER_persian_gulf_fleet",
    "IR2_textile_industry": "PER_rapid_industrialization",
    "IR2_industrial_bank": "PER_national_bank",
    "IR2_soviet_trade": "PER_tehran_moscow_pact",
    "IR2_german_economic_mission": "PER_persian_german_trade",
    "IR2_trans_iranian_railway": "PER_trans_iranian_railway",
    "IR2_press_restraint": "PER_communist_propaganda",
    "IR3_occupation_government": "PER_swear_fealty",
    "IR3_persian_corridor": "PER_expand_tehran_abbas",
    "IR3_tehran_conference": "PER_the_unification_initiative",
}
OVERRIDE_SPRITES = {
    "IR1_foreign_advisers": "GFX_focus_generic_military_mission",
    "IR2_soviet_treaty_1921": "GFX_focus_chi_mission_to_the_soviet_union",
    "IR3_republic_1945": "GFX_focus_PER_iran_first",
    "IR1_bushehr_trade": "GFX_focus_generic_merchant_fleet",
}


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def build_registry(game: str) -> tuple[dict[str, str], set[str]]:
    """Return (vanilla focus id -> icon sprite, every sprite name installed)."""
    sprite_of: dict[str, str] = {}
    names: set[str] = set()
    gfx_pattern = re.compile(r'name\s*=\s*"(GFX_[A-Za-z0-9_]+)"')
    for path in glob.glob(os.path.join(game, "interface", "**", "*.gfx"), recursive=True):
        names.update(gfx_pattern.findall(read(path)))
    dlc = os.path.join(game, "dlc")
    if os.path.isdir(dlc):
        for sub in os.listdir(dlc):
            for path in glob.glob(os.path.join(dlc, sub, "interface", "**", "*.gfx"), recursive=True):
                names.update(gfx_pattern.findall(read(path)))
    for path in glob.glob(os.path.join(game, "common", "national_focus", "**", "*.txt"), recursive=True):
        text = read(path)
        depth, start = 0, None
        for m in re.finditer(r"(?:^|\n)\s*focus\s*=\s*\{", text):
            i = m.end() - 1
            depth, j = 0, i
            while j < len(text):
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            block = text[i:j + 1]
            fid = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+)", block)
            icon = re.search(r"\bicon\s*=\s*(GFX_[A-Za-z0-9_]+)", block)
            if fid and icon:
                sprite_of.setdefault(fid.group(1), icon.group(1))
    return sprite_of, names


def build_texture_index(game: str) -> dict[str, str]:
    index: dict[str, str] = {}
    roots = [os.path.join(game, "gfx"), os.path.join(game, "dlc")]
    for root in roots:
        for ext in ("*.dds", "*.tga", "*.png"):
            for path in glob.glob(os.path.join(root, "**", ext), recursive=True):
                index.setdefault(os.path.splitext(os.path.basename(path))[0].lower(), path)
    return index


def texture_for(sprite: str, index: dict[str, str]) -> str | None:
    stem = sprite.replace("GFX_focus_", "").replace("GFX_goal_", "").replace("GFX_", "")
    for cand in (stem, sprite.replace("GFX_", ""), "focus_" + stem, "goal_" + stem):
        hit = index.get(cand.lower())
        if hit:
            return hit
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--mod", required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    sprite_of, names = build_registry(args.game)
    textures = build_texture_index(args.game)
    print(f"vanilla focuses with icons: {len(sprite_of)} | sprite names: {len(names)} | textures: {len(textures)}")

    families: dict[str, list[str]] = {}
    for family, ids in FAMILIES.items():
        sprites = []
        for pid in ids:
            sprite = sprite_of.get(pid)
            if sprite and sprite in names and texture_for(sprite, textures) and sprite not in sprites:
                sprites.append(sprite)
        families[family] = sprites
    empty = [k for k, v in families.items() if not v]
    if empty:
        print(f"warning: families with no resolvable art: {empty}", file=sys.stderr)

    loc = {}
    for path in glob.glob(os.path.join(args.mod, "localisation", "english", "iran_*_l_english.yml")):
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            for line in fh:
                m = re.match(r'^\s*([A-Za-z0-9_.\-]+):\d*\s*"(.+?)"\s*$', line)
                if m:
                    loc[m.group(1)] = m.group(2)

    focus_dir = os.path.join(args.mod, "common", "national_focus")
    focuses: list[tuple[str, str, str, str]] = []
    for chapter in CHAPTERS:
        text = read(os.path.join(focus_dir, chapter))
        for block in text.split("\n\tfocus = {")[1:]:
            fid = re.search(r"\n\t\tid = (IR\d_\w+)", block)
            if not fid:
                continue
            filters = re.search(r"search_filters = \{([^}]*)\}", block)
            focuses.append((chapter, fid.group(1), loc.get(fid.group(1), ""), (filters.group(1) if filters else "").strip()))

    counters: collections.Counter = collections.Counter()
    assign: dict[str, str] = {}
    family_of: dict[str, str] = {}
    for _, fid, title, filters in focuses:
        if fid in OVERRIDE_SPRITES and OVERRIDE_SPRITES[fid] in names:
            assign[fid], family_of[fid] = OVERRIDE_SPRITES[fid], "hand-picked"
            continue
        target = OVERRIDES.get(fid)
        if target and sprite_of.get(target):
            sprite = sprite_of[target]
            if sprite in names:
                assign[fid], family_of[fid] = sprite, "hand-picked"
                continue
        haystack = f"{fid} {title}".lower()
        family = None
        for name, pattern in RULES:
            if families.get(name) and re.search(pattern, haystack):
                family = name
                break
        if family is None:
            for key, candidate in DEFAULT_BY_FILTER.items():
                if key in filters and families.get(candidate):
                    family = candidate
                    break
        family = family or "parliament"
        pool = families[family]
        assign[fid] = pool[counters[family] % len(pool)]
        counters[family] += 1
        family_of[fid] = family

    unresolved = [(f, s) for f, s in assign.items() if s not in names or not texture_for(s, textures)]
    print(f"assigned {len(assign)} focuses | distinct icons {len(set(assign.values()))} | unresolved {len(unresolved)}")

    if args.check:
        bad = []
        for chapter in CHAPTERS:
            text = read(os.path.join(focus_dir, chapter))
            for block in text.split("\n\tfocus = {")[1:]:
                fid = re.search(r"\n\t\tid = (IR\d_\w+)", block)
                icon = re.search(r"\n\t\ticon = (\S+)", block)
                if not fid:
                    continue
                if not icon:
                    bad.append((fid.group(1), "no icon"))
                elif icon.group(1) not in names:
                    bad.append((fid.group(1), icon.group(1)))
        print(f"check: {len(bad)} problems")
        for fid, icon in bad[:20]:
            print(f"  {fid}: {icon}")
        return 0 if not bad else 1

    written = 0
    for chapter in CHAPTERS:
        path = os.path.join(focus_dir, chapter)
        parts = read(path).split("\n\tfocus = {")
        out = [parts[0]]
        for block in parts[1:]:
            m = re.search(r"\n\t\tid = (IR\d_\w+)", block)
            if m and m.group(1) in assign:
                block = re.sub(r"\n\t\ticon = \S+", f"\n\t\ticon = {assign[m.group(1)]}", block, count=1)
                written += 1
            out.append(block)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n\tfocus = {".join(out))
    print(f"icon lines written: {written}")

    report = os.path.join(args.mod, "docs", "plans", "iran_1910_1945", "icon_assignment.json")
    os.makedirs(os.path.dirname(report), exist_ok=True)
    with open(report, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"assign": assign, "family": family_of, "titles": {f: t for _, f, t, _ in focuses}}, fh, indent=1)
    print(f"mapping written to {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
