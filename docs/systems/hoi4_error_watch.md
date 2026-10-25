# Hourly HOI4 error watch

A cron job launches Hearts of Iron IV on an idle machine once an hour, captures the fresh error log, and hands a grouped report to an agent that repairs the Endsieg-owned errors.
It exists because load-time and gameplay errors only appear in `error.log` after a real launch, and nobody launches the game every hour by hand.

## Ownership

| Part | Location |
| --- | --- |
| Hermes cron job | profile `endsieg`, job `endsieg_hoi4_error_watch` (id `c56c05fb5008`, schedule `every 60m`, delivery `origin` = the chat it was created from) |
| Pre-run script | `%LOCALAPPDATA%\hermes\profiles\endsieg\scripts\hoi4_error_watch.py` |
| Run artifacts | `<mod>\.tmp\hoi4_error_watch\` (gitignored) |
| Game logs read | `Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` and `setup.log` |

Cron only runs scripts that live under the profile's `scripts\` directory, so the script is not in the repository and must not be moved into `.tools\`.
The job's working directory is the mod root, which is also where the script resolves `.tmp\hoi4_error_watch\`.

## Flow

1. The scheduler fires the job every hour.
2. The pre-run script reads the idle time of the interactive session with `GetLastInputInfo`.
3. If the user touched the keyboard or mouse inside ten minutes, the script prints `{"wakeAgent": false}` as its last line.
   Cron then skips both the agent run and the chat message, so a busy machine costs nothing and produces no noise.
4. If Hearts of Iron IV is already running and the machine is idle, the script reads the live session's `error.log` without touching the process.
   A live capture whose grouped errors are identical to the previous capture is silent.
5. If Hearts of Iron IV is not running and the machine is idle, the script starts `hoi4.exe` from the Steam directory with the current playset.
   It waits until `error.log` and `setup.log` have been quiet for a while (at least two minutes, at most ten), then snapshots both logs and any new crash folder.
6. The script closes the process it started, unless keyboard or mouse input arrived during the capture.
   In that case the game is left running and the report says so; the script never closes a game the user may be using.
7. The script groups the error lines, writes `report_latest.md`, `error_latest.log`, `error_previous.log`, `setup_latest.log` and `state.json`, and prints a compact summary with the report paths.
8. The agent reads the report, attributes every group to Endsieg, the vanilla engine or another mod, and fixes the Endsieg ones.
9. The agent's final message is the chat report: capture mode, line and group counts, what it fixed, what it left open and why, and the five highest-count groups verbatim.

## Verdicts

| Verdict | Meaning | Wakes the agent |
| --- | --- | --- |
| `skipped_user_active` | the machine was in use, nothing launched | no |
| `skipped_user_active_game_running` | a game is running and the user is present | no |
| `skipped_live_unchanged` | the running game's log matches the previous capture | no |
| `captured` | launched, captured, closed | yes |
| `captured_live` | read the log of an already running, idle game | yes |
| `crashed_on_startup` | the launch produced a new crash folder | yes |
| `skipped_no_game_dir`, `skipped_no_logs`, `skipped_game_exited`, `skipped_launch_failed` | setup problem; reported in chat | yes |

## Agent contract

- Only Endsieg-owned errors are edited; vanilla, launcher and other-mod messages are reported and left alone.
- Errors are never silenced by deleting content, disabling a feature or adding an unapproved placeholder.
- Fixes follow `AGENTS.md`, `CLAUDE.md` and the matching HOI4 skill for the subsystem being edited, with localisation updated in the same change.
- The run does not commit, stash or revert, and it does not launch, restart or close the game itself; the next hourly capture verifies the fix.

## Operating the job

- Pause: ask for it, or run `hermes cron pause endsieg_hoi4_error_watch`.
- Resume: `hermes cron resume endsieg_hoi4_error_watch`.
- Fire now: `hermes cron run endsieg_hoi4_error_watch`.
- Inspect the last runs: `<profile>\cron\output\c56c05fb5008\`.
- Dry run of the script without launching anything:
  `python "%LOCALAPPDATA%\hermes\profiles\endsieg\scripts\hoi4_error_watch.py" --dry-run --force-idle`
- Tuning environment overrides: `HOI4_WATCH_IDLE_S` (idle gate, default 600), `HOI4_WATCH_GAME_DIR`, `HOI4_WATCH_USER_DIR`, `HOI4_WATCH_STATE_DIR`, `HOI4_WATCH_MOD_ROOT`, `HOI4_WATCH_DEBUG=1` to launch with `-debug`.

## Interactions and limits

- The script launches `hoi4.exe` directly; it does not use the HOI4 Live Tools server, so the two never compete for the game.
  The playset comes from `dlc_load.json`, which the script never writes.
- A launch steals focus for the seconds it runs, which is why the idle gate exists; it cannot detect someone watching a video without touching the keyboard.
- A locked workstation does not block the capture, but a graphics failure under lock is a machine condition, not a mod defect, and the report says which case occurred.
- The script snapshots and reports; it never edits mod content, so a broken watcher can never damage the tree.
- Because the script closes the game it launched, the user's own session and saves are untouched; only a game the script started is ever closed.

## Future plans

- Spread the grouped-error diff against the previous hour into the chat report so an unchanged log is obvious at a glance.
- Add a nightly roll-up that summarises the day's fixes and remaining groups.
- Optionally drive the HOI4 Live Tools server for a main-menu screenshot when a launch looks wrong.

## Icons and assets

None.
The feature is invisible in game and renders only as a chat message, so no sprites, `.gfx` entries or localisation keys are involved.
