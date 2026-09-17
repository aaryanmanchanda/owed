# testdata

This directory is git-ignored (see root `.gitignore`, `testdata/*` with a
`!testdata/README.md` negation) because everything else in it is Aaryan's real
personal banking data. Nothing under here is ever committed except this file.

What belongs here:
- `photos/` — Aaryan's own UPI payment-success screen photos, photographed off
  a phone screen (never a customer's payment screen — HANDOFF §6, PROJECT.md
  Constraints).
- Aaryan's raw transaction export (whatever format Q1 turns out to be — bank
  statement CSV/PDF, business app export, etc.), used to build the Phase 3
  parser fixture and to grade the Phase 2 extraction evaluation.
- Scratch invoke payloads used for manual Lambda testing during development.

None of this is synthetic. `tests/fixtures/` (tracked in git) is where
hand-written, value-scrubbed, shape-faithful data lives instead.
