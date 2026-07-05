# Feature Spec Summary: PO Held-Out Idea-Mode Eval Tasks (FEAT-EVAL-IDEA)

**Stack**: python (plain pytest, stdlib-only graders — house rule of the frozen suite)
**Generated**: 2026-07-05T08:00:13+01:00
**Scenarios**: 24 total (7 smoke, 4 regression)
**Assumptions**: 10 total (0 high / 0 medium / 10 low confidence)
**Review required**: Yes — `--auto` mode; all assumptions unconfirmed

## Scope

Additive extension of the FROZEN po-heldout suite (po-heldout-suite-scope.md, frozen
2026-07-03) covering the two ungated PO modes the sovereign planning loop needs:
`po-held-005-idea` (thin-input idea mode — the mode behind James's Slack intake, SPL
gate G2) and `po-held-006-scope` (constraint-driven selection over an existing
roadmap). Grades deterministically: serving shape, ProductRoadmap schema, mode
pinning, no-corpus grounding/emptiness, assumption discipline (≥3 falsifiable
confidence-tagged assumptions on thin input), and the new **invented-requirement
gate** (trap-anchor mechanism, ASSUM-001) — idea mode's core failure. Scope mode adds
feature_id-allowlist + dependency-closure + constraint-carried gates. The frozen
suite, its §5 thresholds, and its 12-rollout run composition are untouched
(ASSUM-003/007). Judgment axes (assumption quality, prioritisation taste,
decomposition breadth) deliberately stay with the golden-set Coach gate — one suite
per instrument.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 4 |
| Boundary conditions (@boundary) | 6 |
| Negative cases (@negative) | 12 |
| Edge cases (@edge-case) | 5 |

(Some scenarios carry two categories, e.g. @boundary @negative just-outside pairs.)

## Deferred Items

None — no groups deferred (--auto accepted all groups; Phase 4 edge-case expansion
skipped per --auto).

## Open Assumptions (low confidence)

ASSUM-001 (invention-trap mechanism), ASSUM-002 (assumption floors 3/2),
ASSUM-003 (suite tag + --suite runner flag), ASSUM-004 (scope-mode emptiness),
ASSUM-005 (allowlist on feature_id only), ASSUM-006 (closure vs input graph),
ASSUM-007 (own pre-registered verdict G6/G7, Rich freezes),
ASSUM-008 (K=3 reps, frozen-suite conventions), ASSUM-009 (topic-disjoint,
client-content-free inputs), ASSUM-010 (deferral notes not gated).

## Deliverables (build plan input)

1. `tasks/po-held-005-idea/` — task.toml, instruction.md (runner assembly pinned to
   `player_idea.md`), `input/brief.md` (thin idea, deliberate traps), `test/` gates +
   `test/reference/invention_traps.json`, `solution/` authored Oracle + PROVENANCE.md.
2. `tasks/po-held-006-scope/` — same shape; `input/roadmap.json` (authored reference
   roadmap with dependency chains) + constraint; allowlist/closure/constraint gates.
3. `tests/broken_fixtures/po-held-00{5,6}-*/` — one per defect class incl. the
   deliberately-stubbed answer sheet; `tests/good_fixtures/` incl. the
   conservative-on-assumptions response and the literal-think-tag payload.
4. `harness/run_po_eval.py` — additive assembly branches for both tasks + `--suite`
   flag (default `po-heldout`; frozen run composition unchanged).
5. `tests/test_verifier_integrity.py` — additive trap-sanity check (anchors compile,
   invention gate demonstrated); existing discovery picks the tasks up automatically.
6. `docs/research/ideas/po-heldout-idea-extension-scope.md` — extension scope with
   proposed pre-registered verdict (G6/G7) for Rich to amend + freeze.

## Validation (from the SPL build plan, Session 1)

Verifier integrity green including new fixtures; a frontier-model answer sheet
passes; a deliberately-stubbed answer sheet fails.

## Integration with /feature-plan

    /feature-plan "PO Held-Out Idea-Mode Eval Tasks" \
      --context features/po-heldout-idea-mode-tasks/po-heldout-idea-mode-tasks_summary.md
