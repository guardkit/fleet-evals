# Task: greenfield discipline — RoundRoute brief (no corpus)

You are the product-owner agent in **greenfield mode**. There is **no documentation
corpus** — only the short brief in `input/brief.md`. Propose a product roadmap.

## Runner assembly (serving-faithful)

1. **System prompt:** the verbatim contents of
   `specialist-agent/roles/product-owner/prompts/player_greenfield.md`.
2. The brief text from `input/brief.md` as the user request. Project name: `roundroute`.

Save the model's raw output as `response.txt` in the rep's output directory.

## Output contract (what the tests grade)

- `<think>…</think>`, then **one** ```json-fenced `ProductRoadmap` object with
  `mode: "greenfield"`.
- **No corpus ⇒ emptiness is correct:** `coverage_score` must be `null`;
  `source_documents` empty at every level; no citations anywhere. Citing a document
  that was never provided is fabrication by construction.
- The brief deliberately leaves things unstated (fleet size, regulatory constraints,
  platform, integrations). Those become **assumptions** — ≥3 of them, each falsifiable:
  `{id, category, statement, source: "unstated", confidence: high|medium|low,
  impact_if_wrong}`. Do not silently invent a confident requirement.
- Feature descriptions ≥2 sentences; propose, never elicit.

Grade with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q`
