"""Grades the candidate spec triple at $PO_EVAL_OUTPUT_DIR (defaults to the
task's solution/ dir, so a bare pytest run validates the Oracle).

CORRECTION 2026-08-22 — A SKIPPED BAR CAN NO LONGER SCORE GREEN.

Three checks in `test_gate_po_held_007_f1_seed.py` step aside when the graded
tree carries no `qa/pass-bar-seed-*.yaml`. Until today that was invisible: the
runners grade a rep by the exit code of `pytest test/ -q`, and pytest exits 0
when a test skips. Measured on this repo's own assets before the change: every
one of the six registered GOOD fixtures scored `14 passed, 3 skipped`, **exit
0** — a runner would have written all three of those axes down as PASSED while
they measured nothing at all.

`harness/could_not_measure.py` now refuses to let any skip in this grade exit 0.
The grade names the checks that could not be measured and returns exit code 40,
deliberately outside pytest's own range, so "could not measure" is legible as
something other than "measured and failed".

WHAT THIS DOES NOT DECIDE, and it is the open question. The seed file is written
by production's `/feature-spec` POST-PROCESSOR, not by the model, and this task's
own instruction.md never asks the candidate for it. So whether these three axes
belong in this exam at all is a scope question for Rich, recorded in
`docs/research/ideas/po-heldout-spec-extension-scope.md` §11.6. Until he rules,
the honest state is the one you now get: the axes stay, and a tree without a seed
reads "could not measure" rather than "passed".
"""
import os
import sys
from pathlib import Path

import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TASK_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import spec_gates  # noqa: E402
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


@pytest.fixture(scope="session")
def digest(paths):
    """The fourth file (Part A.4, from 2026-08-14)."""
    return spec_gates.load_digest(paths["digest"])
