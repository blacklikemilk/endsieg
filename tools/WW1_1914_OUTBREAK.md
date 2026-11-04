# 1914 outbreak and French mobilization

Updated 3 November 2026. Applies to campaigns begun before the July Crisis, including the January 1914 bookmark.

## Problems traced from the live log

The 1910 campaign log records Austria-Hungary declaring war on Serbia on 28 July, Germany declaring on France, Belgium, Luxembourg and Russia together on 5 August, then repeating those declarations on 8 August. Austria-Hungary did not enter the Russian war until September. The German plan-choice event was barred until 4 August, followed by an MTTH and another focus callback. The direct focus reward and the daily completed-focus dispatcher could both queue the same Schlieffen popup; its option did not recheck whether another popup had already executed.

French mobilization required an existing continental war and a date after 3 August. It added 37 formations after the front had opened. Russia's corresponding event referenced nonexistent `RUS_Mobilization.txt` instead of the existing `RIE_mobilization.txt`.

The German blank-cheque focus was missing from crisis synchronization. Replaying completed war-plan focus rewards could also reopen their declaration events. Separately, France's WWII Benelux strategy was active in 1914 and discouraged defending Belgian, Dutch and Luxembourg borders.

## Accepted historical sequence

The existing German daily hook now executes a bounded calendar only after the accepted ultimatum, rejection, Austrian-Serbian war and Central Powers commitments. Alternative alliances, neutrality, mediation, nonaggression pacts and war-ending flags continue to block the historical route. AI chooses its historical plan without waiting for a popup; a German player retains the existing plan choices, presented from 28 July.

| Date | Scripted action |
| --- | --- |
| 30 July | Russian mobilization |
| 1 August | German and French mobilization; Germany declares on Russia |
| 2 August | Germany enters Luxembourg |
| 3 August | Germany declares on France |
| 4 August | Germany declares on Belgium; the British cabinet event decides whether Britain declares war on Germany |
| 6 August | Serbia declares on Germany and Austria-Hungary declares on Russia |

The declaration dates follow the [Library of Congress timeline](https://www.loc.gov/collections/world-war-i-rotogravures/articles-and-essays/timeline/1914/). The provisional AI diplomatic hold prevents ordinary faction calls from racing the scripted sequence; it is hidden, only assigned to AI countries, removed at the relevant entry dates and expires after twelve days as a fallback. Explicit player actions remain available.

The Schlieffen action, plan choices and mobilization effects recheck their authority when executed. Duplicate or stale popups cannot repeat declarations or grants. Accepted plan markers are restored without replaying their declaration callbacks, and the actual blank-cheque focus receives its normal one-time reward. Existing focus IDs, layouts, event IDs and localization aliases remain intact.

## French army correction

The 1910 French OOB contains 47 formations at 70% equipment; its original mobilization wave adds 37. Germany has 55 starting formations at full equipment plus 79 mobilization formations. These counts are scripted formations, before combat losses, training and recruitment; templates differ in size.

- Added 28 French reserve infantry divisions, each with nine infantry battalions and support artillery, full manpower, 95% equipment and 0.2 starting experience. Seven deploy in each of Lille, Reims, Verdun and Nancy, only while France owns the state and controls the spawn city. Each sector has an independent one-time receipt.
- Retained the original 37 French mobilization formations and their templates, equipment and manpower. Their deployment is spread among Amiens, Reims, Troyes, Calais and Nancy. If a staging area has already fallen, the same one-time wave can instead assemble safely at controlled Paris.
- Issued 40,000 rifles and 1,000 existing-model artillery pieces once. Rifles use the 1914 model if researched, otherwise the known 1910 model. This covers the initial equipment shortfall and supplies a replacement reserve; no later weapon model is granted.
- Added AI covering-force buffers before war and a stronger German-front unit request with careful execution and European priority during war. The request is an AI weighting, not a guaranteed number of divisions on every province.
- Restricted the WWII Benelux avoidance strategy to WWII starts and made an already-active early-start instance abort.

The scripted 1910 force can therefore reach 112 formations, including 99 in Europe, before losses and additional recruitment; January 1914 can reach 108, including 92 in Europe. No German starting or mobilization OOB was reduced, and no permanent French combat modifier was added. The historical French mobilisation context is described by the [Musée de l'Armée](https://www.musee-armee.fr/fileadmin/user_upload/Documents/Support-Visite-Fiches-Objets/Fiches-1914-1918/MA_fiche-objet-mobilisation.pdf); the added reserve templates are a game-balance correction rather than a claim of a reconstructed historical OOB.

## Validation and use

- 111 bounded source/scenario checks passed; all 19 edited/new script files parse. Checks cover dated declarations, incomplete old focus markers, duplicate popups, alternate and player routes, mobilization eligibility, safe late-save deployment, one-time equipment grants and the WWII AI boundary.
- 57 additional focus-helper checks passed, including prerequisite closure, preserved rewards and avoiding repeated diplomatic callbacks. Independent review found no remaining confirmed defect in the audited sources.
- All eight OOB references resolve. All five inventoried starting/German OOB files retain their original hashes. The original French 37-formation wave changes only locations.
- Installed native examples were checked for focus completion/unlocking, hidden AI diplomacy modifiers, front controls, reinforcement requests and covering-force buffers.

HOI4 was not launched. These checks do not simulate combat, automatic faction calls, actual supply throughput or live AI positioning. Playtest a historical 1910 or January 1914 campaign from before the crisis through early August and inspect both fronts, army equipment and focus markers. Loading a save before 28 July is best for verifying the full sequence. A continuing 1914 save can catch up eligible missing stages and French reserves; wars, casualties and defeats that have already happened are not undone. Later 1916/1918 and WWII armies do not receive these mobilization grants.
