# Phase 1: Foundation & Kickoff - Context

**Gathered:** 2026-09-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove the AWS plumbing works end-to-end, get the two build-blocking open questions (Q1-Q5) in motion with Hotel Brindhavan's owner, and produce real (non-fabricated) test data — so nothing downstream is guessing. This is an infrastructure/evaluation-enabling gate (no REQ-IDs map to it; see REQUIREMENTS.md Traceability note). No new capabilities are in scope here — only what ROADMAP.md's Phase 1 success criteria already define.

</domain>

<decisions>
## Implementation Decisions

### Timeline reality check
- **D-01:** Today is confirmed **Friday 2026-09-18** (day 2 of the hackathon), not Sunday. HANDOFF.md's Thu/Fri/Sat/Sun phase mapping still holds; Phase 1 (originally "Thursday") is starting a day behind schedule, not on a compressed same-day deadline. "We need momentum" reflects urgency from being a day behind, not a calendar emergency. — **Reversibility:** reversible

### AWS account blocker (new — not in original HANDOFF.md) — RESOLVED 2026-09-18
- **D-02:** Aaryan's original AWS account was **suspended** (unpaid balance after a free-trial period ended) — not merely short on the promised $100 hackathon credit. This was a hard blocker: nothing could be deployed, including free-tier-eligible resources, until an account was usable.
- **D-03 (RESOLVED):** Aaryan provisioned a **new AWS free-tier account under a different email** on 2026-09-18. The AWS-dependent success criteria are no longer gated — they can proceed on the new account. Two follow-on items to verify, not yet confirmed:
  - Whether Builder Center student verification (HANDOFF §14) needs to be redone under the new account's email.
  - Whether the new account is eligible for the hackathon's $100 AWS credit, or whether Phase 2's evaluation costs come out of free-tier/personal spend instead.
- **D-04 (superseded by resolution):** Phase 1 no longer needs to sequence AWS-dependent work after non-AWS work — both tracks can proceed in parallel now that an account exists. Still worth doing the non-AWS work (repo skeleton, `docs/DECISIONS.md`, test photos, Q1-Q5 outreach) without waiting on AWS console access, since Bedrock model access approval on a brand-new account may not be instant. — **Reversibility:** reversible

### Bedrock risk retirement (Day 1 smoke test)
- **D-05:** Add a **Bedrock smoke test to Phase 1** (originally Phase 1 only required confirming *access*, not a real invocation). This retires HANDOFF §13 risk #2 (IAM + passing S3 image bytes into Bedrock inside Step Functions is the steepest learning curve) a day early, without building Phase 2's real evaluation harness.
- **D-06:** The smoke test must exercise the **exact risky path**: a Lambda reads image bytes from S3 and calls Bedrock directly — never Step Functions' direct Bedrock integration for images (HANDOFF's explicit warning). This is a throwaway/minimal Lambda, not the real `extract/` module — Phase 3 builds the production extraction Lambda.
- **D-07:** **Pass bar = valid schema response.** The Lambda must return the §7 extraction JSON shape (`utr`/`amount_inr`/`screen_time`/`payment_app`/`status_text`/`payee_name`/`notes`, nulls allowed) without erroring. Accuracy is explicitly NOT graded here — that is Phase 2's job with the real ~30-photo test set and both candidate models compared. Do not conflate this smoke test with Phase 2's evaluation. — **Reversibility:** reversible
- **D-08:** **Model choice for the smoke test = whichever of the two Bedrock candidates (one cheaper, one stronger) grants inference access first in ap-south-1.** Do not spend Day 1 time comparing them — that comparison is Phase 2's job. — **Reversibility:** reversible
- **D-09:** This smoke test is gated by D-02/D-03 (AWS account suspension) — it cannot run until the account is reactivated, regardless of how quickly the Lambda code itself is ready.

### Claude's Discretion
- Exact mechanics of contacting Hotel Brindhavan's owner for Q1-Q5 (in person vs. message) and the specific first `docs/DECISIONS.md` entries were not decided in this discussion — proceed with reasonable defaults (in person, since Aaryan lives in the delivery building) and log the actual answers/non-answers as they come in.
- Day-1 repo skeleton scope (full HANDOFF §11 layout now vs. minimal-now-grow-later) and repo visibility during build (public from commit 1 vs. private until near submission) were surfaced as gray areas but not discussed — default to whatever the planner judges best; these are low-stakes/reversible choices.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Primary source
- `HANDOFF.md` §7 — per-photo extraction output schema (the exact JSON shape the smoke test's Lambda must return)
- `HANDOFF.md` §8 — Bedrock extraction test plan (candidate models, harness, what Phase 2 measures — the smoke test must not duplicate or shortcut this)
- `HANDOFF.md` §9 — locked architecture (region ap-south-1, Python, SAM; "call Bedrock from a Lambda, don't use Step Functions' direct Bedrock integration for images" — the constraint the smoke test is designed to satisfy)
- `HANDOFF.md` §13 — timeline and risk list (risk #1: Bedrock access/region/quota surprises; risk #2: IAM + S3-bytes-into-Bedrock plumbing — both of which this phase's decisions directly target)
- `HANDOFF.md` §14 — status checklist (Q1-Q5, deadline time, Builder Center verification — all still unresolved)

### Planning artifacts
- `.planning/PROJECT.md` — Key Decisions (locked), Constraints, Working Rules (§15 session rules apply to every phase including this one)
- `.planning/ROADMAP.md` Phase 1 section — the five original success criteria this context refines (smoke test is an addition, not a replacement)
- `.planning/STATE.md` — Blockers/Concerns section; **must be updated with the AWS account suspension (D-02/D-03) as a new active blocker**, since it did not exist when STATE.md was first written from the HANDOFF ingest

No other external specs — requirements fully captured in decisions above and in PROJECT.md/ROADMAP.md.

</canonical_refs>

<code_context>
## Existing Code Insights

Repo is empty except `HANDOFF.md` and `.planning/` — this is Phase 1 of a brand-new project. No existing code, patterns, or maps to scout (`.planning/codebase/` does not exist yet).

### Reusable Assets
None yet.

### Established Patterns
None yet — HANDOFF.md §11's suggested repo layout is the only structural precedent, not yet materialized on disk.

### Integration Points
None yet.

</code_context>

<specifics>
## Specific Ideas

- The Bedrock smoke test is a genuinely new idea introduced in this discussion, motivated by wanting extra momentum on a day-2 start: prove the single riskiest technical path (Lambda → S3 → Bedrock) works, cheaply and early, before Phase 2's real evaluation and before Phase 3's real extraction Lambda depend on it working.
- The AWS account suspension is a live, unresolved, real-world blocker discovered mid-discussion — it is not hypothetical and should be treated as the most urgent open item in STATE.md, above even Q1-Q5.

</specifics>

<deferred>
## Deferred Ideas

- **Repo visibility during build** (public from commit 1 vs. private until near submission) — surfaced but not discussed; left to planner/Claude's discretion, not a phase-domain concept worth its own phase.
- **Day-1 repo skeleton scope** (full HANDOFF §11 layout vs. minimal) — surfaced but not discussed; left to planner/Claude's discretion.
- **Q1-Q5 owner outreach mechanics/timing** — surfaced but not discussed; the underlying requirement (ask Q1-Q5, record answers or non-answers) is already locked in ROADMAP.md success criterion 4 and does not need a phase change, just execution.

### Reviewed Todos (not folded)
None — no pending todos existed to cross-reference.

</deferred>

---

*Phase: 1-Foundation & Kickoff*
*Context gathered: 2026-09-18*
