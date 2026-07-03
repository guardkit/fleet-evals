# Implement FEAT-9DDE: add a `--json` flag to `/task-status`

The repository at `/app` is GuardKit, a markdown-driven development workflow
toolkit. Implement the feature below exactly as specified. The feature has two
parts: a deterministic producer script, and the wiring that makes it reachable
from the `/task-status` command specs.

## Part 1 — Implement the task-status-json producer script

Create a deterministic Python producer script at
`installer/core/commands/lib/task_status_json.py` that scans the project's
`tasks/` directories, parses task frontmatter, and emits the task dashboard as
stable, machine-readable JSON to stdout.

This is the deterministic producer for the `/task-status --json` flag — same
pattern as `generate_feature_yaml.py` (R1) and `feature_plan_bdd_link.py` (R2).
The JSON must be byte-stable across runs against the same task state: fixed key
order, tasks sorted by `(status, id)` — status in kanban order (backlog,
in_progress, in_review, blocked, completed) — and missing frontmatter fields
emitted as `null` (never omitted).

**Reuse, don't reimplement**: frontmatter parsing already exists in
`installer/core/commands/lib/task_utils.py` (`parse_task_frontmatter`,
`read_task_file`).

### JSON Schema (v1)

```json
{
  "schema_version": "1.0",
  "generated_at": "<ISO 8601 UTC>",
  "base_path": ".",
  "summary": {
    "backlog": 0, "in_progress": 0, "in_review": 0,
    "blocked": 0, "completed": 0, "total": 0
  },
  "tasks": [
    {
      "id": "TASK-XXXX",
      "title": "...",
      "status": "backlog",
      "priority": "high",
      "task_type": "feature",
      "complexity": 4,
      "tags": [],
      "created": "...",
      "updated": "...",
      "epic": null,
      "feature": null,
      "parent_review": null,
      "feature_id": null,
      "file_path": "tasks/backlog/TASK-XXXX-....md"
    }
  ]
}
```

### CLI Contract

```bash
python3 task_status_json.py [TASK-ID] [--base-path PATH]
```

- No args: full dashboard JSON (summary + all tasks)
- Positional `TASK-ID`: single-task JSON object (task shape only, no
  `summary`); exit 1 with a stderr message if not found
- `--base-path`: project root (default: cwd)
- Output: `json.dumps(..., indent=2)` to stdout; nothing else on stdout

### Acceptance Criteria

- `installer/core/commands/lib/task_status_json.py` exists with a `main()`
  entry point and `if __name__ == "__main__":` guard
- Scans `tasks/backlog/`, `tasks/in_progress/`, `tasks/in_review/`,
  `tasks/blocked/`, `tasks/completed/` recursively (including feature
  subfolders like `tasks/backlog/{feature-slug}/` and archive folders like
  `tasks/completed/YYYY-MM/`)
- Emits schema v1 JSON to stdout with fixed key order and tasks sorted by
  `(status, id)`
- Missing frontmatter fields are emitted as `null`, never omitted (single-task
  output includes every schema field)
- Malformed frontmatter degrades gracefully: task entry emitted with `id`
  derived from filename and `"parse_error": true`, sorted after all valid
  tasks; malformed tasks are excluded from the summary counts; the script
  never crashes on one bad file
- Positional `TASK-ID` argument emits single-task JSON; unknown ID exits 1
  with a stderr message naming the task
- `generated_at` is the only non-deterministic field; everything else must be
  byte-stable across two invocations against the same tree

## Part 2 — Register the bin entry and wire `--json` into the command specs

Make the producer reachable from `/task-status --json`:

1. Add `installer/core/commands/lib/task_status_json.py` to
   `installer/core/commands/bin-entries.txt` (with a comment explaining it is
   the `/task-status --json` producer), so `install.sh` exposes it as
   `~/.agentecflow/bin/task-status-json`.
2. Add a `--json` flag section to **both** command specs:
   - `installer/core/commands/task-status.md`
   - `.claude/commands/task-status.md`

   The section must instruct Claude: *when `--json` is passed, execute
   `python3 ~/.agentecflow/bin/task-status-json [TASK-ID] --base-path .` via
   the Bash tool and output its stdout verbatim — do NOT reformat, reorder, or
   annotate the JSON.* Include the schema v1 example for reader reference.
3. Point the orphaned `export:json` mention in
   `.claude/commands/task-status.md` at the new `--json` flag (closing the
   existing runner-without-producer orphan).

### Acceptance Criteria

- `bin-entries.txt` contains the new line with an explanatory comment,
  following the existing R1/R2 comment style
- `installer/core/commands/task-status.md` documents the `--json` flag with
  the verbatim-output execution instruction and schema v1 example
- `.claude/commands/task-status.md` documents the `--json` flag identically
- Both specs state that `--json` combined with a `TASK-ID` emits a single-task
  object
- Default (no-flag) behaviour of both specs is unchanged
