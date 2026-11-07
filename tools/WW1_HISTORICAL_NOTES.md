# WW1 historical notes

The gold `Historical` label is presented in native tooltips. Focus names and narrative descriptions are unmarked. Marked focuses append the note to their completion-effect tooltip; HOI4 uses that tooltip both on hover and in the selected focus's rewards panel. Event and news notes appear only when hovering over their option buttons.

The classification manifest is `tools/ww1_historical_notes.json`: 355 country-specific focuses and ten country-conditional shared focuses. Generic development stays neutral, and historical classification does not alter rewards, requirements, AI weights, layout or outcomes.

Shared focus notes retain their original `original_tag` conditions through `common/scripted_localisation/WWI_historical_notes.txt`, with an empty fallback. Cosmetic tag changes do not alter the classification. Their label no longer adds blank lines to narrative descriptions.

Historical event choices retain their existing curation. Historical episodes with a sole acknowledgement have the label on that button's tooltip. Conditional Serbian withdrawal and Zimmermann assessment outcomes retain their description triggers, so alternative outcomes remain unmarked. Multiple-choice events without a clearly curated historical response remain unmarked.

Abdülhamid's restoration, the Enver executive directorate, the Anglo-German coalition, successful new Habsburg constitutional settlements and alternative war plans remain unmarked. The American associated-power option is marked instead of formal Allied alliance membership.

The existing focus and event prose is preserved. Validation checks reversible source edits, native tooltip syntax, localisation references, UTF-8 BOMs, shared-country conditions and alternative-path exclusions. HOI4 was not launched; final appearance needs a user-run check.
