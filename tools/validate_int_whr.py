"""Static checks for the White Russian post-civil-war focus paths."""

from collections import Counter
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "common/national_focus/INT - RCW - White Russia.txt"
PATHS = ROOT / "common/national_focus/INT - WHR Paths.txt"
DECISIONS = ROOT / "common/decisions/INT_WHR_Paths.txt"
CATEGORIES = ROOT / "common/decisions/categories/INT_WHR_Paths.txt"
EVENTS = ROOT / "events/INT_WHR_Paths.txt"
NEWS = ROOT / "events/INT_WHR_News.txt"
IDEAS = ROOT / "common/ideas/INT_WHR_Paths.txt"
LOC = ROOT / "localisation/replace/english/endsieg_INT_WHR_paths_l_english.yml"
NEWS_LOC = ROOT / "localisation/replace/english/endsieg_INT_WHR_news_l_english.yml"
CHARACTERS = ROOT / "common/characters/WWI - WHR.txt"
HISTORY = ROOT / "history/countries/WHR - White Russia.txt"
LEGACY_EVENTS = ROOT / "events/INT - White Russia.txt"
ON_ACTIONS = ROOT / "common/on_actions/endsieg_on_actions.txt"
IDEOLOGIES = ROOT / "common/ideologies/00_ideologies.txt"
SPRITES = ROOT / "interface/endsieg_ideas.gfx"
EVENT_SPRITES = ROOT / "interface/endsieg_eventpictures.gfx"
CUSTOM_FOCUS_SPRITES = ROOT / "interface/endsieg_int_whr_focus_icons.gfx"
CUSTOM_EVENT_SPRITES = ROOT / "interface/endsieg_int_whr_eventpictures.gfx"
errors = []


def check(ok, message):
    if not ok:
        errors.append(message)


def read(path):
    return path.read_text(encoding="utf-8-sig")


def balanced(path):
    depth = 0
    quoted = False
    escaped = False
    comment = False
    for char in read(path):
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
                errors.append(f"{path.name}: excess closing brace")
                return
    check(depth == 0 and not quoted, f"{path.name}: unbalanced braces or quote")


for path in (TREE, PATHS, DECISIONS, CATEGORIES, EVENTS, NEWS, IDEAS,
             CHARACTERS, HISTORY, LEGACY_EVENTS, ON_ACTIONS):
    balanced(path)

tree = read(TREE)
paths = read(PATHS)
decisions = read(DECISIONS)
categories = read(CATEGORIES)
events = read(EVENTS)
news = read(NEWS)
ideas = read(IDEAS)
characters = read(CHARACTERS)
history = read(HISTORY)
legacy_events = read(LEGACY_EVENTS)
on_actions = read(ON_ACTIONS)
loc = read(LOC)
news_loc = read(NEWS_LOC)

check("id = White_Russia" in tree, "White_Russia tree ID changed")
old_ids = re.findall(r"^\s*id = (WHR_[A-Za-z0-9_]+)\s*$", tree, re.M)
new_ids = re.findall(r"^\s*id = (WHR_INT_[A-Za-z0-9_]+)\s*$", paths, re.M)
all_ids = old_ids + new_ids
check(len(new_ids) == 43, f"Expected 43 new focuses, got {len(new_ids)}")
for ident, count in Counter(all_ids).items():
    check(count == 1, f"Duplicate focus ID: {ident}")
attached = re.findall(r"^\s*shared_focus = (WHR_INT_[A-Za-z0-9_]+)\s*$", tree, re.M)
check(Counter(attached) == Counter(new_ids), "White_Russia tree attachments do not match new focuses")
for parent in re.findall(r"prerequisite = \{([^}]+)\}", paths):
    for ident in re.findall(r"focus = (WHR_[A-Za-z0-9_]+)", parent):
        check(ident in all_ids, f"Missing prerequisite: {ident}")
check("tree = generic_focus keep_completed = yes" in paths, "1936 generic focus handoff missing")
check("focus = WHR_INT_recovery_1935" in paths, "1936 handoff lacks economic recovery")
check(all(f"focus = WHR_INT_{name}" in paths for name in
          ("republic_1935", "monarchy_1935", "kolchak_1935")),
      "1936 handoff lacks a political ending")

positions = {}
for source in (tree, paths):
    for ident, x, y in re.findall(
            r"id = (WHR_[A-Za-z0-9_]+)\s+icon = [^\n]+\s+cost = [^\n]+\s+"
            r"(?:prerequisite = \{[^}]+\}\s+|mutually_exclusive = \{[^}]+\}\s+)*"
            r"x = (\d+)\s+y = (\d+)", source):
        key = (x, y)
        if key in positions and (ident in new_ids or positions[key] in new_ids):
            errors.append(f"Overlapping focuses at {key}: {positions[key]}, {ident}")
        positions[key] = ident

def loc_keys(source):
    keys = re.findall(r"^\s*([A-Za-z0-9_.]+):", source, re.M)
    check(len(keys) == len(set(keys)), "Duplicate localisation keys")
    return set(keys)


keys = loc_keys(loc)
news_keys = loc_keys(news_loc)
decision_ids = re.findall(r"^\t(INT_WHR_[A-Za-z0-9_]+) = \{", decisions, re.M)
category_ids = re.findall(r"^(INT_WHR_[A-Za-z0-9_]+) = \{", categories, re.M)
idea_ids = re.findall(r"^\t\t(INT_WHR_[A-Za-z0-9_]+) = \{", ideas, re.M)
event_ids = re.findall(r"^\s*id = (INT_whr_paths\.\d+)\s*$", events, re.M)
news_ids = re.findall(r"^\s*id = (INT_whr_news\.\d+)\s*$", news, re.M)
for ident in new_ids + decision_ids + category_ids + idea_ids:
    check(ident in keys, f"Missing localisation: {ident}")
    check(ident + "_desc" in keys, f"Missing description: {ident}")
for ident in event_ids:
    for suffix in (".t", ".d", ".a", ".b"):
        check(ident + suffix in keys, f"Missing event localisation: {ident + suffix}")
for ident in news_ids:
    for suffix in (".t", ".d", ".a"):
        check(ident + suffix in news_keys, f"Missing news localisation: {ident + suffix}")
for ident in re.findall(r"country_event = \{ id = (INT_whr_paths\.\d+) days = 1 \}", paths):
    check(ident in event_ids, f"Focus calls missing event: {ident}")
for ident in re.findall(r"news_event = \{ id = (INT_whr_news\.\d+) days = 1 \}", paths):
    check(ident in news_ids, f"Focus calls missing news: {ident}")
for ident in re.findall(r"(?:add_ideas = |idea = )(INT_WHR_[A-Za-z0-9_]+)",
                        paths + decisions + events):
    check(ident in idea_ids, f"Undefined idea: {ident}")
for ident in re.findall(r"has_completed_focus = (WHR_INT_[A-Za-z0-9_]+)", decisions + characters):
    check(ident in new_ids, f"Missing gated focus: {ident}")
for ident in re.findall(r"^(INT_WHR_[A-Za-z0-9_]+) = \{", decisions, re.M):
    check(ident in category_ids, f"Decision category missing: {ident}")

sprites = read(SPRITES)
legacy_advisors = re.findall(
    r"(?m)^\s*(WHR_[A-Za-z0-9_]+)\s*=\s*\{",
    re.sub(r"(?m)#.*$", "", read(ROOT / "common/ideas/INT - White Russia.txt")))
for ident in set(legacy_advisors):
    check("GFX_idea_" + ident in sprites, f"Existing advisor sprite missing: {ident}")
    check((ROOT / f"gfx/interface/ideas/idea_{ident}.dds").is_file(),
          f"Existing advisor portrait missing: {ident}")
    check(re.search(r'name = "GFX_idea_' + re.escape(ident) +
                    r'"\s+texturefile = "gfx/interface/ideas/idea_' +
                    re.escape(ident) + r'\.dds"', sprites) is not None,
          f"Existing advisor sprite uses the wrong portrait: {ident}")
for person in ("Rudolf_Gajda", "Vladimir_Kappel", "Anatoly_Pepelyayev"):
    ident = "WHR_" + person
    check("GFX_idea_" + ident in sprites, f"Advisor sprite missing: {ident}")
    check((ROOT / f"gfx/interface/ideas/idea_{ident}.dds").is_file(),
          f"Advisor portrait missing: {ident}")
    check("idea_token = WHR_" + person.lower() in characters,
          f"Advisor role missing: {ident}")
check("recruit_character = WHR_INT_alexander_kerensky" in history,
      "Kerensky is not recruited at scenario start")
for token, sprite, focus_id in (
        ("WHR_Anton_Denekin", "GFX_idea_WHR_Anton_Denekin", "WHR_INT_officer_government"),
        ("WHR_INT_alexander_kerensky", "GFX_idea_alexander_kerensky", "WHR_INT_civic_ministries")):
    check("idea_token = " + token in characters and
          "available = { has_completed_focus = " + focus_id + " }" in characters,
          f"Focus-gated advisor role missing: {token}")
    match = re.search(r'name = "' + re.escape(sprite) +
                      r'"\s+texturefile = "([^"]+)"', sprites)
    check(match is not None and (ROOT / match.group(1)).is_file() if match else False,
          f"Advisor portrait missing: {token}")
    check(focus_id in new_ids, f"Advisor unlock focus missing: {focus_id}")
check("WHR_INT_alexander_kerensky" in keys and
      "WHR_INT_alexander_kerensky_desc" in keys,
      "Kerensky advisor localisation missing")
check((ROOT / "gfx/leaders/WHR/Portrait_Russia_Alexander_Kerensky.dds").is_file(),
      "White Russian Kerensky leader portrait missing")

# Runtime recruit_character is ignored by current HOI4; dynamic paths must
# promote an existing character or use create_country_leader as a fallback.
ideology_types = set()
for types_block in re.findall(r"(?ms)^\t\ttypes = \{(.*?)^\t\t\}", read(IDEOLOGIES)):
    ideology_types.update(re.findall(r"(?m)^\t\t\t([A-Za-z0-9_]+)\s*=\s*\{", types_block))
check(bool(ideology_types), "No ideology subtypes found")
for path, source in ((LEGACY_EVENTS, legacy_events), (PATHS, paths)):
    check(re.search(r"(?m)^\s*recruit_character\s*=", source) is None,
          f"{path.name}: runtime recruit_character cannot create a leader")
    for ideology in re.findall(r"(?m)^\s*ideology\s*=\s*([A-Za-z0-9_]+)", source):
        check(ideology in ideology_types,
              f"{path.name}: undefined leader ideology: {ideology}")
    for portrait in re.findall(r'picture\s*=\s*"([^"\n]+\.dds)"', source):
        check(any((ROOT / "gfx/leaders" / tag / portrait).is_file()
                  for tag in ("WHR", "RUS", "MON")),
              f"{path.name}: leader portrait missing: {portrait}")
check("has_global_flag = BOC_denikin_victory" in on_actions and
      'name = "Semyon Ivanov"' in on_actions,
      "Existing Denikin campaign leader repair missing")

event_sprites = read(EVENT_SPRITES) + read(CUSTOM_EVENT_SPRITES)
for picture in re.findall(r"picture = (GFX_[A-Za-z0-9_]+)", events + news):
    check(picture in event_sprites, f"Event/news picture missing: {picture}")
    match = re.search(r'name = "' + re.escape(picture) +
                      r'"\s+texturefile = "([^"]+)"', event_sprites)
    check(match is not None and (ROOT / match.group(1)).is_file() if match else False,
          f"Event/news picture texture missing: {picture}")

def locate_vanilla():
    candidates = []
    if os.environ.get("HOI4_INSTALL"):
        candidates.append(Path(os.environ["HOI4_INSTALL"]))
    for variable in ("PROGRAMFILES(X86)", "PROGRAMFILES"):
        if os.environ.get(variable):
            steamapps = Path(os.environ[variable]) / "Steam/steamapps"
            candidates.append(steamapps / "common/Hearts of Iron IV")
    return next((path for path in candidates if (path / "interface/goals.gfx").is_file()), None)


vanilla = locate_vanilla()
check(vanilla is not None, "Current vanilla HOI4 installation not found")
if vanilla is not None:
    goal_sprites = read(vanilla / "interface/goals.gfx")
    custom_goal_sprites = read(CUSTOM_FOCUS_SPRITES)
    decision_sprites = read(vanilla / "interface/decisions.gfx")
    idea_sprites = read(vanilla / "interface/ideas.gfx")
    unique_ideas = read(ROOT / "interface/endsieg_interwar_unique_ideas.gfx")
    for icon in re.findall(r"icon = (GFX_goal_[A-Za-z0-9_]+)", paths):
        check(icon in (custom_goal_sprites if icon.startswith("GFX_goal_WHR_INT_") else goal_sprites),
              f"Focus icon missing: {icon}")
    for icon in re.findall(r"icon = (generic_[A-Za-z0-9_]+|generic)", decisions + categories):
        check("GFX_decision_" + icon in decision_sprites, f"Decision icon missing: {icon}")
    for picture in re.findall(r"picture = ([A-Za-z0-9_]+)", ideas):
        sprite = "GFX_idea_" + picture
        check(sprite in idea_sprites or sprite in unique_ideas, f"Idea picture missing: {picture}")
    vanilla_focus_text = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace")
                                   for path in (vanilla / "common/national_focus").glob("*.txt"))
    for category in set(re.findall(r"category = ([A-Za-z0-9_]+)",
                                   paths + decisions + events)):
        check("category = " + category in vanilla_focus_text,
              f"Technology bonus category has no vanilla precedent: {category}")
    check("id = generic_focus" in read(vanilla / "common/national_focus/generic.txt"),
          "Vanilla generic focus tree missing")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(new_ids)} focuses, {len(decision_ids)} decisions, "
      f"{len(event_ids)} choice events, {len(news_ids)} news events, "
      f"{len(idea_ids)} ideas, 5 focus-gated advisor roles and {len(set(legacy_advisors))} portrait-backed existing advisors")
