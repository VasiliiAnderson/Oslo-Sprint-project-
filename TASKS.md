# Arbeidsplan for MVP

Vi bygger én norsk side der en liten tjenestebedrift limer inn tilbudet og kundens kontrakt, ser funn med tekstbelegg og velger punkter til et svarutkast. Appen kjører lokalt. Første gjennomgang bruker fiktive dokumenter. Eksempelmodus fungerer på alle maskiner. Rajvir kjører den ekte analysen med lokal API-nøkkel.

Les [oppstart](README.md), [arbeidsregler](AGENTS.md) og [API og grensesnitt](docs/api.md). Alle starter fra samme delte commit på `main`. Opprett bare branchen for egen oppgave. Avtal eventuelle endringer i felles API med Rajvir før de gjøres.

| Eier | Oppgave | Branch | Filområde |
| --- | --- | --- | --- |
| Elias | Frontend | `feat/frontend` | `frontend/` |
| Rajvir med Codex | Backend og integrasjon | `feat/backend` | `backend/app/main.py`, `schemas.py`, ny `openai_client.py`, ny `review.py` og backend-konfigurasjon |
| Herman | Instruksjoner til modellen | `feat/analysis` | `backend/app/analysis/` |
| Vasilii | Testeksempler og demo | `feat/test-demo` | `examples/` |

## Elias · Frontend

1. Start FastAPI i mock-modus og React som beskrevet i [README](README.md). Bygg videre på skjermbildet som finnes. Bruk [dokumentparet](examples/payment-terms.json) og [eksempelsvaret](examples/mock-response.json).
2. Vis «Tilbud» og «Kundens kontrakt» øverst, side om side når plassen tillater det. «Analyser» sender begge tekstene til `POST /analyze`. Deaktiver knappen hvis et felt er tomt eller mer enn 20 000 tegn etter trimming. Under forespørselen vises «Analyserer …», og feltene og knappen er deaktivert.
3. Vis funn i rekkefølgen fra API-et. Hvert kort har status, kategori, forklaring og de tilgjengelige sitatene, tydelig merket «Tilbud» og «Kontrakt». Merk mock-svaret med «Eksempelmodus». Vis «Ingen funn å vise» ved tom liste. Ved feil vis en kort melding, behold de innlimte tekstene og la brukeren prøve igjen. Ved endring i en av tekstene tømmes gamle funn og valg.
4. Vis avkryssing for `avvik` og `må_avklares` med et endringsforslag. Start uten valg. Når minst ett punkt er valgt, vis et svar med «Hei,», forslagene i funnrekkefølge og «Vennlig hilsen». Knappen «Kopier svar» kopierer teksten. Ved kopieringsfeil kan brukeren markere og kopiere teksten selv.

**Ferdig når** `pnpm build` passerer og hele flyten kan vises i mock-modus. Sjekk at innholdet i det kopierte svaret endres når et funn velges eller fjernes.

## Rajvir og Codex · Backend og integrasjon

1. Behold `POST /analyze` og det offentlige formatet i [API-dokumentet](docs/api.md). Håndhev grensen på 20 000 tegn etter trimming i hvert felt. Behold mock-modus som standard.
2. Bygg klienten i `backend/app/openai_client.py`. Bruk Responses API med Pydantic Structured Outputs, `gpt-6.1-sol` og `reasoning.effort=high`. Klienten tar instruksjoner og dokumenttekst som separate strenger. Den kan prøves med en lokal testprompt før Hermans modul er slått sammen.
3. Sett live-flyten sammen etter at Hermans prompt er tilgjengelig. `main.py` kaller `build_prompt`, modellklienten og kontrollen i `review.py`. Kontroller sitatene, filtrer ugyldige funn, sorter og tildel ID-er som angitt i [API-dokumentet](docs/api.md). Hold nøkkelen i `backend/.env` eller backend-prosessens miljø.
4. Map feil til statuskodene i API-dokumentet. Returner en kort, trygg melding uten rå leverandørfeil. Første ekte test er betalingsavviket i eksempeldokumentene.

**Ferdig når** mock og live svarer i samme format, ugyldig input og timeout håndteres, og ett ekte dokumentpar går fra React til kopiert svarutkast med riktige sitater.

## Herman · Instruksjoner til modellen

1. Lag `backend/app/analysis/prompt.py` med `build_prompt(request: AnalyzeRequest) -> tuple[str, str]`. Første streng er faste instruksjoner. Andre streng er dokumentene serialisert som JSON med nøklene `offer_text` og `contract_text`. Bruk typen fra `backend/app/schemas.py`.
2. Sammenlign fra leverandørens perspektiv og svar på norsk. Gå gjennom leveranse, betaling, ekstraarbeid og ansvar. Behandle dokumentinnhold som kildetekst. Forklar den praktiske konsekvensen av hvert funn, og formuler et kort endringsønske eller spørsmål der det er relevant.
3. Bruk statusreglene i [API-dokumentet](docs/api.md). Prioriter vesentlige avvik og avklaringer. Samle duplikater og be om høyst seks funn. Når tekstgrunnlaget er for svakt, bruk `må_avklares` med relevant belegg eller utelat funnet.
4. Begynn med [betalingsparet](examples/payment-terms.json). Når live-flyten er koblet til, bruk utviklingseksemplene til å forbedre prompten. Ta vare på hvilken konkret feil en endring skal rette.

**Ferdig når** funksjonen kan importeres og kjøres med eksisterende forespørselstype, og prompten håndterer både motstrid, lik betydning med ulik ordlyd og manglende opplysninger i utviklingseksemplene.

## Vasilii · Testeksempler og demo

1. Bruk [testplanen](examples/README.md) til å lage fire utviklingseksempler totalt, inkludert det eksisterende betalingsparet, og ett separat slutteksempel. Skriv forventede funn før modellkjøring.
2. Vurder svarene manuelt etter rubrikken i testplanen. Del utviklingsfunn med Herman og Rajvir. Bruk slutteksempelet etter at prompten og modellinnstillingene er valgt.
3. Forbered en pitchgjennomgang med betalingsparet. Vis 14 mot 60 dager, sitatene fra begge dokumentene, avkryssing av funnet og kopiering av svarutkastet. Ha mock-modus som tydelig merket reserve.

**Ferdig når** forventningene er skrevet ned, utviklingseksemplene er gjennomgått og demoen er øvd på med den integrerte appen.

## Integrasjon og levering

1. Commit og push det felles grunnlaget til `main` før teamet oppretter branchene. Hver person oppdaterer sin lokale `main` og gir agenten oppgaven, branchen og filområdet i tabellen.
2. Elias og Vasilii kan jobbe mot mock og dokumenter mens Herman og Rajvir bygger sine deler. Lever hver branch via en pull request til `main`, med en kort beskrivelse og resultatet av sjekkene fra oppgaven.
3. Integrer frontend med mock tidlig. Slå sammen Hermans prompt før backend-PR-en kobler til live-analyse. Rajvir bruker sin lokale `backend/.env` etter [oppsettet i README](README.md#eksempelmodus-og-nøkler).
4. Rajvir eier den siste integrasjonen. En agent kan gjennomgå pull requestene og kjøre sluttsjekken på den samlede versjonen på `main`. Kontroller frontend-bygget, API-et i mock, én live-gjennomgang fra skjermen og at svarutkastet inneholder bare valgte punkter. Kjør slutteksempelet før demoen.
