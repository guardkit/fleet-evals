# Feature Spec Summary: Users Active Count Endpoint

**Stack**: generic
**Generated**: 2026-09-06T21:00:00+01:00
**Scenarios**: 8 total (1 smoke, 0 regression)
**Assumptions**: 3 total (0 high / 0 medium / 3 low confidence)
**Review required**: Yes

## Scope

A new GET /users/active-count route and the is_active column it counts from:
the migration that adds the column, the grouping of rows by the flag, the two
counts kept apart in the reply, the answers when a number is zero, a method or
format the route does not offer refused, and rolling the migration back
without losing rows.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 2 |
| Boundary conditions (@boundary) | 3 |
| Negative cases (@negative) | 2 |
| Edge cases (@edge-case) | 1 |

## Deferred Items

None — all proposed groups accepted (--auto).

## Open Assumptions (low confidence)

- ASSUM-001 — what the two numbers are called in the reply (assumed active and inactive)
- ASSUM-002 — the status for a POST to the count route (assumed 405)
- ASSUM-003 — the formats the route offers (assumed JSON only, 406 otherwise)

REVIEW REQUIRED: all assumptions unconfirmed (--auto mode)

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Users Active Count Endpoint" --context features/users-active-count-endpoint/users-active-count-endpoint_summary.md
