# Vanilla state restoration

The affected legacy state files and the newer vanilla state files were copied
byte-for-byte from the installed Hearts of Iron IV `history/states` directory.
The restored legacy IDs are `284`, `286`, `289`, `523`, `635`, `670`, `674`,
`723`, `741`, `976`, `998`, and `1031`; the restored new IDs are `1066` through
`1081`.

All 1,081 state definitions now have unique IDs. Restoring the legacy vanilla
files exposed 44 duplicate province claims in overlapping custom state files.
Those province entries were removed from the overlapping custom states, leaving
one state owner per listed province.

Map state-indexed rows were aligned with the restored vanilla state IDs in
`map/buildings.txt` and `map/weatherpositions.txt`. `map/airports.txt` and
`map/rocketsites.txt` retain their original state keys. The first field in
`map/unitstacks.txt` is province-indexed and was left unchanged.

Static checks confirm that every state file is balanced, every listed province
has a single owner, and all restored state files match the installed vanilla
files byte-for-byte.

The follow-up vanilla alignment also restored states 18, 28, and 785, moved custom-map-only province entries into their matching vanilla geographic states, corrected all map-building state keys against the province bitmap, and aligned the affected strategic-region memberships with vanilla.
