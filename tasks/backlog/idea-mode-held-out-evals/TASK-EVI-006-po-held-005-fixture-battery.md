---
id: TASK-EVI-006
title: "Full fixture battery + anchor-instrument integrity for po-held-005-idea"
status: backlog
task_type: testing
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 5
implementation_mode: task-work
complexity: 5
priority: high
dependencies: [TASK-EVI-003, TASK-EVI-005]
created: 2026-07-05T09:30:00Z
consumer_context:
  - task: TASK-EVI-005
    consumes: CALIBRATED_THRESHOLD
    framework: "fixture authoring against the calibrated matcher"
    driver: "harness.idea_gates"
    format_note: "evasion/stuffing fixtures are cut only AFTER the ASSUM-009 threshold is calibrated — cutting them first bakes in an uncalibrated rule"
---

# TASK-EVI-006 — po-held-005-idea full battery

## Scope

All fixtures authored as **surgical mutations of the Oracle** (frozen-suite pattern),
one dir per defect class with `meta.json` `expect_fail` naming the owning test(s):

**Broken** (`tests/broken_fixtures/po-held-005-idea/`): unlicensed-invention (anchor
asserted, no license); evasion-variant (case/punct/unicode variant of an anchor, incl.
U+2011); keyword-stuffed-license (one statement, >threshold body-asserted groups);
wrong-mode; fabricated-citation (any .md cited); two-assumptions; empty-assumption-fields;
coverage-non-null; duplicate-feature-ids; enum-drift (confidence "certain");
no-think-block; flatten-mismatch. (Stub-sheet landed as seed in TASK-EVI-003.)

**Good** (`tests/good_fixtures/po-held-005-idea/`): frontier-baseline (from
TASK-EVI-005); literal-think-tags-in-payload; trailing-echo; open-question-licensing;
many-assumptions (no upper bound); licensed-per-group — **one good fixture per anchor
group** demonstrating assertion+natural-language license (red-team hardening 4);
compound-assumption (2-group statement licensing both); think-draft-decoy (draft roadmap
WITH anchor terms inside think block, clean payload — owns the payload-only invariant).

**Integrity additions** (NEW file `tests/test_idea_verifier_integrity.py`): every anchor
regex compiles; per-group firing fixture AND licensed good fixture exist; no anchor
alternate matches the brief text; **pinned fixture floor list** for po-held-005-idea
(superset assertion — battery may grow, never shrink below the registered floor).

## Acceptance Criteria

- [ ] Every broken fixture fails exactly its owning test(s); every good fixture passes
- [ ] Per-group firing + licensed coverage proven by the integrity test
- [ ] Floor list registered (in the integrity test + addendum doc)
- [ ] `pytest tests/ -q` fully green at commit
