"""Grades the candidate DCL at $DCL_EVAL_OUTPUT_DIR (defaults to the task's
solution/ dir, so a bare pytest run validates the reference — the fleet-evals
oracle-on-bare-run convention, po-held-001/gc-held-001 pattern).

SPIKE-CLASS: this grader is intentionally self-contained — it shells out to the
vendored WASM checker under bin/ and depends on NOTHING in the repo harness/.
The candidate artifact is a single file named `response.dcl` in the output dir."""
import os
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
BIN_DIR = TASK_DIR / "bin"
CHECKER = BIN_DIR / "dcl-check.mjs"


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def bin_dir() -> Path:
    return BIN_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("DCL_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def response_path(output_dir) -> Path:
    return output_dir / "response.dcl"
