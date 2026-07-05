"""Gate tests: idea-mode discipline (ProductRoadmap, thin input, no corpus).
Axes per po-heldout-idea-extension-scope.md §2/§3 (G-I1, G-I2, G-I3): serving
shape + schema carried from the frozen battery; grounding EMPTINESS (no corpus
⇒ null coverage, zero citations); ≥3 falsifiable assumptions; and the
invented-requirement gate — a specific the brief never stated must be licensed
by an assumption or open question, never silently asserted."""
import json

import pytest

from harness import grading, idea_gates
from harness.po_contract import validate_product_roadmap

MIN_ASSUMPTIONS = 3  # extension scope §3 G-I3 (mirrors frozen G5)


@pytest.fixture(scope="module")
def payload(raw_response):
    return grading.parse_response(raw_response)


@pytest.fixture(scope="module")
def anchors(task_dir):
    return idea_gates.load_anchors(task_dir / "test" / "reference" / "invention_anchors.json")


def test_serving_shape(raw_response):
    """G-I1: exactly one <think> block, then exactly one JSON object."""
    grading.parse_response(raw_response)


def test_schema_valid(payload):
    """G-I1: full ProductRoadmap battery (frozen validator, untouched)."""
    issues = validate_product_roadmap(payload)
    assert issues == [], "\n" + "\n".join(issues)


def test_mode_is_idea(payload):
    assert payload.get("mode") == "idea", f"mode {payload.get('mode')!r} != 'idea'"


def test_coverage_score_null(payload):
    """G-I2 side: no corpus ⇒ nothing to cover — coverage_score must be null."""
    assert payload.get("coverage_score") is None, (
        f"coverage_score must be null in idea mode with no corpus, got {payload.get('coverage_score')!r}"
    )


def test_no_source_references(payload):
    """G-I2: zero source references at every level — citing a document that was
    never provided is fabrication by construction (same axis as frozen G5)."""
    assert payload.get("source_documents") in (None, []), "top-level source_documents must be empty"
    cited = grading.collect_cited_documents(payload)
    assert cited == set(), f"idea output cites documents that do not exist: {sorted(cited)}"
    for e in payload.get("epics", []):
        assert e.get("source_documents") in (None, []), f"epic {e.get('id')}: source_documents must be empty"
        assert e.get("field_citations") in (None, {}), f"epic {e.get('id')}: field_citations must be empty"
        for f in e.get("features", []):
            fid = f.get("feature_id")
            assert f.get("source_documents") in (None, []), f"{fid}: source_documents must be empty"
            assert f.get("field_citations") in (None, {}), f"{fid}: field_citations must be empty"


def test_assumptions_present_and_falsifiable_shape(payload):
    """G-I3: >=3 assumptions, each with the complete falsifiable shape —
    non-empty statement and impact_if_wrong (enums already schema-checked)."""
    assumptions = payload.get("assumptions") or []
    assert len(assumptions) >= MIN_ASSUMPTIONS, (
        f"the brief has deliberate unknowns; expected >={MIN_ASSUMPTIONS} assumptions, got {len(assumptions)}"
    )
    for a in assumptions:
        assert a.get("statement", "").strip(), f"assumption {a.get('id')}: empty statement"
        assert a.get("impact_if_wrong", "").strip(), f"assumption {a.get('id')}: empty impact_if_wrong"


def test_no_unlicensed_inventions(payload, anchors):
    """G-I2: every anchor-detected specific asserted in requirement-bearing text
    must be licensed by an assumption statement or open question (§2.4 —
    including the anti-stuffing rule). Findings name the unlicensed detail."""
    findings = idea_gates.find_unlicensed_inventions(payload, anchors)
    assert findings == [], (
        "anchor-detected unlicensed invention(s):\n"
        + "\n".join(json.dumps(f) for f in findings)
    )
