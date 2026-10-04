"""Static reference checks for the Soviet interwar expansion; does not launch HOI4."""

from collections import Counter
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FOCUS = ROOT / "common/national_focus/INT - RCW - Soviet Russia.txt"
DECISIONS = ROOT / "common/decisions/INT_SOV_Paths.txt"
CATEGORIES = ROOT / "common/decisions/categories/INT_SOV_Paths.txt"
EVENTS = ROOT / "events/INT_SOV_Paths.txt"
IDEAS = ROOT / "common/ideas/INT_SOV_Paths.txt"
LOC = ROOT / "localisation/replace/english/endsieg_INT_SOV_paths_l_english.yml"
HISTORY = ROOT / "history/countries/SOV - Soviet union.txt"
CHARACTERS = ROOT / "common/characters/WWI - SOV.txt"
HANDOFF = ROOT / "common/scripted_effects/INT_SOV_Paths.txt"
GFX = ROOT / "interface/endsieg_ideas.gfx"


def locate_vanilla():
    candidates = []
    if os.environ.get("HOI4_INSTALL"):
        candidates.append(Path(os.environ["HOI4_INSTALL"]))
    for variable in ("PROGRAMFILES(X86)", "PROGRAMFILES"):
        if os.environ.get(variable):
            steamapps = Path(os.environ[variable]) / "Steam/steamapps"
            candidates.append(steamapps / "common/Hearts of Iron IV")
            libraries = steamapps / "libraryfolders.vdf"
            if libraries.is_file():
                for library in re.findall(r'"path"\s+"([^"]+)"',
                                          libraries.read_text(encoding="utf-8-sig")):
                    candidates.append(Path(library.replace("\\\\", "\\")) /
                                      "steamapps/common/Hearts of Iron IV")
    return next((path for path in candidates if (path / "interface/goals.gfx").is_file()), None)


VANILLA = locate_vanilla()
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def balanced(path):
    source = path.read_text(encoding="utf-8-sig")
    depth = 0
    quoted = False
    escaped = False
    comment = False
    for char in source:
        if comment:
            if char == "\n":
                comment = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == "#":
            comment = True
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                errors.append(f"{path.name}: unexpected closing brace")
                return
    check(depth == 0 and not quoted, f"{path.name}: unbalanced braces or quotes")


for path in (FOCUS, DECISIONS, CATEGORIES, EVENTS, IDEAS, HISTORY, CHARACTERS, HANDOFF):
    balanced(path)

focus_text = FOCUS.read_text(encoding="utf-8-sig")
new_focus = focus_text[focus_text.index("id = SO2_INT_transport_reconstruction"):]
all_focus_ids = re.findall(r"^\s*id = (SO2_[A-Za-z0-9_]+)\s*$", focus_text, re.M)
new_focus_ids = re.findall(r"^\s*id = (SO2_INT_[A-Za-z0-9_]+)\s*$", new_focus, re.M)
for focus_id, count in Counter(all_focus_ids).items():
    check(count == 1, f"Duplicate focus ID: {focus_id}")
for parent in re.findall(r"prerequisite = \{ focus = (SO2_[A-Za-z0-9_]+) \}", new_focus):
    check(parent in all_focus_ids, f"Missing prerequisite: {parent}")
check(len(new_focus_ids) == 18, f"Expected 17 new focuses and the 1936 handoff; got {len(new_focus_ids)}")
check("prerequisite = { focus = SO2_INT_workers_congress focus = SO2_INT_plan_consolidation focus = SO2_INT_cooperative_union }" in focus_text,
      "1936 handoff does not accept all three political endings")
check("tree = soviet_focus keep_completed = yes" in focus_text, "1936 vanilla-tree handoff missing")
check("INT_SOV_1936_roster_handoff = yes" in focus_text, "1936 roster handoff missing")
check("prerequisite = { focus = SO2_INT_plan_targets }" in focus_text, "Second plan lacks target-setting prerequisite")

decision_text = DECISIONS.read_text(encoding="utf-8-sig")
category_text = CATEGORIES.read_text(encoding="utf-8-sig")
event_text = EVENTS.read_text(encoding="utf-8-sig")
ideas_text = IDEAS.read_text(encoding="utf-8-sig")
loc_text = LOC.read_text(encoding="utf-8-sig")
loc_keys = re.findall(r"^\s*([A-Za-z0-9_.]+):", loc_text, re.M)
check(len(loc_keys) == len(set(loc_keys)), "Duplicate keys in Soviet interwar localisation")
loc_set = set(loc_keys)
decision_ids = re.findall(r"^\t(INT_SOV_[A-Za-z0-9_]+) = \{", decision_text, re.M)
category_ids = re.findall(r"^(INT_SOV_[A-Za-z0-9_]+) = \{", category_text, re.M)
idea_ids = re.findall(r"^\t\t(INT_SOV_[A-Za-z0-9_]+) = \{", ideas_text, re.M)
event_ids = re.findall(r"^\s*id = (INT_sov_rework\.\d+)\s*$", event_text, re.M)
for key in new_focus_ids + decision_ids + category_ids + idea_ids:
    if key == "SO2_INT_enter_1936":
        continue
    check(key in loc_set, f"Missing localisation: {key}")
    check(key + "_desc" in loc_set, f"Missing description: {key}")
for event_id in event_ids:
    for suffix in (".t", ".d", ".a", ".b"):
        check(event_id + suffix in loc_set, f"Missing event localisation: {event_id + suffix}")
for event_id in re.findall(r"country_event = \{ id = (INT_sov_rework\.\d+) days = 1 \}", focus_text):
    check(event_id in event_ids, f"Focus calls undefined event: {event_id}")
for idea in re.findall(r"(?:add_ideas = |idea = )(INT_SOV_[A-Za-z0-9_]+)", new_focus + decision_text + event_text):
    check(idea in idea_ids, f"Undefined new idea: {idea}")
for focused in re.findall(r"has_completed_focus = (SO2_INT_[A-Za-z0-9_]+)", decision_text):
    check(focused in all_focus_ids, f"Decision references missing focus: {focused}")
for category in re.findall(r"^(INT_SOV_[A-Za-z0-9_]+) = \{", decision_text, re.M):
    check(category in category_ids, f"Decision category missing: {category}")

check(VANILLA is not None, "Current vanilla HOI4 directory not found")
if VANILLA is not None:
    vanilla_goals = (VANILLA / "interface/goals.gfx").read_text(encoding="utf-8-sig")
    vanilla_decisions = (VANILLA / "interface/decisions.gfx").read_text(encoding="utf-8-sig")
    vanilla_ideas = (VANILLA / "interface/ideas.gfx").read_text(encoding="utf-8-sig")
    custom_goals_path = ROOT / "interface/endsieg_int_sov_focus_icons.gfx"
    custom_ideas_path = ROOT / "interface/endsieg_interwar_unique_ideas.gfx"
    custom_goals = custom_goals_path.read_text(encoding="utf-8-sig") if custom_goals_path.is_file() else ""
    custom_ideas = custom_ideas_path.read_text(encoding="utf-8-sig") if custom_ideas_path.is_file() else ""
    for icon in re.findall(r"icon = (GFX_goal_[A-Za-z0-9_]+)", new_focus):
        check(icon in vanilla_goals or icon in custom_goals, f"Focus icon missing: {icon}")
    for icon in re.findall(r"icon = (generic_[A-Za-z0-9_]+|generic)", decision_text + category_text):
        check("GFX_decision_" + icon in vanilla_decisions, f"Decision icon missing from vanilla: {icon}")
    for picture in re.findall(r"picture = ([A-Za-z0-9_]+)", ideas_text):
        sprite = "GFX_idea_" + picture
        check(sprite in vanilla_ideas or sprite in custom_ideas, f"Idea picture missing: {picture}")
picture_names = re.findall(r"picture = (GFX_report_event_[A-Za-z0-9_]+)", event_text)
picture_gfx = (ROOT / "interface/endsieg_eventpictures.gfx").read_text(encoding="utf-8-sig")
for picture in picture_names:
    check(picture in picture_gfx, f"Event picture missing: {picture}")

history_text = HISTORY.read_text(encoding="utf-8-sig")
characters_text = CHARACTERS.read_text(encoding="utf-8-sig")
handoff_text = HANDOFF.read_text(encoding="utf-8-sig")
gfx_text = GFX.read_text(encoding="utf-8-sig")
pre_1920, remaining = history_text.split("1920.1.1 = {", 1)
interwar, after_1936 = remaining.split("1936.1.1 = {", 1)
advisors = ("Maxim_Litvinov", "Georgi_Chicherin", "Grigori_Sokolnikov",
            "Andrei_Bubnov", "Yan_Berzin", "Andrey_Vyshinsky",
            "Alexei_Rykov", "Ivan_Isakov", "Mikhail_Tukachevsky", "Yakov_Alksnis")
for name in advisors:
    ident = "SOV_" + name
    check("recruit_character = " + ident in pre_1920, f"Advisor not initially recruited: {ident}")
    check("retire_character = " + ident not in interwar, f"Advisor still retired in 1920: {ident}")
    check("retire_character = " + ident in after_1936, f"Advisor not retired at 1936 handoff: {ident}")
    check(ident + "={" in characters_text, f"Advisor definition missing: {ident}")
    check("GFX_idea_" + ident in gfx_text, f"Advisor portrait sprite missing: {ident}")
    check((ROOT / f"gfx/interface/ideas/idea_{ident}.dds").is_file(), f"Advisor portrait DDS missing: {ident}")
for name, ledger, focus_id, trait in (
        ("Ivan_Isakov", "navy", "SO2_INT_baltic_fleet_repairs", "naval_theorist"),
        ("Mikhail_Tukachevsky", "army", "SO2_INT_deep_operations", "military_theorist"),
        ("Yakov_Alksnis", "air", "SO2_INT_flight_schools", "air_warfare_theorist")):
    ident = "SOV_" + name
    pattern = (r"advisor\s*=\s*\{\s*slot = theorist\s*ledger = " + ledger +
               r"\s*idea_token = " + ident + r"\s*allowed = \{ original_tag = SOV \}\s*" +
               r"available = \{ has_completed_focus = " + focus_id + r" \}\s*" +
               r"traits = \{ " + trait + r" \}\s*\}")
    check(re.search(pattern, characters_text) is not None,
          f"Missing focus-gated theorist role: {ident}")
    check(focus_id in all_focus_ids, f"Missing theorist unlock focus: {focus_id}")
check("recruit_character = SOV_Leonid_Krasin" in pre_1920, "Krasin is not initially recruited")
check("1926.12.1 = {\n\tretire_character = SOV_Leonid_Krasin" in interwar,
      "Krasin is not retired in 1926")
check("recruit_character = SO2_Ivan_Smirnov" in pre_1920, "Smirnov is not initially recruited")
check("retire_character = SO2_Ivan_Smirnov" not in interwar, "Smirnov is retired in 1920")
check("retire_character = SO2_Ivan_Smirnov" in after_1936, "Smirnov is not retired in 1936")
check("SO2_Ivan_Smirnov={" in characters_text, "Smirnov character definition missing")
check("GFX_idea_SOV_Ivan_Smirnov" in gfx_text, "Smirnov portrait sprite missing")
check((ROOT / "gfx/interface/ideas/idea_SOV_Ivan_Smirnov.dds").is_file(),
      "Smirnov portrait DDS missing")
old_roster = re.findall(r"retire_character = ((?:SOV|SO2)_[A-Za-z0-9_]+)", handoff_text)
modern_roster = re.findall(r"recruit_character = (SOV_[A-Za-z0-9_]+)", handoff_text)
check(len(old_roster) >= 30 and len(old_roster) == len(set(old_roster)), "Interwar roster retirement incomplete or duplicated")
check(len(modern_roster) >= 80 and len(modern_roster) == len(set(modern_roster)), "1936 roster recruitment incomplete or duplicated")
check(all("has_character = " + ident in handoff_text for ident in old_roster + modern_roster),
      "Roster handoff has an unguarded character effect")
if VANILLA is not None:
    vanilla_characters = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace")
                                   for path in (VANILLA / "common/characters").glob("SOV*.txt"))
    for ident in modern_roster:
        check(ident in vanilla_characters or ident in characters_text,
              f"1936 handoff references an undefined character: {ident}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(new_focus_ids)-1} new focuses, {len(decision_ids)} decisions, "
      f"{len(event_ids)} events, {len(idea_ids)} ideas, {len(advisors)+2} interwar advisor characters, "
      "3 focus-gated theorist roles, "
      f"{len(modern_roster)} guarded 1936 recruits")
