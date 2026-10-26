# Negotiating with the Great Game

Four demands, each with seven ways to answer, one held at a time.

The Great Game tracks how much of Iran each patron controls; this layer is about the moment a patron turns that control into a demand on paper.
A demand is one event with up to seven visible options, resolved once, after which the table closes for a year and a half.
Nothing here repeats, and nothing pays twice.

## One demand at a time

`iran_negotiation_tick` runs on the daily Iran tick, as the first line of `iran_campaign_tick`.
It returns immediately while `iran_negotiation_open` (a demand is on the table) or `iran_negotiation_cooldown` (a demand was resolved recently) is set; both are flags with durations, so nothing is cleared by hand.

When the table is clear it walks four demand windows in order and fires at most one:

| Demand | Window | Patron | Asks for |
| --- | --- | --- | --- |
| `iran_n.1` the railway convention | 1912-1914 | the northern power | railway to the Caspian, Caspian carrying trade, Cossack Brigade subsidy |
| `iran_n.4` the Gulf and the telegraph | 1912-1914 or 1916-1918 | Britain | Gulf anchorage, Bushire garrison, telegraph in perpetuity |
| `iran_n.7` the Caspian fisheries | 1922-1932 | the Soviet state | fisheries and the Gilan trade route, against recognition |
| `iran_n.10` the German offer | 1936-1940 | Germany | a commercial treaty, machine tools, an institute |

Each fires only if its patron passes the same validity checks the rest of the tree uses (`iran_sponsor_britain_valid`, `iran_sponsor_germany_valid`, or the equivalent test written inline for the north), and only if the player has not already signed the corresponding Great Game agreement.
The northern patron is tag `SOV` in this mod: `RUS` is Reichskommissariat Nordamerika, and no Iran content tests it.

## The seven answers

Every option carries its own trigger, so only coherent answers appear.

1. **Accept** - concedes to the patron (`iran_concede_*`), adds a named obligation (an `add_timed_idea` or a flag such as `iran_obligation_russian_railway`), and sets `iran_demand_<id>_accepted`.
2. **Submit to the Majlis** - shown instead of Accept when the chamber is strong (`power_balance_value > negotiation_majlis_block`). It sets `iran_demand_<id>_submitted` and fires a vote 75 days later; the deputies ratify or refuse by balance side and by the patron's standing (the German treaty reads `iran_german_influence`, because Germany has no standing value). One of the two vote options is therefore always available: the standing tests are complementary.
3. **Sign by royal decree** - shown when the Crown is strong (balance below `negotiation_crown_bypass`). Same concession, plus `PER_bop_push_crown_small`, a stability cost, and `iran_decree_treaty`, which the vote events read: a chamber asked to ratify a treaty signed behind its back refuses more readily.
4. **Refuse** - `iran_reclaim_<patron>_small`, the patron's standing falls, `iran_demand_<id>_rejected`. A second demand follows 200 days later only if the patron can still apply pressure: it must exist, answer to nobody, not have capitulated, and not be at war with Germany. A patron that cannot is simply refused.
5. **Compromise** - a smaller concession and a named counter-term, different per demand: a Persian railway company with Russian minority shareholders, the customs retained, a joint fisheries company, advisers without a treaty.
6. **Delay** - once per demand. Costs authority and stability and re-fires the same event in 120 days with the compromise off the table and the concession a tier heavier.
7. **Seek support** - only when a rival patron is valid. The rival concedes instead (`iran_concede_<rival>_small`), the original demand is dropped, the original patron's standing falls sharply and `iran_patron_tension_<patron>` is set for four years.

The accept and compromise options set `iran_demand_<id>_binding` for 1095 days. That flag is what the renegotiation decisions wait for.

## Escalation

Demands 1-3 have one escalation event each (`iran_n.3`, `iran_n.6`, `iran_n.9`), scheduled from the refusal, once per demand, with two options instead of six: sign on the patron's terms, a full tier heavier, or refuse again.
Escalation events carry their own `trigger`, so if the patron has collapsed or is at war with Germany in the meantime the event simply does not fire and the refusal stands.

## Renegotiation

Six decisions in the existing `iran_great_powers` category:

| Decision | Visible when |
| --- | --- |
| `iran_renegotiate_russian_railway` | accepted, and its binding flag has lapsed |
| `iran_renegotiate_british_gulf` | accepted, and its binding flag has lapsed |
| `iran_renegotiate_soviet_caspian` | accepted, and its binding flag has lapsed |
| `iran_renegotiate_german_pact` | accepted, and its binding flag has lapsed |
| `iran_renegotiate_anglo_persian` | `iran_agreement_anglo_persian`, after 1925 |
| `iran_renegotiate_abadan_deal` | `iran_abadan_deal_signed`, after 1936 |

Each costs political power, reclaims influence and sovereignty, lowers the patron's standing, clears the obligation flag and idea, and moves the balance to whichever institution carried it.
The Majlis condition is the point: a decision is available under an autocracy, under a Crown-dominant balance, or when the chamber cannot block - not while the chamber is ascendant and opposed.
The two older arrangements are gated by date rather than by a binding flag, because neither was signed through this framework.

## Flags

| Flag | Duration | Meaning |
| --- | --- | --- |
| `iran_negotiation_open` | until the demand resolves | one demand on the table |
| `iran_negotiation_cooldown` | 540 days | no new demand |
| `iran_demand_<id>_done` | permanent | this demand is closed for the campaign |
| `iran_demand_<id>_accepted` / `_compromised` | permanent | the concession is in force |
| `iran_demand_<id>_rejected` | permanent | refused at least once |
| `iran_demand_<id>_supported` | permanent | the rival was played instead |
| `iran_demand_<id>_delayed` | permanent | the single postponement is used |
| `iran_demand_<id>_escalated` | permanent | the escalation has been scheduled |
| `iran_demand_<id>_binding` | 1095 days | the terms cannot be reopened |
| `iran_demand_<id>_renegotiated` | permanent | the concession was bought back |
| `iran_patron_tension_british` / `_northern` / `_german` | 1460 days | that patron's next demand is signed heavier |
| `iran_decree_treaty` | permanent | a treaty was signed without the chamber |
| `iran_obligation_*` | until renegotiated | the named obligation the concession created |
| `iran_railway_company_chartered`, `iran_customs_retained`, `iran_joint_fisheries_company`, `iran_german_advisers_only` | permanent | which compromise was taken |
| `iran_german_economic_pact`, `iran_german_alignment` (existing) | - | the German treaty is in force |

Demand ids: `russian_railway`, `british_gulf`, `soviet_caspian`, `german_pact`.

## Interactions

- **Crown and Majlis** (`PER_crown_and_majlis`): decides whether a demand is answered by the government, by the chamber or by decree, and whether a renegotiation can be carried at all. Every read of `power_balance_value` is guarded by `has_power_balance`.
- **Great Game acts** (`iran_concede_*`, `iran_reclaim_*`): all influence, sovereignty and leverage movement goes through them, so a negotiation moves the same axes as a focus or an agreement. The tier rule lives in the concede effects: a patron already betrayed (`iran_patron_tension_*`) or a demand delayed once is signed one tier heavier.
- **Great Game agreements**: a demand is suppressed if the equivalent agreement is already signed (`iran_agreement_northern_railway`, `iran_agreement_british_loan`, `iran_agreement_german_mission`), so the two systems do not ask for the same thing twice.
- **Budget vote**: `iran_decree_treaty` is the hook a later pass should read; see the note in the change list.
- `iran_refresh_mechanics_hidden` is called from every consequence, so the influence-driven spirits follow the numbers.

## AI

Every option has an `ai_chance`, every decision an `ai_will_do`.
Historical weights favour the answer history took - accept for the railway and the Gulf, compromise for the Caspian fisheries, accept for the German treaty - and the `is_historical_focus_on` modifier doubles those weights.
The Crown side favours the decree, the Majlis side favours submitting, nationalists and republicans favour refusal, and `iran_balancing_powers` favours playing the rival.

## Needed icons

None. The decisions reuse `generic_break_treaty`; the events use `GFX_report_event_russo_persian`, `GFX_report_event_persiancoup`, `GFX_report_event_persia_occupation` and `GFX_report_event_generic_sign_treaty1`, all already used in `events/iran_campaign.txt`.

## Untested

Not played in game. The things most likely to need adjustment: whether `constant:iran_story.negotiation_*_days` is accepted in `days =` fields (the pattern is used elsewhere in this mod for `country_event` delays, not yet for `set_country_flag`), whether the option list reads well at six, and whether the 540-day cooldown starves the 1912-1914 window when both the railway and the Gulf demands are waiting.
