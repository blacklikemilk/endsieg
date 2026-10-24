"""Assign the shared German interwar icon families to ideas and decisions.

Focuses use separate bespoke sprites from package_interwar_german_focus_icons.py.
Run this script after changing idea or decision content. It only changes their
icon/picture fields.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "idea": [
        "common/ideas/INT - Germany.txt",
        "common/ideas/INT_German_Industry.txt",
        "common/ideas/INT_German_Paths.txt",
    ],
    "decision": [
        "common/decisions/INT_German_Industry.txt",
        "common/decisions/INT_German_Paths.txt",
    ],
    "category": [
        "common/decisions/categories/INT_German_Industry.txt",
        "common/decisions/categories/INT_German_Paths.txt",
    ],
}

SPECIAL = {
    "INT_GER_political_turmoil": "republic",
    "INT_GER_defeat_kapp_putsch": "republic",
    "INT_GER_safeguard_civil_rights": "republic",
    "INT_GER_reparations_crisis": "treaty",
    "INT_GER_reconstruction_commission": "public_works",
    "INT_GER_municipal_reconstruction": "public_works",
    "INT_GER_end_ruhr_resistance": "industry",
    "INT_GER_ruhr_resistance": "industry",
    "INT_GER_roaring_twenties": "twenties",
    "INT_GER_depression_response": "depression",
    "INT_GER_great_depression": "depression",
    "INT_GER_industry_credit_crash": "depression",
    "INT_GER_industry_credit_crash_buffered": "finance",
    "INT_GER_industry_austerity_burden": "depression",
    "INT_GER_industry_public_works_burden": "public_works",
    "INT_GER_industry_roaring_investment": "twenties",
    "INT_GER_industrial_safety": "welfare",
    "INT_GER_socialist_science": "science",
    "INT_GER_military_research_with_the_soviets": "military",
    "INT_GER_reichswehr_red_army_contacts": "military",
    "INT_GER_armored_trials_in_the_east": "military",
    "INT_GER_paths_workers_constitution": "councils",
    "INT_GER_workers_republic_constitution": "councils",
    "INT_GER_reichsbahn_reform": "public_works",
    "INT_GER_enter_1936": "republic",
    "INT_GER_paths_municipal_charters": "republic",
    "INT_GER_paths_treaty_legalists": "treaty",
    "INT_GER_eastern_path": "diplomacy",
    "INT_GER_paths_eastern_exercises": "military",
    "INT_GER_eastern_exercises": "military",
    "INT_GER_retain_the_republic": "republic",
    "INT_GER_dismantle_the_republic": "monarchy",
    "INT_GER_joint_industrial_surveys": "science",
    "INT_GER_industrial_recovery": "industry",
    "INT_GER_paths_constitutional_guard_spirit": "republic",
    "INT_GER_paths_constitutional_guard": "republic",
    "INT_GER_defend_constitution": "republic",
    "INT_GER_saar_plebiscite": "republic",
    "INT_GER_paths_republic_oversight": "republic",
    "INT_GER_paths_federal_compact": "republic",
    "INT_GER_federal_compromise": "republic",
    "INT_GER_state_of_the_nation": "republic",
    "INT_GER_recovery_program": "industry",
    "INT_GER_recover_from_depression": "industry",
    "INT_GER_republican_recovery": "industry",
}

# Order matters: distinctive subjects precede broad words such as "state".
RULES = [
    ("authoritarian", r"hitler|gleichschaltung|fascis|enabling_act|reichstag_fire|party_administration|labor_front|discriminat|purge|propaganda_apparatus"),
    ("monarchy", r"monarch|kaiser|princes|crown|royal|imperial_restoration|restored_court|old_elites|prussian_administration"),
    ("military", r"reichswehr|officer|rearmament|military|militia|armored|kama|armaments|arms_contract|aviation|pilot|lipetsk|exercises|clandestine_staff_training|red_training|eastern_training"),
    ("councils", r"communis|council|socialis|soviet|red_|peoples_republic|new_leaf|revolutionary|collectiviz|shop_floor|workers_|central_planning"),
    ("twenties", r"roaring|twenties"),
    ("depression", r"depression|austerity|retrench|crash|crisis|unrest|deadlock|violence"),
    ("press", r"broadcast|(?:^|_)press(?:_|$)|newspaper|propaganda"),
    ("science", r"science|research|technical|surveys|trial|intelligence|chemical|universit|education|retraining"),
    ("treaty", r"versailles|reparations|treaty_revision|repudiate|legal_revision|legal_advocacy|settlement|lausanne|london_reparations|hidden_procurement|secret_armaments|covert|clandestine|undermine"),
    ("diplomacy", r"locarno|league|security_accord|berlin_treaty|rapallo|foreign_policy|diplomatic|reconciliation|eastern_path"),
    ("trade", r"export|trade|commerce|grain|economic_relations"),
    ("finance", r"bank|capital|reserves|reserve|dawes|young_plan|credit|savings|moratorium|budget|currency|inflation|domestic_savings"),
    ("public_works", r"public_works|labor_service|reconstruction_projects|housing|rail|transport|reichsbahn|municipal_reconstruction"),
    ("welfare", r"insurance|welfare|social_compromise|social_partnership|industrial_safety|relief|assistance|food|veteran"),
    ("industry", r"industr|production|factory|machinery|electrification|mittelstand|contracts|planning|rebuild_economy|recovery_program|reconstruction|ruhr"),
    ("republic", r"constitution|parliament|reichstag|national_assembly|federal_chambers|legislative|election|elect_|plebiscite|administration|civil_service|commission|cabinet|bureaucrat|coordination|government_reform|federal|republic|democra|civic|coalition|political|state_elections|charters"),
]


def theme_for(content_id: str) -> str:
    if content_id in SPECIAL:
        return SPECIAL[content_id]
    for theme, pattern in RULES:
        if re.search(pattern, content_id, re.IGNORECASE):
            return theme
    raise ValueError(f"No icon theme assigned for {content_id}")


def wanted(kind: str, content_id: str) -> str:
    theme = theme_for(content_id)
    return ("GFX_goal_" if kind == "focus" else "") + f"INT_GER_{theme}"


def update_file(relative: str, kind: str) -> int:
    path = ROOT / relative
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    depth = 0
    current = None
    assigned = set()
    output = []
    record_depth = {"idea": 2, "decision": 1, "category": 0}[kind] if kind != "focus" else 1
    field = "picture" if kind == "idea" else "icon"
    for line in lines:
        code = line.split("#", 1)[0]
        if kind == "focus":
            if depth == 1 and re.match(r"\s*focus\s*=\s*\{", code):
                current = None
            if depth == 2:
                match = re.match(r"\s*id\s*=\s*(INT_GER_[A-Za-z0-9_]+)\b", code)
                if match:
                    current = match.group(1)
            target_depth = 2
        else:
            if depth == record_depth:
                match = re.match(r"\s*(INT_GER_[A-Za-z0-9_]+)\s*=\s*\{", code)
                if match:
                    current = match.group(1)
            target_depth = record_depth + 1
        if current and depth == target_depth:
            match = re.match(rf"(\s*{field}\s*=\s*)([^\s#]+)(.*)", line)
            if match:
                line = line[:match.start(2)] + wanted(kind, current) + line[match.end(2):]
                if current in assigned:
                    raise ValueError(f"Duplicate {field} for {current} in {relative}")
                assigned.add(current)
                current = None
        output.append(line)
        depth += code.count("{") - code.count("}")
        if depth < 0:
            raise ValueError(f"Unbalanced braces in {relative}")
    if depth != 0:
        raise ValueError(f"Unbalanced braces in {relative}: {depth}")
    if not assigned:
        raise ValueError(f"No {field} assignments in {relative}")
    changed = "".join(output).encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + changed)
    print(f"{relative}: {len(assigned)} {kind} icons")
    return len(assigned)


if __name__ == "__main__":
    for icon_kind, paths in FILES.items():
        for filename in paths:
            update_file(filename, icon_kind)
