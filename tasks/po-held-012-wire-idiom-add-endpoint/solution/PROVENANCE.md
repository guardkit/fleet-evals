# Oracle provenance — po-held-012-wire-idiom-add-endpoint

Hand-written 2026-09-06 (the rewrite-on-refusal lane, Part F; Claude Fable 5.1,
attended). Not model output: no seat was driven when this task was written
(rule 30 of the lane's spec). It is a four-file spec for the sentence in
`input/brief.md` — the 2026-08-25 bake-off's second sentence — written in the
machine idiom: every worked example is a request to the endpoint and the reply
it gets, the method and path, the status code, and what is in the body. It is
validated against the real gates: the four po-held-007 structural gates by
import, and the wire-idiom gate, which classifies every scenario with
guardkit's own routing-law rules. All eight scenarios are stamped by the wire
rule.

The shape follows the specs the seat itself produced for api_test. The status
codes are the ones api_test already answers with (200, 405 for a method a route
does not offer, 406 for a format it does not offer); the active flag is the
service's own `is_active`.

Assumptions are low/deferred per the SPL headless pin. Timestamps are fixed
authoring-time values (2026-09-06T21:00:00+01:00).

`../broken/` is this spec with three worked examples rewritten in the schema
idiom — a migration, a column, a table; the wire-idiom gate must fail it and
name those three titles.
