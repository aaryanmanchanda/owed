# Roadmap: owed

## Overview

A 3.5-day solo hackathon build (kickoff Thu 2026-09-17, submit-by Sun 2026-09-20). The five phases below are a direct, structurally-enforced mapping of HANDOFF.md §13's day-by-day timeline — each phase is a hard prerequisite gate for the next, not just a suggestion:

Foundation proves the AWS plumbing works and gets the two open-question blockers moving (Thu) → the Bedrock extraction evaluation is run and written up *before* anything is built on top of it (Fri morning) → the parser, pure verdict engine, and Step Functions pipeline are built and proven end-to-end from the CLI (Fri afternoon/night) → the frontend, resolve flow, and a rough submission go live with the video recorded (Sat) → the README, writeup, and AI-tools disclosure are finished and the entry is submitted before the deadline (Sun). Phases 1 and 2 are infrastructure/evaluation gates with no direct REQ-ID (see REQUIREMENTS.md note); Phases 3-5 carry all 8 v1 requirements.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation & Kickoff** - Repo, AWS plumbing, Bedrock access, and test data all proven working; Q1-Q5 asked
- [ ] **Phase 2: Bedrock Extraction Evaluation** - Measure real extraction accuracy/cost before building the reconcile engine on top of it
- [ ] **Phase 3: Parser, Reconcile Engine & Step Functions** - A full shift reconciles end-to-end from the CLI, verdict engine pure and tested
- [ ] **Phase 4: Frontend, Resolve Flow & Rough Submission** - Live mobile URL, one-tap resolve, rough submission, video recorded
- [ ] **Phase 5: Deliverables & Final Submission** - README, writeup, AI tools list finished; submitted before deadline

## Phase Details

### Phase 1: Foundation & Kickoff

**Goal**: The AWS plumbing is proven end-to-end, the two build-blocking open questions are in motion, and real (non-fabricated) test data exists — so nothing downstream is guessing.
**Depends on**: Nothing (first phase)
**Requirements**: None (infrastructure-enabling gate — see REQUIREMENTS.md Traceability note). Supports the repo-integrity, data-handling, and architecture decisions in PROJECT.md Key Decisions.
**Success Criteria** (what must be TRUE):

  1. A SAM "hello world" deployed to ap-south-1 returns HTTP 200 from a real endpoint.
  2. Bedrock model access in ap-south-1 is confirmed (or the nearest available inference profile is identified and the region trade-off noted for the writeup).
  3. 20-30 test photos of Aaryan's own UPI payments exist (straight-on, ~30° angle, glare, dim light, partly cut off; GPay/PhonePe/Paytm), plus a fixture built from Aaryan's own transaction export for parser development — no real customer data, no fake-screenshot generators, anywhere.
  4. Q1-Q5 have been asked of the restaurant owner; whatever is answered (or still open) is recorded in `.planning/intel/context.md`'s open-questions status, not silently assumed.
  5. Repo exists with a first commit made after kickoff, matching the HANDOFF §11 layout skeleton, with `docs/DECISIONS.md` started (first entries logged per PROJECT.md Working Rule 6).

**Plans**: 3 plans

Plans:
**Wave 1**

- [ ] 01-01-PLAN.md — Wave 1. AWS toolchain + new-account credentials checkpoint, then the tracer: SAM hello-world deployed to ap-south-1 returning HTTP 200, plus the HANDOFF §11 repo skeleton and `docs/DECISIONS.md` (SC-1, SC-5)

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 01-02-PLAN.md — Wave 2. Resolve the exact ap-south-1 Bedrock inference profile, deploy the throwaway S3-bytes-into-Bedrock smoke-test Lambda with least-privilege IAM, invoke it and validate the §7 schema, record the processing region (SC-2, D-05–D-09)
- [ ] 01-03-PLAN.md — Wave 2. Capture the 20-30 real test photos + transaction export, ask Q1–Q5 and close the HANDOFF §14 logistics items, build the scrubbed credits fixture and record every answer (SC-3, SC-4)

### Phase 2: Bedrock Extraction Evaluation

**Goal**: Know, with real measured numbers and before any reconcile-engine code is written on top of it, whether Bedrock vision extraction is accurate enough — and which model to use.
**Depends on**: Phase 1
**Requirements**: None directly (validates the Bedrock extraction evaluation protocol and per-photo extraction schema constraints that Phase 3 depends on).
**Success Criteria** (what must be TRUE):

  1. Two Bedrock vision models (one cheaper, one stronger, both available via ap-south-1) plus Amazon Rekognition text detection (baseline) have each been run against the ~30-photo test set from Phase 1, using the AWS `ocr-with-aws-ai-services` sample or an equivalent credited harness.
  2. Per photo × model results (UTR exact match, amount correct, null rate, confident-wrong-UTR rate, latency, approximate cost) are written to `docs/extraction-eval.md` with only real, measured numbers — never invented ones.
  3. A model is chosen for the extraction Lambda; the pitch's "reads angled/glare photos" claim is explicitly kept (evidence-backed) or dropped based on the measured pass criteria (amounts nearly always correct; confident-wrong-UTRs near zero).
  4. The actual processing region/inference-profile used is recorded, with any APAC/global (non-India-only) routing disclosed as a deliberate data-residency trade-off.

**Plans**: TBD

Plans:

- [ ] 02-01: TBD

### Phase 3: Parser, Reconcile Engine & Step Functions

**Goal**: A full shift reconciles end-to-end from the CLI, with the verdict engine pure, fully unit-tested, and exactly matching the locked §7 rule table before any more AWS is wired around it.
**Depends on**: Phase 2 (model chosen)
**Requirements**: REQ-shift-creation, REQ-photo-and-record-upload, REQ-reconciliation-run, REQ-per-rider-results, REQ-shift-level-results
**Success Criteria** (what must be TRUE):

  1. A shift can be created, and its photos + payment record uploaded via presigned URLs, and a reconciliation run triggered — all callable from the CLI (`POST /shifts`, `POST /shifts/{id}/uploads`, `POST /shifts/{id}/run`), running the full ParseRecord → ExtractPhotos → Reconcile → Finalize Step Functions execution.
  2. `GET /shifts/{id}` returns, per rider, the verified UPI total, flagged photos grouped by verdict reason, duplicates with the earlier claim's source, and a cash-owed range/number — plus shift-level unclaimed credits.
  3. The parser is written behind an interface; if Q1 is still unanswered, it's implemented and tested only against the fixture built from Aaryan's own transaction export (never a second real format).
  4. Every §7 verdict (`NOT_SUCCESS`, `UNREADABLE`, `DUPLICATE`, `VERIFIED`, `AMOUNT_MISMATCH`, `PROBABLE`, `AMBIGUOUS`, `NOT_FOUND`, `UNCLAIMED_CREDIT`) has a passing unit test using hand-written fixtures (no Bedrock calls in unit tests), including the misread-safety (fabricated-UTR → PROBABLE/AMBIGUOUS, never NOT_FOUND), idempotent-re-run, same-bytes-twice, cash-owed-range, and deterministic-ordering tests.
  5. A concurrency test against DynamoDB Local (or a test table) with N parallel workers claiming the same UTR shows exactly one winner, and reconciling the same shift twice from the CLI gives identical verdicts with no self-duplicate claims.

**Plans**: TBD

Plans:

- [ ] 03-01: TBD

### Phase 4: Frontend, Resolve Flow & Rough Submission

**Goal**: The owner can run the whole flow by hand on a phone, resolve flagged photos with one tap, and a rough version is submitted with the demo video already recorded — de-risking Sunday.
**Depends on**: Phase 3
**Requirements**: REQ-resolve-flow, REQ-frontend
**UI hint**: yes
**Success Criteria** (what must be TRUE):

  1. A live Amplify-hosted URL (branch password protected, no Cognito) works on a phone, covering all four steps in one mobile-first page: create shift, upload photos + payment record, run, results.
  2. The results screen shows, per rider, a card with cash owed and a "check these" list with photo thumbnails, using big tap targets and labels in both Tamil and English — Tamil strings reviewed by a native speaker, not unreviewed machine translation.
  3. The owner can confirm/reject a `PROBABLE` verdict, or pick a candidate for an `AMBIGUOUS` verdict, with one tap (`POST /shifts/{id}/photos/{photo_id}/resolve`); rejecting a `PROBABLE` releases the claimed credit back to unclaimed.
  4. A rough version of the repo is submitted (early submission per event rules — editable until the deadline).
  5. The ≤3:00 demo video is recorded (Saturday night, not left to Sunday) following the HANDOFF §12 timed structure, showing AWS on screen (Step Functions execution graph, DynamoDB duplicate-claim item, Bedrock extraction output) and the concurrency test passing live on screen.

**Plans**: TBD

Plans:

- [ ] 04-01: TBD

### Phase 5: Deliverables & Final Submission

**Goal**: The README, writeup, and AI-tools disclosure meet every HANDOFF §12 deliverable requirement, and the entry is submitted well before the confirmed Sunday deadline.
**Depends on**: Phase 4
**Requirements**: REQ-deliverables
**Success Criteria** (what must be TRUE):

  1. `README.md` (design-doc style) covers, in order, all 11 HANDOFF §12 sections: the problem, what it does, architecture diagram + why each service, verdict rules and why the model never decides, exactly-once design, extraction evaluation results (real numbers from Phase 2), cost decisions, deferred decisions (Cognito, single format, single tenant, data residency), what was learned (only genuinely new: Bedrock multimodal, Step Functions/Map, DynamoDB conditional writes, SAM, Amplify — not S3/CloudFront/EC2), prior art and how this differs, and AI tools used.
  2. `docs/AI_TOOLS.md` and `docs/DECISIONS.md` are complete and current, covering every decision made across all five phases.
  3. The writeup contains the full pitch (§3, with Q4's real detail if answered), the README highlights, and the AI tools list.
  4. The exact Sunday submission deadline has been confirmed from the event page (open item since Phase 1), and the public repo + video + writeup are all submitted before it, satisfying every HANDOFF §12 deliverable and every §15 session rule (small atomic commits, no squashed/backdated history, no copied code, no real customer data, no fake-screenshot generators, decisions logged) — this, not interview/prize selection, is the completion criterion.

**Plans**: TBD

Plans:

- [ ] 05-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Kickoff | 0/3 | Planned | - |
| 2. Bedrock Extraction Evaluation | 0/TBD | Not started | - |
| 3. Parser, Reconcile Engine & Step Functions | 0/TBD | Not started | - |
| 4. Frontend, Resolve Flow & Rough Submission | 0/TBD | Not started | - |
| 5. Deliverables & Final Submission | 0/TBD | Not started | - |
