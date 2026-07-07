---
id: TASK-MDS-003
title: Search access control for signed-in members
task_type: feature
parent_review: TASK-REV-MDS1
feature_id: FEAT-MDS-01
wave: 2
implementation_mode: task-work
complexity: 4
dependencies:
- TASK-MDS-001
---

# TASK-MDS-003 — Search access control for signed-in members

## Description

Restrict directory search to signed-in members: a visitor who is not signed
in is refused before any search executes. Applies to every search entry
point the results page will use.

## Acceptance Criteria

- A signed-in member can invoke directory search.
- A visitor who is not signed in is refused, with no directory data in the
  refusal.
- The refusal path is shared by name and skill search.

## Implementation Notes

Sits beside TASK-MDS-002 in wave 2 — both build on the wave-1 model only,
so they can run in parallel.
