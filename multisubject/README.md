# fleet-evals — the factory's judging estate

Pre-registered, blinded, n-way model evaluation. Seeded from study-tutor's
`scripts/eval/` base-vs-finetune harness (2026-05-18) and generalised so any
set of candidate models can be judged in any **venue** without editing code.

**Local-only repo (by rule).** No GitHub remote exists yet; creating one is
flagged to Rich. Commit locally, never push.

## What a venue is

A **venue** is a ruled evaluation context under `venues/<name>/`:
a committed `PROTOCOL.md` (the pre-registration: hypothesis, decision rule,
seeds, judges, n), a `candidates.yaml` (the n-way candidate list), and the
golden data. The harness **refuses to start any run for a venue without a
`PROTOCOL.md`, and refuses while the protocol's Status is DRAFT** — the
DRAFT → REGISTERED flip is Rich's gate tap. The 2026-05-18 eval had no
pre-registration and its decision rule was arguable after the fact; here that
is impossible by code. Ground rules:
`docs/decisions/ADR-EVAL-001-blinding-and-preregistration.md`.

## How to add a venue

1. `mkdir venues/<name>` and write `candidates.yaml`
   (see `venues/study-tutor-multisubject/candidates.yaml`).
2. Add golden data: `golden/<subject>.jsonl` items with
   `id, category, subject, prompt, expected_behaviours, red_flags`
   (and optionally `golden/multiturn/scenarios.jsonl`).
3. Copy `runbooks/templates/PROTOCOL-template.md` to
   `venues/<name>/PROTOCOL.md`, fill every section, get it BLESSED, and
   commit it **before** any generation.
4. Run the pipeline (below) with `--run-dir runs/YYYY-MM-DD-<name>-<slug>`.

## The pipeline

```bash
# 1. generate n-way responses (one llama-swap swap per candidate)
uv run python -m harness.generate.run_ab_eval \
  --venue venues/<name> --golden venues/<name>/golden/english.jsonl \
  --system-prompt <prompt.txt> --run-dir runs/<run>

# 2. deterministic (no-LLM) scoring
uv run python -m harness.score.deterministic --run-dir runs/<run>

# 3. blind judging — prepare, judge (session/human/API), resolve
uv run python -m harness.judge.prepare --run-dir runs/<run>
#    ...judge blind_pairs.jsonl -> raw_judgements.jsonl (committed BEFORE the key is applied)...
uv run python -m harness.judge.resolve --run-dir runs/<run>
#    or the API path (needs ANTHROPIC_API_KEY + `uv sync --extra api-judge`):
# uv run python -m harness.judge.pairwise_api --run-dir runs/<run>

# 4. aggregate into results-table.md
uv run python -m harness.aggregate --run-dir runs/<run>

# multi-turn track: harness.generate.run_multiturn_eval ->
#   harness.judge.multiturn_prepare -> harness.judge.multiturn_resolve
# criterion track (length-neutral): harness.score.criteria
```

Every stage writes its slice of `runs/<run>/MANIFEST.json` (seeds,
endpoints, model ids, GGUF sha256s, prompt SHAs, judge model, repo HEADs).
Rubrics are selected per item by its `subject` field from
`harness/rubrics/<subject>.md`; only `english.md` is production — the other
seven are `STATUS: DRAFT` stubs the judge refuses unless
`--allow-draft-rubrics` (dry runs only).

## Tests

```bash
uv sync && uv run pytest
```

Hermetic (no network, no model inference). The golden-master suite proves
the lifted resolve/aggregate/score stages reproduce the published 2026-05-18
tables from the original evidence fixtures (`tests/fixtures/2026-05-18/`),
modulo documented format differences (see below).

## Honest state: what exists vs what is planned

**Exists (this build):**

- `harness/` — all 10 scripts lifted from study-tutor `scripts/eval/`
  (HEAD `27bb0b5b`), with the five pinned changes applied: `--run-dir`
  rooting, n-way candidates, rubric-by-subject, per-run MANIFEST.json,
  PROTOCOL.md pre-registration gate.
- `harness/rubrics/` — English rubric verbatim from `judge_pairwise.py`;
  `_base.md` (shared dimensions); 7 DRAFT subject stubs.
- `venues/study-tutor-multisubject/golden/` — eight golden sets, 136 items
  total (english 24 = the 16 lifted items + 8 extensions; maths, french,
  spanish, history, biology, chemistry, physics 16 each), every item
  schema-validated, each set with an adversarial `<subject>.review.md`
  (all PASS) — **status DRAFT: pre-registration inputs awaiting Rich's
  gate tap** (see `golden/README.md`).
- `venues/study-tutor-multisubject/` — 3 multi-turn scenarios +
  `candidates.yaml`; the eight subject
  system prompts extracted byte-verbatim with a sha256 provenance manifest
  (`prompts/PROMPTS-PROVENANCE.md`); `probes-17/probes.jsonl` (the 17-prompt
  protocol as data — C1/C2 carry the pinned Chemistry-under-Biology-preset
  defect annotation; true informal rate 15/17); and `PROTOCOL.md` encoding
  all seven 2026-05-18 required fixes — **Status DRAFT, pending Rich's gate
  tap; the harness refuses DRAFT protocols, so no run can start.**
- `venues/study-tutor-bakeoff/` — Lane 7 n-way skeleton (refreshed Gemma 4
  fine-tune vs Qwen 3.6 fine-tune vs old fine-tune vs base): DRAFT
  PROTOCOL.md + placeholder-honest `candidates.yaml`.
- `tests/` — 2026-05-18 evidence as fixtures + golden-master tests +
  hermetic n-way pipeline tests (incl. DRAFT-protocol refusal).
- `runbooks/` — inherited RUNBOOK-CONVENTIONS (dgx-spark) and
  RESULTS-template (study-tutor); new PROTOCOL-template;
  `RUNBOOK-serve-candidates.md` (operator-only llama-swap seat registration,
  matrix-set/keepalive eviction discipline, the three scored-run blockers).
- `docs/` — ADR-EVAL-001 (blinding + pre-registration, Accepted);
  `docs/history/2026-05-18-base-vs-finetune.md` (the seed eval's RESULTS,
  imported verbatim with provenance).

**Planned (not yet built — do not pretend otherwise):**

- Real (non-DRAFT) rubrics for maths/french/spanish/history/biology/
  chemistry/physics — needs subject expertise, not invention.
- Golden-set n ruling: English now meets the 24–32 bar, but the seven other
  subjects are authored at 16 each while the DRAFT `PROTOCOL.md` data-status
  table still states a 24+ per-subject bar. Whether 16/subject suffices for
  registration, or 8+ more items per subject are required, is Rich's call at
  the gate tap — the PROTOCOL table must be reconciled either way before the
  DRAFT → REGISTERED flip.
- n-way (>2) judging in `pairwise_api.py` (currently refuses >2 candidates)
  — a build prerequisite for the bakeoff venue.
- Automated production of `criteria_judgements.jsonl` (2026-05-18 required
  fix #7) — the multisubject PROTOCOL requires it; the producer does not
  exist yet.
- `RUNBOOK-multisubject-eval.md` (the generalised execution runbook).
- **The first scored run** — attended, and blocked on three operator acts
  (stated plainly in `runbooks/RUNBOOK-serve-candidates.md`): (1) no
  gemma4-base seat/GGUF on this host; (2) the canonical system-prompt.txt
  survives only as the SHA-pinned `prompts/english.txt`; (3) served
  gemma4-tutor GGUF provenance UNVERIFIED — local sha256 `675424b0…3144`,
  and HF `RichWoollcott/studytutor-gcse-26b-moe` is safetensors+LoRA only
  (no GGUF comparator), so resolution is an operator act.

## Deliberate format differences vs the 2026-05-18 artefacts

Golden-master tests assert semantic equality with the published tables; the
following are the intentional deltas (all consequences of n-way
generalisation):

- `responses.jsonl` rows: `{"responses": {name: ...}}` instead of top-level
  `base`/`finetune` keys (legacy files still load; `base`/`finetune` are
  treated as candidate names). Rows are stamped with `subject` +
  `prompt_sha256`.
- `blind_key.json`: `{"candidates": [...], "positions": {id: {label:
  name}}}` instead of `base_position` (legacy keys still resolve).
- `judgements.jsonl` rows: `winner` is a candidate name; `scores: {name:
  {dims}}` instead of `base_scores`/`finetune_scores`.
- Results tables: column/row labels are raw candidate names (`base`,
  `finetune`) instead of "Base"/"Fine-tuned" prose; the single-turn table's
  preamble no longer hard-codes serving claims (Q4_K_M/llama.cpp) — those
  belong to PROTOCOL.md + MANIFEST.json; the Δ column appears only for
  exactly two candidates.
