"""Gate tests: phased extract, Phase B (EnrichmentBatch for EPIC-006).
Axes per po-heldout-suite-scope.md §3.3/§5 (G1, G2, G4)."""
import json

import pytest

from harness import grading
from harness.po_contract import check_batch_against_stub_allowlist, validate_enrichment_batch

TARGET_EPIC = "EPIC-006"


@pytest.fixture(scope="module")
def payload(raw_response):
    return grading.parse_response(raw_response)


@pytest.fixture(scope="module")
def phase_a_epic(task_dir):
    plan = json.loads((task_dir / "input" / "epic_plan.json").read_text(encoding="utf-8"))
    return next(e for e in plan["epics"] if e["epic_id"] == TARGET_EPIC)


def test_serving_shape(raw_response):
    """G1: exactly one <think> block, then exactly one JSON object."""
    grading.parse_response(raw_response)


def test_schema_valid(payload):
    """G1: EnrichmentBatch schema battery, incl. the delta contract (no title/bounded_context)."""
    issues = validate_enrichment_batch(payload)
    assert issues == [], "\n" + "\n".join(issues)


def test_grounding(payload, task_dir):
    """G2: every cited document name resolves against the pinned corpus manifest."""
    manifest = grading.load_corpus_manifest(task_dir / "input" / "corpus")
    fabricated = grading.fabricated_references(payload, manifest)
    assert fabricated == [], f"FABRICATED_SOURCE_REFERENCE: {fabricated}"


def test_phase_b_discipline(payload, phase_a_epic):
    """G4: dispatcher-mirror gates — epic_id match, stub allowlist, enrichment completeness
    (phased_extraction.py:540-733)."""
    allowlist = {s["feature_id"] for s in phase_a_epic["feature_stubs"]}
    issues = check_batch_against_stub_allowlist(payload, TARGET_EPIC, allowlist)
    assert issues == [], "\n" + "\n".join(issues)


def test_all_stubs_enriched(payload, phase_a_epic):
    """G3 (Phase B form): >=1 enrichment per Phase A stub of the target epic — a batch that
    silently drops stubs is coverage collapse."""
    stub_ids = {s["feature_id"] for s in phase_a_epic["feature_stubs"]}
    enriched_ids = {e.get("feature_id") for e in payload.get("enrichments", []) if isinstance(e, dict)}
    missing = sorted(stub_ids - enriched_ids)
    assert missing == [], f"Phase A stubs left unenriched: {missing}"
