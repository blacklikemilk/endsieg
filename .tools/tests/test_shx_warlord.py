#!/usr/bin/env python3
"""Execute the shipped Shanxi warlord source against a small model of the engine.

This is not an engine. It parses the real mod files and runs a deliberately narrow subset of
Clausewitz: if/else_if/else, variables, clamps, flags, idea adds and removes, focus-tree loads and
the effects this slice owns. Every other effect is recorded as an opaque op so a mutation still
changes the outcome instead of being silently ignored.

Run: python .tools/tests/test_shx_warlord.py [--detail]
Exit code 0 when every case, mutant and census passes.
"""
import os
import re
import sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OWNED = [
    "common/script_constants/shx_campaign.txt",
    "common/scripted_effects/china_warlord_release.txt",
    "common/scripted_effects/shx_campaign.txt",
    "common/scripted_triggers/shx_campaign.txt",
    "common/on_actions/shx_campaign.txt",
    "common/on_actions/rch_campaign.txt",
    "common/ideas/shx_campaign.txt",
    "common/decisions/categories/shx_campaign.txt",
    "common/decisions/shx_campaign.txt",
    "events/shx_campaign.txt",
    "common/national_focus/shx_rise.txt",
    "common/national_focus/shx_wars.txt",
    "common/national_focus/shx_nanjing.txt",
    "common/ai_strategy_plans/SHX_warlord.txt",
    "localisation/english/shx_campaign_l_english.yml",
    "localisation/english/shx_campaign_events_l_english.yml",
    "localisation/english/shx_focus_l_english.yml",
]

DETAIL = "--detail" in sys.argv
FAILURES = []
CHECKS = [0]

# Effects the model does not simulate, each declared with the reason its absence cannot change an
# assertion. Anything else that reaches the model raises instead of being recorded and forgotten.
INERT = {
    "mark_focus_tree_layout_dirty",  # a redraw request; no modelled state
    "custom_effect_tooltip",  # prints a line in the decision tooltip; the text is censused separately
}

# Calls into another card's package. They are declared here with their owner so a call that is
# accidentally unknown cannot hide behind this set; their own suites cover them.
EXTERNAL = {
    "rch_campaign_tick",  # the Republic's clock, C9, covered by test_rch_succession.py
}


def check(name, cond, detail=""):
    CHECKS[0] += 1
    if not cond:
        FAILURES.append("%s %s" % (name, detail))
    if DETAIL:
        print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  " + detail))


def read(rel):
    with open(os.path.join(MOD, rel), "r", encoding="utf-8-sig", newline="") as fh:
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

    def block(depth):
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
                # a bare value inside a list block, e.g. remove_ideas = { a b c }
                items.append((None, key))
                continue
            if nxt == "=":
                pos[0] += 1
                if pos[0] >= len(toks):
                    raise ValueError("dangling = after " + key)
                val = toks[pos[0]]
                pos[0] += 1
                if val == "{":
                    items.append((key, block(depth + 1)))
                else:
                    items.append((key, val))
            elif nxt in ("<", ">", "<=", ">=", "=="):
                pos[0] += 1
                num = toks[pos[0]]
                pos[0] += 1
                items.append((key, (nxt, num)))
            else:
                raise ValueError("unmodelled token after %s: %s" % (key, nxt))
        return items

    return block(0)


def get(block, key, default=None):
    for k, v in block:
        if k == key:
            return v
    return default


def getall(block, key):
    return [v for k, v in block if k == key]


# --- constants -------------------------------------------------------------------------------
def load_constants(text):
    tree = parse(text)
    body = get(tree, "shx_story")
    consts = {}
    for k, v in body:
        if k == "schema":
            continue
        consts[k] = float(v) if "." in str(v) else int(v)
    return consts


CONST = load_constants(read("common/script_constants/shx_campaign.txt"))


def load_macros():
    """File-scoped @macros, which the engine substitutes before the model ever sees a value."""
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
        "pp": 200,
        "cp": 100,
        "xp": 100,
        "ws": 0.5,
        "stability": 0.5,
        "equipment": 5000,
        "ops": [],
        "recruited": [],
        "owns": {615: True},
        "tag_owns": {},
        "captured": [],
        "dlc": {"No Compromise, No Surrender", "Waking the Tiger"},
    }
    st.update(kw)
    return st


def dated(token):
    y, m, d = (int(x) for x in str(token).split("."))
    return y * 372 + m * 31 + d


class Source:
    def __init__(self, overrides=None):
        self.text = {}
        for rel in OWNED:
            self.text[rel] = read(rel)
        for rel, txt in (overrides or {}).items():
            self.text[rel] = txt
        self.effects = self._defs("common/scripted_effects/shx_campaign.txt")
        self.effects.update(self._defs("common/scripted_effects/china_warlord_release.txt"))
        self.triggers = self._defs("common/scripted_triggers/shx_campaign.txt")
        self.release = get(parse(self.text["common/scripted_effects/china_warlord_release.txt"]),
                           "china_release_warlord_shx")
        self.rch = parse(self.text["common/on_actions/rch_campaign.txt"])

    def _defs(self, rel):
        return {k: v for k, v in parse(self.text[rel]) if isinstance(v, list)}


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
            if not has_var(v, st):
                return False
        elif k == "has_country_flag":
            if not has_flag(v, st):
                return False
        elif k in ("custom_trigger_tooltip", "hidden_trigger"):
            # both are AND containers. The tooltip key inside a custom_trigger_tooltip is not a
            # condition, so it is dropped; everything else is one.
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
        elif k == "has_war_with":
            if v not in st["ops"]:
                return False
        elif k == "has_character":
            if v not in st["recruited"]:
                return False
        elif k == "owns_state":
            # the model keeps one country, so the scope it is asked from decides which ownership
            # set answers: the released tag's, or the province's current holder's.
            seat = int(v)
            if st.get("tag_scope"):
                return_bool = st["tag_owns"].get(seat, False)
            else:
                return_bool = st["owns"].get(seat, False)
            if not return_bool:
                return False
        elif k == "exists":
            if v not in ("yes", "true"):
                return False
        elif k == "has_dlc":
            if v.strip('"') not in st["dlc"]:
                return False
        elif k.isdigit():
            # a state scope inside a trigger, e.g. 615 = { owner = ROOT }
            if not trig(defs, v, st):
                return False
        elif re.fullmatch(r"[A-Z]{3}", k) and isinstance(v, list):
            # a country-tag scope inside a trigger, e.g. NOT = { SHX = { owns_state = 615 } }
            keep = st.get("tag_scope")
            st["tag_scope"] = k
            try:
                if not trig(defs, v, st):
                    return False
            finally:
                st["tag_scope"] = keep
        elif k == "owner":
            if not st["owns"].get(615, False):
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


def block_items(node):
    return [item for item in node if isinstance(item, list)]


def check_variable(node, st):
    pairs = dict((k, v) for k, v in node if k != "var" and k not in ("value", "compare"))
    if "var" in [k for k, v in node]:
        var = get(node, "var")
        value = val(get(node, "value"))
        compare = get(node, "compare", "equal")
        op = {"greater_than_or_equals": ">=", "less_than_or_equals": "<=",
              "greater_than": ">", "less_than": "<", "equal": "="}.get(compare, "=")
        return cmp(st["vars"].get(var, 0), op, value)
    for k, v in node:
        op, num = v
        return cmp(st["vars"].get(k, 0), op, float(num))
    return True


def has_var(node, st):
    name = node if isinstance(node, str) else get(node, "var")
    return name in st["vars"]


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


def cmp(left, op, right):
    return {"<": left < right, ">": left > right, "=": left == right,
            ">=": left >= right, "<=": left <= right}[op]


def run(defs, node, st):
    if isinstance(node, str):
        return
    items = node
    used_else = False
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
            used_else = True
            i = j
        elif key in ("else_if", "else"):
            raise ValueError("orphan " + key)
        elif key == "hidden_effect":
            run(defs, value, st)
        elif key == "meta_effect":
            run_meta(defs, value, st)
        elif key == "add_to_variable":
            var = get(value, "warlord_cohesion") and "warlord_cohesion"
            if var is None:
                var = [k for k, v in value if k not in ("var", "value")][0]
            amount = val(get(value, var))
            st["vars"][var] = st["vars"].get(var, 0) + amount
        elif key == "set_variable":
            name = [k for k, v in value if k not in ("var", "value")][0]
            st["vars"][name] = val(get(value, name))
        elif key == "clamp_variable":
            name = get(value, "var")
            lo = val(get(value, "min"))
            hi = val(get(value, "max"))
            st["vars"][name] = max(lo, min(hi, st["vars"].get(name, lo)))
        elif key == "set_country_flag":
            st["flags"][value] = st["day"]
        elif key == "clr_country_flag":
            st["flags"].pop(value, None)
        elif key == "add_ideas":
            st["ideas"].add(value)
        elif key == "remove_ideas":
            for idea in value:
                if isinstance(idea, tuple):
                    name = idea[1] if idea[0] is None else idea[0]
                else:
                    name = idea
                st["ideas"].discard(name)
        elif key == "load_focus_tree":
            st["tree"] = get(value, "tree")
            st["ops"].append("load_focus_tree:" + st["tree"])
        elif key == "country_event":
            st["captured"].append(("event", get(value, "id")))
        elif key == "transfer_state":
            seat = value[4:] if str(value).startswith("var:") else value
            seat = st["vars"].get(seat, seat) if str(value).startswith("var:") else seat
            seat = int(seat)
            st["owns"][seat] = False
            st["tag_owns"][seat] = True
        elif key == "add_state_core":
            st["ops"].append("core:%s" % value)
        elif key == "recruit_character":
            st["recruited"].append(value)
        elif key == "add_equipment_to_stockpile":
            st["equipment"] += val(get(value, "amount"))
            st["ops"].append("equipment:%s" % val(get(value, "amount")))
        elif key == "army_experience":
            st["xp"] += val(value)
            st["ops"].append("army_experience:%s" % val(value))
        elif key == "add_political_power":
            st["pp"] += val(value)
            st["ops"].append("political_power:%s" % val(value))
        elif key == "add_command_power":
            st["cp"] += val(value)
            st["ops"].append("command_power:%s" % val(value))
        elif key == "add_war_support":
            st["ws"] += val(value)
            st["ops"].append("war_support:%s" % val(value))
        elif key == "add_stability":
            st["stability"] += val(value)
            st["ops"].append("stability:%s" % val(value))
        elif key == "declare_war_on":
            st["war"] = True
            st["ops"].append("declare_war_on:" + str(get(value, "target")))
        elif key in defs:
            run(defs, defs[key], st)
        elif re.fullmatch(r"[A-Z]{3}", key) and isinstance(value, list):
            # a country-tag scope inside an effect, executed against the same model country
            keep = st.get("tag_scope")
            st["tag_scope"] = key
            try:
                run(defs, value, st)
            finally:
                st["tag_scope"] = keep
        elif key in INERT or key in EXTERNAL:
            st["ops"].append(key)
        else:
            # AC9: an unmodelled block must not pass vacuously. Add it to the model, or to INERT
            # with the reason its absence cannot change an assertion.
            raise ValueError("unmodelled effect in the shipped source: %s" % key)


def run_skip(defs, node, st, skip):
    run(defs, [(k, v) for k, v in node if k not in skip], st)


def run_meta(defs, node, st):
    text = get(node, "text")
    params = {k: v for k, v in node if k != "text"}
    raw = repr_pairs(text)
    for k, v in params.items():
        raw = raw.replace("[%s]" % k, str(v).strip('"'))
    run(defs, parse(raw), st)


def repr_pairs(node):
    if isinstance(node, str):
        return node
    out = []
    for k, v in node:
        if isinstance(v, list):
            out.append("%s = { %s }" % (k, repr_pairs(v)))
        elif isinstance(v, tuple):
            out.append("%s %s %s" % (k, v[0], v[1]))
        else:
            out.append("%s = %s" % (k, v))
    return " ".join(out)


def release_once(st):
    """Run the shipped on_daily_RCH effect body, which contains the guarded release call."""
    body = get(get(get(SRC.rch, "on_actions"), "on_daily_RCH"), "effect")
    run(SRC.effects, body, st)
    return st


def tick(st, defs=None):
    run(defs or SRC.effects, SRC.effects["shx_campaign_tick"], st)
    return st


# --- scenarios -------------------------------------------------------------------------------
def scenario_release():
    st = new_state(day=dated("1916.6.6"))
    release_once(st)
    check("release sets the Republic's flag", "china_released_shx" in st["flags"])
    check("release moves the seat",
          st["tag_owns"].get(615) is True and st["owns"][615] is False,
          str((st["owns"], st["tag_owns"])))
    check("release marks the tag", "china_warlord_released" in st["flags"])
    check("release recruits the governor once", st["recruited"] == ["SHX_yan_xishan"],
          str(st["recruited"]))
    first = st["flags"]["china_released_shx"]
    st["day"] += 1
    release_once(st)
    check("second release pass recruits nobody", st["recruited"] == ["SHX_yan_xishan"],
          str(st["recruited"]))
    check("second release pass keeps the flag date", st["flags"]["china_released_shx"] == first)

    # The shared body is the part a later warlord reuses, so it must not know Shanxi at all:
    # no tag, no seat, no per-tag flag, no character token.
    body = read("common/scripted_effects/china_warlord_release.txt")
    body = body[body.index("china_release_warlord_receive"):]
    body = body[:body.index("\n}")]
    for literal in ("SHX", "615", "china_released_shx", "SHX_yan_xishan", "meta_effect"):
        check("release body is free of the %s literal" % literal, literal not in body, body)

    # And it releases whatever seat the variable names, not the one Shanxi happens to use.
    other = new_state(day=dated("1916.6.6"))
    other["owns"][621] = True
    other["vars"]["china_release_seat"] = 621
    run(SRC.effects, SRC.effects["china_release_warlord_receive"], other)
    check("the shared body releases the seat the variable names",
          other["tag_owns"].get(621) is True and other["owns"][621] is False,
          str((other["owns"], other["tag_owns"])))
    return st


def scenario_routing():
    cases = [
        ("1916.6.5", None),
        ("1916.6.6", "shx_rise"),
        ("1920.7.13", "shx_rise"),
        ("1920.7.14", "shx_wars"),
        ("1927.12.31", "shx_wars"),
        ("1928.1.1", "shx_nanjing"),
        ("1935.12.31", "shx_nanjing"),
        ("1936.1.1", "china_warlord_sea_focus"),
    ]
    for stamp, expected in cases:
        st = new_state(day=dated(stamp))
        if stamp != "1916.6.5":
            st["flags"]["china_warlord_released"] = 0
        tick(st)
        check("routing at %s" % stamp, st["tree"] == expected, "got %s" % st["tree"])
        if stamp == "1916.6.5":
            check("nothing loads before the release flag", st["tree"] is None and not st["ideas"])
    # the handover follows the same DLC order the startup dispatcher uses
    for dlc, expected in (({"Waking the Tiger"}, "china_warlord_focus"),
                          (set(), "generic_focus")):
        st = new_state(day=dated("1936.1.1"), dlc=dlc)
        st["flags"]["china_warlord_released"] = 0
        tick(st)
        check("handover without NCNS loads %s" % expected, st["tree"] == expected,
              "got %s" % st["tree"])
    # a released province keeps exactly one tree when the tick runs repeatedly
    st = new_state(day=dated("1930.1.1"))
    st["flags"]["china_warlord_released"] = 0
    tick(st)
    loads = [op for op in st["ops"] if op.startswith("load_focus_tree")]
    st["ops"] = []
    tick(st)
    again = [op for op in st["ops"] if op.startswith("load_focus_tree")]
    check("band tree loads once", len(loads) == 1, str(loads))
    check("band tree is not reloaded on a later tick", again == [], str(again))
    return st


def scenario_handover():
    """The 1936 handover must end this slice's play, not merely stop loading its own trees."""
    st = new_state(day=dated("1935.12.31"))
    st["flags"]["china_warlord_released"] = 0
    tick(st)
    check("the last day of 1935 is still the province's own tree",
          st["tree"] == "shx_nanjing",
          str(st["tree"]))
    st["day"] = dated("1936.1.1")
    st["ops"] = []
    tick(st)
    check("1936 loads the vanilla warlord tree",
          st["tree"] == "china_warlord_sea_focus", str(st["tree"]))
    check("1936 records the handover", "shx_handover_complete" in st["flags"])
    check("1936 closes the band flags",
          "shx_band_rise" not in st["flags"] and "shx_band_wars" not in st["flags"]
          and "shx_band_nanjing" not in st["flags"],
          str(st["flags"]))
    check("1936 retires the cohesion spirits", st["ideas"] == set(), str(st["ideas"]))
    check("1936 closes the decision category",
          not trig(SRC.triggers, get(CATEGORY, "visible"), st))
    check("1936 closes the clique war",
          not trig(SRC.triggers, SRC.triggers["shx_can_declare_clique_war"], st))
    st["ops"] = []
    st["day"] = dated("1937.6.1")
    tick(st)
    check("the retired tick does nothing afterwards",
          st["ops"] == [] and st["tree"] == "china_warlord_sea_focus",
          str((st["ops"], st["tree"])))
    return st


def scenario_sprites():
    """Every icon a focus names must be a registered sprite, in this mod or the installed game."""
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
    for tree in ("common/national_focus/shx_rise.txt", "common/national_focus/shx_wars.txt"):
        icons = set(re.findall(r"icon = (GFX_[A-Za-z0-9_]+)", SRC.text[tree]))
        check("%s names at least one icon" % tree, bool(icons))
        for icon in sorted(icons):
            check("sprite %s is registered" % icon, icon in registered, icon)


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
    """No dead tuning keys, no unresolved references, no undeclared macro."""
    readers = {}
    for rel in OWNED:
        if not rel.endswith(".txt") or rel.endswith("script_constants/shx_campaign.txt"):
            continue
        for key in re.findall(r"constant:shx_story\.([a-z0-9_]+)", read(rel)):
            readers.setdefault(key, 0)
            readers[key] += 1
    for key in sorted(CONST):
        check("constant %s has a reader" % key, readers.get(key, 0) > 0)
    for rel in OWNED:
        if not rel.endswith(".txt"):
            continue
        text = read(rel)
        code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
        declared = set(re.findall(r"^\s*@([a-z0-9_]+)\s*=", code, re.M))
        for used in sorted(set(re.findall(r"(?<![\w.])@([a-z0-9_]+)", code))):
            check("macro @%s is declared in %s" % (used, rel), used in declared, used)
        for used in sorted(set(re.findall(r"constant:shx_story\.([a-z0-9_]+)", code))):
            check("constant %s resolves in %s" % (used, rel), used in CONST, used)


def scenario_refresh():
    st = new_state()
    st["vars"]["warlord_cohesion"] = 60
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("steady band applies its spirit", st["ideas"] == {"warlord_cohesion_steady"},
          str(st["ideas"]))
    st["ideas"].clear()
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("refresh restores a spirit removed elsewhere",
          st["ideas"] == {"warlord_cohesion_steady"}, str(st["ideas"]))
    st["vars"]["warlord_cohesion"] = 90
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("tier change replaces the family", st["ideas"] == {"warlord_cohesion_devoted"},
          str(st["ideas"]))
    st["vars"]["warlord_cohesion"] = 140
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("cohesion is clamped to its cap", st["vars"]["warlord_cohesion"] == 100,
          str(st["vars"]["warlord_cohesion"]))
    return st


def scenario_debt():
    st = new_state()
    for _ in range(5):
        run(SRC.effects, SRC.effects["shx_add_debt"], st)
    check("debt is capped at three", st["vars"]["warlord_patronage_debt"] == 3,
          str(st["vars"]["warlord_patronage_debt"]))
    run(SRC.effects, SRC.effects["shx_pay_debt"], st)
    check("one payment clears one favour", st["vars"]["warlord_patronage_debt"] == 2,
          str(st["vars"]["warlord_patronage_debt"]))
    return st


_DEC_ROOT = get(parse(read("common/decisions/shx_campaign.txt")), "shx_provincial_command")
DECISIONS = {k: v for k, v in _DEC_ROOT if isinstance(v, list)}
for _block in ("shx_nanjing_government",):
    for _k, _v in get(parse(read("common/decisions/shx_campaign.txt")), _block) or []:
        if isinstance(_v, list):
            DECISIONS[_k] = _v
CATEGORY = get(parse(read("common/decisions/categories/shx_campaign.txt")), "shx_provincial_command")


def decision_visible(name, st):
    node = DECISIONS[name]
    return trig(SRC.triggers, get(node, "visible"), st) and trig(
        SRC.triggers, get(node, "available"), st)


def scenario_patron():
    st = new_state(day=dated("1917.1.1"))
    st["flags"]["china_warlord_released"] = 0
    st["flags"]["shx_band_rise"] = st["day"]
    check("a patron is open before any patron is taken",
          decision_visible("shx_patron_britain", st))
    st["flags"]["warlord_patron_japan"] = st["day"]
    st["flags"]["shx_patron_taken"] = st["day"]
    st["day"] += 200
    check("a second patron is refused inside the year",
          not decision_visible("shx_patron_britain", st))
    st["day"] += 200
    check("a second patron is available after the year",
          decision_visible("shx_patron_britain", st))
    st["flags"]["shx_no_patron"] = st["day"]
    check("refusing all patrons closes the family",
          not decision_visible("shx_patron_britain", st))
    return st


def scenario_war():
    st = new_state(day=dated("1925.1.1"))
    st["flags"]["china_warlord_released"] = 0
    st["vars"]["warlord_cohesion"] = 60
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("no war at the steady band", not decision_visible("shx_declare_clique_war", st))
    st["vars"]["warlord_cohesion"] = 85
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    check("war is available at the devoted band", decision_visible("shx_declare_clique_war", st))
    st["flags"]["shx_commander_grudge"] = st["day"]
    check("a grudging commander closes the war",
          not decision_visible("shx_declare_clique_war", st))
    return st


def scenario_flags_and_loc():
    writes, reads = set(), set()
    for rel in OWNED:
        if not rel.endswith(".txt"):
            continue
        text = read(rel)
        writes |= set(re.findall(r"set_country_flag\s*=\s*([a-zA-Z0-9_]+)", text))
        reads |= set(re.findall(r"has_country_flag\s*=\s*([a-zA-Z0-9_]+)", text))
        reads |= set(re.findall(r"flag\s*=\s*([a-zA-Z0-9_]+)", text))
    for flag in sorted(writes):
        check("flag %s has a reader" % flag, flag in reads)
    loc = ""
    for rel in OWNED:
        if rel.endswith(".yml"):
            loc += read(rel)
    defined = set(re.findall(r"^\s*([A-Za-z0-9_.]+):", loc, re.M))
    referenced = set()
    focus_ids = set(re.findall(r"id = (SHX_[a-z_]+)", read("common/national_focus/shx_rise.txt")
                    + read("common/national_focus/shx_wars.txt")
                    + read("common/national_focus/shx_nanjing.txt")))
    decision_ids = set(DECISIONS)
    event_ids = set(re.findall(r"id = (shx_campaign\.\d)", read("events/shx_campaign.txt")))
    referenced |= focus_ids | {f + "_desc" for f in focus_ids}
    referenced |= decision_ids | {d + "_desc" for d in decision_ids}
    referenced |= {"shx_provincial_command", "shx_provincial_command_desc",
                   "shx_nanjing_government", "shx_nanjing_government_desc"}
    for key in event_ids:
        for suffix in (".t", ".d"):
            referenced.add(key + suffix)
    referenced |= set(re.findall(r"name = (shx_campaign\.\d+\.[a-z])",
                                read("events/shx_campaign.txt")))
    reference_ideas = get(parse(read("common/ideas/shx_campaign.txt")), "ideas")
    idea_block = get(reference_ideas, "country")
    for idea_id, _ in idea_block:
        referenced.add(idea_id)
        referenced.add(idea_id + "_desc")
    referenced |= set(re.findall(r"name = (shx_[a-z_]+_navigation)",
                                 read("common/national_focus/shx_rise.txt")
                                 + read("common/national_focus/shx_wars.txt")
                                 + read("common/national_focus/shx_nanjing.txt")))
    referenced |= set(re.findall(r"tooltip = (shx_tt_[a-z_]+)",
                                 read("common/decisions/shx_campaign.txt")))
    for key in sorted(referenced):
        check("localisation key %s is defined" % key, key in defined)
    for key in sorted(defined):
        if key == "l_english":
            continue
        base = key[:-5] if key.endswith("_desc") else key
        check("localisation key %s is referenced" % key, key in referenced or base in referenced)


# --- player actions, readouts and tooltips ---------------------------------------------------
# The variables the accepted design calls the province's mechanics. The player has to be able to
# read both of them, so both must appear in player text and not only in script.
MECHANIC_VARS = ("warlord_cohesion", "warlord_patronage_debt")


def decisions():
    """The decision blocks, parsed from the live source so a mutant is visible here."""
    root = get(parse(SRC.text["common/decisions/shx_campaign.txt"]), "shx_provincial_command")
    return {k: v for k, v in root if isinstance(v, list)}


def player_take(name, st):
    """Click a decision: it must be visible and available, then its effect body runs."""
    node = decisions()[name]
    assert trig(SRC.triggers, get(node, "visible"), st), "decision is not visible: " + name
    assert trig(SRC.triggers, get(node, "available"), st), "decision is not available: " + name
    body = get(node, "complete_effect") or get(node, "remove_effect")
    assert body is not None, "decision has no effect body: " + name
    run(SRC.effects, body, st)
    return st


def loc_values():
    out = {}
    for rel in OWNED:
        if not rel.endswith(".yml"):
            continue
        for line in SRC.text[rel].splitlines():
            m = re.match(r'\s*([A-Za-z0-9_.]+):\s*"(.*)"\s*$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def scenario_war_cost():
    """The earned war must spend its cost, not mint it, and must never be repeatable income."""
    st = new_state(day=dated("1925.1.1"))
    st["flags"]["china_warlord_released"] = 0
    st["vars"]["warlord_cohesion"] = 85
    run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
    xp, cohesion = st["xp"], st["vars"]["warlord_cohesion"]
    player_take("shx_declare_clique_war", st)
    check("the clique war spends army experience",
          st["xp"] - xp == CONST["war_cost_army_experience"] and st["xp"] < xp,
          "%s then %s" % (xp, st["xp"]))
    check("the clique war spends cohesion",
          st["vars"]["warlord_cohesion"] == cohesion + CONST["cohesion_loss_war"],
          "%s then %s" % (cohesion, st["vars"]["warlord_cohesion"]))
    check("the clique war declares the war", st["war"] is True)
    # declared again after its cooldown, it is still a cost
    for _ in range(3):
        st["day"] += 400
        st["war"] = False
        st["vars"]["warlord_cohesion"] = 100
        st["flags"].pop("shx_commander_grudge", None)
        run(SRC.effects, SRC.effects["shx_refresh_mechanics"], st)
        before = st["xp"]
        player_take("shx_declare_clique_war", st)
        check("a repeated war never grants experience", st["xp"] < before,
              "%s then %s" % (before, st["xp"]))
    return st


def scenario_cost_signs():
    """A constant named as a cost is money out. The war defect was a cost with a positive sign."""
    for key in sorted(CONST):
        if "cost" in key or "drained" in key:
            check("cost constant %s is negative" % key, CONST[key] < 0, str(CONST[key]))


def scenario_mechanic_readout():
    """Both mechanic values must be readable by the player, in text this slice owns."""
    loc = loc_values()
    for var in MECHANIC_VARS:
        holders = sorted(k for k, v in loc.items() if "[?%s" % var in v)
        check("mechanic value %s is printed in player text" % var, bool(holders), str(holders))
    for band in ("fractious", "brittle", "steady", "devoted"):
        key = "shx_band_readout_%s_desc" % band
        check("the %s readout states the cohesion value" % band,
              "[?warlord_cohesion" in loc.get(key, ""), loc.get(key, "<missing>"))
    check("the category description states both values",
          "[?warlord_cohesion" in loc.get("shx_provincial_command_desc", "")
          and "[?warlord_patronage_debt" in loc.get("shx_provincial_command_desc", ""),
          loc.get("shx_provincial_command_desc", "<missing>"))
    check("the purchase tooltip states the current debt",
          "[?warlord_patronage_debt" in loc.get("shx_tt_debt_state", ""),
          loc.get("shx_tt_debt_state", "<missing>"))
    debt_tip = loc.get("shx_tt_debt_state", "")
    check("the purchase tooltip states the political-power demand",
          str(abs(CONST["demand_power_cost_negative"])) in debt_tip, debt_tip)
    check("the purchase tooltip states the equipment demand",
          str(abs(CONST["demand_equipment_drained"])) in debt_tip, debt_tip)
    dec = decisions()
    for name in ("shx_pay_arrears", "shx_equip_commanders", "shx_grant_office"):
        inner = get(get(dec[name], "available"), "custom_trigger_tooltip")
        check("the %s row shows the debt tooltip" % name,
              isinstance(inner, list) and get(inner, "tooltip") == "shx_tt_debt_state", str(inner))
    war = loc.get("shx_tt_war_cost", "")
    check("the war tooltip states the experience it spends",
          str(abs(CONST["war_cost_army_experience"])) in war, war)
    check("the war tooltip states the cohesion it spends",
          str(abs(CONST["cohesion_loss_war"])) in war, war)


def walk_pairs(node):
    for k, v in node:
        yield k, v
        if isinstance(v, list):
            for pair in walk_pairs(v):
                yield pair


def scenario_tooltip_conditions():
    """A custom requirement tooltip with no condition inside is always true, so it lies."""
    for rel in ("common/decisions/shx_campaign.txt", "events/shx_campaign.txt"):
        for key, value in walk_pairs(parse(SRC.text[rel])):
            if key != "custom_trigger_tooltip":
                continue
            conditions = [k for k, _ in value if k != "tooltip"]
            check("%s: every custom tooltip carries a real condition" % rel, bool(conditions),
                  str(value))
    conf = get(get(decisions()["shx_host_the_conference"], "available"),
               "custom_trigger_tooltip")
    check("the conference requirement is gated on the Beijing flag",
          isinstance(conf, list) and get(conf, "has_country_flag") == "shx_paid_beijing", str(conf))


# --- AI intent -------------------------------------------------------------------------------
def ai_weight(node, st):
    """Score an ai_will_do or ai_chance block: base factor times every modifier that passes.

    Weights are scores, not selection probabilities. This asserts the gate on either side of a
    threshold; it never claims what share of a race the AI would take.
    """
    if node is None:
        raise KeyError("AI block missing")
    total = val(get(node, "factor", "1"))
    for mod in getall(node, "modifier"):
        if not isinstance(mod, list):
            raise KeyError("unmodelled AI modifier: %s" % (mod,))
        condition = [(k, v) for k, v in mod if k != "factor"]
        if condition and not trig(SRC.triggers, condition, st):
            continue
        total *= val(get(mod, "factor", "1"))
    return total


def focus_blocks(text):
    tree = get(parse(text), "focus_tree")
    return {get(node, "id"): node for key, node in tree if key == "focus"}


def event_options(text):
    out = {}
    for key, node in parse(text):
        if key != "country_event":
            continue
        for k, v in node:
            if k == "option" and isinstance(v, list):
                out[get(v, "name")] = v
    return out


def scenario_ai_weights():
    """The design's thresholds are rules, so the shipped AI blocks must be zero on the wrong side.

    AC8 names two: refuse Beijing's demand only above the threshold, take a patron only below the
    other. Both the rise tree and the 1916 demand event carry the Beijing rule, and they have to
    agree, because the focus and the popup are two answers to the same question.
    """
    focuses = focus_blocks(SRC.text["common/national_focus/shx_rise.txt"])
    options = event_options(SRC.text["events/shx_campaign.txt"])
    threshold = CONST["ai_beijing_refuse_above"]

    below = new_state()
    below["vars"]["warlord_cohesion"] = threshold - 1
    at = new_state()
    at["vars"]["warlord_cohesion"] = threshold

    refuse = get(focuses["SHX_refuse_beijing"], "ai_will_do")
    pay = get(focuses["SHX_pay_beijing"], "ai_will_do")
    check("the AI refuses Beijing at the threshold", ai_weight(refuse, at) > 0,
          str(ai_weight(refuse, at)))
    check("the AI does not refuse Beijing below the threshold", ai_weight(refuse, below) == 0,
          str(ai_weight(refuse, below)))
    check("the AI pays Beijing below the threshold", ai_weight(pay, below) > 0,
          str(ai_weight(pay, below)))
    check("the AI does not pay Beijing at the threshold", ai_weight(pay, at) == 0,
          str(ai_weight(pay, at)))

    event_refuse = get(options["shx_campaign.2.a"], "ai_chance")
    event_pay = get(options["shx_campaign.2.b"], "ai_chance")
    check("the demand is refused at the threshold", ai_weight(event_refuse, at) > 0,
          str(ai_weight(event_refuse, at)))
    check("the demand is not refused below the threshold", ai_weight(event_refuse, below) == 0,
          str(ai_weight(event_refuse, below)))
    check("the demand is paid below the threshold", ai_weight(event_pay, below) > 0,
          str(ai_weight(event_pay, below)))

    at_war = new_state()
    at_war["vars"]["warlord_cohesion"] = threshold
    at_war["war"] = True
    check("a running war suppresses the refusal", ai_weight(event_refuse, at_war) == 0,
          str(ai_weight(event_refuse, at_war)))

    patron = get(DECISIONS["shx_patron_japan"], "ai_will_do")
    ceiling = CONST["ai_patron_below"]
    high = new_state()
    high["vars"]["warlord_cohesion"] = ceiling
    low = new_state()
    low["vars"]["warlord_cohesion"] = ceiling - 1
    check("a patron is not taken at the ceiling", ai_weight(patron, high) == 0,
          str(ai_weight(patron, high)))
    check("a patron is taken below the ceiling", ai_weight(patron, low) > 0,
          str(ai_weight(patron, low)))

    # The band's order lives in the strategy plan, which is the engine's ordered focus list.
    plan = get(parse(SRC.text["common/ai_strategy_plans/SHX_warlord.txt"]), "SHX_rise_plan")
    order = [v for k, v in get(plan, "ai_national_focuses")]
    check("the rise plan takes the treasury, arsenal and compact in the design's order",
          order[:4] == ["SHX_model_province", "SHX_provincial_treasury",
                        "SHX_arsenal_expansion", "SHX_three_thirds_compact"], str(order[:4]))


# --- mutants ---------------------------------------------------------------------------------
def mutate(rel, old, new):
    txt = read(rel)
    if old not in txt:
        raise AssertionError("mutant anchor not found in %s: %s" % (rel, old[:60]))
    return {rel: txt.replace(old, new, 1)}


def expect_mutant(name, mutation, scenario, needle):
    src = Source(mutation)
    global SRC, CONST
    keep = SRC
    keep_const = CONST
    SRC = src
    # a mutant may edit the constants file, so the model's tuning is reloaded with the source
    CONST = load_constants(SRC.text["common/script_constants/shx_campaign.txt"])
    try:
        before = len(FAILURES)
        raised = False
        try:
            scenario()
        except (AssertionError, KeyError):
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
        SRC = keep
        CONST = keep_const


def mutants():
    # 1. A second patron inside the maturity window.
    mut = mutate("common/scripted_triggers/shx_campaign.txt",
                 """	OR = {
		NOT = { has_country_flag = shx_patron_taken }
		has_country_flag = { flag = shx_patron_taken days > @patron_maturity_days }
	}""",
                 """	OR = { always = yes }""")
    expect_mutant("second patron inside the window", mut, scenario_patron,
                  "a second patron is refused inside the year")

    # 2. A clique war at the steady band.
    mut = mutate("common/scripted_triggers/shx_campaign.txt",
                 "	has_idea = warlord_cohesion_devoted\n"
                 "	NOT = { has_country_flag = shx_commander_grudge }",
                 "	NOT = { has_country_flag = shx_commander_grudge }")
    expect_mutant("war at the steady band", mut, scenario_war, "no war at the steady band")

    # 3. A refresh that drops the family it was asked to publish.
    mut = mutate("common/scripted_effects/shx_campaign.txt",
                 "			remove_ideas = { warlord_cohesion_fractious warlord_cohesion_brittle warlord_cohesion_devoted }\n"
                 "			add_ideas = warlord_cohesion_steady",
                 "			remove_ideas = { warlord_cohesion_fractious warlord_cohesion_brittle warlord_cohesion_steady warlord_cohesion_devoted }")
    expect_mutant("refresh dropping the spirit", mut, scenario_refresh,
                  "steady band applies its spirit")

    # 4. A release that runs twice: no caller flag, no ownership guard, no recruit guard.
    mut = mutate("common/on_actions/rch_campaign.txt",
                 "limit = { date > 1916.6.5 NOT = { has_country_flag = china_released_shx } }",
                 "limit = { date > 1916.6.5 }")
    mut.update(mutate("common/scripted_effects/china_warlord_release.txt",
                      """		limit = {
			NOT = { has_country_flag = china_released_shx }
			owns_state = 615
			SHX = { NOT = { owns_state = 615 } }
		}""",
                      "		limit = { always = yes }"))
    rel = "common/scripted_effects/china_warlord_release.txt"
    mut[rel] = mut[rel].replace(
        """			if = {
				limit = { NOT = { has_character = SHX_yan_xishan } }
				recruit_character = SHX_yan_xishan
			}""", "			recruit_character = SHX_yan_xishan", 1)
    expect_mutant("release running twice", mut, scenario_release,
                  "second release pass recruits nobody")

    # 5. A handover that closes the bands without loading the vanilla tree.
    mut = mutate("common/scripted_effects/shx_campaign.txt",
                 """	if = {
		limit = { has_dlc = "No Compromise, No Surrender" }
		load_focus_tree = { tree = china_warlord_sea_focus keep_completed = yes }
	}
	else_if = {
		limit = { has_dlc = "Waking the Tiger" }
		load_focus_tree = { tree = china_warlord_focus keep_completed = yes }
	}
	else = {
		load_focus_tree = { tree = generic_focus keep_completed = yes }
	}""", "")
    expect_mutant("handover that loads no tree", mut, scenario_handover,
                  "1936 loads the vanilla warlord tree")

    # 6. A focus pointing at a sprite nothing registers.
    mut = mutate("common/national_focus/shx_wars.txt",
                 "icon = GFX_focus_ww1_pdx_native_shared_gen_state_claims",
                 "icon = GFX_focus_ww1_pdx_native_en1_r_neutral_trade")
    expect_mutant("focus with an unregistered sprite", mut, scenario_sprites,
                  "sprite GFX_focus_ww1_pdx_native_en1_r_neutral_trade is registered")


    # 7. A war whose "cost" is a grant.
    mut = mutate("common/script_constants/shx_campaign.txt",
                 "war_cost_army_experience = -25", "war_cost_army_experience = 25")
    expect_mutant("war that grants army experience", mut, scenario_war_cost,
                  "the clique war spends army experience")

    # 8. A requirement tooltip nobody has to meet.
    mut = mutate("common/decisions/shx_campaign.txt",
                 """\t\t\tcustom_trigger_tooltip = {
\t\t\t\ttooltip = shx_tt_paid_beijing
\t\t\t\thas_country_flag = shx_paid_beijing
\t\t\t}""",
                 "\t\t\tcustom_trigger_tooltip = { tooltip = shx_tt_paid_beijing }")
    expect_mutant("requirement tooltip without a condition", mut, scenario_tooltip_conditions,
                  "every custom tooltip carries a real condition")

    # 9. A band readout that names the band but stops printing the meter.
    mut = mutate("localisation/english/shx_campaign_l_english.yml",
                 'shx_band_readout_steady_desc: "The province stands at [?warlord_cohesion|0] of '
                 '100. The garrison',
                 'shx_band_readout_steady_desc: "The garrison')
    expect_mutant("band readout without the value", mut, scenario_mechanic_readout,
                  "the steady readout states the cohesion value")

    # 10. A refuse focus that keeps a share below the design's threshold.
    mut = mutate("common/national_focus/shx_rise.txt",
                 "\t\t\t# The design's threshold is a rule, not a preference: below it the province pays, so\n"
                 "\t\t\t# the weight is zero rather than merely smaller.\n"
                 "\t\t\tmodifier = { factor = 0 NOT = { check_variable = { var = warlord_cohesion "
                 "value = constant:shx_story.ai_beijing_refuse_above compare = greater_than_or_equals } } }\n",
                 "")
    expect_mutant("refuse focus open below the threshold", mut, scenario_ai_weights,
                  "the AI does not refuse Beijing below the threshold")

    # 11. A demand event whose refusal ignores the same threshold.
    mut = mutate("events/shx_campaign.txt",
                 "\t\t\t# The same rule the focus carries: below the threshold the province pays, so refusing\n"
                 "\t\t\t# takes no share of the roll at all.\n"
                 "\t\t\tmodifier = { factor = 0 NOT = { check_variable = { var = warlord_cohesion "
                 "value = constant:shx_story.ai_beijing_refuse_above compare = greater_than_or_equals } } }\n",
                 "")
    expect_mutant("demand refusal open below the threshold", mut, scenario_ai_weights,
                  "the demand is not refused below the threshold")

    # 12. A pay focus that competes above the threshold it is meant to be shut above.
    mut = mutate("common/national_focus/shx_rise.txt",
                 "modifier = { factor = 0 check_variable = { var = warlord_cohesion "
                 "value = constant:shx_story.ai_beijing_refuse_above compare = greater_than_or_equals } }",
                 "modifier = { factor = 3 check_variable = { var = warlord_cohesion "
                 "value = constant:shx_story.ai_beijing_refuse_above compare = greater_than_or_equals } }")
    expect_mutant("pay focus open at the threshold", mut, scenario_ai_weights,
                  "the AI does not pay Beijing at the threshold")


def main():
    scenario_release()
    scenario_routing()
    scenario_handover()
    scenario_sprites()
    scenario_constants()
    scenario_refresh()
    scenario_debt()
    scenario_patron()
    scenario_war()
    scenario_war_cost()
    scenario_cost_signs()
    scenario_mechanic_readout()
    scenario_tooltip_conditions()
    scenario_ai_weights()
    scenario_flags_and_loc()
    mutants()
    print("\n%d checks, %d failures" % (CHECKS[0], len(FAILURES)))
    for f in FAILURES:
        print("  FAIL " + f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
