# PROTOCOL: study-tutor-bakeoff (Lane 7 n-way tutor bake-off — which candidate model family and training state should serve the tutor next?)

> Pre-registration document per `runbooks/templates/PROTOCOL-template.md`.
> This is the n-way SKELETON for the Lane 7 bake-off: the structure is fixed,
> the blanks marked `TBD` are filled at registration time. The harness
> refuses runs while Status is DRAFT (`harness/common.py::require_protocol`).

**Status:** DRAFT — SKELETON (blanks TBD; registration is Rich's gate tap)
**Registered:** —
**Venue:** `venues/study-tutor-bakeoff/`

## Hypothesis

A refreshed fine-tune (Gemma 4 or Qwen 3.6 family) out-tutors both the old
2026-05 fine-tune and the base model on the golden tracks, under identical
system prompts — i.e. the 2026-05-18 "base wins" verdict is reversible by
better training, not only by better prompting. TBD: sharpen into per-pair
falsifiable claims at registration.

## Candidates (n-way, 4 seats)

`candidates.yaml`:

| Name | What it is | Host status |
|---|---|---|
| `gemma4-refresh` | Refreshed Gemma 4 fine-tune (Lane 7 output) | NOT TRAINED YET — placeholder seat |
| `qwen36-tutor` | Qwen 3.6 fine-tune (Lane 7 output; base family = `workhorse` Qwen3.6-35B-A3B) | NOT TRAINED YET — placeholder seat |
| `gemma4-tutor` | The old (2026-05) fine-tune, currently serving | ON HOST; provenance UNVERIFIED (see candidates.yaml — resolution required) |
| `gemma4-base` | Stock `gemma-4-26B-A4B-it` | NOT ON HOST — seat registration is an operator act |

All four via llama-swap `http://localhost:9000/v1`. Every seat needs a
provenance-resolved `gguf_sha256` in `candidates.yaml` before registration —
no checksum, no run. Serving procedure + eviction discipline:
`runbooks/RUNBOOK-serve-candidates.md` (note: a 4-candidate run makes the
matrix-set/keepalive thrash risk worse than the two-way case — all eval seats
in one matrix set, or keepalive paused via the documented flock).

## Parity rule

Identical per-subject system prompts by pinned sha256
(`../study-tutor-multisubject/prompts/` + `PROMPTS-PROVENANCE.md`); greedy
decoding (`temperature 0`, fixed `max_tokens`); same `llama-server` binary
via llama-swap; ~4-bit K-M quants for all four (TBD: record the exact quant
per seat — cross-family quant equivalence is an honest caveat, not an
assumption). Chat templates are per-family as-served; template-token leaks
are MEASURED per family (`harness.score.deterministic` per-model-family leak
list — Qwen vs Gemma control tokens), not papered over.

## Data

TBD at registration: which golden tracks from the multisubject venue are in
scope, at the 24+ per-subject bar (fix #1). Skeleton default: single-turn
English golden (24+) + 3 multi-turn scenarios, extending per subject as their
golden sets and rubrics become real.

## Judging

n-way structure (the harness is n-way end-to-end; `pairwise_api` currently
refuses >2 candidates — closing that is a build prerequisite for this venue):

- API-path judge(s), never the executing session alone (fix #3). TBD judge
  model id(s).
- ≥ 2 judges or seeds, agreement reported (fix #2). TBD seeds.
- Per-subject rubrics; DRAFT rubrics barred from scored runs (fix #4).
- Mandatory human spot-check, ≥ 3–4 full items per subject (blind, pre-key).
- Length-neutral criterion track with automated `criteria_judgements.jsonl`
  production (fix #7).
- Blinding per ADR-EVAL-001: seeded n-way label shuffle, raw judgements
  committed before the key is applied.

## Decision rule (pre-registered — skeleton)

TBD numbers at registration; the SHAPE is fixed now:

| Outcome | Action |
|---|---|
| A refresh candidate wins ≥ TBD% of decided comparisons vs ALL of old-finetune and base, no red-flag regression, no leaks | That candidate becomes the serving tutor; ADR note records the switch. |
| Base or old fine-tune still wins | **No silent status quo (fix #5):** dated ADR note within a week — either serving follows the verdict or Rich signs the reason it doesn't. |
| Refresh candidates split by subject | Per-subject serving decision, recorded per subject in the ADR note. |
| Any leak_total > 0 | That candidate is disqualified from serving until the template is fixed and re-run. |

## Outputs

`runs/YYYY-MM-DD-study-tutor-bakeoff-<slug>/` — immutable, MANIFEST.json
(seeds, endpoints, model ids + quants, GGUF sha256s, prompt SHAs, judge
model(s), repo HEADs) + RESULTS write-up from
`runbooks/templates/RESULTS-template.md`.
