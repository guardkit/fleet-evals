"""Grades the candidate spec at $PO_EVAL_OUTPUT_DIR (defaults to the task's solution/,
so a bare pytest run validates the Oracle).

Two things beyond po-held-007's conftest, both from harness/wire_idiom_gates.py: the
context the routing law's rules are given (the target repository, api_test, declared as
an HTTP surface — read from task.toml [wire_idiom]), and the census line printed at the
end of the grade saying how many worked examples the wire rule stamped.

Skips cannot pass here, for the same reason they cannot in po-held-007: the runners grade
a rep by the exit code of `pytest test/ -q`, and pytest exits 0 when a test skips.
`harness/could_not_measure.py` turns any skip into exit code 40 and names the check that
could not be measured. Two of its hooks share a name with the census hooks, so those two
are wrapped here rather than imported by name — pytest allows one function per hook
name per conftest.
"""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import could_not_measure, spec_gates, wire_idiom_gates  # noqa: E402
from harness.could_not_measure import (  # noqa: E402,F401 — pytest finds hooks by name
    EXIT_COULD_NOT_MEASURE,
    pytest_collectreport,
    pytest_runtest_logreport,
    pytest_sessionfinish,
)


def pytest_sessionstart(session):
    could_not_measure.pytest_sessionstart(session)
    wire_idiom_gates.pytest_sessionstart(session)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    could_not_measure.pytest_terminal_summary(terminalreporter, exitstatus, config)
    wire_idiom_gates.pytest_terminal_summary(terminalreporter, exitstatus, config)


@pytest.fixture(scope="session")
def task_dir() -> Path:
    return TASK_DIR


@pytest.fixture(scope="session")
def output_dir() -> Path:
    return Path(os.environ.get("PO_EVAL_OUTPUT_DIR", TASK_DIR / "solution"))


@pytest.fixture(scope="session")
def rules_context(task_dir):
    """What the rules know beyond the scenario text: api_test has an HTTP surface."""
    return wire_idiom_gates.load_context(task_dir)


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
