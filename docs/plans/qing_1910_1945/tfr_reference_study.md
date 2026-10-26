# TFR reference study for the Qing overhaul

## What was inspected

Read-only inspection of `C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356`.

| File | What it shows | What Endsieg takes from it |
| --- | --- | --- |
| `common/national_focus/TFR_national_focus_CHI.txt` | A single-country tree whose branches carry `allow_branch` on the branch root, dormant nodes use `available = { always = no }`, and rewards fire country events with `hidden_effect` plus separate `custom_effect_tooltip` | Branch locks on every continuation node, not only the settlement node, and rewards that fire events rather than only modifiers |
| `common/national_focus/TFR_national_focus_PRC.txt`, `TFR_national_focus_PRC_centrist.txt`, `_liberal`, `_nationalist`, `_new_left`, `_nationalist_old` | Separate authored trees per political outcome, with `country = { factor = 0 modifier = { add = ... original_tag = ... } }` | One chapter tree per era plus route-locked branches, rather than one tree per faction (fewer files, same outcome control) |
| `events/TFR_events_PRC.txt` (multiple `load_focus_tree` calls) | Trees are swapped from event options when a political outcome is reached, not from on_actions | The Qing swaps chapters from a dated tick that fires a milestone event, and swaps route presentation inside that event |
| `common/scripted_effects/TFR_scripted_effects_PRC.txt` | `load_focus_tree = generic_focus` fallback when a route ends | The Qing self-heals its chapter tree every day and falls back to `generic_focus_ww1` only if the campaign flag is lost |
| `common/bop/TFR_bop_PRC.txt` | Balance of power with a centre range, side ranges, `on_activate`/`on_deactivate` swapping ideas and setting flags | The Qing balance sets and clears the flags focuses read, and swaps the regime spirit through a refresh effect |
| `common/decisions/TFR_decisions_CHI.txt` | Decisions written as missions with `activation`, `available`, `days_mission_timeout`, `timeout_effect`, `complete_effect`, and category blocks keyed by category id | Qing decisions use timed missions for reform programmes and immediate decisions for court moves |
| `common/scripted_guis/TFR_PRC_GUI.txt`, `TFR_scripted_guis_GER.txt` | Country-specific windows for values that do not fit a decision row | Not copied: the Qing keeps its values in native surfaces (balance panel, decision headers, spirit tooltips) to avoid a bespoke panel |

## Mechanisms judged compatible with this HOI4 version

- `load_focus_tree = { tree = ... keep_completed = yes }` with `mark_focus_tree_layout_dirty`: already used by Iran, Spain, Japan and Turkey in this repository.
- Balance of power with `decision_category`, `range`, `side`, `on_activate`, `on_deactivate`: requires Arms Against Tyranny, which the maintainer has installed.
- Event options swapping trees and setting route flags: used by TFR and already used by Endsieg for Japan's interwar transition.
- Mission-style decisions with `days_mission_timeout`: native and already used across Endsieg.

## Mechanisms deliberately not copied

- TFR's custom scripted GUIs, because the Qing mechanic maps cleanly onto the native balance panel and decision categories.
- TFR's tree-per-faction file layout, because the repository's era-chapter convention is one file per era with locked branches and that keeps continuity flags in one place.
- TFR's art and text, which are not reused.
