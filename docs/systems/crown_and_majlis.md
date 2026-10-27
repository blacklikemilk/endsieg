# The Crown and the Majlis

Persia's native balance of power, `PER_crown_and_majlis` in `common/bop/PER.txt`.
Negative values are royal authority, positive values parliamentary power, and the centre is the constitutional settlement.

## Authority against the balance

`iran_authority` is state capacity: taxation, tribes, the reach of the gendarmerie.
The balance is regime form: who decides.
They are kept apart on purpose, and no later pass should merge them.
Authority gates the budget vote; the balance gates what the Majlis can do.

## Lifecycle

The balance is built by `PER_bop_sync` on the daily Iran tick and after every settlement, never during country initialisation.
A start before 1919 opens at +0.15, a later start at -0.15, and a start after the 1941 occupation at +0.30.
Under the Pahlavi settlement the balance is removed and the Pahlavi Autocracy spirit applies; the Majlis sits at the Shah's pleasure.
`PER_bop_resurgence_check` ends that after 16 September 1941 once the country is occupied or has granted the Allies transit: event `iran_campaign.77` fires, the flag `PER_majlis_resurgence` is set and the balance returns at +0.30.
Qajar, constitutional, republican, socialist and nationalist settlements keep the balance; the Pahlavi settlement is the only one that removes it.
The republic keeps the Shah side's art, because no President sprite exists yet.

## Regime shifts

A regime shift out of the autocracy starts with no balance to move, so it builds one before it pushes.
Each shift clears the old regime flags, proclaims its successor flag, creates the balance at the constitutional centre through `PER_bop_open_regime`, applies its settlement push through `PER_bop_settle_*`, and resyncs.
A push applied before the balance existed would move nothing and would leave `PER_bop_sync` to create the era's opening value, which is the position of the autocracy the shift is leaving.
The constitutional shift keeps the Shah and `PER_pahlavi_dynasty`, and its successor flag is what holds `PER_bop_sync` off the autocracy branch, so the balance survives at the centre with the dynasty bound.

## What moves it

- Four standing decisions: Appoint a Royal Cabinet, Convene the Majlis, Negotiate the Settlement and Ratify the Fundamental Laws.
- Foreign agreements: `PER_bop_sign_agreement` pushes the Crown if the Court signed by decree and the Majlis if it ratified.
- The five settlements that keep the balance push it through `PER_bop_settle_*`, and the five later regime shifts open it at the centre first, push it and resync.
- The coup decisions push the Crown (officers, brigade, minister, purge) or the Majlis (the motion against Reza Khan); the motion needs a chamber that can sit, and the monthly coup drift reads the balance.
- 28 political focuses push the balance: the Second Majlis, the 1911 ultimatum and Shuster's dismissal, the 1921 coup, the regency and court ministries, the wartime Majlis and the 1945 constitution among them.
- Every push is guarded, so a focus completed under the Pahlavi settlement does nothing.

## The budget vote

`PER_bop_budget_vote` is a yearly mission.
It is available while authority is at least `iran_story.bop_budget_authority` and the balance is above -0.40.
Holding the vote pays political power and a little stability, and nudges the Majlis forward.
If the 150 days pass, event `iran_campaign.78` opens a constitutional crisis: dissolve the chamber (Crown), yield (Majlis) or negotiate towards the centre.
The AI follows its side: the Crown flag favours dissolution, the Majlis flag favours yielding.

## AI

The historical AI appoints royal cabinets after the 1921 coup and convenes the Majlis on the Majlis path.
Qajar and constitutional-monarchy routes never appoint royal cabinets and favour negotiating the settlement.

## Needed icons

None new.
The Pahlavi Autocracy spirit reuses `PER_reza_shah_pahlavi`.
Qajar and Pahlavi crown variants and a President side icon (`GFX_bop_PER_president_side`) are pending art and were not made.

## Untested

Removing and re-creating the balance on the same day, and the tooltip look, have not been tested in game.
