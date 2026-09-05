# Feature Spec Summary: Tool Loan History

**Stack**: generic
**Generated**: 2026-09-05T14:30:00+01:00
**Scenarios**: 6 total (1 smoke, 0 regression)
**Assumptions**: 2 total (0 high / 0 medium / 2 low confidence)
**Review required**: Yes

## Scope

A tool library member reading their own loan history: what they have borrowed
recently, in what order, what is still out, and what another member may not see.

## Scenario Counts by Category

| Category | Count |
|----------|-------|
| Key examples (@key-example) | 3 |
| Boundary conditions (@boundary) | 1 |
| Negative cases (@negative) | 1 |
| Edge cases (@edge-case) | 1 |

## Deferred Items

None — all proposed groups accepted (--auto).

## Open Assumptions (low confidence)

- ASSUM-001 — how many recent loans the history shows (assumed seven)
- ASSUM-002 — how a loan with no recorded return is treated

REVIEW REQUIRED: all assumptions unconfirmed (--auto mode)

## Integration with /feature-plan

This summary can be passed to `/feature-plan` as a context file:

    /feature-plan "Tool Loan History" --context features/tool-loan-history/tool-loan-history_summary.md
