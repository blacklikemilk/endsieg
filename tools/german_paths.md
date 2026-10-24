# German interwar branch expansion

This expansion covers the non-industry routes of `INT_germany`. It adds optional focuses to six routes while preserving the 99 focus IDs present before this change, existing mutually exclusive political choices, historical event schedules and the `INT_GER_enter_1936` transition.

| Route | New stages | Decisions and event choices |
|---|---|---|
| Republican | Parliamentary commissions, civic education, social compromise, local government, crisis cabinet, constitutional defense | Oversight versus cabinet coordination; coalition relief versus retrenchment; civic and municipal projects. |
| Council republic | Shop-floor committees, planning board, welfare, military schools, constitutional charter | Worker councils versus central planning; council, welfare and training projects. |
| Conservative/monarchist | Prussian administration, federal chambers, royal railways, restored court and reconciliation | Federal compact versus crown prerogative; administrative and railway projects. |
| Eastern cooperation | Rapallo commission, trade network, eastern exercises and joint aviation trials | Civilian commerce versus restricted military research; trade and training projects. |
| Versailles revision | Diplomatic treaty review, foreign press, hidden procurement and professional officers | Legal advocacy versus covert procurement; decisions support the existing revision chain. |
| Authoritarian 1933–35 | Party administration, controlled press, labor front, state and armaments contracts | Bureaucratic coordination versus propaganda; projects include stability costs and stay within the existing historical path. |

The expansion adds 29 focuses, 27 one-time decisions, seven choice events and 20 supporting national spirits. The new routes are optional. Their focuses and decisions check the current government, historical date or required partner where appropriate. They do not change existing government-switching focuses or hand out the 1936 tree early. Decision rewards include national spirits, stability, research, experience, manpower and political capacity. The route decisions are one-time; several focus rewards add a single offsite factory. The one-use aviation research bonus avoids a permanent research-slot gain for a small Political Power cost.

Historical framing draws on the Deutsches Historisches Museum's accounts of the [Weimar constitution](https://www.dhm.de/lemo/kapitel/weimarer-republik/innenpolitik/verfassung), [elections and state representation](https://www.dhm.de/lemo/kapitel/weimarer-republik/innenpolitik/wahlrecht), [Reichswehr and Soviet cooperation](https://www.dhm.de/lemo/kapitel/weimarer-republik/innenpolitik/reichswehr), and [the dismantling of representative institutions in 1933](https://www.dhm.de/lemo/kapitel/ns-regime/etablierung/gleichschaltung). Policy choices and rewards are game abstractions.

## Non-launch validation

Run `python tools/validate_german_paths.py --vanilla "<installed Hearts of Iron IV directory>"` for brace balance, focus IDs and coordinates, prerequisite reachability, one-time decision gates, English localisation, referenced events, and vanilla sprites. This passed with 128 unique focus IDs and 197 unique path-localisation keys. The ten modifiers used by new national spirits have current vanilla precedents. The crisis cabinet now offers distinct temporary relief or retrenchment effects; the press decision has a war-support gain and stability cost. The industry branch remains covered by `python tools/validate_german_industry.py --vanilla "<installed Hearts of Iron IV directory>"`.

## In-game checks for the player

1. Follow each of the three early government routes in separate saves. Confirm only the matching political decisions appear after their focuses complete.
2. Follow both 1933 republican outcomes. The crisis cabinet and constitutional decisions should not remain available after appointing Hitler.
3. For the council, monarchist, Eastern and treaty branches, test each choice event and confirm the resulting one-time decisions show their actual costs and rewards.
4. Test Eastern cooperation with SOV present and absent; no Soviet-targeted decision should be available when SOV does not exist.
5. Test the 1935 authoritarian route and the unchanged Versailles repudiation effects. Confirm no added side focus blocks the transition to the 1936 tree.
6. Inspect focus layout and event/decision text in game; read `error.log` after representative 1919, 1925, 1929 and 1933 campaign starts. Codex does not launch the game.
