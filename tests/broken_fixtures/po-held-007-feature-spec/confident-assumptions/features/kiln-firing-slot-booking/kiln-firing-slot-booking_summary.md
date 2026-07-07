# Feature Spec Summary: Kiln Firing Slot Booking

**Stack**: generic
**Generated**: 2026-07-07T11:00:00+01:00
**Scenarios**: 11 total (2 smoke, 0 regression)
**Assumptions**: 3 total (3 high / 0 medium / 0 low confidence)
**Review required**: No

## Scope

Booking of firing slots in the studio's two kilns by members: viewing
availability, booking a free slot, cancelling a booking, and the studio
manager blocking out slots for servicing. Conflict handling covers
double-booking, ownership of cancellations, and servicing collisions.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 4 |
| Boundary conditions (@boundary) | 2 |
| Negative cases (@negative) | 4 |
| Edge cases (@edge-case) | 2 |

## Deferred Items

None — all proposed groups accepted (--auto).

## Open Assumptions (low confidence)

None.

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Kiln Firing Slot Booking" --context features/kiln-firing-slot-booking/kiln-firing-slot-booking_summary.md
