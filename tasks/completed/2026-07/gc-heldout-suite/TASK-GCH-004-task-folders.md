---
id: TASK-GCH-004
title: "Task folders gc-held-001-humaneval / gc-held-002-mbpp: task.toml, instruction.md, gate battery, Oracle"
status: completed
task_type: feature
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 4
implementation_mode: task-work
complexity: 5
priority: high
dependencies: [TASK-GCH-002, TASK-GCH-003]
created: 2026-07-10T13:56:30Z
consumer_context:
  - task: TASK-GCH-003
    consumes: ANSWER_SHEET_FORMAT
    framework: "pytest gate battery via PO_EVAL_OUTPUT_DIR (house convention)"
    driver: "python3 -m pytest"
    format_note: "conftest output_dir defaults to solution/ so a bare pytest run grades the Oracle; gate tests call gc_gates functions only"
---

# TASK-GCH-004 — Suite task folders (the frozen-task anatomy)

## Scope

**NEW** `tasks/gc-held-001-humaneval/` and `tasks/gc-held-002-mbpp/`, mirroring the
coach-held anatomy:

- `task.toml`: id, `suite = "gc-heldout"`, `mode = "code-generation"`,
  `schema = "per-row candidate program graded by executed reference assertions"`,
  `artifact = "programs/{ROW-ID}.py, one per input row"`, `reps = 3`,
  `timeout_seconds = 300` (generation, per model call), grading command
  `python3 -m pytest test/ -q` with `output_env = "PO_EVAL_OUTPUT_DIR"`, and a
  [provenance] table (row lineage = pinned public subset; instruction authored 2026-07-10;
  oracle = canonical solutions; weakness_source = D-OBS-3 catastrophic-forgetting gap,
  the coach-ft-v3 general-side UNMEASURED lesson).
- `instruction.md`: the operative prompt contract — pinned minimal instruction wrapping
  benchmark content (ASSUM-009): HumanEval = signature+docstring completion, output ONE
  fenced python block, complete function definition; MBPP = problem text + the benchmark's
  reference asserts shown verbatim; sampling posture (serving-faithful; base baselines at
  temp 0.1 / top_p 0.9); K=3 reps; extraction contract reference.
- `test/conftest.py`: house wiring (`PO_EVAL_OUTPUT_DIR` defaulting to `solution/`),
  session-scoped `grades` fixture calling `gc_gates.grade_rows` ONCE per gate run, and a
  session-scoped sandbox-availability check (refuse-loud).
- `test/test_gate_gc_held_00X.py` — the gate battery:
  - `test_input_pins_intact` (G-G4): manifest pins verified before anything executes;
    drifted row NAMED
  - `test_sandbox_isolation_available` (G-G4): `ensure_available()` green
  - `test_answer_sheet_contract` (G-G1): candidate record + every row addressed + no
    foreign rows
  - `test_rows_grade_by_execution` (G-G1): every row reaches a definite PASS/FAIL by
    executed assertions; extraction/truncation failures are row FAILs with reasons
  - `test_regression_floor` (G-G2 for 001 / G-G3 for 002): oracle ⇒ all rows PASS;
    else matching-family baseline resolved (missing ⇒ FAIL naming the gap) and
    `solved >= baseline − 2` with lost rows named
- `solution/` = the Oracle (canonical programs + oracle-marked candidate.json), from
  TASK-GCH-002.

## Acceptance Criteria

- [ ] Bare `python3 -m pytest tasks/gc-held-00X/test -q` grades the Oracle: every row PASS
      on both tasks (the §3.5 house rule made mechanical)
- [ ] All five gate tests import `harness/gc_gates` / `harness/gc_sandbox` only — no logic
      in the test files beyond assertion wiring
- [ ] Frozen task globs remain blind: no frozen integrity file collects `gc-held-*`
- [ ] Full battery green; failing set == baseline
- [ ] All modified files pass project-configured lint/format checks with zero errors
