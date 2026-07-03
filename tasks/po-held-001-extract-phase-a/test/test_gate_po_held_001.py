"""Gate tests: phased extract, Phase A (EpicPlan). Axes per po-heldout-suite-scope.md §3.3/§5."""
import pytest

from harness import grading
from harness.po_contract import validate_epic_plan

MIN_EPICS = 5      # scope §5 G3 anti-collapse floor (April baseline: 8)
MIN_FEATURES = 18  # scope §5 G3 anti-collapse floor (April baseline: 36 stubs)


@pytest.fixture(scope="module")
def payload(raw_response):
    return grading.parse_response(raw_response)


def test_serving_shape(raw_response):
    """G1: exactly one <think> block, then exactly one JSON object."""
    grading.parse_response(raw_response)


def test_schema_valid(payload):
    """G1: EpicPlan schema battery (harness/po_contract.py, Pydantic-faithful + CONTRACT rules)."""
    issues = validate_epic_plan(payload)
    assert issues == [], "\n" + "\n".join(issues)


def test_grounding(payload, task_dir):
    """G2: every cited document name resolves against the pinned corpus manifest."""
    manifest = grading.load_corpus_manifest(task_dir / "input" / "corpus")
    fabricated = grading.fabricated_references(payload, manifest)
    assert fabricated == [], f"FABRICATED_SOURCE_REFERENCE: {fabricated}"


def test_coverage_required(payload, task_dir):
    """G3: all required reference areas covered (checklist from the manual build plan)."""
    checklist = grading.load_checklist(task_dir / "test" / "reference" / "coverage_checklist.json")
    report = grading.coverage_report(payload, checklist)
    missing = grading.uncovered_required(report)
    assert missing == [], f"required reference areas not covered: {missing}"


def test_structure_floors(payload):
    """G3: anti-collapse floors (the Phase-1 smoke's 1-epic/1-feature thinness watch item)."""
    epics, features = grading.structure_counts(payload)
    assert epics >= MIN_EPICS, f"epic collapse: {epics} < {MIN_EPICS}"
    assert features >= MIN_FEATURES, f"feature collapse: {features} < {MIN_FEATURES}"
