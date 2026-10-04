# Ultimate-HOI4-GFX source components

These files are the selected original pieces and flattened PSD frames used by the Endsieg interwar icon rework.

- Upstream: https://github.com/Globvs/Ultimate-HOI4-GFX
- Pinned revision: `3626dc83c8573d6603fa497138090b04b64a15ba`
- Original contributor credits and reuse statement: `CREDITS.txt`
- Recipe manifest with original-file SHA-256 hashes: `tools/interwar_ultimate_icon_manifest.json`

The upstream artwork remains unchanged here. The build tool composes these pieces at native game sizes and exports transparent RGBA DDS textures and editable PNG masters. It does not use AI-generated substitute artwork.

Rebuild from the repository root:

```powershell
python -B tools/build_interwar_ultimate_icons.py --source-dir tools/assets/ultimate_hoi4_gfx --manifest tools/interwar_ultimate_icon_manifest.json --output-root .
```

Add `--preview-dir <folder>` for contact sheets, or `--only <manifest-key>` to rebuild one recipe. Generated files retain the existing Endsieg paths and sprite references. The three newer German focuses now have their own sprites.

Scope: 240 bespoke focus icons, 141 national-spirit icons, 16 shared spirit-theme icons, 16 decision icons and 16 category icons. Event photographs, character portraits and advisor portraits retain their historical artwork.
