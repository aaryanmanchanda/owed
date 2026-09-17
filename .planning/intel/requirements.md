# Requirements

Extracted from HANDOFF.md §3, §6, §9, §12 (the document functions as a PRD for this section — the "one feature" and its deliverables). Source classified SPEC, high confidence, precedence 0.

---

## REQ-shift-creation
- source: HANDOFF.md §6, §9 (API: `POST /shifts`)
- description: Owner/cashier creates a shift by entering, for each rider on that shift, a name and the rider's total order value for the shift (entered by hand).
- acceptance: `POST /shifts` accepts `{business_id, date, riders:[{name, order_total}]}` and creates a shift record.
- scope: shift creation, rider order-total intake

## REQ-photo-and-record-upload
- source: HANDOFF.md §6, §9 (API: `POST /shifts/{id}/uploads`)
- description: Owner/cashier uploads each rider's payment-screen photos and the day's/shift's payment record.
- acceptance: `POST /shifts/{id}/uploads` returns presigned PUT URLs for photos (tagged by rider) and for the payment record; uploads go to S3 (see constraints.md S3 layout).
- scope: photo intake, payment record intake

## REQ-reconciliation-run
- source: HANDOFF.md §9 (API: `POST /shifts/{id}/run`)
- description: Owner/cashier triggers reconciliation processing for the uploaded shift.
- acceptance: `POST /shifts/{id}/run` starts the Step Functions execution; the operation is idempotent per upload set (re-running with the same uploads does not duplicate work or claims — see constraints.md exactly-once/ordering protocol).
- scope: reconciliation execution trigger

## REQ-per-rider-results
- source: HANDOFF.md §6, §9 (API: `GET /shifts/{id}`)
- description: For each rider, the tool shows verified UPI payments and their total; photos that need checking, grouped by reason; duplicates, with where the earlier claim came from; and the cash that rider owes.
- acceptance: cash owed = order total − verified UPI − UPI confirmed by the owner. While anything is unresolved, show a range: "owes ₹X, or ₹Y if the flagged payments are genuine." Range collapses to one number once all flagged items are resolved.
- scope: per-rider results display, cash-owed computation

## REQ-shift-level-results
- source: HANDOFF.md §6
- description: For the whole shift, show unclaimed credits — money that arrived with no matching photo.
- acceptance: `GET /shifts/{id}` response includes an unclaimed-credits list for the shift.
- scope: shift-level results display

## REQ-resolve-flow
- source: HANDOFF.md §9 (API: `POST /shifts/{id}/photos/{photo_id}/resolve`)
- description: Owner can confirm or reject a `PROBABLE` verdict, or pick one candidate for an `AMBIGUOUS` verdict.
- acceptance: `POST /shifts/{id}/photos/{photo_id}/resolve` accepts a confirm/reject (PROBABLE) or a selection among candidates (AMBIGUOUS); rejecting a PROBABLE match releases the claimed candidate credit (see constraints.md verdict rules).
- scope: manual resolution workflow

## REQ-frontend
- source: HANDOFF.md §9 (Frontend section)
- description: One page, mobile-first, covering: (1) create shift (riders + totals), (2) upload photos per rider + payment record, (3) run, (4) results — per rider a card with cash owed and a "check these" list with photo thumbnails and one-tap resolve.
- acceptance: big tap targets; labels in Tamil and English, with Tamil strings checked by a native speaker before the video (unreviewed machine translation must not ship); implementation is plain HTML/JS or a small React build, whichever is faster.
- scope: end-to-end frontend UX

## REQ-deliverables
- source: HANDOFF.md §12
- description: Three submission deliverables are required by the event: a README (design-doc style), a video (max 3:00), and a writeup.
- acceptance:
  - README covers, in order: the problem (Brindhavan, one paragraph); what it does (one feature); architecture diagram + why each service; verdict rules and why the model never decides; exactly-once design; extraction evaluation results (real numbers); cost decisions; deferred decisions (Cognito, multiple formats, multiple businesses, data residency); what was learned (genuinely new: Bedrock multimodal, Step Functions/Map, DynamoDB conditional writes vs. Redis idempotency already known, SAM, Amplify — explicitly not S3/CloudFront/EC2, used before); prior art and how this differs; AI tools used.
  - Video is ≤3:00, recorded (no live demo), following the timed structure: 0:00–0:20 Brindhavan's problem; 0:20–1:00 upload flow on a phone; 1:00–1:40 results (a flagged photo + one rider's corrected cash total); 1:40–2:20 AWS on screen (Step Functions execution graph, DynamoDB duplicate claim item, Bedrock extraction output); 2:20–2:50 concurrency test passing + cost decision; 2:50–3:00 what was learned. Video must show AWS on screen — mentioning it only in the writeup doesn't count.
  - Writeup is the full pitch (§3) plus README highlights and the AI tools list; optionally also published as an AWS Builder Center post if time allows.
- scope: submission deliverables, judging-criteria compliance
