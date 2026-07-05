"""Gate tests: scope-mode selection discipline (ProductRoadmap over an authored
reference roadmap). Axes per po-heldout-idea-extension-scope.md §2.5/§3 (G-I1,
G-I2, G-I4): serving shape + frozen schema battery; grounding emptiness (the
reference roadmap is selection input, not a corpus); selection-subset with
title/bounded_context pinning; dependency closure vs the REFERENCE graph;
constraint-carried floor."""
import json

import pytest

from harness import grading, idea_gates
from harness.po_contract import validate_product_roadmap


@pytest.fixture(scope="module")
def payload(raw_response):
    return grading.parse_response(raw_response)


@pytest.fixture(scope="module")
def reference(task_dir):
    return json.loads(
        (task_dir / "input" / "reference_roadmap.json").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def constraint_anchors(task_dir):
    return idea_gates.load_anchors(task_dir / "test" / "reference" / "constraint_anchors.json")


@pytest.fixture(scope="module")
def selection(payload):
    return idea_gates.extract_selection(payload)


def test_serving_shape(raw_response):
    """G-I1: exactly one <think> block, then exactly one JSON object."""
    grading.parse_response(raw_response)


def test_schema_valid(payload):
    """G-I1: full ProductRoadmap battery (frozen validator, untouched)."""
    issues = validate_product_roadmap(payload)
    assert issues == [], "\n" + "\n".join(issues)


def test_mode_is_scope(payload):
    assert payload.get("mode") == "scope", f"mode {payload.get('mode')!r} != 'scope'"


def test_coverage_score_null(payload):
    """No document corpus ⇒ coverage_score must be null (the reference roadmap
    is selection input, not a corpus)."""
    assert payload.get("coverage_score") is None, (
        f"coverage_score must be null in scope mode with no corpus, got {payload.get('coverage_score')!r}"
    )


def test_no_source_references(payload):
    """G-I2: zero source references at every level — no corpus was provided."""
    assert payload.get("source_documents") in (None, []), "top-level source_documents must be empty"
    cited = grading.collect_cited_documents(payload)
    assert cited == set(), f"scope output cites documents that do not exist: {sorted(cited)}"
    for e in payload.get("epics", []):
        assert e.get("source_documents") in (None, []), f"epic {e.get('id')}: source_documents must be empty"
        for f in e.get("features", []):
            fid = f.get("feature_id")
            assert f.get("source_documents") in (None, []), f"{fid}: source_documents must be empty"


def test_selection_has_features(selection):
    """A scope response that selects nothing is not a selection."""
    assert selection["selected_ids"], "scope response selected zero features"


def test_selection_subset(selection, reference):
    """G-I4: every selected feature exists in the reference AND keeps its
    reference title and bounded_context (content-swap under a legitimate id is
    invention; descriptions deliberately free — Coach territory)."""
    findings = idea_gates.check_selection_subset(selection, reference)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_dependency_closure(selection, reference):
    """G-I4: closure vs the REFERENCE graph — every reference-declared
    prerequisite of a selected feature is selected; response depends_on entries
    resolve to selected ids. Emptied depends_on changes nothing."""
    findings = idea_gates.check_dependency_closure(selection, reference)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_constraint_carried(payload, constraint_anchors):
    """G-I4: ALL constraint-anchor groups match the joined
    constraints_and_dependencies text — the constraint is the whole exercise."""
    findings = idea_gates.check_constraint_carried(payload, constraint_anchors)
    assert findings == [], (
        "delivery constraint not carried:\n" + "\n".join(json.dumps(f) for f in findings)
    )
