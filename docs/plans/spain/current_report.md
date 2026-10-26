# Spain 1910-1945 — current task report

## Request

Overhaul Spain across 1910-1945 with era-changing focus trees, interactive political systems, a developed civil war, post-war content for every plausible victor, correct behaviour in every bookmark, AI behaviour and documentation.
A later instruction from the user narrowed the civil-war scope: investigate and reuse what Endsieg already has, and put the effort into 1910-1936 and 1939-1945 plus the era system.

## What the audit found (and why nothing was rebuilt)

| Existing surface | Size | Decision |
| --- | --- | --- |
| `common/national_focus/spain.txt`, tree `spanish_focus` | 13,428 lines, 281 focuses | kept. It is the vanilla La Résistance tree with two roots (`SPA_a_great_spain`, `SPR_the_popular_front`) and the whole Nationalist/Falangist/Carlist/anarchist/communist branching. |
| `common/decisions/SPR.txt` | 18,269 lines, 178 decisions, 11 categories | kept. Includes `SPA_garrison_control`, the civil-war offensives, foreign arms purchases and the seeds of revolution. |
| `events/LAR_Spain.txt` | 91 events, namespace `lar_spain` | kept. Owns the rising, the tag splits and the war ending. |
| `events/LAR_NewsEvents.txt` | 2,972 lines | kept. |
| `common/ideas/spain_nationalist.txt`, `spain_republic.txt` | 145 spirits | kept. |
| `SPR_scripted_effects.txt`, `SPR_scripted_triggers.txt` | 366 lines | kept. |
| `05_lar_on_actions.txt` | — | kept. Creates SPA/SPB/SPC/SPD and handles the war. |

Before this change, the only trees Spain could load were `spanish_focus` (1936+, `has_dlc = "La Resistance"` selector) and `generic_focus_ww1` (assigned by `on_startup` to every country without its own WWI tree).
So 1910-1935 was played on the generic Great War tree: no Restoration, no Rif War, no dictatorship and no Republic.

## Delivered

### New files

| File | Content |
| --- | --- |
| `common/script_constants/spain_campaign.txt` | all tuning values, read as `constant:spain_campaign.*` |
| `common/scripted_effects/spain_campaign_effects.txt` | initialisation, chapter openers, transitions, daily and weekly clocks, officer corps, coups, balance-of-power nudges, regional control, faction resolution, diplomacy, reconstruction |
| `common/scripted_triggers/spain_campaign_triggers.txt` | 34 predicates for chapters, loyalty, balance ranges, regions, factions, development, Rif War, leverage, reconstruction |
| `common/bop/SPR_crown_and_cortes.txt` | the Crown against the Cortes, 2 sides, 5 ranges, modifiers and range events |
| `common/ideas/spain_campaign.txt` | 46 national spirits: officer corps tiers, four development ladders, Restoration, Republic, statutes, seven wartime regions, four regime identities, diplomacy, reconstruction |
| `common/national_focus/spain_restoration.txt` | 36 focuses, 1910-1923 |
| `common/national_focus/spain_rivera.txt` | 24 focuses, 1923-1930 |
| `common/national_focus/spain_republic.txt` | 29 focuses, 1931-1936 |
| `common/national_focus/spain_republic_postwar.txt` | 22 focuses, 1939-1945 for a victorious Republic |
| `common/decisions/spain_campaign.txt` | 38 decisions in 8 categories |
| `common/decisions/categories/spain_campaign_categories.txt` | 8 decision categories |
| `events/spain_campaign.txt` | 18 events, namespace `spain_campaign`, including two news events |
| `common/on_actions/spain_campaign.txt` | `on_daily_SPR` clock |
| `common/opinion_modifiers/spain_campaign.txt` | 7 reciprocal opinion modifiers |
| `interface/endsieg_spain_icons.gfx` | 2 balance-of-power side sprites, reusing vanilla textures |
| `localisation/english/spain_campaign_focus_l_english.yml` | 227 keys: focus names, descriptions, navigation |
| `localisation/english/spain_campaign_l_english.yml` | 295 keys: spirits, balance of power, categories, decisions, events, tooltips |
| `docs/spain_campaign.md` | permanent feature documentation |
| `docs/specs/spain_1910_1945/spain_1910_1945_spec.md` | architecture and design |

### Modified files

| File | Change |
| --- | --- |
| `common/on_actions/endsieg_on_actions.txt` | one `else_if` for SPR in the pre-1936 tree assignment, and one call added to the existing 1936+ SPR branch |
| `common/ai_strategy_plans/SPR_historical_strategy_plan.txt` | `date > 1935.12.31` added to all three plans so the civil-war party line does not steer the chapter trees |

### Systems, and how they connect

1. **Crown against the Cortes** is a real balance of power with per-range modifiers and events at both extremes. Its decision category is mounted on the balance itself.
2. **Officer loyalty** sets coup pressure, gates coup attempts, and is the input the 1936 rising reads.
3. **Coups** are weighted weekly draws with three answers and three outcomes, one of which opens the dictatorship chapter.
4. **Rif War** operations are timed decisions with equipment and manpower costs.
5. **Regional control** grants seven holding spirits from `controls_state` tests during the war.
6. **Faction struggle** moves four influences, derives tension, fires a crisis event, and resolves the regime identity through a decision or the event.
7. **Wartime diplomacy** moves two leverage values through six decisions and three alignment spirits.
8. **Development** persists across chapters as four variables with three tier spirits each.
9. **Reconstruction** is a genuine debuff that the decision category clears.

### Bookmark coverage

1910, 1914, 1916 and 1918 open the Restoration chapter with a full variable set and balance value.
1936.1.1 opens the civil-war chapter on the vanilla tree.
1939 to 1945 open the post-war chapter with reconstruction in place.

## Validation performed

- Brace balance: all 15 new script files balanced.
- Focus ids: 111 new ids, no duplicates against the existing 281 vanilla focuses or anywhere else in `common/national_focus`.
- Tree references: every `prerequisite`, `mutually_exclusive` and `shared_focus` target resolves inside its own tree.
- Script references: every `spain_* = yes` call resolves to a defined scripted effect or trigger; every `add_ideas`/`remove_ideas`/`has_idea` id exists; every `country_event`/`news_event` id exists.
- Decision categories: every decision block matches a defined category and every category has decisions.
- Localisation: 521 required keys computed from script and all 521 present, no duplicate keys; both files carry a UTF-8 BOM.
- Icons: every `icon = GFX_*` reference in the four trees resolves to a real sprite in the mod or the installed vanilla interface files; every decision and category icon resolves likewise.
- Vanilla effect/trigger predicates used in decisions were checked against the installed `documentation/` reference (`has_army_experience`, `has_political_power`, `has_equipment`, `has_manpower`, `has_power_balance`, `is_debug`).

Not performed: any in-game test. Hearts of Iron IV was not launched. The transition dates, the coup pacing and the balance-of-power speed need one playtest per bookmark.

## Known gaps

- Custom Spanish focus, spirit, decision and balance-of-power art is not produced; everything reuses existing sprites. The exact sprite names and consumers are listed in `docs/spain_campaign.md`.
- The Crown/Cortes panel and the seated hemicycle now exist (`interface/endsieg_spain_cortes.gui`, `common/scripted_guis/spain_cortes_scripted_gui.txt`); their live repaint, party colours and frame mapping remain unverified in game.
- No regional control map.
- No achievements.
- Sanjurjo, Companys, Durruti, Gil Robles and Miguel Primo de Rivera appear in text but have no character definitions or portraits.
- Britain's and Germany's AI do not yet react specifically to Spanish leverage; the pressure exists on the Spanish side only.

## 2026-10-26 — Cortes bill repair and campaign restart

The current campaign brief re-opened Spain with the Cortes as Priority 1.
A source audit of the negotiated bills found that `spain_bill_count_budget` and `spain_bill_count_army` added the Liberal benches to the supporting bloc through `spain_bill_add_liberals`, then added the same Liberal seats to `spain_bill_swing_votes` again while the Liberals sat outside the government.
The budget and army concession options are gated on `spain_bill_swing_votes >= spain_bill_needed`, so the doubled count could offer a concession and pass a bill the chamber never actually carried.

The repair removes the two Liberal base calls: the base is now the government bloc plus the genuine supporters, and the Liberal benches enter the swing total exactly once, only while they are outside the government bloc.
`docs/spain_cortes_bills.md` now states the rule and carries four worked examples.
Only `common/scripted_effects/spain_cortes_bills.txt` and `docs/spain_cortes_bills.md` changed; commit `21161e9d6`.

Independent QA re-derived the arithmetic from the real script rather than the Developer's simulator:

| Case | Base | Swing | Concession option |
| --- | --- | --- | --- |
| Budget, Liberals 60, Conservatives 30, government 100 | 130 | 190 | not offered |
| Budget, Liberals 80, Conservatives 30, government 100 | 130 | 210 | offered |
| Army, Liberals 60, Monarchists 20, Conservatives 15, Falange 5, government 100 | 140 | 200 | not offered |
| Army, Liberals 60, Monarchists 40, Conservatives 30, Falange 20, government 100 | 190 | 250 | offered |

QA also confirmed that the other four bill counts and the two intentional `add_stability` calls in the agrarian concession are byte-identical to HEAD, and ran `hoi4.source_lookup`, `hoi4.event_inspect` (lint and trace) and `hoi4.script_validate` on the changed file.
No bill was brought and no option was clicked; no HOI4 launch was performed.

Residual items, queued to the Cortes audit S1: the decision gate compares the base against the 161-seat floor, so the Liberal concession is only reachable at base 161-200; `common/decisions/spain_cortes.txt:14` and `:170-171` still describe the Liberals as backing the budget and army bills; the pre-existing committed BOM in `common/national_focus/spain_restoration.txt` remains.

Campaign wave after the repair: S8 is designing the electoral law as a contestable bill against the corrected baseline; I0 is auditing Iran's repaired rewards read-only; C0 is reconciling the China master plan read-only.
No premium model was invoked.
