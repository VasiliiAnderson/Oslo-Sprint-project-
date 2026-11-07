# API og grensesnitt

## React → FastAPI

`POST /analyze` tar JSON med `offer_text` og `contract_text`. Begge er påkrevde strenger, trimmes og skal ha 1–20 000 tegn etter trimming. Send [dokumentparet](../examples/payment-terms.json) direkte som forespørsel.

Et vellykket svar er HTTP 200 med `mode` (`mock` eller `live`) og `findings`. [Eksempelsvaret](../examples/mock-response.json) er felles format for begge moduser. Feltnavn og statusverdier er faste.

| Felt i et funn | Betydning |
| --- | --- |
| `id` | Unik streng i svaret, tildelt av backend. Brukes til å velge funn. |
| `category` | `leveranse`, `betaling`, `ekstraarbeid` eller `ansvar`. |
| `status` | `avvik`, `må_avklares` eller `samsvarer`. Status beskriver dokumentene. |
| `explanation` | Kort forklaring på norsk, med praktisk konsekvens der det passer. |
| `offer_quote`, `contract_quote` | Utdrag fra riktig dokument. Bruk `null` når det mangler relevant tekst fra den kilden. |
| `suggested_change` | Et kort spørsmål eller endringsønske. `null` når funnet ikke krever oppfølging. |

### Status og tekstbelegg

- `avvik` betyr at dokumentene sier forskjellige ting om samme vilkår. Krever sitat fra begge og et konkret endringsforslag.
- `må_avklares` betyr at et relevant vilkår er uklart eller mangler. Krever minst ett sitat som begrunner avklaringen. Gi et spørsmål til kunden der det er mulig.
- `samsvarer` betyr at vilkårene har samme betydning. Krever sitat fra begge. Endringsforslaget er `null`.
- En tom `findings`-liste er gyldig. React bygger svarutkastet fra de valgte avvikene og avklaringene som har endringsforslag.

### Modus og feil

Mock er standard og returnerer [det faste eksempelsvaret](../examples/mock-response.json). Frontend merker resultatet som et eksempel. Live-modus skal bruke dokumentene fra forespørselen. Skjelettet gir foreløpig HTTP 503 i live-modus frem til modellklienten er på plass.

| Status | Når den brukes |
| --- | --- |
| `422` | Manglende, tomme eller for lange dokumentfelt, eller ugyldig JSON. |
| `503` | Live-modus er valgt uten gyldig lokal konfigurasjon. |
| `502` | Feil fra modellleverandør, manglende eller ufullstendig strukturert svar, eller alle funn forkastet i kontrollen. |
| `504` | Modellkallet overskrider tidsgrensen. |

Frontend kan vise `detail` når den er en kort tekst. Ved andre feilformer vis en generell melding og behold dokumentfeltene.

## FastAPI → prompt → modell → kontroll

Herman leverer `backend/app/analysis/prompt.py`. Grensesnittet er:

```python
def build_prompt(request: AnalyzeRequest) -> tuple[str, str]:
    """Returner (instructions, user_input)."""
```

`instructions` er faste oppgaveinstruksjoner. `user_input` er JSON med `offer_text` og `contract_text`. Analysemodulen bruker forespørselstypen fra `app.schemas`. Rajvir eier klienten, kontrollen og HTTP-feilhåndteringen.

Modellklienten tar de to strengene og gjør ett kall med OpenAI Python SDK `responses.parse` og Pydantic. Modellens skjema har en `findings`-liste med de offentlige funnfeltene uten `id`. Send `instructions` og `input` separat. Bruk `model=gpt-6.1-sol`, `reasoning={"effort": "high"}`, `store=False` og `max_output_tokens=8192`. Sett klientens timeout til 60 sekunder og `max_retries=0`. Bruk lokal miljøkonfigurasjon. [Modell og innstillinger](https://developers.openai.com/api/docs/models/gpt-6.1-sol) · [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

I live-modus sjekker backend hvert sitat mot riktig dokument. Trim og normaliser blanktegn ved sammenligning. Fjern funn som bryter status- eller sitatkravene. Hvis modellen returnerte funn og alle forkastes, svar med `502`. Behold modellens rekkefølge innenfor hver status, sorter `avvik` før `må_avklares` før `samsvarer`, og returner høyst seks funn med ID-er `f1`, `f2` osv. Logg eventuelt status og request-ID. Hold nøkkel og dokumenttekst utenfor logger.
