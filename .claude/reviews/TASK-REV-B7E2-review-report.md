# Review Report — TASK-REV-B7E2 — Plan: General-Capability Regression Suite (FEAT-EVAL-GC / OBS-7)

**Mode:** decision · **Depth:** standard · **Date:** 2026-07-10
**Input:** `features/gc-heldout-suite/` @ 63ec53f (32 scenarios, 13 assumptions, all Rich-accepted 2026-07-10)
**Host verification performed:** `unshare -rn` unprivileged netns denial confirmed on this box
(ENETUNREACH from fresh netns); pinned interpreter Python 3.12.3; benchmark sources reachable
(openai/human-eval, google-research/mbpp raw). Pre-change battery: **229 passed** (105 s).

## Technical options

### Option 1 — Hand-build in-session, sandbox-first (RECOMMENDED)

Build order: sandbox → provisioning → gates → task folders + runner → integrity battery →
docs. The sandbox is built FIRST because it is the pinned interpreter's execution surface for
subset selection itself (ASSUM-001: rows whose canonical solution fails are excluded — that
check must run in the same sandbox that will grade candidates, or the exclusion rule and the
grading rule diverge).

- Complexity: 7/10 aggregate. Effort: one session.
- Pros: single-source execution semantics; matches every prior eval-suite build
  (TASK-REV-09AB context_b: eval suites are hand-built — grader/fixture authorship is
  judgment-dense and fits poorly into Player/Coach turns); battery green after every wave.
- Cons: sequential; no AutoBuild parallelism (accepted — same gates either way per brief).

### Option 2 — AutoBuild (FEAT yaml → /feature-build)

- Rejected: fixture/oracle authorship order is load-bearing (Oracle before broken fixtures,
  the §3.5 rule); the coach/qav/idea precedent is in-session; a GPU-adjacent grading suite
  benefits from continuous operator-visible verification.

### Option 3 — Reuse run_po_eval.py with a --suite branch

- Rejected by spec (ASSUM-013): runner divergence by design; `run_po_eval.py` is frozen and
  untouched. The gc runner is a direct-serving stand-in per `run_coach_heldout.py`.

## Key design decisions (from spec, resolved to mechanism)

1. **Sandbox** (`harness/gc_sandbox.py`): `unshare -rn` (util-linux, verified working
   unprivileged here) wrapping `python3 -I` per row; scrubbed allowlist env; throwaway
   scratch CWD; rlimits via preexec (CPU, AS, NPROC, FSIZE, CORE); wall-clock kill via
   process-group; `ensure_available()` probe raises `SandboxUnavailable` naming the missing
   isolation — REFUSE-LOUD, never degrade. Grader crash = pytest ERROR (harness defect,
   G-G1 route), candidate failure = row FAIL — structurally distinct.
2. **Answer-sheet format** (the `PO_EVAL_OUTPUT_DIR` contract): `candidate.json` (model id,
   lineage, base+quant family, oracle flag), `programs/{ROW-ID}.py` (extracted candidate
   program), optional `rows/{ROW-ID}.json` (finish_reason, extraction diagnostics). The
   Oracle is `solution/` with canonical programs + an oracle-marked candidate.json.
3. **Grading**: gate battery executes candidate program + reference asserts in the sandbox;
   verdict from executed assertions only. Missing/unparseable program = row FAIL
   (extraction reason), never INVALID. finish_reason=length = row FAIL (truncated) —
   diagnostic distinct from execution failure.
4. **Matching-family rule (structural)**: `harness/gc_baselines.json` keyed by
   `<base-family>/<quant>`; gate test resolves the candidate's declared family; missing ⇒
   the floor test FAILS naming the missing baseline — grading blocked, never cross-quant.
   Oracle mode requires solved == N (the canonical-solutions-all-pass scenario).
   Ships with only the `integrity-fixture/NONE` synthetic instrument entry; real families
   are added additively by the baseline runbook.
5. **Selection rule** (ASSUM-001, pinned): ascending numeric benchmark task-id; canonical
   solution must PASS in the gc sandbox under Python 3.12.3; first 25 survivors per
   benchmark; exclusions recorded with reasons in the manifest.
6. **Baseline aggregation (NEW PROPOSED value for the scope doc)**: `baseline_solved` per
   benchmark = median of the base model's 3 baseline reps (all three recorded). Flagged for
   Rich at freeze alongside ASSUM-001/002/003/010 values.

## Risks

- **Battery wall-clock growth**: each Oracle/fixture gate run executes ≤25 sandboxed
  programs. Mitigation: session-scoped grades fixture (grade once per gate run); short
  timeouts in sandbox integrity tests. Budget ≤ +90 s over the 105 s baseline.
- **RLIMIT_NPROC is per-UID**: on a busy host any fork/thread from candidate code fails
  immediately. Acceptable — accident-class threat model; benchmark solutions are
  single-threaded pure functions. Recorded as residual in the scope doc.
- **FS confinement is CWD-scoping, not mount-ns**: absolute-path writes constrained only by
  host DAC. Accident-class residual; recorded in the scope doc.
- **MBPP asserts in-prompt** (standard convention) means the model sees the tests it must
  pass; contamination residual already pre-registered — the verdict is relative regression.

## Task breakdown → FEAT (7 tasks, 6 waves, sequential)

| Task | What | Cx | Deps |
|---|---|---|---|
| TASK-GCH-001 | Sandbox module + sandbox integrity tests | 6 | — |
| TASK-GCH-002 | Benchmark provisioning: pinned 25+25 subset, manifests, provenance | 6 | 001 |
| TASK-GCH-003 | `harness/gc_gates.py`: extraction, grading, pins, G-G verdict, family rule | 7 | 001, 002 |
| TASK-GCH-004 | Task folders `gc-held-001/002`: task.toml, instruction, gate tests, Oracle | 5 | 002, 003 |
| TASK-GCH-005 | Runner `harness/run_gc_heldout.py` (direct-serving stand-in) | 5 | 003 |
| TASK-GCH-006 | Verifier-integrity battery + broken/good fixtures + floors | 6 | 004 |
| TASK-GCH-007 | RESULTS template, scope doc (PROPOSED), baseline runbook | 4 | all |

**Decision: [I]mplement** — structure generated at `tasks/backlog/gc-heldout-suite/`.
