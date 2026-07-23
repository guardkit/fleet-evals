# RESULTS — QAV held-out deployment gate — qav-ft-v1 — 2026-07-23

**Candidate (tuned):** `qav-ft` = unsloth/gemma-4-26B-A4B-it MoE + 16-bit LoRA pilot tune
(adf `domains/qa-verifier/receipts/tune-train-2026-07-23.md`; 82-row post-exclusion train corpus,
63/63 steps, final train_loss 0.2539) → merged-16bit (Phase-5.2 merged-gen gate PASS 3/3 bare JSON)
→ GGUF **Q4_K_M** via the coach-ft-v3 pipeline (llama.cpp `convert_hf_to_gguf` bf16 →
`llama-quantize` Q4_K_M; never q4_0), served on llama-swap :9000.
GGUF sha256 `c5c9daaf51b51a85f48223bfa372d76fb6cfce961bb8f7f648da2da9b4207308`
(16,796,000,992 bytes, `/opt/llama-swap/models/qav-ft/qav-gemma4-26b-moe.Q4_K_M.gguf`).
Content-addressed chain: train raw sha `8bb5bce0e236eb2a…` (86) → staged seq-16384
`39bfe2b08a55e68c…` (82) → lora-adapter → merged-16bit → this GGUF → the `qav-ft` llama-swap entry.

**Baseline (stock):** `gemma4-26b` = the stock base already configured (unsloth gemma-4-26B-A4B-it
UD-Q4_K_XL, `/opt/llama-swap/models/gemma4-coach/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf`, ctx 32768,
`--reasoning auto`) — its exact served alias, untouched.

**Frozen thresholds:** qav-heldout-suite-scope.md §3, frozen at commit `2165802`. Frozen
`tasks/` / `docs/` / `harness/qav_gates.py` untouched; the only writes this run are `runs/` + this doc.

**Verifier integrity at grade time:** QAV-scoped `python3 -m pytest tests/test_qav_runner.py
tests/test_qav_verifier_integrity.py -q` → **49 passed, exit 0** (unmasked). Full
`pytest tests/ -q` → 353 passed, **8 failed + 17 errors, ALL confined to the gc code-gen sandbox
suite** (`test_gc_sandbox_integrity.py` / `test_gc_gates.py` / `test_gc_verifier_integrity.py` —
the sandbox isolation environment is absent on this host; zero QAV files involved). Recorded
honestly, not hidden: the QAV verifier surface graded green; the gc surface is a pre-existing
environmental gap unrelated to this exam.

**Contamination gate:** `python3 harness/qav_contamination_gate.py` → **PASS** (self-test 3/3:
clean PASS, both poisoned probes FAIL as designed; hold-out clean, B11's check recognizes these rows).

**Runner divergence (by design):** answer sheets by `harness/run_qav_heldout.py` (one fresh
toolless judgment per bundle per rep, fresh single-slot `/running` probe before every seat call),
NOT `run_po_eval.py`. Runner snapshot copied into each run dir per the divergent-copies convention
(`runs/qav-heldout/<candidate>-2026-07-23/run_qav_heldout.py`, sha256 `4d1d3292d665f9d3…` ==
`harness/run_qav_heldout.py` at fleet-evals HEAD `b8df1bb`).

**Sampling/config pins (both candidates, identical):** temperature 0.1 · top_p 0.9 ·
max_tokens 2048 · no grammar · pinned QAV seat system line (sha in each rep's `config.json`) ·
prompt = instruction.md verbatim + that bundle's bundle.json under the stable delimiter ·
`--freeze-commit 2165802` stamped per rep. Serving: `qav-ft` entry mirrors the coach-ft-v3 block
(same llama-server binary/flags shape: ctx 98304, q8 KV, flash-attn, `--jinja --reasoning off`,
temp 0.1/top-p 0.9, -np 1).

## Headline: per-task × per-rep × per-gate — TUNED vs STOCK

| Candidate | Task | Rep | G-Q1 contract | G-Q2 must-catch | G-Q3 catch-floor | G-Q4 false-block | verdict |
|---|---|---|---|---|---|---|---|
| **qav-ft** | qav-held-001-gold-negatives | 1 | PASS | FAIL(test_gold_negatives_all_caught) | — | — | FAIL |
| **qav-ft** | qav-held-001-gold-negatives | 2 | PASS | FAIL(test_gold_negatives_all_caught) | — | — | FAIL |
| **qav-ft** | qav-held-001-gold-negatives | 3 | PASS | FAIL(test_gold_negatives_all_caught) | — | — | FAIL |
| **qav-ft** | qav-held-002-honest-green | 1 | PASS | — | FAIL(test_catch_floor_holds) | **PASS** | FAIL |
| **qav-ft** | qav-held-002-honest-green | 2 | PASS | — | FAIL(test_catch_floor_holds) | **PASS** | FAIL |
| **qav-ft** | qav-held-002-honest-green | 3 | PASS | — | FAIL(test_catch_floor_holds) | **PASS** | FAIL |
| gemma4-26b | qav-held-001-gold-negatives | 1 | FAIL(test_verdict_contract) | FAIL(test_gold_negatives_all_caught) | — | — | FAIL |
| gemma4-26b | qav-held-001-gold-negatives | 2 | FAIL(test_verdict_contract) | FAIL(test_gold_negatives_all_caught) | — | — | FAIL |
| gemma4-26b | qav-held-001-gold-negatives | 3 | FAIL(test_verdict_contract) | FAIL(test_gold_negatives_all_caught) | — | — | FAIL |
| gemma4-26b | qav-held-002-honest-green | 1 | PASS | — | FAIL(test_catch_floor_holds) | **PASS** | FAIL |
| gemma4-26b | qav-held-002-honest-green | 2 | PASS | — | FAIL(test_catch_floor_holds) | **PASS** | FAIL |
| gemma4-26b | qav-held-002-honest-green | 3 | PASS | — | FAIL(test_catch_floor_holds) | **PASS** | FAIL |

Grades = separate unmasked pytest exits per rep (`grade.txt` + `grade-exit.txt` in every rep-task
dir — the tee/tail lesson honored).

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **G-Q1 contract shape (6/6 reps):** tuned **met 6/6**. Stock **NOT met 3/6** — all three
  qav-held-001 reps produced unloadable verdicts (reasoning ran to the max_tokens=2048 ceiling,
  `finish_reason=length`, no JSON object extractable: rep-1 GN-2/GN-3, rep-2 GN-1/GN-2/GN-3,
  rep-3 GN-2/GN-3 — 7 of 12 stock gold-negative generations truncated).
- **G-Q2 must-catch 100% (3/3 qav-held-001 reps):** **NOT met by either.**
  Tuned: **verdict-level 4/4 rejected in every rep (12/12, zero escapes)** but the owning DC class
  + signal-locus requirement failed — GN-2/GN-3/GN-4 own DC-03 (composition seam) and the tune
  attributed DC-05/DC-05/DC-12 (reps 1–2; rep-3 additionally swapped GN-1↔GN-2 classes); anchors
  unfired on GN-2 (reps 1–3) and GN-4 (rep 3). Stock: 7/12 gold negatives ESCAPED outright
  (unloadable ⇒ not a reject), and its parsed rejects carried the same GN-4 misattribution.
- **G-Q3 catch floor (3/3 qav-held-002 reps):** **NOT met by either**, with the same shape:
  RC-01 (the narrative false-green) was **rejected at verdict level by both candidates in all
  reps** but never with the owning class DC-14 (tuned said DC-03 ×3; stock said DC-05/DC-12/DC-12).
- **G-Q4 false-block ceiling (3/3 qav-held-002 reps):** **met by BOTH** — zero honest/ugly greens
  blocked in any rep (HG-01, UG-01, UG-02 approved with empty findings, 9/9 per candidate).

## VERDICT: **NO-DEPLOY**

The frozen bar is not met: G-Q2 (4/4 with owning class + in-bundle locus; 3-of-4 is a FAIL) and
G-Q3 (DC-14 attribution on RC-01) fail on **class/locus attribution** for the tuned candidate, and
on **outright escapes + contract collapse** for stock. Pre-registered disposition: the checkpoint
stays a directory, not a seat — the `qav-ft` llama-swap entry remains a probe-set A/B entry only.

**What the tune demonstrably fixed vs stock (non-gating, but the A/B's point):** the serving
contract and the catch behavior. Tuned: 24/24 bundles bare-JSON parse, 0 truncations, ~1s/bundle
(med 52 completion tokens); every gold negative and the narrative false-green rejected in every
rep; every honest green approved. Stock: 7/24 truncated-unparseable (the "reasons past the token
ceiling, no verdict" failure the fine-tune exists to close), 9–46s/bundle (med 1132 tokens).
**The Phase-5.2 3-row approve-lean flag did NOT materialize on the frozen exam — the residual gap
is defect-class attribution (DC-03 seam evidence read as DC-05 wiring / DC-12), not approve-bias.**

## Non-gating diagnostics

| Metric | qav-ft (rep 1/2/3) | gemma4-26b (rep 1/2/3) | notes |
|---|---|---|---|
| Gold negatives rejected, verdict level (of 4) | 4 / 4 / 4 | 2 / 1 / 2 | stock's misses = truncated-unloadable |
| Gold negatives with owning class correct (of 4) | 1 / 1 / 0 | 1 / 0 / 1 | GN-1=DC-08 the only ever-correct; G-Q2 is class+locus, 4/4-or-fail |
| RC-01 caught (catch floor, verdict level) | yes ×3 | yes ×3 | both misattribute the DC-14 class |
| Ugly greens approved (of 2: UG-01, UG-02) | 2 / 2 / 2 | 2 / 2 / 2 | zero false blocks anywhere |
| Truncated generations (of 8 bundles/rep) | 0 / 0 / 0 | 2 / 3 / 2 | all stock truncations on qav-held-001 |
| Wall/bundle (min/med/max, s) | 0.45 / 1.03 / 1.41 | 9.09 / 25.47 / 46.63 | tuned emits the trained short verdict |

## Honest caps (in-doc, per the pilot's own receipts)

1. **82-row pilot tier.** The train corpus is 82 rows (41 approve / 41 reject) — pilot scale by
   the plateau card's own admission (ceiling ≈133 measured vs the 250 floor). The exam grades
   honestly either way; this is a pilot probe, not a capacity claim.
2. **The 5 named seq-16384 exclusions, 4 of them rejects:** train `qav-5a7c0da775c6938c`
   (66,327 tok, reject DC-03), `qav-6394acf8aa44a442` (57,231, reject DC-05),
   `qav-e39d68e1ee550702` (52,748, reject DC-08), `qav-a1b64a41566b1fc9` (16,607, reject DC-03),
   eval `qav-0327647b6abc2d6a` (51,978, approve). The 4 longest reject bundles — including 2
   DC-03 rows, the exact class the exam's attribution failures concentrate on — were never seen
   by the tune; DC-05 train support is 2 rows. Excluded-never-truncated, recorded not hidden.
3. **The merged-gen approve-lean flag** (Phase-5.2: 2 of 3 held-out rejects approved on the 3-row
   peek) was carried loudly into this A/B; the frozen exam answered it — 12/12 gold-negative
   rejects, 0 false greens escaped at verdict level. The flag is resolved as a non-event for
   catch behavior; the real gap is class attribution.
4. **Probe, not adoption (R3-02).** This run closes another train→grade→gate arc only. The
   `qav-ft` entry is a probe-set llama-swap entry; seat adoption/promotion is a separate
   fleet-evals-gated decision that is Rich's, and a NO-DEPLOY verdict here makes it moot.

## INVALID reps

**None.** All 12 rep-task runs (2 candidates × 2 tasks × 3 reps) completed exit 0 on the first
attempt — no ABORTED.json anywhere, no re-runs required, no rep skipped.

## Serving receipts + rollback

- Config backup: `/opt/llama-swap/config/config.yaml.bak-20260723-095724-pre-qav-ft` (dated .bak
  before the edit, per Rich's standing grant).
- Added: the `qav-ft` model block (coach-ft-v3 mirror), matrix var `qft: qav-ft`, and the exam set
  `qav_exam: "qft & g26 & pk & qt"` — both candidates co-resident (~17+16+5 GB), verified: no
  mid-exam swapping (matrix solve `set=qav_exam … target=[gemma4-26b … qav-ft …]`, both `ready`
  in `/running` throughout).
- Smokes after `systemctl --user restart llama-swap.service`: `/v1/models` lists both aliases;
  1-token completions HTTP 200 for `qav-ft` and `gemma4-26b`.
- **The `qav_exam` set + `qav-ft` entry are left in place** for follow-up probes. Rollback = the
  .bak above (or delete the block + `qft` var + `qav_exam` line).
- Keepalive stayed flock-held (PID 1185504) for the whole window; the s2s audio pair untouched
  and ready throughout. Final `/running` at close: qav-ft ready, gemma4-26b ready,
  parakeet-tdt-0.6b-v3 ready, qwen3-tts-0.6b ready.

## Notes (root cause, and what would move the needle)

- The tune's failures are **one axis: defect-class/locus attribution**, concentrated on DC-03
  (composition seam) — every GN it "missed" was in fact rejected, with plausible-but-wrong wiring
  classes (DC-05/DC-12) and loci that para-phrase rather than name the anchored in-bundle signal.
  Train support: DC-03 has 25 rows but the 2 longest/richest DC-03 reject exemplars sat above the
  seq gate; DC-05:2 / DC-08:7 / DC-14:0-in-name (RC-01's class) — the attribution head is
  under-taught exactly where the exam probes it. A corpus that grows reject-side class diversity
  (the plateau card's "new mechanism class") is the indicated cure, not more epochs on 82 rows.
- Stock's qav-held-001 collapse is the documented base failure mode (reasons past the ceiling,
  no verdict) — the tune eliminates it completely, which is the strongest evidence the serving
  contract took.
- Candidate-under-test comparability caveat: quants differ (tuned Q4_K_M vs stock UD-Q4_K_XL) and
  stock runs `--reasoning auto` per its production entry — both are the estate's real serving
  postures, so this is an honest deploy-shaped A/B, not a controlled ablation.
