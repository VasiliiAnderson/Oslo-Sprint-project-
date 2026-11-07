from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints

DocumentText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)
]


class AnalyzeRequest(BaseModel):
    offer_text: DocumentText
    contract_text: DocumentText


class CandidateFinding(BaseModel):
    category: Literal["leveranse", "betaling", "ekstraarbeid", "ansvar"]
    status: Literal["samsvarer", "avvik", "må_avklares"]
    explanation: str
    offer_quote: str | None
    contract_quote: str | None
    suggested_change: str | None


class ModelFindings(BaseModel):
    findings: list[CandidateFinding]


class Finding(CandidateFinding):
    id: str


class AnalyzeResponse(BaseModel):
    mode: Literal["mock", "live"]
    findings: list[Finding]
