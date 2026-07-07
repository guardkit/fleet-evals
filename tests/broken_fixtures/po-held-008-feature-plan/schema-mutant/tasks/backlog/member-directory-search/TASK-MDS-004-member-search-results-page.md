---
id: TASK-MDS-004
title: Member search results page with profile summaries
task_type: feature
parent_review: TASK-REV-MDS1
feature_id: FEAT-MDS-01
wave: 3
implementation_mode: task-work
complexity: 4
dependencies:
- TASK-MDS-002
- TASK-MDS-003
---

# TASK-MDS-004 — Member search results page with profile summaries

## Description

The member-facing surface: a search entry, paged result listing (all
namesakes shown), and opening a result to the member's profile summary.
Consumes the search service (TASK-MDS-002) behind the access-control gate
(TASK-MDS-003).

## Acceptance Criteria

- Search by name and by skill from one entry point.
- Results list shows one row per matching member, including namesakes.
- Opening a result shows that member's profile summary.
- Paging controls appear when matches exceed one page.
- Refusals (empty/too-short query, not signed in) show the reason returned
  by the service.
- All modified files pass project-configured lint/format checks with zero
  errors.

## Implementation Notes

No new query logic here — every rule lives in TASK-MDS-002/003; this task
renders their outcomes.
