# Broken tree — po-held-013-wire-idiom-extend-endpoint

The solution spec with three worked examples rewritten in the schema idiom —
they describe a migration, a column and a table instead of a request and its
reply:

- "The users table gains an index on created_at for paging"
- "The page query reads ten rows from the users table by default"
- "The migration leaves the existing users columns unchanged"

The other five worked examples are unchanged, and the four files still agree
with each other, so the four structural gates pass and the wire-idiom gate is
the one that fails — naming exactly these three titles. Registered for the
frozen integrity test as
`tests/broken_fixtures/po-held-013-wire-idiom-extend-endpoint/schema-idiom/`,
whose `features` entry links here so the two cannot drift. Hand-written
2026-09-06.
