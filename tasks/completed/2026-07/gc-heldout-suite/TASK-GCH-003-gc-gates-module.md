---
id: TASK-GCH-003
title: "harness/gc_gates.py — extraction contract, execution grading, pins, G-G verdicts, matching-family rule"
status: completed
task_type: feature
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 3
implementation_mode: task-work
complexity: 7
priority: high
dependencies: [TASK-GCH-001, TASK-GCH-002]
created: 2026-07-10T13:56:30Z
consumer_context:
  - task: TASK-GCH-001
    consumes: SANDBOX_RESULT_AND_AVAILABILITY
    framework: "stdlib subprocess sandbox"
    driver: "python3 stdlib"
    format_note: "grade_rows() executes exclusively via run_program(); grader exceptions propagate (harness defect), candidate failures return row FAIL"
  - task: TASK-GCH-002
    consumes: PINNED_ROW_SCHEMA_AND_MANIFEST
    framework: "stdlib json (frozen-suite grader style)"
    driver: "python3 stdlib"
    format_note: "row.json canonical bytes hashed with SHA-256 must equal the manifest pin; verify_pins() runs before any model call"
---

# TASK-GCH-003 — Grading + verdict harness (stdlib-only)

## Scope

**NEW** `harness/gc_gates.py` — pure functions returning structured findings (the
coach_gates/qav_gates house style), plus **NEW** `harness/gc_baselines.json` and
**NEW** `tests/test_gc_gates.py` unit battery.

1. **Pins (G-G4):** `verify_pins(task_dir)` — every `input/rows/{ID}/row.json` hashes to
   its manifest pin; manifest row set == on-disk row set; row-id uniqueness (per task and,
   via the integrity battery, across the suite). A drifted or missing row is a finding
   NAMING the row; grading is blocked before any model call.
2. **Extraction contract (pinned):** `extract_program(text)` — first fenced code block
   (```python/```py/```), else the raw text iff it `ast.parse`s, else `ExtractionError`.
   Trailing prose after one fence tolerated (@boundary scenario).
3. **Answer-sheet contract (G-G1):** `answer_sheet_findings(task_dir, output_dir)` —
   `candidate.json` present + well-formed ({model_id, base_family, quant} or
   {"oracle": true}); every manifest row is addressed (program file present OR
   `rows/{ID}.json` diagnostic recording why not); no foreign program files.
4. **Grading by execution (G-G1 body):** `grade_rows(task_dir, output_dir, run=...)` —
   per row: truncated generation (`finish_reason == "length"`) ⇒ FAIL("truncated-generation")
   recorded as a diagnostic DISTINCT from execution failure; missing program ⇒
   FAIL("no-extractable-program"); else assemble candidate program + benchmark reference
   asserts and execute in the sandbox ⇒ PASS / FAIL("execution: ..."). Unparseable = row
   FAIL, never INVALID; the run proceeds to the next row.
5. **Matching-family rule (STRUCTURAL) + regression floor (G-G2/G-G3):**
   `resolve_baseline(candidate, baselines)` — family key `"{base_family}/{quant}"`; no
   matching-family record ⇒ blocking finding naming the missing baseline (NEVER a
   cross-quant comparison — the coach-ft-v3 Q4_K_M vs Q4_K_XL lesson).
   `regression_floor_findings(solved, baseline_solved, margin=REGRESSION_MARGIN_ROWS)` —
   PASS iff `solved >= baseline_solved - 2` (PROPOSED; per benchmark, per rep); failing
   rows NAMED. Oracle mode: solved must == row count.
6. **Run-level verdict:** `apply_pre_registered_verdict(per_rep_results, ...)` — G-G1..G-G4
   with dispositions (G-G2/G-G3 FAIL ⇒ NO-DEPLOY; G-G1 ⇒ serving/harness defect route;
   G-G4 ⇒ BLOCK GRADING). 3/3 reps required per benchmark.
7. **Output-dir ownership:** `output_dir_findings(out_dir)` — a gc-heldout run refuses a
   directory carrying another suite's records (qav §5 rule generalized).
8. `harness/gc_baselines.json` ships with ONLY the synthetic `integrity-fixture/NONE`
   instrument family (documented as never-a-grading-target); real families are added
   additively by the baseline runbook.

## Acceptance Criteria

- [ ] Margin boundary table from the spec passes verbatim: baseline 20 / candidate 20 ⇒
      pass; 18 ⇒ pass; 17 ⇒ fail
- [ ] Unknown family ⇒ finding names the missing `base_family/quant` baseline and routes
      to "measure additively", never to skip or cross-family compare
- [ ] Extraction: one-fence-plus-prose extracts the fence; prose-only raises; bare
      parseable code accepted; all pinned in unit tests
- [ ] Truncation diagnostic distinguishable from execution failure in `grade_rows` output
- [ ] Grader crash propagates as an exception (harness defect), never a candidate FAIL
- [ ] PROPOSED freeze values live as named module constants (`REGRESSION_MARGIN_ROWS = 2`,
      `REPS = 3`, `ROW_TIMEOUT_S = 10.0`, `GENERATION_TIMEOUT_S = 300`) — single source
- [ ] Frozen files untouched; full battery green (failing set == baseline)
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Seam Tests

```python
"""Seam test: verify PINNED_ROW_SCHEMA_AND_MANIFEST from TASK-GCH-002."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("PINNED_ROW_SCHEMA_AND_MANIFEST")
def test_pinned_row_schema_and_manifest():
    """verify_pins() returns no findings on the committed subset and names the
    row on a corrupted copy (drift blocks grading before any model call).

    Contract: canonical row bytes SHA-256 == manifest pin. Producer: TASK-GCH-002.
    """
    from pathlib import Path
    from harness import gc_gates
    task_dir = Path("tasks/gc-held-001-humaneval")
    assert gc_gates.verify_pins(task_dir) == []
```
