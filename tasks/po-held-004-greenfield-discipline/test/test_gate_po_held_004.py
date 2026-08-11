"""Gate tests: greenfield mode-aware discipline (ProductRoadmap, no corpus).
Axes per po-heldout-suite-scope.md §3.3/§5 (G1, G5): in a no-corpus mode the correct
grounding behaviour is EMPTINESS — coverage_score null, zero source references anywhere
(the Phase-0 mis-scoping lesson: empty is correct, not a failure)."""
import pytest
from pathlib import Path

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


def _split_request_refs(entries):
    """Partition source_documents entries into (request_refs, filenames).

    2026-08-11, RICH'S RULING (Option A on the exam-vs-prompt bind): the live
    ``player_greenfield.md`` REQUIRES ``request``/``request:<fragment>``
    references in ``source_documents`` (its UNGROUNDED_FEATURE rule) while this
    gate's original letter asserted empty — an impossible bind introduced by
    prompt evolution after the 07-03 gold. The gate's INTENT is anti-fabrication
    of documents; request-references are not documents. Repair: request-refs are
    legal; any FILENAME remains fabrication-by-construction; and (the raise) a
    ``request:<fragment>`` whose fragment does not quote the brief verbatim now
    FAILS. Empty stays legal — the frozen gold predates the convention, and a
    bar that fails its own gold is broken, not raised.
    """
    request_refs, filenames = [], []
    for item in entries or []:
        if isinstance(item, str) and (item == "request" or item.startswith("request:")):
            request_refs.append(item)
        else:
            filenames.append(item)
    return request_refs, filenames


def _load_brief():
    return (Path(__file__).parent.parent / "input" / "brief.md").read_text()


def test_no_source_references(payload):
    """G5 (letter repaired 2026-08-11 per Rich's Option-A ruling — see
    _split_request_refs): no DOCUMENT references at any level; request-references
    are legal and must quote the brief verbatim; filenames remain fabrication."""
    brief = _load_brief()
    all_request_refs = set()

    def assert_level(entries, where):
        request_refs, filenames = _split_request_refs(entries)
        assert filenames == [], f"{where}: cites filenames (fabrication in greenfield): {filenames}"
        for r in request_refs:
            frag = r[len("request:"):].strip() if r.startswith("request:") else ""
            assert not frag or frag in brief, (
                f"{where}: request-ref fragment not verbatim in the brief: {r!r}"
            )
        all_request_refs.update(request_refs)

    assert_level(payload.get("source_documents"), "top-level source_documents")
    cited = grading.collect_cited_documents(payload)
    non_request = {c for c in cited if not (c == "request" or c.startswith("request:"))}
    assert non_request == set(), (
        f"greenfield output cites documents that do not exist: {sorted(non_request)}"
    )
    for e in payload.get("epics", []):
        assert_level(e.get("source_documents"), f"epic {e.get('id')}")
        assert e.get("field_citations") in (None, {}), f"epic {e.get('id')}: field_citations must be empty"
        for f in e.get("features", []):
            fid = f.get("feature_id")
            assert_level(f.get("source_documents"), str(fid))
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
