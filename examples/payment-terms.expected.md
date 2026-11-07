# Betaling 14 mot 60 dager

Dokumentpar: [payment-terms.json](payment-terms.json). Hoveddemo. Skrevet før modellkjøring.

Leveransen og revisjonsrundene er like. Bare betalingsfristen skiller seg.

## Forventede hovedfunn

| Kategori | Status | `offer_quote` | `contract_quote` | Forslag |
| --- | --- | --- | --- | --- |
| `betaling` | `avvik` | `Betaling innen 14 dager etter faktura.` | `Betaling innen 60 dager etter faktura.` | Be om 14 dager etter faktura, slik det står i tilbudet. |

Forklaringen bør nevne at kunden får 46 dager lengre frist, og at det gir leverandøren dårligere likviditet.

## Akseptable tilleggsfunn

- `samsvarer` på `leveranse` eller `ekstraarbeid` for «én landingsside med to revisjonsrunder», med sitat fra begge og `suggested_change: null`.

## Feilaktige varsler

- `avvik` eller `må_avklares` på leveranse eller revisjonsrunder.
- Funn om ansvar, opphavsrett eller andre temaer ingen av dokumentene nevner.
- Et forslag som endrer noe annet enn betalingsfristen, for eksempel pris eller omfang.
