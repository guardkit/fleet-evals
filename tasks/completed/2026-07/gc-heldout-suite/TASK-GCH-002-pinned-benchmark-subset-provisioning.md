---
id: TASK-GCH-002
title: "Pinned 25+25 HumanEval/MBPP subset committed in-repo with SHA-256 pins + provenance"
status: completed
task_type: feature
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 2
implementation_mode: task-work
complexity: 6
priority: high
dependencies: [TASK-GCH-001]
created: 2026-07-10T13:56:30Z
consumer_context:
  - task: TASK-GCH-001
    consumes: SANDBOX_RESULT_AND_AVAILABILITY
    framework: "stdlib subprocess sandbox (harness/gc_sandbox.py)"
    driver: "python3 stdlib"
    format_note: "selection-rule validation MUST execute canonical solutions via run_program() — the same surface that will grade candidates — so the exclusion rule and the grading rule cannot diverge"
---

# TASK-GCH-002 — Benchmark subset provisioning (ASSUM-001/007)

## Scope

**NEW** `harness/provision_gc_subset.py` (stdlib-only; network used at build time only) —
deterministic, re-runnable provisioner:

1. Fetch HumanEval (`openai/human-eval` `data/HumanEval.jsonl.gz`, MIT) and MBPP
   (`google-research/google-research` `mbpp/mbpp.jsonl`, CC BY 4.0); record source URL +
   upstream commit + retrieval date.
2. Selection rule (ASSUM-001, pinned verbatim): ascending **numeric** benchmark task-id;
   assemble each row's canonical program (HumanEval: `prompt + canonical_solution` +
   `test` + `check(entry_point)`; MBPP: `code` + `test_setup_code` + `test_list` asserts)
   and execute it in the gc sandbox under the pinned interpreter (Python 3.12.3);
   rows whose canonical solution FAILS are excluded BEFORE pinning, with the exclusion
   and reason recorded in the manifest; first 25 survivors per benchmark.
3. Commit per-row `tasks/gc-held-00X/input/rows/{ROW-ID}/row.json` (canonical bytes:
   `json.dumps(..., indent=2, sort_keys=True) + "\n"`), `input/manifest.json` with per-row
   SHA-256 pins, and `input/PROVENANCE.md` (MIT text + attribution for HumanEval; CC BY 4.0
   attribution + licence link + statement of changes for MBPP).
4. Row ids: `HumanEval-{n}` / `mbpp-{n}` — unique across the whole suite (spec @negative
   row-id collision scenario).
5. **Oracle material**: write `tasks/gc-held-00X/solution/programs/{ROW-ID}.py` (the
   canonical candidate program WITHOUT reference asserts — asserts are grader-side) and
   `solution/candidate.json` marked `"oracle": true`, + `solution/PROVENANCE.md`.

**NOT touched:** `harness/link_assets.py`, `ASSETS.sha256` — the symlink farm is for
private client data; this subset is public and lives in-repo (ASSUM-007).

## Acceptance Criteria

- [ ] 25 rows per benchmark on disk, each matching its manifest SHA-256 pin
- [ ] Every committed row's canonical solution PASSES in the gc sandbox (provisioner
      re-verifies at the end; this becomes the integrity battery's Oracle leg)
- [ ] Exclusions (if any) recorded in the manifest with per-row reasons
- [ ] Licence/provenance records committed (HumanEval MIT, MBPP CC BY 4.0)
- [ ] Row ids unique across both tasks
- [ ] `link_assets.py`/`ASSETS.sha256` byte-identical; frozen suites untouched
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Notes

- MBPP task-ids 1..10 are conventionally few-shot prompting rows; the frozen selection rule
  is "ascending task-id after exclusions" VERBATIM (Rich-confirmed ASSUM-001) — no split
  carve-outs. Record this reading in the scope doc so the freeze covers it.
- The manifest also records the pinned interpreter version and the sandbox module name, so
  a future interpreter bump is a visible instrument revision (reopens the scope doc).
