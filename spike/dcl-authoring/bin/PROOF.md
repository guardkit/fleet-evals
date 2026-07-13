# PROOF — the vendored checker runs (S1, DCL SPIKE)

Two runs, verbatim, captured 2026-07-13 on the GB10 Spark (aarch64), Node v24.15.0.
Both re-run byte-identical (output sha256 stable across repeated runs). Perf per run:
**0.09 s wall, ~82 MB RSS** (matches the eval doc §2 probe: 0.08 s / 81 MB).

Reproduce from this directory:

```sh
node dcl-check.mjs proof-valid.dcl    # expect exit 0
node dcl-check.mjs proof-broken.dcl   # expect exit 1
```

Output-sha check (determinism): `node dcl-check.mjs proof-valid.dcl | sha256sum` →
`7a658a07db13950738f49b57f1ffe3fcd39d67dc8a142357c92cfbc9ddf7ac04` (stable);
broken → `5e596cc2f29da15f29c5b0801bfcf3c4fe7573d45300c2a762f304c656bac814` (stable).

---

## PROOF 1 — the repo README example compiles (`ok:true`, exit 0)

Input: `proof-valid.dcl` — the DCL example from the pinned repo's `readme.md` (lines 43–128),
copied verbatim (86 lines).

Command: `node dcl-check.mjs proof-valid.dcl` → **EXIT 0**

```json
{
  "ok": true,
  "diagnostics": [
    {
      "severity": "warning",
      "message": "policy concern is already effective at this boundary",
      "code": "DCL_SEM_REDUNDANT_POLICY",
      "line": 14,
      "column": 5
    },
    {
      "severity": "warning",
      "message": "policy concern is already effective at this boundary",
      "code": "DCL_SEM_REDUNDANT_POLICY",
      "line": 14,
      "column": 5
    },
    {
      "severity": "warning",
      "message": "policy concern is already effective at this boundary",
      "code": "DCL_SEM_REDUNDANT_POLICY",
      "line": 15,
      "column": 5
    },
    {
      "severity": "warning",
      "message": "policy concern is already effective at this boundary",
      "code": "DCL_SEM_REDUNDANT_POLICY",
      "line": 15,
      "column": 5
    }
  ],
  "diagnosticCount": 4,
  "errorCount": 0,
  "warningCount": 4,
  "infoCount": 0,
  "sourceCount": 1
}
```

`ok:true`, zero errors → exit 0. Four `DCL_SEM_REDUNDANT_POLICY` **warnings** (non-fatal),
each line/column-located — matches the eval doc §2 PROBE-1 (4 redundant-policy warnings on this
same example). A genuine semantic pass, not a bare parse.

---

## PROOF 2 — a deliberately broken file fails (`ok:false`, coded errors, exit 1)

Input: `proof-broken.dcl` — a minimal capability that references an undeclared shape
(`RegistrationInput`) and actor (`Customer`), lists an outcome with no explicit causation, and a
`when` branch naming an outcome (`NonExistentOutcome`) absent from the `outcomes` block.

Command: `node dcl-check.mjs proof-broken.dcl` → **EXIT 1**

```json
{
  "ok": false,
  "diagnostics": [
    {
      "severity": "error",
      "message": "undefined actor",
      "code": "DCL_SEM_UNKNOWN_ACTOR",
      "line": 8,
      "column": 3
    },
    {
      "severity": "error",
      "message": "undefined shape",
      "code": "DCL_SEM_UNKNOWN_SHAPE",
      "line": 8,
      "column": 3
    },
    {
      "severity": "error",
      "message": "outcome has no explicit causation",
      "code": "DCL_SEM_OUTCOME_CAUSE_REQUIRED",
      "line": 11,
      "column": 5
    },
    {
      "severity": "error",
      "message": "when branch references unknown outcome",
      "code": "DCL_SEM_UNKNOWN_OUTCOME",
      "line": 15,
      "column": 5
    }
  ],
  "diagnosticCount": 4,
  "errorCount": 4,
  "warningCount": 0,
  "infoCount": 0,
  "sourceCount": 1
}
```

`ok:false`, four **error** diagnostics → exit 1. The four codes —
`DCL_SEM_UNKNOWN_ACTOR`, `DCL_SEM_UNKNOWN_SHAPE`, `DCL_SEM_OUTCOME_CAUSE_REQUIRED`,
`DCL_SEM_UNKNOWN_OUTCOME` — are **exactly** the four the eval doc §2 PROBE-2 predicted, each
line/column-located. (Note per §2: the first two codes are composed at runtime, so a static
`strings dcl.wasm` grep would not find them; this receipt is the reproduced running output.)

---

## Verdict

S1 met on the PRIMARY (WASM) path: a working, vendored, pinned DCL validity checker invocable
from a script, proving `ok:true` on a valid file (exit 0) and `ok:false` with coded errors on a
broken file (exit 1). The SECONDARY prebuilt-binary path is unavailable on this aarch64 host (no
linux-arm64 mcp build) — see `PROVENANCE.md`.
