# Implementation Guide — FEAT-EVAL-IDEA (Idea-Mode Held-Out Eval Tasks)

**Parent review:** TASK-REV-09AB (`.claude/reviews/TASK-REV-09AB-review-report.md`)
**Spec:** `features/idea-mode-held-out-evals/` (38 scenarios, 11 human-resolved assumptions)
**Execution mode:** sequential hand-build in-session (Context B, 2026-07-05); waves = commit
checkpoints, every commit leaves `pytest tests/` green.
**Wave 0 pre-flight:** `python3 harness/link_assets.py && python3 -m pytest tests/ -q` —
capture the pre-extension 33-green as the non-regression baseline for TASK-EVI-008.

## Standing invariants (every task, every commit)

- `docs/research/ideas/po-heldout-suite-scope.md`, `harness/po_contract.py`,
  `harness/grading.py`, `tests/test_verifier_integrity.py`, `harness/link_assets.py`,
  `harness/ASSETS.sha256`, `tasks/po-held-001..004/**`, existing fixtures: **byte-identical**.
- Never create `input/corpus/` in a new task (frozen 13-file assertion); never name an
  anchor file `coverage_checklist.json` (frozen area pin).
- New gates consume the parsed payload dict, never raw response text.
- New assets are fresh-authored, in-repo, zero client content.

## Data Flow: Read/Write Paths

```mermaid
flowchart LR
    subgraph Writes["Write Paths (build-time authoring)"]
        W1["TASK-EVI-001: addendum doc (DRAFT)"]
        W2["TASK-EVI-002: harness/idea_gates.py + run_po_eval.py --suite"]
        W3["TASK-EVI-003/004: task folders (anchors, oracles, briefs, roadmap)"]
        W4["TASK-EVI-005: frontier sheets (good fixtures)"]
        W5["TASK-EVI-006/007: fixture batteries + idea integrity tests"]
    end

    subgraph Storage["Storage"]
        S1[("docs/research/ideas/po-heldout-idea-extension-scope.md")]
        S2[("harness/idea_gates.py")]
        S3[("tasks/po-held-005-idea/, tasks/po-held-006-scope/")]
        S4[("tests/broken_fixtures/, tests/good_fixtures/")]
        S5[("tests/test_idea_verifier_integrity.py")]
    end

    subgraph Reads["Read Paths (grading & integrity)"]
        R1["per-task gate tests (pytest)"]
        R2["tests/test_verifier_integrity.py (frozen, auto-discovers)"]
        R3["run_po_eval.py --suite po-heldout-idea (12 new rollouts)"]
        R4["Rich: freeze commit on the addendum"]
    end

    W1 --> S1
    W2 --> S2
    W3 --> S3
    W4 --> S4
    W5 --> S4
    W5 --> S5

    S2 -->|"import"| R1
    S3 -->|"gates + anchors + oracle"| R1
    S3 -->|"TASK_IDS glob"| R2
    S4 -->|"FIXTURE_CASES / GOOD_FIXTURE_CASES globs"| R2
    S5 -->|"pytest collection"| R2
    S3 -->|"assembly branches"| R3
    S1 -->|"G-I1..4 verdict applied to R3's grades"| R4
```

Every write path has a live reader — no disconnection alert. The frozen integrity suite
(R2) reads the new tasks *automatically* via its globs, which is why fixtures must land
atomically with task folders.

## Integration Contracts (sequence)

```mermaid
sequenceDiagram
    participant A as Addendum (EVI-001)
    participant H as idea_gates.py (EVI-002)
    participant T as Task folders (EVI-003/004)
    participant F as Frontier sheets (EVI-005)
    participant B as Batteries (EVI-006/007)
    participant V as Validation (EVI-008)

    A->>H: anchors JSON schema + diagnostic contract (named findings, never bool)
    H->>T: matcher API (normalize, invention, constraint, subset, closure)
    T->>F: brief + roadmap + dry-run assembly
    F->>A: calibrated ASSUM-009 threshold (recorded pre-freeze)
    F->>B: frontier sheets as good fixtures + calibration evidence
    T->>B: oracles (fixtures = surgical mutations)
    B->>V: floor lists + integrity additions
    V->>A: measured baselines into the baseline table
    Note over A,V: Addendum stays DRAFT until Rich's freeze commit after EVI-008
```

## Task Dependencies

```mermaid
graph TD
    T1[TASK-EVI-001: Addendum DRAFT cx3] --> T2[TASK-EVI-002: Harness gates + runner cx5]
    T2 --> T3[TASK-EVI-003: po-held-005-idea cx6]
    T2 --> T4[TASK-EVI-004: po-held-006-scope cx6]
    T3 --> T5[TASK-EVI-005: Frontier sheets cx2 ATTENDED]
    T4 --> T5
    T3 --> T6[TASK-EVI-006: 005 battery cx5]
    T5 --> T6
    T4 --> T7[TASK-EVI-007: 006 battery cx4]
    T5 --> T7
    T6 --> T8[TASK-EVI-008: Validation + hand-off cx3]
    T7 --> T8
    T1 --> T8

    style T3 fill:#cfc,stroke:#090
    style T4 fill:#cfc,stroke:#090
    style T6 fill:#cfc,stroke:#090
    style T7 fill:#cfc,stroke:#090
```

_Green tasks are parallel-safe within their wave (003∥004; 006∥007). Execution is
sequential hand-build per Context B — waves act as commit checkpoints._

Waves: 1:[EVI-001] → 2:[EVI-002] → 3:[EVI-003, EVI-004] → 4:[EVI-005] → 5:[EVI-006, EVI-007] → 6:[EVI-008]

## §4: Integration Contracts

### Contract: ANCHOR_SCHEMA_AND_DIAGNOSTIC_CONTRACT
- **Producer task:** TASK-EVI-001 (addendum §instrument-contracts)
- **Consumer task(s):** TASK-EVI-002, TASK-EVI-003, TASK-EVI-004
- **Artifact type:** documented JSON schema + function return-shape contract
- **Format constraint:** anchors JSON = `{groups: [{id, alternates: [regex,...]}]}`;
  matcher returns structured findings naming the unlicensed detail / offending feature id
  (never a bare bool) — two feature scenarios assert the naming
- **Validation method:** TASK-EVI-002's seam test + unit tests

### Contract: IDEA_GATES_API
- **Producer task:** TASK-EVI-002
- **Consumer task(s):** TASK-EVI-003, TASK-EVI-004, TASK-EVI-006, TASK-EVI-007
- **Artifact type:** Python module (`harness/idea_gates.py`, stdlib-only)
- **Format constraint:** pure functions over the parsed payload dict; closure computed
  against the REFERENCE graph; central NFKC normalization; per-group licensing
- **Validation method:** consumer seam tests (EVI-003/004) + gate tests importing the module

### Contract: CALIBRATED_THRESHOLD
- **Producer task:** TASK-EVI-005
- **Consumer task(s):** TASK-EVI-006, TASK-EVI-007, TASK-EVI-001 (record), TASK-EVI-008 (baseline)
- **Artifact type:** addendum calibration-section entry + frontier good fixtures
- **Format constraint:** ASSUM-009 threshold decision (>2 or >3) with evidence, recorded
  BEFORE evasion/stuffing fixtures are cut and before the freeze
- **Validation method:** TASK-EVI-008's baseline check; fixtures must pass/fail per the
  recorded threshold
