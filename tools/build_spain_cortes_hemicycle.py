"""Build the Cortes chamber panel: GUI, seat frames, dot table, effects and UI text.

A parliament is read at a glance, so the chamber is drawn as a semicircle of dots rather
than a list of numbers. 100 dots carry 400 seats between them, four seats each, coloured by
the bloc that holds each dot and sweeping left to right in the political order of the
chamber. Every dot is a frame of a single sprite strip, so the frame a dot shows is the
plain country variable the draw effect wrote: an unset or stale seat reads as the neutral
frame instead of falling through to a party colour.

This script is the single source for these generated artefacts, so changing the number of
dots, the parties or the rows only means editing this file:

  interface/endsieg_spain_cortes.gui                       - window, hemicycle, legend, summary
  common/scripted_guis/spain_cortes_scripted_gui.txt       - one frame property per dot
  common/scripted_localisation/spain_cortes_panel.txt       - party role, verdict, status text
  common/scripted_localisation/spain_cortes_dots.txt        - retired, kept as a stub comment
  common/scripted_effects/spain_cortes_hemicycle.txt        - which bloc owns each dot
  localisation/english/spain_cortes_ui_l_english.yml        - every text the panel shows

The dot textures themselves come from tools/build_spain_cortes_dots.py.

Run from the mod root:  python tools/build_spain_cortes_hemicycle.py
"""

from __future__ import annotations

import io
import math
import os
import sys

# --- chamber ---------------------------------------------------------------
SEATS = 400
DOTS = 100
SEATS_PER_DOT = SEATS // DOTS          # four seats behind every dot

# --- panel geometry --------------------------------------------------------
WINDOW_W = 500
SPRITE_PX = 16                          # native size of a dot texture
DOT_SCALE = 1.25
DOT_PX = int(round(SPRITE_PX * DOT_SCALE))
R_OUTER = 238                           # 476px of the 500px panel: the chamber fills the width
CX = WINDOW_W // 2
CY = 278                                # the diameter of the semicircle, window-relative
RING_FRACTIONS = (0.40, 0.55, 0.70, 0.85, 1.00)

# padding inside the window
MARGIN = 8
TITLE_Y = 4
TITLE_H = 22
ROW_H = 18
LINE_H = 21

# --- parties, left to right ------------------------------------------------
# name, localisation key for the short legend label, spain_government_party id
PARTIES = [
    ("socialists", "SPAIN_CORTES_BLOC_SOCIALISTS", 5),
    ("republicans", "SPAIN_CORTES_BLOC_REPUBLICANS", 4),
    ("liberals", "SPAIN_CORTES_BLOC_LIBERALS", 2),
    ("conservatives", "SPAIN_CORTES_BLOC_CONSERVATIVES", 3),
    ("monarchists", "SPAIN_CORTES_BLOC_MONARCHISTS", 1),
    ("carlists", "SPAIN_CORTES_BLOC_CARLISTS", 6),
    ("falange", "SPAIN_CORTES_BLOC_FALANGE", 7),
]

# Sprite frames are 1-based: noOfFrames = 8 on GFX_spain_cortes_seats carries eight cells, addressed
# 1..8, and tools/build_spain_cortes_dots.py lays the strip out as [neutral] + PARTIES, so frame 1 is
# the neutral bench and frames 2..8 are the parties in chamber order. A seat variable that has never
# been written therefore reads as an empty bench and never as the first party colour, and the highest
# frame asked for is the last cell the strip carries, which is the only way the falange cell is
# reachable at all. Vanilla converts a 0-based index into a frame by adding one
# (common/scripted_effects/SOV_scripted_effects.txt:782) and addresses a ten-level ladder as frames
# 1..10 (common/scripted_guis/INS_revolution_scripted_gui.txt:8-46).
FRAME_EMPTY = 1


def frame_of(party_index: int) -> int:
    """1-based sprite frame for the party in position party_index, counting from the left."""
    return party_index + 1

# column x positions, shared by the legend header and its rows
COL_SWATCH = MARGIN
COL_NAME = 30
COL_SEATS = 186
COL_SHARE = 238
COL_ROLE = 296
COL_NAME_W = 150
COL_NUM_W = 44
COL_ROLE_W = WINDOW_W - MARGIN - COL_ROLE

PARTY_NAMES = {
    "socialists": "Socialists",
    "republicans": "Republicans",
    "liberals": "Liberals",
    "conservatives": "Conservatives",
    "monarchists": "Monarchists",
    "carlists": "Carlists",
    "falange": "Falange",
}


def ring_counts() -> list[int]:
    """Spread DOTS over the rings in proportion to their radius, so spacing is even.

    Arc length is proportional to radius, so one dot per equal slice of arc on every ring
    means the counts grow with the radius. Largest-remainder rounding keeps the total exact.
    """
    weights = [R_OUTER * f for f in RING_FRACTIONS]
    total = sum(weights)
    exact = [DOTS * w / total for w in weights]
    counts = [int(math.floor(v)) for v in exact]
    order = sorted(range(len(exact)), key=lambda i: exact[i] - counts[i], reverse=True)
    while sum(counts) < DOTS:
        for i in order:
            if sum(counts) >= DOTS:
                break
            counts[i] += 1
    while sum(counts) > DOTS:
        for i in reversed(order):
            if sum(counts) <= DOTS:
                break
            counts[i] -= 1
    return counts


def ring_radii() -> list[int]:
    return [int(round(R_OUTER * f)) for f in RING_FRACTIONS]


def dot_positions() -> list[tuple[int, int]]:
    """Every dot on its arc, ordered left to right around the chamber.

    Each dot sits at the centre of its own angular slice, so a ring never puts a dot on the
    diameter and the two ends of the chamber stay symmetric. Dots are then ordered by that
    angle, so consecutive dots walk the chamber from the left benches to the right ones and a
    bloc's seats form a wedge of the semicircle rather than a vertical slice. Rings that share an
    angle are ordered outward on the left half and inward on the right half, so the seat order
    stays strictly left to right and no two blocs interleave at the ends of the chamber.
    """
    radii = ring_radii()
    counts = ring_counts()
    placed: list[tuple[float, int, int, int]] = []      # (angle fraction, radius, x, y)
    for radius, count in zip(radii, counts):
        for j in range(count):
            frac = (j + 0.5) / count                    # 0.0 at the left benches, 1.0 at the right
            theta = math.pi * (1.0 - frac)
            x = CX + radius * math.cos(theta)
            y = CY - radius * math.sin(theta)
            placed.append((frac, radius, int(round(x)), int(round(y))))
    placed.sort(key=lambda p: (p[0], p[1] if p[0] < 0.5 else -p[1]))
    return [(x, y) for _frac, _radius, x, y in placed]


def dot_offsets() -> list[tuple[int, int]]:
    """Top-left corner of each dot sprite, so a dot is centred on its arc position."""
    half = DOT_PX // 2
    return [(x - half, y - half) for x, y in dot_positions()]


def seat_midpoints() -> list[int]:
    """The seat a dot stands for: the middle of its four-seat block."""
    return [int(round((i + 0.5) * SEATS / DOTS)) for i in range(DOTS)]


def layout() -> dict[str, int]:
    chamber_bottom = CY + DOT_PX // 2
    legend_header = chamber_bottom + 14
    legend_rows = legend_header + ROW_H
    legend_bottom = legend_rows + len(PARTIES) * ROW_H
    summary = legend_bottom + 10
    verdict = summary + 3 * LINE_H
    footer = verdict + LINE_H + 6
    window_h = footer + 18 + 6
    return {
        "legend_header": legend_header,
        "legend_rows": legend_rows,
        "legend_bottom": legend_bottom,
        "summary": summary,
        "verdict": verdict,
        "footer": footer,
        "window_h": window_h,
    }


def icon(name: str, sprite: str, x: int, y: int, scale: float, frame: int | None = None) -> list[str]:
    out = ['\t\ticonType = {',
           '\t\t\tname = "%s"' % name,
           '\t\t\tspriteType = "%s"' % sprite]
    if frame is not None:
        out.append('\t\t\tframe = %d' % frame)
    out += ['\t\t\tposition = { x = %d y = %d }' % (x, y),
            '\t\t\tscale = %.2f' % scale,
            '\t\t\tOrientation = UPPER_LEFT',
            '\t\t}', '']
    return out


def text_box(name: str, x: int, y: int, w: int, h: int, body: str,
             font: str = "hoi_16mbs", align: str | None = None) -> list[str]:
    out = ['\t\tinstantTextBoxType = {',
           '\t\t\tname = "%s"' % name,
           '\t\t\tposition = { x = %d y = %d }' % (x, y),
           '\t\t\tfont = %s' % font,
           '\t\t\ttext = "%s"' % body]
    if align:
        out.append('\t\t\tformat = %s' % align)
    out += ['\t\t\tmaxWidth = %d' % w,
            '\t\t\tmaxHeight = %d' % h,
            '\t\t\tfixedsize = yes',
            '\t\t}', '']
    return out


def emit_gui() -> str:
    lay = layout()
    out = ['guiTypes = {', '',
           '\t# The Cortes chamber panel. Mounted by common/scripted_guis/spain_cortes_scripted_gui.txt',
           '\t# from the SPR_cortes decision category, which draws it inside the category description.',
           '\t#',
           '\t# Generated by tools/build_spain_cortes_hemicycle.py: the hemicycle, the legend and the',
           '\t# summary are all generated, because the number of dots and the parties live there.',
           '\tcontainerWindowType = {',
           '\t\tname = "spain_cortes_window"',
           '\t\tposition = { x = 0 y = 0 }',
           '\t\tsize = { width = %d height = %d }' % (WINDOW_W, lay["window_h"]),
           '\t\tOrientation = UPPER_LEFT',
           '\t\tclipping = no',
           '']

    out += text_box("spain_cortes_title", MARGIN, TITLE_Y, 240, TITLE_H,
                    "SPAIN_CORTES_TITLE", font="hoi_18b")
    out += text_box("spain_cortes_scale", 248, TITLE_Y, WINDOW_W - MARGIN - 248, TITLE_H,
                    "SPAIN_CORTES_SCALE", align="right")

    out += ['\t\t# One icon per dot. Every dot is a frame of GFX_spain_cortes_seats, and the frame it',
            '\t\t# shows is the seat variable that spain_cortes_draw_hemicycle writes, 1 being neutral.',
            '']
    for idx, (x, y) in enumerate(dot_offsets(), start=1):
        out += icon("spain_cortes_dot_%d" % idx, "GFX_spain_cortes_seats", x, y, DOT_SCALE,
                    frame=FRAME_EMPTY)

    out += ['\t\t# Legend: the seats each bloc holds, its share of the chamber and its part in the',
            '\t\t# government. The role text is scripted localisation keyed by the government variables.',
            '']
    hy = lay["legend_header"]
    out += text_box("spain_cortes_hdr_party", COL_NAME, hy, COL_NAME_W, ROW_H,
                    "SPAIN_CORTES_HDR_PARTY")
    out += text_box("spain_cortes_hdr_seats", COL_SEATS, hy, COL_NUM_W, ROW_H,
                    "SPAIN_CORTES_HDR_SEATS", align="right")
    out += text_box("spain_cortes_hdr_share", COL_SHARE, hy, COL_NUM_W, ROW_H,
                    "SPAIN_CORTES_HDR_SHARE", align="right")
    out += text_box("spain_cortes_hdr_role", COL_ROLE, hy, COL_ROLE_W, ROW_H,
                    "SPAIN_CORTES_HDR_ROLE")

    for i, (party, label, _govt_id) in enumerate(PARTIES):
        y = lay["legend_rows"] + i * ROW_H
        out += icon("spain_cortes_swatch_%s" % party, "GFX_spain_cortes_dot_%s" % party,
                    COL_SWATCH, y + 1, 1.0)
        out += text_box("spain_cortes_name_%s" % party, COL_NAME, y, COL_NAME_W, ROW_H, label)
        out += text_box("spain_cortes_seats_%s" % party, COL_SEATS, y, COL_NUM_W, ROW_H,
                        "SPAIN_CORTES_SEATS_%s" % party.upper(), align="right")
        out += text_box("spain_cortes_share_%s" % party, COL_SHARE, y, COL_NUM_W, ROW_H,
                        "SPAIN_CORTES_SHARE_%s" % party.upper(), align="right")
        out += text_box("spain_cortes_role_%s" % party, COL_ROLE, y, COL_ROLE_W, ROW_H,
                        "SPAIN_CORTES_ROLE_%s" % party.upper())

    sy = lay["summary"]
    out += ['\t\t# Summary: who governs, on how many seats, and whether that is enough.',
            '']
    out += text_box("spain_cortes_gov_label", MARGIN, sy, 92, LINE_H, "SPAIN_CORTES_GOV_LABEL")
    out += text_box("spain_cortes_gov_name", 104, sy, WINDOW_W - MARGIN - 104, LINE_H,
                    "SPAIN_CORTES_GOV_NAME", font="hoi_18mbs")

    y = sy + LINE_H
    out += text_box("spain_cortes_gov_seats", 104, y, WINDOW_W - MARGIN - 104, LINE_H,
                    "SPAIN_CORTES_GOV_SEATS_LINE")

    y += LINE_H
    out += text_box("spain_cortes_margin_label", MARGIN, y, 170, LINE_H,
                    "SPAIN_CORTES_MARGIN_LABEL")
    out += text_box("spain_cortes_margin_value", 180, y, 36, LINE_H,
                    "SPAIN_CORTES_MARGIN_VALUE", font="hoi_18mbs", align="right")
    out += text_box("spain_cortes_margin_unit", 220, y, 34, LINE_H, "SPAIN_CORTES_MARGIN_UNIT")

    out += text_box("spain_cortes_elections_label", 258, y, 64, LINE_H,
                    "SPAIN_CORTES_ELECTIONS_LABEL")
    out += text_box("spain_cortes_elections_value", 324, y, 24, LINE_H,
                    "SPAIN_CORTES_ELECTIONS_VALUE", align="right")
    out += text_box("spain_cortes_status", 352, y, WINDOW_W - MARGIN - 352, LINE_H,
                    "SPAIN_CORTES_STATUS")

    out += text_box("spain_cortes_verdict", MARGIN, lay["verdict"],
                    WINDOW_W - 2 * MARGIN, LINE_H, "SPAIN_CORTES_VERDICT")

    out += text_box("spain_cortes_footer", MARGIN, lay["footer"], WINDOW_W - 2 * MARGIN, 18,
                    "SPAIN_CORTES_FOOTER")

    out += ['\t}', '}', '']
    return '\n'.join(out)


def emit_scripted_gui() -> str:
    out = ['scripted_gui = {', '',
           '\t# The chamber panel. One frame property per dot, so the hemicycle repaints whenever',
           '\t# spain_cortes_refresh_display rewrites the seat table. A dot is a frame of the seat',
           '\t# sprite strip: frame 1 is the neutral seat, so a seat variable that has never been',
           '\t# written shows an empty bench rather than the first party colour. Generated by',
           '\t# tools/build_spain_cortes_hemicycle.py.',
           '\tspain_cortes_panel = {',
           '\t\tcontext_type = decision_category',
           '\t\twindow_name = "spain_cortes_window"',
           '\t\tvisible = { has_variable = spain_cortes_total }',
           '\t\tai_enabled = { always = no }',
           '',
           '\t\tproperties = {']
    for i in range(1, DOTS + 1):
        out.append('\t\t\tspain_cortes_dot_%d = { frame = spain_cortes_seat_%d }' % (i, i))
    out += ['\t\t}', '\t}', '}', '']
    return '\n'.join(out)


def emit_panel_loc() -> str:
    """Scripted localisation for the derived text: roles, verdict, status, margin, government.

    Triggers run in the scope the GUI is attached to, which for a decision category is the
    country, so they read the country variables directly the way vanilla scripted localisation
    does. No ROOT wrapper: ROOT is not defined while a GUI property is being resolved, and a
    trigger that cannot resolve makes the engine fall back to the first text block in the
    list, which is what painted the whole chamber in the first party colour.
    """
    out = ['# Overview: scripted localisation for the Cortes panel.',
           '# Party roles, the majority verdict, the chamber status and the government name are',
           '# derived here from the country variables the Spanish campaign already keeps, so the',
           '# panel never shows a raw variable or a single unset branch.',
           '# Generated by tools/build_spain_cortes_hemicycle.py.',
           '']

    for party, _label, govt_id in PARTIES:
        out += ['defined_text = {',
                '\tname = spain_cortes_role_%s' % party,
                '\ttext = {',
                '\t\ttrigger = { check_variable = { var = spain_government_party value = %d } }' % govt_id,
                '\t\tlocalization_key = SPAIN_CORTES_ROLE_GOVERNMENT',
                '\t}',
                '\ttext = {',
                '\t\ttrigger = {',
                '\t\t\tOR = {',
                '\t\t\t\tcheck_variable = { var = spain_coalition_1 value = %d }' % govt_id,
                '\t\t\t\tcheck_variable = { var = spain_coalition_2 value = %d }' % govt_id,
                '\t\t\t}',
                '\t\t}',
                '\t\tlocalization_key = SPAIN_CORTES_ROLE_COALITION',
                '\t}',
                '\ttext = { localization_key = SPAIN_CORTES_ROLE_OPPOSITION }',
                '}', '']

    out += ['defined_text = {',
            '\tname = spain_cortes_government_text',
            '\t# one entry per party id the government variables can hold',
            '']
    for party, label, govt_id in PARTIES:
        out += ['\ttext = {',
                '\t\ttrigger = { check_variable = { var = spain_government_party value = %d } }' % govt_id,
                '\t\tlocalization_key = %s' % label,
                '\t}']
    out += ['\ttext = { localization_key = SPAIN_CORTES_NO_GOVERNMENT }',
            '}', '']

    out += ['defined_text = {',
            '\tname = spain_cortes_margin_text',
            '\ttext = {',
            '\t\ttrigger = { check_variable = { var = spain_government_majority value = 1 } }',
            '\t\tlocalization_key = SPAIN_CORTES_MARGIN_OVER',
            '\t}',
            '\ttext = { localization_key = SPAIN_CORTES_MARGIN_SHORT }',
            '}', '']

    out += ['defined_text = {',
            '\tname = spain_cortes_verdict_text',
            '\ttext = {',
            '\t\ttrigger = {',
            '\t\t\tOR = {',
            '\t\t\t\tNOT = { has_variable = spain_government_party }',
            '\t\t\t\tcheck_variable = { var = spain_government_party value = 0 }',
            '\t\t\t}',
            '\t\t}',
            '\t\tlocalization_key = SPAIN_CORTES_VERDICT_NONE',
            '\t}',
            '\ttext = {',
            '\t\ttrigger = { check_variable = { var = spain_government_majority value = 1 } }',
            '\t\tlocalization_key = SPAIN_CORTES_VERDICT_PASS',
            '\t}',
            '\ttext = { localization_key = SPAIN_CORTES_VERDICT_FAIL }',
            '}', '']

    out += ['defined_text = {',
            '\tname = spain_cortes_status_text',
            '\ttext = {',
            '\t\ttrigger = { has_country_flag = spain_cortes_dissolved }',
            '\t\tlocalization_key = SPAIN_CORTES_STATUS_DISSOLVED',
            '\t}',
            '\ttext = { localization_key = SPAIN_CORTES_STATUS_SITTING }',
            '}', '']
    return '\n'.join(out)


def emit_dots_stub() -> str:
    return '\n'.join([
        '# Overview: retired scripted localisation for the Cortes hemicycle.',
        '# The dots used to pick a texture through one defined_text each: 100 blocks of eight',
        '# trigger evaluations, and a trigger that could not resolve made the engine fall back to',
        '# the first text block, so every seat came out in the first party colour. Each dot is now',
        '# a frame of GFX_spain_cortes_seats, set straight from the seat variables by',
        '# common/scripted_guis/spain_cortes_scripted_gui.txt.',
        '# Kept as a stub so the panel has one seat-texture mechanism. Generated by',
        '# tools/build_spain_cortes_hemicycle.py.',
        ''])


def emit_effect() -> str:
    mids = seat_midpoints()
    out = ['# Overview: the seat table behind the Cortes hemicycle.',
           '# One dot is %d seats. spain_cortes_refresh_display writes the cumulative bloc totals,' % SEATS_PER_DOT,
           '# then this decides which frame each dot shows. Frames are 1-based, as the strip registered in',
           '# interface/endsieg_spain_icons.gfx is: frame 1 is the neutral seat and frames 2..8 are the',
           '# parties in chamber order, so a chamber with no seat table yet draws empty benches instead of',
           '# a party colour.',
           '# Generated by tools/build_spain_cortes_hemicycle.py.',
           '#',
           '# Dot order runs left to right around the chamber, so a cumulative total is the point',
           "# on the semicircle where that bloc's seats end: a bloc owns every dot whose middle",
           '# seat falls at or below its running total.',
           'spain_cortes_draw_hemicycle = {',
           '\tif = {',
           '\t\tlimit = { has_variable = spain_cortes_cum_falange }',
           '']
    for i, mid in enumerate(mids, start=1):
        out.append('\t\tset_variable = { var = spain_cortes_seat_%d value = %d }' % (i, FRAME_EMPTY))
        out.append('\t\tif = {')
        out.append('\t\t\tlimit = { check_variable = { var = spain_cortes_cum_socialists value = %d compare = greater_than_or_equals } }' % mid)
        out.append('\t\t\tset_variable = { var = spain_cortes_seat_%d value = %d }' % (i, frame_of(1)))
        out.append('\t\t}')
        for n, (party, _label, _govt_id) in enumerate(PARTIES[1:], start=2):
            out.append('\t\telse_if = {')
            out.append('\t\t\tlimit = { check_variable = { var = spain_cortes_cum_%s value = %d compare = greater_than_or_equals } }' % (party, mid))
            out.append('\t\t\tset_variable = { var = spain_cortes_seat_%d value = %d }' % (i, frame_of(n)))
            out.append('\t\t}')
        out.append('')
    out += ['\t}', '}', '']
    return '\n'.join(out)


def emit_ui_loc() -> str:
    """Every string the panel shows, so no key in the .gui is left unresolved."""
    pct = '%'
    out = ['l_english:',
           ' # Overview: text for the Cortes chamber panel. Generated by',
           ' # tools/build_spain_cortes_hemicycle.py, which also generates the window that reads it.',
           ' SPAIN_CORTES_TITLE: "§YCortes de España§!"',
           ' SPAIN_CORTES_SCALE: "%d dots · %d seats each"' % (DOTS, SEATS_PER_DOT),
           ' SPAIN_CORTES_HDR_PARTY: "PARTY"',
           ' SPAIN_CORTES_HDR_SEATS: "SEATS"',
           ' SPAIN_CORTES_HDR_SHARE: "SHARE"',
           ' SPAIN_CORTES_HDR_ROLE: "ROLE"']

    for party, label, _govt_id in PARTIES:
        out.append(' %s: "%s"' % (label, PARTY_NAMES[party]))
    for party, _label, _govt_id in PARTIES:
        out.append(' SPAIN_CORTES_SEATS_%s: "[?SPR.spain_cortes_seats_%s]"' % (party.upper(), party))
        out.append(' SPAIN_CORTES_SHARE_%s: "[?SPR.spain_cortes_share_%s]%s"' % (party.upper(), party, pct))

    # Every scripted-loc string is reached through a plain localisation key, because a GUI text
    # only looks up keys: the key's value expands the defined_text with [name], the way vanilla
    # localisation does.
    for party, _label, _govt_id in PARTIES:
        out.append(' SPAIN_CORTES_ROLE_%s: "[spain_cortes_role_%s]"' % (party.upper(), party))

    out += [' SPAIN_CORTES_ROLE_GOVERNMENT: "§YGOVERNMENT§!"',
            ' SPAIN_CORTES_ROLE_COALITION: "§GCOALITION§!"',
            ' SPAIN_CORTES_ROLE_OPPOSITION: "OPPOSITION"',
            ' SPAIN_CORTES_GOV_LABEL: "Government"',
            ' SPAIN_CORTES_NO_GOVERNMENT: "No government formed"',
            ' SPAIN_CORTES_GOV_NAME: "[spain_cortes_government_text]"',
            ' SPAIN_CORTES_MARGIN_LABEL: "[spain_cortes_margin_text]"',
            ' SPAIN_CORTES_STATUS: "[spain_cortes_status_text]"',
            ' SPAIN_CORTES_VERDICT: "[spain_cortes_verdict_text]"',
            ' SPAIN_CORTES_GOV_SEATS_LINE: "[?SPR.spain_government_seats] of [?SPR.spain_cortes_total] seats · majority needs [?SPR.spain_cortes_majority_seats]"',
            ' SPAIN_CORTES_MARGIN_SHORT: "Short of a majority"',
            ' SPAIN_CORTES_MARGIN_OVER: "Above a majority"',
            ' SPAIN_CORTES_MARGIN_VALUE: "[?SPR.spain_cortes_govt_gap]"',
            ' SPAIN_CORTES_MARGIN_UNIT: "seats"',
            ' SPAIN_CORTES_ELECTIONS_LABEL: "Elections"',
            ' SPAIN_CORTES_ELECTIONS_VALUE: "[?SPR.spain_elections_fought]"',
            ' SPAIN_CORTES_STATUS_SITTING: "§Gchamber sitting§!"',
            ' SPAIN_CORTES_STATUS_DISSOLVED: "§Rchamber dissolved§!"',
            ' SPAIN_CORTES_VERDICT_PASS: "§GThe government can pass legislation.§!"',
            ' SPAIN_CORTES_VERDICT_FAIL: "§RThe government cannot pass legislation without partners.§!"',
            ' SPAIN_CORTES_VERDICT_NONE: "§RNo government has been formed.§!"',
            ' SPAIN_CORTES_FOOTER: "One dot is %d seats. A bill passes at [?SPR.spain_cortes_majority_seats] of [?SPR.spain_cortes_total]."' % SEATS_PER_DOT,
            '']
    return '\n'.join(out)


def main() -> int:
    positions = dot_positions()
    if len(positions) != DOTS:
        print('expected %d dots, computed %d' % (DOTS, len(positions)))
        return 1
    if len(set(positions)) != DOTS:
        print('two dots share a position; the rings overlap')
        return 1
    if SEATS % DOTS:
        print('%d seats do not divide across %d dots' % (SEATS, DOTS))
        return 1

    lay = layout()
    files = {
        'interface/endsieg_spain_cortes.gui': (emit_gui(), '\n'),
        'common/scripted_guis/spain_cortes_scripted_gui.txt': (emit_scripted_gui(), '\n'),
        'common/scripted_localisation/spain_cortes_panel.txt': (emit_panel_loc(), '\n'),
        'common/scripted_localisation/spain_cortes_dots.txt': (emit_dots_stub(), '\n'),
        'common/scripted_effects/spain_cortes_hemicycle.txt': (emit_effect(), '\n'),
        'localisation/english/spain_cortes_ui_l_english.yml': (emit_ui_loc(), '\r\n'),
    }
    for path, (text, newline) in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # localisation needs a UTF-8 BOM and CRLF; game script must be plain UTF-8
        encoding = 'utf-8-sig' if path.endswith('.yml') else 'utf-8'
        with io.open(path, 'w', encoding=encoding, newline=newline) as fh:
            fh.write(text)
        print('wrote %-56s %5d lines' % (path, text.count('\n')))

    counts = ring_counts()
    print('rings %s -> %d dots' % (counts, sum(counts)))
    print('window %dx%d, chamber %dpx wide, %dpx tall'
          % (WINDOW_W, lay['window_h'], 2 * R_OUTER, R_OUTER))
    return 0


if __name__ == '__main__':
    sys.exit(main())
