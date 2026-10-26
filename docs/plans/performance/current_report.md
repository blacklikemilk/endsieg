# Endsieg long-campaign performance review

## Status and disposition

Disposition: behavior-preserving maintenance optimizations implemented, with broader simulation changes queued for separately verified work.
The user approved implementation after the source review.
The implemented changes preserve event polling, combat AI intervals, recruitment balance, daily strain accumulation, and ration consumption.
No country is frozen and no historical content is removed.

## Implementation and verification

- `common/scripted_effects/endsieg_war_strain.txt`: preserve correct resolve and hardship spirits instead of removing and re-adding them daily.
- `common/scripted_effects/endsieg_war_crisis.txt`: preserve the current crisis spirit and remove only contradictory tiers.
- `common/scripted_effects/endsieg_rations.txt`: replace the pre-meal full display refresh with the stockpile read and clamp that consumption actually needs, retaining the final display and AI refresh.
- `.tools/performance/test_runtime_maintenance.py`: execute the actual changed helper bodies through a bounded fixture which fails on unsupported commands.

The spirit reconciliation still repairs missing spirits and contradictory saved tiers without adding persistent cache state.
Daily thresholds, accumulation, collapse checks, and existing player and AI call sites remain unchanged.
The affected spirit definitions have no lifecycle hooks whose behavior would change when redundant replacement stops.
No localisation or asset changes are necessary because no player-facing wording or presentation has changed.

Executed source tests passed for 4,160 strain boundary/saved-idea combinations, 72 crisis combinations, 960 initialized ration scenarios, and 18 first-day ration initialization comparisons.
Stable repeat calls perform no idea add/remove effects in the spirit fixture.
The ration fixture covers player and AI countries, shortage spirits, stockpile consumption, the final gauge, and production hysteresis.
These tests establish bounded source behavior, not engine timing or a complete Clausewitz simulation.
The independent feature-completion review passed the three-file patch with no semantic regression found, including 4,480 additional before/current ration comparisons.
That review's stale-report warning was addressed by replacing the original recommendations-only disposition with this implementation record.

A normal Endsieg launch reached the paused 1910 map, confirmed by `hoi4_screen`, and the game log records single-player entry at 21:39:49 and activity through 1910.1.2.3.
The fresh error log had zero lines naming the three changed helper files.
The full log contains other concrete diagnostics in country history and unrelated helper sections, so the whole mod is not described as log-clean.
Forced helper testing was refused because the provider identified the resumed autosave as Ironman.
A later time-control call reported `GameNotRunning`.
The inspected crash inventory had no folder newer than the 21:38:58 launch, leaving that session exit unclassified rather than attributed to a mod crash.
No forced-state, stable long-run, or throughput benchmark claim follows from this launch.
The desktop lock was released.

MCP source validation returned `WORKSPACE_CONTEXT_REQUIRED` on the initial request, and the corrected workspace request was blocked by the service circuit breaker.
Direct installed documentation, offline wiki, and executable source fixtures were used after the bounded attempts.

## Queued work and boundaries

The event-polling rewrite, military capacity, postwar establishment, regional invalidation, and native AI interval tuning below remain recommendations rather than implemented optimizations.
Changing those systems without their dedicated lifecycle and behavior comparisons would trade performance for unverified historical timing or AI changes.
The shared working tree contains ongoing changes from other work, which are outside this patch.
Rankings below describe optimization priorities, not measured CPU attribution or promised speedups.

## Executive recommendation

First remove recurring work that has no remaining gameplay purpose, then reduce automatic event polling through explicit event wiring, and integrate the existing military-capacity and postwar-establishment designs to restrain long-term army growth.
Treat map/interface frame rate, simulation throughput, periodic tick stalls, and save pauses as different performance problems.
Do not import TFR's optimization Lua file wholesale or freeze peripheral countries in the normal historical simulation.

## Evidence: event polling

| Source | Event processing offset | Source event definitions | Definitions without triggered-only yes |
|---|---:|---:|---:|
| Endsieg | 1 day | 9,277 | 838 |
| TFR | 30 days | 5,796 | 67 |
| Installed vanilla | 20 days | Not inventoried | Not inventoried |

Endsieg's override is `common/defines/endsieg_defines.lua:4`.
TFR's override is `common/defines/TFR_defines_changes.lua:74` under the approved Workshop reference root.
Vanilla documents the default and explicitly calls daily event checks CPU-heavy in `common/defines/00_defines.lua:301`.
The source inventory recognizes top-level event definitions and inspects their immediate fields, excluding nested event-fire effects and comments.
Of the automatic candidates, 748 Endsieg definitions and 6 TFR definitions declare MTTH.
These are source candidates, not a count of events evaluated every day in a running campaign, and do not resolve overrides, engine eligibility, completed one-shot events, or differing trigger costs.
A lower offset means more frequent polling opportunities, not a proportional whole-game slowdown.
The ignored scratch inventory and scanner are `.tmp/performance_audit/event_inventory.json` and `.tmp/performance_audit/scan.py`.

Recommended work:

- Move events that follow focus completion, war entry, occupation changes, or agreement responses to their actual source actions.
- Schedule dated historical events explicitly with pending/resolved guards and bookmark initialization.
- Keep final event triggers so changed circumstances can cancel an event correctly.
- Preserve MTTH distributions where randomness is intentional rather than replacing stochastic timing with fixed dates.
- Raise the global event-check interval only after polling-dependent content has been classified and timing regression tests exist.

Candidate review files include `events/WWII - Germany.txt` with 83 automatic candidates, `events/NewsEvents.txt` with 70, and `events/WWI - German Empire.txt` with 43.
Do not mass-convert events to triggered-only without supplying their callers.
The offline precedent is `paradox_wiki/Event modding - Hearts of Iron 4 Wiki.md:327–380`.

## Recurring work with concrete optimization opportunities

### Repeated terminal cleanup

`common/on_actions/endsieg_on_actions.txt:893–901` dispatches daily country tree-update helpers.
For example, `FR3_R_update_tree` at `common/scripted_effects/Endsieg_scripted_effects.txt:18695–18705` continues calling `FR3_R_clear_war_programmes` once its postwar condition remains true.
The cleanup repeats many idea-presence checks and the owned-state traversal at line 18815 after the temporary programmes have already been removed.
Similar paths exist for ENG and USA.
Separate terminal cleanup from ongoing tree and diplomacy maintenance, use a versioned completed-repair marker, and keep an ownership-aware route for subsequently acquired marked states.
A done flag alone is insufficient because conquest and release can transfer outstanding state markers.
Implementation review also found concrete external spirit regrants from repeatable British, French, and American decisions, so permanent cleanup skip flags were rejected for this pass.
The cleanup source remains byte-identical to the captured baseline, with detailed evidence in `subagent_handoffs/cleanup.md`.
The optimization requires a complete writer-invalidation contract rather than a local done flag.

### Daily spirit churn

The daily exhaustion caller at `common/on_actions/endsieg_exhaustion.txt:109–110` reaches strain and crisis updates.
`common/scripted_effects/endsieg_war_strain.txt:182–209` removes its possible spirits and restores the applicable ones.
`common/scripted_effects/endsieg_war_crisis.txt:119–136` does the same for crisis spirits.
Reconcile spirits only when the applicable band changes or the expected spirit is missing.
Keep daily accumulation, threshold semantics, crisis consequences, and externally removed-idea repair intact.
This is a lower-behavior-risk candidate than slowing the whole mechanic to monthly updates.

### Regional refresh and GUI invalidation

The AUH and TUR initialization paths also call their substantive regional refresh effects daily.
Relevant owners are `common/scripted_effects/WWI_AUH_stability.txt` and `common/scripted_effects/WWI_TUR_stability.txt`.
Separate initialization, monthly numerical drift, territorial refresh, and modifier reconciliation.
Use explicit invalidation when ownership, control, programme state, or selection changes, with a bounded recovery check.
The corresponding scripted GUIs, `common/scripted_guis/endsieg_auh_stability.txt` and `common/scripted_guis/endsieg_tur_stability.txt`, have no dirty variable.
Installed `common/scripted_guis/_documentation.md:102–105` documents updates every tick by default and the supported dirty-variable mechanism.
TFR uses this mechanism in `common/scripted_guis/TFR_brics_gui.txt:52` and several other list interfaces.
Cover every invalidation dependency to avoid stale readouts or controls.
These are player-side interfaces, not an all-country GUI cost.

### Weekly industrial reconciliation

`common/on_actions/endsieg_on_actions.txt:1984–1985` calls the war-industry effect weekly per country.
`common/scripted_effects/Endsieg_scripted_effects.txt:270–282` enters an owned-state iterator for peaceful countries in pre-1919-start campaigns, including countries without temporary war industry.
The post-1935 branch also continues this traversal.
Track candidate states or an ownership-maintained presence marker and inspect only relevant candidates.
Do not use only the original recipient's mobilized flag because industrial state markers can move with territory.
This is an aggregate state pass across country owners, not a country-squared world sweep.

### Narrow decision searches and tag dispatch

`common/decisions/WWI_home_front_decisions.txt:730` searches countries for a choice whose eligible partners are AUH, TUR, and BUL.
Replace that search with equivalent explicit tag predicates, preserving country-existence semantics.
Use static allowed filters, targeted prechecks, bounded target sets, and cheap early guards for construction and diplomatic decision families.
Installed `common/decisions/_documentation.md:6–44` documents which decision checks occur at startup/load, on interface refresh, or daily.
Move genuinely tag-specific branches from the long global daily dispatcher into tag hooks, while retaining bookmark and old-save repair routes.
No unconditional recurring country-squared world sweep was identified in the inspected Endsieg hooks.
Startup world iteration is not a recurring performance fault.

## Long-campaign force growth

`common/ai_strategy/army_construction.txt:1–16` encourages a minimum peacetime infantry army of 10 divisions.
Its industrial tiers request 20–150, while the suppression strategy at lines 248–265 only activates under restrictive conditions including 300 divisions, peace, and more than 99 military factories.
That is not a universal cap.
The enable and abort factory ranges disagree in several tiers, particularly the 40-division tier at lines 65–79.
Reconcile recruitment floors and emergency recruitment with the existing military-capacity and peacetime-establishment design rather than adding a competing system.
The existing design owner is `docs/specs/military_capacity/`, with settlement progress in `docs/plans/postwar_demobilisation/plan.md`.
The settlement scaffold is not an operating global demobilization system: the inspected source has no gameplay caller for `endsieg_settlement_begin` outside its definition.
Penalties alone are insufficient if the AI keeps producing units despite them.
Tune AI demand and recruitment behavior against capacity, maintain wartime exceptions, and validate actual unit counts after peace.
Include naval, air, equipment-variant, and template growth in runtime observations rather than assuming divisions explain every slowdown.
Do not lower demographic growth merely as a CPU optimization, because population is not individually simulated.

## TFR: transferable and unsuitable patterns

### Selective native AI intervals

| Define | Vanilla | TFR | Recommendation |
|---|---:|---:|---|
| DAYS_BETWEEN_CHECK_BEST_TEMPLATE | 7 days | 21 days | Candidate for controlled comparison |
| DAYS_BETWEEN_CHECK_BEST_EQUIPMENT | 7 days | 21 days | Candidate for controlled comparison |
| AI_UPDATE_ROLES_FREQUENCY_HOURS | 48 hours | 112 hours | Candidate with AI-response checks |
| UPDATE_SUPPLY_BOTTLENECKS_FREQUENCY_HOURS | 168 hours | 504 hours | Combat-sensitive; do not copy first |
| HOURS_BETWEEN_ENCIRCLEMENT_DISCOVERY | 72 hours | 168 hours | Combat-sensitive; do not copy first |
| AIFC_UPDATE_FREQUENCY_DAYS | 5 days | 10 days | Combat-sensitive; do not copy first |

TFR sources are `common/defines/TFR_00_optimization.lua:48–55`.
Vanilla sources are `common/defines/00_defines.lua:2523–2524,2697,3389–3392,3495`.
The doctrine interval in the same TFR file is 21 days versus vanilla's 30, making it more frequent rather than less frequent.
A static comparison found 74 of 148 assignments in the TFR optimization file lack a matching key in installed vanilla's define files.
This includes graphics and many proposed calculation-interval keys; absence does not conclusively establish engine behavior, but those assignments cannot be credited as demonstrated optimizations.
Vanilla already has an unbounded fifth speed setting in `common/defines/00_defines.lua:12`.
Changing lower speed settings is not evidence of reduced simulation cost.

### Peripheral-country freezing

TFR `common/on_actions/00_TFR_on_actions_ZZZ_startup.txt:771–779` disables production, locks templates, and sets research slots to zero for AI countries outside its relevance list.
This deliberately reduces simulation activity and development opportunities.
It is not an appropriate default for Endsieg's multi-decade campaign, in which initially peripheral countries can later become important.
Consider it only as a separately approved optional restricted-simulation mode with complete restoration paths.

### Demobilization and production reserves

TFR's generic economic demobilization decisions primarily roll laws back rather than remove fielded armies.
Its `PRODUCTION_EQUIPMENT_SURPLUS_FACTOR = 0.12` contrasts with vanilla's 0.8 and is not a safe global transplant for sustained world wars.
Avoid improving speed by silently weakening replacement stocks, combat response, or minor-country development.

## Verification plan for implementation

Establish fixed benchmark saves for prewar peace, WWI, postwar settlement, interwar development, WWII, and post-1945 conditions.
Include both a continuous 1910 campaign and fresh later-bookmark starts, because accumulated state and freshly initialized state are different workloads.
For each before/after comparison use the same save, country, camera, graphics settings, game build, mod revision, save behavior, and background workload.
Record real seconds per fixed block of game days, daily/weekly/monthly stalls, map and panel frame times, save durations, and force counts.
Repeat samples and report their variation rather than a single fastest result.
Separate no-debug player-throughput measurements from diagnostic profiling runs.
Installed `documentation/console_commands_documentation.md:1349–1352` advertises the profile command with on/off/print/clear arguments; its availability and output must be exercised before relying on it.
Do not treat observer mode as identical to a normal player campaign.
Compare behavior as well as speed: historical event dates, AI recruitment, equipment reserves, supply response, settlements, acquired-state cleanup, and saved/reloaded GUI state.
Apply small optimization batches so regressions and gains remain attributable.

## Simplifications, omissions, and blockers

No before/after runtime throughput, long-campaign, or FPS benchmark was completed.
The launch and its limitations are recorded in Implementation and verification above.
No speedup percentages are claimed and smooth performance through 1945 or 1964 is not established.
The earlier delegated probability review could not validate AI scenarios because its adapter targets 1.19.2 while the installed game is 1.19.3.
No probability weights, event schedules, AI recruitment policies, localisation, interface layouts, or assets were changed in this maintenance patch.
