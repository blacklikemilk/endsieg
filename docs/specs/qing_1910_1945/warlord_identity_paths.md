# Warlord Identity Paths: Pilot Clique Design (C4)

Status: proposal awaiting Director design review under card C4 (`t_9bbdf83c`).
This document is a design contract for one pilot clique, not approval, not implementation and not gameplay completion.
It writes no script, no localisation, no `.gfx` and no vault note.
Design acceptance lives with the Director; the next card owns the code.

Evidence classes are marked on every load-bearing claim:

- **[src]** — repository file and line in this checkout.
- **[game]** — the installed Hearts of Iron IV 1.19.3 tree, read directly.
- **[wiki]** — the offline snapshot in `paradox_wiki/`.
- **[tool]** — a read-only MCP route run during this card.
- **[plan]** — the master plan in the vault, not verified in the tree.
- **[proposal]** — my design decision, requiring Director acceptance.

Baseline: `TeknoDev-Branch` at `02042bc42`, read-only.
The working tree also contains another session's uncommitted Spain, Iran and docs work; none of it is described here as mine.

---

## 1. What is measured today

| Fact | Evidence |
| --- | --- |
| `SHX = "countries/Shanxi.txt"` is a real tag. | **[src]** `common/country_tags/00_countries.txt:82` |
| SHX capital is 615; SHX has a 1936 history block and recruits 21 characters, `SHX_yan_xishan` first. | **[src]** `history/countries/SHX - Shanxi.txt:1`, `:456-474` |
| `SHX_yan_xishan` is a character with a shipped portrait, a `despotism` `country_leader` block and an army-chief advisor slot. | **[src]** `common/characters/SHX.txt:2-32`; **[tool]** `hoi4.source_lookup SHX_yan_xishan` returns that definition plus the overridden vanilla one |
| The mod's `SHX.txt` override drops the `traits = { SHX_model_governor }` line that vanilla's copy carries. The trait itself exists in the mod. | **[tool]** same lookup, `game:common/characters/Warlords_China.txt:1719-1750` versus `mod:common/characters/SHX.txt:2-31`; **[src]** `common/country_leader/00_traits.txt:938` |
| SHX owns three states from 1936.1.1: 615 Shanxi (capital), 621 Suiyuan, 746 Ordos. Before 1936 all three are RCH's from 1914.1.1, and QIN's before that. SHX owns **nothing** between 1914 and 1936. | **[src]** `history/states/615-Shanxi.txt:13,27-37`; `history/states/621-China 18.txt:13,23-33`; `history/states/746-Ordos.txt:16,27-33` |
| Neighbouring states 611 (South Chahar) and 612 (Chahar) exist and are not SHX-owned. | **[src]** `history/states/611-China 10.txt`, `history/states/612-China 11.txt` (state file names carry the historical region in a comment) |
| `is_chinese_warlord` is a five-tag list: GXC, YUN, SHX, XSM, SIK. It excludes SND, SIC, GDC, XIC, HBC, KHM, NXM, GSM, KUM. | **[src]** `common/scripted_triggers/CHI_scripted_triggers.txt:124-131` |
| Vanilla's warlord autonomy level is `autonomy_sea_warlord_subject`, gated on No Compromise No Surrender, `is_chinese_warlord = yes` and a Chinese overlord, and it sets `can_not_declare_war = yes`. | **[game]** `common/autonomous_states/sea_warlord_subject.txt` |
| The mod ships no `common/autonomous_states` directory at all. | **[src]** directory listing of `common/` |
| `set_autonomy` with `autonomy_sea_warlord_subject` is already used in mod script. | **[src]** `common/decisions/CHI_decisions.txt:9564-9570` |
| No Compromise No Surrender is installed. | **[game]** `dlc/dlc049_no_compromise_no_surrender` |
| The 1936 dispatcher sends SHX, with thirteen other Chinese tags, to `china_warlord_sea_focus` (`keep_completed = yes`) on NCNS, and to `china_warlord_focus` on Waking the Tiger only. | **[src]** `common/on_actions/endsieg_on_actions.txt:551-569`, NCNS load at `:560` |
| Nothing routes SHX before 1936. There is no `on_daily_SHX`, no `shx_*` script, no `SHX` reference in any Republic or Qing campaign file except a war check and an ownership helper. | **[src]** `grep SHX` across `common/`, `events/`, `history/`; `common/scripted_triggers/rch_campaign.txt:147`; `common/scripted_effects/endsieg_china_ownership.txt:84` |
| `china_warlord_sea_focus` contains **no** SHX identity branch: SHX appears twice, both as an AI-weight modifier on a shared focus. | **[src]** `common/national_focus/china_warlord_sea.txt:845-854`; **[tool]** `hoi4.focus_inspect china_warlord_sea_focus` |
| The vanilla NCNS warlord tree is 155 focuses across 48 columns, with 227 connector crossings, 67 too-close same-row pairs and 202 blocking focus diagnostics. | **[tool]** `hoi4.focus_inspect china_warlord_sea_focus`, revision `294a3cee…`, `validation.passed = false` |
| `rch_warlord` is 50 focuses across 43 columns, 0 too-close same-row pairs, 6 crossings, 4 long connectors, and no blocking diagnostics. | **[tool]** `hoi4.focus_inspect rch_warlord`, same revision, `validation.passed = true` |
| The Republic's chapter boundaries are `date < 1919.1.1` (chapter one), `date < 1928.1.1` (chapter two), else chapter three. | **[src]** `common/scripted_effects/rch_campaign.txt:91-101`; the router repeats the same split at `:195-229` |
| The four Republic route flags the C3 contract fixes are `rch_path_beiyang`, `rch_path_parliamentary`, `rch_path_kmt`, `rch_path_provincial`, and they are live in six files. | **[src]** `common/national_focus/rch_warlord.txt:143,159,175,191`; `common/scripted_effects/rch_campaign.txt:17-29` |
| None of the master plan's architecture exists in the tree: `china_fragmentation_tier`, `china_release_warlord`, `china_seat_holder`, `china_reunified_by`, `china_route_focus_tree`, `china_proper_states` all resolve to zero files. | **[src]** symbol sweep across `common/`, `events/`, `history/` |
| `common/script_constants/` holds `qing_campaign.txt`, `rch_campaign.txt`, `iran_*`, `spain_campaign.txt` and `PER_focus_tree.txt`. There is no `china_story.txt`. | **[src]** directory listing |
| The constants namespace convention is `namespace = { schema = { any_key = yes data = fixed_point } … }`, referenced as `constant:namespace.key`. | **[src]** `common/script_constants/rch_campaign.txt:3-6`, and 54 `constant:rch_story` references in `common/scripted_effects/rch_campaign.txt` |
| The ten-tag "another Chinese government" set already exists as `rch_chinese_war`. | **[src]** `common/scripted_triggers/rch_campaign.txt:141-152` |
| Flag maturity uses `has_country_flag = { flag = … days > N }`. | **[src]** `common/scripted_effects/BUL_scripted_effects.txt:519-524` |
| `change_tag_from` appears in the legacy revolution chain and in the 1936 handover. | **[src]** `events/WWI - Chinese Collection Events.txt:71,451,473,494,762`; `common/scripted_effects/rch_campaign.txt:153` |
| `warlord_cohesion`, `warlord_patronage`, `shx_campaign` and `shx_story` collide with nothing in the tree. | **[src]** symbol sweep, zero files each |

---

## 2. The pilot decision

**The pilot clique is `SHX`, Shanxi under Yan Xishan.** **[proposal]**

### 2.1 Why SHX

1. **It is one of the only tags that can legally be a vanilla warlord subject.** `autonomy_sea_warlord_subject.allowed` requires `is_chinese_warlord = yes`, and that trigger names five tags, SHX among them. **[src]** `CHI_scripted_triggers.txt:124-131`, **[game]** `sea_warlord_subject.txt`. Any pilot drawn from SND, SIC, GDC, XIC, HBC, KHM, NXM, GSM or KUM cannot use the vanilla subject relationship without first editing a vanilla-derived trigger.
2. **It has one ruler across all four bands.** Yan Xishan governs from 1911 to 1949, so the pilot tests identity continuity without inventing leaders or portraits for each band, and without a leader-replacement chain that would collide with the 21-character 1936 roster. **[src]** `common/characters/SHX.txt:2-32`, `history/countries/SHX - Shanxi.txt:456-474`.
3. **It has a full 1936 handover to protect.** The dispatcher, the WTT selector and the NCNS tree all already handle SHX from 1936. **[src]** `endsieg_on_actions.txt:551-569`; `common/national_focus/china_warlord.txt:9-24`. The pilot therefore ends exactly where vanilla begins, which is the cheapest possible proof that the era model does not overwrite vanilla content.
4. **It has no existing pre-1936 content to duplicate and no identity branch to collide with.** **[src]** and **[tool]** rows 11-13 above.
5. **Its four bands are genuinely different play, not one tree relabelled.** See section 4.

### 2.2 What was rejected, and why

| Candidate | Verdict | Reason |
| --- | --- | --- |
| `ZHL`, `ANH`, `FNG` — the master plan's first three roster rows **[plan]** | Rejected as pilot, retained as a gated roster step | None of the three is a tag. **[src]** both `common/country_tags` files, zero matches. Creating them needs `country_tags`, `common/countries`, a colour, dormant history and flag art — a card of its own, and an artwork decision this design may not take. |
| `SND` Shandong | Rejected as pilot, retained as a late roster slice | Zhang Zongchang's Shandong is a 1925-28 client, so it has no 1916 rise band and no Nanjing-decade band. A four-band identity would have to be invented. |
| `GXC` Guangxi | Rejected as pilot, promoted to slice 2 | Strong candidate: two regimes in one tag (Old Guangxi to 1921, New Guangxi from 1925). It is harder to validate than SHX because the tag changes hands mid-period, so it should follow the pilot rather than prove the architecture. |
| `YUN` Yunnan | Retained as slice 3 | Strong, but its rise band is the National Protection War, which is already carried by the `NPA` tag and events. Resolving that overlap is its own design question. |
| `SIK`, `XSM` | Retained as slices 5-6 | Both are frontier identities with no national bid; they test the mechanic's low end, not its high end. |

---

## 3. Era windows

The pilot uses four bands. Boundaries are chosen so that one router can serve SHX and the Republic's existing chapter dates without a second calendar.

| Band | Opens | Closes | Boundary evidence |
| --- | --- | --- | --- |
| S1 Rise — the model province | after 1916.6.5 | 1920.7.13 | Yuan's death on 6 June 1916 is the date the accepted C3 contract fixes for the succession gate (`date > 1916.6.5`). **[src]** `docs/specs/qing_1910_1945/republic_succession.md:53-54` |
| S2 Clique wars — neutrality priced | 1920.7.14 | 1927.12.31 | Zhili–Anhui War July 1920 opens the clique-war phase. **[plan]** master plan §3 |
| S3 Nanjing decade | 1928.1.1 | 1935.12.31 | 1928.1.1 is the existing code boundary between `rch_warlord` and `rch_nanjing`. **[src]** `common/scripted_effects/rch_campaign.txt:95-98`. The historical seat transfer is June 1928, five months later; the band opens on the code date and its first content is gated on the seat flag, with a bypass from 1928.7.1. |
| S4 Wartime | 1936.1.1 | 1945 | The existing 1936 dispatcher is the handover. **[src]** `endsieg_on_actions.txt:551-569` |

**The C3 contract's route names are respected, not reused.** `rch_path_beiyang`, `rch_path_parliamentary`, `rch_path_kmt` and `rch_path_provincial` describe the *Republic's* regime choice. A warlord has no route menu; its regime is its seat relationship and its cohesion tier. The pilot therefore adds no `rch_path_*` flag and reads none of them, except where `rch_path_kmt = yes` is needed to know whether the Republic that surrounds it is a party state or a Beiyang government — one read-only reference, no write. **[proposal]**

---

## 4. The four identities of SHX

Each band states what the player is actually doing, what changes on the map, and what the band hands to the next one.

### S1 — The model province (1916.6.6 – 1920.7.13)

- **Fantasy:** be the province that survives by not fighting. The currency, the arsenal, the provincial bank and the village compact are the whole game.
- **Rise:** SHX does not exist on 6 June 1916. It is released into 615 by the fragmentation package with Renzhi recognition of Beijing, cores added first. **[src]** state history rows above; **[proposal]** the release itself.
- **Identity content:** provincial treasury, arsenal and officer school (reusing Yan's existing army-chief advisor slot), the "three-thirds" self-government system, refusal or payment of Beijing's troop demands, and the railway that connects Shanxi to the coast rather than to Zhili.
- **No war.** The band's only war option is defensive; SHX cannot declare.
- **Hands forward:** cohesion level, the patron flag if one was taken, and the `shx_no_troops_to_beijing` flag if the demands were refused.

### S2 — Neutrality priced (1920.7.14 – 1927.12.31)

- **Fantasy:** every war you sit out makes the winner stronger and your own claim to the seat weaker. Neutrality is a resource that runs out.
- **Identity content:** brokerage (sell passage, sell munitions, host the arbitration), the Suiyuan and Chahar question (states 621, 611, 612), and the late join of the Northern Expedition.
- **Clique war:** SHX may declare a limited war on a rival only at cohesion 60 or above, and only while that rival is already at war elsewhere. **[proposal]**
- **Hands forward:** whether SHX joined the expedition, and its cohesion at 1928.1.1.

### S3 — Nanjing decade (1928.1.1 – 1935.12.31)

- **Fantasy:** keep the province while the centre asks for everything. Nominal submission buys time; real submission buys a chair in Nanjing and loses the province.
- **Identity content:** the flag replacement, the 1930 coalition (the one national bid SHX historically made and lost), provincial autonomy statutes, the North China autonomy squeeze, and Japanese economic penetration of the north.
- **The historical seat bid is a defeat, not a reward.** In the historical line the coalition collapses and cohesion falls; the alternate line is what the payoff in section 9 is for.
- **Hands forward:** the `shx_autonomy_charter` flag, cohesion, and whether SHX is a subject of CHI.

### S4 — Wartime (1936.1.1 – 1945)

- **Historical line: no new tree.** SHX is routed to `china_warlord_sea_focus` by the existing dispatcher. The pilot adds nothing to that tree and must not: it already carries 202 blocking diagnostics and 67 too-close pairs. **[tool]** `hoi4.focus_inspect`.
- **Alternate line only:** a `shx_wartime` tree exists for two outcomes, and only those two: SHX holds the seat (section 9), or SHX is a Japanese-aligned subject. In both cases the wartime identity is the three-way squeeze — Chongqing, Yan'an and Tokyo — expressed as cohesion and patron flags, not as new map mechanics.
- **Japanese invasion is not modelled here.** State 615's history already transfers control to JAP on 1938.10.25 and later to PRC and JAP. **[src]** `history/states/615-Shanxi.txt:38-64`. The wartime design reads those blocks; it does not rewrite them.

---

## 5. State model: what is a flag, what is a variable, and why

The rule from the accepted contract is that booleans are flags and tunable magnitudes are variables. **[src]** `republic_succession.md:24-25`.

| Datum | Scope | Kind | Values | Reason |
| --- | --- | --- | --- | --- |
| `warlord_cohesion` | country | variable, 0–100 | opening value per tag in constants | A magnitude with thresholds, losses and gains. It must be comparable and must appear in tooltips. |
| `warlord_cohesion_tier` | *not stored* | derived trigger | 0–3 | Storing a second representation invites drift. The tier is a scripted trigger over `warlord_cohesion`, so the spirit, the AI weight and the tooltip can never disagree. |
| `warlord_patronage_debt` | country | variable, 0–3 | integer | A count of unpaid favours, consumed one at a time by events. A flag cannot be spent. |
| `warlord_seat_bid_made` | country | flag | permanent | A once-per-campaign fact. **[proposal]** |
| `warlord_seat_won` | country | flag | permanent | A once-per-campaign outcome. |
| `warlord_patron_japan` / `_soviet` / `_britain` | country | flags, mutually exclusive | one only | A family, not a count. The lock is a `NOT = { OR = { … } }` in the decision trigger and a second patron is refused by a maturity rule. |
| `warlord_rival_<tag>` | country | flag per rival | any number | Identity of an enemy, not a magnitude. |
| `shx_no_troops_to_beijing` | country | flag | permanent | Event memory that later content reads. |
| `shx_autonomy_charter` | country | flag | permanent | The S3 outcome that S4 reads. |
| `china_seat_holder` | global | variable (country) | one | **Does not exist.** Required by the seat rule; owned by C1, not by this design. |
| `china_reunified_by` | global | variable (country) | one | **Does not exist.** Required by the payoff; owned by C1. |

**Nothing in this design creates a balance of power.** Cohesion is a variable plus one spirit, so the pilot works identically with and without Arms Against Tyranny, which the accepted contract already requires for the Republic's cards. **[src]** `republic_succession.md:70`.

---

## 6. Cohesion

`warlord_cohesion` is 0–100 and belongs to the tag, not to the pilot: every roster slice reads the same variable and the same four spirits. **[proposal]**

| Tier | Band | Spirit | Payload direction |
| --- | --- | --- | --- |
| 0 | below 30 | `warlord_cohesion_fractious` | Stability and division-organisation penalties; defection and mutiny events enabled |
| 1 | 30 to 54 | `warlord_cohesion_brittle` | Small penalties; no offensive war option |
| 2 | 55 to 79 | `warlord_cohesion_steady` | No penalties; limited war enabled |
| 3 | 80 and above | `warlord_cohesion_devoted` | Organisation and recovery bonuses; seat bid enabled |

- **Sources of loss:** unpaid arrears, a lost limited war, a purged commander, a patron's demand refused, a rival's victory in a war SHX sat out.
- **Sources of gain:** patronage, arrears paid, a won limited war, a foreign patron, a provincial compact completed.
- **The refresh effect is one comparison.** `shx_refresh_mechanics` runs from `on_daily_SHX` (a per-tag on_action, permitted) and exits unless the tier trigger's answer differs from the applied spirit. It must re-apply the current tier spirit when it refreshes, because removing a family without re-adding the surviving member erases the result — the exact defect the C3 contract had to legislate against. **[src]** `republic_succession.md:59`.
- **Tuning lives in constants.** Bands, gains, losses, and the AI thresholds below are all `constant:shx_story.*`.

**[proposal]** Every number above is a starting value for review, not a balance claim. No playtest has been run and none is authorised by this card.

---

## 7. Patronage

Patronage is how a poor province buys loyalty it cannot pay for, and the debt is the cost.

- **Act:** a decision family `shx_patronage_category` with three escalating options: pay arrears with political power, equip a commander with army equipment, and grant a commander a provincial office.
- **Effect:** each raises `warlord_cohesion` by a constant and raises `warlord_patronage_debt` by one, clamped at 3.
- **Cost:** at debt 3, a `shx_patronage_demand` event fires on the next monthly tick and offers three answers — pay in political power, pay in equipment, or refuse. Refusal costs cohesion and sets a commander-grudge flag that later blocks the seat bid.
- **No free lunch:** the decision is visible only while `warlord_patronage_debt` is below the cap, and its requirement tooltip states the current debt and the next demand.
- **Anti-farm:** the debt counter is what prevents a player from converting political power into permanent loyalty. Every point of cohesion bought must eventually be paid for twice.

---

## 8. Rivals and foreign patrons

### 8.1 Rivals

- **Rival identity comes from existing tags.** The set is the ten-tag `rch_chinese_war` list, which already exists and is the repository's own definition of "another Chinese government". **[src]** `common/scripted_triggers/rch_campaign.txt:141-152`. The pilot adds no second list.
- **Named rivals for SHX:** `XIC` (the Guominjun, the 1925-30 northern rival), `CHI` (the centre that wants the province), and `SND` (the Fengtian client on the eastern flank) while `SND` exists. **[proposal]**
- **The missing rivals are a real gap.** Zhili (`ZHL`) and Fengtian (`FNG`) are the historical antagonists of the 1920 and 1922 wars, and neither is a tag. Until they exist, an SHX clique war can only be fought against XIC, CHI, SND, YUN, GXC, SIK, XSM, SIC, QIN, GDC or PRC. This is the single largest constraint on the pilot's S2 band and it is a Director decision, not something this design can paper over.
- Rival antagonism is **read from existing relations** rather than duplicated into a parallel counter: war state, opinion and subject status already exist and already change.

### 8.2 Foreign patrons

Three exclusive patrons, each a flag with a distinct payload and a distinct trap. **[proposal]**

| Patron | Grant | Trap | Historical fit |
| --- | --- | --- | --- |
| `warlord_patron_japan` | Cohesion income and equipment | A Japanese demand clock that costs autonomy, and a 1937 choice between resistance and collaboration | North China penetration, 1935 onward |
| `warlord_patron_britain` | Political power and trade | Requires the Republic or the seat to be on good terms with Britain; lost if that government falls | The pre-1927 treaty-port economy |
| `warlord_patron_soviet` | Army experience and equipment | Raises the radicalism the province's own compact suppresses, and the patron switches sides after 1927 | The 1925-27 northern alignment |

- **Maturity rule.** A second patron is refused for 365 days after the first (`has_country_flag = { … days > 365 }`), which is the in-mod maturity idiom. **[src]** `BUL_scripted_effects.txt:519-524`.
- **No patron is a valid choice.** Refusing all three is the historical Shanxi answer and carries its own cohesion penalty, never a hidden bonus.

---

## 9. Seat transfer

The seat rule is the master plan's, not a new one. This section states only what the pilot contributes to it.

- **The effect does not exist yet.** `china_release_warlord`, `china_seat_holder` and the seat transfer belong to C1/C6/C7. **[src]** symbol sweep, zero files. **[plan]** master plan §14.5.
- **SHX's precondition.** A seat bid requires: cohesion tier 3, `warlord_seat_bid_made` unset, a coalition partner flag, and the current seat holder at war and losing. **[proposal]**
- **SHX's cost.** The bid spends cohesion (a large constant), sets `warlord_seat_bid_made`, and, if it fails, applies the fractious spirit for a fixed period and releases any state gained in S2.
- **SHX's win condition.** On success the seat flag is set, `warlord_seat_won` is set, and the country routes to `china_warlord_national`. This is the master plan's named tree. **[plan]** §10.2. It does not exist; the pilot names it as a dependency rather than inventing an alternative.
- **Who moves.** If SHX is human and wins the seat, `change_tag_from` moves the player only inside the transfer effect and only with an event option that offers "follow the government" against "remain with the clique". The engine precedent for `change_tag_from` in this mod is the revolution chain and the 1936 handover. **[src]** `events/WWI - Chinese Collection Events.txt:451,473`; `common/scripted_effects/rch_campaign.txt:153`.
- **One bid per campaign.** The bid flag is permanent and is never cleared, including by a reload, a warsave or a second insurgency.

---

## 10. Reunification payoffs, with costs

A warlord that reunifies China must feel the difference immediately and must not be able to farm it.

| Payoff | What it is | Cost |
| --- | --- | --- |
| **The seat** | `warlord_seat_won` plus `china_seat_holder` set to the unifier | Cohesion spent on the bid; the fractious period if it fails |
| **The national tree** | `china_warlord_national` replaces the band tree | Integration lane decisions must be worked; the tree is not a reward screen |
| **The integration lane** | Four decision families — military integration, civil governors, currency and railway reconstruction, foreign recognition — each with a visible autonomy spirit that shrinks as the work is done | Political power, command power, equipment and time; each family is what turns occupation into revenue |
| **The legitimacy spirit** | One spirit replacing the cohesion spirit, carrying the same values the warlord had earned | None beyond the decisions above; the spirit is a translation, not a bonus |

- **Pay once.** Every payoff effect is guarded by a permanent flag and refuses to run twice. **[proposal]**
- **No repeatable dumps.** No focus, decision or event in this design grants political power, manpower or equipment on a cooldown. The C3 contract's exploit lesson — a card cannot add score merely because it was bought — is the same rule. **[src]** `republic_succession.md:34`.
- **Reunification is not a victory screen.** The integration lane is deliberately the largest part of the payoff, because that is where the master plan's four-part loop already points. **[plan]** §10.3.

---

## 11. Anti-repeat safeguards

| Risk | Safeguard |
| --- | --- |
| Seat bid repeated after failure | `warlord_seat_bid_made` is permanent and never cleared |
| Reunification payoff collected twice | Every payoff effect guarded by its own permanent flag |
| Cohesion bought without limit | `warlord_patronage_debt` capped at 3 and consumed by demand events |
| Two patrons stacked | Second patron refused for 365 days by a flag-maturity test |
| Spirit family erased on refresh | `shx_refresh_mechanics` re-applies the current tier spirit, per the C3 defect |
| Cross-tree `has_completed_focus` | No focus test reads another tree's focus; continuity is flags and variables only **[wiki]** `National focus modding`, shared focuses section |
| Double reward on era swap | Era trees share `shared_focus` blocks loaded with `keep_completed = yes`, so a completed shared focus cannot pay twice **[wiki]** `Effects` `load_focus_tree` |
| Leader double recruitment | The release effect recruits `SHX_yan_xishan` only under `NOT = { has_character = SHX_yan_xishan }`; the 1936 history already recruits him and twenty others **[src]** `history/countries/SHX - Shanxi.txt:456-474` |
| Province released twice | The release effect requires the tag not to exist and the state to be RCH-owned |
| Subject that cannot fight | A warlord needing a clique war is **not** put on `autonomy_sea_warlord_subject`, which sets `can_not_declare_war = yes` **[game]**; independence precedes the declaration |

---

## 12. AI intent per band

Weights live in constants and are read by `ai_will_do` through `constant:shx_story.*`. Weights are scores, not selection probabilities, and no run has measured them. **[proposal]**

| Band | AI intent |
| --- | --- |
| S1 | Never declare war. Take the treasury, arsenal and compact families in that order. Refuse Beijing's troop demand only above cohesion 40. Take a patron only if cohesion is below 35. |
| S2 | Broker rather than fight. Declare a limited war only at cohesion 60 or above and only against a rival already at war. Join the Northern Expedition only after the seat holder has lost two engagements. |
| S3 | Accept nominal submission unless cohesion is at tier 3 and the centre is at war elsewhere. Join the 1930 coalition only with a partner flag and cohesion at tier 3. |
| S4 historical | Take no new tree: hand over to vanilla at 1936.1.1. In the Japanese war, join the strongest side unless `warlord_patron_japan` is set. |
| S4 alternate | After winning the seat, work the integration lane in the order military, administration, economy, recognition. |

**Hard prohibitions for AI.** No seat bid below tier 3. No clique war during a Japanese war. No second patron inside the maturity window. No authoritarian-style purge at tier 0.

---

## 13. English localisation key inventory (keys only)

Milestone 1 is English-only. **[src]** `docs/plans/campaign/milestone1.md:4`. No text is proposed here, because the slice is not yet admitted.

**Spirits** — `warlord_cohesion_fractious`, `warlord_cohesion_brittle`, `warlord_cohesion_steady`, `warlord_cohesion_devoted`, plus `_desc` for each.

**Decision category** — `shx_patronage_category`, `shx_patronage_category_desc`.

**Decisions** — `shx_pay_arrears`, `shx_equip_commanders`, `shx_grant_office`, `shx_patron_japan`, `shx_patron_britain`, `shx_patron_soviet`, `shx_seat_bid`, and `_desc` for each.

**Events** — `shx_campaign.1` through `shx_campaign.12`, with title, description and option keys in the existing `ww1_china.*` / `rch_campaign.*` style.

**Focuses** — proposed ids are new and prefixed `SHX_`, for example `SHX_model_province`, `SHX_provincial_treasury`, `SHX_arsenal_expansion`, `SHX_refuse_beijing`, with the full list fixed by the implementation slice against the collision check. No id in this document reuses an existing one; every proposed id must be grep-checked before use.

**Tooltips** — one `shx_tt_*` key per non-obvious requirement: debt, tier, bid precondition, patron maturity.

**Rules.** Every flag trigger that appears in a player-visible requirement is either localised or wrapped in `hidden_trigger` with a `custom_trigger_tooltip`. No raw `§` or `£`. Keys are unversioned and carry no leading space.

---

## 14. Files a future implementation slice would own

**New files, all of them this slice's alone.**

- `common/script_constants/shx_campaign.txt` — namespace `shx_story`, following the `rch_story` schema line.
- `common/scripted_effects/shx_campaign.txt` — release, refresh, tier application, patron resolution, bid resolution.
- `common/scripted_triggers/shx_campaign.txt` — tier, debt, bid eligibility, patron maturity.
- `common/on_actions/shx_campaign.txt` — `on_daily_SHX` only, following `common/on_actions/rch_campaign.txt`.
- `common/ideas/shx_campaign.txt` — the four cohesion spirits and the wartime spirits.
- `common/decisions/shx_campaign.txt` — the patronage family and the seat bid.
- `events/shx_campaign.txt` — the twelve events.
- `common/national_focus/shx_rise.txt`, `shx_wars.txt`, `shx_nanjing.txt`, and `shx_wartime.txt` only for the alternate S4 line.
- `localisation/english/shx_campaign_l_english.yml`, `shx_campaign_events_l_english.yml`, `shx_focus_l_english.yml`.
- `common/ai_strategy_plans/SHX_warlord.txt`.
- `docs/systems/shx_campaign.md`.
- One or more rows in `docs/endsieg_dynamic_effects.md` for the release and refresh effects.

**Shared files, one owner at a time, not this slice by default.** `common/on_actions/endsieg_on_actions.txt` (C1 or C9), `history/states/615,621,746` (C1's state owner), `common/country_tags` (nobody — no new tag is needed), `common/script_constants/china_story.txt` (C1, does not exist).

**Prerequisites this design returns to the Director rather than creating.**

1. `china_release_warlord` — the release effect, currently assigned to C6. **[plan]** §9.1. The pilot cannot put SHX on the map without it.
2. `china_seat_holder` and `china_reunified_by` — the C1 global state model.
3. `china_warlord_national` — the post-unification tree, C7.
4. Three date-correct SHX state blocks (1916, 1920, 1928) if the release effect does not set ownership itself. Those are C1-owned history files.
5. The `ZHL`/`ANH`/`FNG` decision, which governs whether the S2 clique-war band can ever be historical.

---

## 15. The remaining roster, as queued country-specific slices

Each row is one future card. None is admitted by this document. Tags are the ones that exist; missing tags are marked as such.

| Slice | Tag | Identity in one line | Why it is not copy-paste | Gate |
| --- | --- | --- | --- | --- |
| 2 | `GXC` | Two cliques in one tag: Old Guangxi's mercenary autonomy, then the New Guangxi clique as the Republic's military vanguard | A tag that changes hands mid-period, so continuity must survive a regime change, not a leader change | None |
| 3 | `YUN` | The province that started the National Protection War and then became the road to Burma | Its rise band overlaps the existing `NPA` tag and events; that overlap needs its own decision | NPA overlap resolved |
| 4 | `SND` | The Fengtian client on the eastern flank, 1925-28 | Short, dependent, and the only warlord whose identity is being someone else's army | `FNG` decision |
| 5 | `SIK` | The frontier that survives by playing three empires against each other | No national bid, no Chinese war, an entirely diplomatic identity | None |
| 6 | `XSM` | The northwestern religious-military network, which later splits into `NXM`, `GSM` and `KHM` | A tag that must spawn its own successors rather than be spawned | NCNS split rules |
| 7 | `SIC` | Sichuan's garrison-district system, where the province is many commanders and no ruler | The only identity with no single leader; cohesion must be modelled per commander, not per tag | Cohesion rework |
| 8 | `GDC` | Chen Jiongming's federalist Guangdong | The only warlord whose national programme is the opposite of unification: a federal south | None |
| 9 | `XIC` | The Guominjun, then the Northeast Army | Two unrelated armies share the tag, and the second arrives after the first collapses | Master plan open question 1 |
| 10 | `ZHL` | Zhili: the clique that holds the seat and loses it | Cannot exist until the tag exists | Tag creation |
| 11 | `ANH` | Anhui: the clique that loses the seat in 1920 and returns as a provisional government in 1924 | Same | Tag creation |
| 12 | `FNG` | Fengtian: the only clique that reaches the Grand Marshal government | Same, plus the 1931 army conversion to `XIC` | Tag creation |
| 13 | `HBC`, `KHM`, `NXM`, `GSM`, `KUM` | The 1930s regional actors who exist only at the vanilla floor | Vanilla already owns them; the pre-1936 slice is the frontier variant of slice 5-6 | Vanilla parity review |

**No focus-count target is set for any slice.** The master plan's approximate volume table is a planning aid, not a quota. **[plan]** §13.2.

---

## 16. What this design refuses to do

1. **No focus-count target.** A band gets the focuses its content needs and no others.
2. **No 1936 leader before their era, and no leader before 1936 who is already recruited by 1936 history.** SHX's leader is the exception that proves the rule: he is the same man from 1911, so the release effect recruits him once, guarded, and never twice.
3. **No artwork change and no new icon collection.** The pilot reuses `GFX_portrait_yan_xishan`, the existing `SHX_model_governor` trait icon and the existing vanilla focus icons. Any icon that does not exist is named as a requirement and returned to the Director; none is created here.
4. **No duplicate of an existing warlord branch.** SHX has no identity branch in `china_warlord_sea_focus`, and this design does not add one; the 1936 handover is left untouched.
5. **No new tag, and no claim that `ZHL`, `ANH` or `FNG` exist.**
6. **No edit to `rch_warlord`.** That tree is clean, validated, and belongs to the *seat holder*; SHX is not the seat holder in the historical line.
7. **No second Chinese-country list.** The ten-tag `rch_chinese_war` set is reused.
8. **No world-iterating on_action.** Only `on_daily_SHX`.
9. **No balance of power,** so the mechanic is DLC-independent.
10. **No claim of playability.** No launch, no save, no observation. Every number here is a starting value.

---

## 17. Assumptions needing a Director decision

| # | Assumption | Why it needs you |
| --- | --- | --- |
| A1 | The pilot slice creates `china_release_warlord` as the generic effect, with SHX as first consumer, and C6 later adds tags instead of rewriting it. | The master plan assigns that effect to C6, which is behind C4. Two owners would be worse than one early owner. |
| A2 | The seat rule and the reunification payoff are written against `china_seat_holder` and `china_reunified_by`, which do not exist. | If the pilot must land before C1, the alternative is a country-scoped `warlord_seat_won` flag that C1 later reads. That is a fallback and I will not take it without your word. |
| A3 | SHX is accepted as pilot ahead of the master plan's `ZHL` row. | It reverses the plan's ordering, for the tag-availability reason in section 2.2. |
| A4 | The S2 clique-war band accepts a reduced historical roster (XIC, CHI, SND) until `ZHL`/`ANH`/`FNG` exist. | It is the difference between a plausible S2 and a historical one. |
| A5 | The 1928 boundary is the code boundary (1928.1.1), not the historical seat transfer (June 1928). | It keeps one router calendar for the Republic and the warlords; the five months are covered by a bypass. |

---

## 18. Validation the implementation slice must run

- `hoi4.focus_inspect` per tag for each new tree; layout rules from `hoi4-focus-trees`; no new tree above the measured `rch_warlord` crossing count without a reason.
- `hoi4.source_lookup` for every new symbol, and for every retired one.
- `hoi4.script_validate` on the new effects and triggers.
- `hoi4.event_inspect` on the twelve events, with every option's trigger and effect checked.
- `hoi4.decision_inspect` on the patronage category: availability, visibility and the debt tooltip.
- `hoi4.probability_inspect` on the seat bid and the patron choice, with before and after evidence.
- Localisation reference check for every key in section 13, in English only.
- A scenario table proving that SHX resolves to exactly one tree in each band, and that 1935.12.31 routes to the Endsieg band while 1936.1.1 routes to vanilla.
- A guard test proving the release effect cannot run twice and cannot recruit the leader twice.
- `error.log` from the user's own run, read afterwards, never generated by an agent.

No in-game, panel-render or AI-campaign observation has been performed and none is authorised by this card.

---

## 19. MCP routes run on this card

| Route | Argument | Result |
| --- | --- | --- |
| `hoi4.focus_inspect` | `treeId = china_warlord_sea_focus` | 155 focuses, 48 columns, 227 crossings, 67 too-close pairs, 202 blocking diagnostics; `validation.passed = false`. Used to establish that the 1936 warlord tree has no room and no SHX branch. |
| `hoi4.focus_inspect` | `treeId = rch_warlord` | 50 focuses, 0 too-close pairs, 6 crossings, `validation.passed = true`. Used to establish that the seat tree is not where SHX belongs. |
| `hoi4.source_lookup` | `symbol = SHX_yan_xishan` | Two definitions: the mod's `common/characters/SHX.txt:2-32` and the overridden vanilla `common/characters/Warlords_China.txt:1719-1750`. The mod override omits `traits = { SHX_model_governor }`; the trait exists at `common/country_leader/00_traits.txt:938`. |
| `hoi4.source_lookup` | `symbol = SND` | Zero definitions, 2582 unresolved references. Tags are not indexed as symbols; the tag roster was verified from `common/country_tags` by direct read instead. One attempt, no retry. |
| `hoi4.reference_search` | `load_focus_tree keep_completed completed focuses`, wiki | Confirmed `keep_completed` and the shared-focus pattern, and the `mark_focus_tree_layout_dirty` caveat, from the offline snapshot. |
| `hoi4.reference_search` | `autonomy_level subject puppet autonomous state`, wiki | Returned nothing on the first wording; the corrected query `autonomy subject level` returned `set_autonomy`, `autonomy_gain`, `on_subject_autonomy_level_change` and the autonomy-state modding page. One corrected retry, as allowed. |

MCP is not engine proof. Every claim it supports is also cited to a file, and the one claim it corrected — that tags are not lookup symbols — changed how the rest of the verification was done.

---

## 20. Diagnostics raised, outside this card's ownership

Recorded for the Director, not fixed here.

- **D1.** The mod's `common/characters/SHX.txt:2-31` overrides vanilla's `SHX_yan_xishan` and drops `traits = { SHX_model_governor }`, which vanilla's copy carries. The trait exists in the mod at `common/country_leader/00_traits.txt:938`. Either the override is intentional and the trait is granted elsewhere, or a vanilla leader trait is silently lost. Owner: whoever owns the character file, not this card.
- **D2.** The master plan's §9.1 claim that "the existing Endsieg autonomy levels" live in `common/autonomous_states` is wrong for this checkout: the mod ships no such directory. The only warlord autonomy levels are vanilla's, gated on NCNS. Any design that assumes a mod-local autonomy ladder needs correcting.
- **D3.** `china_warlord_sea_focus` carries 202 blocking focus diagnostics and 67 too-close same-row pairs. That is pre-existing and not mine to fix, but it rules out adding a per-tag branch to it.
