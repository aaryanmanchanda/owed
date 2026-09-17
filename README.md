# owed

A batch reconciliation tool for Hotel Brindhavan, a small Chennai restaurant
with its own delivery staff. Built solo, on AWS (Ship It track), for the
WeMakeDevs "First Commit" hackathon (Sept 17-20, 2026).

This README is written like a design doc, per HANDOFF §12. Each section below
is a stub during Phase 1 (foundation/kickoff) — the prose gets filled in as
each phase completes the work it describes.

## 1. The Problem

_Fills in during Phase 5 (writeup), drawing on HANDOFF §2 and the real Q4
answer once Hotel Brindhavan's owner has been asked. One paragraph on the
manual, error-prone shift-end reconciliation process Brindhavan's cashier
does today._

## 2. What It Does

_Fills in during Phase 5. One feature: upload rider photos + a shift's
payment record, get back per-rider verified totals, flagged photos,
duplicates, and cash owed. See HANDOFF §6 for the locked scope._

## 3. Architecture Diagram + Why Each Service

_Fills in during Phase 4 (frontend) / Phase 5, once the full stack (Amplify,
API Gateway, Lambda, Step Functions, DynamoDB, CloudWatch) is deployed
end-to-end. HANDOFF §9 has the locked architecture; Phase 1 plan 01-01 proves
only the first hop (API Gateway -> Lambda) works._

## 4. Verdict Rules and Why the Model Never Decides

_Fills in during Phase 3 (reconcile engine), once the verdict rules from
HANDOFF §7 are implemented and unit-tested. Core promise: a vision model only
extracts fields from a photo; every verdict comes from deterministic code._

## 5. Exactly-Once Design

_Fills in during Phase 3, once the DynamoDB conditional-write claim layer,
`photo_id` (SHA-256 of image bytes), and the single-writer Reconcile Lambda
are built and concurrency-tested (HANDOFF §7, §10)._

## 6. Extraction Evaluation Results

_Fills in during Phase 2, with real measured numbers only — see
`docs/extraction-eval.md`, currently a headings-only stub. No number is
written here until it has actually been measured (PROJECT.md Working Rule 5)._

## 7. Cost Decisions

_Fills in progressively. Known so far (Phase 1): Lambda functions default to
arm64 Graviton at 256 MB as a deliberate cost lever (see
`docs/DECISIONS.md`). Model tier, image downscaling, and Map concurrency
levers get recorded here once Phase 2/3 make those calls._

## 8. Deferred Decisions

_Fills in progressively. Known so far: no Cognito/accounts (Amplify branch
password protection instead); exactly one payment-record format supported;
single-tenant only (`business_id` kept in keys for future-proofing); data
residency trade-off for whichever Bedrock inference profile the smoke test
and Phase 2 evaluation end up using — see HANDOFF §6, §8, §9._

## 9. What I Learned

_Fills in during Phase 5. Only genuinely new-this-week things: Bedrock
multimodal, Step Functions/Map, DynamoDB conditional writes (vs. the Redis
idempotency patterns Aaryan already knew), SAM, Amplify. Not S3/CloudFront/
EC2, which predate this event for Aaryan._

## 10. Prior Art and How This Differs

_Fills in during Phase 5, drawing on HANDOFF §5's 11-project survey (closest:
reconiq, Payout-reconciliation) and the Phase 1 plan 01-03 10-minute GitHub
prior-art search. Novelty claim is locked in HANDOFF §4 and PROJECT.md._

## 11. AI Tools Used

_See `docs/AI_TOOLS.md` for the dated running list (HANDOFF §1 submission
requirement). Summarized here in Phase 5's writeup pass._
