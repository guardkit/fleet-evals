# RESULTS — QAV held-out deployment gate — qav-ft-v2 — 2026-07-23 (the 3-way re-exam)

**Candidate (v2, fresh this run):** `qav-ft-v2` = unsloth/gemma-4-26B-A4B-it MoE + 16-bit LoRA
retrained on the **302-row attribution corpus** (adf `attribution-corpus-2026-07-23.md` @18b9084 +
`tune-train-v2-2026-07-23.md`; seeded_record family: DC-12 support 0→69, DC-14 7→56; staged
seq-20480, 276 train rows post-exclusion; 207/207 steps, train_loss 0.08727, **eval_loss
1.253→1.100→1.064 still falling** vs v1's 1.512→1.325→1.322 plateau) → merged-16bit
(Phase-5.2 gate PASS 4/4 bare JSON) → GGUF **Q4_K_M** via the same coach-ft-v3 pipeline.
GGUF sha256 `892fb9a324c693595301433ded21860763a2293851aced89b95a981ec68a89be`
(16,796,000,992 bytes — byte-identical size to v1's,
`/opt/llama-swap/models/qav-ft/qav-gemma4-26b-moe-v2.Q4_K_M.gguf`), served as the `qav-ft-v2`
llama-swap entry (exact `qav-ft` block mirror; the `qav_exam` set gained `qft2`).

**Comparison columns (banked, same day / same freeze / same runner):** `qav-ft` (v1) and
`gemma4-26b` (stock) columns cite their 2026-07-23 runs at fleet-evals `e66a8be`
(`runs/qav-heldout/{qav-ft,gemma4-26b}-2026-07-23/`, RESULTS-qav-ft-v1-2026-07-23.md) —
**not re-run**: identical freeze `2165802`, identical runner sha `4d1d3292d665f9d3…`, identical
sampling pins and system-line sha `a7f5c6fa9059fc64…`, same box, same serving stack. Recorded
honestly: v1/stock numbers are that morning's; only v2's 6 rep-runs are fresh (evening, post the
GB10 OOM-wedge recovery — see the adf v2 receipt §6 for the interruption record).

**Frozen thresholds:** qav-heldout-suite-scope.md §3, frozen at `2165802`. Frozen `tasks/` /
`docs/` / `harness/qav_gates.py` untouched; the only writes this run are `runs/qav-ft-v2-…/` + this doc.

**Verifier integrity at grade time:** QAV-scoped `pytest tests/test_qav_runner.py
tests/test_qav_verifier_integrity.py -q` → **49 passed, exit 0** (unmasked).
**Contamination gate:** `harness/qav_contamination_gate.py` → **PASS** (self-test 3/3; the
grown 279-row train manifest's cross-check ran at staging: 562 exam shingles × 279 rows, 0 hits).
Runner snapshot copied per convention (`runs/qav-heldout/qav-ft-v2-2026-07-23/run_qav_heldout.py`,
sha256 == harness HEAD).

## Headline: per-task × per-rep × per-gate — v2 vs v1 vs STOCK

| Candidate | Task | Rep | G-Q1 contract | G-Q2 must-catch | G-Q3 catch-floor | G-Q4 false-block | verdict |
|---|---|---|---|---|---|---|---|
| **qav-ft-v2** | qav-held-001 | 1 | PASS | FAIL(class attribution) | — | — | FAIL |
| **qav-ft-v2** | qav-held-001 | 2 | PASS | FAIL(class attribution) | — | — | FAIL |
| **qav-ft-v2** | qav-held-001 | 3 | PASS | FAIL(class attribution) | — | — | FAIL |
| **qav-ft-v2** | qav-held-002 | 1 | PASS | — | FAIL(RC-01 class) | **PASS** | FAIL |
| **qav-ft-v2** | qav-held-002 | 2 | PASS | — | FAIL(RC-01 class) | **PASS** | FAIL |
| **qav-ft-v2** | qav-held-002 | 3 | PASS | — | FAIL(RC-01 class) | **PASS** | FAIL |
| qav-ft (v1, banked) | both | 1–3 | PASS 6/6 | FAIL ×3 | FAIL ×3 | PASS ×3 | FAIL 6/6 |
| gemma4-26b (banked) | both | 1–3 | 3/6 (7/12 truncated) | FAIL ×3 | FAIL ×3 | PASS ×3 | FAIL 6/6 |

All 6 v2 rep-runs valid on the first attempt (runner exit 0, no ABORTED.json, no re-runs);
grades = separate unmasked pytest exits (`grade.txt` + `grade-exit.txt` per rep-task dir).

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **G-Q1 contract (6/6):** v2 **met 6/6** — 24/24 bundles bare-JSON, `finish=stop` everywhere,
  0 truncations, 0.65–2.78 s/bundle. (v1 6/6; stock 3/6 with 7/12 gold-negative truncation-escapes.)
- **G-Q2 must-catch (3/3 reps of 4/4 with owning class + in-bundle locus):** **NOT met.**
  Verdict level: **12/12 gold negatives REJECTED, zero escapes** (= v1; stock escaped 7/12).
  Owning class: **0/4 in every rep** (v1: 1/1/0). The misses are BYTE-IDENTICAL across reps:
  GN-1 said DC-03 (owns DC-08) · GN-2 said DC-08 (owns DC-03) · GN-3/GN-4 said DC-12 (own DC-03).
  Anchors (locus naming the in-bundle signal): **fired on GN-1 + GN-4 every rep** (v1 fired
  GN-1/GN-3 reliably); unfired on GN-2/GN-3.
- **G-Q3 catch floor:** **NOT met** — RC-01 rejected in all reps (= v1) **with the anchor
  FIRING** (locus names `tests_run`-vacuity — v1 paraphrased) but class **DC-12**, never the
  owning **DC-14**. The single miss item per rep.
- **G-Q4 false-block ceiling:** **met** — 9/9 honest/ugly greens approved with empty findings
  (= v1 = stock).

## VERDICT: **NO-DEPLOY** (pre-registered disposition — the checkpoint stays a directory)

The frozen bar fails exactly where v1's did — **defect-class attribution** — and nowhere else.
`qav-ft-v2` remains a probe-set A/B entry only.

## What the attribution corpus DID move (non-gating, the re-exam's point)

1. **Judgment quality generalized:** eval_loss fell 1.322→1.064 and kept falling at epoch 3;
   every catch/approve behavior held at v1's perfect level with 3.4× the training data.
2. **Loci became evidence-native.** v2's findings name bundle fields and anchors
   (`bdd_authoring_sweep`, `wiring.call_sites.production.missing_kwargs`, `git diff 1ad98c0`,
   `tests_run` vacuity on RC-01) where v1 paraphrased. RC-01's anchor fires for the first time.
3. **Attribution became deterministic.** All three reps produce byte-identical class
   assignments (v1 wobbled rep-to-rep). The tune now has a *stable, wrong* class map — a far
   better retraining target than noise.
4. **The DC-05 guessing habit is gone** (v1 defaulted wiring-flavored rejects to DC-05/DC-12
   stochastically; DC-05 no longer appears anywhere).

## The new failure shape (what the next corpus lever must cut)

- **DC-12 became an attractor.** The corpus's largest new class (69 rows) now swallows
  everything wiring/vacuous-green-shaped: GN-3, GN-4 (both DC-03 composition-seam) and RC-01
  (DC-14 narrative false-green) all read DC-12. **DC-14 never fires despite 56 training rows** —
  and RC-01's locus text ("green claim vacuous, tests_run…") is DC-14-*shaped reasoning wearing
  a DC-12 label*: the model learned the record-native evidence reading but not the class
  boundary between vacuous-wiring-green (DC-12), narrative false-green (DC-14), and
  composition-seam (DC-03).
- **The GN-1↔GN-2 swap is symmetric and deterministic** (the BDD/absent-signal pair: v2
  attaches DC-03 to the authoring-sweep bundle and DC-08 to the bdd-null bundle, the exam's
  ground truth the reverse). This is a class-semantics disagreement, not noise — the corpus's
  DC-03/DC-08 exemplar phrasing plausibly teaches this mapping. Worth a design look before the
  next spike: minimal contrast pairs (same bundle shape, different owning class) rather than
  more per-class volume.
- Indicated cure: **class-boundary contrast exemplars**, not more DC-12 rows — the anti-shortcut
  concern from the lane design now has empirical teeth.

## Non-gating diagnostics

| Metric | qav-ft-v2 (rep 1/2/3) | qav-ft v1 (banked) | gemma4-26b (banked) |
|---|---|---|---|
| Gold negatives rejected, verdict level (of 4) | 4 / 4 / 4 | 4 / 4 / 4 | 2 / 1 / 2 |
| Gold negatives with owning class correct (of 4) | 0 / 0 / 0 | 1 / 1 / 0 | 1 / 0 / 1 |
| GN anchors fired (of 4) | 2 / 2 / 2 (GN-1, GN-4) | ~2 (GN-2 never; GN-4 flaky) | n/a (truncations) |
| RC-01 caught (verdict) / anchor / class | yes ×3 / **fires ×3** / DC-12 | yes ×3 / — / DC-03 | yes ×3 / — / DC-05,DC-12 |
| Greens approved (of 3) | 3 / 3 / 3 | 3 / 3 / 3 | 3 / 3 / 3 |
| Truncated generations (of 8/rep) | 0 / 0 / 0 | 0 / 0 / 0 | 2 / 3 / 2 |
| Wall/bundle (min/med/max, s) | 0.65 / ~1.5 / 2.78 | 0.45 / 1.03 / 1.41 | 9.09 / 25.47 / 46.63 |

## Honest caps

1. **v1/stock columns are banked, not re-run** (same freeze/runner/pins/box, that morning).
   The 3-way is a comparison on the sealed gates, not three simultaneous sits.
2. **The eval split has no DC-12/DC-14 rows** (DC-12 never existed in eval; the only DC-14 row
   fell to the seq-20480 gate) — the frozen exam is the ONLY held-out attribution grade, which
   is exactly where it failed. The corpus's eval-side class coverage is its own open item.
3. **The 3 longest reject exemplars (52–66k tok) remain unseen by any tune** (seq-20480
   exclude-never-truncate, named in the v2 receipt §2).
4. **Probe, not adoption (R3-02).** No deploy claim; seat promotion stays a separate
   fleet-evals-gated decision that is Rich's — moot on a NO-DEPLOY.

## Serving receipts + rollback

- Config backup `/opt/llama-swap/config/config.yaml.bak-20260723-200614-pre-qav-ft-v2`; added
  the `qav-ft-v2` block (exact `qav-ft` mirror), var `qft2`, and `qav_exam` →
  `"qft & qft2 & g26 & pk & qt"`. Restart via systemd; smokes: `/v1/models` lists all three
  candidates; 1-token completions HTTP 200 each (qav-ft-v2 14.5 s / qav-ft 19.4 s /
  gemma4-26b 38.8 s cold).
- **Single-slot law honored the hard way:** the first exam attempt was REFUSED 6/6 by the
  runner's fresh `/running` probe (the startup preload had evicted the candidate — the probe
  did its job); the refusal debris was wiped, the candidate warmed and verified `ready`, and
  the graded run above is the clean second pass. Keepalive stayed flock-held (fresh holder —
  the pre-hang holder died with the wedge) for the whole window; audio pair ready throughout.
- Rollback = the dated .bak above (or delete the `qav-ft-v2` block + `qft2` var + restore the
  set line). The `qav-ft-v2` entry + widened `qav_exam` set are left in place for follow-up probes.
