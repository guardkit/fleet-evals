# dcl-held-004-repair-diagnostics

Compile-**repair** a rejected DCL capability (dcl-heldout / Phase D / D4). Given a
broken `.dcl` and the checker's verbatim diagnostics, produce a compile-clean
repair that preserves the declared semantics. The planted defects include the
**seat near-miss class** — invented enum literals outside DCL v1.0's closed
vocabulary (`actor ... is machine`, `effect ... is in_memory`; see
`spike/dcl-authoring/seat-attempt/SEAT-RESULT.md`) — plus an undeclared-outcome
typo. The grader is the DCL compiler itself (via `harness/dcl_gates.py`).

| Path | Role |
|---|---|
| `task.toml` | task metadata (`suite = "dcl-heldout"`, `reps = 3`) + provenance |
| `instruction.md` | the repair task — fix the four errors, preserve the declared names |
| `input/broken.dcl` | the rejected `GET /stats` capability (four planted defects) |
| `input/diagnostics.json` | the checker's verbatim envelope on `broken.dcl` |
| `solution/response.dcl` | the Oracle — the reference repair, the bare-run reference |
| `test/` | the pytest grader (G1 compile-clean + semantic-preservation floor) via `harness.dcl_gates` |

The gate discriminates: the false-green guard is the task's own `input/broken.dcl`,
which the compile gate MUST reject.

```bash
python3 -m pytest test/ -q                                   # grade the Oracle repair
PO_EVAL_OUTPUT_DIR=/path/to/rep python3 -m pytest test/ -q   # grade a candidate rep
```
