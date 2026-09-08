# Code of Conduct Policy — Chatbot Evaluation Set

**Corpus document:** `Code_of_Conduct.pdf` — Code of Conduct Policy, Asia Asset Finance PLC
**Policy version:** 04 (Four) 2025/2026 · Effective 23 June 2025 · Next review 23 June 2026
**Owner:** Manager – Policy Planning, Policy & Planning Department
**Target system:** AAF HRMS AI Assistant (production chatbot)
**Question count:** 20 graded + 1 routing control

Companion set: `hr_policy_eval.md`. IDs are prefixed `CC-` here and `EVAL-` there so results can be pooled into one run without collision.

---

## How to use this set

Same four-axis rubric as the HR Policy set — Correctness, Groundedness, Citation, Routing — scored 0/0.5/1, with any `must_not_include` violation counting as an outright fail on the item.

What's different about this set: four items (CC-14 to CC-17) require retrieving from **both** the Code of Conduct and the HR Policy in a single answer. These are the items that exercise cross-document RAG rather than single-document lookup, and they are the ones worth watching when you tune reranker depth or fusion weighting. Two of them involve rules that genuinely differ between the documents, so the correct answer is a reconciliation, not a pick.

Coverage: 6 single-hop, 3 table-and-numeric, 4 multi-hop within document, 4 cross-document, 2 conduct-and-premises rules, 1 abstention, 1 routing control.

---

## Section 1 — Single-hop factual retrieval

### CC-01 · Working hours and lunch break
**Intent:** RAG
**Question:** What are the official working hours, and is the lunch break included in them?
**Expected answer:** 8.30 am to 5.00 pm, inclusive of a half-hour staggered lunch break. Employees must sign or scan attendance on arrival and departure. Staff may be required to work after hours, and working hours can be shifted at management's discretion. Leaving the office premises during working hours requires prior approval from the immediate supervisor.
**Source:** §10.1 Working Hours
**must_include:** 8.30 am–5.00 pm, half-hour lunch break included
**must_not_include:** a lunch break stated as additional to the 8.30–5.00 window

---

### CC-02 · Dress code, Friday and Saturday
**Intent:** RAG
**Question:** What am I supposed to wear on a Friday?
**Expected answer:** The company-provided T-shirt on Fridays; smart casual on Saturdays. This applies to both male and female staff. Regardless of day, ¾ pants and rubber slippers are not allowed, and clothing that covers the full face is not allowed.
**Source:** §12.1, §12.2, §12.3, §12.4 point 2–3
**must_include:** company T-shirt for Friday
**must_not_include:** smart casual given as the Friday rule (that is Saturday), office wear with tie (Monday–Thursday)
**Note:** §12.1 and §12.2 both compress Friday and Saturday into one bullet; only §12.3 splits them. Tests whether retrieval reaches the section that actually distinguishes the two days.

---

### CC-03 · Telephone etiquette thresholds
**Intent:** RAG
**Question:** How quickly should I pick up a customer call and how long should the call be?
**Expected answer:** All calls must be answered within a maximum of three rings. Official calls should be short — 3 to 7 minutes. If the conversation will be lengthy, take the customer's details and revert within the day. External calls open with "Good morning / Good afternoon"; on internal calls, identify yourself by name.
**Source:** §21.1, §21.3
**must_include:** 3 rings, 3–7 minutes
**must_not_include:** the 3-ring figure applied to call duration or vice versa

---

### CC-04 · Gifts, hampers and bribes
**Intent:** RAG
**Question:** A customer sent me a hamper for the new year. Do I have to do anything about it?
**Expected answer:** Yes — notify the Human Resources Department with the sender's details and the approximate value. Hampers are not treated as bribes. Promotional items such as diaries and calendars are also not considered bribes or gratuities. Any other items received must be brought to the notice of the respective superior. An employee proved to have received a bribe or gratuity, in cash or in kind, in connection with company business is liable for immediate dismissal without compensation.
**Source:** §14 Accepting Benefits from Customers
**must_include:** notify HR, sender and approximate value, hampers not a bribe
**must_not_include:** the hamper characterised as a bribe or as grounds for dismissal, a monetary threshold (the policy sets none)
**Note:** The dismissal sentence sits directly above the hamper carve-out. Over-triggering on "bribe" and telling the employee to refuse or report themselves is the failure mode.

---

### CC-05 · Official language and communication protocol
**Intent:** RAG
**Question:** Can I send official emails in Sinhala?
**Expected answer:** No. The mode of official communication is English, and all company transactions are to be conducted in English. Staff must also follow the communication protocol, channelling communications through their supervisors to the respective Senior Manager / AGM.
**Source:** §22 Maintaining Protocol and Language Policy
**must_include:** English as the official mode, the supervisor channelling requirement
**must_not_include:** permission to use Sinhala or Tamil for official transactions
**Note:** The rule constrains the employee's official communications, not the assistant's answers. The chatbot should state it as written — flag any response that hedges it into a suggestion, adds exceptions the policy doesn't contain, or reasons about its own output language instead of answering the question.

---

### CC-06 · Policy ownership and version
**Intent:** RAG
**Question:** Who owns the Code of Conduct and which version is current?
**Expected answer:** Version 04 (Four) 2025/2026, owned by the Manager – Policy Planning, under the Policy & Planning Department. Prepared by the Policy Planning Department, approved by the Board of Directors on 23 June 2025, effective 23 June 2025, next review 23 June 2026.
**Source:** Cover page control table
**must_include:** version 04, Manager – Policy Planning / Policy & Planning Department
**must_not_include:** Head of HR or HR Department as the owner (that is the HR Policy's control table), 20 June 2024 as the effective date
**Note:** The two documents have visually near-identical cover tables with three shared dates. This item tests whether the model attributes ownership to the right document rather than blending the two.

---

## Section 2 — Table and numeric extraction

### CC-07 · Leasing service standards
**Intent:** RAG
**Question:** How long do we have to approve a leasing facility?
**Expected answer:** 24 hours from the time of application for a customer within a 25 km radius of the office; 36 hours if beyond 25 km. The delivery order must be released within 4 hours of approval and/or one hour after payment of offer charges. Vendor payments must be made within 4 hours of forwarding the registration certificate.
**Source:** §19.1 Leasing
**must_include:** 24 hrs, 36 hrs, the 25 km radius distinction
**must_not_include:** 10 or 15 working days (those are the mortgage figures)

---

### CC-08 · Mortgage and other facility standards
**Intent:** RAG
**Question:** What's the turnaround time for approving a mortgage loan, and when does the money go out?
**Expected answer:** 10 working days within a 25 km radius; 15 working days beyond 25 km, from the time of application. The first disbursement is made within 4 working hours from completion of documentation, including legal documents.
**Source:** §19.2 Mortgage Loan & Other Facilities
**must_include:** 10 working days, 15 working days, 4 working hours
**must_not_include:** hours substituted for working days, the leasing figures
**Note:** Paired with CC-07 on purpose. The two blocks are structurally identical, adjacent, and differ in unit (hours vs working days). Cross-contamination between them is the single most likely numeric error in this document.

---

### CC-09 · Consequences of misconduct
**Intent:** RAG
**Question:** What happens immediately if I'm accused of misconduct?
**Expected answer:** The employee is liable to be suspended from work without pay pending investigation. If found guilty at a disciplinary inquiry, services may be terminated or the employee suspended without pay, depending on the gravity of the offence. The company reserves the right to warn verbally or in writing without an inquiry. Where a KMP, Departmental Head or Branch Head is involved, it could result in the Board of Directors being informed.
**Source:** §11 Conduct & Decorum at Work
**must_include:** suspension without pay pending investigation, the KMP/Head escalation to the Board
**must_not_include:** the penalisation-level percentages from the HR Policy §1.4 table presented as Code of Conduct provisions
**Note:** The HR Policy's Level 1–5 PA-deduction table is a strong lexical match for "misconduct consequences" and belongs to a different disciplinary track. Pulling it here is a cross-document retrieval error, not a correct synthesis.

---

## Section 3 — Multi-hop within the document

### CC-10 · Post-employment restrictions
**Intent:** RAG
**Question:** I'm resigning to join another finance company. What restrictions apply to me after I leave?
**Expected answer:** Three distinct obligations. (1) Non-solicitation — during and after employment, you must not directly or indirectly solicit or entice away clients, customers or employees. (2) A three-year restriction — for three years after cessation of employment, for whatever reason, you must not set up, be associated with, or be interested in any entity in direct or indirect competition in Sri Lanka with the Relevant Companies, except with the company's written approval. (3) A continuing duty of confidentiality — you must not use, disclose or exploit customer data, contact details or proprietary information to canvass or solicit business for another organisation, competitor or personal venture. Separately, staff leaving by retirement, resignation, retrenchment or dismissal are prohibited from taking, copying, storing or sharing customer data in print or electronic form; such action attracts legal penalties.
**Source:** §28.1 Non-Solicitation (a)–(c), §28.3 Prohibitions (b)
**must_include:** the three-year period, the written-approval exception, the data-removal prohibition
**must_not_include:** an unrestricted right to join a competitor
**Note:** Requires assembling three separated clauses. The three-year restriction is the item most often missed because it sits in a sub-clause rather than under a heading. **This changes the correct answer to EVAL-07 in the HR Policy set** — once both documents are in the corpus, a question about post-employment obligations should surface the three-year term, and EVAL-07's `must_not_include` on "fixed non-compete duration" should be retired.

---

### CC-11 · Secondary employment
**Intent:** RAG
**Question:** Can I do freelance work on weekends?
**Expected answer:** Not without prior written permission from the company. Employees are prohibited from taking or continuing employment, or providing consultancy or any other services, to any person or entity — full time or part time, paid or unpaid — without first obtaining written permission. The same applies to carrying on a business or receiving profits, commissions or gratification from any person or entity.
**Source:** §28.3 Prohibitions (a)–(b)
**must_include:** written permission requirement, the unpaid/part-time scope
**must_not_include:** permission implied because the work is outside office hours or unpaid
**Note:** "Whether for any payment or otherwise" is the clause that decides the answer and is the one most likely dropped.

---

### CC-12 · Personal work during office hours
**Intent:** RAG
**Question:** I need an hour to sort out something personal during the day. What's the correct way to do it?
**Expected answer:** Apply for short leave or half a day's leave from your supervisor. Work hours must not be used for personal work of any nature, whether inside or outside the office. Leaving the premises during working hours also requires prior approval from the immediate supervisor.
**Source:** §28.3 Prohibitions (c), §10.1 point 4
**must_include:** short leave / half-day leave applied for through the supervisor
**must_not_include:** informal permission or making up the time later

---

### CC-13 · Bullying and harassment
**Intent:** RAG
**Question:** A colleague keeps excluding me from team meetings and undermining me in front of others. Is that covered by the Code?
**Expected answer:** Yes. Bullying or harassment of any staff member or stakeholder is a serious offence, and the Code's definition expressly includes excluding someone from work-related events, regularly undermining someone, putting a person in an embarrassing work situation, picking on someone, aggressive behaviour, unreasonable work demands, pressuring someone to behave inappropriately, denying training or promotion opportunities, and spreading malicious rumours. Misconduct is recognised whether it occurs face to face, by email, by phone or by letter. Report it through the whistle-blower policy or designated reporting channels; reports are treated confidentially, anonymity of complainants is maintained, and the informant's details are not disclosed without consent.
**Source:** §11.1.2–11.1.3, §25 Reporting Violations, §26 Whistle Blower Policy
**must_include:** confirmation that exclusion and undermining are named in the definition, a reporting route
**must_not_include:** a judgement on whether this specific colleague is guilty, advice to confront the colleague directly, minimising the behaviour as interpersonal
**Note:** Behavioural item. The assistant should describe the policy and the reporting route, not adjudicate the incident or counsel the employee. Grade tone as well as content.

---

## Section 4 — Cross-document retrieval

These require both the Code of Conduct and the HR Policy. An answer drawn from only one document is at most half correct.

### CC-14 · Late attendance — two rule sets
**Intent:** RAG (cross-document)
**Question:** I got in at 9.15 this morning. What happens?
**Expected answer:** Arriving after 8.30 am on an exceptional basis is allowed subject to applying for short leave (Code of Conduct §10.2). The HR Policy quantifies it: lateness up to 1.5 hours is treated as short leave, over 1.5 hours as half a day's leave — so 9.15 falls within short leave. Habitual lateness is treated differently: habitual late attendees must apply for half a day or casual leave depending on arrival time, and regular late attendance draws a letter of notice, then caution, then warning with further disciplinary action.
**Source:** Code of Conduct §10.2; HR Policy §10.3, §10.5
**must_include:** short leave for this instance, the 1.5-hour threshold from the HR Policy, the habitual-lateness distinction
**must_not_include:** either document's rule presented as the complete answer

---

### CC-15 · Sick leave notification — conflicting deadlines
**Intent:** RAG (cross-document)
**Question:** I woke up ill. By when do I need to tell someone, and do I need a medical certificate?
**Expected answer:** The Code of Conduct requires informing the Head of the Branch or Department before 9.00 am the same day, by telephone or electronic message. The HR Policy states the Head of Department, HR Division or officer in charge of leave should be informed at the earliest opportunity and not later than 24 hours after the absence begins. The stricter same-day 9.00 am deadline governs. On certificates: if the absence exceeds two days, a medical certificate must reach the HR Manager or Officer in Charge of leave no later than the third day of absence, stating the date of issue, the date the employee was first seen, the nature of the illness, and the number of days the employee is expected to be unfit. Management reserves the right to investigate the genuineness of any certificate.
**Source:** Code of Conduct §10.3; HR Policy §7 Leave Entitlements — Medical/Sick Leave
**must_include:** both deadlines surfaced, the stricter one applied, the third-day certificate rule
**must_not_include:** the 24-hour rule given alone as the answer
**Note:** The two documents genuinely differ here. The correct behaviour is to surface both and apply the tighter deadline — not to silently pick whichever chunk ranked higher. This is the clearest test in either set of whether the system reconciles or just retrieves.

---

### CC-16 · Overtime eligibility and payment
**Intent:** RAG (cross-document)
**Question:** Am I entitled to overtime, and when does it get paid?
**Expected answer:** Overtime is paid to staff of Junior Executive grade and below, for work after 5.30 pm, and only with the prior approval of the immediate supervisor (Code of Conduct §10.1). The HR Policy adds that payment is made in accordance with the Shop and Office Act and prevailing labour regulations, paid monthly, and that refusing to work overtime when required, without valid reason, constitutes misconduct. Work after office hours also needs written approval by email and must be supervised.
**Source:** Code of Conduct §10.1 point 5; HR Policy §10.4, §10.1
**must_include:** the Junior Executive and below eligibility, the 5.30 pm threshold, monthly payment
**must_not_include:** overtime offered to grades above Junior Executive

---

### CC-17 · Company ID card
**Intent:** RAG (cross-document, deduplication)
**Question:** What are the rules about my company ID card?
**Expected answer:** Permanent employees are issued an ID card, which must be worn or displayed at all times during office hours. It remains the property of AAF and must be returned to HR on cessation of employment — the staff member and the Branch Manager are jointly responsible for return at resignation. If lost, notify HR immediately and arrange a replacement without delay. The card is issued solely to identify employees during company-related business; any other use, or handing it to a third party, is strictly prohibited and subject to disciplinary action. Employees may request to see another employee's company ID to verify staff status; if identification fails, contact the CISO or Head of HR immediately. Trainees and other non-permanent staff receive temporary ID cards.
**Source:** Code of Conduct §12.4; HR Policy §2.8 Identity Cards
**must_include:** wear at all times, misuse prohibition, CISO / Head of HR verification route, return on cessation
**must_not_include:** the same rule stated twice as though the two documents impose different requirements
**Note:** The passages are near-verbatim across the two documents, and §12.4 items 1.2 and 1.3 are identical duplicates *within* the Code of Conduct. Three copies of one rule are in the index. A clean, non-repetitive answer citing both documents once is the pass condition; a bulleted list restating the misuse clause twice is a deduplication failure.

---

## Section 5 — Conduct and premises rules

### CC-18 · Smoking and intoxication
**Intent:** RAG
**Question:** Can I smoke inside the office, and what's the rule on coming in after a drink?
**Expected answer:** Smoking inside office premises is prohibited. Staff must not enter office premises after consuming alcohol or any illegal substance. Separately, intoxication during working hours is listed as misconduct, which makes the employee liable to suspension without pay pending investigation and possible termination if found guilty at inquiry. The HR Policy states the same entry prohibition.
**Source:** §13 Smoking; §11.1.4; HR Policy §10.1
**must_include:** smoking prohibited inside premises, no entry after alcohol or illegal substances, intoxication as misconduct
**must_not_include:** a designated smoking area or any permitted exception (the policy names none)
**Note:** Two-part question requiring §13 and §11.1.4, which are three pages apart. A model that answers only the smoking half is a partial retrieval failure, not a partial answer.

---

### CC-19 · Male dress code
**Intent:** RAG
**Question:** What's the dress code for male staff Monday to Thursday, and is there anything specific for marketing staff?
**Expected answer:** Monday to Thursday, male staff wear office wear with a tie; shirt and trousers are the standard on working days. Clothes must be clean, well pressed and well fitting, shoes well polished, and hair neat and not coloured. Marketing staff are specifically required to wear ties during office hours and during meetings held with customers.
**Source:** §12.2 Male Staff
**must_include:** office wear with tie, the marketing-staff tie requirement
**must_not_include:** female dress code items (office blouse, saree, skirt), Friday/Saturday casual attire given as the Monday–Thursday rule
**Note:** The male and female dress blocks are adjacent and structurally parallel, which makes them easy to blend. Cross-gender contamination is the failure mode.

---

## Section 6 — Robustness

### CC-20 · Out-of-scope question (abstention test)
**Intent:** RAG → abstain
**Question:** What is AAF's work-from-home policy? How many remote days do I get?
**Expected answer:** Neither the Code of Conduct nor the HR Policy addresses remote or hybrid work. Both define fixed on-site hours of 8.30 am to 5.00 pm with attendance recorded on-site, and the HR Policy requires attendance to be marked at whichever branch the employee is working from. The assistant should state that no work-from-home provision exists in these documents and refer the employee to HR.
**Source:** Absence of provision across both documents
**must_include:** explicit statement that the policy does not cover this, referral to HR
**must_not_include:** any invented number of remote days, a hybrid arrangement described as permitted, general market practice presented as AAF policy
**Note:** Harder abstention than EVAL-20 in the HR set, because both documents contain adjacent attendance and working-hours language that a generative model can easily extend into an answer. A confident fabrication here should block release.

---

### CC-21 · Lost ID card (routing control)
**Intent:** BOTH (RAG + TOOL)
**Question:** I lost my office ID card this morning — what do I do and can you raise it for me?
**Expected answer:** Two parts. Policy: notify the HR department immediately and arrange a replacement without delay; the card is company property and misuse or third-party handover is a disciplinary matter. Action: invoke the ID replacement / HR notification workflow tool for the authenticated user, or state plainly that the request must be raised through HR if no such endpoint exists. A policy-only answer is incomplete; a tool call with no policy context is also incomplete.
**Source:** Code of Conduct §12.4 point 1.1; HR Policy §2.8 — plus workflow endpoint
**must_include:** both the policy instruction and either a tool action or an explicit statement that one is needed
**must_not_include:** a fabricated confirmation that a replacement request was filed
**Note:** The BOTH-intent control for this set. Retrieval overlap with CC-17 is near total, so this pair also tests whether the router splits on intent rather than content — CC-17 is pure RAG, CC-21 is not.

---

## Known document quirks affecting grading

Artefacts of the source PDF. Don't penalise the model for these, but watch for answers that inherit them:

1. **Duplicated ID clause.** §12.4 items 1.2 and 1.3 are word-for-word identical. Combined with the near-identical passage in HR Policy §2.8, one rule appears three times in the index. Covered by CC-17.
2. **Broken lettering in §28.3.** The list runs a), b), b), c) — two items lettered b). Citations to either "b" are acceptable.
3. **Duplicate numbering in §20.** Two items are numbered 6 (credit policy guidelines, and receipting monies collected).
4. **Whistle-blower ambiguity.** §26 states information received "will be used to evaluate the customer without his/her knowledge" — in context this most likely means the subject of the complaint, not a customer. Do not grade on this sentence; flag any answer that confidently interprets it either way, as that is unsupported inference rather than retrieval.
5. **Cover-table collision.** Both documents show approval 23 June 2025, last modification 20 June 2024, next review 23 June 2026. Only the version number, department and owner distinguish them. Covered by CC-06.
6. **Vision statement mismatch.** §1 here reads "To become a premier finance company in Sri Lanka" plus "Empowering people and transforming lives"; the HR Policy's version is longer and references shareholders, customers and regulators. A question on the vision has two defensible answers — avoid grading on it, or accept either with citation.
7. **Gendered grooming rule.** "Hair should be neat and not coloured" appears only under male staff. The asymmetry is in the source; the model should report it as written rather than generalising it to all staff.
8. **Amendment table page references** point to pages that don't align with the contents listing. Citations by section number are more reliable than by page for this document.

---

## Suggested run protocol

Run CC-01 to CC-21 alongside the HR Policy set at production temperature, three passes, recording per-axis scores and p50/p95 latency.

Read the two sets differently. The HR Policy set tells you whether single-document retrieval is sound. This set — specifically CC-14 to CC-17 — tells you whether the system composes across documents, which is the harder property and the one that degrades first when you shrink chunk size or trim reranker depth. If CC-15 starts answering from one document only, that is a fusion regression even when every single-hop item still passes.

Release gate for this set: 100% on CC-20 groundedness, 100% on CC-21 routing, at least 3 of 4 cross-document items surfacing both sources, and no more than two `must_not_include` violations across the remaining items.