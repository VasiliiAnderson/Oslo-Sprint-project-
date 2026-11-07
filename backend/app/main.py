import os
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

from .openai_client import (
    ModelConfigurationError,
    ModelResponseError,
    ModelTimeout,
    generate_chat_context,
    generate_findings,
    generate_follow_up,
)
from .review import follow_up_findings_match, follow_up_sources_match, review_findings
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ChatContextRequest,
    ChatContextResponse,
    DocumentRole,
    FollowUpRequest,
    FollowUpResponse,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")
EXAMPLES_DIR = BACKEND_DIR.parent / "examples"
MockResponse = TypeVar("MockResponse", AnalyzeResponse, FollowUpResponse)
Result = TypeVar("Result")

app = FastAPI(title="Oslo Sprint – kontraktsstøtte")


def _mode() -> str:
    mode = os.getenv("ANALYSIS_MODE", "mock")
    if mode not in {"mock", "live"}:
        raise HTTPException(503, "ANALYSIS_MODE må være mock eller live.")
    return mode


def _read_example(filename: str, schema: type[MockResponse]) -> MockResponse:
    try:
        response = schema.model_validate_json((EXAMPLES_DIR / filename).read_bytes())
    except (OSError, ValidationError):
        raise HTTPException(503, "Eksempelsvaret er ikke tilgjengelig ennå.") from None
    if response.mode != "mock":
        raise HTTPException(503, "Eksempelsvaret må være merket som mock.")
    return response


def _analysis_example(request: AnalyzeRequest) -> str:
    if request.offer_text is None:
        return "mock-contract-response.json"
    revisions = EXAMPLES_DIR / "cases" / "unlimited-revisions.json"
    if revisions.is_file() and request == AnalyzeRequest.model_validate_json(revisions.read_bytes()):
        return "mock-revisions-response.json"
    return "mock-response.json"


def _run_live(
    prompt_name: str, request: BaseModel, generate: Callable[[str, str], Result]
) -> Result:
    try:
        prompt_module = import_module(".analysis.prompt", __package__)
    except ModuleNotFoundError as error:
        if error.name not in {f"{__package__}.analysis", f"{__package__}.analysis.prompt"}:
            raise
        raise HTTPException(503, "Prompten er ikke koblet til ennå.") from None
    build_prompt = getattr(prompt_module, prompt_name, None)
    if not callable(build_prompt):
        raise HTTPException(503, "Prompten er ikke koblet til ennå.")

    instructions, user_input = build_prompt(request)
    try:
        return generate(instructions, user_input)
    except ModelConfigurationError:
        raise HTTPException(503, "Live-modus mangler gyldige modellinnstillinger.") from None
    except ModelTimeout:
        raise HTTPException(504, "Modellen brukte for lang tid. Prøv igjen.") from None
    except ModelResponseError:
        raise HTTPException(502, "Modellen ga ikke et brukbart svar. Prøv igjen.") from None


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    if _mode() == "mock":
        return _read_example(_analysis_example(request), AnalyzeResponse)

    candidates = _run_live("build_prompt", request, generate_findings)
    findings = review_findings(request, candidates)
    if candidates and not findings:
        raise HTTPException(502, "Funnene kunne ikke bekreftes i dokumentene. Prøv igjen.")
    return AnalyzeResponse(mode="live", findings=findings)


@app.post("/follow-up")
def follow_up(request: FollowUpRequest) -> FollowUpResponse:
    if _mode() == "mock":
        return _read_example("mock-follow-up-response.json", FollowUpResponse)

    if not follow_up_findings_match(request):
        raise HTTPException(422, "Funnene passer ikke med dokumentene. Analyser dem på nytt.")

    result = _run_live("build_follow_up_prompt", request, generate_follow_up)
    if not follow_up_sources_match(request, result):
        raise HTTPException(502, "Sitatene kunne ikke bekreftes i dokumentene. Prøv igjen.")
    return FollowUpResponse(mode="live", **result.model_dump())


def _example_role(name: str, content: str) -> DocumentRole:
    label = name.casefold()
    opening = content[:160].casefold()
    if "tilbud" in label or opening.startswith("tilbud"):
        return "offer"
    if "kontrakt" in label or "contract" in label or opening.startswith(("oppdrag", "avtale", "kontrakt")):
        return "contract"
    return "unclear"


@app.post("/chat-context")
def chat_context(request: ChatContextRequest) -> ChatContextResponse:
    if _mode() == "mock":
        roles = [_example_role(file.name, file.text) for file in request.attachments]
        answer = "Legg ved kundens kontrakt eller lim inn et relevant utdrag, så ser jeg nærmere på det."
        if "unclear" in roles:
            file = request.attachments[roles.index("unclear")]
            answer = f"Er «{file.name}» kundens kontrakt eller tilbudet dere sendte?"
        return ChatContextResponse(mode="mock", roles=roles, answer=answer, needs_contract="contract" not in roles)

    result = _run_live("build_chat_context_prompt", request, generate_chat_context)
    if len(result.roles) != len(request.attachments):
        raise HTTPException(502, "Kunne ikke identifisere vedleggene. Prøv igjen.")
    return ChatContextResponse(mode="live", **result.model_dump())
