# HR Policy — Chatbot Evaluation Set

**Corpus document:** `HR_Policy.pdf` — Human Resources Policy (A) and Employee Fraud Prevention Policy (B), Asia Asset Finance PLC
**Policy version:** 2025/2026 · Effective 23 June 2025 · Next review 23 June 2026
**Target system:** AAF HRMS AI Assistant (production chatbot)
**Question count:** 20

---

## How to use this set

Each item has a fixed ID so runs can be compared across model/pipeline changes. Grade every response on four axes:

| Axis | What it measures | Scoring |
|---|---|---|
| **Correctness** | All `must_include` facts present and accurate | 0 / 0.5 / 1 |
| **Groundedness** | No claim outside the source document; no invented numbers | 0 / 1 (hard fail on any fabrication) |
| **Citation** | Points to the correct section of the HR Policy | 0 / 1 |
| **Routing** | Correct intent (CHAT / RAG / TOOL / BOTH) | 0 / 1 |

A response containing anything from `must_not_include` is a **fail on that item regardless of other axes** — these are the distractor traps, and they are the ones that catch retrieval pulling an adjacent-but-wrong chunk.

Coverage: 8 single-hop lookups, 5 multi-hop / cross-section, 3 table-and-numeric extraction, 2 entitlement-and-eligibility, 2 robustness (abstention + routing).

---

## Section 1 — Single-hop factual retrieval

### EVAL-01 · Statutory contribution rates
**Intent:** RAG
**Question:** What percentage of my basic salary goes to EPF and ETF, and how much does the company contribute?
**Expected answer:** Company contributes 12% of basic salary to EPF; employee contributes 8% of basic salary. For ETF, the employer contributes 3% of basic salary (no employee contribution).
**Source:** §5.8 Statutory Obligation — EPF & ETF
**must_include:** 12%, 8%, 3%, "basic salary"
**must_not_include:** any employee-side ETF contribution figure

---

### EVAL-02 · Medical scheme limits by grade
**Intent:** RAG
**Question:** What is the maximum medical claim limit per year for each staff category?
**Expected answer:** Senior Management Rs. 350,000; Management Rs. 250,000; Others Rs. 200,000 — per year.
**Source:** §6.4 Company Medical Scheme
**must_include:** all three categories with correct amounts
**must_not_include:** Rs. 25,000 (that is the cataract lens sub-limit), Rs. 1,000 (government non-paying ward per-event rate)
**Note:** This is a table-extraction test. The two sub-limits sit within a few lines of the main table and are the most likely wrong-chunk pull.

---

### EVAL-03 · Late attendance treatment
**Intent:** RAG
**Question:** If I come in one hour late, how is that recorded?
**Expected answer:** Late attendance up to 1.5 hours is treated as short leave. Over 1.5 hours is treated as half a day's leave. One hour late therefore counts as short leave.
**Source:** §10.3 Late Attendance
**must_include:** short leave, the 1.5-hour threshold
**must_not_include:** half day for a one-hour lateness
**Note:** Tests whether the model applies the threshold rather than reciting both rows of the rule.

---

### EVAL-04 · HR help desk contact
**Intent:** RAG
**Question:** What number do I call to raise an HR complaint?
**Expected answer:** The HR Help Desk / Complaints Hotline mobile line is 077 1201866. Calls are logged in a register, assigned to a staff member for action, and the resolution date is recorded.
**Source:** HR Help Desk and Hotline
**must_include:** 077 1201866
**must_not_include:** any other phone number
**Note:** Needle-in-haystack — a single digit string in a 46-page document. Digit-level accuracy is the whole test; a transposed digit is a fail, not a partial.

---

### EVAL-05 · Fuel reimbursement window
**Intent:** RAG
**Question:** When can I submit my fuel bills and where does the money go?
**Expected answer:** Eligible staff submit from the 5th of each month to the 2nd of the following month; the system resets on the 5th with the eligible litres. Approved reimbursements are credited only to the staff member's LuckEwallet account. Requests are processed within 24 working hours, and approval/rejection notifications go to the Zimbra email.
**Source:** §5.3 Fuel Allowance Reimbursement
**must_include:** 5th, 2nd, LuckEwallet
**must_not_include:** credit to a bank/salary account

---

### EVAL-06 · Document metadata
**Intent:** RAG
**Question:** Which version of the HR policy is currently in force and when is it due for review?
**Expected answer:** Version 2025/2026, prepared by the Head of HR and approved by the Board of Directors on 23 June 2025. Effective 23 June 2025; next review on 23 June 2026.
**Source:** Cover page control table
**must_include:** 2025/2026, 23 June 2026
**must_not_include:** 20 June 2024 presented as the effective or approval date
**Note:** The cover table lists "Last Modified on 20th June 2024" — earlier than the approval date. Tests whether the model reads the right row instead of grabbing the nearest date.

---

### EVAL-07 · Post-employment confidentiality
**Intent:** RAG
**Question:** After I leave the company, am I allowed to contact AAF customers for my new job?
**Expected answer:** No. Employees who resign or otherwise cease employment remain bound by their duty of confidentiality and must not use, disclose or exploit customer data, contact details or proprietary information to canvass or solicit business for another organisation, competitor or personal venture. Breach may result in legal action and reputational consequences.
**Source:** Confidentiality and Post-Employment Obligations (§12)
**must_include:** clear "no", the obligation surviving employment
**must_not_include:** a fixed non-compete duration or geographic scope (the policy states none)

---

### EVAL-08 · Attendance amendment authority
**Intent:** RAG
**Question:** My attendance was marked wrong in the HRIS. Who has to approve a correction?
**Expected answer:** Policy adjustments to attendance time in the HRIS are not normally allowed. Where an amendment is needed due to exceptional circumstances, it requires dual approval from the Department Head — explicitly not the immediate superior — and the Head of HR.
**Source:** §10.2 Attendance, point 7
**must_include:** dual approval, Department Head, Head of HR
**must_not_include:** immediate superior as an approver
**Note:** The exclusion is stated in brackets in the source and is easy to drop during chunking.

---

## Section 2 — Multi-hop and cross-section reasoning

### EVAL-09 · Pro-rated annual leave
**Intent:** RAG
**Question:** I joined AAF in August last year. How many days of annual leave am I entitled to this year?
**Expected answer:** A joining date between 1 July and 30 September gives 07 days of annual leave from the second year of service. (Full entitlement is 14 days, applicable to those who join between 1 January and 31 March.)
**Source:** §7 Leave Entitlements — Annual Leave
**must_include:** 7 days, the July–September bracket
**must_not_include:** 14 days as this employee's entitlement, 10 days, 04 days
**Note:** Requires mapping a month to one of four brackets rather than returning the headline figure. The headline "14 days" appears first in the chunk and is the expected failure mode.

---

### EVAL-10 · Probation and medical scheme eligibility
**Intent:** RAG
**Question:** I'm still on probation and my wife was hospitalised. Can I claim under the company medical scheme?
**Expected answer:** No. The scheme is limited to permanent staff, and employees under probation are explicitly not eligible. Once confirmed, the scheme covers the employee, spouse and any number of dependent, unmarried, unemployed children — hospitalisation only, OPD not covered.
**Source:** §6.4 Company Medical Scheme, eligibility criteria 1–2
**must_include:** not eligible while on probation
**must_not_include:** a claim amount or claim procedure presented as available to this employee
**Note:** Tests refusal of the surrounding helpful detail once the gating condition fails.

---

### EVAL-11 · Maximum probation duration
**Intent:** RAG
**Question:** What is the longest my probation can run in total?
**Expected answer:** The probationary period is 6 or 9 months as decided by management at interview, based on the applicant's experience. It may be extended a maximum of three times, each extension not exceeding three months — up to 9 further months. So the maximum total is 18 months (9-month probation plus three 3-month extensions).
**Source:** §4 Probation and Confirmation
**must_include:** 6/9 months base, 3 extensions, 3 months each
**must_not_include:** unlimited or open-ended extension
**Note:** Requires arithmetic over two separate statements. Accept the components even if the model declines to state a single total, but flag responses that imply extensions are unbounded.

---

### EVAL-12 · Resignation access-revocation timeline
**Intent:** RAG
**Question:** When exactly do my system access, e-banking rights and email get cut off after I resign?
**Expected answer:** Three different points. E-banking privileges and cheque-signing authority are blocked on the same day the resignation notice is given. System access is blocked on the date the resignation notice is received, and the employee is transferred to a non-critical area with no system access. The email address is blocked on the last date of employment. HRIS and fingerprint access are removed by the last date. This applies irrespective of any ongoing negotiations with the resignee.
**Source:** §9.2 Resignation Process, points 2–6
**must_include:** distinct timing for e-banking/system access (notice date) versus email (last date)
**must_not_include:** a single blanket cut-off date for all systems
**Note:** The hardest retrieval item in the set — five near-identical "block the X" lines in one chunk. Collapsing them into one date is the failure to watch for.

---

### EVAL-13 · Transfer rules
**Intent:** RAG
**Question:** I've been at the same branch for over three years. What are the rules on transferring me, and will my salary change?
**Expected answer:** An employee remaining in the same branch for three years must be transferred. Job rotation within the branch is possible except for the Branch Manager / In-charge, who must be moved to a different branch. Staff must remain at the transferred branch for at least six months. Salary is not revised on transfer or job rotation; a living or special travelling allowance may be granted at management discretion. Transfers must not lower job status and are communicated in writing. Transfers on business exigency or as punishment cannot be appealed or rejected — rejection is itself misconduct and may lead to termination.
**Source:** §10.8 Transfers
**must_include:** mandatory transfer at 3 years, 6-month minimum, no salary revision
**must_not_include:** any suggestion of a salary increase or a right of appeal on business/punishment transfers

---

### EVAL-14 · Fraud reporting chain
**Intent:** RAG
**Question:** I suspect the Internal Auditor is involved in a fraud. Who do I report it to?
**Expected answer:** Report to the Chairman of the Audit Committee. The normal route is the immediate superior; if that is not appropriate, the Director/Company Operations Division for branches or the Internal Auditor for Head Office divisions. Where the matter involves the Internal Auditor, Compliance Officer, ED/CEO or Sectional Heads, it goes to the Chairman of the Audit Committee.
**Source:** Employee Fraud Prevention Policy — Policy, and Discovery Reporting Procedures
**must_include:** Chairman of the Audit Committee
**must_not_include:** Internal Auditor as the recipient in this scenario
**Note:** The conditional branch must override the default reporting line stated in the same paragraph.

---

## Section 3 — Table and numeric extraction

### EVAL-15 · Negligence penalisation levels
**Intent:** RAG
**Question:** What are the penalty levels for negligence and insubordination?
**Expected answer:** Level 1 — 10% of Performance Allowance. Level 2 — 25% of PA. Level 3 — 50% of PA plus a letter of concern. Level 4 — 100% of PA plus a warning letter. Level 5 — transfer or termination. Levels 4 and 5 are subject to an inquiry. If lapses continue three times irrespective of level, the staff member is called to an immediate meeting with management, followed by a warning letter and termination if required. Fraud results in termination irrespective of the amount.
**Source:** §1.4 Penalisation Mechanism & Action Process
**must_include:** all five levels with correct percentages, inquiry requirement for levels 4–5
**must_not_include:** percentages applied to basic salary rather than the Performance Allowance

---

### EVAL-16 · Target-failure escalation for marketers
**Intent:** RAG
**Question:** What happens to a marketing officer who misses target for three months in a row?
**Expected answer:** A letter of warning, with a meeting conducted by the ED/SGM. The escalation is: first month's failure — letter of notice (meeting with RM); two continuous months — letter of concern (meeting with GM-Operations); three continuous months — letter of warning (meeting with ED/SGM); four continuous months — transfer or termination (meeting with ED/COO). Non-achievement of quarterly targets also draws a letter of warning. Training needs are to be identified during these meetings.
**Source:** Procedure for Failure to Achieve the Target — A. Marketers & ROs
**must_include:** letter of warning at three months, ED/SGM
**must_not_include:** the Branch Manager escalation ladder (a separate table with different triggers, including a fortnightly memo)
**Note:** Two structurally identical tables sit adjacent. Cross-table contamination is the failure mode.

---

### EVAL-17 · Interview panel composition
**Intent:** RAG
**Question:** Who interviews candidates for an Executive-level position?
**Expected answer:** Three stages: first interview with the immediate supervisor / RM / AGM; second with the Head of HR; third with ED-COO, only if the salary exceeds the given limit. Branch-level recruitment up to Executive level is conducted by the regional HR & Admin Officer and the RM, with the recruitment finalised at head office on their recommendation.
**Source:** §2.4 Constitution of Interview Panels — Senior Executive/Executive/Jnr Executive; §2.1.13
**must_include:** the three stages in order, the salary-limit condition on the third
**must_not_include:** Nomination Committee or Board of Directors (those apply to Top Management and Senior Management only)

---

## Section 4 — Entitlement and eligibility rules

### EVAL-18 · Casual leave entitlement and constraints
**Intent:** RAG
**Question:** How many casual leave days do I get in a year, and how many can I take in a row?
**Expected answer:** Seven days of casual leave per calendar year, which may be taken for at most two days running, and must not immediately precede or follow annual leave or sick leave. In the first year of service, probationers are entitled to 1 day for every 2 months of service; the 7-day entitlement applies from the second year of employment.
**Source:** §7 Leave Entitlements — Casual Leave; Entitlement — Probationers
**must_include:** 7 days, 2 consecutive days maximum, the probationer rule
**must_not_include:** casual leave described as permissible immediately before or after annual or sick leave
**Note:** Two-part item. The adjacency constraint sits at the end of a run-on sentence and is the clause most often dropped, and the probationer entitlement is in a separate sub-block from the main rule.

---

### EVAL-19 · Retirement age and post-retirement engagement
**Intent:** RAG
**Question:** What is the retirement age for permanent employees, and can I keep working after that?
**Expected answer:** 60, or as specified under law. On reaching that age the employee retires automatically — ipso facto — whether or not the company communicates the retirement in writing. Depending on business requirements, retired employees may continue on a fixed-term contract basis where management requires it; accepting or rejecting such applications is at management's sole discretion and is final and conclusive.
**Source:** §9.3 Retirement
**must_include:** 60, automatic retirement, fixed-term contract at management discretion
**must_not_include:** a right or entitlement to continue working after 60
**Note:** Pairs with EVAL-10 — staff above 60 are also excluded from the company medical scheme. A model that surfaces both is doing well, but don't require it.

---

## Section 5 — Robustness

### EVAL-20 · Out-of-scope question (abstention test)
**Intent:** RAG → abstain
**Question:** How many days of paternity leave do I get?
**Expected answer:** The HR Policy does not cover paternity leave. The document defines annual leave, casual leave and medical/sick leave only; maternity appears solely as a medical-scheme benefit (100% of the bill up to the category limit for normal and caesarean deliveries), not as a leave entitlement. The assistant should say the policy does not address paternity leave and direct the employee to HR.
**Source:** §7 Leave Entitlements (absence of provision); §6.4 criterion 9 for the maternity contrast
**must_include:** explicit statement that the policy does not cover this, referral to HR
**must_not_include:** any invented number of days, any figure borrowed from casual or annual leave, Sri Lankan statutory provisions presented as AAF policy
**Note:** The single most important item in the set. A confident fabricated number here should block release regardless of the aggregate score — the NLI groundedness gate is what this question exists to exercise.

---

### EVAL-21 · Personal-data query (routing test)
**Intent:** TOOL (or BOTH), not RAG
**Question:** How many casual leave days do I have left this year?
**Expected answer:** Routes to the leave-balance workflow tool and returns the authenticated user's actual remaining balance. If the tool is unavailable, the assistant should say the balance must come from the HRIS rather than answering from the policy. A policy-only answer of "7 days" is wrong — that is the annual entitlement, not this employee's balance.
**Source:** N/A — workflow endpoint, not the policy document
**must_include:** a live balance, or an explicit statement that a live lookup is needed
**must_not_include:** "7 days" presented as the user's remaining balance
**Note:** Numbered 21 so the twenty graded items keep stable IDs; treat this as the routing control. Retrieval similarity to EVAL-18 is high, which is exactly why it belongs in the set — the router must split them on intent, not on content overlap.

---

## Known document quirks affecting grading

These are artefacts of the source PDF, not model errors. Don't penalise the chatbot for them, but watch for answers that inherit the confusion:

1. **Section numbering breaks.** Retirement and Resignation is headed "8" but its subsections are numbered 9.1, 9.2, 9.3. A model citing "§8" or "§9.1" for resignation is equally correct.
2. **Duplicated attendance register clause.** §10.5 and §10.6 are near-identical, with §10.6 adding the out-of-branch marking rule. Retrieval may return either; only the missing out-of-branch sentence should cost a point.
3. **Cover-page date inconsistency.** "Last Modified on 20th June 2024" predates the 23 June 2025 approval. Covered by EVAL-06.
4. **Recruitment numbering.** §2.1 jumps from 2.1.1 to 1.1.1 onwards. Citation to either form is acceptable.
5. **Medical scheme criteria** contain two items numbered 8. Cataract and government-ward provisions may both cite "criterion 8".
6. **Interview panel tables** for Senior Executive/Executive appear twice, at the bottom of one page and the top of the next. Duplicate retrieval here is a chunking artefact, not a hallucination.

---

## Suggested run protocol

Run all 21 items three times at your production temperature and record per-axis scores, plus p50/p95 latency per item. The multi-hop items (EVAL-09 to EVAL-14) are the ones that should move when you change retrieval — reranker depth, RRF weighting, chunk size. The single-hop items should stay flat; if they move, the regression is in the ingestion pipeline, not the generation model.

Suggested release gate: 100% on EVAL-20 groundedness, 100% on EVAL-21 routing, and no more than two `must_not_include` violations across the remaining nineteen.