# German interwar industry overhaul

The industry section of `INT_germany` uses four economic phases while retaining all 91 existing focus IDs and the political branches. It adds eight focuses, nine one-time decisions, four events and supporting national spirits. Only three decisions grant factories (75/100/100 Political Power for reconstruction/boom/recovery); other projects provide infrastructure, research, temporary support or financial preparation.

| Phase | Progression | Player decisions |
|---|---|---|
| Reconstruction | Reconstruction Commission, transport and municipal reconstruction | Choose initial priorities and fund limited reconstruction projects. |
| Stabilization | Reparations crisis, end Ruhr resistance, stabilize the currency | Establish the basis for investment without bypassing the existing historical crisis events. |
| Roaring Twenties | Investment policy, modernization, railways, chemicals, housing, electrification, domestic capital, exports and reserves | Choose credit-led expansion or domestic saving; complete one-time investment projects. Reserve preparation must finish before the crash. |
| Depression and recovery | Emergency response, public works or austerity, bank restructuring, recovery, retraining and industrial renewal | Deal with the consequences of borrowing and fund the final recovery project. |

The Depression response is a separate visual root: it requires stabilized currency and the existing 1929 crash flag, rather than completion of the optional boom projects. Bank restructuring opens after 12 July 1931; broad recovery remains gated to 1933. Both existing policy choices lead to recovery. Economic choices do not force a change of government.

`INT_depression.1` remains the sole source of the global Depression for Germany. Its German option invokes the new credit-cycle cleanup, avoiding a second crash scheduler. Additional credit exposure and reserves alter the new branch's shock; they do not erase the existing Depression. Late focus/event completion must not restore the boom. Historical news and milestones remain in place.

## Historical framing

The dates and themes follow the Deutsches Historisches Museum's accounts of [currency reform](https://www.dhm.de/lemo/kapitel/weimarer-republik/innenpolitik/waehrungsreform-1923), the [Dawes Plan](https://www.dhm.de/lemo/kapitel/weimarer-republik/aussenpolitik/dawesplan), and [interwar industry](https://www.dhm.de/lemo/kapitel/weimarer-republik/industrie). The investment-policy choices and reserve mechanic are gameplay abstractions, not claims that a reserve fund could have prevented the Depression.

## Non-launch checks

Run `python tools/validate_german_industry.py` for braces, local references, localization, focus coordinates, dependency cycles and structural recovery reachability under either policy. Supply `--vanilla "<installed Hearts of Iron IV directory>"` to also check sprites. These checks pass for the German tree, including the later path expansion (128 focuses, 334 localization keys). All six modifier names used by the new spirits have precedents in the installed vanilla idea files (Steam build 25205862). This does not execute the game engine or measure AI balance.

The repository's broader `tools/validate_focus_split.py` currently reports checksum mismatches in unrelated vanilla focus copies. Those files are outside this change.

## User playtest checklist

1. Start the German interwar tree and complete Reconstruction Commission. Check event presentation, decision category visibility and project costs.
2. Follow currency stabilization into the Roaring Twenties. Test each investment policy in separate saves. Confirm project rewards, national spirits and one-time decision removal.
3. In the foreign-credit route, compare October 1929 with and without completed reserves. Confirm the original Depression still applies and the boom bonus disappears. Check a reserve focus finishing after the crash cannot add protection retroactively.
4. Complete the boom focus or leave its event open until after the crash. No late option should reapply a boom spirit.
5. Follow public works and austerity separately. Both must reach bank restructuring, 1933 recovery, retraining and final industrial renewal. The extra credit penalty should disappear during recovery.
6. Check projects with no eligible controlled core state or no factory slots: construction decisions should be unavailable, rather than charging for no result.
7. Inspect the focus layout, decision text and event tooltips in-game; verify the 1936 transition hides interwar decisions. No live playtest has been performed by Codex.
