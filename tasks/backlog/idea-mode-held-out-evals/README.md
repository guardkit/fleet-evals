# FEAT-EVAL-IDEA — Idea-Mode Held-Out Eval Tasks

**Problem:** The Sovereign Planning Loop's go-live gate G2 requires deterministic eval
coverage of PO idea mode — the mode behind James's Slack intake — and idea mode has zero
real-world training examples and zero held-out coverage. The frozen po-heldout suite
(FROZEN 2026-07-03) gates extract/greenfield only. Invented requirements are the named
worst failure mode of the PO concept in front of James.

**Solution:** Two additive doc-shaped eval tasks (`po-held-005-idea`,
`po-held-006-scope`) under a separate suite tag (`po-heldout-idea`) with new deterministic
gates: invention-anchor licensing (a specific asserted in requirement-bearing text must
be surfaced as an assumption/open question), assumption discipline, and scope-mode
selection gates (subset with content pinning, closure vs the reference graph,
constraint-carried floor). The frozen suite, its thresholds, and its 12-rollout verdict
are untouched by construction; verifier-integrity discipline extends automatically.

**Provenance:** spec `features/idea-mode-held-out-evals/` (curated + fork-reconciled
2026-07-05) → decision review TASK-REV-09AB (3-agent analysis; 2 spec defects fixed,
hardenings folded in) → this 8-task structure.

## Subtasks

| ID | Wave | Cx | Title |
|---|---|---|---|
| TASK-EVI-001 | 1 | 3 | Addendum scope doc (DRAFT) + pinned instrument contracts |
| TASK-EVI-002 | 2 | 5 | harness/idea_gates.py + run_po_eval.py --suite + unit tests |
| TASK-EVI-003 | 3 | 6 | po-held-005-idea folder + seed battery |
| TASK-EVI-004 | 3 | 6 | po-held-006-scope folder + chained roadmap + seed battery |
| TASK-EVI-005 | 4 | 2 | Frontier sheets both tasks + ASSUM-009 calibration (ATTENDED) |
| TASK-EVI-006 | 5 | 5 | 005 full battery + anchor-instrument integrity |
| TASK-EVI-007 | 5 | 4 | 006 full battery + roadmap-pin integrity |
| TASK-EVI-008 | 6 | 3 | Validation, baselines, traceability, freeze hand-off |

Operator follow-up tasks: 1 (TASK-EVI-005 — attended, Fable-window-bound).

**Validation (build-plan Session 1, verbatim):** verifier integrity green including new
fixtures; a frontier-model answer sheet passes; a deliberately-stubbed answer sheet fails.
