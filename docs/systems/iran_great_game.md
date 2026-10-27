# The Great Game

Britain and the northern power meet across Iran because it is the only ground on which they can meet without a war.
The mechanic is not a friendship score.
It tracks three different things — how much each patron *controls*, how much goodwill it holds, and how much freedom of action the Iranian government still has — and it puts a price on every agreement in obligations that outlive the government that signed them.

## The three axes

| Variable | Range | Opens at | Meaning |
| --- | --- | --- | --- |
| `iran_british_influence` | 0–100 | 45 | British control: concessions, advisers, customs, transit |
| `iran_northern_influence` | 0–100 | 40 | Russian or Soviet control in the north |
| `iran_german_influence` | 0–100 | 0 | German technical and commercial presence, 1935 onward |
| `iran_british_standing` | 0–100 | 55 | British goodwill; buys nothing on its own |
| `iran_northern_standing` | 0–100 | 30 | Goodwill of Petersburg, then Moscow |
| `iran_sovereignty` | 0–100 | 35 (1910), 50 (interwar) | Freedom of action |
| `iran_foreign_leverage` | 0–100 | 60 | Aggregate dependence: the influence-held part plus repayable debt |
| `iran_leverage_landed` | 0–100 | 60 | The part of that dependence that patron influence holds |
| `iran_leverage_debt` | 0–100 | 0 | Credit taken from a patron, settled with equipment by decision |

Influence and standing are deliberately separate.
A patron can hold high goodwill and no control, or control and open contempt — the second is the normal case after a renegotiation.

`iran_northern_standing` was previously `iran_soviet_standing`, which was wrong for 1910: the northern power is the Russian Empire until a Soviet state exists.
Nothing is keyed to a fixed date — decisions that need the Soviet state test `country_exists = SOV`.

Initialised in `iran_initialize_campaign`; numbers live in `common/script_constants/iran_campaign.txt` under `sovereignty_*`, `influence_*` and `great_game_*`.

## How sovereignty moves

`iran_influence_tick` runs monthly on `on_monthly_PER`:

- −1 sovereignty per month for every patron whose influence is at or above `influence_pressure_threshold` (50).
- +1 per month while `iran_customs_reformed` is set and sovereignty is below 80.
- Clamped to 0–100.

Sovereignty is therefore not a currency to farm; it is the residual of how much of the country is under foreign administration, and it recovers only through institutions.

## Agreements

Decisions in category `iran_foreign_agreements`, each with an obligation spirit that outlasts the decision:

| Agreement | Cost | Buys | Costs |
| --- | --- | --- | --- |
| British loan | 100 PP | +15 British influence, 5-year financial mission (build speed, cheaper consumer goods) | +7.5 dependence through the influence, −6 sovereignty, stability |
| Northern railway | 100 PP | +15 northern influence, a railway in Golestan, 5-year concession | +7.5 dependence through the influence, −6 sovereignty, stability |
| Foreign military mission | 75 PP | army experience, 4-year training mission | +10 influence to the stronger patron, −6 sovereignty |
| Foreign customs officers | 100 PP | revenue, cheaper consumer goods, stability | +15 repayable debt, −10 sovereignty |

The way back is slower and needs a state worth bargaining with:

| Decision | Requires |
| --- | --- |
| Reform the customs service | 150 PP, authority ≥ 40 |
| Found the National Bank | 200 PP, customs reform |
| Professionalise the gendarmerie | 100 PP, authority ≥ 45 |
| Renegotiate the concessions | 200 PP, sovereignty ≥ 65 |
| End the foreign customs administration | 150 PP, sovereignty ≥ 75 |

## Incompatible obligations

Holding a British loan and a northern railway at the same time adds `iran_competing_concessions` (−10% stability, −10% political power) and fires `iran_campaign.73`, which asks which patron the government actually works for.
Honouring one removes the other agreement and its influence; keeping both is allowed, and expensive.

## The Majlis has to agree

Signing a major agreement requires either a government on the parliamentary side of the Crown and Majlis balance, or a Shah ruling by decree.
A decree signature is legal and costs stability and sovereignty, because the chamber was bypassed.

## Crises

Crises follow the TNO pattern: a mission decision with `days_mission_timeout`, resolved three ways — accept, refuse, or let the deadline decide.

**The Anglo-Persian Agreement, 1919–1921** runs 300 days.
Ratifying it grants influence and leverage in exchange for political power; rejecting it buys sovereignty, war support and authority at the cost of British goodwill; timing out signs it without the government, for a heavier price in stability and sovereignty.

## The powers act

`iran_great_game_tick` (monthly) asks the standing demands, and `iran_influence_tick` (monthly, on the same `on_monthly_PER` hook) carries the wartime corridor.
The two are separate helpers: the standing demands need a patron at 70 goodwill or more, while the corridor needs a patron at war.

- A Britain at war demands transit (`iran_campaign.74`): grant it and be paid while a foreign customs administration runs in the south, refuse it and be treated as a hostile neutral, or offer the corridor to Germany instead.
- The northern power at war takes the same road on better terms (`iran_campaign.75`), and its demand follows Britain's on a later month rather than arriving beside it.
- Germany at war with the mission still in Tehran makes the Allied demand unavoidable (`iran_campaign.76`): send the mission home, or keep it and be remembered for it.

The three corridor demands are one chain, not three independent checks, so at most one of them leaves a monthly tick and the order above is the order of precedence.
Each is fenced to the war years: `.74` and `.76` require `date > 1940.12.31` and `.75` requires `date > 1941.1.1`.
The fences are year-level gameplay eras rather than claims about the day of any ultimatum, and they exist because a Britain at war in 1914 otherwise consumed the transit demand a generation early.
All three also wait while `iran_negotiation_open` is set, so a month spent over another demand spends nothing here.
Each branch sets its own seen flag (`iran_transit_demand_seen`, `iran_soviet_transit_seen`, `iran_allied_demand`) only when it dispatches, and `iran_agreement_transit_allied` still closes both corridor offers once either is signed.
`iran_agreement_german_mission` remains the precondition for the Allied demand, so Germany's war only matters while its mission is still in Tehran.
The incompatible-obligations penalty (`iran_campaign.73`) and the sovereignty band that follow the chain are independent of it, so they still run in a month that also delivers a demand.
Every event here is `is_triggered_only`.

## Germany

Germany has no frontier with Iran and no concession to defend, so its relationship is technical and commercial rather than territorial: a research institute and a barter agreement that asks for nothing in the customs house.
Expelling the mission in 1941 costs the machinery and the research slot, and buys a hearing in London and Moscow.

## Interactions

- Balance of Power (`PER_crown_and_majlis`): gates who may sign, and who pays for signing by decree.
- `iran_refresh_mechanics`: applies the influence-driven spirits; always call it through `iran_refresh_mechanics_hidden` from decisions, or the whole spirit list prints into the tooltip.
- Focus trees: the 1911 ultimatum, the Swedish gendarmerie and Majlis budget authority all move the new axes, so the chapters and the panel describe the same country.
- `iran_foreign_leverage` remains the published aggregate the focus trees and AI read, so no reader had to change when dependence stopped being stored by hand.

## Tuning

All numbers live in `common/script_constants/iran_campaign.txt`: `sovereignty_*`, `influence_*`, `great_game_*`.
Thresholds that decide how easily a debuff comes off are `authority_reform` (65) and `leverage_dependency` (40).
The State Authority panel and the Foreign Dependence spirit quote the dependence threshold in words, so retuning `leverage_dependency` means editing both `iran_state_authority_desc` and `iran_foreign_dependence_desc` in `localisation/english/iran_campaign_l_english.yml` in the same change.

## Known limits

- No custom GUI: the mechanic lives in decision categories. A second Balance of Power or a dedicated panel needs custom tabs, which vanilla does not draw.
- Germany has no crisis of its own beyond the 1941 expulsion demand.
- The 1933 oil negotiation is handled by the existing oil settlement decisions, not by a crisis mission.
- Nothing here has been playtested; the drift rate and decision costs are reasoned, not tuned.
- The 1941 corridor demands are routed and gated here, but their aftermath is still the original option set: no patron agenda, no fresh negotiating position and no separate post-occupation settlement exists for them yet.
- `iran_campaign.75` describes a northern mission that has watched a British request arrive. The chain makes that the normal order, and a Britain that never went to war still lets the northern demand arrive alone.

## Needed icons

No new art is required: every decision uses an existing `GFX_decision_*` sprite and every spirit an existing `GFX_idea_*` picture.
A purpose-made category plate would still be better than `GFX_decision_category_generic_foreign_policy`.

## Future

- A dedicated panel showing all three powers, the sovereignty meter and active agreements, replacing the three decision categories with one screen.
- German crisis content for 1939–41 beyond the expulsion demand.
- A Soviet crisis once the northern railway concession is torn up.
- The I2 patron-agenda slices (fresh negotiating positions for each patron, the pay-as-concession standing demands) remain separate, unfinished work. Nothing in the wartime routing above implements them.

## Foreign acts

Focuses, decisions and events that deal with a patron call one of four effects in `common/scripted_effects/iran_great_game_acts.txt`.
`iran_concede_<patron>_<small|large>` and `iran_reclaim_<patron>_<small|large>`, with patron `british`, `northern` or `german`, are separate explicit effects because parameter substitution inside variable names is unproven.
The `*_leading_*` variants act on whichever patron currently holds the most influence, and are used by domestic reforms such as the national bank, tariff and budget focuses.
A concession raises the patron's influence and lowers sovereignty; a reclaim does the inverse.
Both republish dependence from the influence they actually moved, so a single act is never booked twice.
All 41 focus rewards that used to add to `iran_foreign_leverage` directly now call these effects, as do the two legation decisions and the oil royalty advance.
Tuning lives in `iran_story.concede_*` and `iran_story.reclaim_*`; tooltips are the `iran_concede_*_tt` and `iran_reclaim_*_tt` keys in `iran_great_game_acts_l_english.yml`.

## Dependence, and what is a loan

Dependence is published, not accumulated. `iran_recompute_leverage` in `common/scripted_effects/iran_campaign.txt` is its only writer:

- `iran_leverage_landed` = clamp(`iran_leverage_baseline` + (the three patron influences − `iran_influence_baseline`) × `leverage_derivation_weight`, 0, 100)
- `iran_foreign_leverage` = clamp(`iran_leverage_landed` + `iran_leverage_debt`, 0, 100)

The influences are clamped to 0–100 inside the publisher, so a concession taken at the cap cannot manufacture dependence the patron never gained.
The weight is 0.5, so fifteen points of influence move dependence by 7.5, and the engine's fixed-point arithmetic keeps the half.
`iran_leverage_baseline` and `iran_influence_baseline` are captured once, by `iran_leverage_baseline_init`, after the chapter's opening values and influences exist and before any band is published.
A later chapter transition does not re-base them, and a country that is already running keeps the dependence it has.

Credit is the only stored part. Events and decisions that lend Iran equipment, transit or revenue write `iran_leverage_debt`; nothing else may write it, and the settlement decision `iran_repay_foreign_credit` requires positive repayable debt rather than positive dependence, so equipment can never be spent on patronage that only concessions can buy back.
Every body that writes the debt republishes the band in the same block, because `iran_foreign_dependence` is added and removed only inside `iran_refresh_mechanics`: decisions call `iran_refresh_mechanics_hidden`, and focus rewards wrap `iran_refresh_mechanics` in a `hidden_effect`.
The customs reform and the national bank pay five points down, and the American mission takes ten, so each of them can cross `leverage_dependency`; a debt write that stopped at the publisher would move the numbers and leave the spirit on the old band.

Republication points are `iran_refresh_mechanics` (before the dependence spirit is tested), `iran_influence_tick` (monthly, after the drift), every concession or reclaim effect, and every body that writes the repayable debt.
The publisher never calls `iran_refresh_mechanics`, so no caller can recurse.

## Concessions follow the route

A reward that concedes must be reachable only from a route that conceded something.
`IR2_khuzestan_oil` is opened by either `IR2_domestic_capital` or `IR2_foreign_concessions`, those two are mutually exclusive, and they are its only entrances, so the missing `iran_domestic_capital` flag is exactly "took the foreign concessions".
Its capacity project therefore calls `iran_concede_british_small` only inside `if = { limit = { NOT = { has_country_flag = iran_domestic_capital } } }`, so a domestic-capital Iran neither pays British influence nor loses the sovereignty it just reclaimed, and `iran_recompute_leverage` is not republished from a deal that player refused.
The call sits outside `hidden_effect`, so the concession tooltip appears only on the branch that actually pays it, and the mutual exclusion is what makes that test correct rather than a guess.
Do not widen this to `iran_path_oil_concession`: that trigger reads the concession flags set elsewhere in the campaign, and `IR2_foreign_concessions` sets none of them.
`.tools/tests/test_iran_route_blind_rewards.py` executes the shipped reward against both routes and pins the gate, its exact limit, the tooltip placement and the single application, with four mutants that must each fail by name.
