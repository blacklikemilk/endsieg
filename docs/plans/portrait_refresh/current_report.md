# Portrait refresh — current state

## What this pass was

The head-of-state refresh re-renders every leader portrait in the mod through the
Endsieg-tone ComfyUI workflow, in slices, so the GPU work can run hourly without
blocking a session.
The reviewed install step (`portrait_install.py`) is separate from rendering: nothing
reaches `gfx/leaders` without an explicit `--apply`.

## Passes and their state

| pass | targets | done | renders at |
| --- | --- | --- | --- |
| `leaders_mono` | 16 | 16 | `.tmp/portrait_runs/leaders_mono` |
| `leaders_world` | 137 | 137 | `.tmp/portrait_runs/leaders_world` |
| `leaders_overrides` | 80 | 80 | `.tmp/portrait_runs/leaders_overrides` |

All three passes are complete.
The last slice ran on 2026-10-26 from 08:13 to 09:24 and finished `leaders_overrides`
with 77 portraits (`stage leaders_overrides produced 77 portrait(s), exit code 0` in
`.tmp/portrait_runs/passes5.log`).

## Known gap: the target lists were lost

The three target lists (`leaders_mono.txt`, `leaders_world_rest.txt`,
`leaders_vanilla_overrides.txt`) lived in this folder, which was untracked in git, and
the whole folder went missing from the working tree after the 09:24 slice.
They are not recoverable from git.
`resume_passes.py` now refuses to report a stage as finished when its target list is
absent, because a missing list counts as zero targets and used to print
`all stages complete` for a stage that had never been planned.

How each list was derived, so they can be rebuilt if the pass is ever re-run:

- `leaders_mono.txt` — every record in `.tmp/portrait_runs/leaders/manifest.jsonl`
  whose `source_stats.mean_saturation` is below 35, written as `source_dds` paths
  relative to the mod root.
- `leaders_world_rest.txt` — `leader_index.py --write` for the mod-owned head-of-state
  sprites, split by the European tag list in `europe_tags.txt`, keeping the
  non-European half.
  The European run itself is `.tmp/portrait_runs/leaders` (90 targets).
- `leaders_vanilla_overrides.txt` — heads of state still on vanilla art, 80 of them,
  rendered with `--no-dedupe` so no render is shared between two tags.

## Installation

227 renders were installed to `gfx/leaders` on 2026-10-26 08:14 from the `leaders`,
`leaders_mono` and `leaders_world` runs
(`.tmp/portrait_runs/leaders/install_20261026-081428.jsonl`).
The 80 `leaders_overrides` renders are finished but **not installed**, because the
install step is reviewed rather than automatic.

Next reviewed step:

    python .tools/portrait_pipeline/portrait_install.py --run .tmp/portrait_runs/leaders_overrides --apply
