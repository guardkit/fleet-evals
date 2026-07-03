# Task: extract / Phase B (features) — EPIC-006 Open Banking and Consent Operations

You are the product-owner agent in **extract mode, Phase B (features)**. Phase A has
already produced `input/epic_plan.json`. Enrich **every feature stub of `EPIC-006`**
("Open Banking and Consent Operations") into a full feature spec, emitting an
`EnrichmentBatch` delta — the dispatcher merges it onto the Phase A stubs server-side.

## Runner assembly (serving-faithful)

1. **System prompt:** the verbatim contents of
   `specialist-agent/roles/product-owner/prompts/player_extract_features.md`.
2. **`## Epic Plan`** section: the contents of `input/epic_plan.json`.
3. **`## Product Documentation`** section: the documents named in EPIC-006's
   `cited_docs`, each rendered as a `## File: <filename>` block from `input/corpus/`.
   (The full corpus is in `input/corpus/`; Phase B reads only the cited docs.)
4. **`## Phase`** block containing `features`, epic scope `EPIC-006`.
   Project name: `research`.

Save the model's raw output as `response.txt` in the rep's output directory.

## Output contract (what the tests grade)

- `<think>…</think>`, then **one** ```json-fenced `EnrichmentBatch` object:
  `{project_name, epic_id: "EPIC-006", enrichments: [...]}`.
- Enrichments carry **no** `title` and **no** `bounded_context` — identity comes from
  the Phase A stub. `feature_id`s must come from EPIC-006's stub allowlist; every stub
  must receive an enrichment.
- Each enrichment: `description` ≥2 sentences; `source_documents` ≥1, filenames
  verbatim from the corpus; enum fields use the exact Literals
  (`priority`/`moscow`/`value`/`complexity`); evidence non-default fields in
  `field_citations`. At least one enrichment must populate ≥3 metadata fields
  (completeness gate).

Grade with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q`
