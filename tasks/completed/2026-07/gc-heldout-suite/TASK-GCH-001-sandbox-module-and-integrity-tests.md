---
id: TASK-GCH-001
title: "harness/gc_sandbox.py — stdlib subprocess sandbox (refuse-loud) + sandbox integrity tests"
status: completed
task_type: feature
parent_review: TASK-REV-B7E2
feature_id: FEAT-GCH
wave: 1
implementation_mode: task-work
complexity: 6
priority: high
dependencies: []
created: 2026-07-10T13:56:30Z
---

# TASK-GCH-001 — Execution sandbox + its own integrity battery

## Scope

**NEW** `harness/gc_sandbox.py` (stdlib-only: `subprocess`, `resource`, `tempfile`, `os`,
`signal`, `shutil`, `dataclasses`). The one sanctioned surface for executing model-generated
code (ASSUM-008; DF-001 posture — no Docker):

- `run_program(program_text, *, timeout_s=10.0, memory_bytes, max_processes, ...) -> SandboxResult`
  — writes the program into a throwaway scratch dir, executes
  `unshare -rn -- python3 -I program.py` with CWD=scratch, a scrubbed allowlist env
  (PATH/HOME=scratch/TMPDIR=scratch/LC_ALL only), rlimits set pre-exec (CPU, AS, NPROC,
  FSIZE, CORE=0), `start_new_session=True`; wall-clock kill via process-group on timeout.
  PASS = exit 0; FAIL carries a machine-readable reason (`nonzero-exit`, `timeout`, ...).
  Scratch removed afterwards, always.
- `ensure_available() -> None` — probe battery run at import-of-use time (gate conftest,
  runner start): trivial program exits 0; network probe program must FAIL to connect
  (fresh netns); rlimit application demonstrated. Any missing leg ⇒ raise
  `SandboxUnavailable` NAMING the missing isolation. REFUSE-LOUD: no caller may fall back
  to unsandboxed execution.
- Grader-crash vs candidate-FAIL: our bugs raise exceptions (⇒ pytest ERROR ⇒ G-G1 harness
  defect route); candidate failures return `status="fail"`. Never conflated.

**NEW** `tests/test_gc_sandbox_integrity.py` — the sandbox is itself integrity-tested
(spec Groups C/D): timeout kill (infinite loop, short timeout), network denial, env scrub
(host marker var invisible), scratch-CWD write confinement (repo tree unchanged), memory
containment, process-spawn containment, distinct truncation-free execution reasons,
refuse-loud probe (bad interpreter/unshare path ⇒ `SandboxUnavailable`, nothing executes).

## Acceptance Criteria

- [ ] Candidate code runs in a fresh isolated interpreter (`python3 -I`) in a throwaway
      scratch directory; verdict material comes only from execution
- [ ] Outbound connection attempts fail inside the sandbox (fresh netns via `unshare -rn`);
      probe demonstrates denial before any grading
- [ ] Infinite loop killed at the per-row timeout; host and subsequent runs unaffected
- [ ] Unbounded allocation terminated by rlimits; host stays stable
- [ ] Child-process spawning contained (RLIMIT_NPROC); row fails, host stable
- [ ] Env scrub: no host credential/token visible to the program (allowlist env only)
- [ ] Isolation unavailable ⇒ `SandboxUnavailable` naming the missing leg; no unsandboxed
      execution path exists in the module
- [ ] Frozen files untouched; full battery green (failing set == 229-pass baseline)
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Notes

- `unshare -rn` verified working unprivileged on this host (ENETUNREACH probe, 2026-07-10).
- RLIMIT_NPROC is per-UID: on a busy host ANY fork/thread from candidate code fails
  immediately. Accepted (accident-class threat model) — record as residual in TASK-GCH-007.
- FS confinement is scratch-CWD scoping, not a mount namespace: absolute-path writes are
  constrained only by host DAC. Same residual register.
