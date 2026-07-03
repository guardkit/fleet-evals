"""Independent verifier for abl-spike-001 (FEAT-9DDE re-implementation).

Asserts the observable behaviour of the landed implementation (guardkit
f9c4070be: /task-status --json producer + wiring), authored from the landed
diff — independent of any eval-time agent output by construction.

Hermetic: builds synthetic task trees under tmp_path and invokes the producer
as a subprocess, exactly as the /task-status command spec shells out to it.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

APP = Path("/app")
PRODUCER = APP / "installer/core/commands/lib/task_status_json.py"

# Task-shape fields from the FEAT-9DDE schema-v1 example (TASK-TSJ-001).
SPEC_TASK_FIELDS = [
    "id", "title", "status", "priority", "task_type", "complexity", "tags",
    "created", "updated", "epic", "feature", "parent_review", "feature_id",
    "file_path",
]


def make_task_md(path: Path, task_id: str, status: str, extra: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"id: {task_id}\n"
        f"title: Synthetic {task_id}\n"
        f"status: {status}\n"
        f"{extra}"
        "---\n\n# Body\n",
        encoding="utf-8",
    )


@pytest.fixture()
def task_tree(tmp_path: Path) -> Path:
    """Synthetic project: 4 valid tasks across states (one in a feature
    subfolder, one in a completed/YYYY-MM archive) + 1 malformed file."""
    root = tmp_path / "proj"
    tasks = root / "tasks"
    make_task_md(
        tasks / "backlog" / "TASK-AAA-001-sample.md", "TASK-AAA-001", "backlog",
        extra="priority: high\ntask_type: feature\ncomplexity: 3\ntags: [x, y]\n",
    )
    make_task_md(
        tasks / "backlog" / "feature-x" / "TASK-CCC-003-nested.md",
        "TASK-CCC-003", "backlog",
    )
    make_task_md(
        tasks / "in_progress" / "TASK-BBB-002-doing.md", "TASK-BBB-002",
        "in_progress",
    )
    make_task_md(
        tasks / "completed" / "2026-05" / "TASK-DDD-004-done.md",
        "TASK-DDD-004", "completed",
    )
    bad = tasks / "backlog" / "TASK-EEE-BAD-malformed.md"
    bad.write_text("no frontmatter delimiters here\n", encoding="utf-8")
    (tasks / "in_review").mkdir(parents=True, exist_ok=True)
    (tasks / "blocked").mkdir(parents=True, exist_ok=True)
    return root


def run_producer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PRODUCER), *args],
        capture_output=True,
        cwd=str(APP),
    )


def test_producer_script_exists():
    assert PRODUCER.exists(), f"producer missing at {PRODUCER}"


def test_dashboard_schema_and_ordering(task_tree: Path):
    proc = run_producer("--base-path", str(task_tree))
    assert proc.returncode == 0, proc.stderr.decode()
    data = json.loads(proc.stdout)
    # Fixed top-level key order (schema v1).
    assert list(data.keys()) == [
        "schema_version", "generated_at", "base_path", "summary", "tasks",
    ]
    assert data["schema_version"] == "1.0"
    # Malformed task excluded from counts.
    assert data["summary"] == {
        "backlog": 2, "in_progress": 1, "in_review": 0,
        "blocked": 0, "completed": 1, "total": 4,
    }
    # Kanban status order, then id; parse_error entry sorted last.
    assert [t["id"] for t in data["tasks"]] == [
        "TASK-AAA-001", "TASK-CCC-003", "TASK-BBB-002", "TASK-DDD-004",
        "TASK-EEE-BAD-malformed",
    ]
    assert data["tasks"][-1].get("parse_error") is True


def test_dashboard_byte_stable_modulo_timestamp(task_tree: Path):
    a = run_producer("--base-path", str(task_tree)).stdout
    b = run_producer("--base-path", str(task_tree)).stdout
    assert a, "empty stdout"

    def strip_ts(raw: bytes) -> bytes:
        return b"\n".join(
            line for line in raw.splitlines() if b"generated_at" not in line
        )

    assert strip_ts(a) == strip_ts(b)


def test_single_task_null_filled_and_byte_stable(task_tree: Path):
    a = run_producer("TASK-BBB-002", "--base-path", str(task_tree))
    b = run_producer("TASK-BBB-002", "--base-path", str(task_tree))
    assert a.returncode == 0, a.stderr.decode()
    # No generated_at in single-task output => fully byte-identical.
    assert a.stdout == b.stdout
    data = json.loads(a.stdout)
    assert data["id"] == "TASK-BBB-002"
    assert "summary" not in data
    # Every schema field present; fields absent from frontmatter are null,
    # never omitted.
    missing = [f for f in SPEC_TASK_FIELDS if f not in data]
    assert not missing, f"schema fields omitted: {missing}"
    for field in [
        "priority", "task_type", "complexity", "tags", "created", "updated",
        "epic", "feature", "parent_review", "feature_id",
    ]:
        assert data[field] is None, f"{field} should be null, got {data[field]!r}"


def test_unknown_task_id_exits_1_with_stderr(task_tree: Path):
    proc = run_producer("TASK-NOPE-999", "--base-path", str(task_tree))
    assert proc.returncode == 1
    assert proc.stdout == b"", "nothing but JSON may go to stdout"
    assert b"TASK-NOPE-999" in proc.stderr


def test_bin_entry_registered():
    manifest = APP / "installer/core/commands/bin-entries.txt"
    entries = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    target = "installer/core/commands/lib/task_status_json.py"
    assert target in entries, f"{target} not listed in bin-entries.txt"
    assert (APP / target).exists()


def test_command_specs_wired():
    for spec in [
        APP / "installer/core/commands/task-status.md",
        APP / ".claude/commands/task-status.md",
    ]:
        assert "--json" in spec.read_text(encoding="utf-8"), f"{spec} not wired"
