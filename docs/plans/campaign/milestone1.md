# Milestone 1 — playable Spain, Iran and Qing/China

Status: active execution plan, 2026-10-26.
Milestone 1 means English-only playable mechanics with static/source validation and independent QA.
It does not mean in-game verification, non-English localisation or finished visual polish; those are Milestone 2.
Repository and native Kanban history remain authoritative over this plan.
No artwork replacement, game launch, push or premium model is authorized.

## Already implemented — do not repeat

| Work | Commit / evidence | What it actually delivers |
| --- | --- | --- |
| Spain budget/army bill swing arithmetic | `21161e9d6` | Liberals are the swing party, not double-counted in the supporting bloc. |
| Spain electoral-law support count | `a03205963` | The electoral bill uses a partisan base rather than the whole chamber. |
| Spain Republic recount ordering and seat identities | `f6d12527c` | Era base first, modifiers preserved, one clamp, explicit equality comparisons, real 400-seat invariant; 215 source checks and independent QA pass. |
| Iran interwar Gulf naval rewards | `92b2d7d07` | Both rewards build in coastal Khuzestan; description matches; 24 checks and 15 independent invalid mutations. |
| China Republic chapter routing | `f8f9225b0` | One authoritative chapter/tree transition per day, sibling flags cleared, DLC handover mirrored; independent 3,840-cell walk. |
| B0 quality benchmark | `d666dc710` | Reviewed reward/AI/layout/localisation standard; planning gate only. |
| S1/I0/I1/I3/C0/C1/B0/S0 audits | native cards | Concrete defects and route maps; audits are not implementation. |
| S8 electoral-law design | `11ee701ab` | Proposal only; S3 implemented only a narrow part of it. |

## Remaining Milestone 1 inventory

Estimates use measured worker durations below, not calendar guesses.
`S` = small (1–3 files, existing readers/IDs), `M` = medium (4–8 files or one new decision/event family), `L` = large (new subsystem or multi-file route slice).

| ID | Work | Class | Proposed owned files | Dev est. | QA est. | Dependency |
| --- | --- | --- | --- | ---: | ---: | --- |
| S10 | Spain: exclusive chapter state and bill-cache bootstrap | M | `spain_campaign_effects.txt`, `spain_cortes_effects.txt`, `spain_cortes_bills.txt`, `events/spain_cortes_bills.txt`, one test + handoff | 20 min | 10 min | S1 done |
| S11 | Spain: hemicycle frame indexing, duplicate key, bill cooldown | S | scripted-GUI hemicycle file, `spain_campaign_l_english.yml`, `decisions/spain_cortes.txt`, test + handoff | 15 min | 8 min | S1 done; serialise localisation/decisions |
| S12 | Spain: Restoration reward/layout defects found by S5 | M | S5 findings, then exact focus/localisation paths | 20 min | 10 min | S5 audit |
| S13 | Spain: S2 turno/ministerial implementation slice | M/L | `spain_campaign_effects.txt`, decisions/events, localisation, test; exact paths after design acceptance | 45 min | 15 min | S2 design pass |
| S14 | Spain: S4 dictatorship/Republic chapter slice | L | focus/effects/decisions/loc; exact paths after design | 60 min | 15 min | S4 design |
| S15 | Spain: S6 1945 continuation slice | L | focus/effects/decisions/loc; exact paths after design | 60 min | 15 min | S2/S4/S5 |
| I6 | Iran: Pahlavi agreement availability + regime-shift ordering + ideology id | M | `decisions/iran_foreign_agreements.txt`, `scripted_effects/iran_regime_shift.txt`, `scripted_effects/PER_bop_effects.txt`, `script_constants/iran_campaign.txt`, test + handoff | 25 min | 10 min | I1 done |
| I7 | Iran: decree-treaty timer, unread flag readers, continuity fixes | M | `events/iran_negotiations.txt`, `scripted_triggers/iran_continuity.txt`, `events/iran_campaign.txt`, `decisions/iran_great_powers.txt`, test + handoff | 25 min | 10 min | I6 (serialise shared files) |
| I8 | Iran: focus requirement tooltips (16 raw flags) | M | `iran_interwar.txt`, `iran_ww2.txt`, localisation, test | 20 min | 10 min | I5 done |
| I9 | Iran: I2 slice A — derived leverage, one writer | L | `iran_campaign.txt`, `iran_great_game_acts.txt`, constants, decisions/events, loc, docs | 45 min | 15 min | I6/I7 |
| I10 | Iran: I2 slice B — standing and patron agendas | L | new effects/decisions/category/opinion/ideas/loc/docs; one line in `iran_campaign.txt` | 60 min | 20 min | I9 |
| I11 | Iran: I4 residual reward/branch repair | M | at most five focus IDs and their localisation/effects | 30 min | 12 min | I1/I3 done; I8 serialises focus files |
| C7 | China: gate Qing survival, historical-human fix, pre-uprising settlement | M | `qing_campaign` triggers/effects/constants/events, English loc, test | 25 min | 10 min | C2 design accepted |
| C8 | China: settlement outcomes without unconditional annexation | L | `qing_campaign` effects/triggers/ownership, loc, test | 45 min | 15 min | C7 |
| C9 | China: consolidation band and restoration gate | L | `qing_campaign` decisions/effects/constants, `qing_interwar` gate, loc, test | 60 min | 20 min | C8 |
| C10 | China: C3 Republic succession slice | L | `rch_campaign` effects, events/decisions, loc, test | 60 min | 20 min | C3 design |
| C11 | China: C4 pilot warlord identity/reunification | L | one existing warlord focus/effects/decisions/loc | 60 min | 20 min | C3 accepted |
| C12 | China: C5 continuation/DLC slice | L | `rch_nanjing`/on_actions/effects/loc | 60 min | 20 min | C9/C11 |
| C13 | China: C6 final source/scenario QA | L | read-only; findings only | — | 30 min | C7–C12 |

Approximate worker time: **13–15 hours** for the full table.
The current measured bottleneck is not coding; it is converting the remaining broad designs into the exact slices above and serialising shared files.
Full Milestone 1 is therefore **2–4 working days of continuous agent execution**, with **3 working days** the central estimate.
If only the already-specified defect repairs are counted (S10, S11, S12, I6–I8, C7, plus C8), it is **5–7 hours of worker time**, about **1.5–2 working days** including review and integration.
That narrower set is the recommended first playable target; the design-dependent slices follow immediately.

## Measured throughput and waiting

Completed implementation runs (excluding fixtures): 7.7, 9.8, 5.2/3.6, 13.4/11.8 and 13.5/12.2 minutes.
Median single implementation attempt: **~10.7 minutes**; correction attempts add **~12 minutes**.
Completed independent QA runs: 3.8, 7.6, 5.5/6.8, 7.3/10.0 and 8.9 minutes.
Median QA run: **~7.3 minutes**; most repairs need **one** QA round, two accepted repairs needed one correction round.
Review-to-QA wait when the single QA slot was free: **0.2–0.9 minutes**.
Serialization or Director-only review added **10–30 minutes** in observed cases.
A small/medium implementation therefore costs roughly:
`10–20 min developer + 7–10 min QA + ~5 min integration = 22–35 min wall clock per slice`.
Two implementation workers plus one QA worker yield about **1.7–2.5 finished slices per hour** when exact specs and disjoint files are ready.
Unspecified design work is slower and less predictable; do not use the repair rate for it.

## Safe parallelisation

| Lane A | Lane B | Safe? |
| --- | --- | --- |
| S10 Spain chapter/cache (`spain_campaign_effects`, `spain_cortes_*`, `events/spain_cortes_bills`) | I6 Iran BoP (`iran_foreign_agreements`, `iran_regime_shift`, `PER_bop_effects`, Iran constants) | Yes — disjoint countries and files |
| S10 Spain | C7 Qing survival (`qing_campaign` triggers/effects/events/loc) | Yes |
| I6 Iran | C7 Qing survival | Yes |
| S11 Spain GUI/localisation/decisions | I6 Iran | Yes, but localisation and decisions remain single-owner |
| I9 Iran leverage | C7/C8 China | Yes |
| I7 Iran negotiations | I8 Iran focus tooltips | Yes — different files |
| S10 Spain | S11 Spain | Mostly yes, but localisation/decisions and the shared Cortes files must be checked before writes; prefer cross-country pairing |
| I6 Iran | I9 Iran | No — both touch Iran constants/effects; sequence them |
| C7/C8 China | C9 China | No — same `qing_campaign` files; sequence them |

Rule: reserve exact paths in a native comment before release, one owner per file, and never let two workers edit the same shared localisation or current-report file.

## Design-review policy for speed

- Do not reopen S7/S3/S9/I5/C1/B0; their work is implemented or accepted.
- S10/S11/I6/I7/I8/C7 are defect repairs from accepted audits; they need no new design review.
- I2 and C2 have delivered designs; Director accepts their file-disjoint slices now and records the few decisions in the design cards.
- S2 is correcting four source-proven design defects; its implementation waits for that correction, not for a new full review cycle.
- S4/S6/C3/C4/C5 still need a bounded design slice before implementation; request only the slice needed for the next implementation, not a complete country plan.

## Milestone 1 acceptance

- English localisation for every new key; existing keys preserved.
- No existing artwork, focus icon, ID or namespace replaced.
- Every implementation has a source/static regression test where practical, real MCP validation evidence and independent QA.
- No in-game claim; click-through, AI behaviour, UI rendering and live seat/transition effects remain Milestone 2.
- No unresolved critical defect is hidden by a completed card.

## Milestone 2 — after playable implementation

Remaining supported localisation languages, in-game UI/gameplay verification, visual/layout corrections, noncritical edge cases, live save/load transition checks and final completion reports.
Estimate: **1–2 weeks** depending on translation method and how much visual rework is required.
