# Task: extract / single-pass (full) — FinProxy research corpus

You are the product-owner agent in **extract mode, single-pass** (`--phase=full`) —
the Decision-A serving shape. Read the full product documentation corpus and emit a
complete `ProductRoadmap`: epics with fully enriched features, flattened
`feature_spec_inputs`, constraints, open questions, assumptions and coverage.

## Runner assembly (serving-faithful)

1. **System prompt:** the verbatim contents of
   `specialist-agent/roles/product-owner/prompts/player_extract.md`
   (the deployed single-pass extract serving prompt).
2. **`## Product Documentation`** section: every file in `input/corpus/` (excluding
   `MANIFEST.sha256`), each rendered as a `## File: <filename>` block.
3. Project name: `research`.

Save the model's raw output as `response.txt` in the rep's output directory.

## Output contract (what the tests grade)

- `<think>…</think>`, then **one** ```json-fenced `ProductRoadmap` object with
  `mode: "extract"`.
- `feature_spec_inputs` is the flattened list of ALL epic features — identical
  objects, matching feature_ids.
- Feature descriptions ≥2 sentences, behavioural, domain language.
- Top-level `source_documents` are `{filename, contribution}` objects; epic/feature
  `source_documents` are plain filename strings — all verbatim from the corpus.
  **One misspelled or invented filename anywhere fails the gate.**
- Enum Literals exact (`priority`/`moscow`/`value`/`complexity`); assumptions carry
  `{id, category, statement, source, confidence: high|medium|low, impact_if_wrong}`.

Grade with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q`
