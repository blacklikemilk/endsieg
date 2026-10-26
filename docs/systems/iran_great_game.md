# The Great Game

Britain and Russia meet across Iran because it is the only ground where they can meet without a war.
The mechanic tracks standing with each separately, because the country's whole diplomatic art is
keeping them interested in different things.

## State

| Variable | Range | Opens at |
| --- | --- | --- |
| `iran_british_standing` | 0–100 | 55 (London holds the Gulf and the telegraph in 1910) |
| `iran_soviet_standing` | 0–100 | 30 (the northern sphere, weaker after 1917) |

Initialised in `iran_initialize_campaign`, clamped in `iran_refresh_mechanics` alongside authority and
leverage. Numbers live in `common/script_constants/iran_campaign.txt` under `great_game_*` and
`british_opening` / `soviet_opening`.

## The panel

Category `iran_great_game`, icon `GFX_decision_category_generic_foreign_policy`, six decisions —
the count vanilla categories use (its own examples run 4–6), so the panel does not scroll.

| Decision | Cost | Effect |
| --- | --- | --- |
| Court the British Legation | 75 PP, 180 days | +15 British, −10 Soviet, +10 leverage |
| Cultivate the Soviet Mission | 75 PP, 180 days | +15 Soviet, −10 British, −5% stability |
| Play One Against the Other | 100 PP, 240 days, both ≥ 45 | +10 authority, +50 PP, −10 both |
| Expel the Foreign Advisers | 150 PP, once, authority ≥ 50 | −20 both, +15 authority, −10 leverage, war support, −5% stability, −30 opinion with Britain |
| Grant the Northern Concession | 50 PP, once | +15 Soviet, −10 leverage, +50 PP |
| Invite a Third Power In | 100 PP, once, from 1933, British standing < 45 | +10 authority, −10 British, war support, fires `iran_campaign.70` at Germany |

## The three standings

Exactly one spirit is in force, applied inside a `hidden_effect` so the switch never appears in a
focus tooltip:

| Condition | Spirit | Modifier |
| --- | --- | --- |
| both ≥ 45 and both < 60 | `iran_balancing_powers` | +10% political power, +5% stability |
| British ≥ 60 | `iran_british_preference` | −4% consumer goods, +5% political power |
| Soviet ≥ 60 | `iran_soviet_preference` | +5% factory output, −5% stability |

Balance pays more than either patron's favour and is the hardest state to hold, because every courting
decision moves one patron up and the other down.

## Interactions

- Standing is not the same axis as `iran_foreign_leverage`: leverage is how much *any* foreign power
  holds over the treasury, standing is who holds it. Expelling advisers cuts both.
- The third-power path is closed to Iran whose British standing is already high — you cannot invite
  Berlin in while London is being courted.
- `iran_campaign.70` is gated `tag = GER`; the earlier reuse of `iran_campaign.64` would have done
  nothing, because that event is gated to Britain.

## Tuning

Court gain 15, rival loss −10, expulsion −20, parity threshold 45, preference threshold 60. At +15 per
action a patron reaches a decisive position in three actions, which is roughly two years of play.

## Needed icons

Vanilla only: `GFX_decision_category_generic_foreign_policy`, and the `generic_fundraising`,
`generic_intelligence_operation`, `generic_political_discourse`, `generic_arrest` and `generic_trucks`
decision icons. A purpose-made category plate would be better.

## Future

- Standing should gate the 1941 crisis terms (a high British standing ought to soften the ultimatum).
- The 1907 Anglo-Russian Convention is before the mod's start but should shape the 1910 opening values.
