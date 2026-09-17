---
phase: "01"
slug: "foundation-kickoff"
created: "2026-09-18"
policy: "Full API coverage by default — opt out, never opt in"
---

# Phase 01 — External API Coverage Decisions

Phase 1 integrates exactly one external API with a real capability surface worth enumerating:
**Amazon Bedrock Runtime**, via the throwaway smoke-test Lambda (D-05–D-09, plan 01-02). Every
other AWS service this phase touches (CloudFormation, API Gateway, Lambda, S3, IAM) is
infrastructure provisioning through SAM rather than an API whose capability surface this project
chooses among — those are declared at the bottom rather than matrixed.

The default position for each capability below is FULL COVERAGE. Every `OPT-OUT` carries a
one-line reason.

## Amazon Bedrock — control plane (`bedrock`)

| Capability | Decision | Reason |
|---|---|---|
| `ListInferenceProfiles` | **COVER** — plan 01-02 Task 1 | The only way to resolve the exact ap-south-1 profile ID string, which RESEARCH open question 1 left unobserved. |
| `GetInferenceProfile` | **COVER** — plan 01-02 Task 3 | Supplies the destination-region set that HANDOFF §8's data-residency disclosure requires as measured fact. |
| `ListFoundationModels` | **COVER** — plan 01-02 Task 1 | Identifies which models declare `IMAGE` in `inputModalities`; without it, profile selection is guesswork. |
| `GetFoundationModelAvailability` | **COVER, best-effort** — plan 01-02 Task 1 | Documented purpose-built access check, but the task states a fallback because the installed CLI version may not expose the verb; a successful `Converse` is the authoritative confirmation either way (RESEARCH Pitfall 2). |
| `PutUseCaseForModelAccess` | **COVER, conditional** — plan 01-02 Task 1 | Needed only if selection falls back to an Anthropic model; a brand-new account has never submitted the one-time form (RESEARCH open question 2). |
| `CreateInferenceProfile` / `DeleteInferenceProfile` | OPT-OUT | Application-inference profiles exist for cost allocation by tag; this project has one workload and no cost-attribution requirement. |
| `CreateModelInvocationJob` (batch inference) | OPT-OUT | Batch inference is asynchronous with hours-scale turnaround; HANDOFF §9 locks a Step Functions Map at concurrency 4 over a single shift, which is a synchronous per-photo workload. |
| `CreateGuardrail` / `ApplyGuardrail` | OPT-OUT | Guardrails filter harmful content and PII in conversational output. This model extracts seven fixed fields and never decides a verdict (PROJECT.md Key Decisions); code-side validation per HANDOFF §7 is the correct control, and a guardrail would add per-call cost for no safety gain here. |
| `CreateModelCustomizationJob` / fine-tuning | OPT-OUT | Fine-tuning a vision model is days of work and real spend on a 3.5-day solo hackathon; HANDOFF §8 explicitly frames the approach as prompt plus evaluation, not training. |
| Knowledge Bases / Agents / Flows | OPT-OUT | Retrieval and agentic orchestration solve problems this project does not have; the whole design point is that a deterministic engine owns every decision. |
| `GetModelInvocationLoggingConfiguration` / `PutModelInvocationLoggingConfiguration` | OPT-OUT for Phase 1 | Invocation logging would persist copies of real payment images to S3 or CloudWatch, increasing the data-handling surface for one smoke-test call. The destination-region fact it would have provided is obtained from `GetInferenceProfile` instead. Phase 2 may revisit if its evaluation needs per-call latency from logs. |

## Amazon Bedrock — runtime (`bedrock-runtime`)

| Capability | Decision | Reason |
|---|---|---|
| `Converse` | **COVER** — plan 01-02 Tasks 2 and 3 | The primary call. Chosen over `InvokeModel` specifically because D-08 leaves the model unfixed until runtime and `Converse` gives one request/response shape across vendors (RESEARCH "Alternatives Considered"). |
| `Converse` image content block (raw bytes) | **COVER** — plan 01-02 Task 2 | This is the exact D-06 risky path being retired: `s3.get_object` bytes handed straight to Bedrock, never pre-base64-encoded, never via Step Functions' direct integration. |
| `ConverseStream` | OPT-OUT | Streaming benefits interactive UIs. This is a batch job whose consumer is a Step Functions Map state that needs the complete JSON object before it can proceed. |
| `InvokeModel` / `InvokeModelWithResponseStream` | OPT-OUT | Requires per-model request/response body knowledge, which is precisely the coupling `Converse` removes while D-08 keeps the model choice open. |
| Tool use / function calling in `Converse` | OPT-OUT | Would let the model take actions. Directly contrary to PROJECT.md's locked decision that the model only extracts and never decides. |
| `system` prompt block | **COVER, at discretion** — plan 01-02 Task 2 | The schema instruction and the return-null-when-unsure rule may be placed in a system block or the user text block; either satisfies HANDOFF §7. Phase 2 tunes placement against measured results. |
| `inferenceConfig` (temperature, maxTokens, topP) | **COVER, deferred tuning** — Phase 2 | Phase 1's pass bar is schema validity only (D-07); tuning sampling parameters before there is a measurement to tune against would be guessing. Phase 2 owns it. |
| `additionalModelRequestFields` | OPT-OUT | Vendor-specific escape hatch; nothing in HANDOFF §7's seven-field extraction needs it. |
| `CountTokens` | OPT-OUT for Phase 1 | Useful for the README's cost-decisions section, but cost numbers must be measured on the real 30-photo set, which is Phase 2's job (PROJECT.md Working Rule 5 forbids unmeasured figures). |
| `guardrailConfig` on `Converse` | OPT-OUT | Follows the guardrail opt-out above. |

## Amazon Rekognition

`DetectText` is named in HANDOFF §8 as the OCR baseline for the extraction evaluation.
**OPT-OUT for Phase 1, COVER in Phase 2** — D-07 scopes this phase to a schema smoke test and
forbids conflating it with the evaluation; ROADMAP Phase 2 success criterion 1 explicitly carries
the Rekognition baseline.

## Services provisioned, not capability-matrixed

CloudFormation, API Gateway (HTTP API), Lambda, S3 and IAM are declared through SAM in
`template.yaml` rather than chosen among. Their Phase 1 surface is fixed by HANDOFF §9's locked
architecture and by the controls in each plan's threat model: `$default`-stage HTTP API with one
GET route, one hello function and one throwaway smoke-test function, one bucket with public access
blocked plus AES256 SSE plus a 7-day lifecycle, and two scoped IAM policy entries with no wildcard
resource. Step Functions and DynamoDB are Phase 3; Amplify is Phase 4.
