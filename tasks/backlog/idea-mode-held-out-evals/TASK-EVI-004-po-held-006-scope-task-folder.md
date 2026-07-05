---
id: TASK-EVI-004
title: "po-held-006-scope task folder + authored chained roadmap + seed battery"
status: backlog
task_type: feature
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 3
implementation_mode: task-work
complexity: 6
priority: high
dependencies: [TASK-EVI-002]
created: 2026-07-05T09:30:00Z
consumer_context:
  - task: TASK-EVI-002
    consumes: IDEA_GATES_API
    framework: "pytest gate tests (po-held-004 pattern)"
    driver: "harness.idea_gates"
    format_note: "subset/closure gates consume the REFERENCE roadmap graph loaded from input/reference_roadmap.json; constraint-carried uses constraint_anchors.json under the addendum-pinned schema"
---

# TASK-EVI-004 — po-held-006-scope task folder

## Scope

`tasks/po-held-006-scope/` complete:

- `task.toml` — suite = "po-heldout-idea", mode="scope", schema="ProductRoadmap",
  reps=3, timeout 1800; provenance pins `player_scope.md` + roadmap authorship.
- `input/reference_roadmap.json` — **authored fresh** (ASSUM-003 override): RoundRoute-
  style domain acceptable but content authored for this task; real dependency chains
  (closure non-vacuous), ≥1 dependency-free feature (minimal-selection boundary),
  acyclic graph, unique ids in **FEAT-PO-### style** (the fine-tune's trained id habit).
  Pinned by `input/REFERENCE.sha256`. **NEVER** in a dir named `input/corpus/`
  (frozen 13-file assertion at tests/test_verifier_integrity.py:101-110).
- `input/constraint.md` — "We have 6 weeks and 2 engineers before the pilot; select what
  fits, MVP first" (per ASSUM-003).
- `test/reference/constraint_anchors.json` — groups with number-word/paraphrase
  alternates (6|six[\s-]*week; 2|two|pair…engineer; MVP|minimum viable|pilot); filename
  is NOT coverage_checklist.json (frozen area pin at :118-133); input-disjointness rule
  applies against brief/roadmap only where it doesn't contradict the echo requirement —
  constraint anchors are exempt from the roadmap/constraint disjointness check by design
  (they MUST match the constraint text; the invention-anchor disjointness rule stays).
- `instruction.md` — Runner-assembly (system = player_scope.md verbatim; user = roadmap
  JSON + constraint); output contract: mode="scope", select only reference features,
  **preserve reference feature_ids, titles, bounded_contexts verbatim** (id preservation
  mandated explicitly — avoids systematic false positives from id-style habit),
  descriptions may be rewritten for reduced scope, carry the constraint in
  constraints_and_dependencies, coverage_score null, no citations (no corpus).
- `test/` gates: serving shape, schema, mode=="scope", grounding emptiness,
  coverage null, selection-subset (id + title/bc pinning), dependency-closure
  (vs REFERENCE graph), constraint-carried (all groups, joined text).
- `solution/` authored Oracle (a defensible 6-week MVP selection) + PROVENANCE.md.
- **Seed battery**: `tests/broken_fixtures/po-held-006-scope/invented-feature/`
  (feature id absent from reference; expect_fail names the subset gate).

## Acceptance Criteria

- [ ] `pytest tests/ -q` green after this task's commit
- [ ] Reference-graph sanity test: acyclic, unique ids, ≥1 dependency-free feature, sha256 matches pin
- [ ] Oracle passes all gates incl. closure vs reference graph and constraint-carried
- [ ] Frozen run still lists exactly 4 tasks on default `--dry-run`
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Seam Tests

```python
"""Seam test: verify IDEA_GATES_API closure contract from TASK-EVI-002."""
import json
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("IDEA_GATES_API")
def test_closure_uses_reference_graph_not_response_depends_on():
    """Closure must be computed against the reference roadmap's graph.

    Contract: emptied response depends_on must NOT satisfy closure (red-team B1).
    Producer: TASK-EVI-002.
    """
    from harness import idea_gates
    reference = json.load(open("tasks/po-held-006-scope/input/reference_roadmap.json"))
    dep_free = idea_gates.dependency_free_ids(reference)
    assert dep_free, "reference roadmap must have >=1 dependency-free feature"
    chained = idea_gates.first_chained_pair(reference)  # (prereq_id, dependent_id)
    selection = {"selected_ids": [chained[1]], "response_depends_on": {chained[1]: []}}
    findings = idea_gates.check_dependency_closure(selection, reference)
    assert findings, "dropping a reference-declared prerequisite must fail closure"
```
