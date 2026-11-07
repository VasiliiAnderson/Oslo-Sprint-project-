# Demoflyt: revisjonsparet med kontrakt først og chat

Dokumentpar: [unlimited-revisions.json](unlimited-revisions.json). Skrevet før modellkjøring. Kjøres med `python examples/run_flow.py`.

Flyten følger den nye planen. Kontrakten analyseres alene, så med tilbudet, og til slutt ber brukeren om et svarutkast i chatten.

## Steg 1: kontrakt alene (`offer_text: null`)

| Kategori | Status | `contract_quote` | Forslag |
| --- | --- | --- | --- |
| `ekstraarbeid` (eller `leveranse`) | `risiko` | `Kunden kan be om revisjoner inntil kunden er fornøyd med resultatet, uten ekstra kostnad.` (eller et sammenhengende utdrag) | Be om et fast antall inkluderte revisjonsrunder. |

- Alle funn har `offer_quote: null`.
- Ingen `avvik` eller `samsvarer`, siden det ikke finnes noe tilbud å sammenligne med.
- **Feilaktige varsler:** risiko på pris eller betalingsfrist (14 dager er ikke urimelig), eller funn om temaer kontrakten ikke nevner.

## Steg 2: kontrakt og tilbud

Samme forventning som i [unlimited-revisions.expected.md](unlimited-revisions.expected.md): `avvik` på revisjoner med sitat fra begge dokumenter og et forslag om å avgrense til to runder.

## Steg 3: oppfølging i chatten

Brukermelding: «Skriv et høflig svar der vi holder fast på to revisjonsrunder og spør hva ekstraarbeid skal koste.»

- `draft` er ikke `null`.
- Utkastet ber om **to revisjonsrunder**.
- Utkastet **spør** om pris for ekstraarbeid eller flere runder.
- Utkastet **inneholder ikke et beløp** (ingen «kr» eller tall som pris). Verken tilbudet eller kontrakten har en timepris for revisjoner, så en pris ville vært oppdiktet.
- Utkastet endrer ikke andre vilkår, som pris (24 000 kr) eller betalingsfrist.
- Alle `sources` finnes ordrett i riktig dokument.

## Regresjon

Betalingsparet skal fortsatt gi `avvik` på 14 mot 60 dager. Kjøres med `python examples/run_cases.py`.
