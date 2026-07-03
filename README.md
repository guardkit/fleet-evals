# fleet-evals

Standing evaluation substrate for the fleet (home confirmed in
`../fleet-memory/docs/research/ideas/phase-ablation-build-plan.md`). Eval tasks follow
the phase-ablation §3.2 task-folder contract:
`tasks/<id>/{task.toml, instruction.md, environment|input/, test/, solution/}`.

## PO held-out suite (first resident)

Pre-registered deployment gate for the incoming product-owner fine-tune (po-ft-v1).
**Scope + pre-registered thresholds** (freeze = Rich's commit landing the scope):
`docs/research/ideas/po-heldout-suite-scope.md`.
Doc-shaped tasks (no Docker): the model writes a `response.txt`, pytest grades schema
validity, citation grounding, and coverage-vs-reference (the FinProxy manual build
plan). Stdlib + pytest only.

| Task | Grades |
|---|---|
| `tasks/po-held-001-extract-phase-a` | EpicPlan stubs: leak-free, grounded, covers the reference BCs |
| `tasks/po-held-002-extract-phase-b` | EnrichmentBatch delta: allowlist, completeness, enums, grounding |
| `tasks/po-held-003-extract-full` | Full ProductRoadmap: schema battery, grounding, coverage, floors |
| `tasks/po-held-004-greenfield-discipline` | No-corpus discipline: null coverage, empty sources, assumptions |

**Private assets (required):** the client-derived payloads (FinProxy corpus copies,
April-derived oracles/fixtures, coverage checklists) are NOT in this repo — they live
in the FinProxy org (`lpa-project-docs` repo, `eval-assets/po-heldout/`) and are
symlinked in, pinned by `harness/ASSETS.sha256`. One-time setup after cloning both:

```bash
python3 harness/link_assets.py     # link + SHA-verify (or set PO_EVAL_ASSETS_ROOT)
```

```bash
# Verifier integrity + Oracle gate (must be green before any grading):
python3 -m pytest tests/ -q

# Oracle-validate a single task (default output dir = its solution/):
python3 -m pytest tasks/po-held-001-extract-phase-a/test -q

# Grade a candidate rep:
PO_EVAL_OUTPUT_DIR=/path/to/rep python3 -m pytest tasks/po-held-001-extract-phase-a/test -q
```

`tests/broken_fixtures/` is the permanent false-green corpus (never shrinks): known-bad
outputs — including the real April 2026 fabricated-citation output — that must keep
failing their owning tests. Record graded runs with `RESULTS-po-heldout-TEMPLATE.md`.

GuardKit kanban state lives in `tasks/{backlog,in_progress,in_review,blocked,completed}`
alongside the eval task folders.
