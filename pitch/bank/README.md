# Eksempelbank

Eksempler å hente fra til pitch, demo og tester. Hver mappe har en ferdig slide (`slide.html`), tekstene til verktøyet (`case.json`) og en `README.md` med manus, kilder og forbehold.

Alle kontraktstekster er fiktive. Sakene i `nyheter/` er ekte og har lenke til kilden.

## Eksempler (fiktive kontrakter)

| Mappe | Tittel | Status |
|---|---|---|
| [00-moms](eksempler/00-moms/) | Samme beløp. Ett ord endret. | Fra testdata, ikke kjørt live |
| [01-betalingsfrist-120-dager](eksempler/01-betalingsfrist-120-dager/) | Du blir kundens bank i fire måneder. | Nytt testpar, ikke kjørt live |
| [02-ansvar](eksempler/02-ansvar/) | Et oppdrag til 120 000 kr. En risiko på en million. | Testet live 7. nov 2026 |
| [03-rettigheter](eksempler/03-rettigheter/) | Kunden eier logoen før de har betalt for den. | Fra testdata, ikke kjørt live |
| [04-avtalepart](eksempler/04-avtalepart/) | Du jobber for et selskap du aldri sjekket. | Fra testdata, ikke kjørt live |
| [05-revisjoner](eksempler/05-revisjoner/) | «Til kunden er fornøyd» har ingen slutt. | Testet live 7. nov 2026 |
| [06-godkjenning](eksempler/06-godkjenning/) | Når er jobben ferdig? Når kunden sier det. | Fra testdata, ikke kjørt live |
| [07-ingen-falsk-alarm](eksempler/07-ingen-falsk-alarm/) | Ulike ord. Samme vilkår. Ingen alarm. | Testet live 7. nov 2026 |

## Nyheter (ekte saker + fiktiv kontrakt)

| Mappe | Tittel | Kilde |
|---|---|---|
| [01-serneke-konkurs](nyheter/01-serneke-konkurs/) | Han leverte stålet. Nå vil konkursboet ha pengene tilbake. | SVT 11.12.2025 · Företagarna 14.01.2026 |
| [02-storselskaper-80-dager](nyheter/02-storselskaper-80-dager/) | Små leverandører blir bank for de store. | Företagaren 16.12.2025 · tall fra Bolagsverket |
| [03-traton-90-dager](nyheter/03-traton-90-dager/) | Lovet 30 dager. Betaler etter 90. | Realtid 07.10.2024 · etter Dagens Industri |
| [04-smvdanmark-purring](nyheter/04-smvdanmark-purring/) | 2,8 timer i uka på å jage egne penger. | SMVdanmark via Ritzau 01.11.2026 |
| [05-eu-domstolen-120-dager](nyheter/05-eu-domstolen-120-dager/) | 120 dager i standardvilkårene holdt ikke i retten. | EU-domstolen C-677/22 · 06.02.2025 |

## Samlet visning

- `../examples.html`: alle eksemplene som én presentasjon.
- `../news.html`: alle nyhetssakene som én presentasjon.

## Før du bruker et eksempel

- Bare eksemplene merket «Testet live» er kjørt mot modellen. Kjør `case.json` gjennom verktøyet før du demoer de andre.
- Svenske og danske tall er ikke norske tall. Si hvor de kommer fra.
- Lovhenvisningene er informasjon, ikke juridisk rådgivning.
