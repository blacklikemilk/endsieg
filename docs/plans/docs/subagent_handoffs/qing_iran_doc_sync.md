# D1 handoff: Qing and Iran system docs reconciled with the accepted repairs

Task `t_08e7b4a0`, branch `TeknoDev-Branch`.
The first draft was written at `f8d54678c` and the corrections below were made at `ce6247246`; `git diff --stat f8d54678c..ce6247246` over the cited Qing and Iran source files and `docs/systems/` is empty, so every line citation holds at both revisions.
Reviewer: `endsieg-qa`.
Documentation only: no gameplay, localisation, interface, asset or test file was touched.
No launch, no in-game claim, no staging, no commit; Director integrates.

## Files changed

| File | Change |
| --- | --- |
| `docs/systems/qing_campaign.md` | Settlement window, armistice deadline, three-outcome router, partition honesty, chapter-two gate, file counts |
| `docs/systems/iran_negotiations.md` | `iran_decree_treaty` duration and reader, day-count macros, stale untested item |
| `docs/systems/crown_and_majlis.md` | Regime-shift ordering, settlement/shift counts, changelog phrasing removed |
| `docs/plans/docs/subagent_handoffs/qing_iran_doc_sync.md` | This handoff |

## Corrected claims

### `docs/systems/qing_campaign.md`

| Old text | New text | Decisive source |
| --- | --- | --- |
| "The dynasty can survive the Xinhai revolution through one of four settlements" | "through one of four route settlements, and each route ends the war in one of three territorial outcomes: partition, reunion or conquest" | `common/scripted_effects/qing_campaign.txt:540-634` (four route effects) and `:451-470` (three-outcome router) |
| "The revolution is settled either before Wuchang (a reformed dynasty), by a strong army, or by a court council during the war." (lines 35-36) | "The revolution window opens on the war itself: after 9 October 1911, while the court is at war with the Republic, the tick arms it and offers the first terms." | `common/scripted_effects/qing_campaign.txt:320-327`; `common/scripted_triggers/qing_campaign.txt:131-134` |
| No armistice deadline was stated | "The armistice the powers broker closes it again after `constant:qing_story.armistice_days`, when `qing_campaign.19` sets `qing_armistice_closed`." | `common/scripted_effects/qing_campaign.txt:7,327`; `common/script_constants/qing_campaign.txt:76`; `events/qing_campaign.txt:126-133` |
| "A settlement annexes the Republic, sets exactly one route flag, replaces the leader, and writes `qing_xinhai_settled` as a global flag." | "A settlement sets exactly one route flag — constitutional, authoritarian, Yuan or federal — replaces or promotes the leader, and writes `qing_xinhai_settled` as a global flag." | `common/scripted_effects/qing_campaign.txt:475-489` (partition sets no annexation), `:540-634` (route flags), `:451-470` (router) |
| Settlement events given as `.20`, `.22`, `.23` | `.20`, `.22`, `.23` and `.62` | `events/qing_campaign.txt:136,211,263,1030`; `:1045-1055` (`.62.b` offers the constitutional settlement); fired from `common/national_focus/qing_ww1.txt:1790` |
| "Surviving Qing ... the Republic is annexed" | "a settlement inside the armistice window ... one route flag and one settlement outcome" | `common/scripted_effects/qing_campaign.txt:451-470` |
| No description of the router or of the core question | New section: conquest/reunion/partition in that order, all three a `white_peace = RCH`, reunion and conquest then `annex_country = { target = RCH transfer_troops = no }` while RCH exists, partition annexes nothing, no outcome adds a core in script | `common/scripted_effects/qing_campaign.txt:451-538`; `common/scripted_triggers/qing_campaign.txt:137-157`; zero `add_core_state`/`add_core_of` matches in `common/scripted_effects/qing_campaign.txt` and `events/qing_campaign.txt` |
| Partition implied to hand the Republic the south | "the 1910 base block leaves the Republic owning no state … so partition is a survival, not a grant of the south"; the partition flag excludes the 1914 and 1936 reclaim, the reclaim assigns states to `ROOT` (the Qing) only, and no handover runs | `history/states/592-Guangzhou.txt:13-15` (base owner QIN) against `:33-36` (dated 1914 block, which applies only to a start after that date per `paradox_wiki/State modding - Hearts of Iron 4 Wiki.md:59`); `common/scripted_effects/qing_campaign.txt:283-302` (both reclaim blocks gated `NOT = { has_country_flag = qing_settlement_partition }`); `common/scripted_effects/endsieg_china_ownership.txt:90` (`set_state_owner_to = ROOT`) |
| "`annex_country` on the Republic during the settlement" listed as a general known risk (line 74) | "`annex_country` on the Republic in the reunion and conquest outcomes, resolving after a white peace and only while the Republic exists." | `common/scripted_effects/qing_campaign.txt:501-508,525-532` |
| Focus counts 88 / 85 / 65 | 158 / 99 / 65 | `common/national_focus/qing_ww1.txt:4`, `qing_interwar.txt:5`, `qing_ww2.txt:4` |
| "38 decisions in four categories" | 45 decisions in five categories (`QIN_throne_and_assembly_category` 8, `qing_imperial_government` 16, `qing_reconstruction` 8, `qing_foreign_policy` 7, `qing_war_council` 6) | `common/decisions/qing_campaign.txt` category blocks at `:7,152,523,680,824`; `common/decisions/categories/qing_campaign.txt:4,19,30,40,51` |
| "33 events, 76 options" | 38 events, 89 options | `events/qing_campaign.txt` (38 `country_event`, 89 `option`) |
| Chapter boundaries presented as calendar milestones only | The interwar chapter loads only once `qing_consolidation` is at `constant:qing_story.consolidation_gate`, and a full `constant:qing_story.consolidation_hold_days` opens the restoration band; `qing_consolidation` added to the values table as derived | `common/scripted_effects/qing_campaign.txt:101-121,172-182,199-208,360-367`; `common/scripted_triggers/qing_campaign.txt:243-252` |

### `docs/systems/iran_negotiations.md`

| Old text | New text | Decisive source |
| --- | --- | --- |
| "`iran_decree_treaty` \| permanent \| a treaty was signed without the chamber" | "`iran_decree_treaty` \| 365 days (`@decree_treaty_days`) \| ... and the budget vote is barred until the year is out" | `events/iran_negotiations.txt:15` (`@decree_treaty_days = 365`) with setters at `:71,252,430,608` |
| "- **Budget vote**: `iran_decree_treaty` is the hook a later pass should read; see the note in the change list." | "`PER_bop_budget_vote` cannot be taken while `iran_decree_treaty` is set ... costs the chamber one yearly cycle and no more." | `common/decisions/PER_crown_and_majlis.txt:112-113` (available gate and `PER_bop_decree_treaty_tt`) |
| Decree option described only as read by the vote events | Also states that it bars the budget vote while it runs | same decision gate; `events/iran_negotiations.txt:142,321,499,676` (vote weights) |
| Untested item: "whether `constant:iran_story.negotiation_*_days` is accepted in `days =` fields" | Removed; the doc now records that day counts are file macros | `common/scripted_effects/iran_negotiations.txt:12-13`; `events/iran_negotiations.txt:11-15`; `common/script_constants/iran_campaign.txt:117,129` |

### `docs/systems/crown_and_majlis.md`

| Old text | New text | Decisive source |
| --- | --- | --- |
| "Qajar, constitutional, republican, socialist and nationalist settlements keep the balance." with no ordering | Same sentence plus a "Regime shifts" section: each shift creates the balance at the centre through `PER_bop_open_regime`, pushes through `PER_bop_settle_*`, then resyncs; a push before the balance exists would leave `PER_bop_sync` to create the era's opening value | `common/scripted_effects/iran_regime_shift.txt:35-37,50-52,63-65,77-79,90-92`; `common/scripted_effects/PER_bop_effects.txt:230-247` |
| Nothing said why the constitutional shift keeps the balance | "The constitutional shift keeps the Shah and `PER_pahlavi_dynasty`, and its successor flag is what holds `PER_bop_sync` off the autocracy branch, so the balance survives at the centre" | `common/scripted_effects/iran_regime_shift.txt:56-67` (no `clr_country_flag = PER_pahlavi_dynasty`) against `:31,46,73,87`; `common/scripted_effects/PER_bop_effects.txt:127-152` |
| "The six regime settlements and the six later regime shifts push the balance through `PER_bop_settle_*`." | "The five settlements that keep the balance push it through `PER_bop_settle_*`, and the five later regime shifts open it at the centre first, push it and resync." | `common/scripted_effects/PER_bop_effects.txt:249-253`; `common/scripted_effects/iran_regime_shift.txt:27,41,56,69,83`; `common/scripted_effects/iran_campaign.txt:258-353` (Pahlavi settlement calls only `PER_bop_sync`) |
| "Ten standing decisions became four: ..." (update history) | "Four standing decisions: ..." | `common/decisions/PER_crown_and_majlis.txt:10,33,56,75` |

## Corrections after independent QA round 1

Three statements in the first draft restated the effect's design comment rather than the shipped effect; independent QA rejected all three and this pass corrects them to the script.

| Finding | Old text (first draft) | New text | Decisive source |
| --- | --- | --- | --- |
| Router generalised the standing-value reward | "Every outcome … sets one settlement flag, and moves political capital, stability and at least one standing value." (line 53) | "Every outcome … moves political power and stability." plus "Reunion and conquest also move a standing value — reunion gains `qing_legitimacy`, conquest gains `qing_army_loyalty` while it loses legitimacy — so partition is the only one of the three that leaves the standing values untouched." | `common/scripted_effects/qing_campaign.txt:475-489` (partition writes only `add_political_power` and `add_stability`) against `:494-513` (`qing_legitimacy`) and `:518-538` (`qing_army_loyalty` and `qing_legitimacy` with `constant:qing_story.legitimacy_loss`, negative at `common/script_constants/qing_campaign.txt:17`) |
| Partition promised a historical handover | "… the map follows the historical handover instead." (line 57) | "… the Qing keeps every state it holds and no handover runs." | `common/scripted_effects/qing_campaign.txt:283-302` (both reclaim blocks gated `NOT = { has_country_flag = qing_settlement_partition }`); `common/scripted_effects/endsieg_china_ownership.txt:90` (`set_state_owner_to = ROOT`, never RCH); `history/states/592-Guangzhou.txt:13-15` (base owner QIN) against the dated `:33-36` block |
| Decision-category count | "45 decisions in four categories" (line 20), supported by a citation naming four category blocks | "45 decisions in five categories", with the balance category in the evidence | `common/decisions/qing_campaign.txt:7` (`QIN_throne_and_assembly_category`, 8 decisions), `:152` (16), `:523` (8), `:680` (7), `:824` (6), total 45; `common/decisions/categories/qing_campaign.txt:4,19,30,40,51` |

## MCP evidence

Workspace `endsieg` (`workspaceId: "current"`).
The index was at revision `ea7dfb2ecadf32fdc41c8d1c853b569fb978d6bfe745d9b8161830af39bea92c` when the three routes below were re-run for this pass; an earlier draft recorded `50c02815…7d81` with the same definitions and the same counts.

| Route | Input | Finding | Coverage limit |
| --- | --- | --- | --- |
| `hoi4.source_lookup` | `symbol: qing_end_revolution` | 1 definition, `mod:common/scripted_effects/qing_campaign.txt:451-470`, text returned in full: gate `NOT = { qing_historical_collapse = yes }` plus `qing_armistice_open = yes`, then `qing_can_settle_conquest` → `qing_can_settle_reunion` → `qing_can_settle_partition`; 4 references, one from each `qing_settle_*` route effect (`:546,570,594,618`) | `referencesComplete: false` with `unresolvedReferenceCount: 2570`, which is index-wide and not specific to this symbol; a source index is not engine evaluation |
| `hoi4.source_lookup` | `symbol: qing_armistice_open` | 1 definition, `mod:common/scripted_triggers/qing_campaign.txt:131-134`, text returned in full: `has_country_flag = qing_revolution_window_seen` and `NOT = { has_country_flag = qing_armistice_closed }`; 10 references — `qing_campaign_tick:349`, the router at `:455`, the four settle gates at `:544,568,592,616`, the three settle-availability triggers at `common/scripted_triggers/qing_campaign.txt:138,146,154` and `qing_campaign.62` at `events/qing_campaign.txt:1050` | `referencesComplete: false`; the route proves the definition text and its call sites, not runtime order |
| `hoi4.source_lookup` | `symbol: PER_bop_sync` | 1 definition, `mod:common/scripted_effects/PER_bop_effects.txt:119-190`; 13 references — five `iran_settle_*` effects, five `iran_shift_to_*` effects, `iran_campaign_tick:204` and `iran_campaign.77` at `events/iran_campaign.txt:801`; the returned text shows the Pahlavi autocracy branch and its `has_power_balance` guard | Text returned to line 158 (`nextLine: 159`), so the successor-flag guard at `:127-152` was confirmed from the file, not from the truncated text |
| `hoi4.reference_search` | `query: "state history datestamp only executed if start date is after"` | `State modding` § History, match line 59: a `YYYY.MM.DD = { … }` block inside state history "will make them be executed only if the start date is strictly after the specified date"; corroborated by `Bookmark modding` § Notes, match line 163, "executed if and only if the start date is …". This is what the partition paragraph relies on for the 1914 history blocks not applying to a 1910 campaign | The offline wiki is an engine reference, not a test of this mod's own files; it says nothing about the runtime ordering of `white_peace` and `annex_country` |

## Validation

- `python tools/china_audit.py --mod . --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"`: `## Clean: no problems found`, 468 focuses, 55 China-namespace events, 64 decisions, 0 missing focus keys, 0 unresolved sprites.
- `python tools/iran_audit.py --mod . --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"`: `## Clean: no problems found`, 328 focuses, 0 missing focus keys, 0 unresolved sprites.
- `python .tools/sync/check_guidance_size.py`: "55 guidance files are within the 20,000-token single-read ceiling"; no doc in this card is a guidance file.
- Retired-claim grep on the three owned docs: "before Wuchang" 0 matches; "annexes the Republic" 0 matches; "permanent" 8 matches, all of them flags that genuinely carry no duration (`iran_demand_<id>_done`, `_accepted`/`_compromised`, `_rejected`, `_supported`, `_delayed`, `_escalated`, `_renegotiated`, and the four compromise flags on the shared line at `:81`); `iran_decree_treaty` is not among them.
- Base-block ownership grep behind the partition paragraph: 0 state files carry a base-level `owner = RCH` (two-tab indent), all 55 `owner = RCH` lines sit inside dated blocks (three-tab indent, 1914.1.1 and later), and 64 states carry a base-level `owner = QIN`.
- Markdown only: `git status --porcelain` after the edits lists the three owned docs plus this handoff, and nothing else from this card.

## Unverified without a launch

- Engine acceptance of `set_power_balance` on the first daily tick and of the chapter tree load from the startup hook, both unchanged by this card and still listed in the Qing doc as risks.
- Engine resolution of `annex_country` after a `white_peace` inside the same effect, and whether the annexed Republic's states arrive with or without cores; the doc now claims only what the script does.
- Engine expiry of a duration-carrying `set_country_flag` for `iran_decree_treaty`, and that `PER_bop_budget_vote` reappears on the next yearly cycle.
- Whether `PER_bop_sync` and the shift effects settle in the same day without a visible balance flicker; `docs/systems/crown_and_majlis.md` still records the same-day remove/recreate as untested.

## Noticed, not changed

- `docs/systems/crown_and_majlis.md` still says "28 political focuses push the balance". The count was not re-derived in this card; `PER_bop_push*` call sites number 64 across the three Iran focus files, which does not settle how many focuses are meant.
- `docs/systems/iran_negotiations.md` says the option list should be read "at six" and elsewhere "up to seven visible options"; seven options are defined, of which the Majlis and decree answers are mutually exclusive by balance side, so at most six show. Left as written because both statements are defensible and the card did not own that question.
- `docs/plans/qing_1910_1945/current_report.md` is still stale on the Qing consolidation pass. It is outside this card's owned files.
- `docs/systems/iran_negotiations.md:36` and `:78` say `iran_patron_tension_<patron>` lasts four years / 1460 days, but the setters at `common/scripted_effects/iran_negotiations.txt:28,31,34` carry no duration and no effect clears the flags, so as shipped they last the campaign. The prose and a possibly intended duration are two different repairs, neither of which this card owns; independent QA recorded the line as non-blocking for this card, so it is reported here for Director instead of changed.
