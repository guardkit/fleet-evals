# dcl-held-001-author-stats

The promoted DCL SPIKE authoring task, now a first-class member of the
**`dcl-heldout`** suite (Phase D / D4). Grade a DCL capability document a
model/author produces for api_test's `GET /stats` endpoint — **the grader is the
DCL compiler itself** (the vendored, deterministic, offline, LLM-free WASM
checker at `harness/dcl/bin/`, via `harness/dcl_gates.py`).

| Path | Role |
|---|---|
| `task.toml` | task metadata (`suite = "dcl-heldout"`, `reps = 3`) + provenance |
| `instruction.md` | the authoring task — model `/stats` in DCL + a DCL syntax few-shot |
| `input/feature-brief.md` | the self-contained authoring input (Request + 8 scenarios + pass-bar) |
| `solution/response.dcl` | the Oracle — S2's hand-authored capability, the bare-run reference |
| `test/` | the pytest grader (G1 compile-clean + G2 structural floor) via `harness.dcl_gates` |
| `test/fixtures/broken.dcl` | the false-green guard — a known-bad file the grader MUST keep failing |

```bash
# Grade the Oracle (bare run — output dir defaults to solution/):
python3 -m pytest test/ -q
# Grade a candidate rep (a dir containing response.dcl):
PO_EVAL_OUTPUT_DIR=/path/to/rep python3 -m pytest test/ -q
```
