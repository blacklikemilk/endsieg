# Qing China, 1910–1945

## What the system is

The Qing overhaul gives China a second history that branches from the 1910 start.
The dynasty can survive the Xinhai revolution through one of four settlements and then carry a Qing government through the First World War, the interwar crisis and the Second Sino-Japanese War.
When the dynasty falls, the existing Republic of China chain runs untouched.

## Files

| File | Role |
| --- | --- |
| `common/script_constants/qing_campaign.txt` | All tuning values, `constant:qing_story.*` |
| `common/scripted_triggers/qing_campaign.txt` | Route, value-band, survival and continuity triggers |
| `common/scripted_effects/qing_campaign.txt` | Initialisation, chapter routing, tick, settlement, projects |
| `common/on_actions/qing_campaign.txt` | `on_daily_QIN` only, no world scan |
| `common/national_focus/qing_ww1.txt` | Chapter one, 1910–1918, 88 focuses |
| `common/national_focus/qing_interwar.txt` | Chapter two, 1919–1935, 85 focuses |
| `common/national_focus/qing_ww2.txt` | Chapter three, 1936–1945, 65 focuses |
| `common/decisions/qing_campaign.txt` | 38 decisions in four categories |
| `common/decisions/categories/qing_campaign.txt` | Category metadata, gated by date and state |
| `common/bop/QIN.txt` | `QIN_throne_and_assembly` balance |
| `common/ideas/qing_campaign.txt` | Three-slot regime, army and pressure spirits |
| `common/characters/qing_campaign.txt` | Yuan Shikai, Puyi, Liang Qichao |
| `events/qing_campaign.txt` | 33 events, 76 options |
| `common/ai_strategy_plans/QIN_campaign_AI_strategy_plan.txt` | Historical and constitutional plans |
| `localisation/english/qing_*.yml` | Six English files, complete coverage |

## Flow

1. `on_startup` reaches the QIN branch and calls `qing_initialize_campaign`.
2. The initialiser sets the five values, adds the regency spirit, loads `qing_ww1`, sets `qing_bootstrap_pending` and fires `qing_campaign.1`.
3. The first `on_daily_QIN` tick runs `qing_bootstrap`, which creates the balance of power once and refreshes the layout.
4. The tick fires the dated milestones: the reform edict, the railway crisis, the revolution window, the Great War, the chapter boundaries, the succession, the Manchurian crisis, the war, the Pacific and the victory.
5. The revolution is settled either before Wuchang (a reformed dynasty), by a strong army, or by a court council during the war.
   A settlement annexes the Republic, sets exactly one route flag, replaces the leader, and writes `qing_xinhai_settled` as a global flag.
6. `qing_xinhai_settled` suppresses the historical `ww1_china` revolution events through a trigger on each of them.
   Without the flag nothing changes and the historical chain is the one that runs.

## Values and presentation

| Value | Moved by | Read by |
| --- | --- | --- |
| `qing_legitimacy` | court focuses, decisions, crises | regime spirit tier, decisions, events |
| `qing_reform` | reform focuses, edicts, projects | survival gate, constitutional route, decisions |
| `qing_army_loyalty` | army and Beiyang focuses, pay decisions | survival gate, coup and settlement checks |
| `qing_provincial_trust` | provincial focuses, assemblies, relief | survival gate, federal route |
| `qing_yuan_influence` | Yuan focuses and commission | Yuan route gate, settlement |

`qing_refresh_mechanics` keeps exactly one regime spirit, one army spirit and one pressure spirit.
The balance of power shows the same struggle natively and its ranges set the flags focuses read.

## The two histories

| Path | Trigger | Result |
| --- | --- | --- |
| Historical collapse | the dynasty fails the survival and imposition checks | `ww1_china.3` fires as before, the provincial uprisings run, `ww1_china.19` abdicates and the Republic inherits China |
| Surviving Qing | a settlement in `qing_campaign.20`, `.22` or `.23` | the Republic is annexed, a route flag is set, the chapters continue to 1945 |

The 1914 and later bookmarks never initialise the campaign because the Qing owns no states there.
The 1936 and 1944 bookmarks are untouched.

## Tuning

All values live in `common/script_constants/qing_campaign.txt`.
Effects that take integer-only fields (`army_experience`, `air_experience`, `navy_experience`, `add_manpower`, `add_extra_state_shared_building_slots`) use literal values there because the fields reject `constant:` references.
The literals mirror the constants file, so a change to the tuning must be made in both places and the comment in the constants file records it.

## Known engine risks to verify in a live launch

- `set_power_balance` on the first daily tick rather than in `on_startup`.
- The chapter tree load from the startup hook.
- `qing_xinhai_settled` suppressing the `ww1_china` events without breaking the historical chain.
- `annex_country` on the Republic during the settlement.
