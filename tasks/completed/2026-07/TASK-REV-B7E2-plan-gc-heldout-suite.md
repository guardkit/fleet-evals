---
id: TASK-REV-B7E2
title: "Plan: General-Capability Regression Suite (FEAT-EVAL-GC / OBS-7)"
status: completed
created: 2026-07-10T13:56:30Z
updated: 2026-07-10T14:10:00Z
priority: high
task_type: review
tags: [feature-plan, gc-heldout, eval-suite, obs-7, d-obs-3, flywheel-step-9]
complexity: 0
clarification:
  context_a:
    timestamp: 2026-07-10T13:56:30Z
    source: "pre-answered — attended /feature-spec session 2026-07-10 (63ec53f) + Step 9 build brief; no live operator in this session"
    decisions:
      focus: all
      tradeoff: quality
      concerns: "frozen-suite byte-identity; sandbox refuse-loud; matching-family rule structural"
  context_b:
    timestamp: 2026-07-10T13:56:30Z
    source: "house precedent TASK-REV-09AB/FEAT-0760 (eval-suite features are hand-built in-session) + build brief"
    decisions:
      approach: "hand-build in-session (runner-divergence precedent; stdlib subprocess sandbox per ASSUM-008)"
      execution: sequential
      testing: "verifier-integrity discipline (three-sided proof; full battery green after every wave)"
      gpu: "NONE — baseline graded run is a named operator runbook, not executed here"
test_results:
  status: pending
  coverage: null
  last_run: null
review_results:
  mode: decision
  depth: standard
  decision: implement
  implementation_feature: FEAT-FA7A
  report_path: .claude/reviews/TASK-REV-B7E2-review-report.md
  completed_at: 2026-07-10T14:10:00Z
---

# Task: Plan: General-Capability Regression Suite (FEAT-EVAL-GC / OBS-7)

## Description

Decision review for FEAT-EVAL-GC (flywheel ladder Step 9, D-OBS-3 funded
2026-07-09): plan the additive `gc-heldout` suite (tasks `gc-held-001-humaneval`,
`gc-held-002-mbpp`) per the committed spec at `features/gc-heldout-suite/`
(32 scenarios, 13 Rich-confirmed assumptions, accepted 2026-07-10, commit 63ec53f).

## Review Scope

- Suite assets: pinned 25+25 HumanEval/MBPP subset committed in-repo with
  per-row SHA-256 pins + licence/provenance (ASSUM-001/007); symlink farm and
  `link_assets.py`/`ASSETS.sha256` untouched.
- Sandbox: stdlib-only subprocess, refuse-loud (ASSUM-008); no Docker.
- Harness integration: gate battery via `PO_EVAL_OUTPUT_DIR` per-task pytest,
  runner as direct-serving stand-in (ASSUM-013), `runs/gc-heldout/<candidate>-<date>/`.
- Gates G-G1..G-G4 with PROPOSED values (ASSUM-002/003/010); matching-family
  rule structural, never a cross-quant comparison.
- Scope doc + RESULTS template + baseline runbook (no GPU in this session).

## Acceptance Criteria

- [x] Technical options analysed with a recommended approach
- [x] Task breakdown ready for [I]mplement (waves, dependencies, complexity)
- [x] Frozen-suite freeze discipline preserved in every proposed change
- [x] All 32 spec scenarios mapped to tasks

## Context

- Canonical spec: `features/gc-heldout-suite/gc-heldout-suite_summary.md`
- Runner precedent: `runs/coach-heldout/coach-ft-v3-2026-07-09/run_coach_heldout.py`
- Integrity precedent: `tests/test_qav_verifier_integrity.py`
- Scope-doc template: `docs/research/ideas/qav-heldout-suite-scope.md`
- Sequencing: freeze before first grade, before qav-ft-v1 grade (D-OBS-3)
