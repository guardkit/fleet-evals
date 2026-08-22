"""Grades the candidate plan tree at $PO_EVAL_OUTPUT_DIR (defaults to the
task's solution/ dir, so a bare pytest run validates the Oracle).

CORRECTION 2026-08-22 — the spec `.feature` copy is OPTIONAL here.
Until today this file asserted that the graded tree contained
`features/<slug>/<slug>.feature`, the Step-11 @task-tagged copy of the input
spec. The tool this exam grades cannot produce that file and is not asked to:
see STEP-11-NOTE.md in the task directory for the measurements and the dates.
The copy is therefore looked up, not demanded — present, it is graded exactly
as before; absent, the two tests that need it say so instead of erroring at
fixture setup and hiding the rest of the grade.
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
def tagged_feature_text(tagged_feature_paths) -> str | None:
    """The graded tree's copy of the spec, or None when it holds none.

    None is NOT a defect — see STEP-11-NOTE.md. The plan tool's four artefact
    shapes cannot carry a `.feature` file at all.
    """
    if not tagged_feature_paths:
        return None
    # PREFER A TAGGED COPY OVER SORT ORDER. Taking paths[0] made the whole
    # linkage axis depend on filename ordering: a tree holding an untagged copy
    # that sorts first and a TAGGED copy that sorts second would be judged on
    # the untagged one, and a dangling `@task:` tag in the other file would
    # never be graded. Measured: with the order reversed the same tree flips
    # between "8 passed, 1 skipped" and a caught `dangling_task_tag`. Select on
    # content, never on order; fall back to the first copy when none is tagged.
    for candidate in tagged_feature_paths:
        text = candidate.read_text(encoding="utf-8")
        if "@task:" in text:
            return text
    return tagged_feature_paths[0].read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def parsed(tagged_feature_text):
    if tagged_feature_text is None:
        return None
    return spec_gates.parse_feature(tagged_feature_text)


@pytest.fixture(scope="session")
def pinned_input_feature() -> str:
    return (TASK_DIR / "input" / "features" / SLUG / f"{SLUG}.feature").read_text(encoding="utf-8")
