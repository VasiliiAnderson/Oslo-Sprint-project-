# Slutteksempel: ulikt ansvarstak

Dokumentpar: [liability-cap.json](liability-cap.json). Skrevet før modellkjøring.

**Ikke bruk dette eksempelet til å justere prompten.** Kjør det først når prompten og modellinnstillingene er valgt.

Tilbudet begrenser leverandørens samlede ansvar til 120 000 kr. Kontrakten setter taket til 1 000 000 kr per skadetilfelle. Pris og betaling er like.

## Forventede hovedfunn

| Kategori | Status | `offer_quote` | `contract_quote` | Forslag |
| --- | --- | --- | --- | --- |
| `ansvar` | `avvik` | `Leverandørens samlede ansvar etter oppdraget er begrenset til 120 000 kr.` | `Leverandørens erstatningsansvar er begrenset til 1 000 000 kr per skadetilfelle.` | Be om at ansvaret begrenses til 120 000 kr samlet, slik det står i tilbudet. |

Forklaringen må ha riktige beløp (120 000 kr og 1 000 000 kr). Den bør også nevne at kontraktens tak gjelder per skadetilfelle, mens tilbudets tak er samlet, så den reelle forskjellen kan bli større.

## Akseptable tilleggsfunn

- `samsvarer` på `betaling` for pris eller betalingsfrist.

## Feilaktige varsler

- Feil beløp i forklaring eller forslag, for eksempel 100 000 eller 10 000 000.
- `avvik` på pris eller betalingsfrist.
- Påstand om at taket er ulovlig eller uvanlig.
