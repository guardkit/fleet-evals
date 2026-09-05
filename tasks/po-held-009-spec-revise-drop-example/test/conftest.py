"""Grades the revised spec at $PO_EVAL_OUTPUT_DIR (defaults to the task's
solution/, so a bare pytest run validates the Oracle) against the spec that was
sent back and the note that sent it back.

The note lives in this task's task.toml `[revise]` table. It is data, not code:
a different note is a different table, never a different grader.

Skips cannot pass here, for the same reason they cannot in po-held-007: the
runners grade a rep by the exit code of `pytest test/ -q`, and pytest exits 0
when a test skips. `harness/could_not_measure.py` turns any skip into exit code
40 and names the check that could not be measured.
"""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import revise_gates, spec_gates  # noqa: E402
from harness.could_not_measure import (  # noqa: E402,F401 — pytest finds hooks by name
    EXIT_COULD_NOT_MEASURE,
    pytest_collectreport,
    pytest_runtest_logreport,
    pytest_sessionfinish,
    pytest_sessionstart,
    pytest_terminal_summary,
)


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def note(task_dir) -> dict:
    """The words Rich sent back on the card, and what they asked for."""
    return revise_gates.load_note(task_dir)


@pytest.fixture(scope="session")
def prior_paths(task_dir):
    """The four-file spec that was sent back for revision."""
    return spec_gates.spec_paths(task_dir / "input" / "prior")


@pytest.fixture(scope="session")
def prior_sentences(prior_paths) -> list:
    return revise_gates.digest_sentences(spec_gates.load_digest(prior_paths["digest"]))


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
def digest(paths):
    return spec_gates.load_digest(paths["digest"])


@pytest.fixture(scope="session")
def produced_sentences(digest) -> list:
    return revise_gates.digest_sentences(digest)
