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
| 2026-11-07 | payment-terms | `64ff4fa`, gpt-6.1-sol high | Ja: `avvik` betaling, 14 mot 60 | Nei | OK | Ja, ber om 14 dager | Ja | + `samsvarer` leveranse (akseptabelt) |
| 2026-11-07 | same-meaning-payment | `64ff4fa`, gpt-6.1-sol high | Ja: ingen avvik | Nei, «to uker» = 14 dager | OK | – (ingen) | Ja | 4 × `samsvarer`. Mange, se under |
| 2026-11-07 | unlimited-revisions | `64ff4fa`, gpt-6.1-sol high | Ja: `avvik` ekstraarbeid | Nei | OK | Ja, avgrense til to runder, ingen oppdiktet pris | Ja | + 3 × `samsvarer` |
| 2026-11-07 | extra-work-missing | `64ff4fa`, gpt-6.1-sol high | Ja: `må_avklares`, `contract_quote: null` | Nei | OK | Ja, ber om å ta inn 1 100 kr/t | Ja | + 4 × `samsvarer`. Mange, se under |

**Observasjon til Herman (2026-11-07):** Alle fire består. Modellen tar med `samsvarer` for nesten alle vilkår (opptil 4 av 5 funn), selv om prompten sier at det bare skal gjelde sentrale vilkår. Det er ikke feil, men det gjør listen lengre for brukeren. Vurder å stramme inn hvis dere vil ha kortere svar.

## Slutteksempel

Kjøres én gang etter at prompt og modellinnstillinger er valgt: `python examples/run_cases.py --final`.

| Dato | Eksempel | Prompt/commit | Hovedfunn | Feilvarsel | Sitater | Forslag | Bestått | Notat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | liability-cap | | | | | | | |
