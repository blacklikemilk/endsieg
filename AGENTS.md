# Endsieg Codex Instructions

## Project
This repository is the Hearts of Iron IV mod Endsieg. The active development target for this setup is `sanaa_branch`.

## Primary goal
Preserve Endsieg's intended content and presentation while keeping it compatible with the current Hearts of Iron IV version. Prefer narrow compatibility fixes over broad rewrites.

## Working rules
- Read the relevant existing mod files before editing them.
- For engine-facing structures, compare with the locally installed current vanilla Hearts of Iron IV files whenever available.
- Treat current vanilla syntax and required definitions as the compatibility baseline, but do not overwrite intentional Endsieg mechanics merely because vanilla differs.
- Preserve namespaces, IDs, event chains, focus IDs, country tags, localisation keys and asset names unless a change is required to fix a confirmed problem.
- Do not remove working historical or scenario content as a shortcut for compatibility.
- Do not launch Hearts of Iron IV automatically. The user owns live playtesting.
- Never claim a crash is fixed solely because a text search or syntax check passes.
- When an error.log or game.log is available, start from the concrete errors and trace each relevant reference back to the mod.
- Check for cascading errors: an early missing definition can cause many later messages.
- Avoid unrelated formatting or cleanup in bug-fix commits.

## Vanilla comparison
When vanilla files are locally available, locate the current Hearts of Iron IV installation rather than assuming a hard-coded path. Compare the exact corresponding vanilla file or nearest current implementation. Pay special attention to definitions that changed between HOI4 versions.

For scenario-start crashes, prioritize:
1. parser and missing-content errors from logs,
2. obsolete or missing common definitions,
3. history/state/country references,
4. technologies, equipment and units,
5. scripted effects/triggers and on_actions,
6. interface/GFX only when the failure points there.

## Interface safety
The `interface/` and related `gfx/` content is visually sensitive. Before replacing a vanilla-derived `.gui` or `.gfx` structure, identify exactly which custom Endsieg elements require an override. Prefer the smallest override possible. Preserve custom main-menu art positioning and scenario-selection presentation unless the task explicitly changes them.

## Resources
Do not introduce custom strategic resources or resource-related UI merely to satisfy old references. If obsolete custom resources are encountered, first determine whether they are still intentionally used by gameplay. Remove dead references consistently across common, map/history, localisation and interface rather than leaving partial definitions.

## Agent routing
Use `hoi4_repo_explorer` for large or uncertain changes where the relevant files are not yet known.
Use `hoi4_compatibility_debugger` for version updates, startup/scenario crashes, missing-content errors and vanilla comparisons.
Use `hoi4_script_auditor` for bounded script errors in common/events/history/focus/decision content.
Use `hoi4_interface_debugger` for scenario interface, main-menu wallpaper, `.gui`, `.gfx`, sprites and other presentation regressions.

Agents should receive explicit task context and paths. Do not assume a subagent can see prior conversation context.

## Validation
After edits, perform the strongest available non-launch validation: targeted searches for unresolved IDs, duplicate definitions, missing referenced files, brace/syntax checks where reliable, localisation-reference checks and comparison against the current vanilla construct. Report what was checked and what still requires an in-game test.
