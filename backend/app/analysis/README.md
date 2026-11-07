# Instruksjoner til modellen

Herman eier denne mappen. Implementer `prompt.py` med `build_prompt(request: AnalyzeRequest) -> tuple[str, str]` som beskrevet i [API og grensesnitt](../../../docs/api.md). Se [oppgaven](../../../TASKS.md) og [testeksemplene](../../../examples/README.md).

Returner de faste instruksjonene og dokumentene som separate strenger. Rajvir eier modellkallet, kontroll av tekstbelegg og HTTP-feilhåndtering.

## Prøv prompten på testeksemplene

Kjør fra `backend/` etter at `feat/backend` er slått sammen. Dette kaller modellen og krever gyldig `backend/.env`:

```sh
python -m app.analysis.evaluate
python -m app.analysis.evaluate --save resultat.json
```

Skriptet kjører betalingsparet og alt i `examples/cases/`. Det viser funn som er beholdt, funn kontrollen forkaster og hvorfor, og innholdet i `.expected.md`. Vesentlige funn, feilvarsler og forslag vurderes manuelt etter [testplanen](../../../examples/README.md). Utskriften viser promptversjonen, så kjøringer kan sammenlignes. `--dry-run` sjekker at eksemplene kan leses, uten modell eller nøkkel.

Slutteksempelet kjøres bare når det oppgis som fil. Bruk fiktive dokumenter, og ikke commit resultatfiler.
