# Offer–contract test data (design freelancers and small agencies)

Synthetic test data for the hackathon contract tool. Each pair is an **offer** (tilbud) a supplier sent and the **contract** (oppdragsavtale) the client sent back. Some contracts quietly differ from the offer. The tool should find those differences and ignore everything else.

All companies, people and organisation numbers are fictional.

## Contents

```
data/
  dev/<pair_id>/    offer.txt, contract.txt, expected.json   29 pairs: build and tune prompts here
  test/<pair_id>/   same files                               18 pairs: run once at the end, don't tune on these
  index.csv         one row per pair: split, language, base case, clean or not, planted differences
generate_pairs.py   the script that made the data (python generate_pairs.py --seed 7 gives a new set)
```

| | Pairs | Clean pairs | Expected findings |
|---|---|---|---|
| dev | 29 | 7 | 29 |
| test | 18 | 4 | 15 |
| **total** | **47** (39 Norwegian, 8 English) | **11** | **44** |

There are five base cases: a visual identity, a website design and a campaign in Norwegian, plus a brand identity and a pitch deck in English. Every one of the 12 difference types appears at least once in the test split.

## expected.json

- `offer_fields` / `contract_fields`: the correct normalised values for each document. Use these to **score extraction** field by field.
- `expected_findings`: the differences the tool should report. Use these to **score the comparison**. Each finding has:
  - `field`, `kind` (`differs` or `missing`), `severity` (`high`, `medium`, or `review` for liability)
  - `offer_value`, `contract_value`
  - `offer_quote`, `contract_quote`: exact text from the documents (checked to appear word for word; `null` when the contract term is missing)
  - `explanation`: a reference explanation, useful for an LLM judge
- `is_clean: true` means there should be **zero** findings, so any finding on these pairs is a false alarm.

## Planted difference types

| Mutation | What changes in the contract | Severity |
|---|---|---|
| `payment_days` | Payment deadline 45 or 60 days instead of 14–30 | high |
| `price_vat` | Same amount, but "incl. VAT" instead of "excl. VAT" (about 20% less) | high |
| `revisions_unlimited` | Revisions "until the client is satisfied" | high |
| `revisions_missing` | Revision limit removed entirely | medium |
| `extra_absorbed` | Extra work included in the fixed price | high |
| `extra_missing` | Extra-work clause removed entirely | high |
| `extra_rate` | Hourly rate about 30% lower | medium |
| `delivery_earlier` | Deadline 2–3 weeks earlier | medium |
| `acceptance` | Automatic acceptance replaced by written confirmation with no deadline | medium |
| `ip_on_signing` | All rights, including sketches, transfer on signing instead of after payment | high |
| `liability_uncapped` | Unlimited liability including indirect loss | review |
| `party_entity` | Contract names a different company in the client's group | medium |

## Built-in traps

- **Same meaning, different wording.** Clean contracts rephrase every term, use different number styles ("85 000" vs "85.000", "to" vs "2") and different date formats ("15. januar 2027" vs "15.01.2027"). A tool that matches text instead of meaning will raise false alarms.
- **Neutral extra clauses.** Contracts always contain confidentiality and governing-law clauses the offer never mentioned. These are normal and should **not** be reported.
- **Missing terms.** For the two `missing` types there's nothing to quote in the contract. The tool must notice the absence.

## Suggested scoring

- **Extraction:** share of fields where the extracted value equals `contract_fields` / `offer_fields`.
- **Detection:** share of `expected_findings` the tool reports, matched on `field`.
- **False alarms:** number of reported findings that aren't in `expected_findings`, with the clean pairs reported separately.
- **Quotes:** every quote the tool gives must appear word for word in the document.

## Limits

The data is generated from templates, so wording varies less than in real contracts. Before the demo, have someone read a sample, and add a few real anonymised pairs if possible. Don't present results on this data as proof the tool works on real contracts. Present them as "tested on 47 constructed cases with known answers."
