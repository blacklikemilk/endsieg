# Retired: Industrial Society national spirits

## What the mechanic was

A five-step industrial ladder granted as country spirits: `agrarian_society`, `pre_industrial_society`, `early_industry`, `basic_industry` and `heavy_industry`, displayed as Agrarian Society, Pre-Industrial Society, Early Industrial Society, Basic Industrial Society and Industrial Society.
Each step carried research speed penalties (and, from `early_industry` upward, milder or positive bonuses) plus stability, conscription, training time and construction modifiers.
The ladder was advanced by a shared focus chain, `shared_industrialisation` and its fourteen follow-up focuses, and each level-up focus fired an `industrialisation.N` event whose only effect was `remove_ideas` on the previous level and `add_ideas` on the next one.

## Why it was removed

The design owner retired the mechanic outright; countries should no longer carry an industrial-level spirit of any kind.
The ladder was also the source of the visible penalty tooltips on minor countries, which is what prompted the removal.

## What was removed

- `common/ideas/_industrialisation.txt` (the five idea definitions).
- `common/national_focus/_shared_industrialisation.txt` (fifteen shared focuses).
- `events/IndustrialisationEvents.txt` (the `industrialisation` namespace, events 1 to 18 including the four duplicate-cleanup events).
- `shared_focus = shared_industrialisation` from `WWI - Generic`, `WWI - Russian Empire`, `INT - RCW - White Russia` and the commented line in `INT - RCW - Soviet Russia`.
- Every `add_ideas` and `remove_ideas` reference to the five spirits in `history/countries`, together with the `add_ideas = { }` blocks that were left empty by that removal, and one `remove_ideas = basic_industry` in the Soviet history.
- Every `complete_national_focus` line pointing at `shared_industrialisation` or any of the fourteen follow-up focuses.
- The idea loc keys in `endsieg_ideas_l_english.yml`, the event block in `endsieg_WW1_events_l_english.yml`, `industrialisation_tooltip_up` in `endsieg_tooltips_l_english.yml`, and the fifteen focus name and description keys in `endsieg_focus_l_english.yml`.
- Thirty dead `WW2_*industrial*` focus loc keys in `endsieg_focus_l_english.yml` that had no focus left to display them.
- The five idea icon sprites and DDS files, the fifteen unused `GFX_focus_ww1_pdx_native_shared_*industrial*` sprites and DDS files, and the three event pictures used only by the removed events.

`GFX_report_event_basic_industry` is kept: `events/INT - Soviet Union.txt` and `events/spain_campaign.txt` still use it as a generic picture.

## What was deliberately left alone

The starting industry of countries that had the chain pre-completed is not compensated; those countries simply lose the two instant industrial complexes the focus reward used to give them.
The separate WW1 industry chain `shared_GEN_industrial_effort` in `common/national_focus/_shared_WW1_industry.txt` is untouched, as are all country-specific industrial spirits such as `GE1_RH_industrial_survey` or `INT_SOV_industrial_push`.

## Reintroducing it

Any new industrial-level spirit needs its own ideas file, its own grant path and its own localisation; the old shared focus chain and `industrialisation` namespace no longer exist, so copying an old focus file in will fail on missing events.
Spirits must be granted with `add_ideas` from a decision, focus or event that is actually reachable, not by history pre-completion alone, or the level-up events will never fire.
