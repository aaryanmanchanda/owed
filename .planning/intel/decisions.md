# Decisions

Extracted from HANDOFF.md, classified SPEC (high confidence, precedence 0) but functioning as an ADR-equivalent decision log for this project. The document-level `locked` field from the classifier is `false`, but the document's own text (intro: "don't relitigate a decision without a new reason"; §15 rule 8; §16 header "don't reopen without new evidence") marks the entries below as settled. Per ingest-run instruction, they are treated as locked decisions.

---

## Project idea selection
- source: HANDOFF.md §16 (Decision log so far)
- status: locked
- decision: Chosen idea: "Own-delivery restaurant rider reconciliation" (Hotel Brindhavan) — reason given: "Real user confirmed (Brindhavan); fits the batch differentiator; fits Aaryan's payments background; legible demo." Rejected/dead alternatives, not to be reopened without new evidence: Distributed LLM inference over WebRTC (dead — WebRTC overhead roughly halved throughput in own benchmark, still needs connectivity, SwarmLLM already ships flagship demo, weak AWS fit); mcp-studio (dead for this event — existing public project, rules forbid prior work); Agent action firewall + idempotent ledger / "tree-aware settlement" (dead — crowded space, abstract demo, weak Learning score, prior-work risk); College fest UPI reconciliation (dead — VIT registers events centrally, no real user); Small-merchant screenshot verification (dead — crowded space, merchants need pre-ship verification which isn't a batch job); Aggregator (Swiggy/Zomato) rider photos (not pursued — platform already owns that flow).
- scope: project idea / competition entry selection

## Verdict rules are deterministic; the model never decides
- source: HANDOFF.md §7, §15 rule 8
- status: locked
- decision: The model (Bedrock) only extracts fields from photos. Every verdict comes from deterministic rules, run in code, against the payment record — never the model. Ask Aaryan before changing the verdict rules in §7; they are "the core of the product and of the 'no false accusations' promise."
- scope: verdict engine / core product logic

## Architecture and stack (Ship It track)
- source: HANDOFF.md §9
- status: locked
- decision: Region ap-south-1 (Mumbai). Runtime: Python (current Lambda-supported version). Infrastructure as code: AWS SAM. Flow: Amplify Hosting (mobile-first, branch password protection) → API Gateway (HTTP API) → Lambda `api` → S3 (presigned uploads: photos, payment record) → Step Functions (Standard) execution per shift run, four states in order: ParseRecord (Lambda: parse payment record → CREDIT items) → ExtractPhotos (Map, MaxConcurrency 4, Lambda: Bedrock → PHOTO items) → Reconcile (Lambda: sorted, single writer → verdicts, CLAIM items, RIDER totals) → Finalize (Lambda: status = done). Storage: DynamoDB single table with TTL. Observability: CloudWatch structured JSON logs + one dashboard.
- scope: system architecture, AWS service selection

## Scope boundaries (explicitly out of scope)
- source: HANDOFF.md §6
- status: locked
- decision: Out of scope for this build: Cognito or user accounts (use Amplify branch password protection instead, documented why); any app for riders, or any change to how riders work; judging screenshots for forgery (ELA, layout checks); live or real-time verification, gateways, SMS reading; more than one payment-record format; multiple businesses or tenants (keep a `business_id` in keys anyway, but don't build multi-tenant support); analytics, charts, exports beyond one results screen; any tool that generates fake payment screenshots (not even for test data).
- scope: product scope boundaries

## Repo integrity / competition compliance rules
- source: HANDOFF.md §1, §15
- status: locked
- decision: All project work starts after kickoff (Thursday, Sept 17, 2026); a repo whose history doesn't match the event dates disqualifies the entry. Copy no code from anywhere, including Aaryan's own `mcp-studio` repo and every repo listed in §5 prior art; libraries/frameworks/starter templates are allowed if not written during the event, with credit and a compatible licence. The writeup must list the AI coding tools used; keep `docs/AI_TOOLS.md` up to date. Small commits with clear messages; no squashing history into one commit; never backdate commits. Add an entry to `docs/DECISIONS.md` whenever a decision is made or changed. Stay inside §6 scope — propose additions, don't build them unasked.
- scope: repo process, competition rules compliance

## Data handling and privacy rules
- source: HANDOFF.md §6, §15
- status: locked
- decision: No real customer payment screens in the repo, in fixtures, or in the video. Test photos come from Aaryan's own small transfers, photographed off a phone screen. No real customer data anywhere in the repo. No fake-screenshot generators, even for test data. All DynamoDB items carry a TTL (`expires_at`, default 7 days). S3 gets a lifecycle rule with the same horizon.
- scope: data privacy, compliance, test-data policy

## Framing rule — never use the word "fraud"
- source: HANDOFF.md §2
- status: locked
- decision: The tool protects riders too. A verified payment settles the question for everyone. Never use the word "fraud" in the UI. Anything flagged is shown as "check this."
- scope: UI/UX copy, product framing
