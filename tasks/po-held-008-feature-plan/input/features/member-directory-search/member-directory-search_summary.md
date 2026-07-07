# Feature Spec Summary: Member Directory Search

**Stack**: generic
**Generated**: 2026-07-07T09:30:00+01:00
**Scenarios**: 9 total (2 smoke, 0 regression)
**Assumptions**: 3 total (0 high / 0 medium / 3 low confidence)
**Review required**: Yes

## Scope

Searching the member directory by name or skill for signed-in members:
paged results, profile summaries from results, refusal of empty and
too-short queries, namesake handling, and an opt-out visibility flag.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 3 |
| Boundary conditions (@boundary) | 2 |
| Negative cases (@negative) | 3 |
| Edge cases (@edge-case) | 2 |

## Deferred Items

None — all proposed groups accepted (--auto).

## Open Assumptions (low confidence)

- ASSUM-001 — results page size (assumed twenty)
- ASSUM-002 — minimum query length (assumed two characters)
- ASSUM-003 — directory opt-out flag exists

REVIEW REQUIRED: all assumptions unconfirmed (--auto mode)

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Member Directory Search" --context features/member-directory-search/member-directory-search_summary.md
