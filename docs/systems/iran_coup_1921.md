# The Cossack Question — the 1921 contest

Iran's 1921 coup is the hinge of the interwar chapter: it decides whether the Pahlavi settlement is even reachable, and therefore which 1936 tree Iran loads.
It is deliberately not a single focus.

## State

| Variable | Range | Meaning |
| --- | --- | --- |
| `iran_reza_influence` | 0–100, opens at 25 | Reza Khan's hold over the army and the court |
| `iran_officer_loyalty` | 0–100, opens at 50 | how far the officer corps answers to the crown rather than to him |

Both are initialised by `iran_coup_init`, called from `iran_initialize_campaign`, and clamped by `iran_coup_clamp` after every change.

## Flow

1. `on_monthly_PER` calls `iran_coup_tick` while the date is between 1919 and December 1925 and no settlement has been reached.
2. A player who has committed to the Cossack path (`iran_cossack_ascendant`) gains `reza_drift` (2) influence a month — inaction is what produced the historical coup.
   A player on the Majlis path loses the same amount, because a sitting parliament keeps him in check.
3. The `IR2_the_coup_of_1921` and `IR2_reza_khan_minister` focuses add 30 and 20, so the historical line reaches the threshold without any decision.
4. `IR2_pahlavi_settlement` requires `iran_story.reza_threshold` (60) influence, shown through the `iran_coup_standing_tt` tooltip.
   A player steering towards a Qajar restoration, a constitutional crown or a republic has to keep him *under* it.

## Decisions (category `iran_coup_1921`, 1919–1925 only)

| Decision | Cost | Effect |
| --- | --- | --- |
| Court the Officers | 75 PP | +10 influence, −5 officer loyalty, +command power |
| Buy the Brigade's Obedience | 100 PP | −15 influence, +10 loyalty, +10 authority |
| Motion Against the War Minister | 100 PP, Majlis path, stability > 30% | −20 influence, +10 authority, −5% stability |
| Bring Him Into the Cabinet | 75 PP, once | +20 influence, sets `iran_reza_khan_minister` |
| Break the Cossack Command | 150 PP, authority 50, once | −25 influence, −5 loyalty, −5% stability, +50 PP back on completion |

All five disappear the moment `iran_regime_settled` is set, so they cannot leak into the 1936 chapter.

## Interactions

- The settlement flags feed `iran_route_chapter`: Pahlavi goes to the DLC tree, Qajar and constitutional monarchy go to `iran_ww2`.
- `iran_authority` is used as the cost of the heavier decisions, so a weak state cannot purge its own army.
- Decisions use the Majlis path trigger, so the parliamentary route has a tool the court route does not.

## Tuning

Everything numeric lives in `common/script_constants/iran_campaign.txt` under `reza_*` and `officer_*`.
Drift (2) against a repeatable −20 every 150 days is what makes suppression viable rather than trivial; changing either needs a scenario comparison, not a guess.

## Needed icons

- Decision category: reuses `GFX_decision_category_power_struggle` (vanilla). A purpose-made Cossack category plate would be better but is not required.

## Future

- A forced-coup event if influence passes 85 while the crown still holds real authority.
- Officer loyalty currently has no downstream effect after 1925; it should feed army organisation or the 1941 crisis.
