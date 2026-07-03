# Task: extract / Phase A (roadmap) — FinProxy research corpus

You are the product-owner agent in **extract mode, Phase A (roadmap)** of the phased
extraction flow. Read the full product documentation corpus once, group capabilities
into epics, and emit **minimal feature stubs** — the machine-readable `EpicPlan`
handoff to Phase B.

## Runner assembly (serving-faithful)

Build the model input exactly as the serving path does:

1. **System prompt:** the verbatim contents of
   `specialist-agent/roles/product-owner/prompts/player_extract_roadmap.md`
   (the deployed Phase A serving prompt — provenance pinned in `task.toml`).
2. **`## Product Documentation`** section: every file in `input/corpus/` (excluding
   `MANIFEST.sha256`), each rendered as a `## File: <filename>` block containing the
   file's full text.
3. **`## Phase`** block containing `roadmap`. Project name: `research`.

Save the model's raw output (think block included, nothing stripped) as `response.txt`
in the rep's output directory.

## Output contract (what the tests grade)

- `<think>…</think>` reasoning block, then **one** ```json-fenced `EpicPlan` object.
- Stubs carry **only** `feature_id`, `title`, `intent` (one line, ≤100 chars),
  `source_citations` — any enrichment field on a stub is an ENRICHMENT_LEAK.
- Every epic lists non-empty `cited_docs` (the files Phase B must read).
- Every filename cited anywhere must appear **verbatim** as a `## File:` header in the
  provided corpus. Do not invent, pluralise, respell, or reroot filenames.
- Citations: `section_path` ≥1 heading, quotes ≤200 chars.

Grade with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q`
