# Negotiated bills in the Cortes

The six government bills in the `SPR_cortes` decision category are no longer political-power spends that pass whenever the government holds 201 seats. Each bill now counts the benches that would carry it, and a bill only reaches the floor when that count can still be made to work. Bringing it opens a negotiation: the government passes it cleanly, buys the missing votes with a concession where there are benches to buy, waters it down, or withdraws and takes the political damage.

## Files

| File | Role |
| --- | --- |
| `common/decisions/spain_cortes.txt` | The six bill decisions: era visibility, the vote-count gate, cost, AI willingness, and the event they fire. |
| `common/scripted_effects/spain_cortes_bills.txt` | Seat arithmetic, per-bill counts, concessions, outcomes and cooldowns. |
| `events/spain_cortes_bills.txt` | Namespace `spain_bills`: the six negotiation events (`spain_bills.1`–`.6`) and the hidden clerk event `spain_bills.90`. |
| `common/script_constants/spain_campaign.txt` | `bill_negotiation_reach`, `bill_defeat_shift`, `bill_concession_shift`, `bill_concession_gain`, `bill_autonomy_half`, `bill_coup_relief_half`. |
| `localisation/english/spain_cortes_bills_l_english.yml` | Decision names and descriptions, gate tooltips, event text and option tooltips. |

## Vote arithmetic

`spain_cortes_recount` still normalises the seven parties into exactly 400 seats, so a majority is always `constant:spain_campaign.cortes_majority` (201) and the chamber total is always `constant:spain_campaign.cortes_total` (400).

`spain_bill_count_votes` clears the running total, sets the bar, then dispatches on `spain_bill_current` to one per-bill count:

- `spain_bill_prepare_count` sets `spain_bill_votes` to 0, `spain_bill_needed` to the majority, and `spain_bill_floor` to the majority minus `constant:spain_campaign.bill_negotiation_reach`. The floor is the number of seats a government may be short of the bar and still bring the bill.
- `spain_bill_add_government` adds `spain_government_seats`, which already contains the ruling party and both coalition partners.
- Each `spain_bill_add_<party>` helper adds that party's seats **only when the party sits outside the government bloc**, which is what prevents double counting.
- The swing party of a bill is never one of the helpers in that bill's base count. Its benches enter `spain_bill_swing_votes` in a separate block after the base is clamped, and that block is skipped while the party sits in the government bloc, where `spain_government_seats` already carries it. Each party therefore contributes its benches exactly once to each total.
- The finished total is clamped to the chamber size and copied to `spain_bill_votes_<bill>`, the cache the decision buttons read.

| Bill | Supporting bloc (base) | Swing party whose votes can be bought |
| --- | --- | --- |
| `SPR_bill_budget` | government + Conservatives | Liberals |
| `SPR_bill_agrarian_reform` | government + Republicans + Socialists + Liberals | Conservatives (the landowners) |
| `SPR_bill_labour_charter` | government + Socialists + Republicans + Liberals | Conservatives |
| `SPR_bill_army_budget` | government + Monarchists + Conservatives + Falange | Liberals |
| `SPR_bill_regional_statute` | government + Republicans + Socialists + Liberals | Conservatives |
| `SPR_bill_electoral_law` | government + Republicans + Socialists | none |

The electoral law is counted like the other five, on the benches that would gain from it: the government's own seats plus the Republicans and the Socialists. The Monarchists, the Conservatives, the Carlists and the Falange vote against a franchise that would dilute their own seats, and the Liberals never enter the base — as the governing party they are already inside `spain_government_seats`, and in opposition they do not write the terms of the election they would fight. In the opening restoration chamber that is a Liberal government's 97 seats with 48 Republicans and 26 Socialists (171), or a Conservative government's 81 with the same two benches (155), so a bloc short of the 201 seats the law needs is never assumed to pass: it can only reform the register alone or withdraw the bill, and a chamber that already holds those benches carries it cleanly. The bill has no swing party and `spain_bills.6` has no concession option, because no bench outside the supporting bloc will sell a franchise that would unseat it. What the bill finally costs is the election it fires immediately, which is why it may only be brought once and still uses a 365-day re-enable.

`spain_bill_swing_votes` starts as the base count and gains the swing party's benches once, and only while that party sits outside the government bloc. It is the true ceiling of the bill — the most the chamber could be made to vote — and never the base plus a second copy of benches the base already counted. The event uses it to decide whether a concession could close the gap.

### Worked examples

The government holds 100 Republican seats and neither the Liberals nor the Conservatives sit in it.

| Case | Other benches | Base `spain_bill_votes` | Swing `spain_bill_swing_votes` | Options offered |
| --- | --- | --- | --- | --- |
| Budget, Liberals 60 | Conservatives 30, Socialists 120, Monarchists 40, Carlists 30, Falange 20 | 100 + 30 = **130** | 130 + 60 = **190** | below 201 even with the Liberals: only "water it down" or "withdraw" |
| Budget, Liberals 80 | Conservatives 30, Socialists 110, Monarchists 40, Carlists 20, Falange 20 | 100 + 30 = **130** | 130 + 80 = **210** | the Liberal concession reaches the bar, so `spain_bills.1.b` appears |
| Army budget, Liberals 60 | Monarchists 20, Conservatives 15, Falange 5, Socialists 140, Carlists 60 | 100 + 20 + 15 + 5 = **140** | 140 + 60 = **200** | below 201: no concession, the bill is withdrawn or watered down |
| Army budget, Liberals 60 | Monarchists 40, Conservatives 30, Falange 20, Socialists 90, Carlists 60 | 100 + 40 + 30 + 20 = **190** | 190 + 60 = **250** | the Liberal concession reaches the bar, so `spain_bills.4.b` appears |

When the Liberals are inside the government bloc, `spain_government_seats` already holds their benches: the base count carries them, the swing block is skipped, and the two totals are equal, so only a clean pass is possible. The party is in the room rather than to be bought.

The options column describes what the negotiation offers once the bill is on the floor. Bringing it is a separate gate: the decision's `available` compares the cached base `spain_bill_votes_<bill>` — or the government's own seats — against `spain_bill_floor` (161), so a bill is only brought while its base bloc is within `bill_negotiation_reach` seats of the majority. A government whose base is below the floor never reaches the negotiation whatever the swing party would add; the concession is therefore reachable while the base sits between 161 and 200 seats and the swing benches lift the true total to 201.

## Flow

1. The decision checks its era (`spain_chapter_restoration`, `spain_chapter_rivera` or `spain_chapter_republic`), that the campaign is initialized, that the Cortes is not dissolved, that the bill has not already passed, and that the bill is not on cooldown. `visible` hides a bill that is already law; `available` explains the rest through `custom_trigger_tooltip`.
2. `available` also requires `spain_bill_votes_<bill>` (or, as a floor, `spain_government_seats`) to be at least `spain_bill_floor`. A bill whose bloc cannot reach the floor is listed as unavailable rather than removed, so the player can see why the chamber will not carry it.
3. Taking the bill pays its political power cost and fires `spain_bills.<n>`.
4. The event recounts the chamber live in `immediate`, so the numbers in the text and the option triggers are always current, then offers:
   - **pass cleanly** — only when `spain_bill_votes` already reaches `spain_bill_needed`;
   - **concession** — only when the bill is short of the bar but `spain_bill_swing_votes` reaches it;
   - **water it down** — always;
   - **withdraw** — always.
5. The chosen outcome effect applies the bill, moves the party shifts, sets the `spain_bill_*_passed` flag and recounts the Cortes. A withdrawal or defeat applies `spain_bill_penalise_government` and sets a 60-day cooldown flag on the bill.

## Concessions and their prices

| Bill | Concession | Persistent cost |
| --- | --- | --- |
| Budget | The Catalan question is reopened for the Liberal benches | `spain_catalan_autonomy` up, `spain_party_shift_conservatives` down |
| Agrarian reform | The estates are compensated | `spain_party_shift_conservatives` and `spain_party_shift_carlists` up, two stability costs |
| Labour charter | The right to organise is struck out | `spain_party_shift_socialists` down, `spain_party_shift_conservatives` up, no conciliation flag |
| Army budget | A commission of enquiry on the Africanistas | `spain_coup_pressure` up instead of down, `spain_party_shift_republicans` down |
| Regional statute | The Captain-General is reassured | `spain_military_loyalty` down permanently |
| Electoral law | none — no bench's votes can be bought for a franchise | — |

No concession grants political power. Every concession either moves a party's support, moves a campaign variable, or both, so buying a bill is always paid for somewhere else and cannot be farmed.

## Outcomes

- **Clean pass** applies the bill at full strength, adds `constant:spain_campaign.bill_concession_gain` to the governing party through `spain_bill_credit_government`, and sets the passing flag. The labour charter clears `spain_labour_repression` and sets `spain_labour_conciliation`, so the seat model feels it.
- **Concession pass** applies the same full effect plus the price above, and credits the bought party instead of the government.
- **Watered down** applies the reduced tier: `development_gain` instead of `development_gain_large` for agriculture, `bill_autonomy_half` instead of `autonomy_gain` for the statute, `bill_coup_relief_half` instead of `coup_relief` and `spain_loyalty_gain_small` instead of `spain_loyalty_gain` for the army budget, and `stability_cost` instead of a stability gain everywhere. Development is integral, so a watered budget still builds; it simply pays no political dividend.
- **Defeat or withdrawal** costs `constant:spain_campaign.stability_cost`, runs `spain_government_strain`, takes `constant:spain_campaign.bill_defeat_shift` from the governing party and starts the bill's 60-day cooldown.

## Cached counts and the clerk event

A trigger cannot add variables, so the decision gate reads a cache. `spain_bills_start_ticker` starts the hidden `spain_bills.90` chain the first time a bill is negotiated, and that event re-runs `spain_bills_count_all` every 30 days and re-schedules itself. It stops when `spain_cortes_dissolved` is set or the campaign is no longer initialized, clearing `spain_bills_ticker` so a later session can start it again.

`spain_bill_floor`, `spain_bill_needed`, `spain_bill_votes` and `spain_bill_swing_votes` are working variables; `spain_bill_votes_<bill>` are the cached totals. The negotiation event always recounts live, so a stale cache can only mislead the button, never the vote itself.

Until the first count has run, a bill's cached total does not exist yet and the decision gate falls back to listing the bill for its era, because `check_variable` on a missing variable compares against zero. That is deliberate: the first bill a government brings starts the chain and establishes every count, and the negotiation it opens uses live numbers regardless.

## AI

Each decision keeps an `ai_will_do` base and adds modifiers: strongly higher when the bill's own bloc already holds a majority, higher when the government is short of one or when stability is low, and lower when coup pressure is already at the attempt floor. The army budget inverts that last modifier, and the statute is more attractive while Catalan autonomy is still below `autonomy_statute`.

Every option has an `ai_chance`. The clean pass is the preferred option, the concession follows, watering down comes third, and withdrawal is only weighted up when the bill is below its floor and there is nothing left to trade. The AI never takes a bill it cannot carry and never withdraws from a bill it could still pass.

## Interactions

- `spain_cortes_recount` stays the single source of seats, so every election, proscription, financing or court-the-chamber action changes which bills are offered.
- `spain_government_seats` and `spain_government_majority` remain the government's own standing; a bill can now pass with a government below 201 seats when its bloc plus a concession reaches the bar.
- `spain_loyalty_gain`, `spain_loyalty_gain_small`, `spain_push_crown_small`, `spain_push_cortes_large`, `spain_refresh_campaign_ideas`, `spain_hold_election` and `spain_government_strain` are reused unchanged, so the bill outcomes stay inside the existing campaign model.
- `spain_cortes_dissolved` still closes the category; the bills additionally refuse to open while it is set.

## Icons

No new art is needed. The bills reuse `GFX_decision_category_generic_economy`, `GFX_decision_category_eng_concessions_to_the_trade_unions`, `GFX_decision_category_army_reform` and `GFX_decision_category_generic_democracy` as decision icons, and the events reuse the existing report pictures `GFX_report_event_kuncrowd`, `GFX_report_event_workers_strike`, `GFX_report_event_general_strike` and `GFX_report_event_army_border`.

## Future plans

- Bind `spain_bill_reach_<bill>_tt` to a scripted localisation line that prints the cached count, so the tooltip shows the exact shortfall instead of describing it.
- Let a bill that was watered down be revisited once at full text after the next election, using the existing cooldown flag instead of the passed flag.
- Split the electoral law into franchise and register halves so the Senate veto becomes a real second vote rather than a watered outcome.
- Give the Falange and the Carlists their own bills in the civil-war and postwar chapters, reusing the same count and negotiation effects.
- Drive the clerk's 30-day cycle from the campaign's own monthly tick once that hook accepts external calls, which would remove the hidden event chain.

## Tuning

`bill_negotiation_reach` sets how far short of a majority a government may be and still bring a bill (40 seats, so the floor is 161). `bill_defeat_shift`, `bill_concession_shift` and `bill_concession_gain` set the support movements of failure and of a bought vote. `bill_autonomy_half` and `bill_coup_relief_half` are the reduced tiers for a watered statute and a watered army budget. The bill cooldown is 60 days and lives as `@bill_cooldown_days` in `spain_cortes_bills.txt` because `days =` does not accept a script constant.
