# Feature Spec Summary: General-Capability Regression Suite (FEAT-EVAL-GC / OBS-7)

**Feature id (working):** FEAT-EVAL-GC (observability lane OBS-7; flywheel ladder Step 9; D-OBS-3 FILED 2026-07-09 — fund now)
**Stack**: python (stdlib + pytest only — frozen-suite design rule; the execution sandbox is the one sanctioned execution surface and is itself stdlib-only)
**Generated**: 2026-07-10 (attended /feature-spec session; Fable)
**Scenarios**: 32 total (10 smoke, 2 regression)
**Assumptions**: 13 total (0 high-risk open — 3 low / 7 medium / 3 high confidence, **all human-resolved: Rich accepted every proposed default 2026-07-10**)
**Review required**: No — but see the freeze note below.

> **Freeze note (binding, house procedure):** ASSUM-001/002/003/010 are Rich's
> *threshold* values (subset composition, regression margin, no-absolute-floor,
> G-G gate ids + dispositions). Accepting this spec does **not** freeze them:
> they are PROPOSED until the build session hands `docs/research/ideas/`
> `gc-heldout-suite-scope.md` to Rich and he freezes by commit **before the first
> grade** — the G-C/G-Q lineage. After a freeze, thresholds may only be raised
> between candidates, and instrument revisions reopen the doc before the next
> freeze, never silently.

## Scope

Additive new suite `gc-heldout` (tasks `gc-held-001-humaneval`, `gc-held-002-mbpp`) giving every fine-tune grade a paired general-capability side: a fixed, content-pinned 25+25-row HumanEval/MBPP subset run against the served GGUF via llama-swap and graded **by execution** — candidate programs run against the benchmarks' reference assertions inside a stdlib-only subprocess sandbox (fresh isolated interpreter, scrubbed env, scratch CWD, resource limits, network denied; **sandbox unavailable ⇒ refuse loud, never degrade**). The verdict is **relative regression against a frozen base-model baseline of the same base + quant family** (the coach-ft-v3 Q4_K_M vs base Q4_K_XL lesson), never absolute capability (contamination residual pre-registered: these benchmarks sit in base-model pretraining). Provisioning is resolved **in-repo**: public, permissively-licensed rows committed with per-row SHA-256 pins; the private-asset symlink farm (`link_assets.py` + `ASSETS.sha256`) is deliberately not deepened. Frozen suites (po/arch/coach/qav) are untouched and provably byte-identical; house conventions carried over: K=3 reps, per-rep config records, INVALID-not-failed incomplete runs, verifier-integrity battery (Oracle passes; every broken fixture fails exactly its owning test), `runs/gc-heldout/<candidate>-<date>/` per the `61df81a` convention.

**The two named "M not S" spec problems, resolved:**
1. **Execution sandbox** — first suite to execute model-generated code. Decision: stdlib subprocess sandbox, no Docker on the grading path (DF-001 posture); refuse-loud when isolation is unavailable. Sandbox behaviour is itself integrity-tested (timeout kill, network denial, filesystem confinement, memory/process limits, env scrub, grader-crash-vs-candidate-FAIL distinction).
2. **Provisioning** — in-repo commit of the pinned subset (HumanEval MIT, MBPP CC BY 4.0) with licence/provenance record; no symlink-farm deepening.

**Sequencing (pinned upstream):** lands **before the qav-ft-v1 grade** (D-OBS-3). From first availability the S10 §2.5 paired-grade rule binds: every fine-tune grade runs role suite + this slice on the same candidate and serving config; until then RESULTS carry "general side UNMEASURED".

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 7 |
| Boundary conditions (@boundary) | 6 |
| Negative cases (@negative) | 11 |
| Edge cases (@edge-case) | 12 |

(Categories overlap: 2 scenarios are both @boundary and @negative; 4 are both @negative and @edge-case. 6 scenarios came from the accepted Phase-4 expansion: env scrub, process-count limit, grader-crash routing, row-id collision, transport abort, truncated response.)

## Pre-registered gates (PROPOSED — Rich freezes on the scope doc)

| Gate | What | Threshold (proposed) | FAIL disposition |
|---|---|---|---|
| G-G1 | Run validity + extraction contract | All rollouts complete with per-rep records; every response grades (unparseable = row FAIL, not INVALID) | Serving/harness defect route — not a training-data verdict |
| G-G2 | HumanEval regression floor | Solved count ≥ baseline − 2 rows, 3/3 reps | **NO-DEPLOY** — forgetting measured; failing rows named |
| G-G3 | MBPP regression floor | Solved count ≥ baseline − 2 rows, 3/3 reps | **NO-DEPLOY** |
| G-G4 | Sandbox + pin integrity (standing, pre-grade) | Content pins verified; sandbox self-test green; frozen-suite battery green | **BLOCK GRADING** — repair harness, then grade (candidate unjudged) |

Baselines: measured at build time on the served base handle, recorded per base + quant family, content-pinned; a candidate with no matching-family baseline is blocked until one is added additively.

## Deferred Items

None — all four groups accepted as-is; all six expansion scenarios included.

## Open Assumptions (low confidence)

None open — ASSUM-001/002/003 are low-confidence *by nature* (freeze values) but were explicitly confirmed by Rich in-session; they convert to frozen thresholds via the scope-doc freeze, not via this spec.

## Integration with /feature-plan

    /feature-plan "General-Capability Regression Suite (FEAT-EVAL-GC)" \
      --context features/gc-heldout-suite/gc-heldout-suite_summary.md

Build-session pointers: runner precedent `runs/coach-heldout/coach-ft-v3-2026-07-09/run_coach_heldout.py`; grader/integrity precedent `tests/test_qav_verifier_integrity.py`; scope-doc template `docs/research/ideas/qav-heldout-suite-scope.md` (the most recent freeze); serving truth `dgx-spark/examples/llama-swap-config.gb10-live-2026-07-06-tutor-default.yaml`. Operator riders for the grade run: the keepalive/probe-list foot-gun and GB10 sudo note in the coach-ft-v3 RESULTS morning check.
