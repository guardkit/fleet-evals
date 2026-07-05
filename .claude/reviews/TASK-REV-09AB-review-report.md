# Review Report: TASK-REV-09AB — Plan: Idea-Mode Held-Out Eval Tasks (FEAT-EVAL-IDEA)

**Mode:** decision · **Depth:** standard · **Date:** 2026-07-05
**Method:** 3-agent workflow (architecture-fit / adversarial gate red-team / plan critique), 225k tokens, all findings file:line-verified against the frozen instrument.
**Context A:** focus=all, tradeoff=quality.

## Executive Summary

The feature composes cleanly with the frozen instrument — **exactly one code file needs modification** (`harness/run_po_eval.py`, ~10 additive lines), everything else is new files. The red-team found **two real spec defects that must be fixed before build** (dependency-closure gameable via emptied `depends_on`; selection-subset evadable by content-swap under a legitimate id) plus a set of one-line deterministic hardenings. The plan critique restructured the build into **8 tasks / 5 waves** that keep `pytest tests/` green at every commit and pull the Fable-window-bound frontier answer sheet out as an explicit attended step. **Recommended approach: hand-build in-session** (build plan sanctions it; content-authoring dominates; autobuild adds frozen-file blast-radius risk without leverage).

## Findings (synthesised, most load-bearing first)

### A. Architecture fit (all verified at file:line)

1. **Suite separation works with zero code change** — `run_po_eval.py:330` hard-skips `suite != "po-heldout"` by exact match; precedent: `abl-*` tasks already cohabit. The frozen §5 verdict is applied manually from per-rep grades, so there is no aggregation path to contaminate. (ASSUM-001 confirmed.)
2. **`po_contract.py` needs ZERO edits** — `MODES` already admits idea/scope (:29); confidence enum, coverage null, `constraints_and_dependencies`, `depends_on`, duplicate-id, flatten-match, ≥2-sentence rules all present. State "po_contract.py untouched" as an explicit invariant.
3. **New graders go in a NEW module `harness/idea_gates.py`** (stdlib-only), not appended to `grading.py` — keeps all three frozen grader files **byte-identical**, so "existing grader behaviour untouched" is provable by `git diff`, not argument. Reuse `parse_response`/`collect_cited_documents` by import.
4. **Two hard naming traps** in frozen integrity tests: (a) `test_corpus_integrity` (:101-110) asserts exactly 13 manifest files for ANY task with `input/corpus/` — the scope task's roadmap must live at `input/reference_roadmap.json` + separate SHA-256 pin, never `input/corpus/`; (b) `test_checklist_sanity` (:118-133) pins the 5 FinProxy area ids for ANY `test/reference/coverage_checklist.json` — anchor files must use distinct names (`invention_anchors.json`, `constraint_anchors.json`).
5. **Atomicity constraints**: `test_fixture_battery_is_populated` (:92-96) goes red the moment a task folder lands without ≥1 broken fixture; `assemble()` ValueError is raised outside the retry path (`run_po_eval.py:226`), so task.toml + assemble branch + serving prompts must land as one unit. `player_idea.md`/`player_scope.md` existence in the specialist-agent checkout is a cross-repo prerequisite to provenance-pin.
6. **New assets stay in-repo** — fresh-authored content only; nothing routes through `link_assets.py`/`ASSETS.sha256`.

### B. Gate red-team — spec defects (fix before build)

1. **HIGH — dependency-closure must be computed against the REFERENCE roadmap's graph**, not the response's own `depends_on` (an emptied `depends_on` satisfies self-closure vacuously — the exact vacuity ASSUM-003's override was meant to kill, re-entering through the back door). Also require response `depends_on` entries to resolve to selected ids; add emptied-depends_on broken fixture + reference-graph acyclicity sanity test.
2. **HIGH — selection-subset needs content pinning**: id-subset alone permits invention-by-content-swap under a legitimate id. Require selected features' `title` and `bounded_context` to equal the reference's (NFKC+casefold normalized); leave `description` free (player_scope.md licenses reduced-scope rewrites — Coach territory). Document as gate-stricter-than-serving divergence; add content-swap broken fixture.

### B′. Gate red-team — hardenings (one-liners, each with an owning fixture)

3. **Anti-stuffing counting rule amended**: a statement's stuffing score counts only anchor groups **also asserted in requirement-bearing fields** (spares legitimate compound assumptions — player_idea.md itself trains "state your interpretation and proceed"); calibrate the >2 threshold against the frontier baseline **before the addendum freeze** (raising to >3 is legal pre-freeze).
4. **Per-group licensed good fixture required** (not just a firing broken fixture) — otherwise a narrow group silently becomes a topic ban; licensing is per-GROUP, never per-alternate.
5. **Anchors-disjoint-from-inputs sanity test** — no alternate may match the brief / reference roadmap / constraint text (kills faithful-restating false positives and the constraint-echo-vs-anchor contradiction on 006).
6. **Central NFKC+casefold normalization** + unicode hyphen/space/quote mapping, applied identically to units, licenses, and constraint text.
7. **Matching granularity pinned to the existing `structural_units()` convention** (epic name + bounded_context included); constraint gate matches ALL groups against the **joined** `constraints_and_dependencies` text.
8. **G-I2 worded as "zero ANCHOR-DETECTED unlicensed inventions"** — a detection floor, not completeness; residuals (paraphrase evasion, opposite-polarity licensing, keyword-echo constraint floor) recorded as Coach territory. No negation heuristics.
9. **Anchor groups derived one-per-deliberate-unknown** in the brief; 006 reference ids authored in FEAT-PO-### style with instruction.md mandating id preservation verbatim (avoids systematic 0/3 false positives from the fine-tune's id habit).
10. **Payload-only invariant**: all new gates consume the parsed dict, never raw response text; the think-block-draft fixture carries anchor terms inside the draft to own this.

### C. Plan critique — revised breakdown (8 tasks / 5 waves)

Original 6-task skeleton had correct ordering instincts but fails green-per-commit, hides the frontier sheet, leaves the anchor-file format unpinned across the T2/T3 fork, and sizes T5 at the entire frozen battery's volume.

| Wave | Task | Deps | Cx | Content |
|---|---|---|---|---|
| 0 | (pre-flight) | — | — | `link_assets.py` + full `pytest tests/` → capture pre-extension green (33 checks) as non-regression baseline |
| 1 | R1 addendum doc (DRAFT) | — | 3 | `docs/research/ideas/po-heldout-idea-extension-scope.md`: G-I1..4, INVALID semantics, **pinned anchors-file schema + matcher diagnostic contract** (must name the unlicensed detail / invented id), fixture-floor-list convention, RESULTS template stub. Lands as DRAFT — Rich freezes after build (T1 freeze-point ambiguity resolved) |
| 2 | R2 harness | R1 | 5 | `harness/idea_gates.py` (matchers w/ amended anti-stuffing, structured findings) + `run_po_eval.py` `--suite` + 2 assemble branches; **ships own unit tests** (matcher behaviour; suite selection: default = exactly the 4 frozen ids). Invariants: po_contract.py + grading.py byte-identical |
| 3 | R3 ∥ R4 task folders | R2 | 6, 6 | R3: po-held-005-idea complete + **seed battery** (stub-sheet fixture) so commit stays green. R4: po-held-006-scope + authored chained roadmap (`input/reference_roadmap.json`, ≥1 dependency-free feature, FEAT-PO-### ids) + seed battery |
| 4 | R5 frontier sheet → R6a ∥ R6b batteries | R2+R3 / R3+R5 / R4 | 2, 5, 4 | R5 (attended, Fable-window-bound): frontier sheet from dry-run-assembled prompt; calibrate ASSUM-009 threshold. R6a: full 005 battery + anchor-sanity integrity + floor list. R6b: full 006 battery + roadmap-checksum integrity + floor list. Fixtures = surgical Oracle mutations |
| 5 | R7 validation | all | 3 | full pytest before/after (33 pre-existing checks unchanged); `--suite po-heldout-idea --dry-run` proof 6/6; frontier passes + stub fails (build-plan criteria verbatim); 36-scenario traceability sweep; baselines into addendum; hand to Rich for freeze commit |

**Execution mode: hand-build in-session** (Option 1). Autobuild rejected: work is content-authoring under judgment constraints (disjointness, non-vacuous chains, anchor calibration) with an attended calibration loop; frozen-file blast radius. The frozen suite itself was a same-session hand-build with red-team in the loop.

## Options Matrix

| Option | Fit | Risk | Verdict |
|---|---|---|---|
| 1. Hand-build in-session, 8 tasks/5 waves, idea_gates.py module, red-team hardenings folded in | High | Low | **RECOMMENDED** |
| 2. guardkit autobuild feature | Medium | Medium-high (invented content vs disjointness constraints; frozen-file blast radius; cross-repo runner needs) | Rejected |
| 3. Minimal build (005 only, defer 006) | Low | Low | Rejected — ASSUM-003 confirmed inclusion; 006's gates are the cheapest deterministic wins |

## Spec amendments required before build (fold into [I]mplement)

1. Closure scenario: "declared dependencies" → reference-declared graph (red-team B1).
2. Subset gate scenarios: add title/bounded_context normalized-equality (B2).
3. ASSUM-009 annotation: counting rule amended (body-asserted groups only); threshold calibrated pre-freeze.
4. G-I2 wording in ASSUM-005: "anchor-detected".

## Decision

Awaiting checkpoint: [A]ccept / [R]evise / [I]mplement / [C]ancel.
