---
phase: 01-foundation-kickoff
plan: 01
subsystem: infra
tags: [aws, sam, api-gateway, lambda, cloudformation, python3.13, arm64]

# Dependency graph
requires: []
provides:
  - Deployed CloudFormation stack `owed-foundation` in ap-south-1 (HttpApi + HelloWorldFunction), proving the API Gateway -> Lambda hop
  - HANDOFF §11 repo skeleton on disk (src/{api,parse_record,extract,reconcile,common}, statemachine/, web/, tests/{unit,concurrency,fixtures})
  - docs/DECISIONS.md running decision log, seeded with 10 dated entries
  - .gitignore covering testdata/* (with a testdata/README.md negation), build artifacts, and secret-bearing file patterns
  - requirements-dev.txt pinning pytest for Phase 3
affects: [01-02-bedrock-smoke-test, 01-03-test-data-outreach, phase-3-reconcile-engine]

# Actuals (#2632)
actuals:
  tokens: 5022
  tasks: 3
  commits: 2

# Tech tracking
tech-stack:
  added: [aws-sam-cli 1.166.2, boto3 (Lambda-managed runtime, unpinned), python3.13, pytest>=8,<9]
  patterns:
    - "SAM HttpApi with no StageName -> $default stage -> invoke URL carries no stage prefix"
    - "arm64 Graviton + 256MB MemorySize as Globals.Function default cost lever"
    - "No explicit IAM policy on a Lambda with no AWS calls -> SAM's CloudWatch-Logs-only default role is least-privilege"

key-files:
  created:
    - template.yaml
    - samconfig.toml
    - src/api/hello/app.py
    - .gitignore
    - docs/DECISIONS.md
    - docs/AI_TOOLS.md
    - docs/extraction-eval.md
    - README.md
    - testdata/README.md
    - tests/fixtures/README.md
    - requirements-dev.txt
  modified: []

key-decisions:
  - "Root account access keys used for Day-1 AWS auth instead of a dedicated IAM user - deliberate, informed, logged shortcut under D-01 urgency (see docs/DECISIONS.md)"
  - "arm64 Graviton + 256MB as the Globals.Function default, a Day-1 cost lever"
  - "Repo kept public from commit 1, per planner discretion left open in 01-CONTEXT.md"
  - "Day-1 repo skeleton materializes the full HANDOFF §11 tree now rather than growing it later, per planner discretion"

patterns-established:
  - "Pattern: .gitignore's testdata/* + !testdata/README.md negation must be staged and verified with git check-ignore BEFORE any real photo/export is added, in every future task touching testdata/"
  - "Pattern: docs/DECISIONS.md entries are dated, cite the CONTEXT.md decision ID, and record OPEN follow-on risks explicitly rather than treating a resolution as fully closed"

requirements-completed: [SC-1, SC-5, D-01, D-02, D-03]

coverage:
  - id: D1
    description: "Deployed ap-south-1 HTTP API endpoint (owed-foundation stack) returns HTTP 200 with message + region JSON body"
    requirement: "SC-1"
    verification:
      - kind: integration
        ref: "curl https://tbc6un22c9.execute-api.ap-south-1.amazonaws.com/hello -> 200 {\"message\":\"hello from owed\",\"region\":\"ap-south-1\"}"
        status: pass
    human_judgment: false
  - id: D2
    description: "testdata/photos/ (real UPI payment photos) provably outside git via .gitignore, before any file was ever staged"
    verification:
      - kind: other
        ref: "git check-ignore -q testdata/photos && git ls-files testdata (exactly testdata/README.md)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Repo tree matches HANDOFF §11 layout; docs/DECISIONS.md has 10 dated entries citing D-02, D-03, D-05, D-06, D-07, D-08; every commit postdates 2026-09-17 kickoff"
    requirement: "SC-5"
    verification:
      - kind: other
        ref: "SKELETON_OK / DECISIONS_OK / INTEGRITY_OK automated checks (see Task 3 verify block, 01-01-PLAN.md)"
        status: pass
    human_judgment: false
  - id: D4
    description: "AWS account swap (D-02/D-03) and its follow-on open risks (Builder Center re-verification, $100 credit eligibility) logged and left explicitly OPEN, not silently assumed resolved"
    verification: []
    human_judgment: true
    rationale: "Whether Builder Center verification or the $100 credit actually carries over under the new account email cannot be confirmed programmatically - it requires Aaryan to check the AWS Builder Center console and submit the credit form himself. Logged as open in docs/DECISIONS.md and STATE.md."

duration: 38min
completed: 2026-09-18
status: complete
---

# Phase 1 Plan 1: SAM Hello-World Tracer + HANDOFF §11 Repo Skeleton Summary

**Deployed `owed-foundation` HttpApi→Lambda tracer to ap-south-1 (verified HTTP 200 with region-echo body) and materialized the full HANDOFF §11 repo skeleton with a 10-entry docs/DECISIONS.md log.**

## Performance

- **Duration:** 38 min (Task 1 human checkpoint completed in a prior session; this continuation covers Task 2 and Task 3)
- **Started:** 2026-09-18T02:10:29+05:30 (prior plan commit, baseline)
- **Completed:** 2026-09-18T02:48:20+05:30
- **Tasks:** 3/3 (Task 1 verified via human checkpoint in prior session; Task 2 and Task 3 executed this session)
- **Files modified:** 22 (5 in Task 2, 17 in Task 3)

## Accomplishments
- Deployed CloudFormation stack `owed-foundation` in ap-south-1: `AWS::Serverless::HttpApi` ($default stage, no prefix) → `owed-hello` Lambda (python3.13, arm64, 256MB), returning HTTP 200 with `{"message": "hello from owed", "region": "ap-south-1"}` — proves the region landed correctly, not just that some Lambda answered.
- `.gitignore` written and staged before any other file in Task 2, verified with `git check-ignore` before and after; `testdata/photos/` (3 real UPI payment photos from Task 1) is provably outside git history.
- Full HANDOFF §11 repo tree materialized: `src/{api,parse_record,extract,reconcile,common}/`, `statemachine/`, `web/`, `tests/{unit,concurrency,fixtures}/`, `docs/{DECISIONS,AI_TOOLS,extraction-eval}.md`, `README.md` with all eleven HANDOFF §12 section headings, `requirements-dev.txt` pinning `pytest>=8,<9` only.
- `docs/DECISIONS.md` seeded with 10 dated entries covering the AWS account swap (D-02/D-03, with open follow-on risks explicitly flagged, not assumed closed), the Bedrock smoke-test decisions (D-05 through D-08), the testdata/tests-fixtures data-handling split, the arm64 cost lever, the Day-1 credentials shortcut, repo visibility, and — as a logged deviation — the ROOT-account access-key choice actually made in Task 1.

## Task Commits

Each task was committed atomically:

1. **Task 1: AWS toolchain, new-account credentials, and seed photos** - checkpoint completed by human in a prior session (no repo commit by design — this task writes only `~/.aws/credentials`/`~/.aws/config` and `testdata/photos/`, all outside git)
2. **Task 2: End-to-end "deployed endpoint answers 200"** - `352d238` (feat)
3. **Task 3: HANDOFF §11 skeleton and the running decision log** - `bfb8538` (docs)

**Plan metadata:** commit pending (this SUMMARY + STATE.md/ROADMAP.md update)

## Files Created/Modified
- `template.yaml` - SAM template: `OwedHttpApi` ($default stage HttpApi) + `HelloWorldFunction` (owed-hello, python3.13, arm64, 256MB, 10s timeout)
- `samconfig.toml` - Pins non-interactive deploy: stack `owed-foundation`, region `ap-south-1`, `CAPABILITY_IAM`
- `src/api/hello/app.py` - `lambda_handler` returning 200 JSON with `message` and `AWS_REGION`
- `src/api/hello/requirements.txt` - Intentionally empty (boto3 ships in the managed runtime)
- `.gitignore` - `.aws-sam/`, caches, env/key files, `testdata/*` + `!testdata/README.md` negation
- `src/{api,parse_record,extract,reconcile,common}/__init__.py` - HANDOFF §11 package markers, each naming its owning phase
- `statemachine/.gitkeep`, `web/.gitkeep` - Placeholders for Phase 3/4
- `tests/{__init__.py,unit/__init__.py,concurrency/__init__.py}` - 01-VALIDATION.md Wave 0 test scaffold
- `tests/fixtures/README.md` - States the synthetic-only rule for that directory
- `testdata/README.md` - Only tracked file under the ignored `testdata/` tree
- `requirements-dev.txt` - `pytest>=8,<9`
- `README.md` - Design-doc stub, all eleven HANDOFF §12 headings in order
- `docs/DECISIONS.md` - 10 dated seed entries citing D-02, D-03, D-05, D-06, D-07, D-08, plus the logged ROOT-credentials deviation
- `docs/AI_TOOLS.md` - Dated AI-tools disclosure, seeded with this session's tool
- `docs/extraction-eval.md` - Headings-only stub, explicitly "no numbers measured yet"

## Decisions Made
- Root account access keys used for Day-1 AWS auth rather than a dedicated IAM user (see Deviations below and `docs/DECISIONS.md`).
- arm64 Graviton + 256MB set as the `Globals.Function` default across the whole project, a deliberate Day-1 cost lever (README §7 will cite this).
- Full HANDOFF §11 skeleton materialized now rather than grown incrementally, and the repo kept public from commit 1 — both were left to planner discretion in 01-CONTEXT.md's Deferred Ideas and are now resolved and logged in `docs/DECISIONS.md`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical documentation] Logged the ROOT-account-credentials deviation explicitly in docs/DECISIONS.md**
- **Found during:** Resuming after Task 1's human checkpoint
- **Issue:** Plan Task 1's instructions pointed at IAM → Users → Create access key (a dedicated IAM user). The user instead ran `aws configure` with the new account's ROOT user access keys (confirmed via `aws sts get-caller-identity` returning `arn:aws:iam::038947448788:root`). AWS explicitly advises against root API keys; leaving this undocumented would silently normalize a known-risky shortcut.
- **Fix:** Added a dedicated, dated `docs/DECISIONS.md` entry documenting the root-key usage, the AWS guidance against it, that the user was informed and explicitly chose to proceed anyway under D-01 time pressure, and that it should be revisited (a local `aws configure` swap, not an architecture change) once the timeline allows.
- **Files modified:** `docs/DECISIONS.md`
- **Verification:** Entry present and citation-complete; does not block Task 2 or Task 3's acceptance criteria (both explicitly scoped to the deployed endpoint and the repo skeleton, neither of which depends on the credential type used).
- **Committed in:** `bfb8538` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical documentation, Rule 2)
**Impact on plan:** No scope creep — this is a documentation-only addition required by PROJECT.md Working Rule 6 ("add an entry to docs/DECISIONS.md whenever a decision is made or changed") applied to a decision that emerged mid-execution rather than being pre-planned. The underlying AWS access pattern itself was not changed by this executor; that call belongs to the user and was made with full information.

## Issues Encountered
None - both automated tasks (Task 2, Task 3) executed cleanly on the first attempt: `sam build`/`sam deploy` succeeded without retries, and all three Task 3 verification scripts (`SKELETON_OK`, `DECISIONS_OK`, `INTEGRITY_OK`) passed on the first run.

## User Setup Required
None for this continuation - Task 1's `user_setup` (AWS credentials, SAM/AWS CLI install, seed photos) was already completed and verified by the human before this session began.

## Next Phase Readiness
- Plans 01-02 (Bedrock smoke test) and 01-03 (test data / owner outreach) are both unblocked: the AWS account authenticates, the region is confirmed, and `testdata/photos/` (3 seed photos) exists and is git-ignored.
- ROADMAP Phase 1 success criteria 1 and 5 are both demonstrably met (see `coverage` D1 and D3 above).
- Open, not-yet-resolved items carried forward unchanged: Builder Center re-verification and $100-credit eligibility under the new account email (D-02/D-03 follow-ons), Q1-Q5 owner outreach, exact Sunday submission deadline time — none of these block wave 2.
- The ROOT-credentials shortcut (this plan's one logged deviation) should be revisited before the AWS account holds anything more sensitive than this tracer and plan 01-02's throwaway Bedrock smoke test; swapping to a scoped IAM user is a local `aws configure` change whenever the timeline allows it.

---
*Phase: 01-foundation-kickoff*
*Completed: 2026-09-18*

## Self-Check: PASSED

All 21 files created by Task 2/Task 3 verified present on disk. Both task commits (`352d238`, `bfb8538`) verified present in `git log --oneline --all`.
