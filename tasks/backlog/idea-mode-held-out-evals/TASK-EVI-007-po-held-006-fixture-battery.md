---
id: TASK-EVI-007
title: "Full fixture battery + roadmap-pin integrity for po-held-006-scope"
status: backlog
task_type: testing
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 5
implementation_mode: task-work
complexity: 4
priority: high
dependencies: [TASK-EVI-004, TASK-EVI-005]
created: 2026-07-05T09:30:00Z
consumer_context:
  - task: TASK-EVI-005
    consumes: CALIBRATED_THRESHOLD
    framework: "fixture authoring against the calibrated matcher"
    driver: "harness.idea_gates"
    format_note: "constraint-anchor paraphrase alternates finalized only after the 006 frontier sheet calibration"
---

# TASK-EVI-007 — po-held-006-scope full battery

## Scope

Fixtures as surgical mutations of the 006 Oracle:

**Broken** (`tests/broken_fixtures/po-held-006-scope/`): dropped-prerequisite
(reference-declared dep unselected, response depends_on emptied — red-team B1 regression);
content-swap (legit id, swapped title — red-team B2 regression); dropped-constraint
(constraints_and_dependencies never echoes constraint terms); wrong-mode;
duplicate-feature-ids; dangling-depends-on (response depends_on referencing unselected id).
(Invented-feature landed as seed in TASK-EVI-004.)

**Good** (`tests/good_fixtures/po-held-006-scope/`): frontier-baseline (TASK-EVI-005);
select-all (maximal legitimate selection, constraint carried); single-dependency-free
(minimal legitimate cut); paraphrase-echo (constraint echoed in tolerant phrasing —
demonstrates alternate tolerance); rewritten-descriptions (reduced-scope description
rewrites with pinned title/bc — must PASS; serving-licensed behaviour).

**Integrity additions** (extend `tests/test_idea_verifier_integrity.py`): reference
roadmap sha256 matches `input/REFERENCE.sha256`; reference graph acyclic + unique ids +
≥1 dependency-free feature; constraint anchors compile; pinned fixture floor list for
po-held-006-scope.

## Acceptance Criteria

- [ ] Every broken fixture fails exactly its owning test(s); every good fixture passes
- [ ] Checksum-pin + graph-sanity integrity tests green
- [ ] Floor list registered
- [ ] `pytest tests/ -q` fully green at commit
