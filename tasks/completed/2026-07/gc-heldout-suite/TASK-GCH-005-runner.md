---
id: TASK-GCH-005
title: "harness/run_gc_heldout.py — direct-serving stand-in runner (per rep answer sheets)"
status: completed
task_type: feature
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 4
implementation_mode: task-work
complexity: 5
priority: high
dependencies: [TASK-GCH-003]
created: 2026-07-10T13:56:30Z
consumer_context:
  - task: TASK-GCH-003
    consumes: ANSWER_SHEET_FORMAT
    framework: "urllib.request against llama-swap /v1/chat/completions (coach runner precedent)"
    driver: "python3 stdlib"
    format_note: "runner WRITES the answer sheet (programs/ + rows/ + candidate.json + config.json); it NEVER grades — grading is the gate battery's job"
---

# TASK-GCH-005 — Runner (ASSUM-013: run_coach_heldout.py precedent; run_po_eval.py untouched)

## Scope

**NEW** `harness/run_gc_heldout.py` — toolless chat completion against the served handle
(llama-swap :9000), one rep per invocation:

- Args: `--task-dir --out --model --rep --endpoint --temperature 0.1 --top-p 0.9
  --max-tokens 2048 --quant --base-family --lineage --template --prompt-version`.
- Pre-flight: `gc_sandbox.ensure_available()` (refuse-loud); `gc_gates.verify_pins()`
  (drift blocks before any model call); output-dir ownership check (refuses another
  suite's records — qav §5 rule generalized).
- Per row: build the pinned prompt (single source: `gc_gates` prompt builders; per-row
  prompt SHA-256 recorded), POST with `GENERATION_TIMEOUT_S`; **2 transport retries per
  call, then abort the rep and report** (RETRIES_PER_REP precedent) — no fabricated or
  empty response is ever written as a gradable row; on response: record raw response +
  `finish_reason`, extract program (fence-first contract), write `programs/{ROW-ID}.py`
  or the `rows/{ROW-ID}.json` diagnostic (extraction failure recorded, run continues).
- Rep records: `candidate.json` (model id, lineage, base_family, quant — the family key
  material) + `config.json` (serving pins, sampling, prompt hashes, row SHAs, per-row
  meta, freeze-commit field left "PROPOSED — not yet frozen" until the scope doc freezes).
- An aborted rep leaves an explicit `ABORTED.json` marker (transport failure detail) —
  the run-level validity gate reads it as INVALID-not-failed; re-run in place.

**NEW** unit tests in `tests/test_gc_gates.py` (or sibling) for the pure helpers the
runner shares with the gates: prompt builders + hashes, ownership check, extraction.
Transport behaviour is factored so retry/abort logic is unit-testable without a server.

## Acceptance Criteria

- [ ] `harness/run_po_eval.py` byte-identical (`git diff` empty on frozen paths)
- [ ] Runner never grades; no import of pytest; answer sheet matches ANSWER_SHEET_FORMAT
- [ ] Transport: 2 retries then abort-and-report with `ABORTED.json`; no partial row is
      silently graded
- [ ] Output-dir refusal demonstrated by unit test (foreign suite marker ⇒ refuse to start)
- [ ] Full battery green; failing set == baseline
- [ ] All modified files pass project-configured lint/format checks with zero errors
