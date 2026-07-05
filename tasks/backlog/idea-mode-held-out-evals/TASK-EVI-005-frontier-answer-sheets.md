---
id: TASK-EVI-005
title: "Frontier answer sheets (both tasks) + ASSUM-009 threshold calibration"
status: backlog
task_type: operator_handoff
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 4
implementation_mode: direct
complexity: 2
priority: critical
dependencies: [TASK-EVI-002, TASK-EVI-003, TASK-EVI-004]
created: 2026-07-05T09:30:00Z
consumer_context:
  - task: TASK-EVI-003
    consumes: IDEA_BRIEF_AND_ASSEMBLY
    framework: "serving-faithful prompt assembly"
    driver: "run_po_eval.py --dry-run"
    format_note: "sheet must be produced from the dry-run-assembled prompt (system=player_idea.md, user=brief.md) so it is serving-faithful, not free-form"
---

# TASK-EVI-005 — Frontier answer sheets + calibration (ATTENDED, Fable-window-bound)

## Why operator_handoff

This task requires a frontier model (Fable, this session, in-window) answering the
dry-run-assembled prompts, plus an attended calibration judgment call. AutoBuild's
Player↔Coach loop cannot produce it. Executed attended in the current session.

## Scope

1. Assemble prompts via `run_po_eval.py --suite po-heldout-idea --dry-run` (or read the
   assembly directly): 005 (player_idea.md + brief), 006 (player_scope.md + roadmap +
   constraint).
2. Author frontier-quality answer sheets for BOTH tasks (Context B decision 2026-07-05),
   serving-shape-faithful (one think block + one fenced ProductRoadmap).
3. Store as good fixtures: `tests/good_fixtures/po-held-005-idea/frontier-baseline/`
   and `tests/good_fixtures/po-held-006-scope/frontier-baseline/`, with provenance
   (model, date, assembly sha) recorded in the fixture dirs and the addendum doc.
4. **Calibrate ASSUM-009**: run the invention gate over the 005 frontier sheet and
   natural compound-assumption shapes; if the amended >2 threshold trips the frontier
   baseline, raise to >3 (legal — addendum still DRAFT). Record the decision + evidence
   in the addendum's calibration section. Same pass for constraint-anchor paraphrase
   tolerance on the 006 sheet.

## Required operator follow-up

This task is `task_type: operator_handoff` — AutoBuild will not attempt it. The
operator (this attended session) must verify the runtime acceptance criteria below,
then mark the task complete.

- **AC-1**: Both frontier sheets pass their task's full gate battery (`pytest` with
  `PO_EVAL_OUTPUT_DIR` pointed at each fixture dir)
- **AC-2**: ASSUM-009 threshold decision recorded in the addendum doc with the
  calibration evidence (which shapes were run, what tripped)
- **AC-3**: Provenance recorded (model id, date, assembly source) per fixture
