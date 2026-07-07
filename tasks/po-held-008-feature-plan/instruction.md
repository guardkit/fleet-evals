# Task: po-held-008-feature-plan — headless `/feature-plan` from a pinned spec

You are the architect feature-plan tool (`architect_feature_plan`,
FEAT-SPL-008) running **headless** (`--no-questions`, structured output on —
the default). Plan the feature specified by the pinned `/feature-spec` triple
at `input/features/member-directory-search/` (the `_summary.md` is your
`--context` file; the `.feature` scenarios are the behaviour contract).

## Output contract (graded)

Produce a repo-root shaped tree:

```
.guardkit/features/{FEAT-ID}.yaml        # feature/task/wave YAML
tasks/backlog/member-directory-search/
├── README.md
├── IMPLEMENTATION-GUIDE.md              # with the mandatory Mermaid diagrams
└── TASK-{...}-{kebab-title}.md          # one per task
features/member-directory-search/
└── member-directory-search.feature      # the input spec, Step-11 tagged
```

- **Feature YAML** must pass the deterministic oracle:
  `guardkit feature validate {FEAT-ID}` (exit 0) — schema layer
  (feature_loader Pydantic pins) plus structural layer (task files on disk,
  orchestration completeness both directions, resolvable acyclic
  dependencies, no intra-wave dependencies).
- **Task markdown frontmatter** (Step 9, all REQUIRED): `id` matching the
  YAML task, explicit `task_type` (valid value or alias — never omitted),
  `feature_id`, `wave` matching the task's 1-indexed `parallel_groups` wave,
  `implementation_mode`, `complexity`, `dependencies`.
- **Mode assignment** (pinned generator default): `task-work` for
  complexity ≥ 4, `direct` for ≤ 3.
- **Implementation/refactor tasks** carry the lint-compliance acceptance
  criterion ("All modified files pass project-configured lint/format checks
  with zero errors").
- **IMPLEMENTATION-GUIDE.md** carries the mandatory Mermaid diagrams:
  data-flow (`flowchart`, always) and the task-dependency graph (`graph TD`,
  ≥ 3 tasks).
- **Step 11 (BDD linking)**: tag the spec's scenarios `@task:<TASK-ID>` by
  inserting standalone tag lines — **never rewrite an existing line of the
  input `.feature`**. Every tag must name a real plan task; every `@smoke`
  scenario must be linked; every feature-type task must own at least one
  scenario (a task no scenario motivates is invented work).

## Harness assembly

Answer sheets for this task are produced by the FEAT-SPL-008 target-terminal
harness (specialist-agent) invoking the pinned serving template headless with
the pinned triple placed at `features/member-directory-search/` in a fresh
workspace, one fresh session per rep. This task is NOT assembled by
`harness/run_po_eval.py` (the artifact is a file tree, not `response.txt`).
Grading: `python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at
the workspace root.
