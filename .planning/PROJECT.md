# owed

## What This Is

A batch reconciliation tool for Hotel Brindhavan, a small Chennai restaurant with its own delivery staff. After a shift, the owner/cashier uploads each rider's UPI payment-screen photos plus the day's payment record; the tool tells the counter, per rider, which payments verified, which need checking, which were duplicates, and exactly how much cash that rider owes. Built solo, on AWS (Ship It track), for the WeMakeDevs "First Commit" hackathon (Sept 17-20, 2026).

## Core Value

The cash-owed number for every rider is always correct and never a false accusation — a vision model only *extracts* fields from a photo; every verdict (verified / duplicate / flagged / owed) comes from deterministic code matched against the payment record, never from the model's judgment.

## Business Context

- **Customer**: Hotel Brindhavan (real, confirmed user) — plus, functionally, the hackathon judges/AWS reviewers scoring this as a "Ship It" entry.
- **Revenue model**: None — this is a hackathon entry, not a monetized product. The event's payoff is a shot at a fast-track Amazon interview (up to 10 students named per hackathon, criteria unpublished).
- **Success metric**: Submitted by deadline — done = public repo + video (≤3 min) + writeup submitted before the Sunday deadline (2026-09-20, exact time TBD from the event page — open item, see Context). Must satisfy every HANDOFF.md §12 deliverable and every §15 session rule. Interview/prize selection itself is explicitly out of this roadmap's control and is NOT a completion criterion — finishing and submitting on time is.
- **Strategy notes**: Full source spec/handoff: `HANDOFF.md` (repo root). Synthesized intel: `.planning/intel/SYNTHESIS.md`.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — nothing has shipped)

### Active

<!-- Current scope. Building toward these. See REQUIREMENTS.md for full acceptance criteria. -->

- [ ] **REQ-shift-creation**: Owner/cashier creates a shift (riders + order totals) via `POST /shifts`
- [ ] **REQ-photo-and-record-upload**: Owner/cashier uploads rider photos + payment record via presigned URLs
- [ ] **REQ-reconciliation-run**: Owner/cashier triggers the Step Functions reconciliation run, idempotently
- [ ] **REQ-per-rider-results**: Per-rider verified UPI total, flagged photos, duplicates, cash-owed range/number
- [ ] **REQ-shift-level-results**: Shift-level unclaimed credits (money with no matching photo)
- [ ] **REQ-resolve-flow**: Owner confirms/rejects PROBABLE, or picks a candidate for AMBIGUOUS
- [ ] **REQ-frontend**: One mobile-first page covering create → upload → run → results, bilingual (Tamil/English)
- [ ] **REQ-deliverables**: README (design-doc style) + ≤3:00 video + writeup, per HANDOFF.md §12

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. See decisions.md "Scope boundaries" for source. -->

- Cognito or any user accounts — Amplify branch password protection is the documented substitute; accounts are unneeded complexity for a single-business, single-cashier tool in 3.5 days
- Any app for riders, or any change to how riders work — riders keep doing exactly what they do today; the tool only processes what already exists (photos + payment record)
- Judging screenshots for forgery (ELA, layout checks) — out of scope by design; the bank record is ground truth, not the image
- Live/real-time verification, payment gateways, SMS reading — this is a batch job run after a shift, not a live system
- More than one payment-record format — parser supports exactly one format (whichever Q1 answers); building for multiple formats risks the build, per HANDOFF §13 risk #3
- Multiple businesses/tenants — `business_id` is kept in keys for future-proofing, but multi-tenant support is not built
- Analytics, charts, or exports beyond one results screen — not the feature being scored
- Any tool that generates fake payment screenshots, even for test data — explicit hard rule (HANDOFF §6/§15); test data is real (small) transfers of Aaryan's own money, never synthetic images

## Context

**Event**: First Commit, Bharat Builds Tour (AWS × WeMakeDevs), Sept 17-20, 2026. Solo entry, Ship It track (deployed on AWS). Judging: Idea & Impact, Built on AWS (video must show AWS on screen — mentioning it in the writeup only doesn't count), Learning, Execution, Demo video (≤3:00, recorded, no live demo). Submission = public repo + video + writeup, editable until deadline, not after. **Open item**: exact Sunday deadline time not in source — must be checked on the event page (https://www.wemakedevs.org/aws/first-commit) before Sunday.

**User & problem**: Hotel Brindhavan (small Chennai restaurant, own delivery staff, not tech-savvy) — confirmed real user. Today: customer pays UPI at the door, rider photographs the payment-success screen, riders also collect cash; at shift end someone manually checks photos against the bank app to work out cash owed per rider. Currently manual, error-prone, and not processed by any tool.

**Framing rule**: the tool protects riders too — a verified payment settles the question for everyone. Never use the word "fraud" in the UI; anything flagged reads as "check this."

**Novelty claim (state exactly)**: "Existing tools either make the business adopt something before money is collected (a POS, a rider app, a store plugin, a gateway, a generated QR), or reconcile clean gateway files. This works with what a small kitchen already has: the photos riders already take, and the owner's own payment record, processed in one batch after the shift, producing the cash each rider owes." Don't lead with "the model never decides verdicts" (crowded framing, e.g. reconiq, Payout-reconciliation) — explain it in the README, don't headline it. Possible unproven edge: input is a photo of *another phone's* screen (glare/tilt/moiré), not a clean screenshot — claim only if the §8 extraction evaluation supports it, with measured numbers.

**Prior art** (11 projects surveyed, don't re-search from scratch — full table in `.planning/intel/context.md` and HANDOFF.md §5): closest are reconiq and Payout-reconciliation (both deterministic-core, AI-assists-only design, but gateway/payout scope not photos); everything else requires the business to adopt new infrastructure before money is collected, or only checks single screenshots for forgery. Spend 10 minutes on GitHub's own search before Friday to check for closer prior art (status: not done as of ingest).

**Open questions for Brindhavan — UNANSWERED, do not treat as resolved** (HANDOFF §2, full detail in `.planning/intel/context.md`):
- **Q1** — payment-record format (bank export CSV/PDF? business app? SMS? soundbox?) — decides the parser. Until answered: parser is written behind an interface, developed/tested against a fixture built from Aaryan's own transaction export.
- **Q2** — how rider photos reach the owner (WhatsApp strips EXIF) — affects timestamp handling; use on-screen `screen_time`, never file metadata, regardless of the answer.
- **Q3** — riders/orders per shift, current cash-settlement process — affects scale and demo realism.
- **Q4** — one real mismatch example + time currently spent checking — this is the video's first 20 seconds.
- **Q5** — consent to name the restaurant/film the owner — absent consent, use "a small restaurant near my building."

**Status checklist — all unchecked/blank in source, do not infer answers** (HANDOFF §14): Builder Center student verification; Q1-Q5 answers; 10-minute GitHub prior-art search; exact submission deadline; extraction eval results; Tamil label review sign-off.

**Owner background**: Aaryan Manchanda, final-year B.Tech CS (VIT Chennai, graduating 2027). Backend/payments-infra background (exactly-once billing, idempotent ledgers, OTel tracing) — genuinely new this week: Bedrock, Step Functions, DynamoDB, SAM, Amplify. Known tendency to over-build the correctness layer while README/video wait (HANDOFF §13 risk #6) — watch for this in later phases.

## Constraints

- **Timeline**: 3.5-day solo hackathon. Kickoff Thu 2026-09-17; submit-by Sun 2026-09-20 (exact time TBD from event page). All project work must postdate kickoff — a repo whose commit history doesn't match event dates disqualifies the entry.
- **Region**: AWS ap-south-1 (Mumbai) — all resources, including recording which region Bedrock requests are actually processed in (APAC/global inference profiles must be disclosed as a trade-off if used).
- **Runtime**: Python (current Lambda-supported version).
- **IaC**: AWS SAM.
- **Frontend hosting**: AWS Amplify Hosting, mobile-first, branch password protection (no Cognito/accounts).
- **Architecture (locked, HANDOFF §9)**: Amplify → API Gateway (HTTP API) → Lambda `api` → S3 (presigned uploads) → Step Functions (Standard, 4 states: ParseRecord → ExtractPhotos [Map, MaxConcurrency 4] → Reconcile [single writer] → Finalize) → DynamoDB single table `recon` (TTL on every item) → CloudWatch (structured JSON logs + 1 dashboard).
- **Access control**: no accounts; shared secret header + API Gateway throttling only, explicitly documented as not production-grade (deferred: Cognito).
- **Data handling**: no real customer payment screens anywhere (repo, fixtures, video); test photos are Aaryan's own small transfers photographed off a phone screen; no fake-screenshot generators, ever; every DynamoDB item and S3 object has a TTL/lifecycle rule (default 7 days).
- **Verdict rules are locked (HANDOFF §7)** — see Locked Decisions below; do not change without asking Aaryan first.
- **Bedrock call pattern**: call Bedrock from a Lambda; do not attempt Step Functions' direct Bedrock integration for image bytes (steepest learning-curve risk per §13).
- **Testing**: unit tests per verdict rule using hand-written fixtures, no Bedrock calls in unit tests; misread-safety, idempotent-re-run, same-bytes-twice, concurrency (DynamoDB Local/test table), cash-owed-range, parser, and deterministic-ordering tests all required (HANDOFF §10).

## Working Rules (HANDOFF §15 — apply across every phase, not just one)

These are session rules, not one-time decisions. They constrain how every phase is executed, from Phase 1 through submission:

1. Stay inside the Out-of-Scope boundaries above. Propose additions; don't build them unasked.
2. Small, atomic commits with clear messages. No squashing history into one commit. Never backdate a commit.
3. Copy no code from any HANDOFF §5 prior-art repo or from `mcp-studio`. Design ideas borrowed get a credit in the README.
4. No real customer data anywhere in the repo, ever. No fake-screenshot generators, ever.
5. Never write accuracy or cost numbers that weren't actually measured (applies especially to the §8 extraction evaluation and README's cost-decisions section).
6. Add an entry to `docs/DECISIONS.md` whenever a decision is made or changed — running log with dates.
7. Keep the verdict engine pure and fully unit-tested before wiring any AWS services around it.
8. Ask Aaryan before changing the §7 verdict rules. They are the core of the product and of the "no false accusations" promise — never silently reinterpret them.

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Project idea: own-delivery restaurant rider reconciliation (Hotel Brindhavan) | Real confirmed user; fits batch differentiator; fits owner's payments background; legible demo. 6 alternatives explicitly dead — do not reopen without new evidence | ✓ Locked |
| Verdict rules are deterministic; the model never decides | Core of the "no false accusations" promise; the whole product's credibility rests on this. Ask Aaryan before changing §7 | ✓ Locked |
| Architecture & stack: ap-south-1, Python, SAM, Amplify + API Gateway + Lambda + Step Functions + DynamoDB + CloudWatch | Locked by HANDOFF §9; scores directly on the Ship It track's architecture/cost criteria | ✓ Locked |
| Scope boundaries (see Out of Scope above) | Keeps one feature legible and buildable solo in 3.5 days; "one feature that runs beats five that almost do" | ✓ Locked |
| Repo integrity / competition compliance (post-kickoff-only commits, no copied code, small atomic commits, AI tools disclosed in `docs/AI_TOOLS.md`) | Violating these disqualifies the entry outright | ✓ Locked |
| Data handling & privacy (no real customer data anywhere, TTL everywhere, no fake-screenshot generators) | Ethical/compliance floor; also protects the real user (Brindhavan) | ✓ Locked |
| Framing rule — never use the word "fraud" in the UI | Product protects riders too; a verified payment settles it for everyone | ✓ Locked |

---
*Last updated: 2026-09-18 after initial roadmap creation (ingest of HANDOFF.md)*
