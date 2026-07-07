# PO Held-Out Suite — Feature-Spec/Plan Extension (FEAT-EVAL-SPEC, gate G2b)

**Status:** **PROPOSED — awaiting Rich's freeze.** Thresholds below are proposed by the
build session (2026-07-07) and are frozen only by Rich's commit flipping this line
(house convention: freeze = the commit). Pre-registration discipline verbatim from the
frozen suites: the freeze must precede any grading run; after a grading run starts,
thresholds are immutable; between candidates they may only be *raised*.
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
- **G-S5 — Plan/spec coherence: 3/3 plan reps** pass `test_bdd_linkage_coherence`
  (every @task tag resolves; ≥1 scenario linked; every @smoke scenario linked; every
  feature-type task owns ≥1 scenario) and `test_spec_preserved_verbatim` (stripping the
  inserted `@task:` lines reproduces the pinned input spec byte-for-byte). G-S5 claims
  linkage *discipline*, not pairing *aptness* (whether a scenario truly belongs to that
  task is Coach/judgment territory).

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
| Linkage coherence | `test_bdd_linkage_coherence` | dangling-task-tag, untraced-feature-task, missing-smoke-link, stub-plan | frontier-baseline, minimal-plan |
| Spec preservation | `test_spec_preserved_verbatim` | spec-rewritten | all 008 good (tag-insertion-only) |

## 9. Freeze procedure

This doc is handed to Rich with the build → Rich amends §3 if needed and **freezes by
commit** (the commit that flips the Status line). The frozen thresholds ride with the
RESULTS doc. The frozen suites' own docs are untouched throughout. After the freeze,
G2b reads "built + frozen; grade-pending" in the WS1 gate table until the serving
model's 6-rollout grade lands.
