# Broken tree — po-held-011-wire-idiom-fresh-db

The solution spec with three worked examples rewritten in the schema idiom —
they describe a migration, a column and a table instead of a request and its
reply — in the voice of the two titles the routing law refused on 2026-09-06
(planning run d08a58fc):

- "A new user can be created on a freshly created database"
- "The users table carries the deleted_at column after the migration"
- "Simultaneous user creations on a fresh database succeed"

The other five worked examples are unchanged, and the four files still agree
with each other, so the four structural gates pass and the wire-idiom gate is
the one that fails — naming exactly these three titles. Registered for the
frozen integrity test as
`tests/broken_fixtures/po-held-011-wire-idiom-fresh-db/schema-idiom/`, whose
`features` entry links here so the two cannot drift. Hand-written 2026-09-06.
