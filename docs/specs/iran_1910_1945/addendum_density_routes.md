> **Superseded (icons):** the user rejected the painted `GFX_iran_focus_*` illustration set. Any recommendation below to use, register or generate those sprites is void; Iran focus icons stay vanilla/DLC-style (see `docs/plans/iran_1910_1945/icon_policy.md`).

# Iran density and route addendum

## Purpose

This addendum records the expansion of Iran's three era chapters from a working skeleton into the delivered content set, and it is the route-coverage evidence required before any completion claim.

## Chapter architecture

| Chapter | Tree id | Window | Focuses | Loaded by |
| --- | --- | --- | --- | --- |
| Constitutional Persia and the Great War | `iran_ww1` | before 1919.1.1 | 85 | `iran_initialize_campaign` at startup, `iran_route_chapter` on the daily PER tick |
| The Interwar Settlement | `iran_interwar` | 1919.1.1 - 1935.12.31 | 129 | `iran_route_chapter` |
| Iran and the Second World War | `iran_ww2` | 1936.1.1 onward | 93 | `iran_route_chapter` |

Transitions use `load_focus_tree = { tree = ... keep_completed = yes }` plus `mark_focus_tree_layout_dirty`.
Persistent state lives in country variables and flags, so a chapter swap keeps authority, foreign leverage, the chosen settlement and completed projects.

## Layout

Politics occupies the centre column (`x = 15`), the treasury and development wing sits at `x = 3`, the army wing at `x = 30`, foreign policy at `x = 42`, and regional ambition at `x = 52`.
Each wing is a set of short sibling chains rather than one vertical ladder.
The interwar political centre opens one opening trunk, one 1921 crisis row and then a single fan of six settlement focuses at `y = 10`; every continuation branch sits directly below its own settlement and is hidden by `allow_branch` when another settlement is chosen.
The wartime chapter repeats that shape at `y = 12`-`y = 15` for the six regime continuations.

No two focuses share a coordinate in any chapter (verified by script), and sibling spacing is three units in the settlement rows.

## Political route coverage

| Required route | Implemented route or focus branch | Status | Notes |
| --- | --- | --- | --- |
| Qajar constitutional monarchy | `IR2_constitutional_crown` plus seven continuation focuses, `IR3_constitutional_wartime` branch | Implemented | Keeps Ahmad Shah under a parliamentary settlement; elections allowed |
| Qajar royalist restoration | `IR2_qajar_restoration` plus seven continuation focuses, `IR3_court_wartime` branch | Implemented | Requires court or palace-guard groundwork in the WW1 chapter; non-elective |
| Historical Pahlavi | `IR2_pahlavi_settlement`, `IR3_mohammad_reza`, `IR3_pahlavi_progress` branch | Implemented | Requires the Cossack or Reza Khan flags, matching the historical sequence |
| Alternative Pahlavi | Same settlement with the secular-courts, tribal-disarmament and state-enterprise variants plus the wartime non-historical options | Implemented | Different policy mix, same dynasty; the 1941 succession is conditional on the dynasty still ruling |
| Constitutional republic | `IR2_parliamentary_republic` plus seven continuation focuses, `IR3_republic_wartime` | Implemented | Requires the provincial compact and treasury reform from the decisions layer |
| Socialist and communist Iran | `IR2_gilan_republic` -> `IR2_jangali_congress` -> `IR2_soviet_accord` -> `IR2_socialist_congress` support track, `IR2_socialist_republic` settlement, `IR3_workers_war_effort` branch | Implemented | Support variable gates the settlement; the Gilan movement is the historical basis |
| Nationalist Iran | `IR2_nationalist_movement` -> press -> officers, `IR2_nationalist_front` settlement, `IR3_national_mobilisation` branch | Implemented | Separate from the Pahlavi route; oil sovereignty is its payoff |
| Regional and decentralised alternatives | `IR2_provincial_compacts_ii`, tribal settlement decisions, `IR3_provincial_compacts` | Implemented | A policy family rather than a seventh government; lowers central authority and trades it for manpower and stability |
| Greater Iranian regional ambition | `IR2_regional_ambitions` branch (Caucasus, Mesopotamia, Gulf, Afghanistan, Caspian) plus `IR2_gulf_islands` | Implemented | Diplomatic pressure and influence first; no free territorial cores |

## Focused route locks

Each settlement is mutually exclusive with the other five, and every continuation focus carries `allow_branch = { has_country_flag = <settlement> }` so only the chosen branch is drawn.
Settlement effects call `iran_settle_*` scripted effects, which set the ruling party, promote the historical leader where a character exists, add the matching institution spirit through `iran_refresh_mechanics`, and refresh the layout.

## Interlocking mechanics

| Mechanic | Values | Presentation |
| --- | --- | --- |
| State authority | `iran_authority` 0-100 | Decision category header text, institution spirit tier at 50 |
| Foreign leverage | `iran_foreign_leverage` 0-100 | Decision category header text, `iran_foreign_dependence` spirit at 50 |
| Socialist support | `iran_socialist_support` 0-100 | Custom focus tooltip on the settlement, Gilan chain |
| Institutions | `iran_fragmented_authority`, `iran_constitutional_state`, `iran_pahlavi_state`, `iran_parliamentary_state`, `iran_qajar_state`, `iran_socialist_state`, `iran_nationalist_state` | National spirit tooltips |
| Emergencies | `iran_foreign_dependence`, `iran_supply_emergency` | National spirit tooltips |

All tuning values live in `common/script_constants/iran_campaign.txt` as `constant:iran_story.*`.

## Decisions

| Category | Decisions | Purpose |
| --- | --- | --- |
| `iran_state_authority` | 6 | Provincial compact, treasury reform, gendarmerie equipment, bread distribution, constitutional petitions, provincial security |
| `iran_national_projects` | 11 | Paid, one-time construction with ownership and control checks and cancellation |
| `iran_sovereignty` | 7 | Credit repayment, Shatt al-Arab, Gulf commission, regional assurances, corridor deliveries, withdrawal guarantees, northern administration |
| `iran_political_course` | 6 | Route-specific government work: court appointments, Majlis session, army review, free assembly, republican referendum, court reform |
| `iran_wartime_emergency` | 5 | Rationing, black-market crackdown, civil-defence drills, refugee shelters, underground press |
| `iran_tribal_settlement` | 4 | Tribal negotiation, punitive expedition, tribal regiment, frontier subsidy |

Repeated actions use `days_re_enable`; one-time works use `fire_only_once`; projects that depend on territory cancel cleanly when the state is lost.

## Events

`events/iran_campaign.txt` carries the `iran_campaign` namespace: the constitutional opening (10-19), the chapter transitions (20-30), the interwar crisis and settlements (31-39, 50-56), and the wartime crisis, corridor and settlement chain (40-44, 60-64).
Every option has an `ai_chance`; effects are conditional on the government that actually exists, so a republican Iran never receives Pahlavi abdication text as its own.

## Asset requirement list

Focus icons are drawn from a single Iran-specific family in `gfx/interface/goals/iran_campaign/` and registered in `interface/iran_campaign.gfx`:

| Sprite | Subject |
| --- | --- |
| `GFX_iran_focus_majlis` | Majlis chamber |
| `GFX_iran_focus_constitution` | Constitutional document and seal |
| `GFX_iran_focus_qajar_court` | Qajar court and throne |
| `GFX_iran_focus_crown` | Qajar crown and lion-and-sun |
| `GFX_iran_focus_ahmad_shah` | Ahmad Shah |
| `GFX_iran_focus_royal_council` | Council of ministers |
| `GFX_iran_focus_anjoman` | Provincial assembly |
| `GFX_iran_focus_press` | Printing press and newspapers |
| `GFX_iran_focus_law` | Scales and court of justice |
| `GFX_iran_focus_diplomacy` | Envoy with treaty folio |
| `GFX_iran_focus_treaty` | Signed treaty and seals |
| `GFX_iran_focus_treasury` | Empty strongbox and ledgers |
| `GFX_iran_focus_finance` | Financial adviser |
| `GFX_iran_focus_customs` | Customs house |
| `GFX_iran_focus_advisor` | Foreign adviser |
| `GFX_iran_focus_bank` | Bank and coin stacks |
| `GFX_iran_focus_budget` | Budget ledgers |
| `GFX_iran_focus_telegraph` | Telegraph line |
| `GFX_iran_focus_road` | Mountain road |
| `GFX_iran_focus_port` | Gulf harbour |
| `GFX_iran_focus_harvest` | Harvest |
| `GFX_iran_focus_granary` | Granary stores |
| `GFX_iran_focus_oil` | Oil derrick |
| `GFX_iran_focus_concession` | Concession contract |
| `GFX_iran_focus_workshops` | Bazaar workshops |
| `GFX_iran_focus_famine` | Relief queue |
| `GFX_iran_focus_requisition` | Grain requisition |
| `GFX_iran_focus_relief` | Relief column |
| `GFX_iran_focus_army` | Troops on parade |
| `GFX_iran_focus_gendarmerie` | Gendarmerie patrol |
| `GFX_iran_focus_cossack` | Cossack cavalryman |
| `GFX_iran_focus_recruitment` | Recruiting sergeants |
| `GFX_iran_focus_pay` | Paymaster |
| `GFX_iran_focus_officers` | Officer academy |
| `GFX_iran_focus_rifles` | Stacked rifles |
| `GFX_iran_focus_arsenal` | Arms workshop |
| `GFX_iran_focus_fort` | Frontier fort |
| `GFX_iran_focus_mobilization` | Mobilising column |
| `GFX_iran_focus_resistance` | Partisan irregulars |
| `GFX_iran_focus_law` | Occupation administration reuses the law icon |
| `GFX_iran_focus_air` | Early biplane |
| `GFX_iran_focus_navy` | Gulf gunboat |
| `GFX_iran_focus_neutrality` | Frontier sentry |
| `GFX_iran_focus_british` | British residency |
| `GFX_iran_focus_german` | German envoy |
| `GFX_iran_focus_russian` | Russian consul |
| `GFX_iran_focus_ottoman` | Ottoman frontier post |
| `GFX_iran_focus_tribal_pact` | Tribal chiefs and officer |

## Future plans

- Chapter-specific continuous-focus palettes for each settlement.
- A balance-of-power window for crown against Majlis, replacing the flag-level settlement once the visual asset family exists.
- Post-1945 continuation (Azerbaijan crisis resolution and the oil nationalisation road) if the mod extends the campaign end date.
