"""Grades the candidate output at $PO_EVAL_OUTPUT_DIR (defaults to the task's
solution/ dir, so a bare pytest run validates the Oracle)."""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def raw_response(output_dir) -> str:
    from harness.grading import load_response
    return load_response(output_dir)
