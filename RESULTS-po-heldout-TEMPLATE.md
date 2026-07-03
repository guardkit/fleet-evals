# RESULTS — PO held-out deployment gate — <candidate-id> — <date>

**Candidate:** <model id + quant + adapter, e.g. po-ft-v1 = gemma4-26b + QLoRA-<hash>>
**Frozen thresholds:** po-heldout-suite-scope.md §5, frozen at commit `<freeze-sha>`
**Verifier integrity at grade time:** `python3 -m pytest tests/ -q` → <N> passed (MUST be green before grading)
**Runner config per rep:** recorded in `<results-dir>/rep-*/config.json` (model, quant, temperature, template, endpoint, timestamp)

## Per-task × per-rep

| Task | Rep | shape | schema | grounding | coverage | floors | discipline | verdict |
|---|---|---|---|---|---|---|---|---|
| po-held-001-extract-phase-a | 1 |  |  |  |  |  | — |  |
| po-held-001-extract-phase-a | 2 |  |  |  |  |  | — |  |
| po-held-001-extract-phase-a | 3 |  |  |  |  |  | — |  |
| po-held-002-extract-phase-b | 1 |  |  |  | (all-stubs-enriched) | — |  |  |
| po-held-002-extract-phase-b | 2 |  |  |  | (all-stubs-enriched) | — |  |  |
| po-held-002-extract-phase-b | 3 |  |  |  | (all-stubs-enriched) | — |  |  |
| po-held-003-extract-full | 1 |  |  |  |  |  | — |  |
| po-held-003-extract-full | 2 |  |  |  |  |  | — |  |
| po-held-003-extract-full | 3 |  |  |  |  |  | — |  |
| po-held-004-greenfield-discipline | 1 |  |  | — | — | — |  |  |
| po-held-004-greenfield-discipline | 2 |  |  | — | — | — |  |  |
| po-held-004-greenfield-discipline | 3 |  |  | — | — | — |  |  |

Each cell: PASS / FAIL(test name). Grade a rep with:
`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q`

## §5 verdict (applied verbatim — no post-hoc adjustment)

- **G1 serving shape & schema (12/12; fence-aware think + first-JSON-object cascade + mode + schema):** <met / NOT met — list failing reps>
- **G2 grounding (zero fabricated refs, corpus tasks):** <met / NOT met — list fabrications>
- **G3 coverage ≥ baseline, ≥2/3 reps per corpus task + floors (≥5 epics / ≥18 features) + Phase-B all-stubs-enriched (≥2/3):** <met / NOT met>
- **G4 Phase-B discipline, 3/3 (epic_id, allowlist, batch-level completeness):** <met / NOT met>
- **G5 greenfield discipline, 3/3 (null coverage, zero sources, ≥3 assumptions all complete):** <met / NOT met>

## VERDICT: DEPLOY / NO-DEPLOY

<If NO-DEPLOY: the failing axis, and what Phase 3/4 work it names. Golden-set results do not rescue this verdict.>

## Non-gating diagnostics

| Metric | rep values | April baseline |
|---|---|---|
| Stretch coverage: identity-access |  | not covered |
| Stretch coverage: nats-messaging |  | not covered |
| Epic count (001 / 003) |  | 8 / 8 |
| Feature count (001 / 003) |  | 36 / 36 |
| Assumption count (004) |  | 4 (authored oracle) |

## Notes

<Root-cause notes for any failure; anything that should become a new broken fixture
(scope §6b: every wild catch joins tests/broken_fixtures/).>
