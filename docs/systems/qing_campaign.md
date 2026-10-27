# Qing China, 1910–1945

## What the system is

The Qing overhaul gives China a second history that branches from the 1910 start.
The dynasty can survive the Xinhai revolution through one of four route settlements, and each route ends the war in one of three territorial outcomes: partition, reunion or conquest.
When the dynasty falls, the existing Republic of China chain runs untouched.

## Files

| File | Role |
| --- | --- |
| `common/script_constants/qing_campaign.txt` | All tuning values, `constant:qing_story.*` |
| `common/scripted_triggers/qing_campaign.txt` | Route, value-band, survival and continuity triggers |
| `common/scripted_effects/qing_campaign.txt` | Initialisation, chapter routing, tick, settlement, projects |
| `common/on_actions/qing_campaign.txt` | `on_daily_QIN` only, no world scan |
| `common/national_focus/qing_ww1.txt` | Chapter one, 1910–1919, 158 focuses |
| `common/national_focus/qing_interwar.txt` | Chapter two, 1919–1935, 99 focuses |
| `common/national_focus/qing_ww2.txt` | Chapter three, 1936–1945, 65 focuses |
| `common/decisions/qing_campaign.txt` | 45 decisions in five categories |
| `common/decisions/categories/qing_campaign.txt` | Category metadata, gated by date and state |
| `common/bop/QIN.txt` | `QIN_throne_and_assembly` balance |
| `common/ideas/qing_campaign.txt` | Three-slot regime, army and pressure spirits |
| `common/characters/qing_campaign.txt` | Yuan Shikai, Puyi, Liang Qichao |
| `events/qing_campaign.txt` | 38 events, 89 options |
| `common/ai_strategy_plans/QIN_campaign_AI_strategy_plan.txt` | Historical and constitutional plans |
| `localisation/english/qing_*.yml` | Six English files, complete coverage |

## Flow

1. `on_startup` reaches the QIN branch and calls `qing_initialize_campaign`.
2. The initialiser sets the five standing values, adds the regency spirit, loads `qing_ww1`, sets `qing_bootstrap_pending` and fires `qing_campaign.1`.
3. The first `on_daily_QIN` tick runs `qing_bootstrap`, which creates the balance of power once and refreshes the layout.
4. The tick fires the dated milestones: the reform edict, the railway crisis, the revolution window, the Great War, the chapter boundaries, the succession, the Manchurian crisis, the war, the Pacific and the victory.
5. The revolution window opens on the war itself: after 9 October 1911, while the court is at war with the Republic, the tick arms it and offers the first terms.
6. The armistice the powers broker closes it again after `constant:qing_story.armistice_days`, when `qing_campaign.19` sets `qing_armistice_closed`.
7. `qing_armistice_open` is the gate every settlement effect reads, so nothing can be settled before the garrison rises and nothing after the deadline passes.
8. Four events can settle inside the window: `qing_campaign.20` for a dynasty that meets the survival bar, `qing_campaign.22` for a court that holds the capital with a loyal army, `qing_campaign.23` for the court council during the armistice, and `qing_campaign.62` for the abdication question.
9. A settlement sets exactly one route flag — constitutional, authoritarian, Yuan or federal — replaces or promotes the leader, and writes `qing_xinhai_settled` as a global flag.
10. `qing_xinhai_settled` suppresses the historical `ww1_china` revolution events through a trigger on each of them.
11. Without the flag nothing changes and the historical chain is the one that runs.

## The settlement router

`qing_end_revolution` decides the territorial outcome after the political route has been chosen, and it tries the three forms in this order.

| Outcome | Gate | What it does |
| --- | --- | --- |
| Conquest | `qing_can_settle_conquest`: the armistice is open, the court holds the capital with a loyal army and can pay the settlement price | `qing_revolution_conquest`, the Beiyang army dictating terms |
| Reunion | `qing_can_settle_reunion`: the armistice is open and the survival bar is met at its own price | `qing_revolution_reunion`, the assembly accepting the monarchy |
| Partition | `qing_can_settle_partition`: the armistice is open, and neither of the two stronger forms is available | `qing_revolution_partition`, the war stopping where the armies stand |

Every outcome ends the war with `white_peace = RCH` while the two countries are at war, sets one settlement flag, and moves political power and stability.
Reunion and conquest also move a standing value — reunion gains `qing_legitimacy`, conquest gains `qing_army_loyalty` while it loses legitimacy — so partition is the only one of the three that leaves the standing values untouched.
The court pays the price of reunion or conquest and is paid for a partition.
Reunion and conquest then annex the Republic while it still exists, through `annex_country = { target = RCH transfer_troops = no }`.
Annexation is therefore one branch of the router and never its general case.
Partition annexes nothing and transfers no state: the Republic stays alive, and because the partition flag also excludes the 1914 and 1936 state reclaim, the Qing keeps every state it holds and no handover runs.
The Republic owns no state in the 1910 base block, and the dated 1914 history blocks that would give it the Chinese states run only for a start date after 1 January 1914, so partition is a survival, not a grant of the south.
No outcome of the router adds a core to any state in script.

## Values and presentation

| Value | Moved by | Read by |
| --- | --- | --- |
| `qing_legitimacy` | court focuses, decisions, crises | regime spirit tier, decisions, events |
| `qing_reform` | reform focuses, edicts, projects | survival gate, constitutional route, decisions |
| `qing_army_loyalty` | army and Beiyang focuses, pay decisions | survival gate, coup and settlement checks |
| `qing_provincial_trust` | provincial focuses, assemblies, relief | survival gate, federal route |
| `qing_yuan_influence` | Yuan focuses and commission | Yuan route gate, settlement |
| `qing_consolidation` | derived by `qing_consolidation_refresh`, never bought directly | interwar gate, restoration band, consolidation decisions |

`qing_consolidation_refresh` divides the four standing values by `constant:qing_story.consolidation_family_divisor` and adds `constant:qing_story.consolidation_works_points` for each completed work, then clamps the result.
`qing_refresh_mechanics` keeps exactly one regime spirit, one army spirit and one pressure spirit.
The balance of power shows the same struggle natively and its ranges set the flags focuses read.

## The two histories

| Path | Trigger | Result |
| --- | --- | --- |
| Historical collapse | the dynasty fails the survival and imposition checks | `ww1_china.3` fires as before, the provincial uprisings run, `ww1_china.19` abdicates and the Republic inherits China |
| Surviving Qing | a settlement inside the armistice window | one route flag and one settlement outcome, and the chapters continue to 1945 |

The interwar chapter does not open on the calendar: `qing_open_chapter_two` loads `qing_interwar` only once `qing_consolidation` stands at `constant:qing_story.consolidation_gate`.
A full `constant:qing_story.consolidation_hold_days` at that level opens the restoration band inside the chapter.
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
- `annex_country` on the Republic in the reunion and conquest outcomes, resolving after a white peace and only while the Republic exists.
- The derived `qing_consolidation` reading its opening value on a 1910 start, because the divisor is placed in a variable before the math block.
