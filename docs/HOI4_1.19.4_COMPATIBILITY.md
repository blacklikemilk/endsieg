# Hearts of Iron IV 1.19.4 compatibility

Updated on 29 October 2026 against the installed **Operation Postern 1.19.4.1 / f584** hotfix (Steam build 26282552). The repository descriptor and local development launcher entry target the `1.19.4` patch family. The mod's own release number is unchanged.

## October 29 hotfix follow-up

Paradox's hotfix addresses multiplayer disconnections, the focus minimap at different UI scales, the unit-leader trait window, and focus/decision conditions involving annexed countries. The compatibility checker now verifies the installed `1.19.4.1` build.

A fresh startup log also exposed remaining integration errors. This follow-up:

- Restores 18 current vanilla trade labels, including the two numeric factory counters whose missing keys wrapped down across the resource table, and updates the import-factory tooltip.
- Uses `game:scope` and the native `faction_members` operator for the two WW1 membership collections.
- Restores the native privacy-eye and three-state checkbox sprites in the existing GFX overrides.
- Supplies missing autonomy/peace-conference triggers and the New Guard marker used by inherited vanilla scripts. The Indochina trigger uses Endsieg's own state boundaries. Nation-selection previews reuse the existing display spirits through aliases.
- Converts rejected scripted-effect argument blocks to native country scopes or temporary argument variables for Chinese reunification, Spanish government formation and the super-event helper. Existing effect IDs and argument values are retained.
- Converts 57 AI score constants to their declared numeric values, corrects two invalid modifier names, and charges the Republic rescue's existing 200 PP entry price through its completion effect because mission `cost` is unsupported.
- Corrects the election stability threshold to 0.60, scopes the Belgian occupation checks through Germany's controlled states, and removes ten nonexistent technology grants from Galicia while translating its legacy ideology groups to the mod's four supported groups.

The expanded structural check passes across 1,292 script files. The trade strings, native sprites, helper references and preserved AI scores receive separate integration checks in this checkout. These results require an in-game restart to verify; the saved startup log predates the fixes. Ignored air-base `include_locked` warnings and invalid descriptors belonging to unrelated Workshop mods are outside this patch.

## Changes

- Restored the native repair-priority interface, automatic-import budget/priorities and current technology detail lists in the mod's overrides. Existing construction allocation controls, WW1 technology layouts, main-menu art and scenario presentation were preserved.
- Corrected two faction collection inputs to use the actual native member collection.
- Moved date/focus-tree conditions from persistent decision/AI-plan `allowed` blocks to runtime visibility/enabling conditions. WWII Mexican plans also stop when their tree is no longer active.
- Replaced unsupported political-power comparisons with the current `has_political_power` trigger, including German replies to Mexican counteroffers.
- Registered six Mexican identities dormant in early country history. Runtime effects activate their leader roles instead of attempting recruitment during play. Existing portraits, characters and political routes remain in use.
- Moved six French advisor roles into the character database, retaining their traits, original-country conditions and lifecycle gates. Retirement deactivates hired advisors without destroying their reusable database roles.
- Repaired one German and nineteen Japanese dated-history conditionals using the native nested history form, preserving both branch bodies.
- Matched native No Compromise, No Surrender recruitment ownership for six Chinese commanders; the original recruitment remains available without that DLC.
- Restricted modern Siam startup initialization to WWII-era starts and guarded its two character references.

The mod inherits the current native doctrine files, including Operations/cavalry mastery changes. Optional tank-stat balance changes were not imposed on Endsieg's equipment. The native focus minimap, advisor filters, diplomatic automation and agency-upgrade queue are inherited where the mod has no override.

## Verification

The latest existing local error log provided concrete failures. These changes were compared with the installed game's definitions and documentation. The known-rejection checks passed across 852 script files; exact AST/subtree comparisons verified preserved history branches and custom UI content. Added interface sprites, textures and localization references were checked. The Mexican focus graph, focus text and icon assets were preserved.

Run the repeatable structural check from the mod directory:

```console
python tools/validate_1194_compatibility.py --game "PATH/TO/Hearts of Iron IV"
```

The checker uses only Python's standard library. It detects the known persistent-trigger, political-power, collection, runtime-character/advisor and dated-history regressions; it is not the game parser. The existing `tools/check_linux_paths.py` remains the filename/case audit.

HOI4 was not launched during this update. Fresh in-game checks are still required for UI interaction, scenario starts, AI pacing and save behavior. The previous log remains a pre-fix record. Its two invalid-version warnings concern unrelated workshop descriptors and were not changed. New Mexican identity registration applies when country history is initialized for a new campaign.

## Sources

- [Paradox's official Steam patch notes](https://steamcommunity.com/app/394360/allnews/?l=english), “Hearts of Iron IV | QoL Patch Notes 1.19.4”, 27 October 2026.
- Installed `launcher-settings.json`, `common/collections/generic_collections.txt`, native country histories, native construction/trade/technology interface files and generated trigger/effect documentation.

Detailed before/after snapshots and validation reports for this development checkout are stored in `work/hoi4_1194` in the Codex workspace.
