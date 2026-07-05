---
id: TASK-EVI-008
title: "End-to-end validation, baselines, traceability sweep, freeze hand-off"
status: completed
task_type: testing
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 6
implementation_mode: direct
complexity: 3
priority: high
dependencies: [TASK-EVI-001, TASK-EVI-002, TASK-EVI-003, TASK-EVI-004, TASK-EVI-005, TASK-EVI-006, TASK-EVI-007]
created: 2026-07-05T09:30:00Z
---

# TASK-EVI-008 — Validation + baselines + hand-off

## Scope (the SPL build-plan Session-1 validation criteria, made mechanical)

1. `python3 harness/link_assets.py` (frozen tasks' private assets — environment
   prerequisite; the NEW tasks must depend on zero private assets, assert it).
2. Full `pytest tests/ -q` — compare against the Wave-0 pre-extension baseline: the
   original 33 checks all present and green (superset proof; frozen tasks' gate results
   identical to pre-extension).
3. `run_po_eval.py --suite po-heldout-idea --dry-run` — 6/6 assemblies proven (frozen
   precedent: "dry-run assembly proven 12/12"); default-suite dry-run still 12/12 with
   identical prompt sha256s.
4. Named smoke checks verbatim from the build plan: the frontier answer sheets PASS
   their gates; the deliberately-stubbed answer sheet FAILS.
5. 38-scenario traceability sweep: every scenario in
   `features/idea-mode-held-out-evals/idea-mode-held-out-evals.feature` owned by a named
   test or fixture; record the map in the addendum doc.
6. Record measured baselines (frontier per-axis results, integrity totals) into the
   addendum's baseline table; note the new integrity total as a strict superset of the
   frozen 33.
7. Final commit; hand the DRAFT addendum to Rich for the freeze commit (freeze = his
   commit, house convention). Update the SPL build plan + Fable-window plan status notes.

## Acceptance Criteria

- [ ] Verifier integrity green including all new fixtures (build-plan criterion 1)
- [ ] Frontier sheets pass; stub sheet fails (criteria 2–3)
- [ ] Frozen non-regression proven (33 pre-existing checks unchanged; frozen dry-run sha-identical)
- [ ] Traceability map complete (38/38)
- [ ] Addendum baseline table filled from measurement, not estimation
- [ ] Dated status notes appended to the two ai-transition planning docs
