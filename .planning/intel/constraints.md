# Constraints

Extracted from HANDOFF.md (classified SPEC, high confidence, precedence 0). Technical contracts, schemas, protocols, and non-functional requirements.

---

## Per-photo extraction output schema
- source: HANDOFF.md §7
- type: schema
- content: Bedrock returns per photo: `{"utr": "string of exactly 12 digits, or null", "amount_inr": "number, or null", "screen_time": "ISO-8601 in IST, or null", "payment_app": "gpay | phonepe | paytm | bhim | other | null", "status_text": "success | pending | failed | null", "payee_name": "string or null", "notes": "short free text on legibility"}`. Validation is enforced in code, never trusted from the model: if `utr` doesn't match `^\d{12}$`, set it to null; if `amount_inr` isn't positive with at most 2 decimals, set it to null. The model is instructed to return null whenever it isn't sure — a null is a normal result, not an error.

## Verdict rule table (deterministic)
- source: HANDOFF.md §7
- type: protocol
- content: Rules applied in order, per photo, against the payment record: `NOT_SUCCESS` (status_text pending/failed → not counted, "check this"); `UNREADABLE` (utr and amount_inr both null → not counted, owner reviews); `DUPLICATE` (valid utr already claimed by a different photo_id, any shift → not counted, shows earlier claim source); `VERIFIED` (valid utr found in record, amount equal, claim succeeds, or existing claim belongs to same photo_id → counts toward cash owed); `AMOUNT_MISMATCH` (valid utr found, amount differs → not counted, "check this"); `PROBABLE` (utr null or not in record, and exactly one unclaimed credit with same amount within ±WINDOW_MIN of screen_time → counts only after owner confirms with one tap); `AMBIGUOUS` (same as PROBABLE but two-or-more candidates → not counted, owner picks one); `NOT_FOUND` (no UTR match and no amount+time candidate → not counted, shown as "check this", never as fraud). After all photos: credits in the shift window with no claim are `UNCLAIMED_CREDIT`. Defaults: `WINDOW_MIN = 10` (configurable). All times in IST. Rationale (must be preserved by testing, §10): a model misread that invents a plausible-but-wrong UTR falls through to the amount+time check and becomes PROBABLE/AMBIGUOUS rather than NOT_FOUND whenever a matching credit exists — this ordering must not change.

## Exactly-once and deterministic ordering protocol
- source: HANDOFF.md §7
- type: protocol
- content: `photo_id` = SHA-256 of the image bytes, so the same file uploaded twice is the same photo. Extraction runs in parallel (Map state). Reconciliation runs as one Lambda per shift, processing photos sorted by `(screen_time, photo_id)`, so which photo "wins" a duplicate is deterministic. Claims use DynamoDB conditional writes, protecting against races across concurrent runs and shifts. Re-running the same shift must give identical results: a claim already owned by the same `photo_id` counts as success, not a duplicate. A `PROBABLE` match also claims the candidate credit, marked `pending_confirm`, so two photos can't both take it; if the owner rejects the match, the claim is released.

## API contract
- source: HANDOFF.md §9
- type: api-contract
- content: `POST /shifts` — create a shift `{business_id, date, riders:[{name, order_total}]}`. `POST /shifts/{id}/uploads` — returns presigned PUT URLs for photos (tagged by rider) and the payment record. `POST /shifts/{id}/run` — start the Step Functions execution (idempotent per upload set). `GET /shifts/{id}` — status + per-rider results + unclaimed credits. `POST /shifts/{id}/photos/{photo_id}/resolve` — owner confirms/rejects PROBABLE, or picks one for AMBIGUOUS. Access control: there are no accounts; use a shared secret header plus API Gateway throttling as the minimum, documented as a deferred decision (Cognito would be next) — explicitly not production-grade security.

## DynamoDB single-table schema (`recon`)
- source: HANDOFF.md §9
- type: schema
- content: `PK=BIZ#{biz}`, `SK=CREDIT#{utr}` — from the payment record; if a row has no reference, use `CREDIT#H#{sha256(date,time,amount,narration)}`. `PK=BIZ#{biz}`, `SK=CLAIM#{utr_or_credit_key}` — `attribute_not_exists(SK)` conditional write; stores `photo_id`, `shift_id`, `rider`, `state` (`final` / `pending_confirm`). `PK=SHIFT#{shift}`, `SK=META` — status, created_at, execution ARN. `PK=SHIFT#{shift}`, `SK=RIDER#{name}` — order_total, verified_total, cash_owed_min/max. `PK=SHIFT#{shift}`, `SK=PHOTO#{photo_id}` — rider, s3 key, extraction JSON, verdict, candidate credit keys. Every item has an `expires_at` TTL.

## S3 layout
- source: HANDOFF.md §9
- type: schema
- content: `uploads/{shift_id}/record/{filename}` and `uploads/{shift_id}/photos/{rider}/{photo_id}.jpg`. Block public access, turn on server-side encryption, add a lifecycle expiry.

## Observability requirements
- source: HANDOFF.md §9
- type: nfr
- content: Structured JSON logs carrying `shift_id`, `photo_id`, and `verdict`. One CloudWatch dashboard: executions, Map failures, Bedrock latency, verdict counts. OTel-level tracing is explicitly not required here ("keep this light. It isn't the feature.").

## Testing requirements
- source: HANDOFF.md §10
- type: nfr
- content: Unit tests, one or more per verdict in §7, using hand-written extraction JSON and credit fixtures — no Bedrock calls in unit tests. Misread-safety test: a made-up UTR with a matching amount and time must come out PROBABLE, never NOT_FOUND; two candidates must come out AMBIGUOUS. Idempotent re-run test: reconciling the same shift twice gives identical verdicts and no self-duplicates. Same-bytes-twice test: one photo_id, one claim. Concurrency test: against DynamoDB Local (or a test table), N parallel workers try to claim the same UTR, exactly one succeeds — this test is part of the video. Cash-owed test: min/max range correct with unresolved items, collapses to one number once resolved. Parser test: fixture-based tests for the Q1 format, including a row with no reference. Deterministic-ordering test: shuffling photo input order doesn't change which photo wins a duplicate. Suggested tools: pytest, moto or DynamoDB Local, hypothesis for the ordering property if time allows.

## Bedrock extraction evaluation protocol
- source: HANDOFF.md §8
- type: protocol
- content: Test set: ~30 photos of Aaryan's own UPI payments, photographed off a phone screen, correct values from his own transaction history; conditions: straight on, ~30° angle, overhead glare, dim light, partly cut off; apps: GPay, PhonePe, Paytm (more if available). Candidates: two Bedrock vision models (one cheaper, one stronger, available via ap-south-1) plus Amazon Rekognition text detection as baseline. Harness: AWS's `aws-samples/ocr-with-aws-ai-services` sample repo or a ~50-line script, credited whichever is used; results kept in `docs/extraction-eval.md`. Measure per photo × model: UTR exact match, amount correct, returned null, confident wrong UTR, latency, approximate cost. Pass criteria: amounts nearly always correct; confident wrong UTRs close to zero (honest nulls are fine — the amount+time rule covers them). Cost levers to record for the writeup: model tier, image downscaling to smallest size keeping accuracy, Map concurrency (start at 4). Data residency: must record which region requests are actually processed in; if the chosen model uses an APAC/global inference profile rather than India-only routing, this must be stated in the writeup as a deliberate trade-off. If results are weak: drop the glare/angle claim from the pitch, make amount+time matching the main path, and say so honestly in the writeup. Rule "never write accuracy or cost numbers that weren't measured" (§15 rule 5) applies to all of the above.

## Parser constraint — contingent on unanswered Q1
- source: HANDOFF.md §2, §6, §13 (risk #3)
- type: protocol
- content: Support exactly one payment-record format (the out-of-scope list forbids more than one). Until open question Q1 (how the owner sees incoming UPI money: bank statement export CSV/PDF, PhonePe/Paytm business app, SMS, or soundbox) is answered, the parser must be written behind an interface, with a fixture built from Aaryan's own transaction export used for development and testing. This is flagged as one of the most likely places the build breaks (§13 risk #3: "Blocked on Q1. Support exactly one format."). NOTE: Q1 is UNANSWERED in the source document — do not assume a format.

## Photo-timestamp constraint — contingent on unanswered Q2
- source: HANDOFF.md §2
- type: protocol
- content: If rider photos reach the owner via WhatsApp, WhatsApp strips EXIF metadata. Use the time shown on the payment screen itself, never the file's metadata, for `screen_time`. NOTE: Q2 (how rider photos actually reach the owner) is UNANSWERED in the source document.
