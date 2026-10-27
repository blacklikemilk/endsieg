# I6 handoff: Iran's Crown/Majlis transitions, Pahlavi agreements, decree veto and party id

Task t_9c95f34d (I6), era 1919-1945 Pahlavi/constitutional transition, branch TeknoDev-Branch, base commit `f6d12527cc8a3ed3cda6e533528f46bbba4d6e17`.
Source: the independently accepted I1 audit of the landed I3 Crown/Majlis integration (parent t_23cbbee2), defects D1-D4.
The Developer made no commit; Director integration follows independent QA.
No branch change, launch, artwork, focus-tree or layout change occurred.

## Changed files

| File | Change |
| --- | --- |
| `common/decisions/iran_foreign_agreements.txt` | The `available` OR of all four agreements gains the `NOT = { has_power_balance = ... }` branch (lines 27, 66, 108, 156); the four mis-indented OR blocks are re-indented to the file's own tab depth; the overview comment explains the gate |
| `common/scripted_effects/PER_bop_effects.txt` | New `PER_bop_open_regime` creates the balance at `iran_story.bop_centre` when it is absent; the autocracy branch of `PER_bop_sync` and the `PER_bop_resurgence_check` test both gain the successor-regime guard (correction round 1); comments explain the ordering and the dynasty/autocracy distinction |
| `common/scripted_effects/iran_regime_shift.txt` | All five shifts call `PER_bop_open_regime` before their settlement; `iran_shift_to_socialist` installs `ruling_party = communism`; header comment records the ordering and why the constitutional shift keeps `PER_pahlavi_dynasty` |
| `common/script_constants/iran_campaign.txt` | `bop_centre = 0` and a note that the decree veto's length is the file macro `@decree_treaty_days` |
| `events/iran_negotiations.txt` | `@decree_treaty_days = 365`; the four decree options set a timed flag instead of a permanent one |
| `common/decisions/PER_crown_and_majlis.txt` | Two comment lines at the Budget Vote `available` block recording that the veto is timed |
| `localisation/english/iran_crown_majlis_l_english.yml` | `PER_bop_budget_vote_desc` and `PER_bop_decree_treaty_tt` now describe the decree veto as lasting a year |
| `.tools/tests/test_iran_bop_transitions.py` | New durable source test, 25 checks, with pinned pre-repair mutants for all four defects and an in-memory guard mutant for the correction |
| `docs/plans/iran_1910_1945/subagent_handoffs/bop_transitions.md` | This handoff |

`git status --porcelain` at the start of the run showed a clean tree apart from `?? docs/plans/campaign/`.
During the run another session's Spain work appeared as modified (`common/decisions/spain_cortes.txt`, `common/scripted_effects/spain_campaign_effects.txt`, `spain_cortes_bills.txt`, `spain_cortes_effects.txt`, `spain_cortes_hemicycle.txt` and `localisation/english/spain_campaign_l_english.yml`); it is disjoint from every path above, was read only, and is not part of this card.
`git diff --stat` on this card's tracked paths reports 7 files, 66 insertions and 15 deletions: the six scripts and the one localisation file.
The test is untracked because `.gitignore:5` ignores `.tools/` (verified with `git check-ignore -v`), and this handoff is a new untracked file.

## D1 - the four agreements under Pahlavi rule

Before, every agreement carried the same gate (indentation as shipped):

```
		available = {
			has_political_power > 99
			NOT = { has_country_flag = iran_agreement_british_loan }
					OR = {
				has_country_flag = PER_bop_crown_side
				power_balance_value = { id = PER_crown_and_majlis value > -0.10 }
			}
}
```

After:

```
		available = {
			has_political_power > 99
			NOT = { has_country_flag = iran_agreement_british_loan }
			OR = {
				NOT = { has_power_balance = { id = PER_crown_and_majlis } }
				has_country_flag = PER_bop_crown_side
				power_balance_value = { id = PER_crown_and_majlis value > -0.10 }
			}
		}
```

Why this is the repair: `PER_bop_sync` removes the balance and clears `PER_bop_crown_side` and `PER_bop_majlis_side` whenever the Pahlavi settlement applies (`common/scripted_effects/PER_bop_effects.txt:127-133`), and the balance's range `on_activate`/`on_deactivate` blocks are the only writers of those flags (`common/bop/PER.txt:42-47, 99-104`). Both halves of the old OR were therefore false for the whole 1925-1941 Pahlavi era, and the four decisions were greyed out for good.
`NOT = { has_power_balance = { id = PER_crown_and_majlis } }` is the existing project reading of "the chamber cannot block": `common/decisions/iran_coup_1921.txt:69-72` and the renegotiation decisions in `common/decisions/iran_negotiations.txt:24-27` use it, and `events/iran_negotiations.txt:30` uses the equivalent `OR = { NOT has_power_balance … }` to offer the accept option to a Court that rules alone.

What the test proves for each of the four decisions, against four declared country states:

| State | Balance | Side flag | Availability |
| --- | --- | --- | --- |
| `pahlavi_rule_alone` | absent | none | available (was unavailable) |
| `crown_ascendant` | -0.20 | crown | available (unchanged) |
| `majlis_ascendant` | +0.30 | majlis | available (unchanged) |
| `crown_dominant_without_flag` | -0.50 | none | unavailable (unchanged, the branch did not widen) |

Nothing else in the file moved: the test compares every decision id and every non-`available` field of all 10 decisions with the pinned base revision.
Costs (100/100/75/100), `fire_only_once`, the complete effects, the AI weights (2/2/3/1) and the icons are untouched.
The `date < 1936.1.1` visibility of the loan and the railway concession is design, not a defect: those two agreements belong to the 1910-35 Great Game, so a 1936 start does not show them, and the fix is about the availability gate the audit named.

## D2 - a regime shift out of Pahlavi

Before, every shift ran its settlement push and then the sync:

```
	set_politics = { ruling_party = neutrality elections_allowed = yes }
	add_stability = 0.10
	PER_bop_settle_constitution = yes
	PER_bop_sync = yes
```

Every push is guarded by `has_power_balance`, so under Pahlavi rule the settlement did nothing, and `PER_bop_sync` then decided the balance from the era table: `iran_story.bop_opening_interwar = -0.15` for any start from 1919 onwards, unless the autocracy branch applied and removed it instead.
That branch read "Pahlavi rule" as `OR = { iran_pahlavi, PER_pahlavi_dynasty }`. Four shifts clear `PER_pahlavi_dynasty` on their way out, so those were rebuilt at -0.15: a republic or a socialist state appeared in `PER_bop_crown_ascendant` (-0.40 to -0.10) with `PER_bop_crown_side` set by that range's `on_activate`.
`iran_shift_to_constitutional` does not clear the dynasty flag - it keeps the Shah and binds him - so the autocracy branch applied to it as well: the balance it had just been given was removed, `iran_pahlavi_autocracy` was re-added, and the settlement was a silent no-op that left no balance at all.
The I1 audit described this path as "-0.15 in `PER_bop_crown_ascendant`"; that figure belongs to the four shifts that clear the dynasty flag, not to the constitutional one, and correction round 1 below records the difference.

After:

```
	set_politics = { ruling_party = neutrality elections_allowed = yes }
	add_stability = 0.10
	PER_bop_open_regime = yes
	PER_bop_settle_constitution = yes
	PER_bop_sync = yes
```

`PER_bop_open_regime` creates the balance at the constitutional centre when it is absent and does nothing when one already exists:

```
PER_bop_open_regime = {
	hidden_effect = {
		if = {
			limit = {
				iran_campaign_country = yes
				has_country_flag = iran_campaign_active
				has_dlc = "Arms Against Tyranny"
				NOT = { has_power_balance = { id = PER_crown_and_majlis } }
			}
			set_power_balance = {
				id = PER_crown_and_majlis
				left_side = PER_bop_crown
				right_side = PER_bop_majlis
				set_value = constant:iran_story.bop_centre
			}
		}
	}
}
```

Why the centre and not simply "sync first": the era opening value describes the autocracy the shift is leaving. A 1936 constitutional monarchy starting at -0.15 and pulling to the centre would land on 0 only because `PER_bop_pull_to_centre` resets anything inside ±0.25, while a republic (+0.20) or a socialist state (+0.20) starting from -0.15 would land at +0.05, inside the settlement band and with no Majlis-side flag. Opening at the centre - the 1906 constitutional baseline every one of these regimes claims - and then applying each settlement's own push gives every shift its own half with the push magnitudes unchanged:

| Shift | Opening | Settlement push | Result | Range |
| --- | --- | --- | --- | --- |
| `iran_shift_to_qajar` | 0 | crown -0.20 | -0.20 | `PER_bop_crown_ascendant`, crown side |
| `iran_shift_to_republic` | 0 | majlis +0.20 | +0.20 | `PER_bop_majlis_ascendant`, majlis side |
| `iran_shift_to_constitutional` | 0 | pull to centre | 0 | `PER_bop_constitutional_settlement`, no side |
| `iran_shift_to_socialist` | 0 | majlis +0.20 | +0.20 | `PER_bop_majlis_ascendant`, majlis side |
| `iran_shift_to_nationalist` | 0 | crown -0.20 | -0.20 | `PER_bop_crown_ascendant`, crown side |

The 1919-35 path is unchanged by construction: there the balance already exists, so `PER_bop_open_regime` is a no-op and the settlement pushes the live value exactly as before.
`PER_bop_sync` still runs last and still removes `iran_pahlavi_autocracy` on the non-autocracy branch; after correction round 1 its autocracy branch also requires that no successor regime has been proclaimed, which is what lets the constitutional row above survive the sync.
The test reads the push values from `@bop_crown`/`@bop_majlis` in `PER_bop_effects.txt`, the pull threshold from `PER_bop_pull_to_centre`'s own comparisons, the ranges and their side flags from `common/bop/PER.txt`, and the centre from the constants file, so a later retune of any of them is followed rather than contradicted.

### Correction round 1 (QA rejection `iran-bop-constitutional-shift-sync-removes-balance`)

QA round 1 found that `iran_shift_to_constitutional` was the only shift that did not clear `PER_pahlavi_dynasty`, so `PER_bop_sync` classified the resulting country as the autocracy, removed the balance `PER_bop_open_regime` had just created, cleared the side flags and re-added `iran_pahlavi_autocracy`. The settlement was therefore a no-op and the country ended with no balance at all. The durable test did not model `PER_bop_sync` at all, so it stayed green.

The repair is in the balance layer's regime test rather than in the shift. The four shifts that depose the dynasty are the ones that should clear the dynasty flag; `iran_shift_to_constitutional` keeps the Shah and binds him, which is why it has always left the flag alone - `PER_constituent_assembly` reads it (`common/national_focus/_shared_WW1_persia.txt:660`) and the focus is localised as "The Pahlavi Crown". The defect was the sync's equation of dynasty with autocracy, so both regime tests now exclude a proclaimed successor regime:

```
					OR = { has_country_flag = iran_pahlavi has_country_flag = PER_pahlavi_dynasty }
					NOT = { has_country_flag = PER_majlis_resurgence }
					NOT = {
						OR = {
							has_country_flag = iran_qajar_restoration
							has_country_flag = iran_republic
							has_country_flag = iran_constitutional_monarchy
							has_country_flag = iran_socialist
							has_country_flag = iran_nationalist_front
						}
					}
```

`PER_bop_resurgence_check` gets the same guard for the same reason: its `iran_campaign.77` report opens "The Shah has gone", which is false for a country that settled a constitutional monarchy while keeping him, and the flag is the only thing that let it fire.
Files touched by the correction: `common/scripted_effects/PER_bop_effects.txt` (two limits plus comments), `common/scripted_effects/iran_regime_shift.txt` (header comment only, no effect body) and `.tools/tests/test_iran_bop_transitions.py`.
No shift body, no opening value, no settlement push, no range, no cost and no flag clearing changed in this round.

| Shift, both start states | Before: value after `PER_bop_sync` | After |
| --- | --- | --- |
| `iran_shift_to_constitutional` (1936-41 Pahlavi start) | no balance, `iran_pahlavi_autocracy` re-added | 0, `PER_bop_constitutional_settlement`, no side flag, no autocracy |
| `iran_shift_to_constitutional` (pre-1925 start played forward) | no balance, `iran_pahlavi_autocracy` re-added | 0, `PER_bop_constitutional_settlement`, no side flag, no autocracy |
| `iran_shift_to_qajar` | -0.20 crown side (correct by accident) | -0.20 crown side |
| `iran_shift_to_republic` | -0.15 crown side (wrong half) | +0.20 majlis side |
| `iran_shift_to_socialist` | -0.15 crown side (wrong half) | +0.20 majlis side |
| `iran_shift_to_nationalist` | -0.15 crown side (correct half, wrong value) | -0.20 crown side |

The test grew from 18 to 25 checks: a `D2-sync` group that rebuilds the flag state each shift leaves, evaluates the parsed `PER_bop_sync` limit against it and asserts the resulting range, side flag and autocracy idea from both start states; a `resurgence` set; and `D2-sync-mutant` / `D2-settlement-mutant` controls against the pinned baseline. Mutating the shipped source in memory - deleting the guard from `PER_bop_sync` only - reproduces exactly the QA finding for both start states, and deleting the resurgence guard reproduces the false abdication report; neither probe writes to the repository.

Before-column provenance: the two constitutional rows and the qajar row were measured on the round-1 delivered source, where the shifts already opened the balance and only the sync was unguarded. The republic, socialist and nationalist rows carry the pinned pre-I6 values, which the `D2-settlement-mutant` baseline reproduces; on the round-1 source a republic and a socialist state already settled in `PER_bop_majlis_ascendant` at `+0.20`, so `-0.15 crown side` is not a round-1 measurement.

## D3 - the decree veto expires

Before, four negotiation options set a permanent flag (`events/iran_negotiations.txt`, options `.c` of `iran_n.1`, `iran_n.4`, `iran_n.7`, `iran_n.10`):

```
		set_country_flag = iran_decree_treaty
```

and `PER_bop_budget_vote` refuses to complete while it is set (`common/decisions/PER_crown_and_majlis.txt:109-113`). Nothing cleared it anywhere in the mod, so from the first decree onwards the yearly mission could never be completed again: it activated, could not complete, and timed out into `iran_campaign.78` every cycle.

After, with the duration next to the file's other day macros:

```
@decree_treaty_days = 365

		set_country_flag = { flag = iran_decree_treaty value = 1 days = @decree_treaty_days }
```

365 days is one of the mission's own cycles short: the Budget Vote runs 150 days and then waits `@budget_cooldown_days = 365`, so a decree can cost at most one vote and the loop always returns. The test enforces `days > 0` and `days <= days_mission_timeout + @budget_cooldown_days`, so a later edit cannot quietly make the flag permanent again or longer than one cycle.
The veto itself is unchanged as a design: while it lasts the mission's `available` fails, and a mission that was already running lapses into the existing constitutional-crisis event `iran_campaign.78`. That is the mission's own failure state and its three options still move the balance.
`set_country_flag = { flag = … days = … }` is documented in `paradox_wiki/Effects - Hearts of Iron 4 Wiki.md:897` (`days` optional, `value` optional) with the same shape at line 921-925, and the mod already uses timed flags in this subsystem (`common/decisions/PER_crown_and_majlis.txt:117,123` for the budget cooldown, `common/scripted_effects/iran_negotiations.txt:22,71,…` for the negotiation and binding flags). The four `ai_chance` modifiers that read the flag (0.5 and 2 factors in the vote events) now follow a flag that expires, which matches the wording the veto already had.

Localisation: `PER_bop_decree_treaty_tt` already said "No treaty has **lately** been signed over the Majlis's head", which was false while the flag was permanent. It now reads "No treaty has been signed over the Majlis's head in the past year", and `PER_bop_budget_vote_desc` names the decree among the conditions the chamber weighs.

## D4 - the socialist shift installs a party that exists

Before: `set_politics = { ruling_party = communist elections_allowed = no }`.
`common/ideologies/00_ideologies.txt` declares `democratic` (3), `communism` (70), `fascism` (135) and `neutrality` (195). `communist` is not an id, so no party could be installed and the government never changed.
After: `set_politics = { ruling_party = communism elections_allowed = no }` (line 70). Nothing else in that shift moved: flags, authority, stability, settlement and the layout-dirty call are byte-identical to the base revision, which the test checks.
The nationalist shift's `neutrality` + elections combination is left as designed and is not part of this card.

## Durable test

`.tools/tests/test_iran_bop_transitions.py` parses the eight shipped files listed in its docstring and checks:

1. `D1-agreements`: the three-branch gate and the four declared country states above, plus a full comparison of every decision id and every non-`available` field against the pinned base revision.
2. `D2-settlement`: that each shift opens the balance before its settlement, that sync follows the settlement, and the settlement value, range and side flag for every shift.
3. `D2-sync`: the parsed regime test of `PER_bop_sync` and `PER_bop_resurgence_check` - that it still recognises Pahlavi rule, that it excludes every successor regime flag, that it still removes the balance and re-adds `iran_pahlavi_autocracy` under the autocracy, and that each shift keeps its balance afterwards. It rebuilds the flag state each shift leaves behind from `set_country_flag`/`clr_country_flag` (expanding `iran_clear_regime_flags`) and evaluates the parsed limit against it from two start states: the 1936-41 Pahlavi start from `iran_initialize_campaign`, and a pre-1925 start played forward through the `PER_pahlavi_dynasty` focus.
4. `D3-decree`: four timed setters, a positive duration through the macro, no permanent setter anywhere in `events/`, `common/decisions/`, `common/scripted_effects/` or `common/national_focus/`, the Budget Vote still reading the flag, and the duration bounded by one mission cycle.
5. `D4-ideology`: the party id, that `communism` exists, and that `communist` does not.
6. `preserved`: every pre-existing `PER_bop_*` effect and every shift is unchanged apart from the one opening call, the party id and the successor-regime guard in the two regime tests (stripping that guard must leave each effect identical to the baseline).

Every defect group also runs the same checker against the pinned base revision `f6d12527cc8a3ed3cda6e533528f46bbba4d6e17` and must reject it, which is the mutant control.
The pre-repair run reproduces every audited failure from source:

- `iran_accept_british_loan`, `iran_accept_northern_railway`, `iran_accept_military_mission` and `iran_accept_customs_officers` are all unavailable under `pahlavi_rule_alone`;
- with no opening call the settlement pushes cannot reach a balance, so the era opening alone places a shift: `iran_shift_to_republic` and `iran_shift_to_socialist` land at -0.15 in `PER_bop_crown_ascendant` with `PER_bop_crown_side`;
- after `PER_bop_sync`, `iran_shift_to_constitutional` from either start state is left with **no balance at all** and `iran_pahlavi_autocracy` re-added, and the republic and socialist shifts are left at -0.15 on the Crown side;
- the pre-repair `PER_bop_resurgence_check` fires for all five proclaimed successor regimes, including the constitutional monarchy that kept the Shah;
- all four decree options still set `iran_decree_treaty` permanently;
- `iran_shift_to_socialist` installs `communist`, which is not an ideology id.

A stronger control than the pinned revision was also run: deleting the shipped guard from `PER_bop_sync` in memory (no write to the repository) makes `D2-sync` fail for the constitutional shift from both start states with exactly the QA finding, and deleting the resurgence guard makes that check fail with the false abdication report.

Actual output, from the repository root:

```
python .tools/tests/test_iran_bop_transitions.py
note  the decree veto is read by the yearly Budget Vote mission; the engine expiry of a timed country flag is not proven here
note  no game was launched: availability, the balance ranges and the party change are source facts under the declared country states, not engine observations
25 checks, 0 failures
EXIT=0
```

`--detail` prints each check; `--dump` prints the parsed ranges, push values, pull threshold, opening value, macro, call order per shift and the post-sync value per shift.
`.tools/` is ignored by the HOI4 Mod Setup rules, so Director integration needs the same explicit `git add -f` path the I5 test used; the ignore file was not changed.

## Repository audits re-run

```
python tools/iran_audit.py --game "<HOI4 install>"
```
73 Iran-owned script files, 328 focuses, 171 events, 112 decisions, 197985 localisation keys, 0 missing focus keys, 32412 sprites with 0 unresolved references: "Clean: no problems found".
(Re-run after correction round 1; the localisation-key total moved from 197971 because other sessions' files changed in the same working tree, not because of this card.)

```
python tools/iran_reference_check.py --game "<HOI4 install>"
```
49 files, 327 event references and 155 idea references against 9357 known events and 7891 known ideas: "Every reference resolves".
That covers the new `PER_bop_open_regime` call sites and the regime-guard edits, which add no new symbol.

## MCP evidence

All routes ran with `workspaceId: "current"`.

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.script_validate` | path `common/decisions/iran_foreign_agreements.txt`, before the edit | `valid: true`, 158 commands, 7 findings (all pre-existing `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` at lines 20, 22, 58, 60, 101, 148, 204), `unresolvedCount: 0`, 46 unchecked argument blocks |
| `hoi4.script_validate` | same path, after the edit | `valid: true`, 166 commands, the same 7 warnings at lines 25, 28, 64, 67, 109, 157, 213, `unresolvedCount: 0`, 50 unchecked argument blocks. No new finding; the `NOT = { has_power_balance = … }` branch validates |
| `hoi4.script_validate` | path `common/scripted_effects/iran_regime_shift.txt`, before | `SCRIPT_CHECK_PARTIAL` (scripted effects have no declared scope: 6 unknown scope roots), 0 findings, 55 commands |
| `hoi4.script_validate` | same path, after | `SCRIPT_CHECK_PARTIAL`, 0 findings, 60 commands, 8 unchecked argument blocks, `unresolvedCount: 0` |
| `hoi4.script_validate` | path `common/scripted_effects/PER_bop_effects.txt`, before | `SCRIPT_CHECK_PARTIAL`, 0 findings, 106 commands, 25 unchecked blocks |
| `hoi4.script_validate` | same path, after | `SCRIPT_CHECK_PARTIAL`, 0 findings, 114 commands, 27 unchecked blocks, `unresolvedCount: 0` |
| `hoi4.script_validate` | path `events/iran_negotiations.txt`, after | `SCRIPT_CHECKED`, `valid: true`, 206 commands, 0 findings, 85 roots, `unresolvedCount: 0` |
| `hoi4.script_validate` | path `common/decisions/PER_crown_and_majlis.txt`, after | `SCRIPT_CHECKED`, `valid: true`, 45 commands, 0 findings, `unresolvedCount: 0` |
| `hoi4.script_validate` | path `common/script_constants/iran_campaign.txt` | family `unsupported`: 0 commands, `SCRIPT_CHECK_PARTIAL`. The same limitation I1 recorded for the balance file; the constants are covered by the test instead |
| `hoi4.script_validate` | path `localisation/english/iran_crown_majlis_l_english.yml` | family `unsupported`, `valid: false` on four `SOURCE_STRING_TOO_LONG` findings at lines 3, 25, 29, 32. The file is localisation, not script; three of those values were already longer than 255 characters before this card, and the fourth (line 25) is now 279 characters against 317 in the first draft. Recorded, not silently accepted |
| `hoi4.source_lookup` | symbol `iran_shift_to_socialist`, before | 1 definition at `iran_regime_shift.txt:57-68` with `ruling_party = communist`; 1 reference from `iran_political_question_socialist` |
| `hoi4.source_lookup` | symbol `PER_bop_open_regime`, after | 1 definition at `PER_bop_effects.txt:205-222`; 5 references, one from each shift at lines 31, 46, 59, 73, 86 of `iran_regime_shift.txt` |
| `hoi4.decision_inspect` | `mode: inventory`, before | 4346 decisions, 1366 categories, 0 unresolved definitions, reportHash `2f736d446616fd3b0cddc0c5…` |
| `hoi4.decision_inspect` | `mode: inventory`, after | 4346 decisions, 1366 categories, 0 unresolved definitions, reportHash `8d401f74389b3de1832c90ea…` |
| `hoi4.decision_inspect` | `mode: inspect`, id `iran_accept_british_loan`, scenario `pahlavi_1937` (actor PER, date 1937.1.1, flags `iran_campaign_active`, `iran_pahlavi`) | **failed once**: `PROBABILITY_GAME_VERSION_UNSUPPORTED`, adapter target `Operation Postern 1.19.2.0 (d245)`, observed `1.19.3.0.c01a (5632)`. One corrected retry as `inventory` succeeded; inspect mode is unavailable on this install, which is the limitation I1 recorded |
| `hoi4.event_inspect` | `mode: lint`, selector file `events/iran_negotiations.txt`, before | `EVENT_INSPECTED_PARTIAL`, 9314 events, 14567 options, 2414 diagnostics, 0 blocking, 4797 unresolved nodes, graphHash `6495d93c…` |
| `hoi4.event_inspect` | `mode: lint`, same file, after | identical counts, 0 blocking, graphHash `59cc325d…` |
| `hoi4.event_inspect` | `mode: trace`, selector event `iran_n.1`, downstream, after | `EVENT_INSPECTED_PARTIAL`, same counts, 0 blocking, same graphHash `59cc325d…` |
| `hoi4.reference_search` | `set_country_flag days timed flag`, limit 4 | first hit `Effects - Hearts of Iron 4 Wiki.md:897` (the `flag`/`days`/`value` argument table) with its example at 921-925; `coverage.game_doc` and `coverage.wiki` included, `script_doc` unavailable |

### Correction round 1 routes (re-run after the fix)

| Route | Input | Result |
| --- | --- | --- |
| `hoi4.script_validate` | path `common/scripted_effects/PER_bop_effects.txt`, after the correction | `SCRIPT_CHECK_PARTIAL` (scripted effects family: 16 unknown scope roots, `parametersChecked: false`, 27 unchecked argument blocks), **0 findings**, `unresolvedCount: 0`, 128 commands, docs revision `9227e238…` |
| `hoi4.script_validate` | path `common/scripted_effects/iran_regime_shift.txt`, after the correction | `SCRIPT_CHECK_PARTIAL` (6 unknown scope roots), 0 findings, `unresolvedCount: 0`, 60 commands - the comment-only edit changed no count |
| `hoi4.source_lookup` | symbol `PER_bop_sync`, after the correction | 1 definition at `PER_bop_effects.txt:119-190` whose returned source text contains the successor-regime guard; 13 references: `iran_campaign_tick:204` (the daily tick), the six `iran_settle_*` (`iran_campaign.txt:267,282,300,317,333,349`), the five `iran_shift_to_*` (`iran_regime_shift.txt:37,52,65,79,92`) and `iran_campaign.77` (`events/iran_campaign.txt:780`) |
| `hoi4.source_lookup` | symbol `PER_bop_resurgence_check`, after the correction | 1 definition at `PER_bop_effects.txt:195-223` with the guard; 1 reference, `iran_campaign_tick:203` |
| `hoi4.decision_inspect` | `mode: inventory`, after the correction | 4346 decisions, 1366 categories, 0 unresolved definitions, `reportHash d03c096991e9264a…`, artifact `decision-d03c096991e9264a4b863c0d.json` |
| `hoi4.decision_inspect` | `mode: inspect`, id `PER_bop_budget_vote`, scenario `pahlavi_1938` (actor PER, date 1938.1.1) | **failed once**: `PROBABILITY_GAME_VERSION_UNSUPPORTED` - adapter target `Operation Postern 1.19.2.0 (d245)`, observed `Operation Postern v1.19.3.0.c01a (5632)`. The corrected retry is the `inventory` row above; inspect mode stays unavailable on this install |
| `hoi4.event_inspect` | `mode: lint`, selector file `events/iran_negotiations.txt`, after the correction | `EVENT_INSPECTED_PARTIAL`, 9315 events, 14568 options, 2414 diagnostics, **0 blocking**, graphHash `118bc399…` - unchanged counts, no regression from the earlier round |

Resources: decision inventory after `hoi4-agent://workspace/endsieg/artifact/9d80fee20946fc279f507cd3cb1e5156d4c13d321470b6989615360bc60b2f7f/260bde6fce54923590a7b55d15f3e591134f25c92a08a30654686041ee4be7bb/decision-8d401f74389b3de1832c90ea.json`; event lint after `hoi4-agent://workspace/endsieg/artifact/91cc9c910b19dd9fc1773d61414ee670601aad35e7218675e2292abbc9ec590d/26ff474fd5f118201cf81d69ecb32271bbc8be83f233996cb458b97dc2b11341/event-lint-f5af5aeafa90.json`; event trace `hoi4-agent://workspace/endsieg/artifact/83a76fd7d2a2e226f582b9509846455ef5a8e7a29ac1bbee95b24a854c726afb/baef3482a56a4424b9479c6fd7554a598ea7734f4e847ea0f89934394e5ba6ca/event-trace-f5af5aeafa90.json`; correction-round inventory `hoi4-agent://workspace/endsieg/artifact/b96843579f90b030abd8243ce1fb240b85b524227dfa547ee3db1be9a0d2a589/359177b081780a120e3d6b03dd4512038e327f14146d127b1625dd2db5a62488/decision-d03c096991e9264a4b863c0d.json`; correction-round event lint `hoi4-agent://workspace/endsieg/artifact/0e1114c9405a09448f2ec8c8b372ffc63ba1e1343d703b7a8ff402899c423634/64055d75c6ef629552cb51c9d7232c09030dbcb9deca3b498506b416c41af6e0/event-lint-79aaa0fe700c.json`.

Coverage limits of that evidence: `script_validate` reports `parametersChecked: false` and leaves 8 to 58 argument blocks unchecked per file, so it does not resolve `set_power_balance`, `set_country_flag` or `power_balance_value` arguments; those are covered by the wiki tables, the vanilla and in-repo precedents and the durable test. No route models era transitions, a decision interface or the engine expiry of a timed flag.

## Known residuals, not repaired here

1. **Documentation is now stale in two read-only files.** `docs/systems/iran_negotiations.md:77` still lists `iran_decree_treaty` as "permanent", `:89` still calls the budget-vote read a hook for "a later pass", and `docs/systems/crown_and_majlis.md:34` describes the Budget Vote's conditions without the decree. They were outside this card's ownership; Director owns the docs pass.
2. **D5 (doc drift), D6 (`PER_bop_settled`/`PER_constitution_ratified` written and never read), D7 (no Arms Against Tyranny fallback) and D8 (Graveyard of Empires routing hides the 1936 political-question decisions)** are audit findings outside this card's required outcomes and were not touched.
3. **A one-day window at the very start of a campaign.** Before the first `on_daily_PER` tick creates the balance, `NOT = { has_power_balance = … }` is true, so an agreement could read as available on day one. It costs 100 political power that no start has, and the coup decisions and negotiation options carry the same window by design.
4. **The Crown-alone surcharge still reads the side flag.** The `if = { limit = { has_country_flag = PER_bop_crown_side } add_stability = -0.05 subtract_from_variable = { iran_sovereignty = 2 } }` block inside each agreement does not fire under Pahlavi rule, where no balance exists to set the flag. That is the documented behaviour of every balance push under the Pahlavi settlement (`docs/systems/crown_and_majlis.md:29`), and changing it would alter the agreements' cost, which this card was told to preserve.
5. **Seven pre-existing `SCRIPT_FLAG_TOOLTIP_UNLOCALISED` warnings** on the agreement decisions: `PER_bop_crown_side`, `iran_agreement_british_loan`, `iran_agreement_northern_railway` and `iran_customs_reformed` have no localisation keys, so those requirement lines render raw flag names. Untouched by this card; a later pass can wrap them in `hidden_trigger` with `custom_trigger_tooltip`.
6. **Three localisation values in `iran_crown_majlis_l_english.yml` are longer than 255 characters** (lines 3, 29, 32) and were so before this card, as the validator's own `SOURCE_STRING_TOO_LONG` findings show for a file family it does not otherwise check.

## Not verified

No game was launched. Nothing here proves that the four decisions appear and are clickable under Pahlavi rule, that a shift shows the intended balance range in the interface, that a timed country flag really expires after 365 days, or that the socialist shift visibly changes the ruling party.
Those are engine-side facts and remain for a user-run live check; the card asked for static and MCP evidence only.

## Disposition

Implemented inside the assigned ownership with source-driven regression coverage and pinned mutants for all four defects.
Correction round 1 answered the QA rejection `iran-bop-constitutional-shift-sync-removes-balance`: the balance layer's regime test now excludes a proclaimed successor regime (and the resurgence test with it), the durable test models `PER_bop_sync` so the class cannot pass again, and this document's pre-repair description was corrected - the constitutional shift used to end with no balance at all, not at -0.15.
Independent same-card QA by `endsieg-qa` is mandatory before Director integration; the Developer did not self-complete, did not commit and did not launch the game.
