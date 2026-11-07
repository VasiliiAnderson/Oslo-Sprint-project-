"""Kjør testeksemplene gjennom prompten og modellen, og vis hva kontrollen gjør med funnene.

Bruk bare fiktive dokumenter. Funn og sitater skrives til terminalen.

Kjør fra backend/:
    python -m app.analysis.evaluate                 alle utviklingseksempler
    python -m app.analysis.evaluate --dry-run       uten modell og nøkkel
    python -m app.analysis.evaluate FIL.json        ett bestemt eksempel
    python -m app.analysis.evaluate --save UT.json  lagre resultatet for sammenligning

Slutteksempelet kjøres bare når det oppgis som fil, så det ikke brukes til å justere prompten.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from ..schemas import AnalyzeRequest
from .prompt import INSTRUCTIONS, build_prompt

BACKEND_DIR = Path(__file__).resolve().parents[2]
EXAMPLES = BACKEND_DIR.parent / "examples"
MAX_FINDINGS = 6

MANUAL_CHECKS = (
    "Vurder selv: Fant modellen de vesentlige avvikene? Varslet den feilaktig? "
    "Kan forslagene brukes uten å endre andre vilkår?"
)


def default_cases() -> list[Path]:
    return [EXAMPLES / "payment-terms.json", *sorted((EXAMPLES / "cases").glob("*.json"))]


def read_expected(case: Path) -> str | None:
    expected = case.with_suffix(".expected.md")
    return expected.read_text(encoding="utf-8").strip() if expected.exists() else None


def _normalize(text: str) -> str:
    return " ".join(text.split())


def quote_problems(candidate, request: AnalyzeRequest) -> list[str]:
    """Forklar hvilke sitater som ikke finnes i dokumentet de skal komme fra."""
    sources = (
        ("offer_quote", candidate.offer_quote, request.offer_text),
        ("contract_quote", candidate.contract_quote, request.contract_text),
    )
    return [
        f"{name} finnes ikke i dokumentet"
        for name, quote, document in sources
        if quote is not None and _normalize(quote) not in _normalize(document)
    ]


def evaluate_candidates(request: AnalyzeRequest, candidates: list, review_findings) -> dict:
    """Kontroller funnene samlet som backend gjør, og hvert for seg for å finne de forkastede."""
    rejected = [
        {
            **candidate.model_dump(),
            "reasons": quote_problems(candidate, request)
            or ["bryter status- eller sitatkravene i docs/api.md"],
        }
        for candidate in candidates
        if not review_findings(request, [candidate])
    ]
    findings = [finding.model_dump() for finding in review_findings(request, candidates)]
    warnings = []
    if len(candidates) > MAX_FINDINGS:
        warnings.append(f"Modellen ga {len(candidates)} funn, og backend kutter ved {MAX_FINDINGS}.")
    if candidates and not findings:
        warnings.append("Alle funn ble forkastet. Backend ville svart 502.")
    return {
        "model_findings": len(candidates),
        "findings": findings,
        "rejected": rejected,
        "warnings": warnings,
    }


def print_finding(finding: dict, heading: str) -> None:
    print(f"  {heading} {finding['status']} · {finding['category']}")
    fields = (
        ("Forklaring", "explanation"),
        ("Tilbud", "offer_quote"),
        ("Kontrakt", "contract_quote"),
        ("Forslag", "suggested_change"),
    )
    for label, key in fields:
        if finding[key] is not None:
            print(f"      {label}: {finding[key]}")


def print_result(result: dict) -> None:
    print(f"\n== {result['case']}")
    if result.get("error"):
        print(f"  FEIL: {result['error']}")
        return
    print(f"  Tegn: tilbud {result['offer_chars']}, kontrakt {result['contract_chars']}")
    if "findings" in result:
        print(
            f"  Modellen ga {result['model_findings']} funn: "
            f"{len(result['findings'])} beholdt, {len(result['rejected'])} forkastet"
        )
        for finding in result["findings"]:
            print_finding(finding, f"[{finding['id']}]")
        for finding in result["rejected"]:
            print_finding(finding, "FORKASTET")
            print(f"      Grunn: {'; '.join(finding['reasons'])}")
        for warning in result["warnings"]:
            print(f"  ADVARSEL: {warning}")
    expected = result["expected"]
    if expected is None:
        print("  Forventet: ingen .expected.md. Se tabellen i examples/README.md.")
    else:
        print("  Forventet:")
        for line in expected.splitlines():
            print(f"      {line}")


def load_live_flow():
    """Modellklienten og kontrollen kommer fra feat/backend."""
    try:
        from .. import openai_client, review
    except ImportError as error:
        sys.exit(
            f"Live-flyten er ikke tilgjengelig ({error}). "
            "Slå sammen feat/backend og installer requirements.txt, eller bruk --dry-run."
        )
    return openai_client, review


def run_case(case: Path, dry_run: bool, client, review) -> dict:
    result = {"case": case.stem, "expected": None}
    try:
        request = AnalyzeRequest.model_validate_json(case.read_text(encoding="utf-8"))
    except (OSError, ValueError, ValidationError) as error:
        # Pydantic-feil kan gjengi dokumenttekst, så bare typen vises.
        return {**result, "error": f"kunne ikke lese eksempelet ({type(error).__name__})"}

    result.update(
        expected=read_expected(case),
        offer_chars=len(request.offer_text),
        contract_chars=len(request.contract_text),
    )
    instructions, user_input = build_prompt(request)
    if dry_run:
        return result
    try:
        candidates = client.generate_findings(instructions, user_input)
    except client.ModelConfigurationError:
        sys.exit("Live-modus mangler gyldige modellinnstillinger. Sjekk backend/.env.")
    except client.ModelTimeout:
        return {**result, "error": "modellkallet overskred tidsgrensen"}
    except client.ModelResponseError:
        return {**result, "error": "modellen ga ikke et brukbart svar"}
    return {**result, **evaluate_candidates(request, candidates, review.review_findings)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kjør testeksemplene gjennom prompten.")
    parser.add_argument("cases", nargs="*", type=Path, help="eksempelfiler (standard: alle utviklingseksempler)")
    parser.add_argument("--dry-run", action="store_true", help="bygg prompten uten å kalle modellen")
    parser.add_argument("--save", type=Path, help="skriv resultatet til en JSON-fil")
    args = parser.parse_args(argv)

    load_dotenv(BACKEND_DIR / ".env")
    client, review = (None, None) if args.dry_run else load_live_flow()

    prompt_version = hashlib.sha256(INSTRUCTIONS.encode("utf-8")).hexdigest()[:8]
    model = None if args.dry_run else os.getenv("OPENAI_MODEL", "gpt-6.1-sol")
    print(f"Prompt {prompt_version} ({len(INSTRUCTIONS)} tegn), modell: {model or 'ingen (--dry-run)'}")

    results = []
    for case in args.cases or default_cases():
        results.append(run_case(case, args.dry_run, client, review))
        print_result(results[-1])

    has_errors = any(result.get("error") for result in results)
    has_rejected = any(result.get("rejected") for result in results)
    print(f"\n{len(results)} eksempler, feil: {'ja' if has_errors else 'nei'}, "
          f"forkastede funn: {'ja' if has_rejected else 'nei'}")
    if not args.dry_run:
        print(MANUAL_CHECKS)
    if args.save:
        args.save.write_text(
            json.dumps(
                {"prompt_version": prompt_version, "model": model, "results": results},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Lagret i {args.save}")
    return 1 if has_errors or has_rejected else 0


if __name__ == "__main__":
    # Modellsvar kan ha tegn som terminalen eller en omdirigert fil ikke kan skrive på Windows.
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main())
