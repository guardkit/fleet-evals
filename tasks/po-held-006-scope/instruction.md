# Task: scope-mode selection discipline — RoundRoute roadmap under a 6-week constraint

You are the product-owner agent in **scope mode**. The input is an existing
ProductRoadmap (`input/reference_roadmap.json`) plus a delivery constraint
(`input/constraint.md`). Select what fits; never invent.

## Runner assembly (serving-faithful)

1. **System prompt:** the verbatim contents of
   `specialist-agent/roles/product-owner/prompts/player_scope.md`.
2. **User request:**

   ```
   ## Existing Roadmap

   <contents of input/reference_roadmap.json>

   ## Constraint

   <contents of input/constraint.md>
   ```

   Project name: `roundroute`.

Save the model's raw output as `response.txt` in the rep's output directory.

## Output contract (what the tests grade)

- `<think>…</think>`, then **one** ```json-fenced `ProductRoadmap` object with
  `mode: "scope"`.
- **Selection, never invention:** every feature in the output must exist in the
  reference roadmap. **Preserve `feature_id`, `title`, and `bounded_context`
  verbatim from the reference** — re-labelling a selected feature is treated as
  inventing one. Descriptions MAY be rewritten where the selection reduces a
  feature's scope (≥2 sentences).
- **Dependency closure:** if a selected feature depends on another feature in the
  reference roadmap, that prerequisite must be selected too. Emptying `depends_on`
  does not lift this — closure is checked against the reference roadmap's graph.
- **Carry the constraint:** the stated delivery constraint (the 6-week window, the
  2-engineer capacity, the MVP-first pilot cut) must appear in
  `constraints_and_dependencies`.
- No document corpus was provided: `coverage_score` must be `null` and
  `source_documents`/citations empty at every level.
- Deferred features are listed in prose (`priority_rationale`), not deleted from
  the reference — deferral documentation quality is reviewed by the Coach, not
  gated here.
- Document your constraint interpretation as assumptions (falsifiable shape).

Grade with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q`
