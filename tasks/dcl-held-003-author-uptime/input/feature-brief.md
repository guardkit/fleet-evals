# Authoring input — api_test `GET /uptime` (self-contained)

Distilled from api_test's recorded feature artifacts
(`features/uptime-endpoint/uptime-endpoint.feature` +
`uptime-endpoint_summary.md`), self-contained here so no external repo is needed.

## Request

Add a read-only `GET /uptime` endpoint to the api_test service returning JSON with
exactly three fields:

- `service` — the configured app name,
- `started_at` — the process start time, UTC ISO-8601,
- `uptime_seconds` — the elapsed running time as a decimal number.

It mirrors the existing `src/health/` module structure (own router + Pydantic
response schema + tests). It requires no database access. The PO document's
embellishments (503-degraded behaviour, a version field, a 100ms budget) are
explicitly excluded — the request names exactly these three fields.

## The behaviours the feature must satisfy (in plain terms)

1. Requesting uptime returns the service name, the process start time (UTC
   ISO-8601), and the uptime in seconds as a decimal number.
2. Uptime increases between consecutive requests; both requests report the same
   process start time (captured once at startup, stable across requests).
3. Uptime immediately after startup is zero or greater (non-negative).
4. Attempting to modify the uptime resource is rejected as unsupported (read-only).
5. Uptime remains available when the database is unavailable.

## The machine pass-bar criteria (what a live gate would check)

- `GET /uptime` returns HTTP 200 with `service`, `started_at`, `uptime_seconds`.
- `uptime_seconds` is a non-negative decimal that increases across two successive
  calls; `started_at` is stable across calls.
- A mutating verb on `/uptime` is rejected as unsupported (read-only).
- Degradation: NO degradation when the database is down (no database dependency).
