Target repository: api_test

On a fresh database, creating a user with POST /users answers 201 and GET /users/count-by-domain answers 200 with the counts by domain, so a new deployment works without a hand-made column (today both fail because the users table has no deleted_at column, which the code expects).
