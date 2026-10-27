# Handoff - Iran focus requirement tooltips (I8)

Card `t_65086d91`, assignee `endsieg-developer`, branch `TeknoDev-Branch`, baseline `ad0169dd1c6f67b4b8904f9f1d90f73f3f47754a`.
English-only Milestone 1. No launch, no commit, no stage, no push.

Delivery history: the edits and the test were written in the first run, which exhausted its iteration budget
before it could hand off; the second run re-verified everything from source and by execution (see
"Independent verification of this delivery") and wrote this handoff. Nothing from the first run was taken on
trust, and no file outside the card's ownership was touched.

## What was wrong

The 1925-1935 (`IR2_*`) and 1936-1945 (`IR3_*`) focus chapters printed internal script names in the
focus tooltip wherever a requirement was written with a bare flag or with a bare scripted trigger:

```
available = { NOT = { has_country_flag = iran_crisis_anglo_persian_done } }
```

renders as `has country flag: iran_crisis_anglo_persian_done`, and

```
available = { has_country_flag = iran_nationalist_officers OR = { iran_path_army = yes iran_path_tribal = yes } }
```

additionally renders the unlocalised scripted triggers `iran_path_army` / `iran_path_tribal`, which
have no localisation key anywhere in the mod.

## What was changed

Twelve requirement blocks now wrap their flag conditions in `custom_trigger_tooltip` with an English
key, the pattern these two files already use for `iran_pahlavi_programme_tt`,
`iran_projects_ready_tt`, `iran_coup_standing_tt` and others. `custom_trigger_tooltip` is the
documented alias of `custom_override_tooltip` (`<HOI4>/documentation/triggers_documentation.md`,
"An AND trigger that has an overridden custom tooltip") and is used 13 times in these files already,
so the file keeps one mechanism rather than mixing in the newer spelling.

Nothing else in either file changed: focus ids, order, icons, coordinates, prerequisites,
`mutually_exclusive`, `allow_branch`, `cost`, `search_filters`, `ai_will_do` and every reward are
byte-identical to the baseline (asserted per focus by the new test, see below).

| Focus | Block | Before | After (tooltip key) |
| --- | --- | --- | --- |
| IR2_reject_the_agreement | available | `NOT = { has_country_flag = iran_crisis_anglo_persian_done }` | `iran_anglo_persian_crisis_open_tt` |
| IR2_accept_the_agreement | available | same flag, beside `iran_sponsor_britain_valid` | `iran_anglo_persian_crisis_open_tt` |
| IR2_reza_khan_minister | bypass | `has_country_flag = iran_coup_prevented` | `iran_cossack_refusal_tt` |
| IR2_jangali_congress | available | `has_country_flag = iran_gilan_republic` (beside `date > 1920.5.31`) | `iran_gilan_republic_proclaimed_tt` |
| IR2_nationalist_press | available | `has_country_flag = iran_nationalist_movement` | `iran_nationalist_movement_organized_tt` |
| IR2_nationalist_officers | available | `has_country_flag = iran_nationalist_movement` | `iran_nationalist_movement_organized_tt` |
| IR2_pahlavi_settlement | available | `OR = { iran_cossack_ascendant iran_reza_khan_minister }` unwrapped (the block's third line was already wrapped, which is why the first crude scan missed it) | `iran_reza_at_the_army_tt` |
| IR2_pahlavi_settlement | available | `OR = { iran_path_army = yes NOT = { iran_path_majlis = yes } }` unwrapped scripted triggers | `iran_army_decisive_voice_tt` |
| IR2_nationalist_front | available | `has_country_flag = iran_nationalist_officers OR = { iran_path_army = yes iran_path_tribal = yes }` | `iran_nationalist_front_base_tt` |
| IR2_socialist_republic | available | `has_country_flag = iran_jangali_congress` and `OR = { iran_path_majlis = yes NOT = { iran_path_court = yes } }` unwrapped (the variable check was already wrapped) | `iran_jangali_congress_held_tt`, `iran_majlis_predominance_tt` |
| IR3_mohammad_reza | available | `has_country_flag = iran_pahlavi` | `iran_pahlavi_rule_tt` |
| IR3_wartime_regency | available | `OR` of `iran_pahlavi`, `iran_qajar_restoration`, `iran_constitutional_monarchy` | `iran_monarchy_settled_tt` |
| IR3_occupation_government | available | `has_country_flag = iran_occupied` | `iran_occupied_tt` |
| IR3_resistance_council | available | `has_country_flag = iran_occupied` | `iran_occupied_tt` |

Twelve keys, twelve blocks (three blocks carry two keys because they carry two independent
requirements). This table is the round-1 state; round 2 added a thirteenth wrapper and key, so the
delivered tree carries 13 keys over 16 wrapper sites (see the correction section below).

### Localisation added

`localisation/english/iran_interwar_l_english.yml`:

```
iran_anglo_persian_crisis_open_tt: "The Anglo-Persian agreement of 1919 has been neither ratified nor rejected."
iran_cossack_refusal_tt: "The Cossack officers have refused to march on the capital."
iran_gilan_republic_proclaimed_tt: "The Gilan republic has been proclaimed in the north."
iran_nationalist_movement_organized_tt: "The nationalist movement has been organized."
iran_nationalist_front_base_tt: "The nationalist officers are organized, or the movement rests on the army or on the tribes."
iran_jangali_congress_held_tt: "The Jangali congress has met and given the left a common programme."
iran_majlis_predominance_tt: "The Majlis, rather than the court, has been the ground of government since the constitutional era."
iran_reza_at_the_army_tt: "Reza Khan commands the Cossack brigade or holds the War Ministry."
iran_army_decisive_voice_tt: "The army has the decisive voice, or the Majlis does not."
```

`localisation/english/iran_ww2_l_english.yml`:

```
iran_pahlavi_rule_tt: "The Pahlavi dynasty rules Iran."
iran_monarchy_settled_tt: "A monarchy governs Iran: the Pahlavi dynasty, a restored Qajar court or a constitutional crown."
iran_occupied_tt: "The country is under foreign occupation."
```

`iran_nationalist_front_base_tt` here read "or", justified as `flag OR (army OR tribal)`. That
justification was wrong and QA round 1 rejected it: the wrapper holds two entries, which the engine
ANDs, so the condition is `flag AND (army OR tribal)`. The shipped text states the conjunction now;
see "Correction round 2" at the end of this document.

### Semantics

Every wrapper is evaluated as an AND container, so each rewritten block keeps the exact condition it
had. The test proves this two ways: the wrapper-stripped trigger text is identical to the baseline
block, and the truth table over leaf conditions is identical for every combination. The one place
where the trigger text could not be wrapped whole (a block with a bare `NOT` inside `OR`) the `NOT`
was kept inside the wrapper rather than hoisted, so no `_NOT` tooltip key is needed.

### Scope note - scripted triggers inside the same blocks

Three blocks also carried `iran_path_army`, `iran_path_majlis` and `iran_path_tribal` in the open.
They are scripted triggers from `common/scripted_triggers/iran_continuity.txt` with no localisation
key anywhere, so they render as raw internal names exactly like the flags. Wrapping the flag and
leaving the trigger beside it raw would have left the tooltip half-written, so those conditions were
wrapped in the same block with their own keys. No trigger logic, no shared trigger and no file
outside this card's ownership was changed. If Director prefers the scripted triggers themselves to be
localised, that is a separate change in a file I do not own (`iran_continuity.txt` belongs to I7).

## Test

`.tools/tests/test_iran_focus_tooltips.py` (new, `.tools/` is gitignored: needs `git add -f` at
integration time). It reads the working tree and the pinned baseline, and prints
`577 checks, 0 failures`, `EXIT=0`. Coverage:

1. No `has_country_flag`/`has_global_flag` in any `available`/`bypass` block of either chapter is
   left outside a wrapper (52 blocks scanned in the interwar file, 31 in the ww2 file). The baseline
   is scanned with the same rule and must report the original 9 blocks / 10 occurrences and 4 blocks
   / 6 occurrences, so the check provably fails on the defective state.
2. Every `tooltip =` key used by a requirement block resolves in `localisation/english`; each of the
   twelve new keys is referenced by a block, defined exactly once, and defined in the file this card
   owns.
3. Wrapper-stripped logic identical to baseline, block by block, plus truth-table equivalence over
   leaf conditions (`IR2_socialist_republic` 16 states, `IR3_wartime_regency` 8, and so on).
4. Every non-requirement focus field byte-identical to baseline, and both focus id lists in the same
   order.
5. Encoding: loc files keep their UTF-8 BOM, LF endings and single leading space; both script files
   keep uniform CRLF, no bare LF, no raw `§`.
6. Three in-test mutant controls (unwrapped block, flattened wrapper, unknown tooltip key) must be
   rejected - they are, so the checks are not vacuous.

`python .tools/tests/test_iran_focus_tooltips.py --detail` prints each of the 577 checks;
`--dump` prints the parsed requirement blocks.

## Repository audits

- `python tools/iran_audit.py`: 328 focuses, **0 missing focus keys**, 0 unresolved sprites. One
  pre-existing finding unrelated to this card: 16 generic decision names without localisation
  (`PER_boost_stability`, `PER_core_byzantium_state`, ...) in `common/decisions`, a file this card
  does not own and did not touch.
- `python tools/iran_reference_check.py --game "<HOI4>"`: 327 event and 155 idea references,
  "Every reference resolves".
- `common/national_focus/iran_ww1.txt` was scanned read-only with the same rule: its four
  flag-bearing requirement blocks are already wrapped, and its other seven `has_country_flag`
  occurrences sit in `allow_branch`, `limit` and `ai_will_do`, which are not printed as focus
  requirements. The 1910-1918 chapter needs no change for this defect.

## Independent verification of this delivery

The edits themselves were produced in the run that hit the 80-iteration ceiling before it could hand off;
the run that produced this handoff re-verified every claim from source and by execution instead of
trusting that report. What was actually re-run:

| Check | Command / route | Result |
| --- | --- | --- |
| Shipped test | `python .tools/tests/test_iran_focus_tooltips.py` | `577 checks, 0 failures`, `EXIT=0` |
| Acceptance rule, own scanner (enclosing-block chain, independent of the test's parser) | own script over working tree and `git show ad0169dd1:` copies | interwar 63 flag occurrences in `available`/`bypass`, **0 unwrapped** (baseline 10); ww2 10 occurrences, **0 unwrapped** (baseline 6) |
| Nothing dropped or added | same scan | in-requirement flag occurrence counts identical before and after (63 / 10) |
| Tooltip keys defined once | `grep` over `localisation/english` | 12 keys, 1 definition each, each in the owned file |
| Protected fields untouched | `git diff -U0` of both focus files | 41 changed lines, all inside `available`/`bypass`; no `icon`, `ai_will_do`, `x`/`y`, `cost`, `prerequisite`, `mutually_exclusive`, `allow_branch`, `search_filters` or `completion_reward` line appears in the diff |
| Vanilla precedent for the `bypass` wrapper | `grep` over installed `common/national_focus` | 60 `custom_trigger_tooltip` uses inside `bypass` blocks (e.g. `australia_taog.txt:6361`, `austro_hungarian_releasable_shared.txt:1116`); `custom_override_tooltip` inside `bypass` appears 0 times, so the file's existing spelling is the vanilla one |
| Iran audit | `python tools/iran_audit.py` | 328 focuses, **0 missing focus keys**; the only finding is the pre-existing 16 unlocalised generic decision names, outside this card |
| Reference check | `python tools/iran_reference_check.py` | every reference resolves |

## MCP evidence

All five routes were executed against this working tree during the handoff run, after the edits existed.
No pre-edit MCP run exists: the edits predate this run (see above), so the before-state is evidenced by the
pinned-baseline scans and the baseline comparison inside the test rather than by an earlier MCP call.

- Route: `hoi4.focus_inspect`, input `{mode: national, treeId: iran_interwar, relativePath: common/national_focus/iran_interwar.txt}`
  Result: 139 focuses, 14 diagnostics (13 layout warnings plus one vanilla `continuous_restrict_freedom_desc`
  warning from `game:common/continuous_focus/generic.txt`), `validation.passed: true`, 0 blockers,
  layoutHash `8e91e790309c0326b58de2b9d8a2a8bcc0d0a76fd1f2e131baa82839b20bdb0f` — unchanged by this card.
  Resource: `hoi4-agent://workspace/endsieg/artifact/12a6e58f…/focus-inspect.bbc142b5299307a6.json`.
- Route: `hoi4.focus_inspect`, input `{mode: national, treeId: iran_ww2, relativePath: common/national_focus/iran_ww2.txt}`
  Result: 99 focuses, 18 diagnostics (layout and the same vanilla continuous-focus warning), `validation.passed: true`,
  0 blockers, layoutHash `75251a2b39aad049495bdcc9bf61f9708e1537291adba2781f5ac4c4c59ffc12` — unchanged.
  Resource: `hoi4-agent://workspace/endsieg/artifact/55cfbe1c…/focus-inspect.bbc142b5299307a6.json`.
  Both runs list `mod:localisation/english/iran_interwar_l_english.yml` / `iran_ww2_l_english.yml` in
  `filesScanned`, and neither reports a missing localisation key for any focus it owns.
- Route: `hoi4.focus_render`, inputs `{mode: national, treeId: iran_interwar, png: false}` and
  `{mode: national, treeId: iran_ww2, png: false}`
  Result: `FOCUS_RENDERED`, 12448x2092 and 14560x1860, layoutHashes as above (identical to the inspect runs,
  so the tree geometry is untouched). Resources: `…/iran_interwar.focus.html`,
  `…/iran_ww2.focus.html` (plus `.json`, `.source-map.json`, `.plan.json`, `.svg` in the same artifacts).
- Route: `hoi4.script_validate`, `{path: common/national_focus/iran_interwar.txt}`
  Result: `valid: true`, **0 findings**, 943 commands, `unresolvedCount: 0`, `roots: 240`, `unknownScopeRoots: 0`,
  `checksPerformed: syntax, command_kind, declared_scope, player_text, event_popups, known_mistakes`;
  `parametersChecked: false`, 186 argument blocks unchecked — **PARTIAL** coverage.
- Route: `hoi4.script_validate`, `{path: common/national_focus/iran_ww2.txt}`
  Result: `valid: true`, **0 findings**, 736 commands, `roots: 154`, 167 argument blocks unchecked — **PARTIAL**.
- Not run, with reasons: `hoi4.package_check` (no package manifest covers this surface; localisation coverage is
  asserted against the whole `localisation/english` tree by the test), `hoi4.source_lookup` (no symbol renamed or
  deleted; every flag and scripted trigger still exists under the same name), `hoi4.probability_inspect`
  (no `ai_will_do` value changed — asserted at field level in the diff and by the test).

## Unverified

- No Hearts of Iron IV launch, and none is claimed. Nothing here proves how the tooltip renders in game:
  whether `custom_trigger_tooltip` inside `bypass` prints the key text on the bypass line, how the engine
  colours a wrapper, or whether the tooltip reads naturally in order. That needs a live check by the user.
- `script_validate` is PARTIAL for both files (`parametersChecked: false`, 186 and 167 argument blocks unchecked),
  so it does not prove every argument of every wrapped command is legal.
- The renderer proves the trees parse and lay out; it does not render requirement tooltips.
- The `iran_path_*` scripted triggers still have no localisation key of their own; they are only never shown raw
  where this card wrapped them. Any other surface that prints them is out of scope and unchanged.

## Simplifications, omissions and blockers

- None of the acceptance criteria were dropped or reduced. No fallback mechanism was used.
- Deliberate omission: the seven unlocalised-flag tooltip warnings I6 QA reported on the Pahlavi
  agreement requirements live in `common/decisions/iran_foreign_agreements.txt`, which Director
  excluded from this card.
- No commit, no stage (`.tools/tests/test_iran_focus_tooltips.py` is gitignored and needs
  `git add -f`); Director integrates.

## Correction round 2 - QA changes requested

QA round 1 (`endsieg-qa`, run 111, artifact lens) rejected this delivery on two problems. Both are
fixed in the same six owned paths; nothing outside them was touched and the branch, baseline and
no-commit state are unchanged.

### D1 `iran-focus-raw-scripted-trigger-still-visible`

`IR2_parliamentary_republic` (`common/national_focus/iran_interwar.txt:463`) still carried its
requirement in the open:

```
before:  available = { iran_path_majlis = yes }
after:   available = { custom_trigger_tooltip = { tooltip = iran_majlis_ascendant_tt iran_path_majlis = yes } }
```

Root cause of the miss: the round-1 wrap set was built from a `has_country_flag`/`has_global_flag`
scan plus three hand-picked `iran_path_*` blocks, so the fourth such block was never inventoried.
The handoff's "0 unwrapped" and "three blocks" statements were true only inside that flag-only rule.

New key, English:

```
iran_majlis_ascendant_tt: "The Majlis has been the ground of government since the constitutional era."
```

The condition is `iran_path_majlis` on its own - the OR over the constitutional-era Majlis flags at
`common/scripted_triggers/iran_continuity.txt:17-38`. `iran_majlis_predominance_tt` was deliberately
not reused: it describes `majlis OR NOT court`, and this block tests `majlis` alone.

### D2 `iran-focus-tooltip-text-misstates-condition`

`iran_nationalist_front_base_tt` described a disjunction where the script requires a conjunction.

```
before:  "The nationalist officers are organized, or the movement rests on the army or on the tribes."
after:   "The nationalist officers are organized, and the movement rests on the army or on the tribes."
```

`IR2_nationalist_front.available` wraps two entries - `has_country_flag = iran_nationalist_officers`
and `OR = { iran_path_army = yes iran_path_tribal = yes }` - which the engine ANDs, so
`flag AND (army OR tribal)` is the condition a player has to satisfy. The earlier non-blocking note
in this document ("the wrapped condition really is flag OR (army OR tribal)") was wrong and has been
corrected above.

### D3 test scope (root cause of D1)

The shipped test stayed green at 577/0 with D1 present, because its presentation rule only covered
`has_country_flag`/`has_global_flag` and `REPAIRED_BLOCKS` omitted `IR2_parliamentary_republic`.
Round 2 adds:

- `check_scripted_trigger_names`: every trigger defined in `common/scripted_triggers/*.txt` that sits
  bare in an `available`/`bypass` block must resolve in `localisation/english` under its own name (the
  `iran_sponsor_britain_valid` pattern) or be wrapped. Baseline anchors: 7 unlocalised occurrences in
  the interwar chapter, 0 in the ww2 chapter; current: 0.
- The eight bare-but-localised trigger uses that remain (all intentional, unchanged by this card) are
  measured, not ignored: `iran_sponsor_britain_valid` x4, `iran_sponsor_germany_valid` x3,
  `iran_allied_pressure` x1, each with a written English key.
- `IR2_parliamentary_republic` added to `REPAIRED_BLOCKS`, `iran_majlis_ascendant_tt` to `NEW_KEYS`.
- A fourth mutant control: the baseline `IR2_parliamentary_republic` block is re-inserted in memory
  and the new rule must reject it (it does).

### Round-2 validation actually run

| Check | Command | Result |
| --- | --- | --- |
| Shipped test | `python .tools/tests/test_iran_focus_tooltips.py` | `590 checks, 0 failures`, `EXIT=0` |
| New rule detects the shipped defect (in-test mutant) | same run, `--detail` | `ok mutant control: a bare unlocalised scripted trigger is rejected` |
| Independent scan of the acceptance rule (own parser, working tree vs `git show ad0169dd1:`) | own script: flags plus every mod scripted trigger inside `available`/`bypass` | interwar 75 flag/trigger atoms, 0 unlocalised bare (5 bare triggers all resolve); ww2 13 atoms, 0 unlocalised bare; baseline interwar 22 bare of which 7 unlocalised, ww2 9 bare of which 0 unlocalised |
| Nothing dropped or added | same scan | atom totals identical to baseline (75 interwar, 13 ww2) |
| Keys | test + `grep localisation/english` | 13 new keys, one definition each, all in the two owned files, 16 wrapper sites |
| Protected fields | test `--detail` per-focus field comparison | every non-requirement field byte-identical to baseline on all 238 focuses; ids and order unchanged |
| Encoding | test | both loc files keep UTF-8 BOM, LF, single leading space; both scripts keep uniform CRLF |

### Round-2 MCP evidence (independent runs, this session, after the edits)

- `hoi4.focus_inspect` `{mode: national, treeId: iran_interwar, relativePath: common/national_focus/iran_interwar.txt}`
  -> 139 focuses, 14 diagnostics (13 layout + the vanilla `continuous_restrict_freedom_desc`
  warning), `validation.passed: true`, 0 blockers, layoutHash
  `8e91e790309c0326b58de2b9d8a2a8bcc0d0a76fd1f2e131baa82839b20bdb0f` (unchanged from round 1).
  Artifact `hoi4-agent://workspace/endsieg/artifact/85521e8f.../focus-inspect.1b7316e24f55ad0a.json`.
- `hoi4.focus_inspect` `{treeId: iran_ww2, relativePath: common/national_focus/iran_ww2.txt}`
  -> 99 focuses, 18 diagnostics (17 layout + same vanilla warning), passed true, 0 blockers,
  layoutHash `75251a2b39aad049495bdcc9bf61f9708e1537291adba2781f5ac4c4c59ffc12`.
  Artifact `hoi4-agent://workspace/endsieg/artifact/7c1f625e.../focus-inspect.1b7316e24f55ad0a.json`.
- `hoi4.focus_render` `{treeId: iran_interwar, png: false}` -> `FOCUS_RENDERED`, 12448x2092, layoutHash
  `8e91e790...`; `{treeId: iran_ww2, png: false}` -> 14560x1860, layoutHash `75251a2b...`. Geometry
  matches the inspect runs, so no focus moved. HTML/SVG/JSON artifacts under
  `.../iran_interwar.focus.html` and `.../iran_ww2.focus.html`.
- `hoi4.script_validate` `{path: common/national_focus/iran_interwar.txt}` -> `valid: true`, 0 findings,
  943 commands, `unresolvedCount: 0`, roots 240, `unknownScopeRoots: 0`, `parametersChecked: false`,
  187 argument blocks unchecked (**PARTIAL**; round 1 reported 186, the extra block is the new wrapper).
- `hoi4.script_validate` `{path: common/national_focus/iran_ww2.txt}` -> `valid: true`, 0 findings,
  736 commands, roots 154, 167 argument blocks unchecked - **PARTIAL**.
- `hoi4.source_lookup` `{symbol: iran_path_majlis}` -> 1 definition (`scripted_trigger`,
  `mod:common/scripted_triggers/iran_continuity.txt:17-38`), 13 references including
  `iran_interwar.txt:463` (now inside the wrapper), `:465` (`ai_will_do`, untouched) and `:525`.
- `hoi4.source_lookup` `{symbol: iran_majlis_ascendant_tt}` -> 0 definitions, 0 references. This route
  indexes script symbols, not localisation keys, so it *cannot* confirm a loc key; the key's single
  definition is asserted by the test's `english_loc_keys()` scan of `localisation/english` and by grep.
  Recorded as a tool limitation, not as evidence that the key is missing.

### Round-2 unverified

- No launch, no in-game claim. How the wrapped line renders (text, colour when unmet, order) is still
  unproven; `custom_trigger_tooltip` inside `available`/`bypass` is engine behaviour only a live check
  settles.
- `script_validate` remains PARTIAL for both files (`parametersChecked: false`).
- The `iran_path_*` triggers still have no loc key of their own; they are hidden by wrappers at the
  requirement sites this card owns and nowhere else.

### Round-2 simplifications, omissions, blockers

None. Both rejected problems are fixed at their root, the shipped test now covers the class of defect
that produced D1, and no acceptance criterion was reduced. No file outside the six reserved paths was
written; no commit, stage, push, branch change or launch.
