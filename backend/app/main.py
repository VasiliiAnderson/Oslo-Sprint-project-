import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .openai_client import (
    ModelConfigurationError,
    ModelResponseError,
    ModelTimeout,
    generate_findings,
)
from .review import review_findings
from .schemas import AnalyzeRequest, AnalyzeResponse

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")
MOCK_RESPONSE = BACKEND_DIR.parent / "examples" / "mock-response.json"

app = FastAPI(title="Oslo Sprint – kontraktsstøtte")


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    mode = os.getenv("ANALYSIS_MODE", "mock")
    if mode == "mock":
        return AnalyzeResponse.model_validate_json(MOCK_RESPONSE.read_text(encoding="utf-8"))
    if mode != "live":
        raise HTTPException(503, "ANALYSIS_MODE må være mock eller live.")

    # Mock-modus kan brukes før promptmodulen er slått sammen.
    try:
        from .analysis.prompt import build_prompt
    except ModuleNotFoundError as error:
        if error.name != f"{__package__}.analysis.prompt":
            raise
        raise HTTPException(503, "Analyseprompten er ikke koblet til ennå.") from None

    instructions, user_input = build_prompt(request)
    try:
        candidates = generate_findings(instructions, user_input)
    except ModelConfigurationError:
        raise HTTPException(503, "Live-modus mangler gyldige modellinnstillinger.") from None
    except ModelTimeout:
        raise HTTPException(504, "Analysen tok for lang tid. Prøv igjen.") from None
    except ModelResponseError:
        raise HTTPException(502, "Modellen ga ikke et brukbart svar. Prøv igjen.") from None

    findings = review_findings(request, candidates)
    if candidates and not findings:
        raise HTTPException(502, "Funnene kunne ikke bekreftes i dokumentene. Prøv igjen.")
    return AnalyzeResponse(mode="live", findings=findings)
