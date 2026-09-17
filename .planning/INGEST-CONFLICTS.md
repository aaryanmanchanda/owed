## Conflict Detection Report

### BLOCKERS (0)

None. Only one source document was ingested (HANDOFF.md, classified SPEC, high confidence). No UNKNOWN/low-confidence classifications, no cycles in the cross-ref graph (its cross_refs point to files not present in the classified-doc set: docs/AI_TOOLS.md, docs/DECISIONS.md, docs/extraction-eval.md, template.yaml, statemachine/recon.asl.json, README.md, and an external GitHub URL — none of these reference back to HANDOFF.md, so no cycle exists), and no locked-vs-locked contradiction is possible with a single source.

### WARNINGS (0)

None. With a single source document there are no competing PRD acceptance variants and no cross-document ambiguity to surface.

### INFO (0)

None. With a single source document there is no lower-precedence-vs-higher-precedence contradiction to auto-resolve.

---

GSD > No conflicts detected.

Note for downstream consumers (gsd-roadmapper): HANDOFF.md itself contains five explicitly UNANSWERED open questions (Q1-Q5, §2) and an incomplete status checklist (§14). These are not classification or precedence conflicts — they are open items within the single source — and are therefore not represented above. They are captured verbatim, unresolved, in `.planning/intel/context.md` ("Open questions for Brindhavan — UNANSWERED in source" and "Status checklist — UNANSWERED / incomplete in source") and cross-referenced in `.planning/intel/constraints.md` ("Parser constraint — contingent on unanswered Q1" and "Photo-timestamp constraint — contingent on unanswered Q2"). Roadmapper should not treat the parser format, photo channel, scale, demo mismatch example, or filming consent as resolved.
