# Implementation Guide — gc-heldout (FEAT-EVAL-GC / OBS-7)

Consumer: this build session (waves executed in order) and the post-merge reviewer.
Spec of record: `features/gc-heldout-suite/` @ 63ec53f. Decisions: `.claude/reviews/TASK-REV-B7E2-review-report.md`.

## Data Flow: Read/Write Paths

```mermaid
flowchart LR
    subgraph Writes["Write Paths"]
        W1["provision_gc_subset.py\n(build-time, once)"]
        W2["run_gc_heldout.py\n(per rep, per candidate)"]
        W3["baseline runbook step\n(operator, GB10)"]
    end

    subgraph Storage["Storage"]
        S1[("tasks/gc-held-00X/input/\nrows + manifest.json (SHA-256 pins)")]
        S2[("runs/gc-heldout/&lt;candidate&gt;-&lt;date&gt;/rep-N/\nprograms/ + rows/ + candidate.json + config.json")]
        S3[("harness/gc_baselines.json\n(per base+quant family)")]
        S4[("tasks/gc-held-00X/solution/\nOracle canonical programs")]
    end

    subgraph Reads["Read Paths"]
        R1["gate battery: tasks/gc-held-00X/test/\n(PO_EVAL_OUTPUT_DIR → grades by execution)"]
        R2["tests/test_gc_verifier_integrity.py\n(Oracle + fixtures + pins)"]
        R3["RESULTS assembly (per-rep table,\nG-G verdict applied verbatim)"]
    end

    W1 -->|"pins + provenance"| S1
    W1 -->|"canonical programs"| S4
    W2 -->|"answer sheet per rep"| S2
    W3 -->|"additive family record"| S3

    S1 --> R1
    S2 --> R1
    S3 --> R1
    S4 --> R2
    S1 --> R2
    R1 --> R3
```

*Look for: every store has a reader; the baseline store (S3) is written only by the operator
runbook (additive) and read by the gate's family rule. No disconnected paths.*

## Integration Contracts (sequence)

```mermaid
sequenceDiagram
    participant OP as Operator (GB10)
    participant RN as run_gc_heldout.py
    participant LS as llama-swap :9000
    participant SB as gc_sandbox
    participant GT as gate battery (pytest test/)

    OP->>RN: --task-dir --out --model --rep (+family pins)
    RN->>SB: ensure_available() — refuse-loud
    RN->>LS: chat completion per row (2 retries, then abort rep)
    LS-->>RN: response (finish_reason recorded)
    RN->>RN: extract program (fence-first contract)
    RN-->>OP: rep dir: programs/ + rows/ + candidate.json + config.json
    OP->>GT: PO_EVAL_OUTPUT_DIR=rep-dir pytest tasks/gc-held-00X/test -q
    GT->>SB: execute program + reference asserts per row
    SB-->>GT: SandboxResult (pass/fail, reason)
    GT-->>OP: G-G1 contract + G-G2/G-G3 floor vs matching-family baseline
```

*Look for: the runner never grades; grades come only from the gate battery executing in the
sandbox. Nothing is fetched and discarded.*

## Task Dependencies

```mermaid
graph TD
    T1[TASK-GCH-001: Sandbox + integrity tests] --> T2[TASK-GCH-002: Pinned subset provisioning]
    T1 --> T3[TASK-GCH-003: gc_gates]
    T2 --> T3
    T2 --> T4[TASK-GCH-004: Task folders + Oracle]
    T3 --> T4
    T3 --> T5[TASK-GCH-005: Runner]
    T4 --> T6[TASK-GCH-006: Integrity battery + fixtures]
    T5 --> T6
    T6 --> T7[TASK-GCH-007: RESULTS + scope doc + runbook]

    style T4 fill:#cfc,stroke:#090
    style T5 fill:#cfc,stroke:#090
```

_Tasks with green background share wave 4 (no file conflicts); build runs them sequentially anyway._

## §4: Integration Contracts

### Contract: SANDBOX_RESULT_AND_AVAILABILITY
- **Producer task:** TASK-GCH-001
- **Consumer task(s):** TASK-GCH-002 (selection-rule validation), TASK-GCH-003 (grading), TASK-GCH-004 (gate tests), TASK-GCH-005 (pre-run probe)
- **Artifact type:** Python module `harness/gc_sandbox.py`
- **Format constraint:** `run_program(text, *, timeout_s, ...) -> SandboxResult(status∈{"pass","fail"}, reason, exit_code, stdout, stderr, seconds)`; `ensure_available()` raises `SandboxUnavailable` naming the missing isolation. Grader bugs raise; candidate failures return `status="fail"` — never conflated.
- **Validation method:** `tests/test_gc_sandbox_integrity.py` green; gate conftest imports both names.

### Contract: PINNED_ROW_SCHEMA_AND_MANIFEST
- **Producer task:** TASK-GCH-002
- **Consumer task(s):** TASK-GCH-003, TASK-GCH-004, TASK-GCH-005
- **Artifact type:** committed JSON (`input/rows/{ROW-ID}/row.json`, `input/manifest.json`)
- **Format constraint:** row.json canonical bytes = `json.dumps(row, indent=2, sort_keys=True) + "\n"`; manifest pins `{row_id, benchmark_task_id, sha256}` per row + selection rule + exclusions + licence/provenance; row ids unique across the whole suite (`HumanEval-N` / `mbpp-N`).
- **Validation method:** `gc_gates.verify_pins(task_dir)` returns no findings; integrity battery cross-task uniqueness test.

### Contract: ANSWER_SHEET_FORMAT
- **Producer task:** TASK-GCH-005 (runner) — Oracle variant produced by TASK-GCH-004
- **Consumer task(s):** TASK-GCH-004 (gate tests), TASK-GCH-006 (fixtures are answer sheets)
- **Artifact type:** directory (`PO_EVAL_OUTPUT_DIR`)
- **Format constraint:** `candidate.json` {model_id, lineage, base_family, quant, oracle:bool}; `programs/{ROW-ID}.py`; optional `rows/{ROW-ID}.json` {finish_reason, extraction} diagnostics. Family key = `"{base_family}/{quant}"` must exist in `harness/gc_baselines.json` unless oracle.
- **Validation method:** gate `test_answer_sheet_contract`; broken fixtures `missing-candidate-record`, `unknown-baseline-family` fail exactly their owning tests.

## Wave discipline

After every wave: `python3 -m pytest tests/ -q` green AND the failing set == baseline
(229 passed, captured pre-change). Frozen files byte-identical throughout (`git status` on
frozen paths clean). The smoke gate in the feature YAML makes this mechanical.
