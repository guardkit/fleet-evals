"""Grades the candidate plan tree at $PO_EVAL_OUTPUT_DIR (defaults to the
task's solution/ dir, so a bare pytest run validates the reference answer).

TWO CORRECTIONS, both 2026-08-22, both kept visible.

MORNING — the spec `.feature` copy became OPTIONAL. Until then this file
asserted that the graded tree contained `features/<slug>/<slug>.feature`, a
copy of the specification with tag lines added marking which plan task covers
which scenario. The tool this exam grades cannot produce that file and is not
asked to (STEP-11-NOTE.md has the measurements and the dates). The copy is
therefore looked up, not demanded.

AFTERNOON — the skip that scored green was closed. Making the check optional
left a worse hole: with no copy to grade, the check SKIPPED, and pytest exits 0
when tests skip, so every runner that grades a run by its exit code would have
recorded the bar as PASSED while it measured nothing. Two things changed:

  * the fifth bar was re-pointed, on Rich's ruling, at something the plan tool
    can and does emit — the coverage map in the plan's own feature YAML — and
    the new check (`test_scenario_coverage_map`) never skips; and
  * `pytest_sessionfinish` below refuses to let ANY skip in this grade exit 0.
    A skipped check means COULD NOT MEASURE, and this task's grade now says so
    in its exit code rather than in a line of output nobody parses.

The fixtures that existed only to feed the retired tag check (`parsed`,
`tagged_feature_text`) are gone with it. `tagged_feature_paths` stays: the
spec-preservation bar still grades every copy of the specification found in the
tree, exactly as it did this morning.
"""
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


def spec_copy_paths(output_dir: Path) -> list[Path]:
    """Every place a copy of THIS spec's `.feature` could sit in the graded
    tree, using guardkit's own documented discovery convention (feature-plan.md
    Step 11, 'Feature-file discovery convention'): the nested `/feature-spec`
    default `features/<slug>/<slug>.feature`, plus the flat fallback
    `features/<slug>.feature`, plus any deeper nesting under `features/`.

    Deliberately bounded to `features/` and to THIS slug's filename: the graded
    root can be a real repo worktree carrying other features' specs and a `.git`
    directory, and a gate that walks those is a gate that fails for reasons that
    have nothing to do with the plan under test.
    """
    features = Path(output_dir) / "features"
    if not features.is_dir():
        return []
    found = {p for p in features.rglob(f"{SLUG}.feature") if p.is_file()}
    flat = features / f"{SLUG}.feature"
    if flat.is_file():
        found.add(flat)
    return sorted(found)


@pytest.fixture(scope="session")
def tagged_feature_paths(output_dir) -> list[Path]:
    return spec_copy_paths(output_dir)


@pytest.fixture(scope="session")
def pinned_input_feature() -> str:
    return (TASK_DIR / "input" / "features" / SLUG / f"{SLUG}.feature").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# THE SKIP THAT SCORED GREEN — closed here, for every runner at once
# ---------------------------------------------------------------------------
#
# THE DEFECT, in plain words. Every runner in this repo decides whether a graded
# run passed by looking at the exit code of `python3 -m pytest test/ -q`
# (`harness/run_po_eval.py` grade_rep; `harness/run_po_spec_eval.py` grade_rep).
# pytest exits 0 when a test is SKIPPED. So a check that quietly stepped aside —
# because the thing it wanted to look at was not there — was written down as a
# PASS. A bar that measured nothing scored the same as a bar that measured
# everything, and nothing in the receipt showed the difference.
#
# THE FIX. Any skip in this task's grade makes the run exit non-zero, with its
# own code, and prints the skipped checks by name. The code is deliberately
# outside pytest's own range (0 ok / 1 failed / 2 interrupted / 3 internal /
# 4 usage / 5 nothing collected) so a reader can tell "could not measure" from
# "measured and failed" at a glance, while every existing `returncode == 0`
# check treats it as the failure it is.
#
# This does not stop anyone writing a legitimately conditional check later. It
# stops such a check being scored as a pass — which is the part that was wrong.

EXIT_COULD_NOT_MEASURE = 40

_skipped: "dict[str, str]" = {}


def pytest_runtest_logreport(report):
    """Record every skipped check, whichever phase it skipped in."""
    if not report.skipped:
        return
    reason = ""
    longrepr = getattr(report, "longrepr", None)
    if isinstance(longrepr, tuple) and len(longrepr) == 3:
        reason = str(longrepr[2])
    elif longrepr is not None:
        reason = str(longrepr)
    _skipped.setdefault(report.nodeid, reason)


def pytest_sessionfinish(session, exitstatus):
    """A grade that could not measure something must not exit 0."""
    if not _skipped:
        return
    print("\n" + "=" * 72)
    print("COULD NOT MEASURE — this grade skipped checks, so it is NOT a pass:")
    for nodeid, reason in sorted(_skipped.items()):
        print(f"  - {nodeid}\n      {reason}")
    print("A skipped bar measures nothing. Recording it as green is the defect")
    print("this guard exists to prevent (see the note at the top of this file).")
    print("=" * 72)
    if exitstatus == 0:
        session.exitstatus = EXIT_COULD_NOT_MEASURE
