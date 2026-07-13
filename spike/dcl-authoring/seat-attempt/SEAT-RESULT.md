# Seat leg — ONE bounded qwen36-workhorse attempt (DCL SPIKE S4)

**Question this seeds (handoff §1, eval doc D-ii):** *can the local architect seat author
DCL at all?* Honest answer below — a failing attempt is a RESULT, not a problem.

## Setup (verbatim)

- **Seat:** `qwen36-workhorse` (the architect/product-owner alias), llama.cpp on
  llama-swap `:9000` — resolved read-only from `/opt/llama-swap/config/config.yaml`
  (model `qwen36-35b/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf`, `--reasoning auto`, `-np 1`).
- **Single-slot check before claiming:** `GET /9000/running` showed the model loaded and
  `ready`; no `autobuild`/`feature-build`/`task-work`/orchestrator process was running
  (CPU ~1.6% = idle). Seats were free — one bounded call taken, sequential, nothing else
  driven.
- **Prompt:** `instruction.md` verbatim as the user turn (it embeds the same /stats
  planning inputs S2 used + the repo README DCL syntax as few-shot) + a one-line system
  turn ("output ONLY DCL, no prose/fences"). `temperature 0.3`.

## Two attempts (both preserved, honest)

| | max_tokens | finish | content | verdict |
|---|---|---|---|---|
| `attempt-1-truncated/` | 4096 | `length` | **empty** — all 4096 tokens went to the reasoning channel, model never reached the answer | HARNESS UNDER-BUDGET (my error, not the seat's) — preserved, not graded |
| `response.dcl` (this dir) | 16384 | `stop` | 1327 chars of clean DCL | **GRADED — see below** |

The re-run raised only the token ceiling; the prompt and everything else were identical.
attempt-1 is kept because honesty requires recording it — the seat reasons a lot under
`--reasoning auto` (~5.5k completion tokens here, 21k chars of reasoning), so a realistic
budget matters when seating this model.

## Graded result (attempt-2) — FAIL, but a near miss

`python3 -m pytest test/ -q` with `DCL_EVAL_OUTPUT_DIR=seat-attempt/` → **1 failed, 4
passed**. The checker: `ok:false`, **errorCount 2**, exit 1.

- `test_candidate_exists` — PASS
- `test_candidate_structural_floor` — **PASS** (declared `capability GetStats` with an
  `intent`, an `outcomes` block, and a `lifecycle` — the shape is all there)
- `test_candidate_compiles_zero_errors` — **FAIL**, two semantic errors:
  1. `DCL_SEM_ACTOR_KIND_UNKNOWN` — `actor Client is machine` (line 3). DCL v1.0's actor
     kind vocabulary did not accept `machine`; the README used `is human`.
  2. `DCL_SEM_EFFECT_KIND_UNKNOWN` — `effect ReadProcessStats is in_memory` (line 5). DCL
     did not accept `in_memory` as an effect kind; the README used `persistence` /
     `notification`.
  (Plus 4 non-fatal `DCL_SEM_REDUNDANT_POLICY` warnings on the `governs` lines — the same
  warning the README example itself produces.)

**Reading it straight:** the local seat produced a genuinely well-formed DCL capability
on the first finished try — no prose, no markdown fences, all nine block types present,
sensible intent/outcome/event/policy/observe/when/lifecycle wiring that mirrors the
few-shot. It failed only by **inventing two kind-literals** (`machine`, `in_memory`) that
are outside DCL v1.0's closed vocabulary — exactly the class of mistake the compiler
exists to catch, and exactly what the compiler *did* catch, line-located. So: **the seat
can author DCL structurally, but not yet compiler-clean zero-shot from a README-level
few-shot** — the gap is the language's closed enum vocabulary (actor kinds, effect kinds),
which a fuller grammar/enum reference in the prompt, or a compile-repair loop, would very
plausibly close. This is a "near miss, fixable," not "can't do it" — a useful data point
for the D-ii / G3 fine-tune-or-not decision, and a real illustration that the compiler is
a working grader over an LLM's DCL.

## Files

- `response.dcl` — attempt-2 output, verbatim (the graded candidate)
- `raw-response.json` — full API response (attempt-2) incl. the reasoning channel
- `metadata.json` — model, endpoint, tokens, wall-time (99.9 s), finish reason
- `attempt-1-truncated/` — the under-budget first call, preserved unedited
