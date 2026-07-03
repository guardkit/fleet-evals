#!/bin/bash
# Oracle solution: apply the landed FEAT-FAUD diff (guardkit
# 71db6d268..8e6c5e9cf, behaviour-bearing paths) to the pinned repo.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd /app
git apply --verbose "$SCRIPT_DIR/feat-faud-landed.patch"
