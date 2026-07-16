"""Grades the candidate DCL at $PO_EVAL_OUTPUT_DIR (defaults to the task's
solution/ dir, so a bare pytest run validates the Oracle — the fleet-evals
oracle-on-bare-run convention, gc-held-001/po-held-001 pattern).

The grader shells out to the ONE vendored WASM checker via harness.dcl_gates
(harness/dcl/bin/) — there is no per-task checker copy. The candidate artifact
is a single file named `response.dcl` in the output dir."""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import dcl_gates  # noqa: E402


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def response_path(output_dir) -> Path:
    return output_dir / "response.dcl"
