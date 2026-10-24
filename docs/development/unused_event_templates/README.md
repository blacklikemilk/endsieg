# Unused event templates

`WWI - Default.txt` is retained here as a development reference. Its fifty
`ww1_default.1` through `ww1_default.50` IDs are reserved; do not reuse them.

These events are nonfunctional placeholders: all are triggered-only, have no
automatic triggers, and contain only an empty named option. A scan of the active
mod scripts and localisation found no gameplay callers, namespace dispatches or
localisation references. Keeping the original file outside `events/` prevents
the game from loading unfinished definitions while preserving its exact bytes.

This archive does not supply playable historical content. If development of
these IDs resumes, restore the file to `events/`, add complete event effects,
localisation and artwork, and validate every new caller before release.
