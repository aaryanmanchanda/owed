# Decisions Log

Running log, newest first. Every entry carries a date, the decision, the
rationale, and a source reference (PROJECT.md Working Rule 6).

### 2026-09-18 — Bedrock smoke-test inference profile pinned: `apac.amazon.nova-lite-v1:0`

**Decision:** The Day-1 Bedrock smoke test (plan 01-02) uses the inference
profile ID **`apac.amazon.nova-lite-v1:0`**
(ARN: `arn:aws:bedrock:ap-south-1:038947448788:inference-profile/apac.amazon.nova-lite-v1:0`).

**How it was found:** `aws bedrock list-inference-profiles --region ap-south-1`
returned 30 profiles; `apac.amazon.nova-lite-v1:0` was `ACTIVE`. Cross-referenced
against `aws bedrock list-foundation-models --region ap-south-1`, which confirms
`amazon.nova-lite-v1:0` declares `IMAGE` in `inputModalities` (also `TEXT`,
`VIDEO`) — an image-capable candidate.

**Destination regions** (parsed from the profile's `models[].modelArn`, i.e.
every region this specific request may actually be processed in):
`ap-northeast-1`, `ap-northeast-2`, `ap-northeast-3`, `ap-south-1`,
`ap-southeast-1`, `ap-southeast-2` — all six are inside the Asia-Pacific
geography; none are outside India's broader region grouping used by this
profile's APAC scope (no `us-*`/`eu-*` destination).

**Rationale (D-08 selection order):** Rule 1 of the Task 1 selection order
prefers an ACTIVE profile whose ID begins with `apac.` over `global.`, because
APAC-scoped routing keeps processing inside Asia-Pacific rather than any
commercial region worldwide — a materially smaller data-residency disclosure
(HANDOFF §8). `apac.amazon.nova-lite-v1:0` satisfied this on the very first
candidate: it was ACTIVE, `apac.`-scoped, and image-capable, so rules 2 and 3
of the ordering (Nova-tier preference, Anthropic fallback) were never reached.
No Anthropic use-case form was needed — Nova unblocked immediately with no
Marketplace subscription step, exactly as RESEARCH.md's Standard Stack section
predicted for D-08.

**Outcome:** This choice is the smoke test's only (D-08) — Phase 2's real
~30-photo evaluation compares Nova Lite against the stronger Anthropic
candidate independently and may pick differently. Source: D-08; RESEARCH.md
"Bedrock Model Access on a Fresh Account", "Bedrock Model Availability in
ap-south-1"; RESEARCH.md Open Question 1 (now closed).

### 2026-09-18 — Day-1 AWS access uses the new account's ROOT user, not a dedicated IAM user

**Decision:** Task 1 of plan 01-01 originally instructed creating a dedicated
IAM user and access key for CLI/SAM work. In execution, Aaryan ran
`aws configure` with the new free-tier account's **root user** access keys
instead (confirmed via `aws sts get-caller-identity` returning
`arn:aws:iam::038947448788:root`).

**Rationale:** AWS explicitly advises against using root access keys for
day-to-day API/CLI work — root has unrestrictable full account privileges and
its keys cannot be scoped down. Aaryan was informed of this guidance and
explicitly chose to keep root for now anyway, as a deliberate Day-1
time-pressure shortcut under D-01's "day 2 of 3.5, move with urgency"
constraint, rather than spend time provisioning IAM Identity Center or a
scoped IAM user before any deploy could happen.

**Outcome:** Accepted as a known, documented shortcut, not a silent default.
Does not block plan 01-01 Task 2 or Task 3. Revisit before the account holds
anything more sensitive than a hello-world tracer and a throwaway Bedrock
smoke test — swapping to a scoped IAM user is a local `aws configure` change,
not an architecture change, and can happen anytime the timeline allows.
Source: this session's Task 1 human checkpoint; RESEARCH.md Security Domain
note (see entry below) already flagged root/admin-credential shortcuts as an
acceptable, explicitly-logged Day-1 pattern.

### 2026-09-18 — AWS account swap: original suspended, new free-tier account under a different email

**Decision:** All AWS work in this project runs against a brand-new AWS
free-tier account provisioned under a different email on 2026-09-18, not
Aaryan's original account.

**Rationale:** The original account was suspended for an unpaid post-trial
balance — a hard blocker, not merely a missing hackathon credit. Nothing
could be deployed there, including free-tier-eligible resources.

**Outcome:** Unblocked; Phase 1's AWS-dependent success criteria can proceed.
Two follow-on items remain explicitly OPEN, not resolved: (1) whether AWS
Builder Center student verification needs to be redone under the new email,
and (2) whether the new account is eligible for the hackathon's $100 AWS
credit, or whether Phase 2's evaluation costs must come out of free-tier/
personal spend instead. Source: D-02, D-03; 01-CONTEXT.md.

### 2026-09-18 — Day-1 Bedrock smoke test added to Phase 1

**Decision:** Add a Bedrock smoke test to Phase 1, ahead of Phase 2's real
extraction evaluation.

**Rationale:** Retires HANDOFF §13 risk #2 (IAM + passing S3 image bytes into
Bedrock is the steepest learning-curve risk) a day early, cheaply, without
building Phase 2's full evaluation harness.

**Outcome:** Scheduled as plan 01-02. Source: D-05; HANDOFF §13 risk 2.

### 2026-09-18 — Smoke test calls Bedrock from a Lambda that reads S3 bytes itself

**Decision:** The Bedrock smoke test's Lambda calls `s3.get_object()` for the
image bytes and then calls `bedrock.converse()` directly from inside the
Lambda. Step Functions' native direct-Bedrock-image integration is never used
anywhere in this project.

**Rationale:** HANDOFF §9 explicitly bans the Step Functions direct-Bedrock
image path as the project's single steepest learning-curve risk; mediating
through a Lambda is the locked, tested pattern.

**Outcome:** Locked pattern for plan 01-02 and for Phase 3's real `extract/`
module. Source: D-06; HANDOFF §9.

### 2026-09-18 — Smoke test pass bar is schema-valid response only

**Decision:** The Day-1 Bedrock smoke test passes when the Lambda returns a
response matching the §7 extraction JSON shape without erroring. Accuracy
(UTR exact-match, amount correctness, confident-wrong rate) is explicitly NOT
graded here.

**Rationale:** Conflating this smoke test with Phase 2's real ~30-photo,
two-model evaluation would waste Day-1 time on a comparison that belongs to
Phase 2 and risks under-scoping the throwaway Lambda into something it isn't.

**Outcome:** Phase 2 owns all accuracy numbers; this phase owns only "did it
return the shape." Source: D-07.

### 2026-09-18 — Smoke-test model = whichever Bedrock candidate grants access first in ap-south-1

**Decision:** No time is spent Day 1 comparing the two Bedrock candidate
models (one cheaper, one stronger). Whichever grants inference access first
in ap-south-1 is used for the smoke test.

**Rationale:** The real model comparison is Phase 2's job, with the full test
set. Day 1 only needs to prove the plumbing works, not pick a winner.

**Outcome:** Model choice deferred to plan 01-02 execution; comparison
deferred to Phase 2. Source: D-08.

### 2026-09-18 — Real payment data stays out of git; fixtures stay synthetic-shaped

**Decision:** Real UPI payment photos and Aaryan's raw transaction export are
kept entirely out of git under the ignored `testdata/` directory.
`tests/fixtures/` holds only value-scrubbed, shape-faithful hand-written data,
never a raw bank export and never a payment-screen image.

**Rationale:** No real customer or personal banking data may ever land in a
public repo, fixtures, or the video (HANDOFF §6; PROJECT.md Constraints). The
distinction between `testdata/` (ignored, real) and `tests/fixtures/`
(tracked, synthetic) needs to be explicit from Day 1 so nothing downstream
accidentally blurs the two.

**Outcome:** `.gitignore`'s `testdata/*` + `!testdata/README.md` rule was
written and staged before any other file in plan 01-01 Task 2, and verified
with `git check-ignore` before any photo was ever at risk of being added.
Source: HANDOFF §6, §11.

### 2026-09-18 — Lambda functions default to arm64 Graviton at 256 MB

**Decision:** `template.yaml`'s `Globals.Function` block sets
`Architectures: [arm64]` and `MemorySize: 256` for every Lambda in this
project unless a specific function later needs otherwise.

**Rationale:** arm64 Graviton is the cheaper price-per-invocation option with
no native-dependency requirement anywhere in this project (pure Python), so
there's no reason not to take the cost win from Day 1.

**Outcome:** Recorded as a deliberate cost lever for README section 7. Source:
this session; README section 7 cost-decisions structure.

### 2026-09-18 — Day-1 deploys use the new account's initial credentials on the dev machine

**Decision:** The first `sam deploy` and all Day-1 AWS CLI work run using the
new account's initial credentials directly on Aaryan's development machine,
rather than provisioning a separately-scoped deploy role or CI identity
first.

**Rationale:** RESEARCH.md's Security Domain note explicitly accepts this as
a reasonable Day-1 shortcut given the hackathon's compressed timeline,
provided it's logged rather than silently assumed. (See the ROOT-user entry
above for the more specific deviation that emerged in execution: this
shortcut turned out to mean root credentials specifically, not merely an
unscoped-but-distinct IAM user.)

**Outcome:** Accepted, logged, not silently defaulted. Source: RESEARCH.md
Security Domain note ("acceptable to bootstrap with the account's initial
admin credentials for Day 1... but note this as a documented shortcut").

### 2026-09-18 — Repo stays public with honest post-kickoff history

**Decision:** The repo is kept public throughout the build (not made private
until near submission), with commit history that only ever postdates the
2026-09-17 kickoff.

**Rationale:** HANDOFF §1 makes commit-history integrity a disqualifying
condition if violated; public-from-commit-1 was left to planner discretion in
01-CONTEXT.md's Deferred Ideas, and public-by-default is the simpler,
lower-friction choice for a solo submission that will need to be public by
the deadline anyway.

**Outcome:** Locked for the remainder of the project. Source: HANDOFF §1;
01-CONTEXT.md Deferred Ideas (repo-visibility discretion).
