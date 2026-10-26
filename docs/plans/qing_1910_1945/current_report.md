# Qing overhaul, current report

## What is implemented

| Surface | Content |
| --- | --- |
| Chapter one, `qing_ww1`, 1910–1918 | 88 focuses: shared reform trunk, four route settlements, economy, army, Beiyang command, diplomacy, provincial compact, revolution preparation, chapter convergence |
| Chapter two, `qing_interwar`, 1919–1935 | 85 focuses: four route trunks, industry, army, diplomacy, provincial administration, Manchurian crisis, Nationalist question |
| Chapter three, `qing_ww2`, 1936–1945 | 65 focuses: four route wartime governments, war economy, army, Allied diplomacy, fronts and victory |
| Events | 33 events, 76 options, namespace `qing_campaign` |
| Decisions | 38 decisions in five categories, including the balance-of-power family |
| Ideas | 11 national spirits in three slots |
| Balance of power | `QIN_throne_and_assembly`, six ranges, attached decision category |
| Characters | Yuan Shikai, Puyi, Liang Qichao |
| AI | Two focus-order plans, historical and constitutional |
| Localisation | Six English files, all focus, idea, decision, category, event and balance keys |
| Documentation | Spec, TFR study, asset record, this system doc |

## Route coverage

| Required route | Implemented route | Status | Notes |
| --- | --- | --- | --- |
| Constitutional Qing | `qing_settle_constitutional`, `QW1_constitutional_settlement` and four continuations, `QW2_constitutional_*`, `QW3_constitutional_*` | Implemented | Elections, cabinet responsibility, royal prerogative, constitutional court, wartime coalition |
| Authoritarian Qing | `qing_settle_authoritarian`, `QW1_autocratic_settlement` and four continuations, `QW2_authoritarian_*`, `QW3_authoritarian_*` | Implemented | Grand Council, censorate, banner reform, security bureau, court schools |
| Yuan Shikai protects the Qing | `qing_settle_yuan`, `QW1_yuan_premiership` and continuations, `QW2_yuan_*`, `QW3_yuan_*` | Implemented | Military government, officers' compact, succession crisis, unified command |
| Federal Qing | `qing_settle_federal`, `QW1_federal_settlement` and continuations, `QW2_federal_*`, `QW3_federal_*` | Implemented | Provincial charter, fiscal compact, regional armies, federal bank and police |
| Historical collapse | existing `ww1_china` chain, suppressed only by `qing_xinhai_settled` | Implemented | No existing event rewritten, only guarded |

## The revolution chain

| Step | Event | Condition |
| --- | --- | --- |
| Reform warning | `qing_campaign.2` | 1910, once |
| Railway Protection | `qing_campaign.10`, `.11` | 1911 summer |
| Negotiated survival | `qing_campaign.20` | reform 40, loyalty 50, trust 40 |
| Military settlement | `qing_campaign.22` | Beijing held, army 55, and reform 45 or Yuan 60 |
| Court council during war | `qing_campaign.23` | war with the Republic, Beijing held |
| Historical revolution | `ww1_china.3` and the provincial uprisings | `qing_xinhai_settled` not set |

Each settlement clears the other three route flags, sets its own, annexes the Republic, replaces the leader and refreshes the mechanics.
Survival is never tied to one focus: the gate is a combination of three values that focus rewards and decisions move separately.

## Static validation performed

- `check_tree_geometry.py`: 0 errors, 0 warnings on all three chapter files (duplicate ids, coordinates, row spacing, prerequisite direction, mutex sanity).
- `check_content_refs.py`: brace balance, duplicate ids, 642 required localisation keys present, icon references resolved.
- Custom audit: all 238 focus ids, 11 ideas, 38 decisions, 5 categories, 33 events and 76 options have localisation; every referenced event exists; every AI plan focus exists; every scripted effect and trigger call resolves.
- Icon audit against `interface/**/*.gfx` in the mod and the installed game: all focus, decision and idea sprites resolve.
- Token audit against the installed `effects_documentation.md` and `triggers_documentation.md`: `add_army_experience` was found to be an invalid effect name and replaced with `army_experience`, `air_experience` and `navy_experience`; integer-only fields now use literals.
- Brace balance of the three existing files touched: `events/WWI - Chinese Collection Events.txt`, `common/on_actions/endsieg_on_actions.txt`, `history/countries/QIN - Qing Empire.txt`.

## Engine defects found by the first launch and fixed

The first launch attempt logged:

- `Invalid key name at line 1 and column 1` for four localisation files, caused by a doubled BOM in the generator.
- `unexpected token ... near line: 1 ( Overview: )` for eight script files whose header comment had lost its leading `#`, which dropped the script constants, triggers, effects, ideas, characters, opinion modifiers and decisions, and therefore also the tree load.

Both causes are fixed and the localisation files now carry exactly one BOM.
That launch is the only engine run performed, and it did not reach a clean scenario with the tree, so it is not evidence that the tree loads.

## Pending

- A launch that reaches the 1910 scenario with QIN played, to confirm the tree appears, the values initialise, the balance panel exists, and the first events fire.
- A run through 1911 to confirm the negotiated and historical outcomes.
- A run to 1919 and 1936 to confirm the chapter swaps.
- In-game confirmation that `qing_xinhai_settled` suppresses the historical chain and that the unset case still collapses.
- Portrait and balance-of-power art noted in `qing_assets.md`.
