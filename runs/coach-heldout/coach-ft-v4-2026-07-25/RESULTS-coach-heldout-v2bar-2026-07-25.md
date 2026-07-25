# Coach held-out — coach-ft-v4 vs the FROZEN v2 bar · 2026-07-25
## VERDICT: **CLEAR PASS — 6/6 reps green on the v2 batteries.** The leads-analogue bar
## (judgment perfect + locus clean + honest greens approved) is met. Reseat earned.

## Candidate lineage (pins)

- Base: `unsloth/gemma-4-26B-A4B-it`, the SIGNED updated "Gemma 4 Fixes" release
  (HF `refs/main` = `60941ad6`, lastModified 2026-07-17).
- Corpus: adf `domains/coach-agent/v4_sft_raw.jsonl` (174 rows, 94 approve / 80 reject;
  regenerated in the reconciled v4 contract `{verdict, findings:[{locus}]}` RAW UNFENCED,
  locus derived from labelled bundle anchors + verbatim-grounding gates; adversarial audit
  `wf_6c936265-877`; build adf `489027b`).
- Train: QLoRA r=16 (1.88% trainable), `gemma-4-thinking` template, `train_on_responses_only`,
  seq 4096 (REAL-tokenizer max 4076 → zero truncation), 3 epochs / 132 steps, final
  train_loss 0.042, 44 min on the GB10. [G2] trained response span = pure JSON (no thought
  block) — THE CATCH resolved train-side.
- Export: merged-16bit → **Q8_0 GGUF** (the signed serving pick),
  sha256 `4fcbba950e3a269e95b7aff58874e3d3ad7b1d82844f69da404e914d3504ea1d`.
- Serving: **pinned llama.cpp `720d7fa` (2026-07-25 master — the July Gemma-4 fix PRs)**;
  the live `llama.cpp-new` build (2026-05-30) predates those fixes and was NOT used.
- Exam serving posture: direct pinned `llama-server`, `--jinja`, thinking disabled, temp 0.0.

## Pre-exam gates (both MANDATORY, both PASS)

| gate | result |
|---|---|
| merged-gen gate (12 sampled rows, strict raw contract) | **PASS 12/12 contract-clean, mode=raw (no think-strip), verdict agree 12/12** |
| **THE SERVE GATE** (8 rows over the wire vs the Q8_0 seat — the check coach-ft-v3 skipped) | **PASS 8/8 contract-clean, mode=raw, agree 8/8** — production parser needs NO strip rule |

## Per-task × per-rep (v2 batteries = the frozen bar; graded
## `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task>/test -q -k v2`)

| Task | Rep | v2 result | v1 (informational) |
|---|---|---|---|
| coach-held-001-escape-kin | 1 | **PASS** (2 passed) | class-axis fail (de-scoped) |
| coach-held-001-escape-kin | 2 | **PASS** (2 passed) | class-axis fail (de-scoped) |
| coach-held-001-escape-kin | 3 | **PASS** (2 passed) | class-axis fail (de-scoped) |
| coach-held-002-catch-and-green | 1 | **PASS** (3 passed) | class-axis fail (de-scoped) |
| coach-held-002-catch-and-green | 2 | **PASS** (3 passed) | class-axis fail (de-scoped) |
| coach-held-002-catch-and-green | 3 | **PASS** (3 passed) | class-axis fail (de-scoped) |

All 24 rollouts (8 bundles × 3 reps) `parse_ok=True`, `finish=stop`, ~0.7–1.7 s/bundle.
G-C2 must-catch: every escape-kin (CE-01..04) REJECTED with a locus that anchor-matched the
seeded signal — **the exact axis coach-ft-v3 failed, now clean across all reps**. G-C3: both
catch-kin rejected, locus held. G-C4: both honest greens approved with `findings: []`.

The v1 informational failure is exactly `test_escape_kin_all_caught`'s owning-DC-class
requirement — the axis Rich de-scoped in the v2 freeze. The v2 non-gating class diagnostics
(rep-1: CE-01 want DC-08 got DC-14; CE-02/03/04 want DC-03 got DC-05) reproduce the known
finding across QAV + coach: class attribution is capacity/corpus-bound; judgment + locus are
not. Note the exam's frozen instruction still asks for `class`, so the model (trained with no
class field) volunteers a guess; v2 tolerates extra keys and does not gate it.

## The staged seat (reseat step 1 of 2)

`coach-ft-v4` is LIVE on llama-swap :9000 beside the untouched `gemma4-coach`
(config backup `config.yaml.bak-20260725-215152-pre-coach-ft-v4`; model
`/opt/llama-swap/models/coach-ft-v4/coach-ft-v4.Q8_0.gguf`, sha verified; pinned binary;
ctx 98304 + q8 KV mirroring the production coach envelope; temp 0). Staged-seat smoke:
one full bundle through the seat → **strict raw parse clean, correct reject + grounded locus**.

**The live coach-model flip is NOT done.** Production guardkit still prompts and parses the
old COACHSPLIT grammar (fenced `decision/issues`). The flip requires the guardkit
contract-mirror build (coach prompt assembly + parser move to the v4 raw contract, including
the vocabulary rewrites listed in adf `HANDOFF-coach-v4-corpus.md`) — a guardkit-venue build,
sequenced per the one-guardkit-build-at-a-time constraint. Until then `gemma4-coach` serves
production unchanged.

## GPU protocol receipts

Fleet-idle-first verified → keepalive flocked (detached holder) → `/unload` (109 GB headroom)
→ mem watchdog armed → smoke [G5] 61.2 GB peak → full train → gates → exam → seat smoke →
`/unload` → lock released by exact fd-holder PIDs (both — the inherited-child trap) →
keepalive timer confirmed re-warming the tutor set. Zero incidents.
