# Second brain (Obsidian vault)

This file documents the shared Obsidian vault that Hermes profiles on this machine use as their long-term project memory, and how it relates to this repository.
The repository stays canonical for code, tuning values and design acceptance; the vault indexes, summarizes and connects that material so a later session does not have to re-derive it.

## What it is

- Vault root: `C:/Users/Christopher/Documents/Obsidian/Second Brain`.
- Plain markdown notes with YAML frontmatter, linked with `[[wikilinks]]`, browsable in Obsidian.
- Shared by the Hermes profiles `default`, `endsieg` and `hoi4-gfx-art`; any other agent can be pointed at the same folder.
- It is not a source of truth for the mod and it is not part of this repository.

## Vault layout

| Path | Contents |
| --- | --- |
| `AGENTS.md` | The protocol every agent reads first: read before you work, write before you leave |
| `SCHEMA.md` | Frontmatter keys, Title Case filenames, wikilink and size rules |
| `Home.md` | Dashboard and entry point |
| `identity.md` | Who the maintainer is, how he gives instructions, the standing rules he set |
| `projects.md`, `tasks.md` | Live project index and open loops, kept current by agents |
| `00-Inbox/` | Unprocessed captures |
| `10-Daily/` | One `YYYY-MM-DD.md` per working day |
| `20-Projects/Endsieg/` | `Systems/`, `Countries/`, `Decisions/`, `How-tos/`, `Logs/` |
| `30-Areas/` | `Mod Pipeline`, `Art Pipeline`, `Hermes Tooling` |
| `40-Resources/` | Vanilla paths, reference mods, offline wiki snapshot, MCP routes, skills index |
| `50-Wiki/` | Concept and entity pages reused across projects |
| `90-Archive/` | Finished or superseded material, moved not deleted |

The Endsieg notes are compiled from `docs/systems/`, `docs/specs/` and the `docs/plans/*/current_report.md` files, and each note cites the repository path it came from.

## How it is wired into Hermes

| Piece | Where |
| --- | --- |
| `OBSIDIAN_VAULT_PATH`, `WIKI_PATH` | `.env` of each profile, so the variables resolve in a shell |
| `second-brain` skill | `skills/note-taking/second-brain/SKILL.md` in each of the three profiles; it names the vault, the layout and the read/write workflow |
| Memory entry | One line in each profile's `MEMORY.md` pointing at the vault and the skill |
| Weekly maintenance | Cron job `second_brain_weekly` on the `endsieg` profile, Sundays 09:00: link lint, stale-note listing, index refresh, daily log entry |

The weekly job works only inside the vault.
It never edits this repository, never runs git, and never launches Hearts of Iron IV.

## Read and write rules

Read `AGENTS.md` in the vault root before using it, and `SCHEMA.md` before writing.
In short:

- Read before you work, write before you leave.
- Search the vault before reading notes whole; never bulk-load it into context.
- Append and merge; never overwrite another agent's note; never delete, move to `90-Archive/`.
- Cite the source of every claim: repository path, commit, date or session.
- No secrets, tokens, credentials, long file dumps or generated filler.

## What belongs where

- A mechanic that exists in the mod: a note in `20-Projects/Endsieg/Systems/`.
- A country package and its real status: `20-Projects/Endsieg/Countries/`.
- Why the code is the way it is, with the rejected alternative: `20-Projects/Endsieg/Decisions/`.
- A procedure an agent must follow: `20-Projects/Endsieg/How-tos/`.
- What a session changed: `20-Projects/Endsieg/Logs/YYYY-MM-DD.md`, with the headings asked, changed, verified, open.
- Anything that must stay authoritative for gameplay: this repository, as before.

A vault note is not design approval.
Acceptance still lives in `docs/specs/`, dispositions in `docs/plans/`.

## Boundaries with the shared checkout

Another AI works in the same checkout on parallel content.
Its uncommitted work is read-only for the vault: it is never summarized as ours, and the vault never records a working-tree state as an authored change.

## Not covered yet

- No pointer to the vault exists in `CLAUDE.md` or `AGENTS.md`, so non-Hermes runtimes (Claude Code, Codex, Cursor) do not learn about it from the project instructions. The path is in each Hermes profile's memory and in the `second-brain` skill instead.
- The vault carries no copy of player-facing text, tuning constants or focus ids beyond what a summary needs; those stay in the repository.

## Needed assets

None.
The vault uses Obsidian's own interface and no custom sprites, GFX definitions or localisation keys.
