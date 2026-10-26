"""Generate the late-start focus restore for the Spanish chapters.

A game that begins in 1914 should not open on a blank tree: historical Spain had already
settled the turno, the Moroccan question and the neutrality of 1914. This tool holds the
curated milestone dates and rebuilds spain_restore_past_focuses from them, with two
properties the hand-written version did not have:

  * every prerequisite is completed first, because complete_national_focus silently does
    nothing when a prerequisite is unmet;
  * the output is a function of the seeds and the trees alone, so running it twice gives
    the same file.

Run from the mod root:  python tools/build_spain_restore_schedule.py
"""

from __future__ import annotations

import io
import re
import sys

TREES = {
    'spain_chapter_restoration': 'common/national_focus/spain_restoration.txt',
    'spain_chapter_rivera': 'common/national_focus/spain_rivera.txt',
    'spain_chapter_republic': 'common/national_focus/spain_republic.txt',
    'spain_chapter_postwar': 'common/national_focus/spain_republic_postwar.txt',
}

EFFECT = 'common/scripted_effects/spain_campaign_effects.txt'

# Curated milestones: the date by which historical Spain would have finished the focus.
SEEDS = {
    'spain_chapter_restoration': [
        ('1911.6.1', 'SPR1_caciquismo'),
        ('1911.6.1', 'SPR1_labour_question'),
        ('1911.6.1', 'SPR1_state_budget'),
        ('1912.6.1', 'SPR1_the_army_question'),
        ('1912.6.1', 'SPR1_turno_politics'),
        ('1912.6.1', 'SPR1_royal_prerogative'),
        ('1912.6.1', 'SPR1_tax_reform'),
        ('1913.6.1', 'SPR1_church_and_state'),
        ('1913.6.1', 'SPR1_electoral_reform'),
        ('1913.6.1', 'SPR1_railway_gauge'),
        ('1914.8.1', 'SPR1_neutrality_in_europe'),
        ('1914.8.1', 'SPR1_juntas_de_defensa'),
        ('1914.8.1', 'SPR1_parliamentary_sovereignty'),
        ('1915.6.1', 'SPR1_conciliate_the_cnt'),
        ('1915.6.1', 'SPR1_constitutional_crisis'),
        ('1915.6.1', 'SPR1_industrial_protection'),
        ('1916.6.1', 'SPR1_civil_guard_expansion'),
        ('1916.6.1', 'SPR1_peninsular_reform'),
        ('1916.6.1', 'SPR1_german_overtures'),
        ('1916.6.1', 'SPR1_africanist_command'),
        ('1917.6.1', 'SPR1_the_general_strike'),
        ('1917.6.1', 'SPR1_wolfram_contracts'),
        ('1917.6.1', 'SPR1_catalan_textiles'),
        ('1918.6.1', 'SPR1_the_year_of_crisis'),
        ('1918.6.1', 'SPR1_allied_overtures'),
        ('1918.6.1', 'SPR1_rif_offensive'),
        ('1919.6.1', 'SPR1_rif_settlement'),
        ('1919.6.1', 'SPR1_agrarian_credit'),
        ('1919.6.1', 'SPR1_mancomunitat'),
        ('1920.6.1', 'SPR1_annual_disaster'),
        ('1920.6.1', 'SPR1_the_coup_that_waits'),
        ('1920.6.1', 'SPR1_basque_fueros'),
        ('1921.6.1', 'SPR1_the_assembly_movement'),
        ('1921.6.1', 'SPR1_the_crown_settles'),
        ('1921.6.1', 'SPR1_the_cortes_settles'),
        ('1922.6.1', 'SPR1_the_economy_settles'),
    ],
    'spain_chapter_rivera': [
        ('1924.1.1', 'SPR2_suspend_the_constitution'),
        ('1924.1.1', 'SPR2_civil_governors'),
        ('1925.1.1', 'SPR2_rule_by_decree'),
        ('1925.1.1', 'SPR2_hydraulic_confederation'),
        ('1926.1.1', 'SPR2_unione_patriotica'),
        ('1926.1.1', 'SPR2_railway_monopoly'),
        ('1927.1.1', 'SPR2_alhucemas_landing'),
        ('1927.1.1', 'SPR2_army_reorganisation'),
        ('1928.1.1', 'SPR2_the_assembly'),
        ('1928.1.1', 'SPR2_labour_corporatism'),
        ('1929.1.1', 'SPR2_constitution_of_1929'),
        ('1929.1.1', 'SPR2_syndicate_network'),
        ('1930.1.1', 'SPR2_education_programme'),
        ('1930.1.1', 'SPR2_the_king_withdraws'),
        ('1930.6.1', 'SPR2_officer_discontent'),
        ('1930.6.1', 'SPR2_the_world_crash'),
        ('1931.1.1', 'SPR2_republican_pact'),
        ('1931.1.1', 'SPR2_municipal_elections'),
        ('1931.3.1', 'SPR2_pacify_the_protectorate'),
        ('1931.3.1', 'SPR2_the_dictatorship_ends'),
    ],
    'spain_chapter_republic': [
        ('1931.6.1', 'SPR3_constituent_cortes'),
        ('1932.1.1', 'SPR3_constitution_1931'),
        ('1932.1.1', 'SPR3_public_order'),
        ('1932.6.1', 'SPR3_military_reform'),
        ('1932.9.1', 'SPR3_agrarian_reform'),
        ('1932.9.1', 'SPR3_religious_settlement'),
        ('1933.1.1', 'SPR3_secular_schools'),
        ('1933.6.1', 'SPR3_catalan_statute'),
        ('1933.6.1', 'SPR3_public_works'),
        ('1933.6.1', 'SPR3_labour_ministry'),
        ('1933.11.1', 'SPR3_elections_1933'),
        ('1934.10.1', 'SPR3_asturias_1934'),
        ('1934.11.1', 'SPR3_casas_viejas'),
        ('1935.1.1', 'SPR3_education_mission'),
        ('1935.1.1', 'SPR3_agrarian_credit'),
        ('1935.6.1', 'SPR3_gil_robles'),
        ('1935.6.1', 'SPR3_falange_founded'),
        ('1935.6.1', 'SPR3_the_falange_street'),
        ('1936.2.1', 'SPR3_the_popular_front'),
        ('1936.3.1', 'SPR3_army_union'),
        ('1936.5.1', 'SPR3_army_plot'),
        ('1936.6.1', 'SPR3_the_rising_prepared'),
    ],
    'spain_chapter_postwar': [
        ('1939.10.1', 'SPR4_the_republic_endures'),
        ('1940.1.1', 'SPR4_constitution_of_1939'),
        ('1940.6.1', 'SPR4_rebuild_the_industry'),
        ('1940.6.1', 'SPR4_railway_restoration'),
        ('1941.1.1', 'SPR4_army_of_the_republic'),
        ('1941.1.1', 'SPR4_armed_neutrality'),
        ('1942.1.1', 'SPR4_wolfram_trade'),
        ('1942.6.1', 'SPR4_the_hydroelectric_grid'),
        ('1944.1.1', 'SPR4_diplomacy_with_the_allies'),
        ('1945.1.1', 'SPR4_the_1945_settlement'),
    ],
}


def focus_graph(path: str) -> dict[str, list[list[str]]]:
    """focus id -> list of prerequisite groups (any one of each group is enough)."""
    text = io.open(path, encoding='utf-8-sig').read()
    graph: dict[str, list[list[str]]] = {}
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
        body = text[i:j + 1]
        fid = re.search(r'\bid\s*=\s*(\S+)', body)
        if not fid:
            continue
        groups = []
        for pre in re.findall(r'prerequisite\s*=\s*\{([^{}]*)\}', body):
            alts = re.findall(r'focus\s*=\s*(\S+)', pre)
            if alts:
                groups.append(alts)
        graph[fid.group(1)] = groups
    return graph


def close_and_order(entries: list[tuple[str, str]], graph: dict[str, list[list[str]]]):
    date_of = {f: d for d, f in entries}
    order = [f for _d, f in entries]
    chosen = list(order)

    changed = True
    while changed:
        changed = False
        for focus in list(chosen):
            for group in graph.get(focus, []):
                if any(alt in chosen for alt in group):
                    continue
                pick = next((alt for alt in group if alt in graph), group[0])
                if pick not in chosen:
                    chosen.append(pick)
                    date_of[pick] = date_of.get(focus, '1911.1.1')
                    changed = True

    placed, topo = set(), []
    pending = sorted(chosen, key=lambda f: (date_of[f], order.index(f) if f in order else 999))
    while pending:
        progressed = False
        for focus in list(pending):
            groups = graph.get(focus, [])
            if all(any(alt in placed for alt in group) for group in groups):
                topo.append(focus)
                placed.add(focus)
                pending.remove(focus)
                progressed = True
        if not progressed:
            topo.extend(pending)
            break

    # Dates must respect the dependency order. The effect runs top to bottom and every block
    # gates on its own date, so a prerequisite dated later than its dependent is skipped and
    # the dependent then completes nothing. Walk the topological order once and push each
    # focus to at least the earliest date its prerequisites become available on.
    for focus in topo:
        floor = date_of[focus]
        for group in graph.get(focus, []):
            available = [date_of[alt] for alt in group if alt in date_of]
            if available:
                floor = max(floor, min(available))
        date_of[focus] = floor

    rank = {f: i for i, f in enumerate(topo)}
    return sorted(((date_of[f], f) for f in topo), key=lambda row: (row[0], rank[row[1]]))


def emit_block() -> str:
    graphs = {chapter: focus_graph(path) for chapter, path in TREES.items()}
    out = ['spain_restore_past_focuses = {',
           '\t# Generated by tools/build_spain_restore_schedule.py. A late start completes the',
           '\t# milestones history had already reached, in prerequisite order, so no entry is',
           '\t# skipped by the engine. Never hand-edit: change the seeds in the tool.',
           '\t# A 1910 start completes nothing, because no date gate has passed.']
    for chapter, seeds in SEEDS.items():
        closed = close_and_order(seeds, graphs[chapter])
        out += ['\tif = {', '\t\tlimit = { has_country_flag = %s }' % chapter]
        date = None
        for d, focus in closed:
            if d != date:
                if date is not None:
                    out.append('\t\t}')
                out += ['\t\tif = {', '\t\t\tlimit = { date > %s }' % d]
                date = d
            out.append('\t\t\tcomplete_national_focus = %s' % focus)
        if date is not None:
            out.append('\t\t}')
        out += ['\t}', '']
    out.append('}')
    return '\n'.join(out)


def main() -> int:
    text = io.open(EFFECT, encoding='utf-8-sig').read()
    start = text.index('spain_restore_past_focuses = {')
    depth, j = 0, start
    while j < len(text):
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1

    block = emit_block()
    text = text[:start] + block + text[j + 1:]
    io.open(EFFECT, 'w', encoding='utf-8', newline='').write(text)
    print('wrote %d lines; completions: %d' % (block.count('\n'), block.count('complete_national_focus')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
