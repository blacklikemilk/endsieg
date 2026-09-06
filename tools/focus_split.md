# Scenario focus trees

`common/national_focus/WWI - *.txt` contains the Endsieg trees for Austria-Hungary,
France, Germany, Italy, the Russian Empire, Turkey, the United Kingdom and the
United States (the existing `USC` tag), plus the generic early-scenario tree.
The existing shared branches and Russian Civil War trees are retained.

Before 1936, national Endsieg trees score 20,000 and the generic Endsieg tree
scores 10,000. These exceed the installed vanilla trees' selection scores,
including DLC variants. From 1936 onward these early trees score zero, leaving
vanilla's own country and DLC selection intact. The pre-1936 boundary also
preserves interwar content; it covers all 1910–1918 bookmarks. This selects a
tree when the engine assigns one, rather than forcing a campaign to switch trees
when its calendar reaches 1936.

The 81 files listed in `focus_split_manifest.json` are unmodified copies of the
installed vanilla national-focus directory. Superseded `WWII -` and mixed
`WWI + WWII -` sources have been removed. The placeholder compatibility tree has
also been removed because vanilla now supplies every one of its focus IDs.

Only six tree IDs collided: `french_focus`, `german_focus`, `italian_focus`,
`turkish_focus`, `british_focus` and `generic_focus`. Their WW1 versions have an
`_ww1` suffix. None of the 853 retained national WW1 focus IDs collide with
vanilla, so their IDs, bodies, prerequisites, rewards and localisation keys are
unchanged. The generic WW1 tree uses the existing shared branches; its former
direct WW2 focuses now come from vanilla's separate generic tree.
Four existing stray trailing braces in the WW1 shared air, army, navy and
political files were removed; their focus definitions are unchanged.

Run static validation from the repository root:

```powershell
python tools/validate_focus_split.py
```

Optionally pass `--vanilla` with the installed `common/national_focus` directory
to compare every copied file directly. The manifest records the copied files'
SHA-256 hashes and preserved national WW1 focus IDs. When intentionally updating
vanilla, update those hashes after reviewing the new files and selection scores.

In-game validation remains necessary: open each WW1 bookmark, check a custom
nation and a generic nation, then check WW2 nations with the enabled DLC set.
Also exercise civil-war tree changes and inspect the game logs. Copying focus
files does not by itself validate all supporting events, ideas, technologies or
scripted effects used by the current vanilla game. Do not launch the game from
the validation script.
