# Feature Spec Summary: Idea-Mode Held-Out Eval Tasks

**Feature id (working):** FEAT-EVAL-IDEA (SPL build-plan gate G2)
**Stack**: python (stdlib + pytest only — frozen-suite design rule)
**Generated**: 2026-07-05
**Scenarios**: 31 total (4 smoke, 2 regression)
**Assumptions**: 9 total (1 high / 6 medium / 2 low confidence) — all human-confirmed in attended Phase 5, 2026-07-05
**Review required**: No

## Scope

Additive extension of the frozen PO held-out suite (`docs/research/ideas/po-heldout-suite-scope.md`, FROZEN 2026-07-03 — never edited by this feature) with two new doc-shaped eval tasks: `po-held-005-idea` (idea mode, thin-input hypothesis brief) and `po-held-006-scope` (scope mode, selection from a pinned reference roadmap). New deterministic grading axes: invented-requirement detection via an authored invention-anchor checklist (a specific asserted in requirement-bearing text must be licensed by a co-matching assumption or open question), assumption discipline (≥3 falsifiable-shape, confidence-tagged), selection-subset and dependency-closure gates for scope mode — alongside the carried-over serving-shape, schema, and grounding-emptiness axes. New tasks carry a distinct suite tag (`po-heldout-idea`) so the frozen §5 12-rollout verdict is untouched by construction; their own pre-registered verdict (G-I1…G-I4, gating SPL go-live) lives in a new addendum doc frozen before grading. Verifier-integrity discipline (§3.5) extends automatically: Oracle passes, every broken fixture fails exactly its owning test, good fixtures pass, battery floor never shrinks.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 6 |
| Boundary conditions (@boundary) | 7 |
| Negative cases (@negative) | 12 |
| Edge cases (@edge-case) | 11 |

(Categories overlap: 4 scenarios are both @negative and @edge-case — grader-evasion cases. 4 scenarios tagged @scope-task belong to the optional-but-included po-held-006.)

## Deferred Items

None. The optional po-held-006-scope was explicitly included (ASSUM-003).

## Open Assumptions (low confidence)

- ASSUM-002 — the authored idea brief's domain/content (physiotherapy self-service exercise programmes). Human-confirmed; revisit only if the domain collides with future training data.
- ASSUM-009 — anti-stuffing threshold (>2 anchor groups per statement licenses nothing). Human-confirmed; calibrate against the frontier baseline and stubbed sheets during build.

## Out of scope (explicit)

- Judgment-quality grading (idea *quality*, prioritisation taste, whether a scope selection truly "fits" the constraint) — Coach territory, per the frozen suite's one-suite-per-instrument rule.
- evolve/impact modes (no reference material; same reasoning as the frozen suite §3.2).
- Editing any frozen artefact: §5 thresholds, existing tasks, existing fixtures, existing grader behaviour.

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Idea-Mode Held-Out Eval Tasks" --context features/idea-mode-held-out-evals/idea-mode-held-out-evals_summary.md
