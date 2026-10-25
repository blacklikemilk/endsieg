"""Audit actual file names without relying on the host's case-insensitive exists()."""
from pathlib import Path, PurePosixPath
import argparse, collections, hashlib, json, os, posixpath, re, zipfile, sys

ENGINE_ROOTS = ('common', 'events', 'gfx', 'history', 'interface', 'localisation', 'map', 'music', 'portraits', 'sound', 'tutorial', 'fonts', 'video')
TEXT_EXTS = {'.txt', '.gfx', '.gui', '.asset', '.map', '.mod', '.sfx', '.music', '.shader', '.fx', '.fxh', '.lua', '.fnt'}
FILE_EXTS = {'.txt', '.dds', '.tga', '.png', '.bmp', '.csv', '.mesh', '.anim', '.fx', '.fxh', '.shader', '.fnt', '.ttf', '.otf', '.ogg', '.wav', '.yml', '.gui', '.gfx', '.asset', '.sfx', '.lua', '.mp4', '.bik', '.webm'}
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|\#[^\r\n]*|\?=|!=|<=|>=|[{}=<>]|[^\s{}=<>#!]+')
OOB_KEYS = {'oob', 'set_oob', 'load_oob', 'set_air_oob', 'set_naval_oob'}
SENTINELS = {'', 'none', 'empty'}
def hashfile(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
def inventory(root):
    out = {}
    for folder in ENGINE_ROOTS:
        top = root / folder
        if not top.is_dir(): continue
        for base, dirs, names in os.walk(top):
            for name in names:
                p = Path(base) / name
                out[p.relative_to(root).as_posix()] = p
    for p in root.iterdir():
        if p.is_file() and p.suffix.lower() in {'.mod', '.png'}: out[p.name] = p
    return out

def run(repo, game, out):
    mod = inventory(repo)
    base = inventory(game)
    native = {r: {'provider': 'base', 'path': str(p)} for r, p in base.items()}
    archives = []
    for p in (game / 'dlc').rglob('*.zip'):
        try:
            with zipfile.ZipFile(p) as z:
                count = 0
                for info in z.infolist():
                    rel = info.filename.replace('\\', '/')
                    if info.is_dir() or rel.split('/')[0] not in ENGINE_ROOTS: continue
                    if rel not in native: native[rel] = {'provider': 'dlc', 'archive': p.relative_to(game).as_posix()}
                    count += 1
                archives.append({'file': p.relative_to(game).as_posix(), 'entries': count})
        except zipfile.BadZipFile: archives.append({'file': str(p), 'error': 'bad_zip'})
    # DLC loose assets, if any, are stored with a game-root-relative subpath.
    for dlc_root in ('dlc', 'integrated_dlc'):
        if not (game / dlc_root).is_dir(): continue
        for folder in (game / dlc_root).iterdir():
            if not folder.is_dir(): continue
            for rel, p in inventory(folder).items():
                if rel.split('/')[0] in ENGINE_ROOTS and rel not in native:
                    native[rel] = {'provider': dlc_root + '_loose', 'path': str(p)}
    descriptor = (repo / 'descriptor.mod').read_text(encoding='utf-8-sig')
    replaces = re.findall(r'(?m)^\s*replace_path\s*=\s*"([^"\r\n]+)"', descriptor)
    def hidden(rel):
        return any(rel.startswith(p + '/') for p in replaces)
    merged = {rel: src for rel, src in native.items() if not hidden(rel)}
    for rel in mod: merged[rel] = {'provider': 'mod'}
    folded = collections.defaultdict(set)
    for rel in merged: folded[rel.casefold()].add(rel)
    mod_folded = collections.defaultdict(set)
    for rel in mod: mod_folded[rel.casefold()].add(rel)
    native_folded = collections.defaultdict(set)
    for rel in native: native_folded[rel.casefold()].add(rel)
    collisions = {k: sorted(v) for k, v in mod_folded.items() if len(v) > 1}
    override_cases = []
    for rel in mod:
        matches = native_folded.get(rel.casefold(), set())
        if matches and rel not in matches:
            override_cases.append({'mod_file': rel, 'native_files': sorted(matches), 'replacement_directory': hidden(rel), 'same_bytes_as_base': any(r in base and mod[rel].read_bytes() == base[r].read_bytes() for r in matches)})

    references, errors, encoding, sentinels = [], [], [], []
    parsed_files = 0
    for rel, p in sorted(mod.items()):
        if p.suffix.lower() not in TEXT_EXTS: continue
        raw = p.read_bytes()
        try: s = raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            encoding.append({'file': rel, 'problem': 'non_utf8'})
            s = raw.decode('cp1252', errors='replace')
        parsed_files += 1
        tokens = [m for m in TOKEN.finditer(s) if not m.group().startswith('#')]
        refs_here = set()
        # Tokens preserve literal offsets. Comments and localisation prose are excluded.
        for i in range(2, len(tokens)):
            m = tokens[i]
            if tokens[i-1].group() != '=': continue
            key = tokens[i-2].group()
            if key in {'replace_path', 'path', 'archive', 'dependencies'} and rel.endswith('.mod'): continue
            token = m.group()
            if token in ('{', '}'): continue
            value = token[1:-1] if token.startswith('"') and token.endswith('"') else token
            clean = value.replace('\\', '/')
            target = None
            if key in OOB_KEYS:
                if clean.casefold() in SENTINELS:
                    sentinels.append({'source': rel, 'line': s.count('\n', 0, m.start()) + 1, 'key': key, 'value': value})
                    continue
                target = 'history/units/' + clean + ('' if clean.lower().endswith('.txt') else '.txt')
            elif clean.startswith('countries/'):
                target = 'common/' + clean
            elif clean.split('/')[0].lower() in ENGINE_ROOTS and '/' in clean:
                target = clean
            elif rel == 'descriptor.mod' and key == 'picture':
                target = clean
            elif rel == 'map/default.map' and PurePosixPath(clean).suffix.lower() in FILE_EXTS:
                target = 'map/' + clean
            elif key.lower() in {'file', 'texturefile', 'meshfile', 'animationfile', 'filename', 'diffusefile', 'normalfile', 'specularfile'} and PurePosixPath(clean).suffix.lower() in FILE_EXTS:
                target = str(PurePosixPath(rel).parent / clean)
            elif key == 'Includes':
                # Multi-value shader include lists are handled separately below.
                continue
            if not target or any(c in target for c in '$[]') or target.startswith(('http:', 'https:')): continue
            sourcepos = m.start() + (1 if token.startswith('"') else 0)
            signature = (sourcepos, target)
            if signature in refs_here: continue
            refs_here.add(signature)
            raw_target = target
            target = posixpath.normpath(target.lstrip('/'))
            # Shader effectFile historically uses .lua names for .shader implementations,
            # including in the current native files. This is an engine alias, not a typo.
            if key.lower() == 'effectfile' and target.lower().endswith('.lua'):
                target = target[:-4] + '.shader'
            exact = target in merged
            row = {'source': rel, 'line': s.count('\n', 0, m.start()) + 1, 'key': key, 'value': value, 'target': target, 'start': sourcepos, 'end': m.end() - (1 if token.startswith('"') else 0), 'exact': exact}
            if exact: row['provider'] = merged[target]['provider']
            else:
                row['case_matches'] = sorted(folded.get(target.casefold(), set()))
                row['status'] = 'case_mismatch' if row['case_matches'] else 'missing'
                errors.append(row)
            if '\\' in value: row['backslash'] = True
            if '\\' in value or '//' in value or value.startswith('/'):
                row['noncanonical_separators'] = True
            references.append(row)

    result = {
        'repo': str(repo), 'game_reference': str(game), 'mod_files': len(mod), 'native_files': len(native), 'native_archives': archives,
        'text_files_scanned': parsed_files, 'reference_count': len(references),
        'case_mismatches': [r for r in errors if r['status'] == 'case_mismatch'],
        'missing': [r for r in errors if r['status'] == 'missing'],
        'backslash_references': [r for r in references if r.get('backslash')],
        'separator_references': [r for r in references if r.get('noncanonical_separators')],
        'mod_case_collisions': collisions, 'native_override_case_mismatches': override_cases,
        'encoding': encoding, 'oob_sentinels': sentinels, 'references': references,
        'limits': ['Filename matching uses exact dictionary keys even on a Windows host.', 'Native data comes from the installed Windows game, including optional DLC asset archives, not a Linux depot.', 'No game or renderer execution; unknown dynamic paths are not evaluated.', 'A missing bare model/animation filename can use engine search semantics and requires manual review.', 'Shader include lists and mesh-internal material names need separate review.'],
    }
    dump(out, result)
    print(json.dumps({k: len(result[k]) if isinstance(result[k], (list, dict)) else result[k] for k in ('mod_files', 'native_files', 'text_files_scanned', 'reference_count', 'case_mismatches', 'missing', 'backslash_references', 'mod_case_collisions', 'native_override_case_mismatches', 'encoding')}, indent=2))
    return result

if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    a.add_argument('--game-root', type=Path, required=True)
    a.add_argument('--report', type=Path, required=True)
    a.add_argument('--strict-case', action='store_true', help='Exit with status 1 for case mismatches, case-only native overrides or colliding mod paths. Unresolved optional/base-game references remain diagnostic.')
    args = a.parse_args()
    if not (args.repo / 'descriptor.mod').is_file(): a.error('--repo must contain descriptor.mod')
    if not (args.game_root / 'common').is_dir(): a.error('--game-root must contain the installed game common directory')
    result = run(args.repo.resolve(), args.game_root.resolve(), args.report.resolve())
    if args.strict_case and (result['case_mismatches'] or result['mod_case_collisions'] or result['native_override_case_mismatches']):
        sys.exit(1)
