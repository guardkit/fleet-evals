"""Verifier integrity for the po-heldout-idea extension (extension scope §2).

Additive sibling of the frozen tests/test_verifier_integrity.py (which stays
byte-identical and already auto-discovers the new tasks' Oracle + fixture
cases). This file covers what the frozen suite cannot know about: the anchor
INSTRUMENT itself (compiles, input-disjoint) and the scope task's pinned
reference roadmap (checksum + graph sanity). Fixture floor lists and per-group
firing/licensed coverage land with the full batteries (TASK-EVI-006/007)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from harness import idea_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
T005 = REPO_ROOT / "tasks" / "po-held-005-idea"
T006 = REPO_ROOT / "tasks" / "po-held-006-scope"


def test_invention_anchors_compile_one_group_per_unknown():
    anchors = idea_gates.load_anchors(T005 / "test" / "reference" / "invention_anchors.json")
    compiled = idea_gates.compile_anchors(anchors)
    assert len(compiled) == 5, "one anchor group per deliberate unknown in the brief"


def test_constraint_anchors_compile():
    anchors = idea_gates.load_anchors(T006 / "test" / "reference" / "constraint_anchors.json")
    compiled = idea_gates.compile_anchors(anchors)
    assert len(compiled) == 3, "timebox / team / mvp"


def test_invention_anchors_disjoint_from_brief():
    """§2.1 input-disjointness: an anchor matching the brief's own text would
    turn faithful restating into a gate failure."""
    brief = idea_gates.normalize((T005 / "input" / "brief.md").read_text(encoding="utf-8"))
    anchors = idea_gates.load_anchors(T005 / "test" / "reference" / "invention_anchors.json")
    for group in idea_gates.compile_anchors(anchors):
        for rx in group["patterns"]:
            assert not rx.search(brief), (
                f"anchor group {group['id']!r} pattern {rx.pattern!r} matches the brief itself"
            )


def test_reference_roadmap_checksum_pinned():
    """§2.5: the reference roadmap must not drift after gates are calibrated
    against it (the checksum-pin scenario)."""
    pinned = (T006 / "input" / "REFERENCE.sha256").read_text(encoding="utf-8").split()[0]
    actual = hashlib.sha256(
        (T006 / "input" / "reference_roadmap.json").read_bytes()
    ).hexdigest()
    assert actual == pinned, "reference_roadmap.json does not match input/REFERENCE.sha256"


def test_reference_roadmap_graph_sane():
    """§2.5 instrument sanity: unique ids, resolvable deps, acyclic, and >=1
    dependency-free feature (the minimal-selection boundary needs one)."""
    ref = json.loads((T006 / "input" / "reference_roadmap.json").read_text(encoding="utf-8"))
    issues = idea_gates.reference_graph_sanity(ref)
    assert issues == [], "\n".join(issues)
    assert idea_gates.dependency_free_ids(ref), "no dependency-free feature in the reference"
    assert idea_gates.first_chained_pair(ref), "no dependency chain in the reference (closure would be vacuous)"


# --- Fixture floor lists (§2.7: the battery may grow, never shrink) -----------

FLOOR_BROKEN_005 = {
    "stub-sheet", "unlicensed-invention", "evasion-variant", "stuffed-license",
    "unlicensed-all-groups", "wrong-mode", "fabricated-citation", "two-assumptions",
    "empty-assumption-fields", "coverage-non-null", "duplicate-feature-ids",
    "enum-drift", "no-think-block", "flatten-mismatch",
}
FLOOR_GOOD_005 = {
    "frontier-baseline", "literal-think-tags", "trailing-echo",
    "open-question-licensing", "many-assumptions", "licensed-per-group",
    "think-draft-decoy",
}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def test_005_fixture_floor_never_shrinks():
    broken = _fixture_names(REPO_ROOT / "tests" / "broken_fixtures" / "po-held-005-idea")
    good = _fixture_names(REPO_ROOT / "tests" / "good_fixtures" / "po-held-005-idea")
    assert FLOOR_BROKEN_005 <= broken, f"missing broken fixtures: {sorted(FLOOR_BROKEN_005 - broken)}"
    assert FLOOR_GOOD_005 <= good, f"missing good fixtures: {sorted(FLOOR_GOOD_005 - good)}"


FLOOR_BROKEN_006 = {
    "invented-feature", "dropped-prerequisite", "content-swap", "dropped-constraint",
    "wrong-mode", "duplicate-feature-ids", "dangling-depends-on",
}
FLOOR_GOOD_006 = {
    "frontier-baseline", "select-all", "single-dependency-free",
    "paraphrase-echo", "rewritten-descriptions",
}


def test_006_fixture_floor_never_shrinks():
    broken = _fixture_names(REPO_ROOT / "tests" / "broken_fixtures" / "po-held-006-scope")
    good = _fixture_names(REPO_ROOT / "tests" / "good_fixtures" / "po-held-006-scope")
    assert FLOOR_BROKEN_006 <= broken, f"missing broken fixtures: {sorted(FLOOR_BROKEN_006 - broken)}"
    assert FLOOR_GOOD_006 <= good, f"missing good fixtures: {sorted(FLOOR_GOOD_006 - good)}"


# --- Per-group firing + licensed demonstrations (§2.7) -------------------------

def _payload_of(fixture: Path) -> dict:
    import sys
    sys.path.insert(0, str(REPO_ROOT))
    from harness import grading
    return grading.parse_response((fixture / "response.txt").read_text(encoding="utf-8"))


def test_every_anchor_group_fires_on_the_all_groups_fixture():
    """A group that cannot fire is dead instrument. unlicensed-all-groups must
    trigger a finding for every anchor group."""
    anchors = idea_gates.load_anchors(T005 / "test" / "reference" / "invention_anchors.json")
    payload = _payload_of(REPO_ROOT / "tests" / "broken_fixtures" / "po-held-005-idea" / "unlicensed-all-groups")
    fired = {f["group"] for f in idea_gates.find_unlicensed_inventions(payload, anchors)}
    all_groups = {g["id"] for g in idea_gates.compile_anchors(anchors)}
    assert fired == all_groups, f"groups that never fired: {sorted(all_groups - fired)}"


def test_every_anchor_group_is_licensable_on_the_per_group_fixture():
    """A group that can fire but never license is a topic ban, not a licensing
    check. licensed-per-group asserts every group AND licenses each via a
    distinct natural-language assumption — zero findings."""
    anchors = idea_gates.load_anchors(T005 / "test" / "reference" / "invention_anchors.json")
    payload = _payload_of(REPO_ROOT / "tests" / "good_fixtures" / "po-held-005-idea" / "licensed-per-group")
    groups = idea_gates.compile_anchors(anchors)
    all_ids = {g["id"] for g in groups}
    asserted = {
        g["id"] for g in groups
        if any(idea_gates._first_match(g, idea_gates.normalize(t))
               for _, t in idea_gates.requirement_units(payload))
    }
    assert asserted == all_ids, f"fixture fails to assert: {sorted(all_ids - asserted)}"
    findings = idea_gates.find_unlicensed_inventions(payload, anchors)
    assert findings == [], f"licensed-per-group fixture has unlicensed findings: {findings}"
