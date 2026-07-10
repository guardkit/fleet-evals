# Feature: gc-heldout — General-Capability Regression Suite (FEAT-EVAL-GC / OBS-7)

Additive suite `gc-heldout` (tasks `gc-held-001-humaneval`, `gc-held-002-mbpp`): a fixed,
content-pinned 25+25 HumanEval/MBPP subset run against served GGUFs via llama-swap and graded
**by execution** in a stdlib-only subprocess sandbox (refuse-loud). Verdict is **relative
regression against a frozen same-family base baseline** (G-G1..G-G4, PROPOSED until Rich
freezes `docs/research/ideas/gc-heldout-suite-scope.md` by commit before the first grade).

- Spec of record: `features/gc-heldout-suite/` @ 63ec53f (32 scenarios, 13 assumptions,
  Rich-accepted 2026-07-10)
- Plan of record: `.claude/reviews/TASK-REV-B7E2-review-report.md`
- Build mode: hand-build in-session (house precedent), sequential waves, full
  verifier-integrity battery green after every wave
- NO GPU in the build session: the baseline graded run is delivered as a runbook
  (`docs/runbooks/gc-heldout-baseline-run.md`), executed by the operator once the GB10 frees

## Tasks

| Wave | Task | Title |
|---|---|---|
| 1 | TASK-GCH-001 | Sandbox module + sandbox integrity tests |
| 2 | TASK-GCH-002 | Pinned 25+25 benchmark subset, manifests, provenance |
| 3 | TASK-GCH-003 | gc_gates: extraction, grading, pins, G-G verdicts, family rule |
| 4 | TASK-GCH-004 | Task folders gc-held-001-humaneval / gc-held-002-mbpp |
| 4 | TASK-GCH-005 | Runner harness/run_gc_heldout.py |
| 5 | TASK-GCH-006 | Verifier-integrity battery + fixtures |
| 6 | TASK-GCH-007 | RESULTS template, scope doc (PROPOSED), baseline runbook |

## Constraints (binding)

- Frozen suites (po/arch/coach/qav) NEVER edited — additive only; frozen task globs stay
  blind to `gc-held-*` by construction.
- `link_assets.py` / `ASSETS.sha256` untouched (public data committed in-repo).
- Full-suite failing set == baseline (229 passed pre-change).
- G-G thresholds are PROPOSED here; **do not freeze in this feature** — Rich freezes by
  commit on the scope doc before the first grade (before the qav-ft-v1 grade, D-OBS-3).
