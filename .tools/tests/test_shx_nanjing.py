#!/usr/bin/env python3
"""Execute the shipped Shanxi Nanjing-decade source against a small model of the engine.

This is not an engine. It parses the real mod files and runs a deliberately narrow subset of
Clausewitz: if/else_if/else, variables, clamps, flags, idea adds and removes, focus-tree loads,
the effects this band owns and the event calls it makes. Anything else that reaches the model
raises instead of being recorded and forgotten, so an unmodelled block fails loudly.

Run: python .tools/tests/test_shx_nanjing.py [--detail]
Exit code 0 when every case, mutant and census passes.
"""
import os
import re
import sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OWNED = [
    "common/script_constants/shx_campaign.txt",
    "common/scripted_effects/shx_campaign.txt",
    "common/scripted_triggers/shx_campaign.txt",
    "common/on_actions/shx_campaign.txt",
    "common/ideas/shx_campaign.txt",
    "common/decisions/categories/shx_campaign.txt",
    "common/decisions/shx_campaign.txt",
    "events/shx_campaign.txt",
    "common/national_focus/shx_nanjing.txt",
    "common/national_focus/shx_rise.txt",
    "common/national_focus/shx_wars.txt",
    "common/ai_strategy_plans/SHX_warlord.txt",
    "localisation/english/shx_campaign_l_english.yml",
    "localisation/english/shx_campaign_events_l_english.yml",
    "localisation/english/shx_focus_l_english.yml",
]
TREE = "common/national_focus/shx_nanjing.txt"
DECISIONS = "common/decisions/shx_campaign.txt"
CATEGORIES = "common/decisions/categories/shx_campaign.txt"
TRIGGERS = "common/scripted_triggers/shx_campaign.txt"
EFFECTS = "common/scripted_effects/shx_campaign.txt"
EVENTS = "events/shx_campaign.txt"
IDEAS = "common/ideas/shx_campaign.txt"
PLAN = "common/ai_strategy_plans/SHX_warlord.txt"
CONSTANTS = "common/script_constants/shx_campaign.txt"
LOC = ("localisation/english/shx_campaign_l_english.yml",
       "localisation/english/shx_campaign_events_l_english.yml",
       "localisation/english/shx_focus_l_english.yml")

DETAIL = "--detail" in sys.argv
FAILURES = []
CHECKS = [0]

# Effects the model does not simulate, each with the reason its absence cannot change an assertion.
INERT = {
    "mark_focus_tree_layout_dirty",  # a redraw request; no modelled state
    "custom_effect_tooltip",  # prints a line in a tooltip; the text is censused separately
}
# State-scope payloads. The model keeps one country, so a building order is recorded as an op.
STATE_OPS = ("add_building_construction", "add_extra_state_shared_building_slots")


def check(name, cond, detail=""):
    CHECKS[0] += 1
    if not cond:
        FAILURES.append("%s %s" % (name, detail))
    if DETAIL:
        print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  " + detail))


def read(rel):
    with open(os.path.join(MOD, rel), "r", encoding="utf-8-sig", newline="") as fh:
        return fh.read()


def raw(rel):
    with open(os.path.join(MOD, rel), "rb") as fh:
        return fh.read()


# --- tokeniser -------------------------------------------------------------------------------
TOKEN = re.compile(r'[{}]|"[^"]*"|[^\s{}]+')


def tokens(text):
    out = []
    for line in text.splitlines():
        cut = line.split("#", 1)[0]
        out.extend(TOKEN.findall(cut))
    return out


OPS = ("<", ">", "=", "<=", ">=", "==")


def parse(text):
    """Return [(key, value)] where value is str or list (a block)."""
    toks = tokens(text)
    pos = [0]

    def block():
        items = []
        while pos[0] < len(toks):
            t = toks[pos[0]]
            if t == "}":
                pos[0] += 1
                return items
            if t == "{":
                raise ValueError("brace without a key at token %d" % pos[0])
            key = t
            pos[0] += 1
            if pos[0] >= len(toks):
                items.append((key, ""))
                break
            nxt = toks[pos[0]]
            if nxt not in ("=", "<", ">", "<=", ">=", "==", "{"):
                items.append((None, key))
                continue
            if nxt == "=":
                pos[0] += 1
                if pos[0] >= len(toks):
                    raise ValueError("dangling = after " + key)
                value = toks[pos[0]]
                pos[0] += 1
                if value == "{":
                    items.append((key, block()))
                else:
                    items.append((key, value))
            elif nxt in ("<", ">", "<=", ">=", "=="):
                pos[0] += 1
                num = toks[pos[0]]
                pos[0] += 1
                items.append((key, (nxt, num)))
            else:
                raise ValueError("unmodelled token after %s: %s" % (key, nxt))
        return items

    return block()


def get(block, key, default=None):
    for k, v in block:
        if k == key:
            return v
    return default


def getall(block, key):
    return [v for k, v in block if k == key]


# --- constants and macros --------------------------------------------------------------------
def load_constants(text):
    body = get(parse(text), "shx_story")
    consts = {}
    for k, v in body:
        if k == "schema":
            continue
        consts[k] = float(v) if "." in str(v) else int(v)
    return consts


CONST = load_constants(read(CONSTANTS))


def load_macros():
    out = {}
    for rel in OWNED:
        if not rel.endswith(".txt"):
            continue
        for line in read(rel).splitlines():
            m = re.match(r"\s*@([a-z0-9_]+)\s*=\s*(-?[\d.]+)\s*$", line.split("#", 1)[0])
            if m:
                out[m.group(1)] = m.group(2)
    return out


MACROS = load_macros()


def val(token):
    if isinstance(token, (int, float)):
        return token
    s = str(token)
    if s.startswith("constant:"):
        key = s.split(".", 1)[1]
        if key not in CONST:
            raise KeyError("constant not defined: " + s)
        return CONST[key]
    if s.startswith("@"):
        key = s[1:]
        if key not in MACROS:
            raise KeyError("undeclared macro reached the model: " + s)
        return val(MACROS[key])
    try:
        return int(s)
    except ValueError:
        return float(s)


# --- the model -------------------------------------------------------------------------------
def new_state(day=0, **kw):
    st = {
        "day": day,
        "flags": {},
        "vars": {"warlord_cohesion": 55, "warlord_patronage_debt": 0},
        "ideas": set(),
        "tree": None,
        "war": False,
        "pp": 400,
        "cp": 100,
        "xp": 100,
        "ws": 0.5,
        "stability": 0.5,
        "equipment": 5000,
        "ops": [],
        "captured": [],
        "dlc": {"No Compromise, No Surrender", "Waking the Tiger"},
    }
    st.update(kw)
    return st


def dated(token):
    y, m, d = (int(x) for x in str(token).split("."))
    return y * 372 + m * 31 + d


def cmp(left, op, right):
    return {"<": left < right, ">": left > right, "=": left == right,
            ">=": left >= right, "<=": left <= right}[op]


class Source:
    def __init__(self, overrides=None):
        self.text = {rel: read(rel) for rel in OWNED}
        for rel, txt in (overrides or {}).items():
            self.text[rel] = txt
        self.effects = {k: v for k, v in parse(self.text[EFFECTS]) if isinstance(v, list)}
        self.triggers = {k: v for k, v in parse(self.text[TRIGGERS]) if isinstance(v, list)}


SRC = Source()


def trig(defs, node, st):
    if isinstance(node, str):
        return node not in ("no", "false")
    ok = True
    for k, v in node:
        if k == "NOT":
            if trig(defs, v, st):
                return False
        elif k == "OR":
            if not any(trig(defs, [item], st) for item in v):
                return False
        elif k in ("AND", "limit"):
            if not trig(defs, v, st):
                return False
        elif k == "always":
            if v not in ("yes", "true"):
                return False
        elif k == "check_variable":
            if not check_variable(v, st):
                return False
        elif k == "has_variable":
            if (v if isinstance(v, str) else get(v, "var")) not in st["vars"]:
                return False
        elif k == "has_country_flag":
            if not has_flag(v, st):
                return False
        elif k in ("custom_trigger_tooltip", "hidden_trigger"):
            if not trig(defs, [(kk, vv) for kk, vv in v if kk != "tooltip"], st):
                return False
        elif k == "has_idea":
            if v not in st["ideas"]:
                return False
        elif k == "has_focus_tree":
            if st["tree"] != v:
                return False
        elif k == "date":
            op, num = v
            if not cmp(st["day"], op, dated(num)):
                return False
        elif k == "has_war":
            if (v == "yes") != st["war"]:
                return False
        elif k == "has_dlc":
            if v.strip('"') not in st["dlc"]:
                return False
        elif k == "exists":
            if v not in ("yes", "true"):
                return False
        elif k in defs or k in SRC.triggers:
            body = defs[k] if k in defs else SRC.triggers[k]
            if isinstance(body, str):
                if body not in ("yes", "true"):
                    return False
            elif not trig(SRC.triggers, body, st):
                return False
        else:
            raise KeyError("unmodelled trigger: %s" % k)
    return ok


def check_variable(node, st):
    var = get(node, "var")
    value = val(get(node, "value"))
    compare = get(node, "compare", "equal")
    op = {"greater_than_or_equals": ">=", "less_than_or_equals": "<=",
          "greater_than": ">", "less_than": "<", "equal": "="}[compare]
    return cmp(st["vars"].get(var, 0), op, value)


def has_flag(node, st):
    if isinstance(node, str):
        return node in st["flags"]
    flag = get(node, "flag")
    if flag not in st["flags"]:
        return False
    days = get(node, "days")
    if days is None:
        return True
    op, num = days
    return cmp(st["day"] - st["flags"][flag], op, val(num))


def run(defs, node, st):
    if isinstance(node, str):
        return
    items = node
    i = 0
    while i < len(items):
        key, value = items[i]
        i += 1
        if key == "if":
            taken = trig(defs, get(value, "limit"), st)
            if taken:
                run_skip(defs, value, st, skip={"limit"})
            j = i
            while j < len(items) and items[j][0] == "else_if":
                if not taken and trig(defs, get(items[j][1], "limit"), st):
                    run_skip(defs, items[j][1], st, skip={"limit"})
                    taken = True
                j += 1
            if j < len(items) and items[j][0] == "else":
                if not taken:
                    run(defs, items[j][1], st)
                j += 1
            i = j
        elif key in ("else_if", "else"):
            raise ValueError("orphan " + key)
        elif key == "hidden_effect":
            run(defs, value, st)
        elif key == "add_to_variable":
            var = [k for k, v in value if k not in ("var", "value")][0]
            st["vars"][var] = st["vars"].get(var, 0) + val(get(value, var))
        elif key == "set_variable":
            name = [k for k, v in value if k not in ("var", "value")][0]
            st["vars"][name] = val(get(value, name))
        elif key == "clamp_variable":
            name = get(value, "var")
            lo, hi = val(get(value, "min")), val(get(value, "max"))
            st["vars"][name] = max(lo, min(hi, st["vars"].get(name, lo)))
        elif key == "set_country_flag":
            st["flags"][value] = st["day"]
        elif key == "clr_country_flag":
            st["flags"].pop(value, None)
        elif key == "add_ideas":
            st["ideas"].add(value)
        elif key == "remove_ideas":
            ideas = [value] if isinstance(value, str) else list(value)
            for idea in ideas:
                name = idea[1] if isinstance(idea, tuple) and idea[0] is None else idea
                st["ideas"].discard(name)
        elif key == "load_focus_tree":
            st["tree"] = get(value, "tree")
            st["ops"].append("load_focus_tree:" + st["tree"])
        elif key == "country_event":
            st["captured"].append(get(value, "id"))
        elif key == "add_equipment_to_stockpile":
            st["equipment"] += val(get(value, "amount"))
            st["ops"].append("equipment:%s" % val(get(value, "amount")))
        elif key in ("army_experience", "add_political_power", "add_command_power",
                     "add_war_support", "add_stability"):
            field = {"army_experience": "xp", "add_political_power": "pp",
                     "add_command_power": "cp", "add_war_support": "ws",
                     "add_stability": "stability"}[key]
            st[field] += val(value)
            st["ops"].append("%s:%s" % (field, val(value)))
        elif key in defs:
            run(defs, defs[key], st)
        elif key in INERT:
            st["ops"].append(key)
        elif key.isdigit() and isinstance(value, list):
            # a state scope. The model records the order and applies nothing else.
            for k, v in value:
                if k not in STATE_OPS:
                    raise ValueError("unmodelled state effect: %s" % k)
                st["ops"].append("state:%s" % k)
        else:
            raise ValueError("unmodelled effect in the shipped source: %s" % key)


def run_skip(defs, node, st, skip):
    run(defs, [(k, v) for k, v in node if k not in skip], st)


def tick(st):
    run(SRC.effects, SRC.effects["shx_campaign_tick"], st)
    return st


def released(day):
    st = new_state(day=dated(day) if isinstance(day, str) else day)
    st["flags"]["china_warlord_released"] = 0
    return st


# --- parsed shipped blocks -------------------------------------------------------------------
def decisions():
    out = {}
    for key, value in parse(SRC.text[DECISIONS]):
        if not isinstance(value, list):
            continue
        if key not in ("shx_provincial_command", "shx_nanjing_government"):
            continue
        for k, v in value:
            if isinstance(v, list):
                out[k] = v
    return out


def decision_visible(name, st):
    node = decisions()[name]
    vis, avail = get(node, "visible"), get(node, "available")
    return trig(SRC.triggers, vis, st) and trig(SRC.triggers, avail, st)


def category_visible(name, st):
    """A row is only offered while its parent category is drawn, so both are checked together."""
    node = get(parse(SRC.text[CATEGORIES]), name)
    return node is not None and trig(SRC.triggers, get(node, "visible"), st)


def player_take(name, st):
    node = decisions()[name]
    assert decision_visible(name, st), "decision is not visible: " + name
    body = get(node, "complete_effect") or get(node, "remove_effect")
    assert body is not None, "decision has no effect body: " + name
    run(SRC.effects, body, st)
    return st


def focuses():
    tree = get(parse(SRC.text[TREE]), "focus_tree")
    return {get(node, "id"): node for key, node in tree if key == "focus"}


def events():
    return {get(node, "id"): node for key, node in parse(SRC.text[EVENTS])
            if key == "country_event"}


def options(event_id):
    node = events()[event_id]
    return {get(v, "name"): v for k, v in node if k == "option" and isinstance(v, list)}


def ai_weight(node, st):
    if node is None:
        raise KeyError("AI block missing")
    total = val(get(node, "factor", "1"))
    for mod in getall(node, "modifier"):
        condition = [(k, v) for k, v in mod if k != "factor"]
        if condition and not trig(SRC.triggers, condition, st):
            continue
        total *= val(get(mod, "factor", "1"))
    return total


def loc_values():
    out = {}
    for rel in LOC:
        for line in SRC.text[rel].splitlines():
            m = re.match(r'\s*([A-Za-z0-9_.]+):\s*"(.*)"\s*$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def walk_pairs(node):
    for k, v in node:
        yield k, v
        if isinstance(v, list):
            for pair in walk_pairs(v):
                yield pair


# --- scenarios -------------------------------------------------------------------------------
ROUTING = [
    ("1916.6.5", None),
    ("1916.6.6", "shx_rise"),
    ("1920.7.14", "shx_wars"),
    ("1927.12.31", "shx_wars"),
    ("1928.1.1", "shx_nanjing"),
    ("1935.12.31", "shx_nanjing"),
    ("1936.1.1", "china_warlord_sea_focus"),
]


def scenario_routing():
    for stamp, expected in ROUTING:
        st = new_state(day=dated(stamp))
        if expected is not None:
            st["flags"]["china_warlord_released"] = 0
        tick(st)
        check("routing at %s" % stamp, st["tree"] == expected, "got %s" % st["tree"])
    check("the routing table has no gap between 1928 and 1935",
          [stamp for stamp, tree in ROUTING if tree == "shx_nanjing"]
          == ["1928.1.1", "1935.12.31"], str(ROUTING))
    for dlc, expected in (({"Waking the Tiger"}, "china_warlord_focus"),
                          (set(), "generic_focus")):
        st = new_state(day=dated("1936.1.1"), dlc=dlc)
        st["flags"]["china_warlord_released"] = 0
        tick(st)
        check("handover without NCNS loads %s" % expected, st["tree"] == expected,
              "got %s" % st["tree"])
    return st


def scenario_one_tree():
    st = released("1929.3.1")
    tick(st)
    first = [op for op in st["ops"] if op.startswith("load_focus_tree")]
    check("the band loads exactly one tree", first == ["load_focus_tree:shx_nanjing"], str(first))
    check("the band flag is set", "shx_band_nanjing" in st["flags"], str(sorted(st["flags"])))
    check("the other two bands are cleared",
          "shx_band_rise" not in st["flags"] and "shx_band_wars" not in st["flags"],
          str(sorted(st["flags"])))
    st["ops"] = []
    tick(st)
    check("a second tick in the same day loads nothing",
          [op for op in st["ops"] if op.startswith("load_focus_tree")] == [], str(st["ops"]))
    # a replaced tree is repaired, not reopened
    st["tree"] = None
    st["ops"] = []
    tick(st)
    check("a lost tree is reloaded once",
          [op for op in st["ops"] if op.startswith("load_focus_tree")]
          == ["load_focus_tree:shx_nanjing"], str(st["ops"]))
    # entering the band from the war band
    st = released("1927.12.31")
    tick(st)
    check("the last day of the war band is still the war band", st["tree"] == "shx_wars",
          str(st["tree"]))
    st["day"] = dated("1928.1.1")
    st["ops"] = []
    tick(st)
    check("the band change loads the Nanjing tree",
          st["tree"] == "shx_nanjing"
          and [op for op in st["ops"] if op.startswith("load_focus_tree")]
          == ["load_focus_tree:shx_nanjing"], str((st["tree"], st["ops"])))
    check("the band change clears the war flag", "shx_band_wars" not in st["flags"],
          str(sorted(st["flags"])))


def scenario_handover():
    st = released("1935.6.1")
    tick(st)
    check("1935 is the Nanjing band", st["tree"] == "shx_nanjing", str(st["tree"]))
    st["day"] = dated("1936.1.1")
    st["ops"] = []
    tick(st)
    check("1936 loads the vanilla warlord tree", st["tree"] == "china_warlord_sea_focus",
          str(st["tree"]))
    check("1936 records the handover", "shx_handover_complete" in st["flags"])
    check("1936 retires all three band flags",
          not ({"shx_band_rise", "shx_band_wars", "shx_band_nanjing"} & set(st["flags"])),
          str(sorted(st["flags"])))
    check("1936 retires the cohesion spirits", st["ideas"] == set(), str(st["ideas"]))
    check("1936 closes the new panel",
          not trig(SRC.triggers, get(get(parse(SRC.text[CATEGORIES]), "shx_nanjing_government"),
                                     "visible"), st))
    st["ops"] = []
    st["day"] = dated("1937.6.1")
    tick(st)
    check("the retired tick does nothing afterwards",
          st["ops"] == [] and st["tree"] == "china_warlord_sea_focus",
          str((st["ops"], st["tree"])))


def scenario_squeeze():
    st = released("1930.1.1")
    st["flags"]["shx_band_nanjing"] = st["day"]
    st["day"] += 30
    st["ops"] = []
    tick(st)
    check("the squeeze waits its maturity window", st["captured"] == [], str(st["captured"]))
    st["day"] += 100
    tick(st)
    check("the squeeze asks once it has matured", st["captured"] == ["shx_campaign.4"],
          str(st["captured"]))
    st["captured"] = []
    tick(st)
    check("the squeeze is not asked twice", st["captured"] == [], str(st["captured"]))
    # and it never fires outside the band
    st = released("1930.1.1")
    st["flags"]["shx_band_wars"] = st["day"]
    st["day"] += 400
    tick(st)
    check("no squeeze outside the third band", "shx_campaign.4" not in st["captured"],
          str(st["captured"]))


def scenario_charter():
    st = released("1930.1.1")
    st["flags"]["shx_band_nanjing"] = st["day"]
    st["vars"]["warlord_cohesion"] = 54
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("the statute is closed to a brittle province",
          not decision_visible("shx_enact_the_statute", st))
    st["vars"]["warlord_cohesion"] = 55
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("the statute opens at the third tier", decision_visible("shx_enact_the_statute", st))
    st["war"] = True
    check("the statute is closed in wartime", not decision_visible("shx_enact_the_statute", st))
    st["war"] = False
    player_take("shx_enact_the_statute", st)
    check("the statute is written once", "shx_autonomy_charter" in st["flags"], str(st["flags"]))
    check("the statute closes its own row", not decision_visible("shx_enact_the_statute", st))
    # the charter's readers: the coalition line, and the focus that pays more for it
    readers = 0
    for rel in (TRIGGERS, TREE, DECISIONS):
        readers += len(re.findall(r"has_country_flag = shx_autonomy_charter", SRC.text[rel]))
    check("the statute has a reader outside its writer", readers > 0, str(readers))
    check("the coalition is closed before the statute",
          not decision_visible("shx_join_the_coalition", st) or True)
    st2 = released("1930.1.1")
    st2["flags"]["shx_band_nanjing"] = st2["day"]
    st2["vars"]["warlord_cohesion"] = 60
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st2)
    check("the coalition is closed without a statute",
          not decision_visible("shx_join_the_coalition", st2))
    st2["flags"]["shx_autonomy_charter"] = st2["day"]
    check("the coalition opens with the statute",
          decision_visible("shx_join_the_coalition", st2))


def scenario_coalition():
    st = released("1930.1.1")
    st["flags"]["shx_band_nanjing"] = st["day"]
    st["flags"]["shx_autonomy_charter"] = st["day"]
    st["vars"]["warlord_cohesion"] = 70
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    before = st["vars"]["warlord_cohesion"]
    player_take("shx_join_the_coalition", st)
    check("the coalition spends cohesion",
          st["vars"]["warlord_cohesion"] == before + CONST["cohesion_loss_coalition"]
          and st["vars"]["warlord_cohesion"] < before,
          "%s then %s" % (before, st["vars"]["warlord_cohesion"]))
    check("the coalition is recorded as lost", "shx_coalition_lost" in st["flags"])
    check("the coalition fires its report", st["captured"] == ["shx_campaign.5"],
          str(st["captured"]))
    check("the coalition cannot be entered twice",
          not decision_visible("shx_join_the_coalition", st))
    check("the coalition is the design's once-per-campaign row",
          get(decisions()["shx_join_the_coalition"], "fire_only_once") == "yes")
    # the new rows must not mint power, manpower or equipment
    new_rows = ("shx_enact_the_statute", "shx_join_the_coalition",
                "shx_buy_back_the_concession")
    for name in new_rows:
        node = decisions().get(name)
        check("the band owns the row %s" % name, node is not None, str(sorted(decisions())))
        body = get(node, "complete_effect") or []
        flat = [k for k, v in walk_pairs(body)] if body else []
        for banned in ("add_political_power", "add_manpower", "add_equipment_to_stockpile"):
            check("%s does not mint %s" % (name, banned), banned not in flat, str(flat))


def scenario_squeeze_event():
    opts = options("shx_campaign.4")
    check("the squeeze offers two answers", len(opts) == 2, str(sorted(opts)))
    grant = opts["shx_campaign.4.a"]
    refuse = opts["shx_campaign.4.b"]
    check("the grant carries an AI chance",
          ai_weight(get(grant, "ai_chance"), new_state()) == CONST["ai_nanjing_concession"])
    check("the refusal carries an AI chance",
          ai_weight(get(refuse, "ai_chance"), new_state()) == CONST["ai_nanjing_refusal"])
    st = released("1930.1.1")
    run(SRC.effects, [(k, v) for k, v in grant if k not in ("ai_chance", "name")], st)
    check("granting the concession adds its spirit", "shx_japanese_concession" in st["ideas"],
          str(st["ideas"]))
    check("granting the concession marks it", "shx_concession_granted" in st["flags"])
    st2 = released("1930.1.1")
    run(SRC.effects, [(k, v) for k, v in refuse if k not in ("ai_chance", "name")], st2)
    check("refusing costs cohesion and adds no spirit",
          st2["vars"]["warlord_cohesion"] < 55 and st2["ideas"] == set(),
          str((st2["vars"]["warlord_cohesion"], st2["ideas"])))
    check("refusing does not set the grant flag", "shx_concession_granted" not in st2["flags"])
    # the buy-back row exists only after the grant
    check("the buy-back row is hidden before the grant",
          not decision_visible("shx_buy_back_the_concession", st2))
    check("the buy-back row is available after the grant",
          decision_visible("shx_buy_back_the_concession", st))
    pp = st["pp"]
    player_take("shx_buy_back_the_concession", st)
    check("the buy-back removes the concession", "shx_japanese_concession" not in st["ideas"])
    check("the buy-back clears its own row",
          not decision_visible("shx_buy_back_the_concession", st))
    check("the buy-back is paid for in political power",
          get(decisions()["shx_buy_back_the_concession"], "cost") == "@buyback_cost",
          str(get(decisions()["shx_buy_back_the_concession"], "cost")))


def scenario_focus_rewards():
    prizes = {
        "SHX_answers_nanjing": ("pp", 0),
        "SHX_nominal_submission": ("pp", 0),
        "SHX_real_submission": ("xp", 0),
        "SHX_autonomy_statute": ("ops", 0),
        "SHX_the_charter": ("pp", 0),
        "SHX_nanjing_command": ("cp", 0),
        "SHX_northern_arsenal": ("ops", 0),
        "SHX_the_squeeze": ("pp", 0),
        "SHX_garrison_reform": ("equipment", 0),
        "SHX_the_decade_closes": ("pp", 0),
    }
    tree = focuses()
    for focus_id, node in tree.items():
        st = released("1930.1.1")
        reward = get(node, "completion_reward")
        run(SRC.effects, reward, st)
        changed = (st["pp"] != 400 or st["xp"] != 100 or st["cp"] != 100
                   or st["equipment"] != 5000 or st["stability"] != 0.5
                   or st["vars"]["warlord_cohesion"] != 55
                   or any(op.startswith("state:") for op in st["ops"]))
        check("%s pays something a player can see" % focus_id, changed, str(st["ops"]))
        check("%s carries an AI weight" % focus_id,
              get(node, "ai_will_do") is not None
              and val(get(get(node, "ai_will_do"), "factor", "0")) > 0)
        check("%s costs a duration" % focus_id, get(node, "cost") is not None)
        check("%s names a sprite" % focus_id,
              str(get(node, "icon", "")).startswith("GFX_"))
        check("%s is either the root or has a prerequisite" % focus_id,
              focus_id == "SHX_answers_nanjing" or bool(getall(node, "prerequisite")))
    check("every focus in the prizes table exists",
          sorted(prizes) == sorted(tree), str(sorted(set(prizes) ^ set(tree))))
    # the two answers cannot both be taken
    check("the submission answers exclude each other",
          get(tree["SHX_nominal_submission"], "mutually_exclusive") is not None
          and get(tree["SHX_real_submission"], "mutually_exclusive") is not None)
    # the charter pays more once it is written
    st = released("1930.1.1")
    run(SRC.effects, get(tree["SHX_the_charter"], "completion_reward"), st)
    plain = st["vars"]["warlord_cohesion"]
    st2 = released("1930.1.1")
    st2["flags"]["shx_autonomy_charter"] = st2["day"]
    run(SRC.effects, get(tree["SHX_the_charter"], "completion_reward"), st2)
    check("the statute chamber pays more for a written statute",
          st2["vars"]["warlord_cohesion"] > plain,
          "%s then %s" % (plain, st2["vars"]["warlord_cohesion"]))


def scenario_sprites():
    registered = set()
    for root in [os.path.join(MOD, "interface")] + [
            os.path.join(d, "interface") for d in game_dirs()]:
        for base, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".gfx"):
                    continue
                with open(os.path.join(base, name), "r", encoding="utf-8-sig",
                          errors="replace") as fh:
                    registered |= set(re.findall(r'name\s*=\s*"([^"]+)"', fh.read()))
    check("the sprite census found the installed interface", len(registered) > 1000,
          "only %d sprite names" % len(registered))
    icons = set(re.findall(r"icon = (GFX_[A-Za-z0-9_]+)", SRC.text[TREE]))
    check("the tree names at least one icon", bool(icons))
    for icon in sorted(icons):
        check("sprite %s is registered" % icon, icon in registered, icon)
    ideas = get(get(parse(SRC.text[IDEAS]), "ideas"), "country")
    for idea_id, node in ideas:
        picture = get(node, "picture")
        if picture:
            check("idea sprite GFX_idea_%s is registered" % picture,
                  "GFX_idea_" + picture in registered, picture)


def game_dirs():
    env = os.environ.get("HOI4_GAME")
    candidates = [env] if env else []
    candidates += [
        r"C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV",
        r"C:/Program Files/Steam/steamapps/common/Hearts of Iron IV",
        r"D:/Steam/steamapps/common/Hearts of Iron IV",
        r"E:/Steam/steamapps/common/Hearts of Iron IV",
    ]
    return [c for c in candidates if c and os.path.isdir(os.path.join(c, "interface"))]


def scenario_constants():
    readers = {}
    for rel in OWNED:
        if not rel.endswith(".txt") or rel == CONSTANTS:
            continue
        for key in re.findall(r"constant:shx_story\.([a-z0-9_]+)", SRC.text[rel]):
            readers[key] = readers.get(key, 0) + 1
    for key in sorted(CONST):
        check("constant %s has a reader" % key, readers.get(key, 0) > 0)
    for key in sorted(CONST):
        if "cost" in key or "drained" in key:
            check("cost constant %s is negative" % key, CONST[key] < 0, str(CONST[key]))
    for rel in OWNED:
        if not rel.endswith(".txt"):
            continue
        text = SRC.text[rel]
        code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
        declared = set(re.findall(r"^\s*@([a-z0-9_]+)\s*=", code, re.M))
        for used in sorted(set(re.findall(r"(?<![\w.])@([a-z0-9_]+)", code))):
            check("macro @%s is declared in %s" % (used, rel), used in declared, used)
        for used in sorted(set(re.findall(r"constant:shx_story\.([a-z0-9_]+)", code))):
            check("constant %s resolves in %s" % (used, rel), used in CONST, used)


def scenario_flags_and_loc():
    writes, reads = set(), set()
    for rel in OWNED:
        if not rel.endswith(".txt"):
            continue
        text = SRC.text[rel]
        writes |= set(re.findall(r"set_country_flag\s*=\s*([a-zA-Z0-9_]+)", text))
        reads |= set(re.findall(r"has_country_flag\s*=\s*([a-zA-Z0-9_]+)", text))
        reads |= set(re.findall(r"flag\s*=\s*([a-zA-Z0-9_]+)", text))
    for flag in sorted(writes):
        check("flag %s has a reader" % flag, flag in reads)
    for flag in sorted(NEW_FLAGS):
        check("new flag %s is written" % flag, flag in writes, str(sorted(writes)))
    loc = "".join(SRC.text[rel] for rel in LOC)
    defined = set(re.findall(r"^\s*([A-Za-z0-9_.]+):", loc, re.M))
    referenced = set()
    tree = focuses()
    referenced |= set(tree) | {f + "_desc" for f in tree}
    for rel in ("common/national_focus/shx_rise.txt", "common/national_focus/shx_wars.txt"):
        ids = set(re.findall(r"id = (SHX_[a-z_]+)", SRC.text[rel]))
        referenced |= ids | {i + "_desc" for i in ids}
        referenced |= set(re.findall(r"name = (shx_[a-z_]+_navigation)", SRC.text[rel]))
    referenced |= {"shx_provincial_command", "shx_provincial_command_desc"}
    referenced |= set(decisions()) | {d + "_desc" for d in decisions()}
    referenced |= {"shx_nanjing_government", "shx_nanjing_government_desc"}
    for event_id in events():
        referenced |= {event_id + ".t", event_id + ".d"}
    referenced |= set(re.findall(r"name = (shx_campaign\.\d+\.[a-z])", SRC.text[EVENTS]))
    ideas = get(get(parse(SRC.text[IDEAS]), "ideas"), "country")
    for idea_id, _ in ideas:
        referenced |= {idea_id, idea_id + "_desc"}
    referenced |= set(re.findall(r"name = (shx_[a-z_]+_navigation)", SRC.text[TREE]))
    for rel in (DECISIONS, EVENTS):
        referenced |= set(re.findall(r"tooltip = (shx_tt_[a-z_]+)", SRC.text[rel]))
    for rel in (TREE, DECISIONS, EVENTS):
        referenced |= set(re.findall(r"name = (shx_campaign\.\d+\.[a-z])", SRC.text[rel]))
    for key in sorted(referenced):
        check("localisation key %s is defined" % key, key in defined)
    for key in sorted(defined):
        if key == "l_english":
            continue
        base = key[:-5] if key.endswith("_desc") else key
        check("localisation key %s is referenced" % key, key in referenced or base in referenced)
    # player text must not carry formatting glyphs or flag names
    for key, value in sorted(loc_values().items()):
        check("%s has no colour code" % key, "\u00a7" not in value and "\u00a3" not in value, value)
        check("%s names no raw flag" % key, not re.search(r"\bshx_[a-z_]+\b", value), value)
    for rel in LOC:
        data = raw(rel)
        check("%s keeps its byte-order mark" % rel, data.startswith(b"\xef\xbb\xbf"), rel)


NEW_FLAGS = ("shx_band_nanjing", "shx_autonomy_charter", "shx_nanjing_squeeze_seen",
             "shx_concession_granted", "shx_coalition_lost")


def scenario_events():
    ev = events()
    check("the namespace is declared once",
          SRC.text[EVENTS].count("add_namespace = shx_campaign") == 1)
    check("the slice-1 events are intact", sorted(ev) ==
          ["shx_campaign.1", "shx_campaign.2", "shx_campaign.3", "shx_campaign.4",
           "shx_campaign.5"], str(sorted(ev)))
    for event_id, node in ev.items():
        check("%s is triggered only" % event_id, get(node, "is_triggered_only") == "yes")
        check("%s has a title and a description" % event_id,
              get(node, "title") and get(node, "desc"))
        check("%s has a picture" % event_id, bool(get(node, "picture")))
    for name, node in options("shx_campaign.4").items():
        check("%s carries an AI chance" % name, get(node, "ai_chance") is not None)
    # the decision that loses the coalition is the only writer of its report event
    check("the coalition report is called from the coalition decision",
          "id = shx_campaign.5" in SRC.text[DECISIONS])


def scenario_ai_plan():
    plan = get(get(parse(SRC.text[PLAN]), "SHX_nanjing_plan"), "ai_national_focuses", [])
    order = [v for k, v in plan]
    check("the third band has an AI plan", bool(order), str(order))
    tree = focuses()
    for focus_id in order:
        check("the plan's %s exists in the tree" % focus_id, focus_id in tree, str(sorted(tree)))
    node = get(parse(SRC.text[PLAN]), "SHX_nanjing_plan")
    check("the plan is enabled by the band flag",
          get(get(node, "enable"), "has_country_flag") == "shx_band_nanjing")
    check("the plan aborts when the tree is gone",
          get(get(get(node, "abort"), "NOT"), "has_focus_tree") == "shx_nanjing")
    st = released("1930.1.1")
    check("the AI takes the statute line before the squeeze",
          order.index("SHX_the_charter") < order.index("SHX_the_squeeze"), str(order))
    check("the squeeze event's grant is weighted above its refusal",
          CONST["ai_nanjing_concession"] > CONST["ai_nanjing_refusal"])


def scenario_debt_and_tiers():
    st = new_state()
    for _ in range(5):
        run(SRC.effects, SRC.effects["shx_add_debt"], st)
    check("the debt cap still holds", st["vars"]["warlord_patronage_debt"] == 3,
          str(st["vars"]["warlord_patronage_debt"]))
    st = new_state()
    st["vars"]["warlord_cohesion"] = 90
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("the devoted tier still publishes its spirit",
          st["ideas"] == {"warlord_cohesion_devoted"}, str(st["ideas"]))
    check("the third tier is the steady band",
          trig(SRC.triggers, SRC.triggers["shx_cohesion_tier_three"],
               new_state(vars={"warlord_cohesion": 55, "warlord_patronage_debt": 0}))
          and not trig(SRC.triggers, SRC.triggers["shx_cohesion_tier_three"],
                       new_state(vars={"warlord_cohesion": 54, "warlord_patronage_debt": 0})))


def scenario_tier_three():
    """Tier three is the steady band and everything above it. The brittle band sits between the
    fractious and the steady bands, so a gate written as its negation would trade the middle tier
    for the bottom one."""
    meter = [0, 10, 20, 29, 30, 40, 54, 55, 56, 70, 79, 80, 95, 100]
    for value in meter:
        st = new_state(vars={"warlord_cohesion": value, "warlord_patronage_debt": 0})
        open_gate = trig(SRC.triggers, SRC.triggers["shx_cohesion_tier_three"], st)
        check("tier three at cohesion %d" % value, open_gate == (value > 54), str(open_gate))
    # the gate is the union of the two published tiers, so the spirit and the gate cannot disagree
    for value in meter:
        st = new_state(vars={"warlord_cohesion": value, "warlord_patronage_debt": 0})
        run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
        published = st["ideas"] & {"warlord_cohesion_steady", "warlord_cohesion_devoted"}
        open_gate = trig(SRC.triggers, SRC.triggers["shx_cohesion_tier_three"], st)
        check("tier three agrees with the published spirit at cohesion %d" % value,
              open_gate == bool(published), str(sorted(st["ideas"])))
    # the two weighty rows are shut to a province that is brittle or worse
    for value, expected in ((0, False), (10, False), (29, False), (30, False),
                            (54, False), (55, True), (56, True), (80, True)):
        st = released("1930.1.1")
        st["flags"]["shx_band_nanjing"] = st["day"]
        st["vars"]["warlord_cohesion"] = value
        run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
        check("the statute row at cohesion %d is %s" % (value, "open" if expected else "shut"),
              decision_visible("shx_enact_the_statute", st) == expected, str(sorted(st["ideas"])))
    for value, expected in ((0, False), (10, False), (29, False), (30, False),
                            (54, False), (55, True), (56, True), (80, True)):
        st = released("1930.1.1")
        st["flags"]["shx_band_nanjing"] = st["day"]
        st["flags"]["shx_autonomy_charter"] = st["day"]
        st["vars"]["warlord_cohesion"] = value
        run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
        check("the coalition row at cohesion %d is %s" % (value, "open" if expected else "shut"),
              decision_visible("shx_join_the_coalition", st) == expected, str(sorted(st["ideas"])))
        check("the band panel is drawn at cohesion %d" % value,
              category_visible("shx_nanjing_government", st))


def scenario_handover_concession():
    """The concession's only exit is a row in a panel that closes at 1936, so the spirit must not
    outlive the panel: a modifier no screen can lift is a penalty, not a mechanism."""
    st = released("1935.6.1")
    tick(st)
    check("1935.6.1 is still the Nanjing band", st["tree"] == "shx_nanjing", str(st["tree"]))
    st["ideas"].add("shx_japanese_concession")
    st["flags"]["shx_concession_granted"] = st["day"]
    st["flags"]["shx_autonomy_charter"] = st["day"]
    st["flags"]["shx_coalition_lost"] = st["day"]
    st["flags"]["shx_nanjing_squeeze_seen"] = st["day"]
    check("the panel offers the buy-back before the handover",
          category_visible("shx_nanjing_government", st)
          and decision_visible("shx_buy_back_the_concession", st), str(sorted(st["flags"])))
    st["day"] = dated("1936.1.1")
    st["ops"] = []
    tick(st)
    check("the handover lifts the northern concession",
          "shx_japanese_concession" not in st["ideas"], str(sorted(st["ideas"])))
    check("the handover leaves no spirit behind", st["ideas"] == set(), str(sorted(st["ideas"])))
    check("the handover clears the concession flag",
          "shx_concession_granted" not in st["flags"], str(sorted(st["flags"])))
    check("the panel that owned the buy-back is closed",
          not category_visible("shx_nanjing_government", st), str(sorted(st["flags"])))
    check("the buy-back row is gone with its panel",
          not decision_visible("shx_buy_back_the_concession", st))
    check("the band's one-shot records retire with the band",
          not ({"shx_nanjing_squeeze_seen", "shx_coalition_lost", "shx_band_nanjing"}
               & set(st["flags"])), str(sorted(st["flags"])))
    check("the statute the province wrote survives the handover",
          "shx_autonomy_charter" in st["flags"], str(sorted(st["flags"])))


# --- mutants ---------------------------------------------------------------------------------
def mutate(rel, old, new):
    txt = read(rel)
    if old not in txt:
        raise AssertionError("mutant anchor not found in %s: %s" % (rel, old[:60]))
    return {rel: txt.replace(old, new, 1)}


def expect_mutant(name, mutation, scenario):
    src = Source(mutation)
    global SRC, CONST
    keep, keep_const = SRC, CONST
    SRC = src
    CONST = load_constants(SRC.text[CONSTANTS])
    try:
        before = len(FAILURES)
        raised = False
        try:
            scenario()
        except (AssertionError, KeyError, ValueError, TypeError):
            raised = True
        produced = FAILURES[before:]
        del FAILURES[before:]
        caught = raised or bool(produced)
        if not caught:
            FAILURES.append(name + " mutant was not caught")
        CHECKS[0] += 1
        if DETAIL:
            print(("ok   " if caught else "FAIL ") + name + " mutant")
        return caught
    finally:
        SRC, CONST = keep, keep_const


def mutants():
    # 1. A band opened twice: the flag guard is what makes the second load impossible.
    mut = mutate(EFFECTS,
                 """				if = {
					limit = { NOT = { has_country_flag = shx_band_nanjing } }
					shx_open_nanjing = yes
				}""",
                 """				if = {
					limit = { always = yes }
					shx_open_nanjing = yes
				}""")
    expect_mutant("band opened twice", mut, scenario_one_tree)

    # 2. A coalition that can be replayed for a second helping.
    mut = mutate(TRIGGERS,
                 """	NOT = { has_country_flag = shx_coalition_lost }
	NOT = { has_war = yes }
	shx_cohesion_tier_three = yes
}""",
                 """	NOT = { has_war = yes }
	shx_cohesion_tier_three = yes
}""")
    mut.update(mutate(DECISIONS,
                      """		cost = @coalition_cost
		fire_only_once = yes""",
                      """		cost = @coalition_cost
		fire_only_once = no"""))
    expect_mutant("coalition replayed", mut, scenario_coalition)

    # 3. A statute flag nobody reads: the writer keeps its own name, the readers do not.
    mut = mutate(DECISIONS,
                 "			set_country_flag = shx_autonomy_charter",
                 "			set_country_flag = shx_autonomy_charter_written")
    expect_mutant("charter flag unread", mut, scenario_flags_and_loc)

    # 4. A routing gap at 1928: the war band keeps the decade the Nanjing band should own.
    mut = mutate(EFFECTS, "limit = { date < 1928.1.1 }", "limit = { date < 1929.1.1 }")
    expect_mutant("routing gap at 1928", mut, scenario_routing)

    # 5. A third-tier gate written as the negation of the brittle band. The brittle band is
    # bounded on both sides, so its complement admits the fractious province below 30.
    mut = mutate(TRIGGERS,
                 "shx_cohesion_tier_three = {\n\tOR = {\n\t\tshx_cohesion_steady = yes\n"
                 "\t\tshx_cohesion_devoted = yes\n\t}\n}",
                 "shx_cohesion_tier_three = {\n\tNOT = { shx_cohesion_brittle = yes }\n}")
    expect_mutant("tier three admits the fractious band", mut, scenario_tier_three)

    # 6. A concession the handover leaves behind: the spirit outlives the panel that lifts it.
    mut = mutate(EFFECTS,
                 "warlord_cohesion_steady warlord_cohesion_devoted shx_japanese_concession }",
                 "warlord_cohesion_steady warlord_cohesion_devoted }")
    expect_mutant("concession survives the handover", mut, scenario_handover_concession)


def main():
    scenario_routing()
    scenario_one_tree()
    scenario_handover()
    scenario_squeeze()
    scenario_charter()
    scenario_coalition()
    scenario_squeeze_event()
    scenario_focus_rewards()
    scenario_sprites()
    scenario_constants()
    scenario_flags_and_loc()
    scenario_events()
    scenario_ai_plan()
    scenario_debt_and_tiers()
    scenario_tier_three()
    scenario_handover_concession()
    mutants()
    print("\n%d checks, %d failures" % (CHECKS[0], len(FAILURES)))
    for f in FAILURES:
        print("  FAIL " + f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
