# Arbeidsplan for ContractPilot

Målgruppen er små tjenestebedrifter som skal ta stilling til en kundekontrakt før signering. Brukeren legger inn kontrakten, får viktige funn med tekstbelegg og kan spørre om funnene i chatten. Et tilbud kan legges til for å sammenligne vilkårene. Brukeren velger selv om et foreslått svar skal brukes i utkastet.

Les [README](README.md), [arbeidsreglene](AGENTS.md) og [API-formatet](docs/api.md). Dette er planen for neste versjon. Appen på `main` har allerede sammenligning av to dokumenter og støtte for innlimt tekst og PDF. Start de nye branchene fra den delte plancommiten på `main`.

| Eier | Oppgave | Branch | Filområde |
| --- | --- | --- | --- |
| Elias | Dokumentfelt, chat og svarutkast | `feat/contract-chat-ui` | `frontend/` |
| Rajvir med Codex | API, modellklient, kontroll og integrasjon | `feat/contract-chat-api` | `backend/app/main.py`, `schemas.py`, `openai_client.py`, `review.py` |
| Herman | Instruksjoner for gjennomgang og oppfølging | `feat/contract-chat-prompt` | `backend/app/analysis/` |
| Vasilii | Eksempelsvar, tester og demo | `feat/contract-chat-demo` | `examples/` |

## Elias · Frontend

1. Sett **Kundens kontrakt** først. **Tilbud (valgfritt)** kan stå tomt. Bruk eksisterende felt og PDF-opplasting. Et gyldig kontraktfelt er nok til å kjøre analysen. Send `offer_text: null` når tilbudsfeltet er tomt.
2. Vis funnene med status, forklaring og sitater. Støtt den nye statusen `risiko`. Behold avkryssing for funn med endringsforslag, og behold dagens lokale svarutkast som utgangspunkt.
3. Vis chatten etter en vellykket analyse, også ved tom funnliste. Legg inn ett meldingsfelt med **Send** og korte startspørsmål som «Forklar et vilkår» og «Hjelp meg å svare». Send dokumentene, funnene, de siste meldingene og gjeldende utkast til `POST /follow-up`. Bruk samme Vite-proxy som for `/analyze`.
4. Vis svaret og eventuelle sitater i chatten. Når assistenten foreslår et utkast, vis **Bruk i utkast**. Først ved klikk blir teksten gjeldende svarutkast. Det godkjente utkastet blir stående når brukeren krysser av flere funn, og kan erstattes av et nytt godkjent utkast. Behold **Kopier svar**. Ved feil skal brukeren kunne prøve igjen med meldingen og det godkjente utkastet intakt.
5. Når brukeren endrer eller legger til et dokument, tøm funn, chat og utkast. Kjør ny analyse før chatten åpnes for det nye dokumentgrunnlaget. Hindre at et svar fra en tidligere forespørsel vises etter at dokumentene er byttet.

**Ferdig når** `pnpm build` passerer og brukeren kan gå fra kontrakt alene til sammenligning, oppfølgingsspørsmål, **Bruk i utkast** og **Kopier svar**. Bygg mot [JSON-eksemplene](docs/api.md#eksempel-på-oppfølging) mens backend utvikles.

## Rajvir og Codex · Backend og integrasjon

1. Utvid `POST /analyze` slik at kontrakt er påkrevd og tilbud kan utelates. Behold det eksisterende svaret for to dokumenter og oppdater kontrollen av status og tekstbelegg for kontrakt alene.
2. Legg til `POST /follow-up` etter [API-formatet](docs/api.md). Valider dokumentene og størrelsene på funn, meldinger og utkast. Kontroller sitater fra både innsendte funn og modellens oppfølgingssvar mot riktig dokument.
3. Bruk samme Responses-klient, modell, lokale nøkkel og feilhåndtering. Koble inn Hermans promptfunksjoner. Begge endepunktene skal kunne brukes i tydelig merket mock-modus uten API-nøkkel.

**Ferdig når** kontrakt alene, to dokumenter og oppfølging fungerer i både mock og live, og et gammelt forespørselspar fortsatt gir riktig svarformat.

## Herman · Instruksjoner til modellen

1. Oppdater `build_prompt` for to situasjoner. Med kontrakt alene forklarer modellen konkrete vilkår, risiko og det som bør avklares. Med tilbud sammenligner den også dokumentene. Bruk de avtalte statusreglene og be om korte, ordrette sitater.
2. Lag `build_follow_up_prompt` for spørsmål om det aktive oppdraget. Bruk dokumentene som kilde, og bruk chatten og gjeldende utkast til å forstå hva brukeren vil. Når brukeren ber om et utkast, skriv en melding til kunden og bevar øvrige valg i gjeldende utkast. Skill brukerens ønskede vilkår fra dem som står i dokumentene.
3. Prøv instruksjonene på revisjonsparet og det eksisterende betalingsparet. Bruk testene til å rette konkrete feil i sitater, status eller hva utkastet ber om.

**Ferdig når** promptene gir dokumentbaserte svar i begge analysemodusene, og en oppfølging kan endre formuleringen uten å miste valgte vilkår.

## Vasilii · Testeksempler og demo

1. Bruk [revisjonsparet](examples/cases/unlimited-revisions.json) til å lage to analyseeksempler og ett eksempelsvar for chat. Legg dem i `examples/mock-contract-response.json`, `examples/mock-revisions-response.json` og `examples/mock-follow-up-response.json` etter API-spesifikasjonen.
2. Sjekk samme flyt i live-modus. Kontrakten alene viser risikoen ved ubegrensede revisjoner. Med tilbudet skal appen vise avviket fra to runder. Be deretter om et høflig svar som fastholder to runder og spør hva ekstraarbeid skal koste. Sjekk at utkastet inneholder begge ønskene uten å dikte opp en pris.
3. Kjør betalingsparet som regresjonssjekk og behold det separate slutteksempelet. Oppdater [demomanuset](examples/demo.md) når flyten er testet. Ha eksempelmodus som reserve.

**Ferdig når** hele demoflyten er gjennomgått, og funn, sitater og kopiert utkast stemmer med forventningene.

## Rekkefølge

Frontend, prompt og eksempelsvar kan lages parallelt mot API-formatet. Rajvir kobler først sammen API-et og mock-svarene, deretter modellen og promptene. Teamet tester hele revisjonstilfellet i live før forsiden og pitchen strammes inn. Lever oppgavebranchene via PR mot `main` med hva som er testet.
