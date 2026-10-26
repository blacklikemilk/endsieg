# The Electoral Law in Spain, 1910-1936

> Status: design proposal delivered 2026-10-26. Director accepts the direction but not yet as source design; independent QA and the four open questions at the end are pending. Do not implement from this file until that disposition is recorded.

A design for the franchise as a contested law rather than a bill that counts itself.

## The bill that passes itself

`spain_bill_count_electoral` adds the government and every bench outside it.
Those are all seven parties, so `spain_bill_votes` is 400 in every configuration of the chamber, `spain_bills.6.a` always clears its 201-seat trigger, and the watered and withdrawn options exist only because the player may choose them.
The count is not a count; it is a formality wrapped around a decision the player has already made, and the chamber never gets to disagree.

That matters more here than for any other bill, because the electoral law is the one bill that decides who sits in the chamber next time.
Every other bill spends money, land, autonomy or credits.
This one spends seats, and every bench in the room knows it.

## What the law is for

The electoral law should be the payoff of chamber-building.
A government spends a chapter assembling a majority, buying benches and holding elections, and the law is what it does with the majority once it has one.
The player should be able to lose it, to carry a version of it that is not the version they wanted, or to trade something permanent for it — and the reason should always be legible in the chamber's arithmetic.

So the design makes one structural move and follows it wherever it leads:

> An electoral law is not one bill.
> It is a choice of *which* reform the chamber will carry, followed by a second vote in the body that the reform has to get past.

The first reading is where the player discovers what their chamber actually wants.
The second reading is where the constitution, the Crown or the committee takes its cut.

## The three projects

Three electoral projects were live in this Spain, and they are not three flavours of the same reform.
Each one changes a different thing, each one is carried by a different coalition, and each one leaves the country in a different place.

### Sufragio — widen the electorate

Spain had universal male suffrage from the law of 26 June 1890, and the law did not democratise anything: the cacique networks simply extended to the five million new voters, and governments were still built before the elections rather than after them.
So in the Restoration the widening that remains is the women's vote, which is a radical act rather than a liberal one, and it is the Republic's question, not the Restoration's.

In the Republic it is the argument of 1 October 1931.
Clara Campoamor carried the article by 161 votes to 121 against Victoria Kent, who wanted the vote postponed because the Church, the husband and the father would decide for the woman at the ballot box.
Campoamor's own Radical party voted against her.
The right voted for her, because it expected exactly what Kent feared.
That is the whole design of this project in one sentence: **the left writes the widening and the right wins the first election held under it.**

Widening changes who may vote.
It does not touch the register, the districts or the count.

### Censo — cleanse the register

Maura's law of 8 August 1907 made the vote compulsory, moved the validation of disputed acts to the Supreme Court, and — through Article 29, promoted by the republican Gumersindo de Azcárate — declared a candidate elected without a vote wherever the number of candidates did not exceed the number of seats.
The article meant for clean elections became the machine's most efficient instrument.

Cleansing the register is the technical reform: a poll book taken out of the Ministry of the Interior's hands, Article 29 abolished, the provincial juntas answerable to the courts.
It does not change who may vote.
It changes whether the vote is counted, and it is the only one of the three projects that hurts the government that brings it.

### Prima — restrict and premium

The Republic rewrote the electoral procedure on 27 July 1933: a list needed 40 per cent in the first round, only lists above 8 per cent entered the second, and the largest list took a premium of seats out of all proportion to its votes.
Azaña's government wrote it expecting to win under it, and the right won the landslide in November 1933.

The premium is the project of a government that expects to be the largest list and wants the expectation written into law.
It is the easiest of the three to pass and the hardest to survive, and in the Republic it is the moment the Republic stops being a fair contest.

## Why the chamber votes as it does

Every bench now votes on whether the project helps it, and the support tables below are the design's core.

Parties are the existing ids: 1 monarchists, 2 liberals, 3 conservatives, 4 republicans, 5 socialists, 6 carlists, 7 falange.

### Who carries each project

| Project | Committed benches (base) | The bench that can still be bought (swing) | The price |
| --- | --- | --- | --- |
| Sufragio | Liberals, Republicans, Socialists in the Restoration; Republicans and Socialists in the Republic | Conservatives, in the Republic only | The Church's schools are left standing, and the religious question is not opened |
| Censo | Liberals, Republicans, Socialists, and the Conservatives **while the government has not used the machine** | Conservatives, when they are not already committed | The Senate keeps its own franchise, so the reform stops at the Congress |
| Prima | The government bloc | The largest bloc outside the government | The premium covers the two largest lists, not only the first |

### Three rules that do the work

**The government must have a bench in the project.**
A government cannot bring a franchise law that no party in it supports; the decision is not offered, and the tooltip says the question has to be raised by a party that is in the government.
This is what stops a conservative cabinet from legislating women's suffrage by accident, and it is why the player's first task is usually a coalition rather than a bill.

**The machine poisons the clean register.**
The Conservatives join the Censo base only while `spain_elections_managed` is not set and the government has not been buying benches through `spain_campaign_finance_count`.
A government that has run the machine loses its own reform's most important ally, and must then buy the Conservatives by conceding the Senate — which produces a watered law.
The player's own earlier choices decide whether a clean register is available at all.

**The premium belongs to a government that can already command the chamber.**
Prima is offered only to a government holding 201 seats or more, because a government that cannot carry the chamber cannot rewrite the seat conversion in its own favour.
A minority government has no business writing itself a premium, and the design says so by refusing the decision.

### The gate

The other five bills open when the base bloc is within `bill_negotiation_reach` of a majority, and the negotiation does the rest.
The electoral law opens only when a majority is actually reachable: `max(base, swing) ≥ 201`.

The difference is deliberate.
A government may bring a budget it expects to lose and let the chamber decide.
It does not put its own dissolution on the floor without the votes, and a bill whose every path stops short of 201 should not be bringable at all — the player would only be buying a 40-day humiliation.
This also gives the electoral law a gate that does not depend on the floor question S7 left open for the Director.

## The first reading

The decision fires one event.
The event counts all three projects live into three separate totals, and each project becomes an option only if its own arithmetic reaches the bar.

- **Carry the project as written** — offered when that project's base reaches 201.
- **Take the concession** — offered when the base falls short but base plus the swing bench reaches 201.
- **Water the project down** — always offered, and it is a real law with a reduced effect, not a consolation prize.
- **Withdraw** — always offered.

The three projects share one event because they are one bill before the chamber; the option set is what differs.
The event text names the chamber's arithmetic and the project that the numbers favour, so the player learns to read their own chamber instead of guessing.

Bringing the bill costs political power and, for the first time in this decision category, a non-political cost: the government stakes its standing on the vote and loses stability whatever happens next.
The political-power cost differs by project, because the constitutional fight, the technical reform and the self-serving bargain are not the same purchase.

## The second reading

The project that clears the Congress has not become law.
It goes to the body that the reform has to get past, and that body is different in each chapter, because the Spanish constitution was different in each chapter.

### The Restoration: the Senate

The Constitution of 1876 made the Cortes two colegislative bodies *equal in faculties*: the Congress of Deputies and the Senate.
Article 20 built the Senate from three benches — senators in their own right, life senators appointed by the Crown, and senators elected by the corporations of the state and the largest taxpayers — and capped the first two at 180, which was also the number of the elected bench.
The Senate is therefore 360 seats, half of them the Crown's to appoint, and the elected half chosen by a censitary electorate that the left cannot reach.

The design reads that structure rather than inventing a chamber: 360 seats, 181 to carry a bill, in three parts.

- **The Crown's 180.** How many of them follow the government depends on the Crown-Cortes balance, which the script can read through `power_balance_value` on `SPR_crown_and_cortes`: the nearer the Crown is to ruling alone, the more of its senators it spends; the nearer the Cortes is to sovereignty, the more of them abstain rather than be seen voting for a lost cause.
  A minority government also loses part of this bench, because the Crown does not spend its Senate on a cabinet that may not survive the month.
- **The elected 180.** A proportional mirror of the Congress, filtered by the censitary franchise: the republican and socialist benches count at half weight, because the corporations and the largest taxpayers do not elect them.
- **The bar.** 181 of 360.

The Senate carries the bill, rejects it, or amends it.
When it rejects, the government has three ways out:

- **A joint session.** The Constitution gives the two houses equal faculties, so a deadlock is resolved by sitting them together: 760 votes, 381 to carry. The Congress's arithmetic dominates, but the Crown's 180 still sit in the room. This is the only way to force a franchise law past a hostile upper house, it moves the Crown-Cortes balance sharply toward the Cortes, and it costs stability and feeds coup pressure. The Crown does not forget being outvoted in its own chamber.
- **Accept the amendment.** The Senate strikes the clauses that touch its own franchise and its own electorate. The law passes and it is not the law the government wrote: the reform is watered, and the upper house keeps the bench that the reform was meant to reach.
- **Withdraw.** The bill dies after clearing the Congress, which is the most expensive failure available.

The joint session is the design's answer to the awkward fact that a chamber cannot reform a constitution alone.
A government with a large Congress majority can override the Senate and pay for it; a government with a narrow one cannot, and has to accept the amendment.

### The Republic: the committee

The Republic abolished the Senate — Article 51 puts legislative power in a single Congress of Deputies — so there is no upper house to lose the bill in.
What there is, is the committee.

Bills go to a Comisión, which reports a dictamen, and the plenary then votes the dictamen.
A committee is small and apportioned by the chamber's shares, so a government with a bare majority can easily be a minority in the room where the text is actually written.

The design makes that literal: a committee of 21, apportioned from the Congress by proportional share, 11 to carry the dictamen.

- A republican-socialist government controls it.
- A single-party republican government does not.
- A conservative government in a chamber with a large left does not.

When the committee does not carry the government's text, the government has three ways out:

- **Accept the dictamen.** The committee's amended text is the law: the reform is watered, and the government has been outmanoeuvred in a room of twenty-one people.
- **Make it a question of confidence.** The government ties the vote to its own survival and the plenary restores the original text. A government with 201 seats carries it; a minority government carries it only if the bill's own supporters reach 201 in the plenary, and pays stability, party support and the risk of a failed confidence motion. A failed confidence motion is the worst outcome in the chain: the bill dies, the government is marked, and the army reads it.
- **Withdraw.**

The committee is the Republic's answer to the same problem the Senate poses in the Restoration: a chamber's majority is not the same thing as control of the place where the text is written.

## What each outcome leaves behind

Effects are meant to be felt in the next election, not read as a modifier.

| Project | Carried as written | Watered |
| --- | --- | --- |
| Sufragio | The franchise is widened and the register rewritten: the existing `spain_electoral_reform` shift stands, `spain_women_suffrage` becomes a seat-level fact (the socialist benches gain some, the Conservative and Carlist benches gain more, because the Church's women vote), the Cortes gains authority over the Crown, and the country goes to the polls | The vote goes to women who are heads of household or literate, the chamber's franchise is unchanged in law, `spain_women_suffrage` is not set, the seat shift is a fraction of the full one, and the government gets no credit |
| Censo | `spain_clean_register`: the managed-election bonus is struck out of the recount, the machine's benches lose ground to the republicans, liberals and socialists, and the government takes the credit | The register is cleaned in the Congress districts only: the Senate's electorate and the rural book survive, the managed-election bonus stays available, and the reform is half a reform |
| Prima | `spain_electoral_premium`: the recount gives the largest bloc a large premium and the second a smaller one, the left loses support, and the Crown gains from a chamber that has rigged itself | The premium covers the first list only, the second-list benches are alienated rather than bought, and the effect is roughly half |

The watered tier is where the design earns its keep.
Every one of the three projects has a version that is recognisably the same law and recognisably not worth what the government paid for it.

## Two laws per campaign

A country does not rewrite its franchise indefinitely, but it does rewrite it twice in this period: 1907, then 1931, then 1933.

The design allows two electoral laws.

- The first law may take any project the chamber will carry.
- The second law requires that at least one election has been held under the first, and it must take a **different** project. It replaces the first law's flag rather than stacking with it.
- After the second, the question is settled and the decision leaves the order paper for good.

This is what makes Sufragio and Prima a sequence rather than two unrelated buttons: a Republic that widens the franchise in 1931 and then writes a premium in 1933 has played the actual history, and the 1933 election then lands on a chamber that the premium has already distorted.

## The second law's arithmetic, worked

The figures below are anchors computed from `spain_cortes_recount` as it stands after S7, at the opening Restoration and opening Republic seat distributions.
They exist to show that the design does what it claims; the implementation re-derives them and the constants carry the tuning.

Opening seats — Restoration: monarchists 129, liberals 97, conservatives 81, republicans 48, socialists 26, carlists 16, falange 3.
Opening seats — Republic: monarchists 16, liberals 30, conservatives 82, republicans 130, socialists 110, carlists 25, falange 7.

**A majority government, Restoration, monarchists and conservatives in coalition (210 seats).**
Sufragio is not offered, because no party in the government supports it.
Censo: base 171 with the machine running, 252 without it; with the machine running the Conservatives are the swing bench and their price is the Senate.
Prima: base 210, clean pass.
The chamber offers a premium law and a technical reform, and refuses the widening.

**A minority government, Restoration, monarchists alone (129 seats).**
The government has no bench in any of the three projects, so the question cannot be raised at all.
The electoral law is a wall for a minority Restoration cabinet, and the political route — the `SPR1_electoral_reform` focus — is what it has instead.

**A reformist Republic, republicans and socialists in coalition (240 seats).**
Sufragio: base 240, clean pass, with the Conservative benches available as a cynical second concession.
Censo: base 270, clean pass.
Prima: base 240, clean pass.
The committee apportions 7 republicans, 6 socialists, 4 conservatives, 2 liberals, 1 carlist, 1 monarchist: the government holds 13 of 21 and the dictamen is its own.
Everything is available and the choice is the whole point of the chapter — and every one of the three fires an election that the incumbent may lose.

**A conservative blocking chamber, Republic, conservatives, carlists, monarchists and falange (130 seats).**
Sufragio is not offered, because no party in the government carries it, and 130 seats does not qualify for Prima.
Censo is offered, because the Conservatives are a nominal carrier of the clean register — which is Maura's own law — and with the machine clean the base is the whole left plus the Conservative benches, 352 seats.
So the government carries a law that most of its own party dislikes, on the left's votes, and then loses the committee: the conservative benches hold 6 of 21, the dictamen is rewritten, and the government must accept the amendment or burn a confidence motion it can only win on the bill's own supporters.
That is the blocking chamber's real failure: not that it cannot legislate, but that it legislates something it did not write.

Sufragio deserves its own note.
In the Restoration its base is 171 seats with no bench left that can be bought, so no chamber this chapter can produce will carry the widening, and the design says so plainly rather than pretending a doomed bill is available.
The franchise question belongs to the Republic; the Restoration player who wants reform has the `SPR1_electoral_reform` focus and the political route it represents.

**The Senate, worked.**
On the Restoration opening seats the elected 180 apportion to 65 monarchists, 48 liberals, 40 conservatives, 12 republicans, 6 socialists, 8 carlists, 1 falange, after the censitary filter halves the left.
A Censo bill brought by a clean monarchist-conservative government has 106 elected senators and a deadlocked Crown bench of 110: 216, and the Senate carries it.
The same bill brought by a government that has run the machine has 66 elected senators and 110 Crown senators: 176, short of 181, and the Senate rejects it.
The joint session then sits 760 and needs 381: the clean bill has 468 and passes; the machine's bill has 347 and dies.
The machine costs the government its law twice, once in each house.

## Interactions

**`spain_bill_swing_votes`** keeps its meaning: the true ceiling of the bill, base plus the purchasable bench, counted once.
The electoral law adds no second copy of any bench; the three projects are three separate counts, and only the one being voted is written into the cache the decision reads.

**`spain_government_seats`** stays the government's own standing and enters the count as the government bloc, never as the whole chamber.
A government below 201 seats can carry an electoral law when the chamber's benches do, which is the point of interest-based counting.

**`spain_electoral_reform`** remains the Restoration's declaratory reform and keeps its recount branch.
Sufragio adds to it rather than replacing it, so a country that took the focus and later carried the law is a country that reformed twice.

**`spain_women_suffrage`** is set today by `SPR3_women_suffrage` and read by nothing.
The design gives it a seat-level consequence in the recount, which makes the existing focus mean what its name says without touching the focus.

**`spain_hold_election`** runs after the law is applied, so the first election is fought under the new franchise — and it already applies the incumbent penalty when the government is a minority or stability is low, which is what makes a reform election dangerous for the reformer.

**The Crown-Cortes balance** is read, never written, by the Senate stage: `power_balance_value` supports only `>`, `<` and `=`, so the three bands are strict inequalities with a fall-through.
The joint session and the override write into the balance through the existing push effects.

**`spain_elections_managed`** and `spain_campaign_finance_count` are the machine's fingerprint: they remove the Conservatives from the Censo base and they gate the managed-election bonus once a clean register exists.

**Chapter transitions.** The second reading checks the chapter when it fires.
If the Restoration has become the Republic in the meantime, the Senate stage does not run and the committee stage does, on the same first-reading result — the Constituent Cortes inherits the bill, which is what happened.
If the Cortes is dissolved, the chain ends and the pending flag is cleared; no outcome effect is applied to a chamber that is not sitting.
Every terminal path clears the pending flag, so a hung second reading cannot outlive its chapter.

## AI

**The decision.** Base willingness is moderate, and it is shaped by whether the chamber can carry a project, not by whether the AI likes reform: a government does not bring a franchise law it cannot pass.
Willingness rises when a project's base already holds a majority, because the law is then cheap; it rises further for a minority government whose chamber is hostile, because a new chamber is the only way out; it falls when stability is low, because a government does not dissolve itself in a crisis; and it collapses once the two-law limit is reached.

**The options.** The clean pass is preferred whenever it exists.
The concession is preferred next, weighted up when the price is cheap for the AI's own project — the Conservatives' price for Censo is cheap to a monarchist government and expensive to a republican one, and the reverse for Sufragio.
Watering down is preferred to withdrawal unless the project is the government's signature policy, in which case a watered law is worse than a clean defeat.
Withdrawal is weighted up only when the second reading has already refused the bill and the joint session or the confidence motion is arithmetically lost.

**Named scenarios.**

| Scenario | Expected ordering | Failure condition |
| --- | --- | --- |
| Majority government in the Restoration (210 seats, machine running) | Prima clean, then Censo concession, then watered, then withdraw; Sufragio never offered | The Conservatives refuse the Senate price, Censo falls under 201, and the AI takes the premium instead |
| Minority government in the Restoration (129 seats) | No project available; the AI does not spend the political power, and if it is offered nothing it does not take the decision | The tooltip states that the question needs a party in the government; the AI's decision weight stays at zero while nothing is available |
| Reformist Republic (240 seats) | Censo clean, then Sufragio clean, then Prima clean; the AI prefers Censo unless it expects to be the largest list | The committee refuses the dictamen and the government is a minority, so the confidence motion fails and the bill dies |
| Conservative blocking chamber in the Republic (130 seats) | Censo clean, then the committee's amendment, then the confidence motion, then withdrawal; Sufragio never offered and Prima refused for want of 201 seats | The committee apportions the government only 6 of 21, so the law it carried is rewritten before it is law |

An AI that finds itself with a majority and a machine should be visibly tempted by Prima, because that is the historical mistake and the design should let the AI make it.
The premium's own consequence — the amplified election under an incumbent penalty — is the corrector, not a hidden refusal.

## Text direction

**Viewpoint and voice.** The narrators are the men who draft electoral law: a Ministry of the Interior official in the Restoration who knows exactly which districts the article will silence; a deputy in the Constituent Cortes who has to decide whether the woman at the ballot box will vote for the Church; a minister in 1933 doing arithmetic on the back of a decree.
The chamber is a place with a gallery, a clock and a clerk, not a spreadsheet.

**Restoration.** Procedural, courteous and cold.
The vocabulary is administrative — the poll book, the provincial junta, the act, the district, the article.
The horror is that nobody in the room thinks they are doing anything unusual.
Irony is allowed and should be dry: a government explaining a law that disenfranchises five million people as a technical improvement to the register.

**Republic.** Argumentative and moral, and then abruptly arithmetical.
Sufragio should sound like a genuine dispute between people who agree on the goal and disagree on the timing — the fear is not reaction, it is that the Republic will lose.
Prima should sound like modernisation, because that is what its authors called it.

**What stays uncertain.** The Senate's mood, the committee's arithmetic and the Crown's willingness are shown through what people say in the corridors, not through a counter.
A hostile upper house should be visible as a dinner, a word from a grandee, a senator who is cordial and immovable.
The player should work out that the law is in trouble before the vote, from the way the count does not add up.

**What the text must not do.** It must not announce that a chamber is hostile, that a vote is a trap, or that a reform will backfire.
Sufragio's consequence appears as the result of the next election, not as a prediction attached to the option.

**Cultural reference directions requiring research before wording.** The encasillado and the pucherazo; Article 29 and the candidate proclaimed without a vote; the *cacique* and the *diputación provincial*; the compulsory vote and its fines; Campoamor's and Kent's actual arguments; the Radical party voting against its own deputy; the Church's schools as the price of the conservative vote in 1931; the 40 per cent and the 8 per cent of the 1933 decree.
Any quotation must be sourced, translated and attributed; none is drafted here.

**Option families.** Each project needs one option that means *this is what the chamber can carry* and one that means *this is what it costs to carry it*.
The concession option should sound like a bargain struck in a corridor, not like a purchase.
The watered option should sound like a law that has been edited by someone else.
The withdrawal should sound like a government deciding how much of its authority to leave on the floor.

## Presentation

No new interface and no new artwork.
The Cortes panel already draws the chamber; the second reading is reported through the event text and the option tooltips, with the Senate's three benches and the committee's twenty-one seats shown as numbers in the tooltip rather than as a new window.
The existing decision icon, the existing report pictures and the existing category stay exactly as they are.
The Senate's and the committee's arithmetic are exposed through scripted localisation strings reading the working variables, so the player sees the count that decided the vote.

## What the player learns

The electoral law teaches the chamber.
After one attempt the player should know which benches carry a franchise, which bench can still be bought, what each bench charges, and which house or committee will take a cut.
That knowledge is what makes the second law, and the rest of the bill category, play differently.

## Acceptance criteria

1. `spain_bill_count_electoral` no longer adds every party: each project's base is the committed set from the support table, and the base can be below 201.
2. `spain_bills.6` offers the clean option only for a project whose base reaches 201, the concession only for a project whose base plus swing reaches 201, and the watered and withdrawn options always.
3. The decision is not offered when no project can reach 201, and the tooltip explains why.
4. Bringing the bill costs political power and a non-political cost, and the political-power cost differs by project.
5. A government with no bench in a project cannot bring it, and the tooltip says so.
6. Censo loses the Conservatives from its base while `spain_elections_managed` is set or the government has been financing benches.
7. Prima is offered only to a government holding at least 201 seats.
8. A Restoration bill that clears the Congress fires the Senate stage; a Republic bill fires the committee stage; a chapter change between the two readings swaps the stage and does not drop the bill.
9. The Senate stage computes 360 seats from the three Article 20 benches, reads the Crown-Cortes balance through `power_balance_value`, and carries at 181.
10. A rejected Senate bill offers the joint session at 381 of 760, the amendment, and withdrawal; the joint session moves the Crown-Cortes balance toward the Cortes and costs stability and coup pressure.
11. The committee stage computes 21 seats from the Congress shares and carries at 11; a refused dictamen offers acceptance, a confidence motion and withdrawal, and a failed confidence motion is the harshest failure in the chain.
12. Each project's carried and watered effects are both applied through the recount, and the watered tier is visibly less than the full one.
13. `spain_women_suffrage`, `spain_clean_register`, `spain_electoral_premium` and their watered counterparts each have a recount or election consequence.
14. Two laws per campaign: the second requires an election in between and a different project, and it replaces the first.
15. Every terminal path clears the pending flag; a dissolved Cortes applies no outcome.
16. No other bill's count, gate, cooldown or effect changes.
17. No focus, icon, localisation file or art asset is changed by this design except the new keys the bill needs.

## MCP evidence plan

Run these before the source edits and again after, on the same selectors, and record the revision.

- `hoi4.event_inspect` with `mode: "lint"` on `spain_bills.6`, then on each new second-reading event, and `mode: "trace"`, `direction: "downstream"` on `spain_bills.6` to prove the two stages connect. The inline lint summary reports counts and diagnostics but not option triggers, so option triggers must be read from `events/spain_cortes_bills.txt` directly.
- `hoi4.decision_inspect` with `mode: "inventory"`, which works. `mode: "inspect"` with scenarios is blocked in this install by `PROBABILITY_GAME_VERSION_UNSUPPORTED` (adapters verified for Operation Postern 1.19.2.0, installed game 1.19.3.0), so the gate must be proved by reading the decision source and by the arithmetic checks below, not by the scenario route.
- `hoi4.script_validate` on `common/scripted_effects/spain_cortes_bills.txt` and on `events/spain_cortes_bills.txt`: the baseline today is `totalFindings 0` with `SCRIPT_CHECK_PARTIAL`, 313 commands checked and 143 argument blocks unchecked, so a clean result is a floor and not a proof.
- `hoi4.source_lookup` on `spain_bill_count_electoral`, `spain_electoral_reform`, `spain_women_suffrage`, `spain_elections_managed` and `power_balance_value` to confirm every caller before and after.
- `hoi4.reference_search` for `power_balance_value` and `hoi4.reference_read` on the hit, to hold the strict-inequality reading of the balance trigger against the installed game documentation and the offline wiki.
- `hoi4.focus_inspect` is not required: this design changes no focus.

The arithmetic must also be re-derived from the final script by hand or by a small parser, because no MCP route computes seat totals.
That check is the one that catches the class of error S7 fixed.

## Designed, verified, and not yet played

**Designed here.** The two-reading model, the three projects, the support and swing tables, the machine rules, the availability rules, the Senate and committee arithmetic, the effects of each outcome, the two-law rule, the AI expectations and the acceptance criteria.

**Verified from source and the installed game.** That `spain_bill_count_electoral` adds all seven parties and therefore always totals 400, and that `spain_bills.6.a` is therefore always offered; the seat normalisation, the seven party ids and the government bloc arithmetic; the decision gate and the 40 political power and 365-day re-enable; the existing cooldown, credit, penalty and recount effects; that `spain_women_suffrage` is set by `SPR3_women_suffrage` and read nowhere; that `SPR1_electoral_reform` sets `spain_electoral_reform` and is mutually exclusive with the electoral machine; that `power_balance_value` compares a balance value with `>`, `<` or `=` only; the Article 20 composition of the Senate, the 1890 law, the 1907 law and its Article 29, the 1 October 1931 vote and the 1933 decree, from the sources named in the text.

**Not verified and requiring a live game.** That the event renders with the right numbers and option set; that the tooltips read the working variables without truncation; that the joint session and the confidence motion land on the intended side of their thresholds in an actual session; that the AI's decision weight actually falls to zero when no project is available; and that the first election under each project produces the intended chamber.
No launch was performed for this design.

## Open questions for the Director

1. **The gate.** The electoral law is designed to open only when a majority is reachable, while the other five bills open at the 161 floor. That is deliberate, but it means one decision in `SPR_cortes` has a different gate shape from its siblings, and the S7 floor question remains open for the other five.
2. **Ownership of the recount branches.** The design needs three new branches in `spain_cortes_recount` (and the gating of the managed-election branch). That file belongs to the Cortes seat model; if it is owned elsewhere, the branches need an owner before implementation.
3. **`spain_women_suffrage` becoming live.** The change makes the existing `SPR3_women_suffrage` focus stronger without editing it. That is a balance change to an existing focus reward and needs a decision.
4. **Two laws per campaign.** The card allows one coherent model; two laws is not one, it is one model with a sequel. If the Director prefers a single law per campaign, the two-law rule is the section to cut and everything else stands.
