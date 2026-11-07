# Ekstraarbeid i tilbudet, ikke i kontrakten

Dokumentpar: [extra-work-missing.json](extra-work-missing.json). Skrevet før modellkjøring.

Tilbudet sier at arbeid utover omfanget faktureres med 1 100 kr per time. Kontrakten nevner ikke ekstraarbeid. Omfang, pris, leveringstid og betaling er like.

## Forventede hovedfunn

| Kategori | Status | `offer_quote` | `contract_quote` | Forslag |
| --- | --- | --- | --- | --- |
| `ekstraarbeid` | `må_avklares` | `Arbeid utover avtalt omfang faktureres med 1 100 kr per time etter skriftlig avtale.` | `null` | Spør om timeprisen på 1 100 kr for arbeid utover omfanget kan tas inn i kontrakten. |

Forklaringen bør si at kontrakten ikke nevner betaling for ekstraarbeid i den innlimte teksten, og at leverandøren risikerer å gjøre ekstra arbeid uten betaling.

## Akseptable tilleggsfunn

- `samsvarer` på `leveranse` for 30 produkter eller levering innen 10 virkedager.
- `samsvarer` på `betaling` for fast pris eller betalingsfrist.

## Feilaktige varsler

- `avvik` på ekstraarbeid. Kontrakten sier ikke noe annet, den sier ingenting, så riktig status er `må_avklares`.
- Et `contract_quote` som later som kontrakten omtaler ekstraarbeid.
- `avvik` på pris, omfang, leveringstid eller betalingsfrist.
