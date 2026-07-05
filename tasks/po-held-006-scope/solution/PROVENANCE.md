# Oracle provenance — po-held-006-scope

Authored 2026-07-05 (Claude Fable, attended FEAT-EVAL-IDEA build session,
TASK-EVI-004) as a defensible 6-week MVP selection over the authored reference
roadmap. Not model output from the runner; the frontier baseline good fixture
(TASK-EVI-005) is the serving-faithful frontier sheet.

Design notes:

- Selection {FEAT-PO-001, FEAT-PO-002, FEAT-PO-004, FEAT-PO-008} is
  dependency-closed against the reference graph (001 → 002 → 004 → 008).
- Reference `feature_id`/`title`/`bounded_context` preserved verbatim
  (subset gate with content pinning); descriptions rewritten where the pilot
  narrows scope — the serving-licensed rewrite path the gate deliberately
  leaves free.
- Constraint carried in `constraints_and_dependencies` matching all three
  anchor groups (timebox / team / mvp).
- Deferrals documented in `priority_rationale` prose — deferral quality is
  Coach territory, not gated (extension scope out-of-scope list).
- Grounding empty, `coverage_score` null (the reference roadmap is selection
  input, not a corpus).

Repairs: none — authored to pass; first grading run recorded in the extension
scope doc's baseline table (TASK-EVI-008).
