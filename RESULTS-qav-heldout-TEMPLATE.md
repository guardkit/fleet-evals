# RESULTS — QAV held-out deployment gate — <candidate-id> — <date>

**Candidate:** <QAV serving model id + quant + adapter, e.g. qav-ft-v1 = gemma-4-26b + QLoRA-<hash>, llama-swap :9000>
**Frozen thresholds:** qav-heldout-suite-scope.md §3, frozen at commit `<freeze-sha>`
**Verifier integrity at grade time:** `python3 -m pytest tests/ -q` → <N> passed (MUST be green before grading)
**Contamination gate:** `python3 harness/qav_contamination_gate.py` → PASS (MUST be green — the eval_qav hold-out is clean and B11's check recognizes these rows)
**Runner divergence (by design):** answer sheets are produced by the QA-verifier seat's harness (one fresh judgment per bundle per rep), NOT by `harness/run_po_eval.py`. Per-rep records pin: serving model id (qav-ft lineage) + quant + template + prompt/grammar version + the bundle SHAs.

## Per-task × per-rep

| Task | Rep | G-Q1 contract | G-Q2 must-catch | G-Q3 catch-floor | G-Q4 false-block | verdict |
|---|---|---|---|---|---|---|
| qav-held-001-gold-negatives | 1 |  |  | — | — |  |
| qav-held-001-gold-negatives | 2 |  |  | — | — |  |
| qav-held-001-gold-negatives | 3 |  |  | — | — |  |
| qav-held-002-honest-green | 1 |  | — |  |  |  |
| qav-held-002-honest-green | 2 |  | — |  |  |  |
| qav-held-002-honest-green | 3 |  | — |  |  |  |

Each cell: PASS / FAIL(test name). Grade a rep with:
`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q`

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **G-Q1 contract shape (6/6 reps):** <met / NOT met — list failing reps>
- **G-Q2 must-catch 100% (3/3 qav-held-001 reps; all 4 gold negatives rejected, owning class + signal locus — 3 of 4 is a FAIL):** <met / NOT met — name the escaped gold negative>
- **G-Q3 catch floor (3/3 qav-held-002 reps; the narrative false-green stays caught):** <met / NOT met>
- **G-Q4 false-block ceiling (3/3 qav-held-002 reps; zero honest/ugly greens blocked, N=3 per rep):** <met / NOT met — list wrongly-blocked greens>

## VERDICT: DEPLOY / NO-DEPLOY

<If NO-DEPLOY: the failing axis, and the pre-registered disposition (§3) it triggers. A strong training-loss curve does not rescue this verdict.>

## Non-gating diagnostics

| Metric | rep values | notes |
|---|---|---|
| Gold negatives caught (of 4) |  | G-Q2 is 4/4-or-fail |
| Ugly greens approved (of 2: UG-01, UG-02) |  | the false-block lever |
| Findings naming the exact in-bundle signal |  | anchor firing is the floor, not the ceiling |

## INVALID reps

<Any aborted/missing rep is re-run in place (never skipped); an incomplete run is INVALID, not a failure. List re-run evidence here.>

## Notes

<Root-cause notes for any failure; anything that should become a new broken fixture
(§5: every wild catch joins tests/broken_fixtures/, floors never shrink).>
