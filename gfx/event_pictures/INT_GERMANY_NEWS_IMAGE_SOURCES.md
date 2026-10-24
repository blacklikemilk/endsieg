# German interwar news photographs

Each image is a cropped or padded 397 × 153 RGBA DDS derived from the linked historical photograph. Source and reuse details are on the linked Commons file pages.

- `int_ger_news_constitution.dds`: [1919 Weimar government.jpg](https://commons.wikimedia.org/wiki/File:1919_Weimar_government.jpg) — Public domain.
- `int_ger_news_kapp.dds`: [Kapp demo.jpg](https://commons.wikimedia.org/wiki/File:Kapp_demo.jpg) — Public domain.
- `int_ger_news_rathenau.dds`: [Walther Rathenau.jpg](https://commons.wikimedia.org/wiki/File:Walther_Rathenau.jpg) — Public domain.
- `int_ger_news_ruhr.dds`: [13-1-23 Essen patrouille de dragons français (5e rgt).jpg](https://commons.wikimedia.org/wiki/File:13-1-23_Essen_patrouille_de_dragons_fran%C3%A7ais_%285e_rgt%29.jpg) — Public domain.
- `int_ger_news_currency.dds`: [Hjalmar Schacht.jpg](https://commons.wikimedia.org/wiki/File:Hjalmar_Schacht.jpg) — Public domain.
- `int_ger_news_hindenburg.dds`: [Von Hindenburg.jpg](https://commons.wikimedia.org/wiki/File:Von_Hindenburg.jpg) — Public domain.
- `int_ger_news_locarno.dds`: Roger Dumas, [German delegation at Locarno, 7 October 1925](https://commons.wikimedia.org/wiki/File:1925_German_Delegation_Locarno.jpg), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Cropped, resized, and converted to DDS for Endsieg.
- `int_ger_news_league.dds`: [Genève, 10-9-26, S. des N., discours de M. Stresemann - btv1b531679168.jpg](https://commons.wikimedia.org/wiki/File:Gen%C3%A8ve%2C_10-9-26%2C_S._des_N.%2C_discours_de_M._Stresemann_-_btv1b531679168.jpg) — Public domain.
- `int_ger_news_depression.dds`: [Crowd outside nyse.jpg](https://commons.wikimedia.org/wiki/File:Crowd_outside_nyse.jpg) — Public domain.
- `int_ger_news_young.dds`: [Reparations Commission with Stevenson, 6-25-29 LCCN2016843978.jpg](https://commons.wikimedia.org/wiki/File:Reparations_Commission_with_Stevenson%2C_6-25-29_LCCN2016843978.jpg) — Public domain.
- `int_ger_news_prussia.dds`: [PapenSchleicher0001.jpg](https://commons.wikimedia.org/wiki/File:PapenSchleicher0001.jpg) — Public domain.
- `int_ger_news_hitler.dds`: [HitlerYSuGobierno1933.jpeg](https://commons.wikimedia.org/wiki/File:HitlerYSuGobierno1933.jpeg) — Public domain.

The six later headlines use distinct pictures rather than repeating the portraits
or photographs above. All additions are cropped or resized to 397 × 153 RGBA
DDS; the four downloaded source JPEGs are in `interwar_news_sources/`.

- `int_ger_news_rapallo.dds`: adapted from the existing Endsieg `news_event_rapallo.dds` photograph.
- `int_ger_news_ruhr_occupation.dds`: adapted from the existing Endsieg `news_event_ruhr_occupation.dds` photograph.
- `int_ger_news_hyperinflation.dds`: [Reichsbank money delivery office, Berlin, October 1923](https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_183-R1215-506,_Berlin,_Reichsbank,_Geldauflieferungsstelle.jpg) — Bundesarchiv, Bild 183-R1215-506 / [CC BY-SA 3.0 DE](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en); cropped and resized.
- `int_ger_news_lausanne.dds`: Agence Rol, [von Papen and von Neurath at Lausanne, 15 June 1932](https://commons.wikimedia.org/wiki/File:15-6-32_(Lausanne,_de_g._%C3%A0_d.)_von_Papen_et_von_Neurath_-_btv1b53256311c.jpg) — Public domain; cropped and resized.
- `int_ger_news_enabling_act.dds`: Georg Pahl, [speech in the Kroll Opera House on the Enabling Act, 23 March 1933](https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_102-14439,_Rede_Adolf_Hitlers_zum_Erm%C3%A4chtigungsgesetz.jpg) — Bundesarchiv, Bild 102-14439 / [CC BY-SA 3.0 DE](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en); cropped and resized.
- `int_ger_news_hindenburg_funeral.dds`: [Hindenburg's funeral at the Tannenberg Memorial, 7 August 1934](https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_183-2006-0429-502,_Tannenberg-Denkmal,_Beisetzung_Hindenburg.jpg) — Bundesarchiv, Bild 183-2006-0429-502 / [CC BY-SA 3.0 DE](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en); cropped and resized.

Run `python tools/build_interwar_german_news_images.py` to package the six
additional pictures and refresh `interwar_news_preview.png`. Run it with
`--check` to verify all 18 event-to-sprite-to-image references and dimensions.
