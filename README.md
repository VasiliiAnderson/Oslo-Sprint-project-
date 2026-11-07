# Oslo Sprint – kontraktsstøtte

En liten bedrift gjennomgår kundens kontrakt før signering, får funn med sitater og kan spørre om dem i chatten. Et tilbud kan legges til for å sammenligne vilkårene. Chatten kan lage og revidere utkast som kan kopieres.

## Lokal oppstart

Bruk Python 3.11+ og Node.js 22.12+ med pnpm 11. Kjør backend og frontend i hver sin terminal fra roten av repoet.

**Backend, PowerShell på Windows**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

På macOS/Linux er Python-stien `./.venv/bin/python`. FastAPI kjører på `http://127.0.0.1:8000`.

**Frontend**

```sh
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Åpne adressen Vite viser. Bruk det fiktive [revisjonsparet](examples/cases/unlimited-revisions.json) for å prøve demoflyten.

1. Åpne **Sjekk kontrakten**. Spør hva du bør se etter, eller bruk **Lim inn dokument** for å legge ved kontrakten. Trykk **Send**.
2. Legg til tilbudet i samme samtale. Se avviket fra to inkluderte runder.
3. Be chatten skrive et høflig svar som holder fast på to runder og spør hva ekstraarbeid skal koste. Be om en kortere versjon og velg **Kopier utkast**. Eksempelmodus viser et fast utkast.

## Eksempelmodus og nøkler

Eksempelmodus er standard og bruker faste, fiktive svar for analyse og chat. Hele laget kan kjøre den uten API-nøkkel. `backend/.env.example` er den delte malen med modellinnstillinger og tomt nøkkelfelt.

Rajvir kan opprette `backend/.env` fra malen med PowerShell fra repoets rot:

```powershell
if (-not (Test-Path -LiteralPath backend/.env)) {
    Copy-Item -LiteralPath backend/.env.example -Destination backend/.env
}
git check-ignore -v -- backend/.env
```

Fyll inn `OPENAI_API_KEY` lokalt og behold `OPENAI_MODEL=gpt-6.1-sol` og `OPENAI_REASONING_EFFORT=high`. Behold `ANALYSIS_MODE=mock` frem til modelltilkoblingen er klar. Sett deretter `ANALYSIS_MODE=live` og start FastAPI på nytt. `.gitignore` utelater den lokale filen fra Git. FastAPI leser den ved oppstart.

## Samarbeid

Start med [TASKS.md](TASKS.md). Der finner du oppgaven din, branchen, filområdet og ferdigkriteriene. Les også [arbeidsreglene](AGENTS.md), [API og grensesnitt](docs/api.md) og [testplanen](examples/README.md).

Når grunnoppsettet er delt på GitHub, oppdater `main` og opprett branchen for din oppgave. Her er frontend som eksempel:

```sh
git switch main
git pull --ff-only origin main
git switch -c feat/frontend
```

Push oppgavebranchen og åpne en pull request mot `main` når oppgaven er klar. Rajvir koordinerer integrasjonen.
