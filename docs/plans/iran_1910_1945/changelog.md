# Iran 1910–1945 — development changelog

Newest batch first. This file records what was measured, what was changed, and what was
deliberately *not* changed because it turned out not to be a defect.

## Batch 1 — audit tooling and the defects it found

### Branch

Work is on **`TeknoDev-Branch`**. No branch named `tekodev` exists in this repository
(`git branch -a` lists `TeknoDev-Branch`, `master` and the remote feature branches), and the
instruction was not to create another branch, so the existing development branch was used
as-is. Nothing was force-pushed, reset or deleted. Another agent is active in the same
working tree on Spain, Qing and the settlement system; those paths were not touched.

### Tooling added

- `tools/iran_audit.py` — static audit of the Iran package: duplicate focus ids, focuses
  sharing an absolute grid cell (it resolves `relative_position_id` chains), prerequisites
  and relative positions pointing at missing ids, focuses unreachable from any root,
  duplicate event ids, events in a namespace with no `add_namespace`, duplicate decision
  ids, missing focus localisation, unregistered sprites and idea pictures, and style
  violations. Run with `--game "<HOI4 install>" --report <path>`.
- `tools/prune_dead_portraits.py` — removes character `portraits` entries whose sprite is
  never registered, and the sub-blocks they leave empty.

Current result: **307 focuses, 141 events, 65 decisions, 0 problems.**

### Fixed

| Defect | Detail |
| --- | --- |
| Two Shah portraits unregistered | `gfx/leaders/PER/Portrait_Persia_Ahmad_Shah_Qajar.dds` and `Portrait_Iran_Reza_Shah_Pahlavi.dds` both existed at 156×210 but no sprite referenced them, so the two central characters of the overhaul drew the default portrait. Registered in the new `interface/iran_portraits.gfx`, with 65×67 small crops generated in `gfx/interface/portraits/iran/`. |
| 59 character portraits pointed at art that does not exist | `PER.txt` and `PER_restored.txt` referenced sprites for Foroughi, Mosaddegh, Kashani, Zelli, Arfa, Razmara, Khomeini and others with no image anywhere in `gfx/`. Removed the unresolvable entries so those characters fall back to the engine default instead of a blank frame. See "Pending art" below. |
| 4 operative portraits unresolvable | `PER_scripted_effects.txt` used `GFX_portrait_arabia_generic_operative_male_1/2/4` and `GFX_portrait_PER_teymur_bakhtiar`, none of which exist in the mod or in vanilla. Repointed to vanilla's `GFX_portrait_operative_unknown`. |
| Decision category picture missing its `GFX_` prefix | `picture = decision_cat_picture_national_iranian_radio` → `GFX_decision_cat_picture_national_iranian_radio`. Category pictures take a full sprite name; the unprefixed form resolved to nothing. |
| UTF-8 BOM written into two script files | `PER_decision_categories.txt` and `PER_scripted_effects.txt` were saved with a BOM during this batch, which is fatal to the Clausewitz parser. Stripped; both now start on their first real token. |

### Checked and deliberately not changed

- `check_variable = { iran_authority < 50 }` — the short form. `documentation/triggers_documentation.md`
  documents both `{ var = x value = 1 compare = less_than }` and `{ x < 1 }`, and vanilla
  uses the short form heavily. Not a defect; the auditor no longer flags it.
- Identical `x`/`y` across many focuses — the trees are laid out with `relative_position_id`,
  so equal offsets are relative to different parents. Only absolute positions are compared.
- "Duplicate event ids" in `events/GOE_Persia.txt` — these were inline fires
  (`country_event = { id = X hours = 2 }`), not definitions. The auditor now ignores blocks
  with no `title`/`desc`.

### Pending art

59 characters have no portrait and now use the engine default: Mohammad Mosaddegh,
Mohammad Ali Foroughi, Abol-Ghasem Kashani, Abdollah Zelli, Hasan Arfa, Haj Ali Razmara,
Ruhollah Khomeini, Teymur Bakhtiar, Zia ol-Din Tabatabee, Soleiman Eskandari, Bahram Aryana,
Davud Monshizadeh, Gholamali Bayandor and the rest. Each needs a period portrait before it
can be shown; the names are recorded here so the list does not have to be rediscovered.
