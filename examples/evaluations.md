# Vurderingslogg

Én rad per kjøring. Kjør `python examples/run_cases.py` i live-modus og sammenlign svaret i `results/` med `.expected.md`-filen. Del funn som krever endring med Herman (prompt) og Rajvir (backend), og noter hvilken konkret feil en endring skal rette.

Sjekkene fra [testplanen](README.md):

1. **Hovedfunn:** Fant modellen de vesentlige avvikene?
2. **Feilvarsel:** Varslet den feilaktig?
3. **Sitater:** Stemmer alle sitatene med kilden? Skriptet sjekker dette automatisk.
4. **Forslag:** Kan forslagene brukes uten at de endrer andre vilkår?

Eksempelet er bestått når hovedfunnene er med, det ikke er vesentlige feilvarsler, sitatene stemmer og forslagene følger intensjonen.

| Dato | Eksempel | Prompt/commit | Hovedfunn | Feilvarsel | Sitater | Forslag | Bestått | Notat / sendt til |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | payment-terms | | | | | | | |
| | same-meaning-payment | | | | | | | |
| | unlimited-revisions | | | | | | | |
| | extra-work-missing | | | | | | | |

## Slutteksempel

Kjøres én gang etter at prompt og modellinnstillinger er valgt: `python examples/run_cases.py --final`.

| Dato | Eksempel | Prompt/commit | Hovedfunn | Feilvarsel | Sitater | Forslag | Bestått | Notat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | liability-cap | | | | | | | |
