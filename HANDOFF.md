# Handoff: Rider Payment Reconciler (working name)

Handoff for a Claude Code session. Read the whole file before writing any code. Everything here has been decided, researched, or explicitly left open; don't relitigate a decision without a new reason, and ask before changing scope.

Owner: Aaryan Manchanda (final-year B.Tech CS, VIT Chennai, graduating 2027). Backend and payments-infra background: exactly-once billing, idempotent ledgers, OTel tracing. New this week to Bedrock, Step Functions, DynamoDB, SAM and Amplify.

Written: Thursday, September 17, 2026 (kickoff day).

---

## 1. Event and why the rules shape the build

**Event:** First Commit, the first stop on the Bharat Builds Tour (AWS × WeMakeDevs), Sept 17–20, 2026. Solo entry. Page: https://www.wemakedevs.org/aws/first-commit · Rules: https://www.wemakedevs.org/aws/rules

**Goal:** be put forward for a fast-track Amazon interview. The event names up to ten students per hackathon, drawn from top projects; the project stands in for the screening round. Prizes and interview selection are decided separately, by different people, against criteria that aren't published. So the repo and writeup should read like strong engineering, not only a good demo.

**Judging criteria:**
1. Idea and Impact: "a small problem solved well beats a big one solved vaguely"
2. Built on AWS: mandatory to win a prize. **The video must show AWS**; mentioning it only in the writeup doesn't count.
3. Learning: what was genuinely new counts toward the score.
4. Execution: "one feature that runs beats five that almost do"
5. Demo video: 3 minutes maximum, recorded, no live demo.

**Track:** Ship It (deployed on AWS). Architecture and cost decisions are scored here.

**Submission (three parts):** a public repo, a video of up to 3 minutes, and a short writeup covering the problem, the build, and where AWS fits. Submit early; submissions can be edited until the deadline and not after. **Check the exact Sunday deadline time on the event page.** It isn't recorded here.

**Hard rules for this repo:**
- All project work starts after kickoff. Old projects don't count, even rewritten. **A repo whose history doesn't match the event dates disqualifies the entry.** Commit small and often, with honest messages.
- **Copy no code from anywhere**, including Aaryan's own `mcp-studio` repo and every repo listed in §5. Libraries, frameworks and starter templates are allowed; anything not written during the event needs a credit and a compatible licence.
- The writeup must **list the AI coding tools used**. Keep `docs/AI_TOOLS.md` up to date as you go.
- Pre-event checklist: Aaryan's AWS Builder Center student verification must be complete (§14).

---

## 2. The problem and the user

**User:** Hotel Brindhavan, a small local restaurant in Chennai that delivers to Aaryan's apartment building with its own delivery staff. The staff aren't tech-savvy. Aaryan has confirmed they're willing to be the user.

**Today's process:** when a customer pays by UPI at the door, the rider photographs the payment-success screen on the customer's phone. Riders also collect cash. At the end of a shift, someone has to work out which UPI payments actually arrived and how much cash each rider must hand over. The photos are currently checked by eye, not processed.

**The job the tool does:** after a shift, the owner or cashier uploads each rider's photos, enters that rider's order total, and adds the day's payment record. The tool shows, for each rider: verified UPI payments, photos that need checking, duplicates, and **the cash that rider owes**.

**Framing rule:** the tool protects riders too. A verified payment settles the question for everyone. Never use the word fraud in the UI. Anything flagged is shown as "check this".

### Open questions for Brindhavan (answers change the build)

| # | Question | Why it matters |
|---|---|---|
| Q1 | How does the owner see incoming UPI money: a bank app statement (exportable CSV or PDF?), a PhonePe/Paytm business app, SMS, or a soundbox? | **Decides the parser.** Build for whatever they actually have, and only that. |
| Q2 | How do rider photos reach the owner? WhatsApp? | WhatsApp strips EXIF metadata. Use the **time shown on the payment screen**, never the file's metadata. |
| Q3 | Riders per shift, orders per shift, how cash is settled today | Scale, demo realism, UI layout |
| Q4 | One real example of a mismatch, and how long checking takes now | This is the first 20 seconds of the video. If the honest answer is "5 minutes and never a problem", tell Aaryan. |
| Q5 | Consent to name the restaurant and film the owner briefly | Without consent, say "a small restaurant near my building" instead. |

Until Q1 is answered, write the parser behind an interface and use a fixture built from Aaryan's own transaction export.

---

## 3. Pitch

**Full version (for the writeup):**

> Hotel Brindhavan is a small restaurant that delivers to my apartment building in Chennai. They use their own delivery staff. When someone pays by UPI at the door, the delivery guy takes a photo of the payment screen on the customer's phone. At the end of the night, someone at the counter goes through those photos one by one, checks each against the bank app, and works out how much cash each rider still has to hand over. [REAL DETAIL FROM Q4]
>
> I built a tool for that one job. The cashier uploads a rider's photos, types in his order total for the shift, and adds the day's payment record. The tool shows which payments came in, which ones didn't, which photos were counted twice, and how much cash that rider owes. The riders don't have to do anything differently.
>
> It runs on AWS. Amazon Bedrock reads the photos, Step Functions processes a whole shift at once, and DynamoDB makes sure no payment is counted twice. The model only reads the photos. Whether a payment counts is decided by matching it against the payment record.

**One line:** "Hotel Brindhavan's riders photograph UPI payments at the door. My tool checks those photos against the bank record and tells the counter how much cash each rider owes."

**For the video:** say only the first two paragraphs (about 25 seconds). The screen shows the rest.

**Claim only once tested:** that the tool reads photos taken at an angle or with glare. Include it only if the §8 test supports it, and then with the measured numbers.

---

## 4. Novelty claim (state it exactly like this)

> Existing tools either make the business adopt something before money is collected (a POS, a rider app, a store plugin, a gateway, a generated QR), or reconcile clean gateway files. This works with what a small kitchen already has: the photos riders already take, and the owner's own payment record, processed in one batch after the shift, producing the cash each rider owes.

**Don't** lead with "the model never decides verdicts." Other recent reconciliation repos (reconiq, Payout-reconciliation) already use that design. Explain it in the README, but don't make it the headline.

**Possible technical edge (unproven):** the input is a camera photo of *another phone's* screen (glare, tilt, moiré, many different payment apps), not a clean screenshot. Claim this only if §8 supports it.

---

## 5. Prior art already found (don't re-search from scratch)

| Project | What it does | How we differ |
|---|---|---|
| Ordermatrix (ordermatrix.in) | Order management for Instagram/WhatsApp sellers; screenshot upload + UTR entry, duplicate UTRs flagged | Seller-side SaaS, checks each order at the time; no per-rider cash settlement |
| PosBytz delivery app (posbytz.com/en/free-delivery-app/) | Rider app; photo/signature/geo-stamp per delivery; per-rider cash and end-of-shift settlement reports | Requires their POS and rider app |
| OZi Rider (Play Store) | Rider app generates UPI QR, confirms payments in real time, end-of-day expected vs collected | Requires their app and QR flow |
| RouteMile / FoodXpress for WooCommerce (github.com/codermillat/routemile-woocommerce) | Rider PWA, cash-on-delivery amounts, cash-in-hand total, cash settlement workflow | Requires WooCommerce; no UPI-vs-bank check |
| UPI SmartPay for WooCommerce (github.com/iampmpksamy/WordPress_UPI_SmartPay_For_WooCommerce) | Customer submits UTR/screenshot; staff verify by hand | Checkout-time, manual |
| OpenPayUPI (github.com/chaursia/OpenUpiPay, github.com/swikki099-ui/Pay) | Self-hosted gateway: decimal-suffix amounts, SMS/IMAP matching, Tesseract screenshot UTR, hashed-UTR dedup | Must be set up before money is collected |
| PayGate (pkg.go.dev/github.com/Phloraxx/payment-api) | Paise-fingerprint amounts + bank SMS matching | Same as above |
| fake_Upi (github.com/J0j1n/fake_Upi), ScamShield AI, scamdekho | Checks one screenshot for signs of forgery | We don't judge images; the bank record is the ground truth |
| UPI-Transaction-Extractor (github.com/gautamraj8044/UPI-Transaction-Extractor) | PaddleOCR field extraction from clean screenshots | Clean screenshots only; no reconciliation |
| reconiq (github.com/Aarti-panchal01/reconiq) | Razorpay AI Buildathon; Indian UPI and card settlement reconciliation, deterministic core | Gateway settlement files, not photos |
| Payout-reconciliation (github.com/swaroopt14/Payout-reconciliation) | Engine owns the numbers, AI writes only prose, ambiguous cases never forced | Payment processor / payout scope |
| tallyd (github.com/DaniyalMlk/tallyd) | General double-entry ledger + bank reconciliation | General bookkeeping |

**Gaps in this search:** general web search indexes GitHub poorly. Before Friday, spend 10 minutes on GitHub's own search: `rider cash settlement`, `UTR screenshot reconcile`, `payment screenshot bank statement`, `COD reconciliation UPI`. Add anything closer to this table.

---

## 6. Scope

### The one feature
**Inputs, for each shift:**
- For each rider: a name, the rider's total order value for the shift (entered by hand), and their photos.
- One payment record for the day or shift (format set by Q1).

**Output, for each rider:**
- verified UPI payments and their total
- photos that need checking, grouped by reason (§7)
- duplicates, with where the earlier claim came from
- **cash owed** = order total − verified UPI − UPI confirmed by the owner. While anything is unresolved, show a range: "owes ₹X, or ₹Y if the flagged payments are genuine".

**Output for the whole shift:** unclaimed credits, meaning money that arrived with no matching photo.

### Explicitly out of scope
- Cognito or user accounts (use Amplify branch password protection and document why)
- Any app for riders, or any change to how riders work
- Judging screenshots for forgery (ELA, layout checks)
- Live or real-time verification, gateways, SMS reading
- More than one payment-record format
- Multiple businesses or tenants (keep a `business_id` in keys anyway)
- Analytics, charts, exports beyond one results screen
- **Any tool that generates fake payment screenshots.** Don't build one, even for test data.

### Data rules
- **No real customer payment screens in the repo, in fixtures, or in the video.**
- Test photos come from Aaryan's own small transfers, photographed off a phone screen.
- All DynamoDB items carry a TTL (`expires_at`, default 7 days). S3 gets a lifecycle rule with the same horizon.

---

## 7. Verdict rules (deterministic; the model never decides)

The model only **extracts** fields from photos. Every verdict comes from these rules, run against the payment record.

### Per-photo extraction output (from Bedrock, validated in code)
```json
{
  "utr": "string of exactly 12 digits, or null",
  "amount_inr": "number, or null",
  "screen_time": "ISO-8601 in IST, or null",
  "payment_app": "gpay | phonepe | paytm | bhim | other | null",
  "status_text": "success | pending | failed | null",
  "payee_name": "string or null",
  "notes": "short free text on legibility"
}
```
Validation, in code, never trusted from the model:
- If `utr` doesn't match `^\d{12}$`, set it to null.
- If `amount_inr` isn't positive with at most 2 decimals, set it to null.
- Tell the model to **return null whenever it isn't sure**. A null is a normal result, not an error.

### Rules, applied in order for each photo
| Verdict | Condition | Counts toward cash owed? |
|---|---|---|
| `NOT_SUCCESS` | `status_text` is pending or failed | No; shown as "check this" |
| `UNREADABLE` | `utr` and `amount_inr` are both null | No; owner reviews the photo |
| `DUPLICATE` | valid `utr` already claimed by a **different** `photo_id` (any shift) | No; shows where the earlier claim came from |
| `VERIFIED` | valid `utr` found in the record, amount equal, claim succeeds (or the existing claim belongs to this same `photo_id`) | **Yes** |
| `AMOUNT_MISMATCH` | valid `utr` found, amount differs | No; "check this" |
| `PROBABLE` | `utr` null, or not in the record, **and exactly one** unclaimed credit with the same amount within ±`WINDOW_MIN` of `screen_time` | Only after the owner confirms with one tap |
| `AMBIGUOUS` | same as `PROBABLE` but **two or more** candidates | No; owner picks one |
| `NOT_FOUND` | no UTR match and no amount+time candidate | No; shown as "check this", never as fraud |

After all photos: credits in the shift window with no claim are `UNCLAIMED_CREDIT`.

Defaults: `WINDOW_MIN = 10`, configurable. All times in IST.

### Why a model misread can't cause a false accusation
Vision models reading degraded images can confidently invent plausible text. An invented UTR won't be in the record, so it falls through to the amount+time check and becomes `PROBABLE` or `AMBIGUOUS`, not `NOT_FOUND`, whenever a matching credit exists. Keep this ordering. Test it (§10).

### Exactly-once and ordering
- `photo_id` = SHA-256 of the image bytes, so the same file uploaded twice is the same photo.
- Extraction runs in parallel (Map state). **Reconciliation runs as one Lambda per shift**, processing photos sorted by `(screen_time, photo_id)`, so which photo "wins" a duplicate is deterministic.
- Claims use DynamoDB conditional writes, which protects against races across concurrent runs and shifts.
- Re-running the same shift must give the same result: a claim already owned by the same `photo_id` counts as success, not as a duplicate.
- A `PROBABLE` match also claims the candidate credit, marked `pending_confirm`, so two photos can't both take it. If the owner rejects the match, release the claim.

---

## 8. Bedrock extraction: test first (Friday morning, before building on it)

**What's known:**
- The closest published evidence (a 2026 preprint on photographed monitor screens) found frontier vision models near 98–99.7% exact-match with a task-specific prompt, and an OCR pipeline about 20 points lower.
- Photographed documents are measurably harder than clean ones; MDPBench reports an average drop of 17.8%.
- Glare and moiré are standard distortions in robustness benchmarks.
- Models reading degraded images can make things up.
- **No published results exist for our exact input.** Our own test is the only real answer.

**Test set:** about 30 photos of Aaryan's own UPI payments, photographed off a phone screen. Correct values come from his own transaction history.
- Conditions: straight on; about 30° angle; overhead glare; dim light; partly cut off
- Apps: GPay, PhonePe, Paytm (more if available)

**Candidates:**
- two Bedrock vision models, one cheaper and one stronger. Choose from what's available through ap-south-1 (check each model's page in the Bedrock docs for inference-profile IDs).
- Amazon Rekognition text detection, as a baseline

**Harness:** use AWS's sample repo https://github.com/aws-samples/ocr-with-aws-ai-services (compares Textract, Bedrock and Bedrock Data Automation on accuracy, cost and processing time), or a 50-line script. Credit whichever you use. Keep results in `docs/extraction-eval.md`.

**Measure for each photo × model:** UTR exact match, amount correct, returned null, **confident wrong UTR**, latency, approximate cost.

**What passes:**
- amounts nearly always correct
- **confident wrong UTRs close to zero**. Honest nulls are fine; the amount+time rule covers them.

**Cost levers to record for the writeup:**
- the model tier
- downscaling images to the smallest size that keeps accuracy
- Map concurrency (start at 4)

**Data residency:** these photos show customers' payments. Record which region the requests are actually processed in. India-only routing has been announced for some models; if the chosen model uses an APAC or global profile, say so in the writeup as a deliberate trade-off.

**If the results are weak:** drop the glare/angle claim from the pitch, make amount+time matching the main path, and say so honestly in the writeup.

---

## 9. Architecture (Ship It)

**Region:** ap-south-1 (Mumbai). **Runtime:** Python (current Lambda-supported version). **Infrastructure as code:** AWS SAM.

```
Amplify Hosting (mobile-first page, branch password protection)
        │
API Gateway (HTTP API)
        │
Lambda: api  ──►  S3 (presigned uploads: photos, payment record)
        │
        └─► Step Functions (Standard) execution per shift run
              1. ParseRecord      Lambda: parse payment record → CREDIT items
              2. ExtractPhotos    Map (MaxConcurrency 4) → Lambda: Bedrock → PHOTO items
              3. Reconcile        Lambda: sorted, single writer → verdicts, CLAIM items, RIDER totals
              4. Finalize         Lambda: status = done
        │
DynamoDB (single table, TTL)          CloudWatch (structured JSON logs, 1 dashboard)
```

### API
| Method | Path | Purpose |
|---|---|---|
| POST | `/shifts` | create a shift `{business_id, date, riders:[{name, order_total}]}` |
| POST | `/shifts/{id}/uploads` | returns presigned PUT URLs for photos (tagged by rider) and the payment record |
| POST | `/shifts/{id}/run` | start the Step Functions execution (idempotent per upload set) |
| GET | `/shifts/{id}` | status + per-rider results + unclaimed credits |
| POST | `/shifts/{id}/photos/{photo_id}/resolve` | owner confirms/rejects `PROBABLE`, or picks one for `AMBIGUOUS` |

**Access:** there are no accounts. Use a shared secret header plus API Gateway throttling as the minimum, and write it down as a deferred decision (Cognito would be next). Don't pretend this is production security.

### DynamoDB single table `recon`
| PK | SK | Notes |
|---|---|---|
| `BIZ#{biz}` | `CREDIT#{utr}` | from the payment record; if a row has no reference, use `CREDIT#H#{sha256(date,time,amount,narration)}` |
| `BIZ#{biz}` | `CLAIM#{utr_or_credit_key}` | `attribute_not_exists(SK)`; stores `photo_id`, `shift_id`, `rider`, `state` (`final` / `pending_confirm`) |
| `SHIFT#{shift}` | `META` | status, created_at, execution ARN |
| `SHIFT#{shift}` | `RIDER#{name}` | order_total, verified_total, cash_owed_min/max |
| `SHIFT#{shift}` | `PHOTO#{photo_id}` | rider, s3 key, extraction JSON, verdict, candidate credit keys |

Every item has an `expires_at` TTL.

### S3 layout
`uploads/{shift_id}/record/{filename}` · `uploads/{shift_id}/photos/{rider}/{photo_id}.jpg`. Block public access, turn on server-side encryption, add a lifecycle expiry.

### Observability
- Structured JSON logs carrying `shift_id`, `photo_id` and `verdict`.
- One CloudWatch dashboard: executions, Map failures, Bedrock latency, verdict counts.
- Aaryan knows OTel well, but keep this light. It isn't the feature.

### Frontend
One page, mobile-first:
1. create shift (riders + totals)
2. upload photos per rider + payment record
3. run
4. results: per rider, a card with cash owed and a "check these" list with photo thumbnails and one-tap resolve

- Big tap targets.
- **Labels in Tamil and English. Tamil strings must be checked by a native speaker before the video**; don't ship unreviewed machine translation.
- Plain HTML/JS or a small React build; whichever is faster.

---

## 10. Tests (these are the screening-substitute signal; write them early)

- **Unit tests, one or more per verdict** in §7, using hand-written extraction JSON and credit fixtures. No Bedrock calls in unit tests.
- **Misread safety:** a made-up UTR with a matching amount and time must come out `PROBABLE`, never `NOT_FOUND`. Two candidates must come out `AMBIGUOUS`.
- **Idempotent re-run:** reconciling the same shift twice gives identical verdicts and no self-duplicates.
- **Same bytes uploaded twice:** one `photo_id`, one claim.
- **Concurrency:** against DynamoDB Local (or a test table), N parallel workers try to claim the same UTR, and exactly one succeeds. This test is part of the video.
- **Cash owed:** min/max range correct with unresolved items; collapses to one number once all are resolved.
- **Parser:** fixture-based tests for the Q1 format, including a row with no reference.
- **Deterministic ordering:** shuffling the photo input order doesn't change which photo wins a duplicate.

Suggested tools: `pytest`, `moto` or DynamoDB Local, `hypothesis` for the ordering property if time allows.

---

## 11. Suggested repo layout

```
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

Keep `reconcile/` as pure functions with the DynamoDB layer separate, so the verdict engine can be tested without AWS.

---

## 12. Deliverables

### README (design-doc style)
1. The problem (Brindhavan, one paragraph)
2. What it does (one feature)
3. Architecture diagram + why each service
4. Verdict rules and why the model never decides
5. Exactly-once design (conditional writes, `photo_id`, single-writer reconcile)
6. Extraction evaluation results (real numbers)
7. Cost decisions (model tier, image size, concurrency, TTL)
8. Deferred decisions (Cognito, multiple formats, multiple businesses, data residency)
9. What I learned (only genuinely new things: Bedrock multimodal, Step Functions/Map, DynamoDB conditional writes vs the Redis idempotency I already knew, SAM, Amplify. **Not S3/CloudFront/EC2**, which were used before.)
10. Prior art and how this differs (§5)
11. AI tools used

### Video (3:00 maximum)
| Time | Content |
|---|---|
| 0:00–0:20 | Brindhavan's problem, in the owner's words if he agrees (Q4/Q5) |
| 0:20–1:00 | Upload flow on a phone |
| 1:00–1:40 | Results: a flagged photo and one rider's corrected cash total ("owes ₹1,240, not ₹940") |
| 1:40–2:20 | AWS on screen: Step Functions execution graph, DynamoDB duplicate claim item, Bedrock extraction output |
| 2:20–2:50 | Concurrency test passing; cost decision |
| 2:50–3:00 | What I learned |

### Writeup
The full pitch (§3) plus the README highlights and the AI tools list. If time allows, also publish it as an AWS Builder Center post (a separate prize, and it stays on Aaryan's public profile).

---

## 13. Timeline

| When | Must be done | Checkpoint |
|---|---|---|
| **Thu (today)** | Builder Center student verification; repo created + first commit; SAM hello-world deployed to ap-south-1; Bedrock model access confirmed; 20–30 test photos taken; Q1–Q5 asked | A deployed endpoint returns 200 |
| **Fri morning** | §8 extraction test run and written up | Model chosen, pitch claim kept or dropped |
| **Fri afternoon/night** | Parser (fixture), reconcile engine + all §10 unit tests, claim layer + concurrency test, Step Functions end-to-end **from the CLI** | A full shift reconciles from the CLI |
| **Sat** | Frontend on Amplify; resolve flow; dashboard; **submit a rough version**; record the video Saturday night | A live URL works on a phone |
| **Sun** | README, writeup, AI tools list, Builder Center post; polish; re-record only if needed; final submit well before the deadline | Submitted |

### Where it's most likely to break
1. **Bedrock access, region or quota surprises.** Discover these Thursday, not Friday.
2. **IAM and passing S3 image bytes into Bedrock inside Step Functions.** This is the steepest learning curve. Call Bedrock from a Lambda; don't try Step Functions' direct Bedrock integration for images.
3. **Payment-record format.** Blocked on Q1. Support exactly one format.
4. **Frontend time sink.** Keep it to one page.
5. **Leaving the video to Sunday.** Record Saturday night.
6. **Over-building the correctness layer while the README and video wait.** Aaryan's known tendency, given his background.

---

## 14. Status checklist

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

---

## 15. Rules for the Claude Code session

1. Stay inside §6 scope. Propose additions; don't build them unasked.
2. Small commits with clear messages. No squashing the history into one commit. Never backdate.
3. Don't copy code from any repo in §5 or from `mcp-studio`. Design ideas get a credit in the README.
4. No real customer data anywhere in the repo. No fake-screenshot generators.
5. Never write accuracy or cost numbers that weren't measured.
6. Add an entry to `docs/DECISIONS.md` whenever a decision is made or changed.
7. Keep the verdict engine pure and fully tested before wiring AWS around it.
8. Ask Aaryan before changing the verdict rules in §7. They're the core of the product and of the "no false accusations" promise.

---

## 16. Decision log so far (don't reopen without new evidence)

| Idea | Status | Reason |
|---|---|---|
| Distributed LLM inference over WebRTC (and its reframes) | Dead | Own benchmark: WebRTC overhead roughly halved throughput; still needs connectivity; SwarmLLM already ships the flagship demo; weak AWS fit |
| mcp-studio | Dead for this event | Existing public project; rules forbid prior work |
| Agent action firewall + idempotent ledger (+ "tree-aware settlement") | Dead | Crowded (AgentGate, agent-ledger, @keelstack/guard, AWS Powertools Idempotency); abstract demo; home turf, so weak Learning score and prior-work risk |
| College fest UPI reconciliation | Dead | VIT registers events through a central portal; no real user |
| Small-merchant screenshot verification | Dead | Crowded (Ordermatrix, Razorpay links, UroPay); merchants need to verify before shipping, which isn't a batch job |
| Aggregator (Swiggy/Zomato) rider photos | Not pursued | The platform already owns that flow |
| **Own-delivery restaurant rider reconciliation** | **Chosen** | Real user confirmed (Brindhavan); fits the batch differentiator; fits Aaryan's payments background; legible demo |
