# spike/dcl-authoring — the DCL SPIKE fleet-evals leg (S4)

**SPIKE-CLASS — NOT a frozen suite. No thresholds implied. Freeze = Rich's call
post-spike.** This folder is an additive prove-or-kill probe for the DCL SPIKE (V-02
re-aimed; spec of record: `ai-transition/docs/research/dcl-factory-evaluation-2026-07.md`
§7, run book: `docs/ways-of-working/dcl-spike-handoff.md`). It is deliberately *not* wired
into the standing held-out suites, has no `RESULTS-*` template, and gates nothing.

## What it is

A fleet-evals task that grades *a DCL capability document a model/author produces* for
api_test's `GET /stats` feature. The novelty: **the grader is the DCL compiler itself** —
the vendored, deterministic, offline, LLM-free WASM checker under `bin/` — so the thing a
hand-built suite normally has to author (the oracle) is a free deterministic tool. See the
eval doc §2 for the compiler probe and `bin/PROOF.md` / `bin/PROVENANCE.md` for the S1
staging receipts.

## Layout (fleet-evals task-folder contract)

| Path | Role |
|---|---|
| `task.toml` | task metadata (`spike_class = true`) + provenance |
| `instruction.md` | the authoring task — model `/stats` in DCL, from the SAME planning inputs S2 used (self-contained: the Request, the 8 scenarios, the pass-bar) + a DCL syntax few-shot; doubles as the seat prompt |
| `test/` | the pytest grader — shells out to `bin/dcl-check.mjs`, asserts `ok:true` + zero errors + a light structural floor |
| `test/fixtures/broken.dcl` | the **false-green guard**: a known-bad file (undefined actor/shape, `when` names an undeclared outcome) the grader MUST keep failing |
| `solution/response.dcl` | the reference — S2's hand-authored `capability.dcl`, copied in; the bare-run oracle |
| `bin/` | the vendored + pinned checker (`dcl-check.mjs`, `dcl.wasm`, `wasm_exec.js`) from Capability-Language @ `4f9fbe56` |
| `seat-attempt/` | the ONE bounded qwen36-workhorse attempt (raw `response.dcl` + `metadata.json`), graded honestly |

## Run it

```bash
# Grade the reference (bare run — output dir defaults to solution/):
python3 -m pytest test/ -q

# Grade any candidate rep (a dir containing response.dcl):
DCL_EVAL_OUTPUT_DIR=/path/to/rep python3 -m pytest test/ -q
```

The grader depends on **nothing** in the repo `harness/` — it is self-contained (node +
the vendored WASM blob). `test_broken_fixture_is_rejected` is the permanent false-green
guard; if it ever passes, the grader is void.
