from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator

DocumentText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)
]


class AnalyzeRequest(BaseModel):
    contract_text: DocumentText
    offer_text: DocumentText | None = None

    @field_validator("offer_text", mode="before")
    @classmethod
    def blank_offer_is_missing(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class CandidateFinding(BaseModel):
    category: Literal["leveranse", "betaling", "ekstraarbeid", "ansvar"]
    status: Literal["samsvarer", "avvik", "risiko", "må_avklares"]
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


MessageText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
]
DraftText = Annotated[str, StringConstraints(max_length=4000)]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: MessageText


class ChatAttachment(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    text: DocumentText


class ChatContextRequest(BaseModel):
    attachments: list[ChatAttachment] = Field(max_length=2)
    messages: list[ChatMessage] = Field(max_length=6)


DocumentRole = Literal["contract", "offer", "unclear"]


class ChatContextResult(BaseModel):
    roles: list[DocumentRole]
    answer: str
    needs_contract: bool

    @field_validator("answer")
    @classmethod
    def validate_context_answer(cls, answer: str) -> str:
        answer = answer.strip()
        if not 1 <= len(answer) <= 2000:
            raise ValueError("Svaret må være mellom 1 og 2000 tegn.")
        return answer


class ChatContextResponse(ChatContextResult):
    mode: Literal["mock", "live"]


class FollowUpRequest(AnalyzeRequest):
    findings: list[Finding] = Field(max_length=6)
    messages: list[ChatMessage] = Field(min_length=1, max_length=6)
    current_draft: DraftText | None = None

    @field_validator("messages")
    @classmethod
    def last_message_is_from_user(cls, messages: list[ChatMessage]) -> list[ChatMessage]:
        if messages[-1].role != "user":
            raise ValueError("Siste melding må være fra brukeren.")
        return messages


class SourceQuote(BaseModel):
    document: Literal["offer", "contract"]
    quote: str


class FollowUpResult(BaseModel):
    answer: str
    sources: list[SourceQuote]
    draft: str | None

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, answer: str) -> str:
        answer = answer.strip()
        if not 1 <= len(answer) <= 2000:
            raise ValueError("Svaret må være mellom 1 og 2000 tegn.")
        return answer

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, sources: list[SourceQuote]) -> list[SourceQuote]:
        if len(sources) > 4:
            raise ValueError("Svaret kan ha opptil fire sitater.")
        return sources

    @field_validator("draft")
    @classmethod
    def validate_draft(cls, draft: str | None) -> str | None:
        if draft is None:
            return None
        draft = draft.strip()
        if not 1 <= len(draft) <= 4000:
            raise ValueError("Utkastet må være mellom 1 og 4000 tegn.")
        return draft


class FollowUpResponse(FollowUpResult):
    mode: Literal["mock", "live"]
