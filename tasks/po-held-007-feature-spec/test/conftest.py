"""Grades the candidate spec triple at $PO_EVAL_OUTPUT_DIR (defaults to the
task's solution/ dir, so a bare pytest run validates the Oracle)."""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import spec_gates  # noqa: E402


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def paths(output_dir):
    return spec_gates.spec_paths(output_dir)


@pytest.fixture(scope="session")
def feature_text(paths) -> str:
    return paths["feature"].read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def parsed(feature_text):
    return spec_gates.parse_feature(feature_text)


@pytest.fixture(scope="session")
def manifest(paths):
    return spec_gates.load_assumptions_manifest(paths["assumptions"])


@pytest.fixture(scope="session")
def summary_text(paths) -> str:
    return paths["summary"].read_text(encoding="utf-8")
