# Republic of China, 1912-1936

## What the system is

The Republic of China has its own three chapters, its own routing and its own decisions, so a player who follows the historical collapse is not left on the generic WWI tree.
The historical Qing collapse still runs through the existing `ww1_china` events; the Republic then continues under `rch_campaign` until 1936, when it hands over to the Chinese tree the installed DLC provides.

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
2. The daily sweep's generic fallback list now excludes `RCH`, and `on_daily_RCH` restores the chapter tree if anything else replaces it, without re-firing the chapter event.
3. The historical collapse event (`ww1_china.19`) and the intermission event (`ww1_china.28`) call `rch_initialize_campaign` in the Republic scope immediately after the annexation, so the player has a tree on the day the tag changes.

## Chapters

| Chapter | Tree id | Window | Opened by |
| --- | --- | --- | --- |
| The Early Republic | `rch_republic` | before 1919.1.1 | `rch_open_chapter_one` |
| The Warlord Era | `rch_warlord` | 1919.1.1 - 1927.12.31 | `rch_open_chapter_two` |
| The Nanjing Decade | `rch_nanjing` | 1928.1.1 - 1935.12.31 | `rch_open_chapter_three` |
| China after 1936 | `china_nationalist_sea_focus`, `china_nationalist_focus` or `generic_focus` | 1936.1.1 onward | `rch_load_handover_tree` |

The handover loads an existing tree by id rather than copying the file, so a continuous campaign reads the same content as a 1936 start.

## One routing authority

`rch_campaign_tick` calls one effect, `rch_route_chapter`, and that effect is the only place in the Republic's script that loads a focus tree on a daily cadence.
Before this, the tick called `rch_ensure_chapter_tree` (driven by the stored chapter flag) and then `rch_route_chapter` (driven by the date), so every day from 1919 onward loaded two trees: the flag-driven one first and the date-driven one second.
The flag-driven pass is gone.

`rch_route_chapter` is one `if`/`else_if` chain over the date, with one band per chapter.

| Band | Date | Chapter flag | Tree |
| --- | --- | --- | --- |
| One | before 1919.1.1 | `rch_chapter_one` | `rch_republic` |
| Two | 1919.1.1 - 1927.12.31 | `rch_chapter_two` | `rch_warlord` |
| Three | 1928.1.1 - 1935.12.31 | `rch_chapter_three` | `rch_nanjing` |
| Four | 1936.1.1 onward | `rch_chapter_three` (record only) | the DLC tree from `rch_load_handover_tree` |

Each band does one of two things, never both.

- **Transition.** The band's own chapter flag is absent, so the band calls its opener.
  The opener sets the flag, clears the other two, loads the tree and fires the chapter event once.
  This is what carries a continuous pre-1919 campaign into the warlord era: on 1 January 1919 `rch_chapter_two` is absent, `rch_open_chapter_two` runs, and `rch_campaign.20` fires.
- **Recovery.** The band's chapter flag is already set, so the band only clears a stale sibling flag and reloads the chapter tree if something else replaced it.
  No event, no reward, no second flag.

Exactly one chapter flag is set at any time, so a chapter cannot be recorded twice and a skipped chapter cannot survive into the next band; the 1936 band records the Nanjing chapter and drops any sibling an older save still carries.

The date bands are the only chapter decision. `rch_initialize_campaign` still opens a chapter directly on the day the tag is created, so the player has a tree before the next daily tick; the first tick after that finds the flag already set and takes the recovery path.

## The 1936 handover

From 1 January 1936 the Republic stops being a chapter state.
`rch_settle_1936` runs once, gated by `rch_1936_settled`, and the two outcomes are handled separately:

- **Saved Republic** (`rch_republic_saved`): `endsieg_china_reclaim_states` keeps every Chinese state, and the Republic keeps playing as `RCH`.
  `rch_load_handover_tree` then gives it the Chinese tree the installed DLC provides, once.
- **Ordinary handover** (no saved-Republic flag): `CHI = { change_tag_from = ROOT }` moves the player to `CHI`.
  A pre-1936 scenario leaves `CHI` on `generic_focus_ww1`, so `rch_load_handover_tree` is called in the `CHI` scope and a `rch_1936_handover_tree` flag stops the Republic's tick from touching that country again.

`rch_load_handover_tree` follows the same DLC order as the 1936 setup in `common/on_actions/endsieg_on_actions.txt`: No Compromise, No Surrender gives `china_nationalist_sea_focus`, Waking the Tiger gives `china_nationalist_focus`, and neither gives `generic_focus`.
It loads nothing when the receiving country already holds the right tree.

The handover notice, `rch_campaign.35`, is gated by `rch_1936_handover_seen` and pays out once.
The previous test asked whether `china_nationalist_focus` was loaded, which was only ever true because the handover hardcoded that tree; under the DLC branch the test would repeat every day under any other tree.
The notice is still fired in the `RCH` scope, so in the ordinary handover it is queued for a country the player has just left and only the saved Republic sees it.
Changing the recipient needs an events-file decision and is not part of this repair.

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

A continuous campaign whose Republic survives 1936 keeps playing as `RCH`; the 1936 bookmark plays China as `CHI`.
The focus tree is the same, but decisions and events that gate on `original_tag = CHI` (the Waking the Tiger political-struggle system) do not apply to `RCH`.
The ordinary 1936 handover does not have that gap, because it moves the player to `CHI` itself; only the saved-Republic outcome still needs either a tested tag transfer or an alias pass over the CHI decision and on_action files, and neither can be claimed without a live run.

## The 1936 crisis and the split

The scenario state history hands every Chinese state from QIN to RCH on 1 January 1914 and from RCH to CHI, YUN, GXC, XSM, SIK, SHX, MAN and PRC on 1 January 1936.
That transfer is a dated block in `history/states`, not a decision, so it used to fire regardless of play and left the player as a stateless RCH.

Two things now sit on top of it:

1. **A timed mission, `rch_save_the_republic`.** It opens in 1934, costs 150 political power to attempt, runs for 365 days, and is removed early only if the Republic holds Beijing, has legitimacy 60 or more, stability above 45 per cent, more than 100 political power, no war with Japan, and at least one flagship programme (constitution, currency, German mission, British loan or Whampoa).
   Succeeding grants the `rch_republic_endures` spirit and sets `rch_republic_saved`; timing out sets `rch_republic_failed` and costs stability and legitimacy.
2. **A 1936 settlement, `rch_settle_1936`.** On the first tick after 1 January 1936 it either reclaims every Chinese state for the Republic (if the mission succeeded) or hands the player to CHI with `change_tag_from`, so the player continues as the central government with the warlords splitting around them instead of being left with no land.

A surviving Qing is protected the same way: `endsieg_china_reclaim_states` runs in the Qing tick after 1914 and after 1936, so the dynasty keeps China instead of losing it to the Republic and then to the warlords.

The reclaim effect is `common/scripted_effects/endsieg_china_ownership.txt`; it takes every Asian state owned by a Chinese tag plus 609 and 743, sets owner, controller and core to ROOT.

## Verification state

Source and static evidence: the routing chain and both handover outcomes were walked as a state model over ten representative dates, all eight prior chapter-flag combinations, seven prior tree states and both handover variants, with three repeated same-day calls per case.
Every case ends with at most one tree load, at most one chapter flag, one chapter event per transition and no state change on a repeated call.
The same walk over a 1914-1937 continuous campaign loads three trees in total, against 7,392 under the previous two-pass tick.

Not verified: chapter transitions, `change_tag_from`, a DLC tree load and focus progress across a tree change or a save reload in a running game.
Those need a launch that this repair did not have.

One edge sits outside the daily chain: `rch_initialize_campaign` still opens chapter three for any start date after 1927, so a hand-made 1936-or-later save that starts as `RCH` loads `rch_nanjing` on day one and the DLC tree on the first tick.
No bookmark starts as `RCH`.
