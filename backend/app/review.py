from .schemas import AnalyzeRequest, CandidateFinding, Finding

STATUS_PRIORITY = {"avvik": 0, "må_avklares": 1, "samsvarer": 2}


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _quote_matches(quote: str | None, document: str) -> bool:
    if quote is None:
        return True
    normalized = _normalize(quote)
    return bool(normalized) and normalized in document


def _has_evidence(
    candidate: CandidateFinding, offer: str, contract: str
) -> bool:
    if not candidate.explanation.strip():
        return False
    if not _quote_matches(candidate.offer_quote, offer):
        return False
    if not _quote_matches(candidate.contract_quote, contract):
        return False

    has_offer = candidate.offer_quote is not None
    has_contract = candidate.contract_quote is not None
    change = candidate.suggested_change
    if change is not None and not change.strip():
        return False
    if candidate.status == "må_avklares":
        return has_offer or has_contract
    if candidate.status == "avvik":
        return has_offer and has_contract and change is not None
    return has_offer and has_contract and change is None


def review_findings(
    request: AnalyzeRequest, candidates: list[CandidateFinding]
) -> list[Finding]:
    offer = _normalize(request.offer_text)
    contract = _normalize(request.contract_text)
    supported = [
        candidate for candidate in candidates if _has_evidence(candidate, offer, contract)
    ]
    supported.sort(key=lambda finding: STATUS_PRIORITY[finding.status])
    return [
        Finding(id=f"f{index}", **candidate.model_dump())
        for index, candidate in enumerate(supported[:6], start=1)
    ]
