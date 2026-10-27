# Republic Succession: Accepted First Implementation Slice

Accepted by Director on 2026-10-27 under Christopher's campaign attachment `pasted_content_2026-10-26_20-56-00-429_308d62.txt`, sections 6–8.
This is the binding implementation contract for C3's first slice, not acceptance of every arithmetic claim in its revision-four proposal.
The proposal is `docs/plans/qing_1910_1945/republic_fragmentation.md`; its later territorial, leader and clique work remains queued, not retired.
The sole existing chapter router remains authoritative.

## Decisions Accepted

Implement the eight civil/military pressure cards, the December throne choice, the scored succession, four seat-standing spirits, and the Beiyang balance display described by revision four sections 4–6.
Preserve its exact per-card costs and dial deltas, four family locks, governor cap, spirit payloads, and route-keyed AI weights.
The existing Second Revolution chooses the political route; the death crisis publishes the seat's earned condition rather than offering another free route menu.
A succession tier is not territorial fragmentation: this slice creates no tag, transfers no state, changes no leader and changes no focus tree.
Those campaign obligations remain open for later implementation.
English-only is the accepted Milestone 1 localisation scope.
Reuse existing appropriate vanilla/Endsieg icons and pictures; no artwork replacement, collection or placeholder creation is approved.

## Authoritative Arithmetic

Clamp legitimacy, military influence and nationalist support using existing 0–100 bounds.
Let `half_nat = round(nationalist_support / 2)` and `base = round((legitimacy + 100 - military_influence + half_nat) / 3)`.
Use documented `round_variable` semantics, nearest integer with midpoint away from zero.
Let `score = clamp(base + 8 * (rch_reform_settled + refused_throne) - 6 * governor_count - 15 * chinese_war, 0, 100)`.
Here `refused_throne` and `chinese_war` denote conditions for arithmetic, not stored numeric booleans.
Store booleans as flags.
`rch_reform_settled` is an integer 0–4 frozen at the settlement snapshot, never the current live gate count.

Resolve in this order: tier 3 if military influence is at least 80 or legitimacy is below 20; tier 0 if score is at least 70, all four reforms were settled, throne refused, fewer than three governors, control of state 608 and no Chinese war; tier 1 if score is at least 45; otherwise tier 2.
Use explicit comparison operators in every `check_variable`, particularly tier equality tests.
The default historical floor is tier 2; no score can defeat the tier-3 override.

The Director's executed Decimal probe corrects the proposal's contradictory emergency table.
With no settled reforms and no throne refusal, its five emergency dial states `(35,45,30)`, `(41,45,34)`, `(45,37,34)`, `(51,37,34)` and `(57,37,34)` produce scores **35, 38, 42, 44, 46** and tiers **2, 2, 2, 2, 1**, respectively.
A post-settlement reform cannot add eight points merely because the player bought a card; that would reopen the spree exploit.
Full civil `(62,37,38)`, four settled reforms and refused throne produces base 48, score 88, tier 0 under the territorial/war conditions.
Three civil `(56,37,38)`, three settled reforms and refused throne produces base 46, score 78, tier 1, not the proposal's base 47.
All military `(18,77,20)`, zero reforms, three governors and no throne refusal produces base 17, clamped score 0 and tier 3.
These are arithmetic fixtures, not an income, AI-selection or engine guarantee.
Boundary score tests construct actual states yielding 44/45 and 69/70; do not copy the proposal's erroneous 'five settled gates plus throne' fixture.

## Settlement and Resolution Ownership

On 12 December 1915, a Republic already active before that day takes exactly one snapshot of the four reform flags that are strictly older than 180 days.
A flag set on 14 June 1915 qualifies at 181 calendar days; a flag set on 15 June does not at exactly 180 days.
If all four flags have the same excluded date the count is zero, not three as one proposal fixture claims.
A Republic initialised on or after the settlement date receives a sealed zero snapshot, not retroactive maturity.
This handles a late-created Republic without inventing history.
The throne offer is queued once during 12–31 December 1915; refusal is a settlement condition, not an aged fifth reform.
A start on or after 1 January 1916 is endowed Hongxian with the choice already seen and no refusal.
The calendar difference from 12 December 1915 to 6 June 1916 is 177 days; the queued offer can be answered later, so no 180-day throne-maturity rule is allowed.
The earlier Director 176-day elapsed-time calculation crossed daylight-saving time and is not a calendar-day proof.

The tick owns resolution on the first eligible day after 5 June 1916.
It refreshes, evaluates, freezes final score and tier, applies one line flag and one seat spirit, clears Hongxian, records resolution and the death-seen flag, and only then queues `.5` with the existing one-day delay.
The popup presents only: its `immediate` must not recompute, freeze or resolve anything, contradicting the stale row in proposal section 6.1.
A delayed or absent popup cannot change the outcome.
A post-crisis bookmark resolves silently at initialisation and marks the death seen; it does not receive the old crisis popup.
Preserve the existing political route when one is set; default to the existing Beiyang route without paying its settlement rewards again only when unset.
`rch_refresh_mechanics` must reapply exactly the frozen seat spirit whenever it refreshes other spirit families; adding the family to its removal list without reapplication would erase the result.
Repeat ticks, repeated resolution and refreshes do not grant the score, spirit or rewards twice.

## Pressure Cards and Display

Use the revision-four card table and all four shared family locks.
Both sides of a family are unavailable through day 180 after either action and available on day 181.
An available check locks rather than hides a visible opposite card; requirement text must explain it.
Clear a reform when the opposing military card is taken and restart its flag date when civil reform is re-earned.
Clamp the governor counter after every increment and never reuse the existing `rch_military_governors` flag name for it.
All new tuning, including score arithmetic, thresholds, costs, lock duration, AI weights, spirit values and display bands, belongs in `rch_story`; mirror literals only where the engine rejects constants.
The eight cards and succession are identical with or without Arms Against Tyranny.

The balance display mirrors only military influence, using the proposal's five bands and exact case-sensitive category id `rch_beiyang_order_category`.
Refresh from the actual dial, not from assumed card deltas, daily and after `rch_refresh_mechanics` so existing focus and event writers are reflected.
Create the native balance once, guarded by DLC and absence of the balance.
Publish band transitions using documented `add_power_balance_value` literals/constants and a stored published band; remove the previous band's offset and apply the new one exactly once.
Do not repeatedly call `set_power_balance` each day and rely on unverified reinitialisation semantics.
This is the accepted delta-publication implementation already described as an alternative in C3, not permission for an improvised fallback.
Ranges carry no gameplay modifier; the four seat spirits carry the outcomes.
No-DLC play must execute no balance commands while preserving all cards and outcomes.
Expose the score, four settled-reform requirements, current lock and final seat condition through truthful category/decision/event text without claiming territorial losses.

## AI and Validation

Use the accepted route-keyed civil/military weights: Beiyang 0/0, parliamentary 3/1, KMT 2/1, provincial 1/2.
The throne's accept/refuse weights are 4/1.
These are scores, not exact campaign selection probabilities; do not predict how many cards AI can afford from the stale income table.
Preserve all unrelated existing weights and political choices.
Use the probability-audit workflow and immutable before-source/scenario evidence; the already exhausted adapter 1.19.2-versus-game-1.19.3 failure must be recorded, not retried without changed information.
Direct source calculations must distinguish scores from probabilities and keep unsupported comparisons unresolved.

Tests execute parsed shipped source, fail on unsupported commands and cover every card, snapshot boundaries, locks in both directions, cleared/re-earned flag tenure, four tiers, collapse precedence, absent/deferred popup, bookmark endowment, same-day repeats, spirit refresh survival, display changes from an existing writer and no-DLC parity.
Use mutants for deleted/changed guards, maturity, rounding, family locks, governor clamp, score comparisons and event recomputation.
A control must prove that the pre-implementation source fails for missing features.
Run existing Republic chapter, Qing survival/consolidation and China reference audits; preserve routing and focus IDs/icons/layout.
Implementation handoff and independent QA require their own read-only MCP inspections and post-edit validation with parameters, diagnostics, coverage and resource URIs.
No in-game, panel-render or AI-campaign observation has been performed or is authorised.
