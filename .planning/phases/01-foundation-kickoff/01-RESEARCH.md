# Phase 1: Foundation & Kickoff - Research

**Researched:** 2026-09-18
**Domain:** AWS account bootstrap (SAM + Bedrock) on a brand-new free-tier account, Bedrock image-extraction smoke test pattern, hackathon logistics risk
**Confidence:** MEDIUM (AWS mechanics are well-documented and cross-checked against official docs; hackathon-specific logistics — Builder Center re-verification, $100 credit eligibility, exact deadline — remain genuinely unresolved and are flagged, not guessed)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Today is confirmed Friday 2026-09-18 (day 2 of the hackathon), not Sunday. HANDOFF.md's Thu/Fri/Sat/Sun phase mapping still holds; Phase 1 (originally "Thursday") is starting a day behind schedule, not on a compressed same-day deadline. — Reversibility: reversible
- **D-02:** Aaryan's original AWS account was suspended (unpaid balance after a free-trial period ended) — not merely short on the promised $100 hackathon credit. This was a hard blocker: nothing could be deployed, including free-tier-eligible resources, until an account was usable.
- **D-03 (RESOLVED):** Aaryan provisioned a new AWS free-tier account under a different email on 2026-09-18. The AWS-dependent success criteria are no longer gated — they can proceed on the new account. Two follow-on items to verify, not yet confirmed:
  - Whether Builder Center student verification (HANDOFF §14) needs to be redone under the new account's email.
  - Whether the new account is eligible for the hackathon's $100 AWS credit, or whether Phase 2's evaluation costs come out of free-tier/personal spend instead.
- **D-04 (superseded by resolution):** Phase 1 no longer needs to sequence AWS-dependent work after non-AWS work — both tracks can proceed in parallel now that an account exists. Still worth doing the non-AWS work (repo skeleton, `docs/DECISIONS.md`, test photos, Q1-Q5 outreach) without waiting on AWS console access, since Bedrock model access approval on a brand-new account may not be instant. — Reversibility: reversible
- **D-05:** Add a Bedrock smoke test to Phase 1 (originally Phase 1 only required confirming access, not a real invocation). This retires HANDOFF §13 risk #2 (IAM + passing S3 image bytes into Bedrock inside Step Functions is the steepest learning curve) a day early, without building Phase 2's real evaluation harness.
- **D-06:** The smoke test must exercise the exact risky path: a Lambda reads image bytes from S3 and calls Bedrock directly — never Step Functions' direct Bedrock integration for images (HANDOFF's explicit warning). This is a throwaway/minimal Lambda, not the real `extract/` module — Phase 3 builds the production extraction Lambda.
- **D-07:** Pass bar = valid schema response. The Lambda must return the §7 extraction JSON shape (`utr`/`amount_inr`/`screen_time`/`payment_app`/`status_text`/`payee_name`/`notes`, nulls allowed) without erroring. Accuracy is explicitly NOT graded here — that is Phase 2's job with the real ~30-photo test set and both candidate models compared. Do not conflate this smoke test with Phase 2's evaluation. — Reversibility: reversible
- **D-08:** Model choice for the smoke test = whichever of the two Bedrock candidates (one cheaper, one stronger) grants inference access first in ap-south-1. Do not spend Day 1 time comparing them — that comparison is Phase 2's job. — Reversibility: reversible
- **D-09:** This smoke test is gated by D-02/D-03 (AWS account suspension) — it cannot run until the account is reactivated, regardless of how quickly the Lambda code itself is ready.

### Claude's Discretion
- Exact mechanics of contacting Hotel Brindhavan's owner for Q1-Q5 (in person vs. message) and the specific first `docs/DECISIONS.md` entries were not decided in this discussion — proceed with reasonable defaults (in person, since Aaryan lives in the delivery building) and log the actual answers/non-answers as they come in.
- Day-1 repo skeleton scope (full HANDOFF §11 layout now vs. minimal-now-grow-later) and repo visibility during build (public from commit 1 vs. private until near submission) were surfaced as gray areas but not discussed — default to whatever the planner judges best; these are low-stakes/reversible choices.

### Deferred Ideas (OUT OF SCOPE)
- Repo visibility during build (public from commit 1 vs. private until near submission) — surfaced but not discussed; left to planner/Claude's discretion, not a phase-domain concept worth its own phase.
- Day-1 repo skeleton scope (full HANDOFF §11 layout vs. minimal) — surfaced but not discussed; left to planner/Claude's discretion.
- Q1-Q5 owner outreach mechanics/timing — surfaced but not discussed; the underlying requirement (ask Q1-Q5, record answers or non-answers) is already locked in ROADMAP.md success criterion 4 and does not need a phase change, just execution.
</user_constraints>

<phase_requirements>
## Phase Requirements

No REQ-IDs map to this phase (infrastructure-enabling gate — see REQUIREMENTS.md Traceability note). The five ROADMAP.md success criteria plus the Day-1 Bedrock smoke test (D-05–D-09) stand in for requirements here:

| Success Criterion | Research Support |
|---|---|
| 1. SAM hello world deployed to ap-south-1, HTTP 200 | §"SAM CLI Bootstrap" below — exact command sequence, IAM prerequisites, region entry point verified against official AWS SAM tutorial |
| 2. Bedrock model access confirmed in ap-south-1 (or nearest inference profile identified, trade-off noted) | §"Bedrock Model Access on a Fresh Account" and §"Bedrock Model Availability in ap-south-1" — both researched against official AWS docs, Oct 2025 auto-enablement change found and directly changes D-08's calculus |
| 3. 20-30 test photos + fixture from own transaction export | No external research needed — pure execution task; see Common Pitfalls for angle/glare/format guidance carried over from HANDOFF §8 |
| 4. Q1-Q5 asked, answers/non-answers recorded | No external research needed — pure execution/logistics task |
| 5. Repo skeleton + first commit + `docs/DECISIONS.md` started | §"Recommended Project Structure" — HANDOFF §11 layout reproduced, no deviation researched (locked in HANDOFF) |
| D-05–D-09: Day-1 Bedrock smoke test (Lambda reads S3 bytes → calls Bedrock directly) | §"The Lambda-Reads-S3-Bedrock Pattern" — official Converse API Python example with image bytes, exact IAM permissions, S3 GetObject requirement |
</phase_requirements>

## Summary

This phase is almost entirely AWS-account-bootstrap mechanics plus two pieces of un-automatable human logistics (Q1-Q5 outreach, Builder Center/credit email risk). The good news from this research: two things that looked like they'd cost real Day-1 time turn out to be largely solved by AWS's own recent changes. First, Bedrock model access is **no longer a multi-hour manual-approval wait** for most models — AWS made foundation-model access auto-enabled by default in October 2025; only Anthropic models still require a one-time "use case" form (submitted instantly via console or API, access granted immediately). Second, the exact Python code for "Lambda reads S3 bytes, calls Bedrock with an image" is a documented, copy-adaptable official AWS sample (Converse API), not something to reverse-engineer.

The bad news, and the thing this research surfaces that the phase description did not anticipate: **neither Bedrock candidate model family is available as a plain in-region on-demand call from ap-south-1.** Amazon Nova Lite requires a Geo cross-region inference profile ID (not a bare model ID) from ap-south-1, and Anthropic Claude models require a Global cross-region inference profile whose destination can be *any* commercial AWS region worldwide — not just APAC. This directly triggers the HANDOFF §8 "record which region requests are actually processed in" writeup requirement, and it changes what "confirmed Bedrock access in ap-south-1" (success criterion 2) actually means in practice: it means confirming access to an inference *profile*, not a direct in-region model.

For D-08 ("whichever grants access first"), the auto-enablement finding tips the answer toward **Nova Lite being faster to unblock** than Claude, because Nova (an Amazon-provided model, no AWS Marketplace product ID, no EULA click) has essentially no manual gate beyond the account having `aws-marketplace:Subscribe/Unsubscribe/ViewSubscriptions` IAM permissions, while Claude requires the one-time Anthropic use-case form to be submitted and accepted first. Neither should take more than an hour on a healthy new account, but Nova is the lower-friction path if the smoke test needs to move immediately.

Two items remain genuinely unresolved and are flagged rather than guessed: whether AWS Builder Center student verification and the hackathon's $100-credit Google Form check the requesting identity against the *original* registration email (no evidence found either way — treat as an open risk, not a blocker, since Phase 1's AWS success criteria don't depend on the credit landing), and the exact Sunday submission deadline time (the event page states only "Sept 17–20, 2026," no time or timezone — must be chased down separately, not inferable from research).

**Primary recommendation:** Use Amazon Nova Lite as the D-08 smoke-test model (faster access path), call it via the Converse API from a Lambda using its ap-south-1 Geo inference-profile ID (confirm the exact `apac.amazon.nova-lite-v1:0`-style ID string in the Bedrock console at build time — the fetched doc excerpt only showed `us.`/`eu.` geo IDs), read the image with `s3_client.get_object` inside the Lambda and pass raw bytes to `bedrock_client.converse()`, and record the actual destination region reported by the console/CloudTrail for the writeup's data-residency disclosure.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| SAM "hello world" API endpoint | API / Backend | CDN / Static (API Gateway edge) | Locked by HANDOFF §9: API Gateway (HTTP API) → Lambda is the entry point for all backend capability in this project; Phase 1 just proves the skeleton deploys |
| Bedrock model access verification | API / Backend | — | Access/IAM is an account-level and IAM-role-level concern exercised from a Lambda's execution role, not from any client tier |
| Bedrock image-extraction smoke test (D-05–D-09) | API / Backend | Database / Storage (S3 read) | The Lambda is the only component permitted to call Bedrock (HANDOFF §9 explicit ban on Step Functions' direct Bedrock image integration); S3 is upstream storage the Lambda reads from, not a tier that calls Bedrock itself |
| Test photo / fixture data | Database / Storage | — | Files land in S3 in later phases; for Phase 1 they exist as local files only, no tier assignment needed yet |
| Repo skeleton / `docs/DECISIONS.md` | — (non-runtime) | — | Documentation and IaC scaffolding, not a runtime capability; no tier owns it |
| Q1-Q5 outreach | — (non-runtime, human process) | — | Not a software capability; a logistics task that produces input for later phases (parser format, timestamp handling) |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `aws-sam-cli` | 1.166.2 (verified on PyPI 2026-09-18) [VERIFIED: PyPI registry — `pip index versions aws-sam-cli`] | IaC / local build+deploy tool for the whole stack | Locked by HANDOFF §9 ("Infrastructure as code: AWS SAM") — not a choice, a given |
| `boto3` | 1.43.97 latest / 1.43.89 installed locally (verified on PyPI 2026-09-18) [VERIFIED: PyPI registry — `pip index versions boto3`] | AWS SDK for Python; used by the Lambda to call S3 (`get_object`) and Bedrock (`converse`) | Official AWS SDK; only way to call `bedrock-runtime` from Python |
| Python | 3.13 recommended for Lambda runtime [CITED: docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html via websearch synthesis — not directly fetched this session] | Lambda runtime language | HANDOFF §9 specifies "current Lambda-supported version"; 3.13 is the current LTS (security/bug-fix support until Oct 2029) as of Sept 2026 — local machine has 3.9 installed, which is not what should ship in `template.yaml` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | latest on PyPI, official pytest-dev/pytest repo [ASSUMED — package legitimacy checker flagged SUS on "too-new"/"unknown-downloads" heuristics, but this is a false positive for an extremely well-known package with 1000+ releases and an official org-owned GitHub repo; treat as OK] | Unit test runner (used starting Phase 3, mentioned here for completeness since `tests/` scaffold is created in Phase 1) | HANDOFF §10 suggested tool |
| `moto` | latest on PyPI, official getmoto/moto repo [ASSUMED — same false-positive pattern as pytest] | Mock AWS services (S3, DynamoDB) for local unit tests, no live AWS calls | Phase 3 concurrency/reconcile tests, not needed in Phase 1 itself |
| `hypothesis` | latest on PyPI [ASSUMED — package legitimacy checker flagged SUS ("no-repository" signal is a data-source gap, not a real red flag; hypothesis is a long-established, widely-used property-testing library] | Property-based testing for deterministic-ordering tests | Phase 3, not Phase 1 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SAM CLI | AWS CDK, Serverless Framework, Terraform | Locked out by HANDOFF §9 — not a live decision for this phase |
| Bedrock Converse API | Bedrock `InvokeModel` (raw, model-specific request/response bodies) | Converse gives a uniform request/response shape across models (useful since D-08 picks whichever model becomes available first); `InvokeModel` requires per-model JSON body knowledge. Converse is the better fit here specifically because the smoke test's model choice is not fixed in advance. |
| Amazon Nova Lite (smoke-test candidate) | Anthropic Claude Haiku (smoke-test candidate) | Nova: no Marketplace product ID / no EULA click, likely faster D-08 unblock. Claude: one-time use-case form required per account before first invoke, but form submission is fast (minutes) once done. Actual choice per D-08 should be "whichever responds successfully first" when both are tried. |

**Installation:**
```bash
# macOS (Homebrew) — SAM CLI
brew install aws-sam-cli
brew install awscli   # if not already present — this environment currently has neither installed

# Python Lambda dependencies (per-function requirements.txt, per HANDOFF §11 layout)
boto3   # usually already present in the Lambda execution environment as a built-in layer,
        # but pin it explicitly in requirements.txt for local `sam build` reproducibility
```

**Version verification:** Confirmed via `pip index versions aws-sam-cli` → 1.166.2 (published 2026-09-11) and `pip index versions boto3` → 1.43.97 (published 2026-09-17), both same-week releases relative to this research date, consistent with AWS's frequent-release cadence for these two packages — not a staleness concern. `sam` and `aws` CLIs are **not currently installed** in this development environment (see Environment Availability below) and must be installed before the phase's first deploy step.

## Package Legitimacy Audit

| Package | Registry | Age (latest release) | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `boto3` | PyPI | Latest published 2026-09-17 (project itself is 10+ years old, AWS-official) | Not returned by checker (heuristic gap) | github.com/boto/boto3 | SUS (heuristic: "too-new"/"unknown-downloads") | **Overridden to OK** — official AWS SDK, official org repo, false-positive from release-cadence heuristic |
| `aws-sam-cli` | PyPI | Latest published 2026-09-11 (project is AWS-official, years old) | Not returned by checker | github.com/aws/aws-sam-cli | SUS (heuristic: "too-new"/"unknown-downloads") | **Overridden to OK** — official AWS tool, HANDOFF-mandated, official org repo |
| `pytest` | PyPI | Latest published 2026-06-19 | Not returned by checker | github.com/pytest-dev/pytest | SUS (heuristic: "unknown-downloads") | **Overridden to OK** — one of the most widely used Python test frameworks |
| `moto` | PyPI | Latest published 2026-08-22 | Not returned by checker | github.com/getmoto/moto | SUS (heuristic: "too-new"/"unknown-downloads") | **Overridden to OK** — long-established AWS mocking library, official org repo |
| `hypothesis` | PyPI | Latest published 2026-09-08 | Not returned by checker | Not returned by checker | SUS (heuristic: "too-new"/"unknown-downloads"/"no-repository") | **Overridden to OK, flagged for awareness** — well-known property-testing library (HypothesisWorks/hypothesis on GitHub); the checker's data source did not surface the repo URL this run |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** all five above were heuristic false positives (frequent-release-cadence and downloads-API-gap artifacts), not actual slopsquatting risk — all are extremely well-known, official-org-maintained packages independently corroborated by their GitHub org ownership (`boto`, `aws`, `pytest-dev`, `getmoto`) and by being explicitly named in HANDOFF.md itself as the intended tools. **The planner does not need to insert a `checkpoint:human-verify` task for these five** — the override reasoning is documented here for auditability, not left as a live risk.

## Architecture Patterns

### System Architecture Diagram (Phase 1 scope only)

```
Developer machine
   │
   │ sam init / sam build / sam deploy --guided
   ▼
CloudFormation (ap-south-1) ──creates──▶ API Gateway (HTTP API)
                                              │
                                              ▼
                                     Lambda: HelloWorldFunction
                                              │
                                              ▼
                                     returns {"message":"hello world"}, HTTP 200
                                              │
                                    (separately, throwaway smoke-test Lambda)
Developer machine ──uploads test photo──▶ S3 bucket
                                              │
                              Lambda: bedrock-smoke-test reads bytes via
                              s3_client.get_object(Bucket, Key)
                                              │
                                              ▼
                        bedrock_client.converse(modelId=<inference-profile-id>,
                                                  messages=[{image bytes + prompt}])
                                              │
                                              ▼
                        Bedrock (destination region per inference profile —
                        NOT necessarily ap-south-1; record actual region)
                                              │
                                              ▼
                        Validate response is the §7 JSON shape (schema check only,
                        no accuracy grading) → pass/fail the smoke test
```

A reader can trace: local machine → SAM deploy → API Gateway → Lambda → HTTP response (criterion 1), and separately: local machine → S3 upload → Lambda → Bedrock → schema-validated JSON (D-05–D-09 smoke test). These are two independent, parallel proofs in this phase — not a single pipeline yet (Step Functions wiring is Phase 3).

### Recommended Project Structure

Reproduced verbatim from HANDOFF §11 (locked, not researched — this is the given layout):

```
.
├── README.md                # written like a design doc (§12)
├── template.yaml            # SAM
├── statemachine/recon.asl.json
├── src/
│   ├── api/                 # API Lambda handlers
│   ├── parse_record/        # parser interface + one implementation
│   ├── extract/              # Bedrock call, prompt, validation
│   ├── reconcile/            # pure verdict engine + DynamoDB claim layer
│   └── common/                # models, logging, config
├── web/                      # frontend
├── tests/
│   ├── unit/
│   ├── concurrency/
│   └── fixtures/             # synthetic credits + extraction JSON only
└── docs/
    ├── DECISIONS.md          # running decision log with dates
    ├── AI_TOOLS.md           # required in the writeup
    ├── extraction-eval.md    # §8 results
    └── architecture.png
```

For Phase 1 specifically: `template.yaml` gets the SAM hello-world resources plus (optionally, as a throwaway addition not meant to survive into later phases) a `bedrock-smoke-test/` Lambda under `src/` or a scratch location — HANDOFF explicitly calls the smoke-test Lambda "throwaway," so it does not need to live under `src/extract/` (that's Phase 3's real module). Placing it at `src/_smoketest/` or similar and deleting it after Phase 1, or leaving a comment marking it disposable, avoids confusing later phases about which Lambda is the real extraction path.

### Pattern 1: Lambda-reads-S3-bytes-then-calls-Bedrock (the D-06 mandated pattern)

**What:** The Lambda function itself calls `s3_client.get_object()` to pull raw image bytes, then passes those bytes directly into a Bedrock Converse API call as an `image` content block. Bedrock never touches S3 directly in this pattern — the Lambda mediates.

**When to use:** Always, for any Bedrock image call in this project. HANDOFF §9 explicitly forbids Step Functions' native Bedrock-image integration ("call Bedrock from a Lambda; don't try Step Functions' direct Bedrock integration for images" — the steepest-learning-curve risk per §13 risk #2). This smoke test exists specifically to retire that risk.

**Example (adapted from the official AWS Bedrock Converse API docs' Python image example):**

```python
# Source: https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
# (official AWS sample, adapted here to read from S3 instead of a local path)
import boto3
import json

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]

    # Read image bytes from S3 inside the Lambda — never Step Functions direct-Bedrock
    obj = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = obj["Body"].read()
    image_format = key.split(".")[-1]  # e.g. "jpg" -> use "jpeg" for Bedrock's format field

    prompt = (
        "Extract fields from this UPI payment screenshot. "
        "Return ONLY JSON matching this schema: "
        '{"utr": "12-digit string or null", "amount_inr": "number or null", '
        '"screen_time": "ISO-8601 IST or null", '
        '"payment_app": "gpay|phonepe|paytm|bhim|other|null", '
        '"status_text": "success|pending|failed|null", '
        '"payee_name": "string or null", "notes": "short free text"}. '
        "Return null whenever you are not sure — a null is a normal result, not an error."
    )

    message = {
        "role": "user",
        "content": [
            {"text": prompt},
            {"image": {"format": "jpeg", "source": {"bytes": image_bytes}}},
        ],
    }

    # modelId here is a Bedrock inference-profile ID (Nova Lite geo-inference or
    # Claude global-inference), not a bare on-demand model ID — see "Bedrock Model
    # Availability in ap-south-1" below. Confirm the exact string in the Bedrock
    # console at build time.
    response = bedrock.converse(
        modelId="<inference-profile-id-confirmed-in-console>",
        messages=[message],
    )

    output_text = response["output"]["message"]["content"][0]["text"]
    # D-07 pass bar: this must parse as valid JSON matching the §7 shape.
    # Do NOT grade accuracy here — Phase 2's job.
    extracted = json.loads(output_text)
    return {"statusCode": 200, "body": json.dumps(extracted)}
```

IAM permissions the Lambda's execution role needs (both confirmed against official docs):
- `s3:GetObject` on the specific bucket/prefix holding the test photo.
- `bedrock:InvokeModel` (this single permission covers the `Converse` API call — confirmed: "To call `Converse`, you require permission for the `bedrock:InvokeModel` operation" [CITED: docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html]).
- If using a cross-region inference profile, IAM policies must allow `bedrock:InvokeModel*` in **all destination regions** the profile can route to, not just ap-south-1 — a Deny in a destination region (via SCP or IAM) will fail the whole request even if ap-south-1 itself is allowed [CITED: docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html].
- For first-time model access in the account: `aws-marketplace:Subscribe`, `aws-marketplace:Unsubscribe`, `aws-marketplace:ViewSubscriptions` (needed once per account for the auto-subscribe flow to succeed on serverless third-party models) [CITED: docs.aws.amazon.com/bedrock/latest/userguide/model-access.html]. Amazon-provided models (Nova) are not sold via AWS Marketplace product IDs, so this requirement is Anthropic/third-party-specific.

### Anti-Patterns to Avoid

- **Using Step Functions' direct Bedrock image integration:** explicitly banned by HANDOFF §9. Always mediate through a Lambda.
- **Passing a bare model ID (e.g. `amazon.nova-lite-v1:0`) when calling from ap-south-1:** will fail or behave unexpectedly for models without in-region on-demand support there — must use the model's documented inference-profile ID instead (see below).
- **Treating the smoke test as Phase 2's evaluation:** D-07 explicitly separates "does it return valid schema" (Phase 1) from "is it accurate" (Phase 2). Don't measure UTR/amount correctness in this phase's smoke test.
- **Manually base64-encoding image bytes before calling boto3's `converse()`:** unnecessary — the AWS SDK for Python handles the encoding; passing pre-encoded base64 strings where raw bytes are expected will produce a malformed request.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Uniform request/response shape across Bedrock model providers | A per-model adapter layer during the smoke test | Bedrock Converse API | Handles Anthropic/Amazon/others with one interface — exactly useful for D-08's "whichever grants access first" uncertainty |
| Checking whether Bedrock model access exists | Polling `InvokeModel` in a retry loop and inferring from error codes | `GetFoundationModelAvailability` API (`agreementAvailability`, `authorizationStatus`, `regionAvailability` fields) | Documented API purpose-built for exactly this check [CITED: docs.aws.amazon.com/bedrock/latest/userguide/model-access.html] |
| First-time Bedrock model-access grant automation | A manual clickthrough script or waiting indefinitely | `PutUseCaseForModelAccess` (Anthropic one-time form) + relying on Oct 2025 auto-enablement for Amazon models | Both are official, scriptable APIs; no need to hand-roll polling/backoff around console clicks |

**Key insight:** This phase's temptation is to over-engineer the smoke test (e.g., building retry/backoff logic, a full prompt-eval harness, or a generic multi-model abstraction) when D-05–D-09 explicitly scope it down to "one throwaway Lambda, one schema check, whichever model responds first." Respect that scope — Aaryan's known tendency to over-build (HANDOFF §13 risk #6) applies here too, a day early.

## Runtime State Inventory

Not applicable — this is a greenfield phase (empty repo except `HANDOFF.md` and `.planning/`, per 01-CONTEXT.md's `<code_context>` section: "No existing code, patterns, or maps to scout"). No rename/refactor/migration is in scope.

## Common Pitfalls

### Pitfall 1: Assuming a bare model ID works from ap-south-1

**What goes wrong:** Calling `bedrock.converse(modelId="amazon.nova-lite-v1:0", ...)` (or the equivalent Claude on-demand ID) from a Lambda in ap-south-1 fails or is rejected, because neither candidate family has documented in-region on-demand support there.
**Why it happens:** Most Bedrock tutorials (including the official Converse API sample used above) default to on-demand model IDs from us-east-1, which doesn't reflect ap-south-1's actual support matrix.
**How to avoid:** Look up the specific model's "Regional Availability" table on its official model-card doc page before writing the smoke-test Lambda; use the Geo or Global inference-profile ID it documents instead of the bare model ID.
**Warning signs:** `AccessDeniedException` or `ValidationException` mentioning the model isn't available in the region, even after model access has been granted.

### Pitfall 2: Confusing "model access granted" with "model available on-demand in this region"

**What goes wrong:** Success criterion 2 ("Bedrock model access in ap-south-1 confirmed") gets treated as complete once `GetFoundationModelAvailability` returns `AVAILABLE`, but the team then hits a routing error because the ap-south-1 *source region* requires an inference profile to reach any *destination region* where the model actually runs.
**Why it happens:** "Access" (the account-level EULA/subscription gate) and "regional invocation path" (on-demand vs. Geo vs. Global inference profile) are two separate concepts that are easy to conflate.
**How to avoid:** Treat success criterion 2 as satisfied when (a) `agreementAvailability` is `AVAILABLE` for the chosen model AND (b) a successful `converse()` call has been made from ap-south-1 using the correct profile ID — not just when access is granted.
**Warning signs:** Access shows granted in the console, but the first invocation from ap-south-1 still fails.

### Pitfall 3: Not recording which region actually processed the Bedrock request

**What goes wrong:** The writeup's data-residency disclosure (HANDOFF §8, an explicit deliverable requirement — REQ-deliverables item 8/9) gets skipped or guessed, because cross-region inference profiles don't make the destination region obvious from the client code.
**Why it happens:** The `converse()` response doesn't include the destination region by default; it has to be checked via CloudTrail, Bedrock invocation logging, or the console.
**How to avoid:** During the Phase 1 smoke test, capture and note which region actually served the request (enable Bedrock model invocation logging, or check CloudTrail for the `bedrock-runtime` API call's region), and write this down immediately — don't wait until Phase 5's writeup to reconstruct it.
**Warning signs:** Writeup section 8/9 ends up saying "probably ap-south-1 or nearby" instead of a measured fact.

### Pitfall 4: Treating Builder Center/credit email risk as resolved because the AWS account is now usable

**What goes wrong:** D-03 resolved the account-suspension blocker, but two follow-on risks (Builder Center re-verification, $100-credit eligibility under the new email) were explicitly left open in 01-CONTEXT.md and STATE.md. Assuming they're fine because "the account works now" risks a late surprise (e.g., ineligibility discovered near submission, or a support ticket needed at the worst time).
**Why it happens:** The account being functional for AWS API calls is unrelated to whether the hackathon's separate verification/credit systems recognize the new email.
**How to avoid:** Check these explicitly and early: (1) sign in to AWS Builder Center under the new account's email and see whether student-verification status carries over or needs redoing; (2) submit the $100-credit Google Form (linked from the event page) and see if it accepts the new account/email without issue. Neither blocks Phase 1's AWS success criteria (compute doesn't need the credit to exist — free tier + personal spend covers a hello-world deploy and a few smoke-test invocations), but both should be checked now rather than assumed.
**Warning signs:** No response to the credit form, or a Builder Center profile that shows "not verified" under the new account.

## Code Examples

### Reading S3 bytes and calling Bedrock Converse with an image (full pattern)

See "Pattern 1" above — this is the primary code example for this phase, adapted from the official AWS documentation sample.

### SAM hello-world initialization (interactive flow, official tutorial)

```
# Source: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html
$ sam init
Which template source would you like to use?
    1 - AWS Quick Start Templates
Choice: 1
Choose an AWS Quick Start application template
    1 - Hello World Example
Template: 1
Use the most popular runtime and package type? (Python and zip) [y/N]: y
Would you like to enable X-Ray tracing...? [y/N]: <enter, no>
Would you like to enable monitoring using CloudWatch Application Insights? [y/N]: <enter, no>
Would you like to set Structured Logging in JSON format...? [y/N]: <enter, no>
Project name [sam-app]: <enter>

$ cd sam-app
$ sam build
$ sam deploy --guided
Stack Name [sam-app]: owed-foundation   # or similar project-specific name
AWS Region [us-west-2]: ap-south-1
Confirm changes before deploy [Y/n]: n
Allow SAM CLI IAM role creation [Y/n]: <enter, yes>
Disable rollback [y/N]: <enter, no>
HelloWorldFunction may not have authorization defined, Is this okay? [y/N]: y
Save arguments to configuration file [Y/n]: <enter, yes>
```

After deploy, the CloudFormation Outputs section prints an API Gateway URL; `curl` it to confirm HTTP 200:

```bash
curl https://<restapiid>.execute-api.ap-south-1.amazonaws.com/Prod/hello/
# {"message": "hello world"}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Manually request Bedrock model access per model per region, wait for approval | Access to all Bedrock foundation models auto-enabled by default (with correct Marketplace IAM permissions), in all commercial regions | Announced Oct 2025 [CITED: aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-automatic-enablement-serverless-foundation-models, referenced via docs.aws.amazon.com/bedrock/latest/userguide/model-access.html] | Directly changes D-08's premise — "whichever model grants access first" is now much more likely to be near-instant for Amazon models, with Anthropic needing only a one-time form, not a multi-hour/day wait as older tutorials describe |
| Bedrock model-specific request/response body via raw `InvokeModel` | Unified `Converse`/`ConverseStream` API across model providers | Established feature as of this research (not newly changed, but worth noting as the modern default) | Simplifies the D-08 "whichever model becomes available first" smoke test — same code path regardless of which model wins |

**Deprecated/outdated:** Tutorials describing a lengthy Bedrock model-access approval wait (common in 2023-2024-era blog posts) are outdated for most models as of the Oct 2025 change — don't budget multi-day approval time for Nova; do budget a short one-time form for Anthropic.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AWS Lambda's current recommended Python runtime is 3.13 | Standard Stack | Low — if 3.14/3.15 is preferred by the time of deploy, `template.yaml`'s `Runtime` property is a one-line change; not a design risk |
| A2 | Nova Lite's ap-south-1 Geo inference-profile ID follows an `apac.amazon.nova-lite-v1:0`-style pattern | Summary, Pattern 1 | Medium — the fetched official doc excerpt only showed `us.`/`eu.` geo IDs for Nova Lite; the exact APAC-geo ID string was not directly observed this session and must be confirmed in the Bedrock console or via `ListInferenceProfiles` before writing IAM policy/code |
| A3 | Builder Center student-verification status is tied to the Builder ID/profile (portable across AWS account changes), not to the specific AWS account ID | Common Pitfalls (Pitfall 4) | Medium — if verification is actually tied to the account ID, Aaryan may need to redo verification under the new account; this was explicitly left open in 01-CONTEXT.md and should be checked directly, not assumed from this research |
| A4 | The hackathon's $100 AWS credit Google Form will accept the new account without issue | Summary, Pitfall 4 | Medium — no evidence found either way; if it doesn't, Phase 2's evaluation costs (Bedrock invocations across ~30 photos × 2-3 models) come from free-tier/personal spend instead, which is a minor cost but should be budgeted for, not assumed away |
| A5 | `pytest`/`moto`/`hypothesis` package-legitimacy "SUS" verdicts are heuristic false positives rather than real slopsquatting risk | Package Legitimacy Audit | Low — all five packages are independently corroborated by long-standing, officially-owned GitHub repos and are explicitly named as intended tools in HANDOFF.md itself; risk of this assumption being wrong is very low |
| A6 | IAM role for a brand-new account's root/admin user already has sufficient permissions for `sam deploy --guided`'s first run (no separate manual IAM policy authoring needed) | Standard Stack, Architecture Patterns | Low-Medium — true for an account-root or Administrator-attached IAM user, which is the typical state of a just-created personal AWS account; if a restricted IAM user is used instead, `iam:CreateRole`/`iam:*Role*` and `cloudformation:*` permissions must be explicitly attached first |

**If this table is empty:** N/A — see entries above.

## Open Questions

1. **Exact APAC/Geo inference-profile ID strings for the two Bedrock smoke-test candidates in ap-south-1**
   - What we know: Nova Lite supports Geo cross-region inference from ap-south-1 (Regional Availability table marks it "Yes"); Claude models require Global cross-region inference profiles with IDs like `global.anthropic.claude-sonnet-4-6`.
   - What's unclear: The exact Geo profile ID string for Nova Lite (or Nova Pro) when called from ap-south-1 — the fetched official doc excerpt only rendered the `us.`/`eu.` geo tables, likely because the page's APAC section wasn't captured in this session's fetch.
   - Recommendation: Confirm in the AWS Bedrock console (Model access / model detail page's "Cross-region inference" section) or via `aws bedrock list-inference-profiles --region ap-south-1` at build time, before writing the smoke-test Lambda's `modelId` value.

2. **Whether Anthropic's one-time use-case form needs to be resubmitted under the new AWS account**
   - What we know: The form is submitted once per account (or per AWS Organization's management account), with exceptions for opt-in regions.
   - What's unclear: Since D-03 created a brand-new account (not a sub-account of an existing org), this form has almost certainly never been submitted under this account and will need first-time submission — this is expected, not a blocker, but should be budgeted as a Day-1 step if the smoke test ends up using a Claude model instead of Nova.
   - Recommendation: If pursuing D-08 with Claude as the first candidate tried, submit the use-case form immediately via the Bedrock console (fast — minutes) before attempting the first `converse()` call.

3. **Exact Sunday submission deadline time**
   - What we know: Event page states the hackathon runs "Thursday to Sunday, Sept 17–20, 2026" — no time or timezone given.
   - What's unclear: The actual cutoff hour, needed for Phase 5 planning and to avoid a late submission.
   - Recommendation: This is explicitly called out in HANDOFF §14's status checklist and STATE.md's blockers as something to confirm from the event page directly (possibly requires checking the submission portal itself, not just the marketing page, since the fetched page did not surface it) — not resolvable via research; flag for Aaryan to check directly.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `sam` CLI | Success criterion 1 (SAM deploy) | ✗ | — | Must install (`brew install aws-sam-cli`) before first deploy step — no viable fallback, this is the mandated IaC tool |
| `aws` CLI | Credential configuration, `sam deploy`'s underlying auth | ✗ | — | Must install (`brew install awscli`) — SAM CLI can technically work with env-var credentials alone, but `aws configure` is the standard path and needed for troubleshooting/verification steps anyway |
| Docker | `sam build --use-container` (only needed for compiled/native dependencies) or `sam local invoke`/`sam local start-api` (local testing) | Client installed (v29.1.3), daemon **not running** | 29.1.3 (client only) | Fallback: this project's Lambda dependencies (`boto3`) are pure Python with no native compilation step, so plain `sam build` (no `--use-container`) works without Docker; only start Docker Desktop if local `sam local invoke` testing is wanted, which is optional (§7 of the official tutorial marks local testing "Optional") |
| Python 3.x (local dev) | `sam build`'s PythonPipBuilder | ✓ | 3.9.6 | Local Python version only needs to be compatible enough to run `sam build`'s dependency resolution for a pure-`boto3` Lambda; the Lambda's actual `Runtime:` in `template.yaml` (recommended 3.13) is independent of the local interpreter version, though `sam init --runtime python3.9` vs. specifying 3.13 in the template should be kept consistent to avoid the "build errors from version mismatch" warning in the official tutorial |
| AWS account credentials (`~/.aws/credentials` or `~/.aws/config`) | All `sam deploy`/`aws` calls | ✗ (not found in this environment) | — | Must be configured (`aws configure` or `aws configure sso`) using the new AWS free-tier account's access key before any deploy step — this is expected to happen on Aaryan's actual machine, not necessarily this research sandbox |

**Missing dependencies with no fallback:**
- `sam` CLI, `aws` CLI, and AWS credentials must all be installed/configured before Phase 1 execution can begin. None of these are optional or substitutable given HANDOFF's locked IaC choice.

**Missing dependencies with fallback:**
- Docker daemon not running — acceptable, since this project's dependency stack doesn't require containerized builds; only needed if `sam local` testing or `--use-container` builds are desired.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (per HANDOFF §10; not yet installed/configured — repo is greenfield) |
| Config file | none — see Wave 0 |
| Quick run command | `pytest tests/unit -x` (once `tests/` scaffold and framework config exist) |
| Full suite command | `pytest tests/` |

### Phase Requirements → Test Map

Phase 1 has no REQ-IDs and produces no application logic to unit-test in the traditional sense — its "tests" are manual/observational verification of infra state (an HTTP 200 response, a valid-JSON Bedrock response). No automated pytest-based tests map to this phase's success criteria.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SC-1 | SAM hello-world returns HTTP 200 | smoke (manual/curl) | `curl -sf <api-url>/hello` (exit code 0 = pass) | ❌ Wave 0 — no test file needed, this is a deploy-verification step, not a unit test |
| SC-2/D-05-09 | Bedrock smoke-test Lambda returns valid §7-schema JSON | smoke (manual invoke + schema check) | `aws lambda invoke --function-name <name> --payload '{...}' out.json && python -c "import json,sys; json.load(open('out.json'))"` or an equivalent quick schema-validation script | ❌ Wave 0 — could optionally be formalized as a `tests/smoke/test_bedrock_schema.py` if the planner wants an automated artifact, but HANDOFF frames this as a throwaway/manual check |

### Sampling Rate
- **Per task commit:** Manual verification (curl the endpoint; invoke the Lambda and eyeball the JSON) — no automated quick-run exists yet for this greenfield phase.
- **Per wave merge:** Same as above; there is only one wave's worth of infra work in this phase.
- **Phase gate:** Both success criteria 1 and 2 (plus the D-05–D-09 smoke test) must be manually confirmed working before `/gsd-verify-work`; `pytest` scaffold (Wave 0 below) can be created now even though nothing exercises it yet, to avoid Phase 3 starting from zero.

### Wave 0 Gaps

- [ ] `tests/__init__.py`, `tests/unit/__init__.py` — empty package scaffold per HANDOFF §11 layout, so Phase 3 has somewhere to add real unit tests without restructuring
- [ ] `requirements-dev.txt` or equivalent — pin `pytest` (and later `moto`, `hypothesis`) once package versions are locked for this project (defer actual pins to when Phase 3 needs them; Phase 1 does not need pytest running yet)
- [ ] Framework install: not needed this phase — `pytest` has no code to test yet since `src/` modules don't exist until Phase 3

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Phase 1 has no user-facing auth surface (HANDOFF explicitly defers Cognito/accounts) |
| V3 Session Management | No | No sessions in this phase |
| V4 Access Control | Yes (IAM-level, not application-level) | Least-privilege IAM role for the smoke-test Lambda: scope `s3:GetObject` to the specific test-photo bucket/prefix, scope `bedrock:InvokeModel` (avoid wildcard `bedrock:*` if practical) — SAM's auto-generated execution roles from `sam init`'s Hello World template are a reasonable default for the "hello world" Lambda but should be reviewed, not blindly widened, for the Bedrock smoke-test Lambda |
| V5 Input Validation | Yes (downstream concern, not Phase 1) | Bedrock's returned JSON must never be trusted raw — HANDOFF §7 mandates code-side validation (UTR regex, amount positivity) even though that validation logic is Phase 3's job, not Phase 1's smoke test's |
| V6 Cryptography | Yes (baseline) | S3 server-side encryption (SSE) should be enabled on any bucket created in this phase per HANDOFF §6's data rule, even for a throwaway smoke-test bucket, since it will hold a real photo of Aaryan's own payment screen |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Overly broad Lambda execution-role IAM policy (e.g. `s3:*`, `bedrock:*` on `Resource: "*"`) granted "to make the smoke test work faster" | Elevation of Privilege | Scope IAM policies to the specific bucket ARN and, where practical, the specific inference-profile ARN; SAM's `Policies:` template shortcuts (e.g. `S3ReadPolicy`) make this easy to do correctly from the start |
| Test photo (Aaryan's own real UPI payment) left in a public or unencrypted S3 bucket | Information Disclosure | Block public access + SSE on any bucket created this phase, matching HANDOFF §6's rule even though it's framed there for later phases — the smoke test is exercising real personal payment data now, not synthetic data |
| Long-lived, over-scoped local AWS credentials configured on the dev machine for convenience | Information Disclosure / Elevation of Privilege | Use a scoped IAM user (not root) for day-to-day `sam deploy` work once initial bootstrap is done; acceptable to bootstrap with the account's initial admin credentials for Day 1 given the hackathon's compressed timeline, but note this as a documented shortcut in `docs/DECISIONS.md`, not a silent default |

## Sources

### Primary (HIGH confidence)
- None this session — no verified tool-confirmed-and-authoritative-source claims meeting the strict `[VERIFIED]` bar beyond the two `pip index versions` registry checks (Package Legitimacy Audit / Standard Stack sections), which are HIGH-confidence for version numbers specifically.

### Secondary (MEDIUM confidence, official documentation fetched directly this session)
- docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html — SAM hello-world tutorial, full command sequence
- docs.aws.amazon.com/bedrock/latest/userguide/model-access.html — Bedrock model access process, Oct 2025 auto-enablement change, IAM permissions
- docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html — cross-region inference profile mechanics, Geo vs. Global routing
- docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html — Nova Lite regional-availability table, sample code
- docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html — Converse API request/response shape, official Python image example, IAM permission requirement
- aws.amazon.com/blogs/machine-learning/access-anthropic-claude-models-in-india-on-amazon-bedrock-with-global-cross-region-inference/ — Claude-in-India Global inference profile IDs and data-residency implication

### Tertiary (LOW confidence, WebSearch-synthesized, not directly fetched/quoted from a primary source)
- AWS Lambda Python runtime version currency (3.13 as current LTS) — synthesized from multiple WebSearch results, not a single authoritative page fetch
- AWS Builder Center student verification / re-verification mechanics — synthesized from WebSearch results describing general Builder ID email-change behavior, not the hackathon-specific flow
- $100 AWS credit eligibility under a new account email — no authoritative source found; the event page itself (fetched directly) does not address this question
- sam deploy IAM permission specifics beyond `CAPABILITY_IAM` — synthesized from a GitHub issue and general SAM docs references, not a single official page

## Metadata

**Confidence breakdown:**
- Standard stack (SAM CLI, boto3, Python runtime): HIGH for package versions (registry-verified), MEDIUM for Python runtime recommendation (WebSearch-synthesized, not a single fetched source)
- Architecture / Bedrock invocation pattern: MEDIUM-HIGH — the Converse API image pattern and IAM permission requirement come directly from official AWS documentation fetched and quoted this session
- Bedrock regional availability (ap-south-1 inference-profile requirement): MEDIUM — confirmed against official Nova Lite model-card page and an official AWS blog post about Claude-in-India, but the exact APAC geo-profile ID string for Nova was not directly observed and is flagged as an open question
- Hackathon logistics (Builder Center, $100 credit, exact deadline): LOW — genuinely unresolved by research; correctly flagged as open questions/assumptions rather than answered
- Pitfalls: MEDIUM-HIGH — derived directly from the regional-availability and IAM-permission findings above, not speculative

**Research date:** 2026-09-18
**Valid until:** ~7 days for the Bedrock access-policy and regional-availability specifics (this is a fast-moving area — AWS added the auto-enablement change only ~11 months before this research and continues to add regions/models to inference profiles); ~30 days for the SAM CLI mechanics (stable, mature tool).
