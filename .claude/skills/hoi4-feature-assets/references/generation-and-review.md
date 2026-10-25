# Generated source art and review

Use the project's selected image-generation route and its generated provider details below. When that route offers a model choice, choose only from its listed models and capabilities. Never invent a tool, model, size, reference argument, or backend. Describe the desired canvas and background in the prompt, inspect the returned dimensions, and process to the runtime canvas afterward. Ask for one image per call.

### ChatGPT subscription (GPTImage)
- Tools: auth_status: `image_auth_status`, generate: `generate_image`, list_references: `list_references`
- Tool inputs: output_path: `out`, prompt: `prompt`, quality: `quality`, reference_images: `reference_images`, size: `size`
- References: Use list_references to discover project references, then pass relevant image paths and describe each one's role. Reference count is not documented; output sizes have a maximum edge and aspect-ratio rule.
- Size: This route uses the model's default image size; limits can vary by model.
- Transparent backgrounds: PNG output does not guarantee a transparent background. If unavailable: Use a selected background-removal route and verify alpha; if none is configured, ask the maintainer for another route.
- Reference edits: not available on this route. If unavailable: Use reference_images to make a new version; choose another configured provider for precise image edits.
- Make one image per call. For a transparent image, check that the saved PNG has at least one pixel with alpha below 255; an alpha channel alone does not prove that pixels are transparent.

Before generation, identify the asset type, exact consumer, subject, intended footprint, composition, palette, reserved space, and prohibited additions. Label every supplied reference by filename and role: edit target, permitted subject anchor, style anchor, geometry/composition anchor, or explicit insertion layer. State which properties may transfer. A style reference does not authorize copying its identity, lettering, frame, or unrelated canvas. Portrait sourcing rules and exact map geometry remain authoritative.

Inspect local images before editing. Supply references through the actual tool schema, with the smallest input set that contains every required target. Do not rely on an unseen filename or ambiguous “previous image” to convey a reference.

When a candidate is close, correct one coherent defect on the current accepted candidate, inspect the result, and continue from the accepted output. Preserve accepted candidates and record rejected branches. A substantially wrong composition or requested alternative can justify a new generation. Restate invariants in every edit: subject, pose, proportions, palette, consumer footprint, reserved space, background/alpha, and unchanged regions. Keep functional UI controls and changing labels native.

For alpha-backed families, request real transparency only when the selected route supports it and preserve it through every edit and processing step. Check zero-alpha unused corners and padding, complete subject edges, and absence of fake checkerboard, matte, halo, key colour, or unintended holes. Opaque scene art, portraits, flags, and painted panels retain their required backgrounds. If the route cannot make alpha, use its listed background-removal fallback and check the edges; if no fallback is listed, report the blocker.

If transparent output fails, use a focused edit or removal tool only when the selected provider details list that capability. Keep the accepted subject, preserve the untouched input, record the processing route, and inspect clipped edges, colour spill, internal holes, and changed bounds before promotion. Do not use an unconfigured service or local process as a silent fallback.

Review the full-resolution candidate and the exact native-size processed preview against the brief and matching vanilla family. Check silhouette, framing, palette, edges, transparency, reserved space, and forbidden additions. For animation, also inspect frame order, anchor drift, changing footprint, timing, and loop seam under `hoi4-frame-animation`. A successful generation, file timestamp, spec-folder location, or old status label is not approval. Record explicit user direction or parent acceptance within existing authorization, the selected candidate, and unresolved defects before DDS promotion.

Keep source paths, prompts, accepted-candidate lineage, processing recipe, review findings, and runtime crosswalk together. Ordinary local revisions do not need repeated hand-copied hashes in every note. Preserve machine-generated provenance hashes, source/crop pixel-equality evidence, security and download checksums, provider lineage, uncertain-mutation guards, and deployed-runtime integrity checks wherever their owning contract requires them.
