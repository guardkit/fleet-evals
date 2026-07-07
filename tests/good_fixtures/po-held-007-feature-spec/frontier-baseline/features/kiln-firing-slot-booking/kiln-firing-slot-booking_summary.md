# Feature Spec Summary: Kiln Firing Slot Booking

**Stack**: generic
**Generated**: 2026-07-07T14:20:00+01:00
**Scenarios**: 16 total (3 smoke, 0 regression)
**Assumptions**: 6 total (0 high / 0 medium / 6 low confidence)
**Review required**: Yes

## Scope

Booking of firing slots in the studio's two kilns by members: viewing
availability, booking, cancelling with a notice rule, and manager block-outs
for servicing. Boundary pairs cover the assumed active-booking cap and the
assumed cancellation window; conflict handling covers double-booking, races,
ownership, past slots, and servicing collisions across both kilns.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 4 |
| Boundary conditions (@boundary) | 4 |
| Negative cases (@negative) | 6 |
| Edge cases (@edge-case) | 4 |

## Deferred Items

None — all proposed groups accepted (--auto).

## Open Assumptions (low confidence)

- ASSUM-001 — active-booking limit per member (assumed 3)
- ASSUM-002 — cancellation notice window (assumed 24 hours)
- ASSUM-003 — behaviour when a booked slot is blocked for servicing
- ASSUM-004 — who publishes firing slots, and when
- ASSUM-005 — treatment of slots that have already started
- ASSUM-006 — when a cancelled slot becomes bookable again

REVIEW REQUIRED: all assumptions unconfirmed (--auto mode)

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Kiln Firing Slot Booking" --context features/kiln-firing-slot-booking/kiln-firing-slot-booking_summary.md
