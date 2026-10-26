# Super Events image provenance

This sheet records the photographic panel backdrops that sit behind the super-event text, and the basis for using each one.

Each entry names the source page, the original file name on that page, the photographer or credit the archive states, the date of the photograph, the licence exactly as the source states it, and the archive identifier.
Every file was fetched over HTTPS from Wikimedia Commons, whose MediaWiki `extmetadata` for that file returns `LicenseShortName` = `Public domain` (seven files) or `CC0` (one file).
No item carries an attribution requirement, a modern agency watermark, or a rights reservation.
Nothing requiring attribution was used, so no credit line is needed in game.

Panel images are 1600x900 RGB PNG, 8-bit, no alpha, each under 3 MB. They live in `gfx/super_events/` under the file names the sprite wiring expects.
This sheet covers image files only. No `.gfx`, `.gui`, `.txt`, `.yml` or `.asset` file was changed while producing them.

## Summary

| Final file | Moment | Source archive | Photograph dated | Licence as stated |
| --- | --- | --- | --- | --- |
| `endsieg_se_central_powers_victory.png` | Central Powers victory in the west | US National Archives via Commons | 1917–1918 | Public domain |
| `endsieg_se_fall_of_france.png` | Fall of France, June 1940 | Commons (period postcard booklet) | June 1940 | Public domain |
| `endsieg_se_russian_revolution.png` | Petrograd, July Days 1917 | Commons (Viktor Bulla) | 4 July 1917 | Public domain |
| `endsieg_se_spanish_civil_war.png` | Spanish Civil War, Catalan front | Biblioteca Virtual de Defensa via Commons | 1938–1939 | CC0 1.0 |
| `endsieg_se_great_war_outbreak.png` | Mobilisation, Berlin | Imperial War Museums via Commons (IWM Q 81739) | 1 August 1914 | Public domain |
| `endsieg_se_sino_japanese_war.png` | North China front | Foreign Affairs Association of Japan via Commons (Yomiuri photograph) | 1937 | Public domain |
| `endsieg_se_first_balkan_war.png` | Serbian siege artillery before Monastir | Agence Rol / Bibliothèque nationale de France via Commons | November 1912 | Public domain |
| `endsieg_se_second_balkan_war.png` | Serbian army's return to Belgrade | Belgrade City Library via Commons | 11 August 1913 | Public domain |

## Shared processing

Every panel uses the same filter chain so the five super-event backdrops read as one set: crop to 16:9, downscale to 1600x900, desaturate to three-quarter saturation and pull the image slightly down so white panel text keeps its contrast.

```bash
-vf "crop=<w>:<h>:<x>:<y>,scale=1600:900,eq=saturation=0.75:brightness=-0.02"
```

`-pred mixed` is passed to the PNG encoder, and `-pix_fmt rgb24` is set where the source carried an alpha channel, so all four files match the existing `endsieg_se_compiegne.png` in pixel format.

Source renditions were downloaded to a scratch folder outside the repository; nothing from `docs/assets/` is referenced at runtime.

### Download commands

```bash
UA="EndsiegHOI4Mod/1.0 (modding research)"

curl -sL -A "$UA" -o a_berlin.jpg     "https://commons.wikimedia.org/wiki/Special:FilePath/Enemy%20Activities%20-%20German%20Revolution%20-%20Returned%20German%20troops%20in%20Berlin%2C%20Germany.%20German%20troops%20back%20from%20action%20shown%20%22Unter%20der%20Linden%22%20dense%20crowds%20gather%20to%20see%20them%20march%20by%2C%20and%20general%20attitude%20towards%20the(...)%20-%20NARA%20-%2031478395.jpg?width=3200"
curl -sL -A "$UA" -o c_lechesne_eglise.jpg "https://upload.wikimedia.org/wikipedia/commons/5/5b/Le_Chesne-FR-08-juin_1940-%C3%A9glise-1.jpg"
curl -sL -A "$UA" -o e_petrograd.png  "https://upload.wikimedia.org/wikipedia/commons/f/ff/19170704_Riot_on_Nevsky_prosp_Petrograd.png"
curl -sL -A "$UA" -o g_tortosa.jpg    "https://upload.wikimedia.org/wikipedia/commons/1/18/J_mmue_201334_00001.jpg"
```

## 1. Central Powers victory — `endsieg_se_central_powers_victory.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:Enemy_Activities_-_German_Revolution_-_Returned_German_troops_in_Berlin,_Germany._German_troops_back_from_action_shown_%22Unter_der_Linden%22_dense_crowds_gather_to_see_them_march_by,_and_general_attitude_towards_the(...)_-_NARA_-_31478395.jpg>
- **Original file name:** `Enemy Activities - German Revolution - Returned German troops in Berlin, Germany. German troops back from action shown "Unter der Linden" dense crowds gather to see them march by, and general attitude towards the(...) - NARA - 31478395.jpg`
- **Author / photographer:** the NARA caption card credits the photographic agency **Underwood & Underwood**; the Commons author field reads "Unknown author". Credit line on the card: U.S. National Archives and Records Administration.
- **Date of the photograph:** NARA and Commons date the item 1917–1918; the Committee on Public Information card is stamped `REC'D 2-15-19`. The scene is the return of front-line troops to Berlin after the armistice, watched by crowds along Unter den Linden.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`). The photograph was published in the United States before 1929 and is a Committee on Public Information / Underwood & Underwood item held by NARA, so no term survives.
- **Identifier:** NARA 31478395 (Commons file title suffix `NARA - 31478395`).
- **Source size:** 9117x6284 scan of the full archival card. The working download is the 3840x2647 MediaWiki rendition.
- **Subject match:** German troops parading through the imperial capital with dense civilian crowds, which is the exact subject this panel needs.
- **Crop:** the scan is a card, with the photograph set into the right side and a typed caption block, red `165-WW 159 36` stamp and handwritten numbers on the mount. Row and column brightness scans located the photographic area at roughly x 1490–3495, y 345–1870; the 16:9 window sits fully inside it, so no card margin, caption, stamp or negative number survives. Figures climbing the bare trees and the receding avenue keep the frame busy without any focal portrait, which suits a background.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i a_berlin.jpg -vf "crop=2000:1125:1495:400,scale=1600:900,eq=saturation=0.75:brightness=-0.02" -pred mixed endsieg_se_central_powers_victory.png
  ```
- **Final file:** 1600x900, rgb24, 1 878 860 bytes. SHA-256 `47ae900472d110a2438cdef5fd6fb861e6bf26cec991a75ac4d9dcbdfabc58bb`.

## 2. Fall of France — `endsieg_se_fall_of_france.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:Le_Chesne-FR-08-juin_1940-%C3%A9glise-1.jpg>
- **Original file name:** `Le Chesne-FR-08-juin 1940-église-1.jpg`
- **Author / photographer:** unknown; the Commons credit field names the source publication, the postcard booklet "Sedan 40e anniversaire 10 mai 1940", Imprimerie Félix, Vouziers (Ardennes).
- **Date of the photograph:** June 1940, after the May 1940 bombardments of the Ardennes; Commons records the print as 1940-06-28.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`). The photograph is an anonymous work published in France in 1940, so the French term for anonymous works has run, and it is public domain in the United States as a pre-1946 publication.
- **Identifier:** Wikimedia Commons file name above; the plate is one of a numbered set in that booklet.
- **Source size:** 3531x2503, a halftone reproduction with the print's white margin and visible screen ruling.
- **Subject match:** the church and the gutted houses of Le Chesne in ruins after the May 1940 bombing, which is the "bombed town" reading of the panel rather than the refugee column. The surviving spire against a blank white sky carries the overcast, emptied-out register of the reference panel.
- **Crop:** inset 25 px on each side to drop the print border, then a centred 16:9 window that keeps the ruined church, the hollow façades to its left and the more intact house at the right edge.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i c_lechesne_eglise.jpg -vf "crop=3481:1958:25:272,scale=1600:900,eq=saturation=0.75:brightness=-0.02" -pred mixed endsieg_se_fall_of_france.png
  ```
- **Final file:** 1600x900, rgb24, 2 905 551 bytes. SHA-256 `5f3a9fbe6c47ad4a73598ea851b654e342112177acb3cc3d51cedfeb282c633c`.
- **Note on contrast:** the rubble and sky make the lower band of this panel the lightest of the five. The panel's own dark overlay carries the white text; if the description block ever sits directly on the image without a scrim, this is the panel to check first.

## 3. Russian Revolution — `endsieg_se_russian_revolution.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:19170704_Riot_on_Nevsky_prosp_Petrograd.png>
- **Original file name:** `19170704 Riot on Nevsky prosp Petrograd.png`
- **Author / photographer:** **Viktor Bulla** (1883–1938).
- **Date of the photograph:** 4 July 1917 (17 July New Style), the July Days. Commons describes it as the street demonstration on Nevsky Prospekt just after Provisional Government troops opened fire with machine guns.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`). Bulla died in 1938, so the Russian and EU terms have run, and the print was published before 1929 for United States purposes.
- **Identifier:** Wikimedia Commons file name above. A JPEG rendition of the same plate exists as `19170704 Riot on Nevsky prosp Petrograd.jpg`.
- **Source size:** 3025x1749 PNG with an alpha channel, converted to rgb24 on output.
- **Subject match:** the crowd on Nevsky Prospekt scattering under fire, with the classical façade and tram rails in frame. It reads as a street in collapse rather than a staged parade, which is the register this panel needs.
- **Crop:** a 2800x1575 window inset from the left and top edges discards the emptiest pavement and the top of the building, so the fleeing figures, prone bodies and the lamppost fill the frame.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i e_petrograd.png -vf "crop=2800:1575:110:60,scale=1600:900,eq=saturation=0.75:brightness=-0.02" -pix_fmt rgb24 -pred mixed endsieg_se_russian_revolution.png
  ```
- **Final file:** 1600x900, rgb24, 2 668 390 bytes. SHA-256 `c39569ebc28cf70e1b8f2549cf64e013c5b30d735b939a0b6fd66c47008e1d76`.

## 4. Spanish Civil War — `endsieg_se_spanish_civil_war.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:J_mmue_201334_00001.jpg>
- **Original file name:** `J mmue 201334 00001.jpg`
- **Author / photographer:** unknown; the item is held by the **Biblioteca Virtual de Defensa** (Spanish Ministry of Defence library) and catalogued as `MUE-201334`.
- **Date of the photograph:** between 1938 and 1939, on the Catalan front; the catalogue description places the column in one of the villages near Tortosa, during the Nationalist advance through Catalonia.
- **Licence as the source states it:** `CC0` / `Creative Commons Zero, Public Domain Dedication` (`LicenseUrl` <http://creativecommons.org/publicdomain/zero/1.0/deed.en>). CC0 imposes no attribution condition.
- **Identifier:** `MUE-201334` (Biblioteca Virtual de Defensa: "Fotografía de tropas nacionales en Tortosa durante la guerra civil").
- **Source size:** 2683x1991.
- **Subject match:** a Nationalist column of cavalry, pack animals and a light tankette moving through a whitewashed village street at the close of the war. This is the "troops marching into a city" reading of the panel; the roadside crowd and the Italian pattern equipment date it firmly to the Catalan campaign.
- **Crop:** the upper sky band is cut and the window is taken from just above the tankette to the road, keeping the vehicle, the leading rider and the buildings.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i g_tortosa.jpg -vf "crop=2683:1509:0:280,scale=1600:900,eq=saturation=0.75:brightness=-0.02" -pred mixed endsieg_se_spanish_civil_war.png
  ```
- **Final file:** 1600x900, rgb24, 1 521 984 bytes. SHA-256 `666dcc10f52a6625003b5708d97afb79a39396250e8d7b22a9c4d6c33688fd6d`.

## 5. Great War outbreak — `endsieg_se_great_war_outbreak.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:Crowd_cheers_the_Kaiser_at_the_Berliner_Stadtschloss,_1914.jpg>
- **Original file name:** `Crowd cheers the Kaiser at the Berliner Stadtschloss, 1914.jpg`
- **Author / photographer:** unknown; the Commons author field reads "Unknown author", and the credit field states that the scan comes from the collections of the **Imperial War Museums** as `Q 81739`.
- **Date of the photograph:** 1 August 1914, the day the German mobilisation order was announced. The crowd fills the Schlossfreiheit in front of the Berliner Schloss with the Kaiser on the balcony.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`; `AttributionRequired` false, `Copyrighted` false). The file carries the `PD-scan (PD-UKGov)` and `UK Government artistic works` categories, so the IWM scan is treated as a public-domain UK Government work.
- **Identifier:** IWM Q 81739; Commons file title above.
- **Source size:** 5417x3848. The working download is the 1920x1364 MediaWiki rendition.
- **Subject match:** the mobilisation crowd itself, hats raised towards the palace balcony, with the palace façade and its trees filling the upper frame. It is the "crowds outside a palace" reading of the panel rather than a troop train, and it carries the same dense-figure texture as the reference Petrograd panel.
- **Crop:** full width, with a 1080-tall window starting 150 px down so the palace cornice stays in frame; the bottom 134 px of the nearest crowd is dropped. The scan is full-bleed and carries no caption card, caption strip, stamp or border.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i aw_kaiser.jpg -vf "crop=1505:1080:208:150,scale=457:328:flags=lanczos,eq=saturation=0.75:brightness=-0.02" -pix_fmt rgb24 -pred mixed endsieg_se_great_war_outbreak.png
  ```
- **Final file:** 457x328, rgb24, 254 856 bytes. SHA-256 `cab5a3b31cd742f9a7d1b3555d66b2c17daeb9f6b544286e186920ffce4a75b6`.

## 6. Sino-Japanese War — `endsieg_se_sino_japanese_war.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:How_the_North_China_affair_arose_3.png>
- **Original file name:** `How the North China affair arose 3.png`
- **Author / photographer:** the booklet's publisher, the **Foreign Affairs Association of Japan**; the caption credits a **Yomiuri** photograph and names no individual photographer.
- **Date of the photograph:** 1937. The caption in the source booklet reads "How a Piece of the War Field in North China Looks (Yomiuri photo)", placing it on the North China front in the opening months of the war.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`; `AttributionRequired` false, `Copyrighted` false), carried on the file as `PD-1996`. The booklet was published in Japan in 1937 as an anonymous corporate work, so the Japanese term had run before the 1996 restoration date and the United States term never attached.
- **Identifier:** Commons file title above; the page is scanned from `Index:How the North China affair arose.pdf` on Wikisource.
- **Source size:** 2728x1766. The working download is the 1920x1243 MediaWiki rendition.
- **Subject match:** a column of troops with pack animals on a road between tall crops, with a single tree closing the middle distance. This is the war as it was photographed in the field in 1937 rather than a city entry.
- **Why this frame and not a city street:** every public-domain July 1937 photograph of Japanese troops entering a Chinese city that was located is either a halftone magazine page at 1200–1900 px with a page number or agency credit in the frame, or a wire-service frame credited to a news agency on Commons, so none met the no-lettering and rights standard. A Chinese-defence barricade photograph of July 1937 (`Soldiers of the Chinese 29th Route Army in Beijing…`) was tested and rejected on print quality: at 457 px the halftone screen and blown highlights turn the street into noise.
- **Crop:** full width, with the 1080-tall window bottom-aligned at y=163 so the featureless sky band is cut and the column, cart track and tree carry the frame.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i How_the_North_China_affair_arose_3_png.png -vf "crop=1505:1080:208:163,scale=457:328:flags=lanczos,eq=saturation=0.75:brightness=-0.02" -pix_fmt rgb24 -pred mixed endsieg_se_sino_japanese_war.png
  ```
- **Final file:** 457x328, rgb24, 205 629 bytes. SHA-256 `e7a14c5e394569aa591967174fdd3ce25fd2dfd85394bff206f2bd514485caef`.

## 7. First Balkan War — `endsieg_se_first_balkan_war.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:Artillerie_de_forteresse_serbe_pendant_le_si%C3%A8ge_de_Monastir_-_btv1b53114423v.jpg>
- **Original file name:** `Artillerie de forteresse serbe pendant le siège de Monastir - btv1b53114423v.jpg`
- **Author / photographer:** **Agence Rol**, the Paris press agency, recorded as commissioning agency; the print is held by the **Bibliothèque nationale de France**.
- **Date of the photograph:** November 1912 ("Couverture : .. novembre 1912" in the BnF record), during the siege of Monastir (Bitola) in the First Balkan War.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`; `AttributionRequired` false, `Copyrighted` false), carried as `PD-1996`, `PD US expired` and `PD France`. The agency photograph was published in 1912, so both terms have run.
- **Identifier:** Gallica/BnF shelfmark `btv1b53114423v`; Agence Rol reference `Rol, 25329`; documentary set `Pho20Rol`.
- **Source size:** 8355x6018. The working download is the 1920x1383 MediaWiki rendition.
- **Subject match:** a Serbian fortress battery in a churned emplacement, the long barrel of the leading gun angled across the frame, the crew in greatcoats around the breech and a second gun behind. It is the Serbian siege artillery of the First Balkan War with the guns in place, which is the "artillery on the move" register of the panel.
- **Crop:** the window is inset to x 420–1920 and y 420–1264, which steps past two features of the glass plate: the broken top-left corner, whose black wedge reaches down to about y 400 at the left edge, and the white negative numbers scratched at the lower left around x 96–400, y 1240–1345. Nothing from either survives in the final panel.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i Artillerie_de_forteresse_serbe_pendant_le_si_ge_de_Monastir_.jpg -vf "crop=1176:844:582:420,scale=457:328:flags=lanczos,eq=saturation=0.75:brightness=-0.02" -pix_fmt rgb24 -pred mixed endsieg_se_first_balkan_war.png
  ```
- **Final file:** 457x328, rgb24, 191 375 bytes. SHA-256 `14d613f6009c1bf3f53cae9f68a6b901708e28905856fb48d434bd0b35787064`.

## 8. Second Balkan War — `endsieg_se_second_balkan_war.png`

- **Source page:** <https://commons.wikimedia.org/wiki/File:Srpska_vojska_u_Beogradu.jpg>
- **Original file name:** `Srpska vojska u Beogradu.jpg` ("The Serbian army in Belgrade").
- **Author / photographer:** unknown; the item is a plate from the monograph "Svečani dolazak vojske i otkrivanje Karađorđevog spomenika 11. avgusta 1913. godine u Beogradu", held in the Local History Department of the **Belgrade City Library** and in that library's digital collection.
- **Date of the photograph:** 11 August 1913, the ceremonial return of the Serbian army to Belgrade under Crown Prince Aleksandar Karađorđević after the Second Balkan War.
- **Licence as the source states it:** `Public domain` (`LicenseShortName` and `UsageTerms` both `Public domain`; `AttributionRequired` false, `Copyrighted` false), carried as `PD-Serbia` on a Belgrade City Library content donation with `VRTS permission confirmed`.
- **Identifier:** Commons file title above; Belgrade City Library digital library, monograph of 11 August 1913.
- **Source size:** 1769x1251, the library's own scan; no larger rendition exists.
- **Subject match:** the returning army marching down a Belgrade street lined with civilians, tram rails underfoot. This is the aftermath reading the panel allows. The Second Balkan War's fighting was over by 10 August 1913, and no public-domain photograph of the June–July 1913 fighting was located at a usable resolution.
- **Crop:** the window drops below the shopfront band at y=348, which removes the legible Cyrillic shop signs, and runs from x 80 to 1682 so the marching column and the crowd fill the frame. Only blurred, unreadable façade detail remains above the heads.
- **ffmpeg command:**
  ```bash
  ffmpeg -y -i Srpska_vojska_u_Beogradu_jpg.jpg -vf "crop=1255:901:254:348,scale=457:328:flags=lanczos,eq=saturation=0.75:brightness=-0.02" -pix_fmt rgb24 -pred mixed endsieg_se_second_balkan_war.png
  ```
- **Final file:** 457x328, rgb24, 242 614 bytes. SHA-256 `55e1bc06a77c8dc8a0e0193e03f87d4d7205546be380a42b18b21219a4e1c49e`.

### Download commands for sections 5–8

```bash
UA="EndsiegHOI4Mod/1.0 (modding research)"

curl -sL -A "$UA" -o aw_kaiser.jpg "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/53/Crowd_cheers_the_Kaiser_at_the_Berliner_Stadtschloss%2C_1914.jpg/1920px-Crowd_cheers_the_Kaiser_at_the_Berliner_Stadtschloss%2C_1914.jpg"
curl -sL -A "$UA" -o How_the_North_China_affair_arose_3_png.png "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3b/How_the_North_China_affair_arose_3.png/1920px-How_the_North_China_affair_arose_3.png"
curl -sL -A "$UA" -o Artillerie_de_forteresse_serbe_pendant_le_si_ge_de_Monastir_.jpg "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/ff/Artillerie_de_forteresse_serbe_pendant_le_si%C3%A8ge_de_Monastir_-_btv1b53114423v.jpg/1920px-Artillerie_de_forteresse_serbe_pendant_le_si%C3%A8ge_de_Monastir_-_btv1b53114423v.jpg"
curl -sL -A "$UA" -o Srpska_vojska_u_Beogradu_jpg.jpg "https://upload.wikimedia.org/wikipedia/commons/2/28/Srpska_vojska_u_Beogradu.jpg"
```

### Notes on the 1914–1913 set

Sections 5–8 are the four panels whose image slot draws at 457x328, and they use the same filter chain as sections 1–4 with the window sized to that slot.
`-pix_fmt rgb24` is forced on all four because two of the sources arrive as grayscale JPEG and one as a PNG with an alpha channel, and the shipped set has to match `endsieg_se_compiegne.png`.
The four were checked at final size for captions, plate numbers, borders and legible signage; the only marks found were the BnF plate numbers and the broken plate corner in section 7 and the shopfront band in section 8, and both are outside the crop.
The North China panel is the lightest of the set and the Belgrade panel the darkest; on both, the panel's own dark overlay carries the white text.

## Rejected candidates

These were examined and dropped, so a later pass does not have to re-check them.

| Candidate | Reason for rejection |
| --- | --- |
| `A Frenchman weeps as German soldiers march into the French capital, Paris, on June 14, 1940` (NARA 535892) | The NARA card dates it to a Marseille ceremony of September 1940 or February 1941, and the picture is an identified French press photograph ("The Weeping Frenchman"), so the PD tag on the NARA copy does not settle the photographer's rights. |
| Bundesarchiv Paris and Limoges photographs (`Bild 101I-126-…`, `Bild 146-1975-021-29`) | `CC BY-SA 3.0 de`, which requires attribution. |
| Bibliothèque départementale photographs of the Argelès-sur-Mer camps (`22NUM27FI…`) | `CC BY-SA 4.0`, which requires attribution. |
| `People of Madrid seek refuge in the metro during the Francoist bombings` | Photograph by Alfonso Sánchez Portela (d. 1990), still protected in Spain. |
| `Condor Legion marching during the Spanish Civil War` (USHMM 734682), León victory parade, 22 May 1939 | Marked public domain, but the frame carries large legible "FRANCO" banners, which breaks the no-readable-text rule, and the 1636x1200 scan is too small to hold up at 1600x900. |
| `Barcelona bombing (1938)` | Public domain, but an aerial view of bomb damage rather than a street-level scene. |
| `Japanese troops attacking on the Woosung front` (Agence Meurisse, BnF, 5790x4110, PD) | Mislabelled on Commons: the 5790 px scan shows French colonial infantry under Adrian helmets in a First World War shellscape, not Japanese troops at Shanghai. The other 5–6000 px frames from the same batch carry the same risk, so the batch was abandoned. |
| `First pictures of the Japanese occupation of Peiping in China` (13 August 1937) | The right subject, and a clean continuous-tone scan, but the Commons credit field names **Associated Press**, which leaves the rights basis of a syndicated news frame unsettled. |
| `How the North China affair arose 4` (Japanese guards at Kuanganmen, Peiping, July 1937) | A portrait plate: no 16:9 window holds the Peiping gate and the three soldiers together without cutting heads or feet. |
| `Soldiers of the Chinese 29th Route Army in Beijing preparing for battle` (July 1937) | Exact subject and date, but a coarse halftone from a 1989 book reproduction; at 457 px the screen and blown highlights reduce the street to noise. |
| `Bugarska baterija` ("Bulgarian battery", Belgrade 1913) | The file name and the Commons description disagree on what the gun is, and the frame cannot settle it, so it was not used. |
| `L'armée serbe dans une caserne turque à Uskub` (Rol 25642, 8488x6122, PD) | A strong Serbian-army frame, but the BnF record dates the covering to **January 1913**, which is the First Balkan War, not the Second. |
| `Groupe d'hommes, de femmes et d'enfants et un soldat au milieu de décombres du village` (Albert-Kahn, Stéphane Passet, 20 September 1913, CC0) | Right moment, right licence, an unmistakable Second Balkan War aftermath scene near Melnik, but the plate is an autochrome; through the shared chain it keeps its colour and breaks the black-and-white set. |
| `Balkans (troupes d'une armée belligérante en position de tir avec des mitrailleuses)` (Rol 24061, 1912) | An Ottoman machine-gun position, and the BnF caption names no belligerent; wrong side for a Balkan League panel with no way to establish the unit. |

## Outstanding

The panel sprites in `interface/endsieg_super_events.gfx` are the parent agent's wiring step; the four files in sections 1–4 use the exact file names that wiring expects, and `endsieg_se_great_war_outbreak.png`, `endsieg_se_sino_japanese_war.png`, `endsieg_se_first_balkan_war.png` and `endsieg_se_second_balkan_war.png` are in place and awaiting their sprite entries.
