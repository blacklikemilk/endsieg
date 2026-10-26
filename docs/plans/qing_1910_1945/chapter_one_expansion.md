# Chapter one expansion, 1910-1919

## What was wrong

Chapter one was 96 focuses spread across 24 columns and 11 rows: sibling focuses sat two cells apart, distinct branches sat two cells apart as well, so the court block and the Beiyang block read as one mass and long titles nearly touched.
The 1911 crisis existed only as a loyalist preparation chain, and the Japanese question was a single diplomacy focus with no war content, even though the mod's Japan tree can force a Chinese submission from 1915 and the Qing can be at war with Japan earlier.

## What the chapter is now

149 focuses, laid out in separate bands with a four-cell gutter between branches and a two-cell step between siblings.

| Band | x | Content |
| --- | --- | --- |
| Economy | 0-4 | treasury, salt, land tax, currency, railways, industry, grain, banking, national bank |
| Army | 8-14 | New Army, drill, academies, artillery, engineers, supply, telegraph, cavalry, air service, navy, Manchurian garrisons, conscription |
| Beiyang | 16-20 | Yuan's rise, cabinet, military finance, officers, loyalty, army politics |
| Court and constitution | 25-37 | regency, reform edict versus court resistance, assemblies, legal code, four route settlements, censors, banners |
| Diplomacy | 42-48 | treaty ports, Britain, America, Japan, Shandong, concessions, German and French missions, indemnity |
| Provinces | 51-55 | governors, gentry, assemblies, taxation, militia, border marches, four provincial settlements |
| Japan and the war | 42-48, y 6-14 | the invasion, Shandong, railway zone, boycott, appeal to the powers, arms, war of posts, the demands, rejection or acceptance, mobilisation, the long war |
| The 1911 crisis | 33-37, y 12-20 | railway protection, Sichuan, Wuchang, provincial declarations, Yuan's terms, the abdication question, the redoubt, the Second Revolution, the new dynasty, the National Protection War, the restoration, the declaration for the Entente |
| Society | 25-29, y 12-16 | schools, university charter, women's education, press law, students, the New Culture, public health, local self-government, labour |
| Loyalist preparation | 31, y 11-19 | railway guard, Wuchang garrison, provincial loyalty, capital defences, the dynasty is prepared |

## Historical anchors

| Focus | Anchor |
| --- | --- |
| The Railway Protection Movement | Sichuan railway company and the nationalisation decree, summer 1911 |
| Sichuan in Revolt | Chengdu in the hands of the railway company's supporters, September 1911 |
| The Wuchang Mutiny | bomb in the Russian concession and the mutiny of the 8th Division, 10 October 1911 |
| The Provinces Declare | provincial declarations of independence, October-November 1911 |
| Terms for Yuan Shikai | Yuan recalled as premier, 1 November 1911 |
| The Abdication Question | abdication edict of 12 February 1912 |
| The Second Revolution | the 1913 rising against Yuan |
| The New Dynasty | Yuan's monarchy proclaimed December 1915 |
| The National Protection War | Yunnan's declaration, December 1915 |
| The Restoration | Zhang Xun's restoration, 1-12 July 1917 |
| Declare for the Entente | Chinese declaration of war on Germany, 14 August 1917 |
| The Landing at Tsingtao | Japanese landing at Tsingtao, 2 September 1914 |
| The Demands | Twenty-One Demands presented 18 January 1915 |
| The Long War | war resistance and the 1915 boycott |
| An Air Service | Nanyuan air school, 1913 |
| A University Charter | Peking University under Cai Yuanpei, 1917 |
| The New Culture | New Youth and the vernacular movement, 1915-1919 |
| Local Self-Government | county self-government regulations, 1914 |

The demanded articles and the rejection/acceptance pair are the historical 18 January 1915 list: Group I on Shandong, Group II on Manchuria and eastern Inner Mongolia, Group III on the Hanyeping company, Group IV on the coast, Group V on advisers, police and arsenals.

## The Japan branch

- `QW1_japanese_invasion` is a root focus available only while at war with Japan, so a war that begins in 1911 or 1912 has content immediately.
- `QW1_shandong_crisis` is visible from the start and selectable at war or after 15 August 1914; it fires `qing_campaign.60`.
- `QW1_the_demands` additionally requires 18 January 1915, and fires `qing_campaign.51`, which already carried the historical demands.
- Rejection and acceptance are mutually exclusive, and rejection plus mobilisation unlock `QW1_long_war`.
- The branch grants war support, manpower, army experience, opinion modifiers with Japan, the United States and Britain, and sets `qing_prepared_for_japan` for later chapters.

## The 1911 crisis

The political crisis is a chain of its own, rooted in the railway guard of the loyalist preparation branch: railway protection, Sichuan, Wuchang, the declarations, Yuan's terms, then a fork between the abdication question and the imperial redoubt.
`QW1_wuchang_mutiny` fires `qing_campaign.61`, `QW1_abdication_question` fires `qing_campaign.62`, and `QW1_restoration_1917` fires `qing_campaign.63`.
The constitutional option in `.62` calls `qing_settle_constitutional`, so a player who takes it enters the constitutional route with the assembly in session rather than falling into the historical collapse.

## Static checks

- `tools/china_audit.py` over both country packages: 445 focuses, 53 events, 56 decisions, 0 missing focus localisation, 0 unresolved sprites.
- `check_tree_geometry.py`: 149 focuses, 0 errors, 0 warnings.
- Every `constant:qing_story.*` and every opinion modifier referenced by the chapter resolves.
- The audit tool's sprite scan was fixed to accept unquoted `name = GFX_...` entries, which vanilla uses for leader portraits; before that fix the Puyi portrait was reported as missing when it is registered.

## Still unverified

No launch has been made since these changes.
Whether the new bands read well at the default zoom, whether the Japan branch appears and greys out as intended, and whether the four new events fire from their focuses are all engine questions.

## Beiyang command and the constraint layer

The Beiyang band now runs nine focuses deep: the Baoding academy, Yuan's health, the Zhili, Anhui and Fengtian cliques, the military governors, the Beiyang treasury, the Beiyang army and the army-and-state capstone.
Each sets a flag later chapters read (`qing_zhili_clique`, `qing_anhui_clique`, `qing_fengtian_clique`, `qing_military_governors`, `qing_beiyang_state`) and pays in equipment, manpower, opinion or political power rather than experience alone.

Four standing constraints are now spirits rather than text in a description:
`qing_unequal_treaties` (political power, research and stability penalties) is cleared by the legal code or judicial reform;
`qing_provincial_autonomy` (consumer goods, construction and stability penalties) is cleared by land tax reform;
`qing_reformed_finance` is granted by the national bank and `qing_public_schools` by the new schools.
The refresh effect adds and removes them from the flags, so the panel shows what the dynasty has actually fixed.

## Layout corrections

The society branch moved out of the political centre to a vertical chain at x=24 under the legal code, so its links are one row deep instead of eleven.
The regency household no longer sits between the two mutually exclusive court focuses, which was drawing their exclusion arrow straight through its title plate.
The 1911 crisis, the Japanese war, the later economy, the army reform and the provincial additions were pulled up to sit one to three rows under their parents.
Measured result: links longer than three cells fell from 49 to 37, the longest from 15 cells to 9, and the tree still passes the geometry checker with 158 focuses and no box overlaps.
