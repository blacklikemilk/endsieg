# Irish independence and international news

Historical timeline checked against [Documents on Irish Foreign Policy, volume 1](https://www.difp.ie/books/volume-1/) and the [UK Parliament's Anglo-Irish Treaty research briefing](https://researchbriefings.files.parliament.uk/documents/CBP-9260/CBP-9260.pdf).

| Date | Event | ID |
| --- | --- | --- |
| 28 December 1918 | Sinn Féin election result | `INT_ireland.1` |
| 21 January 1919 | First Dáil and War of Independence | `INT_ireland.2` |
| 21 November 1920 | Bloody Sunday | `INT_ireland.3` |
| 11 July 1921 | Truce; Britain can refuse | `INT_ireland.4` |
| 6 December 1921 | Anglo-Irish Treaty; Britain can refuse | existing `INT_uk_interwar.2` |
| 7 January 1922 | Dáil ratification | `INT_ireland.5` |
| 16 January 1922 | Transfer to provisional government | `INT_ireland.6`, setup `.7` |
| 18 March 1922 | Army split; Ireland can fund reconciliation | `INT_ireland.8` |
| 28 June 1922 | Four Courts and civil war | `INT_ireland.9`, setup `.10`, war `.11` |
| 22 August 1922 | Collins's death, following Griffith's death | `INT_ireland.12` |
| 6 December 1922 | Free State constitution | `INT_ireland.13` |
| 24 May 1923 | Republican ceasefire if Dublin is still held by government | `INT_ireland.14` |
| 3 December 1925 | Boundary agreement | `INT_ireland.15` |
| 11 December 1931 | Legislative autonomy | `INT_ireland.16` |
| 9 March 1932 | De Valera's government | `INT_ireland.17` |
| 3 May 1933 | Abolition of the oath | `INT_ireland.18` |

The guerrilla war applies a British political-pressure spirit. The provisional government receives only British-owned states 113, 134 and 135. State 119 remains British; state 932 is excluded. Commonwealth dominion status is represented by a constitutional spirit, allowing Ireland to manage its own affairs and its internal war.

The civil war uses the existing IRE and IRA tags. IRA receives cores and states before its deferred setup; four weaker republican formations oppose four National Army formations. Legacy IRA templates loaded by its country history are removed only for this chain. Technology history is retained. Both victory callbacks defer full annexation by one hour and also finish cleanup if a peace conference already annexed the defeated tag. Victory events `.19` and `.20` run only once.

The AI accepts the historical truce and Treaty and defends ratification. A player can refuse either British agreement or fund Irish reconciliation. Historical leaders' deaths require the civil war to continue; an earlier peace may change that outcome.

Daily scheduling works independently of the British focus-tree selection. Bounded dates and phase flags prevent late replay and duplicate announcements. A later bookmark initializes the current situation silently. British Irish focuses use the same guarded offer effects as the daily scheduler.

All interwar news declarations use `major = yes`. This broadcasts one source report to all countries; do not use an `every_country` loop. The Irish chain reuses `endsieg_news.60`, `.61`, `.62` and their historical pictures. Its eleven other headlines use `INT_ireland_news`. Additional international political reports use `INT_world_news.1`–`.19`, and Russian diplomatic/war reports use `INT_russian_news.1`–`.13`.

## Validation and playtesting

Static validation covers namespace IDs, event/effect/idea/character/asset/localisation references, state and province IDs, news broadcast flags, encoding, braces and ownership dates. It cannot confirm engine timing or AI combat.

Playtest a continuing 1918 campaign through 1923, observing all milestones from an unrelated country. Also test refusal and reconciliation, both civil-war winners, later bookmarks without old news, and that Northern Ireland remains British. The game is not launched automatically.
