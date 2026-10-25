# Spain 1910-1945 — design

## What exists already

Spain in Endsieg has one focus tree, `spanish_focus` in `common/national_focus/spain.txt` (281 focuses, vanilla La Resistance content, selector requires `has_dlc = "La Resistance"`).
That tree begins in 1936 with `SPA_a_great_spain` and `SPR_the_popular_front`, so it is a civil-war and Franco-era tree.
`common/decisions/SPR.txt` (17,000 lines), `common/ideas/spain_nationalist.txt`, `common/ideas/spain_republic.txt` and `events/LAR_Spain.txt` all belong to the same 1936+ layer.
Every one of those decision categories is gated on `is_in_ww2`, which Endsieg defines as the date threshold 1936.

`history/countries/SPR - Spain.txt` already carries dated setup blocks for 1910, 1914, 1916, 1918, 1936, 1939, 1941, 1942, 1943, 1944, 1944.11 and 1945, and separate orders of battle per era.

The gap is 1910 to 1935.
`common/on_actions/endsieg_on_actions.txt` assigns `generic_focus_ww1` to every country without its own WWI tree, so a 1910 Spain currently plays the generic Great War tree with no Spanish politics, no Restoration, no Rif War and no Republic.

## Architecture

Spain's campaign is a sequence of chapters.
Each chapter is a separate focus tree with its own layout, and the chapter change is a scripted milestone rather than a silent date rollover.

| Chapter | Tree id | Window | Content |
| --- | --- | --- | --- |
| I Restoration | `spain_restoration_focus` | 1910 to 1923 | Crown against Cortes, caciquismo, Rif War, juntas de defensa, labour question, neutrality in the Great War |
| II Dictatorship | `spain_rivera_focus` | 1923 to 1930 | Pronunciamiento, suspension of the constitution, public works, Morocco victory, corporatism, fall of the dictatorship |
| III Republic | `spain_republic_focus` | 1931 to 1936 | Constituent Cortes, agrarian and military reform, church question, Catalan and Basque statutes, Asturias, Popular Front, the plot |
| IV Civil War | `spanish_focus` (existing) | 1936 to 1939 | Kept: the vanilla La Resistance tree is the civil-war chapter and 22,000 lines of existing script depends on it |
| V Nationalist Spain | `spanish_focus` (existing) | 1939 to 1945 | Kept; the regime's political identity is decided by the faction struggle system rather than a separate tree |
| V Republican Spain | `spain_republic_postwar_focus` | 1939 to 1945 | New: a Republican victory gets its own reconstruction and diplomacy chapter |

Tree selection happens in two places.
`on_startup` picks the correct chapter for the bookmark's date, in both the pre-1936 and post-1936 halves of the existing hook.
`spain_campaign_tick` (driven by `on_daily_SPR`) moves a campaign from one chapter to the next when the historical or political conditions are met, using `load_focus_tree` with `keep_completed = yes`.
Every transition fires a milestone event and a news event, applies a temporary national spirit, and writes a chapter flag.

## Systems

All six systems are script-level mechanics that work under every chapter, so earlier choices still matter after a tree change.

### Crown against Cortes

A native balance of power, `SPR_crown_and_cortes`, from the Restoration to the proclamation of the Republic.
Left side is the Crown, right side is the Cortes, five ranges from absolute crown rule to parliamentary sovereignty.
Ranges carry real modifiers (political power, stability, advisor cost, war support) and `on_activate` hooks that fire the crisis events.
Its decision category is attached to the balance of power, so the player acts on it from the balance panel rather than a separate menu.
The value persists into the dictatorship and the Republic as the recorded constitutional settlement.

### Military loyalty

`spain_military_loyalty`, 0 to 100, opening at 55.
Raised by pay, promotions, the Africanist cause and honours; lowered by reform, closures, defeats and political interference.
It drives three separate things: the coup pressure system, the number of garrisons that defect at the outbreak of the civil war (it writes vanilla's `SPA_garrison_control`), and whether the 1936 rising is a coup attempt or a full civil war.

### Coups

`spain_coup_pressure` accumulates while loyalty is low, stability is low and the government is at odds with the officer corps.
A coup attempt is drawn from a weighted pool in the daily tick and resolved by event with three responses: resist, concede or co-opt.
Outcomes are a failed pronunciamiento, a dictatorship, or a civil war, depending on loyalty, garrison control and which officers back the attempt.

### Rif War

A decision category and event chain from 1909 to 1927 covering the Melilla campaign, the Disaster of Annual, the withdrawal, the Alhucemas landing and the pacification.
It consumes manpower, equipment and political power, moves loyalty and stability, and unlocks Moroccan development and the Africanist officer corps.

### Civil-war regional control

During the war the tick records which of six regions each side holds: the north, Aragon, Catalonia, the Levante, Andalusia and the Meseta.
Holding a region grants its historical advantage through national spirits (Basque steel, Catalan industry, Andalusian manpower, the Madrid approaches).
The record survives the war and feeds the reconstruction chapter.

### Nationalist factional struggle

Four influences on the Nationalist side: Falange, Carlists, monarchists and the army.
Decisions and events shift them, `spain_nationalist_tension` measures the gap between the leading and second faction, and high tension produces the unification crisis, the Carlist merger dispute and the monarchist restoration pressure.
The leading faction decides the regime's national spirits and, at the extreme, its head of state.

### Second World War diplomacy

Leverage tracks for the Axis and the Allies, driven by trade, the Blue Division, Gibraltar, Operation Felix and wolfram exports.
The player negotiates with Germany, Italy, Britain and the United States, and the choices decide neutrality, non-belligerency, or entry.
Entry is expensive because a country that has just finished a civil war starts with reconstruction penalties.

### National development

Four persistent values: industry, agriculture, infrastructure and education, 0 to 12 each.
Focuses, decisions and reconstruction raise them; they gate later focus branches and swap three-tier national spirits at thresholds.
They persist across chapter changes, so a 1910 industrial programme is still visible in 1944.

## Bookmarks

`history/countries/SPR - Spain.txt` dated blocks stay authoritative for parties, leaders, technology, order of battle and starting ideas.
`spain_initialize_campaign` reads the start date and sets the variables, flags and balance-of-power value that the chapter expects, so a 1941 start does not inherit an empty 1910 state and a 1910 start does not inherit a finished civil war.

## Assets

Focus icons reuse existing sprites: `GFX_goal_*` generic goals and the vanilla focus icons of other tags.
Decision categories reuse `GFX_decision_category_generic_*` and the existing Spanish civil-war category art.
The balance of power defines two new side sprites in `interface/endsieg_spain_icons.gfx` that point at existing vanilla textures, so nothing is missing at runtime.
Custom Spanish icon art for the new chapters is listed as pending in `docs/spain_campaign.md`.
