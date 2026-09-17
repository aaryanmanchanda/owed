# tests/fixtures

This directory holds only **synthetic credits and hand-written extraction JSON**
(HANDOFF §11). It never holds a raw bank export and never holds a payment-screen
image, real or fabricated.

Real UPI payment photos and Aaryan's raw transaction export live in the
git-ignored `testdata/` directory at the repo root instead (see
`testdata/README.md`). Fixtures here are values a developer typed by hand to
exercise the parser and verdict engine deterministically — they must be
shape-faithful to the real data without carrying any of Aaryan's actual
personal banking details.
