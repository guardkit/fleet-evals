---
id: TASK-MDS-002
title: Directory search service with paging and query rules
parent_review: TASK-REV-MDS1
feature_id: FEAT-MDS-01
wave: 2
implementation_mode: task-work
complexity: 5
dependencies:
- TASK-MDS-001
---

# TASK-MDS-002 — Directory search service with paging and query rules

## Description

Search over the directory model from TASK-MDS-001: match by name or by
skill; page results at the assumed page size of twenty (ASSUM-001); refuse
empty queries and queries under the assumed two-character minimum
(ASSUM-002); exclude opted-out members from every result set (ASSUM-003);
return all namesakes.

## Acceptance Criteria

- Name search returns every non-opted-out member whose name matches.
- Skill search returns every non-opted-out member listing the skill.
- Result pages hold at most twenty members; further matches are reachable on
  subsequent pages.
- Empty and single-character queries are refused with a reason the caller
  can show the member.
- Opted-out members never appear in any result page.
- Two members sharing a name both appear.
- All modified files pass project-configured lint/format checks with zero
  errors.

## Implementation Notes

The three assumed values (page size, minimum query length, opt-out flag) are
deferred assumptions from the spec — keep each in one named constant so the
FEAT-SPL-003 approval loop can retarget them without a hunt.
