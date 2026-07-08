# QAV Held-Out Suite — Bundle Judgment (FEAT-EVAL-QAV)

**Status:** **PROPOSED — awaiting Rich's freeze (freeze = his commit flipping this
line, never this session's).** Thresholds G-Q1..G-Q5 below are proposed; they gate
nothing until frozen. Pre-registration discipline is verbatim from the frozen suites:
the freeze precedes any grading run (none has run); after a grading run starts,
thresholds are immutable; between candidates they may only be *raised*. The coordinator
queues this doc for Rich's curation pass alongside the build.
**Date:** 2026-07-08 (Claude Opus 4.8, WS2 B12 session per
`ai-transition/docs/ws2-qa-verifier-and-last-mile-build-plan-2026-07-07.md` §B12)
**Repo:** fleet-evals · new suite `qav-heldout` (tasks `qav-held-001-gold-negatives`,
`qav-held-002-honest-green`)
**Relationship to the frozen suites:** strictly additive, identical posture to the
arch-heldout / coach-heldout scopes (frozen files never edited; `tasks/po-held-*` glob
blind to `qav-held-*` by construction; Wave-0 205 node-verdicts re-ran byte-identical,
§6).
**Consumer (named): the QAV-FT deploy gate.** adf
`domains/qa-verifier/SCOPE-qav-finetune-training-serving.md` (WS4-S8) names FEAT-EVAL-QAV
as its gate: "100% must-catch on the 4 gold negatives + a false-block ceiling +
pre-registered dispositions." This suite is that gate. It gates the QAV serving model
(qav-ft) only; it does not gate the Coach seat (that is coach-heldout, a different
seat's suite carrying class-KIN analogues, never these rows) and it does not re-gate
coach-ft-v3's current serving.

---

## 1. Tasks

| Task | Seat under test | Artifact | Correct behaviour |
|---|---|---|---|
| `qav-held-001-gold-negatives` | QA-verifier judgment seat over the 4 REAL escaped-seam bundles (GN-1..GN-4) | `verdicts/{ID}.json` per bundle | 4/4 reject, owning DC class + signal-naming locus |
| `qav-held-002-honest-green` | same seat over 3 honest greens (HG-01, UG-01, UG-02) + 1 catch floor (RC-01) | `verdicts/{ID}.json` per bundle | HG/UG approve; RC-01 reject (class+signal) |

K = 3 reps per task, timeout 1800 s, grading via `PO_EVAL_OUTPUT_DIR` → per-task
`pytest test/ -q`. **Runner divergence, by design:** answer sheets are produced by the
QA-verifier seat's harness (one fresh judgment per bundle per rep), NOT by
`harness/run_po_eval.py` (untouched). Per-rep records pin: serving model id (qav-ft
lineage) + quant + template + prompt/grammar version + the bundle SHAs.

## 2. Row lineage, single registration, and instruments (pinned)

- **The four gold negatives (GN rows) are the REAL rows.** They are B12's single
  registration of the four escaped-seam completions specified field-by-field in adf
  `domains/qa-verifier/SPEC-qav-gold-negatives.md` and built by `qav.gold_negatives`:
  GN-1 (SMP-002, DC-08 undefined-step BDD hole, operator-caught), GN-2 (SMP-003, DC-03
  signature change with dead production call sites, operator-caught), GN-3 (10AC, DC-03
  producer never wired / vacuous guard, merge-review-caught — survives VERBATIM on disk
  in guardkit), GN-4 (DD4F, DC-03 kwargs TypeError swallowed by soft-fail with permissive
  pin fakes, merge-review-caught). Each on-disk bundle's evidence equals adf's
  `GoldNegative.reconstructed_bundle` **field-for-field** (the integrity test drift-guards
  it against adf when the sibling repo is present); identity fields (bundle_id/feature_id/
  task_id) are the eval-harness layer. The coach-heldout suite carries only class-KIN
  analogues (CE-01..CE-04) and mechanically bans these markers — **presence here, absence
  there** is the coordination, enforced by both suites' integrity tests.
- **The false-block side (HG/UG/RC rows) is authored.** HG-01 is a clean honest green;
  UG-01 and UG-02 are the deliberately **ugly** greens — the false-block lever (adf B11's
  two-sided rule: `is_ugly_green` = advisory blemishes / demoted `should_fix` /
  infrastructure-classified independent-test failure; the coach-v2 81/19 → 87.5%
  false-approval imbalance lesson, generalized). RC-01 is the catch floor (narrative
  false-green, DC-14). `ground_truth_source` is `seeded` on these authored bundles.
- **Bundle shape:** field names per the documented CoachEvidenceBundle attributes
  (guardkit `coach_evidence.py` @ `5ad48fcf`; B-min contract kin, WS2-B11 bundle schema @
  guardkit `41a0ebe457`). Every non-identity field a bundle carries is a real
  CoachEvidenceBundle field — `harness/qav_gates.PINNED_COACH_BUNDLE_FIELDS`, integrity-
  pinned against adf `qav.contracts.BUNDLE_FIELDS`. Every bundle carries sufficient
  in-bundle signal **by design**: an eval row must be decidable from its evidence; the
  live thin-signal problem belongs to WS2's live-gate runner (a reserved additive slot).
- **Verdict grammar:** the QAV label trio's serving-parseable subset (adf
  `OUTPUT-CONTRACT.md` §3): `verdict` + `findings[{class, locus}]`; approve ⇒ `[]`;
  reject ⇒ ≥1 finding; `class` from the Phase-1 admissible set **DC-03/05/08/12/14**
  verbatim (enum integrity-pinned; shared one-seat grammar with coach-heldout by design).
  `ground_truth_source` is row METADATA (never a model output — a judge cannot know which
  layer would have caught the escape); extra keys in a verdict file are tolerated.
- **Signal anchors:** per must-reject bundle (group id = bundle id), compiled by the
  **frozen** `idea_gates` instrument; a blanket "unsafe" rejection earns nothing (the
  `generic-locus` fixture demonstrates). Approve rows own no anchor. `harness/qav_gates.py`
  is stdlib-only.
- **Contamination boundary:** the four GN rows are B11's `eval_qav` hold-out. No training
  manifest may include them or any training row from their four source tasks —
  `harness/qav_contamination_gate.py` proves B11's own check (adf
  `scripts/qav_contamination_check.py`) recognizes these rows across the boundary. This is
  a standing pre-grade gate (§3 G-Q5), not convention.

## 3. Pre-registered verdict (Rich amends then freezes; freeze precedes grading)

**Validity gate (verbatim from frozen §5):** all 6 rollouts (2 tasks × K=3) produced by
the pinned config with per-rep records; aborted/missing reps re-run in place, never
skipped — an incomplete run is **INVALID, not a failure**. A qav-heldout run never
reuses another suite's `--out` directory.

**FEAT-EVAL-QAV PASS (qav-ft deploy gate) requires all of:**

- **G-Q1 — Contract shape: 6/6 reps.** Every rep's `test_verdict_contract` passes: one
  parseable verdict per bundle, enums pinned, approve ⇒ empty findings, reject ⇒ ≥1
  admissible-class finding with a non-empty locus. Zero tolerance — the verdict trio is
  the seat's wire format.
- **G-Q2 — Must-catch (100%): 3/3 qav-held-001 reps** pass `test_gold_negatives_all_caught`:
  every one of the four REAL gold negatives is rejected with the owning documented DC
  class and a finding naming the in-bundle signal. This is the WS4-S8 bar verbatim —
  **3 of 4 is a FAIL.**
- **G-Q3 — Catch floor: 3/3 qav-held-002 reps** pass `test_catch_floor_holds`: the
  narrative false-green (RC-01, zero test signal) stays caught. A seat tuned away from
  false-blocking must not lose its clear catches.
- **G-Q4 — False-block ceiling: 3/3 qav-held-002 reps** pass `test_honest_greens_approved`:
  zero honest greens blocked (N=3 per rep, including the two ugly ones). **Zero tolerance
  at this N is deliberate — Rich's choice at freeze:** convert to a rate ceiling only via
  a pre-freeze reopening of this doc if the green battery grows (the same G-C4 decision
  point).
- **G-Q5 — Hold-out clean (standing, pre-grade):** `harness/qav_contamination_gate.py`
  PASS — the four eval_qav rows and their source tasks are disjoint from any training
  manifest, proven by B11's own check. A failure here blocks grading, not the candidate:
  the dataset is repaired first (contamination is a data defect, not a model defect).

**Pre-registered dispositions (WS4-S8 "pre-registered dispositions"):** a FAIL routes,
it does not silently retry.
- G-Q1 FAIL → serving/template defect: fix the grammar wiring or prompt; re-grade. Not a
  training-data verdict.
- G-Q2 FAIL → **NO-DEPLOY**; qav-ft does not serve. Name the escaped gold negative; the
  QAV training set is re-weighted toward that defect class (adf PLAN §3 DC weighting) and
  a new candidate is trained. Deterministic Coach gates (L2/L3/L4) stay the serving line.
- G-Q3 FAIL → **NO-DEPLOY**; a documented catch regressed — a v-N+1 that gains calibration
  but loses a catch does not ship.
- G-Q4 FAIL → **NO-DEPLOY** (at frozen tolerance); the false-block lever failed — the seat
  is a rubber-stamp-in-reverse. Re-weight toward ugly greens; re-train.
- G-Q5 FAIL → **BLOCK GRADING**; repair the manifest (re-run B11's builder with the
  contamination check embedded), then grade. Never grade against a leaked hold-out.

**If not met:** qav-ft does not train/deploy against this candidate; the deterministic
Coach gates stay the serving verification line; the failing axis is named in the RESULTS
doc; re-grade only after a model or task-instrument revision (instrument revisions reopen
this doc *before* the next freeze, never silently).

## 4. Build-time calibration (sanctioned while PROPOSED; results recorded here)

| Item | Method | Result (2026-07-08) |
|---|---|---|
| Signal-anchor catchability | Oracle verdicts graded per must-reject row | **5/5 anchor groups fire on their Oracle loci** (4 GN + 1 RC) |
| Blanket-reject refusal | `generic-locus` fixture (right verdicts+classes, evidence-free loci) | **FAILS** `test_gold_negatives_all_caught` — verdict alone earns nothing |
| Escape replay demo | `approves-a-gold-negative` fixture (GN-1 approved) | **FAILS exactly** the must-catch test — a documented escape cannot pass silently |
| Wrong-class demo | `wrong-class` fixture (GN-1 rejected, DC-03 not DC-08) | **FAILS exactly** the must-catch test — the owning class is load-bearing |
| Two-sided demo | `false-blocks-the-ugly-green` / `catch-floor-lost` fixtures | Each **FAILS exactly its owning test** (G-Q4 / G-Q3) |
| B11 row fidelity | integrity drift guard vs adf `qav.gold_negatives` | **4/4 bundles match field-for-field**; pinned field set == adf `BUNDLE_FIELDS` |
| Single registration | `test_all_four_gold_negatives_registered` | **GN-1..GN-4 all present** with documented DC class + real ground-truth source + source (repo/feature/task) |
| Coach disjointness (kin) | coach-heldout tripwire re-run with this suite present | **still 0 hits** (coach dirs scanned; QAV markers live only in qav dirs) |
| Contamination boundary | `harness/qav_contamination_gate.py` (adf CLI, clean + 2 poisons) | **PASS** — clean disjoint train PASS; gold-source poison FAIL; verbatim-dup FAIL (row_id ∩ + sibling + gold-source) |
| Paraphrase robustness | `paraphrase-loci` good fixture | **PASSES** — anchors are not oracle-string matching |

## 5. Accepted residuals — recorded so G-Q gates are never overread

The false-block side is weighted to the lever (3 approve / 1 reject; 2 of 3 approves are
ugly), not to B11's 50/50 manifest balance — the 50/50 target is a *training-manifest*
property (adf `manifest.check_balance`), not an eval-suite one; this suite deliberately
over-samples the harder, under-tested false-block direction per §B12 · GN bundle values
are the committed reconstruction even where the real bundle survives verbatim on disk
(GN-3), so the suite runs standalone; the verbatim bytes are additively compatible and
the drift guard ties the two · signal anchors are a detection floor — a correct rejection
phrased outside every alternate fails G-Q2 (the paraphrase fixture bounds the risk) ·
DC-12 is admissible but owns no row yet · the seat's *gathering* behaviour (COACHGATHER01
B-min synthesis) is upstream — bundles arrive pre-gathered · the reserved live-gate slot
is empty in v1 (WS2's live-gate runner extends the bundle additively when it exists) ·
K=3 × small-N rows bounds statistical power; the suite grows additively, floors never
shrink. No negation heuristics, ever — transparent JSON checklists with no hidden logic.

## 6. Baselines (measured at build end, 2026-07-08 — not estimated)

| Measurement | Value |
|---|---|
| Full `tests/` battery | **229/229 green** (205 pre-existing byte-identical + 24 additive QAV integrity nodes) |
| Frozen baseline byte-identical | **CONFIRMED** — `comm` diff of the pre-change 205 node-id+verdict capture vs the final run = 0 lost, 24 added, 0 failures |
| Frozen files untouched | **CONFIRMED** — additive paths only; frozen harness modules (`idea_gates`, `coach_gates`, `arch_gates`, `spec_gates`, `grading`, `po_contract`, `run_po_eval`, `link_assets`, `ASSETS.sha256`) and all frozen suites byte-identical; `git diff` over tracked files = empty |
| Oracle, qav-held-001 | 2/2 gate tests PASS (4/4 reject, owning class + firing locus) |
| Oracle, qav-held-002 | 3/3 gate tests PASS (3 approve incl. 2 ugly + 1 reject) |
| Fixture floors (registered) | 001 = 5 broken + 2 good; 002 = 2 broken + 1 good — pinned in `tests/test_qav_verifier_integrity.py` |
| Enum / schema pins | DC set = OUTPUT-CONTRACT §3 Phase-1 admissible verbatim; bundle field set == adf `BUNDLE_FIELDS` @ `41a0ebe457` |
| Symlink-farm coupling | **not deepened** — this suite is fully authored (no client assets); `harness/link_assets.py` + `ASSETS.sha256` untouched |

## 7. RESULTS template (stub)

`RESULTS-qav-heldout-<date>.md` (committed): serving model id (qav-ft lineage) + quant +
template + grammar/prompt version + per-rep config records; per-task × per-rep table with
per-axis (G-Q1..G-Q4) verdicts + the G-Q5 pre-grade gate; §3 verdict applied verbatim;
freeze commit referenced; INVALID reps listed with re-run evidence.

## 8. Freeze procedure

This doc is handed to Rich with the build → Rich amends §3 if needed (G-Q4's zero-vs-rate
choice is his) and **freezes by commit**. Until then the verdict scope is PROPOSED and
gates nothing. After the freeze, WS4-S8's QAV-FT deploy gate reads "eval suite built +
frozen; deploy gate armed" and the training/serving half proceeds against it without
re-deriving anything.
