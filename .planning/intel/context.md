# Context

Running notes extracted verbatim (with attribution) from HANDOFF.md — classified SPEC, high confidence, precedence 0. This is the only source document ingested.

---

## Topic: Event and judging
- source: HANDOFF.md §1
- Event: First Commit, the first stop on the Bharat Builds Tour (AWS x WeMakeDevs), Sept 17-20, 2026. Solo entry. Page: https://www.wemakedevs.org/aws/first-commit — Rules: https://www.wemakedevs.org/aws/rules
- Goal: be put forward for a fast-track Amazon interview. Up to ten students named per hackathon, drawn from top projects. Prizes and interview selection are decided separately, by different people, against unpublished criteria — repo and writeup should read like strong engineering, not only a good demo.
- Judging criteria: (1) Idea and Impact — "a small problem solved well beats a big one solved vaguely"; (2) Built on AWS — mandatory to win a prize, the video must show AWS, mentioning it only in the writeup doesn't count; (3) Learning — what was genuinely new counts toward the score; (4) Execution — "one feature that runs beats five that almost do"; (5) Demo video — 3 minutes maximum, recorded, no live demo.
- Track: Ship It (deployed on AWS). Architecture and cost decisions are scored here.
- Submission (three parts): public repo, video up to 3 minutes, short writeup (problem, build, where AWS fits). Submissions editable until deadline, not after. Exact Sunday deadline time must be checked on the event page — it is NOT recorded in the source document.
- Pre-event checklist item: Aaryan's AWS Builder Center student verification must be complete (see Status Checklist topic below).

## Topic: Problem and user
- source: HANDOFF.md §2
- User: Hotel Brindhavan, a small local restaurant in Chennai that delivers to Aaryan's apartment building with its own delivery staff (not tech-savvy). Aaryan has confirmed they're willing to be the user.
- Today's process: customer pays by UPI at the door; rider photographs the payment-success screen on the customer's phone; riders also collect cash. At shift end, someone works out which UPI payments actually arrived and how much cash each rider must hand over. Photos are currently checked by eye, not processed.
- The job the tool does: after a shift, owner/cashier uploads each rider's photos, enters that rider's order total, and adds the day's payment record. Tool shows, per rider: verified UPI payments, photos needing checking, duplicates, and cash owed.
- Framing rule (see decisions.md): tool protects riders too; never use the word "fraud" in the UI.

## Topic: Open questions for Brindhavan — UNANSWERED in source
- source: HANDOFF.md §2
- Q1: How does the owner see incoming UPI money — bank app statement (exportable CSV or PDF?), a PhonePe/Paytm business app, SMS, or a soundbox? Decides the parser; build for whatever they actually have, only that. STATUS: unanswered. See constraints.md "Parser constraint — contingent on unanswered Q1."
- Q2: How do rider photos reach the owner? WhatsApp? (WhatsApp strips EXIF metadata — affects timestamp handling.) STATUS: unanswered. See constraints.md "Photo-timestamp constraint — contingent on unanswered Q2."
- Q3: Riders per shift, orders per shift, how cash is settled today — affects scale, demo realism, UI layout. STATUS: unanswered.
- Q4: One real example of a mismatch, and how long checking takes now — this is the first 20 seconds of the video; if the honest answer is "5 minutes and never a problem," tell Aaryan. STATUS: unanswered.
- Q5: Consent to name the restaurant and film the owner briefly — without consent, use "a small restaurant near my building" instead. STATUS: unanswered.
- Until Q1 is answered: write the parser behind an interface and use a fixture built from Aaryan's own transaction export.
- These are explicitly open in the source document. Do not treat any of them as resolved requirements.

## Topic: Pitch
- source: HANDOFF.md §3
- Full pitch (for writeup, contains a bracketed placeholder "[REAL DETAIL FROM Q4]" pending Q4's answer): Hotel Brindhavan is a small restaurant delivering to Aaryan's apartment building in Chennai with its own delivery staff. When someone pays by UPI at the door, the delivery guy photographs the payment screen. At shift end, someone at the counter checks photos one by one against the bank app and works out cash owed per rider. Aaryan built a tool for that one job: cashier uploads a rider's photos, types in the order total, adds the day's payment record; tool shows which payments came in, which didn't, which photos were double-counted, and how much cash each rider owes. Riders don't have to do anything differently. It runs on AWS: Bedrock reads the photos, Step Functions processes a whole shift at once, DynamoDB ensures no payment is counted twice. The model only reads photos; whether a payment counts is decided by matching it against the payment record.
- One-line pitch: "Hotel Brindhavan's riders photograph UPI payments at the door. My tool checks those photos against the bank record and tells the counter how much cash each rider owes."
- Video framing: say only the first two paragraphs (~25 seconds); the screen shows the rest.
- Claim only once tested: that the tool reads photos taken at an angle or with glare — include only if the §8 extraction test supports it, with measured numbers.

## Topic: Novelty claim
- source: HANDOFF.md §4
- Exact framing: "Existing tools either make the business adopt something before money is collected (a POS, a rider app, a store plugin, a gateway, a generated QR), or reconcile clean gateway files. This works with what a small kitchen already has: the photos riders already take, and the owner's own payment record, processed in one batch after the shift, producing the cash each rider owes."
- Explicit instruction: don't lead with "the model never decides verdicts" — other recent reconciliation repos (reconiq, Payout-reconciliation) already use that design; explain it in the README but don't make it the headline.
- Possible technical edge (unproven): input is a camera photo of another phone's screen (glare, tilt, moiré, many different payment apps), not a clean screenshot — claim only if §8 evaluation supports it.

## Topic: Prior art (don't re-search from scratch)
- source: HANDOFF.md §5
- Ordermatrix (ordermatrix.in) — order management for Instagram/WhatsApp sellers, screenshot upload + UTR entry, duplicate UTRs flagged. Differ: seller-side SaaS, checks per order at time of sale, no per-rider cash settlement.
- PosBytz delivery app (posbytz.com/en/free-delivery-app/) — rider app, photo/signature/geo-stamp per delivery, per-rider cash and end-of-shift settlement reports. Differ: requires their POS and rider app.
- OZi Rider (Play Store) — rider app generates UPI QR, confirms payments real time, end-of-day expected vs collected. Differ: requires their app and QR flow.
- RouteMile / FoodXpress for WooCommerce (github.com/codermillat/routemile-woocommerce) — rider PWA, COD amounts, cash-in-hand total, cash settlement workflow. Differ: requires WooCommerce, no UPI-vs-bank check.
- UPI SmartPay for WooCommerce (github.com/iampmpksamy/WordPress_UPI_SmartPay_For_WooCommerce) — customer submits UTR/screenshot, staff verify by hand. Differ: checkout-time, manual.
- OpenPayUPI (github.com/chaursia/OpenUpiPay, github.com/swikki099-ui/Pay) — self-hosted gateway, decimal-suffix amounts, SMS/IMAP matching, Tesseract screenshot UTR, hashed-UTR dedup. Differ: must be set up before money is collected.
- PayGate (pkg.go.dev/github.com/Phloraxx/payment-api) — paise-fingerprint amounts + bank SMS matching. Differ: same as OpenPayUPI.
- fake_Upi (github.com/J0j1n/fake_Upi), ScamShield AI, scamdekho — checks one screenshot for signs of forgery. Differ: we don't judge images, the bank record is ground truth.
- UPI-Transaction-Extractor (github.com/gautamraj8044/UPI-Transaction-Extractor) — PaddleOCR field extraction from clean screenshots. Differ: clean screenshots only, no reconciliation.
- reconiq (github.com/Aarti-panchal01/reconiq) — Razorpay AI Buildathon, Indian UPI/card settlement reconciliation, deterministic core. Differ: gateway settlement files, not photos.
- Payout-reconciliation (github.com/swaroopt14/Payout-reconciliation) — engine owns numbers, AI writes only prose, ambiguous cases never forced. Differ: payment processor/payout scope.
- tallyd (github.com/DaniyalMlk/tallyd) — general double-entry ledger + bank reconciliation. Differ: general bookkeeping.
- Gap noted in source: general web search indexes GitHub poorly; before Friday, spend 10 minutes on GitHub's own search (`rider cash settlement`, `UTR screenshot reconcile`, `payment screenshot bank statement`, `COD reconciliation UPI`) and add anything closer to this table. (See also Status Checklist — "10-minute GitHub prior-art search done" is unchecked.)

## Topic: Suggested repo layout
- source: HANDOFF.md §11
- ```
  .
  ├── README.md                # written like a design doc (§12)
  ├── template.yaml            # SAM
  ├── statemachine/recon.asl.json
  ├── src/
  │   ├── api/                 # API Lambda handlers
  │   ├── parse_record/        # parser interface + one implementation
  │   ├── extract/             # Bedrock call, prompt, validation
  │   ├── reconcile/           # pure verdict engine + DynamoDB claim layer
  │   └── common/              # models, logging, config
  ├── web/                     # frontend
  ├── tests/
  │   ├── unit/
  │   ├── concurrency/
  │   └── fixtures/            # synthetic credits + extraction JSON only
  └── docs/
      ├── DECISIONS.md         # running decision log with dates
      ├── AI_TOOLS.md          # required in the writeup
      ├── extraction-eval.md   # §8 results
      └── architecture.png
  ```
- Note: keep `reconcile/` as pure functions with the DynamoDB layer separate, so the verdict engine can be tested without AWS.

## Topic: Timeline
- source: HANDOFF.md §13
- Thu (kickoff day): Builder Center student verification; repo created + first commit; SAM hello-world deployed to ap-south-1; Bedrock model access confirmed; 20-30 test photos taken; Q1-Q5 asked. Checkpoint: a deployed endpoint returns 200.
- Fri morning: §8 extraction test run and written up. Checkpoint: model chosen, pitch claim kept or dropped.
- Fri afternoon/night: parser (fixture), reconcile engine + all §10 unit tests, claim layer + concurrency test, Step Functions end-to-end from the CLI. Checkpoint: a full shift reconciles from the CLI.
- Sat: frontend on Amplify; resolve flow; dashboard; submit a rough version; record the video Saturday night. Checkpoint: a live URL works on a phone.
- Sun: README, writeup, AI tools list, Builder Center post; polish; re-record only if needed; final submit well before the deadline. Checkpoint: submitted.

## Topic: Where it's most likely to break (risks)
- source: HANDOFF.md §13
1. Bedrock access, region or quota surprises — discover Thursday, not Friday.
2. IAM and passing S3 image bytes into Bedrock inside Step Functions — steepest learning curve; call Bedrock from a Lambda, don't try Step Functions' direct Bedrock integration for images.
3. Payment-record format — blocked on Q1 (unanswered); support exactly one format.
4. Frontend time sink — keep it to one page.
5. Leaving the video to Sunday — record Saturday night.
6. Over-building the correctness layer while the README and video wait — Aaryan's known tendency, given his background.

## Topic: Status checklist — UNANSWERED / incomplete in source
- source: HANDOFF.md §14
- [ ] Builder Center student verification complete
- [ ] Q1 payment record format: _____
- [ ] Q2 photo channel: _____
- [ ] Q3 scale: _____
- [ ] Q4 real mismatch + time spent: _____
- [ ] Q5 consent to name/film: _____
- [ ] 10-minute GitHub prior-art search done
- [ ] Exact submission deadline (from event page): _____
- [ ] Extraction eval done → model: _____ · UTR exact: ___% · confident-wrong: ___ · amount: ___%
- [ ] Tamil labels reviewed by: _____
- All items above are unchecked/blank in the source document. Do not infer answers or mark these done.

## Topic: Owner background
- source: HANDOFF.md (header)
- Owner: Aaryan Manchanda (final-year B.Tech CS, VIT Chennai, graduating 2027). Backend and payments-infra background: exactly-once billing, idempotent ledgers, OTel tracing. New this week to Bedrock, Step Functions, DynamoDB, SAM and Amplify. Document written Thursday, September 17, 2026 (kickoff day).
