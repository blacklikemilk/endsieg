# Historical WW1 faction goals

Fifteen finite objectives and three continuous faction manifests replace the generic starter sets for the Central Powers, Entente and Balkan League. Each coalition begins with one short-, medium- and long-term objective. Additional goals appear in the native goal selection list when their conditions permit; no additional goal slots are granted.

The objectives express historical aims, including aims that were never achieved. In particular, the Dardanelles expedition and a favourable Central Powers settlement are objectives rather than claims about historical outcomes. Their descriptions carry the same gold `Historical` note as the other WW1 content.

| Faction | Goal | Category | Completion |
| --- | --- | --- | --- |
| Central Powers | Secure the Bulgarian Alliance | Short | Bulgaria is a faction member |
| Central Powers | The Route to Constantinople | Medium | Austria-Hungary, Bulgaria and the Ottoman Empire belong to the coalition; friendly forces control the eight principal junction states |
| Central Powers | A Separate Peace in the East | Long | Existing Brest-Litovsk treaty flag |
| Central Powers | A Polish Kingdom under Our Protection | Medium | Poland controls Warsaw and is protected as a German or Austro-Hungarian subject |
| Central Powers | Force a Settlement in the West | Long | Existing Central Powers victory settlement |
| Entente | Bring Italy into the Entente | Short | Italy is a faction member |
| Entente | Secure Romanian Cooperation | Short | Romania is a faction member |
| Entente | Recover Alsace-Lorraine | Medium | France is a member and controls Alsace-Lorraine |
| Entente | Open the Dardanelles | Medium | Friendly control of Thrace, Edirne and Constantinople; Ottoman membership cannot satisfy it |
| Entente | Honour the London Promises | Medium | Allied Italy controls South Tyrol, Trentino and Trieste |
| Entente | Restore Belgian Sovereignty | Long | A German defeat or armistice and independent Belgian control of its homeland |
| Entente | Restore Serbia | Long | A Habsburg defeat or general armistice and independent Serbian/Yugoslav administration of the Serbian homeland |
| Balkan League | Unite the Four Balkan Allies | Short | Serbia, Bulgaria, Greece and Montenegro are members |
| Balkan League | End Ottoman Rule in Macedonia | Medium | Friendly control of the Skopje and Salonika regions |
| Balkan League | Conclude the Peace of London | Long | Existing 1913 Treaty of London flag; League members are no longer fighting the Ottomans |

The starter goals are Bulgaria/corridor/eastern peace; Italy/Alsace/Belgium; and the three Balkan League goals. Members still enter factions through the existing negotiated focus/event chains. Goals never recruit members, declare wars, transfer states or impose a treaty. Territorial and political progress comes from the actual map and existing event outcomes.

The three manifests retain the previous mutual-defence formula and maximum +5% war support from secured faction core territory. Their names and descriptions now distinguish the Imperial Alliance, Allied Cause and Balkan Agreement. The existing date-gated collection reduces the scaled effect to zero after 1935.

Finite completion grants 25 faction power projection and one initiative to eligible members; long-term goals grant 50 and two. Native country `has_completed_goal` records prevent repeat rewards after faction recreation. The new objectives add no permanent national modifiers.

## Registration and compatibility

New factions receive their starter set from the current templates. Existing factions using those templates are upgraded in place at startup or the next monthly country pulse. Completed old goals and members are retained. Registration runs once per leader and recognises an already upgraded portfolio, preserving selections after a leadership change. It does not recreate a faction or alter joining rules.

Anglo-German and German-Russian conversions are excluded even when they inherit the old Central Powers template. Their existing reconfiguration helpers remove only unfinished historical goals before installing their alternative programme. The French continental route uses its separate template. Goal completion and cancellation explicitly check WW1 scenario/date and coalition identity; visibility alone is not relied upon to stop late completion.

Native global `on_monthly` already has country scope: the new hook calls the guarded leader helper directly. Only startup uses `every_country`. Progress uses fixed small state sets, with stable nonempty denominators; no daily world or state scan is introduced. Initial goals do not depend on `select_effect`, which native skips for goals assigned at game start.

The implementation is in `common/factions/goals/WWI_historical_goals.txt`, `WWI_historical_manifests.txt`, and the `WWI_faction_goals.txt` files in scripted triggers/effects, collections, script constants and on-actions. English text is UTF-8 with BOM. The data manifest is `tools/ww1_faction_goals.json`.

## Historical basis

- [Wilson's Fourteen Points, primary text](https://avalon.law.yale.edu/20th_century/wilson14.asp), especially points VII, VIII and XI, support the Belgian, French and Serbian restoration aims.
- [1918 US diplomatic report on Italian claims](https://history.state.gov/historicaldocuments/frus1918Supp01v01/d841), paragraphs on the April 1915 Treaty of London, records the territorial promises underlying Italian intervention.
- [Treaty of Brest-Litovsk, primary text](https://avalon.law.yale.edu/20th_century/brest.asp), article I, provides the eastern peace milestone.
- [1913 Treaty of London, primary-text transcription](https://en.wikisource.org/wiki/Treaty_of_London_(1913)), articles I–III, provides the Balkan peace framework. The map objectives cover the Macedonian campaign rather than assigning the contested territory or Albania automatically.
- [Research on the Polish Legions](https://encyclopedia.1914-1918-online.net/pdf/1914-1918-Online-polish_legions-2014-10-08.pdf) discusses the Central Powers' proclaimed Polish kingdom. The game's existing protectorate mechanic is used to represent its political dependence.

The junction-based Constantinople corridor and country/state checks are gameplay representations. They do not model every railway segment or every qualification of a treaty. Existing state definitions were inspected directly: Constantinople is state 797 in this map, not the mostly empty older Istanbul state 341; South Tyrol, Trentino and Trieste use states 39, 850 and 736.

## Validation

Native structure/scope comparisons and reference checks are supplemented by 60 bounded scenarios executing the actual completion and registration guards. Checks include neutral Belgium, subjects, Yugoslav succession, absent allied consent, incomplete railway control, historic treaty milestones, changed coalitions, WWII dates, repeated save registration and reward replay. Ratio completion gates are compared with their corresponding explicit conditions. The evaluator deliberately treats self-faction membership as false to exercise the native `tag = ROOT` alternative.

These checks do not simulate the full game engine. HOI4 was not launched automatically; native UI behaviour, goal scheduling and a live save migration remain for an in-game playtest.
