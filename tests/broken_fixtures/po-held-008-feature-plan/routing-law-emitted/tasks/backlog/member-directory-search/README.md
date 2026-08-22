# Feature: Member Directory Search (FEAT-MDS-01)

Search the member directory by name or skill for signed-in members: paged
results, profile summaries, refusal of empty/too-short queries, namesake
handling, and an opt-out visibility flag. Planned headless from the pinned
`/feature-spec` triple (9 scenarios, 3 assumptions — all low confidence,
deferred).

## Tasks

| Task | Title | Type | Wave | Complexity | Mode |
|------|-------|------|------|-----------|------|
| TASK-MDS-001 | Member directory data model and opt-out flag | declarative | 1 | 3 | direct |
| TASK-MDS-002 | Directory search service with paging and query rules | feature | 2 | 5 | task-work |
| TASK-MDS-003 | Search access control for signed-in members | feature | 2 | 4 | task-work |
| TASK-MDS-004 | Member search results page with profile summaries | feature | 3 | 4 | task-work |
| TASK-MDS-005 | End-to-end tests for the directory search scenarios | testing | 4 | 3 | direct |

## Execution

Waves are sequential; TASK-MDS-002 and TASK-MDS-003 run in parallel inside
wave 2. See `IMPLEMENTATION-GUIDE.md` for the data-flow and dependency
diagrams, and `.guardkit/features/FEAT-MDS-01.yaml` for the structured plan.

## Open assumptions (deferred to the approval loop)

- ASSUM-001 — results page size (assumed twenty)
- ASSUM-002 — minimum query length (assumed two characters)
- ASSUM-003 — directory opt-out flag exists (assumed, default false)
