# S16 — the hemicycle is addressed 1..8 again; S13's 0-based mapping was wrong

Card: `t_c8d7558c`. Branch: `TeknoDev-Branch`. Base commit: `62676fadc`. Run 108. No launch, no
commit, no push. This is a source repair plus a regenerated artefact package; nothing here is a live
game test.

## What was wrong

`GFX_spain_cortes_seats` is `noOfFrames = 8` over a strip `tools/build_spain_cortes_dots.py` writes as
`[neutral] + PARTIES`. Eight cells, and the engine addresses them as frames **1..8**: frame 1 is the
neutral bench, frames 2..8 are socialists, republicans, liberals, conservatives, monarchists, carlists
and falange in chamber order.

Two successive changes had it as 0..7. S10 (`5ad0945ad`) hand-corrected the effect from 1..8 to 0..7
on the theory that eight frames mean indices 0..7; S13 then taught the generator the same 0-based
mapping (`FRAME_EMPTY = 0`, `frame_of = party_index`) in an uncommitted edit that is the working-tree
starting point of this card. Under 1-based addressing that mapping paints every dot one cell to the
left of its bloc and never asks for cell 8, so the falange could never appear.

## Why 1-based, stated carefully

The decisive argument is arithmetic plus ordinal numbering, not the absence of a `frame = 0` anywhere
in vanilla — that claim is false and must not be repeated:

* `<HOI4>/interface/countrydiplomacyview.gui:1471` sets `frame = 0` on the 2-frame
  `GFX_generic_checkbox`, and checkbox uses of that same 2-frame sprite appear as 0, 1 and 2 in
  different windows, so `checkboxType.frame` cannot discriminate the base at all.
* `<HOI4>/interface/airselectionview.gui:783` sets `frame = 0` on the 19-frame
  `GFX_strategicair_mission_types` as an `alwaystransparent` placeholder the air UI overwrites.
* What does hold: **no vanilla level selector addresses an N-cell strip as 0..N-1**, while two
  independent ones address it as 1..N. `common/scripted_guis/INS_revolution_scripted_gui.txt:8-46`
  maps revolution levels 1..10 to `frame = 1` … `frame = 10`. And
  `common/scripted_effects/SOV_scripted_effects.txt:782` (with `common/decisions/SOV.txt:1763`)
  computes a 0-based portrait index and then executes
  `add_to_temp_variable = { SOV_generic_portrait_frame = 1 }` before storing the value the scripted
  GUI reads as `frame`. Vanilla converts an index into a frame by adding one.
* The offline wiki numbers strip cells ordinally: `paradox_wiki/Character modding - Hearts of Iron 4
  Wiki.md:648` (`noOfFrames = 3` → `sprite = 1` is the left third) and
  `paradox_wiki/Resources modding - Hearts of Iron 4 Wiki.md:37` (`1` = Oil, `2` = Aluminium).

So: an eight-cell strip has to be addressed 1..8 for the last cell to be reachable at all. How the
engine treats an **out-of-range** frame (0 or 9 here) is **unverified** and is not what this repair
rests on.

**S13's premise was wrong.** Its reasoning treated `noOfFrames = 8` as "indices 0..7" and read the
wiki's ordinal prose as prose numbering rather than as the addressing rule. Its artefacts were
consistent with its own builder, which is why its tests passed: the tests pinned the same wrong base.

## Changed files (all inside the card's owned list of twelve)

| # | File | Change |
| --- | --- | --- |
| 1 | `tools/build_spain_cortes_hemicycle.py` | `FRAME_EMPTY = 1`; `frame_of(party_index)` returns `party_index + 1`; the frame comment states 1-based with 1 = neutral and 2..8 = the parties and cites the SOV/INS evidence; `FRAME_PLACEHOLDER` folded back into `FRAME_EMPTY` so the generated window and the seat table cannot drift; effect header emitted as 1-based. |
| 2 | `tools/build_spain_cortes_dots.py` | Prose only: docstring and the `PARTIES` comment now say frames 1..8 with frame 1 neutral. Strip geometry untouched (`[EMPTY] + PARTIES`, 8 cells, same nine DDS files). |
| 3 | `interface/endsieg_spain_icons.gfx` | `GFX_spain_cortes_seats` comment corrected to "frames 1..8, frame 1 the neutral seat and frames 2..8 the parties". No sprite name, texture path, size or `noOfFrames` change. |
| 4 | `interface/endsieg_spain_cortes.gui` | Regenerated, **byte-identical**: the builder writes the same `frame = 1` on all 100 dots, which is now the neutral frame itself. |
| 5 | `common/scripted_guis/spain_cortes_scripted_gui.txt` | Regenerated, **byte-identical**: its header already said "frame 1 is the neutral seat", which was stale under S13 and is correct now. |
| 6 | `common/scripted_effects/spain_cortes_hemicycle.txt` | Regenerated: 800 writes, 100 each of frames 1..8, no `value = 0`; header says 1-based. 802 lines changed (800 writes + the two header lines). |
| 7 | `common/scripted_localisation/spain_cortes_panel.txt` | Regenerated, **byte-identical**. |
| 8 | `common/scripted_localisation/spain_cortes_dots.txt` | Regenerated, **byte-identical** (stub comment). |
| 9 | `localisation/english/spain_cortes_ui_l_english.yml` | Regenerated, **byte-identical** (BOM + CRLF preserved). |
| 10 | `.tools/tests/test_spain_hemicycle_builder.py` | Rewritten for the 1-based contract: neutral 1, party frames 2..8, `frame_of(7) == 8`, no emitted 0 and no emitted 9, histogram 100 of each 1..8, window placeholder all 1, byte-reproduction of all six artefacts, and a mutant control that rebuilds the 0-based mapping from the current source (S13's edit was never committed, so no revision could be pinned). 69 checks. |
| 11 | `.tools/tests/test_spain_cortes_runtime.py` | `NEUTRAL_FRAME = 1`, `PARTY_FRAMES` 2..8, `STRIP_FRAMES = 8`; the frame-range assertion is now `range(1, 9)` with an explicit "no frame 0 and no frame 9" check; the old mutant block (pre-S10 1..8 file) no longer discriminates and was replaced by the 0-based table pinned at `5ad0945ad1a92944a258a5097680a220cb1c7af6`. 113 checks. |
| 12 | `docs/plans/spain/subagent_handoffs/hemicycle_builder.md` | This handoff, replacing S13's. |

`.tools/` is gitignored, so paths 10 and 11 do not appear in `git status`; 11 is tracked from S10 and
does appear as modified.

## Evidence actually run

Both builders, from the mod root:

```
$ python tools/build_spain_cortes_hemicycle.py
wrote interface/endsieg_spain_cortes.gui                        1449 lines
wrote common/scripted_guis/spain_cortes_scripted_gui.txt         117 lines
wrote common/scripted_localisation/spain_cortes_panel.txt        202 lines
wrote common/scripted_localisation/spain_cortes_dots.txt           8 lines
wrote common/scripted_effects/spain_cortes_hemicycle.txt        3017 lines
wrote localisation/english/spain_cortes_ui_l_english.yml          59 lines
rings [11, 16, 20, 24, 29] -> 100 dots
window 500x570, chamber 476px wide, 238px tall
$ python tools/build_spain_cortes_dots.py
party order matches the chamber generator: 7 parties
wrote gfx\interface\endsieg_spain_dots\spain_cortes_seats.dds 128x16, 8 frames
wrote gfx\interface\endsieg_spain_dots\spain_cortes_dot_empty.dds
… eight single-dot sprites
```

The histograms, read straight out of the generated file:

```
$ grep -o 'var = spain_cortes_seat_[0-9]* value = [0-9]*' common/scripted_effects/spain_cortes_hemicycle.txt | sed 's/.*value = //' | sort -n | uniq -c
    100 1
    100 2
    100 3
    100 4
    100 5
    100 6
    100 7
    100 8
$ grep -c 'set_variable = { var = spain_cortes_seat_' common/scripted_effects/spain_cortes_hemicycle.txt
800
$ grep -c 'value = 0 }' common/scripted_effects/spain_cortes_hemicycle.txt
0
$ grep -c 'value = 9 }' common/scripted_effects/spain_cortes_hemicycle.txt
0
```

The window and the scripted GUI:

```
$ grep -o 'frame = [0-9]*' interface/endsieg_spain_cortes.gui | sort | uniq -c
    100 frame = 1
$ grep -c 'spriteType = "GFX_spain_cortes_seats"' interface/endsieg_spain_cortes.gui
100
$ grep -c 'frame = spain_cortes_seat_' common/scripted_guis/spain_cortes_scripted_gui.txt
100
frame = spain_cortes_seat_1 … frame = spain_cortes_seat_100
```

Byte-identical regeneration (criterion 1): `git status --porcelain` and `git diff --stat` were saved
after the first run and again after a second run of both builders. `diff` reported no difference:

```
SECOND RUN: git status and git diff --stat unchanged
```

The nine DDS textures the dots builder writes were hashed before the run and compared byte for byte
afterwards with `cmp`: all nine `identical`. `git status --porcelain -- gfx/` is empty, so the strip
and its sprites are untouched.

Suites:

```
$ python .tools/tests/test_spain_hemicycle_builder.py
  note  0-based mutant rejected by 16 of 37 shared checks
69 checks, 0 failures          (exit 0)

$ python .tools/tests/test_spain_cortes_runtime.py
113 checks, 0 failures         (exit 0)

$ python .tools/tests/test_spain_cortes_recount.py
215 checks, 0 failures         (exit 0)
```

The runtime suite moved 111 → 113 because three checks were added on the frame range and one
(frame 8 on an eight-frame strip) was replaced by the 0-based mutant pair.

Mutant control (criterion 3): the suite rebuilds `FRAME_EMPTY = 0` and `return party_index` from the
current builder source, asserts the mutant really is 0-based (neutral 0, `frame_of(1) == 1`,
`frame_of(7) == 7`, highest frame 7, never asks for cell 8), and then requires the shared assertions to
reject it: 16 of 37 shared checks fail, including the neutral-frame, frame-0/range and reproduction
checks. If a future rename makes the mutation impossible, the control raises instead of passing.

Working-tree hygiene (criterion 6): `git diff --name-only` compared against Director's 00:10 baseline
list gives exactly four paths newly modified — `.tools/tests/test_spain_cortes_runtime.py`,
`common/scripted_effects/spain_cortes_hemicycle.txt`, `interface/endsieg_spain_icons.gfx`,
`tools/build_spain_cortes_dots.py` — plus `tools/build_spain_cortes_hemicycle.py`, already dirty at the
baseline because it carried S13's edit. Nothing was reverted, staged or cleaned: the comm of the
baseline against the current set shows no path that stopped being modified.

One unowned path did change, and it is a bytecode artefact:
`tools/__pycache__/build_spain_cortes_hemicycle.cpython-314.pyc` is tracked, was already modified at
the baseline (S13's run had rewritten it), and any `python tools/build_spain_cortes_hemicycle.py`
rewrites it again. It now reflects this builder. I did not `git checkout` it because Director reserved
the working tree. It carries no mod content; recommend excluding `__pycache__` at integration.

## MCP evidence (read-only routes only)

| Route | Input | Before (00:1x) | After |
| --- | --- | --- | --- |
| `hoi4.source_lookup` | `symbol=spain_cortes_draw_hemicycle` | revision `4fef7036…`; 1 definition `mod:common/scripted_effects/spain_cortes_hemicycle.txt:12-3017`; 1 reference `spain_cortes_refresh_display` at `spain_cortes_effects.txt:253`; first writes `seat_1 value = 0` then `value = 1` | revision `1f7b1413…`; same definition and the same single reference; first writes `seat_1 value = 1` then `value = 2` |
| `hoi4.source_lookup` | `symbol=spain_cortes_seat_1` | 0 definitions (it is a variable), 8 `variable_write` references at lines 16/19/23/27/31/35/39/43 | unchanged: 0 definitions, the same 8 writes at the same lines |
| `hoi4.script_validate` | `path=common/scripted_effects/spain_cortes_hemicycle.txt` | `SCRIPT_CHECK_PARTIAL`, `valid: null`, 0 findings, `checkedCommands: 2202`, `unresolvedCount: 0`, `argumentBlocksUnchecked: 1500`, `parametersChecked: false`, `roots: 1`, `unknownScopeRoots: 1`, `checksPerformed: [syntax, command_kind, declared_scope, event_popups, known_mistakes]` | identical figures: `SCRIPT_CHECK_PARTIAL`, 0 findings, 2202 commands, 1500 unchecked argument blocks, same scope roots |
| `hoi4.script_validate` | `path=common/scripted_guis/spain_cortes_scripted_gui.txt` | — | `SCRIPT_CHECK_PARTIAL`, 0 findings, `checkedCommands: 0`, `family: unsupported` — the validator does not model scripted-GUI files, so this route proves only that the file parses as a block tree |
| `hoi4.gui_inspect` | `windowName=endsieg_spain_cortes` | — | `GUI_INSPECTED`; graph-wide: 3513 elements, 51282 nodes, 41915 sprites, 32 scripted GUIs; `inspectedElementCount: 0` because no element carries that name (it is the feature name, not a window) |
| `hoi4.gui_inspect` | `windowName=spain_cortes_window` (retry with the real container name) | — | `GUI_INSPECTED`; `inspectedElementCount: 153` (100 dot icons + 7 legend swatches + header/summary/verdict/footer texts); graph 3513 elements / 51302 nodes / 214255 edges / 41915 sprites / 32 scripted GUIs; validation `gui-source-graph: passed`; resource `hoi4-agent://workspace/endsieg/artifact/6c2a9c1f…/gui-inspect.744a1a8c8718c493.json` |

No dot frame resolves to 0 or 9: every one of the 100 dot icons in the window carries the literal
`frame = 1` placeholder, and the 100 scripted-GUI frame properties resolve to the seat variables whose
emitted values are 100 each of 1..8 with none at 0 or 9. Note that `gui_inspect` cannot evaluate those
variables — the frame a dot finally paints is engine state, not a `.gui` property — so this is a
source-level resolution, not a rendered one.

Diagnostics returned by `gui_inspect` that are **not** this card: seven `GUI_SPRITE_MISSING`
"missing sprite OPPOSITION" findings on the `spain_cortes_role_*` text elements (the tool resolves the
panel's scripted-loc key to its default branch's literal text and reads it as a sprite name — the
elements are `instantTextBoxType`, and `common/scripted_localisation/spain_cortes_panel.txt` is
byte-identical to HEAD in this card), 185 non-blocking `GUI_INCONSISTENT_ALIGNMENT` notes on the
hemicycle arcs, and workspace-wide blockers from other countries' GUIs (`bul_`, `gre_`, `sov_`,
`swe_`, `usa_`, `war_escalation_` unresolved windows, `SOURCE_TOKEN_LIMIT` on
`FR_SCRIPTING_FULL_AUTOMATED.txt`, 109k truncated reference diagnostics). All of those are outside the
twelve owned paths and predate this run.

## Not performed / unverified

* No HOI4 launch, no save inspection, no live playtest (not authorized). The rendered chamber is
  **unverified**: that frame 1 is the neutral cell and frame 8 the falange cell on screen, that the
  dots repaint when `spain_cortes_refresh_display` rewrites the table, and that the first paint before
  the scripted GUI resolves shows empty benches are all engine behaviour this package does not test.
* The engine's treatment of an out-of-range frame (whether 0 falls back to the first cell, an error or
  nothing) is unverified and is not part of the argument.
* `hoi4.gui_render` was not run: a frame index living in a seat variable is not a `.gui` property, so a
  renderer would show the placeholder, not the value.
* The validator cannot confirm a frame value: `argumentBlocksUnchecked: 1500` is this file family's
  standing limit.

Commit: **none**. Runtime deployment is Director's; `.tools/tests/test_spain_hemicycle_builder.py`
needs `git add -f` if it is to be committed, because `.tools/` is gitignored.
