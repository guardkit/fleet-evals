# Feature Spec Summary: Fresh Database User Creation and Domain Counts

**Stack**: generic
**Generated**: 2026-09-06T21:00:00+01:00
**Scenarios**: 8 total (2 smoke, 0 regression)
**Assumptions**: 3 total (0 high / 0 medium / 3 low confidence)
**Review required**: Yes

## Scope

Creating users and counting them by domain on a freshly created database: the
users table after the migration, the deleted_at column the code expects, the
count route before and after users exist, bad and duplicate bodies refused for
the right reason, and two rows written at the same moment.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 3 |
| Boundary conditions (@boundary) | 2 |
| Negative cases (@negative) | 2 |
| Edge cases (@edge-case) | 1 |

## Deferred Items

None — all proposed groups accepted (--auto).

## Open Assumptions (low confidence)

- ASSUM-001 — what the count route answers when no users exist (assumed 200 with an empty list)
- ASSUM-002 — the status for a body with no email (assumed 400)
- ASSUM-003 — the status for an email already taken (assumed 409)

REVIEW REQUIRED: all assumptions unconfirmed (--auto mode)

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Fresh Database User Creation and Domain Counts" --context features/fresh-database-user-creation-and-domain-counts/fresh-database-user-creation-and-domain-counts_summary.md
