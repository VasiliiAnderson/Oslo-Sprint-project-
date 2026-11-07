# Betaling 14 dager mot to uker

Dokumentpar: [same-meaning-payment.json](same-meaning-payment.json). Skrevet før modellkjøring.

Vilkårene er like, men med ulik ordlyd. Begge fristene regnes fra fakturadato. Testen sjekker at modellen ikke varsler om avvik når betydningen er den samme.

## Forventede hovedfunn

Ingen `avvik` og ingen `må_avklares`. En tom liste er bestått.

## Akseptable tilleggsfunn

| Kategori | Status | `offer_quote` | `contract_quote` |
| --- | --- | --- | --- |
| `betaling` | `samsvarer` | `Betaling innen 14 dager etter fakturadato.` | `Fakturaen forfaller til betaling to uker etter fakturadato.` |
| `ekstraarbeid` eller `leveranse` | `samsvarer` | `Inntil to revisjonsrunder er inkludert.` | `To revisjonsrunder inngår i prisen.` |
| `betaling` | `samsvarer` | `Prisen er 38 000 kr eks. mva.` | `Vederlaget er 38 000 kr eks. mva.` |

Alle `samsvarer`-funn skal ha `suggested_change: null`.

## Feilaktige varsler

- `avvik` på betaling for «14 dager» mot «to uker». Dette er den viktigste feilen testen ser etter.
- `avvik` på «Inntil to» mot «To» revisjonsrunder.
- `må_avklares` om ansvar, opphavsrett eller annet som ingen av dokumentene nevner.
