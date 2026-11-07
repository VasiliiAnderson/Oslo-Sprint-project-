import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .schemas import AnalyzeRequest, AnalyzeResponse

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")
MOCK_RESPONSE = BACKEND_DIR.parent / "examples" / "mock-response.json"

app = FastAPI(title="Oslo Sprint – kontraktsstøtte")


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    mode = os.getenv("ANALYSIS_MODE", "mock")
    if mode == "live":
        raise HTTPException(503, "Ekte analyse er ikke koblet til ennå.")
    if mode != "mock":
        raise HTTPException(503, "ANALYSIS_MODE må være mock eller live.")
    return AnalyzeResponse.model_validate_json(MOCK_RESPONSE.read_text(encoding="utf-8"))
