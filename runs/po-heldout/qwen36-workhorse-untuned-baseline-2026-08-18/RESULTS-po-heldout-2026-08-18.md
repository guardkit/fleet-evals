# RESULTS — PO held-out deployment gate — qwen36-workhorse (UNTUNED BASELINE, the production PO seat) — 2026-08-18

**Candidate:** the untuned production seat: llama-swap alias `product-owner-agent` → `qwen36-workhorse`
(Qwen3.6-35B-A3B-UD-Q4_K_XL, `--ctx-size 131072 -np 1 --reasoning auto`, server defaults temp 0.6 / top-p 0.95).
This is the never-before-run baseline, not a po-ft candidate. NOT a deploy decision.
**Frozen thresholds:** po-heldout-suite-scope.md §5; G5 letter as repaired 2026-08-11 (Option-A, `ab011c3` after rebase) — graded AS-RUN under that letter; the same evening the letter's whitespace defect was fixed (see Notes) and the three 004 reps were re-graded in place (`grade-regraded-letterfix-2026-08-18.txt`, all 6/6 PASS). Both grades are kept.
**Verifier integrity at grade time:** `python3 -m pytest tests/ -q` → 353 passed, 8 failed, 17 errors — every red is in `tests/test_gc_*` (general-coding sandbox: isolation binary absent on this host); PO/idea/spec slice (`test_verifier_integrity.py test_idea_gates.py test_idea_verifier_integrity.py test_spec_verifier_integrity.py`) → **161 passed**. `harness/link_assets.py --check` → 88 files pinned ✓.
**Runner config per rep:** `<task>/rep<N>/config.json` (endpoint, alias, server_model, gen params = server defaults, sha256 of system/user prompt, corpus manifest sha, usage, duration, finish_reason, response_provenance).
**Run:** `python3 harness/run_po_eval.py --model product-owner-agent --grade` (default suite po-heldout, 4 tasks × 3 reps), 2026-08-18 18:12:04Z → 19:17:12Z (65 min); prompts from `specialist-agent @ 3f796d9` (= origin/main). 12/12 reps completed, finish_reason=stop, 0 transport errors, 0 re-runs. All 12 replies arrived with the think block in `reasoning_content` and were re-wrapped by the runner (`rewrapped_reasoning_content`).
Session of record: ai-transition `docs/po-lane-state-2026-08-18.md` §4.

## Per-task × per-rep

| Task | Rep | shape | schema | grounding | coverage | floors | discipline | verdict |
|---|---|---|---|---|---|---|---|---|
| po-held-001-extract-phase-a | 1 | PASS | PASS | PASS | PASS | FAIL(test_structure_floors: 6 epics / 17 stubs < 18) | — | FAIL |
| po-held-001-extract-phase-a | 2 | PASS | PASS | PASS | PASS | FAIL(test_structure_floors: 6 / 17 < 18) | — | FAIL |
| po-held-001-extract-phase-a | 3 | PASS | PASS | PASS | PASS | PASS (13 / 25) | — | PASS |
| po-held-002-extract-phase-b | 1 | PASS | PASS | PASS | PASS (all-stubs-enriched, 4/4) | — | PASS | PASS |
| po-held-002-extract-phase-b | 2 | PASS | PASS | PASS | PASS (4/4) | — | PASS | PASS |
| po-held-002-extract-phase-b | 3 | PASS | PASS | PASS | PASS (4/4) | — | PASS | PASS |
| po-held-003-extract-full | 1 | PASS | PASS | PASS | PASS | PASS (7 / 18) | — | PASS |
| po-held-003-extract-full | 2 | PASS | PASS | PASS | PASS | PASS (6 / 31) | — | PASS |
| po-held-003-extract-full | 3 | PASS | PASS | PASS | PASS | PASS (15 / 19) | — | PASS |
| po-held-004-greenfield-discipline | 1 | PASS | PASS | — | — | — | FAIL(test_no_source_references — see Notes) | FAIL |
| po-held-004-greenfield-discipline | 2 | PASS | PASS | — | — | — | FAIL(test_no_source_references) | FAIL |
| po-held-004-greenfield-discipline | 3 | PASS | PASS | — | — | — | FAIL(test_no_source_references) | FAIL |

(`test_mode_is_extract` / `test_mode_is_greenfield` PASS on every 003/004 rep; `test_coverage_score_null` and `test_assumptions_present_and_falsifiable_shape` PASS on every 004 rep — assumptions 5 / 4 / 4.)

Grade any rep with: `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q`

## §5 verdict (applied verbatim — no post-hoc adjustment)

- **G1 serving shape & schema (12/12):** MET — 12/12.
- **G2 grounding (zero fabricated refs, corpus tasks):** MET — 9/9 reps, all cited names resolve to the manifest.
- **G3 coverage ≥ baseline, ≥2/3 reps per corpus task + floors (≥5 epics / ≥18 features) + Phase-B all-stubs-enriched (≥2/3):** NOT MET — 003 3/3, 002 3/3, **001 1/3** (coverage passed 3/3, epic floor held 3/3, feature floor failed reps 1–2 at 17 < 18).
- **G4 Phase-B discipline, 3/3:** MET — 3/3.
- **G5 greenfield discipline, 3/3:** NOT MET as the letter stood at run time — 0/3; **MET 3/3 under the letter as fixed the same evening** (whitespace-normalised verbatim check; every other G5 item passed as-run). Every failure is `test_gate_po_held_004.py:80` (`frag in brief`) on `request:<fragment>` references whose fragment spans a line-wrap in `input/brief.md` (e.g. `gives the driver a manifest they can work through on the road` vs the brief's `…they\ncan work…`). Whitespace-normalised re-check of all request refs in all three reps (scratch, no repo edit): 0 failures → 3/3. All other G5 letter items PASS on every rep (null coverage, zero filenames, 0 empty features, ≥3 complete assumptions).

## VERDICT: NO-DEPLOY (baseline; not a candidate)

Failing axis under the fixed letter: G3 only (po-held-001 feature floor, 17 < 18 in two reps). G5 was failed as-run by the gate-letter whitespace defect, not by model behaviour, and passes 3/3 re-graded. Golden-set results were not run and would not rescue this verdict.

## Non-gating diagnostics

| Metric | rep values | April baseline |
|---|---|---|
| Stretch coverage: identity-access | not measured in this run | not covered |
| Stretch coverage: nats-messaging | not measured in this run | not covered |
| Epic count (001 / 003) | 6, 6, 13 / 7, 6, 15 | 8 / 8 |
| Feature count (001 / 003) | 17, 17, 25 / 18, 31, 19 | 36 / 36 |
| Assumption count (004) | 5, 4, 4 | 4 (authored oracle) |
| Self-reported coverage_score (001 / 003) | 0.95, 0.95, 0.92 / 0.93, 0.97, 0.96 | — |
| Prompt / completion tokens | 001: 63,100 / 12.5–15.6k · 002: 36,706 / 10.0–21.6k · 003: 64,408 / 17.2–22.2k · 004: 2,801 / 6.4–8.4k | — |
| Wall-clock per rep | 001: 337/298/373 s · 002: 477/207/325 s · 003: 447/539/429 s · 004: 152/190/126 s | — |

## Notes

- **G5 letter defect (FIXED same evening on Rich's word, commit alongside this run; good fixture `request-refs-across-line-wrap` = rep3 of this run, broken fixture `request-ref-not-in-brief` keeps the raise enforceable):** `test_no_source_references` compares `request:` fragments as raw substrings against a hard-wrapped brief; a fragment that quotes across a line break fails. Fix is one line (normalise whitespace on both sides). It is a bug in the 08-11 Option-A repair, not a raise or de-scope. The three failing 004 rollouts are the first wild catch for it — candidate for `tests/broken_fixtures/` per scope §6b once ruled.
- **Behavioural datum:** the untuned seat grounds every greenfield feature with `request:<verbatim fragment>` (10/7/6 refs, 0 empty) — the deployed `player_greenfield.md` convention. The 42 synthetic greenfield training rows in `agentic-dataset-factory/corpora/` teach empty `source_documents` (see the session report).
- 001 reps 1–2: 6 epics / 17 stubs — one stub under the 18 floor, coverage and grounding otherwise clean; rep 3 25 stubs. Three reps only; §5 forbids extra rollouts.
- Live-fleet posture during the run: `-np 1` seat shared with production traffic (a forge build completed on it during the run); no swap, no drain, no serving-config change.
- Committed on Rich's word 2026-08-18 evening ("proceed to implement all the recommendations … merge").
