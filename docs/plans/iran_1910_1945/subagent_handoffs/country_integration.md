# Iran country integration handoff

## Disposition

Implemented the assigned country-integration patch without changing other country packages.
No design simplifications were made.
No game launch, commit, workshop write, portrait change or secret access was performed.

## Owned files and exact changes

- `common/on_actions/endsieg_on_actions.txt:212–215` adds the pre-1936 `tag = PER` arm immediately before the generic fallback and calls `iran_initialize_campaign = yes`.
- `common/on_actions/endsieg_on_actions.txt:399–402` replaces the post-1936 PER arm's `persian_focus_tree` load with the same no-parameter helper call.
- `common/on_actions/endsieg_on_actions.txt:1435` adds `tag = PER` to the daily generic-tree fallback exclusion list.
- `history/countries/PER - Persia.txt` removes 49 old focus completion commands, comprising 12 `PER_*` and 37 `shared_*` completions.
- `events/WWI - Persia.txt` adds `NOT = { has_country_flag = iran_campaign_active }` to the triggers of `persia.1`, `persia.2` and `persia.4`.
- `common/characters/PER_restored.txt` replaces the two `has_completed_focus = PER_codify_the_state` visibility gates with `has_country_flag = iran_civil_service` for `PER_arthur_millspaugh` and `PER_ali_akbar_davar`, and updates the corresponding header comment.

No `on_daily_PER` hook or `iran_campaign_tick` call was added.
Millspaugh retains the exact additional visibility condition `has_country_flag = PER_treasury_reformed`.
Other characters, character roles, traits, portraits and availability conditions are unchanged.
Country history recruitment, politics, forces, technologies, economy, faction setup and the nine non-prefixed 1939 generic focus completions are unchanged.
The obsolete history completion wrappers and temporary `PER_history_start` set/clear pairs remain, as requested by the narrow command-removal scope.

## Source validation

A Python assertion pass compared all four files against their tracked baseline.
It returned the following results:

```json
{
  "history_removed_completions": 49,
  "removed_PER": 12,
  "removed_shared": 37,
  "history_remaining_other_completions": [
    "army_effort", "equipment_effort", "motorization_effort",
    "aviation_effort", "naval_effort", "flexible_navy",
    "industrial_effort", "construction_effort", "production_effort"
  ],
  "history_other_nonblank_lines_unchanged": true,
  "legacy_events_exactly_guard_only": ["persia.1", "persia.2", "persia.4"],
  "advisor_other_definitions_unchanged": true,
  "startup_helper_calls": 2,
  "added_tick_calls": 0,
  "brace_checks": "4 files passed"
}
```

The event comparison proves that removing only the three added trigger lines restores the complete original event file, including IDs, options, MTTH and the commented `persia.3` block.
The character comparison proves that, apart from the header comment, substituting the two intended gates restores the complete original file.
The history comparison proves all remaining nonblank lines are unchanged after removing the requested focus completion commands.
Targeted `git diff --check` returned success.
The assertion script is temporary and outside the repository at `C:/Users/Christopher/AppData/Local/hermes/profiles/endsieg/cache/scratch/iran_country_integration_check.py`.

## References consulted

- `paradox_wiki/On actions - Hearts of Iron 4 Wiki.md:91–112` documents startup's default none scope, explicit country scoping and the country-specific daily hook.
- Installed `common/on_actions/00_on_actions.txt:1–6,243–245,1633–1638` supplies current vanilla startup/effect and country-specific daily precedents.
- Installed `documentation/triggers_documentation.md:3624–3637` confirms country-scoped `has_country_flag` syntax.
- Installed `common/characters/PER.txt:475–494,610–627` supplies the existing Millspaugh and Davar advisor/visibility structure.
- `paradox_wiki/Character modding - Hearts of Iron 4 Wiki.md:507` recommends declarative advisor visibility triggers for characters hidden at startup.
- `common/scripted_effects/iran_campaign.txt:26–85`, read only, already defines the parent's idempotent initializer, activation flag, civil-service late-start flag and the 1919/1936 chapter router.

Skills consulted: `hoi4-events`, `hoi4-characters-leaders` and the project `hoi4-subagents` and `hoi4-focus-trees` guidance.
No general skill change was needed for this bounded patch.

## Remaining integration risks and unavailable checks

MCP source inspection, render, comparison and script-validation evidence remains unavailable under the parent's existing `WORKSPACE_CONTEXT_REQUIRED` followed by `FOCUS_SOURCE_NOT_FOUND` failure record in `current_report.md:33–41`.
Its retry budget was already exhausted and was not repeated.
These are source-level assertions, not engine or rendered evidence.
No probability weights or MTTH values changed.

The parent still owns the dedicated `on_daily_PER` hook, final helper integration and complete package validation.
At inspection time the initializer sets `iran_civil_service` after 1925 but does not set `PER_treasury_reformed` in the viewed startup body, so Millspaugh remains hidden until the retained treasury flag is supplied by the parent-owned package.
This flag was deliberately preserved rather than silently renamed or removed.
Other legacy advisor focus gates remain unchanged under the explicit instruction not to alter unrelated characters.
Map, state, flag assets, military setup and technologies were preserved rather than independently redesigned or audited.
