# Hearts of Iron IV 1.19.4 compatibility

Updated on 29 October 2026 against the installed **Operation Postern 1.19.4.0 / a783** build. The repository descriptor and local development launcher entry now target `1.19.4`. The mod's own release number is unchanged.

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
