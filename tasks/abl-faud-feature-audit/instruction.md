# Implement FEAT-FAUD: feature-status staleness auditor

The repository at `/app` is GuardKit, a markdown-driven development workflow
toolkit. Feature YAMLs under `.guardkit/features/*.yaml` declare a `status`
field, but nothing keeps it honest: a feature whose tasks have all been
completed can still say `in_progress`. Implement a `guardkit feature audit`
command that detects stale feature-YAML statuses by inferring each feature's
real status from whether its tasks live under `tasks/completed/`, and
reconciles them with `--fix`.

## Part 1 — Auditor core module

Create `guardkit/orchestrator/feature_audit.py` with:

- A `FeatureAuditRow` dataclass: `feature_id`, `declared_status`,
  `inferred_status`, `tasks_total`, `tasks_completed`, `tasks_pending`,
  `is_stale` (true when declared differs from inferred).
- `audit_features(repo_root: Path) -> List[FeatureAuditRow]` scanning
  `.guardkit/features/*.yaml`.

Inference rules:

- A task counts as **completed** when a markdown file whose name contains the
  task id exists anywhere under `tasks/completed/` (recursive — archive
  subfolders like `tasks/completed/2026-06/` included).
- Feature YAMLs declare `tasks` as a list of mappings
  (`{"id": "TASK-XXX-YYYY", "name": ..., "file_path": ...}`); older or
  hand-written forms may use bare id strings. **Both schemas must work.**
- Status inference from counts: no tasks → `planned`; all tasks completed →
  `completed`; some but not all completed → `in_progress`.
- Unparseable or non-mapping YAML files are skipped gracefully (logged, never
  crash the audit).

## Part 2 — CLI subcommand

Add an `audit` subcommand to the existing `feature` command group
(`guardkit/cli/feature.py`), so it is reachable as `guardkit feature audit`
(the CLI group behind the `guardkit-py` console script):

- Prints a table: Feature | Declared | Inferred | Tasks (completed/total) |
  Stale? — stale rows marked with ⚠.
- Prints a summary line: `N stale feature(s) found.` when stale features
  exist, `No stale features.` when clean.
- **Exit codes (CI gate):** exit `1` when stale features exist and `--fix`
  was not given; exit `0` when clean.
- `--fix`: update the `status` field of each stale feature YAML in place to
  the inferred status, report each update, and exit `0`.

## Acceptance Criteria

- `audit_features` returns one row per feature YAML with correct counts and
  staleness for both task schemas (dict and bare-string)
- `guardkit feature audit` exits 1 on a repo with ≥1 stale feature and prints
  the stale count; exits 0 on a clean repo
- `guardkit feature audit --fix` rewrites stale YAML statuses to the inferred
  status and exits 0; a subsequent audit is clean
- A feature with only some tasks completed infers `in_progress` and is NOT
  stale when declared as such
- Unit tests cover the core module and the CLI paths
