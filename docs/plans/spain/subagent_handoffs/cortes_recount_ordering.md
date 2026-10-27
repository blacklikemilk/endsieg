# S9 — preserve Republic party shifts in the Cortes recount

Card: `t_9ea8e35d` (endsieg-developer), reviewer `endsieg-qa`.
Branch `TeknoDev-Branch`, base HEAD `a03205963`, no commit (Director integrates).
Era: Republic/post-war 1931-1945, with the Restoration/Directory held as the regression baseline.

Two rounds are recorded here: round 1 repaired the order inside `spain_cortes_recount`, round 2 repaired the
seat arithmetic that the order then fed.

## Round 1 — the ordering defect

`spain_cortes_recount` built the chamber in the wrong order.
It applied the nine legislature flags and the seven accumulated `spain_party_shift_*` to the Restoration base,
clamped, and only then overwrote all seven `spain_cortes_raw_*` from the Republic base.
Every Republic modifier was therefore discarded: focus rewards, financing, elections, proscriptions and
concessions changed a variable that the same effect then threw away.

Reach: 53 call sites of `spain_cortes_recount` (`hoi4.source_lookup`, one definition), and 26 reward lines
writing `spain_party_shift_*` across the Republic and Republican post-war chapters.

### Repair

One order, and only one era base:

1. choose the era base — Republic/post-war when `spain_chapter_restoration` and `spain_chapter_rivera` are both
   absent, otherwise the Restoration/Directory base;
2. apply the nine common flags;
3. add the seven `spain_party_shift_*`;
4. apply the four Republic-only flags inside the Republic branch;
5. clamp every party to the existing 1..1000 band;
6. normalise, correct to 400 seats, recount the government, refresh the panel (unchanged).

Every tuning literal was moved, not retyped, so each appears exactly once and no value could drift.
The file header states the ordering rule so the next editor does not reorder it back.
QA accepted this half in run 47.

## Round 2 — the seat arithmetic the ordering exposed

### Why round 1 did not meet acceptance 3

The card requires the 400-seat correction to be preserved, and it was, unchanged and still called.
But that correction lives in `spain_cortes_fix_seat_total`, and it decided which bench receives the drift with
a bare `check_variable = { var = spain_cortes_top_party value = N }`.
The offline wiki documents the omitted `compare` as `greater_than_or_equals`
(`paradox_wiki/Data structures - Hearts of Iron 4 Wiki.md`, `check_variable` row, line 566), so every party at
or below the top party's index took the drift, and `spain_government_recount` summed parties 1..N instead of
its members.
Before round 1 the defect was latent, because a Republic chamber built from the bare base rounds to exactly
400 and never enters the correction at all; once the shifts and flags reached the chamber, the correction ran
and the chamber landed off 400.

QA reproduced it on the in-play path: `spain_bill_pass_electoral` and `spain_bill_water_electoral` set
`spain_electoral_reform` and call `spain_cortes_recount` on the next line
(`common/scripted_effects/spain_cortes_bills.txt:542-557`).

### Granted scope

Director granted this card ownership of `common/scripted_effects/spain_cortes_parties.txt` for the identity
comparisons only: `spain_cortes_fix_seat_total:77-83`, and `spain_government_recount:103` and `:114-136`.
Nothing else in that file was touched: the `not_equals` at `:43` and the `greater_than` chain at `:47-72` are
byte-identical, as are all thresholds, election, funding, proscription and monthly effects.

### The change

Twenty-nine comparisons now say `compare = equals` where they intend identity: seven for the drift bench, one
for the blank-government test, seven for the governing party and fourteen for the two coalition slots.
`git diff` on that file is 29 insertions and 29 deletions, and nothing else.

`spain_cortes_effects.txt` gained one comment correction and nothing else: the clamp rationale at `:89-92`
claimed the operations "only add", which is false because nine of them subtract, and that one clamp at the end
is the same as clamping after each.
The position is still right for the opposite reason, and the comment now says so.

### Measured before and after, from the shipped source

The in-play electoral-law path in the Republic:

| source | raw | pre-correction seats | drift benches | final seats | sum | `spain_government_seats` |
| --- | --- | --- | --- | --- | --- | --- |
| bare identities (round-1 state, rejected) | 1/22/60/109/80/18/5 | 1/30/81/148/108/24/7 = 399 | 4 | 2/31/82/149/108/24/7 | **403** | **264** (parties 1..4) |
| explicit `equals` (this round) | same | same | 1 | 1/30/81/149/108/24/7 | **400** | **149** (republicans only) |

A 40-scenario sweep over both eras — baseline, each of the 13 flags, each of the seven shifts at +10 and −10,
and two mixtures — went from 11 non-400 chambers, 7 of them regressing from the pinned source's 400, to zero
non-400 chambers.
QA's independent 49-scenario sweep found the same seven regressions and the same mechanism before this round.

### What the test now asserts

`assert_chamber` is a real assertion, not a note.
For every scenario it requires the seven benches to sum to 400, `spain_cortes_total` to read 400, and the drift
to have been applied to exactly one bench when the correction ran, and to none when the shares already total
400.
A regression to the bare form fails on all three counts, which control A below demonstrates.

A new `government` group asserts that the bloc is exactly its member benches: each of the seven single-party
governments alone, four distinct coalitions (`party+1`, `party+2`, two three-way), the majority flag at 201, the
era default only when the chamber is blank (party absent or 0), and a named government surviving a recount.

A new `identities` group runs the pinned pre-fix parties file against the repaired ordering and requires the
old source to fail both identities: a chamber that cannot total 400, the drift applied to `top_party` benches
rather than one, a government that sums parties 1..N, and a named government overwritten by the era default.

### Negative controls, run not assumed

| Control | Result |
| --- | --- |
| A: shipped effects + pinned pre-fix parties (the round-1 state) | 101 checks, **27 failures**, no exception — 403 and 402 chambers, drift on 4 and 3 benches, government 264 and 258 |
| B: `order` group against the pre-fix effects (no era `else`) | 13 checks, **5 named failures**, no `TypeError` — the `:603` crash QA reproduced is gone |
| C: pinned baseline repointed at the repaired files | mutant group **12 failures** plus identities group **5 failures** in 60 checks — the mutants are not vacuous |

Control C is the one that answers "a green run is not evidence": with a vacuous baseline both mutant groups
fail, so the pass above is a real comparison against pre-fix source.

## Regression test

`.tools/tests/test_spain_cortes_recount.py` — **215 checks, 0 failures**, exit 0.
Groups: order 13, baseline 21, shifts 37, clamp 8, flags 35, government 37, calls 4, mutant 55, identities 5.

It is not a restatement of the arithmetic.
It tokenises the shipped Clausewitz text, compiles `spain_cortes_recount`, `spain_cortes_fix_seat_total`,
`spain_government_recount` and `spain_cortes_refresh_display`, and executes them, so the numbers under test
come from the source:

- `order` — two era branches, each assigning every party exactly once (`if`/`else`, no unconditional base left
  over); every base assigned before any modifier; every clamp after every modifier; the era predicate is
  exactly `NOT restoration` + `NOT rivera`; the seven clamps are the 1..1000 band; and the code outside the
  recount block is token-identical to the pinned baseline.
- `baseline` — Republic 12/22/60/95/80/18/5, Restoration and Directory 40/30/25/15/8/5/1, both era flags at
  once resolving to one base, and 400 seats for each.
- `shifts` — all seven parties at +10, −10, +3 and −4 individually, all seven mixed at once, and each shift op
  executing exactly once.
- `clamp` — −1000 lands on 1 in both eras, +1000 lands on the 1000 ceiling, +500 keeps 12+500, and the clamped
  chamber still totals 400.
- `flags` — each of the nine common and four Republic-only flags applied exactly once where its era allows it:
  the common nine in both eras, the Republic-only four once in the Republic and never in the Restoration, with
  the flag block's execution counted so a double application fails.
- `government` — the bloc, the coalitions, the majority flag and the default described above.
- `calls` — the three downstream calls preserved in order and run once, no unexpected external call, and the
  file's definition set unchanged.
- `mutant` — the pinned pre-fix effects file `1ecd63d215cb8853e40749952219136615cc21f5` read through `git show`
  and run through the same engine. Every Republic shift and flag must be discarded there, and its clamp must
  precede its last base. The same group runs every Restoration scenario through both sources and requires
  identical raw values and identical seats.
- `identities` — the same pinned object's parties file, which is byte-identical to `HEAD`'s (sha256
  `f2975516…`), as a second mutant for the two identities.

Both baselines are full object names, not `HEAD`, so committing the repair does not dissolve the controls.
If either object cannot be read the test exits 2 and prints `this is not a pass`.

## Validation actually run

| Check | Result |
| --- | --- |
| `python .tools/tests/test_spain_cortes_recount.py` | `215 checks, 0 failures` (was 165) |
| control A: pinned parties + shipped effects | 27 failures / 101 checks — the invariant is not vacuous |
| control B: pre-fix effects, `order` group | 5 failures / 13 checks, no traceback |
| control C: repointed baseline | 17 failures / 60 checks across the two mutant groups |
| `python tools/check_spain_parties.py` | `decisions: 17, localisation keys: 49` / `no dangling references` |
| `python tools/check_script_bom.py` | no BOM in any changed or new file (`# O` / `"""`); flags only the pre-existing `spain_restoration.txt` |
| structure | parties 306/306 braces, effects 185/185, no `}word` splice; 29 `compare = equals`, 21 `greater_than`, 1 `not_equals`, 1 `less_than`, 1 `greater_than_or_equals` |
| `hoi4.script_validate` parties | 259 commands, 0 findings, `SCRIPT_CHECK_PARTIAL`, `unresolvedCount 0`, 155 argument blocks unchecked, 9 roots |
| `hoi4.script_validate` effects | 204 commands, 0 findings, `SCRIPT_CHECK_PARTIAL`, 137 unchecked, 4 roots |
| `hoi4.source_lookup` `spain_cortes_fix_seat_total` | 1 definition, `spain_cortes_parties.txt:38-87`, not shadowed, 1 reference (`spain_cortes_effects.txt:157`) |
| `hoi4.source_lookup` `spain_government_recount` | 1 definition, `spain_cortes_parties.txt:95-142`, not shadowed, 6 references (`effects:158`, `parties:151,206,226,234,262`) |

`SCRIPT_CHECK_PARTIAL` and `validation.passed: false` are the route's unresolved-coverage code
(`unresolvedCount: 0`), identical in command count and coverage before and after, and not a finding.

## MCP evidence

```text
Route: hoi4.script_validate   Input: path=common/scripted_effects/spain_cortes_parties.txt, workspaceId=current
Result: 259 commands checked, 0 findings, unresolvedCount 0, argumentBlocksUnchecked 155, roots 9
Checks: syntax, command_kind, declared_scope, event_popups, known_mistakes
Resource: game_doc revision 9227e238bce49345e9c358598b4dd4940c733d906b72324e8a02a57ecb42093b

Route: hoi4.script_validate   Input: path=common/scripted_effects/spain_cortes_effects.txt, workspaceId=current
Result: 204 commands checked, 0 findings, unresolvedCount 0, argumentBlocksUnchecked 137, roots 4

Route: hoi4.source_lookup      Input: symbol=spain_cortes_fix_seat_total, maxReferences=20, maxLines=40
Result: 1 definition, 38-87, overridden=false, sourceShadowed=false, referenceCount 1
Resource: workspace_index revision e9383877565762d9e4af7ab63313e39b52a1a14c00e3f85267151640bccb9927

Route: hoi4.source_lookup      Input: symbol=spain_government_recount, maxReferences=20, maxLines=40
Result: 1 definition, 95-142, overridden=false, sourceShadowed=false, referenceCount 6
Resource: workspace_index revision e9383877565762d9e4af7ab63313e39b52a1a14c00e3f85267151640bccb9927
```

Not run, with reason: `focus_inspect` / `focus_render` (no focus file is owned or changed here),
`package_check` / `decision_inspect` (the decision and localisation surface is unchanged and not owned), and
`error_log` (no launch, so there is no current log).

## Documentation and precedents read

`documentation/effects_documentation.md` (`set_variable`, `add_to_variable`, `clamp_variable`, `if`) and
`documentation/triggers_documentation.md` (`check_variable`); offline
`paradox_wiki/Data structures - Hearts of Iron 4 Wiki.md` (the `check_variable` row at line 566: the omitted
`compare` is `greater_than_or_equals`; `clamp_variable` changes only the current value); vanilla
`common/scripted_effects/GRE_scripted_effects.txt:23-25` (identity compares written with explicit
`compare = equals`), `AST_scripted_effects.txt` (additive modifiers, clamp last) and `else = {` across 34
vanilla scripted-effect files.
Of 747 `check_variable` blocks in vanilla `common/scripted_effects`, 193 carry an explicit `compare` and none
matches the bare `{ var = X value = N }` identity shape.

## Not done, out of scope, and what it would take

- **No game launch and no in-game check.** Nothing here proves a focus click moves a seat, that a bill gate
  opens, or that the panel repaints. A source simulator plus the documented default is not engine proof; one
  Republic focus reward in a launched campaign is.
- **Three bare identity compares remain in `spain_cortes_parties.txt`, outside the granted lines**: `:147` in
  `spain_government_strain`, `:194` in `spain_hold_election` and `:288` in `spain_party_monthly`, all
  `check_variable = { var = spain_government_majority value = 0 }`.
  Under the documented default each is always true, so the minority stability and coup penalty in
  `spain_government_strain`, the incumbent-loss block in `spain_hold_election` and the monthly minority penalty
  in `spain_party_monthly` all fire whether or not the government has a majority.
  This repair makes `spain_government_majority` a meaningful 0/1 signal for the first time, so those three are
  worth their own card and one launch; they were outside the grant and were not touched.
- **The same pattern is mod-wide**: 83 bare `{ var = X value = N }` compares across `common/` — 31 in
  `common/scripted_localisation/spain_cortes_panel.txt`, 27 in `common/decisions/spain_parties.txt`, 20 in
  S3's `spain_cortes_bills.txt`, the 3 above, 1 in `common/national_focus/spain_republic.txt` and 1 in
  `common/decisions/spain_cortes.txt`.
  Whether each is an identity compare or an intended `>=` band needs reading case by case; the count is a
  pointer, not a defect list.
- `spain_chapter_*` flags are still never cleared (P1b), the bill caches are still unseeded until the clerk
  counts (P2), and the hemicycle frame indexing is still 1..8 against an 8-frame strip.
  No claim is made that the Cortes is finished.
- `common/national_focus/spain_restoration.txt` carries a BOM in `HEAD` (byte-identical in the working tree,
  untouched here); `tools/check_script_bom.py` flags it and it is not this card's file.
- The card's owned test path is inside `.tools/`, which `.gitignore:5` ignores. Director selected force-add of
  exactly that path at integration, and no `.gitignore` change was made here.
