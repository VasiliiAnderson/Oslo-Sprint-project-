"""Kjør testeksemplene mot POST /analyze og sjekk sitatene automatisk.

Bruk fra repoets rot mens backend kjører:

    python examples/run_cases.py            # utviklingseksemplene
    python examples/run_cases.py --final    # bare slutteksempelet
    python examples/run_cases.py --api http://127.0.0.1:8000

Svarene lagres i examples/results/<eksempel>.<modus>.json. Skriptet sjekker
sitater og statusregler fra docs/api.md. Om modellen fant de riktige funnene,
vurderer du manuelt mot .expected.md-filen og fører resultatet i evaluations.md.
Bruker bare standardbiblioteket.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent
RESULTS = EXAMPLES / "results"
DEV_CASES = [EXAMPLES / "payment-terms.json", *sorted((EXAMPLES / "cases").glob("*.json"))]
FINAL_CASES = sorted((EXAMPLES / "final").glob("*.json"))


def normalize(text: str) -> str:
    return " ".join(text.split())


def check_finding(finding: dict, offer: str, contract: str) -> list[str]:
    """Returner brudd på sitat- og statusreglene for ett funn."""
    problems = []
    status = finding.get("status")
    offer_quote = finding.get("offer_quote")
    contract_quote = finding.get("contract_quote")
    suggestion = finding.get("suggested_change")

    if offer_quote and normalize(offer_quote) not in normalize(offer):
        problems.append(f"offer_quote finnes ikke i tilbudet: «{offer_quote}»")
    if contract_quote and normalize(contract_quote) not in normalize(contract):
        problems.append(f"contract_quote finnes ikke i kontrakten: «{contract_quote}»")

    if status == "avvik":
        if not (offer_quote and contract_quote):
            problems.append("avvik mangler sitat fra begge dokumenter")
        if not suggestion:
            problems.append("avvik mangler endringsforslag")
    elif status == "må_avklares":
        if not (offer_quote or contract_quote):
            problems.append("må_avklares mangler sitat")
    elif status == "samsvarer":
        if not (offer_quote and contract_quote):
            problems.append("samsvarer mangler sitat fra begge dokumenter")
        if suggestion:
            problems.append("samsvarer skal ha suggested_change: null")
    else:
        problems.append(f"ukjent status: {status}")
    return problems


def post(api: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        f"{api.rstrip('/')}/analyze",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, {"detail": body[:200]}


def run_case(api: str, path: Path) -> bool:
    payload = json.loads(path.read_text(encoding="utf-8"))
    name = path.stem
    print(f"\n== {name} ==")
    try:
        status_code, body = post(api, payload)
    except urllib.error.URLError as error:
        print(f"  Fikk ikke kontakt med {api}: {error.reason}")
        return False

    if status_code != 200:
        print(f"  HTTP {status_code}: {body.get('detail')}")
        return False

    mode = body.get("mode", "ukjent")
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{name}.{mode}.json"
    out.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    findings = body.get("findings", [])
    print(f"  Modus: {mode} · {len(findings)} funn · lagret i {out.relative_to(EXAMPLES.parent)}")
    if mode == "mock":
        print("  Merk: mock gir alltid samme eksempelsvar, så sitatsjekken sier lite her.")

    ok = True
    for finding in findings:
        problems = check_finding(finding, payload["offer_text"], payload["contract_text"])
        mark = "OK " if not problems else "FEIL"
        print(f"  [{mark}] {finding.get('id')} {finding.get('category')}/{finding.get('status')}: "
              f"{finding.get('explanation')}")
        for problem in problems:
            print(f"         - {problem}")
        ok = ok and not problems
    print(f"  Sammenlign med {path.with_suffix('').name}.expected.md")
    return ok


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # æøå i Windows-terminalen
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="Adressen til FastAPI")
    parser.add_argument("--final", action="store_true", help="Kjør bare slutteksempelet")
    args = parser.parse_args()

    cases = FINAL_CASES if args.final else DEV_CASES
    results = [run_case(args.api, path) for path in cases]
    print(f"\nAutomatisk sjekk bestått for {sum(results)} av {len(results)} eksempler.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
