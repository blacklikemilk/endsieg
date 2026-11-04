# Republic of China: 1910 campaign settlement and supply

Updated 2 November 2026 for a reported Republican defeat in April 1913 in a fresh historical-AI 1910 campaign.

## Confirmed source problems

The live error log rejected `num_of_owned_states` in `ww1_china.19`. Independently, that event required the Republic to retain Wuhan and more than four states before historical Qing could abdicate. The alternate AI surrender branch explicitly excluded historical Qing. Losing Wuhan could therefore leave the historical civil war running indefinitely. The log proves the rejected trigger; the user's report supplies the capitulation outcome, which is not itself recorded in the game log.

The China state model also used unsupported `COUNTRY` parameter blocks in scripted-trigger calls and called its array builder without a supported scope at startup. These generated separate logged errors; they are not established causes of the military defeat.

## Changes

- Historical AI abdication remains available after 11 February 1912 during the actual Xinhai war while the Republic exists, has territory and has not capitulated. It no longer requires Wuhan or battlefield dominance. Human Qing and nonhistorical AI retain their existing surrender conditions and survival routes.
- The option rechecks its complete eligibility at selection time, refuses repeated settlements, switches a Qing player before annexation and retains troop transfer and the existing Republic/Tibet follow-up effects.
- The existing one-time Hubei uprising setup receives 40 convoys through the native runtime `add_equipment_to_stockpile` effect, using `convoy_1` and producer `RCH`. This supplies the transport reserve that the 1914 bookmark already provides, without a daily refill.
- A targeted Republic daily hook can move the provisional capital to Nanjing from January 1912, provided the Republic owns the state and controls the city. The later Beijing move requires the existing Yuan-presidency flag, the March date, ownership and city control. Flags prevent repeated moves; human capitals outside the intended historical seats are preserved. This applies to the early campaign, not later bookmarks.
- State-model holding tests now run in each candidate country's scope; `PREV` inside the global state array identifies that candidate. All 19 candidates and all 62 state scopes are preserved. Startup builds the array once from fixed state scope 283.

## Military balance retained

No troop OOB, combat modifier or rifle allocation was changed. Qing begins with 34 six-battalion divisions and loses its two Hubei units at the uprising. The Republic receives eight six-battalion divisions followed by 57 four-battalion provincial formations. Its existing 12,000-rifle reserve covers the initial equipment shortfall before combat losses and new recruitment. The 1914 Republican OOB is a bookmark file, not the uprising's runtime army.

The opening supply capital at Hubei reaches two of the Republic's 19 owned hubs through the audited rail network; the Nanjing cluster reaches five and the eastern port network. Actual supply delivery and AI front management still require a playtest. No speculative train grant was added, since native starting-train seeding exists.

## Validation and playtest

All six edited script files parse. Ninety-two bounded source checks cover historical, human and nonhistorical eligibility; stale and repeated event options; capital ownership, control, date and player safeguards; one-time transport grants; candidate scope, array initialization and immutable reunifier recording. All 17 inventoried troop OOBs retain their pre-edit hashes. An independent script review compared the new effects with installed vanilla constructs.

These checks do not emulate the engine, combat, supply throughput or peace conferences. HOI4 was not launched. Test a fresh historical 1910 campaign through February–March 1912 and verify Qing abdication, surviving Republican forces, the capital moves and Tibetan settlement. Later Republican succession/rebellion content should still operate. A save before Republican defeat can receive the settlement/capital corrections; the opening convoy grant only runs when the uprising is first raised. An already annexed Republic is not resurrected by this patch.

## References

- [US diplomatic account of the abdication and Yuan's presidency](https://history.state.gov/historicaldocuments/frus1913/d89).
- [March 1912 telegram concerning Yuan's inauguration at Peking](https://history.state.gov/historicaldocuments/frus1912/d85).
- [Contemporary 1912 China correspondence, including the provisional government at Nanking](https://history.state.gov/historicaldocuments/frus1912/ch11?start=61).
- Installed vanilla `events/AAT_Finland.txt`, convoy stockpile grant; `documentation/effects_documentation.md`, `set_capital` and `change_tag_from`; `common/scripted_effects/00_scripted_effects.txt`, array loops with candidate scope in `PREV`.
