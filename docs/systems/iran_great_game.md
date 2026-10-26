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
| `iran_foreign_leverage` | 0–100 | 60 | Aggregate dependence, read by the rest of the tree |

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
| British loan | 100 PP | +15 British influence, 5-year financial mission (build speed, cheaper consumer goods) | +10 leverage, −6 sovereignty, stability |
| Northern railway | 100 PP | +15 northern influence, a railway in Golestan, 5-year concession | +10 leverage, −6 sovereignty, stability |
| Foreign military mission | 75 PP | army experience, 4-year training mission | +10 influence to the stronger patron, −6 sovereignty |
| Foreign customs officers | 100 PP | revenue, cheaper consumer goods, stability | +15 leverage, −10 sovereignty |

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

`iran_great_game_tick` (monthly) has each power react to its own situation:

- A Britain at war demands transit (`iran_campaign.74`) — grant it, refuse it, or offer the corridor to Germany instead.
- A Soviet Union at war after 1941 demands the same corridor on better terms (`iran_campaign.75`).
- A Germany at war with the mission still in Tehran makes the Allied demand unavoidable (`iran_campaign.76`).

Agreements are once-only where they represent a single historical arrangement; the tick uses `seen` flags so no demand repeats, and each event is `is_triggered_only`.

## Germany

Germany has no frontier with Iran and no concession to defend, so its relationship is technical and commercial rather than territorial: a research institute and a barter agreement that asks for nothing in the customs house.
Expelling the mission in 1941 costs the machinery and the research slot, and buys a hearing in London and Moscow.

## Interactions

- Balance of Power (`PER_crown_and_majlis`): gates who may sign, and who pays for signing by decree.
- `iran_refresh_mechanics`: applies the influence-driven spirits; always call it through `iran_refresh_mechanics_hidden` from decisions, or the whole spirit list prints into the tooltip.
- Focus trees: the 1911 ultimatum, the Swedish gendarmerie and Majlis budget authority all move the new axes, so the chapters and the panel describe the same country.
- `iran_foreign_leverage` remains the aggregate the focus trees read, so no existing content had to be rewritten for the redesign.

## Tuning

All numbers live in `common/script_constants/iran_campaign.txt`: `sovereignty_*`, `influence_*`, `great_game_*`.
Thresholds that decide how easily a debuff comes off are `authority_reform` (65) and `leverage_dependency` (40).

## Known limits

- No custom GUI: the mechanic lives in decision categories. A second Balance of Power or a dedicated panel needs custom tabs, which vanilla does not draw.
- Germany has no crisis of its own beyond the 1941 expulsion demand.
- The 1933 oil negotiation is handled by the existing oil settlement decisions, not by a crisis mission.
- Nothing here has been playtested; the drift rate and decision costs are reasoned, not tuned.

## Needed icons

No new art is required: every decision uses an existing `GFX_decision_*` sprite and every spirit an existing `GFX_idea_*` picture.
A purpose-made category plate would still be better than `GFX_decision_category_generic_foreign_policy`.

## Future

- A dedicated panel showing all three powers, the sovereignty meter and active agreements, replacing the three decision categories with one screen.
- German crisis content for 1939–41 beyond the expulsion demand.
- A Soviet crisis once the northern railway concession is torn up.

## Foreign acts

Focuses, decisions and events that deal with a patron call one of four effects in `common/scripted_effects/iran_great_game_acts.txt`.
`iran_concede_small`, `iran_concede_large`, `iran_reclaim_small` and `iran_reclaim_large` take `patron = british | northern | german`.
The `*_leading_*` variants act on whichever patron currently holds the most influence, and are used by domestic reforms such as the national bank, tariff and budget focuses.
A concession raises the patron's influence, lowers sovereignty and raises foreign leverage; a reclaim does the inverse.
All 41 focus rewards that used to add to `iran_foreign_leverage` directly now call these effects, so every foreign-flavoured focus moves the Great Game axes.
Tuning lives in `iran_story.concede_*` and `iran_story.reclaim_*`; tooltips are the `iran_concede_*_tt` and `iran_reclaim_*_tt` keys in `iran_great_game_acts_l_english.yml`.
Foreign leverage is still a stored credit value, because the repayment decision and the credit events spend it directly; it is moved by these effects but not recomputed from the influences.
