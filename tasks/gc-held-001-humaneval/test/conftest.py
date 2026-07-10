"""Grades the candidate answer sheet at $PO_EVAL_OUTPUT_DIR (defaults to the
task's solution/ dir, so a bare pytest run validates the Oracle).

Grading happens ONCE per gate run (session-scoped `grades` fixture) and only
after pins verify and the sandbox proves its isolation — the pre-grade block
(G-G4) is enforced structurally, not by convention."""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import gc_gates, gc_sandbox  # noqa: E402


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def candidate(output_dir) -> dict:
    return gc_gates.load_candidate(output_dir)


@pytest.fixture(scope="session")
def grades(task_dir, output_dir) -> dict:
    """Execution results, computed once. Pins and sandbox isolation are
    re-checked here so no candidate code can execute against drifted content
    or outside the sandbox even if test ordering changes."""
    pin_findings = gc_gates.verify_pins(task_dir)
    assert pin_findings == [], f"grading blocked before execution: {pin_findings}"
    gc_sandbox.ensure_available()
    return gc_gates.grade_rows(task_dir, output_dir)
