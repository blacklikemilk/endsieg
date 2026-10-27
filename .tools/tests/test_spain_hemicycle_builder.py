"""Regression test: the hemicycle builder emits the 1-based frames the strip is addressed with.

`tools/build_spain_cortes_hemicycle.py` is the single source of
`common/scripted_effects/spain_cortes_hemicycle.txt`, so a mapping that disagrees with the file
silently rewrites the seat table the next time anyone regenerates it. That is exactly what happened
twice: S10 corrected the shipped effect by hand from frames 1..8 to 0..7 on an eight-cell strip, and
S13 then taught the generator the same 0-based mapping. Both were wrong in the same way.
`GFX_spain_cortes_seats` is `noOfFrames = 8` over a strip laid out as `[neutral] + PARTIES`, and the
engine addresses those eight cells as frames 1..8: frame 1 is the neutral bench, frames 2..8 the
parties in chamber order. A 0-based mapping shifts every dot one cell to the left and never asks for
cell 8, so the falange can never appear.

The evidence for the 1-based addressing is arithmetic and ordinal, not the absence of a frame 0 in
vanilla: `common/scripted_effects/SOV_scripted_effects.txt:782` computes a 0-based portrait index and
then adds 1 before the scripted GUI reads it as `frame`, `common/scripted_guis/
INS_revolution_scripted_gui.txt:8-46` addresses a ten-level ladder as frames 1..10, and the offline
wiki numbers strip cells ordinally (`paradox_wiki/Character modding - Hearts of Iron 4 Wiki.md:648`).
How the engine treats an out-of-range frame is unverified; that an eight-cell strip has to be
addressed 1..8 for the last cell to be reachable at all is not.

This test pins that contract from four directions:

  - the builder's frame path: `FRAME_EMPTY` is 1, `frame_of(n)` is `n + 1`, and the highest frame the
    generator asks for is 8, never 9 and never 0;
  - the generated text: every dot writes its neutral seat once and then seven party frames in
    chamber order, over exactly 100 seat variables and 400 seats, 100 writes of each frame 1..8;
  - the generated file: `emit_effect()` is byte-identical to the committed effect, which is what
    makes a regeneration a no-op;
  - the other five generated artefacts: byte-identical too, so the repair cannot move a layout
    coordinate, a party label or a localisation key as a side effect.

The mutant control rebuilds the 0-based mapping from this builder's own source in a scratch file and
drives the same assertions through it. S13's 0-based edit was never committed, so no revision can be
pinned as the mutant; mutating the current source is the honest equivalent, and the mutant's own
values are asserted before the shared checks are allowed to reject it, so the control cannot pass
vacuously.

Run from the repository root:

    python .tools/tests/test_spain_hemicycle_builder.py            # exit 0 = pass
    python .tools/tests/test_spain_hemicycle_builder.py --detail   # print every check
    python .tools/tests/test_spain_hemicycle_builder.py --mutant   # only the mutant control

This is a source simulation. It proves what the generator writes, not what the engine draws: the
sprite strip, the scripted GUI and the rendered chamber still need a game launch, which this test
never performs.
"""

from __future__ import annotations

import collections
import importlib.util
import io
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_spain_cortes_recount as base  # noqa: E402  (the S9 report harness, reused on purpose)

BUILDER_PATH = 'tools/build_spain_cortes_hemicycle.py'
EFFECT_PATH = 'common/scripted_effects/spain_cortes_hemicycle.txt'

# The strip GFX_spain_cortes_seats registers: eight cells, addressed as frames 1..8.
STRIP_FRAMES = 8
NEUTRAL_FRAME = 1

GENERATED = (
    'interface/endsieg_spain_cortes.gui',
    'common/scripted_guis/spain_cortes_scripted_gui.txt',
    'common/scripted_localisation/spain_cortes_panel.txt',
    'common/scripted_localisation/spain_cortes_dots.txt',
    EFFECT_PATH,
    'localisation/english/spain_cortes_ui_l_english.yml',
)

SEAT_WRITE = re.compile(r'set_variable = \{ var = spain_cortes_seat_(\d+) value = (\d+) \}')
CUM_CHECK = re.compile(r'var = spain_cortes_cum_(\w+) value = (\d+) compare = greater_than_or_equals')
DOT_ICON = re.compile(r'name = "spain_cortes_dot_(\d+)"\n\t\t\tspriteType = "GFX_spain_cortes_seats"'
                      r'\n\t\t\tframe = (\d+)')


def load_builder(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_text(relative, encoding='utf-8', newline=''):
    with io.open(str(ROOT / relative), 'r', encoding=encoding, newline=newline) as handle:
        return handle.read()


def parse_dots(text):
    """Every dot block, in document order: its writes, its party branches and their limits.

    A dot block starts at the neutral write that carries its index and runs to the next dot, so a
    block's writes read as `[neutral, party 1, ..., party 7]`.
    """
    dots = []
    current = None
    for line in text.splitlines():
        write = SEAT_WRITE.search(line)
        if write:
            index, value = int(write.group(1)), int(write.group(2))
            if current is None or current['index'] != index:
                current = {'index': index, 'writes': [], 'parties': [], 'mids': []}
                dots.append(current)
            current['writes'].append(value)
            continue
        cum = CUM_CHECK.search(line)
        if cum and current is not None:
            current['parties'].append(cum.group(1))
            current['mids'].append(int(cum.group(2)))
    return dots


def same_text(report, label, actual, expected):
    """Equality with a compact detail: whole generated files are too big to print in a report."""
    if actual == expected:
        report.check(label, True)
        return
    detail = '%d characters, expected %d' % (len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual.splitlines(), expected.splitlines()), start=1):
        if left != right:
            detail += '; first difference at line %d: %r vs %r' % (index, left[:80], right[:80])
            break
    report.check(label, False, detail)


# --- assertions shared by the working tree and the mutant -----------------------------

def assert_frame_path(report, module, text, prefix):
    """The neutral frame, the party mapping and the frame range of an eight-cell strip."""
    parties = [party for party, _label, _id in module.PARTIES]
    frames = len(parties) + 1

    report.equal('%sFRAME_EMPTY is the neutral cell of the strip' % prefix, module.FRAME_EMPTY,
                 NEUTRAL_FRAME)
    report.equal('%sstrip has one cell per party plus the neutral bench' % prefix, frames,
                 STRIP_FRAMES)
    for party_index in range(1, len(parties) + 1):
        report.equal('%sframe_of(%d) is the party cell after it' % (prefix, party_index),
                     module.frame_of(party_index), party_index + 1)
    report.check('%sno party frame is its bare 0-based index' % prefix,
                 module.frame_of(1) != 1 and module.frame_of(len(parties)) != len(parties),
                 'frame_of(1) is %d, frame_of(%d) is %d'
                 % (module.frame_of(1), len(parties), module.frame_of(len(parties))))
    report.equal('%sthe last party asks for the last cell of the strip' % prefix,
                 module.frame_of(len(parties)), STRIP_FRAMES)

    dots = parse_dots(text)
    values = [value for dot in dots for value in dot['writes']]
    report.equal('%shighest frame written' % prefix, max(values), STRIP_FRAMES)
    report.check('%shighest frame is inside the strip' % prefix,
                 max(values) <= STRIP_FRAMES, 'max %d against %d frames' % (max(values), frames))
    report.check('%sno frame below the first cell' % prefix, min(values) >= NEUTRAL_FRAME,
                 'min %d' % min(values))
    report.check('%sno frame 0 is emitted' % prefix, 0 not in values,
                 '%d writes of frame 0' % values.count(0))
    report.check('%sno frame 9 is emitted' % prefix, 9 not in values,
                 '%d writes of frame 9' % values.count(9))
    report.check('%severy frame is one the strip carries' % prefix,
                 set(values) <= set(range(NEUTRAL_FRAME, STRIP_FRAMES + 1)),
                 repr(sorted(set(values))))


def assert_seat_table(report, module, text, prefix):
    """100 dots, four seats each, one neutral write and seven party writes per dot."""
    dots = parse_dots(text)
    parties = [party for party, _label, _id in module.PARTIES]
    mids = module.seat_midpoints()

    report.equal('%sdot count' % prefix, len(dots), module.DOTS)
    report.equal('%sseat variables are 1..%d' % (prefix, module.DOTS),
                 [dot['index'] for dot in dots], list(range(1, module.DOTS + 1)))
    report.equal('%sseats per dot' % prefix, module.SEATS_PER_DOT, 4)
    report.equal('%schamber size' % prefix, module.SEATS, module.DOTS * module.SEATS_PER_DOT)
    report.equal('%sseat writes' % prefix,
                 sum(len(dot['writes']) for dot in dots), module.DOTS * (len(parties) + 1))

    histogram = collections.Counter(value for dot in dots for value in dot['writes'])
    report.equal('%swrites of every frame 1..8' % prefix, sorted(histogram.items()),
                 [(frame, module.DOTS) for frame in range(NEUTRAL_FRAME, STRIP_FRAMES + 1)])
    report.equal('%sneutral writes' % prefix, histogram[module.FRAME_EMPTY], module.DOTS)
    report.equal('%swrites per dot' % prefix,
                 sorted({len(dot['writes']) for dot in dots}), [len(parties) + 1])
    report.equal('%sparty frames after the neutral seat' % prefix,
                 sorted({tuple(dot['writes'][1:]) for dot in dots}),
                 [tuple(module.frame_of(i) for i in range(1, len(parties) + 1))])
    report.equal('%sneutral seat is written first' % prefix,
                 sorted({dot['writes'][0] for dot in dots}), [module.FRAME_EMPTY])

    report.equal('%sparty order per dot' % prefix,
                 sorted({tuple(dot['parties']) for dot in dots}), [tuple(parties)])
    report.equal('%sa dot draws one seat boundary' % prefix,
                 sorted({len(set(dot['mids'])) for dot in dots}), [1])
    report.equal('%sseat identity per dot' % prefix,
                 [dot['mids'][0] for dot in dots if dot['mids']], mids)
    report.equal('%sfirst dot stands for the second seat' % prefix, mids[0], 2)
    report.equal('%slast dot stands for the last bench' % prefix, mids[-1],
                 module.SEATS - module.SEATS_PER_DOT + 2)


def assert_reproduction(report, text, committed, prefix):
    same_text(report, '%sgenerated effect is the committed file' % prefix, text, committed)
    report.check('%scommitted file ends in a newline' % prefix, committed.endswith('\n'))
    report.check('%sheader states the 1-based frame base' % prefix,
                 '# then this decides which frame each dot shows. Frames are 1-based' in committed)
    report.check('%sheader names frame 1 as the neutral seat' % prefix,
                 '# interface/endsieg_spain_icons.gfx is: frame 1 is the neutral seat' in committed)
    report.check('%sheader no longer claims frame 0 is neutral' % prefix,
                 'frame 0 is the neutral seat' not in committed)


def assert_generated_artefacts(report, module, prefix):
    """Every other artefact this builder owns still matches the tree, byte for byte."""
    report.equal('%sdot positions' % prefix, len(module.dot_positions()), module.DOTS)
    report.equal('%sdot positions are distinct' % prefix,
                 len(set(module.dot_positions())), module.DOTS)
    report.equal('%sparty count' % prefix, len(module.PARTIES), 7)

    gui = read_text('interface/endsieg_spain_cortes.gui')
    icons = DOT_ICON.findall(gui)
    report.equal('%sthe window carries one icon per dot' % prefix, len(icons), module.DOTS)
    report.equal('%sthe window numbers its dots from 1' % prefix,
                 [int(index) for index, _frame in icons], list(range(1, module.DOTS + 1)))
    report.equal('%severy dot placeholder is the neutral frame' % prefix,
                 sorted({int(frame) for _index, frame in icons}), [NEUTRAL_FRAME])

    for relative, text in (
        ('interface/endsieg_spain_cortes.gui', module.emit_gui()),
        ('common/scripted_guis/spain_cortes_scripted_gui.txt', module.emit_scripted_gui()),
        ('common/scripted_localisation/spain_cortes_panel.txt', module.emit_panel_loc()),
        ('common/scripted_localisation/spain_cortes_dots.txt', module.emit_dots_stub()),
    ):
        same_text(report, '%s%s is unchanged' % (prefix, relative), text, read_text(relative))

    # localisation is written CRLF with a BOM; compare the text, then the framing separately.
    with io.open(str(ROOT / 'localisation/english/spain_cortes_ui_l_english.yml'),
                 'r', encoding='utf-8-sig', newline='') as handle:
        raw = handle.read()
    same_text(report, '%slocalisation text is unchanged' % prefix,
              module.emit_ui_loc(), raw.replace('\r\n', '\n'))
    with io.open(str(ROOT / 'localisation/english/spain_cortes_ui_l_english.yml'),
                 'rb') as handle:
        report.check('%slocalisation keeps its BOM and CRLF' % prefix,
                     handle.read(3) == b'\xef\xbb\xbf' and b'\r\n' in raw.encode('utf-8'))


# --- groups --------------------------------------------------------------------------

def test_builder_source(report, module):
    source = read_text(BUILDER_PATH)
    report.check('build_spain_cortes_hemicycle.py is present', bool(source))
    report.check('the module states that frames are 1-based', 'frames are 1-based' in source)
    report.check('no comment still claims 0-based frames', 'frames are 0-based' not in source)
    report.check('FRAME_EMPTY is defined as 1', 'FRAME_EMPTY = 1' in source)
    report.check('the window placeholder is the neutral frame itself',
                 not hasattr(module, 'FRAME_PLACEHOLDER'),
                 'a separate placeholder would let the window and the seat table drift apart')

    body = source.split('def frame_of', 1)[1].split('def ', 1)[0]
    report.check('frame_of offsets the party index by one', 'return party_index + 1' in body,
                 body.strip())


def test_committed_effect(report, module):
    text = module.emit_effect()
    committed = read_text(EFFECT_PATH)

    assert_frame_path(report, module, text, 'effect: ')
    assert_seat_table(report, module, text, 'effect: ')
    assert_reproduction(report, text, committed, 'effect: ')
    assert_generated_artefacts(report, module, 'artefacts: ')

    report.check('the committed effect is the file the builder writes', EFFECT_PATH in GENERATED)


def zero_based_mutant_source():
    """S13's 0-based builder, rebuilt from this one so no revision has to be pinned.

    Every substitution is counted: a rename in the builder must fail the mutant control loudly
    instead of quietly producing a mutant identical to the repair.
    """
    source = read_text(BUILDER_PATH)
    edits = (
        ('FRAME_EMPTY = 1', 'FRAME_EMPTY = 0'),
        ('return party_index + 1', 'return party_index'),
        ('Frames are 1-based, as the strip registered in',
         'Frames are 0-based, as the strip registered in'),
        ('is: frame 1 is the neutral seat and frames 2..8 are the',
         'is: frame 0 is the neutral seat and frames 1..7 are the'),
    )
    for before, after in edits:
        if source.count(before) != 1:
            raise SystemExit('the mutant control cannot rebuild the 0-based mapping: %r appears %d '
                             'times in %s' % (before, source.count(before), BUILDER_PATH))
        source = source.replace(before, after)
    return source


def test_mutant(report, module):
    """The 0-based mapping must fail the checks the repair is about."""
    handle = tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8')
    with handle:
        handle.write(zero_based_mutant_source())
    path = Path(handle.name)
    try:
        mutant = load_builder(path, 'hemicycle_builder_zero_based')
    finally:
        path.unlink(missing_ok=True)

    committed = read_text(EFFECT_PATH)
    text = mutant.emit_effect()
    dots = parse_dots(text)
    values = [value for dot in dots for value in dot['writes']]

    report.equal('mutant FRAME_EMPTY is the old 0', mutant.FRAME_EMPTY, 0)
    report.equal('mutant maps party 1 to frame 1', mutant.frame_of(1), 1)
    report.equal('mutant maps the last party to frame 7', mutant.frame_of(7), 7)
    report.equal('mutant still writes 100 seat variables', len(dots), 100)
    report.equal('mutant neutral frame', min(dot['writes'][0] for dot in dots), 0)
    report.equal('mutant writes a frame 0', min(values), 0)
    report.check('mutant never asks for the strip\'s last cell', max(values) < STRIP_FRAMES,
                 'highest frame %d of %d cells' % (max(values), STRIP_FRAMES))
    report.equal('mutant highest frame', max(values), 7)
    report.check('mutant does not reproduce the committed effect', text != committed,
                 '%d characters generated, %d committed' % (len(text), len(committed)))

    # Drive the same assertions the repaired builder passes, in their own report.
    probe = base.Report(detail=False)
    assert_frame_path(probe, mutant, text, 'mutant: ')
    assert_seat_table(probe, mutant, text, 'mutant: ')
    assert_reproduction(probe, text, committed, 'mutant: ')

    report.check('mutant fails the shared assertions', len(probe.failures) > 0,
                 '%d of %d checks fail' % (len(probe.failures), len(probe.checks)))
    report.check('mutant fails the neutral-frame check',
                 any('neutral' in failure for failure in probe.failures))
    report.check('mutant fails the frame-range check',
                 any('frame 0' in failure or 'below the first cell' in failure
                     for failure in probe.failures))
    report.check('mutant fails the reproduction check',
                 any('generated effect is the committed file' in failure
                     for failure in probe.failures))
    report.note('0-based mutant rejected by %d of %d shared checks'
                % (len(probe.failures), len(probe.checks)))


def main():
    report = base.Report(detail='--detail' in sys.argv)
    module = load_builder(ROOT / BUILDER_PATH, 'build_spain_cortes_hemicycle')

    if '--mutant' in sys.argv:
        report.start('mutant')
        test_mutant(report, module)
        return 0 if report.summary() else 1

    for group, function in (
        ('source', test_builder_source),
        ('effect', test_committed_effect),
        ('mutant', test_mutant),
    ):
        report.start(group)
        function(report, module)

    return 0 if report.summary() else 1


if __name__ == '__main__':
    sys.exit(main())
