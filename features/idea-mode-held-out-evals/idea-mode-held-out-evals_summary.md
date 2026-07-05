# Feature Spec Summary: Idea-Mode Held-Out Eval Tasks

**Feature id (working):** FEAT-EVAL-IDEA (SPL build-plan gate G2)
**Stack**: python (stdlib + pytest only — frozen-suite design rule)
**Generated**: 2026-07-05 (merged same day — see fork note below)
**Scenarios**: 36 total (4 smoke, 2 regression)
**Assumptions**: 10 total (1 high / 7 medium / 2 low confidence) — all human-resolved (confirmed or explicitly overridden), attended sessions 2026-07-05
**Review required**: No

> **Fork note (2026-07-05):** a parallel session ran the same action with `--auto`
> (`features/po-heldout-idea-mode-tasks/`, commit `34ae77e`). Rich resolved the fork:
> this attended spec is canonical; the --auto spec's unique content was absorbed
> (constraint-carried gate, scope maximal/minimal selection boundaries, confidence-enum
> negative, anchor-instrument sanity, authored-reference-roadmap-with-chains) and the
> duplicate directory retired. History preserves the retired spec.

## Scope

Additive extension of the frozen PO held-out suite (`docs/research/ideas/po-heldout-suite-scope.md`, FROZEN 2026-07-03 — never edited by this feature) with two new doc-shaped eval tasks: `po-held-005-idea` (idea mode, thin-input hypothesis brief) and `po-held-006-scope` (scope mode, selection from an authored, dependency-chained, checksum-pinned reference roadmap). New deterministic grading axes: invented-requirement detection via an authored invention-anchor checklist (a specific asserted in requirement-bearing text must be licensed by a co-matching assumption or open question), assumption discipline (≥3 falsifiable-shape, confidence-tagged), and for scope mode selection-subset, dependency-closure, and constraint-carried gates — alongside the carried-over serving-shape, schema, and grounding-emptiness axes. New tasks carry a distinct suite tag (`po-heldout-idea`) so the frozen §5 12-rollout verdict is untouched by construction; their own pre-registered verdict (G-I1…G-I4, gating SPL go-live) lives in a new addendum doc frozen before grading. Verifier-integrity discipline (§3.5) extends automatically: Oracle passes, every broken fixture fails exactly its owning test, good fixtures pass, battery floor never shrinks.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 6 |
| Boundary conditions (@boundary) | 9 |
| Negative cases (@negative) | 14 |
| Edge cases (@edge-case) | 12 |

(Categories overlap: 4 scenarios are both @negative and @edge-case — grader-evasion cases. 7 scenarios tagged @scope-task belong to the optional-but-included po-held-006.)

## Deferred Items

None. The optional po-held-006-scope was explicitly included (ASSUM-003).

## Open Assumptions (low confidence)

- ASSUM-002 — the authored idea brief's domain/content (physiotherapy self-service exercise programmes). Human-confirmed; revisit only if the domain collides with future training data.
- ASSUM-009 — anti-stuffing threshold (>2 anchor groups per statement licenses nothing). Human-confirmed; calibrate against the frontier baseline and stubbed sheets during build.

## Out of scope (explicit)

- Judgment-quality grading (idea *quality*, prioritisation taste, whether a scope selection truly "fits" the constraint) — Coach territory, per the frozen suite's one-suite-per-instrument rule.
- Scope-mode deferred-feature documentation quality (why each deferral happened) — Coach territory; only the deterministic selection axes are gated.
- evolve/impact modes (no reference material; same reasoning as the frozen suite §3.2).
- Editing any frozen artefact: §5 thresholds, existing tasks, existing fixtures, existing grader behaviour.

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Idea-Mode Held-Out Eval Tasks" --context features/idea-mode-held-out-evals/idea-mode-held-out-evals_summary.md
