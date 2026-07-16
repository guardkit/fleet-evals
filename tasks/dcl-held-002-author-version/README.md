# dcl-held-002-author-version

Author a DCL capability for api_test's **`GET /version`** endpoint (dcl-heldout /
Phase D / D4). The grader is the DCL compiler itself (the vendored WASM checker
at `harness/dcl/bin/`, via `harness/dcl_gates.py`).

| Path | Role |
|---|---|
| `task.toml` | task metadata (`suite = "dcl-heldout"`, `reps = 3`) + provenance |
| `instruction.md` | the authoring task — model `/version` in DCL + a DCL syntax few-shot |
| `input/feature-brief.md` | the self-contained authoring brief (distilled from api_test FEAT-B70F) |
| `solution/response.dcl` | the Oracle — a hand-authored `/version` capability, the bare-run reference |
| `test/` | the pytest grader (G1 compile-clean + G2 structural floor) via `harness.dcl_gates` |
| `test/fixtures/broken.dcl` | the false-green guard — a known-bad file the grader MUST keep failing |

```bash
python3 -m pytest test/ -q                                   # grade the Oracle
PO_EVAL_OUTPUT_DIR=/path/to/rep python3 -m pytest test/ -q   # grade a candidate rep
```
