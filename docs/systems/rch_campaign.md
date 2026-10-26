# Republic of China, 1912-1936

## What the system is

The Republic of China has its own three chapters, its own routing and its own decisions, so a player who follows the historical collapse is not left on the generic WWI tree.
The historical Qing collapse still runs through the existing `ww1_china` events; the Republic then continues under `rch_campaign` until 1936, when it hands over to the Waking the Tiger tree that every later bookmark already uses.

## Files

| File | Role |
| --- | --- |
| `common/script_constants/rch_campaign.txt` | Tuning, `constant:rch_story.*` |
| `common/scripted_triggers/rch_campaign.txt` | Route, value-band and continuity triggers |
| `common/scripted_effects/rch_campaign.txt` | Initialisation, chapter routing, tick, settlements, projects |
| `common/on_actions/rch_campaign.txt` | `on_daily_RCH` only |
| `common/national_focus/rch_republic.txt` | 1912-1919, 51 focuses |
| `common/national_focus/rch_warlord.txt` | 1919-1927, 50 focuses |
| `common/national_focus/rch_nanjing.txt` | 1928-1935, 45 focuses |
| `common/decisions/rch_campaign.txt` | 17 decisions in three categories |
| `common/decisions/categories/rch_campaign.txt` | Category metadata, date gated |
| `common/ideas/rch_campaign.txt` | Ten spirits in three slots |
| `events/rch_campaign.txt` | 16 events, 38 options |
| `common/ai_strategy_plans/RCH_campaign_AI_strategy_plan.txt` | Historical and parliamentary plans |
| `localisation/english/rch_*.yml` | Complete English coverage |

## The missing 1918 tree, and what actually caused it

The Republic was not missing a tree file. It was missing a tree.

At the 1910 start the Republic owns no states, so the startup hook skipped it as dormant and never assigned a tree.
When the revolution gave it states, the only thing that assigned a tree was the generic WWI fallback in the daily sweep, so a continuous campaign reached 1912 and 1918 with the generic tree and nothing Chinese in it.
A 1914 or 1918 bookmark got the same generic tree for the same reason.

Three changes fix it:

1. `on_startup` now has an explicit `tag = RCH` branch that calls `rch_initialize_campaign`, before the generic fallback.
2. The daily sweep's generic fallback list now excludes `RCH`, and `on_daily_RCH` self-heals the correct chapter if anything else ever replaces it.
3. The historical collapse event (`ww1_china.19`) and the intermission event (`ww1_china.28`) call `rch_initialize_campaign` in the Republic scope immediately after the annexation, so the player has a tree on the day the tag changes.

## Chapters

| Chapter | Tree id | Window | Loaded by |
| --- | --- | --- | --- |
| The Early Republic | `rch_republic` | before 1919.1.1 | startup hook, collapse event, daily self-heal |
| The Warlord Era | `rch_warlord` | 1919.1.1 - 1927.12.31 | daily tick at the era boundary |
| The Nanjing Decade | `rch_nanjing` | 1928.1.1 - 1935.12.31 | daily tick at the era boundary |
| Waking the Tiger China | `china_nationalist_focus` | 1936.1.1 onward | daily tick at the handover |

The handover loads the existing tree by id rather than copying the file, so the 1936 bookmark and a continuous campaign read the same content.

## Routes

| Route | Flag | Government |
| --- | --- | --- |
| Parliamentary | `rch_route_parliamentary` | Assembly and cabinet, elections on |
| Beiyang | `rch_route_beiyang` | Presidency and garrison commanders |
| Nationalist | `rch_route_kmt` | Party-state and party army |
| Provincial | `rch_route_provincial` | Compact of governors |

Routes are settled by the Second Revolution, Yuan's death or the Northern Expedition, and then lock the continuation bands in all three chapters.

## Values

`rch_legitimacy`, `rch_military_influence` and `rch_nationalist_support`, all 0-100 and presented through the regime, army and pressure spirits.
`rch_refresh_mechanics` keeps exactly one of each.

## Known limitation

A continuous campaign plays the Republic as `RCH`; the 1936 bookmark plays China as `CHI`.
The focus tree is the same, but decisions and events that gate on `original_tag = CHI` (the Waking the Tiger political-struggle system) do not apply to `RCH`.
Closing that gap needs either a tested tag transfer or an alias pass over the CHI decision and on_action files, and neither can be claimed without a live run.

## The 1936 crisis and the split

The scenario state history hands every Chinese state from QIN to RCH on 1 January 1914 and from RCH to CHI, YUN, GXC, XSM, SIK, SHX, MAN and PRC on 1 January 1936.
That transfer is a dated block in `history/states`, not a decision, so it used to fire regardless of play and left the player as a stateless RCH.

Two things now sit on top of it:

1. **A timed mission, `rch_save_the_republic`.** It opens in 1934, costs 150 political power to attempt, runs for 365 days, and is removed early only if the Republic holds Beijing, has legitimacy 60 or more, stability above 45 per cent, more than 100 political power, no war with Japan, and at least one flagship programme (constitution, currency, German mission, British loan or Whampoa).
   Succeeding grants the `rch_republic_endures` spirit and sets `rch_republic_saved`; timing out sets `rch_republic_failed` and costs stability and legitimacy.
2. **A 1936 settlement, `rch_settle_1936`.** On the first tick after 1 January 1936 it either reclaims every Chinese state for the Republic (if the mission succeeded) or hands the player to CHI with `change_tag_from`, so the player continues as the central government with the warlords splitting around them instead of being left with no land.

A surviving Qing is protected the same way: `endsieg_china_reclaim_states` runs in the Qing tick after 1914 and after 1936, so the dynasty keeps China instead of losing it to the Republic and then to the warlords.

The reclaim effect is `common/scripted_effects/endsieg_china_ownership.txt`; it takes every Asian state owned by a Chinese tag plus 609 and 743, sets owner, controller and core to ROOT.
