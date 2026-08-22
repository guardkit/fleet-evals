---
id: TASK-MDS-001
title: Member directory data model and opt-out flag
task_type: declarative
parent_review: TASK-REV-MDS1
feature_id: FEAT-MDS-01
wave: 1
implementation_mode: direct
complexity: 3
dependencies: []
---

# TASK-MDS-001 — Member directory data model and opt-out flag

## Description

Define the directory entry model: member name, listed skills, profile
summary, and the `directory_opt_out` visibility flag (ASSUM-003 — deferred,
default false). Pure data definitions plus a seed fixture; no behaviour.

## Acceptance Criteria

- Directory entry model exposes name, skills, profile summary, and the
  opt-out flag with a false default.
- Skills are a list of free-text labels (no taxonomy — the spec assumes none).
- A seed fixture provides several members, including two sharing a name and
  one opted out, for downstream task tests.

## Implementation Notes

Model-only task (`declarative`): no queries, no access control — those land
in TASK-MDS-002/003.
