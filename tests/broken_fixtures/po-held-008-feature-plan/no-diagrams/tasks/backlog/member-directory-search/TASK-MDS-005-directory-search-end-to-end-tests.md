---
id: TASK-MDS-005
title: End-to-end tests for the directory search scenarios
task_type: testing
parent_review: TASK-REV-MDS1
feature_id: FEAT-MDS-01
wave: 4
implementation_mode: direct
complexity: 3
dependencies:
- TASK-MDS-004
---

# TASK-MDS-005 — End-to-end tests for the directory search scenarios

## Description

Exercise the nine pinned spec scenarios end-to-end against the assembled
feature (model + service + access control + results page), covering the
smoke pair on every build.

## Acceptance Criteria

- Every scenario in `features/member-directory-search/member-directory-search.feature`
  has an end-to-end test, including both `@smoke` scenarios.
- The opt-out, namesake, and paging edge cases run against the wave-1 seed
  fixture.
- Refusal scenarios assert the member-visible reason, not internals.

## Implementation Notes

Test-only task: no production code changes. If a scenario cannot pass
without a production change, that is a defect against the owning wave-2/3
task, not something to patch here.
