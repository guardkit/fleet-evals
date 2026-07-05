# Task: idea-mode discipline — HomeStretch idea (thin input, no corpus)

You are the product-owner agent in **idea mode**. The input is a 3-sentence idea
from `input/brief.md` — no documentation corpus, no knowledge graph. Explore the
idea's implications and propose a ProductRoadmap.

## Runner assembly (serving-faithful)

1. **System prompt:** the verbatim contents of
   `specialist-agent/roles/product-owner/prompts/player_idea.md`.
2. The idea text from `input/brief.md` as the user request. Project name: `homestretch`.

Save the model's raw output as `response.txt` in the rep's output directory.

## Output contract (what the tests grade)

- `<think>…</think>`, then **one** ```json-fenced `ProductRoadmap` object with
  `mode: "idea"`.
- **No corpus ⇒ emptiness is correct:** `coverage_score` must be `null`;
  `source_documents` empty at every level; no citations anywhere. Citing a document
  that was never provided is fabrication by construction.
- The brief deliberately leaves things unstated (platform, regulatory posture,
  integration depth, patient-data handling, clinician workflow). Those become
  **assumptions** — ≥3 of them, each falsifiable: `{id, category, statement,
  source, confidence: high|medium|low, impact_if_wrong}` — or open questions.
- **A specific the brief never stated must be surfaced, not silently asserted:**
  if a feature, constraint, or the priority rationale asserts such a specific, an
  assumption statement or open question must carry the same specific (the
  invented-requirement gate, extension scope §2.4). Do not silently invent a
  confident requirement.
- Feature descriptions ≥2 sentences; propose, never elicit.

Grade with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q`
