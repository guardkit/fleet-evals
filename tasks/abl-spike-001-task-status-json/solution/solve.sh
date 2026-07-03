#!/bin/bash
# Oracle solution: apply the landed FEAT-9DDE diff (guardkit
# 3450f602c..f9c4070be, behaviour-bearing paths) to the pinned repo.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd /app
git apply --verbose "$SCRIPT_DIR/feat-9dde-landed.patch"
