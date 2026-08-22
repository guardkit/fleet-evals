# PO Held-Out Suite — Feature-Spec/Plan Extension (FEAT-EVAL-SPEC, gate G2b)

**Status:** **FROZEN 2026-07-07 (Rich — thresholds G-S1..G-S5 accepted as proposed; this
commit is the freeze). REOPENED 2026-08-22 on the G-S5 axis only; RULED and RE-FROZEN the
same day — see G-S5 in §3.**
The reopening was deliberate and visible, per this document's own rule that instrument
revisions "reopen this doc *before* the next freeze, never silently". G-S1..G-S4 are
untouched and remain frozen. **G-S5 was re-pointed on Rich's ruling of 2026-08-22** at the
routing-law scenario coverage map — option 2 of the three put to him, in his words "a
better long term option" — and is measurable again. The reopened text and the three
options are kept below exactly as they were written, so the reasoning that led to the
ruling stays readable. The 008 task instrument was corrected the same day; no 008 grading run
has ever been recorded (`runs/po-heldout-spec/` holds 007 reps only), so no started run
is being retro-fitted. Acceptance given by Rich's instruction in the 2026-07-07
whole-factory analysis session (ai-transition); house convention: freeze = the commit
flipping this line. Pre-registration discipline verbatim from the frozen suites: the
freeze precedes any grading run (none has run); after a grading run starts, thresholds
are immutable; between candidates they may only be *raised*.
**Date:** 2026-07-07 (Claude Fable 5, WS1 Session H per
`ai-transition/docs/ws1-outer-loop-completion-build-plan-2026-07-07.md` §8)
**Repo:** fleet-evals · new suite `po-heldout-spec` (tasks `po-held-007-feature-spec`,
`po-held-008-feature-plan`)
**Relationship to the frozen suites:** strictly additive. `po-heldout-suite-scope.md`
(FROZEN 2026-07-03), `po-heldout-idea-extension-scope.md` (FROZEN 2026-07-05), tasks
po-held-001..006, `harness/po_contract.py`, `harness/grading.py`, `harness/idea_gates.py`,
`tests/test_verifier_integrity.py`, and `tests/test_idea_verifier_integrity.py` are never
edited. New tasks carry `suite = "po-heldout-spec"`; the runner's exact-match suite filter
excludes them from the frozen grades by construction. The frozen 105 verifier-integrity
node-verdicts re-ran byte-identical after this build (§6).
**Consumer (named):** **gate G2b — the FEAT-SPL-007/008 TARGET TERMINAL** (WS1 delta plan
§8/§12): the local `/feature-spec` → `/feature-plan` chain replacing the PLANNED-HANDOFF
terminal. G2b gates ONLY that terminal; the PLANNED-HANDOFF fallback needs only G2. This
verdict never gates the po-ft-v1 deploy (frozen §5's job) nor SPL G2 (idea extension's
job), and neither of those ever rescues a failed G-S gate.

---

## 1. Tasks

| Task | Tool under test | Artifact | Oracle |
|---|---|---|---|
| `po-held-007-feature-spec` | FEAT-SPL-007 `po_feature_spec`, headless `--auto`/SPL semantics, thin authored brief | three-file spec triple under `features/{slug}/` | authored minimal (licensing path exercised) |
| `po-held-008-feature-plan` | FEAT-SPL-008 `architect_feature_plan`, headless, pinned input spec triple | repo-root tree: feature YAML + task folder + Step-11-tagged spec copy | authored 5-task/4-wave plan |

**Amended 2026-08-22 (G-S5 ruling).** The 008 Artifact cell above still reads
"Step-11-tagged spec copy". That is the 2026-07-07 wording and is left standing as the
record; it is no longer the contract. The graded 008 artifact is the four-shape tree the
plan tool actually emits — `.guardkit/features/{FEAT-ID}.yaml` plus
`tasks/backlog/{slug}/{README.md, IMPLEMENTATION-GUIDE.md, TASK-*.md}` — and the feature
YAML must now carry the routing-law coverage map (`feature_files:` + `scenarios:`). No
`.feature` copy is required or expected; the tool's output grammar forbids one.

K = 3 reps per task, timeout 1800 s, grading via `PO_EVAL_OUTPUT_DIR` → per-task
`pytest test/ -q` (frozen-suite convention). **Runner divergence, by design:** answer
sheets are file TREES produced by the target-terminal harness (Session D,
specialist-agent), NOT by `harness/run_po_eval.py` (untouched — its artifact contract is
`response.txt`). Per-rep records must pin: serving model id + quant + template, the
FEAT-SPL-007/008 tool versions, the guardkit template/oracle pin, and the input SHAs.

## 2. Contract sources and instruments (pinned)

- **Grading contract:** `specialist-agent/docs/design/contracts/CONTRACT-feature-spec-plan-outputs.md`
  (WS1 Session B, 2026-07-07) — Part A (three-file spec contract) and Parts B+D
  (feature/task/wave YAML, frontmatter, plan-body obligations, round-trip fixtures).
  Guardkit pins: feature-spec.md @ `ce914f7c`, feature-plan.md @ `5ad48fcf`,
  feature_loader/task_types/bdd_linker @ main `28587b61`. Gold traces were used as
  SHAPE references only (both binding caveats honoured: pre-cutover traces; 008's
  oracle authored fresh against the post-2026-07-05 template, never harvested).
- **Deterministic plan oracle:** the installed `guardkit feature validate` CLI
  (resolves to the checkout @ `28587b61`, contract §0). Missing CLI = instrument
  error naming the pin, never a silent skip (`tests/test_spec_verifier_integrity.py`).
- **Invention anchors (007):** `test/reference/invention_anchors.json` — 6 groups, one
  per deliberate unknown in the authored brief (payment, notification-channel,
  membership-tier, cancellation-window, booking-limit, waitlist); idea-extension §2.1
  schema, §2.2 normalization, per-group licensing with the §2.4 anti-stuffing rule
  (threshold >2, imported from the frozen `idea_gates`), input-disjointness enforced.
  License source: manifest `assumption` statements (the canonical record of every
  inferred value; annotations are presentation of the same rows).
- **Domain-language banlist (007):** `test/reference/domain_language_banlist.json` —
  5 groups from the pinned template §Domain Language (http-status, sql, file-path,
  json-body, tech-internals), applied to STEP lines only; every group's firing
  direction demonstrated by the `implementation-language` fixture.
- **Pinned input spec (008):** authored triple at `input/features/member-directory-search/`,
  SHA-256-pinned (`input/INPUT.sha256`), structurally sane and untagged by integrity test —
  the byte-exact spec-preservation gate is computed against it via the pinned
  `bdd_linker.apply_mapping` insertion shape (standalone `@task:` lines only).
- **Routing-law contract (added 2026-08-22, the G-S5 re-pointing):** guardkit
  `installer/core/commands/feature-plan.md` — the "Required Fields" table
  (`feature_files`, `scenarios`) and "The Routing Law: `verifier:` stamps" section —
  as pinned by specialist-agent `templates/pins.py` under the name
  `feature-plan-methodology` (sha256 `20a3061159…`, `pinned_commit 3ad3a366`, 3,017
  lines). The closed verifier vocabulary and the Gherkin title lexer are **imported**
  from `guardkit.orchestrator.verifier_stamp` by `harness/spec_gates.py`, never copied,
  so the exam and the production feature loader cannot drift apart; a failed import is
  an instrument error naming the pin, never a silent skip. **Measured drift worth
  naming:** the contract's oracle pin is the guardkit checkout @ `28587b61`; the working
  checkout the CLI and the import both resolve to sat at `703734ee` on 2026-08-22. That
  drift pre-dates this lane and is recorded, not resolved, here.
- **Dependency posture (documented divergence):** `harness/spec_gates.py` uses PyYAML —
  guardkit's own parser (`feature_loader.py` `yaml.safe_load`) — for parse-parity with
  the oracle, rather than a hand-rolled YAML subset that could disagree with it. The
  frozen graders remain stdlib-only and untouched.

## 3. Pre-registered verdict (Rich amends then freezes; freeze precedes grading)

**Validity gate (verbatim from frozen §5):** all 6 rollouts (2 tasks × K=3) produced by
the pinned config with per-rep records; aborted/missing reps re-run in place, never
skipped — an incomplete run is **INVALID, not a failure**. A po-heldout-spec run never
reuses another suite's `--out` directory.

**G2b (target-terminal go-live) requires all of:**

- **G-S1 — Contract shape: 6/6 reps.** Every 007 rep emits exactly the three-file
  triple and passes the structural battery (`test_three_file_contract`,
  `test_gherkin_structure`, `test_single_line_steps`, `test_feature_header_block`);
  every 008 rep passes `guardkit feature validate` (exit 0) and the Step 8/9 folder
  contract (`test_guardkit_validate`, `test_readme_and_guide_present`). Zero tolerance
  is deliberate: an unparseable spec or invalid YAML stops the downstream terminal
  outright.
- **G-S2 — Gherkin discipline: 3/3 spec reps** pass `test_category_tags` (all four
  Specification-by-Example categories + non-empty @smoke set), `test_why_comments`,
  `test_domain_language` (banlist zero findings; no `# Implementation:` comments), and
  `test_scenario_floor` (≥8 scenarios). The banlist is a **detection floor**, not a
  completeness claim.
- **G-S3 — Assumption discipline: 3/3 spec reps** pass `test_auto_mode_discipline`
  (≥3 assumptions, every confidence `low`, every human_response `deferred` — the SPL
  propose-never-elicit pin — and `review_required: true`),
  `test_assumptions_manifest_schema`, `test_assumption_annotations`,
  `test_summary_coherence`, and `test_no_unlicensed_inventions` (zero anchor-detected
  unlicensed inventions — a detection floor binding exactly what the authored anchors
  detect; per-group licensing with anti-stuffing >2 carried over frozen).
- **G-S4 — Plan discipline: 3/3 plan reps** pass `test_task_frontmatter_discipline`
  (explicit valid task_type; id/feature_id/wave agreement), `test_mode_assignment`
  (task-work ≥4 / direct ≤3), `test_plan_structure_floor` (≥3 tasks, ≥2 waves),
  `test_mandatory_diagrams` (data-flow always; dependency graph at ≥3 tasks), and
  `test_lint_acceptance_criterion`.
- **G-S5 — Plan/spec coherence — RE-POINTED 2026-08-22 ON RICH'S RULING; MEASURABLE
  AGAIN.** The axis now reads: *3/3 plan reps pass `test_scenario_coverage_map` (the
  plan's own feature YAML declares `feature_files:` naming the pinned specification and
  a `scenarios:` map that stamps every scenario in it, keyed by the scenario's title
  copied verbatim, each with a verification home from the closed list, `toolchain` homes
  naming their test, and no `routing_law:` policy flag) and `test_spec_preserved_verbatim`
  (any copy of the specification in the tree is the pinned input plus inserted `@task:`
  lines and nothing else).* G-S5 claims coverage *discipline*, not routing *aptness* —
  whether `hurl` was the right home for a given scenario stays Coach territory (§5).

  **What this axis measures, in plain words.** Does the plan say which scenarios it
  covers and where each one will be proved — and is what it says true against the
  specification it was handed? A plan that says nothing fails. A plan that says something
  untrue fails, and the finding names the scenario.

  **AS FROZEN ON 2026-07-07 IT READ, VERBATIM — kept because a threshold's history is
  part of the threshold:** *3/3 plan reps pass `test_bdd_linkage_coherence` (every @task
  tag resolves; ≥1 scenario linked; every @smoke scenario linked; every feature-type task
  owns ≥1 scenario) and `test_spec_preserved_verbatim` (stripping the inserted `@task:`
  lines reproduces the pinned input spec byte-for-byte). G-S5 claims linkage *discipline*,
  not pairing *aptness*.*

  **THE HISTORY, KEPT VISIBLE.**

  | Date | What happened to this axis |
  |---|---|
  | 2026-07-07 | Frozen, grading Step-11 `@task:` scenario tagging. Correct on the day. |
  | 2026-07-09 | The headless plan tool this exam actually grades is created. It never implemented Step 11, and its output grammar FORBIDS emitting a `.feature` file — a model obeying the old instruction had its whole plan discarded. |
  | 2026-08-14 | Rich retires Step 11 (guardkit `a87862ef`, BDD-replacement card Q10). The template reads "RETIRED. DO NOT RUN". The same ruling creates the routing law, the successor mechanism. |
  | 2026-08-22 am | The exam is corrected so the check stops erroring. **This made it worse:** with nothing to grade it SKIPPED, `harness/run_po_eval.py:255` grades a rep by `proc.returncode == 0`, and **pytest exits 0 when tests skip** — so the axis would have been recorded GREEN while measuring nothing. This document was reopened on that, visibly, with three options for Rich. |
  | 2026-08-22 pm | **Rich rules: option 2.** The axis is re-pointed at the coverage map, the reference answer and the fixture battery are brought up to it, and the skip is closed. |

  **The three options that were put to him, kept for the record.** (1) Strike the linkage
  half and keep only spec-preservation — cheapest, leaves coverage ungraded. (2) Re-point
  the axis at the routing-law successor the current template already specifies, which the
  plan tool CAN emit and needs no grammar change — "the option that restores real teeth".
  (3) Un-retire Step 11 — rejected on this lane's read: it re-arms the oracle Rich
  deliberately disarmed. **HE CHOSE (2).**

  **A CLAIM IN THE REOPENED TEXT WAS WRONG AND IS CORRECTED HERE.** The 2026-08-22
  morning entry said "Measured 2026-08-22: today's drives emit neither key". That was
  measured on ONE run — the exam drive against this task's own pinned spec — and
  generalised. Re-measured across all eleven captured planning runs of that morning
  (`ai-transition/docs/evidence/architect-plan-drives-2026-08-22/`): **ten of the eleven
  emit both keys.** The exam drive is the only one that emits neither. So the tool does
  this routinely; the requirement is not a new capability being demanded of it, it is an
  existing behaviour being made non-optional. What remains true is that forge TOLERATES
  the omission rather than requiring it (`declare_feature_files_if_absent` fills the key
  in), so nothing outside this exam forces the map today.

  **WHAT WAS LOST AND HAS NO SUCCESSOR, stated plainly rather than glossed.** The retired
  tags named a TASK per scenario, so the axis could ask "does every task named exist?"
  and "does every task own a scenario?". The routing-law map has **no task field** — its
  stamp schema (`ScenarioStamp`, `extra="forbid"`) allows exactly `verifier`, `test_ref`,
  `test_paths` — because the law replaced task-ownership with verification-home
  ownership. Those two questions are **no longer asked by this exam**. The nearest
  surviving task-side check is the task-frontmatter `verifier:` stamp, which IS graded.

  **THE SKIP IS CLOSED TWICE OVER.** (a) The new check cannot skip: a plan with no
  coverage map fails it. (b) `tasks/po-held-008-feature-plan/test/conftest.py` refuses to
  let ANY skip in this task's grade exit 0 — it names the skipped checks and returns exit
  code **40**, deliberately outside pytest's own range (0/1/2/3/4/5) so "could not
  measure" is distinguishable from "measured and failed", while every existing
  `returncode == 0` check treats it as the failure it is. Proved by running it, on a plan
  of exactly the shape today's tool produces (the reference answer with no spec copy and
  no coverage map): **this morning's instrument → 8 passed, 1 skipped, exit 0 (recorded
  as PASSED); this afternoon's → 8 passed, 1 failed, exit 1.**

  **THE REFERENCE ANSWER FAILED THE NEW BAR.** `solution/` was authored 2026-07-07, five
  weeks before the routing law existed, and carried neither key. The bar was **not**
  weakened to fit it; the reference was brought up to the current contract by appending
  the coverage map (nine scenarios, titles copied from the pinned input, `toolchain` homes
  each naming their test). Nothing else about it changed, and the pinned input triple and
  its checksums are untouched. The same map was appended to all eighteen 008 fixtures so
  each still fails only for its own defect.

**If not met:** the target terminal does NOT go live on this model — FEAT-SPL-007/008
stay behind the PLANNED-HANDOFF fallback (which needs only G2); the failing axis is
named in the RESULTS doc; re-grade only after a model or task-instrument revision
(instrument revisions reopen this doc *before* the next freeze, never silently).
**Session-H clarification (WS1 plan §8):** this build flips G2b to "built"; G2b **PASS**
additionally requires the serving model's grade under this §3 — not this session's job.

## 4. Build-time calibration (sanctioned while PROPOSED; results recorded here)

| Item | Method | Result (2026-07-07) |
|---|---|---|
| Anti-stuffing threshold (>2, inherited) | Frontier 007 sheet graded; compound-licensing fixture at score 2 | **No raise needed.** Frontier sheet has no compound statements; the 2-group compound fixture licenses both (at threshold); the synthetic 3-group salad voids (`test_stuffed_statement_licenses_nothing`) |
| Banlist false-positive sweep | Banlist run over both authored oracles + the 16-scenario frontier sheet | **Zero findings** on legitimate domain-language steps; all five groups fire on the implementation-language fixture |
| Scenario floor (≥8) | Oracle 11, frontier 16, gold thin-input traces 23/32; stub 3 | **≥8 CONFIRMED** — separates stub from minimal-legitimate with margin |
| Plan floors (≥3 tasks / ≥2 waves) | Oracle 5/4, frontier 6/4, minimal-plan good fixture exactly 3/2; collapsed 2/1 and stub 1/1 fail | **Floors CONFIRMED at the boundary** (minimal-plan passes; collapsed/stub fail) |

## 5. Accepted residuals — Coach territory, recorded so G-S gates are never overread

Full official-Gherkin grammar beyond the purpose-built parser floor (the serving tool
runs `feature_spec_normalize` itself; the gate re-checks the load-bearing single-line
invariant + structure) · scenario/step *semantic* quality and boundary-pair completeness
per documented bound · synonym/paraphrase evasion outside the authored anchors and
banlist · assumption posture quality (falsifiable-shape is forced; wisdom is not) ·
scenario→task pairing aptness (G-S5 checks structure) · task sizing/decomposition taste
beyond the floors · §4 Integration Contracts and the complexity-conditional sequence
diagram (input-dependent) · smoke_gates authoring (warn-mode nudge at serving). No
negation heuristics, ever — transparent JSON checklists with no hidden logic.

## 6. Baselines (measured at build end, 2026-07-07 — not estimated)

| Measurement | Value |
|---|---|
| Verifier integrity, total | **161/161 green** (105 frozen + 56 additive: 2 Oracles + 31 broken-fixture cases auto-discovered by the frozen file + 23 spec-integrity tests) |
| Frozen baseline byte-identical | **CONFIRMED** — `comm` diff of the Wave-0 105 node-id+verdict capture vs the final run = 0 lines |
| Frozen files untouched | **CONFIRMED** — `git diff` over the full frozen surface (tasks 001..006, frozen harness modules, frozen test files, frozen scope docs) = empty |
| Frontier sheet, po-held-007: per-axis | **13/13 PASS** (16 scenarios, boundary pairs for both assumed limits, 6 low/deferred assumptions, licensed anchored specifics) |
| Frontier sheet, po-held-008: per-axis | **9/9 PASS** (6 tasks / 4 waves incl. documentation task, full diagrams, complete Step-11 linkage, guardkit validate exit 0) |
| Deliberately-stubbed sheets FAIL (owning gates named) | 007 `stub-sheet` → exactly `test_scenario_floor` + `test_auto_mode_discipline` + `test_category_tags`; 008 `stub-plan` → exactly `test_plan_structure_floor` + `test_bdd_linkage_coherence` + `test_mandatory_diagrams` (both stubs are otherwise well-formed — the 008 stub is even guardkit-VALID, proving the YAML oracle alone cannot catch effort-dodging) |
| Fixture floor lists (registered) | Pinned in `tests/test_spec_verifier_integrity.py`: 007 = 17 broken + 6 good; 008 = 14 broken + 4 good |
| guardkit oracle identity | installed CLI resolves to checkout @ `28587b61` (contract §0), verified by round-trip in `test_guardkit_validate` Oracle run |

## 7. RESULTS template (stub)

`RESULTS-po-heldout-spec-<date>.md`: serving model id + quant + template + tool
(FEAT-SPL-007/008) versions + guardkit pin + per-rep config records; per-task × per-rep
table with per-axis (G-S1..G-S5) verdicts; §3 verdict applied verbatim; freeze commit
referenced; INVALID reps listed with re-run evidence.

## 8. Traceability map (gate axes → owning tests/fixtures)

| Axis | Owning tests | Firing demos (broken) | Pass demos (good) |
|---|---|---|---|
| Three-file contract | `test_three_file_contract` | missing-summary, extra-files | all 007 good |
| Gherkin structure + BOM | `test_gherkin_structure` | bom-file | outline-and-docstring |
| Single-line steps | `test_single_line_steps` | wrapped-step | outline-and-docstring (sanctioned multi-line forms) |
| Header block | `test_feature_header_block` | header-drift | frontier-baseline |
| Category tags / smoke set | `test_category_tags` | missing-category-tag, stub-sheet | frontier-baseline |
| # Why annotations | `test_why_comments` | missing-why | box-drawing-dividers |
| Domain language | `test_domain_language` | implementation-language (all 5 groups fire) | frontier-baseline |
| Manifest schema + referential integrity | `test_assumptions_manifest_schema` | manifest-enum-drift, dangling-scenario-ref | frontier-baseline |
| Annotation agreement | `test_assumption_annotations` | annotation-missing | licensed-per-group |
| SPL --auto discipline | `test_auto_mode_discipline` | confident-assumptions, stub-sheet | frontier-baseline |
| Summary coherence | `test_summary_coherence` | summary-count-mismatch | extra-summary-rows (additive rows allowed) |
| Invention licensing | `test_no_unlicensed_inventions` | unlicensed-invention, unlicensed-all-groups (all 6 fire), stuffed-license | licensed-per-group, compound-licensing (at threshold) |
| Scenario floor | `test_scenario_floor` | stub-sheet | frontier-baseline |
| YAML oracle | `test_guardkit_validate` | schema-mutant, struct-mutant | extra-yaml-keys (extra='ignore') |
| Frontmatter discipline | `test_task_frontmatter_discipline` | missing-task-type, wrong-wave | alias-task-type (aliases valid) |
| Mode assignment | `test_mode_assignment` | mode-mismatch | frontier-baseline |
| Plan floors | `test_plan_structure_floor` | collapsed-plan, stub-plan | minimal-plan (exactly at floor) |
| Folder contract | `test_readme_and_guide_present` | no-guide | frontier-baseline |
| Mandatory diagrams | `test_mandatory_diagrams` | no-diagrams, stub-plan | frontier-baseline |
| Lint criterion | `test_lint_acceptance_criterion` | missing-lint-criterion | frontier-baseline |
| Scenario coverage map (re-pointed 2026-08-22; was "Linkage coherence" / `test_bdd_linkage_coherence`, whose firing demos were dangling-task-tag, untraced-feature-task, missing-smoke-link, stub-plan) | `test_scenario_coverage_map` | no-coverage-map, paraphrased-scenario-key, unknown-verifier-home, bare-toolchain-stamp, feature-files-wrong-path, routing-law-emitted, dangling-task-tag, missing-smoke-link, untraced-feature-task | frontier-baseline, minimal-plan, alias-task-type, extra-yaml-keys |
| Spec preservation | `test_spec_preserved_verbatim` | spec-rewritten | all 008 good (tag-insertion-only) |

## 9. Freeze procedure

This doc is handed to Rich with the build → Rich amends §3 if needed and **freezes by
commit** (the commit that flips the Status line). The frozen thresholds ride with the
RESULTS doc. The frozen suites' own docs are untouched throughout. After the freeze,
G2b reads "built + frozen; grade-pending" in the WS1 gate table until the serving
model's 6-rollout grade lands.

---

## 10. Calibration of the re-pointed G-S5 axis (measured 2026-08-22, the ruling lane)

Sanctioned by §4's precedent: calibration is recorded here, and it is recorded whether or
not it flatters the change. **No grading run of the frozen suite has started, so no
pre-registered threshold is being altered after the fact.**

### 10.1 The instrument's own battery

| Measurement | Result |
|---|---|
| 008 fixture battery | **20 broken / 4 good** (was 14/4). Every broken fixture fails, and every one fails the check its `meta.json` names. Every good fixture passes. |
| Reference answer (`solution/`) | **9/9 pass** after the coverage map was appended (see §3 G-S5 — it failed before, and that failure is a finding, not a calibration). |
| Instrument integrity (`tests/test_spec_verifier_integrity.py`) | **31 passed** |
| Frozen integrity file, 008 cases (`tests/test_verifier_integrity.py -k po-held-008`) | **21 passed** |
| Frozen surfaces (tasks 001–006, `po_contract.py`, `grading.py`, `idea_gates.py`, `test_verifier_integrity.py`, `test_idea_verifier_integrity.py`, `run_po_eval.py`, the frozen scope docs) | **untouched — `git status` shows no change to any of them** |
| po-held-007 gate | **17 passed** — unaffected by the shared `spec_gates` change |

Two of the new checks are **independently corroborated**: `bare-toolchain-stamp` and
`unknown-verifier-home` also fail `test_guardkit_validate`, i.e. guardkit's own CLI
refuses those stamps at load with no involvement from the exam.

### 10.2 The skip that scored green — before and after, on one tree

The tree: the reference answer with no specification copy and no coverage map, which is
exactly the shape the current plan tool produces.

| Instrument | pytest result | Exit code | What a runner records |
|---|---|---|---|
| 2026-08-22 morning | 8 passed, 1 **skipped** | **0** | **PASSED** |
| 2026-08-22 afternoon (this lane) | 8 passed, 1 **failed** | **1** | FAILED |

And with a deliberately unmeasurable check added to the grade, to prove the guard itself
rather than only the new bar: morning instrument → 9 passed, 1 skipped, **exit 0**;
this lane's → same tests, **exit 40** with a named `COULD NOT MEASURE` block.

### 10.3 The bar run against eleven real planning runs (off-exam)

Every architect planning run captured on 2026-08-22
(`ai-transition/docs/evidence/architect-plan-drives-2026-08-22/`), graded by
`harness/grade_coverage_map.py`, which calls the **same** `coverage_map_findings` the
exam's fifth bar calls, against each run's **own** specification (carried in its request
as `spec_feature`). Ten of the eleven are plans for other features, so the exam's own
pytest gate cannot be pointed at them; this is the widest independent test of the
instrument available without a model.

| Run | Scenarios in its spec | Entries in its map | Verdict |
|---|---|---|---|
| drv-01-uptcount | 6 | 6 | PASS |
| drv-02 | 4 | 4 | PASS |
| drv-03 | 11 | 11 | PASS |
| drv-04 | 14 | 14 | PASS |
| drv-05 | 18 | 18 | PASS |
| drv-06 | 18 | 18 | PASS |
| **drv-07** | 27 | 27 | **FAIL** — 5 titles written in the plan's own words, so 5 real scenarios have no verification home |
| drv-08 | 19 | 19 | PASS |
| drv-09 | 27 | 27 | PASS |
| drv-10 | 25 | 25 | PASS |
| **exam-r2** (the 008 exam drive) | 9 | 0 | **FAIL** — no `feature_files:`, no `scenarios:` at all |

**9 of 11 pass.** This was not the expected result and it matters three ways.

1. **False-positive sweep.** 142 scenarios across nine plans and four unrelated feature
   specifications produced **zero findings**. The verbatim-title rule does not fire on
   legitimate maps.
2. **The requirement is not new work for the tool.** It emits this map routinely. The
   ruling makes an existing behaviour non-optional; it does not demand a new capability.
3. **The one real defect the bar caught is invisible without it.** drv-07's plan stamps
   27 entries and looks complete, but five of them are the model's own phrasing rather
   than the specification's titles — so five scenarios are silently unverified while the
   plan reads as fully covered. For example the plan wrote *"Partial write must not leave
   corrupted episodes in the graph"* where the specification says *"Metrics write
   interrupted mid-operation does not leave partial episodes"*. Both the coach score
   (0.935) and `guardkit feature validate` pass that plan.

**Honest scope note.** These eleven runs are the same seat on the same morning; they are
not reps of this exam and they are not a grade of any model. They calibrate the
instrument, nothing more. And nine of eleven passing says the bar is not a rubber stamp
only because the two failures are real — it is not evidence that the bar is hard.

### 10.4 The one measurement this lane could not make — DESIGNED, NOT RUN

**Not run because the GPU was not this lane's to use** (another lane held ~100 GB of the
box's memory throughout). No model was loaded, no server was started or stopped, nothing
was trained. Everything in §10.1–§10.3 was measured off-line from files.

**The open question.** Ten of eleven captured runs emit the coverage map and one — the
run against this exam's own pinned specification — does not. That could be run-to-run
variation, or it could be something about this specification (nine scenarios, four
category tags, three low-confidence assumptions) that makes the seat drop the map. Three
fresh reps against the same input would answer it, and G-S5 needs 3/3 anyway.

**Run it like this when the box frees.** Each rep needs its own correlation id — replies
on `agents.result.architect-agent` were measured arriving twice on 2026-08-22, so a
reused id can collect a stale duplicate:

```bash
cd ~/Projects/appmilla_github/ai-transition/docs/evidence/architect-plan-drives-2026-08-22

for REP in 1 2 3; do
  python3 - "$REP" <<'PY'
import json, sys
p = json.load(open("exam-r2.payload.json"))
p["payload"]["correlation_id"] = f"exam-r3-rep{sys.argv[1]}"
json.dump(p, open(f"/tmp/exam-r3-rep{sys.argv[1]}.payload.json", "w"))
PY
  ./run_drive.sh /tmp/exam-r3-rep$REP.payload.json /tmp/exam-r3-rep$REP.reply.json 900
  python3 exam_materialise.py /tmp/exam-r3-rep$REP.reply.json /tmp/exam-r3-rep$REP-tree
done

cd ~/Projects/appmilla_github/fleet-evals/tasks/po-held-008-feature-plan
for REP in 1 2 3; do
  echo "--- rep$REP"
  PO_EVAL_OUTPUT_DIR=/tmp/exam-r3-rep$REP-tree python3 -m pytest test/ -q
  echo "exit $?   (0 = pass · 1 = failed a bar · 40 = a bar could not measure)"
done
```

**How to read the result.** 3/3 exit 0 ⇒ G-S5 met on this model. Any rep exiting 1 with
`test_scenario_coverage_map` named ⇒ the axis fails, and the finding names the scenario.
Any rep exiting **40** ⇒ COULD NOT MEASURE — never write that down as a pass.
