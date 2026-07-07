# Architect Held-Out Suite — Adversarial Review (FEAT-EVAL-ARCH)

**Status:** **FROZEN 2026-07-08 (Rich — thresholds G-A1..G-A3 accepted as proposed,
G-A2 at must-catch 100%; the MISSING_SEAM taxonomy extension explicitly RATIFIED —
"so many issues trace back to the seam"; this commit is the freeze).** Acceptance given
by Rich in the 2026-07-08 P16 follow-up session (fleet-evals); house convention:
freeze = the commit flipping this line. Pre-registration discipline verbatim from the
frozen suites: the freeze precedes any grading run (none has run); after a grading run
starts, thresholds are immutable; between candidates they may only be *raised*.
**Date:** 2026-07-08 (Claude Fable 5, P16 session per
`ai-transition/docs/kickoff-prompts-fable-sessions-2026-07-07.md` Prompt 16)
**Repo:** fleet-evals · new suite `arch-heldout` (tasks `arch-held-001-adversarial-review`,
`arch-held-002-sound-design-review`)
**Relationship to the frozen suites:** strictly additive. Every frozen artifact
(`po-heldout-suite-scope.md` 2026-07-03, `po-heldout-idea-extension-scope.md` 2026-07-05,
`po-heldout-spec-extension-scope.md` 2026-07-07, tasks po-held-001..008, the frozen
harness modules, the frozen test files) is never edited. New tasks carry
`suite = "arch-heldout"`; the frozen integrity file's `tasks/po-held-*` glob cannot see
them, so the frozen parametrization is unchanged **by construction**. The Wave-0 221
node-verdicts (`pytest tests/ tasks/`) re-ran byte-identical after this build (§6).
**Consumer (named): the architect fine-tune (arch-FT).** WS4 §5 names an eval suite as
the architect fine-tune's PRECONDITION ("no architect fine-tune before it exists" —
Architect row + WS4-S8 disposition note) and names the adversarial-depth weakness
(PHANTOM/gap detection, "accepting without stress-testing" — specialist-agent fan-out
GAP, no landed remediation) as the fine-tune's training objective. This suite is that
precondition's judgment half: it gates arch-FT training acceptance and any architect-seat
model bump (WS4 §6.2 loop gate: frozen suites + role suite). It does NOT gate G2b
(FEAT-EVAL-SPEC owns the FEAT-SPL-007/008 terminal — po-held-008 already grades the
architect's plan-*generation* shape), nor the po-ft-v1 deploy, nor SPL G2; none of those
ever rescue a failed G-A gate.
**Scoping note (the WS4 §5 debt has two halves):** (a) generation graded against the
39 `/feature-plan` gold traces — the shape floor of that half already exists as
po-held-008 under G2b, and a gold-trace-seeded architect *generation* extension can be
added additively later; (b) the adversarial-depth *judgment* half — seeded-flaw review
where correct behaviour is to catch the phantom component or missing seam. This suite is
(b), the half the kickoff names as the primary target, sharing the flaw taxonomy posture
with the QAV dataset (WS4 §5.3).

---

## 1. Tasks

| Task | Seat under test | Artifact | Correct behaviour |
|---|---|---|---|
| `arch-held-001-adversarial-review` | architect review seat, seeded-flaw packet (goals + design + repo manifest, FoodReach domain, authored fresh) | `review.json` (verdict + findings[{pattern,target,evidence}]) | `revise`; all 4 seeded flaws named |
| `arch-held-002-sound-design-review` | same seat, same goals/manifest **byte-identical**, repaired design | `review.json` | `approve` with zero findings |

K = 3 reps per task, timeout 1800 s, grading via `PO_EVAL_OUTPUT_DIR` → per-task
`pytest test/ -q` (frozen-suite convention). **Runner divergence, by design:** answer
sheets are produced by the architect review seat's harness (specialist-agent
`roles/architect`; the serving prompt is built when that seat's headless harness lands),
NOT by `harness/run_po_eval.py` (untouched). Per-rep records must pin: serving model id +
quant + template, the review-seat tool version, and the input SHAs. The two tasks share
goals + manifest byte-identically (integrity-pinned) so a verdict split isolates
judgment, not input drift.

## 2. Contract sources and instruments (pinned)

- **Pattern vocabulary:** the architect Coach's own detection taxonomy —
  specialist-agent `roles/architect/criteria/definitions.yaml` `detection_patterns`
  @ `ed2cfe5` (7 ids), plus `MISSING_SEAM` added by this suite for the player.md
  flow-trace duty ("missing interactions" — WS4 §5's "phantom component or missing
  seam" pair has no definitions.yaml id; mislabelling the class would be worse than
  extending the enum). Enum pinned by `tests/test_arch_verifier_integrity.py`.
- **Verdict grammar:** carried from the QAV label contract (adf
  `domains/qa-verifier/OUTPUT-CONTRACT.md` §3): `approve` ⇒ `findings: []`; `revise` ⇒
  ≥1 finding. One verdict grammar across the factory's judgment seats, deliberately.
- **Seeded-flaw anchors (001):** `test/reference/flaw_anchors.json` — 4 groups, one per
  seeded flaw (phantom-reconciliation · missing-notification-seam ·
  replica-scale-assumption · gamification-creep), idea-extension §2.1 schema compiled by
  the **frozen** `idea_gates` instrument (imported, not copied), per-finding matching
  with the frozen anti-stuffing threshold (>2 ⇒ the finding credits nothing).
  **Disjointness, adapted:** no alternate may match `goals.md` or `repo-manifest.json`
  (restating the inputs earns nothing); `design.md` is exempt by construction — it
  contains the flaws. The missing-seam group's alternates demand absence-language or the
  named missing edge, so goal-restating text cannot fire it.
- **Dependency posture:** `harness/arch_gates.py` is stdlib-only and imports the anchor
  machinery + threshold from the frozen `idea_gates` (the spec_gates precedent). No
  frozen module edited.

## 3. Pre-registered verdict (Rich amends then freezes; freeze precedes grading)

**Validity gate (verbatim from frozen §5):** all 6 rollouts (2 tasks × K=3) produced by
the pinned config with per-rep records; aborted/missing reps re-run in place, never
skipped — an incomplete run is **INVALID, not a failure**. An arch-heldout run never
reuses another suite's `--out` directory.

**FEAT-EVAL-ARCH PASS (arch-FT gate) requires all of:**

- **G-A1 — Contract shape: 6/6 reps.** Every rep emits a parseable `review.json`
  passing `test_review_schema` (verdict enum; pinned pattern enum; approve ⇒ zero
  findings; every finding carries target + evidence). Zero tolerance: an unparseable or
  incoherent review is unusable by any downstream consumer.
- **G-A2 — Adversarial depth (must-catch, 100%): 3/3 001 reps** pass
  `test_verdict_is_revise` AND `test_all_seeded_flaws_caught` (all 4 anchor groups fire;
  stuffed findings credit nothing). This is the weakness under test — the bar is the
  QAV gold-negative posture applied to design review: catching 3 of 4 is a FAIL.
- **G-A3 — False-block ceiling: 3/3 002 reps** pass `test_verdict_is_approve` (the
  repaired design approved, findings empty). Zero tolerance at K=3 is deliberate — a
  seat that fails everything scores G-A2 for free; G-A3 is what makes G-A2 mean
  something.

**If not met:** no architect fine-tune trains against this bar's dataset and no
architect-seat model bump deploys; the failing axis is named in the RESULTS doc;
re-grade only after a model or task-instrument revision (instrument revisions reopen
this doc *before* the next freeze, never silently).

## 4. Build-time calibration (sanctioned while PROPOSED; results recorded here)

| Item | Method | Result (2026-07-08) |
|---|---|---|
| Anchor catchability | Oracle graded per-axis | **4/4 groups fire on the Oracle**, one finding per flaw, none stuffed |
| Anchor disjointness | every alternate run over goals.md + repo-manifest.json | **Zero matches** (integrity-pinned per input) |
| Anti-stuffing carry-over | `stuffed-finding` fixture (4-group keyword salad) | **Credits zero groups**; with the threshold lifted it credits >2 — the rule is load-bearing |
| Paraphrase robustness | `paraphrase-catch` good fixture (no oracle wording) | **PASSES** — anchors are not oracle-string matching |
| Signature failure demo | `accepts-without-stress-test` fixture (approve on the flawed design) | **FAILS exactly** `test_verdict_is_revise` + `test_all_seeded_flaws_caught` |
| Input-pair identity | byte-compare goals/manifest across 001/002 | **CONFIRMED** identical; designs differ |

## 5. Accepted residuals — recorded so G-A gates are never overread

The anchor battery is a **detection floor**, not a completeness claim: a review may
catch genuine flaws the anchors do not encode (uncredited, harmless) or phrase a catch
outside every alternate (a miss under G-A2 — accepted; the paraphrase fixture bounds
the risk) · pattern-label *aptness* beyond the enum is unchecked (a MISSING_SEAM filed
as PHANTOM still credits its anchor group) · target grounding (does `target` name a real
design element?) is not machine-checked · severity/priority calibration is out of scope
· one authored domain (FoodReach) — domain generalization is future additive work ·
G-A3 binds the blocking verdict only; advisory wording inside `notes` (ignored key) is
unread. No negation heuristics, ever — transparent JSON checklists with no hidden logic.

## 6. Baselines (measured at build end, 2026-07-08 — not estimated)

| Measurement | Value |
|---|---|
| Full battery (`pytest tests/ tasks/`) | **275/275 green** (221 pre-existing + 54 additive: this suite's 22 integrity + coach-heldout's 22 + 10 per-task gate nodes across both new suites) |
| Frozen baseline byte-identical | **CONFIRMED** — `comm` diff of the Wave-0 221 node-id+verdict capture vs the final run = 0 lines lost, 54 added |
| Frozen files untouched | **CONFIRMED** — `git status` shows additive paths only; `git diff` over tracked files = empty |
| Oracle, arch-held-001 | 3/3 gate tests PASS (revise; 4/4 anchors; schema) |
| Oracle, arch-held-002 | 2/2 gate tests PASS (approve; schema) |
| Fixture floors (registered) | 001 = 5 broken + 2 good; 002 = 2 broken + 2 good — pinned in `tests/test_arch_verifier_integrity.py` |
| Taxonomy pin | definitions.yaml @ `ed2cfe5` ids + MISSING_SEAM, enum-tested |

## 7. RESULTS template (stub)

`RESULTS-arch-heldout-<date>.md`: serving model id + quant + template + review-seat tool
version + per-rep config records; per-task × per-rep table with per-axis (G-A1..G-A3)
verdicts; §3 verdict applied verbatim; freeze commit referenced; INVALID reps listed
with re-run evidence.

## 8. Freeze procedure

This doc is handed to Rich with the build → Rich amends §3 if needed and **freezes by
commit** (the commit that flips the Status line). Until then the verdict scope is
PROPOSED and gates nothing. After the freeze, the arch-FT precondition reads "suite
built + frozen; grade-pending" in WS4 §5 until a serving candidate's 6-rollout grade
lands.
