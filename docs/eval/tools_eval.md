# Tool Call Evaluation Set — Astrynox AI

Evaluation questions for validating accuracy and truthfulness of tool-based responses in production.
Each question is tied to a specific tool and includes what a correct answer **must** contain and what constitutes a **failure**.

> **How to use:** Run each question against the production bot using a logged-in employee account. Compare the bot's response against the HRIS source data for that employee. Mark Pass / Fail in the last column.

---

## Tool: `get_leave_balance`

### Q1 — Annual leave remaining
**Question:** How many annual leave days do I have left?

- **Must contain:** The exact number of available annual leave days from the HRIS.
- **Must not:** Invent a number, say "14 days" without checking actual balance, or confuse annual with casual leave.
- **Failure case:** Bot says "You have 14 days" when the employee has already used some.

---

### Q2 — Specific leave type balance
**Question:** What is my casual leave balance for this year?

- **Must contain:** Eligible, used, pending, and available figures for casual leave.
- **Must not:** Omit pending leave or present only the eligible entitlement as if none was used.
- **Failure case:** Bot reports eligible (7) instead of available (e.g. 1 after 6 used).

---

### Q3 — Medical leave inquiry
**Question:** Do I have any medical leave days remaining?

- **Must contain:** A clear yes/no with the exact available medical leave figure.
- **Must not:** Give a generic policy answer ("Medical leave is 7 days per year") instead of the employee's actual balance.
- **Failure case:** Bot answers from policy context instead of calling the tool.

---

### Q4 — Short leave availability
**Question:** Can I take a short leave today? How many do I have left this month?

- **Must contain:** The monthly short leave available count from HRIS data.
- **Must not:** Confuse monthly entitlement with yearly, or omit the period (monthly vs yearly).
- **Failure case:** Bot mixes up summary_period and presents monthly leave as annual.

---

### Q5 — All leave types summary
**Question:** Give me a summary of all my leave balances.

- **Must contain:** All leave types returned by the API listed clearly — annual, casual, medical, short leave at minimum.
- **Must not:** Omit any leave type returned in the payload, or add leave types not present in the data.
- **Failure case:** Bot only mentions annual and casual, skips medical and short leave.

---

### Q6 — Leave already used
**Question:** How many casual leave days have I used so far this year?

- **Must contain:** The exact `used` value for casual leave from the HRIS.
- **Must not:** Say "0 days used" if the employee has used leave, or confuse used with pending.
- **Failure case:** Bot says "You haven't used any casual leave" when `used` is 6.

---

### Q7 — Pending leave impact
**Question:** I have a leave application pending. Does that affect my available balance?

- **Must contain:** The `pending` leave count and an explanation that pending leave reduces the available count.
- **Must not:** Ignore the pending field or claim pending leaves do not affect available balance.
- **Failure case:** Bot says available is 14 when pending is 2 and available is actually 12.

---

## Tool: `get_attendance_timeline`

### Q8 — Recent absence check
**Question:** Was I marked absent or late in the last two weeks?

- **Must contain:** A factual account of actual attendance statuses from the timeline — present, absent, or late entries only for the past 14 days.
- **Must not:** Include future dates, or claim "all present" when there are absent/late records.
- **Failure case:** Bot summarises future planned days as past attendance.

> **Note:** The timeline covers the last 30 days only. Questions asking about more than 30 days ago should be answered with "that data is not available in the current window."

---

### Q9 — Check-in time for a specific day
**Question:** What time did I check in last Monday?

- **Must contain:** The exact `in_time` for last Monday from the timeline (or "no record" if the day was a holiday/leave).
- **Must not:** Hallucinate a time, give today's time, or say "no data" when a record exists.
- **Failure case:** Bot says "07:49" when last Monday's `final_in_time` was null (holiday).

---

### Q10 — Total days worked in the window
**Question:** How many days have I worked in the past 30 days?

- **Must contain:** A count of days where `status` is "Present" (or equivalent) in the timeline.
- **Must not:** Count holidays, weekends, or leave days as worked days. Must not claim to cover 60 days — the window is 30 days.
- **Failure case:** Bot counts all calendar days instead of only present days.

---

### Q11 — Hours worked on a specific day
**Question:** How many hours did I work last Friday?

- **Must contain:** The `worked_minutes` for last Friday converted to hours and minutes (e.g. "9 hours 25 minutes").
- **Must not:** Make up a duration or report minutes as hours.
- **Failure case:** Bot says "565 hours" instead of "9 hours 25 minutes".

---

### Q12 — Manual attendance eligibility
**Question:** Are there any days where I can apply for manual attendance correction?

- **Must contain:** The specific dates where `can_apply_manual` is true, or "none" if all are false.
- **Must not:** Say "yes you can" generically without identifying the specific dates.
- **Failure case:** Bot says "you can apply for any past working day" — this is policy, not HRIS data.

---

### Q13 — Leave days in the period
**Question:** Which days was I on leave in the past 30 days?

- **Must contain:** The specific dates where `leave` is not null in the timeline, with the leave category name.
- **Must not:** Count holidays or weekends as leave days, or answer from `get_leave_balance` (that tool shows totals, not specific dates).
- **Failure case:** Bot calls `get_leave_balance` and says "You have used 6 casual leave days" instead of listing the actual dates from the timeline.

---

### Q14 — Attendance on a public holiday
**Question:** Was I marked as working on any holiday in my attendance records?

- **Must contain:** Identify the holiday date(s) from the timeline (`holiday` field not null) and report `is_working_day` for that date.
- **Must not:** Give a generic policy answer about public holidays.
- **Failure case:** Bot answers "No, public holidays are non-working days" without checking the actual record. Or router classifies as RAG because the word "holiday" triggers a policy search.

---

### Q15 — Late arrival pattern
**Question:** Have I been late to work more than once this month?

- **Must contain:** Count of days this month where status indicates late arrival, based on timeline data.
- **Must not:** Claim "no late arrivals" without checking, or count days with no in_time record as late.
- **Failure case:** Bot says "I don't have that information" when the timeline clearly has status data.

---

## Tool: `get_employee_details`

### Q16 — Supervisor name
**Question:** Who is my direct supervisor?

- **Must contain:** The exact `supervisor` name from the HRIS office profile.
- **Must not:** Name anyone not in the data, or say "I don't know your supervisor".
- **Failure case:** Bot names a different person or a department head instead of the direct supervisor.

---

### Q17 — Department and designation
**Question:** What is my job title and which department do I belong to?

- **Must contain:** Both `designation` and `department` exactly as in the HRIS — including any leading/trailing spaces stripped (e.g. "Executive - Digital Products", not " Executive - Digital Products").
- **Must not:** Paraphrase or abbreviate the designation.
- **Failure case:** Bot trims the designation incorrectly and shows a partial title.

---

### Q18 — EPF number
**Question:** What is my EPF number?

- **Must contain:** The exact `epf_no` value from the office profile.
- **Must not:** Confuse EPF with MSL number, or fabricate a number.
- **Failure case:** Bot returns the MSL number instead of the EPF number.

---

### Q19 — Join date
**Question:** When did I join Asia Asset Finance?

- **Must contain:** The `join_date` formatted as a readable date (date portion only, no time component).
- **Must not:** Include the time `00:00:00` in the response, or guess a date.
- **Failure case:** Bot says "2024-03-14 00:00:00" instead of "14 March 2024".

---

### Q20 — Employment type and grade
**Question:** Am I a permanent employee? What grade am I?

- **Must contain:** Both `employment_type` (e.g. "PERMANENT") and `grade` (e.g. "Executive") from the HRIS.
- **Must not:** Answer based on policy context ("permanent employees are entitled to...") without confirming the employee's actual category from the data.
- **Failure case:** Bot gives a policy explanation about permanent employment without confirming the user's actual employment type.

---

## Scoring Guide

| Result | Criteria |
|---|---|
| ✅ Pass | Response matches HRIS data exactly; no hallucinated figures; correct tool triggered |
| ⚠️ Partial | Correct tool triggered but response omits a required field or reformats data incorrectly |
| ❌ Fail | Wrong tool triggered, hallucinated data, policy answer instead of live data, or tool not called at all |

**Target:** ≥ 18/20 Pass for production readiness.
