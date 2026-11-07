# Gaps in the solution: legal, market, scalability and data

> **Status:** Discussion paper for the team, 7 November 2026. Not a decision and not legal advice. The legal points need checking with a lawyer before we rely on them.
>
> **How to read the evidence:** "Code" means checked in this repo on `main` (`4efe19c`). "Source" means a linked source listed at the end. "Assumption" means our own estimate, which we should replace with measured numbers.

## Summary

The prototype shows a working flow, but we have not shown three things that decide whether this is a business:

1. Small firms have this problem often enough to pay for a solution.
2. The product finds more of what matters than pasting the same contract into a general AI assistant.
3. It works on real contracts, which are much longer and messier than our test data.

Scalability is the least urgent of the four areas. By our rough estimates, a realistic early user base needs little capacity and model costs are low per contract. The harder problems are **trust, accuracy and reaching customers cheaply**.

The largest product gap is a contradiction between what we promise and how the system works. The landing page asks "Hva mangler?", but the prompt tells the model not to report topics that neither document mentions, because they cannot be backed by a quote. So the current design cannot flag a missing liability cap unless the topic is mentioned somewhere.

| Area | Most important gap | Urgency |
|---|---|---|
| Data | No accuracy measurement on realistic contracts | Now |
| Market | No evidence of demand, and no proof we beat a general AI assistant | Now |
| Legal | Advice features and real contracts have not been reviewed by a lawyer | Before real users |
| Scalability | Open, unauthenticated, paid endpoints | Before any public launch |

## 1. Legal

### 1.1 Advice is allowed, but it carries responsibility

Since the new advocate rules took effect on 1 January 2025, anyone may give legal advice outside the courts ([regjeringen.no](https://www.regjeringen.no/no/aktuelt/rettsradsmonopolet-oppheves-nar-nytt-advokatregelverk-trer-i-kraft/id3058763/)). That is good news for us, but three limits remain:

- Advice given in a business in an irresponsible way can lead to a ban from Advokattilsynet (§ 70, same source).
- "Jurist" is a protected title, so neither the product nor our marketing should present the assistant as one.
- Representing clients in court remains reserved.

The sources we found do not agree on whether commercial legal-advice providers must register. A lawyer should confirm this, and whether § 70 and any registration rules apply to software.

**A disclaimer does not settle this.** The site says the tool gives no legal advice, while the landing page tabs tell the user what to demand. The closer the product gets to the end goal, the weaker that disclaimer becomes.

### 1.2 Accuracy claims need evidence

The US FTC ordered DoNotPay, the "robot lawyer", to pay $193,000 and barred it from claiming it performs like a real lawyer without evidence. The complaint said the company had not tested whether its service matched a human lawyer, and had not hired attorneys to check quality ([FTC](https://www.ftc.gov/node/87474)). This is US law, but it is a useful warning, and Norwegian marketing rules should be checked too.

We should only claim what we have measured. For example, "tested on 47 constructed cases with known answers", which is the wording `kontraktdata/README.md` already recommends, and only once we have actually run that test.

### 1.3 Silence can read as an all-clear

Findings the user never sees may be the biggest source of harm. Three behaviours in the code on `main` make this worse:

- **Empty result:** the UI shows "Ingen funn å vise", which a stressed user can read as "this contract is fine" (`frontend/src/Tool.tsx`).
- **Silent cut-off:** `review.py` keeps at most six findings, and the user isn't told when more were found.
- **Silent removal:** findings that fail the quote check disappear without notice, unless all of them fail.

**Fix (small and cheap):** say what was and wasn't checked, for example "Vi fant ingen punkter i teksten du la inn. Det betyr ikke at kontrakten er trygg." Also show when findings were removed or cut off.

### 1.4 Contracts are confidential and contain personal data

Real contracts contain the customer's commercial terms, often names and contact details, and sometimes their own confidentiality clause. For real use we would need at least:

- **Clear roles under GDPR:** most likely the user's firm is controller, we are processor and OpenAI is sub-processor. A lawyer should confirm this.
- **Agreements:** a data processing agreement with customers and with OpenAI. OpenAI says it supports signing one.
- **A correct privacy statement:** `store=False` is set in our client, and OpenAI says API data isn't used for training by default. However, a third-party review says API data may be kept for up to 30 days for abuse monitoring, with zero retention only for approved customers. **So "not stored by us" must not become "not stored anywhere".** Check the current OpenAI terms.
- **Location of processing:** OpenAI describes European data residency for eligible API customers. It appears to need configuring, so we shouldn't promise Norwegian or EU processing until it's set up.
- **Warning to users:** uploading a contract may itself conflict with its confidentiality clause. We should tell them, and offer to remove names and amounts where possible.

### 1.5 AI rules

- **EU:** the AI Act's transparency rules became applicable on 2 August 2026, including telling users they are dealing with an AI unless that's obvious ([Goodwin](https://www.goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force)).
- **Norway:** in January 2026, CMS expected the AI Act to become Norwegian law sometime in 2027 ([CMS](https://cms.law/en/nor/publication/teknologinytt-hva-er-kunstig-intelligens-reguleringen-ai-act-og-naar-blir-den-norsk-lov)). Check the current status.
- **Our position (assumption):** we don't appear to be a high-risk system, but that needs confirming. Labelling the chat clearly as AI is easy, so we should simply do it now.

### 1.6 Negotiation psychology

This is an ethical risk as well as a legal one. The advice must not teach users to mislead or pressure the other party. A sensible line is to help with explaining reasons, proposing fair trade-offs and spotting pressure from the other side, and to avoid bluffing or invented deadlines.

### Questions for a lawyer

1. Where is the line between information and advice for this product, and does § 70 or any registration rule apply?
2. What liability do we carry if the tool misses a clause, and how far can terms of service limit it?
3. Which marketing claims are safe?
4. What is the right GDPR setup, including data transfers to OpenAI?
5. Can a user upload a contract that has a confidentiality clause?

## 2. Market advantage

### 2.1 Our real competitor is free and already open

A user can paste both documents into ChatGPT or Claude and ask what changed. We use a general model too, so the first result may look similar. What we add today:

| What we add | How easy to copy | Comment |
|---|---|---|
| Quotes checked against the document | Easy | Valuable, but it only proves the text exists, not that our reading of it is right |
| Comparison against the user's own offer | Easy | Our clearest angle, and easy to explain |
| A ready reply to the customer | Easy | Saves time, but a general assistant can also write one |
| A checked Norwegian checklist of terms | Harder | Doesn't exist yet |
| A published accuracy record | Harder | Doesn't exist yet |
| Sales channels through partners | Hardest | Doesn't exist yet |

**A strategic tension:** the team's new plan puts the contract first and makes the offer optional. This widens the use cases, but contract-only review is exactly what general assistants already do. We should keep the offer comparison prominent, because that is what makes us different.

### 2.2 The test that matters most

Run the same contracts through the same model with a plain prompt, such as "what is different and what should I worry about?", and compare the results with our product. The concept document already suggests this baseline.

If we can't clearly beat it on missed findings, false alarms or time to a usable reply, then the product is a nicer interface and not an advantage. It's better to learn that this week than after building more.

### 2.3 Who actually buys this?

Our documents describe different customers: IT and analytics consultants on SSA-B-style agreements (concept document), small service businesses in general (`TASKS.md`), and design freelancers and agencies (test data).

These groups use different contracts, face different risks and are reached in different ways. **We should choose one.** Design freelancers and small agencies are the natural start, since all our test data fits them.

### 2.4 Business model

Usage is infrequent, because a freelancer might only review a few contracts a year. That has three consequences:

- **Subscriptions are hard to justify** for individuals. Pay-per-contract fits the need better.
- **Revenue per customer is low,** so paid advertising could easily cost more than a customer brings in.
- **Partners may be the only affordable route to customers:** accounting software, banks, insurers, and associations. Grafill, for example, offers its members free legal help, which makes it either a competitor or a natural partner.

An illustrative example, where every number is an assumption:

| | Per customer per year |
|---|---|
| Contracts reviewed | 6 |
| Price per contract | 99 kr |
| Revenue | 594 kr |
| Model cost (see section 3.1) | under 50 kr |
| **Left to pay for sales, support, legal and hosting** | **about 550 kr** |

Model costs aren't the issue here. If winning a customer costs more than a few hundred kroner, this doesn't work without partners or a higher price. The value argument can support a higher price, since one caught change like our 17,000 kr example pays for many reviews. Whether people will actually pay that needs testing.

### 2.5 Competitors we haven't mapped

This paper doesn't contain a proper competitor analysis. Our search found contract-management tools, IKT Norge's paid model agreements ([Hjort](https://www.hjort.no/en/?p=10536)), and AI tools in legal research services aimed at lawyers. Someone should map direct competitors in the Nordics before the jury asks.

## 3. Scalability

The earlier jury question was about overloaded databases. We have no database today, so the useful discussion is about what limits us instead.

### 3.1 Cost per contract is probably low (assumption)

Reported list prices for `gpt-6.1-sol` are $2 per million input tokens and $10 per million output tokens. These come from third-party sites, and we couldn't open OpenAI's own price page.

| Item | Estimate |
|---|---|
| Largest input: two documents of 20,000 characters plus instructions | about 15,000 tokens, $0.03 |
| Largest output, capped by `max_output_tokens=8192` | $0.08 |
| **Largest cost per model call** | **about $0.11** |
| One analysis and five chat messages, worst case | about $0.70, or roughly 8 kr at an assumed 11 kr per dollar |

This corrects a concern raised earlier in the team's discussion: model cost is unlikely to be what breaks the business. It should be replaced with real token counts from live runs, since these are upper estimates and chat requests may be somewhat larger.

### 3.2 Capacity is not the near-term limit (assumption)

| Scenario | Value |
|---|---|
| Customers | 1,000 |
| Contracts per customer per year | 6 |
| Model calls per contract | 6 |
| Total model calls | 36,000 per year, about 100 per day |

FastAPI runs our blocking route on a thread pool, 40 threads by default as far as we know. Even if every call took the full 60 seconds, one process could handle about 40 calls a minute, which is far above the average load in this scenario. We have not load-tested this, and OpenAI's rate limits for our account may be the real ceiling.

### 3.3 What would actually hurt

| Gap | Effect | Fix |
|---|---|---|
| **No login or rate limit** (code) | Anyone who finds the endpoint can spend our money. At $0.11 a call, 10,000 calls cost $1,100 | Login or payment first, per-user limits, a hard spending cap at OpenAI |
| **Long blocking calls and no retries** (code: 60 s timeout, `max_retries=0`) | Slow calls hold a thread, and a brief provider error reaches the user | Async client, limited retries, later a queue with progress |
| **One provider** | An OpenAI outage stops the core feature | Clear error message at first, a second provider later |
| **No monitoring** | We can't see cost, errors or how long calls take | Log status, duration and tokens, never document text |

### 3.4 Quality scales worse than the servers

These limits matter more than traffic does:

- **Length:** the limit is 20,000 characters per document. As a rough assumption, that's 6–8 pages, so longer contracts with attachments won't fit. The user must cut the text down manually, which means parts may never be checked.
- **PDFs:** scanned documents aren't supported. Our PDF tests only used browser-generated files, so Word exports, multiple columns and words split across lines are untested.
- **New contract types and countries:** each needs its own checklist, test set and legal review, so cost grows with coverage even though the software itself is cheap to run.

### 3.5 When a database arrives

Accounts, payments and saved history would need a database. Postgres is a good default for this usage, with connection pooling, and no database transactions held open during model calls. Storing contracts is a bigger privacy decision than a technical one, so we should keep not storing them for as long as we can.

## 4. Sourcing of data

### 4.1 Test data is far from real contracts

Measured from `kontraktdata/` (code):

| Measure | Result |
|---|---|
| Documents | 94, across 47 pairs |
| Median length | 1,641 characters |
| Longest | 1,894 characters, about 9% of the 20,000 limit |
| Expected findings | 44, with 11 clean pairs |
| Source | Generated from five templates |

Passing these tests says little about a 15-page contract with cross-references, attachments and unusual wording.

We also haven't used this set properly. No script on `main` refers to `kontraktdata`, and the live log in `examples/evaluations.md` covers only the five small examples in `examples/`, each under about 500 characters where we checked. **We don't yet have accuracy numbers from the 47 pairs.** The only thing they have been used for is testing PDF extraction.

### 4.2 Checked quotes don't mean correct answers

A study of legal research tools built on retrieval found they still gave wrong or unsupported answers between 17% and 33% of the time, and called claims of hallucination-free results overstated ([Magesh et al.](https://arxiv.org/abs/2405.20362v1)). The tools and task differ from ours, and the study tested 2024 versions, but the lesson applies.

Our check in `review.py` confirms that a quote exists in the document. It can't confirm that:

- the explanation is right
- the quote is the relevant one
- something else important wasn't missed
- the suggested change is sensible

So "sitatene er kontrollert" should not be heard as "svaret er riktig", and the pitch should make that clear.

### 4.3 Advice needs sources we don't have

For the end goal, each kind of advice needs its own basis:

| Advice | Source needed | Status |
|---|---|---|
| What changed | The user's own documents | Have it |
| What this clause means | The document, plus legal background | Partly |
| What should be in the contract | A checked checklist, built from sources such as [SSA templates](https://www.anskaffelser.no/verktoy/mal/ssa-b-og-ssa-b-enkel-bistandsavtalene), industry norms and law, reviewed by a lawyer | Missing |
| What's normal in the market | Many real contracts, or expert judgment | Missing, and the prompt correctly forbids claiming it today |
| Negotiation psychology | Recognised negotiation literature and expert review | Missing |

Someone must also own keeping this up to date, since laws and standards change. Check the licence terms of every source. Paid model agreements, for example, can't be assumed free to reuse.

**Design change needed for "Hva mangler?":** every finding currently needs a quote, and an absence has none. It could work like this:

1. Add a status such as `ikke_nevnt`, linked to a checklist item as its source. This is an API change, so it needs agreeing with Rajvir and Herman.
2. Word it carefully: "Vi fant ikke dette i teksten du la inn", since it may be in an attachment we haven't seen.
3. Test it for false "missing" alarms, because those would quickly destroy trust.

### 4.4 Getting real contracts

Real data is the hardest thing to get, and the most valuable. Workable routes:

- **Testers who agree to share:** with written consent, anonymised, and with a clear deletion date. Also consider that the other party's information is in there.
- **Public sector contracts and templates:** easier to get, but they differ from what freelancers receive.
- **Public benchmark sets:** [CUAD](https://arxiv.org/abs/2103.06268) has over 13,000 expert annotations on about 500 contracts, reportedly under CC BY 4.0. It's in English and from a US commercial setting, so it's useful for testing method and long documents, not for Norwegian accuracy.

The rule in `AGENTS.md` still applies: real contracts stay out of Git, the frontend and logs. A separate access-controlled store with a deletion routine is needed before collecting any.

### 4.5 Attacks through the document

The contract comes from the other party, and PDF extraction can also pick up text that a reader never sees, such as white text. A hidden line could tell the model not to mention a clause. The prompt says to treat documents as source text and ignore their instructions, which is the right start, but we found no test for it (code). The quote check wouldn't catch this either, since a missing finding has no quote to check. We should add test cases for it.

### 4.6 Our market evidence is thin

| Claim | What we have | Weakness |
|---|---|---|
| Payment terms hurt small firms | Fortnox: 17% of Swedish small-business invoices paid late or not at all, 2023 | Sweden, from a vendor, and about late payment rather than changed contracts |
| Many small firms exist | SSB: 38,115 new sole proprietorships in 2020 | Old, and not all of them are in our segment |
| **Contracts differ from offers** | **Nothing** | **This is the claim our whole idea depends on** |
| **People would pay** | **Nothing** | **Same** |

## 5. What to do next

The order is cheapest and most decisive first. Owners are suggestions.

| # | Action | Answers | Suggested owner | Effort |
|---|---|---|---|---|
| 1 | Interview 5–10 design freelancers and agency owners | Is the need real? Would they pay? | Whole team | 2–3 days |
| 2 | Run the 47 pairs live and score them, using the scoring in `kontraktdata/README.md` | How accurate are we? | Vasilii, Herman | 1 day |
| 3 | Run the same pairs with a plain prompt | Do we beat a general assistant? | Vasilii, Herman | 1 day |
| 4 | Fix the wording for empty, cut-off and removed findings | Reduces false reassurance | Elias, Rajvir | Hours |
| 5 | Record real tokens and duration per call | Real cost and speed | Rajvir | Hours |
| 6 | Add test cases for hidden instructions in documents | Is it robust? | Vasilii, Herman | Hours |
| 7 | One hour with a lawyer, using the questions in section 1 | Can we offer advice, and how? | Whole team | 1 hour |
| 8 | Collect 10–20 real anonymised contracts with consent, and have an expert review them | Does it work on real contracts? | Whole team | Weeks |
| 9 | Build and legally review a checklist for one niche | Our main possible advantage | Herman, plus a lawyer | Weeks |
| 10 | Add login, limits and spending cap | Safe to go public | Rajvir | Days |

### Suggested go or no-go checks

These thresholds are suggestions to debate, not established standards.

| Question | Continue if |
|---|---|
| Is the problem real? | At least half of those interviewed have signed something that differed from their offer, or skipped reading a contract and regretted it |
| Will they pay? | At least 3 of 10 will try it on a real contract, or commit to a price |
| Does it find what matters? | At least 90% of high-severity findings in the 47 pairs |
| Does it avoid false alarms? | At most 1 of the 11 clean pairs gets a false alarm |
| Does it beat the baseline? | Clearly better than the plain prompt on the above |
| Does it hold up on real contracts? | An expert finds no serious misses or errors in most of a reviewed sample |

### Decisions the team should make

1. **Who is the first customer?** We suggest design freelancers and small agencies.
2. **Is the offer comparison still our main angle,** or is contract-only review the main product?
3. **What is the landing page allowed to promise today?** We suggest marking rights and psychology advice clearly as coming later, until they exist and are reviewed.
4. **Direct sales or partners?** The numbers above point toward partners.

## 6. Suggested answers for the jury

- **"Is this legal advice?"** "Nei, vi viser hva som står og hva du bør spørre om. Før vi utvider til råd om krav, vil vi få det vurdert av en jurist."
- **"Why not just use ChatGPT?"** "Du kan det, men vi sammenligner mot ditt eget tilbud, kontrollerer sitatene mot dokumentet og lager et svar du selv godkjenner. Vi måler nå om det faktisk gir bedre resultat."
- **"Can it scale?"** "Serveren lagrer ingenting mellom forespørsler, så den er enkel å skalere. Den virkelige utfordringen er kvalitet på lange, ekte kontrakter."
- **"Is the data safe?"** "Vi lagrer ikke kontrakter. Teksten sendes til modelleverandøren, så før ekte bruk trenger vi databehandleravtale og tydelig informasjon til brukeren."
- **"How accurate is it?"** Give only numbers we have measured. Today, that's: "Våre fem små testeksempler besto i live-kjøring. Nøyaktighet på større datasett og ekte kontrakter er neste steg."

## Sources

**Legal**
- [Regjeringen: Rettsrådsmonopolet oppheves](https://www.regjeringen.no/no/aktuelt/rettsradsmonopolet-oppheves-nar-nytt-advokatregelverk-trer-i-kraft/id3058763/)
- [Regjeringen: Advokatloven trer i kraft](https://www.regjeringen.no/id3058766/)
- [FTC: DoNotPay order](https://www.ftc.gov/node/87474)
- [Goodwin: EU AI Act transparency obligations](https://www.goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force)
- [CMS: When the AI Act becomes Norwegian law](https://cms.law/en/nor/publication/teknologinytt-hva-er-kunstig-intelligens-reguleringen-ai-act-og-naar-blir-den-norsk-lov)

**Provider and cost**
- [OpenAI: Business data privacy](https://openai.com/index/business-data/) (we read a search excerpt, because the page blocked direct access)
- [Redress Compliance: OpenAI data clauses](https://redresscompliance.com/openai-data-privacy-enterprise-agreement-clauses) (third-party source for the retention point)
- [Developers Digest: GPT-6.1 Sol](https://www.developersdigest.tech/models/gpt-6-1-sol) (third-party source for prices)

**Accuracy and data**
- [Magesh et al.: Hallucination-Free?](https://arxiv.org/abs/2405.20362v1)
- [CUAD paper](https://arxiv.org/abs/2103.06268)
- [DFØ: SSA-B](https://www.anskaffelser.no/verktoy/mal/ssa-b-og-ssa-b-enkel-bistandsavtalene)

**Market**
- [Fortnox: Late payment in Sweden](https://www.fortnox.se/fortnox-foretagsguide/driva-foretag/finansiering/uppemot-var-femte-krona-betalas-sent-till-foretagare)
- [SSB: New businesses](https://www.ssb.no/virksomheter-foretak-og-regnskap/statistikker/etablerere/aar)
- [Grafill: Legal assistance](https://www.grafill.no/om-grafill/english-2/legal-assistance)
- [Hjort: Model agreements](https://www.hjort.no/en/?p=10536)
