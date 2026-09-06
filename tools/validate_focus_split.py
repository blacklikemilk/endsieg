"""Validate the WW1/vanilla focus split without launching Hearts of Iron IV."""
from pathlib import Path
import re, json
ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[=<>!]+|[^\s{}=<>!#"]+')
def nodes(text):
    ts = [m for m in TOKEN.finditer(text) if not m[0].startswith('#')]
    def walk(i, block=False):
        out=[]
        while i < len(ts):
            if ts[i][0] == '}':
                if not block:
                    # Tolerate an existing trailing brace in the installed vanilla
                    # TSR joint branch. Copied files are checked byte-for-byte;
                    # custom early files receive a strict balance check below.
                    i+=1
                    continue
                return out,i+1
            if i+2 < len(ts) and ts[i+1][0] in ('=','<','>','<=','>=','!=','?='):
                start=ts[i].start(); key=ts[i][0]; op=ts[i+1][0]; val=ts[i+2][0]
                i+=3; children=[]
                if val == '{': children,i=walk(i,True)
                out.append(dict(key=key,op=op,value=val,start=start,end=ts[i-1].end(),children=children))
            elif ts[i][0] == '{':
                _,i=walk(i+1,True)
            else: i+=1
        if block: raise ValueError('Unclosed brace')
        return out,i
    return walk(0)[0]
def get(ns,key): return next(n for n in ns if n['key']==key)
def ident(n): return get(n['children'],'id')['value']
def defs(text):
    result=[]
    for n in nodes(text):
        if n['key'] in ('shared_focus','joint_focus') and n['value']=='{': result.append(ident(n))
        if n['key']=='focus_tree':
            result += [ident(c) for c in n['children'] if c['key']=='focus' and c['value']=='{']
    return result

def validate():
    import argparse
    import hashlib
    from collections import defaultdict
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vanilla", type=Path, help="Installed common/national_focus directory")
    args = parser.parse_args()
    folder = ROOT / "common/national_focus"
    manifest = json.loads((ROOT / "tools/focus_split_manifest.json").read_text())
    errors = []
    all_ids = defaultdict(list)
    tree_ids = defaultdict(list)
    parsed = {}
    for path in folder.glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig")
        parsed[path.name] = nodes(text)
        for focus_id in defs(text):
            all_ids[focus_id].append(path.name)
        for tree in parsed[path.name]:
            if tree["key"] == "focus_tree":
                tree_ids[ident(tree)].append(path.name)
    for label, entries in (("focus", all_ids), ("tree", tree_ids)):
        for key, files in entries.items():
            if len(files) != 1:
                errors.append(f"Duplicate {label} {key}: {files}")
    for name, digest in manifest["vanilla_files"].items():
        path = folder / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f"Vanilla copy changed: {name}")
        if args.vanilla and path.read_bytes() != (args.vanilla / name).read_bytes():
            errors.append(f"Installed vanilla differs: {name}")
    for nation, ids in manifest["ww1_focus_ids"].items():
        name = nation if nation.endswith(".txt") else f"WWI - {nation}.txt"
        actual = defs((folder / name).read_text(encoding="utf-8-sig"))
        if actual != ids:
            errors.append(f"WW1 focus content was lost or reordered: {name}")
    def walk(ns):
        for node in ns:
            yield node
            yield from walk(node["children"])
    early_files = [name for name in parsed if name.startswith(("WWI - ", "INT - ", "_shared"))]
    for name in early_files:
        depth = 0
        for token in TOKEN.finditer((folder / name).read_text(encoding="utf-8-sig")):
            if token[0] == "{":
                depth += 1
            elif token[0] == "}":
                depth -= 1
                if depth < 0:
                    errors.append(f"Unexpected closing brace: {name}")
                    break
        if depth != 0:
            errors.append(f"Unbalanced braces: {name}")
        for node in walk(parsed[name]):
            if node["value"] != "{" and node["key"] in (
                "focus", "relative_position_id", "shared_focus", "has_completed_focus",
                "complete_national_focus", "unlock_national_focus", "uncomplete_national_focus"
            ) and node["value"] not in all_ids:
                errors.append(f"Unresolved WW1 reference in {name}: {node['value']}")
        if name.startswith("WWI - ") or name.startswith("INT - RCW"):
            tree = get(parsed[name], "focus_tree")
            country = get(tree["children"], "country")
            modifier = get(country["children"], "modifier")
            score = int(get(modifier["children"], "add")["value"])
            expected = 10000 if name == "WWI - Generic.txt" else 20000
            # WW1 trees are selected by their high score; WW2 selection is
            # performed explicitly by common/on_actions/endsieg_on_actions.txt.
            if score != expected:
                errors.append(f"Wrong early-scenario selection in {name}")
            if get(country["children"], "factor")["value"] != "0":
                errors.append(f"Early tree can win in WW2: {name}")
            if get(tree["children"], "default")["value"] != "no":
                errors.append(f"Early tree is an unconditional default: {name}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(manifest['vanilla_files'])} unchanged vanilla files; "
          f"{len(all_ids)} unique focus IDs; {len(tree_ids)} unique tree IDs.")
    print("PASS: all preserved WW1 focus IDs, early-tree date/priority rules, and WW1 references.")
    print("Static validation only; scenario loading and DLC behavior still need in-game testing.")

if __name__ == "__main__":
    validate()
