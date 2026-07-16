# Authoring input — api_test `GET /stats` (self-contained)

This is the SAME planning input the feature's spec was built from. Model the
**Request** only; the drone-fleet "Product Documentation" that rode along in the
originating planning document is product-owner-seat template bleed and is
**excluded** (the same low-confidence exclusion the feature's Gherkin recorded).

## Request (verbatim)

> Please add a GET /stats endpoint to the api_test service. It should return JSON
> with three fields: `service` (the configured app name), `requests_served` (a
> process-lifetime count of HTTP requests handled, integer) and `first_request_at`
> (UTC ISO-8601 time of the first request handled, null until one has been). Keep
> the counter in-process (no database). Follow the same module structure as the
> existing /health endpoint (own router + Pydantic response schema + tests). The
> existing test suite must stay green.

## The behaviours the feature must satisfy (the 8 scenarios on record, in plain terms)

1. A statistics request returns the service name, an integer request count, and
   the first-request time.
2. The served-request count increases as requests are handled.
3. The first-request time is stable once set, and is UTC ISO-8601.
4. A freshly started service counts the statistics request itself (at least one
   served).
5. The served-request count never decreases while the service runs.
6. Modifying the statistics is not allowed (the endpoint is read-only).
7. Statistics remain available when the database is unavailable (no storage
   dependency).
8. A service restart begins a fresh count (process-lifetime counting).

## The machine pass-bar criteria (what a live gate would check)

- `GET /stats` returns HTTP 200 with standard headers.
- Body is JSON with exactly `service` (non-empty string), `requests_served`
  (integer), `first_request_at`.
- `requests_served` strictly increases across two successive calls.
- `first_request_at` is non-null once a request has been handled, stable across
  calls, UTC ISO-8601.
- `POST /stats` is rejected with 405 (read-only).
- Degradation: NO degradation when the database is down (the endpoint touches no
  database).
