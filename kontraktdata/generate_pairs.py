"""
Generate synthetic offer-contract pairs for a design freelancer / small agency.

Every pair has:
  offer.txt      - the offer (tilbud) the supplier sent
  contract.txt   - the contract (oppdragsavtale) the client sent back
  expected.json  - ground truth: normalised fields for both documents
                   (for scoring extraction) and the expected findings
                   (for scoring the comparison)

Run:  python generate_pairs.py            -> writes ./data
      python generate_pairs.py --seed 7   -> a different but reproducible set

All companies, people and organisation numbers are fictional.
"""

import argparse
import csv
import json
import random
import shutil
from datetime import date, timedelta
from pathlib import Path

# --------------------------------------------------------------------------
# Base cases: offer and contract agree on everything in a clean pair
# --------------------------------------------------------------------------

BASES = [
    dict(id="no-identitet", lang="no",
         supplier="Fjordlys Design AS", supplier_org="998 214 337", supplier_contact="Ingrid Haugen",
         client="Nordkaffe AS", client_org="997 503 118", client_contact="Thomas Berg",
         client_alt="Nordkaffe Holding AS", client_alt_org="996 881 402",
         project="Ny visuell identitet for Nordkaffe",
         description="Utvikling av ny visuell identitet for Nordkaffes kaffebarer og nettbutikk.",
         deliverables=["Logo i tre varianter (primær, sekundær og ikon)", "Fargepalett og typografi",
                       "Designmanual (PDF, ca. 20 sider)", "Maler for visittkort og brevark"],
         price=85000, payment_days=14, revisions=2, rate=1150, acceptance_days=10,
         offer_date=date(2026, 10, 12), contract_date=date(2026, 10, 26), delivery=date(2027, 1, 15)),
    dict(id="no-nettside", lang="no",
         supplier="Studio Bølge Kari Nilsen", supplier_org="923 456 781", supplier_contact="Kari Nilsen",
         client="Tindvik Sykkel AS", client_org="915 220 674", client_contact="Jonas Aas",
         client_alt="Tindvik Gruppen AS", client_alt_org="912 008 345",
         project="Design av ny nettside for Tindvik Sykkel",
         description="Design av ny nettside med fokus på mobilvisning og nettbutikk.",
         deliverables=["Designskisser for forside og seks undersider", "Mobil- og desktopversjon",
                       "Klikkbar prototype i Figma", "Komponentbibliotek for utviklere"],
         price=64000, payment_days=20, revisions=3, rate=950, acceptance_days=7,
         offer_date=date(2026, 9, 2), contract_date=date(2026, 9, 14), delivery=date(2026, 11, 30)),
    dict(id="no-kampanje", lang="no",
         supplier="Maren Lund Grafisk", supplier_org="926 771 090", supplier_contact="Maren Lund",
         client="Havsalt Restaurantgruppe AS", client_org="919 334 852", client_contact="Sofie Dahl",
         client_alt="Havsalt Eiendom AS", client_alt_org="918 662 113",
         project="Vårkampanje 2027 for Havsalt",
         description="Kampanjemateriell til vårkampanjen i gruppens fire restauranter.",
         deliverables=["Tre plakatdesign (A2 og A4)", "Tolv maler for sosiale medier",
                       "Ny sesongmeny (to sider)", "Trykkeklare filer"],
         price=38500, payment_days=30, revisions=2, rate=850, acceptance_days=5,
         offer_date=date(2027, 1, 8), contract_date=date(2027, 1, 20), delivery=date(2027, 3, 1)),
    dict(id="en-brand", lang="en",
         supplier="Northlight Studio AS", supplier_org="924 118 506", supplier_contact="Erik Solberg",
         client="Brightwater Outdoor Ltd", client_org="UK 10482231", client_contact="Hannah Price",
         client_alt="Brightwater Holdings Ltd", client_alt_org="UK 09113874",
         project="Brand identity for Brightwater Outdoor",
         description="Design of a new brand identity for Brightwater's Nordic product line.",
         deliverables=["Logo in three versions", "Colour palette and typography",
                       "Brand guidelines (PDF, approx. 20 pages)", "Packaging label template"],
         price=92000, payment_days=14, revisions=2, rate=1200, acceptance_days=10,
         offer_date=date(2026, 10, 5), contract_date=date(2026, 10, 19), delivery=date(2027, 1, 22)),
    dict(id="en-deck", lang="en",
         supplier="Kvist Creative AS", supplier_org="927 330 214", supplier_contact="Lena Kvist",
         client="Polar Analytics GmbH", client_org="HRB 228734", client_contact="Markus Weber",
         client_alt="Polar Group GmbH", client_alt_org="HRB 201156",
         project="Investor pitch deck for Polar Analytics",
         description="Design of an investor pitch deck and a matching one-page summary.",
         deliverables=["Pitch deck of up to 20 slides", "Editable PowerPoint template",
                       "One-page summary (PDF)", "Icon set of 15 icons"],
         price=45000, payment_days=14, revisions=3, rate=1100, acceptance_days=5,
         offer_date=date(2026, 11, 2), contract_date=date(2026, 11, 9), delivery=date(2026, 12, 11)),
]

MUTATIONS = ["payment_days", "price_vat", "revisions_unlimited", "revisions_missing",
             "extra_absorbed", "extra_missing", "extra_rate", "delivery_earlier",
             "acceptance", "ip_on_signing", "liability_uncapped", "party_entity"]

# --------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------

NO_MONTHS = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august",
             "september", "oktober", "november", "desember"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
NO_NUM = {1: "én", 2: "to", 3: "tre", 4: "fire"}
EN_NUM = {1: "one", 2: "two", 3: "three", 4: "four"}


def d_long(d, lang):
    return f"{d.day}. {NO_MONTHS[d.month-1]} {d.year}" if lang == "no" else f"{d.day} {EN_MONTHS[d.month-1]} {d.year}"


def d_num(d, lang):
    return d.strftime("%d.%m.%Y") if lang == "no" else d.strftime("%d/%m/%Y")


def nok(x, style=0, lang="no"):
    s = f"{x:,}"
    if style == 0:
        return s.replace(",", " ")
    return s.replace(",", ".") if lang == "no" else s


def num_word(n, lang, cap=False):
    w = (NO_NUM if lang == "no" else EN_NUM).get(n, str(n))
    return w.capitalize() if cap else w


# --------------------------------------------------------------------------
# Text pieces. Each function returns a sentence (or None if section removed).
# Offer and clean-contract phrasings are written to mean exactly the same.
# --------------------------------------------------------------------------

T = {
 "no": dict(
  offer_title="TILBUD",
  contract_title="OPPDRAGSAVTALE",
  offer_intro=lambda b: f"Fra: {b['supplier']} (org.nr. {b['supplier_org']}), v/ {b['supplier_contact']}\n"
                        f"Til: {b['client']} (org.nr. {b['client_org']}), att. {b['client_contact']}\n"
                        f"Dato: {d_long(b['offer_date'], 'no')}\nTilbudet gjelder i 30 dager.",
  offer_close=lambda b: f"Øvrige vilkår avtales i egen oppdragsavtale.\n\nMed vennlig hilsen\n{b['supplier_contact']}\n{b['supplier']}",
  h=dict(parties="Parter", scope="Oppdraget", price="Pris", revisions="Revisjoner", extra="Tilleggsarbeid",
         delivery="Levering", acceptance="Godkjenning", payment="Betaling", ip="Rettigheter",
         liability="Ansvar", conf="Taushetsplikt", law="Lovvalg og tvister"),
  c_scope_head=lambda b: f"Avtalen gjelder {b['description'][0].lower() + b['description'][1:]} Oppdraget omfatter:",
  o_scope_head=lambda b: f"{b['description']} Oppdraget omfatter:",
  c_parties=lambda b, name, org: (f"Oppdragsgiver: {name}, org.nr. {org}", f"Leverandør: {b['supplier']}, org.nr. {b['supplier_org']}"),
  o_price=["Fast pris for oppdraget er kr {p} eks. mva.", "Totalpris: kr {p},- eksklusive mva."],
  c_price=["Avtalt vederlag er NOK {p} eksklusive merverdiavgift.", "Oppdragsgiver betaler et fast vederlag på kr {p} eks. mva."],
  c_price_vat=["Avtalt vederlag er NOK {p} inkludert merverdiavgift.", "Oppdragsgiver betaler et fast vederlag på kr {p} inkl. mva."],
  o_rev=["Prisen inkluderer {n} revisjonsrunder. Ytterligere revisjoner faktureres som tilleggsarbeid.",
         "Inntil {nw} runder med revisjoner er inkludert i prisen. Flere runder faktureres som tilleggsarbeid."],
  c_rev=["{NW} revisjonsrunder er inkludert i vederlaget. Ytterligere revisjoner faktureres som tilleggsarbeid.",
         "Vederlaget dekker inntil {n} revisjonsrunder. Revisjoner utover dette faktureres som tilleggsarbeid."],
  c_rev_unl="Leverandøren skal gjennomføre revisjoner inntil Oppdragsgiver er tilfreds med resultatet.",
  o_extra=["Arbeid utover beskrevet omfang faktureres med kr {r} per time eks. mva., og utføres kun etter skriftlig godkjenning fra Oppdragsgiver.",
           "Tilleggsarbeid avtales skriftlig på forhånd og faktureres etter medgått tid à kr {r} per time eks. mva."],
  c_extra=["Endringer eller tillegg til oppdraget skal avtales skriftlig før arbeidet starter, og faktureres med kr {r} per time eks. mva.",
           "Arbeid som ikke omfattes av punkt 2, utføres bare etter skriftlig avtale og faktureres etter medgått tid med kr {r} per time eks. mva."],
  c_extra_abs="Mindre endringer og tillegg i omfang som Oppdragsgiver ber om underveis, inngår i det faste vederlaget.",
  o_deliv=["Ferdig leveranse innen {dl}.", "Vi leverer endelig materiale senest {dl}."],
  c_deliv=["Leveransen skal være ferdigstilt senest {dl}.", "Endelig leveranse skal skje innen {dn}."],
  o_acc=["Leveransen anses godkjent dersom Oppdragsgiver ikke har meldt skriftlige innsigelser innen {k} dager etter levering."],
  c_acc=["Har Oppdragsgiver ikke gitt skriftlig melding om mangler innen {k} dager etter levering, anses leveransen som godkjent.",
         "Leveransen regnes som godkjent {k} dager etter levering, med mindre Oppdragsgiver innen da har reklamert skriftlig."],
  c_acc_mut="Leveransen er først godkjent når Oppdragsgiver har bekreftet dette skriftlig.",
  o_pay=["Fakturering skjer ved levering. Betalingsbetingelser: {d} dager netto fra fakturadato.",
         "Fakturering skjer ved levering. Faktura forfaller til betaling {d} dager etter fakturadato."],
  c_pay=["Leverandøren fakturerer ved levering. Faktura betales innen {d} dager fra fakturadato.",
         "Leverandøren fakturerer ved levering. Oppdragsgiver betaler fakturaen senest {d} dager etter fakturadato."],
  o_ip=["Rettighetene til det endelige materialet overføres til Oppdragsgiver når fullt vederlag er betalt. Skisser og forkastede forslag forblir Leverandørens eiendom."],
  c_ip=["Når vederlaget er betalt i sin helhet, overtar Oppdragsgiver rettighetene til det endelige materialet. Skisser og forkastede forslag tilhører fortsatt Leverandøren.",
        "Oppdragsgiver får rettighetene til det endelige materialet når hele vederlaget er betalt. Leverandøren beholder rettighetene til skisser og forslag som ikke ble valgt."],
  c_ip_mut="Alle rettigheter til materiale utarbeidet under oppdraget, inkludert skisser og forkastede forslag, overføres til Oppdragsgiver ved signering av denne avtalen.",
  o_liab=["Leverandørens samlede ansvar under oppdraget er begrenset til oppdragets verdi."],
  c_liab=["Leverandørens samlede erstatningsansvar er begrenset til det avtalte vederlaget.",
          "Leverandørens ansvar etter denne avtalen kan ikke overstige avtalt vederlag."],
  c_liab_mut="Leverandøren er ansvarlig for ethvert direkte og indirekte tap Oppdragsgiver måtte lide som følge av leveransen, uten beløpsbegrensning.",
  c_conf="Partene skal behandle opplysninger om hverandres virksomhet konfidensielt, også etter at oppdraget er avsluttet.",
  c_law="Avtalen er underlagt norsk rett. Tvister skal søkes løst ved forhandlinger, og ellers med Oslo tingrett som verneting.",
  c_sign=lambda b, name: f"Sted og dato: Oslo, {d_long(b['contract_date'], 'no')}\n\nFor Oppdragsgiver: ____________________ ({name})\nFor Leverandør: ____________________ ({b['supplier']})",
  c_ref=lambda b: f"Avtalen bygger på tilbud datert {d_num(b['offer_date'], 'no')}.",
 ),
 "en": dict(
  offer_title="QUOTE",
  contract_title="SERVICES AGREEMENT",
  offer_intro=lambda b: f"From: {b['supplier']} (org. no. {b['supplier_org']}), attn. {b['supplier_contact']}\n"
                        f"To: {b['client']} (reg. no. {b['client_org']}), attn. {b['client_contact']}\n"
                        f"Date: {d_long(b['offer_date'], 'en')}\nThis quote is valid for 30 days.",
  offer_close=lambda b: f"Other terms will be set out in a separate services agreement.\n\nKind regards\n{b['supplier_contact']}\n{b['supplier']}",
  h=dict(parties="Parties", scope="Scope", price="Price", revisions="Revisions", extra="Additional work",
         delivery="Delivery", acceptance="Acceptance", payment="Payment", ip="Intellectual property",
         liability="Liability", conf="Confidentiality", law="Governing law and disputes"),
  c_scope_head=lambda b: f"This agreement covers the {b['description'][0].lower() + b['description'][1:]} The work includes:",
  o_scope_head=lambda b: f"{b['description']} The work includes:",
  c_parties=lambda b, name, org: (f"Client: {name}, reg. no. {org}", f"Supplier: {b['supplier']}, org. no. {b['supplier_org']}"),
  o_price=["The fixed price for the project is NOK {p} excluding VAT.", "Total price: NOK {p} excl. VAT."],
  c_price=["The agreed fee is NOK {p}, exclusive of VAT.", "The Client shall pay a fixed fee of NOK {p} excl. VAT."],
  c_price_vat=["The agreed fee is NOK {p}, inclusive of VAT.", "The Client shall pay a fixed fee of NOK {p} incl. VAT."],
  o_rev=["The price includes {n} rounds of revisions. Further revisions are invoiced as additional work.",
         "Up to {nw} rounds of revisions are included in the price. Additional rounds are invoiced as additional work."],
  c_rev=["{NW} rounds of revisions are included in the fee. Further revisions are invoiced as additional work.",
         "The fee covers up to {n} rounds of revisions. Revisions beyond this are invoiced as additional work."],
  c_rev_unl="The Supplier shall carry out revisions until the Client is satisfied with the result.",
  o_extra=["Work outside the described scope is invoiced at NOK {r} per hour excl. VAT, and is only carried out with the Client's written approval.",
           "Additional work is agreed in writing in advance and invoiced on a time basis at NOK {r} per hour excl. VAT."],
  c_extra=["Changes or additions to the work shall be agreed in writing before work starts, and are invoiced at NOK {r} per hour excl. VAT.",
           "Work not covered by clause 2 is only carried out under a written agreement and invoiced on a time basis at NOK {r} per hour excl. VAT."],
  c_extra_abs="Minor changes and additions to the scope requested by the Client during the project are included in the fixed fee.",
  o_deliv=["Final delivery by {dl}.", "We will deliver the final material no later than {dl}."],
  c_deliv=["The deliverables shall be completed no later than {dl}.", "Final delivery shall take place by {dn}."],
  o_acc=["The delivery is deemed accepted if the Client has not raised written objections within {k} days of delivery."],
  c_acc=["If the Client has not notified any defects in writing within {k} days of delivery, the delivery is deemed accepted.",
         "The delivery is considered accepted {k} days after delivery unless the Client has raised a written complaint before then."],
  c_acc_mut="The delivery is only accepted once the Client has confirmed acceptance in writing.",
  o_pay=["Invoicing on delivery. Payment terms: {d} days net from the invoice date.",
         "Invoicing on delivery. Invoices are due for payment {d} days after the invoice date."],
  c_pay=["The Supplier invoices on delivery. Invoices shall be paid within {d} days of the invoice date.",
         "The Supplier invoices on delivery. The Client shall pay the invoice no later than {d} days after the invoice date."],
  o_ip=["The rights to the final material are transferred to the Client once the full fee has been paid. Sketches and rejected proposals remain the Supplier's property."],
  c_ip=["Once the fee has been paid in full, the Client acquires the rights to the final material. Sketches and rejected proposals remain with the Supplier.",
        "The Client receives the rights to the final material when the full fee has been paid. The Supplier retains the rights to sketches and proposals that were not selected."],
  c_ip_mut="All rights to material produced under this agreement, including sketches and rejected proposals, are transferred to the Client on signing of this agreement.",
  o_liab=["The Supplier's total liability for the project is limited to the value of the project."],
  c_liab=["The Supplier's total liability is limited to the agreed fee.",
          "The Supplier's liability under this agreement shall not exceed the agreed fee."],
  c_liab_mut="The Supplier is liable for any direct and indirect loss suffered by the Client as a result of the deliverables, without any financial limit.",
  c_conf="The parties shall keep information about each other's business confidential, also after the project has ended.",
  c_law="This agreement is governed by Norwegian law. Disputes shall be resolved through negotiation, failing which Oslo District Court shall be the agreed venue.",
  c_sign=lambda b, name: f"Place and date: Oslo, {d_long(b['contract_date'], 'en')}\n\nFor the Client: ____________________ ({name})\nFor the Supplier: ____________________ ({b['supplier']})",
  c_ref=lambda b: f"This agreement is based on the quote dated {d_num(b['offer_date'], 'en')}.",
 ),
}

# Ideal explanations of each finding (useful as reference for an LLM judge)
EXPLAIN = {
 "no": {
  "payment_days": "Kontrakten gir kunden {c} dagers betalingsfrist, mot {o} dager i tilbudet. Du får pengene senere enn avtalt.",
  "price_vat": "Kontrakten sier at prisen er inkludert mva., mens tilbudet var eks. mva. Du får dermed rundt 20 % mindre betalt.",
  "revisions_unlimited": "Tilbudet begrenset revisjoner til {o} runder, men kontrakten krever revisjoner til kunden er fornøyd, uten øvre grense.",
  "revisions_missing": "Tilbudet begrenset revisjoner til {o} runder, men kontrakten sier ingenting om antall revisjoner.",
  "extra_absorbed": "Tilbudet fakturerte tilleggsarbeid per time, men kontrakten sier at endringer og tillegg inngår i fastprisen.",
  "extra_missing": "Kontrakten mangler regler for tilleggsarbeid. Tilbudet sa at slikt arbeid faktureres per time etter skriftlig godkjenning.",
  "extra_rate": "Timeprisen for tilleggsarbeid er kr {c} i kontrakten, mot kr {o} i tilbudet.",
  "delivery_earlier": "Leveransefristen i kontrakten er {c}, tidligere enn {o} i tilbudet.",
  "acceptance": "Tilbudet hadde automatisk godkjenning etter {o} dager. Kontrakten krever skriftlig godkjenning uten frist, så kunden kan utsette godkjenningen.",
  "ip_on_signing": "Kontrakten overfører alle rettigheter, også skisser og forkastede forslag, ved signering. Tilbudet overførte bare endelig materiale, og først etter full betaling.",
  "liability_uncapped": "Kontrakten gir ubegrenset ansvar, også for indirekte tap. Tilbudet begrenset ansvaret til oppdragets verdi. Bør vurderes nærmere.",
  "party_entity": "Kontrakten er med {c}, ikke {o} som tilbudet gjaldt. Sjekk hvem du faktisk kan kreve betaling fra.",
 },
 "en": {
  "payment_days": "The contract gives the client {c} days to pay, compared with {o} days in the quote. You get paid later than agreed.",
  "price_vat": "The contract says the fee includes VAT, while the quote was excluding VAT. You would be paid about 20% less.",
  "revisions_unlimited": "The quote limited revisions to {o} rounds, but the contract requires revisions until the client is satisfied, with no limit.",
  "revisions_missing": "The quote limited revisions to {o} rounds, but the contract says nothing about the number of revisions.",
  "extra_absorbed": "The quote charged additional work by the hour, but the contract includes changes and additions in the fixed fee.",
  "extra_missing": "The contract has no rules for additional work. The quote said such work is invoiced hourly after written approval.",
  "extra_rate": "The hourly rate for additional work is NOK {c} in the contract, compared with NOK {o} in the quote.",
  "delivery_earlier": "The delivery deadline in the contract is {c}, earlier than {o} in the quote.",
  "acceptance": "The quote had automatic acceptance after {o} days. The contract requires written acceptance with no deadline, so the client can delay it.",
  "ip_on_signing": "The contract transfers all rights, including sketches and rejected proposals, on signing. The quote only transferred final material, and only after full payment.",
  "liability_uncapped": "The contract makes your liability unlimited, including indirect loss. The quote capped it at the project value. Worth a closer look.",
  "party_entity": "The contract is with {c}, not {o} as in the quote. Check who you can actually invoice.",
 },
}

SEVERITY = {"payment_days": "high", "price_vat": "high", "revisions_unlimited": "high",
            "revisions_missing": "medium", "extra_absorbed": "high", "extra_missing": "high",
            "extra_rate": "medium", "delivery_earlier": "medium", "acceptance": "medium",
            "ip_on_signing": "high", "liability_uncapped": "review", "party_entity": "medium"}

FIELD = {"payment_days": "payment_days", "price_vat": "price_nok_ex_vat",
         "revisions_unlimited": "revision_rounds", "revisions_missing": "revision_rounds",
         "extra_absorbed": "extra_work", "extra_missing": "extra_work", "extra_rate": "extra_work",
         "delivery_earlier": "delivery_date", "acceptance": "acceptance", "ip_on_signing": "ip_transfer",
         "liability_uncapped": "liability", "party_entity": "client_party"}

KIND = {"revisions_missing": "missing", "extra_missing": "missing"}  # everything else: "differs"


# --------------------------------------------------------------------------
# Build one pair
# --------------------------------------------------------------------------

def render(title, header, sections):
    out = [title, "", header, ""] if header else [title, ""]
    for i, (head, body) in enumerate(sections, 1):
        out += [f"{i}. {head}", body, ""]
    return "\n".join(out).rstrip() + "\n"


def build_pair(b, mutations, rng):
    L, t = b["lang"], T[b["lang"]]
    h = t["h"]
    pick = rng.choice
    pf = rng.randint(0, 1)  # number style in contract

    # ---- offer ----
    o = {}
    o["scope"] = t["o_scope_head"](b) + "\n" + "\n".join(f"- {x}" for x in b["deliverables"])
    o["price"] = pick(t["o_price"]).format(p=nok(b["price"]))
    o["revisions"] = pick(t["o_rev"]).format(n=b["revisions"], nw=num_word(b["revisions"], L))
    o["extra"] = pick(t["o_extra"]).format(r=nok(b["rate"]))
    o["delivery"] = pick(t["o_deliv"]).format(dl=d_long(b["delivery"], L))
    o["acceptance"] = pick(t["o_acc"]).format(k=b["acceptance_days"])
    o["payment"] = pick(t["o_pay"]).format(d=b["payment_days"])
    o["ip"] = pick(t["o_ip"])
    o["liability"] = pick(t["o_liab"])
    offer_sections = [(h[k], o[k]) for k in ["scope", "price", "revisions", "extra", "delivery",
                                             "acceptance", "payment", "ip", "liability"]]
    offer_text = render(f"{t['offer_title']} – {b['project']}", t["offer_intro"](b),
                        offer_sections) + "\n" + t["offer_close"](b) + "\n"

    offer_fields = dict(client_name=b["client"], client_org=b["client_org"],
                        supplier_name=b["supplier"], supplier_org=b["supplier_org"],
                        price_nok_ex_vat=b["price"], payment_days=b["payment_days"],
                        revision_rounds=b["revisions"],
                        extra_work=dict(billed_hourly=True, rate_nok=b["rate"], requires_written_approval=True),
                        delivery_date=b["delivery"].isoformat(),
                        acceptance=dict(type="automatic_after_days", days=b["acceptance_days"]),
                        ip_transfer=dict(timing="on_full_payment", includes_sketches=False),
                        liability="capped_at_fee")

    # ---- contract (start clean, then apply mutations) ----
    cf = json.loads(json.dumps(offer_fields))
    c = {}
    client_name, client_org = b["client"], b["client_org"]
    if "party_entity" in mutations:
        client_name, client_org = b["client_alt"], b["client_alt_org"]
        cf["client_name"], cf["client_org"] = client_name, client_org
    p_line, s_line = t["c_parties"](b, client_name, client_org)
    c["parties"] = p_line + "\n" + s_line
    c["scope"] = t["c_scope_head"](b) + "\n" + "\n".join(f"- {x}" for x in b["deliverables"]) + "\n" + t["c_ref"](b)

    if "price_vat" in mutations:
        c["price"] = pick(t["c_price_vat"]).format(p=nok(b["price"], pf, L))
        cf["price_nok_ex_vat"] = round(b["price"] / 1.25)
    else:
        c["price"] = pick(t["c_price"]).format(p=nok(b["price"], pf, L))

    if "revisions_unlimited" in mutations:
        c["revisions"] = t["c_rev_unl"]; cf["revision_rounds"] = "unlimited"
    elif "revisions_missing" in mutations:
        c["revisions"] = None; cf["revision_rounds"] = None
    else:
        c["revisions"] = pick(t["c_rev"]).format(n=b["revisions"], NW=num_word(b["revisions"], L, cap=True))

    rate = b["rate"]
    if "extra_absorbed" in mutations:
        c["extra"] = t["c_extra_abs"]
        cf["extra_work"] = dict(billed_hourly=False, rate_nok=None, requires_written_approval=False,
                                included_in_fixed_price=True)
    elif "extra_missing" in mutations:
        c["extra"] = None; cf["extra_work"] = None
    else:
        if "extra_rate" in mutations:
            rate = int(round(b["rate"] * 0.7 / 50) * 50); cf["extra_work"]["rate_nok"] = rate
        c["extra"] = pick(t["c_extra"]).format(r=nok(rate, pf, L))

    deliv = b["delivery"]
    if "delivery_earlier" in mutations:
        deliv = b["delivery"] - timedelta(days=pick([14, 21])); cf["delivery_date"] = deliv.isoformat()
    c["delivery"] = pick(t["c_deliv"]).format(dl=d_long(deliv, L), dn=d_num(deliv, L))

    if "acceptance" in mutations:
        c["acceptance"] = t["c_acc_mut"]; cf["acceptance"] = dict(type="written_confirmation", days=None)
    else:
        c["acceptance"] = pick(t["c_acc"]).format(k=b["acceptance_days"])

    pay = b["payment_days"]
    if "payment_days" in mutations:
        pay = pick([45, 60]); cf["payment_days"] = pay
    c["payment"] = pick(t["c_pay"]).format(d=pay)

    if "ip_on_signing" in mutations:
        c["ip"] = t["c_ip_mut"]; cf["ip_transfer"] = dict(timing="on_signing", includes_sketches=True)
    else:
        c["ip"] = pick(t["c_ip"])

    if "liability_uncapped" in mutations:
        c["liability"] = t["c_liab_mut"]; cf["liability"] = "uncapped"
    else:
        c["liability"] = pick(t["c_liab"])

    c["conf"], c["law"] = t["c_conf"], t["c_law"]
    order = ["parties", "scope", "price", "revisions", "extra", "delivery", "acceptance",
             "payment", "ip", "liability", "conf", "law"]
    contract_sections = [(h[k], c[k]) for k in order if c[k] is not None]
    contract_text = render(f"{t['contract_title']} – {b['project']}", None, contract_sections) \
        + "\n" + t["c_sign"](b, client_name) + "\n"

    # ---- expected findings ----
    oq = {"payment_days": o["payment"], "price_vat": o["price"], "revisions_unlimited": o["revisions"],
          "revisions_missing": o["revisions"], "extra_absorbed": o["extra"], "extra_missing": o["extra"],
          "extra_rate": o["extra"], "delivery_earlier": o["delivery"], "acceptance": o["acceptance"],
          "ip_on_signing": o["ip"], "liability_uncapped": o["liability"],
          "party_entity": f"{b['client']} (org.nr. {b['client_org']})" if L == "no"
                          else f"{b['client']} (reg. no. {b['client_org']})"}
    cq = {"payment_days": c["payment"], "price_vat": c["price"], "revisions_unlimited": c["revisions"],
          "revisions_missing": None, "extra_absorbed": c["extra"], "extra_missing": None,
          "extra_rate": c["extra"], "delivery_earlier": c["delivery"], "acceptance": c["acceptance"],
          "ip_on_signing": c["ip"], "liability_uncapped": c["liability"], "party_entity": p_line}
    ov = {"payment_days": b["payment_days"], "extra_rate": b["rate"], "revisions_unlimited": b["revisions"],
          "revisions_missing": b["revisions"], "delivery_earlier": d_long(b["delivery"], L),
          "acceptance": b["acceptance_days"], "party_entity": b["client"]}
    cv = {"payment_days": pay, "extra_rate": rate, "delivery_earlier": d_long(deliv, L), "party_entity": client_name}

    findings = []
    for m in mutations:
        f = FIELD[m]
        findings.append(dict(
            mutation=m, field=f, kind=KIND.get(m, "differs"), severity=SEVERITY[m],
            offer_value=offer_fields.get(f), contract_value=cf.get(f),
            offer_quote=oq[m], contract_quote=cq[m],
            explanation=EXPLAIN[L][m].format(o=ov.get(m, ""), c=cv.get(m, "")),
        ))
    findings.sort(key=lambda x: {"high": 0, "medium": 1, "review": 2}[x["severity"]])
    return offer_text, contract_text, offer_fields, cf, findings


# --------------------------------------------------------------------------
# Plan which pairs to generate
# --------------------------------------------------------------------------

def plan(rng):
    """39 Norwegian pairs (3 bases x 13) and 8 English (2 bases x 4).
    Every mutation appears exactly twice as a single change in the Norwegian set."""
    jobs = []
    no_bases = [b for b in BASES if b["lang"] == "no"]
    en_bases = [b for b in BASES if b["lang"] == "en"]
    singles = MUTATIONS * 2
    rng.shuffle(singles)
    for i, b in enumerate(no_bases):
        jobs += [(b, [])] * 3
        jobs += [(b, [m]) for m in singles[i*8:(i+1)*8]]
        jobs += [(b, rng.sample(MUTATIONS, 2)) for _ in range(2)]
    for b in en_bases:
        jobs.append((b, []))
        jobs += [(b, [m]) for m in rng.sample(MUTATIONS, 2)]
        jobs.append((b, rng.sample(MUTATIONS, 2)))
    return jobs


def assign_splits(records, rng):
    """Test split: one Norwegian single-change pair per mutation type (so every
    type is tested once), a third of the clean pairs, and some English pairs.
    Everything else is dev."""
    for r in records:
        r["split"] = "dev"
    seen = set()
    no_singles = [r for r in records if r["language"] == "no" and len(r["mutations"]) == 1]
    rng.shuffle(no_singles)
    for r in no_singles:
        if r["mutations"][0] not in seen:
            seen.add(r["mutations"][0]); r["split"] = "test"
    for group, n in [(("no", True), 3), (("en", True), 1), (("en", False), 2)]:
        recs = [r for r in records if (r["language"], r["is_clean"]) == group]
        rng.shuffle(recs)
        for r in recs[:n]:
            r["split"] = "test"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)

    records = []
    counters = {}
    for b, muts in plan(rng):
        counters[b["id"]] = counters.get(b["id"], 0) + 1
        pid = f"{b['id']}-{counters[b['id']]:02d}"
        offer, contract, of, cf, findings = build_pair(b, muts, rng)
        records.append(dict(pair_id=pid, language=b["lang"], base_case=b["id"],
                            is_clean=not muts, mutations=muts, offer=offer, contract=contract,
                            offer_fields=of, contract_fields=cf, expected_findings=findings))
    assign_splits(records, rng)

    for r in records:
        d = out / r["split"] / r["pair_id"]
        d.mkdir(parents=True)
        (d / "offer.txt").write_text(r.pop("offer"), encoding="utf-8")
        (d / "contract.txt").write_text(r.pop("contract"), encoding="utf-8")
        r["notes"] = ("Confidentiality and governing-law clauses appear only in the contract. "
                      "They are neutral and should not be reported as findings.")
        (d / "expected.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")

    with open(out / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pair_id", "split", "language", "base_case", "is_clean", "n_findings", "mutations"])
        for r in records:
            w.writerow([r["pair_id"], r["split"], r["language"], r["base_case"], r["is_clean"],
                        len(r["expected_findings"]), ";".join(r["mutations"])])

    print(f"Wrote {len(records)} pairs to {out}/")
    for s in ["dev", "test"]:
        rs = [r for r in records if r["split"] == s]
        print(f"  {s}: {len(rs)} pairs, {sum(r['is_clean'] for r in rs)} clean, "
              f"{sum(len(r['expected_findings']) for r in rs)} expected findings")


if __name__ == "__main__":
    main()
