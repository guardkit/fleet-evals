---
id: TASK-GCH-007
title: "RESULTS-gc-heldout-TEMPLATE.md + scope doc (PROPOSED, ready for Rich's freeze) + baseline runbook"
status: completed
task_type: documentation
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 6
implementation_mode: direct
complexity: 4
priority: high
dependencies: [TASK-GCH-001, TASK-GCH-002, TASK-GCH-003, TASK-GCH-004, TASK-GCH-005, TASK-GCH-006]
created: 2026-07-10T13:56:30Z
---

# TASK-GCH-007 — Docs wave (the freeze hand-off + the deferred-GPU closing artifact)

## Scope

1. **NEW** `RESULTS-gc-heldout-TEMPLATE.md` — the RESULTS-*-TEMPLATE pattern: candidate +
   frozen thresholds reference + verifier-integrity-at-grade-time line + per-task × per-rep
   G-G table + §3 verdict applied verbatim + INVALID reps + paired-grade line (role suite +
   this slice on the same candidate/serving config, S10 §2.5).
2. **NEW** `docs/research/ideas/gc-heldout-suite-scope.md` — **Status: PROPOSED — awaiting
   Rich's freeze-by-commit (DO NOT freeze in this session)**. Carries: subset composition
   (the actual pinned row ids + exclusions), the −2-row margin (per benchmark, per rep,
   3/3 reps), no-absolute-floor-in-v1, the G-G1..G-G4 gate table + dispositions, the
   matching-family rule, baseline aggregation (baseline_solved = median of the base
   model's 3 reps — NEW proposed value, flagged), sampling posture, extraction contract,
   sandbox residuals register (NPROC per-UID; CWD-scoping not mount-ns; MBPP asserts
   in-prompt; contamination residual pre-registered), build-time calibration table
   (measured, not estimated), baselines §6 (battery counts + byte-identical proof), freeze
   procedure §8 (freeze precedes the first grade, which precedes the qav-ft-v1 grade —
   D-OBS-3).
3. **NEW** `docs/runbooks/gc-heldout-baseline-run.md` — the named closing artifact for the
   deferred GPU step: serve the base model of qav-ft-v1's base+quant family via llama-swap;
   run K=3 reps per task with `run_gc_heldout.py`; grade each rep; add the family record
   ADDITIVELY to `harness/gc_baselines.json`; commit; THEN hand the scope doc to Rich for
   freeze. Include the GB10 operator riders: keepalive/probe-list foot-gun and the
   interactive-sudo note (`sudo systemctl start llama-swap-keepalive.timer` cannot run
   unattended).
4. Move feature tasks to `tasks/completed/2026-07/gc-heldout-suite/` per house convention.

## Acceptance Criteria

- [ ] Scope doc carries every PROPOSED freeze value from ASSUM-001/002/003/010 plus the
      flagged additions (median aggregation; MBPP no-carve-out reading; refuse-loud netns
      requirement) — nothing frozen, everything ready to freeze
- [ ] Runbook is executable start-to-finish by an operator with no session context
- [ ] RESULTS template mirrors the house pattern and carries the "general side" pairing
      line for role-suite RESULTS
- [ ] Full battery green; byte-identical proof recorded in the scope doc §6
