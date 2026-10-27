# I9 handoff: era-correct and serialised wartime Great Game demands

Card: `t_804cba7b` (I9), Developer `endsieg-developer`, branch `TeknoDev-Branch` at `ce6247246`.
Independent reviewer: `endsieg-qa`. No Git commit: Director integrates.
Date of this pass: 2026-10-27.

## 1. What was repaired

`iran_influence_tick` in `common/scripted_effects/iran_campaign.txt` dispatched Iran's three wartime
Great Game demands as three independent `if` blocks. Source confirmed the three defects the I2 design
review predicted:

- the British transit branch had no era gate, so `ENG = { has_war = yes }` in 1914 satisfied it and
  `iran_transit_demand_seen` was burned a generation early;
- the northern branch had `date > 1941.1.1` and the Allied branch `date > 1940.1.1`, but neither waited
  for `iran_negotiation_open`, so a demand could be spent while another negotiation was on the table;
- all three could dispatch in the same monthly tick, putting three incompatible corridor demands on
  one day.

The repair makes the three branches one `if` / `else_if` / `else_if` chain, fences all three to the war
years, gives every branch the negotiation guard, and leaves each branch's own seen flag set inside the
branch body. The branches that follow the chain are untouched.

## 2. Files changed

| Path | Change |
| --- | --- |
| `common/scripted_effects/iran_campaign.txt` | lines 441-478 replaced: the three wartime demand branches and their explanatory comment. Now 15 comment lines plus one `if` and two `else_if` members. |
| `docs/systems/iran_great_game.md` | "The powers act" body rewritten for correct tick attribution, era fences, chain order, negotiation guard and preserved option consequences. Two Known limits bullets and one Future bullet added. |
| `.tools/tests/test_iran_wartime_demands.py` | new source-driven regression, pre-edit snapshot rejection and four mutants. |
| `docs/plans/iran_1910_1945/subagent_handoffs/wartime_demands.md` | this handoff. |

Integration note for Director: `.gitignore` line 5 ignores the whole `.tools/` directory, so the new
test file is untracked and ignored. Existing tests under `.tools/tests/` are tracked and still show as
modified, so they were added before that rule or forced. Staging this one needs
`git add -f .tools/tests/test_iran_wartime_demands.py`. This worker stages nothing.

Not changed, by design:

- `events/iran_campaign.txt`: no defensive trigger guard was needed. The three events are
  `is_triggered_only` and the tick fires them in the same effect execution, so there is no window in
  which eligibility can lapse between the flag write and delivery. Every event id, option, `ai_chance`
  weight, picture, idea, timed idea and variable payload is byte-identical to `ce6247246`, and the test
  asserts that per event.
- `localisation/english/iran_great_powers_l_english.yml`: **no keys edited**. The existing `.74` /
  `.75` / `.76` text still matches the repaired routing, and the test asserts those keys are unchanged
  against the pre-edit revision.
- No focus, decision, constants, act, spirit, Balance of Power, `on_actions`, shared registry, Spain or
  China file was touched.

## 3. Routing before and after

| State | Before (`ce6247246`) | After |
| --- | --- | --- |
| 1914, Britain at war, mission in Tehran | `.74` dispatches, `iran_transit_demand_seen` set | nothing dispatches, no seen flag |
| 1919 standing-demand era | `.74` dispatches | nothing dispatches |
| 1940.12.31 | `.76` dispatches (`date > 1940.1.1`), `.74` dispatches | nothing dispatches |
| 1941.1.1 | `.74` and `.76` dispatch together | `.74` only |
| 1941.1.2, all three predicates true | `.74`, `.75` and `.76` dispatch together | `.74` only |
| next month with `.74` seen | `.75` and `.76` together | `.75` only |
| next month with `.74` and `.75` seen | `.76` | `.76` |
| all three seen | nothing | nothing |
| `iran_negotiation_open` set | `.75` and `.76` still dispatch | nothing, no seen flag consumed |
| `iran_agreement_transit_allied` held | `.75` suppressed by source intent | both corridor offers suppressed, `.76` can still fire |
| Britain absent, north at war | `.75` and `.76` | `.75` |
| non-Iran country | nothing | nothing |
| demand dispatch in the same tick as an incompatible-obligations state | `.73` plus demands | `.74` and `.73` both run, `iran_competing_concessions` and the sovereignty band still applied |

Era fences: `.74` and `.76` use `date > 1940.12.31`, `.75` keeps `date > 1941.1.1`. The fence is a
year-level gameplay era boundary, not a claim about the day of any ultimatum.

Cadence and ownership: `common/on_actions/iran_campaign.txt` calls `iran_coup_tick`,
`iran_great_game_tick` and `iran_influence_tick` from `on_monthly_PER`, and `iran_campaign_tick` from
`on_daily_PER`. The wartime demands are in `iran_influence_tick` (monthly), the standing `.71` / `.72`
demands are in `iran_great_game_tick` (monthly). No world-iterating `on_action` was added, no
open-demand framework and no asynchronous lock.

## 4. Test evidence

`python .tools/tests/test_iran_wartime_demands.py` -> `38 checks, 0 failures`, exit 0.
`python .tools/tests/test_iran_wartime_demands.py --detail` -> the same 38 checks listed, exit 0.

The test parses the shipped files rather than retyping the routing:

- `common/scripted_effects/iran_campaign.txt` for the `iran_influence_tick` body;
- `common/scripted_triggers/iran_campaign.txt` for `iran_campaign_country`;
- `common/script_constants/iran_campaign.txt` for `constant:iran_story.*`;
- `common/on_actions/iran_campaign.txt` for the hook wiring;
- `events/iran_campaign.txt` and the localisation file for the preservation checks.

It then executes that parsed body with the engine's own `if` / `else_if` precedence: a member of the
chain runs only if no earlier member ran. Eighteen declared country states are executed, and
`common/on_actions` is asserted to call the effect from `on_monthly_PER` and not from `on_daily_PER`.

Structural checks: the three branches are adjacent `if` / `else_if` / `else_if` entries in source order,
the branch that follows them is a standalone `if` carrying `iran_campaign.73`, each branch carries its
era fence, each carries `NOT = { has_country_flag = iran_negotiation_open }`, each sets only its own
seen flag, and the tick contains no `<=` or `>=`.

The pre-edit snapshot (`git show ce6247246:...`) is rejected:

```
PASS the pre-edit chain is rejected by the structural check
   note: the chain is ['if', 'if', 'if'], not one if with two else_if members;
   iran_campaign.74 is not fenced at date > 1940.12.31 (found []);
   iran_campaign.75 does not wait while iran_negotiation_open is set;
   iran_campaign.76 is not fenced at date > 1940.12.31 (found [('>', (1940, 1, 1))])
PASS the pre-edit tick dispatches a British demand in 1914
PASS the pre-edit tick dispatches all three demands in one month
   note: 10 pre-edit behaviour failures
```

Four in-memory mutants, each applied to the current source, each failing for its own reason and each
still passing the rest of the suite:

| Mutant | Case it breaks | It dispatches |
| --- | --- | --- |
| British era fence reverted | `tick: 1914 Britain at war dispatches nothing` | `['iran_campaign.74']` |
| northern negotiation guard reverted | `tick: negotiation open blocks the northern demand too` | `['iran_campaign.75']` |
| Allied negotiation guard reverted | `tick: negotiation open blocks the Allied demand too` | `['iran_campaign.76']` |
| independent `if` blocks restored | `tick: all three eligible dispatch only the British transit` | `['iran_campaign.74', 'iran_campaign.75', 'iran_campaign.76']` |

Each mutant check asserts the specific dispatch it leaks, not merely that some check failed, because a
mutant that trips an unrelated case would prove nothing.

## 5. Repository validation runs

| Command | Output |
| --- | --- |
| `python tools/iran_audit.py --mod . --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"` | `73` Iran-owned files, `328` focuses, `171` events in 12 namespaces, `112` decisions, `198070` localisation keys (0 missing focus keys), `32412` sprites (0 unresolved), `Clean: no problems found` |
| `python tools/iran_reference_check.py --game "..."` | `49` files, `327` event references, `155` idea references, `9358` events known, `7891` ideas known, `Every reference resolves` |
| `python .tools/tests/test_iran_bop_transitions.py` | `25 checks, 0 failures` |
| `python .tools/tests/test_iran_flag_readers.py` | `21 checks, 0 failures` |
| `python .tools/tests/test_iran_focus_tooltips.py` | `590 checks, 0 failures` |
| `python .tools/tests/test_iran_gulf_rewards.py` | `2` failures, both in its own pinned localisation baseline, see below |
| `python tools/check_script_bom.py` | reports a BOM in `common/national_focus/spain_restoration.txt`, see below |

Baseline issues recorded, not repaired here because neither file is in this card's ownership:

1. `test_iran_gulf_rewards.py` pins `localisation/english/iran_interwar_l_english.yml` at
   `f8f9225b048874109ff965654c9fb7fa973df0cd` and asserts the description is the only changed value.
   The file is clean in `git status`, and `HEAD` (`ce6247246`) already differs from that baseline by ten
   `_tt` keys (`grep -c ira` gives 17 lines at `HEAD` against 7 at the pinned revision). The check is
   stale against a later committed Iran card, not broken by this change: it reads only that
   localisation file and the baseline commit, neither of which this card touched.
2. `tools/check_script_bom.py` reports `BOM in script file: common\national_focus\spain_restoration.txt`.
   That is a Spain working-tree file owned by another session, dirty before this card started.

## 6. MCP evidence

All routes read-only. `workspaceId` resolved to `endsieg` from the server `cwd` in every call.

- Route: `hoi4.source_lookup`, input `{symbol: "iran_influence_tick", includeReferences: true, maxReferences: 20, maxLines: 80}`, pre-edit.
  Result: 1 definition, `mod:common/scripted_effects/iran_campaign.txt` lines 418-542, 1 reference (`on_monthly_PER`, `mod:common/on_actions/iran_campaign.txt:6`), `referencesComplete: false`, `unresolvedReferenceCount: 2570`.
  Revision `ea7dfb2ecadf32fdc41c8d1c853b569fb978d6bfe745d9b8161830af39bea92c`. Resource: none (inline source).
- Route: `hoi4.source_lookup`, input `{symbol: "iran_great_game_tick", maxLines: 40}`, pre-edit.
  Result: 1 definition, lines 390-414, same single reference. Same revision.
- Route: `hoi4.source_lookup`, input `{symbol: "iran_influence_tick", maxLines: 61}`, post-edit.
  Result: 1 definition, lines 418-558 (was 418-542), same single reference. Revision `6a9563d16fa0376570c78616b4c1048e805bcc0f8c6c46557f536523e93ec09e`.
- Route: `hoi4.source_lookup`, input `{symbol: "iran_great_game_tick", maxLines: 30}`, post-edit.
  Result: unchanged, lines 390-414. Revision `9cc0f3f00e6fda97cf266b4b0514605618b27d6a741cd4c0dd2c4d7f1960e6da`.
- Route: `hoi4.event_inspect`, input `{mode: "scan", selector: {kind: "namespace", namespace: "iran_campaign"}}`, pre-edit baseline.
  Result: `analysisMode: focused`, `helpers: 0` (focused boundary defers workspace helper projections), 9316 events, 1214 entries, 35078 edges, 14569 options, 17696 state accesses, 2414 diagnostics of which 0 blocking, 4801 unresolved nodes, 0 skipped sources. Revision `33196bbabcc72107b76be18ccf50e11f8f1b535d900405fbd24c4fa7d6403ed3`, graphHash `78bdb163…`.
  Resources: `event-scan-33196bbabcc7.json` sha `88179f35…`, `event-graph-33196bbabcc72107…json` sha `bb2a123b…` under `hoi4-agent://workspace/endsieg/artifact/`.
- Route: `hoi4.event_inspect`, input `{mode: "trace", selector: {kind: "event", eventId: "iran_campaign.74"}, direction: "upstream", maxDepth: 3, maxNodes: 60}`, pre-edit.
  Result: 1 artifact, `event-trace-33196bbabcc7.json` sha `948d71c9…`, same revision and graph hash, 0 blocking diagnostics.
- Route: `hoi4.event_inspect`, input `{mode: "lint", selector: {kind: "event", eventId: "iran_campaign.74"}, maxDepth: 2, maxNodes: 40}`, pre-edit and again post-edit with `refresh: true`.
  Result: 0 findings, 0 blocking diagnostics, same counts, revision `33196bbabcc7…` both times. Lint artifact shas `33be4a08…` (pre) and `ef4bb3fe…` (post).
- Route: `hoi4.event_inspect`, input `{mode: "scan", selector: {kind: "event", eventId: "iran_campaign.74"}, refresh: true}`, post-edit.
  Result: same counts, revision `33196bbabcc7…`, graphHash `78bdb163…` (identical), scan artifact sha `7aa52ca7…` (changed from `88179f35…`).
- Route: `hoi4.script_validate`, input `{path: "common/scripted_effects/iran_campaign.txt"}`, after the first write.
  Result: 6 findings, all `SCRIPT_EXPECTED_COMMAND` at line 442. This was a real defect I introduced: a
  comment continuation line was written without its leading `#`, which is the exact first-line/comment
  trap the static-validation skill warns about. Fixed by restoring the `#`, then re-validated:
- Route: `hoi4.script_validate`, input `{path: "common/scripted_effects/iran_campaign.txt"}`, final.
  Result: `SCRIPT_CHECK_PARTIAL`, 0 findings, `checksPerformed: [syntax, command_kind, declared_scope, event_popups, known_mistakes]`, `parametersChecked: false`, `checkedCommands: 443`, `argumentBlocksUnchecked: 79`, `unresolvedCount: 0`, `roots: 16`, `unknownScopeRoots: 16`, documentation revision `9227e238…` with `effectCount: 544`, `triggerCount: 656`.
- Route: `hoi4.reference_search`, input `{query: "else_if"}`.
  Result: 4 hits. Coverage: `game_doc` 50 files / 3281 sections, `wiki` 54 files / 8359 sections, `script_doc` unavailable.
- Route: `hoi4.reference_read`, input `{id: "f437d1c2…", revision: "997ddb09…"}` (offline wiki, "Effects", "If statements", lines 4454-4503).
  Result: `else_if` semantics, unnested form preferred, `limit` gates each member.

What these routes cannot prove, stated plainly:

- `event_inspect` cannot see the change at all. The routing lives inside a scripted effect, and the
  post-edit graph hash (`78bdb163…`) and graph artifact sha (`bb2a123b…`) are byte-identical to the
  pre-edit ones while the scan inventory sha moved. `mode: "compare"` was therefore not run: with one
  identical graph on both sides it could not attribute a difference, and the event graph does not model
  scripted-effect ordering in the first place. The executed-source test is the evidence for this repair.
- Focused analysis kept `helpers: 0`, so the helper-projection pass did not cover the effect chain.
- `script_validate` leaves 79 argument blocks unchecked and 16 roots at unknown scope.
- Nothing here proves in-game firing, ordering or tooltips. No game was launched, no save was read and
  no live scenario was run.

## 7. References consulted

- Offline wiki `Effects - Hearts of Iron 4 Wiki.md`, "If statements" (unnested `if` / `else_if`
  precedence, `limit` per member) and `Triggers - Hearts of Iron 4 Wiki.md:343`.
- Installed game documentation through `hoi4.script_validate` (`game_doc` revision `9227e238…`).
- Vanilla precedent for a country-scoped monthly hook with unnested conditional blocks:
  `common/on_actions/00_on_actions.txt:5920` (`on_monthly_GER`), and the existing `on_monthly_PER` at
  `common/on_actions/13_goe_on_actions.txt:1693`.
- The repository's own existing fence convention: `common/scripted_effects/iran_campaign.txt:235`
  already uses `date > 1940.12.31` for the Allied-pressure crisis.

## 8. Limits of this pass

- The repair routes the three demands and fences them. It does not give them a new aftermath: `.74`,
  `.75` and `.76` keep their original option set, and no patron agenda, fresh negotiating position or
  post-occupation settlement was added. The accepted I2 slices A/B/C remain separate, unfinished work.
- `iran_campaign.75` describes a northern mission that has watched a British request arrive. The chain
  makes that the normal order, but a Britain that never entered the war still lets `.75` arrive alone.
  Recorded in the doc's Known limits rather than fixed by inventing new prose or a new gate.
- No visual, localisation or asset surface changed, so no render, icon or screenshot evidence exists and
  none is claimed. Existing icons and every asset reference are untouched.
- No engine behaviour was observed. A user-run launch remains the only way to see the demands appear in
  a campaign.

## 9. Next steps

1. Independent QA (`endsieg-qa`) reruns `.tools/tests/test_iran_wartime_demands.py` plain and `--detail`,
   reads the three branches and the branches that follow them in the shipped effect, reads
   `common/on_actions/iran_campaign.txt`, and confirms the event payload and localisation bytes against
   `ce6247246` independently.
2. Director reviews and integrates the four changed paths. No commit was made by this worker.
