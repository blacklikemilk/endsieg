# Ottoman political settlement

The WW1 Ottoman political branch now offers a negotiated return of Abdülhamid II and an expanded Committee of Union and Progress (İttihad ve Terakki) route. Existing focus IDs are retained. Thirteen focuses are added to the Ottoman tree; unrelated military, industrial and foreign-policy branches retain their mechanics.

## Restoration and imperial renewal

`TUR_anti_young_turk` opens the palace route. The former sultan's household, petitions and approaches to sympathetic officers precede `OT1_P_revisit_deposition`. Mehmed V agrees to a conditional, voluntary withdrawal. This is an alternate-history agreement, not a claim that such a restoration was historically arranged.

Three timed decisions obtain the required assurances:

| Programme | Initial political power | Duration | Reply |
| --- | ---: | ---: | --- |
| Seek the Officers' Assurances | 45 | 60 days | Professional guarantees or a less binding declaration |
| Consult the Ulema | 35 | 45 days | Public legal undertakings or wider sovereign discretion |
| Receive the Provincial Delegation | 50 | 60 days | Recorded consultation rights or stronger central authority |

Only one political programme can run at a time. A consultation keeps that slot until the reply is answered. Reply options have their own costs and tradeoffs. Pending replies are validated again when clicked, so expired campaigns and repeated answers cannot pay rewards.

`OT1_P_return_to_yildiz` requires a living, registered Abdülhamid, the household's recall, dynastic consent, all three assurances, stability above 34%, officer loyalty of at least 45, a controlled capital and no capitulation. It promotes the existing character rather than creating another identity. A failed last-minute invitation can be renewed through a 14-day decision once the requirements are met.

The returned sovereign chooses between reserved royal powers and an oath before the Chamber. Both converge on a Yıldız council and parallel programmes of provincial inspection, technical education and railways, and cautious diplomacy. Their completion unlocks a modest permanent administrative spirit and a research slot if the country has fewer than five slots; otherwise it grants industrial research assistance. Scholarships are a further 180-day programme.

The ambition is to restore imperial authority through a government able to pay for and execute its decisions. Returning the sovereign does not instantly settle provincial grievances. A delayed confrontation with the officer corps tests promises made during the restoration. Central authority, officer loyalty, provincial confidence and the existing Sick Man of Europe system remain relevant.

The personal restoration closes on 10 February 1918. If the invitation was never completed, the institutional palace branch can continue under the reigning dynasty. If Abdülhamid rules when he dies, succession returns to Mehmed V, or Mehmed VI after Mehmed V's historical death date. A former sovereign's death does not displace another current ruler. Identity and succession handling remain active after the WW1 focus tree is left; changing trees does not itself kill or depose a living ruler.

## The Ittihadists

The Unionist route develops political clubs and officer cadres before the January 1913 seizure of the Sublime Porte. Existing later-start coup resolution bypasses the preparation where appropriate. A secretariat, inspectorates, schools and national credit give the Committee a state-building programme.

Civilian direction relies on Talat's political organisation while retaining the reigning sultan as formal head of state. The alternative officer directorate installs Enver as the actual country leader and becomes available from January 1914 while he is eligible. The choice is mutually exclusive. The civilian branch develops provincial organisation; the officer branch integrates the War Ministry. Both converge on a common Ittihadist programme and the Unionist State.

The routes have different political and military costs. Civilian authority must negotiate with officers; military priority can reduce civilian confidence and strain food distribution. Centralisation gives real production and administrative benefits while aggravating provincial concerns. A 180-day procurement decision supports industrial methods and army experience. No focus in this addition independently joins a faction, declares a war or grants lost territory.

Historical AI follows the civilian CUP programme. Nonhistorical AI can select the palace route or the Ittihadist alternative, including a civilian/officer preference. AI avoids beginning the personal restoration too close to Abdülhamid's death; human players retain the opportunity while he lives.

## Files and validation

The focus tree is `common/national_focus/WWI - Turkey.txt`. New supporting files use the `WWI_Ottoman_politics` stem in decisions, scripted effects, scripted triggers, ideas, country-leader traits, on-actions and events. New localisation is `localisation/replace/english/endsieg_ottoman_politics_l_english.yml`, encoded as UTF-8 with BOM. The event namespace is `ww1_ottoman_politics`; flags and other additions use `OT1_P_`.

Static review covers parsing, original focus ID preservation, prerequisite references, localisation, sprites, modifiers, character registration, AI gates and unchanged unrelated scripted effects. Thirty-one bounded probes execute the new guards and relevant transactions, including succession, repeated replies, lost-capital cleanup and delayed legacy events. The probe runner stubs unrelated administration helpers and native engine operations; it is not a full HOI4 simulation. These checks do not replace an in-game playtest. HOI4 was not launched automatically.

## Historical basis and art provenance

- [TDV İslâm Ansiklopedisi: Abdülhamid II](https://islamansiklopedisi.org.tr/abdulhamid-ii): deposition, confinement, transfer to Beylerbeyi and death. The restoration and the negotiated withdrawal of Mehmed V are fictional divergences.
- [Turkish National Palaces: Beylerbeyi Palace](https://www.millisaraylar.gov.tr/Lokasyon/4/Beylerbeyi-Sarayi?culture=en): Abdülhamid's last residence.
- [M. Şükrü Hanioğlu: İttihat ve Terakki Cemiyeti](https://islamansiklopedisi.org.tr/ittihat-ve-terakki-cemiyeti): organisation and the consolidation of CUP authority.
- [The Committee's 1913 political programme](https://tr.wikisource.org/wiki/%C4%B0ttihat_ve_Terakki_Cemiyeti_siyasi_program%C4%B1_(1913)): administrative inspection, education and economic policy.
- [1914–1918 Online: Governments, Parliaments and Parties, Ottoman Empire/Middle East](https://encyclopedia.1914-1918-online.net/pdf/1914-1918-Online-governments_parliaments_and_parties_ottoman_empiremiddle_east-2019-10-17.pdf): wartime institutions and political responsibility.

The new character portrait, `gfx/leaders/TUR/Portrait_Turkey_Abdulhamid_II.dds`, is converted at its original 156×210 dimensions from the locally installed **The Great War Redux**, workshop item **3365515312**, version **0.15.20**, `gfx/leaders/TUR/TUR_abdulhamid_ii.png`. The original source SHA-256 is `457a26ad188dd3be66b1fbb2e2c02065b1bde8108ab61aec9a2f139e7eb36c29`. The individual artist is not identified in the inspected local credits or embedded image metadata. Attribution is retained here. Existing native/DLC focus and idea sprites are referenced by their game sprite names; no generated icon collection is installed by this change. Events reuse existing historical Ottoman scenes and avoid depicting another sultan as Abdülhamid.
