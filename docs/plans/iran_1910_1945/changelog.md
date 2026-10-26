# Iran 1910–1945 — development changelog

Newest batch first. This file records what was measured, what was changed, and what was
deliberately *not* changed because it turned out not to be a defect.

## Batch 7 — the Great Game

British and Soviet standing are now tracked separately (`iran_british_standing` opens 55,
`iran_soviet_standing` 30) and played against each other through a six-decision category in the
decisions tab. Courting one costs you the other; playing them off needs both at 45 or more and pays in
authority and political power; expelling both buys authority and costs the leverage that came with
them. Inviting Germany in is only possible while London has not been courted too hard, and fires a
dedicated `iran_campaign.70` at Berlin.

Three mutually exclusive spirits — `iran_balancing_powers`, `iran_british_preference`,
`iran_soviet_preference` — reflect which patron has the upper hand. Balance is worth more than either
patron's favour and is the hardest to hold. The switch runs inside `hidden_effect` so it never shows up
as add/remove noise in focus tooltips.

### UI

The category holds six decisions, which is what vanilla categories use (its own run 4–6), so the panel
does not scroll. Titles are kept under thirty characters. The Iran decision tab now shows eight
categories in a 1941 game (state authority, national projects, sovereignty, political course, tribal
settlement, oil, the Great Game, wartime emergency) plus the coup panel in 1919–25 and the
regime-switch panel only on the fallback tree. If that reads as crowded in game, the merge candidate is
`iran_sovereignty` — the same subject matter — at the cost of one category of thirteen decisions.

### Caught by the tooling before commit

- The third-power decision first fired `iran_campaign.64`, which is gated `tag = ENG`; Germany would
  have received nothing. Replaced with `iran_campaign.70`, gated to `GER`.
- The event picture was invented (`GFX_report_event_generic_sign_treaty` does not exist); the sprite
  check caught it and it now uses `..._treaty1`.
- The balance condition first compared each standing against 15 rather than their gap. There is no
  `abs_temp_variable` in the engine, so the rule was redefined without arithmetic: both patrons at 45
  or more, neither at 60.

Audit clean at 307 focuses / 142 events / 86 decisions / 0 unresolved sprites; reference check clean.

## Batch 6 — oil becomes the interactive system the country is actually about

The package had one oil project decision and nothing else, while the brief treats the concession as
Iran's defining mechanic. There is now a category with five decisions spanning 1925–1945: press the
company for royalties (repeatable), settle the concession (the 1933 compromise), cancel it outright,
build a domestic refinery, and spend the revenue on Khuzestan's roads.

None of them is free. Squeezing costs leverage and stability and only pays for a year (timed dividend
spirit). Settling keeps the company and grows its stake. Cancelling gives authority, war support and
stability but takes 25 leverage and a −30 opinion hit with Britain.

The interaction that matters: **cancelling the concession closes the 1941 transit option**, because that
option requires 50 foreign leverage. A nationalist Iran cannot then negotiate a quiet arrangement with
London — the consequence falls out of the ledger rather than from a scripted rule.

### Validation tooling, again catching itself

- Decision localisation is now audited. The first run reported 32 missing keys; 16 of those were
  vanilla GoE decisions that ship without a `_desc`, so the check now requires titles only.
- The localisation loader was reading the mod and ignoring the game, which made every vanilla-provided
  key look absent. Fixed: 197,213 keys across mod plus vanilla.
- `iran_cancel_the_concession` and `iran_abadan_company_deal` first pointed at decision icons that do not
  exist (`generic_oil`, `generic_nationalization`). Replaced with registered ones
  (`generic_fundraising`, `generic_nationalism`).

Audit clean at 307 focuses / 141 events / 80 decisions / 0 unresolved sprites; reference check clean at
262 event and 30 idea references. Not played.

## Batch 5 — officer loyalty pays off, 1941 resistance gets a real gate, references get checked

### Balance and interactivity

- The 1941 crisis event (`iran_campaign.40`) offered resistance with **no condition at all** — any Iran
  could choose to fight Britain and the Soviet Union. Resistance is now gated on `iran_army_stands_firm`:
  officer loyalty ≥ 50, authority ≥ 40 and war support > 25%.
- New third option: grant transit under protest. It needs 50 foreign leverage, costs authority and
  stability, keeps Iran unoccupied, and grants the `iran_transit_standing` spirit
  (+5% stability, +5% political power, −3% consumer goods). Without the spirit the flag it set was read
  by nothing — a choice with no consequence.
- The 1921 officer-loyalty variable now has a downstream effect instead of dying in 1925: below 40
  loyalty Iran carries `iran_divided_officer_corps` (−5% army organisation, −10% planning speed,
  −10% command power gain) until the corps is rebuilt. Purging the Cossacks in 1922 costs army quality
  in 1941 — which is the point of tracking it.

### Stability

- `tools/iran_reference_check.py` resolves every event, idea and scripted call the package makes
  against the mod plus the installed game: **262 event references and 29 idea references, all
  resolving**. A decision firing an undefined event looks available and does nothing; that class is
  now caught before a launch.
- `tools/iran_balance_report.py` reports buildings, equipment, manpower, once-only gating and variable
  write counts so outliers can be compared rather than guessed. Its first run flagged five repeatable
  decisions and unbounded variables; both turned out to be checker artefacts — the decisions are gated
  by completion flags, and `iran_authority`/`iran_foreign_leverage` are clamped in
  `iran_refresh_mechanics`. Recorded here so the next pass does not re-investigate them.
- Self-inflicted defect caught before commit: the new officer-corps idea was first appended **outside**
  the `ideas = { }` wrapper, where the engine ignores it. Moved inside; the reference checker is what
  caught it.

Validation: audit clean (307 focuses, 141 events, 75 decisions, 0 unresolved sprites), reference check
clean. Still not played.

## Batch 4 — the regime-switch decisions had no category to live in

`common/decisions/iran_political_question.txt` exposed five decision bodies at top level
(`iran_political_question_qajar`, `_republic`, `_constitution`, `_socialist`, `_nationalist`)
while `common/decisions/categories/` defined exactly one category, `iran_political_question`.
A decisions file maps one top-level block to one category, so those five had nothing to attach
to and every regime-switch decision in the fallback 1936 chapter would have been dropped.

They are now nested inside a single `iran_political_question = { ... }` block matching the
category, with consistent indentation and the stray indent on the last `ai_will_do` corrected.
All five `iran_shift_to_*` effects they call exist.

The audit gained a structural check for this: any Iran decisions block whose name has no
category is now an error. Decision count rose from 70 to 75 simply because the five were
invisible to the old counter — they were never loading.

## Batch 3 — the 1921 coup becomes a contest, and six corrupted focus lines

### Parser corruption (real defects, found by hand)

Six focus blocks carried a spliced fragment of their own id where a key belongs, e.g.
`prerequisite = { focus = IR2_command_and_cabinet }d_and_cabinet cost = @short`. A stray
token there fails the parse. Repaired one in `iran_ww1.txt`, three in `iran_interwar.txt` and
two in `iran_ww2.txt`; `tools/iran_audit.py` now flags the pattern so it cannot return quietly.

### The coup

Previously two focuses: take the coup, take the ministry, take the Pahlavi settlement. Now a
measured contest with two variables, a monthly drift, five decisions and a threshold gate. Full
write-up in `docs/systems/iran_coup_1921.md`.

- `iran_reza_influence` (opens 25) and `iran_officer_loyalty` (opens 50), initialised in
  `iran_initialize_campaign`, clamped after every change.
- `iran_coup_tick` runs from a new `on_monthly_PER` hook — not the daily tick, or a monthly drift
  would fire every day. `on_monthly_TAG` is vanilla-supported (`on_monthly_GER` etc.).
- The historical focuses still reach the threshold on their own (25 + 30 + 20 = 75 against a
  threshold of 60), so historical AI is unaffected.
- Qajar, constitutional and republican players now have five decisions to hold him down, at real
  cost in political power, stability and equipment.

Validation: audit clean at 307 focuses / 141 events / 70 decisions / 0 unresolved sprites.
Not yet played — the drift rate and the decision costs are reasoned, not tested.

## Batch 2 — the 1936 handover no longer flattens three regimes

`iran_route_chapter` handed Iran to the DLC's `persian_focus_tree` in 1936 whenever the DLC was
present, whatever the interwar outcome. That tree only distinguishes four governments: communist,
democratic, fascist and non-aligned. A Qajar restoration, a constitutional monarchy and a Pahlavi
Iran all arrive as "neutral", so three of the six settlements became the same country at 1936.

The router now hands over only to regimes the DLC tree can actually represent:

| Settlement | 1936 tree | Why |
| --- | --- | --- |
| none (historical) | `persian_focus_tree` | the DLC's own historical content |
| Pahlavi | `persian_focus_tree` | non-aligned *is* the historical Pahlavi line, and it is the deepest content |
| Republic | `persian_focus_tree` | democratic branch |
| Nationalist front | `persian_focus_tree` | fascist branch |
| Socialist republic | `persian_focus_tree` | communist branch |
| Qajar restoration | `iran_ww2` | the DLC tree has no Qajar concept; `IR3` has a dedicated branch |
| Constitutional monarchy | `iran_ww2` | same — no distinct ideology to map onto |

The three ideology settlements also gain `add_popularity` for their ideology (0.30), because the DLC
tree's branch *entry* focuses are gated on popularity rather than on the ruling party alone; without
it a legitimately communist Iran could still find Tudeh content locked.

Validation: audit re-run clean (307 focuses, 0 problems); braces balanced; no localisation impact.
Not yet seen on screen — the 1936 handover has not been played through in this batch.

## Batch 1 — audit tooling and the defects it found

### Branch

Work is on **`TeknoDev-Branch`**. No branch named `tekodev` exists in this repository
(`git branch -a` lists `TeknoDev-Branch`, `master` and the remote feature branches), and the
instruction was not to create another branch, so the existing development branch was used
as-is. Nothing was force-pushed, reset or deleted. Another agent is active in the same
working tree on Spain, Qing and the settlement system; those paths were not touched.

### Tooling added

- `tools/iran_audit.py` — static audit of the Iran package: duplicate focus ids, focuses
  sharing an absolute grid cell (it resolves `relative_position_id` chains), prerequisites
  and relative positions pointing at missing ids, focuses unreachable from any root,
  duplicate event ids, events in a namespace with no `add_namespace`, duplicate decision
  ids, missing focus localisation, unregistered sprites and idea pictures, and style
  violations. Run with `--game "<HOI4 install>" --report <path>`.
- `tools/prune_dead_portraits.py` — removes character `portraits` entries whose sprite is
  never registered, and the sub-blocks they leave empty.

Current result: **307 focuses, 141 events, 65 decisions, 0 problems.**

### Fixed

| Defect | Detail |
| --- | --- |
| Two Shah portraits unregistered | `gfx/leaders/PER/Portrait_Persia_Ahmad_Shah_Qajar.dds` and `Portrait_Iran_Reza_Shah_Pahlavi.dds` both existed at 156×210 but no sprite referenced them, so the two central characters of the overhaul drew the default portrait. Registered in the new `interface/iran_portraits.gfx`, with 65×67 small crops generated in `gfx/interface/portraits/iran/`. |
| 59 character portraits pointed at art that does not exist | `PER.txt` and `PER_restored.txt` referenced sprites for Foroughi, Mosaddegh, Kashani, Zelli, Arfa, Razmara, Khomeini and others with no image anywhere in `gfx/`. Removed the unresolvable entries so those characters fall back to the engine default instead of a blank frame. See "Pending art" below. |
| 4 operative portraits unresolvable | `PER_scripted_effects.txt` used `GFX_portrait_arabia_generic_operative_male_1/2/4` and `GFX_portrait_PER_teymur_bakhtiar`, none of which exist in the mod or in vanilla. Repointed to vanilla's `GFX_portrait_operative_unknown`. |
| Decision category picture missing its `GFX_` prefix | `picture = decision_cat_picture_national_iranian_radio` → `GFX_decision_cat_picture_national_iranian_radio`. Category pictures take a full sprite name; the unprefixed form resolved to nothing. |
| UTF-8 BOM written into two script files | `PER_decision_categories.txt` and `PER_scripted_effects.txt` were saved with a BOM during this batch, which is fatal to the Clausewitz parser. Stripped; both now start on their first real token. |

### Checked and deliberately not changed

- `check_variable = { iran_authority < 50 }` — the short form. `documentation/triggers_documentation.md`
  documents both `{ var = x value = 1 compare = less_than }` and `{ x < 1 }`, and vanilla
  uses the short form heavily. Not a defect; the auditor no longer flags it.
- Identical `x`/`y` across many focuses — the trees are laid out with `relative_position_id`,
  so equal offsets are relative to different parents. Only absolute positions are compared.
- "Duplicate event ids" in `events/GOE_Persia.txt` — these were inline fires
  (`country_event = { id = X hours = 2 }`), not definitions. The auditor now ignores blocks
  with no `title`/`desc`.

### Pending art

59 characters have no portrait and now use the engine default: Mohammad Mosaddegh,
Mohammad Ali Foroughi, Abol-Ghasem Kashani, Abdollah Zelli, Hasan Arfa, Haj Ali Razmara,
Ruhollah Khomeini, Teymur Bakhtiar, Zia ol-Din Tabatabee, Soleiman Eskandari, Bahram Aryana,
Davud Monshizadeh, Gholamali Bayandor and the rest. Each needs a period portrait before it
can be shown; the names are recorded here so the list does not have to be rediscovered.
