"""Grades the candidate plan tree at $PO_EVAL_OUTPUT_DIR (defaults to the
task's solution/ dir, so a bare pytest run validates the Oracle)."""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import spec_gates  # noqa: E402

SLUG = "member-directory-search"


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def feature_yaml(output_dir):
    return spec_gates.load_feature_yaml(output_dir)


@pytest.fixture(scope="session")
def tagged_feature_text(output_dir) -> str:
    path = output_dir / "features" / SLUG / f"{SLUG}.feature"
    assert path.is_file(), f"tagged spec copy missing: {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def parsed(tagged_feature_text):
    return spec_gates.parse_feature(tagged_feature_text)


@pytest.fixture(scope="session")
def pinned_input_feature() -> str:
    return (TASK_DIR / "input" / "features" / SLUG / f"{SLUG}.feature").read_text(encoding="utf-8")
