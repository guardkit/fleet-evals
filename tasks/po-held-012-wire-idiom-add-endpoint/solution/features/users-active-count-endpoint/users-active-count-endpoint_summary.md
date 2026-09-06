# Feature Spec Summary: Users Active Count Endpoint

**Stack**: generic
**Generated**: 2026-09-06T21:00:00+01:00
**Scenarios**: 8 total (1 smoke, 0 regression)
**Assumptions**: 3 total (0 high / 0 medium / 3 low confidence)
**Review required**: Yes

## Scope

What a caller sees from a new GET /users/active-count route: the number of
active users and the number of inactive users as two separate counts, the
answers when one or both numbers are zero, a method the route does not offer
refused, a format the route does not offer refused, and two requests at the
same moment seeing the same numbers. Every worked example is a request to the
endpoint and the reply it gets.

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
