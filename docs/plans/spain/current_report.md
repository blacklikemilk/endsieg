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
- No scripted GUI for the Crown and Cortes panel or the regional control map.
- No achievements.
- Sanjurjo, Companys, Durruti, Gil Robles and Miguel Primo de Rivera appear in text but have no character definitions or portraits.
- Britain's and Germany's AI do not yet react specifically to Spanish leverage; the pressure exists on the Spanish side only.
