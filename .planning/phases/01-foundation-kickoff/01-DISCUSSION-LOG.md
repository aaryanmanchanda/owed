# Phase 1: Foundation & Kickoff - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-18
**Phase:** 1-Foundation & Kickoff
**Areas discussed:** Bedrock risk retirement depth (plus two unplanned blockers surfaced mid-discussion: timeline reality check, AWS account suspension)

---

## Gray area selection

Presented 4 candidate areas: Bedrock risk retirement depth, Repo visibility during build, Day-1 repo skeleton scope, Q1-Q5 owner outreach. User selected only **Bedrock risk retirement depth**, with a free-text note: "let's add the smoke test to day 1. it's already sunday so we need momentum."

---

## Timeline reality check (surfaced mid-discussion)

The user's "it's already sunday" claim contradicted the system clock (2026-09-18, a Friday per HANDOFF.md's own Thu-kickoff dating). Stopped to clarify rather than silently trust either source.

| Option | Description | Selected |
|--------|-------------|----------|
| Friday (system date is right) | Today is 2026-09-18, day 2 of 4. Phase 1 (Thu work) is a day behind, not on a same-day deadline. | ✓ |
| Sunday (deadline is today) | Real calendar day is the Sunday deadline; roadmap would need emergency replanning. | |

**User's choice:** Friday (system date is right).
**Notes:** "Need momentum" was urgency about being a day behind, not a literal same-day deadline. No replan needed; recorded as D-01 in CONTEXT.md.

---

## Bedrock risk retirement depth

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal (access/quota check only) | Just confirm the model is listed and quota exists. | |
| Smoke test (Lambda → S3 → Bedrock) | One real invocation through the exact risky path, proving IAM + plumbing works, without building Phase 2's evaluation. | ✓ (user's initial free-text answer) |
| Full extraction Lambda now | Would encroach into Phase 2/3 scope. | |

**User's choice:** Smoke test — added explicitly via free text before the formal options were even presented.

### Follow-up: pass bar

| Option | Description | Selected |
|--------|-------------|----------|
| Valid schema response | Lambda returns the §7 JSON shape without erroring; accuracy not graded here. | ✓ |
| Correct extraction on a known photo | Also requires getting UTR/amount right on one photo — risks conflating with Phase 2's real evaluation. | |

**User's choice:** Valid schema response.

### Follow-up: model choice

| Option | Description | Selected |
|--------|-------------|----------|
| Whichever grants access fastest | Don't spend Day 1 comparing models — that's Phase 2's job. | ✓ |
| The stronger candidate specifically | More confidence it'll work, defers cost/accuracy tradeoff to Phase 2. | |

**User's choice:** Whichever grants access fastest.

---

## AWS account blocker (surfaced mid-discussion)

When asked to continue or wrap up, the user instead revealed: "actually i'm yet to receive the 100USD of aws credits promised by the hackathon, let's make phase 1 all stuff we can do without the credits." Follow-up clarified this was actually a **suspended account**, not just a missing credit.

### What's blocked

| Option | Description | Selected |
|--------|-------------|----------|
| No billing on the account at all | Nothing that costs money can run, including free-tier resources. | |
| Billing works, avoiding spend on principle | A few cents for the smoke test would be fine. | |

**User's choice:** Neither cleanly — actual answer was "my account got suspended because i didn't upgrade to a paid plan for a while after my free trial ended." Recorded as D-02: this is a full deployment blocker, not a spend-avoidance preference.

### Resolution timeline

| Option | Description | Selected |
|--------|-------------|----------|
| Reactivating this account | Fast once payment clears, but ETA not fully controllable. | |
| New AWS account instead | Fresh account, but re-do IAM/region setup. | |
| Unresolved / waiting to hear back | No firm ETA yet. | ✓ |

**User's choice:** Unresolved / waiting to hear back.

### Meanwhile

| Option | Description | Selected |
|--------|-------------|----------|
| Do the non-AWS work now | Repo skeleton, first commit, docs/DECISIONS.md, test photos, Q1-Q5 outreach proceed regardless; AWS-gated criteria become a gated sub-track. | ✓ |
| Hold everything until AWS access is back | Don't start Phase 1 work at all. | |

**User's choice:** Do the non-AWS work now.

---

## Claude's Discretion

- Exact mechanics/timing of contacting Hotel Brindhavan's owner for Q1-Q5.
- Specific wording of the first `docs/DECISIONS.md` entries.
- Day-1 repo skeleton scope (full HANDOFF §11 layout vs. minimal) — surfaced as a candidate gray area, not selected for discussion.
- Repo visibility during build (public vs. private until near submission) — surfaced as a candidate gray area, not selected for discussion.

## Deferred Ideas

- Day-1 repo skeleton scope and repo visibility during build were presented as selectable areas but the user chose not to discuss them this round — left open for the planner or a future discuss-phase pass, not lost.
