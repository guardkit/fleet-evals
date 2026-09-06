# Broken tree — po-held-012-wire-idiom-add-endpoint

The solution spec with three worked examples rewritten in the schema idiom —
they describe a migration, a column and a table instead of a request and its
reply:

- "The users table has an is_active column"
- "Active rows are counted from the is_active column"
- "The migration can be rolled back without losing user rows"

The other five worked examples are unchanged, and the four files still agree
with each other, so the four structural gates pass and the wire-idiom gate is
the one that fails — naming exactly these three titles. Registered for the
frozen integrity test as
`tests/broken_fixtures/po-held-012-wire-idiom-add-endpoint/schema-idiom/`,
whose `features` entry links here so the two cannot drift. Hand-written
2026-09-06.
