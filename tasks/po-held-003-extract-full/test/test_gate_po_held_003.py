"""Gate tests: single-pass extract (ProductRoadmap — the Decision-A serving shape).
Axes per po-heldout-suite-scope.md §3.3/§5."""
import pytest

from harness import grading
from harness.po_contract import validate_product_roadmap

MIN_EPICS = 5      # scope §5 G3 anti-collapse floor (April baseline: 8)
MIN_FEATURES = 18  # scope §5 G3 anti-collapse floor (April baseline: 36)


@pytest.fixture(scope="module")
def payload(raw_response):
    return grading.parse_response(raw_response)


def test_serving_shape(raw_response):
    """G1: exactly one <think> block, then exactly one JSON object."""
    grading.parse_response(raw_response)


def test_schema_valid(payload):
    """G1: full ProductRoadmap battery incl. feature_spec_inputs flatten-match,
    >=2-sentence descriptions, exact enum Literals, SourceDocument/Assumption shapes."""
    issues = validate_product_roadmap(payload)
    assert issues == [], "\n" + "\n".join(issues)


def test_mode_is_extract(payload):
    assert payload.get("mode") == "extract", f"mode {payload.get('mode')!r} != 'extract'"


def test_grounding(payload, task_dir):
    """G2: every cited document name resolves against the pinned corpus manifest.
    This is the axis the April base output failed (FEAT-PO-032's misspelled citation)."""
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
    """G3: anti-collapse floors."""
    epics, features = grading.structure_counts(payload)
    assert epics >= MIN_EPICS, f"epic collapse: {epics} < {MIN_EPICS}"
    assert features >= MIN_FEATURES, f"feature collapse: {features} < {MIN_FEATURES}"
