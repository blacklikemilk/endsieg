# All 159 interwar news definitions and their scripted timeline

Inventory of the current Endsieg scripts. Dates below are the source trigger windows, not a promise that every headline fires on that date. Country choices, required focuses, flags, wars and the usual short event delays still apply. This is a script inventory, not a claim that every focus window matches the real-world date.

The count includes multiple national headlines about the same incident, alternative-history reports, and one unused British treaty definition. All 159 definitions have `major = yes`; that broadcasts a report to all countries once its source actually calls it. Broadcasting does not create a source trigger.

Historical major-country schedulers generally require their interwar tree, a date before 1936 and no Central Powers victory. Several French and German reports additionally require Compiègne/Versailles and their appropriate political route. Turkey combines focus completion with settlement safeguards; its Lausanne, republic and sultanate steps have dated fallbacks. Irish reports have their own phase, ownership and war checks.

The three Irish-chain reports `endsieg_news.60` (War of Independence), `.61` (Anglo-Irish Treaty) and `.62` (civil-war outbreak) are existing non-INT definitions and are **additional to these 159**. Their source dates are 1919-01-21, 1921-12-06 and 1922-06-28 respectively, subject to chain progress.

## Dated or dated-fallback reports (112)

Dates show the calendar days within the strict `date >` / `date <` bounds. A news report scheduled after a source event or its chosen option can arrive later.

| Trigger window | Event ID | Headline | Source |
| --- | --- | --- | --- |
| 1918-12-28–1919-01-20 | `INT_ireland_news.1` | Sinn Féin Wins the Irish Election | [INT_ireland.1](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:7>) |
| 1919-01-05 | `INT_world_news.3` | Fighting in Berlin | [INT_ger_milestone.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:190>) |
| 1919-04-07 | `INT_world_news.4` | A Council Republic Proclaimed in Bavaria | [INT_ger_milestone.14](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:204>) |
| 1919-05-03 | `INT_world_news.5` | The Munich Council Republic Is Suppressed | [INT_ger_milestone.15](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:218>) |
| 1919-07-16–1919-08-14 | `INT_eastern.11` | Poland Secures Eastern Galicia | [INT_eastern.1](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Eastern Settlement.txt:59>) |
| 1919-09-12–1919-09-30 | `INT_ita_news.1` | Italian Nationalists Occupy Fiume | [INT_ita_interwar.1](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:13>) |
| 1919-11-16–1919-11-30 | `INT_france_news.1` | The Postwar Chamber Meets | [INT_france.6](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:87>) |
| 1919-11-19–1919-12-14 | `INT_usa_news.1` | America Rejects the Versailles Treaty | [INT_usa_interwar.1](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:10>) |
| 1920-03-23 | `INT_ger_news.2` | General Strike Defeats the Kapp Putsch | [INT_weimar.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Weimar Republic.txt:121>) |
| 1920-08-18–1920-09-14 | `INT_world_news.15` | The Nineteenth Amendment | [INT_usa_interwar.2](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:20>) |
| 1920-09-01–1920-09-30 | `INT_ita_news.2` | Factory Occupations Spread in Italy | [INT_ita_interwar.2](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:27>) |
| 1920-11-12–1920-11-30 | `INT_ita_news.10` | An Adriatic Treaty Is Signed | [INT_ita_interwar.4](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:54>) |
| 1920-11-21–1920-12-14 | `INT_ireland_news.2` | Bloody Sunday in Dublin | [INT_ireland.3](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:17>) |
| 1920-12-29–1921-01-14 | `INT_france_news.16` | French Socialists Split at Tours | [INT_france.24](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:342>) |
| 1921-03-04–1921-03-31 | `INT_usa_news.2` | Harding Becomes President | [INT_usa_interwar.3](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:30>) |
| 1921-03-18–1921-05-31 | `INT_eastern.12` | Peace Signed at Riga | [INT_eastern.2](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Eastern Settlement.txt:92>) |
| 1921-07-11–1921-08-31 | `INT_ireland_news.3` | A Truce Ends the Fighting in Ireland | [INT_ireland.4](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:26>) |
| 1921-11-04–1921-11-30 | `INT_japan_news.1` | Japanese Prime Minister Assassinated | [INT_japan_interwar.2](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:20>) |
| 1921-11-09–1921-11-30 | `INT_ita_news.12` | A National Fascist Party Is Founded | [INT_ita_interwar.16](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:227>) |
| 1922-02-06–1922-02-28 | `INT_japan_news.2` | Five Powers Sign Naval Treaty | [INT_japan_interwar.3](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:30>) |
| 1922-02-06–1922-02-28 | `INT_usa_news.3` | Naval Powers Sign the Washington Treaty | [INT_usa_interwar.4](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:40>) |
| 1922-04-16 | `INT_ger_news.13` | Germany and Soviet Russia Sign at Rapallo | [INT_ger_milestone.2](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:31>) |
| 1922-06-24 | `INT_ger_news.3` | Foreign Minister Rathenau Assassinated | [INT_weimar.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Weimar Republic.txt:163>) |
| 1922-08-22–1922-09-14 | `INT_ireland_news.10` | Michael Collins Is Killed | [INT_ireland.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:97>) |
| 1922-10-23–1922-11-14 | `INT_world_news.10` | Bonar Law Forms a Government | [INT_uk_interwar.3](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:30>) |
| 1922-11-01 onward; sultanate focus/fallback | `INT_turkey_news.16` | The Ottoman Sultanate Is Abolished | [INT_TUR_end_sultanate](<C:/Users/adam0/Documents/GitHub/endsieg/common/scripted_effects/INT - Turkey.txt:17>) |
| 1922-12-06–1922-12-31 | `INT_ireland_news.4` | The Irish Free State Comes into Being | [INT_ireland.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:109>) |
| 1923-01-11–1923-01-31 | `INT_france_news.2` | France and Belgium Occupy the Ruhr | [INT_france.7](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:100>) |
| 1923-01-11 | `INT_ger_news.14` | French and Belgian Forces Enter the Ruhr | [INT_ger_milestone.3](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:46>) |
| 1923-05-22–1923-06-14 | `INT_world_news.11` | Baldwin Succeeds Bonar Law | [INT_uk_interwar.4](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:35>) |
| 1923-07-24 onward; Lausanne focus/fallback | `INT_turkey_news.1` | Peace Signed at Lausanne | [ww1_turkey.66](<C:/Users/adam0/Documents/GitHub/endsieg/events/WWI - Ottoman Empire.txt:1650>) |
| 1923-08-03–1923-08-31 | `INT_usa_news.4` | President Harding Dies | [INT_usa_interwar.5](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:50>) |
| 1923-08-12 | `INT_ger_news.15` | Germany's Mark Loses Its Value | [INT_ger_milestone.4](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:60>) |
| 1923-08-31–1923-09-14 | `INT_ita_news.14` | Italy Occupies Corfu | [INT_ita_interwar.19](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:257>) |
| 1923-09-01–1923-09-19 | `INT_world_news.9` | The Great Kanto Earthquake | [INT_japan_interwar.4](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:40>) |
| 1923-10-22–1923-11-19 | `INT_usa_news.12` | American Senate Investigates Naval Oil Leases | [INT_usa_interwar.24](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:240>) |
| 1923-10-29 onward; republic focus/fallback | `INT_turkey_news.2` | Turkey Proclaims a Republic | [INT_TUR_republic](<C:/Users/adam0/Documents/GitHub/endsieg/common/national_focus/INT - Turkey.txt:448>) |
| 1923-11-09 | `INT_world_news.1` | The Munich Putsch Fails | [INT_ger_milestone.5](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:75>) |
| 1924-01-22–1924-02-14 | `INT_uk_news.2` | Labour Forms a Government in Britain | [INT_uk_interwar.5](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:40>) |
| 1924-03-16–1924-03-31 | `INT_ita_news.13` | Fiume Formally Joins Italy | [INT_ita_interwar.18](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:242>) |
| 1924-04-06–1924-04-30 | `INT_ita_news.19` | Fascist National List Wins Italian Election | [INT_ita_interwar.27](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:366>) |
| 1924-05-11–1924-05-31 | `INT_france_news.3` | The Cartel des Gauches Wins in France | [INT_france.8](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:113>) |
| 1924-05-26–1924-06-19 | `INT_world_news.16` | The Immigration Act | [INT_usa_interwar.6](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:60>) |
| 1924-06-10–1924-06-30 | `INT_ita_news.4` | Matteotti's Disappearance Shakes Italy | [INT_ita_interwar.7](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:99>) |
| 1924-11-04–1924-11-30 | `INT_world_news.12` | Baldwin Returns to Downing Street | [INT_uk_interwar.6](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:45>) |
| 1925-01-03–1925-01-31 | `INT_ita_news.5` | Mussolini Consolidates Power | [INT_ita_interwar.8](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:114>) |
| 1925-04-26 | `INT_ger_news.6` | Hindenburg Elected Reich President | [INT_weimar.16](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Weimar Republic.txt:208>) |
| 1925-05-05–1925-05-31 | `INT_japan_news.3` | Japan Expands the Franchise | [INT_japan_interwar.5](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:50>) |
| 1925-10-16–1925-10-31 | `INT_france_news.10` | The Locarno Treaties | [INT_france.15](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:216>) |
| 1925-12-03–1925-12-31 | `INT_ireland_news.6` | The Irish Border Is Confirmed | [INT_ireland.15](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:120>) |
| 1926-05-03–1926-05-11 | `INT_uk_news.3` | A General Strike Begins in Britain | [INT_uk_interwar.7](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:50>) |
| 1926-07-23–1926-08-14 | `INT_france_news.4` | Poincaré Called Back to Power | [INT_france.9](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:126>) |
| 1926-11-27–1926-12-14 | `INT_ita_news.15` | Italy and Albania Sign a Pact | [INT_ita_interwar.20](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:271>) |
| 1926-12-25–1927-01-14 | `INT_japan_news.4` | Japan Enters the Showa Era | [INT_japan_interwar.6](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:60>) |
| 1927-03-14–1927-04-09 | `INT_japan_news.5` | Japanese Banks Face Crisis | [INT_japan_interwar.7](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:70>) |
| 1928-06-04–1928-06-30 | `INT_japan_news.6` | Manchurian Warlord Killed | [INT_japan_interwar.8](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:80>) |
| 1928-06-25–1928-07-14 | `INT_france_news.5` | France Passes a Monetary Law | [INT_france.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:139>) |
| 1929-02-11–1929-02-28 | `INT_ita_news.6` | Italy and the Holy See Reach an Accord | [INT_ita_interwar.9](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:129>) |
| 1929-03-04–1929-03-31 | `INT_world_news.17` | Hoover Takes Office | [INT_usa_interwar.7](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:70>) |
| 1929-06-05–1929-06-30 | `INT_world_news.13` | MacDonald Returns to Office | [INT_uk_interwar.8](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:55>) |
| 1929-06-07–1929-06-30 | `INT_france_news.15` | Reparations Experts Submit the Young Plan | [INT_france.21](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:299>) |
| 1929-10-24–1929-12-31 | `INT_ger_news.9` | The Economic Crisis Reaches Germany | [INT_depression.1](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Great Depression.txt:19>) |
| 1929-10-29–1929-11-14 | `INT_usa_news.5` | Shares Collapse on Wall Street | [INT_usa_interwar.8](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:80>) |
| 1930-01-14–1930-01-31 | `INT_france_news.11` | France Votes Funds for the Maginot Line | [INT_france.16](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:230>) |
| 1930-06-17–1930-07-14 | `INT_world_news.18` | Smoot-Hawley Becomes Law | [INT_usa_interwar.9](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:90>) |
| 1930-10-01–1930-10-31 | `INT_japan_news.7` | Japan Ratifies London Naval Treaty | [INT_japan_interwar.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:100>) |
| 1930-11-14–1930-11-30 | `INT_japan_news.8` | Japanese Prime Minister Wounded | [INT_japan_interwar.11](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:110>) |
| 1931-01-02–1931-07-31 | `INT_ita_news.11` | Italy Faces the World Slump | [INT_ita_interwar.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:143>) |
| 1931-06-01–1931-06-30 | `INT_france_news.6` | The Depression Reaches France | [INT_france.11](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:161>) |
| 1931-08-24–1931-09-14 | `INT_uk_news.4` | Britain Forms a National Government | [INT_uk_interwar.9](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:60>) |
| 1931-09-18–1931-10-09 | `INT_japan_news.9` | Japanese Forces Advance in Manchuria | [INT_japan_interwar.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:120>) |
| 1931-09-21–1931-10-14 | `INT_uk_news.5` | Britain Suspends Gold Convertibility | [INT_uk_interwar.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:65>) |
| 1931-12-11–1932-01-14 | `INT_ireland_news.7` | Ireland Gains Legislative Autonomy | [INT_ireland.16](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:128>) |
| 1931-12-11–1932-01-14 | `INT_uk_news.6` | Dominions Gain Legislative Independence | [INT_uk_interwar.11](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:70>) |
| 1931-12-13–1932-01-14 | `INT_japan_news.10` | Japan Leaves the Gold Standard | [INT_japan_interwar.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:130>) |
| 1932-01-22–1932-02-19 | `INT_world_news.19` | The Reconstruction Finance Corporation | [INT_usa_interwar.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:100>) |
| 1932-03-01–1932-03-31 | `INT_japan_news.11` | Manchukuo Is Proclaimed | [INT_japan_interwar.14](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:140>) |
| 1932-03-09–1932-03-31 | `INT_ireland_news.11` | De Valera Forms an Irish Government | [INT_ireland.17](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:141>) |
| 1932-05-08–1932-05-31 | `INT_france_news.12` | The French Left Wins Again | [INT_france.17](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:243>) |
| 1932-05-15–1932-05-31 | `INT_japan_news.12` | Japan's Prime Minister Assassinated | [INT_japan_interwar.15](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:150>) |
| 1932-07-09–1932-07-31 | `INT_france_news.17` | Lausanne Revises German Reparations | [INT_france.26](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:370>) |
| 1932-07-09 | `INT_ger_news.16` | Lausanne Ends the Reparations Schedule | [INT_ger_milestone.9](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:131>) |
| 1932-07-20 | `INT_ger_news.11` | Presidential Decree Topples the Prussian Government | [INT_weimar.18](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Weimar Republic.txt:237>) |
| 1933-01-23–1933-02-28 | `INT_ita_news.7` | Italy Creates an Industrial Rescue Agency | [INT_ita_interwar.11](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:158>) |
| 1933-02-28 | `INT_world_news.2` | The Reichstag Fire Decree | [INT_ger_milestone.10](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:145>) |
| 1933-03-04–1933-03-31 | `INT_usa_news.6` | Roosevelt Takes Office | [INT_usa_interwar.11](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:110>) |
| 1933-03-06–1933-03-08 | `INT_usa_news.7` | The United States Closes Its Banks | [INT_usa_interwar.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:120>) |
| 1933-03-09–1933-03-19 | `INT_usa_news.8` | American Banks Begin to Reopen | [INT_usa_interwar.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:130>) |
| 1933-03-24 | `INT_ger_news.17` | German Cabinet Gains Legislative Powers | [INT_ger_milestone.11](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:160>) |
| 1933-03-27–1933-04-14 | `INT_japan_news.13` | Japan Withdraws from the League | [INT_japan_interwar.16](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:160>) |
| 1933-05-03–1933-05-31 | `INT_ireland_news.8` | Ireland Abolishes the Treaty Oath | [INT_ireland.18](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Ireland.txt:147>) |
| 1933-06-16–1933-07-14 | `INT_usa_news.9` | The United States Launches Industrial Recovery | [INT_usa_interwar.16](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:160>) |
| 1933-10-14 | `INT_world_news.6` | Germany Leaves the League of Nations | [INT_ger_milestone.17](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:247>) |
| 1934-01-09–1934-01-31 | `INT_france_news.7` | Scandal Shakes the French Republic | [INT_france.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:174>) |
| 1934-02-06–1934-02-19 | `INT_france_news.8` | Riots Outside the French Chamber | [INT_france.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:187>) |
| 1934-03-17–1934-03-31 | `INT_ita_news.16` | Rome Protocols Signed | [INT_ita_interwar.24](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:324>) |
| 1934-07-25–1934-08-09 | `INT_ita_news.18` | A Failed Coup in Austria | [INT_ita_interwar.26](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:352>) |
| 1934-08-02 | `INT_ger_news.18` | President Hindenburg Dies | [INT_ger_milestone.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:176>) |
| 1934-12-29–1935-01-19 | `INT_japan_news.14` | Japan Denounces Washington Naval Treaty | [INT_japan_interwar.17](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Japan.txt:170>) |
| 1935-01-07–1935-01-31 | `INT_ita_news.17` | France and Italy Reach an Accord | [INT_ita_interwar.25](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:338>) |
| 1935-03-15–1935-03-31 | `INT_france_news.18` | France Lengthens Military Service | [INT_france.28](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:398>) |
| 1935-04-14–1935-04-30 | `INT_france_news.13` | Powers Confer at Stresa | [INT_france.19](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:269>) |
| 1935-04-14–1935-04-30 | `INT_ita_news.8` | The Powers Meet at Stresa | [INT_ita_interwar.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:172>) |
| 1935-05-02–1935-05-31 | `INT_france_news.14` | France and the Soviet Union Sign a Pact | [INT_france.20](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:282>) |
| 1935-06-07–1935-06-30 | `INT_world_news.14` | Baldwin Again Becomes Prime Minister | [INT_uk_interwar.12](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:75>) |
| 1935-06-18 | `INT_world_news.7` | Anglo-German Naval Agreement | [INT_ger_milestone.18](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:261>) |
| 1935-07-14–1935-07-31 | `INT_france_news.9` | France's Left Unites | [INT_france.14](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - France.txt:200>) |
| 1935-08-14–1935-08-31 | `INT_usa_news.10` | America Establishes Social Security | [INT_usa_interwar.20](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:200>) |
| 1935-08-31–1935-09-19 | `INT_usa_news.11` | The United States Passes a Neutrality Act | [INT_usa_interwar.21](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United States.txt:210>) |
| 1935-09-15 | `INT_world_news.8` | The Nuremberg Laws | [INT_ger_milestone.19](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - German Milestones.txt:275>) |
| 1935-10-03–1935-11-30 | `INT_ita_news.9` | Italy Invades Ethiopia | [INT_ita_interwar.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - Italy.txt:186>) |
| 1935-10-03–1935-10-31 | `INT_uk_news.7` | Britain Debates Sanctions on Italy | [INT_uk_interwar.13](<C:/Users/adam0/Documents/GitHub/endsieg/events/INT - United Kingdom.txt:80>) |

## Focus-driven reports (44)

These dates unlock focuses or bound the announcement; the report follows focus completion. They are not automatically scheduled on the opening date. White Russia and a surviving Ottoman parliamentary path are alternative-history outcomes.

| Timing | Event ID | Headline | Required focus |
| --- | --- | --- | --- |
| From 1918-01-02 | `INT_russian_news.3` | Soviet Russia Intervenes in Finland | `SO2_intervene_finland` |
| From 1918-01-02 | `INT_russian_news.6` | Soviet Russia Intervenes in Mongolia | `SO2_invade_mongolia` |
| From 1918-01-02 | `INT_russian_news.7` | The New Economic Policy Is Introduced | `SO2_new_economic_policy` |
| From 1919-01-02; before 1921-01-01 | `INT_ger_news.1` | Germany Adopts a Republican Constitution | `INT_GER_hold_national_assembly_1919` |
| From 1919-01-02 | `INT_russian_news.1` | The Communist International Is Founded | `SO2_found_comintern` |
| From 1919-01-02 | `INT_russian_news.2` | Soviet Russia Declares War on Romania | `SO2_intervene_in_hungary` |
| From 1919-01-02 | `INT_russian_news.8` | Soviet Russia Intervenes in Persia | `SO2_intervene_PSSR` |
| From 1919-04-02; White victory branch | `INT_russian_news.10` | White Russia Declares War on Ukraine | `WHR_war_ukraine` |
| From 1919-04-02; White victory branch | `INT_russian_news.11` | White Russia Declares War in Finland | `WHR_war_finland` |
| From 1919-04-02; White victory branch | `INT_russian_news.12` | White Russia Moves Against the Baltic States | `WHR_war_baltic` |
| From 1919-04-02; White victory branch | `INT_russian_news.13` | White Russia Moves into Transcaucasia | `WHR_war_caucus` |
| From 1919-04-02; White victory branch | `INT_russian_news.9` | White Russia Declares War on Poland | `WHR_war_poland` |
| From 1919-05-15; before 1920-01-01 | `INT_turkey_news.10` | Greek Troops Land at Izmir | `INT_TUR_occupation_of_izmir` |
| From 1919-05-19; before 1920-01-01 | `INT_turkey_news.11` | A National Movement Gathers in Anatolia | `INT_TUR_samsun` |
| From 1920-01-02 | `INT_russian_news.4` | The Far Eastern Republic Is Reintegrated | `SO2_reintegrate_FAR` |
| From 1920-01-02 | `INT_turkey_news.9` | Ottoman Parliament Reconvenes | `INT_TUR_ottoman_parliament` |
| From 1920-04-23; before 1921-01-01 | `INT_turkey_news.12` | A New Assembly Opens in Ankara | `INT_TUR_grand_national_assembly` |
| From 1920-08-10; before 1921-01-01 | `INT_turkey_news.13` | Ankara Rejects the Treaty of Sèvres | `INT_TUR_reject_sevres` |
| From 1921-09-13; before 1922-01-01 | `INT_turkey_news.14` | Turkish Forces Hold at Sakarya | `INT_TUR_sakarya` |
| From 1922-09-09; before 1923-01-01 | `INT_turkey_news.15` | Turkish Forces Enter Izmir | `INT_TUR_liberate_izmir` |
| From 1922-10-28 | `INT_ita_news.3` | Mussolini Forms an Italian Government | `INT_ITA_march_on_rome` |
| From 1923-09-26; before 1924-07-01 | `INT_ger_news.4` | Germany Ends Passive Resistance in the Ruhr | `INT_GER_end_ruhr_resistance` |
| From 1923-11-02; before 1925-01-01 | `INT_ger_news.5` | Germany Moves to Stabilize the Mark | `INT_GER_stabilize_currency` |
| From 1924-01-02 | `INT_whr_news.1` | An Elected Government in Russia | `WHR_INT_constituent_elections` |
| From 1924-03-03; before 1925-01-01 | `INT_turkey_news.17` | Ankara Abolishes the Caliphate | `INT_TUR_abolish_caliphate` |
| From 1924-04-20; before 1925-04-21 | `INT_turkey_news.3` | A New Constitution in Ankara | `INT_TUR_1924_constitution` |
| From 1925-01-02 | `INT_russian_news.5` | The Soviet-Japanese Convention Is Signed | `SO2_SO2_JAP_convention` |
| From 1925-02-13; before 1926-01-01 | `INT_turkey_news.22` | Rebellion Breaks Out in Eastern Turkey | `INT_TUR_sheikh_said_rebellion` |
| From 1925-10-02; before 1927-01-01 | `INT_ger_news.7` | European Powers Agree at Locarno | `INT_GER_locarno_treaties` |
| From 1926-06-05; before 1927-01-01 | `INT_turkey_news.20` | Turkey and Iraq Settle the Mosul Question | `INT_TUR_mosul_settlement` |
| From 1926-09-08; before 1928-01-01 | `INT_ger_news.8` | Germany Enters the League of Nations | `INT_GER_join_league_of_nations` |
| From 1928-11-01; before 1929-01-01 | `INT_turkey_news.18` | Turkey Adopts a New Alphabet | `INT_TUR_alphabet_reform` |
| From 1929-06-02; before 1932-07-01 | `INT_ger_news.10` | Young Plan Reshapes German Reparations | `INT_GER_young_plan_focus` |
| From 1930-08-12; before 1931-01-01 | `INT_turkey_news.19` | A New Opposition Party Forms in Turkey | `INT_TUR_free_republican_party` |
| From 1930-10-30; before 1932-01-01 | `INT_turkey_news.4` | Turkey and Greece Seek Reconciliation | `INT_TUR_greek_rapprochement` |
| From 1932-07-18; before 1934-01-01 | `INT_turkey_news.5` | Turkey Joins the League of Nations | `INT_TUR_league_of_nations` |
| From 1933-01-30 | `INT_ger_news.12` | Hitler Appointed Reich Chancellor | `INT_GER_appoint_hitler` |
| From 1933-04-17; before 1935-01-01 | `INT_turkey_news.8` | Turkey Announces an Industrial Plan | `INT_TUR_first_industrial_plan` |
| From 1934-01-02 | `INT_whr_news.4` | Russia Reports Economic Recovery | `WHR_INT_recovery_1935` |
| From 1934-02-09; before 1935-01-01 | `INT_turkey_news.6` | Balkan Entente Signed | `INT_TUR_balkan_entente` |
| From 1934-06-21; before 1935-01-01 | `INT_turkey_news.21` | Turkey Adopts a Surname Law | `INT_TUR_surname_law` |
| From 1934-12-05; before 1935-12-05 | `INT_turkey_news.7` | Turkish Women Gain Parliamentary Suffrage | `INT_TUR_womens_suffrage` |
| From 1935-01-02 | `INT_whr_news.2` | Russia's Monarchy Consolidated | `WHR_INT_monarchy_1935` |
| From 1935-01-02 | `INT_whr_news.3` | Kolchak's Directorate Endures | `WHR_INT_kolchak_1935` |

## Outcome-driven reports and unused definition (3)

| Condition | Event ID | Headline |
| --- | --- | --- |
| Government victory; ceasefire fallback from 1923-05-24 | `INT_ireland_news.5` | The Irish Civil War Ends |
| Republican victory in the civil war | `INT_ireland_news.9` | The Irish Republicans Defeat the Free State |
| Unused definition; no active caller | `INT_uk_news.1` | Britain and Ireland Sign a Treaty |

The unused `INT_uk_news.1` is replaced in the active Irish chain by `endsieg_news.61`; it is retained to preserve the existing ID.

## Count by namespace

| Namespace | Definitions |
| --- | --- |
| `INT_world_news` | 19 |
| `INT_eastern` | 2 |
| `INT_france_news` | 18 |
| `INT_ger_news` | 18 |
| `INT_ireland_news` | 11 |
| `INT_ita_news` | 19 |
| `INT_japan_news` | 14 |
| `INT_russian_news` | 13 |
| `INT_turkey_news` | 22 |
| `INT_uk_news` | 7 |
| `INT_usa_news` | 12 |
| `INT_whr_news` | 4 |
| **Total** | **159** |

Checked against the local mod files without launching HOI4. No gameplay scripts were changed for this inventory.
