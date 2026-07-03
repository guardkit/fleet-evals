"""Independent verifier for abl-faud (FEAT-FAUD re-implementation).

Asserts the observable behaviour of the landed implementation (guardkit
8e6c5e9cf: feature-status staleness auditor), authored from the landed diff —
independent of any eval-time agent output by construction.

Black-box: builds synthetic guardkit project trees under tmp_path and drives
the installed `guardkit-py feature audit` console script as a subprocess,
exactly as CI would.
"""

import subprocess
from pathlib import Path

import pytest
import yaml

APP = Path("/app")
MODULE = APP / "guardkit/orchestrator/feature_audit.py"


def write_feature(features_dir: Path, feature_id: str, status: str, tasks) -> Path:
    features_dir.mkdir(parents=True, exist_ok=True)
    path = features_dir / f"{feature_id}.yaml"
    path.write_text(
        yaml.safe_dump({"id": feature_id, "status": status, "tasks": tasks}),
        encoding="utf-8",
    )
    return path


def complete_task(repo: Path, task_id: str) -> None:
    d = repo / "tasks" / "completed" / "2026-06"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{task_id}-done.md").write_text(f"# {task_id}\n", encoding="utf-8")


@pytest.fixture()
def stale_repo(tmp_path: Path) -> Path:
    """One stale feature (dict task schema, all tasks completed but declared
    in_progress), one clean completed feature (bare-string schema), one clean
    partially-done feature (must infer in_progress, NOT stale)."""
    repo = tmp_path / "proj"
    features = repo / ".guardkit" / "features"
    write_feature(features, "FEAT-STALE", "in_progress",
                  [{"id": "TASK-ST-001"}, {"id": "TASK-ST-002"}])
    complete_task(repo, "TASK-ST-001")
    complete_task(repo, "TASK-ST-002")
    write_feature(features, "FEAT-CLEAN", "completed", ["TASK-CL-001"])
    complete_task(repo, "TASK-CL-001")
    write_feature(features, "FEAT-PART", "in_progress",
                  [{"id": "TASK-PA-001"}, {"id": "TASK-PA-002"}])
    complete_task(repo, "TASK-PA-001")
    return repo


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "proj"
    write_feature(repo / ".guardkit" / "features", "FEAT-CLEAN", "completed",
                  ["TASK-CL-001"])
    complete_task(repo, "TASK-CL-001")
    return repo


def run_audit(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["guardkit-py", "feature", "audit", *args],
        capture_output=True,
        text=True,
        cwd=str(repo),
    )


def test_auditor_module_exists():
    assert MODULE.exists(), f"auditor core missing at {MODULE}"


def test_stale_detected_exit_1(stale_repo: Path):
    proc = run_audit(stale_repo)
    assert proc.returncode == 1, (
        f"expected exit 1 with a stale feature, got {proc.returncode}:\n"
        + proc.stdout + proc.stderr
    )
    out = proc.stdout.lower()
    assert "1 stale feature(s) found" in out, proc.stdout
    assert "feat-stale" in out, proc.stdout


def test_partial_feature_not_stale(stale_repo: Path):
    # FEAT-PART (1/2 completed, declared in_progress) must not be counted
    # stale — the stale count in the summary is exactly 1.
    proc = run_audit(stale_repo)
    assert "1 stale feature(s) found" in proc.stdout.lower(), proc.stdout


def test_fix_reconciles_and_clean_exit_0(stale_repo: Path):
    proc = run_audit(stale_repo, "--fix")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = yaml.safe_load(
        (stale_repo / ".guardkit/features/FEAT-STALE.yaml").read_text()
    )
    assert data["status"] == "completed", data
    # Non-stale features untouched.
    clean = yaml.safe_load(
        (stale_repo / ".guardkit/features/FEAT-CLEAN.yaml").read_text()
    )
    assert clean["status"] == "completed"
    part = yaml.safe_load(
        (stale_repo / ".guardkit/features/FEAT-PART.yaml").read_text()
    )
    assert part["status"] == "in_progress"
    # Audit after fix: clean, exit 0.
    proc2 = run_audit(stale_repo)
    assert proc2.returncode == 0, proc2.stdout + proc2.stderr
    assert "no stale features" in proc2.stdout.lower(), proc2.stdout


def test_clean_repo_exit_0(clean_repo: Path):
    proc = run_audit(clean_repo)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "no stale features" in proc.stdout.lower(), proc.stdout
