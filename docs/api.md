# API og grensesnitt for neste versjon

Dette er byggekontrakten for kontrakt først, valgfritt tilbud og oppfølgingschat. De offentlige feltene i dagens sammenligning beholdes.

## POST /analyze

JSON-feltet `contract_text` er påkrevd. `offer_text` er valgfritt og kan utelates, være `null` eller være blankt. Trim dokumenttekst, gjør blankt tilbud om til `null` og håndhev 1–20 000 tegn per dokument som faktisk er lagt inn. PDF-tekst hentes fortsatt ut i nettleseren og sendes som tekst.

Et vellykket svar er HTTP 200 med `mode` (`mock` eller `live`) og `findings`. Hvert funn følger dette formatet.

| Felt | Betydning |
| --- | --- |
| `id` | Unik streng i svaret, tildelt av backend. |
| `category` | `leveranse`, `betaling`, `ekstraarbeid` eller `ansvar`. |
| `status` | `risiko`, `må_avklares`, `avvik` eller `samsvarer`, etter reglene nedenfor. |
| `explanation` | Kort forklaring på norsk med praktisk konsekvens der det passer. |
| `offer_quote`, `contract_quote` | Ordrette utdrag fra riktig dokument, eller `null` når kilden mangler. |
| `suggested_change` | Kort spørsmål eller endringsønske, eller `null`. |

- **Kontrakt alene.** Bruk `risiko` for et konkret vilkår som kan koste leverandøren tid, penger eller rettigheter. Bruk `må_avklares` for et uklart vilkår eller noe teksten viser til, men som mangler. Begge krever et kontraktsitat. `offer_quote` er `null`.
- **Kontrakt med tilbud.** Behold dagens statusregler. `avvik` krever motstrid, sitat fra begge og et endringsforslag. `samsvarer` krever samme betydning og sitat fra begge, og har `suggested_change: null`. `må_avklares` krever minst ett relevant sitat.
- En tom funnliste er gyldig. Backend kontrollerer sitatene mot riktig dokument etter normalisering av blanktegn. Fjern ugyldige funn. Hvis modellen ga funn og alle forkastes, svar med `502`. Sorter `avvik`, `risiko`, `må_avklares`, `samsvarer` i den rekkefølgen. Behold modellens rekkefølge innen hver status. Returner opptil seks funn med ID-er `f1`, `f2` osv.

## POST /follow-up

Forespørselen bruker samme dokumentfelt som `/analyze` og tar i tillegg disse feltene.

| Felt | Betydning |
| --- | --- |
| `findings` | Listen fra siste analyse av dette dokumentgrunnlaget, med 0–6 funn i samme format. |
| `messages` | De siste 1–6 chatmeldingene, fra eldst til nyest. Hver har `role` (`user` eller `assistant`) og `content` (1–2 000 tegn etter trimming). Siste melding er fra brukeren. |
| `current_draft` | Gjeldende svarutkast, maksimalt 4 000 tegn, eller `null`. |

Svar med HTTP 200 og `mode`, `answer`, `sources` og `draft`. `answer` er en kort melding på norsk. `sources` har opptil fire sitater med `document` (`offer` eller `contract`) og `quote` (ordrett utdrag). `draft` er en foreslått melding til kunden, eller `null` hvis svaret bare forklarer eller stiller et spørsmål. React erstatter gjeldende utkast først når brukeren velger **Bruk i utkast**.

I live-modus kontrollerer backend sitatene i innsendte funn før modellkallet og gir `422` hvis de ikke passer dokumentgrunnlaget. Kontroller sitatene i modellens svar etterpå og gi `502` hvis et sitat ikke finnes i oppgitt dokument. Modellen skal underbygge påstander om dokumentene med sitater og markere usikkerhet når teksten ikke gir svar. Brukerens motforslag er et ønske fra brukeren. Det trenger ikke et sitat.

### Eksempel på oppfølging

Analyser først kontrakten fra [revisjonsparet](../examples/cases/unlimited-revisions.json) alene, med `offer_text: null`. Analyser igjen etter at tilbudet er lagt ved. En oppfølgingsforespørsel etter sammenligningen kan se slik ut.

```json
{
  "contract_text": "Kunden kan be om revisjoner inntil kunden er fornøyd med resultatet, uten ekstra kostnad.",
  "offer_text": "To revisjonsrunder er inkludert.",
  "findings": [
    {
      "id": "f1",
      "category": "ekstraarbeid",
      "status": "avvik",
      "explanation": "Kontrakten åpner for flere revisjoner enn tilbudet.",
      "offer_quote": "To revisjonsrunder er inkludert.",
      "contract_quote": "Kunden kan be om revisjoner inntil kunden er fornøyd med resultatet, uten ekstra kostnad.",
      "suggested_change": "Kan vi avgrense oppdraget til to revisjonsrunder?"
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "Skriv et høflig svar der vi holder på to runder og avklarer prisen for ekstraarbeid."
    }
  ],
  "current_draft": null
}
```

```json
{
  "mode": "live",
  "answer": "Her er et utkast som fastholder to inkluderte runder og ber om prisavklaring før ekstraarbeid.",
  "sources": [
    { "document": "offer", "quote": "To revisjonsrunder er inkludert." }
  ],
  "draft": "Hei! Kan vi presisere at to revisjonsrunder er inkludert, slik det står i tilbudet? Hvis det blir behov for flere runder, kan vi avtale prisen før ekstraarbeidet starter? Vennlig hilsen"
}
```

## Modus og feil

Mock er standard og merkes tydelig i UI. For kontrakt alene bruker `/analyze` det planlagte `examples/mock-contract-response.json`. For [revisjonsparet](../examples/cases/unlimited-revisions.json) med begge tekster bruker den `examples/mock-revisions-response.json`. Dagens [betalingsfixture](../examples/mock-response.json) forblir standard for andre forespørsler med to dokumenter. `/follow-up` bruker `examples/mock-follow-up-response.json`. Mock viser fiktive svar. Kildesjekken for modellens resultater kjøres i live-modus.

| Status | Når den brukes |
| --- | --- |
| `422` | Ugyldig JSON, manglende påkrevde felt, innhold over grensene eller funn i oppfølgingen som ikke passer dokumentene. |
| `503` | Ugyldig analysemodus, eller manglende promptmodul eller lokal modellkonfigurasjon i live. |
| `502` | Leverandørfeil, ufullstendig eller ugyldig modellsvar, eller tekstbelegg som ikke kan bekreftes. |
| `504` | Modellkallet overskrider tidsgrensen. |

Frontend kan vise `detail` hvis det er en kort tekst. Ved andre feilformer vis en generell melding og behold dokumenter, siste melding og godkjent utkast.

## FastAPI og promptmodul

Herman eier `backend/app/analysis/prompt.py`. Rajvir eier skjemaene, modellklienten og kontrollen i backend.

```python
def build_prompt(request: AnalyzeRequest) -> tuple[str, str]:
    """Returner (instructions, user_input) for analyse."""

def build_follow_up_prompt(request: FollowUpRequest) -> tuple[str, str]:
    """Returner (instructions, user_input) for oppfølging."""
```

Faste instruksjoner sendes separat. `user_input` er JSON med dokumentene og eventuelt oppfølgingsfeltene. Bruk ett strukturert modellkall per forespørsel med eksisterende Responses-klient og innstillinger. Analyseskjemaet er `findings` uten `id`. Oppfølgingsskjemaet er `answer`, `sources` og `draft` uten `mode`. Backend legger til ID-er og modus etter kontroll. Bruk lokal miljøkonfigurasjon for `gpt-6.1-sol` med `high`, 60 sekunders timeout, `store=False`, `max_output_tokens=8192` og `max_retries=0`. Hold nøkkel og dokumenttekst utenfor logger.
