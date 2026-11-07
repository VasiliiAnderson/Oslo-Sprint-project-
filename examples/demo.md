# Pitchgjennomgang

Demoen bruker [betalingsparet](payment-terms.json) og kjøres med ekte analyse på Rajvirs maskin. Eksempelmodus er en tydelig merket reserve.

## Før demoen

- [ ] Backend kjører med `ANALYSIS_MODE=live` på Rajvirs maskin, og `python examples/run_cases.py` gir et riktig betalingsfunn.
- [ ] Frontend kjører, og nettleseren er zoomet slik at begge tekstfeltene og funnkortet synes.
- [ ] Tilbudet og kontrakten fra `payment-terms.json` ligger klare til innliming i et eget vindu.
- [ ] Reserve: en annen terminal der backend kan startes med `ANALYSIS_MODE=mock`.

## Manus (ca. 2 minutter)

1. **Problemet (20 s).** «Små tjenestebedrifter sender et tilbud, og så kommer kunden tilbake med sin egen kontrakt. Vilkårene endrer seg i det stille, og ingen har tid eller råd til å la en jurist lese alt.»
2. **Lim inn (15 s).** Lim inn tilbudet i «Tilbud» og kontrakten i «Kundens kontrakt». «Her er et typisk tilbud på en landingsside, og kundens kontrakt.»
3. **Analyser (20 s).** Trykk **Analyser**. Mens «Analyserer …» vises: «Appen sammenligner dokumentene fra leverandørens side.»
4. **Funnet (30 s).** Pek på kortet: status `avvik`, kategori betaling. «Tilbudet sier 14 dager. Kontrakten sier 60 dager.» Vis sitatet merket «Tilbud» og sitatet merket «Kontrakt». «Hvert funn har sitat fra begge dokumentene, og sitatene sjekkes mot kildeteksten, så du ser nøyaktig hvor det står.»
5. **Velg og kopier (25 s).** Kryss av funnet. Vis svarutkastet med «Hei,», forslaget om 14 dager og «Vennlig hilsen». Trykk **Kopier svar**. «Nå har du en e-post til kunden på sekunder.»
6. **Avslutning (10 s).** «Leveransen og revisjonsrundene var like, så appen lot dem være. Du får bare det som faktisk trenger oppfølging.»

## Hvis noe går galt

- **Live-analysen feiler eller tar for lang tid:** Bytt til mock-backend. Si tydelig: «Her viser jeg eksempelmodus, merket som eksempel på skjermen, med samme format som den ekte analysen.»
- **Modellen gir et uventet ekstra funn:** Vis det kort, og fokuser på betalingsfunnet.
- **Kopiering feiler:** Marker teksten og kopier med Ctrl+C.
