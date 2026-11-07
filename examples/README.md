# Testeksempler og demo

[payment-terms.json](payment-terms.json) er det første fiktive dokumentparet og hoveddemoen. Forvent ett avvik på betaling med riktige sitater for 14 og 60 dager. Leveransen og de to revisjonsrundene samsvarer. [mock-response.json](mock-response.json) er felles eksempelsvar til appen.

Vasilii lager fire utviklingseksempler totalt og ett slutteksempel. Bruk samme JSON-felter som i betalingsparet. Legg nye utviklingseksempler under `cases/` med én `.json`-fil og en `.expected.md` med samme navn for hvert par. Skriv forventede funn, hvilken status de skal ha, relevante sitater og hva som vil være et feilaktig varsel. Hold slutteksempelet separat frem til prompten er valgt.

| Eksempel | Filer | Forventet |
| --- | --- | --- |
| Betaling innen 14 mot 60 dager | [json](payment-terms.json) · [forventet](payment-terms.expected.md) | `avvik` på betaling, med sitat fra begge dokumenter og et forslag om 14 dager. |
| Betaling innen 14 dager mot to uker fra samme tidspunkt | [json](cases/same-meaning-payment.json) · [forventet](cases/same-meaning-payment.expected.md) | Ingen feilaktig melding om betalingsavvik. |
| To revisjonsrunder mot ubegrensede revisjoner | [json](cases/unlimited-revisions.json) · [forventet](cases/unlimited-revisions.expected.md) | `avvik` på ekstraarbeid eller leveranse. Foreslå å avgrense revisjonsrundene. |
| Tilbudet har betaling for ekstraarbeid, kontrakten omtaler det ikke | [json](cases/extra-work-missing.json) · [forventet](cases/extra-work-missing.expected.md) | `må_avklares` med sitat fra tilbudet og et spørsmål om betaling for ekstraarbeid. |
| Slutteksempel med forskjellig ansvarstak | [json](final/liability-cap.json) · [forventet](final/liability-cap.expected.md) | `avvik` på ansvar, med riktige beløp og sitater. |

Slutteksempelet ligger i `final/`. Det skal ikke brukes til å justere prompten.

## Kjøring og vurdering

Start backend som beskrevet i [README](../README.md), og kjør fra repoets rot:

```sh
python examples/run_cases.py           # de fire utviklingseksemplene
python examples/run_cases.py --final   # slutteksempelet, når prompten er valgt
```

Skriptet lagrer svarene i `results/` og sjekker sitater og statusregler automatisk. Hovedfunn, feilvarsler og forslag vurderer du manuelt mot `.expected.md`, og resultatet føres i [vurderingsloggen](evaluations.md). Manuset til pitchen står i [demo.md](demo.md).

For hvert svar registrerer du fire sjekker. Fant modellen de vesentlige avvikene? Varslet den feilaktig? Stemmer alle sitatene med kilden? Kan forslagene brukes uten at de endrer andre vilkår? Et eksempel er bestått når de forventede hovedfunnene er med, det ikke er vesentlige feilvarsler, sitatene stemmer og forslagene følger intensjonen.

Øv pitchen på betalingsparet. Vis innliming, analyse, sitater fra begge dokumenter, valg av funn og kopiert svarutkast. Kjør ekte analyse på Rajvirs maskin. Eksempelmodus er en merket reserve.
