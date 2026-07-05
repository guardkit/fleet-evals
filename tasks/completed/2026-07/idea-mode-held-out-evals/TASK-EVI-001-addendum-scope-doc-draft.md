---
id: TASK-EVI-001
title: "Addendum scope doc (DRAFT): idea-gate verdict + pinned instrument contracts"
status: completed
task_type: documentation
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 1
implementation_mode: direct
complexity: 3
priority: high
dependencies: []
created: 2026-07-05T09:30:00Z
---

# TASK-EVI-001 — Addendum scope doc (DRAFT)

Create `docs/research/ideas/po-heldout-idea-extension-scope.md`, landing explicitly as
**DRAFT** (Rich freezes only after build validation — TASK-EVI-008 hands it over;
"pre-registered" means frozen before *grading*, not before build).

## Acceptance Criteria

- [ ] Pre-registered verdict gates G-I1..G-I4 per ASSUM-005 (amended wording: G-I2 =
      "zero ANCHOR-DETECTED unlicensed inventions" — detection floor; G-I4 = subset with
      title/bc pinning + closure vs REFERENCE graph + constraint-carried floor), gating
      SPL go-live (G2), never po-ft-v1 deploy
- [ ] INVALID-run semantics carried over verbatim from the frozen §5 validity gate
      (aborted/missing rep ⇒ INVALID, re-run, never skip; new-suite runs never reuse a
      frozen run's --out dir)
- [ ] Pinned instrument contracts (the TASK-EVI-002/003/004 integration contract):
      `invention_anchors.json` / `constraint_anchors.json` schema (group ids, alternates
      arrays), matcher diagnostic contract (structured findings that NAME the unlicensed
      detail / invented or content-swapped feature id — never a bare bool), central
      NFKC+casefold normalization rule, structural_units()-convention granularity,
      per-group firing+licensed fixture requirement, fixture-floor-list convention
- [ ] Recorded accepted residuals (Coach territory): paraphrase evasion outside the
      checklist, opposite-polarity licensing, keyword-echo constraint floor, homoglyphs
- [ ] Frontier-baseline section (both tasks, per Context B) + baseline table left empty
      for TASK-EVI-008 measurement; RESULTS template stub for the idea-gate run
- [ ] States the frozen doc/suite is never edited; documents gate-stricter-than-serving
      divergences (title/bc pinning) per the frozen suite's divergence pattern
- [ ] Status line reads DRAFT with the freeze hand-off procedure named

## Coach Validation

Doc exists at the path above; contains G-I1..G-I4, DRAFT status, anchors schema,
diagnostic contract, residuals section; `git diff` shows zero changes to
`docs/research/ideas/po-heldout-suite-scope.md`.
