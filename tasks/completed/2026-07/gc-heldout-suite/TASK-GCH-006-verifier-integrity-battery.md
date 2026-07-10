---
id: TASK-GCH-006
title: "tests/test_gc_verifier_integrity.py — three-sided proof + broken/good fixtures + floors"
status: completed
task_type: testing
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 5
implementation_mode: task-work
complexity: 6
priority: high
dependencies: [TASK-GCH-004, TASK-GCH-005]
created: 2026-07-10T13:56:30Z
consumer_context:
  - task: TASK-GCH-004
    consumes: ANSWER_SHEET_FORMAT
    framework: "pytest run_gate subprocess convention (qav integrity precedent)"
    driver: "python3 -m pytest"
    format_note: "fixtures ARE answer sheets; each broken fixture's meta.json expect_fail must be a subset of the actually-failing gate tests"
---

# TASK-GCH-006 — Verifier integrity (the qav-file pattern, applied to gc-held-*)

## Scope

**NEW** `tests/test_gc_verifier_integrity.py` — additive sibling of the frozen integrity
files (all stay byte-identical; frozen discovery globs are blind to `gc-held-*` by
construction). Owns:

- **Three-sided proof** (frozen rules (a)/(b)/(c) verbatim):
  (a) Oracle passes both tasks' full gate battery (25/25 rows PASS by execution);
  (b) every broken fixture fails its owning test(s);
  (c) every good fixture passes the whole battery.
- **Instruments:** manifest/pin checks (counts == 25; ids unique per task AND across the
  suite — the row-id collision scenario); pin-drift demo (corrupted tmp copy ⇒
  `verify_pins` names the row); exclusion-provenance keys present; baseline file schema
  (only the `integrity-fixture/NONE` instrument family at build time, `instrument: true`).
- **Fixture floors** (grow, never shrink), pinned in-file.

**NEW** fixtures:
- `tests/broken_fixtures/gc-held-001-humaneval/`:
  `regressed-beyond-margin` (integrity-fixture family, 3+ sabotaged rows ⇒
  `test_regression_floor`), `missing-candidate-record` (⇒ `test_answer_sheet_contract`),
  `unknown-baseline-family` (⇒ `test_regression_floor`, message names the missing family),
  `foreign-row-injected` (⇒ `test_answer_sheet_contract`).
- `tests/broken_fixtures/gc-held-002-mbpp/`:
  `regressed-beyond-margin`, `truncated-rows-regress` (finish_reason=length diagnostics
  driving the count below floor ⇒ `test_regression_floor`).
- `tests/good_fixtures/gc-held-001-humaneval/`: `within-margin` (exactly 2 sabotaged rows —
  the margin boundary held), `extraction-fail-row-within-margin` (a missing program is a
  row FAIL, not a run crash).
- `tests/good_fixtures/gc-held-002-mbpp/`: `within-margin`.

Fixture sheets are generated from the Oracle programs (sabotage = wrong return value /
removed program + diagnostic), committed as files, with `meta.json` naming `expect_fail`.

## Acceptance Criteria

- [ ] Oracle leg green for both tasks; every broken fixture's `expect_fail` ⊆ actual
      failures; every good fixture passes
- [ ] Row-id uniqueness enforced ACROSS the suite, not just per task
- [ ] Frozen integrity files byte-identical; pre-existing 229 nodes re-run with identical
      verdicts (comm diff: 0 lost, N added, 0 failures)
- [ ] Fixture floors pinned; battery wall-clock increase ≤ ~90 s over baseline
- [ ] All modified files pass project-configured lint/format checks with zero errors
