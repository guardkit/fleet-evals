# Authoring input — api_test `GET /version` (self-contained)

Distilled from api_test's recorded feature artifacts for FEAT-B70F
(`features/version-endpoint/version-endpoint.feature` + the
`qa/pass-bar-TASK-B70F-*.yaml` pass-bars), self-contained here so no external
repo is needed.

## Request

Add a read-only `GET /version` endpoint to the api_test service. It returns JSON
with exactly three **build-time-injected** metadata fields:

- `version` — the application version string,
- `commit` — the git commit hash,
- `service` — the configured service name.

No authentication is required (public, read-only contract). It touches no
database. It mirrors the existing `/uptime` and `/stats` endpoints in shape and
access pattern (own router + Pydantic response schema + tests). All non-GET
methods are rejected as method-not-allowed.

## The behaviours the feature must satisfy (in plain terms)

1. A `GET /version` request returns the application version, the git commit hash,
   and the service name.
2. `POST`, `PUT`, `PATCH` and `DELETE` to `/version` are each rejected as method
   not allowed.
3. The response is valid JSON with exactly the keys `version`, `commit`,
   `service` (flat object, no nesting, no unexpected keys).
4. Accessing `/version` without authentication succeeds.

## The machine pass-bar criteria (what a live gate would check)

- `GET /version` returns HTTP 200 with the application metadata.
- Body is JSON with exactly `version`, `commit`, `service`.
- `POST /version` (and the other mutating verbs) is rejected as method-not-allowed.
- Degradation: NO degradation when the database is down (the endpoint touches no
  database — `dependency_down_degradation`).
