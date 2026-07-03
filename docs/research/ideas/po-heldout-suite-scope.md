# PO Fine-Tune Held-Out Suite — Scope (Phase POH)

**Status:** **FROZEN 2026-07-03** (Rich; thresholds accepted as proposed). Freeze lineage: original freeze commit `6f9b9b7` (14:33 BST) was **superseded same day by a history rewrite** — the suite had committed FinProxy client documents into this repo, which sat PUBLIC on `github.com/guardkit/fleet-evals` for ~80 minutes (0 forks/stars/watchers observed; repo made private ~14:55). Remediation: all client-derived payloads (3× corpus copies, April-derived oracles/fixtures, coverage checklists) externalized to the FinProxy org (`lpa-project-docs` → `eval-assets/po-heldout/`, mirrored layout), pinned by `harness/ASSETS.sha256` (88 files) and symlinked in via `harness/link_assets.py`; history rebuilt from the clean root without client content. **§5 re-landed byte-identical to `6f9b9b7`** (diff-verified) — the thresholds have been frozen continuously since 14:33. Also folded in: the 4 runner defects from the pre-freeze adversarial review, fixed in `harness/run_po_eval.py`. Residual name-level references (client name, corpus filenames in manifests/instructions) remain by policy — content externalized, names tolerated while this repo stays private. Originally DRAFT (Claude Code-authored 2026-07-03, verified from source same day). Suite built same session (§4) — the ideation-work-order build-plan step was deliberately collapsed into the same-session build for a suite this small; baseline numbers in §5.1 are measured, not estimated. Suite red-teamed same session (3 adversarial reviewers: grader evasion, contract fidelity, scope consistency); all proven findings fixed and each fix owns a fixture in the verifier-integrity battery.
**Date:** 2026-07-03
**Repo:** fleet-evals (this repo — substrate home confirmed in `../fleet-memory/docs/research/ideas/phase-ablation-build-plan.md`)
**Contract:** task-folder contract per `../fleet-memory/docs/research/ideas/phase-ablation-scope.md` §3.2, **doc-shaped variant** (no Docker: `input/` replaces `environment/`; grading runs local pytest on the candidate's written output, not container state)
**Decision frame:** DF-001 (local, deterministic, no cloud on the critical path) · DF-006 (golden-set philosophy — deterministic yardstick, not a shared LLM oracle) · phase-ablation scope §6b (every fine-tune gets a pre-registered held-out suite on this contract *before deployment*)
**Consumer (named):** the **deploy / no-deploy decision for po-ft-v1** — the Gemma-4-26B QLoRA product-owner fine-tune coming out of the dataset-factory run (PLAN-po-dataset-generation §7 Phase 4). Secondary consumer: phase-ablation §6c — the suite's verifier-integrity fixtures join the permanent regression corpus.

---

## 1. Objective

A **pre-registered, deterministic deployment gate** for the incoming PO fine-tune: doc-shaped tasks graded by pytest on **schema validity** and **coverage-vs-reference**, with thresholds frozen by Rich **before** the fine-tune is graded against them. Per §6b of the ablation scope: the suite exists before the bulk-generation run completes, or the fine-tune's success is the next unmeasured belief.

Why deterministic: the training pipeline's only gate today is the golden set scored by an LLM Coach (`score_golden_set.py`) — there is **no mechanical schema validation anywhere in the pipeline** (verified from source, §2). Grading the fine-tune solely with an LLM judge is the shared-oracle problem that retracted phase-ablation v1; this suite is the independent instrument. It complements — does not replace — the golden-set gate: judgment quality (assumption posture, trap behaviour) stays with the Coach harness; **shape, grounding, and coverage move to pytest**.

## 2. Current state (verified from source 2026-07-03)

| Component | State (verified) |
|---|---|
| The fine-tune (po-ft-v1) | Not yet trained. Base `gemma4-26b` (Gemma-4-26B-A4B-IT MoE, `UD-Q4_K_XL` on llama-swap :9000), Unsloth QLoRA SFT, chat template `gemma-4`. Serving contract (Decision A 2026-07-02): `<think>…</think>` + **one json-fenced object** that `ProductOwnerOutputHandler.parse()` accepts. Drops into specialist-agent's `product-owner` role unchanged. RAG-out day-one (ADR-FLEET-002) |
| Training pipeline status | Phase 0 (golden set + base diagnosis) concluded 2026-07-02 — base is strong (0/11 trap false-confidence in all three runs); fine-tune emphasis = **reinforcement + serving-shape fluency**, not judgment repair. Phase 1 (factory generative mode) concluded 2026-07-03 (6/6 smoke). Phase 3 bulk generate = the long GB10 run (pilot live since 08:00 today); Phase 4 = train + gate on golden set |
| Existing gate instrument | `agentic-dataset-factory/domains/product-owner/score_golden_set.py` — LLM-Coach-graded (9 behaviour criteria from GOAL.md), only mechanical check is a `<think>` substring flag. Golden set: 19 items, **2 of 6 modes only** (greenfield + extract), all single-turn, 15/19 assumption traps. It is the **training-time** gate (Phase 4 gates on it) — not held out from the training loop's own design pressure |
| Output schemas | Pinned verbatim from specialist-agent source: `ProductRoadmap`/`Epic`/`FeatureSpecInput` (`src/specialist_agent/roles/product_owner/types.py:80-320`), `EpicPlan`/`EpicStub`/`FeatureStub` (`phased_extraction.py:107-217`), `EnrichmentBatch`/`FeatureEnrichment` (`phase_b_delta.py:22-144`), `SourceCitation` (`types.py:33-77`), `SourceDocument`/`Assumption` (`roles/architect/types.py:40-134`). All validators enumerated in `harness/po_contract.py` with file:line provenance. Parse flow: think-strip then `_extract_json` fence cascade (`handler.py:535-609`); Phase B is bare-`json.loads` + quote-truncation repair (`session.py:1121-1135`) |
| Reference corpus: input docs | `lpa-project-docs/research/` — 13 FinProxy markdown files, 283,586 chars as pinned (the session log's own `total_chars`: 284,576), exactly the `files_read` of the April run's session log. Copied + SHA-256-pinned into each task's `input/corpus/` |
| Reference corpus: April PO outputs | Phased extract run of 2026-04-21/22 (base specialist-agent PO, `llm_provider=openai`), surviving at `~/finproxy-archive-backup/specialist-agent-pre-cleanup-2026-05-02/output/lpa-research/` (identical copy at `~/Projects/Appmilla/FinProxy/lpa-research/`): `epic_plan.json` (8 epics, 36 stubs, 55 quoted citations, contract-clean), `enriched_roadmap.json` (full ProductRoadmap shape, 36 features), session log (final_score 0.865, 1 iteration). **Known defect found during verification:** `FEAT-PO-032` cites the non-existent `FinProxy-Achitecture-Exploration.md` (misspelled) — a real `FABRICATED_SOURCE_REFERENCE` in accepted April output, kept as a verifier-integrity fixture (§3.5). Earlier single-pass run of 2026-04-14 survives only as its review doc |
| Reference corpus: manual build plan | `lpa-platform/docs/buildplan.md` (Rich, 2026-04-10): 7 bounded contexts with concept-level feature lists — the coverage reference. Comparative review `lpa-platform/docs/reviews/po-agent-extract-vs-manual-buildplan-review.md` (2026-04-14): ~65% coverage, both total gaps traced to docs missing from the input corpus |
| Corpus grounding of the 7 reference BCs | Verified doc-by-doc: LPA Management, Open Banking, Behavioural Intelligence, Escalation, Audit & Compliance — grounded (multiple docs each). Identity & Access — grounded at tech-selection/requirements level only (Keycloak/OIDC in Tech-Stack docs, RBAC in Data-Architecture §8, FAPI/2FA in Regulatory-Compliance). Fleet Integration — **split**: NATS/event-driven messaging grounded in 4 docs; the "fleet capability" half appears in zero corpus files → excluded from required coverage (requiring it would reward fabrication) |
| Hold-out integrity | FinProxy appears nowhere in the training loop: harvest = guardkit/forge/jarvis/specialist-agent/study-tutor repos; golden set seeded from those harvests + synthetic briefs; Phase 3 generation walks the GOAL.md book taxonomy. April outputs were produced by the *old* OpenAI-player PO, not the model under test. **Constraint registered in §7: FinProxy docs and these April outputs must never enter Phase 2/3 seed data** |

## 3. Design

### 3.1 Task-folder contract (doc-shaped)

```
tasks/<task-id>/
  task.toml         # id, mode/phase, schema, expected artifact, timeout, K reps, grading command
  instruction.md    # the prompt for the model under test (mode framing + output contract), provenance-pinned
  input/            # corpus/ (13 docs + MANIFEST.sha256) and any phase inputs (e.g. epic_plan.json for Phase B)
  test/             # pytest graders (schema validity, grounding, coverage-vs-reference) + reference/ checklists
  solution/         # Oracle output (April-derived or authored; provenance + any repairs in PROVENANCE.md)
```

Identical to ablation §3.2 minus `environment/` (no Docker — the artifact under test is a document, not container state). Candidate output is graded from `$PO_EVAL_OUTPUT_DIR/response.txt` (raw model text, think block included); Oracle validation runs the same tests with `PO_EVAL_OUTPUT_DIR=<task>/solution/`. Tasks live under `tasks/<id>/` per the ablation build plan's files table; they cohabit with GuardKit's kanban dirs (`backlog/`, `in_progress/`, …), which are managed state, not eval tasks.

Grading is **stdlib + pytest only** (no pydantic, no network): every schema rule is re-implemented in `harness/po_contract.py` faithful to the pinned Pydantic source, so the gate runs anywhere Python 3.12+ runs and cannot drift silently — drift shows up as a verifier-integrity failure (§3.5).

### 3.2 Tasks — N = 4 graded tasks + verifier-integrity meta-suite

| Task | Mode/phase | Schema | Oracle | What it gates |
|---|---|---|---|---|
| `po-held-001-extract-phase-a` | phased extract, Phase A | `EpicPlan` | April `epic_plan.json` (contract-clean as found) | stub discipline (no enrichment leak), citations quote ≤200 + section_path, cited_docs grounding, epic coverage vs reference |
| `po-held-002-extract-phase-b` | phased extract, Phase B (EPIC-006 Open Banking) | `EnrichmentBatch` | reconstructed from April enriched features of EPIC-006 | delta contract: feature_id allowlist, no title/bounded_context, ≥2-sentence descriptions, non-empty grounded source_documents, exact enum Literals, enrichment completeness |
| `po-held-003-extract-full` | single-pass extract (the Decision-A serving shape) | `ProductRoadmap` | April `enriched_roadmap.json`, **repaired** (fabricated citation fixed; repairs logged in PROVENANCE.md) | full roadmap validity incl. feature_spec_inputs flatten-match, SourceDocument objects, assumptions shape, citation grounding, coverage-vs-reference |
| `po-held-004-greenfield-discipline` | greenfield (no corpus) | `ProductRoadmap` | authored minimal roadmap | mode-aware discipline: `coverage_score=null`, **empty** source_documents/citations at every level (empty is correct — the Phase-0 mis-scoping lesson), ≥3 falsifiable-shape assumptions |

Extract gets three of four tasks because extract is the deployment mode with real stakes (it is what `/po-*` serves against actual product corpora) and the only mode with a human reference. Greenfield is the second-trained mode and the one whose correct behaviour is *emptiness* — cheap to gate deterministically, embarrassing to get wrong. The four ungated modes (idea/evolve/impact/scope) are explicitly out of scope (§7) — they have zero golden-set items and zero reference corpus; gating them here would be pretend coverage.

### 3.3 Grading axes (all deterministic)

1. **Serving shape**: raw output contains exactly one well-formed `<think>…</think>` block (counted **fence-aware** — literal think tags inside the JSON payload are content, per `think_block.py:120-132`); the remainder's **first JSON object parses via the pinned runtime cascade** (whole-text → first fence → leading bare-object, faithful to `handler.py:557-604` / `session.py:1121`, including the runtime's tolerance of trailing echo text after the first fence). Mode pinning (extract/greenfield per task) is asserted alongside.
2. **Schema validity**: the full validator battery from §2's schema row — required fields, exact enum Literals (including `"Easy (≈1d)"` U+2248 and `"Won't"` ASCII apostrophe), ≥2-sentence descriptions (same regex as source), ≥1 epic / ≥1 feature per epic, feature_spec_inputs flatten-match, citation rules (section_path ≥1, quote ≤200 — except Phase B, where serving truncates-and-repairs overlong quotes and the gate follows; line_end ≥ line_start), `phase_a_completed_at` ISO-8601 when present. Unique feature_ids: source-enforced for EpicPlan/EnrichmentBatch; CONTRACT-tightened for ProductRoadmap (duplicates collide in the written `feature_spec_inputs/<id>.md` artefacts).
3. **Grounding**: every cited document name — `cited_docs`, stub `source_citations[].document`, feature `source_documents[]` (**every string entry, no extension heuristic**), `field_citations` values, top-level `source_documents[].filename` — must exactly match a file in `input/corpus/MANIFEST.sha256`. This is the deterministic core of `FABRICATED_SOURCE_REFERENCE` / `grounding_fidelity`, and it catches the exact defect class the April run shipped. Quote/section *content* fidelity (a real filename with an invented quote) is a Coach axis, not graded here.
4. **Coverage-vs-reference**: `test/reference/coverage_checklist.json` derives from the manual build plan's 7 BCs, corpus-grounding-filtered (§2). Five **required** areas (LPA Management, Open Banking, Behavioural Intelligence, Escalation, Audit & Compliance) + two **stretch** areas reported non-gating (Identity & Access, NATS/event-driven messaging — grounded but the April baseline itself misses both; gating above the baseline is a §5 freeze decision, not an author decision). An area counts covered when ≥2 distinct anchor patterns match **and the matches span ≥2 distinct epics/features** — a single keyword-stuffed field cannot cover an area (red-team hardening). Anti-collapse floors (the Phase-1 smoke's "1 epic / 1 feature" thinness watch item): minimum epic and feature counts pinned in §5.
5. **Phase-B discipline**: dispatcher gates mirrored from `phased_extraction.py:540-733` — epic_id match, allowlist, enrichment completeness (≥3 of the 7 metadata fields populated on ≥1 enrichment; empty strings/lists/dicts count as absent, per `_is_populated`). This is a **batch-level floor, faithful to the serving dispatcher** — per-enrichment completeness is Coach territory.

**Deliberate gate-vs-serving divergences** (all gate-stricter, each documented at its rule in `harness/po_contract.py`): think block required (serving parses without one; Decision A makes it the fine-tune's shape); stub ENRICHMENT_LEAK hard-fails (serving prompt calls it advisory, Pydantic drops it); `intent` ≤100 chars (contract doc, not code); `cited_docs` non-empty (contract doc: "hard failure"); `project_name` required (serving injects it); ProductRoadmap duplicate feature_ids rejected (artefact collision). No axis is gate-laxer than serving.

What is **not** graded here, deliberately: assumption *quality*, trap posture, prioritisation judgment, decomposition taste, citation-content fidelity — LLM-judgment axes that stay with the golden-set Coach gate (PLAN §7 Phase 4). One suite per instrument; neither rescues the other.

### 3.4 Repetitions and runner

K = **3 reps per task** (nondeterministic sampling; same rationale as ablation §3.4), fresh session per rep, pinned model id + quant + temperature + template, config recorded per rep alongside `response.txt`. 12 rollouts total — small enough to run on a lunch break, large enough to catch shape flakiness, which is the axis this fine-tune exists to fix. The runner is whatever invokes the model (specialist-agent role or bare llama-swap call with `instruction.md`); the suite grades files, not processes — DF-001-clean.

### 3.5 Verifier integrity (the Oracle gate, made permanent)

Ablation §3.2's rule — *a task whose Oracle fails is a broken verifier, not a hard task* — plus its inverse: **a verifier that cannot fail a known-bad output is also broken**. `tests/test_verifier_integrity.py` asserts, for every task: (a) the Oracle passes its own test battery; (b) each fixture in `tests/broken_fixtures/` — one per defect class, including the **real April fabricated citation preserved un-repaired** — fails the specific test that owns that class. Runs in plain pytest; must be green before the suite may grade anything, and stays green forever (phase-ablation §6c: the false-green corpus never shrinks).

## 4. Features

### FEAT-POH-001 — Contract harness
`harness/po_contract.py` (schema validators, Pydantic-faithful, file:line provenance per rule) + `harness/grading.py` (think/fence extraction, grounding, coverage matcher). Stdlib only. **Acceptance:** verifier-integrity suite green.

### FEAT-POH-002 — Task corpus ×4
The four §3.2 task folders, corpus copies SHA-256-pinned, instructions provenance-pinned to the serving prompts at `specialist-agent/roles/product-owner/prompts/` (`player_extract_roadmap.md`, `player_extract_features.md`, `player_extract.md`, `player_greenfield.md`). **Acceptance:** 4/4 Oracle passes with `PO_EVAL_OUTPUT_DIR=solution/`.

### FEAT-POH-003 — Fixture battery (broken + good)
Broken: ≥1 fixture per grading axis per applicable task (schema violation, enum drift, fabricated citation — with and without `.md` extension, coverage collapse, keyword-salad coverage, enrichment leak, allowlist escape, empty-string metadata, duplicate roadmap ids, bad timestamp, non-empty greenfield sources, no-think). Good: legitimate-but-tricky shapes that must PASS (literal think tags inside the payload, serving-repairable overlong Phase B quote, trailing echo fence). **Acceptance:** every broken fixture fails exactly its owning test, every good fixture passes; battery includes the April `FEAT-PO-032` defect verbatim.

### FEAT-POH-004 — Baseline measurement + RESULTS template
Run the graders over the un-repaired April outputs (the base-model baseline) and the Oracles; record per-axis results in §5.1. `RESULTS-po-heldout-<date>.md` template for the graded run: per-task × per-rep table, per-axis verdicts, §5 verdict applied verbatim. **Acceptance:** §5.1 table filled from measurement, not estimation.

## 5. Pre-registered verdict (Rich amends if needed, then FREEZES before po-ft-v1 is graded — freeze = the commit that lands this file)

**Validity gate:** all 12 rollouts produced by the pinned po-ft-v1 config with per-rep config records; missing/aborted reps re-run, never skipped. An invalid run is INVALID, not a failure.

**po-ft-v1 DEPLOYS into the product-owner role iff all of:**

- **G1 — Serving shape & schema: 12/12 reps.** Every rep of every task parses (one fence-aware think block; first JSON object via the runtime cascade), asserts its task's pinned mode, and validates against its task's schema. Zero tolerance is deliberate: serving-shape fluency is the fine-tune's stated purpose (Phase-0 verdict); a model that emits an unparseable roadmap in 1 of 12 tries fails in the first week of real use.
- **G2 — Grounding: zero fabricated references** across all reps of the three corpus tasks. Every cited name resolves against the corpus manifest. NOTE: this is the one axis where the gate is deliberately **stricter than the April baseline** (which shipped one fabrication at accept) — fabricated sources are the named worst failure mode of the entire PO concept and are deterministic, zero-cost behaviour to satisfy.
- **G3 — Coverage-vs-reference: ≥2 of 3 reps per corpus task at or above the April baseline** on the required checklist (per-task numbers in §5.1) **and above the anti-collapse floors:** ≥5 epics and ≥18 features (phase-a stubs / full-mode features; floors chosen against the April baseline's 8/36 — 18 is half the features, 5 keeps a majority of the epic spread), and — Phase B's coverage form, same ≥2/3 tolerance — ≥1 enrichment per Phase-A stub of the target epic (`test_all_stubs_enriched`).
- **G4 — Phase-B discipline: 3/3 reps** pass the dispatcher-mirror gates (epic_id, allowlist, batch-level completeness, grounded non-empty sources).
- **G5 — Greenfield discipline: 3/3 reps** emit `coverage_score=null`, zero source references at every level, and ≥3 assumptions — **every** assumption present must have the complete falsifiable shape (non-empty `statement` and `impact_if_wrong`, `confidence ∈ {high,medium,low}`).

**If not met:** NO-DEPLOY; po-ft-v1 returns to Phase 3/4 with the failing axis named in RESULTS; the base model keeps serving. The gate is never adjusted after grading has started — amendments before the freeze only, and the frozen thresholds ride with the RESULTS doc. Golden-set (Coach) results never rescue a failed G1–G5, and vice versa: **both** gates must pass to deploy.

### 5.1 Measured baselines (filled by FEAT-POH-004 during build — same session)

| Measurement | Value |
|---|---|
| Oracle pass, 4/4 tasks | **PASS** (see PROVENANCE.md per task for repairs applied to `po-held-003`'s Oracle) |
| Verifier integrity | **33/33 green**: 4 Oracle passes, 20 broken fixtures each failing exactly their owning test, 3 good fixtures passing, 3 corpus manifests verified, checklist sanity ×2, battery-populated |
| April baseline, grounding (G2 axis) | **FAIL — 1 fabricated reference** (`FinProxy-Achitecture-Exploration.md`, FEAT-PO-032 `field_citations`) — preserved as broken fixture |
| April baseline, required coverage: phase-a | **5/5 required areas** (per-unit matcher; areas matched across 6–24 distinct units) |
| April baseline, required coverage: full | **5/5 required areas** (over repaired `enriched_roadmap.json`; 9–36 distinct units per area) |
| April baseline, stretch areas | **Both not covered.** Identity & Access: no I&A epic/feature in April output. NATS/event-messaging: April's epic/feature *text* never names NATS/JetStream (1 anchor only, below the 2-anchor bar) even though EPIC-007 cites the Tech-Stack docs — hence both stretch, non-gating |
| April baseline, structure | 8 epics / 36 features; floors set at 5 / 18 |

*(Values above confirmed by `pytest tests/ tasks/` at build end — §8.1/8.2. If any value changes on re-measurement, the change is a defect to investigate, not a number to update silently.)*

## 6. The suite outlives the gate

- **(a) po-ft-v2, v3, …** — same suite, same frozen thresholds, new RESULTS doc per candidate; thresholds may only be *raised* between candidates, never lowered mid-grade.
- **(b) The false-green corpus** (ablation §6c): the April fabricated-citation fixture is the first doc-shaped member; every wild catch from PO serving joins `tests/broken_fixtures/`.
- **(c) Backward edge**: when the runtime Coach (criteria/definitions.yaml rubric) grades a PO output that later fails this suite's axes, that disagreement is QA-Verifier calibration data, same as ablation §6a.

## 7. Explicitly out of scope

Judgment-quality grading (assumption posture, prioritisation, decomposition taste — the golden-set Coach gate owns those) · idea/evolve/impact/scope modes (no reference corpus, no training coverage; add when either exists) · multi-turn revise loops · runtime Coach calibration · the code-shaped coach-ft suite (own scope) · running the fine-tune itself (Phase 3/4, agentic-dataset-factory). **Standing constraint:** the 13 FinProxy docs, the April outputs, and the manual build plan must never enter PO training or golden-set seed data — the day they do, this suite stops being held-out and must be rebuilt on a fresh reference.

## 8. Success criteria (phase level)

1. Suite exists, Oracle-validated 4/4, **before the bulk-generation run completes** (§6b deadline; run live since 08:00 today).
2. Verifier-integrity battery green: every broken fixture fails its owning test, including the real April fabrication.
3. §5 thresholds frozen by Rich before po-ft-v1 is graded; freeze commit referenced in the RESULTS doc.
4. Graded run (12 rollouts) produces `RESULTS-po-heldout-<date>.md` with the §5 verdict applied verbatim within one day of Phase 4 completing.

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Schema drift: specialist-agent types change after this pin | Harness rules carry file:line provenance; §5 freeze pins the contract version; re-pin = new suite version + re-freeze, never silent edits |
| Anchor-based coverage matcher too loose/too strict | Calibrated against both April outputs + broken coverage-collapse fixture; matcher transparency (checklist JSON, no hidden logic) makes disagreements auditable |
| Reference leakage into training | §7 standing constraint; hold-out integrity row in §2 verified today; re-verify at Phase 2/3 seed assembly |
| Oracle repairs over-fit the tests to the oracle | Every repair logged in PROVENANCE.md; un-repaired original preserved as a fixture that must FAIL — the repair set is exactly the defect set |
| Suite passes a bad model (shape ≠ quality) | By design — G1–G5 are the deterministic floor; the golden-set Coach gate is the judgment ceiling; deployment requires both |
| GB10-side runner drift (wrong quant/template at grade time) | Validity gate: per-rep config records required; mismatch ⇒ INVALID run, not a graded result |

---

**Next step:** ~~Rich reviews this scope + the built suite, amends §5 if needed, and freezes by committing~~ **done — reviewed and frozen 2026-07-03 (commit `6f9b9b7`).** Runner: `harness/run_po_eval.py` — serving-faithful assembly per each task's instruction.md Runner-assembly section, per-rep config records incl. a server probe (§9 drift mitigation); adversarially reviewed same day (4 defects found; fixes landed in the post-freeze instrument amendment — see Status); dry-run assembly proven 12/12. When po-ft-v1 lands on llama-swap:

```bash
cd ~/Projects/appmilla_github/fleet-evals
python3 harness/link_assets.py                               # link + SHA-verify the private FinProxy assets
python3 -m pytest tests/ -q                                  # verifier integrity — must be green before grading
python3 harness/run_po_eval.py --model po-ft-v1 --grade      # 12 rollouts + per-rep grading
# aborted reps: re-run with --task <id> --rep <n> --out <same run dir> (never skip)
# then apply §5 verbatim in RESULTS-po-heldout-<date>.md (template in repo root)
```
