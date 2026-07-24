# RESULTS — QAV held-out deployment gate — qav-ft-v3 — 2026-07-24 (the contrast-pair re-exam)

**Candidate (v3, fresh this run):** `qav-ft-v3` = unsloth/gemma-4-26B-A4B-it MoE + 16-bit LoRA
retrained on the **387-row contrast-pair corpus** (adf `contrast-pair-corpus-2026-07-24.md` @f48a921:
21 atomic class-boundary pairs + matched approve controls via the v1.2 populate-with-defect
doctrine; **eval holds every class for the first time** — DC-12 0→8, DC-14 1→5; staged seq-20480
331 train / 49 eval; 249/249 steps, train_loss 0.0789, **eval_loss 0.575→0.453→0.456** on the
class-complete eval) → merged-16bit (Phase-5.2 gate PASS 6/6 bare JSON on ALL-HELD-OUT
class-diverse probes — **the held-out DC-14 pair row and DC-12 pair row both REJECTED**, a first)
→ GGUF **Q4_K_M** via the same pipeline, sha256
`6db1f801b4054af35efb22befc7fefaa027b615d32f3ed9e3c4f60429afebf47` (16,796,000,992 bytes —
byte-identical size to v1/v2), served as `qav-ft-v3` (exact block mirror; `qav_exam` gained `qft3`).

**Comparison columns (banked):** `qav-ft-v2`/`qav-ft`/`gemma4-26b` cite their same-freeze
(`2165802`), same-runner (sha `4d1d3292…`), same-pins runs at `0fbee7e`/`e66a8be` — not re-run.
**Frozen thresholds:** qav-heldout-suite-scope.md §3 @`2165802`; frozen files untouched; the only
writes are `runs/qav-ft-v3-…/` + this doc. Verifier integrity + contamination gates: green at the
v2 sitting hours earlier, harness unchanged since (`git status` clean at exam time); runner
snapshot sha == harness HEAD.

## Headline: per-task × per-rep × per-gate — v3 vs v2 vs v1 vs STOCK

| Candidate | Task | Rep | G-Q1 contract | G-Q2 must-catch | G-Q3 catch-floor | G-Q4 false-block | verdict |
|---|---|---|---|---|---|---|---|
| **qav-ft-v3** | qav-held-001 | 1–3 | PASS ×3 | FAIL(class attribution) ×3 | — | — | FAIL |
| **qav-ft-v3** | qav-held-002 | 1–3 | PASS ×3 | — | FAIL(RC-01 class) ×3 | **PASS ×3** | FAIL |
| qav-ft-v2 (banked) | both | 1–3 | PASS 6/6 | FAIL ×3 | FAIL ×3 | PASS ×3 | FAIL 6/6 |
| qav-ft v1 (banked) | both | 1–3 | PASS 6/6 | FAIL ×3 | FAIL ×3 | PASS ×3 | FAIL 6/6 |
| gemma4-26b (banked) | both | 1–3 | 3/6 | FAIL ×3 | FAIL ×3 | PASS ×3 | FAIL 6/6 |

All 6 v3 rep-runs valid first-attempt (runner exit 0, 24/24 bundles `finish=stop`, 0.6–2.0 s/bundle);
grades = separate unmasked pytest exits per rep-task dir.

## §3 verdict (applied verbatim)

- **G-Q1 contract:** met 6/6 (= v1/v2). **G-Q4 false-block:** met 9/9 (= all candidates, all sits).
- **G-Q2 must-catch:** NOT met. Verdict level: **12/12 gold negatives rejected** (= v1/v2).
  Owning class: **1/12** — rep-3 GN-1 = DC-08 with anchor, **the lane's first-ever correct GN-1
  leg**. The rest miss; detail below.
- **G-Q3 catch floor:** NOT met — RC-01 rejected ×3 **with the anchor firing ×3** (locus names
  `tests_run=0` / `signal_absent` / the claims text) but class DC-03, never DC-14.

## VERDICT: **NO-DEPLOY** (pre-registered disposition — the checkpoint stays a directory)

## What the contrast pairs demonstrably moved (non-gating — the re-exam's evidence)

| Signal | v2 | v3 |
|---|---|---|
| DC-12 attractor legs (of 15) | **9** (GN-3, GN-4, RC-01 ×3) | **3** (GN-4 only) — **the attractor broke** |
| Attribution determinism | byte-identical wrong ×3 | per-rep wobble (GN-1: DC-03/DC-05/DC-08) — the shape→class shortcut destabilized |
| GN-1 owning class | 0/3 | **1/3** (first ever) |
| GN-3 anchor (producer vacancy named) | 0/3 | **3/3** |
| RC-01 anchor | 3/3 | 3/3 (class still stuck: DC-03) |
| GN-4 anchor | 3/3 (via `kwargs`) | 0/3 — **regressed**: loci say "wiring null" and lost the kwargs/soft-fail vocabulary |
| Held-out gate probes (DC-12/DC-14 pair shapes) | impossible (eval had neither class) | **both REJECT at the Phase-5.2 gate** — the pair shapes themselves transfer held-out |

Per-leg exact record (recomputed with the frozen `qav_gates` instruments): GN-1 said
DC-03/DC-05/**DC-08✓**; GN-2 said DC-05/DC-08/DC-08 (anchor 0/3); GN-3 said DC-05 ×3 (anchor
3/3); GN-4 said DC-12 ×3 (anchor 0/3); RC-01 said DC-03 ×3 (anchor 3/3).

## The residual, precisely — the design's own honest cap materialized

The remaining failure concentrates on **the null-vacancy shape**: every GN bundle's DC-03
signature is a *null* composition field under green suites, and the exam-time loci show v3
reading that evidence correctly ("wiring null + gates green = production call site unverified"
— textbook DC-03 analysis) while naming DC-05 or DC-12. The v1.2 pairs taught
**populate-with-defect** shapes (the only same-task construction available — nulling a field
the approve control also has null would be label-incoherent, design v1.2 §2); the pure
**vacancy→DC-03** mapping rode only the 3 `C-dc03` rows study_tutor spines could mint. The
design named exactly this cap before the run. Two secondary findings: (a) **DC-05 emerged as a
null-wiring mini-attractor** (5 legs) — DC-05's owning signature is tamper *evidence* (sysmod
stubs, skip-guard divergence), never a mere vacancy, and no control teaches that negative rule
(DC-05 train support: 3 rows); (b) GN-4's kwargs/soft-fail vocabulary was crowded out —
the populated-defect A-dc03 loci carry it, but on vacancy spines v3 falls back to "wiring null"
prose.

**Indicated v4 levers (named, not claimed):** (1) a VACANCY-shape cohort at scale — more
populated-control spines (study_tutor breadth; record-store recovery for UPT-001/QAV-006-class
tasks) nulled per-field-combo, plus vacancy loci carrying the kwargs/soft-fail/producer
vocabulary; (2) DC-05 boundary controls — vacancy-approve/tamper-reject pairs so "null ≠
tamper" is taught, cutting the new mini-attractor; (3) the eval-side gate now sees every class —
keep it as the cheap pre-exam attribution probe it just proved to be.

## Honest caps

1. v2/v1/stock columns banked (same freeze/runner/pins/box); v3's 6 rep-runs are the only fresh sits.
2. The Phase-5.2 verdict-informational axis missed the two historic thin-prompt rows
   (`43c8de…` DC-08, `13f964…` DC-03 — missed by every tune's gate, three for three) and a
   DC-05 row; the frozen exam remains the only grade and the gate's format axis (6/6) is what gates.
3. The corpus cycle's harvest-mode miss (30 rows dropped by a config-default launch) was cured
   by byte-preserved `.bak` merge + engine-rebuilt manifest before staging — receipted in adf.
4. The widened eval-split exam crosscheck fired on first use and was scoped with a gold-negative
   exemption (the corpus's gold rows are deliberate exam twins, never trained) — adf `33edfe1`.
5. Probe, not adoption (R3-02): `qav-ft-v3` is a probe-set entry; NO-DEPLOY makes promotion moot.

## Serving receipts + rollback

Config backup `config.yaml.bak-20260724-060941-pre-qav-ft-v3`; added the `qav-ft-v3` block
(exact mirror), var `qft3`, `qav_exam` → `"qft & qft2 & qft3 & g26 & pk & qt"`; systemd restart;
`/v1/models` lists all four candidates; warm-smoke 200 in 19.5 s; single-slot law honored
(solver-quiet wait → warm → `ready` verified before the runner — the v2 refusal lesson applied,
zero refusals this sitting). Keepalive stayed flock-held for the whole overnight window
(fresh holder post-wedge); the pause is released at close-out. All three tuned candidates
remain parked on llama-swap for follow-up probes; rollback = the dated .bak.
