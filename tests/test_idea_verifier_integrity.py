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
