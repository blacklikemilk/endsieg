# C7 handoff: Qing survival is earned and the all-China annexation is gone

Card: `t_a2961bf2`, C7, 2026-10-26, Developer (`endsieg-developer`, DeepSeek V4.1 Flash / OpenCode Go).
Branch `TeknoDev-Branch`, no commit, no launch, no premium route, no focus or artwork change.

## What changed and what it does now

### 1. The historical rule no longer railroads a human player

`qing_historical_collapse` now requires `is_ai = yes`.
A human Qing on the historical focus is not scripted to lose.
It faces `qing_historical_pressure`, a second and higher survival bar (`survival_*_pressure`, base plus 10), and loses standing once when Wuchang rises (`revolution_pressure = -10`, applied by the tick).
An AI Qing on the historical focus still collapses exactly as before.
`qing_survival_possible` reads the pressure bar through an explicit `OR` of two `AND` branches because trigger blocks cannot branch.

### 2. The settlement window is war-gated and has an armistice deadline

The old window was `date > 1911.9.1`, five weeks before the uprising, so a reformed court could settle before the revolution began.
It is now opened only by the war detector in `qing_campaign_tick`:

- `date > 1911.10.9`, `has_war_with = RCH`, and `qing_revolution_window_seen` unset;
- opening the window schedules `qing_campaign.19` with `@qing_armistice_days` (90, mirroring `armistice_days`), a hidden timer that sets `qing_armistice_closed` unless the regime already settled;
- `qing_armistice_open` = window seen and not closed;
- `qing_end_revolution`, all four `qing_settle_*` route effects, `qing_campaign.23` and `qing_campaign.62.b` all require `qing_armistice_open`.

Before Wuchang the flag cannot exist, so survival cannot pre-empt Wuchang. After the deadline nothing can settle.

### 3. `qing_campaign.62.b` is gated and readable

`QW1_abdication_question` fires `qing_campaign.62`.
Option b was a silent no-op under the historical rule, because `qing_end_revolution` was already limited by `NOT = { qing_historical_collapse = yes }`.
It is now gated by `custom_trigger_tooltip = { tooltip = qing_campaign.62.b_tt qing_survival_possible = yes qing_armistice_open = yes }`.
The tooltip names the survival bar, the armistice, and the three possible outcomes.
`qing_settle_constitutional` and the other route effects are gated again on entry, so even a forced call cannot settle outside the window.

### 4. Three settlement outcomes replace the unconditional annexation

`qing_end_revolution` is now a router. It selects the strongest reachable form:

| Outcome | Effect | Gate | Result |
| --- | --- | --- | --- |
| Partition | `qing_revolution_partition` | `qing_armistice_open` | White peace, RCH survives in the south, no states transferred, no cores, +50 political power and +0.10 stability |
| Reunion | `qing_revolution_reunion` | armistice, `qing_survival_possible`, political power above 75 | RCH annexed with `transfer_troops = no`, charged 75 political power, no southern cores |
| Conquest | `qing_revolution_conquest` | armistice, `qing_can_impose_settlement` (Beijing held, army loyal, reform or Yuan), political power above 50 | RCH annexed with `transfer_troops = no`, charged 50 political power, no southern cores |

`annex_country` does not create cores, and none of the three outcomes calls `add_core_of` or `set_state_owner_to`.
A partition sets `qing_settlement_partition`, which suppresses the 1914 and 1936 ownership repairs, so the Republic is not quietly swept back into Beijing by bookkeeping.

### 5. The reclaim sweep is closed

`endsieg_china_reclaim_states` previously took every state on the Asian continent owned by CHI, RCH, YUN, GXC, XSM, SIK, SHX, MAN, PRC or SND, plus states 609 and 743 unconditionally, and granted a core on each. State 743 is Qingdao, a German concession the 1910 Qing never owned.

It now matches only the 55 states that

- `history/states` gives to QIN in the undated 1910 block, and
- a dated block hands to a Chinese successor government without stripping the Qing core,
- and only while one of those successor governments holds them.

Tibet, Mongolia and Tannu Tuva are given independence by the same dated blocks and are outside the successor tag set, so they stay out of the sweep. States ceded to Japan, Germany or Mengjiang stay out too. One core grant remains and it is inside the state loop.

Provenance: derived from `history/states/*.txt` by `.tools/tests/test_qing_survival.py`, which recomputes the set from the scenario on every run.

### 6. Inherited localisation collision repaired

`qing_campaign.20.d`, `.22.d` and `.23.d` were each used twice, once as the event description and once as option d, so option d could only ever display the description paragraph and the engine logged duplicate keys.
The three description keys are now `.20.desc`, `.22.desc` and `.23.desc`.
No event, option or focus id changed.

## Changed files

| File | Change |
| --- | --- |
| `common/script_constants/qing_campaign.txt` | Added `survival_*_pressure`, `revolution_pressure`, `armistice_days`, `settlement_treasury_reunion/conquest`, `settlement_price_reunion/conquest` |
| `common/scripted_triggers/qing_campaign.txt` | `is_ai` on the historical collapse, `qing_historical_pressure`, `qing_survival_bar`, `qing_survival_bar_pressure`, rewritten `qing_survival_possible`, `qing_armistice_open`, `qing_can_settle_partition/reunion/conquest` |
| `common/scripted_effects/qing_campaign.txt` | `@qing_armistice_days`, war-gated window with deadline and pressure, partition guard on both ownership repairs, `qing_end_revolution` router, three outcome effects, four gated route effects |
| `events/qing_campaign.txt` | New hidden `qing_campaign.19`, gated `.62.b` with tooltip, readable tooltips on the gated `.20`/`.22`/`.23` options, description key repairs |
| `common/scripted_effects/endsieg_china_ownership.txt` | Closed 55-state reclaim set with the successor tag guard, state 743 and the continent selector removed |
| `localisation/english/qing_campaign_events_l_english.yml` | `.19.a`, nine option tooltips, `.62.b_tt`, rewritten `.20`/`.21`/`.22` descriptions, three description key repairs |
| `.tools/tests/test_qing_survival.py` | New source test, eight sections, mutant controls against `f6d12527cc8a` |

## Validation actually run

- `python .tools/tests/test_qing_survival.py` — 8 sections, all PASS, exit 0, baseline `f6d12527cc8a3ed3cda6e533528f46bbba4d6e17` rejected by every mutant control. Sections: historical gate, war-gated window, abdication gate, three outcomes, reclaim sweep, preserved ids/options/weights, localisation coverage, constants and literals.
- `hoi4.script_validate` `path` on all five changed script files, 0 findings. `events/qing_campaign.txt` returned `SCRIPT_CHECKED` with `valid: true` (298 commands, 0 unresolved). The three `scripted_*` files returned `SCRIPT_CHECK_PARTIAL` because scripted files have no declared scope (`unknownScopeRoots`), with 0 findings and 0 unresolved commands; `common/script_constants/qing_campaign.txt` is reported as an unsupported family, so it is covered only by the source test.
- `hoi4.focus_inspect` `treeId=qing_ww1`, before edits: 158 focuses, `layoutHash f87a888babdef3fd`, 106 diagnostics, no blocking diagnostics.
- `hoi4.event_inspect` `mode=scan`, `selector={kind: namespace, namespace: qing_campaign}`, before edits: revision `f5af5aeafa909b9e`, `analysisMode: focused`, 0 blocking diagnostics.
- `hoi4.script_validate` source probes for `has_political_power > constant:...` and `add_political_power = constant:...`: both accepted, but `parametersChecked: false`, so the shipped script uses a documented literal mirror instead of an unverified constant in a comparison operand.
- Vanilla precedent read: `custom_trigger_tooltip` in trigger context (`common/decisions/AFG.txt:732`, `common/scripted_triggers/00_scripted_triggers.txt:37`), `white_peace` and `annex_country` in event options (`events/AAT_Denmark.txt`, `events/AAT_Finland.txt`), `state = <id>` as a state-scope trigger (`common/achievements.txt:1159`), and `is_ai` scope (`documentation/triggers_documentation.md:5244`).

## Explicitly not performed

- No game launch. Nothing here is in-game evidence; no player click, popup, tooltip render or AI choice was observed.
- No QA. Independent `endsieg-qa` review is required and has not happened.
- No commit, no staging, no branch or worktree operation.

## Open items for Director

1. `docs/systems/qing_campaign.md` and `docs/systems/rch_campaign.md` still describe the pre-repair behaviour (settlement annexes the Republic; the sweep keeps every Chinese state). Both files are outside this card's ownership and need a follow-up edit.
2. The 1936 dated block cedes state 609 to Japan and strips the Qing core. The tag guard leaves it with Japan rather than seizing it back; if a surviving Qing is meant to hold it, that is a separate design decision.
3. `qing_campaign.21` still offers a single "prepare the capital" option after the war has begun with no settlement possible; it is deliberately not a choice, but a later slice may want the redoubt decisions to react to it.
4. The settlement costs 75 and 50 political power for reunion and conquest. Those figures are first-pass balance and have no playtest behind them.
