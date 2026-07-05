---
id: TASK-REV-09AB
title: "Plan: Idea-Mode Held-Out Eval Tasks"
status: completed
created: 2026-07-05T08:30:00Z
updated: 2026-07-05T09:15:00Z
priority: high
task_type: review
tags: [feature-plan, po-heldout, eval-suite, spl-g2]
complexity: 0
clarification:
  context_a:
    timestamp: 2026-07-05T08:28:00Z
    decisions:
      focus: all
      tradeoff: quality
  context_b:
    timestamp: 2026-07-05T09:25:00Z
    decisions:
      approach: "hand-build in-session (Option 1, recommended)"
      execution: sequential
      testing: "verifier-integrity discipline (per frozen-suite ethos)"
      frontier_sheets: both_tasks
test_results:
  status: pending
  coverage: null
  last_run: null
review_results:
  mode: decision
  depth: standard
  findings_count: 27
  recommendations_count: 12
  decision: implement
  implementation_feature: FEAT-0760
  report_path: .claude/reviews/TASK-REV-09AB-review-report.md
  completed_at: 2026-07-05T09:15:00Z
---

# Task: Plan: Idea-Mode Held-Out Eval Tasks

## Description

Decision review for FEAT-EVAL-IDEA (SPL build-plan gate G2): plan the additive
extension of the frozen PO held-out suite with `po-held-005-idea` and
`po-held-006-scope`, per the canonical curated spec at
`features/idea-mode-held-out-evals/` (36 scenarios, 10 human-resolved
assumptions, fork-reconciled 2026-07-05).

## Review Scope

- Technical options for implementing the new graders (invention anchors,
  constraint-carried, selection-subset/closure) against the frozen stdlib+pytest
  harness.
- Architecture fit: additive-only composition with `harness/po_contract.py`,
  `harness/grading.py`, `harness/run_po_eval.py` (suite tag + `--suite` flag),
  and `tests/test_verifier_integrity.py` auto-discovery.
- Task breakdown with dependencies and waves; verifier-integrity discipline
  (§3.5) as the acceptance floor for every task.
- Risks: frozen-suite contamination, anchor over/under-fitting, oracle/fixture
  authorship order.

## Acceptance Criteria

- [ ] Technical options analysed with a recommended approach
- [ ] Task breakdown ready for [I]mplement (waves, dependencies, complexity)
- [ ] Frozen-suite freeze discipline preserved in every proposed change
- [ ] Validation criteria from SPL build plan Session 1 mapped to tasks

## Context

- Canonical spec: `features/idea-mode-held-out-evals/idea-mode-held-out-evals_summary.md`
- Frozen suite scope: `docs/research/ideas/po-heldout-suite-scope.md` (§5 FROZEN 2026-07-03)
- SPL build plan Session 1: `../ai-transition/docs/sovereign-planning-loop-build-plan.md`
