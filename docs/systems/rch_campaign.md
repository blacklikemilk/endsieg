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

## The 1915 settlement and the 1916 succession

The Republic's first four years are a contest between a civil government and the commanders who guarantee it, and that contest is decided before Yuan Shikai dies.

### The Beiyang Order category

`rch_beiyang_order_category` holds eight repeatable cards in four families: constitution, army, provinces and money.

Each family has one civil card and one military card, and one shared lock flag (`rch_press_lock_constitution`, `..._army`, `..._provinces`, `..._money`).
Either side of a family takes the lock, and both sides carry the same `available` clause, so a family acts once per 180 days rather than twice.
Every press clears its gate and its family lock before re-setting them, so the reform tenure and the lock date restart at that press instead of inheriting the date of the term before it.
The lock is shown, not hidden: a card whose family has acted stays visible with `rch_press_family_available` explaining why it cannot be pressed.
The shared text is worded as the requirement the card draws ("The government has not pressed this matter in the past six months."), so the line reads true when the family is free and unmet when it is locked, and the tooltip never states the tuning rule itself.

A civil card sets its reform gate (`rch_gate_constitution`, `rch_gate_officer_rotation`, `rch_gate_civil_governors`, `rch_gate_treasury`).
The military card in the same family clears that gate and takes a governor instead.
Re-setting a cleared gate clears the flag first, so its date restarts and a stale date cannot re-qualify a reform.

`rch_governor_count` is a new clamped counter (0 to 3). It is deliberately not the existing `rch_military_governors` flag, which a focus sets in every chapter tree.

Every card is available with or without *Arms Against Tyranny*; only the display is DLC-bound.

### The settlement, 12 December 1915

`rch_settlement_snapshot` runs once from `rch_campaign_tick` on 12 December 1915 and stores `rch_reform_settled` (0 to 4).
A gate counts only when its flag stood more than 180 days at that date: a gate set on 14 June 1915 counts, a gate set on 15 June does not.
Nothing bought after 12 December 1915 can enlarge the count, and the snapshot is taken before the throne is answered.

`rch_campaign.42` (the Hongxian choice) is queued once between 12 and 31 December 1915.
Refusing sets `rch_gate_throne_refused`; accepting sets `rch_hongxian` and the refusal gate can never be set.
A start at or after 1 January 1916 has already lived through the proclamation: `rch_succession_endow` gives it `rch_hongxian`, `rch_throne_choice_seen` and a sealed zero snapshot.

### The succession, 6 June 1916

`rch_campaign_tick` owns the resolution. On the first day after 5 June 1916 it calls `rch_succession_resolve`, which settles, freezes and only then queues `rch_campaign.5` with the existing one-day delay.

`rch_succession_refresh` computes the score as a pure function of the three dials, the frozen reform count, the throne answer, the governor counter and a war against another Chinese government:

`base = round((legitimacy + 100 - military_influence + round(nationalist_support / 2)) / 3)`
`score = clamp(base + 8 * (settled reforms + refused throne) - 6 * governors - 15 * chinese war, 0, 100)`

`rch_succession_evaluate` applies one exclusive precedence:

| Order | Tier | Condition |
| --- | --- | --- |
| 1 | 3 Dissolved | military influence 80 or more, or legitimacy below 20 |
| 2 | 0 Unified | not collapsed, score 70 or more, four settled reforms, throne refused, fewer than three governors, control of state 608, no Chinese war |
| 3 | 1 Contested | not collapsed, score 45 or more |
| 4 | 2 Garrison | everything else |

The tier is frozen into `rch_succession_final_tier` and `rch_succession_final_score`, one line flag is set (`rch_line_unified`, `rch_line_contested`, `rch_line_garrison`, `rch_line_dissolved`) and one seat spirit is applied.
`rch_campaign.5` presents exactly one option, chosen by an exclusive trigger on the frozen tier, and its `immediate` computes nothing.
A deferred, closed or lost popup therefore cannot change the outcome, and a post-crisis start resolves silently at initialisation.

`rch_refresh_mechanics` removes and reapplies the seat spirit from the frozen line flag, so a routine refresh of the other spirit families cannot erase the result.

| Spirit | Tier | Payload |
| --- | --- | --- |
| `rch_succession_constitutional` | 0 | political power +10%, stability +10%, building speed +5% |
| `rch_succession_contested` | 1 | political power -5%, stability -5% |
| `rch_succession_garrison` | 2 | army organisation +5%, political power -10%, stability -5% |
| `rch_succession_dissolved` | 3 | political power -15%, stability -10%, army organisation -5% |

This slice creates no tag, transfers no state and changes no leader. The tier is the interface the later territorial and leader slices consume.

### The Beiyang display

`common/bop/RCH.txt` defines `RCH_beiyang_order` with two sides and five ranges, and no modifier anywhere: the spirit carries the gameplay.
`rch_beiyang_refresh` reads `rch_military_influence` itself, so every existing focus, decision and event writer of the dial is mirrored, and it publishes one of five literal offsets through `add_power_balance_value`:

| Military influence | Published offset |
| --- | --- |
| above 75 | +0.85 |
| above 60 | +0.25 |
| above 50 | 0.00 |
| above 35 | -0.25 |
| otherwise | -0.85 |

The published band is remembered in `rch_bop_band`. A band change removes the old offset and applies the new one exactly once, so the panel is never re-initialised from a daily call.
`rch_beiyang_bootstrap` creates the panel once, guarded by the DLC and by the absence of the balance, and it is also reachable from `rch_beiyang_refresh` so a save loaded mid-campaign gets the panel.
Without *Arms Against Tyranny* no balance command runs and every card and outcome is unchanged.

The panel never shows a raw identifier: `RCH_beiyang_order`, `RCH_side_civil`, `RCH_side_military`, `RCH_bop_settlement`, `RCH_bop_civil_ascendant`, `RCH_bop_civil_supremacy`, `RCH_bop_military_government` and `RCH_bop_military_supremacy` are all localised once in `localisation/english/rch_campaign_l_english.yml`, beside the category they belong to.

### What the player is told

The settlement, the conditions the seat is judged on and the standing it earned are stated in six player-facing values, so a player can plan the four reforms instead of discovering them after the fact and can read the result afterwards.

| Surface | Key | What it states |
| --- | --- | --- |
| The Beiyang category | `rch_beiyang_order_category_desc` | The 12 December 1915 record, the more-than-180-days tenure, the four counted measures, and every condition the seat is judged on |
| The 1912 announcement | `rch_campaign.2.d` | That December closes the reform record, the tenure a reform needs before it counts, and that the seat is judged when the presidency falls |
| The succession popup | `rch_campaign.5.d` | The four counted measures, the tenure, the crown, the dials, the governors, Beijing and war with another Chinese government, the judgement at resolution, and the frozen standing it prints |
| The four seat spirits | `rch_succession_constitutional_desc`, `rch_succession_contested_desc`, `rch_succession_garrison_desc`, `rch_succession_dissolved_desc` | The same frozen standing, printed by the spirit that is still standing after the crisis |

The four measures named in the text are the four civil cards: the constitution, the rotation of the officer corps, the civil governors and the funding of the ministries.
`display_contract()` in `.tools/tests/test_rch_succession.py` binds the prose to the script: it executes each of those four cards and requires the gate the text names to be the gate the card sets, and it requires the popup path to take no further settlement snapshot.
The same section forbids a territorial claim in any of the three values, because a succession tier is not fragmentation.
`score_readout()` resolves every fixture through the shipped `rch_succession_settle`, compares the number the popup and the standing seat spirit would draw with the score that effect froze, requires the pre-resolution category to print no number, and proves an absent variable is not read as zero.

The lock is stated in the same style on the cards themselves, through `rch_press_family_available`.

### What the standing number is, and when it exists

`rch_succession_settle` assigns `rch_succession_final_score` and `rch_succession_final_tier` once, when the succession resolves, and only then queues the popup and leaves the seat spirit standing.
Both consumers print the frozen variable directly, as `Seat standing: [?rch_succession_final_score|0] out of 100.`, in an ordinary localisation value.
No `common/scripted_localisation` entry is involved and none is needed: this is a formatted country variable, the same form vanilla uses for a country variable inside a spirit description.
The lifetime follows from that assignment order. During 1912, at the 12 December 1915 record and through January 1916 the variable does not exist, which is why the category and the eight cards describe composition and print no number; the popup and the four seat spirits exist only after the assignment, and the popup is queued after it.
A post-crisis bookmark resolves at initialisation with no popup, so there the seat spirit is the surface that shows the number.
The number is the standing the seat was judged on, not a projection: later dial changes, a refresh or a repeated tick leave it as it was, because nothing recomputes it after resolution.

### Reference and validation state

`.tools/tests/test_rch_succession.py` parses the shipped constants, triggers, effects, decisions, ideas and balance file and executes them against a synthetic Republic.
It covers the eight cards, the three chapter openers, the opposing stability costs of the two civil bargains, the five emergency rows, the full-civil and three-civil plans, the military collapse, the 44/45 and 69/70 boundaries, tier exclusivity, the 181/180 settlement boundary, the sealed 1916 and silent 1918 starts, same-day repeats, seat-spirit survival across a refresh with an earlier seat already standing, the display band transitions, no-DLC parity, the frozen standing readout on the popup and on all four seat spirits, and the mutants listed below.
Every claim is a named statement in a record, and the shipped source must hold all of them.
Each effect handler the suite books a claim on is probed directly for the bookkeeping it performs, and each of those handlers also carries a source mutant that must raise a named defect through the same record: the frozen score and tier, every term of the succession arithmetic, the score clamp, the line flag, the seat addition and the seat removal, the panel creation, one published band offset, the queued popup, the chapter tree, the chapter clears, and the stability gain and cost.
A handler that silently stops booking its command therefore fails twice, once as a probe and once as a mutant that no longer bites.
The anti-exploit guards are executed rather than read.
Each card's `available` block is run with its family lock absent, fresh, exactly at the window and one day past it, and the family is then pressed twice a term apart to prove the lock date follows the later press instead of the first.
Every press effect is run with all four gates and all four locks aged 400 days, and the executed trace must clear its own gate and its own lock before setting them, leave the gate dated at the press, leave a military bargain with no gate standing, and touch no other family's gate.
Each literal the engine fields demand (`days_re_enable`, the lock window, the settlement maturity window, `controls_state`) is compared with the constant it documents.
`rch_campaign_tick` itself is executed on a 1916 day and on a quiet 1917 day, which proves the tick settles, records, queues one popup, republishes the display, stays silent on a repeat call and still publishes on a day with no other display work.
On the text side it reads the eight identifiers the balance panel draws and fails on any that has no English key, and it checks that all eight cards still attach the shared family lock tooltip, that each tooltip ages its own family flag, and that the tooltip text is the availability requirement rather than the locked state or the tuning rule.
Every guard carries a mutant that must break it: releasing every family lock at day 0, deleting a gate clear, deleting the family lock clears, drifting the cooldown constant to 200, drifting the capital constant to 611, and dropping the daily display refresh from the tick.
The display contract has its own section and its own mutants: the settlement paragraph cut from the category description, the judgement sentence cut from the popup, the tenure clause replaced with a vague one in the settlement announcement, and a territorial claim inserted into the category text are each caught by a named check, while a clean mirror still passes.
`display_contract_mutants()` runs those four inside the suite, and the same four were also applied to a full mirror tree through `RCH_TEST_ROOT`, where each run exited non-zero on the named check for the text it lost.
The pre-source control runs this same suite against the `HEAD` version of every input through `RCH_TEST_ROOT` and requires a named failure there, so the suite cannot pass on the tree that had no slice in it.
Three localisation mutants keep those checks honest: dropping the side and range keys, restoring the blocked-state wording and moving one card off the shared tooltip are all caught.

The model is a single-country interpreter, not the engine: it does not debit a decision's `cost`, does not schedule events, missions or MTTH, and renders no panel, popup, focus tree or tooltip, so those surfaces remain unverified without a launch.
Not verified: no launch was performed, so the panel has never been seen, the popup has never been presented and no campaign has been played through 1916.

## Verification state

Source and static evidence: the routing chain and both handover outcomes were walked as a state model over ten representative dates, all eight prior chapter-flag combinations, seven prior tree states and both handover variants, with three repeated same-day calls per case.
Every case ends with at most one tree load, at most one chapter flag, one chapter event per transition and no state change on a repeated call.
The same walk over a 1914-1937 continuous campaign loads three trees in total, against 7,392 under the previous two-pass tick.

Not verified: chapter transitions, `change_tag_from`, a DLC tree load and focus progress across a tree change or a save reload in a running game.
Those need a launch that this repair did not have.

One edge sits outside the daily chain: `rch_initialize_campaign` still opens chapter three for any start date after 1927, so a hand-made 1936-or-later save that starts as `RCH` loads `rch_nanjing` on day one and the DLC tree on the first tick.
No bookmark starts as `RCH`.
