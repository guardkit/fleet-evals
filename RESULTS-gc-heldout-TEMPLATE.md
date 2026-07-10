# RESULTS — gc-heldout general-capability regression — <candidate-id> — <date>

**Candidate:** <serving model id + lineage + quant, e.g. qav-ft-v1 = gemma-4-26b + QLoRA-<hash>, Q4_K_M, llama-swap :9000>
**Family key (matching-family rule):** `<base_family>/<quant>` — frozen baseline record present in `harness/gc_baselines.json` at commit `<sha>` (**a missing matching-family baseline BLOCKS grading — measure it additively first; never a cross-quant comparison**)
**Frozen thresholds:** gc-heldout-suite-scope.md §3, frozen at commit `<freeze-sha>`
**Verifier integrity at grade time:** `python3 -m pytest tests/ -q` → <N> passed (MUST be green before grading — G-G4 is standing)
**Paired grade (S10 §2.5):** role-suite RESULTS for the SAME candidate + serving config: `<link>` — a fine-tune grade without this general-capability side is incomplete from this suite's first availability
**Runner divergence (by design):** answer sheets produced by `harness/run_gc_heldout.py` (one fresh generation per pinned row per rep, toolless), NOT `harness/run_po_eval.py`. Per-rep records pin: model id + lineage + base/quant family + template + sampling + prompt hashes + row SHAs.

## Per-task × per-rep

| Task | Rep | G-G4 pins+sandbox | G-G1 contract+extraction | G-G2/G-G3 regression floor | solved/25 | verdict |
|---|---|---|---|---|---|---|
| gc-held-001-humaneval | 1 |  |  |  |  |  |
| gc-held-001-humaneval | 2 |  |  |  |  |  |
| gc-held-001-humaneval | 3 |  |  |  |  |  |
| gc-held-002-mbpp | 1 |  |  |  |  |  |
| gc-held-002-mbpp | 2 |  |  |  |  |  |
| gc-held-002-mbpp | 3 |  |  |  |  |  |

Each cell: PASS / FAIL(test name). Grade a rep with:
`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q`

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **G-G1 run validity + extraction contract (6/6 reps):** <met / NOT met — list failing reps; unparseable = row FAIL, not INVALID; missing reps re-run in place>
- **G-G2 HumanEval regression floor (3/3 reps; solved ≥ baseline − 2):** <met / NOT met — name the lost rows>
- **G-G3 MBPP regression floor (3/3 reps; solved ≥ baseline − 2):** <met / NOT met — name the lost rows>
- **G-G4 sandbox + pin integrity (standing, pre-grade):** <green at grade time / BLOCKED — repair harness, then grade>

## VERDICT: PASS / NO-DEPLOY

<If NO-DEPLOY: the failing benchmark(s), the lost rows BY NAME, and the pre-registered
disposition (§3). The verdict is RELATIVE regression vs the frozen same-family base
baseline — never absolute capability (contamination residual pre-registered: these
benchmarks sit in base-model pretraining). A strong role-suite grade does not rescue
this verdict, and vice versa.>

## Non-gating diagnostics

| Metric | rep values | notes |
|---|---|---|
| Solved counts vs baseline (<baseline_solved>) |  | margin is −2 rows per benchmark per rep |
| Extraction failures (no-extractable-program) |  | row FAILs, contract still valid |
| Truncated generations (finish_reason=length) |  | distinct diagnostic, never conflated with execution failure |
| Rows lost on ALL 3 reps |  | stable forgetting signal — candidate re-training target |

## INVALID reps

<Any aborted rep (transport ABORTED.json, serving eviction) is re-run in place under the
same pinned config — never skipped, never graded partial. List re-run evidence here.>

## Notes

<Root-cause notes; anything that should become a new broken fixture
(tests/broken_fixtures/gc-held-*/ — floors never shrink).>
