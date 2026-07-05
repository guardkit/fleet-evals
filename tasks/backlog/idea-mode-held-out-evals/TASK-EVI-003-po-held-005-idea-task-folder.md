---
id: TASK-EVI-003
title: "po-held-005-idea task folder + seed fixture battery"
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
    format_note: "gate tests import idea_gates functions + grading.parse_response/collect_cited_documents; per-task conftest copies po-held-004's sys.path insert (no repo-level conftest exists)"
---

# TASK-EVI-003 — po-held-005-idea task folder

## Scope

`tasks/po-held-005-idea/` complete:

- `task.toml` — id, **suite = "po-heldout-idea"**, mode="idea", phase="full",
  schema="ProductRoadmap", artifact="response.txt", reps=3, timeout_seconds=1800,
  grading command per po-held-004; `[provenance]` pins `player_idea.md` (serving prompt)
  and the brief's authorship.
- `instruction.md` — Runner-assembly section (system = player_idea.md verbatim, user =
  brief), output contract (one think block + one json-fenced ProductRoadmap mode="idea";
  emptiness correct: coverage_score null, zero source references; ≥3 falsifiable
  assumptions; specifics unstated by the brief must be surfaced as assumptions or open
  questions, never silently asserted).
- `input/brief.md` — ASSUM-002: fresh 2–3 sentence physiotherapy-clinic self-service
  exercise-programme hypothesis; deliberate unknowns: platform, regulatory posture,
  integration depth, patient-data handling, clinician workflow. Disjoint from RoundRoute,
  golden-set briefs, FinProxy.
- `test/reference/invention_anchors.json` — 5 groups, **one per deliberate unknown**,
  per the addendum-pinned schema; every group has ≥1 short distinctive alternate; no
  alternate matches the brief's own text.
- `test/conftest.py` + `test/test_gate_po_held_005.py` — gates: serving shape, schema,
  mode=="idea", coverage_score null, grounding emptiness (collect_cited_documents —
  remember it harvests suggested_context_files *.md and every 'document' key),
  assumptions ≥3 falsifiable shape, invented-requirement gate (idea_gates).
- `solution/response.txt` + `solution/PROVENANCE.md` — authored minimal Oracle: passes
  every gate including the anchor gate (≥3 assumptions licensing any specifics it uses).
- **Seed battery** (same commit — `test_fixture_battery_is_populated` demands ≥1):
  `tests/broken_fixtures/po-held-005-idea/stub-sheet/` (schema-shaped, boilerplate
  one-sentence descriptions, no assumptions; meta.json expect_fail names the
  description/assumption gates).

## Acceptance Criteria

- [ ] `pytest tests/ -q` green after this task's commit (Oracle passes; seed fixture fails its owner)
- [ ] Task invisible to the frozen run: `run_po_eval.py --dry-run` default suite lists 4 tasks only
- [ ] Anchors: 5 groups mapped 1:1 to the brief's deliberate unknowns; input-disjointness holds
- [ ] NEVER creates `input/corpus/` (frozen 13-file assertion) nor `test/reference/coverage_checklist.json` (frozen area pin)
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Seam Tests

```python
"""Seam test: verify IDEA_GATES_API contract from TASK-EVI-002."""
import json
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("IDEA_GATES_API")
def test_idea_gates_api_loads_task_anchors():
    """The task's anchors file parses under the pinned schema and compiles.

    Contract: per-task anchors JSON consumed by harness.idea_gates matcher.
    Producer: TASK-EVI-002.
    """
    from harness import idea_gates
    anchors = json.load(open("tasks/po-held-005-idea/test/reference/invention_anchors.json"))
    compiled = idea_gates.compile_anchors(anchors)
    assert len(compiled) == 5, "one group per deliberate unknown"
```
