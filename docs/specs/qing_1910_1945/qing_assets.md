# Qing asset record

## Focus icons

All 238 focuses use sprites that already exist in the mod or in the installed game.
The families used:

| Family | Examples | Used for |
| --- | --- | --- |
| Waking the Tiger Chinese icons | `GFX_focus_CHI_lay_the_foundation_for_a_united_china`, `GFX_focus_CHI_the_northern_mandate`, `GFX_focus_CHI_guerrilla_warfare`, `GFX_focus_CHI_the_hump` | Chinese politics, provinces, army and war |
| Monarchist icons | `GFX_focus_generic_monarchy_1`, `GFX_focus_generic_monarchy_2`, `GFX_focus_PER_constitutional_monarchy`, `GFX_focus_BRA_constitutional_monarchy` | Court, constitution, routes |
| Industry and infrastructure | `GFX_focus_generic_industry_1` to `_3`, `GFX_focus_generic_railroad`, `GFX_focus_generic_military_industry` | Economy and projects |
| Military | `GFX_focus_chi_army_reform`, `GFX_focus_generic_military_academy`, `GFX_focus_CHI_air_force`, `GFX_focus_generic_navy_battleship2` | Army, air and river navy |
| Diplomacy | `GFX_focus_chi_british_cooperation`, `GFX_focus_chi_mission_to_germany`, `GFX_focus_chi_mission_to_the_us`, `GFX_focus_CHI_negotiate_the_nine_powers_treaty` | Foreign policy |
| First World War native set | `GFX_focus_ww1_pdx_native_auh_artillery_effort_1`, `GFX_focus_ww1_pdx_native_en1_r_parliamentary_settlement` | Doctrines and constitutional crisis |

Every reference was checked against the sprite definitions in `interface/**/*.gfx` in both the mod and the installed game.

## National spirits

Pictures reuse existing idea art: `CHI_cradle_of_civilization`, `AUS_habsburg_monarchy_restored`, `CHI_baojia_system`, `CHI_corruption_armed_forces`, `chi_warlord_integration`, `chi_army_corruption`, `CHI_hanyang`, `chi_whampoa_military_academy`, `CHI_bank_of_china`, `CHI_china_merchant_group`, `CHI_a_new_middle_kingdom`.

## Portraits and characters

| Character | Portrait source |
| --- | --- |
| Yuan Shikai | `gfx/leaders/RCH/Portrait_China_Yuan_Shikai.dds`, already shipped |
| Puyi | `GFX_portrait_MAN_aisin_gioro_puyi`, native sprite |
| Liang Qichao | `gfx/leaders/RCH/Portrait_China_Li_Yuanhong.dds` as a stand-in |

Liang Qichao uses a stand-in portrait and should be replaced with a sourced image before the feature is called visually complete.
Puyi as an adult ruler and Yuan Shikai as a long-lived regent both want bespoke portraits for the 1920s and 1930s, when the native art is a young man and a 1911 photograph respectively.

## Balance of power

Two native 72x88 side sprites are reused: `GFX_bop_ITA_king_vittorio_side` for the court and `GFX_bop_SWI_centralization_council_side` for the assembly.
Bespoke Qing side art would be better and is the first art task for a second pass.

## Bespoke art worth commissioning

1. Two balance side sprites: the throne and the assembly.
2. A Puyi adult portrait and a Yuan Shikai regent portrait.
3. A Liang Qichao portrait.
4. Four or five route emblems for the settlement events.
5. Focus icons for the imperial court and the banner establishment, which currently borrow generic monarchist art.
