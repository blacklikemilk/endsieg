# Super Events audio provenance

This sheet records the nine one-shot cues used by the Endsieg super events and the basis for using each recording.

All nine come from the Library of Congress National Jukebox mirror held by the Hessel Digital Library on Internet Archive (`archive.org`), which is the approved source for this task. Every item carries the Internet Archive licence field `https://creativecommons.org/publicdomain/mark/1.0/` and a Library of Congress rights statement naming the Music Modernization Act basis (`17 U.S.C. sec. 1401`), because each recording was first published between 1907 and 1923.

Under the Music Modernization Act, pre-1972 US sound recordings enter the public domain 100 years after first publication, so as of 1 January 2026 every recording published in 1930 or earlier is public domain in the United States. Each chosen item is comfortably inside that line, and the Library of Congress states the public-domain status explicitly on the item record, so no judgement call was needed beyond confirming the published date.

That 1930 line settles one research question before it starts: no recording first published in the 1930s, Chinese or Japanese, can be shown public domain today, so no contemporaneous 1937 Sino-Japanese War record was usable. Cues for twentieth-century moments are therefore built from the earliest documented recording of the music that belongs to the moment, and the recording date is stated openly in every entry below rather than stretched to the event year.

Final files live in `sound/endsieg_super_events/` and are Ogg Vorbis, 44.1 kHz, stereo, 45–120 seconds, each with a 2 second fade in and a 3 second fade out. No script, localisation, `.gfx` or `.asset` file was touched.

## Summary

| Final file | Moment | Source recording | Published | Duration |
| --- | --- | --- | --- | --- |
| `compiegne.ogg` | Compiègne armistice 1918 | "Ich hatt' einen Kameraden" (Victor) | 1924-05-02 | 107.5 s |
| `central_powers_victory.ogg` | Central Powers victory | "Treue zu Kaiser und Reich" (Victor) | 1914-03-20 | 100.0 s |
| `fall_of_france.ogg` | Fall of France 1940 | "Chopin's funeral march" (Victor) | 1913-06-10 | 105.0 s |
| `russian_revolution.ogg` | Russian Revolution 1917 | "Dubinushca" (Victor) | 1917-04-12 | 108.0 s |
| `spanish_civil_war.ogg` | End of the Spanish Civil War 1939 | "Himno de Riego" (Victor) | 1907-03-15 | 110.0 s |
| `great_war_outbreak.ogg` | Outbreak of the Great War 1914 | "Die Wacht am Rhein" (Victor) | 1914-11-10 | 103.3 s |
| `sino_japanese_war.ogg` | Outbreak of the Second Sino-Japanese War 1937 | "Japanese naval march" (Victor) | 1923-07-10 | 111.4 s |
| `balkan_wars.ogg` | First Balkan War 1912 | "War on the Balkan field" (Victor) | 1918-03-29 | 86.2 s |
| `second_balkan_war.ogg` | Second Balkan War 1913 | "Gorda stara planina" (Victor) | 1919-07-22 | 104.3 s |

## Shared conversion settings

Every final file was produced from the bit-exact Library of Congress MP3 mirrored by Internet Archive, using this command shape:

```bash
ffmpeg -y -i <download>.mp3 \
  -af "atrim=start=<SS>:duration=<DUR>,asetpts=PTS-STARTPTS,volume=<GAIN>,afade=t=in:st=0:d=2,afade=t=out:st=<DUR-3>:d=3" \
  -ar 44100 -ac 2 -c:a libvorbis -q:a 5 <name>.ogg
```

`atrim` plus `asetpts` keeps the fade timing exact after the cut, `volume` is a small trim that sets level: a downward one where the acoustic-era transfer already peaks close to full scale, an upward one on the rare side that was transferred quietly. `-q:a 5` is roughly 160 kbit/s Vorbis. Cut points were placed on detected phrase or section breaks rather than on round numbers.

## 1. Compiègne armistice 1918 — `compiegne.ogg`

- **Archive.org identifier:** `loc-jukebox-70119-ich-hatt-einen-kameraden`
- **Item title:** Ich hatt' einen Kameraden
- **Composer:** The record credits no composer. The words are Ludwig Uhland's poem "Der gute Kamerad" (1809) and the melody is the traditional setting attributed to Friedrich Silcher (1825); the LOC catalogue lists performers only.
- **Performer:** Library of Congress participant credit: `prince, charles adams ; steier, harry` — Harry Steier (tenor) with orchestra under Charles Adams Prince.
- **Recording date / publication:** recorded and published 1924-05-02; Victor matrix `B-30036/2`.
- **Source URL:** https://archive.org/details/loc-jukebox-70119-ich-hatt-einen-kameraden (original record: https://www.loc.gov/item/jukebox-70119/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement on the item: "Public domain. Sound recording first published 1924; statutory protection ended per Music Modernization Act, 17 U.S.C. sec. 1401 (100 years after publication + transition)." A 1924 US publication is also outside the 95-year copyright term, so both the recording and the underlying 19th-century song are free of rights.
- **Why this cue:** "Ich hatt' einen Kameraden" is the German military funeral song, which is exactly the mourning register for an armistice signed in defeat at Compiègne; it is sombre, slow and immediately legible as a German loss.
- **Trim:** 0.5 s → 108.0 s of a 110.6 s source. The whole surviving side is retained, only the lead-in is dropped.
- **Final duration:** 107.5 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_compiegne.mp3 -af "atrim=start=0.5:duration=107.5,asetpts=PTS-STARTPTS,volume=0dB,afade=t=in:st=0:d=2,afade=t=out:st=104.5:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 compiegne.ogg
  ```
- **Final SHA-256:** `e51be800a93bfb0232649894f1b129637b58b7bcc24ee1646baab5f0afab5e35`

## 2. Central Powers victory — `central_powers_victory.ogg`

- **Archive.org identifier:** `loc-jukebox-134784-treue-zu-kaiser-und-reich`
- **Item title:** Treue zu Kaiser und Reich
- **Composer:** Heinrich Warnken, per the LOC participant credit (`warnken, heinrich`).
- **Performer:** United States Marine Band, conducted by William H. Santelmann (`santelmann, william h.`), Victor matrix `B-14601/1`.
- **Recording date / publication:** 1914-03-20.
- **Source URL:** https://archive.org/details/loc-jukebox-134784-treue-zu-kaiser-und-reich (original record: https://www.loc.gov/item/jukebox-134784/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement: "Public domain. Sound recording first published 1914; statutory protection ended per Music Modernization Act, 17 U.S.C. sec. 1401." A 1914 publication is far outside the US copyright term for both the recording and the march itself.
- **Why this cue:** A German imperial loyalty march ("Loyalty to Kaiser and Reich") in full brass-band scoring, recorded in 1914, which is the same ceremonial register as "Heil dir im Siegerkranz"—the imperial anthem itself has no dated pre-1929 transfer on Internet Archive that also carries a clear rights statement, so the closest documented imperial German triumph march was chosen instead. The United States Marine Band of 1914 played the standard German military repertoire, so the arrangement and style are period-German rather than an American pastiche.
- **Trim:** 9.0 s → 109.0 s of a 164.7 s source, starting after the lead-in groove noise and ending on a phrase boundary covered by the fade.
- **Final duration:** 100.0 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_central.mp3 -af "atrim=start=9.0:duration=100,asetpts=PTS-STARTPTS,volume=-1.5dB,afade=t=in:st=0:d=2,afade=t=out:st=97.0:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 central_powers_victory.ogg
  ```
- **Final SHA-256:** `ab0e3864d9ff2540f228025d508ce90a4ec65e4219832336f1daac8ee9b087d7`

## 3. Fall of France 1940 — `fall_of_france.ogg`

- **Archive.org identifier:** `loc-jukebox-421981-chopin-s-funeral-march`
- **Item title:** Chopin's funeral march
- **Composer:** Frédéric Chopin — the Marche funèbre of the Piano Sonata No. 2 in B-flat minor, Op. 35.
- **Performer:** Arthur Pryor's Band, Victor matrix `C-807/00`.
- **Recording date / publication:** 1913-06-10.
- **Source URL:** https://archive.org/details/loc-jukebox-421981-chopin-s-funeral-march (original record: https://www.loc.gov/item/jukebox-421981/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement: "Public domain. Sound recording first published 1913; statutory protection ended per Music Modernization Act, 17 U.S.C. sec. 1401." Chopin died in 1849, so the composition has been free of rights for over a century, and the 1913 performance is public domain on the same 100-year recording term.
- **Why this cue:** The funeral march is the standard French and European mourning music of the period, and this is a French-repertoire band performance rather than a piano reduction, which suits a national-scale defeat cue. It is deliberately different from the German funeral song used at Compiègne so the two sombre cues do not sound interchangeable.
- **Trim:** 20.0 s → 125.0 s of a 253.2 s source, taking the march statement and the following development while avoiding the long closing section.
- **Final duration:** 105.0 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_france.mp3 -af "atrim=start=20.0:duration=105,asetpts=PTS-STARTPTS,volume=-2dB,afade=t=in:st=0:d=2,afade=t=out:st=102.0:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 fall_of_france.ogg
  ```
- **Final SHA-256:** `6cbcd5736594378ddc6175668022dc7f7979a60801704424488fe7e0a54f2cf9`

## 4. Russian Revolution 1917 — `russian_revolution.ogg`

- **Archive.org identifier:** `loc-jukebox-22563-dubinushca`
- **Item title:** Dubinushca (Дубинушка, "the little oak club")
- **Composer:** No composer credited; "Dubinushka" is a traditional Russian Volga barge-haulers' song that became a standard revolutionary song after 1905.
- **Performer:** Bernardo Olshansky (baritone) with King's Orchestra, conducted by Rosario Bourdon; Victor matrix `B-19471/1`, sung in Russian.
- **Recording date / publication:** 1917-04-12.
- **Source URL:** https://archive.org/details/loc-jukebox-22563-dubinushca (original record: https://www.loc.gov/item/jukebox-22563/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement: "Public domain. Sound recording first published 1917; statutory protection ended per Music Modernization Act, 17 U.S.C. sec. 1401." The song itself is traditional and pre-1900, and the 1917 performance is past the 100-year recording term.
- **Why this cue:** It is a genuine Russian-language revolutionary song, recorded in the revolution year, and it carries the collapse-of-the-old-order weight the event needs rather than a triumphant Soviet anthem. The baritone-and-orchestra acoustic transfer has the right rough period texture.
- **Trim:** 12.0 s → 120.0 s of a 140.0 s source, dropping the lead-in noise.
- **Final duration:** 108.0 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_russia.mp3 -af "atrim=start=12.0:duration=108,asetpts=PTS-STARTPTS,volume=-1.5dB,afade=t=in:st=0:d=2,afade=t=out:st=105.0:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 russian_revolution.ogg
  ```
- **Final SHA-256:** `68d8a6ff97c8dfe42ad3a618420ee246359df38067cdfa0703df6cf0f8f868e7`

## 5. End of the Spanish Civil War 1939 — `spanish_civil_war.ogg`

- **Archive.org identifier:** `loc-jukebox-6502-himno-de-riego`
- **Item title:** Himno de Riego
- **Composer:** Melody attributed to José Melchor Gomis (1820), words by Evaristo de San Miguel; the LOC record credits performers only.
- **Performer:** Orquesta de Felipe Valdés, with Teresa de Riego credited by the LOC catalogue; Victor matrix `O-158/1`, tagged `spanish (cuba)`.
- **Recording date / publication:** 1907-03-15.
- **Source URL:** https://archive.org/details/loc-jukebox-6502-himno-de-riego (original record: https://www.loc.gov/item/jukebox-6502/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement: "Public domain. Sound recording first published 1907; statutory protection ended per Music Modernization Act, 17 U.S.C. sec. 1401." The 1907 publication is the earliest of the five and far outside any US term.
- **Why this cue:** The Himno de Riego was the official anthem of the Spanish Republic, so a period band recording of it lands on the republican register the event asks for, and the 1907 date means the recording itself is unambiguously free.
- **Trim:** 9.0 s → 119.0 s of a 196.7 s source, starting after the run-in.
- **Final duration:** 110.0 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_spain.mp3 -af "atrim=start=9.0:duration=110,asetpts=PTS-STARTPTS,volume=-2dB,afade=t=in:st=0:d=2,afade=t=out:st=107.0:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 spanish_civil_war.ogg
  ```
- **Final SHA-256:** `9177d2fea45839762f171ed9528823a9c20528a7ab2a0849a349067a60a2aadf`

## 6. Outbreak of the Great War 1914 — `great_war_outbreak.ogg`

- **Archive.org identifier:** `loc-jukebox-11508-die-wacht-am-rhein`
- **Item title:** Die Wacht am Rhein
- **Composer:** The record credits no composer. The words are Max Schneckenburger's poem of 1840 and the melody is the setting long attributed to Karl Wilhelm (1854); the LOC participant field names `wilhelm, carl`, which is the only composer-side name on the item. Both the poem and the melody are nineteenth-century and free of rights in every jurisdiction.
- **Performer:** Library of Congress participant credit: `schlegel, carl ; rogers, walter b. ; wilhelm, carl` — a German-language vocal performance with Victor's house orchestra under Walter B. Rogers; Victor matrix `B-15364/2`, tagged `victor; german; vocal`.
- **Recording date / publication:** 1914-11-10.
- **Source URL:** https://archive.org/details/loc-jukebox-11508-die-wacht-am-rhein (original record: https://www.loc.gov/item/jukebox-11508/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement on the item: "Public domain. Sound recording first published 1914; under the Music Modernization Act (17 U.S.C. sec. 1401) recordings first published in 1914 entered the public domain 100 years after publication." The 1914 publication is also far outside the 95-year term that would apply to any other fixation.
- **Why this cue:** The Rhine-guard song was the most widely sung German patriotic song of the 1914 mobilisation, and this side was cut in November 1914, inside the war-fever months the event depicts, so the cue carries the actual sound of the outbreak rather than a later reconstruction. The mod frames the Great War from the German side, which is why the German song was preferred over the equally public-domain French alternative, the Victor Military Band's 1914-12-29 recording of the march "Le Sambre et Meuse". A German or French march of 1914 was the brief; this is the German half of that pair, and the band-and-voices scoring gives the martial pulse without adding a fifth brass-band march to the set.
- **Trim:** 0.6 s → 103.9 s of a 191.4 s source, starting where the run-in ends and stopping on a detected phrase break at 103.9 s.
- **Final duration:** 103.3 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_wacht.mp3 -af "atrim=start=0.6:duration=103.3,asetpts=PTS-STARTPTS,volume=-1.5dB,afade=t=in:st=0:d=2,afade=t=out:st=100.3:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 great_war_outbreak.ogg
  ```
- **Final SHA-256:** `034cb94c6a1d89b822c70d18761cd4116cd43b18f012903d6cff7d5f7e37b6bf`

## 7. Outbreak of the Second Sino-Japanese War 1937 — `sino_japanese_war.ogg`

- **Archive.org identifier:** `loc-jukebox-67552-japanese-naval-march`
- **Item title:** Japanese naval march
- **Composer:** No composer credit on the record. The Japanese naval march of the period is the Gunkan kōshinkyoku (軍艦行進曲, "Warship March"), melody of 1897 by Setoguchi Tōkichi on words of 1893 by Toriyama Hiraku, which is public domain on age alone. The catalogue funds no title link beyond "Japanese naval march", so the identification of this disc with that march is probable rather than documented; the rights basis does not depend on it, because the recording itself is dated 1923 and carries the Library of Congress public-domain statement.
- **Performer:** Victor Military Band under Nathaniel Shilkret, Victor matrix `B-28263/2`, tagged `victor; japanese; instrumental`.
- **Recording date / publication:** 1923-07-10.
- **Source URL:** https://archive.org/details/loc-jukebox-67552-japanese-naval-march (original record: https://www.loc.gov/item/jukebox-67552/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement on the item: "Public domain. Sound recording first published 1923; under the Music Modernization Act (17 U.S.C. sec. 1401) recordings first published in 1923 entered the public domain 100 years after publication."
- **Why this cue:** The moment is the Japanese attack on China in July 1937, and the naval march is the Japanese military-band register that the war was announced to. Every recording actually cut in 1937 or later is still in copyright in the United States until at least 2037, so a contemporaneous Chinese or Japanese disc cannot be used at all; this 1923 performance of a Japanese navy march is the latest verifiable public-domain item in that repertoire, and the march itself was still the standard Japanese naval march through the war years. The limitation is stated plainly: the band is Victor's, not a Japanese service band.
- **Trim:** 1.0 s → 112.4 s of a 176.7 s source. The side peaks at only -5.2 dB, so the cue is lifted 4 dB rather than trimmed, which brings it level with the other cues without approaching full scale.
- **Final duration:** 111.4 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_japan_naval.mp3 -af "atrim=start=1.0:duration=111.4,asetpts=PTS-STARTPTS,volume=4dB,afade=t=in:st=0:d=2,afade=t=out:st=108.4:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 sino_japanese_war.ogg
  ```
- **Final SHA-256:** `6e395d539a4926522fc014c1bf5d33df5835d28c6c000a6276ff54d99c075a62`

## 8. First Balkan War 1912 — `balkan_wars.ogg`

- **Archive.org identifier:** `loc-jukebox-28628-war-on-the-balkan-field`
- **Item title:** War on the Balkan field
- **Composer:** No composer credit; a Serbian instrumental carried by the item under the `serbian` genre tag with English title only.
- **Performer:** Library of Congress participant credit: `zerbesa, steve ; tamburăsko društvo` — Steve Zerbesa with a tamburica ensemble, Victor matrix `B-21718/1`.
- **Recording date / publication:** 1918-03-29.
- **Source URL:** https://archive.org/details/loc-jukebox-28628-war-on-the-balkan-field (original record: https://www.loc.gov/item/jukebox-28628/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement on the item: "Public domain. Sound recording first published 1918; under the Music Modernization Act (17 U.S.C. sec. 1401) recordings first published in 1918 entered the public domain 100 years after publication."
- **Why this cue:** The First Balkan War is the Serbian and Bulgarian advance that broke Ottoman Macedonia in 1912, and a Serbian tamburica ensemble playing "War on the Balkan field" is the plainest period statement of that front, cut in 1918 while the Balkan theatre was still live. Its plucked-string texture also keeps it audibly apart from the brass-band cues elsewhere in the set, so the two Balkan events do not sound like the same recording twice.
- **Trim:** 1.5 s → 87.7 s of a 187.1 s source, from the end of the run-in to a detected section break at 87.7 s.
- **Final duration:** 86.2 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_balkan.mp3 -af "atrim=start=1.5:duration=86.2,asetpts=PTS-STARTPTS,volume=0.5dB,afade=t=in:st=0:d=2,afade=t=out:st=83.2:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 balkan_wars.ogg
  ```
- **Final SHA-256:** `c01b9eb00f4acbc718b0af5c30af1e2054ce1b5c406e202e862ffe08f4a0fced`

## 9. Second Balkan War 1913 — `second_balkan_war.ogg`

- **Archive.org identifier:** `loc-jukebox-33296-gorda-stara-planina`
- **Item title:** Gorda stara planina (Горда Стара планина, "Proud Old Mountain")
- **Composer:** The record credits no composer. The song is the Bulgarian patriotic song written in 1885 by Tsvetan Radoslavov as he left to fight in the Serbo-Bulgarian war; the same melody later became the basis of Bulgaria's anthem "Mila Rodino". An 1885 composition is public domain on age alone.
- **Performer:** Library of Congress participant credit: `bourdon, rosario ; shilkret, nathaniel ; mintcheff, dimiter` — the Bulgarian tenor Dimiter Mintcheff with Victor orchestra, matrix `B-23085/1`, tagged `bulgarian; vocal`.
- **Recording date / publication:** 1919-07-22.
- **Source URL:** https://archive.org/details/loc-jukebox-33296-gorda-stara-planina (original record: https://www.loc.gov/item/jukebox-33296/)
- **Licence / public-domain basis:** Internet Archive licence `CC Public Domain Mark 1.0`, plus the Library of Congress statement on the item: "Public domain. Sound recording first published 1919; under the Music Modernization Act (17 U.S.C. sec. 1401) recordings first published in 1919 entered the public domain 100 years after publication."
- **Why this cue:** In June 1913 Bulgaria attacked Serbia and was then set upon by Serbia, Greece, Romania and the Ottomans together, and lost the Macedonia it had just helped take. A Bulgarian song born in the 1885 war against Serbia lands on exactly that enmity from the losing side, and it is a Bulgarian-language vocal rather than another band march, so it cannot be mistaken for the Serbian cue used for 1912. It is a different recording from `balkan_wars.ogg`, so nothing is reused across the two Balkan events.
- **Trim:** 1.2 s → 105.5 s of a 176.0 s source, from the end of the run-in to a detected break at 105.5 s.
- **Final duration:** 104.3 s
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i src_gorda.mp3 -af "atrim=start=1.2:duration=104.3,asetpts=PTS-STARTPTS,volume=-2.5dB,afade=t=in:st=0:d=2,afade=t=out:st=101.3:d=3" -ar 44100 -ac 2 -c:a libvorbis -q:a 5 second_balkan_war.ogg
  ```
- **Final SHA-256:** `dfcf33ffa18c9ad35bdd1837f339d8598b81144e132db9fa40b7488547e08593`

## Rejected candidates

- `heil-dir-in-siegerkranz-german-solo-by-herr-muench-78rpm` (the only literal "Heil dir im Siegerkranz" 78 transfer on Internet Archive): the uploader asserts the Public Domain Mark and the disc is plainly acoustic-era, but no recording or publication date is recorded anywhere in the item, only stamped matrix numbers (`6221`, `14370`). Without a dated publication the public-domain claim cannot be demonstrated, so it was rejected and the dated 1914 imperial march was used instead.
- The many `youtube-*` reuploads of "Heil dir im Siegerkranz" and other anthems: modern uploads of unknown provenance with no recording date or rights statement, rejected outright.
- Great 78 Project items without a rights statement (for example `78_die-wacht-am-rhein_gbia0082835a`, `78_russian-national-hymn_a-von-luoff_gbia0082939b`): the dates are usable but the item records carry no public-domain assertion, so they lost to the Library of Congress items that state the basis explicitly.
- `loc-jukebox-312598-chinese-recording`, `loc-jukebox-312589-chinese-recording` and `loc-jukebox-242261-chinese-recording` (1902–1903): the titles are only bracketed catalogue placeholders, no work is identified, so nothing can be claimed about the music even though the dates are well inside the term.
- Every Chinese and Japanese recording dated 1930 or later, including anything that could be matched to the 1937 war: a first publication after 1930 carries statutory protection past 2030 under the Music Modernization Act, so no such item could be used for the 1937 moment at all. The 1923 Japanese naval march is the alternative that survives the date test.

### Verified public domain, held as alternatives

These were checked to the same standard as the chosen items and are free of rights, but were not used for the cue named.

- `loc-jukebox-11958-le-sambre-et-meuse` — "Le Sambre et Meuse", Victor Military Band, 1914-12-29, Victor matrix `B-15551/2`: the French 1914 march half of the Great War brief, kept as the drop-in alternative to `great_war_outbreak.ogg`.
- `loc-jukebox-11129-china-national-air-the-world-s-delight` — "China national air ('The world's delight')", Victor Military Band, 1914-09-18, matrix `B-15202/1`: a Chinese air that would sit on the Chinese side of the 1937 moment, but it is 1914 and American-band scored, so the Japanese march was preferred for the aggressor's register.
- `loc-jukebox-648807-chinese-march` — "Chinese march", Ellery Band under Luigi Musso, 1913-05-20, Columbia matrix `38865/1`: a Western band's "Chinese" march, which is pastiche rather than Chinese military music.
- `loc-jukebox-66877-stambouloff-march` and `loc-jukebox-66876-pirotski-march-naroden-march` — Victor Band under Nathaniel Shilkret, 1923-04-16, matrices `B-27827/1` and `B-27826/2`, both tagged `bulgarian`: Bulgarian marches that would serve a Balkan cue, unused because the Bulgarian vocal gives the second Balkan event a different register from the Serbian instrumental.
- `loc-jukebox-33299-prosti-narode` — "Prosti narode", Dimiter Mintcheff, 1919-07-22, matrix `B-23086/2`: a Bulgarian song, but its text is a condemned man's farewell from the Ilinden generation rather than a Balkan Wars song.
- `loc-jukebox-188137-napred-stupaj` — "Napred stupaj!", 1917-07-18, tagged `serbian`: a Serbian march, unused so that the two Balkan cues are not both Serbian marches.
- `loc-jukebox-119690-japanese-national-air` — Pryor's Band, 1913-06-12: the Japanese national air, which reads as the anthem rather than the war.

## Source files and working folder

Raw downloads are kept, not deleted, in `.tmp/super_event_audio/` as `src_compiegne.mp3` (SHA-256 `d8174205c16bc3f2912dc0b2bba625a50b387f7fd8039a4242eaf1618a2f1690`), `src_central.mp3` (`6a9eb66fa1fe147688db7851d8efdf1848aa7a5a9eb3d6d2b5331e92920b5c91`), `src_france.mp3` (`5bbac24f5d75336f808040076761c124afe5c074332dd447ef85f7e0bed1b516`), `src_russia.mp3` (`06abf8bba9fe61a8bc7c0eefa2655b1f9455dd9a824d6bcdb6533b750c88db82`), `src_spain.mp3` (`c2cbbe7f6fb0e1a03967ac48c2fc5cc2d1a67aef2051f00c64138de4de3ed103`), `src_wacht.mp3` (`087f56f7e7ac42f7e24839c83380d12602a06c2f836b1d2fd9efa3222374c110`), `src_japan_naval.mp3` (`ceb3c4d28a5cf4d3e6cc0efe22a707765017d4e8c4d1897e832d90b32233b047`), `src_balkan.mp3` (`58f228f664873b1bddcfc6094433203db0058b08bd8bce2ac4074a1b02a107e5`) and `src_gorda.mp3` (`610e75f2297ae74bd59def5655d3a6dfa307a7ed330dd1f15c374b4d54a43c3a`).

## Wiring note for the implementation owner

The files are named for direct use as sound asset ids; this sheet does not define the `sound/*.asset` entries or the `sound_effect` calls, because that wiring belongs to the implementation change. Suggested ids: `endsieg_compiegne`, `endsieg_central_powers_victory`, `endsieg_fall_of_france`, `endsieg_russian_revolution`, `endsieg_spanish_civil_war`, `endsieg_great_war_outbreak`, `endsieg_sino_japanese_war`, `endsieg_balkan_wars` and `endsieg_second_balkan_war`, each pointing at `sound/endsieg_super_events/<file>.ogg`.
