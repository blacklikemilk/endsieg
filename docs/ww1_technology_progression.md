# WWI technology progression

Early land equipment and industry now start below the installed vanilla game's
1936 baseline. Existing WWI and interwar research closes the gap. Research and
equipment production determine progress; reaching a calendar year does not grant
technologies or replace equipment in divisions.

## Land equipment

| Equipment | Defence | Breakthrough | Soft attack | IC cost |
| --- | ---: | ---: | ---: | ---: |
| 1910 infantry weapons | 9 | 0.25 | 0.8 | 0.20 |
| 1918 infantry weapons | 17 | 1.3 | 2.4 | 0.35 |
| 1923 infantry weapons | 18 | 1.7 | 2.7 | 0.38 |
| Basic infantry weapons | 20 | 2 | 3 | 0.43 |
| 1936 infantry weapons | 22 | 3 | 6 | 0.50 |
| Early field artillery | 3 | 2 | 6 | 2.00 |
| 1918 field artillery | 9 | 8 | 20 | 3.25 |
| 1934 field artillery | 11 | 10 | 26 | 3.50 |

Early infantry models now improve consistently, including the previously weaker
1923 model. Field artillery also gains reliability as its models develop. Early
anti-air and anti-tank weapons have weaker combat profiles; their 1936 models
match vanilla's equipment statistics and costs.

The equipment validator compares complete resolved profiles with the installed
game, including speed, reliability, piercing and resources. Later custom equipment
models retain their previous profiles. Support artillery, support anti-tank and
cavalry use vanilla's corresponding combat factors.

The existing interwar offset system remains responsible for retiring accumulated
WWI technology bonuses. It now also covers reconnaissance, maintenance, military
police, marines, engineers and anti-air at their corresponding modern endpoints.
Each correction accounts for technologies actually owned, including incomplete
scenario histories and research obtained out of order. The standard 1936 support
unlocks no longer add extra bonuses absent from their vanilla equivalents.
Custom units, national spirits and later custom research still produce their own
differences between armies.

## Industry

These are baseline adjustments before researched technologies, laws, national
spirits and other country modifiers:

| Statistic | Unmodernized early baseline |
| --- | ---: |
| Military factory output | -20% |
| Dockyard output | -15% |
| Construction speed | -25% |
| Production efficiency cap | -15 percentage points |
| Resource extraction | -20% |

Machine tools, wartime industrial organization, postwar reorganization and
construction research restore these losses in stages. The mature 1934 technologies
produce the same net modifiers as their corresponding vanilla 1936 technologies.
The formerly negative demobilization technologies now represent improvements in
industrial methods. Their descriptions have been updated accordingly.

A single variable-backed dynamic modifier supplies the early baseline and removes
only recovery bonuses from technologies actually owned once a branch matures.
It has no icon, following vanilla's documented dynamic modifier format, so this
system does not add visible national spirit icons. Starting directly in a modern
scenario reconciles its existing research without granting additional research.

Relevant research callbacks maintain the calculations. Startup initializes new
campaigns; a guarded monthly initialization covers existing saves and newly
created countries. Normal monthly ticks do not repeatedly calculate every
country's progression after initialization.

## Validation

Run the repository checks with the current vanilla installation:

```powershell
python tools/validate_1910_equipment_progression.py --vanilla 'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV'
python tools/validate_1910_industry_progression.py --vanilla 'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV'
python tools/validate_interwar_support_offsets.py
```

Additional industry and support validators check researched-source subsets,
research order, repeated reconciliation, source removal and native endpoint
definitions. Static checks cannot verify live campaign balance. Test a fresh 1910
campaign, a direct 1936 start and an existing save; existing saves initialize the
new corrections on their next monthly tick.
