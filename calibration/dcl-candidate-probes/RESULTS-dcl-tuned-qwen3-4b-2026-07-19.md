# RESULTS — DCL pilot tune A/B (dcl-tuned-qwen3-4b vs stock, frozen exam)

**Date:** 2026-07-19 · **Candidate:** `dcl-tuned-qwen3-4b` = `Qwen/Qwen3-4B-Instruct-2507`
(Apache-2.0) + QLoRA, trained per agentic-dataset-factory
`domains/dcl-capability-language/RUNBOOK-dcl-fine-tune.md` v1.2 on the 507-row verified
corpus (87 authors ×2 oversample + 420 repairs; targets staged bare/think-free per the v1.2
transforms). Served as Q4_K_M GGUF (~2.5 GB — laptop-runnable) via llama-swap.
**Suite:** frozen dcl-heldout (re-freeze `8a3b9d1`), tasks 001/002/003 author + 004 repair
× {zero-shot, §10 protocol (vocab-ref + ≤1 bounded repair)} × K=3 — same runner, same
grading, same reference rows as `COMPARISON-2026-07-19.md`.
**The bar (pilot handoff §6):** demolish stock protocol authoring 2/9 AND hold repair 3/3.

## The graded table

| Candidate (Q4 GGUF) | Zero-shot authoring | Zero-shot repair | Protocol authoring |
|---|---|---|---|
| qwen36-workhorse 35B (reference) | 0/9 | 3/3 | 9/9 |
| stock Qwen3-4B-Instruct-2507 | 0/9 | 3/3 | 2/9 (2/3 · 0/3 · 0/3) |
| **dcl-tuned-qwen3-4b (this run)** | 0/9 | **3/3** | **7/9 (3/3 · 3/3 · 1/3)** |

## Verdict: **BAR MET**

- **Protocol authoring 7/9 vs stock 2/9** — 3.5×, with clean 3/3 sweeps on
  `dcl-held-001-author-stats` (stock 2/3) and `dcl-held-002-author-version` (stock 0/3 —
  stock never passed it once). `dcl-held-003-author-uptime`, the hardest task (stock 0/3),
  lands 1/3.
- **Repair held 3/3** — the base's one stock strength survived the tune intact.
- **Zero-shot authoring 0/9, unchanged from stock.** Expected and honest: zero-shot exam
  briefs carry no vocabulary reference, while every training row embeds it (the row
  contract); the tune's operating mode is vocab-in-prompt — which is also the production
  chain's authoring shape. The gift's model card should document that usage.
- Not the 35B's 9/9 — a 4B on 507 rows was never going to be — but decisively past the bar.

## The three runs (what the pilot taught — all fixes committed to the runbook)

**v1 — `<tool_call>` spam (catches #1+#2).** Trained clean (eval loss 0.033) but served
deterministic `<tool_call>` spam. Bisection: merged-16bit spams under plain transformers,
base+adapter via peft spams identically, raw base healthy, and a "```dcl"-prefill continues
into perfect DCL — only the first-token distribution was corrupt. Root cause pair: Unsloth
silently replaces the tokenizer's template with the hybrid-THINKING Qwen3 template (catch #1 —
it injected empty `<think>` pairs into every author target, and it doesn't even run under
llama.cpp's minja), and `<think>`/`</think>` are near-untrained added tokens in the
non-thinking base (catch #2) — LoRA leaves `lm_head` frozen, so cross-entropy could not
separate them from the confusable `<tool_call>` row 10 ids away. Teacher-forced loss was
blind to all of it. Fixes: forced stock 2507 template + strip-think staging + trainer [G6]
(ADF `01416d5`).

**v2 — every author rep failed at the lexer (catch #3).** Graded 0/9 · 3/3 · 0/9, but ALL
author failures were the markdown fence itself reaching the compiler
(`DCL_LEX_UNEXPECTED_CHAR` at 1:1). The exam pins *"Output ONLY the DCL source... no
markdown fences"* and grades verbatim by design; 528/528 fenced targets taught the model to
re-fence even inside the §10 repair leg, wasting the bounded repair on phantom fence
diagnostics. Fence-stripped diagnostic of the v2 artifacts: zero-shot content 0/9 (6–14 real
errors), protocol content 3/9. Fix: targets staged as bare DCL source (ADF `fd805ef`).
**The general law both catches spell:** staged targets must byte-match what the serving
contract asks the model to emit.

**v3 — this graded run.** Bare think-free targets, stock template, train == the exam's
pinned serving contract. Train loss 0.014 / eval 0.0056; mandatory merged-model generation
gate (runbook v1.2) passed before any GGUF work.

## Run integrity note

The v3 chain was interrupted mid-run at ~09:44 by the estate's standing-default tutor set
preloading + live tutor traffic (the runner's single-slot discipline refused those reps
rather than grade on a contended GPU — correctly). The 10 affected reps (zero-shot repair
rep-3 + all 9 protocol reps) were re-run to completion in a quiet window (~10:19) with the
identical runner/flags; every rep independently re-verifies the freeze/refreeze pins and the
slot. Per-rep artifacts + grades sit beside this doc under
`dcl-tuned-qwen3-4b/{zero-shot,protocol}/`.

## Artifacts

- Per-rep artifacts + `grade.txt`/`grade-exit.txt`: `dcl-tuned-qwen3-4b/…` (this dir).
- Training: GB10 `~/fine-tuning/output/dcl-qwen3-4b-v3/` (lora-adapter · merged-16bit ·
  GGUF Q4_K_M); staging manifest `~/fine-tuning/data/dcl-staging-manifest.json`.
- Serving: `~/dcl-probe-models/qwen3-4b-tuned/DCL-Qwen3-4B-Instruct-2507-Q4_K_M.gguf`,
  llama-swap entry `dcl-tuned-qwen3-4b` (stock-template `--chat-template-file`
  belt-and-braces; config backup `.bak-20260719-pre-dcltuned`).
- v1/v2 training outputs retained on the box (`dcl-qwen3-4b/`, `dcl-qwen3-4b-v2/`) for the
  record; their probe artifacts were wiped as invalid (broken-serve garbage), receipts in
  the session log.

**Next (Rich's moments, per the pilot claim):** gift packaging — HF merged + GGUF + adapter
+ model card citing the case studies (Apache NOTICE retention), Ollama Modelfile;
publication surface + whether the synthetic corpus ships. DF-008 default holds: corpus
private, synthetic-only training slice.
