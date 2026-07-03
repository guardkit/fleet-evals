#!/bin/bash
# Oracle solution: the landed symptom fix (fleet-memory 6390d1e) — pass the
# required settings argument to DeterministicWriter in the app lifespan.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd /app
git apply --verbose "$SCRIPT_DIR/fs01-fix.patch"
