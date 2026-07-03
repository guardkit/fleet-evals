"""Gate tests: greenfield mode-aware discipline (ProductRoadmap, no corpus).
Axes per po-heldout-suite-scope.md §3.3/§5 (G1, G5): in a no-corpus mode the correct
grounding behaviour is EMPTINESS — coverage_score null, zero source references anywhere
(the Phase-0 mis-scoping lesson: empty is correct, not a failure)."""
import pytest

from harness import grading
from harness.po_contract import validate_product_roadmap

MIN_ASSUMPTIONS = 3  # scope §5 G5


@pytest.fixture(scope="module")
def payload(raw_response):
    return grading.parse_response(raw_response)


def test_serving_shape(raw_response):
    """G1: exactly one <think> block, then exactly one JSON object."""
    grading.parse_response(raw_response)


def test_schema_valid(payload):
    """G1: full ProductRoadmap battery."""
    issues = validate_product_roadmap(payload)
    assert issues == [], "\n" + "\n".join(issues)


def test_mode_is_greenfield(payload):
    assert payload.get("mode") == "greenfield", f"mode {payload.get('mode')!r} != 'greenfield'"


def test_coverage_score_null(payload):
    """G5: greenfield has no corpus to cover — coverage_score must be null."""
    assert payload.get("coverage_score") is None, (
        f"coverage_score must be null in greenfield, got {payload.get('coverage_score')!r}"
    )


def test_no_source_references(payload):
    """G5: zero source references at every level — top-level source_documents, epic/feature
    source_documents, field_citations, citations. A greenfield output citing documents that
    were never provided is fabrication by construction."""
    assert payload.get("source_documents") in (None, []), "top-level source_documents must be empty"
    cited = grading.collect_cited_documents(payload)
    assert cited == set(), f"greenfield output cites documents that do not exist: {sorted(cited)}"
    for e in payload.get("epics", []):
        assert e.get("source_documents") in (None, []), f"epic {e.get('id')}: source_documents must be empty"
        assert e.get("field_citations") in (None, {}), f"epic {e.get('id')}: field_citations must be empty"
        for f in e.get("features", []):
            fid = f.get("feature_id")
            assert f.get("source_documents") in (None, []), f"{fid}: source_documents must be empty"
            assert f.get("field_citations") in (None, {}), f"{fid}: field_citations must be empty"


def test_assumptions_present_and_falsifiable_shape(payload):
    """G5: >=3 assumptions, each with the complete falsifiable shape — non-empty statement
    and impact_if_wrong, confidence in {high, medium, low} (enum already schema-checked)."""
    assumptions = payload.get("assumptions") or []
    assert len(assumptions) >= MIN_ASSUMPTIONS, (
        f"greenfield brief has deliberate unknowns; expected >={MIN_ASSUMPTIONS} assumptions, got {len(assumptions)}"
    )
    for a in assumptions:
        assert a.get("statement", "").strip(), f"assumption {a.get('id')}: empty statement"
        assert a.get("impact_if_wrong", "").strip(), f"assumption {a.get('id')}: empty impact_if_wrong"
