# Oracle provenance — po-held-011-wire-idiom-fresh-db

Hand-written 2026-09-06 (the rewrite-on-refusal lane, Part F; Claude Fable 5.1,
attended). Not model output: no seat was driven when this task was written
(rule 30 of the lane's spec). It is a four-file spec for the sentence in
`input/brief.md`, written in the machine idiom — every worked example is a
request to the endpoint and the reply it gets: the method and path, the status
code, and what is in the body — and validated against the real gates: the four
po-held-007 structural gates by import, and the wire-idiom gate, which
classifies every scenario with guardkit's own routing-law rules. All eight
scenarios are stamped by the wire rule.

The shape follows the specs the seat itself produced for api_test (for example
`features/user-domain-analytics-and-user-creation-extension/` on api_test main,
the spec from the run that refused two titles), with one deliberate difference:
where the seat's examples said "the database is freshly created and empty …
the user should be created successfully", these say what a caller sends and
what comes back. The status codes are the ones api_test already answers with
(201 on create, 400 on invalid input, 409 on an email that exists).

Assumptions are low/deferred per the SPL headless pin. Timestamps are fixed
authoring-time values (2026-09-06T21:00:00+01:00).

`../broken/` is this spec with three worked examples rewritten in the schema
idiom — a migration, a column, a table — in the voice of the two titles the
routing law refused on 2026-09-06; the wire-idiom gate must fail it and name
those three titles.
