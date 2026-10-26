# The Oil Settlement

Iran's concession is the country's one great asset and the thing every foreign power in it actually wants.
It is handled as a bargaining position rather than a resource counter: it can be squeezed, compromised,
broken or invested, and each has a price somewhere else.

## Where it lives

| Piece | File |
| --- | --- |
| Category | `common/decisions/categories/iran_oil_settlement.txt` |
| Decisions | `common/decisions/iran_oil_settlement.txt` |
| Text | `localisation/english/iran_oil_l_english.yml` |
| Numbers | `common/script_constants/iran_campaign.txt` (`oil_*`) |
| Standing spirits | `common/ideas/iran_campaign.txt` |

The oil state is **413** (Khuzestan); every decision requires owning it, and the two building projects
also require controlling it, so an occupied Iran cannot develop its own field.

## The five decisions

| Decision | When | Cost | Gains | Price |
| --- | --- | --- | --- | --- |
| Press the Company for Better Royalties | 1930–1945, repeatable every 365 days | 100 PP | fuel, political power, one year of `iran_oil_revenue_dividend` (−5% consumer goods, +10% PP) | +10 foreign leverage, −5% stability |
| Settle the Concession Question | 1933–1945, once | 125 PP | political power, fuel, +10 authority | +10 leverage, and the company stays |
| Cancel the Concession | 1933–1945, once, authority ≥ 50 | 150 PP | +15 authority, −25 leverage, war support, +10% stability | −30 opinion with Britain, the dispute never fully closes |
| Build a Refinery of Our Own | 1925–1945, once | 75 PP, 120 days, one civilian factory | industrial complex in Khuzestan, fuel | factory time |
| Spend the Oil Revenue on the Ground | 1925–1945, every 180 days | 75 PP | infrastructure in Khuzestan, stability | political power that could go elsewhere |

## How it interacts

- Cancelling drops foreign leverage by 25, which **closes the 1941 transit option** (`iran_campaign.40.c`
  needs 50 leverage). Nationalising the oil and then asking London for a quiet arrangement do not go
  together, and the player feels that without a line of script saying so.
- The royalty dividend is a timed spirit, so squeezing the company pays for a year and then stops.
- `iran_path_oil_national` from the 1910–18 chapter weights the AI towards cancellation, so the earlier
  era's choices still bend the later one.

## Tuning

`oil_royalty_fuel` (400), `oil_royalty_capital` (40), `oil_nationalise_authority` (15),
`oil_nationalise_leverage` (−25), `oil_compromise_leverage` (10), `oil_refinery_capacity` (600).
All in `common/script_constants/iran_campaign.txt`.

## Needed icons

Every icon here is vanilla: `GFX_decision_category_generic_prospect_for_resources`, and the
`generic_fundraising` / `generic_political_discourse` / `generic_nationalism` / `generic_factory` /
`generic_construction` decision icons. A purpose-made Abadan category plate would be better.

## Future

- Royalty revenue should feed the treasury variable rather than paying political power directly.
- The 1951 nationalisation is out of scope (the mod ends in 1945) but the same flags would carry it.
