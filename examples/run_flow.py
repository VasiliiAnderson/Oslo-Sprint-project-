"""Kjør demoflyten med revisjonsparet: kontrakt alene, kontrakt med tilbud og oppfølging i chat.

Bruk fra repoets rot mens backend kjører:

    python examples/run_flow.py
    python examples/run_flow.py --api http://127.0.0.1:8000

Svarene lagres i examples/results/flow-<steg>.<modus>.json. Skriptet sjekker
sitater, statusregler og de automatiske kravene til utkastet i
cases/unlimited-revisions.flow.expected.md. Bruker bare standardbiblioteket.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from run_cases import RESULTS, check_finding, normalize, post

EXAMPLES = Path(__file__).resolve().parent
PAIR = EXAMPLES / "cases" / "unlimited-revisions.json"
QUESTION = "Skriv et høflig svar der vi holder fast på to revisjonsrunder og spør hva ekstraarbeid skal koste."


def save(name: str, body: dict) -> None:
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"flow-{name}.{body.get('mode', 'ukjent')}.json"
    out.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def report(label: str, problems: list[str]) -> bool:
    print(f"  [{'OK ' if not problems else 'FEIL'}] {label}")
    for problem in problems:
        print(f"         - {problem}")
    return not problems


def analyze(api: str, name: str, payload: dict, contract_only: bool) -> tuple[bool, list]:
    print(f"\n== {name} ==")
    status_code, body = post(api, payload, "/analyze")
    if status_code != 200:
        print(f"  HTTP {status_code}: {body.get('detail')}")
        return False, []
    save(name, body)
    findings = body.get("findings", [])
    print(f"  Modus: {body.get('mode')} · {len(findings)} funn")
    ok = True
    for f in findings:
        problems = check_finding(f, payload.get("offer_text") or "", payload["contract_text"])
        if contract_only and f.get("status") in {"avvik", "samsvarer"}:
            problems.append(f"{f.get('status')} krever tilbud, men bare kontrakten ble sendt")
        if contract_only and f.get("offer_quote"):
            problems.append("offer_quote skal være null uten tilbud")
        ok = report(f"{f.get('id')} {f.get('category')}/{f.get('status')}: {f.get('explanation')}", problems) and ok
        if f.get("suggested_change"):
            print(f"         forslag: {f['suggested_change']}")
    return ok, findings


def follow_up(api: str, pair: dict, findings: list) -> bool:
    print("\n== oppfølging ==")
    payload = {
        **pair,
        "findings": findings,
        "messages": [{"role": "user", "content": QUESTION}],
        "current_draft": None,
    }
    status_code, body = post(api, payload, "/follow-up")
    if status_code != 200:
        print(f"  HTTP {status_code}: {body.get('detail')}")
        return False
    save("follow-up", body)
    print(f"  Modus: {body.get('mode')}")
    print(f"  Svar: {body.get('answer')}")

    problems = []
    docs = {"offer": pair["offer_text"], "contract": pair["contract_text"]}
    for source in body.get("sources", []):
        doc = docs.get(source.get("document"))
        if doc is None or normalize(source.get("quote", "")) not in normalize(doc):
            problems.append(f"sitat finnes ikke i {source.get('document')}: «{source.get('quote')}»")

    draft = body.get("draft")
    if not draft:
        problems.append("draft mangler")
    else:
        text = draft.lower()
        if not re.search(r"\b(to|2)\s+(revisjons)?runder", text):
            problems.append("utkastet nevner ikke to revisjonsrunder")
        if "?" not in draft:
            problems.append("utkastet stiller ikke noe spørsmål")
        if re.search(r"\d[\d\s.]*\s*(kr|kroner|,-)|kr\.?\s*\d", text):
            problems.append("utkastet inneholder et beløp (mulig oppdiktet pris)")
    ok = report("kilder og utkast", problems)
    if draft:
        print("  --- Utkast ---")
        for line in draft.splitlines():
            print(f"  | {line}")
    return ok


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="Adressen til FastAPI")
    args = parser.parse_args()

    pair = json.loads(PAIR.read_text(encoding="utf-8"))
    ok1, _ = analyze(args.api, "kontrakt-alene", {"contract_text": pair["contract_text"], "offer_text": None}, True)
    ok2, findings = analyze(args.api, "med-tilbud", pair, False)
    ok3 = follow_up(args.api, pair, findings) if ok2 else False

    results = [ok1, ok2, ok3]
    print(f"\nAutomatisk sjekk bestått for {sum(results)} av 3 steg. "
          "Vurder resten manuelt mot cases/unlimited-revisions.flow.expected.md.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
