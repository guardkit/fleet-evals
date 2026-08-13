> Imported VERBATIM (below this note) from study-tutor `docs/runbooks/RESULTS-base-vs-finetune-tutor-eval-2026-05-18.md` at HEAD `5d2d849e55bbe69c047c965bae1b48c553ea8370` (imported 2026-08-07, source sha256 `eec282bf64ee3d20d5ad9088bddcabb9a53b5796e90690ee9afef5243c793b34`). This is the eval this estate was seeded from — its seven required fixes are encoded in `venues/study-tutor-multisubject/PROTOCOL.md`, and its full artefact set is mirrored as regression fixtures at `tests/fixtures/2026-05-18/`. Internal links (runbook, known-issues, evidence paths) resolve in the study-tutor repo, not here. Do not edit below this line.

# RESULTS: base-vs-finetune-tutor-eval (2026-05-18, first execution)

**Date:** 2026-05-18 (evening — first execution of this runbook, hackathon
submission day).
**Operator:** Claude Code (interactive session on the GB10, the house
runbook-execution pattern).
**Machine:** GB10 (`promaxgb10-41b1`) — single-host, all-local.
**Runbook executed:** [`RUNBOOK-base-vs-finetune-tutor-eval.md`](RUNBOOK-base-vs-finetune-tutor-eval.md)

## Participating-repo HEADs

| Repo | HEAD | Notes |
|---|---|---|
| `study-tutor` | `6e2c332` | Eval harness `scripts/eval/` added in this session (uncommitted at run time) |

Inference stack:

- `llama-server` (llama.cpp build at `~/llama.cpp/build/bin/`) on a single GB10 CUDA device (124 GB VRAM-equivalent unified memory), via the `llama-swap` user-mode service.
- Judge: the Claude Code session executing the runbook (blind, position-randomised). No external API used.

## Models compared

| Role | Identity | Serving |
|---|---|---|
| Base | `unsloth/gemma-4-26B-A4B-it` — Gemma 4 26B-A4B MoE | llama-swap `gemma4-base`, GGUF `gemma-4-26B-A4B-it-UD-Q4_K_M` |
| Fine-tune | `RichWoollcott/studytutor-gcse-26b-moe` (LoRA r16, Unsloth+TRL SFT) | llama-swap `gemma4-tutor`, GGUF `…Q4_K_M` |

Parity held: identical 804-byte tutor system prompt, identical greedy decoding
(`temperature 0`, `max_tokens 2048`), the **same `llama-server` binary and
`gemma4-tutor.jinja` chat template** for both. The only deliberate variable is
the model weights.

## Headline result

**Both evaluations favour the base model.** Fine-tuning did not produce a
tutor that out-scores the stock `gemma-4-26B-A4B-it` instruction model under
the same tutoring system prompt.

| Evaluation | Base | Fine-tune | Tie |
|---|---|---|---|
| Single-turn (16 golden-set prompts) | **15** | 1 | 0 |
| Multi-turn (3 scripted sessions, holistic) | **2** | 0 | 1 |

### Single-turn dimension means (1–5)

| Dimension | Base | Fine-tune | Δ (ft − base) |
|---|---|---|---|
| Socratic stance | 4.31 | 4.25 | −0.06 (≈ tied) |
| AQA alignment | 3.50 | 2.06 | −1.44 |
| Scaffolding | 4.62 | 3.38 | −1.25 |
| Subject accuracy | 4.81 | 4.00 | −0.81 |
| Tone | 4.62 | 4.06 | −0.56 |
| Reasoning visibility | 1.44 | 2.88 | **+1.44** |

### Multi-turn dimension means (1–5)

| Dimension | Base | Fine-tune | Δ (ft − base) |
|---|---|---|---|
| Socratic stance | 4.00 | 5.00 | **+1.00** |
| AQA alignment | 4.67 | 3.00 | −1.67 |
| Scaffolding | 5.00 | 3.67 | −1.33 |
| Subject accuracy | 5.00 | 4.33 | −0.67 |
| Tone | 5.00 | 4.00 | −1.00 |
| Reasoning visibility | 1.33 | 3.33 | **+2.00** |

Deterministic (single-turn): fine-tune emits an inline `<think>` block on
62.5% of prompts (base 0%); **zero template-token leaks either model**;
fine-tune visible answers average 95 words vs the base's 212.

### Criterion-referenced re-score (length-neutral)

The pairwise judge favours longer, more thorough-*looking* answers — a known
LLM-judge bias. To remove it, every response was re-scored *only* against its
own item's `expected_behaviours` (met / partial / not) and `red_flags`
(tripped) — no model-vs-model comparison, so verbosity cannot inflate a score.

| Metric | Base | Fine-tune |
|---|---|---|
| Expected behaviours met | **88.5%** | **62.5%** |
| Red flags tripped | 0 / 45 | 1 / 45 |
| Clean items (all behaviours, no red flag) | 9 / 16 | 2 / 16 |

The length-neutral instrument **does not close the gap** — so the result is not
a length-bias artefact. But it locates the difference precisely: the fine-tune
scores *equal to or above* the base on pure-Socratic items (`essay-feedback-01`
1.00=1.00, `quote-analysis-01` 1.00=1.00, `quote-analysis-02` 0.83 > 0.67). It
loses points specifically where it (a) makes a factual slip, (b) **deflects
with a question when the student asked a direct question** (`exam-technique-01`
0.17, `exam-technique-02` 0.33 — a student asking "what does AO2 mean?" gets
questions back, not an explanation), or (c) drifts role / omits a concrete next
step. Those are real, specific, fixable weaknesses — not verbosity scoring.

## Interpretation — honest reading

**What the fine-tune genuinely does better.** It is the more reliably
*Socratic* tutor — tied single-turn, and clearly ahead multi-turn (+1.00),
the setting it was trained for. It surfaces pedagogical `<think>` reasoning
the base never produces (`reasoning_visibility` +1.44 / +2.00). Those trained
behaviours are real and held up.

**Why the base scores higher overall.** The base `-it` model is a very strong
instruction-follower; given an 804-byte tutoring system prompt it produces
long, well-structured, AQA/AO-explicit, accurate single-shot tutoring. The
fine-tune produces short conversational turns (~95 words) and keeps most of
its AO awareness inside the hidden `<think>` block — so the *visible* answer a
student reads carries less explicit scaffolding.

**Methodological caveats (logged, not excuses).**
1. The fine-tune is trained on multi-turn Player–Coach dialogue; short turns
   are by design. The multi-turn eval was added specifically to test on its
   home ground — it narrowed the gap (one genuine tie; Socratic +1.00) but did
   not reverse it.
2. The base was served with the fine-tune's `gemma4-tutor.jinja` template
   because its own embedded template leaks `<|channel>` tokens that
   `llama-server` then 500s on (see Execution notes). This means base and
   fine-tune differ only in weights — tighter parity — but the base ran in a
   well-configured setup.
3. Single judge (this session), 16 + 3 items — a *directional* result, not a
   statistically significant one.

**Fine-tune issues surfaced** (now in [`known-issues.md`](known-issues.md)):
a confirmed factual error (date of *An Inspector Calls*), a misnamed poem
("Nuit's Last Duchess"), a character-name slip ("Birley"), and one role-drift.

## Decision-gate outcome

Per the runbook's §7.2 matrix this is the **"base wins → stop and re-check"**
branch. Re-checks done: parity confirmed (same prompt/template/decoding/quant
family); `responses.jsonl` inspected — the base output is genuine, well-formed
tutoring, not degenerate text inflating the score. The result is judged
**real and directional**: under a single tutoring system prompt, the base
model is the stronger tutor on these tasks.

**Consequence for the submission:** the evaluation section of
`technical-writeup.md` (§11) must NOT claim "fine-tuning beat the base." The
honest, defensible options were put to the project owner — see the runbook
§7 and the session hand-off.

## Execution notes (2026-05-18)

1. **Base model registered in llama-swap, not Ollama.** Ollama was not
   usable from the runbook session; the base GGUF
   (`unsloth/gemma-4-26B-A4B-it-GGUF`, `UD-Q4_K_M`, ~16 GB) was downloaded to
   `/opt/llama-swap/models/gemma4-base/` and added as a `gemma4-base` model
   block.
2. **`<|channel>` leak / HTTP 500.** Served with its own embedded template,
   the base 500s on some prompts — `llama-server` fails to parse `<|channel>`
   tokens the model emits. Fixed by serving the base with the same
   `--chat-template-file gemma4-tutor.jinja` as the fine-tune.
3. **Generation batched by model.** `run_ab_eval.py` runs all base calls then
   all fine-tune calls (one model swap, not 32) after per-item swapping caused
   cold-swap 500s.
4. **Judge.** Performed by the Claude Code session via the
   blinding→judging→resolution split (`judge_prepare.py` → `raw_judgements` →
   `judge_resolve.py`); the base/fine-tune key was not consulted until raw
   verdicts were committed.

## Artefacts

All under `docs/runbooks/evidence/base-vs-finetune-eval/`:
`responses.jsonl`, `deterministic.json`, `blind_pairs.jsonl`, `blind_key.json`,
`raw_judgements.jsonl`, `judgements.jsonl`, `results-table.md`,
`multiturn_transcripts.jsonl`, `multiturn_blind.jsonl`, `multiturn_key.json`,
`multiturn_raw_judgements.jsonl`, `multiturn_judgements.jsonl`,
`multiturn_results-table.md`.

*Companion files: none (first execution of this runbook).*
