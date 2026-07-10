# GC Held-Out Suite — General-Capability Regression (FEAT-EVAL-GC / OBS-7)

**Status:** **PROPOSED — awaiting Rich's freeze-by-commit.** Nothing here gates anything
yet. Freeze order is pinned by D-OBS-3: this doc freezes **before the suite's first
grade**, which lands **before the qav-ft-v1 grade**. Between now and the freeze the
values below are Rich's to amend; after the freeze, thresholds may only be **raised**
between candidates, and any instrument revision reopens this doc BEFORE the next
freeze, never silently (the G-C4/G-Q4 lineage).
**Date:** 2026-07-10 (Fable build session; flywheel ladder Step 9 build half — spec
63ec53f, attended /feature-spec, 13 assumptions Rich-accepted 2026-07-10)
**Repo:** fleet-evals · new suite `gc-heldout` (tasks `gc-held-001-humaneval`,
`gc-held-002-mbpp`)
**Relationship to the frozen suites:** strictly additive, identical posture to the
arch/coach/qav scopes (frozen files never edited; frozen discovery globs blind to
`gc-held-*` by construction; the pre-change 229 node-verdicts re-ran byte-identical, §6).
**Consumer (named): every fine-tune deploy gate, from this suite's first availability.**
The S10 §2.5 paired-grade rule binds: every fine-tune grade runs role suite + this slice
on the same candidate and serving config. First mandatory pairing: the **qav-ft-v1
grade** (D-OBS-3, FILED 2026-07-09 — fund now). Until the freeze + baseline exist,
RESULTS carry "general side UNMEASURED".

---

## 1. Tasks

| Task | Seat under test | Artifact | Correct behaviour |
|---|---|---|---|
| `gc-held-001-humaneval` | the served checkpoint's general Python competence over 25 pinned HumanEval rows | `programs/{ROW-ID}.py` per row (+ `rows/{ROW-ID}.json` diagnostics) | solved ≥ same-family baseline − 2, every rep |
| `gc-held-002-mbpp` | same seat over 25 pinned MBPP rows | same | same |

K = 3 reps per task; generation timeout 300 s per model call; per-row execution timeout
10 s wall-clock; grading via `PO_EVAL_OUTPUT_DIR` → per-task `pytest test/ -q`.
**Runner divergence, by design (ASSUM-013):** answer sheets are produced by
`harness/run_gc_heldout.py` (one fresh toolless generation per pinned row per rep against
the llama-swap handle), NOT by `harness/run_po_eval.py` (untouched). Per-rep records pin:
model id + lineage + **base+quant family** + template + sampling + prompt hashes + row SHAs.

## 2. Row lineage, provisioning, and instruments (pinned)

- **Subset composition (freeze value, ASSUM-001):** 25 + 25 rows, committed in-repo with
  per-row SHA-256 pins (`input/manifest.json`). Selection rule applied verbatim:
  ascending NUMERIC benchmark task-id; a row is excluded — recorded with reason — iff its
  canonical solution fails under the pinned interpreter (Python 3.12.3) inside the gc
  sandbox (the same surface that grades candidates); first 25 survivors pinned.
  **Result: HumanEval/0–HumanEval/24 (`HumanEval-0..24`) and MBPP task_id 1–25
  (`mbpp-1..25`); ZERO exclusions were needed.** No split carve-outs: MBPP ids 1–10 are
  conventionally few-shot rows, but the accepted rule is ascending-after-exclusions
  verbatim and this suite prompts zero-shot — recorded here so the freeze covers the
  reading. Row ids are unique across the whole suite (integrity-tested).
- **Provisioning (ASSUM-007):** public, permissively-licensed data committed in-repo —
  HumanEval (MIT, `openai/human-eval` @ `463c980`), MBPP (CC BY 4.0,
  `google-research/google-research` @ `f82046b`); licence/provenance + contamination
  residual pre-registered in each task's `input/PROVENANCE.md`. The private-asset symlink
  farm (`link_assets.py` + `ASSETS.sha256`) is untouched and NOT deepened.
- **Sandbox (ASSUM-008; the first suite to execute model-generated code):** stdlib-only
  subprocess, no Docker — `unshare -rn` (fresh unprivileged user+network namespaces) +
  `python3 -I` per row, scrubbed allowlist env, throwaway scratch CWD, rlimits (CPU,
  512 MB address space, process count, file size, no cores), wall-clock kill via process
  group. **Network isolation is REQUIRED, not best-effort:** `ensure_available()` must
  demonstrate connection denial before any grading; any missing isolation leg ⇒
  `SandboxUnavailable` naming it ⇒ **refuse loud, never degrade** (G-G4). Sandbox
  behaviour is itself integrity-tested (17 nodes: timeout kill, net+DNS denial, env
  scrub, write confinement, memory/process containment, refuse-loud probes,
  single-spawn-site proof).
- **Extraction contract (pinned):** first fenced code block wins (trailing prose
  tolerated); a bare response that parses as Python is accepted; anything else is a row
  FAIL with an extraction reason. `finish_reason == "length"` is a row FAIL recorded as
  `truncated-generation` — a diagnostic DISTINCT from execution failure. Unparseable
  output is a row FAIL under G-G1, never an INVALID run and never a harness crash.
- **Verdicts come from execution only:** the gate battery assembles candidate program +
  the benchmark's reference assertions (grader-side; never part of the candidate
  program) and executes in the sandbox. No text matching, ever. A grader crash surfaces
  as a pytest ERROR — the G-G1 harness-defect route, never a candidate FAIL.
- **Prompt convention (ASSUM-009, hash-recorded per rep):** pinned minimal system prompt;
  HumanEval = signature+docstring completion; MBPP = problem text + the benchmark's
  reference asserts verbatim (the standard convention). Single source:
  `harness/gc_rows.py`.

## 3. Pre-registered verdict (Rich amends then freezes; freeze precedes the first grade)

**Validity gate:** all 6 rollouts (2 tasks × K=3) produced by the pinned config with
per-rep records; aborted reps (transport `ABORTED.json`, serving eviction) re-run in
place under the same pinned config, never skipped — an incomplete run is **INVALID, not
a failure**. A gc-heldout run never reuses another suite's output directory.

**FEAT-EVAL-GC PASS (the general-capability side of a fine-tune grade) requires all of:**

- **G-G1 — Run validity + extraction contract: 6/6 reps.** Every rep's
  `test_answer_sheet_contract` + `test_rows_grade_by_execution` pass: per-rep records
  complete, every pinned row reaches a definite executed verdict (unparseable/truncated =
  row FAIL, not INVALID).
- **G-G2 — HumanEval regression floor: 3/3 gc-held-001 reps** pass
  `test_regression_floor`: solved count ≥ **matching-family baseline − 2 rows**
  (freeze value, ASSUM-002: an integer row count, not a rate, at this N — 2 rows ≈ 8pp).
- **G-G3 — MBPP regression floor: 3/3 gc-held-002 reps** — same rule, other benchmark.
- **G-G4 — Sandbox + pin integrity (standing, pre-grade):** content pins verified
  (`test_input_pins_intact`), sandbox self-test green
  (`test_sandbox_isolation_available`), full verifier-integrity battery green at grade
  time.

**Structural rules carried into the gate implementation (not conventions):**
- **Matching-family rule:** a candidate is compared ONLY against a frozen baseline of its
  own `base_family/quant` (the coach-ft-v3 Q4_K_M vs base Q4_K_XL lesson). No matching
  record in `harness/gc_baselines.json` ⇒ grading BLOCKED with the gap named and routed
  to "measure a baseline additively" — a cross-family comparison is never performed.
- **No absolute floor in v1 (freeze value, ASSUM-003):** the gate is purely
  baseline-relative; a floor may be added additively at freeze once the base baseline is
  measured.
- **Baseline aggregation (NEW PROPOSED value — flag for Rich):** a family's
  `baseline_solved` per benchmark = the **median** of the base model's 3 baseline rep
  solved counts (all three recorded in the family record). Also proposed: if the base's
  own reps do not pass their own family floor (rep variance > margin), the margin
  assumption is broken — reopen this doc before freezing.

**Pre-registered dispositions (a FAIL routes, it does not silently retry):**
- G-G1 FAIL → serving/harness defect: fix transport/extraction/records; re-grade. Not a
  training-data verdict.
- G-G2 / G-G3 FAIL → **NO-DEPLOY** — catastrophic forgetting measured; the failing
  benchmark and the lost rows are NAMED in RESULTS; the fine-tune recipe (not the eval)
  is revised.
- G-G4 FAIL → **BLOCK GRADING** — repair harness/pins, then grade. The candidate is
  unjudged, not failed.

**If not met:** the candidate does not deploy regardless of its role-suite grade; the
failing axis is named in the RESULTS doc; re-grade only after a model or task-instrument
revision (instrument revisions reopen this doc *before* the next freeze, never silently).

## 4. Build-time calibration (sanctioned while PROPOSED; measured 2026-07-10, not estimated)

| Item | Method | Result |
|---|---|---|
| Oracle catchability | canonical solutions graded as answer sheets, by execution | **25/25 PASS on both tasks** (gate battery green against `solution/`) |
| Margin boundary | good fixture `within-margin` (exactly 2 lost rows, solved 23 = floor) | **PASSES the whole battery** — the gate is not stricter than registered |
| Regression demo | broken fixtures `regressed-beyond-margin` (3 lost rows, both tasks) | **FAIL exactly** `test_regression_floor`, lost rows named |
| Matching-family demo | broken fixture `unknown-baseline-family` | **FAILS naming** the missing `base_family/quant` and the additive-measure route |
| Contract demo | broken fixtures `missing-candidate-record`, `foreign-row-injected` | Each **FAILS exactly** `test_answer_sheet_contract` |
| Truncation routing | broken fixture `truncated-rows-regress` (3 × finish_reason=length) | rows FAIL as `truncated-generation` (distinct diagnostic) and **the floor catches the loss** |
| Extraction-failure routing | good fixture `extraction-fail-row-within-margin` | a missing program is a clean row FAIL; the sheet still **PASSES** within margin |
| Pin drift | corrupted-copy demonstration | `verify_pins` **names the drifted row**; gate blocks before execution |
| Sandbox integrity | 17-node battery | timeout kill ✅ net+DNS denial ✅ env scrub ✅ memory/process containment ✅ refuse-loud probes ✅ |
| Spec margin table | unit battery (baseline 20: candidate 20/18/17) | **pass / pass / fail** — verbatim |

## 5. Accepted residuals — recorded so the G-G gates are never overread

Contamination: both benchmarks sit in base-model pretraining; MBPP additionally shows its
reference asserts in-prompt (the standard convention). The verdict is therefore RELATIVE
regression vs the same-family base baseline, never absolute capability — by construction ·
Filesystem confinement is scratch-CWD scoping + host DAC, not a mount namespace; the
threat model is accident (our own checkpoints' output), not malice · RLIMIT_NPROC is
per-UID: any fork/thread from candidate code fails immediately on a busy host — benchmark
solutions are single-threaded pure functions · pass@1 with K=3 at N=25 bounds statistical
power; the margin is an integer row count for exactly this reason; the suite grows
additively, floors never shrink · the extraction contract is a detection floor — a model
that answers correctly outside every accepted shape fails the row (bounded by the
bare-code fallback) · serving posture variance (temp 0.1 sampling is not greedy) is
absorbed by the margin, not modelled · no negation heuristics, ever — transparent
execution verdicts with no hidden logic.

## 6. Baselines (measured at build end, 2026-07-10 — not estimated)

| Measurement | Value |
|---|---|
| Full `tests/` battery | **299/299 green** (229 pre-existing byte-identical + 70 additive gc nodes: 17 sandbox + 32 gates/rows + 21 verifier-integrity) |
| Frozen baseline byte-identical | **CONFIRMED** — `comm` diff of the pre-change 229 node-id+verdict capture vs the final run = 0 lost, 70 added, 0 failures |
| Frozen files untouched | **CONFIRMED** — additive paths only; `git status` over tracked files = empty throughout the build (every gc file is NEW) |
| Oracle, both tasks | 5/5 gate tests PASS each (25/25 rows solved, by execution) |
| Fixture floors (registered) | 001 = 4 broken + 2 good; 002 = 2 broken + 1 good — pinned in `tests/test_gc_verifier_integrity.py` |
| Base-model family baselines | **NONE YET — deliberately.** No GPU in the build session (a build owns the GB10). `harness/gc_baselines.json` ships with only the synthetic `integrity-fixture/NONE` instrument family. The first real family record is the operator runbook's job: `docs/runbooks/gc-heldout-baseline-run.md` |
| Symlink-farm coupling | **not deepened** — public data in-repo; `harness/link_assets.py` + `ASSETS.sha256` untouched |

## 7. RESULTS template

`RESULTS-gc-heldout-TEMPLATE.md` (committed): candidate + family key + frozen-thresholds
commit + verifier-integrity-at-grade-time line + **paired-grade link to the role suite's
RESULTS for the same candidate and serving config (S10 §2.5)** + per-task × per-rep G-G
table + §3 verdict applied verbatim + INVALID reps with re-run evidence. Runs live under
`runs/gc-heldout/<candidate>-<date>/` (committed home, the `61df81a` convention).

## 8. Freeze procedure

This doc is handed to Rich with the build → the **baseline runbook step runs first**
(the GB10 must free; the matching family is dictated by the first candidate, qav-ft-v1's
serving posture) and its family record lands additively in `harness/gc_baselines.json` →
Rich amends §3 if needed (the −2 margin, the no-absolute-floor choice, and the NEW median
aggregation rule are his freeze values) and **freezes by commit** → only then does the
first grade run. After the freeze, the S10 §2.5 paired-grade rule reads "general side
MEASURED" and every fine-tune grade carries both verdicts without re-deriving anything.
