#!/usr/bin/env bash
# FEAT-ABL-003 smoke: trivial stand-in for `guardkit autobuild`, run INSIDE the
# task container by AutoBuildAgent (--ak command=@adapter/smoke/smoke_command.sh).
# Proves the adapter's exec + env-injection + artifact-collection path e2e:
#   1. env injection : prints the FLEET_MEMORY_* contract as this command sees it
#                      (the adapter separately records it to fleet-memory-env.txt)
#   2. exec          : applies the spike task's oracle patch (uploaded to
#                      /solution via --ak solution_dir=...) so the verifier
#                      scores reward 1.0 — the exec demonstrably changed the env
#   3. artifacts     : writes an ABL-001-shaped retrieval log at the seam path
#                      (DEFAULT_RETRIEVAL_LOG_SRC) the adapter collects from
set -euo pipefail

echo "[smoke] FLEET_MEMORY_* visible to the in-container command:"
env | grep '^FLEET_MEMORY_' | sed 's|^\(FLEET_MEMORY_PG_DSN=\).*|\1<redacted>|' | sort

echo "[smoke] applying oracle solution from /solution"
bash /solution/solve.sh

echo "[smoke] writing fake ABL-001-shaped retrieval log"
mkdir -p /app/.guardkit/logs
cat > /app/.guardkit/logs/retrieval.jsonl <<'EOF'
{"query": "smoke retrieval", "arm": "off", "items": [{"id": "smoke-item-1", "score": 0.91}, {"id": "smoke-item-2", "score": 0.83}]}
EOF

echo "[smoke] done"
