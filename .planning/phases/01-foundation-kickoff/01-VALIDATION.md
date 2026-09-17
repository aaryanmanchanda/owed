---
phase: "01"
slug: "foundation-kickoff"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-18"
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (per HANDOFF §10; not yet installed/configured — repo is greenfield) |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/unit -x` (once tests/ scaffold and framework config exist) |
| **Full suite command** | `pytest tests/` |
| **Estimated runtime** | ~1 second (empty scaffold, no real tests yet) |

---

## Sampling Rate

- **After every task commit:** Manual verification (curl the SAM hello-world endpoint; invoke the Bedrock smoke-test Lambda and eyeball the returned JSON against the §7 schema) — no automated quick-run exists yet for this greenfield infra phase.
- **After every plan wave:** Same manual checks; this phase has only one wave's worth of infra work.
- **Before `/gsd-verify-work`:** Both success criteria 1 and 2 (SAM hello-world HTTP 200, Bedrock smoke test valid-schema response) must be manually confirmed working.
- **Max feedback latency:** N/A this phase — verification is manual (curl / lambda invoke), not automated test-suite driven.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-XX | 01 | 1 | SC-1 (SAM hello-world) | — | HTTP 200 from real ap-south-1 endpoint | smoke (manual/curl) | `curl -sf <api-url>/hello` (exit 0 = pass) | ❌ W0 — no test file, deploy-verification not unit test | ⬜ pending |
| 01-01-XX | 01 | 1 | SC-2 / D-05–D-09 (Bedrock smoke test) | — | Lambda returns valid §7-schema JSON from S3-bytes-into-Bedrock call | smoke (manual invoke + schema check) | `aws lambda invoke --function-name <name> --payload '{...}' out.json && python -c "import json; json.load(open('out.json'))"` | ❌ W0 — optional `tests/smoke/test_bedrock_schema.py` if planner wants an automated artifact | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py`, `tests/unit/__init__.py` — empty package scaffold per HANDOFF §11 layout, so Phase 3 has somewhere to add real unit tests without restructuring
- [ ] `requirements-dev.txt` (or equivalent) — pin `pytest` now; defer `moto`/`hypothesis` pins to when Phase 3 needs them
- [ ] Framework install: not strictly needed this phase — no `src/` modules exist yet to test (Phase 3 creates them)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SAM hello-world reachable | SC-1 | Deploy-state verification, not application logic | `sam deploy` then `curl -sf <output ApiUrl>/hello` and confirm HTTP 200 |
| Bedrock smoke-test Lambda returns valid schema | SC-2, D-05–D-09 | Throwaway Lambda per D-06/D-07; accuracy explicitly not graded here (Phase 2's job) — only "did it return the shape without erroring" | Invoke Lambda with a test image key in S3, confirm output JSON has `utr`/`amount_inr`/`screen_time`/`payment_app`/`status_text`/`payee_name`/`notes` keys (nulls allowed), no error |
| Bedrock model access confirmed | SC-2 | AWS console / CLI state check, not code | `aws bedrock list-inference-profiles --region ap-south-1` (or console) confirms an inference profile is usable for the chosen model |
| Test photo set collected | SC-3 | Physical photo-taking task, not testable in CI | Manually count 20-30 photos in the designated fixture directory covering the angle/glare/dim-light/cut-off variations listed in SC-3 |
| Q1-Q5 asked and recorded | SC-4 | Human conversation with the restaurant owner | Confirm `.planning/intel/context.md` open-questions section has been updated with answers or explicit "still open" status |
| Repo skeleton + first commit | SC-5 | Structural/git-state check, not a test | `git log` shows a post-kickoff commit; repo tree matches HANDOFF §11 layout; `docs/DECISIONS.md` has first entries |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < N/A this phase (manual verification)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
