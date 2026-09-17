# Requirements: owed

**Defined:** 2026-09-18
**Core Value:** The cash-owed number for every rider is always correct and never a false accusation — a vision model only extracts fields; deterministic code decides every verdict.

## v1 Requirements

Requirements for the hackathon submission (the only release — there is no v2 cycle for this event). Each maps to exactly one roadmap phase. Sourced from `HANDOFF.md` §3/§6/§9/§12 via `.planning/intel/requirements.md`.

### Shift & Data Intake

- [ ] **REQ-shift-creation**: Owner/cashier creates a shift by entering, for each rider on that shift, a name and the rider's total order value for the shift (entered by hand).
  - Acceptance: `POST /shifts` accepts `{business_id, date, riders:[{name, order_total}]}` and creates a shift record.
- [ ] **REQ-photo-and-record-upload**: Owner/cashier uploads each rider's payment-screen photos and the day's/shift's payment record.
  - Acceptance: `POST /shifts/{id}/uploads` returns presigned PUT URLs for photos (tagged by rider) and for the payment record; uploads go to S3 at `uploads/{shift_id}/record/{filename}` and `uploads/{shift_id}/photos/{rider}/{photo_id}.jpg` (public access blocked, SSE on, lifecycle expiry set).
- [ ] **REQ-reconciliation-run**: Owner/cashier triggers reconciliation processing for the uploaded shift.
  - Acceptance: `POST /shifts/{id}/run` starts the Step Functions execution (ParseRecord → ExtractPhotos → Reconcile → Finalize); the operation is idempotent per upload set — re-running with the same uploads does not duplicate work or claims (a claim already owned by the same `photo_id` counts as success, not a duplicate).

### Results & Resolution

- [ ] **REQ-per-rider-results**: For each rider, the tool shows verified UPI payments and their total; photos that need checking, grouped by verdict reason; duplicates, with where the earlier claim came from; and the cash that rider owes.
  - Acceptance: cash owed = order total − verified UPI − UPI confirmed by the owner. While anything is unresolved, show a range: "owes ₹X, or ₹Y if the flagged payments are genuine." Range collapses to one number once all flagged items are resolved. Every §7 verdict (`NOT_SUCCESS`, `UNREADABLE`, `DUPLICATE`, `VERIFIED`, `AMOUNT_MISMATCH`, `PROBABLE`, `AMBIGUOUS`, `NOT_FOUND`) must be represented correctly per the locked rule table (see PROJECT.md Constraints / Key Decisions — never reinterpret without asking).
- [ ] **REQ-shift-level-results**: For the whole shift, show unclaimed credits — money that arrived with no matching photo.
  - Acceptance: `GET /shifts/{id}` response includes an unclaimed-credits list for the shift alongside per-rider results.
- [ ] **REQ-resolve-flow**: Owner can confirm or reject a `PROBABLE` verdict, or pick one candidate for an `AMBIGUOUS` verdict.
  - Acceptance: `POST /shifts/{id}/photos/{photo_id}/resolve` accepts a confirm/reject (PROBABLE) or a selection among candidates (AMBIGUOUS); rejecting a PROBABLE match releases the claimed candidate credit.

### Frontend

- [ ] **REQ-frontend**: One page, mobile-first, covering: (1) create shift (riders + totals), (2) upload photos per rider + payment record, (3) run, (4) results — per rider a card with cash owed and a "check these" list with photo thumbnails and one-tap resolve.
  - Acceptance: big tap targets; labels in Tamil and English, with Tamil strings checked by a native speaker before the video (unreviewed machine translation must not ship); implementation is plain HTML/JS or a small React build, whichever is faster.

### Deliverables

- [ ] **REQ-deliverables**: Three submission deliverables required by the event: a README (design-doc style), a video (max 3:00), and a writeup.
  - Acceptance — README covers, in order: (1) the problem (Brindhavan, one paragraph), (2) what it does (one feature), (3) architecture diagram + why each service, (4) verdict rules and why the model never decides, (5) exactly-once design, (6) extraction evaluation results (real measured numbers), (7) cost decisions, (8) deferred decisions (Cognito, multiple formats, multiple businesses, data residency), (9) what was learned (genuinely new only: Bedrock multimodal, Step Functions/Map, DynamoDB conditional writes vs. Redis idempotency already known, SAM, Amplify — explicitly not S3/CloudFront/EC2, used before), (10) prior art and how this differs, (11) AI tools used.
  - Acceptance — Video is ≤3:00, recorded (no live demo), following the timed structure: 0:00-0:20 Brindhavan's problem; 0:20-1:00 upload flow on a phone; 1:00-1:40 results (a flagged photo + one rider's corrected cash total); 1:40-2:20 AWS on screen (Step Functions execution graph, DynamoDB duplicate claim item, Bedrock extraction output); 2:20-2:50 concurrency test passing + cost decision; 2:50-3:00 what was learned. Video must show AWS on screen — mentioning it only in the writeup doesn't count.
  - Acceptance — Writeup is the full pitch (§3) plus README highlights and the AI tools list; optionally also published as an AWS Builder Center post if time allows.

## v2 Requirements

None. This is a single 3.5-day hackathon milestone with a hard Sunday deadline — there is no v2 cycle. Anything beyond v1 scope is captured under Out of Scope below (in PROJECT.md, mirrored here) rather than deferred to a future release.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep. Source: `.planning/intel/decisions.md` "Scope boundaries."

| Feature | Reason |
|---------|--------|
| Cognito or user accounts | Amplify branch password protection substitutes; unneeded complexity for a single-business, single-cashier tool built solo in 3.5 days |
| Any app for riders, or any change to how riders work | Riders keep doing exactly what they do today; tool only processes existing photos + payment record |
| Judging screenshots for forgery (ELA, layout checks) | The bank/payment record is ground truth, not the image; not this product's job |
| Live/real-time verification, gateways, SMS reading | This is a batch job run after a shift ends, not a live system |
| More than one payment-record format | Parser supports exactly one format (whichever Q1 answers); multiple formats is flagged as a top build-breaking risk |
| Multiple businesses/tenants | `business_id` kept in keys for future-proofing only; multi-tenant support not built |
| Analytics, charts, exports beyond one results screen | Not the feature being judged; scope discipline |
| Any tool that generates fake payment screenshots, even for test data | Hard rule — no fake-screenshot generators under any circumstance |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-shift-creation | Phase 3 | Pending |
| REQ-photo-and-record-upload | Phase 3 | Pending |
| REQ-reconciliation-run | Phase 3 | Pending |
| REQ-per-rider-results | Phase 3 | Pending |
| REQ-shift-level-results | Phase 3 | Pending |
| REQ-resolve-flow | Phase 4 | Pending |
| REQ-frontend | Phase 4 | Pending |
| REQ-deliverables | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✓

Note: Phases 1 (Foundation & Kickoff) and 2 (Bedrock Extraction Evaluation) carry no REQ-IDs — they are infrastructure-proving and evaluation gates mandated by HANDOFF.md §13's timeline (Thu bootstrap; Fri-morning evaluation *before* the reconcile engine is built on top of it), not user-facing requirements. Their success criteria are in ROADMAP.md.

---
*Requirements defined: 2026-09-18*
*Last updated: 2026-09-18 after initial roadmap creation*
