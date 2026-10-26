# Post-WWI programme cleanup handoff

## Disposition

Not changed: no behavior-preserving scan reduction was established within the permitted source hunks.
The parent agent's preservation requirement covers removal of externally regranted old spirits and rules out unproven permanent skip flags.
Only this handoff was created; `common/scripted_effects/Endsieg_scripted_effects.txt` remains byte-identical to the supplied baseline.
No game was launched, no commit was made, and no performance gain is claimed.

## Scope and ownership

Acted as `.claude/agents/hoi4-scripted-system-architect.md` under the bounded parent assignment.
Read `CLAUDE.md`, `docs/plans/performance/current_report.md`, the relevant scripted effects, direct callers, idea definitions, offline wiki, and installed documentation.
Authorized gameplay scope was only narrow cleanup hunks in `common/scripted_effects/Endsieg_scripted_effects.txt`.
Exact owned source hunks changed: none.
Changed functions, new helpers, changed call sites, flags, constants, event targets, and migration logic: none.
Other AI work, strain/crisis churn, ration display, diplomacy, tree maintenance, thresholds, events, AI weights, and industrial state logic were not edited.

## Inspected helper map

All helpers execute in country scope with no parameters and remove matching ideas only when present.
They are not pure terminal migrations: repeated invocation also repairs regranted ideas.

| Helper | Baseline lines | Idea checks | Unique ideas inside helper | Additional behavior retained |
|---|---|---:|---:|---|
| `EN1_R_clear_war_programmes` | 18579–18586 | 83 | 83 | Conditional owned-state industrial demobilization |
| `FR3_R_clear_war_programmes` | 18742–18843 | 98 | 98 | Two conditional reconstruction removals; conditional owned-state industrial demobilization |
| `US2_R_clear_war_programmes` | 18992–19029 | 35 | 35 | Unconditional owned-state industrial demobilization |
| `US2_R_clear_all_programmes` | 19031–19167 | 130 | 130 | Unconditional owned-state industrial demobilization; dated Theodore Roosevelt retirement |
| `JP1_R_clear_programmes` | 19822–19827 | 149 | 149 | Idea cleanup only |

Programmatic inventory found 495 checks across these helpers and 460 distinct referenced idea IDs across the group.
There are no duplicate idea removals within any individual helper.
The cross-helper overlap is not duplicate work inside a single call: USA's update helper chooses `clear_all_programmes` versus `clear_war_programmes` through `if`/`else_if`, rather than running both sequentially.
Japan has no helper literally named `clear_war_programmes`; its relevant cleanup is `JP1_R_clear_programmes`.
The Ottoman helper was outside the requested ENG/FRA/USA/JAP scope and was not changed.

## Direct callers and recurrence

`common/on_actions/endsieg_on_actions.txt:893,897,899,901` dispatches JAP, USA, FRA, and ENG update helpers in the existing daily country path.
No on_action was added or changed.

- ENG: `EN1_R_update_tree` calls cleanup after Compiegne, Central Powers victory, the 1935 cutoff, or loss of the WWI tree.
  Direct focus callers are `EN1_R_close_emergency_powers` at `common/national_focus/WWI - United Kingdom.txt:647`, `EN1_R_demobilisation` at line 1323, and `EN1_I_reconversion` at line 2124.
  These focus calls can occur before the WWI idea-granting era is over, so the first cleanup call is not an authoritative lifetime completion point.
- FRA: `FR3_R_update_tree` has the same terminal-condition shape; `FR3_R_demobilisation` at `common/national_focus/WWI - France.txt:753` is a direct caller.
  `FR3_R_reconstruction_spirit` and `FR3_WW1_reconstruction_spirit` remain removable only when their existing date/tree/continental-war predicate becomes true; a marker set during an earlier cleanup could suppress this later change.
- USA: `US2_R_update_tree:18987–18988` calls all-programme cleanup after tree exit/cutoff, otherwise war-programme cleanup after the settlement flags.
  `events/WWI - USA.txt:696`, event `ww1_usa.217`, directly calls war-programme cleanup while `US2_R_no_great_war` holds.
  That predicate is current war absence against specified major tags, not proof that future programme grants are impossible (`common/scripted_triggers/endsieg_scripted_triggers.txt:2724–2734`).
- JAP: `JP1_R_update_tree:19802–19803` calls cleanup during tree transition and thereafter outside the WWI tree.
  Pre-1936 tree exit does not prove all pending or externally initiated grants are impossible; preserving later regrant repair prevents treating it as an authoritative lifetime boundary.

## Why no done flag was shipped

All 460 referenced idea IDs resolve in mod/installed idea definitions, and the inspected definitions contain no `on_add` or `on_remove` hooks.
This makes repeated removal side-effect-free for those ideas, but does not make skipping future removal equivalent.
Source grants exist in focus rewards, events, repeatable decisions, and scripted effects outside the allowed edit hunks.
Existing project-active flags serialize decisions; they do not authoritatively record whether all cleanup-list ideas are absent, and their writers do not invalidate any cleanup-complete marker.

Concrete regrant counterexamples:

- `common/decisions/WWI_home_front_decisions.txt:1002`, repeatable `EN1_R_decision_irish_guarantees`, can grant `EN1_R_irish_compact` while the British WWI tree remains active, including after an earlier peace cleanup.
- The same file at line 1027, repeatable `US2_R_decision_veteran_care`, can grant `US2_R_veterans_spirit` before 1936 while the USA WWI tree remains active; the decision does not require the settlement flags to be absent.
  Existing recurring war-programme cleanup removes that regrant, whereas a permanent done flag would leave it active.
- Line 1013 grants `FR3_R_reconstruction_spirit` again in peacetime; its cleanup is intentionally conditional and must continue responding when war, date, or tree conditions later change.
- Events also grant listed spirits, including British Irish/cabinet/service programmes, French government/liaison programmes, Japanese cabinet programmes, and American event spirits.
  Historical date gates alone do not establish the stronger requested invariant that externally regranted spirits will still be removed.

An authoritative invalidation scheme would require covering all relevant idea writers outside this file, as well as defining the treatment of external grants.
That exceeds the permitted source scope and would change the stated repair contract unless deliberately designed and accepted.
No existing marker was established as safe for eliminating all idea scans.
No duplicate identical checks existed inside an individual cleanup call to remove as an alternative safe improvement.

## Before/after semantics

Identical: every invocation performs its existing per-idea presence checks and removals, including regrant repair.
Identical: FRA's two reconstruction predicates remain reevaluated on every call.
Identical: all owned-state reconciliation remains outside any new guard because there is no new guard.
Newly conquered or otherwise transferred states carrying `endsieg_ww1_industry_active` therefore retain their existing cleanup route.
Identical: all thresholds, dates, tree maintenance, diplomacy, events, probabilities, industrial state effects, and USA character-retirement behavior.

## Validation and evidence

- Programmatic per-function extraction and duplicate inventory: counts shown above; no duplicate IDs within any of the five functions.
- Idea-definition resolution across mod and installed vanilla: 460 of 460 IDs resolved, zero missing, zero inspected `on_add`/`on_remove` hooks.
- Direct-caller search across repository `.txt` files and focused source reads: callers listed above; USA alternatives are mutually exclusive within its update call.
- Baseline comparison: current source bytes equal `.tmp/performance_implementation/before/common/scripted_effects/Endsieg_scripted_effects.txt`.
- Source SHA-256: `4f3328266da1735e79537e9eb63b15e4d6989500d2b16d514128bcf2bc15e570`.
- Offline reference: `paradox_wiki/Idea modding - Hearts of Iron 4 Wiki.md:220–235` explains addition/removal hooks and cancellation effects.
- Installed reference: `documentation/effects_documentation.md:6065–6072` documents country-scoped idea removal; lines 6730–6737 document country-scoped flags.
- The inherited MCP blocker is unchanged: adapter targets 1.19.2 while installed game is 1.19.3, and the parent review records a rejected reference route.
  No retry was made against the already-known unavailable capability; no MCP, render, or engine-validation claim is made.
- No gameplay patch was produced, so no new parser behavior requires validation for this handoff.
  No launch, live test, throughput benchmark, or external-grant engine scenario was run; parent owns final validation.

## Follow-up disposition

Permanent skip-marker proposal: rejected for this bounded task because regrant preservation is not established.
Broad writer invalidation: not implemented; requires a separately authorized cross-file design and explicit external-grant contract.
Safe local cleanup reduction: not identified; source intentionally left unchanged rather than shipping semantic drift.
